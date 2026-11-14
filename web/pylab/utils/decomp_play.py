"""
Playground engine for D1.8 Task Decomposition, on the SIMULATED backend in utils/decomp_lab.py. The typed task decides which
backend runs: "review" → the reviewer; "test" / "legacy" → the legacy codebase.
"""

from __future__ import annotations

from dataclasses import dataclass

from utils import decomp_lab as dl
from utils import lab_trace


@dataclass
class DecompConfig:
    mode: str = "review"          # review | plan | pick
    strategy: str = "chain"       # review: single | per_file | chain
    n_files: int = 14             # review: 3 or 14
    plan: str = "adaptive"        # plan: fixed | mapped | adaptive
    budget: int = 6
    pattern: str = "chaining"     # pick: chaining | dynamic


def _review(strategy, n):
    dl.configure("small_review" if n <= 3 else "large_review")
    files, lines = dl.FILES, []
    if strategy == "single":
        issues = dl.review_files(files, "Review all of these files, including cross-file mismatches.").issues
        lines.append(f"1 pass over {len(files)} files (attention reaches {min(len(files), dl.ATTENTION)} of them).")
    elif strategy == "picky":
        picked = [p for p in files if any(w in p for w in ("pay", "pric", "order", "auth", "currency"))]
        per = [dl.review_file(p) for p in picked]
        issues = [i for r in per for i in r.issues] + dl.integration_pass([r.summary for r in per])
        lines.append(f"Adaptive picking reviewed {len(picked)} of {len(files)} files: {picked}.")
    else:
        per = [dl.review_file(p) for p in files]
        issues = [i for r in per for i in r.issues]
        lines.append(f"{len(files)} per-file passes.")
        if strategy == "chain":
            issues += dl.integration_pass([r.summary for r in per])
            lines.append("+ 1 cross-file integration pass over the per-file summaries.")
    want = dl.expected_issues()
    got = want & set(issues)
    return {"lines": lines, "items": issues, "ok": got == want, "score": f"{len(got)}/{len(want)} planted issues found",
            "missed": sorted(want - got)}


def _tests(plan, budget):
    dl.configure("legacy_tests")
    dl.BUDGET = budget
    lines = []
    if plan == "fixed":
        order = list(dl.MODULE_NAMES)
        lines.append(f"Fixed plan, no mapping: {order}")
    else:
        mods = dl.map_structure()
        order = [m["name"] for m in sorted(mods, key=lambda m: m["risk"] != "high")]
        lines.append(f"Mapped, high-impact first: {order}")
    while order:
        name = order.pop(0)
        res = dl.write_tests(name)
        lines.append(f"{name}: {res}")
        if res.startswith("OUT OF BUDGET"):
            break
        if res.startswith("BLOCKED") and plan == "adaptive":
            helper = res.split("need a ")[1].split(" helper")[0]
            lines.append(f"   adapt → {dl.create_helper(helper)}; retry {name}")
            order.insert(0, name)
    tested = set(dl.STATE["tested"])
    high = {"auth", "orders", "payments"}
    dl.BUDGET = 6
    return {"lines": lines, "items": sorted(tested), "ok": high <= tested,
            "score": f"high-impact tested: {sorted(tested & high)} of {sorted(high)}", "missed": sorted(high - tested)}


def run_decomp(message: str, cfg: DecompConfig) -> dict:
    lab_trace.reset()
    low = message.lower()
    is_tests = ("test" in low or "legacy" in low) and "review" not in low
    if cfg.mode == "review":
        return _review(cfg.strategy, cfg.n_files)
    if cfg.mode == "plan":
        return _tests(cfg.plan, cfg.budget)
    if is_tests:
        out = _tests("adaptive" if cfg.pattern == "dynamic" else "fixed", 6)
    else:
        out = _review("chain" if cfg.pattern == "chaining" else "picky", 14)
    out["lines"].insert(0, f"Task type: {'open-ended (tests)' if is_tests else 'predictable (review)'} · pattern: {cfg.pattern}")
    return out
