"""Draw a Mermaid diagram in the browser (mermaid.js@11 from jsdelivr, so it needs internet; the source is escaped and
shown as a fallback message if the script does not load). Same approach as pages/c234_mcp_oracle.py::_mermaid, shared here
so concept pages can use it too. Syntax reference: .claude/skills/mermaid-diagram-specialist/."""

import streamlit as st
import streamlit.components.v1 as components


def page_html(source: str) -> str:
    escaped = source.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f"""
        <style>body {{ margin:0; font-family:sans-serif }} pre.mermaid {{ display:flex; justify-content:center; margin:0 }}</style>
        <pre class="mermaid">{escaped}</pre>
        <p id="fail" style="display:none;color:#a33">The diagram could not be drawn: mermaid.js did not load
        (it needs internet access).</p>
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


def show(source: str, height: int) -> None:
    page = page_html(source)
    if hasattr(st, "iframe"):                      # newer Streamlit: components.v1.html is deprecated there
        st.iframe(page, height=height)
    else:
        components.html(page, height=height, scrolling=True)
