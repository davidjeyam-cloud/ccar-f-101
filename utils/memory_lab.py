"""
SIMULATED Claude Code memory loader for D1.7 Agent Instruction Files (CLAUDE.md / AGENTS.md). You describe a repository's
instruction files and a user's own files; the simulator works out which instructions each person's session actually loads.

Loading rules implemented (code.claude.com/docs/en/memory, fetched 2026-09-27):
- scopes: user ~/.claude/CLAUDE.md (that user only) · project ./CLAUDE.md or ./.claude/CLAUDE.md (checked in, shared)
  · ./CLAUDE.local.md (personal, gitignored — so a teammate's clone doesn't have it)
- files in the working directory and above load at launch; CLAUDE.md files in SUBdirectories load on demand when Claude
  reads files in those subdirectories
- `@path` imports are expanded; relative paths resolve relative to the FILE containing the import; max depth 4 hops
- .claude/rules/*.md without `paths` frontmatter load at launch; with `paths` they load when Claude reads a matching file
- AGENTS.md (default setting): read only when there is no CLAUDE.md / .claude/CLAUDE.md / CLAUDE.local.md in the working
  directory or above; otherwise only the CLAUDE.md files load unless a CLAUDE.md imports it (@AGENTS.md)
- target under 200 lines per CLAUDE.md file (longer files consume more context and reduce adherence)
Simplifications (simulation): the working directory is always the repository root; managed policy files, claudeMdExcludes,
--add-dir and the "Project instructions" setting are not modelled; "instructions" are identified by marker phrases.
"""

from __future__ import annotations

import fnmatch
import posixpath
import re

from utils import lab_trace

SCENARIO_IDS = ("new_teammate", "package_standards", "split_rules", "agents_md")
MAX_LINES = 200
MAX_IMPORT_DEPTH = 4

# marker phrase -> what the instruction is (used to check who received what)
MARKERS = {
    "pnpm test": "team rule: run pnpm test before committing",
    "integer cents": "billing standard: money as integer cents",
    "design-system": "web standard: use design-system components",
    "regression test": "testing rule",
    "validate every request body": "API rule (path-scoped to src/api/**)",
    "deploy only from main": "deployment rule",
    "conventional commit": "AGENTS.md rule shared with other coding tools",
    "short answers": "personal preference",
}

SCENARIO_TEXT = {
    "new_teammate": "A new teammate clones the repo and starts Claude Code at the root. Do they get the team's rules?",
    "package_standards": "Billing and web packages have different maintainers and standards. Does each package get only its own?",
    "split_rules": "The instructions have grown to hundreds of lines. Are they split into focused topic files, with API rules loading only for API code?",
    "agents_md": "The repo already has an AGENTS.md for other coding tools. Does Claude Code still follow it once a CLAUDE.md exists?",
}


def _norm(path: str) -> str:
    return path[2:] if path.startswith("./") else path


def _frontmatter_paths(text: str):
    m = re.match(r"\s*---\s*\n(.*?)\n---", text or "", re.S)
    if not m:
        return None
    return re.findall(r'-\s*"?([^"\n]+?)"?\s*$', m.group(1), re.M) or None


def _dir(path: str) -> str:
    d = posixpath.dirname(path)
    return "" if d in (".", "") else d


def _expand(path: str, files: dict, depth: int, seen: set, loaded: list, why: str) -> None:
    if path in seen or path not in files:
        return
    seen.add(path)
    loaded.append({"path": path, "why": why})
    if depth >= MAX_IMPORT_DEPTH:
        return
    for ref in re.findall(r"(?<![`\w])@([~\w./-]+)", files[path]):
        target = posixpath.normpath(posixpath.join(_dir(path), ref)) if not ref.startswith("~") else ref
        if target in files:
            _expand(target, files, depth + 1, seen, loaded, f"imported by {path}")
        else:
            loaded.append({"path": target, "why": f"@import in {path} — FILE NOT FOUND (resolved relative to {path})",
                           "missing": True})


def load(persona: str, repo: dict, user: dict, reads=()) -> list:
    """Which files a session loads. persona 'you' (the author) or 'teammate' (a fresh clone, their own empty user file)."""
    files = {_norm(k): v for k, v in repo.items()}
    if persona == "teammate":
        files = {k: v for k, v in files.items() if posixpath.basename(k) != "CLAUDE.local.md"}   # gitignored: not in the clone
    else:
        files.update(user)
    loaded, seen = [], set()
    if persona == "you":
        for p in user:
            _expand(p, files, 0, seen, loaded, "user scope (this user only)")
    root_claude = [p for p in ("CLAUDE.md", ".claude/CLAUDE.md", "CLAUDE.local.md") if p in files]
    for p in root_claude:
        _expand(p, files, 0, seen, loaded, "project scope, loaded at launch")
    if not root_claude:
        for p in ("AGENTS.md", ".claude/AGENTS.md"):
            if p in files:
                _expand(p, files, 0, seen, loaded, "AGENTS.md — no CLAUDE.md present, so it is read instead")
    rules = sorted(p for p in files if p.startswith(".claude/rules/") and p.endswith(".md"))
    for p in rules:
        if _frontmatter_paths(files[p]) is None:
            _expand(p, files, 0, seen, loaded, "rule without paths: loaded at launch")
    for r in reads:
        r = _norm(r)
        parts = _dir(r).split("/") if _dir(r) else []
        for i in range(1, len(parts) + 1):
            d = "/".join(parts[:i])
            for name in ("CLAUDE.md", "CLAUDE.local.md"):
                p = f"{d}/{name}"
                if p in files:
                    _expand(p, files, 0, seen, loaded, f"subdirectory file, loaded when Claude read {r}")
        for p in rules:
            globs = _frontmatter_paths(files[p])
            if globs and any(fnmatch.fnmatch(r, g) for g in globs):
                _expand(p, files, 0, seen, loaded, f"path-scoped rule ({', '.join(globs)}) matched {r}")
    return loaded


def instructions(loaded: list, repo: dict, user: dict) -> set:
    files = {_norm(k): v for k, v in repo.items()}
    files.update(user)
    text = " ".join(files.get(x["path"], "") for x in loaded if not x.get("missing")).lower()
    return {m for m in MARKERS if m in text}


def _longest(repo: dict):
    sizes = {k: len(v.splitlines()) for k, v in repo.items() if posixpath.basename(_norm(k)) in ("CLAUDE.md", "CLAUDE.local.md")}
    return max(sizes.items(), key=lambda kv: kv[1]) if sizes else ("—", 0)


SCENARIO = "new_teammate"


def configure(scenario_id: str) -> None:
    global SCENARIO
    SCENARIO = scenario_id


def _check(sc, repo, user):
    def got(persona, reads=()):
        return instructions(load(persona, repo, user, reads), repo, user)
    if sc == "new_teammate":
        t = got("teammate")
        return "pnpm test" in t, f"teammate at the repo root receives: {sorted(t) or 'nothing'}"
    if sc == "package_standards":
        b = got("teammate", ["packages/billing/invoice.py"])
        w = got("teammate", ["packages/web/page.tsx"])
        ok = "integer cents" in b and "design-system" in w and "integer cents" not in w and "design-system" not in b
        return ok, f"editing billing → {sorted(b)} · editing web → {sorted(w)}"
    if sc == "split_rules":
        path, lines = _longest(repo)
        launch = got("teammate")
        api = got("teammate", ["src/api/orders.ts"])
        rules = [k for k in repo if _norm(k).startswith(".claude/rules/")]
        ok = (lines <= MAX_LINES and {"regression test", "deploy only from main"} <= launch
              and "validate every request body" not in launch and "validate every request body" in api)
        return ok, (f"longest CLAUDE.md: {path} = {lines} lines (docs: target < {MAX_LINES}) · rule files: {len(rules)} · "
                    f"API rule at launch: {'validate every request body' in launch} · API rule when editing src/api: "
                    f"{'validate every request body' in api}")
    t = got("teammate")
    return "conventional commit" in t, f"teammate receives: {sorted(t)}"


def simulate(repo: dict, user: dict) -> None:
    """Run this layout through the loader for the current scenario and record the outcome for the lab's check."""
    ok, detail = _check(SCENARIO, repo, user)
    views = {
        "you @ root": load("you", repo, user),
        "teammate @ root": load("teammate", repo, user),
        "teammate editing packages/billing/invoice.py": load("teammate", repo, user, ["packages/billing/invoice.py"]),
        "teammate editing src/api/orders.ts": load("teammate", repo, user, ["src/api/orders.ts"]),
    }
    for who, lst in views.items():
        print(f"/memory — {who}:")
        for x in lst:
            print(f"   {x['path']}  ({x['why']})")
    print("CHECK:", detail)
    lab_trace.record({"kind": "memory_check", "scenario": SCENARIO, "ok": ok, "detail": detail,
                      "missing_imports": [x["path"] for lst in views.values() for x in lst if x.get("missing")],
                      "longest": _longest(repo),
                      "team_rule_where": next((k for k, v in {**user, **repo}.items() if "pnpm test" in v.lower()), None)})
