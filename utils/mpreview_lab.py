"""
SIMULATED generator and reviewers for D4.10 Multi-Instance & Multi-Pass Review (guide TS 4.6).

Grounding: guide TS 4.6 (read 2026-09-28) and the platform prompting best practices (fetched 2026-09-28): the common chaining
pattern is self-correction — generate a draft, have Claude review it against criteria, refine — each step a separate API call
you can log and evaluate.
INVENTED (simulation) — deterministic stand-ins:
- a reviewer in the SAME session as the generator shares its reasoning ("I handled the empty page") and misses the page=0 bug,
  whatever it is told ("be critical") or however long it thinks; a NEW instance given only the code catches it;
- one pass over a 14-file PR dilutes attention: it misses local issues in files 5–10 and contradicts itself on file 3;
  per-file passes catch local issues but not the cross-file data flow (a field renamed in one file and read in another); an
  integration pass given the per-file summaries catches that;
- a verification pass attaches a confidence to each finding; these confidences are calibrated in this simulation.
"""

from __future__ import annotations

from utils import lab_trace

SCENARIO_IDS = ("self_review", "extended_thinking", "large_pr", "cross_file", "calibrated_routing")
SCENARIO = "self_review"

FILES = [f"src/orders/file_{i:02d}.py" for i in range(1, 15)]
LOCAL_BUGS = {"src/orders/file_02.py": "unchecked None", "src/orders/file_06.py": "off-by-one", "src/orders/file_08.py": "SQL from input",
              "src/orders/file_11.py": "timezone bug"}
CROSS_BUG = "file_04 renames total → amount; file_12 still reads total"
LOG: dict = {}


def configure(scenario_id: str) -> None:
    global SCENARIO
    SCENARIO = scenario_id if scenario_id in SCENARIO_IDS else "self_review"
    LOG.clear()
    LOG.update(passes=[], findings=[], routed=None, reviewer=None)


configure("self_review")


def generate(task: str) -> dict:
    """The generator writes the code; its session holds its reasoning."""
    return {"code": "def page(items, n, size): return items[(n - 1) * size : n * size]", "session": "gen-1",
            "reasoning": "pages are 1-based; I handled the empty page"}


def review(code: dict, session: str = "new", instructions: str = "", extended_thinking: bool = False) -> list:
    """session='same' reviews inside the generator's session (with its reasoning); 'new' is an independent instance."""
    same = session == "same"
    LOG["reviewer"] = {"session": session, "instructions": instructions, "extended_thinking": extended_thinking}
    found = [] if same else ["page(items, 0, size) returns items[-size:0] → an empty page instead of an error (n must be ≥ 1)"]
    LOG["findings"] += found
    LOG["passes"].append(f"review ({'same session as the generator' if same else 'independent instance, code only'}"
                         f"{', told: ' + instructions if instructions else ''}{', extended thinking' if extended_thinking else ''}) → {len(found)} finding(s)")
    return found


def one_pass_review(files: list) -> list:
    found = [f"{p}: {b}" for p, b in LOCAL_BUGS.items() if not ("05" <= p[-5:-3] <= "10")]
    found += ["src/orders/file_03.py: looks fine", "src/orders/file_03.py: missing validation"]   # contradictory
    LOG["findings"] += found
    LOG["passes"].append(f"one pass over {len(files)} files → {len(found)} findings (files 5–10 skimmed; file_03 judged both ways)")
    return found


def per_file_review(path: str) -> list:
    found = [f"{path}: {LOCAL_BUGS[path]}"] if path in LOCAL_BUGS else []
    LOG["findings"] += found
    LOG["passes"].append(f"per-file pass {path.split('/')[-1]} → {len(found)}")
    return found


def integration_review(files: list, summaries: list) -> list:
    found = [CROSS_BUG] if summaries is not None and len(files) > 1 else []
    LOG["findings"] += found
    LOG["passes"].append(f"integration pass over {len(files)} files with {len(summaries or [])} per-file summaries → {len(found)}")
    return found


CANDIDATES = [("cart.py:57 off-by-one", True, 0.93), ("search.py:21 SQL from input", True, 0.97), ("util.py:3 unused variable?", False, 0.41),
              ("orders.py:88 possible None", True, 0.72), ("api.py:10 naming", False, 0.30), ("tax.py:5 rounding", True, 0.88)]


def verify(findings: list, with_confidence: bool = True) -> list:
    out = [{"finding": f, "real": r, **({"confidence": c} if with_confidence else {})} for f, r, c in CANDIDATES]
    LOG["passes"].append(f"verification pass → {len(out)} findings{' with a confidence each' if with_confidence else ''}")
    return out


def route(verified: list, auto_post_at: float | None = 0.8) -> dict:
    auto, human = [], []
    for v in verified:
        c = v.get("confidence")
        (auto if (auto_post_at is not None and c is not None and c >= auto_post_at) or auto_post_at is None else human).append(v)
    LOG["routed"] = {"auto": [a["finding"] for a in auto], "human": [h["finding"] for h in human],
                     "auto_false": [a["finding"] for a in auto if not a["real"]], "human_load": len(human)}
    LOG["passes"].append(f"routing: {len(auto)} auto-posted, {len(human)} to a human")
    return LOG["routed"]


def finish() -> None:
    all_found = " ".join(LOG["findings"])
    rec = {"kind": "mpreview_run", "scenario": SCENARIO, "passes": list(LOG["passes"]), "findings": list(LOG["findings"]),
           "routed": LOG["routed"], "reviewer": LOG["reviewer"],
           "caught_gen_bug": "empty page" in all_found,
           "local_caught": sorted(p for p in LOCAL_BUGS if p in all_found),
           "cross_caught": CROSS_BUG in all_found,
           "contradictions": "looks fine" in all_found and "missing validation" in all_found}
    lab_trace.record(rec)
    print("\n".join(rec["passes"]))
    for f in rec["findings"]:
        print("  •", f)
    if rec["routed"]:
        print(f"routed: {rec['routed']}")
