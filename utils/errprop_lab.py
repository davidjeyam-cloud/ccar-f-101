"""
SIMULATED multi-agent research for D5.3 Error Propagation (guide TS 5.3).

Grounding: guide TS 5.3 (read 2026-11-14, pp.21): structured error context (failure type, attempted query, partial results,
alternatives) lets the coordinator recover (Knowledge 1); access failures are not valid empty results (Knowledge 2); generic
statuses hide context (Knowledge 3); suppressing errors and terminating the whole workflow are both anti-patterns (Knowledge 4);
subagents recover locally from transient failures and propagate only what they cannot resolve (Skill 3); synthesis carries
coverage annotations (Skill 4). Official docs (fetched 2026-11-14): a tool failure goes back as a tool_result with is_error and an
instructive message, a subagent's final message is all that returns to its parent, and the Agent SDK ends a run with a typed
result subtype that must be checked before the result is read.
INVENTED (simulation): the topics, the findings, which searches fail and how, and the coordinator's recovery policy. The coordinator
here is deterministic code, not a model, so each effect is repeatable. Nothing here calls a real search tool.
"""

from __future__ import annotations

from collections import Counter

from utils import lab_trace

SCENARIO_IDS = ("timeout_alt", "empty_valid", "transient", "partial_gap")
SCENARIO = "timeout_alt"
TOPICS = ("visual arts", "music", "film")


class SearchError(Exception):
    """A search that could not be completed: an ACCESS failure (timeout, source down), never a valid empty result."""

    def __init__(self, failure_type: str, partial: list | None = None):
        super().__init__(failure_type)
        self.failure_type = failure_type
        self.partial = list(partial or [])


def _f(claim, source, date):
    return {"claim": claim, "source": source, "date": date}


_FINDINGS = {
    "visual arts": [_f("Illustrators report AI tools now draft most concept art.", "Studio Survey A", "2025-03"),
                    _f("Stock-image platforms added AI-labelled galleries.", "Platform Report B", "2025-06")],
    "music": [_f("Streaming services label AI-generated tracks.", "Industry Brief C", "2025-02"),
              _f("Session musicians report fewer jobs for jingles.", "Union Study D", "2025-05"),
              _f("Labels use AI for stem separation and mastering.", "Trade Journal E", "2025-08")],
    "film": [_f("Studios use AI for previsualisation and de-ageing.", "Film Review F", "2025-04"),
             _f("Guild contracts now cover digital replicas.", "Guild Notice G", "2025-07")],
}
_ARCHIVE = {"music": [_f("Archive: broadcast radio logs show a rise in AI-assisted playlists.", "News Archive H", "2025-01")]}

# per scenario: topic -> what each successive web call does ("ok" | "timeout" | "partial" | "empty"); the last step repeats
_PLAN = {
    "timeout_alt": {"music": ["timeout"]},
    "empty_valid": {"film": ["empty"]},
    "transient": {"music": ["timeout", "ok"]},
    "partial_gap": {"music": ["partial"]},
}
_ARCHIVE_WORKS = {"timeout_alt": True, "empty_valid": False, "transient": True, "partial_gap": False}
KNOWN_ALTERNATIVES = ("news_archive",)

_CALLS: Counter = Counter()


def configure(scenario_id: str) -> None:
    global SCENARIO
    SCENARIO = scenario_id if scenario_id in SCENARIO_IDS else "timeout_alt"
    _CALLS.clear()


def web_search(topic: str) -> list:
    """The primary search. Returns findings; [] is a VALID empty result. Raises SearchError for an access failure."""
    _CALLS[topic] += 1
    plan = _PLAN[SCENARIO].get(topic, ["ok"])
    step = plan[min(_CALLS[topic], len(plan)) - 1]
    if step == "timeout":
        raise SearchError("timeout")
    if step == "partial":
        raise SearchError("timeout", partial=_FINDINGS[topic][:2])
    if step == "empty":
        return []
    return list(_FINDINGS[topic])


def _alternative(topic: str, approach: str) -> list:
    """What the coordinator gets when it tries an alternative approach (only a known one can work)."""
    if approach in KNOWN_ALTERNATIVES and _ARCHIVE_WORKS[SCENARIO]:
        return list(_ARCHIVE.get(topic, []))
    return []


def _coordinate(topic: str, r, tally: dict) -> tuple:
    """The coordinator's deterministic recovery policy. Returns (findings, coverage entry)."""
    status = r.get("status") if isinstance(r, dict) else None
    if status == "ok":
        return list(r.get("findings", [])), {"status": "supported"}
    if status == "empty":
        return [], {"status": "none_found"}
    if status != "error":
        tally["invalid"] += 1
        return [], {"status": "gap", "reason": "the subagent returned something the coordinator cannot read"}
    tally["errors"] += 1
    failure, attempted = r.get("failure_type"), r.get("attempted")
    if not failure or not attempted:                      # a generic status: nothing to base a decision on
        tally["generic"] += 1
        return [], {"status": "gap", "reason": r.get("message") or "no reason given"}
    alts, partial = r.get("alternatives") or [], r.get("partial") or []
    if alts:                                              # recovery decision 1: try an alternative approach
        tally["round_trips"] += 1
        got = _alternative(topic, alts[0])
        if got:
            return got, {"status": "supported", "via": alts[0]}
    if partial:                                           # recovery decision 2: proceed with what was found
        return list(partial), {"status": "partial", "reason": failure, "found": len(partial)}
    return [], {"status": "gap", "reason": failure}


def run_research(search_subagent, synthesize) -> dict | None:
    """Plays the research run. Your search_subagent(topic) is called once per topic and returns a result dict; the coordinator
    decides from it; your synthesize(findings, coverage) writes the report. An exception from a subagent ends the whole run."""
    _CALLS.clear()
    results = []
    for topic in TOPICS:
        try:
            results.append((topic, search_subagent(topic)))
        except Exception as exc:                          # the top-level handler: the whole workflow stops here
            rec = {"kind": "errprop_run", "scenario": SCENARIO, "terminated": f"{type(exc).__name__}: {exc}", "topic": topic,
                   "report": None, "coverage": None, "round_trips": 0, "errors": 0, "generic": 0, "calls": dict(_CALLS)}
            lab_trace.record(rec)
            print(f"WORKFLOW TERMINATED by an unhandled {type(exc).__name__} in the '{topic}' subagent: nothing was reported.")
            return None
    tally = Counter()
    findings, coverage = {}, {}
    for topic, r in results:
        findings[topic], coverage[topic] = _coordinate(topic, r, tally)
    report = synthesize(findings, coverage)
    shown = report.get("coverage") if isinstance(report, dict) else None
    rec = {"kind": "errprop_run", "scenario": SCENARIO, "terminated": None, "report": report, "coverage": shown,
           "truth": coverage, "round_trips": tally["round_trips"], "errors": tally["errors"], "generic": tally["generic"],
           "invalid": tally["invalid"], "calls": dict(_CALLS)}
    lab_trace.record(rec)
    for topic in TOPICS:
        c = (shown or {}).get(topic) if isinstance(shown, dict) else None
        print(f"{topic}: {c['status'] if c else 'not annotated'}" + (f" ({c.get('reason') or c.get('via')})" if c and (c.get('reason') or c.get('via')) else ""))
    print(f"errors reaching the coordinator: {tally['errors']} · coordinator round trips: {tally['round_trips']}")
    return report


# What a correct run reports, per scenario: the coverage status of each topic, and how many coordinator round trips it costs.
_ALL_OK = {"visual arts": "supported", "music": "supported", "film": "supported"}
EXPECTED = {
    "timeout_alt": (_ALL_OK, 1),                                         # the alternative recovers music
    "empty_valid": ({**_ALL_OK, "film": "none_found"}, 0),               # film worked and matched nothing
    "transient": (_ALL_OK, 0),                                           # recovered locally; the coordinator never hears of it
    "partial_gap": ({**_ALL_OK, "music": "partial"}, 1),                 # two findings kept, the gap shown
}


def diagnose(rec: dict | None) -> tuple:
    """(ok, bug key or None, one-line description of what the run showed) for an errprop_run event."""
    if rec is None:
        return False, None, "nothing ran"
    sc = rec["scenario"]
    if rec["terminated"]:
        return False, "TERMINATE", f"workflow terminated ({rec['terminated'][:60]}) - no report at all"
    cov = rec["coverage"]
    if not isinstance(cov, dict):
        return False, "NOCOVER", "the report has no coverage annotations, so it reads as complete"
    want, want_rt = EXPECTED[sc]
    got = {t: (cov.get(t) or {}).get("status", "missing") for t in TOPICS}
    txt = (f"coverage {got} · errors that reached the coordinator: {rec['errors']} · coordinator round trips: "
           f"{rec['round_trips']}")
    if got == want and rec["round_trips"] == want_rt:
        return True, None, txt
    if rec.get("generic"):
        return False, "GENERIC", txt
    if sc == "empty_valid" and got.get("film") == "gap":
        return False, "EMPTYERR", txt
    if any(got[t] == "none_found" and want[t] != "none_found" for t in TOPICS):
        return False, "SUPPRESS", txt
    if sc == "transient" and rec["errors"]:
        return False, "NOLOCAL", txt
    return False, None, txt
