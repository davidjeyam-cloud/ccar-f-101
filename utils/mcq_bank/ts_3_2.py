"""Exam bank · TS 3.2. Original questions; see docs/MCQ_BANK_PLAN.md."""
from utils.mcq_sets import MCQ, Evidence

TS = "3.2"
BULLETS = {
    "K1": "Project commands in .claude/commands/ travel with version control; user commands in ~/.claude/commands/ stay personal",
    "K2": "Skills live in .claude/skills/ as SKILL.md files, configured through frontmatter such as context, allowed-tools and argument-hint",
    "K3": "context: fork runs a skill in an isolated subagent so that its output does not pollute the main conversation",
    "K4": "Personal skill variants go in ~/.claude/skills/ under different names so that teammates are not affected",
    "S1": "Create project-scoped commands in .claude/commands/ so the whole team gets them through version control",
    "S2": "Use context: fork for skills with verbose output or exploratory context",
    "S3": "Configure allowed-tools in skill frontmatter to control tool access while a skill runs",
    "S4": "Use argument-hint so developers see the parameters a skill expects",
    "S5": "Choose between skills (on-demand task workflows) and CLAUDE.md (always-loaded universal standards)",
}

QUESTIONS = (
    # ---- K1: project vs user commands ----
    MCQ(
        id="Q3.2-01",
        q=("Ten engineers copied the `/gen-changelog` command from the team wiki into `~/.claude/commands/`. The wiki page has been "
           "edited three times since, and in last month's release notes three engineers' output followed the old template while "
           "seven followed the new one. The team wants changes to the command reviewed like code. What is the most effective fix?"),
        opts=("Post each wiki edit in the team channel and ask engineers to refresh their copies the same day.",
              "Commit it to `.claude/commands/` and have every engineer delete the personal copy.",
              "Link the wiki page from CLAUDE.md, so the template Claude follows is the current wiki text.",
              "Run a nightly script on each laptop that downloads the wiki page into `~/.claude/commands/`."),
        ans=1,
        explain=("Project commands reach everyone through version control and go through pull-request review, and removing the "
                 "personal copies removes the thing that drifted. A keeps ten hand-maintained copies. C replaces the command with a "
                 "pointer, so what runs is no longer the reviewed template. D automates the copying but leaves ten private files "
                 "fed from a wiki that is not reviewed like code."),
        scenarios=(4,), points=("3.2:K1", "3.2:S1"),
        evidence=(Evidence("cc_skills", "Commit it so your team gets it too"),),
        qtype="fix", level="medium", principle="fit_for_purpose",
        situation="wiki-copied changelog command drifts across ten laptops",
        trap="announce edits or sync the wiki to each machine",
    ),
    MCQ(
        id="Q3.2-02",
        q=("A migration left `/check-pr` in two committed places: the old "
           "`.claude/commands/check-pr.md`, and a stricter rewrite in the skills folder as `check-pr/SKILL.md`. An engineer "
           "adds a check to the old file. `/check-pr` still runs and applies the stricter checks from the rewrite, but never her "
           "new one. She has no personal `check-pr`. What best explains why her edit has no effect?"),
        opts=("Changes to files in `.claude/commands/` are read only at the next restart, so she has to relaunch.",
              "Both files define `/check-pr`, and Claude Code runs whichever of them was committed most recently.",
              "Claude Code found a name clash, loaded neither file and passed `/check-pr` to Claude as plain text.",
              "A skill beats a command file of the same name, so her edit sits in a file that never runs."),
        ans=3,
        explain=("Custom commands have been merged into skills, and when both exist under one name the skill wins, so the older file "
                 "is dead weight. A invents a restart rule, and the stem shows that the command does run. B invents a recency rule. "
                 "C is contradicted by the stem, where the rewritten skill's checks do apply."),
        scenarios=(4,), points=("3.2:K1", "3.2:K2"),
        evidence=(Evidence("cc_skills", "| A skill and a file in `.claude/commands/` | The skill |"),),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="edited old command file loses to a same-named skill after migration",
        trap="blame a restart or the file's age",
    ),
    MCQ(
        id="Q3.2-03",
        q=("An engineer keeps a `/my-standup` command in `~/.claude/commands/`. It reads her private notes folder and formats updates "
           "the way her own manager likes them. A teammate suggests committing it to the repository's `.claude/commands/` so it is "
           "backed up. How should you evaluate this suggestion?"),
        opts=("Decline: it is personal and stays in `~/.claude/commands/`; a committed copy reaches everyone.",
              "Accept: committing is the only way to back up a command, and teammates can ignore what they do not use.",
              "Accept, but rename the file so that it does not collide with commands teammates may add later.",
              "Decline: user commands are shared through the home folder, so teammates can already run it."),
        ans=0,
        explain=("User commands are personal and a committed command reaches every teammate who clones, so a command built around her "
                 "own notes folder and manager belongs in her home folder. B is wrong because a backup does not need the shared repository. "
                 "C fixes naming and still publishes the command. D is wrong because a home folder exists on one machine only."),
        scenarios=(4,), points=("3.2:K1",),
        evidence=(Evidence("cc_skills", "All your projects on this machine, but not [Cowork or cloud sessions](#skills-in-cowork-and-cloud-sessions)"),
                  Evidence("cc_skills", "Commit it so your team gets it too")),
        qtype="evaluate", level="easy", principle="fit_for_purpose",
        situation="private standup command proposed for the shared repository as a backup",
        trap="treat the repository as a backup location",
    ),
    # ---- K2: SKILL.md and frontmatter ----
    MCQ(
        id="Q3.2-04",
        q=("Your repository has a skill `/db-notes` with 900 lines of schema notes and the description `Database stuff.` Engineers can "
           "run it by typing its name, but when they ask in plain words which tables hold invoice data, Claude answers from guesses and "
           "loads the skill in only 2 of 20 trials. Which change is most effective?"),
        opts=("Add `context: fork`, which runs the skill in a separate subagent that the main session picks more often.",
              "Move the full notes into CLAUDE.md so that Claude has the schema in every session.",
              "Rewrite the description to name what it covers, using words engineers use, like invoice tables.",
              "Add `disable-model-invocation: false` so that Claude is allowed to select the skill during a conversation."),
        ans=2,
        explain=("Claude decides whether to load a skill by matching the request against its description, so the description has to "
                 "contain the words people use. A changes where the skill runs, not how it is chosen. B pays for 900 lines in every "
                 "session to fix a matching problem. D sets a value that is already the default."),
        scenarios=(4,), points=("3.2:K2",),
        evidence=(Evidence("cc_skills", "Check the description includes keywords users would naturally say"),
                  Evidence("cc_skills", "(default) | Yes | Yes | Description always in context, full skill loads when invoked")),
        qtype="fix", level="easy", principle="explicit",
        situation="vague one-line description keeps a schema skill from loading",
        trap="move the notes to CLAUDE.md",
    ),
    MCQ(
        id="Q3.2-05",
        q=("A code-generation skill needs a 500-line API reference, 20 example payloads and a script that validates generated clients. "
           "Engineers use it a few times a week, and teammates working on unrelated bugs should not pay a context cost for the "
           "reference. How should you structure it?"),
        opts=("A `SKILL.md` that contains the full reference and the examples, with the validator described in text.",
              "Three skills, one each for the reference, the examples and the script, all set to load together.",
              "A short CLAUDE.md section, with the reference and examples pulled in through `@` imports.",
              "A skill folder with a short `SKILL.md` that points to separate reference, example and script files."),
        ans=3,
        explain=("A skill folder keeps `SKILL.md` as an overview and lets Claude read the reference and examples only when the task needs "
                 "them, while the script is executed rather than loaded. A puts everything in context each time the skill runs. B "
                 "multiplies descriptions that sit in context in every session. C is wrong because imported files are expanded and "
                 "loaded alongside CLAUDE.md in every session."),
        scenarios=(2,), points=("3.2:K2", "3.2:S5"),
        evidence=(Evidence("cc_skills", "Large reference docs, API specifications, or example collections don't need to load into context every time the skill runs."),
                  Evidence("code:memory", "Imported files are expanded and loaded into context alongside the CLAUDE.md that references them.")),
        qtype="configure", level="medium", principle="fit_for_purpose",
        situation="large API reference, payloads and validator script for a generation skill",
        trap="put everything in the SKILL.md body or in CLAUDE.md imports",
    ),
    MCQ(
        id="Q3.2-06",
        q=("Last week an engineer extended the `/pr-checklist` skill's description with a pasted 4,000-character review runbook, "
           "ending with the trigger sentence \"Use when the reviewer asks for a checklist\". Typing `/pr-checklist` still works, but in "
           "fresh sessions Claude has stopped choosing it on its own during reviews: 0 of 10 trials, against 9 of 10 before. What is "
           "the most likely root cause?"),
        opts=("The runbook contains angle brackets, which Claude Code strips from descriptions, so the trigger no longer matches.",
              "The skill listing cuts long descriptions at a character cap, so the trigger sentence at the end was dropped.",
              "A description that long makes Claude Code treat the skill as user-only, hiding it from automatic selection.",
              "The trigger sentence now belongs in `when_to_use`, because `description` is only used for the summary line."),
        ans=1,
        explain=("The combined description text is truncated at a character cap in the skill listing, so Claude sees only the start of "
                 "the runbook and never the trigger sentence; the key use case belongs first. A is not what happens to brackets, and "
                 "the stem does not say the runbook has any. C invents a length rule for invocation. D is wrong because `description` "
                 "is what Claude uses to decide when to apply the skill."),
        scenarios=(5,), points=("3.2:K2",),
        evidence=(Evidence("cc_skills", "the combined `description` and `when_to_use` text is truncated at 1,536 characters in the skill listing to reduce context usage"),),
        basis="docs",
        qtype="diagnose", level="medium", principle="root_cause",
        situation="a long pasted runbook pushes the trigger sentence past the description cap",
        trap="blame brackets or a separate when_to_use field",
    ),
    # ---- K3: context: fork ----
    MCQ(
        id="Q3.2-07",
        q=("A `/find-callers` skill uses `context: fork` and `agent: Explore`. The project's CLAUDE.md requires reports to name call "
           "sites as `path:line` and to skip generated folders. The skill's reports ignore both rules in every run, although "
           "ordinary sessions in the same repository follow them. What is the most likely root cause?"),
        opts=("The Explore agent starts without CLAUDE.md, so those rules never reached the forked subagent.",
              "A forked skill reads CLAUDE.md only after it finishes, so the rules apply to the next answer.",
              "The rules are phrased as preferences, so a subagent treats them as optional.",
              "The `agent` field cannot be combined with `context: fork` unless `allowed-tools` also lists Read."),
        ans=0,
        explain=("A forked skill using `agent: Explore` starts with the skill content and that agent's own system prompt, and none of the "
                 "CLAUDE.md files, so anything the task needs has to be written into SKILL.md. B invents a delayed read. C would not "
                 "explain why ordinary sessions obey the same wording. D invents a pairing requirement."),
        scenarios=(4,), points=("3.2:K3",),
        evidence=(Evidence("cc_skills", "A forked skill using `agent: Explore` starts with that content and the agent's own system prompt, and none of your CLAUDE.md files."),),
        basis="docs",
        qtype="diagnose", level="hard", principle="explicit",
        situation="forked Explore skill ignores CLAUDE.md output rules that normal sessions follow",
        trap="blame the wording of the rules",
    ),
    MCQ(
        id="Q3.2-08",
        q=("Your `/audit-deps` skill runs with `context: fork` and ends by returning a short verdict. Engineers like that the main "
           "conversation stays small, but last week they followed up 8 times with \"show me the lockfile line behind that warning\", "
           "and Claude had to search from scratch. Which change best fixes this?"),
        opts=("Remove `context: fork`, so that the full dependency scan stays in the main conversation.",
              "Run `/compact` right after each audit, so the scan is summarised without losing lockfile lines.",
              "Change the skill so that its final report names the file and line behind each warning.",
              "Add `allowed-tools: Read` so that Claude can open the lockfile again without asking each time."),
        ans=2,
        explain=("Only the subagent's final summary returns to the main conversation, so whatever follow-ups will need has to be in that "
                 "report. A gives up the isolation that engineers like. B summarises after the fact and the lines are not guaranteed "
                 "to survive. D removes a prompt but still leaves Claude searching for the line."),
        scenarios=(4,), points=("3.2:K3", "3.2:S2"),
        evidence=(Evidence("cc_skills", "The subagent summarizes its results and returns them to your main conversation when it finishes"),),
        qtype="fix", level="medium", principle="preserve_information",
        situation="forked audit returns a verdict without the lockfile lines behind it",
        trap="drop the fork or compact afterwards",
    ),
    MCQ(
        id="Q3.2-09",
        q=("In a CI-tooling repository, an engineer wants her `/summarize-flaky-tests` skill to run in an isolated subagent. She adds "
           "`context: fork` as the first line of the skill's instructions, below the closing `---` of the frontmatter. The skill "
           "runs as before: all 6,000 lines of test output still land in the main conversation. What is the most likely root cause?"),
        opts=("A forked skill sends its output to the main conversation unless it also names an `agent` type.",
              "The CI tooling starts sessions with isolation turned off, so no skill can be forked there.",
              "The subagent was created, but its output is copied back in full because the run is in the foreground.",
              "The line is in the body, so Claude reads it as an instruction, not as frontmatter configuration."),
        ans=3,
        explain=("Skill configuration is YAML between the `---` markers, and everything after the closing marker is the instruction text. "
                 "A is wrong because `agent` is optional and defaults to a general-purpose subagent. B invents a session setting. "
                 "C describes a copy-back that the isolation does not do."),
        scenarios=(5,), points=("3.2:K3",),
        evidence=(Evidence("cc_skills", "between `---` markers at the top of `SKILL.md`, and write the skill's instructions as Markdown after the closing `---`."),),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="context: fork written below the closing frontmatter marker",
        trap="blame the CI runner or a missing agent type",
    ),
    # ---- K4: personal skill variants ----
    MCQ(
        id="Q3.2-10",
        q=("A consultant works in six client repositories. She wants her own `/proposal-outline` skill available in all of them, and "
           "she revises it every week. None of the clients' teams should receive it. Where should she create it?"),
        opts=("In `.claude/skills/proposal-outline/` of each client repository, kept out of version control with an ignore rule.",
              "In `~/.claude/skills/proposal-outline/`, as a personal skill with a `SKILL.md` inside the folder.",
              "In `~/.claude/CLAUDE.md`, as a section that describes the outline steps for every session.",
              "In `.claude/skills/proposal-outline/` of one repository, copied into the others at the start of each project."),
        ans=1,
        explain=("A personal skill loads in all of her projects on the machine and is shared with no one, and it is edited in one place. "
                 "A and D create six copies that drift with every weekly revision. C turns an on-demand workflow into text that "
                 "loads in every session and cannot be invoked by name."),
        scenarios=(4,), points=("3.2:K4",),
        evidence=(Evidence("cc_skills", "All your projects on this machine, but not [Cowork or cloud sessions](#skills-in-cowork-and-cloud-sessions)"),),
        qtype="choose", level="easy", principle="fit_for_purpose",
        situation="one consultant's skill needed across six client repositories",
        trap="copy it into each repository and ignore it",
    ),
    MCQ(
        id="Q3.2-11",
        q=("Fifteen engineers each tune their own copy of the team's `/pr-review` skill. The platform lead proposes committing every "
           "variant to `.claude/skills/` as `pr-review-alice`, `pr-review-ben` and so on, so that nothing is lost. In a trial week "
           "Claude picked someone else's variant in 9 of 40 reviews. How should you evaluate the proposal?"),
        opts=("Keep it, and add a CLAUDE.md line telling Claude which variant belongs to which engineer.",
              "Keep it, and give each variant a longer description so that Claude can tell them apart.",
              "Reject it: variants belong in each engineer's `~/.claude/skills/`, leaving one shared skill.",
              "Reject it, and have engineers edit the team's skill in turn, so that there is a single version."),
        ans=2,
        explain=("Variants committed to the project reach everyone, and fifteen near-identical descriptions in every session leave Claude "
                 "to pick between skills whose purpose is the same. Personal folders keep each variant to its author. A and B try "
                 "to patch the overlap without removing it. D makes every edit land on all fourteen other engineers."),
        scenarios=(4,), points=("3.2:K4",),
        evidence=(Evidence("code:features-overview", "If descriptions are vague or overlap, Claude may load the wrong skill or miss one that would help."),),
        qtype="evaluate", level="hard", principle="fit_for_purpose",
        situation="fifteen committed personal variants of one review skill confuse selection",
        trap="keep the variants and disambiguate with descriptions or notes",
    ),
    MCQ(
        id="Q3.2-12",
        q=("An engineer saves a stricter variant as `~/.claude/skills/api-check-strict.md`, a single Markdown file with correct "
           "frontmatter, beside five personal skill folders that already work. After an hour, `/api-check-strict` is not in the "
           "`/` menu. No teammate, project or bundled command uses that name. What is the most likely root cause?"),
        opts=("A personal skill must be a folder named for it with `SKILL.md` inside; her file is not laid out so.",
              "She must run `/reload-skills`, because skills added to an existing folder are listed only after a reload.",
              "Personal skills may use only names that contain the word `personal`, so they cannot clash with project skills.",
              "Variants with `strict` in the name are held back until a teammate approves them in the project settings."),
        ans=0,
        explain=("Personal skills live at `~/.claude/skills/<skill-name>/SKILL.md`, so a lone file beside the folders is not a skill. B "
                 "is wrong because changes under an existing skills folder are picked up within the session, and `/reload-skills` is for "
                 "a top-level folder that did not exist at launch. C and D invent naming and approval rules."),
        scenarios=(2,), points=("3.2:K4", "3.2:K2"),
        evidence=(Evidence("cc_skills", "`~/.claude/skills/<skill-name>/SKILL.md`"),
                  Evidence("cc_skills", "Claude Code picks up the change within the current session, without a restart.")),
        basis="docs",
        qtype="diagnose", level="medium", principle="root_cause",
        situation="personal variant saved as a loose markdown file in the skills folder",
        trap="run a reload instead of fixing the layout",
    ),
    # ---- S1: project-scoped commands ----
    MCQ(
        id="Q3.2-13",
        q=("A lead believes she committed `.claude/commands/new-endpoint.md`, and her own sessions run `/new-endpoint` every day. "
           "Three new hires cloned the repository on Monday and none of them has the command. `git log --all` shows no commit "
           "touching that path on any branch, and her `git status` is clean. What is the most likely root cause?"),
        opts=("Her commit sits on a local feature branch that was never pushed, so clones cannot see it.",
              "An ignore rule covers `.claude/`, so the file was never committed and exists only on her machine.",
              "Project commands are shared through a cloud account, and the new hires have not been invited to it yet.",
              "She committed it on a branch that was never merged, so clones of the default branch lack it."),
        ans=1,
        explain=("A project command travels only if it is in version control. A file that exists locally, a clean status and no commit "
                 "on any branch point to an ignore rule. A and D would leave a commit visible in `git log --all`. C describes a sharing "
                 "mechanism that does not exist for command files."),
        scenarios=(4,), points=("3.2:S1",),
        evidence=(Evidence("cc_skills", "Commit it so your team gets it too"),),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="project command never reached git because an ignore rule covers its folder",
        trap="suspect an unpushed or unmerged branch",
    ),
    MCQ(
        id="Q3.2-14",
        q=("Developers run `/security-review`, a project command, in interactive sessions and update it through pull requests. The CI "
           "pipeline contains a pasted copy of the same prompt in its YAML, and the two have drifted: CI missed a check that developers "
           "gained three weeks ago. The CI step runs `claude -p` after checking out the repository. How should you configure the step?"),
        opts=("Keep the pasted copy and add a pipeline check that fails when its wording differs from the wiki.",
              "Install the command in `~/.claude/commands/` on the CI image, so that every job reads the same file.",
              "Pass `/security-review` as the prompt of the `claude -p` step, so the committed command runs.",
              "Turn the prompt into a CLAUDE.md section, since command files are read by interactive sessions only."),
        ans=2,
        explain=("In `-p` runs a custom command is expanded from the checked-out `.claude/commands/` file, so CI and developers use the "
                 "one reviewed copy. A keeps two copies and polices them. B adds a third copy to maintain on the image. D rests on a "
                 "limit that does not exist for `-p` runs."),
        scenarios=(5,), points=("3.2:S1",),
        evidence=(Evidence("code:headless", "and custom commands work. Include `/skill-name` in the prompt string and Claude Code expands it before running."),),
        qtype="configure", level="medium", principle="fit_for_purpose",
        situation="CI pipeline holds a pasted copy of a committed security-review prompt",
        trap="police the copy or bake it into the CI image",
    ),
    MCQ(
        id="Q3.2-15",
        q=("Your repository has 25 committed commands in `.claude/commands/`, all working well. One of them, `/scaffold-service`, now "
           "needs a 300-line template and a validation script that it should read only when it runs. Engineers are wary of changing "
           "everything at once. What is the most proportionate approach?"),
        opts=("Convert all 25 commands to skills at once, so that the repository uses a single format.",
              "Paste the template into the command file and describe the script in prose, keeping the format.",
              "Move all 25 commands to `~/.claude/commands/` and put the template in a shared folder.",
              "Leave the other 24 alone and make this one a skill folder holding the template and script."),
        ans=3,
        explain=("Existing command files keep working, and a skill folder is the form that can hold supporting files, so only the "
                 "command that needs them changes. A migrates 24 commands for no benefit. B loads the whole template into context on "
                 "every run and cannot hold a script. C removes the commands from version control."),
        scenarios=(2,), points=("3.2:S1", "3.2:K2"),
        evidence=(Evidence("cc_skills", "Your existing `.claude/commands/` files keep working. Skills add optional features: a directory for supporting files"),),
        qtype="configure", level="hard", principle="proportionate",
        situation="one of 25 committed commands needs a template and a script",
        trap="migrate everything or inline the template",
    ),
    # ---- S2: context: fork for verbose or exploratory skills ----
    MCQ(
        id="Q3.2-16",
        q=("A `/design-options` skill asks Claude to sketch twelve possible designs for a feature, argue for and against each, and "
           "recommend three. Engineers want to carry on implementing a recommended design in the same session, without the nine "
           "rejected sketches filling the conversation. Which frontmatter option fits?"),
        opts=("`context: fork`, with instructions to return only the three recommended designs and why.",
              "`argument-hint: [feature]`, so that engineers name the feature and Claude writes less per design.",
              "`allowed-tools: Read`, so Claude has no file access to spend turns on while sketching.",
              "`user-invocable: false`, so that the sketches are produced in the background and not shown."),
        ans=0,
        explain=("Brainstorming is exploratory context: running it in a forked subagent keeps the rejected sketches there and returns "
                 "only the result. B only documents the input. C governs permissions and does nothing about how much text is produced. "
                 "D hides the command from the `/` menu and does not isolate anything."),
        scenarios=(4,), points=("3.2:S2",),
        evidence=(Evidence("cc_skills", "Add `context: fork` to your frontmatter when you want a skill to run in isolation."),),
        qtype="choose", level="easy", principle="fit_for_purpose",
        situation="twelve brainstormed designs where only three recommendations matter",
        trap="a tool or hint setting for an isolation problem",
    ),
    MCQ(
        id="Q3.2-17",
        q=("Three skills in a CI-tooling repository are being reviewed for `context: fork`. `/trace-callers` reads about 80 files and "
           "answers with one paragraph. `/ticket-format` applies a 10-line template to the ticket the engineer has just been discussing "
           "with Claude. `/style-notes` holds naming guidance that Claude should apply while it writes code. Which should get "
           "`context: fork`?"),
        opts=("All three, so that none of them adds anything to the main conversation.",
              "`/ticket-format` and `/style-notes`, because they are used most often in a session.",
              "`/trace-callers` only, because it explores a lot and returns a short result.",
              "`/ticket-format` only, because it works on one ticket and needs no other files."),
        ans=2,
        explain=("Forking pays off when a skill does verbose exploration and the main session needs only the outcome. `/ticket-format` "
                 "depends on a conversation that a forked subagent cannot see, and `/style-notes` is reference guidance that must run "
                 "alongside the main work, so forking both defeats them. A and B include those skills; D picks the one whose input "
                 "lives in the conversation."),
        scenarios=(5,), points=("3.2:S2", "3.2:K3"),
        evidence=(Evidence("cc_skills", "The subagent doesn't see your conversation history, so the skill's instructions have to stand on their own."),
                  Evidence("cc_skills", "`context: fork` only makes sense for skills with explicit instructions. If your skill contains guidelines like \"use these API conventions\" without a task, the subagent receives the guidelines but no actionable prompt, and returns without meaningful output.")),
        qtype="choose", level="medium", principle="fit_for_purpose",
        situation="picking which of three skills should run in a fork",
        trap="fork everything or fork by frequency of use",
    ),
    MCQ(
        id="Q3.2-18",
        q=("A tech lead proposes `context: fork` for all 30 team skills, \"so that the main conversation never gets cluttered\". One "
           "of them, `/sort-imports`, takes a file path, rewrites the import block in that file and replies with a two-line "
           "confirmation. How should you evaluate the proposal for this skill?"),
        opts=("Apply it: isolation is free, and the skill's edit stays out of the main conversation as well.",
              "Apply it, and set `agent: Explore` so that the subagent can reach the file quickly and cheaply.",
              "Skip it here: forked skills cannot edit files in the repository.",
              "Skip it here: nothing verbose to isolate, and a fork would put its edit outside checkpoints."),
        ans=3,
        explain=("Forking pays off for verbose or exploratory output, and this skill returns two lines. A fork also has a cost for an "
                 "editing skill: its edits fall outside the session's checkpoints, so `/rewind` does not restore them. A treats "
                 "isolation as free. B picks a read-only exploration agent for a skill that must write. C is false: a forked subagent "
                 "can edit files."),
        scenarios=(4,), points=("3.2:S2",),
        evidence=(Evidence("cc_skills", "After one, `/rewind` restores only the files Claude had already edited in your conversation."),
                  Evidence("cc_skills", "the agent provides read-only tools optimized for codebase exploration")),
        qtype="evaluate", level="hard", principle="proportionate",
        situation="blanket fork proposal reaches a small editing skill with a two-line reply",
        trap="fork every skill for tidiness",
    ),
    # ---- S3: allowed-tools ----
    MCQ(
        id="Q3.2-19",
        q=("A `/commit` skill runs `git status`, `git add` and `git commit`. Engineers approve a permission prompt for each of the three "
           "every time, and have started to click through them unread. The team wants those commands to run without a prompt when the "
           "skill is used, while other shell commands keep asking. What is the right configuration?"),
        opts=("Add `Bash` to the allow rules in the project's `settings.json`, so that shell commands stop prompting.",
              "Set `disable-model-invocation: true`, so that Claude cannot ask for permission during the skill.",
              "Set `context: fork`, so the subagent runs these commands outside the permission system.",
              "Set `allowed-tools: Bash(git status *) Bash(git add *) Bash(git commit *)` in the skill."),
        ans=3,
        explain=("Listing exactly the three command patterns in the skill's `allowed-tools` grants them for the skill's turn and nothing "
                 "else, so other shell commands still ask. A opens every shell command for every session. B controls who may start "
                 "the skill and still leaves the prompts. C moves the work to a subagent without changing permissions."),
        scenarios=(4,), points=("3.2:S3",),
        evidence=(Evidence("cc_skills", "The `allowed-tools` field grants permission for the listed tools during the turn that invokes the skill, so Claude can use them without prompting you for approval."),),
        qtype="configure", level="easy", principle="least_privilege",
        situation="three git commands prompt on every use of a commit skill",
        trap="allow all of Bash in project settings",
    ),
    MCQ(
        id="Q3.2-20",
        q=("A skill `/fix-lint` has `allowed-tools: Bash(npm run lint *) Bash(npm run format *)`. When an engineer runs `/fix-lint`, "
           "those commands run without prompts. She then sends a follow-up message, \"run the formatter again\", in the same session, "
           "and Claude asks permission for `npm run format`. The skill's instructions are still in the conversation. What explains the "
           "prompt?"),
        opts=("The pre-approval covers only the turn that ran the skill, so it cleared with her next message.",
              "The skill content was dropped from the conversation, so its frontmatter no longer applies to later turns.",
              "Only the first listed pattern is pre-approved, and the second one needs a separate rule.",
              "Follow-up messages run in a new subagent with its own permission settings, which ignore the skill's."),
        ans=0,
        explain=("The grant is tied to the turn that invokes the skill and clears with the next message, even though the skill's text stays "
                 "in context; invoking the skill again re-applies it. B contradicts the stem, which says the instructions remain. C "
                 "and D invent per-pattern and per-message rules."),
        scenarios=(5,), points=("3.2:S3",),
        evidence=(Evidence("cc_skills", "The grant clears when you send your next message"),),
        basis="docs",
        qtype="diagnose", level="medium", principle="root_cause",
        situation="a skill's pre-approved commands prompt again on the next message",
        trap="assume the grant lasts as long as the skill text",
    ),
    MCQ(
        id="Q3.2-21",
        q=("A CI repository has 14 skills, and developers also use ordinary prompts. After an incident in which a skill ran `Write` on a "
           "protected config file, security wants `Write` unavailable to Claude in this repository during any skill and any plain "
           "prompt, whatever a skill's frontmatter says. Which approach best meets this?"),
        opts=("Add `disallowed-tools: Write` to the frontmatter of each of the 14 skills.",
              "Add a CLAUDE.md rule telling Claude not to use `Write` in this repository.",
              "Add a deny rule for `Write` in the project's permission settings.",
              "Add a PostToolUse hook that restores protected files after each `Write` call."),
        ans=2,
        explain=("A deny rule in the permission settings applies across all skills and prompts, so it covers every route with one entry. "
                 "A removes the tool only while those 14 skills are active, which leaves plain prompts and any new skill open. B is "
                 "an instruction, which the model may skip. D reacts after the file has been changed."),
        scenarios=(5,), points=("3.2:S3", "3.2:K2"),
        evidence=(Evidence("cc_skills", "To block tools across all skills and prompts, add deny rules in your"),),
        basis="docs",
        qtype="choose", level="hard", principle="least_privilege",
        situation="Write must be unavailable to every skill and every prompt in a CI repository",
        trap="repeat a per-skill setting 14 times",
    ),
    # ---- S4: argument-hint ----
    MCQ(
        id="Q3.2-22",
        q=("Engineers use a `/convert-file` skill that expects a file path, a source format and a target format. Half of the invocations "
           "arrive with only the path, so Claude asks questions back, and new engineers do not know that the skill takes three values. "
           "What is the most effective change to the frontmatter?"),
        opts=("Add `context: fork`, so that the skill gathers the missing values in a separate subagent.",
              "Add `argument-hint: [file] [from-format] [to-format]`, so the values show as engineers type.",
              "Add `allowed-tools: Read Write`, so that Claude can open the file and work out the other formats.",
              "Add `disable-model-invocation: true`, so Claude cannot run the skill with incomplete input."),
        ans=1,
        explain=("The hint puts the expected parameters in front of the engineer when they type the command, which is where the "
                 "values are missing. A changes where the skill runs. C governs tools and cannot tell Claude which formats were "
                 "meant. D controls who may start the skill, and these runs were started by the engineers."),
        scenarios=(4,), points=("3.2:S4",),
        evidence=(Evidence("cc_skills", "Hint shown during autocomplete to indicate expected arguments."),),
        qtype="fix", level="easy", principle="explicit",
        situation="engineers omit two of three parameters of a conversion skill",
        trap="reach for a tool or invocation setting",
    ),
    MCQ(
        id="Q3.2-23",
        q=("A `/open-ticket` skill reads the current git branch and repository itself, and engineers supply only the ticket number. "
           "Its frontmatter says `argument-hint: [repo] [branch] [ticket]`, copied from an older version. New engineers now type all "
           "three values, and about 1 run in 5 fails on a mistyped branch name. Which change is most effective?"),
        opts=("Keep the hint and add a note to the description saying which values have defaults.",
              "Add `allowed-tools: Bash(git branch *)` so that Claude can look up the branch itself.",
              "Describe the three values in CLAUDE.md so that Claude can correct a mistyped branch name.",
              "Change the hint to `[ticket]`, so it lists only what the engineer has to type."),
        ans=3,
        explain=("The hint is what engineers see while typing, so it should list only the values they supply. A leaves the misleading "
                 "hint in place and puts the correction where it is read less. B pre-approves a command the skill already runs. C "
                 "asks the model to repair input that should never have been requested."),
        scenarios=(5,), points=("3.2:S4",),
        evidence=(Evidence("cc_skills", "Hint shown during autocomplete to indicate expected arguments."),),
        qtype="fix", level="medium", principle="explicit",
        situation="stale hint asks engineers for values the skill derives from git",
        trap="document defaults elsewhere and leave the hint",
    ),
    MCQ(
        id="Q3.2-24",
        q=("A `/lookup-order` skill has `argument-hint: [order-id]`. Claude usually starts it by itself when a customer message "
           "mentions an order, and in 7 of 30 such runs it passed the customer's name as the argument. Engineers who type the "
           "command never make this mistake. Which change is most effective?"),
        opts=("Rewrite the hint as `[order-id, numeric only]` so that Claude sees the format.",
              "Set `disable-model-invocation: true` so that engineers always type the command themselves.",
              "State in the skill's description and body what the argument must be and where to find it.",
              "Add `context: fork` so the lookup runs with a clean context that has no customer names."),
        ans=2,
        explain=("The hint is shown to people while they type, whereas Claude decides what to pass from the skill's description and "
                 "instructions, so the rule belongs there. A edits text that autocomplete shows to typists. B removes the automatic "
                 "route the team wants. D hides the names from the subagent, which then cannot find the order either."),
        scenarios=(4,), points=("3.2:S4",),
        evidence=(Evidence("cc_skills", "Hint shown during autocomplete to indicate expected arguments."),
                  Evidence("cc_skills", "Both you and Claude can pass arguments when invoking a skill.")),
        qtype="fix", level="hard", principle="explicit",
        situation="Claude passes a customer name as the argument of an order lookup skill",
        trap="improve the autocomplete hint for a model-started run",
    ),
    # ---- S5: skills vs CLAUDE.md ----
    MCQ(
        id="Q3.2-25",
        q=("A team put its branch rule, \"create branches as `feat/<ticket>` and do not commit to main\", in a skill named "
           "`git-conventions` with a good description. The rule is one line and applies to every task that touches git. In 11 of 40 "
           "sessions Claude committed straight to main; the sessions that followed the rule were ones where an engineer asked about "
           "git conventions or typed `/git-conventions`. What is the most effective fix?"),
        opts=("Move the rule to CLAUDE.md, which loads in every session, and leave the skill for other material.",
              "Lengthen the skill's description to include the phrases that people use when they commit code.",
              "Set `disable-model-invocation: true` on the skill so that its rules apply consistently to all work.",
              "Move the skill to `~/.claude/skills/` so that it loads for every project on the machine."),
        ans=0,
        explain=("A one-line rule that applies to all work is a universal standard, and CLAUDE.md is loaded in every session while a "
                 "skill's content loads only when it is invoked or judged relevant. B depends on matching again. C removes the "
                 "automatic route that did exist. D invents a naming feature."),
        scenarios=(2,), points=("3.2:S5",),
        evidence=(Evidence("code:memory", "Keep it to facts Claude should hold in every session"),
                  Evidence("cc_skills", "In a regular session, skill descriptions are loaded into context so Claude knows what's available, but full skill content only loads when invoked.")),
        qtype="fix", level="easy", principle="fit_for_purpose",
        situation="one-line branch rule kept in a skill is skipped in 11 of 40 sessions",
        trap="polish the skill's description or name",
    ),
    MCQ(
        id="Q3.2-26",
        q=("Your 600-line API style guide matters only when engineers write endpoints, about one session in four. In a trial where it "
           "lived in a skill with a clear description, Claude consulted it in 4 of 10 endpoint-writing sessions. With the whole guide "
           "in CLAUDE.md it was used in 9 of 10, but sessions on other work became slower and less accurate. Which arrangement fits best?"),
        opts=("A short rule in CLAUDE.md to follow the API style guide, with the full guide kept in the skill.",
              "The whole guide in the skill, with the skill moved higher in the skill listing to be chosen first.",
              "The whole guide in CLAUDE.md, because reliable use of the guide matters more than context cost.",
              "The guide split into 12 skills, one per section, so that each description matches a narrower request."),
        ans=0,
        explain=("CLAUDE.md holds the always-on rule and the skill holds the reference material that loads on demand, so Claude is "
                 "reminded in every session and pays for the 600 lines only when it writes endpoints. B uses a listing priority that "
                 "does not exist. C is the trial that hurt the other 75% of sessions. D multiplies descriptions without adding a "
                 "reminder."),
        scenarios=(4,), points=("3.2:S5",),
        evidence=(Evidence("code:features-overview", "CLAUDE.md holds always-on rules; skills hold reference material loaded on demand"),),
        qtype="choose", level="hard", principle="fit_for_purpose",
        situation="API style guide used in one session in four, with skill-only and CLAUDE.md-only trials",
        trap="pick one location for the whole guide",
    ),
    MCQ(
        id="Q3.2-27",
        q=("Your team wants engineers to type `/incident-report` to run a nine-step write-up that is needed a few times a month. "
           "Separately, Claude must know the three severity definitions (S1 to S3) in every session, because they come up in reviews, "
           "tickets and chat. Where should each go?"),
        opts=("Both in CLAUDE.md, with the nine steps under a heading that engineers can name in a prompt.",
              "The severity definitions in CLAUDE.md, and the nine-step write-up in a skill named `incident-report`.",
              "Both in one skill whose description lists the severity words, so Claude loads it when they come up.",
              "The nine steps in CLAUDE.md, and the severity definitions in a skill that Claude can load when needed."),
        ans=1,
        explain=("Short facts needed in every session belong in the always-loaded CLAUDE.md, and an occasional workflow triggered by name "
                 "belongs in a skill. A loads nine steps into every session and gives no `/incident-report` command. C makes the severity "
                 "definitions depend on a skill being chosen. D swaps the two placements."),
        scenarios=(4,), points=("3.2:S5", "3.2:K2"),
        evidence=(Evidence("code:features-overview", "**Put it in a skill** if it's reference material Claude needs sometimes (API docs, style guides) or a workflow you trigger with `/<name>` (deploy, review, release)."),),
        qtype="choose", level="medium", principle="fit_for_purpose",
        situation="severity definitions plus a nine-step incident write-up triggered by name",
        trap="put both in one place",
    ),
)
