"""Exam bank · TS 1.6. Original questions; see docs/MCQ_BANK_PLAN.md."""
from utils.mcq_sets import MCQ, Evidence

TS = "1.6"
BULLETS = {
    "K1": "When a fixed sequential pipeline (prompt chaining) fits and when dynamic decomposition driven by findings fits",
    "K2": "Chaining patterns that split a review into steps, such as each file alone and then a cross-file integration pass",
    "K3": "The value of investigation plans that create subtasks from what each step discovers",
    "S1": "Choosing the pattern for the workflow: chaining for predictable multi-aspect reviews, dynamic decomposition for open-ended investigation",
    "S2": "Splitting large reviews into per-file local passes plus a separate cross-file pass to avoid attention dilution",
    "S3": "Decomposing open-ended tasks by mapping structure, finding high-impact areas, then following a prioritised plan that adapts to discovered dependencies",
}

_CHAIN = "Explicit prompt chaining (breaking a task into sequential API calls) is still useful when you need to inspect intermediate outputs or enforce a specific pipeline structure."
_CHAIN_STEPS = "Each step is a separate API call so you can log, evaluate, or branch at any point."
_ADAPT = "Claude decides what each step requires based on what it learned from the previous step, chaining dozens of actions together and course-correcting along the way."
_BP = "api:build-with-claude/prompt-engineering/claude-prompting-best-practices"

QUESTIONS = (
    # ---- K1: chaining versus dynamic decomposition ----
    MCQ(
        id="Q1.6-01",
        q=("After every closed support chat, your pipeline runs three steps in order: extract the issue, check the outcome "
           "against policy, write the CRM note. It handles 12,000 chats a week, and QA samples each step's output. A "
           "colleague proposes replacing this with one agent that plans its own steps for each chat. How should you "
           "evaluate the proposal?"),
        opts=("Accept it, since Claude now handles multistep reasoning internally and a chain only adds extra calls.",
              "Reject it, since nothing a stage finds alters what comes next, and QA reads the stage results.",
              "Accept it, provided the agent writes a log of each stage's result for QA to sample afterwards.",
              "Reject it, and merge the stages into one prompt with three output sections for QA to sample."),
        ans=1,
        explain=("The work never varies and QA relies on real stage outputs, which is when explicit chaining is still worth it. "
                 "A overlooks that the docs keep chaining for inspection and enforced structure. C swaps real stage outputs for "
                 "the agent's own account of them, and adapting adds nothing here. D gives QA labelled sections of one answer, "
                 "not separately produced results that can be evaluated."),
        scenarios=(1,), points=("1.6:K1",),
        evidence=(Evidence(_BP, _CHAIN),),
        qtype="evaluate", level="medium", principle="fit_for_purpose",
        situation="post-chat CRM note chain with QA sampling is proposed for replacement by a self-planning agent",
        trap="assume newer models make every chain unnecessary",
    ),
    MCQ(
        id="Q1.6-02",
        q=("Your research system runs one pipeline for everything: plan five subtopics, search each, summarise, write. Monthly "
           "market briefs score 4.6 of 5 with reviewers. Exploratory questions such as \"why are regional hospitals dropping "
           "telehealth?\" score 2.9, and reviewers note that promising sources are cited once and never pursued. Spot checks "
           "find the searches and summaries accurate on both. What is the most likely root cause?"),
        opts=("The planner stops at five subtopics, and these questions would need about ten for enough breadth.",
              "The planner's subtopics are too narrow, so its prompt needs guidance towards broader coverage.",
              "The synthesis agent compresses too hard, so the depth in its summaries never reaches the report.",
              "The plan is set once, ahead of the evidence, so nothing found can redirect the work."),
        ans=3,
        explain=("One pipeline does well where the work is predictable and badly where the next step should depend on what turned "
                 "up, so the shape of the plan is the cause. A and B improve the first plan, yet any plan set before reading "
                 "stays blind to what the sources reveal. C blames a step that spot checks found accurate."),
        scenarios=(3,), points=("1.6:K1",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the contrast between fixed pipelines and decomposition based on intermediate findings is the guide's.",
        qtype="diagnose", level="medium", principle="root_cause",
        situation="same research pipeline scores well on briefs and poorly on exploratory questions",
        trap="widen the first plan instead of letting findings change it",
    ),
    MCQ(
        id="Q1.6-03",
        q=("A migration agent must replace a deprecated logging call across 600 files. The change is the same in each file, "
           "so the steps are: rewrite, compile, run that file's tests. In a pilot of 50 files, 47 passed and 3 failed in "
           "different ways that nobody predicted. A colleague says this proves the whole job needs adaptive planning. Which "
           "design fits best?"),
        opts=("Keep the three steps, and have code send any failure to an open-ended investigation.",
              "Replace the steps with an adaptive planner that chooses what to do for every file in each run.",
              "Keep the three steps, and add a fourth fixed step that applies the repairs found in the pilot.",
              "Run a planner over all 600 files first to group them, then build a separate chain for each group."),
        ans=0,
        explain=("Most files are predictable and only the failures are open-ended, so each part gets the pattern that fits, and "
                 "separate steps let code branch on a result. B gives up steps that work for 94% of files. C assumes later "
                 "failures will match three that already differ from each other. D adds a planning layer when the rewrite is "
                 "the same everywhere."),
        scenarios=(4,), points=("1.6:K1", "1.6:S1"),
        evidence=(Evidence(_BP, _CHAIN_STEPS),),
        qtype="choose", level="hard", principle="proportionate",
        situation="logging migration chain passes 47 of 50 pilot files and fails 3 unpredictably",
        trap="switch all 600 files to adaptive planning because of a few failures",
    ),
    # ---- K2: chaining patterns for reviews ----
    MCQ(
        id="Q1.6-04",
        q=("Your review tool analyses each changed file in its own step, then runs an integration step. The per-file reports "
           "go to a dashboard, and the integration step is given only the 45-file diff, none of the earlier output. Its result is "
           "vague, repeats local nits and rarely mentions interfaces, while the per-file reports are sharp and accurate. What is "
           "the most effective fix?"),
        opts=("Add a list of interface categories to the integration prompt, so that it knows what to look for.",
              "Split the integration step into five groups of nine files, so that each group gets a closer look.",
              "Give it the per-file reports plus the interface-relevant code.",
              "Raise the integration step's output limit, so that it has room for a longer and deeper analysis."),
        ans=2,
        explain=("In a chain each step builds on the one before, and here the last step re-reads 45 files in one go and ignores "
                 "the focused work already done. A adds instructions but leaves the same overload. B hides any interface that "
                 "crosses two groups. D gives more room for output, not better input."),
        scenarios=(4, 5), points=("1.6:K2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the guide names per-file analysis followed by an integration pass; passing the reports forward is what makes it a chain, and no official page states it for reviews.",
        qtype="fix", level="medium", principle="preserve_information",
        situation="integration step gets the 45-file diff while per-file reports only reach a dashboard",
        trap="add focus categories to an overloaded integration step",
    ),
    MCQ(
        id="Q1.6-05",
        q=("Your research system must compare 12 clinical papers on a new therapy. A single step reads all 12 and lists the "
           "findings and conflicts. Findings from the first few papers dominate, later papers get one line each, and the last "
           "audit found two direct conflicts between papers that went unreported. Which design best addresses this?"),
        opts=("Analyse each paper alone, then run a separate step that compares the extracted findings.",
              "Analyse each paper alone, then join the per-paper results together to form the final report.",
              "Keep the first step, and add a second step that re-reads all 12 papers looking only for conflicts.",
              "Divide the papers into three groups of four, and write one combined summary for each of the groups."),
        ans=0,
        explain=("Focused analysis of each item, then a pass over the results for what only appears across items, is the review "
                 "chain applied to documents. B fixes the depth but no step ever looks for conflicts. C keeps a step that reads "
                 "everything at once, so the overload simply moves. D hides any conflict between papers in different groups."),
        scenarios=(3,), points=("1.6:K2", "1.6:S2"),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the guide gives this pattern for code reviews; applying it to papers is my extension of the same idea.",
        qtype="choose", level="medium", principle="fit_for_purpose",
        situation="single step reading 12 clinical papers misses two conflicts between them",
        trap="analyse each paper but skip the comparison step",
    ),
    MCQ(
        id="Q1.6-06",
        q=("A review chain logs every step. A developer reports that a merged SQL injection in `export_api.py` was never "
           "flagged on the pull request. The log shows the per-file step reported it with the right line number. The "
           "integration step receives only the diff and no per-file reports; its output lists three cross-file issues, and the "
           "posted comment lists the same three. What is the "
           "most likely root cause?"),
        opts=("The per-file finding was worded too weakly for the later steps to treat it as a real problem.",
              "The integration step did not rate the injection as serious enough to include in its output.",
              "Nothing in the chain carries local results through to what gets posted.",
              "The change to `export_api.py` was too large for one step to examine the file with enough focus."),
        ans=2,
        explain=("The logged steps show the finding existed and show where it vanished: the comment mirrors the integration "
                 "output. A and B assume a later step weighed the finding, but the integration step never saw it "
                 "and so could not have rated it. D is ruled out, because the per-file step found the flaw on the right line."),
        scenarios=(4, 5), points=("1.6:K2",),
        evidence=(Evidence(_BP, _CHAIN_STEPS),),
        qtype="diagnose", level="easy", principle="preserve_information",
        situation="per-file step reports a SQL injection but the posted comment mirrors integration output",
        trap="blame the integration step's judgment of severity",
    ),
    # ---- K3: adaptive investigation plans ----
    MCQ(
        id="Q1.6-07",
        q=("Your coordinator writes six research subtasks at the start and dispatches them in order. On a recent run, subtask "
           "2 reported that the dataset named in subtasks 3 and 4 was retracted last year. Subtasks 3 and 4 then ran as "
           "written, and their findings entered the report with a small note from the synthesis agent. What is the most "
           "effective fix?"),
        opts=("Add a final verification subagent that removes any finding built on a retracted source.",
              "Extend the planning prompt, so that the first plan checks for retractions before any search runs.",
              "Tell each subagent in its prompt to skip its subtask whenever it believes a source is unreliable.",
              "Have the coordinator re-plan what remains each time a result comes back."),
        ans=3,
        explain=("A discovery should change the work still to come, and the coordinator is the agent that sees every result. A "
                 "cleans up after the wasted work and still leaves the gap unfilled. B handles retractions only, and the next "
                 "surprise will be something else. C fails because subtasks 3 and 4 never see what subtask 2 reported."),
        scenarios=(3,), points=("1.6:K3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the value of plans that generate subtasks from discoveries is the guide's.",
        qtype="fix", level="medium", principle="model_driven",
        situation="subtask 2 reports a retracted dataset yet subtasks 3 and 4 still run on it",
        trap="clean up afterwards with a verification subagent",
    ),
    MCQ(
        id="Q1.6-08",
        q=("A customer writes that they were charged twice. Your support agent's hard-coded path for this case is "
           "`get_customer`, `lookup_order`, then `process_refund`, and a code gate blocks any refund outside policy. On one ticket, `get_customer` shows two accounts on the same email, with "
           "one charge on each, and the case stalls. Reviews find a stall like this in about 1 ticket in 12, each with "
           "different details. Which design fits best?"),
        opts=("Add a code branch for each new stall type as reviews identify it, and keep the path otherwise.",
              "Let the agent decide what to check next from what the lookups have shown so far.",
              "Refund the most recent charge in code whenever more than one account matches the email.",
              "Add a duplicate-account check as a fixed first step on every double-charge ticket."),
        ans=1,
        explain=("The stalls differ, so the next step has to come from what each lookup reveals. A and D handle known cases only, "
                 "so each new kind stalls until someone adds another rule. C acts on a guess before anyone knows which charge "
                 "is wrong."),
        scenarios=(1,), points=("1.6:K3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: applying adaptive subtasks to a support case is my extension of the guide's bullet.",
        qtype="choose", level="medium", principle="model_driven",
        situation="double-charge path stalls when one customer has two accounts on one email",
        trap="add one more fixed check for the latest surprise",
    ),
    MCQ(
        id="Q1.6-09",
        q=("An engineer is investigating why a nightly export sometimes duplicates rows, in a service nobody on the team wrote. "
           "The manager requires the agent to produce a complete step list before it reads any code, to have that list "
           "approved, and then to follow it exactly. How should you evaluate this requirement?"),
        opts=("Accept it, since an approved list gives the team both control and an audit trail of the work.",
              "Accept it, and add a branch to the list for each likely cause, so that it covers what turns up.",
              "Reject it, and start from a few hypotheses that change as evidence arrives.",
              "Reject it, and let the agent explore freely, reporting only its final diagnosis at the end."),
        ans=2,
        explain=("Nobody knows the cause, so useful steps cannot be listed before the code is read, and revisable hypotheses keep "
                 "the work visible. A gives control over guesses. B writes a longer decision tree that still cannot cover what "
                 "nobody has predicted. D goes too far the other way and leaves the team nothing to review along the way."),
        scenarios=(4,), points=("1.6:K3", "1.6:S1"),
        evidence=(Evidence("code:how-claude-code-works", _ADAPT),),
        qtype="evaluate", level="medium", principle="model_driven",
        situation="manager requires an approved full step list before any code is read on an unknown bug",
        trap="a list with branches for every likely cause",
    ),
    # ---- S1: selecting the pattern ----
    MCQ(
        id="Q1.6-10",
        q=("Your platform team is choosing a decomposition pattern for four new agent jobs, and each job has a different owner. "
           "Which job is the best fit for dynamic decomposition?"),
        opts=("Checking every pull request against a long, fixed eight-item security checklist.",
              "Extracting 40 fields from thousands of supplier contracts of varying length.",
              "Writing a nightly summary of incidents from the logs of 30 production services.",
              "Tracing why one integration test fails on about 1 run in 30."),
        ans=3,
        explain=("An intermittent failure is open-ended, because each finding decides what to check next. A, B and C are large "
                 "but their steps are known in advance and repeat without change, so size alone does not call for an adaptive "
                 "plan."),
        scenarios=(4,), points=("1.6:S1",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the split between predictable work and open-ended investigation is the guide's.",
        qtype="choose", level="easy", principle="fit_for_purpose",
        situation="choosing among four new jobs, only a flaky test is an open investigation",
        trap="mistake a big predictable job for an open-ended one",
    ),
    MCQ(
        id="Q1.6-11",
        q=("Your system produces a monthly competitor brief with the same six sections from the same sources. It runs as one "
           "open-ended coordinator, and runs vary from 9 to 40 subagent calls. In the last 12 briefs, the partnerships section "
           "was missing 3 times and the section order changed 5 times. What is the most effective fix?"),
        opts=("Replace the coordinator with one chained step per heading, then assemble.",
              "Keep the coordinator, and add a checklist of all six sections to its system prompt.",
              "Keep the coordinator, and cap it at 15 subagent calls so that runs become more consistent.",
              "Keep the coordinator, and give it a template file that shows the expected order of sections."),
        ans=0,
        explain=("The brief is predictable and needs a fixed structure, so a chain enforces what the coordinator only sometimes "
                 "delivers. B and D ask for that structure through instructions, and the model can still skip or reorder. C "
                 "limits the calls and may lose more sections, without making any section certain."),
        scenarios=(3,), points=("1.6:S1",),
        evidence=(Evidence(_BP, _CHAIN),),
        qtype="fix", level="medium", principle="deterministic",
        situation="fixed-format monthly competitor brief run by an open-ended coordinator drops a section",
        trap="add a checklist or template to the coordinator prompt",
    ),
    MCQ(
        id="Q1.6-12",
        q=("Your QA team reviews each refund conversation on four aspects: policy compliance, identity check, tone and handoff "
           "quality. One prompt covers all four. An audit of 400 conversations found tone comments on nearly all of them, "
           "while the identity check was assessed on only 35%. The four aspects never change. Which design fits best?"),
        opts=("An adaptive planner that reads each conversation and decides which aspects are worth assessing.",
              "One prompt that rotates the order of the aspects on every run, so that none is always crowded out.",
              "A fixed chain with a focused step for each criterion, then a merge.",
              "One prompt that asks for a confidence score beside each aspect, with low scores sent to a person."),
        ans=2,
        explain=("A predictable multi-aspect review suits chaining, because a step of its own means no aspect can be crowded out. "
                 "A lets a run skip aspects that must always be assessed. B only moves the gap around at random. D measures how "
                 "sure the model feels, and does nothing about an aspect it never assessed."),
        scenarios=(1,), points=("1.6:S1",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the guide names chaining for predictable multi-aspect reviews; the docs do not discuss this case.",
        qtype="choose", level="medium", principle="fit_for_purpose",
        situation="one QA prompt over four aspects assesses the identity check on only 35% of conversations",
        trap="let a planner choose which aspects to assess",
    ),
    MCQ(
        id="Q1.6-13",
        q=("A shared `Money` type changes, and 9 packages call it. An engineer wrote a chain that gives each package its own "
           "fresh session, one after another. Every build passes, and a final integration step reviewed all nine diffs but could "
           "not reconcile the three different conversion helpers and two rounding rules without redoing several packages. What is the most likely root cause?"),
        opts=("Each package lacks its own CLAUDE.md, so every session was free to follow its own local style.",
              "One design choice was split up, so it was worked out afresh in isolation.",
              "The integration step lacks a fixed checklist of the rounding and conversion rules to apply.",
              "Each session's prompt was too short to describe the target design of the type in enough detail."),
        ans=1,
        explain=("Decomposition suits work that can stand alone, and these edits share one design decision, so handing over the "
                 "shared edit and its call sites together keeps it consistent. A adds more places for the decision to differ. C "
                 "expects review to repair inconsistency that need not arise, as the integration step already ran. D treats it as a wording gap, but the "
                 "helpers and rounding rules were choices each session had to make for itself."),
        scenarios=(4,), points=("1.6:S1",),
        evidence=(Evidence("code:large-codebases", "**Give Claude the whole change in one session**: handing over the shared edit and its call sites together keeps the decisions behind each edit consistent, rather than re-deriving them per package"),),
        basis="docs",
        qtype="diagnose", level="hard", principle="fit_for_purpose",
        situation="shared Money type change chained per package ends with three helpers and two rounding rules",
        trap="add an integration step to reconcile interdependent edits afterwards",
    ),
    # ---- S2: per-file passes plus an integration pass ----
    MCQ(
        id="Q1.6-14",
        q=("Your review assistant reads a 38-file change in one request that uses about 8% of the model's context window. "
           "Files near the start get detailed comments, and the last 15 average one line each, though many are just as "
           "complex. The log shows all 38 in the request and `stop_reason: \"end_turn\"`. An engineer argues that with so "
           "much of the window free, focus cannot be the issue. What is the most likely root cause?"),
        opts=("The output limit ran out partway through, so the model had no room left for the later files.",
              "The request's size made the API drop detail from the later files before the model read them.",
              "The model needs a larger context window, so that files late in the request stay within reach.",
              "One pass over this many files thins its focus, however much of the window is free."),
        ans=3,
        explain=("Depth falls with position while the window has plenty of room, so space is not the constraint. The problem is "
                 "asking one pass to cover so many files. A is ruled out by `end_turn`, which is not a truncated response. B "
                 "invents a behaviour, and the log shows all 38 files in the request. C solves a capacity problem that the 8% "
                 "figure rules out."),
        scenarios=(4, 5), points=("1.6:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: attention dilution is the guide's term; no official page describes it.",
        qtype="diagnose", level="hard", principle="root_cause",
        situation="38-file review uses 8% of the window yet late files get one line each",
        trap="assume a window that is not full means no loss of focus",
    ),
    MCQ(
        id="Q1.6-15",
        q=("Your per-file review pass flags a missing null check in `invoice_view.py` on 22% of runs. `invoice_service.py`, the "
           "only caller, rejects null values first, so developers now ignore the comment and have started ignoring others "
           "too. A separate integration pass exists, but it only adds new findings. What is the most effective fix?"),
        opts=("Have the integration pass confirm or drop local findings before posting.",
              "Add a rule to the per-file prompt: assume that callers have already validated their inputs.",
              "Ask each per-file pass to score its confidence, and then hide every finding that falls below 0.7.",
              "Load the whole repository into each per-file pass, so that every pass is able to see the callers."),
        ans=0,
        explain=("Whether this finding is real depends on another file, so the pass with the cross-file view should decide it. B "
                 "also silences real missing checks. C trusts a score from a pass that cannot see the caller. D brings back the "
                 "dilution that per-file passes exist to avoid."),
        scenarios=(4, 5), points=("1.6:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the guide says splitting avoids attention dilution and contradictory findings; no official page covers resolving them in the integration pass.",
        qtype="fix", level="hard", principle="fit_for_purpose",
        situation="per-file pass reports a null check that the only caller already performs",
        trap="tell the per-file prompt to assume callers validate",
    ),
    MCQ(
        id="Q1.6-16",
        q=("You run per-file review subagents through the Task tool, then an integration subagent. To cut 20-file reviews from "
           "9 minutes to 5, an engineer starts the integration subagent at the same time as the per-file ones, giving it the "
           "same diff. Reviews are faster, but cross-file findings have fallen by half. How should the run be arranged?"),
        opts=("Keep them all concurrent, and tell the integration subagent to inherit the others' history.",
              "Run every subagent one after another, the per-file ones included, so that nothing overlaps.",
              "Start integration only once the parallel per-file reports exist, passing them in.",
              "Keep them all concurrent, and give the integration subagent a higher turn limit for its work."),
        ans=2,
        explain=("Per-file passes do not depend on each other, so they can run in parallel, but the integration pass depends on "
                 "their results, and a subagent returns only its final message. A relies on inheritance that does not exist. B "
                 "gives up a parallel speed-up those passes can safely use. D gives more turns and still none of the findings."),
        scenarios=(4, 5), points=("1.6:S2", "1.6:K2"),
        evidence=(Evidence("code:agent-sdk/subagents", "only its final message returns to the parent."),),
        community="Guide-only: that the integration pass runs after the per-file passes is the guide's pattern; the docs quote covers only what a subagent returns.",
        qtype="configure", level="medium", principle="explicit",
        situation="integration subagent is started alongside per-file subagents to cut review time",
        trap="run a dependent pass concurrently with its inputs",
    ),
    MCQ(
        id="Q1.6-17",
        q=("Your review chain has per-file passes and a separate integration pass. A teammate is deciding which pass should "
           "own each kind of check. Which check belongs in the integration pass?"),
        opts=("`orders.py` imports `billing.py` but never uses anything from it.",
              "`orders.py` writes UTC times that `billing.py` reads as local.",
              "`parser.py` reads `rows[len(rows)]` on a list it built itself.",
              "`cache.py` wraps a `store.py` handle in a badly named local variable."),
        ans=1,
        explain=("The timestamp mismatch is data flow between two files, and neither file looks wrong alone. A, C and D can each "
                 "be judged from one file alone, so the per-file pass is the right home."),
        scenarios=(4, 5), points=("1.6:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the guide assigns local issues to per-file passes and cross-file data flow to the integration pass.",
        qtype="configure", level="easy", principle="fit_for_purpose",
        situation="teammate assigns four kinds of check to per-file or integration passes",
        trap="a local defect that merely mentions a second file",
    ),
    # ---- S3: open-ended tasks ----
    MCQ(
        id="Q1.6-18",
        q=("An engineer tells the agent to \"harden error handling across our legacy payments monolith\": about 400 files, thin "
           "docs, and nobody on the team who knows all of it. On the first try the agent began editing at once, and after 60 "
           "files the build broke in ways nobody could trace. What should the agent do first on the next attempt?"),
        opts=("Learn how the parts depend on each other, read-only, before choosing what to touch.",
              "Spawn one subagent per directory, so that all 400 files are edited in parallel at the same time.",
              "Write out a complete list of edits for all 400 files, and then apply that list in a single pass.",
              "Edit the 20 smallest files first, so that progress appears quickly and each edit carries less risk."),
        ans=0,
        explain=("With unknown structure, the first step is understanding it without changing anything; plan mode is one way to "
                 "do that. B repeats the blind editing at greater speed. C commits to every edit before the dependencies are "
                 "known. D orders the work by size, which says nothing about the dependencies that broke the build."),
        scenarios=(4,), points=("1.6:S3",),
        evidence=(Evidence("code:permission-modes", "Plan mode tells Claude to research and propose changes without making them."),),
        qtype="choose", level="easy", principle="fit_for_purpose",
        situation="agent edits 60 files of a payments monolith at once and breaks the build",
        trap="edit in parallel or smallest first before mapping",
    ),
    MCQ(
        id="Q1.6-19",
        q=("Your agent is following a prioritised plan to add tests to a legacy scheduling service. While testing the top "
           "module, it finds that a global clock singleton makes that module and 14 others impossible to test "
           "deterministically. The plan has no item for this, and the agent has written 3 flaky tests so far. What is the most "
           "effective next step?"),
        opts=("Keep to the approved order, and stub the clock separately inside each test that needs it.",
              "Finish the other high-priority modules first, and log the clock problem as a follow-up item.",
              "Stop, and ask the engineer to refactor the clock by hand before any further work is attempted.",
              "Insert the work of making time injectable ahead of what it blocks, then re-rank."),
        ans=3,
        explain=("A plan for an open-ended task should change when a dependency turns up, and this one blocks 15 modules. A "
                 "repeats a workaround across every test. B leaves the highest-ranked modules untested and keeps producing tests "
                 "on a broken base. C hands back work the agent can plan itself, when nothing in the stem calls for a person."),
        scenarios=(4,), points=("1.6:S3", "1.6:K3"),
        evidence=(Evidence("code:how-claude-code-works", _ADAPT),),
        qtype="fix", level="hard", principle="model_driven",
        situation="global clock singleton found mid-plan blocks tests on 15 scheduling modules",
        trap="stick to the approved test order",
    ),
    MCQ(
        id="Q1.6-20",
        q=("After mapping a 300-module legacy system, the agent must rank where to add tests first. Your manager's target is 80% "
           "line coverage this quarter, and generated data classes could supply most of it quickly. The order settlement "
           "modules have 40 dependants and caused 6 of last year's 9 incidents. How should you evaluate the ranking?"),
        opts=("Start with the generated data classes, since the quarterly coverage target is the agreed measure.",
              "Put settlement first, because failures there spread and have already happened.",
              "Rank by lowest current coverage in each module, so that the widest gaps are closed first.",
              "Rank by most recently changed modules, on the grounds that newer code carries the most risk."),
        ans=1,
        explain=("The point of mapping is to find high-impact areas, and the dependants and incidents show where they are. A "
                 "reaches the number while testing the code least likely to matter. C measures the gap, not the impact. D uses a "
                 "rough proxy when direct evidence of impact is available."),
        scenarios=(4,), points=("1.6:S3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the guide says to identify high-impact areas; which signals show impact is my judgment.",
        qtype="evaluate", level="medium", principle="fit_for_purpose",
        situation="coverage target favours generated data classes over incident-prone settlement modules",
        trap="chase line coverage through generated code",
    ),
)
