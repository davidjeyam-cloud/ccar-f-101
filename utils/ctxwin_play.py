"""
Playground engine for D5.1 Context Window Management, on the SIMULATED context window in utils/ctxwin_lab.py.
History tab: the message box is the customer's last message. Exploration tab: your question for the codebase. Session tab: the
rule you want to keep. Downstream tab: the report topic (shown in the transcript only).
"""

from __future__ import annotations

import contextlib
import io
from dataclasses import dataclass

from utils import ctxwin_lab as cl
from utils import lab_trace


@dataclass
class CtxWinConfig:
    mode: str = "history"
    cw_history: str = "full"          # full | latest | recent3
    cw_explore: str = "subagent"      # subagent | main
    cw_rule: str = "claude_md"        # claude_md | chat
    cw_full: str = "compact"          # compact | clear
    cw_upstream: str = "structured"   # structured | verbose
    cw_budget: str = "6000"           # 6000 | 12000 | 24000


def run_ctxwin(message: str, cfg: CtxWinConfig) -> dict:
    lab_trace.reset()
    buf = io.StringIO()
    lines, notes = [], []
    with contextlib.redirect_stdout(buf):
        if cfg.mode == "history":
            cl.configure("stateless_history")
            turns = list(cl.CHAT_TURNS)
            if message.strip():
                turns[-1] = message.strip()
            history = []
            for t in turns:
                history.append({"role": "user", "content": t})
                sent = {"full": history, "latest": history[-1:], "recent3": history[-3:]}[cfg.cw_history]
                reply = cl.chat(list(sent))
                history.append({"role": "assistant", "content": reply})
            for i, e in enumerate(lab_trace.EVENTS, 1):
                lines.append(f"Call {i}: sent {e['sent']} message(s), ~{e['tokens']} tokens → “{e['reply']}”")
            if not lab_trace.EVENTS[-1]["knows_order"]:
                notes.append("The last call didn't include the turn with the order number, so the model had to ask again. "
                             "The API remembers nothing between calls.")
        elif cfg.mode == "explore":
            cl.configure("exploration")
            q = message.strip() or cl.QUESTION
            if cfg.cw_explore == "subagent":
                cl.spawn_explorer(q)
            else:
                try:
                    for p in cl.FILES:
                        cl.read(p)
                    cl.answer(q)
                except cl.ContextOverflow as e:
                    notes.append(str(e))
            r = lab_trace.EVENTS[-1]
            lines.append(f"Mode: {r['mode']} · main context {r['main_tokens']:,} / {cl.WINDOW:,} tokens"
                         + (f" · subagent's own window ~{r['sub_tokens']:,}" if r.get("sub_tokens") else ""))
            if r["answer"]:
                lines.append(f"Answer: {r['answer']}")
        elif cfg.mode == "session":
            cl.configure("long_session")
            rule = message.strip() or "Never edit files under migrations/"
            if "migrations" not in rule:
                rule += " (and never edit files under migrations/)"
            s = cl.session(claude_md=[rule] if cfg.cw_rule == "claude_md" else [])
            if cfg.cw_rule == "chat":
                s.say(rule)
            s.work(until_percent=95)
            s.clear() if cfg.cw_full == "clear" else s.compact(focus="the webhook retry change")
            s.work_more()
            r = lab_trace.EVENTS[-1]
            lines += [" → ".join(r["events"]),
                      f"Knows the task: {r['knows_task']} · knows the findings: {r['knows_finding']} · rule active: {r['rule_active']}",
                      f"Edited: {r['edits'] or 'nothing'} → {r['result']}"]
            if not r["knows_task"]:
                notes.append("/clear threw away the task and the findings; only CLAUDE.md survived.")
            elif "migrations/0042_retry_columns.py" in r["edits"]:
                notes.append("The rule was said once in the conversation and was lost at compaction, so a migration was edited.")
        else:
            cl.configure("downstream_budget")
            results = [run(structured=cfg.cw_upstream == "structured") for run in cl.analyses()]
            cl.report(results, budget=int(cfg.cw_budget))
            r = lab_trace.EVENTS[-1]
            if message.strip():
                lines.append(f"Report topic: {message.strip()}")
            lines += [f"Upstream format: {cfg.cw_upstream} · report input {r['used']:,} / {r['budget']:,} tokens",
                      f"Included: {r['included']} · dropped: {r['dropped'] or 'none'} · citations kept: {r['cited']}"]
            if r["dropped"]:
                notes.append(f"{', '.join(r['dropped'])} didn't fit the report agent's budget.")
            elif not r["cited"]:
                notes.append("Everything fitted, but verbose text has no separate citations to carry into the report.")
    return {"lines": lines, "notes": notes, "ok": not notes}
