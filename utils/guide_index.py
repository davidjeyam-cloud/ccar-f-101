"""
Exact locations in the official exam guide (v1.0, the PDF in docs/source/, local only).

This module stores POSITIONS ONLY — section, page, and how many bullets each task
statement has — never the guide's text (copyright; see CLAUDE.md). The numbers were
read from the PDF on 2026-09-26 with pdftotext; re-check them if the guide is reissued.

How references are written
    Guide §6 · TS 1.1 · Knowledge 2 · p.5
      §6        the guide's section "Detailed Objectives by Domain" (pp.5-23)
      TS 1.1    the task statement
      Knowledge 2 / Skill 3   the 2nd bullet under "Knowledge of:" / 3rd under "Skills in:".
                The guide does NOT number its bullets — the numbers are the order they appear,
                counted by this workbench, so they are stable but not the guide's own numbering.
      p.5       the PDF page (pages 10-11 for a task statement that spans a page break)
"""

# task statement -> (first page, last page, number of Knowledge bullets, number of Skill bullets)
_TS = {
    "1.1": (5, 5, 3, 3), "1.2": (5, 6, 4, 4), "1.3": (6, 7, 4, 4), "1.4": (7, 7, 3, 3),
    "1.5": (7, 8, 3, 3), "1.6": (8, 8, 3, 3), "1.7": (8, 9, 4, 4),
    "2.1": (9, 9, 4, 4), "2.2": (9, 10, 4, 4), "2.3": (10, 11, 4, 5), "2.4": (11, 11, 4, 5),
    "2.5": (11, 12, 4, 5),
    "3.1": (12, 13, 4, 4), "3.2": (13, 13, 4, 5), "3.3": (13, 14, 3, 3), "3.4": (14, 14, 4, 4),
    "3.5": (14, 15, 4, 5), "3.6": (15, 16, 4, 5),
    "4.1": (16, 16, 3, 3), "4.2": (16, 17, 4, 5), "4.3": (17, 18, 4, 6), "4.4": (18, 18, 4, 4),
    "4.5": (18, 19, 4, 4), "4.6": (19, 19, 3, 3),
    "5.1": (19, 20, 4, 6), "5.2": (20, 21, 4, 5), "5.3": (21, 21, 4, 4), "5.4": (21, 22, 4, 5),
    "5.5": (22, 23, 4, 4), "5.6": (23, 23, 4, 5),
}

# guide section 5 "Exam Scenarios" (pp.3-4): scenario number -> page
SCENARIO_PAGE = {1: 3, 2: 3, 3: 4, 4: 4, 5: 4, 6: 4}
SCENARIO_NAME = {1: "Customer Support Resolution Agent", 2: "Code Generation with Claude Code",
                 3: "Multi-Agent Research System", 4: "Developer Productivity with Claude",
                 5: "Claude Code for Continuous Integration", 6: "Structured Data Extraction"}

SECTION_OBJECTIVES = "§6"   # "Detailed Objectives by Domain"
SECTION_APPENDIX = "§17"    # out-of-scope list, p.36


def pages(ts: str) -> str:
    first, last, _, _ = _TS[ts]
    return f"p.{first}" if first == last else f"pp.{first}–{last}"


def ts_ref(ts: str) -> str:
    """'Guide §6 · TS 1.1 · p.5'"""
    return f"Guide {SECTION_OBJECTIVES} · TS {ts} · {pages(ts)}"


def point_ref(ts: str, kind: str, n: int) -> str:
    """kind 'K' (Knowledge of) or 'S' (Skills in): 'TS 1.1 · Knowledge 2 · p.5'. Checks the bullet exists."""
    _, _, k, s = _TS[ts]
    if kind not in ("K", "S") or not 1 <= n <= (k if kind == "K" else s):
        raise ValueError(f"guide has no {kind}{n} under TS {ts} (K={k}, S={s})")
    return f"TS {ts} · {'Knowledge' if kind == 'K' else 'Skill'} {n} · {pages(ts)}"


def resolve_source(source: str) -> str:
    """Turn a distractor/variant source into display text.
        'guide:1.1:S3' -> '⭐ EXAM — TS 1.1 · Skill 3 · p.5'      'guide:1.1' -> '⭐ EXAM — Guide §6 · TS 1.1 · p.5'
        'docs' -> '📘 official docs (beyond the guide)'
    """
    if source.startswith("guide"):
        parts = source.split(":")
        if len(parts) == 3:
            return "⭐ EXAM — " + point_ref(parts[1], parts[2][0], int(parts[2][1:]))
        if len(parts) == 2:
            return "⭐ EXAM — " + ts_ref(parts[1])
        return "🎓 exam guide"
    if source == "docs":
        return "📘 official docs (beyond the guide)"
    return source


def scenario_ref(n: int) -> str:
    return f"Guide §5 · Scenario {n} ({SCENARIO_NAME[n]}) · p.{SCENARIO_PAGE[n]}"
