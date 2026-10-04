"""
CCAR-F Study Workbench — main entry point.
Defines sidebar navigation grouped by phase.
Run with: streamlit run app.py

The sidebar shows the full 46-page roadmap from utils/course_map.py. Pages
CLAUDE.md's Phase Status table marks 🔜 get a shared placeholder page
(utils/placeholder.py) instead of a real file, so the nav never has a dead
or missing link. When a page is actually built, its PageEntry in
course_map.py flips to built=True and its file: path below is added -
see utils/placeholder.py's docstring for the three-step checklist.
"""

import functools
import streamlit as st
from utils.styles import apply_theme
from utils.course_map import PHASES, nav_title
from utils.placeholder import render_placeholder
from utils import concepts_map as cm
from utils.concept_page import render_concept

st.set_page_config(
    page_title="CCAR-F Study Workbench",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()

# Real, built pages point at their file. Everything else in course_map.py
# renders through the shared placeholder. Add a line here the same commit
# a page's `built` flag flips to True.
_REAL_PAGES = {
    "00_Hello_Claude": "pages/00_Hello_Claude.py",
    "00a_Home": "pages/00a_Home.py",
    "00b_Exam_Blueprint": "pages/00b_Exam_Blueprint.py",
}

nav: dict[str, list] = {}
for phase_group, entries in PHASES.items():
    pages = []
    for entry in entries:
        if entry.built and entry.slug in _REAL_PAGES:
            # Hello Claude stays the landing page even though CONCEPTS now sit first in the sidebar.
            pages.append(st.Page(_REAL_PAGES[entry.slug], title=nav_title(entry),
                                 default=(entry.slug == "00_Hello_Claude")))
        else:
            pages.append(st.Page(
                functools.partial(render_placeholder, entry, phase_group),
                title=nav_title(entry),
                icon="🔜",
                # functools.partial objects all share one __name__, so Streamlit's
                # inferred URL pathname collides across every placeholder unless
                # each is given an explicit, unique one.
                url_path=entry.slug,
            ))
    nav[phase_group] = pages

# ── CONCEPTS (shown at the TOP of the sidebar; the phase groups above are unchanged) ──
# One Page per concept in utils/concepts_map.py. The 30 numbered concepts (D1.1 …
# D5.2) get sidebar entries under their domain; the 41 unnumbered "cross-cutting"
# ones are registered but hidden from the sidebar (still reachable from the index
# page's cards) so the sidebar isn't flooded with topics that mostly aren't in the
# guide. The Page objects are shared via session state so the index and "related
# concepts" links can st.page_link to them.
concept_pages = {
    c.slug: st.Page(
        functools.partial(render_concept, c.slug),
        title=cm.nav_title(c),
        url_path=cm.page_url_path(c.slug),
        visibility="visible" if c.code else "hidden",
    )
    for c in cm.CONCEPTS
}
st.session_state["_concept_pages"] = concept_pages

concepts_nav: dict[str, list] = {
    "CONCEPTS": [st.Page("pages/concepts_index.py", title="All concepts", icon="🧪", url_path="concepts")] + [
        concept_pages[c.slug] for c in cm.cross_cutting()
    ]
}
# D2.3.1 and D2.3.2 are hand-written LIVE pages (real MCP servers), not concepts_map entries: they sit straight
# after D2.3 MCP in the sidebar and leave the 71-concept taxonomy and its counts untouched.
mcp_live_pages = {
    "hosted": st.Page("pages/c231_mcp_hosted.py", title="D2.3.1 MCP client → hosted server  ➕🌐", url_path="concept-mcp-hosted"),
    "local": st.Page("pages/c232_mcp_local.py", title="D2.3.2 My own MCP server (local)  ➕🏠", url_path="concept-mcp-local"),
}
st.session_state["_mcp_pages"] = mcp_live_pages
for domain, short in cm.DOMAIN_SHORT.items():
    group = []
    for c in cm.by_domain(domain):
        group.append(concept_pages[c.slug])
        if c.slug == "mcp":
            group += list(mcp_live_pages.values())
    concepts_nav[f"CONCEPTS · D{domain} {short}"] = group
nav = {**concepts_nav, **nav}

pg = st.navigation(nav)
pg.run()
