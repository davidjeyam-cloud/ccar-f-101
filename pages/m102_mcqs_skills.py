"""10.2 — MCQs: Claude Skills (10 original questions; guide TS 3.2). The content is in utils/mcq_sets.py."""

import importlib

import streamlit as st

from utils import mcq_page, mcq_sets

importlib.reload(mcq_sets)      # Streamlit keeps imported modules in memory: reload so edits show without a restart
importlib.reload(mcq_page)

st.set_page_config(page_title="10.2 — MCQs: Claude Skills", page_icon="📝", layout="wide")
mcq_page.render("skills")
