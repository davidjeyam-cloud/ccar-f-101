"""
Playground engine for D1.6 Subagent State Handoff: type the instruction for the downstream agent, choose what the handoff
carries, and see exactly what that agent received and what it could do with it. Built on the SIMULATED agents in
utils/handoff_lab.py (see its docstring for what is documented vs invented).
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from utils import handoff_lab as hl
from utils import lab_trace


@dataclass
class HandoffConfig:
    mode: str = "payload"        # payload | format | transcript | phase | crash
    payload: str = "all"         # all | pointer | first_two
    fmt: str = "structured"      # structured | prose
    crossing: str = "final"      # final | raw
    n_findings: int = 6          # 6 | 24
    summary: str = "yes"         # phase: inject the phase-1 summary?
    state: str = "yes"           # crash: inject the saved state?


def _structured(fs):
    return json.dumps([{"claim": f["claim"], "source": {"url": f["source_url"], "document": f["document"], "page": f["page"]}}
                       for f in fs], indent=0)


def _prose(fs):
    return " ".join(f["claim"] for f in fs)


def run_handoff(message: str, cfg: HandoffConfig) -> dict:
    lab_trace.reset()
    head = message.strip() or "Write a cited report from these findings."
    if cfg.mode in ("payload", "format", "transcript"):
        hl.configure("long_research" if cfg.n_findings > 6 else "cited_report")
        fs = hl.FINDINGS
        if cfg.mode == "transcript" and cfg.crossing == "raw":
            body = hl.RAW_TRANSCRIPTS
        elif cfg.payload == "pointer":
            body = "(the findings from the search agents)"
        else:
            chosen = fs[:2] if cfg.payload == "first_two" else fs
            body = _prose(chosen) if cfg.fmt == "prose" else _structured(chosen)
        prompt = f"{head}\n{body}"
        out = hl.run_agent("synthesizer", prompt)
        ev = lab_trace.EVENTS[-1]
        ok = ev["claims_used"] == len(fs) and ev["cited"] == len(fs) and not ev["over_budget"]
        why = (f"The agent received {ev['claims_received']}/{len(fs)} claims, used {ev['claims_used']}, cited {ev['cited']}"
               + (f" — its prompt was {ev['prompt_tokens']} tokens, over the simulated {hl.CONTEXT_BUDGET}-token budget." if ev["over_budget"] else "."))
        return {"prompt": prompt, "output": out, "ok": ok, "why": why,
                "metrics": {"prompt tokens": ev["prompt_tokens"], "claims received": ev["claims_received"],
                            "claims cited": ev["cited"]}}
    if cfg.mode == "phase":
        hl.configure("next_phase")
        prompt = head + ("\nWhat phase 1 already established:\n" + hl.PHASE1_SUMMARY if cfg.summary == "yes" else "")
    else:
        hl.configure("crash_resume")
        prompt = head + ("\nYour saved state:\n" + json.dumps(hl.SAVED_STATE) if cfg.state == "yes" else "")
    out = hl.run_agent("explorer", prompt)
    ev = lab_trace.EVENTS[-1]
    ok = ev["reads"] <= 2
    why = (f"It read {ev['reads']} file(s)" + (" — continuing from its saved state." if ev["had_state"] else
           " — building on the phase-1 summary." if ev["had_summary"] else " — it had to explore the whole repository again."))
    return {"prompt": prompt, "output": out, "ok": ok, "why": why, "metrics": {"file reads": ev["reads"], "prompt tokens": ev["prompt_tokens"]}}
