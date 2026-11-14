"""
Playground engine for D5.3 Error Propagation, on the SIMULATED research run in utils/errprop_lab.py. The message box holds the
research question (the simulation ignores its wording); each tab plays the scenario its sub-concept is about, and its knobs change
how the subagent reports a failure and how the synthesis is written. Pass/fail comes from errprop_lab.diagnose, the same check the
code lab uses.
"""

from __future__ import annotations

import contextlib
import io
from dataclasses import dataclass

from utils import errprop_lab as el
from utils import lab_trace


@dataclass
class ErrPropConfig:
    mode: str = "context"
    ep_context: str = "full"        # full | generic
    ep_partial: str = "keep"        # keep | drop
    ep_empty: str = "valid"         # valid | error
    ep_local: str = "retry"         # retry | none
    ep_failure: str = "structured"  # structured | suppress | terminate
    ep_coverage: str = "annotate"   # annotate | none


_SCENARIO = {"context": "timeout_alt", "partial": "partial_gap", "empty": "empty_valid", "local": "transient",
             "anti": "partial_gap", "coverage": "partial_gap"}

_WHY = {
    "GENERIC": "the subagent sent only “search unavailable”, so the coordinator could not choose a recovery",
    "SUPPRESS": "the failure was returned as an empty result, so the report says nothing was found",
    "TERMINATE": "an exception ended the whole workflow, so even the topics that worked were lost",
    "EMPTYERR": "a search that worked and found nothing was reported as a failure",
    "NOLOCAL": "a one-off failure was propagated instead of being retried inside the subagent",
    "NOCOVER": "the report carries no coverage annotations, so it reads as complete",
}


def run_errprop(message: str, cfg: ErrPropConfig) -> dict:
    lab_trace.reset()
    sc = _SCENARIO.get(cfg.mode, "timeout_alt")
    el.configure(sc)

    def subagent(topic):
        attempted, failure, partial = [], None, []
        for attempt in range(2 if cfg.ep_local == "retry" else 1):
            attempted.append(f"web search: {topic} (attempt {attempt + 1})")
            try:
                hits = el.web_search(topic)
            except el.SearchError as err:
                if cfg.ep_failure == "terminate":
                    raise
                failure, partial = err.failure_type, err.partial
                continue
            if not hits:
                if cfg.ep_empty == "error":
                    return {"status": "error", "topic": topic, "failure_type": "no_results", "attempted": attempted,
                            "partial": [], "alternatives": ["news_archive"]}
                return {"status": "empty", "topic": topic, "query": topic}
            return {"status": "ok", "topic": topic, "findings": hits}
        if cfg.ep_failure == "suppress":
            return {"status": "empty", "topic": topic, "query": topic}
        if cfg.ep_context == "generic":
            return {"status": "error", "message": "search unavailable"}
        return {"status": "error", "topic": topic, "failure_type": failure, "attempted": attempted,
                "partial": partial if cfg.ep_partial == "keep" else [], "alternatives": ["news_archive"]}

    def synthesize(findings, coverage):
        claims = [f"{f['claim']} ({f['source']}, {f['date']})" for hits in findings.values() for f in hits]
        return {"claims": claims, "coverage": coverage} if cfg.ep_coverage == "annotate" else {"claims": claims}

    with contextlib.redirect_stdout(io.StringIO()):
        el.run_research(subagent, synthesize)
    rec = next((e for e in reversed(lab_trace.EVENTS) if e["kind"] == "errprop_run"), None)
    ok, bug, text = el.diagnose(rec)
    want_cov, want_rt = el.EXPECTED[sc]
    lines = [f"Question: {message.strip() or '(none)'}",
             f"Scenario: {sc} · what a correct run reports: {want_cov} with {want_rt} coordinator round trip(s)"]
    if rec and rec["terminated"]:
        lines.append(f"Result: workflow terminated ({rec['terminated'][:80]}); no report was produced")
    elif rec:
        lines.append(f"Report: {len((rec['report'] or {}).get('claims', []))} claim(s)")
        lines.append(text)
        if rec["truth"]:
            lines.append("What the coordinator concluded per topic: "
                         + "; ".join(f"{t}: {c['status']}" for t, c in rec["truth"].items()))
    if ok:
        notes = []
    elif bug in _WHY:
        notes = [f"{_WHY[bug]}."]
    elif cfg.mode == "partial" and cfg.ep_partial == "drop":
        notes = ["the two partial findings were dropped, so music is a bare gap instead of “partial” with what was found."]
    else:
        notes = ["The run does not match what a correct one reports."]
    return {"lines": lines, "notes": notes, "ok": ok}
