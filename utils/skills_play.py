"""
Playground engine for D3.3 Skills, on the SIMULATED loader in utils/skills_lab.py. Knobs build the repository's commands and
skills; the message box is what the developer types (a /command with arguments, or a request).
"""

from __future__ import annotations

import contextlib
import io
import re
from dataclasses import dataclass

from utils import lab_trace
from utils import skills_lab as sl


@dataclass
class SkillsConfig:
    mode: str = "where"
    who: str = "teammate"
    cmd_where: str = "project_commands"   # project_commands | project_skills | user_commands
    fork_on: str = "yes"
    fork_agent: str = "Explore"
    allowed_list: str = "write_edit"      # none | write_edit
    disallowed_list: str = "bash"         # none | bash
    session_mode: str = "acceptEdits"     # default | acceptEdits
    hint_on: str = "yes"
    std_where: str = "claude_md"          # claude_md | skill


def run_skills(message: str, cfg: SkillsConfig) -> dict:
    lab_trace.reset()
    lines, notes = [], []
    msg = message.strip()
    if cfg.mode == "where":
        project, user = {}, {}
        target = {"project_commands": (project, ".claude/commands/review-pr.md", sl.TEAM_REVIEW),
                  "project_skills": (project, ".claude/skills/review-pr/SKILL.md", f"---\nname: review-pr\ndescription: Team PR review\n---\n{sl.TEAM_REVIEW}"),
                  "user_commands": (user, "~/.claude/commands/review-pr.md", sl.TEAM_REVIEW)}[cfg.cmd_where]
        target[0][target[1]] = target[2]
        cmds = sl.available(cfg.who, project, user)
        typed = (msg or "/review-pr").split()[0].lstrip("/")
        lines += [f"Stored at `{target[1]}` ({'in git' if target[0] is project else 'your machine only'})",
                  f"{'A teammate (fresh clone)' if cfg.who == 'teammate' else 'You'} can run: {sorted('/' + c for c in cmds) or 'nothing'}",
                  f"`/{typed}` → {'runs: “' + cmds[typed][1].get('_body', '').strip() + '”' if typed in cmds else 'unknown command'}"]
        if typed not in cmds:
            notes.append(f"/{typed} doesn't exist for this person.")
        return {"lines": lines, "notes": notes, "ok": not notes}
    if cfg.mode == "fork":
        fork = cfg.fork_on == "yes"
        added = 2_000 if fork else 40_000
        lines += [f"`{msg or '/analyze-codebase'}` → " + (f"runs in a forked {cfg.fork_agent} subagent with no conversation history; "
                  "only its one-page summary returns" if fork else "runs in the main conversation — every file listing and dependency dump stays there"),
                  f"Main context: +{added:,} simulated tokens"]
        if not fork:
            notes.append("40,000 tokens of analysis output now sit in your main conversation.")
        return {"lines": lines, "notes": notes, "ok": not notes}
    if cfg.mode == "tools":
        allowed = ["Write", "Edit"] if cfg.allowed_list == "write_edit" else []
        disallowed = ["Bash"] if cfg.disallowed_list == "bash" else []
        pool = [t for t in sl.ALL_TOOLS if t not in disallowed]
        lines.append(f"Frontmatter: allowed-tools: {' '.join(allowed) or '—'} · disallowed-tools: {' '.join(disallowed) or '—'} · session mode: {cfg.session_mode}")
        lines.append(f"Tools Claude can call during /scaffold: {pool}")
        for f in ("src/Card.tsx", "src/Card.test.tsx"):
            how = "pre-approved (allowed-tools)" if "Write" in allowed else ("auto-approved (acceptEdits)" if cfg.session_mode == "acceptEdits" else "asks you first")
            lines.append(f"Write({f}) → {how}")
        if "Bash" not in pool:
            lines.append("Bash(rm -rf build/) → not available while the skill runs — nothing deleted")
        elif cfg.session_mode == "acceptEdits":
            lines.append("Bash(rm -rf build/) → available, and rm inside the project is auto-approved in acceptEdits → build/ DELETED")
            notes.append("allowed-tools pre-approved Write/Edit but did not take Bash away.")
        else:
            lines.append("Bash(rm -rf build/) → available; in default mode it asks you first (so it depends on you clicking No)")
            notes.append("Bash is still available — only your permission prompt stands between the skill and rm -rf.")
        return {"lines": lines, "notes": notes, "ok": not notes}
    if cfg.mode == "args":
        typed = msg or "/fix-issue"
        args = " ".join(typed.split()[1:]) if typed.startswith("/") else typed
        hint = cfg.hint_on == "yes"
        lines.append(f"Autocomplete shows: /fix-issue {'[issue-number]' if hint else '(no hint)'}")
        if hint and not args:
            lines.append("…the hint shows a number is expected — (simulated) the developer adds one: /fix-issue 4521")
            args = "4521"
        lines.append(f"You typed: `{typed}` → the skill Claude receives: “Fix issue {args}: reproduce it, fix it, add a test.”")
        if not re.search(r"\d", args):
            notes.append("No issue number reached the skill — Claude has to guess which issue.")
        return {"lines": lines, "notes": notes, "ok": not notes}
    # skill vs CLAUDE.md
    req = msg or "run the tests before you commit"
    in_md = cfg.std_where == "claude_md"
    invoked = req.startswith("/package-manager")
    matched = (not in_md) and any(w in req.lower() for w in ("package manager", "pnpm", "npm install", "dependency", "dependencies"))
    uses_pnpm = in_md or invoked or matched
    lines += [f"The pnpm standard lives in: {'CLAUDE.md (loaded every session)' if in_md else 'a skill (description always visible; content only when invoked or matched)'}",
              f"Request: “{req}” → {'standard in context' if uses_pnpm else 'the skill did not load for this request'}",
              f"Claude runs: {'pnpm' if uses_pnpm else 'npm'} …"]
    if not uses_pnpm:
        notes.append("An always-needed standard wasn't in context — it belongs in CLAUDE.md.")
    return {"lines": lines, "notes": notes, "ok": not notes}
