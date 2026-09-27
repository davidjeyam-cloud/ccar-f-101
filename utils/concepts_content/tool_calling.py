"""
D2.1 Tool Calling — designing tool interfaces the model can choose between correctly. Guide TS 2.1 (descriptions,
boundaries, overlap, splitting, system-prompt keywords; p.9) with TS 1.1 (the tool_use / tool_result round trip; p.5 — taught
in depth on D1.1).

GROUNDING (CLAUDE.md, user rules): guide read from the PDF (2026-09-27); platform docs fetched 2026-09-27 (DOC_REFS). Every
claim is in GROUNDING with its source type. Paraphrased; no real exam question reproduced.
"""

import re

from utils.concept_types import Claim, ConceptContent, DocRef, ExamPoint, PlayTab, Question, Variant

DOCS_VERIFIED_ON = "2026-09-27"
_P = "https://platform.claude.com/docs/en"

DOC_REFS = (
    DocRef("Define tools — tool definitions and best practices", f"{_P}/agents-and-tools/tool-use/define-tools"),
    DocRef("How tool use works — the agentic loop", f"{_P}/agents-and-tools/tool-use/how-tool-use-works"),
    DocRef("Handle tool calls — tool_result formatting, is_error", f"{_P}/agents-and-tools/tool-use/handle-tool-calls"),
)

GROUNDING = (
    Claim("A tool definition has a name (must match ^[a-zA-Z0-9_-]{1,128}$), a description, an input_schema (JSON Schema) and "
          "optionally input_examples (each must validate against the schema, else a 400).", "docs", "define-tools § Specifying client tools; Providing tool use examples"),
    Claim("The API builds a special system prompt from your tool definitions, tool configuration and your own system prompt.",
          "docs", "define-tools § Tool use system prompt"),
    Claim("Extremely detailed descriptions are by far the most important factor in tool performance: say what the tool does, when "
          "to use it and when not, what each parameter means, and caveats/limitations such as what it does not return — at least "
          "3–4 sentences, more for complex tools.", "docs", "define-tools § Best practices for tool definitions"),
    Claim("Use input_examples for complex, nested or format-sensitive inputs (they cost ~20–50 tokens for simple examples, ~100–200 "
          "for complex ones); consolidate related operations into fewer tools (e.g. one tool with an action parameter); namespace "
          "tool names by service (github_list_prs, slack_send_message); return only high-signal information with stable identifiers.",
          "docs", "define-tools § Best practices; Providing tool use examples"),
    Claim("Claude may add text before its tool_use blocks; code must not rely on that text's formatting.",
          "docs", "define-tools § Model responses with tools"),
    Claim("Tool descriptions are the primary mechanism for tool selection; minimal descriptions make selection among similar tools "
          "unreliable.", "guide", "TS 2.1 · Knowledge 1 · p.9"),
    Claim("Include input formats, example queries, edge cases and boundaries in tool descriptions.", "guide", "TS 2.1 · Knowledge 2 · p.9"),
    Claim("Ambiguous or overlapping descriptions cause misrouting (e.g. analyze_content vs analyze_document with near-identical "
          "descriptions).", "guide", "TS 2.1 · Knowledge 3 · p.9"),
    Claim("System-prompt wording affects selection: keyword-sensitive instructions can create unintended tool associations.",
          "guide", "TS 2.1 · Knowledge 4 · p.9"),
    Claim("Skills: differentiate each tool's purpose, inputs, outputs and when to use it vs similar tools; rename tools and rewrite "
          "descriptions to remove overlap (analyze_content → extract_web_results); split generic tools into purpose-specific ones "
          "with defined input/output contracts (analyze_document → extract_data_points, summarize_content, verify_claim_against_source); "
          "review system prompts for keyword-sensitive instructions that override good descriptions.", "guide", "TS 2.1 · Skills 1–4 · p.9"),
    Claim("The loop around tool calls (send → stop_reason tool_use → run → tool_result → repeat) is TS 1.1.", "guide", "TS 1.1 · Knowledge 1 · p.5 (D1.1 page)"),
    Claim("Guide vs docs on tool granularity: the guide splits a GENERIC tool into purpose-specific tools; the docs consolidate "
          "closely related ACTIONS (create/review/merge a PR) into one tool with an action parameter. Both aim at unambiguous "
          "selection with clear contracts — this page teaches both and when each applies.", "recommendation", "TS 2.1 S3 vs define-tools § Best practices"),
    Claim("The simulated model's word-matching router (+1 per matching word, −2 for words in a “do not use” sentence, first tool wins "
          "a tie, system-prompt keyword rules override, ORD- formatting when the description says so) is invented to make the effect "
          "of descriptions visible and deterministic.", "simulated", "utils/tool_select_lab.py"),
)

CORRECT = r'''from utils.tool_select_lab import evaluate   # SIMULATED model that picks tools from their definitions

SYSTEM = "You are a research and support assistant. Choose the tool whose description matches the input you were given."

TOOLS = [
    {"name": "extract_web_results",
     "description": ("Extracts the key facts from web search results: the titles, snippets and URLs a web search returned. "
                     "Use it for any request whose input is web search results or web pages - including summarising them or "
                     "turning them into notes or a short write-up. "
                     "Returns a list of facts, each with the URL it came from. "
                     "Do not use it when the input is an uploaded, attached or PDF file, contract or report - use the file tools instead."),
     "input_schema": {"type": "object", "properties": {"results": {"type": "string", "description": "The raw web search results"}},
                      "required": ["results"]}},
    {"name": "extract_data_points",
     "description": ("Extracts specific data points - prices, dates, amounts, names, payment terms - from an uploaded or attached "
                     "document such as a PDF contract, invoice or report. Returns a list of {field, value, page}. "
                     "Use it when the user wants exact values pulled out of a document. "
                     "Do not use it for summaries, for checking claims, or for web search results."),
     "input_schema": {"type": "object", "properties": {"document_id": {"type": "string"}, "fields": {"type": "array", "items": {"type": "string"}}},
                      "required": ["document_id"]}},
    {"name": "summarize_content",
     "description": ("Writes a short summary or overview of an uploaded or attached document such as a report. "
                     "Use it when the user asks what a document says overall or wants it condensed. "
                     "Returns plain-text summary sentences. "
                     "Do not use it for web search results (use extract_web_results), to pull out exact values, or to verify a claim."),
     "input_schema": {"type": "object", "properties": {"document_id": {"type": "string"}, "max_sentences": {"type": "integer"}},
                      "required": ["document_id"]}},
    {"name": "verify_claim_against_source",
     "description": ("Checks whether a source document actually supports a specific claim and returns supported / contradicted / "
                     "not found with the evidence. Use it when the user asks whether a report or document supports, confirms or "
                     "backs up a claim. Do not use it for summaries or data extraction."),
     "input_schema": {"type": "object", "properties": {"claim": {"type": "string"}, "document_id": {"type": "string"}},
                      "required": ["claim", "document_id"]}},
    {"name": "lookup_order",
     "description": ("Looks up one order's status, amount and delivery date by its order id. "
                     "Order ids are in the form ORD-#### (for example ORD-1001); if the user gives only the number, prefix it "
                     "with ORD-. Returns status and amount, not customer details. "
                     "Do not use it when you only have an email address - use get_customer first."),
     "input_schema": {"type": "object", "properties": {"order_id": {"type": "string", "description": "Order id, e.g. ORD-1001"}},
                      "required": ["order_id"]}},
    {"name": "get_customer",
     "description": ("Finds a customer record by email address and returns the customer id and their recent order ids. "
                     "Use it when the user identifies an order or account by email. "
                     "It does not return order status."),
     "input_schema": {"type": "object", "properties": {"email": {"type": "string"}}, "required": ["email"]}},
]

evaluate(TOOLS, SYSTEM)
'''

# ── Transformations (each one = one exam mistake). The playground combines them with its knobs. ─────────────

_MINIMAL = {"extract_web_results": "Extracts web results.", "extract_data_points": "Extracts data points.",
            "summarize_content": "Summarizes content.", "verify_claim_against_source": "Verifies a claim.",
            "lookup_order": "Looks up an order.", "get_customer": "Gets a customer."}


def _set_description(code: str, name: str, new_desc_src: str) -> str:
    pat = r'(\{"name": "' + re.escape(name) + r'",\n     "description": )\((.*?)\),\n'
    out, n = re.subn(pat, lambda m: m.group(1) + new_desc_src + "\n", code, count=1, flags=re.S)
    assert n == 1, f"tool {name} not found"
    return out


def make_minimal(code: str) -> str:
    for name, short in _MINIMAL.items():
        code = _set_description(code, name, f'"{short}",   # WRONG: a minimal description')
    return code


_WEB_BLOCK = re.compile(r'    \{"name": "extract_web_results",.*?(?=    \{"name": "extract_data_points",)', re.S)


def make_overlapping(code: str) -> str:
    pair = ('    {"name": "analyze_document",\n'
            '     "description": "Analyzes documents, web results or report content and returns the key information.",   # WRONG: near-identical\n'
            '     "input_schema": {"type": "object", "properties": {"content": {"type": "string"}}, "required": ["content"]}},\n'
            '    {"name": "analyze_content",\n'
            '     "description": "Analyzes content such as documents, web results or reports and returns the key information.",   # WRONG: overlaps\n'
            '     "input_schema": {"type": "object", "properties": {"content": {"type": "string"}}, "required": ["content"]}},\n')
    out, n = _WEB_BLOCK.subn(pair, code, count=1)
    assert n == 1
    return out


_SPLIT_BLOCK = re.compile(r'    \{"name": "extract_data_points",.*?(?=    \{"name": "lookup_order",)', re.S)


def make_generic(code: str) -> str:
    generic = ('    {"name": "analyze_document",   # WRONG: one generic tool instead of three purpose-specific ones\n'
               '     "description": ("Analyzes an uploaded or attached document such as a PDF contract, invoice or report. "\n'
               '                     "Use it for anything about a document: extracting values, summarising it or checking claims. "\n'
               '                     "Returns an analysis of the document. Do not use it for web search results."),\n'
               '     "input_schema": {"type": "object", "properties": {"document_id": {"type": "string"}, "request": {"type": "string"}},\n'
               '                      "required": ["document_id", "request"]}},\n')
    out, n = _SPLIT_BLOCK.subn(generic, code, count=1)
    assert n == 1
    return out


def add_keyword_rule(code: str) -> str:
    return code.replace('the input you were given."\n', 'the input you were given."\n'
                        'SYSTEM += " Whenever the user mentions a document, use summarize_content."   # WRONG: a keyword rule\n', 1)


def strip_formats(code: str) -> str:
    code = _set_description(code, "lookup_order", '"Looks up an order\'s status by order id. Returns status and amount.",   # WRONG: no format, no boundary')
    code = _set_description(code, "get_customer", '"Finds a customer record and returns the customer id.",   # WRONG: no boundary')
    return code.replace('"description": "Order id, e.g. ORD-1001"', '"description": "The order id"', 1)


VARIANT_A = make_minimal(CORRECT)
VARIANT_B = make_overlapping(CORRECT)
VARIANT_C = make_generic(CORRECT)
VARIANT_D = add_keyword_rule(CORRECT)
VARIANT_E = strip_formats(CORRECT)

# ── Check and chart ────────────────────────────────────────────────────────────


def _facts(trace):
    ev = [e for e in trace["events"] if e["kind"] == "tool_eval"]
    return ev[-1] if ev else None


EXPECTED = {"similar_tools": "all 4 requests routed to the right kind of tool (web results vs documents)",
            "generic_tool": "extract / summarise / verify each routed to a purpose-specific tool",
            "keyword_prompt": "both web-results requests routed to the web tool, even the one that says “document”",
            "edge_cases": "order 1001 looked up as ORD-1001, and the email-only request sent to get_customer"}


def check_outcome(scenario, trace):
    e = _facts(trace)
    if e is None:
        return False, EXPECTED[scenario], f"evaluate() was not called ({trace['status']['raised'] or 'no result'})"
    wrong = [f"“{r['request'][:48]}…” → {r['picked']}" + (" (tie)" if r["ambiguous"] else "") + (" (keyword rule)" if r["keyword_override"] else "")
             + (f" input {r['input']}" if r["input"] else "") for r in e["rows"] if not r["ok"]]
    txt = f"routed correctly {e['score']}/{e['total']} · tools: {e['n_tools']}" + (f" · wrong: {wrong}" if wrong else "")
    return e["score"] == e["total"] and not trace["status"]["raised"], EXPECTED[scenario], txt


_CONCEPT = {
    "req":   ("#EDE9FE", "#7C3AED", "the request and the model's choice"),
    "def":   ("#DBEAFE", "#0066CC", "the tool definition you write"),
    "sys":   ("#FEF3C7", "#D97706", "the system prompt"),
    "run":   ("#D1FAE5", "#059669", "the call runs (tool_use → tool_result)"),
    "bug":   ("#FFFFFF", "#DC2626", "bug (an exam distractor)"),
}
_NODES = {
    "REQ":   ("User request", "box", "req"),
    "SYS":   ("⭐ System prompt\\n(no keyword rules that\\noverride descriptions)", "box", "sys"),
    "PICK":  ("⭐ Model reads names +\\ndescriptions and picks a tool", "diamond", "req"),
    "DESC":  ("⭐ Detailed description:\\nwhat it does · when to use ·\\nwhen NOT to use · caveats", "box", "def"),
    "DIFF":  ("⭐ Differentiated from\\nsimilar tools (renamed)", "box", "def"),
    "SPLIT": ("⭐ Purpose-specific tools with\\ninput/output contracts", "box", "def"),
    "FMT":   ("⭐ Input formats, examples,\\nedge cases, boundaries", "box", "def"),
    "CALL":  ("tool_use with the right\\ntool and a well-formed input", "box", "run"),
    "MINIMAL": ("✗ minimal descriptions", "box", "bug"),
    "OVERLAP": ("✗ near-identical\\ndescriptions", "box", "bug"),
    "GENERIC": ("✗ one generic tool", "box", "bug"),
    "KEYWORD": ("✗ keyword rule in the\\nsystem prompt", "box", "bug"),
    "NOFMT":  ("✗ no formats /\\nboundaries", "box", "bug"),
}
_BUGS = ["MINIMAL", "OVERLAP", "GENERIC", "KEYWORD", "NOFMT"]
_EXP = {"similar_tools": ["DESC", "DIFF"], "generic_tool": ["SPLIT"], "keyword_prompt": ["SYS"], "edge_cases": ["FMT"]}


def _key(hl):
    rows = "".join(f'<TR><TD BGCOLOR="{f}" WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14"></TD><TD ALIGN="LEFT" BORDER="0"><FONT '
                   f'POINT-SIZE="10">{t}</FONT></TD></TR>' for f, _l, t in _CONCEPT.values())
    rows += ('<TR><TD WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14">⭐</TD><TD ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">named by '
             'the exam guide (TS 2.1, p.9)</FONT></TD></TR>')
    if hl:
        rows += ('<TR><TD COLSPAN="2" ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">Your run: <B>green</B> = what this scenario '
                 'tests · <B>red</B> = the bug your definitions show · grey = not involved</FONT></TD></TR>')
    return ('  KEY [shape=plain, label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="3" CELLPADDING="3"><TR><TD COLSPAN="2" '
            'BORDER="0" ALIGN="LEFT"><B>Key</B></TD></TR>' + rows + '</TABLE>>];')


def flow_dot(states):
    hl = bool(states)
    lines = ["digraph G {", '  rankdir=TB; bgcolor="transparent"; nodesep=0.35; ranksep=0.45; newrank=true;',
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
    lines += ["  REQ -> PICK; SYS -> PICK;", "  DESC -> PICK; DIFF -> PICK; SPLIT -> PICK; FMT -> PICK;",
              "  { rank=same; REQ; SYS; }", "  { rank=same; DESC; DIFF; SPLIT; FMT; }", "  REQ -> DESC [style=invis];",
              "  PICK -> CALL;", "  { rank=same; " + "; ".join(_BUGS) + "; }", "  CALL -> MINIMAL [style=invis];", _key(hl),
              "  OVERLAP -> KEY [style=invis];", "}"]
    return "\n".join(lines)


def _bug(e):
    rows = [r for r in e["rows"] if not r["ok"]]
    sc = e["scenario"]
    if any(r["keyword_override"] for r in rows):
        return "KEYWORD"
    if sc == "generic_tool":
        return "GENERIC"
    if sc == "edge_cases":
        return "NOFMT"
    if e["short_descriptions"] and len(e["short_descriptions"]) >= 3:
        return "MINIMAL"
    return "OVERLAP"


def node_states(trace):
    if not trace:
        return {}
    e = _facts(trace)
    if e is None:
        return {}
    ok = e["score"] == e["total"]
    s = {"REQ": ("ok", ""), "PICK": ("ok" if ok else "bad", f"{e['score']}/{e['total']} right"), "CALL": ("ok", "") if ok else ("bad", "wrong tool or input")}
    for n in _EXP.get(e["scenario"], []):
        s[n] = ("ok", "" if ok else "what this scenario tests")
    if not ok:
        s[_bug(e)] = ("bad", "your definitions")
    return s


EXAM_POINTS = (
    ExamPoint("2.1", "K", 1, "Tool descriptions are the model's primary basis for choosing a tool; minimal descriptions make choosing "
              "between similar tools unreliable.", "❌ A · playground “Descriptions”"),
    ExamPoint("2.1", "K", 2, "Descriptions should include input formats, example queries, edge cases and boundaries.",
              "✅ lookup_order / get_customer · ❌ E · playground “Formats & boundaries”"),
    ExamPoint("2.1", "K", 3, "Ambiguous or overlapping descriptions cause misrouting (analyze_content vs analyze_document).",
              "❌ B · playground “Overlap & renaming”"),
    ExamPoint("2.1", "K", 4, "System-prompt wording influences tool choice: keyword-sensitive instructions create unintended associations.",
              "❌ D · playground “System prompt”"),
    ExamPoint("2.1", "S", 1, "Write descriptions that separate each tool's purpose, inputs, outputs and when to use it versus similar tools.",
              "✅ every TOOLS entry"),
    ExamPoint("2.1", "S", 2, "Rename tools and rewrite descriptions to remove overlap (analyze_content → extract_web_results).",
              "✅ extract_web_results · ❌ B"),
    ExamPoint("2.1", "S", 3, "Split generic tools into purpose-specific tools with defined input/output contracts (extract_data_points, "
              "summarize_content, verify_claim_against_source).", "✅ generic_tool · ❌ C · playground “Split”"),
    ExamPoint("2.1", "S", 4, "Review system prompts for keyword-sensitive instructions that override good descriptions.", "✅ SYSTEM · ❌ D"),
    ExamPoint("1.1", "K", 1, "The loop around the call: stop_reason tool_use → run the tool → return a tool_result → next iteration.",
              "the D1.1 Agentic Loops page"),
)

VARIANTS = (
    Variant("correct", "✅ ⭐ Detailed, differentiated, purpose-specific, bounded", "correct", CORRECT, "similar_tools",
            observe=("Every test request is routed right — 4/4, 3/3, 2/2, 2/2 across the scenarios. Read the reasons in the output: the "
                     "web request matches “web / search / result”, the PDF request matches “uploaded / pdf / contract”, and each "
                     "“do not use … (use X)” sentence pushes a request away from the neighbouring tool. “order 1001” goes out as "
                     "ORD-1001 because the description gives the format, and the email-only request goes to get_customer because "
                     "lookup_order's description says when not to use it."),
            why=("Each description follows the docs' checklist — what the tool does, when to use it, when NOT to (naming the "
                 "alternative), what it returns, what its input looks like — so near-neighbours are separable.")),
    Variant("A", "⭐❌ A — minimal one-line descriptions", "distractor", VARIANT_A, "similar_tools",
            observe=("“Extracts web results.” / “Summarizes content.” … The two document requests match nothing, TIE at 0, and go to "
                     "the first tool listed — extract_web_results: 2/4. generic_tool 1/3. edge_cases 0/2: “1001” is sent without ORD- and "
                     "the email-only request goes to lookup_order."),
            why="With nothing to match against, the model can't tell similar tools apart; the docs call detailed descriptions the most important factor.",
            fix="Write 3–4+ sentences per tool: what it does, when to use / not use it, parameters, what it returns and doesn't.",
            source="guide:2.1:K1"),
    Variant("B", "⭐❌ B — two tools with near-identical descriptions", "distractor", VARIANT_B, "similar_tools",
            observe=("analyze_content and analyze_document both “analyze documents, web results or reports and return the key "
                     "information”. Every web request TIES between them and goes to analyze_document, listed first: 2/4 here, 0/2 on "
                     "keyword_prompt. Long descriptions don't help when they say the same thing."),
            why="Overlapping descriptions give the model no basis to choose — the guide's analyze_content vs analyze_document example.",
            fix="Rename by purpose (analyze_content → extract_web_results) and give it a web-only description with a “don't use for files” boundary.",
            source="guide:2.1:K3"),
    Variant("C", "⭐❌ C — one generic analyze_document", "distractor", VARIANT_C, "generic_tool",
            observe=("Extract, summarise and verify all go to the one analyze_document — 0/3 against the purpose-specific contracts: "
                     "one tool returning “an analysis” can't promise a list of values, a summary AND a supported/contradicted verdict."),
            why="A generic tool has no defined input/output contract per job; the guide splits it into purpose-specific tools.",
            fix="Split into extract_data_points, summarize_content and verify_claim_against_source, each with its own inputs and outputs.",
            source="guide:2.1:S3"),
    Variant("D", "⭐❌ D — a keyword rule in the system prompt", "distractor", VARIANT_D, "keyword_prompt",
            observe=("The descriptions are the correct ones, but SYSTEM adds “Whenever the user mentions a document, use summarize_content.” "
                     "“Turn these web search results into a short document” now goes to summarize_content (keyword rule): 1/2."),
            why="Keyword-sensitive instructions create associations that override well-written descriptions.",
            fix="Remove keyword triggers; let descriptions carry the routing, and review system prompts for such rules.",
            source="guide:2.1:K4"),
    Variant("E", "⭐❌ E — no input format, no boundaries", "distractor", VARIANT_E, "edge_cases",
            observe=("lookup_order just “looks up an order's status by order id”: “order 1001” is sent as '1001', which the order system "
                     "doesn't recognise, and “the order for alice@example.com” goes to lookup_order with no id at all: 0/2."),
            why="Without the id format and the “only have an email → use get_customer” boundary, the model guesses both.",
            fix="State formats with an example (ORD-1001), edge cases (bare numbers) and boundaries (what to use instead).",
            source="guide:2.1:K2"),
)

TLDR = (
    "Claude chooses a tool by reading its **name and description** — the docs call detailed descriptions “by far the most important "
    "factor in tool performance”. Say **what the tool does, when to use it and when not to (name the alternative), what each parameter "
    "means, what it returns and doesn't**, with input formats and edge cases. Tools whose descriptions **overlap** get confused; "
    "**generic** tools should be **split** into purpose-specific ones with clear input/output contracts; and a **keyword rule in the "
    "system prompt** can silently override all of it."
)
MENTAL_MODEL = ("Tool descriptions are job adverts for a team the model is staffing: vague adverts (“does stuff with documents”) get "
                "the wrong hire, two identical adverts are a coin toss, and a manager's note saying “anyone who says ‘document’ goes "
                "to Sam” overrides every advert.")

WHAT_IT_IS = """
A tool definition is `name` + `description` + `input_schema` (+ optional `input_examples`). The API builds a special system prompt from
your tool definitions and your own system prompt, and the model decides from that which tool (if any) to call (docs: define tools).
The exam guide's TS 2.1 (Guide §6, p.9) is about writing those definitions so the model routes correctly. The round trip around a call —
`stop_reason: "tool_use"` → run → `tool_result` → continue — is TS 1.1, taught on D1.1.

**Sub-concepts — each with its picture to remember**

| # | Sub-concept | 🧭 Mental model | ⭐ Exam reference |
|---|---|---|---|
| 1 | Description = the selection signal | A job advert: the model hires from the advert, not from the code behind it. | ⭐ TS 2.1 · Knowledge 1 · p.9 |
| 2 | Formats, examples, edge cases, boundaries | A form with a filled-in sample: “ORD-1001, not 1001”; “email only? use the other desk”. | ⭐ TS 2.1 · Knowledge 2 · p.9 |
| 3 | Overlap → misrouting | Two shop signs saying the same thing: customers walk into whichever comes first. | ⭐ TS 2.1 · Knowledge 3 · p.9 |
| 4 | Keyword rules in the system prompt | A sticky note “anyone who says X goes to Y” overrides every sign in the building. | ⭐ TS 2.1 · Knowledge 4, Skill 4 · p.9 |
| 5 | Differentiate & rename | Name the job, not the verb: extract_web_results says what goes in. | ⭐ TS 2.1 · Skills 1–2 · p.9 |
| 6 | Split generic tools | One “handyman” advert vs three specialists with a clear brief each. | ⭐ TS 2.1 · Skill 3 · p.9 |
| 7 | input_examples, namespacing, consolidation | Samples on the form; a department prefix on every desk; one desk per closely related task. | 📘 docs (define tools § Best practices) |

**Anatomy of a good description** (docs checklist)

| # | Say… | Example (lookup_order) |
|---|---|---|
| 1 | What it does | Looks up one order's status, amount and delivery date by its order id |
| 2 | When to use it | The user gives an order id |
| 3 | When NOT to use it — and what instead | Only an email? Use get_customer first |
| 4 | What each parameter means / looks like | order_id is ORD-#### (e.g. ORD-1001); prefix a bare number |
| 5 | What it returns — and doesn't | Status and amount; not customer details |

**Split or consolidate?** The guide splits a *generic* tool (analyze_document) into purpose-specific tools with their own contracts. The
docs consolidate closely related *actions* on one resource (create/review/merge a PR) into one tool with an `action` parameter. Both aim
at the same thing: every tool has one clear job the model can match.
"""

HOW_IT_WORKS = """
1. **List the jobs**, not the functions: what inputs arrive, what outputs are needed.
2. **One tool per distinct job** (split generic tools); **name it by purpose** (extract_web_results, not analyze_content).
3. **Describe** it: what it does, when to use it, when not to (name the neighbour), parameters and formats, what it returns and doesn't —
   3–4+ sentences. Add `input_examples` for format-sensitive or nested inputs.
4. **Read the system prompt** for keyword triggers (“whenever the user mentions…, use…”) and remove them.
5. **Test selection** with realistic, ambiguous requests — the lab's 11 test requests are a small version of that.
"""

WHERE_SEEN = """
- **Scenario 3 — Multi-Agent Research System** (Guide §5, p.4): web-results vs document tools (the analyze_content / analyze_document case).
- **Scenario 1 — Customer Support Resolution Agent** (Guide §5, p.3): get_customer / lookup_order boundaries and id formats.
- **Scenario 4 — Developer Productivity with Claude** (Guide §5, p.4): MCP tool descriptions vs built-in tools (see D2.3).
"""

GUIDE_NOTE = ("Grounded in the exam guide §6 TS 2.1 (p.9) and TS 1.1 (p.5), and the platform tool-use docs (verified 2026-09-27 — "
              "pages listed above). Section layout inspired by a community concept list (claudearchitectcertification.com — "
              "community source, unverified; no text copied).")

LAB_INTRO = """
You write the **tool definitions and the system prompt**. A **simulated** model routes a small test set of realistic requests with them —
the lab prints, for every request, the tool it picked, the input it built and **why** (the words that matched, the “do not use” words that
counted against, or a tie). Four situations; all five mistakes are named in the exam guide (⭐).
"""

DISTRACTORS = (
    ("A · Minimal descriptions", "The name already says what it does.", "Similar tools can't be told apart; ties go to whatever is listed first.",
     "3–4+ sentences: purpose, when to use/not use, params, returns.", "guide:2.1:K1"),
    ("B · Near-identical descriptions", "Both are described in detail.", "Detail that says the same thing gives no basis to choose.",
     "Rename by purpose; differentiate; add boundaries.", "guide:2.1:K3"),
    ("C · One generic tool", "Fewer tools, simpler.", "No clear contract per job — extract, summarise and verify blur together.",
     "Purpose-specific tools with I/O contracts.", "guide:2.1:S3"),
    ("D · Keyword rule in the system prompt", "It's an explicit routing instruction.", "It overrides good descriptions on any request with the word.",
     "Remove keyword triggers; review system prompts.", "guide:2.1:K4"),
    ("E · No formats or boundaries", "The model can figure out the format.", "Bare ids and email-only requests are guessed wrong.",
     "Formats with examples, edge cases, “use X instead”.", "guide:2.1:K2"),
)

SIDE_BY_SIDE_HEADERS = ("#", "Aspect", "Detailed, differentiated", "Minimal", "Overlapping", "Generic")
SIDE_BY_SIDE_ROWS = (
    ("1", "What the model can match on", "Purpose, inputs, boundaries", "Almost nothing", "The same words for two tools", "One broad job"),
    ("2", "Typical result", "Right tool, right input", "Ties → first-listed tool", "Ties → first-listed tool", "Right tool, wrong contract"),
    ("3", "Fix", "—", "Write the docs' checklist", "Rename + boundaries", "Split by purpose"),
    ("4", "Exam reference", "TS 2.1 S1–S2", "TS 2.1 K1", "TS 2.1 K3", "TS 2.1 S3"),
)

DECISION_DOT = '''digraph D {
  rankdir=TB; bgcolor="transparent"; nodesep=0.35; ranksep=0.4;
  node [fontname="Helvetica", fontsize=12, style="rounded,filled", fillcolor="#F3F4F6", color="#9CA3AF", penwidth=1.5];
  edge [fontname="Helvetica", fontsize=11, color="#6B7280"];
  Q1 [shape=diamond, label="Does one tool do several\\ndifferent jobs?"];
  SPLIT [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="Split into purpose-specific tools\\n(TS 2.1 S3)"];
  Q2 [shape=diamond, label="Could two tools' descriptions\\nfit the same request?"];
  DIFF [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="Rename by purpose; add\\n“use X instead” boundaries (TS 2.1 S2)"];
  Q3 [shape=diamond, label="Format-sensitive input\\nor edge cases?"];
  FMT [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="State formats + examples\\n(input_examples) (TS 2.1 K2)"];
  Q4 [shape=diamond, label="Keyword rules in the\\nsystem prompt?"];
  SYS [shape=box, fillcolor="#FEF3C7", color="#D97706", label="Remove them (TS 2.1 S4)"];
  OK [shape=box, fillcolor="#D1FAE5", color="#059669", label="Test selection with\\nambiguous requests"];
  Q1 -> SPLIT [label="yes"]; Q1 -> Q2 [label="no"]; SPLIT -> Q2;
  Q2 -> DIFF [label="yes"]; Q2 -> Q3 [label="no"]; DIFF -> Q3;
  Q3 -> FMT [label="yes"]; Q3 -> Q4 [label="no"]; FMT -> Q4;
  Q4 -> SYS [label="yes"]; Q4 -> OK [label="no"]; SYS -> OK;
}'''

EXPERIMENTS = (
    "Run ✅ on similar_tools and read the matched words for each request.",
    "Run ⭐❌ B and find the TIE lines. Then rename analyze_content and give it a web-only description — ties gone?",
    "In ✅, delete the “Do not use it for web search results (use extract_web_results)” clause of summarize_content and run keyword_prompt.",
    "In ✅, move get_customer above lookup_order and delete lookup_order's email boundary: which way does the tie fall now?",
    "Add a line `SYSTEM += \" Whenever the user mentions results, use verify_claim_against_source.\"` and run similar_tools.",
)

QUESTIONS = (
    Question(
        q=("An agent has analyze_content and analyze_document, both described as “Analyzes content and returns key information.” Requests about "
           "web search results are often routed to analyze_document. What is the most effective fix?"),
        opts=("Add a system-prompt rule: “if the user mentions the web, use analyze_content”.",
              "Rename analyze_content to extract_web_results and rewrite both descriptions to state each tool's input, output and when not to use it.",
              "Merge both tools into one and let the model decide.",
              "Lower the temperature so routing is more consistent."),
        ans=1,
        explain=("Overlapping descriptions cause misrouting; the guide's fix is renaming and differentiated descriptions. A keyword rule creates "
                 "new unintended associations; lower temperature doesn't add the missing information."),
        scenarios=(3,), ts="2.1"),
    Question(
        q=("A single analyze_document tool is used to extract figures, summarise reports and check claims, and downstream code often receives "
           "the wrong kind of output. What change fits best?"),
        opts=("Add more examples to analyze_document's description.",
              "Split it into extract_data_points, summarize_content and verify_claim_against_source, each with its own input/output contract.",
              "Force tool_choice to analyze_document.",
              "Parse the output with a regular expression."),
        ans=1,
        explain="The guide splits generic tools into purpose-specific tools with defined input/output contracts.",
        scenarios=(3,), ts="2.1"),
    Question(
        q=("Tool descriptions were rewritten carefully, yet requests containing the word “report” still go to the wrong tool. What should you check next?"),
        opts=("The tool names' length.", "The system prompt, for keyword-sensitive instructions such as “when the user mentions a report, use …”.",
              "The model's max_tokens.", "The order of properties in the input schema."),
        ans=1,
        explain="Keyword-sensitive system-prompt wording can override well-written descriptions — review it (TS 2.1 K4, S4).",
        scenarios=(3,), ts="2.1"),
    Question(
        q=("Customers say “order 1001”; the order system only accepts ids like ORD-1001, and lookups keep failing. What is the best first fix?"),
        opts=("Retry failed lookups three times.",
              "State the id format with an example in the tool/parameter description (ORD-####; prefix bare numbers), plus when to use get_customer instead.",
              "Ask customers to always type ORD-.", "Remove the order_id parameter."),
        ans=1,
        explain="Input formats, examples, edge cases and boundaries belong in the description (TS 2.1 K2).",
        scenarios=(1,), ts="2.1"),
    Question(
        q=("Per the tool-use docs, what is “by far the most important factor” in tool performance, and roughly how long should a description be?"),
        opts=("The number of tools; fewer than five.", "Extremely detailed descriptions; at least 3–4 sentences per tool, more for complex tools.",
              "Short names; one word.", "Strict mode; always on."),
        ans=1,
        explain="The define-tools best practices say detailed descriptions are by far the most important factor, aiming for at least 3–4 sentences.",
        basis="docs", in_bank=False),
)

FAQ = (
    ("Does the model really just match words?",
     "No — the lab's router is a deliberately simple stand-in so you can see why a choice was made. The documented point is that the "
     "description is what Claude uses to decide, so it must carry the purpose, boundaries and formats."),
    ("Split (guide) or consolidate (docs)?",
     "Split a tool that does unrelated jobs with different outputs; consolidate closely related actions on the same resource behind one "
     "`action` parameter. Either way, one clear job per tool."),
    ("What are input_examples?",
     "Optional example inputs on a tool definition (each must validate against the schema, else a 400). Useful for nested or "
     "format-sensitive inputs; they cost roughly 20–50 tokens each for simple ones."),
    ("Where does tool_choice come in?",
     "tool_choice controls WHETHER and WHICH tool must be called (auto / any / tool / none) — that's D2.2. This page is about making the "
     "model's own choice right."),
)

PLAYGROUND_INTRO = """
Type any request and choose how the tools are defined. The simulated model shows every tool's score — the words that matched, the
“do not use” words that counted against — and which tool it picked with what input.
"""


def _tab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this):
    return PlayTab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this, engine="toolsel")


_EX = ("Pull the key facts out of these web search results about solar panel prices.",
       "Go through this uploaded PDF contract and pull out the payment terms.",
       "Does the attached report actually support the claim that sales rose 20%?",
       "What's the status of order 1001?", "Turn these web search results into a short document for the team.")

PLAYGROUND = (
    _tab("desc", "⭐ Descriptions", "desc", "A job advert: the model hires from the advert, not from the code behind it.", "guide:2.1:K1",
         "Detailed vs one-line descriptions for the same six tools.", "define-tools § Best practices; guide TS 2.1 Knowledge 1",
         ("quality",), {"quality": "detailed"}, _EX[:3],
         ("Detailed: each example picks its tool with a clear lead.", "Minimal: document requests tie at 0 and go to the first tool listed.")),
    _tab("overlap", "⭐ Overlap & renaming", "overlap", "Two shop signs saying the same thing: customers walk into whichever comes first.", "guide:2.1:K3",
         "The web tool as extract_web_results (renamed, web-only) or as analyze_content next to a near-identical analyze_document.",
         "guide TS 2.1 Knowledge 3, Skill 2", ("web_tool",), {"web_tool": "renamed"}, _EX[:1],
         ("Renamed: web requests go to extract_web_results.", "Overlapping: a TIE — analyze_document, listed first, wins.")),
    _tab("split", "⭐ Split generic tools", "split", "One “handyman” advert vs three specialists with a clear brief each.", "guide:2.1:S3",
         "Three purpose-specific document tools, or one generic analyze_document.", "guide TS 2.1 Skill 3",
         ("doc_tools",), {"doc_tools": "split"}, (_EX[1], _EX[2]),
         ("Split: extract vs verify go to different tools with different outputs.", "Generic: both go to analyze_document.")),
    _tab("system", "⭐ System prompt", "system", "A sticky note “anyone who says X goes to Y” overrides every sign in the building.", "guide:2.1:K4",
         "Add or remove the keyword rule “whenever the user mentions a document, use summarize_content”.", "guide TS 2.1 Knowledge 4, Skill 4",
         ("keyword_rule",), {"keyword_rule": "off"}, (_EX[4],),
         ("Off: web results → extract_web_results.", "On: any request with “document” → summarize_content, whatever it contains.")),
    _tab("formats", "⭐ Formats & boundaries", "formats", "A form with a filled-in sample: “ORD-1001, not 1001”.", "guide:2.1:K2",
         "lookup_order / get_customer with or without the id format and the “email only → get_customer” boundary.", "guide TS 2.1 Knowledge 2",
         ("formats",), {"formats": "with"}, (_EX[3], "Where is the order for alice@example.com?"),
         ("With: ORD-1001; the email request goes to get_customer.", "Without: '1001', and lookup_order with no id.")),
)

CONTENT = ConceptContent(
    slug="tool-calling", tldr=TLDR, mental_model=MENTAL_MODEL, what_it_is=WHAT_IT_IS, how_it_works=HOW_IT_WORKS,
    where_seen=WHERE_SEEN, guide_note=GUIDE_NOTE, docs_refs=DOC_REFS, docs_verified_on=DOCS_VERIFIED_ON, grounding=GROUNDING,
    flow_dot=flow_dot, node_states=node_states, lab_intro=LAB_INTRO, variants=VARIANTS, check_outcome=check_outcome,
    distractors=DISTRACTORS, side_by_side_headers=SIDE_BY_SIDE_HEADERS, side_by_side_rows=SIDE_BY_SIDE_ROWS,
    decision_dot=DECISION_DOT, experiments=EXPERIMENTS, questions=QUESTIONS, faq=FAQ,
    related=("agentic-loops", "tool-choice", "mcp"), exam_points=EXAM_POINTS, playground=PLAYGROUND, playground_intro=PLAYGROUND_INTRO,
    scenarios=("similar_tools", "generic_tool", "keyword_prompt", "edge_cases"), show_ledger=False,
)
