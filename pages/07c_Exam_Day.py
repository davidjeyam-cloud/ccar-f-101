"""07c · Exam Day — registration, ID, policies and rules of conduct, paraphrased from the official guide (sections 11-14)."""

import streamlit as st

from utils.progress import load_progress, save_progress

st.set_page_config(page_title="Exam Day", page_icon="🗓️", layout="wide")
st.title("🗓️ Exam Day")
st.caption("Everything here is paraphrased from the official exam guide v1.0 (sections 11 to 14, PDF pp.33-35). Policies can change: "
           "re-read the current guide and the Pearson VUE pages before you book. Not legal or policy advice.")

st.subheader("Before the day")
st.markdown(
    "| # | What | Guide says | Where |\n|---|---|---|---|\n"
    "| 1 | Register | Via the Anthropic Partner Academy; read the exam guide, the Certification Terms and Conditions and the "
    "Certification Exam Policy first | §11 · p.33 |\n"
    "| 2 | Fee | $125 USD; the checkout price reflects any discount for your partner tier | §3 · p.2 and §11 · p.33 |\n"
    "| 3 | Schedule | Create a Pearson VUE account, then pick a date and either online proctoring or a Pearson test center | §11 · p.33 |\n"
    "| 4 | Cancel or move | Allowed up to 24 hours before the appointment; later changes forfeit the fee | §11 · p.33 |\n"
    "| 5 | ID | Valid, unexpired, government-issued photo ID; the name must match your registration exactly | §12 · p.34 |\n"
    "| 6 | Name wrong? | Contact certifications-support@anthropic.com before you schedule | §12 · p.34 |\n"
    "| 7 | Accommodations | Must be approved by Pearson VUE before you schedule; do not book until approved | §12 · p.34 |\n"
    "| 8 | No-show or late | Forfeits the fee and you must re-register. The guide does not state the late-arrival window | §12 · p.34 |")

st.subheader("During the exam")
st.markdown(
    "| # | Rule | Where |\n|---|---|---|\n"
    "| 1 | Online: stay in view of the proctor and the webcam for the whole session | §13 · p.35 |\n"
    "| 2 | Keep the workspace clear of notes, books, phones, second monitors and other materials | §13 · p.35 |\n"
    "| 3 | No communicating with anyone else | §13 · p.35 |\n"
    "| 4 | Never capture, copy, photograph or reproduce any exam content | §13 · p.35 |\n"
    "| 5 | Prohibited: phones, smart watches, headphones, study materials, any recording device. Permitted items, such as "
    "proctor-provided scratch paper, are set by Pearson VUE | §13 · p.35 |\n"
    "| 6 | You accept a confidentiality agreement before starting; if you decline, the session ends with no refund | §14 · p.35 |\n"
    "| 7 | Misconduct can mean an invalidated result, a revoked credential and a ban from future exams | §13 · p.35 |")

st.subheader("The exam itself")
st.markdown(
    "| # | Item | Value | Where |\n|---|---|---|---|\n"
    "| 1 | Items | 60, multiple-choice and multiple-response; each item says how many answers to select | §3 · p.2 |\n"
    "| 2 | Structure | 4 scenarios drawn from a bank of 6 | §3 · p.2 |\n"
    "| 3 | Time | 120 minutes, about 2 minutes per item | §3 · p.2 |\n"
    "| 4 | Pass | Scaled 720 on 100 to 1,000 | §3 · p.2 |\n"
    "| 5 | Report | Pass or fail, scaled score, percent correct by domain | §3 · p.2 |")
st.warning("The real exam has multiple-response items. The question bank and the Timed Mock here are single-answer only, so "
           "practise reading each stem for how many answers it asks for.")

st.subheader("After the exam")
st.markdown(
    "| # | Topic | Guide says | Where |\n|---|---|---|---|\n"
    "| 1 | Retake waits | 14 days after the first fail, 30 after the second, 90 after the third | §12 · p.34 |\n"
    "| 2 | Retake limit | Up to four attempts in a rolling twelve months, per exam; the fee applies each time | §12 · p.34 |\n"
    "| 3 | Validity | 12 months from the award date | §15 · p.35 |\n"
    "| 4 | Renewal | On time: review what changed and pass a free, non-proctored assessment on the Partner Academy; "
    "lapsed: retake the full exam at the full fee | §15 · pp.35-36 |\n"
    "| 5 | Appeals | Within 14 days of being notified, or of the exam date for a result concern, through Pearson VUE support | §16 · p.36 |")

st.subheader("Your checklist")
CHECKS = ["Read the guide, Terms and Conditions and Exam Policy", "Name on my ID matches my registration exactly",
          "Accommodations (if any) approved before booking", "Booked, and I know the cancel-by time (24 hours before)",
          "Testing space cleared; phone, watch and headphones out of reach", "Passed a timed mock at or above the 720 estimate",
          "All four readiness gates are green on the Error Log page"]
data = load_progress()
done = data.setdefault("examday_checks", [])
for c in CHECKS:
    if st.checkbox(c, value=c in done, key=f"ed_{c}") != (c in done):
        done.remove(c) if c in done else done.append(c)
        save_progress(data)
        st.rerun()
st.caption("Contacts per the guide: name corrections to certifications-support@anthropic.com; everything else to Pearson VUE "
           "support (pearsonvue.com/us/en/anthropic.html).")
