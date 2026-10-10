"""
Section 10 · MCQs — 20 original exam-style questions: 10 on MCP, 10 on Claude Skills.

HOW THEY WERE BUILT AND CHECKED (nothing here is a guess):
  1. Scope: the official exam guide, TS 2.4 and TS 2.2 for MCP, TS 3.2 for Skills (positions in utils/guide_index.py).
  2. Topics and traps: the community repositories in utils/study_repos.py, read for WHAT they test, never copied.
  3. Facts: every correct answer carries one or more WORD-FOR-WORD quotes from an official page (Evidence below).
     `python -m utils.mcq_verify` re-downloads those pages and checks that every quote is still on them.
  4. Live checks: three MCP answers were also observed on the real Claude Code CLI (2.1.168) in an isolated config
     directory (see `live` on those items).
  5. Every wrong option is refuted in the explanation, and where it can be, by a quote too.

Style follows CLAUDE.md's QUESTION RULE: a production symptom with numbers, a hidden qualifier, four options that are each
a real engineering move, the correct option never the longest, and correct positions spread across A–D.
Not in the exam question bank (utils/question_bank.py): these sit in their own section until the owner signs them off.
"""

from dataclasses import dataclass

from utils.guide_index import point_ref

CHECKED_ON = "2026-10-10"

# key -> (page title, URL shown to the reader, URL fetched by the verifier)
SOURCES = {
    "cc_mcp": ("Claude Code: Connect to tools via MCP", "https://code.claude.com/docs/en/mcp",
               "https://code.claude.com/docs/en/mcp.md"),
    "cc_skills": ("Claude Code: Extend Claude with skills", "https://code.claude.com/docs/en/skills",
                  "https://code.claude.com/docs/en/skills.md"),
    "cc_memory": ("Claude Code: How Claude remembers your project", "https://code.claude.com/docs/en/memory",
                  "https://code.claude.com/docs/en/memory.md"),
    "mcp_concepts": ("MCP: Understanding MCP servers", "https://modelcontextprotocol.io/docs/learn/server-concepts",
                     "https://modelcontextprotocol.io/docs/learn/server-concepts.md"),
    "mcp_tools_spec": ("MCP specification (2026-07-28): Tools", "https://modelcontextprotocol.io/specification/2026-07-28/server/tools",
                       "https://modelcontextprotocol.io/specification/2026-07-28/server/tools.md"),
}


@dataclass(frozen=True)
class Evidence:
    src: str        # key in SOURCES
    quote: str      # copied word for word from that page (markdown links, backticks and ** are ignored when checking)


@dataclass(frozen=True)
class MCQ:
    id: str
    q: str
    opts: tuple
    ans: int
    explain: str
    scenarios: tuple            # guide scenarios 1 Support … 6 Extraction
    points: tuple               # guide bullets, "<ts>:<K|S><n>"
    evidence: tuple             # Evidence, …
    basis: str = "guide"        # "guide" = inside the guide's scope; "docs" = the behaviour is from the docs, beyond the guide's wording
    community: str = ""         # what the community repositories I read say about the same point
    live: str = ""              # what I observed on the real CLI, if anything

    def __post_init__(self):
        if len(self.opts) != 4 or not 0 <= self.ans < 4:
            raise ValueError(f"{self.id}: need 4 options and an answer index 0-3")
        for p in self.points:
            ts, b = p.split(":")
            point_ref(ts, b[0], int(b[1:]))          # raises if the guide has no such bullet
        if not self.points or not self.scenarios or not self.evidence:
            raise ValueError(f"{self.id}: needs guide points, a scenario and evidence")
        if not all(1 <= s <= 6 for s in self.scenarios):
            raise ValueError(f"{self.id}: scenario must be 1-6")
        for e in self.evidence:
            if e.src not in SOURCES:
                raise ValueError(f"{self.id}: unknown evidence source {e.src}")


# ══ MCP ══════════════════════════════════════════════════════════════════════════════════════════════════════════
MCP = (
    MCQ(
        id="MCP-01",
        q=("Your 12-engineer team uses Claude Code for developer productivity work. A platform engineer runs "
           "`claude mcp add --transport http jira https://jira-mcp.example.com/mcp` on her laptop and tells the team the "
           "Jira tools are ready. She sees the tools in every session in that repository. After pulling, none of the other "
           "11 engineers see them, and her setup left no changed files in `git status`. What is the most likely cause?"),
        opts=("Servers are shared only once they are described in the repository's CLAUDE.md file, so her setup never reached the team through git.",
              "She passed no `--scope`, so the server went in at the default local scope: private to her, not written to `.mcp.json`.",
              "HTTP servers can only be user-scoped, so each engineer must run the same command again with their own Jira account.",
              "Claude Code shares a server only after an administrator approves it in the organisation's managed settings, which has not happened yet."),
        ans=1,
        explain=("Local scope is the default for `claude mcp add`: the server loads only in that project, stays private to her, and is "
                 "stored in `~/.claude.json`, so nothing is written to the repository. Shared tooling belongs in a project-scoped "
                 "`.mcp.json` that is committed (`--scope project`). Why the others fail: CLAUDE.md holds instructions, not server "
                 "definitions; transport (HTTP or stdio) is independent of scope, and `--scope project` works for HTTP servers; and "
                 "managed settings are an optional admin route, not a gate that sharing must pass."),
        scenarios=(4,), points=("2.4:K1", "2.4:S1"),
        evidence=(Evidence("cc_mcp", "Local scope is the default. A local-scoped server loads only in the project where you added it and stays private to you."),
                  Evidence("cc_mcp", "Check `.mcp.json` into version control so everyone on your team gets the same MCP tools and services.")),
        community=("dnacenta §2.4 states the local default. paullarionov §4.3 describes only project and user scope, so it leaves the "
                   "default out, and it is the trap in this question."),
        live=("Claude Code 2.1.168, isolated config directory: `claude mcp add --help` prints “-s, --scope <scope> Configuration scope "
              "(local, user, or project) (default: \"local\")”, and a server added with no `--scope` was reported by `claude mcp get` as "
              "“Scope: Local config (private to you in this project)”."),
    ),
    MCQ(
        id="MCP-02",
        q=("A committed `.mcp.json` defines a Jira server with `\"env\": { \"JIRA_TOKEN\": \"${JIRA_TOKEN}\" }`. It works for the 11 "
           "engineers who export `JIRA_TOKEN` in their shell. A new engineer reports that the server starts but every Jira call "
           "comes back with a 401. Her shell has no `JIRA_TOKEN`. What is the most effective first step?"),
        opts=("Replace `${JIRA_TOKEN}` in `.mcp.json` with her literal token so that the file works on every machine.",
              "Delete the `env` block, because Claude Code reads missing credentials from the operating system keychain.",
              "Run `claude mcp list`, read the warning naming the unset variable, then export it and restart.",
              "Add a fallback such as `${JIRA_TOKEN:-team-shared-token}` so the file always resolves to a value."),
        ans=2,
        explain=("The configuration still loads when a referenced variable is unset: Claude Code warns about it in `claude mcp list` "
                 "and sends the unexpanded `${JIRA_TOKEN}` text as-is, which is why the server rejects the call with a 401. The warning "
                 "names the variable, so the fix is to export it. A and D put a secret in a file that is committed, which is exactly "
                 "what environment-variable expansion exists to avoid (guide TS 2.4, knowledge 2). B describes a keychain fallback "
                 "that does not exist."),
        scenarios=(4,), points=("2.4:K2", "2.4:S1"),
        evidence=(Evidence("cc_mcp", "If a referenced environment variable isn't set and has no default value, the config still loads: Claude Code reports a missing-variable warning for that server in `claude mcp list` output and uses the unexpanded `${VAR}` text as-is."),
                  Evidence("cc_mcp", "Claude Code supports environment variable expansion in `.mcp.json` files, allowing teams to share configurations while maintaining flexibility for machine-specific paths and sensitive values like API keys.")),
        community=("paullarionov §4.3 and dnacenta §2.4 both show `${VAR}` expansion; neither states what happens when the variable is "
                   "unset (dnacenta mentions `${VAR:-default}` only)."),
        live=("Claude Code 2.1.168, isolated config directory, `.mcp.json` with `\"TOKEN\": \"${CCARF_TEST_UNSET_TOKEN}\"`: `claude mcp list` "
              "printed “[Warning] [demo] mcpServers.demo: Missing environment variables: CCARF_TEST_UNSET_TOKEN” and the server showed "
              "“Pending approval”."),
    ),
    MCQ(
        id="MCP-03",
        q=("Your research agent's Claude Code session connects to 6 MCP servers that together expose about 90 tools. A teammate wants "
           "to cap each server at 10 tools because, in his words, “Claude Code limits tools per server and loads every definition at "
           "startup”. You check how current Claude Code behaves. Which statement should you give the team?"),
        opts=("Only tool names and server instructions load at startup; definitions load on demand, so there is no per-server cap.",
              "Claude Code enforces a fixed cap on tools per server, so any server that exposes more than that must be split in two.",
              "Tools load only from the first connected server; the others must be switched on with `/mcp` before their tools work.",
              "Tools from different servers are never visible together, so the agent must disconnect one server before using another."),
        ans=0,
        explain=("The guide expects tools from all configured servers to be discovered at connection time and available together "
                 "(TS 2.4, knowledge 3). The docs add that Claude Code defers the definitions by default: only names and server "
                 "instructions load at startup, so adding servers costs little context and there is no fixed per-server cap; the "
                 "practical limit is the context budget. B contradicts that, and C and D contradict the simultaneous availability the "
                 "guide describes and the multi-server design MCP is built for."),
        scenarios=(3,), points=("2.4:K3",), basis="docs",
        evidence=(Evidence("cc_mcp", "Only tool names and server instructions load at session start, so adding more MCP servers has minimal impact on your context window. Claude Code doesn't impose a fixed per-server tool cap; the practical limit is your context window budget."),
                  Evidence("mcp_concepts", "The real power of MCP emerges when multiple servers work together, combining their specialized capabilities through a unified interface.")),
        community=("dnacenta §2.4 (“Tool Search Is On by Default”) agrees. paullarionov §4.2 says tools from all connected servers are "
                   "available at once; it says nothing about deferred loading."),
    ),
    MCQ(
        id="MCP-04",
        q=("A data assistant for developer productivity queries a warehouse of 140 tables through one MCP tool, `query_table(name, "
           "filters)`. In 31% of sessions it spends 5 to 7 exploratory calls just discovering which tables and columns exist, and "
           "some sessions reach the turn limit before answering. The platform team owns the MCP server. Which change most directly "
           "removes the discovery overhead?"),
        opts=("Raise the agent's turn limit so the exploratory calls have room to finish before it has to give an answer to each user question.",
              "Add a system-prompt line telling the agent to list every table in the warehouse before it answers any question from a user.",
              "Replace `query_table` with 140 separate per-table tools so that every single table is visible in the agent's tool list at once.",
              "Expose the table catalogue (names, descriptions, columns) as an MCP resource that the application attaches as context."),
        ans=3,
        explain=("Resources exist to expose content catalogues such as database schemas, so the agent starts with a map instead of "
                 "discovering one call at a time (TS 2.4, knowledge 4 and skill 5). A raises the limit but leaves the 5 to 7 calls in "
                 "place; B turns the exploration into a required step; C over-provisions tools, which degrades tool selection "
                 "(TS 2.3). The application decides which resources to attach, which is the control model for resources."),
        scenarios=(4,), points=("2.4:K4", "2.4:S5"),
        evidence=(Evidence("mcp_concepts", "Passive data sources that provide read-only access to information for context, such as file contents, database schemas, or API documentation."),
                  Evidence("mcp_concepts", "Resources are application-driven, giving them flexibility in how they retrieve, process, and present available context."),
                  Evidence("cc_mcp", "Resources are automatically fetched and included as attachments when referenced")),
        community=("paullarionov §4.5 and OlivierAlter Q38 test the same idea (a catalogue exposed as a resource); this item uses a "
                   "different setup and different distractors."),
    ),
    MCQ(
        id="MCP-05",
        q=("Your team wants a standard “triage this ticket” workflow: fixed instruction text with two blanks, a ticket id and a "
           "severity. Engineers should start it on purpose from the slash menu. The model must not start it on its own, and it is an "
           "instruction template, not data. Which MCP primitive fits best?"),
        opts=("A tool, because tools accept typed arguments such as the ticket id and the severity.",
              "A prompt, which the user invokes; Claude Code lists it as a `/mcp__server__prompt` command.",
              "A resource at a fixed URI, because resources are read by the application rather than the model.",
              "An elicitation request, because it collects the ticket id and the severity from the user."),
        ans=1,
        explain=("MCP gives each primitive a different controller: tools are model-controlled, resources are application-driven, and "
                 "prompts are user-controlled, requiring explicit invocation. A prompt is a reusable template the user picks; Claude "
                 "Code lists server prompts as commands. A would let the model decide when to start it; C is data, not an instruction "
                 "template; D is a request a server makes in the middle of a task for input, not a reusable workflow."),
        scenarios=(4,), points=("2.4:K4",), basis="docs",
        evidence=(Evidence("mcp_concepts", "Prompts are user-controlled, requiring explicit invocation."),
                  Evidence("mcp_concepts", "Tools are model-controlled, meaning AI models can discover and invoke them automatically."),
                  Evidence("cc_mcp", "MCP servers can expose prompts that become available as commands in Claude Code."),
                  Evidence("cc_mcp", "Claude Code lists each MCP prompt as `/servername:promptname (MCP)`.")),
        community=("paullarionov §4.1 and dnacenta §2.4 both list prompts as a primitive; the guide's TS 2.4 bullets name resources "
                   "but not prompts, so this item is marked as docs-based."),
    ),
    MCQ(
        id="MCP-06",
        q=("Your MCP server's `search_issues` tool supports field filters and returns ranked results with owners, yet traces show the "
           "agent reaching for the built-in Grep on exported JSON in 70% of runs. The tool's description is 3,100 characters: 2,400 "
           "characters of changelog and licence notes come first, and what the tool can do and return is at the end. Which change "
           "is most likely to fix the behaviour?"),
        opts=("Add “ALWAYS use this tool instead of Grep” as the final line of the existing description.",
              "Deny the built-in Grep tool in the permission settings so that it is unavailable in every session.",
              "Rewrite the description to open with what the tool searches and returns, within 2,048 characters.",
              "Raise `MAX_MCP_OUTPUT_TOKENS` so that larger results from the tool are not cut off before the agent reads them."),
        ans=2,
        explain=("The guide asks for descriptions that explain capabilities and outputs so the agent does not prefer built-in tools "
                 "(TS 2.4, skill 3). Claude Code truncates each tool description at 2,048 characters, and here the capabilities sit "
                 "after the cut, so the agent never sees them. Put the critical details first. A adds emphasis to the part that is "
                 "truncated; B removes a built-in tool that other work needs; D concerns the size of results, not the description."),
        scenarios=(4,), points=("2.4:S3",), basis="docs",
        evidence=(Evidence("cc_mcp", "Claude Code truncates each tool description and each server's instructions at 2,048 characters by default. Keep them concise, and put critical details near the start."),),
        community=("dnacenta §2.4 mentions the 2,048-character truncation. paullarionov §4.2 says descriptions determine how the model "
                   "uses a tool, and does not mention the limit."),
    ),
    MCQ(
        id="MCP-07",
        q=("Your team needs two integrations: (1) Jira ticket search, and (2) a release-approval check that reads three proprietary "
           "systems and applies your company's go/no-go rules. A custom Jira server would cost about three engineer-weeks plus "
           "upkeep. Which plan best matches how MCP servers should be chosen?"),
        opts=("Adopt an existing, reviewed Jira server for (1) once you trust it, and build a custom server only for (2).",
              "Build custom servers for both so that every tool follows the naming conventions your own team already uses.",
              "Use the existing Jira server for both, describing the approval rules inside its tool descriptions for the model.",
              "Skip MCP: store the Jira and system credentials in CLAUDE.md and have the agent call the REST APIs from Bash."),
        ans=0,
        explain=("For a standard integration such as Jira, choose an existing community or vendor server; reserve custom servers for "
                 "team-specific workflows like the approval check (TS 2.4, skill 4). The docs add that you should verify you trust "
                 "any server before connecting it, because servers that fetch external content can expose you to prompt injection. "
                 "B pays three weeks for something that already exists; C cannot work because a Jira server cannot read your "
                 "proprietary systems, and rules written in a description are not logic; D puts secrets into a file that is loaded in "
                 "every session."),
        scenarios=(4,), points=("2.4:S4",),
        evidence=(Evidence("cc_mcp", "Verify you trust each server before connecting it. Servers that fetch external content can expose you to prompt injection risk."),
                  Evidence("cc_mcp", "Browse reviewed connectors in the Anthropic Directory.")),
        community=("paullarionov §4.3 gives the same rule (prefer existing community servers for Jira, GitHub, Slack; build your own "
                   "for team-specific workflows). The trust check comes from the docs."),
    ),
    MCQ(
        id="MCP-08",
        q=("Your support agent's `schedule_callback` MCP tool requires an ISO date. When a customer says “03/09/26” the server raises "
           "an exception and the client receives the JSON-RPC error `-32602 Invalid params`. In 88% of such cases the agent simply "
           "apologises to the customer instead of correcting the date and retrying. Which server change best lets the agent recover?"),
        opts=("Keep the JSON-RPC error but make its message longer and add the required date format to it.",
              "Return success with the text “Callback not scheduled”, so the agent can read the outcome as normal output.",
              "Retry the call three times inside the server before reporting a failure to the agent.",
              "Return a normal tool result with `isError: true` whose text states the required format and today's date."),
        ans=3,
        explain=("The MCP specification separates protocol errors (a malformed request or an unknown tool, which models are less "
                 "likely to fix) from tool execution errors (API failures, input validation errors such as a date in the wrong format, "
                 "and business-logic errors). Execution errors go back in the tool result with `isError: true`, and clients should "
                 "pass them to the model so it can self-correct. A leaves the failure in the channel models are less likely to act on; "
                 "B hides the failure behind a success (guide TS 2.2: a failure must be reported as one); C retries a request that can "
                 "never succeed, because bad input is not transient."),
        scenarios=(1,), points=("2.2:K1", "2.2:K2", "2.2:S1"),
        evidence=(Evidence("mcp_tools_spec", "Tool Execution Errors contain actionable feedback that language models can use to self-correct and retry with adjusted parameters:"),
                  Evidence("mcp_tools_spec", "Input validation errors (e.g., date in wrong format, value out of range)"),
                  Evidence("mcp_tools_spec", "Clients SHOULD provide tool execution errors to language models to enable self-correction."),
                  Evidence("mcp_tools_spec", "Protocol Errors indicate issues with the request structure itself that models are less likely to be able to fix:")),
        community=("paullarionov §4.4 and OlivierAlter Q32 and Q34 test the `isError` pattern and generic errors. The protocol-error versus "
                   "execution-error split in this item comes from the specification."),
    ),
    MCQ(
        id="MCP-09",
        q=("Your CI job runs `claude -p` on every pull request, including pull requests from outside contributors. The repository's "
           "`.mcp.json` defines two internal servers, and a security reviewer points out that a pull request can edit that file. In "
           "interactive sessions engineers get an approval prompt for project servers. What happens in the CI run, and which control "
           "fits?"),
        opts=("The run skips every project-scoped server because no one is present to approve it, so no change to the job is needed.",
              "The run loads project servers with no prompt; use `--strict-mcp-config` and pass only wanted servers via `--mcp-config`.",
              "The run auto-approves only servers whose names appear in CLAUDE.md, so adding the server names there to be safe is enough.",
              "The run fails unless `--dangerously-skip-permissions` is set, so the job is already protected against that kind of edit."),
        ans=1,
        explain=("In `claude -p` runs (as in Agent SDK and cloud sessions) Claude Code cannot show the approval prompt, so it loads "
                 "project-scoped servers without asking. A pull request that edits `.mcp.json` can therefore add a server to the CI "
                 "run. `--strict-mcp-config` makes Claude Code use only the servers passed with `--mcp-config`. A assumes the "
                 "opposite behaviour; C and D describe mechanisms that do not exist."),
        scenarios=(5,), points=("2.4:K1", "2.4:S1"), basis="docs",
        evidence=(Evidence("cc_mcp", "In `claude -p` runs, [Agent SDK](/docs/en/headless) sessions, and [cloud sessions](/docs/en/claude-code-on-the-web), Claude Code can't show that prompt: it loads project-scoped servers without asking."),
                  Evidence("cc_mcp", "Start the session with [`--strict-mcp-config`](/docs/en/cli-reference#cli-flags). Claude Code then uses only the MCP servers you pass with `--mcp-config`.")),
        community=("dnacenta §2.4 states the same behaviour and names `disabledMcpjsonServers` and `--setting-sources` as ways to keep a "
                   "server out of headless runs; the docs add `--strict-mcp-config`."),
    ),
    MCQ(
        id="MCP-10",
        q=("A team's `.mcp.json` defines an `analytics` server at `https://analytics.internal/mcp`. A maintainer changes the URL in "
           "`.mcp.json`, merges, and everyone pulls. One engineer's sessions still reach the old URL with the old headers. Last month "
           "she ran `claude mcp add analytics ...` with no `--scope` to try a prototype. What is the root cause?"),
        opts=("Claude Code merges the two entries field by field and keeps the older URL because it was written first.",
              "User scope outranks project scope, so the entry in her `~/.claude.json` shadows the shared file.",
              "Her local-scope entry of the same name outranks the project entry, and is used whole, unmerged.",
              "She must run `claude mcp reset-project-choices` after any `.mcp.json` edit, or the old URL stays cached."),
        ans=2,
        explain=("When the same server name is defined in more than one place, Claude Code uses the definition from the "
                 "highest-precedence source, in the order local, project, user. Her `claude mcp add` without a scope created a local "
                 "entry, so it beats the project's `.mcp.json`, and the whole entry is used: fields are not merged. A is wrong because "
                 "of that no-merge rule; B reverses the order, since user scope is the lowest of the three and her entry is local, not "
                 "user; D is wrong because `reset-project-choices` resets approval choices, not definitions."),
        scenarios=(4,), points=("2.4:K1", "2.4:S1"), basis="docs",
        evidence=(Evidence("cc_mcp", "When the same server is defined in more than one place, Claude Code connects to it once, using the definition from the highest-precedence source. The entire server entry from that source is used; fields are not merged across scopes."),
                  Evidence("cc_mcp", "Claude Code matches duplicates across the three scopes by name."),
                  Evidence("cc_mcp", "To reset those approval choices, run `claude mcp reset-project-choices`.")),
        community=("paullarionov §4.3 does not describe a local scope or any precedence. dnacenta §2.4 lists the scopes but not the "
                   "precedence order."),
        live=("Claude Code 2.1.168, isolated config directory: with a project `.mcp.json` entry named `demo`, adding a server named `demo` "
              "at local scope made `claude mcp get demo` report “Scope: Local config” and the local entry's own command; the "
              "project entry's `env` was not carried over."),
    ),
)

# ══ CLAUDE SKILLS ════════════════════════════════════════════════════════════════════════════════════════════════
SKILLS = (
    MCQ(
        id="SKL-01",
        q=("Your team wants a `/release-notes` command for all 15 engineers. It needs a Markdown template that the command fills "
           "in. One engineer built it in `~/.claude/commands/release-notes.md` with the template beside it, and teammates report that "
           "the command does not exist for them. Which fix best serves the whole team?"),
        opts=("Copy the file into every engineer's `~/.claude/commands/` with a setup script that each person runs once per laptop.",
              "Describe the release-notes steps in the repository's CLAUDE.md and ask engineers to paste the template themselves.",
              "Create `.claude/skills/release-notes/SKILL.md` in the repository with the template beside it, and commit it.",
              "Move the file to `.claude/settings.local.json` so that the command becomes part of the project settings."),
        ans=2,
        explain=("Project-scoped skills and commands live in the repository and reach everyone through version control, while files "
                 "under `~/.claude/` exist only on one machine. Both `.claude/commands/` and `.claude/skills/` create a `/name`; the "
                 "docs prefer skills for new work because a skill directory can carry supporting files such as the template. A works "
                 "but drifts and needs manual repetition; B puts a multi-step procedure in memory that loads every session; D is not a "
                 "command location, and local settings are not committed."),
        scenarios=(2,), points=("3.2:K1", "3.2:S1"),
        evidence=(Evidence("cc_skills", "Sessions in this repository. Commit it so your team gets it too"),
                  Evidence("cc_skills", "All your projects on this machine, but not [Cowork or cloud sessions](#skills-in-cowork-and-cloud-sessions)"),
                  Evidence("cc_skills", "Prefer a skill for new work, since skills also support [supporting files](#add-supporting-files).")),
        community=("paullarionov §5.4 and dnacenta §3.2 both say commands and skills are merged and that project versions are shared "
                   "through version control; the guide names `.claude/commands/`."),
    ),
    MCQ(
        id="SKL-02",
        q=("A `/map-dependencies` skill reads about 200 files and prints a long report. After each use the main session's context is "
           "full of file contents and engineers lose track of their original task, although the report is all they need. Which "
           "frontmatter setting best fixes this?"),
        opts=("`context: fork`, so the skill runs in an isolated subagent and returns only its result.",
              "`allowed-tools: []`, so the skill is unable to read any files into the main session at all.",
              "`argument-hint: [directory]`, so the skill receives only the directory name and therefore reads less.",
              "`disable-model-invocation: true`, so that Claude can never load the skill by itself during a session."),
        ans=0,
        explain=("`context: fork` runs the skill in a new, isolated subagent context, and the subagent returns its summary to the main "
                 "conversation, so the verbose exploration never lands in the main context (TS 3.2, knowledge 3 and skill 2). B fails "
                 "because `allowed-tools` pre-approves tools rather than removing them, so an empty list stops nothing; C is only an "
                 "autocomplete hint; D controls who may start the skill, not where it runs."),
        scenarios=(4,), points=("3.2:K3", "3.2:S2"),
        evidence=(Evidence("cc_skills", "Add `context: fork` to your frontmatter when you want a skill to run in isolation."),
                  Evidence("cc_skills", "The subagent summarizes its results and returns them to your main conversation when it finishes")),
        community=("OlivierAlter Q43 tests the same idea with different wording; paullarionov §5.5 and dnacenta §3.2 describe "
                   "`context: fork` the same way."),
    ),
    MCQ(
        id="SKL-03",
        q=("A `/summarize-logs` skill should never run shell commands. An engineer adds `allowed-tools: Read Grep Glob` to its "
           "frontmatter, expecting Bash to become unavailable during the skill. In testing, Claude still runs `rm -rf build/` through "
           "Bash during the skill, after asking permission. What happened, and what actually removes the tool?"),
        opts=("The skill file was not loaded, because `allowed-tools` must be declared in `settings.json` and not in frontmatter.",
              "`allowed-tools` needs the exact entry `Bash(none)` before it blocks anything, so the plain list was ignored.",
              "Claude ignored the field, since a skill always runs with the main session's full tool set whatever its frontmatter says.",
              "`allowed-tools` only pre-approves, so Bash stayed callable; use `disallowed-tools` or a deny rule."),
        ans=3,
        explain=("`allowed-tools` grants permission for the listed tools for the turn that invokes the skill, so Claude can use them "
                 "without asking. It does not restrict which tools are available: every tool remains callable and the permission "
                 "settings still govern the unlisted ones, which is why Bash only asked first. To take a tool away while the skill is "
                 "active, use `disallowed-tools` in the frontmatter, or a deny rule in permission settings. A is wrong because the "
                 "field is frontmatter; B invents a syntax; C is wrong because the listed tools were pre-approved, so the field was "
                 "honoured. Note: the exam guide words this field as restricting tool access; the docs are more precise, and this "
                 "item tests the documented behaviour."),
        scenarios=(2,), points=("3.2:S3",), basis="docs",
        evidence=(Evidence("cc_skills", "It does not restrict which tools are available: every tool remains callable, and your [permission settings](/docs/en/permissions) still govern tools that are not listed."),
                  Evidence("cc_skills", "Tools removed from Claude's available pool while this skill is active."),
                  Evidence("cc_skills", "Tools Claude can use without asking permission during the turn that invokes this skill.")),
        community=("paullarionov §5.5 says `allowed-tools` “Restricts which tools are available”, which the docs contradict. dnacenta "
                   "§3.2 (“Tools pre-approved while this skill is active”) agrees with the docs."),
    ),
    MCQ(
        id="SKL-04",
        q=("A skill `fix-issue` has `argument-hint: [issue-number]`. Its body says “Fix the GitHub issue following our standards” and "
           "contains no `$ARGUMENTS` anywhere. An engineer types `/fix-issue 482`. What does Claude receive?"),
        opts=("The skill body only; `482` is discarded because no placeholder in the body uses it at all.",
              "The skill body with `ARGUMENTS: 482` appended, so Claude still sees what was typed.",
              "A prompt asking her for the issue number, because the hint makes the argument required for the skill.",
              "An error saying that the skill needs a `$ARGUMENTS` placeholder before it can take input."),
        ans=1,
        explain=("When you invoke a skill with arguments but no placeholder in its content receives one, Claude Code appends "
                 "`ARGUMENTS: <your input>` to the end of the skill content. `argument-hint` only shows a hint during autocomplete; it "
                 "does not prompt for, require or validate an argument (the guide describes it as prompting for parameters; the docs "
                 "describe the hint precisely). A is wrong because the input is appended, C credits the hint with behaviour it does not "
                 "have, and D describes an error that does not exist."),
        scenarios=(4,), points=("3.2:S4",),
        evidence=(Evidence("cc_skills", "If you invoke a skill with arguments but no placeholder in the skill's content receives one, Claude Code appends `ARGUMENTS: <your input>` to the end of the skill content so Claude still sees what you typed."),
                  Evidence("cc_skills", "Hint shown during autocomplete to indicate expected arguments.")),
        community=("paullarionov §5.5 says the hint “asks for an argument when invoked without parameters”, which the docs do not "
                   "support. dnacenta §3.2 (“Hint shown in autocomplete”) agrees with the docs."),
    ),
    MCQ(
        id="SKL-05",
        q=("Your CLAUDE.md has grown to 420 lines. Besides “run `make lint` before every commit” and your naming conventions, it holds "
           "12 multi-step procedures (release, database migration, incident write-up) that each matter in about one session in "
           "twenty. Sessions feel slower and Claude follows the rules less reliably. What is the best restructuring?"),
        opts=("Split the file into 12 smaller CLAUDE.md files and import them all with `@`, so that everything stays in one place.",
              "Move the universal rules into skills too, so that nothing at all is loaded until someone invokes it.",
              "Keep the universal standards in CLAUDE.md and move each procedure into its own skill, loaded when invoked.",
              "Rely on a larger context window so that the extra procedures stop crowding out the rules that matter."),
        ans=2,
        explain=("CLAUDE.md is for facts Claude should hold in every session; a multi-step procedure that matters occasionally belongs "
                 "in a skill, whose full content loads only when it is invoked (TS 3.2, skill 5). A fails because imported files are "
                 "expanded and loaded into context at launch, so nothing is saved; B moves always-needed standards to on-demand "
                 "loading, so they would be missing when needed; D treats longer files as a capacity problem, but the docs say longer "
                 "files consume more context and reduce adherence."),
        scenarios=(2,), points=("3.2:S5",),
        evidence=(Evidence("cc_memory", "If an entry is a multi-step procedure or only matters for one part of the codebase, move it to a [skill](/docs/en/skills)"),
                  Evidence("cc_memory", "Longer files consume more context and reduce adherence."),
                  Evidence("cc_memory", "Imported files are expanded and loaded into context at launch alongside the CLAUDE.md that references them."),
                  Evidence("cc_skills", "In a regular session, skill descriptions are loaded into context so Claude knows what's available, but full skill content only loads when invoked.")),
        community=("paullarionov §5.5 states the same split (skill for on-demand tasks, CLAUDE.md for always-loaded standards)."),
    ),
    MCQ(
        id="SKL-06",
        q=("Your team's project skill `.claude/skills/review/SKILL.md` is committed and used by 15 engineers. One engineer wants a "
           "stricter variant that also checks accessibility. Which approach best avoids affecting her teammates?"),
        opts=("Edit the committed `review` skill in place and ask the team to ignore it until her changes are finished.",
              "Create `~/.claude/skills/review-strict/SKILL.md` under a different name and use it only in her own sessions.",
              "Copy the skill to `.claude/skills/review-strict/` and commit it, so the variant is available if others want it.",
              "Add `disable-model-invocation: true` to the committed `review` skill so that only she decides when it runs."),
        ans=1,
        explain=("A personal skill under `~/.claude/skills/` loads for you in all your projects and is not shared, whereas anything in the "
                 "project's `.claude/skills/` is committed and reaches the team (TS 3.2, knowledge 4). Giving the variant its own name "
                 "means it cannot be confused with, or replace, the team's `/review`. A, C and D all change what the other 14 "
                 "engineers get: A edits the shared file, C adds a shared skill, and D changes how the shared skill behaves for "
                 "everyone."),
        scenarios=(2,), points=("3.2:K4",),
        evidence=(Evidence("cc_skills", "Sessions in this repository. Commit it so your team gets it too"),
                  Evidence("cc_skills", "All your projects on this machine, but not [Cowork or cloud sessions](#skills-in-cowork-and-cloud-sessions)")),
        community=("paullarionov §5.5 advises personal variants under different names so teammates are not affected, matching the guide."),
    ),
    MCQ(
        id="SKL-07",
        q=("A `/deploy` skill pushes to production. On Tuesday, after a green test run, Claude invoked the skill by itself because "
           "the conversation sounded like “ready to ship”. The team wants engineers to run `/deploy staging` deliberately, and nobody "
           "else to trigger it. Which setting fits?"),
        opts=("`user-invocable: false`, so that only a deliberate action can ever run the skill.",
              "`context: fork`, so that the deployment runs in a separate subagent context.",
              "`allowed-tools: Bash(git push *)`, so that the deployment is limited to git pushes.",
              "`disable-model-invocation: true`, so that Claude cannot run it on its own."),
        ans=3,
        explain=("`disable-model-invocation: true` stops Claude from invoking the skill automatically while you can still type "
                 "`/deploy`; the docs recommend it for workflows with side effects or timing you want to control. A is the opposite: "
                 "`user-invocable: false` leaves only Claude able to invoke it. B changes where the skill runs, not who starts it. C "
                 "pre-approves git push commands, which would let a model-triggered run push without a prompt."),
        scenarios=(2,), points=("3.2:K2",), basis="docs",
        evidence=(Evidence("cc_skills", "`disable-model-invocation: true`: Claude can't invoke the skill on its own. Use this for workflows with side effects or that you want to control timing, like `/commit`, `/deploy`, or `/send-slack-message`."),
                  Evidence("cc_skills", "`user-invocable: false`: Only Claude can invoke the skill.")),
        community=("dnacenta §3.2 lists both fields in its frontmatter table; the guide's TS 3.2 bullets do not name them."),
    ),
    MCQ(
        id="SKL-08",
        q=("An engineer notices a wrong command in a skill's `SKILL.md` and fixes it while a session is open. Claude Code picks up the "
           "edited file, yet in that conversation Claude keeps using the old command from a skill she invoked ten minutes earlier. "
           "What explains this, and what is the quickest fix?"),
        opts=("The earlier text stays in the conversation and the file is not re-read; invoke the skill again.",
              "Skill edits take effect only after Claude Code restarts, so she must quit and relaunch before the fix is used.",
              "Edited skills are reloaded only when `/compact` rewrites the conversation, so she should compact the session first.",
              "A running session pins every skill file at launch, so the fix applies only to sessions that start later."),
        ans=0,
        explain=("When a skill is invoked, its rendered content enters the conversation as one message and stays there; Claude Code "
                 "does not re-read the file on later turns. Edits to skill files are detected within the current session without a "
                 "restart, so invoking the skill again adds the new, different content. B and D contradict the live change detection "
                 "the docs describe; C invents a link between `/compact` and reloading."),
        scenarios=(2,), points=("3.2:K2",), basis="docs",
        evidence=(Evidence("cc_skills", "When you or Claude invoke a skill, the rendered `SKILL.md` content enters the conversation as a single message and stays there across later turns."),
                  Evidence("cc_skills", "Claude Code does not re-read the skill file on later turns"),
                  Evidence("cc_skills", "When the rendered content differs, because the arguments changed or a [dynamic context](#inject-dynamic-context) command produced new output, Claude Code appends the full content again."),
                  Evidence("cc_skills", "Claude Code picks up the change within the current session, without a restart.")),
        community=("dnacenta §3.2 (“Skill Lifecycle and Compaction”) states that the body stays in the conversation and the file is not "
                   "re-read."),
    ),
    MCQ(
        id="SKL-09",
        q=("An engineer writes `.claude/skills/api-style/SKILL.md` with `context: fork` and a body of 15 bullet rules about API naming "
           "and error formats, with no task in it. Invoking `/api-style` returns almost nothing useful. What is the most likely "
           "cause?"),
        opts=("Forked skills cannot read CLAUDE.md, so the conventions in the body cannot be resolved by the subagent.",
              "`context: fork` works only when `allowed-tools` is also set, otherwise the subagent has no tools.",
              "The subagent gets the body as its prompt; rules with no task give it nothing to do.",
              "Forked skills run only when `disable-model-invocation: true` is also set in the same frontmatter."),
        ans=2,
        explain=("A forked skill starts a new subagent and gives it the skill content as its prompt; the subagent does not see the "
                 "conversation, so the instructions must stand alone, and guidelines with no task produce no meaningful output. "
                 "Reference content such as conventions should run inline: drop `context: fork`. A is wrong because a forked skill "
                 "loads CLAUDE.md per the agent's startup context; B and D describe requirements that the documented frontmatter "
                 "does not have (all fields are optional)."),
        scenarios=(2,), points=("3.2:K3",),
        evidence=(Evidence("cc_skills", "`context: fork` only makes sense for skills with explicit instructions. If your skill contains guidelines like \"use these API conventions\" without a task, the subagent receives the guidelines but no actionable prompt, and returns without meaningful output."),
                  Evidence("cc_skills", "The subagent doesn't see your conversation history, so the skill's instructions have to stand on their own."),
                  Evidence("cc_skills", "All fields are optional.")),
        community=("paullarionov §5.5 and dnacenta §3.2 describe `context: fork` as isolation; neither mentions the reference-content "
                   "warning that this item tests."),
    ),
    MCQ(
        id="SKL-10",
        q=("Your project has a committed skill `/lint` at `.claude/skills/lint/SKILL.md`. One engineer also has a personal skill "
           "`~/.claude/skills/lint/SKILL.md` that runs a different linter. She types `/lint`. A teammate who has no personal `lint` "
           "types the same command. What happens?"),
        opts=("Both skills load and Claude Code asks each engineer which of them to run on every call.",
              "She runs her personal skill, and the teammate runs the project skill.",
              "Both engineers run the project skill, because a shared project skill always takes priority.",
              "Claude Code reports a name conflict and runs neither skill for her until one is renamed."),
        ans=1,
        explain=("When the same name exists at more than one level, enterprise outranks personal and personal outranks project, so her "
                 "`/lint` runs the personal skill while her teammate, who has no personal copy, gets the project skill. That is why a "
                 "personal variant with the same name silently replaces the team's version for you, and why the guide recommends "
                 "different names for personal variants. A, C and D describe prompts, priorities and errors that the precedence rules "
                 "do not contain."),
        scenarios=(2,), points=("3.2:K1", "3.2:K4"), basis="docs",
        evidence=(Evidence("cc_skills", "Enterprise over personal, and personal over project. With `deploy` in both `~/.claude/skills/` and the project's `.claude/skills/`, `/deploy` runs the personal one"),),
        community=("dnacenta §3.2 states the priority as “Enterprise > Personal > Project > Plugin”, matching the docs."),
    ),
)

SETS = {"mcp": MCP, "skills": SKILLS}
TITLES = {"mcp": "MCP", "skills": "Claude Skills"}
