"""Exam bank · TS 3.4. Original questions; see docs/MCQ_BANK_PLAN.md."""
from utils.mcq_sets import MCQ, Evidence

TS = "3.4"
BULLETS = {
    "K1": "Plan mode suits complex work: large-scale changes, several valid approaches, architectural decisions, many files",
    "K2": "Direct execution suits simple, well-scoped changes such as one validation check in one function",
    "K3": "Plan mode lets Claude explore the code and design before committing, which prevents costly rework",
    "K4": "The Explore subagent isolates verbose discovery output and returns a summary to protect the main context",
    "S1": "Choosing plan mode for architectural work: restructuring, large library migrations, integration approaches with different infrastructure",
    "S2": "Choosing direct execution for well-understood changes with clear scope, such as a single-file fix with a clear stack trace",
    "S3": "Using the Explore subagent for verbose discovery phases so multi-phase tasks do not exhaust the context window",
    "S4": "Combining plan mode for investigation with direct execution for implementation of the planned approach",
}

QUESTIONS = (
    # ---- K1: plan mode for complex work ----
    MCQ(
        id="Q3.4-01",
        q=("A platform team asks Claude Code to move 40 services from a homegrown retry helper to a shared resilience library. "
           "The library offers two integration styles, a decorator at each call site or a wrapped client, and they treat timeouts "
           "differently. In the last migration the agent edited directly, picked decorators in 14 files, and 9 services then failed "
           "integration tests because their timeouts are set per client. Rolling back took two days. How should the team start the next one?"),
        opts=("Run it directly again, with an instruction to run the test suite after every file edit.",
              "Split it into 40 direct requests, one per service, each with its own test run.",
              "Use plan mode to compare both styles against the services before any edit.",
              "Run it directly with checkpoints on, so a wrong style can be rewound file by file."),
        ans=2,
        explain=("The costly step was a design choice made while editing, and plan mode lets Claude read the services and weigh both "
                 "styles before anything changes. A finds the wrong style only after edits have started. B makes the style choice "
                 "40 times, so services can end up on different styles. D makes undoing cheaper but leaves the choice no better informed."),
        scenarios=(2,), points=("3.4:K1",),
        evidence=(Evidence("code:permission-modes", "Plan mode tells Claude to research and propose changes without making them."),),
        qtype="choose", level="medium", principle="fit_for_purpose",
        situation="retry-helper migration where decorators broke per-client timeouts in 9 of 40 services",
        trap="add a test run after every edit",
    ),
    MCQ(
        id="Q3.4-02",
        q=("A developer asks Claude Code to \"add audit logging to the platform\" and lets it edit with no planning step. After 25 minutes "
           "it has changed 17 files across three services and introduced a new event format. The reviewer rejects the pull request "
           "because the data team already maintains an event format that three other services use. A colleague later finished the "
           "same ticket in two hours using that format. What most likely explains the rejected result?"),
        opts=("The task left design choices open, and no step had Claude explore and propose before editing.",
              "Claude lost the existing event format once the session passed the middle of its context window.",
              "Auto-accepted edits skip the check where Claude compares new code with existing conventions.",
              "Three services in one request is too much for one session, so each needs its own run."),
        ans=0,
        explain=("An open-ended, cross-service request with several defensible designs needs exploration and a reviewed approach before "
                 "edits, and nothing in the stem shows that step. B and C invent causes: the stem shows no context loss and no "
                 "such convention check exists. D would split the work, but three separate runs would each invent their own format."),
        scenarios=(4,), points=("3.4:K1",),
        evidence=(Evidence("code:common-workflows", "Claude reads files and proposes a plan but makes no edits until you approve."),),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="audit logging added across three services duplicates an event format the data team owns",
        trap="blame context loss or split the task by service",
    ),
    MCQ(
        id="Q3.4-03",
        q=("A teammate argues that plan mode is only for changes that touch dozens of files, so a ticket for cursor-based pagination on "
           "the orders endpoint should go straight to direct execution because it touches 3 files. The ticket says only \"add "
           "pagination\". Cursor and offset paging would both satisfy it, and they change what the mobile app and two partner "
           "integrations must send. How should you evaluate the rule?"),
        opts=("Sound: a three-file diff is small, so the cost of rework is low whichever style Claude picks.",
              "Sound if the prompt lists the three files, because a named scope settles the design question.",
              "Flawed: plan mode should be the default for every ticket so that no edit is ever unreviewed.",
              "Flawed: two valid designs that affect callers differently call for a plan whatever the size."),
        ans=3,
        explain=("The guide ties plan mode to multiple valid approaches and wider effects, not to diff size, and a wrong contract choice "
                 "here means rework in three consumers. A treats file count as a measure of rework. B is wrong because naming files "
                 "fixes where edits go and not which design is used. C swaps one blanket rule for another and would plan trivial tickets too."),
        scenarios=(4,), points=("3.4:K1",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 3.4 Knowledge 1 names multiple valid approaches as a reason for plan mode; no official page ranks size against design choice.",
        qtype="evaluate", level="hard", principle="proportionate",
        situation="three-file pagination ticket with cursor and offset both acceptable to API consumers",
        trap="decide the mode by file count",
    ),
    # ---- K2: direct execution for simple changes ----
    MCQ(
        id="Q3.4-04",
        q=("Support reports that entering -3 as the quantity on the order form drives the total below zero. The ticket asks for "
           "quantities under 1 to be refused inside `validate_line_item()` in `orders/validators.py`, with the existing error format, and a "
           "failing test is already in the repository. Which way of working with Claude Code is the most effective here?"),
        opts=("Enter plan mode first, so the one-line condition is reviewed before it is written.",
              "Describe the change and the failing test, and let Claude implement it directly and run the test.",
              "Send an Explore subagent to find every caller of the validator, then add the check in the main conversation.",
              "Ask Claude to propose two validation designs and choose between them before writing the check."),
        ans=1,
        explain=("One clearly stated condition in one function, with a test to confirm it, leaves nothing to design. A adds a review "
                 "step to a change that has no choices in it. C reads callers that the change does not affect. D invents alternatives "
                 "when the ticket already states the behaviour."),
        scenarios=(2,), points=("3.4:K2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 3.4 Knowledge 2 gives a single validation check in one function as the example for direct execution.",
        qtype="choose", level="easy", principle="proportionate",
        situation="negative quantity accepted on the order form, one validator and a failing test",
        trap="plan mode first for a one-condition change",
    ),
    MCQ(
        id="Q3.4-05",
        q=("A pipeline runs `claude -p` on each failing pull request to fix lint errors such as import order and trailing whitespace, "
           "about 90 runs a day. Most runs touch one file and a few touch up to five, and each is verified by re-running the linter. "
           "Nobody watches the runs. An engineer proposes switching every run to plan mode \"so changes are reviewed first\". "
           "How should you evaluate the proposal?"),
        opts=("Keep direct execution: the fixes are scoped and mechanical, and the linter verifies them.",
              "Adopt it, and have a second Claude session approve each plan before the first one edits anything.",
              "Adopt it for runs that touch more than one file, and keep the single-file runs direct.",
              "Adopt it for the first month, then switch to direct execution once the plans look consistent."),
        ans=0,
        explain=("The changes are well scoped and have a deterministic check, and an unattended run has nobody to read a plan. B adds "
                 "another model as the reviewer, which is cost without judgment the linter lacks. C counts files, but five import-order "
                 "fixes are as mechanical as one. D pays for a month of plans that nobody reads to reach the same conclusion."),
        scenarios=(5,), points=("3.4:K2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: whether a mechanical fix needs a plan is a judgment the guide states through its direct-execution examples; no official page ranks it.",
        qtype="evaluate", level="medium", principle="proportionate",
        situation="unattended lint-fix runs proposed for plan mode",
        trap="plan mode approved by a second model or by file count",
    ),
    MCQ(
        id="Q3.4-06",
        q=("A team made plan mode mandatory for every Claude Code task. A review of 60 tasks found that 41 were single-function changes "
           "such as renaming a constant, adding a validation or fixing a message; their plans restated the prompt and took about "
           "10 minutes to read and approve. In the other 19 tasks the plan was changed during review. Which change to the policy "
           "is most effective?"),
        opts=("Keep plan mode for every task, but ask Claude to limit each plan to five lines or fewer.",
              "Remove plan mode, and review all 60 kinds of change as diffs once they have been made.",
              "Run scoped single-function changes directly, and keep plan mode for open-ended work.",
              "Make plan mode optional for engineers who have more than a year of experience on the codebase."),
        ans=2,
        explain=("The data shows the plan paid off only where there was something to decide, so the mode should follow the task. A "
                 "shortens the plans but still pays an approval step for tasks with nothing to decide. B drops the step that corrected "
                 "19 tasks before any edit. D picks by seniority instead of by what the task is."),
        scenarios=(4,), points=("3.4:K2", "3.4:S2"),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 3.4 Knowledge 2 (direct for simple changes) read against Knowledge 1; the policy trade-off is a guide judgment.",
        qtype="fix", level="medium", principle="proportionate",
        situation="mandatory plan mode where 41 of 60 tasks were single-function changes",
        trap="shorten the plans instead of skipping them",
    ),
    # ---- K3: plan mode enables safe exploration ----
    MCQ(
        id="Q3.4-07",
        q=("A new hire asks Claude Code to \"make invoice timestamps UTC\". In default mode it edits the writer module, one template and "
           "four callers. The change passes its tests, but month-end reconciliation fails: a batch job in the same repository reads the "
           "exported files and expects local time, and Claude never opened it. Which approach would most likely have avoided "
           "the failure?"),
        opts=("Ask Claude to explain each edit as it makes it, so the reviewer sees its reasoning.",
              "Run the change in a separate git worktree, so production code is untouched until the merge.",
              "Use direct execution with `/rewind` ready, so each edit can be undone if a problem turns up.",
              "Start in plan mode so Claude can trace what consumes the files before it edits."),
        ans=3,
        explain=("Plan mode lets Claude read the code and run exploratory commands while nothing is edited, so the reconciliation job can "
                 "be found before any change exists. A explains edits that are already being made. B isolates the work, yet the "
                 "tests would pass and the same change would be merged. C makes undoing cheap, but the failure only appears at "
                 "month-end, long after the edits."),
        scenarios=(2,), points=("3.4:K3",),
        evidence=(Evidence("code:permission-modes", "Claude reads files, runs shell commands to explore, and writes a plan, but does not edit your source."),),
        qtype="fix", level="medium", principle="fit_for_purpose",
        situation="UTC timestamp change breaks a reconciliation job that reads the exports",
        trap="isolate in a worktree or rely on rewind instead of exploring first",
    ),
    MCQ(
        id="Q3.4-08",
        q=("In plan mode, Claude proposes splitting the `events` table and rewriting the ingest job. Step 4 renames the `ts` column, which "
           "12 analytics dashboards in `queries/` read, and steps 2 and 3 are written around the new name. Nothing has been edited yet. "
           "What is the best next step?"),
        opts=("Approve the plan, then ask Claude to revert step 4 as soon as the dashboards start failing.",
              "Choose \"No, keep planning\" and tell Claude to keep `ts` and adapt steps 2 and 3.",
              "Leave plan mode and have Claude run steps 1 to 3 directly while step 4 waits for the analytics team.",
              "Approve with manual approval of each edit, and reject the rename when it appears."),
        ans=1,
        explain=("Before any edit the plan is the cheapest place to change the design, and steps 2 and 3 depend on the rename, so Claude "
                 "should revise them too. A and D let edits build on the new name first, so removing step 4 later means rework in steps "
                 "2 and 3. C runs steps 2 and 3 as written, and they assume the renamed column."),
        scenarios=(4,), points=("3.4:K3",),
        evidence=(Evidence("code:permission-modes", "No, keep planning: stay in plan mode and tell Claude what to change."),),
        qtype="choose", level="medium", principle="preserve_information",
        situation="plan renames a column that 12 dashboards read, with later steps built on the new name",
        trap="approve and reject the one edit later",
    ),
    MCQ(
        id="Q3.4-09",
        q=("Your team wants every new terminal session in the `payments` repository, on every teammate's machine, to start in plan mode during "
           "onboarding week, so newcomers explore the code before anything is edited. The setup must not rely on each person's own "
           "configuration. What is the most direct way to do it?"),
        opts=("Add `Write` and `Edit` to the `deny` list in the project's `.claude/settings.json`.",
              "Set `defaultMode` to `plan` in the project's checked-in `.claude/settings.json`.",
              "Write \"start every session in plan mode\" at the top of the project's CLAUDE.md file.",
              "Ask each teammate to start Claude with `--permission-mode plan` from a shell alias."),
        ans=1,
        explain=("A project setting for the default permission mode applies to everyone who opens the repository, and plan mode still lets "
                 "them approve a plan and edit afterwards. A blocks edits permanently, so nobody could implement after approving. C is an "
                 "instruction, and an instruction cannot change a permission mode. D depends on each person's own shell setup."),
        scenarios=(2,), points=("3.4:K3",),
        evidence=(Evidence("code:permission-modes", "To make plan mode the default for a project's terminal sessions, set `defaultMode` to `plan` in `.claude/settings.json`"),),
        basis="docs",
        qtype="configure", level="easy", principle="fit_for_purpose",
        situation="onboarding week sessions in one repository should start read-only for exploration",
        trap="deny edit tools or write the rule into CLAUDE.md",
    ),
    # ---- K4: Explore subagent isolates verbose discovery ----
    MCQ(
        id="Q3.4-10",
        q=("A developer asks Claude Code in the main conversation to \"find every place we build a Money object and list the rounding each "
           "uses\". Claude searches and reads 140 files. The context meter then shows 85% full, and auto-compaction runs when the "
           "developer asks for a follow-up edit. The follow-up answer cites 30 of the roughly 110 sites that were found. What is the "
           "most likely root cause?"),
        opts=("Grep returns too few matches in a large repository, so Claude had to fall back on reading files.",
              "Auto-compaction summarises too aggressively and should be turned off for long investigations.",
              "The context window is too small for a repository this size, so a bigger one is needed.",
              "Discovery ran in the main conversation, so file contents filled it rather than a subagent."),
        ans=3,
        explain=("Verbose discovery belongs in a subagent, whose context absorbs the file reads and returns only a summary. A is not "
                 "supported, since roughly 110 sites were found. B treats the symptom, and with the context already full some "
                 "detail would still be lost. C delays the problem with a bigger window but leaves unneeded file contents in the main conversation."),
        scenarios=(2,), points=("3.4:K4",),
        evidence=(Evidence("code:sub-agents", "Use one when a side task would flood your main conversation with search results, logs, or file contents you won't reference again: the subagent does that work in its own context and returns only the summary."),),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="Money rounding audit reads 140 files in the main conversation and loses 80 sites at compaction",
        trap="turn off compaction or buy a bigger window",
    ),
    MCQ(
        id="Q3.4-11",
        q=("A developer delegates \"find why checkout totals drift and patch it\" to the built-in Explore subagent. It returns a clear "
           "diagnosis naming `apply_discount()`, but the working tree is unchanged and no patch exists. What is the most likely "
           "explanation?"),
        opts=("Explore is read-only: it reports findings, and the main conversation makes the edit.",
              "The patch was written in a temporary worktree that was cleaned up when Explore finished.",
              "Explore only produces edits when its thoroughness level is set to very thorough.",
              "Explore returns edits only after the developer approves its plan in the main conversation."),
        ans=0,
        explain=("Explore is built for searching and analysing code with write tools denied, so a diagnosis with no patch is its normal "
                 "result. B invents a worktree step, and Explore has no write tools to make a patch anywhere. C has no basis in the "
                 "docs, where the thoroughness levels (quick, medium, very thorough) describe how comprehensive the analysis is. D mixes it up with plan mode, which has the approval step."),
        scenarios=(4,), points=("3.4:K4",),
        evidence=(Evidence("code:sub-agents", "read-only tools; Write and Edit are denied"),),
        basis="docs",
        qtype="diagnose", level="easy", principle="fit_for_purpose",
        situation="Explore diagnoses checkout drift but leaves no patch",
        trap="assume Explore edits in a worktree or after approval",
    ),
    MCQ(
        id="Q3.4-12",
        q=("A teammate proposes that every file read, including the three files being edited, goes through the Explore subagent \"to keep "
           "the main context clean\". The task is a 250-line module that will be refined over about five rounds of review comments, and it "
           "also needs a search for which of 90 other files call the module. How should you evaluate the proposal?"),
        opts=("Adopt it everywhere: summaries keep the context small, and edits can be re-derived from them.",
              "Adopt it with the very thorough level, so that summaries carry the full text of each file.",
              "Use Explore for the wide search, and read the files being edited in the main conversation.",
              "Skip Explore on this task, and read every file in the main conversation."),
        ans=2,
        explain=("The search over 90 files is verbose discovery worth isolating, while a module refined over several rounds needs its exact "
                 "text in the main conversation. A leaves the edits working from summaries that drop details. B expects the very thorough level, "
                 "which the docs describe as comprehensive analysis, to hand back whole files, and Explore returns a summary. D fills the main context with the "
                 "caller search that a subagent could do."),
        scenarios=(4,), points=("3.4:K4", "3.4:S3"),
        evidence=(Evidence("code:sub-agents", "The task needs frequent back-and-forth or iterative refinement"),),
        qtype="evaluate", level="hard", principle="proportionate",
        situation="proposal to route all file reads including the edited module through Explore",
        trap="delegate every read, or none",
    ),
    # ---- S1: plan mode for architectural work ----
    MCQ(
        id="Q3.4-13",
        q=("Product wants an invoicing app, built for one customer, to serve many. Data can be isolated with a tenant column on every "
           "table or with a separate schema per tenant; both touch about 90 files, and migrations are run differently for each. Last "
           "month a direct run added `tenant_id` to 30 models before the lead found that one customer's contract requires separate "
           "schemas, and the work was dropped. What should the lead do differently on the next attempt?"),
        opts=("Start directly with the tenant column, since it is the simpler design, and adjust later if needed.",
              "Run it directly in batches of 30 files, running the full test suite after each batch.",
              "Plan first: compare both isolation designs, including migrations, then do the approved one.",
              "Ask Claude to build the schema-per-tenant version directly in a branch and compare it afterwards."),
        ans=2,
        explain=("Tenant isolation is an architectural decision with two valid designs and different operational effects, and plan mode "
                 "lets Claude explore the code and compare them before any file changes. A and B commit to a design first, and "
                 "tests cannot tell whether the design suits the contract. D builds one design in full to learn about it, "
                 "which is the rework that planning avoids."),
        scenarios=(2,), points=("3.4:S1",),
        evidence=(Evidence("code:permission-modes", "Plan mode tells Claude to research and propose changes without making them."),),
        qtype="choose", level="medium", principle="fit_for_purpose",
        situation="single-tenant invoicing app becoming multi-tenant with two isolation designs",
        trap="start building one design and adjust later",
    ),
    MCQ(
        id="Q3.4-14",
        q=("A direct-execution run moved 58 files from an old date library to a new one. Review found two conventions for the start of "
           "the week: a global setting in 21 files and a per-call option in 37. Weekly report totals now differ by module, in about 3% "
           "of reports. Which change to the process would best prevent this next time?"),
        opts=("Plan the migration first, so one convention is chosen and then applied to every file.",
              "Give each directory its own direct request with an identical prompt, so every run follows the same instructions.",
              "Add the preferred convention to CLAUDE.md after the migration, so later work follows it.",
              "Add a lint rule that rejects whichever of the two conventions is less common."),
        ans=0,
        explain=("Where one change spans many files, the approach has to be decided once and then applied everywhere, which a reviewed plan "
                 "does. B repeats the decision independently in every run. C arrives after the migration and cannot fix it. D picks "
                 "the winner by popularity instead of by correctness and acts only after the inconsistency exists."),
        scenarios=(4,), points=("3.4:S1",),
        evidence=(Evidence("code:permission-modes", "Plan mode tells Claude to research and propose changes without making them."),),
        qtype="fix", level="hard", principle="explicit",
        situation="58-file date library migration with two week-start conventions mixed",
        trap="repeat the same prompt per directory",
    ),
    MCQ(
        id="Q3.4-15",
        q=("A ticket asks for `order_shipped` events to reach a logistics partner. The partner accepts either a webhook push, which needs a "
           "public endpoint, a retry queue and signing keys, or a nightly file drop that runs on the existing job runner. Either would "
           "touch about six files, and operations must provision whatever infrastructure is chosen. What is the best way to start "
           "with Claude Code?"),
        opts=("Build the file drop directly, since it needs the least infrastructure, and revisit it if the partner objects.",
              "Use plan mode to lay out both designs with their infrastructure needs, and decide before any edits.",
              "Build the webhook directly behind a feature flag, so it can be switched off if operations cannot provision it.",
              "Ask an Explore subagent to build both versions in parallel, and keep the one that passes the tests."),
        ans=1,
        explain=("Two valid integrations with different infrastructure needs are an architectural choice, and plan mode lets Claude lay "
                 "out both before anything is built. A and C commit to one design before operations has agreed to its infrastructure. "
                 "D cannot work, because Explore is a read-only subagent that does not edit files."),
        scenarios=(4,), points=("3.4:S1",),
        evidence=(Evidence("code:sub-agents", "read-only tools; Write and Edit are denied"),),
        community="Docs support the Explore read-only fact (option D); choosing plan mode for two designs with different infrastructure needs is TS 3.4 Skill 1, a guide judgment.",
        qtype="choose", level="medium", principle="fit_for_purpose",
        situation="webhook push versus nightly file drop for a logistics partner",
        trap="build one design directly and revisit it later",
    ),
    # ---- S2: direct execution for clear scope ----
    MCQ(
        id="Q3.4-16",
        q=("A CI helper runs Claude Code on a failing build while no one is watching. The log shows one failed test, "
           "`test_parse_duration`, with the assertion and the line in `parse_duration()` that returns 3600 for the input `1h30`. The job "
           "now starts with an Explore subagent that surveys the repository, and runs average 9 minutes against about 2 minutes "
           "for jobs without that step. What is the most effective change?"),
        opts=("Run it in plan mode, so the cause is confirmed in a plan before the function is edited.",
              "Keep the survey but move it to a smaller model, since the cost comes from the reading.",
              "Replace the survey with a two-step job that proposes the fix and then waits for approval.",
              "Pass the failure output to Claude to fix the function directly, then rerun the test."),
        ans=3,
        explain=("The log already names the function and the failing behaviour, so there is nothing to discover or design, and a fix with a "
                 "rerun of the test is enough. A adds a plan to a change with one obvious location. B keeps the survey and only "
                 "makes it cheaper. C adds an approval step to an unattended job, where nobody is there to give it."),
        scenarios=(5,), points=("3.4:S2",),
        evidence=(Evidence("code:sub-agents", "You're making a quick, targeted change"),),
        qtype="choose", level="easy", principle="proportionate",
        situation="CI fix job spends 9 minutes surveying the repository before a one-function fix",
        trap="survey with a cheaper model or add an approval step",
    ),
    MCQ(
        id="Q3.4-17",
        q=("A CI job runs `claude -p --permission-mode plan` when a snapshot test fails, to update one snapshot file. The log shows the "
           "failing test and its diff, Claude reads the file and prints a sensible change, and the run ends green. Over two weeks "
           "none of the 40 runs committed a change, and the snapshot still fails on the next build. What is the most likely "
           "root cause?"),
        opts=("The prompt omits the failing test's name, so Claude cannot find the snapshot file.",
              "Claude cannot edit snapshot files in non-interactive runs.",
              "The effort level is too low for Claude to commit to an edit on a single-file fix.",
              "The run is in plan mode, so it proposes the change and waits for an approval."),
        ans=3,
        explain=("Plan mode researches and proposes but makes no edits until a plan is approved, and an unattended job has nobody to approve "
                 "it, so a one-file fix that suits direct execution never lands. A is contradicted by the stem, where Claude printed a "
                 "sensible change to the file. B and C invent limits that the stem gives no sign of."),
        scenarios=(5,), points=("3.4:S2",),
        evidence=(Evidence("code:common-workflows", "Claude reads files and proposes a plan but makes no edits until you approve."),),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="unattended snapshot-fix job configured in plan mode never changes a file",
        trap="blame the prompt or the effort level",
    ),
    MCQ(
        id="Q3.4-18",
        q=("A lead is considering a rule that every change under `billing/` must start in plan mode, because billing code is sensitive. "
           "Meanwhile a developer needs to correct one misspelled label, \"Invoce date\", in a single template under `billing/templates/`. Tests and code review "
           "already cover that folder. How should you evaluate the rule when applied to this change?"),
        opts=("Adopt the rule: the sensitivity of the folder, not the size of the change, decides the mode.",
              "Reject the rule here: the scope is clear, and tests and review guard the folder.",
              "Adopt the rule, but approve the plan automatically since it will contain a single step.",
              "Use an Explore subagent over `billing/` first, then correct the label in plan mode."),
        ans=1,
        explain=("The mode should follow the task's scope and open decisions, and a one-word fix in one file has neither, while the "
                 "existing tests and review already protect the folder. A chooses the mode by location, not by scope. C keeps the ceremony and removes "
                 "the review it exists for. D adds a survey of a folder to a one-word fix."),
        scenarios=(4,), points=("3.4:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 3.4 Skills 1 and 2 choose the mode by scope and architectural effect; a folder-based rule is a policy judgment the guide does not mention.",
        qtype="evaluate", level="easy", principle="proportionate",
        situation="blanket plan-mode rule for a typo in one billing template",
        trap="choose the mode by folder sensitivity",
    ),
    # ---- S3: Explore for verbose discovery in multi-phase tasks ----
    MCQ(
        id="Q3.4-19",
        q=("A migration has four phases: find the usages of a deprecated API, design the replacement, edit, and test. In the main "
           "conversation the discovery phase read 310 call sites across 190 files. A `/compact` before the edit phase dropped 40 of "
           "the sites from its summary, and the edits missed them. The raw file contents were needed only to build the list of sites, "
           "which itself is under 2,000 tokens. Which fix is most effective?"),
        opts=("Run discovery in an Explore subagent that returns the sites grouped by pattern.",
              "Start a new session for each phase and paste the previous phase's full output into the next one.",
              "Run `/compact` with a focus on the call sites after discovery, so the summary keeps all 310.",
              "Switch to a model whose window is larger, to hold discovery and editing together."),
        ans=0,
        explain=("The file reads are the bulk and only the list matters, so a subagent can read them in its own context and return the "
                 "list, which keeps the main context free for the later phases. B pastes the whole output into each new session, "
                 "which refills the context. C still loads every file first and depends on a lossy summary that has already failed once. "
                 "D delays the squeeze without removing the unneeded reads."),
        scenarios=(2,), points=("3.4:S3",),
        evidence=(Evidence("code:common-workflows", "Exploring a large codebase fills your context with file reads. Delegate the exploration so only the findings come back."),),
        qtype="fix", level="hard", principle="preserve_information",
        situation="deprecated-API discovery over 190 files loses 40 of 310 sites at compaction",
        trap="compact with a focus instead of isolating the reads",
    ),
    MCQ(
        id="Q3.4-20",
        q=("A developer needs to add a shared retry adapter to a new service. First they must learn how three existing services "
           "implement retries, which means reading about 120 files of client code, and then they will write the adapter with Claude "
           "Code. Which approach best protects the main conversation's context?"),
        opts=("Switch to plan mode for the reading, because plan mode makes Claude read fewer files in the first place.",
              "Search for `retry` and read only the matching files, one service at a time, in the main conversation.",
              "Have Explore read the code and summarise each service, then write the adapter in the main chat.",
              "Choose a model with more room in its window, so all 120 files fit next to the adapter work."),
        ans=2,
        explain=("The reading is verbose discovery, and Explore reads in its own context and returns only a summary, leaving the main "
                 "conversation free for the adapter. A misreads plan mode, which limits edits and does not reduce how much Claude reads, "
                 "so the same files still fill the context. B still brings every matching file into it and can miss retry code that "
                 "is named differently. D delays the problem and keeps the unneeded file contents."),
        scenarios=(4,), points=("3.4:S3",),
        evidence=(Evidence("code:sub-agents", "This keeps exploration results out of your main conversation context."),),
        qtype="choose", level="medium", principle="fit_for_purpose",
        situation="reading 120 files of retry code in three services before writing an adapter",
        trap="believe plan mode isolates file reads from the context",
    ),
    MCQ(
        id="Q3.4-21",
        q=("Explore has summarised how three services handle retries, and the main conversation now holds that summary. The developer "
           "must edit the loop in `client_b/retry.py` and needs its exact current code. What is the most effective next step?"),
        opts=("Resume the Explore subagent and ask it to paste the whole file into its summary.",
              "Read that one file in the main conversation, since it is now the target of the edit.",
              "Repeat the discovery in the main conversation so that every source file is available for editing.",
              "Ask Explore for a very thorough pass, which includes the full text of each file."),
        ans=1,
        explain=("Once the work narrows to one file that will be edited, reading it directly costs little context and gives Claude the exact text. "
                 "A cannot work, because the built-in Explore agent is one-shot and cannot be resumed. C undoes the isolation that "
                 "protected the context. D expects the very thorough level, which the docs describe as comprehensive analysis, to "
                 "return whole files, and Explore returns a summary."),
        scenarios=(4,), points=("3.4:S3",),
        evidence=(Evidence("code:sub-agents", "The built-in Explore and Plan agents are one-shot and return no agent ID, so Claude can't resume them."),),
        basis="docs",
        qtype="choose", level="medium", principle="proportionate",
        situation="exact code of one retry loop needed after an Explore summary",
        trap="resume Explore or repeat discovery in the main conversation",
    ),
    # ---- S4: plan for investigation, direct for implementation ----
    MCQ(
        id="Q3.4-22",
        q=("A developer has spent 40 minutes in a default-mode session on a flaky integration test that spans three services. Claude "
           "now knows the test setup, but the cause is still unknown and several fixes are possible. The developer wants the cause "
           "found without any edits and then wants the chosen fix applied in the same session. What is the best way to do this?"),
        opts=("Prefix the investigation with `/plan`, approve the chosen plan, then let the session make the fix.",
              "Open a second session for the fix, and copy the findings across by hand when the first one is done.",
              "Stay in default mode and tell Claude not to edit anything until the developer says so.",
              "Restart Claude with `--permission-mode plan` so the investigation starts from a clean session."),
        ans=0,
        explain=("Plan mode for the investigation and approval for the implementation keeps the session's context and blocks edits while the "
                 "cause is unknown. B copies findings by hand and loses what the session knows. C relies on an instruction where the mode "
                 "gives a guarantee. D throws away the 40 minutes of context that the investigation needs."),
        scenarios=(4,), points=("3.4:S4",),
        evidence=(Evidence("code:permission-modes", "Enter plan mode by pressing `Shift+Tab` or prefixing a single prompt with `/plan`."),),
        qtype="configure", level="medium", principle="deterministic",
        situation="flaky cross-service test investigated read-only, then fixed in the same session",
        trap="tell Claude not to edit instead of using plan mode",
    ),
    MCQ(
        id="Q3.4-23",
        q=("A planned change to a shared type and its 50 call sites across four packages is half done when the session compacts. The "
           "developer fears the plan is lost and proposes pasting it into CLAUDE.md and also ending the session at 70% context to "
           "restart with the whole plan pasted. The plan was written in plan mode. How should you evaluate those precautions?"),
        opts=("Both are needed: a plan lives only in the conversation, and compaction replaces it with a summary.",
              "Only the restart is needed, because a compacted session cannot follow a plan made before compaction.",
              "Only CLAUDE.md is needed, because that file is reloaded in every session while plan files are not.",
              "Neither: Claude wrote the plan to a file, and Claude Code re-injects it after each compaction."),
        ans=3,
        explain=("In a long cross-package session the plan file is re-injected after each compaction, so the plan survives where conversation "
                 "history may not and the planned approach can be carried out in the same session. A wrongly assumes the plan lives only "
                 "in the conversation. B has no basis, since the plan is back in context after compaction. C is wrong because the plan "
                 "file is exactly what is re-injected."),
        scenarios=(2,), points=("3.4:S4",),
        evidence=(Evidence("code:large-codebases", "Claude Code re-injects the plan file after each compaction, so the plan survives where conversation history may not"),),
        basis="docs",
        qtype="evaluate", level="hard", principle="fit_for_purpose",
        situation="plan written in plan mode for a 50-call-site type change, session compacts halfway",
        trap="copy the plan into CLAUDE.md or restart the session",
    ),
    MCQ(
        id="Q3.4-24",
        q=("A plan to change 52 files to a new date library was approved and execution has finished two groups cleanly. In group 3, Claude "
           "finds six call sites that use a custom subclass of the old date type, which the plan does not mention and which can be "
           "handled in two different ways. What is the best way to continue?"),
        opts=("Continue executing and let Claude pick a way for the six sites, since the plan fixes the general approach.",
              "Discard the plan and restart the migration from plan mode, because the plan has proved wrong.",
              "Return to plan mode for those six sites, update the plan, then resume executing it.",
              "Ask an Explore subagent to rewrite the six sites in its own context and return the diffs."),
        ans=2,
        explain=("The plan holds for the groups already done, but the six sites carry a new design choice, so planning is needed for them "
                 "and direct execution can resume afterwards. A makes that choice unreviewed, and it may differ from other uses of the "
                 "subclass. B throws away two groups of valid work. D fails because Explore is read-only."),
        scenarios=(2,), points=("3.4:S4",),
        evidence=(Evidence("code:permission-modes", "Plan mode tells Claude to research and propose changes without making them."),
                  Evidence("code:permission-modes", "To plan again, cycle back to plan mode with `Shift+Tab`, or prefix your next prompt with `/plan`.")),
        qtype="fix", level="hard", principle="proportionate",
        situation="approved migration plan meets six call sites it did not cover",
        trap="let the executor decide the new design choice or discard the whole plan",
    ),
)
