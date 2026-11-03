"""Exam bank · TS 1.2. Original questions; see docs/MCQ_BANK_PLAN.md."""
from utils.mcq_sets import MCQ, Evidence

TS = "1.2"
BULLETS = {
    "K1": "Hub-and-spoke: the coordinator manages all communication between subagents, plus error handling and information routing",
    "K2": "Subagents run with isolated context and do not automatically receive the coordinator's conversation history",
    "K3": "The coordinator's job: break the task down, delegate, combine results, and pick subagents according to query complexity",
    "K4": "Decomposition that is too narrow leaves parts of a broad research topic uncovered",
    "S1": "Coordinators that analyse each query and choose which subagents to invoke, instead of always running the full pipeline",
    "S2": "Dividing research scope across subagents, by distinct subtopic or source type, so that they duplicate less work",
    "S3": "Refinement loops: evaluate the synthesis for gaps, re-delegate targeted queries, re-run synthesis until coverage is enough",
    "S4": "Sending all subagent communication through the coordinator for observability, consistent errors and controlled flow",
}

_CHAIN = "Each subagent completes its task and returns results to Claude, which then passes relevant context to the next subagent."
_FAILURE = "A subagent whose run ends on an API error, such as a usage limit or a repeated server error, reports that failure back to Claude."
_PROMPT_ONLY = ("The only content you pass from parent to subagent is the Agent tool's prompt string, so include any file paths, "
                "error messages, or decisions the subagent needs directly in that prompt.")
_BEST = "api:build-with-claude/prompt-engineering/claude-prompting-best-practices"

QUESTIONS = (
    # ---- K1: hub and spoke ----
    MCQ(
        id="Q1.2-01",
        q=("To remove a step, your document analysis subagents now save findings to a shared folder, and the synthesis subagent "
           "reads whatever is there when a 10-minute timer ends. Since the change, 9% of reports silently lack one document. "
           "Synthesis is told how many documents to expect and logs the shortfall, but nothing acts on it. In each case an analysis subagent crashed, and its error appears in that subagent's own log only. What is the most "
           "likely root cause?"),
        opts=('Analysis subagents have no local retry, so one crash ends the work with no second attempt.',
              'Exchanges skip the coordinator, so nothing able to recover ever hears about a failure.',
              'Synthesis is not told how many documents to expect, so a short set looks complete to it.',
              'The 10-minute timer is too short, so synthesis starts before slower analysis runs finish.'),
        ans=1,
        explain=('Crashes stay in one log because the exchange goes around the coordinator, the agent meant to see failures and decide on recovery. A could help with brief faults, but a lasting failure would still go unseen. C is ruled out because synthesis already knows the count and logs the shortfall, yet it cannot re-delegate. D is ruled out because these subagents crashed and would never have delivered.'),
        scenarios=(3,), points=("1.2:K1", "1.2:S4"),
        evidence=(Evidence("code:sub-agents", _CHAIN),),
        qtype="diagnose", level="hard", principle="root_cause",
        situation="analysis subagents drop findings in a shared folder read on a timer and crashes go unseen",
        trap="lengthen the timer or swap the store",
    ),
    MCQ(
        id="Q1.2-02",
        q=("Your support coordinator delegates to billing, returns and account subagents, and each one writes to the customer's chat as it finishes. When `process_refund` fails, customers see billing apologise and returns say the refund is on its way, in the same conversation. About 4% of multi-issue chats are affected. What is the most effective fix?"),
        opts=('Give every subagent read access to the live chat, so that each checks earlier replies before it writes.',
              'Merge billing and returns into one subagent, so that a single agent owns each refund from start to end.',
              'Add a step that compares each new reply with earlier ones and holds any that appears to contradict them.',
              'Return outcomes and errors to the coordinator, and let it compose the one reply that is sent.'),
        ans=3,
        explain=("Handling failures and routing information is the coordinator's job, and it is the one agent that can see all the outcomes. A leaves several agents writing at once, each depending on what has already been posted. B fixes one pair and gives up specialisation. C catches some clashes by adding a checker, while nobody is handling the failed refund."),
        scenarios=(1,), points=("1.2:K1", "1.2:S4"),
        evidence=(Evidence("guide", ""),),
        qtype="fix", level="medium", principle="root_cause",
        situation="billing and returns subagents post contradictory refund messages into one customer chat",
        trap="let each subagent read the live chat",
    ),
    MCQ(
        id="Q1.2-03",
        q=("Your developer assistant has a coordinator and five subagents. An engineer proposes giving each subagent the names of "
           "the others and a tool to message them, so they can agree among themselves who does what. That design has 20 possible "
           "links, and the current one has 5. How should you evaluate the proposal?"),
        opts=('Reject it: a single hub is what keeps routing and failure handling traceable.',
              'Reject it: 20 links will use more tokens per run than the five links use today.',
              'Accept it, and have every message copied to a shared store so nothing goes unseen.',
              'Accept it for the two busiest subagent pairs, and keep the hub for the other three.'),
        ans=0,
        explain=('With a hub, every exchange passes one point that routes it, logs it and handles its failures. B reaches the right decision for a reason the stem does not support. C records the messages, but nobody acts on a failure or controls what each subagent receives. D keeps the same loss of control on the busiest paths.'),
        scenarios=(4,), points=("1.2:K1",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the docs describe chaining through the parent but give no guidance on peer-to-peer designs.",
        qtype="evaluate", level="easy", principle="root_cause",
        situation="proposal to let five dev subagents message each other and divide the work themselves",
        trap="peer messaging with a shared message store",
    ),
    # ---- K2: isolated context ----
    MCQ(
        id="Q1.2-04",
        q=("In a chat with your research coordinator, a user says: \"only use sources from 2022 onward.\" The coordinator "
           "acknowledges this, then spawns search subagents with the prompt \"find evidence on four-day work weeks.\" In 40% of "
           "these runs the findings include sources from before 2022. What is the most likely root cause?"),
        opts=("The chat rule should be in the coordinator's system prompt, which subagents do inherit.",
              'Subagents do read the chat, but they give more weight to the prompt than to old turns.',
              "The spawn prompt omitted the rule; the subagent sees none of the parent's chat or prompt.",
              'The search tool ranks by relevance alone, so older pages keep appearing whatever the request says.'),
        ans=2,
        explain=("A subagent starts fresh, and the spawn prompt shown does not contain the rule. A is wrong because a subagent does not receive the parent's system prompt either. B is wrong because a subagent does not see the parent's conversation at all. D blames the tool, though no date rule was ever passed to it."),
        scenarios=(3,), points=("1.2:K2",),
        evidence=(Evidence("code:agent-sdk/subagents", "its context window starts fresh, with no parent conversation, but isn't empty."),),
        qtype="diagnose", level="easy", principle="explicit",
        situation="user's date rule stated to the coordinator never reaches the search subagents",
        trap="assume subagents inherit the system prompt or chat",
    ),
    MCQ(
        id="Q1.2-05",
        q=("Your support coordinator verifies the customer and finds the order, then spawns a returns subagent with the prompt "
           "\"handle this return.\" In 22% of cases the subagent asks the customer for an order number they already gave, and "
           "the customers complain. What is the most effective fix?"),
        opts=('Include the verified customer ID, order number and request in each spawn prompt.',
              'Tell the returns subagent in its definition not to ask customers to repeat any detail.',
              'Have the subagent call `lookup_order` first, before it asks the customer for anything.',
              "Copy the coordinator's system prompt into the returns subagent's own system prompt."),
        ans=0,
        explain=("The spawn prompt is the only thing passed from coordinator to subagent, so per-case facts go there. B forbids the question and still leaves the subagent without the answer. C cannot work without the order number or customer ID, which is what the subagent lacks. D copies standing instructions and none of this customer's facts."),
        scenarios=(1,), points=("1.2:K2", "1.3:K2"),
        evidence=(Evidence("code:agent-sdk/subagents", _PROMPT_ONLY),),
        qtype="fix", level="easy", principle="explicit",
        situation="returns subagent re-asks customers for an order number the coordinator already verified",
        trap="forbid the question without passing the fact",
    ),
    MCQ(
        id="Q1.2-06",
        q=("Your coordinator's gap check tells it to \"list the pages each search subagent opened\" before deciding what to do "
           "next. The subagents' final reports contain only a findings summary. Audits show 15% of the listed URLs were never "
           "opened by anyone, though each subagent's own transcript looks correct. What is the most likely root cause?"),
        opts=('The search subagents log opened pages under the wrong URL in their own transcripts.',
              "The coordinator's context filled up, so older tool results were dropped before the check.",
              'The coordinator received the tool results, but parallel runs got their URLs mixed up.',
              'Each report is all it receives from a subagent, so it filled the list in by itself.'),
        ans=3,
        explain=("A subagent's tool calls stay inside its own context, so the coordinator had no URLs to list and supplied some itself. The fix is to require the URLs in each final report. A is ruled out, as the transcripts look correct. B assumes the results reached the coordinator, which they never did. C would give real URLs against the wrong subagent, not URLs nobody opened."),
        scenarios=(3,), points=("1.2:K2",),
        evidence=(Evidence("code:agent-sdk/subagents", "Either way, intermediate tool calls and results stay inside the subagent; only its final message returns to the parent."),),
        basis="docs",
        qtype="diagnose", level="hard", principle="preserve_information",
        situation="coordinator lists pages opened by subagents and invents URLs missing from their final reports",
        trap="assume the coordinator can see subagent tool calls",
    ),
    # ---- K3: the coordinator's role ----
    MCQ(
        id="Q1.2-07",
        q=('A legacy audit tool has security, performance and dependency subagents, and the engineer receives their three final reports joined end to end. Reviewers find the same slow query flagged three times, with two conflicting recommendations and no overall priority. Each report is accurate for its own area. Which change is most effective?'),
        opts=("Define one severity scale in all three subagents' prompts, so that the reports rank alike.",
              'Have the coordinator merge the three outputs and settle any conflicts before delivery.',
              'Run the subagents in sequence, so each one sees earlier findings and skips any repeats.',
              'Replace the specialists with one general audit subagent that writes one combined report.'),
        ans=1,
        explain=("Combining results is part of the coordinator's job, and here it is skipped while each specialist does its part. A makes rankings comparable but leaves the duplicates and the conflicting advice. C adds delay to independent work and still leaves nobody to settle a conflict. D gives up the specialisation that made each report accurate."),
        scenarios=(4,), points=("1.2:K3",),
        evidence=(Evidence("code:sub-agents", "Each subagent explores its area independently, then Claude synthesizes the findings."),),
        qtype="choose", level="medium", principle="root_cause",
        situation="audit tool joins three specialist reports with a duplicated finding and conflicting advice",
        trap="shared severity scale or sequential subagents",
    ),
    MCQ(
        id="Q1.2-08",
        q=('Customers often write messages like "refund order 118 and change the address on order 204." Logs for such chats show your support coordinator spawning one subagent with the customer\'s message as its prompt. In 18% of them the refund is done, the address is unchanged, and the case closes as resolved. What is the most effective fix?'),
        opts=('Spawn every subagent with the full message, so that each one can act on its own part.',
              "Broaden the billing subagent's tools, so that it can also make any account changes.",
              'Have the coordinator break out each ask, delegate them, then combine the outcomes.',
              'Check with the customer before closing, so that any open request is caught at that point.'),
        ans=2,
        explain=("Breaking a message into parts, delegating each and combining the outcomes is the coordinator's role, and the logs show one subagent handed everything. A brings back the full pipeline and risks two subagents acting on one request. B over-provisions a specialist. D relies on the customer to find the gap and works against first-contact resolution."),
        scenarios=(1,), points=("1.2:K3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 1.2 Knowledge 3 and TS 1.4 on multi-concern requests; the docs do not discuss this support case.",
        qtype="fix", level="medium", principle="preserve_information",
        situation="two-request support messages go whole to one subagent and the second request is dropped",
        trap="broaden one subagent's tools",
    ),
    MCQ(
        id="Q1.2-09",
        q=("Your research coordinator has the Task tool and also `web_search`, added for quick checks. Its prompt already tells it to delegate searches, yet in 45% of runs it does the "
           "searching itself. Its context then fills with raw pages, and it ends up giving subagents "
           "shorter briefs and losing details from earlier results. Which change best restores its role?"),
        opts=("Strengthen the prompt's delegation wording, and add examples of searches that go to subagents.",
              'Have the coordinator summarise each raw page as soon as its own search returns.',
              'Switch the coordinator to a bigger context window, so that raw pages fit more easily.',
              'Remove `web_search` from the coordinator, so findings come via subagents only.'),
        ans=3,
        explain=("The coordinator should decompose, delegate and combine, and removing the tool makes delegation the only route while keeping raw pages out of its context. A adds more prompt guidance to a rule that already fails 45% of the time, while removing the tool guarantees the route (guidance would be the first step only if no rule existed yet). B spends the coordinator's context on a specialist's work. C leaves it doing that work too, with more room."),
        scenarios=(3,), points=("1.2:K3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 1.2 Knowledge 3 on the coordinator delegating; the docs quote only supports context hygiene.",
        qtype="choose", level="hard", principle="least_privilege",
        situation="coordinator with its own web_search stops delegating and fills its context with raw pages",
        trap="strengthen a prompt rule that already fails",
    ),
    # ---- K4: overly narrow decomposition ----
    MCQ(
        id="Q1.2-10",
        q=("An engineer asks your code exploration agent to \"find everywhere we store customer email addresses.\" The coordinator's "
           "log shows three assignments: the users service, the orders service and the billing service. All three subagents "
           "report accurately. A compliance review later finds the addresses also sit in nightly export jobs and in a support "
           "tool. What is the most likely root cause?"),
        opts=("Those places appear in none of the assignments, so nobody was sent to search them.",
              "The explorer subagents' `Grep` patterns were too strict to match the address fields in other code.",
              "The summary step discarded the matches found in the export jobs before it reached the engineer.",
              "The explorer subagents use too small a model to follow references out of their assigned services."),
        ans=0,
        explain=("The log shows the gap in the assignments: nobody was asked to look outside three services, while each subagent did "
                 "its own job well. B blames patterns that were never run on that code. C assumes matches existed, but no agent "
                 "searched there. D expects a subagent to go beyond its brief, which is the wrong place for scope to be set."),
        scenarios=(4,), points=("1.2:K4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the docs do not discuss narrow decomposition; TS 1.2 Knowledge 4.",
        qtype="diagnose", level="medium", principle="root_cause",
        situation="data audit scoped to three services misses export jobs and a support tool",
        trap="blame Grep patterns in code nobody searched",
    ),
    MCQ(
        id="Q1.2-11",
        q=('Reports on "how cities adapt to extreme heat" cover tree canopy and cool roofs but not health, housing or water. Your lead proposes doubling search subagents from 3 to 6. In a trial, sources rose from 40 to 85, and the coordinator\'s log listed subtasks such as street trees, roof coatings and canopy surveys; 2 of 8 expected areas were covered, as before. How should you evaluate the proposal?'),
        opts=('Accept it, and add a gap check in synthesis to flag areas that remain missing.',
              'Accept it, and let synthesis fill any remaining gaps from general knowledge.',
              'Reject it: extra agents do not help while the assigned subtasks stay this narrow.',
              "Reject it: widen each search subagent's queries so that each covers all eight areas."),
        ans=2,
        explain=('Doubling the agents doubled the sources and left coverage at 2 of 8, and the log shows why: every subtask sits in the same two areas. A only reports the gap after paying for six agents. B fills it with unsourced text. D makes subagents stray beyond their assignments and leaves the decomposition as it was.'),
        scenarios=(3,), points=("1.2:K4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the docs do not discuss narrow decomposition; TS 1.2 Knowledge 4.",
        qtype="evaluate", level="hard", principle="root_cause",
        situation="doubling search subagents doubles sources but leaves heat adaptation coverage at 2 of 8 areas",
        trap="add more subagents for coverage",
    ),
    MCQ(
        id="Q1.2-12",
        q=("Your research system's dashboard shows 99% subtask success, yet readers rate 30% of reports as incomplete. A sample shows "
           "those reports omit whole areas that the request named. Your manager wants to know whether the system is healthy. "
           "How should you evaluate it?"),
        opts=('Review a sample of subagent outputs for accuracy, and treat it as healthy if they hold up.',
              "Score each report against its request's areas; subtask success does not measure scope.",
              'Have each subagent rate its own completeness, then average that into a coverage figure.',
              'Track sources per report, as a high count would suggest that coverage is sufficient.'),
        ans=1,
        explain=('Subtasks can all succeed while the set of subtasks misses part of the request, so coverage must be measured against the request itself. A checks the quality of assigned work, which may be fine. C uses self-assessment, and a subagent cannot see what it was never assigned. D counts volume, which can pile up in one narrow area.'),
        scenarios=(3,), points=("1.2:K4", "1.2:S3"),
        evidence=(Evidence("guide", ""),),
        qtype="evaluate", level="medium", principle="independent_check",
        situation="dashboard shows 99% subtask success while readers rate 30% of reports incomplete",
        trap="read subtask success as coverage",
    ),
    # ---- S1: dynamic selection ----
    MCQ(
        id="Q1.2-13",
        q=("Your support coordinator's prompt lists the billing, returns and account subagents as the standard handling for a ticket. Finance finds that 2% of billing-only tickets led to return labels nobody asked for. The traces show the returns subagent locating the order and starting a return, as its own instructions say. What is the root cause?"),
        opts=('Billing did not tell the returns subagent that no return was needed for this ticket.',
              "The returns subagent's `description` is too vague for it to recognise its own tickets.",
              'The coordinator invokes returns without checking that the request involves one.',
              "The returns subagent's model misjudges these tickets, so a stronger model is needed."),
        ans=2,
        explain=("The returns subagent acted correctly on a ticket it should not have received, so the coordinator needs to choose by what each ticket requires. A adds a link between subagents to patch the routing. B is wrong because a `description` guides the coordinator's choice, and this coordinator follows a standing list. D blames a model that did what it was told."),
        scenarios=(1,), points=("1.2:S1",),
        evidence=(Evidence("guide", ""),),
        qtype="diagnose", level="easy", principle="model_driven",
        situation="fixed billing-returns-account chain creates unrequested return labels on billing tickets",
        trap="make subagents warn each other",
    ),
    MCQ(
        id="Q1.2-14",
        q=("A classifier labels each query simple or complex before your coordinator starts, and the label fixes the subagent list "
           "for that run. In 12% of simple runs, the search results reveal conflicting figures, but analysis is not on the list, "
           "so the report just states one figure. Which design best addresses this?"),
        opts=("Retrain the classifier on more examples, so that fewer of these queries are labelled as simple.",
              "Add a third, medium label to the classifier with its own fixed list of subagents for the run.",
              "Run all four subagents on every query, so that analysis is never left out when it is needed.",
              "Let the coordinator pick each next subagent from what the latest result actually showed."),
        ans=3,
        explain=("The need for analysis only became visible in the search results, so the choice has to be made as results arrive. A and "
                 "B still decide before any result exists. C brings back the full pipeline, with its cost on every simple query."),
        scenarios=(3,), points=("1.2:S1", "1.1:K3"),
        evidence=(Evidence("guide", ""),),
        qtype="choose", level="medium", principle="model_driven",
        situation="upfront complexity label fixes subagents and analysis misses conflicts found by search",
        trap="retrain the classifier or add a third label",
    ),
    MCQ(
        id="Q1.2-15",
        q=("Since a model upgrade, your developer agent's coordinator spawns two subagents for single-file edits that one tool call "
           "could finish, and those tasks now take four times as long. It still does well on wide multi-service investigations, "
           "where delegation clearly helps. What should you configure first?"),
        opts=("Add guidance to the coordinator on when to delegate and when to work directly.",
              "Remove the Task tool from `allowedTools`, so that the coordinator can never spawn.",
              "Set a low `maxTurns` on each subagent definition, so that the spawned runs end sooner.",
              "Build a router in code that counts files in each request and picks a path from that."),
        ans=0,
        explain=("Telling the coordinator when subagents are and are not warranted keeps wide investigations and stops small ones "
                 "being delegated, and it is the smallest change. B removes the delegation you want to keep. C cuts subagents short "
                 "but they still spawn. D adds a layer of infrastructure before the simple fix has been tried."),
        scenarios=(4,), points=("1.2:S1", "1.2:K3"),
        evidence=(Evidence(_BEST, "If you’re seeing excessive subagent use, add explicit guidance about when subagents are and aren’t warranted:"),),
        basis="docs",
        qtype="configure", level="medium", principle="proportionate",
        situation="after an upgrade the coordinator spawns two subagents for single-file edits",
        trap="remove the Task tool or build a file-count router",
    ),
    # ---- S2: partitioning ----
    MCQ(
        id="Q1.2-16",
        q=("A user asks what one new port-fee regulation means for shippers. The question is too narrow to split into subtopics, so "
           "your three search subagents get the same brief, and 75% of the pages they return are shared. Primary filings are "
           "barely represented. What is the best way to divide this work?"),
        opts=("Give each subagent a differently worded version of the same question, so that their results differ.",
              "Assign each subagent a source type, such as official filings, academic papers and trade press.",
              "Raise each subagent's results limit, so that the shared pages form a smaller share of the total.",
              "Remove duplicate pages after the search step, and pass the unique pages on to the analysis agent."),
        ans=1,
        explain=("When a topic has no natural subtopics, source type is another way to give each agent distinct ground, and it brings in "
                 "the missing filings. A still lands on the same top pages. C adds volume without separating the work. D cleans up "
                 "after the wasted effort and does nothing about the missing primary sources."),
        scenarios=(3,), points=("1.2:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 1.2 Skill 2 names source types as a way to divide scope; the docs do not cover this.",
        qtype="choose", level="easy", principle="fit_for_purpose",
        situation="narrow regulation question has no subtopics and three subagents return the same pages",
        trap="reword the same brief for each subagent",
    ),
    MCQ(
        id="Q1.2-17",
        q=("To document how services handle retries, your coordinator spawns four explorer subagents with the same brief: \"survey "
           "retry logic in this monorepo.\" All four start at the top of the repository, and 65% of the files they read are read "
           "by more than one. Two services at the edge of the tree are never reached. What is the most effective fix?"),
        opts=("Have subagents note each file in a shared list, so that the others can skip it as they go along.",
              "Raise `maxTurns` on the four subagents, so that each one can work its way out to the edge of the tree.",
              "Tell every subagent in its prompt to avoid any files the others have probably already read.",
              "Have the coordinator list the services and assign each subagent its own distinct group."),
        ans=3,
        explain=('Dividing the repository up front removes the overlap and gives every service an owner. A adds a channel outside the coordinator, and all four still start from the same brief. B lets the agents keep duplicating each other for longer. C asks a subagent to guess at work it cannot see, since subagents share no context.'),
        scenarios=(4,), points=("1.2:S2",),
        evidence=(Evidence("code:sub-agents", "Research the authentication, database, and API modules in parallel using separate subagents"),),
        qtype="fix", level="medium", principle="explicit",
        situation="four explorers with one monorepo brief reread the same files and miss edge services",
        trap="shared list of files already read",
    ),
    MCQ(
        id="Q1.2-18",
        q=("Your three search subagents overlap by about 50%. An engineer proposes running them one after another and pasting each "
           "one's results into the next one's prompt, with \"don't repeat these.\" Overlap would fall, but each search takes "
           "about 50 seconds, and the three areas of the topic are independent. How should you evaluate the proposal?"),
        opts=("Accept it, because seeing earlier results is the only way a subagent can avoid repeating them.",
              "Accept it, since 150 seconds is a fair price for cleaner input to synthesis.",
              "Reject it: dividing the scope up front removes the overlap and lets the three run in parallel.",
              "Reject it, and instead let the subagents run as now and remove all duplicates after they finish."),
        ans=2,
        explain=('The areas are independent, so distinct assignments remove the overlap and keep the phase at about 50 seconds, not 150. A is wrong because a good partition prevents repeats with no sharing at all. B accepts a threefold delay that distinct assignments make unnecessary. D still pays for the duplicated searches.'),
        scenarios=(3,), points=("1.2:S2",),
        evidence=(Evidence("code:agent-sdk/subagents", "multiple subagents can run concurrently, so independent subtasks finish in the time of the slowest one rather than the sum of all of them."),),
        qtype="evaluate", level="medium", principle="proportionate",
        situation="proposal to serialise independent searches and paste prior results to reduce overlap",
        trap="sequential runs in place of a partition",
    ),
    # ---- S3: refinement loops ----
    MCQ(
        id="Q1.2-19",
        q=("Your coordinator repeats search and synthesis until the synthesis subagent ends its draft with `COVERAGE: COMPLETE`. "
           "Runs stop after one round about 90% of the time, yet an audit finds that 30% of final reports miss an area named in "
           "the request. What is the most effective change?"),
        opts=("Have the coordinator judge each draft against the request, looping until all is covered.",
              "Require the synthesis subagent to justify its `COVERAGE: COMPLETE` line in a few sentences.",
              "Run exactly three rounds on every request, whatever the state of the draft after each round.",
              "Tighten the parser so that the marker counts only when it stands alone on the final line."),
        ans=0,
        explain=("The coordinator should judge the draft against the request instead of accepting a self-report in free text, and the "
                 "criteria then decide when to stop. B improves the wording of the same self-assessment. C replaces the signal with a "
                 "fixed count, which wastes rounds on easy topics and can stop early on hard ones. D polishes the parsing of a signal "
                 "that is wrong in the first place."),
        scenarios=(3,), points=("1.2:S3",),
        evidence=(Evidence("guide", ""),),
        qtype="choose", level="medium", principle="independent_check",
        situation="refinement loop stops on the synthesis subagent's own COVERAGE COMPLETE marker",
        trap="fixed three rounds or a tighter marker parser",
    ),
    MCQ(
        id="Q1.2-20",
        q=("Your coordinator is writing a guide to a legacy payments module. It notices that the draft says nothing on retry "
           "handling, so it respawns the explorer with \"look deeper and find more.\" The second pass reads 80% of the same "
           "files and adds nothing, and this happens on most gaps. What is the most effective fix?"),
        opts=("Raise the explorer's turn limit, so that a deeper pass can reach more of the module's files.",
              "State the specific gap and the files already covered in the new prompt to the explorer.",
              "Spawn three explorers with the same \"look deeper\" prompt, to widen what the pass can find.",
              "Have the writing subagent fill in the retry section from what it knows of payment systems."),
        ans=1,
        explain=("A re-delegation should be a targeted query, and a new explorer knows only its prompt, so the prompt must name the gap "
                 "and what was already read. A gives more turns to an aimless brief. C runs the same vague brief three times. D writes "
                 "unsourced content into the guide instead of closing the gap."),
        scenarios=(4,), points=("1.2:S3", "1.3:K2"),
        evidence=(Evidence("code:agent-sdk/subagents", _PROMPT_ONLY),),
        qtype="fix", level="medium", principle="explicit",
        situation="coordinator respawns an explorer with look deeper and the retry-handling gap stays open",
        trap="more turns or more explorers on a vague brief",
    ),
    MCQ(
        id="Q1.2-21",
        q=('Your refinement loop finds strong new material on a missing area in round two, and the coordinator spawns synthesis again, passing the new findings. The new draft covers the gap well, but 60% of the round-one citations are gone and two earlier sections have vanished. What is the most likely root cause?'),
        opts=('The round-two sources were so strong that synthesis chose to discount all earlier ones.',
              "The synthesis subagent's `max_tokens` is too low, so its output stopped before the rest.",
              "The new run knows only its prompt, which held none of the first round's material.",
              "The coordinator's context overflowed, so its copy of the first draft had been removed."),
        ans=2,
        explain=('Each spawned subagent knows only its prompt, so a re-run of synthesis needs all the findings, old and new. A has no support in the stem, and synthesis had no earlier sources in front of it to discount. B would cut off the end of a draft, not remove citations throughout. D does not explain it, because the stem shows only the new findings being passed.'),
        scenarios=(3,), points=("1.2:S3", "1.3:K2"),
        evidence=(Evidence("code:agent-sdk/subagents", "its context window starts fresh, with no parent conversation, but isn't empty."),),
        qtype="diagnose", level="medium", principle="preserve_information",
        situation="round-two synthesis gets only new findings and drops round-one citations and sections",
        trap="blame max_tokens for missing sections",
    ),
    # ---- S4: routing through the coordinator ----
    MCQ(
        id="Q1.2-22",
        q=("Your support coordinator uses the fraud subagent's internal risk score to decide on escalation, and the reply-drafting subagent reads the same results feed. A reviewer finds that 1 in 300 customer replies quotes the score. A prompt rule against mentioning it cut the rate by half, but not to zero. What is the most effective fix?"),
        opts=('Strengthen the prompt rule with few-shot examples of replies that do not mention the score at all.',
              'Scan each reply for the word "score" in code, and send any matching reply back to be drafted again.',
              "Remove the score from the fraud subagent's results, so that no agent has it to quote.",
              'Send fraud results to the coordinator, which gives the drafter only what a reply needs.'),
        ans=3,
        explain=('Routing through the coordinator controls what each subagent receives, so the drafter cannot quote a score it never gets. A adds more of a prompt approach that has already fallen short. B catches one word, not the many ways to express a score. C also takes the score away from the coordinator, which needs it to decide on escalation.'),
        scenarios=(1,), points=("1.2:S4",),
        evidence=(Evidence("guide", ""),),
        qtype="fix", level="hard", principle="least_privilege",
        situation="reply drafter shares the fraud results feed and quotes an internal risk score",
        trap="stronger prompt rule or word scan",
    ),
    MCQ(
        id="Q1.2-23",
        q=("Over time your research system gained three direct subagent-to-subagent calls, each with its own failure logic. In one "
           "incident, analysis retried a dead search endpoint 40 times while synthesis gave up after one failure on the same "
           "endpoint, and neither event reached the coordinator's logs. What is the most effective fix?"),
        opts=("Remove the direct calls, so that failures reach the coordinator and it applies one policy.",
              "Copy the same retry settings into all three direct calls, and keep the calls where they are.",
              "Add a shared retry library for the subagents, and have it send an alert after 40 failed tries.",
              "Tell each subagent, in its prompt, to give up after a sensible number of failed attempts."),
        ans=0,
        explain=("Failure policy differs because three places own it, and the coordinator cannot see any of them; sending the traffic "
                 "through the hub fixes both. B aligns the numbers today, but the calls stay invisible and will drift apart. C makes "
                 "the retries uniform and still leaves the coordinator unable to decide on recovery. D swaps code for a vague prompt "
                 "rule."),
        scenarios=(3,), points=("1.2:S4", "1.2:K1"),
        evidence=(Evidence("code:sub-agents", _FAILURE),),
        qtype="fix", level="medium", principle="root_cause",
        situation="three direct subagent calls have different retry logic invisible to the coordinator",
        trap="copy retry settings across the direct calls",
    ),
    MCQ(
        id="Q1.2-24",
        q=("Your developer assistant's subagents communicate only through the coordinator. Support engineers now need a trace for "
           "each run showing which subagents ran, what each was asked and what came back. Which approach is simplest and most "
           "reliable?"),
        opts=("Ask each subagent to end its final message with a summary of what it was asked and what it did.",
              "Record each Task call and its returned result at the coordinator, as all of them pass through it.",
              "Turn on a log inside each subagent, and join the files afterwards using a run ID.",
              "Parse the coordinator's final answer afterwards to work out which subagents must have contributed."),
        ans=1,
        explain=('Because all communication passes through the coordinator, one logging point there captures every prompt and result in code. A depends on what each subagent chooses to report. C works, but needs a log and a join for every subagent when one point already sees everything. D infers events from prose and will miss subagents whose work was not quoted.'),
        scenarios=(4,), points=("1.2:S4",),
        evidence=(Evidence("code:sub-agents", "When subagents complete, their results return to your main conversation."),),
        qtype="configure", level="easy", principle="independent_check",
        situation="support engineers need a per-run trace of what each subagent was asked and returned",
        trap="rely on subagents to report on themselves",
    ),
)
