"""
SIMULATED Claude Code session for D3.2 Plan Mode (guide TS 3.4): you write the policy — plan mode or direct execution, whether
to send verbose discovery to the Explore subagent, and what to do once a plan is approved — and the lab runs tasks taken from
the guide's own examples.

Documented behaviour it follows (code.claude.com/docs/en/permission-modes § plan mode; sub-agents § built-in subagents —
fetched 2026-09-28): in plan mode Claude reads and explores but does not edit source until the plan is approved; approving
switches to an executing mode (auto / accept edits / manual approval) — "keep planning" stays in plan mode; Explore is a
read-only subagent that keeps exploration output out of the main conversation's context.
INVENTED (simulation): the tasks' numbers, the minutes, the token counts, the 200k simulated context window, the "first
approach turns out wrong after N files" behaviour of direct execution on tasks with several valid approaches.
"""

from __future__ import annotations

from utils import lab_trace

SCENARIO_IDS = ("library_migration", "single_bug", "choose_integration", "big_discovery")
SCENARIO = "library_migration"
CONTEXT_WINDOW = 200_000
TOKENS_PER_FILE = 900
SUMMARY_TOKENS = 2_500
PLAN_OVERHEAD_MIN = 8

TASKS = {
    "library_migration": {"name": "Migrate from the old HTTP library to the new one", "files": 45, "approaches": 2,
                          "architectural": True, "clear_fix": False, "discovery_files": 45},
    "single_bug": {"name": "Fix a null check in orders.py (stack trace points to line 88)", "files": 1, "approaches": 1,
                   "architectural": False, "clear_fix": True, "discovery_files": 1},
    "choose_integration": {"name": "Add payments: hosted checkout page vs embedded card form", "files": 2, "approaches": 2,
                           "architectural": True, "clear_fix": False, "discovery_files": 6},
    "big_discovery": {"name": "Find every place the old auth token is read, then replace it", "files": 12, "approaches": 1,
                      "architectural": False, "clear_fix": False, "discovery_files": 300},
}


def configure(scenario_id: str) -> None:
    global SCENARIO
    SCENARIO = scenario_id if scenario_id in TASKS else "library_migration"


def current_task() -> dict:
    return dict(TASKS[SCENARIO])


def run_session(choose_mode, use_explore=None, after_approval=None) -> dict:
    """Run the scenario's task with your policy on the SIMULATED session."""
    task = current_task()
    mode = choose_mode(dict(task))
    explore = bool(use_explore(dict(task))) if use_explore else False
    log, minutes, rework, done, context = [], 0, 0, False, 20_000
    log.append(f"task: {task['name']} · {task['files']} file(s) · {task['approaches']} valid approach(es)"
               f"{' · architectural' if task['architectural'] else ''}")
    log.append(f"mode: {mode}{' · discovery via the Explore subagent' if explore else ''}")

    # discovery
    disc_tokens = task["discovery_files"] * TOKENS_PER_FILE
    if explore:
        context += SUMMARY_TOKENS
        log.append(f"Explore read {task['discovery_files']} files in its own context → a {SUMMARY_TOKENS:,}-token summary came back")
    else:
        context += disc_tokens
        log.append(f"discovery in the main conversation: {task['discovery_files']} files → +{disc_tokens:,} tokens")
    minutes += max(1, task["discovery_files"] // 20)

    if mode == "plan":
        minutes += PLAN_OVERHEAD_MIN
        log.append("plan mode: read-only exploration, compared the approaches, wrote a plan (no edits yet)")
        nxt = after_approval(dict(task)) if after_approval else "acceptEdits"
        log.append(f"at the approval prompt → {nxt}")
        if nxt in ("keep_planning", "plan"):
            log.append("still in plan mode — edits stay blocked, nothing was changed")
        else:
            minutes += task["files"]
            done = True
            log.append(f"executed the planned approach across {task['files']} file(s)")
    else:
        if task["approaches"] > 1 or task["architectural"]:
            wasted = max(1, task["files"] * 2 // 3)
            rework += wasted
            minutes += wasted * 2 + task["files"]
            log.append(f"direct: started on the first approach; after {wasted} file(s) it turned out wrong "
                       f"(the other approach fits the infrastructure) → reverted {wasted}, redid the work")
        else:
            minutes += task["files"] * 2
            log.append(f"direct: made the change in {task['files']} file(s)")
        done = True
    exhausted = context > CONTEXT_WINDOW
    if exhausted:
        log.append(f"main context {context:,} tokens > {CONTEXT_WINDOW:,} window → exhausted; earlier decisions were lost")
    rec = {"kind": "plan_session", "scenario": SCENARIO, "task": task, "mode": mode, "explore": explore, "minutes": minutes,
           "rework_files": rework, "done": done and not exhausted, "context": context, "exhausted": exhausted, "log": log}
    lab_trace.record(rec)
    print("\n".join(log))
    print(f"result: {'DONE' if rec['done'] else 'NOT DONE'} · {minutes} simulated min · reworked files: {rework} · "
          f"main context: {context:,} tokens")
    return rec
