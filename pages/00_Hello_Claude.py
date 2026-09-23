"""
Phase 0 — Hello Claude
Confirm your setup, understand the three-key architecture, and make your
first live model call (which runs on Gemini — see the concept expander
below for why, and what that means for exam prep).
"""

import os
import streamlit as st
from dotenv import load_dotenv

from utils.styles import phase_header, ACCENT_CURRENT
from utils.diagrams import diagram_00_hello
from utils.trace import render_trace
from utils.progress import render_progress_ticks
from utils import llm

load_dotenv()

PAGE_SLUG = "00_Hello_Claude"  # see utils/progress.py naming note — never name this *_KEY

st.set_page_config(page_title="Phase 0 — Hello Claude", page_icon="👋", layout="wide")

# ── Phase header ─────────────────────────────────────────────────────────────
st.markdown(phase_header(
    "Phase 0 &nbsp;·&nbsp; Foundations &nbsp;·&nbsp; Setup",
    "👋 Hello Claude",
    "Confirm your setup, understand the three keys this workbench uses, and "
    "make your first live model call.",
    accent=ACCENT_CURRENT,
), unsafe_allow_html=True)

# ── Diagram ──────────────────────────────────────────────────────────────────
st.image(diagram_00_hello(), width="stretch")

# ── Concept ──────────────────────────────────────────────────────────────────
with st.expander("📖 What is CCAR-F, and why does this workbench run on Gemini?"):
    st.markdown("""
**What the certification tests.** The official exam guide (v1.0, CCAR-F) says the
Claude Certified Architect – Foundations exam validates that practitioners can make
informed decisions about tradeoffs when implementing real-world solutions with Claude —
across **Claude Code**, the **Claude Agent SDK**, the **Claude API**, and **MCP**.
Questions are scenario-based, drawn from 4 of a published bank of 6 production contexts,
and test judgment and architecture decisions, not trivia.

**Why this app's demos run on Gemini, not the Claude API.** You chose Gemini for this
workbench's live demos on cost grounds — it's the same setup as your earlier `agents101`
project, and it's cheap enough to run every pattern demo freely while you study. That is
a deliberate trade-off, not an oversight, and it comes with one consequence worth being
honest about: **a Gemini demo shows the *pattern* the exam is testing, not Claude's exact
fields.** Where Gemini says `function_call`, Claude says `tool_use`; where Gemini has a
function-calling *mode*, Claude has `tool_choice`. The full mapping lives in `CLAUDE.md` →
Critical SDK Notes, and every page that matters shows both terms side by side.

**Where the real Claude API comes back in.** A handful of pages — flagged 🔑 in the phase
tables — teach mechanics that only the real Claude API can show honestly (the exact
`stop_reason` loop, the three `tool_choice` modes, structured output via `tool_use`,
Message Batches). Those pages use the real Claude API and remind you to buy a small,
capped key before you reach them. Everywhere else, Claude Code itself — the tool you are
using right now, in this VS Code panel — runs on your **subscription**, with no API key
involved at all.
""")

# ── Core code pattern ─────────────────────────────────────────────────────────
with st.expander("📐 Core Code Pattern — utils/llm.py"):
    st.code('''from google import genai

client   = genai.Client(api_key=GEMINI_API_KEY)
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What does CCAR-F test, in one sentence?",
)
print(response.text)''', language="python")
    st.markdown("""
`utils/llm.py` wraps this call: it loads the key, builds the client, retries on
transient 503s, and returns plain text. Every page in this course imports the same
`chat()` function — to swap the model, you change **one line** (`MODEL = "..."`) in
that one file. When the first 🔑 page is built, a `CLAUDE_MODEL` constant is added
right next to it, using the real `anthropic` SDK instead — not a replacement for this
wrapper, a second one beside it.
""")

st.markdown("---")

# ── Key status ─────────────────────────────────────────────────────────────────
st.subheader("Your setup")

gemini_key = os.getenv("GEMINI_API_KEY")
claude_key = os.getenv("ANTHROPIC_API_KEY")

col1, col2 = st.columns(2)
with col1:
    if gemini_key:
        st.success(f"✅ **GEMINI_API_KEY** loaded — `{gemini_key[:6]}...{gemini_key[-4:]}` "
                   "(this app's demo engine)")
    else:
        st.error(
            "**GEMINI_API_KEY not found.**\n\n"
            "1. Copy `.env.example` → `.env`\n"
            "2. Paste your key from [Google AI Studio](https://aistudio.google.com/apikey)\n"
            "3. Restart Streamlit"
        )
with col2:
    if claude_key:
        st.success("✅ **ANTHROPIC_API_KEY** detected — 🔑 pages will use it when you reach them.")
    else:
        st.info(
            "ℹ️ **ANTHROPIC_API_KEY** not set yet — that's expected right now. "
            "You'll need it before page **1.1** (the first 🔑 page). "
            "See `docs/STUDY_PLAN.md` for where and when to buy it."
        )

st.markdown("---")

# ── Live demo ────────────────────────────────────────────────────────────────
st.subheader("Try it — your first live call")

prompt = st.text_input(
    "Your question:",
    value="What does the CCAR-F exam test, in one sentence?",
    placeholder="Type a question and press Send",
)

if st.button("Send", type="primary", disabled=not gemini_key):
    if not prompt.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Calling Gemini 2.5 Flash…"):
            try:
                from google import genai as _genai
                from google.genai import types as _types

                _client = _genai.Client(api_key=gemini_key)
                _resp = llm._call(
                    _client.models.generate_content,
                    model=llm.MODEL,
                    contents=prompt,
                )

                st.markdown("**Response:**")
                st.markdown(_resp.text)

                usage = getattr(_resp, "usage_metadata", None)
                has_call = bool(getattr(_resp, "function_calls", None))
                finish = "function_call present" if has_call else "text only, no function_call"
                claude_term = "stop_reason = tool_use" if has_call else "stop_reason = end_turn"

                def _tab_call():
                    st.markdown("**System prompt:** *(none — plain single-turn call)*")
                    st.markdown("**User message:**")
                    st.code(prompt, language="text")

                def _tab_raw():
                    st.code(_resp.text, language="text")

                def _tab_decision():
                    st.code(
                        f"finish reason: {finish}\n"
                        f"  -> Claude equivalent: {claude_term}\n"
                        f"function-calling mode used: none (no tools passed on this call)\n"
                        f"  -> Claude equivalent: tool_choice not applicable (no tools)\n"
                        f"tokens (usage_metadata): input={getattr(usage, 'prompt_token_count', '?')}, "
                        f"output={getattr(usage, 'candidates_token_count', '?')}",
                        language="text",
                    )

                render_trace(
                    ("Model Call", _tab_call),
                    ("Raw Output", _tab_raw),
                    ("Decision Logic", _tab_decision),
                )

            except Exception as e:
                st.error(f"Error: {e}")

with st.expander("🔍 What just happened"):
    st.markdown("""
That call went to **Gemini 2.5 Flash**, through `utils/llm.py`, the same wrapper every
later page uses. The Execution Trace above shows the finish reason Gemini actually
returned, with the Claude term it maps to written beside it — that side-by-side habit is
how every ★ page in this course stays honest about which product it's really
demonstrating.
""")

# ── The three keys, compared ───────────────────────────────────────────────────
st.markdown("#### The three keys at a glance")
st.markdown("""
| # | Claude Code (this panel) | GEMINI_API_KEY | ANTHROPIC_API_KEY |
|---|---|---|---|
| 1 | Billing: your Claude subscription | Billing: Google, pay-per-token, has a free tier | Billing: Anthropic Console, pay-per-token, no ongoing free tier |
| 2 | Needed: right now, to build every page | Needed: right now, for every page's live demo | Needed: only from page **1.1** onward (🔑 pages) |
| 3 | Cost if unset: nothing works — Claude Code *is* this session | Cost if unset: demos show a clear "needs GEMINI_API_KEY" message, page still loads | Cost if unset: 🔑 pages flash a reminder banner; the Gemini pattern demo still runs |
| 4 | Where it lives: your Claude Code login, never a file in this repo | Where it lives: local `.env`, gitignored, never committed | Where it lives: local `.env`, gitignored, never committed |
""")

# ── Traps ────────────────────────────────────────────────────────────────────
st.markdown("#### Common traps")
st.markdown("""
| # | Tempting assumption | Why it's wrong | What to do instead |
|---|---|---|---|
| 1 | "I need `ANTHROPIC_API_KEY` before I can start this course." | Only `GEMINI_API_KEY` is required to begin — it powers every pattern demo in Phases 0–7. | Set up `GEMINI_API_KEY` now; buy `ANTHROPIC_API_KEY` before Day 1 of the study plan, ahead of page 1.1. |
| 2 | "Claude Code (this VS Code panel) must have its own API key somewhere." | Claude Code runs on your subscription. There is no API key to find or protect for it. | Never search for or add an API key for Claude Code itself — only the app's two keys go in `.env`. |
| 3 | "A Gemini demo on this page *is* the Claude behaviour the exam asks about." | Gemini's `function_call`/mode system is a different product with different field names than Claude's `tool_use`/`stop_reason`/`tool_choice`. | Read the Claude↔Gemini mapping table in `CLAUDE.md` before trusting a Gemini trace as exam ground truth; use the 🔑 pages for the real thing. |
| 4 | "I can skip buying the Claude API key and still be fully exam-ready." | A handful of task statements (loops, `tool_choice`, structured output, batching) can only be shown honestly against the real Claude API. | Budget the small cost — see the pricing comparison in this session's chat history / `docs/STUDY_PLAN.md` — and buy it before page 1.1. |
""")

# ── Build it in VS Code ────────────────────────────────────────────────────────
with st.expander("🛠️ Build it in VS Code with Claude Code"):
    st.markdown("""
**Prompt to try in the Claude Code panel:**

> Create a `sandbox_project/` folder here with a minimal `CLAUDE.md` inside it that
> says `# Sandbox Project — CCAR-F exercises` and one line: "Fake data only. No real
> customer information ever." Then tell me how to confirm Claude Code has loaded it.

**Done when:**
- [ ] `sandbox_project/CLAUDE.md` exists with that content
- [ ] Running `/memory` (or opening a Claude Code session inside `sandbox_project/`)
      confirms the file is loaded
- [ ] You understand this folder is where every later "Build it" step happens — it's
      never meant to hold real data, only exercises
""")

render_progress_ticks(PAGE_SLUG)

st.markdown("### What's next → 00a — Home")
st.markdown(
    "The dashboard: your 30-cell domain coverage map, and where every phase stands."
)
