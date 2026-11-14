"""
SIMULATED session layer for the D1.4 Session State & Persistence labs: named sessions, resume, continue, fork,
a small fake codebase that changes between work sessions, context degradation, a scratchpad file and a crash-
recovery manifest. It mimics the SHAPE of the Agent SDK / Claude Code session controls so the lab code reads like
real code; nothing here calls a model.

Grounding — what is documented (fetched 2026-09-27):
- `claude --resume <name>` resumes a named session; `--continue` reopens the most recent conversation in the current
  directory; `--fork-session` / `/branch` copy the conversation into a NEW session and leave the original unchanged;
  a resumed session restores the full history including tool calls and results; `/compact` replaces history with a
  summary ........................................................ code.claude.com/docs/en/sessions
- Agent SDK: `resume=<session id>`, `fork_session=True`, `continue_conversation=True`; forks branch the conversation,
  not the filesystem; "don't rely on session resume" — capture results as application state and pass them into a fresh
  session's prompt ............................................... code.claude.com/docs/en/agent-sdk/sessions
- performance degrades as the context window fills ................ code.claude.com/docs/en/best-practices
- guide (the exam view): TS 1.7 (pp.8–9) resume / fork / inform about changed files / fresh start with a structured
  summary; TS 5.4 (pp.21–22) context degradation, scratchpad files, manifests for crash recovery, /compact.
What is INVENTED (simulation): the fake files and their token sizes, the degradation threshold, when the simulated
agent re-reads a file, and its wording. Real Claude is not this literal.
"""

from __future__ import annotations

import copy
import itertools
import re
from dataclasses import dataclass, field

from utils import lab_trace

FILE_TOKENS = 800        # simulated cost of one file read in the context window
DEGRADE_AT = 7000        # simulated: above this many context tokens the answers turn vague (guide TS 5.4 Knowledge 1)
BASELINE = "refund-investigation"
QUESTION = "What is the current auto-approve refund limit, and in which file is it defined?"

_DAY1 = {
    "refund_policy.py": "AUTO_APPROVE_LIMIT = 100   # refunds up to this amount are approved automatically",
    "orders.py": "def load_order(order_id): ...   # reads the orders table",
    "auth.py": "def verify_customer(email): ...   # returns a verified customer id",
    "ledger.py": "def post_refund(order_id, amount): ...   # writes the refund to the ledger",
    "notifications.py": "def send_confirmation(customer_id, text): ...",
    "tests/test_refund.py": "def test_refund_under_limit(): ...",
}

SCRATCHPAD = """# notes/refund-findings.md  (written during the Day-1 analysis)
- Goal: decide whether to raise the auto-approve refund limit.
- Refund limit: AUTO_APPROVE_LIMIT in refund_policy.py
- Refunds are written by ledger.py::post_refund; customers are verified by auth.py::verify_customer.
- Decision so far: keep customer verification before any refund."""

MANIFEST_PATH = "state/manifest.json"
_AREA_FINDINGS = {
    "test_files": "tests/test_refund.py covers refunds under the limit; nothing covers the limit boundary.",
    "refund_flow": "orders.load_order -> refund_policy.AUTO_APPROVE_LIMIT check -> ledger.post_refund.",
    "auth_flow": "auth.verify_customer is called before every refund; token refresh happens in auth.refresh().",
}

SCENARIO_IDS = ("next_day_unchanged", "one_file_changed", "major_refactor", "compare_approaches", "crash_recovery")

# ── state (reset per run) ──────────────────────────────────────────────────────
FILES: dict = {}
CHANGES: dict = {}          # old path -> current path, for files changed since the Day-1 analysis (like `git status`)
TASK = "continue"
ANALYZED_FILES = tuple(_DAY1)
SESSIONS: dict = {}
MANIFEST: dict | None = None
TRUTH: dict = {}
_SEQ = itertools.count(1)
_TICK = itertools.count(1)


class SessionNotFound(Exception):
    pass


@dataclass
class Result:
    session_id: str
    session_name: str
    text: str
    reads: int
    context_tokens: int
    degraded: bool = False
    value: int | None = None
    path: str | None = None
    extra: dict = field(default_factory=dict)

    def __repr__(self) -> str:
        return (f"Result(session={self.session_name!r}, reads={self.reads}, context_tokens={self.context_tokens}, "
                f"text={self.text!r})")


def _entry(kind, **kw) -> dict:
    tokens = kw.pop("tokens", None)
    if tokens is None:
        tokens = FILE_TOKENS if kind == "read" else max(20, len(kw.get("text", "")) // 4)
    return {"type": kind, "tokens": tokens, **kw}


def _new_session(name, history, forked_from=None) -> str:
    sid = f"sess_{next(_SEQ):03d}"
    SESSIONS[sid] = {"name": name, "history": history, "created": next(_TICK), "forked_from": forked_from}
    return sid


def configure(scenario_id: str) -> None:
    """Build Day 1 (the analysis session, then an unrelated session) and the scenario's Day-2 state."""
    global FILES, CHANGES, TASK, MANIFEST, _SEQ, _TICK
    _SEQ, _TICK = itertools.count(1), itertools.count(1)
    SESSIONS.clear()
    FILES = dict(_DAY1)
    day1 = [_entry("prompt", text="Investigate how refunds work in this codebase.")]
    day1 += [_entry("read", path=p, content=c) for p, c in _DAY1.items()]
    day1.append(_entry("answer", text="Findings: the refund limit is AUTO_APPROVE_LIMIT = 100 in refund_policy.py; ...",
                       tokens=400))
    _new_session(BASELINE, day1)
    _new_session("docs-typo", [_entry("prompt", text="Fix the typo in README.md"),
                               _entry("read", path="README.md", content="# Refund service"),
                               _entry("answer", text="Fixed the typo.")])     # the MOST RECENT session
    CHANGES, TASK, MANIFEST = {}, "continue", None
    if scenario_id == "one_file_changed":
        FILES["refund_policy.py"] = "AUTO_APPROVE_LIMIT = 50   # lowered after the fraud review"
        CHANGES = {"refund_policy.py": "refund_policy.py"}
    elif scenario_id == "major_refactor":
        del FILES["refund_policy.py"]
        FILES["policies/refunds.py"] = "AUTO_APPROVE_LIMIT = 75   # moved here in the policy refactor"
        for p in ("orders.py", "auth.py", "ledger.py", "notifications.py"):
            FILES[p] = FILES[p] + "   # refactored"
        CHANGES = {"refund_policy.py": "policies/refunds.py", "orders.py": "orders.py", "auth.py": "auth.py",
                   "ledger.py": "ledger.py", "notifications.py": "notifications.py"}
    elif scenario_id == "compare_approaches":
        TASK = "compare"
    elif scenario_id == "crash_recovery":
        TASK = "recover"
        MANIFEST = {"agents": {
            "test_files": {"status": "done", "findings": _AREA_FINDINGS["test_files"]},
            "refund_flow": {"status": "done", "findings": _AREA_FINDINGS["refund_flow"]},
            "auth_flow": {"status": "in_progress", "partial": "auth.py read; token refresh not traced yet"}}}
    path, value = _find_limit(FILES)
    TRUTH.clear()
    TRUTH.update({"scenario": scenario_id, "path": path, "value": value,
                  "baseline_len": len(SESSIONS[_resolve(BASELINE)]["history"])})


def _resolve(ref: str) -> str:
    if ref in SESSIONS:
        return ref
    hits = [sid for sid, s in SESSIONS.items() if s["name"] == ref]
    if len(hits) != 1:
        raise SessionNotFound(f"No conversation found with session name or id: {ref} (SIMULATED)")
    return hits[0]


def _find_limit(files: dict):
    for p, c in files.items():
        m = re.search(r"AUTO_APPROVE_LIMIT = (\d+)", c or "")
        if m:
            return p, int(m.group(1))
    return None, None


def _knowledge(history) -> dict:
    k = {}
    for e in history:
        if e["type"] == "read":
            k[e["path"]] = e["content"]
    return k


def _read(history, path) -> bool:
    if path not in FILES:
        history.append(_entry("read", path=path, content=None, tokens=40))
        return False
    history.append(_entry("read", path=path, content=FILES[path]))
    return True


def query(prompt: str, resume: str | None = None, fork_session: bool = False, continue_conversation: bool = False,
          name: str | None = None) -> Result:
    """Send one prompt. resume=<name or id> continues that session; fork_session=True copies it into a new one;
    continue_conversation=True picks the most recent session; none of them = a fresh session. SIMULATED."""
    base_id = None
    if continue_conversation:
        base_id = max(SESSIONS, key=lambda s: SESSIONS[s]["created"])
    elif resume:
        base_id = _resolve(resume)
    if base_id and not fork_session:
        sid = base_id
        SESSIONS[sid]["created"] = next(_TICK)
        history = SESSIONS[sid]["history"]
    else:
        history = copy.deepcopy(SESSIONS[base_id]["history"]) if base_id else []
        default = (SESSIONS[base_id]["name"] + "-branch") if base_id else "new-session"
        sid = _new_session(name or default, history, forked_from=base_id if fork_session else None)
    before = len(history)
    history.append(_entry("prompt", text=prompt))
    knew = _knowledge(history)
    reads = 0
    # a resumed agent that is TOLD which files changed re-reads exactly those it had read before
    told = [old for old in CHANGES if old in prompt]
    for old in told:
        if old in knew:
            history.append(_entry("read", path=CHANGES[old], content=FILES.get(CHANGES[old])))
            if CHANGES[old] != old:
                history.append(_entry("note", text=f"{old} no longer exists", tokens=10))
            reads += 1
    extra = {}
    low = prompt.lower()
    if "approach" in low:
        others = [e["text"] for e in history[:-1] if e["type"] == "prompt" and "approach" in e["text"].lower()]
        text = (f"Plan: {prompt.strip()[:70]} - built on the Day-1 analysis ({len(_knowledge(history))} files already read)."
                + (f" [ALSO CARRYING: {others[-1][:50]!r}]" if others else ""))
        value = path = None
        extra["saw_other_approach"] = bool(others)
    elif "limit" in low or "refund" in low:
        k = _knowledge(history)
        for old in told:                      # files the agent was told changed: trust only their fresh read
            if CHANGES[old] != old:
                k.pop(old, None)
        path, value = _find_limit(k)
        if path is None:
            m = re.search(r"Refund limit: AUTO_APPROVE_LIMIT in (\S+)", prompt)
            if m:                                  # a structured summary names the file: read just that one
                target = CHANGES.get(m.group(1), m.group(1)) if m.group(1) in prompt and m.group(1) in told else m.group(1)
                reads += 1
                if not _read(history, target):
                    for p in FILES:                # the summary's file is gone and nobody said where it went
                        reads += 1
                        _read(history, p)
            else:                                   # nothing to go on: explore the whole codebase again
                for p in FILES:
                    reads += 1
                    _read(history, p)
            path, value = _find_limit(_knowledge(history))
        ctx = sum(e["tokens"] for e in history)
        if ctx > DEGRADE_AT:
            text = ("Refund limits are typically defined as a constant in a policy or config module, usually near the "
                    "refund handler.")
            value = path = None
        else:
            text = f"The auto-approve limit is {value}, defined as AUTO_APPROVE_LIMIT in {path}."
    else:
        text, value, path = "Noted.", None, None
    history.append(_entry("answer", text=text))
    ctx = sum(e["tokens"] for e in history)
    r = Result(sid, SESSIONS[sid]["name"], text, reads, ctx, degraded=ctx > DEGRADE_AT and "typically" in text,
               value=value, path=path, extra=extra)
    lab_trace.record({
        "kind": "session_query", "session_id": sid, "session_name": r.session_name,
        "base": SESSIONS[base_id]["name"] if base_id else None, "forked": bool(base_id and fork_session),
        "continued": continue_conversation, "fresh": base_id is None, "reads": reads, "ctx": ctx,
        "degraded": r.degraded, "value": value, "path": path, "prompt_head": prompt[:160], "history_before": before,
        "told": told, "saw_other_approach": extra.get("saw_other_approach", False),
        "has_summary": "Refund limit: AUTO_APPROVE_LIMIT" in prompt})
    return r


def load_manifest() -> dict:
    """Read the state each agent exported before the crash (a known location)."""
    if MANIFEST is None:
        raise FileNotFoundError(f"{MANIFEST_PATH} not found (no crash in this scenario)")
    lab_trace.record({"kind": "manifest_loaded"})
    return copy.deepcopy(MANIFEST)


def run_agent(area: str, prompt: str) -> str:
    """Run one exploration agent for an area (reads that area's files). SIMULATED."""
    lab_trace.record({"kind": "agent_run", "area": area, "prompt_head": prompt[:200],
                      "had_state": bool(MANIFEST and MANIFEST["agents"].get(area, {}).get("partial", "~") in prompt)})
    return _AREA_FINDINGS.get(area, "no findings")


def submit(*results) -> None:
    """Hand the outcome back to the lab's result check."""
    items = []
    for r in results:
        if isinstance(r, Result):
            items.append({"type": "result", "session_id": r.session_id, "value": r.value, "path": r.path,
                          "degraded": r.degraded})
        elif isinstance(r, dict):
            items.append({"type": "findings", "areas": sorted(r)})
        else:
            items.append({"type": "other", "repr": repr(r)[:120]})
    base = SESSIONS.get(_resolve(BASELINE)) if any(s["name"] == BASELINE for s in SESSIONS.values()) else None
    lab_trace.record({"kind": "submit", "items": items, "baseline_len": len(base["history"]) if base else None,
                      "baseline_len_day1": TRUTH.get("baseline_len")})
    print("SUBMITTED:", items)
