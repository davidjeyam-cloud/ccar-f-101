"""Exam bank · TS 5.2. Original questions; see docs/MCQ_BANK_PLAN.md."""
from utils.mcq_sets import MCQ, Evidence

TS = "5.2"
BULLETS = {
    "K1": "Escalation triggers: the customer asks for a human, a policy exception or gap, or no meaningful progress (complexity alone is not a trigger)",
    "K2": "Escalate at once when the customer explicitly demands a person, but offer to resolve when the issue is straightforward and only frustration was shown",
    "K3": "Sentiment and self-reported confidence are unreliable stand-ins for how complex a case really is",
    "K4": "Several customer matches call for asking for more identifiers, not for picking one by a heuristic",
    "S1": "Put explicit escalation criteria with few-shot examples in the system prompt, showing when to escalate and when to resolve",
    "S2": "Honour an explicit request for a human straight away, without trying to investigate first",
    "S3": "Acknowledge frustration and offer a fix within the agent's reach; escalate only if the customer repeats the preference",
    "S4": "Escalate when policy is ambiguous or silent on the specific request",
    "S5": "Instruct the agent to ask for extra identifiers when a tool returns several matches, not to choose by heuristics",
}

QUESTIONS = (
    # ---- K1: escalation triggers ----
    MCQ(
        id="Q5.2-01",
        q=("Your support agent can refund up to 150 pounds, replace damaged goods and move delivery slots. A manager reviews a day "
           "of conversations and asks which one the agent should have handed to a human. Which conversation is it?"),
        opts=("A customer returning five items from two orders, all inside the return window, who wants a single refund for both.",
              "A customer whose parcel arrived five days late, who is annoyed and wants the shipping fee back, as the policy allows.",
              "A customer wanting a refund on a laptop bought 11 months ago, outside a 30-day window only a supervisor can waive.",
              "A customer whose replacement request needs three lookups across two systems before the photo can be matched to the order."),
        ans=2,
        explain=("The laptop request is a policy exception that only a supervisor can grant, so it belongs with a human. A is "
                 "intricate but sits fully inside the policy. B comes from an annoyed customer, yet the policy allows the fix. D "
                 "takes several tool calls and is still within what the agent is allowed to do."),
        scenarios=(1,), points=("5.2:K1",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 5.2 Knowledge 1 (exceptions and gaps, not just complex cases) is an escalation-policy judgment that no official page states.",
        qtype="choose", level="easy", principle="calibrated_escalation",
        situation="five conversations reviewed, one is an 11-month-old laptop refund against a 30-day window",
        trap="escalate the conversation that looks complex instead of the one needing an exception",
    ),
    MCQ(
        id="Q5.2-02",
        q=("During a ledger outage, a customer's 48 pound refund has failed nine times in 12 minutes: `process_refund` returns "
           "\"ledger temporarily unavailable\" each time, and the agent retries with the same arguments while apologising. The "
           "status page says repairs may take hours, no other tool can pay a refund, and store credit needs a supervisor's "
           "approval. Which change to the agent's behaviour is most effective?"),
        opts=("Escalate to a human with the details and the attempts so far, once repeated tries bring no change.",
              "Retry on a longer schedule, say once a minute, until the ledger answers, and keep the customer posted meanwhile.",
              "Offer store credit for the same amount, since the credit tool still works and the value reaches the customer now.",
              "Tell the customer that the refund cannot be made and ask them to come back once the outage has been fixed."),
        ans=0,
        explain=("Nine identical failures with no way forward are a lack of meaningful progress, so the case goes to a person who can "
                 "decide what to do. B keeps trying a path the status page says is down for hours. C grants a remedy the agent is "
                 "not allowed to give. D ends the conversation with nobody owning the refund."),
        scenarios=(1,), points=("5.2:K1",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: 'inability to make meaningful progress' as a trigger is named in TS 5.2 Knowledge 1; no official page gives an escalation rule.",
        qtype="fix", level="medium", principle="calibrated_escalation",
        situation="nine identical refund failures during a ledger outage with hours of repair time",
        trap="keep retrying on a slower schedule",
    ),
    MCQ(
        id="Q5.2-03",
        q=("A customer disputes a billing error. `get_customer` on her name returns three accounts. She says she has no order number "
           "to hand and cannot read mail at the address she used. She has refused every identifier the agent has asked for, "
           "including the last four digits of her card. Eight turns later the conversation is no closer to one account. What "
           "should the agent do?"),
        opts=("Take the account whose postcode she remembers best, then ask her to confirm the amount of the disputed charge.",
              "Keep asking for other identifiers one at a time until she gives one that narrows the three accounts.",
              "Hand the case to a human, listing the three candidate accounts and the identifiers already asked for.",
              "End the chat politely and point her to the website, where she can open a ticket and attach documents."),
        ans=2,
        explain=("Eight turns with no narrowing is the no-meaningful-progress trigger, so the case needs a person who can verify her another way, and the summary "
                 "saves them repeating the questions. A is still a heuristic pick, with a weak check on top. B repeats an approach "
                 "she has refused eight times. D sends her away with nobody owning the dispute."),
        scenarios=(1,), points=("5.2:K1", "5.2:K4"),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: no official page covers when to stop asking for identifiers and escalate.",
        qtype="choose", level="hard", principle="calibrated_escalation",
        situation="customer refuses every identifier across eight turns while three accounts match",
        trap="keep asking for yet another identifier",
    ),
    # ---- K2: immediate vs offer to resolve ----
    MCQ(
        id="Q5.2-04",
        q=("A product lead notes that 12 intents, such as address changes and delivery-slot moves, are fixed by the agent in 95% of "
           "attempts. She proposes that on these intents the agent always tries the fix first and hands over only after the "
           "customer has asked for a person twice. How should you evaluate this proposal?"),
        opts=("Adopt it: a 95% success rate means trying first leaves most customers better off, whatever they asked for.",
              "Adopt it, but only for customers whose earlier conversations rated the agent positively.",
              "Reject it, and send all 12 intents straight to a human, since the agent should not touch them alone.",
              "Adopt it for customers who have not asked for a person, and hand over at once when one has asked."),
        ans=3,
        explain=("Offering a fix suits straightforward issues when the customer has only shown frustration, but a customer who "
                 "explicitly asks for a person is owed the handover at once. A overrides stated requests because the odds look good. "
                 "B filters on past ratings, which says nothing about what this customer asked for. C throws away a 95% fix rate "
                 "the customers who did not ask for a person would benefit from."),
        scenarios=(1,), points=("5.2:K2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the immediate-versus-offer distinction is stated in TS 5.2 Knowledge 2 and is not covered by an official page.",
        qtype="evaluate", level="medium", principle="calibrated_escalation",
        situation="resolve-first proposal for 12 simple intents with a second-ask handover",
        trap="let a high success rate override an explicit request",
    ),
    MCQ(
        id="Q5.2-05",
        q=("A quarterly review compares two kinds of chat. In 400 chats the customer vented but did not ask for a person; the agent "
           "acknowledged the frustration and offered a fix, and 83% ended without a handover. In 150 chats the customer wrote "
           "something like \"transfer me\" or \"get me an agent\". Within those 150, the 66 where the agent tried a fix first "
           "scored 1.8 out of 5 on satisfaction, against 3.9 for the 84 handed over at once, with the same mix of intents. What do "
           "these results most strongly indicate?"),
        opts=("Fix attempts need better scripts, because the customers in the second group reacted badly to the wording.",
              "A request for a person should be honoured at once, while venting without one is where a fix is offered.",
              "Both kinds of chat should begin with an offered fix, as the first group shows that offers work for most customers.",
              "The low scores come from harder cases, so they say nothing about how the agent responded to the request."),
        ans=1,
        explain=("The same intent mix with a gap of 1.8 against 3.9 points at the response itself: a fix attempt after an explicit "
                 "request hurts, while an offer after venting works. A blames wording that no result in the stem examines. C "
                 "ignores that the offers worked in the group that never asked for a person. D is ruled out by the stem, which "
                 "gives the two sets the same intent mix."),
        scenarios=(1,), points=("5.2:K2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 5.2 Knowledge 2; no official page speaks to honouring explicit requests for a human.",
        qtype="diagnose", level="medium", principle="calibrated_escalation",
        situation="satisfaction 1.8 against 3.9 when a fix was tried before honouring 'transfer me'",
        trap="polish the fix-attempt wording",
    ),
    MCQ(
        id="Q5.2-06",
        q=("An agent's prompt says to hand over at once when a customer explicitly asks for a person, and otherwise to try to "
           "resolve the issue. Four customers write in. For which message should the agent hand over immediately, without "
           "attempting a fix?"),
        opts=("\"Third email about this refund and nobody has answered. This is ridiculous.\"",
              "\"Forget the order number. Put me through to an agent now.\"",
              "\"Does a human handle refunds over 500 pounds, or does this bot do it?\"",
              "\"I have tried this chat three times today and it keeps asking the same question.\""),
        ans=1,
        explain=("Only B is an explicit request for a person. A shows frustration but asks for nothing, so the agent acknowledges it and "
                 "offers a fix. C asks a question about how refunds work, which the agent can answer. D describes a failing "
                 "conversation, and the fix is a better answer, not a handover."),
        scenarios=(1,), points=("5.2:K2", "5.2:S2"),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: telling an explicit demand from venting is a TS 5.2 judgment with no official page.",
        qtype="choose", level="easy", principle="calibrated_escalation",
        situation="four messages: venting, demand, a process question and a looping complaint",
        trap="treat any strong emotion as a request for a person",
    ),
    # ---- K3: sentiment and confidence are weak proxies ----
    MCQ(
        id="Q5.2-07",
        q=("Your agent escalates when a sentiment score falls below -0.4. QA reviewed 60 cases in which a human was needed, such as "
           "exceptions to the returns window, but the agent settled or refused them on its own. In 52 of the 60 the sentiment "
           "score was above 0 and the customer was courteous. What is the most likely root cause?"),
        opts=("Sentiment measures mood, and a polite customer can still ask for what only a human may approve.",
              "The threshold of -0.4 is set too low, so raising it to 0 would also catch the courteous customers.",
              "The sentiment model learned from general text and should be retrained on this company's tickets.",
              "Courteous customers write short messages, and the classifier scores short messages as neutral."),
        ans=0,
        explain=("Whether a case needs a person depends on the request, not on how the customer feels, so a mood score misses polite "
                 "exception requests. B would send every mildly negative chat to humans while the courteous exceptions still "
                 "pass through. C improves how well mood is measured but not what it tells you. D invents a classifier quirk the "
                 "stem does not mention."),
        scenarios=(1,), points=("5.2:K3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 5.2 Knowledge 3; the official support guides measure sentiment but do not say whether it should drive escalation.",
        qtype="diagnose", level="medium", principle="root_cause",
        situation="52 of 60 missed exceptions came from courteous customers with positive sentiment",
        trap="move the sentiment threshold or retrain the classifier",
    ),
    MCQ(
        id="Q5.2-08",
        q=("Each agent reply carries a `confidence` field from 1 to 10, and the team plans to escalate below 6. A labelled set of "
           "800 past conversations exists, in which reviewers marked those that needed a human. Before launch, an engineer is asked "
           "how to find out whether the score is a usable escalation signal. Which analysis is most informative?"),
        opts=("Replay each conversation several times and check that the agent gives the same score on every run.",
              "Ask the agent to explain each score in a sentence, and have reviewers read a sample of the explanations.",
              "Plot how the scores are distributed, and accept the signal if they spread across the whole range of 1 to 10.",
              "Compare the scores with the reviewers' labels, counting cases needing a human that scored 6 or more."),
        ans=3,
        explain=("The question is whether the score tracks the need for a person, so it must be set against the reviewers' labels. A tests "
                 "consistency, and a score can be steady and still wrong. B checks that the explanation reads well, not that "
                 "the score is right. C shows a spread but not whether the spread follows case difficulty."),
        scenarios=(1,), points=("5.2:K3",),
        evidence=(Evidence("api:about-claude/use-case-guides/customer-support-chat",
                           "Track the percentage of correctly escalated conversations versus those that should have been escalated"),),
        community="The quote supports the method of checking escalation accuracy against what should have been escalated, not Knowledge 3's claim itself.",
        qtype="evaluate", level="hard", principle="independent_check",
        situation="checking a 1-to-10 self-rating against 800 reviewer-labelled conversations",
        trap="check the score for consistency or spread instead of correctness",
    ),
    MCQ(
        id="Q5.2-09",
        q=("A customer writes warmly: \"Thanks for the help so far! Could you also waive the early-termination fee? I have only had the "
           "plan for two months.\" Sentiment scores +0.8, and the agent rates its own confidence at 9 out of 10. The policy says "
           "that early-termination fees are waived only by the retention team. What is the sound basis for the agent's next step?"),
        opts=("The positive sentiment: a happy customer will take a polite refusal well, so the agent can decline.",
              "The 9 out of 10 confidence: the agent feels sure, so it should go ahead and grant the waiver.",
              "The policy reserves fee waivers for the retention team, so the agent hands it over.",
              "The two-month tenure: a new customer is a churn risk, so the agent should pass the case on."),
        ans=2,
        explain=("The deciding fact is that the policy reserves this exception for another team. A and B both lean on a signal, mood or the "
                 "agent's own rating, that says nothing about whether the agent may decide. D picks a different proxy, and "
                 "tenure does not make a request outside policy any more or less so."),
        scenarios=(1,), points=("5.2:K3", "5.2:K1"),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 5.2 Knowledge 3 and Knowledge 1; no official page names a basis for escalating.",
        qtype="choose", level="easy", principle="calibrated_escalation",
        situation="warm customer asks for an early-termination fee waiver only the retention team may grant",
        trap="decide from sentiment or from the agent's own confidence rating",
    ),
    # ---- K4: several matches mean ask ----
    MCQ(
        id="Q5.2-10",
        q=("Customers who write in from a shared household landline are looked up by phone number. `get_customer` often returns two or "
           "three records, and the agent takes the one whose first name matches the name given in the chat. In a sample of 500 chats, "
           "17 showed another household member's order details to the caller. Which change is most effective?"),
        opts=("Match on first name and the most recent order date together, which narrows the choice to a single record more often.",
              "Ask for an email address or order number whenever more than one record comes back, and look up again.",
              "Show only the order status, not its contents, whenever more than one record matches the phone number.",
              "Have the tool return only the record with the highest relevance score, so the agent never sees the others."),
        ans=1,
        explain=("Names typed into a chat are unverified, so the choice needs a detail that tells the records apart, which the customer "
                 "can supply. A is a heuristic with one more field. C still serves the call from a record picked by guess. D hides "
                 "the ambiguity inside the tool, so nobody can see the other records exist."),
        scenarios=(1,), points=("5.2:K4",),
        evidence=(Evidence("api:agents-and-tools/tool-use/overview",
                           "if you ask Claude “What’s the weather?” without specifying a location, Claude (particularly Claude Sonnet) might guess values you didn’t supply"),),
        qtype="fix", level="easy", principle="preserve_information",
        situation="shared landline returns up to three records and a first-name match picks one",
        trap="add another matching field to the heuristic",
    ),
    MCQ(
        id="Q5.2-11",
        q=("A research coordinator asks a web-search subagent about \"Halden Group's 2025 emissions\". The search returns two "
           "organisations with that name: a Norwegian shipping firm and a UK care-home chain. The subagent takes the first result and "
           "writes a confident section. In 4 of 30 test runs it was the wrong company, and the requester never named a sector. What is "
           "the most effective fix?"),
        opts=("Return both candidates with details such as country and sector, so the requester can be asked which is meant.",
              "Choose the organisation with the higher search rank, and state the choice and its rank in the report for readers to check.",
              "Research both companies in full and merge the emissions figures into one section that cites both sets of sources.",
              "Choose the organisation that appears in more of the retrieved sources, as that is probably the one the requester meant."),
        ans=0,
        explain=("Two real candidates and no deciding fact in the request mean the subagent returns both, with enough detail to tell them apart, "
                 "to the coordinator, which asks the requester. B keeps the guess and only labels it. C blends two unrelated companies into figures "
                 "that describe neither. D swaps the first-result heuristic for a popularity one."),
        scenarios=(3,), points=("5.2:K4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: asking rather than picking is TS 5.2 Knowledge 4; the subagent has no user to ask, so it returns candidates to the coordinator.",
        qtype="fix", level="medium", principle="preserve_information",
        situation="two organisations called Halden Group and the subagent keeps the top-ranked one",
        trap="pick by search rank or source count and label the choice",
    ),
    MCQ(
        id="Q5.2-12",
        q=("An extraction pipeline reads the sender's name from forwarded complaint emails and links each to a customer record. When two records share a "
           "name, it takes the one whose text is closest to the email. About 3% of cases are filed under the wrong customer, nearly all "
           "with names that two records share. Most emails quote an order number in the body. What "
           "change is most effective?"),
        opts=("Pick the record with the most orders in the last 90 days, since an active customer is more likely to be right.",
              "Link only when the similarity is above 0.95, so that near-ties between two records are rarer.",
              "Run a second pass in which the model chooses between the two records using its own judgment.",
              "When two records match, leave the link empty, read the order number, and queue for review if absent."),
        ans=3,
        explain=("When names cannot separate two records, a further identifier has to, and if none is found the case waits for a person "
                 "instead of being guessed. A swaps one heuristic for another. B does nothing for identical names, which tie at "
                 "any threshold. C asks the model to guess again with no new fact."),
        scenarios=(6,), points=("5.2:K4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 5.2 Knowledge 4 applied to customer matches inside an extraction pipeline (scenario 6).",
        qtype="fix", level="hard", principle="preserve_information",
        situation="two customer records share a name and the closest-text match is filed",
        trap="raise the similarity threshold or add a recent-activity tie-break",
    ),
    # ---- S1: explicit criteria and few-shot examples ----
    MCQ(
        id="Q5.2-13",
        q=("Your support agent's prompt says to \"escalate complex or sensitive cases\". In a review of 300 conversations it escalated "
           "41% of water-damage warranty claims, which the policy lets it settle when the indicator strip is intact, yet it settled "
           "warranty-transfer requests that need a supervisor's approval. What change is most effective?"),
        opts=("Add a classifier model in front of the agent that predicts which warranty claims need a human to see.",
              "Move to a larger model, which will judge better which warranty claims are complex or sensitive.",
              "Replace the vague wording with explicit criteria and examples of escalate and settle cases.",
              "Repeat the rule in capitals, and add that the agent should escalate only when it is truly necessary."),
        ans=2,
        explain=("The agent draws the line in the wrong place in both directions, which points to unclear criteria, and examples that "
                 "show the boundary fix that most directly. A adds a component before the simple prompt change has been tried. B "
                 "assumes a bigger model would guess your company's boundary correctly. D adds emphasis, with no new information "
                 "about where the boundary lies."),
        scenarios=(1,), points=("5.2:S1",),
        evidence=(Evidence("api:build-with-claude/prompt-engineering/claude-prompting-best-practices",
                           "Examples are one of the most reliable ways to steer Claude’s output format, tone, and structure."),),
        qtype="fix", level="medium", principle="proportionate",
        situation="'escalate complex or sensitive cases' sends settleable warranty claims up and lets transfers through",
        trap="add a classifier or a bigger model before fixing the prompt",
    ),
    MCQ(
        id="Q5.2-14",
        q=("You are writing the examples for the escalation section of a system prompt. The agent handles refunds, damaged goods and "
           "subscription changes, and its worst errors fall on the boundary: requests that look alike but differ in whether the "
           "policy covers them. Which set of examples is best?"),
        opts=("Six cases that escalate, each for a different reason, so that the agent learns every trigger.",
              "Four look-alike pairs, one covered by policy and one not, each with a one-line reason.",
              "Ten resolved cases of every common type, so that the agent learns what normal handling looks like.",
              "Three cases of angry customers who were escalated, quoting the exact words each customer used."),
        ans=1,
        explain=("Pairs that differ only in the deciding fact teach the boundary where the errors occur, and the reason names the rule. A "
                 "shows only one side, so nothing teaches the agent when to settle. C shows only handling, with no case "
                 "that crosses the line. D teaches that anger is the trigger, which is not an escalation criterion."),
        scenarios=(1,), points=("5.2:S1",),
        evidence=(Evidence("api:build-with-claude/prompt-engineering/claude-prompting-best-practices",
                           "Cover edge cases and vary enough that Claude doesn’t pick up unintended patterns."),),
        qtype="configure", level="hard", principle="explicit",
        situation="choosing few-shot examples for boundary cases between covered and uncovered requests",
        trap="show only escalations or only resolved cases",
    ),
    MCQ(
        id="Q5.2-15",
        q=("After you added six escalation criteria to the prompt, escalations fell from 38% to 31%. QA still finds that in 15% of "
           "chats the agent sends refunds below the 150 pound limit to humans \"to be safe\". The prompt lists the six escalation "
           "triggers with one example of each, and nothing else about escalation. What is the most likely root cause?"),
        opts=("The prompt shows only when to escalate, with no cases to settle, so in-limit refunds still look risky.",
              "Six criteria are more than the agent can apply, so the list should be cut to the three most common triggers.",
              "The limit should be repeated at the top of the prompt, since the agent may overlook it among the criteria.",
              "The agent's confidence in refunds is low, so a confidence threshold would filter out the needless escalations."),
        ans=0,
        explain=("The examples all point one way, so the agent has no picture of a case it should settle itself and plays safe. Adding "
                 "settle examples next to the triggers corrects that. B removes triggers that are working. C assumes the limit is "
                 "overlooked, which the stem does not suggest. D uses the agent's own rating as the filter, which does not track "
                 "whether a case needs a human."),
        scenarios=(1,), points=("5.2:S1",),
        evidence=(Evidence("api:build-with-claude/prompt-engineering/claude-prompting-best-practices",
                           "Cover edge cases and vary enough that Claude doesn’t pick up unintended patterns."),),
        qtype="diagnose", level="medium", principle="root_cause",
        situation="six escalation triggers with matching examples and no settle examples",
        trap="trim the criteria or add a confidence threshold",
    ),
    # ---- S2: honour an explicit request at once ----
    MCQ(
        id="Q5.2-16",
        q=("Human agents complain that handovers arrive with little context. A team lead proposes that, when a customer explicitly "
           "asks for a person, the agent first runs `get_customer` and `lookup_order` to write a briefing, and then hands over. This "
           "adds about 40 seconds. How should you evaluate the proposal?"),
        opts=("Adopt it: a better briefing shortens the human's handling time, so the customer is helped sooner overall.",
              "Adopt it, but tell the customer in advance that the briefing will take about 40 seconds.",
              "Reject it: hand over at once with what the conversation holds, and let the human look up the rest.",
              "Adopt it only for customers who have already given an order number, since those lookups tend to succeed."),
        ans=2,
        explain=("The customer asked for a person, and every second of investigation first goes against that request; the human can "
                 "do the lookups with the issue as stated in hand. A trades the customer's wish for the team's convenience. B only "
                 "announces the delay. D narrows the proposal without changing what it does to a customer who asked for a person."),
        scenarios=(1,), points=("5.2:S2",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 5.2 Skill 2 (hand over without first investigating); no official page covers it.",
        qtype="evaluate", level="medium", principle="calibrated_escalation",
        situation="briefing lookups proposed before honouring a request for a person",
        trap="investigate first to make the handover richer",
    ),
    MCQ(
        id="Q5.2-17",
        q=("A customer's name returns two accounts. The agent has twice asked for an email address or order number. The customer now "
           "writes: \"No more questions. Get me a person.\" What should the agent do?"),
        opts=("Ask once more, explaining that the details are needed so that the human can find the right account.",
              "Take the account with the latest order, escalate with it, and mention that the match was a guess.",
              "Say it can still fix the problem if the customer gives one detail, and escalate if they decline.",
              "Escalate now with the issue as stated, noting that two accounts match and neither is confirmed."),
        ans=3,
        explain=("The customer has made an explicit request, so the handover happens now, and the open ambiguity travels with it. A and "
                 "C keep working on the case after the request, only phrased as a favour. B settles the ambiguity by guessing, so the "
                 "human may start from the wrong account."),
        scenarios=(1,), points=("5.2:S2", "5.2:S5"),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: combines TS 5.2 Skill 2 and Skill 5; no official page covers it.",
        qtype="choose", level="hard", principle="calibrated_escalation",
        situation="customer demands a person after two unanswered identifier requests on a two-account match",
        trap="make one more attempt to resolve the match first",
    ),
    MCQ(
        id="Q5.2-18",
        q=("The cancellation prompt says: \"Try to keep the customer with a 20% discount offer before any handover.\" In 130 chats where "
           "the customer had written \"connect me to an agent\", the agent made the offer first, 61% of those customers repeated the "
           "request at least once, and satisfaction averaged 2.0 out of 5. How should the prompt change?"),
        opts=("Shorten the offer and put it in the same message as the handover notice, so that the customer sees both together.",
              "Hand over at once when the customer asks for a person, and keep the offer for those who have not asked.",
              "Make the offer only once per customer, and hand over if the customer then repeats the request.",
              "Raise the discount to 30% for customers who ask for a person, as a better offer is more likely to hold them."),
        ans=1,
        explain=("An explicit request outranks the retention step, which belongs with customers who have only voiced doubt. A still "
                 "puts an offer in front of the handover. C delays the handover by one more offer. D tries to buy the customer out "
                 "of the request."),
        scenarios=(1,), points=("5.2:S2", "5.2:K2"),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 5.2 Skill 2 and Knowledge 2; the retention flow is invented for this question.",
        qtype="fix", level="medium", principle="calibrated_escalation",
        situation="cancellation retention offer made before honouring 'connect me to an agent'",
        trap="keep the retention step and make it shorter or richer",
    ),
    # ---- S3: acknowledge frustration, offer a fix, escalate on reiteration ----
    MCQ(
        id="Q5.2-19",
        q=("A customer was charged twice for the same 34.50 pound order and writes: \"This is ridiculous. I am sick of this company.\" "
           "The agent can reverse duplicate charges up to 100 pounds with `reverse_charge`, and the customer has not asked for a "
           "person. What should the agent do?"),
        opts=("Acknowledge the frustration briefly, reverse the duplicate charge and confirm that it is done.",
              "Hand the conversation to a human, because a customer this upset is at risk of leaving.",
              "Explain first how the duplicate happened, to show that the company's process is sound, then reverse it.",
              "Reverse the charge and add a voucher for 20% of the order to show how seriously the company takes it."),
        ans=0,
        explain=("The issue is inside the agent's reach, so it acknowledges the feeling and fixes the problem; a handover stays available "
                 "if the customer asks. B treats mood as a reason to escalate. C puts a defence of the company ahead of the fix. D "
                 "invents a goodwill policy the business never set."),
        scenarios=(1,), points=("5.2:S3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 5.2 Skill 3; the official support guides do not say how an agent should treat a frustrated customer.",
        qtype="choose", level="easy", principle="calibrated_escalation",
        situation="angry customer with a 34.50 pound duplicate charge the agent can reverse",
        trap="escalate or compensate because the customer is upset",
    ),
    MCQ(
        id="Q5.2-20",
        q=("You are writing the prompt rule for customers who say they would prefer a person but have made no request for one, for example "
           "\"honestly I'd rather talk to someone\". In current logs, an agent that hands over on the first such remark gives up on "
           "29% of cases it could have fixed in one tool call. Which rule fits best?"),
        opts=("Hand over on the first remark of this kind, since the customer has said what they want.",
              "Offer a fix up to three times, and hand over only if the customer asks a fourth time.",
              "Offer a fix once, and keep offering for as long as the customer's tone becomes less negative.",
              "Acknowledge the frustration and offer a fix once; hand over if the preference is repeated."),
        ans=3,
        explain=("A first remark of preference with a fix within reach earns one offer, and a repeat shows the customer means it. A "
                 "gives up fixable cases. B and C make the customer ask again and again, or wait for their mood to change, before "
                 "a request is honoured."),
        scenarios=(1,), points=("5.2:S3",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 5.2 Skill 3; no official page covers it.",
        qtype="configure", level="medium", principle="explicit",
        situation="'I'd rather talk to someone' remark with a one-call fix available",
        trap="hand over on the first remark, or keep offering for several rounds",
    ),
    MCQ(
        id="Q5.2-21",
        q=("A frustrated customer wants a refund on a blender bought 140 days ago and says the company \"never listens\". The returns "
           "window is 30 days, and the policy says exceptions to the window are decided by a supervisor. What should the agent do?"),
        opts=("Acknowledge the frustration, explain the 30-day window and decline, so the customer has a clear answer.",
              "Acknowledge the frustration and offer store credit worth half the price as a goodwill gesture.",
              "Acknowledge the frustration, say the request needs a supervisor's decision, and escalate with a case summary.",
              "Acknowledge the frustration and offer troubleshooting for the blender before anything is decided on the refund."),
        ans=2,
        explain=("Acknowledging the feeling is right, but this request is an exception that only a supervisor may decide, so it goes up "
                 "with a summary. A makes the supervisor's decision for them. B invents a remedy outside policy. D offers a fix for a "
                 "problem the customer did not raise."),
        scenarios=(1,), points=("5.2:S3", "5.2:K1"),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: limits of TS 5.2 Skill 3 (a fix within the agent's reach) set against Knowledge 1; no official page covers it.",
        qtype="choose", level="medium", principle="calibrated_escalation",
        situation="140-day-old blender refund against a 30-day window decided by supervisors",
        trap="resolve by declining or by inventing goodwill because the request is within the agent's reach",
    ),
    # ---- S4: policy ambiguous or silent ----
    MCQ(
        id="Q5.2-22",
        q=("The returns policy covers sending back a whole bundle unopened, and sending back a single unopened item from a bundle. It "
           "says nothing about bundles that have been partly used. In a pilot the agent approved 52% of requests to return a partly used "
           "bundle and refused 48%, with no pattern by price, customer or tone, and QA judged about half the rulings wrong. What is "
           "the most likely root cause?"),
        opts=("Sampling randomness: at a lower temperature the agent would give the same ruling on similar requests.",
              "The policy is silent on these requests, so the agent improvises rulings that differ per chat.",
              "The agent weighs the customer's tone, so calmer customers get refusals and anxious ones get approvals.",
              "The policy search returns the unopened-bundle clause first, so the agent applies it to used bundles."),
        ans=1,
        explain=("Requests the policy does not address leave the agent to decide for itself, and that gives the inconsistent rulings "
                 "seen; such requests should go to a person who owns the policy. A would at best make the improvisation consistent. "
                 "C is ruled out by the stem, which finds no pattern by tone. D would produce steady approvals, not an even split."),
        scenarios=(1,), points=("5.2:S4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 5.2 Skill 4 (escalate when policy is silent); no official page covers it.",
        qtype="diagnose", level="medium", principle="root_cause",
        situation="partly used bundles are approved 52% and refused 48% with no pattern",
        trap="lower the temperature to make the improvisation consistent",
    ),
    MCQ(
        id="Q5.2-23",
        q=("The subscription policy covers cancelling and refunding a month. A customer on parental leave asks to pause for three months "
           "and keep her price. The policy says nothing about pausing, and no tool exists for it, though the agent can cancel and "
           "resubscribe. What should the agent do?"),
        opts=("Escalate to a human with the request, noting that the policy does not address pausing.",
              "Cancel now and resubscribe in three months, treating a pause as a cancellation with a return.",
              "Decline, because the policy only describes cancelling and refunding, so a pause is not on offer.",
              "Offer 50% off for the three months, which gives her most of the benefit of a pause."),
        ans=0,
        explain=("A request the policy neither allows nor forbids is a gap that a person must settle. B stretches cancel and resubscribe "
                 "into something the policy never promised, including her price. C turns silence into a refusal. D invents a discount."),
        scenarios=(1,), points=("5.2:S4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 5.2 Skill 4; the pause request is invented for this question.",
        qtype="choose", level="medium", principle="calibrated_escalation",
        situation="subscription pause requested where the policy only covers cancelling and refunding",
        trap="treat silence as refusal or stretch another rule by analogy",
    ),
    MCQ(
        id="Q5.2-24",
        q=("After you added \"escalate when the policy does not address the request\", escalations rose from 12% to 37%. In a sample of "
           "100 escalations, 70 were for requests that the policy does cover, in sections near its end. The policy runs to 9,000 "
           "characters, and the log shows that the string `get_policy` returns to the agent is 2,000 characters long. What is the "
           "root cause?"),
        opts=("The criterion is too broad, so the agent should escalate only when it also reports low confidence.",
              "The agent treats unfamiliar wording as a gap, so the criterion needs examples of true gaps.",
              "A model cannot recognise a policy gap by reading the policy, so the criterion should be dropped.",
              "The tool gives the agent only part of the policy, so covered requests look unaddressed."),
        ans=3,
        explain=("A gap can be judged only against the whole policy, and the agent sees under a quarter of it, so covered requests look "
                 "like gaps. A adds an unreliable signal to a criterion that is working as written. B would be worth doing if the agent "
                 "saw the full text, but the evidence points at the truncated result. C drops a criterion the guide recommends."),
        scenarios=(1,), points=("5.2:S4",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: root-causing false 'policy gap' escalations has no official page. It tests tool-result truncation as the cause, read against the S4 criterion; the truncated result is invented.",
        qtype="diagnose", level="hard", principle="root_cause",
        situation="get_policy returns 2,000 of 9,000 characters and escalations jump to 37%",
        trap="rework the criterion instead of checking what the tool returns",
    ),
    # ---- S5: ask for identifiers on multiple matches ----
    MCQ(
        id="Q5.2-25",
        q=("Customers who write from a shared company mailbox are looked up with `search_orders(email)`, which can return up to eight "
           "orders. The agent's prompt says to \"pick the most plausible order\", and 6% of refunds go to the wrong order. The orders "
           "belong to different employees and are private to each, and the customer is available in the chat to reply. Which rewrite of the instruction is best?"),
        opts=("List all the returned orders to the customer and ask which is theirs, then act on that choice.",
              "Pick the most plausible order, tell the customer which one was chosen, and ask them to confirm.",
              "If several orders come back, ask for the order number or the item and delivery date, then act.",
              "Use only the most recent order from the shared mailbox, since it is the one most likely to be open."),
        ans=2,
        explain=("With several matches the agent asks for a detail that tells the orders apart and acts only when one fits. A reads every "
                 "order on the mailbox out to whoever is in the chat, including other people's. B keeps the guess and asks the "
                 "customer to approve it. D swaps the guess for a simpler rule."),
        scenarios=(1,), points=("5.2:S5",),
        evidence=(Evidence("api:agents-and-tools/tool-use/overview",
                           "if you ask Claude “What’s the weather?” without specifying a location, Claude (particularly Claude Sonnet) might guess values you didn’t supply"),),
        qtype="configure", level="medium", principle="explicit",
        situation="shared mailbox returns up to eight orders and the agent picks the most plausible",
        trap="list every order to the customer or have them confirm a guess",
    ),
    MCQ(
        id="Q5.2-26",
        q=("Two records for \"Priya Raman\" differ in email address and order history but share name and postal address. The agent's "
           "prompt tells it to ask for additional identifiers when several records match, and in 41% of these cases it asks for \"your "
           "full name and address\", then asks again, and the customer abandons the chat. What is the most likely root cause?"),
        opts=("The identifiers it asks for are ones both records share, so the answer cannot narrow the match.",
              "It asks too early, and should first try to infer the right record from the customer's earlier messages.",
              "Asking for any identifier feels like an interrogation, so these cases should go to a human at once.",
              "The tool should return only the most recent record, so the agent has no need to ask the customer."),
        ans=0,
        explain=("Asking is right, but the identifiers must be ones that differ between the records, such as email or recent order details; "
                 "name and address cannot separate these two. B goes back to guessing. C escalates a case that one good question can "
                 "resolve. D hides the second record and brings back the original mistake."),
        scenarios=(1,), points=("5.2:S5",),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: TS 5.2 Skill 5 names the instruction but not which identifiers to ask for; no official page covers it.",
        qtype="diagnose", level="hard", principle="root_cause",
        situation="agent asks for name and address, which both Priya Raman records share",
        trap="stop asking and infer or escalate",
    ),
    MCQ(
        id="Q5.2-27",
        q=("A developer works in Claude Code with an MCP tool `find_service`. For \"billing\" it returns three services: billing-api, "
           "billing-worker and billing-ui. In about 1 of 4 sessions the agent edits the first one, often the wrong one. You are adding "
           "one line to CLAUDE.md. Which line is best?"),
        opts=("When a lookup returns several candidates, guess the one that seems closest to the task and say which.",
              "When a lookup returns several candidates, list them and ask which one is meant before editing anything.",
              "When a lookup returns several candidates, edit all of them and then remove the changes that were not needed.",
              "When a lookup returns several candidates, deny edits to all of them until a hook approves the target."),
        ans=1,
        explain=("Several equal matches and an interactive developer make a short question the cheapest way to get the right target. A "
                 "is still a guess, only announced. C makes unwanted edits and relies on cleaning up afterwards. D "
                 "builds a hook for a case where asking one question settles it."),
        scenarios=(2,), points=("5.2:S5",),
        evidence=(Evidence("api:agents-and-tools/tool-use/overview",
                           "if you ask Claude “What’s the weather?” without specifying a location, Claude (particularly Claude Sonnet) might guess values you didn’t supply"),),
        community="Extension: a Claude Code case at the edge of TS 5.2 Skill 5, which is written for customer matches.",
        qtype="configure", level="easy", principle="explicit",
        situation="find_service returns three billing services and the first is edited",
        trap="pick by name similarity or build a hook instead of asking",
    ),
)
