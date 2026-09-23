"""
Shared "coming soon" page shown in the sidebar for every page CLAUDE.md's
Phase Status table still marks 🔜. One function, reused as a bound callable
for every not-yet-built nav entry — see app.py — so the sidebar shows the
whole 46-page course now, without 45 stub files that would each need to be
kept in sync by hand.

When a page is actually built (Stage B, one per /next-page session):
1. write pages/<real file>.py to the full Page Structure Standard
2. in app.py, replace that entry's placeholder callable with the real file
3. in utils/course_map.py, flip that PageEntry's `built` flag to True
Do all three in the same commit - a stale flag here means the sidebar
disagrees with CLAUDE.md's Phase Status table.
"""

import streamlit as st
from utils.styles import phase_header, ACCENT_COMING
from utils.course_map import PageEntry


def render_placeholder(entry: PageEntry, phase_group: str) -> None:
    st.set_page_config(page_title=f"{entry.title} — not built yet", page_icon="🔜", layout="wide")

    st.markdown(phase_header(
        phase_group,
        f"🔜 {entry.title}",
        "Not built yet — this is a placeholder so the full course map is visible from page one.",
        accent=ACCENT_COMING,
    ), unsafe_allow_html=True)

    st.info(
        "This page doesn't exist yet. In the Claude Code panel, type **`/next-page`** — "
        "it builds pages in phase order, so this one becomes real once its turn comes up."
    )

    bits = []
    guide_ref = entry.guide_ref()
    if guide_ref:
        bits.append(f"**Guide reference:** {guide_ref}")
    if entry.interactive:
        bits.append("**★ Real interactive demo** planned")
    if entry.needs_claude_key:
        bits.append(
            "**🔑 Uses the real Claude API.** When built, this page will remind you "
            "to buy `ANTHROPIC_API_KEY` if it isn't set yet."
        )
    if bits:
        st.markdown("  \n".join(bits))

    st.caption("Full roadmap and build order: `CLAUDE.md` → Phase Status tables and Capstone Protocol.")
