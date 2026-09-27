"""
SIMULATED Message Batches API for D4.3 Batch API (guide TS 4.5).

Documented behaviour it follows (platform.claude.com/docs/en/build-with-claude/batch-processing, fetched 2026-09-28):
- 50% cheaper than the synchronous Messages API; asynchronous — most batches finish within an hour, results are available when
  all requests finish or after 24 hours, and requests not processed within 24 hours EXPIRE; no latency guarantee;
- every request carries a unique custom_id (1–64 chars, [a-zA-Z0-9_-]); results may come back in ANY order — match them by
  custom_id; result types: succeeded · errored (invalid request / server error — not billed) · canceled · expired (not billed);
- one request's failure doesn't affect the others; "implement appropriate retry logic for failed requests".
- each request is processed independently: your code can't run a tool mid-request and send the result back inside the
  batch (the guide: no multi-turn tool calling within a single request).
INVENTED (simulation): the jobs, the documents, which ones fail, token/cost units, the effect of refining the prompt on a sample.
"""

from __future__ import annotations

import random
import re

from utils import lab_trace

SCENARIO_IDS = ("premerge", "nightly", "results_order", "partial_failure", "sla_cadence", "tool_loop", "sample_first")
SCENARIO = "premerge"
BATCH_HOURS = 24
SYNC_COST, BATCH_COST = 1.0, 0.5

JOBS = {
    "premerge": {"name": "Pre-merge security check on every pull request", "blocking": True, "needs_tool_loop": False, "docs": 1, "sla_hours": 0.25},
    "nightly": {"name": "Nightly test generation for 400 modules", "blocking": False, "needs_tool_loop": False, "docs": 400, "sla_hours": 24},
    "results_order": {"name": "Weekly audit summaries for 6 contracts", "blocking": False, "needs_tool_loop": False, "docs": 6, "sla_hours": 48},
    "partial_failure": {"name": "Overnight extraction for 100 invoices", "blocking": False, "needs_tool_loop": False, "docs": 100, "sla_hours": 30},
    "sla_cadence": {"name": "Documents arrive all day; each must be processed within 30 hours", "blocking": False, "needs_tool_loop": False, "docs": 50, "sla_hours": 30},
    "tool_loop": {"name": "Order investigations that must call lookup_order and refund tools", "blocking": False, "needs_tool_loop": True, "docs": 20, "sla_hours": 24},
    "sample_first": {"name": "Classify 10,000 support tickets overnight", "blocking": False, "needs_tool_loop": False, "docs": 10000, "sla_hours": 24},
}


def configure(scenario_id: str) -> None:
    global SCENARIO
    SCENARIO = scenario_id if scenario_id in JOBS else "premerge"


def current_job() -> dict:
    return dict(JOBS[SCENARIO])


def _docs(n):
    return [{"id": f"DOC-{i:05d}", "text": f"document {i}", "too_long": SCENARIO == "partial_failure" and i in (7, 42)} for i in range(n)]


def run(choose_api, custom_id_for=None, attach=None, retry=None, submit_every_hours=4, sample_first=False) -> dict:
    """Run the scenario's job with your policy on the SIMULATED Batches / Messages APIs."""
    job = current_job()
    api = choose_api(dict(job))
    log = [f"job: {job['name']} · {'blocking' if job['blocking'] else 'not blocking'} · SLA {job['sla_hours']} h"
           + (" · needs tool calls mid-request" if job["needs_tool_loop"] else ""), f"API chosen: {api}"]
    rec = {"kind": "batch_run", "scenario": SCENARIO, "api": api, "log": log, "ok": True, "problem": ""}
    docs = _docs(min(job["docs"], 100))
    cost_units = job["docs"] * (SYNC_COST if api == "sync" else BATCH_COST)
    if api == "sync":
        latency = 0.05
        log.append(f"synchronous Messages API: answers in seconds; cost {cost_units:g} units")
        if job["needs_tool_loop"]:
            log.append("each investigation runs the agentic loop: tool_use → your code runs the tool → tool_result → … → end_turn")
    else:
        latency = BATCH_HOURS
        log.append(f"Message Batches API: 50% cheaper ({cost_units:g} units); up to {BATCH_HOURS} h; no latency guarantee")
        if job["needs_tool_loop"]:
            rec.update(ok=False, problem="tool_loop")
            log.append("each request ends at stop_reason tool_use — nothing runs the tool and sends the result back inside the batch; "
                       "20 investigations stop half-way")
    if job["blocking"] and api != "sync":
        rec.update(ok=False, problem="blocking")
        log.append("the developer waits for the PR check: up to 24 h with no latency guarantee — merges are blocked")
    if SCENARIO == "nightly" and api == "sync":
        rec.update(ok=False, problem="cost")
        log.append("a latency-tolerant overnight job paid full price: 400 units instead of 200")
    if SCENARIO == "results_order":
        ids = [custom_id_for(d) if custom_id_for else f"req-{i}" for i, d in enumerate(docs)]
        bad = [c for c in ids if not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", str(c))]
        dup = len(set(ids)) != len(ids)
        results = [{"custom_id": c, "type": "succeeded", "text": f"summary of {d['id']}"} for c, d in zip(ids, docs)]
        random.Random(7).shuffle(results)
        log.append(f"results arrived in this order: {[r['custom_id'] for r in results]}")
        mapping = attach(results, docs, ids) if attach else {}
        wrong = [d["id"] for d in docs if mapping.get(d["id"]) != f"summary of {d['id']}"]
        if bad or dup:
            rec.update(ok=False, problem="custom_id")
            log.append(f"invalid or duplicate custom_id values: {bad or 'duplicates'}")
        elif wrong:
            rec.update(ok=False, problem="order")
            log.append(f"{len(wrong)} of {len(docs)} documents got another document's summary: {wrong[:3]}…")
        else:
            log.append("every summary matched to its own document by custom_id")
    if SCENARIO == "partial_failure":
        results = []
        for d in docs:
            if d["too_long"]:
                results.append({"custom_id": d["id"], "type": "errored", "error": "invalid_request_error: prompt is too long"})
            elif d["id"] == "DOC-00013":
                results.append({"custom_id": d["id"], "type": "errored", "error": "api_error: internal server error"})
            elif d["id"] in ("DOC-00050", "DOC-00051"):
                results.append({"custom_id": d["id"], "type": "expired"})
            else:
                results.append({"custom_id": d["id"], "type": "succeeded"})
        plan = retry(results) if retry else {}
        resub = [c for c, a in plan.items() if a in ("resubmit", "resubmit_chunked")]
        chunked = [c for c, a in plan.items() if a == "resubmit_chunked"]
        failed = [r["custom_id"] for r in results if r["type"] != "succeeded"]
        log.append(f"results: {sum(r['type'] == 'succeeded' for r in results)} succeeded · errored {[r['custom_id'] for r in results if r['type'] == 'errored']} "
                   f"· expired {[r['custom_id'] for r in results if r['type'] == 'expired']}")
        log.append(f"your resubmission: {len(resub)} request(s){' — chunked: ' + str(chunked) if chunked else ''}")
        rec["resubmitted"], rec["chunked"] = len(resub), chunked
        if len(resub) > len(failed):
            rec.update(ok=False, problem="resubmit_all")
            log.append(f"resubmitted {len(resub)} requests to recover {len(failed)} — paying again for {len(resub) - len(failed)} that already succeeded")
        elif set(failed) - set(resub):
            rec.update(ok=False, problem="dropped")
            log.append(f"never resubmitted: {sorted(set(failed) - set(resub))}")
        elif set(chunked) != {"DOC-00007", "DOC-00042"}:
            rec.update(ok=False, problem="no_chunk")
            log.append("DOC-00007 and DOC-00042 were resubmitted unchanged — “prompt is too long” again")
        else:
            log.append("only the 5 failed documents resubmitted; the 2 over-long ones split into chunks → all 100 done")
    if SCENARIO == "sla_cadence" and api == "batch":
        worst = submit_every_hours + BATCH_HOURS
        rec["worst_case_hours"] = worst
        log.append(f"a document arriving just after a submission waits {submit_every_hours} h, then up to {BATCH_HOURS} h in the batch "
                   f"→ worst case {worst} h (SLA {job['sla_hours']} h)")
        if worst > job["sla_hours"]:
            rec.update(ok=False, problem="cadence")
    if SCENARIO == "sample_first" and api == "batch":
        first_pass = 0.97 if sample_first else 0.70
        redo = int(job["docs"] * (1 - first_pass))
        rec["redo"] = redo
        log.append(("refined the prompt on a 50-ticket sample first (sync) → " if sample_first else "sent all 10,000 with the untested prompt → ")
                   + f"first-pass success {first_pass:.0%}; {redo:,} tickets need a second batch")
        if not sample_first:
            rec.update(ok=False, problem="no_sample")
    rec["latency_hours"] = latency
    lab_trace.record(rec)
    print("\n".join(log))
    print(f"→ {'OK' if rec['ok'] else 'PROBLEM: ' + rec['problem']}")
    return rec
