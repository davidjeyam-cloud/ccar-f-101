"""Exam bank · TS 1.7. Original questions; see docs/MCQ_BANK_PLAN.md."""
from utils.mcq_sets import MCQ, Evidence

TS = "1.7"
BULLETS = {
    "K1": "Named session resumption: --resume <session-name> continues one specific earlier conversation",
    "K2": "fork_session makes independent branches from a shared analysis baseline to try different approaches",
    "K3": "A resumed agent must be told about changes to files it analysed earlier",
    "K4": "A new session with a structured summary is more reliable than resuming with stale tool results",
    "S1": "Using --resume with session names to carry named investigations across work sessions",
    "S2": "Using fork_session for parallel exploration branches from one codebase analysis",
    "S3": "Choosing resumption when prior context is mostly valid, and a fresh start with an injected summary when tool results are stale",
    "S4": "Telling a resumed session about specific file changes so it re-analyses those, not everything",
}

_SDK = "code:agent-sdk/sessions"
_CLI = "code:sessions"
_HOW = "code:how-claude-code-works"
_RESTORED = "Conversation history: the messages, tool calls, and results."
_FULL = "Returning to a session means the agent has full context from before: files it already read, analysis it already performed, decisions it already made."

QUESTIONS = (
    # ---- K1: named resumption ----
    MCQ(
        id="Q1.7-01",
        q=("Your team's morning script runs `claude --continue` to bring each engineer back into a long migration investigation. "
           "On about 20% of mornings the agent knows nothing about the migration, yet it can describe a small lint fix from the "
           "evening before. The migration transcript is still on disk on those days. What is the most likely root cause?"),
        opts=("`--continue` loads only a compaction summary on those days, so the detailed findings are left out.",
              "`--continue` selects by recency, so whatever ran last in the directory is what gets reopened.",
              "`--continue` restores the messages but not the tool results, so the agent has lost what it read.",
              "`--continue` stops matching once a newer session exists, so it has opened a blank session instead."),
        ans=1,
        explain=("The flag reopens the most recent session in the directory, and the agent's knowledge of last night's lint fix shows "
                 "that it is in that session; resuming by name would select the migration instead. A does not explain why a "
                 "different task's details are present. C is false, because a resumed session restores tool calls and results. D "
                 "is ruled out because the session is not blank: it knows about the lint fix."),
        scenarios=(4,), points=("1.7:K1", "1.7:S1"),
        evidence=(Evidence(_CLI, "Reopens the most recent session in the current directory"),
                  Evidence(_CLI, "Resumes the named session directly"),),
        qtype="diagnose", level="easy", principle="root_cause",
        situation="morning script lands engineers in last night's lint-fix session on 20% of days",
        trap="believe the resume dropped the findings",
    ),
    MCQ(
        id="Q1.7-02",
        q=("Each evening an engineer runs `/export` on a session named `etl-migration`, and each morning pastes the text into a new "
           "session as its first prompt. She also runs other sessions in this repository during the day, and the code under "
           "study has not changed all week. The new session cannot quote the exact output of earlier test runs and spends about 30 "
           "minutes re-reading files already covered. Which approach is best?"),
        opts=("Seed the new session with a structured summary in place of the export, as fresh starts are more reliable.",
              "Save the export as a scratchpad file, and have each new session read that file before it does anything.",
              "Run `claude --continue` each morning, as that brings back the latest conversation with its full history.",
              "Reopen the original with `--resume`, as everything it read and concluded still holds."),
        ans=3,
        explain=("Nothing is stale, so the real conversation, with its tool results, is worth keeping, and resuming it by name "
                 "restores all of it. A applies the advice for stale context to context that is valid, and throws detail away. B "
                 "keeps a flattened copy of the transcript in place of the real history. C reopens whichever session ran last, which "
                 "may be one of her other sessions."),
        scenarios=(4,), points=("1.7:K1", "1.7:S3"),
        evidence=(Evidence(_CLI, _RESTORED),),
        qtype="choose", level="medium", principle="fit_for_purpose",
        situation="engineer pastes an /export of yesterday's session into a new session every morning",
        trap="replace the paste with a summary although nothing is stale",
    ),
    MCQ(
        id="Q1.7-03",
        q=("A platform engineer has 14 Claude Code sessions from two weeks of work on four incidents. The picker shows several rows "
           "titled \"Investigate failing job\", and finding the right one takes about ten minutes and two wrong attempts each day. "
           "Which change most directly fixes this?"),
        opts=("Set a name per incident with `-n` or `/rename`, and reopen it with `--resume <name>`.",
              "Move all four incidents into one long session, so that only one row ever needs to be found.",
              "Start each incident in its own subdirectory, and reopen with `--continue` from that directory.",
              "Script a keyword search over the raw `.jsonl` transcripts, and print the session IDs that match."),
        ans=0,
        explain=("Descriptive names make a session findable and resumable directly. B mixes four incidents in one context, so each "
                 "investigation competes with the others. C still depends on recency, and an incident can have more than one "
                 "session. D builds on a transcript format the docs call internal, when a name solves the problem."),
        scenarios=(4,), points=("1.7:K1",),
        evidence=(Evidence(_CLI, "Give sessions descriptive names so they're findable in the session picker and resumable by name."),),
        qtype="fix", level="easy", principle="proportionate",
        situation="14 sessions on four incidents with look-alike titles in the picker",
        trap="merge the incidents into one long session",
    ),
    # ---- K2: fork from a baseline ----
    MCQ(
        id="Q1.7-04",
        q=("To compare event sourcing with a simple status table, a team runs a 50-minute study of the order module in each of two "
           "sessions, then explores one design in each. One study flagged 5 hot spots and the other flagged 8, so reviewers cannot "
           "tell whether the designs or the studies explain the differences in outcome. What is the most effective change?"),
        opts=("Give both runs one fixed checklist of what to examine, so that their lists of findings line up.",
              "Merge both lists into one notes file, and restart the two design sessions from that shared file.",
              "Do the reading once and branch it with `fork_session`, so both start from identical context.",
              "Run the study once, then explore both designs in that same session, one straight after the other."),
        ans=2,
        explain=("Forks start from a copy of the same history, so each design begins from an identical baseline and the comparison is "
                 "fair, and the study is paid for once. A narrows two separate runs and still gives two different baselines. B pays "
                 "for both studies, redoes the designs, and swaps the full context for notes. D has one baseline, but the first "
                 "design then colours the second."),
        scenarios=(4,), points=("1.7:K2", "1.7:S2"),
        evidence=(Evidence(_SDK, "Forking creates a new session that starts with a copy of the original's history but diverges from that point."),),
        qtype="fix", level="medium", principle="fit_for_purpose",
        situation="a 50-minute study is run twice per design and finds 5 versus 8 hot spots",
        trap="give both runs a fixed checklist so that they match",
    ),
    MCQ(
        id="Q1.7-05",
        q=("A research session reads 45 sources, drafts a regulation-led recommendation, then is asked for a market-led one and told to "
           "treat it as separate work. Reviewers find that 6 of 9 sections of the second draft argue against the first instead of "
           "making their own case. Where the second draft does quote a source, the quote is accurate. What is the most likely "
           "root cause?"),
        opts=("Both drafts came from one history, so the second was reasoned with the first in view.",
              "The instruction was too weak, and firmer wording would have put the first draft out of consideration.",
              "The 45 sources had dropped out of context by then, so only the first draft was left to work from.",
              "The model was too small for the job, and a stronger one would keep the two arguments separate."),
        ans=0,
        explain=("Everything in a session stays in what the model reasons from, so the first draft shaped the second; a fork taken "
                 "after the reading would have avoided that. B asks an instruction to remove what the history still holds. C is "
                 "ruled out by the accurate quotes, which show the sources were still available. D changes the model and leaves "
                 "the first draft in its context."),
        scenarios=(3,), points=("1.7:K2",),
        evidence=(Evidence(_SDK, "It contains your prompt, every tool call the agent made, every tool result, and every response."),
                  Evidence(_SDK, "You end up with two independent sessions you can resume separately."),),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="market-led draft written after a regulation-led draft argues against it",
        trap="use firmer wording to make the model set the first draft aside",
    ),
    MCQ(
        id="Q1.7-06",
        q=("After a shared analysis, an engineer forks the session twice and starts both forks in one checkout: one moves the cache to "
           "Redis, the other removes the cache. Each fork's history shows no sign of the other. Yet the removal fork's test run fails "
           "on a `redis_client.py` it never created, and the Redis fork's edits to `cache.py` are gone. What is the root cause?"),
        opts=("Each fork keeps a private snapshot of the files, and the snapshots were merged when the tests began.",
              "Both forks kept their parent's session ID, so their tool calls were written into a single transcript.",
              "File checkpointing restored the baseline as the second fork started, and that undid the earlier edits.",
              "Forking separates conversations only, so both agents were changing the same working files."),
        ans=3,
        explain=("A fork copies history, not the filesystem, so one fork's edits are real and visible to the other; separate worktrees "
                 "give each branch its own checkout. A invents a per-fork snapshot that does not exist. B is false, because a fork "
                 "gets its own session ID, and the histories are separate. C does not fit: nobody ran a rewind, and the "
                 "`redis_client.py` from the other fork is still on disk."),
        scenarios=(4,), points=("1.7:K2", "1.7:S2"),
        evidence=(Evidence(_SDK, "Forking branches the conversation history, not the filesystem."),
                  Evidence(_SDK, "If a forked agent edits files, those changes are real and visible to any session working in the same directory."),
                  Evidence("code:best-practices", "When you have separate pieces of work going at once, give each its own checkout so the edits can't collide."),),
        basis="docs",
        community="The guide says only that forks are independent branches. That independence covers the conversation; the filesystem detail is from the docs.",
        qtype="diagnose", level="hard", principle="root_cause",
        situation="two forks in one checkout overwrite each other's cache changes",
        trap="assume forks also isolate the files on disk",
    ),
    # ---- K3: tell the agent what changed ----
    MCQ(
        id="Q1.7-07",
        q=("Picked up again on Thursday, a named investigation files a ticket claiming `retry.py` lacks backoff. `git log` shows a "
           "teammate's backoff commit merged on Wednesday, and the current file has it. Tuesday is the last time that session "
           "read `retry.py`, and no file-changed note appears in the log. What most likely explains the wrong ticket?"),
        opts=("The resume dropped Tuesday's tool results, so the agent guessed the contents from the file's name.",
              "The agent read the file correctly and overlooked the backoff code, which a stronger model would catch.",
              "Its Tuesday result is still in context, and nothing prompted it to look at that code again.",
              "A resume puts the files back as they were on Tuesday, so its working copy lacks the commit."),
        ans=2,
        explain=("A resumed session brings back its earlier tool results, so an old read stands until something leads the agent to "
                 "repeat it. A is backwards: the results were restored, and that is the source of the claim. B does not fit, since "
                 "the only read happened before the commit existed. D is false, because sessions hold the conversation and do "
                 "not touch the files on disk."),
        scenarios=(4,), points=("1.7:K3",),
        evidence=(Evidence(_SDK, _FULL),
                  Evidence(_SDK, "Sessions persist the **conversation**, not the filesystem."),),
        qtype="diagnose", level="easy", principle="root_cause",
        situation="resumed session files a ticket about missing backoff in retry.py",
        trap="think a resume rolls the files back",
    ),
    MCQ(
        id="Q1.7-08",
        q=("A research session analysed 40 reports in a shared folder and was left overnight. By morning 3 reports had been reissued "
           "with corrected revenue figures, and the other 37 were untouched. Resumed the next day, it produces a draft that "
           "still shows the old revenue for those companies. What is the most effective fix?"),
        opts=("Resume it with an instruction to refresh every figure in the draft from the folder before continuing.",
              "Point it at the reissued files by name, and have it redo only the figures drawn from them.",
              "Seed a fresh session with a structured summary, and have it read the reissued reports from there.",
              "Add a verification subagent that compares every number in the draft against the whole folder."),
        ans=1,
        explain=("Only 3 of 40 inputs changed, so the context is mostly valid and naming those files is the smallest fix that corrects "
                 "the draft. A re-reads 37 reports that are fine. C drops a session that is mostly valid, which is the remedy for "
                 "context that is mostly stale. D adds a component and repeats the same work on all 40."),
        scenarios=(3,), points=("1.7:K3", "1.7:S4"),
        evidence=(Evidence(_SDK, _FULL),),
        community="The targeted fix is the guide's position; the docs quote supports only that earlier reads are carried in the session.",
        qtype="fix", level="medium", principle="proportionate",
        situation="3 of 40 reports reissued overnight with corrected figures",
        trap="restart with a summary when only a few inputs changed",
    ),
    MCQ(
        id="Q1.7-09",
        q=("Before resuming sessions after a merge, an engineer skips any note about what changed, arguing that \"the agent will read "
           "the file again when it needs to.\" Last week, in two of his resumed sessions, the agent gave advice about changed "
           "files, and neither session log shows a new read of them. How should you evaluate his position?"),
        opts=("He is right for existing files, as the re-read is automatic, so only brand-new files need a note.",
              "He is right if he runs `/compact` after each resume, which clears the older reads from the context.",
              "He is wrong: a merge makes earlier context unreliable, so start a new session after every merge.",
              "He is wrong: name the changed files on resume so that the agent re-analyses them."),
        ans=3,
        explain=("Earlier tool results come back with the session, and his own logs show the agent answering from them without "
                 "re-reading, so a sentence naming the files is cheap protection. A is contradicted by those logs, "
                 "which show no re-read of changed files. B only condenses the outdated content. C overcorrects, since a small merge "
                 "leaves most of the context valid."),
        scenarios=(4,), points=("1.7:K3",),
        evidence=(Evidence(_CLI, _RESTORED),),
        community=("Docs note: Claude Code can add a note that a file read earlier changed on disk (agent-sdk/modifying-system-prompts), "
                   "but they do not say this covers a resume. The question rests on the logs in the stem and the guide's bullet."),
        qtype="evaluate", level="medium", principle="explicit",
        situation="engineer argues no change note is needed because the agent re-reads on demand",
        trap="trust the agent to re-read without being told",
    ),
    # ---- K4: fresh start with a structured summary ----
    MCQ(
        id="Q1.7-10",
        q=("A customer returns to a support case after 9 days. Every order, refund and account record in the saved session has since "
           "changed. In resumed test runs the agent quotes the old refund status in about a third of replies. What is the best "
           "way to handle such returns?"),
        opts=("Open a new session seeded with the durable case facts, and fetch live records through tools.",
              "Resume, and force a `lookup_order` as the first step, so that newer results follow the older ones.",
              "Resume, and tell the agent which fields changed, so it re-reads those fields and nothing else.",
              "Resume, and run `/compact` first, so that the stale records are condensed before the agent continues."),
        ans=0,
        explain=("When nearly all tool results are stale, a new session with the durable facts of the case is more reliable than "
                 "resuming, because the old results no longer compete with the live ones. B leaves the old records in context, "
                 "where they can still outweigh the new result. C suits a few changes, but here every record moved. D "
                 "condenses the stale records without correcting them."),
        scenarios=(1,), points=("1.7:K4", "1.7:S3"),
        evidence=(Evidence(_CLI, _RESTORED),
                  Evidence(_SDK, "Capture the results you need (analysis output, decisions, file diffs) as application state and pass them into a fresh session's prompt."),),
        qtype="choose", level="hard", principle="fit_for_purpose",
        situation="customer returns after 9 days and resumed runs quote the old refund status",
        trap="force a new lookup so that fresh results follow the stale ones",
    ),
    MCQ(
        id="Q1.7-11",
        q=("After a framework upgrade rewrites most of a service, an engineer asks the old session to \"recap everything you know\" and "
           "seeds a new session with that recap as JSON. The new session cites two controllers that no longer exist and treats a "
           "deleted queue as current, without checking either. Starting a new session was the right call. What went wrong?"),
        opts=("The recap should have been shortened with `/compact` first, so that only key points carried across.",
              "The recap should have used a stricter JSON schema, because a tighter format would stop such errors.",
              "The recap was unfiltered, so outdated claims crossed over looking the same as verified ones.",
              "The recap should have gone in the system prompt, where the model would have checked it more closely."),
        ans=2,
        explain=("A summary helps only if it separates what still holds from what must be re-checked; an unfiltered recap from a stale "
                 "session carries the staleness along as settled fact. A condenses the same claims, and condensing does not "
                 "correct them. B improves the shape, not the truth, and a schema-valid claim can still be outdated. D moves the "
                 "same claims to a different place, and they still read as fact."),
        scenarios=(4,), points=("1.7:K4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the guide calls for a structured summary; no official page says how to separate verified claims from unverified ones.",
        qtype="diagnose", level="hard", principle="independent_check",
        situation="unfiltered recap from a stale session seeds removed controllers into the new session",
        trap="treat a tighter JSON schema as the fix for stale claims",
    ),
    MCQ(
        id="Q1.7-12",
        q=("A market research session ran for days, three weeks ago, and nearly all its `web_search` results are from before a large data "
           "refresh. Resumed with new searches, it reports two different market sizes, each with a citation, in 11 of 14 sections. "
           "The scope and method notes from that session are still sound. What is the most reliable way forward?"),
        opts=("Resume it, run `/compact` so that the old results are condensed, and then repeat the searches.",
              "Begin a new session seeded with the sound scope and method, and repeat the searches there.",
              "Resume it, with an instruction to prefer the most recently retrieved figure in any conflict.",
              "Resume it, and add a subagent that resolves each conflict by choosing the figure with a later date."),
        ans=1,
        explain=("With most tool results stale, the old and new figures compete in one context, so a new session carrying only what "
                 "still holds is more reliable. A condenses the outdated figures into the summary without correcting them. C asks a "
                 "prompt to win against 11 sections of old evidence. D adds a component to manage a conflict that a clean "
                 "session would not have."),
        scenarios=(3,), points=("1.7:K4", "1.7:S3"),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the guide compares a structured summary with resuming on stale results; no official page makes this comparison.",
        qtype="choose", level="medium", principle="fit_for_purpose",
        situation="three-week-old research session gives two market sizes after a data refresh",
        trap="add a subagent that resolves old-versus-new conflicts",
    ),
    # ---- S1: --resume with names ----
    MCQ(
        id="Q1.7-13",
        q=("You are starting a billing audit that will take several days, with other Claude Code work in the same repository in "
           "between. You want to return to exactly this conversation each day by a label you choose. Which pair of commands "
           "does this?"),
        opts=("Start with `claude --session-id billing-audit`, then return with `claude --resume billing-audit`.",
              "Start with `claude -n billing-audit`, then return with `claude --continue billing-audit`.",
              "Start with `claude -n billing-audit`, then return with plain `claude --continue`.",
              "Start with `claude -n billing-audit`, then return with `claude --resume billing-audit`."),
        ans=3,
        explain=("`-n` sets the session's name and `--resume <name>` returns to it. A fails because `--session-id` needs a valid UUID, "
                 "not a label. B fails because `--continue` does not select a session by name. C reopens the most recent session, "
                 "which may be the other work."),
        scenarios=(4,), points=("1.7:S1", "1.7:K1"),
        evidence=(Evidence("code:cli-reference", "You can resume a named session with `claude --resume <name>`."),
                  Evidence("code:cli-reference", "Use a specific session ID for the conversation (must be a valid UUID)"),),
        qtype="configure", level="easy", principle="fit_for_purpose",
        situation="choosing the commands to start and reopen a multi-day billing audit by label",
        trap="use --session-id with a readable label",
    ),
    MCQ(
        id="Q1.7-14",
        q=("Two hours into an unnamed session tracing a memory leak, you learn you must drop it until Thursday and work on other "
           "tasks in this repository first. The findings are valuable and that code will not change. What should you do now?"),
        opts=("Run `/rename leak-trace`, then use `claude --resume leak-trace` on Thursday.",
              "Do nothing now, and run `claude --continue` on Thursday to come back to this work.",
              "Start a new named session on Thursday, and have it redo the trace from the beginning.",
              "Write the findings into CLAUDE.md, so that every Thursday session already knows them."),
        ans=0,
        explain=("A session can be named after it starts, and the name then works as a resume handle, with nothing lost. B reopens "
                 "the most recent session, which by Thursday will be one of the other tasks. C repeats two hours of work. D puts "
                 "one bug's notes into instructions loaded in every session, and still drops the evidence behind them."),
        scenarios=(4,), points=("1.7:S1",),
        evidence=(Evidence("code:best-practices", "And for work that spans several days, `/rename oauth-migration` in the session names it"),),
        qtype="fix", level="easy", principle="proportionate",
        situation="unnamed memory-leak session must be parked until Thursday",
        trap="rely on --continue after other work has happened",
    ),
    MCQ(
        id="Q1.7-15",
        q=("A nightly script runs `claude -p --continue` three times from one directory, to extend separate investigations on suppliers, "
           "pricing and logistics. After a week, the logistics report cites pricing sources, and all three reports share "
           "conclusions. the session store shows one session file updated all week. What is the most effective fix?"),
        opts=("Add a prompt line telling each run to stay on its own topic and ignore anything about the other two.",
              "Run `/compact` between the runs, so that each topic's details are condensed before the next one starts.",
              "Keep one session per topic, and pass that topic's stored ID to `--resume` on each run.",
              "Add `--fork-session` to each run, so that every run starts on a separate copy of the previous night."),
        ans=2,
        explain=("`--continue` means the most recent session, so all three runs appended to one conversation; each topic needs its own "
                 "session, selected explicitly. A leaves all three topics in one context. B condenses the mixture but keeps it "
                 "mixed. D gives each run a new ID, but every copy still starts from the mixed history."),
        scenarios=(3,), points=("1.7:S1", "1.7:K1"),
        evidence=(Evidence(_SDK, "Required when you have multiple sessions (for example, one per user in a multi-user app) or want to return to one that isn't the most recent."),
                  Evidence(_CLI, "You can still resume one by passing its session ID to `claude --resume <session-id>`."),),
        basis="docs",
        community="The guide speaks of session names; the docs say `-p` sessions are resumed by session ID, so the answer uses the ID.",
        qtype="diagnose", level="hard", principle="root_cause",
        situation="nightly -p --continue runs blend three investigations",
        trap="fork each night from the already mixed history",
    ),
    # ---- S2: fork_session in practice ----
    MCQ(
        id="Q1.7-16",
        q=("An Agent SDK service has analysed a codebase in a session whose ID it stored as `base_id`. It must now try a monorepo split "
           "and a module-boundary cleanup without either seeing the other, and keep `base_id` usable for later experiments. "
           "How should it configure each of the two runs?"),
        opts=("`continue_conversation=True` on each run, so that both pick up the analysis.",
              "`resume=base_id, fork_session=True` on each run, so each gets a separate copy.",
              "`resume=base_id` on each run, so that both pick up the stored analysis session.",
              "`fork_session=True` alone on each run, so that each starts a brand new branch."),
        ans=1,
        explain=("`resume` names the session to branch from and `fork_session` makes the run a new session, leaving the original as it "
                 "was. A and C both add to an existing session, so the two experiments would pile into one history. D gives the "
                 "fork nothing to branch from, because a fork needs a session ID."),
        scenarios=(3,), points=("1.7:S2", "1.7:K2"),
        evidence=(Evidence("code:agent-sdk/python", "When resuming with `resume`, fork to a new session ID instead of continuing the original session"),
                  Evidence(_SDK, "Resume and fork require a session ID."),),
        qtype="configure", level="easy", principle="fit_for_purpose",
        situation="SDK service must branch two refactors from a stored base_id",
        trap="pass resume alone on both runs",
    ),
    MCQ(
        id="Q1.7-17",
        q=("To protect a shared analysis, an engineer copies its `.jsonl` transcript aside before each experiment, explores in the "
           "original session, then restores the copy by hand. Two restores this month used the wrong copy. The team wants to keep "
           "every experiment's conversation for review, and a third experiment is due. What should you recommend?"),
        opts=("Replace it with `fork_session`, giving each experiment a separate session off that baseline.",
              "Keep it but script it, since a script removes the human error behind the two bad restores.",
              "Replace it with `/rewind`, stepping back to the end of the shared work after each experiment.",
              "Keep it but commit the copies to git, so that every saved baseline is versioned beside the code."),
        ans=0,
        explain=("A fork gets its own session and leaves the original's history unchanged, so the copying solves a problem the product "
                 "has already solved, and each experiment's conversation is kept. B automates a workaround on a format the docs "
                 "call internal. C steps back past each experiment, so its conversation is not kept as a session of its own to review. "
                 "D still relies on hand restores and puts internal files under version control."),
        scenarios=(4,), points=("1.7:S2",),
        evidence=(Evidence(_SDK, "The fork gets its own session ID; the original's ID and history stay unchanged."),
                  Evidence(_CLI, "The entry format is internal to Claude Code and changes between versions, so scripts that parse these files directly can break on any release."),),
        qtype="evaluate", level="medium", principle="fit_for_purpose",
        situation="engineer hand-copies the transcript to protect a baseline before experiments",
        trap="automate a transcript backup instead of forking",
    ),
    MCQ(
        id="Q1.7-18",
        q=("After a 70-minute analysis of a payments module, an engineer wants to compare contract tests against end-to-end tests. In a "
           "trial, two fresh subagents spawned with the Task tool and a one-line brief each spent 20 minutes re-reading the module, "
           "and their plans covered only 3 of the 11 risks the analysis had listed. What is the most effective approach?"),
        opts=("Extend each brief to a one-paragraph recap, so that the subagents know the main conclusions.",
              "Give both subagents a higher-tier model, so that they rebuild the picture faster from the code.",
              "Explore the two kinds of test one after the other in the original session, and compare at the end.",
              "Fork that session once per kind of test, so each branch holds its whole history."),
        ans=3,
        explain=("Fresh subagents receive only their prompt, whereas a fork starts with a copy of the whole analysis and stays "
                 "independent of the other branch. A is better than a line but carries a fraction of what 70 minutes produced. "
                 "B pays again to rebuild what already exists. C keeps the findings but lets the first plan colour the second."),
        scenarios=(4,), points=("1.7:S2", "1.3:K4", "1.3:K2"),
        evidence=(Evidence(_SDK, "Fork is different: it creates a new session that starts with a copy of the original's history."),
                  Evidence(_HOW, "A subagent starts fresh unless it's a fork, which starts with a copy of your conversation so far."),),
        community="The guide's subagents do not inherit context; the docs add a fork subagent type, so the stem says the subagents are fresh.",
        qtype="choose", level="hard", principle="preserve_information",
        situation="fresh subagents with a one-line brief cover 3 of 11 known risks",
        trap="extend the subagent brief to a short recap",
    ),
    # ---- S3: resume or start fresh ----
    MCQ(
        id="Q1.7-19",
        q=("An analysis session covered 200 source files on Monday. By Wednesday the only changes in the repository are to a dependency "
           "lockfile and one CI config. You want to continue the work. What should you do?"),
        opts=("Fork the session and continue in the fork, so that the original is protected from those edits.",
              "Resume it and note those two paths, as nearly all of its earlier reads still hold.",
              "Resume it and ask it to read all 200 files again, so that its conclusions rest on current code.",
              "Open a new session with a structured summary, because that is more reliable than a resume."),
        ans=1,
        explain=("A summary beats a resume when tool results are stale, and here almost nothing is, so resuming keeps the context at "
                 "the cost of a short note. A copies the same context and adds a session without solving anything. C repeats "
                 "valid work. D applies the advice for stale context to valid context, and gives up detail for nothing."),
        scenarios=(4,), points=("1.7:S3",),
        evidence=(Evidence(_SDK, "The agent already analyzed something; now you want it to act on that analysis without re-reading files."),),
        qtype="choose", level="easy", principle="proportionate",
        situation="only a lockfile and one CI config changed after a 200-file analysis",
        trap="start fresh out of habit when the context is valid",
    ),
    MCQ(
        id="Q1.7-20",
        q=("After two bad incidents, your leads want one team rule for returning to Claude Code work. Your logs show the first incident "
           "followed a resume after a rewrite, and the second followed a restart that dropped a sound three-hour analysis. "
           "Sessions on this team are typically between one and ten days old. Which rule should you adopt?"),
        opts=("Resume by default, and restart with a summary only once a session is more than a week old.",
              "Restart with a summary by default, and resume only when the same engineer returns within a day.",
              "Decide per session, from how many of its earlier reads a diff shows to be out of date.",
              "Decide per session, from a confidence rating that the session gives for its own findings."),
        ans=2,
        explain=("The choice depends on how much of the prior context is still valid, and a diff shows that directly. A uses age, and "
                 "a rewrite can happen in a day. B also uses age and would repeat the second incident. D relies on self-reported "
                 "confidence from a session that cannot see what has changed."),
        scenarios=(4,), points=("1.7:S3", "1.7:K4"),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the guide states the resume-or-fresh criterion; no official page gives a rule for it.",
        qtype="evaluate", level="medium", principle="fit_for_purpose",
        situation="leads want one team rule for resuming after two opposite incidents",
        trap="use session age or self-reported confidence as the rule",
    ),
    MCQ(
        id="Q1.7-21",
        q=("You have three paused research sessions, each built on 80 source files. Session North has 2 files changed since it paused. "
           "Session South has 55 files replaced by a new data release. Session West has no changes, but paused three days ago. "
           "What should you do with each?"),
        opts=("Resume North with a note of its 2 files, resume West, and restart South from a summary.",
              "Resume North and West, and fork South so that its 55 changes stay apart from the old work.",
              "Resume all three, each with its list of changed files, so that no earlier analysis is thrown away.",
              "Resume West only, and restart the others, because any change leaves earlier tool results unreliable."),
        ans=0,
        explain=("Decide by how much of each session's context is still valid: nearly all for North, all for West, and little for "
                 "South. B copies South's stale results into the fork. C keeps 55 stale results competing with new reads in South. "
                 "D discards North, where only 2 of 80 files changed."),
        scenarios=(3,), points=("1.7:S3",),
        evidence=(Evidence(_SDK, _FULL),),
        community="The sorting rule is the guide's; the docs quote supports only that a resume brings the earlier reads back.",
        qtype="choose", level="medium", principle="fit_for_purpose",
        situation="triage of three paused sessions with 2, 55 and 0 changed files",
        trap="fork the stale session, or resume everything with change lists",
    ),
    # ---- S4: specific changes, targeted re-analysis ----
    MCQ(
        id="Q1.7-22",
        q=("A team resumes a 140-file analysis after each small merge with the prompt \"the code has changed, please re-check your "
           "findings\". Each resume re-reads nearly all 140 files and takes 25 minutes, though most merges touch 3 or 4 files. The "
           "findings do stay accurate. What is the most effective change?"),
        opts=("Have it re-check only the findings that it rates as low confidence, and leave all of the others as they are.",
              "Seed a fresh session with a structured summary after each merge, so that it reads only what it needs.",
              "Run `/compact` before the prompt, so that fewer of the earlier reads remain to be checked afterwards.",
              "Give it the paths from the diff, plus what moved, and scope the re-check to those."),
        ans=3,
        explain=("A vague prompt gives the agent no way to scope the work; naming the files enables targeted re-analysis. A relies on "
                 "self-reported confidence, which does not know what the merge touched. B throws away a session that is mostly valid "
                 "after each small merge. C loses detail and still gives the agent no idea of what changed."),
        scenarios=(4,), points=("1.7:S4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the guide states targeted re-analysis; no official page describes this resume practice.",
        qtype="fix", level="medium", principle="explicit",
        situation="vague re-check prompt makes each resume re-read 140 files",
        trap="restart after each small merge",
    ),
    MCQ(
        id="Q1.7-23",
        q=("A support team used one session to study 6 policy files and 30 past tickets, then draft escalation rules for its agent. "
           "Overnight, legal changed section 4 of `returns.md`, which feeds 3 of the 12 draft rules. You resume the session. "
           "Which first message is most effective?"),
        opts=("\"returns.md changed overnight. Re-read all the policy files, then review each of the 12 rules.\"",
              "\"Section 4 of returns.md changed. Re-read it and revise the rules that rest on it.\"",
              "\"Section 4 of returns.md changed overnight. Keep that in mind as you continue the draft.\"",
              "\"Section 4 of returns.md changed. Rate each rule, and re-check those you score below 80%.\""),
        ans=1,
        explain=("Naming the section and asking for a re-read of it points the session at what changed and keeps the rest. A re-reads "
                 "5 unchanged files and reviews 9 unaffected rules. C names the change, but it never asks for a re-read, so the old "
                 "text stays the basis. D relies on self-reported confidence in place of the rules' link to section 4."),
        scenarios=(1,), points=("1.7:S4", "1.7:K3"),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the guide states the practice of naming specific changes; no official page describes it.",
        qtype="fix", level="medium", principle="explicit",
        situation="one section of returns.md changes while escalation rules are being drafted",
        trap="ask the session to rate its confidence in each rule",
    ),
    MCQ(
        id="Q1.7-24",
        q=("You resume an analysis and tell it the 4 files that a merge modified, and it updates its findings on those 4. Its report "
           "still says retries are handled in `retry.py`. `git show` for that merge lists `retry.py` as deleted and "
           "`retry_policy.py` as new. What was the gap in your message?"),
        opts=("It should have asked for the whole analysis again, because any merge leaves a report unsafe.",
              "It left out what changed inside the 4 files, so that the updates to them were too shallow.",
              "It covered edits only, and a change note should list deleted, moved and added files too.",
              "It should have gone in CLAUDE.md, so that every later turn would keep the merge details in view."),
        ans=2,
        explain=("The session can re-analyse only what it knows about, and the deleted and moved file was missing from the note. "
                 "A overcorrects, since the other files are unaffected. B would improve the 4 updates, but the stale claim is not in "
                 "them. D changes where the note lives, and the note would still omit the deleted file."),
        scenarios=(4,), points=("1.7:S4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the guide says to name specific file changes; covering added files is the same idea applied.",
        qtype="diagnose", level="hard", principle="explicit",
        situation="change note lists 4 modified files but retry.py deleted and moved is left out",
        trap="assume the note failed for lack of detail on the listed files",
    ),
)
