"""Exam bank · TS 4.4. Original questions; see docs/MCQ_BANK_PLAN.md."""
from utils.mcq_sets import MCQ, Evidence

TS = "4.4"
BULLETS = {
    "K1": "Retry with error feedback: append the specific validation errors to the prompt so the model can correct itself",
    "K2": "The limits of retry: it cannot help when the needed information is absent from the source, unlike format or structural errors",
    "K3": "Feedback loop design: a detected_pattern field shows which code constructs trigger findings, so dismissals can be analysed",
    "K4": "Semantic validation errors (values do not add up, wrong field) differ from schema syntax errors, which tool use removes",
    "S1": "Follow-up requests that carry the original document, the failed extraction and the specific validation errors",
    "S2": "Telling when a retry will fail (information only in a document not provided) from when it will work (format, structure)",
    "S3": "Adding detected_pattern to structured findings to study false-positive patterns when developers dismiss them",
    "S4": "Self-correction flows: calculated_total beside stated_total, and conflict_detected booleans for inconsistent sources",
}

QUESTIONS = (
    # ---- K1: retry with error feedback ----
    MCQ(
        id="Q4.4-01",
        q=("Your CI reviewer returns a JSON list of 10 to 25 findings per pull request. A validator checks each finding and, in "
           "about 6% of runs, rejects one or two, for example because the cited line lies outside the diff. The retry appends "
           "the line \"Your previous output was invalid. Try again.\" to a conversation that already holds the diff and the "
           "earlier output, and only 30% of retries pass. What should the retry message contain instead?"),
        opts=("A reminder of the full schema, listing every field name, type and allowed value once more for the model.",
              "The same line as before, but sent up to five times, because every attempt starts from a fresh sample.",
              "The failing finding and the rule it broke, such as finding 7 citing line 412 when the diff ends at 188.",
              "A request to explain why the output was invalid, followed by a corrected list of all of the findings."),
        ans=2,
        explain=("The model can only repair what it is told about, and the validator knows which finding failed and why. A repeats "
                 "a schema that the output already satisfied, since the failure is about a value. B sends no new information, so "
                 "more attempts mostly repeat the same miss. D asks the model to work out the failure for itself, without the "
                 "validator's findings."),
        scenarios=(5,), points=("4.4:K1",),
        evidence=(Evidence("api:agents-and-tools/tool-use/handle-tool-calls", "include what went wrong and what Claude should try next"),),
        qtype="configure", level="medium", principle="explicit",
        situation="generic invalid-output line after 6% of review runs have a finding rejected",
        trap="resend a generic try-again line",
    ),
    MCQ(
        id="Q4.4-02",
        q=("A lease-extraction pipeline runs seven code checks on each output: dates in order, rent positive, deposit within three "
           "months of rent, and so on. The validator returns a single message, the first check that fails, and the pipeline "
           "appends it to the correction request, with a limit of three attempts. Leases can break up to six checks at once. "
           "45% of such leases still fail after the third attempt, and the logs show a different check failing each time. "
           "What is the most effective fix?"),
        opts=("Run all seven checks, then append every failure to the same correction request.",
              "Raise the limit to six attempts, so that every failing check gets a correction round of its own.",
              "Order the checks by how often they fail, so that the likeliest error is corrected first.",
              "Send each failing check as a separate request, then merge the corrected fields afterwards."),
        ans=0,
        explain=("With every error in one request the model can fix all of them in a single pass. B costs up to six calls on the "
                 "whole document and still corrects one problem per call. C changes the order but leaves one error per round. "
                 "D splits the work across calls, so corrected fields can contradict each other, for example two dates."),
        scenarios=(6,), points=("4.4:K1",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 4.4 Knowledge 1 and Skill 1 say to send the specific errors; no official page speaks to reporting every failed check at once.",
        qtype="fix", level="medium", principle="explicit",
        situation="validator hands back only the first failed check of seven",
        trap="raise the attempt limit",
    ),
    MCQ(
        id="Q4.4-03",
        q=("Your pipeline extracts names, dates and test results from lab reports. A code check flags results whose unit does not "
           "match the test type, in about 5% of reports. To correct them, the team asks the model \"What did you get wrong?\" and "
           "feeds its answer back with the report. For 4 in 10 corrected reports the answer names a different field from the one "
           "the check flagged, and the unit stays wrong. Which design is best?"),
        opts=("Ask the model to rate its confidence in each field, and retry only the fields it rates below 0.8 on the scale.",
              "Give the explanation step to a larger model, because the current one is placing the mistake in the wrong field.",
              "Ask for two separate explanations of the error, and keep the one that both of them point to as the cause.",
              "Feed back the check's own result: the flagged field, the unit found and the units that are allowed."),
        ans=3,
        explain=("The code already knows what failed, so its result is a more reliable correction signal than the model's account of "
                 "its own mistake. A uses self-reported confidence, which is not evidence. B assumes a bigger model would be a better "
                 "witness, which it need not be. C compares two self-explanations, and agreement between them is still the model's "
                 "opinion."),
        scenarios=(6,), points=("4.4:K1",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 4.4 Knowledge 1 says to append specific validation errors; no official page compares code errors with model self-explanations.",
        qtype="choose", level="medium", principle="independent_check",
        situation="model's own account of its mistake fed back instead of the check result",
        trap="ask the model what went wrong",
    ),
    # ---- K2: limits of retry ----
    MCQ(
        id="Q4.4-04",
        q=("An insurer's pipeline extracts claim forms and requires policy_number. Format slips, such as a missing prefix, are fixed "
           "by one retry in 95% of cases. For 9% of forms the field stays wrong, and the logs show a different 10-digit number in "
           "each retried output. Those forms say only \"see policy schedule\", and the pipeline sends the model nothing but the "
           "claim form. What is the most likely reason retries cannot fix these forms?"),
        opts=("The correction messages are long, so the model overlooks the field in the retried prompt.",
              "The number is nowhere in what the model receives, so each attempt can only guess a value.",
              "Three attempts is too few for such a field, so the limit should be raised to ten attempts.",
              "The model has not seen enough forms to learn how this insurer lays out its numbers."),
        ans=1,
        explain=("A retry helps when the model has the information and mis-shapes it, which is why format slips are fixed. Here the "
                 "value lives in a file the model never sees, and the changing numbers show guessing. A has no support in the logs, "
                 "which show the field changing every time. C adds guesses to the same loop. D treats a missing input as a layout "
                 "problem."),
        scenarios=(6,), points=("4.4:K2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 4.4 Knowledge 2 says retries cannot supply information absent from the source; no official page addresses retry futility.",
        qtype="diagnose", level="easy", principle="root_cause",
        situation="claim form points to a policy schedule file the model never gets",
        trap="raise the retry limit",
    ),
    MCQ(
        id="Q4.4-06",
        q=("A mortgage-document pipeline retries failed extractions with the specific errors appended. Across 40,000 packets the "
           "success rates are: first pass 88%, after one retry 96.5%, after two 97.2%, after three 97.3%. The packets still failing "
           "show the same error on every attempt, and each retry is a full call on a 60-page document. A manager asks whether to "
           "raise the limit from three to eight to reach the remaining 2.7%. How should you evaluate this?"),
        opts=("Lower the cap to one or two retries and send what remains to review, as later attempts add very little.",
              "Raise it to eight, since the cost of a few extra calls is likely lower than the cost of a manual review.",
              "Keep three, but run the last retry on a larger model so that it can resolve the hardest packets.",
              "Remove retries and send all of the 12% of first-pass failures to review, which keeps the process predictable."),
        ans=0,
        explain=("Most of the benefit comes from the first retry, and failures that repeat the same error across attempts are not the "
                 "kind a retry repairs, so extra rounds add cost for little gain. B assumes more attempts will change those results. "
                 "C expects a larger model to supply what is not in the input. D gives up the 8.5 points the first retry recovers."),
        scenarios=(6,), points=("4.4:K2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the guide says retries fail when information is absent; where to cap a retry loop is a cost judgment no official page makes.",
        qtype="evaluate", level="hard", principle="proportionate",
        situation="success curve flattens after one retry while failures repeat the same error",
        trap="raise the limit to eight",
    ),
    MCQ(
        id="Q4.4-17",
        q=("The team rewrote the criteria for `optional-chaining-suggestion`. In the next two weeks its dismissal rate fell from 85% "
           "to 20%, and the number of findings raised with that pattern fell by 90%. A manager calls the rewrite a success. "
           "How should you evaluate the result?"),
        opts=("Accept it: the dismissal rate fell from 85% to 20%, which was the aim of the rewrite.",
              "Roll back the rewrite, because a 90% fall in volume proves that the new criteria are broken.",
              "Check a sample of code from before the rewrite, to see whether real issues are no longer raised.",
              "Compare the dismissal rates of the other patterns, to see whether they moved along with this one."),
        ans=2,
        explain=("A falling dismissal rate is only good if the findings that disappeared were the false ones, and only a sample of "
                 "the code can show that. A reads the rate alone. B overreacts, since removing false positives would cut volume "
                 "as well. D checks other patterns, which cannot show what this rewrite stopped raising."),
        scenarios=(5,), points=("4.4:K3", "4.4:S3"),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the guide says dismissals reveal false-positive patterns; checking that a fix did not hide real issues is design judgment.",
        qtype="evaluate", level="hard", principle="independent_check",
        situation="dismissal rate and volume both fall after a criteria rewrite",
        trap="read the lower dismissal rate as proof of success",
    ),
    MCQ(
        id="Q4.4-07",
        q=("About 38 in every 100 findings from your CI reviewer are dismissed by developers. Each finding carries file, line, "
           "severity, category (bug, security or style) and message. Dismissal rates look alike in every category and at every severity, and the team has no way to see "
           "what sort of code produces the unwanted ones. One review rule can fire on very different code. Which addition lets them find out most directly?"),
        opts=("A confidence score between 0 and 1 on every finding, so that low-scoring ones can be examined first.",
              "A reviewer note on every dismissal, so that each developer explains in a line why it was dismissed.",
              "A detected_pattern field naming the code construct that triggered each finding.",
              "A rule_id field naming the review rule that fired, so that dismissals can be counted per rule."),
        ans=2,
        explain=("Recording the construct on each finding lets dismissals be grouped by what triggered them. A is the model's own "
                 "rating, and says nothing about constructs. B produces free text after the fact, one note at a time, with no "
                 "common grouping. D counts per rule, but one rule fires on very different code, so the constructs stay hidden."),
        scenarios=(5,), points=("4.4:K3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 4.4 Knowledge 3 names the detected_pattern field; no official page discusses dismissal analysis.",
        qtype="choose", level="easy", principle="fit_for_purpose",
        situation="38% dismissals look the same across category and severity",
        trap="add a confidence score",
    ),
    MCQ(
        id="Q4.4-08",
        q=("Your CI reviewer emits detected_pattern from a fixed list of 25 names plus 'other' with a detail field. After six weeks, "
           "34% of the 6,000 findings are labelled 'other', so the dismissal analysis says little about a third of the findings. "
           "What is the most effective next step?"),
        opts=("Remove 'other', so that every finding has to pick a listed pattern and the labels stay consistent.",
              "Count the detail text under 'other', and add the most frequent constructs to the list.",
              "Leave the list as it is, since a large 'other' group shows that the reviewer raises unusual code.",
              "Replace the list with free-text labels, so that no finding is ever forced into 'other'."),
        ans=1,
        explain=("The detail values show which constructs the list is missing, so promoting the frequent ones makes the next "
                 "analysis cover them. A forces findings into the wrong patterns and corrupts the counts. C accepts a third of "
                 "the data as unanalysable. D brings back labels that vary from finding to finding."),
        scenarios=(5,), points=("4.4:K3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the guide names detected_pattern and, in TS 4.3, 'other' plus a detail field; no official page covers maintaining the list.",
        qtype="fix", level="medium", principle="fit_for_purpose",
        situation="34% of findings land in 'other' so pattern analysis misses a third of them",
        trap="remove 'other' to force consistent labels",
    ),
    MCQ(
        id="Q4.4-10",
        q=("A team moves its purchase-order extractor to a strict tool schema. JSON parse failures fall from 3% to zero, so an "
           "engineer proposes deleting the validation and retry layer. That layer also checks that line totals add up to the order "
           "total and that quantity and unit price are not swapped. A sample of 500 orders contains 14 whose total does not add up. "
           "How should you evaluate the proposal?"),
        opts=("Keep the semantic checks and retries: a schema removes syntax failures, not wrong values.",
              "Delete the layer, since zero parse failures show that the extracted values are now correct.",
              "Delete the layer, and audit a sample of 50 orders by hand each night to find bad totals.",
              "Replace it with a stricter schema that requires each order's total to equal the sum of its lines."),
        ans=0,
        explain=("The schema guarantees valid structure and types, but a total that does not add up is a valid number in the wrong "
                 "place. B treats a syntax result as proof of correctness. C finds bad totals a day late and by hand, though a check "
                 "can find them on every order. D asks the schema to express arithmetic across fields, which it cannot."),
        scenarios=(6,), points=("4.4:K4",),
        evidence=(Evidence("api:build-with-claude/structured-outputs", "No retries needed for schema violations"),),
        qtype="evaluate", level="easy", principle="fit_for_purpose",
        situation="proposal to delete the check layer after switching to a strict schema",
        trap="read zero parse failures as correct output",
    ),
    MCQ(
        id="Q4.4-11",
        q=("A freight pipeline extracts ship_date and delivery_date from bills of lading. Both are required ISO date strings, and "
           "every output passes the schema. In 3% of documents the model puts the delivery date into ship_date and the booking "
           "date into delivery_date, so deliveries appear to happen before shipping. Which check catches this?"),
        opts=("Add a date format and a date pattern to both fields, so only real calendar dates are accepted.",
              "Mark both fields as required and forbid extra properties, so that a shifted value cannot appear.",
              "A code check that rejects a delivery_date earlier than ship_date and returns the error to the model.",
              "A line in the prompt asking the model to confirm that each date is in the right field before it answers."),
        ans=2,
        explain=("Wrong-field placement is a semantic error, and a rule that compares the two fields can detect it, then feed the "
                 "specific error to a retry. A and B tighten syntax, which every swapped output already satisfies. D asks the "
                 "model to catch its own slip, which is the behaviour that failed."),
        scenarios=(6,), points=("4.4:K4",),
        evidence=(Evidence("api:build-with-claude/structured-outputs", "Guaranteed field types and required fields"),),
        qtype="configure", level="medium", principle="deterministic",
        situation="ship and delivery dates swapped but both valid ISO strings",
        trap="tighten the date format in the schema",
    ),
    MCQ(
        id="Q4.4-12",
        q=("Your CI reviewer returns findings through a strict tool schema where `line` is an integer. Parsing has not failed in "
           "two months, yet developers report that on large diffs about one finding in five points 10 to 40 lines away from the "
           "code it describes. All the numbers are valid integers inside the file's length, and the API does not enforce `minimum` or `maximum` on that field. What is the best fix?"),
        opts=("Add a minimum and a maximum to `line`, so that the number must fall inside the file's length.",
              "Add a code_snippet field, verify it against the cited line in code, and send mismatches back.",
              "Tell the model in the prompt to count lines carefully before it writes each number in a finding.",
              "Move to a model with a bigger context window, since long diffs are not being read reliably."),
        ans=1,
        explain=("The numbers are valid and wrong, a semantic error that a check against the file can find and turn into a specific "
                 "message for a retry. A would not exclude them, since the stem says they are already inside the file. C asks for "
                 "care without any means to tell when it failed. D assumes a reading limit that the evidence does not show."),
        scenarios=(5,), points=("4.4:K4",),
        evidence=(Evidence("api:build-with-claude/structured-outputs", "Structured outputs guarantee schema-compliant responses through constrained decoding"),
                  Evidence("api:build-with-claude/structured-outputs", "stripped from the wire schema, appended to the description, and validated against the response")),
        qtype="diagnose", level="hard", principle="deterministic",
        situation="valid but misplaced line numbers in review findings on large diffs",
        trap="bound the integer in the schema",
    ),
    # ---- S1: follow-up requests ----
    MCQ(
        id="Q4.4-13",
        q=("An invoice pipeline retries a failed extraction by sending the invoice again plus the validator's message, for example "
           "\"due_date is earlier than issue_date\". The flagged field is fixed in 90% of retries, but 12% of retried outputs now "
           "hold a wrong value in a field that was right the first time, usually in the line items. Which change most directly "
           "removes the new errors?"),
        opts=("Include the earlier extraction in the follow-up, so that the model edits it, not restarts.",
              "Add 'change only the flagged field' to the retry prompt, and leave everything else exactly as it is.",
              "Run the retry at temperature 0, so that unchanged fields come back identical every time.",
              "Run two retries and keep each field's value only where both retries gave the same answer."),
        ans=0,
        explain=("With the earlier output in front of it, the model can correct the one field and keep the rest. B gives an "
                 "instruction with nothing to preserve, since the request carries no earlier values. C lowers randomness but a "
                 "fresh extraction can still differ. D doubles the calls and still starts each retry from nothing."),
        scenarios=(6,), points=("4.4:S1",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 4.4 Skill 1 says the follow-up carries the failed extraction; no official page describes the regression when it is left out.",
        qtype="diagnose", level="medium", principle="preserve_information",
        situation="retry without the earlier output breaks fields that were right",
        trap="instruct the model to change only the flagged field",
    ),
    MCQ(
        id="Q4.4-14",
        q=("To save tokens on 90-page contracts, a retry sends the model only its failed JSON and the check message "
           "\"effective_date is after expiry_date\". The new output passes the check every time, but an audit against the PDFs "
           "finds that 35% of the retried dates differ from the contract. What is the most likely root cause?"),
        opts=("The message gives the rule but no example of a correct date, so the model picks one at random.",
              "A correction needs two rounds to settle on the right values, and only one round was allowed.",
              "With no contract in the request, the model rearranged values until the check passed.",
              "The message names the wrong field, so the model edits a date that was correct."),
        ans=2,
        explain=("The model has nothing to read the true dates from, so it can only satisfy the rule. A and B would not make "
                 "passing outputs wrong at this rate: an example date is no evidence about this contract, and a second round "
                 "would have the same inputs. D contradicts the stem, where the message names both dates involved."),
        scenarios=(6,), points=("4.4:S1",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 4.4 Skill 1 says the follow-up carries the original document; no official page describes what happens when it is left out.",
        qtype="diagnose", level="medium", principle="explicit",
        situation="retry on long contracts omits the document and bends dates to pass",
        trap="blame the wording or number of correction rounds",
    ),
    MCQ(
        id="Q4.4-15",
        q=("A validator finds that 2 of your CI reviewer's 19 findings cite files the pull request does not touch. You now build the "
           "follow-up request for self-correction, and the model has to be able to see what the pull request actually changed. "
           "Which contents should it carry?"),
        opts=("The two bad findings and the validator's messages, since the other 17 findings are already correct.",
              "The diff and an instruction to produce all of the findings again, noting that some were invalid.",
              "The diff and the validator's messages, because the earlier findings could anchor the model on its mistakes.",
              "The diff, the full 19-finding output and the validator's messages for the two failures."),
        ans=3,
        explain=("The model needs the source to check against, its earlier output to correct, and the specific errors. A leaves out "
                 "the diff, so there is nothing to check file names against. B omits the output and the errors, so the 17 good "
                 "findings may change. C omits the output, so the model must rebuild all 19 findings with no sign of which "
                 "two were wrong."),
        scenarios=(5,), points=("4.4:S1",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 4.4 Skill 1 names the three parts of a follow-up request; no official page lists them.",
        qtype="configure", level="easy", principle="explicit",
        situation="follow-up for 2 of 19 findings that cite files outside the pull request",
        trap="send only the bad findings, or only the diff",
    ),
    # ---- S2: when retries work ----
    MCQ(
        id="Q4.4-05",
        q=("Your invoice pipeline extracts stated_total as printed and calculated_total from the lines, and on a mismatch it "
           "retries with the specific discrepancy appended. After the change 70% of retried pairs agree, yet an audit against "
           "the PDFs finds that in most of those the retry rewrote stated_total to equal the sum of the lines, while the "
           "document prints a different figure. What is the most effective fix?"),
        opts=("Retry again with the size of the discrepancy in the message, so that a specific error leads to a correct total.",
              "Lock stated_total in the schema, so that on a retry the model can only change calculated_total.",
              "Add a second extraction pass with a different prompt, and keep the total on which both passes agree.",
              "Stop retrying a flagged pair, keep both figures as printed, set a discrepancy flag and send it to review."),
        ans=3,
        explain=("The invoice itself contradicts its lines, so no retry can produce a right answer, and one that makes the figures "
                 "agree has altered the transcription. A repeats the loop that caused the rewrite. B relies on a schema locking "
                 "feature that does not exist. C compares two passes that can both be pulled toward the sum of the lines."),
        scenarios=(6,), points=("4.4:S4", "4.4:S2"),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 4.4 Skill 4 names calculated_total beside stated_total and Skill 2 limits retries; no official page covers a source that contradicts itself.",
        qtype="diagnose", level="medium", principle="preserve_information",
        situation="retry rewrites the printed total so that it agrees with the line sum",
        trap="retry again with the discrepancy size",
    ),
    MCQ(
        id="Q4.4-16",
        q=("Last week 1,000 customs-form extractions failed validation. By error: 560 have dates written as \"31.12.2025\" where "
           "ISO is required, 240 put the gross weight into the net_weight field, and 200 have an empty exporter_license_no because "
           "the licence is on a separate permit that was not part of the submission. You must decide what each group gets. What is "
           "the best policy?"),
        opts=("Retry all three groups with the errors appended, up to three attempts each, then review what still fails.",
              "Retry the date and weight groups with their errors, and mark the licence group null with a flag.",
              "Retry only the date group, because weight mix-ups are meaning errors that a retry cannot correct.",
              "Retry the weight and licence groups with their errors, and convert the dates with a pattern in code."),
        ans=1,
        explain=("Format and structural errors are the kind a retry corrects, while the licence number cannot be produced from "
                 "documents that do not contain it. A spends three attempts per form on the 200 that cannot succeed. C treats a "
                 "wrong-field error as beyond repair, though the model has the weight. D retries the one group that cannot be "
                 "fixed."),
        scenarios=(6,), points=("4.4:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 4.4 Skill 2 contrasts external-document gaps with format and structural errors; no official page grades retry candidates.",
        qtype="choose", level="hard", principle="proportionate",
        situation="1,000 customs failures split by date format, wrong field and absent permit",
        trap="retry every group the same way",
    ),
    MCQ(
        id="Q4.4-18",
        q=("A pipeline converts PDFs to text and sends the text to the model. 7% of mortgage packets fail the check that "
           "signature_date must be present, and every retry with the error appended fails the same way. A reviewer opens a failed "
           "packet and finds the signature page is page 14. The converter's log for those packets shows \"pages processed: 10\". "
           "What is the most effective fix?"),
        opts=("Raise the converter's page limit so the signature page is sent, then re-run those packets.",
              "Add worked examples of signature blocks to the prompt, so the model finds them more reliably.",
              "Raise the retry limit from three to six for the packets that still fail the signature check.",
              "Make signature_date nullable, so that these packets pass the check without a date."),
        ans=0,
        explain=("The date is in the document but not in what the model is given, so no retry can find it, and the converter has "
                 "to supply it. B would help a model that can see a signature block, and this one cannot. C repeats a loop that "
                 "has failed identically. D hides a fixable data loss instead of correcting it."),
        scenarios=(6,), points=("4.4:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 4.4 Skill 2 contrasts information that is not provided with format errors; no official page addresses retry futility.",
        qtype="diagnose", level="hard", principle="root_cause",
        situation="converter stops at page 10 so a page-14 signature date is never seen",
        trap="raise the retry limit for the failing packets",
    ),
    # ---- S3: detected_pattern analysis ----
    MCQ(
        id="Q4.4-09",
        q=("After six weeks the dashboard groups 2,100 dismissed findings by detected_pattern. `optional-chaining-suggestion` "
           "accounts for 41% of all dismissals and is dismissed 85% of the times it is raised. `sql-string-concat` was raised 190 "
           "times and dismissed 4% of the time. The team has time for one change this sprint. What is the best use of the data?"),
        opts=("Hide every finding that falls below a given confidence score, until overall dismissals drop under 20%.",
              "Ask developers to leave a reason on each dismissal, then read the reasons next quarter.",
              "Hide both patterns until the reviewer is retrained, since each ranks near the top of the list.",
              "Rewrite the criteria for the optional-chaining pattern with skip examples, then measure it again."),
        ans=3,
        explain=("The data points at one pattern that developers reject nearly every time, so it is the one to fix, and a "
                 "re-measure shows whether the change worked. A applies a self-reported score to all patterns, including the accurate "
                 "ones. B delays any action and gathers text, when the pattern counts already show where the problem is. C also "
                 "hides sql-string-concat, which developers act on 96% of the time."),
        scenarios=(5,), points=("4.4:S3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 4.4 Skill 3 describes analysing false-positive patterns from dismissals; no official page covers this loop.",
        qtype="evaluate", level="medium", principle="proportionate",
        situation="one pattern is 85% dismissed while another is 4% dismissed",
        trap="hide findings by confidence score across the board",
    ),
    MCQ(
        id="Q4.4-19",
        q=("The weekly report ranks detected_pattern values by dismissal rate: `rare-regex-backtracking` 5 of 6 dismissed (83%), "
           "`unchecked-array-index` 280 of 400 (70%), and `hardcoded-credential` 3 of 90 (3%). The team has time to retune the "
           "criteria for one pattern this sprint. Which should it choose?"),
        opts=("`rare-regex-backtracking`, since it has the highest dismissal rate of the three patterns.",
              "`hardcoded-credential`, since a pattern that few people act on needs the most careful review.",
              "All three patterns, because a dismissal rate is only useful when each pattern is retuned together.",
              "`unchecked-array-index`, since 400 findings back its rate and it wastes the most reviews."),
        ans=3,
        explain=("A pattern with 400 findings and 70% dismissed is a reliable signal and the largest cost to developers. A rests on "
                 "six findings, too few to say anything. B has it backwards, since 3% dismissed means developers act on it. C "
                 "spreads one sprint over patterns that do not all need work."),
        scenarios=(5,), points=("4.4:S3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the guide says to analyse false-positive patterns from dismissals; weighing sample size is analysis judgment.",
        qtype="choose", level="medium", principle="proportionate",
        situation="83% dismissal on 6 findings versus 70% on 400",
        trap="pick the highest dismissal rate regardless of sample size",
    ),
    MCQ(
        id="Q4.4-20",
        q=("The pattern analysis shows `missing-error-handling` dismissed 62% of 480 times, and the team plans to rewrite its "
           "criteria to cut that. A lead notes that about 90% of those dismissals came from two services during a release freeze, and "
           "that elsewhere the pattern is dismissed 20% of the time. How should you evaluate the plan?"),
        opts=("Proceed, since a 62% dismissal rate is above any acceptable level whatever the source of the dismissals.",
              "Hold it, and sample the freeze-period dismissals to see whether they were false positives or deferrals.",
              "Proceed, but only for the two services, since they produce most of the dismissals.",
              "Hold it, drop the freeze-period dismissals from the data, and treat the 20% rate as the true one."),
        ans=1,
        explain=("A dismissal is a signal, not proof of a false positive, so the freeze-period dismissals need checking before they "
                 "drive a rewrite. A takes every dismissal as an error. C keeps the unverified assumption and narrows the scope. "
                 "D discards data on a guess, and the 20% may itself include deferrals."),
        scenarios=(5,), points=("4.4:S3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the guide says dismissals reveal false-positive patterns; whether every dismissal is a false positive is a judgment call.",
        qtype="evaluate", level="hard", principle="independent_check",
        situation="a 62% dismissal rate concentrated in two services during a release freeze",
        trap="treat every dismissal as a false positive",
    ),
    # ---- S4: calculated_total, stated_total, conflict_detected ----
    MCQ(
        id="Q4.4-21",
        q=("Rate confirmations list base freight, a fuel surcharge and accessorial lines, and print a total at the bottom. Your "
           "pipeline stores the printed total. A quarterly audit found that 2.4% of confirmations print a total that differs from "
           "the sum of their lines, and carriers were overpaid. Which schema change best lets the pipeline catch this?"),
        opts=("Replace the printed total with the model's own sum, since the lines are what the carrier is owed.",
              "Add a total_confidence field, and send low-confidence totals to review.",
              "Extract calculated_total from the lines next to stated_total, and flag every pair that differs.",
              "Make total required and non-null, so that the model returns a number for every confirmation."),
        ans=2,
        explain=("Holding both figures makes a disagreement visible, whichever figure is wrong. A drops the printed total, so the "
                 "document's own error is never flagged. B uses the model's self-rating, which does not detect arithmetic. D "
                 "forces a value to appear but does not check it."),
        scenarios=(6,), points=("4.4:S4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: calculated_total beside stated_total is named in TS 4.4 Skill 4; no official page covers the pattern.",
        qtype="choose", level="easy", principle="preserve_information",
        situation="printed total on rate confirmations disagrees with the sum of the lines",
        trap="replace the printed total by the model's own sum",
    ),
    MCQ(
        id="Q4.4-22",
        q=("Permit applications state the applicant's date of birth in the form header and again in an attached ID scan, and about "
           "3% show two different dates. The pipeline asks for one date_of_birth, and the model silently takes the header's. "
           "Eligibility depends on age, wrong approvals have occurred, and reviewers need to see both values to decide. A null date skips the age rule, and "
           "no queue routes nulls to a person. What is the best change?"),
        opts=("Extract both dates, set conflict_detected when they differ, and route those cases to review.",
              "Take the later of the two dates, since a correction is usually entered after the original.",
              "Take the ID scan's date, since an official document outranks a form field.",
              "Return null for date_of_birth whenever the two differ, and let the eligibility check reject nulls."),
        ans=0,
        explain=("The flag turns an inconsistent source into a visible case, with both values kept for the reviewer. B and C choose "
                 "a value by a rule nobody has agreed, so a wrong date still enters the record silently. D loses both values "
                 "and gives the reviewer no reason for the rejection."),
        scenarios=(6,), points=("4.4:S4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: conflict_detected is named in TS 4.4 Skill 4; no official page covers inconsistent-source handling.",
        qtype="fix", level="medium", principle="preserve_information",
        situation="header and ID scan give two dates of birth and the model silently picks one",
        trap="pick one by a guessed precedence rule",
    ),
    MCQ(
        id="Q4.4-23",
        q=("Your pipeline extracts calculated_total and stated_total from supplier invoices and flags any pair that differs. Since "
           "launch, 18% of invoices are flagged, and reviewers find that most flagged invoices are correct. The prompt describes "
           "calculated_total as \"the total of the invoice\", and the flagged pairs typically differ by the tax amount. What is "
           "the most effective fix?"),
        opts=("Lower the review priority of flagged invoices, since most of them turn out to be correct.",
              "Define calculated_total as the line items plus the tax lines shown, and compare with a small tolerance.",
              "Drop calculated_total and trust the stated total, since the printed figure is what the supplier will be paid.",
              "Add a tax_total field and ask the model to say which of the two totals it trusts more."),
        ans=1,
        explain=("The two fields measure different things, so differences are produced by the definitions and not by errors in the "
                 "invoices. A leaves the noise in place and risks hiding the real mismatches. C removes the check that the design "
                 "exists for. D relies on a self-reported preference instead of comparing like with like."),
        scenarios=(6,), points=("4.4:S4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the guide names calculated_total and stated_total; how to define them so they compare cleanly is design judgment.",
        qtype="diagnose", level="medium", principle="root_cause",
        situation="18% of invoices flagged because calculated_total leaves out tax",
        trap="demote the flagged queue instead of fixing the field definitions",
    ),
    MCQ(
        id="Q4.4-24",
        q=("A team extracting meter readings from utility bills wants a way to flag bad extractions. One proposal is a "
           "self-reported `confidence` from 0 to 1 on each field. The other is to extract a computed usage (current reading minus "
           "previous reading) next to the usage printed on the bill, and flag bills where they differ. A pilot of 300 bills holds 11 "
           "known extraction errors. How should you evaluate the two designs?"),
        opts=("Prefer confidence: it covers every field, while the usage comparison covers only one figure read.",
              "Prefer confidence, once it has been calibrated against the 11 known errors in the pilot sample.",
              "Use both, and flag a bill only when the two designs agree that it is wrong.",
              "Prefer the comparison: it tests a figure against the bill, and confidence is only an opinion."),
        ans=3,
        explain=("A disagreement between a computed and a printed figure is evidence from the document, while a self-reported score "
                 "is not. A values breadth of coverage over whether the signal means anything. B still rests on the model's opinion "
                 "of itself, however it is calibrated. C flags only the bills where both signals fire, so errors caught by one alone go through."),
        scenarios=(6,), points=("4.4:S4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the guide favours calculated_total beside stated_total; comparing it with self-reported confidence is a judgment about evidence.",
        qtype="evaluate", level="easy", principle="independent_check",
        situation="meter readings: computed usage versus self-reported confidence as the flag",
        trap="trust the model's own confidence score",
    ),
)
