"""
Playground engine for D4.7 Attention Engineering, on the SIMULATED reader in utils/attention_lab.py. In the layout tab the
message box is your question (it's placed first or last by the knob); in the case-facts tab it's the customer's last message.
"""

from __future__ import annotations

import contextlib
import io
from dataclasses import dataclass

from utils import attention_lab as al
from utils import lab_trace


@dataclass
class AttentionConfig:
    mode: str = "layout"
    lead_summary: str = "yes"
    q_position: str = "end"          # end | start
    use_headers: str = "yes"
    keep_facts: str = "yes"
    trim_fields: str = "5"           # 5 | 12 | all


def run_attention(message: str, cfg: AttentionConfig) -> dict:
    lab_trace.reset()
    lines, notes = [], []
    buf = io.StringIO()
    if cfg.mode == "layout":
        al.configure("lost_in_middle")
        saved_q = al.QUESTION
        al.QUESTION = message.strip() or saved_q
        try:
            summary = "KEY FINDINGS:\n" + "\n".join(f"- {s['key']}" for s in al.SECTIONS) if cfg.lead_summary == "yes" else ""
            sep = "## " if cfg.use_headers == "yes" else ""
            details = "\n\n".join((f"{sep}{s['title']}\n" if sep else "") + s["text"] for s in al.SECTIONS)
            if cfg.use_headers != "yes" and cfg.lead_summary == "yes":
                details = al.SECTIONS[0]["title"] + "\n" + details     # keep the lead detectable without headers
            body = (summary + "\n\n" if summary else "") + details
            prompt = ("QUESTION: " + al.QUESTION + "\n\n" + body) if cfg.q_position == "start" else (body + "\n\nQUESTION: " + al.QUESTION)
            with contextlib.redirect_stdout(buf):
                al.ask(prompt)
        finally:
            al.QUESTION = saved_q
        r = lab_trace.EVENTS[-1]
        lines += [f"Layout: summary up front {r['summary_lead']} · headers {r['headers']}/9 · question {'first' if r['question_first'] else 'last'}",
                  f"Sections the reader used: {r['used']}", f"Answer: {r['answer']}"]
        if r["question_first"]:
            notes.append("With the question before the documents, the reader answered from the first report only.")
        elif not r["found_critical"]:
            notes.append("The EU battery finding (section 4 of 9) was lost in the middle.")
        return {"lines": lines, "notes": notes, "ok": not notes}
    if cfg.mode == "facts":
        al.configure("summary_drift")
        saved = list(al.CONVERSATION)
        if message.strip():
            al.CONVERSATION[-1] = "Customer A: " + message.strip()
        try:
            def build(turns):
                s = al.summarize(turns[:-1]) + "\n" + turns[-1]
                if cfg.keep_facts == "yes":
                    f = al.facts_from(turns)
                    s = "CASE FACTS: " + "; ".join(f"{k}={v}" for k, v in f.items()) + "\n" + s
                return s
            with contextlib.redirect_stdout(buf):
                al.run_conversation(build)
        finally:
            al.CONVERSATION[:] = saved
        r = lab_trace.EVENTS[-1]
        lines += [f"What the model sees:\n```\n{r['context']}\n```", f"Facts present: {r['has']}", f"Reply: {r['answer']}"]
        if not all(r["has"].values()):
            notes.append("The summary blurred the amount, order number and date — the reply is vague.")
        return {"lines": lines, "notes": notes, "ok": not notes}
    al.configure("verbose_tools")
    keep = {"5": ("order_id", "status", "delivered_on", "total", "return_window_days"),
            "12": ("order_id", "status", "delivered_on", "total", "return_window_days") + tuple(al.ORDER_FIELDS[:7])}.get(cfg.trim_fields)
    with contextlib.redirect_stdout(buf):
        al.run_lookups((lambda o: {k: o[k] for k in keep}) if keep else (lambda o: o))
    r = lab_trace.EVENTS[-1]
    lines += [f"Fields kept per lookup: {r['fields_kept']} · tool-output tokens {r['tokens']:,} (budget {al.BUDGET:,}) · evicted: {r['evicted'] or 'none'}",
              f"Answer to “which orders can still be returned?”: {r['answer']}"]
    if not r["ok"]:
        notes.append("ORD-1000's 14-day window was pushed out of context by bulky tool results.")
    return {"lines": lines, "notes": notes, "ok": not notes}
