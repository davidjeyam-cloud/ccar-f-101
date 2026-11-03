"""Exam bank · TS 1.3. Original questions; see docs/MCQ_BANK_PLAN.md."""
from utils.mcq_sets import MCQ, Evidence

TS = "1.3"
BULLETS = {
    "K1": "The Task tool is how subagents are spawned, and a coordinator's allowedTools has to include it",
    "K2": "Subagents get context only through their prompt: nothing is inherited from the parent or kept between invocations",
    "K3": "AgentDefinition settings per subagent type: description, system prompt and tool restrictions",
    "K4": "Forking a session to explore different approaches from one shared analysis baseline",
    "S1": "Putting the complete findings of earlier agents directly into the next subagent's prompt",
    "S2": "Structured formats that keep content apart from metadata such as URLs, document names and pages, so attribution survives",
    "S3": "Parallel subagents: several Task calls in one coordinator response, not one per turn",
    "S4": "Coordinator prompts that set goals and quality criteria, not step-by-step procedures, so subagents can adapt",
}

QUESTIONS = (
    # ---- K1: the Task tool and allowedTools ----
    MCQ(
        id="Q1.3-01",
        q=("A research coordinator on the Agent SDK has so far worked alone with `allowedTools: [\"WebSearch\", \"Read\"]`. You are "
           "adding two specialists, `web-search` and `doc-analysis`, and the coordinator should decide for itself when to use "
           "them. Which configuration is correct?"),
        opts=("Define both under `agents`, and put \"Task\" in the `tools` list of each of those two definitions.",
              "Define both under `agents`, and add \"Task\" to the coordinator's `allowedTools` list.",
              "Define both under `agents`, and add `web-search` and `doc-analysis` to the `allowedTools` list.",
              "Describe both specialists in the coordinator's system prompt, and leave the current options as they are."),
        ans=1,
        explain=("A definition makes a subagent available, and the coordinator starts it through the spawning tool. The guide expects "
                 "that tool, Task, in the coordinator's `allowedTools`, and the docs list it there to auto-approve it; the docs "
                 "call the tool `Agent`. A puts the spawning tool on the specialists, not on the agent that delegates. C lists "
                 "agent names, but `allowedTools` holds tool names. D has no definitions, so the coordinator has nothing "
                 "to spawn by name."),
        scenarios=(3,), points=("1.3:K1",),
        evidence=(Evidence("code:agent-sdk/subagents", "Define subagents directly in your code using the `agents` parameter. Claude invokes subagents through the `Agent` tool."),),
        qtype="configure", level="medium", principle="explicit",
        situation="solo research coordinator gains two specialists and needs the right options",
        trap="list subagent names in allowedTools",
    ),
    MCQ(
        id="Q1.3-02",
        q=("The acceptance test for a code-migration agent passes when its final message names the `security-reviewer` subagent. "
           "A spot check of 40 passing runs finds 9 where that message says the reviewer approved the change, yet no output from "
           "any reviewer exists in the run. How should the test change?"),
        opts=("Require the final message to quote the reviewer's verdict word for word before the test will pass.",
              "Have the reviewer end its reply with a fixed token, and check the final message for that token.",
              "Add a second model call that judges whether the final message sounds like real delegation took place.",
              "Check the message stream for a spawn tool call with that `subagent_type`, not the wording."),
        ans=3,
        explain=("A subagent only runs when the agent makes the spawn call, so that structured event is the evidence; the docs say "
                 "to match both names, `Agent` and `Task`. A and B still read text the main agent writes, and an agent that can "
                 "claim an approval can also write a quote or a token. C has one model grade another's wording, and the "
                 "run's record already holds the fact."),
        scenarios=(4,), points=("1.3:K1",),
        evidence=(Evidence("code:agent-sdk/subagents", "Claude invokes subagents through the Agent tool. To detect when a subagent is invoked, check for `tool_use` blocks where `name` is `\"Agent\"`."),),
        basis="docs",
        qtype="evaluate", level="medium", principle="independent_check",
        situation="final message claims a reviewer approved in 9 of 40 runs with no reviewer output",
        trap="demand a quote or token in the final text",
    ),
    MCQ(
        id="Q1.3-03",
        q=("While debugging, a developer added \"Task\" to the `tools` list of all five subagents in a research system. Before the "
           "change a run made about 6 spawns. Now it makes about 30, run trees go three levels deep, and the coordinator's "
           "own log accounts for only 6 of them, so failures deeper down are invisible to it. What is the most effective fix?"),
        opts=("Take the spawning tool off the five definitions, so that only the coordinator holds it.",
              "Keep the lists, and set `max_budget_usd` so that a run stops before the tree can grow very large.",
              "Keep the lists, and tell every subagent through its system prompt to finish tasks without delegating.",
              "Keep the lists, and add a hook that copies each nested spawn into the coordinator's log for review."),
        ans=0,
        explain=("Giving a subagent the spawning tool lets it delegate on its own, so work leaves the coordinator's view; removing "
                 "the tool restores one hub and takes away a capability the subagents never needed. B caps the bill and leaves the "
                 "nesting. C asks a prompt to hold back a capability the agent still has. D improves the log, but the coordinator "
                 "still does not control or handle that work."),
        scenarios=(3,), points=("1.3:K1", "1.2:S4"),
        evidence=(Evidence("code:sub-agents", "In a subagent definition, listing `Agent` in `tools` lets that subagent spawn subagents of its own while the [depth limit](#let-subagents-spawn-their-own-subagents) allows it"),),
        qtype="fix", level="hard", principle="least_privilege",
        situation="spawn count jumps from 6 to 30 and run trees reach three levels",
        trap="cap budget or log nested spawns while subagents keep the tool",
    ),
    # ---- K2: nothing is inherited ----
    MCQ(
        id="Q1.3-04",
        q=("A support coordinator spawns `policy-check`, which reports that a warranty exception applies to the customer. Minutes "
           "later it spawns `policy-check` again with the prompt \"Given the exception you found, work out the replacement "
           "option.\" The second run repeats the policy lookups and says it has no record of any exception. "
           "Which change is best?"),
        opts=("Add the exception to the coordinator's system prompt, where each later spawn is able to read it.",
              "Add the exception to the `description` in the `policy-check` definition before spawning it again.",
              "Write out the exception and its details in the text of the second spawn request.",
              "Extend the prompt with an instruction to recall earlier results before starting any new lookups."),
        ans=2,
        explain=("A new invocation shares no memory with the last one, so what it needs has to travel in its own prompt. A fails "
                 "because a subagent does not receive the parent's system prompt. B changes what the coordinator reads when "
                 "choosing an agent, not the subagent's working context. D asks it to recall something it never had."),
        scenarios=(1,), points=("1.3:K2",),
        evidence=(Evidence("code:agent-sdk/subagents", "The only content you pass from parent to subagent is the Agent tool's prompt string, so include any file paths, error messages, or decisions the subagent needs directly in that prompt."),
                  Evidence("code:agent-sdk/subagents", "The parent's system prompt")),
        qtype="diagnose", level="medium", principle="explicit",
        situation="second policy-check spawn has no record of the exception the first one found",
        trap="put the fact in the coordinator's system prompt",
    ),
    MCQ(
        id="Q1.3-05",
        q=("In a 200-package monorepo, a developer and the main agent spend ten minutes narrowing a flaky test down to one race. "
           "The agent then delegates with \"Fix the race we found.\" The subagent runs for 18 minutes, reads 60 files and "
           "patches a different lock in another package. Which change is most effective?"),
        opts=("Write the file, failing test and agreed diagnosis into the delegation message itself.",
              "Record each bug under investigation in the project CLAUDE.md, so that every subagent loads it.",
              "Run the subagent on a more capable model, so that it can trace the same race on its own.",
              "Limit the subagent's `tools` to `Read` and `Edit`, so that it has fewer ways of wandering off."),
        ans=0,
        explain=("The subagent saw none of that ten-minute discussion, and the delegation message is the only way to hand it over. "
                 "B misuses a file for standing project rules to carry one task's state. C asks a better model to rediscover "
                 "what is already known. D narrows what the subagent can do, and it still does not know where the race is."),
        scenarios=(4,), points=("1.3:K2",),
        evidence=(Evidence("code:sub-agents", "Each subagent starts with a fresh, isolated context window. It doesn't see your conversation history, the skills you've already invoked, or the files Claude has already read."),),
        qtype="fix", level="easy", principle="explicit",
        situation="delegated race fix patches a different lock after ten minutes of diagnosis in chat",
        trap="store task state in CLAUDE.md",
    ),
    MCQ(
        id="Q1.3-06",
        q=("Your migration subagent obeys every naming rule in the project CLAUDE.md. Earlier in the session an engineer told the "
           "main agent to target only the v2 payments client, and the main agent agreed. Given the prompt \"Migrate the checkout "
           "module\", the subagent used v1 in 5 of 12 files. What best explains this mix of behaviour?"),
        opts=("CLAUDE.md outranks instructions given in conversation whenever the subagent finds that the two of them disagree.",
              "The instruction was dropped when the main conversation compacted, so it never reached any later agent.",
              "The subagent did inherit the session history, and it gave that history less weight than its system prompt.",
              "Project memory loads at subagent start, while chat decisions travel only inside the spawn prompt."),
        ans=3,
        explain=("A non-fork subagent starts with its own prompt, tool definitions and project CLAUDE.md, but not the parent's "
                 "conversation, and this spawn prompt never mentioned v2. A invents a conflict, since CLAUDE.md says nothing on the "
                 "client version. B blames compaction, which nothing in the stem shows. C is the common misreading: no history "
                 "was inherited to weigh."),
        scenarios=(4,), points=("1.3:K2",),
        evidence=(Evidence("code:agent-sdk/subagents", "The parent's conversation history or tool results"),
                  Evidence("code:agent-sdk/subagents", "Project CLAUDE.md (loaded via")),
        basis="docs",
        qtype="diagnose", level="hard", principle="root_cause",
        situation="subagent keeps CLAUDE.md naming rules but misses a v2-only decision from the chat",
        trap="assume it inherited history and weighed it low",
    ),
    # ---- K3: AgentDefinition ----
    MCQ(
        id="Q1.3-07",
        q=("A support system defines `billing-specialist` and `account-specialist`, and both have the description \"Helps customers "
           "with their account issues.\" Their system prompts are detailed and accurate. In 22% of spawns the coordinator picks "
           "the wrong one: a duplicate charge goes to `account-specialist`, for example. What is the most effective fix?"),
        opts=("Add routing examples to each specialist's system prompt, showing which requests belong to it.",
              "Rewrite each description to say which requests it takes and which it leaves to the other.",
              "Add a keyword table to the coordinator's prompt that maps common phrases to a specialist.",
              "Add a small classifier in code that chooses the specialist before the coordinator ever runs."),
        ans=1,
        explain=("The coordinator chooses from the descriptions, and these two are identical, so distinct ones are the direct fix. A "
                 "is the near miss: a system prompt is read only after the specialist has been spawned, too late to affect the choice. "
                 "C keeps the vague descriptions and adds a phrase list that fails on new wordings. D is extra machinery "
                 "before the simple fix has been tried."),
        scenarios=(1,), points=("1.3:K3",),
        evidence=(Evidence("code:sub-agents", "Make each description specific enough to route to the right subagent"),),
        qtype="fix", level="medium", principle="explicit",
        situation="billing and account specialists share one description and 22% of spawns go wrong",
        trap="put routing examples in the subagent's system prompt",
    ),
    MCQ(
        id="Q1.3-08",
        q=("Your `doc-auditor` subagent's definition has a description and a system prompt only. The prompt says \"Report problems; "
           "never change files.\" Across 500 runs, 11 contain an `Edit` call. A new policy says this agent must be unable to "
           "alter a file. Which change meets the policy?"),
        opts=("Add few-shot examples to the prompt that show the auditor reporting a problem and leaving the file alone.",
              "Take `Edit` off the coordinator's `allowedTools` list, so that the call is no longer approved.",
              "Set the definition's `tools` field to `Read`, `Grep` and `Glob`.",
              "Repeat the rule in the `description`, so that it is stated in both parts of the definition."),
        ans=2,
        explain=("With `tools` omitted, a subagent gets every tool available to subagents, while a tool left off the list is not in "
                 "its session at all. A is still a prompt, and the policy says unable. B misreads `allowedTools`, which approves "
                 "calls and does not remove tools. D only restates the rule in text that does not bind it."),
        scenarios=(4,), points=("1.3:K3",),
        evidence=(Evidence("code:agent-sdk/subagents", "A tool you leave out isn't in the subagent's session at all: Claude works without it, with no permission prompt or error."),),
        qtype="configure", level="easy", principle="least_privilege",
        situation="doc-auditor with no tools field makes 11 Edit calls in 500 runs",
        trap="remove Edit from the coordinator's allowedTools",
    ),
    MCQ(
        id="Q1.3-09",
        q=("A developer moves a 60-line review checklist into the `description` of `contract-analyzer`, leaving its `prompt` as "
           "\"You review documents.\" The coordinator now selects this agent reliably, but its reviews cover a few items in no "
           "consistent order. The coordinator's spawn prompts do not mention the checklist. What is the most likely cause?"),
        opts=("Long descriptions are cut off at a fixed length, so only the first few checklist items are kept.",
              "The coordinator's system prompt is inherited by the subagent and overrides what the checklist asks for.",
              "Definitions are ignored once a subagent is running, so the checklist belongs in each spawn request.",
              "`description` serves the choice of agent, while the agent's working instructions come from `prompt`."),
        ans=3,
        explain=("The description tells the coordinator when to use the agent, and the `prompt` field is the agent's system prompt, "
                 "which here is one vague line. A invents a cut-off; the selection improved, and the docs state no such rule. B is "
                 "false, since the parent's system prompt is not passed down. C is false, because the definition's `prompt` does "
                 "reach the subagent."),
        scenarios=(3,), points=("1.3:K3",),
        evidence=(Evidence("code:agent-sdk/subagents", "Natural language description of when to use this agent"),
                  Evidence("code:agent-sdk/subagents", "The agent's system prompt defining its role and behavior")),
        qtype="diagnose", level="medium", principle="fit_for_purpose",
        situation="review checklist placed in description and the agent still reviews loosely",
        trap="blame a description length limit",
    ),
    # ---- K4: fork-based sessions ----
    MCQ(
        id="Q1.3-10",
        q=("After a 40-minute analysis of 30 supplier filings in one SDK session, a script produces two report drafts, one on cost "
           "risk and one on legal risk. It passes `resume` with the analysis session ID for the cost draft, then does the same "
           "for the legal draft. The legal draft keeps referring to conclusions from the cost draft. What should the script "
           "do on next month's run?"),
        opts=("Use `continue` for the legal draft, so that it picks up from the latest session in the directory.",
              "Set `fork_session` on both draft runs, so that each one branches from the analysis.",
              "Spawn two fresh subagents for the drafts, and include the analysis session ID in their prompts.",
              "Keep `resume`, and add a line to the legal request telling it to ignore the cost draft."),
        ans=1,
        explain=("Resume adds to the same session, so the second draft inherits the first, while a fork starts from a copy and "
                 "leaves the original unchanged. A also adds to that same session. C gives the subagents an ID and no analysis, "
                 "since a session ID in a prompt loads nothing. D asks the model to set aside text that is still in "
                 "its history."),
        scenarios=(3,), points=("1.3:K4",),
        evidence=(Evidence("code:agent-sdk/sessions", "**Fork** is different: it creates a new session that starts with a copy of the original's history. The original stays unchanged."),),
        qtype="diagnose", level="medium", principle="fit_for_purpose",
        situation="legal draft repeats cost draft conclusions after two resumes of one session",
        trap="tell the second draft to ignore the first",
    ),
    MCQ(
        id="Q1.3-11",
        q=("Mid-way through a long session, an engineer has mapped how a reporting service works and is building a nightly export. "
           "She wants to find out whether event-driven exports are workable. That trial may take days, and the current line "
           "of work must carry on meanwhile, with both keeping everything learned so far. Which approach fits?"),
        opts=("Open a second terminal, and resume the same session ID there for the event-driven trial.",
              "Delegate the trial to a subagent, and give it a one-page summary of the service in its prompt.",
              "Fork the session, then work each line under its own session ID.",
              "Finish the export first in this session, then use it for the trial once that work is done."),
        ans=2,
        explain=("A fork gives two independent sessions that hold the same history and can each be picked up separately. A adds "
                 "both lines to one session, so they would mix. B starts from a summary, not from everything learned, and "
                 "a subagent does not fit days of back-and-forth. D breaks the requirement that both go on at once."),
        scenarios=(4,), points=("1.3:K4",),
        evidence=(Evidence("code:agent-sdk/sessions", "You end up with two independent sessions you can resume separately."),),
        qtype="choose", level="medium", principle="fit_for_purpose",
        situation="days-long event-driven trial must run beside an export with the same analysis",
        trap="delegate the trial to a subagent with a summary",
    ),
    MCQ(
        id="Q1.3-12",
        q=("A nightly script forks an analysed session twice to trial two dependency upgrades in one checkout, the second "
           "trial running after the first. Each fork has its own session ID, and the agent changes `package.json` with `Edit`. "
           "The second trial's build keeps failing with version conflicts on a package it never touched. What should you change?"),
        opts=("Enable file checkpointing, and rewind to the pre-fork checkpoint before each trial.",
              "Fork the second trial from the first fork's session ID, so that the two histories line up.",
              "Instruct the second fork to disregard any changes it finds that it did not make itself.",
              "Resume the original session between the trials, so that its unchanged history resets the files."),
        ans=0,
        explain=("A fork copies conversation history, not files, so the first trial's edits are still in the checkout. Checkpointing "
                 "is the feature that reverts them. B stacks the trials and makes the overlap worse. C asks the model to ignore "
                 "real files that the build still reads. D assumes history controls the disk, and resuming a session "
                 "restores nothing there."),
        scenarios=(4,), points=("1.3:K4",),
        evidence=(Evidence("code:agent-sdk/sessions", "Forking branches the conversation history, not the filesystem. If a forked agent edits files, those changes are real and visible to any session working in the same directory."),),
        basis="docs",
        qtype="diagnose", level="medium", principle="root_cause",
        situation="second forked dependency trial fails on conflicts in a package it never touched",
        trap="fork from the first fork so histories line up",
    ),
    # ---- S1: complete findings in the prompt ----
    MCQ(
        id="Q1.3-13",
        q=("Reports from your research system cite news sites well but rarely use the PDFs. The document analysis subagent returns "
           "about 14 findings per run. The synthesis prompt has a full \"Web findings\" section, then one line: \"Document "
           "analysis has also been completed.\" What is the best fix?"),
        opts=("Grant synthesis the `Read` tool, so that it can open the PDFs and study them for itself.",
              "Paste those 14 findings in full into the synthesis prompt beside the web section.",
              "Let the document analysis subagent send its results straight to synthesis.",
              "Add a rule to the synthesis system prompt saying that both kinds of source carry equal weight."),
        ans=1,
        explain=("Synthesis sees only its prompt, and the prompt holds none of the analysis. A repeats finished work and gives "
                 "synthesis a tool outside its role. C bypasses the coordinator, which should route all communication between "
                 "subagents. D sets a weighting for material that never arrives."),
        scenarios=(3,), points=("1.3:S1",),
        evidence=(Evidence("code:agent-sdk/subagents", "The only content you pass from parent to subagent is the Agent tool's prompt string"),),
        qtype="fix", level="easy", principle="preserve_information",
        situation="synthesis prompt says analysis is done but omits its 14 findings",
        trap="give synthesis Read to redo the analysis",
    ),
    MCQ(
        id="Q1.3-14",
        q=("An audit of research reports finds that 40% of figures are vague or a year out when compared with what the search "
           "subagents returned. Yet every one of those figures matches the synthesis subagent's spawn prompt, wording included. "
           "The search subagents' outputs check out against their sources. Where is the most likely fault?"),
        opts=("In the search subagents, whose final messages were too short to hold the figures in the first place.",
              "In the synthesis subagent, which reworded precise figures while it was writing the final report.",
              "In the coordinator's handover, which restated the results and lost precision on the way.",
              "In the coordinator's context window, which cut off the results as they came back from search."),
        ans=2,
        explain=("The figures are right on leaving search and already wrong on entering synthesis, so the loss sits in the "
                 "handover, which should carry findings complete. A is ruled out because the search outputs hold the "
                 "exact figures. B blames an agent that reproduced its input faithfully. D would cause missing results, "
                 "and nothing in the stem shows truncation; these figures are present but altered."),
        scenarios=(3,), points=("1.3:S1",),
        evidence=(Evidence("code:sub-agents", "Claude composes a delegation message that summarizes the task, and the subagent works from there."),),
        qtype="diagnose", level="hard", principle="preserve_information",
        situation="report figures match the spawn prompt but not the search output",
        trap="blame synthesis for rewording",
    ),
    MCQ(
        id="Q1.3-15",
        q=("A coordinator spawns `code-explorer`, which returns a 300-line report of 19 call sites, then spawns `test-writer` with "
           "\"Write tests for the call sites the explorer found.\" `test-writer` spends 25 minutes rediscovering them and misses 4. "
           "Which design is best?"),
        opts=("Let `test-writer` message `code-explorer` directly and ask it for each call site it needs.",
              "Give `test-writer` the spawning tool, so that it can run its own explorer before it writes tests.",
              "Tell `test-writer` in its system prompt to search more thoroughly before it writes any test.",
              "Have the coordinator carry the report over, in full, inside the next spawn prompt."),
        ans=3,
        explain=("The coordinator already holds the report, and passing it on avoids both the delay and the misses. A routes work "
                 "around the coordinator and loses its view of what passed between them. B repeats the exploration one level "
                 "down. C pushes for a better rediscovery of facts that already exist."),
        scenarios=(4,), points=("1.3:S1",),
        evidence=(Evidence("code:agent-sdk/subagents", "The only content you pass from parent to subagent is the Agent tool's prompt string"),),
        qtype="choose", level="medium", principle="explicit",
        situation="test-writer rediscovers 19 call sites the explorer already reported",
        trap="let the second subagent run its own explorer",
    ),
    # ---- S2: content apart from metadata ----
    MCQ(
        id="Q1.3-16",
        q=("Each analysis subagent returns a paragraph of findings on one filing, ending with the filing's name. Compliance now needs "
           "every figure in a report traced to its document and page. In a sample of 200 figures, reviewers could place only 55%, "
           "because one paragraph blends figures from many pages. What is the most effective change?"),
        opts=("Return each finding as a record with separate claim, document and page fields.",
              "Tell the synthesis subagent to give a page number for every figure that it reports.",
              "Add a later step that searches the filings for each figure and fills in its page number.",
              "Pass the full text of each filing to synthesis, so that the pages are there if needed."),
        ans=0,
        explain=("The page is lost at the source, so the analysis output has to carry it as its own field through every handover. B "
                 "asks synthesis for data it never received. C rebuilds the link afterwards and can match the wrong "
                 "page when a figure repeats. D floods the prompt, and synthesis still has to work out which page backs "
                 "which claim."),
        scenarios=(3,), points=("1.3:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only judgment (TS 1.3 Skill 2): no official page discusses agent output formats for attribution.",
        qtype="fix", level="medium", principle="preserve_information",
        situation="compliance can place only 55% of figures because paragraphs blend pages",
        trap="reconstruct page numbers with a later search step",
    ),
    MCQ(
        id="Q1.3-17",
        q=("A synthesis subagent's prompt holds 15 sources pasted one after another, each opening with a line such as `From: "
           "annual-report.pdf, p.12`. About a quarter of the report's claims credit the wrong source, usually a neighbour in "
           "the list. You decide to change how the prompt lays the sources out. Which layout is best?"),
        opts=("Give each source a header block with its name and page, then a rule of equals signs, then its text.",
              "List all 15 names and pages in a numbered index at the top, with the texts below carrying only their numbers.",
              "Wrap each in a `<document>` tag with `<document_content>` and `<source>` subtags.",
              "Wrap each text in a `<document>` tag, and keep its name and page as the first line of the content."),
        ans=2,
        explain=("Tags give every source a clear boundary and hold its metadata in its own subtag beside the content, the form the "
                 "docs recommend. A is a header and a divider in plain text, which is close to the layout that already fails. B "
                 "moves the metadata far from the text it describes and relies on the model matching numbers across the "
                 "prompt. D wraps the text but leaves the metadata inside the content, so nothing separates the two."),
        scenarios=(3,), points=("1.3:S2",),
        evidence=(Evidence("api:build-with-claude/prompt-engineering/claude-prompting-best-practices", "When using multiple documents, wrap each document in `<document>` tags with `<document_content>` and `<source>` (and other metadata) subtags for clarity."),),
        qtype="configure", level="medium", principle="preserve_information",
        situation="15 pasted sources with From lines and claims credited to a neighbour",
        trap="gather the source lines into one list",
    ),
    MCQ(
        id="Q1.3-18",
        q=("A bug-tracing subagent reports: \"The config loader lacks a guard for empty values, close to where retries happen.\" The coordinator "
           "passes that sentence on, complete, to a fix subagent. The repository has three `config.py` files, and in 6 of 20 runs "
           "the fix lands in a file that was never faulty. What is the most effective change?"),
        opts=("Add a human confirmation step, in which someone approves the target file before each fix is made.",
              "Have the tracer return separate fields for file path, line number and its finding.",
              "Ask the tracer in its prompt to write fuller sentences that describe where the code is.",
              "Give the fix subagent `Grep`, so that it can search for the loader before it edits anything."),
        ans=1,
        explain=("The tracer knew the location, but it travelled as loose words, and fields keep it exact through the handover. A adds "
                 "a person to carry a detail the system already has. C keeps location inside prose, so its exactness still depends "
                 "on the wording. D makes the fix agent guess again among three matching files."),
        scenarios=(4,), points=("1.3:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only judgment (TS 1.3 Skill 2): no official page discusses handover formats between code agents.",
        qtype="diagnose", level="medium", principle="preserve_information",
        situation="fix lands in the wrong one of three config.py files after a prose handover",
        trap="ask the tracer for fuller sentences",
    ),
    # ---- S3: parallel Task calls ----
    MCQ(
        id="Q1.3-19",
        q=("A coordinator runs academic, news, patent and filings searches one per turn, which makes the research phase take four "
           "minutes. No search depends on another. A platform engineer proposes a Python thread pool outside the agent that makes "
           "four separate `query()` calls and pastes the results into the coordinator's first prompt. How should you evaluate this?"),
        opts=("Prefer one coordinator response holding all four spawns, keeping the work in its hands.",
              "Prefer the pool, since a coordinator can only run its subagents one at a time.",
              "Prefer the pool, provided that all four `query()` calls share a session ID to keep them linked.",
              "Prefer one broad search subagent covering all four source types in a single spawn."),
        ans=0,
        explain=("Several spawn calls in one response give the speed-up, and the coordinator still decides what runs and handles what "
                 "returns. B is false, because subagents can run concurrently. C keeps code deciding in advance what the coordinator "
                 "should decide. D drops the parallelism and the division of the work into separate source types."),
        scenarios=(3,), points=("1.3:S3",),
        evidence=(Evidence("api:agents-and-tools/tool-use/parallel-tool-use", "When Claude calls tools, the response has a `stop_reason` of `tool_use` and can contain several `tool_use` blocks in a single assistant turn."),
                  Evidence("code:agent-sdk/subagents", "**Parallelization**: multiple subagents can run concurrently, so independent subtasks finish in the time of the slowest one rather than the sum of all of them.")),
        qtype="evaluate", level="medium", principle="fit_for_purpose",
        situation="thread pool outside the agent proposed to speed up four source searches",
        trap="orchestrate parallelism in external code",
    ),
    MCQ(
        id="Q1.3-20",
        q=("To speed things up, a coordinator's prompt now says \"Make all your Task calls in your first response.\" Each run then "
           "emits three search spawns and one synthesis spawn together. All four complete without errors, yet in every run the "
           "synthesis output says no findings were supplied. What is the most likely root cause?"),
        opts=("Subagents spawned in one response cannot return their results to the same coordinator.",
              "Synthesis has no tool for reading the outputs of the search subagents running beside it.",
              "Four spawns went past the concurrency limit, so the search results were discarded.",
              "Its spawn prompt was written before any search had returned anything to include."),
        ans=3,
        explain=("Parallel spawning suits independent work, and synthesis depends on the searches, so its prompt had nothing to carry "
                 "at the moment it was written. A is false, since parallel results do return to the coordinator. B is the near "
                 "miss, but subagents should not read each other's output; the coordinator passes it. C is wrong because the "
                 "default limit is 20 and a refused spawn returns an error."),
        scenarios=(3,), points=("1.3:S3",),
        evidence=(Evidence("api:build-with-claude/prompt-engineering/claude-prompting-best-practices", "dependent values like the parameters, do NOT call these tools in parallel and instead"),
                  Evidence("code:agent-sdk/subagents", "`20` subagents running at once")),
        qtype="diagnose", level="hard", principle="root_cause",
        situation="synthesis spawned beside three searches reports no findings supplied",
        trap="give synthesis a tool to read sibling outputs",
    ),
    MCQ(
        id="Q1.3-21",
        q=("A customer writes about a late parcel, a double charge and a warranty claim. The support coordinator spawns a specialist "
           "for each, one per turn, and the reply takes 100 seconds. No specialist needs another's output, and all three need the "
           "customer ID from the original message. Which change is best?"),
        opts=("Spawn the first specialist, and let it start the other two so that they can share what it has found.",
              "Spawn one general specialist with all the tools, so that a single call covers all three issues.",
              "Emit all three spawns in a single response, with the ID written into each prompt.",
              "Emit all three spawns in a single response, and let them read the ID from the conversation history."),
        ans=2,
        explain=("Independent work belongs in one response, and each subagent needs the ID in its own prompt. A moves the spawning "
                 "away from the coordinator and still delays two of the issues. B removes the specialisation and "
                 "over-provisions one agent. D is the near miss: the timing is right, but subagents do not see "
                 "the conversation, so they would not have the ID."),
        scenarios=(1,), points=("1.3:S3", "1.3:K2"),
        evidence=(Evidence("code:agent-sdk/subagents", "Unless the subagent is a [fork](https://code.claude.com/docs/en/sub-agents.md#fork-the-current-conversation), its context window starts fresh, with no parent conversation, but isn't empty."),),
        qtype="choose", level="medium", principle="fit_for_purpose",
        situation="three-issue customer message waits 100 seconds for specialists spawned one per turn",
        trap="spawn together but rely on inherited history for the ID",
    ),
    # ---- S4: goals and quality criteria ----
    MCQ(
        id="Q1.3-22",
        q=("A coordinator's prompt to its explorer reads: \"Grep for chargeCard, open the first three hits, list their callers.\" "
           "Last sprint the payments team renamed that function, and since then the explorer returns \"no callers found\" and the "
           "coordinator reports nothing to change, though about 30 call sites exist. Which change to the prompt is best?"),
        opts=("Add the new function name, and keep a list of renames in the prompt as further changes land.",
              "Ask for every path that reaches card payment, and say what a complete answer must contain.",
              "Add a fallback step: if the grep finds nothing, search for the word `charge` and read five hits.",
              "Keep the steps as they are, and run the explorer on a stronger model that can spot the rename."),
        ans=1,
        explain=("A goal with a completeness bar lets the explorer adapt when a step comes back empty. A fixes this rename and "
                 "needs editing after the next one. C adds another scripted step that fails in its own way. D leaves the agent "
                 "bound to steps that end in an empty result."),
        scenarios=(4,), points=("1.3:S4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only judgment (TS 1.3 Skill 4): the docs do not discuss coordinator prompts in these terms.",
        qtype="fix", level="easy", principle="model_driven",
        situation="renamed function makes a scripted explorer report no callers",
        trap="keep a rename list or add a fallback step",
    ),
    MCQ(
        id="Q1.3-23",
        q=("After a review called your prompts too procedural, the coordinator now tells search subagents only: \"Research the "
           "impact of heat pumps on grid demand.\" The subagents do vary their approach, but 45% of their returns rest on two or "
           "three blog posts, and synthesis has little to weigh. Nothing in any prompt says what counts as a sufficient "
           "return. What is the best next change?"),
        opts=("Bring back numbered search steps that name the sites to use, now that the weakness has been measured.",
              "Have synthesis reject thin returns, so that the coordinator can send those topics back for more searching.",
              "Raise the subagents' turn limit, so that they have the room to keep on searching for longer.",
              "Say what an acceptable return looks like: source types, recency, and a source for each claim."),
        ans=3,
        explain=("The prompt gained freedom and lost its standard, and the fix is quality criteria that leave the method open. A "
                 "undoes the adaptability. B is the near miss: synthesis has nothing to reject against, since no criteria exist, "
                 "and every thin return is paid for first. C gives more time and no reason to search differently."),
        scenarios=(3,), points=("1.3:S4",),
        evidence=(Evidence("api:build-with-claude/prompt-engineering/claude-prompting-best-practices", "**Provide clear success criteria:** Define what constitutes a successful answer to your research question."),),
        qtype="choose", level="hard", principle="explicit",
        situation="goal-only search prompt returns thin blog-based results in 45% of cases",
        trap="bring back numbered steps",
    ),
    MCQ(
        id="Q1.3-24",
        q=("A coordinator's prompt to its returns subagent says: \"Call get_customer, then lookup_order, then offer a 10% credit.\" "
           "This suits late deliveries, but damaged goods and subscription issues are now 35% of cases, and those often get the "
           "wrong remedy. An engineer proposes adding if/else steps for each case type. What should you do?"),
        opts=("State the outcome wanted and the conditions a sound resolution has to meet.",
              "Move the if/else steps into a code router that picks one script for each case.",
              "Add a worked example of each case type's exact tool sequence to the prompt.",
              "Create one subagent per case type, each with a fixed script of its own to follow."),
        ans=0,
        explain=("An outcome and its conditions let the subagent choose tools and remedy from what it finds. B keeps the scripts and "
                 "moves them into code, so each new case type needs another branch. C still teaches fixed sequences. D multiplies "
                 "the scripts, and a case that spans two types has no home."),
        scenarios=(1,), points=("1.3:S4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only judgment (TS 1.3 Skill 4): the docs do not discuss coordinator prompts in these terms.",
        qtype="evaluate", level="easy", principle="model_driven",
        situation="scripted returns prompt gives wrong remedies for damaged goods and subscriptions",
        trap="add if/else branches or one scripted subagent per case",
    ),
)
