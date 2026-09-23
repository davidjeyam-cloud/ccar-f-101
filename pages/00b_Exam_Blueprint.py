"""
Phase 0 — Exam Blueprint
Dashboard, not a lesson page: exam mechanics (format, timing, scoring,
policies, out-of-scope) grounded in the official guide. Complements Home,
which covers *what* is tested (domains/task-statements/scenarios); this
page covers *how the exam itself works* — deliberately not duplicating
Home's blueprint table.
"""

import streamlit as st
from utils.styles import phase_header, ACCENT_CURRENT, apply_dashboard_css

st.set_page_config(page_title="Exam Blueprint — CCAR-F", page_icon="📋", layout="wide")

apply_dashboard_css()

st.markdown(phase_header(
    "Phase 0 &nbsp;·&nbsp; Foundations &nbsp;·&nbsp; Exam Mechanics",
    "📋 Exam Blueprint",
    "How the exam itself works: format, timing, scoring, policies, and what it "
    "deliberately does not test. For what topics are tested, see Home.",
    accent=ACCENT_CURRENT,
), unsafe_allow_html=True)

# ── Exam details at a glance ─────────────────────────────────────────────────
st.markdown("""
<div class="wb-card">
<h4>Exam details at a glance</h4>
<table class="wb-table">
<tr><th>Item</th><th>Value</th></tr>
<tr><td>Credential</td><td>Claude Certified Architect – Foundations</td></tr>
<tr><td>Exam code</td><td>CCAR-F</td></tr>
<tr><td>Number of items</td><td>60 — multiple-choice and multiple-response; each item states how many responses to select</td></tr>
<tr><td>Exam structure</td><td>4 scenarios drawn at random from a bank of 6</td></tr>
<tr><td>Time limit</td><td>120 minutes</td></tr>
<tr><td>Delivery</td><td>Proctored — online proctored and/or test center, per program policy</td></tr>
<tr><td>Passing score</td><td>Scaled 720, on a 100–1,000 scale</td></tr>
<tr><td>Exam fee</td><td>$125 USD (per attempt — a retake pays again)</td></tr>
<tr><td>Validity period</td><td>12 months from the date the credential is awarded</td></tr>
<tr><td>Result reporting</td><td>Pass/fail with scaled score, plus percent-correct by domain</td></tr>
</table>
<p class="wb-cite">Source: guide §3 "Exam Details at a Glance".</p>
</div>
""", unsafe_allow_html=True)

# ── How it's scored ──────────────────────────────────────────────────────────
st.markdown("""
<div class="wb-card">
<h4>How it's scored</h4>
<p>The exam is <strong>criterion-referenced</strong>: you're measured against a fixed
performance standard set by a formal standard-setting study, not ranked against other
candidates. Passing means demonstrating the blueprint's knowledge and skills at or above
that standard — not outperforming a percentage of peers.</p>
<p>Your result is pass/fail with a scaled score (100–1,000, cut score 720). The domain
percent-correct breakdown on your score report is diagnostic only — it helps you see where
you were weak, but your pass/fail is decided by the total scaled score, not by any single
domain's percentage.</p>
<p class="wb-cite">Source: guide §10 "How the Exam Is Scored".</p>
</div>
""", unsafe_allow_html=True)

# ── Policies you actually need to plan around ───────────────────────────────
st.markdown("""
<div class="wb-card">
<h4>Policies worth planning around</h4>
<table class="wb-table">
<tr><th>Situation</th><th>What the guide says</th></tr>
<tr><td>ID on exam day</td><td>Valid, unexpired, government-issued photo ID; the name must match your registration exactly</td></tr>
<tr><td>Accommodations</td><td>Must be requested and approved by Pearson VUE <em>before</em> you schedule — don't book first</td></tr>
<tr><td>Retake waiting period</td><td>14 days after attempt 1, 30 days after attempt 2, 90 days after attempt 3</td></tr>
<tr><td>Retake limit</td><td>Up to 4 attempts within a rolling 12-month period; the fee applies every time</td></tr>
<tr><td>No-show / late arrival</td><td>Forfeits the exam fee — you must re-register</td></tr>
<tr><td>During the exam</td><td>Stay in webcam view if online; no notes, phones, second monitors, or recording devices; no communicating with anyone; no capturing or reproducing exam content</td></tr>
<tr><td>Misconduct consequences</td><td>Can mean an invalidated result, a revoked credential, and a ban from future exams</td></tr>
<tr><td>Recertification</td><td>Free, non-proctored renewal assessment before the 12-month mark; a lapsed credential requires the full exam again at full fee</td></tr>
</table>
<p class="wb-cite">Source: guide §12 "Exam Policies", §13 "Exam-Day Experience and Rules of Conduct", §15 "Credential Maintenance and Recertification".</p>
</div>
""", unsafe_allow_html=True)

# ── Out of scope ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="wb-card">
<h4>Explicitly out of scope — don't spend study time here</h4>
<table class="wb-table">
<tr><th>#</th><th>Not tested</th></tr>
<tr><td>1</td><td>Fine-tuning Claude or training custom models</td></tr>
<tr><td>2</td><td>Claude API authentication, billing, or account management</td></tr>
<tr><td>3</td><td>Language/framework implementation detail beyond tool and schema configuration</td></tr>
<tr><td>4</td><td>Deploying or hosting MCP servers (infrastructure, networking, orchestration)</td></tr>
<tr><td>5</td><td>Claude's internal architecture, training process, or model weights</td></tr>
<tr><td>6</td><td>Constitutional AI, RLHF, or safety-training methodologies</td></tr>
<tr><td>7</td><td>Embedding models or vector-database implementation details</td></tr>
<tr><td>8</td><td>Computer use (browser automation, desktop interaction)</td></tr>
<tr><td>9</td><td>Vision / image-analysis capabilities</td></tr>
<tr><td>10</td><td>Streaming API implementation or server-sent events</td></tr>
<tr><td>11</td><td>Rate limits, quotas, or API pricing calculations</td></tr>
<tr><td>12</td><td>OAuth, API key rotation, or authentication protocol details</td></tr>
<tr><td>13</td><td>Specific cloud-provider configuration (AWS, GCP, Azure)</td></tr>
<tr><td>14</td><td>Benchmarking or model-comparison metrics</td></tr>
<tr><td>15</td><td>Prompt-caching implementation details (knowing it exists is enough)</td></tr>
<tr><td>16</td><td>Token-counting algorithms or tokenisation specifics</td></tr>
</table>
<p class="wb-cite">Source: guide Appendix, "Out-of-Scope Topics". This list is also enforced in <code>CLAUDE.md</code> — no page or quiz question in this workbench is built on any of these.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("### What's next → the study plan")
st.markdown(
    "For *what* is tested (domains, task statements, scenarios), see **Home**. "
    "To build the next page, type `/next-page` in the Claude Code panel."
)
