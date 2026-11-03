"""Exam bank · TS 5.4. Original questions; see docs/MCQ_BANK_PLAN.md."""
from utils.mcq_sets import MCQ, Evidence

TS = "5.4"
BULLETS = {
    "K1": "Context degradation in long sessions: inconsistent answers and generic 'typical patterns' instead of specific classes found earlier",
    "K2": "Scratchpad files persist key findings across context boundaries",
    "K3": "Subagents isolate verbose exploration output while the main agent keeps high-level understanding",
    "K4": "Crash recovery needs structured state: each agent exports state to a known place and the coordinator loads a manifest on resume",
    "S1": "Spawning subagents for specific questions while the main agent keeps coordinating",
    "S2": "Having agents keep scratchpad files and consult them for later questions",
    "S3": "Summarizing one exploration phase and injecting the summary into the next phase's subagents",
    "S4": "Designing crash recovery with manifests that the coordinator loads and injects into agent prompts",
    "S5": "Using /compact to cut context use when exploration has filled it with verbose discovery output",
}

_ROT = Evidence("api:build-with-claude/context-windows",
                "As token count grows, accuracy and recall degrade, a phenomenon known as context rot.")
_FRESH = Evidence("code:sub-agents",
                  "Each subagent starts with a fresh, isolated context window. It doesn't see your conversation history, the skills you've already invoked, or the files Claude has already read.")
_ISOLATE = Evidence("code:sub-agents",
                    "By delegating these to a subagent, the verbose output stays in the subagent's context while only the relevant summary returns to your main conversation.")
_STRUCT = Evidence("api:build-with-claude/prompt-engineering/claude-prompting-best-practices",
                   "When tracking structured information (such as test results or task status), use JSON or other structured formats to make schema requirements explicit to Claude.")

QUESTIONS = (
    # ---- K1: context degradation ----
    MCQ(
        id="Q5.4-01",
        q=("A developer spends four hours in one Claude Code session mapping a billing service. In the first hour the agent named "
           "`LedgerReconciler` and `RetryPolicyV2` and said tax is computed in `InvoiceBuilder`. By hour four, after 300 turns, it says "
           "\"a repository class typically handles this\" and places tax calculation in a different module. `/context` shows 78% used, "
           "mostly file reads and command output. What is the most likely root cause?"),
        opts=("The repository index went stale as files changed, so searches now return generic matches.",
              "Hours of tool output bury the earlier findings, so answers drift toward generic patterns.",
              "`CLAUDE.md` stopped loading after the first hour, so the class names are no longer visible.",
              "The model's sampling temperature rises as a session grows, which makes its answers vary more."),
        ans=1,
        explain=("Accuracy and recall fall as the accumulated context grows, so specifics found early give way to generic wording and "
                 "contradictions. A invents an index; Claude Code searches the files directly. C is wrong because the project-root CLAUDE.md is "
                 "re-injected from disk after compaction. D describes a setting that does not change during a session."),
        scenarios=(2,), points=("5.4:K1",),
        evidence=(_ROT, Evidence("code:context-window", "Project-root CLAUDE.md and unscoped rules | Re-injected from disk")),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="four-hour billing-service session answers with generic patterns and moves tax to another module",
        trap="blame a stale index, instructions or temperature",
    ),
    MCQ(
        id="Q5.4-02",
        q=("In a long session an agent says unit tests for `payments/` live under `tests/unit/`, while a colleague insists they sit in "
           "`payments/tests/`. The engineer suspects the search tooling. The session is at hour six with about 60% of the context in use. "
           "Which check best separates a tooling fault from context degradation?"),
        opts=("Ask the same question again in this same session and see whether the answer changes at all.",
              "Ask the agent to rate its confidence in the answer on a scale of 1 to 10, then compare.",
              "Ask the same question in a fresh session on the same checkout and compare the answers.",
              "Run the agent's search command by hand and check that it returns results at all."),
        ans=2,
        explain=("A fresh session has the same tools and the same files but none of the accumulated history, so a specific, correct answer "
                 "there points to the long context. A repeats the question inside the same context, which proves little. B uses "
                 "self-reported confidence, which is not evidence. D shows the command runs, not whether the agent still uses its "
                 "results well."),
        scenarios=(2,), points=("5.4:K1",),
        evidence=(_ROT,),
        qtype="evaluate", level="medium", principle="independent_check",
        situation="agent and colleague disagree on where payments tests live at hour six",
        trap="re-ask in the same context or ask for a confidence score",
    ),
    MCQ(
        id="Q5.4-03",
        q=("A research team runs a 1M-token model and argues that context degradation cannot affect them: their agent sessions peak at "
           "40% of the window. Yet in 25-turn runs over 40 sources, the agent now says \"industry sources generally agree\" where it "
           "earlier named six analyst reports. How should the team read this?"),
        opts=("Quality holds steady until the window is nearly full, so the search tool must be at fault.",
              "The effect appears only after compaction, so switching compaction off will restore the specifics.",
              "A window this large removes the effect, so the source list must be confusing the agent.",
              "Accuracy and recall can fall as content builds up, well below the limit, so curate context."),
        ans=3,
        explain=("The docs tie degradation to growing token count, not to hitting the limit, so curating what stays in context matters at 40% "
                 "too. A assumes a cliff at the limit and blames a tool without evidence. B ties the effect to compaction, but the "
                 "run never compacted. C treats a larger window as a cure; it only changes where the limit sits."),
        scenarios=(3,), points=("5.4:K1",),
        evidence=(_ROT,),
        qtype="evaluate", level="hard", principle="fit_for_purpose",
        situation="analyst reports become 'sources generally agree' at 40% of a 1M window",
        trap="assume a big window or the limit decides degradation",
    ),
    # ---- K2: scratchpad files ----
    MCQ(
        id="Q5.4-04",
        q=("An agent is finding every authentication call site in a 600-file monorepo and expects the session to run for hours. The "
           "developer wants the confirmed sites to survive context turnover. Which approach is most effective?"),
        opts=("Have the agent append each confirmed site (file, symbol, status) to a notes file as it goes.",
              "Ask the agent for one full summary of all confirmed sites once the exploration has finished.",
              "Record the confirmed sites in `CLAUDE.md`, so that every later session starts with them.",
              "Keep the sites in the conversation and rely on the model's large context window to hold all of them."),
        ans=0,
        explain=("A file written as findings appear is on disk, so compaction does not affect it, and a new session can read it. "
                 "B writes everything at the end, after the earlier findings may already have been summarised away. C puts task findings "
                 "in a file meant for standing rules, which every later task would then load. D leaves the findings inside the context "
                 "that degrades."),
        scenarios=(2,), points=("5.4:K2",),
        evidence=(Evidence("code:agent-sdk/sessions", "Sessions persist the conversation, not the filesystem."), Evidence("code:large-codebases", "Claude Code re-injects the plan file after each compaction, so the plan survives where conversation history may not")),
        qtype="choose", level="easy", principle="preserve_information",
        situation="hours-long hunt for authentication call sites in a 600-file monorepo",
        trap="summary at the end, findings in CLAUDE.md, or trust the window",
    ),
    MCQ(
        id="Q5.4-05",
        q=("A research agent keeps `notes/findings.md` and has 85 correct entries by turn 60. In a final check, it states a market figure "
           "that contradicts entry 31. The tool log shows the agent called Read on the notes file at turn 1, when it was empty, and "
           "wrote to it at turns 12, 19 and 33 only. What is the most likely root cause?"),
        opts=("The notes were kept in Markdown rather than JSON, so the agent was unable to use the entries.",
              "The agent wrote the file but never read it back, so the entries did not reach its context.",
              "Files written during a session are lost from disk when the context is later compacted away.",
              "An 85-entry file is too large for the Read tool to return in one call, so it was cut off."),
        ans=1,
        explain=("A scratchpad helps only when its contents are brought back into context; here the only Read happened when the file "
                 "was empty. A blames the format, although Markdown notes are fine. C is wrong because files on disk are not part of "
                 "the conversation and stay put. D invents a limit that 85 short entries would not reach."),
        scenarios=(3,), points=("5.4:K2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: that a scratchpad must be read back into context to help is a design judgment from the guide.",
        qtype="diagnose", level="medium", principle="root_cause",
        situation="agent contradicts entry 31 of its own notes after reading the file only when empty",
        trap="blame the format, compaction or file size",
    ),
    MCQ(
        id="Q5.4-06",
        q=("After three hours mapping a legacy order system, a developer wants the agent's scratchpad to be useful to a colleague who "
           "picks up tomorrow. Which kind of entry is most useful?"),
        opts=("The full text of each file the agent read, so nothing is lost between sessions.",
              "A running prose guess about the overall design, updated whenever the agent changes its mind.",
              "Confirmed facts with file paths and symbol names, plus a list of questions still open.",
              "A log of every command the agent ran, in order, with its raw output."),
        ans=2,
        explain=("Specific, checkable facts with locations, plus open questions, give a reader what the agent would otherwise have to "
                 "rediscover. A copies the files back into context, which defeats the purpose. B keeps the vague, generic wording that "
                 "degradation produces. D records activity instead of conclusions and would fill context again."),
        scenarios=(2,), points=("5.4:K2",),
        evidence=(_STRUCT,),
        qtype="choose", level="easy", principle="preserve_information",
        situation="scratchpad for a legacy order system handed to a colleague tomorrow",
        trap="store raw files, prose guesses or command logs",
    ),
    # ---- K3: subagent delegation ----
    MCQ(
        id="Q5.4-07",
        q=("A developer asks the main agent which of 14 nightly load-test runs regressed. Each run prints about 6,000 lines of timing "
           "tables. After reading all of them in the main conversation, the agent forgets the 5% regression threshold agreed earlier "
           "and flags runs the team had already accepted. What is the most effective fix?"),
        opts=("Run `/clear` before the comparison starts, then paste the agreed threshold back in afterwards.",
              "Limit each read to the first 200 lines of a run so that less text enters the context window.",
              "Move to a model with a bigger window, and carry on reading every run in the main chat.",
              "Delegate the comparison to a subagent that returns the regressed runs and their deltas."),
        ans=3,
        explain=("The timing tables stay in the subagent's context, and only the short result returns, so the threshold stays in view. "
                 "A throws away the session along with the noise. B drops lines that may hold the regression. C keeps the bulk in "
                 "the main context, only moving the limit."),
        scenarios=(2,), points=("5.4:K3",),
        evidence=(_ISOLATE,),
        qtype="fix", level="easy", principle="fit_for_purpose",
        situation="84,000 lines of load-test timings make the agent forget the agreed regression threshold",
        trap="clear the session, truncate output or buy a bigger window",
    ),
    MCQ(
        id="Q5.4-08",
        q=("A team is moving a 1,200-file legacy application to a new framework. The lead wants the main agent to keep the overall "
           "picture and make design decisions throughout a two-day effort. Which structure fits best?"),
        opts=("The main agent keeps a module map and decisions; a subagent per module returns a short summary.",
              "The main agent reads each module in turn and runs `/clear` between modules to keep the context small.",
              "One subagent explores the whole application and returns everything it found for the main agent to use.",
              "The main agent reads all modules itself, and subagents are used only to make the edits afterwards."),
        ans=0,
        explain=("The module reads stay in subagent contexts, and the main agent holds the map, decisions and summaries. B clears the map "
                 "with each module. C returns an application-sized report into the main context and loses the isolation. D leaves the "
                 "verbose reading where it does the most harm."),
        scenarios=(2,), points=("5.4:K3",),
        evidence=(_ISOLATE,),
        qtype="choose", level="medium", principle="fit_for_purpose",
        situation="two-day migration of a 1,200-file application with the main agent as coordinator",
        trap="clear between modules, one giant subagent, or delegate only edits",
    ),
    MCQ(
        id="Q5.4-09",
        q=("A research coordinator spawns subagents that each read about 200,000 tokens of company filings. After the first subagent "
           "finishes, the coordinator's own context has grown by 28,000 tokens, and after four the coordinator is losing track of the "
           "overall plan. What is the most likely root cause?"),
        opts=("Subagent contexts are merged into the coordinator's when a subagent finishes.",
              "The subagents should have run in parallel, because sequential runs keep results longer in context.",
              "The coordinator should have read the filings itself so that nothing gets compressed.",
              "Each subagent's final message was long, and only that message enters the coordinator's context."),
        ans=3,
        explain=("Isolation holds only if what comes back is short: the final message is the one thing the coordinator receives, so a long "
                 "report brings the bulk back in. A is false; contexts stay separate. B changes timing, not size. C would put all the "
                 "filings in the coordinator's context, which is worse."),
        scenarios=(3,), points=("5.4:K3",),
        evidence=(Evidence("code:agent-sdk/subagents", "intermediate tool calls and results stay inside the subagent; only its final message returns to the parent."),),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="28,000 tokens return per subagent although each read 200,000",
        trap="merged contexts, run order, or reading filings in the coordinator",
    ),
    # ---- K4: crash recovery state ----
    MCQ(
        id="Q5.4-10",
        q=("A research run with a coordinator and six subagents crashed at about 70% completion when a host restarted. On restart the "
           "coordinator spawned all six again, and the run repeated about two hours of work. Which design best avoids this next time?"),
        opts=("Each subagent exports state to a known path; the coordinator reloads a manifest on resume.",
              "Ask the coordinator to remember which subagents finished, and trust that memory after the restart.",
              "Raise the host's timeout so that long runs are less likely to be interrupted by a restart.",
              "Save only the final report, since the earlier steps can be regenerated from it later."),
        ans=0,
        explain=("State exported to known locations and indexed by a manifest survives the process, so the coordinator can skip finished "
                 "work. B relies on memory that died with the process. C reduces how often crashes occur, but does not help once one "
                 "happens. D keeps nothing until the end, so a mid-run crash has nothing to restore."),
        scenarios=(3,), points=("5.4:K4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the guide names exporting state to a known location and loading a manifest on resume; no official page describes this pattern.",
        qtype="choose", level="medium", principle="preserve_information",
        situation="six-subagent research run repeats two hours of work after a host restart",
        trap="memory in the coordinator, longer timeouts, or final report only",
    ),
    MCQ(
        id="Q5.4-11",
        q=("A coordinator resumes an extraction run from `manifest.json`, which lists all 12 chunks as `done`. The merged output is "
           "missing the results of 3 chunks. The file's modification time is 10 minutes before the crash, yet all 12 `done` entries "
           "were added within the first second of the run. What is the most likely root cause?"),
        opts=("The subagents wrote output that was too large for the coordinator to merge into one file.",
              "The manifest was updated before each chunk's state was exported, so `done` meant nothing.",
              "The coordinator should have reloaded its own conversation instead of reading a manifest file.",
              "A larger context window was needed to hold all twelve chunk results at once during merging."),
        ans=1,
        explain=("Entries written in the first second cannot reflect finished work; a manifest should change only after the matching "
                 "state export is safely written. A has no support in the log. C offers an unrelated mechanism that would not know "
                 "about chunk files. D treats a bookkeeping error as a capacity problem."),
        scenarios=(6,), points=("5.4:K4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: manifest ordering is a design judgment from the guide's crash-recovery bullet.",
        qtype="diagnose", level="hard", principle="root_cause",
        situation="manifest lists 12 chunks done within one second, 3 results missing",
        trap="blame output size, conversation reload or window size",
    ),
    MCQ(
        id="Q5.4-12",
        q=("A team designs what each research agent should export so that a replacement agent can continue after a crash. Which "
           "export is best?"),
        opts=("The agent's complete transcript, which a replacement can read through from the start.",
              "A structured list of finished items with their findings and sources, but no list of pending ones.",
              "Structured entries of finished items, with sources, and the identifiers still pending.",
              "The agent's own estimate of how complete the work is, shown as a percentage of the total."),
        ans=2,
        explain=("Structured state lets a replacement skip finished items, reuse findings with their sources and pick up the pending ones. "
                 "A brings back the bulk and the noise. B records what is done but gives a replacement no way to know what remains. D is a self-report that "
                 "says nothing about which items remain."),
        scenarios=(3,), points=("5.4:K4",),
        evidence=(_STRUCT,),
        qtype="evaluate", level="medium", principle="preserve_information",
        situation="choosing the contents of a per-agent state export for a research run",
        trap="transcript, prose recap or self-reported completion",
    ),
    # ---- S1: spawn subagents for specific questions ----
    MCQ(
        id="Q5.4-13",
        q=("A developer has the main agent trace refund flow dependencies in an 80-file service. Tracing in the main conversation has "
           "already consumed 40% of the context, and three more questions about the same service are queued. How should the next "
           "question be delegated?"),
        opts=("Spawn a subagent told to explore the service and report anything that seems relevant to it.",
              "Spawn one subagent per file, so that each of the 80 files is read separately in isolation.",
              "Finish tracing in the main conversation first, then spawn a subagent to summarise what it found.",
              "Spawn a subagent with the exact question and the answer shape wanted, e.g. callers per module."),
        ans=3,
        explain=("A subagent starts without the conversation or the files already read, so it needs a precise question and an answer shape. "
                 "A is vague and invites a sprawling report. B creates 80 contexts and loses the connections between files. "
                 "C summarises after the verbose reading has already filled the main context."),
        scenarios=(2,), points=("5.4:S1",),
        evidence=(_FRESH,),
        community="Evidence supports only the premise that subagents start fresh; which answer is best is guide judgment.",
        qtype="fix", level="medium", principle="explicit",
        situation="refund-flow tracing at 40% context with three more questions queued",
        trap="vague exploration, one subagent per file, or delegate after the reading",
    ),
    MCQ(
        id="Q5.4-14",
        q=("A coordinator asks a subagent to \"find all test files\" in a large repository. The subagent returns 2,100 paths, about 18,000 "
           "tokens, and the coordinator's context jumps. The coordinator only needs to know which directories hold tests and how many "
           "files each framework has. What is the best change?"),
        opts=("Ask for counts grouped by directory and framework, with the full path list saved to a file.",
              "Ask the subagent to return only the first 100 paths it finds, and ignore the remaining ones.",
              "Do the search in the main conversation and pipe the output through `head` to cut it short.",
              "Spawn a second subagent to condense the first subagent's list before it reaches the coordinator."),
        ans=0,
        explain=("The request should shape the answer to what the coordinator will use, and the full list stays available on disk. B returns "
                 "an arbitrary slice that may miss whole directories. C puts the search back in the main context. D adds a second "
                 "agent to fix a problem that a better request avoids."),
        scenarios=(2,), points=("5.4:S1",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: shaping a subagent request to the answer the coordinator needs is guide judgment.",
        qtype="fix", level="easy", principle="proportionate",
        situation="'find all test files' returns 2,100 paths when only counts per framework are needed",
        trap="truncate the list, search in main, or chain a second subagent",
    ),
    MCQ(
        id="Q5.4-15",
        q=("A developer wants a subagent to help understand an invoice extraction pipeline in which totals sometimes differ by a cent "
           "between ingest and export. Which delegation request is best?"),
        opts=("Review the whole extraction package, read every module in it, and report anything that looks wrong or surprising.",
              "Trace where `invoice_total` is rounded between ingest and export; return file and line for each step.",
              "Build a deep understanding of the pipeline so that you can answer later questions about it.",
              "Read every module under `extract/` and return their contents with your comments added."),
        ans=1,
        explain=("A specific question with a defined return gives a short answer the main agent can use. A is open-ended and returns a "
                 "broad report. C asks for understanding that stays in the subagent, because it does not carry over to later questions. "
                 "D copies the verbose material back into the main context."),
        scenarios=(6,), points=("5.4:S1",),
        evidence=(_FRESH,),
        community="Evidence supports only the premise that subagents start fresh; which answer is best is guide judgment.",
        qtype="evaluate", level="easy", principle="explicit",
        situation="cent differences in invoice totals between ingest and export",
        trap="open-ended review, 'understand it', or return all contents",
    ),
    # ---- S2: scratchpad discipline ----
    MCQ(
        id="Q5.4-16",
        q=("A team wants its codebase-exploration agent to counter context degradation. Which instruction, added to the task prompt, "
           "best sets up the behaviour?"),
        opts=("Every 20 turns, write a summary of everything you know into the chat so that it stays visible to you.",
              "Keep what you learn in mind throughout, and tell me if you feel unsure about any earlier detail.",
              "Append each finding to `.scratch/findings.md` as path, symbol, fact; read it before new questions.",
              "Write all findings to a single notes file once the whole exploration is finished, then read it."),
        ans=2,
        explain=("Writing as findings appear and reading before each new question puts verified specifics back in front of the model. A "
                 "keeps the summaries inside the conversation that degrades. B relies on the model's recall, which is the thing "
                 "that fails. D writes too late: earlier findings may already be lost."),
        scenarios=(2,), points=("5.4:S2",),
        evidence=(_STRUCT,),
        qtype="configure", level="medium", principle="explicit",
        situation="instruction that makes an exploration agent keep and use a scratchpad",
        trap="summaries in chat, rely on recall, or write once at the end",
    ),
    MCQ(
        id="Q5.4-17",
        q=("A research agent's scratchpad has grown to 4,000 lines over a week of work. Reading it in full at the start of each question "
           "now uses about 25,000 tokens, and answers have started to blur again. What is the best change?"),
        opts=("Keep a one-line index plus per-topic files, and read the index and only the topics needed.",
              "Stop re-reading the scratchpad and rely on the agent's memory of what it contains instead.",
              "Have a larger model rewrite the scratchpad into a shorter summary at the end of each night.",
              "Delete entries once the file passes 4,000 lines, starting from the oldest, to keep it short."),
        ans=0,
        explain=("An index lets the agent find relevant entries while detail stays out of context until needed. B abandons the mechanism "
                 "that counters degradation. C risks summaries that lose specifics, and the model size does not matter. D discards "
                 "findings by age instead of relevance."),
        scenarios=(3,), points=("5.4:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: scratchpad structure for a long-lived research agent is a design judgment from the guide, not described in the docs.",
        qtype="fix", level="hard", principle="proportionate",
        situation="4,000-line scratchpad costs 25,000 tokens per question",
        trap="drop the file, summarise with a bigger model, or delete by age",
    ),
    MCQ(
        id="Q5.4-18",
        q=("An exploration session is auto-compacted at turn 90. The agent keeps a scratchpad, last updated at the end of the previous "
           "phase. Afterwards it re-reads the scratchpad but still cannot name about 40 call sites that it found earlier in the current phase, though it recalls "
           "everything from before. What is the most likely root cause?"),
        opts=("Compaction deletes files that were written less than an hour before it ran, as a safety measure.",
              "The scratchpad format could not hold call sites, so the agent skipped recording them as it worked.",
              "Compaction summarises only the most recent turns and keeps the older turns word for word in the context.",
              "Findings were written only at phase end, so the current phase's findings lived in the conversation."),
        ans=3,
        explain=("What was only in the conversation was compressed; what was on disk is still intact, which matches the pattern. A has "
                 "no basis, since compaction does not touch files. B does not fit an agent that recalls everything that was recorded. C "
                 "has it backwards: compaction summarises older conversation."),
        scenarios=(2,), points=("5.4:S2",),
        evidence=(Evidence("code:agent-sdk/sessions", "Sessions persist the conversation, not the filesystem."), Evidence("code:how-claude-code-works", "The summary keeps your requests and key code snippets, but detailed instructions from early in the conversation may be lost.")),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="40 current-phase call sites lost after compaction though earlier phases survived",
        trap="blame compaction deleting files or the notes format",
    ),
    # ---- S3: phase summaries injected ----
    MCQ(
        id="Q5.4-19",
        q=("A research coordinator finishes phase one, which found 30 candidate sources, and now spawns eight subagents to read the "
           "chosen sources in depth. How should it start the phase-two subagents?"),
        opts=("Tell them to continue from phase one, since the earlier work is part of the shared context here.",
              "Put a short phase-one summary (ranked sources, reasons, exclusions, open questions) in each prompt.",
              "Give each subagent the raw phase-one transcript so that it has absolutely everything to work from.",
              "Let each subagent rediscover the sources itself, to avoid carrying forward any earlier mistakes made."),
        ans=1,
        explain=("A new subagent has only its prompt, so a compact summary of what phase one decided must be put there. A assumes an "
                 "inheritance that does not exist. C brings back the full bulk the phase split was meant to avoid. D repeats "
                 "phase one eight times."),
        scenarios=(3,), points=("5.4:S3",),
        evidence=(_FRESH,),
        community="Evidence supports only the premise that subagents start fresh; which answer is best is guide judgment.",
        qtype="choose", level="medium", principle="explicit",
        situation="eight deep-read subagents start after a 30-source discovery phase",
        trap="assume inheritance, send the raw transcript, or rediscover",
    ),
    MCQ(
        id="Q5.4-20",
        q=("A code-audit coordinator injects a complete 600-word phase-one summary listing the 40 modules flagged as risky. Phase-two reviewers flag 14 "
           "further modules that phase one examined and rejected, and about a third of the reviewers' time goes to them. What is the "
           "most likely root cause?"),
        opts=("Phase-two subagents inherited an outdated copy of the phase-one conversation from the coordinator.",
              "The summary was cut off by a prompt length limit, so the rejections at its end never arrived.",
              "The summary recorded what was found but not what was ruled out, so reviewers re-derived it.",
              "The reviewers were given too much context, which made them check more modules than needed."),
        ans=2,
        explain=("A summary that lists the 40 flagged modules but not the rejected ones gives the next phase no reason to skip them. A is wrong because new "
                 "subagents inherit nothing. B invents a truncation; the summary reached the prompts and simply lacked the rejections. D mistakes the cause: the context given was "
                 "incomplete, not excessive."),
        scenarios=(2,), points=("5.4:S3",),
        evidence=(_FRESH,),
        community="Evidence supports only the premise that subagents start fresh; which answer is best is guide judgment.",
        qtype="diagnose", level="hard", principle="preserve_information",
        situation="14 modules rejected in phase one are flagged again in phase two",
        trap="blame inheritance, injection limits or too much context",
    ),
    MCQ(
        id="Q5.4-21",
        q=("A coordinator is about to launch eight phase-two subagents. One engineer proposes injecting the full 25,000-token phase-one "
           "transcript into each \"so nothing is lost\"; another proposes a 1,500-token summary. How should you evaluate the proposals?"),
        opts=("Use the summary of decisions and evidence, with a pointer to the files that hold the detail.",
              "Use the full transcript, because any summary will drop something that a subagent turns out to need.",
              "Use neither, so the subagents work independently and avoid anchoring on what phase one decided.",
              "Use a summary with conclusions only, because sources would use up context for no real gain."),
        ans=0,
        explain=("A summary that carries decisions and evidence, plus pointers to detail, gives each subagent what it needs and spends little "
                 "of its context. B puts the noise and 200,000 tokens of repeated bulk into the eight prompts. C wastes the phase-one work "
                 "without any reason to need independence. D leaves out the evidence the next phase must check."),
        scenarios=(3,), points=("5.4:S3",),
        evidence=(_FRESH,),
        community="Evidence supports only the premise that subagents start fresh; which answer is best is guide judgment.",
        qtype="evaluate", level="hard", principle="proportionate",
        situation="25,000-token transcript versus 1,500-token summary for eight subagents",
        trap="full transcript, no injection, or conclusions without sources",
    ),
    # ---- S4: manifests injected into prompts ----
    MCQ(
        id="Q5.4-22",
        q=("After a crash, a coordinator reloads its manifest, which lists three agents as `done` and two as `incomplete` with the paths "
           "of their state files. How should it resume?"),
        opts=("Respawn all five agents, and tell them that some of their work may already have been done today.",
              "Ask the model to infer from the earlier final report which of the agents had finished.",
              "Reload only the last report written, and respawn those agents that the report did not mention.",
              "Skip the three done agents; respawn the two with their state file contents in the prompts."),
        ans=3,
        explain=("The manifest says what to skip, and the exported state gives the respawned agents their starting point. A repeats finished work "
                 "and leaves the agents to guess. B replaces recorded status with inference. C depends on a report that a crash "
                 "may have prevented from being written."),
        scenarios=(3,), points=("5.4:S4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: injecting manifest state into agent prompts on resume is a design pattern from the guide, not an official docs page.",
        qtype="configure", level="easy", principle="deterministic",
        situation="manifest shows three agents done and two incomplete with state paths",
        trap="respawn everything, infer status, or depend on a report",
    ),
    MCQ(
        id="Q5.4-23",
        q=("A resumed extraction run repeats 140 documents that were already processed. The coordinator's log shows it parsed a "
           "manifest with 140 `done` entries, then spawned six extractor agents with the prompt \"process batch 3 of 5\". What is "
           "the most likely root cause?"),
        opts=("The manifest was too long to be parsed, so the coordinator ignored it when it spawned them.",
              "The coordinator read the manifest but did not put its contents into the extractors' prompts.",
              "Extractors always restart from the first document of a batch after a crash has occurred.",
              "The extractors' context was already full, which made them drop the earlier documents of a batch."),
        ans=1,
        explain=("Fresh agents know only their prompt, so a manifest the coordinator read but did not pass on cannot change what they "
                 "do. A contradicts the log, which shows it was parsed. C describes behaviour nothing in the setup mandates. "
                 "D cannot apply to newly spawned agents with empty contexts."),
        scenarios=(6,), points=("5.4:S4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the coordinator's duty to inject manifest state into agent prompts comes from the guide's crash-recovery skill.",
        qtype="diagnose", level="medium", principle="explicit",
        situation="140 done documents reprocessed although the manifest was parsed",
        trap="blame manifest size, restart behaviour or full context",
    ),
    MCQ(
        id="Q5.4-24",
        q=("A refactoring run over 30 modules crashed while one agent was editing module 17. The manifest marks 1 to 16 `done` and 17 "
           "`in_progress`, and module 17's files on disk are partly changed. What is the best way to resume module 17?"),
        opts=("Treat module 17 as finished, since its files on disk already show some of the changes made.",
              "Run `git checkout .` and restart all 30 modules from the beginning, to be certain of the result.",
              "Mark it incomplete, inject its saved state, and tell the new agent to re-check the disk.",
              "Skip module 17 and continue, then ask the model whether anything was left undone afterwards."),
        ans=2,
        explain=("The saved state shows what was intended and the disk shows what happened, so the new agent must be told about both. "
                 "A assumes a half-edited module is complete. B discards sixteen finished modules. D leaves a possibly broken module "
                 "for the model to guess about."),
        scenarios=(2,), points=("5.4:S4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: applies the guide's skill of injecting exported state into agent prompts to an in-progress unit; the check-the-disk step is design judgment.",
        qtype="fix", level="hard", principle="preserve_information",
        situation="crash during edits of module 17 of 30",
        trap="assume it is finished, reset everything, or skip it",
    ),
    # ---- S5: /compact ----
    MCQ(
        id="Q5.4-25",
        q=("After three hours exploring authentication code, a developer's context is at 70%. The findings exist only in the conversation, and "
           "nothing has been written to disk. Next the agent will write a migration plan for the auth module. What is the best step before starting the plan?"),
        opts=("Run `/compact` with instructions to keep the auth module's paths, call sites and open questions.",
              "Run `/clear` so that the planning starts with an empty context and no leftover detail at all.",
              "Wait for auto-compaction, which keeps whatever the model finds most important at that moment.",
              "Run `/compact` with no instructions, so that the default summary covers the whole session evenly."),
        ans=0,
        explain=("A focused `/compact` lets you choose what the summary keeps, instead of what the automatic pass guesses. B is destructive here: "
                 "findings never written to disk would be erased. C leaves the choice to the model, and may happen at a bad moment. "
                 "D spreads the summary over everything, including the verbose output."),
        scenarios=(2,), points=("5.4:S5",),
        evidence=(Evidence("code:context-window", "The summary keeps what you choose instead of what the automatic pass guesses is important."),),
        qtype="choose", level="easy", principle="explicit",
        situation="70% context after auth exploration, findings only in the conversation",
        trap="clear, wait for auto, or compact without a focus",
    ),
    MCQ(
        id="Q5.4-26",
        q=("A repository has `.claude/rules/billing.md` with `paths:` frontmatter for `billing/**`, requiring amounts in cents. During a "
           "long session the agent follows it while editing billing files. After `/compact`, it edits a billing file that it had read "
           "before the compaction and writes decimal amounts, though the rule file is unchanged. What is the most likely root cause?"),
        opts=("`/compact` removes every rule file from the session, including the root-level ones loaded at start.",
              "The rule loaded into the conversation when billing files were read, so the summary absorbed it.",
              "The rule file is re-injected from disk after compaction, so the agent chose to ignore it.",
              "The rule is too long, so compaction cut it down to its first few lines when it re-injected."),
        ans=1,
        explain=("Path-scoped rules load into message history when a matching file is touched, so compaction summarises them with the rest. "
                 "A is wrong: unscoped rules and the root CLAUDE.md are re-injected. C is wrong because the docs say the rule is summarised away "
                 "with the rest of the history, not re-injected. D confuses this with the size cap on skill bodies. The docs' own fix: drop "
                 "`paths:` or move the rule to the root CLAUDE.md."),
        scenarios=(2,), points=("5.4:S5",),
        evidence=(Evidence("code:context-window", "Path-scoped rules and nested CLAUDE.md files load into message history when Claude reads, writes, or edits their trigger file, so compaction summarizes them away with everything else."),),
        basis="docs",
        qtype="diagnose", level="hard", principle="fit_for_purpose",
        situation="cents-only billing rule ignored after /compact",
        trap="assume compaction removes all rules or never reloads them",
    ),
    MCQ(
        id="Q5.4-27",
        q=("An agent must answer questions about one 4 MB generated schema file. Each read of the file fills the context, automatic "
           "compaction summarises it, and the next read fills the context again. After a few attempts Claude Code stops compacting and "
           "reports an error. What is the best fix?"),
        opts=("Run `/compact` by hand each time the error appears, and repeat until the read completes.",
              "Move to a model with a bigger window, hoping the entire file then fits in a single read.",
              "Run `/clear` and repeat the same full read in the fresh session, now that the context is empty.",
              "Have a subagent search the file, or read targeted ranges, and return only what is needed."),
        ans=3,
        explain=("The file is the problem, so keep it out of the main context and bring back only the relevant parts. A repeats the loop that "
                 "already failed. B moves the limit, but 4 MB of text remains a large read. C returns to the same full read that "
                 "fills the context again."),
        scenarios=(2,), points=("5.4:S5",),
        evidence=(Evidence("code:how-claude-code-works", "If a single file or tool output is so large that context refills immediately after each summary, Claude Code stops auto-compacting after a few attempts and shows an error instead of looping."),),
        basis="docs",
        qtype="fix", level="medium", principle="root_cause",
        situation="4 MB schema read refills the context after every compaction",
        trap="repeat compaction, bigger window, or clear and repeat the read",
    ),
)
