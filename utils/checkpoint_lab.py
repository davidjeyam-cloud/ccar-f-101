"""
SIMULATED Claude Code session with checkpoints for D3.4 Checkpoints & Session Management.

Documented behaviour it follows (code.claude.com/docs/en/checkpointing, sessions — fetched 2026-09-28):
- every prompt you send that starts a turn creates a checkpoint of the code before it; checkpoints are saved with the
  conversation, so /rewind works after you resume that session (they belong to that session);
- /rewind (or Esc Esc) → restore code and conversation · restore conversation (keep current code) · restore code (keep the
  conversation) · summarize from here · summarize up to here;
- checkpoints track edits made by Claude's file-editing tools — NOT files changed by Bash (rm, mv, cp) or outside Claude Code;
- summarizing compresses context in the same session (like a targeted /compact) and doesn't change files; to try another
  approach while keeping the original intact, branch (/branch or --fork-session) instead of rewinding;
- checkpoints are not a replacement for version control (git).
INVENTED (simulation): the files, the prompts, the token counts and the "instructions kept?" bookkeeping.
"""

from __future__ import annotations

import copy

from utils import lab_trace

SCENARIO_IDS = ("bad_edit", "bash_rm", "context_full", "try_alternative", "undo_yesterday")
SCENARIO = "bad_edit"
WINDOW = 200_000

_GIT = {"src/cart.py": "def total(items):\n    return sum(i.price for i in items)\n",
        "src/tax.py": "RATE = 0.2\n", "config.json": '{"currency": "GBP"}\n'}


class Session:
    def __init__(self, name, prompts, files, tokens=40_000):
        self.name, self.prompts, self.files, self.tokens = name, prompts, files, tokens
        self.instructions_kept, self.log, self.branches, self.alive = True, [], [], True

    # prompts: [{"n": 1, "text": ..., "before": {files snapshot}, "tool_edits": {...}, "bash": [...]}]
    def rewind(self, to_prompt: int, action: str = "code_and_conversation"):
        cp = next((p for p in self.prompts if p["n"] == to_prompt), None)
        if cp is None:
            self.log.append(f"/rewind: no checkpoint for prompt {to_prompt} in session '{self.name}'")
            return
        if action in ("code", "code_and_conversation"):
            restored = []
            for path, text in cp["before"].items():
                if any(path in p.get("tool_edits", {}) for p in self.prompts if p["n"] >= to_prompt):
                    self.files[path] = text
                    restored.append(path)
            bash_touched = sorted({f for p in self.prompts if p["n"] >= to_prompt for f in p.get("bash", [])})
            self.log.append(f"/rewind → restore {'code and conversation' if action != 'code' else 'code'} at prompt {to_prompt}: "
                            f"restored {restored or 'nothing'}" + (f" · NOT restored (changed by Bash): {bash_touched}" if bash_touched else ""))
        if action in ("conversation", "code_and_conversation"):
            self.prompts = [p for p in self.prompts if p["n"] < to_prompt]
            self.log.append(f"conversation rewound to before prompt {to_prompt}" + (" (code kept as is)" if action == "conversation" else ""))
        if action == "summarize_from_here":
            later = sum(p.get("tokens", 0) for p in self.prompts if p["n"] >= to_prompt)
            self.tokens -= int(later * 0.9)
            self.log.append(f"summarized from prompt {to_prompt}: ~{int(later * 0.9):,} tokens freed; earlier messages (your "
                            f"instructions) kept as they were")
        if action == "summarize_up_to_here":
            earlier = sum(p.get("tokens", 0) for p in self.prompts if p["n"] < to_prompt)
            self.tokens -= int(earlier * 0.9)
            self.instructions_kept = False
            self.log.append(f"summarized everything before prompt {to_prompt} — your opening instructions are now only a summary")

    def compact(self, focus: str = ""):
        self.tokens = int(self.tokens * 0.3)
        self.log.append(f"/compact{(' ' + focus) if focus else ''}: context → {self.tokens:,} tokens; key instructions kept in the summary")

    def clear(self):
        self.tokens, self.instructions_kept = 8_000, False
        self.log.append("/clear: fresh context — the task's instructions and findings are gone")

    def git_restore(self, path: str):
        self.files[path] = _GIT[path]
        self.log.append(f"git restore {path} → back to the committed version")

    def branch(self):
        b = Session(self.name + "-branch", copy.deepcopy(self.prompts), copy.deepcopy(self.files), self.tokens)
        self.branches.append(b)
        self.log.append(f"/branch → new session '{b.name}' with a copy of the history; '{self.name}' stays intact")
        return b


def _build(sc):
    files = copy.deepcopy(_GIT)
    if sc in ("bad_edit", "undo_yesterday"):
        before = copy.deepcopy(files)
        files["src/cart.py"] = "def total(items):\n    return sum(i.price for i in items) * 100  # BUG\n"
        files["src/tax.py"] = "RATE = 20  # BUG\n"
        prompts = [{"n": 1, "text": "Explain the cart module", "before": before, "tool_edits": {}, "tokens": 6_000},
                   {"n": 2, "text": "Add pence-based totals", "before": before,
                    "tool_edits": {"src/cart.py": 1, "src/tax.py": 1}, "tokens": 9_000}]
        return prompts, files, "Add pence-based totals broke cart.py and tax.py — undo Claude's edits, keep the discussion"
    if sc == "bash_rm":
        before = copy.deepcopy(files)
        files["src/cart.py"] = "def total(items):\n    return 0  # BUG\n"
        del files["config.json"]
        prompts = [{"n": 1, "text": "Tidy the project", "before": before, "tool_edits": {"src/cart.py": 1},
                    "bash": ["config.json"], "tokens": 7_000}]
        return prompts, files, "“Tidy the project” edited cart.py AND ran `rm config.json` — get both back"
    if sc == "context_full":
        prompts = [{"n": 1, "text": "Task brief: migrate billing; keep GBP; never touch tax.py", "before": copy.deepcopy(files),
                    "tool_edits": {}, "tokens": 4_000}] + [
                   {"n": i, "text": f"debugging step {i}", "before": copy.deepcopy(files), "tool_edits": {}, "tokens": 30_000}
                   for i in range(2, 8)]
        return prompts, files, "six debugging prompts filled the context (184k/200k); keep the task brief from prompt 1"
    if sc == "try_alternative":
        prompts = [{"n": 1, "text": "Analyse the test suite", "before": copy.deepcopy(files), "tool_edits": {}, "tokens": 20_000},
                   {"n": 2, "text": "Approach A: snapshot tests", "before": copy.deepcopy(files), "tool_edits": {"src/cart.py": 1},
                    "tokens": 15_000}]
        return prompts, files, "approach A (snapshot tests) is half done; you want to also try approach B from the same analysis"
    return [], files, "unknown"


SITUATION: dict = {}
_SESSIONS: dict = {}
current = None


def configure(scenario_id: str) -> None:
    global SCENARIO, current
    SCENARIO = scenario_id if scenario_id in SCENARIO_IDS else "bad_edit"
    prompts, files, problem = _build(SCENARIO)
    _SESSIONS.clear()
    if SCENARIO == "undo_yesterday":
        _SESSIONS["cart-pence"] = Session("cart-pence", prompts, files, 24_000)          # yesterday's named session
        current = Session("(new)", [], files, 8_000)                                     # today: a fresh terminal
        problem = "yesterday's session 'cart-pence' (prompt 2) broke cart.py and tax.py — today, undo those edits"
    else:
        current = Session("work", prompts, files, 40_000 if SCENARIO != "context_full" else 184_000)
    SITUATION.clear()
    SITUATION.update(problem=problem, scenario=SCENARIO, bad_prompt=2 if SCENARIO in ("bad_edit", "undo_yesterday") else 1,
                     after_instructions=2, session_name="cart-pence",
                     deleted_by_bash=["config.json"] if SCENARIO == "bash_rm" else [])


configure("bad_edit")


class _Api:
    """What your recover() calls — each maps to a documented Claude Code action."""

    def rewind(self, to_prompt, action="code_and_conversation"):
        current.rewind(to_prompt, action)

    def compact(self, focus=""):
        current.compact(focus)

    def clear(self):
        current.clear()

    def git_restore(self, path):
        current.git_restore(path)

    def branch(self):
        return current.branch()

    def resume(self, name):
        global current
        s = _SESSIONS.get(name)
        if s is None:
            current.log.append(f"claude --resume {name}: no such session")
            return
        s.log = current.log + [f"claude --resume {name} → back in yesterday's session, with its checkpoints"]
        current = s

    def new_session(self):
        global current
        current = Session("(new)", [], current.files, 8_000)
        current.log.append("started a new session (no history, no checkpoints)")


session = _Api()


def run(recover) -> None:
    start_branch_count = len(current.branches)
    recover(dict(SITUATION))
    s = current
    rec = {"kind": "checkpoint_run", "scenario": SCENARIO, "log": list(s.log), "files": dict(s.files),
           "prompts": [p["n"] for p in s.prompts], "tokens": s.tokens, "instructions_kept": s.instructions_kept,
           "branches": len(s.branches) - start_branch_count, "session": s.name}
    lab_trace.record(rec)
    print("situation:", SITUATION["problem"])
    print("\n".join(rec["log"]) or "(no action taken)")
    print(f"files now: cart.py {'OK' if s.files.get('src/cart.py') == _GIT['src/cart.py'] else 'CHANGED'} · tax.py "
          f"{'OK' if s.files.get('src/tax.py') == _GIT['src/tax.py'] else 'CHANGED'} · config.json "
          f"{'present' if 'config.json' in s.files else 'MISSING'} · context {s.tokens:,} tokens · session '{s.name}'")


GIT = _GIT
