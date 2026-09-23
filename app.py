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
            pages.append(st.Page(_REAL_PAGES[entry.slug], title=nav_title(entry)))
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

pg = st.navigation(nav)
pg.run()
