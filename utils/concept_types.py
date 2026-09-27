"""
Data shapes for a CONCEPTS page. Kept separate from the renderer
(utils/concept_page.py) so each concept's content module can import them
without importing Streamlit or creating a circular import.

Grounding rule (CLAUDE.md, user rule 2026-09-26): every CONCEPTS page is
grounded in the OFFICIAL Claude documentation (platform.claude.com/docs and
code.claude.com/docs — the platform docs redirect the Agent SDK to the latter).
A page therefore carries `docs_refs` (what was read, and when) and `grounding`
(each substantive claim tagged with where it comes from), so a reader can audit
it instead of trusting it.
"""

from dataclasses import dataclass
from typing import Callable, Optional

# Provenance kinds for a Claim — shown as icons on the page.
CLAIM_KINDS = {
    "docs": "📘 official docs",
    "guide": "🎓 exam guide",
    "recommendation": "💡 my recommendation",
    "simulated": "🧪 simulated",
}


@dataclass(frozen=True)
class DocRef:
    """An official documentation page that was actually fetched and read for this concept."""
    title: str
    url: str


@dataclass(frozen=True)
class Claim:
    """One substantive claim on the page and where it comes from."""
    text: str
    kind: str      # a key of CLAIM_KINDS
    ref: str       # docs URL (+ section), guide task statement, or a short note


@dataclass(frozen=True)
class Variant:
    """One starting point for the code lab: the correct pattern or a distractor."""
    key: str
    label: str
    kind: str          # "correct" | "distractor"
    code: str
    scenario: str      # scenario id (utils/mock_claude.py) that makes this variant's behaviour visible
    observe: str       # what the learner should see after pressing Run
    why: str           # why it works / why it fails
    fix: str = ""      # what to do instead (distractors)
    source: str = ""   # "guide:<ts>:<K|S><n>" (exam-named, exact bullet) | "guide:<ts>" | "docs" (empty for the correct variant)


@dataclass(frozen=True)
class ExamPoint:
    """One thing the exam guide says the candidate must know or be able to do (paraphrased, never copied)."""
    ts: str          # task statement, e.g. "1.1"
    kind: str        # "K" = a "Knowledge of" bullet, "S" = a "Skills in" bullet
    n: int           # its order under that heading (1-based) — checked by utils/guide_index.point_ref
    text: str        # the requirement, in this workbench's words
    lab: str = ""    # where this page lets the learner exercise it


@dataclass(frozen=True)
class PlayTab:
    """One sub-concept's tab in the agent playground: its own message box and its own constraints."""
    key: str
    label: str
    condition: str            # simulated behaviour: none | long_answer | refusal | pause | runaway
    mental_model: str         # CLAUDE.md MENTAL MODEL RULE — one line, true to the docs
    exam_source: str          # "guide:1.1:K1" (⭐ exam-named, exact bullet) or "" (docs-only, not gold)
    meaning: str              # what this stop reason / limit means and what a loop must do (docs-grounded)
    docs: str                 # docs page + section this tab is grounded in
    knobs: tuple              # keys of utils/playground_ui._KNOBS shown on this tab
    defaults: dict            # knob -> starting value
    examples: tuple           # suggested messages; the first pre-fills the box
    try_this: tuple = ()      # experiments
    engine: str = "support"   # "support" (D1.1 single agent) | "research" (coordinator + subagents) | "stop" (stop_reason inspector) | "session" (D1.4 sessions) | "escalation" (D1.5) | "fork" (session fork demo)


@dataclass(frozen=True)
class Question:
    """An ORIGINAL practice item — never a real exam question."""
    q: str
    opts: tuple
    ans: int
    explain: str
    scenarios: tuple = ()        # guide scenario numbers (1 Support … 6 Extraction) this item fits
    basis: str = "guide"         # "guide" (examinable, checked against the guide) or "docs" (beyond the guide's scope)
    in_bank: bool = True         # only guide-based items enter utils/question_bank.py
    ts: str = ""                 # task statement this item tests, if not the concept's primary one (question bank tag)


# node id -> (state, suffix text); state is "ok" | "bad"; missing node = not visited
NodeStates = dict


@dataclass(frozen=True)
class ConceptContent:
    slug: str
    tldr: str
    mental_model: str
    what_it_is: str
    how_it_works: str
    where_seen: str
    guide_note: str
    docs_refs: tuple             # DocRef, …
    docs_verified_on: str        # ISO date the docs were fetched and read
    grounding: tuple             # Claim, …
    flow_dot: Callable[[NodeStates], str]
    node_states: Callable[[Optional[dict]], NodeStates]
    lab_intro: str
    variants: tuple
    check_outcome: Callable[[str, dict], tuple]   # (scenario, trace) -> (ok, expected, observed)
    distractors: tuple          # (name, why it looks right, why it fails, do this instead, source)
    side_by_side_headers: tuple
    side_by_side_rows: tuple
    decision_dot: str
    experiments: tuple
    questions: tuple
    faq: tuple                  # (question, answer)
    related: tuple              # concept slugs
    exam_points: tuple = ()     # ExamPoint, … — what the guide demands (exam concepts only)
    playground: tuple = ()      # PlayTab, … — one message box per sub-concept (optional)
    playground_intro: str = ""
    scenarios: tuple = ()       # scenario ids for the code lab (empty = the D1.1 single-agent scenarios)
    show_ledger: bool = True    # the fake support backend's refund ledger tab (D1.1); off for other labs
