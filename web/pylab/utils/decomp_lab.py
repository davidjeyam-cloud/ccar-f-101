"""
SIMULATED backend for D1.8 Task Decomposition: (1) a multi-file code review — predictable, so a fixed chain of steps
(per-file passes, then a cross-file integration pass) fits; (2) "add tests to a legacy codebase" — open-ended, so an
adaptive plan fits (map the structure, prioritise, turn discovered dependencies into new subtasks).

Grounding: guide TS 1.6 (p.8) — prompt chaining vs dynamic adaptive decomposition; per-file passes + a cross-file
integration pass to avoid attention dilution; map → prioritise → adapt for open-ended tasks. Docs (fetched 2026-09-27):
prompt chaining is useful to inspect intermediate outputs or enforce a pipeline (platform prompting best practices § Chain
complex prompts); use subagents for parallel, independent work and work directly for sequential or simple tasks (§ Subagent
orchestration); performance degrades as the context fills (code.claude.com best-practices).
INVENTED (simulation): the files and planted issues, the "3 files per pass" attention limit, the modules, their risk, the
FakeClock dependency and the action budget.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from utils import lab_trace

SCENARIO_IDS = ("large_review", "small_review", "legacy_tests")
ATTENTION = 3          # simulated: a single pass examines at most this many files in full

_LARGE = ["README.md", "config.py", "logging_setup.py", "currency.py", "customers.py", "search.py", "inventory.py", "shipping.py",
          "export.py", "pricing.py", "orders.py", "reports.py", "auth.py", "notifications.py"]
_SMALL = ["currency.py", "pricing.py", "orders.py"]
_LOCAL = {"currency.py": "currency.py: rounds money with float arithmetic",
          "search.py": "search.py: SQL built by string concatenation (injection risk)",
          "export.py": "export.py: file handle never closed"}
_CROSS = "orders.py ↔ pricing.py: orders still calls pricing.total(items) but total now requires (items, currency)"
_SUMMARY = {"pricing.py": "pricing.py exports total(items, currency)", "orders.py": "orders.py calls pricing.total(items)"}

_MODULES = [  # the legacy codebase, as mapping reveals it
    {"name": "auth", "risk": "high", "why": "every request passes through it"},
    {"name": "legacy_export", "risk": "low", "why": "used once a quarter"},
    {"name": "orders", "risk": "high", "why": "changes weekly; many callers"},
    {"name": "payments", "risk": "high", "why": "moves money"},
    {"name": "reports", "risk": "low", "why": "read-only"},
    {"name": "string_utils", "risk": "low", "why": "small, stable"},
]
_NEEDS = {"payments": "FakeClock"}
MODULE_NAMES = sorted(m["name"] for m in _MODULES)   # known up front: the folder names (not their risk)

TASK = "review"
FILES: list = []
BUDGET = 6
STATE = {"used": 0, "helpers": set(), "tested": []}


def configure(scenario_id: str) -> None:
    global TASK, FILES
    TASK = "tests" if scenario_id == "legacy_tests" else "review"
    FILES = list(_SMALL if scenario_id == "small_review" else _LARGE)
    STATE.update({"used": 0, "helpers": set(), "tested": []})


def expected_issues() -> set:
    return {v for k, v in _LOCAL.items() if k in FILES} | ({_CROSS} if {"orders.py", "pricing.py"} <= set(FILES) else set())


@dataclass
class Review:
    issues: list
    summary: dict = field(default_factory=dict)


def _examine(paths, cross_requested: bool):
    seen = paths[:ATTENTION]
    issues = [_LOCAL[p] for p in seen if p in _LOCAL]
    if cross_requested and {"orders.py", "pricing.py"} <= set(seen):
        issues.append(_CROSS)
    return seen, issues


def review_file(path: str) -> Review:
    """One pass over ONE file: its local issues plus a summary of its interface (for a later integration pass)."""
    _, issues = _examine([path], False)
    lab_trace.record({"kind": "review_pass", "files": [path], "examined": [path], "found": issues, "type": "per_file"})
    return Review(issues, {path: _SUMMARY[path]} if path in _SUMMARY else {})


def review_files(paths: list, instructions: str = "") -> Review:
    """One pass over SEVERAL files at once (attention is spread across all of them)."""
    cross = any(w in instructions.lower() for w in ("cross-file", "integration", "between files"))
    seen, issues = _examine(list(paths), cross)
    lab_trace.record({"kind": "review_pass", "files": list(paths), "examined": seen, "found": issues, "type": "multi"})
    return Review(issues)


def integration_pass(summaries: list) -> list:
    """A separate cross-file pass over the per-file interface summaries."""
    merged = {}
    for s in summaries:
        merged.update(s or {})
    found = [_CROSS] if {"orders.py", "pricing.py"} <= set(merged) else []
    lab_trace.record({"kind": "review_pass", "files": sorted(merged), "examined": sorted(merged), "found": found, "type": "integration"})
    return found


def map_structure() -> list:
    """Step 1 of an open-ended task: map the codebase (costs one action)."""
    STATE["used"] += 1
    lab_trace.record({"kind": "plan_step", "action": "map_structure", "used": STATE["used"]})
    return [dict(m) for m in _MODULES]


def _spend(action: str) -> bool:
    if STATE["used"] >= BUDGET:
        lab_trace.record({"kind": "plan_step", "action": action, "used": STATE["used"], "result": "OUT OF BUDGET"})
        return False
    STATE["used"] += 1
    return True


def write_tests(module: str) -> str:
    if not _spend(f"write_tests({module})"):
        return "OUT OF BUDGET"
    need = _NEEDS.get(module)
    if need and need not in STATE["helpers"]:
        res = f"BLOCKED: {module} reads the system clock directly - its tests need a {need} helper first"
    else:
        STATE["tested"].append(module)
        res = f"tests added for {module}"
    lab_trace.record({"kind": "plan_step", "action": f"write_tests({module})", "used": STATE["used"], "result": res})
    return res


def create_helper(name: str) -> str:
    if not _spend(f"create_helper({name})"):
        return "OUT OF BUDGET"
    STATE["helpers"].add(name)
    lab_trace.record({"kind": "plan_step", "action": f"create_helper({name})", "used": STATE["used"], "result": "created"})
    return f"{name} created"


def submit(result) -> None:
    items = list(result) if isinstance(result, (list, tuple, set)) else [result]
    lab_trace.record({"kind": "submit", "items": [str(x) for x in items], "tested": list(STATE["tested"]), "used": STATE["used"]})
    print("SUBMITTED:", items)
