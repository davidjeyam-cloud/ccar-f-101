# Usage: .\scripts\deploy_web.ps1
# Refreshes the React app on Cloudflare: regenerates web/public/data/*.json from the Python sources, builds, deploys with
# wrangler, then checks that the LIVE site serves exactly the course.json that was just built.
# Needs: a logged-in wrangler (npx wrangler login), node/npm, and the .venv (or python on PATH).
# NOTE: ASCII only on purpose - Windows PowerShell 5.1 misreads UTF-8 without a BOM.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$url = "https://ccar-f-web.ccar-f-web.workers.dev"
Set-Location $root

function Fail($msg) { Write-Host "DEPLOY FAILED: $msg" -ForegroundColor Red; exit 1 }

$py = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }
$env:PYTHONIOENCODING = "utf-8"

Write-Host "1/3 Exporting course data..." -ForegroundColor Cyan
& $py scripts/export_web_data.py
if ($LASTEXITCODE -ne 0) { Fail "export_web_data.py failed - the site was NOT redeployed." }

Write-Host "2/3 Building and deploying to Cloudflare..." -ForegroundColor Cyan
Push-Location web
npm run deploy
$code = $LASTEXITCODE
Pop-Location
if ($code -ne 0) { Fail "npm run deploy failed (is wrangler logged in? run: npx wrangler login). The site was NOT refreshed." }

Write-Host "3/3 Checking the live site..." -ForegroundColor Cyan
$localText = [IO.File]::ReadAllText((Join-Path $root "web\public\data\course.json"), [Text.Encoding]::UTF8)
$live = $false
for ($i = 1; $i -le 6 -and -not $live; $i++) {
    try {
        $r = Invoke-WebRequest -UseBasicParsing -Uri "$url/data/course.json?cb=$([guid]::NewGuid())" -TimeoutSec 30
        if ($r.Content -eq $localText) { $live = $true }
    } catch { }
    if (-not $live) { Start-Sleep -Seconds 5 }
}
if (-not $live) { Fail "deployed, but the live course.json does not match the local one yet. Check $url in a minute." }
Write-Host "Cloudflare app refreshed and verified: $url" -ForegroundColor Green
