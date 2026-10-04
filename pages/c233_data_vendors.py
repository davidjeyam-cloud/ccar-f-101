"""
D2.3.3 — Financial-data vendors: what they expose over MCP and APIs  (➕ extra — not on the CCAR-F exam)

A reference table for an investment-banking agent that would draw on several data sources: for each vendor, the MCP
and API endpoints it publishes, what it sells (high level), and how a client gets access. Every row carries a basis
label saying whether it was read on the vendor's own page. The facts and their sources are in utils/vendor_facts.py.
This page makes no network call and needs no key, so it works on the hosted copy too.
"""

import streamlit as st

from utils import vendor_facts as vf

st.set_page_config(page_title="D2.3.3 — Financial-data vendors", page_icon="🏦", layout="wide")
st.markdown("<style>table { font-size:0.9rem; } td, th { vertical-align: top; }</style>", unsafe_allow_html=True)


def _cell(text) -> str:
    return str(text).replace("|", "\\|").replace("$", "\\$").replace("\n", " ")


def _table(headers, rows) -> None:
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    lines += ["| " + " | ".join(_cell(c) for c in r) + " |" for r in rows]
    st.markdown("\n".join(lines))


st.title("🏦 Financial-data vendors — what they expose")
st.caption(f"What each vendor publishes over MCP and APIs, what it sells, and how a client gets it · read {vf.READ_ON} · "
           "➕ Extra: not on the CCAR-F exam · not investment or procurement advice")

st.markdown("**Basis of each row**")
_table(["", "Meaning"], [[k, v] for k, v in vf.BASIS.items()])
st.caption("No price appears on this page: none of the pages I read states one. Where a page did not say something, the "
           "table says “not stated”.")

tabs = st.tabs(["📋 At a glance", "🔎 Vendor details and sources", "🧭 For an investment-banking agent", "⚠️ What I could not check"])

with tabs[0]:
    _table(["#", "Vendor", "MCP server", "API", "What they sell (high level)", "How a client gets access", "Basis"],
           [[str(i), f"**{v}**" + (f" — {g}" if g != "—" else ""), mcp, api, sells, access, basis]
            for i, (v, g, mcp, api, sells, access, basis) in enumerate(vf.GLANCE, 1)])
    st.caption("MCP = a server an AI agent connects to and calls tools on. API = the vendor's own web or library interface for "
               "programs. “Not stated” means the vendor's page did not say.")

with tabs[1]:
    st.markdown("One section per vendor: the details behind the table, and the pages each row was read from.")
    for vendor, facts, sources in vf.DETAILS:
        with st.expander(vendor):
            _table(["Topic", "What the page says"], [[t, x] for t, x in facts])
            if sources:
                st.markdown("**Pages read:** " + " · ".join(f"[{label}]({url})" for label, url in sources))

with tabs[2]:
    st.markdown("**Which source answers which question** — my reading of the table, not a claim by any vendor.")
    _table(["#", "A question the agent asks", "Sources that cover it"],
           [[str(i), q, a] for i, (q, a) in enumerate(vf.AGENT_MAP, 1)])
    st.markdown("**What the vendors have in common**")
    _table(["#", "Pattern", "What the rows show"], [[str(i), p, t] for i, (p, t) in enumerate(vf.PATTERNS, 1)])
    st.markdown("**Next step for the agent:** the MCP client on pages D2.3.1 and D2.3.2 connects to one MCP server by URL "
                "(Streamable HTTP) or by command (stdio). A vendor server that signs the user in with OAuth is the same "
                "client with a different URL and a sign-in step; this workbench's client does not do that sign-in yet.")

with tabs[3]:
    st.markdown("Things I could not verify, so you can decide what to chase before building on this table:")
    st.markdown("\n".join(f"- {g}" for g in vf.GAPS))
