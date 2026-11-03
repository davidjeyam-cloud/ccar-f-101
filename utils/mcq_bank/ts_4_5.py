"""Exam bank · TS 4.5. Original questions; see docs/MCQ_BANK_PLAN.md."""
from utils.mcq_sets import MCQ, Evidence

TS = "4.5"
BULLETS = {
    "K1": "Message Batches API facts: half the cost, up to a 24-hour window, no guaranteed latency",
    "K2": "Batch suits non-blocking, latency-tolerant work and does not suit blocking workflows",
    "K3": "A batch request cannot run a tool mid-request and return the result to the model",
    "K4": "custom_id correlates each batch request with its result",
    "S1": "Matching the API approach (synchronous or batch) to the workflow's latency requirement",
    "S2": "Working out how often to submit batches so that the SLA holds given the 24-hour processing window",
    "S3": "After failures, resubmit only the failed documents by custom_id, with the fix the failure calls for",
    "S4": "Refine the prompt on a sample set before processing a large volume in a batch",
}

_API = "api:build-with-claude/batch-processing"

QUESTIONS = (
    # ---- K1: the facts ----
    MCQ(
        id="Q4.5-01",
        q=("Your nightly job asks Claude to draft unit tests for 1,200 modules through the Message Batches API, submitted at 01:00. "
           "For three weeks the batch ended between 01:40 and 02:10, and a release engineer wants the runbook to promise testers a "
           "finished suite by 03:00 every night. On one Friday the batch was still running at 20:00, and running the whole job "
           "synchronously takes about three hours. How should you evaluate the promise?"),
        opts=("Keep it: three weeks of timings show the usual duration, and the Friday run is one outlier to investigate later.",
              "Drop it: the API sets no latency guarantee, only a 24-hour limit, so later steps must cope with a late suite.",
              "Keep it, and cancel any batch still running at 03:00 so that the work can be rerun with synchronous calls.",
              "Drop it, and promise 12 hours instead, since half of the 24-hour limit leaves room for a slow night."),
        ans=1,
        explain=("The service sets an upper bound of 24 hours and no latency guarantee, so a fixed delivery time cannot be promised "
                 "from observed timings. A treats a typical time as a guarantee, and the Friday run shows how far it can stray. C "
                 "starts a three-hour synchronous run at 03:00, so the suite would still miss the promise. D swaps one unsupported "
                 "number for another."),
        scenarios=(5,), points=("4.5:K1",),
        evidence=(Evidence(_API, "The system processes each batch as fast as possible, with most batches completing within 1 hour."),
                  Evidence(_API, "Batches expire if processing does not complete within 24 hours.")),
        qtype="evaluate", level="medium", principle="fit_for_purpose",
        situation="nightly test-generation batch with a 03:00 delivery promise based on three typical weeks",
        trap="read the usual duration as a guarantee",
    ),
    MCQ(
        id="Q4.5-02",
        q=("A batch of 40,000 scanned-form extractions was submitted at 21:00. A day later it shows as ended: 36,500 results are "
           "succeeded, none are errored, and 3,500 carry the result type expired. The forms behind the expired results look ordinary, "
           "and a synchronous test of ten of them extracts cleanly. What is the most likely root cause?"),
        opts=("Those forms exceeded the context limit, so the service stopped them before they ran.",
              "The forms were malformed, and the service marked them expired after checking them.",
              "Their ids repeated, so the service dropped the second copy of each.",
              "Processing ran out of time before those requests reached the model."),
        ans=3,
        explain=("An expired result means the batch reached its expiration before that request was sent to the model, so the request "
                 "never ran at all. A and B describe input problems, which would show up as errored results and would also fail in "
                 "the synchronous test. C invents a duplicate-dropping behaviour."),
        scenarios=(6,), points=("4.5:K1",),
        evidence=(Evidence(_API, "Batch reached its 24-hour expiration before this request could be sent to the model."),),
        basis="docs",
        qtype="diagnose", level="medium", principle="root_cause",
        situation="3,500 extraction requests marked expired with no errors in a 40,000 batch",
        trap="read expired as a bad-input failure",
    ),
    MCQ(
        id="Q4.5-03",
        q=("An insurer's intake service must have claim fields extracted within 3 hours of a document arriving, because adjusters "
           "begin from them. It makes one synchronous call per document today. A proposal moves it to the Message Batches API, "
           "noting that most batches finish within an hour and cost half as much. How should you evaluate the proposal?"),
        opts=("Adopt it with hourly submission, since a batch that finishes in an hour fits inside a 3-hour limit.",
              "Adopt it, and move the deadline in the service agreement to 24 hours to match the batch limit.",
              "Keep it synchronous: batches carry no latency guarantee, so a 3-hour deadline cannot be promised.",
              "Adopt it with submission every 30 minutes, so that no document waits long for a batch to start."),
        ans=2,
        explain=("The deadline is a business requirement, and an API with no latency guarantee and a 24-hour limit cannot promise "
                 "it. A and D count the typical hour (or the wait to submit) and ignore that processing can take far longer. B "
                 "changes the requirement instead of meeting it."),
        scenarios=(6,), points=("4.5:K1", "4.5:S1"),
        evidence=(Evidence(_API, "The system processes each batch as fast as possible, with most batches completing within 1 hour."),),
        qtype="evaluate", level="medium", principle="fit_for_purpose",
        situation="3-hour claim extraction deadline weighed against a half-price batch that usually ends in an hour",
        trap="submit more often to shorten the wait",
    ),
    # ---- K2: suitable and unsuitable workloads ----
    MCQ(
        id="Q4.5-04",
        q=("A release pipeline holds each production deploy until Claude has summarised the breaking changes since the last release. "
           "Deploys happen about 12 times a day, each must have the summary before it goes out, and none may wait more than 10 minutes for it. In your own tests, batches of these "
           "summaries took 25 to 60 minutes. A teammate proposes the Message Batches API for the saving. What is the best response?"),
        opts=("Keep the stage synchronous: a deploy that waits on the result cannot absorb a batch's open turnaround.",
              "Move it to batches and submit the summary when the release's first commit lands, so it is ready by deploy time.",
              "Move it to batches with a 10-minute timeout, then fall back to a synchronous call.",
              "Move it to batches with a 24-hour timeout, and ship when the summary lands."),
        ans=0,
        explain=("A stage that blocks a deploy needs an answer on demand, and batches give no latency guarantee. B hopes that "
                 "an early start finishes in time and cannot cover commits that land later. C would fall back on most deploys, "
                 "since the tests took 25 to 60 minutes against a 10-minute limit, so it pays twice and still waits. D drops the "
                 "requirement that the deploy waits for the summary."),
        scenarios=(5,), points=("4.5:K2",),
        evidence=(Evidence(_API, "This approach is well-suited to tasks that do not require immediate responses"),),
        qtype="evaluate", level="medium", principle="fit_for_purpose",
        situation="deploy gate that waits on a change summary is proposed for batching",
        trap="keep the timeout and add a synchronous fallback",
    ),
    MCQ(
        id="Q4.5-05",
        q=("A document service runs three Claude workloads: (1) extraction shown to a user in the upload form within seconds so the "
           "user can confirm it, (2) a nightly reconciliation report that finance reads some time the next afternoon, and (3) re-extraction of 90,000 "
           "stored forms after a schema change, needed by the end of next week. Cost is the concern. Which workloads should move to "
           "the Message Batches API?"),
        opts=("Only workload 2, as the others have a user or a deadline attached.",
              "Workloads 2 and 3, with workload 1 left synchronous.",
              "Workloads 1 and 2, since both run every day and so save the most over time.",
              "All three, with the upload form showing a pending state until a batch ends."),
        ans=1,
        explain=("The report and the re-extraction can both wait, so both suit batches; the upload form has a person waiting for "
                 "an answer in seconds. A leaves out the re-extraction, whose deadline is a week away. C picks the workload with a "
                 "user waiting. D turns an instant confirmation into an open-ended wait."),
        scenarios=(6,), points=("4.5:K2",),
        evidence=(Evidence(_API, "This approach is well-suited to tasks that do not require immediate responses"),),
        qtype="choose", level="easy", principle="fit_for_purpose",
        situation="three workloads in one document service: live upload, nightly report, schema-change backfill",
        trap="move the busiest workload first",
    ),
    MCQ(
        id="Q4.5-06",
        q=("A nightly Message Batch drafts tests for 1,200 modules and normally ends within the hour. After the release train was "
           "changed to start its 06:00 build only once the batch has ended, builds began at 14:00 and at 21:00 on two nights. "
           "Running the generation synchronously would take about nine hours. The team wants the build to stop waiting on the batch. What is the most effective fix?"),
        opts=("Poll the batch every minute, so that the build starts as soon as the last result lands.",
              "Split the modules across 12 batches submitted at 01:00, so that each of them ends sooner.",
              "Move generation to synchronous calls started at 01:00, so the suite is ready before the build.",
              "Build at 06:00 with the last finished batch's tests, and add new ones when they land."),
        ans=3,
        explain=("The batch suits work that nobody waits on, and the change turned it into a gate. Taking the gate away restores "
                 "that. A speeds up noticing the end, not the end itself. B does not change the 24-hour limit or promise "
                 "that smaller batches finish sooner. C needs about nine hours, so it cannot finish before 06:00."),
        scenarios=(5,), points=("4.5:K2",),
        evidence=(Evidence(_API, "The system processes each batch as fast as possible, with most batches completing within 1 hour."),
                  Evidence(_API, "This approach is well-suited to tasks that do not require immediate responses")),
        qtype="fix", level="hard", principle="fit_for_purpose",
        situation="release build made to wait for the nightly test batch and starting a day late",
        trap="poll more often or split into more batches",
    ),
    # ---- K3: no tool round trip inside a batch request ----
    MCQ(
        id="Q4.5-07",
        q=("An extraction pipeline has Claude call a `lookup_vendor` tool to fill an `approved` field for each of 30,000 invoices. "
           "To save cost, the team ran a pilot of 200 as a Message Batch with the tool defined in every request. All 200 results "
           "are succeeded, but each has stop_reason \"tool_use\" and no `approved` value. What is the most likely root cause?"),
        opts=("Batch requests cannot carry tool definitions at all, so the call was malformed from the start.",
              "The `lookup_vendor` schema lacks a required field, so Claude cannot finish the call it began.",
              "No step inside a batch request runs the tool and returns its result for Claude to continue.",
              "The custom_id values were not attached to the tool calls, so the results were never matched."),
        ans=2,
        explain=("A request in a batch is processed on its own, so a client-side tool call cannot be executed and answered inside it. The "
                 "result ends at the tool request, which is why the field is empty. A is false, since the tool definition was "
                 "accepted. B would give a schema problem, not a clean tool_use result. D confuses matching results with running tools."),
        scenarios=(6,), points=("4.5:K3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the docs allow tool definitions in a batch request, while the guide excludes the mid-request round trip (running the tool and returning the result).",
        qtype="diagnose", level="medium", principle="root_cause",
        situation="batched invoice extraction ends every result at a tool_use request",
        trap="blame the tool definition or the schema",
    ),
    MCQ(
        id="Q4.5-08",
        q=("A nightly job must produce 6,000 unit tests. For each, Claude writes the test, a `run_tests` tool executes it, and when "
           "it fails Claude reads the output and revises the test before it is accepted. Nobody looks at the result until "
           "morning. Which design fits?"),
        opts=("Run the loop on the synchronous API overnight, with your code executing `run_tests` between turns.",
              "Submit the loop as a Message Batch with `run_tests` defined, so that Claude runs it between its own turns.",
              "Submit a Message Batch and tell Claude to mentally run each test and fix it before it answers.",
              "Submit a Message Batch with extended thinking on, so that Claude checks every test before it answers."),
        ans=0,
        explain=("The loop needs a tool executed and its output returned to the model, which a batch request cannot do for a client-side tool, so the loop"
                 "belongs on the synchronous API even if it runs overnight. B expects the batch to run the tool. C and D ask the "
                 "model to imagine a result that only a real test run can give."),
        scenarios=(5,), points=("4.5:K3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the docs allow tool definitions in a batch request, while the guide excludes the mid-request round trip (running the tool and returning the result).",
        qtype="choose", level="medium", principle="fit_for_purpose",
        situation="overnight write, run and revise loop for generated tests",
        trap="ask the model to imagine the test result",
    ),
    MCQ(
        id="Q4.5-09",
        q=("Three nightly CI jobs are candidates for the Message Batches API: (1) labelling 50,000 failure logs, with each log's "
           "text supplied in its prompt, (2) an agent that investigates each failing test by calling `git_blame` and `read_file` "
           "and following what they return, and (3) summarising each day's commit messages, also supplied in the prompt. "
           "Which jobs can be submitted as batches without redesign?"),
        opts=("Jobs 1, 2 and 3, as the API runs the tool calls inside a batch.",
              "Jobs 1 and 3, whose requests are answered in a single turn.",
              "Job 2 only, as it does the most work per request and so saves the most.",
              "Job 1 only, as it has by far the most requests."),
        ans=1,
        explain=("Requests answered in one turn from supplied text fit a batch. Job 2 depends on tool results coming back to the "
                 "model mid-request, which a batch cannot do. A is false: the API does not run client-side tools such as git_blame and read_file inside a batch."
                 "C picks the one job that cannot work. D leaves out job 3, which has the same shape as job 1."),
        scenarios=(5,), points=("4.5:K3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the docs allow tool definitions in a batch request, while the guide excludes the mid-request round trip (running the tool and returning the result).",
        qtype="choose", level="easy", principle="fit_for_purpose",
        situation="three nightly CI jobs, one of which investigates failures through tool calls",
        trap="treat tool definitions as proof that tools can run in a batch",
    ),
    # ---- K4: custom_id ----
    MCQ(
        id="Q4.5-10",
        q=("A team submits 9,000 contract extractions as one batch, using each file's storage path as its custom_id. Six hours "
           "later the batch ends: 2,200 results are errored with an invalid request message, and 6,800 succeeded. The failures "
           "include `legal/2024/Acme Corp v2.pdf`, while the successes include `legal-2024-acme_v1`. What is the most likely "
           "root cause?"),
        opts=("The failed documents exceed the context limit, so the service rejected their requests.",
              "Requests with long paths exceed a size limit that applies to the batch as a whole.",
              "Claude declined to read contracts from that folder, so the service marked them as errors.",
              "Those ids hold characters that the field does not allow."),
        ans=3,
        explain=("The id field accepts only letters, digits, hyphens and underscores, up to 64 characters, and the failed ids break "
                 "that rule while the successful ones keep it. A would affect documents by length, not by how their ids are "
                 "written. B invents a size rule tied to path length. C describes a refusal, which would not be reported as an "
                 "invalid request."),
        scenarios=(6,), points=("4.5:K4",),
        evidence=(Evidence(_API, "Must be 1 to 64 characters and contain only alphanumeric characters, hyphens, and underscores"),),
        basis="docs",
        qtype="diagnose", level="medium", principle="root_cause",
        situation="file paths with slashes and spaces used as custom_id fail after the batch ends",
        trap="blame document size or refusals",
    ),
    MCQ(
        id="Q4.5-11",
        q=("A CI team runs per-file review requests as a Message Batch of 3,000. Their client code pairs the i-th result line with "
           "the i-th request in its list and sets no custom_id. Across 20 test batches the pairing came out right every time, so a "
           "reviewer asks you to approve the code for production. How should you evaluate it?"),
        opts=("Approve it: 20 matching batches are strong evidence that the order will hold in production.",
              "Approve it, with a count check that rejects any batch whose result total differs from its request total.",
              "Reject it: results can come back in any order, so each request needs an id and matching should use it.",
              "Reject it, and sort the results by completion time before pairing so that the order is restored."),
        ans=2,
        explain=("The documentation says results can arrive in any order and may not match the submission order, so matching has to "
                 "use the id carried by each request. A reads a small sample as a guarantee. B checks the count, which stays right "
                 "when the results are paired wrongly. D swaps one unreliable order for another."),
        scenarios=(5,), points=("4.5:K4",),
        evidence=(Evidence(_API, "Batch results can be returned in any order, and may not match the ordering of requests when the batch was created."),),
        qtype="evaluate", level="medium", principle="explicit",
        situation="positional pairing of batch results validated on 20 test batches",
        trap="trust an order that happened to hold in testing",
    ),
    MCQ(
        id="Q4.5-12",
        q=("Contracts are re-uploaded with corrections while their extraction is still waiting in a batch. Each document keeps its "
           "ID and gains a revision number on every upload. Last week a result for revision 3 arrived after revision 4 had been "
           "stored, and it overwrote the newer fields in 41 records. A separate loader writes results and sees only the result "
           "lines. How should the requests be identified to prevent this?"),
        opts=("Build each custom_id from document ID and revision, and have the loader skip stale results.",
              "Keep the latest-finished result for each document ID, because the newest result is the best.",
              "Cancel every pending batch whenever a document is re-uploaded, and resubmit the whole set.",
              "Ask Claude to repeat the revision number in each extraction, and have the loader compare it."),
        ans=0,
        explain=("The id travels with the request and comes back with its result, so putting the revision in it lets the loader "
                 "decide without extra lookups. B uses finishing order, which is exactly what failed. C throws away the work of "
                 "every other document. D leans on generated text for something the id field exists to carry."),
        scenarios=(6,), points=("4.5:K4",),
        evidence=(Evidence(_API, "To correctly match results with their corresponding requests, always use the `custom_id` field."),),
        qtype="configure", level="hard", principle="deterministic",
        situation="stale revision results overwrite newer extractions",
        trap="let the latest finish time decide",
    ),
    # ---- S1: match the approach to the latency requirement ----
    MCQ(
        id="Q4.5-13",
        q=("One code-review prompt serves two triggers: a pull request being opened, where merging is blocked until the review "
           "posts, and a weekly sweep of 2,000 older files. Merges happen at any hour across three time zones. Cost is up, and the "
           "team wants the Message Batches API wherever it fits. Which design is best?"),
        opts=("Send all reviews as batches, and show the pull request check as pending until its result arrives.",
              "Send pull request reviews synchronously and the weekly sweep as a batch.",
              "Send reviews synchronously by day and as batches by night, as nobody is waiting overnight.",
              "Send every review synchronously, and cut cost by shortening the prompt."),
        ans=1,
        explain=("The trigger decides whether someone is blocked, so it decides the API. A makes merges wait for an open-ended "
                 "result. C assumes nobody waits at night, but merges happen at any hour. D gives up the saving on work that can wait."),
        scenarios=(5,), points=("4.5:S1",),
        evidence=(Evidence(_API, "This approach is well-suited to tasks that do not require immediate responses"),),
        qtype="choose", level="easy", principle="fit_for_purpose",
        situation="one review prompt used by a blocking PR trigger and a weekly sweep",
        trap="route by time of day",
    ),
    MCQ(
        id="Q4.5-14",
        q=("A nightly job extracts fields from about 15,000 partner documents received during the day and loads them into a "
           "warehouse that analysts query the next afternoon, and they accept data a day old. It runs as 15,000 synchronous calls with retries, and its spend is the team's "
           "largest line. Nobody looks at individual results before the load, and a delay of a day is acceptable. What is the most effective change?"),
        opts=("Run more calls in parallel so that the job ends earlier and fewer retries are needed overall.",
              "Move the job to a smaller model, since the documents are fairly simple to read.",
              "Add a check after each call and retry the failed documents one by one.",
              "Submit them as a Message Batch, since no one needs a single result before morning."),
        ans=3,
        explain=("The job is latency-tolerant and fully synchronous, so batching halves its cost without anyone noticing. A "
                 "finishes sooner, which nobody asked for. B changes the model without an evidence that quality would hold. C adds "
                 "more calls to a job that is already paid for at full price."),
        scenarios=(6,), points=("4.5:S1",),
        evidence=(Evidence(_API, "This approach is well-suited to tasks that do not require immediate responses"),),
        qtype="fix", level="easy", principle="proportionate",
        situation="nightly warehouse load running as synchronous calls",
        trap="speed up a job nobody is waiting on",
    ),
    MCQ(
        id="Q4.5-15",
        q=("A `/review-all` command lets a developer ask Claude to review all 6,000 files of a service before opening a pull "
           "request. Developers abandon the command after about ten minutes of waiting, and these reviews are most of the team's "
           "Claude spend. A teammate says the volume makes it a natural fit for the Message Batches API. What is the best response?"),
        opts=("Agree, and email each developer the results when the batch ends.",
              "Agree, and cut the work into 60 batches of 100 files so that each ends sooner.",
              "Keep it synchronous, with reviews in parallel, since a person is waiting.",
              "Agree, and add a progress bar that polls the batch until its results arrive."),
        ans=2,
        explain=("What matters is whether someone is waiting, not how large the job is. These developers expect output inside "
                 "minutes, which a batch cannot promise. A and D accept an open wait that has already led to abandoned runs. B does "
                 "not shorten the 24-hour limit."),
        scenarios=(5,), points=("4.5:S1",),
        evidence=(Evidence(_API, "This approach is well-suited to tasks that do not require immediate responses"),),
        qtype="evaluate", level="medium", principle="fit_for_purpose",
        situation="large on-demand repo review that developers wait on",
        trap="choose batch because the volume is large",
    ),
    # ---- S2: submission frequency from the SLA ----
    MCQ(
        id="Q4.5-16",
        q=("Partner documents arrive around the clock, and each must have its extracted fields available within 54 hours of "
           "arrival. Processing a Message Batch can take up to 24 hours. The pipeline submits a batch every hour, producing "
           "hundreds of small batches, and the team wants to submit as rarely as the deadline allows. Which schedule is the "
           "least frequent that still guarantees the deadline?"),
        opts=("Every 24 hours.",
              "Every 12 hours, twice a day.",
              "Every 36 hours, a day and a half.",
              "Every 48 hours, every other day."),
        ans=0,
        explain=("The worst case is the wait for the next submission plus up to 24 hours of processing. Every 24 hours gives 48 "
                 "hours, inside 54. B also meets the deadline but submits more often than needed. C gives 60 hours and D gives 72, "
                 "both past 54."),
        scenarios=(6,), points=("4.5:S2",),
        evidence=(Evidence(_API, "Batches expire if processing does not complete within 24 hours."),),
        qtype="choose", level="easy", principle="proportionate",
        situation="54-hour extraction deadline and the least frequent batch schedule that meets it",
        trap="pick the next interval up without adding the processing time",
    ),
    MCQ(
        id="Q4.5-17",
        q=("A pipeline sends each merged change's test suggestions through a Message Batch submitted once a day at 02:00. The "
           "promise to developers is suggestions within 40 hours of the merge. A month of data shows 11% of changes missed it, "
           "nearly all merged within a few hours after 02:00 on days when the batch ran for most of its window. Splitting the daily "
           "batch into ten smaller ones submitted together did not help. Which change fixes the schedule?"),
        opts=("Keep submitting once a day, but move the submission to 14:00 when fewer merges are waiting.",
              "Submit every 12 hours, and treat the 24-hour limit as the processing time.",
              "Submit every 36 hours, so that each batch is larger and slow days become rare.",
              "Keep the daily batch, and request faster processing for changes merged just after 02:00."),
        ans=1,
        explain=("A change merged just after a submission waits almost a full interval, then up to 24 hours more. With a daily "
                 "schedule that is nearly 48 hours, past 40, and a 12-hour interval brings it to 36. A moves the cutoff without "
                 "shortening the interval. C lengthens the interval and so the wait. D relies on a priority option that the API "
                 "does not offer."),
        scenarios=(5,), points=("4.5:S2",),
        evidence=(Evidence(_API, "Batches expire if processing does not complete within 24 hours."),),
        qtype="fix", level="hard", principle="root_cause",
        situation="daily 02:00 batch misses a 40-hour promise for changes merged just after the cutoff",
        trap="move the cutoff time or split the batch",
    ),
    MCQ(
        id="Q4.5-18",
        q=("A service promises extracted fields within 26 hours of a document's arrival. An engineer plans one batch every 24 "
           "hours, arguing that batches usually finish in under an hour, so the worst case is 24 hours of waiting plus about one "
           "hour, which is 25. How should you evaluate the plan?"),
        opts=("Accept it: its worst case of 25 hours sits comfortably inside the 26-hour promise made.",
              "Accept it, and resubmit anything that expires in the next day's batch of requests.",
              "Reject it: budget 24 hours for processing, so submit every 2 hours or sooner.",
              "Reject it: with 24 hours budgeted for processing, submitting every 12 hours is enough."),
        ans=2,
        explain=("A guarantee has to use the upper bound of 24 hours for processing, not the usual time. That leaves 2 hours of "
                 "waiting inside a 26-hour promise. A uses the typical hour. B resubmits expired work into a batch that is "
                 "another day away. D budgets 24 hours correctly, but 12 plus 24 is 36, past 26."),
        scenarios=(6,), points=("4.5:S2",),
        evidence=(Evidence(_API, "Batches expire if processing does not complete within 24 hours."),),
        qtype="evaluate", level="hard", principle="root_cause",
        situation="26-hour promise planned from the typical one-hour batch",
        trap="budget the typical time instead of the 24-hour limit",
    ),
    # ---- S3: resubmit only failures, with the right modification ----
    MCQ(
        id="Q4.5-19",
        q=("In a nightly batch of 1,800 per-file reviews, 35 requests errored because their source files exceed the context "
           "limit. The fix is to split each of those files into four parts, review each part as its own request, and merge "
           "the findings per file. How should the resubmitted requests be identified?"),
        opts=("Reuse the original custom_id on all four parts, since the findings belong to that file.",
              "Give the parts new random ids, and keep the mapping in memory until the batch ends.",
              "Number the parts 1 to 140 in order, and pair them with files by position.",
              "Build each id from the original plus the part number, so results map to file and part."),
        ans=3,
        explain=("An id that carries the file and the part lets the results be merged per file and traced to what was resubmitted. "
                 "A is wrong because each custom_id must be unique, so four requests with one id are not allowed. B loses the link if the process "
                 "restarts. C pairs by position, and results do not come back in submission order."),
        scenarios=(5,), points=("4.5:S3", "4.5:K4"),
        evidence=(Evidence(_API, "A unique custom_id for identifying the Messages request."),),
        qtype="configure", level="medium", principle="preserve_information",
        situation="oversized files split into four parts and resubmitted",
        trap="reuse one id for all parts",
    ),
    MCQ(
        id="Q4.5-20",
        q=("A 20,000-document extraction batch ends with 19,500 succeeded, 400 expired, 80 errored with internal server errors, and "
           "20 errored because the documents exceed the context limit; all 20 are scans of more than 300 pages. What is the most efficient recovery?"),
        opts=("Resubmit the 480 expired and server-error ids as is, and chunk the 20 scans.",
              "Resubmit all 500 ids unchanged, and repeat until the error count reaches zero.",
              "Resubmit the 20,000 documents in a new batch, so one set of results covers everything.",
              "Run the 500 ids on the synchronous API, which returns faster than a second batch."),
        ans=0,
        explain=("Expired and server-error requests did not fail because of their input, so they can go again as they are, while the "
                 "oversized scans fail the same way until they are changed. B resubmits the 20 scans unchanged, and they fail again. "
                 "C repeats 19,500 successes. D gives up the saving and still sends the 20 scans unchanged."),
        scenarios=(6,), points=("4.5:S3",),
        evidence=(Evidence(_API, "Possible errors include invalid requests and internal server errors."),
                  Evidence(_API, "Batch reached its 24-hour expiration before this request could be sent to the model.")),
        basis="docs",
        qtype="fix", level="hard", principle="proportionate",
        situation="batch ends with expired, server-error and invalid-request results together",
        trap="resubmit every failure unchanged",
    ),
    MCQ(
        id="Q4.5-21",
        q=("An extraction service receives about 20,000 documents a day. Roughly 5% are flagged urgent and a clerk needs their "
           "fields within a few minutes; the rest are read by analysts the following afternoon. Spend is high and everything now "
           "runs synchronously. Which routing is best?"),
        opts=("Send everything as a batch, and place the urgent documents first within each batch.",
              "Send urgent documents as small batches submitted every minute, and the rest as one daily batch.",
              "Keep everything synchronous, and batch only the documents that arrive overnight.",
              "Send urgent documents synchronously and the rest as a Message Batch."),
        ans=3,
        explain=("The flag marks who is waiting: urgent documents need an answer in minutes, which a batch cannot promise, while "
                 "the rest tolerate a day. A assumes order inside a batch changes when results come back, and there is no such "
                 "guarantee. B submits often, but each small batch can still take up to 24 hours. C batches by arrival time, "
                 "which says nothing about who is waiting."),
        scenarios=(6,), points=("4.5:S1",),
        evidence=(Evidence(_API, "This approach is well-suited to tasks that do not require immediate responses"),),
        qtype="choose", level="medium", principle="fit_for_purpose",
        situation="5% urgent documents and a day-tolerant remainder",
        trap="order the urgent ones first inside a batch",
    ),
    # ---- S4: refine on a sample first ----
    MCQ(
        id="Q4.5-22",
        q=("Before a 60,000-form extraction batch, the team tuned the prompt on 25 clean, typed forms until it got 100% valid "
           "output. The batch finished with 71% of results usable, and the failures cluster on faxed, rotated and handwritten "
           "forms, which are 30% of the volume. Which earlier step would have been most effective?"),
        opts=("Tuning on a sample with faxed, rotated and handwritten forms in real proportions.",
              "Tuning on many more clean typed forms, since a larger sample gives a more reliable success rate.",
              "Submitting the full batch first, and fixing the prompt from whichever results come back wrong.",
              "Tuning only on the faxed forms, since those are the hardest to read."),
        ans=0,
        explain=("A sample only predicts first-pass success if it looks like the volume, including the hard cases. B adds more of "
                 "the easy case. C turns the whole run into the test, and every wrong result is a resubmission. D tunes on one "
                 "slice and may break the typed forms that already worked."),
        scenarios=(6,), points=("4.5:S4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: refining on a sample set before a large batch is named in TS 4.5 Skill 4; no official page addresses how to choose the sample.",
        qtype="diagnose", level="medium", principle="root_cause",
        situation="prompt tuned on 25 clean forms fails on faxed and handwritten ones in a 60,000 batch",
        trap="enlarge the sample without making it representative",
    ),
    MCQ(
        id="Q4.5-23",
        q=("A team is tuning the prompt for a 3,000-request test-generation batch. Each round submits the whole batch, waits "
           "about five hours for the results, and then edits the prompt; after five rounds the prompt is still changing. How "
           "should the tuning be done instead?"),
        opts=("Submit several prompt variants as separate full batches in the same round, and compare them.",
              "Poll the batch status more often, so that each round starts as soon as the results land.",
              "Iterate on a sample with synchronous calls, then submit the full batch once.",
              "Cut each round to a batch of 300 requests, so that every round finishes much sooner."),
        ans=2,
        explain=("A sample run through the synchronous API returns in seconds, so many prompt edits fit in an afternoon and the large "
                 "batch is submitted once. A multiplies the work by the number of variants. B saves minutes from a five-hour wait. "
                 "D keeps the wait, since a smaller batch carries no latency guarantee either."),
        scenarios=(5,), points=("4.5:S4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 4.5 Skill 4 names refining on a sample to cut resubmission cost; no official page addresses tuning rounds.",
        qtype="fix", level="easy", principle="proportionate",
        situation="five full-batch tuning rounds of five hours each",
        trap="shrink the batch instead of using synchronous calls",
    ),
    MCQ(
        id="Q4.5-24",
        q=("A team tuned its prompt on 120 invoices drawn from one supplier until all outputs were valid against the schema, then "
           "ran 40,000 invoices from 300 suppliers as one batch. Spot checks found the invoice total in the wrong field in 14% "
           "of records, mostly on layouts the sample never contained. How should the prompt have been refined before the batch?"),
        opts=("On more invoices from the same supplier, until two rounds in a row look clean.",
              "On a sample spanning the layouts, scored against hand-checked values for each field.",
              "On the first 5,000 invoices submitted as a batch, using the errors to adjust the prompt.",
              "On the same 120 invoices, run twice, keeping the prompt if both runs give identical output."),
        ans=1,
        explain=("Refinement raises first-pass success only if the sample resembles the volume and is scored on correct values. A "
                 "and D keep the single-supplier sample, so unseen layouts stay unseen, and D measures steadiness, not accuracy. C "
                 "makes a large batch the test, with hours of waiting per round."),
        scenarios=(6,), points=("4.5:S4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 4.5 Skill 4 names refining on a sample set to raise first-pass success; the choice of sample is a judgment no official page states.",
        qtype="evaluate", level="medium", principle="independent_check",
        situation="prompt tuned on one supplier's invoices fails on other layouts in a 40,000 batch",
        trap="tune longer on an unrepresentative sample",
    ),
)
