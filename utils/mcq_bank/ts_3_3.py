"""Exam bank · TS 3.3. Original questions; see docs/MCQ_BANK_PLAN.md."""
from utils.mcq_sets import MCQ, Evidence

TS = "3.3"
BULLETS = {
    "K1": "Files in .claude/rules/ carry YAML frontmatter with a paths field of glob patterns that switches a rule on conditionally",
    "K2": "A path-scoped rule loads only when matching files are being worked on, which cuts irrelevant context and tokens",
    "K3": "For conventions spread over many directories, glob rules beat directory-level CLAUDE.md files",
    "S1": "Writing a rule file in .claude/rules/ whose paths frontmatter scopes it to matching files",
    "S2": "Using globs so a convention follows a kind of file wherever it sits in the tree",
    "S3": "Choosing a path-specific rule over subdirectory CLAUDE.md files when the files are scattered",
}

QUESTIONS = (
    # ---- K1: .claude/rules/ files and the paths frontmatter ----
    MCQ(
        id="Q3.3-01",
        q=("A mobile team keeps `*.graphql` schema files in 12 feature folders. They want naming conventions for those schemas "
           "applied only when Claude works on them, and are drafting `.claude/rules/graphql.md`. Which approach switches the rule "
           "on for those files only?"),
        opts=("Put a first line in the body saying the section applies only to `.graphql` files, so the model skips it elsewhere.",
              "Open the file with YAML frontmatter containing a `paths` list whose entry is `**/*.graphql`.",
              "Open the file with frontmatter containing a `globs` list whose entry is `**/*.graphql`.",
              "Add a `claudeMdExcludes` entry for every file type other than `.graphql` in the project settings."),
        ans=1,
        explain=("`paths` is the field that scopes a rule to matching files. A leaves the rule loading in every session and asks the "
                 "model to ignore it, which is persuasion rather than scoping. C uses a field name Claude Code does not read, so the "
                 "rule would behave as unscoped. D is a setting for skipping CLAUDE.md files by path and does not scope a rule."),
        scenarios=(2,), points=("3.3:K1",),
        evidence=(Evidence("code:memory", "`paths` is the only field Claude Code reads from a rule; any other field is ignored without an error."),),
        qtype="configure", level="easy", principle="fit_for_purpose",
        situation="graphql schemas in 12 feature folders need naming rules only for those files",
        trap="body sentence or invented globs field instead of paths frontmatter",
    ),
    MCQ(
        id="Q3.3-02",
        q=("A Go rule starts with the frontmatter line `paths: [\"services/**/*.go]` and the author expects it to apply only to Go "
           "sources. Last week the 900-token rule showed up in every session, including 120 sessions that only touched the "
           "React dashboard. Which explanation is most likely?"),
        opts=("Rules apply only to extensions the project lists in settings, and `.go` was not listed.",
              "Rules under `.claude/rules/` always load at launch, and `paths` only decides their priority.",
              "The `services/**` prefix matches nothing at the root, so the rule falls back to loading everywhere.",
              "The frontmatter is not valid YAML, so it is ignored and the rule loads as if it had no scope."),
        ans=3,
        explain=("An unparseable frontmatter block is dropped, which leaves a rule with no `paths` and therefore no scope. A invents a "
                 "settings list. B is false because scoped rules do load conditionally. C reverses the behaviour: a pattern that "
                 "matches nothing loads nothing, it does not widen."),
        scenarios=(4,), points=("3.3:K1",),
        evidence=(Evidence("code:memory", "If the YAML between the markers doesn't parse, Claude Code ignores the frontmatter and loads the rule as if it had no `paths`."),),
        basis="docs",
        qtype="diagnose", level="medium", principle="root_cause",
        situation="Go rule with a stray quote loads in 120 React-only sessions",
        trap="blame the glob prefix or an extension list",
    ),
    MCQ(
        id="Q3.3-03",
        q=("An engineer saves `.claude/rules/docs/changelog.md` with no frontmatter, expecting it to apply only when documentation "
           "is edited because it sits in a `docs` folder. Context listings show its 600 tokens present in all sessions, including "
           "ones that only touch the payments API. What accounts for this?"),
        opts=("A rule whose file name matches a project file, here `CHANGELOG.md`, is loaded only once that file is opened.",
              "Folders inside `.claude/rules/` scope a rule to the same-named project folder once that folder is edited.",
              "A rule with no `paths` field is loaded unconditionally, and subfolders only organise the rule files.",
              "Rules are scoped through the first heading of the file, which here does not name any directory."),
        ans=2,
        explain=("Scoping comes from `paths`; without it the rule applies to all files, and the folder layout inside `.claude/rules/` "
                 "is for organisation. A and B describe scoping by name or location, which does not exist. D invents a heading "
                 "convention."),
        scenarios=(4,), points=("3.3:K1",),
        evidence=(Evidence("code:memory", "Rules without a `paths` field are loaded unconditionally and apply to all files."),),
        qtype="diagnose", level="easy", principle="explicit",
        situation="changelog rule in a docs subfolder of rules still loads for payments work",
        trap="expect folder or file name to scope a rule",
    ),
    MCQ(
        id="Q3.3-04",
        q=("A rule file `api-errors.md` scoped to `api/**/*` and an unscoped `style.md` give conflicting advice on error wording. "
           "A team lead adds `priority: high` to the frontmatter of `api-errors.md` so it wins. Across 10 trial sessions on API "
           "files the conflict still resolves unpredictably. What should the team do?"),
        opts=("Remove the conflicting wording from one file, because the field is ignored and the clash remains.",
              "Raise the value to `priority: 1`, since Claude Code reads numbers in this field but not words.",
              "Rename the scoped file so it sorts after `style.md`, since the last rule loaded takes precedence.",
              "Move `api-errors.md` into the root CLAUDE.md, whose instructions Claude always weighs above rule files."),
        ans=0,
        explain=("`paths` is the only frontmatter field read, so `priority` does nothing, and contradictory instructions leave the "
                 "model free to choose either. The fix is to resolve the contradiction. B assumes a field that is not read in "
                 "any form. C and D assume precedence rules that the docs do not give."),
        scenarios=(4,), points=("3.3:K1",),
        evidence=(Evidence("code:memory", "`paths` is the only field Claude Code reads from a rule; any other field is ignored without an error."),
                  Evidence("code:memory", "if two instructions contradict each other, Claude may pick one arbitrarily.")),
        qtype="evaluate", level="hard", principle="root_cause",
        situation="priority: high added to a scoped rule that clashes with an unscoped one",
        trap="assume extra frontmatter fields influence precedence",
    ),
    # ---- K2: rules load only for matching files ----
    MCQ(
        id="Q3.3-05",
        q=("A rule scoped to `payments/**/*` holds idempotency conventions. At the start of a session a developer asks Claude "
           "to summarise the team's conventions for payment code, before any file has been opened, and gets generic advice. "
           "After Claude edits `payments/refund.py` in the same session, its changes follow the rule. What explains the "
           "difference?"),
        opts=("The glob needs a trailing slash, and the first answer fell back to defaults until the pattern was fixed.",
              "Path-scoped rules enter context when Claude works on a matching file, not at launch.",
              "Rules are read once per session, so the developer should have restarted Claude Code before asking.",
              "Scoped rules are fetched only when `/memory` is opened, which happened between the two answers."),
        ans=1,
        explain=("A scoped rule is conditional: it loads when Claude reads or edits a file that matches, so nothing is in context "
                 "until then. A treats a working glob as broken, and the later success shows it works. C and D invent a restart "
                 "requirement and a `/memory` trigger."),
        scenarios=(4,), points=("3.3:K2",),
        evidence=(Evidence("code:memory", "A path-scoped rule loads when Claude uses the Read, Write, or Edit tool on a matching file."),),
        qtype="diagnose", level="medium", principle="explicit",
        situation="payments conventions unknown before any payments file is opened",
        trap="treat on-demand loading as a broken pattern",
    ),
    MCQ(
        id="Q3.3-06",
        q=("A monorepo's root CLAUDE.md has grown to 450 lines: Go service notes, React web notes and Swift iOS notes. In web "
           "sessions Claude often applies the iOS naming scheme, and the file costs context in every session. What is the most "
           "effective restructure?"),
        opts=("Delete the Go and Swift sections, since the web engineers seldom need them.",
              "Capitalise the web section and move it to the top, so it outweighs the other platforms' notes.",
              "Tell developers to begin every session with `/compact` to shed the notes they will not use.",
              "Move each platform's notes into a rule with `paths` covering that platform's folders."),
        ans=3,
        explain=("Path-scoped rules load only for the platform being edited, which removes the irrelevant notes and their cost. A "
                 "throws away notes the other teams still need. B competes for attention within the same crowded context. C compacts conversation history and does not "
                 "change which instruction files load."),
        scenarios=(2,), points=("3.3:K2",),
        evidence=(Evidence("code:memory", "Move instructions that matter for only part of the codebase into path-scoped rules, which load only when Claude works with matching files."),),
        qtype="fix", level="medium", principle="proportionate",
        situation="450-line root CLAUDE.md mixes Go, React and Swift notes",
        trap="delete or emphasise notes instead of scoping",
    ),
    MCQ(
        id="Q3.3-07",
        q=("During a long refactor, a developer runs `/compact`. A rule `api-errors.md` scoped to `api/**/*` had been loaded "
           "earlier by an edit under `api/`, and the developer wonders whether the rule is now lost. Next, Claude is asked to "
           "edit another file under `api/`. What happens?"),
        opts=("The rule is loaded again when a matching file is worked on; until then it is out of context.",
              "The rule stays out for the rest of the session, because compaction removes a loaded rule for good.",
              "The rule returns only if its `paths` frontmatter is removed, since scoped rules cannot reload.",
              "The rule returns only once the developer pastes its text into a prompt, as nothing else restores it."),
        ans=0,
        explain=("Compaction summarises away a rule that was loaded by a trigger file, so it can be missing until a matching file "
                 "is worked on again, and then it reloads on demand. B and D deny the reload. C is the advice for a rule that must "
                 "stay in context without any trigger; it is not needed for the rule to come back on the next matching edit."),
        scenarios=(4,), points=("3.3:K2",),
        evidence=(Evidence("code:context-window", "Path-scoped rules and nested CLAUDE.md files load into message history when Claude reads, writes, or edits their trigger file, so compaction summarizes them away with everything else."),
                  Evidence("code:memory", "load again on demand.")),
        basis="docs",
        qtype="evaluate", level="medium", principle="explicit",
        situation="scoped api rule after /compact and the next api edit",
        trap="think a loaded scoped rule is gone for good or needs manual restoring",
    ),
    # ---- K3: glob rules vs directory CLAUDE.md ----
    MCQ(
        id="Q3.3-08",
        q=("Every service under `services/` has a `Dockerfile`, and `tools/ci/` adds two more named `Dockerfile.runner` and "
           "`Dockerfile.cache`. Image conventions (pinned digests, non-root user) must apply to all of them, and new services "
           "appear monthly. Which setup serves this best?"),
        opts=("A CLAUDE.md in every service folder, copied from a template whenever a service is created.",
              "A single CLAUDE.md in `services/`, which covers every service folder beneath it.",
              "A rule with `paths: [\"**/Dockerfile*\"]`, which matches each of these files wherever it sits.",
              "A paragraph in the root CLAUDE.md that begins \"When editing a Dockerfile\" and lists the conventions."),
        ans=2,
        explain=("The conventions follow a file name, so one glob covers the current files, the two in `tools/ci/` and every "
                 "future service. A needs a new copy per service and leaves the tools folder out. B loads for any file in "
                 "`services/`, not only Dockerfiles, and misses `tools/ci/`. D keeps the text in every session regardless of "
                 "what is being edited."),
        scenarios=(2,), points=("3.3:K3",),
        evidence=(Evidence("code:memory", "Rules can also be scoped to specific file paths, so they only load into context when Claude works with matching files, reducing noise and saving context space."),),
        qtype="choose", level="medium", principle="fit_for_purpose",
        situation="Dockerfiles in every service plus two under tools/ci",
        trap="per-folder or parent-folder CLAUDE.md for a file-name convention",
    ),
    MCQ(
        id="Q3.3-09",
        q=("A team added `src/components/CLAUDE.md` saying every `*.stories.tsx` file must export a default `meta` object with a "
           "title built from the folder path. Story files also live under `src/features/*/ui/` and `packages/ui/src/`. In a "
           "sample of 60 story edits, the rule was followed in all 20 under `src/components` and in 3 of the other 40. "
           "What is the root cause?"),
        opts=("A CLAUDE.md in a subdirectory is read only for the first 200 lines, so the later instruction was cut.",
              "It loads only when Claude works in its own folder, which covers just one of the three roots.",
              "Claude Code keeps one nested CLAUDE.md per session, and the first one opened pushes the others out.",
              "Nested CLAUDE.md files load at launch only for the working directory, so deeper folders never see them."),
        ans=1,
        explain=("A directory-level file is tied to its own folder, so edits to stories elsewhere never trigger it. A, C and D "
                 "describe limits that do not match the evidence: the same file worked in 20 of 20 edits in its own folder, so it "
                 "was read and applied there, and nothing in the docs says a nested file displaces another."),
        scenarios=(4,), points=("3.3:K3",),
        evidence=(Evidence("code:memory", "Instead of loading them at launch, Claude Code loads each one once Claude reads, writes, or edits another file in that subdirectory."),),
        qtype="diagnose", level="hard", principle="root_cause",
        situation="stories convention followed in 20 of 20 edits in one folder and 3 of 40 elsewhere",
        trap="blame size or nesting limits instead of folder-bound loading",
    ),
    MCQ(
        id="Q3.3-10",
        q=("In 14 service folders, `app/` holds Python modules and SQL files side by side. Python files need typing conventions "
           "and SQL files need naming conventions, and neither set should be in context for the other kind of work. A lead "
           "suggests a CLAUDE.md in each `app/` folder. Which design is best?"),
        opts=("Two rules, one with `paths: [\"**/*.py\"]` and one with `paths: [\"**/*.sql\"]`.",
              "A CLAUDE.md in each `app/` folder with a Python section and a SQL section.",
              "A CLAUDE.md in each `app/` folder, with the SQL part imported from a shared file.",
              "One skill per file type that engineers invoke before they start editing."),
        ans=0,
        explain=("File-type globs separate the two sets wherever the files sit, so each loads only for its own kind of work. B "
                 "loads both sections whenever anything in the folder is touched. C has the same problem with imports "
                 "added. D relies on engineers remembering to invoke the skill."),
        scenarios=(4,), points=("3.3:K3",),
        evidence=(Evidence("code:memory", "Rules can also be scoped to specific file paths, so they only load into context when Claude works with matching files, reducing noise and saving context space."),),
        qtype="choose", level="medium", principle="fit_for_purpose",
        situation="python and sql files share 14 app folders but need different conventions",
        trap="folder-level file loads both sets for any file in the folder",
    ),
    # ---- S1: writing the rule file ----
    MCQ(
        id="Q3.3-11",
        q=("Deployment manifests live in `infra/deploy/base/` and in `infra/deploy/overlays/<env>/`, up to two levels below `infra/deploy/`. "
           "A rule should load when Claude works on any of them and not otherwise. Which `paths` entry in "
           "`.claude/rules/deploy.md` does that?"),
        opts=("`infra/deploy/*`, which stands for everything under the manifest folder.",
              "`deploy/**/*`, since the rule file already sits in the repository's `.claude` folder.",
              "`*.yaml`, which covers all manifests through their extension.",
              "`infra/deploy/**/*`, which covers all files beneath that folder at any depth."),
        ans=3,
        explain=("`**` crosses directory levels, and the pattern is read from the project root. A reaches only files directly in "
                 "`infra/deploy/`. B drops the `infra` prefix, so it points at a folder that does not exist. C matches only YAML "
                 "files in the project root and would also miss manifests ending in `.yml` or `.json`."),
        scenarios=(2,), points=("3.3:S1",),
        evidence=(Evidence("code:memory", "All files under `src/` directory"),),
        qtype="configure", level="easy", principle="fit_for_purpose",
        situation="manifests nested three deep under infra/deploy",
        trap="single star stops at one level, root-only extension glob",
    ),
    MCQ(
        id="Q3.3-12",
        q=("In a monorepo, a team put `apps/web/.claude/rules/forms.md` with `paths: [\"apps/web/src/forms/**/*\"]`. The folder "
           "`apps/web/src/forms/` exists and Claude edits files there daily, yet the rule never appears in context. Which change "
           "fixes it?"),
        opts=("Move the rule to the top-level `.claude/rules/` folder, since nested rule folders are not read at all.",
              "Add `apps/web/` to the project's additional working directories so the nested rules are discovered.",
              "Wrap the value in single quotes, because double-quoted globs are treated as plain text.",
              "Change it to `src/forms/**/*`, read from the folder that holds the `.claude` directory."),
        ans=3,
        explain=("Project rule patterns are relative to the directory containing the rule's `.claude` folder, so the repeated "
                 "`apps/web/` prefix points at a path that does not exist. A is wrong because rules in a subdirectory's "
                 "`.claude/rules/` do load on demand. B changes which directories are visible and not how the pattern is read. "
                 "C is wrong because double-quoted globs are the form the docs use."),
        scenarios=(4,), points=("3.3:S1",),
        evidence=(Evidence("code:memory", "Project rules**: the directory that contains the rule's `.claude` folder"),),
        basis="docs",
        qtype="diagnose", level="hard", principle="root_cause",
        situation="nested apps/web rule with a pattern repeating the apps/web prefix",
        trap="patterns resolved from repo root instead of the rule's own base folder",
    ),
    MCQ(
        id="Q3.3-13",
        q=("An engineer wrote a path-scoped review rule in `~/.claude/rules/` on their laptop. Local sessions follow it, but the "
           "CI review job, which checks out the repository on a fresh runner, ignores it in all of the last 30 runs. "
           "What is the right fix?"),
        opts=("Commit the rule to the repository's `.claude/rules/` folder so every checkout carries it.",
              "Change the `paths` value to an absolute path so that the runner's checkout matches it as well.",
              "Import the home-folder file from the repository's CLAUDE.md with an `@` line, as an include.",
              "Set `paths` to `**/*`, so the rule matches on any machine that runs the review job."),
        ans=0,
        explain=("Project rules travel with the repository, whereas a file in the home folder exists only on that machine. B "
                 "changes how files are matched but does not put the rule on the runner. C points at a file the runner does not "
                 "have. D widens the scope and still has no rule file to apply."),
        scenarios=(5,), points=("3.3:S1",),
        evidence=(Evidence("code:memory", "Personal rules in `~/.claude/rules/` apply to every project on your machine."),),
        qtype="fix", level="medium", principle="root_cause",
        situation="personal scoped rule works locally and not on the CI runner",
        trap="change the glob when the rule file is not on the runner",
    ),
    MCQ(
        id="Q3.3-14",
        q=("A rule must apply to `.ts` and `.tsx` files anywhere under `src/`, and to `.ts` files at any depth under `lib/`, "
           "which has subfolders like `lib/http/retry/`. Which frontmatter does this?"),
        opts=("`paths: \"src/**/*.ts, src/**/*.tsx, lib/*.ts\"`",
              "`paths: [\"src/**/*.{ts,tsx}\", \"lib/**/*.ts\"]`",
              "`paths: [\"src/*.{ts,tsx}\", \"lib/**/*.ts\", \"lib/*.ts\"]`",
              "`paths: [\"src/**/*.[ts,tsx]\", \"lib/**/*.ts\", \"lib/*.ts\"]`"),
        ans=1,
        explain=("Brace expansion lists two extensions in one pattern, and `**` reaches every depth. A uses `lib/*.ts`, which "
                 "reaches only files directly in `lib/`, so `lib/http/retry/` is missed. C uses `src/*`, which skips nested "
                 "folders. D uses square brackets, which are a character class matching one character, not two extensions."),
        scenarios=(2,), points=("3.3:S1",),
        evidence=(Evidence("code:memory", "You can specify multiple patterns and use brace expansion to match multiple extensions in one pattern:"),),
        qtype="configure", level="hard", principle="explicit",
        situation="ts and tsx under src plus ts at any depth under lib",
        trap="single star, bracket class and missing tsx",
    ),
    # ---- S2: globs follow a kind of file across directories ----
    MCQ(
        id="Q3.3-15",
        q=("Generated gRPC code (`*.pb.go`) sits next to the sources that use it in about 60 packages. A rule should tell Claude "
           "to regenerate with `make proto` and never hand-edit these files. Which `paths` entry covers them?"),
        opts=("`*.pb.go`, which matches the generated suffix.",
              "`proto/**/*`, which covers the folder holding the definitions.",
              "`**/*.pb.go`, which matches the suffix in any directory.",
              "`**/pb.go`, which matches a file with that exact name in any directory."),
        ans=2,
        explain=("`**/` followed by the file pattern reaches generated files at any depth. A without `**/` matches only the "
                 "project root. B matches the definition sources, not the generated output beside the packages. D requires the "
                 "whole file name to be `pb.go`, which none of these files has."),
        scenarios=(2,), points=("3.3:S2",),
        evidence=(Evidence("code:memory", "All TypeScript files in any directory"),),
        qtype="configure", level="easy", principle="fit_for_purpose",
        situation="generated pb.go files beside sources in 60 packages",
        trap="suffix glob without a leading double star",
    ),
    MCQ(
        id="Q3.3-16",
        q=("A migration rule says every change needs a down script. Its pattern is `**/*.sql`. Engineers now report Claude adding "
           "down scripts to the analytics queries in `reports/`, about 1 in 3 of those edits, while migration files sit in "
           "`migrations/` folders at several depths. What is the best fix?"),
        opts=("Narrow the pattern to `db/migrations/*.sql`, which matches the main migrations folder only.",
              "Add a line to the rule body telling Claude to ignore it for reports and analytics queries.",
              "Create a CLAUDE.md in `reports/` that overrides the migration rule for files in that folder.",
              "Change it to `**/migrations/**/*.sql`, so the folder and the extension must both match."),
        ans=3,
        explain=("Combining the folder name with the extension limits the rule to migration files at any depth. A would miss "
                 "migrations in other `migrations/` folders. B leaves the rule loading for reports and relies on the model to "
                 "disregard it. C adds a conflicting instruction instead of removing the cause, and contradictory instructions "
                 "may be resolved either way."),
        scenarios=(4,), points=("3.3:S2",),
        evidence=(Evidence("code:memory", "Use glob patterns in the `paths` field to match files by extension, directory, or any combination:"),),
        qtype="fix", level="medium", principle="proportionate",
        situation="sql glob applies migration down-script rule to report queries",
        trap="narrow too far, or patch with prompt text and an override file",
    ),
    MCQ(
        id="Q3.3-17",
        q=("React hook modules are named `useAuth.ts`, `useCart.ts` and so on, and sit in `hooks/` folders at varying depths "
           "under `src/`, next to unrelated files such as `reuse.ts` and `cause.ts`. A rule on hook conventions should load for "
           "hook modules only. Which `paths` entry does that?"),
        opts=("`src/**/use*.ts`, which matches names starting with `use` at any depth under `src/`.",
              "`src/**/*use*.ts`, which matches any name that contains `use` at any depth under `src/`.",
              "`src/use*.ts`, which matches names starting with `use` in the `src` folder.",
              "`**/use.ts`, which matches a file called exactly `use.ts` at any depth."),
        ans=0,
        explain=("The prefix pattern with `**/` catches the hook modules at every depth and leaves out names that only contain "
                 "the letters. B also matches `reuse.ts` and `cause.ts`. C reaches only files directly in `src/`. D needs the "
                 "whole name to be `use.ts`, which no hook module has."),
        scenarios=(4,), points=("3.3:S2",),
        evidence=(Evidence("code:memory", "Use glob patterns in the `paths` field to match files by extension, directory, or any combination:"),),
        qtype="configure", level="medium", principle="explicit",
        situation="hook modules useX.ts at varying depths beside reuse.ts and cause.ts",
        trap="contains-pattern over-matches, single level misses",
    ),
    # ---- S3: path rules over subdirectory CLAUDE.md for scattered files ----
    MCQ(
        id="Q3.3-18",
        q=("Each of 17 packages has a `flags.ts` that must follow one naming scheme and a registration step. A lead wants a "
           "CLAUDE.md in each package \"because packages are the natural unit\". New packages arrive monthly, and the scheme "
           "was revised twice this year. Which choice is best?"),
        opts=("Keep a template CLAUDE.md and copy it into each new package, so the packages stay uniform.",
              "A rule with `paths: [\"**/flags.ts\"]`, since the convention follows one file name in all packages.",
              "A root CLAUDE.md note that tells Claude to open each package's CLAUDE.md before it edits `flags.ts`.",
              "A CLAUDE.md in `packages/` only, since it sits above every package that has a `flags.ts`."),
        ans=1,
        explain=("The convention attaches to a file name that repeats across packages, so one glob covers existing and future "
                 "packages and is revised in one place. A produces 17 copies that need updating after each revision. C adds a "
                 "manual step and keeps the text in every session. D loads for any file under `packages/`, not just "
                 "`flags.ts`."),
        scenarios=(4,), points=("3.3:S3",),
        evidence=(Evidence("code:memory", "Rules can also be scoped to specific file paths, so they only load into context when Claude works with matching files, reducing noise and saving context space."),),
        qtype="choose", level="medium", principle="proportionate",
        situation="flags.ts in 17 packages with a scheme revised twice this year",
        trap="per-package copies or a parent-folder CLAUDE.md",
    ),
    MCQ(
        id="Q3.3-19",
        q=("Platform engineers keep shared rules in `/opt/shared-rules/` and symlink that folder into each repository's "
           "`.claude/rules/`. After the project approved external imports, the unscoped rules load in CI and locally, but the "
           "`paths`-scoped ones never load, even on matching files. What should the team do?"),
        opts=("Raise the approval to user level, since project approval covers only rules without a scope.",
              "Mark the symlink read-only so that scoped rules in it are trusted like local ones.",
              "Copy the scoped rules into each repo's rules folder, or keep them in `~/.claude/rules/`.",
              "Prefix each pattern with `/opt/shared-rules/`, so it matches from the link's target folder."),
        ans=2,
        explain=("A symlink whose target is outside the working directory is treated as an external import, and after approval "
                 "only the rules without `paths` load. Real files in the repository, or user-level rules, are not subject to that. "
                 "A and B invent trust levels and permissions. D changes the pattern base, which is not what is blocking the load."),
        scenarios=(5,), points=("3.3:S1",),
        evidence=(Evidence("code:memory", "The linked rules don't load until you approve external imports for the project, and after that only the ones without a `paths` field load."),),
        basis="docs",
        qtype="fix", level="hard", principle="root_cause",
        situation="shared rules symlinked from outside the repo, scoped ones never load",
        trap="invent trust settings or a base-folder prefix",
    ),
    MCQ(
        id="Q3.3-20",
        q=("A platform lead lists four conventions and asks which one a path-scoped rule serves better than a subdirectory "
           "CLAUDE.md. A CI review job and local sessions must both apply it, and the team is not sure which is right."),
        opts=("The ledger service's retry policy, which applies to every file inside the `ledger/` folder.",
              "The commit message format, which applies to every change made anywhere in the repository.",
              "SQL keyword casing, which applies to `*.sql` files that sit in 14 different services.",
              "The \"do not refactor\" notice for the `legacy/` folder, which applies only to files in that folder."),
        ans=2,
        explain=("Only the SQL convention follows a kind of file across many folders, which a glob captures and a folder cannot. "
                 "A and D belong to one folder, where a CLAUDE.md in that folder fits. B applies to all work and belongs in the "
                 "root CLAUDE.md."),
        scenarios=(5,), points=("3.3:S3",),
        evidence=(Evidence("code:memory", "Rules can also be scoped to specific file paths, so they only load into context when Claude works with matching files, reducing noise and saving context space."),),
        qtype="choose", level="easy", principle="fit_for_purpose",
        situation="four conventions sorted into folder, repository and file-type scope",
        trap="treat every convention as needing a per-folder file",
    ),
)
