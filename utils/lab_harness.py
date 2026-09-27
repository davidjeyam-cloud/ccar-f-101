"""
Runs ONE learner code file inside the code lab's separate Python process and
prints the event trace as JSON at the end. Started by utils/lab_runner.py —
not meant to be run by hand.

Contract with lab_runner: everything the learner's code prints comes first;
after a line containing TRACE_MARK comes one JSON object with the events, the
fake-backend ledger and whether the code raised.
"""

import json
import os
import runpy
import sys
import traceback

# This file lives in utils/, which contains modules named like stdlib ones
# (utils/trace.py vs the stdlib `trace`). Python puts the script's own folder
# first on sys.path, so remove it — only the repo root should be importable.
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:] = [p for p in sys.path if os.path.abspath(p or ".") != _HERE]
sys.path.insert(0, os.environ["LAB_REPO_ROOT"])

from utils import lab_trace, mock_claude, research_backend, session_lab, stop_lab, support_lab, tools  # noqa: E402
import importlib  # noqa: E402

# simulated lab modules that are configured by scenario id (each exposes SCENARIO_IDS and configure())
_SCENARIO_MODULES = ("handoff_lab", "memory_lab", "decomp_lab")


def main() -> None:
    code_path = sys.argv[1]
    scenario = mock_claude.SCENARIOS[os.environ.get("LAB_SCENARIO", "damaged_order")]
    tools.configure(scenario.backend_status)
    research_backend.configure(**(scenario.research or {}))
    stop_lab.configure(scenario.id)
    if scenario.id in session_lab.SCENARIO_IDS:
        session_lab.configure(scenario.id)
    if scenario.id in support_lab.SCENARIO_IDS:
        support_lab.configure(scenario.id)
    for name in _SCENARIO_MODULES:
        try:
            mod = importlib.import_module(f"utils.{name}")
        except ModuleNotFoundError:
            continue
        if scenario.id in mod.SCENARIO_IDS:
            mod.configure(scenario.id)
    lab_trace.reset()

    status = {"raised": None, "scenario": scenario.id}
    try:
        runpy.run_path(code_path, run_name="__main__")
    except SystemExit:
        pass
    except BaseException as exc:  # the learner's code may raise anything
        status["raised"] = f"{type(exc).__name__}: {exc}"
        traceback.print_exc(file=sys.stderr)

    sys.stdout.flush()
    print("\n" + lab_trace.TRACE_MARK)
    print(json.dumps({"events": lab_trace.EVENTS, "ledger": tools.LEDGER, "status": status},
                     default=str))


main()
