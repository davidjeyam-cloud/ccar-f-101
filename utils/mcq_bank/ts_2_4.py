"""Exam bank · TS 2.4. Original questions; see docs/MCQ_BANK_PLAN.md."""
from utils.mcq_sets import MCQ, Evidence

TS = "2.4"
BULLETS = {
    "K1": "Project scope (.mcp.json) for shared team servers versus user scope (~/.claude.json) for personal or experimental ones",
    "K2": "Environment variable expansion in .mcp.json keeps credentials out of version control",
    "K3": "Tools from every configured MCP server are discovered at connection time and available to the agent together",
    "K4": "MCP resources expose content catalogues (issue summaries, documentation trees, schemas) to cut exploratory tool calls",
    "S1": "Configuring shared servers in a project-scoped .mcp.json with variable expansion for auth tokens",
    "S2": "Configuring personal or experimental servers in user-scoped ~/.claude.json",
    "S3": "Writing detailed MCP tool descriptions so the agent does not prefer built-in tools such as Grep",
    "S4": "Choosing an existing community server for standard integrations and a custom server only for team-specific workflows",
    "S5": "Exposing content catalogues as MCP resources so agents can see what data exists without exploratory calls",
}

QUESTIONS = (
    # ---- K1: project scope versus user scope ----
    MCQ(
        id="Q2.4-01",
        q=("Your 14-engineer platform team onboards people with a wiki page of six `claude mcp add --scope user` commands for the "
           "shared Sentry, GitHub and deploy-status servers. After the Sentry URL changed, 5 of the 14 laptops still point at the old "
           "one and fail, and two engineers added a different seventh server by hand. The team lead proposes a nightly script, pushed "
           "to every laptop, that re-runs the six commands. How should you evaluate this?"),
        opts=("Adopt it: the script keeps every user-scoped entry identical, so the six servers stay consistent on all 14 laptops.",
              "Reject it: define the six servers once in a committed `.mcp.json`, and keep user scope for personal servers.",
              "Adopt it, and add a CI job that fails whenever a laptop's server list differs from the list on the wiki page.",
              "Reject it: keep the wiki, put the new Sentry URL at the top, and ask each engineer to re-run that one command."),
        ans=1,
        explain=("Shared servers belong in the one place the team already shares and reviews: a committed `.mcp.json` arrives with "
                 "every pull, so there is nothing to push to laptops. A keeps copying per-machine configuration and still depends on "
                 "the script reaching each laptop. C only detects drift afterwards, and a CI job cannot read laptops anyway. D leaves "
                 "the update to people remembering, which is how the 5 stale laptops happened."),
        scenarios=(4,), points=("2.4:K1",),
        evidence=(Evidence("code:mcp", "Check `.mcp.json` into version control so everyone on your team gets the same MCP tools and services."),),
        qtype="evaluate", level="medium", principle="fit_for_purpose",
        situation="wiki commands for shared servers drift across 14 laptops",
        trap="script that pushes user-scope config to laptops",
    ),
    MCQ(
        id="Q2.4-02",
        q=("A research team of nine shares one repository. Everyone needs the citations-index server and the news-archive server. "
           "One researcher also runs a bookmarks-search server over her own exported browser data, in every project she opens, and "
           "nobody else wants it. Which placement fits?"),
        opts=("Citations and archive in a committed `.mcp.json`; bookmarks in her user-scoped `~/.claude.json`.",
              "All three in the committed `.mcp.json`, with a README line saying that the bookmarks entry is hers alone.",
              "All three at user scope, with each of the nine researchers adding the two shared servers on their own laptop.",
              "Citations and archive in each researcher's own `.mcp.json` kept out of git; bookmarks at user scope."),
        ans=0,
        explain=("Servers the whole team needs go in the committed project file, and a server that belongs to one person across all "
                 "her projects goes in her user scope. B puts a personal server in front of eight people who will then be asked about "
                 "it. C and D both leave the shared servers as nine separate copies that drift apart."),
        scenarios=(3,), points=("2.4:K1",),
        evidence=(Evidence("code:mcp", "Check `.mcp.json` into version control so everyone on your team gets the same MCP tools and services."),
                  Evidence("code:mcp", "User-scoped servers are stored in `~/.claude.json` and provide cross-project accessibility, making them available across all projects on your machine while remaining private to your user account.")),
        qtype="choose", level="easy", principle="fit_for_purpose",
        situation="two shared research servers plus one researcher's private bookmarks server",
        trap="put the personal server in the shared file with a README note",
    ),
    MCQ(
        id="Q2.4-03",
        q=("A freelance engineer works in two clients' repositories on one laptop. Client A's internal wiki server must be available "
           "to every engineer on Client A's team through that repository. It must not load in Client B's repository, where its "
           "tools could pull Client A's pages into Client B's work. Where should the server be configured?"),
        opts=("In her user-scoped `~/.claude.json`, because the server is hers to use on this laptop across projects.",
              "In both repositories' `.mcp.json` files, with a note in Client B's repository saying that it is switched off.",
              "In Client A's CLAUDE.md, which tells Claude Code which servers to start for that project.",
              "In Client A's committed `.mcp.json`, so that it loads in that project and travels with it."),
        ans=3,
        explain=("Project scope is tied to the repository, so the server loads there for the whole team and nowhere else. A loads it "
                 "in every project on her machine, including Client B's. B ships Client A's server into Client B's repository. C "
                 "describes a file that holds instructions, not server definitions."),
        scenarios=(4,), points=("2.4:K1",),
        evidence=(Evidence("code:mcp", "User-scoped servers are stored in `~/.claude.json` and provide cross-project accessibility, making them available across all projects on your machine while remaining private to your user account."),),
        qtype="choose", level="medium", principle="least_privilege",
        situation="one client's wiki server must not load in another client's repository",
        trap="user scope loads in every project on the machine",
    ),
    # ---- K2: environment variable expansion ----
    MCQ(
        id="Q2.4-04",
        q=("Your research team's committed `.mcp.json` points the archive server at the production archive. Engineers who test "
           "against the staging archive keep editing the file and have committed the staging URL 7 times this quarter. Everyone else "
           "must still get a working server with no setup, and testers should switch targets by setting one shell variable. Which "
           "`url` value does this?"),
        opts=("`\"https://archive.example.com/mcp\"`, with testers told to run `git update-index --assume-unchanged .mcp.json` first.",
              "`\"${ARCHIVE_BASE}/mcp\"`, with every engineer told to export `ARCHIVE_BASE` once.",
              "`\"${ARCHIVE_BASE:-https://archive.example.com}/mcp\"`",
              "`\"${ARCHIVE_BASE:=https://archive.example.com}/mcp\"`, which assigns the default for later use."),
        ans=2,
        explain=("`${VAR:-default}` uses the variable when it is set and the default when it is not, so most people need nothing and "
                 "testers set one variable. B has no default, so for anyone who has not exported the variable the unexpanded text is "
                 "kept and the URL is broken. A still has testers editing a tracked file. D uses a shell form that Claude Code does not "
                 "list; it supports `${VAR}` and `${VAR:-default}`."),
        scenarios=(3,), points=("2.4:K2",),
        evidence=(Evidence("code:mcp", "`${VAR:-default}`: expands to the value of `VAR` if `VAR` is set, or to `default` if it is unset"),),
        basis="docs",
        qtype="configure", level="medium", principle="explicit",
        situation="testers keep committing the staging archive URL",
        trap="variable reference without a default",
    ),
    MCQ(
        id="Q2.4-05",
        q=("A support team's committed `.mcp.json` launches a local ticket-export server as a stdio command. The server takes its "
           "database connection string, which contains a password, only as a `--dsn` argument and ignores its environment. The file "
           "must hold no password, no wrapper script may be added, and each engineer keeps their own credentials in their shell. How "
           "should the entry be written?"),
        opts=("Put `\"--dsn\", \"${EXPORT_DSN}\"` in the `args` list, and have each engineer export `EXPORT_DSN`.",
              "Add `\"env\": {\"EXPORT_DSN\": \"${EXPORT_DSN}\"}` and leave `--dsn` out, because variables expand only in `env`.",
              "Write the shared test-database connection string into `args`, and let engineers override it locally when needed.",
              "Put `\"--dsn\", \"EXPORT_DSN\"` in `args`, because Claude Code swaps a bare variable name for its value."),
        ans=0,
        explain=("Claude Code expands `${VAR}` in `command`, `args`, `env`, `url` and `headers`, so the argument can reference the "
                 "variable and the file holds no secret. B assumes expansion is limited to `env`, and the server never reads its "
                 "environment. C commits a password. D relies on a substitution that Claude Code does not perform, so the server "
                 "would receive the literal name."),
        scenarios=(1,), points=("2.4:K2",),
        evidence=(Evidence("code:mcp", "You can reference an environment variable in a server's `command`, `args`, `env`, `url`, or `headers` value, in either of two forms:"),),
        basis="docs",
        qtype="configure", level="medium", principle="explicit",
        situation="stdio export server takes its connection string only as a command-line argument",
        trap="assume variables expand only in the env block",
    ),
    MCQ(
        id="Q2.4-06",
        q=("A new `.mcp.json` entry sends `\"Authorization\": \"Bearer ${DEPLOY_API_TOKEN}\"`. To make onboarding \"work out of the "
           "box\", an engineer proposes committing a `.env` file that holds the team's real token, which a setup script loads into "
           "each shell. The repository is private. How should you evaluate this?"),
        opts=("Accept: a private repository gives the token the same exposure as the rest of the source code.",
              "Reject: commit a `.env.example` with a placeholder, and have each engineer use their own token.",
              "Accept, and add `.env` to `.gitignore` in a later commit so that the file stops being tracked.",
              "Reject: store the token base64-encoded in `.mcp.json` instead, so it cannot be read at a glance."),
        ans=1,
        explain=("The reason to use `${VAR}` is that values stay out of the committed file, and a committed `.env` puts the same "
                 "secret straight back into git. A treats a private repository as a safe place for a shared secret. C leaves the token "
                 "in history after the first commit. D is encoding, not protection, and it moves the secret into the config file."),
        scenarios=(4,), points=("2.4:K2",),
        evidence=(Evidence("code:mcp", "allowing teams to share configurations while maintaining flexibility for machine-specific paths and sensitive values like API keys."),),
        qtype="evaluate", level="easy", principle="least_privilege",
        situation="proposal to commit a .env with the real token beside a ${VAR} config",
        trap="a private repository counts as a safe place for a secret",
    ),
    # ---- K3: tools from all servers are available together ----
    MCQ(
        id="Q2.4-07",
        q=("Your support agent in Claude Code uses four MCP servers (billing, shipping, returns and CRM) with about 35 tools in all. A "
           "staff engineer proposes a gateway server that wraps the four, \"so that the agent can combine data from several systems "
           "in one request\". The four servers belong to other teams and rarely change. How should you evaluate the proposal?"),
        opts=("Build it: tools from separate servers can be used together only if one server exposes them.",
              "Build it for billing and shipping only, the pair that the agent needs together most often.",
              "Skip it: the agent already has the tools of all four servers at once.",
              "Skip it, and run one subagent per server so that each system's data is gathered separately."),
        ans=2,
        explain=("Claude Code connects to every configured server, and the agent can discover and call tools from all four servers, so a request can "
                 "use billing and then shipping with nothing in between. A states a limit that does not exist. B builds the same "
                 "unneeded layer for a smaller set. D splits work that one agent can already do and adds a merging step."),
        scenarios=(1,), points=("2.4:K3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 2.4 Knowledge 3 says tools from all configured servers are available simultaneously; the judgment about a needless gateway is not stated on a docs page.",
        qtype="evaluate", level="medium", principle="proportionate",
        situation="gateway server proposed to wrap four existing MCP servers",
        trap="assume tools from separate servers cannot be used together",
    ),
    MCQ(
        id="Q2.4-08",
        q=("A developer asks the agent when a service was last deployed, and it answers from `git log`, which only shows merges. "
           "Teammates' sessions answer the same question from the `deploys` server's tools. In this developer's session, none of the "
           "`deploys` tools appear in the tool list, while the other three servers' tools do. What is the most likely cause?"),
        opts=("The `deploys` tool descriptions are too short, so the agent chooses its built-in tools instead.",
              "Claude Code offers tools from only three servers at a time, and `deploys` was connected last.",
              "The agent needs a CLAUDE.md line that names the `deploys` tools before it will consider them.",
              "The server never connected, so its tools were never discovered or offered."),
        ans=3,
        explain=("Tools are discovered when a server connects, and this one apparently never connected, so "
                 "the agent had nothing to call. A is ruled out because the same descriptions work in teammates' sessions. B invents a "
                 "limit on servers. C asks for a prompt workaround for a server that is not running."),
        scenarios=(4,), points=("2.4:K3",),
        evidence=(Evidence("code:mcp", "After a server connects, Claude Code sends it capability discovery requests such as `tools/list`, `prompts/list`, and `resources/list`."),),
        qtype="diagnose", level="easy", principle="root_cause",
        situation="deploys server failed to launch so the agent falls back to git log",
        trap="blame tool descriptions for a server that never connected",
    ),
    MCQ(
        id="Q2.4-09",
        q=("A research agent in Claude Code has two servers connected. The `literature` server has a tool `search` described as "
           "\"Search for relevant information.\" The `notes` server, which holds the team's meeting notes, also has a `search` tool "
           "with the same description. In 28 of 80 logged runs the agent sent a question about published papers to the `notes` "
           "server's `search` and reported no results. What is the most likely root cause?"),
        opts=("Both are offered together, and identical descriptions give the agent no way to tell them apart.",
              "The two tools share a name, so one overwrites the other and only the later server's `search` is offered.",
              "Claude Code lets only one tool called `search` run per session, and the `notes` server connected first.",
              "The agent tries servers in alphabetical order, so the `notes` tool is always tried before `literature`."),
        ans=0,
        explain=("Every connected server's tools sit in the same pool, and the agent picks between them from the descriptions, so two "
                 "that read alike get mixed up; each should say what it searches and what it returns. B is wrong because a tool's full "
                 "name includes its server, so the two do not collide. C and D describe selection rules that Claude Code does not have."),
        scenarios=(3,), points=("2.4:K3", "2.4:S3"),
        evidence=(Evidence("code:mcp", "select the tool to see its full name, such as `mcp__<server>__<tool>`."),
                  Evidence("api:agents-and-tools/tool-use/define-tools", "This is by far the most important factor in tool performance.")),
        qtype="diagnose", level="hard", principle="root_cause",
        situation="two servers each expose a search tool with the same one-line description",
        trap="assume the same tool name makes one server's tool replace the other",
    ),
    # ---- K4: resources expose content catalogues ----
    MCQ(
        id="Q2.4-10",
        q=("Your coding agent's `search_docs` tool queries a 600-page internal handbook. Traces show 4 to 6 searches per session just "
           "to learn which sections exist before the right page turns up. The server can publish its section tree: titles, paths and "
           "a one-line purpose for each. Engineers want the tree in view from the start of a session, without relying on the model "
           "deciding to look for it. What should the server do?"),
        opts=("Add a `list_sections` tool, and tell the model in the prompt to call it before any search.",
              "Publish the section tree as an MCP resource that engineers attach with an @ reference.",
              "Raise `search_docs` from 5 to 25 results per call so that the right page appears sooner.",
              "Paste the section tree into the `search_docs` description so it is seen with every call."),
        ans=1,
        explain=("A resource is content the application attaches as context, so the model sees what exists without spending calls to "
                 "find out. A still depends on the model choosing to call the tool. C returns more of the same results and does not "
                 "show the structure. D puts a large tree into a description, where long text is cut off."),
        scenarios=(4,), points=("2.4:K4",),
        evidence=(Evidence("code:mcp", "Type `@` in your prompt to see available resources from all connected MCP servers."),
                  Evidence("code:mcp", "Resources are automatically fetched and included as attachments when referenced")),
        qtype="choose", level="easy", principle="fit_for_purpose",
        situation="documentation tree discovered through 4 to 6 blind searches",
        trap="add a list tool the model must remember to call",
    ),
    MCQ(
        id="Q2.4-11",
        q=("Your warehouse server publishes a `warehouse://schema` resource that engineers attach to sessions. Since it went live, "
           "discovery calls fell from 6 to 1 per session, but \"table not found\" errors rose to 22 a week, clustered in the days "
           "after schema migrations. The server is redeployed only at release time. What is the most likely root cause?"),
        opts=("Claude Code cuts attached resources off after 50 entries, so later tables never reach the agent.",
              "The agent ignores an attached resource whenever the question names a specific table.",
              "The catalogue is a snapshot from the last release, so it describes tables as they were then.",
              "The client fetches resources once a day, so changes appear only after the next daily refresh."),
        ans=2,
        explain=("A catalogue exists to be trusted instead of explored, so it must be built from the live schema when it is read; "
                 "content fixed at release time goes stale between releases, which fits errors after migrations. A and "
                 "B would hit tables at random, not those just changed. D invents a daily fetch cycle."),
        scenarios=(4,), points=("2.4:K4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: no official page speaks to keeping a catalogue resource current; this is a server-design judgment built on TS 2.4 Knowledge 4.",
        qtype="diagnose", level="hard", principle="root_cause",
        situation="schema resource served from a build-time file misses renamed tables",
        trap="blame the client for truncating or ignoring the resource",
    ),
    MCQ(
        id="Q2.4-12",
        q=("The `run_query` tool of your analytics server has a 40-table schema, about 30,000 characters, pasted into its "
           "description so that the agent knows the tables. The agent often invents column names that appear only in the second half "
           "of the schema. Which change fixes this?"),
        opts=("Cut the description down to table names only, so it stays within what Claude Code keeps.",
              "Repeat the column lists at the end of the description, where they are read last.",
              "Replace `run_query` with 40 per-table tools, each carrying its own columns in its description.",
              "Move the schema to an MCP resource, and keep the description to what `run_query` does."),
        ans=3,
        explain=("Claude Code cuts a long description and the agent sees only the text before the cut, which is why the later columns "
                 "are guessed. A catalogue belongs in a resource that is attached when needed, leaving the description short and "
                 "useful. A removes the columns the agent needs. B puts them at the end, which is the part that gets cut. C swaps "
                 "one tool for 40 and loads the same schema text, spread across 40 descriptions."),
        scenarios=(4,), points=("2.4:K4",),
        evidence=(Evidence("code:mcp", "Claude Code cuts a tool description or server instructions that run past these default limits, and Claude sees only the text before the cut:"),),
        qtype="choose", level="medium", principle="fit_for_purpose",
        situation="whole schema pasted into a query tool's description",
        trap="repeat the columns at the end of the description",
    ),
    # ---- S1: shared .mcp.json with variable expansion ----
    MCQ(
        id="Q2.4-13",
        q=("Which entry in the committed `.mcp.json` gives every engineer the same remote Sentry server, each using a personal token, "
           "with no secret in git?"),
        opts=("`\"sentry\": {\"type\": \"http\", \"url\": \"https://mcp.sentry.example.com/mcp\", \"headers\": {\"Authorization\": \"Bearer ${SENTRY_TOKEN}\"}}`",
              "The same entry with `\"Authorization\": \"Bearer ${SENTRY_TOKEN:-team-shared-token}\"`, so the server works before anyone sets a token.",
              "The same entry with `\"Authorization\": \"Bearer <your-token>\"`, which each engineer edits locally before starting a session.",
              "The same entry with an empty `headers` object, and each engineer adds their own header to a user-scoped `sentry` entry."),
        ans=0,
        explain=("The variable reference keeps the secret out of the file, and each engineer's shell supplies their own value. B puts a "
                 "shared token in git as the default. C has everyone edit a tracked file and risk committing the edit. D fails "
                 "because when one name is defined in two scopes, the project entry is used whole and the user entry is ignored."),
        scenarios=(4,), points=("2.4:S1",),
        evidence=(Evidence("code:mcp", "expands to the value of environment variable `VAR`"),
                  Evidence("code:mcp", "The entire server entry from that source is used; fields are not merged across scopes.")),
        qtype="configure", level="easy", principle="least_privilege",
        situation="shared remote server needs a per-engineer bearer token",
        trap="give the variable a shared-token default",
    ),
    MCQ(
        id="Q2.4-14",
        q=("A pull request adds a community-built Kafka-inspection server to the repository's `.mcp.json`, with its token written as "
           "`${KAFKA_TOKEN}`. Engineers get an approval prompt for project servers in interactive sessions, and a reviewer wants to "
           "merge because \"each engineer will vet it when prompted\". The repository also runs `claude -p` in CI on every pull "
           "request. How should you evaluate this?"),
        opts=("Merge: the approval prompt gives each engineer a chance to vet it, and CI is covered by the same prompt.",
              "Review it before merging: non-interactive runs load project servers without asking.",
              "Merge: a token passed as a variable means the server cannot reach anything beyond what that token allows.",
              "Reject: community-built servers may not be committed to `.mcp.json`; only custom servers belong there."),
        ans=1,
        explain=("A committed project server reaches every engineer and every CI run, and where Claude Code cannot show the prompt it "
                 "loads the server without asking, so the review has to happen at merge time. A assumes a prompt that CI never sees. "
                 "C mixes up the token's reach with the server's, which runs its own code. D contradicts the guidance to prefer "
                 "existing servers for standard integrations."),
        scenarios=(4,), points=("2.4:K1",),
        evidence=(Evidence("code:mcp", "Claude Code can't show that prompt: it loads project-scoped servers without asking."),
                  Evidence("code:mcp", "Verify you trust each server before connecting it.")),
        basis="docs",
        qtype="evaluate", level="hard", principle="least_privilege",
        situation="community server added to .mcp.json while CI runs claude -p",
        trap="rely on the interactive approval prompt as the review",
    ),
    MCQ(
        id="Q2.4-15",
        q=("A researcher adds this to the repository's `.mcp.json`: an `archive` entry with `\"url\": "
           "\"https://archive.example.com/mcp\"` and `\"headers\": {\"Authorization\": \"Bearer ${ARCHIVE_TOKEN}\"}`. Everyone "
           "has exported `ARCHIVE_TOKEN`, yet nobody sees any archive tools, and a configuration warning about the entry appears at "
           "startup. What is the most likely root cause?"),
        opts=("A header value cannot contain a variable reference, because only `env` values expand.",
              "A root-level `.mcp.json` is read only for stdio servers; remote ones need `.claude/mcp.json`.",
              "The entry has no `type`, so Claude Code reads it as a stdio server and skips it.",
              "The token must first be listed in a committed `.env`, or the entry is rejected at startup."),
        ans=2,
        explain=("A remote entry needs `\"type\": \"http\"`; without it Claude Code treats the entry as a local command, finds none, "
                 "and skips it with a warning. A is wrong because `headers` is one of the places that expand. B and D invent file "
                 "locations and a `.env` requirement that Claude Code does not have."),
        scenarios=(3,), points=("2.4:S1",),
        evidence=(Evidence("code:mcp", "A JSON entry that has a `url` but no `type` is a configuration error, because Claude Code reads an entry with no `type` as a stdio server."),),
        basis="docs",
        qtype="diagnose", level="medium", principle="root_cause",
        situation="remote archive entry without a type field never loads",
        trap="blame the header variable reference",
    ),
    # ---- S2: personal servers in user scope ----
    MCQ(
        id="Q2.4-16",
        q=("A staff engineer wants to trial a new code-search server for two weeks. It starts in about 20 seconds and exposes 3 "
           "tools. To make it easy for the 11 engineers who want to try it, she proposes adding it to the committed `.mcp.json` "
           "and \"removing it if it doesn't work out\". The other 12 engineers have not asked for it. How should you evaluate this?"),
        opts=("Accept: removing the entry later is one more commit, so nobody is harmed in the meantime.",
              "Accept it on a long-lived branch that only the interested engineers check out and keep up to date.",
              "Accept it, with a README note that the server is experimental and optional for everyone.",
              "Reject it: interested engineers add it at user scope, and promote it if the trial succeeds."),
        ans=3,
        explain=("A trial server is personal and experimental, so it belongs at user scope, and only a server the team has decided to "
                 "adopt belongs in the shared file. A and C put the approval prompt and the server in front of all 23 engineers. B turns the "
                 "trial into a branch to be kept in step with the main one."),
        scenarios=(4,), points=("2.4:S2",),
        evidence=(Evidence("code:mcp", "User-scoped servers are stored in `~/.claude.json` and provide cross-project accessibility, making them available across all projects on your machine while remaining private to your user account."),),
        qtype="evaluate", level="medium", principle="proportionate",
        situation="two-week trial of a code-search server proposed for the shared file",
        trap="add it to the shared file and remove it later",
    ),
    MCQ(
        id="Q2.4-17",
        q=("A researcher wrote a stdio script, `/home/maya/tools/notes_mcp.py`, that searches her own markdown notes. She wants it "
           "available in every project she opens, and no teammate has that file. Which command sets it up?"),
        opts=("`claude mcp add --transport stdio --scope user notes -- python /home/maya/tools/notes_mcp.py`",
              "`claude mcp add --transport stdio notes -- python /home/maya/tools/notes_mcp.py`, run once in each project that she opens",
              "`claude mcp add --transport stdio --scope project --env NOTES_DIR=/home/maya/notes notes -- python /home/maya/tools/notes_mcp.py`",
              "`claude mcp add --transport http --scope user --env NOTES_DIR=/home/maya/notes notes /home/maya/tools/notes_mcp.py`"),
        ans=0,
        explain=("`--scope user` stores the server in her `~/.claude.json` for all her projects, and everything after `--` is the "
                 "command that starts the script. B leaves out the scope, so the default local scope applies and each project needs "
                 "its own command. C writes her home path into a file the team shares. D treats a local script as an HTTP endpoint."),
        scenarios=(3,), points=("2.4:S2",),
        evidence=(Evidence("code:mcp", "Local scope is the default. A local-scoped server loads only in the project where you added it and stays private to you."),),
        qtype="configure", level="easy", principle="fit_for_purpose",
        situation="personal stdio notes script wanted in every project",
        trap="omit --scope so the default local scope applies",
    ),
    MCQ(
        id="Q2.4-18",
        q=("An engineer adds an `analytics` server at user scope, pointing at her sandbox URL, to try a new endpoint in all her "
           "repositories. In the team repository, whose committed `.mcp.json` also defines `analytics` with the shared URL, her "
           "sessions still reach the shared server and she sees only its tools. What is the most likely root cause?"),
        opts=("Claude Code merges the two entries field by field, and the URL from the file loaded first wins.",
              "The project entry outranks the user entry, and is used whole while her sandbox entry is ignored.",
              "User-scoped servers apply only in repositories that have no `.mcp.json` file of their own.",
              "Entries in `~/.claude.json` load only once she approves them with `claude mcp reset-project-choices`."),
        ans=1,
        explain=("When a name is defined in more than one scope, Claude Code connects once, using the whole entry from the "
                 "highest-precedence scope, and project scope ranks above user scope. A is wrong because fields are not merged. C "
                 "invents a restriction on user scope. D mixes up the reset command, which concerns approvals for project servers."),
        scenarios=(4,), points=("2.4:S2", "2.4:K1"),
        evidence=(Evidence("code:mcp", "When the same server is defined in more than one place, Claude Code connects to it once, using the definition from the highest-precedence source."),
                  Evidence("code:mcp", "The entire server entry from that source is used; fields are not merged across scopes.")),
        basis="docs",
        qtype="diagnose", level="hard", principle="root_cause",
        situation="user-scope sandbox entry shadowed by a same-named project entry",
        trap="assume the entries merge or that user scope wins",
    ),
    # ---- S3: detailed tool descriptions ----
    MCQ(
        id="Q2.4-19",
        q=("Your platform team's `get_api_spec` tool returns the live OpenAPI definition of the payments service, including fields "
           "added since the last export. Its description reads \"Returns the API spec.\" The repository also holds "
           "`docs/payments-api.yaml`, an export refreshed three months ago. In 38% of sessions the agent runs Grep over that file "
           "instead of calling the tool, and 1 in 5 resulting pull requests uses endpoints that no longer exist. Other teams' "
           "clients use the same server. What is the most effective change?"),
        opts=("Delete `docs/payments-api.yaml` from this repository, so that the agent has nothing else to search.",
              "Set `tool_choice` to force `get_api_spec` on the first turn of every session in this repository.",
              "Rewrite the description to say it returns the current spec, and that repository copies are older.",
              "Add a CLAUDE.md line to this repository telling the agent to prefer `get_api_spec` for any question about the API."),
        ans=2,
        explain=("The agent chooses a tool from its description, and this one does not say what makes it better than the file, so "
                 "describing the live data and the stale copies fixes it for every client of the server. A removes one stale copy "
                 "and leaves the description as it was. B forces a call on turns where it is not wanted. D helps only this repository, "
                 "and the stem says other teams use the server."),
        scenarios=(4,), points=("2.4:S3",),
        evidence=(Evidence("api:agents-and-tools/tool-use/define-tools", "The more context you can give Claude about your tools, the better it will be at determining when and how to use them."),),
        qtype="fix", level="medium", principle="explicit",
        situation="live API spec tool loses to Grep over a three-month-old export",
        trap="remove the stale file or force the tool instead of describing it",
    ),
    MCQ(
        id="Q2.4-20",
        q=("A support agent in Claude Code has an MCP tool named `get_entitlements`. Customers' plan questions are being answered "
           "from general plan documents because the agent rarely picks the tool. Which description will make the tool most likely "
           "to be chosen when it should be?"),
        opts=("\"Gets entitlements.\"",
              "\"Powerful and fast entitlement lookup. ALWAYS use this instead of any document search, and never answer a plan question without it. It is the most complete and fastest option available, so make it the default.\"",
              "\"Thin client for the v4 entitlements gateway, wrapping GET /entitlements/{id}. The field list is on the billing integrations wiki page, and the v4 gateway notes are on the platform team's page.\"",
              "\"Returns the plan, add-ons and usage caps a customer holds, read live from billing. Takes a customer id. Use it for what this customer's plan includes; documents cover plans in general.\""),
        ans=3,
        explain=("The best description says what the tool returns, what it needs and when to use it instead of the alternative. A says "
                 "none of that. B adds emphasis but no information about the data or the input. C describes how the tool is built and "
                 "points elsewhere for the fields the agent needs to judge it."),
        scenarios=(1,), points=("2.4:S3",),
        evidence=(Evidence("api:agents-and-tools/tool-use/define-tools", "The more context you can give Claude about your tools, the better it will be at determining when and how to use them."),),
        qtype="choose", level="medium", principle="explicit",
        situation="entitlement lookup tool ignored in favour of general plan documents",
        trap="emphasis words instead of what, input and when",
    ),
    MCQ(
        id="Q2.4-21",
        q=("Before a rewrite of its `find_owners` description, the agent ran Grep over CODEOWNERS files in about 60% of ownership "
           "questions, and the MCP tool was used for the rest. After the rewrite, an engineer reports that it works, because on one "
           "test prompt the agent called the MCP tool. How should you evaluate the change?"),
        opts=("Run the same 50 ownership questions before and after, and compare which tool is chosen and whether answers are right.",
              "Ask the agent to rate how clear the new description is, and accept the change if it gives 8 out of 10 or higher.",
              "Accept it: a successful call on a test prompt shows that the description now outweighs the agent's habit of using Grep.",
              "Run the rewritten description 20 times on that same test prompt, and accept it if the tool is called every time."),
        ans=0,
        explain=("A change in tool choice is a rate across many realistic questions, and it has to be compared with the same questions "
                 "before the change; correctness matters too, because a tool picked wrongly is no gain. B relies on the agent's own "
                 "opinion of the text. C and D rest on a single prompt, so they cannot show a change in the 60%."),
        scenarios=(4,), points=("2.4:S3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 2.4 Skill 3 says detailed descriptions prevent built-in tool preference; how to measure that is an evaluation judgment no official page states.",
        qtype="evaluate", level="hard", principle="independent_check",
        situation="one successful test prompt after a find_owners description rewrite",
        trap="judge a description by one prompt or by the agent's rating",
    ),
    # ---- S4: community versus custom servers ----
    MCQ(
        id="Q2.4-22",
        q=("The team wants an agent to answer questions from its reporting Postgres database. A community-built Postgres server with a "
           "clear README, recent commits and an active issue list covers the five queries needed. A custom server would take about "
           "two engineer-weeks. How should you evaluate adopting the community server?"),
        opts=("Adopt it as it is: active maintainers mean it has been checked, so connecting with the admin account is fine.",
              "Adopt it after reading what it does with queries, and connect it with a read-only database account.",
              "Build the custom server anyway, because any code that touches the database must be written in-house.",
              "Adopt it with the read-write account the team's other tools use, since reporting queries only read."),
        ans=1,
        explain=("A standard integration should come from an existing server, with a check on what it does and the least access it "
                 "needs, here a read-only account. A treats maintenance as a security review and hands over full rights. C spends two "
                 "weeks on something that exists. D gives a server that can run any statement more access than reporting needs."),
        scenarios=(4,), points=("2.4:S4",),
        evidence=(Evidence("code:mcp", "Verify you trust each server before connecting it."),),
        qtype="evaluate", level="medium", principle="least_privilege",
        situation="community Postgres server covers the five reporting queries needed",
        trap="build in-house for anything that touches a database",
    ),
    MCQ(
        id="Q2.4-23",
        q=("Your support team uses a well-maintained community ticketing server that covers searching, reading, commenting and "
           "updating tickets. The agent also needs an `sla_breach_risk` tool that applies your own contract-specific rules to a "
           "ticket's history. One engineer has part of a week each month for this. What is the best plan?"),
        opts=("Fork the community server, add the SLA logic to it, and merge its upstream releases by hand.",
              "Replace the community server with a custom one covering all five operations, so that everything follows one design.",
              "Keep the community server for standard operations, and add a small custom one for `sla_breach_risk` only.",
              "Ask the community server's maintainers to add the SLA rules, and enable the agent after their next release."),
        ans=2,
        explain=("Standard operations should come from the existing server, and only the logic unique to your contracts needs code you "
                 "own, so a small custom server with one tool keeps the upkeep tiny. A makes a part-time engineer carry the whole "
                 "community server through every upstream change. B rebuilds four tools that already work. D asks outsiders to "
                 "implement rules that are specific to your company."),
        scenarios=(1,), points=("2.4:S4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 2.4 Skill 4 says to choose existing community servers for standard integrations and reserve custom servers for team-specific workflows.",
        qtype="choose", level="hard", principle="proportionate",
        situation="community ticketing server lacks a contract-specific SLA risk tool",
        trap="fork the whole community server to add one tool",
    ),
    MCQ(
        id="Q2.4-24",
        q=("The team needs its agent to search a Confluence space, fetch pages and browse the page tree, read-only, and finds three "
           "community servers. One has the most GitHub stars and runs read-only, but only fetches a page by id. One has 40 tools and was last updated 18 months ago. The third covers "
           "search, page fetch and listing a space's page tree, was updated last month, and can be run read-only. Which should the "
           "team choose?"),
        opts=("The one with the most stars: it is widely used and already runs read-only.",
              "The one with 40 tools, because the broadest server will cover whatever the agent needs later.",
              "None of them: write a custom server so that the tools match the team's own naming.",
              "The one covering search, fetch and page-tree listing, recently updated and read-only."),
        ans=3,
        explain=("Pick the existing server that covers the operations needed, is still maintained, and can be limited to reading. A "
                 "is popular and read-only, but cannot search or browse. B takes breadth and age over fit, and a stale server is an upkeep risk. C "
                 "builds a custom server for a standard integration and gains only naming."),
        scenarios=(4,), points=("2.4:S4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 2.4 Skill 4 prefers existing servers for standard integrations; the selection criteria are an engineering judgment.",
        qtype="choose", level="medium", principle="fit_for_purpose",
        situation="three community Confluence servers to choose between",
        trap="choose by stars or by tool count",
    ),
    # ---- S5: catalogues as resources ----
    MCQ(
        id="Q2.4-25",
        q=("A research agent reads papers through a `fetch_paper(id)` tool on an internal server. The ids are opaque strings, and in "
           "41% of sessions the agent spends 3 to 5 calls searching and guessing before it finds an id that exists. The server can "
           "list its 3,000 papers with id, title and year. Which change most directly removes the guessing?"),
        opts=("Expose the paper list (id, title, year) as a resource, readable before any fetch call.",
              "Make `fetch_paper` return the five closest ids whenever an id is not found.",
              "Add an instruction telling the agent to try ids in ascending order until one resolves.",
              "Raise the agent's turn limit so that the guessing has room to finish before an answer is due."),
        ans=0,
        explain=("The agent guesses because it cannot see what exists, and a catalogue resource shows it before the first call. B "
                 "still makes the agent fail, then try again, and C turns guessing into a procedure. D accepts the wasted calls and "
                 "gives them more room."),
        scenarios=(3,), points=("2.4:S5",),
        evidence=(Evidence("code:mcp", "Claude Code automatically provides tools to list and read MCP resources when servers support them"),),
        qtype="fix", level="medium", principle="preserve_information",
        situation="opaque paper ids are guessed over 3 to 5 calls",
        trap="return nearest ids on failure instead of showing what exists",
    ),
    MCQ(
        id="Q2.4-26",
        q=("Your support agent's server holds 2,400 open cases. The agent opens full case records one by one, about 6 `get_case` calls "
           "per new complaint, to find duplicates, and each full record averages 8,000 characters. Case titles are often generic, such as \"Billing problem\". The server owner wants to expose "
           "a case catalogue as a resource. What should it contain?"),
        opts=("Every open case in full, so that the agent never needs `get_case` again.",
              "One line per case: id, title, status and a short summary.",
              "One line per case with its id and title only, to keep the list short.",
              "The 50 most recent cases in full, since duplicates are usually recent."),
        ans=1,
        explain=("A catalogue should be short enough to attach and rich enough to choose from, so the agent can spot a likely duplicate "
                 "and open only that case. A is about 19 million characters. C leaves generic titles with nothing to tell cases apart. D drops older cases "
                 "that may be the duplicate and still carries 400,000 characters."),
        scenarios=(1,), points=("2.4:S5",),
        evidence=(Evidence("code:mcp", "Resources are automatically fetched and included as attachments when referenced"),),
        qtype="choose", level="easy", principle="fit_for_purpose",
        situation="case catalogue resource for duplicate detection across 2,400 cases",
        trap="attach full records instead of a compact index",
    ),
    MCQ(
        id="Q2.4-27",
        q=("Your warehouse schema changes most days. About one session in five touches the warehouse, mostly analytics questions "
           "rather than edits to warehouse files, and those sessions waste 5 or 6 calls discovering tables. Someone proposes a nightly "
           "job that writes the schema into a section of the repository's CLAUDE.md. Which approach is best?"),
        opts=("Do the nightly CLAUDE.md job, since memory files are always in context and cannot be missed.",
              "Write the nightly job's output to a path-scoped rules file, so that it loads when warehouse files are open.",
              "Expose the schema as an MCP resource that the server builds from the live database when it is read.",
              "Add a `describe_schema` tool and a prompt rule telling the agent to call it at the start of every session."),
        ans=2,
        explain=("A resource is read when wanted and generated from the live database, so it is current and costs nothing in the four "
                 "sessions in five that never touch the warehouse. A loads a day-old schema into every session. B loads only when "
                 "warehouse files are open, which these sessions do not do. D makes all sessions spend a call at the start."),
        scenarios=(4,), points=("2.4:S5",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 2.4 Skill 5 names resources for catalogues; comparing them with memory files is a fit-for-purpose judgment.",
        qtype="choose", level="medium", principle="fit_for_purpose",
        situation="daily-changing schema proposed as a nightly CLAUDE.md section",
        trap="load a day-old catalogue into every session through memory files",
    ),
)
