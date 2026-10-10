"""
10.0 — Study sources: the community repositories and websites collated as the basis for section 10 · MCQs.
Data: utils/study_repos.py. Static page: no network call, no key, no model.
"""

import importlib

import streamlit as st

from utils import mcq_page, study_repos as sr

importlib.reload(sr)      # Streamlit keeps imported modules in memory: reload so edits show without a restart

st.set_page_config(page_title="10.0 — Study sources", page_icon="📚", layout="wide")

st.title("📚 10 · MCQs — Study sources")
st.caption(f"➕ Extra · found {sr.FOUND_ON} · community material is unofficial: the exam guide decides scope, the official docs decide "
           "facts · used for topics and traps only, nothing copied")

st.markdown(f"**GitHub: {len(sr.GITHUB)} repositories** (stars, licence and last push as GitHub reported them on {sr.FOUND_ON})")
rows = []
for repo, stars, lic, pushed, what, read in sr.GITHUB:
    rows.append([f"[{repo}](https://github.com/{repo})", "—" if stars is None else f"{stars:,}", lic, pushed, what, read])
mcq_page._table(["Repository", "Stars", "Licence", "Last push", "What it is", "What I read"], rows)
st.caption("“none” = GitHub shows no licence, so the text stays all-rights-reserved: it can be read, not reused. That is why every "
           "question here is original and carries a quote from an official page instead.")

st.markdown("**GitLab**")
st.write(sr.GITLAB)

st.markdown("**Websites** (from web search results only; I did not open them, so no claim is made about their quality)")
mcq_page._table(["Site", "What the search result says"], [[f"[{n}]({u})", d] for n, u, d in sr.WEBSITES])

st.markdown("**Where a community source differs from the official docs** (found while checking the questions)")
mcq_page._table(["Source", "It says", "The official docs say", "Who agrees with the docs", "Used in"],
                [list(r) for r in sr.DISAGREEMENTS])
st.caption("Re-check these claims any time: `python -m utils.mcq_verify` re-reads the raw repository files.")
