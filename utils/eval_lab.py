"""
SIMULATED tool-evaluation lab for D2.5 Tool Evaluation & Testing: you write a test set, per-category success criteria, a
grader and a release decision; the lab runs your suite through the SIMULATED tool router from D2.1 (utils/tool_select_lab.py)
and then shows what the same tool set does on "production traffic" you didn't write — so a release decision can be checked.

Grounding: guide §7 (p.24: test tool-selection reliability with ambiguous requests) and TS 2.1; platform docs
test-and-evaluate/develop-tests (specific + measurable criteria, task-specific evals with edge cases, automate grading,
volume over quality, multidimensional criteria, exact-match grading for categorical answers) and tool-use troubleshooting
(wrong tool → sharpen descriptions; wrong parameters → strict / input_examples) — fetched 2026-09-28.
INVENTED (simulation): the router's scoring (see tool_select_lab), the three tool-set versions, the production traffic and the
90 % per-category bar used to judge a release as good or bad.
"""

from __future__ import annotations

import copy
import re

from utils import lab_trace
from utils.tool_select_lab import KIND, route

SCENARIO_IDS = ("ambiguous_traffic", "fixed_tools", "regression")
SCENARIO = "ambiguous_traffic"
PROD_BAR = 0.90

SYSTEM = "You are a research and support assistant. Choose the tool whose description matches the input you were given."


def _good_tools():
    from utils.concepts_content import tool_calling as tc
    ns: dict = {}
    exec(tc.CORRECT.split("\nevaluate(")[0].replace("from utils.tool_select_lab import evaluate", ""), ns)
    return ns["TOOLS"]


def _v1(good):
    """A vague web tool ("Analyzes content.") beside the document tools, and no "not for web results" boundaries —
    requests about web search results can't be told apart from document requests and misroute."""
    v = copy.deepcopy(good)
    for t in v:
        if t["name"] == "extract_web_results":
            t.update(name="analyze_content", description="Analyzes content.",
                     input_schema={"type": "object", "properties": {"content": {"type": "string"}}, "required": ["content"]})
        t["description"] = " ".join(x for x in re.split(r"(?<=[.])\s+", t["description"]) if "web" not in x.lower())
    v.sort(key=lambda t: t["name"] != "summarize_content")
    return v


def _v3(good):
    """Descriptions fixed for web vs documents — but lookup_order lost its 'ORD-####' formatting sentence."""
    v = copy.deepcopy(good)
    for t in v:
        if t["name"] == "lookup_order":
            t["description"] = ("Looks up one order's status, amount and delivery date by its order id. Returns status and "
                                "amount, not customer details. Do not use it when you only have an email address - use "
                                "get_customer first.")
            t["input_schema"]["properties"]["order_id"]["description"] = "The order id"
    return v


KIND.setdefault("analyze_content", "web")

_GOOD = None


def versions():
    global _GOOD
    if _GOOD is None:
        _GOOD = _good_tools()
    return {"v1": _v1(_GOOD), "v2": copy.deepcopy(_GOOD), "v3": _v3(_GOOD)}


CANDIDATE_OF = {"ambiguous_traffic": "v1", "fixed_tools": "v2", "regression": "v3"}

PRODUCTION = [   # traffic the tool set will actually meet — you never see it before release
    ("Can you check whether the attached audit backs up the claim that costs dropped?", "verify", None, "clear"),
    ("Pull every amount and due date from the uploaded invoice PDF.", "extract", None, "clear"),
    ("Which orders does dave@example.com have?", "customer", None, "clear"),
    ("Summarize the attached board report for me.", "summarize", None, "clear"),
    ("Extract the main facts from these web search results about EV chargers.", "web", None, "ambiguous"),
    ("Make a short summary of these web search results for the newsletter.", "web", None, "ambiguous"),
    ("What do these web results say about battery recycling? key facts please", "web", None, "ambiguous"),
    ("Status of order 3003?", "order", {"order_id": "ORD-3003"}, "edge"),
    ("has order 4004 been delivered", "order", {"order_id": "ORD-4004"}, "edge"),
]


def configure(scenario_id: str) -> None:
    global SCENARIO
    SCENARIO = scenario_id if scenario_id in CANDIDATE_OF else "ambiguous_traffic"


def job(tool_name) -> str:
    """The job a tool actually does in the fake backend (web / summarize / extract / verify / order / customer)."""
    return KIND.get(tool_name, "unknown")


def _run(cases, grade, tools):
    rows = []
    for c in cases:
        r = route(c["request"], tools, SYSTEM)
        ok = bool(grade(c, {"tool": r["tool"], "input": r["input"], "tie": r["ambiguous"]}))
        rows.append({"request": c["request"], "category": c.get("category", "?"), "expect": c.get("expect"),
                     "tool": r["tool"], "input": r["input"], "passed": ok, "tie": r["ambiguous"]})
    return rows


def _report(rows):
    rep = {}
    for r in rows:
        d = rep.setdefault(r["category"], {"n": 0, "passed": 0})
        d["n"] += 1
        d["passed"] += r["passed"]
    for d in rep.values():
        d["accuracy"] = round(d["passed"] / d["n"], 2)
    total = sum(d["n"] for d in rep.values())
    rep["_overall"] = {"n": total, "passed": sum(d["passed"] for k, d in rep.items() if k != "_overall"),
                       "accuracy": round(sum(r["passed"] for r in rows) / total, 2) if total else 0.0}
    return rep


def production_check(tools):
    """Truth: how the tool set does on real traffic, per category (graded exactly: right job AND right input)."""
    cats = {}
    for req, kind, inp, cat in PRODUCTION:
        r = route(req, tools, SYSTEM)
        ok = job(r["tool"]) == kind and (inp is None or r["input"] == inp)
        d = cats.setdefault(cat, [0, 0])
        d[0] += ok
        d[1] += 1
    acc = {c: round(p / n, 2) for c, (p, n) in cats.items()}
    return acc, all(a >= PROD_BAR for a in acc.values())


def release(test_set, grade, decide, select_cases=None) -> bool:
    """Run your suite on the candidate tool set, decide ship / block, then compare with production."""
    v = versions()
    select_cases = select_cases or (lambda ts, failures: ts)
    baseline_failures = []
    if SCENARIO == "regression":
        base = _run(test_set, grade, v["v1"])
        baseline_failures = [c for c, r in zip(test_set, base) if not r["passed"]]
        print(f"baseline v1: {sum(r['passed'] for r in base)}/{len(base)} passed · failing: "
              f"{[c['request'][:40] for c in baseline_failures]}")
    cand = CANDIDATE_OF[SCENARIO]
    # select_cases only matters AFTER a change (the regression scenario); a first release runs the whole set
    cases = list(select_cases(test_set, baseline_failures)) if SCENARIO == "regression" else list(test_set)
    rows = _run(cases, grade, v[cand])
    if SCENARIO == "regression" and len(cases) < len(test_set):
        # an incremental re-run: cases you didn't re-run keep LAST run's (stale) result on the old version
        stale = [dict(r, stale=True) for c, r in zip(test_set, base) if c not in cases]
        print(f"reused {len(stale)} results from the v1 run without re-running them on {cand}")
        rows = rows + stale
    rep = _report(rows)
    ship = bool(decide({k: dict(d) for k, d in rep.items() if k != "_overall"} | {"_overall": rep["_overall"]}))
    prod_acc, prod_ok = production_check(v[cand])
    for r in rows:
        print(f"  {'✓' if r['passed'] else '✗'} [{r['category']}] {r['request'][:70]} → {r['tool']}{r['input'] or ''}")
    print("report: " + " · ".join(f"{k} {d['passed']}/{d['n']} ({d['accuracy']:.0%})" for k, d in rep.items()))
    print(f"decision on {cand}: {'SHIP' if ship else 'BLOCK'}")
    print(f"production per category: {prod_acc} → the release is {'GOOD' if prod_ok else 'BAD'}")
    lab_trace.record({"kind": "eval_release", "scenario": SCENARIO, "candidate": cand, "cases_run": len(cases),
                      "categories": sorted(k for k in rep if k != "_overall"), "report": rep, "ship": ship,
                      "prod": prod_acc, "prod_ok": prod_ok, "rows": rows,
                      "baseline_failures": len(baseline_failures), "test_set_size": len(test_set)})
    return ship
