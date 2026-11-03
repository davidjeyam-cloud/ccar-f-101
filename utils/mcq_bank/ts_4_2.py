"""Exam bank · TS 4.2. Original questions; see docs/MCQ_BANK_PLAN.md."""
from utils.mcq_sets import MCQ, Evidence

TS = "4.2"
BULLETS = {
    "K1": "Few-shot examples are the most effective way to get consistent, usable output when instructions alone vary",
    "K2": "Examples show how ambiguous cases are handled (which tool, which coverage gap counts)",
    "K3": "Examples let the model carry judgment over to new patterns instead of matching only listed cases",
    "K4": "Examples reduce hallucination in extraction (informal measurements, varied document structures)",
    "S1": "Write a few targeted examples for ambiguous cases that show why one action beat the alternatives",
    "S2": "Use examples that show the exact review output layout: location, issue, severity, suggested fix",
    "S3": "Use examples that separate acceptable code patterns from real issues to cut false positives and still generalise",
    "S4": "Use examples that show correct handling of varied document structures (inline vs listed citations, methods vs embedded detail)",
    "S5": "Use examples of varied formats to fix empty or null extraction of required fields",
}

BP = "api:build-with-claude/prompt-engineering/claude-prompting-best-practices"

QUESTIONS = (
    # ---- K1: consistent, usable format ----
    MCQ(
        id="Q4.2-01",
        q=("Your CI pipeline asks Claude to summarise each failed test run for a chat channel in three labelled lines: Service, "
           "Likely cause, Owner team. The prompt describes the layout in a paragraph. In about 25% of runs the summary comes "
           "back as a bulleted list, a paragraph, or with the Owner line missing, and the channel bot drops any message it "
           "cannot parse. What is the most effective change?"),
        opts=("Add a few sample summaries in the exact layout, one per kind of failure.",
              "Have the bot re-run the summary until one reply happens to match the layout.",
              "Put the layout paragraph in capitals and repeat it again at the end of the prompt.",
              "Ask Claude to review its own summary and fix the layout before it replies."),
        ans=0,
        explain=("Samples show the layout instead of describing it, which is the most effective way to get consistent output when "
                 "instructions alone vary. B spends extra calls and never changes why replies differ. C repeats an instruction "
                 "that is already not enough. D asks the same model that varies to police its own output."),
        scenarios=(5,), points=("4.2:K1",),
        evidence=(Evidence(BP, "Examples are one of the most reliable ways to steer Claude’s output format, tone, and structure."),),
        qtype="fix", level="easy", principle="explicit",
        situation="failed-test summaries for a chat bot arrive as lists, prose or with the owner line missing",
        trap="emphasise or repeat the prose layout, retry until it matches, or self-review",
    ),
    MCQ(
        id="Q4.2-02",
        q=("A code review bot must post findings in a four-field layout, and about 20% of findings used to break it. The team "
           "added three sample findings to the prompt, re-ran the three pull requests those samples were taken from, and every "
           "finding matched the layout. They want to ship. How should they judge whether the change fixed the inconsistency?"),
        opts=("Re-run the same three pull requests ten more times and check that each finding still matches.",
              "Ask Claude whether each finding in the new output follows the required layout.",
              "Run unseen recent pull requests and measure the share of findings that match.",
              "Check that the sample findings are repeated word for word in the reviewer's output."),
        ans=2,
        explain=("The three pull requests produced the samples, so matching on them shows little. Unseen pull requests show whether "
                 "the layout holds in general, and a measured share can be compared with the old 20%. A repeats the same inputs. "
                 "B uses the model's own opinion as the check. D tests copying, which is not what the team needs."),
        scenarios=(5,), points=("4.2:K1",),
        evidence=(Evidence("guide", ""),),
        community="guide-only: evaluating a prompt change on inputs outside the examples",
        qtype="evaluate", level="medium", principle="independent_check",
        situation="layout fix checked only on the three pull requests the samples came from",
        trap="re-test on the same inputs or ask the model to grade itself",
    ),
    MCQ(
        id="Q4.2-03",
        q=("You are adding sample findings to a CI review prompt that also contains a long block of review rules. Early tests "
           "show Claude sometimes treats a sample's wording as a rule to apply to the pull request itself. How should the "
           "samples be laid out in the prompt?"),
        opts=("Put them in the middle of the rules, so each sample sits next to the rule it illustrates.",
              "Wrap them in example tags, separate from the rules, and make them relevant and varied.",
              "Merge them into the rules text as sentences that begin with \"for instance\".",
              "Put them last and label the whole prompt \"examples only\" so the rules are ignored."),
        ans=1,
        explain=("Wrapping examples in their own tags lets Claude tell them from instructions, and relevant, varied examples avoid "
                 "unintended patterns. A and C blur the boundary between rule and sample, which is how a sample gets read as a "
                 "rule. D throws away the rules the reviewer still needs."),
        scenarios=(5,), points=("4.2:K1",),
        evidence=(Evidence(BP, "Wrap examples in `<example>` tags (multiple examples in `<examples>` tags) so Claude can distinguish them from instructions."),),
        qtype="configure", level="easy", principle="explicit",
        situation="sample findings read as rules when mixed into the rule text",
        trap="interleave samples with rules or discard the rules",
    ),
    # ---- K2: ambiguous cases ----
    MCQ(
        id="Q4.2-04",
        q=("A CI reviewer reads the diff and the changed tests and must point out branches that no test exercises. It reliably flags a new "
           "function with no tests, but for one-line conditionals such as `if retries > limit: use_cache()` it reports an untested branch "
           "in about half of runs, with no pattern. Line coverage on those lines is already 100%, and the tests only ever run with "
           "retries below the limit. Which change is best?"),
        opts=("Examples of new functions with no tests, since those are the cases it already flags well.",
              "Tell the reviewer to treat any line that holds a conditional as a possible untested branch.",
              "Ask it to report its confidence for each finding and discard those below a fixed cut-off.",
              "Add reasoned examples of covered lines that hide an untested branch and ones that do not."),
        ans=3,
        explain=("The ambiguity is whether a covered line still hides an untested branch, and examples with reasons show how that call is made. "
                 "A spends the examples on a case that already works. B flags every conditional and drowns the real gaps. C uses self-reported "
                 "confidence, which is not evidence."),
        scenarios=(5,), points=("4.2:K2",),
        evidence=(Evidence(BP, "Cover edge cases and vary enough that Claude doesn’t pick up unintended patterns."),),
        community="docs cover the edge-case principle; the choice of which examples is the guide's judgment",
        qtype="choose", level="medium", principle="explicit",
        situation="one-line conditionals with full line coverage flagged as untested branches about half the time",
        trap="examples of the wrong cases, a blanket rule or a confidence cut-off",
    ),
    MCQ(
        id="Q4.2-05",
        q=("A contract extractor must fill `signing_party`, and billing needs exactly one primary signer per contract. The full signature "
           "block is always in the input. In about 15% of contracts a company signs as buyer while a director also signs as guarantor, and "
           "the extractor returns one or the other with no consistency. The field description and schema were reviewed and are clear. "
           "What is the most likely root cause?"),
        opts=("The signature block is cut off in long contracts, so the second signer is never seen.",
              "The prompt shows no case with two signers, so each run picks one by chance.",
              "The extractor needs a second pass that reads each document twice to find every signer.",
              "The schema should allow a list, so that both signers can be recorded."),
        ans=1,
        explain=("Nothing in the prompt shows how to settle the choice when two people sign, so it drifts between runs. Examples showing the "
                 "decision and the reason fix that. A contradicts the stem, which says the full block is always present. C adds work while the "
                 "missing guidance stays missing. D changes the data model although billing needs exactly one signer."),
        scenarios=(6,), points=("4.2:K2",),
        evidence=(Evidence(BP, "A few well-crafted examples (known as few-shot or multishot prompting) improve accuracy and consistency."),),
        community="",
        qtype="diagnose", level="easy", principle="root_cause",
        situation="buyer and guarantor both sign and the extractor picks either although billing needs one",
        trap="truncation, another reading pass or a list-valued field",
    ),
    MCQ(
        id="Q4.2-06",
        q=("A CI triage agent has two tools, `rerun_job` and `open_ticket`. For logs such as \"timeout after fetching dependencies\" it picks "
           "`rerun_job` in about 55% of cases and `open_ticket` in the rest, though the team's owners agree on the right tool for most of "
           "these. The tool descriptions were tuned last month and work for clear-cut failures. What is the best fix?"),
        opts=("A few ambiguous logs, each with the tool chosen and the reason it beat the other.",
              "A keyword router in code that sends every log containing \"timeout\" to `rerun_job`.",
              "Examples of clear-cut failures for each tool, so it sees many correct choices together.",
              "A merged `handle_failure` tool that decides internally what to do with the log."),
        ans=0,
        explain=("The missing piece is guidance on the borderline logs, and examples with reasons show how the choice is made. B turns one "
                 "judgment into a text rule that misroutes real outages. C shows cases that already work. D hides the choice inside a tool and "
                 "teaches nothing about it."),
        scenarios=(5,), points=("4.2:K2", "4.2:S1"),
        evidence=(Evidence(BP, "Cover edge cases and vary enough that Claude doesn’t pick up unintended patterns."),),
        community="docs cover the edge-case principle; the tool-choice detail is the guide's judgment",
        qtype="fix", level="medium", principle="model_driven",
        situation="timeout logs split between rerun_job and open_ticket",
        trap="keyword routing, clear-cut examples or merging the two tools",
    ),
    # ---- K3: generalise to new patterns ----
    MCQ(
        id="Q4.2-07",
        q=("Your supplier-invoice extractor maps payment terms to a number of days. The prompt contains a table of eight phrasings, "
           "from \"Net 30\" to \"Due on receipt\", and it handles those well. A new supplier writes \"payable within 45 days of "
           "receiving this invoice\" and the extractor returns 30, the nearest row in the table. What would help most?"),
        opts=("Add the new supplier's phrasing as a ninth row in the table.",
              "Add a similarity step that picks the closest table row and reports its score.",
              "A few examples of varied wordings, each with the days and the reason.",
              "Send every unfamiliar phrasing to a person before the invoice is accepted."),
        ans=2,
        explain=("Examples that show how days follow from the wording let the model handle phrasings nobody listed. A fixes this one "
                 "supplier and the next new wording fails again. B formalises the same wrong behaviour of snapping to a row. D adds "
                 "manual work for a judgment the model can learn."),
        scenarios=(6,), points=("4.2:K3",),
        evidence=(Evidence(BP, "Cover edge cases and vary enough that Claude doesn’t pick up unintended patterns."),),
        qtype="diagnose", level="medium", principle="model_driven",
        situation="payable within 45 days returned as 30 because the prompt lists eight fixed phrasings",
        trap="add the new phrase as another table row or snap to the nearest row",
    ),
    MCQ(
        id="Q4.2-08",
        q=("The team added examples to a CI reviewer and known defect types are now caught consistently. Before rollout, an engineer "
           "wants evidence that the reviewer applies the same judgment to patterns the examples never showed. Which test gives "
           "that evidence?"),
        opts=("Re-run the pull requests that held the defects used in the examples and compare against last week.",
              "Count how many of the example defect types appear in the reviewer's output.",
              "Ask the reviewer to list other defect types it believes it could find.",
              "Run it on real defects of a kind no example shows and count catches."),
        ans=3,
        explain=("Only inputs outside the examples show whether judgment carries over rather than matching listed cases. A and B measure "
                 "what the examples already cover. C relies on the model's claim about itself, not on results."),
        scenarios=(5,), points=("4.2:K3",),
        evidence=(Evidence("guide", ""),),
        community="guide-only: testing generalisation to patterns not shown in the examples",
        qtype="evaluate", level="medium", principle="independent_check",
        situation="checking that example-driven catches extend to defect types never shown",
        trap="test on the example defects or ask the model what else it can find",
    ),
    MCQ(
        id="Q4.2-09",
        q=("An extractor for purchase orders reached 97% accuracy on test documents after you added four examples, all taken from "
           "one big customer's template. In production, orders from other customers, whose totals sit at the top and whose "
           "line items are in a different order, are extracted correctly only 71% of the time. Which statement explains this?"),
        opts=("Few-shot examples help only with output format, not with the choice of which values to extract.",
              "The four examples share one layout, so the model learned that template instead of the task.",
              "The examples belong in the system prompt, where they apply to every document without exception.",
              "Examples cost context, so the later part of each long order is no longer read."),
        ans=1,
        explain=("When all examples look alike, the model picks up their shared layout as if it were part of the task, so other layouts "
                 "fail. Varied examples fix that. A is untrue, since examples also teach what to extract. C changes where they sit, "
                 "not what they show. D has no sign of truncation in the stem."),
        scenarios=(6,), points=("4.2:K3",),
        evidence=(Evidence(BP, "Cover edge cases and vary enough that Claude doesn’t pick up unintended patterns."),),
        qtype="diagnose", level="hard", principle="root_cause",
        situation="four examples from one customer template, 97% in test and 71% on other layouts",
        trap="blame example placement, example purpose or context cost",
    ),
    # ---- K4: hallucination in extraction ----
    MCQ(
        id="Q4.2-10",
        q=("Spot checks of a product-sheet extractor show that 9% of records carry a `warranty_months` value that appears nowhere in the "
           "source sheet; the typical value is 12. The field is already nullable and the prompt says to extract only what the sheet states. "
           "Which change most directly reduces these invented values?"),
        opts=("Examples of sheets without warranty text giving null, next to sheets that state one.",
              "Examples drawn only from sheets that state a warranty, so it learns what a good record looks like.",
              "A check that rejects any record whose warranty differs from the category's usual value.",
              "A confidence score per field, with low-scoring values removed from the record."),
        ans=0,
        explain=("Examples that show an absent field coming back as null teach the model that this is the correct answer, and sheets that state a "
                 "value keep it extracting real ones. B shows only complete records, so absence is never demonstrated. C flags real unusual "
                 "warranties and passes invented ones that match the usual value. D depends on self-reported confidence."),
        scenarios=(6,), points=("4.2:K4",),
        evidence=(Evidence("guide", ""),),
        community="guide only: the docs page on admitting uncertainty does not state that null examples are the fix",
        qtype="diagnose", level="medium", principle="explicit",
        situation="warranty_months of 12 invented for sheets that never mention a warranty",
        trap="examples of complete records only, comparison with typical values or a confidence cut-off",
    ),
    MCQ(
        id="Q4.2-11",
        q=("A furniture-listing extractor fills `width_cm`, and the search page filters on that number. For phrases like \"about two metres\" "
           "it returns 200 correctly, but for \"roughly shoebox-sized\" it returns 33, and for \"fits most hallways\" it returns 90. Every "
           "such value is invented and lands items in the wrong search results. Telling the model \"never estimate\" cut the problem by only "
           "a few points. What is the best fix?"),
        opts=("Examples that convert each object comparison to a number using the object's typical size.",
              "Run extraction twice and keep a width only when both runs return the same number.",
              "Examples where measurable phrases give a number and object comparisons give null.",
              "Make `width_cm` a free-text field so the original wording is kept as written."),
        ans=2,
        explain=("The examples show where the line falls between a measurable phrase and an unquantified comparison, which the instruction alone "
                 "could not teach. A demonstrates the invention it should stop. B can agree on the same invented number. D breaks the numeric "
                 "filter that the search page depends on."),
        scenarios=(6,), points=("4.2:K4",),
        evidence=(Evidence("api:build-with-claude/prompt-engineering/prompting-claude-opus-5", "Positive examples of the communication style you want tend to be more effective than instructions about what not to do."),),
        community="",
        qtype="fix", level="medium", principle="explicit",
        situation="shoebox-sized and fits most hallways turned into invented widths for a numeric filter",
        trap="examples that convert comparisons, agreement between two runs or free text",
    ),
    MCQ(
        id="Q4.2-12",
        q=("A lease extractor returns records that all pass schema validation, yet a reviewer finds that 6% contain a `notice_period_days` "
           "that the lease text does not support: the lease states no period, or a different one. Running each lease twice and keeping "
           "only fields that agree removed little of this. Which approach should the team try next?"),
        opts=("Examples of complete leases in which every field, including the notice period, has a value.",
              "Use a larger model tier for any lease that is longer than twenty pages of text.",
              "Raise the number of runs per lease to five and take the majority value for each field.",
              "Examples returning a value only with a supporting passage, else null."),
        ans=3,
        explain=("Examples that return a value only when a passage supports it, and null otherwise, teach the model to stay empty when the text is "
                 "silent. A shows only filled fields, so the model learns to always fill one. B and C add cost, while runs can agree on the same "
                 "unsupported value."),
        scenarios=(6,), points=("4.2:K4",),
        evidence=(Evidence("guide", ""),),
        community="guide only: the docs' quote-first technique is related but does not state the example design",
        qtype="choose", level="hard", principle="preserve_information",
        situation="notice periods that pass the schema but the lease text does not support",
        trap="examples of complete records, a bigger model or a majority vote",
    ),
    # ---- S1: targeted examples with reasoning ----
    MCQ(
        id="Q4.2-13",
        q=("A CI bot must choose between blocking a merge and leaving a comment when a single integration test fails. In about "
           "35% of ambiguous failures (one test, passed on the previous run) its choice changes between runs. You can write a "
           "small set of examples. Which design is best?"),
        opts=("A handful of past failures labelled block or comment, with no explanations.",
              "A few borderline failures, each with the action chosen and why it beat the other.",
              "One example per rule in the team's merge policy, written as a policy sentence each.",
              "A single long example that walks through the decision process of the policy in prose."),
        ans=1,
        explain=("Borderline cases with the reason for the choice show the trade-off the model must weigh. A gives answers without the "
                 "reasoning, so the model copies surface features. C restates the policy and adds no borderline cases. D is one case "
                 "in disguise and does not show the boundary."),
        scenarios=(5,), points=("4.2:S1",),
        evidence=(Evidence(BP, "Cover edge cases and vary enough that Claude doesn’t pick up unintended patterns."),),
        community="docs cover the edge-case principle; reasons in examples are the guide's judgment",
        qtype="choose", level="medium", principle="explicit",
        situation="single failing integration test blocks or comments depending on the run",
        trap="labels without reasons or policy sentences instead of borderline cases",
    ),
    MCQ(
        id="Q4.2-14",
        q=("A CI reviewer's verdict on the same finding flips between runs about 12% of the time. Comparing 200 flipped findings shows three "
           "borderline patterns (a retry around a non-idempotent call, a broad exception catch that re-raises, a TODO that cites a ticket) "
           "behind 70% of the flips. The prompt has room for only a few examples. Where should they go?"),
        opts=("On those three patterns, each with the right verdict and the reason.",
              "On the three most common finding types, with one clean example for each of them.",
              "On ten findings the reviewer already gets right every time, to anchor the style.",
              "On one example per review rule, so that every rule in the prompt is covered."),
        ans=0,
        explain=("Examples should be spent where the model is actually uncertain, and the comparison of flips points at those patterns. B and C "
                 "spend them on cases that already work. D spreads them thin over rules that mostly go right."),
        scenarios=(5,), points=("4.2:S1",),
        evidence=(Evidence(BP, "Cover edge cases and vary enough that Claude doesn’t pick up unintended patterns."),),
        community="docs cover the edge-case principle; where to spend few examples is the guide's judgment",
        qtype="evaluate", level="medium", principle="proportionate",
        situation="three borderline patterns behind 70% of flipped review verdicts",
        trap="spread examples over common types, easy cases or every rule",
    ),
    MCQ(
        id="Q4.2-15",
        q=("A CI reviewer was given examples with reasons for ignoring hard-coded values. One example said: \"Ignore this value, "
           "it is in the fixtures folder.\" Since then it has stopped reporting everything under `fixtures/`, including two real "
           "issues in code that builds a database URL there. What is the most likely cause?"),
        opts=("The reviewer took the folder named in the reason as the rule.",
              "The reviewer memorised that single example file and compares each file with it.",
              "Reasons in examples make the reviewer skip analysis, so they should be removed.",
              "The example sits too close to the end of the prompt and has the largest weight."),
        ans=0,
        explain=("A reason that points to a surface cue teaches the cue. A reason that names the property that decides, such as a "
                 "placeholder value used only by tests, carries over to other files. B would not cover the whole folder. C is wrong "
                 "because reasons are what make examples generalise. D invents a position effect that the stem gives no sign of."),
        scenarios=(5,), points=("4.2:S1", "4.2:K3"),
        evidence=(Evidence(BP, "Cover edge cases and vary enough that Claude doesn’t pick up unintended patterns."),),
        community="docs say examples can teach unintended patterns; the reason-wording judgment is the guide's",
        qtype="diagnose", level="hard", principle="root_cause",
        situation="reason cites the fixtures folder and the reviewer stops reporting that whole folder",
        trap="blame memorisation, removing reasons or the position of the example",
    ),
    # ---- S2: output layout ----
    MCQ(
        id="Q4.2-16",
        q=("Your CI comment bot files review findings by severity and accepts only the exact tokens high, medium or low. About 20% of "
           "findings arrive with other spellings such as Critical, sev-1 or HIGH!, so the bot drops them, and new spellings turn up every "
           "week. The prompt lists the allowed tokens in one sentence. What is the best change?"),
        opts=("Map every spelling the reviewer has produced so far to the three tokens, inside the bot.",
              "Examples in which each finding uses a different spelling, so the model sees every variant.",
              "Ask the reviewer to repeat the allowed tokens before each finding it writes.",
              "Examples in the same layout where severity is always exactly high, medium or low."),
        ans=3,
        explain=("Examples in the exact layout show the allowed tokens in use, which is what the one-sentence list did not achieve. A can never keep up with spellings that change weekly. B demonstrates the variation it should remove. C repeats the instruction that already fails."),
        scenarios=(5,), points=("4.2:S2", "4.2:K1"),
        evidence=(Evidence(BP, "Examples are one of the most reliable ways to steer Claude’s output format, tone, and structure."),),
        community="",
        qtype="fix", level="easy", principle="explicit",
        situation="severity arrives as Critical, sev-1 or HIGH! although the bot accepts three tokens",
        trap="map variants in code, show variant spellings or repeat the instruction",
    ),
    MCQ(
        id="Q4.2-17",
        q=("Developers ignore the \"suggested fix\" line of a CI reviewer: in a sample of 100 findings, 61 say \"consider refactoring this\" "
           "or similar, and developers want a change they can apply without rewriting it. The other three fields look good, and the prompt "
           "says that fixes must be actionable. Which change should be tried first?"),
        opts=("Require every suggested fix to be at least 30 words long in the output.",
              "Add examples whose fix field gives a concrete change, like the new line.",
              "Add examples whose fix field names the idea, such as \"use a context manager\".",
              "Remove the fix field and let developers decide how to resolve each issue."),
        ans=1,
        explain=("Examples convey the level of detail wanted more clearly than a description, so showing concrete fixes in the layout closes the gap. A rewards length and gives vague text more words. C shows fixes at the same vague level the team wants to leave. D drops a field the team wants."),
        scenarios=(5,), points=("4.2:S2",),
        evidence=(Evidence(BP, "Examples are one of the most reliable ways to steer Claude’s output format, tone, and structure."),),
        community="",
        qtype="diagnose", level="medium", principle="proportionate",
        situation="61 of 100 suggested fixes say consider refactoring",
        trap="minimum length, idea-level fixes in examples or dropping the field",
    ),
    MCQ(
        id="Q4.2-18",
        q=("A CI reviewer prompt asks for \"file, finding, priority, remedy\", while the three examples in it are written as "
           "\"Location / Issue / Severity / Fix\". Output labels now vary between runs: some use the instruction's names, some the "
           "examples' names, some a mix, and the comment bot expects one set. What is the most effective fix?"),
        opts=("Use one set of field names in both the instructions and every example.",
              "Add a parsing step that maps each variant of the names to the expected ones.",
              "Remove the examples so only the instruction's wording is left.",
              "Add more examples until the examples' naming outweighs the instruction."),
        ans=0,
        explain=("Two names for the same fields give the model two patterns to follow, and one set removes the conflict. B accepts the "
                 "variation and builds a mapping to hide it. C loses the examples that make the layout consistent. D piles on more "
                 "examples to fight a conflict that has a one-line fix."),
        scenarios=(5,), points=("4.2:S2", "4.2:K1"),
        evidence=(Evidence(BP, "Mirror your actual use case closely."),),
        qtype="diagnose", level="medium", principle="explicit",
        situation="instructions say file/finding/priority/remedy while examples use Location/Issue/Severity/Fix",
        trap="map the label variants in code, drop examples or add more of them",
    ),
    # ---- S3: acceptable patterns vs genuine issues ----
    MCQ(
        id="Q4.2-19",
        q=("After you added examples to a CI reviewer, it flags nearly every JavaScript pull request for unsafe input handling and almost "
           "none in Python. The examples hold six genuine issues, all in JavaScript, and six acceptable cases, all in Python; each has a "
           "reason naming the unsafe or safe property. Real issues in the repository occur in both languages. What is the most likely root "
           "cause?"),
        opts=("The examples sit before the rules in the prompt, so the rules override them.",
              "The model is simply stronger at finding input-handling problems in JavaScript.",
              "Language differs along with the verdict, so the reviewer uses it as the cue.",
              "The reasons in the examples make the reviewer skip analysis of the new code."),
        ans=2,
        explain=("When every genuine example is one language and every acceptable one another, the language becomes a shortcut. Pairing both verdicts in each language removes it. A has nothing in the stem to support a position effect. B does not explain near-zero findings in Python. D is wrong because the reasons name the property that should decide."),
        scenarios=(5,), points=("4.2:S3", "4.2:K3"),
        evidence=(Evidence(BP, "Cover edge cases and vary enough that Claude doesn’t pick up unintended patterns."),),
        community="",
        qtype="diagnose", level="medium", principle="root_cause",
        situation="every genuine example is JavaScript and every acceptable one is Python",
        trap="blame example order, language strength or the reasons",
    ),
    MCQ(
        id="Q4.2-20",
        q=("After the team added acceptable-versus-problem examples, a CI reviewer's false positives for logging calls fell from 22 "
           "a week to 6. One week later it passed a call that logs a full customer record, which resembles the acceptable "
           "example that logs only an order ID. What is the best adjustment?"),
        opts=("Delete the acceptable example, since it is the likely source of the missed case.",
              "Add a rule that logging calls must never be approved.",
              "Raise the severity of all logging findings so someone reviews them.",
              "Add a pair that differs only in what is logged, with the reason for each."),
        ans=3,
        explain=("A pair that differs only in the detail that matters shows the boundary, so the acceptable case stays acceptable and "
                 "the lookalike is caught. A brings back the 22 false positives. B undoes the false positive gain. C makes "
                 "people read every logging finding."),
        scenarios=(5,), points=("4.2:S3",),
        evidence=(Evidence(BP, "Cover edge cases and vary enough that Claude doesn’t pick up unintended patterns."),),
        community="",
        qtype="evaluate", level="hard", principle="explicit",
        situation="full customer record logged slips through after an order-ID-only example",
        trap="remove the example, forbid logging findings or just raise severity",
    ),
    MCQ(
        id="Q4.2-21",
        q=("You are writing one example for a CI reviewer that must separate a loop of database calls in a one-off migration script "
           "(acceptable) from the same loop on a web request path (a real issue). What should the example contain so the "
           "reviewer applies the idea to other scripts?"),
        opts=("The code, the verdict and the file path that decides the verdict in this case.",
              "The code, the verdict, and a sentence naming the property, such as runs only once.",
              "The code and the verdict, followed by the full text of the team's performance guideline.",
              "The verdict and the file path only, without the code that is being judged."),
        ans=1,
        explain=("The reason in terms of the deciding property transfers to scripts the examples never showed. A teaches a path rule. C "
                 "buries the point in a long document. D leaves out the code the model has to read."),
        scenarios=(5,), points=("4.2:S3",),
        evidence=(Evidence("api:agents-and-tools/agent-skills/best-practices", "Examples convey the desired style and level of detail to Claude more clearly than descriptions alone."),),
        qtype="configure", level="easy", principle="explicit",
        situation="loop of database calls in a one-off migration versus on a request path",
        trap="cite the path or paste the whole guideline instead of naming the deciding property",
    ),
    # ---- S4: varied document structures ----
    MCQ(
        id="Q4.2-22",
        q=("An invoice extractor has three examples, all taken from the largest customers' invoices. A breakdown of errors by layout shows "
           "tables with the total in a column at 3%, running text at 4%, and invoices that give the total in a footnote at 31%. Footnote "
           "invoices are about a fifth of volume. What is the most effective change?"),
        opts=("Add examples of footnote-style invoices showing where the total is.",
              "Add more invoices from the largest customers' layouts, to reinforce what already works.",
              "Detect the layout in code and use a different prompt for each layout.",
              "Instruct the model to look at the end of the document whenever the total is missing."),
        ans=0,
        explain=("The breakdown points at one structure that the examples never show, and an example of it is the targeted fix. B adds more of what already works. C adds detection code for a problem examples can handle. D describes the fix without demonstrating it."),
        scenarios=(6, 3), points=("4.2:S4",),
        evidence=(Evidence(BP, "Mirror your actual use case closely."),),
        community="",
        qtype="diagnose", level="medium", principle="root_cause",
        situation="total in a footnote gives 31% errors while tables and prose stay under 5%",
        trap="more of the same examples, per-layout prompts in code or a prose hint",
    ),
    MCQ(
        id="Q4.2-23",
        q=("A research assistant pulls the names and roles of executives from press releases (names in a quote block), annual "
           "reports (a table) and blog posts (names woven into prose). With a handful of slots for examples, which choice "
           "should work best?"),
        opts=("Three examples from press releases, since they are the most common source.",
              "Three examples of annual-report tables, as tables are the most structured format.",
              "One example per structure, each with a different layout of the same kind of fact.",
              "One example of a blog post, since prose is the hardest case and tables follow from it."),
        ans=2,
        explain=("Each source puts the same fact in a different place, so covering each structure shows the model what to look for in "
                 "all of them. A and B repeat a single structure. D assumes that skill on prose carries over to tables and quote "
                 "blocks, which the examples never show."),
        scenarios=(6, 3), points=("4.2:S4",),
        evidence=(Evidence(BP, "Cover edge cases and vary enough that Claude doesn’t pick up unintended patterns."),),
        qtype="choose", level="hard", principle="explicit",
        situation="executive names found in a quote block, a table or woven into blog prose",
        trap="all examples from the most common source or the hardest one",
    ),
    MCQ(
        id="Q4.2-24",
        q=("Market reports state a figure twice: as a rounded number in the summary at the top (\"about 2,000 units\") and as an exact one "
           "in a detail table lower down (\"2,114\"). The team's policy is that the table is authoritative, but the extractor returns the "
           "summary figure in about a third of runs. How should this be fixed?"),
        opts=("Tell the extractor to prefer larger numbers, since the table figure is more precise.",
              "Cut the summary from each report before extraction, since the table has the detail.",
              "Add several examples of reports that have a summary and no detail table at all.",
              "Say the table overrides the summary, with one example where they differ."),
        ans=3,
        explain=("A stated precedence plus one example where the two differ settles the choice and shows the reason. A rewards a number's size instead of its source. B fails when the summary holds facts the table lacks. C shows only cases with no conflict."),
        scenarios=(6,), points=("4.2:S4", "4.2:K2"),
        evidence=(Evidence("guide", ""),),
        community="guide-only: precedence instruction plus an example of conflicting sections",
        qtype="fix", level="hard", principle="explicit",
        situation="summary says about 2,000 while the detail table says 2,114",
        trap="prefer bigger numbers, cut the summary or show only conflict-free reports",
    ),
    # ---- S5: varied formats and null extraction ----
    MCQ(
        id="Q4.2-25",
        q=("A required `invoice_number` comes back empty for 14% of invoices. The affected ones label the value \"Ref: INV/2024/118\", \"No. 118\" or \"Document no.\", while invoices headed \"Invoice #\" extract well. The prompt asks for the invoice number and its examples all use \"Invoice #\". What is the best fix?"),
        opts=("Make `invoice_number` optional so that those invoices stop failing validation.",
              "Examples where Ref, No. and Document no. labels all give the invoice number.",
              "Examples that keep the Invoice # label but vary how the number itself is formatted.",
              "A second model call that asks whether the invoice carries a number at all."),
        ans=1,
        explain=("The examples teach the other labels, so the field is filled instead of left empty. A hides the failure and the data is still missing. C varies the number's format, which is not what differs in the failing invoices. D repeats the same model's misreading."),
        scenarios=(6,), points=("4.2:S5",),
        evidence=(Evidence(BP, "Mirror your actual use case closely."),),
        community="",
        qtype="diagnose", level="easy", principle="root_cause",
        situation="invoice number empty when labelled Ref, No. or Document no.",
        trap="make the field optional, vary the wrong axis, ask again",
    ),
    MCQ(
        id="Q4.2-26",
        q=("A required `order_date` comes back empty on 11% of orders. Every affected order labels it in German or French (Bestelldatum, "
           "Date de commande), while English-labelled orders extract well. The prompt's examples show English labels with eight different "
           "date notations. What is the best fix?"),
        opts=("Examples in which German and French labels each yield the order date.",
              "More English examples with additional date notations, since dates are the weak point.",
              "Translate every document into English before extraction runs.",
              "Make `order_date` optional so those orders stop failing validation."),
        ans=0,
        explain=("The failing orders differ in the label language, so examples in those languages show the model where the date sits. B varies notation, which is not what differs. C adds a lossy step for a problem the examples can handle. D hides the gap while the dates stay missing."),
        scenarios=(6,), points=("4.2:S5",),
        evidence=(Evidence(BP, "Cover edge cases and vary enough that Claude doesn’t pick up unintended patterns."),),
        community="",
        qtype="fix", level="medium", principle="root_cause",
        situation="order date empty when the label is German or French",
        trap="vary date notation, translate first or make the field optional",
    ),
    MCQ(
        id="Q4.2-27",
        q=("Delivery notes arrive as text exported from a two-column PDF, where each label sits on one line and its value on the next. "
           "`delivery_date` is empty on 17% of them, though the dates are plainly present. The examples show \"Date: 12 May\" on a single "
           "line, and a prompt line saying that values may be on the next line was added last week and changed little. What is the best fix?"),
        opts=("Re-export the PDFs with a different tool so that labels and values share a line.",
              "Add examples of the single-line layout with many more date notations.",
              "Add examples in the flattened two-line layout, with the date on the value line.",
              "Move the hint to the end of the prompt and repeat it in capitals."),
        ans=2,
        explain=("Examples in the same layout as the failing inputs show where the value sits. A rebuilds the input side, which may not be possible for every sender. B varies notation, not layout. D repeats a hint that has already been tried."),
        scenarios=(6,), points=("4.2:S5",),
        evidence=(Evidence(BP, "Mirror your actual use case closely."),),
        community="",
        qtype="fix", level="easy", principle="explicit",
        situation="label and value on separate lines in flattened two-column text",
        trap="re-export the input, vary the wrong axis or repeat the hint",
    ),
)
