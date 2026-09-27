"""
D4.2 Prompt Caching — an ℹ️ AWARENESS page (no lab, no playground).

Scope: guide v1.0 has no task statement for prompt caching. Its only mention is the Appendix's out-of-scope list:
implementation details are out of scope "beyond knowing it exists" (§17 Appendix · Out-of-Scope Topics · p.39; the list
starts on p.38). So this page teaches exactly that: that it exists, what it is for, and what it does NOT fix — the last
because a feature you only "know exists" is most likely to appear as a tempting wrong option. Built at the user's request
(2026-09-28: "i'd not skip this and add content which orients and prepares for exam").

Grounding: the official prompt-caching and batch-processing docs, fetched and read 2026-09-28. No implementation detail
(breakpoints, TTLs, minimum lengths, usage fields, invalidation rules, pricing) is taught — those are named once, as
"deliberately not on this page".
"""

from utils.concept_types import AwarenessContent, Claim, DocRef, Question

DOCS_VERIFIED_ON = "2026-09-28"
DOC_REFS = (
    DocRef("Prompt caching", "https://platform.claude.com/docs/en/build-with-claude/prompt-caching"),
    DocRef("Batch processing — Using prompt caching with Message Batches",
           "https://platform.claude.com/docs/en/build-with-claude/batch-processing"),
)

TLDR = (
    "**Prompt caching** lets the API reuse the processing of a prompt's beginning (its **prefix**) when later requests "
    "start with exactly the same content. The order is tools, then system, then messages. This cuts processing time "
    "and cost for prompts that repeat a lot of fixed material: many examples, large background documents, the same "
    "long instructions every time, or long multi-turn conversations.\n\n"
    "It **does not change the answer.** The docs say the response is identical to the one you'd get without caching. "
    "So it can make a working prompt faster and cheaper, but it can't fix a wrong one.\n\n"
    "For the exam, you need to know it **exists** and what it's for. How to configure it is explicitly out of scope."
)

MENTAL_MODEL = (
    "Prompt caching is a bookmark in a book you keep re-reading: it saves you re-reading the same opening pages, but "
    "only if they're word-for-word the same, and it never changes what the book says. The trap is picking it to fix "
    "a wrong, missed or stale answer. Caching makes a prompt faster, not better."
)

EXAM_NOTE = (
    "No task statement covers prompt caching. The guide's out-of-scope list puts its implementation details out of "
    "scope, apart from knowing that it exists (Guide §17 Appendix · Out-of-Scope Topics · p.39). So be ready to "
    "recognise it: know what problem it addresses (repeated identical prompt prefixes: latency and cost). Also know "
    "what it doesn't do, so you can reject it when an option offers it as the fix for a quality, context or "
    "correctness problem. You won't be asked to configure it."
)

WHAT_IT_IS = """
**Sub-concepts, each with a picture to remember**

| # | Sub-concept | What the docs say (paraphrased) | 🧭 Mental model |
|---|---|---|---|
| 1 | What gets reused | The prefix of the prompt, in the order tools → system → messages, when it is **100% identical** to a previous request's. | A bookmark only helps if every page before it is the same, word for word. |
| 2 | What it's for | Repeated long material: many examples, large background context, the same instructions every time, long multi-turn conversations. It cuts processing time and cost. | Don't re-read the same opening chapters every time. |
| 3 | What it doesn't change | The output. The response is identical to the uncached one. | A faster photocopier, not a better writer: a wrong answer stays wrong. |
| 4 | It isn't memory | Each request still sends the full prompt. Caching reuses processing of an identical prefix; it doesn't give Claude, a subagent or a later session any new information. | The bookmark saves time; it doesn't remember what you learned. |
| 5 | Caching and batch together | Batches support prompt caching and the discounts can stack. Batch requests run asynchronously and concurrently, so cache hits inside a batch are best-effort. | Two separate levers: batch trades waiting time for cost, caching reuses an identical start. |

**Where you might meet it (my reading of the scenarios, not guide text):**

- **Customer support agent (Scenario 1):** every turn resends the same long system prompt and tool definitions. That's the kind of repeated prefix caching is for.
- **Structured data extraction (Scenario 6):** a large batch shares the same instructions and examples. Batch + caching can be combined.

In both, caching is an **efficiency** choice, never a fix for how well the agent behaves.
"""

NOT_EXAMINABLE = """
The guide puts **implementation details** out of scope, so this page deliberately doesn't teach:

- `cache_control` placement (automatic vs explicit breakpoints);
- cache lifetimes;
- minimum cacheable lengths;
- the `usage` fields that report cache reads and writes;
- which parameter changes invalidate the cache;
- pricing (pricing calculations are also on the out-of-scope list).

If you need them for real work, they're all on the official prompt-caching page linked below. Don't spend exam study
time on them.
"""

DISTRACTORS = (
    ("“Enable prompt caching” to stop the agent missing facts in the middle of long documents",
     "It's a long-context feature, so it sounds relevant.",
     "Caching doesn't change the output (docs): the same facts get missed, just faster.",
     "Fix the context: key facts summarised at the top, query at the end, trimmed tool output (D4.7).",
     "💡 my recommendation — from the docs: output is identical with or without caching"),
    ("“Use prompt caching so the resumed session knows the code changed”",
     "Caching sounds like it keeps context “fresh”.",
     "It reuses an identical prefix; it adds no new information. Stale tool results stay stale.",
     "Tell the resumed session what changed, or start fresh with a summary (D1.4).",
     "💡 my recommendation — from the docs: caching reuses processing of an identical prefix"),
    ("“Cache the coordinator's prompt so subagents inherit its context”",
     "Caching sounds like shared memory.",
     "A cache is not a channel between agents. A subagent only sees what's in its own prompt.",
     "Pass the needed context explicitly in the subagent's prompt (D1.2, D1.6).",
     "💡 my recommendation — from the docs: each request still sends its full prompt"),
    ("“Use prompt caching instead of the Batch API for the overnight job”",
     "Both are described as ways to cut cost.",
     "They're different levers: batch trades latency for a discount (guide TS 4.5); caching reuses an identical prefix. They can be combined.",
     "Pick batch for work that can wait; add caching when many requests share the same long prefix.",
     "💡 my recommendation — from the batch docs: caching works with batches, discounts stack, hits best-effort"),
    ("“Caching will make the extraction output consistent”",
     "Same prompt prefix → same result?",
     "Caching doesn't change what's generated; consistency comes from the prompt and the schema.",
     "Few-shot examples and a schema / structured output (D4.4, D4.9).",
     "💡 my recommendation — from the docs: output is identical with or without caching"),
)

SIDE_BY_SIDE_HEADERS = ("#", "Question", "Prompt caching", "Message Batches API")
SIDE_BY_SIDE_ROWS = (
    ("1", "On the exam?", "Awareness only (§17 Appendix · p.39)", "⭐ Yes, TS 4.5"),
    ("2", "What it saves", "Processing time and cost for a repeated identical prefix", "Cost (guide: 50%), in exchange for waiting up to 24 h"),
    ("3", "Latency", "Lower for the cached prefix", "Higher: asynchronous, no latency guarantee"),
    ("4", "Changes the output?", "No", "No"),
    ("5", "Needs identical content?", "Yes, the prefix must match exactly", "—"),
    ("6", "Use together?", "Yes, discounts stack; hits in a batch are best-effort", "Yes"),
    ("7", "Fixes wrong / missed / stale answers?", "No", "No"),
)

QUESTIONS = (
    Question(
        q=("An extraction pipeline sends 400-page contracts and often misses clauses in the middle of the document. A "
           "teammate proposes enabling prompt caching. What's the best response?"),
        opts=("Agree: caching keeps the whole document in view.",
              "Disagree: caching reuses processing of an identical prefix and doesn't change the output. Restructure the context instead.",
              "Agree, but only with a long cache lifetime.",
              "Disagree: caching only works for images."),
        ans=1,
        explain=("Per the docs, the response with caching is identical to the one without it. Missed middle content is "
                 "an attention/context problem (D4.7)."),
        scenarios=(6,), basis="docs", in_bank=False),
    Question(
        q=("A support agent must answer customers immediately. Every call resends the same long system prompt and the "
           "same tool definitions, and the team wants to cut the processing time and cost of that repeated part. Which "
           "feature is designed for this?"),
        opts=("The Message Batches API.", "Prompt caching.", "Forcing tool_choice to a specific tool.", "A larger max_tokens."),
        ans=1,
        explain=("Caching targets a repeated identical prefix and keeps the call synchronous. Batch would trade away the "
                 "immediate response."),
        scenarios=(1,), basis="docs", in_bank=False),
    Question(
        q="Which statement about prompt caching is accurate?",
        opts=("It lets later requests use information from earlier conversations.",
              "It improves answer quality on long prompts.",
              "It returns the same response you'd get without caching; it only reuses processing of an identical prompt prefix.",
              "It replaces the Message Batches API."),
        ans=2,
        explain="The docs state caching has no effect on the generated output. It isn't memory and doesn't replace batch.",
        scenarios=(6,), basis="docs", in_bank=False),
)

FAQ = (
    ("Will the exam ask me how to configure prompt caching?",
     "Per the guide, no. Implementation details are out of scope beyond knowing that it exists (§17 Appendix · p.39). "
     "Know what it's for and what it doesn't fix."),
    ("Why is it “D4.2” here if it's barely in the guide?",
     "The numbering comes from a community concept list (unverified) that this section mirrors for layout. The official "
     "guide decides scope, and it makes this topic awareness-only."),
    ("Does caching make Claude remember earlier conversations?",
     "No. Each request still sends its full prompt. Caching only avoids re-processing a prefix identical to a recent "
     "request's."),
    ("Does caching work with the Batch API?",
     "Yes, per the batch docs: the discounts can stack. Because batch requests run asynchronously and concurrently, "
     "cache hits there are best-effort."),
)

GROUNDING = (
    Claim("Implementation details are out of scope beyond knowing that it exists.", "guide", "§17 Appendix · Out-of-Scope Topics · p.39"),
    Claim("No task statement mentions prompt caching.", "guide", "keyword search of guide v1.0, 2026-09-28"),
    Claim("Caching resumes from an identical prompt prefix, reducing processing time and cost.", "docs", "prompt-caching page"),
    Claim("Prefix order is tools → system → messages; the cached segment must be 100% identical.", "docs", "prompt-caching page (cache prefix order)"),
    Claim("Useful for many examples, large background context, repeated instructions, long multi-turn conversations.", "docs", "prompt-caching page"),
    Claim("Caching has no effect on the generated output; the response is identical.", "docs", "prompt-caching page (effect on output)"),
    Claim("Message Batches support prompt caching; discounts can stack; cache hits are best-effort.", "docs", "batch-processing § Using prompt caching with Message Batches"),
    Claim("Batch trades latency for cost (50%, up to 24 h).", "guide", "TS 4.5"),
    Claim("Caching is not memory and not a channel between agents.", "recommendation", "from the docs: each request sends its full prompt; output unchanged"),
    Claim("Which scenarios caching fits (support agent, extraction batches).", "recommendation", "my reading of guide §5 scenarios 1 and 6"),
    Claim("The “looks right, isn't” rows are answer patterns to reject, not guide text.", "recommendation", "derived from the docs facts above"),
)

AWARENESS = AwarenessContent(
    slug="prompt-caching",
    tldr=TLDR,
    mental_model=MENTAL_MODEL,
    exam_note=EXAM_NOTE,
    what_it_is=WHAT_IT_IS,
    not_examinable=NOT_EXAMINABLE,
    distractors=DISTRACTORS,
    side_by_side_headers=SIDE_BY_SIDE_HEADERS,
    side_by_side_rows=SIDE_BY_SIDE_ROWS,
    questions=QUESTIONS,
    faq=FAQ,
    related=("batch-api", "attention-engineering", "session-state", "subagent-state-handoff"),
    docs_refs=DOC_REFS,
    docs_verified_on=DOCS_VERIFIED_ON,
    grounding=GROUNDING,
    guide_note=("Awareness page built at the user's request (2026-09-28). Scope from the exam guide's out-of-scope list; "
                "facts from the official prompt-caching and batch-processing docs (read 2026-09-28). Numbering from a "
                "community concept list (unverified; layout only)."),
)
