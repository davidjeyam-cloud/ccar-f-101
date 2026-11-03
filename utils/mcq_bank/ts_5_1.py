"""Exam bank · TS 5.1. Original questions; see docs/MCQ_BANK_PLAN.md."""
from utils.mcq_sets import MCQ, Evidence

TS = "5.1"
BULLETS = {
    "K1": "Progressive summarization turns numbers, percentages, dates and customer-stated expectations into vague summaries",
    "K2": "Models handle the start and end of long inputs reliably but may omit findings from the middle",
    "K3": "Tool results pile up in context and use tokens out of proportion to their relevance",
    "K4": "Each API request must carry the complete conversation history for the exchange to stay coherent",
    "S1": "Keeping transactional facts in a persistent case-facts block in each prompt, outside the summarized history",
    "S2": "Keeping structured issue data in a separate context layer for sessions that raise several issues",
    "S3": "Trimming verbose tool outputs to the relevant fields before they accumulate in context",
    "S4": "Putting a key-findings summary first and organizing detail under explicit section headers to offset position effects",
    "S5": "Requiring subagents to return metadata (dates, source locations, method) in structured outputs for accurate synthesis",
    "S6": "Having upstream agents return structured data instead of verbose content when downstream agents have small budgets",
}

_CTX_ROT = Evidence("api:build-with-claude/context-windows", "As token count grows, accuracy and recall degrade, a phenomenon known as context rot.")
_ACCUM = Evidence("api:build-with-claude/context-windows", "each user message and assistant response accumulates within the context window, and previous turns are preserved completely.")
_INPUT = Evidence("api:build-with-claude/context-windows", "Contains all previous conversation history plus the current user message")
_TOOLCTX = Evidence("api:agents-and-tools/tool-use/manage-tool-context", "Tool definitions and accumulated `tool_result` blocks consume your context window.")
_DROPS = Evidence("api:build-with-claude/compaction", "when the default summary drops something a later turn needs")
_REPLACES = Evidence("api:build-with-claude/compaction", "Compaction replaces the older turns of a conversation with a summary that Claude writes on the server")
_TOP = Evidence("api:build-with-claude/prompt-engineering/claude-prompting-best-practices", "Place your long documents and inputs near the top of your prompt, above your query, instructions, and examples.")
_QEND = Evidence("api:build-with-claude/prompt-engineering/claude-prompting-best-practices", "Queries at the end can improve response quality by up to 30 percent in tests, especially with complex, multidocument inputs.")
_SOURCE = Evidence("api:build-with-claude/prompt-engineering/claude-prompting-best-practices", "wrap each document in `<document>` tags with `<document_content>` and `<source>` (and other metadata) subtags for clarity.")
_FINAL = Evidence("code:agent-sdk/subagents", "intermediate tool calls and results stay inside the subagent; only its final message returns to the parent.")

QUESTIONS = (
    # ---- K1: progressive summarization ----
    MCQ(
        id="Q5.1-01",
        q=("A market research agent condenses each round's findings into a short summary before starting the next round. The raw "
           "round 1 tool results contain \"operating margin 14.2% in fiscal 2025\" and \"warranty reserves up 31% year on year\". "
           "After four rounds the report says margins are healthy and warranty costs are rising, although its prompt asks for a "
           "figure with every claim. Neither number appears in the agent's notes, and token usage never passed 40% of the window. "
           "What is the most likely root cause?"),
        opts=("The oldest tool results were cut off by the context limit before the report was written up.",
              "The report prompt's concise style led the model to swap numbers for more general wording.",
              "Summaries turned the exact figures into vague wording, which later rounds inherited.",
              "The search tool returned snippets in round 1 that left out the figures from its pages."),
        ans=2,
        explain=("Condensing round after round keeps the gist and drops the exact values, so nothing later could quote them. "
                 "A is ruled out by the usage figure. B fails because the prompt asks for figures, and a model cannot quote what "
                 "it was not given. D contradicts the raw results, which hold both numbers."),
        scenarios=(3,), points=("5.1:K1",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: progressive summarization risk is a guide item; the docs only say that a default summary can drop what a later turn needs.",
        qtype="diagnose", level="medium", principle="preserve_information",
        situation="margin and warranty figures become vague wording after round-by-round summaries",
        trap="blame the context limit or the report's style",
    ),
    MCQ(
        id="Q5.1-02",
        q=("A support team compresses long chats into a running summary and must decide whether it is safe to ship. Chats average "
           "45 turns, and the amounts, dates and deadlines customers state come back in the agent's later replies. Which "
           "evaluation is most informative?"),
        opts=("Take the amounts, dates and deadlines from sampled transcripts and check each survives in the summary.",
              "Have a reviewer model rate each summary for readability and tone, and ship when the average is high enough.",
              "Measure how much shorter each summary is than its chat, and ship once summaries are small enough.",
              "Ask the agent at the end of each chat whether it remembers the key details, and count the confident answers."),
        ans=0,
        explain=("The risk is lost specifics, so the check has to compare those specifics before and after. B grades style, which "
                 "a summary can have while losing every figure. C measures size, not content. D relies on the agent's own "
                 "sense of what it remembers."),
        scenarios=(1,), points=("5.1:K1",),
        evidence=(_DROPS,),
        community="",
        qtype="evaluate", level="medium", principle="independent_check",
        situation="deciding if a 45-turn chat summary is safe to ship",
        trap="score fluency, length or self-reported memory",
    ),
    MCQ(
        id="Q5.1-03",
        q=("A contract extraction job handles 120-page agreements by summarising each 20-page chunk and then extracting payment "
           "terms from the six summaries. The summary prompt already tells the model to keep every amount and notice period "
           "exactly. On 20% of contracts, amounts and notice periods still come back as \"standard\" or \"several weeks\". Which "
           "change to the pipeline fixes this?"),
        opts=("Make each chunk summary twice as long, and extract from the longer summaries as before.",
              "Add a check that rejects any extraction containing words such as standard or several.",
              "Summarise the six summaries into one, so all payment terms sit together in a single text.",
              "Extract the payment fields from each chunk directly, and merge the records afterwards."),
        ans=3,
        explain=("Values must be read from the source text, not from a condensed version of it. A still extracts from summaries, "
                 "which keep the gist and lose exact values. B only catches the symptom and has no source to retry from. C "
                 "summarises a second time and loses more."),
        scenarios=(6,), points=("5.1:K1",),
        evidence=(_DROPS,),
        community="",
        qtype="choose", level="easy", principle="preserve_information",
        situation="payment terms become standard or several weeks after chunk summaries",
        trap="lengthen or reject at the summary stage",
    ),
    # ---- K2: lost in the middle ----
    MCQ(
        id="Q5.1-04",
        q=("A synthesis step receives 10 subagent reports of about 6,000 tokens each (60,000 in total) in a fixed order and leaves "
           "out findings from reports 4 to 7 in about 60% of runs. Engineers disagree on whether the cause is where the reports "
           "sit or something about those subagents' content. Which test separates the two explanations?"),
        opts=("Compare the length of reports 4 to 7 with the others, since short reports are the easiest to overlook.",
              "Shuffle the report order across runs and see if omissions follow the position or the reports.",
              "Add a sentence telling the model to cover every report, and see whether the omission rate falls.",
              "Ask the model why it left out each finding, and read its explanations for a common cause."),
        ans=1,
        explain=("Changing only the order, with the content fixed, shows whether omissions track position. A is a correlation "
                 "with a possible third cause. C tests a remedy, and a drop would not say why the findings were missed. D "
                 "relies on explanations the model builds after the fact."),
        scenarios=(3,), points=("5.1:K2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the lost-in-the-middle effect is a guide item and is not stated on the official pages in the corpus.",
        qtype="evaluate", level="hard", principle="root_cause",
        situation="findings from reports 4 to 7 of 10 vanish in 60% of syntheses",
        trap="correlate with length or ask the model to explain itself",
    ),
    MCQ(
        id="Q5.1-05",
        q=("A support agent's prompt holds 45 policy articles (about 90,000 tokens) in arbitrary order. Rules from the first and "
           "last few articles are applied reliably, but rules from the middle of the set are missed in about 40% of the tickets "
           "that need them. For each ticket type, the 8 highest-priority articles are known. What is the most effective fix?"),
        opts=("Switch to a bigger-window model, so the set fits with plenty of room to spare.",
              "Add an instruction at the start of the prompt saying that every article deserves the same careful reading.",
              "Include the full set twice, so that most rules also appear in a stronger position once.",
              "Open with a short summary of the key rules, and put the highest-priority articles at the start and end."),
        ans=3,
        explain=("Content at the edges of a long input is used more reliably, so the rules that matter most should sit there, "
                 "with a short summary first. A adds room but not attention. B asks for evenness the model does not deliver. C "
                 "doubles the length, which makes the problem worse."),
        scenarios=(1,), points=("5.1:K2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the position effect is a guide item and is not stated on the official pages in the corpus.",
        qtype="fix", level="easy", principle="fit_for_purpose",
        situation="middle policy articles missed in 40% of tickets",
        trap="larger window or an instruction to read evenly",
    ),
    MCQ(
        id="Q5.1-06",
        q=("A clause-review agent is given 14 contracts (about 70,000 tokens) in one prompt, built fresh from the files, and asked "
           "to list every termination clause. It lists most clauses from the first three and last three contracts but only 2 of "
           "the 9 clauses in contracts 6 to 9. The response ended with `stop_reason` \"end_turn\" after 700 of the 4,096 output "
           "tokens allowed, and all contracts use the same file format. What is the most likely root cause?"),
        opts=("Material in the middle of a long input gets less reliable attention than the start and end.",
              "The report reached its output limit, which cut it off before the later clauses could be written.",
              "The model cannot parse the middle contracts, so it reads them as blank pages.",
              "An earlier summarising step removed those clauses, so they never reached the review prompt."),
        ans=0,
        explain=("The input held every contract and the response finished normally with room to spare, which points to "
                 "position. B contradicts the end_turn stop and the unused output budget. C is unlikely when the format matches "
                 "the contracts that were read well. D fails because the prompt is built fresh from the files."),
        scenarios=(6,), points=("5.1:K2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the lost-in-the-middle effect is a guide item and is not stated on the official pages in the corpus.",
        qtype="diagnose", level="hard", principle="root_cause",
        situation="termination clauses in contracts 6 to 9 of 14 are missed with output room left",
        trap="raise the output limit",
    ),
    # ---- K3: tool results accumulate ----
    MCQ(
        id="Q5.1-07",
        q=("A billing agent calls `get_account_history` for each customer question. Each call returns 24 months of transactions, "
           "about 7,000 tokens, while most questions concern the latest invoice. The system prompt is 600 tokens and replies "
           "average 150. After five lookups, replies start missing details from the customer's first message, and each request "
           "is about 35,000 tokens larger than at the start. What is the most likely cause?"),
        opts=("The system prompt has grown too long for the model to keep the first message in clear view.",
              "Tool results pile up in the history, and most of their tokens bear little on the question.",
              "The model's own replies are long enough to push the customer's first message out of its view.",
              "The API keeps no record of earlier messages, so the first message was never seen again."),
        ans=1,
        explain=("Five lookups add about 35,000 tokens, most of it history the question does not need, and the model attends "
                 "less well as the input grows. A and C are ruled out by the 600 and 150 token figures. D contradicts the "
                 "growing request size, which shows earlier content is being sent."),
        scenarios=(1,), points=("5.1:K3",),
        evidence=(_TOOLCTX,),
        community="",
        qtype="diagnose", level="easy", principle="proportionate",
        situation="24-month account history lookups crowd out the first message",
        trap="blame the system prompt or the replies",
    ),
    MCQ(
        id="Q5.1-08",
        q=("A support agent's tool results fill most of its context in long chats, and it uses six tools. The team wants to "
           "know which tool to trim first. Which measurement best answers that?"),
        opts=("The average latency of each tool call, since slow tools tend to return the largest results.",
              "The number of calls to each tool per chat, since the most called tool adds the most tokens.",
              "Each tool's share of context tokens, set against how many of its fields the replies used.",
              "The agent's own estimate of which tool results it found least useful, collected after each chat."),
        ans=2,
        explain=("Trimming pays where many tokens are carried for few used fields, so both numbers are needed. A guesses size "
                 "from speed. B ignores how large each result is, so a cheap tool called often can outrank a costly one. D "
                 "depends on the agent's self-report."),
        scenarios=(1,), points=("5.1:K3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: no official page covers how to measure tool-result waste.",
        qtype="evaluate", level="medium", principle="proportionate",
        situation="choosing which of six tools to trim first",
        trap="rank by latency, call count or self-report",
    ),
    MCQ(
        id="Q5.1-09",
        q=("A research agent runs for hundreds of turns with six tools. The tool definitions total 2,000 tokens, but early "
           "search results that are no longer needed now take over 150,000 tokens of the history. Which approach targets this "
           "source of context pressure?"),
        opts=("Context editing, which removes old `tool_result` blocks from the conversation history.",
              "Reduce the number of tools from six to three, so the definitions take less of the window.",
              "Summarise the tool definitions into shorter text, so they take less space in each request.",
              "A higher `max_tokens` value, so the model has more room to write after the history has grown."),
        ans=0,
        explain=("The weight is in old results, and context editing removes exactly those; it is a beta feature, so check its "
                 "availability for your platform. B and C shrink tool definitions, which here are only 2,000 tokens. D changes "
                 "the output limit and leaves the history as large as it was."),
        scenarios=(3,), points=("5.1:K3",),
        evidence=(Evidence("api:agents-and-tools/tool-use/manage-tool-context", "Context editing removes old `tool_result` blocks from the conversation history once they\u2019ve served their purpose."),
                  _TOOLCTX),
        basis="docs",
        community="",
        qtype="choose", level="medium", principle="fit_for_purpose",
        situation="150,000 tokens of stale search results in a long research loop",
        trap="shrink the tool definitions",
    ),
    # ---- K4: complete conversation history ----
    MCQ(
        id="Q5.1-10",
        q=("A chat service sends only the last six messages with each request. In chats longer than 25 turns, 30% of replies "
           "ask for an order number the customer gave in turn 2 or contradict a refund promise the agent made in turn 5. What "
           "is the most effective fix?"),
        opts=("Raise the window to the last twelve messages, so that most of the early details stay in view.",
              "Instruct the model in its system prompt to keep hold of every number and promise given in the chat.",
              "Ask customers to restate their order number whenever the agent needs to look something up again.",
              "Send the complete conversation history with every request, as the model sees only what it holds."),
        ans=3,
        explain=("The model has no memory outside the request, so coherence over 25 turns needs the whole exchange sent. A "
                 "still drops everything older than twelve messages. B asks the model to remember what it is never shown. C "
                 "pushes the repair onto the customer."),
        scenarios=(1,), points=("5.1:K4",),
        evidence=(_INPUT,),
        community="",
        qtype="fix", level="easy", principle="explicit",
        situation="six-message window loses the turn 2 order number in 25-turn chats",
        trap="widen the window or ask the model to remember",
    ),
    MCQ(
        id="Q5.1-11",
        q=("A script wraps the Messages API for a coding assistant. For each follow-up it sends the new instruction plus the "
           "assistant's latest code block, about 3,000 tokens in all. During a long review the assistant keeps reverting "
           "decisions made earlier in the chat, such as agreed `snake_case` naming and a banned library. What is the most "
           "likely cause?"),
        opts=("The decisions belong in a rules file such as CLAUDE.md, which the script never loads.",
              "Earlier exchanges are absent from each request, so the model cannot see those decisions.",
              "The latest code block is long enough that the model skips the instruction in the new message.",
              "The context window was exceeded, so the model dropped the oldest part of each request."),
        ans=1,
        explain=("Each request is all the model has, and the script leaves the earlier turns out. A would help for lasting "
                 "conventions, but these were agreed in this chat and the model never sees that chat. C is unlikely when the "
                 "instruction is present in a short request. D cannot apply to requests of about 3,000 tokens."),
        scenarios=(2,), points=("5.1:K4",),
        evidence=(_ACCUM,),
        community="",
        qtype="diagnose", level="easy", principle="explicit",
        situation="follow-up requests carry only the latest code block and revert snake_case decisions",
        trap="move the decisions to a rules file or blame length",
    ),
    MCQ(
        id="Q5.1-12",
        q=("To save tokens, a support harness sends each request with only the customer's messages and the current tool results, "
           "leaving out the agent's own earlier replies. Customers report that the agent offers the same goodwill voucher twice "
           "and contradicts a deadline it gave earlier. Each request carries the right customer's messages, and tool results "
           "are short and correct. What is the most likely cause?"),
        opts=("The voucher tool treats a repeated call as a new request, so a second voucher is issued.",
              "A longer system prompt is needed, listing in advance which offers the agent is allowed to make.",
              "The agent cannot see its own earlier commitments, as they are left out of each request.",
              "The tool results are long enough that the model overlooks the earlier voucher record inside them."),
        ans=2,
        explain=("The conversation is only as complete as what is sent, and the agent's own turns hold its promises. A blames a "
                 "tool the evidence does not implicate. B treats the symptom with static text that cannot know what was offered. "
                 "D contradicts the statement that the results are short."),
        scenarios=(1,), points=("5.1:K4",),
        evidence=(_INPUT,),
        community="",
        qtype="diagnose", level="medium", principle="preserve_information",
        situation="agent repeats a voucher after its own replies were dropped from requests",
        trap="blame the voucher tool or add static prompt text",
    ),
    # ---- S1: persistent case-facts block ----
    MCQ(
        id="Q5.1-13",
        q=("A support harness writes a case-facts block (order number, refund 86.40, ticket status) as the first message of the "
           "conversation. At turn 30 the conversation is compacted into a summary using a prompt that asks for exact figures. "
           "Afterwards the agent asks for the order number again and quotes a refund of \"about 90\". The block was correct "
           "before compaction. What is the most likely cause?"),
        opts=("The block sat inside the summarised history, so it was condensed along with everything else.",
              "The summary was too short, and a longer summary would have kept the exact refund amount intact.",
              "The block should have been stored in the tool results, which compaction leaves untouched.",
              "The model stops reading the first message of a conversation once a summary has been created."),
        ans=0,
        explain=("A block that lives inside the summarised history is summarised with it, so it belongs in every prompt outside "
                 "that history. B fails because summaries of any length are lossy, and the prompt already asked for exact "
                 "figures. C assumes tool results are exempt from summarising, which nothing in the stem supports, and facts "
                 "kept in the history stay exposed. D has no support either."),
        scenarios=(1,), points=("5.1:S1",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: keeping the block outside the summarized history is the guide's skill; no official page speaks to this exact setup.",
        qtype="diagnose", level="medium", principle="preserve_information",
        situation="case-facts block stored as message one is summarised away at turn 30",
        trap="lengthen the summary",
    ),
    MCQ(
        id="Q5.1-14",
        q=("In a returns agent, the model rewrites the case-facts block after each turn from its memory of the chat. Amounts "
           "must match the order system exactly, yet 4% of recorded refund amounts are transposed or rounded (148.20 stored "
           "as 184.20), although each amount appears exactly in a structured `get_order` result. Which fix best removes the "
           "errors?"),
        opts=("Add a second model call that proofreads the block against the conversation after each update.",
              "Move the block-writing step to a larger model, which copies figures from earlier turns more accurately.",
              "Have the harness copy the amount, date and status fields from each tool result into the block in code.",
              "Tell the model to copy figures exactly and to check each digit twice before it writes the block."),
        ans=2,
        explain=("The values already exist as structured fields, so code can carry them across without any chance of a "
                 "transposition. A and B still depend on a model reproducing digits, which may be right most of the time. D is "
                 "an instruction, and instructions give only probable compliance."),
        scenarios=(1,), points=("5.1:S1",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the guide names extraction into a block but no official page says how the values should be copied.",
        qtype="fix", level="medium", principle="deterministic",
        situation="model-written block turns 148.20 into 184.20 in 4% of cases",
        trap="proofread with a model or a bigger model",
    ),
    MCQ(
        id="Q5.1-15",
        q=("You are designing the persistent block that a returns agent receives in every prompt, outside the summarised "
           "history. Which content belongs in it?"),
        opts=("The agent's reasoning for each decision, so later turns can follow why it acted as it did.",
              "Order numbers, amounts, dates and statuses confirmed by tools, kept as short labelled fields.",
              "The full lookup result for each order, so the agent need not fetch the record again.",
              "A paragraph on the customer's mood and the tone of earlier replies, so the agent stays consistent."),
        ans=1,
        explain=("The block is for exact transactional facts, which are the first thing a summary blurs. A is reasoning, which "
                 "grows quickly and is not a fact to preserve. C copies the verbose record, which defeats the purpose of a "
                 "compact block. D holds soft content that a summary can carry."),
        scenarios=(1,), points=("5.1:S1",),
        evidence=(_DROPS,),
        community="",
        qtype="choose", level="easy", principle="preserve_information",
        situation="deciding what a persistent block holds for a returns agent",
        trap="fill it with reasoning, full records or tone",
    ),
    # ---- S2: structured issue data in a separate layer ----
    MCQ(
        id="Q5.1-16",
        q=("A team stores structured issue records (order ID, amount, status) in a separate layer for chats in which customers "
           "raise three or more problems. They must decide whether it fixes cross-issue mix-ups before rollout. Which "
           "evaluation is most convincing?"),
        opts=("Check that every stored record validates against its JSON schema in a sample of multi-issue chats.",
              "Replay only single-issue chats with the layer on, because they are the cleanest to score.",
              "Compare the final conversation summary with the stored records and confirm both mention each issue.",
              "Replay multi-issue chats and check each reply's figures against the matching issue's record."),
        ans=3,
        explain=("Mix-ups show when a figure from one issue is used for another, so replies must be checked against the matching "
                 "record. A shows that records are well formed, not that they are correct or used correctly. B leaves out the "
                 "chats where the failure occurs. C compares two artefacts and never checks a reply."),
        scenarios=(1,), points=("5.1:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the evaluation design for the issue layer is not covered by an official page.",
        qtype="evaluate", level="hard", principle="independent_check",
        situation="proving an issue layer fixes cross-issue mix-ups before rollout",
        trap="check schema validity or only single-issue chats",
    ),
    MCQ(
        id="Q5.1-17",
        q=("A market-brief agent researches three competitors in one session, alternating between them, and keeps its notes as "
           "one running log. Figures sit in tables that are copied forward from turn to turn, and the brief compares the three "
           "side by side. In 9% of briefs a figure such as a headcount or contract value is credited to the wrong competitor, "
           "although the citations are intact. What is the most effective fix?"),
        opts=("Keep a structured record per competitor (metric, value, date) in a layer outside the log.",
              "Ask the agent to name the competitor in every sentence of the log, so that each figure carries its owner.",
              "Research each competitor in its own session, and merge the three finished briefs by hand afterwards.",
              "Reorder the log so each competitor's notes form one block, and tell the model to read block by block."),
        ans=0,
        explain=("Separate structured records stop figures from different entities blending. B does not reach the figures, "
                 "which live in tables rather than sentences. D relies on the model keeping a long log straight, which is the "
                 "thing that is failing. C gives up the side-by-side comparison the brief needs and adds manual work."),
        scenarios=(3,), points=("5.1:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the guide's example is order issues; applying the layer to research entities is an extension.",
        qtype="fix", level="medium", principle="preserve_information",
        situation="headcount credited to the wrong one of three competitors",
        trap="rely on naming the owner in prose or split the sessions",
    ),
    MCQ(
        id="Q5.1-18",
        q=("An extraction agent processes 12 supplier invoices of about 8 pages each, one at a time, in one session that must stay "
           "under 60,000 tokens while the 12 invoices take about 110,000. By invoice 10 it sometimes attaches line items from "
           "invoice 3 to the wrong invoice number. Which design keeps the figures straight?"),
        opts=("Keep prose notes on each invoice in the running chat, and summarise them every few invoices.",
              "Track only a running total across the invoices, which is the figure the final report needs.",
              "Keep a record per invoice (number, total, status, items) outside the chat, sent each time.",
              "Send all 12 invoices in full with each request, so every line item is in view at once."),
        ans=2,
        explain=("A compact record per invoice carries what later steps need without the pages. A keeps the same prose and "
                 "loses precision when it is summarised. B drops the per-invoice detail the mix-up is about. D exceeds the "
                 "stated budget."),
        scenarios=(6,), points=("5.1:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: record-per-document layers are the guide's pattern, not an official docs page.",
        qtype="configure", level="medium", principle="fit_for_purpose",
        situation="line items from invoice 3 land on invoice 10 in a 12-invoice session",
        trap="prose notes, a running total or resending everything",
    ),
    # ---- S3: trim verbose tool output ----
    MCQ(
        id="Q5.1-19",
        q=("A lookup tool returns a 6,000-character JSON record per order. An engineer proposes cutting each result to its first "
           "2,000 characters before it enters the context. Tests show that `refund_eligible` and `delivered_on`, which the "
           "agent needs, appear after character 3,500 in about a third of records. What is the best approach?"),
        opts=("Cut to the first 3,500 characters instead, because that covers the two fields in most of the records.",
              "Keep the proposed cut, and tell the agent to ask for the rest when a field seems to be missing.",
              "Summarise each record with a model call before it enters the context, and keep only that summary text.",
              "Keep named fields only (`refund_eligible`, `delivered_on`, status, total) and drop the rest."),
        ans=3,
        explain=("Trimming should keep what the decision needs by field, whatever its position. A still loses the fields in "
                 "records where they come later and keeps unneeded text. B leaves the agent to notice a gap it cannot see. C "
                 "adds a lossy model step where a fixed selection would do."),
        scenarios=(1,), points=("5.1:S3",),
        evidence=(_TOOLCTX,),
        community="",
        qtype="fix", level="medium", principle="fit_for_purpose",
        situation="first 2,000 characters of an order record miss refund_eligible",
        trap="trim by length instead of by field",
    ),
    MCQ(
        id="Q5.1-20",
        q=("A coding agent runs its test suite through a wrapper that returns all output: 4,000 lines, about 40 of which describe "
           "failing tests, interleaved with passing lines in run order. Four such runs fill much of the context. How should "
           "the wrapper change what it returns?"),
        opts=("Return the last 200 lines, since failures and the summary line are usually printed near the end.",
              "Return the failing test names with their error lines, plus the pass and fail counts.",
              "Return the first 200 lines, and let the agent re-run the suite with a filter if it needs more.",
              "Have the agent summarise the output in its next message, and then ignore the original lines."),
        ans=1,
        explain=("The agent acts on failures, so those and the counts are what to keep. A and C keep a slice by position, and "
                 "with interleaved output most failures fall outside it. D leaves the full output in context, where it still "
                 "uses the tokens."),
        scenarios=(2,), points=("5.1:S3",),
        evidence=(_TOOLCTX,),
        community="",
        qtype="configure", level="medium", principle="fit_for_purpose",
        situation="4,000-line test output holds 40 failing lines",
        trap="keep the head or tail of the output",
    ),
    MCQ(
        id="Q5.1-21",
        q=("After trimming `get_order` results to five fields, context use dropped by about 85%. Fifteen different other fields have "
           "each turned out to matter in 0.1% to 1% of cases, and the agent cannot see them. Which design keeps the saving and "
           "handles those cases?"),
        opts=("Keep the five-field default, and add an optional parameter for requesting named extra fields.",
              "Restore all 40 fields on every lookup, since a missing field is worse than extra tokens.",
              "Add the fifteen occasionally needed fields to the default set returned by every lookup.",
              "Add a second tool returning the full record, and tell the agent to call it after every lookup."),
        ans=0,
        explain=("The default stays small and the agent can ask for the rarely needed field when a case calls for it. B gives "
                 "back the whole cost. C does the same, to a smaller degree, for fields most cases do not use. D reloads the "
                 "full record on every lookup, which cancels the trimming."),
        scenarios=(1,), points=("5.1:S3",),
        evidence=(_TOOLCTX,),
        community="",
        qtype="choose", level="hard", principle="proportionate",
        situation="fifteen rarely needed fields after trimming to five",
        trap="restore the full record or widen the default",
    ),
    # ---- S4: key findings first, explicit headers ----
    MCQ(
        id="Q5.1-22",
        q=("A reconciliation step receives 40 extracted invoice records (about 30,000 tokens) and must flag mismatches against "
           "purchase orders, including payments split across two invoices. An earlier step has already listed the 8 records "
           "with a suspected mismatch. The step flags the first and last records reliably but misses about half the mismatches "
           "in records 15 to 25. How should you arrange the input?"),
        opts=("Shorten the field names in the records, so each record takes fewer tokens.",
              "Send the records in four batches of ten, and merge the flagged results afterwards.",
              "Open with the 8 suspected mismatches, then the records under a header per invoice.",
              "Add a line before the records saying that records in the middle deserve some extra attention."),
        ans=2,
        explain=("A summary of key findings up front, with the detail under clear headers, offsets the weak middle of a long "
                 "input. A trims tokens but leaves the same positions. B cannot catch payments split across invoices that land "
                 "in different batches. D asks for an attention the model does not reliably give."),
        scenarios=(6,), points=("5.1:S4",),
        evidence=(_TOP,),
        community="Mixes the guide's summary-first skill with the docs advice to put long material near the top.",
        qtype="configure", level="medium", principle="fit_for_purpose",
        situation="mismatches in records 15 to 25 of 40 are missed",
        trap="shorten fields, batch the records or ask for extra attention",
    ),
    MCQ(
        id="Q5.1-23",
        q=("An assistant for human agents receives a customer's case file (about 45,000 tokens of tickets, order notes and chat "
           "logs) plus the agent's question: was the customer promised a refund? Which prompt layout works best?"),
        opts=("The question first, then the instructions, then the file in creation order with no headers.",
              "The instructions and question first, then the file under headers, and a key-findings summary at the end.",
              "The first half of the file, then the question, then the second half, so the question is not buried.",
              "A key-findings summary first, then the file under headers by record type, then the question last."),
        ans=3,
        explain=("Long material goes near the top with its key findings first and organised under headers, and the question "
                 "closes the prompt. A and B put the question ahead of the data, and A has no structure. B also puts the "
                 "summary after 45,000 tokens of detail. C splits the file around the question."),
        scenarios=(1,), points=("5.1:S4",),
        evidence=(_TOP, _QEND),
        basis="docs",
        community="Mixes the guide's summary-first skill with the docs advice to put long material first and the query last.",
        qtype="configure", level="easy", principle="explicit",
        situation="laying out a 45,000-token case file with a refund question",
        trap="question first, summary last or question in the middle",
    ),
    MCQ(
        id="Q5.1-24",
        q=("A coordinator joins five subagent outputs into one block, each starting with only the word \"Findings\" and giving no "
           "record of its subagent or source locations. In 12% of reports a claim is credited to the wrong source, although "
           "every cited source is real. What is the most effective change?"),
        opts=("Ask the synthesis agent to double-check each attribution once it has written the report.",
              "Require each output to carry its subagent, topic and sources as labelled sections.",
              "Reduce the number of subagents to three, so that there are fewer outputs to keep apart.",
              "Order the five outputs alphabetically by topic, so that related claims are kept together."),
        ans=1,
        explain=("Source locations carried in each output, and labelled sections, let the synthesis tie each claim to its "
                 "origin. A asks the model to check a distinction it could not see in the first place. C reduces volume and "
                 "keeps outputs unlabelled. D changes the order and leaves the outputs indistinguishable."),
        scenarios=(3,), points=("5.1:S5",),
        evidence=(_SOURCE,),
        community="",
        qtype="fix", level="medium", principle="explicit",
        situation="five unlabelled outputs begin with the same word and claims cross sources",
        trap="verify afterwards or cut the number of subagents",
    ),
    # ---- S5: metadata in subagent outputs ----
    MCQ(
        id="Q5.1-25",
        q=("A coordinator combines a billing subagent's \"refund: pending\" with a shipping subagent's \"return: received\" and "
           "tells a customer that the refund is still pending. It had been paid three days earlier. The billing subagent had "
           "read a ledger snapshot that refreshes weekly. What should change?"),
        opts=("Require every status in a subagent's output to carry its as-of time and its source system.",
              "Have the coordinator prefer the shipping subagent's status whenever the two statuses seem to disagree.",
              "Add a line to the coordinator's prompt telling it to treat any pending status with caution.",
              "Have the billing subagent repeat its lookup once whenever the result is a pending status."),
        ans=0,
        explain=("With as-of time and source attached, the coordinator can see that the status is old and weigh it. B picks a "
                 "winner by rule and is wrong when billing is right. C is vague advice with nothing to act on. D rereads the "
                 "same weekly snapshot and returns the same answer."),
        scenarios=(1,), points=("5.1:S5",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: dates and source context in subagent outputs are a guide skill; the docs page quoted elsewhere covers document tags, not status timestamps.",
        qtype="fix", level="medium", principle="preserve_information",
        situation="refund shown as pending from a weekly ledger snapshot",
        trap="pick a favoured subagent or retry the same lookup",
    ),
    MCQ(
        id="Q5.1-26",
        q=("You are specifying the structured output of a web research subagent whose findings feed a synthesis agent that must "
           "reconcile claims from different sources. Which set of fields supports accurate synthesis?"),
        opts=("The claim, a confidence score the subagent gives itself, and a line describing its search strategy.",
              "The claim, the full text of the page it came from, and the subagent's reasoning for choosing it.",
              "The claim, the source URL and a relevance score, leaving dates and method for synthesis to find later.",
              "The claim, its value, the source URL with section, the data date, and how the figure was measured."),
        ans=3,
        explain=("Synthesis can compare claims only when each carries where it came from, when it applies and how it was "
                 "obtained. A relies on self-reported confidence and a strategy line that says little about the figure. B "
                 "brings back the volume a structured output is meant to remove. C leaves out the metadata that cannot be "
                 "recovered afterwards."),
        scenarios=(3,), points=("5.1:S5",),
        evidence=(_SOURCE,),
        community="",
        qtype="configure", level="medium", principle="preserve_information",
        situation="choosing fields for a research subagent's structured output",
        trap="self-reported confidence, full page text or no dates",
    ),
    MCQ(
        id="Q5.1-27",
        q=("Two analysis subagents inspect a repository for dead code, and both branches matter to the release. One reports "
           "that `parse_legacy` has no callers, the other reports three callers, and each finding is only a function name and "
           "a verdict. The main agent, which has no repository access of its own, deletes the function and the release build "
           "fails. It later emerges that one subagent searched `main` with grep and the other `release/4` through the "
           "compiler's call graph. What should change?"),
        opts=("Run both subagents on the same single branch, so that their verdicts agree with each other.",
              "Require each finding to name the branch searched and the method used.",
              "Have the main agent re-run both searches itself whenever the two verdicts differ.",
              "Add a third subagent that casts the deciding vote whenever two verdicts conflict."),
        ans=1,
        explain=("The verdicts were both right for what each searched, and the main agent could not see that. Branch and method "
                 "in each finding let it reconcile them, and the main agent receives only the subagent's final message. A "
                 "removes the release branch from the analysis. C is impossible without repository access. D adds a vote and "
                 "still cannot tell which scope each result covered."),
        scenarios=(2,), points=("5.1:S5",),
        evidence=(_FINAL,),
        community="",
        qtype="diagnose", level="hard", principle="preserve_information",
        situation="parse_legacy has no callers on main and three on release/4",
        trap="align the branches or add a tiebreak subagent",
    ),
    # ---- S6: structured upstream output for small downstream budgets ----
    MCQ(
        id="Q5.1-28",
        q=("An exploration subagent maps where a deprecated API is used, across 90 files and 140 call sites, and returns the full "
           "text of every file it opened, about 35,000 tokens. The main agent has roughly 12,000 tokens of room left, needs "
           "each location for its refactor plan, and begins dropping files from it. What is the most effective change?"),
        opts=("Have the subagent return a prose summary of each file in place of the file text.",
              "Have the main agent read the returned text in two halves, and plan the whole refactor in two steps.",
              "Have the subagent return a list of file path, line, symbol and relevance score per use.",
              "Ask the subagent to return the same file text with the most important files placed first."),
        ans=2,
        explain=("The main agent needs where and how each use occurs, not the file contents. A still returns about 90 summaries "
                 "in prose, which stay long and may not give exact lines. B splits the plan, so no step sees all the uses. D "
                 "keeps the volume and just reorders it."),
        scenarios=(2,), points=("5.1:S6",),
        evidence=(_FINAL,),
        community="",
        qtype="fix", level="easy", principle="proportionate",
        situation="35,000 tokens of file text reach a main agent with 12,000 tokens left",
        trap="summarise per file or reorder the same text",
    ),
    MCQ(
        id="Q5.1-29",
        q=("Six research subagents each return 12 structured findings (fact, citation, and a relevance score each subagent "
           "assigns by its own judgement), about 3,000 tokens per subagent. The synthesis agent can take in 8,000 tokens. "
           "Cutting the combined input at 8,000 tokens drops three subagents entirely. What is the best way to fit the budget?"),
        opts=("Cap each subagent at about 1,300 tokens, returning its top-priority findings with citations.",
              "Ask each subagent for a 250-word narrative of its findings in place of the structured items.",
              "Cut the combined input at 8,000 tokens, but shuffle the subagent order each run to spread the loss.",
              "Send the findings in two requests and have the synthesis agent write two reports to be merged."),
        ans=0,
        explain=("Each subagent knows its own material, so a capped, prioritised, structured list sized to its share keeps every "
                 "source represented with citations. B drops the citations and structure that make checking possible. C still "
                 "throws away whole subagents, just different ones each time. D splits the synthesis and leaves it without a "
                 "view of all the findings."),
        scenarios=(3,), points=("5.1:S6",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: structured upstream output for small downstream budgets is a guide skill.",
        qtype="choose", level="hard", principle="proportionate",
        situation="18,000 tokens of structured findings against an 8,000-token synthesis budget",
        trap="truncate the tail, shuffle the order or return narratives",
    ),
    MCQ(
        id="Q5.1-30",
        q=("You changed research subagents from returning narrative reasoning to returning key facts, citations and relevance "
           "scores, because the downstream synthesis budget is small. How should you check that the change did not lose "
           "information the reports need?"),
        opts=("Compare the token counts of old and new outputs, and accept the change if the new ones are under budget.",
              "Ask the synthesis agent to rate its confidence in each report, and compare the averages before and after.",
              "Read a sample of the new outputs and confirm that they look complete and are easy to read.",
              "Run the same questions under both formats and compare the reports against facts known from the sources."),
        ans=3,
        explain=("The outcome that matters is report quality against known facts, measured under both formats. A shows only that "
                 "the output fits. B uses the agent's self-reported confidence, which is not evidence of accuracy. C checks how "
                 "the outputs look, and a tidy output can still lack a needed fact."),
        scenarios=(3,), points=("5.1:S6",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: evaluating an upstream format change is not covered by an official page.",
        qtype="evaluate", level="hard", principle="independent_check",
        situation="validating the switch from narrative to structured subagent output",
        trap="check size, self-confidence or appearance",
    ),
)
