"""
Phase 0 — Home
Dashboard: project intent (grounded in the official exam guide) and the
full 30-cell blueprint coverage map. Not a lesson page (no task statement
of its own), so it skips the Page Structure Standard's concept/demo/quiz
steps, the same way agents101's own Home page is a dashboard, not a lesson.

Every number and cell on this page is read from utils/course_map.py, not
hand-typed here - that data was cross-checked against docs/source/*.pdf on
2026-09-22 (see docs/SESSION_LOG.md), and this page inherits that grounding
automatically instead of risking its own copy drifting out of sync.
"""

import streamlit as st
from utils.styles import C, phase_header, ACCENT_CURRENT, apply_dashboard_css
from utils import concepts_map as cm, mcq_bank
from utils.course_map import PHASES, DOMAINS, SCENARIOS

st.set_page_config(page_title="CCAR-F Study Workbench — Home", page_icon="🎓", layout="wide")

# Progress is measured on the real learning surfaces: concept labs and the exam question bank.
# (The 46 phase pages are mostly placeholders that only show bank questions - counting them said "13% built".)
bank = mcq_bank.load()
all_q = [q for m in bank.values() for q in m.QUESTIONS]
labs = [c for c in cm.CONCEPTS if cm.is_built(c.slug) and cm.kind(c) == "exam"]
ts_with_lab = {t for c in labs for t in c.guide_refs}
ts_all = [e.task_statement for entries in PHASES.values() for e in entries if e.task_statement]

apply_dashboard_css()

# Page-local additions to the shared wb-* classes — the coloured task-statement
# grid is a Home-specific visual, not reused elsewhere (yet), so it stays here.
st.markdown(f"""
<style>
.cf-domain-name {{ font-weight:700; color:{C['text_prim']}; }}
.cf-weight-badge {{
    display:inline-block; background:{C['bg_overlay']}; color:{C['blue']}; font-weight:700;
    font-size:0.78rem; border-radius:20px; padding:2px 10px; margin-top:4px;
}}
.cf-cell-row {{ display:flex; flex-wrap:wrap; gap:6px; }}
.cf-cell {{
    display:inline-block; border-radius:8px; padding:4px 9px; font-size:0.78rem; font-weight:600;
    border:1px solid {C['border']}; color:{C['text_sec']}; background:{C['bg_overlay']};
}}
.cf-cell.built {{ background:rgba(5,150,105,0.10); border-color:{C['green']}; color:{C['green']}; }}
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(phase_header(
    "Phase 0 &nbsp;·&nbsp; Foundations &nbsp;·&nbsp; Dashboard",
    "🎓 CCAR-F Study Workbench",
    "What this project is for, and the full exam blueprint it's built to cover.",
    accent=ACCENT_CURRENT,
), unsafe_allow_html=True)

# ── Stats ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="wb-stats">
  <div class="wb-stat"><div class="wb-stat-num" style="color:{C['green']}">{len(labs)}</div>
    <div class="wb-stat-label">Exam concept labs built</div></div>
  <div class="wb-stat"><div class="wb-stat-num" style="color:{C['blue']}">{len(ts_with_lab & set(ts_all))} / {len(ts_all)}</div>
    <div class="wb-stat-label">Task statements with a lab</div></div>
  <div class="wb-stat"><div class="wb-stat-num" style="color:{C['purple']}">{len(all_q)}</div>
    <div class="wb-stat-label">Exam-style questions (all 30 task statements)</div></div>
  <div class="wb-stat"><div class="wb-stat-num" style="color:{C['orange']}">4 of 6</div>
    <div class="wb-stat-label">Scenarios drawn per sitting</div></div>
</div>
""", unsafe_allow_html=True)

# ── Project intent — grounded in the guide ──────────────────────────────────
st.markdown(f"""
<div class="wb-card">
<h4>What this project is for</h4>
<p>This is a study workbench for the <strong>Claude Certified Architect – Foundations</strong>
exam (CCAR-F, guide v1.0, effective July 2026). The official guide states the certification
validates that practitioners can make <em>informed decisions about tradeoffs</em> when
implementing real-world solutions with Claude — across Claude Code, the Claude Agent SDK,
the Claude API, and MCP. Its questions are grounded in realistic production scenarios
(customer support agents, multi-agent research pipelines, CI/CD integration, developer
productivity tools, structured data extraction), and it explicitly tests judgment and
architecture decisions, not trivia recall.</p>
<p>The guide's own description of the ideal candidate — hands-on experience building
agentic applications, configuring Claude Code for team workflows, designing MCP interfaces,
engineering reliable structured output, managing context across long sessions, integrating
Claude into CI/CD, and making sound escalation decisions — is this workbench's build list.
Every page here exists because the guide names the skill it teaches; nothing is built that
the guide places out of scope (see <code>docs/SOURCES.md</code>).</p>
<p>How it works: each topic is <strong>built by hand in VS Code with Claude Code</strong>
(<code>sandbox_project/</code>) — that is where the actual learning happens. This app tracks
progress and runs small pattern demos on Gemini for cost reasons; a handful of pages
(flagged 🔑) also use the real Claude API, because the exam tests Claude's exact mechanics
and a Gemini demo alone can't honestly stand in for that.</p>
<p class="wb-cite">Grounded in the official guide, §1 "About This Certification" and
§2 "Intended Audience" — paraphrased, not quoted, per this project's guardrails.</p>
</div>
""", unsafe_allow_html=True)

# ── Blueprint — the visual coverage map ─────────────────────────────────────
st.markdown("#### The exam blueprint — 30 task statements across 5 domains")
st.caption(
    "Every cell is one guide task statement. Green = at least one concept lab covers it. Hover for the "
    "title and question count. Labs, gaps and questions per task statement: **Concepts → 🗺️ Course map**. "
    "Source: guide §4 Exam Content Outline, §6 Detailed Objectives by Domain."
)

rows = []
for d, (name, weight, _section) in DOMAINS.items():
    group = next(g for g in PHASES if g.startswith(f"Phase {d} "))
    cells = ""
    for e in PHASES[group]:
        if not e.task_statement:
            continue
        nq = len(bank[e.task_statement].QUESTIONS) if e.task_statement in bank else 0
        cls = "cf-cell built" if e.task_statement in ts_with_lab else "cf-cell"
        cells += f'<span class="{cls}" title="{e.title} · {nq} questions">{e.task_statement}</span>'
    rows.append(f"""
    <tr>
      <td style="width:26%">
        <div class="cf-domain-name">Domain {d} — {name}</div>
        <span class="cf-weight-badge">{weight} of the exam</span>
      </td>
      <td><div class="cf-cell-row">{cells}</div></td>
    </tr>""")

st.markdown(f"""
<div class="wb-card">
<table class="wb-table">
  <tr><th>Domain (guide §6)</th><th>Task statements (blueprint sub-topics)</th></tr>
  {"".join(rows)}
</table>
</div>
""", unsafe_allow_html=True)

# ── Scenarios ────────────────────────────────────────────────────────────────
st.markdown("#### The 6 exam scenarios — 4 drawn at random per sitting")
st.caption("Source: guide §5 Exam Scenarios. Each has a question drill (Phase 6 page); the build-and-break exercises are not built yet.")

scen_rows = ""
for slug, (num, title, domains) in sorted(SCENARIOS.items(), key=lambda kv: kv[1][0]):
    entry = next(e for e in PHASES["Phase 6 — Capstones"] if e.slug == slug)
    nq = sum(1 for q in all_q if q.scenarios[0] == num)
    status = f"📝 {nq} questions · exercise 🔜"
    key_flag = ""
    dom_str = ", ".join(f"D{d}" for d in domains)
    scen_rows += (
        f'<tr><td>{num}</td><td>{title}{key_flag}</td>'
        f'<td>{dom_str}</td><td>{status}</td></tr>'
    )

st.markdown(f"""
<div class="wb-card">
<table class="wb-table">
  <tr><th>#</th><th>Scenario</th><th>Primary domains</th><th>Status</th></tr>
  {scen_rows}
</table>
</div>
""", unsafe_allow_html=True)

st.markdown("### What's next → Concepts, then the Timed Mock")
st.markdown(
    "Learn a topic in **Concepts** (labs + the 🗺️ Course map), drill it with the questions on its phase page, "
    "then sit a 60-item **Timed Mock** in Phase 7. Traceability: `docs/GUIDE_MAP.md`. Build rules: `CLAUDE.md`."
)
