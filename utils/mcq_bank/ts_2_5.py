"""Exam bank · TS 2.5. Original questions; see docs/MCQ_BANK_PLAN.md.
Framing: assume Glob and Grep are enabled (on macOS, Linux and WSL they are absent by default and Claude searches through Bash)."""
from utils.mcq_sets import MCQ, Evidence

TS = "2.5"
BULLETS = {
    "K1": "Grep searches file contents for patterns such as function names, error messages and import statements",
    "K2": "Glob matches file paths by name or extension patterns",
    "K3": "Read and Write handle whole files, while Edit changes a file through unique matching text",
    "K4": "When Edit finds no unique text to match, Read followed by Write is the reliable fallback",
    "S1": "Choosing Grep to search code content, for example for all callers of a function or for an error message",
    "S2": "Choosing Glob to find files by a naming pattern such as a test-file suffix",
    "S3": "Using Read to load the full file and then Write when Edit has no unique anchor text",
    "S4": "Building understanding step by step: Grep to find entry points, then Read along imports, instead of reading everything first",
    "S5": "Tracing a function through wrapper modules by listing the names each wrapper exports and then searching for each name",
}

_GREP = "The Grep tool searches file contents for patterns. Where Glob finds files by name, Grep finds lines inside them."
_GLOB = "The Glob tool finds files by name pattern."
_WRITE = "The Write tool creates a new file or overwrites an existing one with the full content provided. It doesn't append or merge."
_UNIQ = ("`old_string` must appear exactly once. When it appears more than once, Claude either supplies a longer string with enough "
         "surrounding context to pin down one occurrence, or sets `replace_all: true` to replace them all.")

QUESTIONS = (
    # ---- K1: Grep searches contents ----
    MCQ(
        id="Q2.5-01",
        q=("Your team is dropping the `legacy_pdf` package from a 1,800-file monorepo. Before the dependency is removed, the agent "
           "must list every source file that uses the package, and nobody has a record of which services import it. Which approach "
           "gives that list most directly?"),
        opts=("Read the dependency manifests and take the modules listed beside the package as the ones that use it.",
              "Glob for `**/*pdf*` and treat each file that matches as one that depends on the package.",
              "Grep for import lines that mention `legacy_pdf` across the source tree.",
              "Glob every `.py` file and read the top of each one, since imports sit at the start of a file."),
        ans=2,
        explain=("Finding which files import a package is a search of file contents, which is what Grep does. A manifest says that the "
                 "dependency exists, not which files use it (A). Glob matches names, and a file can import the package without having "
                 "pdf in its name (B). D would open thousands of files to read a few lines of each."),
        scenarios=(4,), points=("2.5:K1",),
        evidence=(Evidence("code:tools-reference", _GREP),),
        qtype="choose", level="easy", principle="fit_for_purpose",
        situation="list every file importing a package scheduled for removal",
        trap="read the dependency manifest instead of searching imports",
    ),
    MCQ(
        id="Q2.5-02",
        q=("A research agent has a folder of 600 saved earnings-call transcripts named `call_0001.txt` to `call_0600.txt`. Asked "
           "which calls discuss a covenant waiver, it ran Glob with `**/*covenant*`, got no results and reported that none do. "
           "An analyst opens three of the files and finds the phrase in each. What is the most likely root cause?"),
        opts=("The file names are sequence numbers, so a name pattern cannot tell which files hold a phrase.",
              "Glob returns only files changed recently, and the transcripts were saved too long ago to show up.",
              "Glob skips files that `.gitignore` lists, and the transcripts folder is one of the ignored paths.",
              "The pattern needed the extension, as in `**/*covenant*.txt`, because Glob ignores names without one."),
        ans=0,
        explain=("Glob compares a pattern with file names only, and these names hold a number and nothing else, so an empty result "
                 "says nothing about the text; a content search with Grep is the tool for this job. B invents a recency filter: Glob "
                 "sorts by modification time, it does not drop older files. C has it backwards, since Glob does not apply "
                 "`.gitignore` by default. D invents an extension rule."),
        scenarios=(3,), points=("2.5:K1", "2.5:K2"),
        evidence=(Evidence("code:tools-reference", _GLOB),),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="empty Glob over numbered transcript names read as no mention of a phrase",
        trap="search names for a phrase that lives in the text",
    ),
    MCQ(
        id="Q2.5-03",
        q=("In a 5,000-file monorepo the agent greps for `TIMEOUT_MS` to see where a service reads the setting. The search returns "
           "900 lines, most of them from a vendored `third_party/` folder, and the next two turns spend most of the context window "
           "on them. The agent needs to see the lines that read the setting, and the service's own code is all under `services/`. "
           "What is the most effective change?"),
        opts=("Switch to Glob over `**/*.py` and read the files whose names look related to the service.",
              "Search again for `TIMEOUT_MS`, but ask Grep to return only the number of matches in each file.",
              "Read the largest of the matching files first, since the setting is most likely read where it is mentioned most.",
              "Run the same Grep limited to `services/`, using the `glob` or `type` option for the service's language."),
        ans=3,
        explain=("Narrowing the search to first-party code keeps the useful lines and leaves the vendored matches out; Grep can be "
                 "scoped by path, by a `glob` pattern or by a language `type`. A swaps a content search for a name search, which cannot "
                 "show where a setting is read. B drops the lines the agent needs and still lists every vendored file. C guesses "
                 "from file size and pays for whole files."),
        scenarios=(4,), points=("2.5:K1", "2.5:S1"),
        evidence=(Evidence("code:tools-reference", "Claude can scope results by file with the `glob` parameter, such as `**/*.tsx`, or by language with the `type` parameter, such as `py` or `rust`."),),
        qtype="fix", level="medium", principle="proportionate",
        situation="TIMEOUT_MS search returns 900 lines mostly from a vendored folder",
        trap="count matches instead of narrowing the search scope",
    ),
    # ---- K2: Glob matches paths ----
    MCQ(
        id="Q2.5-04",
        q=("A platform engineer has 60 repositories checked out under one workspace folder and asks the agent to list every "
           "`CODEOWNERS` file, wherever it sits, so that ownership can be audited. Which approach finds them?"),
        opts=("Grep the workspace for the word `CODEOWNERS` and list the files that contain it.",
              "Glob with `**/CODEOWNERS`, which matches that file name at any depth.",
              "Read the `.github` folder of the first repository and assume the others are laid out the same way.",
              "Read the workspace folder to get its listing, then open the root of each repository in turn."),
        ans=1,
        explain=("Locating a file by its name is a pattern match on paths, which is Glob, and `**` reaches every depth. Grep searches "
                 "contents, so it returns files that mention the word and misses an ownership file that never contains it (A). C "
                 "assumes a layout nobody has confirmed. Read opens files, not directories (D)."),
        scenarios=(4,), points=("2.5:K2",),
        evidence=(Evidence("code:tools-reference", _GLOB), Evidence("code:tools-reference", "Read only reads files, not directories.")),
        qtype="choose", level="easy", principle="fit_for_purpose",
        situation="locate every CODEOWNERS file across 60 checked-out repositories",
        trap="grep the file name as a word in contents",
    ),
    MCQ(
        id="Q2.5-05",
        q=("A research pipeline keeps its inputs as CSV files under `data/`. Asked how many there are, the agent runs Glob with "
           "`data/**/*.csv` and answers 100. The data engineer's own `find` count is about 1,400, and a second run of the agent's "
           "Glob again gives 100. What is the most likely root cause?"),
        opts=("Glob keeps only files modified in the last 100 days, so older CSV files drop out.",
              "Glob respects `.gitignore`, and most of the CSV files in `data/` are ignored by git.",
              "The `**` in the pattern reaches only the first two levels below the `data/` folder.",
              "The list is capped at 100 files, and the agent counted it as if it were complete."),
        ans=3,
        explain=("Glob returns at most 100 files and sets a truncation flag, so a count of exactly 100 means the list was cut short; "
                 "the agent should narrow the pattern, for example by subfolder, and count each part. Results are sorted by "
                 "modification time, not filtered by it, so A is wrong. B is backwards, because Glob does not apply `.gitignore` by "
                 "default. C is wrong because `**` matches at any depth."),
        scenarios=(3,), points=("2.5:K2",),
        evidence=(Evidence("code:tools-reference", "Results are sorted by modification time and capped at 100 files."),
                  Evidence("code:tools-reference", "If the cap is hit, Claude sees a truncation flag in the result and can narrow the pattern.")),
        basis="docs",
        qtype="diagnose", level="hard", principle="root_cause",
        situation="Glob count of exactly 100 CSV files reported as the total",
        trap="trust a list that hit the result cap",
    ),
    MCQ(
        id="Q2.5-06",
        q=("Support exports each ticket as one JSON file named like `2025-03-14_T88231.json`. The date exists only in the file "
           "name, because the body stores the time as epoch seconds. A manager wants the agent to pull every March 2025 ticket for "
           "a quality review. The export holds 3,000 tickets, about 60 of them from March. Which approach is best?"),
        opts=("Glob with `**/2025-03-*.json`, which selects the files by the date in their names.",
              "Grep for `2025-03` in the file contents, since each ticket records when it was created.",
              "Grep for `March 2025` in the ticket text, which customers often write when they describe an issue.",
              "Read the export folder and pick out the March files from the listing it returns."),
        ans=0,
        explain=("The date is a property of the file name, so a name pattern selects exactly the right files without opening any of "
                 "them. B searches the contents for a date format the body does not use. C finds tickets that happen to mention the "
                 "month, which is a different set. D fails because Read opens files, not directories."),
        scenarios=(1,), points=("2.5:K2", "2.5:S2"),
        evidence=(Evidence("code:tools-reference", _GLOB), Evidence("code:tools-reference", "Read only reads files, not directories.")),
        qtype="choose", level="medium", principle="fit_for_purpose",
        situation="March tickets exported as files whose date is only in the name",
        trap="search contents for a date the body stores differently",
    ),
    # ---- K3: Read/Write whole files, Edit unique match ----
    MCQ(
        id="Q2.5-07",
        q=("In a 600-line `settings.py`, the agent must change the default `MAX_RETRIES = 3` to 5. That line appears once, and "
           "nothing else in the file should change. Which operation makes the change with the least risk to the rest of the file?"),
        opts=("Read the file, then Write the whole file back with the single value changed.",
              "Write a new file that holds only the changed line and let the loader merge it.",
              "Edit the line, replacing `MAX_RETRIES = 3` with `MAX_RETRIES = 5`.",
              "Grep for the line, then Write the matching line over the file at that position."),
        ans=2,
        explain=("Changing text that appears once is what Edit is for, and every other line stays as it was. Read plus Write would "
                 "retype 600 lines to change one, which is where accidental changes creep in (A). Write does not merge, so B relies "
                 "on a feature it lacks. D assumes Write can place text at a position, but Write replaces the whole file."),
        scenarios=(4,), points=("2.5:K3",),
        evidence=(Evidence("code:tools-reference", "For partial changes to an existing file, Claude uses Edit instead of Write."),
                  Evidence("code:tools-reference", "The Edit tool performs exact string replacement.")),
        qtype="choose", level="easy", principle="proportionate",
        situation="one default value changed in a 600-line settings file",
        trap="rewrite the whole file for a single-line change",
    ),
    MCQ(
        id="Q2.5-08",
        q=("The support team's agent project keeps its dependencies in `pyproject.toml`. To add a `[tool.pytest]` section, the agent "
           "called Write with just the three new lines and reported success. The next build fails because the project name and every "
           "dependency are missing from the file. What is the most likely root cause?"),
        opts=("Write replaces a file with the content it is given, and it was given only the new section.",
              "Write merges by section header, and it matched `[tool.pytest]` against the wrong table.",
              "The agent did not Read first, so the tool threw away the copy of the file that it had stored.",
              "Write appended the section, and the TOML parser then dropped the keys above the new one."),
        ans=0,
        explain=("Write creates or overwrites a file with the full content provided, so a three-line call leaves a three-line file. "
                 "Adding a section needs Edit, or Read plus a Write of the complete file. B and D credit Write with merge or append "
                 "behaviour it does not have. C blames a missing Read, which is not why content disappears."),
        scenarios=(1,), points=("2.5:K3",),
        evidence=(Evidence("code:tools-reference", _WRITE),),
        qtype="diagnose", level="medium", principle="fit_for_purpose",
        situation="dependencies vanish after Write is given only a new config section",
        trap="assume Write adds to the file",
    ),
    MCQ(
        id="Q2.5-09",
        q=("After two failed Edit calls on a config file, a teammate proposes a convention for the developer productivity agent: "
           "make every change with Read followed by Write, since that never fails to find the text. Over a month the agent makes "
           "about 300 small changes, mostly single-line fixes to text that appears once, and reviewers have started to see unrelated "
           "lines changed in the diffs. How should you evaluate the proposal?"),
        opts=("Adopt it: a complete rewrite is more reliable than text matching, and the diffs will settle as the agent adapts.",
              "Reject it: Edit suits targeted changes, and Read plus Write is the fallback when no unique text exists.",
              "Adopt it, and add a check that reverts unrelated line changes after every Write.",
              "Reject it, and move every change to Edit with `replace_all` so that no anchor text is ever ambiguous."),
        ans=1,
        explain=("Edit changes only the text it matches, so the rest of the file stays as written; a whole-file rewrite is the fallback "
                 "for when no unique anchor exists, and it means the agent regenerates every line, so unrelated lines can change. A treats the symptom as "
                 "a habit that will pass. C patches the output of the wrong tool choice. D would change every occurrence of the "
                 "text, not the one that was meant."),
        scenarios=(4,), points=("2.5:K4", "2.5:K3"),
        evidence=(Evidence("code:tools-reference", "For partial changes to an existing file, Claude uses Edit instead of Write."),
                  Evidence("code:tools-reference", _UNIQ)),
        qtype="evaluate", level="medium", principle="proportionate",
        situation="convention to replace Edit with Read plus Write after two anchor failures",
        trap="use the whole-file fallback for every change",
    ),
    # ---- K4: non-unique text, Read + Write fallback ----
    MCQ(
        id="Q2.5-10",
        q=("The agent edits a Makefile and tries to replace the line `    $(CC) -o app main.o`, typed with four spaces, with a new "
           "link line. Edit returns an error saying the text was not found. The agent assumes the line is too common to match, "
           "and starts a Read plus Write of the 400-line file. What is the right response to the error?"),
        opts=("Switch to `replace_all`, because an Edit error means the line occurs more than once.",
              "Look at the line as the file holds it, copy its exact indentation, and retry Edit.",
              "Carry on with Read plus Write, which copes with any Edit error at no extra cost.",
              "Retry Edit with extra lines around the target, since more context makes a match more likely."),
        ans=1,
        explain=("Edit needs the text exactly as written, to the character of whitespace, and a Makefile indents recipe lines with "
                 "tabs, so the text really was absent. Fixing the call fixes the problem. A mistakes a missing match for several "
                 "matches. C rewrites 400 lines to avoid a one-character fix. D adds context around the same wrong indentation."),
        scenarios=(4,), points=("2.5:K3", "2.5:K4"),
        evidence=(Evidence("code:tools-reference", "`old_string` must appear in the file exactly as written. A single character of whitespace or indentation difference is enough to miss."),),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="Edit reports text not found on a tab-indented Makefile line typed with spaces",
        trap="treat any Edit failure as a reason for the Read plus Write fallback",
    ),
    MCQ(
        id="Q2.5-11",
        q=("A support knowledge-base export, `kb_export.json`, is 9,000 lines and has the same `\"status\": \"draft\"` line in 200 "
           "entries whose surrounding lines are byte-identical, so no unique context exists. Edit rejects the change, so the agent "
           "reads the file in three pages with `offset` and `limit`, assembles the content and writes it back with the one entry "
           "fixed. The next day the file holds 6,000 lines, the entries from the last third are missing, and the export job fails. "
           "What is the most likely root cause?"),
        opts=("Write keeps at most two thirds of any file, so the tail was dropped when the file was saved.",
              "The failed Edit left the file locked, so the later write kept only the part that had been flushed.",
              "The pages were stitched together for Write, and the last page was left out of the content.",
              "Write merged the new text into the file by line number and removed the entries after the changed line."),
        ans=2,
        explain=("Write overwrites the file with exactly the content it is given, so anything the agent left out of that content is "
                 "gone. The Read plus Write fallback works only when the complete file is written back, and when the file is paged "
                 "that includes every page. A and D invent a size limit and a merge, and B invents a lock."),
        scenarios=(1,), points=("2.5:K4",),
        evidence=(Evidence("code:tools-reference", _WRITE),),
        qtype="diagnose", level="medium", principle="preserve_information",
        situation="paged read of a 9,000-line export written back without its last page",
        trap="write back less than the whole file",
    ),
    MCQ(
        id="Q2.5-12",
        q=("A service is moving from `old-api.internal` to `new-api.internal`. In the 800-line `client.ts`, the host name appears in "
           "12 places and every one of them must change. Edit rejects the first attempt because the text appears more than once, "
           "and the agent starts planning to read the file and write it back in full. What is the most proportionate way to finish?"),
        opts=("Edit each of the 12 places separately, adding surrounding lines so that every call has a unique anchor.",
              "Read the file and Write it back in full, because Read plus Write is the fallback for repeated text.",
              "Grep for the host name and ask the developer to change the 12 lines by hand.",
              "Edit again with `replace_all` set, which replaces every occurrence in one call."),
        ans=3,
        explain=("When every occurrence should change, `replace_all` does it in one call. Read plus Write is for text that cannot be "
                 "pinned to the one place that should change, and nothing here needs pinning (B). A does the same job in twelve "
                 "calls, where one call is the fewest. C gives up on a change the tools can make."),
        scenarios=(4,), points=("2.5:K3",),
        evidence=(Evidence("code:tools-reference", _UNIQ),),
        qtype="choose", level="easy", principle="proportionate",
        situation="host name renamed in 12 places of one file",
        trap="reach for Read plus Write when replace_all fits",
    ),
    # ---- S1: choose Grep ----
    MCQ(
        id="Q2.5-13",
        q=("A production log shows `InvoiceRounding: negative remainder -0.03 on line 4`. The agent must find where the service "
           "raises this error. The amount and the line number change on every occurrence, and the message is built in several "
           "modules. Which search is best?"),
        opts=("Grep for the full logged line, including `-0.03` and `line 4`, so that the match is exact.",
              "Grep for the fixed text `InvoiceRounding: negative remainder`, then read the matches.",
              "Glob for `**/*rounding*` and read each file whose name matches.",
              "Grep for `negative`, which is the most distinctive word in the message."),
        ans=1,
        explain=("Grep matches text in the source, and the source holds only the constant part of the message; the amount and line "
                 "are filled in at run time. A searches for values that never appear in code. C finds files named like the error, "
                 "not the code that raises it. D matches a common word all over the codebase."),
        scenarios=(1,), points=("2.5:S1",),
        evidence=(Evidence("code:tools-reference", _GREP),),
        qtype="choose", level="medium", principle="fit_for_purpose",
        situation="log line with run-time values used to find where an error is raised",
        trap="search for the full logged line including its values",
    ),
    MCQ(
        id="Q2.5-14",
        q=("A research agent audits 300 tracked documentation pages to find every page that cites Smith 2021. Its Grep for "
           "`Smith 2021` returns 4 pages, but the author knows the paper is cited on roughly 30. Opening three of the missed pages "
           "shows the citation on a single line in each, for example `Smith (2021)` and `Smith et al., 2021`. What is the most likely root cause?"),
        opts=("Grep respects `.gitignore`, and most of the missing pages are ignored by git.",
              "Patterns match within one line, and the citation is split across a line break on the missed pages.",
              "The literal pattern fits one way of writing the citation, and other pages write it differently.",
              "Grep returns only the first file in each folder unless the output mode is changed to show content."),
        ans=2,
        explain=("A literal string matches one spelling. Grep takes a regular expression, so a single pattern that allows an optional "
                 "comma, parentheses or `et al.` covers the variants. The pages are tracked, which rules out A. Each citation sits on "
                 "one line, which rules out B. D is wrong because the default mode lists every file that matches."),
        scenarios=(3,), points=("2.5:S1",),
        evidence=(Evidence("code:tools-reference", "Grep is built on ripgrep and uses ripgrep's regex syntax, not POSIX grep."),),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="literal citation search finds 4 of about 30 pages",
        trap="blame ignore rules or line breaks instead of the literal pattern",
    ),
    MCQ(
        id="Q2.5-15",
        q=("Before deleting `format_legacy_ticket` from a Python service, the agent greps for the name with the `type` option set to "
           "`py` and finds no callers. After the deletion, the nightly export job fails with a missing-function error that comes from "
           "`ops/nightly.yml`, which names the function as a string. What is the most likely root cause?"),
        opts=("Grep ignores files that have not changed recently, and the YAML file had been stable for a year.",
              "Grep patterns cannot match inside quote marks, so a function named in a string is invisible.",
              "The agent used the wrong output mode, so matches in the YAML file were counted but never listed.",
              "The search covered Python files only, so the YAML reference was never looked at."),
        ans=3,
        explain=("The `type` option restricts a search to one language, which suits finding Python callers and hides every other kind "
                 "of file. Before deleting something, search all file types, or add each type that can hold a reference. A invents "
                 "a recency rule, B invents a limit on strings, and C is wrong because every output mode reports the files that "
                 "match."),
        scenarios=(4,), points=("2.5:S1",),
        evidence=(Evidence("code:tools-reference", "Claude can scope results by file with the `glob` parameter, such as `**/*.tsx`, or by language with the `type` parameter, such as `py` or `rust`."),),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="function deleted after a Python-only search misses a YAML job reference",
        trap="blame a recency rule instead of the file-type scope",
    ),
    # ---- S2: choose Glob ----
    MCQ(
        id="Q2.5-16",
        q=("Four services each keep a `db/migrations/` folder with several hundred files named like `0098_add_index.sql`, "
           "`0150_drop_old_table.sql` and `0231_backfill.sql`. The agent must list the migrations numbered 0100 to 0199 in all four, "
           "about 40 files in total. Which call returns them?"),
        opts=("Grep for the numbers `0100` to `0199` in the contents of the migration files.",
              "Glob with `**/db/migrations/*.sql`, then keep the files whose numbers fall in the range by reading each name.",
              "Glob with `**/db/migrations/01*.sql`, which selects by the number at the start of each name.",
              "Read each `db/migrations` folder and note the files in the range from the listing."),
        ans=2,
        explain=("The range is written into the file names, so a name pattern selects it directly. B returns every migration in the "
                 "four folders, and Glob caps its list at 100 files, so the range could be cut off before the filtering even starts. "
                 "A searches the contents for numbers that appear in names. D fails because Read opens files, not directories."),
        scenarios=(4,), points=("2.5:S2",),
        evidence=(Evidence("code:tools-reference", "Results are sorted by modification time and capped at 100 files."),
                  Evidence("code:tools-reference", "`**/*.js` matches all `.js` files at any depth")),
        qtype="configure", level="medium", principle="fit_for_purpose",
        situation="migrations numbered 0100 to 0199 selected across four services",
        trap="list every migration and filter by hand",
    ),
    MCQ(
        id="Q2.5-17",
        q=("A research agent has 900 filings saved as `AAPL_10K_2023.htm`, `AAPL_10Q_2023Q2.htm` and so on, one folder per company. "
           "It must collect the annual reports (10-K) for 2023, about 60 files. The quarterly filings mention the annual report often. Which "
           "approach is best?"),
        opts=("Glob with `**/*_10K_2023.htm`, which selects those files by name.",
              "Grep for `10-K` in the contents of every filing and keep the files that contain it.",
              "Grep for `10-K` and `2023` together in each file and keep the files where both appear.",
              "Glob for `**/*.htm` and open the first lines of each file to check the filing type."),
        ans=0,
        explain=("The filing type and year are part of every file name, so a name pattern picks the right set without opening a file. "
                 "Quarterly filings also say 10-K, so contents searches pull them in (B, C). D lists all 900 files, where the result "
                 "is capped at 100, and then checks them one by one."),
        scenarios=(3,), points=("2.5:S2",),
        evidence=(Evidence("code:tools-reference", _GLOB),),
        qtype="choose", level="easy", principle="fit_for_purpose",
        situation="annual filings for one year picked from 900 files named by type and year",
        trap="search contents for a filing type that quarterly files also mention",
    ),
    MCQ(
        id="Q2.5-18",
        q=("A developer asks the agent to list the TypeScript source files of a web app, to plan a new lint rule. The app keeps its "
           "code under `src/`, and the project root also holds `dist/`, full of compiled `.d.ts` files, and a `node_modules/` folder, and `src/` holds about 80 `.ts` files. "
           "Which Glob pattern returns the right set?"),
        opts=("`**/*.ts`, which matches `.ts` files at any depth in the project.",
              "`src/**/*.ts`, which matches the `.ts` files under `src/`.",
              "`*.ts`, which matches the `.ts` files in the project root.",
              "`src/*.ts`, which matches every `.ts` file inside `src/`."),
        ans=1,
        explain=("Scoping the pattern to `src/` with `**` reaches nested source files and leaves out `dist/` and `node_modules/`, which "
                 "Glob would otherwise return because it does not apply `.gitignore` by default. A returns compiled and third-party "
                 "files as well. C finds only files in the project root (C). D reaches only the files directly inside `src/`."),
        scenarios=(4,), points=("2.5:S2",),
        evidence=(Evidence("code:tools-reference", "`src/**/*.ts` matches all `.ts` files under `src/`"),
                  Evidence("code:tools-reference", "Glob doesn't respect `.gitignore` by default, so it finds gitignored files alongside tracked ones.")),
        qtype="configure", level="medium", principle="fit_for_purpose",
        situation="TypeScript sources listed in a project that also holds compiled output and dependencies",
        trap="match the extension at every depth from the project root",
    ),
    # ---- S3: Read then Write when Edit has no unique anchor ----
    MCQ(
        id="Q2.5-19",
        q=("In a long session, the agent read `deploy.yaml` 40 turns ago. Its Edit to a `replicas` line now fails because the text "
           "appears in three services' blocks that are byte-identical for several lines around the target, so no unique context exists, and the agent plans to Write the whole file from its earlier summary with the one "
           "line changed. Meanwhile a teammate has pulled two commits that changed that file. What should the agent do?"),
        opts=("Write from the summary, since the summary keeps the structure and only the replicas line differs.",
              "Retry Edit with `replace_all`, then restore the other two services' values from the summary.",
              "Write now, then compare the result with the repository using Grep and repair the differences.",
              "Read the file again now, then Write it back in full with only the replicas line changed."),
        ans=3,
        explain=("Read plus Write rewrites the file with what was read, so the read must be fresh: the rewrite then starts from the "
                 "file as it is today, including the teammate's commits. A and C overwrite those commits with older content. B "
                 "changes all three blocks first and relies on a summary to undo two of them."),
        scenarios=(4,), points=("2.5:S3",),
        evidence=(Evidence("code:tools-reference", _WRITE),),
        qtype="fix", level="medium", principle="preserve_information",
        situation="whole-file write planned from a 40-turn-old summary of a changed deploy file",
        trap="write from memory instead of a fresh read",
    ),
    MCQ(
        id="Q2.5-20",
        q=("A research pipeline's `config.toml` has 80 lines and needs nine scattered changes to move it to a new schema. Some of "
           "the changes alter lines that other changes use as their anchor text, and after the third Edit two of the remaining "
           "anchors have become identical to other lines, with byte-identical lines around them, so no unique context exists and those calls fail. Which approach is most reliable?"),
        opts=("Read the file once and Write it back with all nine changes made together.",
              "Run the nine Edit calls again in a different order until all of them are accepted.",
              "Set `replace_all` on the failing Edit calls, then correct any lines that changed by mistake.",
              "Make nine temporary copies of the file with Write, edit one in each, and merge them."),
        ans=0,
        explain=("Nine interacting changes to a short file are one rewrite: read it once and write the full updated content, so no "
                 "change depends on the text another change left behind. B is trial and error that may never settle. C alters lines "
                 "that were meant to stay. D adds nine writes and a merge step."),
        scenarios=(3,), points=("2.5:S3",),
        evidence=(Evidence("code:tools-reference", _WRITE),),
        qtype="fix", level="hard", principle="deterministic",
        situation="nine interdependent changes to a short config where later anchors turn non-unique",
        trap="reorder the Edit calls until they stop failing",
    ),
    MCQ(
        id="Q2.5-21",
        q=("A config-maintenance subagent is defined with `tools: [\"Read\", \"Grep\", \"Edit\"]`. About 4% of its runs end with "
           "\"could not apply change\", always where the line to change is repeated in the file, and each failure is an Edit error "
           "saying the text appears more than once, in blocks that are byte-identical around the target so no unique context exists. "
           "What is the smallest change that lets those runs succeed?"),
        opts=("Add `Bash`, so that the subagent can edit with `sed` when Edit refuses.",
              "Add `Write`, so it can read the file and write the whole file back.",
              "Replace `Edit` with `Write`, since rewriting whole files avoids matching problems.",
              "Add `Glob`, so that it can find a second copy of each file to edit instead."),
        ans=1,
        explain=("The fallback for an Edit with no unique anchor is Read plus Write; the subagent already has Read, so adding Write is "
                 "the smallest addition that completes it. A adds a shell for a job the file tools can do. C drops targeted "
                 "edits that work in 96% of runs and turns every small change into a rewrite. D finds files by name, which has "
                 "nothing to do with the failure."),
        scenarios=(4,), points=("2.5:S3",),
        evidence=(Evidence("code:agent-sdk/subagents", "Use the `tools` field to limit what a subagent can do:"),),
        qtype="configure", level="medium", principle="least_privilege",
        situation="subagent with Read, Grep and Edit fails on repeated lines",
        trap="grant a shell instead of the missing write tool",
    ),
    # ---- S4: build understanding step by step ----
    MCQ(
        id="Q2.5-22",
        q=("A new developer asks the agent where invoice PDFs are produced in a 2,000-file Django project and how the data reaches "
           "the renderer. The agent's first plan is to read every file under `billing/` and `documents/`, about 300 files. Which "
           "plan is the most effective?"),
        opts=("Glob every Python file in both folders and read them in order of last modification.",
              "Read `billing/models.py` in full, since the data for an invoice comes from the models.",
              "Read the settings file and the README, then describe the flow from the module names.",
              "Grep for the rendering call, then Read its callers and follow their imports."),
        ans=3,
        explain=("A content search locates where the PDF is rendered, and reading then follows the trail from there, so only the files "
                 "on the path are loaded. The original plan and A still load hundreds of files up front. B reads one file and assumes "
                 "it holds the whole answer. C describes a flow from names, which is a guess."),
        scenarios=(4,), points=("2.5:S4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 2.5 Skill 4 states the Grep-then-Read approach; no official page prescribes an order for exploring a codebase.",
        qtype="choose", level="medium", principle="proportionate",
        situation="where invoice PDFs are produced in a Django project",
        trap="read the models file and assume it holds the whole flow",
    ),
    MCQ(
        id="Q2.5-23",
        q=("A research agent explains `bootstrap_ci` in an unfamiliar statistics library. It reads `core.py` (3,800 lines) in pages, "
           "then three more large modules, and the context window fills before it answers. The trace shows that the function is "
           "defined in 90 lines of the second module and called from two places. What is the most likely root cause?"),
        opts=("The window is too small for any library of this size, so a model with a larger context window is the remedy.",
              "Read returns files in pages, so each file takes many calls, and the number of calls is what filled the window.",
              "The agent opened whole modules to find the function instead of locating it first and reading only the trail.",
              "The agent should have listed the modules with Glob first, because Read cannot open a file it has not listed."),
        ans=2,
        explain=("The function was in 90 lines and had two callers, so a search for its name would have pointed straight to what "
                 "mattered; reading modules in the hope of meeting it loaded thousands of lines that did not. A makes the window "
                 "bigger without changing the habit. B counts calls, when the volume read is the problem. D invents a listing "
                 "requirement."),
        scenarios=(3,), points=("2.5:S4",),
        evidence=(Evidence("code:tools-reference", "an error telling it to read a portion with `offset` and `limit`, or to search for specific content with Grep instead"),),
        qtype="diagnose", level="hard", principle="root_cause",
        situation="explaining one function exhausts context after reading four large modules",
        trap="blame the window size or the page count instead of the read-everything habit",
    ),
    MCQ(
        id="Q2.5-24",
        q=("Two onboarding prompts for the support-agent codebase are compared on the same 20 questions about a 3,000-file repository. "
           "Prompt X says to read the files under `src/` before answering. Prompt Y says to search for the entry point and then read "
           "along the imports it leads to. Both answered all 20 questions with 17 correct. X averaged 85% of the context window used "
           "at the moment it answered, and Y averaged 25%. Users will ask several follow-up questions in the same session. How "
           "should you evaluate the two?"),
        opts=("Prefer Y: accuracy is equal, and it leaves most of the window free for follow-ups.",
              "Treat them as equal, since both got 17 of 20 and accuracy is what the team is measuring.",
              "Prefer X, because reading every file means that no file was missed.",
              "Prefer X, and move it to a model with a bigger window so the follow-up questions have room."),
        ans=0,
        explain=("Accuracy is the same, so the difference is what each approach costs: X has used most of the window before the first "
                 "follow-up, while Y has room to continue. B ignores a difference that will matter in a session with follow-ups. C "
                 "rests on reading everything, which produced no better answers here. D keeps the read-everything habit and pays "
                 "for a bigger window to hide it."),
        scenarios=(1,), points=("2.5:S4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 2.5 Skill 4 prefers incremental exploration; comparing two prompts on context use is an evaluation judgment, not a documented behaviour.",
        qtype="evaluate", level="easy", principle="proportionate",
        situation="read-first and search-then-follow prompts with equal accuracy and unequal context use",
        trap="treat equal accuracy as equal quality and buy a bigger window",
    ),
    MCQ(
        id="Q2.5-25",
        q=("A support platform's `gateway.submit_charge(order, amount)` is wrapped by a `PaymentsClient` class whose public methods "
           "`charge()` and `charge_async()` call it, and application code uses only the client. The team will change the signature of "
           "`submit_charge` and wants every affected call site. A Grep for `submit_charge` returns 2 hits, both inside "
           "`PaymentsClient`. What should the agent do next?"),
        opts=("Report the 2 hits as the affected sites, since nothing outside the client mentions the function.",
              "Grep for `PaymentsClient` and count every file that imports the class as an affected site.",
              "Read `PaymentsClient` for the methods that call `submit_charge`, then Grep for each method name.",
              "Grep for `submit` and `charge` separately, which will surface any caller that spells the name differently."),
        ans=2,
        explain=("Callers reach the function through the client's methods, so the names to search for are the ones the wrapper exposes. "
                 "A takes the wrapper's own two hits for the whole picture. B counts every importer, whether or not it calls the "
                 "affected methods. D matches two common words and finds callers by luck, not by the names they use."),
        scenarios=(1,), points=("2.5:S5",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 2.5 Skill 5 describes tracing usage through wrapper modules by listing exported names; no official page addresses it.",
        qtype="fix", level="hard", principle="explicit",
        situation="charge function reached only through two methods of a client class",
        trap="count importers of the wrapper as usages",
    ),
    MCQ(
        id="Q2.5-26",
        q=("A data-loading helper `read_docs` lives in `pkg/_impl.py`. `pkg/compat.py` re-exports it as `load_corpus`, and "
           "`pkg/__init__.py` exports it only as `open_corpus`. Researchers import from `pkg` or from `pkg.compat`. The team "
           "will change the helper's return type and needs every affected call site. Which search plan covers them?"),
        opts=("Grep for `read_docs`, since every alias is defined from that name and the imports follow it.",
              "Grep for `open_corpus`, the name at the top of the chain and the one researchers import.",
              "Read only `pkg/__init__.py`, take its exported names, and Grep for those.",
              "Read each re-exporting module to list the helper's names, then Grep for all of them."),
        ans=3,
        explain=("Researchers can import the helper under either public name, so the plan has to follow the chain through each module and "
                 "search for every name it carries: `load_corpus` and `open_corpus`. A finds only the definition and the re-export "
                 "lines. B misses everyone who imports `load_corpus` from `pkg.compat`. C gets only `open_corpus` from the package file and misses `load_corpus`."),
        scenarios=(3,), points=("2.5:S5",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 2.5 Skill 5 describes tracing through wrapper modules; no official page addresses a chain of re-exports.",
        qtype="fix", level="hard", principle="explicit",
        situation="helper re-exported under a new name at two layers of one package",
        trap="search the top-layer name only",
    ),
    MCQ(
        id="Q2.5-27",
        q=("Two packages each define a helper named `format_date`: `billing/_dates.py` and `reports/_dates.py`. `billing/__init__.py` "
           "exports the billing one, and every caller imports it with a line like `from billing import format_date`. The team will "
           "change the billing helper's output and needs its callers. A Grep for `format_date` returns 85 hits across the repository. "
           "Which plan is best?"),
        opts=("Treat all 85 hits as callers, since they use the same name.",
              "Read the package file for its export, then Grep for import lines naming `billing` and `format_date`.",
              "Read each of the 85 matching files in full to decide which helper it calls.",
              "Rename the reports helper first, then Grep for `format_date` again and see which files still match it."),
        ans=1,
        explain=("The import line says which helper a file uses, so searching for that line narrows 85 hits to the billing callers, and "
                 "the exported name then leads to their calls. A counts the reports callers too. C opens whole files when one line "
                 "settles it. D changes code in order to search it, and only shows what breaks."),
        scenarios=(4,), points=("2.5:S5",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 2.5 Skill 5 describes tracing usage through exported names; separating same-named helpers by their import line is a judgment no official page states.",
        qtype="choose", level="medium", principle="fit_for_purpose",
        situation="same-named helpers in two packages and 85 search hits",
        trap="count every same-named hit as a caller",
    ),
)
