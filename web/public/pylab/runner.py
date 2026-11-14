"""Runs ONE learner lab program inside Pyodide (the browser). A faithful copy of utils/lab_harness.py's logic for a long-lived
interpreter: every run starts from freshly imported utils modules, so global state (counters, ledgers) never leaks between runs,
exactly as a new process would. Returns one JSON string: {"stdout", "stderr", "trace": {"events", "ledger", "status"}}.
The page enforces the 10-second limit by terminating the Web Worker this runs in."""
import contextlib
import importlib
import io
import json
import os
import re
import sys
import traceback


def _scenario_modules() -> list:
    src = open("/utils/lab_harness.py", encoding="utf-8").read()
    m = re.search(r"_SCENARIO_MODULES = \((.*?)\)", src, re.S)
    return re.findall(r'"([a-z_0-9]+)"', m.group(1)) if m else []


def _run_coroutine(coro):
    """Stand-in for asyncio.run in the browser. Pyodide cannot block on an event loop from this synchronous entry point, and the
    labs only use `async def` callbacks that finish without really waiting, so drive the coroutine to its end directly."""
    try:
        while True:
            yielded = coro.send(None)
            if yielded is not None:
                raise RuntimeError("this lab runs async callbacks without real waiting; a call that waits on a real timer or "
                                   "network is not available in the browser")
    except StopIteration as stop:
        return stop.value


def run(code: str, scenario: str) -> str:
    for name in [n for n in sys.modules if n == "utils" or n.startswith("utils.")]:
        del sys.modules[name]                       # a fresh "process" for every run
    importlib.invalidate_caches()
    if "/" not in sys.path:
        sys.path.insert(0, "/")
    os.environ["LAB_SCENARIO"] = scenario
    import asyncio
    asyncio.run = _run_coroutine

    from utils import lab_trace, mock_claude, research_backend, session_lab, stop_lab, support_lab, tools

    sc = mock_claude.SCENARIOS[scenario]
    tools.configure(sc.backend_status)
    research_backend.configure(**(sc.research or {}))
    stop_lab.configure(sc.id)
    if sc.id in session_lab.SCENARIO_IDS:
        session_lab.configure(sc.id)
    if sc.id in support_lab.SCENARIO_IDS:
        support_lab.configure(sc.id)
    for name in _scenario_modules():
        try:
            mod = importlib.import_module(f"utils.{name}")
        except ModuleNotFoundError:
            continue
        if sc.id in mod.SCENARIO_IDS:
            mod.configure(sc.id)
    lab_trace.reset()

    status = {"raised": None, "scenario": sc.id}
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            exec(compile(code, "lab_code.py", "exec"), {"__name__": "__main__"})
        except SystemExit:
            pass
        except BaseException as exc:                # the learner's code may raise anything
            status["raised"] = f"{type(exc).__name__}: {exc}"
            traceback.print_exc(file=err)
    return json.dumps({"stdout": out.getvalue().rstrip("\n"), "stderr": err.getvalue(),
                       "trace": {"events": lab_trace.EVENTS, "ledger": tools.LEDGER, "status": status}}, default=str)
