"""
SIMULATED model for D4.9 Prompt Engineering Techniques (guide TS 4.2 few-shot; TS 3.5 iterative refinement).

Grounding: guide TS 4.2 / 3.5 (read 2026-09-28) and the platform prompting best practices (fetched 2026-09-28): examples are
one of the most reliable ways to steer format, tone and structure; make them relevant, diverse (so Claude doesn't pick up
unintended patterns) and wrapped in <example> tags; 3–5 is the docs' suggestion (the guide: 2–4 targeted examples).
INVENTED (simulation) — deterministic rules standing in for model behaviour:
- output format is consistent only with ≥ 2 examples that each show every field;
- a NEW ambiguous request is routed correctly only if the examples explain why one tool beat a plausible alternative AND use
  more than one tool (all-same examples teach "always pick that tool");
- informal measurements are extracted only if the examples cover ≥ 2 different formats; otherwise the required field is null;
- iteration converges in 2 rounds when feedback names the failing test with expected vs actual, else it hasn't passed after 4;
- two interacting bugs are fixed in one round when described together; fixed one at a time they undo each other.
"""

from __future__ import annotations

import re

from utils import lab_trace

SCENARIO_IDS = ("format_consistency", "ambiguous_case", "informal_extraction", "test_driven", "interacting_issues")
SCENARIO = "format_consistency"
FIELDS = ("location", "issue", "severity", "fix")


def configure(scenario_id: str) -> None:
    global SCENARIO
    SCENARIO = scenario_id if scenario_id in SCENARIO_IDS else "format_consistency"


def _rec(**kw):
    rec = {"kind": "fewshot_run", "scenario": SCENARIO, **kw}
    lab_trace.record(rec)
    return rec


def review(examples: list) -> list:
    good = [e for e in examples if all(k in (e.get("output") or {}) for k in FIELDS)]
    consistent = len(good) >= 2
    raw = [("cart.py:57", "off-by-one drops the last item"), ("search.py:21", "SQL built from user input"), ("orders.py:88", "null not handled")]
    if consistent:
        out = [{"location": l, "issue": i, "severity": "major", "fix": "…"} for l, i in raw]
    else:
        out = [{"location": raw[0][0], "issue": raw[0][1]}, f"{raw[1][0]} — {raw[1][1]} (high)", {"problem": raw[2][1], "where": raw[2][0], "sev": 2}]
    ok = consistent
    _rec(task="review", examples=len(examples), complete_examples=len(good), output=out, ok=ok)
    print(f"{len(examples)} example(s), {len(good)} showing all of {list(FIELDS)}")
    for o in out:
        print("  ", o)
    print("→ " + ("every finding in the same shape" if ok else "three findings, three different shapes"))
    return out


_ROUTES = [("Summarise these web search results about heat pumps", "web", True),
           ("Pull the totals out of the attached PDF invoice", "doc", False),
           ("Turn these search results into a one-page brief", "web", True)]


def route(examples: list) -> str:
    tools = {e.get("tool") for e in examples}
    reasoned = [e for e in examples if re.search(r"\b(over|instead of|rather than|not)\b", e.get("why", "") or "", re.I)]
    novel = "Give me the key points from these news search results on EV batteries"
    if len(examples) >= 2 and len(reasoned) >= 2 and len(tools) >= 2:
        pick, why = "web", "it generalised: search RESULTS go to the web tool, whatever the wording"
    elif len(tools) == 1 and examples:
        pick, why = next(iter(tools)), f"every example used {next(iter(tools))} — it learned “always {next(iter(tools))}”"
    else:
        pick, why = "doc", "no reasoning to generalise from; “key points” looked like the document examples"
    ok = pick == "web"
    _rec(task="route", examples=len(examples), reasoned=len(reasoned), tools=sorted(t for t in tools if t), pick=pick, ok=ok)
    print(f"new request: “{novel}” → {pick} tool ({why})")
    return pick


INPUTS = ["about two metres", "6 ft 2 in", "150 cm", "roughly a metre and a half"]


def extract(examples: list) -> list:
    kinds = set()
    for e in examples:
        t = (e.get("text") or "").lower()
        kinds.add("imperial" if re.search(r"ft|foot|feet|in\b|inch", t) else "approx" if re.search(r"about|roughly|around|~", t)
                  else "metric")
    varied = len(kinds) >= 2
    values = {"about two metres": 2.0, "6 ft 2 in": 1.88, "150 cm": 1.5, "roughly a metre and a half": 1.5}
    out = [{"text": t, "height_m": (values[t] if (varied or t == "150 cm") else None)} for t in INPUTS]
    nulls = [o["text"] for o in out if o["height_m"] is None]
    _rec(task="extract", examples=len(examples), formats=sorted(kinds), nulls=nulls, ok=not nulls)
    print(f"example formats: {sorted(kinds) or 'none'}")
    for o in out:
        print("  ", o)
    return out


TESTS = [{"name": "test_null_email", "expected": "row skipped, warning logged", "got": "TypeError: NoneType"},
         {"name": "test_duplicate_id", "expected": "second row merged", "got": "IntegrityError"}]


def iterate(feedback_fn) -> int:
    fb = feedback_fn(TESTS) or ""
    specific = all(t["name"] in fb for t in TESTS) and ("expected" in fb.lower() and ("got" in fb.lower() or "actual" in fb.lower()))
    rounds = 2 if specific else None
    _rec(task="iterate", feedback=fb, specific=specific, rounds=rounds, ok=specific)
    print(f"feedback sent: “{fb}”")
    print(f"→ {'all tests pass after 2 rounds' if specific else 'still failing after 4 rounds — Claude is guessing at what is wrong'}")
    return rounds or 4


def fix(together: bool) -> bool:
    issues = ["the currency rounding in total()", "the tax step that relies on total()'s rounding"]
    if together:
        log = ["round 1: both issues described in one message → rounding and tax fixed together → tests pass"]
        ok = True
    else:
        log = ["round 1: fix rounding → the tax step now double-rounds", "round 2: fix tax → rounding change reverted",
               "round 3: fix rounding again → tax breaks again"]
        ok = False
    _rec(task="fix", together=together, log=log, ok=ok)
    print("\n".join(log))
    return ok
