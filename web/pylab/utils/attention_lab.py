"""
SIMULATED long-context reader for D4.7 Attention Engineering (guide TS 5.1; TS 1.6 for attention dilution).

Grounding: guide TS 5.1 (the "lost in the middle" effect; progressive summarisation losing numbers and dates; tool results
accumulating tokens out of proportion to their relevance) and the platform docs' long-context tips (prompting best practices §
Long context prompting, fetched 2026-09-28: put long documents at the top and the query at the end — up to 30% better on
complex multi-document inputs; structure documents with XML tags and metadata; ground answers in quotes).
INVENTED (simulation): how the reader drops middle sections (items in the middle third are missed unless they also appear in a
leading key-findings summary), the "query first → answers only from the first document" behaviour, how a summariser blurs
facts, and the token budget that evicts early tool results.
"""

from __future__ import annotations

import re

from utils import lab_trace

SCENARIO_IDS = ("lost_in_middle", "query_placement", "summary_drift", "verbose_tools")
SCENARIO = "lost_in_middle"
BUDGET = 6_000       # simulated tokens of tool output the conversation can hold before early results are evicted

SECTIONS = [
    {"title": f"Subagent {i + 1}: {t}", "text": body, "key": key}
    for i, (t, body, key) in enumerate([
        ("pricing", "Competitor prices rose 4% in Q2. Detailed tables follow…", "competitor prices +4% in Q2"),
        ("reviews", "Customer reviews are mostly positive; delivery complaints fell…", "delivery complaints fell"),
        ("logistics", "Warehouse capacity is adequate through Q3…", "warehouse capacity adequate to Q3"),
        ("regulation", "A new EU battery regulation takes effect 1 Jan 2027 and bans our current pack design…",
         "EU battery rule bans our pack design from 2027-01-01"),
        ("supply", "The main cell supplier signed a 3-year contract…", "cell supply secured for 3 years"),
        ("hiring", "Engineering hiring is on plan…", "hiring on plan"),
        ("marketing", "Campaign reach grew 12%…", "campaign reach +12%"),
        ("finance", "Cash runway is 26 months…", "runway 26 months"),
        ("security", "No incidents this quarter…", "no security incidents"),
    ])]
CRITICAL = "EU battery"            # the finding that sits in the middle (section 4 of 9)
QUESTION = "What is the single biggest risk to next year's product plan?"

CONVERSATION = [
    "Customer A: I was charged $1,240.00 twice for order ORD-7731.",
    "Agent: I can see both charges. I'll refund the duplicate $1,240.00.",
    "Customer A: When will it arrive? I need it by Friday 14 March.",
    "Agent: Refunds take 3-5 business days; I'll mark it urgent for Friday 14 March.",
    "Customer A: Also, my address changed to 2 Example Road.",
    "Agent: Updated. Anything else?",
    "Customer A: Just confirm the refund amount and the date again please.",
]
FACT_PATTERNS = [r"\$[\d,]+\.\d\d", r"ORD-\d+", r"Friday \d+ \w+"]

ORDER_FIELDS = [f"field_{i:02d}" for i in range(35)]


def configure(scenario_id: str) -> None:
    global SCENARIO
    SCENARIO = scenario_id if scenario_id in SCENARIO_IDS else "lost_in_middle"


def ask(prompt: str) -> str:
    """The SIMULATED reader answers QUESTION from the prompt you built."""
    q_pos = prompt.find(QUESTION)
    starts_with_q = 0 <= q_pos < 40
    first_title = SECTIONS[0]["title"]
    lead = prompt[:max(0, prompt.find(first_title))] if first_title in prompt else ""
    in_lead = CRITICAL.lower() in lead.lower()
    headers = sum(1 for s in SECTIONS if f"## {s['title']}" in prompt or f"<title>{s['title']}</title>" in prompt)
    if starts_with_q:
        used = [SECTIONS[0]["key"]]
        answer = f"Based on the first report: {SECTIONS[0]['key']}."
    else:
        n = len(SECTIONS)
        used = [s["key"] for i, s in enumerate(SECTIONS) if i < n // 3 or i >= 2 * n // 3]
        if in_lead:
            used.append(SECTIONS[3]["key"])
        answer = ("The biggest risk: the EU battery regulation bans our pack design from 1 Jan 2027." if in_lead
                  else "The biggest risk: competitor price pressure (+4% in Q2).")
    rec = {"kind": "attention_run", "scenario": SCENARIO, "task": "ask", "question_first": starts_with_q, "summary_lead": in_lead,
           "headers": headers, "used": used, "answer": answer, "found_critical": "EU battery" in answer}
    lab_trace.record(rec)
    print(f"prompt: {len(prompt):,} chars · question {'FIRST' if starts_with_q else 'at the end'} · key-findings summary up front: "
          f"{'yes' if in_lead else 'no'} · section headers: {headers}/{len(SECTIONS)}")
    print(f"the reader drew on: {used}")
    print(f"answer: {answer}")
    return answer


def summarize(turns: list) -> str:
    """A SIMULATED progressive summary: it keeps the gist and blurs the numbers and dates."""
    return "Summary: customer reported a duplicate charge; agent agreed to refund it soon; customer updated their address."


def facts_from(turns: list) -> dict:
    """Pull transactional facts (amounts, order numbers, dates) out of the turns verbatim."""
    text = " ".join(turns)
    return {"amount": (re.findall(FACT_PATTERNS[0], text) or [None])[0], "order": (re.findall(FACT_PATTERNS[1], text) or [None])[0],
            "deadline": (re.findall(FACT_PATTERNS[2], text) or [None])[0]}


def run_conversation(build_context) -> str:
    """Late in the conversation older turns are summarised; your build_context(turns) decides what the model sees."""
    turns = CONVERSATION
    context = build_context(turns)
    has = {k: bool(re.search(p, context)) for k, p in zip(("amount", "order", "deadline"), FACT_PATTERNS)}
    answer = ("Your refund of $1,240.00 for ORD-7731 is marked urgent for Friday 14 March." if all(has.values())
              else "Your refund is on its way and should arrive soon.")
    rec = {"kind": "attention_run", "scenario": SCENARIO, "task": "conversation", "context": context, "has": has, "answer": answer}
    lab_trace.record(rec)
    print(f"what the model sees for the last turn:\n{context}\n---\nfacts present: {has}\nanswer: {answer}")
    return answer


def lookup_order(i: int) -> dict:
    rec = {f: f"value {j}" for j, f in enumerate(ORDER_FIELDS)}
    rec.update(order_id=f"ORD-{1000 + i}", status="delivered", delivered_on=f"2026-03-{i + 1:02d}", total=100.0 + i,
               return_window_days=30 if i != 0 else 14)
    return rec


def run_lookups(trim) -> str:
    """Eight order lookups in one conversation; then: “which orders can still be returned?” (order 0 has a 14-day window)."""
    kept, tokens, evicted = [], 0, []
    for i in range(8):
        r = trim(lookup_order(i))
        cost = len(r) * 20
        kept.append((r, cost))
        tokens += cost
    while tokens > BUDGET:
        r, c = kept.pop(0)
        evicted.append(r.get("order_id"))
        tokens -= c
    seen = {r.get("order_id"): r for r, _c in kept}
    ok = "ORD-1000" in seen and seen["ORD-1000"].get("return_window_days") == 14
    answer = ("ORD-1000 has a 14-day window (already past); ORD-1001…1007 can be returned." if ok
              else "All eight orders can be returned within 30 days.")
    rec = {"kind": "attention_run", "scenario": SCENARIO, "task": "lookups", "fields_kept": len(kept[0][0]) if kept else 0,
           "tokens": tokens, "evicted": evicted, "answer": answer, "ok": ok}
    lab_trace.record(rec)
    print(f"fields kept per lookup: {rec['fields_kept']} · tool-output tokens: {tokens:,} (budget {BUDGET:,}) · evicted: {evicted or 'none'}")
    print(f"answer: {answer}")
    return answer
