"""Exam bank · TS 4.1. Original questions; see docs/MCQ_BANK_PLAN.md."""
from utils.mcq_sets import MCQ, Evidence

TS = "4.1"
BULLETS = {
    "K1": "Explicit criteria beat vague instructions: say exactly what counts as a defect",
    "K2": "General instructions such as 'be conservative' or 'only high-confidence findings' do not raise precision the way specific categories do",
    "K3": "False positives in one category lower developers' trust in the categories that are accurate",
    "S1": "Writing review criteria that say which issues to report and which to skip, instead of filtering on confidence",
    "S2": "Switching off a high false-positive category for a while to restore trust, while its prompt is improved",
    "S3": "Defining each severity level with explicit criteria and concrete code examples for consistent classification",
}

BP = "api:build-with-claude/prompt-engineering/claude-prompting-best-practices"
CONS = "api:test-and-evaluate/strengthen-guardrails/increase-consistency"

QUESTIONS = (
    # ---- K1: explicit criteria over vague instructions ----
    MCQ(
        id="Q4.1-01",
        q=("Your CI reviewer's security pass is told to \"look for security problems in the diff\". Across 150 pull requests it "
           "posted 380 findings, and a sample of 60 shows that most are string concatenations in log messages and error text. "
           "Developers have started closing the security section without reading it. What is the most effective change?"),
        opts=("Define what counts: queries or shell commands built from user input without parameter binding.",
              "Ask the reviewer to double-check each security finding before posting, and drop any it doubts.",
              "Restrict the security pass to the database directory, where most injection risks are concentrated.",
              "Cap the security pass at five findings per pull request so that developers see fewer comments."),
        ans=0,
        explain=("A names the pattern that is a defect, so log text drops out while real injection paths stay in scope. B relies "
                 "on the model's own doubt, which has no way to know where the team draws the line. C also hides injection "
                 "risks in the rest of the code. D cuts real and false findings alike."),
        scenarios=(5,), points=("4.1:K1", "4.1:S1"),
        evidence=(Evidence("guide", ""),),
        community="Guide-based: the judgment comes from the guide's task statement; the general prompting pages add nothing specific to it.",
        qtype="fix", level="easy", principle="explicit",
        situation="security pass flags every string concatenation, mostly log text",
        trap="self-check, narrower directory or findings cap instead of a defining criterion",
    ),
    MCQ(
        id="Q4.1-02",
        q=("A reviewer prompt says \"flag risky dependency changes\". Of 220 dependency findings last month, 190 were patch-version "
           "bumps in lockfiles, and the team no longer opens the dependency comments. Its comments quote each changed version "
           "line correctly. Which explanation best accounts for this volume?"),
        opts=("Lockfile hunks are too large for the reviewer to read in full, so it flags them without reading.",
              "\"Risky\" has no stated boundary, so the model treats any version change as a candidate for reporting.",
              "The prompt is too short, and repeating the request several times would make the reviewer more selective.",
              "The reviewer cannot see release notes, so it flags every change whose contents it cannot inspect."),
        ans=1,
        explain=("An undefined word leaves the boundary to the model, and a patch bump fits some readings of it. A is ruled out by "
                 "the correct quotes of the changed lines. C treats length as the problem, when no criterion has been added. D "
                 "invents a missing capability that the stem gives no sign of."),
        scenarios=(5,), points=("4.1:K1",),
        evidence=(Evidence("guide", ""),),
        community="Guide-based: the judgment comes from the guide's task statement; the general prompting pages add nothing specific to it.",
        qtype="diagnose", level="medium", principle="explicit",
        situation="risky dependency changes flagged on 190 of 220 patch bumps",
        trap="blame lockfile size, prompt length or a missing release-notes tool",
    ),
    MCQ(
        id="Q4.1-03",
        q=("A document pipeline asks Claude to \"flag invoices that look suspicious\" for the finance review queue. 38% of 1,200 "
           "invoices are flagged, and reviewers approve 96% of the flagged ones without changes. Confirmed fraud was found in 4 "
           "invoices. Which change will raise precision most?"),
        opts=("Add three of last quarter's confirmed fraudulent invoices to the prompt as examples of suspicious.",
              "Switch to a larger model, which will judge what looks suspicious more like the finance team does.",
              "Name the conditions: items not summing to the total, or a payee absent from the vendor list.",
              "Run the flagging step twice and queue only the invoices that both runs flagged."),
        ans=2,
        explain=("Concrete conditions tell Claude what to flag, and the review queue gets only invoices meeting them. A teaches only the rare "
                 "fraud pattern, when the queue is full of invoices that merely look odd. B hopes a bigger model guesses the finance team's "
                 "meaning of suspicious. D keeps only what two runs agree on, and both runs share the same vague definition."),
        scenarios=(6,), points=("4.1:K1", "4.1:S1"),
        evidence=(Evidence("guide", ""),),
        community="Guide-based: the judgment comes from the guide's task statement; the general prompting pages add nothing specific to it.",
        qtype="fix", level="medium", principle="explicit",
        situation="suspicious invoices flagged for 38% of volume and approved 96% of the time",
        trap="score threshold, larger model or two-run agreement",
    ),
    # ---- K2: confidence wording does not improve precision ----
    MCQ(
        id="Q4.1-04",
        q=("A reviewer prompt was extended with \"only report findings you are highly confident about\". Posted findings fell "
           "from 31 to 24 per pull request, yet developers still dismiss about half of them in both months. The dismissed ones "
           "are mostly renaming and formatting suggestions, which the reviewer's own notes rate as very likely. Which "
           "explanation fits best?"),
        opts=("The threshold is not demanding enough, and a stricter one would clear the remaining false positives.",
              "The reviewer gives less weight to lines added late in a prompt, so the new line had no effect.",
              "Dismissals reflect reviewer fatigue under time pressure, not the quality of the findings.",
              "Confidence says nothing about whether a finding is in a worthwhile category, so nits still pass."),
        ans=3,
        explain=("The model can be sure that a name is poor, and that is still not a defect worth a comment, so categories are "
                 "what separates them. A assumes certainty tracks relevance. B is contradicted by the drop from 31 to 24, which "
                 "shows the line had some effect. C blames developers' state when the dismissed items are of one kind."),
        scenarios=(5,), points=("4.1:K2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-based: the judgment comes from the guide's task statement; the general prompting pages add nothing specific to it.",
        qtype="diagnose", level="medium", principle="explicit",
        situation="confidence-only wording cut volume 31 to 24 with dismissals still near 50%",
        trap="demand stricter certainty or blame position of the line or tired developers",
    ),
    MCQ(
        id="Q4.1-05",
        q=("To improve precision you ran two prompt variants over the same 400 pull requests and counted the findings developers "
           "acted on. Baseline: 10,000 findings, 30% acted on. Variant X added \"be conservative and report only "
           "high-confidence findings\": 8,300 findings, 31% acted on. Variant Y listed categories to report and to skip: 3,900 "
           "findings, 77% acted on. Which conclusion do the results support?"),
        opts=("Y changed what the reviewer treats as reportable, while X mostly trimmed volume and left quality alone.",
              "Both variants improved precision, since each posted fewer findings, and X is the simpler of the two changes.",
              "Y lost recall, because it posted fewer findings, so X is the safer variant to roll out.",
              "X needs tuning, since a stricter version of the same wording would reach the precision Y shows."),
        ans=0,
        explain=("X posted 17% fewer findings but its acted-on share barely moved, whereas Y raised it from 30% to 77%. Y also "
                 "kept about 3,000 acted-on findings, the same as the baseline, so it dropped noise and not value. B counts "
                 "volume as precision. C is contradicted by those acted-on totals. D assumes that more of the same wording will "
                 "do what it has not done."),
        scenarios=(5,), points=("4.1:K2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-based: the judgment comes from the guide's task statement; the general prompting pages add nothing specific to it.",
        qtype="evaluate", level="hard", principle="independent_check",
        situation="A/B of conservative wording versus report-and-skip categories over 400 pull requests",
        trap="count fewer findings as higher precision",
    ),
    MCQ(
        id="Q4.1-06",
        q=("A data pipeline asks Claude to list possible duplicate customer records, and the prompt says \"flag only pairs you are "
           "very confident are duplicates\". Reviewers find that about half the flagged pairs are different people who share "
           "a surname and a postcode. Which change is best?"),
        opts=("Ask for a confidence score on every pair and queue only the pairs scoring above 0.95.",
              "State what qualifies: the same email address, or the same phone number plus postcode.",
              "Add the full customer table to the prompt so Claude can compare each flagged pair with every other record.",
              "Tell Claude that sharing a surname and postcode is common, so each flagged pair needs more care."),
        ans=1,
        explain=("Matching rules tell Claude what makes a duplicate, and a shared surname stops being enough. A rests on "
                 "the model's own sense of certainty, which was already what the prompt asked for. C adds context but no rule for what makes a duplicate. D is a hint with no "
                 "criterion, so the boundary stays vague."),
        scenarios=(6,), points=("4.1:K2", "4.1:S1"),
        evidence=(Evidence("guide", ""),),
        community="Guide-based: the judgment comes from the guide's task statement; the general prompting pages add nothing specific to it.",
        qtype="choose", level="easy", principle="explicit",
        situation="duplicate-customer pairs flagged on surname and postcode alone",
        trap="self-reported confidence score or self-withdrawal pass",
    ),
    # ---- K3: false positives and trust ----
    MCQ(
        id="Q4.1-07",
        q=("Your CI reviewer covers five categories. Fix rates by category: security 88%, logic 81%, naming 9%, documentation 12%, "
           "the last two being 60% of all comments. Eight weeks on, the security fix rate has dropped to 52%. A re-audit of 50 "
           "recent security comments found 46 still correct, and they appear first in each review. Which explanation is "
           "most likely?"),
        opts=("Security findings have become less accurate since the prompt was last edited, so the rate reflects worse output.",
              "Developers need security training, since they cannot tell which of the reviewer's findings are real.",
              "Noisy naming and documentation comments have eroded trust in the whole tool, accurate findings included.",
              "Security findings sit in the middle of long reviews, where they are overlooked."),
        ans=2,
        explain=("Developers who learn that most comments are noise start skipping all of them, including the accurate ones. A is "
                 "ruled out by the re-audit, and D by the findings being posted first. B conflicts with the 88% rate at the "
                 "start, when the same developers acted on most security findings."),
        scenarios=(5,), points=("4.1:K3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the link between a noisy category and trust in accurate ones is the guide's point; no official page covers it.",
        qtype="diagnose", level="medium", principle="root_cause",
        situation="security fix rate falls from 88% to 52% beside noisy naming and documentation categories",
        trap="blame prompt drift, missing training or finding position",
    ),
    MCQ(
        id="Q4.1-08",
        q=("Your team reports the reviewer's overall precision as 71% across 6,000 findings last quarter, and leadership calls the "
           "tool healthy. Developers' comments say that they ignore it. Which additional measurement would best show what is "
           "going on?"),
        opts=("The average number of findings per pull request, tracked week by week.",
              "The overall precision recomputed on a larger sample, to firm up the 71% figure.",
              "The share of reviews in which developers fix at least one finding, split by repository.",
              "Precision per finding category, taken from what developers fixed or dismissed."),
        ans=3,
        explain=("A single average hides a category that is wrong most of the time while others are right. Per-category figures "
                 "show where trust is being lost. A shows volume and says nothing about quality. B gives a more exact version "
                 "of a number that is already too coarse. C counts reviews in which anything was fixed, which a few good "
                 "categories can satisfy."),
        scenarios=(5,), points=("4.1:K3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: measuring false positives per category follows the guide's point about categories; no official page covers it.",
        qtype="evaluate", level="medium", principle="fit_for_purpose",
        situation="71% overall precision while developers ignore the bot",
        trap="aggregate precision hides a noisy category",
    ),
    MCQ(
        id="Q4.1-09",
        q=("A contracts pipeline queues records for human review with a reason code, about 40 records per reviewer per day, which "
           "is workable. In the first two weeks reviewers caught 90% of real total mismatches; six weeks later they approve 97% "
           "of the queue unchanged, and an audit found real mismatches among the approved records, all queued with the "
           "'total mismatch' reason. 'Address format differs' fills 58% of the queue and is corrected in 3% of cases. What "
           "best explains the missed mismatches?"),
        opts=("Reviewers learned queued records are usually fine, so a noisy reason trained them to approve all.",
              "The total check is too weak, so most mismatches reach review with no reason code attached to them.",
              "Reviewers have not been trained to compare totals against the source document.",
              "The queue is too large for one reviewer, so it should be split into smaller daily batches."),
        ans=0,
        explain=("Reasons that are nearly always wrong teach reviewers to wave records through, and the accurate reason code gets "
                 "the same treatment. B is ruled out because the missed ones were all queued with the reason code. C conflicts "
                 "with the 90% catch rate in the first two weeks. D is ruled out by the workload being workable."),
        scenarios=(6,), points=("4.1:K3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: transfers the guide's false-positive and trust point to a review queue; no official page covers it.",
        qtype="diagnose", level="hard", principle="root_cause",
        situation="reviewers rubber-stamp a queue after address-format reason fills 58% of it",
        trap="blame weak detection, missing training or queue size",
    ),
    # ---- S1: report versus skip criteria ----
    MCQ(
        id="Q4.1-10",
        q=("You are writing the review criteria for a CI reviewer on a payments service. The team wants real bugs and security "
           "flaws reported and nothing else. Which prompt section best implements that?"),
        opts=("Report anything that could be improved in the change, rank each finding by importance, and mark the minor ones as optional.",
              "Report: wrong results, missing authorisation, unhandled failures. Skip: naming, formatting, import order.",
              "Report only serious problems with the code and skip the trivial ones, using your best judgement about which are which.",
              "Report bugs and security flaws in any file, and skip only the files that the repository ignores in git."),
        ans=1,
        explain=("B lists what to report and what to skip, so the boundary is stated and not guessed. A reports everything and "
                 "pushes sorting onto developers. C leaves 'serious' and 'trivial' undefined. D skips by file, so style nits "
                 "in tracked files are still reported."),
        scenarios=(5,), points=("4.1:S1",),
        evidence=(Evidence("guide", ""),),
        community="Guide-based: the judgment comes from the guide's task statement; the general prompting pages add nothing specific to it.",
        qtype="configure", level="easy", principle="explicit",
        situation="criteria section for a payments-service reviewer",
        trap="rank-everything, undefined seriousness or certainty cut-off instead of report and skip lists",
    ),
    MCQ(
        id="Q4.1-11",
        q=("The reviewer posts about 400 comments a week on magic numbers in test fixtures, such as order totals and ids, which "
           "the team deliberately keeps inline for readability. The same rule also catches a real unexplained constant in "
           "`src/` about once a week, and the team wants those caught on every pull request. Developers now dismiss the whole "
           "category. How should the criteria change?"),
        opts=("Move the category into a weekly summary that developers can open when they choose.",
              "Add that magic numbers are minor, so they are reported last, after bug and security findings.",
              "Report unexplained constants in `src/` that affect behaviour; skip literals in fixtures and test data.",
              "Tell the reviewer to report a magic number only when it is fully certain that the literal needs a name."),
        ans=2,
        explain=("C keeps the useful check where it matters and states the accepted local pattern as a skip. A keeps the same "
                 "noise in a different place, and the check no longer runs on every pull request. B leaves the 400 fixture "
                 "comments in the review, only lower down. D filters on certainty, which does not mark fixtures as accepted."),
        scenarios=(5,), points=("4.1:S1",),
        evidence=(Evidence("guide", ""),),
        community="Guide-based: the judgment comes from the guide's task statement; the general prompting pages add nothing specific to it.",
        qtype="fix", level="medium", principle="explicit",
        situation="400 weekly magic-number comments on test fixtures, one real hit a week in src",
        trap="weekly digest, reorder or certainty filter in place of a skip rule",
    ),
    MCQ(
        id="Q4.1-12",
        q=("After you rewrote the reviewer prompt to \"report bugs, skip style\", style comments disappeared. It now posts about "
           "30 \"possible race condition\" comments a week, and in a sample of 40 none names an input or interleaving that "
           "gives a wrong result. Which change to the criteria is most effective?"),
        opts=("Add that the reviewer should skip speculative concerns and report only what it is quite sure about.",
              "Move concurrency review into a separate pass, which can have its own instructions and its own focus.",
              "Limit concurrency comments to files that import threading or asyncio, where races are possible.",
              "Define a reportable bug as one where it can state the input or sequence that gives a wrong result."),
        ans=3,
        explain=("D gives a test that a finding must pass, so a vague worry no longer qualifies. A restates the vague caution "
                 "that has not worked elsewhere. B separates the concern without saying what counts as a bug. C narrows where it looks, "
                 "but a speculative worry in those files would still be reported."),
        scenarios=(5,), points=("4.1:S1", "4.1:K2"),
        evidence=(Evidence(BP, "Providing context or motivation behind your instructions, such as explaining to Claude why such behavior is important, can give Claude more information about your goals and help it deliver more targeted responses."),),
        qtype="fix", level="hard", principle="explicit",
        situation="possible-race-condition comments with no concrete trigger after style was skipped",
        trap="extra caution wording, separate pass or likelihood rating",
    ),
    MCQ(
        id="Q4.1-13",
        q=("A second Claude step validates extracted invoice records against the source text and lists issues. It reports about "
           "14 per record, mostly dates or currencies written differently from the source (\"3 Mar 2026\" stored as "
           "\"2026-03-03\"), which downstream code normalises anyway. Reviewers skim the list, and a wrong vendor id was "
           "missed last week. Which criteria should the validator use?"),
        opts=("Report values that differ in meaning from the source, or are missing. Skip formats normalised downstream.",
              "Report every difference it finds with a severity label, and let reviewers filter the whole list by that label.",
              "Report differences only when it is sure, and mention in a note that formatting is of low importance.",
              "Report only amount fields, since a mistake in those causes the most financial loss."),
        ans=0,
        explain=("A separates a real discrepancy from a style difference that is already handled, and it covers every field, "
                 "vendor ids included. B leaves the noise in front of reviewers. C filters on certainty and puts the "
                 "formatting guidance in a note. D drops vendor ids and other fields where mistakes also cost money."),
        scenarios=(6,), points=("4.1:S1", "4.1:K1"),
        evidence=(Evidence("guide", ""),),
        community="Guide-based: the judgment comes from the guide's task statement; the general prompting pages add nothing specific to it.",
        qtype="choose", level="medium", principle="explicit",
        situation="validator lists 14 formatting differences per invoice record and hides a wrong vendor id",
        trap="label-and-filter, certainty gate or amount-only scope",
    ),
    # ---- S2: temporarily disable high false-positive categories ----
    MCQ(
        id="Q4.1-14",
        q=("Weekly metrics show that the reviewer's \"unused parameter\" category posted 62 comments and developers dismissed 57 "
           "of them, while the other four categories are acted on at 70% or more. A demo for two other teams is next week, "
           "and a colleague wants every category visible for it. What should you do first?"),
        opts=("Keep every category on for the demo and revisit the unused-parameter category once it is over.",
              "Pause unused-parameter comments, keep the other four active, and rewrite its criteria.",
              "Pause the whole reviewer for the demo week, then switch every category on again afterwards.",
              "Keep the category on, and add a sentence to each comment saying that it is often a false positive."),
        ans=1,
        explain=("Pausing only the noisy category protects trust in the four accurate ones and still gives the demo something "
                 "worth showing. A puts the 92% dismissed comments in front of the new audience. C stops the four categories "
                 "that work. D keeps the same comments and adds a warning, which tells developers to doubt them."),
        scenarios=(5,), points=("4.1:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: temporarily disabling a noisy category is the guide's skill; no official page covers it.",
        qtype="choose", level="easy", principle="proportionate",
        situation="unused-parameter category dismissed 57 of 62 times before a cross-team demo",
        trap="keep everything on for the demo, pause the whole reviewer or add a warning label",
    ),
        MCQ(
        id="Q4.1-15",
        q=("Developers dismiss 84% of the reviewer's \"complexity\" comments, so you will hide that category while its criteria are "
           "rewritten. You plan to test the rewrite on live pull requests by comparing the reviewer's complexity findings with "
           "what a senior reviewer flags by hand. Which setup should you use?"),
        opts=("Remove the complexity instructions from the prompt and restore them once the new criteria are written.",
              "Keep the category in the prompt, but add \"rarely report complexity\" until the new criteria are ready.",
              "Keep generating complexity findings, withhold them from pull requests, and log them for comparison.",
              "Post complexity findings to a separate channel that developers can follow if they want to."),
        ans=2,
        explain=("Withholding the findings stops the noise reaching developers while the logged output stays available for the "
                 "test. A leaves nothing to compare against until the rewrite is live again. B is a vague instruction, and "
                 "some complexity comments would still appear. D keeps the stream running, only outside the reviews."),
        scenarios=(5,), points=("4.1:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: hiding a category while criteria are improved is the guide's skill; the shadow-logging setup is this question's own design choice.",
        qtype="configure", level="hard", principle="proportionate",
        situation="complexity category hidden while its rewrite is tested against hand-flagged pull requests",
        trap="delete the instructions, add rarely-report wording or move findings to a side channel",
    ),
    MCQ(
        id="Q4.1-16",
        q=("The \"logging\" category was switched off three weeks ago after developers dismissed 78% of its comments, and a "
           "rewritten prompt for it is ready. What should decide whether it is switched back on?"),
        opts=("Waiting until the category has been off for 30 days, so that trust in the other categories recovers.",
              "Asking the reviewer to rate each new logging finding for confidence and switching on if most rate high.",
              "Having three developers read the new prompt and approve its wording before the category is switched on.",
              "Replaying the new prompt on triaged past logging comments and comparing its precision with 22%."),
        ans=3,
        explain=("D tests the rewrite on cases where the right answer is already known, against the old precision of 22%. A "
                 "measures time and not the prompt. B relies on self-rated confidence. C judges the wording, and a prompt "
                 "that reads well can still produce the same false positives."),
        scenarios=(5,), points=("4.1:S2", "4.1:K3"),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the guide says to improve prompts for disabled categories but not how to gate them; the replay test is this question's own design.",
        qtype="evaluate", level="medium", principle="independent_check",
        situation="deciding when the switched-off logging category may return",
        trap="wait a fixed time, rate by confidence or approve the wording",
    ),
    # ---- S3: explicit severity criteria with code examples ----
    MCQ(
        id="Q4.1-17",
        q=("The severity section defines three levels with a code example each, but every example comes from the payments "
           "service, a Python backend. Run on the TypeScript web client, the reviewer classified the same 60 findings "
           "differently in 18 re-reviews, and it often rated rendering glitches as high. Which change is most effective?"),
        opts=("Add an example per level from the web client, such as a crash on submit for high and a misaligned label for low.",
              "Replace the examples with a longer description of each level, so the definitions are no longer tied to one codebase.",
              "Add a rule that web client findings are never rated above medium, since the client holds no sensitive data.",
              "Pass each finding through a second reviewer that compares its level with the levels of similar findings."),
        ans=0,
        explain=("The examples set what each level means, and none of them resembles client code, so the reviewer has to guess. "
                 "Examples from the client fix that. B drops the concrete examples that the guide asks for. C classifies by "
                 "location, and a script-injection flaw in the client would be capped at medium. D compares labels that "
                 "come from the same unanchored judgment."),
        scenarios=(5,), points=("4.1:S3",),
        evidence=(Evidence(BP, "Diverse: Cover edge cases and vary enough that Claude doesn’t pick up unintended patterns."),),
        qtype="fix", level="medium", principle="explicit",
        situation="severity examples all from a Python backend, misapplied on a TypeScript web client",
        trap="prose definitions, location cap or second-pass relabel instead of examples from the new code",
    ),
        MCQ(
        id="Q4.1-18",
        q=("The severity section gives a code example for \"high\" (a SQL string built from user input) and for \"medium\" (an "
           "unchecked list index), and defines \"low\" as \"everything else\". Re-reviewing 40 pull requests twice, the reviewer "
           "assigned \"medium\" to 40% of the findings developers class as low, and the level of the same finding changed "
           "between runs about a quarter of the time. What explains this best?"),
        opts=("Two examples are too few; the reviewer needs about ten per level before it applies them evenly.",
              "\"Low\" has no anchor of its own, so borderline findings drift to the nearest level that does.",
              "The reviewer picks severity from how a finding is worded, so findings should follow a fixed template.",
              "Three named levels cannot be applied consistently by a model, so a numeric scale is needed."),
        ans=1,
        explain=("A level defined only as a leftover gives the model nothing to match, so ambiguous findings move to the levels "
                 "that have examples. A invents a minimum count that the stem does not support. C blames wording when the "
                 "missing piece is the low-level definition. D claims that named levels cannot work, which the "
                 "well-anchored high level in the same prompt contradicts."),
        scenarios=(5,), points=("4.1:S3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-based: the judgment comes from the guide's task statement; the general prompting pages add nothing specific to it.",
        qtype="diagnose", level="medium", principle="root_cause",
        situation="low severity defined as everything else, medium over-assigned on borderline findings",
        trap="more examples, fixed template or numeric scale instead of anchoring the low level",
    ),
    MCQ(
        id="Q4.1-19",
        q=("A validator step labels each extraction discrepancy \"error\" (blocks the record) or \"warning\" (passes it with a "
           "note). In a trial, the same kind of discrepancy was labelled error in 26 of 60 runs and warning in the rest. "
           "Which definition of the two levels will classify most consistently?"),
        opts=("error: the discrepancy is important to the record. warning: the discrepancy is less important to the record. Decide using your overall view of the whole record.",
              "error: any discrepancy in an amount field. warning: any discrepancy in every other field, whichever way the value differs.",
              "error: value contradicts source, as with \"Total 1,204.50\" stored as 1204.05. warning: same meaning, as with \"3 Mar 2026\" stored as \"2026-03-03\".",
              "error: the model is under 70% sure of the value. warning: the model is at least 70% sure of the value."),
        ans=2,
        explain=("C defines both levels by what the discrepancy does and shows a real case for each. A restates the labels in "
                 "other words. B decides by field, so a harmless format change in an amount would block the record while "
                 "a wrong vendor id would only warn. D uses self-reported certainty, which says nothing about whether the value contradicts the source."),
        scenarios=(6,), points=("4.1:S3",),
        evidence=(Evidence(CONS, "Provide examples of the output you want. This is more effective than abstract instructions."),),
        qtype="configure", level="medium", principle="explicit",
        situation="error versus warning labels flip in 26 of 60 runs for the same discrepancy",
        trap="restated adjectives, field-based rule or confidence cut-off",
    ),
    MCQ(
        id="Q4.1-20",
        q=("You rewrote the severity section with definitions and one code example per level, taken from 12 findings in last "
           "month's reviews. To check it, you rerun the reviewer on those 12 findings five times, and it labels them the same "
           "way every time. How should you evaluate whether the new section works?"),
        opts=("Accept the result, since identical labels over five runs show that the section classifies consistently.",
              "Rerun the same 12 findings on another model, and keep the section if both models agree on every one.",
              "Add the rest of last month's findings to the examples and rerun them, then compare the agreement.",
              "Label a fresh set of findings not used as examples, then check the new levels against those labels."),
        ans=3,
        explain=("The examples sit inside the prompt, so the 12 findings test memory and not classification. A fresh labelled set "
                 "shows whether the criteria carry over to new code. A takes that memory as proof of consistency. B swaps in "
                 "another model but keeps the same 12 findings. C feeds more findings into the examples, so no unseen test set is left."),
        scenarios=(5,), points=("4.1:S3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the guide asks for severity examples but not how to test them; the held-out check is this question's own judgment.",
        qtype="evaluate", level="hard", principle="independent_check",
        situation="severity section checked on the same 12 findings used as its examples",
        trap="score the examples, cross-check another model or enlarge the example set",
    ),
)
