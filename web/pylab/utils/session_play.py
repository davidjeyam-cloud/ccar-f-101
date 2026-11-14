"""
Playground engine for D1.4 Session State & Persistence: one run per message, driven by the tab's knobs, on top of
the SIMULATED session layer in utils/session_lab.py (see its docstring for what is documented vs invented).
"""

from __future__ import annotations

from dataclasses import dataclass

from utils import lab_trace
from utils import session_lab as sl


@dataclass
class SessionConfig:
    mode: str = "return"            # return | changes | fork | degrade | manifest
    how: str = "resume_name"        # return tab: resume_name | continue | fresh_nosummary
    changed: str = "one"            # changes tab: none | one | most
    approach: str = "resume_tell"   # changes tab: resume_tell | resume_silent | fresh_summary | fresh_nosummary
    fork: str = "yes"               # fork tab
    explored: int = 12              # degrade tab: files read in the long exploration session
    compact: str = "no"             # degrade tab: run /compact before asking
    scratchpad: str = "no"          # degrade tab: the agent keeps and consults a scratchpad of key findings
    manifest: str = "yes"           # manifest tab: agents exported their state before the crash


def _ask(q: str) -> str:
    return q if ("limit" in q.lower() or "refund" in q.lower()) else q + " (and what is the current refund limit?)"


def _return(q, cfg):
    sl.configure("next_day_unchanged")
    lines = ["Sessions on disk: refund-investigation (yesterday's analysis, 6 files read) · docs-typo (later, "
             "unrelated — the MOST RECENT one)."]
    if cfg.how == "resume_name":
        r = sl.query(q, resume=sl.BASELINE)
        lines.append("claude --resume refund-investigation → the named session, with its full history restored.")
    elif cfg.how == "continue":
        r = sl.query(q, continue_conversation=True)
        lines.append("claude --continue → reopens the MOST RECENT conversation in this directory.")
    else:
        r = sl.query(q, name="new")
        lines.append("A new session with no summary → the agent starts from nothing.")
    ok = r.session_name == sl.BASELINE and r.reads == 0 and r.value == sl.TRUTH["value"]
    return {"lines": lines, "answer": r.text, "ok": ok,
            "why": (f"Started a new session and read {r.reads} file(s) again." if cfg.how == "fresh_nosummary"
                    else f"Continued '{r.session_name}' and read {r.reads} file(s)."),
            "metrics": {"session used": r.session_name, "file reads": r.reads, "context tokens": r.context_tokens}}


def _changes(q, cfg):
    sl.configure({"none": "next_day_unchanged", "one": "one_file_changed", "most": "major_refactor"}[cfg.changed])
    moves = {k: v for k, v in sl.CHANGES.items() if k != v}
    lines = [f"Changed since the analysis: {list(sl.CHANGES) or 'nothing'}" + (f" · moved: {moves}" if moves else "")]
    if cfg.approach == "resume_tell":
        r = sl.query(f"Since your analysis these files changed: {list(sl.CHANGES)}. Re-read only those.\n{q}",
                     resume=sl.BASELINE)
        lines.append("Resumed refund-investigation and named the changed files.")
    elif cfg.approach == "resume_silent":
        r = sl.query(q, resume=sl.BASELINE)
        lines.append("Resumed refund-investigation WITHOUT saying what changed.")
    elif cfg.approach == "fresh_summary":
        r = sl.query(f"Key findings so far:\n{sl.SCRATCHPAD}\nFiles changed since then (old -> new): {sl.CHANGES}\n\n{q}",
                     name="v2")
        lines.append("New session, seeded with the structured summary (the scratchpad notes) + the change list.")
    else:
        r = sl.query(q, name="v2")
        lines.append("New session with NO summary.")
    truth = sl.TRUTH
    ok = r.value == truth["value"] and r.path == truth["path"] and not r.degraded and r.reads <= 2
    if r.value is not None and r.value != truth["value"]:
        why = "Stale: it answered from a tool result read before the change."
    elif r.degraded:
        why = "Context degraded: the old results plus all the re-reads piled up past the simulated threshold."
    elif r.reads > 2:
        why = f"Correct, but by full re-exploration: {r.reads} file reads."
    else:
        why = f"Correct with {r.reads} targeted read(s)."
    return {"lines": lines, "answer": r.text, "ok": ok, "why": why,
            "metrics": {"truth": f"{truth['value']} in {truth['path']}", "file reads": r.reads,
                        "context tokens": r.context_tokens}}


def _fork(message, cfg):
    sl.configure("compare_approaches")
    b_prompt = (message.strip() if "approach" in message.lower()
                else "Plan approach B: " + (message.strip() or "move the limit into the config service."))
    kw = {"resume": sl.BASELINE, "fork_session": cfg.fork == "yes"}
    sl.query("Plan approach A: raise the limit behind a feature flag.", **kw)
    b = sl.query(b_prompt, **kw)
    lines = []
    for sid, s in sl.SESSIONS.items():
        prompts = [e["text"][:55] for e in s["history"] if e["type"] == "prompt"]
        origin = f" (forked from {sl.SESSIONS[s['forked_from']]['name']})" if s.get("forked_from") else ""
        lines.append(f"`{sid}` **{s['name']}**{origin}: {len(s['history'])} entries · prompts {prompts}")
    base_len = len(sl.SESSIONS[sl._resolve(sl.BASELINE)]["history"])
    ok = cfg.fork == "yes" and not b.extra.get("saw_other_approach") and base_len == sl.TRUTH["baseline_len"]
    why = ("Two independent branches; the baseline still holds only its Day-1 history." if ok else
           "Both approaches went into the ONE baseline session: approach B carries approach A, and the baseline is no "
           "longer a clean shared starting point.")
    return {"lines": lines, "answer": b.text, "ok": ok, "why": why,
            "metrics": {"baseline entries (Day 1 = 8)": base_len, "B saw A": b.extra.get("saw_other_approach", False)}}


def _degrade(q, cfg):
    base = 400 + cfg.explored * sl.FILE_TOKENS
    lines = [f"A long exploration session read {cfg.explored} files (≈{base} context tokens; simulated degradation "
             f"above {sl.DEGRADE_AT})."]
    ctx = base + len(q) // 4
    if cfg.compact == "yes":
        ctx = 500 + 5 * sl.FILE_TOKENS + len(q) // 4
        lines.append("/compact → the history is replaced by a summary (the docs: plus recent exchanges and a few "
                     "recently read files when resuming from a summary).")
    if cfg.scratchpad == "yes":
        lines.append("The agent kept notes/refund-findings.md while exploring and consults it for this question.")
    vague = ctx > sl.DEGRADE_AT and cfg.scratchpad != "yes"
    if vague:
        answer = "Refund limits are typically defined as a constant in a policy or config module, usually near the refund handler."
    else:
        answer = ("The auto-approve limit is 100, defined as AUTO_APPROVE_LIMIT in refund_policy.py"
                  + (" (from the scratchpad notes)." if cfg.scratchpad == "yes" and ctx > sl.DEGRADE_AT else "."))
    return {"lines": lines, "answer": answer, "ok": not vague,
            "why": "A vague 'typical pattern' answer — context degradation." if vague else "A specific answer.",
            "metrics": {"context tokens": ctx, "degraded": vague}}


def _manifest(cfg):
    sl.configure("crash_recovery")
    lines = ["Crash: test_files ✔ done · refund_flow ✔ done · auth_flow … in progress."]
    if cfg.manifest == "yes":
        m = sl.load_manifest()
        done = sum(1 for a in m["agents"].values() if a["status"] == "done")
        lines.append(f"The coordinator loads {sl.MANIFEST_PATH}, reuses {done} finished results, and re-runs auth_flow "
                     "with its saved state injected into the prompt.")
        sl.run_agent("auth_flow", f"Continue exploring auth_flow. Your saved state: {m['agents']['auth_flow']['partial']}")
        runs = 1
    else:
        lines.append("No manifest: nothing records what finished, so every agent starts again from scratch.")
        for area in ("test_files", "refund_flow", "auth_flow"):
            sl.run_agent(area, f"Explore {area}.")
        runs = 3
    return {"lines": lines, "answer": f"{runs} agent run(s) to recover; the report covers all 3 areas.", "ok": runs == 1,
            "why": ("Only the unfinished agent re-ran, from its saved state." if runs == 1
                    else "Finished work was redone because nothing recorded it."),
            "metrics": {"agent runs": runs}}


def run_play(message: str, cfg: SessionConfig) -> dict:
    lab_trace.reset()
    q = _ask(message.strip() or sl.QUESTION)
    return {"return": lambda: _return(q, cfg), "changes": lambda: _changes(q, cfg), "fork": lambda: _fork(message, cfg),
            "degrade": lambda: _degrade(q, cfg), "manifest": lambda: _manifest(cfg)}[cfg.mode]()
