"""
Playground engine for D2.3 MCP, on the SIMULATED session, agent and backends in utils/mcp_lab.py (see its docstring for
what is documented vs invented). Configs and tool handlers are built from the tab's knobs.
"""

from __future__ import annotations

import contextlib
import io
import json
from dataclasses import dataclass

from utils import lab_trace
from utils import mcp_lab as ml


@dataclass
class McpConfig:
    mode: str = "scopes"
    github_scope: str = "project"      # project | user | local
    token_style: str = "var"           # var | literal
    teammate_env: str = "set"          # set | unset
    jira_source: str = "community"     # community | custom
    notes_scope: str = "user"          # user | project
    tool_desc: str = "detailed"        # detailed | vague
    resources: str = "yes"
    error_style: str = "structured"    # structured | generic | code_only
    err_case: str = "policy"           # timeout | policy | permission | empty
    orders_state: str = "empty"        # empty | permission | timeout_twice
    empty_handling: str = "success"    # success | error | swallow
    local_retry: str = "yes"
    partial_info: str = "yes"


_DETAILED = ("Finds every caller of a function across ALL of the team's service repositories, not just the one that is open, "
             "using the build's call graph. Returns the file, line, service and calling function for each reference. Use it "
             "instead of Grep whenever you need callers or usages beyond the current repository.")


def _impl(cfg):
    return {"refund-platform": {
        "tools": [{"name": "find_references", "description": _DETAILED if cfg.tool_desc == "detailed" else "Finds references."},
                  {"name": "list_tables", "description": "Lists the refunds database tables."},
                  {"name": "describe_table", "description": "Returns one table's columns."}],
        "resources": ([{"uri": "schema://tables", "description": "Every refunds-database table with a one-line purpose"}]
                      if cfg.resources == "yes" else [])}}


def _configs(cfg):
    token = "${GITHUB_TOKEN}" if cfg.token_style == "var" else "not-a-real-token-123"
    github = {"command": "npx", "args": ["-y", ml.COMMUNITY["github"]], "env": {"GITHUB_TOKEN": token}}
    jira = ({"command": "npx", "args": ["-y", ml.COMMUNITY["jira"]], "env": {"JIRA_TOKEN": "${JIRA_TOKEN}"}}
            if cfg.jira_source == "community" else
            {"command": "python", "args": ["tools/our_jira_server.py"], "env": {"JIRA_TOKEN": "${JIRA_TOKEN}"}})
    notes = {"command": "python", "args": ["~/experiments/notes_server.py"]}
    proj = {"jira": jira, "refund-platform": {"command": "python", "args": ["tools/refund_platform_server.py"]}}
    user = {}
    if cfg.github_scope == "project":
        proj = {"github": github, **proj}
    else:
        user["github"] = github            # user and local scope both live in YOUR ~/.claude.json - never in the repo
    (proj if cfg.notes_scope == "project" else user)["scratch-notes"] = notes
    return {"mcpServers": proj}, {"mcpServers": user}


def _ok(data):
    return {"content": [{"type": "text", "text": json.dumps(data)}]}


def _err(cfg, category, retryable, description, customer_message=None):
    if cfg.error_style == "generic":
        body = {"error": "Operation failed"}
    elif cfg.error_style == "code_only":
        body = {"errorCategory": category, "isRetryable": retryable, "description": description.split(":")[0] + " (code 4031)"}
    else:
        body = {"errorCategory": category, "isRetryable": retryable, "description": description}
        if customer_message:
            body["customer_message"] = customer_message
    return {"isError": True, "content": [{"type": "text", "text": json.dumps(body)}]}


def _handlers(cfg, empty_handling="success", retry=True, partial=True):
    def lookup_orders(customer_id):
        try:
            orders = ml.orders_backend.query(customer_id)
        except ml.BackendTimeout as e:
            if empty_handling == "swallow":
                return _ok({"orders": []})
            return _err(cfg, "transient", True, f"Order service timed out: {e}")
        except ml.PermissionDenied as e:
            if empty_handling == "swallow":
                return _ok({"orders": []})
            return _err(cfg, "permission", False, f"Not allowed to read these orders: {e}")
        if not orders and empty_handling == "error":
            return _err(cfg, "not_found", True, "No orders found")
        return _ok({"orders": orders})

    def issue_refund(order_id, amount):
        try:
            return _ok(ml.refund_backend.issue(order_id, amount))
        except ml.PolicyViolation as e:
            return _err(cfg, "business", False, f"{e.code}: refund {amount} exceeds the {e.limit} limit",
                        customer_message=f"Refunds over ${e.limit} need a manager's approval - I've requested it for you.")

    def orders_subagent(customer_id):
        profile = ml.get_profile(customer_id)
        attempted, info = [], {}
        for attempt in range(1, 4 if retry else 2):
            raw = lookup_orders(customer_id)
            info = json.loads(raw["content"][0]["text"])
            if not raw.get("isError"):
                return {"status": "ok", "profile": profile, "orders": info["orders"]}
            attempted.append(f"lookup_orders #{attempt}: {info.get('errorCategory', '?')}")
            if not info.get("isRetryable"):
                break
        if not partial:
            return {"status": "failed"}
        return {"status": "failed", "error": info, "attempted": attempted, "partial": {"profile": profile}}

    return lookup_orders, issue_refund, orders_subagent


_ORDERS_SC = {"empty": "empty_result", "permission": "access_failure", "timeout_twice": "transient_timeout"}


def run_mcp(message: str, cfg: McpConfig) -> dict:
    lab_trace.reset()
    out = {"lines": [], "notes": [], "files": {}, "ok": True}
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        if cfg.mode in ("scopes", "descriptions", "resources"):
            ml.configure({"scopes": "team_server", "descriptions": "grep_preferred", "resources": "catalog"}[cfg.mode])
            if cfg.mode == "scopes" and cfg.teammate_env == "unset":
                ml.TEAMMATE_ENV = {"JIRA_TOKEN"}
            else:
                ml.TEAMMATE_ENV = {"GITHUB_TOKEN", "JIRA_TOKEN"}
            proj, user = _configs(cfg)
            ml.connect(proj, user, _impl(cfg))
            ml.TEAMMATE_ENV = {"GITHUB_TOKEN", "JIRA_TOKEN"}
            c = next(e for e in lab_trace.EVENTS if e["kind"] == "mcp_connect")
            if cfg.mode == "scopes":
                where = {"project": ".mcp.json (project scope - committed)", "user": "~/.claude.json (user scope - all your projects)",
                         "local": "~/.claude.json under this project's path (local scope, the default - only you, only here)"}
                out["files"] = {".mcp.json  (committed to git)": proj, "~/.claude.json  (your machine only)": user}
                out["lines"] += [f"GitHub server stored in: {where[cfg.github_scope]}",
                                 f"Your session loads: {c['you']}", f"A teammate who clones the repo loads: {c['teammate']}"]
                out["lines"] += [f"warning: {w}" for w in c["you_warnings"] + c["teammate_warnings"]]
                if c["committed_secrets"]:
                    out["notes"].append(f"A literal credential is in the committed .mcp.json: {c['committed_secrets']}")
                if "github" not in c["teammate"]:
                    out["notes"].append("Your teammate has no working GitHub server.")
                if "scratch-notes" in c["teammate"]:
                    out["notes"].append("Your personal experiment is now in every teammate's session (and asks each of them for approval).")
                if c["custom_standard"]:
                    out["notes"].append(f"You wrote and now maintain a custom server for a standard integration: {c['custom_standard']}.")
            else:
                out["lines"].append(f"Tools available together: {['Grep', 'Read', '…'] + c['tools']}")
                if c["resources"]:
                    out["lines"].append(f"Resources: {c['resources']}")
                ml.ask_agent(message.strip())
                a = lab_trace.EVENTS[-1]
                out["lines"] += [f"Agent calls: {a['calls']}", f"Answer: {a['answer']}"]
                if cfg.mode == "descriptions" and "Grep" in a["calls"][0]:
                    out["notes"].append("The agent used Grep and found only this repository's callers.")
                if cfg.mode == "resources" and len(a["calls"]) > 2:
                    out["notes"].append(f"{len(a['calls'])} exploratory calls to find one table.")
        else:
            if cfg.mode == "errors":
                sc = {"timeout": "transient_timeout", "policy": "policy_violation", "permission": "access_failure",
                      "empty": "empty_result"}[cfg.err_case]
                h = _handlers(cfg)
            elif cfg.mode == "empty":
                sc = _ORDERS_SC[cfg.orders_state]
                h = _handlers(McpConfig(), empty_handling=cfg.empty_handling)
            else:
                sc = _ORDERS_SC[cfg.orders_state]
                h = _handlers(McpConfig(), retry=cfg.local_retry == "yes", partial=cfg.partial_info == "yes")
            ml.configure(sc)
            ml.run_support(*h)
            s = next(e for e in lab_trace.EVENTS if e["kind"] == "mcp_support")
            ok, _bug, _t = __import__("utils.concepts_content.mcp", fromlist=["_diagnose"])._diagnose(
                {"scenario": sc, "raised": None, "conn": None, "agent": None, "sup": s})
            if s.get("tool_results"):
                out["lines"].append(f"Tool result the agent read (last): {s['tool_results'][-1]}")
                out["lines"].append(f"Agent attempts: {s.get('agent_attempts')}")
            if s.get("subagent") is not None:
                out["lines"].append(f"Subagent returned to the coordinator: {s['subagent']}")
            out["lines"] += [f"Customer is told: “{s['reply']}”", f"Backend calls: {s['backend_calls']}"
                             + (f" · subagent dispatched {s['dispatches']}×" if s["dispatches"] > 1 else "")]
            if not ok:
                out["notes"].append({"transient_timeout": "The customer didn't get their orders although the service recovered.",
                                     "policy_violation": "Wasted retries or an unfriendly reply for a policy refusal.",
                                     "empty_result": "A valid “no orders” answer was treated as a failure.",
                                     "access_failure": "The failure was hidden or handed over without what was tried and what is known."}[sc])
    out["log"] = buf.getvalue()
    out["ok"] = not out["notes"]
    return out
