# Usage: .\push.ps1 "your commit message"
# Runs a secret scan, stages the tracked folders, commits, and pushes to GitHub.
# Aborts (and unstages) if a secret is found or anything under docs/source/ is staged.
# Works for the very first push to a new, empty GitHub repo and tells you before it does anything unusual.
# NOTE: ASCII only on purpose - Windows PowerShell 5.1 misreads UTF-8 without a BOM.
param([string]$msg = "")

if (-not $msg) {
    $msg = "update: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
}

# --- 0. Sanity: inside a git repo, with a remote already set -----------------
git rev-parse --is-inside-work-tree *> $null
if ($LASTEXITCODE -ne 0) { Write-Host "ABORT: not inside a git repository." -ForegroundColor Red; exit 1 }

$remote = (git remote get-url origin 2>$null)
if (-not $remote) {
    Write-Host "ABORT: no 'origin' remote is set. This script will not set it silently." -ForegroundColor Red
    Write-Host "       Set it yourself, e.g.: git remote add origin https://github.com/davidjeyam-cloud/ccar-f-101.git"
    exit 1
}
$branch = (git symbolic-ref --short HEAD 2>$null)
if (-not $branch) { Write-Host "ABORT: detached HEAD - check out a branch first." -ForegroundColor Red; exit 1 }

# --- 1. Stage only the tracked folders/files that exist -----------------------
# The build prompt's list, plus config files added at the owner's request (2026-09-21) so everything is committed.
# .env, .venv, docs/source/, progress.json and output/ are gitignored and never staged.
$paths = @("app.py", "pages", "utils", "docs", "sandbox_project", "AGENTS.md", "CLAUDE.md",
           ".gitignore", "requirements.txt", ".env.example", ".streamlit", ".claude", "push.ps1")
$toAdd = $paths | Where-Object { Test-Path $_ }
if (-not $toAdd) { Write-Host "Nothing to stage: none of the tracked paths exist yet." -ForegroundColor Yellow; exit 0 }
git add -- $toAdd

# --- 2. Guard: nothing under docs/source/ may be staged, and no PDF anywhere --
# The docs/source/ check catches the canonical copy. The blanket *.pdf check is
# defense in depth: on 2026-09-22 a byte-identical stray copy of the copyrighted
# guide was found sitting directly under docs/ (not docs/source/), with no
# clear origin - it was never staged or committed, but docs/source/-only
# guards would not have caught it if it had been. This repo's docs pipeline
# never intentionally produces a PDF deliverable, so any staged .pdf aborts.
$staged = @(git diff --cached --name-only)
$forbidden = $staged | Where-Object { $_ -like "docs/source/*" }
if ($forbidden) {
    git reset -q
    Write-Host "ABORT: files under docs/source/ are staged (the official guide is copyrighted):" -ForegroundColor Red
    $forbidden | ForEach-Object { Write-Host "  $_" }
    exit 1
}
$forbiddenPdf = $staged | Where-Object { $_ -like "*.pdf" }
if ($forbiddenPdf) {
    git reset -q
    Write-Host "ABORT: a .pdf file is staged. This repo never commits a PDF - the exam guide" -ForegroundColor Red
    Write-Host "       must stay local-only in docs/source/, and nothing else here should be a PDF:"
    $forbiddenPdf | ForEach-Object { Write-Host "  $_" }
    exit 1
}
$skipCommit = $false
$scanBase = $null
if (-not $staged) {
    # Nothing new to commit - but there may be commits that were made earlier and never pushed.
    git rev-parse --verify HEAD *> $null
    if ($LASTEXITCODE -ne 0) { Write-Host "Nothing to commit and no commits yet." -ForegroundColor Yellow; exit 0 }
    git rev-parse --abbrev-ref --symbolic-full-name "@{u}" *> $null
    if ($LASTEXITCODE -ne 0) {
        $scanBase = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"   # git's empty tree: scan everything in HEAD
    } else {
        $ahead = [int](git rev-list --count "@{u}..HEAD")
        if ($ahead -eq 0) { Write-Host "Nothing to commit and nothing to push - already up to date." -ForegroundColor Yellow; exit 0 }
        $scanBase = "@{u}"
    }
    Write-Host "Nothing new to commit, but there are unpushed commits. Scanning them, then going straight to push." -ForegroundColor Yellow
    $skipCommit = $true
    $touchedFiles = @(git diff --name-only $scanBase HEAD)
    $forbiddenCommitted = $touchedFiles | Where-Object { $_ -like "docs/source/*" }
    if ($forbiddenCommitted) {
        Write-Host "ABORT: unpushed commits contain files under docs/source/ (copyrighted guide):" -ForegroundColor Red
        $forbiddenCommitted | ForEach-Object { Write-Host "  $_" }
        exit 1
    }
    $forbiddenPdfCommitted = $touchedFiles | Where-Object { $_ -like "*.pdf" }
    if ($forbiddenPdfCommitted) {
        Write-Host "ABORT: unpushed commits contain a .pdf file - this repo never commits a PDF:" -ForegroundColor Red
        $forbiddenPdfCommitted | ForEach-Object { Write-Host "  $_" }
        exit 1
    }
}

# --- 3. Secret scan over ADDED lines of the staged diff -----------------------
# Flags real-looking values only. Placeholders (your_..., <...>, example, xxx, ${VAR}, os.getenv) are allowed.
# push.ps1 is itself staged, so skip only its own rule-definition lines (they contain the patterns as text).
if ($skipCommit) { $diffText = git diff $scanBase HEAD -U0 --no-color } else { $diffText = git diff --cached -U0 --no-color }
$added = $diffText | Where-Object { $_ -match '^\+' -and $_ -notmatch '^\+\+\+' -and $_ -notmatch '^\+\s*@\{ Name = ' }
$placeholder = '(?i)your[_-]|<[^>]+>|example|placeholder|changeme|xxxx|\$\{|os\.getenv|environ|\.\.\.'
# "KEY= assignment" captures the right-hand-side VALUE in group 1 so it can be
# checked separately: a value that itself spells "key" (GEMINI_API_KEY, api_key,
# gemini_key, PAGE_KEY, ...) is a variable/constant NAME being referenced in code,
# not a literal secret - a real secret token never spells the word "key" in its
# own random-looking character content. This keeps the rule catching an actual
# leaked value while not flagging every line that passes a key variable around.
$rules = @(
    @{ Name = "Google/Gemini key (AIza)"; Rx = 'AIza[0-9A-Za-z_\-]{20,}' },
    @{ Name = "Anthropic key (sk-ant-)"; Rx = 'sk-ant-[A-Za-z0-9_\-]{16,}' },
    @{ Name = "API key (sk-)";           Rx = 'sk-[A-Za-z0-9]{20,}' },
    @{ Name = "KEY= assignment";         Rx = '(?i)[A-Z0-9_]*_KEY\s*=\s*["'']?([^\s"'']{8,})'; ValueMustNotContain = 'key' },
    @{ Name = "password= assignment";    Rx = '(?i)password\s*[=:]\s*["'']?[^\s"'']{4,}' },
    @{ Name = "secret= assignment";      Rx = '(?i)secret\s*[=:]\s*["'']?[^\s"'']{4,}' },
    @{ Name = "token= assignment";       Rx = '(?i)token\s*[=:]\s*["'']?[^\s"'']{8,}' }
)
$hits = @()
foreach ($line in $added) {
    foreach ($r in $rules) {
        if ($line -notmatch $r.Rx -or $line -match $placeholder) { continue }
        if ($r.ValueMustNotContain -and $Matches[1] -match $r.ValueMustNotContain) { continue }
        $hits += "[{0}] {1}" -f $r.Name, $line.Trim()
    }
}
if ($hits) {
    if ($skipCommit) {
        Write-Host "ABORT: possible secret in commits that are not pushed yet. NOTHING WAS PUSHED." -ForegroundColor Red
        Write-Host "       The commit(s) still exist locally - remove the secret and fix or undo the commit before pushing."
    } else {
        git reset -q
        Write-Host "ABORT: possible secret in staged changes. Nothing was committed; everything was unstaged." -ForegroundColor Red
    }
    $hits | Select-Object -Unique | ForEach-Object { Write-Host "  $_" }
    Write-Host "If it is a false positive, make it an obvious placeholder (e.g. your_api_key_here) and re-run."
    exit 1
}

# --- 4. Commit ---------------------------------------------------------------
if (-not $skipCommit) {
    git commit -m $msg
    if ($LASTEXITCODE -ne 0) { Write-Host "ABORT: commit failed." -ForegroundColor Red; exit 1 }
}

# --- 5. Push (tell the user first if this is unusual) ------------------------
$remoteHeads = @(git ls-remote --heads origin 2>$null)
$hasUpstream = $false
git rev-parse --abbrev-ref --symbolic-full-name "@{u}" *> $null
if ($LASTEXITCODE -eq 0) { $hasUpstream = $true }

if (-not $remoteHeads) {
    Write-Host ""
    Write-Host "NOTICE: the remote is empty - this is the FIRST push." -ForegroundColor Yellow
    Write-Host "  Remote : $remote"
    Write-Host "  Branch : $branch  (will be created on the remote and set as upstream)"
    $ans = Read-Host "Continue? (y/N)"
    if ($ans -notmatch '^(y|yes)$') { Write-Host "Cancelled. Your commit is local only; nothing was pushed."; exit 0 }
    git push -u origin $branch
}
elseif (-not $hasUpstream) {
    Write-Host ""
    Write-Host "NOTICE: branch '$branch' has no upstream. Pushing and setting origin/$branch as upstream." -ForegroundColor Yellow
    $ans = Read-Host "Continue? (y/N)"
    if ($ans -notmatch '^(y|yes)$') { Write-Host "Cancelled. Your commit is local only; nothing was pushed."; exit 0 }
    git push -u origin $branch
}
else {
    git push
}
if ($LASTEXITCODE -ne 0) { Write-Host "Push failed - see the message above." -ForegroundColor Red; exit 1 }
Write-Host "Done." -ForegroundColor Green
