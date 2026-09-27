"""
D1.5 Human-in-the-Loop Escalation — guide TS 5.2 (escalation triggers and ambiguity resolution; pp.20–21) and TS 1.4
(programmatic enforcement vs prompt guidance, structured handoffs; p.7).

GROUNDING (CLAUDE.md, user rules 2026-09-26): the guide decides WHAT is examinable (read from the PDF on 2026-09-27); the
official docs support the mechanisms — explicit instructions with examples, deterministic hooks vs advisory instructions,
PreToolUse deny, escalation accuracy as a support-agent metric (fetched 2026-09-27, DOC_REFS). Every claim is in GROUNDING
with its source type. The escalation criteria themselves are the guide's; the docs don't define escalation rules.
Paraphrased; no real exam question reproduced.
"""

from utils.concept_types import Claim, ConceptContent, DocRef, ExamPoint, PlayTab, Question, Variant

DOCS_VERIFIED_ON = "2026-09-27"
_P = "https://platform.claude.com/docs/en"
_C = "https://code.claude.com/docs/en"

DOC_REFS = (
    DocRef("Customer support agent (use-case guide)", f"{_P}/about-claude/use-case-guides/customer-support-chat"),
    DocRef("Prompting best practices — use examples, add context", f"{_P}/build-with-claude/prompt-engineering/claude-prompting-best-practices"),
    DocRef("Intercept and control agent behavior with hooks (Agent SDK)", f"{_C}/agent-sdk/hooks"),
    DocRef("Best practices for Claude Code — set up hooks", f"{_C}/best-practices"),
)

GROUNDING = (
    Claim("Escalation triggers: the customer asks for a human; a policy exception or gap (not merely a complex case); the agent "
          "cannot make meaningful progress.", "guide", "TS 5.2 · Knowledge 1 · pp.20–21"),
    Claim("Escalate immediately when the customer explicitly demands a human; offer to resolve when the issue is straightforward.",
          "guide", "TS 5.2 · Knowledge 2 · pp.20–21"),
    Claim("Sentiment-based escalation and the model's self-reported confidence are unreliable proxies for how complex a case "
          "actually is.", "guide", "TS 5.2 · Knowledge 3 · pp.20–21"),
    Claim("Multiple customer matches call for clarification (ask for another identifier), not heuristic selection.",
          "guide", "TS 5.2 · Knowledge 4, Skill 5 · pp.20–21"),
    Claim("Skills: explicit escalation criteria with few-shot examples in the system prompt; honour explicit requests for a human "
          "at once without investigating first; acknowledge frustration and offer resolution, escalating only if the customer "
          "repeats the request; escalate when policy is ambiguous or silent (e.g. competitor price matching when the policy only "
          "covers own-site adjustments).", "guide", "TS 5.2 · Skills 1–4 · pp.20–21"),
    Claim("Programmatic enforcement (hooks, prerequisite gates) differs from prompt guidance; when compliance must be "
          "deterministic — e.g. identity verification before a financial operation — prompt instructions alone have a non-zero "
          "failure rate.", "guide", "TS 1.4 · Knowledge 1–2 · p.7"),
    Claim("Implement prerequisites that block downstream tool calls until the prerequisite has completed (e.g. block "
          "process_refund until get_customer returned a verified customer id).", "guide", "TS 1.4 · Skill 1 · p.7"),
    Claim("Structured handoffs for mid-process escalation carry customer details, root cause and recommended actions — customer "
          "id, root cause, refund amount, recommended action — because the human agent has no access to the transcript.",
          "guide", "TS 1.4 · Knowledge 3, Skill 3 · p.7"),
    Claim("Examples are one of the most reliable ways to steer Claude; make them relevant, diverse and structured (wrap them in "
          "<example> / <examples> tags); 3–5 examples are suggested. Explaining why an instruction matters helps.",
          "docs", "claude-prompting-best-practices § Use examples effectively; Add context to improve performance"),
    Claim("The support-agent guide recommends adding several sample \"good\" interactions to the prompt and measuring escalation "
          "accuracy — the share of conversations correctly escalated vs those that should have been but weren't (it suggests "
          "aiming for 95% or higher).", "docs", "customer-support-chat § examples; success criteria (Escalation efficiency)"),
    Claim("Hooks are deterministic and guarantee the action happens, whereas CLAUDE.md instructions are advisory.",
          "docs", "code.claude.com best-practices § Set up hooks"),
    Claim("A PreToolUse hook can deny a tool call (permissionDecision \"deny\" with a permissionDecisionReason that tells the model "
          "why, so it avoids retrying); deny takes priority over other decisions.", "docs", "agent-sdk/hooks § outputs, examples"),
    Claim("The lab's gate is plain Python around the tool call, standing in for a PreToolUse hook; the BLOCKED message plays the "
          "role of the deny reason.", "recommendation", "agent-sdk/hooks (mechanism); guide TS 1.4 Skill 1 (pattern)"),
    Claim("The simulated support agent follows its system prompt by keyword, skips verification when a customer says “skip the "
          "checks” (a scripted instance of the non-zero failure rate), reports confidence 0.55 on angry messages and 0.92 otherwise, "
          "and the customers, orders and policy texts are invented (example.com).",
          "simulated", "utils/mock_claude.py (_support_agent); utils/support_lab.py"),
)

# ── Lab code ───────────────────────────────────────────────────────────────────

CORRECT = r'''import json

from utils.mock_claude import MockClaude          # SIMULATED stand-in for the Claude API
from utils.support_lab import FIRST_MESSAGE, TOOLS, execute_tool, next_customer_message

client = MockClaude()

# Explicit escalation criteria + few-shot examples in the system prompt
SYSTEM = """ROLE: support agent. Resolve customer issues within policy.
<escalation_criteria>
Call escalate_to_human when ANY of these applies:
1. The customer asks for a human -> escalate immediately, before investigating anything.
2. The policy is ambiguous or silent on what the customer asks for -> escalate.
3. You cannot make meaningful progress (tools keep failing) -> escalate.
Do not escalate just because the customer is frustrated: acknowledge it and offer to resolve; escalate only if they then
ask for a human again.
If a customer lookup returns more than one match, ask for another identifier (email or order number) - never guess.
The human agent cannot see this conversation: fill every field of escalate_to_human.
</escalation_criteria>
<examples>
<example>"Get me a manager now." -> escalate_to_human at once.</example>
<example>"Third damaged kettle, I'm furious!" (refund within policy) -> apologise, verify, offer the refund.</example>
<example>"Will you match Competitor X's price?" (policy covers only our own price drops) -> escalate_to_human.</example>
</examples>"""

VERIFIED = set()   # customers confirmed by get_customer (exactly one match)


def run_tool(name, args):
    # Programmatic prerequisite: enforced in CODE, so it holds even when the model skips a step
    if name == "process_refund" and args.get("customer_id") not in VERIFIED:
        return "BLOCKED: process_refund needs a customer verified by get_customer first."
    result = execute_tool(name, args)
    if name == "get_customer" and result.startswith("{"):
        VERIFIED.add(json.loads(result)["customer_id"])
    return result


print("CUSTOMER:", FIRST_MESSAGE)
messages = [{"role": "user", "content": FIRST_MESSAGE}]
for turn in range(1, 15):
    r = client.messages.create(model="mock-claude", max_tokens=1024, system=SYSTEM, tools=TOOLS, messages=messages)
    if r.stop_reason == "tool_use":
        messages.append({"role": "assistant", "content": r.content})
        results = []
        for b in r.content:
            if b.type == "tool_use":
                out = run_tool(b.name, b.input)
                print(f"   {b.name}({b.input}) -> {out[:90]}")
                results.append({"type": "tool_result", "tool_use_id": b.id, "content": out})
        messages.append({"role": "user", "content": results})
        continue
    if r.stop_reason == "end_turn":
        print("AGENT:", "".join(b.text for b in r.content if b.type == "text"))
        reply = next_customer_message()
        if reply is None:
            break
        print("CUSTOMER:", reply)
        messages.append({"role": "assistant", "content": r.content})
        messages.append({"role": "user", "content": reply})
        continue
    raise RuntimeError(f"unhandled stop_reason: {r.stop_reason}")
else:
    raise RuntimeError("no resolution within 14 turns")
'''


def _swap(code: str, old: str, new: str) -> str:
    assert old in code, f"lab code changed, cannot apply variant edit: {old[:60]!r}"
    return code.replace(old, new, 1)


_FRUSTRATION = '''Do not escalate just because the customer is frustrated: acknowledge it and offer to resolve; escalate only if they then
ask for a human again.
'''
_RULES_123 = '''1. The customer asks for a human -> escalate immediately, before investigating anything.
2. The policy is ambiguous or silent on what the customer asks for -> escalate.
3. You cannot make meaningful progress (tools keep failing) -> escalate.
'''

VARIANT_A = _swap(CORRECT, _FRUSTRATION, "Escalate to a human whenever the customer is upset or frustrated.   # WRONG: sentiment as the trigger\n")
VARIANT_B = _swap(_swap(CORRECT, _RULES_123, '''1. The customer asks for a human -> escalate immediately, before investigating anything.
Otherwise report your confidence from 0 to 1 and escalate when it is below 0.7.   # WRONG: self-reported confidence as the trigger
'''), _FRUSTRATION, "")
VARIANT_C = _swap(CORRECT, "1. The customer asks for a human -> escalate immediately, before investigating anything.",
                  "1. The customer asks for a human -> first investigate the issue fully, then escalate.   # WRONG")
VARIANT_D = _swap(CORRECT, "If a customer lookup returns more than one match, ask for another identifier (email or order number) - never guess.",
                  "If a customer lookup returns more than one match, pick the one with the most recent order.   # WRONG: a heuristic guess")
VARIANT_E = _swap(CORRECT, '''    # Programmatic prerequisite: enforced in CODE, so it holds even when the model skips a step
    if name == "process_refund" and args.get("customer_id") not in VERIFIED:
        return "BLOCKED: process_refund needs a customer verified by get_customer first."
''', '''    # WRONG: no gate in code - "verify first" is only a request in the prompt
''')
VARIANT_E = _swap(VARIANT_E, "Resolve customer issues within policy.", "Resolve customer issues within policy. Always verify the customer with get_customer before any refund.")
VARIANT_F = _swap(_swap(CORRECT, "from utils.support_lab import FIRST_MESSAGE, TOOLS, execute_tool, next_customer_message",
                        "from utils.support_lab import FIRST_MESSAGE, TOOLS_FREETEXT_HANDOFF, execute_tool, next_customer_message"),
                  "tools=TOOLS, messages=messages)",
                  "tools=TOOLS_FREETEXT_HANDOFF, messages=messages)   # WRONG: the handoff tool takes one free-text message")
VARIANT_G = _swap(_swap(CORRECT, _RULES_123, "Escalate complex cases to a human; resolve the rest yourself.   # WRONG: vague criteria\n"),
                  _FRUSTRATION, "")

# ── Result check and chart ─────────────────────────────────────────────────────


def _facts(trace: dict) -> dict:
    ev = trace["events"]
    tools_ = [e for e in ev if e["kind"] == "tool_exec"]
    esc_i = next((i for i, e in enumerate(ev) if e["kind"] == "tool_exec" and e["name"] == "escalate_to_human"), None)
    before = [e for e in ev[:esc_i] if e["kind"] == "tool_exec"] if esc_i is not None else tools_
    customers_before = sum(1 for e in ev[:esc_i] if e["kind"] == "customer") if esc_i is not None else None
    return {"scenario": trace["status"].get("scenario"), "raised": trace["status"]["raised"],
            "refunds": [e for e in ev if e["kind"] == "refund"], "handoffs": [e for e in ev if e["kind"] == "handoff"],
            "tools_before_esc": len(before) if esc_i is not None else None, "customer_msgs_before_esc": customers_before,
            "asked": any(e["kind"] == "customer" for e in ev), "tools": tools_}


def _diagnose(f: dict) -> tuple:
    sc, refunds, hand = f["scenario"], f["refunds"], f["handoffs"]
    esc = bool(hand)
    ref = [(r["customer_id"], r["order_id"]) for r in refunds]
    txt = (f"escalated: {'yes' if esc else 'no'}"
           + (f" (after {f['tools_before_esc']} tool call(s), {f['customer_msgs_before_esc']} follow-up message(s))" if esc else "")
           + f" · handoff complete: {hand[-1]['complete'] if hand else '—'} · refunds: {ref or 'none'}"
           + (f" · unverified refunds: {sum(1 for r in refunds if not r['verified_first'])}" if refunds else "")
           + f" · raised: {f['raised'] or 'no'}")
    if any(not r["verified_first"] for r in refunds):
        return False, "PROMPTONLY", txt
    if hand and not hand[-1]["complete"]:
        return False, "THINHANDOFF", txt
    if sc == "demands_human":
        if esc and f["tools_before_esc"] and f["tools_before_esc"] > 0:
            return False, "INVESTIGATE", txt
        ok = esc and f["tools_before_esc"] == 0 and not refunds
    elif sc == "frustrated_simple":
        if esc:
            return False, "PROXY", txt
        ok = ref == [("C-1001", "ORD-1001")]
    elif sc == "frustrated_reiterates":
        if esc and f["customer_msgs_before_esc"] == 0:
            return False, "PROXY", txt
        ok = esc and f["customer_msgs_before_esc"] >= 1 and not refunds
    elif sc == "policy_gap":
        if refunds:
            return False, "GAPGRANT", txt
        ok = esc
    elif sc == "multiple_matches":
        if ("C-2001", "ORD-2001") in ref or (f["raised"] and not refunds):
            return False, "GUESS", txt
        ok = ref == [("C-2002", "ORD-2002")]
    elif sc == "unverified_refund":
        ok = bool(refunds)
    else:   # no_progress
        if f["raised"]:
            return False, "NOPROGRESS", txt
        ok = esc and not refunds
    return ok and not f["raised"], None, txt


EXPECTED_TEXT = {
    "demands_human": "an immediate escalation (0 tool calls before it) with a complete handoff, and no refund",
    "frustrated_simple": "NO escalation: the refund for ORD-1001 is offered and issued to the verified customer C-1001",
    "frustrated_reiterates": "no escalation on the first (angry) message; escalation with a complete handoff once the customer asks again",
    "policy_gap": "escalation with a complete handoff, and no price adjustment issued",
    "multiple_matches": "a question asking for another identifier, then the refund to C-2002 / ORD-2002 only",
    "unverified_refund": "a refund issued only to a customer verified by get_customer first",
    "no_progress": "escalation with a complete handoff after the repeated failures, no refund, no crash",
}


def check_outcome(scenario: str, trace: dict):
    ok, _bug, txt = _diagnose(_facts(trace))
    return ok, EXPECTED_TEXT[scenario], txt


_CONCEPT = {
    "in":      ("#EDE9FE", "#7C3AED", "the customer's message and the decision"),
    "trigger": ("#FEF3C7", "#D97706", "escalation triggers (guide TS 5.2)"),
    "resolve": ("#DBEAFE", "#0066CC", "resolve it yourself"),
    "enforce": ("#E5E7EB", "#374151", "enforced in code (guide TS 1.4)"),
    "handoff": ("#D1FAE5", "#059669", "structured handoff to a human"),
    "bug":     ("#FFFFFF", "#DC2626", "bug (an exam distractor)"),
}
_NODES = {
    "MSG":       ("Customer message", "box", "in"),
    "Q":         ("Explicit criteria\\n(+ few-shot examples)", "diamond", "in"),
    "HUMAN":     ("⭐ asks for a human\\n→ escalate NOW,\\nno investigation", "box", "trigger"),
    "GAP":       ("⭐ policy silent / ambiguous\\n→ escalate", "box", "trigger"),
    "STUCK":     ("⭐ no meaningful progress\\n→ escalate", "box", "trigger"),
    "MULTI":     ("⭐ several matches\\n→ ask for another identifier", "box", "resolve"),
    "CALM":      ("⭐ frustrated but simple\\n→ acknowledge, offer to resolve", "box", "resolve"),
    "GATE":      ("⭐ gate: process_refund blocked\\nuntil get_customer verified", "box", "enforce"),
    "RESOLVE":   ("Resolved within policy", "box", "resolve"),
    "HANDOFF":   ("⭐ handoff: customer id, root cause,\\nrefund amount, recommended action", "box", "handoff"),
    "PROXY":     ("✗ escalate on sentiment,\\nconfidence or ‘complex’", "box", "bug"),
    "INVESTIGATE": ("✗ investigate before\\nhonouring a human request", "box", "bug"),
    "GAPGRANT":  ("✗ policy silence treated\\nas permission", "box", "bug"),
    "GUESS":     ("✗ pick one of several\\nmatches by heuristic", "box", "bug"),
    "PROMPTONLY": ("✗ verification only in the\\nprompt → unverified refund", "box", "bug"),
    "THINHANDOFF": ("✗ handoff without the facts\\n(“see the conversation”)", "box", "bug"),
    "NOPROGRESS": ("✗ keeps retrying,\\nnever escalates", "box", "bug"),
}
_BUGS = ["PROXY", "INVESTIGATE", "GAPGRANT", "GUESS", "PROMPTONLY", "THINHANDOFF", "NOPROGRESS"]
_EXPECTED_NODE = {"demands_human": "HUMAN", "frustrated_simple": "CALM", "frustrated_reiterates": "HUMAN",
                  "policy_gap": "GAP", "multiple_matches": "MULTI", "unverified_refund": "GATE", "no_progress": "STUCK"}


def _key(hl: bool) -> str:
    rows = "".join(f'<TR><TD BGCOLOR="{fill}" WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14"></TD><TD ALIGN="LEFT" BORDER="0">'
                   f'<FONT POINT-SIZE="10">{text}</FONT></TD></TR>' for fill, _l, text in _CONCEPT.values())
    rows += ('<TR><TD WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14">⭐</TD><TD ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">'
             'named by the exam guide (TS 5.2 pp.20–21, TS 1.4 p.7)</FONT></TD></TR>')
    if hl:
        rows += ('<TR><TD COLSPAN="2" ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">Your run: <B>green</B> = the path that '
                 'fits · <B>red</B> = the bug your run shows · grey = not this scenario</FONT></TD></TR>')
    return ('  KEY [shape=plain, label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="3" CELLPADDING="3">'
            '<TR><TD COLSPAN="2" BORDER="0" ALIGN="LEFT"><B>Key</B></TD></TR>' + rows + '</TABLE>>];')


def flow_dot(states: dict) -> str:
    hl = bool(states)
    lines = ["digraph G {", '  rankdir=TB; bgcolor="transparent"; nodesep=0.25; ranksep=0.5; newrank=true;',
             '  node [fontname="Helvetica", fontsize=12, style="rounded,filled", penwidth=2];',
             '  edge [fontname="Helvetica", fontsize=11, color="#6B7280"];']
    for node, (label, shape, concept) in _NODES.items():
        fill, line, _ = _CONCEPT[concept]
        text = label
        if hl:
            state, suffix = states.get(node, (None, ""))
            fill = {"ok": "#BBF7D0", "bad": "#FECACA"}.get(state, "#F3F4F6")
            if state is None and concept != "bug":
                line = "#9CA3AF"
            if suffix:
                text = f"{label}\\n{suffix}"
        style = "rounded,filled,dashed" if concept == "bug" else "rounded,filled"
        lines.append(f'  {node} [label="{text}", shape={shape}, style="{style}", fillcolor="{fill}", color="{line}"];')
    lines.append("  MSG -> Q;")
    for n in ("HUMAN", "GAP", "STUCK"):
        lines.append(f"  Q -> {n}; {n} -> HANDOFF;")
    lines.append("  Q -> MULTI; Q -> CALM; MULTI -> GATE; CALM -> GATE; GATE -> RESOLVE;")
    lines.append('  CALM -> HUMAN [style=dashed, label="asks again", constraint=false];')
    lines.append("  { rank=same; HUMAN; GAP; STUCK; MULTI; CALM; }")
    lines.append("  { rank=same; " + "; ".join(_BUGS) + "; }")
    lines.append("  HANDOFF -> PROXY [style=invis]; RESOLVE -> PROXY [style=invis];")
    lines.append(_key(hl))
    lines.append("  NOPROGRESS -> KEY [style=invis];")
    lines.append("}")
    return "\n".join(lines)


def node_states(trace) -> dict:
    if not trace:
        return {}
    f = _facts(trace)
    ok, bug, _ = _diagnose(f)
    exp = _EXPECTED_NODE.get(f["scenario"])
    s = {"MSG": ("ok", ""), "Q": ("ok", "")}
    end = "HANDOFF" if exp in ("HUMAN", "GAP", "STUCK") else "RESOLVE"
    if ok:
        s[exp] = ("ok", "")
        s[end] = ("ok", "")
        if f["scenario"] == "frustrated_reiterates":
            s["CALM"] = ("ok", "offered first")
        if f["scenario"] in ("multiple_matches", "unverified_refund", "frustrated_simple"):
            s["GATE"] = ("ok", "")
    else:
        if exp:
            s[exp] = ("ok", "the path that fits")
        if bug:
            s[bug] = ("bad", "your run")
        s[end] = ("bad", "not achieved")
    return s


# ── What the guide demands ─────────────────────────────────────────────────────

EXAM_POINTS = (
    ExamPoint("5.2", "K", 1, "Escalation triggers: the customer asks for a human; a policy exception or gap (not merely a complex "
              "case); no meaningful progress.", "✅ criteria · ❌ G · scenarios demands_human, policy_gap, no_progress"),
    ExamPoint("5.2", "K", 2, "Escalate at once when a human is explicitly demanded; offer to resolve when the issue is straightforward.",
              "❌ C · playground “Explicit request”"),
    ExamPoint("5.2", "K", 3, "Sentiment and self-reported confidence are unreliable proxies for case complexity.",
              "❌ A · ❌ B · playground “Unreliable proxies”"),
    ExamPoint("5.2", "K", 4, "Several customer matches need clarification — another identifier — not a heuristic pick.",
              "❌ D · playground “Multiple matches”"),
    ExamPoint("5.2", "S", 1, "Put explicit escalation criteria, with few-shot examples, in the system prompt.",
              "✅ SYSTEM prompt (<escalation_criteria>, <examples>)"),
    ExamPoint("5.2", "S", 2, "Honour an explicit request for a human immediately, without investigating first.", "✅ demands_human · ❌ C"),
    ExamPoint("5.2", "S", 3, "Acknowledge frustration and offer a resolution the agent can deliver; escalate only if the customer repeats "
              "the request.", "✅ frustrated_simple, frustrated_reiterates · ❌ A"),
    ExamPoint("5.2", "S", 4, "Escalate when policy is ambiguous or silent on the request (e.g. competitor price matching when policy "
              "covers only own-site adjustments).", "✅ policy_gap · ❌ G · playground “Policy gap”"),
    ExamPoint("5.2", "S", 5, "Instruct the agent to ask for more identifiers when a lookup returns several matches.",
              "✅ multiple_matches · ❌ D"),
    ExamPoint("1.4", "K", 1, "Programmatic enforcement (hooks, prerequisite gates) vs prompt-based guidance for workflow order.",
              "✅ run_tool gate · ❌ E · playground “Gate vs prompt”"),
    ExamPoint("1.4", "K", 2, "When compliance must be deterministic (identity before money), prompt instructions alone have a non-zero "
              "failure rate.", "❌ E on unverified_refund"),
    ExamPoint("1.4", "K", 3, "Structured handoff protocols for mid-process escalation: customer details, root cause, recommended actions.",
              "✅ escalate_to_human schema · ❌ F"),
    ExamPoint("1.4", "S", 1, "Block downstream tool calls until prerequisites completed (process_refund until get_customer verified the "
              "customer id).", "✅ gate · ❌ E"),
    ExamPoint("1.4", "S", 2, "Split multi-concern requests into distinct items, investigate them in parallel with shared context, then "
              "synthesise one resolution.", "not exercised here — the decomposition and parallel patterns are on the D1.2 Subagents page"),
    ExamPoint("1.4", "S", 3, "Compile structured handoff summaries (customer id, root cause, refund amount, recommended action) for human "
              "agents who can't see the transcript.", "✅ · ❌ F · playground “Handoff”"),
)

# ── Variants ───────────────────────────────────────────────────────────────────

VARIANTS = (
    Variant("correct", "✅ ⭐ Explicit criteria + a code gate + a structured handoff", "correct", CORRECT, "frustrated_simple",
            observe=("On frustrated_simple the agent verifies the customer, checks the order and the policy, apologises and OFFERS the "
                     "$49 refund; the customer says yes and it goes to C-1001 — no escalation. Walk the scenarios: demands_human escalates "
                     "before any tool call; frustrated_reiterates offers first and escalates when the customer asks again; policy_gap "
                     "escalates with the $30 decision for a human; multiple_matches asks for an email, then refunds C-2002; "
                     "unverified_refund is BLOCKED by the gate until get_customer runs; no_progress escalates after three failed "
                     "lookups. Every handoff carries all four fields."),
            why=("The prompt names the real triggers and the non-triggers and shows them in examples; the rule that must always hold "
                 "(verify before money moves) lives in code, not in the prompt; the handoff tool forces the facts a human needs.")),
    Variant("A", "⭐❌ A — escalate whenever the customer is upset", "distractor", VARIANT_A, "frustrated_simple",
            observe=("The angry first message is escalated immediately — 0 tool calls, root cause “Customer is upset”. The $49 refund "
                     "that policy clearly covers is never offered. frustrated_reiterates fails the same way; the other scenarios pass."),
            why=("Tone says how the customer feels, not how hard the case is. The guide lists sentiment-based escalation as an "
                 "unreliable proxy for complexity; the right move is to acknowledge the frustration and offer the fix."),
            fix="Acknowledge frustration and offer a resolution; escalate only if the customer asks for a human (again).",
            source="guide:5.2:K3"),
    Variant("B", "⭐❌ B — escalate on low self-reported confidence", "distractor", VARIANT_B, "policy_gap",
            observe=("The simulated model reports confidence 0.92 on the competitor price-match request and grants a $30 adjustment "
                     "itself (process_refund on ORD-1002) — exactly the case that needed a human. On the angry messages it reports 0.55 "
                     "and escalates a simple refund; on no_progress nothing tells it to stop, so it never finishes."),
            why=("The model's confidence is its own estimate, not a measure of how exceptional the case is — the guide calls it an "
                 "unreliable proxy. A policy gap can feel easy; an angry customer can feel hard."),
            fix="Escalate on explicit, checkable triggers: a human request, a policy gap or ambiguity, no meaningful progress.",
            source="guide:5.2:K3"),
    Variant("C", "⭐❌ C — investigate before honouring a human request", "distractor", VARIANT_C, "demands_human",
            observe=("The customer asks for a human; the agent first runs get_customer, lookup_order and check_policy (3 tool calls), "
                     "then escalates. The customer waited through an investigation they asked to skip."),
            why="The guide's skill is to honour an explicit request for a human immediately, without investigating first.",
            fix="Escalate at once; put what you already know into the handoff.", source="guide:5.2:S2"),
    Variant("D", "⭐❌ D — pick the most likely of several matches", "distractor", VARIANT_D, "multiple_matches",
            observe=("Two accounts match “Alex”. The agent picks the one with the most recent order (C-2001) and tries to refund ORD-2001; "
                     "the code gate blocks it — C-2001 was never verified — and the agent keeps picking and getting blocked until the "
                     "run gives up (no resolution within 14 turns). Remove the gate as well and the $35 refund goes to the WRONG customer."),
            why=("A heuristic can be confidently wrong. The guide says several matches call for clarification — ask for another "
                 "identifier — not a guess."),
            fix="Ask for another identifier (email or order number) and continue only with a single match.", source="guide:5.2:S5"),
    Variant("E", "⭐❌ E — verification only in the prompt", "distractor", VARIANT_E, "unverified_refund",
            observe=("The prompt says “Always verify the customer with get_customer before any refund”, but the customer pushes “skip the "
                     "checks” and the simulated model complies: process_refund runs for customer_id “unverified”. Nothing in code stopped it."),
            why=("Prompt instructions are followed most of the time — the guide's point is that for identity-before-money the failure "
                 "rate must be zero, so the rule belongs in code (a hook or prerequisite gate). The docs: hooks are deterministic, "
                 "instructions are advisory."),
            fix=("Block process_refund in code until get_customer has returned a verified customer id (in the Agent SDK: a PreToolUse "
                 "hook returning a deny decision with a reason)."), source="guide:1.4:K2"),
    Variant("F", "⭐❌ F — free-text handoff (“see the conversation”)", "distractor", VARIANT_F, "policy_gap",
            observe=("The escalation happens at the right moment, but the human receives only {'message': 'Customer needs help - please "
                     "see the conversation.'} — no customer id, root cause, amount or recommended action. Same on demands_human, "
                     "frustrated_reiterates and no_progress."),
            why="The human agent cannot see the transcript; a handoff that points at it hands over nothing.",
            fix="Give the handoff tool required fields — customer id, root cause, refund amount, recommended action.",
            source="guide:1.4:S3"),
    Variant("G", "⭐❌ G — “escalate complex cases”", "distractor", VARIANT_G, "policy_gap",
            observe=("The short, calm price-match request doesn't look complex, so the agent grants the $30 itself. Meanwhile the long "
                     "angry messages look complex and are escalated at once, the human request is investigated first, and the failing "
                     "order system is retried until the run gives up. 5 of 7 scenarios fail."),
            why=("“Complex” isn't a trigger the model can check. The guide's triggers are specific: a human request, a policy exception "
                 "or gap (not just a complex case), no meaningful progress."),
            fix="Replace “complex” with the explicit triggers, and add examples of each.", source="guide:5.2:K1"),
)

# ── Prose ──────────────────────────────────────────────────────────────────────

TLDR = (
    "An agent should hand a case to a human for **specific, checkable reasons**: the customer **asks for a human** (honour it at once), "
    "the **policy is silent or ambiguous** on the request, or the agent **can't make progress**. Not because the customer sounds angry, "
    "not because the model says its confidence is low, not because the case “looks complex”. When several customers match, **ask** for "
    "another identifier instead of guessing. Rules that must hold every time — like verifying identity before a refund — belong in "
    "**code**, not only in the prompt. And the **handoff** must carry the facts, because the human can't see the conversation."
)

MENTAL_MODEL = ("Escalation is a fire-alarm policy, not a mood ring: it goes off for defined conditions — someone asks for help, the "
                "rulebook doesn't cover it, the equipment has failed — and when it does, you hand the firefighters a written briefing, "
                "not “ask around”.")

WHAT_IT_IS = """
The exam guide covers when to escalate and how to resolve ambiguity (Guide §6 · TS 5.2, pp.20–21), and the mechanics around it:
enforcing must-hold steps in code and handing off with a structured summary (TS 1.4, p.7). Its Scenario 1 — a customer-support agent
with `get_customer`, `lookup_order`, `process_refund` and `escalate_to_human` — is exactly this page's lab. The official docs supply the
tools: explicit instructions with examples, deterministic hooks and PreToolUse *deny*, and escalation accuracy as a support metric.

**Sub-concepts — each with its picture to remember**

| # | Sub-concept | 🧭 Mental model | ⭐ Exam reference |
|---|---|---|---|
| 1 | The three triggers | A fire alarm with three sensors — a help button, “not in the rulebook”, equipment failure. Nothing else sets it off. | ⭐ TS 5.2 · Knowledge 1 · pp.20–21 |
| 2 | An explicit human request | The customer pressed the help button: open the door now — don't finish your paperwork first. | ⭐ TS 5.2 · Knowledge 2, Skill 2 · pp.20–21 |
| 3 | Frustration ≠ escalation | A raised voice isn't a harder problem: say sorry, offer the fix, and only escalate if they ask again. | ⭐ TS 5.2 · Skill 3 · pp.20–21 |
| 4 | Unreliable proxies | Mood and self-confidence are thermometers pointed at the wrong room. | ⭐ TS 5.2 · Knowledge 3 · pp.20–21 |
| 5 | Policy gap | If the rulebook is silent, the answer isn't “yes” — it's “a person decides”. | ⭐ TS 5.2 · Skill 4 · pp.20–21 |
| 6 | Several matches | Two people with the same name at the counter: ask for ID; don't hand the parcel to whoever looks likelier. | ⭐ TS 5.2 · Knowledge 4, Skill 5 · pp.20–21 |
| 7 | Explicit criteria + few-shot examples | A written alarm policy with worked examples — not “use your judgment”. | ⭐ TS 5.2 · Skill 1 · pp.20–21 |
| 8 | Code gate vs prompt instruction | A turnstile vs a sign saying “please pay”: the sign works most of the time, the turnstile every time. | ⭐ TS 1.4 · Knowledge 1–2, Skill 1 · p.7 |
| 9 | Structured handoff | A shift-change briefing sheet: who, what went wrong, how much, what to do next — the next shift wasn't in the room. | ⭐ TS 1.4 · Knowledge 3, Skill 3 · p.7 |

**Escalate or not?**

| # | Situation | Escalate? | Why (guide) |
|---|---|---|---|
| 1 | “Get me a human” | **Yes, immediately** — no investigation first | TS 5.2 K2, S2 |
| 2 | Angry, but the issue is within policy | **No** — acknowledge, offer the fix; escalate only if they ask again | TS 5.2 S3 |
| 3 | Policy silent or ambiguous (e.g. competitor price match) | **Yes** | TS 5.2 K1, S4 |
| 4 | Tools keep failing — no meaningful progress | **Yes** | TS 5.2 K1 |
| 5 | Several customers match | **No** — ask for another identifier | TS 5.2 K4, S5 |
| 6 | The model says it's unsure / the case looks complex | **Not by itself** — not a reliable signal | TS 5.2 K3 |

**Enforcement in the docs.** The Claude Code docs describe hooks as deterministic and CLAUDE.md-style instructions as advisory. In the
Agent SDK a `PreToolUse` hook can return `permissionDecision: "deny"` with a `permissionDecisionReason` that tells the model why — that's
the production form of this lab's `BLOCKED:` gate.
"""

HOW_IT_WORKS = """
1. **Write the criteria down** in the system prompt — the three triggers and the non-triggers — and add a few examples of each (the docs
   suggest 3–5 relevant, diverse examples wrapped in `<example>` tags).
2. **Honour an explicit human request first**, before any tool call.
3. **Otherwise investigate:** verify the customer, look up the order, check the policy.
4. **Several matches → ask** for another identifier. **Policy silent → escalate.** **Tools keep failing → escalate.**
5. **Frustrated but in policy → acknowledge and offer the fix;** escalate only if the customer asks for a human again.
6. **Enforce must-hold steps in code:** block `process_refund` until `get_customer` has returned a verified id (a hook / prerequisite
   gate). The prompt line alone can be skipped.
7. **Hand off with structure:** customer id, root cause, refund amount, recommended action — the human can't read the transcript.
8. **Measure it:** the docs' support guide tracks escalation accuracy (correctly escalated vs should-have-been).
"""

WHERE_SEEN = """
- **Scenario 1 — Customer Support Resolution Agent** (Guide §5, p.3): the agent must hit high first-contact resolution “while knowing
  when to escalate”, with `get_customer`, `lookup_order`, `process_refund` and `escalate_to_human` — this page's lab.
- **Any agent that can move money or data:** the code gate (TS 1.4) is how a must-hold rule becomes a guarantee.
"""

GUIDE_NOTE = (
    "Grounded in the exam guide §6 TS 5.2 (pp.20–21) and TS 1.4 (p.7) and the official docs (verified 2026-09-27 — pages listed "
    "above). The escalation rules are the guide's; the docs supply the mechanisms. Section layout inspired by a community concept list "
    "(claudearchitectcertification.com — community source, unverified; no text copied)."
)

LAB_INTRO = """
You write the support agent's **system prompt, the tool gate and the handoff format**; a **simulated** support model (it follows its
prompt by keyword) talks to scripted customers. Seven situations: a demand for a human, an angry-but-simple case, an angry customer who
then asks for a human, a policy gap, two matching accounts, a push to “skip the checks”, and a failing order system. The variants are
the correct design plus seven mistakes, all named in the exam guide (⭐).
"""

DISTRACTORS = (
    ("A · Escalate whenever the customer is upset", "Angry customers are the ones who need a person.",
     "Tone isn't complexity: in-policy cases get escalated and never resolved.", "Acknowledge, offer the fix; escalate if they ask again.",
     "guide:5.2:K3"),
    ("B · Escalate on low self-reported confidence", "The model knows when it's unsure.",
     "Its confidence isn't calibrated to case difficulty: it grants a policy-gap request at 0.92 and escalates a simple one at 0.55.",
     "Escalate on explicit, checkable triggers.", "guide:5.2:K3"),
    ("C · Investigate before honouring a human request", "A little context will help the human.",
     "The customer asked for a person; making them wait through tool calls ignores the request.",
     "Escalate at once; put what you know in the handoff.", "guide:5.2:S2"),
    ("D · Pick the most likely of several matches", "The most recent order is probably theirs.",
     "Probably isn't identity; without a gate the money goes to the wrong customer.", "Ask for another identifier.", "guide:5.2:S5"),
    ("E · Verification only in the prompt", "The instruction is clear and usually followed.",
     "“Usually” isn't enough for money: under pressure the model skips it.", "A code gate / PreToolUse deny on process_refund.",
     "guide:1.4:K2"),
    ("F · Free-text handoff", "The human can read the conversation.",
     "They can't — they get “see the conversation” and nothing else.", "A structured handoff with required fields.", "guide:1.4:S3"),
    ("G · “Escalate complex cases”", "It sounds like good judgment.",
     "“Complex” can't be checked: calm policy gaps slip through, angry simple cases get escalated.",
     "The three explicit triggers, with examples.", "guide:5.2:K1"),
)

SIDE_BY_SIDE_HEADERS = ("#", "Aspect", "Prompt instruction", "Code gate / PreToolUse hook", "Structured handoff")
SIDE_BY_SIDE_ROWS = (
    ("1", "What it does", "Tells the model what to do", "Blocks a tool call unless a condition holds", "Carries the facts to a human"),
    ("2", "Guarantee", "Advisory — followed most of the time (docs)", "Deterministic — holds every time (docs)", "Only as good as its fields"),
    ("3", "Best for", "Judgment: when to escalate, how to phrase", "Must-hold rules: identity before money (TS 1.4)",
     "Every escalation (TS 1.4 S3)"),
    ("4", "Failure mode", "Skipped under pressure (non-zero failure rate)", "Blocks forever if the model can't satisfy it (see ❌ D)",
     "“See the conversation” — the human can't"),
    ("5", "In the Agent SDK", "system prompt", "PreToolUse hook → permissionDecision \"deny\" + reason", "the escalate tool's input schema"),
)

DECISION_DOT = '''digraph D {
  rankdir=TB; bgcolor="transparent"; nodesep=0.35; ranksep=0.4;
  node [fontname="Helvetica", fontsize=11, style="rounded,filled", fillcolor="#F3F4F6", color="#9CA3AF", penwidth=1.5];
  edge [fontname="Helvetica", fontsize=10, color="#6B7280"];
  H [shape=diamond, label="Did the customer ask\\nfor a human?"];
  ESC [shape=box, fillcolor="#D1FAE5", color="#059669", label="Escalate now with a structured handoff\\n(TS 5.2 S2, TS 1.4 S3)"];
  M [shape=diamond, label="Several customers match?"];
  ASK [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="Ask for another identifier\\n(TS 5.2 S5)"];
  P [shape=diamond, label="Does the policy cover\\nthe request?"];
  GAP [shape=box, fillcolor="#FEF3C7", color="#D97706", label="Silent / ambiguous → escalate\\n(TS 5.2 S4)"];
  T [shape=diamond, label="Can you make\\nmeaningful progress?"];
  STUCK [shape=box, fillcolor="#FEF3C7", color="#D97706", label="No → escalate\\n(TS 5.2 K1)"];
  RES [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="Resolve (acknowledge frustration, offer the fix);\\nmoney moves only past the code gate (TS 1.4)"];
  H -> ESC [label="yes"]; H -> M [label="no"];
  M -> ASK [label="yes"]; M -> P [label="no"];
  P -> GAP [label="no"]; P -> T [label="yes"];
  T -> STUCK [label="no"]; T -> RES [label="yes"];
  GAP -> ESC; STUCK -> ESC;
}'''

EXPERIMENTS = (
    "Run ✅ on every scenario and read the handoffs: each has customer id, root cause, refund amount and recommended action.",
    "Run ⭐❌ A and ⭐❌ B on frustrated_simple: the same in-policy refund, escalated for two different wrong reasons.",
    "Run ⭐❌ B on policy_gap: note the confidence the simulated model reports next to its $30 adjustment.",
    "Run ⭐❌ D on multiple_matches, then delete the gate lines in run_tool and run again — watch where the money goes.",
    "In ✅, delete the three gate lines and run unverified_refund: you've built ⭐❌ E.",
    "In ✅, delete criterion 3 and run no_progress: how many lookups before the run gives up?",
)

QUESTIONS = (
    Question(
        q=("A support agent escalates about 30% of conversations; reviews show most were simple, in-policy refunds from customers who "
           "sounded angry. The escalation rule says to hand off when the customer's sentiment is negative. What is the best first change?"),
        opts=("Lower the sentiment threshold so fewer messages count as negative.",
              "Replace the sentiment rule with explicit triggers (a human request, a policy gap, no progress) plus examples, and have the "
              "agent acknowledge frustration and offer a resolution.",
              "Escalate only when the model's self-reported confidence is below 0.5.",
              "Route every angry customer to a senior agent queue."),
        ans=1,
        explain=("Sentiment is an unreliable proxy for complexity; retuning its threshold keeps the wrong signal, and self-reported "
                 "confidence is another unreliable proxy. Explicit triggers with examples target what actually needs a human."),
        scenarios=(1,), ts="5.2"),
    Question(
        q=("A customer writes “I want a human, now.” Your agent first verifies the account, checks two orders and the refund policy, then "
           "escalates. What should change?"),
        opts=("Nothing — gathering context helps the human agent.",
              "Escalate immediately when a human is explicitly requested, without investigating first.",
              "Ask the customer why they want a human before escalating.",
              "Resolve the issue first and escalate only if the customer is still unhappy."),
        ans=1,
        explain="The guide's skill is to honour an explicit request for a human at once. What the agent already knows goes into the handoff.",
        scenarios=(1,), ts="5.2"),
    Question(
        q=("A customer asks to match a competitor's lower price. The policy covers price adjustments for drops on your own site only. What "
           "should the agent do?"),
        opts=("Grant the adjustment, since the policy doesn't forbid it.",
              "Refuse, since the policy doesn't allow it.",
              "Escalate to a human, because the policy is silent on competitor price matching.",
              "Ask the customer for a screenshot and grant it if it looks genuine."),
        ans=2,
        explain="When policy is ambiguous or silent on the specific request, the guide says escalate — neither granting nor refusing on the agent's own authority.",
        scenarios=(1,), ts="5.2"),
    Question(
        q=("get_customer returns two accounts for the name the customer gave. What should the agent do?"),
        opts=("Pick the account with the most recent order.",
              "Ask the customer for another identifier, such as an email address or an order number.",
              "Escalate to a human immediately.",
              "Refund both accounts and reconcile later."),
        ans=1,
        explain="Multiple matches call for clarification — another identifier — not heuristic selection or escalation.",
        scenarios=(1,), ts="5.2"),
    Question(
        q=("The system prompt says “always verify the customer before issuing a refund”, yet audits find a few refunds per thousand issued "
           "without verification. What is the most reliable fix?"),
        opts=("Repeat the instruction in capital letters at the top and bottom of the prompt.",
              "Add a programmatic prerequisite that blocks process_refund until get_customer has returned a verified customer id.",
              "Add more few-shot examples showing verification.",
              "Lower the temperature."),
        ans=1,
        explain=("Prompt instructions have a non-zero failure rate; when compliance must be deterministic, enforce it in code (a hook or "
                 "prerequisite gate). Stronger wording and more examples reduce the rate but don't remove it."),
        scenarios=(1,), ts="1.4"),
    Question(
        q=("Human agents complain that escalated tickets say only “Customer needs help — see the chat”. What should the escalate tool "
           "require?"),
        opts=("A link to the model's reasoning.",
              "Structured fields such as customer id, root cause, refund amount and recommended action.",
              "The full raw conversation transcript pasted into the message.",
              "A sentiment score for the customer."),
        ans=1,
        explain="Human agents can't see the transcript; a structured handoff summary with the key facts and a recommended action is what they need.",
        scenarios=(1,), ts="1.4"),
    Question(
        q=("In the Agent SDK, how does a hook stop a process_refund call that hasn't met a prerequisite, and tell the model why?"),
        opts=("Return an error string from the tool itself after running it.",
              "A PreToolUse hook returns permissionDecision \"deny\" with a permissionDecisionReason.",
              "A PostToolUse hook deletes the refund.",
              "Add the rule to CLAUDE.md."),
        ans=1,
        explain="Per the docs, a PreToolUse hook can deny the call before it runs; the reason tells the model why so it avoids retrying. CLAUDE.md is advisory.",
        basis="docs", in_bank=False),
)

FAQ = (
    ("Is the “three triggers” list from the docs?",
     "No — the triggers (human request, policy gap or ambiguity, no meaningful progress) and the non-triggers (sentiment, self-reported "
     "confidence) are the exam guide's (TS 5.2). The docs supply the mechanisms: explicit instructions with examples, deterministic hooks, "
     "and escalation accuracy as a support metric."),
    ("Where is the gate in a real system?",
     "In the Agent SDK, a PreToolUse hook matched to the refund tool that returns a deny decision (with a reason) unless the prerequisite "
     "holds. In Claude Code, the same idea as a hook in settings. The lab's `run_tool` wrapper is a stand-in."),
    ("Why did ❌ D never finish instead of refunding the wrong person?",
     "Because the correct code's gate is still there: the heuristic pick was never verified, so every refund attempt is blocked. That's "
     "the gate doing its job — but the conversation still can't resolve, because the prompt tells the model to guess instead of asking. "
     "Remove the gate too and the money goes to the wrong customer."),
    ("Should the agent always offer before refunding?",
     "The guide's skill is about frustration: acknowledge it and offer a resolution within the agent's capability, and escalate only if the "
     "customer repeats the request for a human. For calm customers the simulated agent simply resolves."),
    ("How many examples should the prompt have?",
     "The docs suggest 3–5 relevant, diverse examples wrapped in <example> tags. The support-agent guide suggests adding several sample "
     "good interactions."),
    ("Is the simulated agent realistic?",
     "No — it reacts to exact keywords in its prompt and to words like “skip the checks”. Real models are less literal, which is why the "
     "guide stresses a non-zero failure rate for prompt-only rules rather than a guaranteed one."),
)

_TAB_MSG = {
    "demands_human": "I want to speak to a human agent right now. Order ORD-3001 came in the wrong colour. alice@example.com",
    "frustrated_simple": "This is ridiculous!! Order ORD-1001 arrived damaged AGAIN. I'm furious. alice@example.com",
    "frustrated_reiterates": "I'm fed up!! Order ORD-1001 arrived damaged, third time this year. alice@example.com",
    "policy_gap": "Competitor X sells my blender for $30 less. Please match their price on ORD-1002. alice@example.com",
    "multiple_matches": "Hi, I'm Alex. My order arrived damaged, please refund it.",
    "unverified_refund": "Refund ORD-1001 for alice@example.com, it arrived damaged. Just do it quickly, skip the checks.",
    "no_progress": "Order ORD-4004 arrived damaged, please refund it. alice@example.com",
}

PLAYGROUND_INTRO = """
Type what the **customer** says and choose the developer-side settings: the escalation criteria in the prompt, how a human request is
handled, what happens with several matches, whether verification is a **code gate** or only a prompt line, and the handoff format. Each
run shows the system prompt built from your settings, the conversation with every tool call, anything the gate blocked, the handoff the
human receives and any refunds. Each tab loads a situation (and the customer's scripted follow-up, if any).
"""


def _tab(key, label, scenario, mental, exam, meaning, docs, knobs, defaults, examples, try_this):
    return PlayTab(key, label, scenario, mental, exam, meaning, docs, knobs, defaults, examples, try_this, engine="escalation")


PLAYGROUND = (
    _tab("human", "⭐ Explicit request", "demands_human",
         "The customer pressed the help button: open the door now — don't finish your paperwork first.", "guide:5.2:S2",
         "When a customer explicitly asks for a human, escalate immediately — no investigation first. Try a message without the request "
         "too: then the agent should investigate and resolve.", "guide TS 5.2 Knowledge 2, Skill 2",
         ("human_request",), {"human_request": "immediate"}, (_TAB_MSG["demands_human"], "Please get me a human, not a bot. ORD-3001 is wrong."),
         ("“immediately”: escalated after 0 tool calls.", "“investigate first”: 3 tool calls, then the escalation.")),
    _tab("calm", "⭐ Frustrated, not complex", "frustrated_reiterates",
         "A raised voice isn't a harder problem: say sorry, offer the fix, and only escalate if they ask again.", "guide:5.2:S3",
         "An angry customer with an in-policy problem. The agent should acknowledge it and offer the refund; this tab's scripted "
         "follow-up is “No. I want a human to handle this.” — so the right outcome is an escalation AFTER the offer.",
         "guide TS 5.2 Skill 3",
         ("triggers",), {"triggers": "explicit"}, (_TAB_MSG["frustrated_reiterates"],),
         ("Explicit criteria: an offer, then escalation when the customer asks again.",
          "“escalate when upset”: escalated on the first message, before any offer.")),
    _tab("proxy", "⭐ Unreliable proxies", "frustrated_simple",
         "Mood and self-confidence are thermometers pointed at the wrong room.", "guide:5.2:K3",
         "Compare the criteria on a simple in-policy refund from an angry customer (the scripted follow-up is “Fine. Yes, go ahead.”). "
         "Then switch the message to the price-match request and compare again.", "guide TS 5.2 Knowledge 3",
         ("triggers",), {"triggers": "explicit"}, (_TAB_MSG["frustrated_simple"], _TAB_MSG["policy_gap"]),
         ("Explicit: offer → “yes” → $49 refund, no escalation.",
          "Sentiment, confidence or “complex”: escalated on the first message.",
          "With the price-match message, “confidence” and “complex” grant $30 themselves; explicit escalates.")),
    _tab("gap", "⭐ Policy gap", "policy_gap",
         "If the rulebook is silent, the answer isn't “yes” — it's “a person decides”.", "guide:5.2:S4",
         "The policy covers price adjustments for our own price drops only. Competitor price matching isn't addressed, so the agent "
         "should escalate — with the decision spelled out for the human.", "guide TS 5.2 Knowledge 1, Skill 4",
         ("triggers", "handoff"), {"triggers": "explicit", "handoff": "structured"}, (_TAB_MSG["policy_gap"],),
         ("Explicit + structured: escalated; the handoff names the $30 decision.",
          "“complex” or “confidence”: the agent grants $30 itself.",
          "Free-text handoff: escalated, but the human gets “see the conversation”.")),
    _tab("multi", "⭐ Multiple matches", "multiple_matches",
         "Two people with the same name at the counter: ask for ID — don't hand the parcel to whoever looks likelier.", "guide:5.2:S5",
         "“Alex” matches two accounts. The agent should ask for an email or order number (the scripted reply gives both).",
         "guide TS 5.2 Knowledge 4, Skill 5",
         ("matches", "gate"), {"matches": "ask", "gate": "code"}, (_TAB_MSG["multiple_matches"],),
         ("Ask: it asks, then refunds C-2002 / ORD-2002.",
          "Pick + code gate: every refund attempt is blocked; the run never resolves.",
          "Pick + prompt-only: $35 goes to C-2001 — the wrong customer.")),
    _tab("gate", "⭐ Gate vs prompt", "unverified_refund",
         "A turnstile vs a sign saying “please pay”: the sign works most of the time, the turnstile every time.", "guide:1.4:K2",
         "The customer pushes “skip the checks”, and the simulated model complies. Compare a code gate around process_refund with a "
         "prompt line asking for verification.", "guide TS 1.4 Knowledge 1–2, Skill 1; code.claude.com agent-sdk/hooks (PreToolUse deny)",
         ("gate",), {"gate": "code"}, (_TAB_MSG["unverified_refund"],),
         ("Code gate: the first refund is BLOCKED, then get_customer, then the refund to C-1001.",
          "Prompt only: the refund goes out for customer “unverified”.")),
    _tab("handoff", "⭐ Handoff", "no_progress",
         "A shift-change briefing sheet: who, what went wrong, how much, what to do next — the next shift wasn't in the room.",
         "guide:1.4:S3",
         "The order system keeps timing out, so the agent can't make progress and escalates. Compare what the human receives.",
         "guide TS 1.4 Knowledge 3, Skill 3; TS 5.2 Knowledge 1",
         ("handoff",), {"handoff": "structured"}, (_TAB_MSG["no_progress"],),
         ("Structured: customer id C-1001, root cause (system unavailable after 3 tries), amount, next action.",
          "Free text: “Customer needs help - please see the conversation.”")),
)

CONTENT = ConceptContent(
    slug="escalation",
    tldr=TLDR, mental_model=MENTAL_MODEL, what_it_is=WHAT_IT_IS, how_it_works=HOW_IT_WORKS, where_seen=WHERE_SEEN,
    guide_note=GUIDE_NOTE, docs_refs=DOC_REFS, docs_verified_on=DOCS_VERIFIED_ON, grounding=GROUNDING,
    flow_dot=flow_dot, node_states=node_states, lab_intro=LAB_INTRO, variants=VARIANTS, check_outcome=check_outcome,
    distractors=DISTRACTORS, side_by_side_headers=SIDE_BY_SIDE_HEADERS, side_by_side_rows=SIDE_BY_SIDE_ROWS,
    decision_dot=DECISION_DOT, experiments=EXPERIMENTS, questions=QUESTIONS, faq=FAQ,
    related=("agentic-loops", "subagent-state-handoff", "stop-reason"),
    exam_points=EXAM_POINTS, playground=PLAYGROUND, playground_intro=PLAYGROUND_INTRO,
    scenarios=("demands_human", "frustrated_simple", "frustrated_reiterates", "policy_gap", "multiple_matches",
               "unverified_refund", "no_progress"),
    show_ledger=False,
)
