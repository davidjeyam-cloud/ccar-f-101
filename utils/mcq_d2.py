"""
Section 10 · MCQs — Domain 2 (Tool Design & MCP Integration): 20 original questions covering every Knowledge/Skill
bullet of task statements 2.1 – 2.5 in the official exam guide (the 41 bullets are listed in utils/guide_index.py).

Same method as utils/mcq_sets.py (see its docstring): the guide decides scope, each correct answer carries WORD-FOR-WORD
quotes from official pages that `python -m utils.mcq_verify` re-downloads and checks, community repositories were read for
coverage only, and nothing is copied. Where the guide's wording is a convention that no official page documents
(`errorCategory`, `isRetryable`, `retriable: false`), the quotes support the underlying principle only and the item says so.

Coverage (ids → bullets): 2.1 = D2-01..04 · 2.2 = D2-05..09 · 2.3 = D2-10..14 · 2.4 (user scope; the other 2.4 bullets are in
utils/mcq_sets.py MCP-01..10) = D2-15 · 2.5 = D2-16..20.
"""

from utils.mcq_sets import MCQ, Evidence

D2 = (
    # ── TS 2.1 · tool descriptions and boundaries ────────────────────────────────────────────────────────────────
    MCQ(
        id="D2-01",
        q=("A support agent has two tools. `get_customer` is described as “Retrieves customer information” and `lookup_order` as "
           "“Retrieves order details”. In a review of 400 conversations, 23% of requests that contain an order number (for "
           "example “where is order 88412?”) went to `get_customer` first, and the agent then asked the customer for an email "
           "address it did not need. What is the most effective first fix?"),
        opts=("Add a keyword classifier in front of the agent that picks the tool from the customer's message and passes it only that tool.",
              "Rewrite both descriptions with the accepted input formats, what each returns, and when to use the other tool.",
              "Force `lookup_order` with `tool_choice` on every turn so that order questions can no longer reach the other tool.",
              "Move to a model with a larger context window so that both tool definitions are weighed more carefully."),
        ans=1,
        explain=("The description is the main thing the model has to choose a tool by, so a one-line description of each leaves it "
                 "guessing between two tools that both ‘retrieve’ something. Adding inputs (customer id vs order number), outputs and "
                 "‘use the other tool when…’ boundaries fixes the cause (guide TS 2.1, knowledge 1 and 2; skill 1). A builds a router "
                 "around a problem the descriptions can solve; C breaks every non-order question; D changes capacity, not clarity."),
        scenarios=(1,), points=("2.1:K1", "2.1:K2", "2.1:S1"),
        evidence=(Evidence("api_define_tools", "Provide extremely detailed descriptions. This is by far the most important factor in tool performance."),
                  Evidence("api_define_tools", "When it should be used (and when it shouldn't)")),
        community=("paullarionov and OlivierAlter both test ‘minimal descriptions cause misrouting’; this item uses a different tool "
                   "pair and different distractors."),
    ),
    MCQ(
        id="D2-02",
        q=("A research coordinator has `analyze_content` and `analyze_document`. Both are described as “Analyzes content and returns "
           "key information”. Across 200 runs, the coordinator picked the wrong one for 35% of web pages and 31% of PDFs. Which "
           "change most directly removes the overlap?"),
        opts=("Add a system-prompt rule saying to use `analyze_document` for anything that is a file, and keep both tools and their descriptions exactly as they are.",
              "Set `tool_choice` to `any` so that the coordinator must call one of the two tools on every single step.",
              "Give every subagent all 18 tools so that it has more options to fall back on after a wrong first choice.",
              "Rename `analyze_content` to `extract_web_results` with a web-only description that says when to use the other tool."),
        ans=3,
        explain=("Near-identical names and descriptions are the cause of the misrouting, so the fix is in the tools: a name that says "
                 "what the tool is for, a description limited to web results, and a boundary sentence pointing at the other tool "
                 "(guide TS 2.1, knowledge 3; skill 2). A leaves the ambiguity in place and adds a rule to patch it; B only "
                 "guarantees that some tool is called, not the right one; C adds more choices."),
        scenarios=(3,), points=("2.1:K3", "2.1:S2"),
        evidence=(Evidence("api_define_tools", "Use meaningful namespacing in tool names."),
                  Evidence("api_define_tools", "This makes tool selection unambiguous as your library grows")),
        community="OlivierAlter's task index lists tool-description questions; the analyze_content example is the guide's own.",
    ),
    MCQ(
        id="D2-03",
        q=("In a research system one tool, `analyze_document(doc, task)`, is used to pull out data points, to summarise, and to "
           "check a claim against a source. It returns a different shape for each use, and the coordinator passes inconsistent "
           "`task` strings. 17% of downstream steps fail on a malformed result. What should you do?"),
        opts=("Split it into `extract_data_points`, `summarize_content` and `verify_claim_against_source`, each with a defined contract.",
              "Add few-shot examples to the system prompt showing the correct `task` string for each job the tool is used for, and keep one tool.",
              "Lengthen the single description so that it covers all three jobs and each of their different return shapes in one long paragraph.",
              "Let the synthesis agent reshape every output into one common format and ignore which job produced it, whatever the shape."),
        ans=0,
        explain=("One generic tool hides three jobs with three different contracts. Splitting it into purpose-specific tools gives "
                 "each a clear description and a defined input and output (guide TS 2.1, skill 3). B and C try to explain a "
                 "confusing tool instead of removing the confusion; D blames the consumer for a producer problem. (The API docs also "
                 "advise grouping closely related actions into one tool; the guide's split is for jobs whose purposes and "
                 "outputs differ, as here.)"),
        scenarios=(3,), points=("2.1:S3",), basis="docs",
        evidence=(Evidence("api_define_tools", "What each parameter means and how it affects the tool's behavior"),
                  Evidence("api_define_tools", "Fewer, more capable tools reduce selection ambiguity")),
        community="The analyze_document split is the guide's own example (TS 2.1 skill 3); community repos repeat it.",
    ),
    MCQ(
        id="D2-04",
        q=("After a prompt change, a support agent calls `get_customer` in 41% of conversations, including “what is your return "
           "window?”, where `search_kb` is correct. The tool descriptions are detailed and unchanged. The only new line in the "
           "system prompt is “Always verify the customer's account before answering.” What is the most likely cause and fix?"),
        opts=("The tool descriptions are too long and the agent skims them, so shorten each description to one sentence.",
              "Sampling is too random for reliable tool selection, so lower the temperature setting on every request.",
              "The prompt wording ties ‘account’ to one tool; scope it so checks apply only to account questions.",
              "Remove `get_customer` from the agent and call it from application code before every conversation starts, whatever the topic."),
        ans=2,
        explain=("The only thing that changed is the system prompt, and its wording steers which tool the model reaches for. "
                 "Reviewing the prompt for keyword-sensitive instructions and scoping them (‘when the question is about the "
                 "customer's own account’) fixes it without touching good descriptions (guide TS 2.1, knowledge 4; skill 4). "
                 "A undoes the clarity that was working; B treats a wording effect as randomness; D over-engineers and removes "
                 "a tool the agent legitimately needs."),
        scenarios=(1,), points=("2.1:K4", "2.1:S4"), basis="docs",
        evidence=(Evidence("api_tool_use_overview", "This boundary is steerable through your system prompt."),
                  Evidence("api_tool_use_overview", "If Claude isn't calling tools when you expect, a light instruction such as")),
        community="Keyword-sensitive system prompts appear in OlivierAlter's TS 2.1 questions; stem and options here are original.",
    ),
    # ── TS 2.2 · structured errors ───────────────────────────────────────────────────────────────────────────────
    MCQ(
        id="D2-05",
        q=("The `process_refund` tool of a support agent fails for three reasons: bad input (a negative amount), a payment-service "
           "outage, and a policy limit. In all three cases the MCP server returns the text “Refund failed” as ordinary content, "
           "and the agent tells 9% of customers their refund was issued. What is the most effective fix?"),
        opts=("Add a line to the system prompt: if the output of a tool contains the word “failed”, treat the call as unsuccessful and say so.",
              "Return the failure with `isError: true` and an `errorCategory`, so outages, bad input and policy limits are told apart.",
              "Make the MCP server answer with a transport-level HTTP 500 so that the client reports the failure by itself to the user.",
              "Wrap the agent loop in a retry that re-sends the same call whenever the final answer mentions an error."),
        ans=1,
        explain=("The MCP pattern for a tool that ran and failed is a normal result with `isError: true`, which tells the agent "
                 "the call did not succeed; a category then lets it choose between retrying, fixing input and explaining a limit "
                 "(guide TS 2.2, knowledge 1 and 2). A parses text instead of using the flag; C confuses transport errors with "
                 "tool failures; D retries failures that retrying cannot fix. (`errorCategory` is the guide's convention; MCP "
                 "itself defines only the flag.)"),
        scenarios=(1,), points=("2.2:K1", "2.2:K2"),
        evidence=(Evidence("mcp_tools_spec", "They are reported in tool results with `isError: true`"),
                  Evidence("mcp_tools_spec", "contain actionable feedback that language models can use to self-correct and retry with adjusted parameters")),
        community="OlivierAlter Q34 tests the isError pattern; this item covers all three failure kinds instead.",
    ),
    MCQ(
        id="D2-06",
        q=("Every failure from a support agent's tools reads “Operation failed”. In 600 logged failures the agent retried the same "
           "call three times in 71% of cases, even when the input was invalid, adding about 9 seconds each time. Which change "
           "most directly stops the wasted retries?"),
        opts=("Lower the loop's retry limit from three to one for every tool, whatever the kind of failure it hits.",
              "Add “never retry a failed tool call” to the system prompt for all failures from every tool, including timeouts.",
              "Return the raw stack trace of each exception so that the agent can work out for itself what has happened.",
              "Return `errorCategory`, `isRetryable` and a short description so only transient failures get retried."),
        ans=3,
        explain=("A uniform message gives the agent nothing to decide with. Structured metadata separates retryable failures "
                 "(timeouts) from non-retryable ones (invalid input), so retries are spent only where they can help (guide TS 2.2, "
                 "knowledge 3 and 4; skill 1). A and B also cut off the retries that do help; C is long and unstructured, and "
                 "leaks internals."),
        scenarios=(1,), points=("2.2:K3", "2.2:K4", "2.2:S1"),
        evidence=(Evidence("api_handle_calls", "Instead of generic errors like"),
                  Evidence("api_handle_calls", "include what went wrong and what Claude should try next")),
        community="`errorCategory` and `isRetryable` are the guide's wording; community repos repeat them. No official page names these fields.",
    ),
    MCQ(
        id="D2-07",
        q=("A customer asks for a $900 refund; the policy limit is $500. The tool returns `isError: true` with the text “Request "
           "denied”. The agent retries at $899, then splits the refund into two calls, and finally tells the customer there was "
           "a technical problem. What should the tool return instead?"),
        opts=("An error flagged `retriable: false`, with a customer-friendly explanation of the limit the agent can relay.",
              "An error categorised as transient, so that the agent waits and retries once the policy check has refreshed itself.",
              "An empty result without an error, so the agent does not try to reword the refund request.",
              "A plain success message, with the limit enforced by a rule in the system prompt rather than in the tool."),
        ans=0,
        explain=("A policy violation is a business error: retrying cannot change it. Flagging it as not retriable and giving a "
                 "customer-friendly reason lets the agent stop retrying and say something true (guide TS 2.2, skill 2). B mislabels "
                 "it as temporary; C hides the failure behind ‘success’; D moves a hard rule into a prompt, where it can be talked "
                 "around."),
        scenarios=(1,), points=("2.2:S2",),
        evidence=(Evidence("api_handle_calls", "include what went wrong and what Claude should try next"),
                  Evidence("mcp_tools_spec", "Clients **SHOULD** provide tool execution errors to language models to enable self-correction.")),
        community="`retriable: false` with a customer-friendly message is the guide's wording (TS 2.2 skill 2); no official page defines it.",
    ),
    MCQ(
        id="D2-08",
        q=("In a research system the web-search subagent sometimes hits a timeout. Today it passes a bare error to the coordinator, "
           "which abandons the whole report even when 4 of 5 sources were fetched. Which design is best?"),
        opts=("Have the subagent report every timeout to the coordinator at once, so that the coordinator decides about each retry.",
              "Let the coordinator discard the subagent's result and re-run the whole research task again from the beginning.",
              "Retry timeouts in the subagent; escalate only what stays unresolved, with partial results and attempts made.",
              "Have the subagent return the 4 successful sources and leave out any mention at all of the one that failed."),
        ans=2,
        explain=("Transient failures are cheap to fix where they happen. Only what cannot be resolved locally goes up, together "
                 "with the partial results and what was attempted, so the coordinator can decide with the facts (guide TS 2.2, "
                 "skill 3). A moves every small problem up a level; B throws away good work; D silently hides a gap in the "
                 "evidence."),
        scenarios=(3,), points=("2.2:S3",), basis="docs",
        evidence=(Evidence("cc_subagents", "the subagent does that work in its own context and returns only the summary"),),
        community="Local recovery then escalation with partial results is the guide's TS 2.2 skill 3; the docs quote supports only the ‘returns only a summary’ part.",
    ),
    MCQ(
        id="D2-09",
        q=("A search tool in a research system returns `[]` both when nothing matches and when the index request times out. In 12% "
           "of runs the agent concludes “no evidence exists” although a later manual check found some. What change fixes the "
           "cause?"),
        opts=("Return the string “no results” in place of `[]` for both cases, which the agent will read more reliably than an empty list.",
              "Return a timeout as a retryable error, and ‘no matches’ as a normal, successful, empty result.",
              "Run every search twice and treat two empty answers as proof that nothing at all exists.",
              "Treat every empty result as an access failure and retry it three times before accepting it."),
        ans=1,
        explain=("The two situations mean different things: a failed access says nothing about the data, while an empty "
                 "result from a working query is a real answer. They need different signals so the agent can retry one and "
                 "accept the other (guide TS 2.2, skill 4). A renames the same ambiguity; C repeats a call that may fail the same "
                 "way twice; D wastes calls on valid empty answers."),
        scenarios=(3,), points=("2.2:S4",), basis="docs",
        evidence=(Evidence("api_handle_calls", "If the tool itself throws an error during execution"),),
        community="OlivierAlter and dnacenta both note ‘empty result vs error’ under TS 2.2; the stem and options are original.",
    ),
    # ── TS 2.3 · tool distribution and tool_choice ───────────────────────────────────────────────────────────────
    MCQ(
        id="D2-10",
        q=("A synthesis subagent in a research system was given the same 18 tools as the coordinator. In 28% of runs it tries web "
           "searches during synthesis and picks a wrong tool among near-neighbours. What is the most effective change?"),
        opts=("Add a system-prompt rule saying the synthesis agent must never search, and keep all 18 tools available to it.",
              "Add three more tools with detailed descriptions, so each of its jobs has its own more specific tool.",
              "Set `tool_choice` to `auto` explicitly, because the searches come from the default being `any`.",
              "Give it only the few tools its role needs, and leave searching to the search subagent."),
        ans=3,
        explain=("An agent with tools outside its specialty tends to use them, and a long tool list makes every choice harder. "
                 "Scoping the tool set to the role removes both problems (guide TS 2.3, knowledge 1, 2 and 3; skill 1). A leaves the "
                 "temptation in place; B adds more choices; C misreads the parameter: with tools provided, `auto` already is the "
                 "default. (The docs put the point where selection degrades at 30–50 tools; the guide's 18 versus 4–5 illustrates "
                 "the same direction.)"),
        scenarios=(3,), points=("2.3:K1", "2.3:K2", "2.3:K3", "2.3:S1"),
        evidence=(Evidence("cc_subagents", "To restrict tools, use the `tools` field as an allowlist or the `disallowedTools` field as a denylist."),
                  Evidence("cc_subagents", "Inherits every tool available to subagents if omitted."),
                  Evidence("api_tool_search", "Claude's ability to pick the right tool degrades once you exceed 30–50 available tools.")),
        community="The synthesis agent that searches the web is the guide's own example (TS 2.3 knowledge 2).",
    ),
    MCQ(
        id="D2-11",
        q=("A synthesis subagent has 4 tools and no web access. In 3 of 10 reports it needs a quick check of a date or a name; "
           "each check is routed through the coordinator and adds about 40% to the run time. Giving it the full search toolset "
           "earlier caused misuse. What is the best design?"),
        opts=("Give it a narrow `verify_fact` tool for simple checks; route complex ones through the coordinator.",
              "Give it the full web-search toolset for every report, because it will only use the tools when it really does need them.",
              "Remove verification from the synthesis agent and add a separate verification pass at the end of every report.",
              "Let it call the search subagent directly for every fact, so that the coordinator is bypassed completely."),
        ans=0,
        explain=("A small, scoped cross-role tool covers the frequent simple need without handing over the whole search toolset; "
                 "complex cases still go through the coordinator (guide TS 2.3, knowledge 3; skill 3). B repeats the misuse that "
                 "already happened; C changes the workflow without removing the round trips for mid-report checks; D removes the "
                 "coordinator's control."),
        scenarios=(3,), points=("2.3:K3", "2.3:S3"),
        evidence=(Evidence("cc_subagents", "Inherits every tool available to subagents if omitted."),
                  Evidence("cc_subagents", "To restrict tools, use the `tools` field as an allowlist or the `disallowedTools` field as a denylist.")),
        community="`verify_fact` is the guide's own example; the docs quotes support only the narrowing of a subagent's tools.",
    ),
    MCQ(
        id="D2-12",
        q=("Research subagents use a generic `fetch_url(url)`. In 9% of calls it fetches a login page, an image or an internal admin "
           "URL, and the agent then reasons over useless content. Which change best addresses the cause?"),
        opts=("Describe in the system prompt which kinds of URL are acceptable, and leave the `fetch_url` tool itself unchanged.",
              "Add a second tool, `fetch_any_url`, with a longer description, and let the agent choose between the two tools.",
              "Replace it with `load_document`, which checks that the URL points to a supported document before fetching.",
              "Wrap `fetch_url` in a retry so that a rejected page is fetched again until a document comes back."),
        ans=2,
        explain=("The cause is a tool that accepts anything. A constrained replacement that validates its input removes the bad "
                 "calls instead of asking the model to avoid them (guide TS 2.3, skill 2). A relies on instructions; B adds an "
                 "even more generic tool; D repeats a call whose result is wrong rather than failed."),
        scenarios=(3,), points=("2.3:S2",), basis="docs",
        evidence=(Evidence("cc_subagents", "To restrict tools, use the `tools` field as an allowlist or the `disallowedTools` field as a denylist."),),
        community=("`load_document` replacing `fetch_url` is the guide's example (TS 2.3 skill 2); no official page discusses it, so the "
                   "quote supports only the idea that a subagent's tool access is narrowed on purpose."),
    ),
    MCQ(
        id="D2-13",
        q=("An extraction pipeline offers `extract_metadata` and three enrichment tools. In 14% of runs the model starts with an "
           "enrichment tool, and the records come out mismatched. Metadata must always be extracted first. Which configuration "
           "fixes this?"),
        opts=("Use `tool_choice: any` for the whole conversation, so that the model has to call some tool at every single step.",
              "Force `extract_metadata` on the first request, then continue in follow-up turns with the other tools.",
              "Keep `auto` and add “always call extract_metadata first” to the system prompt as the opening sentence of it.",
              "Force `extract_metadata` on every request in the loop so that each later step also begins with that same call."),
        ans=1,
        explain=("Forced selection (`{\"type\": \"tool\", \"name\": \"extract_metadata\"}`) guarantees the first call; the next "
                 "steps are separate turns with a different setting (guide TS 2.3, knowledge 4; skill 4). A guarantees only that "
                 "some tool is called; C is a request, not a guarantee; D would force the same call forever. Forced selection is "
                 "not accepted by every model or setting, so check that before relying on it."),
        scenarios=(6,), points=("2.3:K4", "2.3:S4"),
        evidence=(Evidence("api_define_tools", "`tool` forces Claude to always use a particular tool."),
                  Evidence("api_define_tools", "Not every model and setting supports forced tool use.")),
        community="Forcing `extract_metadata` first is the guide's example (TS 2.3 skill 4); options here are original.",
    ),
    MCQ(
        id="D2-14",
        q=("An extraction service has `extract_invoice`, `extract_receipt` and `extract_contract`, and documents of unknown type. With "
           "`tool_choice: auto`, 8% of requests come back as conversational text (“This looks like an invoice…”) rather than a "
           "structured extraction. What is the correct setting?"),
        opts=("Force `extract_invoice` on every request, since invoices are the most common kind of document we receive.",
              "Keep `auto` and add “respond only with a tool call” as a sentence in the system prompt.",
              "Set `tool_choice` to `none` and parse the JSON out of the model's text replies on the application side.",
              "Set `tool_choice` to `any`; the model must call an extraction tool but chooses which one."),
        ans=3,
        explain=("`any` guarantees a tool call without fixing which tool, which is what an unknown document type needs. A "
                 "would send receipts and contracts through the invoice schema; B asks for what only a setting can guarantee; "
                 "C turns tools off. (With `any` or a forced tool the model writes no text before the tool call.)"),
        scenarios=(6,), points=("2.3:K4", "2.3:S5"),
        evidence=(Evidence("api_define_tools", "`any` tells Claude that it must use one of the provided tools, but doesn't force a particular tool."),
                  Evidence("api_define_tools", "`auto` allows Claude to determine whether to call any provided tools or not.")),
        community="OlivierAlter and paullarionov test auto/any/forced; the unknown document type setting here is original.",
    ),
    # ── TS 2.4 · MCP servers (user scope; the other 2.4 bullets are MCP-01..10) ─────────────────────────────────
    MCQ(
        id="D2-15",
        q=("An engineer wants to try an experimental Postgres MCP server in every repository she works on. Her teammates should not "
           "see it, and nothing should change in any repository. Where should she configure it?"),
        opts=("At user scope, in `~/.claude.json`: private to her and available in all of her projects.",
              "In each repository's `.mcp.json` file, and ask all of her teammates to ignore the entry.",
              "At project scope in every repository she uses, then remove all the entries again when the experiment ends.",
              "In the repository's CLAUDE.md file, which Claude Code reads in order to start any server that the file mentions."),
        ans=0,
        explain=("Personal and experimental servers belong in user-scoped configuration, which is cross-project and private "
                 "(guide TS 2.4, knowledge 1; skill 2). B and C commit her experiment into shared files; D describes a feature "
                 "that does not exist, since CLAUDE.md holds instructions, not server definitions."),
        scenarios=(4,), points=("2.4:K1", "2.4:S2"),
        evidence=(Evidence("cc_mcp", "User-scoped servers are stored in `~/.claude.json` and provide cross-project accessibility, making them available across all projects on your machine while remaining private to your user account."),),
        community="paullarionov §4.3 and dnacenta §2.4 both describe user scope; the ‘every repository’ framing here is original.",
    ),
    # ── TS 2.5 · built-in tools ──────────────────────────────────────────────────────────────────────────────────
    MCQ(
        id="D2-16",
        q=("A developer asks the agent to find every caller of `calculate_tax` in a 3,000-file repository before changing its "
           "signature. Which approach is the most direct?"),
        opts=("Glob for `**/*tax*` and read the files that come back, since callers are likely to have ‘tax’ in their names.",
              "Read each source folder in turn and look for the function name while scanning every file in it.",
              "Search the file contents for `calculate_tax` with Grep, then read the files it points to.",
              "Read the file that defines `calculate_tax`, since the list of its callers is at the top of it."),
        ans=2,
        explain=("Finding callers is a content search: Grep looks inside files for a function name, an error message or an import. "
                 "Glob matches file names, so A finds files named like the function, not files that call it (guide TS 2.5, "
                 "knowledge 1; skill 1). B reads everything; D assumes a list that source files do not contain."),
        scenarios=(2,), points=("2.5:K1", "2.5:S1"),
        evidence=(Evidence("cc_tools", "The Grep tool searches file contents for patterns. Where Glob finds files by name, Grep finds lines inside them."),),
        community="Grep for callers and Glob for names is the guide's pairing; every community repo repeats it.",
    ),
    MCQ(
        id="D2-17",
        q=("A CI job needs the list of every `*.test.tsx` file in a monorepo to see which components have no test next to them. "
           "Which approach returns it?"),
        opts=("Grep the whole repository for the word `test` and collect the file names that appear in the results.",
              "Glob with the pattern `**/*.test.tsx`, which matches files by name at any depth.",
              "Read the `src` directory to get its listing and pick the files with the right extension.",
              "Read `package.json` and infer the test files from its `scripts` entries."),
        ans=1,
        explain=("Matching files by a name pattern is what Glob does; `**` matches at any depth (guide TS 2.5, knowledge 2; "
                 "skill 2). A searches contents and would also return every file that merely mentions ‘test’; C fails because "
                 "Read reads files, not directories; D guesses from a script that may not list them."),
        scenarios=(5,), points=("2.5:K2", "2.5:S2"),
        evidence=(Evidence("cc_tools", "The Glob tool finds files by name pattern."),
                  Evidence("cc_tools", "`**/*.js` matches all `.js` files at any depth"),
                  Evidence("cc_tools", "Read only reads files, not directories.")),
        community="`**/*.test.tsx` is the guide's own example (TS 2.5 skill 2).",
    ),
    MCQ(
        id="D2-18",
        q=("The agent must change one `timeout: 30` line in a config file that contains four identical, copy-pasted blocks. Each "
           "block is the same for dozens of lines around the target, so no longer snippet is unique, and only one of the four "
           "should change. Edit keeps failing. What is the reliable approach?"),
        opts=("Run the same Edit again until the tool accepts one of the matches.",
              "Set `replace_all` so that all four blocks change, then restore three by hand.",
              "Grep for the line, then Write only that line back, since Write updates just what it is given.",
              "Read the whole file, then Write the full file back with only the intended line changed."),
        ans=3,
        explain=("Edit needs the text it replaces to appear exactly once. When no unique anchor exists, the fallback is to read "
                 "the full file and write the full updated content (guide TS 2.5, knowledge 3 and 4; skill 3). A repeats a call "
                 "that cannot succeed; B changes the wrong blocks first; C ignores that Write overwrites the whole file and does "
                 "not merge, so it would destroy the rest. (The docs' first resort is a longer anchor or `replace_all`; here "
                 "neither fits the case.)"),
        scenarios=(2,), points=("2.5:K3", "2.5:K4", "2.5:S3"),
        evidence=(Evidence("cc_tools", "`old_string` must appear exactly once."),
                  Evidence("cc_tools", "The Write tool creates a new file or overwrites an existing one with the full content provided. It doesn't append or merge.")),
        community="Read + Write as the fallback for a non-unique Edit is the guide's wording; community repos repeat it.",
    ),
    MCQ(
        id="D2-19",
        q=("A new teammate asks the agent how checkout works in an unfamiliar 900-file repository. The agent starts by reading every "
           "file and reaches 70% of its context before it has answered. Which approach is better?"),
        opts=("Grep for entry points first, then Read the hits and follow imports.",
              "Glob every source file and read them all in alphabetical order, summarising each one as it goes.",
              "Concatenate the whole repository into one very large file and read that file in a single pass.",
              "Switch to a model with a larger context window and keep on reading every single file first."),
        ans=0,
        explain=("Understanding is built step by step: search to locate where the flow starts, then read only what the trail "
                 "leads to (guide TS 2.5, skill 4). B, C and D all still read everything up front, only more neatly or with a "
                 "bigger window."),
        scenarios=(4,), points=("2.5:S4",),
        evidence=(Evidence("cc_tools", "to search for specific content with Grep instead"),),
        community="OlivierAlter and dnacenta describe ‘Grep to find entry points, then Read to follow imports’; the repo is original.",
    ),
    MCQ(
        id="D2-20",
        q=("The agent must find every use of a payments helper that application code reaches through a wrapper module. The wrapper "
           "re-exports it under other names (`pay_charge`, `pay_refund`). A search for the helper's original name finds only 2 of "
           "about 40 usages. What should the agent do?"),
        opts=("Search again for the original name using different regular-expression flags and case settings.",
              "Search for the wrapper's file name and assume that every importer of it uses the helper.",
              "Read the wrapper to list its exported names, then search the codebase for each name.",
              "Glob for files with ‘pay’ in their names and read all of the files that come back in full."),
        ans=2,
        explain=("Callers use the exported names, not the original one. List what the wrapper exports first, then search for "
                 "each exported name (guide TS 2.5, skill 5). A repeats a search that cannot match; B counts importers rather than "
                 "usages; D matches file names, which says nothing about who calls what."),
        scenarios=(4,), points=("2.5:S5",),
        evidence=(Evidence("cc_tools", "Claude can scope results by file with the `glob` parameter"),
                  Evidence("cc_tools", "Grep finds lines inside them.")),
        community="Tracing usage through wrapper modules is the guide's TS 2.5 skill 5; the community repos I read only restate it.",
    ),
)
