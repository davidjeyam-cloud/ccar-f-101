"""
The CONCEPTS taxonomy: 71 concepts, mirroring the layout of a community concept
list (claudearchitectcertification.com/concepts — a THIRD-PARTY site, so a
community source: unverified, used for structure only, no content copied).

That list has 30 numbered concepts (D1.1 … D5.2, one per exam domain) and 41
unnumbered "cross-cutting" ones. The official guide — not the community list —
decides what this workbench builds (CLAUDE.md source-of-truth rules), so every
concept carries a scope status decided by Claude on 2026-09-26 from a
keyword search and reading of guide v1.0. These are judgments: verify them.

    in_guide      maps cleanly to one or more guide task statements
    partial       overlaps a task statement, or only part of it is in the guide
    awareness     the guide says only "know that it exists"
    out_of_scope  the guide's Appendix explicitly excludes it — never built
    not_in_guide  no matching task statement or knowledge item found in guide v1.0

A concept counts as BUILT when utils/concepts_content/<slug_with_underscores>.py
exists — nothing here needs flipping by hand, so this list cannot drift.
Real, buildable = in_guide / partial (built one at a time with /next-concept).
"""

import re
from dataclasses import dataclass
from pathlib import Path

from utils.course_map import PHASES

_CONTENT_DIR = Path(__file__).resolve().parent / "concepts_content"

STATUS_LABEL = {
    "in_guide": "In the guide",
    "partial": "Partly in the guide",
    "awareness": "Awareness only",
    "out_of_scope": "Out of scope",
    "not_in_guide": "Not in the guide",
}
STATUS_ICON = {"in_guide": "🎯", "partial": "◐", "awareness": "ℹ️", "out_of_scope": "⛔", "not_in_guide": "⚪"}
BUILDABLE = ("in_guide", "partial")

# Grounding rule (CLAUDE.md, 2026-09-26): every built concept is grounded in the OFFICIAL Claude docs.
# A not_in_guide concept can therefore only be built as an EXTRA if an official docs page covers it.
# These are CANDIDATE pages found in the docs indexes (platform.claude.com/docs/llms.txt) — they are
# fetched and read when the concept is actually built (/next-concept), not before.
# Not listed here = no docs basis found = "ungroundable": it stays a stub and is not built.
_P = "https://platform.claude.com/docs/en"
_C = "https://code.claude.com/docs/en"
EXTRA_DOCS = {
    "model-selection-tradeoffs": (f"{_P}/about-claude/models/overview", f"{_P}/about-claude/models/choosing-a-model"),
    "optimizing-ai-workflows-for-efficiency": (f"{_P}/build-with-claude/batch-processing",
                                               f"{_P}/test-and-evaluate/strengthen-guardrails/reduce-latency"),
    "ai-application-security-prompt-injection": (f"{_P}/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks",
                                                 f"{_P}/agents-and-tools/tool-use/how-tool-use-works"),
    "llm-risks-and-failure-modes": (f"{_P}/test-and-evaluate/strengthen-guardrails/reduce-hallucinations",
                                    f"{_P}/build-with-claude/handling-stop-reasons"),
    "debugging-llm-system-failures": (f"{_C}/agent-sdk/observability",),
    "claude-product-feature-selection": (f"{_C}/features-overview",),
    "task-type-prompting-strategies": (f"{_P}/build-with-claude/prompt-engineering/claude-prompting-best-practices",),
    "choosing-output-formats-artifacts-vs-inline": (f"{_P}/build-with-claude/structured-outputs",),
    "claude-application-design-across-interfaces": (f"{_C}/agent-sdk/overview", f"{_P}/managed-agents/overview"),
}


@dataclass(frozen=True)
class Concept:
    slug: str                    # the community site's slug (also our url_path suffix)
    code: str | None             # "D1.1" … "D5.2"; None for cross-cutting concepts
    title: str
    domain: int | None           # 1-5 for numbered concepts
    status: str
    guide_refs: tuple = ()       # guide task statements, e.g. ("1.1",)
    note: str = ""               # the evidence behind the status


def _c(slug, code, title, domain, status, refs=(), note=""):
    return Concept(slug, code, title, domain, status, tuple(refs), note)


_NOT_FOUND = "No matching task statement or knowledge item in guide v1.0 (keyword search, 2026-09-26)."

CONCEPTS: tuple = (
    # ── D1 · Agentic Architecture & Orchestration ──────────────────────────────
    _c("agentic-loops", "D1.1", "Agentic Loops", 1, "in_guide", ["1.1"]),
    _c("subagents", "D1.2", "Subagents", 1, "in_guide", ["1.2", "1.3"]),
    _c("stop-reason", "D1.3", "Stop Reason", 1, "in_guide", ["1.1"],
       "stop_reason inspection is part of TS 1.1; the guide's appendix lists stop_reason handling."),
    _c("session-state", "D1.4", "Session State & Persistence", 1, "in_guide", ["1.7", "5.4"]),
    _c("escalation", "D1.5", "Human-in-the-Loop Escalation", 1, "in_guide", ["5.2", "1.4"]),
    _c("subagent-state-handoff", "D1.6", "Subagent State Handoff", 1, "in_guide", ["1.3", "1.4", "5.4"]),
    _c("agent-instruction-files", "D1.7", "Agent Instruction Files (CLAUDE.md / AGENTS.md)", 1, "partial", ["3.1"],
       "CLAUDE.md is in the guide (TS 3.1); AGENTS.md does not appear anywhere in it."),
    _c("task-decomposition", "D1.8", "Task Decomposition Strategies", 1, "in_guide", ["1.6"]),
    # ── D2 · Tool Design & MCP Integration ─────────────────────────────────────
    _c("tool-calling", "D2.1", "Tool Calling", 2, "in_guide", ["2.1", "1.1"]),
    _c("tool-choice", "D2.2", "Tool Choice", 2, "in_guide", ["2.3", "4.3"]),
    _c("mcp", "D2.3", "Model Context Protocol", 2, "in_guide", ["2.4", "2.2"]),
    _c("hooks", "D2.4", "SDK Hooks (Pre/PostToolUse)", 2, "in_guide", ["1.5"]),
    _c("evaluation", "D2.5", "Tool Evaluation & Testing", 2, "partial", ["2.1"],
       "Guide §7/§8 asks you to test tool-selection reliability with ambiguous requests; there is no dedicated task statement."),
    _c("agentic-tool-surface-selection", "D2.6", "Built-In Tools vs Custom Tools vs Skills vs MCP", 2, "in_guide",
       ["2.5", "3.2", "2.4"]),
    # ── D3 · Claude Code Configuration & Workflows ─────────────────────────────
    _c("claude-md-hierarchy", "D3.1", "CLAUDE.md Hierarchy", 3, "in_guide", ["3.1", "3.3"]),
    _c("plan-mode", "D3.2", "Plan Mode", 3, "in_guide", ["3.4"]),
    _c("skills", "D3.3", "Skills", 3, "in_guide", ["3.2"]),
    _c("checkpoints", "D3.4", "Checkpoints & Session Management", 3, "partial", ["1.7", "5.4"],
       "The guide covers --resume, fork_session and /compact; the word “checkpoints” does not appear."),
    # ── D4 · Prompt Engineering & Structured Output ────────────────────────────
    _c("system-prompts", "D4.1", "System Prompts & Instructions", 4, "in_guide", ["4.1"]),
    _c("prompt-caching", "D4.2", "Prompt Caching", 4, "awareness", [],
       "Guide §17 Appendix · Out-of-Scope Topics · p.39: implementation details out of scope “beyond knowing it exists”. "
       "An awareness page (no lab) was built at the user's request on 2026-09-28."),
    _c("batch-api", "D4.3", "Batch API", 4, "in_guide", ["4.5"]),
    _c("structured-outputs", "D4.4", "Structured Outputs", 4, "in_guide", ["4.3", "4.4"]),
    _c("vision-multimodal", "D4.5", "Vision & Multimodal", 4, "out_of_scope", [],
       "Guide Appendix: vision / image-analysis capabilities will not appear on the exam."),
    _c("streaming", "D4.6", "Streaming", 4, "out_of_scope", [],
       "Guide Appendix: streaming API implementation and server-sent events will not appear on the exam."),
    _c("attention-engineering", "D4.7", "Attention Engineering", 4, "partial", ["5.1", "1.6"],
       "The guide names the lost-in-the-middle effect (5.1) and attention dilution (1.6, 4.6); no dedicated task statement."),
    _c("4d-framework", "D4.8", "4D Framework", 4, "not_in_guide", [], _NOT_FOUND),
    _c("prompt-engineering-techniques", "D4.9", "Prompt Engineering Techniques", 4, "in_guide", ["4.1", "4.2", "3.5"]),
    _c("multi-pass-review-architectures", "D4.10", "Multi-Instance & Multi-Pass Review Architectures", 4,
       "in_guide", ["4.6"]),
    # ── D5 · Context Management & Reliability ──────────────────────────────────
    _c("context-window", "D5.1", "Context Window Management", 5, "in_guide", ["5.1", "5.4"]),
    _c("case-facts-block", "D5.2", "Case Facts Block", 5, "in_guide", ["5.1"]),
    # ── Cross-cutting (unnumbered on the community list) ───────────────────────
    _c("requirements-to-solution-design", None, "Translating Business Requirements into Claude Solutions", None,
       "not_in_guide", [], _NOT_FOUND),
    _c("end-to-end-architecture-design", None, "End-to-End Architecture Design (Input to Feedback Loop)", None,
       "not_in_guide", [], _NOT_FOUND),
    _c("workflow-vs-agent-architecture-patterns", None, "Workflow vs Agent: Choosing the Right Architecture", None,
       "partial", ["1.6", "1.1"], "Fixed pipelines vs dynamic decomposition (1.6) and model-driven vs pre-set sequences (1.1)."),
    _c("business-value-alignment", None, "Aligning Solutions to Business Value Pillars", None, "not_in_guide", [], _NOT_FOUND),
    _c("model-selection-tradeoffs", None, "Claude Model Selection & Tradeoffs", None, "not_in_guide", [],
       _NOT_FOUND + " Adjacent exclusion: performance benchmarking / model-comparison metrics."),
    _c("auth-and-access-control-for-agents", None, "Authentication & Access Control for Agent Systems", None,
       "out_of_scope", [], "Guide Appendix excludes API authentication / account management and OAuth / key-rotation / auth-protocol details."),
    _c("accuracy-latency-cost-tradeoffs", None, "Accuracy-Latency-Cost Tradeoff Analysis", None, "partial", ["4.5"],
       "Only the batch-vs-synchronous latency/cost trade-off is covered."),
    _c("observability-and-monitoring-at-scale", None, "Observability & Monitoring for Agents at Scale", None, "partial", ["1.2"],
       "The guide mentions observability only as a reason to route subagent communication through the coordinator."),
    _c("progressive-disclosure-vs-monolithic-context", None, "Progressive Discovery vs Monolithic Context Strategy", None,
       "partial", ["2.5", "5.4"], "Incremental codebase exploration (Grep, then Read) and scratchpad files."),
    _c("debugging-llm-system-failures", None, "Debugging LLM System Failures", None, "not_in_guide", [],
       _NOT_FOUND + " (Root-cause diagnosis is exercised throughout the §9 sample questions, but there is no dedicated task statement.)"),
    _c("guardrails-and-safety-controls", None, "Guardrails & Safe Deployment Practices", None, "partial", ["1.4", "1.5"],
       "The word “guardrails” never appears; programmatic enforcement via hooks / prerequisite gates does (1.4, 1.5)."),
    _c("llm-risks-and-failure-modes", None, "LLM System Risks & Failure Modes", None, "not_in_guide", [], _NOT_FOUND),
    _c("regulatory-compliance-for-ai-systems", None, "Regulatory Compliance for AI Systems (GDPR, HIPAA, FedRAMP)", None,
       "not_in_guide", [], _NOT_FOUND),
    _c("ethical-ai-considerations", None, "Ethical AI Considerations (Bias, Fairness, Transparency)", None,
       "not_in_guide", [], _NOT_FOUND),
    _c("stakeholder-discovery-and-requirements", None, "Structured Stakeholder Discovery", None, "not_in_guide", [], _NOT_FOUND),
    _c("communicating-ai-decisions-and-value-to-stakeholders", None, "Communicating AI Decisions & Value to Stakeholders",
       None, "not_in_guide", [], _NOT_FOUND),
    _c("stakeholder-feedback-and-sla-alignment", None, "Stakeholder Feedback Loops & SLA Alignment", None, "not_in_guide", [], _NOT_FOUND),
    _c("architecture-documentation-and-handoff", None, "Architecture Documentation & Implementation Handoff", None,
       "not_in_guide", [], _NOT_FOUND),
    _c("ai-solution-lifecycle-management", None, "AI Solution Lifecycle Management", None, "not_in_guide", [], _NOT_FOUND),
    _c("agent-construction-with-claude-agent-sdk", None, "Building Agents: Client SDK vs Agent SDK vs Managed Agents",
       None, "partial", ["1.1", "1.2", "1.3", "1.5", "1.7"],
       "The guide covers the Claude Agent SDK; “Client SDK” and “Managed Agents” do not appear."),
    _c("agent-frameworks-and-design-patterns", None, "Agent Design Patterns: Memory, Context Management & Third-Party Frameworks",
       None, "partial", ["5.1", "5.4"], "Context management is in scope; specific third-party frameworks are excluded by the Appendix."),
    _c("systems-life-cycle-management", None, "Systems Life Cycle Management for Claude Applications", None, "not_in_guide", [], _NOT_FOUND),
    _c("software-engineering-foundations-for-claude-apps", None, "Software Engineering Foundations for Claude Applications",
       None, "not_in_guide", [], _NOT_FOUND + " Adjacent exclusion: language/framework detail beyond tool and schema configuration."),
    _c("claude-application-design-across-interfaces", None, "Claude Application Design Across Interfaces", None,
       "not_in_guide", [], _NOT_FOUND),
    _c("llm-fundamentals-tokens-and-sampling", None, "LLM Fundamentals: Tokens, Sampling & Non-Determinism", None,
       "not_in_guide", [], _NOT_FOUND + " Adjacent exclusion: token-counting algorithms and tokenisation specifics."),
    _c("technical-fundamentals-sdks-and-websockets", None, "Technical Fundamentals: SDKs, REST, and WebSockets", None,
       "not_in_guide", [], _NOT_FOUND + " Adjacent exclusion: streaming / server-sent-events implementation."),
    _c("ai-application-security-prompt-injection", None, "AI Application Security: Prompt Injection & Untrusted Input",
       None, "not_in_guide", [], _NOT_FOUND),
    _c("task-type-prompting-strategies", None, "Prompting Strategy by Task Type: Analysis, Research, Drafting, Brainstorming",
       None, "not_in_guide", [], _NOT_FOUND),
    _c("evaluating-output-accuracy-completeness", None, "Evaluating Claude Output for Accuracy & Completeness", None,
       "partial", ["5.5", "4.4"]),
    _c("identifying-and-validating-ai-output-errors", None, "Identifying Hallucinations, Inconsistencies & Bias in AI Output",
       None, "partial", ["4.4", "4.2", "5.5"],
       "“Hallucination” appears only for extraction (fabricated values); “bias” does not appear."),
    _c("adapting-outputs-for-audience", None, "Editing & Adapting Outputs for the Intended Audience", None, "not_in_guide", [], _NOT_FOUND),
    _c("choosing-output-formats-artifacts-vs-inline", None, "Choosing Output Formats: Artifacts vs Inline vs Structured Data",
       None, "not_in_guide", [], _NOT_FOUND),
    _c("claude-product-feature-selection", None, "Selecting the Right Claude Product Feature", None, "not_in_guide", [], _NOT_FOUND),
    _c("claude-for-research-planning-and-solution-design", None, "Using Claude for Research, Planning & Solution Development",
       None, "not_in_guide", [], _NOT_FOUND),
    _c("integrating-claude-into-existing-workflows", None, "Integrating Claude into Existing Workflows", None, "partial", ["3.6"]),
    _c("configuring-claude-projects", None, "Configuring & Maintaining Claude Projects", None, "not_in_guide", [], _NOT_FOUND),
    _c("managing-knowledge-connectors", None, "Managing Uploaded Knowledge & Connectors", None, "not_in_guide", [], _NOT_FOUND),
    _c("appropriate-ai-use-cases", None, "Identifying Appropriate vs Inappropriate AI Use Cases", None, "not_in_guide", [], _NOT_FOUND),
    _c("organizational-ai-governance-policy", None, "Following Organizational AI Governance Policy", None, "not_in_guide", [], _NOT_FOUND),
    _c("adjusting-approach-from-feedback", None, "Adjusting Approach Based on Feedback & Results", None, "partial", ["3.5"]),
    _c("optimizing-ai-workflows-for-efficiency", None, "Optimizing AI Workflows for Efficiency", None, "not_in_guide", [], _NOT_FOUND),
)

_BY_SLUG = {c.slug: c for c in CONCEPTS}

# short section names for the sidebar, matching the existing phase groups
DOMAIN_SHORT = {1: "Agentic Architecture", 2: "Tool Design & MCP", 3: "Claude Code Config",
                4: "Prompts & Structured Output", 5: "Context & Reliability"}


def get(slug: str) -> Concept | None:
    return _BY_SLUG.get(slug)


def by_domain(domain: int) -> list:
    return [c for c in CONCEPTS if c.domain == domain]


def cross_cutting() -> list:
    return [c for c in CONCEPTS if c.code is None]


def content_module_name(slug: str) -> str:
    return slug.replace("-", "_")


def is_built(slug: str) -> bool:
    return (_CONTENT_DIR / f"{content_module_name(slug)}.py").exists()


def page_url_path(slug: str) -> str:
    return f"concept-{slug}"


def kind(c: Concept) -> str:
    """exam (in_guide / partial) · extra (not in the guide, but an official docs page covers it)
    · ungroundable (not in the guide and no official docs basis found) · excluded (out of scope / awareness)."""
    if c.status in BUILDABLE:
        return "exam"
    if c.status == "not_in_guide":
        return "extra" if c.slug in EXTRA_DOCS else "ungroundable"
    return "excluded"


def buildable(c: Concept) -> bool:
    return kind(c) in ("exam", "extra")


def nav_title(c: Concept) -> str:
    base = f"{c.code} {c.title}" if c.code else c.title
    if is_built(c.slug):
        return base + {"extra": "  ➕🧪", "exam": "  ⭐🧪", "excluded": "  ℹ️📘"}.get(kind(c), "  🧪")
    marker = {"exam": "  ⭐", "extra": "  ➕", "ungroundable": "  ⚪", "excluded": ""}[kind(c)]
    if kind(c) == "excluded":
        marker = "  ⛔" if c.status == "out_of_scope" else "  ℹ️"
    return base + marker


def status_counts() -> dict:
    counts = {s: 0 for s in STATUS_LABEL}
    for c in CONCEPTS:
        counts[c.status] += 1
    return counts


def ts_title(task_statement: str) -> str:
    """Short title of a guide task statement (from course_map), without its leading number."""
    for entries in PHASES.values():
        for e in entries:
            if e.task_statement == task_statement:
                return re.sub(r"^\d+\.\d+\s*", "", e.title)
    return ""


def guide_alignment(c: Concept) -> str:
    if not c.guide_refs:
        return ""
    from utils.guide_index import pages
    return " · ".join(f"TS {t} — {ts_title(t)} ({pages(t)})" for t in c.guide_refs)


def render_concepts_map_markdown() -> str:
    """docs/CONCEPTS_MAP.md body. Regenerate with:
        python -c "from utils.concepts_map import render_concepts_map_markdown as f; \
                    open('docs/CONCEPTS_MAP.md','w',encoding='utf-8',newline='\\n').write(f())"
    """
    counts = status_counts()
    built = sum(1 for c in CONCEPTS if is_built(c.slug))
    lines = [
        "# Concepts Map — the CONCEPTS section vs the official guide",
        "",
        "> Auto-generated from `utils/concepts_map.py` — do not hand-edit. The taxonomy mirrors a community "
        "concept list (claudearchitectcertification.com/concepts, a third-party site: unverified, structure only, "
        "no content copied). **Scope statuses are Claude's judgment from a keyword search and reading of guide "
        "v1.0 on 2026-09-26 — verify them.**",
        "",
        f"**{len(CONCEPTS)} concepts · {built} built.** " + " · ".join(
            f"{STATUS_ICON[s]} {STATUS_LABEL[s]}: {counts[s]}" for s in STATUS_LABEL),
        "",
        "**Kinds:** exam = in the guide (built with docs + guide) · ➕ extra = not on the exam but an official docs page "
        "covers it (built only if grounded, labelled *not on the exam*) · ungroundable = no official docs basis found, "
        "stays a stub · excluded = out of scope / awareness, never built. Candidate docs are fetched and read when the "
        "concept is built.",
        "",
        "| # | Code | Concept | Status | Kind | Guide alignment | Candidate official docs | Evidence / note | Built |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for i, c in enumerate(CONCEPTS, 1):
        align = guide_alignment(c) or "—"
        docs = "<br>".join(EXTRA_DOCS.get(c.slug, ())) or "—"
        lines.append(f"| {i} | {c.code or '—'} | {c.title} | {STATUS_ICON[c.status]} {STATUS_LABEL[c.status]} | "
                     f"{kind(c)} | {align} | {docs} | {c.note or '—'} | {('📘 awareness page' if kind(c) == 'excluded' else '🧪') if is_built(c.slug) else '—'} |")
    return "\n".join(lines) + "\n"
