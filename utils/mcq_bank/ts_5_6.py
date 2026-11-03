"""Exam bank · TS 5.6. Original questions; see docs/MCQ_BANK_PLAN.md."""
from utils.mcq_sets import MCQ, Evidence

TS = "5.6"
BULLETS = {
    "K1": "Source attribution is lost when findings are compressed or summarised without claim-source mappings",
    "K2": "Structured claim-source mappings must be preserved, and merged, by the synthesis agent",
    "K3": "Conflicting statistics from credible sources are annotated with attribution, not arbitrarily resolved to one value",
    "K4": "Temporal data: dates in structured outputs stop differences over time being read as contradictions",
    "S1": "Subagents output structured claim-source mappings (URL or document name, excerpt) that downstream agents preserve",
    "S2": "Reports separate well-established from contested findings, keeping each source's own characterisation and method",
    "S3": "Document analysis finishes with conflicting values included and annotated, and the coordinator reconciles before synthesis",
    "S4": "Subagents include publication or data collection dates so that time can be interpreted correctly",
    "S5": "Content types are rendered appropriately (financial data as tables, news as prose, technical findings as lists), not in one uniform format",
}

_CIT = "api:build-with-claude/citations"
_BP = "api:build-with-claude/prompt-engineering/claude-prompting-best-practices"

QUESTIONS = (
    # ---- K1: attribution lost in compression ----
    MCQ(
        id="Q5.6-01",
        q=("Six search subagents return 40 findings to a research coordinator, each paired with its correct URL. To fit the synthesis "
           "prompt, a compression step is told: \"Condense these findings into a one-page brief of the most important points, and "
           "list the sources you used.\" The synthesis prompt asks for a source after each claim. In a sample of 100 report "
           "sentences, reviewers matched only 31 to the source that supports them, and 12 matched a different URL from the list. "
           "What is the most likely root cause?"),
        opts=("The synthesis prompt never told the agent to place a citation after each sentence that it writes.",
              "Compression turned findings into prose with one pooled source list, so no claim kept its own source.",
              "The search subagents attached URLs to their findings that did not match the pages they were taken from.",
              "The one-page limit was too small for 40 findings, so the brief dropped the sources of the shortest ones."),
        ans=1,
        explain=("The brief merged claims and listed the sources together, so the link between each claim and its source was gone "
                 "before synthesis started, and synthesis could only guess from the list. A is ruled out because the prompt already "
                 "asks for a source after each claim. C contradicts the stem, which says each finding arrived with its correct URL. "
                 "D does not fit the evidence: sources were present and attached to the wrong sentences, not missing."),
        scenarios=(3,), points=("5.6:K1",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only judgment (TS 5.6 Knowledge 1): no official page discusses attribution lost in compression.",
        qtype="diagnose", level="medium", principle="preserve_information",
        situation="one-page brief of 40 findings ends in a pooled list of 22 URLs and sentences match the wrong source",
        trap="blame the synthesis prompt for missing citations",
    ),
    MCQ(
        id="Q5.6-02",
        q=("A monthly job extracts totals from about 900 supplier invoices. A model then condenses each supplier's extractions into "
           "one digest line such as \"Acme: freight charges up 8%, two late fees.\" Auditors can no longer say which invoices "
           "support a digest line. What is the best change to the condensing step?"),
        opts=("Append the list of all invoice IDs for the supplier to the end of each digest line.",
              "Cut the digests to totals only, so that each line holds less that needs a source.",
              "Run a second extraction over the digest lines to recover the invoice behind each figure.",
              "Have each digest figure keep the invoice ID and page of the extraction it came from."),
        ans=3,
        explain=("Condensing is where the mapping between a figure and its invoice disappears, so the step has to carry the "
                 "invoice and page with every figure it keeps. A attaches the whole group, and auditors still cannot tell which "
                 "invoice produced which figure. B shrinks the digest and leaves its totals just as untraceable. C tries to "
                 "rebuild the link afterwards and can match the wrong invoice when amounts repeat."),
        scenarios=(6,), points=("5.6:K1",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only judgment (TS 5.6 Knowledge 1): no official page discusses attribution lost in compression.",
        qtype="fix", level="easy", principle="preserve_information",
        situation="monthly invoice digest lines cannot be traced to invoices",
        trap="append the supplier's whole invoice list to each line",
    ),
    MCQ(
        id="Q5.6-03",
        q=("Findings from five subagents total 30,000 tokens, and the synthesis prompt can take 8,000. Each finding is a record "
           "with claim, source URL, date and supporting excerpt. Reviewers check claims against excerpts, and figures are "
           "read by date. Which way of getting under the limit is best?"),
        opts=("Drop the weakest records whole, and pass on the rest with all of their fields.",
              "Have a model rewrite all records as a topic-by-topic summary, with the URLs in a numbered list at the end.",
              "Merge records on the same topic into one paragraph, with that topic's URLs in brackets after it.",
              "Keep every record's claim and URL, and cut the dates and excerpts to save space."),
        ans=0,
        explain=("Removing whole records changes how much is reported but leaves every remaining claim tied to its source, date "
                 "and excerpt. B and C compress prose and pool the sources, which breaks the claim-source link. D keeps "
                 "the URL but removes the fields the reviewers and the date reading depend on."),
        scenarios=(3,), points=("5.6:K1",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only judgment (TS 5.6 Knowledge 1): no official page discusses how to trim findings without losing attribution.",
        qtype="choose", level="medium", principle="preserve_information",
        situation="30,000 tokens of findings must fit an 8,000 token synthesis prompt",
        trap="rewrite the records as merged topic summaries",
    ),
    # ---- K2: preserve and merge mappings ----
    MCQ(
        id="Q5.6-04",
        q=("Two subagents independently report that grid-scale battery capacity in a region doubled between 2021 and 2023. One "
           "cites a regulator's yearbook and the other a trade magazine. Readers must see a claim's support at a glance, with no repeated sentences. The synthesis step cites only the source that arrived first. Reviewers now treat this claim as resting on a single article. "
           "What should the synthesis rule be?"),
        opts=("Cite the source from the more authoritative publisher, and omit the other to keep the footnote short.",
              "Cite the source whose excerpt is longer, since a longer excerpt shows more of the claim's support.",
              "State the claim once, and attach every source that supports it from the merged mappings.",
              "Repeat the claim for each source, so that every citation stays beside its own wording."),
        ans=2,
        explain=("Findings that agree are merged into one claim whose mapping lists all of its sources, so the reader sees the "
                 "full support. A and B still choose one source and drop the other, which understates the support. D "
                 "keeps the sources but breaks the rule that each claim is stated once."),
        scenarios=(3,), points=("5.6:K2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only judgment (TS 5.6 Knowledge 2): no official page discusses merging claim-source mappings.",
        qtype="fix", level="medium", principle="preserve_information",
        situation="battery capacity claim confirmed by two sources is cited to only the first to arrive",
        trap="keep only one source for each merged claim",
    ),
    MCQ(
        id="Q5.6-05",
        q=("Each of three search subagents returns findings with footnote numbers [1], [2], [3] and so on, which refer to its own "
           "source list. The synthesis step combines the findings into one report, keeps the numbers as written and adds a single "
           "source list at the end. In 9 of 25 reports, readers who open footnote [2] find a page that does not support the "
           "sentence. What is the root cause?"),
        opts=("The synthesis agent paraphrased the claims, so the sentences no longer match what the sources say.",
              "Footnote numbers were local to each subagent's list, so once merged one number points to several.",
              "The source list at the end is longer than the footnote format can number, so later entries are skipped.",
              "The search subagents ran in parallel, so they numbered their sources in an order that varied between runs."),
        ans=1,
        explain=("A footnote number only means something relative to the list it was made for, and three lists were merged under "
                 "one set of numbers. Stable source identifiers in each mapping, with numbers assigned once after merging, "
                 "avoid this. A is possible in general, but it would not make footnote [2] point to unrelated pages. C invents a "
                 "limit. D confuses order with scope: each subagent's numbers were consistent with its own list however they were "
                 "ordered."),
        scenarios=(3,), points=("5.6:K2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only judgment (TS 5.6 Knowledge 2): no official page discusses merging footnote numbering across agents.",
        qtype="diagnose", level="medium", principle="root_cause",
        situation="footnote [2] points to different pages once three subagents' findings are merged",
        trap="blame paraphrasing or parallel ordering",
    ),
    MCQ(
        id="Q5.6-06",
        q=("A contract pipeline reads each contract page by page and merges the page results into one record. The renewal date is "
           "stated on pages 2, 9 and 14 of one contract. Legal wants to check any merged field against the source pages without "
           "rereading the contract. Which field design for the merged record is best?"),
        opts=("Each field holds its value plus a list of entries, each with document name, page and a short excerpt.",
              "Each field holds its value plus the number of pages that stated it, as a check on agreement.",
              "Each field holds its value plus the first page where it appeared, since later pages repeat it.",
              "Each field holds its value plus a notes string where the extractor describes where it found the value."),
        ans=0,
        explain=("Merging should keep every supporting location for a value, as separate fields that can be checked. B counts "
                 "agreement and names no place to look. C keeps one location of three and loses the rest. D puts the "
                 "locations into free text that has to be parsed and may be inconsistent."),
        scenarios=(6,), points=("5.6:K2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only judgment (TS 5.6 Knowledge 2): no official page discusses merged claim-source records.",
        qtype="configure", level="easy", principle="preserve_information",
        situation="renewal date stated on pages 2, 9 and 14 is merged into one contract field",
        trap="record only a count or the first page",
    ),
    # ---- K3: conflicting statistics annotated ----
    MCQ(
        id="Q5.6-07",
        q=("A report says \"hybrid staff are 13% more productive.\" A subagent had also returned a 4% figure. Both are credible: "
           "the 13% comes from a two-year study of 16,000 staff at a payments firm, and the 4% from a one-year survey of 900 staff "
           "across public bodies. Neither source has been disputed. The synthesis step kept only the 13%, and a stakeholder found "
           "the 4% elsewhere. What should the synthesis step do instead?"),
        opts=("Keep the 13% figure, and add that other surveys found lower values, with no source or number.",
              "Report the average of the two figures, and cite both sources beside that single number.",
              "Report both figures, each with its source, sample and period, and say that they differ.",
              "Report the range 4% to 13% as the finding, and move the two sources to an appendix."),
        ans=2,
        explain=("When credible sources disagree, the report shows both values with their attribution and context so the reader "
                 "can weigh them. A still picks one figure and gives the other no source. B invents a number that no source "
                 "reported. D hides which source supports which end of the range."),
        scenarios=(3,), points=("5.6:K3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only judgment (TS 5.6 Knowledge 3): no official page discusses annotating conflicting statistics.",
        qtype="fix", level="medium", principle="preserve_information",
        situation="13% productivity figure reported alone while a credible 4% figure was dropped",
        trap="average the figures or keep the larger study's value",
    ),
    MCQ(
        id="Q5.6-08",
        q=("Two credible surveys report how many employees work remotely at least three days a week: 31% in one, 18% in the other. "
           "The first sampled 1,200 staff at software firms, and the second 40,000 staff across all employers in a national labour "
           "survey. A synthesis agent must report both in a research brief. What is the most effective handling?"),
        opts=("Report the national survey's 18% as the estimate, since a broader sample is the better one, and cite it.",
              "Report the weighted average of the two figures, and cite both surveys beside that single number.",
              "Present the two figures as an unresolved conflict, each with its URL and the date of its page only.",
              "Report both with populations and methods, and note that they describe different groups."),
        ans=3,
        explain=("The figures measure different groups, so the brief keeps each source's population and method and says the numbers "
                 "are not directly comparable, instead of declaring a winner. A picks one figure though it does not describe the "
                 "same group. B produces a number that describes no population. C calls it a plain conflict and leaves out the "
                 "context that shows it is not one."),
        scenarios=(3,), points=("5.6:K3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only judgment (TS 5.6 Knowledge 3): no official page discusses annotating conflicting statistics.",
        qtype="choose", level="medium", principle="preserve_information",
        situation="31% from software firms versus 18% from a national survey of all employers",
        trap="pick the broader sample or average the two",
    ),
    MCQ(
        id="Q5.6-09",
        q=("An extraction pipeline reads product data sheets from two approved distributors for the same part. One lists the weight "
           "as 1.2 kg and the other as 1.5 kg; neither is marked as authoritative. The other 40 fields agree. The merged record "
           "must reach the review queue today, where staff fix open points. How should the weight field be handled?"),
        opts=("Set the weight to empty and drop both values, with a note in the record that the weight is unavailable.",
              "Keep both weights, each with its distributor and sheet, flag the field as conflicting, and deliver.",
              "Hold the whole record back in the pipeline until a person has settled the weight.",
              "Keep the first value in processing order, and log the other one in a debug file."),
        ans=1,
        explain=("The conflict is passed on, annotated with its two sources, and the rest of the record still moves. A discards "
                 "information that the reviewers could use. C stops 40 good fields for one open point. D lets processing order decide "
                 "and hides the other value in a log."),
        scenarios=(6,), points=("5.6:K3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only judgment (TS 5.6 Knowledge 3): no official page discusses annotating conflicts between sources.",
        qtype="choose", level="easy", principle="preserve_information",
        situation="1.2 kg versus 1.5 kg from two approved distributors in a record due today",
        trap="blank the field or hold the record",
    ),
    # ---- K4: temporal data ----
    MCQ(
        id="Q5.6-10",
        q=("In a market brief, the \"Contested findings\" section lists \"fibre coverage: 61% (2020) versus 74% (2023).\" Both "
           "figures come from credible sources, and the findings carry each figure's collection year. Analysts say these are "
           "one trend, not a dispute, and 11 of 30 contested items this quarter were like this. What change to the synthesis prompt "
           "is most effective?"),
        opts=("Treat figures with different dates as a time series, and call only same-period differences conflicts.",
              "Keep only the newest figure for each topic, so that the contested section holds current figures alone.",
              "Add a verification subagent that re-fetches both pages to determine which of the two figures is correct.",
              "Ask the subagents to attach a confidence score to every figure, so that synthesis can break ties."),
        ans=0,
        explain=("Dates are only useful if synthesis uses them to tell change over time from disagreement; comparing within a period "
                 "keeps real conflicts and shows the rest as a trend. B throws the earlier point away. C re-checks figures that "
                 "were both right. D adds a self-reported score that says nothing about when each figure applies."),
        scenarios=(3,), points=("5.6:K4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only judgment (TS 5.6 Knowledge 4): no official page discusses dates in multi-source synthesis.",
        qtype="fix", level="medium", principle="root_cause",
        situation="2020 and 2023 fibre coverage figures filed as a contested item",
        trap="keep only the newest or add a verification pass",
    ),
    MCQ(
        id="Q5.6-11",
        q=("A pricing extractor reads supplier invoices from the last 18 months. The conflict check in the merge step flags price "
           "pairs for the same part number that differ by more than 3%. Analysts get 160 flags and find that nearly all come "
           "from invoices months apart, where the price was updated. Each record holds part number, price, invoice file and page. "
           "The report must show the price history of each part. What should change?"),
        opts=("Raise the threshold from 3% to 10%, so that normal price updates stop being flagged.",
              "Send flagged pairs to a model that decides which invoice's price is the current one.",
              "Add the invoice date to every record, and compare prices only within the same period.",
              "Keep only the latest invoice per part number before the check, so that older prices never conflict."),
        ans=2,
        explain=("The records have no date, so a price change over time looks like a conflict. With dates, the check compares "
                 "like with like and the history stays. A hides real conflicts above the new threshold and keeps the missing field. "
                 "B asks a model to guess from records that do not say when each price applied. D removes the history that "
                 "the report must show."),
        scenarios=(6,), points=("5.6:K4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only judgment (TS 5.6 Knowledge 4): no official page discusses dates in multi-source extraction.",
        qtype="fix", level="medium", principle="root_cause",
        situation="140 of 160 price conflict flags are price updates months apart",
        trap="loosen the threshold or discard older invoices",
    ),
    MCQ(
        id="Q5.6-12",
        q=("Subagent findings now carry data collection dates, giving annual figures from 2015 to 2024. To reduce noise, a colleague proposes that synthesis silently exclude any "
           "figure from a source more than two years old. The report topic is how electric bus adoption in one country "
           "changed since 2015. How should you evaluate the proposal?"),
        opts=("Adopt it, since recent figures are more likely to be accurate than older ones.",
              "Adopt it, and show the exclusion cutoff in the report's methodology section.",
              "Reject it, and use the dates to rank sources, quoting the newest figure in each case.",
              "Reject it; keep older figures and date them to show change over time."),
        ans=3,
        explain=("The dates are there so that the numbers can be read as a series, and this topic is a trend that needs the old "
                 "points. A assumes age makes a figure wrong, when an old figure may be correct for its time. B discloses "
                 "the filter but still removes the data the topic is about. C uses the dates only to pick the newest value, "
                 "which discards the earlier ones."),
        scenarios=(3,), points=("5.6:K4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only judgment (TS 5.6 Knowledge 4): no official page discusses using dates to interpret findings.",
        qtype="evaluate", level="medium", principle="fit_for_purpose",
        situation="rule proposed to drop figures over two years old from an adoption trend report",
        trap="use dates to filter or pick the newest rather than to interpret",
    ),
    # ---- S1: structured claim-source mappings from subagents ----
    MCQ(
        id="Q5.6-13",
        q=("Search subagents return a 150-word summary per topic that draws on about five pages. Reviewers cannot tell which page "
           "supports which sentence, and pages are long, so they need to see the supporting passage. Which output rule should "
           "the subagent prompt add?"),
        opts=("One paragraph per topic, with every URL consulted listed in brackets at the end of the paragraph.",
              "One record per claim, with its own URL, document name and excerpt, and no claim across pages.",
              "One paragraph per topic, with a confidence score and the search query that produced it.",
              "One record per page, summarising everything the page says, with the page's URL beside the summary."),
        ans=1,
        explain=("Claim-level records tie each statement to the passage that supports it, so the link survives later handovers. A "
                 "pools the URLs for the whole paragraph. C offers a self-reported score and the query, neither of which shows the "
                 "source. D attributes at page level, so a summary still mixes claims that a reviewer cannot check one by one."),
        scenarios=(3,), points=("5.6:S1",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only judgment (TS 5.6 Skill 1): no official page discusses claim-level source mappings in subagent output.",
        qtype="configure", level="easy", principle="preserve_information",
        situation="150-word topic summaries over five pages with no claim-level source",
        trap="list all URLs at the end or summarise per page",
    ),
    MCQ(
        id="Q5.6-14",
        q=("Document analysis subagents return each finding as a claim with a document name and an excerpt of the supporting "
           "passage. The final reports show the claims with document names only, and reviewers cannot see the passages. The "
           "synthesis prompt says: \"Write a clear, concise report for executives and cite your sources.\" What is the most "
           "likely cause?"),
        opts=("The synthesis prompt asks for concision and never requires the claim-source fields to be kept.",
              "Excerpts are returned to the coordinator only by design, and cannot be passed to another subagent.",
              "The synthesis agent's context window was full, so the excerpts were the first part to be cut.",
              "The reports are too short, and a longer output limit would let the synthesis agent keep the excerpts."),
        ans=0,
        explain=("The mapping arrives complete, and the synthesis prompt asks for brevity with citations in the loosest sense, so "
                 "the agent keeps only what that asks. Telling it to preserve the fields as they arrive fixes this. B is false, since the coordinator passes "
                 "anything it holds in the next prompt. C has no support in the stem. D "
                 "mistakes the prompt's wording for an output limit; nothing says the report hit one."),
        scenarios=(3,), points=("5.6:S1",),
        evidence=(Evidence(_CIT, "Responses might now include multiple text blocks where each text block can contain a claim that Claude is making and a list of citations that support the claim."),),
        qtype="diagnose", level="medium", principle="explicit",
        situation="reports show document names but drop the excerpts that arrived with each claim",
        trap="blame the context window or the output limit",
    ),
    MCQ(
        id="Q5.6-15",
        q=("A support agent answers refund questions using a policy-lookup subagent. The agent told one customer \"You have 30 "
           "days to return it,\" and a quality reviewer cannot tell which policy document or wording that came from. The "
           "subagent currently returns a short answer sentence. Which change best lets the reviewer verify answers?"),
        opts=("Have the subagent return a confidence score with each answer, and review the low-scoring ones.",
              "Have the coordinator save the whole policy library with each case for the reviewer to search.",
              "Have the subagent return the answer with document, section and the policy sentence it used.",
              "Have the support agent restate the policy in its own words, so that its reasoning is visible."),
        ans=2,
        explain=("A claim paired with its document, section and the quoted sentence can be checked in seconds and passed on "
                 "to the coordinator unchanged. A offers a self-reported score that does not show where the answer came from. "
                 "B shifts the work onto the reviewer and still gives no link from answer to wording. D shows a "
                 "paraphrase, which is less checkable than the original sentence."),
        scenarios=(1,), points=("5.6:S1",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only judgment (TS 5.6 Skill 1): no official page discusses claim-source mappings from subagents.",
        qtype="choose", level="medium", principle="preserve_information",
        situation="30-day return answer cannot be traced to a policy document",
        trap="use a confidence score or the agent's own restatement",
    ),
    # ---- S2: established vs contested sections ----
    MCQ(
        id="Q5.6-16",
        q=("A report on a new battery technology has 9 key claims. Six are backed by three or more independent studies that agree. "
           "Three rest on a single source each or on sources that disagree. Readers skim, and stakeholders have acted on the "
           "weaker claims as though they were settled. Which report structure fits best?"),
        opts=("Two sections, established and contested, with each claim listed beside a bare link to its source page.",
              "One narrative, with qualifiers such as \"may\" or \"reportedly\" on the weaker claims.",
              "The full report as written, then a closing section listing every claim with fewer than three sources.",
              "Established and contested sections, naming each source with its own wording and method."),
        ans=3,
        explain=("Two labelled sections let a skimming reader see at once which claims are settled and which are open, and name the "
                 "sources behind each. A splits the sections but drops what each source says and how it measured it. B uses hedging words that are easy "
                 "to skim past. C leaves the weak claims stated as fact in the body, where the stakeholders read them."),
        scenarios=(3,), points=("5.6:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only judgment (TS 5.6 Skill 2): no official page discusses established versus contested report sections.",
        qtype="choose", level="easy", principle="fit_for_purpose",
        situation="nine battery claims, three of them weak, read as settled by stakeholders",
        trap="hedge words or a confidence percentage in one list",
    ),
    MCQ(
        id="Q5.6-17",
        q=("A report says: \"Research shows that late-night screen use harms teenagers' sleep.\" The search subagent's finding for "
           "this claim reads \"screen use linked to shorter sleep\", with URL and date. When a reviewer opens the page, it "
           "describes an observational survey of 200 students in one district that reports an association only. What is the "
           "most likely root cause?"),
        opts=("The synthesis agent was not told to check each claim against its page before writing the report.",
              "The finding lost the study's wording and method, so synthesis wrote a stronger claim.",
              "The search subagent used a source of lower quality than the topic needed, and should have found a trial.",
              "Subtasks were split too narrowly, so no trial-based sources were ever looked for."),
        ans=1,
        explain=("The mapping held a claim and a location but nothing about how the study was done, so synthesis had no limits to "
                 "preserve and wrote the stronger general statement. A asks synthesis to reopen sources it was not given. C "
                 "blames the subagent for using a real source with an honestly reported result. D is a coverage problem, and "
                 "the report states a claim from a source that was found."),
        scenarios=(3,), points=("5.6:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only judgment (TS 5.6 Skill 2): no official page discusses preserving source methodology in synthesis.",
        qtype="diagnose", level="hard", principle="preserve_information",
        situation="an association in a 200-student survey becomes research showing harm",
        trap="blame coverage or ask synthesis to recheck pages it never received",
    ),
    MCQ(
        id="Q5.6-18",
        q=("The \"Contested findings\" section of a report lists items such as \"Sources differ on the share of recycled aluminium: "
           "38% or 52%.\" Readers cannot judge the difference, and an editor asks for the section to be rebuilt. The subagent "
           "findings include the source name, the source's own statement of its result, and how it measured it. What should "
           "the rebuilt entries contain?"),
        opts=("Each figure with its source, the source's own wording of the result, and how it was measured.",
              "Each figure with a rating of how likely it is to be right, based on the synthesis agent's judgment.",
              "Each figure with a link, followed by a sentence saying which one the editor should trust more.",
              "Each figure with its source, and a single combined figure that readers can use as a working value."),
        ans=0,
        explain=("Readers can weigh a disagreement when each side keeps its source, its own characterisation of the result and its "
                 "method. B and C replace that detail with the synthesis agent's opinion. D adds a combined number that no source "
                 "reported."),
        scenarios=(3,), points=("5.6:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only judgment (TS 5.6 Skill 2): no official page discusses presenting contested findings.",
        qtype="fix", level="medium", principle="preserve_information",
        situation="contested section says 38% or 52% with nothing to weigh the figures by",
        trap="add a likelihood rating or a recommended source",
    ),
    # ---- S3: complete analysis with conflicts annotated; coordinator reconciles ----
    MCQ(
        id="Q5.6-19",
        q=("A document analysis subagent compared two reports that give different 2022 market sizes, 9.1 and 11.4 billion. Its prompt "
           "says \"Return the most reliable value for each metric.\" The coordinator's final reports show only one value, although "
           "the subagent's own analysis log flagged the disagreement. What is the cause?"),
        opts=("The coordinator's context window was full, so the second value was cut from the subagent's long reply.",
              "Subagents are unable to pass more than one value per metric back to the coordinator.",
              "The prompt asks for one value per metric, so the subagent chose one and left the other in its log.",
              "The subagent should have asked the coordinator which report to trust before it analysed either."),
        ans=2,
        explain=("The prompt forces a single answer, so the conflict was settled inside the subagent and never reached the coordinator. "
                 "The analysis should finish with both values included and annotated. A has no support in the stem. B is false, "
                 "since a subagent can return any structure it is asked for. D stops the analysis until someone else rules, when it "
                 "should be completed with the conflict marked."),
        scenarios=(3,), points=("5.6:S3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only judgment (TS 5.6 Skill 3): no official page discusses how document analysis reports conflicting values.",
        qtype="diagnose", level="easy", principle="preserve_information",
        situation="most-reliable-value prompt hides a 9.1 versus 11.4 billion disagreement",
        trap="assume a tool or context limit dropped the second value",
    ),
    MCQ(
        id="Q5.6-20",
        q=("To keep conflicts away from synthesis, a developer proposes that document analysis subagents stop and return an error "
           "whenever two passages in a batch of 40 contradict each other, so the coordinator can retry. In your tests about 30% "
           "of batches contain at least one contradiction. How should you evaluate the proposal?"),
        opts=("Adopt it; on an error the coordinator retries the batch with a different prompt to get a consistent answer.",
              "Reject it; the subagent should finish its analysis and return both values with sources, flagged.",
              "Adopt it, but only after the subagent sets aside the contradicting passages and reports on the others.",
              "Reject it; the subagent should resolve each contradiction itself and return one clean value per metric."),
        ans=1,
        explain=("Real sources contradict each other, so a retry will hit the same passages. Completing the analysis with both "
                 "values annotated gives the coordinator what it needs to reconcile. A throws away the other 39 passages' "
                 "results and a retry cannot change what the documents say. C hides the contradicting passages, which are the "
                 "ones that most need attention. D removes the conflict where the context to resolve it is missing."),
        scenarios=(3,), points=("5.6:S3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only judgment (TS 5.6 Skill 3): no official page discusses document analysis output for conflicting sources.",
        qtype="evaluate", level="hard", principle="preserve_information",
        situation="halt on contradiction proposed when 30% of batches contain one",
        trap="treat a contradiction in sources as an error to retry",
    ),
    MCQ(
        id="Q5.6-21",
        q=("A user asked for churn rates for North American subscription services only. The user's request is visible to the "
           "coordinator and to synthesis, not to the subagents. The document analysis subagent returns two annotated figures for "
           "one service, 22% from an annual report and 31% from an analyst note; the coordinator forwards both unchanged, and the "
           "report shows an open conflict. A reader notes that the 31% covers global subscribers. Where should the conflict be "
           "reconciled?"),
        opts=("In synthesis, which should pick the figure that matches the request and drop the other.",
              "In the document analysis subagent, which should drop any figure whose scope it cannot confirm.",
              "In a review step after synthesis, where an editor agent corrects the final report text.",
              "In the coordinator, which should reconcile conflicts against the request before synthesis."),
        ans=3,
        explain=("The coordinator receives the annotated conflict, holds the request, and can note the scope difference or send a "
                 "follow-up search before synthesis starts. A leaves the decision to the last stage, which drops a source without "
                 "the coordinator seeing it. B asks the subagent to apply a scope it was not given. C repairs the text after "
                 "the report is written."),
        scenarios=(3,), points=("5.6:S3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only judgment (TS 5.6 Skill 3): no official page discusses where multi-agent conflicts are reconciled.",
        qtype="choose", level="hard", principle="explicit",
        situation="global 31% churn shown beside a North American 22% as an open conflict",
        trap="leave reconciliation to the synthesis stage",
    ),
    # ---- S4: publication or collection dates ----
    MCQ(
        id="Q5.6-22",
        q=("A 2024 news article quotes a \"recent\" survey on remote-work preference that was actually fielded in 2019. Search "
           "subagents record the article's publication date with each finding. The report treats the figure as 2024 data and "
           "describes it as a reversal against a 2023 survey. What change to the subagents' required output best prevents "
           "this?"),
        opts=("Require a data collection date where the source states one, beside the publication date.",
              "Require the retrieval date of each page, so that synthesis can see how current each finding is.",
              "Make the publication date mandatory, and drop any finding whose page does not show one.",
              "Add a verification subagent that searches for newer versions of every figure before synthesis."),
        ans=0,
        explain=("The publication date says when the claim was written, and the collection date says when the data describes. "
                 "Both are needed to read a figure in time. B records when the page was fetched, which says nothing about "
                 "the data. C leaves the 2019 survey dated 2024 and discards sources without a date. D adds a round "
                 "trip for each figure and still does not date the data."),
        scenarios=(3,), points=("5.6:S4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only judgment (TS 5.6 Skill 4): no official page discusses publication versus collection dates.",
        qtype="fix", level="hard", principle="preserve_information",
        situation="2019 survey quoted in a 2024 article is treated as 2024 data",
        trap="record only the publication date or the retrieval date",
    ),
    MCQ(
        id="Q5.6-23",
        q=("A support agent told a customer that parcels usually arrive in 4.2 days, then another that they take 6.8 days. Both "
           "figures came from the delivery-report subagent, which returned the number and the report name only. One report covers "
           "March and the other the December holiday peak, and the agent had no way to know. What should the subagent's output "
           "include?"),
        opts=("Only the most recent report's figure, since customers want current delivery times.",
              "The average of the two figures, with both report names listed beside it.",
              "The period each figure covers, next to the figure and its report name.",
              "Both figures with a flag marking them as a conflict between internal reports."),
        ans=2,
        explain=("With the period attached, the agent can see the two figures describe different seasons and explain them. A "
                 "discards the other season. B yields a figure that no report stated. D calls it a conflict and withholds the "
                 "fact that would show it is not one."),
        scenarios=(1,), points=("5.6:S4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only judgment (TS 5.6 Skill 4): no official page discusses data collection periods in subagent output.",
        qtype="fix", level="easy", principle="preserve_information",
        situation="4.2 and 6.8 day delivery figures from March and the holiday peak",
        trap="keep the newest figure or flag a conflict",
    ),
    MCQ(
        id="Q5.6-24",
        q=("Search subagents now return a date field, but the values include \"last year\", \"earlier this quarter\" and \"recently\", "
           "copied from the article text. Every article carries a publication date. In 12 of 40 reports, a figure carried the wrong year and was reported as conflicting "
           "with another. What is the most likely cause?"),
        opts=("The subagents should have returned the retrieval time of each page in place of the date from the text.",
              "The date field is optional, so the subagents leave it empty whenever an article gives no year.",
              "The synthesis agent does not know today's date, and should be given it in its system prompt.",
              "Relative phrases need the article's date, so subagents should resolve them to absolute dates."),
        ans=3,
        explain=("\"Last year\" in a 2022 article means 2021, and a reader or agent who lacks that date will place it wrongly. "
                 "Absolute dates resolved at the source remove the guess. A swaps a text date for a fetch time that does not "
                 "describe the data. B contradicts the stem, which shows values being returned. C would resolve phrases "
                 "against the wrong anchor, because they are relative to the article, not to today."),
        scenarios=(3,), points=("5.6:S4",),
        evidence=(Evidence("guide", ""),),
        community="Writer's recommendation (the guide requires dates in structured outputs, not absolute-date resolution); no official page speaks to it.",
        qtype="diagnose", level="medium", principle="root_cause",
        situation="last year and recently stored as dates cause wrong-year figures",
        trap="give synthesis today's date to resolve relative phrases",
    ),
    # ---- S5: render content types appropriately ----
    MCQ(
        id="Q5.6-25",
        q=("A competitive-analysis report covers three kinds of content: revenue and margin figures for six firms over eight "
           "quarters, news about two acquisitions, and findings on three battery chemistries (a safety history, a supply-chain "
           "constraint and a pending regulatory review, each described differently). The current draft is bullet points throughout. Which rendering fits best?"),
        opts=("Prose for the figures, a table for the news and one paragraph for each chemistry.",
              "A table for financials, prose for the news and a structured list for chemistries.",
              "A table for each of the three kinds, so that the layout is uniform and easy to scan later.",
              "Bullet points kept throughout, with bold headings added for each of the three kinds."),
        ans=1,
        explain=("Each kind of content suits its own form: numbers compare in a table, an event reads as prose, and findings with "
                 "repeating attributes scan as a structured list. A reverses the fit. C and D apply one form to everything, "
                 "which is what makes the current draft hard to use."),
        scenarios=(3,), points=("5.6:S5",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only judgment (TS 5.6 Skill 5): no official page discusses rendering by content type.",
        qtype="choose", level="easy", principle="fit_for_purpose",
        situation="six firms over eight quarters, two acquisitions and three chemistries all in bullets",
        trap="apply one uniform format to every content type",
    ),
    MCQ(
        id="Q5.6-26",
        q=("To simplify parsing, an engineer proposes that every agent in the research pipeline, including the synthesis agent that "
           "writes the reader-facing report, return JSON only, with a template turning it into text. The team wants to keep "
           "claim-source mappings intact and the report readable. How should you evaluate this?"),
        opts=("Keep structured mappings between agents, and render each content type in its own form.",
              "Adopt it in full; one JSON shape for every content type is what keeps the mappings intact.",
              "Keep JSON between agents, and render the final report through one template for every content type.",
              "Adopt it, but let the template drop fields the report does not show, including the sources."),
        ans=0,
        explain=("Structured data suits the handovers between agents, while the final report should present each kind of content in the "
                 "form that reads best. B and C fix the output to one shape, so financial data, news and technical findings all "
                 "read alike. D drops the sources the mappings exist to protect."),
        scenarios=(3,), points=("5.6:S5", "5.6:S1"),
        evidence=(Evidence("guide", ""),),
        community="Guide-only judgment (TS 5.6 Skill 5): no official page discusses rendering by content type.",
        qtype="evaluate", level="hard", principle="fit_for_purpose",
        situation="JSON-only pipeline with one template proposed for the reader-facing report",
        trap="confuse the format between agents with the format readers see",
    ),
    MCQ(
        id="Q5.6-27",
        q=("A synthesis agent in a battery research system wrote its technical findings section as paragraphs. There are 17 "
           "findings, each covering a component, a risk, the evidence found and the action to take. Engineers need to filter and "
           "assign them by component and risk. What change to the synthesis prompt is best?"),
        opts=("Replace the findings with a one-line summary per component, dropping the evidence for each.",
              "Keep the paragraphs, sort them by risk, and bold the component name at the start of each one.",
              "Ask for each finding as a list entry with labelled component, risk, evidence and action.",
              "Ask for short bullet points of about a sentence each, one bullet for every finding."),
        ans=2,
        explain=("Findings that share the same attributes read best as a structured list with labelled fields, which also lets "
                 "engineers filter by component and risk. A discards the evidence that justifies each finding. B keeps the paragraph "
                 "form, which still has to be read to find any field. D shrinks each finding to a sentence and mixes the fields "
                 "together."),
        scenarios=(3,), points=("5.6:S5",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only judgment (TS 5.6 Skill 5): no official page discusses rendering technical findings as structured lists.",
        qtype="fix", level="medium", principle="fit_for_purpose",
        situation="17 battery findings written as paragraphs",
        trap="shorten, sort or bold the paragraphs instead of structuring them",
    ),
)
