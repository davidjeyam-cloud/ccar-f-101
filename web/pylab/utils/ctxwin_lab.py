"""
SIMULATED context window for D5.1 Context Window Management (guide TS 5.1 + TS 5.4).

Grounding (fetched 2026-09-28):
- platform docs "Context windows": everything in the request counts (system prompt, every message including tool results,
  tool definitions) plus the output; each turn's input is the whole previous conversation plus the new user message; more
  context isn't automatically better ("context rot"); if the input alone exceeds the window the API returns a 400
  invalid_request_error ("prompt is too long").
- code.claude.com "How Claude Code works": as context fills, Claude Code compacts automatically; requests and key code
  snippets are preserved but detailed instructions from early in the conversation may be lost, so put persistent rules in
  CLAUDE.md; /compact takes a focus; subagents work in their own context window and return a summary.
- guide TS 5.1 (K4 full history; S6 structured upstream output for limited downstream budgets) and TS 5.4 (K1 degradation,
  K3/S1 subagents isolate exploration, S5 /compact).
INVENTED (simulation): the token numbers (a 20,000-token window, 900 tokens per file read, 3,000 per verbose analysis), which
turn counts as an "early detailed instruction", and the simulated model's replies. Token figures are illustrative only.
"""

from __future__ import annotations

from utils import lab_trace

SCENARIO_IDS = ("stateless_history", "exploration", "long_session", "downstream_budget")
SCENARIO = "stateless_history"
WINDOW = 20_000          # simulated context window (tokens)
FILE_TOKENS = 900
FILES = [f"src/payments/{n}.py" for n in (
    "api", "models", "webhooks", "retry_policy", "settings", "stripe_client", "refunds", "ledger", "notifications", "audit",
    "fraud", "currency", "tax", "invoices", "exports", "admin", "cli", "tasks", "queue", "cache", "metrics", "health",
    "auth", "sessions", "rate_limit", "errors", "utils", "schema", "fixtures", "conftest")]
QUESTION = "Where is the retry policy for payment webhooks configured?"
ANSWER = "webhooks.py reads RETRY_POLICY from retry_policy.py (max 5 attempts, exponential backoff)"

CHAT_TURNS = [
    "Hi, my order ORD-4410 arrived damaged.",
    "It's the blender - the glass jug is cracked.",
    "Can you refund it to my card?",
]


class ContextOverflow(Exception):
    """SIMULATED 400 invalid_request_error: prompt is too long."""


def configure(scenario_id: str) -> None:
    global SCENARIO
    SCENARIO = scenario_id if scenario_id in SCENARIO_IDS else "stateless_history"
    _MAIN.clear()
    _MAIN.update(tokens=1_500, reads=[])


_MAIN: dict = {}
configure("stateless_history")


def _tokens(messages: list) -> int:
    return sum(40 + len(str(m.get("content", ""))) // 4 for m in messages)


# ── Scenario 1: the API is stateless ─────────────────────────────────────────


def chat(messages: list) -> str:
    """One Messages API call. The SIMULATED model sees ONLY `messages` - nothing is remembered between calls."""
    text = " ".join(str(m.get("content", "")) for m in messages if m.get("role") == "user")
    last = str(messages[-1].get("content", "")) if messages else ""
    knows_order = "ORD-4410" in text
    knows_item = "blender" in text
    if "refund" in last.lower():
        reply = ("Done - I've refunded the blender on ORD-4410 to your card." if knows_order and knows_item
                 else "I can help with a refund. Could you tell me your order number and which item it is?")
    elif "blender" in last.lower():
        reply = "Sorry about the cracked jug. " + ("I can see ORD-4410." if knows_order else "What's the order number?")
    else:
        reply = "Sorry to hear that - which item was damaged?"
    rec = {"kind": "ctxwin_run", "scenario": SCENARIO, "task": "chat", "sent": len(messages), "tokens": _tokens(messages),
           "last": last, "reply": reply, "knows_order": knows_order}
    lab_trace.record(rec)
    print(f"call with {len(messages)} message(s), ~{rec['tokens']} tokens -> {reply}")
    return reply


# ── Scenario 2: verbose exploration ──────────────────────────────────────────


def read(path: str) -> str:
    """Read a file INTO THE MAIN CONTEXT (like the Read tool in the main conversation)."""
    _MAIN["tokens"] += FILE_TOKENS
    _MAIN["reads"].append(path)
    if _MAIN["tokens"] > WINDOW:
        rec = {"kind": "ctxwin_run", "scenario": SCENARIO, "task": "explore", "mode": "main", "main_tokens": _MAIN["tokens"],
               "reads": len(_MAIN["reads"]), "overflow": True, "answer": None}
        lab_trace.record(rec)
        print(f"main context {_MAIN['tokens']:,} / {WINDOW:,} tokens after {len(_MAIN['reads'])} reads")
        raise ContextOverflow("SIMULATED 400 invalid_request_error: prompt is too long "
                              f"({_MAIN['tokens']:,} tokens > {WINDOW:,} window)")
    return f"<contents of {path}>"


def answer(question: str) -> str:
    """Answer from what the MAIN context holds."""
    found = "src/payments/retry_policy.py" in _MAIN["reads"] and "src/payments/webhooks.py" in _MAIN["reads"]
    text = ANSWER if found else "I couldn't find where the retry policy is configured."
    rec = {"kind": "ctxwin_run", "scenario": SCENARIO, "task": "explore", "mode": "main", "main_tokens": _MAIN["tokens"],
           "reads": len(_MAIN["reads"]), "overflow": False, "answer": text}
    lab_trace.record(rec)
    print(f"main context {_MAIN['tokens']:,} / {WINDOW:,} tokens · answer: {text}")
    return text


def spawn_explorer(question: str) -> str:
    """A subagent explores in ITS OWN context window and returns only a short summary to the main conversation."""
    sub_reads = ["src/payments/webhooks.py", "src/payments/retry_policy.py", "src/payments/settings.py",
                 "src/payments/queue.py", "src/payments/tasks.py"]
    summary = f"Summary from explorer: {ANSWER}. Files: webhooks.py, retry_policy.py."
    _MAIN["tokens"] += 300
    rec = {"kind": "ctxwin_run", "scenario": SCENARIO, "task": "explore", "mode": "subagent", "main_tokens": _MAIN["tokens"],
           "sub_tokens": 1_500 + FILE_TOKENS * len(sub_reads), "reads": 0, "overflow": False, "answer": summary}
    lab_trace.record(rec)
    print(f"subagent read {len(sub_reads)} files in its own context (~{rec['sub_tokens']:,} tokens there); "
          f"main context grew to {_MAIN['tokens']:,} tokens")
    print(summary)
    return summary


# ── Scenario 3: a long Claude Code session ───────────────────────────────────


class Session:
    """A SIMULATED Claude Code session. CLAUDE.md is reloaded every time; the conversation can be compacted or cleared."""

    TASK = "Add jittered backoff to the payment-webhook retries"

    def __init__(self, claude_md=None):
        self.claude_md = list(claude_md or [])
        self.convo = [("request", self.TASK)]
        self.used = 3_000
        self.events = []

    def say(self, text: str) -> None:
        """Tell Claude something in the conversation (not in CLAUDE.md)."""
        self.convo.append(("instruction", text))
        self.used += 200

    def work(self, until_percent: int = 95) -> None:
        self.convo.append(("finding", "retry logic lives in webhooks.py:88; backoff constant in retry_policy.py"))
        self.used = int(WINDOW * until_percent / 100)
        self.events.append(f"worked until {until_percent}% of the window ({self.used:,} tokens)")

    def compact(self, focus: str = "") -> None:
        """/compact: summarise. Requests and key findings are kept; detailed instructions from early on may be lost (docs)."""
        self.convo = [c for c in self.convo if c[0] != "instruction"]
        self.used = 4_000
        self.events.append(f"/compact{(' focus: ' + focus) if focus else ''} -> {self.used:,} tokens; early instructions dropped")

    def clear(self) -> None:
        """/clear: a fresh context. Only CLAUDE.md remains."""
        self.convo = []
        self.used = 1_500
        self.events.append("/clear -> the conversation is gone")

    def work_more(self) -> str:
        if self.used > int(WINDOW * 0.9):
            self.compact()   # Claude Code auto-compacts as it approaches the limit
            self.events.append("(auto-compacted)")
        knows_task = any(k == "request" for k, _ in self.convo)
        knows_finding = any(k == "finding" for k, _ in self.convo)
        rules = self.claude_md + [t for k, t in self.convo if k == "instruction"]
        protects = any("migrations" in r for r in rules)
        edits = []
        if knows_task:
            edits = ["src/payments/webhooks.py", "src/payments/retry_policy.py"]
            if not protects:
                edits.append("migrations/0042_retry_columns.py")
        result = ("Jittered backoff added" if knows_task and knows_finding
                  else "Asked what to work on" if not knows_task else "Re-explored the codebase from scratch")
        rec = {"kind": "ctxwin_run", "scenario": SCENARIO, "task": "session", "events": list(self.events), "knows_task": knows_task,
               "knows_finding": knows_finding, "rule_active": protects, "edits": edits, "result": result,
               "rule_in_claude_md": any("migrations" in r for r in self.claude_md)}
        lab_trace.record(rec)
        print("\n".join(self.events))
        print(f"knows the task: {knows_task} · knows the findings: {knows_finding} · 'never edit migrations/' active: {protects}")
        print(f"edited: {edits or 'nothing'} -> {result}")
        return result


def session(claude_md=None) -> Session:
    return Session(claude_md)


# ── Scenario 4: a downstream agent with a small budget ───────────────────────

REPORT_BUDGET = 6_000
_ANALYSES = [
    ("market", "EU demand for heat pumps grew 18% in 2025", "https://example.com/market-2025"),
    ("policy", "subsidy cut in Germany from July 2026", "https://example.com/policy-de"),
    ("supply", "compressor lead times doubled to 20 weeks", "https://example.com/supply"),
    ("competition", "two new entrants undercut prices by 12%", "https://example.com/competitors"),
]


def analyses() -> list:
    """Four document-analysis subagents. Call each with structured=True/False to get its output."""
    def make(name, fact, url):
        def run(structured: bool = False) -> dict:
            if structured:
                return {"name": name, "tokens": 400, "key_facts": [fact], "citations": [url], "relevance": 0.9}
            return {"name": name, "tokens": 3_000, "text": f"[{name}] long reasoning chain ... {fact} ... more caveats ..."}
        run.__name__ = f"analysis_{name}"
        return run
    return [make(*a) for a in _ANALYSES]


def report(results: list, budget: int | None = None) -> str:
    """The report agent can only fit `budget` tokens of input; what doesn't fit is dropped."""
    budget = budget or REPORT_BUDGET
    used, included, dropped = 0, [], []
    for r in results:
        if used + r["tokens"] <= budget:
            used += r["tokens"]
            included.append(r["name"])
        else:
            dropped.append(r["name"])
    cited = all("citations" in r for r in results if r["name"] in included)
    rec = {"kind": "ctxwin_run", "scenario": SCENARIO, "task": "report", "used": used, "budget": budget,
           "included": included, "dropped": dropped, "cited": cited}
    lab_trace.record(rec)
    print(f"report input {used:,} / {budget:,} tokens · included {included} · dropped {dropped or 'none'} · citations kept: {cited}")
    return f"Report covering {', '.join(included)}"
