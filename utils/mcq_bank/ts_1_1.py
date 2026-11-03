"""Exam bank · TS 1.1. Original questions; see docs/MCQ_BANK_PLAN.md."""
from utils.mcq_sets import MCQ, Evidence

TS = "1.1"
BULLETS = {
    "K1": "The loop lifecycle: send a request, read stop_reason, run the requested tools, return the results, repeat",
    "K2": "Tool results are added to the conversation history so the model can reason about its next action",
    "K3": "Model-driven decisions (Claude picks the next tool from context) versus fixed decision trees or tool sequences",
    "S1": "Control flow that continues on stop_reason tool_use and ends on end_turn",
    "S2": "Adding tool results to the context between iterations so new information reaches the model",
    "S3": "Avoiding parsing language for termination, iteration caps as the main stop, and text content as a completion signal",
}

QUESTIONS = (
    # ---- K1: lifecycle ----
    MCQ(
        id="Q1.1-01",
        q=("Your report subagent writes correct reports, yet every run makes exactly 40 API calls, its guard limit. In the "
           "trace, the first 6 responses have `stop_reason: \"tool_use\"` and their tools run. From response 7 on, each one "
           "has `stop_reason: \"end_turn\"`, no tool calls and the same report text. The debug log prints `continue=True` on "
           "all 40 passes. What is the most likely root cause?"),
        opts=("The system prompt never says that the subagent should stop working once its report has been written.",
              "The guard is set far too high, so a run has room to continue long after the useful work has ended.",
              "The continue check tests a value saved earlier, not the signal on the newest response received.",
              "The tool results are not reaching the model, so it keeps repeating its report and cannot move past it."),
        ans=2,
        explain=("The model signalled `end_turn` at response 7, but the code still reports `continue=True`, so the check is not "
                 "reading each new `stop_reason`. A blames the model, which had already stopped. B only limits the waste and "
                 "leaves the guard as the real stop. D does not fit, since the report is correct and the model finished."),
        scenarios=(3,), points=("1.1:K1", "1.1:S1"),
        evidence=(Evidence("api:agents-and-tools/tool-use/how-tool-use-works", "Repeat from step 2 while `stop_reason` is `\"tool_use\"`."),),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="report subagent keeps calling after end_turn until a 40-call guard trips",
        trap="lower the guard or blame the prompt for a stale stop_reason",
    ),
    MCQ(
        id="Q1.1-02",
        q=("The document analysis subagent gained a third tool last week. Since then about 30% of runs fail with a 400: "
           "`tool_use ids were found without tool_result blocks immediately after`. The failing traces all show a response "
           "with `stop_reason: \"tool_use\"` and three `tool_use` blocks, followed by a user message with one `tool_result`. "
           "What is the most likely root cause?"),
        opts=("The loop handles a single block per response, but every `tool_use` block needs its own `tool_result`.",
              "Each of the three results has to travel in its own user message, and the loop merged them into just one.",
              "The tool definitions now exceed what one request can hold, so the API drops the later `tool_use` blocks.",
              "The text block ahead of the tool calls has to be removed from the assistant turn before the next request."),
        ans=0,
        explain=("One response can carry several `tool_use` blocks, and each one needs a matching `tool_result` in the next "
                 "user message; the trace shows three calls and one result. B is backwards, since all results belong "
                 "together in a single user message. C invents a limit, and the trace shows all three blocks arriving. D is "
                 "wrong because the assistant turn goes back as it came, and text ahead of a tool call is normal."),
        scenarios=(3,), points=("1.1:K1", "1.1:S2"),
        evidence=(Evidence("api:agents-and-tools/tool-use/parallel-tool-use", "Whichever strategy you use, return one `tool_result` for each `tool_use` block, all together in the next user message."),),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="adding a third tool makes document analysis runs fail with a 400 on missing results",
        trap="send each result in its own user message",
    ),
    MCQ(
        id="Q1.1-03",
        q=("A new developer adds an `issue_replacement` tool to a manual support loop and tests it. Claude responds with "
           "`stop_reason: \"tool_use\"` and a block holding the right order number, the code logs the response, and the "
           "script exits. No replacement ever appears in the order system. What is the actual problem?"),
        opts=("The tool description is too short, so Claude is unsure the replacement is really meant to be issued.",
              "`tool_choice` is left on `auto`, and it must be set to `any` before Claude is able to execute a tool.",
              "Claude's service account lacks write access to the order system, so its update was rejected silently.",
              "Claude only asks for the call; the application must run the tool and send a `tool_result` back."),
        ans=3,
        explain=("Tool use is a contract: the model emits a structured request and your code runs the operation, then returns "
                 "the result on the next request. A is wrong because Claude picked the tool with correct arguments. B misreads "
                 "`tool_choice`, which affects whether a tool is called, not who runs it. C assumes Claude touches the backend "
                 "itself, which it never does."),
        scenarios=(1,), points=("1.1:K1",),
        evidence=(Evidence("api:agents-and-tools/tool-use/how-tool-use-works", "The model never runs anything on its own."),),
        qtype="diagnose", level="easy", principle="fit_for_purpose",
        situation="new replacement tool is called correctly but nothing changes in the order system",
        trap="blame Claude's write access to the backend",
    ),
    MCQ(
        id="Q1.1-04",
        q=("To cut latency on your support agent, an engineer proposes a shortcut: when Claude requests `lookup_order`, the "
           "code runs it and shows the order record straight to the customer, skipping the next model call. Logs show that "
           "after a lookup, about 40% of conversations go on to `process_refund` or `escalate_to_human`. How should you "
           "evaluate the proposal?"),
        opts=("Accept it: records from the backend are authoritative, so the model adds nothing after a lookup.",
              "Reject it: Claude has to receive that output in order to work out what the case needs next.",
              "Reject it: raw records read poorly in chat, so a model should always rewrite them for customers.",
              "Accept it for plain status questions, using a keyword check on each message to pick those out."),
        ans=1,
        explain=("The loop is not finished when a tool runs: the output goes back so the model can reason about the next action, "
                 "and here 40% of cases need one. A confuses accurate data with a decision about what to do next. C reaches the "
                 "right verdict for a minor reason; a formatting template would answer it, and the next action would still be "
                 "lost. D replaces the model's reasoning with a keyword rule."),
        scenarios=(1,), points=("1.1:K1", "1.1:K2"),
        evidence=(Evidence("api:agents-and-tools/tool-use/how-tool-use-works", "The model can’t run your code, so every tool call is a round trip: the model asks, you execute, you report back, the model continues."),),
        qtype="evaluate", level="medium", principle="model_driven",
        situation="latency shortcut shows order records directly and skips the next model call",
        trap="treat the tool result as the end of the loop",
    ),
    # ---- K2: results in history ----
    MCQ(
        id="Q1.1-05",
        q=("A test-fixing agent runs the suite through `Bash`. To keep history small, a helper replaces each test output with "
           "just `exit code 1` before adding it as the tool result. Since then the agent edits unrelated files in 35% of runs "
           "and often re-runs the suite with no change. Its reasoning says it cannot tell which test failed. What is the most "
           "likely root cause?"),
        opts=("`Bash` is an unreliable way to run tests, and a dedicated test tool would give the agent steadier results.",
              "The model can only reason from what reaches its history, and the helper removed the failure details.",
              "The model is too weak for debugging work, and a higher-tier model would work out which test had failed.",
              "The system prompt lacks an instruction to read the test output with care before it edits any of the files."),
        ans=1,
        explain=("Tool results are how new information reaches the next decision, and the failing test's name never arrived; the "
                 "agent even says so. A blames a tool that ran correctly. C expects a better model to recover facts it was never "
                 "given. D tells the model to read carefully, but the output is no longer there to read."),
        scenarios=(4,), points=("1.1:K2",),
        evidence=(Evidence("code:how-claude-code-works", "Each tool use returns information that feeds back into the loop, informing Claude's next decision."),),
        qtype="diagnose", level="medium", principle="preserve_information",
        situation="helper reduces test output to an exit code and the agent edits unrelated files",
        trap="upgrade the model when the facts were removed",
    ),
    MCQ(
        id="Q1.1-06",
        q=("Your web search subagent must `search`, then `fetch_source` using URLs from the search results. To shrink requests, "
           "the loop keeps only the latest `tool_use` and `tool_result` pair in history. The agent now searches again before nearly every fetch, "
           "tripling its calls, and its citations sometimes point at the wrong URL. Which change is most effective?"),
        opts=("Hard-code each run in code to alternate one search with one fetch, so that the order can never drift.",
              "Instruct the agent, through its prompt, to memorise each URL and avoid searching one topic twice.",
              "Switch this subagent to a higher-capacity model, so that URLs from past searches are recalled reliably.",
              "Keep earlier tool results in history, and trim their verbose fields instead of dropping whole results."),
        ans=3,
        explain=("Each iteration should build on all earlier results, and dropping them removes the URLs the next step needs. "
                 "Trimming unneeded fields still meets the goal of smaller requests. A swaps model-driven reasoning for a fixed "
                 "order and still loses the URLs. B asks the model to remember what is no longer in its context. C does not help, "
                 "because the loop is deleting the data, whatever the window size."),
        scenarios=(3,), points=("1.1:K2", "1.1:S2"),
        evidence=(Evidence("api:agents-and-tools/tool-use/how-tool-use-works", "Send a new request containing the original messages, the assistant’s response, and a user message with the `tool_result` blocks."),),
        qtype="choose", level="medium", principle="preserve_information",
        situation="loop keeps only the latest tool result so the agent re-searches before every fetch",
        trap="tell the model to memorise URLs",
    ),
    MCQ(
        id="Q1.1-07",
        q=("Customers often hold several orders, and your support agent calls `get_customer`, reads the returned order list, "
           "then calls `lookup_order` for the one that matches the complaint. To save a round trip, an engineer proposes "
           "making the agent request both tools together in its first response. How should you evaluate this?"),
        opts=("Keep two iterations: the second call's input depends on what the first one returns.",
              "Adopt it: the model can infer a likely order number from what the customer has said.",
              "Adopt it: code can fill in the order number on the second call once the first returns.",
              "Adopt it: parallel calls run faster, and a wrong order can be corrected in a later turn."),
        ans=0,
        explain=("Choosing the order requires reasoning over the list, and that list exists only once the first result is in the "
                 "history. B has the model guess an identifier before it has the data. C moves the choice into code, which "
                 "cannot match a complaint to an order the way the model can. D accepts lookups on wrong orders as a cost of "
                 "speed, and the saving is lost to correction turns."),
        scenarios=(1,), points=("1.1:K2",),
        evidence=(Evidence("code:how-claude-code-works", "Each tool use gives Claude new information that informs the next step."),),
        qtype="evaluate", level="hard", principle="model_driven",
        situation="proposal to request get_customer and lookup_order together when the order comes from the list",
        trap="let code fill in the second call's input",
    ),
    # ---- K3: model-driven vs fixed sequences ----
    MCQ(
        id="Q1.1-08",
        q=("Your web research subagent always runs search, then fetches the top three hits, then summarises. On niche topics "
           "only 2 of 10 hits are relevant, so one fetch in three is noise; on simple topics the first search already "
           "answers the question, yet three pages are fetched anyway. Which redesign best addresses both problems?"),
        opts=("Add branches keyed on hit count and topic type, so the code picks the right number of fetches per run.",
              "Have Claude write its complete tool plan at the start, and then execute that plan without any revisions.",
              "Give Claude the goal and tools in a loop, so each next call is chosen from what the last result showed.",
              "Raise the fixed fetch count to ten, so that a relevant page is nearly always among those that are read."),
        ans=2,
        explain=("The right next step depends on what the last result contained, so the choice belongs with the model inside "
                 "the loop. A grows a decision tree that still cannot read the results. B is still a fixed sequence, only "
                 "written earlier, and it is set before any result exists. D makes the noise and the waste on simple topics "
                 "worse."),
        scenarios=(3,), points=("1.1:K3",),
        evidence=(Evidence("code:how-claude-code-works", "Claude decides what each step requires based on what it learned from the previous step, chaining dozens of actions together and course-correcting along the way."),),
        qtype="choose", level="medium", principle="model_driven",
        situation="research subagent fetches three pages on every topic whatever the search returned",
        trap="add branches on hit count to the code",
    ),
    MCQ(
        id="Q1.1-09",
        q=("A legacy-system assistant classifies each ticket as build, test or runtime, then follows that category's fixed "
           "tool order: for example `Grep`, then `Read`, then `Bash`. Results reach the model correctly. In a review of 300 "
           "runs, 28% reached a wrong conclusion, and in most of those the first `Read` had pointed at a generated config "
           "that the fixed order never opened. What is the most likely root cause?"),
        opts=("The next step was fixed before the results existed, so what `Read` revealed could not change the route.",
              "Three categories are too few, and a larger trained classifier would have sent these tickets to better paths.",
              "`Grep` returned too few matches for the agent to find the config, so a better search tool is needed first.",
              "The model lost the `Read` output between iterations, because the tool results were not reaching its history."),
        ans=0,
        explain=("The failing runs found the lead and could not follow it, because the order was set in advance. B adds more "
                 "fixed paths, and new categories still cannot react to a result. C blames `Grep`, yet the first `Read` "
                 "had already reached the lead. D contradicts the stem, which says results reached the model."),
        scenarios=(4,), points=("1.1:K3",),
        evidence=(Evidence("code:how-claude-code-works", "Each tool use gives Claude new information that informs the next step."),),
        qtype="diagnose", level="medium", principle="model_driven",
        situation="ticket categories force a tool order that never opens the generated config",
        trap="add more categories with a trained classifier",
    ),
    MCQ(
        id="Q1.1-10",
        q=("Each new microservice needs the same four steps: render the service template, add the standard config, add the "
           "CI file, run the linter. Over 400 past runs, the steps never changed and the order never mattered to any "
           "result; lint failures simply stop the job for an engineer. Which design fits this task best?"),
        opts=("A model-driven loop with every tool available, because letting Claude choose is always more reliable.",
              "A coordinator with four subagents, one per step, so that each step gets its own focused context.",
              "A model-driven loop with an extra instruction listing the four steps that it should always follow.",
              "A fixed sequence of the four steps, because nothing here depends on judging an earlier result."),
        ans=3,
        explain=("Model-driven choice earns its place when the next step depends on what was just learned; here the path is known "
                 "in advance, so a fixed sequence is simpler and repeatable. A overrates autonomy, since there is nothing to "
                 "decide. B adds orchestration to four predictable steps. C pays for reasoning and then tells the model what to "
                 "do anyway, with only a prompt holding the order."),
        scenarios=(4,), points=("1.1:K3", "1.6:K1"),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 1.1 and TS 1.6 set out when a fixed sequence suits a predictable workflow; no official page states this judgment.",
        qtype="choose", level="hard", principle="fit_for_purpose",
        situation="identical four-step service scaffolding with no decision points over 400 runs",
        trap="assume model-driven is always better",
    ),
    MCQ(
        id="Q1.1-11",
        q=("A monthly dependency-upgrade agent must update the lockfile, run the tests, repair anything that broke, then "
           "open a pull request. The first, second and last steps never vary. Repairs vary widely: some need one import "
           "changed, others need several files read and a changelog checked. Which design is most effective?"),
        opts=("Let Claude choose every step in one open loop, so the whole job adapts to each repository.",
              "Fix the outer stages in code, and run a model-driven loop for the repair stage alone.",
              "Fix all stages in code, and give the repair stage three scripted retries of one prompt.",
              "Fix all stages in code, and map each known test error message to a stored repair recipe."),
        ans=1,
        explain=("Each part gets the control it needs: the stages are known in advance, and only the repair depends on what each "
                 "result reveals. A gives up a repeatable order for steps that hold no decision. C repeats the same attempt "
                 "without letting the model investigate. D is a decision tree, which fails on any error it has not seen."),
        scenarios=(4,), points=("1.1:K3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the split follows from TS 1.1 Knowledge 3 and TS 1.6; no official page states this design.",
        qtype="choose", level="hard", principle="model_driven",
        situation="upgrade job with fixed outer stages and an unpredictable repair stage",
        trap="map known test errors to stored recipes",
    ),
    # ---- S1: control flow ----
    MCQ(
        id="Q1.1-12",
        q=("Your report subagent's loop is written `while response.stop_reason != \"end_turn\"`. In 6% of runs it reaches its "
           "25-call guard. The traces show `stop_reason: \"max_tokens\"` from about the fourth call on, with no `tool_use` "
           "blocks, so the loop finds nothing to run and sends the request again. What is the most effective fix?"),
        opts=("Raise the guard from 25 calls to 100, so that long reports have more chances of reaching `end_turn`.",
              "Raise `max_tokens` for this subagent and leave the loop condition just as it is written today.",
              "Loop only while `stop_reason` is `tool_use`, then branch on whichever other value ended the loop.",
              "Exit the loop as soon as a response contains any text, and treat that text as the finished report."),
        ans=2,
        explain=("Looping until `end_turn` retries every other stop reason, including ones with no tool to run. The loop should "
                 "continue only on `tool_use`, and any other value exits and gets handled. A lets the same request repeat for "
                 "longer. B helps this one stop reason, but a refusal would spin the same way. D is the text-as-completion "
                 "anti-pattern and would also accept the truncated output."),
        scenarios=(3,), points=("1.1:S1",),
        evidence=(Evidence("api:agents-and-tools/tool-use/how-tool-use-works", "The loop exits on any other stop reason"),
                  Evidence("api:agents-and-tools/tool-use/how-tool-use-works", "Repeat from step 2 while `stop_reason` is `\"tool_use\"`.")),
        qtype="fix", level="medium", principle="model_driven",
        situation="report loop written as not-equal end_turn resends after truncation until the guard",
        trap="raise max_tokens and keep the condition",
    ),
    MCQ(
        id="Q1.1-13",
        q=("A legacy-code explainer answers one-file questions well. On questions that span several modules, about 30% of "
           "answers end with \"Next I will read the billing module\", and nothing follows. In those runs the second response "
           "has `stop_reason: \"tool_use\"`, its `Read` call never executes, and the code returns that response's text. What "
           "is the most effective change?"),
        opts=("Raise `max_tokens`, so that the second response has enough room to finish the whole explanation.",
              "Instruct the agent, through its prompt, to collect all it needs within its opening response.",
              "Set `tool_choice` to `any` on every request, so that the agent always carries on working to the end.",
              "Replace the single tool pass with a loop that repeats until a response stops asking for tools."),
        ans=3,
        explain=("The model asked for another tool and the code did not honour it, so tool handling has to repeat for as long as "
                 "`stop_reason` is `tool_use`. A treats this as truncation, which would show `max_tokens`. B asks for a fixed "
                 "amount of work up front, although each read decides the next. C misreads the setting: forcing a tool on every "
                 "request means the model can never give its final text answer."),
        scenarios=(4,), points=("1.1:S1", "1.1:K1"),
        evidence=(Evidence("api:agents-and-tools/tool-use/how-tool-use-works", "In practice this reads as: while `stop_reason == \"tool_use\"`, run the tools and continue the conversation."),),
        qtype="fix", level="medium", principle="model_driven",
        situation="explainer stops at the second response's unexecuted Read on multi-module questions",
        trap="force tool_choice any on every request",
    ),
    MCQ(
        id="Q1.1-14",
        q=("A repository summariser has five tools, but small repositories need only two of them. An engineer proposes that "
           "after `stop_reason: \"end_turn\"` the code should check whether every tool was used and, if not, send another "
           "request asking for the rest. Runs currently finish with good summaries. How should you evaluate the proposal?"),
        opts=("Reject it: `end_turn` means Claude has finished, and which tools it needs is its own decision.",
              "Accept it, because a run cannot be complete until each registered tool has been called at least once.",
              "Accept it, but limit it to three extra requests so that the additional tool calls stay under control.",
              "Reject it, and instead hard-code the five tools in a fixed order so that each run uses all of them."),
        ans=0,
        explain=("The loop ends on `end_turn`, and Claude chooses tools from the task, so unused tools are not a defect. B treats "
                 "the tool list as a checklist. C keeps the same mistake with a limit on it. D also ignores what each "
                 "repository needs, by forcing a fixed sequence."),
        scenarios=(4,), points=("1.1:S1", "1.1:K3"),
        evidence=(Evidence("api:agents-and-tools/tool-use/how-tool-use-works", "Claude determines when and how to call them."),),
        qtype="evaluate", level="easy", principle="model_driven",
        situation="summariser proposal to continue after end_turn until all five tools are used",
        trap="treat the tool list as a checklist",
    ),
    # ---- S2: adding results between iterations ----
    MCQ(
        id="Q1.1-15",
        q=("Your document analysis subagent has 30 seconds per round and runs four `fetch_paper` calls concurrently, each taking about 20 seconds. As each finishes, its output is "
           "appended to a list, and the list is zipped with the response's `tool_use` blocks to build the `tool_result` "
           "blocks. No errors appear, but 7% of reports credit findings to the wrong paper. What is the most effective fix?"),
        opts=("Run the fetches one at a time, so outputs always come back in the order the blocks appear in.",
              "Add a step where the synthesis agent checks each citation against the source papers before it writes.",
              "Record each call's `id` when it starts, and set that value as the `tool_use_id` on its own result.",
              "Instruct the model through the system prompt to fetch one paper per response, which avoids any mix-ups."),
        ans=2,
        explain=("The results are paired by finish order, so a fast paper can land on another call's id, and the model then "
                 "reasons from mislabelled evidence. The id is what ties a result to its call. A would take about 80 seconds, well over "
                 "the 30-second budget. B blames a later agent, which has to catch errors the loop "
                 "created. D relies on a prompt and also gives up parallel calls."),
        scenarios=(3,), points=("1.1:S2",),
        evidence=(Evidence("api:agents-and-tools/tool-use/parallel-tool-use", "Match each result to its call with `tool_use_id`, and put every `tool_result` block before any text content in that message."),),
        qtype="fix", level="hard", principle="preserve_information",
        situation="concurrent paper fetches paired with calls by finish order credit the wrong paper",
        trap="serialise the calls to hide the pairing bug",
    ),
    MCQ(
        id="Q1.1-16",
        q=("A scaffolding agent's migration step fails in 12% of runs with `column already exists`. Today the code ends the "
           "run on any failed tool call and pages an engineer. In 50 paged runs, 34 needed only a small next step, such as "
           "checking the schema and skipping that migration. Which change is most effective?"),
        opts=("Have the code retry the failed command three times before it pages an engineer about the run.",
              "Send the failure text back as an error result, so the agent can decide on its own next step.",
              "Report the step to the agent as a success with empty output, so that the run can carry on.",
              "Add a table in code that maps each known database error to the fix that should be applied."),
        ans=1,
        explain=("A failure is new information too: once it reaches the history, the model can check the schema and adapt, and the "
                 "instructive error text tells it what happened. A repeats a command that will fail the same way. C hides the "
                 "failure, so the model builds on a step that did not work. D is a fixed decision table that takes the "
                 "reasoning away from the model and covers only known errors."),
        scenarios=(4,), points=("1.1:S2",),
        evidence=(Evidence("api:agents-and-tools/tool-use/handle-tool-calls", "you can return the error message in the `content` along with `\"is_error\": true`:"),),
        qtype="fix", level="medium", principle="preserve_information",
        situation="migration failure ends the run and pages an engineer though a next step exists",
        trap="retry the failed command in code",
    ),
    MCQ(
        id="Q1.1-17",
        q=("A research subagent repeats each `search_archive` call up to five times, then reports that the archive had no "
           "usable data. The archive's own logs show every query returning 20 or more matching records. In the "
           "conversation history, each of those calls has the same tool result: `status: ok`. What is the most effective fix?"),
        opts=("Expand the tool description, so the agent understands what kind of data the archive gives back.",
              "Cap `search_archive` at one call per run, so that the agent moves on to its other sources sooner.",
              "Tell the model in the prompt to trust the archive and to stop searching after the first attempt.",
              "Return the matched records themselves as the tool result, in place of the bare status line."),
        ans=3,
        explain=("The search worked, but only a status line reached the history, so the model had no new information to reason "
                 "from. A explains the tool better while the records stay missing. B stops the repeats and still gives the "
                 "model nothing. C asks the model to trust data it never received."),
        scenarios=(3,), points=("1.1:S2",),
        evidence=(Evidence("api:agents-and-tools/tool-use/how-tool-use-works", "Your application extracts those arguments, runs the operation (a database query, an HTTP call, a file write, whatever the tool does), and sends the output back in a `tool_result` block on the next request."),),
        qtype="fix", level="easy", principle="preserve_information",
        situation="archive search history holds only a status line so the agent repeats each search",
        trap="cap the tool instead of returning the records",
    ),
    # ---- S3: anti-patterns ----
    MCQ(
        id="Q1.1-18",
        q=("Your support agent is told to write `ROUTE: human` when a case needs a person, and a regex in the loop hands the "
           "conversation over when it sees that string. In 3% of cases the reply says something like \"no need to ROUTE: human "
           "yet\" and the case is handed over wrongly. What is the most effective fix?"),
        opts=("Have the agent call `escalate_to_human`, so the handover is a tool call and not a string in prose.",
              "Tighten the regex so that the marker only counts when it sits alone on the last line of the reply.",
              "Add a system prompt rule that forbids mentioning the marker unless a handover is truly intended.",
              "Run a second model call that reads each reply and judges whether it truly means to hand the case over."),
        ans=0,
        explain=("A control decision hidden in free text is a sign that it belongs in a tool call, which is structured and "
                 "unambiguous. B keeps parsing language and only moves the failure to new wordings. C asks a prompt to protect "
                 "a parser, which reduces the misses without ending them. D adds a second model and more cost to paper over a "
                 "signal that should have been structured."),
        scenarios=(1,), points=("1.1:S3",),
        evidence=(Evidence("api:agents-and-tools/tool-use/how-tool-use-works", "Parsing free-form text to recover structured intent is a sign the structure belongs in the schema."),),
        qtype="fix", level="easy", principle="model_driven",
        situation="handover marker regex fires on replies that merely mention the marker",
        trap="tighten the regex",
    ),
    MCQ(
        id="Q1.1-19",
        q=("A nightly boilerplate job on the Agent SDK sets `max_turns=12`, and its script catches all exceptions and "
           "keeps the last assistant text as the finished work. About 11% of repositories are left half-generated, yet the dashboard shows every run as done. "
           "Most repositories need 6 to 10 turns, and a few need 20 or more. Your lead wants the limit raised. How should "
           "you evaluate that?"),
        opts=("Raise `max_turns` to 200 for all repositories, so that no run can reach the limit in the first place.",
              "Require the agent to end with the word COMPLETE, and have the script search the final text for that word.",
              "Check the result `subtype`, and resume `error_max_turns` runs with a higher limit; 12 is only a guard.",
              "Lower `max_turns` to 8 and split each repository into several jobs, so every job stays within the cap."),
        ans=2,
        explain=("Hitting the cap is an error result, not success, and the `subtype` field is what reports it, so the job can "
                 "resume those runs and keep its guard. A removes the guard and the script would still trust any last text. B "
                 "goes back to parsing language for completion. D treats the cap as the design driver and still cannot tell "
                 "finished work from cut-off work."),
        scenarios=(4,), points=("1.1:S3",),
        evidence=(Evidence("code:agent-sdk/agent-loop", "The `subtype` field (available in both SDKs) is the primary way to check termination state."),
                  Evidence("code:agent-sdk/agent-loop", "Agent ran out of turns. Resume with a higher limit.")),
        basis="docs",
        qtype="evaluate", level="hard", principle="preserve_information",
        situation="nightly generation shows every run as done while a turn cap cuts off 11%",
        trap="raise max_turns to 200",
    ),
    MCQ(
        id="Q1.1-20",
        q=("An engineer ran your Agent SDK assistant on \"improve test coverage across this repo\", and it worked for hours "
           "and ran up a large bill. Your manager proposes `max_turns=10` on every run as the way to stop this. Normal "
           "bug-fix tasks need 30 to 50 turns. How should you evaluate the proposal?"),
        opts=("Accept the idea with a higher cap: use `max_turns=60`, so normal tasks fit and each run ends at that cap.",
              "Reject it: let runs end when Claude finishes, with a `max_budget_usd` guard whose error you handle.",
              "Reject it: have code stop the run as soon as any tool call repeats, since repeats show lost progress.",
              "Accept it, and have Claude state its progress each turn, so code can extend the cap when work remains."),
        ans=1,
        explain=("A limit should guard against runaway work, not be how the loop normally ends, and a budget limit protects spend "
                 "without cutting off normal tasks, as long as the error result is handled. A looks reasonable but keeps a cap "
                 "as the main stop, and open-ended runs would still end cut off. C stops valid work, since re-running tests is a "
                 "repeated call. D keeps the cap too low and parses language to decide whether to go on."),
        scenarios=(4,), points=("1.1:S3",),
        evidence=(Evidence("code:agent-sdk/agent-loop", "Setting a budget is a good default for production agents."),),
        basis="docs",
        qtype="evaluate", level="medium", principle="model_driven",
        situation="open-ended coverage prompt runs for hours and a blanket cap of ten is proposed",
        trap="higher turn cap as the main stop",
    ),
)
