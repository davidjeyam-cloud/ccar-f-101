"""Exam bank · TS 1.4. Original questions; see docs/MCQ_BANK_PLAN.md."""
from utils.mcq_sets import MCQ, Evidence

TS = "1.4"
BULLETS = {
    "K1": "Programmatic enforcement (hooks, prerequisite gates) versus prompt-based guidance for workflow ordering",
    "K2": "Prompt instructions alone keep a non-zero failure rate where compliance must be deterministic",
    "K3": "Structured handoff protocols for mid-process escalation: customer details, root cause analysis, recommended actions",
    "S1": "Programmatic prerequisites that block downstream tool calls until earlier steps have completed",
    "S2": "Splitting multi-concern requests into items, investigating them in parallel with shared context, then one unified resolution",
    "S3": "Structured handoff summaries for human agents who cannot see the conversation transcript",
}

QUESTIONS = (
    # ---- K1: enforcement versus guidance ----
    MCQ(
        id="Q1.4-01",
        q=("Your boilerplate agent has two team rules. A database snapshot must exist before `db_migrate` runs, because one "
           "unprotected migration last quarter cost a day of data. Separately, the team likes named exports over default "
           "exports, with some exceptions for framework files. Both rules sit in CLAUDE.md today. Where should each one live?"),
        opts=("Put the snapshot steps in a skill the agent invokes before migrating, and leave exports in CLAUDE.md.",
              "Use a hook that denies the call until a snapshot exists, and leave exports as a CLAUDE.md line.",
              "Use one hook for each rule, so that both are applied the same way on every matching tool call.",
              "Move the snapshot rule to the top of CLAUDE.md, and put exports in a path-specific rules file."),
        ans=1,
        explain=("A rule that must hold every time belongs in code, while a preference with exceptions can stay as guidance. "
                 "A looks structured, but the model still chooses whether to invoke the skill. C blocks the legitimate "
                 "framework exceptions. D only moves the costly rule to another place the model reads."),
        scenarios=(4,), points=("1.4:K1", "1.4:K2"),
        evidence=(Evidence("code:best-practices", "If something has to happen every time, make it a hook, a deny rule, or a managed setting."),),
        qtype="choose", level="easy", principle="deterministic",
        situation="snapshot before db_migrate and a named-exports preference both sit in CLAUDE.md",
        trap="use a skill for the must-hold step, or hooks for everything",
    ),
    MCQ(
        id="Q1.4-02",
        q=("A new `transfer_balance` tool must run only after identity is verified. The team registers a `PostToolUse` hook on "
           "it that checks for a verified ID and, when none exists, writes an alert to the security channel. Alerts arrive "
           "for every unverified transfer, yet the unverified rate stays at 9 per 1,000 and each alerted transfer had "
           "already moved money. What is the most likely root cause?"),
        opts=("The hook's matcher is too broad, so alerts for other tools bury the ones that concern transfers.",
              "The alert should be returned to the model as added context, so that the agent can react to it.",
              "The hook should run asynchronously, so that checking identity does not slow the transfer down.",
              "The check runs after the tool has executed, so it can report a breach and cannot prevent one."),
        ans=3,
        explain=("`PostToolUse` fires once the tool has run, so it works for auditing and not for prerequisites; a check that "
                 "must block belongs before the call. A is ruled out, since every unverified transfer did raise an alert. B "
                 "gives the model information about a transfer that already happened. C would make the check even less able "
                 "to affect the call."),
        scenarios=(1,), points=("1.4:K1", "1.4:S1"),
        evidence=(Evidence("code:hooks-guide", "`PreToolUse` fires before tool execution, `PostToolUse` fires after."),),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="PostToolUse identity check alerts on every unverified transfer after the money has moved",
        trap="tune the matcher or feed the alert back to the model",
    ),
    MCQ(
        id="Q1.4-03",
        q=("Your support prompt says the agent should usually call `search_faq` before asking the customer a clarifying "
           "question. It does so in about 90% of chats, and a miss costs one extra question. An engineer proposes a gate that "
           "blocks every reply until `search_faq` has run. Many order-status chats never need the FAQ, but a keyword check to "
           "spot them misfiled about one chat in five when tried. How should you evaluate the proposal?"),
        opts=("Reject it: a miss costs little and many chats rightly skip the step, so guidance suits this order.",
              "Adopt it: the 10% of misses show a non-zero failure rate, and that is what calls for a gate in code.",
              "Adopt it with an exemption for order-status chats, detected by a keyword check on the first message.",
              "Reject it, and add few-shot examples until the prompt reaches full compliance on this ordering rule."),
        ans=0,
        explain=("A non-zero failure rate matters when compliance must be deterministic; here a miss is cheap and the model "
                 "should be free to skip the step. B applies that test without asking what a miss costs. C keeps the needless "
                 "gate and adds a brittle keyword rule. D chases full compliance on a rule that does not need it, and many "
                 "chats should skip the step anyway."),
        scenarios=(1,), points=("1.4:K1",),
        evidence=(Evidence("code:best-practices", "`CLAUDE.md` is for guidelines, and Claude is allowed to decide a guideline doesn't apply."),),
        qtype="evaluate", level="medium", principle="proportionate",
        situation="engineer proposes a gate forcing search_faq before every support reply",
        trap="enforce every ordering in code",
    ),
    MCQ(
        id="Q1.4-04",
        q=("A Claude Code agent on your platform team must run `terraform validate` before any `terraform apply`, and "
           "CLAUDE.md says so. Auditing 300 long sessions, you find the rule was followed on every apply in the first 30 "
           "turns, but on only 88% of applies after turn 120. The rule is still in context at that point. Which change "
           "best meets a requirement of 100%?"),
        opts=("Move the rule into a skill that the agent loads before it runs any apply command.",
              "Send the rule again as added context every 20 turns, using a `UserPromptSubmit` hook.",
              "Add a `PreToolUse` command hook that denies `terraform apply` until validate has passed.",
              "End each session at 100 turns with `/clear`, so that the rule is always fresh in context."),
        ans=2,
        explain=("A requirement of 100% needs a gate in code, which does not depend on how far into a session the model is. A "
                 "moves the rule to another place the model has to choose to follow. B repeats guidance, which raises the "
                 "rate and leaves the choice with the model. D shortens the exposure and keeps a non-zero failure rate."),
        scenarios=(4,), points=("1.4:K2", "1.4:K1"),
        evidence=(Evidence("code:best-practices", "A line like `Always typecheck before you finish` in this file works most of the time, not every time."),),
        qtype="configure", level="medium", principle="deterministic",
        situation="terraform validate rule drops to 88% compliance late in long sessions",
        trap="repeat or relocate the rule instead of gating the apply",
    ),
    # ---- K2: non-zero failure rate ----
    MCQ(
        id="Q1.4-05",
        q=("Before launching account closures, your team tests a prompt rule that the agent must verify identity before "
           "calling `close_account`. In 2,000 scripted test chats it verified every time, so an engineer says a code gate is "
           "now unnecessary. A wrongful closure cannot be undone. How should you evaluate the claim?"),
        opts=("It holds, because 2,000 chats with no failures is strong evidence the rule will last in production.",
              "It holds if a daily audit of closures is added, so any miss is noticed and raised within a day.",
              "It fails: no failures in a sample is not a guarantee, and this action needs one before it runs.",
              "It needs more data: run 20,000 varied chats, and drop the gate if there are still no failures."),
        ans=2,
        explain=("A prompt leaves the decision to the model each time, so a clean sample lowers the estimated rate and does not "
                 "make it zero; an irreversible action needs a guarantee. A treats a test as a proof. B finds a wrongful "
                 "closure after it can no longer be undone. D gives a tighter estimate with the same limit."),
        scenarios=(1,), points=("1.4:K2",),
        evidence=(Evidence("code:best-practices", "but there's no *guarantee* that it'll follow your instructions."),),
        qtype="evaluate", level="medium", principle="deterministic",
        situation="2,000 clean test chats used to argue that account closure needs no gate",
        trap="treat a clean sample as a guarantee",
    ),
    MCQ(
        id="Q1.4-06",
        q=("After an agent deployed without the smoke test, your team rewrote the CLAUDE.md line in capitals with the word "
           "IMPORTANT. Two weeks later it happened again. The session log shows the file was loaded and the line was in "
           "context, and no other instruction conflicted with it. Your manager asks why the rewrite failed. What is the best "
           "explanation?"),
        opts=("Capitals are ignored by the model, so a numbered checklist at the top of the file would have held.",
              "A line in that file is read and weighed, so strong wording improves the odds and no more.",
              "The line sits at the wrong level of the hierarchy, and a project-level copy would have applied.",
              "The line gave no reason, so adding the cost of skipping the test would have made the model follow it."),
        ans=1,
        explain=("CLAUDE.md is guidance the model weighs, so any wording improves the odds and gives no guarantee; a must-happen "
                 "step needs a hook. A and D only swap one wording for another, which can lower the miss rate and still leaves "
                 "the decision with the model. C is ruled out because the line was in context."),
        scenarios=(4,), points=("1.4:K2",),
        evidence=(Evidence("code:best-practices", "But no matter how strongly you word it, whether Claude follows that line on a given turn is still Claude's call."),),
        qtype="diagnose", level="easy", principle="deterministic",
        situation="capitalised CLAUDE.md smoke-test rule is loaded and still skipped before a deploy",
        trap="better wording instead of enforcement",
    ),
    # ---- K3: handoff protocols ----
    MCQ(
        id="Q1.4-07",
        q=("Your agent's handoffs carry four set fields: customer ID, order number, refund amount and recommended action. Human "
           "agents still reopen the investigation on 64% of tickets, repeating the same lookups before approving anything. "
           "When reviewers check, the recommendation was right in 91% of cases. A trial that added the chat transcript to "
           "tickets changed nothing. What is the most likely root cause?"),
        opts=("The recommended action is too loose, and it should name the exact tool call the human must make.",
              "The ticket shows no confidence score, so human agents cannot tell which recommendations to accept.",
              "The tickets reach human agents too late, after the details have already gone stale in the backend.",
              "Nothing in the ticket says what went wrong, so the advice cannot be judged without rework."),
        ans=3,
        explain=("The four fields leave out the analysis behind the recommendation, so a human has to rebuild it to trust it. A "
                 "tightens a recommendation that is already right in 91% of cases. B adds a self-reported number and no "
                 "reason. C has no support in the stem, since the lookups repeat what the agent already found."),
        scenarios=(1,), points=("1.4:K3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 1.4 Knowledge 3 lists root cause analysis as part of the handoff; no official page covers human handoffs.",
        qtype="diagnose", level="medium", principle="preserve_information",
        situation="accurate four-field handoffs still make humans reopen 64% of tickets",
        trap="add a confidence score or tighten the recommendation",
    ),
    MCQ(
        id="Q1.4-08",
        q=("A customer's two-item return is escalated partway through: `process_refund` has already succeeded for the kettle, "
           "and the lamp needs a policy exception. The handoff gives the customer ID, the root cause and a recommended lamp "
           "refund, and human agents cannot see the chat. Last month, 4 such tickets ended with the first item refunded twice. "
           "What is the most effective fix?"),
        opts=("State each action already taken and its result in a required section of the handoff.",
              "Open one ticket per item, so that each human agent deals with a single item of the return.",
              "Escalate as soon as any exception appears, before the agent has refunded any other item.",
              "Have human agents ask the customer which refunds have arrived before they approve another."),
        ans=0,
        explain=("A mid-process handoff has to say what has already happened, or the human may repeat it. B splits the return "
                 "but the kettle ticket still does not say it was refunded. C holds up the routine item, and any step taken "
                 "before the escalation still goes unreported. D relies on the customer for a fact the agent already holds."),
        scenarios=(1,), points=("1.4:K3", "1.4:S3"),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 1.4 Knowledge 3 covers mid-process escalation; no official page covers human handoffs.",
        qtype="fix", level="medium", principle="preserve_information",
        situation="partly refunded two-item return is escalated and the first item is refunded twice",
        trap="split the ticket or escalate earlier",
    ),
    MCQ(
        id="Q1.4-09",
        q=("A migration agent working for an internal team stops at step 3 of 5 on a conflict, and pages the on-call engineer "
           "with \"Migration failed, check logs\". The engineer cannot open the agent's session, and twice this month "
           "re-ran the early steps, which damaged data. Which change most improves this handoff?"),
        opts=("Link the raw 9,000-line session log from the page, with the final error line copied into the alert.",
              "Have a stronger model retry the conflict first, so that it pages the engineer far less often overall.",
              "Send requester, repository, work done, cause and suggested next step as fixed fields.",
              "Add a runbook section that shows engineers how to work out which steps ran from the database state."),
        ans=2,
        explain=("The engineer needs what a support handoff carries: who it is for, what was done, why it stopped and what to do "
                 "next. A gives the engineer a pile to search and still does not state those conclusions. B changes how often "
                 "the handoff happens, not what it carries. D makes the engineer reconstruct what the agent already knows."),
        scenarios=(4,), points=("1.4:K3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: applies TS 1.4 Knowledge 3 to an internal requester; no official page covers human handoffs.",
        qtype="fix", level="medium", principle="preserve_information",
        situation="migration agent pages on-call with a bare failure and early steps are re-run",
        trap="link the raw session log",
    ),
    # ---- S1: programmatic prerequisites ----
    MCQ(
        id="Q1.4-10",
        q=("Your gate blocks `process_refund` until `get_customer` has appeared in the session's tool log. A monthly audit "
           "still finds refunds on unverified accounts. In each case `get_customer` had returned zero matches or two matches "
           "and the agent carried on. What is the most effective fix?"),
        opts=("Require a `customer_id` argument in the `process_refund` schema, so a refund cannot name no account.",
              "Open the gate only on a stored result holding exactly one confirmed account ID for the session.",
              "Add a `verified: true` argument the agent must set on `process_refund`, and have the gate test it.",
              "Extend the prompt so the agent halts whenever a `get_customer` lookup looks unusual or incomplete."),
        ans=1,
        explain=("The prerequisite is a verified ID, so the gate must test the tool's outcome and not the fact that it ran. A "
                 "makes the model supply an ID, but nothing checks that it was verified. C turns the gate into a check of "
                 "the model's own claim. D hands the decision back to a prompt in the exact case the gate exists for."),
        scenarios=(1,), points=("1.4:S1",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 1.4 Skill 1 names a returned verified customer ID as the condition.",
        qtype="fix", level="easy", principle="deterministic",
        situation="refund gate opens on any get_customer call, even one with zero or two matches",
        trap="have the model assert verification in an argument",
    ),
    MCQ(
        id="Q1.4-11",
        q=("Your gate blocks `process_refund` until a verified customer ID is stored for the session. An audit finds 7 refunds "
           "that passed it. In each, a real customer verified correctly, then gave an order number they had seen on someone "
           "else's parcel, and the refund posted to that order. Which change closes this gap?"),
        opts=("Run `get_customer` again just before each refund, so that the stored ID is fresh when the gate is checked.",
              "Add a system prompt rule that customers may only ever request a refund on an order placed on their account.",
              "Clear the stored ID after each refund, so that every later refund in the chat must pass verification again.",
              "Have the gate look up the order named in the call, and refuse it unless its owner is the stored ID."),
        ans=3,
        explain=("The gate proves that someone is verified, not that this refund belongs to them, so it must compare the call's "
                 "order with the stored ID. A and C repeat a check that this customer passes honestly each time. B moves a "
                 "must-hold rule back into a prompt."),
        scenarios=(1,), points=("1.4:K1", "1.4:S1"),
        evidence=(Evidence("code:agent-sdk/hooks", "`PreToolUseHookInput` includes `tool_name` and `tool_input`"),),
        qtype="fix", level="medium", principle="deterministic",
        situation="verified customer gets a refund on an order number seen on another parcel",
        trap="re-verify instead of comparing the order with the verified ID",
    ),
    MCQ(
        id="Q1.4-12",
        q=("Your new gate stops unverified refunds by raising a bare `Error 500`. Since launch, the agent retries the blocked "
           "call four times in about 15% of chats, then tells customers the refund system is down. The refund service has "
           "had no outage, and in those chats the agent never calls `get_customer`. What is the most likely root cause?"),
        opts=("The rejection says nothing of what is missing, so the model has no way to see its next step.",
              "The error is not marked as non-retryable, so the agent's retries are what leads it to give up.",
              "The prompt no longer tells the agent to call `get_customer`, since that rule moved into code.",
              "The block comes at call time, when it is too late in the chat for the agent to change its plan."),
        ans=0,
        explain=("A block helps only if it says what is missing, because Claude reads the rejection and decides what to do next. "
                 "B would stop the retries, but the agent would still never learn that it must verify first. C is not the cause, since the "
                 "agent reads each result and could adapt to a clear reason. D is wrong because a rejected call simply "
                 "returns to the model, which can take another step."),
        scenarios=(1,), points=("1.4:S1",),
        evidence=(Evidence("code:agent-sdk/agent-loop", "a `PreToolUse` hook that rejects a tool call prevents it from executing, and Claude receives the rejection message instead."),),
        qtype="diagnose", level="medium", principle="explicit",
        situation="gate raises a bare 500 and the agent tells customers refunds are down",
        trap="mark the error non-retryable and stop there",
    ),
    MCQ(
        id="Q1.4-13",
        q=("Your research coordinator's `publish_report` is blocked until `verify_citations` passes, and a flag records the pass. "
           "An audit finds that 5% of published reports hold claims with no checked source, though the gate logged a valid pass "
           "for each. In those runs, the last `Edit` timestamp is later than the pass. What is the most effective fix?"),
        opts=("Tell the coordinator through its prompt to run `verify_citations` again after any change to a draft.",
              "Let the gate accept only a pass recorded within the last ten minutes, so that old passes expire.",
              "Save the pass against a hash of that draft, and refuse the call unless the hash still matches.",
              "Run `verify_citations` over published reports each night, and retract any report that fails the check."),
        ans=2,
        explain=("The prerequisite is a verified version of this report, so the pass must be tied to the exact content being "
                 "published. A puts a must-hold step back in a prompt. B narrows the window, yet an edit made inside ten "
                 "minutes still opens the gate. D catches the problem after the report is out."),
        scenarios=(3,), points=("1.4:S1",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 1.4 Skill 1 requires prerequisites that block until the earlier step has completed; no official page covers stale pass state.",
        qtype="fix", level="hard", principle="deterministic",
        situation="report edited after verify_citations passes and the stale flag still opens publish",
        trap="ask the coordinator to re-verify through its prompt",
    ),
    # ---- S2: multi-concern requests ----
    MCQ(
        id="Q1.4-14",
        q=("Your coordinator verifies the customer, splits a message into three concerns and starts three parallel subagents "
           "through the Task tool. Each subagent then calls `get_customer` and asks the customer for an identifier, so "
           "customers are asked three times in one chat. Satisfaction on these chats fell 18 points. What is the most likely "
           "root cause?"),
        opts=("Parallel subagents cannot share one session, so the concerns have to be worked through in sequence.",
              "The subagents need a shared datastore, because a coordinator has no direct way to hand them any data.",
              "The subagents do see the coordinator's history, but they are told to treat every step as unverified.",
              "A subagent knows only what its spawn prompt holds, and the record was not put in those prompts."),
        ans=3,
        explain=("Subagents start without the parent's conversation, so the verified record has to travel in each prompt. A gives "
                 "up the parallel work without supplying the record. B builds infrastructure when the prompt is already a "
                 "direct channel. C has it backwards, since history is not inherited."),
        scenarios=(1,), points=("1.4:S2",),
        evidence=(Evidence("code:agent-sdk/subagents", "The only content you pass from parent to subagent is the Agent tool's prompt string"),),
        qtype="diagnose", level="medium", principle="explicit",
        situation="three parallel subagents each ask the customer to identify themselves again",
        trap="assume subagents see the coordinator's history or need a datastore",
    ),
    MCQ(
        id="Q1.4-15",
        q=("A customer writes that order 512 arrived late and was also overcharged. Two parallel subagents, one per concern, "
           "each have `process_refund` access, and each issues £30. The ledger shows both payments trace to one duplicate "
           "shipping fee. About 5% of multi-concern chats pay twice for one fault, and a trial that ran the two one after "
           "the other changed nothing, since the second subagent never sees what the first did. What is the most "
           "effective fix?"),
        opts=("Give both subagents a `get_refunds` tool, so that each can check what has been paid before it pays.",
              "Limit them to read-only tools, and have the coordinator combine findings before any money moves.",
              "Extend each subagent's prompt with a rule against paying for any fault its sibling already settled.",
              "Run the subagents one after the other, and keep the `process_refund` access each one has today."),
        ans=1,
        explain=("Investigation can run in parallel, but action comes after the findings are combined, which is where the shared "
                 "cause shows up. A leaves a race, since parallel subagents can both check before either pays. C asks each "
                 "subagent to respect work it cannot see. D has no step that compares the findings, and gives up the parallel "
                 "work."),
        scenarios=(1,), points=("1.4:S2",),
        evidence=(Evidence("code:agent-sdk/subagents", "multiple subagents can run concurrently, so independent subtasks finish in the time of the slowest one rather than the sum of all of them."),
                  Evidence("code:agent-sdk/subagents", "The only content you pass from parent to subagent is the Agent tool's prompt string")),
        qtype="fix", level="hard", principle="least_privilege",
        situation="parallel subagents each refund one duplicate shipping fee and pay twice",
        trap="give each subagent a lookup or serialise them, with no synthesis",
    ),
    MCQ(
        id="Q1.4-16",
        q=("A single-label intent classifier sends each support message to one workflow. Reviewing 1,000 chats, you find that 27% "
           "of messages raise two or more concerns, and everything after the labelled one goes unanswered. Label accuracy is "
           "96%. Which redesign best addresses this?"),
        opts=("Retrain the classifier on more multi-topic data, so that it finds the customer's main request more often.",
              "Add combined labels such as refund-and-address, so that the most common pairs have their own workflows.",
              "Have the agent break each message into a list of separate issues, and work every item.",
              "Finish the labelled workflow, then ask the customer if anything else is needed before the chat closes."),
        ans=2,
        explain=("One label cannot describe a message with several issues, so the message has to become a list of items. A "
                 "improves a score that is already fine. B grows a fixed set of pairs that can never cover every mix. D makes "
                 "the customer repeat what they already wrote."),
        scenarios=(1,), points=("1.4:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 1.4 Skill 2 requires decomposing multi-concern requests into distinct items.",
        qtype="choose", level="easy", principle="model_driven",
        situation="single-label intent classifier drops every concern after the first on 27% of messages",
        trap="add combined labels or retrain for accuracy",
    ),
    MCQ(
        id="Q1.4-17",
        q=("Your support agent splits a message into three concerns and starts a subagent for each, in parallel, with the "
           "customer record in every prompt. Each subagent posts its own reply as it finishes. In 21% of these chats the "
           "customer sends a confused follow-up, usually because one reply promises a refund to the card while another says "
           "the same order was cancelled for store credit. Which redesign is best?"),
        opts=("Have subagents return findings to the coordinator, which settles overlaps and sends one reply.",
              "Run the subagents one at a time, so that each reply can refer to what the earlier ones said.",
              "Hold every subagent's reply for a short delay, so that the three replies land together in the chat.",
              "Put all three concerns in each subagent's prompt, so that each can mention the related outcomes."),
        ans=0,
        explain=("Investigating in parallel is fine, but the outcomes must be reconciled in one place before the customer sees "
                 "anything. B still posts separate replies, and each only sees the earlier ones. C changes when the replies "
                 "arrive, not whether they agree. D has three subagents decide on the same outcomes independently, so they "
                 "can still disagree."),
        scenarios=(1,), points=("1.4:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 1.4 Skill 2 ends in a unified resolution; no official page covers support replies.",
        qtype="choose", level="medium", principle="preserve_information",
        situation="parallel subagents each post their own reply and promise conflicting outcomes",
        trap="serialise or delay the replies instead of synthesising",
    ),
    # ---- S3: compiling the handoff summary ----
    MCQ(
        id="Q1.4-18",
        q=("`escalate_to_human` takes one free-text `notes` string. The system prompt lists what a note must contain, yet 18% of "
           "tickets lack the refund amount, and human agents cannot see the transcript to find it. You want every ticket to "
           "carry each item. Which change is most effective?"),
        opts=("Lengthen the tool description, and repeat there the full list of items that each note has to contain.",
              "Ask the agent to write `notes` as a JSON object, with one key for each item that a ticket must carry.",
              "Run a regex over each note after the call, and flag tickets with no amount for a human to fill in.",
              "Replace `notes` with separate required properties, and set `strict: true` on the definition."),
        ans=3,
        explain=("Required properties under strict mode make the content part of the tool's contract, not a request. A adds more "
                 "instructions to a rule that is already missed. B looks structured, but it is still a free string the "
                 "schema does not check. C notices the gap afterwards and leaves the human without the amount."),
        scenarios=(1,), points=("1.4:S3",),
        evidence=(Evidence("api:agents-and-tools/tool-use/strict-tool-use", "Without strict mode, Claude might return incompatible types (`\"2\"` instead of `2`) or omit required fields, breaking your functions and causing runtime errors."),),
        qtype="configure", level="medium", principle="deterministic",
        situation="free-text notes on escalate_to_human lack the amount on 18% of tickets",
        trap="ask for JSON inside the free-text string",
    ),
    MCQ(
        id="Q1.4-19",
        q=("In 6% of escalated tickets, the refund amount differs from the order record: for example, £200 on a £120 order. The "
           "chat logs show that the customer typed the higher figure in each case. Human agents cannot see those chats and "
           "approve what the ticket says. What is the most effective fix?"),
        opts=("Take the figure from the `lookup_order` result, and show the claim as a separate item.",
              "Remove the amount from the handoff, so that a human looks it up afresh for each new ticket.",
              "Have the agent ask the customer to confirm the amount once more before creating the ticket.",
              "Tell the agent through its prompt to add a remark whenever a figure came from the customer."),
        ans=0,
        explain=("The handoff should carry the verified value and keep the customer's claim visible as a claim, so the human sees "
                 "the gap. B throws away a fact the agent already holds and adds work. C confirms the same unverified figure. "
                 "D leaves the wrong number in the amount and depends on the agent remembering a remark."),
        scenarios=(1,), points=("1.4:S3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 1.4 Skill 3 lists the refund amount for humans without the transcript; no official page covers human handoffs.",
        qtype="fix", level="medium", principle="preserve_information",
        situation="handoff amount copied from the customer's claim instead of the order record",
        trap="have the customer confirm the same figure",
    ),
    MCQ(
        id="Q1.4-20",
        q=("Your `escalate_to_human` schema requires `root_cause`. When a customer demands a person in the first message, the "
           "agent escalates at once, as it should, with no investigation done. Audits show that 30% of those tickets state a "
           "cause no tool result supports, and human agents waste time chasing it. How should you resolve this?"),
        opts=("Hold the escalation until the agent has investigated enough to fill `root_cause` with a real finding.",
              "Let the field take an explicit `unknown` value, and say in the prompt that this is acceptable.",
              "Remove `root_cause` from the schema, since a part of the tickets cannot be trusted on this field.",
              "Add a self-reported confidence score beside `root_cause`, so that humans can decide how far to trust it."),
        ans=1,
        explain=("A required field with no honest way to say \"not known\" pushes the model to make something up, so it needs a "
                 "stated way out. A delays a customer who asked for a person. C loses the field for the many tickets where "
                 "the cause is real. D adds a self-reported number to a guess, and the invented text stays on the ticket."),
        scenarios=(1,), points=("1.4:S3", "1.4:K3"),
        evidence=(Evidence("api:test-and-evaluate/strengthen-guardrails/reduce-hallucinations", "Explicitly give Claude permission to admit uncertainty."),),
        qtype="evaluate", level="hard", principle="preserve_information",
        situation="required root_cause field filled with an invented cause on instant escalations",
        trap="delay escalation until the field can be filled",
    ),
)
