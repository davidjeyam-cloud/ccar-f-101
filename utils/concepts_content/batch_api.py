"""
D4.3 Batch API — when to use the Message Batches API (latency-tolerant, non-blocking work at 50% cost) and when not (blocking
checks, workflows that need tool results mid-request), correlating results by custom_id, resubmitting only failures, submission
cadence for an SLA, and refining the prompt on a sample first. Guide TS 4.5 (pp.18–19).

GROUNDING (CLAUDE.md, user rules): guide read from the PDF (2026-09-28); batch-processing docs fetched 2026-09-28 (DOC_REFS).
Every claim is in GROUNDING with its source type. Paraphrased; no real exam question reproduced.
"""

from utils.concept_types import Claim, ConceptContent, DocRef, ExamPoint, PlayTab, Question, Variant
from utils.flow_style import readable

DOCS_VERIFIED_ON = "2026-09-28"
_P = "https://platform.claude.com/docs/en"

DOC_REFS = (DocRef("Batch processing — Message Batches API", f"{_P}/build-with-claude/batch-processing"),)

GROUNDING = (
    Claim("The Message Batches API processes requests asynchronously at 50% of the standard cost; most batches finish within an "
          "hour; results are available when all requests finish or after 24 hours; requests not processed within 24 hours expire.",
          "docs", "batch-processing § How it works; Batch limitations; Pricing"),
    Claim("A batch holds up to 100,000 requests or 256 MB; results are available for 29 days.", "docs", "batch-processing § Batch limitations"),
    Claim("Each request needs a unique custom_id (1–64 characters: letters, digits, - and _); results can be returned in any order "
          "— always match them with custom_id.", "docs", "batch-processing § Prepare and create; Retrieving results (note)"),
    Claim("Result types: succeeded, errored (invalid request or server error — not billed), canceled, expired (not billed); one "
          "request's failure doesn't affect the others; implement retry logic for failed requests.", "docs",
          "batch-processing § Retrieving batch results; Best practices; Troubleshooting"),
    Claim("Batches accept tool use, system messages and multi-turn conversation history, but each request is processed "
          "independently — there's no round trip for your code to run a tool and return its result within the request.",
          "docs", "batch-processing § What can be batched"),
    Claim("Best practices: meaningful custom_id values; break very large datasets into multiple batches; dry-run a single "
          "request shape with the Messages API to avoid validation errors.", "docs", "batch-processing § Best practices"),
    Claim("Batch API: 50% cost savings, up to 24-hour processing, no latency SLA; suited to non-blocking, latency-tolerant work "
          "(overnight reports, weekly audits, nightly test generation), not blocking workflows (pre-merge checks); no multi-turn "
          "tool calling within a single request; custom_id correlates requests and responses.", "guide", "TS 4.5 · Knowledge 1–4 · p.18"),
    Claim("Skills: sync API for blocking pre-merge checks, batch for overnight/weekly; compute submission frequency from the SLA "
          "(4-hour windows keep a 30-hour SLA with 24-hour processing); resubmit only failed documents by custom_id, e.g. chunking "
          "ones that exceeded context limits; refine the prompt on a sample before large batches.", "guide", "TS 4.5 · Skills 1–4 · pp.18–19"),
    Claim("The jobs, documents, failures, cost units and the effect of sample refinement are invented.", "simulated", "utils/batch_lab.py"),
)

CORRECT = r'''from utils.batch_lab import run   # SIMULATED Messages API + Message Batches API


def choose_api(job):
    """Blocking, or needs tool results mid-request -> synchronous. Latency-tolerant -> batch (50% cheaper)."""
    if job["blocking"] or job["needs_tool_loop"]:
        return "sync"
    return "batch"


def custom_id_for(doc):
    return doc["id"]                                   # unique, meaningful, 1-64 chars of [a-zA-Z0-9_-]


def attach(results, docs, ids):
    """Results come back in ANY order - match them by custom_id, never by position."""
    by_id = {r["custom_id"]: r["text"] for r in results}
    return {doc["id"]: by_id.get(cid) for doc, cid in zip(docs, ids)}


def retry(results):
    """Resubmit only what failed; split documents that were too long."""
    plan = {}
    for r in results:
        if r["type"] == "succeeded":
            continue
        too_long = r["type"] == "errored" and "too long" in r.get("error", "")
        plan[r["custom_id"]] = "resubmit_chunked" if too_long else "resubmit"
    return plan


SUBMIT_EVERY_HOURS = 4      # worst case: 4 h waiting + 24 h in the batch = 28 h, inside a 30 h SLA
SAMPLE_FIRST = True         # refine the prompt on a small sample before sending 10,000

run(choose_api, custom_id_for, attach, retry, SUBMIT_EVERY_HOURS, SAMPLE_FIRST)
'''


def _swap(code, old, new):
    assert old in code, f"lab code changed: {old[:60]!r}"
    return code.replace(old, new, 1)


_CHOOSE = '''    if job["blocking"] or job["needs_tool_loop"]:
        return "sync"
    return "batch"'''
# ⭐ TS 4.5 · Skill 1 / Knowledge 2 — batch for a blocking check
VARIANT_A = _swap(CORRECT, _CHOOSE, '''    if job["needs_tool_loop"]:
        return "sync"
    return "batch"   # WRONG: the blocking pre-merge check goes to the batch too - it's cheaper''')
# ⭐ TS 4.5 · Knowledge 4 — matching results by position
VARIANT_B = _swap(CORRECT, '''    by_id = {r["custom_id"]: r["text"] for r in results}
    return {doc["id"]: by_id.get(cid) for doc, cid in zip(docs, ids)}''',
                  '''    return {doc["id"]: r["text"] for doc, r in zip(docs, results)}   # WRONG: assumes results come back in order''')
# ⭐ TS 4.5 · Skill 3 — resubmitting the whole batch
VARIANT_C = _swap(CORRECT, '''    plan = {}
    for r in results:
        if r["type"] == "succeeded":
            continue''', '''    plan = {}
    for r in results:   # WRONG: resubmits every document, including the ones that succeeded''')
# ⭐ TS 4.5 · Skill 3 — resubmitting too-long documents unchanged
VARIANT_D = _swap(CORRECT, '''        plan[r["custom_id"]] = "resubmit_chunked" if too_long else "resubmit"''',
                  '''        plan[r["custom_id"]] = "resubmit"   # WRONG: the too-long documents go back unchanged''')
# ⭐ TS 4.5 · Skill 2 — a once-a-day submission for a 30-hour SLA
VARIANT_E = _swap(CORRECT, '''SUBMIT_EVERY_HOURS = 4      # worst case: 4 h waiting + 24 h in the batch = 28 h, inside a 30 h SLA''',
                  '''SUBMIT_EVERY_HOURS = 24     # WRONG: once a day''')
# ⭐ TS 4.5 · Knowledge 3 — a tool-calling workflow in a batch
VARIANT_F = _swap(CORRECT, _CHOOSE, '''    if job["blocking"]:
        return "sync"
    return "batch"   # WRONG: includes jobs that need tool results mid-request''')
# ⭐ TS 4.5 · Skill 4 — no sample refinement
VARIANT_G = _swap(CORRECT, '''SAMPLE_FIRST = True         # refine the prompt on a small sample before sending 10,000''',
                  '''SAMPLE_FIRST = False        # WRONG: the untested prompt goes straight to 10,000 tickets''')

# ── Check and chart ────────────────────────────────────────────────────────────


def _facts(trace):
    ev = [e for e in trace["events"] if e["kind"] == "batch_run"]
    return {"scenario": trace["status"].get("scenario"), "raised": trace["status"]["raised"], "run": ev[-1] if ev else None}


_BUG = {"blocking": "BLOCKING", "cost": "SYNCCOST", "order": "ORDER", "custom_id": "ORDER", "resubmit_all": "RESUBALL",
        "dropped": "RESUBALL", "no_chunk": "NOCHUNK", "cadence": "CADENCE", "tool_loop": "TOOLLOOP", "no_sample": "NOSAMPLE"}


def _diagnose(f):
    r = f["run"]
    if f["raised"]:
        return False, None, f"raised: {f['raised'][:160]}"
    if r is None:
        return False, None, "run() was never called"
    txt = " · ".join(r["log"])
    return (True, None, txt) if r["ok"] else (False, _BUG.get(r["problem"]), txt)


EXPECTED = {
    "premerge": "synchronous API — the PR check answers in seconds",
    "nightly": "Message Batches API — 200 cost units instead of 400",
    "results_order": "every summary matched to its own document by custom_id, whatever order results arrive in",
    "partial_failure": "only the 5 failed documents resubmitted, the 2 over-long ones in chunks",
    "sla_cadence": "worst case (window + 24 h) within the 30 h SLA",
    "tool_loop": "synchronous API — the tool loop can run",
    "sample_first": "prompt refined on a sample first; ~300 re-dos instead of 3,000",
}


def check_outcome(scenario, trace):
    ok, _b, txt = _diagnose(_facts(trace))
    return ok, EXPECTED[scenario], txt


_CONCEPT = {
    "q":    ("#EDE9FE", "#7C3AED", "the choice"),
    "sync": ("#D1FAE5", "#059669", "synchronous Messages API"),
    "bat":  ("#DBEAFE", "#0066CC", "Message Batches API"),
    "ops":  ("#FEF3C7", "#D97706", "running batches well"),
    "bug":  ("#FFFFFF", "#DC2626", "bug (a distractor)"),
}
_NODES = {
    "Q":      ("Blocking, or needs tool\\nresults mid-request?", "diamond", "q"),
    "SYNC":   ("⭐ Synchronous API\\n(pre-merge checks, tool loops)", "box", "sync"),
    "BATCH":  ("⭐ Batch API: 50% cheaper,\\nup to 24 h, no latency SLA", "box", "bat"),
    "SAMPLE": ("⭐ Refine the prompt on\\na sample first", "box", "ops"),
    "CID":    ("⭐ custom_id per request;\\nmatch results by it", "box", "ops"),
    "RETRY":  ("⭐ Resubmit only failures;\\nchunk the too-long ones", "box", "ops"),
    "CAD":    ("⭐ Submit every N h so that\\nN + 24 ≤ SLA", "box", "ops"),
    "BLOCKING": ("✗ blocking check\\nin a batch", "box", "bug"),
    "SYNCCOST": ("✗ overnight job on\\nthe sync API", "box", "bug"),
    "ORDER":    ("✗ results matched\\nby position", "box", "bug"),
    "RESUBALL": ("✗ resubmitting\\nthe whole batch", "box", "bug"),
    "NOCHUNK":  ("✗ too-long documents\\nresent unchanged", "box", "bug"),
    "CADENCE":  ("✗ submitting once\\na day", "box", "bug"),
    "TOOLLOOP": ("✗ tool loop\\nin a batch", "box", "bug"),
    "NOSAMPLE": ("✗ untested prompt on\\n10,000 requests", "box", "bug"),
}
_BUGS = ["BLOCKING", "SYNCCOST", "ORDER", "RESUBALL", "NOCHUNK", "CADENCE", "TOOLLOOP", "NOSAMPLE"]
_EXP = {"premerge": ["SYNC"], "nightly": ["BATCH"], "results_order": ["BATCH", "CID"], "partial_failure": ["BATCH", "RETRY"],
        "sla_cadence": ["BATCH", "CAD"], "tool_loop": ["SYNC"], "sample_first": ["SAMPLE", "BATCH"]}


def _key(hl):
    rows = "".join(f'<TR><TD BGCOLOR="{f}" WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14"></TD><TD ALIGN="LEFT" BORDER="0"><FONT '
                   f'POINT-SIZE="10">{t}</FONT></TD></TR>' for f, _l, t in _CONCEPT.values())
    rows += ('<TR><TD WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14">⭐</TD><TD ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">named by '
             'the exam guide (TS 4.5 pp.18–19)</FONT></TD></TR>')
    if hl:
        rows += ('<TR><TD COLSPAN="2" ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">Your run: <B>green</B> = what this job '
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
    lines += ['  Q -> SYNC [label="yes"]; Q -> BATCH [label="no"]; { rank=same; SYNC; BATCH; }',
              "  BATCH -> SAMPLE; SAMPLE -> CID; CID -> RETRY; RETRY -> CAD;",
              "  { rank=same; " + "; ".join(_BUGS) + "; }", "  CAD -> BLOCKING [style=invis]; SYNC -> BLOCKING [style=invis];",
              _key(hl), f"  {_BUGS[0]} -> KEY [style=invis];", "}"]
    return readable("\n".join(lines))   # FLOWCHART RULE: 18pt, max 2 nodes per row


def node_states(trace):
    if not trace:
        return {}
    f = _facts(trace)
    ok, bug, _ = _diagnose(f)
    s = {"Q": ("ok", "")}
    for n in _EXP.get(f["scenario"], []):
        s[n] = ("ok", "" if ok else "what this job needs")
    if bug:
        s[bug] = ("bad", "your run")
    return s


EXAM_POINTS = (
    ExamPoint("4.5", "K", 1, "Message Batches API: 50% cost savings, up to 24-hour processing, no guaranteed latency.", "✅ nightly · ❌ A"),
    ExamPoint("4.5", "K", 2, "Batch suits non-blocking, latency-tolerant work (overnight reports, weekly audits, nightly tests), not blocking workflows (pre-merge checks).",
              "✅ premerge, nightly · ❌ A"),
    ExamPoint("4.5", "K", 3, "No multi-turn tool calling within one batch request — tools can't run mid-request with results returned.", "✅ tool_loop · ❌ F"),
    ExamPoint("4.5", "K", 4, "custom_id correlates each request with its response.", "✅ results_order · ❌ B"),
    ExamPoint("4.5", "S", 1, "Match the API to latency needs: synchronous for blocking pre-merge checks, batch for overnight/weekly analysis.", "✅ choose_api · ❌ A"),
    ExamPoint("4.5", "S", 2, "Compute submission frequency from the SLA (4-hour windows keep a 30-hour SLA with 24-hour processing).", "✅ sla_cadence · ❌ E"),
    ExamPoint("4.5", "S", 3, "On failures, resubmit only the failed documents (by custom_id), with fixes such as chunking over-long documents.",
              "✅ partial_failure · ❌ C · ❌ D"),
    ExamPoint("4.5", "S", 4, "Refine the prompt on a sample before batch-processing large volumes, to raise first-pass success.", "✅ sample_first · ❌ G"),
)

VARIANTS = (
    Variant("correct", "✅ ⭐ sync for blocking & tool loops · batch for the rest · custom_id · resubmit failures · 4 h windows · sample first",
            "correct", CORRECT, "premerge",
            observe=("premerge → sync. nightly → batch, 200 units instead of 400. results_order: results arrive shuffled; every summary "
                     "is matched by custom_id. partial_failure: 5 resubmitted, DOC-00007 and DOC-00042 in chunks. sla_cadence: 4 + 24 = "
                     "28 h ≤ 30 h. tool_loop → sync, the agentic loop runs. sample_first: 97% first-pass, 300 re-dos."),
            why="Each job goes where its latency and its need for tool results allow, and the batch is run with the docs' own practices."),
    Variant("A", "⭐❌ A — a blocking pre-merge check in a batch", "distractor", VARIANT_A, "premerge",
            observe="The PR check waits up to 24 h with no latency guarantee — merges are blocked.",
            why="Batches are for non-blocking, latency-tolerant work; a blocking check needs the synchronous API.",
            fix="Synchronous API for blocking checks.", source="guide:4.5:S1"),
    Variant("B", "⭐❌ B — matching results by position", "distractor", VARIANT_B, "results_order",
            observe="Results arrive as DOC-00004, 00000, 00005 … — 5 of 6 documents get another document's summary.",
            why="Batch results can come back in any order; custom_id is how requests and responses are correlated.",
            fix="Match on custom_id.", source="guide:4.5:K4"),
    Variant("C", "⭐❌ C — resubmitting the whole batch", "distractor", VARIANT_C, "partial_failure",
            observe="100 requests resubmitted to recover 5 — paying again for 95 that already succeeded.",
            why="Only the failed documents, identified by custom_id, need resubmitting.",
            fix="Resubmit failed custom_ids only.", source="guide:4.5:S3"),
    Variant("D", "⭐❌ D — resubmitting too-long documents unchanged", "distractor", VARIANT_D, "partial_failure",
            observe="DOC-00007 and DOC-00042 go back as they were — “prompt is too long” again.",
            why="A failure caused by the document itself needs a change (the guide's example: chunking) before resubmitting.",
            fix="Chunk the over-long documents.", source="guide:4.5:S3"),
    Variant("E", "⭐❌ E — submitting once a day for a 30 h SLA", "distractor", VARIANT_E, "sla_cadence",
            observe="A document arriving just after submission waits 24 h, then up to 24 h in the batch → 48 h > 30 h.",
            why="Worst case = submission window + 24 h processing; the window must fit inside the SLA (the guide uses 4 h).",
            fix="Submit every 4 h.", source="guide:4.5:S2"),
    Variant("F", "⭐❌ F — a tool-calling workflow in a batch", "distractor", VARIANT_F, "tool_loop",
            observe="Each request ends at stop_reason tool_use — nothing runs the tool and sends the result back; 20 investigations stop half-way.",
            why="A batch request can't have your code execute a tool mid-request and return the result.",
            fix="Run tool loops on the synchronous API.", source="guide:4.5:K3"),
    Variant("G", "⭐❌ G — no sample refinement", "distractor", VARIANT_G, "sample_first",
            observe="The untested prompt goes to 10,000 tickets: 70% first-pass success, 3,000 need a second batch.",
            why="Refining the prompt on a sample first raises first-pass success and cuts resubmission cost.",
            fix="Iterate on a small sample (sync), then batch.", source="guide:4.5:S4"),
)

TLDR = (
    "The **Message Batches API** costs **50% less**, but runs asynchronously: up to **24 hours**, **no latency guarantee**.\n\n"
    "- **Batch it:** latency-tolerant, non-blocking work (overnight reports, weekly audits, nightly test generation).\n"
    "- **Keep synchronous:** **blocking** checks (pre-merge), and workflows that need **tool results mid-request**.\n\n"
    "**Running a batch well:**\n\n"
    "- Give every request a unique **`custom_id`** and match results by it, because order isn't guaranteed.\n"
    "- **Resubmit only failures**, fixing the cause (e.g. chunk over-long documents).\n"
    "- Pick a submission window so **window + 24 h ≤ SLA** (4 h for a 30 h SLA).\n"
    "- **Refine the prompt on a sample** before sending thousands."
)
MENTAL_MODEL = ("The batch API is the overnight post: half the price, delivered sometime within a day, in no particular order. "
                "Put a label (custom_id) on every envelope so you know which reply belongs to which letter. Don't post anything "
                "someone is standing at the counter waiting for — or any letter that needs a reply before it can be finished.")

WHAT_IT_IS = """
The exam guide covers designing efficient batch processing (Guide §6 · TS 4.5, pp.18–19). The batch-processing docs give the
exact limits and result types.

**Sub-concepts — each with its picture to remember**

| # | Sub-concept | 🧭 Mental model | ⭐ Exam reference |
|---|---|---|---|
| 1 | 50% cheaper, up to 24 h, no SLA | Overnight post: cheap, arrives within a day. | ⭐ TS 4.5 · Knowledge 1 |
| 2 | Blocking vs latency-tolerant | Nobody waits at the counter for overnight post. | ⭐ TS 4.5 · Knowledge 2, Skill 1 |
| 3 | No mid-request tool loop | A letter that needs a reply before it's finished can't go by post. | ⭐ TS 4.5 · Knowledge 3 |
| 4 | `custom_id` | A label on every envelope — replies arrive in any order. | ⭐ TS 4.5 · Knowledge 4 |
| 5 | Resubmit only failures (fixed) | Re-post only the letters that came back — trimmed if they were too heavy. | ⭐ TS 4.5 · Skill 3 |
| 6 | Cadence from the SLA | Post often enough that waiting plus delivery fits the promise. | ⭐ TS 4.5 · Skill 2 |
| 7 | Sample first | Proof-read one letter before printing ten thousand. | ⭐ TS 4.5 · Skill 4 |
| 8 | Result types | Delivered · returned (errored) · cancelled · expired — only delivered ones are billed. | 📘 docs |

**Message Batches API vs synchronous Messages API** (the comparison CLAUDE.md requires)

| # | Aspect | Message Batches API | Synchronous Messages API |
|---|---|---|---|
| 1 | Cost | ⭐ 50% of standard | Standard |
| 2 | Latency | ⭐ Most within 1 h, up to 24 h; no guarantee; expires after 24 h | Seconds |
| 3 | Use for | ⭐ Overnight reports, weekly audits, nightly test generation | ⭐ Blocking pre-merge checks, interactive work |
| 4 | Tool loop mid-request | ⭐ No — nothing returns tool results inside the request | Yes — the agentic loop |
| 5 | Correlation | ⭐ `custom_id`; results in any order | The response to your call |
| 6 | Failures | Per request: errored / expired (not billed); resubmit those | Per call: retry the call |
| 7 | Size limits | 100,000 requests or 256 MB per batch | One request |
| 8 | Results kept | 29 days | — |

**Submission cadence for an SLA** (batch processing up to 24 h)

| # | SLA | Largest window (SLA − 24 h) | Guide example |
|---|---|---|---|
| 1 | 30 h | 6 h | ⭐ 4 h windows (leaves margin) |
| 2 | 36 h | 12 h | — |
| 3 | 48 h | 24 h (once a day) | — |
"""

HOW_IT_WORKS = """
1. **Is someone waiting, or does the task need tool results mid-request?** Use the synchronous API. Otherwise, batch.
2. **Refine the prompt on a small sample** with the synchronous API; the docs also advise dry-running one request shape.
3. **Build requests** with a unique, meaningful `custom_id` (1–64 chars: letters, digits, `-`, `_`).
4. **Submit on a cadence** where window + 24 h fits the SLA.
5. **Read results by `custom_id`.** Resubmit only errored or expired ones, fixing the cause first (e.g. chunk over-long
   documents).
"""

WHERE_SEEN = """
- **Scenario 5 — Claude Code for Continuous Integration** (Guide §5, p.4): pre-merge checks (sync) vs nightly analysis (batch).
- **Scenario 6 — Structured Data Extraction** (Guide §5, p.4): overnight extraction of large document sets.
- **Guide §8, Exercise 3** (p.25): practise batch processing with the Message Batches API.
"""

GUIDE_NOTE = ("Grounded in the exam guide §6 TS 4.5 (pp.18–19) and the Message Batches API docs (verified 2026-09-28). Cost units "
              "on this page are relative (batch = half), not prices. Section layout inspired by a community concept list "
              "(claudearchitectcertification.com — community source, unverified; no text copied).")

LAB_INTRO = """
You write a team's batch policy:

- which API each job uses;
- the `custom_id` for each request;
- how results are matched back;
- what gets resubmitted;
- how often to submit;
- whether to refine the prompt on a sample first.

The **simulated** Batches API behaves as the docs describe: results come back shuffled, some requests error or expire, and
nothing runs your tools inside a request. Seven jobs test each decision.
"""

DISTRACTORS = (
    ("A · Blocking check in a batch", "Half price.", "Up to 24 h — merges blocked.", "Sync.", "guide:4.5:S1"),
    ("B · Match results by position", "They came back in a list.", "Order isn't guaranteed.", "custom_id.", "guide:4.5:K4"),
    ("C · Resubmit the whole batch", "Simplest recovery.", "Pay again for 95 successes.", "Failed custom_ids only.", "guide:4.5:S3"),
    ("D · Resend too-long docs unchanged", "Maybe it was a blip.", "Same error again.", "Chunk them.", "guide:4.5:S3"),
    ("E · Submit once a day", "Fewer batches.", "48 h worst case > 30 h SLA.", "4 h windows.", "guide:4.5:S2"),
    ("F · Tool loop in a batch", "Batches support tool use.", "No round trip to run the tool.", "Sync.", "guide:4.5:K3"),
    ("G · No sample first", "Saves a step.", "3,000 re-dos.", "Refine on a sample.", "guide:4.5:S4"),
)

SIDE_BY_SIDE_HEADERS = ("#", "Workload (guide examples)", "API", "Why")
SIDE_BY_SIDE_ROWS = (
    ("1", "Pre-merge check on every PR", "Synchronous", "Blocking — someone waits"),
    ("2", "Nightly test generation", "Batch", "Latency-tolerant; 50% cheaper"),
    ("3", "Weekly audit", "Batch", "Latency-tolerant"),
    ("4", "Overnight report", "Batch", "Latency-tolerant"),
    ("5", "Investigation that calls tools step by step", "Synchronous", "Needs tool results mid-request"),
)

DECISION_DOT = readable('''digraph D {
  rankdir=TB; bgcolor="transparent"; nodesep=0.35; ranksep=0.4;
  node [fontname="Helvetica", fontsize=12, style="rounded,filled", fillcolor="#F3F4F6", color="#9CA3AF", penwidth=1.5];
  edge [fontname="Helvetica", fontsize=11, color="#6B7280"];
  Q1 [shape=diamond, label="Is someone waiting\\nfor the answer?"];
  Q2 [shape=diamond, label="Needs tool results\\nmid-request?"];
  SYNC [shape=box, fillcolor="#D1FAE5", color="#059669", label="Synchronous API"];
  Q3 [shape=diamond, label="Prompt tested\\non a sample?"];
  SAMPLE [shape=box, fillcolor="#FEF3C7", color="#D97706", label="Refine on a sample"];
  BATCH [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="Batch: custom_id each;\\nwindow + 24 h ≤ SLA"];
  Q1 -> SYNC [label="yes"]; Q1 -> Q2 [label="no"]; Q2 -> SYNC [label="yes"]; Q2 -> Q3 [label="no"];
  Q3 -> SAMPLE [label="no"]; SAMPLE -> BATCH; Q3 -> BATCH [label="yes"];
}''')

EXPERIMENTS = (
    "Run ✅ on all seven jobs and compare the cost units and latency.",
    "In ✅, set SUBMIT_EVERY_HOURS = 6: does the 30 h SLA still hold? What about 7?",
    "Run ⭐❌ B on results_order and read the shuffled order line.",
    "In the playground's cadence tab, type an SLA of 36 and find the largest window.",
)

QUESTIONS = (
    Question(
        q=("To cut costs, a team wants to move two workloads to the Message Batches API: the automated review that "
           "developers wait on before they can merge, and a nightly job that generates missing unit tests. What's the "
           "right call?"),
        opts=("Move both, since the 50% saving is worth it.",
              "Move only the nightly test generation; keep the pre-merge review synchronous.",
              "Move only the pre-merge review, since it runs more often.",
              "Move neither, because batches can't process code."),
        ans=1,
        explain=("Batch processing can take up to 24 hours with no latency guarantee, so it suits non-blocking work like "
                 "nightly jobs, not blocking workflows like pre-merge checks."),
        scenarios=(5,), points=("4.5:K2", "4.5:S1"),
    ),
    Question(
        q=("A batch of 500 document extractions comes back, and the team pairs each result with its input by position in "
           "the list. Some records end up with another document's data. What's the fix?"),
        opts=("Sort the results alphabetically before pairing.",
              "Submit smaller batches so the order is kept.",
              "Wait for the batch to fully finish before reading results.",
              "Give every request a custom_id and match results by custom_id."),
        ans=3,
        explain=("Batch results aren't guaranteed to come back in input order. custom_id correlates each request with its "
                 "response."),
        scenarios=(6,), points=("4.5:K4",),
    ),
    Question(
        q=("In a nightly batch of 2,000 extractions, 40 requests failed. Twelve failed because their documents exceeded "
           "the context limit. What's the most efficient recovery?"),
        opts=("Resubmit only the 40 failed requests by custom_id, splitting the 12 over-long documents into chunks first.",
              "Resubmit the whole batch of 2,000.",
              "Resubmit the 40 unchanged, since failures are transient.",
              "Process the 40 synchronously with the same prompts and sizes."),
        ans=0,
        explain=("Resubmit only the failed documents, identified by custom_id, and fix the cause (chunk over-long "
                 "documents). Resubmitting unchanged repeats the context-limit failures."),
        scenarios=(6,), points=("4.5:S3",),
    ),
    Question(
        q=("Documents arrive all day, and each must be extracted within 30 hours of arriving. Batches can take up to 24 "
           "hours to process. How often should the team submit batches?"),
        opts=("Once a day, at midnight.",
              "Every 12 hours.",
              "Every 4 hours, so waiting time plus processing stays inside 30 hours.",
              "Every 30 hours."),
        ans=2,
        explain=("Work backwards from the SLA: with up to 24 hours of processing, a document can wait at most about 6 "
                 "hours before submission. 4-hour windows keep a 30-hour SLA; daily or 12-hour windows break it."),
        scenarios=(6,), points=("4.5:S2",),
    ),
    Question(
        q=("A refund-review job needs the model to call lookup_order, see the result, then decide on the refund. Someone "
           "suggests running thousands of these as a Message Batch. What's the problem?"),
        opts=("Batches don't support the tools parameter at all.",
              "Within one batch request there's no mid-request round trip: the tool can't run and return its result for the model to continue.",
              "Batch requests can't include system prompts.",
              "Batch results expire before the refund decision is made."),
        ans=1,
        explain=("There's no multi-turn tool calling within a single batch request. Each request is one call, so a "
                 "tool-then-decide loop needs synchronous calls, or a batch per step driven by your code."),
        scenarios=(1,), points=("4.5:K3",),
    ),
    Question(
        q=("A team is about to batch-process 100,000 archived contracts with a brand-new extraction prompt. What should "
           "they do first?"),
        opts=("Refine the prompt on a representative sample until first-pass results are good, then submit the full batch.",
              "Submit all 100,000 at once to benefit from the 50% saving.",
              "Split into 100 batches of 1,000 with the same prompt.",
              "Run everything synchronously the first time."),
        ans=0,
        explain=("Refining the prompt on a sample before batch-processing large volumes raises the first-pass success "
                 "rate and avoids paying to reprocess thousands of documents."),
        scenarios=(6,), points=("4.5:S4",),
    ),
    Question(
        q=("Finance asks to move a weekly compliance audit of support transcripts to the Message Batches API. An engineer "
           "objects that results might arrive many hours later. What's the right assessment?"),
        opts=("Reject it: batches have a guaranteed one-hour turnaround, which is too short for audits.",
              "Reject it: batches can't process transcripts.",
              "Accept it only if the audit is split into real-time calls.",
              "Accept it: 50% cheaper, up to 24 hours to process, no latency guarantee — fine for a weekly audit."),
        ans=3,
        explain=("The Message Batches API gives 50% cost savings with up to 24-hour processing and no guaranteed latency, "
                 "which matches latency-tolerant work such as weekly audits."),
        scenarios=(1,), points=("4.5:K1", "4.5:K2"),
    ),
)


FAQ = (
    ("The docs say batches support tool use and multi-turn conversations — doesn't that contradict the guide?",
     "No. A batched request can include tool definitions and earlier turns. What can't happen is the round trip: Claude asks for "
     "a tool, your code runs it, and the result goes back within the same request. Each request is processed on its own, so "
     "tool loops belong on the synchronous API."),
    ("Are failed requests billed?",
     "The docs say errored, canceled and expired requests are not billed. Resubmitting only those keeps the cost at what you "
     "actually needed."),
    ("Why 4-hour windows if the arithmetic allows 6?",
     "30 − 24 = 6 is the limit with no slack. The guide's example uses 4 hours, leaving margin for queueing and resubmissions."),
    ("How big can a batch be?",
     "Up to 100,000 requests or 256 MB, whichever comes first. The docs suggest splitting very large datasets into several "
     "batches."),
)

PLAYGROUND_INTRO = """
Each tab is one decision from the lab. In the cadence tab, type your SLA in hours to see the largest submission window. It
all runs on the **simulated** Batches API; cost units are relative (batch = half), not prices.
"""


def _tab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this):
    return PlayTab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this, engine="batch")


PLAYGROUND = (
    _tab("route", "⭐ Sync or batch?", "route", "Nobody waits at the counter for overnight post.", "guide:4.5:S1",
         "Pick a job and an API.", "batch-processing; guide TS 4.5 K2–K3, S1", ("job_pick", "api_pick"),
         {"job_pick": "premerge", "api_pick": "sync"}, ("Route this job",),
         ("pre-merge + batch: blocked.", "nightly + sync: full price.", "tool investigations + batch: stop at tool_use.")),
    _tab("order", "⭐ custom_id", "order", "A label on every envelope.", "guide:4.5:K4",
         "Six results come back shuffled.", "batch-processing § Retrieving results", ("match_by",), {"match_by": "custom_id"},
         ("Match the results",), ("by position: 5 of 6 wrong.",)),
    _tab("failures", "⭐ Failures", "failures", "Re-post only what came back — trimmed if too heavy.", "guide:4.5:S3",
         "95 succeeded; 3 errored (2 too long); 2 expired.", "batch-processing § Result types; guide TS 4.5 S3",
         ("retry_mode",), {"retry_mode": "failed_chunked"}, ("Recover the failures",),
         ("all: 100 resubmitted.", "failed only: the long ones fail again.")),
    _tab("cadence", "⭐ SLA cadence", "cadence", "Post often enough that waiting + delivery fits the promise.", "guide:4.5:S2",
         "Type the SLA in hours; pick a submission window.", "guide TS 4.5 S2", ("window_hours",), {"window_hours": "4"},
         ("30", "36", "48"), ("30 h + 12 h window: broken.", "48 h + 12 h window: fine.")),
    _tab("sample", "⭐ Sample first", "sample", "Proof-read one letter before printing ten thousand.", "guide:4.5:S4",
         "10,000 tickets overnight.", "guide TS 4.5 S4; batch-processing § Best practices", ("sample_on",), {"sample_on": "yes"},
         ("Classify the tickets",), ("no sample: 3,000 re-dos.",)),
)

CONTENT = ConceptContent(
    slug="batch-api", tldr=TLDR, mental_model=MENTAL_MODEL, what_it_is=WHAT_IT_IS, how_it_works=HOW_IT_WORKS,
    where_seen=WHERE_SEEN, guide_note=GUIDE_NOTE, docs_refs=DOC_REFS, docs_verified_on=DOCS_VERIFIED_ON, grounding=GROUNDING,
    flow_dot=flow_dot, node_states=node_states, lab_intro=LAB_INTRO, variants=VARIANTS, check_outcome=check_outcome,
    distractors=DISTRACTORS, side_by_side_headers=SIDE_BY_SIDE_HEADERS, side_by_side_rows=SIDE_BY_SIDE_ROWS,
    decision_dot=DECISION_DOT, experiments=EXPERIMENTS, questions=QUESTIONS, faq=FAQ,
    related=("structured-outputs", "agentic-loops", "system-prompts"), exam_points=EXAM_POINTS, playground=PLAYGROUND,
    playground_intro=PLAYGROUND_INTRO,
    scenarios=("premerge", "nightly", "results_order", "partial_failure", "sla_cadence", "tool_loop", "sample_first"), show_ledger=False,
)
