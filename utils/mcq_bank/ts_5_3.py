"""Exam bank · TS 5.3. Original questions; see docs/MCQ_BANK_PLAN.md."""
from utils.mcq_sets import MCQ, Evidence

TS = "5.3"
BULLETS = {
    "K1": "Structured error context (failure type, attempted query, partial results, alternatives) lets the coordinator recover intelligently",
    "K2": "Access failures that need a retry decision differ from valid empty results (a successful query with no matches)",
    "K3": "A generic status such as 'search unavailable' hides context the coordinator needs",
    "K4": "Silently turning errors into empty successes, and ending a whole workflow on one failure, are both anti-patterns",
    "S1": "Return structured error context: failure type, what was attempted, partial results, possible alternatives",
    "S2": "Report access failures and valid empty results differently so the coordinator can decide appropriately",
    "S3": "Subagents recover locally from transient failures and propagate only what they cannot resolve, with attempts and partial results",
    "S4": "Structure synthesis output with coverage annotations: well-supported findings versus gaps from unavailable sources",
}

E_SUB = Evidence("code:agent-sdk/subagents", "intermediate tool calls and results stay inside the subagent; only its final message returns to the parent")
E_CTX = Evidence("code:agent-sdk/custom-tools", "You can add context the raw exception lacks, such as which request failed or what to try instead.")
E_FAIL = Evidence("code:agent-sdk/custom-tools", "so Claude can tell the user what went wrong rather than treating a failure as a normal result")

QUESTIONS = (
    # ---- K1: structured context drives coordinator recovery ----
    MCQ(
        id="Q5.3-01",
        q=("A patent-search subagent queried one index with an 800-term boolean string, with the terms joined by OR. The index refused it, and the subagent "
           "returned: failure type `query_too_complex`, the query it sent, the 12 hits it had gathered from the first 60 terms, "
           "and a note that the same index accepts at most 100 terms per query. The coordinator must pick its next step. "
           "Which is the best one?"),
        opts=("Re-run the same query on the same index in case the refusal was temporary, then use the 12 hits if it fails again.",
              "Give up on this index, drop the 12 hits because they came from an incomplete query, and rely on the other subagents.",
              "Send a new subagent the same 800-term query with a longer timeout, so that the index has time to process it.",
              "Split the query into groups of at most 100 terms, run each on the same index, and merge with the 12 hits."),
        ans=3,
        explain=("The failure type and the stated limit show that the cause is the shape of the query, so a modified query on the "
                 "same source is the intelligent recovery, and the partial hits stay useful. A repeats an attempt that cannot "
                 "work. B discards usable results and a reachable source. C changes the timeout, which is not what was refused."),
        scenarios=(3,), points=("5.3:K1",),
        evidence=(E_CTX,),
        qtype="choose", level="hard", principle="preserve_information",
        situation="patent index refuses an 800-term query and reports the 100-term limit",
        trap="repeat the identical call or discard the partial hits",
    ),
    MCQ(
        id="Q5.3-02",
        q=("A support coordinator runs a billing subagent and a shipping subagent for a customer asking \"why was I charged twice "
           "and where is my parcel?\". The billing subagent reports failure type `ledger_timeout`, the account it queried, and "
           "no results. The shipping subagent returns a full tracking history. What should the coordinator do?"),
        opts=("Answer the parcel part now, say the charge check is open, and retry the ledger for that account.",
              "Hold the whole reply until billing succeeds, so the customer receives one complete answer.",
              "Tell the customer both parts are unavailable, and offer to hand the case to a person right away.",
              "Treat the missing billing result as proof that no duplicate charge exists, and answer on that basis."),
        ans=0,
        explain=("The context says what failed and for which account, so the coordinator can use the part that worked and make a "
                 "targeted retry for the rest. B and C let one failed subagent block or misreport work that succeeded. D reads a "
                 "failure as a finding."),
        scenarios=(1,), points=("5.3:K1",),
        evidence=(E_CTX,),
        qtype="choose", level="medium", principle="calibrated_escalation",
        situation="billing ledger times out while the shipping lookup in the same reply succeeds",
        trap="block, misreport or invent an answer for the part that failed",
    ),
    MCQ(
        id="Q5.3-03",
        q=("An extraction coordinator sends 40-page contracts to a reader subagent. For one contract the subagent returns fields "
           "from pages 1 to 37, plus a failure record: pages 38 to 40, failure type `no_text_layer`, tried: text extraction "
           "twice. The coordinator currently marks the contract failed and re-queues all 40 pages. How should recovery work instead?"),
        opts=("Raise the retry count for text extraction on this contract, since two attempts did not settle it.",
              "Keep the 37 pages' fields and send only pages 38 to 40 to a path that can read scanned images.",
              "Store the 37 pages' fields as the final record and mark the contract complete to avoid more cost.",
              "Re-queue all 40 pages to a second reader subagent, to check that the first one read pages 1 to 37 correctly."),
        ans=1,
        explain=("The record gives a failure type, the scope of the failure and the work already done, so the coordinator can redo "
                 "only the missing part by a different route. A repeats an approach that the failure type says cannot work. C "
                 "hides a gap in the record. D repeats finished work."),
        scenarios=(6,), points=("5.3:K1",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 5.3 Knowledge 1 (use failure type, scope and partial results to recover); no official page covers it.",
        qtype="choose", level="hard", principle="preserve_information",
        situation="contract pages 38 to 40 have no text layer while 37 pages were extracted",
        trap="re-run everything or mark a partial record complete",
    ),
    # ---- K2: access failure vs valid empty result ----
    MCQ(
        id="Q5.3-04",
        q=("A coordinator sent two subagents to check a regulator's enforcement database and a court-records site for a named company. "
           "Subagent 1 returns status `ok`, 0 matches, and the three queries it ran. Subagent 2 returns status `failed`, failure "
           "type `access_denied`, 0 matches. How should the coordinator treat them?"),
        opts=("Both as unknown, because neither produced a match to cite in the report.",
              "Subagent 1 as a finding of none, and subagent 2 as a source still to cover another way.",
              "Both as findings of absence, since either way the company has no matches in the sources checked.",
              "Subagent 2 as a finding of absence, and subagent 1 as unreliable until it repeats its three queries."),
        ans=1,
        explain=("A query that ran and found nothing is a real result, while a source that refused access has told the coordinator "
                 "nothing about the company. A and C erase the difference between those two. D reverses it."),
        scenarios=(3,), points=("5.3:K2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 5.3 Knowledge 2 (a source that ran and found nothing versus a source that refused access); no official page covers it.",
        qtype="choose", level="easy", principle="fit_for_purpose",
        situation="one source returns zero matches normally and another is denied",
        trap="read both zero-match responses the same way",
    ),
    MCQ(
        id="Q5.3-05",
        q=("A support coordinator looks up warranty cover through a subagent. For customers whose products are outside every "
           "warranty programme, the subagent returns an empty list with status `ok`. The coordinator's own retry code fires "
           "whenever a subagent returns an empty list, so it then spends three more subagent calls on a different search. "
           "These extra calls appear in 30% of conversations and never change the answer. What is the most effective change?"),
        opts=("Raise the subagent's timeout so that slow lookups finish before the coordinator's retry code runs.",
              "Have the subagent return a confidence value, which the coordinator uses to skip the extra search.",
              "Fire the coordinator's retry on `status: failed`, and treat an empty `ok` list as the answer.",
              "Cap the coordinator at one extra subagent call per conversation, whatever the status says."),
        ans=2,
        explain=("An `ok` status with an empty list is a complete answer for an uncovered product, so retries belong to failures only. "
                 "A targets slowness, but the lookups here finished with status `ok`. B adds a self-reported number to a distinction "
                 "the status already makes. D lowers the waste but still retries real answers and still allows one retry on a failure."),
        scenarios=(1,), points=("5.3:K2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 5.3 Knowledge 2 (a successful query with no matches is not an access failure); no official page covers it.",
        qtype="fix", level="medium", principle="root_cause",
        situation="coordinator retry code fires on every empty ok warranty lookup",
        trap="tune timeouts or add a confidence number instead of changing the trigger",
    ),
    MCQ(
        id="Q5.3-06",
        q=("A research subagent reports two problems to the coordinator. Problem 1: the news archive timed out after 30 seconds on "
           "a broad query. Problem 2: the licensed journal service answered `access_denied` for a subscription the team does not "
           "hold. Which retry decision for the coordinator is best?"),
        opts=("Retry problem 1 with a narrower query, and use another source for problem 2.",
              "Retry both with the same query, because the coordinator cannot know which failures will clear.",
              "Retry problem 2 with a longer timeout, and treat problem 1 as a gap because it already failed once.",
              "Treat both as gaps and stop, because the subagent already used its attempts on them."),
        ans=0,
        explain=("A timeout may clear with a changed attempt, while a denied subscription will not clear by repeating it, so the "
                 "failure types point to different decisions. B ignores the types. C swaps them. D stops although problem 1 has an "
                 "obvious modified attempt left."),
        scenarios=(3,), points=("5.3:K2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 5.3 Knowledge 2 (timeouts need a retry decision, denied access does not clear by repeating); no official page covers it.",
        qtype="choose", level="medium", principle="proportionate",
        situation="archive timeout versus a subscription the team does not hold",
        trap="apply one retry rule to both failure types",
    ),
    # ---- K3: generic statuses hide context ----
    MCQ(
        id="Q5.3-07",
        q=("A literature-review coordinator receives `{\"status\": \"search unavailable\"}` from a subagent whenever any of its three "
           "databases fails, and in 27% of runs the final report drops that topic entirely. A sample of the failures shows that 40% were "
           "paywall or `access_denied` errors, which fail the same way on every retry, and the rest were timeouts. Which change is "
           "most effective?"),
        opts=("Add an instruction telling the coordinator to retry any topic whose status is `search unavailable`.",
              "Switch the subagent to a larger model, which will better judge what went wrong before replying.",
              "Raise the subagent's timeouts so that fewer databases fail in the first place.",
              "Return the failure type, the database and query tried, and any results already gathered."),
        ans=3,
        explain=("With context, the coordinator can retry the timeouts, switch database for the paywalls, and keep results "
                 "already found. A retries all of them blindly, and the 40% never clear. B gives a model more to guess about "
                 "without the facts. C reduces how often timeouts occur but leaves every remaining failure opaque."),
        scenarios=(3,), points=("5.3:K3",),
        evidence=(E_CTX,),
        qtype="fix", level="medium", principle="preserve_information",
        situation="search unavailable status leads to whole topics dropped from review reports",
        trap="retry blindly, change the model, or tune timeouts",
    ),
    MCQ(
        id="Q5.3-08",
        q=("A support coordinator gets `Order system error` from the order subagent, which has already retried each call three times "
           "with backoff before returning it. The coordinator escalates every such case to a human, 41% of tickets, and the escalation "
           "policy matches what the support team wrote. A sample shows 60% of the cases were a deploy window that ended minutes later, "
           "and 40% were permanent (cancelled orders, missing permissions). What is the root cause of the over-escalation?"),
        opts=("The coordinator's escalation policy is stricter than it should be for order problems.",
              "The message cannot tell the coordinator a deploy window that clears from a failure that does not.",
              "The order service deploys too often, and its schedule should be moved to quieter hours.",
              "The order subagent should retry for several minutes before reporting, so the message is never needed."),
        ans=1,
        explain=("One message covers transient and permanent failures, so escalating every case is the only safe choice for the "
                 "coordinator. A contradicts the stem, since the policy matches the support team's. C addresses frequency while the "
                 "missing signal stays. D keeps the customer waiting for the 40% that never clear and still returns an opaque message."),
        scenarios=(1,), points=("5.3:K3",),
        evidence=(E_CTX,),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="one order system error message sends 41% of tickets to humans",
        trap="tune the policy or fix the symptom's frequency",
    ),
    MCQ(
        id="Q5.3-09",
        q=("A trace-review team notes that the final report often says \"market-size data unavailable\" with no cause. They propose "
           "that the subagent keep the generic message but write the details to its log file, which engineers can open. How should "
           "you evaluate the proposal?"),
        opts=("Accept it: the details are kept, and engineers can find the cause when they review the run.",
              "Reject it: the live recovery decision needs the details in what comes back, not in a log.",
              "Accept it, provided the log also records the time of each failure for later analysis.",
              "Reject it, and rerun the subagent in case a later final message shows the cause."),
        ans=1,
        explain=("The coordinator decides whether to retry, switch source or report a gap while the run is live, from what the "
                 "subagent returns, so the details belong in that message. A and C help later review but not that decision. D reruns "
                 "the subagent in the hope of a different message, when the details could simply be returned."),
        scenarios=(3,), points=("5.3:K3",),
        evidence=(E_SUB,),
        qtype="evaluate", level="easy", principle="preserve_information",
        situation="details of a market-size failure kept only in a log file",
        trap="treat after-the-fact logs as a substitute for context passed up",
    ),
    # ---- K4: the two anti-patterns ----
    MCQ(
        id="Q5.3-10",
        q=("An invoice pipeline's page reader catches every exception and returns a blank record for that page so the batch "
           "continues. Month-end reconciliation finds 5% of invoices with a blank total, and each had gone through with status "
           "`done`. Which change addresses the cause?"),
        opts=("Add a nightly job that scans for blank totals and re-queues those invoices for the reader.",
              "Ask the downstream agent to ignore invoices whose total is blank when it prepares the monthly figures.",
              "Return a failure record with the type, page and partial fields, and mark the invoice as incomplete.",
              "Have the reader retry each page five times before it returns a blank record."),
        ans=2,
        explain=("The blank record converts a failure into a success, so nothing downstream can know a page was lost. Reporting the "
                 "failure with its context fixes that at the source. A repairs some losses after the fact and leaves the status "
                 "misleading. B hides the loss from the figures. D delays the same blank result for pages that never succeed."),
        scenarios=(6,), points=("5.3:K4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 5.3 Knowledge 4 (turning a failure into an empty success is an anti-pattern); no official page covers it.",
        qtype="fix", level="medium", principle="root_cause",
        situation="reader returns blank records for failed pages and invoices finish as done",
        trap="clean up blanks downstream or retry more",
    ),
    MCQ(
        id="Q5.3-11",
        q=("A coordinator runs five source-specific subagents in parallel, each about 90% done after 20 minutes. The patent "
           "subagent hits a licence error. The coordinator cancels the other four and ends the run with no report. This happens in "
           "22% of runs. What is the best design?"),
        opts=("Retry the patent subagent from the start before cancelling the others, to see if the error clears.",
              "Wait for the other four to finish, then stop the run, because one missing source makes any report incomplete.",
              "Cancel the others as now, but store their partial work for a manual restart later.",
              "Let the four finish, record the patent failure with its cause, and build the report with that gap marked."),
        ans=3,
        explain=("One source failing is a coverage problem, not a reason to discard finished work from four others. A retries a "
                 "licence error that repeating will not fix. B and C still produce no report for the reader. D delivers a report "
                 "that is usable and honest about what is missing."),
        scenarios=(3,), points=("5.3:K4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 5.3 Knowledge 4 (ending a whole workflow on one failure is an anti-pattern); no official page covers it.",
        qtype="fix", level="medium", principle="proportionate",
        situation="licence error in one of five parallel subagents cancels the other four",
        trap="end the workflow, or wait and still deliver nothing",
    ),
    MCQ(
        id="Q5.3-12",
        q=("In a code review for your research agent, a colleague adds a wrapper around every subagent call: `try: return run() "
           "except Exception: return []`. They say the report stays clean because failures no longer interrupt the run. "
           "How should you evaluate it?"),
        opts=("Accept it: the coordinator can still run its checks on the lists it receives from each subagent.",
              "Accept it, if the wrapper writes the exception to a log so that engineers can find the failures later.",
              "Reject it, and instead stop the whole run on the first exception so no failure goes unnoticed.",
              "Reject it: a failed call becomes an empty success, so the report may claim there is nothing to find."),
        ans=3,
        explain=("An empty list is how a source with no matches looks, so the wrapper hides failures from everything that reads the "
                 "result. A assumes the checks can see a difference the wrapper removed. B records it where the coordinator "
                 "cannot use it. C swaps one anti-pattern for the other by ending everything on a single failure."),
        scenarios=(3,), points=("5.3:K4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 5.3 Knowledge 4 (turning a failure into an empty success is an anti-pattern); no official page covers it.",
        qtype="evaluate", level="easy", principle="deterministic",
        situation="wrapper converts every subagent exception into an empty list",
        trap="log it quietly or end the whole run",
    ),
    # ---- S1: return structured error context ----
    MCQ(
        id="Q5.3-13",
        q=("You are writing the output format for a web-search subagent in a multi-agent research system, so that the coordinator "
           "can recover on its own when a search fails. Which failure record should the subagent return?"),
        opts=("`failure_type`, `source`, `query_attempted`, `partial_results`, and `alternatives` to try.",
              "`failure_type`, `source`, `query_attempted`, and `alternatives`, with partial results left in the log.",
              "`failure_type`, `source`, `query_attempted`, `partial_results`, and a `confidence` between 0 and 1.",
              "`status: \"failed\"`, `source`, `query_attempted`, `partial_results`, and `alternatives`."),
        ans=0,
        explain=("These fields cover what failed, what was tried, what survives, and where to go next, which are the decisions the "
                 "coordinator must make. B leaves the surviving results out of what comes back. C swaps the alternatives for a "
                 "self-reported number that suggests no next step. D has only a generic status, so the coordinator cannot tell a "
                 "timeout from a denied subscription."),
        scenarios=(3,), points=("5.3:S1",),
        evidence=(E_CTX,),
        qtype="configure", level="medium", principle="explicit",
        situation="designing the failure record of a web-search subagent",
        trap="omit partial results, add a self-reported confidence or keep a generic status",
    ),
    MCQ(
        id="Q5.3-14",
        q=("A support subagent checks eight order IDs against a shipping API. After 6 succeed it hits a throttle and returns "
           "`{\"failure_type\": \"throttled\", \"query\": \"order 7\"}`. The coordinator re-runs all eight IDs, which costs "
           "extra API calls and re-triggers the throttle in 15% of runs. What is the missing piece?"),
        opts=("The six lookups that succeeded, so that the coordinator re-runs only the order IDs left.",
              "A longer delay, which the subagent should wait before it returns the failure to the coordinator.",
              "A confidence score for the six lookups, so the coordinator can decide whether to trust them.",
              "A field naming the model that ran the subagent, so the coordinator can retry with another."),
        ans=0,
        explain=("The record shows what failed but not what was done, so the coordinator cannot avoid repeating finished work. "
                 "B moves the same limit later without saving anything. C and D add information that does not change which IDs "
                 "remain."),
        scenarios=(1,), points=("5.3:S1",),
        evidence=(E_CTX,),
        qtype="diagnose", level="medium", principle="preserve_information",
        situation="shipping lookups redone for all eight IDs after a rate limit at the seventh",
        trap="add delay, confidence or model fields",
    ),
    MCQ(
        id="Q5.3-15",
        q=("A research system has three layers: a search subagent, the coordinator, and a synthesis subagent. The search subagent "
           "returns failure type `paywall`, the query, and 3 partial results. The coordinator passes the synthesis agent only "
           "\"search partly failed\" plus the results. The final report states 3-source findings as complete. Where was the "
           "context lost?"),
        opts=("In the search subagent, whose failure record was missing a field for the number of sources.",
              "In the synthesis subagent, which should have inferred the gap from the shortage of results.",
              "In the report format, which needs a longer summary section to fit every failure in.",
              "In the coordinator, which summarised the record and did not pass the fields on."),
        ans=3,
        explain=("The search subagent supplied everything; the coordinator compressed it into a phrase, so the next layer could not "
                 "tell what was missing. A is contradicted by the record in the stem. B asks the agent to guess from absence. C "
                 "treats it as a space problem while the fields were never passed on."),
        scenarios=(3,), points=("5.3:S1",),
        evidence=(E_CTX,),
        qtype="diagnose", level="hard", principle="preserve_information",
        situation="coordinator shortens a paywall failure to search partly failed before synthesis",
        trap="blame the first or last layer instead of the one that compressed",
    ),
    # ---- S2: access failure vs valid empty result in reporting ----
    MCQ(
        id="Q5.3-16",
        q=("A coordinator is compiling a prior-art brief from six source subagents. Four report `status: ok` with 0 results after "
           "three phrasings each, one reports `ok` with 3 results, and one reports `failed` with failure type `timeout`. The brief "
           "must state which sources found nothing. What should the coordinator do next?"),
        opts=("Re-run all six with broader queries, since an empty result might hide a hit.",
              "Retry only the timed-out source, narrowed, and report the four empty `ok` sources as searched, no hits.",
              "Report the timed-out source as having no hits too, since five of six sources agree there is little to find.",
              "Hold the brief and escalate to a person until every source returns at least one result."),
        ans=1,
        explain=("The four empty results are complete answers, and only the timeout is a failure with a sensible modified retry. A "
                 "repeats searches that succeeded. C turns an unsearched source into a finding. D treats a valid empty result as a "
                 "fault and blocks the brief for no reason."),
        scenarios=(3,), points=("5.3:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 5.3 Skill 2 (the coordinator acts differently on access failures and valid empty results); no official page covers it.",
        qtype="choose", level="medium", principle="proportionate",
        situation="four valid empty sources and one timeout in a six-source prior-art brief",
        trap="re-run everything or fold the failed source into the empty ones",
    ),
    MCQ(
        id="Q5.3-17",
        q=("A contract-review coordinator asks a subagent to find indemnity clauses in 30 contracts. It reports 0 clauses for 4 "
           "contracts, all with `status: ok`. A reviewer opens them and finds two are scanned images, whose text extraction "
           "returned an empty string, and that the other two have no indemnity clause. What is the best change?"),
        opts=("Add a rule that any contract with 0 clauses is sent to a person, whatever the cause.",
              "Have the subagent run extraction a second time for contracts with 0 clauses, then report the result.",
              "Report an unreadable document as a failure with its type; keep `ok` and 0 for readable ones.",
              "Give the subagent a larger context window, which will let it read more of each contract."),
        ans=2,
        explain=("The subagent has to say whether it could read the document, since 0 clauses is only a finding when the text was "
                 "read. A hands people the contracts that really have none and does not name the cause. B repeats an extraction "
                 "that gives the same empty string. D addresses length when the contract had no text."),
        scenarios=(6,), points=("5.3:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 5.3 Skill 2 (an unreadable document is an access failure, not a valid empty result); no official page covers it.",
        qtype="diagnose", level="hard", principle="root_cause",
        situation="scanned contracts with empty text reported as having 0 indemnity clauses",
        trap="route every zero to a person or re-run the same extraction",
    ),
    MCQ(
        id="Q5.3-18",
        q=("Before release you must show that your research system tells a source that was unreachable from a source with no "
           "matches. How should you evaluate it?"),
        opts=("Compare the length of reports from a run with all sources up against a run with one source down.",
              "Ask the coordinator at the end of each run how confident it is that no sources were missed.",
              "Time out one source, seed another with no matches, and check the report words them apart.",
              "Run the system on 200 live topics and check that none finishes with an unhandled exception."),
        ans=2,
        explain=("Injecting both conditions deliberately checks the distinction directly, with known ground truth. A depends on "
                 "report length, which can change for other reasons. B uses the agent's own confidence. D shows that nothing "
                 "crashed, which a system that swallows failures would also pass."),
        scenarios=(3,), points=("5.3:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 5.3 Skill 2 (reports must distinguish access failures from valid empty results); no official page covers it.",
        qtype="evaluate", level="medium", principle="independent_check",
        situation="proving a report separates an unreachable source from an empty one",
        trap="measure length, self-reported confidence or absence of crashes",
    ),
    # ---- S3: local recovery, propagate only the unresolved ----
    MCQ(
        id="Q5.3-19",
        q=("A journal-search subagent is assigned to peer-reviewed sources, and the coordinator tracks which source types are "
           "covered. Its journal API times out after backoff retries and one try on the publisher's mirror. It can also reach a "
           "general web search tool. What should it do?"),
        opts=("Switch to the web search and return its results as if they came from journals, so coverage is complete.",
              "Return the failure with the attempts made and the partial results, for the coordinator to act on.",
              "Keep retrying the journal API until it answers, since the coordinator is waiting for journal results.",
              "Return an empty result set with status `ok`, because no peer-reviewed article was found."),
        ans=1,
        explain=("The subagent has done its local recovery for this source, and which other source type to use is a coverage decision "
                 "that belongs to the coordinator, so the failure goes up with what is needed to decide. A changes the source "
                 "type and hides it. C has no end and blocks the coordinator. D reports a failure as no matches."),
        scenarios=(3,), points=("5.3:S3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 5.3 Skill 3 (propagate what cannot be resolved locally, with attempts and partial results); no official page covers it.",
        qtype="choose", level="hard", principle="calibrated_escalation",
        situation="journal API fails after retries while a general web search is available",
        trap="switch source type silently, retry forever or report no matches",
    ),
    MCQ(
        id="Q5.3-20",
        q=("A search subagent makes three attempts in all at each failed request, spacing the attempts as the API's documentation advises, then "
           "reports the failure type and the three attempts to the coordinator. The coordinator re-runs the failed subagent call up to "
           "three times. Against a rate-limited API, logs show nine identical requests for each outage, and the API blocks the key for "
           "an hour in 12% of outages. What is the root cause?"),
        opts=("The coordinator's retry count is too high for the allowance the API gives one key.",
              "The subagent's three attempts are more than the API tolerates in a single outage.",
              "The API is shared with other teams, so the block comes from their traffic and not from this system.",
              "The coordinator repeats the same call blindly although the report shows it was exhausted."),
        ans=3,
        explain=("The subagent's attempts are the local recovery, and its report says they were used up. The coordinator should act on "
                 "that, with a changed query or another source, and not repeat the call. A and B adjust numbers inside a pattern that "
                 "multiplies. C blames outside traffic although the log shows nine identical requests from this system."),
        scenarios=(3,), points=("5.3:S3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 5.3 Skill 3 (propagate what cannot be resolved locally, with the attempts made); no official page covers it.",
        qtype="diagnose", level="hard", principle="root_cause",
        situation="three subagent retries under three coordinator retries produce nine identical requests",
        trap="tune the retry numbers instead of removing the repeated blind call",
    ),
    MCQ(
        id="Q5.3-21",
        q=("A news subagent runs ten queries, retries two failures with backoff and gives up on a third after a refused connection, "
           "writing each attempt in its tool calls. The coordinator's next step is wrong each time: it re-queries the same "
           "host, because the only thing it received was \"1 query failed\". What should change?"),
        opts=("The subagent's final message should state the failed query, the host, what it tried, and the results so far.",
              "The coordinator should read the subagent's tool calls to see what was attempted before it chooses the next step.",
              "The subagent should write its attempts to a shared file that the coordinator is told to open.",
              "The subagent should stop after the first failure and let the coordinator decide whether to retry."),
        ans=0,
        explain=("The coordinator receives the subagent's final message, and its tool calls stay inside the subagent, so whatever "
                 "must inform the next step has to be in that message. B assumes tool calls are returned to the parent, but only the final message is. C adds "
                 "a channel for something one message can carry. D drops local recovery for failures that backoff would clear."),
        scenarios=(3,), points=("5.3:S3",),
        evidence=(E_SUB,),
        qtype="fix", level="medium", principle="preserve_information",
        situation="attempt details stay in the subagent's tool calls and the coordinator sees one query failed",
        trap="expect the coordinator to read tool calls or add a side channel",
    ),
    # ---- S4: coverage annotations in synthesis ----
    MCQ(
        id="Q5.3-22",
        q=("A synthesis agent builds a report on seven topics. Sources for topic 5 were unavailable (the licensed database was "
           "denied and the archive timed out), and the other six are well covered by 3 to 5 sources each. Which output is best?"),
        opts=("Leave topic 5 out, so that every section of the report is supported and the report reads consistently.",
              "Write topic 5 from the model's background knowledge, marked with a footnote that no source was found.",
              "Include topic 5 with a coverage note: no findings, sources unavailable, and the failures behind it.",
              "Place a single line at the start of the report saying that coverage may be incomplete for some topics."),
        ans=2,
        explain=("The reader should see which part is supported and which is a gap, with the reason. A removes the gap from view. "
                 "B fills it with content that has no source behind it. D warns generally and does not say which topic or why."),
        scenarios=(3,), points=("5.3:S4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 5.3 Skill 4 (coverage annotations show supported findings versus gaps from unavailable sources); no official page covers it.",
        qtype="fix", level="easy", principle="explicit",
        situation="one topic of seven has no sources because two were unavailable",
        trap="drop the topic, fill it from memory or add a vague disclaimer",
    ),
    MCQ(
        id="Q5.3-23",
        q=("Reviewers of a research report say every section reads equally confident. Run logs show sections 2 and 6 rest on one "
           "source each because the other sources timed out, while the rest cite four or more. Which change to the synthesis "
           "output fixes this?"),
        opts=("Add a coverage field to each finding: how many sources support it and which were unavailable.",
              "Have the synthesis agent give each finding a confidence percentage, based on how sure it feels.",
              "Remove findings supported by a single source, so that every statement in the report is well supported.",
              "Move the failed-source list to a final appendix, which readers can consult if they want to."),
        ans=0,
        explain=("The annotation travels with each finding, so a reader sees which findings are thin and why. B uses a self-reported "
                 "number that does not reflect the sources. C removes true information instead of labelling it. D separates the "
                 "gaps from the findings they affect."),
        scenarios=(3,), points=("5.3:S4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 5.3 Skill 4 (coverage annotations per finding); no official page covers it.",
        qtype="fix", level="hard", principle="calibrated_escalation",
        situation="single-source sections read as confident as four-source sections",
        trap="self-reported confidence, deletion or an appendix",
    ),
    MCQ(
        id="Q5.3-24",
        q=("A synthesis agent ends its brief on seven topics with the line \"All 7 topics covered\". Topics 3 and 6 rest on partial "
           "subagent results because the archive and a licensed database failed, and each carries `status: partial` in the data the "
           "agent received. A reader finds the gaps a month later. Which closing line is best?"),
        opts=("State how many topics were covered and an average coverage percentage across all seven.",
              "List the topics that rest on full results, and email the two partial topics to the author separately.",
              "Say all 7 topics are covered, since each topic's `status: partial` is already shown in its section.",
              "Name the 5 fully supported topics, mark topics 3 and 6 as partial, and give each failed source."),
        ans=3,
        explain=("The closing line must separate supported topics from gaps and give the reason, because readers act on it first. A "
                 "averages the gap away. B moves the warning out of the brief. C keeps the headline claim and leaves the gap to a "
                 "field that the closing line contradicts."),
        scenarios=(3,), points=("5.3:S4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 5.3 Skill 4 (coverage annotations in synthesis output); no official page covers it.",
        qtype="choose", level="easy", principle="explicit",
        situation="closing line says all 7 topics covered while two rest on partial results",
        trap="average completeness, split the warning off, or rely on a field the headline contradicts",
    ),
)
