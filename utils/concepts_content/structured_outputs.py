"""
D4.4 Structured Outputs — after the schema guarantees valid JSON: semantic validation (calculated vs stated totals), retry with
specific error feedback, knowing when a retry can't help (the information isn't in the document), conflict flags, format
normalisation, and a detected_pattern field for analysing dismissed findings. Guide TS 4.4 (p.18) with TS 4.3 (pp.17–18).
D2.2 Tool Choice covers tool_choice and schema design (nullable, other/unclear) in depth.

GROUNDING (CLAUDE.md, user rules): guide read from the PDF (2026-09-28); structured-outputs docs fetched 2026-09-28 (DOC_REFS).
Every claim is in GROUNDING with its source type. Paraphrased; no real exam question reproduced.
"""

from utils.concept_types import Claim, ConceptContent, DocRef, ExamPoint, PlayTab, Question, Variant
from utils.flow_style import readable

DOCS_VERIFIED_ON = "2026-09-28"
_P = "https://platform.claude.com/docs/en"

DOC_REFS = (
    DocRef("Structured outputs — guarantees and limits", f"{_P}/build-with-claude/structured-outputs"),
    DocRef("Strict tool use", f"{_P}/agents-and-tools/tool-use/strict-tool-use"),
)

GROUNDING = (
    Claim("Structured outputs (JSON outputs and strict tool use) guarantee schema-compliant responses — valid JSON, the right "
          "types, required fields present — so schema violations need no retries.", "docs", "structured-outputs § guarantees"),
    Claim("They don't guarantee semantic correctness; invalid values can still be generated; refusals and max_tokens cut-offs can "
          "still happen. Retries for semantic validation failures are yours to implement.", "docs", "structured-outputs § limits; handling invalid content"),
    Claim("JSON schema limits: numerical constraints (minimum, maximum) and string length constraints aren't enforced by the "
          "API — SDKs validate them after the response.", "docs", "structured-outputs § JSON Schema limitations"),
    Claim("Tool use with JSON schemas is the most reliable route to schema-compliant output and removes syntax errors but not "
          "semantic ones (line items that don't sum to the total, values in the wrong field); include format-normalisation rules "
          "in the prompt alongside strict schemas; nullable fields prevent fabricated values.", "guide", "TS 4.3 · Knowledge 1, 3; Skills 4, 6 · pp.17–18"),
    Claim("Retry with error feedback: append the specific validation errors on retry; retries don't help when the information "
          "is absent from the source (vs format or structural errors); detected_pattern fields let you analyse dismissal patterns; "
          "semantic validation errors differ from syntax errors (which tool use removes).", "guide", "TS 4.4 · Knowledge 1–4 · p.18"),
    Claim("Skills: follow-up requests carry the original document, the failed extraction and the specific errors; tell when a "
          "retry will fail (the information is in an external document not provided) vs succeed (format mismatches, structural "
          "errors); add detected_pattern to findings; extract calculated_total alongside stated_total and a conflict_detected "
          "boolean for inconsistent source data.", "guide", "TS 4.4 · Skills 1–4 · p.18"),
    Claim("The documents, the misread line item that is fixed only with a specific error, the external PO, the conflicting totals, "
          "the date formats and the dismissal data are invented.", "simulated", "utils/extract_lab.py"),
)

CORRECT = r'''from utils.extract_lab import (analyse_dismissals, document, extract, finish, retry_with_feedback, route_to_human,
                                store)   # SIMULATED extraction model (schema-valid output, values not guaranteed)

SCHEMA = {"type": "object", "additionalProperties": False, "properties": {
    "invoice_id": {"type": "string"},
    "line_items": {"type": "array", "items": {"type": "number"}},
    "stated_total": {"type": "number"},
    "calculated_total": {"type": "number"},                  # sum of the line items, to check against stated_total
    "conflict_detected": {"type": "boolean"},                # the source itself disagrees (e.g. two different totals)
    "po_number": {"type": ["string", "null"]},               # null when the document doesn't contain it
    "issued": {"type": ["string", "null"]}, "due": {"type": ["string", "null"]}}}
RULES = "Dates: ISO 8601 (YYYY-MM-DD); numeric dates are UK day/month. Money: plain numbers, no currency symbols."


def validate(x):
    errors = []
    if "calculated_total" in x and abs(x["calculated_total"] - x["stated_total"]) > 0.01:
        errors.append(f"line items sum to {x['calculated_total']} but stated_total is {x['stated_total']} - re-read each line item")
    return errors


doc = document()
x = extract(doc, SCHEMA, RULES)
if x.get("conflict_detected"):
    route_to_human(x, "the document states two different totals")          # a retry can't fix the source
elif "po_number" in x and x["po_number"] is None and "see attached" in doc:
    store(x, flags=["po_number is only in an attached document that wasn't provided"])   # absent: don't retry
else:
    for attempt in range(2):
        errors = validate(x)
        if not errors:
            break
        # the follow-up carries the original document, the failed extraction and the SPECIFIC errors
        x = retry_with_feedback(doc, x, errors, SCHEMA, RULES)
    if validate(x):
        route_to_human(x, "; ".join(validate(x)))
    else:
        store(x)

# code-review findings carry detected_pattern so dismissals can be grouped by construct
analyse_dismissals(["location", "issue", "severity", "detected_pattern"])
finish()
'''


def _swap(code, old, new):
    assert old in code, f"lab code changed: {old[:60]!r}"
    return code.replace(old, new, 1)


# ⭐ TS 4.3 · Knowledge 3 / TS 4.4 · Knowledge 4 — trusting schema-valid output
VARIANT_A = _swap(CORRECT, '''    if "calculated_total" in x and abs(x["calculated_total"] - x["stated_total"]) > 0.01:
        errors.append(f"line items sum to {x['calculated_total']} but stated_total is {x['stated_total']} - re-read each line item")
    return errors''', '''    return errors   # WRONG: "the schema guarantees it" - no semantic check''')
# ⭐ TS 4.4 · Knowledge 1 / Skill 1 — retrying without the specific error
VARIANT_B = _swap(CORRECT, '''        x = retry_with_feedback(doc, x, errors, SCHEMA, RULES)''',
                  '''        x = retry_with_feedback(doc, x, ["invalid output, try again"], SCHEMA, RULES)   # WRONG: generic feedback''')
# ⭐ TS 4.4 · Knowledge 2 / Skill 2 — retrying when the information is absent
VARIANT_C = _swap(_swap(CORRECT, '''elif "po_number" in x and x["po_number"] is None and "see attached" in doc:
    store(x, flags=["po_number is only in an attached document that wasn't provided"])   # absent: don't retry
''', ""), '''        errors.append(f"line items sum to {x['calculated_total']} but stated_total is {x['stated_total']} - re-read each line item")
''', '''        errors.append(f"line items sum to {x['calculated_total']} but stated_total is {x['stated_total']} - re-read each line item")
    if "po_number" in x and x["po_number"] is None:
        errors.append("po_number is missing - find it")   # WRONG: retries for information the document doesn't contain
''')
# ⭐ TS 4.4 · Skill 4 — no conflict flag
VARIANT_D = _swap(CORRECT, '''    "conflict_detected": {"type": "boolean"},                # the source itself disagrees (e.g. two different totals)
''', "")
# ⭐ TS 4.3 · Skill 6 — no normalisation rules
VARIANT_E = _swap(CORRECT, '''RULES = "Dates: ISO 8601 (YYYY-MM-DD); numeric dates are UK day/month. Money: plain numbers, no currency symbols."''',
                  '''RULES = ""   # WRONG: no format-normalisation rules''')
# ⭐ TS 4.4 · Skill 3 / Knowledge 3 — findings without detected_pattern
VARIANT_F = _swap(CORRECT, '''analyse_dismissals(["location", "issue", "severity", "detected_pattern"])''',
                  '''analyse_dismissals(["location", "issue", "severity"])   # WRONG: no detected_pattern''')

# ── Check and chart ────────────────────────────────────────────────────────────


def _facts(trace):
    ev = [e for e in trace["events"] if e["kind"] == "extract_run"]
    return {"scenario": trace["status"].get("scenario"), "raised": trace["status"]["raised"], "run": ev[-1] if ev else None}


def _diagnose(f):
    r, sc = f["run"], f["scenario"]
    if f["raised"]:
        return False, None, f"raised: {f['raised'][:160]}"
    if r is None:
        return False, None, "finish() was never called"
    stored = (r["stored"] or {}).get("record")
    txt = (f"calls: {len(r['calls'])} · retries: {r['retries']} · feedback sent: {r['feedback'] or 'none'} · stored: {stored} "
           f"{(r['stored'] or {}).get('flags') or ''} · to a human: {(r['human'] or {}).get('reason')} · dismissal analysis: {r['analysis']}")
    if sc == "sum_mismatch":
        ok = stored is not None and stored.get("line_items") == [700.0, 500.0, 40.0]
        bug = None if ok else ("NOVALIDATE" if r["retries"] == 0 else "GENERIC")
        return ok, bug, txt
    if sc == "absent_info":
        ok = stored is not None and stored.get("po_number") is None and r["retries"] == 0
        return ok, (None if ok else "FUTILE"), txt
    if sc == "conflicting_source":
        ok = r["human"] is not None and stored is None
        return ok, (None if ok else "NOCONFLICT"), txt
    if sc == "mixed_formats":
        ok = stored is not None and stored.get("issued") == "2026-03-03" and stored.get("due") == "2026-04-05"
        return ok, (None if ok else "NOFORMAT"), txt
    a = r["analysis"] or {}
    ok = bool(a.get("can_group")) and a.get("top", ("", 0))[0] == "broad-except-in-tests"
    return ok, (None if ok else "NOPATTERN"), txt


EXPECTED = {
    "sum_mismatch": "the misread line item is caught (1,600 ≠ 1,240), fixed on a retry that names the error, and stored as 700 / 500 / 40",
    "absent_info": "stored with po_number null and a flag — no retries, because the PO isn't in this document",
    "conflicting_source": "not stored; sent to a human because the document states two different totals",
    "mixed_formats": "issued 2026-03-03, due 2026-04-05 — one format, 05/04 read as UK day/month",
    "dismissal_patterns": "dismissals grouped by detected_pattern: 4 of 5 are broad-except-in-tests",
}


def check_outcome(scenario, trace):
    ok, _b, txt = _diagnose(_facts(trace))
    return ok, EXPECTED[scenario], txt


_CONCEPT = {
    "q":    ("#EDE9FE", "#7C3AED", "schema-valid output"),
    "val":  ("#DBEAFE", "#0066CC", "semantic validation"),
    "fix":  ("#FEF3C7", "#D97706", "retry / route"),
    "loop": ("#CCFBF1", "#0D9488", "feedback loop"),
    "bug":  ("#FFFFFF", "#DC2626", "bug (a distractor)"),
}
_NODES = {
    "EXTRACT": ("Strict schema + normalisation rules\\n→ valid JSON (syntax guaranteed)", "box", "q"),
    "CHECK":   ("⭐ Semantic checks: calculated_total\\nvs stated_total, conflict_detected", "box", "val"),
    "Q":       ("What kind of problem?", "diamond", "val"),
    "RETRY":   ("⭐ Retry with the original doc,\\nthe failed output and the\\nSPECIFIC errors", "box", "fix"),
    "ABSENT":  ("⭐ Information not in the\\ndocument → null + flag,\\nno retry", "box", "fix"),
    "HUMAN":   ("⭐ Source contradicts itself\\n→ a human", "box", "fix"),
    "STORE":   ("Store", "box", "q"),
    "PATTERN": ("⭐ detected_pattern on findings\\n→ analyse dismissals", "box", "loop"),
    "NOVALIDATE": ("✗ “schema-valid\\nmeans correct”", "box", "bug"),
    "GENERIC":    ("✗ retry with “try\\nagain”", "box", "bug"),
    "FUTILE":     ("✗ retrying for info\\nthat isn't there", "box", "bug"),
    "NOCONFLICT": ("✗ one total picked\\nsilently", "box", "bug"),
    "NOFORMAT":   ("✗ no normalisation\\nrules", "box", "bug"),
    "NOPATTERN":  ("✗ findings without\\ndetected_pattern", "box", "bug"),
}
_BUGS = ["NOVALIDATE", "GENERIC", "FUTILE", "NOCONFLICT", "NOFORMAT", "NOPATTERN"]
_EXP = {"sum_mismatch": ["EXTRACT", "CHECK", "Q", "RETRY", "STORE"], "absent_info": ["EXTRACT", "Q", "ABSENT", "STORE"],
        "conflicting_source": ["EXTRACT", "CHECK", "Q", "HUMAN"], "mixed_formats": ["EXTRACT", "STORE"], "dismissal_patterns": ["PATTERN"]}


def _key(hl):
    rows = "".join(f'<TR><TD BGCOLOR="{f}" WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14"></TD><TD ALIGN="LEFT" BORDER="0"><FONT '
                   f'POINT-SIZE="10">{t}</FONT></TD></TR>' for f, _l, t in _CONCEPT.values())
    rows += ('<TR><TD WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14">⭐</TD><TD ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">named by '
             'the exam guide (TS 4.4 p.18, TS 4.3 pp.17–18)</FONT></TD></TR>')
    if hl:
        rows += ('<TR><TD COLSPAN="2" ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">Your run: <B>green</B> = what this document '
                 'needs · <B>red</B> = the bug your run shows</FONT></TD></TR>')
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
    lines += ["  EXTRACT -> CHECK -> Q;", '  Q -> RETRY [label="misread / format"]; Q -> ABSENT [label="not in the document"];',
              '  Q -> HUMAN [label="source conflicts"]; RETRY -> CHECK [label="re-validate", style=dashed];',
              '  Q -> STORE [label="no problem"]; ABSENT -> STORE; STORE -> PATTERN [style=dashed, label="findings"];',
              "  { rank=same; " + "; ".join(_BUGS) + "; }", "  PATTERN -> NOVALIDATE [style=invis];", _key(hl),
              f"  {_BUGS[0]} -> KEY [style=invis];", "}"]
    return readable("\n".join(lines))   # FLOWCHART RULE: 18pt, max 2 nodes per row


def node_states(trace):
    if not trace:
        return {}
    f = _facts(trace)
    ok, bug, _ = _diagnose(f)
    s = {}
    for n in _EXP.get(f["scenario"], []):
        s[n] = ("ok", "" if ok else "what this document needs")
    if bug:
        s[bug] = ("bad", "your run")
    return s


EXAM_POINTS = (
    ExamPoint("4.4", "K", 1, "Retry with error feedback: append the specific validation errors on retry to guide correction.", "✅ sum_mismatch · ❌ B"),
    ExamPoint("4.4", "K", 2, "Retries don't help when the information is absent from the source (unlike format or structural errors).", "✅ absent_info · ❌ C"),
    ExamPoint("4.4", "K", 3, "Feedback loops: a detected_pattern field lets you analyse which constructs trigger dismissed findings.", "✅ dismissal_patterns · ❌ F"),
    ExamPoint("4.4", "K", 4, "Semantic validation errors (values don't sum, wrong field) differ from syntax errors (removed by tool use).", "✅ validate() · ❌ A"),
    ExamPoint("4.4", "S", 1, "Follow-up requests include the original document, the failed extraction and the specific validation errors.", "✅ retry_with_feedback · ❌ B"),
    ExamPoint("4.4", "S", 2, "Tell when retries will fail (information only in an external document) vs succeed (format mismatches, structural errors).", "✅ absent_info · ❌ C"),
    ExamPoint("4.4", "S", 3, "Add detected_pattern fields to structured findings to analyse false-positive patterns.", "✅ dismissal_patterns · ❌ F"),
    ExamPoint("4.4", "S", 4, "Self-correction: extract calculated_total alongside stated_total; add a conflict_detected boolean for inconsistent sources.",
              "✅ sum_mismatch, conflicting_source · ❌ A · ❌ D"),
    ExamPoint("4.3", "K", 3, "Strict schemas remove syntax errors but not semantic errors (totals that don't add up).", "✅ sum_mismatch · ❌ A"),
    ExamPoint("4.3", "S", 6, "Include format-normalisation rules in prompts alongside strict schemas.", "✅ mixed_formats · ❌ E"),
)

VARIANTS = (
    Variant("correct", "✅ ⭐ semantic checks · specific-error retries · no retry for absent info · conflict flag · normalisation · detected_pattern",
            "correct", CORRECT, "sum_mismatch",
            observe=("sum_mismatch: the first extraction reads 40.00 as 400.00 (calculated 1,600 ≠ stated 1,240); the retry names the "
                     "mismatch → 700 / 500 / 40 stored. absent_info: po_number null + a flag, 0 retries. conflicting_source: "
                     "conflict_detected → a human. mixed_formats: 2026-03-03 and 2026-04-05. dismissal_patterns: 4 of 5 dismissals are "
                     "broad-except-in-tests."),
            why="The schema guarantees shape; the checks, retries and flags handle meaning — and each problem gets the response that can actually fix it."),
    Variant("A", "⭐❌ A — trusting schema-valid output", "distractor", VARIANT_A, "sum_mismatch",
            observe="Stored line items 700 / 500 / 400 with stated_total 1,240 and calculated_total 1,600 — valid JSON, wrong data.",
            why="Strict schemas remove syntax errors, not semantic ones such as totals that don't add up.",
            fix="Compare calculated_total with stated_total.", source="guide:4.4:K4"),
    Variant("B", "⭐❌ B — retrying with “invalid output, try again”", "distractor", VARIANT_B, "sum_mismatch",
            observe="Two retries repeat the same 400.00 misread; the record goes to a human.",
            why="The retry must carry the specific validation error (with the document and the failed extraction) to guide the fix.",
            fix="Send the specific error.", source="guide:4.4:S1"),
    Variant("C", "⭐❌ C — retrying for information that isn't there", "distractor", VARIANT_C, "absent_info",
            observe="Two retries ask for the PO number; it's still null — it's only in an attached document that wasn't provided.",
            why="Retries fix format and structural errors, not missing information.",
            fix="Store null with a flag; get the external document if it's needed.", source="guide:4.4:S2"),
    Variant("D", "⭐❌ D — no conflict_detected field", "distractor", VARIANT_D, "conflicting_source",
            observe="The header says 980.00 and the footer 1,080.00; 980.00 is stored silently.",
            why="A conflict_detected boolean lets the model report inconsistent sources instead of choosing one.",
            fix="Add conflict_detected and route conflicts to a person.", source="guide:4.4:S4"),
    Variant("E", "⭐❌ E — no format-normalisation rules", "distractor", VARIANT_E, "mixed_formats",
            observe="issued “3 March 2026”, due “05/04/2026” — two formats, and 05/04 is ambiguous.",
            why="A strict schema fixes types, not formats; normalisation rules in the prompt make the values consistent.",
            fix="Add rules: ISO 8601; numeric dates are UK day/month.", source="guide:4.3:S6"),
    Variant("F", "⭐❌ F — findings without detected_pattern", "distractor", VARIANT_F, "dismissal_patterns",
            observe="5 of 10 findings were dismissed, but nothing says which construct they came from.",
            why="A detected_pattern field makes dismissals groupable, so the prompt can be fixed where it misfires.",
            fix="Add detected_pattern to the findings schema.", source="guide:4.4:S3"),
)

TLDR = (
    "A strict schema guarantees **valid JSON**, not **correct values** (docs and guide). So you:\n\n"
    "- **Validate meaning:** extract `calculated_total` next to `stated_total`, and add a `conflict_detected` flag.\n"
    "- **Retry with the specific error**, the original document and the failed extraction.\n"
    "- **Don't retry** when the information simply **isn't in the document**: store null with a flag.\n"
    "- **Send contradictions to a person.**\n"
    "- **Put normalisation rules in the prompt** (ISO dates, UK day/month).\n"
    "- **Give findings a `detected_pattern`**, so dismissals show where the prompt misfires."
)
MENTAL_MODEL = ("The schema is the form; it guarantees every box is filled with the right kind of thing — not that the numbers "
                "are true. So check the arithmetic, and when it's wrong, tell the clerk exactly which box. If the answer isn't "
                "anywhere in the paperwork, asking again won't conjure it — note it and move on. And if the paperwork contradicts "
                "itself, pass it to a supervisor.")

WHAT_IT_IS = """
The exam guide covers validation, retry and feedback loops (Guide §6 · TS 4.4, p.18). Two points come from TS 4.3 (pp.17–18):
strict schemas don't stop semantic errors, and prompts should carry normalisation rules. The structured-outputs docs state
what is and isn't guaranteed. D2.2 covers `tool_choice` and schema design.

**Sub-concepts — each with its picture to remember**

| # | Sub-concept | 🧭 Mental model | ⭐ Exam reference |
|---|---|---|---|
| 1 | Syntax vs semantic errors | The form has every box filled — the numbers can still be wrong. | ⭐ TS 4.4 · Knowledge 4; TS 4.3 · Knowledge 3 |
| 2 | calculated_total vs stated_total | Check the arithmetic on the form. | ⭐ TS 4.4 · Skill 4 |
| 3 | Retry with the specific error | Tell the clerk which box is wrong, not “redo it”. | ⭐ TS 4.4 · Knowledge 1, Skill 1 |
| 4 | When retries can't help | Asking again won't conjure what isn't in the paperwork. | ⭐ TS 4.4 · Knowledge 2, Skill 2 |
| 5 | conflict_detected | The paperwork contradicts itself — pass it to a supervisor. | ⭐ TS 4.4 · Skill 4 |
| 6 | Normalisation rules | A house style for dates and money, written on the form. | ⭐ TS 4.3 · Skill 6 |
| 7 | detected_pattern | Label every complaint by cause, so you fix the cause. | ⭐ TS 4.4 · Knowledge 3, Skill 3 |

**What a strict schema does and doesn't guarantee** (docs)

| # | Guaranteed | Not guaranteed |
|---|---|---|
| 1 | Valid JSON — no parse errors | Semantic correctness (totals that add up) |
| 2 | Field types and required fields | Values in the right field |
| 3 | No retries needed for schema violations | Protection from invented values (unless fields are nullable) |
| 4 | — | Numerical / string-length constraints (the SDK validates those afterwards) |
| 5 | — | No refusal or `max_tokens` cut-off |

**Which problems a retry fixes**

| # | Problem | Retry helps? | Response |
|---|---|---|---|
| 1 | A value misread (400 for 40) | ✅ with the specific error | Retry with the document, the failed output and the error |
| 2 | Wrong format / structure | ✅ | Retry with the specific error (and add normalisation rules) |
| 3 | Information not in this document | ❌ | null + a flag; fetch the other document if needed |
| 4 | The source contradicts itself | ❌ | conflict_detected → a person |
"""

HOW_IT_WORKS = """
1. **Extract with a strict schema** that includes `calculated_total`, `conflict_detected` and nullable fields, and put
   **normalisation rules** in the prompt.
2. **Validate the meaning:** do the line items sum to the stated total?
3. **Conflict in the source?** Send it to a person. **Information absent?** Store null with a flag.
4. **Misread or format error?** Retry with the **original document, the failed extraction and the specific error**, then
   validate again.
5. **Findings carry `detected_pattern`,** so dismissals can be grouped and the prompt fixed where it misfires.
"""

WHERE_SEEN = """
- **Scenario 6 — Structured Data Extraction** (Guide §5, p.4): invoices, validation, retries, human review.
- **Scenario 5 — Claude Code for Continuous Integration** (Guide §5, p.4): findings with detected_pattern and dismissal analysis.
- **Guide §8, Exercise 3** (p.25): validation-retry loops and nullable schema fields.
"""

GUIDE_NOTE = ("Grounded in the exam guide §6 TS 4.4 (p.18) and TS 4.3 K3/S6 (pp.17–18), and the structured-outputs docs (verified "
              "2026-09-28). Section layout inspired by a community concept list (claudearchitectcertification.com — community "
              "source, unverified; no text copied).")

LAB_INTRO = """
You write the extraction pipeline around a **simulated** model whose output is always schema-valid, but not always right:

- the schema;
- the prompt's normalisation rules;
- the semantic check;
- when to retry and what to send with the retry;
- when to store with a flag, or hand to a person;
- which fields findings carry.

Five documents test it: a misread line item, a PO number that lives in another document, conflicting totals, mixed date
formats, and a set of dismissed review findings.
"""

DISTRACTORS = (
    ("A · Trust schema-valid output", "The schema guarantees it.", "Valid JSON with a wrong total.", "calculated_total vs stated_total.", "guide:4.4:K4"),
    ("B · “Try again” retries", "Retries fix things.", "The same misread, twice.", "Send the specific error.", "guide:4.4:S1"),
    ("C · Retry for absent info", "Maybe it missed it.", "It isn't in the document.", "null + flag.", "guide:4.4:S2"),
    ("D · No conflict flag", "Pick the first total.", "The wrong total stored silently.", "conflict_detected.", "guide:4.4:S4"),
    ("E · No normalisation rules", "The schema has a date field.", "Mixed and ambiguous formats.", "Rules in the prompt.", "guide:4.3:S6"),
    ("F · No detected_pattern", "Severity is enough.", "Dismissals can't be grouped.", "detected_pattern.", "guide:4.4:S3"),
)

SIDE_BY_SIDE_HEADERS = ("#", "Aspect", "Generic retry", "Retry with feedback")
SIDE_BY_SIDE_ROWS = (
    ("1", "What's sent", "“Invalid output, try again”", "The original document + the failed extraction + the specific error"),
    ("2", "Model knows what to fix", "No", "Yes — “line items sum to 1,600 but stated_total is 1,240”"),
    ("3", "Result here", "The same misread twice", "Fixed on the first retry"),
    ("4", "Guide reference", "—", "⭐ TS 4.4 · Knowledge 1, Skill 1"),
)

DECISION_DOT = readable('''digraph D {
  rankdir=TB; bgcolor="transparent"; nodesep=0.35; ranksep=0.4;
  node [fontname="Helvetica", fontsize=12, style="rounded,filled", fillcolor="#F3F4F6", color="#9CA3AF", penwidth=1.5];
  edge [fontname="Helvetica", fontsize=11, color="#6B7280"];
  Q1 [shape=diamond, label="Values pass the\\nsemantic checks?"];
  STORE [shape=box, fillcolor="#D1FAE5", color="#059669", label="Store"];
  Q2 [shape=diamond, label="Why not?"];
  RETRY [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="Retry with document +\\nfailed output + specific error"];
  FLAG [shape=box, fillcolor="#FEF3C7", color="#D97706", label="null + flag\\n(no retry)"];
  HUMAN [shape=box, fillcolor="#FEF3C7", color="#D97706", label="A person"];
  Q1 -> STORE [label="yes"]; Q1 -> Q2 [label="no"]; Q2 -> RETRY [label="misread / format"];
  Q2 -> FLAG [label="not in the document"]; Q2 -> HUMAN [label="source conflicts"]; RETRY -> Q1 [style=dashed];
}''')

EXPERIMENTS = (
    "Run ✅ on all five scenarios and read each call's output.",
    "In ✅, change the retry feedback to “please check your work” and run sum_mismatch.",
    "Run ⭐❌ C and count the wasted retries.",
    "In the playground's “Retry feedback” tab, write your own feedback and see whether the misread gets fixed.",
)

QUESTIONS = (
    Question(
        q=("An extraction service asks Claude to “reply with JSON only” and parses the text. About 2% of responses break "
           "the parser: a trailing comment, a missing bracket, or prose before the JSON. What's the most reliable fix?"),
        opts=("Add “your JSON must be valid” to the prompt.",
              "Repair the JSON with a tolerant parser.",
              "Define an extraction tool whose input is the JSON schema, and read the data from the tool_use block.",
              "Retry every response that fails to parse."),
        ans=2,
        explain=("Tool use with a JSON schema is the most reliable route to schema-compliant output and removes JSON "
                 "syntax errors. Prompt wording and repair or retry loops only reduce the rate."),
        scenarios=(6,), points=("4.3:K1", "4.3:S1"),
    ),
    Question(
        q=("The pipeline now uses strict tool use, so every invoice extraction is valid JSON. Audits still find invoices "
           "whose line items add up to £1,200 while total says £1,240. What's needed?"),
        opts=("A semantic validation step (for example, checking that line items sum to the total), because schemas can't catch this.",
              "A stricter schema with more required fields.",
              "Switching tool_choice to “any”.",
              "A higher max_tokens so the model has room to add up."),
        ans=0,
        explain=("Strict schemas remove syntax errors but not semantic errors: values that don't add up or sit in the "
                 "wrong field. Those need separate validation."),
        scenarios=(6,), points=("4.3:K3", "4.4:K4"),
    ),
    Question(
        q=("When validation fails, the pipeline retries with “The previous output was invalid, please try again”, and the "
           "model often repeats the same mistake. What should the retry request contain?"),
        opts=("The same prompt with a higher temperature, to get a different answer.",
              "Just the validation errors.",
              "A request to double-check its work.",
              "The original document, the failed extraction, and the specific validation errors."),
        ans=3,
        explain=("Retry with error feedback: append the specific validation errors, along with the original document and "
                 "the failed extraction, so the model knows exactly what to correct."),
        scenarios=(6,), points=("4.4:K1", "4.4:S1"),
    ),
    Question(
        q=("Invoices often say “PO: see attached purchase order”, but the attachment isn't sent to the model. The "
           "pipeline retries up to three times for the missing po_number and still fails. What's the right handling?"),
        opts=("Increase the retries to ten.",
              "Stop retrying: the information isn't in the source, so return po_number as null and flag it for follow-up.",
              "Tell the model the PO number is required and must be found.",
              "Ask the model to infer a likely PO number from the invoice date."),
        ans=1,
        explain=("Retries help with format or structure errors, not when the information is absent from the source. "
                 "Here the data lives in an external document that was never provided."),
        scenarios=(6,), points=("4.4:K2", "4.4:S2"),
    ),
    Question(
        q=("Developers dismiss many of the CI reviewer's findings, but the team can't tell which kinds of code trigger the "
           "false positives. What schema change enables that analysis?"),
        opts=("Add a free-text “notes” field to each finding.",
              "Remove low-severity findings.",
              "Add a detected_pattern field to each structured finding, so dismissals can be grouped by the code construct that triggered them.",
              "Ask the reviewer to explain its reasoning at length."),
        ans=2,
        explain=("A detected_pattern field creates a feedback loop: you can analyse which constructs lead to dismissed "
                 "findings and refine the criteria for those."),
        scenarios=(5,), points=("4.4:K3", "4.4:S3"),
    ),
    Question(
        q=("Some invoices contain their own arithmetic errors, and some list a total in the summary that differs from the "
           "total on the payment slip. The pipeline should catch both and never silently pick one. What's the best schema "
           "design?"),
        opts=("Extract calculated_total alongside stated_total, and add a conflict_detected boolean for sources that disagree.",
              "Extract one total and let the model choose the more plausible value.",
              "Always use the larger total, to be safe.",
              "Drop the total field and compute it downstream."),
        ans=0,
        explain=("Extracting calculated and stated totals side by side lets the pipeline self-check. A conflict flag "
                 "surfaces inconsistent sources instead of hiding them."),
        scenarios=(6,), points=("4.4:S4",),
    ),
    Question(
        q=("Due dates arrive as “05/04/2026” (UK invoices), “April 5th” and “2026-04-05”, and extractions put some of them "
           "into the wrong month. The schema already requires an ISO date string. What else is needed?"),
        opts=("A regex check that the output looks like YYYY-MM-DD.",
              "More retries when the date looks wrong.",
              "Change the field type from string to date.",
              "Format-normalisation rules in the prompt, such as how to read day/month order for UK sources, alongside the strict schema."),
        ans=3,
        explain=("Put format-normalisation rules in the prompt alongside strict schemas to handle inconsistent source "
                 "formatting. The schema checks the shape but can't know that 05/04 means 5 April."),
        scenarios=(6,), points=("4.3:S6",),
    ),
    Question(
        q=("A team assumes that because they use a strict JSON schema, extracted values are guaranteed correct. According "
           "to the structured-outputs docs, what's actually guaranteed?"),
        opts=("That every value is copied exactly from the source.",
              "That the output conforms to the schema (types, required fields); not that the values are right.",
              "That numeric fields are arithmetically consistent.",
              "Nothing; strict mode is only a hint."),
        ans=1,
        explain=("Per the docs, structured outputs guarantee schema conformance. Whether the values are correct still "
                 "needs validation."),
        scenarios=(6,), basis="docs", in_bank=False,
    ),
)


FAQ = (
    ("If the schema guarantees the shape, why validate?",
     "Because the guarantee stops at shape. The docs say semantic correctness isn't guaranteed, and the guide says the same "
     "about totals that don't add up. Validation is your code comparing values."),
    ("How many retries?",
     "The guide doesn't give a number. What matters is that each retry carries the specific error and that you recognise "
     "unfixable cases, such as absent information or conflicting sources. The lab allows two."),
    ("Where do normalisation rules go — schema or prompt?",
     "The prompt. The schema fixes types; the prompt says which format to use (ISO 8601; numeric dates are UK day/month). The "
     "guide pairs rules in the prompt with strict schemas."),
    ("Isn't this D2.2 again?",
     "D2.2 covers getting structured output: tool_choice, strict schemas, nullable fields, and other/unclear enums. This page "
     "covers what happens after: validation, retries and feedback loops."),
)

PLAYGROUND_INTRO = """
Each tab is one decision from the lab. In the “Retry feedback” tab, write the feedback yourself. The **simulated** model fixes
its misread only if you name the sum or total and a number.
"""


def _tab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this):
    return PlayTab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this, engine="extract")


PLAYGROUND = (
    _tab("validate", "⭐ Semantic check", "validate", "The form is filled in — check the arithmetic.", "guide:4.4:K4",
         "A schema-valid extraction with a misread line item.", "structured-outputs § limits; guide TS 4.4 K4, S4",
         ("sem_check",), {"sem_check": "yes"}, ("Extract INV-31",), ("no check: 400 stored.",)),
    _tab("retry", "⭐ Retry feedback", "retry", "Tell the clerk which box is wrong.", "guide:4.4:S1",
         "Your message is the feedback sent on retry.", "guide TS 4.4 K1, S1", (), {},
         ("The line items sum to 1600 but the stated total is 1240 - re-read each line item", "Invalid output, try again"),
         ("“try again”: the same mistake.", "name the sum and the total: fixed.")),
    _tab("absent", "⭐ Absent information", "absent", "Asking again won't conjure it.", "guide:4.4:S2",
         "The PO number is only in an attachment you don't have.", "guide TS 4.4 K2, S2; TS 4.3 S4",
         ("absent_policy", "po_nullable"), {"absent_policy": "flag", "po_nullable": "yes"}, ("Extract INV-32",),
         ("retry: 2 wasted calls.", "non-nullable: PO-00000 invented.")),
    _tab("conflict", "⭐ Conflicting source", "conflict", "Pass contradictions to a supervisor.", "guide:4.4:S4",
         "Header 980.00, footer 1,080.00.", "guide TS 4.4 S4", ("conflict_field",), {"conflict_field": "yes"}, ("Extract INV-33",),
         ("no field: 980 stored silently.",)),
    _tab("formats", "⭐ Normalisation", "formats", "A house style written on the form.", "guide:4.3:S6",
         "“3 March 2026” and “05/04/2026”.", "guide TS 4.3 S6", ("norm_rules",), {"norm_rules": "iso_uk"}, ("Extract INV-34",),
         ("ISO only: 05/04 read as May 4.", "none: two formats.")),
    _tab("patterns", "⭐ detected_pattern", "patterns", "Label every complaint by cause.", "guide:4.4:S3",
         "10 findings, 5 dismissed.", "guide TS 4.4 K3, S3", ("pattern_field",), {"pattern_field": "yes"}, ("Analyse dismissals",),
         ("no field: can't group.",)),
)

CONTENT = ConceptContent(
    slug="structured-outputs", tldr=TLDR, mental_model=MENTAL_MODEL, what_it_is=WHAT_IT_IS, how_it_works=HOW_IT_WORKS,
    where_seen=WHERE_SEEN, guide_note=GUIDE_NOTE, docs_refs=DOC_REFS, docs_verified_on=DOCS_VERIFIED_ON, grounding=GROUNDING,
    flow_dot=flow_dot, node_states=node_states, lab_intro=LAB_INTRO, variants=VARIANTS, check_outcome=check_outcome,
    distractors=DISTRACTORS, side_by_side_headers=SIDE_BY_SIDE_HEADERS, side_by_side_rows=SIDE_BY_SIDE_ROWS,
    decision_dot=DECISION_DOT, experiments=EXPERIMENTS, questions=QUESTIONS, faq=FAQ,
    related=("tool-choice", "batch-api", "system-prompts"), exam_points=EXAM_POINTS, playground=PLAYGROUND,
    playground_intro=PLAYGROUND_INTRO,
    scenarios=("sum_mismatch", "absent_info", "conflicting_source", "mixed_formats", "dismissal_patterns"), show_ledger=False,
)
