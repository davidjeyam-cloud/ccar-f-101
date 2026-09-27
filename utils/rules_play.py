"""
Playground engine for D3.1 CLAUDE.md Hierarchy: the message box is a file path Claude reads; knobs move instructions between
scopes or change a rule's `paths`. Runs on the SIMULATED memory loader (utils/memory_lab.py, rules from the memory docs) and
prints a /memory-style list of what loaded and why.
"""

from __future__ import annotations

from dataclasses import dataclass

from utils import memory_lab as ml
from utils.rules_lab import MARKERS


@dataclass
class RulesConfig:
    mode: str = "where"
    who: str = "teammate"                 # you | teammate
    api_rule_where: str = "project_rule"  # project_rule | root_claude_md | user_rule | local_md
    tf_paths: str = "scoped"              # scoped | none | misspelled
    test_rule_as: str = "glob_rule"       # glob_rule | dir_claude_md | root_glob


_BASE = {"CLAUDE.md": "# Project\n- Run pnpm test before committing.\n"}
_USER = {"~/.claude/CLAUDE.md": "- I like short answers.\n"}


def _repo_user(cfg):
    repo, user = dict(_BASE), dict(_USER)
    api = "# API\n- Validate every request body.\n"
    where = cfg.api_rule_where if cfg.mode in ("where", "memory") else "project_rule"
    if where == "project_rule":
        repo[".claude/rules/api.md"] = '---\npaths: "src/api/**"\n---\n' + api
    elif where == "root_claude_md":
        repo["CLAUDE.md"] += api
    elif where == "user_rule":
        user["~/.claude/rules/api.md"] = api
    else:
        repo["CLAUDE.local.md"] = api
    tf = "# Terraform\n- Pin provider versions.\n"
    tfp = cfg.tf_paths if cfg.mode in ("scoped", "memory") else "scoped"
    repo[".claude/rules/terraform.md"] = {"scoped": '---\npaths:\n  - "terraform/**/*"\n---\n' + tf, "none": tf,
                                          "misspelled": '---\npath:\n  - "terraform/**/*"\n---\n' + tf}[tfp]
    t = "# Test files\n- Structure every test as arrange-act-assert.\n"
    how = cfg.test_rule_as if cfg.mode in ("spread", "memory") else "glob_rule"
    if how == "glob_rule":
        repo[".claude/rules/testing.md"] = '---\npaths:\n  - "**/*.test.tsx"\n---\n' + t
    elif how == "root_glob":
        repo[".claude/rules/testing.md"] = '---\npaths:\n  - "*.test.tsx"\n---\n' + t
    else:
        repo["src/web/CLAUDE.md"] = "# Web\n" + t
    return repo, user


def run_rules(message: str, cfg: RulesConfig) -> dict:
    repo, user = _repo_user(cfg)
    read = (message.strip() or "src/api/orders.ts").lstrip("./")
    who = cfg.who if cfg.mode in ("where", "memory") else "you"
    loaded = ml.load(who, repo, user, reads=[read])
    files = {**{ml._norm(k): v for k, v in repo.items()}, **user}
    text = " ".join(files.get(x["path"], "") for x in loaded if not x.get("missing")).lower()
    got = [MARKERS[m] for m in MARKERS if m in text]
    lines = [f"Session: **{'a teammate (fresh clone)' if who == 'teammate' else 'you'}**, Claude reads `{read}`", "/memory:"]
    lines += [f"`{x['path']}` — {x['why']}" for x in loaded]
    lines.append(f"Instructions in context: {got or 'none'}")
    notes = []
    if cfg.mode == "where" and read.startswith("src/api/") and "API rule" not in got:
        notes.append("The API rule didn't reach this session — it lives somewhere this person doesn't load (user level, or gitignored CLAUDE.local.md).")
    if cfg.mode == "scoped" and not read.startswith("terraform/") and "Terraform rule" in got:
        notes.append("The Terraform rule loaded for a non-Terraform file — it costs context in every session.")
    if cfg.mode == "scoped" and read.startswith("terraform/") and "Terraform rule" not in got:
        notes.append("The Terraform rule didn't load for a Terraform file.")
    if cfg.mode == "spread" and read.endswith(".test.tsx") and "test-file convention" not in got:
        notes.append("This test file didn't get the test convention.")
    if cfg.mode == "spread" and not read.endswith(".test.tsx") and "test-file convention" in got:
        notes.append("The test convention loaded for a file that isn't a test.")
    return {"lines": lines, "notes": notes, "ok": not notes}
