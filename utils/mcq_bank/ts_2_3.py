"""Exam bank · TS 2.3. Original questions; see docs/MCQ_BANK_PLAN.md."""
from utils.mcq_sets import MCQ, Evidence

TS = "2.3"
BULLETS = {
    "K1": "Giving an agent too many tools (18 instead of 4 or 5) makes tool selection less reliable",
    "K2": "Agents holding tools outside their specialty tend to misuse them",
    "K3": "Scoped tool access: only the tools a role needs, plus a few limited cross-role tools for frequent needs",
    "K4": "The tool_choice options: auto, any, and forced selection of a named tool",
    "S1": "Restricting each subagent's tool set to its role to prevent cross-specialty misuse",
    "S2": "Replacing a generic tool with a constrained one that validates its input",
    "S3": "Giving a scoped cross-role tool for a frequent need while routing complex cases through the coordinator",
    "S4": "Forcing a specific tool first, then handling later steps in follow-up turns",
    "S5": "Using tool_choice any to guarantee the model calls a tool instead of replying in text",
}

_FEWER = "Fewer, more capable tools reduce selection ambiguity and make your tool surface easier for Claude to navigate."
_ALLOW = "To restrict tools, use the `tools` field as an allowlist or the `disallowedTools` field as a denylist."
_INHERIT = "Inherits every tool available to subagents if omitted."
_ANY = "`any` tells Claude that it must use one of the provided tools, but doesn't force a particular tool."
_TOOL = "`tool` forces Claude to always use a particular tool."
_AUTO = "`auto` allows Claude to determine whether to call any provided tools."

QUESTIONS = (
    # ---- K1: too many tools ----
    MCQ(
        id="Q2.3-01",
        q=("A developer assistant is connected to five MCP servers (git, tickets, CI, docs, database) and now exposes 27 tools. "
           "A typical task uses at most five of them. In a 300-task sample it called a wrong but similar tool in 11% of tasks, "
           "against 2% when it had 6 tools. Which change most effectively lowers the error rate?"),
        opts=("Move to a stronger model tier, which can tell 27 similar tools apart.",
              "Give each kind of task an agent holding only the few tools it uses.",
              "Place a table of all 27 tools and when to use each in the system prompt.",
              "Require the model to say which tool it will call, and why, before each call."),
        ans=1,
        explain=("Selection gets harder as the number of options per decision grows, so splitting the work into agents with small, "
                 "role-specific tool sets attacks the cause. A leaves the same 27 options in front of the model. C adds more text "
                 "about the same list without reducing the choices. D asks for reasoning over the same 27 options."),
        scenarios=(4,), points=("2.3:K1",),
        evidence=(Evidence("api_define_tools", _FEWER),),
        qtype="fix", level="easy", principle="fit_for_purpose",
        situation="27 tools from five MCP servers give 11% near-neighbour mistakes",
        trap="stronger model or a tool table in the prompt",
    ),
    MCQ(
        id="Q2.3-02",
        q=("A support agent holds 14 tools for orders, shipping and refunds, and wrong-tool calls have risen from 3% at 6 tools to 9%. "
           "Product wants to add three gift-card tools (issue, check balance, void). They are needed in about 4% of chats and have "
           "nothing to do with the existing work. What is the best way to add them?"),
        opts=("Add them to the agent and rewrite the refund tool descriptions so the gift-card tools are not confused with them.",
              "Add them and let a keyword router switch on only the 8 tools that look relevant to each message.",
              "Give them to a separate gift-card agent, and have the coordinator hand it those requests.",
              "Add them and drop the three least-used existing tools so that the total stays at 14."),
        ans=2,
        explain=("A separate agent keeps the main agent's choice set from growing and gives the new tools a small set of their own. "
                 "A leaves the agent with 17 tools to choose between. B adds a brittle routing layer in front of the model. "
                 "D removes working capability to make room."),
        scenarios=(1,), points=("2.3:K1",),
        evidence=(Evidence("api_define_tools", _FEWER),),
        qtype="choose", level="medium", principle="proportionate",
        situation="three unrelated gift-card tools proposed for a 14-tool support agent",
        trap="keyword router or removing existing tools",
    ),
    MCQ(
        id="Q2.3-03",
        q=("A research team measured tool-selection accuracy for one agent as it was given more tools, keeping every description "
           "accurate and distinct: 98% with 4 tools, 94% with 9, 86% with 17 and 71% with 30. A teammate says the descriptions "
           "must be failing. Which reading of the data is best supported?"),
        opts=("Every added tool is one more option to tell apart, so accuracy falls; split the tools by role.",
              "The descriptions are failing, so rewrite the 26 that were added after the first four.",
              "Definitions fill the context, so cutting every description in half should restore the accuracy.",
              "Tools late in the list get skipped, so ordering the list by how often each tool is used should restore it."),
        ans=0,
        explain=("The decline tracks the number of tools while the descriptions stay accurate, which points to decision complexity, "
                 "and the lever is a smaller tool set per agent. B contradicts the stem's description that they are accurate and "
                 "distinct. C shortens the very descriptions the model relies on. D assumes a position effect that the data does "
                 "not show."),
        scenarios=(3,), points=("2.3:K1",),
        evidence=(Evidence("api_define_tools", _FEWER),),
        qtype="evaluate", level="hard", principle="root_cause",
        situation="accuracy drops from 98% to 71% as tools grow from 4 to 30 with sound descriptions",
        trap="blame the descriptions or the list order",
    ),
    # ---- K2: tools outside the specialty get misused ----
    MCQ(
        id="Q2.3-04",
        q=("A citation-checking subagent should only compare quoted passages with source texts supplied in its prompt. Its definition "
           "has a description and a prompt but no tools field. In 6% of runs the report file was rewritten, and in others the agent "
           "searched the web for new quotes. The spawn prompt always contains the passages and the sources. What is the most "
           "likely root cause?"),
        opts=("The subagent cannot see the coordinator's conversation, so it fills the gaps by acting on its own.",
              "Its description is too short for the coordinator to understand what the subagent is for.",
              "The definition grants every available tool, and an agent with spare tools tends to use them.",
              "The sources arrive as text, so it goes looking for the original documents."),
        ans=2,
        explain=("With the tools field left out the subagent inherits everything, and tools beyond its job get used. A is ruled out "
                 "because the prompt carries the passages and sources. B concerns when the coordinator delegates, not what the "
                 "subagent does once running. D does not explain the rewritten report file."),
        scenarios=(3,), points=("2.3:K2",),
        evidence=(Evidence("cc_subagents", _INHERIT),),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="citation checker with no tools field rewrites the report and searches the web",
        trap="blame missing context or a short description",
    ),
    MCQ(
        id="Q2.3-05",
        q=("A code-review subagent was tested in two configurations over 400 reviews each. Configuration 1 had Read, Grep and Glob. "
           "Configuration 2 added Bash \"to run the linter\". Configuration 2 ran the full test suite in 23 reviews, ran git "
           "commands unrelated to the diff in 9, and modified a file in 3; configuration 1 showed none of this. Review quality "
           "scores were the same. What does the result best support?"),
        opts=("Bash is unreliable inside subagents, so shell access should be removed from every agent.",
              "The reviewer prompt needs a longer checklist, because the extra actions show it misunderstood its task.",
              "The gap is probably noise, because review quality scores were the same in both configurations.",
              "The extra tool opened actions outside the job and they were used; supply lint output another way."),
        ans=3,
        explain=("Capability beyond the role was used, so the cause is the tool set, and the linter need can be met with a narrower "
                 "route. A overgeneralises from one extra tool. B treats a tool-set problem as a prompt problem. C ignores that "
                 "35 unrequested actions appeared in one arm and none in the other; equal quality scores do not make them harmless."),
        scenarios=(4,), points=("2.3:K2",),
        evidence=(Evidence("cc_subagents", _ALLOW),),
        qtype="evaluate", level="medium", principle="least_privilege",
        situation="reviewer with Bash added runs tests, git and edits in 35 of 400 reviews",
        trap="equal quality scores read as no harm",
    ),
    MCQ(
        id="Q2.3-06",
        q=("A refund-policy subagent holds `process_refund` as well as its lookup tools, because the team wanted to avoid a second "
           "hand-off. A prompt line \"Answer policy questions only; never issue refunds\" cut unintended refunds from 12 per 1,000 "
           "chats to 5 per 1,000, and three rewordings have not improved on that. What is the best next step?"),
        opts=("Move the sentence to the top of the prompt and put the key word in capitals, to stress it.",
              "Remove `process_refund` from this subagent; another agent is meant to issue refunds.",
              "Add ten examples of correct refusals to the prompt, since the rule alone is not enough.",
              "Have it state its intended action in text before each call, so mistakes can be caught."),
        ans=1,
        explain=("An instruction lowers the odds of misuse but cannot remove it while the tool is available; taking the tool away "
                 "does. A and C keep trying to persuade a model that still has the capability. D relies on the model reporting its "
                 "own errors correctly before they happen."),
        scenarios=(1,), points=("2.3:K2",),
        evidence=(Evidence("cc_subagents", _ALLOW),),
        qtype="fix", level="hard", principle="deterministic",
        situation="prompt rule leaves 5 unintended refunds per 1,000 from a policy subagent",
        trap="reword or add examples instead of removing the tool",
    ),
    # ---- K3: scoped access with limited cross-role tools ----
    MCQ(
        id="Q2.3-07",
        q=("In a support system the billing, shipping and returns subagents each hold only their own tools. The returns subagent needs "
           "the carrier's delivery date in 70% of its cases. It is one read-only field available through the shipping subagent's "
           "tracking tool, so each time returns asks the coordinator and waits for a shipping subagent to run. Operations also want "
           "every cross-agent request to stay visible in the coordinator's log. Which design keeps the roles and removes most of "
           "the delay?"),
        opts=("Give returns the shipping subagent's full toolset so it can look up anything it wants about a parcel.",
              "Give returns a read-only `get_delivery_date(order_id)` tool; the rest goes via the coordinator.",
              "Paste the delivery date of every open order into the returns subagent's prompt at each spawn.",
              "Let returns message the shipping subagent directly whenever it needs a delivery date."),
        ans=1,
        explain=("A single narrow, read-only tool covers the frequent need while the role boundaries and the coordinator's visibility "
                 "stay. A hands over a whole role's capability. C ships data nobody asked for and goes stale. D bypasses the "
                 "coordinator, which the stem says must see cross-agent requests."),
        scenarios=(1,), points=("2.3:K3",),
        evidence=(Evidence("cc_subagents", _ALLOW),),
        qtype="choose", level="medium", principle="least_privilege",
        situation="returns subagent waits on the coordinator for a delivery date in 70% of cases",
        trap="share the whole shipping toolset or message agents directly",
    ),
    MCQ(
        id="Q2.3-08",
        q=("Over a week a coordinator logged what its test-writer subagent requested from the code-explorer subagent: 58% single-symbol "
           "signature lookups, 25% \"find all callers of this function across modules\" (needing several rounds of judgment about "
           "indirect calls), and 17% other. Each relay costs about 30 seconds. The test-writer holds only Read and Write. Which "
           "addition best fits scoped cross-role access?"),
        opts=("A narrow `get_signature(symbol)` tool for the test-writer; the explorer keeps caller tracing.",
              "A general `search_repo` tool that lets the test-writer run Grep across the whole repository.",
              "A `trace_callers(function)` tool for the test-writer, since it removes the slowest requests.",
              "No new tool; the coordinator pre-loads the explorer's entire index into the test-writer's prompt."),
        ans=0,
        explain=("The frequent, simple need gets a narrow tool, and the complex multi-round work stays where judgment is available. "
                 "B covers all three request types and so erases the role boundary. C moves a task needing repeated judgment into a "
                 "single-call tool. D loads far more than any task uses."),
        scenarios=(4,), points=("2.3:K3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: no official page covers choosing which cross-role tool to add.",
        qtype="evaluate", level="hard", principle="proportionate",
        situation="58% signature lookups and 25% caller tracing relayed through the coordinator",
        trap="cover every request type with one general tool",
    ),
    MCQ(
        id="Q2.3-09",
        q=("In a five-subagent research system every subagent is limited to its own tools and sends all other needs to the coordinator. "
           "By the middle of a typical run the coordinator's context is 80% full, and most of it is relay traffic: \"convert this "
           "amount to USD\" and \"what weekday was this date\" requests and answers, repeated dozens of times. Report quality "
           "drops after that point. What is the most effective change?"),
        opts=("Give each subagent the complete toolset of whichever agent usually answers, so nothing is relayed.",
              "Have the coordinator summarise its own context whenever it passes 70% full, to free up room.",
              "Start a second coordinator to take over once the first reaches 80% of its context window.",
              "Give subagents two small tools for those two lookups, keeping the rest on the coordinator."),
        ans=3,
        explain=("The two frequent needs are simple, so narrow tools remove most of the traffic while the roles stay intact. A erases "
                 "the role boundaries. B copes with the symptom and still sends the relays through. C adds a second coordinator "
                 "to carry the same traffic."),
        scenarios=(3,), points=("2.3:K3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: no official page covers limited cross-role tools.",
        qtype="fix", level="medium", principle="proportionate",
        situation="coordinator context 80% full of currency and weekday relay traffic",
        trap="summarise the coordinator or add a second one",
    ),
    # ---- K4: the tool_choice options ----
    MCQ(
        id="Q2.3-10",
        q=("A support chat agent has five tools and runs with `tool_choice: {\"type\": \"any\"}`. When customers send \"hello\" or "
           "\"thanks, that's all\" (about 15% of chats), it calls `get_customer` with an empty identifier, gets an error, and then "
           "apologises for a system problem. What is the best fix?"),
        opts=("Switch to `auto`, so the model can reply in text when no tool fits the message.",
              "Keep `any` and make `get_customer` return a friendlier error for an empty identifier.",
              "Force `get_customer` by name, so there is no doubt which tool is called.",
              "Keep `any` and add a prompt rule that greetings need no lookup."),
        ans=0,
        explain=("`any` requires a tool call on every turn, so a message with no tool need still produces one; `auto` lets the model "
                 "answer in text. B softens the error but the pointless call remains. C makes the call certain rather than optional. "
                 "D asks the prompt to override a setting that requires a call."),
        scenarios=(1,), points=("2.3:K4",),
        evidence=(Evidence("api_define_tools", _ANY), Evidence("api_define_tools", _AUTO)),
        qtype="fix", level="easy", principle="fit_for_purpose",
        situation="greetings trigger an empty-identifier lookup under any",
        trap="patch the error instead of the setting",
    ),
    MCQ(
        id="Q2.3-11",
        q=("A research pipeline makes one request per step. Step 1 offers four tools and must begin with `plan_subtopics`. Step 2 offers "
           "the same four tools; the model may call any of them or reply with a plain-text status. Step 3 lists only `submit_summary` "
           "and `submit_full`; one of them must be called and the model decides which. Which `tool_choice` values for steps 1, 2 "
           "and 3 meet this?"),
        opts=("`any`, `auto`, forced `submit_full` by name",
              "`auto`, `auto`, `any` on all three steps",
              "forced `plan_subtopics`, `auto`, `any`",
              "forced `plan_subtopics`, `any`, `auto`"),
        ans=2,
        explain=("Step 1 needs one named tool, so forced selection; step 2 allows free choice including text, so `auto`; step 3 needs "
                 "some tool without naming it, so `any`. A uses `any` where a named tool is required and forces the choice step 3 "
                 "leaves to the model. B cannot guarantee step 1. D stops step 2 from replying in text and lets step 3 skip the "
                 "call."),
        scenarios=(3,), points=("2.3:K4",),
        evidence=(Evidence("api_define_tools", _TOOL), Evidence("api_define_tools", _ANY)),
        qtype="configure", level="medium", principle="explicit",
        situation="three research steps need forced, free and any-tool behaviour respectively",
        trap="mixing up any and forced selection",
    ),
    MCQ(
        id="Q2.3-12",
        q=("A reviewer is checking the `tool_choice` plan for a developer-productivity agent. Which line would not behave as its "
           "author expects?"),
        opts=("Open questions about the repository use `auto`, so the model can answer in plain text when no tool is needed.",
              "The first request of a session forces `load_config` by name, because it has to run before anything else.",
              "The verdict step lists `approve_change` and `reject_change` and uses `any`, so a verdict is always recorded.",
              "The lint step uses `any`, because `lint_report` has to run and that setting selects that tool."),
        ans=3,
        explain=("`any` guarantees that some tool is called but leaves the choice to the model; running a particular tool takes forced "
                 "selection by name. A, B and C each match the setting to what it does: free text with `auto`, a named first call "
                 "with forced selection, and one of two listed tools with `any`."),
        scenarios=(4,), points=("2.3:K4",),
        evidence=(Evidence("api_define_tools", _ANY), Evidence("api_define_tools", _TOOL)),
        qtype="evaluate", level="medium", principle="fit_for_purpose",
        situation="plan expects any to run a specific lint tool",
        trap="treat any as selecting a named tool",
    ),
    # ---- S1: restrict each subagent's tool set ----
    MCQ(
        id="Q2.3-13",
        q=("You are defining a `document-reader` subagent that must read and search files but never write them or run commands. "
           "Which definition does that?"),
        opts=("Leave the `tools` field out and give it the description \"Read-only document reader\".",
              "`tools: Read, Grep, Glob`",
              "`disallowedTools: Read, Grep, Glob`",
              "`tools: Read, Grep, Glob, Bash`, with Bash used only for `cat` and `ls`."),
        ans=1,
        explain=("An explicit allowlist gives the subagent exactly those tools. A omits the field, which means it inherits every "
                 "tool whatever the description says. C removes the very tools it needs. D includes a shell that can write "
                 "files, with the limit stated only in words."),
        scenarios=(3,), points=("2.3:S1",),
        evidence=(Evidence("cc_subagents", _ALLOW), Evidence("cc_subagents", _INHERIT)),
        qtype="configure", level="easy", principle="least_privilege",
        situation="read-only document reader subagent definition",
        trap="omit the tools field or include Bash",
    ),
    MCQ(
        id="Q2.3-14",
        q=("A documentation-lookup subagent needs two tools, `search_docs` and `fetch_page`. It runs in a project where five MCP servers "
           "expose 25 tools, and a new server is added about once a week. Its tools field is currently omitted, and it picks a wrong "
           "tool in 8% of lookups. Which change keeps its tool set right over the coming months?"),
        opts=("Set its `tools` field to `search_docs` and `fetch_page`.",
              "Leave `tools` out and list the 23 other tools in `disallowedTools`.",
              "Leave `tools` out and add a prompt paragraph naming the two tools it should prefer.",
              "Move the five servers to user scope so that subagents no longer see them."),
        ans=0,
        explain=("An allowlist stays correct as servers are added, because anything not listed is not available. B works today but "
                 "each new server's tools are inherited until someone lists them. C leaves every tool available and relies on the "
                 "prompt. D changes where the servers are configured, not which tools a subagent inherits."),
        scenarios=(4,), points=("2.3:S1",),
        evidence=(Evidence("cc_subagents", _ALLOW), Evidence("cc_subagents", _INHERIT)),
        qtype="choose", level="medium", principle="least_privilege",
        situation="lookup subagent in a project that gains a new MCP server every week",
        trap="denylist the other 23 tools",
    ),
    MCQ(
        id="Q2.3-15",
        q=("A research system has three subagents: search, analysis and synthesis. The available tools are `web_search`, `fetch_page`, "
           "`read_document`, `compute_stats` and `write_report`. Which assignment follows the principle of restricting each subagent "
           "to its role?"),
        opts=("All three get all five tools, and each prompt names the tools that particular agent should use.",
              "Search gets all five tools since it runs first, while analysis and synthesis keep only their own.",
              "Search: `web_search`, `fetch_page`. Analysis: `read_document`, `compute_stats`. Synthesis: `write_report`.",
              "Search and analysis keep their own tools; synthesis also gets `web_search` to fill gaps found while writing."),
        ans=2,
        explain=("Each agent holds exactly the tools its job needs. A puts the restriction in the prompt only. B gives the broadest "
                 "toolset to the agent most likely to wander. D lets synthesis do search work, which is the cross-role misuse the "
                 "split is meant to prevent."),
        scenarios=(3,), points=("2.3:S1",),
        evidence=(Evidence("cc_subagents", _ALLOW),),
        qtype="choose", level="easy", principle="least_privilege",
        situation="five tools shared out among search, analysis and synthesis subagents",
        trap="broad toolset for the first agent or search for synthesis",
    ),
    # ---- S2: constrained replacement for a generic tool ----
    MCQ(
        id="Q2.3-16",
        q=("A deployment assistant has one generic `run_shell(command)` tool. Its real duties are restarting three named services and "
           "reading the last N log lines of each. Over 1,200 sessions it also installed packages in 14 and deleted a temp "
           "directory in 2, none requested. The team has already seen `curl | sh` and `apt` get past command deny lists. "
           "Which change best addresses this?"),
        opts=("Add a PreToolUse hook that denies any command containing `rm`, `pip` or `npm`, and logs the attempt.",
              "Add a prompt section that lists the only shell commands the assistant may use during a session, with examples.",
              "Log every command and have an engineer review the whole log each morning.",
              "Replace it with `restart_service(name)` and `tail_log(name, lines)` for the three service names."),
        ans=3,
        explain=("Tools that can do only the two duties, and validate their input, remove the unwanted actions at the source. A covers "
                 "only the commands someone thought of; other installers and delete forms pass. B relies on the model following the "
                 "list. C finds problems after they have happened."),
        scenarios=(4,), points=("2.3:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: no official page covers replacing a generic tool with a constrained one.",
        qtype="fix", level="medium", principle="deterministic",
        situation="generic shell tool installs packages and deletes a directory unasked",
        trap="denylist hook on command words",
    ),
    MCQ(
        id="Q2.3-17",
        q=("A support agent uses a generic `send_email(to, subject, body)` tool. An audit of 2,000 chats found 17 replies sent to an "
           "address the customer had typed into the chat instead of the account's address, once exposing order details to a third "
           "party. Which change best fixes the tool design?"),
        opts=("Keep `send_email` and ask the agent to read the address back to the customer before sending.",
              "Replace it with `send_order_update(order_id, template)`, recipient taken from the account.",
              "Keep `send_email` and list the permitted recipient domains in the system prompt.",
              "Add a PostToolUse hook that records each sent message for weekly compliance review."),
        ans=1,
        explain=("A constrained tool that fixes the recipient and the content type makes the unsafe send impossible. A has the "
                 "customer confirm an address that may be a third party's. C asks the prompt to police a tool that accepts "
                 "any recipient. D records the leak after the message has gone."),
        scenarios=(1,), points=("2.3:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: no official page covers replacing a generic tool with a constrained one.",
        qtype="fix", level="medium", principle="least_privilege",
        situation="generic email tool sends order details to an address typed in chat",
        trap="read-back confirmation or a domain list in the prompt",
    ),
    MCQ(
        id="Q2.3-18",
        q=("To stop research subagents fetching login pages and images, a team added a validated `load_document(url)` tool that rejects "
           "anything but supported document types. They left the generic `fetch_url` in the tools list \"as a fallback\". Two weeks "
           "later 8% of calls still go to non-document pages, almost unchanged, and the logs show every one of them is a "
           "`fetch_url` call. What is the most likely root cause?"),
        opts=("The generic tool is still listed, so the agent can pick it and the unsafe path stays open.",
              "`load_document` needs more worked examples in its description to compete with the simpler tool.",
              "Subagents ignore their tool list unless the prompt repeats the names of the permitted tools.",
              "The unsupported pages arrive through redirects that `load_document` follows without checking."),
        ans=0,
        explain=("A constrained tool only helps when the generic one is gone; while both exist the agent can still take the open "
                 "route. B tries to win the choice by persuasion rather than removing it. C describes behaviour that does not match "
                 "an explicit tool list. D is ruled out because every bad call is `fetch_url`."),
        scenarios=(3,), points=("2.3:S2",),
        evidence=(Evidence("cc_subagents", _ALLOW),),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="validated load_document added but fetch_url kept, misuse stays at 8%",
        trap="improve the new tool's description instead of removing the old one",
    ),
    # ---- S3: scoped cross-role tool, complex cases to the coordinator ----
    MCQ(
        id="Q2.3-19",
        q=("A docs-writer subagent has a narrow read-only `get_package_version` tool that covers most of its needs. While updating "
           "examples it must find out whether a breaking change in version 3 affects any of three modules that each use a different "
           "part of the library. What should it do?"),
        opts=("Call `get_package_version` for each module and infer the impact from the version numbers.",
              "Ask for the build subagent's manifest-editing tool so that it can read the changelogs itself.",
              "Hand the question back so the coordinator can route it to the code-explorer subagent.",
              "Write the examples for version 3 and mark the three modules as unverified in a footnote."),
        ans=2,
        explain=("The narrow tool answers the frequent simple question; an impact analysis across modules is a complex case, and "
                 "those go through the coordinator. A treats a version string as evidence of impact. B asks for a tool that can edit "
                 "manifests. D completes the task while leaving the question unanswered."),
        scenarios=(4,), points=("2.3:S3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: no official page covers routing complex cases through a coordinator.",
        qtype="choose", level="easy", principle="least_privilege",
        situation="docs writer with a version tool must judge a breaking change across modules",
        trap="stretch the narrow tool or ask for an editing tool",
    ),
    MCQ(
        id="Q2.3-20",
        q=("In a support system, 90% of the billing subagent's cases need only to know whether the customer's identity was verified "
           "earlier in the chat. The identity subagent holds `get_customer` (the full record, including payment details), "
           "`send_verification_code` and `update_contact`. Which option best serves billing?"),
        opts=("Give billing `get_customer`, since the tool only reads data.",
              "Give billing `send_verification_code`, so it can verify the customer itself when unsure.",
              "Run every billing case through the identity subagent, to leave billing's tools unchanged.",
              "Give billing an `is_verified(customer_id)` tool that returns only true or false."),
        ans=3,
        explain=("The frequent need is a yes or no answer, so a tool that returns exactly that serves it with no more access than "
                 "required. A exposes payment details billing does not need. B hands over an action that contacts the customer. C "
                 "sends 90% of cases through a relay."),
        scenarios=(1,), points=("2.3:S3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: no official page covers designing a limited cross-role tool.",
        qtype="choose", level="medium", principle="least_privilege",
        situation="billing needs only a verified flag held by the identity subagent",
        trap="share the full customer record or the verification action",
    ),
    MCQ(
        id="Q2.3-21",
        q=("A synthesis subagent was given `check_figure(claim_id)`, which returns the source's value for one figure, and it worked "
           "well for single figures. Logs now show it calling the tool up to 15 times on a claim where two sources disagree, getting "
           "a different value each time, and then writing the average into the report. What is the best change?"),
        opts=("Add a prompt rule not to call `check_figure` more than twice per claim.",
              "Make the tool flag conflicting sources and return no value, so the claim goes to the coordinator.",
              "Give the subagent the full source-comparison toolset that the analysis subagent uses to compare them.",
              "Cache the first value returned so every repeat call gives the same figure."),
        ans=1,
        explain=("The cross-role tool should stay narrow and signal when a case is beyond it, so that the complex disagreement is "
                 "routed through the coordinator. A caps the calls but the average still gets written. C turns a limited tool into a "
                 "second analysis agent. D hides the disagreement behind a stable but arbitrary number."),
        scenarios=(3,), points=("2.3:S3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: no official page covers keeping cross-role tools narrow.",
        qtype="fix", level="hard", principle="preserve_information",
        situation="check_figure called 15 times on conflicting sources and an average written",
        trap="cap calls or cache the first value",
    ),
    # ---- S4: force a tool first, then follow-up turns ----
    MCQ(
        id="Q2.3-22",
        q=("A repository assistant edits files for tickets. When a ticket touches the `migrations/` folder it must call "
           "`check_schema_lock(migration_path)` before any edit; the tool needs a path that only migration tickets have. With a prompt "
           "rule alone, 5 of the last 40 migration tickets skipped the check. What is the most effective setup?"),
        opts=("Force `check_schema_lock` first when code sees a `migrations/` path, then use `auto`.",
              "Force `check_schema_lock` on the first request of every ticket, so the rule cannot be missed.",
              "Use `any` on the first request of every ticket, so some tool is called before editing.",
              "Run `check_schema_lock` after the edits and revert them if the schema turns out to be locked."),
        ans=0,
        explain=("The application knows from the ticket whether the check applies, so it forces the tool only then and returns to "
                 "`auto` for later steps. B forces a call that needs a migration path on tickets that have none. C guarantees some "
                 "tool, not this one. D checks after the damage is done."),
        scenarios=(4,), points=("2.3:S4",),
        evidence=(Evidence("api_define_tools", _TOOL),),
        qtype="configure", level="medium", principle="deterministic",
        situation="schema lock check needed only on migration tickets",
        trap="force it on every ticket or check after the edits",
    ),
    MCQ(
        id="Q2.3-23",
        q=("In a research pipeline `plan_subtopics` must run first, so the first request forces it. What happens next depends on what "
           "the searches return, which cannot be predicted from the plan: sometimes `read_page` is needed on known sources, sometimes "
           "another `web_search`. A developer proposes forcing each later call in code from the plan's `breadth` field, giving a "
           "fixed script of forced calls. Which approach is better?"),
        opts=("Force each later call from the plan's `breadth` field, producing a fixed script.",
              "Start a new conversation for each step, pasting the plan into the prompt.",
              "Send its result back with the history and let the model choose the next tool.",
              "Use `any` on the follow-up requests so that a tool is called at every step."),
        ans=2,
        explain=("Only the first step needs a guarantee; later steps go in follow-up turns where the model, which sees the results so "
                 "far, picks the tool. A hard-codes a sequence that the stem says depends on unpredictable results. B drops the "
                 "history the model needs. D rules out ending the loop with a plain-text answer."),
        scenarios=(3,), points=("2.3:S4",),
        evidence=(Evidence("api_define_tools", _TOOL),),
        qtype="choose", level="hard", principle="model_driven",
        situation="forced plan step followed by data-dependent searching and reading",
        trap="script every later call with forced selection",
    ),
    MCQ(
        id="Q2.3-24",
        q=("A support chat agent must begin each conversation by calling `lookup_customer`, and the team enforced that with a forced "
           "`tool_choice`. Median reply time has risen from 2 s to 7 s, and the logs show lookup calls on messages such as \"what are your "
           "opening hours?\". What is the most likely root cause?"),
        opts=("Customer lookups are not cached, so each forced call repeats the full lookup.",
              "`any` was set in place of a forced tool, so the model repeats a lookup it has already made.",
              "The prompt does not say the customer should be looked up once per conversation.",
              "The forced setting is applied to every request, not only the first of the conversation."),
        ans=3,
        explain=("Forcing is for the step that must come first; if the same setting goes on every later request, every message "
                 "triggers the call. A would make repeated calls cheaper but would not explain why they occur. B names a different "
                 "setting than the one used. C asks the prompt to override a forced choice."),
        scenarios=(1,), points=("2.3:S4",),
        evidence=(Evidence("api_define_tools", _TOOL),),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="lookup_customer called on all five messages of a chat",
        trap="cache the lookup instead of limiting the forced setting",
    ),
    # ---- S5: any guarantees a tool call ----
    MCQ(
        id="Q2.3-25",
        q=("A support platform needs every chat to end with a recorded disposition, through the tools `resolve_ticket`, "
           "`escalate_ticket` or `request_callback`. With `tool_choice: auto`, 6% of chats close with a sympathetic sentence and no "
           "tool call. Operations added a regex over the reply to guess the disposition, and it misreads 1 in 5 of those chats. "
           "The disposition is requested in a closing request of its own that lists only these three tools. What is the best fix?"),
        opts=("Add more patterns to the regex until it reads the sympathetic sentences correctly.",
              "Set `tool_choice` to `any` on that closing request, so a disposition tool is called.",
              "Force `resolve_ticket` by name, since most chats end that way in practice.",
              "Ask the model to end each message with a bracketed disposition keyword and match that."),
        ans=1,
        explain=("`any` guarantees a tool call and lets the model choose which disposition fits, so no text needs parsing. A keeps "
                 "guessing from free text. C records the wrong disposition for every chat that is not a resolution. D is a "
                 "prompt request, which can be skipped like the original rule."),
        scenarios=(1,), points=("2.3:S5",),
        evidence=(Evidence("api_define_tools", _ANY),),
        qtype="fix", level="easy", principle="deterministic",
        situation="6% of chats end in text with no disposition tool call",
        trap="regex over the reply or a bracketed keyword",
    ),
    MCQ(
        id="Q2.3-26",
        q=("A research coordinator's routing step has the tools `route_to_search`, `route_to_analysis` and `finish`, and the model "
           "decides which fits the state. To stop 4% of text-only replies a developer forced `route_to_search` by name. The text-only "
           "replies vanished, but now every run goes to search and the budget is spent before any analysis starts. What is the "
           "right configuration?"),
        opts=("Use `any`, so a tool is called at each step and the model still picks which.",
              "Keep the forced tool and add a prompt rule to route to analysis once enough sources exist.",
              "Use `auto` and resend the request whenever the reply is text only.",
              "Force `route_to_search` on odd steps and `route_to_analysis` on even steps."),
        ans=0,
        explain=("`any` removes the text-only replies without choosing the route for the model. B asks the prompt to override a "
                 "forced choice. C goes back to a setting that allowed the text-only replies and pays for the resends. D replaces "
                 "the model's routing judgment with a fixed alternation."),
        scenarios=(3,), points=("2.3:S5",),
        evidence=(Evidence("api_define_tools", _ANY), Evidence("api_define_tools", _TOOL)),
        qtype="fix", level="medium", principle="model_driven",
        situation="forced route_to_search starves the analysis step",
        trap="force one named route to remove text replies",
    ),
    MCQ(
        id="Q2.3-27",
        q=("Compliance says no pull request may be left without a recorded outcome, so the review step must end in a tool call "
           "(`approve`, `request_changes` or `comment_only`). A team tried three setups on 1,000 requests each: a prompt line "
           "\"call a tool\" gave a tool call in 94%; `auto` with up to three resends on a text-only reply gave 99.4%; "
           "`tool_choice: any` gave 100%. Which conclusion is best supported?"),
        opts=("Resending is the best option, because 99.4% is close enough to 100% for compliance purposes.",
              "The prompt line works best once it is moved to the top of the system prompt, ahead of the rest.",
              "Of the three setups, only `any` guarantees a call; the others make text-only replies rarer.",
              "`any` is unsuitable here, because it stops the model from choosing among the three tools."),
        ans=2,
        explain=("A requirement that no request goes unrecorded needs a guarantee, and `any` provides one while leaving the choice of "
                 "tool to the model. A accepts 6 unrecorded pull requests per 1,000. B is a guess the data does not test. D is "
                 "wrong because `any` still lets the model pick any of the three."),
        scenarios=(4,), points=("2.3:S5",),
        evidence=(Evidence("api_define_tools", _ANY),),
        qtype="evaluate", level="medium", principle="deterministic",
        situation="prompt 94%, resend 99.4%, any 100% on a no-gap compliance rule",
        trap="treat 99.4% as good enough",
    ),
)
