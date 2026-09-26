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
            QUESTION_BANK.setdefault(tag, []).append({
                "q": q.q,
                "opts": list(q.opts),
                "ans": q.ans,
                "type": "rootcause",
                "explain": q.explain,
                "task_statement": tag,
                "scenarios": list(q.scenarios),
                "source": f"concept:{concept.slug}",
                "checked_against": f"guide v1.0 §6 Task Statement {tag} (Claude, 2026-09-26)",
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
