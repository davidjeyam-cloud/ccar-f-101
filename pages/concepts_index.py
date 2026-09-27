"""
CONCEPTS — index. Mirrors the layout of the community concept list: domain
filter tabs over a card grid. Unlike that list, every card is tagged with how
it relates to the OFFICIAL guide, and the built ones open a runnable code lab.

Cards link through the Page objects app.py stores in st.session_state, so
navigation stays inside the same Streamlit session (no full page reload).
"""

import streamlit as st

from utils import concepts_map as cm
from utils.course_map import DOMAINS
from utils.styles import C, ACCENT_CURRENT, apply_dashboard_css, phase_header

st.set_page_config(page_title="Concepts — CCAR-F Study Workbench", page_icon="🧪", layout="wide")
apply_dashboard_css()

pages = st.session_state.get("_concept_pages", {})
counts = cm.status_counts()
built = sum(1 for c in cm.CONCEPTS if cm.is_built(c.slug))
kinds = {k: sum(1 for c in cm.CONCEPTS if cm.kind(c) == k) for k in ("exam", "extra", "ungroundable", "excluded")}

st.markdown(phase_header(
    "CONCEPTS",
    "🧪 Concepts",
    "Learn one concept at a time: a flowchart, code you can edit and run, and the exam distractors — "
    "shown failing on purpose.",
    accent=ACCENT_CURRENT,
), unsafe_allow_html=True)

st.markdown(f"""
<div class="wb-stats">
  <div class="wb-stat"><div class="wb-stat-num" style="color:{C['blue']}">{len(cm.CONCEPTS)}</div>
    <div class="wb-stat-label">Concepts listed</div></div>
  <div class="wb-stat"><div class="wb-stat-num" style="color:{C['green']}">{built}</div>
    <div class="wb-stat-label">Labs built</div></div>
  <div class="wb-stat"><div class="wb-stat-num" style="color:{C['purple']}">{kinds['exam']}</div>
    <div class="wb-stat-label">Exam concepts</div></div>
  <div class="wb-stat"><div class="wb-stat-num" style="color:{C['blue']}">{kinds['extra']}</div>
    <div class="wb-stat-label">➕ Extras (docs-grounded)</div></div>
  <div class="wb-stat"><div class="wb-stat-num" style="color:{C['orange']}">{kinds['excluded']}</div>
    <div class="wb-stat-label">Out of scope / awareness</div></div>
  <div class="wb-stat"><div class="wb-stat-num" style="color:{C['text_muted']}">{kinds['ungroundable']}</div>
    <div class="wb-stat-label">No docs basis (not built)</div></div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="wb-card">
<h4>How this section works</h4>
<p>Each <strong>built</strong> concept page has: a summary and mental model · a flowchart of the mechanism ·
a <strong>code lab</strong> where you edit real Python and press <em>Run</em> against a simulated Claude and a fake
backend · the exam <strong>distractors</strong>, each loadable as runnable code so you can watch it fail · a
side-by-side table and decision tree · original practice questions. After a run, the flowchart lights up along
the path <em>your</em> code took.</p>
<p><strong>Rule: every concept is 100% grounded in the official Claude docs</strong> (platform.claude.com and
code.claude.com). Each built page lists the docs pages it was written from and tags every claim as 📘 docs · 🎓 guide ·
💡 my recommendation · 🧪 simulated.</p>
<p><strong>Scope is decided by the official guide, not by the list this layout comes from.</strong> Tags: 🎯 in the
guide · ◐ partly in the guide (both = ⭐ <strong>exam topic</strong>, with its exact guide section and page on the concept page) · ➕ <em>extra</em> — not on the exam, but an official docs page covers it (built after the
exam concepts, labelled as such) · ℹ️ awareness only · ⛔ explicitly out of scope · ⚪ not in the guide and no docs basis
found (not built). Build order: exam concepts first, one at a time with <code>/next-concept</code>. The tags are Claude's
judgment (keyword search of guide v1.0, 2026-09-26): verify them in <code>docs/CONCEPTS_MAP.md</code>.</p>
<p class="wb-cite">Layout inspired by a community concept list (claudearchitectcertification.com/concepts) — a
third-party source: unverified, used for structure only, no content copied.</p>
</div>
""", unsafe_allow_html=True)


def _card(c: cm.Concept) -> None:
    built_lab = cm.is_built(c.slug)
    with st.container(border=True):
        badge = ("➕ Extra — not on the exam" if cm.kind(c) == "extra"
                 else "⭐ EXAM TOPIC" if cm.kind(c) == "exam"
                 else f"{cm.STATUS_ICON[c.status]} {cm.STATUS_LABEL[c.status]}")
        st.caption(f"{c.code or 'Cross-cutting'} · {badge}" + (("  ·  📘 awareness page" if cm.kind(c) == "excluded" else "  ·  🧪 lab built") if built_lab else ""))
        st.markdown(f"**{c.title}**")
        alignment = cm.guide_alignment(c)
        st.caption(alignment if alignment else "No guide task statement")
        page = pages.get(c.slug)
        if page is not None:
            st.page_link(page, label="Open the lab" if built_lab and cm.kind(c) != "excluded" else "Open",
                         icon="🧪" if built_lab and cm.kind(c) != "excluded" else "🔗")


def _grid(concepts: list) -> None:
    for start in range(0, len(concepts), 3):
        cols = st.columns(3)
        for col, concept in zip(cols, concepts[start:start + 3]):
            with col:
                _card(concept)


tab_labels = ["All topics"] + [f"D{d} · {DOMAINS[d][0]}" for d in DOMAINS] + [f"Cross-cutting ({len(cm.cross_cutting())})"]
tabs = st.tabs(tab_labels)

with tabs[0]:
    _grid(list(cm.CONCEPTS))
for i, d in enumerate(DOMAINS, start=1):
    with tabs[i]:
        name, weight, _ = DOMAINS[d]
        st.caption(f"Domain {d} — {name} · {weight} of the exam")
        _grid(cm.by_domain(d))
with tabs[-1]:
    st.caption("Unnumbered on the community list. Most are not part of CCAR-F — see each card's tag.")
    _grid(cm.cross_cutting())
