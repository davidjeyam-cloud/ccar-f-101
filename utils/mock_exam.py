"""
Timed-mock logic (pages/07a_Timed_Mock.py): draw an exam from the question bank and grade it. Pure Python, no Streamlit.

Shape follows the guide's exam format (CLAUDE.md "Exam at a glance"): 60 single-answer items, 4 scenarios drawn at
random from the 6, 120 minutes, domain weights 27/18/20/20/15. The draw gives each domain its weighted share of the
60 items, taken from questions whose first scenario is one of the 4 chosen.
"""

import random
from dataclasses import dataclass

from utils import mcq_bank

ITEMS = 60
MINUTES = 120
WEIGHTS = {1: 27, 2: 18, 3: 20, 4: 20, 5: 15}
PASS_SCALED = 720
# The guide states 720 as the passing score on a 100-1,000 scale but not the conversion from percent correct.
# This straight-line map is only a rough guide so the report has the same shape as the real one.
SCALE_NOTE = ("Estimated: a straight line from percent correct to the 100-1,000 scale. The guide gives the pass mark (720) "
              "but not the real conversion, so treat this as a rough guide, not a prediction.")


def domain_of(q) -> int:
    return int(q.points[0].split(".")[0])


def quotas(items: int = ITEMS) -> dict:
    """Largest-remainder split of `items` by the domain weights (60 -> 16/11/12/12/9)."""
    raw = {d: items * w / 100 for d, w in WEIGHTS.items()}
    out = {d: int(v) for d, v in raw.items()}
    for d in sorted(raw, key=lambda d: raw[d] - out[d], reverse=True)[: items - sum(out.values())]:
        out[d] += 1
    return out


def all_questions() -> list:
    return [q for mod in mcq_bank.load().values() for q in mod.QUESTIONS]


def draw(seed: int | None = None, pool: list | None = None) -> dict:
    """-> {"scenarios": [4 numbers], "ids": [60 ids], "short": {domain: missing items}}.
    `short` is non-empty only if the chosen scenarios hold too few questions for a domain; the gap is then filled from the
    other scenarios, and the page says so."""
    rng = random.Random(seed)
    pool = pool if pool is not None else all_questions()
    need = quotas()

    def by_dom(scs):
        out = {d: [] for d in WEIGHTS}
        for q in pool:
            if q.scenarios[0] in scs:
                out[domain_of(q)].append(q)
        return out

    options = [sorted(rng.sample(range(1, 7), 4)) for _ in range(300)]
    scs = next((o for o in options if all(len(v) >= need[d] for d, v in by_dom(o).items())), options[0])
    chosen_pool = by_dom(scs)
    picked, short = [], {}
    for d, n in need.items():
        have = rng.sample(chosen_pool[d], min(n, len(chosen_pool[d])))
        if len(have) < n:
            short[d] = n - len(have)
            rest = [q for q in pool if domain_of(q) == d and q not in have]
            have += rng.sample(rest, n - len(have))
        picked += have
    rng.shuffle(picked)
    return {"scenarios": scs, "ids": [q.id for q in picked], "short": short}


def grade(questions: list, answers: dict) -> dict:
    """answers: question id -> chosen index 0-3 (missing = unanswered, counted wrong).
    -> {"correct", "total", "pct", "scaled", "passed", "by_domain": {d: (correct, total)}, "missed": [ids]}"""
    by_domain = {d: [0, 0] for d in WEIGHTS}
    missed = []
    for q in questions:
        d = domain_of(q)
        by_domain[d][1] += 1
        if answers.get(q.id) == q.ans:
            by_domain[d][0] += 1
        else:
            missed.append(q.id)
    total = len(questions)
    correct = total - len(missed)
    pct = correct / total if total else 0.0
    scaled = round(100 + 900 * pct)
    return {"correct": correct, "total": total, "pct": pct, "scaled": scaled, "passed": scaled >= PASS_SCALED,
            "by_domain": {d: tuple(v) for d, v in by_domain.items()}, "missed": missed}
