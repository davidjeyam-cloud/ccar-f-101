"""10.3 — MCQs: Domain 2, Tool Design & MCP Integration (20 original questions; guide TS 2.1 – 2.5). Content: utils/mcq_d2.py."""

import importlib

import streamlit as st

from utils import mcq_sets          # first: it imports utils.mcq_d2 after defining MCQ (importing mcq_d2 first would be circular)
from utils import mcq_d2, mcq_page

importlib.reload(mcq_sets)      # Streamlit keeps imported modules in memory: reload so edits show without a restart
importlib.reload(mcq_d2)
importlib.reload(mcq_sets)      # again, so SETS holds the reloaded D2 tuple
importlib.reload(mcq_page)

st.set_page_config(page_title="10.3 — MCQs: Domain 2", page_icon="📝", layout="wide")
mcq_page.render("d2")
