"""Exam bank · TS 4.3. Original questions; see docs/MCQ_BANK_PLAN.md."""
from utils.mcq_sets import MCQ, Evidence

TS = "4.3"
BULLETS = {
    "K1": "Tool use with JSON schemas is the most reliable route to schema-compliant output, with no JSON syntax errors",
    "K2": "tool_choice auto may return text, any must call some tool, and a forced selection must call one named tool",
    "K3": "Strict schemas remove syntax errors but not semantic errors such as line items that do not sum or values in the wrong field",
    "K4": "Schema design: required versus optional fields, and enums with an other value plus a detail string",
    "S1": "Defining extraction tools with JSON schemas as input parameters and reading the data from the tool_use response",
    "S2": "Setting tool_choice any to guarantee structured output when several extraction schemas exist and the document type is unknown",
    "S3": "Forcing a named tool so that one particular extraction runs before the enrichment steps",
    "S4": "Making fields optional or nullable when the source may lack the information, so the model does not invent values",
    "S5": "Adding enum values such as unclear for ambiguous cases, and other plus a detail field for extensible categories",
    "S6": "Putting format normalization rules in the prompt alongside strict output schemas",
}

QUESTIONS = (
    # ---- K1: tool_use with a JSON schema ----
    MCQ(
        id="Q4.3-01",
        q=("A receipt pipeline asks Claude to \"respond with only a JSON object\" and parses the reply with `json.loads`. Across 1,200 "
           "receipts, 31 replies failed to parse: some begin with \"Here is the extracted data:\" and others end with a note about an "
           "unreadable line. Which change most reliably removes these failures?"),
        opts=("Cut each reply down to the text between its first and last curly brace, and parse that part.",
              "Define a strict tool whose `input_schema` is the receipt record, and read its input.",
              "Repeat the instruction at the end of the prompt, and add two examples that show a bare JSON reply.",
              "Re-send the request up to three times when a reply fails to parse, and keep the first one that parses."),
        ans=1,
        explain=("A tool's input follows its schema, so the record arrives as structured data with no prose around it and nothing "
                 "to parse. A hides the symptom, and it still breaks on a stray brace inside a note. C asks for compliance and "
                 "cannot guarantee it. D pays for extra requests and still ends with a reply that happens to parse."),
        scenarios=(6,), points=("4.3:K1", "4.3:S1"),
        evidence=(Evidence("api:agents-and-tools/tool-use/strict-tool-use", "Tool `input` strictly follows the `input_schema`"),),
        qtype="fix", level="easy", principle="deterministic",
        situation="receipt replies wrapped in a sentence fail json.loads in 31 of 1,200",
        trap="strip the text around the braces or retry",
    ),
    MCQ(
        id="Q4.3-02",
        q=("An extraction prompt for purchase orders shows a 40-line example record and says every record must include `currency`. "
           "Across 5,000 documents, 90 records (1.8%) came back with no `currency` key, and the loader throws on each of them. "
           "The team wants the key present in every record, not just in most. Which configuration achieves that?"),
        opts=("Put the `currency` rule in capital letters at the very start of the system prompt, before everything else.",
              "Send a second request for the 90 records that asks only for the missing key, then merge the answers.",
              "Add a second example that shows `currency` beside the total, and also lower the temperature to zero.",
              "Mark `currency` as required in a strict extraction tool's `input_schema`, and read the input."),
        ans=3,
        explain=("Required fields in a strict tool schema are part of what the output is constrained to, so a record without the key "
                 "cannot be returned. A and C make the omission less likely and cannot promise it. B repairs records after the "
                 "loader has already failed and doubles the work on every miss."),
        scenarios=(6,), points=("4.3:K1",),
        evidence=(Evidence("api:build-with-claude/structured-outputs", "Guaranteed field types and required fields"),),
        qtype="configure", level="medium", principle="deterministic",
        situation="1.8% of purchase-order records lack a currency key despite an example record",
        trap="repeat the rule in the prompt",
    ),
    MCQ(
        id="Q4.3-03",
        q=("A CI job asks Claude for a review and sets the pull request's check status from the last line of the reply, which "
           "should read `VERDICT: PASS` or `VERDICT: FAIL`. In 2% of 2,000 runs the last line says things like \"Verdict - pass\" or "
           "\"Overall: looks fine\", and the status step errors. Which design is most reliable?"),
        opts=("Put the verdict and the comment in two fields of one strict tool; set the status from the verdict.",
              "Make the status step case-insensitive and accept `pass`, `passed`, `ok` and `looks fine` as success.",
              "Add a second request that reads the review text and answers PASS or FAIL for the status step to use.",
              "Put three example last lines in the prompt, and tell the model to copy the format exactly as shown."),
        ans=0,
        explain=("A schema with an enum for the verdict and a string for the comment makes both machine-readable and human-readable "
                 "output arrive in fixed places. B chases wordings one at a time and fails on the next new phrase. C adds a model "
                 "call to interpret text that did not need to be text. D is a request for compliance, which the 2% shows is not enough."),
        scenarios=(5,), points=("4.3:K1",),
        evidence=(Evidence("api:agents-and-tools/tool-use/strict-tool-use", "Tool `input` strictly follows the `input_schema`"),),
        qtype="choose", level="medium", principle="deterministic",
        situation="verdict parsed from the last line of a review reply goes wrong in 2% of runs",
        trap="widen the text matcher",
    ),
    # ---- K2: auto, any, forced ----
    MCQ(
        id="Q4.3-04",
        q=("A claims service passes three extraction tools, `extract_claim_form`, `extract_medical_bill` and `extract_police_report`, "
           "with `tool_choice` set to `any`. Each description is one sentence such as \"Extracts data from the document.\" Every "
           "request now ends in a tool call, but a labelled sample of 800 shows 9% of medical bills processed by "
           "`extract_claim_form`, with plausible-looking fields. What is the most likely root cause?"),
        opts=("`any` falls back to the first tool in the list when a document could fit more than one schema.",
              "These documents needed a forced tool instead, so `any` was the wrong mode for them.",
              "Selection is left to the model, and descriptions that read alike give it little to go on.",
              "Strict checking is off, so the model is free to send bill data to the wrong tool."),
        ans=2,
        explain=("`any` guarantees that some tool is called and nothing about which one, so selection quality rests on the tool "
                 "descriptions. A describes a fallback that does not exist. B would send every document through one schema, which "
                 "is worse for mixed uploads. D confuses schema conformance with choosing the right tool: a bill fitted into the "
                 "wrong schema can still be valid."),
        scenarios=(6,), points=("4.3:K2",),
        evidence=(Evidence("api:agents-and-tools/tool-use/define-tools", "`any` tells Claude that it must use one of the provided tools"),
                  Evidence("api:agents-and-tools/tool-use/define-tools", "This is by far the most important factor in tool performance.")),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="medical bills land in the claim-form schema under any with one-line descriptions",
        trap="blame the mode instead of the descriptions",
    ),
    MCQ(
        id="Q4.3-05",
        q=("A CI step has two tools, `list_changed_files` and `report_review`, and uses `tool_choice: any` on a model that supports it. The system prompt says: "
           "\"Before calling a tool, write a short paragraph explaining your reasoning; it will be posted on the pull request.\" "
           "Across 400 runs no paragraph was ever posted, although the tool calls and their inputs look correct. What is the most "
           "likely root cause?"),
        opts=("The instruction comes after the tool descriptions, so the model treats it as optional.",
              "The API starts the reply with a tool call under `any`, so no text can come before it.",
              "A reply that contains a `tool_use` block has its text blocks discarded before it is returned.",
              "Text is only allowed after the last tool of a run, and `list_changed_files` is called first."),
        ans=1,
        explain=("With `any` or a forced tool the response begins with the tool call, so a paragraph written \"before\" it cannot "
                 "exist; the reasoning has to travel in a field of the schema, or the mode has to be `auto`. A blames prompt order "
                 "for a limit that sits in the API. C is false, since text and tool blocks can share a response under `auto`. D "
                 "invents a rule about the last tool."),
        scenarios=(5,), points=("4.3:K2",),
        evidence=(Evidence("api:agents-and-tools/tool-use/define-tools", "This means that the models will not emit a natural language response or explanation before `tool_use` content blocks, even if explicitly asked to do so."),),
        basis="docs",
        qtype="diagnose", level="hard", principle="fit_for_purpose",
        situation="requested reasoning paragraph never appears under any in a CI review step",
        trap="reorder the prompt instead of putting the reasoning in the schema",
    ),
    MCQ(
        id="Q4.3-06",
        q=("A shared extraction service exposes `extract_po` and `extract_invoice` to several inboxes. The purchase-order inbox "
           "receives only purchase orders, yet 3% of its documents go to `extract_invoice` because they mention payment terms. The "
           "other inboxes need both tools to stay available. On a model that supports forced tool use, what is the best configuration for the purchase-order inbox?"),
        opts=("Force `extract_po` with `tool_choice: {\"type\": \"tool\", \"name\": \"extract_po\"}` for that inbox.",
              "Use `tool_choice: any` for that inbox, so the model has to call a tool and will pick the closest schema.",
              "Keep `auto` and add a line to the system prompt saying that the inbox holds purchase orders.",
              "Remove `extract_invoice` from the shared tool list so that every inbox uses `extract_po`."),
        ans=0,
        explain=("When the type is known, naming the tool leaves the model nothing to choose. B still leaves the choice with the "
                 "model, which is where the 3% comes from. C is a hint under `auto`, with no guarantee. D breaks the inboxes that "
                 "do receive invoices."),
        scenarios=(6,), points=("4.3:K2",),
        evidence=(Evidence("api:agents-and-tools/tool-use/define-tools", "`tool` forces Claude to always use a particular tool."),),
        qtype="choose", level="easy", principle="fit_for_purpose",
        situation="purchase orders mentioning payment terms drift to the invoice tool",
        trap="use any or a prompt hint when the type is already known",
    ),
    # ---- K3: syntax versus semantic errors ----
    MCQ(
        id="Q4.3-07",
        q=("An invoice tool returns `vendor`, `total` and an array of `line_items`, and every response validates against its "
           "schema. A finance review of 600 invoices found 21 where the line items add up to a different amount than `total`, "
           "usually by a transposed digit. The team asks for a stricter schema. What is the most effective step?"),
        opts=("Add `minimum` and `maximum` bounds to `total` so that implausible totals are rejected.",
              "Switch to a larger model, whose totals are less likely to be transposed.",
              "Add a sentence to the tool description asking the model to check that the figures sum.",
              "Compare the line-item sum with `total` in code, and send mismatches for review."),
        ans=3,
        explain=("A schema checks the shape of a response, and a total that disagrees with its lines is still the right shape, so the "
                 "relationship has to be checked in code. A bounds a single value and would pass a wrong total inside the range. B "
                 "lowers the rate without checking anything. C asks the model to police itself."),
        scenarios=(6,), points=("4.3:K3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: Knowledge 3 names line items that do not sum to the total; no official page discusses semantic checks on extraction output.",
        qtype="fix", level="medium", principle="independent_check",
        situation="valid invoice records whose line items disagree with the total",
        trap="tighten the schema or ask the model to self-check",
    ),
    MCQ(
        id="Q4.3-08",
        q=("A purchase-order schema has two required string fields, `address_a` (\"the first address\") and `address_b` (\"the "
           "second address\"). Output validates every time, but a review of 500 multi-address orders found billing and shipping "
           "details swapped in 11%, because suppliers print them in different orders. Which change best addresses the cause?"),
        opts=("Switch strict checking on, so that each value stays in the field that the schema defines for it.",
              "Reject any order in which the two addresses are identical, and send it back for a manual check.",
              "Rename them `billing_address` and `shipping_address`, and describe how documents label each.",
              "Add a `confidence` number to each address, and send low-confidence orders to a human for review."),
        ans=2,
        explain=("The field names say nothing about meaning, so the model has no basis for assigning an address to either; names "
                 "and descriptions that mirror the document labels give it one. A guarantees types, and a swapped address is still "
                 "a string. B catches a case that is not the one described. D relies on the model's own confidence to find "
                 "its mistakes."),
        scenarios=(6,), points=("4.3:K3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: Knowledge 3 names values in the wrong field; naming fields after the document's own labels is a schema-design judgment no official page states.",
        qtype="fix", level="medium", principle="explicit",
        situation="billing and shipping addresses swapped under vague field names",
        trap="add strictness or a confidence field instead of meaningful names",
    ),
    MCQ(
        id="Q4.3-09",
        q=("A team moved its contract extraction to a tool with a JSON schema and told management: \"Schema validation passes on "
           "100% of 4,000 documents, so extraction accuracy is now 100%.\" You are asked to review the claim. What is the "
           "most accurate response?"),
        opts=("Correct: a response that validates has every field filled from the right part of the document.",
              "Validity covers form only; accuracy needs field-level comparison with labelled documents.",
              "Partly right: add a check that the line items sum to the total, and call a pass accuracy.",
              "Not credible: a model cannot reach 100% validity without a repair step after the response."),
        ans=1,
        explain=("A schema constrains the form of the output and says nothing about whether a value is right, so accuracy must be "
                 "measured against known answers. A treats form as truth. C catches one kind of error, and wrong values that still add up "
                 "pass it. D doubts a result that tool schemas are designed to deliver."),
        scenarios=(6,), points=("4.3:K3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: Knowledge 3 says strict schemas leave semantic errors; how to measure accuracy is a judgment the official docs do not cover.",
        qtype="evaluate", level="easy", principle="independent_check",
        situation="100% schema validity reported as 100% extraction accuracy",
        trap="treat validity as correctness",
    ),
    # ---- K4: required versus optional, enum with other ----
    MCQ(
        id="Q4.3-10",
        q=("A vendor-invoice schema is being finalised. From 500 sampled documents, field presence is: `vendor_name` 100%, "
           "`total_amount` 100%, `due_date` 88%, `tax_id` 63% and `po_number` 41%. Downstream, only the vendor and the total are "
           "needed to post an invoice. Which design is best?"),
        opts=("Require `vendor_name` and `total_amount`, and make the other three optional or nullable.",
              "Require all five, and tell the model to enter a placeholder when a value is missing.",
              "Require the three fields present in more than half the documents, and make the other two optional.",
              "Make every field optional, since the model will fill in whatever it finds."),
        ans=0,
        explain=("A field belongs in `required` only if every document of this type has it; otherwise the schema pushes the model "
                 "to supply something. B turns missing values into fake ones. C requires `due_date`, which is absent in 12% of "
                 "documents, and `tax_id`, absent in 37%. D lets the two fields that posting depends on go missing."),
        scenarios=(6,), points=("4.3:K4",),
        evidence=(Evidence("code:agent-sdk/structured-outputs", "The schema includes optional fields (`author` and `date`) since git blame information might not be available for all files."),),
        qtype="choose", level="medium", principle="fit_for_purpose",
        situation="choosing required fields from presence rates of 100%, 88%, 63% and 41%",
        trap="require whatever is usually present",
    ),
    MCQ(
        id="Q4.3-11",
        q=("A shipping-document schema defines `carrier` as an enum of the five carriers the company uses. After onboarding "
           "regional partners, 14% of documents name a carrier that is not listed, and the model assigns the nearest listed one, "
           "which corrupts the cost report. Which schema change fixes this and keeps reports groupable?"),
        opts=("Replace the enum with a free-text string so that any carrier name can be recorded.",
              "Make `carrier` optional, so that unlisted carriers are left out of the record.",
              "Add an `other` value to the enum and a `carrier_detail` string for the name.",
              "Add the twenty partner carriers to the enum now, and repeat that whenever a partner joins."),
        ans=2,
        explain=("`other` with a detail string keeps the known carriers as clean groups and records the rest without forcing a wrong "
                 "match. A gives up grouping, since spelling variants become separate values. B drops the carrier for exactly the "
                 "documents that are new. D can never be complete and lets errors reappear with each new partner."),
        scenarios=(6,), points=("4.3:K4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: Knowledge 4 names the enum with an other value plus a detail string; no official page discusses this pattern.",
        qtype="choose", level="easy", principle="fit_for_purpose",
        situation="partner carriers missing from a five-value carrier enum",
        trap="free text or an endless enum",
    ),
    MCQ(
        id="Q4.3-12",
        q=("A teammate reviewing your CI schema proposes adding an `other` value with a detail string to every enum. Two of them "
           "are `failure_type` (test, build, lint, timeout; new kinds appear every quarter) and `severity` (low, medium, high, "
           "critical; a policy scale that code uses to page the on-call engineer). How should you evaluate the proposal?"),
        opts=("Accept it for both, since an enum without an escape value fails on any input it does not list.",
              "Reject it for both, since a detail string lets the model put anything into the field.",
              "Accept it for `severity` only, since paging depends on it and a wrong value there costs more.",
              "Accept it for `failure_type` only; `severity` is a closed scale that code maps to pages."),
        ans=3,
        explain=("The pattern is for categories that will grow. A closed scale defined by policy has a fixed meaning in code, and an "
                 "`other` there would be a value nothing can route. A applies the pattern where it adds a hole. B discards its "
                 "benefit for the open field. C reverses the logic and makes the paging field the one that can escape its scale."),
        scenarios=(5,), points=("4.3:K4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: Knowledge 4 limits the other-plus-detail pattern to extensible categories; applying it only where categories grow is a design judgment.",
        qtype="evaluate", level="hard", principle="proportionate",
        situation="an other value proposed for a closed severity scale as well as an open failure type",
        trap="add an escape value to every enum",
    ),
    # ---- S1: defining extraction tools and reading tool_use ----
    MCQ(
        id="Q4.3-13",
        q=("An extraction service defines `record_invoice` and reads the result with `response.content[0].input`. In 400 requests, "
           "140 raise an AttributeError, and the failing responses begin with a sentence such as \"I'll extract the fields from "
           "this invoice.\" What is the best fix?"),
        opts=("Add \"do not write any text before calling the tool\" to the system prompt.",
              "Look through the content blocks for the one of type `tool_use` and read its input.",
              "Parse the first text block with `json.loads`, since the model repeats the fields in it.",
              "Retry each failing request until the first block comes back as a tool call."),
        ans=1,
        explain=("A response can hold a text block as well as the tool call, so the code should find the block by its type "
                 "instead of by position. A asks for compliance on a point the code can handle on its own. C parses text that was "
                 "never meant to hold the record. D spends requests to fit a response to a fragile assumption."),
        scenarios=(6,), points=("4.3:S1",),
        evidence=(Evidence("api_handle_calls", "Extract the `name`, `id`, and `input` from the `tool_use` block."),),
        qtype="fix", level="easy", principle="model_driven",
        situation="a leading sentence shifts the tool_use block away from content[0]",
        trap="rely on block position or a prompt rule against text",
    ),
    MCQ(
        id="Q4.3-14",
        q=("An extraction tool is defined with `input_schema: {\"type\": \"object\"}` and a description that lists the wanted "
           "fields in prose. Across 1,000 documents the keys vary: `invoice_no`, `invoiceNumber` and `invoice_number` all appear, and "
           "the loader fails on 17% of the records. What is the most likely root cause?"),
        opts=("The schema leaves the property names open, so nothing fixes the keys the model uses.",
              "`tool_choice` is `auto`, so on some replies the model writes the record as text, with its own key names.",
              "The field list belongs in the system prompt, because tool descriptions are read less closely.",
              "Strict mode is off, and switching it on would map every spelling to the key the loader expects."),
        ans=0,
        explain=("The contract between the model and the loader is the `input_schema`, and this one says nothing about names, "
                 "so the prose list is only a suggestion. B is not what the stem shows, and under `auto` a text reply would not carry these keys either. C moves the list to another "
                 "place where it is still prose. D credits strict mode with choosing names, when it enforces the properties a schema "
                 "defines and this one defines none."),
        scenarios=(6,), points=("4.3:S1",),
        evidence=(Evidence("api_handle_calls", "`input`: An object containing the input being passed to the tool, conforming to the tool’s `input_schema`."),),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="three spellings of the invoice number under an empty object schema",
        trap="fix the description instead of defining the properties",
    ),
    MCQ(
        id="Q4.3-15",
        q=("Supplier contracts hold between 0 and 60 line items, each with `sku`, `quantity` and `unit_price`. You are defining "
           "the strict extraction tool, and the application will read the items from the `tool_use` response. Which design is best?"),
        opts=("Fields `item_1` to `item_20`, each an object, with a note to leave unused ones empty.",
              "A single `line_items_json` string field, which the application parses.",
              "A separate `add_line_item` tool, called once per line until the contract ends.",
              "A `line_items` array whose items are objects with the three fields marked required."),
        ans=3,
        explain=("An array of objects holds any number of lines, and the schema enforces the fields of every item. A caps the count at "
                 "twenty and invites filler values in the unused slots. B puts JSON inside a string, which brings back the syntax "
                 "errors that the schema was there to remove. C needs a loop of calls that may stop early, with no record of "
                 "what is missing."),
        scenarios=(6,), points=("4.3:S1", "4.3:K4"),
        evidence=(Evidence("api:agents-and-tools/tool-use/strict-tool-use", "Tool `input` strictly follows the `input_schema`"),),
        qtype="choose", level="hard", principle="fit_for_purpose",
        situation="0 to 60 contract line items in one extraction tool",
        trap="numbered fields, a JSON string field or one tool call per line",
    ),
    # ---- S2: any with several schemas ----
    MCQ(
        id="Q4.3-16",
        q=("A mortgage-document service passes four extraction tools with `tool_choice: any` (on a model that supports it), and every upload must yield a "
           "structured result. About 7% of uploads are cover sheets or blank scans, and each is run through one of the extraction "
           "tools, producing records with invented-looking values. A line in the prompt tells the model to reply \"not a document\" "
           "for these, but no such reply ever appears. Which change fixes this?"),
        opts=("Switch to `auto`, so the model may answer in plain text when a page holds no data.",
              "Force the most general extraction tool, whose optional fields a blank page can leave empty.",
              "Add a `flag_unprocessable` tool with a reason field, and keep `any`.",
              "Repeat the \"not a document\" rule in bold in the system prompt, with two examples."),
        ans=2,
        explain=("Under `any` the model must call a tool and cannot write a text reply, so it needs a tool that means \"this is not a "
                 "document\" and still gives a structured result. A brings back conversational replies for the other 93% of uploads, "
                 "which broke the pipeline before. B forces one schema onto every document. D asks for a text reply that `any` "
                 "does not allow."),
        scenarios=(6,), points=("4.3:S2", "4.3:K2"),
        evidence=(Evidence("api:agents-and-tools/tool-use/define-tools", "`any` tells Claude that it must use one of the provided tools"),
                  Evidence("api:agents-and-tools/tool-use/define-tools", "This means that the models will not emit a natural language response or explanation before `tool_use` content blocks, even if explicitly asked to do so.")),
        qtype="choose", level="medium", principle="fit_for_purpose",
        situation="blank scans forced through extraction tools under any",
        trap="switch to auto or repeat a text-reply rule",
    ),
    MCQ(
        id="Q4.3-17",
        q=("Mixed claim uploads (accident forms, repair estimates, witness statements) arrive with no type label. On a labelled "
           "sample of 2,000, `tool_choice: any` (on a model that supports it) over three extraction tools picks the matching tool 99% of the time. A teammate "
           "proposes a separate classification request that picks the type first and then forces the matching tool \"for "
           "certainty\"; on the same sample the classifier is right 98.7% of the time. How should you evaluate this?"),
        opts=("Keep `any`: it already returns a structured result from the right tool, with no extra step.",
              "Adopt it, since forcing a named tool is more reliable than letting the model choose between tools.",
              "Adopt it, since `any` cannot be used when the documents carry no type label.",
              "Keep `any`, but only if the model also reports a confidence score for the tool it chose."),
        ans=0,
        explain=("`any` is meant for unknown types: it guarantees a tool call and the model picks the schema. The classifier would "
                 "make the same kind of choice with slightly lower accuracy, and then add a call. B forgets that the forced tool is "
                 "only as right as the classifier that names it. C reverses the purpose of `any`. D leans on self-reported "
                 "confidence."),
        scenarios=(6,), points=("4.3:S2",),
        evidence=(Evidence("api:agents-and-tools/tool-use/define-tools", "`any` tells Claude that it must use one of the provided tools"),),
        qtype="evaluate", level="hard", principle="proportionate",
        situation="a classify-then-force step proposed over any for unlabelled claim uploads",
        trap="add a classifier where any already works",
    ),
    MCQ(
        id="Q4.3-18",
        q=("A pipeline offers three extraction tools with `tool_choice: any`, so every request ends in a tool call. But in 1.5% of "
           "calls a numeric field such as `page_count` arrives as the string \"12\", and the loader throws. Which addition "
           "fixes this while keeping `any`?"),
        opts=("A sentence in the system prompt saying numeric fields must be numbers.",
              "`strict: true` on the tool definitions.",
              "A forced tool selection, which also fixes the types of that tool's fields.",
              "A retry that re-sends the request whenever the loader throws."),
        ans=1,
        explain=("`any` makes sure a tool is called, and strict tool use makes sure its input matches the schema; the two are meant to be "
                 "combined. A is a request that a setting can guarantee. C changes which tool is called and does nothing for the "
                 "types. D repeats work after the failure."),
        scenarios=(6,), points=("4.3:S2", "4.3:K1"),
        evidence=(Evidence("api:agents-and-tools/tool-use/define-tools", "Set `strict: true` on your tool definitions to enable schema validation."),),
        basis="docs",
        qtype="configure", level="medium", principle="deterministic",
        situation="numeric fields arrive as strings under any",
        trap="rely on a prompt sentence or a retry for types",
    ),
    # ---- S3: forced tool before enrichment ----
    MCQ(
        id="Q4.3-19",
        q=("On a model that supports forced tool use, a claims pipeline forces `extract_claim_header` on its first request, then "
           "calls again with `auto` and two enrichment tools. The enrichment tools are being called with claim IDs that appear "
           "nowhere in the document, in nearly every run. The second request holds the original document and the enrichment "
           "tools. Which change fixes this?"),
        opts=("Force `extract_claim_header` again on the second request, so that the ID is extracted once more.",
              "Add a prompt rule saying that claim IDs must come from the document text.",
              "Add the assistant's `tool_use` turn and a matching `tool_result` turn before the next request.",
              "Use `any` on the second request, which carries over the arguments of the earlier tool call."),
        ans=2,
        explain=("The model only knows what is in the messages, so the extracted header has to come back as a `tool_result` that "
                 "answers the forced call; without it the model has nothing to take the ID from. A would repeat the first step "
                 "and still not give the model the result. B points the model at a document that holds no such ID. D describes "
                 "a carry-over that does not exist."),
        scenarios=(6,), points=("4.3:S1", "4.3:S3"),
        evidence=(Evidence("api:agents-and-tools/tool-use/how-tool-use-works", "Send a new request containing the original messages, the assistant’s response, and a user message with the `tool_result` blocks."),),
        basis="docs",
        qtype="diagnose", level="hard", principle="explicit",
        situation="the extracted claim header never reaches the enrichment request",
        trap="re-force the extraction or ask the model to find the ID in the document",
    ),
    MCQ(
        id="Q4.3-20",
        q=("A lease-review pipeline has three steps: `extract_header` must run first; then the model decides which of two lookup "
           "tools to call, and some leases need neither; finally the model writes a plain-text summary for the reviewer. On a "
           "model that supports forced tool use, a teammate proposes forcing `extract_header` on every request \"for "
           "uniformity\". How should you evaluate this?"),
        opts=("Adopt it: forcing every step keeps the pipeline uniform and removes the chance of a text reply.",
              "Adopt it for the first two steps, which both need tool calls, and use `auto` for the summary.",
              "Reject it, and use `any` on every request so that the model can still choose between the tools.",
              "Reject it: force the first request only, then use `auto` so lookups are optional."),
        ans=3,
        explain=("Forcing guarantees the first extraction, but a forced call also rules out a text reply and repeats the same tool, "
                 "so only the opening request should be forced. A would stop the summary from ever being written. B forces a "
                 "call in the second step even for leases that need no lookup. C has the same effect, since `any` also requires "
                 "a tool call on each request."),
        scenarios=(6,), points=("4.3:S3", "4.3:K2"),
        evidence=(Evidence("api:agents-and-tools/tool-use/define-tools", "`tool` forces Claude to always use a particular tool."),
                  Evidence("api:agents-and-tools/tool-use/define-tools", "This means that the models will not emit a natural language response or explanation before `tool_use` content blocks, even if explicitly asked to do so.")),
        qtype="evaluate", level="medium", principle="proportionate",
        situation="forcing the header tool on every request of a lease pipeline that ends in a text summary",
        trap="force every step for uniformity",
    ),
    MCQ(
        id="Q4.3-21",
        q=("On a model that supports forced tool use, an ingestion service forces `extract_metadata` as its first call so that `title`, `author` and `date` exist before "
           "enrichment runs. In 5% of documents, scanned pages with no readable text, the metadata comes back with a plausible "
           "title and an author name that appear nowhere in the document. Which change best fixes this while keeping the "
           "extraction first?"),
        opts=("Make the three fields nullable, and describe null as nothing found in the document.",
              "Switch to `auto`, so the model can reply that the page is unreadable instead of calling the tool.",
              "Add \"if the page is empty, say so before calling the tool\" to the system prompt.",
              "Skip the forced call for scanned pages, which an OCR step detects before the request."),
        ans=0,
        explain=("A forced call cannot decline, so a schema that demands values makes the model supply some; allowing null lets it "
                 "report absence and keeps the order of steps. B gives up the guarantee that extraction comes first. C asks for "
                 "text before the tool call, which a forced call does not allow. D adds a detector for a case that the schema "
                 "could simply express."),
        scenarios=(6,), points=("4.3:S3", "4.3:S4"),
        evidence=(Evidence("api:agents-and-tools/tool-use/define-tools", "`tool` forces Claude to always use a particular tool."),
                  Evidence("api:test-and-evaluate/strengthen-guardrails/reduce-hallucinations", "Explicitly give Claude permission to admit uncertainty.")),
        qtype="fix", level="medium", principle="preserve_information",
        situation="forced metadata extraction invents authors for unreadable scans",
        trap="drop the forced call or ask for text before it",
    ),
    # ---- S4: nullable and optional fields ----
    MCQ(
        id="Q4.3-22",
        q=("A contract schema marks `termination_notice_days` as a required integer. In an audit of 300 contracts, 45 have no "
           "notice clause, yet all 45 records say 30 days, and a customer acted on one of them. Which change best prevents this?"),
        opts=("Add a few-shot example of a contract with no clause, where the correct value is shown as 0.",
              "Allow null for the field, and describe null as the contract having no notice clause.",
              "Lower the temperature, so that the model stops guessing a typical value for the field.",
              "Send a second request that asks the model whether each extracted value appears in the contract."),
        ans=1,
        explain=("A required field that the source may lack pushes the model to supply something, and 30 is simply a likely number. "
                 "A nullable field gives it an honest answer. A teaches a sentinel that is also a real value, and 0 days is a "
                 "legal notice period. C makes the guess more consistent, not more truthful. D adds a call that the schema change "
                 "makes unnecessary."),
        scenarios=(6,), points=("4.3:S4",),
        evidence=(Evidence("api:test-and-evaluate/strengthen-guardrails/reduce-hallucinations", "Explicitly give Claude permission to admit uncertainty. This technique can drastically reduce false information."),),
        qtype="fix", level="medium", principle="preserve_information",
        situation="all 45 contracts without a notice clause say 30 days",
        trap="a zero sentinel or a lower temperature",
    ),
    MCQ(
        id="Q4.3-23",
        q=("Receipts feeding a spending dashboard use `tip` as a required number, and the prompt says \"use 0 when no tip "
           "appears\". The dashboard shows average taxi tips of 0.4%. Spot checks show that many of those receipts have no tip "
           "line at all, because tips were paid in cash and are unknown, while others show a printed tip of 0. How should the "
           "design change?"),
        opts=("Keep the schema and add the receipts' tip line to the prompt as a separate note.",
              "Make `tip` optional, and tell the model to leave it out whenever the value is zero.",
              "Make `tip` nullable: null for no tip information, 0 for a printed zero.",
              "Replace `tip` with a string field, so the model can write \"none\" or \"unknown\"."),
        ans=2,
        explain=("Two different facts, no information and a tip of zero, are being stored as the same number. A nullable field keeps them "
                 "apart. A changes the prompt and keeps the collision. B drops real zeros and still cannot say \"unknown\". D "
                 "loses the numeric type and brings back free-text variants."),
        scenarios=(6,), points=("4.3:S4",),
        evidence=(Evidence("code:agent-sdk/structured-outputs", "The agent fills in what it can find and omits the rest."),),
        qtype="choose", level="medium", principle="preserve_information",
        situation="unknown tips stored as zero in a spending dashboard",
        trap="use 0 as a stand-in for missing",
    ),
    MCQ(
        id="Q4.3-24",
        q=("A review tool's schema requires `suggested_fix` (a string) for every finding, and developers apply suggested fixes "
           "automatically. In a month, 4% of the fixes for findings the model could not resolve were plausible but wrong patches, "
           "and two reached main. The team wants a fix only when one can be drawn from the code. Which design is best?"),
        opts=("Add a `fix_confidence` number, and apply only fixes above 0.9.",
              "Add \"only suggest a fix when you are sure\" to the field description, and keep the field required.",
              "Have a second model call review each suggested fix before it is applied.",
              "Make `suggested_fix` nullable, with null for no fix, and apply only non-null fixes."),
        ans=3,
        explain=("A required field makes a wrong patch the only way to finish a finding; a nullable one lets \"no fix\" be an answer "
                 "that the pipeline can act on. A relies on the model's own confidence. B asks the model to be careful and still "
                 "requires a value. C adds a reviewer for a problem that the schema creates."),
        scenarios=(5,), points=("4.3:S4",),
        evidence=(Evidence("api:test-and-evaluate/strengthen-guardrails/reduce-hallucinations", "Explicitly give Claude permission to admit uncertainty."),),
        qtype="choose", level="hard", principle="preserve_information",
        situation="invented patches for findings that have no safe fix",
        trap="confidence score or a second reviewer instead of a nullable field",
    ),
    # ---- S5: unclear, other plus detail ----
    MCQ(
        id="Q4.3-25",
        q=("An accounts-payable schema has `payment_status` with values `paid`, `unpaid` and `partial`. Some scanned invoices carry "
           "both a PAID stamp and a printed \"Balance due: 410.00\", and reviewers found the model splitting these between `paid` "
           "and `unpaid` almost at random, so 9% of 800 reviewed were misfiled. The three statuses cover every real case; the "
           "problem is evidence that conflicts. What is the best schema change?"),
        opts=("Add an `unclear` value, and route those records to a person.",
              "Add an `other` value with a detail string, so the model can describe the conflict.",
              "Allow null for the field, so that conflicting evidence can be reported as null.",
              "Add a `confidence` field, and accept `paid` only when confidence is high."),
        ans=0,
        explain=("An explicit value for ambiguity lets the model say so instead of guessing, and the record can be reviewed. B is "
                 "for categories that are missing from the list, and the stem rules that out. C uses null, which means the "
                 "information is absent, for a case where it is present and contradictory. D uses self-reported confidence to "
                 "decide which guesses to trust."),
        scenarios=(6,), points=("4.3:S5",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: Skill 5 names an unclear value for ambiguous cases; the separation from null and other is a design judgment the official docs do not discuss.",
        qtype="fix", level="medium", principle="calibrated_escalation",
        situation="PAID stamp and balance due on the same invoice",
        trap="use other or null for conflicting evidence",
    ),
    MCQ(
        id="Q4.3-26",
        q=("A support-ticket schema has `product_area` as an enum that includes `other`, with a `product_area_detail` string. A "
           "quarter later, 19% of 6,000 tickets are `other`. In a sample of 300 of them, 40% of the details say \"single sign-on\", "
           "25% say \"data export\" and the rest are scattered. How should you evaluate the schema and what should change?"),
        opts=("Leave it as it is: `other` with a detail is doing what it was designed to do.",
              "Add enum values for the two recurring details, and keep `other` plus a detail for the rest.",
              "Remove `other` and require the nearest listed area, so that the report totals stay complete.",
              "Replace the enum with the detail strings, and group them with a clustering job each quarter."),
        ans=1,
        explain=("The detail strings show that two categories have become common enough to deserve their own value, while the scattered "
                 "tail still needs `other`. A ignores what the data shows. C hides new areas inside wrong ones. D throws away the stable "
                 "categories for the 81% that fit them."),
        scenarios=(6,), points=("4.3:S5", "4.3:K4"),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: Skill 5 names other plus a detail field for extensible categorization; reviewing details to extend the list is a judgment, not an official page.",
        qtype="evaluate", level="medium", principle="preserve_information",
        situation="recurring single-sign-on and export details inside other",
        trap="leave other alone or remove it",
    ),
    MCQ(
        id="Q4.3-27",
        q=("After a team added `unclear` to a failure-category enum, 41% of CI failures are labelled `unclear`; the labelled "
           "mistakes it was meant to cut had been 6%. The field description reads \"use unclear if you are not fully certain\". "
           "Logs for most of the `unclear` failures plainly show a timeout. What is the best fix?"),
        opts=("Remove `unclear` from the enum, which restores the earlier labelling of failures.",
              "Cap `unclear` at 10% of failures per run, using an instruction in the prompt.",
              "Define `unclear` as missing evidence, or evidence that points to several categories.",
              "Let the model write the category as free text, then group the results in a later step."),
        ans=2,
        explain=("The value exists but the description turns it into an escape from any doubt. Defining it by the state of the evidence "
                 "restores its purpose. A returns to the 6% of confident wrong answers. B limits the count and does not say which "
                 "failures qualify. D gives up the fixed categories."),
        scenarios=(5,), points=("4.3:S5",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: Skill 5 names an unclear value for ambiguous cases; defining when to use it is a design judgment not covered by an official page.",
        qtype="fix", level="hard", principle="explicit",
        situation="unclear used for 41% of CI failures under a vague description",
        trap="remove the value or cap its count",
    ),
    # ---- S6: format normalization rules in the prompt ----
    MCQ(
        id="Q4.3-28",
        q=("An invoice tool defines `total` as a number in a strict schema. Output always validates, but a reconciliation of "
           "700 supplier invoices found 38 totals about a thousand times too small. The invoices come from many countries and print amounts as "
           "\"1.234,50 €\", \"1,234.50\" or \"1 234,50\", and the country is not reliably known. The prompt contains no "
           "formatting rules. What is the best fix?"),
        opts=("Change `total` to a string field, and convert the text to a number in the application code.",
              "Add a `minimum` to `total` in the schema, so that implausibly small totals are rejected there.",
              "Send each total that looks too small to a second request that checks it against the page.",
              "Say in the prompt how separators work in each supplier format, and ask for a plain number."),
        ans=3,
        explain=("The schema guarantees a number; it cannot know that the comma is a decimal point in the source. Rules in the prompt "
                 "tell the model how to read each convention. A moves the same problem into code, where the string is just as "
                 "ambiguous, because the locale is not known. B uses a numeric bound, which strict schemas do not support, and a bound would not tell the model how to read the amount. C patches the symptom "
                 "and relies on guessing which totals look small."),
        scenarios=(6,), points=("4.3:S6",),
        evidence=(Evidence("api:build-with-claude/prompt-engineering/claude-prompting-best-practices", "Be specific about the output format and constraints you want."),),
        qtype="fix", level="medium", principle="explicit",
        situation="amounts printed as 1.234,50 read as 1.234 in a number field",
        trap="change the type or add a numeric bound",
    ),
    MCQ(
        id="Q4.3-29",
        q=("A review bot posts inline comments using the `file` field of a strict tool schema (a string). Comments fail to attach "
           "for 22% of findings: the field holds `./src/app.py`, `/repo/src/app.py` or `src/app.py` for the same file, and only the "
           "last form matches the diff. The checkout root varies per job in ways the bot cannot know in advance. What is "
           "the best fix?"),
        opts=("Tell the model to return repository-relative paths with no leading `./` or `/`.",
              "Set `strict: true` on the tool so that the string follows the path format the diff uses.",
              "Strip a fixed `/repo` prefix in the bot before it posts each comment.",
              "Add a second pass that asks the model to check each path against the diff."),
        ans=0,
        explain=("The schema only requires a string, so the convention has to be stated: one form, written where the model reads it. "
                 "B misreads strict mode, which enforces the schema's types and nothing about path style. C handles only the checkout roots it was written for, and the others "
                 "still fail. D adds a call for a rule that can be given up front."),
        scenarios=(5,), points=("4.3:S6",),
        evidence=(Evidence("api:build-with-claude/prompt-engineering/claude-prompting-best-practices", "Be specific about the output format and constraints you want."),),
        qtype="configure", level="easy", principle="explicit",
        situation="three spellings of one file path break inline comments",
        trap="rely on strict mode or a fixed prefix strip",
    ),
    MCQ(
        id="Q4.3-30",
        q=("Invoices from UK, US and German suppliers print slash dates such as `03/04/2025`. The extraction tool returns "
           "`invoice_date` as a string, and the prompt says \"convert dates to ISO 8601\". Output is always valid, but 14% of "
           "dates in a sample of 500 have day and month reversed. Each request already includes the supplier's country code as "
           "metadata. What is the best change?"),
        opts=("Add `format: date` to the field, so that only dates the schema accepts are produced.",
              "Compare each date with the upload date in code, and swap day and month when the date is in the future.",
              "Tell the model which order each supplier country uses for slash dates, and to write ISO 8601.",
              "Add a `date_order` enum that the model fills in per document, and apply it in code."),
        ans=2,
        explain=("The date is ambiguous in the text itself, so the rule has to say how to resolve it, using evidence the request already "
                 "carries. A checks that a date is well formed, and `04/03/2025` is well formed either way. B fixes only dates that "
                 "land in the future. D asks the model to guess the order, which is the step that fails."),
        scenarios=(6,), points=("4.3:S6",),
        evidence=(Evidence("api:build-with-claude/prompt-engineering/claude-prompting-best-practices", "Be specific about the output format and constraints you want."),),
        qtype="choose", level="hard", principle="explicit",
        situation="slash dates read day-first or month-first depending on the supplier's country",
        trap="a schema date format or a code heuristic instead of a stated rule",
    ),
)
