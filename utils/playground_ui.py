"""
Streamlit UI for the agent playground: one tab per sub-concept, each with its own message box, its own knobs
(the developer-side constraints that sub-concept is about) and a transcript of how the agent handled it.
Engine: utils/agent_playground.py. Content (tabs, blurbs, mental models): the concept's `playground` tuple.

Everything the "model" does is SIMULATED and labelled so on screen.
"""

import html

import streamlit as st

from utils.agent_playground import IN_RATE_PER_1K, OUT_RATE_PER_1K, PlayConfig, run_agent
from utils.guide_index import resolve_source

HISTORY_KEEP = 3   # runs kept per tab

# what each knob is, for the widgets: key -> (label, kind, extra)
_KNOBS = {
    "max_tokens": ("max_tokens (per request)", "int", {"min_value": 20, "max_value": 2048, "step": 10,
                   "help": "The API parameter: the most output tokens one response may use."}),
    "max_tokens_policy": ("When stop_reason is max_tokens…", "choice",
                          {"options": {"raise": "raise max_tokens and ask again (handled)",
                                       "surface": "report it as a result (don't show it as an answer)"}}),
    "refusal_policy": ("When stop_reason is refusal…", "choice",
                       {"options": {"different_model": "retry on a DIFFERENT model (docs)",
                                    "same_model": "retry the SAME model (up to 3×)",
                                    "stop": "stop, no retry"}}),
    "pause_policy": ("When stop_reason is pause_turn…", "choice",
                     {"options": {"resume": "send the response back as-is (docs)",
                                  "treat_as_final": "treat it as the final answer (bug)"}}),
    "stop_sequences": ("Stop sequence (your tripwire text)", "text",
                       {"help": "If the reply would contain this text, generation halts there. Leave empty for none."}),
    "context_window": ("Context window (SIMULATED tokens)", "int", {"min_value": 0, "max_value": 2000, "step": 10,
                       "help": "0 = unlimited. Each request re-sends the whole conversation, so input tokens grow every turn."}),
    "max_turns": ("max_turns (tool-use turns)", "int", {"min_value": 0, "max_value": 30, "step": 1,
                  "help": "0 = no limit (the SDK default). Counts tool-use turns only."}),
    "max_budget_usd": ("max_budget_usd (SIMULATED $)", "float", {"min_value": 0.0, "max_value": 0.05, "step": 0.0005,
                       "format": "%.4f", "help": "0 = no limit (the SDK default). Illustrative rates, not real pricing."}),
}


def _bubble(text: str, role: str = "assistant", avatar: str | None = None) -> None:
    with st.chat_message(role, avatar=avatar):
        st.markdown(text)


def _render_run(run: dict) -> None:
    for ev in run["events"]:
        t = ev["type"]
        if t == "user":
            _bubble(ev["text"], "user")
            if not ev["intent"]:
                st.caption("No order mentioned → the simulated model answers without tools (a model-driven decision).")
        elif t == "api":
            parts = []
            for b in ev["blocks"]:
                if b["type"] == "text":
                    parts.append(b["text"] or "*(empty text)*")
                else:
                    parts.append(f"`{b['type']}: {b['name']}({b['input']})`")
            body = "  \n".join(parts) if parts else "*(empty content — the response has no blocks)*"
            _bubble(body)
            det = f" · stop_details = `{ev['stop_details']}`" if ev["stop_details"] else ""
            seq = f" · stop_sequence = `{ev['stop_sequence']}`" if ev["stop_sequence"] else ""
            st.caption(f"call #{ev['call']} · {ev['model']} · max_tokens {ev['max_tokens']} · in {ev['in']} / out {ev['out']} "
                       f"tokens · ${ev['cost']:.4f} (running ${ev['spent']:.4f})")
            st.markdown(f"**`stop_reason = {ev['stop_reason']}`**{det}{seq}  \n➡️ *{ev['action']}*")
        elif t == "tool":
            _bubble(f"ran `{ev['name']}({ev['args']})` → `{ev['result'][:110]}`", avatar="🛠️")

    res = run["result"]
    lines = (f"**Result: `{res['subtype']}`**  \n{res['why']}  \n"
             f"API calls {res['api_calls']} · tool turns {res['tool_turns']} · simulated spend ${res['spent']:.4f}")
    if res["text"]:
        lines += f"  \nText returned: “{res['text']}”"
    tag = ("SDK result subtype" if res["source"] == "sdk" else
           "this playground's label — not an SDK subtype")
    if res["ok"]:
        st.success(lines)
    elif res["subtype"].startswith("error_"):
        st.error(lines)
    else:
        st.warning(lines)
    st.caption(f"Label type: {tag}.")


def _knob_widget(base: str, knob: str, default):
    label, kind, extra = _KNOBS[knob]
    key = f"{base}_{knob}"
    if kind == "int":
        return st.number_input(label, value=int(default), key=key, **extra)
    if kind == "float":
        return st.number_input(label, value=float(default), key=key, **extra)
    if kind == "text":
        return st.text_input(label, value=str(default), key=key, **extra)
    options = list(extra["options"])
    return st.selectbox(label, options, index=options.index(default), key=key,
                        format_func=lambda o: extra["options"][o])


def _render_tab(slug: str, spec) -> None:
    base = f"pg_{slug.replace('-', '_')}_{spec.key}"
    hist_key = f"{base}_history"

    if spec.exam_source:
        st.markdown(f"**{resolve_source(spec.exam_source)}**")
    else:
        st.markdown("**📘 Official docs — beyond the guide's wording (not gold)**")
    st.info(f"🧭 **Mental model.** {spec.mental_model}")
    st.markdown(spec.meaning)
    st.caption(f"Docs: {spec.docs}")

    st.markdown("**Constraints you control (the developer side)**")
    values = {}
    if spec.knobs:
        cols = st.columns(min(3, len(spec.knobs)))
        for i, knob in enumerate(spec.knobs):
            with cols[i % len(cols)]:
                values[knob] = _knob_widget(base, knob, spec.defaults.get(knob, PlayConfig.__dataclass_fields__[knob].default
                                                                          if knob in PlayConfig.__dataclass_fields__ else 0))
    else:
        st.caption("No knobs on this tab — it shows the normal loop. Try different messages.")

    st.markdown("**Say something to the agent** (each message starts a fresh run)")
    msg = st.text_input("Your message", value=spec.examples[0], key=f"{base}_msg", label_visibility="collapsed")
    st.caption("Try: " + "  ·  ".join(f"`{e}`" for e in spec.examples))
    c1, c2, _ = st.columns([1, 1, 4])
    send = c1.button("▶ Send", type="primary", key=f"{base}_send")
    if c2.button("🗑 Clear", key=f"{base}_clear"):
        st.session_state[hist_key] = []

    if send:
        if not msg.strip():
            st.warning("Type a message first.")
        else:
            cfg = PlayConfig(condition=spec.condition,
                             **{**({"max_tokens": 1024} if "max_tokens" not in values else {}),
                                **{k: (tuple(s for s in [v] if s) if k == "stop_sequences" else v) for k, v in values.items()}})
            with st.spinner("Running the simulated agent…"):
                run = run_agent(msg.strip(), cfg)
            hist = st.session_state.setdefault(hist_key, [])
            hist.insert(0, {"cfg": cfg, "run": run})
            del hist[HISTORY_KEEP:]

    for i, item in enumerate(st.session_state.get(hist_key, [])):
        with st.container(border=(i == 0)):
            if i == 0:
                st.markdown("**Latest run**")
            else:
                st.markdown(f"*Earlier run #{i}*")
            _render_run(item["run"])

    if spec.try_this:
        with st.expander("Try this next"):
            for i, t in enumerate(spec.try_this, 1):
                st.markdown(f"{i}. {t}")


def render_playground(slug: str, content) -> None:
    st.subheader("💬 Agent playground — type a message, watch how the agent handles it")
    st.markdown(content.playground_intro)
    st.markdown(
        '<div class="cc-sim"><strong>SIMULATED.</strong> The agent loop is real workbench code, but the “model” is a '
        f'scripted stand-in (<code>utils/mock_claude.py</code>) — not Claude. Token sizes are invented and dollars use '
        f'illustrative rates (${IN_RATE_PER_1K}/1K in, ${OUT_RATE_PER_1K}/1K out), <em>not real pricing</em>. It runs '
        "in this app's process; no API key, no cost.</div>", unsafe_allow_html=True)
    tabs = st.tabs([t.label for t in content.playground])
    for tab, spec in zip(tabs, content.playground):
        with tab:
            _render_tab(slug, spec)
