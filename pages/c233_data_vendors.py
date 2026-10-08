"""
D2.3.3 — Financial-data vendors: what they expose over MCP and APIs  (➕ extra — not on the CCAR-F exam)

A reference table for an investment-banking agent that would draw on several data sources: for each vendor, the MCP
and API endpoints it publishes, what it sells (high level), and how a client gets access. Every row carries a basis
label saying whether it was read on the vendor's own page. The facts and their sources are in utils/vendor_facts.py.
This page makes no network call and needs no key, so it works on the hosted copy too.
"""

import streamlit as st

import importlib

from utils import vendor_facts as vf

importlib.reload(vf)   # Streamlit keeps imported modules in memory: reload so edits to the facts file show without a restart

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

tabs = st.tabs(["📋 At a glance", "🧰 Tools and APIs", "🧱 Databricks Marketplace", "🔎 Vendor details and sources", "🧭 For an investment-banking agent", "⚠️ What I could not check"])

with tabs[0]:
    _table(["#", "Vendor", "MCP server", "API", "What they sell (high level)", "How a client gets access", "Basis"],
           [[str(i), f"**{v}**" + (f" — {g}" if g != "—" else ""), mcp, api, sells, access, basis]
            for i, (v, g, mcp, api, sells, access, basis) in enumerate(vf.GLANCE, 1)])
    st.caption("MCP = a server an AI agent connects to and calls tools on. API = the vendor's own web or library interface for "
               "programs. “Not stated” means the vendor's page did not say.")

with tabs[1]:
    n_tools = len(vf.MCP_TOOLS)
    st.markdown(f"**MCP tools listed by name on the vendors' pages: {n_tools} in total, from 4 vendors (the 11 FactSet names are from a search summary, marked 🔎).**")
    _table(["#", "Vendor", "Tools listed", "Page", "Note"],
           [[str(i), v, n, f"[page]({u})" if u else "—", note] for i, (v, n, u, note) in enumerate(vf.TOOL_COUNTS, 1)])
    st.markdown("**MCP tools** — inputs and outputs as the page states them")
    _table(["#", "Vendor", "Tool", "Short description", "MCP inputs", "MCP outputs"],
           [[str(i), *row] for i, row in enumerate(vf.MCP_TOOLS, 1)])
    st.markdown("**REST and library APIs** — the same columns, kept apart because the API calls are not one-to-one with the MCP tools")
    _table(["#", "Vendor", "API or endpoint", "Short description", "REST inputs", "REST outputs"],
           [[str(i), *row] for i, row in enumerate(vf.REST_APIS, 1)])
    st.caption("“not stated” = the page I read did not say. Parameter names are the vendors' own. Vendors absent from the tool "
               "table publish no tool list on the pages I could read; I did not guess one.")

with tabs[2]:
    st.markdown("**What Databricks Marketplace lists** — per its product page")
    _table(["#", "Type", "Note"], [[str(i), t, n] for i, (t, n) in enumerate(vf.DBX_TYPES, 1)])
    st.markdown(f"**MCP servers named on Databricks' own blog posts: {len(vf.DBX_MCP)}**")
    _table(["#", "Provider", "Product", "What it offers", "Access method", "Basis"],
           [[str(i), *row] for i, row in enumerate(vf.DBX_MCP, 1)])
    st.markdown("**Pages read:** " + " · ".join(f"[{label}]({url})" for label, url in vf.DBX_SOURCES))
    st.markdown("**What I could not check**")
    st.markdown("\n".join(f"- {g}" for g in vf.DBX_GAPS))

with tabs[3]:
    st.markdown("One section per vendor: the details behind the table, and the pages each row was read from.")
    for vendor, facts, sources in vf.DETAILS:
        with st.expander(vendor):
            _table(["Topic", "What the page says"], [[t, x] for t, x in facts])
            if sources:
                st.markdown("**Pages read:** " + " · ".join(f"[{label}]({url})" for label, url in sources))

with tabs[4]:
    st.markdown("**Which source answers which question** — my reading of the table, not a claim by any vendor.")
    _table(["#", "A question the agent asks", "Sources that cover it"],
           [[str(i), q, a] for i, (q, a) in enumerate(vf.AGENT_MAP, 1)])
    st.markdown("**What the vendors have in common**")
    _table(["#", "Pattern", "What the rows show"], [[str(i), p, t] for i, (p, t) in enumerate(vf.PATTERNS, 1)])
    st.markdown("**Next step for the agent:** the MCP client on pages D2.3.1 and D2.3.2 connects to one MCP server by URL "
                "(Streamable HTTP) or by command (stdio). A vendor server that signs the user in with OAuth is the same "
                "client with a different URL and a sign-in step; this workbench's client does not do that sign-in yet.")

with tabs[5]:
    st.markdown("Things I could not verify, so you can decide what to chase before building on this table:")
    st.markdown("\n".join(f"- {g}" for g in vf.GAPS))
