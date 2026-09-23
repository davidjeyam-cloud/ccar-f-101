"""
Single structured mirror (in code) of CLAUDE.md's Phase Status tables and
AGENTS.md's Phase Map. Two consumers: app.py (sidebar navigation, including
placeholder entries for pages not yet built) and, from page 2 onward,
pages/00a_Home.py (the 30-cell domain coverage map).

CLAUDE.md remains the source of truth for exam content. When a page's status
changes there (checklist item 5, "Docs sync"), flip its `built` flag here too
- app.py's navigation reads this file, so a stale flag here means the
sidebar keeps showing a real page as a placeholder (or vice versa).

Real filenames for phases 1-6 are still an open question (not yet answered
by the user - see docs/SESSION_LOG.md). `slug` below is therefore a stable
short id, not necessarily the final pages/<slug>.py filename; when a page is
actually built, update BOTH its `built` flag here and its nav entry in
app.py to point at the real file.
"""

from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Verified 2026-09-22 against a fresh `pdftotext -layout` extraction of
# docs/source/*.pdf ("Claude Certified Architect - Foundations Exam Guide,
# Version 1.0, Effective July 2026") - byte-identical to the extraction used
# to write CLAUDE.md's Phase Status tables on 2026-09-21. Domain names,
# weights, task-statement numbering and scenario primary domains below are
# copied verbatim from the guide's section 4 (Exam Content Outline) and
# section 5 (Exam Scenarios). Re-verify here if the guide is ever updated.
# ---------------------------------------------------------------------------

# domain number -> (official name, weight, guide section)
DOMAINS: dict[int, tuple[str, str, str]] = {
    1: ("Agentic Architecture & Orchestration", "27%", "guide §6, Domain 1"),
    2: ("Tool Design & MCP Integration", "18%", "guide §6, Domain 2"),
    3: ("Claude Code Configuration & Workflows", "20%", "guide §6, Domain 3"),
    4: ("Prompt Engineering & Structured Output", "20%", "guide §6, Domain 4"),
    5: ("Context Management & Reliability", "15%", "guide §6, Domain 5"),
}

# capstone slug -> (guide scenario number, guide scenario title, primary domain numbers)
SCENARIOS: dict[str, tuple[int, str, tuple[int, ...]]] = {
    "06a": (2, "Code Generation with Claude Code", (3, 5)),
    "06b": (5, "Claude Code for Continuous Integration", (3, 4)),
    "06c": (6, "Structured Data Extraction", (4, 5)),
    "06d": (1, "Customer Support Resolution Agent", (1, 2, 5)),
    "06e": (3, "Multi-Agent Research System", (1, 2, 5)),
    "06f": (4, "Developer Productivity with Claude", (2, 3, 1)),
}


@dataclass(frozen=True)
class PageEntry:
    slug: str                      # stable short id, e.g. "01a" - not always the final filename yet
    title: str                     # short nav / card title
    task_statement: str | None = None   # e.g. "2.1"; None for non-task-statement pages
    domain: int | None = None           # 1-5; None for Phase 0 / 6 / 7
    interactive: bool = False           # star page - real live demo
    needs_claude_key: bool = False      # key page - Claude API gives a real advantage
    built: bool = False

    def guide_ref(self) -> str | None:
        """One line tracing this page back to the guide - what CLAUDE.md's
        checklist calls the source-of-truth reference. None for pages with
        no direct guide section (e.g. Home, Study Plan itself)."""
        if self.task_statement and self.domain:
            name, weight, section = DOMAINS[self.domain]
            return f"Domain {self.domain} — {name} ({weight}) · Task Statement {self.task_statement} · {section}"
        if self.slug in SCENARIOS:
            num, title, domains = SCENARIOS[self.slug]
            dom_names = ", ".join(f"D{d}" for d in domains)
            return f"Scenario {num} — \"{title}\" · guide §5 · primary domains: {dom_names}"
        return None


PHASES: dict[str, list[PageEntry]] = {
    "Phase 0 — Foundations": [
        PageEntry("00_Hello_Claude", "Hello Claude", built=True),
        PageEntry("00a_Home", "Home", built=True),
        PageEntry("00b_Exam_Blueprint", "Exam Blueprint", built=True),
        PageEntry("00c_Study_Plan", "Study Plan"),
        PageEntry("00d_Approach_Scorecard", "Approach Scorecard"),
        PageEntry("00e_ToolUse_Primer", "Tool-Use Primer"),
        PageEntry("0q_Quiz_Hub", "Quiz Hub"),
    ],
    "Phase 1 — Agentic Architecture (27%)": [
        PageEntry("01a", "1.1 Agentic loops", "1.1", 1, interactive=True, needs_claude_key=True),
        PageEntry("01b", "1.2 Coordinator-subagent", "1.2", 1),
        PageEntry("01c", "1.3 Subagent invocation", "1.3", 1),
        PageEntry("01d", "1.4 Enforcement & handoff", "1.4", 1, interactive=True),
        PageEntry("01e", "1.5 Hooks", "1.5", 1),
        PageEntry("01f", "1.6 Task decomposition", "1.6", 1),
        PageEntry("01g", "1.7 Session state", "1.7", 1),
    ],
    "Phase 2 — Tool Design & MCP (18%)": [
        PageEntry("02a", "2.1 Tool descriptions", "2.1", 2, interactive=True),
        PageEntry("02b", "2.2 Structured errors", "2.2", 2),
        PageEntry("02c", "2.3 Tool choice", "2.3", 2, interactive=True, needs_claude_key=True),
        PageEntry("02d", "2.4 MCP config", "2.4", 2),
        PageEntry("02e", "2.5 Built-in tools", "2.5", 2),
    ],
    "Phase 3 — Claude Code Config (20%)": [
        PageEntry("03a", "3.1 CLAUDE.md hierarchy", "3.1", 3, interactive=True),
        PageEntry("03b", "3.2 Commands and skills", "3.2", 3),
        PageEntry("03c", "3.3 Path-specific rules", "3.3", 3, interactive=True),
        PageEntry("03d", "3.4 Plan vs direct", "3.4", 3),
        PageEntry("03e", "3.5 Iterative refinement", "3.5", 3),
        PageEntry("03f", "3.6 CI/CD", "3.6", 3, interactive=True),
    ],
    "Phase 4 — Prompts & Structured Output (20%)": [
        PageEntry("04a", "4.1 Explicit criteria", "4.1", 4),
        PageEntry("04b", "4.2 Few-shot", "4.2", 4),
        PageEntry("04c", "4.3 Structured output", "4.3", 4, interactive=True, needs_claude_key=True),
        PageEntry("04d", "4.4 Validation-retry", "4.4", 4, needs_claude_key=True),
        PageEntry("04e", "4.5 Batch", "4.5", 4, interactive=True, needs_claude_key=True),
        PageEntry("04f", "4.6 Multi-pass review", "4.6", 4),
    ],
    "Phase 5 — Context & Reliability (15%)": [
        PageEntry("05a", "5.1 Context preservation", "5.1", 5, interactive=True),
        PageEntry("05b", "5.2 Escalation", "5.2", 5),
        PageEntry("05c", "5.3 Error propagation", "5.3", 5),
        PageEntry("05d", "5.4 Codebase exploration", "5.4", 5),
        PageEntry("05e", "5.5 Human review", "5.5", 5, interactive=True),
        PageEntry("05f", "5.6 Provenance", "5.6", 5),
    ],
    "Phase 6 — Capstones": [
        PageEntry("06a", "CodeGen (scenario 2)"),
        PageEntry("06b", "CI (scenario 5)"),
        PageEntry("06c", "Extraction (scenario 6)", needs_claude_key=True),
        PageEntry("06d", "Support (scenario 1)", needs_claude_key=True),
        PageEntry("06e", "Research (scenario 3)", needs_claude_key=True),
        PageEntry("06f", "DevProd (scenario 4)"),
    ],
    "Phase 7 — Exam Readiness": [
        PageEntry("07a_Timed_Mock", "Timed Mock"),
        PageEntry("07b_Error_Log", "Error Log"),
        PageEntry("07c_Exam_Day", "Exam Day"),
    ],
}


def all_entries() -> list[PageEntry]:
    return [e for entries in PHASES.values() for e in entries]


def counts() -> tuple[int, int]:
    """(built, total) across every page."""
    entries = all_entries()
    return sum(1 for e in entries if e.built), len(entries)


def nav_title(e: PageEntry) -> str:
    marker = ("  ★" if e.interactive else "") + ("  🔑" if e.needs_claude_key else "")
    return e.title + marker


def render_guide_map_markdown() -> str:
    """Generate docs/GUIDE_MAP.md's body from this module - the single
    source of truth. Regenerate with:
        python -c "from utils.course_map import render_guide_map_markdown as f; \
                    open('docs/GUIDE_MAP.md','w',encoding='utf-8').write(f())"
    whenever PHASES, DOMAINS or SCENARIOS changes (docs-sync checklist)."""
    built, total = counts()
    lines = [
        "# Guide Map — every page traced to the official exam guide",
        "",
        "> Auto-generated from `utils/course_map.py` — do not hand-edit; regenerate instead "
        "(see that file's `render_guide_map_markdown()` docstring). This is the same data the "
        "sidebar and each placeholder page show; this file is the durable, off-app copy.",
        "",
        f"Ground truth: `docs/source/*.pdf` — Claude Certified Architect – Foundations Exam "
        f"Guide, v1.0, effective July 2026. **{built} of {total} pages built.**",
        "",
        "## Domains (guide §4 Exam Content Outline, §6 Detailed Objectives)",
        "",
        "| Domain | Name | Weight | Task statements |",
        "|---|---|---|---|",
    ]
    for d, (name, weight, _section) in DOMAINS.items():
        ts = [e.task_statement for e in all_entries() if e.domain == d and e.task_statement]
        lines.append(f"| {d} | {name} | {weight} | {ts[0]}–{ts[-1]} |")

    lines += [
        "",
        "## Scenarios (guide §5 Exam Scenarios — 4 of 6 drawn at random per sitting)",
        "",
        "| Capstone page | Guide scenario # | Guide title | Primary domains |",
        "|---|---|---|---|",
    ]
    for slug, (num, title, domains) in sorted(SCENARIOS.items(), key=lambda kv: kv[1][0]):
        dom_str = ", ".join(f"D{d}" for d in domains)
        lines.append(f"| {slug} | {num} | {title} | {dom_str} |")

    lines += [
        "",
        "## Every page",
        "",
        "| Page | Guide reference | Status |",
        "|---|---|---|",
    ]
    for phase_group, entries in PHASES.items():
        lines.append(f"| **{phase_group}** | | |")
        for e in entries:
            ref = e.guide_ref() or "— (no single guide section — foundational/meta page)"
            status = "✅ built" if e.built else "🔜"
            lines.append(f"| {e.slug} — {e.title} | {ref} | {status} |")

    return "\n".join(lines) + "\n"
