"""
render_trace() — standardised Execution Trace expander.
Ensures every model-calling page has a consistent title, tab numbering, and
structure. Identical to agents101's utils/trace.py.

Usage (single tab):
    render_trace(("Model Call", fn))

Usage (multi-tab):
    render_trace(
        ("Model Call",     fn_call),
        ("Raw Output",     fn_raw),
        ("Decision Logic", fn_logic),
    )

Each fn is a zero-argument callable that renders its tab content.
Inner functions with closures work naturally:

    def _tab_call():
        st.code(system_prompt)
        st.code(user_msg)

    def _tab_raw():
        st.code(raw_response)

    render_trace(("Model Call", _tab_call), ("Raw Output", _tab_raw))

Per CLAUDE.md's Execution Trace Standard, pages that call the model must
also show, inside these tabs: the finish reason with the Claude term beside
it (e.g. "function_call present -> Claude: stop_reason = tool_use"), every
function_call/function_response block, the function-calling mode used (with
the Claude tool_choice term beside it), and token counts from usage_metadata.
"""

import streamlit as st

_NUMS = "①②③④⑤"
TRACE_TITLE = "🔬 Execution Trace — exact prompts and raw responses"


def render_trace(*sections: tuple) -> None:
    """
    Render a standardised Execution Trace expander.

    sections: one or more (label, render_fn) tuples
    Single section: content rendered without a tab bar.
    Multiple sections: each gets a numbered tab ①②③...
    """
    with st.expander(TRACE_TITLE):
        if not sections:
            return
        if len(sections) == 1:
            sections[0][1]()
        else:
            tab_labels = [f"{_NUMS[i]} {lbl}" for i, (lbl, _) in enumerate(sections)]
            tabs = st.tabs(tab_labels)
            for tab, (_, fn) in zip(tabs, sections):
                with tab:
                    fn()
