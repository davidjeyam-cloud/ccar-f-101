"""
Renderer for section 10 · MCQs (pages/m101_mcqs_mcp.py, pages/m102_mcqs_skills.py, pages/m100_mcq_sources.py).

Plain on purpose (user feedback on other pages: little text, no tabs): a score line, then each question as a card.
Pick an option and the answer is checked at once; under every answer an expander shows HOW it was checked — the word-for-word
quote from the official page, the community cross-check, and any live CLI observation. No model call, no key, no network.
"""

import streamlit as st

from utils.guide_index import SCENARIO_NAME, point_ref
from utils.mcq_sets import CHECKED_ON, SETS, SOURCES, TITLES


def esc(text: str) -> str:
    """Escape `$` outside backtick spans so Streamlit does not read ${...} or $ARGUMENTS as maths."""
    parts = text.split("`")
    return "`".join(p.replace("$", "\\$") if i % 2 == 0 else p for i, p in enumerate(parts))


def _table(headers, rows) -> None:
    cell = lambda t: str(t).replace("|", "\\|").replace("\n", " ")
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    lines += ["| " + " | ".join(cell(c) for c in r) + " |" for r in rows]
    st.markdown("\n".join(lines))


def _how_checked(q) -> None:
    with st.expander("How this answer was checked"):
        st.markdown("**Official wording** (word for word; re-checked by `python -m utils.mcq_verify`)")
        for e in q.evidence:
            title, url, _ = SOURCES[e.src]
            st.markdown(f"> {esc(e.quote)}  \n> — [{title}]({url})")
        if q.live:
            st.markdown("**Seen on the real CLI**")
            st.markdown(esc(q.live))
        if q.community:
            st.markdown("**Community cross-check** (study repositories, read for coverage only)")
            st.markdown(esc(q.community))
        refs = " · ".join(point_ref(p.split(":")[0], p.split(":")[1][0], int(p.split(":")[1][1:])) for p in q.points)
        st.caption("⭐ What this tests in the exam guide: " + refs)


def render(key: str) -> None:
    qs = SETS[key]
    title = TITLES[key]
    st.title(f"📝 10 · MCQs — {title}")
    st.caption(f"➕ Own section, not in the exam question bank · {len(qs)} original questions · answers checked against official pages on "
               f"{CHECKED_ON} · not real exam questions")

    picks = {q.id: st.session_state.get(f"mcq_{key}_{q.id}_label") for q in qs}      # widget state is set before the script runs
    done = [q for q in qs if picks[q.id] is not None]
    right = sum(1 for q in done if "ABCD".index(picks[q.id][0]) == q.ans)
    st.markdown(f"**Score: {right} / {len(done)} answered** (of {len(qs)})")

    with st.expander("How these questions were built and checked"):
        st.markdown(
            "1. **Scope:** the official exam guide (task statements "
            + ("2.4 and 2.2" if key == "mcp" else "3.2") + ").\n"
            "2. **Topics and traps:** the community study repositories collated on the *Study sources* page, read for what they "
            "test. Nothing is copied.\n"
            "3. **Facts:** every correct answer has a word-for-word quote from an official page, shown under the answer.\n"
            "4. **Back-test:** `python -m utils.mcq_verify` downloads those pages again and checks every quote, the answer "
            "positions and the option lengths. A corrupted quote is rejected.\n"
            "5. **Live:** where the real Claude Code CLI could show the behaviour safely, it was run in an isolated config folder.")
        st.caption("📘 = the behaviour comes from the official docs and goes beyond the guide's wording. Where the guide and the docs "
                   "word something differently, the explanation says so.")

    for n, q in enumerate(qs, 1):
        with st.container(border=True):
            s = q.scenarios[0]
            st.markdown(f"**{q.id}** · 📋 Scenario {s}: {SCENARIO_NAME[s]}" + ("  ·  📘 docs-based" if q.basis == "docs" else ""))
            st.markdown(esc(q.q))
            labels = [f"{'ABCD'[i]})  {esc(o)}" for i, o in enumerate(q.opts)]
            choice = st.radio("Your answer", labels, index=None, key=f"mcq_{key}_{q.id}_label", label_visibility="collapsed")
            if choice is not None:
                picked = labels.index(choice)
                if picked == q.ans:
                    st.success("Correct. " + esc(q.explain))
                else:
                    st.error(f"Not quite. The best answer is **{'ABCD'[q.ans]}**. " + esc(q.explain))
                _how_checked(q)
