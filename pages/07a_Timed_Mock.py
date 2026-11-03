"""07a · Timed Mock — 60 questions from the exam bank, 4 scenarios, 120 minutes, scored by domain."""

import time
from datetime import datetime

import streamlit as st

from utils import mock_exam as mx
from utils.guide_index import SCENARIO_NAME
from utils.course_map import DOMAINS
from utils.mcq_page import esc
from utils.progress import load_progress, save_progress

st.set_page_config(page_title="Timed Mock", page_icon="⏱️", layout="wide")
st.title("⏱️ Timed Mock")
st.caption(f"{mx.ITEMS} questions · {mx.MINUTES} minutes · 4 of the 6 scenarios drawn at random · domain mix follows the exam "
           "weights · single answer · original questions, not real exam questions")

S = st.session_state
bank = {q.id: q for q in mx.all_questions()}


def _start() -> None:
    d = mx.draw()
    S["mock"] = {"run": S.get("mock", {}).get("run", 0) + 1, "draw": d, "deadline": time.time() + mx.MINUTES * 60,
                 "result": None}


def _finish(m: dict) -> None:
    qs = [bank[i] for i in m["draw"]["ids"]]
    answers = {}
    for q in qs:
        pick = S.get(f"mock{m['run']}_{q.id}")
        if pick is not None:
            answers[q.id] = "ABCD".index(pick[0])
    m["answers"] = answers
    m["result"] = mx.grade(qs, answers)
    m["left"] = max(0, int(m["deadline"] - time.time()))
    data = load_progress()
    data.setdefault("mock_history", []).append({
        "when": datetime.now().strftime("%Y-%m-%d %H:%M"), "scenarios": m["draw"]["scenarios"], "scaled": m["result"]["scaled"],
        "pct": round(m["result"]["pct"], 3), "by_domain": {str(d): list(v) for d, v in m["result"]["by_domain"].items()},
        "missed": m["result"]["missed"]})
    save_progress(data)


m = S.get("mock")

if m is None:
    st.markdown("Same shape as the exam: you cannot see answers until you submit, and the clock runs for "
                f"{mx.MINUTES} minutes. Questions come from the 734-item bank; each domain gets its weighted share.")
    st.markdown("| Domain | Name | Weight | Items |\n|---|---|---|---|\n" + "\n".join(
        f"| {d} | {DOMAINS[d][0]} | {DOMAINS[d][1]} | {n} |" for d, n in mx.quotas().items()))
    st.button("▶ Start the mock", type="primary", on_click=_start)
    hist = load_progress().get("mock_history", [])
    if hist:
        st.markdown("**Your earlier mocks**")
        st.markdown("| When | Scenarios | Estimated score | Percent |\n|---|---|---|---|\n" + "\n".join(
            f"| {h['when']} | {', '.join(map(str, h['scenarios']))} | {h['scaled']} | {h['pct']:.0%} |" for h in hist[-10:]))
    st.stop()

draw = m["draw"]
qs = [bank[i] for i in draw["ids"]]

if m["result"] is None and time.time() >= m["deadline"]:
    _finish(m)
    st.warning("Time is up: the mock was submitted with the answers you had picked.")

if m["result"] is None:
    st.markdown("**Scenarios in this mock:** " + " · ".join(f"{s} {SCENARIO_NAME[s]}" for s in draw["scenarios"]))
    if draw["short"]:
        st.warning("These scenarios did not hold enough questions for every domain, so some were taken from other scenarios: "
                   + ", ".join(f"domain {d} (+{n})" for d, n in draw["short"].items()))

    @st.fragment(run_every="1s")
    def _clock():
        left = int(m["deadline"] - time.time())
        if left <= 0:
            st.rerun()
        st.metric("Time left", f"{left // 60:02d}:{left % 60:02d}")
        st.progress(min(1.0, max(0.0, left / (mx.MINUTES * 60))))

    _clock()
    answered = sum(1 for q in qs if S.get(f"mock{m['run']}_{q.id}") is not None)
    st.markdown(f"**Answered {answered} / {len(qs)}**")
    for n, q in enumerate(qs, 1):
        with st.container(border=True):
            s = q.scenarios[0]
            st.markdown(f"**Question {n}** · 📋 Scenario {s}: {SCENARIO_NAME[s]}")
            st.markdown(esc(q.q))
            st.radio("Your answer", [f"{'ABCD'[i]})  {esc(o)}" for i, o in enumerate(q.opts)], index=None,
                     key=f"mock{m['run']}_{q.id}", label_visibility="collapsed")
    if st.button("Submit the mock", type="primary"):
        _finish(m)
        st.rerun()
    st.stop()

r = m["result"]
st.subheader("Result")
c1, c2, c3 = st.columns(3)
c1.metric("Correct", f"{r['correct']} / {r['total']}")
c2.metric("Estimated scaled score", r["scaled"], delta=f"{r['scaled'] - mx.PASS_SCALED:+d} vs the 720 pass mark")
c3.metric("Time used", f"{(mx.MINUTES * 60 - m['left']) // 60} min")
st.caption(mx.SCALE_NOTE)
st.markdown("| Domain | Name | Correct | Percent | Readiness gate (80%) |\n|---|---|---|---|---|\n" + "\n".join(
    f"| {d} | {DOMAINS[d][0]} | {c} / {t} | {(c / t if t else 0):.0%} | {'✅' if t and c / t >= 0.8 else '❌'} |"
    for d, (c, t) in r["by_domain"].items()))
st.button("Take another mock", on_click=_start)

st.subheader("Review")
only_missed = st.toggle("Show only the questions I missed", value=True)
for n, q in enumerate(qs, 1):
    if only_missed and q.id not in r["missed"]:
        continue
    got = m["answers"].get(q.id)
    with st.container(border=True):
        st.markdown(f"**Question {n}** · {q.id} · {'✅' if q.id not in r['missed'] else '❌'}")
        st.markdown(esc(q.q))
        for i, o in enumerate(q.opts):
            mark = "✅" if i == q.ans else ("❌" if i == got else "▫️")
            st.markdown(f"{mark} {'ABCD'[i]}) {esc(o)}")
        if got is None:
            st.caption("Not answered.")
        st.info(esc(q.explain))
