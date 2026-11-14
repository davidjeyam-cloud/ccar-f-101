"""
SIMULATED instruction-file sessions for D3.1 CLAUDE.md Hierarchy (guide TS 3.1 + 3.3), built on the memory loader in
utils/memory_lab.py (rules from code.claude.com/docs/en/memory, re-fetched 2026-09-28):
- user ~/.claude/CLAUDE.md and ~/.claude/rules/ apply to that user only; project CLAUDE.md / .claude/rules/ are shared via git;
- rules without `paths` load at launch; path-scoped rules load when Claude READS a matching file (docs wording — the guide
  says "when editing"); subdirectory CLAUDE.md files load when Claude reads files in that directory;
- `paths` is the only frontmatter field read; `*` stays in one directory (`*.md` = root only), `**` crosses directories.
Each scenario runs a few sessions (who, which files Claude reads) and prints a /memory-style list of what loaded.
INVENTED (simulation): the repository, the sessions and the marker phrases that identify each instruction.
"""

from __future__ import annotations

from utils import lab_trace
from utils import memory_lab as ml

SCENARIO_IDS = ("test_convention", "terraform_scoped", "teammate_api")
SCENARIO = "test_convention"

MARKERS = {
    "arrange-act-assert": "test-file convention",
    "pin provider versions": "Terraform rule",
    "validate every request body": "API rule",
    "pnpm test": "team rule (root CLAUDE.md)",
    "short answers": "personal preference",
}

# (session label, persona, files Claude reads, {marker: should it be loaded?})
SESSIONS = {
    "test_convention": [
        ("you edit src/web/Button.test.tsx", "you", ["src/web/Button.test.tsx"], {"arrange-act-assert": True}),
        ("you edit src/api/orders.test.tsx", "you", ["src/api/orders.test.tsx"], {"arrange-act-assert": True}),
        ("you edit src/api/orders.ts (not a test)", "you", ["src/api/orders.ts"], {"arrange-act-assert": False}),
    ],
    "terraform_scoped": [
        ("you edit terraform/modules/db/main.tf", "you", ["terraform/modules/db/main.tf"], {"pin provider versions": True}),
        ("you edit src/web/App.tsx", "you", ["src/web/App.tsx"], {"pin provider versions": False}),
    ],
    "teammate_api": [
        ("a teammate (fresh clone) edits src/api/orders.ts", "teammate", ["src/api/orders.ts"],
         {"validate every request body": True, "pnpm test": True}),
    ],
}


def configure(scenario_id: str) -> None:
    global SCENARIO
    SCENARIO = scenario_id if scenario_id in SESSIONS else "test_convention"


def _markers(loaded, repo, user):
    files = {ml._norm(k): v for k, v in repo.items()}
    files.update(user)
    text = " ".join(files.get(x["path"], "") for x in loaded if not x.get("missing")).lower()
    return {m for m in MARKERS if m in text}


def simulate(repo: dict, user: dict | None = None) -> None:
    """Run this scenario's sessions and print what each one loaded (like /memory)."""
    user = user or {}
    rows = []
    for label, persona, reads, want in SESSIONS[SCENARIO]:
        launch = ml.load(persona, repo, user, reads=())
        loaded = ml.load(persona, repo, user, reads=reads)
        got = _markers(loaded, repo, user)
        ok = all((m in got) == should for m, should in want.items())
        rows.append({"session": label, "persona": persona, "reads": reads,
                     "at_launch": [x["path"] for x in launch], "loaded": [(x["path"], x["why"]) for x in loaded],
                     "got": sorted(got), "want": want, "ok": ok})
        print(f"\n▶ {label}")
        print("  /memory (loaded files):")
        for path, why in rows[-1]["loaded"]:
            print(f"    {path}  — {why}")
        for m, should in want.items():
            print(f"  {'✓' if (m in got) == should else '✗'} {MARKERS[m]}: {'loaded' if m in got else 'NOT loaded'}"
                  f" (should {'load' if should else 'not load'})")
    lab_trace.record({"kind": "rules_sessions", "scenario": SCENARIO, "rows": rows, "ok": all(r["ok"] for r in rows),
                      "repo_files": sorted(repo), "user_files": sorted(user)})
