"""
D2.2 Tool Choice — controlling WHETHER and WHICH tool is called, extracting structured data through tool schemas, and giving
each agent the right tools. Guide TS 2.3 (tool distribution and tool_choice; pp.10–11) and TS 4.3 (structured output via tool
use and JSON schemas; pp.17–18).

GROUNDING (CLAUDE.md, user rules): guide read from the PDF (2026-09-27); platform docs fetched 2026-09-27 (DOC_REFS). Every claim
is in GROUNDING with its source type. The guide names three tool_choice options; the docs list four (+ "none") and document models
that reject forced tool use — both shown. Paraphrased; no real exam question reproduced.
"""

from utils.concept_types import Claim, ConceptContent, DocRef, ExamPoint, PlayTab, Question, Variant
from utils.flow_style import readable

DOCS_VERIFIED_ON = "2026-09-27"
_P = "https://platform.claude.com/docs/en"
_C = "https://code.claude.com/docs/en"

DOC_REFS = (
    DocRef("Define tools — Forcing tool use / tool_choice", f"{_P}/agents-and-tools/tool-use/define-tools"),
    DocRef("Strict tool use", f"{_P}/agents-and-tools/tool-use/strict-tool-use"),
    DocRef("Structured outputs", f"{_P}/build-with-claude/structured-outputs"),
    DocRef("Subagents in the SDK — tool restrictions", f"{_C}/agent-sdk/subagents"),
    DocRef("Give Claude custom tools — allowed tools and availability", f"{_C}/agent-sdk/custom-tools"),
)

GROUNDING = (
    Claim("tool_choice has four options: auto (Claude decides; the default when tools are provided), any (must use one of the "
          "provided tools), tool (must use the named tool), none (no tools; the default when no tools are provided).",
          "docs", "define-tools § Forcing tool use"),
    Claim("With any or tool the API prefills the assistant message, so Claude emits no natural-language text before the tool_use "
          "block — even if asked. To get an explanation AND a tool call, use auto plus an explicit instruction in the user message.",
          "docs", "define-tools § Forcing tool use"),
    Claim("Forced tool use isn't supported everywhere: with manual extended thinking (thinking type enabled) any/tool error; on "
          "Claude Opus 5.5, Fable 5.1 and Mythos 5.1 any/tool return a 400 — use auto with strict tool use, or structured outputs. "
          "auto and none still work.", "docs", "define-tools § Forcing tool use (table)"),
    Claim("On models that support forcing, combine tool_choice any with strict: true to guarantee a tool is called AND its input "
          "follows the schema.", "docs", "define-tools § Forcing tool use (tip)"),
    Claim("strict: true constrains sampling so tool inputs always match the input_schema (types, required fields) and the tool name "
          "is valid; strict schemas need additionalProperties: false. Without strict, Claude might pass \"2\" instead of 2 or omit "
          "required fields.", "docs", "strict-tool-use § Why strict tool use matters; How it works"),
    Claim("Structured outputs guarantee schema compliance, not semantic correctness; refusals and max_tokens can still produce "
          "non-compliant output.", "docs", "structured-outputs § caveats"),
    Claim("Subagent tools can be restricted (AgentDefinition tools); a tool left out isn't in the agent's context at all. In the "
          "Agent SDK, `tools` controls availability and allowedTools controls permission.", "docs", "agent-sdk/subagents § Tool restrictions; custom-tools § Configure allowed tools"),
    Claim("Too many tools (e.g. 18 instead of 4–5) degrade selection reliability; agents with tools outside their specialisation "
          "misuse them (a synthesis agent running web searches); scope each agent's tools to its role, with limited cross-role "
          "tools for specific high-frequency needs.", "guide", "TS 2.3 · Knowledge 1–3 · pp.10–11"),
    Claim("tool_choice options: \"auto\", \"any\", forced {\"type\":\"tool\",\"name\":…}.", "guide", "TS 2.3 · Knowledge 4 · pp.10–11; TS 4.3 · Knowledge 2 · pp.17–18"),
    Claim("Skills: restrict each subagent's tools to its role; replace generic tools with constrained ones (fetch_url → load_document "
          "that validates document URLs); give scoped cross-role tools (verify_fact for the synthesis agent) and route complex cases "
          "through the coordinator; force a specific tool first (extract_metadata before enrichment), then handle later steps in "
          "follow-up turns; use any to guarantee a tool call instead of conversational text.", "guide", "TS 2.3 · Skills 1–5 · pp.10–11"),
    Claim("Tool use with JSON schemas is the most reliable way to get schema-compliant structured output and removes JSON syntax "
          "errors — but not semantic errors (line items not summing to the total, values in the wrong field).",
          "guide", "TS 4.3 · Knowledge 1, 3 · pp.17–18"),
    Claim("Schema design: required vs optional; enums with \"other\" + a detail string; nullable fields where the source may lack the "
          "information (prevents fabricated values); an \"unclear\" enum value for ambiguous cases; any when several extraction schemas "
          "exist and the document type is unknown; format-normalisation rules in the prompt.", "guide", "TS 4.3 · Knowledge 4, Skills 1–6 · pp.17–18"),
    Claim("The guide lists three tool_choice options; the docs add none and document models/settings that reject forced tool use.",
          "guide", "TS 2.3 K4 / TS 4.3 K2 vs define-tools"),
    Claim("The adaptive first_choice() helper (force when supported, otherwise auto + an explicit instruction) is this page's pattern "
          "for writing code that works on both kinds of model.", "recommendation", "define-tools § Forcing tool use"),
    Claim("The documents, the “chatty document → auto answers in text” behaviour, the value invented for a required-but-missing field, "
          "the $-string type slip without strict, the 18-tool confusion and the synthesis agent's search misuse are invented; "
          "“mock-opus-5.5” stands for a model that rejects forced tool use.", "simulated", "utils/toolchoice_lab.py"),
)

CORRECT = r'''from utils.toolchoice_lab import (DOCUMENT, FORCED_TOOL_CHOICE_SUPPORTED, MODEL, TASK, create, run_agent, run_tool,
                                  submit_extraction)   # SIMULATED Messages API and agents

# strict: true -> inputs always match the schema. Nullable fields -> nothing invented when the document lacks it.
# "other" + a detail field -> categories you didn't foresee; "unclear" -> honest ambiguity.
INVOICE = {"name": "extract_invoice", "strict": True,
           "description": "Extracts an invoice: vendor, total, date, tax id and spend category.",
           "input_schema": {"type": "object", "additionalProperties": False,
                            "properties": {
                                "vendor": {"type": "string"},
                                "total": {"type": "number", "description": "A number, e.g. 1240.0 - no currency symbol"},
                                "invoice_date": {"type": ["string", "null"]},
                                "tax_id": {"type": ["string", "null"], "description": "null if the document shows no tax id - never guess"},
                                "category": {"type": "string", "enum": ["hardware", "software", "services", "other", "unclear"]},
                                "category_detail": {"type": ["string", "null"], "description": "What 'other' means"}},
                            "required": ["vendor", "total", "invoice_date", "tax_id", "category", "category_detail"]}}
CONTRACT = {"name": "extract_contract", "strict": True,
            "description": "Extracts a contract: the two parties, start date, term and fee.",
            "input_schema": {"type": "object", "additionalProperties": False,
                             "properties": {"party_a": {"type": "string"}, "party_b": {"type": "string"},
                                            "effective_date": {"type": ["string", "null"]},
                                            "term_months": {"type": ["integer", "null"]},
                                            "monthly_fee": {"type": ["number", "null"]}},
                             "required": ["party_a", "party_b", "effective_date", "term_months", "monthly_fee"]}}
METADATA = {"name": "extract_metadata", "strict": True, "description": "Extracts the vendor name and document type.",
            "input_schema": {"type": "object", "additionalProperties": False,
                             "properties": {"vendor": {"type": "string"}, "document_type": {"type": "string"}},
                             "required": ["vendor", "document_type"]}}
ENRICH = {"name": "enrich_vendor", "strict": True, "description": "Adds credit terms to a vendor record. Needs the vendor_id.",
          "input_schema": {"type": "object", "additionalProperties": False,
                           "properties": {"vendor_id": {"type": "string"}}, "required": ["vendor_id"]}}


def first_choice(name=None):
    """Guarantee a tool call: any (or one named tool) - on models that support forcing."""
    if not FORCED_TOOL_CHOICE_SUPPORTED:          # docs: some models reject any/tool with a 400
        return {"type": "auto"}                   # -> auto + strict tools + an explicit instruction instead
    return {"type": "tool", "name": name} if name else {"type": "any"}


instruction = "" if FORCED_TOOL_CHOICE_SUPPORTED else " Use the matching extraction tool."

if TASK == "extract":
    # the document type is unknown -> offer every extractor and require that ONE of them is called
    r = create(model=MODEL, tools=[INVOICE, CONTRACT], tool_choice=first_choice(),
               messages=[{"role": "user", "content": DOCUMENT + instruction}])
    submit_extraction(r)

elif TASK == "pipeline":
    messages = [{"role": "user", "content": DOCUMENT + " Extract the metadata, then enrich the vendor record."}]
    choice = first_choice("extract_metadata")     # step 1: force metadata extraction to run FIRST
    for turn in range(1, 6):
        r = create(model=MODEL, tools=[METADATA, ENRICH], tool_choice=choice, messages=messages)
        print(f"turn {turn}: {r.stop_reason} {[b.name for b in r.content if b.type == 'tool_use']}")
        if r.stop_reason != "tool_use":
            break
        messages.append({"role": "assistant", "content": r.content})
        messages.append({"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": b.id, "content": run_tool(b.name, b.input)}
            for b in r.content if b.type == "tool_use"]})
        choice = {"type": "auto"}                 # later steps: follow-up turns, the model continues on its own

else:  # distribute tools across agents
    run_agent("searcher", ["web_search", "load_document"])   # its role's tools only; load_document validates document URLs
    run_agent("synthesizer", ["verify_fact"])                 # a scoped cross-role tool for quick fact checks - no web search
'''


def _swap(code, old, new):
    assert old in code, f"lab code changed: {old[:60]!r}"
    return code.replace(old, new, 1)


VARIANT_A = _swap(CORRECT, '''    return {"type": "tool", "name": name} if name else {"type": "any"}''',
                  '''    return {"type": "auto"}   # WRONG: never force - the model may just answer in text''')
VARIANT_B = _swap(CORRECT, '''    r = create(model=MODEL, tools=[INVOICE, CONTRACT], tool_choice=first_choice(),''',
                  '''    r = create(model=MODEL, tools=[INVOICE, CONTRACT], tool_choice=first_choice("extract_invoice"),   # WRONG: assumes an invoice''')
VARIANT_C = _swap(CORRECT, '''        choice = {"type": "auto"}                 # later steps: follow-up turns, the model continues on its own''',
                  '''        # WRONG: the forced tool_choice is never released''')
VARIANT_D = _swap(CORRECT, '''    choice = first_choice("extract_metadata")     # step 1: force metadata extraction to run FIRST''',
                  '''    choice = first_choice()                       # WRONG: "any tool" - nothing makes metadata come first''')
VARIANT_E = _swap(_swap(_swap(CORRECT,
                  '''"tax_id": {"type": ["string", "null"], "description": "null if the document shows no tax id - never guess"},''',
                  '''"tax_id": {"type": "string"},   # WRONG: required and not nullable'''),
                  '''"category": {"type": "string", "enum": ["hardware", "software", "services", "other", "unclear"]},
                                "category_detail": {"type": ["string", "null"], "description": "What 'other' means"}},''',
                  '''"category": {"type": "string", "enum": ["hardware", "software", "services"]}},   # WRONG: closed enum'''),
                  '''"required": ["vendor", "total", "invoice_date", "tax_id", "category", "category_detail"]}}''',
                  '''"required": ["vendor", "total", "invoice_date", "tax_id", "category"]}}''')
VARIANT_F = _swap(_swap(CORRECT, '''    run_agent("searcher", ["web_search", "load_document"])''',
                        '''    from utils.toolchoice_lab import ALL_TOOLS
    run_agent("searcher", ALL_TOOLS)       # WRONG: all 18 tools for every agent'''),
                  '''    run_agent("synthesizer", ["verify_fact"])''', '''    run_agent("synthesizer", ALL_TOOLS)''')
VARIANT_G = _swap(CORRECT, '''    if not FORCED_TOOL_CHOICE_SUPPORTED:          # docs: some models reject any/tool with a 400
        return {"type": "auto"}                   # -> auto + strict tools + an explicit instruction instead
''', '''    # WRONG: assumes every model supports forced tool use
''')
VARIANT_H = _swap(CORRECT, '''INVOICE = {"name": "extract_invoice", "strict": True,''', '''INVOICE = {"name": "extract_invoice",   # WRONG: no strict: true''')

# ── Check and chart ────────────────────────────────────────────────────────────

_WANT_TOOL = {"must_extract": "extract_invoice", "unknown_type": "extract_contract", "missing_fields": "extract_invoice",
              "model_rejects_forcing": "extract_invoice"}


def _facts(trace):
    ev = trace["events"]
    return {"scenario": trace["status"].get("scenario"), "raised": trace["status"]["raised"],
            "calls": [e for e in ev if e["kind"] == "tc_call"], "sub": next((e for e in reversed(ev) if e["kind"] == "tc_submit"), None),
            "agents": {e["role"]: e for e in ev if e["kind"] == "tc_agent"}}


def _diagnose(f):
    sc, calls = f["scenario"], f["calls"]
    if f["raised"]:
        return False, ("FORCEREJECT" if "forced tool use" in f["raised"] else None), f"raised: {f['raised'][:160]}"
    if sc in _WANT_TOOL:
        s = f["sub"]
        if s is None:
            return False, None, "no extraction submitted"
        last = calls[-1] if calls else {}
        inp = s["input"] or {}
        money = inp.get("total", inp.get("monthly_fee"))
        txt = (f"tool_choice {last.get('tool_choice')} · called: {s['tool'] or 'NO TOOL (text reply)'} · input: {inp} · "
               f"invented values: {last.get('fabricated') or 'none'} · forced into a category: {last.get('miscategorized') or 'none'}")
        if s["tool"] is None:
            return False, "AUTO", txt
        if s["tool"] != _WANT_TOOL[sc]:
            return False, "WRONGFORCE", txt
        if last.get("fabricated") or last.get("miscategorized"):
            return False, "SCHEMA", txt
        if isinstance(money, str):
            return False, "NOSTRICT", txt
        if sc == "missing_fields" and not (inp.get("tax_id") is None and inp.get("category") == "other" and inp.get("category_detail")):
            return False, "SCHEMA", txt
        return True, None, txt
    if sc == "metadata_first":
        seq = [c["tool"] for c in calls]
        enrich = [c for c in calls if c["tool"] == "enrich_vendor"]
        txt = f"calls: {seq} · enrich input: {[c['input'] for c in enrich] or 'never called'}"
        if not seq or seq[0] != "extract_metadata":
            return False, "NOFORCE", txt
        if not enrich:
            return False, "STUCK", txt
        if any(c["fabricated"] for c in enrich):
            return False, "NOFORCE", txt
        return seq[-1] is None, (None if seq[-1] is None else "STUCK"), txt
    a = f["agents"]
    s_, y = a.get("searcher"), a.get("synthesizer")
    if not s_ or not y:
        return False, None, "both agents must run"
    txt = (f"searcher {len(s_['tools'])} tools → {s_['calls']} · synthesizer {len(y['tools'])} tools → {y['calls']}")
    bad = (len(s_["tools"]) > 5 or len(y["tools"]) > 5 or any("fetch_url" in c for c in s_["calls"])
           or any(c.startswith("web_search") for c in y["calls"]) or not any(c.startswith("verify_fact") for c in y["calls"])
           or "web_search" not in s_["calls"])
    return (not bad), ("TOOMANY" if bad else None), txt


EXPECTED = {
    "must_extract": "a guaranteed extraction tool call (not a chatty text reply), total as a number",
    "unknown_type": "the CONTRACT extractor chosen for a contract (not a forced invoice schema), nothing invented",
    "missing_fields": "tax_id null (not invented), category 'other' + detail 'maintenance', total as a number",
    "metadata_first": "extract_metadata first, then enrich_vendor once with the real vendor id, then the model finishes",
    "scoped_tools": "each agent ≤ 5 role tools; searcher uses web_search + load_document; synthesizer uses verify_fact, never web_search",
    "model_rejects_forcing": "the extraction still happens on a model that rejects forced tool use (no 400)",
}


def check_outcome(scenario, trace):
    ok, _b, txt = _diagnose(_facts(trace))
    return ok, EXPECTED[scenario], txt


_CONCEPT = {
    "q":      ("#EDE9FE", "#7C3AED", "the decision"),
    "choice": ("#DBEAFE", "#0066CC", "tool_choice"),
    "schema": ("#FEF3C7", "#D97706", "schema design (strict, nullable, enums)"),
    "dist":   ("#CCFBF1", "#0D9488", "tool distribution across agents"),
    "docs":   ("#F3F4F6", "#6B7280", "📘 docs-only (not in the guide)"),
    "bug":    ("#FFFFFF", "#DC2626", "bug (a distractor)"),
}
_NODES = {
    "Q":      ("What must be guaranteed?", "diamond", "q"),
    "AUTO":   ("⭐ auto — the model may\\nanswer in text (default)", "box", "choice"),
    "ANY":    ("⭐ any — must call SOME tool\\n(type unknown: it picks)", "box", "choice"),
    "FORCE":  ("⭐ tool — must call THIS tool\\n(first step), then release", "box", "choice"),
    "NONE":   ("none — no tools", "box", "docs"),
    "NOSUP":  ("Model rejects forcing (400)?\\n→ auto + strict + instruction", "box", "docs"),
    "STRICT": ("⭐ strict schema: types guaranteed;\\nnullable where data may be missing;\\n“other” + detail, “unclear”", "box", "schema"),
    "SCOPE":  ("⭐ each agent: 4–5 role tools\\n+ scoped cross-role tool", "box", "dist"),
    "OUT":    ("Right tool, schema-valid input,\\nnothing invented", "box", "q"),
    "AUTOBUG": ("✗ auto when a tool\\ncall must happen", "box", "bug"),
    "WRONGFORCE": ("✗ forcing one schema\\nfor unknown types", "box", "bug"),
    "STUCK":  ("✗ forced every turn", "box", "bug"),
    "NOFORCE": ("✗ nothing forces the\\nfirst step", "box", "bug"),
    "SCHEMA": ("✗ required non-null /\\nclosed enums → invented values", "box", "bug"),
    "NOSTRICT": ("✗ no strict: a “$1,240.00”\\nstring in a number field", "box", "bug"),
    "TOOMANY": ("✗ 18 tools for every agent", "box", "bug"),
    "FORCEREJECT": ("✗ forcing on a model\\nthat rejects it", "box", "bug"),
}
_BUGS = ["AUTOBUG", "WRONGFORCE", "STUCK", "NOFORCE", "SCHEMA", "NOSTRICT", "TOOMANY", "FORCEREJECT"]
_BUGMAP = {"AUTO": "AUTOBUG"}
_EXP = {"must_extract": ["ANY", "STRICT"], "unknown_type": ["ANY"], "missing_fields": ["STRICT"], "metadata_first": ["FORCE"],
        "scoped_tools": ["SCOPE"], "model_rejects_forcing": ["NOSUP"]}


def _key(hl):
    rows = "".join(f'<TR><TD BGCOLOR="{f}" WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14"></TD><TD ALIGN="LEFT" BORDER="0"><FONT '
                   f'POINT-SIZE="10">{t}</FONT></TD></TR>' for f, _l, t in _CONCEPT.values())
    rows += ('<TR><TD WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14">⭐</TD><TD ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">named by '
             'the exam guide (TS 2.3 pp.10–11, TS 4.3 pp.17–18)</FONT></TD></TR>')
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
    lines += ['  Q -> AUTO [label="nothing"]; Q -> ANY [label="a tool call"]; Q -> FORCE [label="this tool first"]; Q -> NONE [label="no tools"];',
              "  { rank=same; AUTO; ANY; FORCE; NONE; }", "  ANY -> NOSUP [style=dashed]; FORCE -> NOSUP [style=dashed];",
              "  ANY -> STRICT; FORCE -> STRICT; AUTO -> STRICT; STRICT -> OUT; SCOPE -> Q;",
              "  { rank=same; " + "; ".join(_BUGS[:4]) + "; }", "  { rank=same; " + "; ".join(_BUGS[4:]) + "; }",
              "  OUT -> AUTOBUG [style=invis]; AUTOBUG -> SCHEMA [style=invis];", _key(hl), "  SCHEMA -> KEY [style=invis];", "}"]
    return readable("\n".join(lines))   # FLOWCHART RULE: 18pt, max 2 nodes per row


def node_states(trace):
    if not trace:
        return {}
    f = _facts(trace)
    ok, bug, _ = _diagnose(f)
    s = {"Q": ("ok", ""), "OUT": ("ok", "") if ok else ("bad", "not achieved")}
    for n in _EXP.get(f["scenario"], []):
        s[n] = ("ok", "" if ok else "what this scenario needs")
    if bug:
        s[_BUGMAP.get(bug, bug)] = ("bad", "your run")
    return s


EXAM_POINTS = (
    ExamPoint("2.3", "K", 1, "Too many tools (e.g. 18 instead of 4–5) degrade tool-selection reliability.", "❌ F · playground “Tool distribution”"),
    ExamPoint("2.3", "K", 2, "Agents with tools outside their specialisation misuse them (a synthesis agent doing web searches).", "❌ F"),
    ExamPoint("2.3", "K", 3, "Scoped tool access: only the role's tools, plus limited cross-role tools for specific high-frequency needs.",
              "✅ scoped_tools"),
    ExamPoint("2.3", "K", 4, "tool_choice options: \"auto\", \"any\", and forced {\"type\": \"tool\", \"name\": …}.", "✅ first_choice() · playground “tool_choice modes”"),
    ExamPoint("2.3", "S", 1, "Restrict each subagent's tool set to its role to prevent cross-specialisation misuse.", "✅ run_agent tool lists · ❌ F"),
    ExamPoint("2.3", "S", 2, "Replace generic tools with constrained ones (fetch_url → load_document that validates document URLs).",
              "✅ load_document · playground “Tool distribution”"),
    ExamPoint("2.3", "S", 3, "Give scoped cross-role tools for high-frequency needs (verify_fact for the synthesis agent); route complex cases "
              "through the coordinator.", "✅ synthesizer → verify_fact"),
    ExamPoint("2.3", "S", 4, "Force a specific tool so it runs first (extract_metadata before enrichment), then handle later steps in follow-up turns.",
              "✅ metadata_first · ❌ C · ❌ D"),
    ExamPoint("2.3", "S", 5, "Set tool_choice \"any\" to guarantee a tool call rather than conversational text.", "✅ must_extract · ❌ A"),
    ExamPoint("4.3", "K", 1, "Tool use with JSON schemas is the most reliable route to schema-compliant output and removes JSON syntax errors.",
              "✅ strict extractors · ❌ H"),
    ExamPoint("4.3", "K", 2, "auto may return text; any must call a tool but chooses which; forced must call the named tool.", "✅ · ❌ A · ❌ B"),
    ExamPoint("4.3", "K", 3, "Strict schemas remove syntax errors but not semantic errors (totals that don't add up, values in the wrong field).",
              "FAQ · playground “strict ≠ correct”"),
    ExamPoint("4.3", "K", 4, "Schema design: required vs optional fields; enums with \"other\" + a detail string for extensible categories.",
              "✅ INVOICE schema · ❌ E"),
    ExamPoint("4.3", "S", 1, "Define extraction tools with JSON-schema inputs and read the structured data from the tool_use block.", "✅ submit_extraction(r)"),
    ExamPoint("4.3", "S", 2, "Use any to guarantee structured output when several extraction schemas exist and the document type is unknown.",
              "✅ unknown_type · ❌ B"),
    ExamPoint("4.3", "S", 3, "Force a specific tool (e.g. extract_metadata) so that extraction runs before enrichment.", "✅ metadata_first"),
    ExamPoint("4.3", "S", 4, "Make fields optional/nullable when the source may not contain them, so the model doesn't fabricate values.",
              "✅ tax_id nullable · ❌ E"),
    ExamPoint("4.3", "S", 5, "Add enum values like \"unclear\" for ambiguous cases and \"other\" + detail for extensible categories.", "✅ · ❌ E"),
    ExamPoint("4.3", "S", 6, "Put format-normalisation rules in the prompt alongside strict schemas to handle inconsistent source formatting.",
              "✅ total's description (“a number, no currency symbol”) · FAQ"),
)

VARIANTS = (
    Variant("correct", "✅ ⭐ any to guarantee, force to sequence, strict + nullable schemas, scoped tools", "correct", CORRECT, "must_extract",
            observe=("must_extract: tool_choice any → extract_invoice is called (no text before it), total comes back as 1240.0. "
                     "unknown_type: any lets the model pick extract_contract for a contract. missing_fields: tax_id null, category "
                     "“other” + “maintenance”, nothing invented. metadata_first: extract_metadata (forced) → enrich_vendor(V-4471) → the "
                     "model finishes on auto. scoped_tools: searcher uses web_search + load_document (which rejects the login page), "
                     "synthesizer uses verify_fact. model_rejects_forcing: first_choice() falls back to auto + an explicit instruction, "
                     "so extraction still happens without a 400."),
            why=("Each guarantee comes from the right lever: any for “a tool must be called”, a forced tool for “this step first”, a "
                 "strict schema for types, nullable/“other” fields for honesty, scoped tool lists for role discipline — and a fallback "
                 "where the docs say forcing isn't supported.")),
    Variant("A", "⭐❌ A — auto where a tool call must happen", "distractor", VARIANT_A, "must_extract",
            observe=("The invoice arrives in a friendly email; on auto the simulated model replies “Thanks for sharing! This looks like "
                     "an invoice from Acme Parts Ltd.” — no tool call, nothing to store. Same on unknown_type and missing_fields; on "
                     "metadata_first it jumps to enrich_vendor with an invented vendor id (V-0000) five times."),
            why="auto lets the model decide whether to call a tool at all; a pipeline that needs structured output must guarantee the call.",
            fix="tool_choice any (or a forced tool) where a tool call must happen.", source="guide:2.3:S5"),
    Variant("B", "⭐❌ B — force the invoice schema on every document", "distractor", VARIANT_B, "unknown_type",
            observe=("The document is a contract, but extract_invoice is forced: vendor “(guessed vendor)”, total 0, category "
                     "“(guessed category)” — three invented values to fill a schema that doesn't fit."),
            why="Forcing one named tool is for a step that must run; when the document type is unknown, any lets the model choose the right schema.",
            fix="Offer all extractors with tool_choice any.", source="guide:4.3:S2"),
    Variant("C", "⭐❌ C — the forced tool_choice is never released", "distractor", VARIANT_C, "metadata_first",
            observe="extract_metadata is forced on turns 1–5: it runs five times and enrich_vendor never does.",
            why="Forcing is for the first step; later steps belong to follow-up turns where the model is free to choose.",
            fix="Force extract_metadata on the first call only, then switch to auto (or any).", source="guide:2.3:S4"),
    Variant("D", "⭐❌ D — nothing forces the first step", "distractor", VARIANT_D, "metadata_first",
            observe=("With any from the start the model goes straight to enrich_vendor — without a vendor id, so it invents V-0000, "
                     "gets “unknown vendor id” and keeps trying."),
            why="any guarantees A tool, not WHICH one; ordering needs the forced form for the first call.",
            fix="tool_choice {\"type\": \"tool\", \"name\": \"extract_metadata\"} on the first call.", source="guide:2.3:S4"),
    Variant("E", "⭐❌ E — tax_id required and non-null, a closed enum", "distractor", VARIANT_E, "missing_fields",
            observe=("The invoice has no tax id: the required non-null field gets “(guessed tax_id)”. Its category, maintenance, isn't in "
                     "[hardware, software, services], so it is forced into “hardware”. Both are schema-valid — and wrong."),
            why="A required field makes the model produce SOMETHING; a closed enum makes it pick the nearest wrong category.",
            fix="Nullable fields for data the source may lack; enums with “other” + a detail field (and “unclear”).", source="guide:4.3:S4"),
    Variant("F", "⭐❌ F — all 18 tools for every agent", "distractor", VARIANT_F, "scoped_tools",
            observe=("With 18 tools the searcher picks search_internal_wiki instead of web_search, and the synthesis agent runs a "
                     "web_search itself — doing the searcher's job — instead of a quick verify_fact."),
            why="More tools mean harder choices, and tools outside an agent's role get misused.",
            fix="4–5 role tools per agent, plus a scoped cross-role tool (verify_fact) for the synthesizer.", source="guide:2.3:K1"),
    Variant("G", "❌ G — force tool_choice on a model that rejects it", "distractor", VARIANT_G, "model_rejects_forcing",
            observe="The simulated model rejects forced tool use: 400 invalid_request_error — the extraction never happens.",
            why=("The docs list models (Claude Opus 5.5, Fable 5.1, Mythos 5.1) and a setting (manual extended thinking) where any/tool "
                 "are rejected; auto and none still work."),
            fix="Use auto with strict tools and an explicit instruction (or structured outputs) where forcing isn't supported.",
            source="docs"),
    Variant("H", "⭐❌ H — no strict: true on the extractor", "distractor", VARIANT_H, "must_extract",
            observe=("total comes back as the string “$1,240.00” in a number field — your downstream code now has a type error. "
                     "Also fails missing_fields and model_rejects_forcing; the contract extractor (still strict) is fine."),
            why=("Tool use with a JSON schema is the reliable route to structured output; strict: true is what guarantees the input "
                 "matches the schema's types (docs)."),
            fix="Set strict: true (with additionalProperties: false) on extraction tools.", source="guide:4.3:K1"),
)

TLDR = (
    "`tool_choice` decides **whether** and **which** tool must be called: **`auto`** (default — the model may just answer in text), "
    "**`any`** (must call *some* tool — the model picks), **`{\"type\":\"tool\",\"name\":…}`** (must call *that* tool), and — per the "
    "docs — **`none`**. Use `any` to **guarantee** structured output, a **forced tool** to make a step run **first** (then release it), "
    "`strict: true` + **nullable fields** + **“other”/“unclear” enums** so schemas neither break nor invent. Give each agent only its "
    "**role's 4–5 tools**. And know the docs' caveat: some models and manual extended thinking **reject forced tool use** (400)."
)
MENTAL_MODEL = ("tool_choice is how you hand the model a menu: “order if you like” (auto), “you must order something” (any), “you must "
                "order the soup first” (tool) — and a strict schema is the order form with boxes that only take numbers. A good "
                "form has a “none / other: ____” box; without one, people tick something wrong.")

WHAT_IT_IS = """
The exam guide covers distributing tools and configuring `tool_choice` (Guide §6 · TS 2.3, pp.10–11) and getting structured output
through tool use and JSON schemas (TS 4.3, pp.17–18). The docs define the options and their limits.

**Sub-concepts — each with its picture to remember**

| # | Sub-concept | 🧭 Mental model | ⭐ Exam reference |
|---|---|---|---|
| 1 | `auto` | “Order if you like” — the model may just chat. | ⭐ TS 2.3 · Knowledge 4; TS 4.3 · Knowledge 2 |
| 2 | `any` | “You must order something” — guaranteed tool call, the model picks which. | ⭐ TS 2.3 · Skill 5; TS 4.3 · Skill 2 |
| 3 | Forced `tool` | “The soup first” — sequence a step, then let the model choose again. | ⭐ TS 2.3 · Skill 4; TS 4.3 · Skill 3 |
| 4 | `none` | Menu closed. | 📘 docs only |
| 5 | Forcing not supported | Some kitchens don't take fixed orders: ask nicely (auto + instruction) and use a strict form. | 📘 docs only |
| 6 | Strict schema | A form whose boxes only accept the right type — no “two” in a number box. | ⭐ TS 4.3 · Knowledge 1 |
| 7 | Syntax ≠ semantics | A perfectly filled form can still have the wrong total. | ⭐ TS 4.3 · Knowledge 3 |
| 8 | Nullable / “other” / “unclear” | A “not stated”, “other: ____” and “not sure” box, so nobody ticks something false. | ⭐ TS 4.3 · Knowledge 4, Skills 4–5 |
| 9 | Scoped tools per agent | Give each worker their own toolbox; one shared box of 18 tools means wrong tools grabbed. | ⭐ TS 2.3 · Knowledge 1–3, Skills 1–3 |

**tool_choice: auto vs any vs forced** (the comparison CLAUDE.md requires)

| # | Aspect | `auto` | `any` | forced `{"type":"tool","name":…}` | `none` (docs) |
|---|---|---|---|---|---|
| 1 | Must a tool be called? | No — text is allowed | Yes | Yes | No tools |
| 2 | Which tool? | Model decides | Model picks one of yours | The one you name | — |
| 3 | Text before the tool call? | Often | No (prefilled) | No (prefilled) | — |
| 4 | Use it for | Normal agent turns | Guaranteed structured output, type unknown | A step that must run first | Turning tools off |
| 5 | Default when | Tools are provided | — | — | No tools are provided |
| 6 | Not supported with | — | Manual extended thinking; Opus 5.5 / Fable 5.1 / Mythos 5.1 (400) | Same | — |
| 7 | Exam reference | TS 2.3 K4 · TS 4.3 K2 | TS 2.3 S5 · TS 4.3 S2 | TS 2.3 S4 · TS 4.3 S3 | 📘 docs |

**Schema design that doesn't invent**

| # | Field situation | Schema choice | Why (guide) |
|---|---|---|---|
| 1 | Might be missing from the source | `"type": ["string", "null"]` | Prevents fabricated values (TS 4.3 S4) |
| 2 | Categories you can't fully foresee | enum + `"other"` + a `*_detail` string | Extensible (TS 4.3 K4, S5) |
| 3 | Genuinely ambiguous | enum value `"unclear"` | Honest ambiguity (TS 4.3 S5) |
| 4 | Numbers written inconsistently (“$1,240.00”) | `number` type + a normalisation rule in the description/prompt | TS 4.3 S6 |
"""

HOW_IT_WORKS = """
1. **Decide what must be guaranteed.** Nothing → `auto`. A tool call → `any`. A specific first step → forced tool, then release it.
2. **Check the model supports forcing.** If not (docs: Opus 5.5, Fable 5.1, Mythos 5.1, or manual extended thinking), use `auto` with
   strict tools and an explicit instruction — or structured outputs.
3. **Make extraction schemas honest:** `strict: true`, `additionalProperties: false`, nullable where data may be missing, `other` +
   detail and `unclear` in enums, normalisation rules for messy formats.
4. **Validate semantics yourself** — strict guarantees types, not that totals add up (validation/retry is TS 4.4).
5. **Distribute tools:** each agent gets its role's 4–5 tools, constrained versions of risky generic tools, and a scoped cross-role
   tool for frequent needs; complex cases go back through the coordinator.
"""

WHERE_SEEN = """
- **Scenario 6 — Structured Data Extraction** (Guide §5, p.4): schemas, any/forced tool_choice, nullable fields, enums.
- **Scenario 3 — Multi-Agent Research System** (Guide §5, p.4): scoped tools per agent, verify_fact for the synthesizer.
- **Scenario 1 — Customer Support Resolution Agent** (Guide §5, p.3): tool distribution for support agents.
"""

GUIDE_NOTE = ("Grounded in the exam guide §6 TS 2.3 (pp.10–11) and TS 4.3 (pp.17–18), and the platform and Agent SDK docs (verified "
              "2026-09-27 — pages listed above). Section layout inspired by a community concept list (claudearchitectcertification.com "
              "— community source, unverified; no text copied).")

LAB_INTRO = """
You write the **tool definitions, the tool_choice for each call and each agent's tool list**. The **simulated** API enforces the documented
rules (no text before a forced call; a 400 where forcing isn't supported) and the simulated model fills schemas the way the guide warns
about — inventing values for required fields the document lacks. Six situations; seven mistakes from the exam guide (⭐), one from the docs.
"""

DISTRACTORS = (
    ("A · auto where a tool call must happen", "The model usually calls the tool.", "“Usually” — a chatty document gets a chatty reply.",
     "any (or a forced tool).", "guide:2.3:S5"),
    ("B · Force one schema for unknown types", "Forcing guarantees extraction.", "The wrong schema gets filled with invented values.",
     "any across all extractors.", "guide:4.3:S2"),
    ("C · Force on every turn", "Keeps the model on track.", "The forced step repeats; later steps never run.",
     "Force the first call only.", "guide:2.3:S4"),
    ("D · Nothing forces the first step", "any guarantees a tool call.", "Any tool — the wrong one runs first.",
     "Force the named first tool.", "guide:2.3:S4"),
    ("E · Required non-null fields, closed enums", "Required fields make the output complete.", "Missing data is invented; odd categories mislabelled.",
     "Nullable fields; other + detail; unclear.", "guide:4.3:S4"),
    ("F · Every agent gets every tool", "More capability can't hurt.", "Selection degrades; agents misuse tools outside their role.",
     "4–5 role tools + a scoped cross-role tool.", "guide:2.3:K1"),
    ("G · Force on a model that rejects it", "Forcing is the documented way.", "Some models / manual thinking return a 400.",
     "auto + strict + an instruction, or structured outputs.", "docs"),
    ("H · No strict: true", "The schema already says number.", "Without strict, “$1,240.00” can land in a number field.",
     "strict: true + additionalProperties: false.", "guide:4.3:K1"),
)

SIDE_BY_SIDE_HEADERS = ("#", "Aspect", "Tool use + strict schema", "JSON outputs (structured outputs)", "Prompt “reply in JSON”")
SIDE_BY_SIDE_ROWS = (
    ("1", "Guarantees", "Tool input matches the schema; valid tool name", "Response text is valid JSON matching the schema", "Nothing"),
    ("2", "Where the data is", "The tool_use block's input", "A text block", "Wherever the model put it"),
    ("3", "Semantic correctness", "Not guaranteed", "Not guaranteed", "Not guaranteed"),
    ("4", "Exam view", "The guide's most reliable approach (TS 4.3 K1)", "📘 docs alternative, incl. where forcing is rejected", "Syntax errors possible"),
)

DECISION_DOT = '''digraph D {
  rankdir=TB; bgcolor="transparent"; nodesep=0.35; ranksep=0.4;
  node [fontname="Helvetica", fontsize=12, style="rounded,filled", fillcolor="#F3F4F6", color="#9CA3AF", penwidth=1.5];
  edge [fontname="Helvetica", fontsize=11, color="#6B7280"];
  Q1 [shape=diamond, label="Must a tool be called\\non this turn?"];
  AUTO [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="auto"];
  Q2 [shape=diamond, label="Must it be ONE specific tool\\n(a first step)?"];
  ANY [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="any\\n(type unknown: the model picks)"];
  FORCE [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="tool: name — then release\\nto auto on later turns"];
  Q3 [shape=diamond, label="Does this model / setting\\nsupport forcing?"];
  FALL [shape=box, fillcolor="#FEF3C7", color="#D97706", label="auto + strict tools + explicit\\ninstruction (or structured outputs)"];
  OK [shape=box, fillcolor="#D1FAE5", color="#059669", label="Send it; strict schema with\\nnullable / other / unclear"];
  Q1 -> AUTO [label="no"]; Q1 -> Q2 [label="yes"]; Q2 -> FORCE [label="yes"]; Q2 -> ANY [label="no"];
  ANY -> Q3; FORCE -> Q3; Q3 -> FALL [label="no"]; Q3 -> OK [label="yes"]; FALL -> OK; AUTO -> OK;
}'''

EXPERIMENTS = (
    "Run ✅ on every scenario and read the tool_choice and the call sequence in the output.",
    "In ✅, change first_choice() to always return {\"type\": \"auto\"} and run must_extract — that's ⭐❌ A.",
    "Run ⭐❌ E on missing_fields and compare its tax_id and category with ✅'s.",
    "Run ❌ G on model_rejects_forcing, then read how ✅'s first_choice() avoids the 400.",
    "In ✅, give the synthesizer [\"verify_fact\", \"web_search\"] and run scoped_tools: what does it do with the extra tool?",
)

QUESTIONS = (
    Question(
        q=("An invoice-extraction pipeline defines one extraction tool, but on short or odd documents Claude sometimes "
           "replies in plain text (“This appears to be a receipt…”) instead of calling it, and the parser crashes. "
           "tool_choice is “auto”. What's the most direct fix?"),
        opts=("Add “always call the tool” to the system prompt.",
              "Parse the text reply with a regex when it happens.",
              "Set tool_choice to “any”, so the model must call a tool instead of answering in text.",
              "Lower the temperature to zero."),
        ans=2,
        explain=("With “auto” the model may answer in text. “any” guarantees a tool call. A prompt instruction improves "
                 "the odds but guarantees nothing."),
        scenarios=(6,), points=("2.3:K4", "2.3:S5", "4.3:K2"),
    ),
    Question(
        q=("Incoming documents may be invoices, receipts or contracts, each with its own extraction tool and schema. The "
           "type isn't known in advance, and every document must produce structured output. How should tool_choice be set?"),
        opts=("“any” with all three tools, so the model must call one and picks which fits the document.",
              "Force the invoice tool, then retry with the others if it fails.",
              "“auto”, trusting the model to call the right tool.",
              "Classify the document in a separate call and parse its text answer."),
        ans=0,
        explain=("“any” guarantees structured output when several extraction schemas exist and the type is unknown: "
                 "the model must call a tool but chooses which. Forcing one tool would push contracts into the invoice schema."),
        scenarios=(6,), points=("4.3:S2", "4.3:K2"),
    ),
    Question(
        q=("In an extraction workflow, extract_metadata must always run first. After that, the model should decide "
           "freely between enrichment tools or answer. How should tool_choice be configured?"),
        opts=("“any” on every turn.",
              "“auto” on every turn, with “call extract_metadata first” in the prompt.",
              "Force extract_metadata on every turn.",
              "Force extract_metadata on the first request, then use “auto” on the follow-up turns."),
        ans=3,
        explain=("Forcing {\"type\": \"tool\", \"name\": \"extract_metadata\"} guarantees it runs first. Later steps are "
                 "handled in follow-up turns with normal choice. Forcing it every turn would loop the same tool."),
        scenarios=(6,), points=("2.3:S4", "4.3:S3"),
    ),
    Question(
        q=("An extraction schema marks tax_id as a required string. Audits find plausible-looking but invented tax ids on "
           "invoices that don't contain one. What's the best schema change?"),
        opts=("Add “never invent values” to the tool description.",
              "Make tax_id optional/nullable, so the model can report it as absent.",
              "Validate tax ids with a checksum and retry until one passes.",
              "Change tax_id from a string to an integer."),
        ans=1,
        explain=("A required field pushes the model to fill it even when the source has nothing. Making it "
                 "optional/nullable lets it report absence. A retry loop can't produce information that isn't there."),
        scenarios=(6,), points=("4.3:S4", "4.3:K4"),
    ),
    Question(
        q=("A document_type enum lists invoice, receipt and contract. New kinds, such as credit notes and delivery "
           "slips, keep being squeezed into “receipt”, and some scans are too blurry to classify. What's the best "
           "schema design?"),
        opts=("Add every future document type to the enum now.",
              "Remove the enum and accept free text.",
              "Add “other” with a detail string for new kinds, and “unclear” for documents that can't be classified.",
              "Make document_type required so the model tries harder."),
        ans=2,
        explain=("An enum with “other” plus a detail string handles extensible categories, and “unclear” covers "
                 "ambiguous cases, while keeping the field structured. Free text loses the structure."),
        scenarios=(6,), points=("4.3:K4", "4.3:S5"),
    ),
    Question(
        q=("In the research system, every agent gets all 18 tools. The synthesis agent keeps running web searches of its "
           "own instead of synthesising, and reports drift off-brief. What's the best change?"),
        opts=("Tell the synthesis agent not to search unless necessary.",
              "Lower the synthesis agent's max_turns.",
              "Put the web search tools last in the list.",
              "Restrict each agent's tools to its role, so the synthesis agent has no general web search."),
        ans=3,
        explain=("Agents given tools outside their specialisation tend to misuse them. Scoped tool access per role "
                 "prevents that. A prompt request is probabilistic, and tool order doesn't change what's available."),
        scenarios=(3,), points=("2.3:K2", "2.3:S1"),
    ),
    Question(
        q=("After scoping, the synthesis agent often needs to check a single fact (a date, a figure) and each check takes "
           "a slow round trip through the coordinator to the search agent. About 85% of checks are that simple. What's "
           "the best design?"),
        opts=("Give the synthesis agent a narrowly scoped verify_fact tool, and keep complex verification routed through the coordinator.",
              "Give the synthesis agent every web search tool back.",
              "Let the synthesis agent message the search agent directly.",
              "Skip verification for simple facts."),
        ans=0,
        explain=("Scoped cross-role tools for high-frequency needs cut the round trips, while complex cases still go "
                 "through the coordinator. Full tool access brings back the misuse, and direct messaging bypasses the hub."),
        scenarios=(3,), points=("2.3:S3", "2.3:K3"),
    ),
    Question(
        q=("A document-analysis subagent has a generic fetch_url tool. It sometimes fetches unrelated web pages, and even "
           "tracking pixels, instead of the documents it was given. What's the best fix?"),
        opts=("Add “only fetch documents” to fetch_url's description.",
              "Log every fetch and review them weekly.",
              "Give the subagent a larger context window.",
              "Replace fetch_url with a constrained load_document tool that only accepts and validates document URLs."),
        ans=3,
        explain=("Replacing a generic tool with a constrained one (fetch_url → load_document, which validates its "
                 "input) removes the misuse at the source. A description change still leaves the generic capability there."),
        scenarios=(3,), points=("2.3:S2",),
    ),
    Question(
        q=("A single support agent was given 18 tools as features were added: refunds, shipping, loyalty, marketing and "
           "analytics. Tool-selection mistakes rose with each addition. Which design best restores reliability?"),
        opts=("Rewrite all 18 descriptions to be twice as long.",
              "Split the work across focused agents, each with the 4–5 tools its job needs.",
              "Number the tools so the model can refer to them precisely.",
              "Add examples of all 18 tools to the system prompt."),
        ans=1,
        explain=("Too many tools (such as 18 instead of 4–5) degrade selection reliability. Scoping tools to focused "
                 "roles addresses that. Longer descriptions and examples add context without reducing the choice."),
        scenarios=(1,), points=("2.3:K1", "2.3:K3"),
    ),
    Question(
        q=("An extraction service that sets tool_choice {\"type\": \"any\"} starts getting HTTP 400 errors after being "
           "moved to a newer model. According to the tool-use docs, what's the right adjustment?"),
        opts=("Retry the request, since a 400 is transient.",
              "Switch to forcing a specific tool instead of “any”.",
              "Use tool_choice “auto” with strict tools, or structured outputs, on models that don't support forced tool use.",
              "Remove the tools and parse JSON from the text."),
        ans=2,
        explain=("Per the docs, forced tool use (“any” or a named tool) isn't supported on some models or with manual "
                 "extended thinking, and returns a 400. The documented route is “auto” with strict tools, or structured outputs."),
        scenarios=(6,), basis="docs", in_bank=False,
    ),
)


FAQ = (
    ("Why can't I get an explanation with a forced tool call?",
     "With any or tool the API prefills the assistant turn, so no text precedes the tool_use block. Use auto with an explicit instruction "
     "in the user message if you need both (docs)."),
    ("Does strict: true make the data correct?",
     "No. It guarantees the input matches the schema (types, required fields, valid tool name). Whether the total matches the line items "
     "is yours to validate — the exam's syntax-vs-semantics point."),
    ("Is `none` on the exam?",
     "The guide names auto, any and forced. none (no tools) comes from the docs; it is also the default when no tools are provided."),
    ("Which models reject forced tool use?",
     "At the time of fetching (2026-09-27) the docs listed Claude Opus 5.5, Fable 5.1 and Mythos 5.1, plus manual extended thinking. "
     "Check the docs' table — it can change."),
    ("How is load_document different from fetch_url?",
     "It's the guide's example of a constrained replacement for a generic tool: it only loads document URLs and rejects anything else, "
     "so an agent can't wander onto login pages or trackers."),
)

PLAYGROUND_INTRO = """
Type an instruction to send with the document and choose the settings. Each run shows the request (tools, tool_choice, strict),
whether the API accepted it, whether text came before the tool call, which tool ran and the exact input — with any invented values
or mis-categorisations flagged.
"""


def _tab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this):
    return PlayTab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this, engine="toolchoice")


PLAYGROUND = (
    _tab("modes", "⭐ tool_choice modes", "modes", "“Order if you like” / “order something” / “order the soup” / menu closed.", "guide:2.3:K4",
         "The same chatty document under auto, any, a forced tool, or none — and with an invoice or a contract.",
         "define-tools § Forcing tool use; guide TS 2.3 Knowledge 4, TS 4.3 Knowledge 2",
         ("choice", "doc"), {"choice": "any", "doc": "invoice"}, ("Here is the document.", "Here is the document. Use the extraction tool."),
         ("any: a tool call, no text before it.", "auto: a friendly text reply — unless your message says “use the extraction tool”.",
          "Forced extract_invoice on the contract: invented values.", "none: text only.")),
    _tab("pipeline", "⭐ Force the first step", "pipeline", "The soup first — then let them order freely.", "guide:2.3:S4",
         "extract_metadata must run before enrich_vendor. Choose the first call's tool_choice and whether it is released afterwards.",
         "guide TS 2.3 Skill 4, TS 4.3 Skill 3", ("first", "release"), {"first": "forced", "release": "yes"},
         ("Extract the metadata, then enrich the vendor record.",),
         ("forced + release: metadata → enrich → done.", "forced, never released: metadata five times.", "any or auto first: enrichment first, with an invented id.")),
    _tab("schema", "⭐ Schema design", "schema", "A form with “not stated” and “other: ____” boxes, so nobody ticks something false.", "guide:4.3:S4",
         "The Northwind invoice has no tax id and an unforeseen category. Toggle nullable, “other”, and strict.",
         "guide TS 4.3 Knowledge 4, Skills 4–5; strict-tool-use", ("nullable", "other", "strict"), {"nullable": "yes", "other": "yes", "strict": "yes"},
         ("Extract this invoice.",),
         ("All on: tax_id null, other + maintenance, total 310.5.", "nullable off: an invented tax id.", "other off: forced into hardware.",
          "strict off: total “$310.50” as a string.")),
    _tab("semantic", "⭐ strict ≠ correct", "semantic", "A perfectly filled form can still have the wrong total.", "guide:4.3:K3",
         "A schema-valid extraction whose line items don't add up to the total. Turn your own semantic check on or off.",
         "guide TS 4.3 Knowledge 3; structured-outputs caveats", ("validate",), {"validate": "yes"}, ("Extract this invoice with line items.",),
         ("validate: the mismatch is caught (1,200 vs 1,240).", "no validation: schema-valid, wrong, and stored.")),
    _tab("distribution", "⭐ Tool distribution", "distribution", "Give each worker their own toolbox; one box of 18 means wrong tools grabbed.", "guide:2.3:K1",
         "Choose the searcher's and the synthesizer's tools.", "guide TS 2.3 Knowledge 1–3, Skills 1–3; agent-sdk/subagents § Tool restrictions",
         ("searcher_tools", "synth_tools"), {"searcher_tools": "scoped", "synth_tools": "verify_fact"}, ("Research EV battery costs.",),
         ("scoped + verify_fact: web_search, load_document rejects the login page, one fact check.",
          "all 18: search_internal_wiki picked; the synthesizer searches the web.", "fetch_url: the login page is fetched.")),
    _tab("support", "Forcing support", "support", "Some kitchens don't take fixed orders: ask nicely and use a strict form.", "",
         "📘 Docs only: a model that rejects forced tool use, and manual extended thinking.", "define-tools § Forcing tool use (table)",
         ("model", "thinking", "choice"), {"model": "mock-opus-5.5", "thinking": "off", "choice": "auto"},
         ("Here is the document. Use the extraction tool.", "Here is the document."),
         ("Default — mock-opus-5.5 + auto + “use the extraction tool”: works.", "Switch tool_choice to any: 400.",
          "mock-claude + thinking enabled + any: 400.", "mock-claude + any, thinking off: works.")),
)

DECISION_DOT = readable(DECISION_DOT)   # FLOWCHART RULE: 18pt, max 2 nodes per row

CONTENT = ConceptContent(
    slug="tool-choice", tldr=TLDR, mental_model=MENTAL_MODEL, what_it_is=WHAT_IT_IS, how_it_works=HOW_IT_WORKS,
    where_seen=WHERE_SEEN, guide_note=GUIDE_NOTE, docs_refs=DOC_REFS, docs_verified_on=DOCS_VERIFIED_ON, grounding=GROUNDING,
    flow_dot=flow_dot, node_states=node_states, lab_intro=LAB_INTRO, variants=VARIANTS, check_outcome=check_outcome,
    distractors=DISTRACTORS, side_by_side_headers=SIDE_BY_SIDE_HEADERS, side_by_side_rows=SIDE_BY_SIDE_ROWS,
    decision_dot=DECISION_DOT, experiments=EXPERIMENTS, questions=QUESTIONS, faq=FAQ,
    related=("tool-calling", "mcp", "subagents"), exam_points=EXAM_POINTS, playground=PLAYGROUND, playground_intro=PLAYGROUND_INTRO,
    scenarios=("must_extract", "unknown_type", "missing_fields", "metadata_first", "scoped_tools", "model_rejects_forcing"),
    show_ledger=False,
)
