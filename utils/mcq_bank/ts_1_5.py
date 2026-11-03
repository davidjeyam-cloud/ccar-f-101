"""Exam bank · TS 1.5. Original questions; see docs/MCQ_BANK_PLAN.md."""
from utils.mcq_sets import MCQ, Evidence

TS = "1.5"
BULLETS = {
    "K1": "Hooks such as PostToolUse catch tool results and transform them before the model reads them",
    "K2": "Hooks catch outgoing tool calls so that a compliance rule is applied before the call runs",
    "K3": "Hooks give deterministic guarantees, while prompt instructions give only probable compliance",
    "S1": "Writing PostToolUse hooks that bring mixed data formats from different MCP tools into one form",
    "S2": "Writing interception hooks that block a policy-violating action and redirect to another workflow",
    "S3": "Choosing a hook over a prompt rule when the business needs guaranteed compliance",
}

QUESTIONS = (
    # ---- K1: transform results before the model sees them ----
    MCQ(
        id="Q1.5-01",
        q=("Your web search subagent reads pages through an MCP tool that returns the full page. In a sample of 200 results, "
           "about 70% of the text was menus, cookie notices and adverts, and long topics now run out of context before the "
           "synthesis step. Each result carries a URL and publication date, which the citations need. What is the most effective fix?"),
        opts=("A PostToolUse hook that returns `additionalContext` marking which sections of each page are noise.",
              "A PreToolUse hook that rewrites each URL to the site's print view, which usually has less page furniture.",
              "A PostToolUse hook that replaces each result with the body text plus its source fields.",
              "Automatic compaction, which will summarise the older pages whenever the context comes close to full."),
        ans=2,
        explain=("Replacing the result means the noise never enters context, and the citation fields are kept. A adds text "
                 "beside the original output, so the context grows. B depends on every site offering a print view. D lets "
                 "the noise in first, and its summaries can lose the URLs and dates the citations need."),
        scenarios=(3,), points=("1.5:K1",),
        evidence=(Evidence("code:agent-sdk/hooks", "To replace the tool's output before Claude sees it, set `updatedToolOutput`, which works for any tool in both SDKs."),),
        qtype="fix", level="medium", principle="fit_for_purpose",
        situation="web pages are 70% menus and adverts and fill the subagent's context",
        trap="annotate the noise instead of removing it",
    ),
    MCQ(
        id="Q1.5-02",
        q=("Tax identifiers must never reach your support agent's context. A synchronous PostToolUse hook on `get_tax_record` "
           "detects them and returns `decision: \"block\"` with the reason \"tax ID redacted\". Your logs show the hook firing "
           "and returning on every call, yet the agent still quoted a tax ID in 2% of its replies. What is the most likely "
           "root cause?"),
        opts=("`block` leaves the original output in place, so the identifier still reaches the model.",
              "`block` is not valid here; a result is only withheld when the hook returns `permissionDecision: \"deny\"`.",
              "The result had already been added to the conversation, because a PostToolUse hook can only observe it.",
              "The reason names the field without its value, so the model cannot tell what should be left out of replies."),
        ans=0,
        explain=("On PostToolUse, `block` adds the reason next to the result and the original stays; replacing it takes "
                 "`updatedToolOutput`. B borrows a PreToolUse field that does not withhold a result. C is wrong because this "
                 "hook can replace the output before the model sees it. D treats it as a wording problem, when the value is "
                 "still in the model's context."),
        scenarios=(1,), points=("1.5:K1",),
        evidence=(Evidence("code:hooks", "adds the `reason` next to the tool result. Claude still sees the original output; to replace it, use `updatedToolOutput`"),),
        basis="docs",
        qtype="diagnose", level="hard", principle="fit_for_purpose",
        situation="tax IDs still quoted although a result hook returns block on every call",
        trap="assume block removes the tool output",
    ),
    MCQ(
        id="Q1.5-03",
        q=("A repository clean-up agent has a `delete_stale_branches` tool. To protect release branches, a PostToolUse hook "
           "checks the branch list in each result and, on a match, replaces the output with \"blocked: protected branch\". "
           "The agent then reports that nothing was deleted. Last week `release/9.2` vanished from the remote during such a "
           "run. What is the root cause?"),
        opts=("The hook returned a replacement; it should have returned `decision: \"block\"` to cancel the running call.",
              "The match ran on the text of the result, which lists branches only after the remote has been updated.",
              "Replacing output works only for MCP tools, so the agent's report came from the unchanged result.",
              "The check runs once the tool has finished, so the rewrite changed only the model's view of it."),
        ans=3,
        explain=("PostToolUse fires after the tool has run, so rewriting the result changes what the model sees and nothing else; "
                 "a check that must stop an action belongs on the outgoing call. A is wrong because `block` on this event only "
                 "adds a reason. B describes the ordering but keeps the check in the same too-late place. C is false, since the "
                 "replacement works for any tool, and the agent's report shows it applied."),
        scenarios=(4,), points=("1.5:K1", "1.5:K2"),
        evidence=(Evidence("code:hooks", "`updatedToolOutput` only changes what Claude sees."),
                  Evidence("code:hooks", "The tool has already run by the time the hook fires, so any files written, commands executed, or network requests sent have already taken effect.")),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="result hook reports a release branch as protected after it was deleted",
        trap="treat rewriting a result as stopping the action",
    ),
    # ---- K2: intercept outgoing calls ----
    MCQ(
        id="Q1.5-04",
        q=("Goodwill credits are limited to 200 pounds per case, and a case may receive several. A hook on `issue_credit` denies "
           "any call above 200, and single large credits have stopped. This month's audit found 31 cases with three or four "
           "credits of about 90 pounds each. Which change best enforces the rule as written?"),
        opts=("Have the hook deny any second credit in a case, so that one call can never be followed by another.",
              "Have the hook add the case's earlier credits to the requested amount before it decides.",
              "Add a PostToolUse hook that returns the case total as `additionalContext`, so the model stops at the limit.",
              "Have the hook deny any credit issued within 24 hours of an earlier one on the same case."),
        ans=1,
        explain=("The limit applies to the case but the check looks at one call, so the decision needs the case total. A forbids "
                 "repeat credits that the policy allows. C gives the model better information but leaves the decision with the "
                 "model. D only spreads the same credits over more days."),
        scenarios=(1,), points=("1.5:K2",),
        evidence=(Evidence("code:agent-sdk/hooks", "receives input about what's happening: the tool name, its arguments, the session ID, and other event-specific details."),),
        qtype="choose", level="medium", principle="deterministic",
        situation="three small credits in one case add up past a per-case limit",
        trap="feed the total to the model as context",
    ),
    MCQ(
        id="Q1.5-05",
        q=("Files under `infra/prod/` sync to production on write. Your platform assistant has a PreToolUse hook with a "
           "`Write|Edit` matcher whose callback denies those paths by reading `file_path`. The assistant also runs tests through "
           "`Bash`. Over 900 sessions the hook logged no denials, yet 6 production files changed, and each of those sessions "
           "contains a `sed -i` step. What is the most effective fix?"),
        opts=("Widen the matcher to match every tool, and keep the callback's `file_path` check just as it is.",
              "Remove `Bash` from the assistant, so that every file change has to pass through `Write` or `Edit`.",
              "Add a PostToolUse hook on `Bash` that restores any production file changed by a shell command.",
              "Also intercept `Bash`, with a callback that checks `tool_input.command` for that folder."),
        ans=3,
        explain=("A shell write never reaches a `Write|Edit` matcher, so interception must cover that route and read the "
                 "argument that tool has. A runs on `Bash` but looks for a `file_path` that its input does not contain. B breaks "
                 "the test runs the assistant needs. C restores the file after it has already synced to production."),
        scenarios=(4,), points=("1.5:K2",),
        evidence=(Evidence("code:agent-sdk/hooks", "If Claude writes `.env` with a Bash command, the hook doesn't run."),),
        basis="docs",
        qtype="fix", level="hard", principle="deterministic",
        situation="sed through Bash changes production files past a Write and Edit hook",
        trap="widen the matcher but keep the file_path check",
    ),
    MCQ(
        id="Q1.5-06",
        q=("Legal has listed 40 publisher domains that your research subagents must never request, because of a licence "
           "dispute. The subagents use `WebFetch` on many other sites, and the list changes monthly. A prompt rule was missed "
           "in 11 of 5,000 fetches. How should you configure the control?"),
        opts=("A PreToolUse hook matching `WebFetch`, whose callback reads the URL and denies listed domains.",
              "A PreToolUse hook whose matcher is a regex of the 40 domains, so that it fires for those fetches only.",
              "A PostToolUse hook on `WebFetch` that replaces the page with a notice when the URL is on the list.",
              "A PreToolUse hook on every tool that returns the 40 domains as `additionalContext` before each call."),
        ans=0,
        explain=("The block must come before the request, and the domain is an argument, so the callback has to inspect it. B "
                 "misreads matchers, which test the tool name and would never see a domain. C hides the page but the prohibited "
                 "request has already gone out. D only gives the model a stronger reminder, so it is still the model's choice."),
        scenarios=(3,), points=("1.5:K2",),
        evidence=(Evidence("code:agent-sdk/hooks", "Matchers only match tool names, not file paths or other arguments."),),
        qtype="configure", level="medium", principle="deterministic",
        situation="research fetches must never request 40 disputed publisher domains",
        trap="put the domains in the matcher",
    ),
    MCQ(
        id="Q1.5-07",
        q=("Accounts with an open dispute must never be closed by your support agent. The agent calls `close_account` about "
           "150 times a day, and the dispute flag can be read from the billing system. Closure takes effect at once and "
           "cannot be reversed. Where should the check go?"),
        opts=("In a PostToolUse hook on `get_account` that adds a dispute warning as context for the next decision.",
              "In the `close_account` tool description, as a condition that the agent has to confirm before calling it.",
              "In a PreToolUse hook on `close_account` that reads the flag and denies the call if needed.",
              "In a first step that forces a call to `get_dispute_status` through `tool_choice` at the start of each chat."),
        ans=2,
        explain=("The rule must hold on every closure, so code has to decide on the outgoing call. A informs the model and leaves "
                 "the choice with it. B is a prompt instruction in another place. D makes the status call happen but nothing "
                 "ties the later closure to its answer."),
        scenarios=(1,), points=("1.5:K2",),
        evidence=(Evidence("code:agent-sdk/hooks", "**Block dangerous operations** before they execute, like destructive shell commands or unauthorized file access"),),
        qtype="configure", level="easy", principle="deterministic",
        situation="irreversible account closure while a billing dispute is open",
        trap="warn the model through context instead of deciding in code",
    ),
    # ---- K3: deterministic vs probabilistic ----
    MCQ(
        id="Q1.5-08",
        q=("Law forbids shipping replacement goods to embargoed regions, and any breach must be reported to a regulator. Your "
           "team tuned the support agent's prompt until an evaluation of 3,000 conversations showed no embargoed shipments. "
           "The manager now wants to release as it is, since \"the data proves the prompt works\". How should you evaluate this?"),
        opts=("Release it: 3,000 clean conversations are enough evidence that this rule holds in production.",
              "Hold it for a check in code on the shipping call, as a clean sample describes past runs.",
              "Release it, and make the evaluation a gate that must pass again on every change to the prompt.",
              "Hold it until adversarial test conversations also come back with zero embargoed shipments."),
        ans=1,
        explain=("Whether the model follows a prompt is decided again on each turn, so a clean score does not rule out a breach, "
                 "and this rule allows none. A treats a test result as a guarantee. C catches regressions in testing but enforces "
                 "nothing in production. D produces a better estimate of the same kind."),
        scenarios=(1,), points=("1.5:K3",),
        evidence=(Evidence("code:best-practices", "A prompt alone can't guarantee either of those."),),
        qtype="evaluate", level="medium", principle="deterministic",
        situation="prompt scores clean on 3,000 conversations for embargoed shipments",
        trap="treat an evaluation score as a guarantee",
    ),
    MCQ(
        id="Q1.5-09",
        q=("A PreToolUse command hook denies `release_hold` calls above 400 units, and policy says the limit is a guarantee. "
           "Before launch the team plans to run 5,000 simulated customer chats, including pushy ones, and require zero "
           "breaches. Each run takes three days, and the hook's decision depends only on the call it receives. Which "
           "verification is most effective?"),
        opts=("Run the 5,000 chats nightly for a month, and release only if no breach appears in any run.",
              "Send scripted calls straight to the hook at 399, 400 and 401 units, and assert each decision.",
              "Have a second model read the hook script and rate how likely it is to block every large call.",
              "Run the chats once with a prompt-only agent, and release if the hook cuts the breaches tenfold."),
        ans=1,
        explain=("The hook returns the same decision for the same call whatever the model says, so scripted inputs test it "
                 "directly, quickly and at the edges. A samples conversations, which only reach the edge cases by luck and cost "
                 "three days a run. C asks a model for a probability about code that can simply be run. D measures a reduction "
                 "in a rate, which suits a prompt and is not the proof a guarantee needs."),
        scenarios=(1,), points=("1.5:K3",),
        evidence=(Evidence("code:best-practices", "Claude Code applies this every time, no matter what the model decided to do."),),
        qtype="evaluate", level="medium", principle="deterministic",
        situation="verifying a unit-limit hook by sampling simulated chats",
        trap="sample conversations to test a code gate",
    ),
    MCQ(
        id="Q1.5-10",
        q=("Reviewers want your research synthesis agent to favour peer-reviewed papers when they conflict with blog posts, and "
           "blogs are often the only source on recent events. Runs are unattended. After a hook fixed a compliance issue "
           "elsewhere, an engineer proposes one that denies fetches from any site outside a list of 200 journals. How should "
           "you evaluate this?"),
        opts=("Keep it in the prompt with clear criteria, since weighing two sources takes judgment.",
              "Use the proposed hook, since a preference that reviewers rely on should not depend on the model.",
              "Use the hook with an `ask` decision, so that a reviewer approves each fetch outside the journal list.",
              "Use a PostToolUse hook that removes a blog result whenever a journal result covers the same topic."),
        ans=0,
        explain=("Hooks suit rules that hold the same way every time, while deciding which source to trust in a conflict needs "
                 "the model to think. B cuts off the blogs that recent events depend on. C needs a reviewer, and the runs are "
                 "unattended. D makes the same judgment in code, and code cannot tell when two sources really conflict."),
        scenarios=(3,), points=("1.5:K3", "1.5:S3"),
        evidence=(Evidence("code:features-overview", "**Use a hook** when the action must happen the same way every time and doesn't need Claude to think."),),
        qtype="evaluate", level="medium", principle="proportionate",
        situation="source preference for peer-reviewed papers proposed as a domain allowlist hook",
        trap="turn a judgment preference into a hook",
    ),
    # ---- S1: normalise mixed formats ----
    MCQ(
        id="Q1.5-11",
        q=("Your support agent calls three MCP tools that report money differently: billing sends integer pence, shipping "
           "sends a decimal string, and returns sends text with a currency sign. In 9% of partial-refund cases the agent adds "
           "these up wrongly. The servers belong to other teams and will not change this year. Which approach is best?"),
        opts=("A `calculate_total` tool, and a prompt rule telling the model to send every sum through it.",
              "A PostToolUse hook that returns `additionalContext` stating the unit of each money field.",
              "A PostToolUse hook that rewrites every money field into a single format.",
              "A format table in the system prompt, so that the model can convert each value on its own."),
        ans=2,
        explain=("The mismatch sits in the results, so code should settle it once, before the model reads them. A moves the "
                 "arithmetic, but the model must still read each format correctly to fill in the inputs. B labels the units and "
                 "leaves the conversion with the model. D has the same weakness, and it is where the 9% comes from."),
        scenarios=(1,), points=("1.5:S1",),
        evidence=(Evidence("code:agent-sdk/hooks", "To replace the tool's output before Claude sees it, set `updatedToolOutput`, which works for any tool in both SDKs."),),
        qtype="choose", level="easy", principle="deterministic",
        situation="pence, decimal strings and currency text are added up wrongly in refunds",
        trap="add a calculator tool",
    ),
    MCQ(
        id="Q1.5-12",
        q=("Your research agent builds timelines from a US news archive and a UK court register, both MCP servers. Both return "
           "dates like `03/04/2025`, each in its own country's usual order. A value such as `25/04/2025` is clear, but most are "
           "not, and 12% of timelines misorder events. How should the PostToolUse normaliser work?"),
        opts=("Try day first on every value, then fall back to month first when that fails to parse.",
              "Pick the date order for each result from `tool_name`, then rewrite the values in ISO 8601.",
              "Call a small model inside the hook to infer each date's order from the text around it.",
              "Keep each raw date and return `additionalContext` warning the model that it may be ambiguous."),
        ans=1,
        explain=("The same string can mean two dates, so the value alone cannot settle it, but the hook knows which tool produced "
                 "it and each source has one order. A silently reads most US dates wrongly. C replaces a fact the code has with a "
                 "guess. D passes the same ambiguity back to the model, which has no better way to resolve it."),
        scenarios=(3,), points=("1.5:S1",),
        evidence=(Evidence("code:agent-sdk/hooks", "receives input about what's happening: the tool name, its arguments, the session ID, and other event-specific details."),),
        qtype="configure", level="medium", principle="deterministic",
        situation="identical date strings mean day-first or month-first depending on the server",
        trap="one parser with a fallback order",
    ),
    MCQ(
        id="Q1.5-13",
        q=("An incident-review agent combines deployment records in Unix seconds with error logs in ISO 8601 with offsets. A "
           "PostToolUse hook now rewrites both as `YYYY-MM-DD`, which ended the format mix-ups. But in 15 of 60 reviews the agent "
           "says it cannot tell whether a deployment came before an error on the same day. What is the most likely root cause?"),
        opts=("The shared format holds no time of day, so same-date events have no order.",
              "The hook applied offsets unevenly, so events from the two tools no longer line up within a day.",
              "A PostToolUse hook sees one tool's result at a time, so it cannot align values across two tools.",
              "The model needs each tool's original strings, because it cannot compare values that a hook rewrote."),
        ans=0,
        explain=("Normalising should unify the format and keep the meaning, and this format dropped the detail the question "
                 "depends on, so full UTC timestamps are needed. B would give wrong orders, not an agent unable to tell. C is "
                 "wrong because each value can be converted alone to one shared format. D is ruled out by the stem, where the "
                 "rewrite ended the mix-ups."),
        scenarios=(4,), points=("1.5:S1",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 1.5 Skill 1 names normalising timestamps; keeping their precision is a judgment no official page states.",
        qtype="diagnose", level="medium", principle="preserve_information",
        situation="date-only normaliser hides the order of a deployment and an error",
        trap="blame the hook's handling of offsets",
    ),
    MCQ(
        id="Q1.5-14",
        q=("Four research subagents read three archive MCP servers whose results use numeric status codes for items such as "
           "preprint, published and retracted. Each subagent's prompt holds a paragraph decoding them. When one archive "
           "redefined code 7, one paragraph was updated, and retracted papers were cited in 5% of reports for a month. Which "
           "design best prevents a repeat? Even the subagent with the updated paragraph misread about 2% of codes."),
        opts=("One shared prompt fragment, imported by all four subagents, that holds the decoding table.",
              "A `decode_status` tool that each subagent is told to call whenever a result contains a code.",
              "A table in the coordinator's prompt, which it copies into each Task prompt that it sends.",
              "One PostToolUse hook that turns each code into its meaning before any subagent reads it."),
        ans=3,
        explain=("Code turns every code into a word before any model reads it, so nothing is decoded by a model and a change is "
                 "made once; the 2% shows that decoding by the model is itself unreliable. A fixes the duplication but still "
                 "leaves the decoding with each model. B depends on the model choosing to call the tool. C leaves the "
                 "decoding with the model too, and adds a copying step."),
        scenarios=(3,), points=("1.5:S1",),
        evidence=(Evidence("code:agent-sdk/hooks", "To replace the tool's output before Claude sees it, set `updatedToolOutput`, which works for any tool in both SDKs."),),
        qtype="fix", level="medium", principle="deterministic",
        situation="redefined archive status code updated in one of four subagent prompts",
        trap="share the decoding table as a prompt fragment",
    ),
    # ---- S2: block and redirect ----
    MCQ(
        id="Q1.5-15",
        q=("A hook denies `export_customer_data` when a request lacks a signed consent form. To redirect those cases, it puts "
           "\"Do not retry. Call `escalate_to_human`\" in `systemMessage` and leaves `permissionDecisionReason` empty. The agent "
           "keeps retrying the export, and customers see the message on screen. What is the most likely root cause?"),
        opts=("`systemMessage` is delivered on the next turn, so it arrives after the agent has already retried.",
              "A denied call removes the other tools for that turn, so the agent has only the export left to call.",
              "The model never received the redirect, because it was written to a field meant for the user.",
              "The deny needs `continue: false` as well, or the model treats the denial as a temporary failure."),
        ans=2,
        explain=("`systemMessage` is shown to the user, which the stem confirms, while the deny reason is what the model reads, "
                 "and here it is empty. A invents a delay, and the text would not reach the model at any time. B invents a rule, "
                 "since a denial leaves the other tools available. D would stop the agent, which is the opposite of redirecting it."),
        scenarios=(1,), points=("1.5:S2",),
        evidence=(Evidence("code:agent-sdk/hooks", "The `systemMessage` field shows a message to the user, not the model."),
                  Evidence("code:agent-sdk/hooks", "`permissionDecisionReason` tells the model why.")),
        basis="docs",
        qtype="diagnose", level="medium", principle="fit_for_purpose",
        situation="redirect text placed in systemMessage so the agent retries a denied export",
        trap="assume systemMessage reaches the model later",
    ),
    MCQ(
        id="Q1.5-16",
        q=("A hook denies your citation subagent's fetches from paywalled journals, and its reason says to use "
           "`request_licensed_copy` instead. That tool works when the coordinator calls it. The subagent is defined with "
           "`tools: [\"WebSearch\", \"WebFetch\"]`. After each denial it makes no further call for that source and writes "
           "\"source unavailable\", which now affects 18% of citations. What is the most likely root cause?"),
        opts=("The reason is worded as advice, so the subagent is free to treat the redirect as optional.",
              "The redirect names a tool that this subagent's definition does not give it.",
              "A deny ends a subagent's work on that source, so that only the coordinator can act on it.",
              "The coordinator is not told of each denial, and it must approve the next step for the subagent."),
        ans=1,
        explain=("A redirect only works if the alternative is reachable, and the definition lists two tools that do not include "
                 "it. A would call for firmer wording, but no wording makes a missing tool callable. C is wrong because a denial "
                 "reaches the model as a reason and the subagent can carry on. D invents an approval step between denial and "
                 "the next call."),
        scenarios=(3,), points=("1.5:S2",),
        evidence=(Evidence("code:agent-sdk/subagents", "Use the `tools` field to limit what a subagent can do:"),
                  Evidence("code:agent-sdk/hooks", "`permissionDecisionReason` tells the model why.")),
        qtype="diagnose", level="hard", principle="root_cause",
        situation="deny reason points to a licensed-copy tool the subagent does not have",
        trap="reword the reason more firmly",
    ),
    MCQ(
        id="Q1.5-17",
        q=("A hook denies `reverse_chargeback` for flagged accounts and opens a ticket itself from the call's arguments, an "
           "account ID and an amount. The fraud team works from its ticket queue and cannot open agent sessions. In 60% of these "
           "tickets the analyst must ask the customer to explain everything again. The agent's only other route to a person "
           "is `escalate_to_human`. What is the most effective change?"),
        opts=("Have the deny reason direct the model to call `escalate_to_human` with a structured summary.",
              "Add the session ID to each ticket, so that the analyst can look up what the customer has said.",
              "Have the hook read the transcript file and paste the whole conversation into each ticket.",
              "Have the hook copy every field of `tool_input` to the ticket, so the analyst has all the arguments."),
        ans=0,
        explain=("The hook sees only the call, while the model holds the cause and the customer's account of it, so the redirect "
                 "should send it to a handoff that carries those; with the call denied, that route is the only one left, so the "
                 "model has little choice but to take it. B points to sessions the team cannot open. C gives a raw "
                 "transcript with no root cause or recommended action. D copies the same two fields again."),
        scenarios=(1,), points=("1.5:S2", "1.4:S3"),
        evidence=(Evidence("code:agent-sdk/hooks", "`permissionDecisionReason` tells the model why."),),
        qtype="fix", level="medium", principle="preserve_information",
        situation="hook-made tickets hold only account ID and amount for a blocked chargeback reversal",
        trap="paste the raw transcript into the ticket",
    ),
    MCQ(
        id="Q1.5-18",
        q=("Credit notes above 300 pounds need a finance manager's decision. An engineer suggests that instead of denying those "
           "calls, the hook should rewrite the amount to 300 with `updatedInput` and let the call run, so that \"the customer "
           "gets something at once and no case waits in a queue\". Logs show requests of up to 2,000 pounds. How should you "
           "evaluate this?"),
        opts=("Use the rewrite: each call that runs stays within the limit, so the policy is met in full.",
              "Use the rewrite, and have the agent tell each customer that the amount was reduced by a rule.",
              "Deny instead, and send the case on, so that a person sets the amount above the limit.",
              "Use the rewrite with an `ask` decision, so that the customer confirms the lower amount in the chat."),
        ans=2,
        explain=("The policy reserves these cases for a manager, so the call should stop and the case should go there. A keeps "
                 "the number legal but settles the case with no decision, when more or nothing may be owed. B only announces the "
                 "same bypass. D gets the customer's consent, which is not the decision the policy requires."),
        scenarios=(1,), points=("1.5:S2",),
        evidence=(Evidence("code:agent-sdk/hooks", "`permissionDecision: 'deny'` stops the tool call."),),
        qtype="evaluate", level="medium", principle="calibrated_escalation",
        situation="proposal to rewrite large credit notes down to the limit instead of blocking",
        trap="silently cap the amount with a rewritten input",
    ),
    # ---- S3: choose hooks for guaranteed compliance ----
    MCQ(
        id="Q1.5-19",
        q=("Payout details may change only after `verify_identity` has passed in that session. A prompt rule held at 99.8% for "
           "months, then fell to 97% after a routine model update, and 40 accounts changed unverified. The manager proposes "
           "pinning the old model and marking the rule as CRITICAL. Which response best meets the requirement?"),
        opts=("Pin the old model as proposed, and add an alert for whenever compliance drops below 99%.",
              "Mark the rule as CRITICAL, and add few-shot examples showing the check before each change.",
              "Force a `verify_identity` call with `tool_choice` on the first turn of every conversation.",
              "Deny `update_payout_account` in a hook unless the session holds a passed check."),
        ans=3,
        explain=("The rule needs a guarantee, and the drop shows that prompt compliance moves for reasons outside the rule, so code "
                 "must check the prerequisite on the call. A freezes the model and keeps a failure rate. B adds prompt text to a "
                 "rule that prompts did not hold. C makes the check run, but nothing stops a change after it fails."),
        scenarios=(1,), points=("1.5:S3", "1.4:S1"),
        evidence=(Evidence("code:best-practices", "If something has to happen every time, make it a hook, a deny rule, or a managed setting."),),
        qtype="choose", level="medium", principle="deterministic",
        situation="payout-change rule falls to 97% after a routine model update",
        trap="force the check on the first turn with tool_choice",
    ),
    MCQ(
        id="Q1.5-20",
        q=("CLAUDE.md says \"never edit generated files under `src/gen/`\", and code review caught the rule being broken in 3 of "
           "400 sessions. Each slip cost a release, so the team now requires zero. An engineer suggests moving the line to the "
           "top of CLAUDE.md in capitals. What is the best choice?"),
        opts=("Move the line to the top, since instructions read first carry the most weight with the model.",
              "Add a PreToolUse hook that denies those paths and names the real source to change.",
              "Move the rule to a path-scoped file in `.claude/rules/`, so that it loads with those files.",
              "Move the rule into a skill that the agent loads whenever it is about to touch that folder."),
        ans=1,
        explain=("An instruction is a request wherever it sits, and zero needs enforcement on the edit itself. A changes the "
                 "emphasis of the same request. C makes the rule load at a better moment, but it is still an instruction. D "
                 "moves the request to another file, and the agent still decides whether to follow it."),
        scenarios=(4,), points=("1.5:S3",),
        evidence=(Evidence("code:features-overview", "A `PreToolUse` hook that blocks the edit is enforcement."),),
        qtype="choose", level="easy", principle="deterministic",
        situation="generated-files rule in CLAUDE.md broken in 3 of 400 sessions",
        trap="move the rule to a path-scoped rules file",
    ),
)
