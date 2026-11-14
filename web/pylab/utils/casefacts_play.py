"""
Playground engine for D5.2 Case Facts Block, on the SIMULATED support session in utils/casefacts_lab.py. The message box is the
customer's final question (it replaces the scripted one); each tab plays the scenario its sub-concept is about.
"""

from __future__ import annotations

import contextlib
import io
import json
from dataclasses import dataclass

from utils import casefacts_lab as cf
from utils import lab_trace


@dataclass
class CaseFactsConfig:
    mode: str = "block"
    cf_block: str = "every_prompt"    # every_prompt | none
    cf_format: str = "json"           # json | prose
    cf_per_issue: str = "yes"         # yes | flat
    cf_updates: str = "overwrite"     # overwrite | set_once
    cf_customer: str = "yes"          # yes | tools_only


_SCENARIO = {"block": "refund_promise", "issues": "multi_issue", "updates": "status_change", "expect": "customer_expectation"}


def run_casefacts(message: str, cfg: CaseFactsConfig) -> dict:
    lab_trace.reset()
    sc = _SCENARIO.get(cfg.mode, "refund_promise")
    cf.configure(sc)

    def update(facts, ev):
        for f in ev["facts"]:
            if cfg.cf_customer == "tools_only" and f["source"] != "tool":
                continue
            rec = facts.setdefault(f["issue"], {}) if cfg.cf_per_issue == "yes" else facts
            if cfg.cf_updates == "set_once":
                rec.setdefault(f["field"], f["value"])
            else:
                rec[f["field"]] = f["value"]
        return facts

    def build(facts, summary, recent):
        if cfg.cf_block == "none":
            return summary + recent
        body = json.dumps(facts, ensure_ascii=False) if cfg.cf_format == "json" else cf.prose_note(facts)
        return [{"role": "system", "content": "CASE FACTS (current, verbatim)\n" + body}] + summary + recent

    saved = cf.FINAL[sc]
    if message.strip():
        cf.FINAL[sc] = (message.strip(),) + saved[1:]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            cf.run_session(update, build)
    finally:
        cf.FINAL[sc] = saved
    r = lab_trace.EVENTS[-1]
    lines = [f"Scenario: {sc} · {len(cf.EVENTS[sc])} events; all but the last {cf.KEEP_RECENT} were summarised",
             f"Case facts in the prompt: {r['format']}"]
    if r["facts"] is not None:
        lines.append(f"```\n{json.dumps(r['facts'], ensure_ascii=False, indent=1)[:600]}\n```")
    lines += [f"Customer: {r['question']}", f"Agent: {r['reply']}"]
    notes = []
    if r["missing"]:
        why = {"none": "the facts only existed in the summarised history, which lost them",
               "prose": "the block is a friendly sentence, not data, so the exact values are gone",
               "json-flat": "one flat record: the last order's values overwrote the lamp's"}.get(r["format"])
        if why is None:
            why = ("the block still holds the first status it saw" if sc == "status_change"
                   else "what the customer said they need never made it into the block")
        notes.append(f"Missing {r['missing']}: {why}.")
    return {"lines": lines, "notes": notes, "ok": not notes}
