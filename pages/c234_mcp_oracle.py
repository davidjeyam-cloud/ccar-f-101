"""
D2.3.4 — Chat question → SQL on an Oracle database, through MCP  (➕ extra — not on the CCAR-F exam)

One top-down, layered Mermaid diagram carries the whole path; two small "zoom" diagrams expand one part each (how the
LLM learns the table names, and a second server). No tabs, no big tables. Facts and diagram sources:
utils/mcp_oracle_facts.py. No model call, no key; diagrams are drawn in the browser by mermaid.js (loaded from a CDN),
so they need internet access to draw. The source is shown if they cannot load.
"""

import json

import streamlit as st
import streamlit.components.v1 as components

from utils import mcp_oracle_facts as of

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
z1, z2 = st.columns(2, gap="large")
with z1:
    st.markdown("**Zoom 1 — how does the LLM know the table names?**")
    _mermaid(of.ZOOM_SCHEMA, height=500)
with z2:
    st.markdown("**Zoom 2 — a second server**")
    _mermaid(of.ZOOM_SERVERS, height=500)
    st.caption(of.TWO_SERVERS)

st.markdown("---")
st.markdown("**Oracle's own server** 🏛 — " + of.ORACLE_LINE)
st.caption(of.NOT_STATED)
st.markdown(" · ".join(f"[{label}]({url})" for label, url in of.SOURCES))
st.markdown("**Expand next:** " + of.NEXT_STEPS)
with st.expander("Diagram sources (Mermaid)"):
    st.code(of.MERMAID, language="text")
    st.code(of.ZOOM_SCHEMA, language="text")
    st.code(of.ZOOM_SERVERS, language="text")
