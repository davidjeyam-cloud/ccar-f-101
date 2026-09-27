"""
Curated, original questions — tagged by task statement (e.g. "1.1", "2.3")
and scenario number (1-6, per the official guide's numbering: 1 Support,
2 CodeGen, 3 Research, 4 DevProd, 5 CI, 6 Extraction).

These are the ONLY questions that count as "verified" toward the readiness
gates in docs/STUDY_PLAN.md (CLAUDE.md deviation 2). Generator output from
utils/quiz.py::generate_questions() is always labelled "unverified" instead.

Rules for every entry (CLAUDE.md commit checklist item 4):
- At least one original question per built task statement.
- Wording hides the qualifier the way real exam stems do (first step,
  guarantee, most maintainable, root cause) - never a bare recall question.
- Never reproduce or paraphrase a real exam question - these are original.
- Never touch an out-of-scope topic (see docs/SOURCES.md).

Where the entries come from: each BUILT concept page (utils/concepts_content/)
ships its own practice questions; they are registered here under the concept's
primary guide task statement, so the page and the bank share one source of
truth. Each item records that it was checked against the guide's task-statement
text by Claude (2026-09-26) and `reviewed_by_user: False` until the workbench's
owner has reviewed it — the bank's "verified" label means checked against the
guide, not yet signed off by a human.
"""

import importlib

QUESTION_BANK: dict[str, list[dict]] = {}


def _register_concept_questions() -> None:
    from utils import concepts_map as cm  # local import keeps this module cheap to import

    for concept in cm.CONCEPTS:
        if not cm.is_built(concept.slug) or not concept.guide_refs:
            continue
        module = importlib.import_module(f"utils.concepts_content.{cm.content_module_name(concept.slug)}")
        tag = concept.guide_refs[0]  # primary guide task statement
        for q in module.CONTENT.questions:
            if not q.in_bank:   # docs-based items go beyond the guide's wording - shown on the page, not banked
                continue
            qtag = q.ts or (q.points[0].split(":")[0] if q.points else tag)
            QUESTION_BANK.setdefault(qtag, []).append({
                "q": q.q,
                "opts": list(q.opts),
                "ans": q.ans,
                "type": "rootcause",
                "explain": q.explain,
                "task_statement": qtag,
                "scenarios": list(q.scenarios),
                "points": list(q.points),
                "source": f"concept:{concept.slug}",
                "checked_against": f"guide v1.0 §6 Task Statement {qtag} (Claude, 2026-09-26)",
                "reviewed_by_user": False,
            })


_register_concept_questions()


def get_bank_questions(tag: str) -> list[dict]:
    """
    Return the bank questions tagged with a task statement like "1.1".
    Empty list if none exist yet - callers should treat that as "not built
    yet", not an error, since the bank grows one page at a time.
    """
    return QUESTION_BANK.get(tag, [])


def for_scenario(number: int) -> list[dict]:
    """All bank questions tagged with a guide scenario number (1-6)."""
    return [q for items in QUESTION_BANK.values() for q in items if number in q["scenarios"]]


def bullet_coverage() -> dict:
    """{(ts, "K1"|"S2"…): [question dicts that pin that guide bullet]} over every task statement in the guide."""
    from utils.guide_index import _TS
    cov = {}
    for ts, (_, _, k, s) in _TS.items():
        for kind, n in (("K", k), ("S", s)):
            for i in range(1, n + 1):
                cov[(ts, f"{kind}{i}")] = []
    for items in QUESTION_BANK.values():
        for q in items:
            for p in q["points"]:
                ts, b = p.split(":")
                cov[(ts, b)].append(q)
    return cov


def render_question_map_markdown() -> str:
    """docs/QUESTION_MAP.md body — which guide bullet each bank question tests. Regenerate with:
        python -c "from utils.question_bank import render_question_map_markdown as f; \
                    open('docs/QUESTION_MAP.md','w',encoding='utf-8',newline='\n').write(f())"
    """
    from collections import Counter
    from utils import concepts_map as cm
    from utils.guide_index import SCENARIO_NAME, _TS, point_ref

    cov = bullet_coverage()
    allq = [q for items in QUESTION_BANK.values() for q in items]
    built_ts = sorted({ts for c in cm.CONCEPTS if cm.is_built(c.slug) for ts in c.guide_refs}
                      | {p.split(":")[0] for q in allq for p in q["points"]}, key=lambda t: tuple(map(int, t.split("."))))
    in_scope = {k: v for k, v in cov.items() if k[0] in built_ts}
    covered = sum(1 for v in in_scope.values() if v)
    scen = Counter(s for q in allq for s in q["scenarios"][:1])
    pos = Counter(q["ans"] for q in allq)
    lines = [
        "# Question Map — every bank question pinned to the exam guide",
        "",
        "Auto-generated from `utils/question_bank.py` (which collects each built concept page's practice items). "
        "Regenerate, don't hand-edit. Every bank question is set in one of the guide's six scenarios (§5, pp.3–4) "
        "and pinned to the exact Knowledge/Skill bullet(s) it tests (§6). A wrong pin fails at import "
        "(`Question.__post_init__` → `guide_index.point_ref`). Questions are original — never real exam items — "
        "and `reviewed_by_user: False` until the owner signs them off.",
        "",
        f"**{len(allq)} bank questions.** Guide bullets covered in the task statements built so far: "
        f"**{covered} / {len(in_scope)}**. Whole guide: {sum(1 for v in cov.values() if v)} / {len(cov)} "
        "(task statements with no built concept yet are listed as gaps below).",
        "",
        "| # | Scenario (primary) | Questions |",
        "|---|---|---|",
    ]
    for n in range(1, 7):
        lines.append(f"| {n} | {SCENARIO_NAME[n]} | {scen.get(n, 0)} |")
    lines += ["", "**Correct-answer position** (should be roughly even): "
              + " · ".join(f"{'ABCD'[i]} {pos.get(i, 0)}" for i in range(4)), ""]
    for ts in sorted(_TS, key=lambda t: tuple(map(int, t.split(".")))):
        rows = [(b, v) for (t, b), v in cov.items() if t == ts]
        n_cov = sum(1 for _, v in rows if v)
        status = "" if ts in built_ts else " — *no built concept yet*"
        lines += ["", f"## TS {ts} — {cm.ts_title(ts)} ({n_cov}/{len(rows)} bullets){status}", "",
                  "| Bullet | Guide reference | Questions (concept · scenario) |", "|---|---|---|"]
        for b, v in rows:
            ref = point_ref(ts, b[0], int(b[1:]))
            qs = "<br>".join(f"{q['source'].split(':')[1]} · S{q['scenarios'][0]} — {q['q'][:90]}…" for q in v) or "⚠️ **gap**"
            lines.append(f"| {b} | {ref} | {qs} |")
    return "\n".join(lines) + "\n"
