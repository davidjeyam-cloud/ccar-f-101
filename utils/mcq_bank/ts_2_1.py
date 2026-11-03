"""Exam bank · TS 2.1. Original questions; see docs/MCQ_BANK_PLAN.md."""
from utils.mcq_sets import MCQ, Evidence

TS = "2.1"
BULLETS = {
    "K1": "Descriptions are the main thing the model selects a tool by; minimal ones make selection among similar tools unreliable",
    "K2": "Descriptions should carry input formats, example queries, edge cases and boundaries against other tools",
    "K3": "Ambiguous or overlapping descriptions cause misrouting between near-identical tools",
    "K4": "System prompt wording can create unintended tool associations through keyword-sensitive instructions",
    "S1": "Writing descriptions that differentiate purpose, inputs, outputs and when to use a tool versus alternatives",
    "S2": "Renaming tools and updating descriptions to remove functional overlap",
    "S3": "Splitting a generic tool into purpose-specific tools with defined input and output contracts",
    "S4": "Reviewing system prompts for keyword-sensitive instructions that override good descriptions",
}

DEFINE = "api:agents-and-tools/tool-use/define-tools"
TROUBLE = "api:agents-and-tools/tool-use/troubleshooting-tool-use"
OVERVIEW = "api:agents-and-tools/tool-use/overview"

QUESTIONS = (
    # ---- K1: minimal descriptions ----
    MCQ(
        id="Q2.1-01",
        q=("Your team registered `find_usages`, a custom tool that returns resolved references to a symbol across the monorepo, "
           "including calls made through interfaces. Its description is \"Finds usages.\" In a sample of 300 refactoring tasks the "
           "agent used the built-in Grep to find callers in 86% of them, and 9% of the rename tasks broke callers reached through "
           "interfaces. Grep is still needed for comments and config files, and rename requests rarely contain the word "
           "\"usages\". Which change is most effective?"),
        opts=("Take Grep away from the agent, which leaves `find_usages` as the only way to look for callers in the repo.",
              "Force `find_usages` with `tool_choice` on each turn of the refactoring tasks, so Grep is never picked.",
              "Rewrite the description: what it returns, that it follows interface calls, and when text search is better.",
              "Add a system prompt line telling the agent to prefer `find_usages` whenever a task mentions callers or usages."),
        ans=2,
        explain=("The one-line description gives the model no reason to prefer the custom tool over a tool it already knows, and the "
                 "fix is to say what the tool returns that Grep cannot and where each one fits. A removes a tool the agent still "
                 "needs. B forces the tool on turns that have nothing to do with callers. D ties the choice to a keyword, and "
                 "rename requests do not contain it."),
        scenarios=(4,), points=("2.1:K1",),
        evidence=(Evidence(TROUBLE, "Differentiate tools by WHEN to use them, not only WHAT they do."),),
        qtype="fix", level="medium", principle="explicit",
        situation="custom find_usages with a one-line description loses to built-in Grep",
        trap="remove the competing built-in tool",
    ),
    MCQ(
        id="Q2.1-02",
        q=("Your support agent's tool list grew from 4 to 12 tools as teams added billing, shipping and loyalty lookups. Each new "
           "tool has a one-line description such as \"Gets loyalty data\", and correct tool choice in the weekly sample fell from "
           "96% to 71%. A colleague proposes moving to the largest available model. How should you evaluate this proposal?"),
        opts=("Hold it: with one-line descriptions the tools are hard to tell apart, so improve them and measure again.",
              "Adopt it: a larger model infers each tool's purpose from its name and schema, so short descriptions will do.",
              "Hold it until a tool search layer is in place, because twelve tools are too many for a model to choose between.",
              "Adopt it, and add three worked routing examples to the system prompt in case the larger model still guesses."),
        ans=0,
        explain=("The drop followed a growth in similar tools described in a few words, so the first move is to give the model "
                 "something to choose by. B assumes a bigger model removes the need for descriptions. C answers a problem of "
                 "hundreds of tools, and twelve is far below that. D pays for a larger model and adds examples before checking "
                 "the cheapest likely cause."),
        scenarios=(1,), points=("2.1:K1",),
        evidence=(Evidence(DEFINE, "Provide extremely detailed descriptions. This is by far the most important factor in tool performance."),),
        qtype="evaluate", level="easy", principle="proportionate",
        situation="tool list grows from 4 to 12 with one-line descriptions and a bigger model is proposed",
        trap="upgrade the model instead of fixing descriptions",
    ),
    MCQ(
        id="Q2.1-03",
        q=("An evaluation of your IDE agent's six tools shows 97% correct selection with one-line descriptions and 97% with "
           "three-sentence ones, so a colleague proposes keeping the short ones across the platform. The six tools do very "
           "different jobs (open a file, run a test, query a ticket, and so on). Next quarter the platform will add "
           "`search_tickets_v2` and `search_wiki`, each close in purpose to an existing search tool. How should you evaluate "
           "the finding?"),
        opts=("Accept it, and re-run the evaluation after the new tools ship to see whether anything changed.",
              "Accept it: an equal score on six tools shows that the model selects well from names and schemas alone.",
              "Reject it, and re-run the evaluation with 600 requests per tool so that the two equal scores can be told apart.",
              "Treat it as true only for unlike tools, and add near-duplicate search tools to the test before cutting detail."),
        ans=3,
        explain=("The six tools are easy to tell apart, so short descriptions had nothing to fail at; the risk sits with tools that "
                 "resemble each other, which the test does not contain. A finds the regression after release. B reads an easy "
                 "test as a general result. C adds more of the same easy requests when the scores are already equal."),
        scenarios=(4,), points=("2.1:K1",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 2.1 Knowledge 1 says minimal descriptions make selection among similar tools unreliable; judging what an evaluation of unlike tools can show is evaluation judgment no official page states.",
        qtype="evaluate", level="hard", principle="explicit",
        situation="equal eval scores for short and long descriptions on six unlike tools",
        trap="generalise from a test that has no similar tools",
    ),
    # ---- K2: formats, examples, edge cases, boundaries ----
    MCQ(
        id="Q2.1-04",
        q=("Your `search_kb` tool runs a keyword search over help articles and returns the top 5 matches. Its description reads "
           "\"Searches the knowledge base.\" Customers write full sentences, and the model passes them through unchanged, for "
           "example \"hi, could you tell me whether I can still send back the kettle I bought last month?\". The right article "
           "is in the top 5 for only 41% of queries, against 90% for hand-written queries of two to four words. The team wants to "
           "keep results at 5 to protect context. What should you configure?"),
        opts=("A separate query-rewriting model call placed in front of `search_kb` and run on every search the agent makes.",
              "A description saying the search matches keywords, with example queries such as \"return window electronics\".",
              "A result limit of 20, so that the right article is more likely to be among the matches returned.",
              "A second tool, `ask_kb`, that accepts full sentences, kept beside the first for natural questions."),
        ans=1,
        explain=("The model builds its queries from what the description tells it, so saying that the search is keyword-based and "
                 "showing example queries changes the input at its source. A adds another model call to correct inputs the first "
                 "model would have written well. C works against the stated limit and returns noise. D adds a tool for a "
                 "problem that the existing one can solve."),
        scenarios=(1,), points=("2.1:K2",),
        evidence=(Evidence(DEFINE, "The more context you can give Claude about your tools, the better it will be at determining when and how to use them."),),
        qtype="configure", level="easy", principle="explicit",
        situation="keyword help-article search is given full sentences by the model",
        trap="add a query-rewriting model call",
    ),
    MCQ(
        id="Q2.1-05",
        q=("Six internal agents, each with its own system prompt, share a `run_tests` tool whose description says \"Runs tests.\" "
           "and which takes a `path`. When `path` is a directory, every suite beneath it runs and takes about 40 minutes; a "
           "single file takes seconds. In one week 31% of calls passed a directory although the agent needed one file's tests, "
           "and builds queued behind them. A directory is sometimes the right input. What is the most effective change?"),
        opts=("Lower the tool's timeout to five minutes, so that slow runs are cut off and the agent retries with a narrower path.",
              "Add a PreToolUse hook that denies every call whose `path` is a directory, for all six agents that share the tool.",
              "Add a paragraph to each of the six system prompts, telling the agent to prefer a file path over a directory.",
              "Extend the description with what `path` accepts, the 40-minute cost of a directory, and when each is appropriate."),
        ans=3,
        explain=("The edge case belongs with the tool, because every agent that uses it needs the same facts. A cuts off the "
                 "runs that were legitimately big and still lets the agent choose the expensive form. B blocks the cases where "
                 "a directory is right. C scatters the same facts across six prompts, where they drift apart."),
        scenarios=(4,), points=("2.1:K2",),
        evidence=(Evidence(DEFINE, "What each parameter means and how it affects the tool"),),
        qtype="fix", level="medium", principle="fit_for_purpose",
        situation="directory path runs a 40-minute suite where a file was wanted",
        trap="deny directories in a hook",
    ),
    MCQ(
        id="Q2.1-06",
        q=("Your `create_ticket` tool takes a nested `fields` object with an optional `components` array. The schema and "
           "description are accurate, and every call validates. Yet in 64% of 250 sampled calls the agent leaves out "
           "`components`, so tickets land in the default queue, and the description already explains what components are for. "
           "Which change is most effective?"),
        opts=("Set `strict: true` on the tool, so that arguments are guaranteed to match the schema.",
              "Set `tool_choice` to `create_ticket`, so that the call is always made with every field filled in.",
              "Add `input_examples` that show calls with `components` filled in for typical tickets.",
              "Expand the `components` description with three paragraphs on how to choose between queues."),
        ans=2,
        explain=("Examples show the model when an optional parameter is worth including and how a nested object looks. A guarantees "
                 "valid arguments, and these already validate. B forces the call, which does not fill an optional field. D adds "
                 "to a description that already explains the field, when concrete patterns are what is missing."),
        scenarios=(4,), points=("2.1:K2",),
        evidence=(Evidence(DEFINE, "These patterns indicate when to include optional parameters, what formats to use, and how to structure complex inputs."),),
        basis="docs",
        qtype="configure", level="medium", principle="fit_for_purpose",
        situation="optional components array omitted in 64% of valid create_ticket calls",
        trap="turn on strict schema mode",
    ),
    # ---- K3: overlap causes misrouting ----
    MCQ(
        id="Q2.1-07",
        q=("After a merger, your support agent has `lookup_shipment` from the retail team and `track_package` from the logistics "
           "team. Both are described as \"Gets the delivery status of a shipment\", call the same backend and return identical "
           "fields. The agent picks `lookup_shipment` 58% of the time and `track_package` 42% for the same kinds of request. Both "
           "tools sit in the lists of five other agents with different prompts. What is the best change?"),
        opts=("Write a longer description for each tool, to bring out how it differs from the other.",
              "Keep one of the two tools and retire the other, since there is no difference to describe.",
              "Add a system prompt line telling the agent to prefer `lookup_shipment` for delivery questions.",
              "Force `track_package` with `tool_choice` whenever a message contains a tracking number."),
        ans=1,
        explain=("The split between the tools follows their identical descriptions, and there is nothing true to say that would "
                 "tell them apart, so one should go. A would have to invent a difference. C patches one agent's prompt while "
                 "five others keep the duplicate. D forces a tool on one kind of message and leaves the overlap in place."),
        scenarios=(1,), points=("2.1:K3",),
        evidence=(Evidence(DEFINE, "Fewer, more capable tools reduce selection ambiguity"),),
        qtype="choose", level="easy", principle="proportionate",
        situation="two merged-company tools with identical description and backend split calls 58/42",
        trap="invent differences or patch one prompt",
    ),
    MCQ(
        id="Q2.1-08",
        q=("Your research agent has `search_internal_wiki`, described in detail as searching Acme's engineering wiki. You add a "
           "third-party MCP server whose only search tool is `search`, described as \"Search for information.\" Afterwards the "
           "share of internal-wiki questions answered with `search_internal_wiki` falls from 82% to 19%, and answers cite public "
           "pages that contradict internal standards. The wiki tool and its description are unchanged, and its remaining calls succeed. What is the "
           "most likely root cause?"),
        opts=("The model favours whichever tool was added most recently, whatever its description says.",
              "The wiki tool's calls now fail validation, so the model gives up on it after the first error.",
              "The new tool's broad description fits nearly any request, so it competes with the wiki tool.",
              "The longer tool list went over a size limit, so the wiki tool is no longer sent to the model."),
        ans=2,
        explain=("A description as broad as \"Search for information\" fits every question the wiki tool should get, and the "
                 "drop followed the addition. A describes a preference for recency that is not how selection works. B is ruled out by the stem, "
                 "which says its remaining calls succeed. D is ruled out because the agent still uses the "
                 "wiki tool in 19% of cases."),
        scenarios=(3,), points=("2.1:K3",),
        evidence=(Evidence(DEFINE, "The good description clearly explains what the tool does, when to use it, what data it returns"),),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="new generic MCP search tool takes questions from a detailed internal wiki tool",
        trap="blame recency or the longer description",
    ),
    MCQ(
        id="Q2.1-09",
        q=("Your coding agent has `run_linter` (\"Checks code for problems and style issues\") and `run_type_check` (\"Checks code "
           "for type problems\"). Of 120 sampled requests that clearly need a type check, 46 went to `run_linter`; of 150 that "
           "clearly need a lint pass, 4 went to `run_type_check`. Linter output never contains type errors. What is the most "
           "likely root cause?"),
        opts=("`run_linter` is described broadly enough to include type problems, so it absorbs the other tool's requests.",
              "The two names are too alike, which would send requests to either tool about equally often, both ways.",
              "`run_type_check` is registered after `run_linter`, and the model leans toward tools that are listed earlier.",
              "`run_type_check` returns too much output, so the model avoids calling it whenever it can find another route."),
        ans=0,
        explain=("The misroutes run almost one way: requests for the narrow tool go to the broad one, which says its job includes "
                 "\"problems\" in general. B would produce errors in both directions. C and D invent behaviours that the numbers "
                 "do not call for; the same agent calls `run_type_check` correctly for 62% of requests that need it."),
        scenarios=(4,), points=("2.1:K3",),
        evidence=(Evidence(DEFINE, "The good description clearly explains what the tool does, when to use it, what data it returns"),),
        qtype="diagnose", level="hard", principle="root_cause",
        situation="46 of 120 type-check requests go to a linter with a broad description, 4 of 150 the other way",
        trap="read one-way misrouting as symmetric name confusion",
    ),
    # ---- K4: prompt wording creates tool associations ----
    MCQ(
        id="Q2.1-10",
        q=("Your support agent's system prompt contains the line \"Customers who mention cancellation want their subscription "
           "cancelled: call `cancel_subscription`.\" The tool descriptions are detailed and correct. Of 120 sampled conversations "
           "that contain the word \"cancellation\", 14 triggered `cancel_subscription` although the customer had only asked what the "
           "cancellation policy was; among 120 conversations without the word, none did. Which explanation fits the evidence best?"),
        opts=("`cancel_subscription` is listed before `get_policy_text`, and the model favours tools listed first.",
              "The prompt line ties a word to a tool, and the model acts on it even for a question about policy.",
              "The conversations were long enough that the model lost track of what each tool does.",
              "Sampling randomness makes tool choice drift whenever a request mentions a change to an account."),
        ans=1,
        explain=("Every wrong call sits in conversations that contain the trigger word, which points at the instruction and not at "
                 "the descriptions. A and D name causes that would not follow the word. C would show up in long conversations "
                 "generally, and the sample is defined by the word."),
        scenarios=(1,), points=("2.1:K4",),
        evidence=(Evidence(OVERVIEW, "This boundary is steerable through your system prompt."),),
        qtype="diagnose", level="easy", principle="root_cause",
        situation="a prompt line pairs the word cancellation with cancel_subscription",
        trap="blame tool order or sampling",
    ),
    MCQ(
        id="Q2.1-11",
        q=("After a move to a newer model, your support agent calls `search_kb` on 93% of turns, including \"thanks\" and \"ok\", "
           "which adds about two seconds of latency each time. The system prompt, unchanged from the older model, includes "
           "\"CRITICAL: You MUST call search_kb before answering ANY message.\" The tool descriptions are fine. What is the most "
           "effective fix?"),
        opts=("Set `tool_choice` to `none` on any turn where the customer message is shorter than 20 characters.",
              "Add a classifier that detects pleasantries and strips the tools from those requests before the call.",
              "Lower the sampling temperature so that the model makes tool calls less often overall.",
              "Replace the line with plain wording: \"Use search_kb when a question needs policy details.\""),
        ans=3,
        explain=("Models that follow the system prompt more closely act on forceful wording, so softening it restores the "
                 "model's own judgment about when a call is useful. A uses message length as a stand-in for intent and will "
                 "cut off short questions that need the knowledge base. B builds a separate component for what a wording "
                 "change fixes. C misreads temperature, which does not decide whether a tool is needed."),
        scenarios=(1,), points=("2.1:K4",),
        evidence=(Evidence("api:build-with-claude/prompt-engineering/claude-prompting-best-practices", "The fix is to soften any aggressive language."),),
        basis="docs",
        qtype="fix", level="medium", principle="proportionate",
        situation="emphatic MUST line makes search_kb run on every pleasantry",
        trap="add a classifier or length rule instead of softening the prompt",
    ),
    MCQ(
        id="Q2.1-12",
        q=("A research agent is given `query_filings_db`, whose description says it holds filings for single companies and no "
           "industry data, plus `web_search`. The system prompt says: \"Anything about market size goes to query_filings_db.\" Of 90 sampled "
           "questions about industry market size, all 90 called the database first, 64 got an empty result, and the agent then "
           "wrote an answer from memory with no search at all. Industry questions that do not use the phrase went to `web_search`. Which explanation best accounts for the database calls?"),
        opts=("The prompt line pairs a phrase with a tool that the description rules out, and the model follows the line.",
              "The questions read like company questions, so the database description looks as if it covers them.",
              "The `web_search` description lacks the words \"market size\", so the model cannot match it to these questions.",
              "The model weighs a tool description and a prompt instruction equally, so it picks between them at random."),
        ans=0,
        explain=("All 90 calls went to one tool, which a random choice would not do, and the only thing tying these questions to "
                 "that tool is the prompt line. B describes how the failure was handled afterwards, and does not explain why the "
                 "database was called. C adds a cause that would send some questions elsewhere, and none went. D is contradicted "
                 "by 90 of 90."),
        scenarios=(3,), points=("2.1:K4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 2.1 Knowledge 4 states that keyword-sensitive prompt wording can create unintended tool associations; no official page speaks to this judgment.",
        qtype="diagnose", level="hard", principle="root_cause",
        situation="market size rule sends 90 of 90 industry questions to a filings database",
        trap="blame the empty-result handling",
    ),
    # ---- S4 (first of three): fix the instruction, not the descriptions ----
    MCQ(
        id="Q2.1-13",
        q=("Your coding agent's prompt says \"For anything about a build, use the `ci_status` tool.\" It was added because, before "
           "it, the agent sometimes skipped CI checks when asked about failing pipelines. Now about 1 in 5 requests like \"build a "
           "pagination helper for the orders list\" make the agent poll `ci_status` for the main branch before writing any code. "
           "The tool descriptions are accurate. What is the best fix?"),
        opts=("Delete the line, since the tool descriptions already say when to check CI.",
              "Repeat the line in capitals, so that the agent sees it as the rule that governs CI questions.",
              "Reword it around the intent: use `ci_status` when asked whether a pipeline run passed or failed.",
              "Add a second line telling the agent to skip `ci_status` for any request that starts with the verb \"build\"."),
        ans=2,
        explain=("The word \"build\" means two things and the instruction keys on the word, so naming the intent keeps the "
                 "behaviour the line was added for. A brings back the skipped checks. B makes the keyword rule stronger. D patches "
                 "one phrasing and leaves \"compile the project\" or \"building a feature\" to find their own way in."),
        scenarios=(4,), points=("2.1:S4",),
        evidence=(Evidence(OVERVIEW, "This boundary is steerable through your system prompt."),),
        qtype="fix", level="medium", principle="explicit",
        situation="the word build in a prompt sends coding requests to the CI status tool",
        trap="emphasise or patch the keyword rule",
    ),
    # ---- S1: write differentiating descriptions ----
    MCQ(
        id="Q2.1-14",
        q=("You are adding `search_invoices` next to the existing `get_invoice`. `get_invoice` takes an invoice ID and returns line "
           "items and a PDF link. `search_invoices` takes a customer ID and an optional date range, and returns up to 20 summaries "
           "(ID, date, total) without line items. Which description for `search_invoices` best prevents mix-ups?"),
        opts=("\"Finds invoices. Useful when customers ask about their invoices, or want to know what they were charged for in a given month.\"",
              "\"Lists up to 20 invoice summaries (ID, date, total) for a customer ID and optional dates. No line items: use get_invoice.\"",
              "\"Returns invoice data from the billing system, including identifiers, dates and totals, as JSON with a stable field order.\"",
              "\"Searches invoices by customer. Prefer get_invoice whenever an invoice ID is known, and call this only as a last resort.\""),
        ans=1,
        explain=("It states the input, the output, the limit, and which tool to use for the missing detail. A says only that it "
                 "finds invoices, which is also what the other tool does. C describes formatting and is silent on when to use "
                 "it. D gives a preference order and leaves the model unsure what the tool returns or accepts."),
        scenarios=(1,), points=("2.1:S1",),
        evidence=(Evidence(DEFINE, "Provide extremely detailed descriptions. This is by far the most important factor in tool performance."),),
        qtype="choose", level="medium", principle="explicit",
        situation="summary-list tool must be told apart from a single-invoice tool",
        trap="describe the purpose or format without the boundary",
    ),
    MCQ(
        id="Q2.1-15",
        q=("Your SRE assistant has `get_metrics` (\"Returns metrics for a service\") and `get_slo_report` (\"Returns SLO data for a "
           "service\"). For questions such as \"is checkout within its latency SLO this week?\" the agent calls `get_metrics`, then "
           "computes the burn rate itself, and is wrong in 30% of 200 sampled answers. `get_slo_report` returns pass or fail per "
           "window with the burn rate already computed. The agent also needs `get_metrics` for graph and trend questions. What "
           "change is most effective?"),
        opts=("Write the burn-rate formula into the system prompt and let the agent work it out from raw metrics.",
              "Remove `get_metrics` from the agent, so that the only route to an SLO answer is the report tool.",
              "Rewrite both: the report tool gives pass or fail and burn rate; the metrics tool gives raw points.",
              "Give the agent a `calculate` tool, so that its arithmetic on the raw data points is exact every time."),
        ans=2,
        explain=("The descriptions say what both tools return in the same loose terms, so the model takes the raw data and does "
                 "its own sums. Stating the output and when to use each sends SLO questions to the tool that already has the "
                 "answer. A keeps the wrong path and tries to make it work. B takes away a tool the agent needs for trends. D "
                 "makes the arithmetic exact but leaves the wrong inputs."),
        scenarios=(4,), points=("2.1:S1",),
        evidence=(Evidence(TROUBLE, "Differentiate tools by WHEN to use them, not only WHAT they do."),),
        qtype="fix", level="medium", principle="explicit",
        situation="raw metrics tool preferred over a ready-made SLO report tool",
        trap="teach the formula in the prompt or add a calculator",
    ),
    MCQ(
        id="Q2.1-16",
        q=("You added `apply_promo_code`, which lowers the total of an open order, next to `issue_credit`, which gives store "
           "credit after payment. Since launch, 21% of promo-code requests from unpaid orders have gone to `issue_credit`, "
           "and some customers received credit they did not ask for. Which description for `apply_promo_code` best fixes "
           "the mix-up?"),
        opts=("\"Applies a promo code to an unpaid order and returns the new total. Takes the code as typed, such as SPRING25. After payment, use issue_credit.\"",
              "\"Applies a promo code to an order. Returns the new total and a list of the discounts applied, each with its code, amount and expiry date, as JSON.\"",
              "\"Reduces what a customer pays. Takes the code the customer typed, exactly as typed, and applies it. Customers often ask about this at checkout.\"",
              "\"Applies a promo code to an order. The code goes in the `code` field; see the schema for details. Do not use it for refunds or returned goods.\""),
        ans=0,
        explain=("It gives the input, the output and the boundary against `issue_credit`, which is the tool that took the "
                 "requests. B says what comes back and nothing about when to use it instead of the credit tool. C describes "
                 "the customer's goal and gives no boundary. D draws its boundary against refunds, which are not the "
                 "confusion in the logs."),
        scenarios=(1,), points=("2.1:S1",),
        evidence=(Evidence(TROUBLE, "Differentiate tools by WHEN to use them, not only WHAT they do."),),
        qtype="choose", level="medium", principle="explicit",
        situation="21% of promo requests on unpaid orders go to a store-credit tool",
        trap="describe the output or goal but not the boundary",
    ),
    # ---- S2: rename and update ----
    MCQ(
        id="Q2.1-17",
        q=("Your research agent has `get_data`, which queries the internal metrics warehouse, and `get_info`, which fetches public "
           "web pages. Each description already says accurately what it returns and what it does not. Even so, the agent picks "
           "the wrong one in 25% of 200 sampled runs, and its stated reasoning shows it choosing from the names (\"get info "
           "about the market\"). What is the best change?"),
        opts=("Add a third tool, `route_query`, that decides which of the two the agent should call each time.",
              "Lengthen both descriptions with five further example questions for each one of the two tools in use.",
              "Force `get_data` with `tool_choice` whenever the question contains a figure or a number.",
              "Rename them `query_internal_metrics` and `fetch_public_web_page`, keeping descriptions in line."),
        ans=3,
        explain=("The agent reads the names, which say almost the same thing, so the names must carry the difference as well as "
                 "the descriptions. A adds a layer to fix what a rename fixes. B adds text to descriptions that are already "
                 "accurate, while the names keep misleading. C forces a tool on a keyword and ignores the questions that "
                 "contain no figure."),
        scenarios=(3,), points=("2.1:S2",),
        evidence=(Evidence(DEFINE, "This makes tool selection unambiguous as your library grows"),),
        qtype="choose", level="medium", principle="proportionate",
        situation="get_data and get_info are chosen from their names alone",
        trap="add a router tool or more examples",
    ),
    MCQ(
        id="Q2.1-18",
        q=("After a merger your agent has `update_address`, which changes the billing address on the account, and "
           "`change_address`, which changes the delivery address on an open order. Both are described as \"Changes the "
           "customer's address\", and 19% of address requests change the wrong one. What should you do?"),
        opts=("Rename them `update_billing_address` and `update_delivery_address`, saying which address each changes.",
              "Merge them into one `manage_address` tool with a `kind` parameter, and keep the shared description as it is.",
              "Add a system prompt table that maps each kind of address request to one of the two tools by name.",
              "Keep the names and add \"Do not use for delivery addresses\" to one of the two descriptions only."),
        ans=0,
        explain=("The two tools do different things but are named and described as if they were the same, so names and "
                 "descriptions both need to say which address changes. B can be fine when actions share a contract, but here it keeps the "
                 "shared description and moves the confusion into a parameter. C relies on a table in the prompt for what the tools should say about themselves. D "
                 "corrects one side and leaves the other still ambiguous."),
        scenarios=(1,), points=("2.1:S2",),
        evidence=(Evidence(DEFINE, "This makes tool selection unambiguous as your library grows"),),
        qtype="fix", level="easy", principle="explicit",
        situation="billing and delivery address tools share one description after a merger",
        trap="merge into a kind parameter or patch one description",
    ),
    MCQ(
        id="Q2.1-19",
        q=("To remove an overlap, your team renamed `run_checks` to `run_unit_tests` and rewrote its description. Right afterwards "
           "22% of sessions log \"unknown tool: run_checks\", and the agent then skips testing and commits. The new description is "
           "accurate and `run_unit_tests` is in the tool list of every affected agent. Where should you look first for the cause?"),
        opts=("At how tool definitions from earlier sessions are stored and served to the model.",
              "At the system prompt and instructions, for text that still names `run_checks`.",
              "At the new name, which may be so specific that the model hesitates to call it.",
              "At the new description, which should mention the old name so that the model can map it."),
        ans=1,
        explain=("The model is asking for a name that the tool list no longer holds, so it is reading it from text written before "
                 "the rename, and instruction text is where such text sits. A has the tool list sent fresh on each request. C would "
                 "not produce calls to a name that is gone. D treats a stale reference as a missing alias and keeps the old name alive."),
        scenarios=(4,), points=("2.1:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 2.1 Skill 2 names renaming a tool and updating its description; finding stale references to the old name in prompts is judgment the official pages do not address.",
        qtype="diagnose", level="hard", principle="root_cause",
        situation="agent calls run_checks after it was renamed because the prompt still names it",
        trap="blame caching or add the old name to the description",
    ),
    # ---- S3: split generic tools ----
    MCQ(
        id="Q2.1-20",
        q=("Your support agent has one `manage_subscription(action, ...)` tool, where `action` is \"pause\", \"cancel\", "
           "\"change_plan\" or \"refund_remaining\". Each action needs different fields and returns a different shape, and in a "
           "sample of 300 conversations 8% of customers who asked to pause were cancelled. What is the most effective redesign?"),
        opts=("Keep one tool and add a `confirmed` boolean that the model must set before it cancels anything at all.",
              "Keep one tool and put a table of each action's fields and results into its description text.",
              "Split it into `pause_subscription`, `cancel_subscription`, `change_plan` and `refund_balance`.",
              "Keep one tool and add a PostToolUse hook that restores any subscription cancelled by mistake."),
        ans=2,
        explain=("Four jobs with different fields and results are hidden behind one entry point, so the model picks the job "
                 "through a string value; one tool with an action parameter is fine when the actions share a contract, and these do not. Separate tools put each job's name, inputs and output in its own definition. A adds a "
                 "flag the model can set wrongly as easily. B documents the differing contracts without removing them. D repairs the "
                 "mistake after the customer has been affected."),
        scenarios=(1,), points=("2.1:S3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 2.1 Skill 3 describes splitting generic tools into purpose-specific ones. The API docs advise grouping closely related actions, so the stem makes the actions differ in fields and results, which is the guide's case.",
        qtype="fix", level="medium", principle="explicit",
        situation="a manage_subscription action string makes pause requests cancel the account",
        trap="add a confirm flag or document the table",
    ),
    MCQ(
        id="Q2.1-21",
        q=("Your database assistant has one tool, `run_sql(statement)`, used for SELECT reports and also for UPDATE and DELETE "
           "maintenance. Security wants every write to need a developer's approval in the IDE, while reads must stay unattended, "
           "and approvals are set per tool. A hook that searches the statement text for UPDATE or DELETE was tried and let "
           "through a `WITH ... DELETE` statement. What should you do?"),
        opts=("Add \"never write without approval\" to the `run_sql` description, and repeat it in the system prompt.",
              "Require approval on every `run_sql` call, so that reads and writes share one safe rule.",
              "Keep one tool and extend the text-matching hook to cover `WITH ... DELETE` and other forms.",
              "Split it into `query_readonly` and `modify_data`, so approval can apply to the write tool alone."),
        ans=3,
        explain=("Two different jobs, with different risk, share one entry point, so no rule on the tool can tell them apart; "
                 "splitting gives each job its own contract and its own approval. A is an instruction, and the requirement is a "
                 "guarantee. B ends the unattended reads. C keeps guessing at intent from text, which the missed statement "
                 "already showed to be fragile."),
        scenarios=(4,), points=("2.1:S3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 2.1 Skill 3 (splitting a generic tool into purpose-specific tools with defined contracts); applying approval to one tool is the reason in this scenario.",
        qtype="choose", level="hard", principle="least_privilege",
        situation="one run_sql tool for reads and writes when only writes need approval",
        trap="parse statement text in a hook",
    ),
    MCQ(
        id="Q2.1-22",
        q=("Your `analyze_document` tool takes a `document_id` and returns the same summary-and-key-figures structure for PDFs, "
           "Word files and web pages. 3% of calls time out on files over 200 pages. An engineer proposes splitting it into "
           "`analyze_pdf`, `analyze_docx` and `analyze_webpage` to fix this. How should you evaluate the proposal?"),
        opts=("Reject it: the split is by file type with one contract, so it adds near-duplicates and leaves timeouts.",
              "Accept it: narrower tools with narrower descriptions are selected more reliably than one general tool is.",
              "Accept it, and keep `analyze_document` as a general fallback for any other file format that comes up.",
              "Reject it, and add a `format` parameter that tells the tool what the file is, so timeouts get set per format."),
        ans=0,
        explain=("A split is for jobs with different purposes and contracts, while one tool is fine when the contract is shared; these three jobs are the same, and the failure is "
                 "about length. B ignores that three near-identical descriptions create the overlap a split is meant to remove. "
                 "C does the same and keeps a fourth tool. D relocates the same distinction into a parameter and does not "
                 "touch the cause of the timeouts."),
        scenarios=(3,), points=("2.1:S3",),
        evidence=(Evidence(DEFINE, "Fewer, more capable tools reduce selection ambiguity and make your tool surface easier for Claude to navigate."),),
        community="Docs support the point that narrower, more numerous tools do not by themselves improve selection (option B); the timeout diagnosis is judgment.",
        qtype="evaluate", level="medium", principle="proportionate",
        situation="split by file type proposed to fix timeouts on long documents",
        trap="split a tool whose contract is the same for every input",
    ),
    # ---- S4: review system prompts ----
    MCQ(
        id="Q2.1-23",
        q=("A support agent's system prompt has 14 rules written by four teams. Six name a tool next to a trigger phrase, for "
           "example \"when the customer mentions a chargeback, use `open_dispute`\", and some of them were added to fix real routing "
           "failures. Overall tool-selection accuracy is 93% on your standard request set. Before launch you want to find "
           "unintended tool associations. Which review is most effective?"),
        opts=("Ask the model to list the prompt rules that might conflict with a tool description, and then fix what it reports.",
              "Write requests with each rule's phrase that need another tool, and compare results with and without the rule.",
              "Raise the launch bar for overall accuracy from 93% to 97% on the standard request set used so far.",
              "Remove every rule that names a tool, and rely on the tool descriptions alone."),
        ans=1,
        explain=("A misrouting caused by a phrase shows up only on requests that contain the phrase and belong elsewhere, and a "
                 "with-and-without comparison shows which rule does it. A relies on the model's own opinion of its prompt. C "
                 "raises a bar on a set that does not contain such requests. D discards rules that fixed real failures."),
        scenarios=(1,), points=("2.1:S4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 2.1 Skill 4 (review system prompts for keyword-sensitive instructions); the probing method is evaluation judgment and not in any official page.",
        qtype="evaluate", level="hard", principle="independent_check",
        situation="six trigger-phrase rules in a 14-rule prompt checked before launch",
        trap="ask the model to audit its own prompt",
    ),
    MCQ(
        id="Q2.1-24",
        q=("A support prompt says \"Answer simple questions directly, without looking anything up.\" The agent now answers \"how "
           "long do I have to return an electronics item?\" from its own wording of the policy and is wrong in 17% of 300 such "
           "questions. The `search_kb` description already says it holds the current return and warranty policy. What is the "
           "best fix?"),
        opts=("Add \"ALWAYS call a tool first\" to the prompt, so that nothing at all is answered from memory.",
              "Set `tool_choice` to `any`, so that every single turn of the conversation must call a tool.",
              "Add three more sentences to the `search_kb` description saying that it holds the return policy text.",
              "Name what may be answered directly, such as greetings, and send policy questions to the tool."),
        ans=3,
        explain=("The word \"simple\" lets the model decide that a short policy question is simple, and the instruction is the thing "
                 "overriding a good description. Stating what counts as answerable without tools removes that reading. A swings to "
                 "the opposite extreme. B also forces calls on greetings. C repeats what the description already says."),
        scenarios=(1,), points=("2.1:S4",),
        evidence=(Evidence(OVERVIEW, "This boundary is steerable through your system prompt."),),
        qtype="fix", level="medium", principle="explicit",
        situation="a prompt about simple questions makes the agent skip search_kb for a policy question",
        trap="swing to always call a tool",
    ),
)
