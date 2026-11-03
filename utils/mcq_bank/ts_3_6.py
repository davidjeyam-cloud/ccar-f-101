"""Exam bank · TS 3.6. Original questions; see docs/MCQ_BANK_PLAN.md."""
from utils.mcq_sets import MCQ, Evidence

TS = "3.6"
BULLETS = {
    "K1": "The -p (--print) flag runs Claude Code non-interactively inside automated pipelines",
    "K2": "--output-format json and --json-schema enforce structured output in CI",
    "K3": "CLAUDE.md carries project context (testing standards, fixtures, review criteria) to CI-invoked Claude Code",
    "K4": "The session that wrote the code is a weaker reviewer of it than an independent review instance",
    "S1": "Running Claude Code in CI with -p so that no interactive input hangs the job",
    "S2": "Producing machine-parseable findings with json output and a schema, for inline PR comments",
    "S3": "Giving prior findings on a re-run and asking for only new or still-unaddressed issues",
    "S4": "Giving existing test files as context so generated tests do not repeat covered scenarios",
    "S5": "Documenting testing standards, valuable-test criteria and fixtures in CLAUDE.md",
}

QUESTIONS = (
    # ---- K1: -p / --print ----
    MCQ(
        id="Q3.6-01",
        q=("A merge gate on a CI runner with a clean checkout starts `claude --bare \"Check this branch for hard-coded internal "
           "hostnames\"` to get a fast, repeatable start. The step prints nothing and is cancelled at the 30-minute job limit; "
           "the runner has no terminal attached. What is the most effective change?"),
        opts=("Add `--max-turns 3` so that the run is forced to stop early.",
              "Keep `--bare` and set a shorter job timeout, so a stuck step fails sooner.",
              "Add `-p` so the prompt runs non-interactively and the answer is printed.",
              "Replace `--bare` with `--continue`, so the run picks up an earlier session."),
        ans=2,
        explain=("`--bare` only skips auto-discovery of hooks, MCP servers and CLAUDE.md for a repeatable start; it does not make the "
                 "session non-interactive, and `-p` is what prints the answer and returns control. A caps agentic turns but does "
                 "not change how the session starts. B turns a hang into a quicker failure with the same empty output. D reopens "
                 "an older conversation, and a clean checkout on a fresh runner holds none."),
        scenarios=(5,), points=("3.6:K1",),
        evidence=(Evidence("code:headless", "Add the `-p` (or `--print`) flag to any `claude` command to run it non-interactively."),
                  Evidence("code:headless", "Bare mode is useful for CI and scripts where you need the same result on every machine.")),
        qtype="fix", level="easy", principle="fit_for_purpose",
        situation="merge gate started with --bare prints nothing and hits the 30-minute job limit",
        trap="treat --bare or a shorter timeout as the non-interactive switch",
    ),
    MCQ(
        id="Q3.6-02",
        q=("A nightly job runs `claude -p \"Fix the lint errors in src/\"` on a runner. It exits 0 in under a minute, but the commit "
           "step finds no changed files on any night. The run's log shows Claude reading the files and proposing edits. What is the "
           "most effective fix?"),
        opts=("Pass `--allowedTools \"Read,Edit\"` so edits are not denied for lack of approval.",
              "Remove `-p`, so that Claude can ask for permission before it makes each edit.",
              "Say in the prompt that Claude has permission to edit files and should apply every change.",
              "Raise the turn limit with `--max-turns 20` so Claude has enough turns to finish the edits."),
        ans=0,
        explain=("In a `-p` run nobody can answer an approval prompt, so a call that needs approval is denied and the run carries "
                 "on; naming the tools in `--allowedTools` lets the edits happen. B brings back the interactive session that "
                 "hangs a pipeline. C is a prompt instruction, and permission is decided by the tool settings, not by what the "
                 "model is told. D fixes a limit that was never reached, since a run that hits it exits with an error."),
        scenarios=(5,), points=("3.6:K1",),
        evidence=(Evidence("code:headless", "Listing `Read` and `Edit` lets Claude read and edit files without asking for permission"),
                  Evidence("code:headless", "`claude -p` run, a call that needs approval is denied unless something approves it")),
        basis="docs",
        qtype="fix", level="medium", principle="root_cause",
        situation="lint-fix job exits 0 with no changed files because edit calls were denied",
        trap="ask Claude for permission in the prompt",
    ),
    MCQ(
        id="Q3.6-03",
        q=("A wrapper script runs `claude -p \"Apply the codemod to src/legacy\" --max-turns 6 > out.txt` and marks the CI step "
           "passed when out.txt contains the word \"done\". On some nights the run stops at its turn limit with the codemod half-applied, yet out.txt "
           "still has \"done\" in a progress line. How should the step decide whether the run succeeded?"),
        opts=("Require the last line of out.txt to be exactly \"done\" before passing.",
              "Instruct Claude in the prompt to print FAILED when it could not finish.",
              "Search out.txt for the words error, failed and incomplete as well.",
              "Branch on the exit status of `claude -p`; it is non-zero on failure."),
        ans=3,
        explain=("The exit status is a deterministic signal: Claude Code exits non-zero when the run fails, including when the "
                 "turn limit is reached. A, B and C all keep judging success from model-written text, which is a different "
                 "wording away from failing again. B also asks the model to report its own failure, the case where it may not."),
        scenarios=(5,), points=("3.6:K1",),
        evidence=(Evidence("code:headless", "Claude Code exits with code 0 on success and a non-zero code when the run fails, so your scripts can branch on the exit status."),
                  Evidence("code:cli-reference", "Exits with an error when the limit is reached.")),
        basis="docs",
        qtype="choose", level="medium", principle="deterministic",
        situation="half-applied codemod passes because a progress line says done",
        trap="judge success from words in the output",
    ),
    # ---- K2: --output-format json / --json-schema ----
    MCQ(
        id="Q3.6-04",
        q=("A dashboard needs, for every CI run of the PR reviewer, the session ID and what the run cost. The job calls "
           "`claude -p \"Review this PR\"` and the log holds only the review text. Which change gives a script those values in "
           "one machine-readable object?"),
        opts=("Ask in the prompt that the review ends with a line giving the session ID and the cost of the run.",
              "Add `--output-format json` and read the fields from the object printed at the end of the run.",
              "Add `--json-schema` with fields named `session_id` and `cost`, which Claude fills in itself.",
              "Parse the plain-text log for lines that mention the session and the cost."),
        ans=1,
        explain=("With `--output-format json` the run returns one object holding the result, the session ID and metadata such as "
                 "`total_cost_usd`. A asks the model to state values it does not hold. C makes the model write the numbers, "
                 "where a schema only shapes the answer it composes. D relies on text that the plain-text format never contains."),
        scenarios=(5,), points=("3.6:K2",),
        evidence=(Evidence("code:headless", "`json`: structured JSON with result, session ID, and metadata"),
                  Evidence("code:headless", "the response payload includes `total_cost_usd`")),
        qtype="choose", level="easy", principle="fit_for_purpose",
        situation="dashboard needs session ID and run cost per CI review",
        trap="have the model write run metadata or scrape the text log",
    ),
    MCQ(
        id="Q3.6-05",
        q=("A review job runs `claude -p \"$PROMPT\" --output-format json --json-schema \"$SCHEMA\"` and a script then runs "
           "`jq -r '.structured_output.findings[].message'`. About 1 run in 150 fails in jq with `Cannot iterate over null`. In "
           "those runs the JSON object has a `result` text but no `structured_output` key. What is the most likely root cause?"),
        opts=("The schema is too strict, so Claude Code rejects a few outputs and exits before it prints anything.",
              "These PRs had no issues, and Claude Code leaves out the field when the findings list is empty.",
              "Those runs ended without valid structured output, and the script never checks the field exists.",
              "The `format` keyword in the schema is not enforced, so some runs returned free text instead."),
        ans=2,
        explain=("When a run ends without valid structured output, for example because Claude declined the request, the response "
                 "has no `structured_output` field, so the script must test for it first. A fits an invalid schema, which fails "
                 "at start on every run and prints no object. B is wrong because an empty findings list is still valid output "
                 "and appears in the field. D confuses `format`, which only annotates a value, with whether the field is present."),
        scenarios=(5,), points=("3.6:K2",),
        evidence=(Evidence("code:headless", "If a run ends without valid structured output, for example because Claude declined the request, the response has no `structured_output` field."),
                  Evidence("code:headless", "Before your script uses `structured_output`, check that the field is present.")),
        qtype="diagnose", level="hard", principle="root_cause",
        situation="jq fails on 1 in 150 reviews where structured_output is absent",
        trap="blame the schema or empty findings instead of checking the field",
    ),
    MCQ(
        id="Q3.6-06",
        q=("The findings schema of a CI reviewer declares `fixed_by` as `{\"type\": \"string\", \"format\": \"email\"}` so the "
           "poster can mention the author. After a month, 3% of findings carry values such as `unknown` or `the author`, and "
           "the poster fails when it looks the author up. Claude Code raised no schema error. What is the most likely cause?"),
        opts=("`format` is treated as an annotation and not enforced, so strings that are not e-mail addresses pass.",
              "The schema was applied to the top-level keys only, so nested fields such as this one were never checked.",
              "These runs hit the turn limit, and output produced at that point skips schema validation.",
              "`email` is not a valid value for `format`, so Claude Code dropped the constraint without a message."),
        ans=0,
        explain=("Claude Code accepts `format`, such as `\"format\": \"email\"`, but treats it as an annotation and does not enforce it, "
                 "so the poster must check the value itself. B and C invent limits on validation that the stem gives no sign of. "
                 "D is refuted by the same behaviour: `email` is accepted, just not enforced."),
        scenarios=(5,), points=("3.6:K2",),
        evidence=(Evidence("code:headless", "Claude Code accepts schemas that use the `format` keyword, such as `\"format\": \"email\"`, but treats `format` as an annotation and doesn't enforce it."),),
        basis="docs",
        qtype="diagnose", level="hard", principle="root_cause",
        situation="author field with format email receives unknown and the author",
        trap="assume a schema keyword is enforced",
    ),
    # ---- K3: CLAUDE.md as CI context ----
    MCQ(
        id="Q3.6-07",
        q=("The CI reviewer keeps flagging generated files under `gen/` and the intentional raw SQL in `migrations/`, and "
           "developers dismiss about a third of its comments as noise. The team lead wants the review rules, what to skip and "
           "what counts as a defect, to guide CI runs and also developers' local sessions. Where should the rules go?"),
        opts=("In a personal `~/.claude/CLAUDE.md` on each developer's machine, loaded in all their sessions.",
              "In the wiki page for contributors, with a link in the PR template.",
              "In the `-p` prompt string, which is the only text Claude Code reads on a CI run.",
              "In the repository's `CLAUDE.md`, which is committed and loaded in both places."),
        ans=3,
        explain=("A project `CLAUDE.md` in the repository is checked out on the runner and read in local sessions (unless the run uses `--bare`), so one file "
                 "serves both. A lives on each developer's machine, and the runner is a different one. B is documentation for "
                 "people, which no Claude Code run loads. C is false: a CI run loads CLAUDE.md as well, and a long prompt string "
                 "would leave local sessions out."),
        scenarios=(5,), points=("3.6:K3",),
        evidence=(Evidence("code:github-actions", "Create a `CLAUDE.md` file in your repository root to define code style guidelines, review criteria, project-specific rules, and preferred patterns."),),
        qtype="choose", level="easy", principle="explicit",
        situation="reviewer flags generated files and intentional raw SQL as defects",
        trap="put the rules in a personal file, a wiki or only the pipeline prompt",
    ),
    MCQ(
        id="Q3.6-08",
        q=("An engineer put a rule in `CLAUDE.local.md` at the repository root: ignore TODO comments dated within the last 30 "
           "days. Her local `claude` sessions follow it. The CI reviewer, run with `claude -p` on a clean checkout of the same "
           "repository, flags every recent TODO. What is the most likely cause?"),
        opts=("`-p` runs do not load any CLAUDE.md files, so no project rules reach a CI run on a runner.",
              "`CLAUDE.local.md` is personal and meant to be gitignored, so the clean checkout lacks it.",
              "Rules about comments only take effect from a `CLAUDE.md` placed in the directory next to the code they cover.",
              "`CLAUDE.local.md` is loaded only in interactive sessions, so `-p` runs skip it."),
        ans=1,
        explain=("`CLAUDE.local.md` holds private preferences that the docs say to add to `.gitignore`, so it does not reach the runner; a rule "
                 "CI must follow belongs in the committed `CLAUDE.md`. A is false, since `claude -p` discovers and loads CLAUDE.md "
                 "as an interactive session does. C invents a placement rule. D is also false: the file loads alongside "
                 "`CLAUDE.md` wherever it exists, and here it does not exist."),
        scenarios=(5,), points=("3.6:K3",),
        evidence=(Evidence("code:memory", "Add `CLAUDE.local.md` to your `.gitignore` so it isn't committed."),
                  Evidence("code:headless", "Without it, `claude -p` discovers and loads them as an interactive session would")),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="TODO rule in CLAUDE.local.md is followed locally and ignored on the runner",
        trap="blame -p mode instead of the uncommitted file",
    ),
    MCQ(
        id="Q3.6-09",
        q=("The repository's CLAUDE.md has grown to 700 lines: the whole style guide, release history, an API reference, and "
           "four review rules that matter most (no request bodies in logs, no new `any` types, database calls only in `repo/`, "
           "reversible migrations). The CI reviewer applies those four rules in only about half of its runs. What is the most "
           "effective change?"),
        opts=("Move the CI job to a larger model, since the rules are already in the file.",
              "Repeat the four rules in capital letters at the top and at the bottom of the file.",
              "Cut the file down to the short, specific standards and criteria a CI run needs.",
              "Copy the four rules into a second CLAUDE.md under `.github/`, so they load twice."),
        ans=2,
        explain=("The file is read on every run, so a focused CLAUDE.md that holds only the standards and criteria keeps those "
                 "rules from being buried. A assumes the model is the weak part when the rules are lost in volume. B adds emphasis "
                 "to a file that is still long. D adds more text and a second place to keep in step."),
        scenarios=(5,), points=("3.6:K3",),
        evidence=(Evidence("code:github-actions", "Keep your `CLAUDE.md` concise, since Claude reads it on every run"),
                  Evidence("code:memory", "Files over 200 lines consume more context and may reduce adherence.")),
        qtype="fix", level="medium", principle="proportionate",
        situation="700-line CLAUDE.md buries four review rules, applied in half of runs",
        trap="bigger model, shouting or duplicating the rules",
    ),
    # ---- K4: session context isolation ----
    MCQ(
        id="Q3.6-10",
        q=("A team reviews AI-written changes in a second step: the same `claude` session that wrote the code is asked, \"Now "
           "review your changes.\" It approves almost everything, and human reviewers keep finding bugs that it passed. Which "
           "explanation fits best?"),
        opts=("The session still holds the reasoning behind the code, so it rarely questions it.",
              "A session cannot read its own earlier edits, so it reviews an out-of-date copy of the files.",
              "Reviewing needs a larger context window than writing, and the session has used most of its own.",
              "A model tuned for writing code cannot be prompted into reviewing any code at all, even its own."),
        ans=0,
        explain=("The generating session carries the assumptions behind its own decisions, which makes it a weaker reviewer than "
                 "an independent instance that has not seen how the code was written. B is false, since a session sees its own "
                 "edits. C blames space, when the reviewer fails in a short session too. D claims a limit that does not exist."),
        scenarios=(5,), points=("3.6:K4",),
        evidence=(Evidence("code:best-practices", "A second session is also the easiest independent reviewer you can get."),),
        qtype="evaluate", level="easy", principle="independent_check",
        situation="writing session asked to review itself approves nearly everything",
        trap="blame file visibility, window size or model tuning",
    ),
    MCQ(
        id="Q3.6-11",
        q=("A pipeline makes two separate `claude -p` calls per PR. The reviewer call is given the diff plus the generator's "
           "closing summary of about 150 words: \"edge cases covered: empty cart, expired coupon.\" In a test with 10 planted "
           "bugs, the reviewer found 7 when given only the diff and 3 when the summary was included. What is the most likely "
           "cause?"),
        opts=("The summary pushed part of the diff out of the reviewer's context window, so later hunks were skipped.",
              "The reviewer obeyed the summary's wording as an instruction, so it stopped reviewing after the listed cases.",
              "Two separate `claude -p` calls share one session by default, so the reviewer is not independent.",
              "The summary states what the generator thinks is handled, which anchors the reviewer to its blind spots."),
        ans=3,
        explain=("An independent review works because it does not inherit the author's assumptions; handing it the author's list of "
                 "covered cases brings those assumptions back. A cannot hold for 150 words. B is not what happened, because the "
                 "reviewer still reviewed, just toward the same gaps. C is false: each `claude -p` call starts a new session unless "
                 "it is told to continue one."),
        scenarios=(5,), points=("3.6:K4",),
        evidence=(Evidence("guide", ""),),
        community="guide-only: the anchoring mechanism is a guide judgment, no official page speaks to it",
        qtype="diagnose", level="medium", principle="independent_check",
        situation="reviewer given the generator's summary finds 3 of 10 planted bugs instead of 7",
        trap="blame context size or shared sessions rather than anchoring",
    ),
    MCQ(
        id="Q3.6-12",
        q=("To cut pipeline time, an engineer proposes one call instead of two: `claude -p \"Implement the ticket, then review "
           "your own diff and fix any problems\"`. A trial on 20 tickets shows 35% less wall-clock time, and the combined run "
           "reports \"no problems found\" on 19 of them. The separate reviewer step used to block 6 of the same 20. How should "
           "you evaluate the proposal?"),
        opts=("Adopt it, since it is faster for the same output, and add `--max-turns` to bound the run overall.",
              "Reject it: the review needs an instance that did not write the code, so keep two calls.",
              "Adopt it, and tell the merged run to be more critical when it reviews its own diff.",
              "Reject it, and move the merged call to a larger model so it finds what the reviewer found."),
        ans=1,
        explain=("The saving comes from dropping the independence that made the reviewer useful, as the 6 blocked tickets show. "
                 "An independent instance reviewing the diff is what catches them. A trades quality for speed and a turn limit "
                 "does not restore it. C asks for self-criticism inside the session that wrote the code. D assumes size, not "
                 "perspective, was the gap."),
        scenarios=(5,), points=("3.6:K4",),
        evidence=(Evidence("code:best-practices", "A second session is also the easiest independent reviewer you can get."),),
        qtype="evaluate", level="medium", principle="independent_check",
        situation="merged implement-and-review call is 35% faster and passes 19 of 20 that the reviewer blocked 6 of",
        trap="trade review independence for speed",
    ),
    # ---- S1: -p to prevent interactive hangs ----
    MCQ(
        id="Q3.6-13",
        q=("A Jenkins stage that generates unit tests runs `claude \"Write tests for src/billing/\"` on a build agent. Every run is "
           "ended only by the 45-minute stage timeout, with no files written, and the agent has no terminal attached. What is the "
           "most effective fix?"),
        opts=("Run it with `-p`, so the prompt runs non-interactively and the process exits.",
              "Raise the stage timeout to 90 minutes, to give Claude more time to finish the work.",
              "Add `--dangerously-skip-permissions`, so that no approval prompt blocks the run.",
              "Run the command under a pseudo-terminal, so the session can draw its screen."),
        ans=0,
        explain=("Without `-p` an interactive session waits for input; `-p` runs the prompt non-interactively and exits when the response is complete. B waits longer on "
                 "a process that never finishes. C removes approval prompts, but the session is still interactive and still "
                 "waits for input when it has finished. D gives the session a screen to wait on."),
        scenarios=(5,), points=("3.6:S1",),
        evidence=(Evidence("code:headless", "Add the `-p` (or `--print`) flag to any `claude` command to run it non-interactively."),),
        qtype="fix", level="easy", principle="root_cause",
        situation="Jenkins test-generation stage killed by its 45-minute timeout",
        trap="raise the stage timeout",
    ),
    MCQ(
        id="Q3.6-14",
        q=("A cron entry on a shared server runs `claude \"Summarise last week's merged PRs\" >> weekly.md` every Monday at 06:00. "
           "The file `weekly.md` stays empty, and `ps` shows a `claude` process from each of the last four Mondays still running. "
           "What is the most effective change?"),
        opts=("Wrap the command in `nohup`, so it no longer depends on a terminal session.",
              "Redirect stderr as well with `2>&1`, so that the failure message reaches `weekly.md`.",
              "Move the entry to 02:00, when the server is less busy.",
              "Add `-p` to the command, so each run prints its answer and exits."),
        ans=3,
        explain=("Without `-p` each run opens an interactive session and waits for input, which is why old processes pile up and "
                 "nothing is written. With `-p` the run prints its answer and exits. A detaches the same waiting session from a "
                 "terminal. B would capture a message that no failure produced. C changes the time, not the waiting."),
        scenarios=(4,), points=("3.6:S1",),
        evidence=(Evidence("code:headless", "Add the `-p` (or `--print`) flag to any `claude` command to run it non-interactively."),),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="weekly cron summary leaves four stuck claude processes and an empty file",
        trap="detach the process with nohup or move the schedule",
    ),
    MCQ(
        id="Q3.6-15",
        q=("A review script runs `claude -p \"Review the diff in pr.diff\" > review.txt`, then `claude --continue \"Reduce the "
           "findings to the five most severe\" > top5.txt`. The first command always finishes. The second sits until the job "
           "limit, and top5.txt is empty. What is the most likely cause?"),
        opts=("The follow-up exceeds the turn budget inherited from the first run, so it waits for a higher limit.",
              "The first command's output file is still open, so the second command waits for it to be closed.",
              "The second command has no `-p`, so it opens an interactive session that waits for input.",
              "A session from a `-p` run is discarded when it exits, so `--continue` has nothing to load."),
        ans=2,
        explain=("Every pipeline call needs `-p`, including a follow-up: `claude -p --continue` continues the earlier `-p` session "
                 "non-interactively. A invents an inherited budget, and a run that hits its turn limit exits with an error "
                 "rather than waiting. B is an ordinary shell concern that does not hold a process. D is wrong because "
                 "`claude -p --continue` includes sessions created by `-p` runs."),
        scenarios=(5,), points=("3.6:S1",),
        evidence=(Evidence("code:cli-reference", "`claude -p --continue` includes `-p`, SDK, and `/loop` sessions."),
                  Evidence("code:headless", "Add the `-p` (or `--print`) flag to any `claude` command to run it non-interactively.")),
        basis="docs",
        qtype="diagnose", level="hard", principle="root_cause",
        situation="follow-up claude --continue without -p sits until the job limit",
        trap="assume only the first command in a pipeline needs -p",
    ),
    # ---- S2: json + schema for inline PR comments ----
    MCQ(
        id="Q3.6-16",
        q=("Your bot posts review findings as inline PR comments, and its posting script needs each finding's file, line and "
           "text. Which schema passed to `--json-schema` lets the script work with no text parsing?"),
        opts=("An object with one required string field, `review`, that holds the complete text of the review.",
              "A `findings` array of objects with required `file`, `line` (integer), `severity` and `message`.",
              "An object with a `findings` array of strings, each one written in the form \"path:line message\" for parsing.",
              "An object with a boolean `approved` and a string `reason` that explains the decision in full text."),
        ans=1,
        explain=("Separate typed fields give the script what an inline comment needs without parsing, and `required` makes missing "
                 "ones a schema failure. A leaves the whole review as text to parse. C hides the location inside a string that "
                 "must be split again. D carries a verdict but no locations, so there is nothing to attach a comment to."),
        scenarios=(5,), points=("3.6:S2",),
        evidence=(Evidence("code:cli-reference", "Get validated JSON output matching a JSON Schema after the agent completes its workflow (print mode only)."),),
        qtype="configure", level="medium", principle="deterministic",
        situation="inline-comment poster needs file, line and message per finding",
        trap="a schema with one text field or locations packed into strings",
    ),
    MCQ(
        id="Q3.6-17",
        q=("A job fails the build when the review output contains the word \"critical\", found with `grep -i critical` on the "
           "`result` text from `--output-format json`. It now fails on reviews that say \"no critical issues found\", and "
           "developers re-run until it passes. What is the most effective fix?"),
        opts=("Add `--json-schema` with a `severity` on each finding, and fail on any `critical` finding.",
              "Tell Claude to use the word \"critical\" only when it reports a critical defect in the code it reviews.",
              "Extend the grep to skip lines that contain \"no critical\" before it fails the build.",
              "Run the review three times and fail only when at least two of the runs contain the word."),
        ans=0,
        explain=("A severity field in the schema makes the gate a plain comparison on data rather than a search through prose. B asks "
                 "the model to police its own wording, and C chases one phrasing at a time. D multiplies cost and still keys "
                 "on the same word."),
        scenarios=(5,), points=("3.6:S2",),
        evidence=(Evidence("code:cli-reference", "Get validated JSON output matching a JSON Schema after the agent completes its workflow (print mode only)."),
                  Evidence("code:headless", "The response includes metadata about the request (session ID, usage, etc.) with the structured output in the `structured_output` field."),),
        qtype="fix", level="medium", principle="deterministic",
        situation="build gate greps the word critical and fails on no critical issues found",
        trap="patch the keyword search instead of using a severity field",
    ),
    MCQ(
        id="Q3.6-18",
        q=("A poster script turns each item in `structured_output.findings` (file, line and message, all required by the schema) "
           "into an inline PR comment. In a week of 400 findings, 31 could not be attached because the file and line they name "
           "are not among the PR's changed lines, although every one passed schema validation. What is the most effective "
           "change?"),
        opts=("Tighten the schema so that `line` must be an integer of at least 1 and `file` a non-empty string.",
              "Switch to `--output-format stream-json` so that locations are checked while the output streams.",
              "Have the poster check each file and line against the PR's changes, sending misses to a summary.",
              "Add \"only report lines that exist in the changed files\" to the schema's `description` for `line`."),
        ans=2,
        explain=("A schema guarantees the shape of a finding, not that its location is true, so the poster has to check "
                 "locations in code and handle the misses. A would not have stopped the 31, since their lines were valid "
                 "integers. B changes delivery, not validity. D asks the model to be careful, with no check behind it."),
        scenarios=(5,), points=("3.6:S2",),
        evidence=(Evidence("code:cli-reference", "Get validated JSON output matching a JSON Schema after the agent completes its workflow (print mode only)."),
                  Evidence("code:headless", "but treats `format` as an annotation and doesn't enforce it.")),
        community="guide-only judgment on the limits of schema validation; the docs describe the flag, not this check",
        qtype="diagnose", level="hard", principle="deterministic",
        situation="31 of 400 schema-valid findings name lines outside the PR's changes",
        trap="expect the schema to guarantee a true location",
    ),
    # ---- S3: prior findings on re-runs ----
    MCQ(
        id="Q3.6-19",
        q=("A PR reviewer job runs on every push, each time on a fresh runner, and reviews the whole diff. A PR with 12 open "
           "findings gets about 12 new comments after every push, most restating earlier ones in different words, and "
           "developers have started to mute the bot. What is the most effective fix?"),
        opts=("Run the review only when the PR opens and when it is marked ready, not on every single push.",
              "Delete the bot's earlier comments before each run and post the new set of comments instead.",
              "Resume the previous run's session with `--continue`, so that it remembers what it already reported.",
              "Pass the earlier findings to the next run and tell it to report only new or unaddressed issues."),
        ans=3,
        explain=("Supplying the earlier findings, with an instruction to report only new or still-unaddressed issues, lets the "
                 "run skip what is already raised. A drops coverage of later commits. B removes the threads developers replied "
                 "in, and the new set still repeats itself. C cannot work, because each run starts on a fresh runner that holds "
                 "no earlier session."),
        scenarios=(5,), points=("3.6:S3",),
        evidence=(Evidence("guide", ""),),
        community="guide-only: no official page covers feeding earlier review findings into a re-run",
        qtype="fix", level="medium", principle="explicit",
        situation="12 open findings re-posted in new words after every push",
        trap="skip later pushes, delete comments or resume a session that is gone",
    ),
    MCQ(
        id="Q3.6-20",
        q=("To stop repeat comments, a team changes its reviewer to look only at the commits added since the last review. After "
           "three pushes, an issue flagged in the first review is still in the code, because a fix commit touched the wrong "
           "function, and the bot says nothing. How should you evaluate the approach?"),
        opts=("Sound: reviewing only increments is right, and this miss is a one-off from a wrong fix by the developer.",
              "Sound if combined with a higher `--max-turns`, which lets the reviewer re-check the older files.",
              "Flawed: review the whole PR each time, supplying prior findings, and report only new or open ones.",
              "Flawed: review the whole PR each time and delete every earlier comment before posting the new ones."),
        ans=2,
        explain=("An increment-only review never looks again at the code behind an old finding, so it cannot tell whether that "
                 "finding is still open. Supplying the earlier findings alongside the full PR lets the run keep the open ones "
                 "and add new ones. A treats a design gap as bad luck. B expects a turn limit to widen the scope. D repeats "
                 "everything and discards the old thread history."),
        scenarios=(5,), points=("3.6:S3",),
        evidence=(Evidence("guide", ""),),
        community="guide-only: re-run design for avoiding duplicate review comments",
        qtype="evaluate", level="hard", principle="preserve_information",
        situation="incremental-only review stays silent about a finding left unfixed by a wrong fix",
        trap="review only new commits to avoid duplicates",
    ),
    MCQ(
        id="Q3.6-21",
        q=("A reviewer is given earlier findings as a list of locations such as `src/cart.py:88` and told to skip them. A refactor "
           "commit moves code and shifts line numbers, and the next run reports three known issues as new while missing a "
           "different one that now sits at line 88. What should the prior-findings input contain instead?"),
        opts=("Each finding's file, a short description and its status, so Claude can match it to the current code.",
              "The same line numbers, with an instruction to treat any finding within 20 lines of one as a duplicate.",
              "A hash of each earlier finding, so identical findings can be recognised exactly.",
              "Only the count of earlier findings per file, so that the model knows how many to skip."),
        ans=0,
        explain=("A description lets the model match a finding to the code wherever it now sits, and the status says whether it "
                 "was addressed. B would also hide a real new issue near an old one. C works only for identical wording, and "
                 "findings are reworded between runs. D tells the model how many to skip without saying which."),
        scenarios=(5,), points=("3.6:S3",),
        evidence=(Evidence("guide", ""),),
        community="guide-only: what a prior-findings input should carry is an engineering judgment",
        qtype="choose", level="medium", principle="preserve_information",
        situation="known issues re-reported after a refactor moves line numbers",
        trap="identify earlier findings by line number or hash",
    ),
    # ---- S4: existing tests in context ----
    MCQ(
        id="Q3.6-22",
        q=("A CI step pipes only `src/invoice/discount.py` into `claude -p` with the prompt \"Write unit tests for this module.\" "
           "Reviewing last week's output, 12 of the 30 new tests repeat scenarios already in `tests/test_discount.py`, with the "
           "same inputs and expected values. What is the most effective fix?"),
        opts=("Ask for fewer tests, because fewer generated tests means fewer repeats.",
              "Add a CI step that deletes any new test whose function name already exists in the test suite.",
              "Include `tests/test_discount.py` as input and ask only for scenarios it does not cover.",
              "Run the generation twice and keep just the tests found in both of the runs."),
        ans=2,
        explain=("The generator cannot avoid scenarios it has never seen, so the existing tests go into its context together with an "
                 "instruction to skip them. A shrinks the output without targeting repeats. B compares names, and the duplicates "
                 "here differ in name but not in inputs. D keeps the commonest tests, which are the ones already written."),
        scenarios=(5,), points=("3.6:S4",),
        evidence=(Evidence("guide", ""),),
        community="guide-only: giving existing tests as context to avoid duplicate generated scenarios",
        qtype="fix", level="easy", principle="explicit",
        situation="12 of 30 generated tests repeat scenarios in the existing discount tests",
        trap="trim volume or compare names instead of showing the existing tests",
    ),
    MCQ(
        id="Q3.6-23",
        q=("Test generation runs in CI for a monorepo with 300 test files, too many to put into a single run. For a change to "
           "`payments/refund.py`, the output should not repeat scenarios already tested. Which existing material should go into "
           "context?"),
        opts=("The test files that cover `payments/refund.py`, plus the fixtures they use.",
              "The project-wide coverage percentage, so Claude knows how much is already tested.",
              "All 300 test files joined together, cut off where the context fills up.",
              "The names of the five test files changed most recently anywhere in the monorepo."),
        ans=0,
        explain=("The tests for the module being changed are what show which scenarios already exist, and the fixtures show what is "
                 "available to reuse. B gives a number with no scenarios in it. C fills the context with unrelated tests and cuts "
                 "arbitrarily. D selects by recency, which has no link to the module under test."),
        scenarios=(5, 2), points=("3.6:S4",),
        evidence=(Evidence("guide", ""),),
        community="guide-only: choosing which existing tests to supply is an engineering judgment",
        qtype="choose", level="medium", principle="proportionate",
        situation="refund module change in a 300-test-file monorepo needs context to avoid duplicates",
        trap="supply a coverage number, everything or the most recently changed tests",
    ),
    MCQ(
        id="Q3.6-24",
        q=("A CI job gives `claude -p` the module and `tests/test_refund.py` under the heading \"existing tests, for reference\", "
           "and asks for \"comprehensive tests for this module\". Of the 25 tests generated, 9 repeat scenarios that the supplied "
           "file already covers. What is the most effective change?"),
        opts=("Supply the existing tests a second time, placed after the source file, in case they were overlooked.",
              "Tell the run to propose only scenarios the supplied tests do not cover, and name those skipped.",
              "Move the job to a larger model, which will notice the overlap with the supplied tests by itself.",
              "Cut the supplied tests down to their function names, which are shorter and easier to scan."),
        ans=1,
        explain=("The tests are in context, but nothing tells the run what to do with them, and \"comprehensive\" invites restating known "
                 "cases. An explicit instruction to cover only what is missing turns the context into a filter. A repeats the "
                 "same unframed material. C assumes capability is the gap. D removes the inputs and expected values that show "
                 "which scenarios are covered."),
        scenarios=(5,), points=("3.6:S4",),
        evidence=(Evidence("guide", ""),),
        community="guide-only: giving existing tests as context and instructing the run to avoid covered scenarios",
        qtype="fix", level="medium", principle="explicit",
        situation="existing tests supplied for reference but the prompt asks for comprehensive tests",
        trap="more context or a bigger model instead of an explicit skip-covered instruction",
    ),
    # ---- S5: testing standards in CLAUDE.md ----
    MCQ(
        id="Q3.6-25",
        q=("Developers use Claude Code locally, and three CI jobs use `claude -p`, to generate tests. About 70% of the new tests "
           "build customers from raw dict literals, although `conftest.py` provides `make_customer()` and `make_order()` "
           "fixtures. What is the most effective fix?"),
        opts=("Describe the fixtures, and when to use each, in the repository's `CLAUDE.md`.",
              "Copy a sentence about the fixtures into the prompts of each of the three CI jobs.",
              "Put all of `conftest.py` into each prompt and tell Claude to reuse whatever it finds.",
              "Add a CI step that rejects any generated test which contains a raw dict literal."),
        ans=0,
        explain=("`CLAUDE.md` is read by every run, local and CI, so one description of the fixtures steers all of them. B covers "
                 "only the CI jobs and has to be kept in step in three places. C leaves out when each fixture should be used and "
                 "still covers CI only. D rejects after generation, and does not improve the tests that Claude writes."),
        scenarios=(5, 2), points=("3.6:S5",),
        evidence=(Evidence("code:github-actions", "Create a `CLAUDE.md` file in your repository root to define code style guidelines, review criteria, project-specific rules, and preferred patterns."),),
        qtype="fix", level="easy", principle="explicit",
        situation="70% of generated tests ignore make_customer and make_order fixtures",
        trap="repeat fixture hints in each CI prompt or reject after generation",
    ),
    MCQ(
        id="Q3.6-26",
        q=("Tests that the CI job generated for a pricing module pass, but a review of 60 of them finds about 40% assert that a getter returns what "
           "the constructor stored or re-check library behaviour, and none covers rounding or negative quantities. The team "
           "wants fewer low-value tests without capping the count. What is the most effective change?"),
        opts=("Require at least 90% line coverage from the generated tests as a pipeline check before the PR can merge.",
              "Tell Claude in each prompt to write only good tests and to avoid tests that are not valuable.",
              "State in `CLAUDE.md` what makes a test worth writing, such as boundary and error cases, and what to skip.",
              "Limit the run with `--max-turns 4`, so that fewer tests are produced by each run of the job in the pipeline."),
        ans=2,
        explain=("Stating the criteria for a valuable test, and the cases to skip, gives the generator the standard it was missing. "
                 "A rewards trivial getter tests, which raise line coverage cheaply. B names no criterion. D cuts the count "
                 "without changing which tests get written."),
        scenarios=(5,), points=("3.6:S5",),
        evidence=(Evidence("guide", ""),),
        community="guide-only: criteria for a valuable test are the guide's judgment; the docs only say CLAUDE.md holds standards",
        qtype="fix", level="medium", principle="explicit",
        situation="40% of generated pricing tests are trivial getter and library checks",
        trap="coverage threshold, vague prompt wording or a turn cap",
    ),
    MCQ(
        id="Q3.6-27",
        q=("A test-generation job changed from `claude -p \"Add tests for the changed files\"` to `claude --bare -p \"Add tests "
           "for the changed files\"` to start faster; `ANTHROPIC_API_KEY` is set on the runner. The repository's `CLAUDE.md` lists the fixtures and "
           "test standards, and the team wants it to stay their single source. Since the change, generated tests ignore the fixtures. What is the most "
           "likely cause?"),
        opts=("`--bare` limits the model to a shorter context, so the long fixtures list no longer fits.",
              "`-p` and `--bare` conflict, so the run falls back to built-in defaults for test style.",
              "`--bare` removes the model's access to the repository's files, so it cannot see `conftest.py`.",
              "`--bare` skips discovery of CLAUDE.md, so the standards are not loaded; stop using it here."),
        ans=3,
        explain=("Bare mode skips auto-discovery of hooks, MCP servers and CLAUDE.md, so the file that held the fixtures and "
                 "standards is never read; dropping `--bare` here restores it as the single source; the alternative is to keep "
                 "`--bare` and pass the file with `--append-system-prompt-file`, which makes a second copy. A and B invent "
                 "limits the docs do not describe, since `--bare` is meant to be combined with `-p`. C is wrong because bare "
                 "mode skips auto-discovery, not the file tools."),
        scenarios=(5,), points=("3.6:S5", "3.6:K3"),
        evidence=(Evidence("code:headless", "Add `--bare` to reduce startup time by skipping auto-discovery of hooks, skills, custom commands, subagents, installed plugins, MCP servers, auto memory, and CLAUDE.md."),),
        basis="docs",
        qtype="diagnose", level="hard", principle="root_cause",
        situation="adding --bare to a test-generation job stops generated tests following CLAUDE.md fixtures",
        trap="blame context length or flag conflicts instead of skipped CLAUDE.md discovery",
    ),
)
