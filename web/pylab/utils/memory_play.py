"""
Playground engine for D1.7 Agent Instruction Files: type the file Claude opens, choose who runs Claude Code and how the
instruction files are arranged, and get a /memory-style view of what loads and why. Uses the SIMULATED loader in
utils/memory_lab.py (rules from code.claude.com/docs/en/memory, fetched 2026-09-27).
"""

from __future__ import annotations

from dataclasses import dataclass

from utils import memory_lab as ml

_API = "# API conventions\n- Validate every request body."


@dataclass
class MemoryConfig:
    mode: str = "hierarchy"               # hierarchy | imports | rules | memory | agents
    team_rule_in: str = "project"         # project | user | local
    persona: str = "teammate"             # you | teammate
    import_at: str = "package"            # package | root
    import_path: str = "relative_to_file"  # relative_to_file | relative_to_root
    layout: str = "rules"                 # rules | monolith
    api_paths: str = "yes"                # yes | no
    claude_md: str = "imports"            # none | no_import | imports


def build(cfg: MemoryConfig):
    user = {"~/.claude/CLAUDE.md": "- I prefer short answers."}
    root = ["# Project instructions"]
    repo = {"AGENTS.md": "- Use conventional commit messages.", "standards/money.md": "- Store money as integer cents.",
            "standards/ui.md": "- Use design-system components."}
    team = "- Run `pnpm test` before committing."
    if cfg.team_rule_in == "user":
        user["~/.claude/CLAUDE.md"] += "\n" + team
    elif cfg.team_rule_in == "local":
        repo["CLAUDE.local.md"] = team
    else:
        root.append(team)
    if cfg.mode == "agents" and cfg.claude_md == "imports":
        root.insert(1, "@AGENTS.md")
    if cfg.mode != "agents" and cfg.claude_md == "imports":
        root.insert(1, "@AGENTS.md")
    if cfg.layout == "monolith":
        root += ["# Testing", "- Every bug fix gets a regression test.", "# Deployment", "- Deploy only from main.", _API]
        root += [f"- detailed guideline {i}" for i in range(1, 251)]
    else:
        repo[".claude/rules/testing.md"] = "# Testing\n- Every bug fix gets a regression test."
        repo[".claude/rules/deployment.md"] = "# Deployment\n- Deploy only from main."
        repo[".claude/rules/api-conventions.md"] = ('---\npaths:\n  - "src/api/**"\n---\n' + _API) if cfg.api_paths == "yes" else _API
    if cfg.import_at == "root":
        root += ["@standards/money.md", "@standards/ui.md"]
    else:
        pre = "../../" if cfg.import_path == "relative_to_file" else ""
        repo["packages/billing/CLAUDE.md"] = f"@{pre}standards/money.md\n- Billing owners review every change."
        repo["packages/web/CLAUDE.md"] = f"@{pre}standards/ui.md"
    if not (cfg.mode == "agents" and cfg.claude_md == "none"):
        repo["CLAUDE.md"] = "\n".join(root)
    elif cfg.team_rule_in == "project":
        repo["AGENTS.md"] += "\n" + team
    return repo, user


def run_memory(message: str, cfg: MemoryConfig) -> dict:
    repo, user = build(cfg)
    opened = message.strip().strip("`") or "README.md"
    persona = cfg.persona if cfg.mode in ("hierarchy", "memory") else "teammate"
    loaded = ml.load(persona, repo, user, [opened])
    got = ml.instructions(loaded, repo, user)
    longest = ml._longest(repo)
    notes = []
    if cfg.mode == "hierarchy" and "pnpm test" not in got:
        notes.append("The team rule doesn't reach this person — it lives in a file their session doesn't load.")
    if any(x.get("missing") for x in loaded):
        notes.append("An @import points at a file that doesn't exist from the importing file's folder.")
    if longest[1] > ml.MAX_LINES:
        notes.append(f"{longest[0]} is {longest[1]} lines — the docs target under {ml.MAX_LINES}.")
    if "validate every request body" in got and not opened.startswith("src/api/"):
        notes.append("The API rule loaded for a file outside src/api/.")
    if "integer cents" in got and not opened.startswith("packages/billing/"):
        notes.append("The billing money standard loaded outside the billing package.")
    if cfg.mode == "agents" and "conventional commit" not in got:
        notes.append("AGENTS.md was not read: a CLAUDE.md exists and doesn't import it.")
    return {"persona": persona, "opened": opened, "loaded": loaded,
            "received": sorted(ml.MARKERS[m] for m in got), "notes": notes, "ok": not notes,
            "files": {k: v for k, v in {**user, **repo}.items()}}
