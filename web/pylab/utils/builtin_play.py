"""
Playground engine for D2.6: built-in tool choice on the SIMULATED repo in utils/builtin_lab.py, and a "which surface?" tab
whose consequences come straight from the docs' feature comparison (code.claude.com/docs/en/features-overview, fetched
2026-09-28) — load time, context cost and whether it's guaranteed. Nothing in that tab is simulated behaviour.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from utils import builtin_lab as bl
from utils import lab_trace


@dataclass
class BuiltinConfig:
    mode: str = "search"
    search_tool: str = "grep"          # grep | glob
    edit_strategy: str = "read_write"  # short_anchor | longer_anchor | replace_all | read_write
    explore: str = "incremental"       # incremental | read_all
    wrapper_names: str = "exported"    # exported | original
    need: str = "always_rule"
    surface: str = "claude_md"


# docs: features-overview — what each surface is for, when it loads, what it costs, whether it's enforced
_SURFACE = {
    "claude_md": ("CLAUDE.md", "every session, full content", "every request", "an instruction (followed, not enforced)"),
    "skill": ("Skill", "description every session; full content when invoked or relevant", "low until used", "an instruction Claude interprets"),
    "hook": ("Hook", "runs on its event, outside the conversation", "zero unless it returns output", "guaranteed — always fires on its event"),
    "mcp": ("MCP server", "tool names at start; schemas on demand", "low until a tool is used", "tools + data from an external system"),
    "subagent": ("Subagent", "when spawned, in its own context", "isolated from the main session", "a worker that returns a summary"),
}
_NEEDS = {
    "always_rule": ("“Use pnpm, not npm” — every session", "claude_md",
                    "Always-needed conventions belong in CLAUDE.md (docs: “always do X” rules; guide TS 3.2 Skill 5)."),
    "deploy_workflow": ("A multi-step /deploy checklist you run sometimes", "skill",
                        "On-demand workflows belong in a skill (docs; guide TS 3.2 Skill 5) — CLAUDE.md would load it every session."),
    "guardrail": ("Never let Claude edit .env", "hook",
                  "A rule that must hold every time is a hook; in CLAUDE.md or a skill it's a request, not a guarantee (docs)."),
    "external_data": ("Read tickets from the team's issue tracker", "mcp",
                      "External data or actions come through MCP — a community server for standard integrations (guide TS 2.4 Skill 4)."),
    "verbose_research": ("Scan 200 files and report only the findings", "subagent",
                         "Work that reads a lot but returns a little goes to a subagent, so the main context stays clean (docs)."),
}


def run_builtin(message: str, cfg: BuiltinConfig) -> dict:
    lab_trace.reset()
    lines, notes = [], []
    if cfg.mode == "surface":
        need_text, right, why = _NEEDS[cfg.need]
        name, loads, cost, kind = _SURFACE[cfg.surface]
        lines += [f"Need: {need_text}", f"You chose: **{name}** — when it loads: {loads}; context cost: {cost}; it is {kind}.",
                  f"Docs' pick: **{_SURFACE[right][0]}** — {why}"]
        if cfg.surface != right:
            notes.append(f"{name} is not the right surface for this need.")
        return {"lines": lines, "notes": notes, "ok": not notes}
    bl.configure({"search": "find_callers", "edit": "edit_nonunique", "explore": "trace_flow", "wrapper": "wrapper_usage"}[cfg.mode])
    if cfg.mode == "search":
        q = message.strip() or "process_refund("
        if cfg.search_tool == "grep":
            hits = bl.grep(re.escape(q))
            files = sorted({h[0] for h in hits})
            lines += [f"Grep {q!r} (file CONTENTS) → {len(hits)} lines in {files}"] + [f"`{p}:{n}` {t.strip()}" for p, n, t in hits[:8]]
        else:
            files = bl.glob(q if any(c in q for c in "*?") else f"**/*{q}*")
            lines.append(f"Glob {q!r} (file PATHS) → {files}")
        lines.append("Tip: Grep answers “where is this text used?”; Glob answers “which files are named like this?”.")
        return {"lines": lines, "notes": notes, "ok": True}
    if cfg.mode == "edit":
        p = "config/app.toml"
        bl.read(p)
        try:
            if cfg.edit_strategy == "short_anchor":
                bl.edit(p, "timeout = 30", "timeout = 60")
            elif cfg.edit_strategy == "longer_anchor":
                bl.edit(p, "[payments]\ntimeout = 30", "[payments]\ntimeout = 60")
            elif cfg.edit_strategy == "replace_all":
                bl.edit(p, "timeout = 30", "timeout = 60", replace_all=True)
            else:
                try:
                    bl.edit(p, "timeout = 30", "timeout = 60")
                except bl.EditError:
                    head, tail = bl.read(p).split("[payments]")
                    bl.write(p, head + "[payments]" + tail.replace("timeout = 30", "timeout = 60", 1))
        except bl.EditError as e:
            notes.append(f"Edit failed: {e}")
        toml = bl.FILES[p]
        lines += bl._LOG["calls"] + [f"config/app.toml now:\n```\n{toml}```"]
        orders_ok = "timeout = 30" in toml.split("[payments]")[0]
        pay_ok = "timeout = 60" in toml.split("[payments]")[1]
        if not orders_ok:
            notes.append("The [orders] timeout changed too.")
        if not pay_ok:
            notes.append("The [payments] timeout is still 30.")
        return {"lines": lines, "notes": notes, "ok": not notes}
    if cfg.mode == "explore":
        if cfg.explore == "read_all":
            texts = {p: bl.read(p) for p in bl.all_paths()}
            seen = sorted(p for p in ("billing/refunds.py", "billing/approvals.py", "billing/limits.py") if p in texts)
        else:
            entry = bl.grep(r"def process_refund\(")[0][0]
            seen, queue = [], [entry]
            while queue:
                path = queue.pop(0)
                if path not in seen:
                    seen.append(path)
                    queue += [m.replace(".", "/") + ".py" for m in re.findall(r"from (billing\.\w+) import", bl.read(path))]
        lines += [f"Files read: {len(bl._LOG['read'])} · chars read: {bl._LOG['chars_read']} (budget {bl.READ_BUDGET})",
                  f"The refund flow: {' → '.join(sorted(seen))}"]
        if bl._LOG["chars_read"] > bl.READ_BUDGET:
            notes.append(f"Read {bl._LOG['chars_read']} chars to find 3 files — most of the context went on unrelated code.")
        return {"lines": lines, "notes": notes, "ok": not notes}
    # wrapper
    if cfg.wrapper_names == "exported":
        names = re.findall(r"'(\w+)'", bl.read("payments/__init__.py").split("__all__")[1])
    else:
        names = ["charge", "refund"]
    users = sorted({p for n in names for p, _l, _t in bl.grep(rf"\b{n}\(") if not p.startswith("payments/")})
    lines += [f"Names searched: {names}", f"Callers found: {users}", "Expected: ['shop/admin.py', 'shop/cart.py', 'shop/returns.py']"]
    if users != ["shop/admin.py", "shop/cart.py", "shop/returns.py"]:
        notes.append("The wrapper re-exports the functions under other names (charge_card, issue_refund) — searching the originals misses every caller.")
    return {"lines": lines, "notes": notes, "ok": not notes}
