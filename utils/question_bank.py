"""
Curated, original, human-verified questions — tagged by task statement
(e.g. "1.1", "2.3") and/or scenario number (1-6, per the official guide's
numbering: 1 Support, 2 CodeGen, 3 Research, 4 DevProd, 5 CI, 6 Extraction).

These are the ONLY questions that count as "verified" toward the readiness
gates in docs/STUDY_PLAN.md (CLAUDE.md deviation 2). Generator output from
utils/quiz.py::generate_questions() is always labelled "unverified" instead.

Rules for every entry (CLAUDE.md commit checklist item 4):
- At least one original question per built task statement.
- Wording hides the qualifier the way real exam stems do (first step,
  guarantee, most maintainable, root cause) - never a bare recall question.
- Never reproduce or paraphrase a real exam question - these are original.
- Never touch an out-of-scope topic (see docs/SOURCES.md).

Empty for now: Phase 0 (this page) has no task-statement number, so its
question needs are covered by utils/quiz.py's generator instead. The first
entries here arrive with page 1.1.
"""

QUESTION_BANK: dict[str, list[dict]] = {}


def get_bank_questions(tag: str) -> list[dict]:
    """
    Return the verified bank questions tagged with `tag` (a task statement
    like "1.1", or a scenario number as a string like "1"). Empty list if
    none exist yet - callers should treat that as "not built yet", not
    an error, since the bank grows one page at a time.
    """
    return QUESTION_BANK.get(tag, [])
