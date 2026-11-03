"""07b · Error Log + readiness gates — why each mock question was missed, and the four gates from CLAUDE.md."""

from datetime import datetime

import streamlit as st

from utils.course_map import DOMAINS
from utils.guide_index import SCENARIO_NAME
from utils.mcq_page import esc
from utils import mock_exam as mx
from utils.progress import load_progress, save_progress

st.set_page_config(page_title="Error Log", page_icon="📓", layout="wide")
st.title("📓 Error Log + readiness gates")
st.caption("Log why you missed each mock question, then see whether you meet the four readiness gates. Saved in the gitignored "
           "progress.json: on the hosted copy it resets when the app restarts.")

REASONS = ["misread the qualifier", "two looked right", "didn't know", "second-guessed", "rushed"]
MISREAD = REASONS[0]
CAPSTONES = [f"{n} {SCENARIO_NAME[n]}" for n in (2, 5, 6, 1, 3, 4)]      # 06a to 06f, in the capstone protocol's order

data = load_progress()
hist = data.get("mock_history", [])
log = data.setdefault("error_log", {})
gates = data.setdefault("gates", {"capstones": [], "practice": 0})
bank = {q.id: q for q in mx.all_questions()}

# ---- gates -------------------------------------------------------------------------------------------------------------
tot = {d: [0, 0] for d in DOMAINS}
for h in hist:
    for d, (c, t) in h["by_domain"].items():
        tot[int(d)][0] += c
        tot[int(d)][1] += t
dom_ok = all(t[1] >= 5 and t[0] / t[1] >= 0.8 for t in tot.values())

last_two = hist[-2:]
misread_in = [any(log.get(f"{h['when']}|{i}", {}).get("reason") == MISREAD for i in h["missed"]) for h in last_two]
repeat_misread = len(last_two) == 2 and all(misread_in)

st.subheader("Readiness gates")
st.markdown(
    "| # | Gate | Status |\n|---|---|---|\n"
    f"| 1 | Every domain at 80% or more, at least 5 answered per domain, across your mocks | {'✅' if dom_ok else '❌'} |\n"
    f"| 2 | All six capstones done | {'✅' if len(gates['capstones']) == 6 else '❌'} {len(gates['capstones'])} / 6 |\n"
    f"| 3 | Official practice exam at 900 or more (a floor: candidates report real scores 40 to 190 points lower; "
    f"community claim, verify) | {'✅' if gates['practice'] >= 900 else '❌'} {gates['practice'] or 'not entered'} |\n"
    f"| 4 | No repeated \"misread the qualifier\" error in the last two mocks | "
    f"{'❌ repeated' if repeat_misread else ('✅' if len(last_two) == 2 else '⏳ needs two mocks')} |")

st.markdown("**Per domain across all mocks**")
st.markdown("| Domain | Name | Correct | Percent |\n|---|---|---|---|\n" + "\n".join(
    f"| {d} | {DOMAINS[d][0]} | {c} / {t} | {(f'{c / t:.0%}' if t else '—')} |" for d, (c, t) in tot.items()))

with st.expander("Update gates 2 and 3 (entered by you; the app cannot grade them)"):
    caps = st.multiselect("Capstones finished", CAPSTONES, default=[c for c in gates["capstones"] if c in CAPSTONES])
    prac = st.number_input("Official practice exam score (0 if not taken)", 0, 1000, int(gates["practice"]), step=10)
    if st.button("Save gates"):
        gates["capstones"], gates["practice"] = caps, int(prac)
        save_progress(data)
        st.rerun()

# ---- the log -----------------------------------------------------------------------------------------------------------
st.subheader("Log your misses")
if not hist:
    st.info("No mocks yet. Take one on the Timed Mock page; its missed questions appear here.")
    st.stop()

labels = [f"{h['when']} · {h['scaled']} · {len(h['missed'])} missed" for h in hist]
pick = st.selectbox("Mock", range(len(hist)), index=len(hist) - 1, format_func=lambda i: labels[i])
h = hist[pick]
unlogged = [i for i in h["missed"] if f"{h['when']}|{i}" not in log]
st.markdown(f"**{len(h['missed']) - len(unlogged)} of {len(h['missed'])} logged**")

for qid in h["missed"]:
    q, key = bank.get(qid), f"{h['when']}|{qid}"
    if q is None:
        st.caption(f"{qid}: no longer in the bank.")
        continue
    with st.container(border=True):
        st.markdown(f"**{qid}** · 📋 Scenario {q.scenarios[0]}: {SCENARIO_NAME[q.scenarios[0]]}")
        st.markdown(esc(q.q))
        st.markdown(f"Best answer: **{'ABCD'[q.ans]}**) {esc(q.opts[q.ans])}")
        st.info(esc(q.explain))
        cur = log.get(key, {}).get("reason")
        reason = st.radio("Why did you miss it?", REASONS, index=REASONS.index(cur) if cur in REASONS else None,
                          horizontal=True, key=f"why_{key}")
        if reason and reason != cur:
            log[key] = {"reason": reason, "logged": datetime.now().strftime("%Y-%m-%d %H:%M")}
            save_progress(data)
            st.rerun()          # the gates above were drawn before this choice, so draw again

# ---- patterns ----------------------------------------------------------------------------------------------------------
mine = [v["reason"] for v in log.values()]
if mine:
    st.subheader("Patterns")
    st.markdown("| Reason | Count |\n|---|---|\n" + "\n".join(f"| {r} | {mine.count(r)} |" for r in REASONS))
