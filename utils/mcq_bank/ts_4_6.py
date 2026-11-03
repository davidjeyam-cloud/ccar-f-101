"""Exam bank · TS 4.6. Original questions; see docs/MCQ_BANK_PLAN.md."""
from utils.mcq_sets import MCQ, Evidence

TS = "4.6"
BULLETS = {
    "K1": "A model keeps its reasoning context from generation, so it is less likely to question its own decisions in the same session",
    "K2": "Independent review instances without the generator's reasoning beat self-review instructions or extended thinking",
    "K3": "Large reviews split into per-file local passes plus cross-file integration passes to avoid attention dilution and contradictory findings",
    "S1": "Using a second independent Claude instance to review generated code without the generator's reasoning context",
    "S2": "Splitting multi-file reviews into per-file passes for local issues plus integration passes for cross-file data flow",
    "S3": "Running verification passes where the model reports confidence beside each finding, to route review in a calibrated way",
}

_FRESH = "A fresh reviewer does help, because it hasn't seen your reasoning, which is a different thing from delegating."
_CHAIN_STEPS = "Each step is a separate API call so you can log, evaluate, or branch at any point."
_BP = "api:build-with-claude/prompt-engineering/claude-prompting-best-practices"

QUESTIONS = (
    # ---- K1: limits of self-review ----
    MCQ(
        id="Q4.6-01",
        q=("Your invoice extraction pipeline sends each document to Claude, then adds a second turn in the same conversation on "
           "every invoice: \"Re-read the invoice and confirm every field.\" The confirmation succeeds on 99% of invoices. A human "
           "audit of 300 invoices still finds 8% of fields wrong, and in 41 of the 46 wrong cases the confirmation text repeats the "
           "same column mapping that caused the error, such as a net amount read as the gross amount. What is the most likely root cause?"),
        opts=("The second turn builds on a reading that is still in the conversation, so it tends to confirm that reading.",
              "The confirmation turn is skipped unless the first answer parses against the schema, so some answers are never rechecked.",
              "The conversation is long by the second turn, so the invoice text has been dropped before the model re-reads it.",
              "The request covers every field, so the model spreads its attention too thin to notice single mistakes."),
        ans=0,
        explain=("The model that made the first reading is still holding the reasoning behind it, so asking it to confirm mostly "
                 "repeats the same interpretation; the repeated column mapping shows this. B conflicts with the stem, where the "
                 "turn runs on every invoice. C would produce random misses, not one mapping repeated, and the invoice is still in "
                 "the conversation. D predicts scattered misses too, where the audit found the same mistake again and again."),
        scenarios=(6,), points=("4.6:K1",),
        evidence=(Evidence("code:best-practices", _FRESH),),
        qtype="diagnose", level="medium", principle="independent_check",
        situation="same-conversation confirm turn repeats the net-versus-gross column error on invoices",
        trap="blame attention spread or truncation rather than shared reasoning",
    ),
    MCQ(
        id="Q4.6-02",
        q=("In your CI environment, Claude Code implements a `bulk_discount()` function and, in the same session, writes its unit "
           "tests. All 14 tests pass, including five edge cases such as the maximum quantity, and line coverage is 96%. A week "
           "later, orders with quantity 0 receive a negative total. Review finds that the faulty arithmetic sits on a line the "
           "tests do run, but never with that input. The ticket did not mention zero quantities. What explains the gap most directly?"),
        opts=("Coverage of 96% is too low, and the untested 4% of lines held the zero-quantity logic.",
              "Tests written after the code are dropped when the session ends, so the final run used an older test file.",
              "The tests came from the same reasoning as the function, so they share its view of valid input.",
              "The session ran short of context while writing tests, so it stopped before it reached the odd inputs."),
        ans=2,
        explain=("The session that wrote the function also chose which inputs were worth testing, so the tests inherit the same "
                 "blind spot and pass. A is ruled out because the faulty line is covered. B invents a behaviour, and the "
                 "tests did run. D conflicts with the stem, where the session finished and covered five edge cases."),
        scenarios=(5,), points=("4.6:K1",),
        evidence=(Evidence("code:best-practices", _FRESH),),
        qtype="diagnose", level="medium", principle="independent_check",
        situation="generator-written tests all pass but miss zero quantity in a discount function",
        trap="blame the coverage figure instead of the shared assumptions",
    ),
    MCQ(
        id="Q4.6-03",
        q=("After extracting contract terms, your pipeline asks the same Claude conversation to justify each ambiguous field, for "
           "example why a notice period is 60 days when two clauses disagree. The justifications read as coherent for 97% of "
           "fields, yet an audit finds 12% of those fields wrong. How should you evaluate the justification step as a quality control?"),
        opts=("Keep it, and audit a 5% sample, since a coherent explanation is good evidence that the field is right.",
              "Replace it with a second instance that reads only the document, and review the fields where they disagree.",
              "Require longer justifications that quote the clause text, so a wrong field becomes harder to explain convincingly.",
              "Move the justification into a structured output field, so the explanation is checked against the schema."),
        ans=1,
        explain=("An explanation produced by the session that chose the value is built from the same reasoning, so it sounds "
                 "convincing whether or not the value is right; an instance that reads the document afresh is a real second view. "
                 "A treats fluency as proof. C stays in the same session, and a quoted clause can be misread just as confidently. "
                 "D checks that the explanation has the right shape, not that it is true."),
        scenarios=(6,), points=("4.6:K1",),
        evidence=(Evidence("code:best-practices", "A second session is also the easiest independent reviewer you can get."),),
        community="Docs support the independent second reviewer (best-practices); that a self-generated rationale is weak evidence follows from the guide's self-review limitation, which no official page tests.",
        qtype="evaluate", level="hard", principle="independent_check",
        situation="coherent same-session justifications for contract fields that audit shows are 12% wrong",
        trap="treat a fluent rationale as verification",
    ),
    # ---- K2: independent instances beat self-review and extended thinking ----
    MCQ(
        id="Q4.6-04",
        q=("Your CI job has one Claude session generate a patch and then review it. On a set of 20 seeded defects, the review "
           "caught 5. Enabling extended thinking with a large budget for the review step raised that to 6. A fresh instance given "
           "only the diff and the repository caught 13. What should you do next?"),
        opts=("Raise the thinking budget again, since the move from 5 to 6 shows that deeper reasoning helps.",
              "Add a checklist of 30 common defect types to the review prompt of the generating session.",
              "Move the review to a larger model but keep it inside the generating session.",
              "Make the review a separate instance that has not seen how the patch was produced."),
        ans=3,
        explain=("The big gain came from taking the generator's reasoning out of the reviewer, which more thinking in the same "
                 "session cannot do. A chases a one-defect improvement. B adds instructions to a session that still believes its own "
                 "choices. C changes the model, not the shared context that produced the blind spot."),
        scenarios=(5,), points=("4.6:K2",),
        evidence=(Evidence("code:best-practices", _FRESH),),
        qtype="choose", level="easy", principle="independent_check",
        situation="extended thinking in the generating session lifts seeded-defect catches from 5 to 6, a fresh instance gets 13",
        trap="spend more thinking on the same session",
    ),
    MCQ(
        id="Q4.6-05",
        q=("Your CI finder pass returns about 40 candidate findings per PR, and a labelled sample shows only a quarter are real. "
           "You add a verification stage. Which design best follows a verification pass with reported confidence and calibrated routing?"),
        opts=("Ask the finder to attach a confidence to each finding, and drop the lowest 60% on that score alone, unseen.",
              "Pass each candidate and its code to a separate checker that reports confidence, and route by measured bands.",
              "Repeat the finder three times and post whatever two of the repeats both report, with a note on each.",
              "Post all 40 with a label saying they are unverified, and let developers decide which ones deserve a close read."),
        ans=1,
        explain=("A separate pass checks each candidate against the code, and routing on its confidence is sound once bands are "
                 "measured against labelled outcomes. A trusts the finder's own score and drops findings unseen. C repeats the same "
                 "finder, whose repeated mistakes agree with each other. D moves the filtering to developers, which is the cost "
                 "that the stage should remove."),
        scenarios=(5,), points=("4.6:S3",),
        evidence=(Evidence("code:code-review", "a verification step checks the candidate findings against the code and filters out false positives."),),
        qtype="choose", level="medium", principle="independent_check",
        situation="finder with 25% precision gets a verification stage with calibrated routing",
        trap="trust the finder's own score or its repeated runs",
    ),
    MCQ(
        id="Q4.6-06",
        q=("To improve review quality without extra calls, a team appends this to the generating session: \"Forget how you wrote "
           "this and review it as a skeptical outsider.\" On 20 seeded defects the session caught 4, while a fresh instance given "
           "only the diff caught 12. Which explanation fits best?"),
        opts=("The instruction cannot remove the reasoning from the conversation, so the code is still read through it.",
              "A skeptical persona makes the model reject correct code, so many of its flags were false alarms.",
              "Review instructions apply only to the first turn of a session, so the appended request was ignored.",
              "The fresh instance had a larger context window than the session, which is why it reached more of the defects."),
        ans=0,
        explain=("The reasoning that produced the code is still sitting in the session, and a request to ignore it does not "
                 "remove it. B is contradicted by the stem, which counts defects caught. C invents a rule about first turns. "
                 "D has nothing in the stem behind it, and window size was not shown to matter."),
        scenarios=(5,), points=("4.6:K2",),
        evidence=(Evidence("code:best-practices", _FRESH),),
        qtype="diagnose", level="medium", principle="independent_check",
        situation="skeptical-outsider instruction appended to the generating session catches 4 of 20 seeded defects",
        trap="trust a prompt to switch off context the session already holds",
    ),
    # ---- K3: per-file and integration passes ----
    MCQ(
        id="Q4.6-07",
        q=("A legal-tech pipeline sends each 90-page contract with its amendments to Claude in one call and asks for every "
           "obligation and key date. Obligations from the first 20 pages come back detailed, those after page 60 are thin, and "
           "across repeated runs the notice period is 30 days in one and 60 in another. The base contract says 30 and an amendment "
           "on page 81 says 60. What is the most effective redesign?"),
        opts=("Run the single call three times and keep only the values on which all three runs agree.",
              "Put the amendments first in the prompt, so the later pages are read with more care.",
              "Extract section by section in separate passes, then run one pass that reconciles terms across sections.",
              "Move to a model with a bigger context window, so that the entire contract fits and is read in a single call."),
        ans=2,
        explain=("Local extraction gives each section full attention, and a separate pass looks at what only shows up across "
                 "sections, such as an amendment that overrides a clause. A drops the notice period whenever runs differ, so the "
                 "conflict is hidden and not resolved. B reorders the prompt and the single pass still thins out. D adds room, "
                 "but the thin coverage comes from one pass doing too much."),
        scenarios=(6,), points=("4.6:K3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the guide's per-file plus cross-file integration pattern, applied here to contract sections as a reconciliation pass, which is my extension.",
        qtype="fix", level="medium", principle="fit_for_purpose",
        situation="90-page contract in one call gives thin late sections and a notice period that flips between 30 and 60 days",
        trap="read the whole contract in one bigger call",
    ),
    MCQ(
        id="Q4.6-08",
        q=("Your CI reviews a 28-file pull request in a single pass. Run to run on the same commit, the findings cluster in "
           "different places: one run comments heavily on files 1 to 9, the next on files 14 to 22. The prompt already defines "
           "four severity levels with examples, the diff is fed in the same order every time, 4-file PRs give stable findings, context use is 6% of the window, "
           "and every run ends with `stop_reason: \"end_turn\"`. What is the most likely root cause?"),
        opts=("The prompt lacks guidance on which files matter, so each run decides for itself which to examine closely.",
              "Each run reads the files in a different order, so a fixed file order would make the findings identical.",
              "The output limit is reached at a different point in each run, so the later files are cut off.",
              "One pass over 28 files spreads attention unevenly, and where the depth lands changes from run to run."),
        ans=3,
        explain=("When one pass covers many files, depth falls where attention thins, and which files get it varies, which "
                 "per-file passes would remove by giving every file the same focus. A is weakened by the prompt's severity "
                 "definitions, which speak to importance. B is ruled out because the order is fixed. C is ruled out by `end_turn`, "
                 "which is not a truncated response."),
        scenarios=(5,), points=("4.6:K3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: attention dilution is the guide's term; no official page describes it.",
        qtype="diagnose", level="medium", principle="root_cause",
        situation="same 28-file commit gets detailed comments on different files in each run",
        trap="blame file order, truncation or the prompt rather than one-pass dilution",
    ),
    MCQ(
        id="Q4.6-09",
        q=("Your team reviews pull requests with one Claude pass. The median PR is 3 files and 90% are under 8 files, but a few "
           "migration PRs touch 40 to 120 files and cannot be split by their authors. A pilot found review quality unchanged up to about 15 "
           "files and falling sharply beyond 30, where late files get one-line comments. A proposal would run per-file passes plus an integration pass on "
           "every PR. How should you evaluate it?"),
        opts=("Adopt it for every PR, so that all authors get the same review process.",
              "Adopt it only for PRs above about 30 files, and keep the single pass for smaller ones.",
              "Reject it: splitting removes context that a single pass keeps, and a larger window fixes the migrations.",
              "Reject it, and require migration authors to split their work so that no review exceeds eight files."),
        ans=1,
        explain=("The weakness shows only on large changes, so the extra passes belong there and nowhere else, since each one is "
                 "another call. A pays for passes on PRs that have no dilution problem. C offers a bigger window for a problem "
                 "that is about focus. D asks for what the stem says authors cannot do."),
        scenarios=(5,), points=("4.6:K3",),
        community="Cost proportionality: the guide says to split large reviews; the file-count threshold is a judgment from the pilot in the stem, not a guide rule.",
        evidence=(Evidence("code:best-practices", "Subagents are still great for parallel work, keeping noisy output out of your way, and independent review, but each of those costs extra tokens."),),
        qtype="evaluate", level="medium", principle="proportionate",
        situation="split-review proposal for all PRs when only 40-to-120-file migrations are diluted",
        trap="apply multi-pass review everywhere",
    ),
    # ---- S1: a second independent instance ----
    MCQ(
        id="Q4.6-10",
        q=("In a Claude Code session, Claude has just implemented a retry wrapper from `SPEC.md`. You want an independent review "
           "before opening the pull request. Which setup gives the most independent check?"),
        opts=("Fork the current conversation into a subagent and ask it to review, so it can see the files and the discussion.",
              "Start a read-only reviewer subagent and pass it the implementation plan and a note on the trade-offs Claude chose.",
              "Start a reviewer subagent and point it at the changed files and `SPEC.md`.",
              "Ask the current session to re-read the changed files from disk and review them against `SPEC.md`."),
        ans=2,
        explain=("A non-fork subagent has no conversation history, only the prompt string plus project CLAUDE.md, so pointing it at the "
                 "code and the spec gives it what it needs to check and nothing of the author's reasoning. A copies the conversation, so the reasoning "
                 "comes along. B puts the author's plan and trade-offs into the prompt, and read-only tools do not undo that. D keeps everything the session already believes."),
        scenarios=(5,), points=("4.6:S1",),
        evidence=(Evidence("code:agent-sdk/subagents", "A [fork](https://code.claude.com/docs/en/sub-agents.md#fork-the-current-conversation) is a subagent that copies the conversation so far instead of starting fresh."),
                  Evidence("code:best-practices", "Getting a reviewer that hasn't seen how the code was written")),
        basis="docs",
        qtype="configure", level="easy", principle="independent_check",
        situation="choosing how to launch a reviewer for a retry wrapper implemented from a spec",
        trap="fork the session or hand the reviewer the author's plan",
    ),
    MCQ(
        id="Q4.6-11",
        q=("You add a second Claude instance to review invoice extractions. The extractor produces a JSON record plus about 200 "
           "words of notes on how it resolved each unclear field. The reviewer will run on every invoice and should catch "
           "misread values. Which input should it receive?"),
        opts=("The source invoice and the extracted JSON, but not the extractor's notes.",
              "The source invoice, the JSON and the notes, so that it can check the extractor's reasoning.",
              "The extracted JSON and the notes, so it can judge consistency without rereading the invoice.",
              "The source invoice, the JSON and a one-line list of the fields the extractor found unclear."),
        ans=0,
        explain=("The reviewer needs the source to check against and the record to check, and nothing that tells it how the "
                 "extractor came to its values. B and D pass along the extractor's reasoning or doubts, which points the reviewer "
                 "toward the same spots. C removes the source, so it cannot find a misread value at all."),
        scenarios=(6,), points=("4.6:S1",),
        evidence=(Evidence("code:best-practices", _FRESH),),
        qtype="choose", level="medium", principle="independent_check",
        situation="deciding what a second instance receives when reviewing invoice extractions",
        trap="give the reviewer the extractor's notes or a list of its doubts",
    ),
    MCQ(
        id="Q4.6-12",
        q=("To review 2,000 extracted invoice records, a single reviewer conversation works through them in order. Its detection "
           "of planted errors is 85% in the first 50 records and 55% after the 400th. Its early comments show it accepted a "
           "day-first date reading for one supplier, and it has applied that reading since. Context use is under 30%. What is the "
           "most effective change?"),
        opts=("Remind the reviewer every 100 records to re-check its date assumptions against the source documents.",
              "Summarise the conversation every 200 records so that it stays short and keeps its earlier conclusions.",
              "Switch the reviewer to a model with more context room, so that nothing in the conversation is dropped.",
              "Make each record its own reviewer call, given only the source document and the record."),
        ans=3,
        explain=("The long conversation turns the reviewer's earlier judgments into context it then defers to, so independence "
                 "erodes with every record; a fresh call per record starts without them. A asks the same drifting session to "
                 "police itself. B keeps the earlier conclusions in the summary. C is unneeded, since context use is under 30%."),
        scenarios=(6,), points=("4.6:S1",),
        evidence=(Evidence("code:best-practices", _FRESH),),
        qtype="fix", level="medium", principle="independent_check",
        situation="one long reviewer conversation adopts an early date assumption and misses more errors",
        trap="remind or summarise instead of starting each review fresh",
    ),
    # ---- S2: per-file passes plus integration passes ----
    MCQ(
        id="Q4.6-13",
        q=("A PR changes `normalize_date()` in `dates.py` so that it returns `None` for malformed input instead of raising. Your "
           "pipeline runs a per-file pass on each of the 3 changed files and an integration pass over the same 3 files. All "
           "pass cleanly. Two days after the merge, six unchanged modules that call `normalize_date()` crash on `None`. How "
           "should the pipeline change?"),
        opts=("Name the six callers in the per-file prompt, so that each pass checks them for crashes.",
              "Let the integration pass search the repository for callers of the changed functions and check them.",
              "Run a per-file pass on every file in the repository whenever a function's return value changes.",
              "Tell the per-file pass to flag every changed return value, so that the integration pass gets a warning."),
        ans=1,
        explain=("Following a changed function's data to the code that uses it is the integration pass's job, and here the "
                 "affected files are outside the diff, so that pass needs to look beyond it. A cannot work, since nobody knows "
                 "the callers beforehand. C pays for hundreds of per-file passes where a targeted search would do. D produces "
                 "a flag, and the pass receiving it still cannot see the callers."),
        scenarios=(5,), points=("4.6:S2",),
        evidence=(Evidence("code:code-review", "**Find**: several agents examine the diff and the surrounding code in parallel."),),
        qtype="fix", level="hard", principle="fit_for_purpose",
        situation="return value of a changed helper breaks six unchanged callers outside the diff",
        trap="limit the integration pass to the changed files",
    ),
    MCQ(
        id="Q4.6-14",
        q=("To save time, your pipeline runs one reviewer per file in parallel, and each posts its own inline comments. On a "
           "12-file change, `cache.py` is told to make `get_user` asynchronous, while `api.py` is told to keep `get_user` "
           "synchronous because `api.py` calls it that way. Developers lose time deciding who is right. What is the most "
           "effective fix?"),
        opts=("Have each pass read the other files' diffs before it comments, so each can see what it conflicts with.",
              "Run the per-file passes one after another, each told to avoid contradicting the earlier ones.",
              "Hold the per-file findings back, and let an integration pass reconcile them before any are posted.",
              "Add a rule to every per-file prompt: do not suggest changing the signature of a function."),
        ans=2,
        explain=("Each per-file pass sees one file, so conflicts between them are expected, and the cross-file pass is the place "
                 "to settle them before a developer sees them. A loads every diff into every pass and brings back the dilution "
                 "that per-file passes avoid. B gives up the parallelism and still relies on each pass remembering earlier "
                 "comments. D silences valid findings about signatures."),
        scenarios=(5,), points=("4.6:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the guide says integration passes avoid contradictory findings; no official page covers reconciling per-file reviewers.",
        qtype="fix", level="medium", principle="fit_for_purpose",
        situation="parallel per-file reviewers post opposite advice about one shared function",
        trap="let every per-file pass see every diff",
    ),
    MCQ(
        id="Q4.6-15",
        q=("A nightly job extracts supplier invoices, one document per call. A separate Claude instance then validates each record "
           "against its own document, and all 2,000 records from last night validate. Finance still reports invoice number "
           "`INV-4471` under two different suppliers, and \"Acme Ltd\" and \"ACME Limited\" counted as two vendors. Which gap in "
           "the review design best explains this?"),
        opts=("No pass looks across records, and these problems exist only between documents.",
              "The validation pass is not an independent instance, so it confirms whatever the extractor produced.",
              "The batch is too large for one validation call, so records beyond the first few hundred were never checked.",
              "The validation pass reads each document in too much detail, so it overlooks problems between records."),
        ans=0,
        explain=("Checking each record against its own source is the local pass, and it passed; duplicates and name variants "
                 "appear only when records are compared, which needs a pass over all of them. B conflicts with the stem, where a "
                 "separate instance validates. C conflicts with it too, since all 2,000 records were validated. D treats detail as "
                 "the cause, when no local look could find a problem that spans documents."),
        scenarios=(6,), points=("4.6:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the guide describes per-file passes plus a cross-file integration pass for code; applying it to batches of extracted records is my extension.",
        qtype="diagnose", level="medium", principle="root_cause",
        situation="per-document validation passes while duplicate invoice numbers and vendor name variants slip through",
        trap="blame the independence or size of the local validation",
    ),
    MCQ(
        id="Q4.6-16",
        q=("Your integration pass receives the diff plus the per-file findings, and its prompt says \"Review this whole change "
           "thoroughly\". It re-reports local issues the per-file passes already judged, and in 9 of 40 PRs it calls a line a bug "
           "that a per-file pass had cleared with a stated reason. Its cross-file findings are few. What is the most effective fix?"),
        opts=("Remove the per-file findings from its input, so that it forms its own view without being influenced.",
              "Raise its thinking budget, so that it resolves disagreements with the per-file passes by reasoning.",
              "Tell it to prefer the per-file verdict whenever the two disagree, and drop its own.",
              "Scope its prompt to cross-file data flow and interface mismatches, using local verdicts as input."),
        ans=3,
        explain=("The integration pass exists for what a single file cannot show; when it is told to redo everything, it competes "
                 "with the passes that have already given each file full attention, and contradicts them. A removes the context it "
                 "should build on. B keeps it doing the wrong job with more effort. C settles the contradiction by discarding the "
                 "pass's own output, so the cross-file findings could go too."),
        scenarios=(5,), points=("4.6:S2", "4.6:K3"),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the guide says integration passes handle cross-file data flow and that splitting avoids contradictory findings; how to scope the integration prompt is my judgment.",
        qtype="fix", level="hard", principle="explicit",
        situation="integration prompt asks for a thorough whole-change review and contradicts per-file verdicts",
        trap="remove the per-file results or let one pass overrule the other",
    ),
    # ---- S3: verification passes and calibrated routing ----
    MCQ(
        id="Q4.6-17",
        q=("A verification pass in your extraction pipeline reports a confidence from 0 to 1 beside each extracted field, and fields "
           "at 0.90 or above skip human review. The team labelled 400 fields by hand. Fields at 0.90 or above were correct 99% of "
           "the time for amounts and 86% for dates, and skipping review requires at least 97% accuracy. What should you change?"),
        opts=("Raise the cutoff for all fields to 0.97, since the cutoff should equal the accuracy you require.",
              "Keep the cutoff, and add a line to the prompt asking the model to be more careful with dates.",
              "Set a cutoff for each field type from the labelled results, and keep dates in review until 97%.",
              "Keep the cutoff, since the accuracy across both field types is above 90% and close enough."),
        ans=2,
        explain=("A confidence value is only useful once it is measured against outcomes, and the labels show it means different "
                 "things for different field types, so routing needs per-type cutoffs set from measured accuracy. A confuses a "
                 "confidence value with an accuracy rate. B hopes a prompt changes the numbers. D accepts a result below the stated requirement."),
        scenarios=(6,), points=("4.6:S3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: self-reported confidence and calibrated routing come from the guide's skill; no official page covers calibrating cutoffs against labelled data.",
        qtype="fix", level="hard", principle="independent_check",
        situation="a 0.90 cutoff that is 99% accurate for amounts but 86% for dates",
        trap="set the cutoff equal to the required accuracy",
    ),
    MCQ(
        id="Q4.6-18",
        q=("A verification pass gives each CI review finding a confidence, and findings at 0.80 or above are posted automatically. "
           "For three months about 40% of findings cleared the cutoff and developers accepted 90% of them. After a model update, "
           "85% of findings clear it and developers accept only 68%. The prompt did not change, and a hand-labelled sample "
           "confirms that the posted findings are less often correct. What is the most likely root cause?"),
        opts=("The new model's stated confidence no longer lines up with outcomes, so the old cutoff has lost its meaning.",
              "Developers have become stricter reviewers, so acceptance fell while the findings stayed as accurate as before.",
              "The new model finds more real issues, so a larger share of its findings legitimately clears the cutoff.",
              "Confidence values are rounded to two places, so many findings tie at 0.80 and pass the cutoff."),
        ans=0,
        explain=("The share above the cutoff jumped while accuracy fell, which means the numbers the model reports mean something "
                 "different now; the cutoff has to be re-measured against labelled outcomes after a change like this. B is ruled out "
                 "by the labelled sample. C conflicts with the lower accuracy. D invents a rounding effect that would not appear only after an update."),
        scenarios=(5,), points=("4.6:S3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: calibrated review routing is the guide's skill; re-measuring after a model change is my judgment.",
        qtype="diagnose", level="medium", principle="independent_check",
        situation="after a model update 85% of findings clear the 0.80 cutoff but acceptance falls from 90% to 68%",
        trap="assume a confidence cutoff keeps its meaning across model changes",
    ),
    MCQ(
        id="Q4.6-19",
        q=("Your verification pass attaches a confidence to each finding. Over 1,000 hand-labelled findings: the 0.9 to 1.0 band "
           "had 600 findings with 540 correct; the 0.7 to 0.9 band had 300 with 180 correct; below 0.7 there were 100 with 20 "
           "correct. Policy: post automatically only a band whose measured precision is at least 85%, send every other finding to "
           "a reviewer, and discard none. Which routing meets the policy?"),
        opts=("Post automatically at 0.7 and above, and send findings below 0.7 to a reviewer.",
              "Post every finding automatically, and let developers dismiss the wrong ones.",
              "Post at 0.9 and above, discard findings below 0.7, and send the middle band to a reviewer.",
              "Post at 0.9 and above, and send every finding below 0.9 to a reviewer."),
        ans=3,
        explain=("Only the top band measures 90%, above the 85% bar, and the policy sends everything else to a person. A would "
                 "post a mix of bands at 80% precision (720 of 900). B posts at 74%. C breaks the rule that none are discarded."),
        scenarios=(5,), points=("4.6:S3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the guide names calibrated review routing from reported confidence; the numbers and policy here are invented.",
        qtype="evaluate", level="easy", principle="independent_check",
        situation="choosing a posting cutoff from labelled precision of three confidence bands",
        trap="trust the stated confidence without reading the measured precision per band",
    ),
    MCQ(
        id="Q4.6-20",
        q=("Your extraction call returns each field with a self-reported confidence. 96% of fields report 0.9 or higher, yet a "
           "labelled audit finds only 62% of those fields correct, so the confidence cannot route anything: no cutoff on it reaches the required 97% accuracy. A separate instance "
           "given only the document and the extracted record produces a wide spread of confidences, and 91% of its 0.9-and-above "
           "fields are correct. Which design should you adopt?"),
        opts=("Keep the extractor's confidence, and raise the cutoff to 0.99 until the audit accuracy reaches 91%.",
              "Add a verification pass by a separate instance, and route on its confidence once labels back it.",
              "Ask the extractor to rate its confidence on a 1 to 10 scale, which spreads the values more.",
              "Average the extractor's and the verifier's confidence, and route on the average."),
        ans=1,
        explain=("A verifier that has not seen the extractor's reasoning is less swayed by it, and its confidence is worth routing on "
                 "once labelled data shows it separates right from wrong. A keeps a number that is high for nearly everything. C changes "
                 "the scale of a score that carries no signal. D blends the useful score with the useless one."),
        scenarios=(6,), points=("4.6:S3", "4.6:K2"),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: self-reported confidence and calibrated routing come from the guide; no official page covers calibrating it.",
        qtype="fix", level="hard", principle="independent_check",
        situation="extractor reports 0.9 or higher on 96% of fields while only 62% are correct",
        trap="raise the cutoff on a confidence that is high for everything",
    ),
)
