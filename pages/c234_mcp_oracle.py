"""
D2.3.4 — Chat question → SQL on an Oracle database, through MCP  (➕ extra — not on the CCAR-F exam)

One top-down, layered Mermaid diagram carries the whole path; two "zoom" sections expand one part each (how the
LLM learns the table names, and a second server), each laid out like the main one: diagram left, example cards right.
No tabs. Facts and diagram sources:
utils/mcp_oracle_facts.py. No model call, no key; diagrams are drawn in the browser by mermaid.js (loaded from a CDN),
so they need internet access to draw. The source is shown if they cannot load.
"""

import json

import streamlit as st
import streamlit.components.v1 as components

import importlib

from utils import mcp_oracle_facts as of

importlib.reload(of)   # Streamlit keeps imported modules in memory: reload so edits to the facts file show without a restart

st.set_page_config(page_title="D2.3.4 — Chat to SQL on Oracle", page_icon="🗄️", layout="wide")


def _mermaid(source: str, height: int) -> None:
    """Draw a Mermaid diagram in the browser. The source is escaped so it cannot break out of the page."""
    escaped = source.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    page = f"""
        <style>body {{ margin:0; font-family:sans-serif }} pre.mermaid {{ display:flex; justify-content:center; margin:0 }}</style>
        <pre class="mermaid">{escaped}</pre>
        <p id="fail" style="display:none;color:#a33">The diagram could not be drawn: mermaid.js did not load
        (it needs internet access). Its source is under the page.</p>
        <script type="module">
          try {{
            const mermaid = (await import("https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs")).default;
            mermaid.initialize({{ startOnLoad: false, securityLevel: "strict", theme: "base",
              themeVariables: {{ fontSize: "17px", edgeLabelBackground: "#ffffff" }},
              flowchart: {{ htmlLabels: true, curve: "basis", nodeSpacing: 30, rankSpacing: 50 }} }});
            await mermaid.run({{ querySelector: ".mermaid" }});
          }} catch (e) {{
            document.getElementById("fail").style.display = "block";
          }}
        </script>"""
    if hasattr(st, "iframe"):                      # newer Streamlit: components.v1.html is deprecated there
        st.iframe(page, height=height)
    else:
        components.html(page, height=height, scrolling=True)


st.title("🗄️ Chat question → SQL on Oracle, through MCP")
st.caption("➕ Extra: not on the CCAR-F exam · the diagram and the cards show the same run, with the same step numbers")

st.info(of.KEY_IDEA)

left, right = st.columns([6, 5], gap="large")

with left:
    _mermaid(of.MERMAID, height=1050)

with right:
    with st.container(border=True):
        st.markdown("**1 · You ask** — ① chat")
        with st.chat_message("user"):
            st.write(of.CHAT_QUESTION)
    with st.container(border=True):
        st.markdown("**2 · The LLM writes the SQL** — ② app → ③ client")
        st.caption("A tool call: tool `run-sql`, with this SQL as its argument 🧪")
        st.code(of.EXAMPLE_SQL, language="sql")
    with st.container(border=True):
        st.markdown("**3 · The client sends it** — ③ client → ④ server")
        st.code(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                            "params": {"name": "run-sql", "arguments": {"sql": of.WIRE_SQL_SHORT}}}, indent=2),
                language="json")
    with st.container(border=True):
        st.markdown("**4 · Oracle runs it · 5 · rows come back** — ④ server ⇄ ⑤ database")
        st.table({"name": [r[0] for r in of.ROWS], "total_spent": [r[1] for r in of.ROWS]})
    with st.container(border=True):
        st.markdown("**6 · The LLM answers in words** — ② app → ① you")
        with st.chat_message("assistant"):
            st.write(of.ANSWER)
    st.caption("🧪 The chat, SQL, names and numbers are my invented example, never run. The `tools/call` envelope is the "
               "MCP message shape 📘; the argument name `sql` is my example, because Oracle's page does not state "
               "`run-sql`'s inputs. The SQL is shortened in step 3.")

st.markdown("---")
st.subheader("Zoom 1 — how does the LLM know the table names?")
st.caption("To write the three-table join it must know which tables and columns exist. Three routes, A, B and C.")
zl, zr = st.columns([6, 5], gap="large")
with zl:
    _mermaid(of.ZOOM_SCHEMA, height=900)
with zr:
    with st.container(border=True):
        st.markdown(f"**A · a resource** — `{of.SCHEMA_NOTES_URI}` 🧪")
        st.code(of.SCHEMA_NOTES, language="text")
        st.caption("The app reads it and puts it in the LLM's context before the question. 📘 MCP's docs name "
                   "database schemas as a resource example.")
    with st.container(border=True):
        st.markdown("**B · a tool** — `describe-schema` 🧪")
        st.code(json.dumps({"method": "tools/call", "params": of.SCHEMA_TOOL_CALL}, indent=2), language="json")
        st.caption("An invented tool. Whether Oracle's server has one: not stated. ❓")
    with st.container(border=True):
        st.markdown("**C · a catalogue query** — through `run-sql`")
        st.code(of.CATALOGUE_SQL, language="sql")
        st.table({"table_name": [r[0] for r in of.CATALOGUE_ROWS], "column_name": [r[1] for r in of.CATALOGUE_ROWS]})
        st.caption("🏛 Oracle: `USER_TAB_COLUMNS` describes the columns of the tables you own. That the LLM queries it "
                   "through `run-sql` is my example. 🧪")

st.markdown("---")
st.subheader("Zoom 2 — a second server")
st.caption(of.TWO_SERVERS)
sl, sr = st.columns([6, 5], gap="large")
with sl:
    _mermaid(of.ZOOM_SERVERS, height=960)
with sr:
    with st.container(border=True):
        st.markdown("**1 · You ask** — ① chat")
        with st.chat_message("user"):
            st.write(of.TWO_SERVER_QUESTION)
    with st.container(border=True):
        st.markdown("**What the LLM is shown** — ② app")
        st.table({"Server": [r[0] for r in of.TOOLS_SEEN], "Tools": [r[1] for r in of.TOOLS_SEEN]})
    with st.container(border=True):
        st.markdown("**2 · Needs the data** — ③ client A → ④ server A")
        st.caption("`run-sql` with the SQL from the main example. Result: Customer A, 48,210.00 🧪")
    with st.container(border=True):
        st.markdown("**3 · Needs the web** — ③ client B → ④ server B")
        st.code(json.dumps({"method": "tools/call", "params": of.SEARCH_CALL}, indent=2), language="json")
        st.caption("An invented tool and argument. 🧪")
    with st.container(border=True):
        st.markdown("**4 · One answer** — ② app → ① you")
        with st.chat_message("assistant"):
            st.write(of.TWO_SERVER_ANSWER)

st.markdown("---")
st.markdown("**Oracle's own server** 🏛 — " + of.ORACLE_LINE)
st.caption(of.NOT_STATED)
st.markdown(" · ".join(f"[{label}]({url})" for label, url in of.SOURCES))
st.markdown("**Expand next:** " + of.NEXT_STEPS)
with st.expander("Diagram sources (Mermaid)"):
    st.code(of.MERMAID, language="text")
    st.code(of.ZOOM_SCHEMA, language="text")
    st.code(of.ZOOM_SERVERS, language="text")
