"""
Community study material for the Claude Certified Architect – Foundations exam, collated for section 10 · MCQs.

Found 2026-10-10 by: GitHub repository search (gh search repos, four queries), web search (GitHub, GitLab, general
websites) and GitLab's public project-search API. Stars, licence and last-push date are as GitHub reported them that day.

HOW THESE ARE USED (CLAUDE.md source-of-truth rules): topic and trap coverage only. The official exam guide decides scope,
the official docs decide technical facts, and a community source is unverified. No question text, option or explanation is
copied: none of the repositories read carries an open licence (the two you named have none), so their text stays theirs.
Every MCQ is original and carries a word-for-word quote from an official page instead.
"""

FOUND_ON = "2026-10-10"

# (repo, stars, licence, last push, what it is, read by me?)
GITHUB = (
    ("paullarionov/claude-certified-architect", 5004, "none", "2026-10-02",
     "Study guide in 15 languages (EN markdown, PDF, EPUB) + Anki deck; chapters on API, tools, Agent SDK, MCP, Claude Code, prompts, batch, context, provenance",
     "yes — the MCP chapter, the commands/skills sections and the README"),
    ("OlivierAlter/Claude-Certified-Architect-Foundations-Certification-Exam", 242, "none", "2026-03-15",
     "77 scenario-based practice questions with answers (a Claude Code skill runs them interactively)",
     "yes — the README, the task index, and the MCP / skills questions (for topic coverage only)"),
    ("daronyondem/claude-architect-exam-guide", 1116, "other", "2026-06-10",
     "One long exam-preparation guide (about 180 KB of markdown)", "tree only"),
    ("dnacenta/claude-certified-architect", 129, "none", "2026-09-26",
     "Domain-by-domain guide with code, anti-patterns and practice questions; also a website and a PDF",
     "yes — domain 2 (MCP configuration) and the skills section of domain 3"),
    ("hamzafarooq/claude-certified-architect", 159, "MIT", "2026-09-10",
     "Domain cheat sheets, sample questions and a local HTML practice exam", "tree only"),
    ("timothywarner-org/claude-architect", 93, "MIT", "2026-09-19",
     "Study path, a 136 KB practice-questions file, claude-cookbooks code and skills examples", "tree only"),
    ("aderegil/claude-certified-architect", 108, "other", "2026-05-19",
     "Guided labs: 6 scenarios, 5 domains, 30 tasks", "not opened"),
    ("utkarsh1agarwal/claude-architect-exam-guide", 30, "other", "2026-07-28",
     "Study guide and 6 mock exams (360 questions, per its description)", "not opened"),
    ("haytamAroui/Claude-Certified-Architect", 8, "MIT", "2026-03-27",
     "6 courses and 120 practice questions (per its description)", "not opened"),
    ("Connectry-io/connectrylab-architect-cert-mcp", 38, "MIT", "2026-03-19",
     "An MCP server for exam prep; 390 questions with spaced repetition (per its description)", "not opened"),
    ("hong-chu/claude-certified-architect-foundations-llm-wiki", 28, "CC-BY-4.0", "2026-06-12",
     "Domain-organised study wiki", "not opened"),
    ("termidy/CCAR-F", 39, "none", "2026-09-21", "Repository named CCAR-F", "not opened"),
    ("ankitrahejagatech/claude-certified-architect-prep", 27, "none", "2026-06-23",
     "Interactive practice exam, 5 domain cheat sheets, official sample questions", "not opened"),
    ("wbhm/claude-certified-architect-foundations-study-guide", None, "unknown", "unknown",
     "Notes on all 5 domains, decision rules, practice sets, runnable Claude API exercises", "found by web search; stats not fetched"),
    ("sarveshtalele/claude-architect-exam-guide", None, "unknown", "unknown",
     "Curated resources, Claude skills and a learning path (CCAR-F and CCAR-P)", "found by web search; stats not fetched"),
)

# Websites (found by web search; not opened beyond the search result, so no claim is made about their content quality)
WEBSITES = (
    ("tutorialsdojo.com", "https://tutorialsdojo.com/ccar-f-claude-certified-architect-foundations-study-guide/", "study guide; practice tests listed as paid"),
    ("certified-architect.com", "https://certified-architect.com/", "mock exam and study guides (free trial, then paid, per the search result)"),
    ("claudecertificationguide.com", "https://claudecertificationguide.com/", "lessons, practice questions and a mock exam, described as free"),
    ("open-exam-prep.com", "https://open-exam-prep.com/practice/anthropic-cca-f", "100 free exam-style questions, per the search result"),
    ("claudecertifiedarchitects.com", "https://www.claudecertifiedarchitects.com/cca-practice-questions/", "free sample, larger bank behind it"),
    ("certsafari.com", "https://www.certsafari.com/anthropic/claude-certified-architect-foundations", "practice questions (paid)"),
    ("preporato.com", "https://preporato.com/certificates/claude-certified-architect", "practice tests (paid)"),
    ("re-cinq.com blog", "https://re-cinq.com/blog/claude-certified-architect-foundations-exam", "a study write-up"),
    ("Udemy", "https://www.udemy.com/course/new-claude-certified-architect-foundations-cca-f-exams/", "a paid practice-test course"),
)

GITLAB = ("No GitLab project was found. GitLab's public project-search API returned 0 results for “claude-certified-architect” "
          "and “claude architect exam”, and the one hit for “CCA-F” was unrelated (a 2022 ESG project). Web search surfaced "
          "only GitHub repositories. Private or unindexed GitLab projects would not appear.")

# Where a community source differs from the official docs, found by checking what I READ against the docs.
# Each row: (source, what it says, what the official docs say, who agrees with the docs, used in)
DISAGREEMENTS = (
    ("paullarionov guide, §5.5 (frontmatter table)",
     "`allowed-tools`: “Restricts which tools are available”",
     "`allowed-tools` pre-approves the listed tools for the turn; it “does not restrict which tools are available: every tool remains callable”. `disallowed-tools` or a deny rule removes tools.",
     "dnacenta §3.2 (“Tools pre-approved while this skill is active”)",
     "Skills Q3"),
    ("paullarionov guide, §4.3",
     "MCP scoping is two-way: project (`.mcp.json`) and user (`~/.claude.json`)",
     "Three scopes. The default for `claude mcp add` is LOCAL: private to you, per project, also stored in `~/.claude.json`. Same-name precedence is local, then project, then user; the whole entry is used, nothing is merged.",
     "dnacenta §2.4 lists local, project, user and managed",
     "MCP Q1 and Q10"),
    ("paullarionov guide, §5.5 (frontmatter table)",
     "`argument-hint`: “asks for an argument when invoked without parameters”",
     "A hint “shown during autocomplete”. It does not prompt or validate. If no placeholder in the body uses an argument, Claude Code appends `ARGUMENTS: <value>` to the skill.",
     "dnacenta §3.2 (“Hint shown in autocomplete”)",
     "Skills Q4"),
    ("Exam guide TS 3.2, skills bullet 3",
     "Use `allowed-tools` “to restrict tool access during skill execution”",
     "The docs are more precise (pre-approval, not restriction). Project rule: the guide decides what is examinable, the docs decide technical facts, so the question tests the docs' behaviour and the explanation says where the wording differs.",
     "—",
     "Skills Q3 explanation"),
)
