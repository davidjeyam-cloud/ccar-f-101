"""Exam bank · TS 3.5. Original questions; see docs/MCQ_BANK_PLAN.md."""
from utils.mcq_sets import MCQ, Evidence

TS = "3.5"
BULLETS = {
    "K1": "Concrete input/output examples communicate a transformation best when prose is read inconsistently",
    "K2": "Test-driven iteration: write the tests first, then iterate by sharing the failures",
    "K3": "The interview pattern: Claude asks questions to surface considerations the developer has not anticipated",
    "K4": "When to put all issues in one message (they interact) and when to fix them one by one (they are independent)",
    "S1": "Giving 2-3 concrete input/output examples when a prose description produces inconsistent results",
    "S2": "Writing tests for expected behaviour, edge cases and performance before implementing, then sharing failures",
    "S3": "Using the interview pattern in unfamiliar domains to surface design considerations such as failure modes",
    "S4": "Giving specific test cases with example input and expected output to fix edge-case handling",
    "S5": "Describing interacting issues together in one detailed message, independent issues sequentially",
}

BP_API = "api:build-with-claude/prompt-engineering/claude-prompting-best-practices"

QUESTIONS = (
    # ---- K1: examples beat prose ----
    MCQ(
        id="Q3.5-01",
        q=("A data-team engineer asks Claude Code to \"standardise the phone numbers in customers.csv\" for an import tool. Run on the "
           "same 500-row sample five times, the output differs: some runs write `+44 7700 900123`, others `07700900123`, others "
           "`+447700900123`. The instruction has been reworded twice with more detail about spacing and prefixes, and the variation "
           "continues. What is the most effective fix?"),
        opts=("Put a rule in CLAUDE.md that phone numbers get one standard form, and ask Claude to apply it strictly.",
              "Show a few rows as raw value and exact output, including one number with no country code.",
              "Run the task three times and keep the format that appears most often in the results of those runs.",
              "Ask Claude to announce the format it has chosen at the start of each run and to hold to it for the whole file."),
        ans=1,
        explain=("Pairs of raw input and exact output pin down the transformation, including the case the prose left open. A moves the "
                 "same wording to another file. C picks the most popular output, which need not be the required one. D has Claude "
                 "report a choice it makes anew in each run, so the formats still differ between runs."),
        scenarios=(4,), points=("3.5:K1",),
        evidence=(Evidence(BP_API, "Examples are one of the most reliable ways to steer Claude’s output format, tone, and structure."),),
        qtype="fix", level="medium", principle="explicit",
        situation="phone numbers standardised three different ways across five runs of a CSV job",
        trap="more prose, a CLAUDE.md line or majority vote instead of input/output pairs",
    ),
    MCQ(
        id="Q3.5-02",
        q=("A finance engineer wants Claude Code to rewrite expense lines like `Taxi 12.50 USD` into the ledger form `TRAVEL|1250|USD`. "
           "She supplies three examples: a taxi, a train and a bus fare, each with a decimal amount in USD. On a test batch, "
           "`Hotel 140 EUR` comes out as `TRAVEL|140|EUR` in some runs and `LODGING|14000|EUR` in others. What is the most likely "
           "root cause?"),
        opts=("Three examples are too few; a format cannot be generalised until a dozen or so have been shown.",
              "A transformation cannot be applied to lines whose currency differs from the one shown in the examples.",
              "The examples differ only in item and amount, so the whole-number and non-USD lines were never shown.",
              "The target form must first be given as a template with placeholders before any examples can be used."),
        ans=2,
        explain=("Examples teach only what they cover, and these three share the same shape, so Claude guesses at the cases the batch "
                 "contains and guesses differently each time. A invents a threshold, since a few varied examples can be enough. B "
                 "describes a limit that does not exist. D adds a step that would not change what is missing, which is cases showing "
                 "whole numbers and another currency."),
        scenarios=(4,), points=("3.5:K1",),
        evidence=(Evidence(BP_API, "**Diverse:** Cover edge cases and vary enough that Claude doesn’t pick up unintended patterns."),),
        qtype="diagnose", level="hard", principle="explicit",
        situation="three same-shaped expense examples leave whole-number euro lines to chance",
        trap="blame the number of examples or the lack of a template",
    ),
    MCQ(
        id="Q3.5-03",
        q=("A platform team has Claude Code tidy changelog entries \"into our house style\" before each release. The written style guide "
           "is already pasted into the prompt. Reviewers see that about a third of runs capitalise the word after the colon, a third do "
           "not, and the order of entries varies. The team lead suggests running the job three times and keeping the version that "
           "appears most often. What is the better fix?"),
        opts=("Run it five times instead of three, and keep the version that appears most often among them.",
              "Move the style guide to the end of the prompt, where the last instructions are read first.",
              "Rewrite the style guide as a numbered list of ten formatting rules, one sentence each.",
              "Add a few entries as before and after text, covering capitalisation and order."),
        ans=3,
        explain=("Before-and-after entries show the style where the written guide is read in different ways. A and the lead's plan only "
                 "choose among outputs and do not define the right one. B changes where the same text sits. C is more prose, from "
                 "which the same variation would come."),
        scenarios=(5,), points=("3.5:K1",),
        evidence=(Evidence(BP_API, "A few well-crafted examples (known as few-shot or multishot prompting) improve accuracy and consistency."),),
        qtype="fix", level="easy", principle="explicit",
        situation="changelog tidy-up capitalises after the colon in a third of runs",
        trap="vote across more runs or rewrite the guide as more rules",
    ),
    # ---- K2: test-driven iteration ----
    MCQ(
        id="Q3.5-04",
        q=("You are adding a `shipping_fee()` function to a checkout service. The fee has weight tiers (up to 1 kg, over 1 to 5 kg, over "
           "5 kg), free shipping above an order-value threshold, and an error for zero or negative weights. You want Claude Code to "
           "deliver a correct implementation with the least back-and-forth. Which approach is most effective?"),
        opts=("Write tests for tier boundaries, the threshold and bad weights first, then let Claude iterate to green.",
              "Describe the rules in a detailed prompt, then compare the finished function against the list by reading it.",
              "Have Claude implement the function first, then write tests from its code to confirm the behaviour it built.",
              "Have Claude implement the function in two separate sessions, then compare the two versions for differences."),
        ans=0,
        explain=("Tests written first define done independently of the code, and each failure tells Claude what to change. B leaves "
                 "the checking to a manual read. C writes the tests from the implementation, so they confirm whatever was built. D "
                 "compares two guesses with each other, and does not check either against the rules."),
        scenarios=(2,), points=("3.5:K2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 3.5 Knowledge 2 (tests written first, then iterate); no official page addresses tests-first versus tests-from-code.",
        qtype="choose", level="easy", principle="independent_check",
        situation="tiered shipping fee function with boundaries and invalid weights",
        trap="tests derived from the finished implementation",
    ),
    MCQ(
        id="Q3.5-05",
        q=("A developer asks Claude Code to fix a failing `test_prorate_refund` suite that runs only on the team's CI server. After each "
           "attempt, the developer replies with a summary such as \"the refund amounts are still slightly off\". Six rounds in, "
           "Claude has changed rounding, date arithmetic and the currency lookup, and 3 of 9 cases still fail. What is the most likely "
           "reason progress is slow?"),
        opts=("The suite is too large for Claude to read in one pass, so it works from the first few cases.",
              "Claude is told how the result looks, not which cases fail or what each one expected and got.",
              "Claude Code cannot repair tests that run on a CI server, only those that run on the developer's machine.",
              "The test names do not describe the checks well enough for Claude to infer what each case covers."),
        ans=1,
        explain=("A loop only converges when Claude sees the specific failures, so the failing assertions with expected and actual values "
                 "should be pasted. A is unsupported by the stem, which says it touched three areas. C describes a limit that does not "
                 "exist. D concerns naming, while the missing information is the actual output of the failing cases."),
        scenarios=(4,), points=("3.5:K2",),
        evidence=(Evidence("code:best-practices", "It makes the change, runs the check, and if something broke it reads the output and fixes it before running the check again."),),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="prorated refund fix stalls when failures are relayed as a vague summary",
        trap="blame suite size, CI location or test naming",
    ),
    MCQ(
        id="Q3.5-06",
        q=("A developer has written 12 tests for a discount engine before any code exists. Claude Code is asked to make them pass. "
           "Each round the developer pastes only the output of the one test being targeted. After three rounds, five tests are failing "
           "every time, but a different five each round, and the developer is losing track of what each change breaks. What is the "
           "most likely root cause?"),
        opts=("Claude cannot work on more than one failing test at a time, so regressions are expected.",
              "Each round runs in a fresh context, which discards what the earlier rounds established.",
              "Only one test's result is shared, so what each change breaks elsewhere stays hidden.",
              "A suite of 12 tests is too large to converge, and it should be split into smaller suites."),
        ans=2,
        explain=("Iteration works when the failures Claude sees show the effect of its last change on the whole suite, so the full "
                 "result of each run should be shared. A invents a one-test limit. B contradicts the stem, which describes a continuing "
                 "series of rounds. D treats a small suite as too big."),
        scenarios=(4,), points=("3.5:K2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 3.5 Knowledge 2 (share the test failures to guide each round); no official page addresses sharing partial versus full results.",
        qtype="diagnose", level="hard", principle="root_cause",
        situation="a different five of 12 tests fail each round when only one test's output is shared",
        trap="blame a one-test limit, fresh contexts or suite size",
    ),
    MCQ(
        id="Q3.5-07",
        q=("You asked Claude Code to interview you about a retry policy for an outbound email service you had never designed. After 14 "
           "questions about per-recipient limits, bounce handling and provider outages, it says it has enough to write the spec. You "
           "want the build to begin from a clean context and a written definition of done. What should you do next?"),
        opts=("Ask Claude to start coding in the same session, so that the interview's wording stays in context.",
              "Ask Claude to record the interview answers in CLAUDE.md so that every later session loads them.",
              "Run /compact and let the build start from the compacted interview in the same session.",
              "Have Claude write the spec to a file, then start a fresh session and build from that file."),
        ans=3,
        explain=("A spec file captures the answers and gives the build a written target, and a fresh session starts without the "
                 "interview's back-and-forth. A keeps the long interview in context. B puts a one-off design into a file that "
                 "loads on every task. C leaves a summary of the conversation in place of a spec."),
        scenarios=(2,), points=("3.5:K3",),
        evidence=(Evidence("code:best-practices", "start a fresh session to build from it, so the build begins with a clean context and a written definition of done."),),
        basis="docs",
        qtype="configure", level="easy", principle="explicit",
        situation="interview finished for an email retry policy and a build is about to begin",
        trap="build in the same session or store the answers in CLAUDE.md",
    ),
    MCQ(
        id="Q3.5-08",
        q=("A developer asked Claude Code to \"add retries to the job queue worker and handle every failure mode\". Claude added "
           "exponential backoff. In review, the team found that the jobs charge cards, so a duplicate run after a timeout is a serious "
           "risk, and failed jobs also need a dead-letter record. The developer has not worked on payment queues before and does not know which failure modes matter. They want to catch needs like these before coding next time. "
           "Which approach would best have surfaced them?"),
        opts=("Ask Claude to interview the developer about failures and duplicate runs before implementing.",
              "Use plan mode, so that Claude proposes a design and the developer approves it if it looks sound.",
              "Add \"consider duplicate runs and dead letters\" to the prompt of every future queue task.",
              "Ask Claude to list the failure modes it can think of and then implement every one of them."),
        ans=0,
        explain=("Questions to the developer bring out requirements that only the developer knows, such as card charges. B shows what "
                 "Claude assumed, and the developer can approve a plan without noticing what is missing. C is a fix for these two "
                 "cases and does not help with the next unknown. D relies on Claude's guesses about a system it cannot see."),
        scenarios=(4,), points=("3.5:K3",),
        evidence=(Evidence("code:best-practices", "Claude comes back with multiple-choice questions about the parts you haven't pinned down"),),
        qtype="evaluate", level="medium", principle="fit_for_purpose",
        situation="queue retries miss duplicate charges and dead-letter records",
        trap="plan mode or a fixed reminder instead of questions to the developer",
    ),
    MCQ(
        id="Q3.5-09",
        q=("A team runs Claude Code headless in CI each night to fix lint violations flagged by a fixed ruleset, then opens a PR. A "
           "colleague proposes adding the interview pattern, so that Claude asks questions about each violation before editing. The "
           "ruleset and its fixes are well understood, and nobody is present when the job runs. How should you evaluate the proposal?"),
        opts=("Adopt it: questions before every edit remove the risk of a wrong fix.",
              "Decline it: nobody is there to answer, and nothing here is new enough to need it.",
              "Adopt it, with Claude answering its own questions from the repository before it edits.",
              "Decline it: the interview pattern only works in plan mode and does not run headless."),
        ans=1,
        explain=("The pattern pays off when a developer is present and the domain is new to them; neither holds here. A adds waiting "
                 "for answers that no one can give. C removes what makes an interview useful, which is the developer's own knowledge. "
                 "D states a restriction that is not part of the pattern."),
        scenarios=(5,), points=("3.5:K3",),
        evidence=(Evidence("code:best-practices", "When you don't know exactly what you want yet, you don't have to work it all out before you prompt."),),
        basis="docs",
        qtype="evaluate", level="medium", principle="proportionate",
        situation="interview step proposed for an unattended nightly lint-fix job",
        trap="use an interactive pattern where nobody can answer",
    ),
    # ---- K4: one message vs sequential ----
    MCQ(
        id="Q3.5-10",
        q=("A dashboard has two open bugs: sessions go stale, and some users stay signed in after logout. The developer first asks Claude "
           "Code about the stale sessions, and it adds a cache TTL. The logout bug is raised next, Claude clears the cookie, and the "
           "stale sessions return. After three rounds of alternating, both symptoms still appear. Which next step is best "
           "to take?"),
        opts=("Keep alternating, but ask Claude to run the whole suite after each fix so a regression shows at once.",
              "Run /clear and report each bug again in its own message, in the original order.",
              "Describe both bugs in one message, with how each fix affects the other and what must hold.",
              "Fix the logout bug first, since a security problem should be settled before a stale cache."),
        ans=2,
        explain=("The two fixes touch the same session handling, so Claude needs both problems and their dependency at once to design "
                 "them together. A catches the regression but repeats the same one-at-a-time cycle. B restarts the sequence that "
                 "produced the flip-flop. D chooses an order, but any order has the same effect on the other bug."),
        scenarios=(2,), points=("3.5:K4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 3.5 Knowledge 4 (interacting problems in one message versus sequential fixes); no official page states the rule.",
        qtype="diagnose", level="medium", principle="root_cause",
        situation="session cache TTL and logout cookie fixes undo each other over three rounds",
        trap="keep alternating with a regression run or choose a priority order",
    ),
    MCQ(
        id="Q3.5-11",
        q=("Four items are open on an internal tools repo: a missing database index slowing the audit-log page, a mobile layout overflow "
           "on the settings screen, a misspelt label in the billing form, and an out-of-date base image in the Dockerfile. Each was "
           "reported by a different team and sits in a different part of the repo. How should you raise them with Claude Code?"),
        opts=("All four in one detailed message, so that Claude can plan the changes together.",
              "Two messages: the two user-facing items together, and the two infrastructure items together.",
              "Group by size: the two quick fixes in one message and each larger item in a message of its own.",
              "One at a time, checking each result before raising the next."),
        ans=3,
        explain=("Independent problems are best handled sequentially, so each change gets Claude's full attention and its result can "
                 "be checked on its own. A bundles unrelated work without any dependency to justify it. B and C group items by theme or "
                 "size, which has no bearing on whether the fixes affect each other."),
        scenarios=(4,), points=("3.5:K4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 3.5 Knowledge 4 and Skill 5 (independent issues are fixed sequentially); no official page states the rule.",
        qtype="choose", level="easy", principle="proportionate",
        situation="four unrelated tickets on an internal tools repo",
        trap="bundle by theme or size even though nothing interacts",
    ),
    MCQ(
        id="Q3.5-12",
        q=("After a dependency upgrade, a CI run fails in three places: a type error in `OrderMapper`, a runtime error in a checkout API "
           "test and a snapshot mismatch in the invoice report. All three stack traces pass through the upgraded `fetchCustomer` helper. The engineer pastes the "
           "three failures into one message with the request \"fix these\". Claude adds a cast in `OrderMapper`, and the other two "
           "failures change shape but remain. What is the most likely reason?"),
        opts=("The message does not say the failures share a cause, so each is fixed on its own.",
              "Three failures are too many for one message, and each should have been sent on its own.",
              "Type errors have to be fixed before runtime errors, and the message did not give that order.",
              "Snapshot mismatches cannot be repaired from a CI log and have to be regenerated by hand."),
        ans=0,
        explain=("Interacting problems need one detailed message that says how they relate; here that is the library's new nullable "
                 "return type, which the three fixes must handle consistently. B pushes toward the sequential approach that suits "
                 "independent problems. C invents an ordering rule. D is false, as a snapshot can be corrected from its diff."),
        scenarios=(5,), points=("3.5:K4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 3.5 Knowledge 4 and Skill 5 (a single detailed message for interacting issues); no official page states the rule.",
        qtype="diagnose", level="hard", principle="root_cause",
        situation="three CI failures after an upgrade pasted together with only fix these",
        trap="split the failures or invent a type-then-runtime order",
    ),
    # ---- S1: 2-3 concrete examples ----
    MCQ(
        id="Q3.5-13",
        q=("Claude Code is generating TypeScript models from a database schema. The prompt says \"convert column names to our camelCase "
           "convention\". Across runs, `user_id` becomes `userId` or `userID`, and `address_line_2` becomes `addressLine2` or "
           "`addressLine_2`. Which change to the prompt is most effective?"),
        opts=("Add a second sentence describing the convention in more detail, covering acronyms and trailing digits.",
              "Add three input and output pairs: a plain column, one with an acronym and one with a number suffix.",
              "Point Claude to the team's style guide file and ask it to follow that file closely.",
              "Have Claude convert the first ten columns, then tell it to continue in the same style for the rest."),
        ans=1,
        explain=("A few pairs that cover the awkward cases show the exact output, which prose keeps leaving open. A is more of the "
                 "wording that is already read in two ways. C adds another piece of prose to interpret. D uses Claude's own first "
                 "ten outputs as the pattern, so whichever way it chose becomes the rule."),
        scenarios=(2,), points=("3.5:S1",),
        evidence=(Evidence(BP_API, "**Diverse:** Cover edge cases and vary enough that Claude doesn’t pick up unintended patterns."),),
        qtype="configure", level="medium", principle="explicit",
        situation="user_id becomes userId or userID in generated TypeScript models",
        trap="describe the convention in more words or learn it from Claude's own output",
    ),
    MCQ(
        id="Q3.5-14",
        q=("A team has 60 recorded before-and-after pairs from a past manual conversion of release-note drafts into a fixed "
           "customer-facing form. An engineer prompts Claude Code to convert the next batch. A prose-only attempt gave inconsistent "
           "output, and the choices on the table are to paste all 60 pairs or to keep the prose. How should you evaluate them?"),
        opts=("Paste all 60 pairs, since each extra pair narrows the variation a little further.",
              "Keep the prose and add more rules, since 60 pairs would take up too much of the context.",
              "Use neither as they stand: pick a few varied pairs, awkward ones included.",
              "Paste the first 10 pairs in file order, as those came from the most recent conversion."),
        ans=2,
        explain=("A handful of relevant and varied pairs is what guides the transformation, and the awkward ones carry the most "
                 "information. A treats volume as the goal and buries the unusual cases. B returns to the prose that already produced "
                 "inconsistent results. D chooses by position in the file, which says nothing about coverage."),
        scenarios=(4,), points=("3.5:S1",),
        evidence=(Evidence(BP_API, "Include 3–5 examples for best results."),),
        community="Guide says 2-3 examples and the docs say 3-5; the question tests only that a few varied examples beat both extremes.",
        qtype="evaluate", level="medium", principle="proportionate",
        situation="60 recorded pairs versus prose for release-note conversion",
        trap="paste everything, or fall back to more rules",
    ),
    MCQ(
        id="Q3.5-15",
        q=("A CI step asks Claude Code to normalise product codes in a data file and gives three examples. `ab-12 ` becomes `AB-12`, "
           "`cd-07` becomes `CD-07`, and `ef-3 ` becomes `EF-3 `. Across runs, about half of the codes with a trailing space come out "
           "trimmed and half do not. What is the most likely root cause?"),
        opts=("Claude reads only the first example, and the third is ignored whenever a trailing space is present.",
              "Three examples are too few, and a larger set would settle the behaviour for trailing spaces.",
              "The file reader removes trailing spaces before Claude sees them in about half of the runs.",
              "The examples disagree about trailing spaces, so the output follows one of two valid readings."),
        ans=3,
        explain=("The first example trims the space and the third keeps it, so Claude has two consistent readings to follow. Examples "
                 "must agree with each other as well as cover the cases. A invents a rule about which example is read. B suggests more "
                 "examples, which would not help while they conflict. C assumes a reader fault that the stem gives no sign of."),
        scenarios=(5,), points=("3.5:S1",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 3.5 Skill 1 (examples must be consistent with one another); no official page states it.",
        qtype="diagnose", level="hard", principle="root_cause",
        situation="two of three product-code examples disagree about a trailing space",
        trap="add more examples instead of fixing the conflict",
    ),
    # ---- S2: tests first, covering behaviour, edge cases, performance ----
    MCQ(
        id="Q3.5-16",
        q=("You are about to ask Claude Code to write `dedupe_contacts()`, which merges duplicate rows in a contact list that can reach "
           "2 million rows and must finish within 60 seconds. You decide to write the tests first. Which test plan is best?"),
        opts=("Ordinary duplicates, an empty list and mixed-case near-duplicates, plus a 2-million-row timing test.",
              "Ordinary duplicates, an empty list and mixed-case near-duplicates; the 60-second limit is checked once the logic passes.",
              "Ordinary duplicates and a 2-million-row timing test; edge cases will appear as failures once real data runs through it.",
              "Ordinary duplicates at several sizes up to 2 million rows, with empty and mixed-case inputs left to code review."),
        ans=0,
        explain=("Only the first plan puts expected behaviour, edge cases and the performance requirement into the suite before any "
                 "code exists. B defers speed, so a slow solution can pass as complete. C leaves edge cases to be found in use. D "
                 "covers size but relies on review to catch the edge inputs."),
        scenarios=(2,), points=("3.5:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 3.5 Skill 2 (tests covering behaviour, edge cases and performance before implementation); no official page states it.",
        qtype="configure", level="easy", principle="explicit",
        situation="tests before a contact-deduplication function with a 60-second budget",
        trap="leave speed or edge cases out of the first suite",
    ),
    MCQ(
        id="Q3.5-17",
        q=("A CI job for a nightly export runs Claude Code's generated `build_report()`. All 38 tests pass, yet the job takes 14 minutes "
           "against a 2-minute budget, and an engineer who reads the code finds nested loops over the full row set. The tests were "
           "written before the implementation and check output values only. What is the most likely root cause?"),
        opts=("The CI runners are slower than the developer's machine on which Claude iterated.",
              "Speed was never expressed as a test, so a correct but slow solution counted as done.",
              "Claude Code prefers short code by default and writes loops in place of library calls.",
              "The 38 tests are too few; with 100 tests the slow code would have failed some of them."),
        ans=1,
        explain=("Claude stops when its checks pass, and none of them measured time. A would not account for the nested loops that "
                 "the engineer found. C is a guess about habits, not something the stem shows. D confuses count with coverage, since "
                 "more value checks would still pass on slow code."),
        scenarios=(5,), points=("3.5:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 3.5 Skill 2 (performance requirements in the suite); no official page states it.",
        qtype="diagnose", level="medium", principle="root_cause",
        situation="38 passing value tests and a report that takes 14 minutes",
        trap="blame slower runners or a low test count",
    ),
    MCQ(
        id="Q3.5-18",
        q=("Before any implementation exists, you ask Claude Code to draft tests for a new rate-card importer from the ticket. It returns "
           "24 tests. You disagree with six of the expected values, which you think come from a misreading of the ticket. What is "
           "the best next step?"),
        opts=("Start the implementation, and correct the six values later if they still fail.",
              "Delete the six disputed tests, and let the remaining 18 drive the implementation.",
              "Correct the six expectations with Claude now, then implement against the agreed suite.",
              "Implement against all 24, then ask Claude to explain which failures it thinks are test errors."),
        ans=2,
        explain=("The suite is the definition of done, so it should be right before it is used as a target. A builds code toward "
                 "values you believe are wrong. B removes cases and leaves their behaviour undefined. D asks Claude to decide which "
                 "expectations to trust, after it has already adjusted the code toward them."),
        scenarios=(4,), points=("3.5:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 3.5 Skill 2 (the suite as the agreed definition of done before implementation); no official page states it.",
        qtype="choose", level="medium", principle="explicit",
        situation="six of 24 drafted rate-card tests carry a misread expectation",
        trap="implement first and sort out disputed tests later",
    ),
    # ---- S3: interview in unfamiliar domains ----
    MCQ(
        id="Q3.5-19",
        q=("You asked Claude Code to interview you before it builds your first payment-provider webhook receiver. Its open questions, "
           "such as \"How should duplicate deliveries be handled?\", get the answer \"not sure\" nine times out of twelve, and the "
           "interview is stalling. What is the most effective change?"),
        opts=("End the interview and have Claude implement with its own defaults, then review the code.",
              "Tell Claude to ask fewer questions, limited to the three it considers most important.",
              "Answer each question with a best guess, and correct the guesses that prove wrong in review.",
              "Ask for each question as a few options, with what each option would mean for the receiver."),
        ans=3,
        explain=("Questions that offer concrete options let a newcomer choose without already knowing the answer, and the interview "
                 "keeps surfacing considerations. A returns to unexamined defaults. B trims the number of considerations surfaced. C "
                 "feeds guesses into the spec as if they were decisions."),
        scenarios=(4,), points=("3.5:S3",),
        evidence=(Evidence("code:best-practices", "Claude comes back with multiple-choice questions about the parts you haven't pinned down"),),
        qtype="fix", level="medium", principle="fit_for_purpose",
        situation="webhook interview stalls on open questions answered not sure",
        trap="drop the interview or fill the gaps with guesses",
    ),
    MCQ(
        id="Q3.5-20",
        q=("Before adding a job scheduler, a developer wrote: \"If anything is unclear, ask me before you start.\" Claude Code replied "
           "that nothing was unclear and wrote a scheduler with an in-process lock. In staging, with four instances running, jobs ran "
           "four times. The developer has never built distributed scheduling. What change to the request is most effective?"),
        opts=("Ask for an interview about scheduling and failure behaviour, run until a spec could be written.",
              "Replace the sentence with \"ask me anything you might need to know\", to make the trigger broader.",
              "Add \"the scheduler will run on several instances\" to the prompt, and ask for the same implementation.",
              "Switch to plan mode, so that Claude describes its approach before it changes any files."),
        ans=0,
        explain=("Making the interview the task means Claude must put its questions about the unfamiliar parts to the developer, "
                 "whatever it thinks it already knows. B is the same optional wording with a wider trigger. C fixes the one fact "
                 "the developer now knows, while the other unknowns stay hidden. D shows an approach built on the same assumptions."),
        scenarios=(2,), points=("3.5:S3",),
        evidence=(Evidence("code:best-practices", "Interview me until you could write the spec, then write it to SPEC.md."),),
        qtype="fix", level="hard", principle="root_cause",
        situation="optional ask-me-if-unclear leaves an in-process lock running four times",
        trap="widen the optional trigger or add the one known fact",
    ),
    MCQ(
        id="Q3.5-21",
        q=("A team has never run zero-downtime database migrations and wants Claude Code to add a migration step to its CI pipeline. "
           "The repository has no earlier migration scripts, and nobody can say which risks apply to them, such as locks on large "
           "tables or the rollback of a half-applied change. Which opening is best?"),
        opts=("Ask Claude to search the repository for how migrations are normally done here, and copy that.",
              "Ask Claude to interview the team about risks and constraints before it writes the step.",
              "Ask Claude for the standard migration step that most teams use, and adjust it in review.",
              "Ask Claude to write the step, plus a runbook of every risk it can think of, for reading later."),
        ans=1,
        explain=("In an unfamiliar domain, questions put to the team bring out the design considerations, such as locking and "
                 "rollback, before code exists. A looks for a pattern the repository does not contain. C imports another team's "
                 "assumptions. D produces the risks only after the step has been written around them."),
        scenarios=(5,), points=("3.5:S3",),
        evidence=(Evidence("code:best-practices", "Interview me until you could write the spec, then write it to SPEC.md."),),
        qtype="choose", level="easy", principle="fit_for_purpose",
        situation="first zero-downtime migration step with no existing scripts to learn from",
        trap="search the repo for a pattern that is not there or accept a generic default",
    ),
    # ---- S4: specific test cases for edge cases ----
    MCQ(
        id="Q3.5-22",
        q=("A migration script copies `orders` into a new table. Rows where `shipped_at` is NULL (about 8% of 1.2 million) end up with "
           "`shipped_at` set to 1970-01-01, and legacy rows holding `0000-00-00` crash the run. The developer's last message said "
           "\"handle bad dates properly\" and made things worse. Which next message is most effective?"),
        opts=("Say the script must be careful with dates, and ask Claude to check every date column again.",
              "Say that the 1970 values are wrong, and ask Claude to wrap each date conversion in a try/except.",
              "Give three cases: NULL gives NULL, `0000-00-00` gives NULL, a valid date is copied as it is.",
              "Paste the stack trace from the crash, and ask Claude to make the script stop failing."),
        ans=2,
        explain=("Specific inputs with the exact expected outputs define what \"properly\" means for each edge case. A repeats the "
                 "vague request. B stops the crash but leaves open what the new value should be, and could hide bad rows. D shows "
                 "where it failed, and not what the result should have been."),
        scenarios=(2,), points=("3.5:S4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 3.5 Skill 4 (specific input and expected-output cases for edge cases); no official page states it.",
        qtype="fix", level="medium", principle="explicit",
        situation="NULL shipped_at becomes 1970-01-01 and zero dates crash a migration",
        trap="repeat a vague instruction or suppress errors with try/except",
    ),
    MCQ(
        id="Q3.5-23",
        q=("Finance reports that invoice totals are off by one cent on about 1 in 300 invoices. Claude Code's rounding fix passed the "
           "developer's check on three sample invoices, and the discrepancies continued. The developer wants to pin the behaviour "
           "down before another attempt. Which input is most effective?"),
        opts=("Export 500 recent invoices with the totals the current code produces as the expected values.",
              "A written description of the rounding rule, with an instruction to apply it to every line item.",
              "The number of one failing production invoice, with a request to make that invoice's total correct.",
              "A few cases on half-cent amounts, a zero line and a credit, each with its exact total."),
        ans=3,
        explain=("Specific inputs at the boundaries, each with the exact expected output, define the edge-case behaviour and give "
                 "Claude something to run. A treats the buggy code's own output as the answer. B is prose, which is where the "
                 "ambiguity began. C fixes one invoice and leaves the cases around it unspecified."),
        scenarios=(5,), points=("3.5:S4",),
        evidence=(Evidence("code:common-workflows", "Claude can analyze your code paths and suggest tests for error conditions, boundary values, and unexpected inputs that are often overlooked."),),
        qtype="choose", level="medium", principle="explicit",
        situation="one-cent invoice differences on 1 in 300 after a fix checked on three samples",
        trap="use the buggy code's own output as the expected values",
    ),
    MCQ(
        id="Q3.5-24",
        q=("Claude Code fixed an off-by-one error in `days_in_range(start, end)` after the developer gave it three cases: 2025-03-01 to "
           "2025-03-31 returns 31, a one-day range returns 1, and a reversed range raises an error. Over the next two weeks, other "
           "changes broke the function twice before anyone noticed. How should the three cases have been kept so that the next "
           "breakage is caught when it happens?"),
        opts=("As tests in the repository's suite, so that they run on every later change.",
              "As comments above the function, so that later editors can see the intended results.",
              "As a rule in CLAUDE.md, so that Claude remembers the cases in later sessions.",
              "As a message re-sent to Claude Code each time somebody touches the function."),
        ans=0,
        explain=("Cases with example input and expected output become a check that runs without anyone remembering it. B and C are "
                 "text that still depends on someone reading it, and C reaches only sessions that involve Claude. D needs a person "
                 "to recall the step each time, which is how the two breakages went unnoticed."),
        scenarios=(4,), points=("3.5:K2",),
        evidence=(Evidence("code:best-practices", "Give Claude something it can run that comes back pass or fail."),),
        qtype="choose", level="easy", principle="deterministic",
        situation="three date-range cases are not kept as tests and the function breaks twice",
        trap="store the cases as comments, rules or messages instead of runnable tests",
    ),
    # ---- S5: interacting issues in one detailed message ----
    MCQ(
        id="Q3.5-25",
        q=("A list API sorts by `created_at` and returns an opaque cursor that encodes the last row's `created_at`. Claude Code changes "
           "the ORDER BY to `updated_at`, and the second page of results then repeats and skips rows, because the cursor still "
           "encodes `created_at`. The sort and the cursor must agree with each other. How should the developer raise the follow-up?"),
        opts=("Revert the sort change, ask for the cursor change, then ask again for the sort change.",
              "Describe the sort change, the cursor encoding and their dependency in one message.",
              "Ask only for the cursor fix, then see whether the sort order is also wrong afterwards.",
              "Open a new session for the cursor and keep the sort change in the current session."),
        ans=1,
        explain=("The two changes are coupled, so one detailed message lets Claude design them to agree. A and C handle them in turn "
                 "and invite a mismatch between the two. D separates them across sessions that cannot see each other's work."),
        scenarios=(2,), points=("3.5:S5",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 3.5 Skill 5 (interacting issues in one detailed message); no official page states the rule.",
        qtype="choose", level="medium", principle="explicit",
        situation="sort key changed while the pagination cursor still encodes the old key",
        trap="fix the pieces one after another across messages or sessions",
    ),
    MCQ(
        id="Q3.5-26",
        q=("A schema change renamed `customer.region` to `customer.sales_region` and made it nullable. The next CI run fails in four "
           "places: an ORM mapping, a report query, a fixture loader and an API serializer. Each log line cites the old name or a "
           "null error. An engineer plans to give Claude Code the failures one at a time, in the order CI printed them, re-running CI "
           "between each. How should you evaluate this plan?"),
        opts=("Sound: each failure is small, and focused messages give Claude the clearest view of each.",
              "Sound, provided CI is re-run after each message so that any new failure is caught early.",
              "Weak: all four stem from one schema change, so one message should carry all of them.",
              "Weak: the order should follow the dependency graph, so the ORM mapping is fixed first."),
        ans=2,
        explain=("The four failures come from one change and the fixes must be consistent with each other, so they interact and are "
                 "best described together. A and B treat the failures as independent, and the re-runs only find a mismatch after the "
                 "fact. D keeps the one-at-a-time sequence and changes only which item is first."),
        scenarios=(5,), points=("3.5:S5",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 3.5 Skill 5 (interacting issues in one detailed message); no official page states the rule.",
        qtype="evaluate", level="hard", principle="root_cause",
        situation="one renamed nullable column breaks an ORM, a query, a loader and a serializer",
        trap="feed the CI failures in print order",
    ),
    MCQ(
        id="Q3.5-27",
        q=("A developer has two tickets: report exports time out at 30 seconds, and duplicate invoices appear when clients retry. Logs "
           "show duplicates also follow 503 responses that arrive within 2 seconds, and last month a change to one HTTP client setting "
           "doubled the duplicates. Her plan is two separate requests to Claude Code: raise `client.timeout` for the first ticket, then "
           "change `client.retries` for the second. How should you evaluate this plan?"),
        opts=("Sound: these are separate tickets, and separate requests keep each change small enough to review.",
              "Sound: raising the timeout first removes the timeouts that trigger retries, and the retries can be handled after.",
              "Weak: both tickets come down to one problem, so a single change to the retry count and timeout would be enough.",
              "Weak: the two settings affect each other, so both fixes should be described together."),
        ans=3,
        explain=("The timeout and the retry count act on the same behaviour, as last month's change showed, so the fixes must be "
                 "designed together. A judges by ticket boundaries, not by whether the fixes interact. B overlooks the duplicates that "
                 "follow 503s, which a longer timeout does not touch. C merges two different causes into one change and still leaves "
                 "the duplicates unaddressed."),
        scenarios=(4,), points=("3.5:S5",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 3.5 Skill 5 (judging whether fixes interact); no official page states the rule.",
        qtype="evaluate", level="hard", principle="root_cause",
        situation="timeout and retry settings shared by report exports and duplicate invoices",
        trap="split by ticket although both fixes act on one retry path",
    ),
)
