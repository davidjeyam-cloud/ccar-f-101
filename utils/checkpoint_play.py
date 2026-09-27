"""
Playground engine for D3.4 Checkpoints & Session Management, on the SIMULATED session in utils/checkpoint_lab.py. In the rewind
tabs the message box is the prompt number to rewind to; in the context tab it's the focus you give the summary / compact.
"""

from __future__ import annotations

import contextlib
import io
import re
from dataclasses import dataclass

from utils import checkpoint_lab as cl
from utils import lab_trace


@dataclass
class CheckpointConfig:
    mode: str = "rewind"
    rw_action: str = "code"                      # code | conversation | code_and_conversation
    git_too: str = "yes"
    ctx_action: str = "summarize_from_here"      # summarize_from_here | summarize_up_to_here | compact | clear
    alt_action: str = "branch"                   # branch | rewind
    resume_first: str = "yes"


def run_checkpoint(message: str, cfg: CheckpointConfig) -> dict:
    lab_trace.reset()
    sc = {"rewind": "bad_edit", "bash": "bash_rm", "context": "context_full", "branch": "try_alternative", "resume": "undo_yesterday"}[cfg.mode]
    cl.configure(sc)
    s = dict(cl.SITUATION)
    num = re.search(r"\d+", message or "")
    to = int(num.group(0)) if num and cfg.mode in ("rewind", "bash", "resume") else s["bad_prompt"]

    def recover(_s):
        api = cl.session
        if cfg.mode == "rewind":
            api.rewind(to, cfg.rw_action)
        elif cfg.mode == "bash":
            api.rewind(to, "code")
            if cfg.git_too == "yes":
                api.git_restore("config.json")
        elif cfg.mode == "context":
            if cfg.ctx_action == "compact":
                api.compact(message.strip())
            elif cfg.ctx_action == "clear":
                api.clear()
            else:
                api.rewind(2, cfg.ctx_action)
        elif cfg.mode == "branch":
            if cfg.alt_action == "branch":
                api.branch()
            else:
                api.rewind(2, "code_and_conversation")
        else:
            if cfg.resume_first == "yes":
                api.resume("cart-pence")
            api.rewind(to, "code")

    with contextlib.redirect_stdout(io.StringIO()):
        cl.run(recover)
    r = [e for e in lab_trace.EVENTS if e["kind"] == "checkpoint_run"][-1]
    from utils.concepts_content.checkpoints import _diagnose
    ok, _bug, _t = _diagnose({"scenario": sc, "raised": None, "run": r})
    files = r["files"]
    lines = [f"Situation: {s['problem']}"] + r["log"] + [
        f"Files: cart.py {'restored' if files.get('src/cart.py') == cl.GIT['src/cart.py'] else 'still changed'} · tax.py "
        f"{'restored' if files.get('src/tax.py') == cl.GIT['src/tax.py'] else 'still changed'} · config.json "
        f"{'present' if 'config.json' in files else 'MISSING'}",
        f"Session '{r['session']}' · prompts left: {r['prompts']} · context {r['tokens']:,} tokens · task brief kept: {r['instructions_kept']}"]
    notes = [] if ok else [{"rewind": "The code (or the conversation you wanted) didn't come back.",
                            "bash": "config.json was deleted by Bash — checkpoints can't bring it back; git can.",
                            "context": "The context was freed, but the task brief was lost (or the context is still full).",
                            "branch": "Approach A is gone — rewinding replaced it instead of branching.",
                            "resume": "Nothing to rewind here — yesterday's checkpoints live in yesterday's session."}[cfg.mode]]
    return {"lines": lines, "notes": notes, "ok": ok}
