"""
Playground engine for D3.2 Plan Mode, on the SIMULATED session in utils/plan_lab.py. The message box can describe your own task
("rename a field in 30 files", "two ways to add caching", "fix the crash in cart.py, stack trace line 12"); the engine reads
simple cues from it (file counts, 'two/several approaches', 'architecture', 'stack trace') — a simulation shortcut, stated so.
"""

from __future__ import annotations

import contextlib
import io
import re
from dataclasses import dataclass

from utils import lab_trace
from utils import plan_lab as pl


@dataclass
class PlanConfig:
    mode: str = "decide"
    task_pick: str = "library_migration"
    mode_pick: str = "plan"
    discovery: str = "300"
    use_explore: str = "yes"
    approval: str = "acceptEdits"


def _task_from(message: str, fallback: str) -> tuple[dict, str]:
    m = message.strip().lower()
    base = dict(pl.TASKS[fallback])
    if not m or m == base["name"].lower() or m.startswith("use the task selected") or m in ("go", "run"):
        return base, "preset"
    n = re.search(r"(\d+)\s*(?:\+\s*)?files?", m)
    task = {"name": message.strip(), "files": int(n.group(1)) if n else (1 if "stack trace" in m or "one file" in m else 3),
            "approaches": 2 if re.search(r"\b(two|2|several|multiple)\b[^.]*\b(ways|approaches|options)\b|\bvs\b|\bor\b", m) else 1,
            "architectural": bool(re.search(r"architect|restructur|migrat|microservice|infrastructure", m)),
            "clear_fix": "stack trace" in m, "discovery_files": int(n.group(1)) if n else 5}
    return task, "read from your message (simulation cues: file count, 'two ways / vs', 'architecture / migration', 'stack trace')"


def run_plan(message: str, cfg: PlanConfig) -> dict:
    lab_trace.reset()
    pl.configure(cfg.task_pick if cfg.mode == "decide" else "big_discovery" if cfg.mode == "explore" else "library_migration")
    task, how = _task_from(message, pl.SCENARIO) if cfg.mode == "decide" else (dict(pl.TASKS[pl.SCENARIO]), "preset")
    if cfg.mode == "explore":
        task["discovery_files"] = int(cfg.discovery)
    saved = pl.TASKS[pl.SCENARIO]
    pl.TASKS[pl.SCENARIO] = task
    try:
        mode_choice = cfg.mode_pick if cfg.mode == "decide" else "plan"
        with contextlib.redirect_stdout(io.StringIO()):
            rec = pl.run_session(lambda t: mode_choice, (lambda t: cfg.use_explore == "yes") if cfg.mode == "explore" else (lambda t: False),
                                 (lambda t: cfg.approval) if cfg.mode == "approve" else (lambda t: "acceptEdits"))
    finally:
        pl.TASKS[pl.SCENARIO] = saved
    lines = [f"Task ({how}): {task['name']} — {task['files']} file(s), {task['approaches']} approach(es)"
             f"{', architectural' if task['architectural'] else ''}"] + rec["log"][1:]
    lines.append(f"Result: {'DONE' if rec['done'] else 'NOT DONE'} · {rec['minutes']} simulated min · reworked files: "
                 f"{rec['rework_files']} · main context {rec['context']:,} / {pl.CONTEXT_WINDOW:,}")
    notes = []
    needs_plan = task["files"] > 3 or task["approaches"] > 1 or task["architectural"]
    if cfg.mode == "decide":
        if rec["mode"] == "direct" and needs_plan:
            notes.append(f"Direct execution on a task that needed design — {rec['rework_files']} file(s) of rework.")
        if rec["mode"] == "plan" and not needs_plan:
            notes.append("Plan mode for a small, clear change — the planning step only added time.")
    if rec["exhausted"]:
        notes.append("The main context overflowed with discovery output.")
    if cfg.mode == "approve" and not rec["done"]:
        notes.append("The plan was approved but never executed — edits stay blocked in plan mode.")
    return {"lines": lines, "notes": notes, "ok": not notes}
