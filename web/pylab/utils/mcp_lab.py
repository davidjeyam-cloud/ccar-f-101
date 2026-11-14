"""
SIMULATED MCP lab for D2.3 Model Context Protocol — configuring MCP servers in Claude Code and returning structured errors
from MCP tools.

Documented behaviour it follows (code.claude.com/docs/en/mcp, common-workflows, agent-sdk/custom-tools — fetched 2026-09-27):
- project scope = .mcp.json at the project root, checked in and shared with the team; user scope = ~/.claude.json, available
  in all your projects and private to you (local scope, the default, is also private: ~/.claude.json under the project path);
- ${VAR} and ${VAR:-default} expand in command, args, env, url and headers; an unset variable with no default leaves the
  text unexpanded and Claude Code warns (claude mcp list);
- tools from every connected server are available together, named mcp__<server>__<tool>;
- resources are referenced as @server:resource;
- a tool reports a failure with isError (TS) / "is_error" (Python) so the agent reads it as an error and the loop continues.
The guide's conventions it follows (TS 2.2 / 2.4): errorCategory, isRetryable, customer-friendly text for business rules,
local recovery in subagents, empty result vs access failure, community vs custom servers, rich MCP tool descriptions.
INVENTED (simulation): the servers, the environment, the "community" Jira package name, the agent's tool choice between Grep
and an MCP tool, the backends and their failures, and how the simulated agent reacts to each result.
"""

from __future__ import annotations

import json
import re

from utils import lab_trace

SCENARIO_IDS = ("team_server", "personal_server", "grep_preferred", "catalog",
                "transient_timeout", "policy_violation", "empty_result", "access_failure")
CONFIG_SCENARIOS = SCENARIO_IDS[:4]

TASK = "config"
SCENARIO = "team_server"
COMMUNITY = {"jira": "example-community-jira-mcp", "github": "example-community-github-mcp"}   # FAKE package names
STANDARD_INTEGRATIONS = {"jira", "github", "slack", "sentry"}
YOUR_ENV = {"GITHUB_TOKEN", "JIRA_TOKEN"}         # names only - the simulation never holds a value
TEAMMATE_ENV = {"GITHUB_TOKEN", "JIRA_TOKEN"}
_SECRETY = re.compile(r"(token|key|secret|password|authorization)", re.I)
BUILTIN_TOOLS = ["Read", "Grep", "Glob", "Bash", "Edit", "Write"]
REFUND_LIMIT = 500
_SESSION: dict = {}


def configure(scenario_id: str) -> None:
    global TASK, SCENARIO
    SCENARIO = scenario_id
    TASK = "config" if scenario_id in CONFIG_SCENARIOS else "errors"
    _SESSION.clear()
    orders_backend.calls = 0
    refund_backend.calls = 0


# ── Part 1: configuration ─────────────────────────────────────────────────────

def _expand(value, env):
    """${VAR} / ${VAR:-default} expansion (docs). Returns (text, missing-var list)."""
    missing = []

    def rep(m):
        name, default = m.group(1), m.group(3)
        if name in env:
            return f"<{name} from your environment>"
        if default is not None:
            return default
        missing.append(name)
        return m.group(0)                          # docs: the unexpanded ${VAR} text is used as-is

    return re.sub(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(:-([^}]*))?\}", rep, str(value)), missing


def _literal_secrets(project_mcp):
    found = []
    for name, spec in (project_mcp or {}).get("mcpServers", {}).items():
        for field in ("env", "headers"):
            for k, v in (spec.get(field) or {}).items():
                if _SECRETY.search(k) and "${" not in str(v):
                    found.append(f"{name}.{field}.{k}")
        for a in spec.get("args", []) + [spec.get("url", "")]:
            if re.search(r"(token|key|secret)=[^$]", str(a), re.I):
                found.append(f"{name}: literal credential in args/url")
    return found


def _load(servers: dict, env: set, impls: dict):
    loaded, warnings, tools = {}, [], []
    for name, spec in servers.items():
        miss = []
        for field in ("command", "url"):
            if spec.get(field):
                miss += _expand(spec[field], env)[1]
        for a in spec.get("args", []):
            miss += _expand(a, env)[1]
        for field in ("env", "headers"):
            for v in (spec.get(field) or {}).values():
                miss += _expand(v, env)[1]
        if miss:
            warnings.append(f"{name}: missing variable(s) {sorted(set(miss))} - left unexpanded, server can't authenticate")
            continue
        loaded[name] = spec
        impl = impls.get(name) or {"tools": [{"name": "call", "description": f"{name} tools"}]}
        tools += [f"mcp__{name}__{t['name']}" for t in impl.get("tools", [])]
    return loaded, warnings, tools


def connect(project_mcp: dict, user_mcp: dict, server_impls: dict | None = None) -> list[str]:
    """Start a SIMULATED Claude Code session for you AND for a teammate who just cloned the repo.
    project_mcp = the .mcp.json you commit; user_mcp = the mcpServers in YOUR ~/.claude.json (the teammate has their own, empty)."""
    impls = server_impls or {}
    proj = dict((project_mcp or {}).get("mcpServers", {}))
    user = dict((user_mcp or {}).get("mcpServers", {}))
    you_servers = {**user, **proj}                 # (local > project > user precedence - no local entries here)
    you, you_warn, you_tools = _load(you_servers, YOUR_ENV, impls)
    mate, mate_warn, mate_tools = _load(proj, TEAMMATE_ENV, impls)
    custom_standard = [n for n, s in proj.items() if n in STANDARD_INTEGRATIONS
                       and not any(COMMUNITY.get(n, "\0") in str(x) for x in [s.get("command", "")] + s.get("args", []))]
    _SESSION.update({"impls": impls, "tools": BUILTIN_TOOLS + you_tools})
    ev = {"kind": "mcp_connect", "project": sorted(proj), "user": sorted(user), "you": sorted(you), "teammate": sorted(mate),
          "you_warnings": you_warn, "teammate_warnings": mate_warn, "committed_secrets": _literal_secrets(project_mcp),
          "custom_standard": custom_standard, "tools": you_tools,
          "resources": sorted(f"@{n}:{r['uri']}" for n, i in impls.items() if n in you for r in i.get("resources", []))}
    lab_trace.record(ev)
    print(f"your session: servers {ev['you']} · teammate's session: servers {ev['teammate']}")
    print(f"tools available together (discovered at connection): {you_tools}")
    for w in you_warn + mate_warn:
        print("warning:", w)
    if ev["committed_secrets"]:
        print("!! committed in .mcp.json:", ev["committed_secrets"])
    return you_tools


_CALLERS_ALL = ["billing/api.py:88", "billing/jobs.py:14", "support/refunds.py:41", "support/bot.py:203",
                "ledger/sync.py:57", "ledger/audit.py:12", "web/checkout.py:311"]
_CALLERS_HERE = [c for c in _CALLERS_ALL if c.startswith("support/")] + ["support/tests/test_refunds.py:9"]


def ask_agent(question: str = "") -> str:
    """The SIMULATED agent answers the scenario's question with the tools and resources connected."""
    impls, tools = _SESSION.get("impls", {}), _SESSION.get("tools", BUILTIN_TOOLS)
    calls, answer = [], ""
    if SCENARIO == "grep_preferred" or "caller" in question.lower():
        mcp = next(((n, t) for n, i in impls.items() for t in i.get("tools", [])
                    if t["name"] == "find_references" and f"mcp__{n}__find_references" in tools), None)
        d = (mcp[1].get("description", "") if mcp else "").lower()
        detailed = len(d.split()) >= 20 and ("across" in d or "all repositor" in d)
        if detailed:
            calls.append(f"mcp__{mcp[0]}__find_references(process_refund)")
            answer = f"{len(_CALLERS_ALL)} callers across 4 services: {_CALLERS_ALL}"
        else:
            calls.append("Grep(pattern='process_refund(')")     # a vague MCP description -> the familiar built-in wins
            answer = f"{len(_CALLERS_HERE)} callers (this repository only): {_CALLERS_HERE}"
        q = "Find every caller of process_refund across our services."
    else:
        res = [(n, r) for n, i in impls.items() for r in i.get("resources", [])]
        q = "Which table stores refund approvals?"
        if res and any(f"mcp__{n}__" in " ".join(tools) for n, _ in res):
            n, r = res[0]
            calls.append(f"read resource @{n}:{r['uri']}")
            answer = "refund_approvals (from the catalog: 'approvals for refunds above the limit')"
        else:
            calls.append("mcp__refund-platform__list_tables()")
            for t in ["customers", "orders", "payments", "refunds", "refund_events", "refund_approvals"]:
                calls.append(f"mcp__refund-platform__describe_table({t})")
            answer = "refund_approvals (found after describing 6 tables)"
    lab_trace.record({"kind": "mcp_agent", "question": question or q, "calls": calls, "answer": answer})
    print(f"agent: {question or q}\n  calls: {calls}\n  answer: {answer}")
    return answer


# ── Part 2: structured errors from MCP tools ─────────────────────────────────

class BackendTimeout(Exception):
    """The order service didn't answer in time (transient)."""


class PermissionDenied(Exception):
    """This service account may not read orders for that region (permission)."""


class PolicyViolation(Exception):
    """A business rule refused the operation."""

    def __init__(self, code, limit):
        super().__init__(code)
        self.code, self.limit = code, limit


class _Orders:
    calls = 0

    def profile(self, customer_id):
        return {"customer_id": customer_id, "name": "Customer A", "email": "customer.a@example.com", "tier": "gold"}

    def query(self, customer_id):
        self.calls += 1
        lab_trace.record({"kind": "mcp_backend", "service": "orders", "n": self.calls})
        if SCENARIO == "transient_timeout" and self.calls <= 2:
            raise BackendTimeout("orders service timed out after 5s")
        if SCENARIO == "access_failure":
            raise PermissionDenied("service account svc-support lacks orders:read for region EU")
        if SCENARIO == "empty_result":
            return []
        return [{"order_id": "ORD-2001", "total": 120.0}, {"order_id": "ORD-2002", "total": 900.0}]


class _Refunds:
    calls = 0

    def issue(self, order_id, amount):
        self.calls += 1
        lab_trace.record({"kind": "mcp_backend", "service": "refunds", "n": self.calls})
        if amount > REFUND_LIMIT:
            raise PolicyViolation("POLICY_LIMIT_EXCEEDED", REFUND_LIMIT)
        return {"refund_id": "RF-1", "amount": amount}


orders_backend = _Orders()
refund_backend = _Refunds()


def get_profile(customer_id):
    return orders_backend.profile(customer_id)


def _read(result):
    if not isinstance(result, dict):
        return {"description": str(result)}, False
    text = "".join(c.get("text", "") for c in result.get("content", []) if isinstance(c, dict))
    try:
        info = json.loads(text)
    except (ValueError, TypeError):
        info = {"description": text}
    if not isinstance(info, dict):
        info = {"value": info}
    return info, bool(result.get("isError"))


_JARGON = re.compile(r"[A-Z]{3,}_[A-Z_]{3,}|code \d{3,}|Operation failed|Traceback", re.I)


def run_support(lookup_orders, issue_refund, orders_subagent) -> str:
    """The SIMULATED coordinator handles the scenario's customer request with YOUR tool handlers and subagent."""
    rec = {"kind": "mcp_support", "scenario": SCENARIO, "tool_results": [], "dispatches": 0}
    if SCENARIO == "policy_violation":
        attempts = 0
        for attempts in range(1, 4):
            r = issue_refund("ORD-2002", 900.0)
            info, is_err = _read(r)
            rec["tool_results"].append({"isError": is_err, **info})
            if not is_err:
                reply = "Your refund has been issued."
                break
            if info.get("isRetryable") is False:        # structured metadata: retrying won't help
                break
        if rec["tool_results"] and rec["tool_results"][-1]["isError"]:
            reply = info.get("customer_message") or info.get("description") or "Sorry, something went wrong."
        rec.update(agent_attempts=attempts, reply=reply)
    else:
        rec["dispatches"] = 1
        out = orders_subagent("C-1001")
        rec["subagent"] = out
        if out.get("status") == "ok":
            orders = out.get("orders")
            reply = (f"I found {len(orders)} orders: {[o['order_id'] for o in orders]}." if orders
                     else "You have no orders on file with us.")
        elif out.get("partial") and out.get("attempted"):
            reply = (f"I can see your {out['partial'].get('profile', {}).get('tier', '')} account, but I couldn't reach your order "
                     f"history ({out.get('error', {}).get('errorCategory', 'error')}). I've passed this to a colleague with the details.")
            rec["escalated"] = True
        else:                                            # nothing to go on: re-dispatch blind, then give up
            rec["dispatches"] = 2
            out2 = orders_subagent("C-1001")
            reply = "Sorry, something went wrong. Please try again later." if out2.get("status") != "ok" else "Found your orders."
    rec["reply"] = reply
    rec["backend_calls"] = {"orders": orders_backend.calls, "refunds": refund_backend.calls}
    lab_trace.record(rec)
    print(f"customer is told: {reply}")
    print(f"backend calls: {rec['backend_calls']}" + (f" · coordinator dispatched the subagent {rec['dispatches']}x" if rec["dispatches"] > 1 else ""))
    return reply


def is_jargon(text: str) -> bool:
    return bool(_JARGON.search(text or ""))
