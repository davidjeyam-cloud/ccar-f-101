"""Exam bank · TS 3.1. Original questions; see docs/MCQ_BANK_PLAN.md."""
from utils.mcq_sets import MCQ, Evidence

TS = "3.1"
BULLETS = {
    "K1": "The CLAUDE.md hierarchy: user-level, project-level and directory-level files",
    "K2": "User-level instructions apply only to that user and are not shared through version control",
    "K3": "The @import syntax keeps CLAUDE.md modular by referencing external files",
    "K4": "The .claude/rules/ directory holds topic-specific rule files instead of one monolithic CLAUDE.md",
    "S1": "Diagnosing hierarchy problems, such as instructions sitting at user level instead of project level",
    "S2": "Using @import to include only the relevant standards files in each package's CLAUDE.md",
    "S3": "Splitting a large CLAUDE.md into focused topic files in .claude/rules/",
    "S4": "Using /memory to see which memory files are in play and to diagnose inconsistent behaviour across sessions",
}

QUESTIONS = (
    # ---- K1: the hierarchy ----
    MCQ(
        id="Q3.1-01",
        q=("Your monorepo's root CLAUDE.md says tests use Jest, while `packages/api/CLAUDE.md` says they use Vitest. A tech lead "
           "argues that the deeper file wins inside `packages/api`, so the root line can stay. In 14 of the last 40 sessions started "
           "inside `packages/api`, Claude still wrote Jest tests. How should you evaluate the lead's assumption?"),
        opts=("It holds, since the closer file replaces the root one, and the Jest tests were the model ignoring that file.",
              "It fails, because both files are placed in context together and neither replaces the other.",
              "It holds only when the session is launched from the repository root rather than from the package.",
              "It fails, because the root file takes priority over deeper ones, so the Vitest line belongs in it."),
        ans=1,
        explain=("Discovered files are concatenated rather than overriding each other, so two contradicting lines leave the model free to "
                 "follow either, and the fix is to remove the contradiction. A repeats the assumption and blames the model. C invents a "
                 "launch-directory condition, and the session already started in the package. D invents a priority order that the "
                 "files do not have."),
        scenarios=(2,), points=("3.1:K1",),
        evidence=(Evidence("code:memory", "All discovered files are concatenated into context rather than overriding each other."),
                  Evidence("code:memory", "if two instructions contradict each other, Claude may pick one arbitrarily.")),
        qtype="evaluate", level="medium", principle="explicit",
        situation="tech lead assumes the package CLAUDE.md overrides a contradicting root line about Jest and Vitest",
        trap="treat the closer file as an override",
    ),
    MCQ(
        id="Q3.1-02",
        q=("Two requests reach you in one week. The team wants every commit message in this repository to start with a ticket ID. "
           "Separately, one engineer wants Claude to explain its changes in British English in every project she works on. "
           "Where should each instruction go?"),
        opts=("Both in the repository's CLAUDE.md, so that version control keeps them consistent for everyone.",
              "Both in her own ~/.claude/CLAUDE.md, since she is the person who will ask Claude to commit.",
              "The ticket rule in her ~/.claude/CLAUDE.md, and the English preference in the repository's .claude/CLAUDE.md.",
              "The ticket rule in the repository's CLAUDE.md, and the English preference in her ~/.claude/CLAUDE.md."),
        ans=3,
        explain=("The ticket rule is a team standard for one repository, so it belongs in a file that version control shares; the "
                 "language preference is personal and spans all her projects, so it belongs at user level. A pushes her preference "
                 "onto every teammate. B keeps the team rule on one machine only. C swaps the two destinations."),
        scenarios=(4,), points=("3.1:K1",),
        evidence=(Evidence("code:memory", "Personal preferences for all projects"),
                  Evidence("code:memory", "These instructions are shared with your team through version control, so focus on project-level standards rather than personal preferences.")),
        qtype="choose", level="easy", principle="fit_for_purpose",
        situation="commit-prefix team rule and one engineer's British English preference need placing",
        trap="put both in the same file",
    ),
    MCQ(
        id="Q3.1-03",
        q=("In a monorepo, `packages/api/CLAUDE.md` says every public handler must return the standard error envelope. A developer "
           "launches Claude Code at the repository root to fix type errors in `packages/web`. In about 20% of those sessions Claude then also wraps web "
           "errors in the envelope. Nothing under `packages/web` or at the root mentions envelopes. Logs show that these sessions all "
           "read `packages/api/openapi.yaml`, a file with no prose, to copy a type. What is the most likely root cause?"),
        opts=("Reading a file under `packages/api` made that directory's CLAUDE.md load into the session.",
              "CLAUDE.md files in all packages load at launch, and the model applies them unevenly.",
              "The web package inherits the api package's CLAUDE.md through their shared root directory.",
              "The type that Claude copied carries the envelope convention, which it then repeats elsewhere."),
        ans=0,
        explain=("Directory-level files load when Claude reads or edits a file in that directory, so the rule arrives only in sessions "
                 "that touch the api package. B is wrong because directory-level files do not load at launch. C invents inheritance between "
                 "sibling directories. D is ruled out by the stem, since the YAML file holds no prose to repeat."),
        scenarios=(4,), points=("3.1:K1",),
        evidence=(Evidence("code:memory", "Instead of loading them at launch, Claude Code loads each one once Claude reads, writes, or edits another file in that subdirectory."),),
        basis="docs",
        qtype="diagnose", level="hard", principle="root_cause",
        situation="api package rule appears in web sessions that read one api file",
        trap="assume sibling directory files load at launch",
    ),
    # ---- K2: user-level is personal ----
    MCQ(
        id="Q3.1-04",
        q=("A GitHub Actions job runs Claude Code in a fresh container on every pull request and posts review comments. Reviewers "
           "say it ignores the team's naming conventions in about 80% of PRs. The repository has no CLAUDE.md. The conventions live "
           "in each engineer's `~/.claude/CLAUDE.md`, and running Claude Code locally on the same PR follows them. What is the most "
           "likely root cause?"),
        opts=("The job reviews the diff alone, so no instruction file of any kind can reach its comments.",
              "Conventions written at user level load only for interactive sessions and are skipped in automated runs.",
              "The conventions exist only in personal files, and the container has no copy of any of them.",
              "The container has a shallow checkout, which hides the repository's instruction files from the reviewer."),
        ans=2,
        explain=("User-level files stay on each engineer's machine, so a fresh container never sees them; the standards have to be "
                 "committed to the repository. A is false, since the docs tell teams to put review criteria in the repository's "
                 "CLAUDE.md for exactly this job. B invents an interactive-only rule. D describes a hidden repository file, but "
                 "the stem says none exists."),
        scenarios=(5,), points=("3.1:K2",),
        evidence=(Evidence("code:github-actions", "Create a `CLAUDE.md` file in your repository root to define code style guidelines, review criteria, project-specific rules, and preferred patterns."),),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="CI reviewer in a fresh container ignores conventions kept in engineers' home-directory files",
        trap="blame automated runs instead of the file's location",
    ),
    MCQ(
        id="Q3.1-05",
        q=("A merged PR added the line \"Answer tersely and skip explanations, I am an expert\" to the repository's CLAUDE.md. Five "
           "teammates now get answers they find too short. The author wants that style in every repository she works in. What is "
           "the best change?"),
        opts=("Remove the line from the repository file and put it in her own `~/.claude/CLAUDE.md`.",
              "Keep the line, and ask each teammate to add a longer-answer line to their own `~/.claude/CLAUDE.md`.",
              "Keep the line, but move it to a rules file under `.claude/rules/` so that it is easier to find and edit.",
              "Remove the line from the repository file and put it in `CLAUDE.local.md` at the root of this repository."),
        ans=0,
        explain=("A personal style belongs at user level, where it follows her into all her projects and reaches nobody else. B asks "
                 "five people to cancel a line, which leaves conflicting instructions in context. C moves "
                 "the same shared instruction into another shared file. D keeps it personal but limits it to this one repository, "
                 "which misses her requirement."),
        scenarios=(4,), points=("3.1:K2",),
        evidence=(Evidence("code:memory", "Personal preferences for all projects"),
                  Evidence("code:memory", "These instructions are shared with your team through version control, so focus on project-level standards rather than personal preferences.")),
        qtype="choose", level="easy", principle="fit_for_purpose",
        situation="one engineer's terse-answers preference committed to the shared repository file",
        trap="make teammates cancel it with their own user-level lines",
    ),
    MCQ(
        id="Q3.1-06",
        q=("A reviewer notices that PRs from one engineer, and only that engineer, always carry a `// reviewed by assistant` header and "
           "use `pytest -x`. The same quirks appear in her PRs to two other repositories. None of the three repositories mentions "
           "either habit, the three clones live in unrelated folders with no shared parent, and her teammates, who work on the same repositories, do not produce them. What is the most likely root "
           "cause?"),
        opts=("A CLAUDE.md in a parent folder above all three clones is loaded for every session she starts there.",
              "Auto memory saved the habits from her earlier corrections and replays them in the same repository only.",
              "Her model version differs from her teammates' and formats code differently across all repositories.",
              "Her own `~/.claude/CLAUDE.md` holds the habits and applies to every project she opens."),
        ans=3,
        explain=("Instructions in her user-level file follow her to every project and reach no one else, which matches a quirk shared by "
                 "her three repositories and absent for her teammates. A needs a shared parent folder, and the clones "
                 "are in unrelated ones. B fails because auto memory is kept "
                 "per repository, while the quirks cross repositories. C is a guess about a model difference that would not "
                 "produce a specific header and test flag."),
        scenarios=(4,), points=("3.1:K2", "3.1:S1"),
        evidence=(Evidence("code:memory", "Personal preferences for all projects"),),
        qtype="diagnose", level="hard", principle="root_cause",
        situation="one engineer's PRs share a header and a test flag across three repositories",
        trap="blame auto memory or the model version",
    ),
    # ---- K3: @import ----
    MCQ(
        id="Q3.1-07",
        q=("The team keeps its testing standards in `docs/testing.md`, read by humans and by CI. You want Claude to have that exact "
           "text in context from the start of every session in this repository, without a second copy. Which line in the root "
           "CLAUDE.md does that?"),
        opts=("`Testing standards: docs/testing.md`, which tells Claude where the file lives.",
              "`Testing standards: @docs/testing.md`, which expands the file into the session.",
              "`Testing standards: [docs/testing.md](docs/testing.md)`, a Markdown link to the page.",
              "`Testing standards: include(docs/testing.md)`, a directive that pulls in the page."),
        ans=1,
        explain=("The `@path` form imports the file, so its text is loaded with the CLAUDE.md that references it, and the original stays "
                 "the only copy. A and C name the file, and Claude would have to decide to open it. D is not a syntax that CLAUDE.md "
                 "files support."),
        scenarios=(2,), points=("3.1:K3",),
        evidence=(Evidence("code:memory", "CLAUDE.md files can import additional files using `@path/to/import` syntax."),),
        qtype="configure", level="easy", principle="explicit",
        situation="testing standards document must load from a CLAUDE.md without being copied",
        trap="link or name the file in prose",
    ),
    MCQ(
        id="Q3.1-08",
        q=("Your CLAUDE.md has a line: \"Never hand-edit @src/gen/schema.ts, it is generated.\" Since the line was added, every "
           "session starts with roughly 40,000 more tokens of context, `schema.ts` is a 3,000-line generated file, and Claude "
           "cites its internals in answers. Nothing else changed. What is the most likely root cause?"),
        opts=("The word \"generated\" tells Claude to read the file at startup so that it can recognise generated code.",
              "A mention of a file in a rule makes Claude read it in full before it answers anything else.",
              "The bare `@src/gen/schema.ts` imports the file, so its whole text loads with CLAUDE.md.",
              "The `src/gen/` folder has its own CLAUDE.md that loads at launch and repeats the schema."),
        ans=2,
        explain=("In ordinary text, `@path` is an import, so the file is expanded into context at the start of each session; wrapping "
                 "the path in backticks keeps it literal. A and B describe reading behaviour that CLAUDE.md does not trigger. "
                 "D contradicts the stem, which names a single line as the only change and no such file."),
        scenarios=(4,), points=("3.1:K3",),
        evidence=(Evidence("code:memory", "To mention a path in your CLAUDE.md without importing it, wrap it in backticks"),),
        basis="docs",
        qtype="diagnose", level="hard", principle="root_cause",
        situation="a rule that names a generated schema file loads 40,000 tokens at session start",
        trap="think a file mention makes Claude read it",
    ),
    MCQ(
        id="Q3.1-09",
        q=("`packages/etl/CLAUDE.md` contains the line `@standards/python.md`. The shared file lives at the repository root as "
           "`standards/python.md`. Sessions in `packages/etl` ignore every Python rule from it. The file exists, and nothing else "
           "in the package's CLAUDE.md is affected. Which change fixes it?"),
        opts=("Wrap the path in double quotes so that spaces and slashes are read as part of one name.",
              "Move the line to the root CLAUDE.md, because imports work only in the topmost file of a repository.",
              "Prefix the line with `Import:` so that Claude treats the reference as an instruction.",
              "Write the path as `@../../standards/python.md`, relative to the file that contains the line."),
        ans=3,
        explain=("A relative path resolves from the file holding the import, not from the repository root or the working directory, so the "
                 "package file has to climb two levels. A is wrong because a quoted path is not imported at all. B invents a limit; "
                 "any CLAUDE.md can import. C adds a word, and the `@` is what marks the import."),
        scenarios=(2,), points=("3.1:K3", "3.1:S2"),
        evidence=(Evidence("code:memory", "Relative paths resolve relative to the file containing the import, not the working directory."),),
        basis="docs",
        qtype="fix", level="medium", principle="explicit",
        situation="package CLAUDE.md imports a root-level standards file with a root-relative path",
        trap="quote the path or move the import to the root",
    ),
    # ---- K4: .claude/rules/ ----
    MCQ(
        id="Q3.1-10",
        q=("Your team wants its testing, API and deployment conventions kept as separate files that different owners can review, "
           "committed with the repository, and picked up by Claude Code without anyone registering them. Which layout fits?"),
        opts=("A `conventions/` folder at the root, with one file per owner, and a line in CLAUDE.md that lists every file.",
              "One CLAUDE.md per team member, each kept in a personal `~/.claude/` folder and synced by a script.",
              "Separate files such as `testing.md`, `api-design.md` and `releases.md` under `.claude/rules/`.",
              "A `.claude/rules/` folder holding one file per sprint, with the newest file listed first."),
        ans=2,
        explain=("Each topic gets its own descriptive markdown file in `.claude/rules/`, which is committed with the project and "
                 "discovered automatically. A needs a manual list that can fall out of date, and the files are not discovered "
                 "on their own. B keeps team rules out of version control. D organises by time, so related rules end up scattered."),
        scenarios=(4,), points=("3.1:K4",),
        evidence=(Evidence("code:memory", "Each file should cover one topic, with a descriptive filename like `testing.md` or `api-design.md`."),),
        qtype="choose", level="easy", principle="fit_for_purpose",
        situation="testing, API and deployment conventions need separate owned files without registration",
        trap="organise by owner or by sprint",
    ),
    MCQ(
        id="Q3.1-11",
        q=("A team split a 640-line CLAUDE.md into five files in `.claude/rules/`, none with a `paths` field, hoping that sessions would "
           "start with far less context. Measured at the start of a session, the context used is unchanged, and an engineer calls the "
           "split a failure. How should you evaluate this?"),
        opts=("Expected: rules without `paths` load at launch like CLAUDE.md, so the split organises but does not shrink.",
              "The split worked, but the numbers are stale until Claude Code is restarted after the rule files are created.",
              "The split failed, because Claude loads rules files at a lower priority and repeats their content in each prompt.",
              "The split worked, since rules files are read only when the matching topic comes up in the conversation."),
        ans=0,
        explain=("Unscoped rule files load at launch with the same priority as CLAUDE.md, so the same text still enters the session; the "
                 "gain is separate, reviewable files, and a size gain needs scoping or removing text. B invents a staleness rule. C "
                 "invents a lower priority. D describes topic-triggered loading that rules files do not have."),
        scenarios=(2,), points=("3.1:K4",),
        evidence=(Evidence("code:memory", "are loaded at launch with the same priority as `.claude/CLAUDE.md`."),),
        qtype="evaluate", level="medium", principle="proportionate",
        situation="five unscoped rules files expected to shrink the starting context of a 640-line file",
        trap="expect a split alone to save context",
    ),
    MCQ(
        id="Q3.1-12",
        q=("An engineer keeps personal workflow notes, such as how she likes branches named and when to run slow tests, and wants "
           "them applied in all her projects, as separate topic files rather than one long list. She does not want them in any "
           "repository. Where should she put them?"),
        opts=("In `.claude/rules/` of the first repository she opens, and then copy the folder into each of the others.",
              "In `~/.claude/rules/`, where files apply to every project on her machine.",
              "In one long `~/.claude/CLAUDE.md`, because user-level locations take no topic files.",
              "In a `CLAUDE.local.md` file at the root of each repository, listed in its `.gitignore`."),
        ans=1,
        explain=("User-level rules in `~/.claude/rules/` give her topic files that apply to every project and live outside every repository. "
                 "A puts personal files into a repository and creates copies. C is wrong, since the rules folder also exists at "
                 "user level. D is per repository, so she would keep one copy for each."),
        scenarios=(4,), points=("3.1:K4", "3.1:K2"),
        evidence=(Evidence("code:memory", "Personal rules in `~/.claude/rules/` apply to every project on your machine."),),
        basis="docs",
        qtype="choose", level="medium", principle="fit_for_purpose",
        situation="personal workflow notes as topic files for all projects",
        trap="copy a rules folder into each repository",
    ),
    # ---- S1: diagnosing hierarchy issues ----
    MCQ(
        id="Q3.1-13",
        q=("A platform team wrote 14 rules for Claude Code in `.claude/standards.md` and committed it. Three weeks later, sessions "
           "show no sign of any of them, for the author and for everyone else. The team's other instructions, in the root "
           "CLAUDE.md, work. The file's content is clear and specific. What should you check first?"),
        opts=("Whether the 14 rules are too long, because files over 200 lines are skipped entirely.",
              "Whether each rule begins with an imperative verb, since only commands are treated as instructions.",
              "Whether the team's model is recent enough to read Markdown files that are placed in dotted folders.",
              "Whether `.claude/standards.md` is a location that Claude Code loads at all."),
        ans=3,
        explain=("Claude Code reads CLAUDE.md files and the files in `.claude/rules/`; an arbitrary file name in `.claude/` is never "
                 "loaded, so the fix is to import it from CLAUDE.md or move it to the rules folder. A overstates a length "
                 "guideline, since long files reduce adherence rather than disappearing. B and C invent loading conditions."),
        scenarios=(4,), points=("3.1:S1",),
        evidence=(Evidence("code:memory", "Check that the relevant CLAUDE.md is in a location that gets loaded for your session"),),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="standards written to an unrecognised file name inside .claude",
        trap="blame the wording or length of the rules",
    ),
    MCQ(
        id="Q3.1-14",
        q=("A team put its test conventions in `tests/CLAUDE.md`. When engineers ask Claude to fix a test, the conventions are "
           "followed. When they ask for a new feature in `src/`, Claude writes the code and no tests, or tests that break the "
           "conventions, in about 60% of sessions, and Claude touches no file under `tests/` in those sessions. What is the most likely root cause?"),
        opts=("Claude follows directory-level files only for the first request in a session and drops them afterwards.",
              "The conventions apply to work in `tests/`, which a feature session in `src/` does not load.",
              "The file name `tests/CLAUDE.md` is reserved for test runners, and Claude Code reads it only when asked.",
              "Feature requests are long, and the model ignores the conventions whenever the request is complex."),
        ans=1,
        explain=("A directory-level file is tied to its directory, so work in `src/` that never touches `tests/` does not see it; conventions "
                 "that cover every kind of work belong in the project file or a rule that fits. A and C invent behaviours. D blames "
                 "the model, when the pattern of fixes working and features failing follows the directory."),
        scenarios=(2,), points=("3.1:S1", "3.1:K1"),
        evidence=(Evidence("code:memory", "Instead of loading them at launch, Claude Code loads each one once Claude reads, writes, or edits another file in that subdirectory."),),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="test conventions in tests/CLAUDE.md are missing from feature sessions in src",
        trap="blame request complexity",
    ),
    MCQ(
        id="Q3.1-15",
        q=("An engineer committed `.claude/CLAUDE.md` with 20 project rules, and Claude follows them in her sessions. Three new "
           "contractors, working from fresh clones, never see them. In the contractors' clones `git ls-files .claude` prints "
           "nothing, and the repository's `.gitignore` is the only file that differs from a default one. What is the most likely "
           "root cause?"),
        opts=("The contractors lack permission to read the folder, so Claude Code skips the files under it.",
              "Project-level files load only for people listed as maintainers, and the contractors are not on the list.",
              "The contractors need to run `/init` once, which copies the project's instruction files into place.",
              "A `.gitignore` entry for `.claude/` kept the file out of version control, so it never left her machine."),
        ans=3,
        explain=("Project-level instructions reach teammates only through version control, and an ignore rule on `.claude/` keeps the file "
                 "local; removing the rule and committing it fixes the hierarchy problem. A and B invent permission and maintainer "
                 "rules. C is wrong, since `/init` generates a CLAUDE.md and does not fetch the project's existing files."),
        scenarios=(2,), points=("3.1:S1", "3.1:K2"),
        evidence=(Evidence("code:memory", "These instructions are shared with your team through version control, so focus on project-level standards rather than personal preferences."),),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="project CLAUDE.md missing from contractors' clones because .claude is ignored",
        trap="invent a permission or setup step",
    ),
    # ---- S2: selective import ----
    MCQ(
        id="Q3.1-16",
        q=("A monorepo has 12 files under `standards/`. A data package is mostly Python, plus three TypeScript files that only "
           "configure its build. An engineer proposes a CI script that scans each package and writes @imports for every standards "
           "file whose language appears there. The package maintainers object. How should you evaluate the proposal?"),
        opts=("Accept it, since a script is repeatable and does not forget any standard that applies to a package.",
              "Reject it: frontend rules would load because of three TypeScript files that only run the build.",
              "Accept it, and add a review step in which a second script removes any import the package never uses.",
              "Reject it, and import all 12 files in the root CLAUDE.md so that every package gets every standard."),
        ans=1,
        explain=("Deciding which standards apply takes the maintainers' domain knowledge, and file extensions mislead here: the TypeScript "
                 "files are build glue, so the frontend rules would only add noise. A trusts a heuristic. C needs a second heuristic to fix "
                 "the first. D makes the over-inclusion worse and puts it on every package."),
        scenarios=(2,), points=("3.1:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 3.1 Skill 2 says imports are chosen from maintainers' domain knowledge; no official page addresses how to pick them.",
        qtype="evaluate", level="hard", principle="fit_for_purpose",
        situation="CI script writes imports from file extensions for a Python package with TypeScript build files",
        trap="select standards by language detection",
    ),
    MCQ(
        id="Q3.1-17",
        q=("`packages/billing-batch` runs nightly Python jobs that write to Postgres. It has no user interface and no public "
           "API, and its maintainers say every job must emit metrics and logs. `standards/` holds `python.md`, `sql.md`, `react.md`, "
           "`public-api.md` and `observability.md`. Which imports should its CLAUDE.md contain?"),
        opts=("`python.md`, `sql.md`, `react.md`, `public-api.md` and `observability.md`, so nothing is missed.",
              "`python.md` and `sql.md`, plus `public-api.md`, since every service eventually exposes an interface.",
              "`python.md`, `sql.md` and `observability.md`, the three standards that apply to this package.",
              "`python.md` and `sql.md` only, with metrics and logging left for the model to work out for itself."),
        ans=2,
        explain=("The package gets exactly the standards its work and its maintainers call for. A includes two that cannot apply and costs "
                 "context in every session. B adds `public-api.md` for an interface the package does not have. D drops the logging "
                 "requirement the maintainers named."),
        scenarios=(4,), points=("3.1:S2",),
        evidence=(Evidence("code:memory", "Imported files are expanded and loaded into context alongside the CLAUDE.md that references them."),),
        qtype="configure", level="easy", principle="proportionate",
        situation="nightly batch package needs three of five standards files",
        trap="import everything to be safe",
    ),
    MCQ(
        id="Q3.1-18",
        q=("The monorepo has 20 other packages that must not load `standards/errors.md`, and four packages share it as an 80-line file. To make each package's CLAUDE.md \"self-contained\", an engineer "
           "wants to paste that text into all four. Last quarter, three copies of a similar file drifted apart within weeks, "
           "and sessions in different packages gave different advice. Which approach is best?"),
        opts=("Paste the text into four files, and add a monthly reminder for someone to compare them.",
              "Move the text to the root CLAUDE.md so that every package gets it without any import.",
              "Place the text in every developer's `~/.claude/CLAUDE.md`, where it stays the same on each machine.",
              "Keep one `standards/errors.md` and import it from each package's CLAUDE.md."),
        ans=3,
        explain=("A single source imported where it applies cannot drift, and each package still loads it. A keeps four copies and relies on "
                 "a reminder. B loads it in packages that do not need it. C takes a team standard out of version control and leaves new "
                 "hires without it."),
        scenarios=(2,), points=("3.1:S2", "3.1:K3"),
        evidence=(Evidence("code:memory", "CLAUDE.md files can import additional files using `@path/to/import` syntax."),),
        qtype="choose", level="medium", principle="fit_for_purpose",
        situation="four packages copy a shared error-handling standard",
        trap="paste copies and rely on a reminder",
    ),
    # ---- S3: splitting into .claude/rules/ ----
    MCQ(
        id="Q3.1-19",
        q=("While splitting a 900-line CLAUDE.md into rules files, an engineer finds that the old text says \"use Jest\" in the testing "
           "section and \"use Mocha\" in a legacy section nobody has edited for two years. The plan is to copy each section into "
           "a file unchanged so the PR is a pure move. What is the best way to proceed?"),
        opts=("Resolve the contradiction during the split, keeping the framework in use and deleting the other.",
              "Copy everything unchanged, and rely on `testing.md` being more specific to outrank the legacy file.",
              "Copy everything unchanged, and add a line telling Claude to prefer whichever framework appears first.",
              "Leave the legacy section in CLAUDE.md and put only the Jest line into `testing.md`, to avoid editing."),
        ans=0,
        explain=("Files are loaded together and a contradiction lets Claude pick either side, so the split is the moment to remove it. B "
                 "assumes a priority between files that does not exist. C adds a third instruction on top of two conflicting ones. "
                 "D keeps both contradicting lines in context."),
        scenarios=(2,), points=("3.1:S3",),
        evidence=(Evidence("code:memory", "if two instructions contradict each other, Claude may pick one arbitrarily."),),
        qtype="fix", level="medium", principle="root_cause",
        situation="Jest and Mocha contradiction found in a 900-line file while moving sections",
        trap="move the text unchanged and rely on a priority",
    ),
    MCQ(
        id="Q3.1-20",
        q=("A 900-line CLAUDE.md breaks down as 240 lines on testing, 310 on API conventions, 180 on deployment, and 170 on general "
           "code style. Everyone needs the last part in every session. Teams want to review their own topics "
           "separately. Which end state is best?"),
        opts=("A CLAUDE.md in a folder for each topic, so that `testing/`, `api/` and `deployment/` each hold their own.",
              "Everything moved into `.claude/rules/`, with the 170 lines of code style in a file named `misc.md`.",
              "CLAUDE.md for code style, plus `testing.md`, `api-design.md` and `releases.md` in rules.",
              "One personal copy of the file per team, each kept in a `~/.claude/` folder, edited by that team only."),
        ans=2,
        explain=("The general style stays in the short project file, and each topic gets its own descriptive rules file with its own "
                 "owners. A ties topics to directories, but testing and API work cut across folders, and directory files load by "
                 "location. B hides the one part everybody needs in a catch-all. D takes shared standards out of version control."),
        scenarios=(2,), points=("3.1:S3",),
        evidence=(Evidence("code:memory", "Keep it to facts Claude should hold in every session: build commands, conventions, project layout"),),
        qtype="configure", level="medium", principle="fit_for_purpose",
        situation="900-line file split into testing, API and deployment topics with a universal core",
        trap="use one directory file per topic",
    ),
    MCQ(
        id="Q3.1-21",
        q=("Six weeks after a CLAUDE.md was split into `.claude/rules/`, the folder holds `testing.md`, `deploy.md`, and two catch-alls: "
           "`general.md` with 410 lines and `misc.md` with 380 lines on unrelated subjects. Claude follows the rules in "
           "those two files inconsistently, and engineers cannot tell who owns what. What is the most effective fix?"),
        opts=("Rename `general.md` to `important.md` and `misc.md` to `other.md` so that their purpose is clearer.",
              "Redistribute their content into single-topic files with descriptive names, and delete both.",
              "Move both files to the end of the alphabet so that they load last and carry the most weight.",
              "Merge the catch-alls back into CLAUDE.md, which Claude treats as more binding than rule files."),
        ans=1,
        explain=("The point of the folder is one topic per file, with names that say what is inside, so ownership and review stay clear. A "
                 "changes labels and keeps the same mixed content. C assumes that load order gives weight, which the docs do not state. "
                 "D rebuilds the monolith, and CLAUDE.md is context like the rule files."),
        scenarios=(2,), points=("3.1:S3", "3.1:K4"),
        evidence=(Evidence("code:memory", "Each file should cover one topic, with a descriptive filename like `testing.md` or `api-design.md`."),),
        qtype="fix", level="hard", principle="explicit",
        situation="two 400-line catch-all rules files with mixed subjects",
        trap="rename the catch-all files",
    ),
    # ---- S4: /memory ----
    MCQ(
        id="Q3.1-22",
        q=("After a refactor moved the project instructions from `CLAUDE.md` to `.claude/CLAUDE.md`, three engineers report that "
           "Claude behaves differently for each of them on the same task. They need to see which memory files each session "
           "has in play before changing anything. What is the best first step?"),
        opts=("Run `/memory` in each session and compare the memory files it shows.",
              "Run `/init` in each session, so that the project instructions are regenerated for everyone.",
              "Run `/compact` in each session, so that old instructions stop competing with the new ones.",
              "Ask Claude in each session to recite every rule it is following, then diff the three lists."),
        ans=0,
        explain=("`/memory` lists the CLAUDE.md and other memory file locations for user and project scopes, including files that do not exist "
                 "yet, so differences between sessions show up; `/context` confirms what actually loaded. B rewrites files before anyone knows what differs. C shortens the conversation and leaves the memory files "
                 "the same. D relies on the model's account of its own context."),
        scenarios=(2,), points=("3.1:S4",),
        evidence=(Evidence("code:memory", "The `/memory` command lists your CLAUDE.md, CLAUDE.local.md, and other memory file locations across user and project scopes"),),
        qtype="choose", level="easy", principle="root_cause",
        situation="three engineers see different behaviour after the project file moved into .claude",
        trap="regenerate or compact before looking",
    ),
    MCQ(
        id="Q3.1-23",
        q=("One engineer works on the same branch of the same repository from a laptop and a desktop. On the laptop, Claude replies "
           "in short bullet points with the team's ticket prefix on commits. On the desktop, it writes long paragraphs and still "
           "uses the prefix. Both machines were cloned this week at the same commit. What is the most effective way to find the "
           "cause?"),
        opts=("Reinstall Claude Code on the desktop, since a damaged install explains the style gap.",
              "Re-clone the repository on the desktop, because it must be missing project files that the laptop has.",
              "Move the style instruction to the top of the repository's CLAUDE.md on both machines.",
              "Open `/memory` on both machines and compare the user-level entries, since only the style differs."),
        ans=3,
        explain=("The ticket prefix, a project rule, behaves the same on both machines and only the style differs, which points at a "
                 "personal file on one machine; `/memory` lists the user-level locations for comparison and `/context` confirms what loaded. A and B "
                 "make heavy changes without a diagnosis, and B ignores that the project rule works. C puts a personal preference "
                 "into the shared file."),
        scenarios=(4,), points=("3.1:S4", "3.1:K2"),
        evidence=(Evidence("code:memory", "The `/memory` command lists your CLAUDE.md, CLAUDE.local.md, and other memory file locations across user and project scopes"),),
        qtype="diagnose", level="hard", principle="root_cause",
        situation="same repository, two machines, different answer style but same commit prefix",
        trap="reinstall or re-clone without comparing memory files",
    ),
    MCQ(
        id="Q3.1-24",
        q=("Before announcing new `.claude/rules/` files to 30 engineers, you tested them in your own working copy and they loaded. "
           "A colleague worries that your copy holds uncommitted or ignored files that teammates will not have. Which check best "
           "confirms what the team will actually receive?"),
        opts=("Ask Claude in your own session to list every rule it knows, and confirm that the new ones appear.",
              "Run a Markdown linter over the rules folder, which proves each file is valid.",
              "Clone the pushed branch into a new folder and run `/context` in a session there.",
              "Read the diff of the pull request carefully, since a file in the diff is a file that will load."),
        ans=2,
        explain=("A fresh clone contains only what version control delivers, so `/context` there lists the memory and rules files that a teammate would get loaded. A "
                 "tests the working copy that the colleague doubts and relies on the model's own account. B checks syntax, not location "
                 "or loading. D shows that a file was committed, but not that it sits where Claude Code looks."),
        scenarios=(4,), points=("3.1:S4", "3.1:K2"),
        evidence=(Evidence("code:memory", "To check which `CLAUDE.md` and rules files loaded at launch, run `/context`."),),
        qtype="evaluate", level="hard", principle="independent_check",
        situation="rules tested only in the author's working copy before announcing to 30 engineers",
        trap="check the working copy or the diff instead of a fresh clone",
    ),
)
