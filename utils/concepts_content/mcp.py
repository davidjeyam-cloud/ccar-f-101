"""
D2.3 Model Context Protocol — connecting MCP servers to Claude Code / agents (scopes, ${VAR} expansion, tool descriptions,
resources, community vs custom servers) and returning structured errors from MCP tools. Guide TS 2.4 (p.11) and TS 2.2
(pp.9–10).

GROUNDING (CLAUDE.md, user rules): guide read from the PDF (2026-09-27); Claude Code and Agent SDK docs fetched 2026-09-27
(DOC_REFS). Every claim is in GROUNDING with its source type. The guide names two scopes; the docs add a third (local, the
default) — both shown. errorCategory / isRetryable are the guide's convention inside the error content; the protocol-level
flag is isError. Paraphrased; no real exam question reproduced.
"""

from utils.concept_types import Claim, ConceptContent, DocRef, ExamPoint, PlayTab, Question, Variant

DOCS_VERIFIED_ON = "2026-09-27"
_C = "https://code.claude.com/docs/en"

DOC_REFS = (
    DocRef("Connect Claude Code to tools via MCP — scopes, .mcp.json, env expansion, precedence, output limits", f"{_C}/mcp"),
    DocRef("Common workflows — reference MCP resources with @server:resource", f"{_C}/common-workflows"),
    DocRef("Give Claude custom tools — isError / is_error, errors keep the loop running", f"{_C}/agent-sdk/custom-tools"),
)

GROUNDING = (
    Claim("Three scopes: local (the default — ~/.claude.json under that project's path, only you, only this project), project "
          "(.mcp.json at the project root, checked in and shared with the team), user (~/.claude.json, all your projects, private "
          "to you).", "docs", "mcp § installation scopes"),
    Claim("Interactive sessions ask for approval before using project-scoped servers from .mcp.json; claude -p, Agent SDK and "
          "cloud sessions load them without asking.", "docs", "mcp § project scope"),
    Claim("When the same server name is defined in several places, Claude Code connects once using the highest-precedence "
          "definition: local, then project, then user, then plugin servers, then claude.ai connectors.", "docs", "mcp § scope precedence"),
    Claim("${VAR} and ${VAR:-default} expand in command, args, env, url and headers. If a variable is unset with no default the "
          "config still loads, claude mcp list shows a missing-variable warning, and the literal ${VAR} text is used.",
          "docs", "mcp § environment variable expansion"),
    Claim("In a remote server's url and headers, some credential variables (e.g. ANTHROPIC_API_KEY, NPM_TOKEN) are read as empty "
          "rather than expanded.", "docs", "mcp § environment variable expansion"),
    Claim("MCP resources are referenced with @server:resource, which fetches the data from the connected server.", "docs",
          "common-workflows § Reference files and directories"),
    Claim("Claude Code warns when an MCP tool's output exceeds 10,000 tokens; the default maximum is 25,000 (MAX_MCP_OUTPUT_TOKENS "
          "raises it).", "docs", "mcp § output limits"),
    Claim("A custom tool reports failure by returning isError: true (TypeScript) / \"is_error\": True (Python); the agent reads the "
          "message as an error and the loop continues. An uncaught exception also becomes an error result.", "docs",
          "agent-sdk/custom-tools § Handle errors"),
    Claim("Scoping: project-level .mcp.json for shared team tooling vs user-level ~/.claude.json for personal/experimental servers; "
          "${GITHUB_TOKEN}-style expansion keeps credentials out of the committed file; tools from all configured servers are "
          "discovered at connection and available together; resources expose content catalogs (issue summaries, documentation "
          "hierarchies, database schemas) to cut exploratory tool calls.", "guide", "TS 2.4 · Knowledge 1–4 · p.11"),
    Claim("Skills: shared servers in .mcp.json with env-var tokens; personal servers in ~/.claude.json; detailed MCP tool "
          "descriptions so the agent doesn't prefer built-ins like Grep; community servers for standard integrations (Jira), "
          "custom servers for team-specific workflows; resources for catalogs.", "guide", "TS 2.4 · Skills 1–5 · p.11"),
    Claim("The isError flag communicates tool failures; errors are transient (timeouts, unavailability), validation, business "
          "(policy violations) or permission; uniform \"Operation failed\" errors block good recovery; retryable vs non-retryable "
          "metadata prevents wasted retries.", "guide", "TS 2.2 · Knowledge 1–4 · pp.9–10"),
    Claim("Skills: return errorCategory, isRetryable and a human-readable description; retriable: false plus a customer-friendly "
          "explanation for business-rule violations; recover transient failures locally in subagents and propagate only "
          "unresolvable errors with partial results and what was attempted; tell access failures from valid empty results.",
          "guide", "TS 2.2 · Skills 1–4 · p.10"),
    Claim("The guide names project and user scope; the docs add local scope (the default). The guide says all tools are "
          "discovered at connection; the docs also describe tool search and cached tool lists that defer connecting.",
          "guide", "TS 2.4 K1, K3 vs mcp"),
    Claim("Putting the error metadata as JSON in the error's text content, and a customer_message beside the description, is this "
          "page's way of applying the guide's convention.", "recommendation", "TS 2.2 · Skills 1–2"),
    Claim("The servers, the fake community package names, the environment, the Grep-vs-MCP choice, the table catalog, the "
          "backends, their failures and the agent's reactions are invented.", "simulated", "utils/mcp_lab.py"),
)

CORRECT = r'''import json
from utils.mcp_lab import (COMMUNITY, TASK, BackendTimeout, PermissionDenied, PolicyViolation, ask_agent, connect,
                           get_profile, orders_backend, refund_backend, run_support)   # SIMULATED Claude Code, agent, backends

# ── Part 1 · configuration ────────────────────────────────────────────────────
# .mcp.json - project scope: committed, shared with the team. Tokens come from each person's environment.
PROJECT_MCP = {"mcpServers": {
    "github": {"command": "npx", "args": ["-y", COMMUNITY["github"]], "env": {"GITHUB_TOKEN": "${GITHUB_TOKEN}"}},
    "jira":   {"command": "npx", "args": ["-y", COMMUNITY["jira"]], "env": {"JIRA_TOKEN": "${JIRA_TOKEN}"}},  # standard -> community
    "refund-platform": {"command": "python", "args": ["tools/refund_platform_server.py"]},   # team-specific -> custom
}}
# ~/.claude.json - user scope: my personal, experimental server. Teammates never see it.
USER_MCP = {"mcpServers": {"scratch-notes": {"command": "python", "args": ["~/experiments/notes_server.py"]}}}

# What our custom server exposes: a well-described tool and a resource catalog
REFUND_PLATFORM = {
    "tools": [{"name": "find_references",
               "description": ("Finds every caller of a function across ALL of the team's service repositories, not just the "
                               "one that is open, using the build's call graph. Returns the file, line, service and calling "
                               "function for each reference. Use it instead of Grep whenever you need callers or usages "
                               "beyond the current repository.")},
              {"name": "list_tables", "description": "Lists the refunds database tables."},
              {"name": "describe_table", "description": "Returns one table's columns."}],
    "resources": [{"uri": "schema://tables", "description": "Every refunds-database table with a one-line purpose"}],
}


# ── Part 2 · structured errors from MCP tools ─────────────────────────────────
def ok(data):
    return {"content": [{"type": "text", "text": json.dumps(data)}]}


def error(category, retryable, description, customer_message=None):
    body = {"errorCategory": category, "isRetryable": retryable, "description": description}
    if customer_message:
        body["customer_message"] = customer_message
    return {"isError": True, "content": [{"type": "text", "text": json.dumps(body)}]}


def lookup_orders(customer_id):
    try:
        orders = orders_backend.query(customer_id)
    except BackendTimeout as e:
        return error("transient", True, f"Order service timed out: {e}")
    except PermissionDenied as e:
        return error("permission", False, f"Not allowed to read these orders: {e}")
    return ok({"orders": orders})            # an empty list is a SUCCESSFUL query with no matches


def issue_refund(order_id, amount):
    try:
        return ok(refund_backend.issue(order_id, amount))
    except PolicyViolation as e:
        return error("business", False, f"{e.code}: refund {amount} exceeds the {e.limit} limit",
                     customer_message=f"Refunds over ${e.limit} need a manager's approval - I've requested it for you.")


def orders_subagent(customer_id):
    profile = get_profile(customer_id)       # what we already know - partial results
    attempted = []
    for attempt in range(1, 4):
        info_raw = lookup_orders(customer_id)
        info = json.loads(info_raw["content"][0]["text"])
        if not info_raw.get("isError"):
            return {"status": "ok", "profile": profile, "orders": info["orders"]}
        attempted.append(f"lookup_orders #{attempt}: {info.get('errorCategory', '?')}")
        if not info.get("isRetryable"):
            break                            # retrying won't help: stop and report
    # couldn't resolve it locally -> tell the coordinator what failed, what we tried, and what we have
    return {"status": "failed", "error": info, "attempted": attempted, "partial": {"profile": profile}}


if TASK == "config":
    connect(PROJECT_MCP, USER_MCP, {"refund-platform": REFUND_PLATFORM})
    ask_agent()
else:
    run_support(lookup_orders, issue_refund, orders_subagent)
'''


def _swap(code, old, new):
    assert old in code, f"lab code changed: {old[:60]!r}"
    return code.replace(old, new, 1)


# ⭐ TS 2.2 · Knowledge 3 — one uniform error for everything
VARIANT_A = _swap(CORRECT, '''    body = {"errorCategory": category, "isRetryable": retryable, "description": description}
    if customer_message:
        body["customer_message"] = customer_message
''', '''    body = {"error": "Operation failed"}     # WRONG: the same generic error for every failure
''')
# ⭐ TS 2.2 · Skill 2 — non-retryable, but no customer-friendly explanation
VARIANT_B = _swap(CORRECT, '''        return error("business", False, f"{e.code}: refund {amount} exceeds the {e.limit} limit",
                     customer_message=f"Refunds over ${e.limit} need a manager's approval - I've requested it for you.")''',
                  '''        return error("business", False, f"{e.code} (code 4031)")   # WRONG: machine text only - the agent passes it to the customer''')
# ⭐ TS 2.2 · Skill 4 — "no matches" reported as an error
VARIANT_C = _swap(CORRECT, '''    return ok({"orders": orders})            # an empty list is a SUCCESSFUL query with no matches''',
                  '''    if not orders:
        return error("not_found", True, "No orders found")   # WRONG: an empty result is not a failure
    return ok({"orders": orders})''')
# ⭐ TS 2.2 · Skill 4 / Knowledge 1 — failures swallowed into an empty result
VARIANT_D = _swap(CORRECT, '''    try:
        orders = orders_backend.query(customer_id)
    except BackendTimeout as e:
        return error("transient", True, f"Order service timed out: {e}")
    except PermissionDenied as e:
        return error("permission", False, f"Not allowed to read these orders: {e}")''',
                  '''    try:
        orders = orders_backend.query(customer_id)
    except Exception:
        orders = []                          # WRONG: an access failure now looks like "no orders"''')
# ⭐ TS 2.2 · Skill 3 — no local recovery: every error goes straight up
VARIANT_E = _swap(CORRECT, '''    for attempt in range(1, 4):''', '''    for attempt in range(1, 2):              # WRONG: one try - transient errors aren't retried locally''')
# ⭐ TS 2.2 · Skill 3 — propagate without partial results or what was attempted
VARIANT_F = _swap(CORRECT, '''    return {"status": "failed", "error": info, "attempted": attempted, "partial": {"profile": profile}}''',
                  '''    return {"status": "failed"}              # WRONG: no error details, no attempts, no partial results''')
# ⭐ TS 2.4 · Knowledge 2 — a literal token in the committed .mcp.json
VARIANT_G = _swap(CORRECT, '''"env": {"GITHUB_TOKEN": "${GITHUB_TOKEN}"}},''',
                  '''"env": {"GITHUB_TOKEN": "not-a-real-token-123"}},   # WRONG: a literal secret in a committed file''')
# ⭐ TS 2.4 · Knowledge 1 / Skill 1 — the shared server configured in user scope
VARIANT_H = _swap(_swap(CORRECT,
    '''    "github": {"command": "npx", "args": ["-y", COMMUNITY["github"]], "env": {"GITHUB_TOKEN": "${GITHUB_TOKEN}"}},
''', ''),
    '''USER_MCP = {"mcpServers": {"scratch-notes": {"command": "python", "args": ["~/experiments/notes_server.py"]}}}''',
    '''USER_MCP = {"mcpServers": {"scratch-notes": {"command": "python", "args": ["~/experiments/notes_server.py"]},
                           # WRONG: the team's GitHub server in MY user config - teammates don't get it
                           "github": {"command": "npx", "args": ["-y", COMMUNITY["github"]], "env": {"GITHUB_TOKEN": "${GITHUB_TOKEN}"}}}}''')
# ⭐ TS 2.4 · Skill 2 — a personal experiment in the shared .mcp.json
VARIANT_I = _swap(_swap(CORRECT,
    '''    "refund-platform": {"command": "python", "args": ["tools/refund_platform_server.py"]},   # team-specific -> custom
}}''', '''    "refund-platform": {"command": "python", "args": ["tools/refund_platform_server.py"]},   # team-specific -> custom
    "scratch-notes": {"command": "python", "args": ["~/experiments/notes_server.py"]},   # WRONG: my experiment, now everyone's
}}'''), '''USER_MCP = {"mcpServers": {"scratch-notes": {"command": "python", "args": ["~/experiments/notes_server.py"]}}}''',
    '''USER_MCP = {"mcpServers": {}}''')
# ⭐ TS 2.4 · Skill 3 — a one-line MCP tool description
VARIANT_J = _swap(CORRECT, '''               "description": ("Finds every caller of a function across ALL of the team's service repositories, not just the "
                               "one that is open, using the build's call graph. Returns the file, line, service and calling "
                               "function for each reference. Use it instead of Grep whenever you need callers or usages "
                               "beyond the current repository.")},''',
                  '''               "description": "Finds references."},   # WRONG: too vague to beat the familiar Grep''')
# ⭐ TS 2.4 · Knowledge 4 / Skill 5 — no resource catalog
VARIANT_K = _swap(CORRECT, '''    "resources": [{"uri": "schema://tables", "description": "Every refunds-database table with a one-line purpose"}],''',
                  '''    "resources": [],                     # WRONG: no catalog - the agent has to explore''')
# ⭐ TS 2.4 · Skill 4 — a custom server for a standard integration
VARIANT_L = _swap(CORRECT, '''    "jira":   {"command": "npx", "args": ["-y", COMMUNITY["jira"]], "env": {"JIRA_TOKEN": "${JIRA_TOKEN}"}},  # standard -> community''',
                  '''    "jira":   {"command": "python", "args": ["tools/our_jira_server.py"], "env": {"JIRA_TOKEN": "${JIRA_TOKEN}"}},  # WRONG: we wrote our own Jira server''')

# ── Check and chart ────────────────────────────────────────────────────────────


def _facts(trace):
    ev = trace["events"]
    last = lambda k: next((e for e in reversed(ev) if e["kind"] == k), None)   # noqa: E731
    return {"scenario": trace["status"].get("scenario"), "raised": trace["status"]["raised"],
            "conn": last("mcp_connect"), "agent": last("mcp_agent"), "sup": last("mcp_support")}


def _diagnose(f):
    sc = f["scenario"]
    if f["raised"]:
        return False, None, f"raised: {f['raised'][:160]}"
    if sc in ("team_server", "personal_server", "grep_preferred", "catalog"):
        c = f["conn"]
        if c is None:
            return False, None, "connect() was never called"
        txt = (f".mcp.json: {c['project']} · your ~/.claude.json: {c['user']} · teammate gets: {c['teammate']} · "
               f"literal secrets committed: {c['committed_secrets'] or 'none'} · custom servers for standard integrations: "
               f"{c['custom_standard'] or 'none'}")
        if sc == "team_server":
            if c["committed_secrets"]:
                return False, "SECRET", txt
            if not {"github", "jira", "refund-platform"} <= set(c["teammate"]):
                return False, "USERSCOPE", txt
            if c["custom_standard"]:
                return False, "CUSTOM", txt
            return True, None, txt
        if sc == "personal_server":
            if "scratch-notes" in c["project"] or "scratch-notes" in c["teammate"]:
                return False, "SHAREDPERSONAL", txt
            return ("scratch-notes" in c["you"]), (None if "scratch-notes" in c["you"] else "SHAREDPERSONAL"), txt
        a = f["agent"]
        if a is None:
            return False, None, txt + " · the agent was never asked"
        txt = f"agent calls: {a['calls']} · answer: {a['answer']}"
        if sc == "grep_preferred":
            return ("find_references" in a["calls"][0]), (None if "find_references" in a["calls"][0] else "GREP"), txt
        return (len(a["calls"]) <= 2), (None if len(a["calls"]) <= 2 else "EXPLORE"), txt
    s = f["sup"]
    if s is None:
        return False, None, "run_support() was never called"
    reply, calls = s["reply"], s["backend_calls"]
    txt = f"customer is told: “{reply}” · backend calls: {calls} · subagent dispatches: {s['dispatches']}"
    if sc == "policy_violation":
        txt += f" · agent attempts: {s.get('agent_attempts')}"
        if s.get("agent_attempts", 0) > 1:
            return False, "GENERIC", txt
        if "manager" not in reply.lower():
            return False, "JARGON", txt
        return True, None, txt
    if sc == "transient_timeout":
        if "2 orders" in reply:
            return True, None, txt
        if "no orders" in reply.lower():
            return False, "SWALLOW", txt
        if s["dispatches"] > 1:
            return False, "NOPARTIAL", txt
        err = (s.get("subagent") or {}).get("error") or {}
        return False, ("NOLOCAL" if "errorCategory" in err else "GENERIC"), txt
    if sc == "empty_result":
        if "no orders" in reply.lower() and calls["orders"] == 1:
            return True, None, txt
        return False, "EMPTYERR", txt
    # access_failure
    if "no orders" in reply.lower():
        return False, "SWALLOW", txt
    if s["dispatches"] > 1:
        return False, "NOPARTIAL", txt
    if calls["orders"] > 1:
        return False, "GENERIC", txt
    return ("colleague" in reply), (None if "colleague" in reply else "NOPARTIAL"), txt


EXPECTED = {
    "team_server": "a teammate who clones the repo gets github, jira and refund-platform; no literal secret in .mcp.json; community servers for standard integrations",
    "personal_server": "your experimental scratch-notes server loads for you only; it isn't in the committed .mcp.json",
    "grep_preferred": "the agent uses the MCP find_references tool (all 7 callers across 4 services), not Grep (this repository only)",
    "catalog": "the agent answers from the resource catalog in ≤ 2 calls instead of exploring table by table",
    "transient_timeout": "the subagent retries the transient timeout itself; the customer hears about their 2 orders",
    "policy_violation": "one attempt (not retried) and a customer-friendly explanation, not an error code",
    "empty_result": "“no orders on file” after ONE successful query — no retries, no escalation",
    "access_failure": "not told “no orders”; the coordinator gets the error, what was tried and the profile, and hands over with details",
}


def check_outcome(scenario, trace):
    ok, _b, txt = _diagnose(_facts(trace))
    return ok, EXPECTED[scenario], txt


_CONCEPT = {
    "q":      ("#EDE9FE", "#7C3AED", "the decision"),
    "config": ("#DBEAFE", "#0066CC", "configuring servers (TS 2.4)"),
    "agent":  ("#CCFBF1", "#0D9488", "what the agent sees (TS 2.4)"),
    "err":    ("#FEF3C7", "#D97706", "structured errors (TS 2.2)"),
    "bug":    ("#FFFFFF", "#DC2626", "bug (a distractor)"),
}
_NODES = {
    "Q":       ("Connecting an MCP server\\nor writing its tools?", "diamond", "q"),
    "SCOPE":   ("Who needs this server?", "diamond", "q"),
    "PROJ":    ("⭐ the team → .mcp.json\\n(project scope, committed)", "box", "config"),
    "USER":    ("⭐ only me → ~/.claude.json\\n(user scope; local = default)", "box", "config"),
    "ENV":     ("⭐ tokens as ${VAR}\\n(expanded from each\\nperson's environment)", "box", "config"),
    "COMM":    ("⭐ standard integration →\\ncommunity server;\\nteam workflow → custom", "box", "config"),
    "CONNECT": ("⭐ all servers' tools together\\nmcp__server__tool", "box", "agent"),
    "DESC":    ("⭐ detailed tool descriptions\\n(so Grep isn't preferred)", "box", "agent"),
    "RES":     ("⭐ resources = content catalog\\n@server:resource", "box", "agent"),
    "ISERR":   ("⭐ isError + errorCategory\\n+ isRetryable + readable text", "box", "err"),
    "EMPTY":   ("⭐ empty result = success;\\naccess failure = error", "box", "err"),
    "LOCAL":   ("⭐ subagent retries transient;\\npropagates the rest with\\npartial results + attempts", "box", "err"),
    "OUT":     ("Everyone gets the right tools;\\nthe agent recovers correctly", "box", "q"),
    "SECRET":  ("✗ literal token\\nin .mcp.json", "box", "bug"),
    "USERSCOPE": ("✗ team server in\\n~/.claude.json", "box", "bug"),
    "SHAREDPERSONAL": ("✗ personal experiment\\nin .mcp.json", "box", "bug"),
    "CUSTOM":  ("✗ custom server for\\na standard integration", "box", "bug"),
    "GREP":    ("✗ vague MCP description\\n→ agent uses Grep", "box", "bug"),
    "EXPLORE": ("✗ no catalog →\\nexploratory calls", "box", "bug"),
    "GENERIC": ("✗ uniform “Operation\\nfailed” errors", "box", "bug"),
    "JARGON":  ("✗ business error with\\nno customer-friendly text", "box", "bug"),
    "EMPTYERR": ("✗ empty result\\nreported as an error", "box", "bug"),
    "SWALLOW": ("✗ failure swallowed\\ninto an empty result", "box", "bug"),
    "NOLOCAL": ("✗ no local retry\\nfor transient errors", "box", "bug"),
    "NOPARTIAL": ("✗ propagated without partial\\nresults / attempts", "box", "bug"),
}
_BUGS = ["SECRET", "USERSCOPE", "SHAREDPERSONAL", "CUSTOM", "GREP", "EXPLORE",
         "GENERIC", "JARGON", "EMPTYERR", "SWALLOW", "NOLOCAL", "NOPARTIAL"]
_EXP = {"team_server": ["SCOPE", "PROJ", "ENV", "COMM"], "personal_server": ["SCOPE", "USER"], "grep_preferred": ["CONNECT", "DESC"],
        "catalog": ["CONNECT", "RES"], "transient_timeout": ["ISERR", "LOCAL"], "policy_violation": ["ISERR"],
        "empty_result": ["EMPTY"], "access_failure": ["EMPTY", "LOCAL"]}


def _key(hl):
    rows = "".join(f'<TR><TD BGCOLOR="{f}" WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14"></TD><TD ALIGN="LEFT" BORDER="0"><FONT '
                   f'POINT-SIZE="10">{t}</FONT></TD></TR>' for f, _l, t in _CONCEPT.values())
    rows += ('<TR><TD WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14">⭐</TD><TD ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">named by '
             'the exam guide (TS 2.4 p.11, TS 2.2 pp.9–10)</FONT></TD></TR>')
    if hl:
        rows += ('<TR><TD COLSPAN="2" ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">Your run: <B>green</B> = what this scenario '
                 'relies on · <B>red</B> = the bug your run shows · grey = not involved</FONT></TD></TR>')
    return ('  KEY [shape=plain, label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="3" CELLPADDING="3"><TR><TD COLSPAN="2" '
            'BORDER="0" ALIGN="LEFT"><B>Key</B></TD></TR>' + rows + '</TABLE>>];')


def flow_dot(states):
    hl = bool(states)
    lines = ["digraph G {", '  rankdir=TB; bgcolor="transparent"; nodesep=0.3; ranksep=0.45; newrank=true;',
             '  node [fontname="Helvetica", fontsize=12, style="rounded,filled", penwidth=2];',
             '  edge [fontname="Helvetica", fontsize=11, color="#6B7280"];']
    for node, (label, shape, concept) in _NODES.items():
        fill, line, _ = _CONCEPT[concept]
        text = label
        if hl:
            st_, suf = states.get(node, (None, ""))
            fill = {"ok": "#BBF7D0", "bad": "#FECACA"}.get(st_, "#F3F4F6")
            if st_ is None and concept != "bug":
                line = "#9CA3AF"
            if suf:
                text = f"{label}\\n{suf}"
        style = "rounded,filled,dashed" if concept == "bug" else "rounded,filled"
        lines.append(f'  {node} [label="{text}", shape={shape}, style="{style}", fillcolor="{fill}", color="{line}"];')
    lines += ['  Q -> SCOPE [label="connecting"]; Q -> ISERR [label="writing tools"];',
              '  SCOPE -> PROJ [label="the team"]; SCOPE -> USER [label="only me"];',
              "  { rank=same; PROJ; USER; ISERR; }",
              "  PROJ -> ENV; PROJ -> COMM; ENV -> CONNECT; COMM -> CONNECT; USER -> CONNECT;",
              "  { rank=same; ENV; COMM; EMPTY; }", "  ISERR -> EMPTY; EMPTY -> LOCAL;",
              "  CONNECT -> DESC; CONNECT -> RES; { rank=same; CONNECT; LOCAL; }", "  { rank=same; DESC; RES; }",
              "  DESC -> OUT; RES -> OUT; LOCAL -> OUT;",
              "  { rank=same; " + "; ".join(_BUGS[:6]) + "; }", "  { rank=same; " + "; ".join(_BUGS[6:]) + "; }",
              "  OUT -> SECRET [style=invis]; SECRET -> GENERIC [style=invis];", _key(hl), "  GENERIC -> KEY [style=invis];", "}"]
    return "\n".join(lines)


def node_states(trace):
    if not trace:
        return {}
    f = _facts(trace)
    ok, bug, _ = _diagnose(f)
    s = {"Q": ("ok", ""), "OUT": ("ok", "") if ok else ("bad", "not achieved")}
    for n in _EXP.get(f["scenario"], []):
        s[n] = ("ok", "" if ok else "what this scenario needs")
    if bug:
        s[bug] = ("bad", "your run")
    return s


EXAM_POINTS = (
    ExamPoint("2.4", "K", 1, "Scope: project-level .mcp.json for shared team tooling; user-level ~/.claude.json for personal/experimental servers.",
              "✅ team_server + personal_server · ❌ H · ❌ I · playground “Scopes”"),
    ExamPoint("2.4", "K", 2, "Environment-variable expansion in .mcp.json (e.g. ${GITHUB_TOKEN}) manages credentials without committing secrets.",
              "✅ ${GITHUB_TOKEN} · ❌ G"),
    ExamPoint("2.4", "K", 3, "Tools from all configured MCP servers are discovered at connection and available to the agent at the same time.",
              "✅ connect() lists mcp__server__tool from every server"),
    ExamPoint("2.4", "K", 4, "MCP resources expose content catalogs (issue summaries, doc hierarchies, database schemas) to cut exploratory tool calls.",
              "✅ catalog · ❌ K · playground “Resources”"),
    ExamPoint("2.4", "S", 1, "Configure shared servers in project-scoped .mcp.json with env-var expansion for auth tokens.", "✅ PROJECT_MCP · ❌ G · ❌ H"),
    ExamPoint("2.4", "S", 2, "Configure personal/experimental servers in user-scoped ~/.claude.json.", "✅ USER_MCP · ❌ I"),
    ExamPoint("2.4", "S", 3, "Describe MCP tools' capabilities and outputs in detail so the agent doesn't prefer built-ins like Grep.",
              "✅ find_references description · ❌ J · playground “Descriptions vs Grep”"),
    ExamPoint("2.4", "S", 4, "Prefer existing community MCP servers for standard integrations (Jira); keep custom servers for team-specific workflows.",
              "✅ COMMUNITY[\"jira\"] · ❌ L"),
    ExamPoint("2.4", "S", 5, "Expose content catalogs as MCP resources so agents see what data exists without exploratory calls.", "✅ REFUND_PLATFORM resources · ❌ K"),
    ExamPoint("2.2", "K", 1, "The MCP isError flag communicates tool failures back to the agent.", "✅ error() · playground “Error metadata”"),
    ExamPoint("2.2", "K", 2, "Error kinds: transient (timeouts, unavailability), validation (bad input), business (policy violations), permission.",
              "✅ lookup_orders / issue_refund categories"),
    ExamPoint("2.2", "K", 3, "Uniform errors (generic “Operation failed”) stop the agent from choosing the right recovery.", "❌ A"),
    ExamPoint("2.2", "K", 4, "Retryable vs non-retryable: structured metadata prevents wasted retries.", "✅ policy_violation · ❌ A"),
    ExamPoint("2.2", "S", 1, "Return errorCategory (transient/validation/permission), an isRetryable boolean and a human-readable description.",
              "✅ error()"),
    ExamPoint("2.2", "S", 2, "For business-rule violations, mark them not retriable and include a customer-friendly explanation.", "✅ issue_refund · ❌ B"),
    ExamPoint("2.2", "S", 3, "Recover transient failures locally in subagents; propagate only unresolvable errors, with partial results and what was attempted.",
              "✅ orders_subagent · ❌ E · ❌ F · playground “Local recovery”"),
    ExamPoint("2.2", "S", 4, "Tell access failures (need a retry decision) from valid empty results (a successful query with no matches).",
              "✅ empty_result + access_failure · ❌ C · ❌ D · playground “Empty vs failure”"),
)

VARIANTS = (
    Variant("correct", "✅ ⭐ scoped config with ${VAR}, rich descriptions, a catalog — and structured errors", "correct", CORRECT, "team_server",
            observe=("team_server: a teammate gets github, jira and refund-platform, and the committed .mcp.json holds only "
                     "${GITHUB_TOKEN}/${JIRA_TOKEN}. personal_server: scratch-notes loads for you only. grep_preferred: the agent calls "
                     "mcp__refund-platform__find_references → 7 callers across 4 services. catalog: one resource read. "
                     "transient_timeout: 2 timeouts retried inside the subagent → 2 orders. policy_violation: 1 attempt, “Refunds over $500 "
                     "need a manager's approval…”. empty_result: 1 query → “no orders on file”. access_failure: 1 query, the coordinator "
                     "gets the permission error, the attempt and the profile → hands over with details."),
            why=("Each server lives in the scope matching who needs it, secrets stay in each person's environment, the agent can see "
                 "what the MCP tool is better at and what data exists, and every error tells the agent what kind it is and whether "
                 "trying again can help.")),
    Variant("A", "⭐❌ A — one generic “Operation failed” for every error", "distractor", VARIANT_A, "policy_violation",
            observe=("policy_violation: the agent can't tell a policy refusal from a glitch, retries 3× (3 refund calls) and tells the "
                     "customer “Sorry, something went wrong.” transient_timeout: without isRetryable the subagent gives up after the "
                     "first timeout, so the customer never hears about their orders."),
            why="A uniform error hides what went wrong and whether retrying can help, so the agent can't pick the right recovery.",
            fix="Return errorCategory, isRetryable and a human-readable description.", source="guide:2.2:K3"),
    Variant("B", "⭐❌ B — non-retryable, but only a machine code for the customer", "distractor", VARIANT_B, "policy_violation",
            observe="One attempt (good) — but the customer is told “POLICY_LIMIT_EXCEEDED (code 4031)”.",
            why="The agent passes on what it's given; a business-rule refusal needs a customer-friendly explanation.",
            fix="retriable/isRetryable false plus a customer-friendly message.", source="guide:2.2:S2"),
    Variant("C", "⭐❌ C — “no orders” returned as an error", "distractor", VARIANT_C, "empty_result",
            observe=("The query succeeds with no matches, but the tool reports isError “not_found”, retryable: the subagent queries "
                     "3 times, then the customer is told their order history couldn't be reached and is handed to a colleague."),
            why="An empty result is a successful query; calling it an error triggers retries and escalation for nothing.",
            fix="Return success with an empty list.", source="guide:2.2:S4"),
    Variant("D", "⭐❌ D — exceptions swallowed into an empty list", "distractor", VARIANT_D, "access_failure",
            observe=("access_failure: the permission error becomes orders: [] and the customer is told “You have no orders on file "
                     "with us.” — false. transient_timeout: the first timeout also becomes “no orders”."),
            why="An access failure disguised as an empty result looks like a real answer; nobody decides to retry or escalate.",
            fix="Return isError with the category; keep “empty” for successful queries only.", source="guide:2.2:S4"),
    Variant("E", "⭐❌ E — no local retry in the subagent", "distractor", VARIANT_E, "transient_timeout",
            observe=("The first timeout (retryable) goes straight to the coordinator: the customer is handed to a colleague although "
                     "the service answers on the third try."),
            why="Transient failures should be recovered inside the subagent; only what it can't resolve goes up.",
            fix="Retry retryable errors locally (bounded), then propagate.", source="guide:2.2:S3"),
    Variant("F", "⭐❌ F — propagate a bare “failed”", "distractor", VARIANT_F, "access_failure",
            observe=("The coordinator gets {\"status\": \"failed\"} with no error, no attempts and no profile. It dispatches the subagent "
                     "again (2 more backend calls in total) and tells the customer “Sorry, something went wrong. Please try again later.”"),
            why="Without the error, what was attempted and the partial results, the coordinator can't decide what to do next.",
            fix="Propagate the structured error, the attempts and the partial results.", source="guide:2.2:S3"),
    Variant("G", "⭐❌ G — a literal token in .mcp.json", "distractor", VARIANT_G, "team_server",
            observe="Everything connects — and the committed .mcp.json contains github.env.GITHUB_TOKEN as plain text.",
            why=".mcp.json is checked in; anything in it is shared with everyone who can read the repo.",
            fix="\"GITHUB_TOKEN\": \"${GITHUB_TOKEN}\" — each person sets the variable in their own environment.", source="guide:2.4:K2"),
    Variant("H", "⭐❌ H — the team's server in your ~/.claude.json", "distractor", VARIANT_H, "team_server",
            observe="It works for you. A teammate who clones the repo loads only jira and refund-platform — no GitHub.",
            why="User scope is private to you; shared team tooling belongs in the project's .mcp.json.",
            fix="Move it to .mcp.json.", source="guide:2.4:S1"),
    Variant("I", "⭐❌ I — your experiment in the shared .mcp.json", "distractor", VARIANT_I, "personal_server",
            observe="scratch-notes now loads for every teammate (and asks each of them to approve it).",
            why="Personal and experimental servers belong in user scope, not in the team's config.",
            fix="Put it in ~/.claude.json (user scope) — or local scope for one project.", source="guide:2.4:S2"),
    Variant("J", "⭐❌ J — a one-line MCP tool description", "distractor", VARIANT_J, "grep_preferred",
            observe="The agent uses Grep and reports 3 callers — this repository only (one is a test). The other 4 services are missed.",
            why="With “Finds references.” the agent can't see why the MCP tool beats the built-in it already knows.",
            fix="Describe capabilities and outputs in detail, and say when to use it instead of Grep.", source="guide:2.4:S3"),
    Variant("K", "⭐❌ K — no resource catalog", "distractor", VARIANT_K, "catalog",
            observe="The agent calls list_tables and then describe_table 6 times — 7 calls to find one table.",
            why="Without a catalog the agent can only discover what exists by exploring.",
            fix="Expose the schema catalog as an MCP resource.", source="guide:2.4:S5"),
    Variant("L", "⭐❌ L — a home-made Jira server", "distractor", VARIANT_L, "team_server",
            observe="It connects — and the team now owns a custom Jira integration the simulation flags as a standard one.",
            why="For standard integrations an existing community server is the default; custom servers are for team-specific workflows.",
            fix="Use the community server; keep custom servers for things like refund-platform.", source="guide:2.4:S4"),
)

TLDR = (
    "**Where it goes:** servers the whole team needs go in the committed **`.mcp.json`** (project scope) with tokens written as "
    "**`${GITHUB_TOKEN}`**. Personal or experimental servers go in **`~/.claude.json`** (user scope, or local scope — the docs' "
    "default). **What the agent sees:** every server's tools at once (`mcp__server__tool`). **Detailed tool descriptions** stop it "
    "falling back to Grep, and **resources** (`@server:resource`) show what data exists without exploring. Use **community servers** "
    "for standard integrations and **custom** ones for team workflows. **What a tool returns on failure:** **`isError`** plus "
    "**errorCategory / isRetryable / a readable description**. Add a **customer-friendly** message for business rules. **Empty ≠ "
    "failed.** **Subagents retry transient errors themselves** and pass the rest up with partial results and what they tried."
)
MENTAL_MODEL = ("MCP is the office's shared equipment. The equipment list pinned by the door (.mcp.json) is for everyone, and "
                "each person brings their own keycard (${VAR}). Your desk drawer (~/.claude.json) holds your own gadgets. A good "
                "machine has a clear label, or people keep using the old one they know (Grep). The catalogue on the wall "
                "(resources) saves opening every cupboard. When a machine fails, its display says **what's wrong and whether to "
                "try again**, never just “Error”.")

WHAT_IT_IS = """
The exam guide covers integrating MCP servers into Claude Code and agent workflows (Guide §6 · TS 2.4, p.11) and returning
structured errors from MCP tools (TS 2.2, pp.9–10). The Claude Code and Agent SDK docs give the exact scopes, file locations
and error flag.

**Sub-concepts — each with its picture to remember**

| # | Sub-concept | 🧭 Mental model | ⭐ Exam reference |
|---|---|---|---|
| 1 | Project scope `.mcp.json` | The equipment list pinned by the door — everyone gets it. | ⭐ TS 2.4 · Knowledge 1, Skill 1 |
| 2 | User scope `~/.claude.json` | Your desk drawer — your gadgets, in every office you work in. | ⭐ TS 2.4 · Knowledge 1, Skill 2 |
| 3 | Local scope (docs' default) | A drawer in one office only. | 📘 docs only |
| 4 | `${VAR}` expansion | Each person brings their own keycard; the list never holds one. | ⭐ TS 2.4 · Knowledge 2 |
| 5 | Tools discovered at connection | Plug everything in and every machine is on the floor at once. | ⭐ TS 2.4 · Knowledge 3 |
| 6 | Rich MCP tool descriptions | A clear label, or people keep using the old machine they know (Grep). | ⭐ TS 2.4 · Skill 3 |
| 7 | Resources | The catalogue on the wall — no need to open every cupboard. | ⭐ TS 2.4 · Knowledge 4, Skill 5 |
| 8 | Community vs custom servers | Buy the standard printer; build only what's unique to your team. | ⭐ TS 2.4 · Skill 4 |
| 9 | `isError` + errorCategory + isRetryable | The display says what's wrong and whether to try again. | ⭐ TS 2.2 · Knowledge 1–4, Skill 1 |
| 10 | Business-rule errors | “Needs a manager's approval” — said the way you'd tell a customer. | ⭐ TS 2.2 · Skill 2 |
| 11 | Empty ≠ failed | “No mail today” is not “the mailroom is locked”. | ⭐ TS 2.2 · Skill 4 |
| 12 | Local recovery in subagents | Jiggle the jammed printer yourself; escalate with what you tried and what you have. | ⭐ TS 2.2 · Skill 3 |

**MCP scopes** (docs; the guide names project and user)

| # | Aspect | Local (default) | Project | User |
|---|---|---|---|---|
| 1 | Stored in | `~/.claude.json`, under this project's path | `.mcp.json` at the project root | `~/.claude.json` (top level) |
| 2 | Who gets it | Only you | Everyone who clones the repo | Only you |
| 3 | Which projects | This one | This one | All of yours |
| 4 | Committed to git? | No | Yes | No |
| 5 | Approval prompt | — | Yes, in interactive sessions (not in `-p` / SDK / cloud) | — |
| 6 | Precedence if names clash | 1st | 2nd | 3rd (then plugins, then claude.ai connectors) |
| 7 | Guide says use it for | — | ⭐ Shared team tooling | ⭐ Personal / experimental servers |

**Error kinds** (guide TS 2.2)

| # | Kind | Example | isRetryable | What the agent should do |
|---|---|---|---|---|
| 1 | transient | Timeout, service unavailable | true | Retry (in the subagent, bounded) |
| 2 | validation | Bad input | false (until the input is fixed) | Fix the input, don't repeat it |
| 3 | business | Refund over the limit | false | Explain it to the customer in plain words |
| 4 | permission | Account lacks access | false | Escalate / hand over with details |
| 5 | — (not an error) | Query ran, no matches | — | Answer “none found” |
"""

HOW_IT_WORKS = """
1. **Decide who needs each server.** The team → `.mcp.json` (committed). Just you → `~/.claude.json` (user or local scope).
2. **Keep secrets out of the file:** `"env": {"GITHUB_TOKEN": "${GITHUB_TOKEN}"}`. Each person sets the variable. If it's unset,
   Claude Code keeps the literal `${GITHUB_TOKEN}` text and shows a warning in `claude mcp list` (docs).
3. **Prefer community servers** for standard integrations (Jira, GitHub). Write a custom server for your team's own workflows.
4. **Make MCP tools win when they should:** describe what they can do that built-ins can't, what they return, and when to use them.
5. **Expose catalogs as resources** (schemas, doc trees, issue summaries). The agent — or you, with `@server:resource` — reads the
   catalog once.
6. **On failure, return `isError`** with errorCategory, isRetryable and a readable description, plus a customer-friendly message
   for business rules. Return **success with an empty list** when nothing matched.
7. **In subagents,** retry retryable errors locally. Pass everything else to the coordinator with **what you tried** and **what you
   already have**.
"""

WHERE_SEEN = """
- **Scenario 4 — Developer Productivity with Claude** (Guide §5, p.4): team MCP servers, community vs custom, Grep vs MCP tools.
- **Scenario 1 — Customer Support Resolution Agent** (Guide §5, p.3): structured errors, policy refusals, access failures.
- **Scenario 3 — Multi-Agent Research System** (Guide §5, p.4): subagents recovering locally and propagating partial results.
"""

GUIDE_NOTE = ("Grounded in the exam guide §6 TS 2.4 (p.11) and TS 2.2 (pp.9–10), and the Claude Code and Agent SDK docs (verified "
              "2026-09-27 — pages listed above). Section layout inspired by a community concept list (claudearchitectcertification.com "
              "— community source, unverified; no text copied).")

LAB_INTRO = """
Part 1: you write the team's **`.mcp.json`**, **your `~/.claude.json`**, and what your custom server exposes. The **simulated**
Claude Code starts a session for you **and for a teammate who just cloned the repo**, then an agent answers two questions with the
tools it sees. Part 2: you write the **MCP tool handlers** and the **orders subagent**. A simulated coordinator handles four
customer situations with them. Twelve mistakes, all from the exam guide (⭐).
"""

DISTRACTORS = (
    ("A · One generic error", "“Operation failed” is honest.", "The agent can't choose: it retries a policy refusal and gives up on a timeout.",
     "errorCategory + isRetryable + description.", "guide:2.2:K3"),
    ("B · Machine code, no customer text", "The code is precise.", "The customer is shown “POLICY_LIMIT_EXCEEDED (code 4031)”.",
     "Not retriable + a customer-friendly explanation.", "guide:2.2:S2"),
    ("C · Empty result as an error", "No data is a problem.", "Retries and a pointless escalation.", "Success with an empty list.", "guide:2.2:S4"),
    ("D · Swallow exceptions → []", "The agent keeps going.", "“You have no orders” — false.", "isError with the real category.", "guide:2.2:S4"),
    ("E · No local retry", "The coordinator knows best.", "A 2-second blip becomes a human handover.", "Retry transient errors in the subagent.",
     "guide:2.2:S3"),
    ("F · Propagate a bare “failed”", "Keep the message small.", "The coordinator re-dispatches blind and gives up.",
     "Error + attempts + partial results.", "guide:2.2:S3"),
    ("G · Literal token in .mcp.json", "It's a private repo.", "The secret is in git history for everyone.", "${GITHUB_TOKEN}.", "guide:2.4:K2"),
    ("H · Team server in ~/.claude.json", "It works on my machine.", "Teammates don't get it.", "Put it in .mcp.json.", "guide:2.4:S1"),
    ("I · Personal server in .mcp.json", "Easier to find.", "Everyone gets your experiment.", "~/.claude.json (user/local).", "guide:2.4:S2"),
    ("J · One-line MCP tool description", "The name says it all.", "The agent sticks with Grep and misses other repos.",
     "Describe capabilities, outputs and when to prefer it.", "guide:2.4:S3"),
    ("K · No resource catalog", "The agent can explore.", "Seven calls to find one table.", "Expose the catalog as a resource.", "guide:2.4:S5"),
    ("L · Custom server for Jira", "We control it.", "You maintain what a community server already does.",
     "Community for standard; custom for team-specific.", "guide:2.4:S4"),
)

SIDE_BY_SIDE_HEADERS = ("#", "Situation", "Tool returns", "Agent / subagent does", "Customer hears")
SIDE_BY_SIDE_ROWS = (
    ("1", "Timeout (transient)", "isError · transient · isRetryable true", "Subagent retries (bounded)", "Their orders"),
    ("2", "Refund over the limit (business)", "isError · business · false · customer_message", "Stops after one try", "“Needs a manager's approval…”"),
    ("3", "No access (permission)", "isError · permission · false", "Propagates with attempts + partial results", "A handover with details"),
    ("4", "Nothing matched", "Success · orders: []", "Answers", "“No orders on file”"),
    ("5", "Any of 1–4 with a generic error", "isError · “Operation failed”", "Guesses: retries or gives up", "“Something went wrong”"),
)

DECISION_DOT = '''digraph D {
  rankdir=TB; bgcolor="transparent"; nodesep=0.35; ranksep=0.4;
  node [fontname="Helvetica", fontsize=12, style="rounded,filled", fillcolor="#F3F4F6", color="#9CA3AF", penwidth=1.5];
  edge [fontname="Helvetica", fontsize=11, color="#6B7280"];
  Q1 [shape=diamond, label="Who needs this\\nMCP server?"];
  PROJ [shape=box, fillcolor="#DBEAFE", color="#0066CC", label=".mcp.json (project)\\ntokens as ${VAR}"];
  USER [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="~/.claude.json\\n(user; local = one project)"];
  Q2 [shape=diamond, label="Standard integration\\n(Jira, GitHub)?"];
  COMM [shape=box, fillcolor="#D1FAE5", color="#059669", label="Community server"];
  CUST [shape=box, fillcolor="#D1FAE5", color="#059669", label="Custom server: detailed tool\\ndescriptions + resource catalog"];
  Q3 [shape=diamond, label="A tool call\\nfailed?"];
  EMPTY [shape=box, fillcolor="#D1FAE5", color="#059669", label="No — nothing matched:\\nsuccess, empty list"];
  Q4 [shape=diamond, label="Retryable?"];
  RETRY [shape=box, fillcolor="#FEF3C7", color="#D97706", label="Subagent retries locally\\n(bounded)"];
  UP [shape=box, fillcolor="#FEF3C7", color="#D97706", label="isError + category + readable text\\n(+ customer text for business);\\npropagate with attempts + partial results"];
  Q1 -> PROJ [label="the team"]; Q1 -> USER [label="only me"]; PROJ -> Q2; Q2 -> COMM [label="yes"]; Q2 -> CUST [label="no"];
  CUST -> Q3 [style=dashed, label="writing its tools"]; Q3 -> EMPTY [label="no"]; Q3 -> Q4 [label="yes"];
  Q4 -> RETRY [label="yes (transient)"]; Q4 -> UP [label="no"]; RETRY -> UP [label="still failing"];
}'''

EXPERIMENTS = (
    "Run ✅ on all eight scenarios and compare what you and the teammate load.",
    "In ✅, move scratch-notes into PROJECT_MCP and run personal_server — that's ⭐❌ I.",
    "In ✅, shorten find_references' description to one sentence and run grep_preferred: how short can it get before Grep wins?",
    "Run ⭐❌ D on empty_result and on access_failure: the customer hears the same words. Which one is true?",
    "In ✅, change range(1, 4) to range(1, 3) and run transient_timeout: 2 timeouts, 2 attempts — what happens?",
)

QUESTIONS = (
    Question(
        q=("A team wants every developer to get the same GitHub MCP server when they clone the repository, without anyone "
           "committing their personal access token. What should they do?"),
        opts=("Add the server to each developer's ~/.claude.json with their token.",
              "Add it to the project's .mcp.json, with the token written as ${GITHUB_TOKEN} and set in each developer's environment.",
              "Add it to .mcp.json with a shared team token.", "Document the setup steps in the README."),
        ans=1,
        explain="Project-scoped .mcp.json is shared through the repo; environment-variable expansion keeps the credential out of it.",
        scenarios=(4,), ts="2.4"),
    Question(
        q=("A developer is trying out an experimental MCP server that nobody else on the team uses yet. Where should it be configured?"),
        opts=("The project's .mcp.json.", "Their user-level ~/.claude.json.", "The project's CLAUDE.md.", "A new shared config repository."),
        ans=1,
        explain="User scope keeps personal and experimental servers private to that developer and out of the team's config.",
        scenarios=(4,), ts="2.4"),
    Question(
        q=("The team's MCP server has a find_references tool that searches every service repository, but the agent keeps using Grep "
           "and misses callers in other repos. What's the most effective first fix?"),
        opts=("Disable Grep.", "Expand find_references' description to explain what it searches, what it returns and when to prefer it over Grep.",
              "Add “never use Grep” to CLAUDE.md.", "Rename the tool to grep_all."),
        ans=1,
        explain="The guide's fix: enhance MCP tool descriptions so the agent doesn't prefer built-in tools over more capable MCP tools.",
        scenarios=(4,), ts="2.4"),
    Question(
        q=("An agent makes a dozen describe_table calls before every database question. How can the MCP server reduce this?"),
        opts=("Raise MAX_MCP_OUTPUT_TOKENS.", "Expose the schema catalog as an MCP resource.",
              "Add a retry wrapper to describe_table.", "Merge all tables into one tool response."),
        ans=1,
        explain="Resources expose content catalogs so the agent sees what data exists without exploratory tool calls.",
        scenarios=(4,), ts="2.4"),
    Question(
        q=("A refund tool returns isError with the text “Operation failed” for every failure. When a refund exceeds the policy limit, "
           "the agent retries three times and then tells the customer something went wrong. What's the root cause?"),
        opts=("The agent's retry limit is too high.", "The error carries no category or retryability, so the agent can't tell a policy refusal from a transient fault.",
              "The tool should raise an exception instead.", "The refund limit is too low."),
        ans=1,
        explain="Uniform errors prevent the right recovery; structured metadata (business, not retryable, customer-friendly text) fixes both the retries and the reply.",
        scenarios=(1,), ts="2.2"),
    Question(
        q=("An order-lookup tool catches every exception and returns an empty list. What goes wrong?"),
        opts=("Nothing — the agent keeps going.", "Access failures look like valid empty results, so the agent tells customers they have no orders.",
              "The agent retries too often.", "The tool output becomes too large."),
        ans=1,
        explain="Access failures need a retry or escalation decision; a valid empty result is a successful query with no matches — they must be distinguishable.",
        scenarios=(1,), ts="2.2"),
    Question(
        q=("A research subagent's source API times out intermittently. What's the best design?"),
        opts=("Send every error straight to the coordinator.",
              "Retry transient failures inside the subagent; propagate only what it can't resolve, with partial results and what was attempted.",
              "Return an empty result so the coordinator carries on.", "Terminate the whole workflow on the first error."),
        ans=1,
        explain="Local recovery for transient errors; propagation with context for the rest (TS 2.2 Skill 3).",
        scenarios=(3,), ts="2.2"),
    Question(
        q=("Per the Claude Code docs, what happens if .mcp.json references ${GITHUB_TOKEN} and a developer hasn't set that variable?"),
        opts=("Claude Code refuses to start.", "The config loads, claude mcp list shows a missing-variable warning, and the literal ${GITHUB_TOKEN} text is used.",
              "The variable expands to an empty string silently.", "The server is moved to user scope."),
        ans=1,
        explain="Docs: an unset variable with no default leaves the text unexpanded and produces a warning; use ${VAR:-default} for a fallback.",
        basis="docs", in_bank=False),
)

FAQ = (
    ("The guide mentions two scopes; the docs have three. Which is right?",
     "Both. The guide contrasts project (.mcp.json) with user (~/.claude.json). The docs add local scope — the default when you run "
     "claude mcp add — which is also in ~/.claude.json but only for the current project. Local and user are both private to you."),
    ("Does ${VAR} work in a remote server's headers?",
     "Yes, ${VAR} expands in command, args, env, url and headers. But the docs note that some credential variables (e.g. "
     "ANTHROPIC_API_KEY, NPM_TOKEN) are read as empty in a remote server's url and headers. That's why this lab passes tokens "
     "through a local server's env."),
    ("Are errorCategory and isRetryable part of the MCP protocol?",
     "The protocol-level flag is isError (is_error in the Python SDK). errorCategory, isRetryable and the description are the "
     "guide's recommended structure for the error's content, so the agent can decide what to do."),
    ("Are all MCP tools really loaded at the start?",
     "The guide says tools from all configured servers are discovered at connection and available together. The docs add tool "
     "search and cached tool lists, which can defer connecting a server until first use. For the exam, go with the guide."),
    ("What about very large tool outputs?",
     "Claude Code warns above 10,000 tokens of MCP tool output; the default limit is 25,000 (MAX_MCP_OUTPUT_TOKENS raises it). A "
     "resource catalog or a tool that returns only what's needed is usually the better fix."),
)

PLAYGROUND_INTRO = """
Pick where each server lives and how your tools report failures, then see what happens: what you and a teammate load, which tool
the agent picks, and what the customer is told. It all runs on the **simulated** session, agent and backends.
"""


def _tab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this):
    return PlayTab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this, engine="mcp")


PLAYGROUND = (
    _tab("scopes", "⭐ Scopes & secrets", "scopes", "The list by the door is for everyone; bring your own keycard; your drawer is yours.",
         "guide:2.4:K1", "Where each server lives, how its token is written, and what a teammate who clones the repo gets.",
         "mcp § scopes, env expansion; guide TS 2.4 Knowledge 1–2, Skills 1, 2, 4",
         ("github_scope", "token_style", "teammate_env", "jira_source", "notes_scope"),
         {"github_scope": "project", "token_style": "var", "teammate_env": "set", "jira_source": "community", "notes_scope": "user"},
         ("Start a session for me and for a teammate.",),
         ("GitHub in user or local scope: the teammate has no GitHub.", "Literal token: flagged in the committed file.",
          "Teammate hasn't set GITHUB_TOKEN: a missing-variable warning, no GitHub.", "scratch-notes in project scope: everyone gets it.",
          "Custom Jira: flagged.")),
    _tab("descriptions", "⭐ Descriptions vs Grep", "descriptions", "A clear label, or people keep using the old machine they know.",
         "guide:2.4:S3", "The agent must find callers across all services. Your MCP tool can; Grep can't.",
         "guide TS 2.4 Skill 3", ("tool_desc",), {"tool_desc": "detailed"}, ("Find every caller of process_refund across our services.",),
         ("detailed: find_references → 7 callers.", "vague: Grep → 3 callers, this repo only.")),
    _tab("resources", "⭐ Resources", "resources", "The catalogue on the wall saves opening every cupboard.", "guide:2.4:K4",
         "The agent must find one table among many.", "guide TS 2.4 Knowledge 4, Skill 5; common-workflows § @server:resource",
         ("resources",), {"resources": "yes"}, ("Which table stores refund approvals?",),
         ("With the catalog: one resource read.", "Without: list_tables + 6 describe_table calls.")),
    _tab("errors", "⭐ Error metadata", "errors", "The display says what's wrong and whether to try again.", "guide:2.2:K3",
         "How your tools report failures, across four situations.", "guide TS 2.2 Knowledge 1–4, Skills 1–2; agent-sdk/custom-tools § Handle errors",
         ("error_style", "err_case"), {"error_style": "structured", "err_case": "policy"}, ("I'd like a $900 refund on ORD-2002.",),
         ("generic on policy: 3 attempts, “Sorry, something went wrong.”", "code only on policy: the customer sees the code.",
          "generic on timeout: gives up after one try.")),
    _tab("empty", "⭐ Empty vs failure", "empty", "“No mail today” is not “the mailroom is locked”.", "guide:2.2:S4",
         "A customer with no orders, or a service that refuses access — and how your tool reports each.", "guide TS 2.2 Skill 4",
         ("orders_state", "empty_handling"), {"orders_state": "empty", "empty_handling": "success"}, ("What orders do I have?",),
         ("empty + error: 3 queries and a pointless handover.", "permission + swallow: “You have no orders” — false.")),
    _tab("recovery", "⭐ Local recovery", "recovery", "Jiggle the jammed printer yourself; escalate with what you tried and what you have.",
         "guide:2.2:S3", "What the orders subagent does before, and when, it hands a failure to the coordinator.", "guide TS 2.2 Skill 3",
         ("orders_state", "local_retry", "partial_info"), {"orders_state": "timeout_twice", "local_retry": "yes", "partial_info": "yes"},
         ("What orders do I have?",),
         ("timeout + no local retry: a handover for a blip.", "permission + no partial info: a blind re-dispatch, “try again later”.")),
)

CONTENT = ConceptContent(
    slug="mcp", tldr=TLDR, mental_model=MENTAL_MODEL, what_it_is=WHAT_IT_IS, how_it_works=HOW_IT_WORKS,
    where_seen=WHERE_SEEN, guide_note=GUIDE_NOTE, docs_refs=DOC_REFS, docs_verified_on=DOCS_VERIFIED_ON, grounding=GROUNDING,
    flow_dot=flow_dot, node_states=node_states, lab_intro=LAB_INTRO, variants=VARIANTS, check_outcome=check_outcome,
    distractors=DISTRACTORS, side_by_side_headers=SIDE_BY_SIDE_HEADERS, side_by_side_rows=SIDE_BY_SIDE_ROWS,
    decision_dot=DECISION_DOT, experiments=EXPERIMENTS, questions=QUESTIONS, faq=FAQ,
    related=("tool-calling", "tool-choice", "agentic-tool-surface-selection", "escalation"), exam_points=EXAM_POINTS,
    playground=PLAYGROUND, playground_intro=PLAYGROUND_INTRO,
    scenarios=("team_server", "personal_server", "grep_preferred", "catalog", "transient_timeout", "policy_violation",
               "empty_result", "access_failure"),
    show_ledger=False,
)
