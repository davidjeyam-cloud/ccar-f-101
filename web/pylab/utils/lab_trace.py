"""
Tiny shared event log for the CONCEPTS code lab.

The simulated model (utils/mock_claude.py) and the fake backend
(utils/tools.py) both append events here while a learner's edited code runs
inside the lab's separate Python process; utils/lab_harness.py dumps the log
as JSON when the run ends, and the Streamlit page turns it into the step
table and the highlighted flowchart. It only ever lives inside that
short-lived subprocess, so there is no cross-run state to clean up.
"""

# Separator between what the learner's code printed and the JSON trace that follows it.
TRACE_MARK = "<<<LAB_TRACE>>>"

EVENTS: list[dict] = []


def record(event: dict) -> None:
    EVENTS.append(event)


def reset() -> None:
    EVENTS.clear()
