"""Exam bank · TS 2.2. Original questions; see docs/MCQ_BANK_PLAN.md.

The field names errorCategory, isRetryable and the "business" category are the exam guide's convention; no official page defines them
(MCP itself defines only the isError flag)."""
from utils.mcq_sets import MCQ, Evidence

TS = "2.2"
BULLETS = {
    "K1": "The MCP isError flag is how a tool tells the agent that a call failed",
    "K2": "Transient, validation, business and permission errors are different kinds that call for different responses",
    "K3": "A uniform 'Operation failed' response leaves the agent unable to choose a recovery",
    "K4": "Retryable and non-retryable errors differ, and structured metadata prevents wasted retries",
    "S1": "Return errorCategory, isRetryable and a human-readable description",
    "S2": "For business-rule violations return isRetryable: false and a customer-friendly explanation",
    "S3": "Recover from transient failures inside the subagent; pass up only unresolved errors with partial results and attempts",
    "S4": "Tell an access failure (a retry decision) apart from a valid empty result (a successful query)",
}

_SPEC = "mcp:specification/2026-07-28/server/tools"
_HANDLE = "api:agents-and-tools/tool-use/handle-tool-calls"

QUESTIONS = (
    # ---- K1: the isError pattern ----
    MCQ(
        id="Q2.2-01",
        q=("A research platform's usage report counts failed tool calls by scanning each result's text for the word \"error\". "
           "One archive server answers in German with \"Zugriff verweigert\" when it refuses a request. The dashboard shows "
           "99% of calls succeeding, yet 22% of the failed calls were never counted, and several reports have gaps. "
           "What is the most effective fix?"),
        opts=("Add the German phrases, and those of the other archives, to the keyword list the report scans for.",
              "Ask each subagent to end its summary with the line FAILED whenever a tool call did not work.",
              "Count calls by the `isError` flag in each tool result, and have every server set it on a failure.",
              "Run a small model over every tool result to label it as a success or a failure."),
        ans=2,
        explain=("The flag is the agreed signal for a failed call, so counting it needs no reading of text in any language. "
                 "A chases wording one language at a time and will miss the next phrasing. B relies on a model remembering to "
                 "add a line, which is the kind of probabilistic step the report is trying to avoid. D adds a model call per "
                 "result to recover what the server could state outright."),
        scenarios=(3,), points=("2.2:K1",),
        evidence=(Evidence(_SPEC, "They are reported in tool results with `isError: true`:"),),
        qtype="fix", level="easy", principle="deterministic",
        situation="failure counter scans result text for the word error and misses German refusals",
        trap="extend the keyword list instead of reading the flag",
    ),
    MCQ(
        id="Q2.2-02",
        q=("A coordinator's harness ends a research run as soon as any MCP tool result carries `isError: true`, on the view that "
           "a flagged call cannot be recovered. 14% of runs now end this way. In a replay of 10 sampled runs, nine of the "
           "failed tools had said which argument was out of range, and a corrected call would have worked. How should you "
           "evaluate the harness rule?"),
        opts=("It discards what the flag is for: the model should see the error text, adjust and retry.",
              "It is sound, because a flagged result means the run is unsafe to continue, so keep it and restart the run.",
              "It is sound for tools the team owns, and should be relaxed only for tools from third-party servers.",
              "It needs a threshold, so that the run ends after three flagged results in a row instead of the first one."),
        ans=0,
        explain=("The flag reports that the call failed and the text says why, which lets the model correct itself; ending "
                 "the run throws that away. B treats a failed call as a failed run. C separates tools by owner, but the cause "
                 "of the failure and not its owner decides whether a retry can work. D still ends runs that a single corrected "
                 "call would have saved."),
        scenarios=(3,), points=("2.2:K1",),
        evidence=(Evidence(_SPEC, "Clients **SHOULD** provide tool execution errors to language models to enable self-correction."),),
        qtype="evaluate", level="medium", principle="model_driven",
        situation="harness ends the whole research run on any flagged tool result",
        trap="treat a flagged tool failure as a fatal run failure",
    ),
    MCQ(
        id="Q2.2-03",
        q=("A developer assistant has an in-process `query_metrics` tool whose handler lets exceptions escape. When the metrics "
           "service throttles it, Claude reads the raw message `HTTPStatusError: Client error '429 Too Many Requests' for "
           "url ...` and tells developers that \"the metrics service is broken\" in 25% of such cases, although the throttle "
           "clears in 30 seconds. What change fits best?"),
        opts=("Add a prompt rule that explains how to read raw HTTP exception messages from the tools.",
              "Catch the error and return empty content, so that the assistant moves on to its next task.",
              "Raise the handler's timeout so that fewer calls reach the point of failing in the first place.",
              "Catch it in the handler and return `isError: true` with the cause and the wait."),
        ans=3,
        explain=("An uncaught exception still reaches Claude as an error, but with the raw message; catching it lets the handler "
                 "write what failed and what to do next. A asks the model to decode internals that the tool could simply state. "
                 "B hides the failure and so invites a wrong conclusion. C targets timeouts, while this failure is a throttle."),
        scenarios=(4,), points=("2.2:K1",),
        evidence=(Evidence("code:agent-sdk/custom-tools", "Claude sees the message you compose. You can add context the raw exception lacks, such as which request failed or what to try instead."),),
        basis="docs",
        qtype="fix", level="medium", principle="explicit",
        situation="raw 429 exception text read as the metrics service being broken",
        trap="teach the model to decode raw exception text",
    ),
    # ---- K2: the kinds of error ----
    MCQ(
        id="Q2.2-04",
        q=("A subscription server labels a failure \"transient\" for any 5xx status and \"validation\" for any other 4xx. A "
           "customer asks to downgrade in month four of a 12-month contract, the backend answers 409 \"contract term active\", "
           "and the tool reports a validation error. The agent asks the customer to re-enter the plan code up to three times, "
           "in about 38 conversations a week. What is the most effective change?"),
        opts=("Report 409 as transient, so that the agent waits and tries again once the backend is ready.",
              "Add a \"business\" category for contract and policy refusals, set by cause.",
              "Tell the agent in its prompt to stop after two validation errors in a row and apologise.",
              "Return the backend's 409 text as the whole error and drop the category from the response."),
        ans=1,
        explain=("A refusal under a contract is a business error, which neither a retry nor a corrected plan code can change, so it "
                 "needs its own kind, decided by what went wrong rather than by status code. A mislabels it and invites waiting for "
                 "something that will not happen. C caps the repeats but still tells the customer nothing true. D removes the "
                 "category that lets the agent choose a response."),
        scenarios=(1,), points=("2.2:K2",),
        evidence=(Evidence(_SPEC, "Business logic errors"),),
        qtype="fix", level="medium", principle="root_cause",
        situation="contract-term refusal reported as a validation error because it is a 4xx",
        trap="keep the status-code mapping and cap repeats in the prompt",
    ),
    MCQ(
        id="Q2.2-05",
        q=("An engineer proposes that your assistant's tools report failures with only `isRetryable`, calling categories \"overkill "
           "since the agent just needs retry or not\". A week of logs holds 500 failures: 180 timeouts, 140 calls with bad "
           "arguments, 90 refusals for missing access and 90 breaches of a business rule. A routing script sends missing-access "
           "failures to an access-request queue. How should you evaluate the proposal?"),
        opts=("Adopt it, because a yes or no flag covers every case and fewer fields leave fewer places for a tool to be wrong.",
              "Adopt it, and describe the kind of failure in the message text so the model can read it there.",
              "Keep the category: the 320 non-retryable failures need different responses, and the script reads it.",
              "Reject it, but only to add a retry-after field for timeouts and leave the other failures with the flag."),
        ans=2,
        explain=("Not retrying is one outcome, but the next step differs: fix the arguments, request access, or explain the rule. "
                 "A flag cannot say which, and the script cannot read prose reliably. A treats one bit as enough for four kinds of "
                 "failure. B leaves the kind in text that code cannot route on. D improves timeouts only and keeps the other "
                 "three kinds indistinct."),
        scenarios=(4,), points=("2.2:K2",),
        evidence=(Evidence(_SPEC, "Input validation errors (e.g., date in wrong format, value out of range)"),
                  Evidence(_SPEC, "Business logic errors"), Evidence(_SPEC, "API failures")),
        qtype="evaluate", level="medium", principle="preserve_information",
        situation="proposal to drop error categories in favour of a single retry flag",
        trap="collapse four kinds of failure into retry or not",
    ),
    MCQ(
        id="Q2.2-06",
        q=("The developer assistant's `get_payroll_report` tool returns an error with category \"permission\" and "
           "`isRetryable: false`, because its service account has no payroll scope. A developer asked for the report to plan a "
           "team budget. The analytics export tool, which the assistant can call, is not meant to expose payroll data. Which behaviour should the assistant show?"),
        opts=("Stop trying to read that report, tell the developer which access is missing, and let them request it.",
              "Retry after a pause, in case the permission change that was approved earlier has not yet taken effect.",
              "Retry with a narrower date range, since smaller requests sometimes pass the access check.",
              "Read the same figures through the analytics export tool, which the assistant is able to call."),
        ans=0,
        explain=("A permission failure needs someone with authority to grant access, so the assistant should report it and stop "
                 "at that resource. B retries what the flag says cannot succeed. C changes the arguments, which do not decide "
                 "access. D gets around the control through another route to the same data."),
        scenarios=(4,), points=("2.2:K2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 2.2 Knowledge 2 names permission errors as a kind; what an agent should do about one is a design judgment.",
        qtype="choose", level="easy", principle="least_privilege",
        situation="payroll report refused for missing scope and the agent looks for another route",
        trap="route around the permission error through another tool",
    ),
    # ---- K3: uniform responses ----
    MCQ(
        id="Q2.2-07",
        q=("An `exchange_item` tool returns \"Request could not be completed\" for every failure. In 300 reviewed chats the agent "
           "apologised and offered a phone number, and in 55% of them the server log reads \"size M out of stock; size L "
           "available\". The customers had not asked for the phone line. What is the most likely root cause?"),
        opts=("The agent is too ready to give up, and its prompt should tell it to try other sizes.",
              "The response carries no cause, so the agent cannot tell a stock gap from a fault.",
              "The failures are temporary, and the agent should retry the exchange before it apologises.",
              "The agent has too many tools, so it picks the wrong exchange route and cannot complete it."),
        ans=1,
        explain=("The cause is in the log and not in the response, so the agent has nothing to act on. A asks for initiative with "
                 "no information to use it on. C assumes a temporary fault, but the log shows a stock position that a retry "
                 "will not change. D blames tool choice, when the tool that ran was the right one."),
        scenarios=(1,), points=("2.2:K3",),
        evidence=(Evidence(_HANDLE, "Write instructive error messages."),),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="size-out-of-stock cause stays in the server log while the agent offers the phone line",
        trap="tell the agent in the prompt to try harder",
    ),
    MCQ(
        id="Q2.2-08",
        q=("A `charge_saved_card` tool returns \"Operation failed\" for declines, expired cards and gateway outages alike. In 11 of "
           "80 reviewed chats the agent told the customer \"your card was declined\" while the gateway log shows an outage "
           "at that moment, and several customers then cancelled their orders. Which change is most effective?"),
        opts=("Add a prompt rule that forbids the agent to name a reason for a failure.",
              "Switch to a larger model, which gives fewer unsupported explanations when a tool says little.",
              "Retry the charge once inside the agent loop before the customer is told anything.",
              "Return a category and a plain description of the cause, so the agent can report it."),
        ans=3,
        explain=("A tool that gives no cause leaves the model to fill the gap with a guess, and the fix is to supply the cause. A would "
                 "stop the guess but leave the agent unable to say anything useful. B treats the symptom with a bigger model "
                 "and still gives it no facts. C retries a decline that cannot succeed and does nothing for the wrong message."),
        scenarios=(1,), points=("2.2:K3",),
        evidence=(Evidence(_HANDLE, "This gives Claude the context it needs to recover or adapt without guessing."),),
        qtype="fix", level="medium", principle="preserve_information",
        situation="agent invents a card decline when the gateway was down",
        trap="forbid the agent to name a cause instead of supplying one",
    ),
    MCQ(
        id="Q2.2-09",
        q=("A platform team returns the same \"Internal error\" for every tool failure, \"so we never leak internals\", and the "
           "developer assistant on top of the tools retries blindly and wastes minutes. Security's real concern is hostnames "
           "and stack traces reaching the model. How should you evaluate the design?"),
        opts=("Keep it: any extra detail in an error is a leak, so one fixed message is the safe design.",
              "Keep the message, and let the assistant read the server logs to learn what went wrong.",
              "Return a category, a retry flag and a description; keep traces and hostnames in server logs.",
              "Return the full exception with its stack trace, since the assistant runs inside the company network."),
        ans=2,
        explain=("The concern is leaking internals, not giving the agent a cause, and a short description can carry the cause without "
                 "any hostname or trace. A gives up recovery to avoid a risk that has a narrower answer. B opens more of the "
                 "internals than the description would. D sends exactly what security wanted kept out."),
        scenarios=(4,), points=("2.2:K3",),
        evidence=(Evidence(_HANDLE, "This gives Claude the context it needs to recover or adapt without guessing."),),
        qtype="evaluate", level="medium", principle="fit_for_purpose",
        situation="one Internal error message for all failures to avoid leaking hostnames",
        trap="trade the agent's recovery for a risk that a safe description removes",
    ),
    # ---- K4: retryable vs non-retryable ----
    MCQ(
        id="Q2.2-10",
        q=("A `run_linter` server returns `isRetryable: true` on every error. The harness retries a flagged call up to three times "
           "with a 5-second pause. Of 400 failing calls in a week, 310 were \"file not found\" for a path the agent had mistyped, "
           "and only 15 retried calls ever succeeded. What is the root cause of the wasted time?"),
        opts=("The server flags every failure as retryable, so the flag tells the harness nothing.",
              "The harness allows three retries per call, which is more than most tool calls need to succeed.",
              "The pause between retries is too short for the linter to recover from its own failures.",
              "The agent has no tool for checking that a path exists before it calls the linter tool."),
        ans=0,
        explain=("The harness is doing what the flag asks, so the flag has to be right: mistyped paths cannot succeed on a retry and "
                 "should be reported as not retryable. B changes the number of wasted attempts without removing them. C assumes "
                 "recovery that cannot happen for a missing file. D adds a prevention step, but the waste comes from retrying."),
        scenarios=(4,), points=("2.2:K4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 2.2 Knowledge 4 (retryable versus non-retryable errors); no official page defines isRetryable.",
        qtype="diagnose", level="medium", principle="root_cause",
        situation="linter server flags every failure retryable, so mistyped paths are retried three times",
        trap="lower the retry count instead of fixing the flag",
    ),
    MCQ(
        id="Q2.2-11",
        q=("A carrier API answers your `track_parcel` tool with HTTP 429 and a `Retry-After` of 30 seconds. Which error should the "
           "tool return to the support agent?"),
        opts=("Category \"business\", `isRetryable: false`, and the message \"Tracking limit applies to this account.\"",
              "Category \"transient\", `isRetryable: true`, and the message \"Carrier is limiting requests; retry after 30 seconds.\"",
              "Category \"transient\", `isRetryable: false`, and the message \"Too many requests; try again later.\"",
              "Category \"permission\", `isRetryable: true`, and the message \"Carrier refused this request; retry after 30 seconds.\""),
        ans=1,
        explain=("A 429 throttle is temporary, the same call will work after the wait, and the description tells the agent how long. "
                 "A calls a temporary throttle a rule about the account and stops the agent. C contradicts itself, since it calls "
                 "the failure transient yet forbids the retry. D files a throttle under access and so points the agent at "
                 "the wrong response."),
        scenarios=(1,), points=("2.2:K4", "2.2:S1"),
        evidence=(Evidence(_HANDLE, "include what went wrong and what Claude should try next"),),
        qtype="configure", level="easy", principle="explicit",
        situation="carrier 429 with a 30-second Retry-After must become a structured error",
        trap="mark a temporary rate limit as not retryable",
    ),
    MCQ(
        id="Q2.2-12",
        q=("A `build_preview` tool returns `isError: true`, category \"validation\" and `isRetryable: false` for an unknown branch "
           "name. The harness log shows the identical call three times, two seconds apart, while the model request log shows a "
           "single assistant turn. What is the root cause?"),
        opts=("The model ignores the structured fields and needs a prompt telling it not to repeat a failed call.",
              "The flag is honoured only when its value is repeated in the description text of the error as well.",
              "The retry logic can act on the error only when it is raised as a JSON-RPC protocol error by the server.",
              "The retry logic around the call treats any flagged result as retryable, whatever `isRetryable` says."),
        ans=3,
        explain=("The repeats happen inside the harness within one model turn, in code that retries whatever is flagged. Metadata helps only "
                 "if the code that retries reads it. A blames the model, but only one assistant turn occurred. B and C "
                 "describe behaviour that the stem gives no sign of."),
        scenarios=(4,), points=("2.2:K4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: a harness has to read the retry metadata for it to prevent wasted attempts; no official page covers this design.",
        qtype="diagnose", level="hard", principle="root_cause",
        situation="generic retry decorator repeats a call that is flagged not retryable",
        trap="blame the model for ignoring the metadata",
    ),
    # ---- S1: category, isRetryable, description ----
    MCQ(
        id="Q2.2-13",
        q=("An `apply_coupon` tool returns an error with category \"validation\", `isRetryable: true` and the description "
           "\"ERR_CPN_114\". In 40 chats the agent told the customer \"the system reported error 114\", and none of them got a "
           "usable next step. Which fix is best?"),
        opts=("Put a table that explains the ERR codes in the system prompt, and keep the code in the description.",
              "Map every ERR code to an HTTP status and return that status as the description.",
              "Replace the code with a plain statement of what is wrong and what to supply.",
              "Set `isRetryable` to false so that the agent stops mentioning the code to the customer."),
        ans=2,
        explain=("A description is written for a reader who has to act on it, and a code that only the server team understands is not "
                 "that. A pushes decoding into a prompt table that drifts from the codes. B swaps one opaque value for "
                 "another. D misreads the flag: it controls retries, not what the agent says."),
        scenarios=(1,), points=("2.2:S1",),
        evidence=(Evidence(_HANDLE, "include what went wrong and what Claude should try next"),),
        qtype="fix", level="medium", principle="explicit",
        situation="coupon error returns only an internal code that the agent repeats to customers",
        trap="decode the internal code through a prompt table",
    ),
    MCQ(
        id="Q2.2-14",
        q=("Four teams own twelve internal MCP tools. Failures that clear on their own are labelled \"temp\", \"transient\", "
           "\"retry_later\" and \"TRANSIENT_ERR\" depending on the team, and the agent retries some and not others. All four teams "
           "can change their servers. What is the best way to fix this?"),
        opts=("Define one shared set of categories and the retry flag in a helper every server imports.",
              "Add a table of the four spellings to the agent's system prompt and say they mean the same thing.",
              "Add a PostToolUse hook that rewrites each spelling into one before the agent reads the result.",
              "Let each team keep its own labels, and publish a style guide that explains how to name them."),
        ans=0,
        explain=("The servers are all owned, so the definition belongs at the source, where one shared list makes a mismatch "
                 "impossible. B depends on a model matching spellings every time. C patches downstream what the owners could "
                 "fix once. D leaves four vocabularies in place and only documents them."),
        scenarios=(4,), points=("2.2:S1",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 2.2 Skill 1 asks for a consistent errorCategory; where to define it is a design judgment.",
        qtype="choose", level="medium", principle="deterministic",
        situation="four teams spell the transient category four ways across twelve tools",
        trap="patch the spellings downstream instead of agreeing one set at the source",
    ),
    MCQ(
        id="Q2.2-15",
        q=("A `search_trials` tool takes six parameters and rejects a bad call with category \"validation\" and the description "
           "\"Invalid argument.\" The agent repeats the same call twice and then drops the registry from its report in 20% of "
           "runs. Which change is most effective?"),
        opts=("Allow the harness three more attempts per call, so the agent has room to find the right arguments.",
              "Say which argument failed, why, and which values are accepted, beside the category and flag.",
              "Return the tool's complete input schema with every validation error and let the model compare.",
              "Make the system prompt list the legal value of each parameter for all of the tools the agent has."),
        ans=1,
        explain=("The description should point to the argument that failed and how to correct it, so the next call can differ from "
                 "the last. A adds attempts of the same failing call. C sends the whole schema when one parameter is "
                 "wrong, which buries the answer. D copies tool details into a prompt that goes stale, and still does not say "
                 "which argument failed."),
        scenarios=(3,), points=("2.2:S1",),
        evidence=(Evidence(_HANDLE, "Write instructive error messages."),),
        qtype="fix", level="medium", principle="explicit",
        situation="Invalid argument gives no hint which of six parameters failed",
        trap="allow more retries of an unchanged call",
    ),
    # ---- S2: business errors ----
    MCQ(
        id="Q2.2-16",
        q=("A `buy_gift_card` tool refuses an order that contains a promotion code and returns \"Declined: rule GC-9\". About 25 "
           "customers a week are told \"your payment was declined\" and re-enter their cards. Which response from the tool is "
           "best?"),
        opts=("The same text with category \"transient\", so the agent suggests trying again later.",
              "A \"transient\" error that says gift cards cannot be bought with a promotion code, so try later.",
              "A success reply stating that no gift card was issued for this order.",
              "A \"business\" error, `isRetryable: false`: no gift cards with a promotion code."),
        ans=3,
        explain=("A rule breach is a business error: the agent should stop retrying and be able to tell the customer the real reason. "
                 "A suggests a wait and gives no reason. B gives the reason but files it as transient, so the agent invites a retry that "
                 "cannot succeed. C reports a refusal as a success, so nothing marks the call as failed."),
        scenarios=(1,), points=("2.2:S2",),
        evidence=(Evidence(_HANDLE, "include what went wrong and what Claude should try next"),),
        qtype="choose", level="easy", principle="fit_for_purpose",
        situation="gift card refused because of a promotion code and customers blamed their cards",
        trap="flag not retryable but give the agent no reason to relay",
    ),
    MCQ(
        id="Q2.2-17",
        q=("A support agent's tools enforce 40 policy rules and fail with \"Blocked: rule R-17, `isRetryable: false`\". The team plans "
           "to keep the customer-facing wording in a system-prompt table keyed by rule number. Policy text changes about once a "
           "month, and the prompt table has already drifted from it twice. How should you evaluate the plan?"),
        opts=("Adopt it: one table in one place is easier to update than 40 strings spread across the tools.",
              "Adopt it, and load the table through a CLAUDE.md file so that every deployment picks it up.",
              "Have each enforcing tool return its own customer wording, so rule and text change together.",
              "Adopt it, and add a nightly test that checks every rule number has a row in the table."),
        ans=2,
        explain=("The explanation belongs with the code that enforces the rule, so an edit to the rule cannot leave stale wording "
                 "behind. A moves the wording away from the rule it describes. B changes where the table is stored and keeps "
                 "the split. D detects a missing row but not a row whose wording has gone out of date."),
        scenarios=(1,), points=("2.2:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 2.2 Skill 2 puts the explanation in the error response; where to keep the wording is a design judgment.",
        qtype="evaluate", level="medium", principle="deterministic",
        situation="rule explanations kept in a prompt table that drifts from monthly policy changes",
        trap="separate the wording from the code that enforces the rule",
    ),
    MCQ(
        id="Q2.2-18",
        q=("Your developer assistant has a `purge_logs` tool, and company policy keeps audit logs for seven years. When asked to "
           "clean up a 3-year-old log set, the tool must refuse. How should the refusal be configured so the assistant handles "
           "it well?"),
        opts=("A \"business\" error with `isRetryable: false`, explaining that logs under retention cannot be purged.",
              "An error with category \"transient\" and `isRetryable: true`, so the assistant tries again at a quieter time.",
              "An error with category \"validation\", so the assistant supplies a different date range and asks again.",
              "A success result that reports 0 logs purged, so the assistant carries on with the rest of its cleanup."),
        ans=0,
        explain=("The refusal is a policy rule, so the assistant must stop and tell the developer why. B turns a rule into a wait. C "
                 "implies the request was malformed, so the assistant would hunt for dates that pass. D reports a refusal "
                 "as a success and hides that the cleanup did not happen."),
        scenarios=(4,), points=("2.2:S2",),
        evidence=(Evidence(_SPEC, "Business logic errors"),),
        qtype="configure", level="easy", principle="explicit",
        situation="purge of audit logs under a seven-year retention rule",
        trap="report the refusal as a success with zero items purged",
    ),
    # ---- S3: local recovery in subagents ----
    MCQ(
        id="Q2.2-19",
        q=("A fetch subagent, which can fetch any URL it is given, reads six PDFs from one mirror, times out on two of them, and tells the coordinator \"2 sources "
           "unavailable\". The coordinator hands the two to a fresh subagent, which tries the same mirror and fails, and the "
           "loop repeats three times in 31% of runs, although the publisher's own site would serve both files. What is the root "
           "cause?"),
        opts=("The coordinator's timeout is too short for the mirror to answer.",
              "The coordinator should resume the original subagent and not create a new one for the retry.",
              "The subagent lacks a web fetch tool and so cannot reach the publisher's site.",
              "The report says what failed but not what was tried, so the same route is repeated."),
        ans=3,
        explain=("The coordinator can choose another route only if it knows which routes have been used, and the report does not tell "
                 "it. A and B change the attempt that repeats and not the information the next attempt lacks. C is ruled out "
                 "because the subagent can fetch any URL it is given."),
        scenarios=(3,), points=("2.2:S3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 2.2 Skill 3 (propagate what was attempted with partial results); no official page covers it.",
        qtype="diagnose", level="hard", principle="preserve_information",
        situation="coordinator retries a mirror because the failure report omits what was attempted",
        trap="blame the coordinator's timeout or its choice of subagent",
    ),
    MCQ(
        id="Q2.2-20",
        q=("One run of a research subagent hit four problems: an archive 503 that cleared on the second attempt, a throttle that "
           "cleared after a 20-second wait, a licensed database that refused access to six papers, and a scanned PDF with no "
           "extractable text for which it has no OCR tool. Which should it send up to the coordinator?"),
        opts=("All four, so that the coordinator has the complete picture of the run.",
              "The refused papers and the scanned PDF, with the results so far and what was tried.",
              "Only the refused papers, because the scanned PDF is a content problem and not an access one.",
              "The 503 and the throttle, because the coordinator owns the timing of any retries."),
        ans=1,
        explain=("The subagent can settle the two transient failures itself, and only what it cannot resolve needs a decision from "
                 "above, together with the partial results and the attempts made. A moves problems that were already solved. "
                 "C keeps back a failure the subagent cannot fix either. D sends up the problems that were resolved and keeps "
                 "back those that were not."),
        scenarios=(3,), points=("2.2:S3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 2.2 Skill 3 (recover locally, propagate only what cannot be resolved); no official page covers it.",
        qtype="choose", level="hard", principle="proportionate",
        situation="two transient failures cleared and two unresolvable ones remain in one subagent run",
        trap="forward everything, including failures already resolved",
    ),
    MCQ(
        id="Q2.2-21",
        q=("A test-running subagent retries a flaky test-database connection with no limit. One run held for 25 minutes on the "
           "same failure and kept the coordinator, and four sibling subagents waiting on its result, from finishing. Which design "
           "is best?"),
        opts=("Cap local retries with backoff, then return the failure plus results of the tests that ran.",
              "Remove local retries so the first connection failure goes straight to the coordinator.",
              "Let the coordinator cancel any subagent after 10 minutes and discard whatever it produced.",
              "Raise the database connection timeout so that each attempt waits longer before it counts as failed."),
        ans=0,
        explain=("Local retry fits a transient failure, but it needs a limit, after which the failure goes up with partial results and "
                 "the attempts made. B sends up failures that one retry would have fixed. C throws away work and ends the "
                 "subagent without a report of what it tried. D makes each attempt slower and still has no end."),
        scenarios=(4,), points=("2.2:S3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 2.2 Skill 3 (local recovery, then propagate); the retry cap is a design judgment.",
        qtype="fix", level="medium", principle="proportionate",
        situation="unbounded retry on a flaky test database stalls a coordinator and four siblings",
        trap="remove local recovery or cancel from outside",
    ),
    # ---- S4: access failure vs valid empty result ----
    MCQ(
        id="Q2.2-22",
        q=("A `find_usages` tool returns `references: []` both when no code uses a function and when the repository's index is "
           "still building. The assistant was told that `legacy_total()` had no usages in `billing-v2`, deleted it, and three "
           "modules stopped compiling. The index build for that repository had not finished. Which change is most effective?"),
        opts=("Tell the assistant in its prompt to confirm every empty result with Grep before deleting any code.",
              "Return `references: []` together with the time of the last index build, and let the model judge it.",
              "Return an error that the index is still building; keep an empty list for real no-hit searches.",
              "Give new repositories a higher priority in the index queue, so that builds finish sooner."),
        ans=2,
        explain=("A search that could not run says nothing about usages, so it must not look like a search that found none. A relies on "
                 "the model remembering a check for each deletion. B leaves the ambiguity in place and makes the model reason "
                 "about a timestamp. D shortens the window in which the failure happens but does not remove the confusion."),
        scenarios=(4,), points=("2.2:S4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 2.2 Skill 4 (access failure versus valid empty result); no official page covers it.",
        qtype="fix", level="hard", principle="root_cause",
        situation="index still building returns an empty list that is read as no usages",
        trap="ask the model to double-check every empty result",
    ),
    MCQ(
        id="Q2.2-23",
        q=("A support agent's `order_history` tool returns a successful empty list for a customer with no orders in the past 90 "
           "days. A proposal says the tool should return an error in that case, \"so the agent definitely notices\". Logs show the "
           "current agent already tells such customers that nothing was found. How should you evaluate the proposal?"),
        opts=("Adopt it: an error is noticed more reliably than an empty list, which an agent may skip.",
              "Keep it a success with an empty list, and name the period searched.",
              "Adopt it, and set `isRetryable: true` so that the agent checks again before it answers.",
              "Keep it as a success, but return the customer's older orders so that the list is never empty."),
        ans=1,
        explain=("A lookup that ran and found nothing has given a true answer, and flagging it as an error would send the agent "
                 "into retries or escalation for no reason. A treats a correct answer as a fault. C adds retries for a lookup that "
                 "worked. D changes the answer by returning orders outside the period that was asked for."),
        scenarios=(1,), points=("2.2:S4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 2.2 Skill 4 (valid empty results are successful queries); no official page covers it.",
        qtype="evaluate", level="easy", principle="fit_for_purpose",
        situation="proposal to report a customer with no recent orders as an error",
        trap="turn a valid empty result into a failure",
    ),
    MCQ(
        id="Q2.2-24",
        q=("A systematic-review agent calls a `search_all` tool that queries four sources and merges whatever comes back. In 9% of "
           "runs the report says \"no registered trials found\", although a manual check finds some. In those runs the clinical "
           "trials registry logged a timeout, and the tool still returned the other three sources' results without any note. "
           "What is the root cause?"),
        opts=("The synthesis agent should have cross-checked the registry through a separate web search.",
              "The registry's timeout is set too short for its busiest hours.",
              "The synthesis prompt does not tell the agent to confirm that trials are absent before reporting.",
              "The merge step drops a failed source, so a source never searched looks like no matches."),
        ans=3,
        explain=("The tool turned an access failure into an empty contribution, so the agent could not tell 'searched, nothing' from "
                 "'could not search'. A and C ask the agent to compensate for a signal the tool should have given. B concerns "
                 "how often the failure happens and not why it goes unnoticed when it does."),
        scenarios=(3,), points=("2.2:S4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 2.2 Skill 4 (access failure versus valid empty result); no official page covers it.",
        qtype="diagnose", level="hard", principle="root_cause",
        situation="federated search drops a timed-out registry and reports no trials found",
        trap="ask the agent to cross-check instead of reporting the failed source",
    ),
)
