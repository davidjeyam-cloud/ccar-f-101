"""
SIMULATED custom commands & skills for D3.3 Skills (guide TS 3.2): you write the repository's .claude/commands/ and
.claude/skills/, your own ~/.claude/skills/ and the project CLAUDE.md; the lab runs six situations and checks what each person
can invoke and what happens when they do.

Documented behaviour it follows (code.claude.com/docs/en/skills, fetched 2026-09-28):
- project skills (.claude/skills/<name>/SKILL.md) and commands (.claude/commands/<name>.md) are in the repository; personal
  skills live in ~/.claude/skills/ (all your projects, only you); same name: personal beats project, and a skill beats a command;
- context: fork runs the skill in an isolated subagent (no conversation history); its result returns to the main conversation;
- allowed-tools PRE-APPROVES tools for the invoking turn — it "does not restrict which tools are available";
  disallowed-tools REMOVES tools while the skill is active (the guide words tool restriction as "allowed-tools");
- argument-hint is shown during autocomplete; $ARGUMENTS expands to what was typed after /name;
- a skill's description is in context; its full content loads only when invoked or when the request matches it; CLAUDE.md is
  loaded every session;
- in acceptEdits mode, file edits and filesystem commands such as rm inside the working directory are auto-approved
  (agent-sdk/permissions § acceptEdits).
INVENTED (simulation): the token counts, the scaffold skill's stray `rm -rf build/`, the developer who types what the
argument-hint suggests, and the "run the tests" request that doesn't match a package-manager skill's description.
"""

from __future__ import annotations

import posixpath
import re

from utils import lab_trace

SCENARIO_IDS = ("team_command", "verbose_analysis", "restrict_tools", "missing_argument", "always_standard", "personal_variant")
SCENARIO = "team_command"
TEAM_REVIEW = "Review the open PR for bugs, tests and naming. Report findings as a list."
ALL_TOOLS = ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "WebFetch", "Agent"]


def configure(scenario_id: str) -> None:
    global SCENARIO
    SCENARIO = scenario_id if scenario_id in SCENARIO_IDS else "team_command"


def _front(text: str) -> dict:
    m = re.match(r"\s*---\s*\n(.*?)\n---\s*\n?(.*)", text or "", re.S)
    if not m:
        return {"_body": text or ""}
    out = {"_body": m.group(2)}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def _tools(v: str) -> list:
    return [t for t in re.split(r"[\s,]+", (v or "").strip("[] ")) if t]


def _commands(files: dict) -> dict:
    """name -> (source, parsed) for every / command in these files (skills beat commands with the same name)."""
    out = {}
    for path, text in files.items():
        p = path.replace("\\", "/")
        m = re.match(r"(?:~/)?\.claude/commands/(.+)\.md$", p)
        if m:
            out.setdefault(m.group(1), (path, _front(text)))
    for path, text in files.items():
        p = path.replace("\\", "/")
        m = re.match(r"(?:~/)?\.claude/skills/([^/]+)/SKILL\.md$", p)
        if m:
            fm = _front(text)
            out[fm.get("name") or m.group(1)] = (path, fm)
    return out


def available(persona: str, project: dict, user: dict) -> dict:
    """The / commands a person has: project ones for everyone, personal ones for you (personal beats project)."""
    cmds = _commands(project)
    if persona == "you":
        cmds.update(_commands(user))
    return cmds


def simulate(project: dict, user: dict | None = None, claude_md: str = "") -> None:
    user = user or {}
    sc, log, ok = SCENARIO, [], False
    you, mate = available("you", project, user), available("teammate", project, user)
    if sc == "team_command":
        ok = "review-pr" in mate
        log.append(f"a teammate's fresh clone has: {sorted(mate)} → /review-pr {'works' if ok else 'is UNKNOWN for them'}")
    elif sc == "verbose_analysis":
        cmd = you.get("analyze-codebase")
        if not cmd:
            log.append("/analyze-codebase doesn't exist")
        else:
            fork = cmd[1].get("context") == "fork"
            added = 2_000 if fork else 40_000
            ok = fork
            log.append(f"/analyze-codebase {'ran in a forked subagent (' + cmd[1].get('agent', 'general-purpose') + ') — only its summary returned' if fork else 'ran in the main conversation — every file listing and dependency dump stayed there'}")
            log.append(f"main context +{added:,} tokens")
    elif sc == "restrict_tools":
        cmd = you.get("scaffold")
        if not cmd:
            log.append("/scaffold doesn't exist")
        else:
            fm = cmd[1]
            pool = [t for t in ALL_TOOLS if t not in _tools(fm.get("disallowed-tools", ""))]
            pre = set(_tools(fm.get("allowed-tools", "")))
            log.append(f"session mode: acceptEdits · tools available during /scaffold: {pool} · pre-approved by allowed-tools: {sorted(pre) or 'none'}")
            for f in ("src/Card.tsx", "src/Card.test.tsx", "src/Card.stories.tsx"):
                log.append(f"  Write({f}) → {'auto-approved (allowed-tools)' if 'Write' in pre else 'auto-approved (acceptEdits)'}")
            if "Bash" not in pool:
                ok = True
                log.append("  Bash(rm -rf build/) → Bash isn't available while /scaffold runs (disallowed-tools) — nothing deleted")
            else:
                log.append("  Bash(rm -rf build/) → Bash is still available; rm in the working directory is auto-approved in "
                           "acceptEdits → build/ DELETED")
    elif sc == "missing_argument":
        cmd = you.get("fix-issue")
        if not cmd:
            log.append("/fix-issue doesn't exist")
        else:
            fm = cmd[1]
            hint = fm.get("argument-hint")
            typed = "4521" if hint else ""
            log.append(f"autocomplete shows: /fix-issue {hint or '(no hint)'} → the developer types /fix-issue {typed}".rstrip())
            body = fm["_body"]
            expanded = body.replace("$ARGUMENTS", typed) if "$ARGUMENTS" in body else body + (f"\nARGUMENTS: {typed}" if typed else "")
            log.append(f"the skill Claude receives: “{expanded.strip()}”")
            ok = "4521" in expanded
            if not ok:
                log.append("no issue number → Claude picks the most recent open issue (#4519) — the wrong one")
    elif sc == "always_standard":
        request = "run the tests before you commit"
        in_md = "pnpm" in (claude_md or "").lower()
        skill_hit = [n for n, (_p, fm) in you.items() if "pnpm" in (fm.get("_body", "") + fm.get("description", "")).lower()]
        loaded = [n for n in skill_hit if any(w in (you[n][1].get("description", "")).lower() for w in ("test", "commit"))]
        ok = in_md or bool(loaded)
        log.append(f"request: “{request}” · CLAUDE.md {'says to use pnpm' if in_md else 'says nothing about pnpm'} · "
                   f"skills mentioning pnpm: {skill_hit or 'none'} · loaded for this request: {loaded or 'none'}")
        log.append(f"Claude runs: {'pnpm test' if ok else 'npm test'}")
    else:  # personal_variant
        team = mate.get("review-pr")
        team_body = (team[1].get("_body", "") if team else "").strip()
        mine = [n for n in you if n != "review-pr" and n not in mate]
        yours_review = you.get("review-pr")
        ok = team_body == TEAM_REVIEW and bool(mine) and yours_review and yours_review[1].get("_body", "").strip() == TEAM_REVIEW
        log.append(f"teammate's /review-pr: “{team_body or 'missing'}” ({'unchanged' if team_body == TEAM_REVIEW else 'CHANGED'})")
        log.append(f"your personal commands: {mine or 'none'} · your /review-pr runs: “{(yours_review[1].get('_body', '').strip() if yours_review else 'missing')}”"
                   f" ({yours_review[0] if yours_review else '—'})")
    rec = {"kind": "skills_run", "scenario": sc, "ok": bool(ok), "log": log, "you": sorted(you), "teammate": sorted(mate),
           "project": sorted(project), "user": sorted(user)}
    lab_trace.record(rec)
    print("\n".join(log))
    print(f"→ {'OK' if ok else 'PROBLEM'}")
