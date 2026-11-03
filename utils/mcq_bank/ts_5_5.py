"""Exam bank · TS 5.5. Original questions; see docs/MCQ_BANK_PLAN.md."""
from utils.mcq_sets import MCQ, Evidence

TS = "5.5"
BULLETS = {
    "K1": "An overall accuracy figure such as 97% can hide weak results on particular document types or fields",
    "K2": "Stratified random sampling of high-confidence extractions measures their error rate and reveals new error patterns",
    "K3": "Field-level confidence scores, calibrated on labelled validation sets, decide where review attention goes",
    "K4": "Accuracy must be checked by document type and field segment before high-confidence extractions are automated",
    "S1": "Setting up stratified random sampling of high-confidence extractions for ongoing error measurement",
    "S2": "Analysing accuracy by document type and field before human review is reduced",
    "S3": "Having the model output field-level confidence, then calibrating review thresholds on labelled validation sets",
    "S4": "Routing low-confidence or ambiguous/contradictory extractions to people, spending limited reviewer capacity wisely",
}

_RARE = "You might also need to consider edge case handling, such as how well the model needs to perform on rare or challenging inputs."
_DIST = "Design evals that mirror your real-world task distribution."

QUESTIONS = (
    MCQ(
        id="Q5.5-01",
        q=("Your QA team checked 2,000 supplier documents by hand and scored the extractor at about 97% overall. Since "
           "launch, the customs team has complained that nearly every customs declaration it receives has a wrong tariff"
           " code. Customs declarations are 3% of volume, the tariff-code field appears on all ten document types, and "
           "the other nine types are each at about 97% or better. Which explanation best fits the mismatch?"),
        opts=("The audit sample was too small to be trusted, so its 97% figure is mostly noise.",
              "The tariff-code field is read badly by the model, whatever type of document it appears in.",
              "Overall accuracy is dominated by the common types, so one weak type barely moves it.",
              "The customs team is comparing declarations against a stricter standard than the audit used.",),
        ans=2,
        explain=("A figure averaged over all documents is mostly the large types, so a weak 3% slice can fail most of its "
           "documents while the total stays at 97%. A is not supported, since 2,000 documents give a stable overall "
           "figure, just not a per-type one. B contradicts the stem, because the other nine types are fine. D blames a "
           "reviewer for a complaint the audit design could not have shown."),
        scenarios=(6,), points=('5.5:K1',),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: that one aggregate figure can hide a weak document type is the guide's knowledge point; no official page covers it.",
        qtype="diagnose", level="medium", principle="root_cause",
        situation="97% audit figure while customs declarations (3% of volume) have wrong tariff codes",
        trap="doubt the sample size or blame one field",
    ),
    MCQ(
        id="Q5.5-02",
        q=("A support agent reads incoming emails and fills a form with order number, product, return reason and refund "
           "amount. The weekly dashboard shows 97% overall accuracy and has been flat for two months, yet the refunds "
           "team keeps correcting the refund amount by hand. Which change to the reporting best lets the team see where "
           "the pipeline is weak?"),
        opts=("Report accuracy per field and email type, with the number of checked items beside each cell.",
              "Raise the target on the existing dashboard figure from 97% to 99% and alert when it is missed.",
              "Add the average confidence score for the week beside the accuracy figure on the dashboard.",
              "Double the weekly audit sample so that the overall figure moves less from week to week.",),
        ans=0,
        explain=("The overall figure averages fields that behave differently, so only a per-field view with counts shows the "
           "refund amount problem. B asks for a tighter version of the same number. C adds a score that is not measured "
           "against outcomes. D steadies the average without splitting it."),
        scenarios=(1,), points=('5.5:K1',),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: reporting accuracy by field and document type follows the guide's knowledge point; no official page covers it.",
        qtype="choose", level="easy", principle="fit_for_purpose",
        situation="flat 97% dashboard while one form field is corrected by hand every week",
        trap="tighten or smooth the single headline figure",
    ),
    MCQ(
        id="Q5.5-03",
        q=("An invoice extractor reads 12 fields per invoice. A hand check of 500 invoices shows each individual field "
           "is correct about 97% of the time. The finance system, however, rejects roughly 3 in 10 posted records "
           "because some value is wrong, and the team suspects the finance system's validation. What does the evidence "
           "point to?"),
        opts=("Per-field accuracy understates record-level errors, since one wrong field among twelve spoils a record.",
              "The finance system is over-strict, because 97% accuracy should produce rejections in about 3% of records.",
              "The invoice sample was drawn from easy documents, so the real field accuracy must be far below 97%.",
              "Rejections come from the confidence threshold, because lowering it would admit fewer wrong fields.",),
        ans=0,
        explain=("A record is only usable when all its fields are right, so a 97% per-field rate leaves a large share of "
           "records with at least one error; the metric must also be reported per record. B mistakes a per-field rate "
           "for a per-record rate. C assumes a bias the stem does not show. D reverses the effect of a threshold, which "
           "would send more fields to people, not fewer wrong ones to the finance system."),
        scenarios=(6,), points=('5.5:K1',),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: that one aggregate number can hide poor results is the guide's knowledge point; the per-record framing is my illustration.",
        qtype="diagnose", level="hard", principle="root_cause",
        situation="97% per-field accuracy over twelve fields yet three in ten records rejected",
        trap="blame the downstream system's validation",
    ),
    MCQ(
        id="Q5.5-04",
        q=("Fields below 0.85 confidence go to a review queue, and the rest are posted automatically. To judge the "
           "pipeline, the team reports the correction rate from the queue: reviewers changed 6% of items. A manager "
           "concludes that the pipeline is about 94% accurate overall. What is the main flaw in this estimate?"),
        opts=("It tells you nothing about the auto-posted fields, whose error rate has never been checked.",
              "Six percent of the queue is too small a share of all fields to give a usable estimate.",
              "Reviewers disagree with each other, so their corrections give an unreliable measure of accuracy.",
              "A correction rate counts only changed values, so it cannot be turned into an accuracy figure at all.",),
        ans=0,
        explain=("The queue holds only the low-confidence items, so the quality of what posts without a person has never been "
           "observed; it has to be sampled directly. B comments on the size of the figure and C on the reviewers, but "
           "even a perfect queue measurement would say nothing about the auto-posted fields. D is wrong because "
           "corrections do give the queue's own accuracy; the trouble is which items they cover."),
        scenarios=(6,), points=('5.5:K2',),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: measuring error rates inside the high-confidence band is the guide's knowledge point.",
        qtype="evaluate", level="medium", principle="independent_check",
        situation="pipeline accuracy inferred from corrections made on the low-confidence queue only",
        trap="treat the review queue as a sample of everything",
    ),
    MCQ(
        id="Q5.5-05",
        q=("Your extraction pipeline auto-posts any field above 0.90 confidence. Three weeks ago a new supplier started "
           "sending invoices with the tax shown in a footnote, and the model now reads the wrong number at 0.95 "
           "confidence. Nothing in the review queue shows it, and a customer found it. Which sampling design would most "
           "likely have caught it early?"),
        opts=("Sample only fields in the 0.90 to 0.92 band, since a pattern shows first where confidence is weakest.",
              "Sample the queue items that reviewers corrected most often, and extend the review to similar fields.",
              "Sample the fields that validators flagged, because any new pattern must trip a validator first.",
              "Draw weekly at random within each type from the posted band, plus a small plain random share.",),
        ans=3,
        explain=("A recurring random draw from the posted band, spread over types with a plain random share for what no "
           "stratum anticipated, can show a pattern that confidence and validators miss. A looks only at a thin edge of "
           "the band and the stem's error sits at 0.95. C assumes validators cover every new error. B examines the "
           "queue, where this error never appeared."),
        scenarios=(6,), points=('5.5:K2',),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: sampling high-confidence extractions to detect novel error patterns is the guide's knowledge point.",
        qtype="choose", level="medium", principle="independent_check",
        situation="footnote tax from a new supplier read wrongly at 0.95 and posted automatically",
        trap="sample the thin edge of the band or the already-flagged items",
    ),
    MCQ(
        id="Q5.5-06",
        q=("A research assistant extracts figures from reports and posts those above 0.9 confidence. Each week a "
           "reviewer picks the 20 posted figures that look odd and checks them. Last month 30% of the picks were wrong, "
           "and leadership proposed pausing the assistant. The reviewer says the picks are the interesting ones, not "
           "typical ones. How should the measurement change?"),
        opts=("Keep the hand-picked checks as the error measure, since they surface the most informative failures.",
              "Sample at random within each report type, and keep the hand-picked list only as a lead.",
              "Raise the weekly pick from 20 to 100 so that the error rate stops swinging so much.",
              "Check only the 20 posted figures with the highest confidence, because those are the ones nobody would review.",),
        ans=1,
        explain=("Hand-picked items are biased towards errors, so the 30% describes the picks, not the posted stream; a random"
           " draw gives an error rate you can report, and the picks stay useful for finding causes. A keeps the biased "
           "figure. C scales the same bias. D chooses by confidence rather than at random, so it still does not describe"
           " the stream."),
        scenarios=(3,), points=('5.5:K2',),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: why the sample must be random is the guide's point on stratified random sampling; the scenario is my own.",
        qtype="fix", level="easy", principle="independent_check",
        situation="reviewer's hand-picked odd-looking figures give a 30% error rate used to judge the whole stream",
        trap="count a biased pick as the measured error rate",
    ),
    MCQ(
        id="Q5.5-07",
        q=("Your extractor gives each 12-field invoice a single document confidence. Invoices under 0.9 go to reviewers,"
           " who take 6 minutes each because they re-key all twelve fields. Labelled data show that on a typical flagged"
           " invoice only one or two fields are wrong, and the rest are right over 99% of the time. What design change "
           "best cuts review effort without removing coverage?"),
        opts=("Give every field its own confidence, and show reviewers only fields under their threshold.",
              "Lower the document threshold from 0.9 to 0.8 so that fewer invoices reach the reviewers at all.",
              "Ask the model to list the fields it is unsure of, and trust that list as the review set each day.",
              "Train reviewers to skim each flagged invoice and only re-key the fields that look wrong to them.",),
        ans=0,
        explain=("Field-level scores, with a threshold measured on labelled data for each field, send people to the fields "
           "that need them. B cuts volume but lets more wrong fields through unmeasured. C replaces a calibrated score "
           "with an uncalibrated list. D leaves the decision to the reviewer's eye, which is slow and varies by person."),
        scenarios=(6,), points=('5.5:K3',),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: field-level confidence to direct review attention is the guide's knowledge point.",
        qtype="choose", level="medium", principle="calibrated_escalation",
        situation="reviewers re-key whole invoices when one or two of twelve fields are in doubt",
        trap="use one document score or lower its threshold",
    ),
    MCQ(
        id="Q5.5-08",
        q=("You are building the labelled validation set that will calibrate review thresholds for a pipeline that "
           "handles 8 document types. The pilot customer sent 300 clean, typed invoices, which are the easiest to label."
           " In production, 40% of volume is scanned forms and 15% is handwritten notes. What should the validation set "
           "look like?"),
        opts=("The 300 pilot invoices, because clean labels give the most accurate threshold.",
              "A labelled sample from production documents of all eight types, scans and handwriting too.",
              "The 300 pilot invoices plus several hundred more invoices from the same pilot customer.",
              "Documents labelled by the model itself, because they can cover far more types at no extra cost.",),
        ans=1,
        explain=("Thresholds only mean something on documents like those they will be applied to, so the set must be drawn "
           "from the production mix, all eight types included. A calibrates on an easy slice and applies the result to "
           "scans and handwriting. C adds volume but no variety, so the easy slice still stands in for everything. D "
           "uses model labels as the ground truth they are meant to be checked against."),
        scenarios=(6,), points=('5.5:K3',),
        evidence=(Evidence("api:test-and-evaluate/develop-tests", _DIST),),
        qtype="configure", level="medium", principle="independent_check",
        situation="validation set of 300 clean pilot invoices while 55% of production is scans and handwriting",
        trap="calibrate on the easy labelled slice",
    ),
    MCQ(
        id="Q5.5-09",
        q=("A labelled set shows how fields behave by confidence band. 0.95 and above: 22% of fields, 0.4% wrong. 0.90 "
           "to 0.95: 24% of fields, 2.0% wrong. 0.80 to 0.90: 25%, 6.0% wrong. 0.70 to 0.80: 17%, 9.0% wrong. The rest "
           "fall below 0.70. Policy allows at most 1.5% wrong among all auto-posted fields taken together, and wants as "
           "much posted automatically as that allows. Which threshold do you set?"),
        opts=("0.90: fields above it are 1.2% wrong together, which fits though one band alone does not.",
              "0.95, because the 0.90 to 0.95 band alone is 2.0% wrong, which is above the limit.",
              "0.80, since it posts 71% of fields and is the highest volume that stays near the limit.",
              "0.70, because the extra volume is worth a few more errors that reviewers can clean up later.",),
        ans=0,
        explain=("The limit covers all auto-posted fields together, so the bands are combined: the top two give (22% x 0.4% + "
           "24% x 2.0%) / 46% = 1.2% wrong while posting 46% of fields. B judges one band alone against a limit that "
           "covers the whole posted set, and gives up volume. C adds the 6.0% band and reaches about 2.9% together. D "
           "reaches about 4.1% and leaves the errors in posted data."),
        scenarios=(6,), points=('5.5:K3',),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: setting the threshold from labelled results is the guide's knowledge point; the numbers are invented.",
        qtype="evaluate", level="medium", principle="calibrated_escalation",
        situation="auto-post threshold chosen when the second band alone is above the limit but the combined set is below",
        trap="judge one band alone against a limit that applies to the combined posted set",
    ),
    MCQ(
        id="Q5.5-10",
        q=("Before auto-posting high-confidence extractions, the team tabulates labelled results. Policy: automate a "
           "type-and-field combination only if accuracy is at least 98% on at least 200 labelled items. Invoices: total "
           "99.1% (n=420), due date 98.6% (n=420), line items 93.0% (n=420). Receipts: total 98.9% (n=35). Credit notes:"
           " total 98.0% (n=210). Which set may be automated?"),
        opts=("Invoice total and due date, and receipt total, because every one of them is above 98%.",
              "Invoice total, due date and line items, because invoices average above 98% over their three fields.",
              "Invoice total and due date only, because the credit note result is exactly on the limit.",
              "Invoice total, due date and credit note total, since each meets both rules.",),
        ans=3,
        explain=("Each combination is judged on its own accuracy and its own sample size: invoice total, invoice due date and "
           "credit note total pass both tests. A includes receipt total, whose 35 items are too few. B lets the strong "
           "fields carry the line items at 93%. C wrongly drops the credit note, which sits exactly at 98.0% and meets "
           "the rule."),
        scenarios=(6,), points=('5.5:K4',),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: segment-level validation before automation is the guide's knowledge point; the policy and numbers are invented.",
        qtype="evaluate", level="easy", principle="calibrated_escalation",
        situation="deciding which type-and-field cells meet 98% on at least 200 items",
        trap="average across fields or accept a tiny sample",
    ),
    MCQ(
        id="Q5.5-11",
        q=("The pipeline has been validated on English invoices, with 97.8% accuracy in every segment. The company now "
           "receives German and Spanish invoices at 30% of volume, and the plan is to put them straight into the "
           "existing auto-post rule because the layouts look the same. What should happen first?"),
        opts=("Run them through the existing rule and treat the first month's complaints as the test.",
              "Translate each invoice to English first, since validation then transfers directly.",
              "Auto-post them with the English thresholds at once, and double the weekly sampling for a month.",
              "Keep them in full review while each language and field is measured on a labelled sample.",),
        ans=3,
        explain=("Accuracy for one segment does not carry over to another, so the new languages need their own labelled "
           "measurement before automation. A treats customers as the test. B adds a translation step that creates new "
           "errors and still has not been measured. C posts unmeasured values from day one, and sampling finds the "
           "problem only after wrong values have been posted."),
        scenarios=(6,), points=('5.5:K4',),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: validating each segment before automating it is the guide's knowledge point; the language expansion is my own case.",
        qtype="choose", level="medium", principle="proportionate",
        situation="German and Spanish invoices proposed for an auto-post rule validated on English only",
        trap="transfer the English validation to a new segment",
    ),
    MCQ(
        id="Q5.5-12",
        q=("Six months after launch, policy requires every stratum to stay under 2% errors among auto-posted fields, and"
           " the dashboard shows 1.4% overall. The weekly stratified sample of 60 faxed documents, which are 4% of auto-"
           "posted volume, has shown 6% to 8% errors in each of the last four weeks, while every other stratum stays "
           "under 1.5%. What is the best response?"),
        opts=("Do nothing, since the overall figure meets the limit and faxes are a small share of volume.",
              "Return faxed documents to full review until fixed, and keep sampling the other strata.",
              "Raise the confidence threshold for all documents so that fewer faxed extractions pass.",
              "Stop auto-posting entirely until the whole pipeline has been revalidated on fresh labels.",),
        ans=1,
        explain=("The policy applies to each stratum, and four weekly samples of 60 all above it make the fax result a "
           "pattern, not noise, so pull that segment back to review and leave the healthy ones running. A lets a known "
           "bad segment through because it is small. C penalises every segment, and a global threshold was never shown "
           "to fix faxes. D stops work that the sample shows is healthy."),
        scenarios=(6,), points=('5.5:K4', '5.5:K1'),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: acting on a weak segment instead of the average is the guide's point; the case is my own.",
        qtype="fix", level="hard", principle="proportionate",
        situation="fax stratum at 6-8% in four weekly samples of 60 while the overall auto-post figure is 1.4%",
        trap="reassure with the overall figure or halt everything",
    ),
    MCQ(
        id="Q5.5-13",
        q=("You sample 50 auto-posted extractions at random from each of five document types and review them. Errors "
           "found: invoices 1, receipts 0, purchase orders 3, credit notes 2, bills of lading 6. Auto-posted volume is "
           "invoices 70%, receipts 15%, purchase orders 8%, credit notes 5%, bills of lading 2%. How should you report "
           "the error rate for the auto-posted stream as a whole?"),
        opts=("Pool all 250 reviewed items and divide the 12 errors by 250, giving one overall rate.",
              "Take the simple average of the five stratum error rates and report it as the stream rate.",
              "Report the worst stratum, bills of lading, as the error rate for the whole stream.",
              "Weight each stratum's rate by its volume share, and publish the five rates too.",),
        ans=3,
        explain=("Strata were sampled equally but contribute unequally to the stream, so each stratum's rate is weighted by "
           "its volume share; the per-stratum rates stay visible so a weak one is not hidden. A and B treat the five "
           "strata as equal in size, which overweights the rare types. C is the right figure for that stratum and the "
           "wrong one for the stream."),
        scenarios=(6,), points=('5.5:S1',),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: stratified sampling for error-rate measurement is the guide's skill; the weighting arithmetic is standard and my addition.",
        qtype="evaluate", level="hard", principle="independent_check",
        situation="equal 50-item samples from strata with 70%, 15%, 8%, 5% and 2% of volume",
        trap="pool or average strata of unequal size",
    ),
    MCQ(
        id="Q5.5-14",
        q=("Your weekly plan reviews 10 random auto-posted extractions from each of eight strata. After a month no "
           "errors were found in any stratum, and a manager says the auto-post error rate is zero. The target is under "
           "3% errors in each stratum. How should the plan change?"),
        opts=("Keep the 10-per-stratum plan, because zero errors in every stratum already shows the target is met.",
              "Raise each stratum to about 100 items a week, so that a clean result can rule out rates above 3%.",
              "Merge the eight strata into one pool of 80 items, which gives a single more reliable figure.",
              "Drop the eight strata and review the 80 items that have the highest model confidence.",),
        ans=1,
        explain=("Ten clean items fit a stratum with 10% errors about one time in three (0.9 to the power 10 is 0.35), so they"
           " cannot show the 3% target is met; about 100 items make a clean result unlikely if the rate were 3% or more."
           " A takes a thin sample as proof. C gives one number for eight strata, so a weak stratum is hidden and each "
           "stratum's target is still untested. D swaps random draws for a biased pick."),
        scenarios=(6,), points=('5.5:S1',),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: ongoing error-rate measurement by sampling is the guide's skill; the sample-size reasoning is statistical common sense, not an official page.",
        qtype="fix", level="medium", principle="independent_check",
        situation="10 clean items in each of eight strata read as a zero error rate",
        trap="treat a very small clean sample as proof",
    ),
    MCQ(
        id="Q5.5-15",
        q=("A support agent auto-resolves refund cases using extracted order data. The QA team ran a thorough stratified"
           " review of 600 auto-resolved cases at launch, found 1.2% errors, and stopped sampling. Two months later a "
           "new product line doubled the share of bundle orders, and complaints about bundle refunds are rising. What "
           "should have been in the plan from the start?"),
        opts=("A one-off sample at a larger size, since the launch result would then have held for longer.",
              "A rule to re-run the launch sample only when complaints exceed a set number per week.",
              "A recurring random sample per stratum, with the strata revised as the order mix shifts.",
              "A switch to full review of every auto-resolved case for the first six months of operation.",),
        ans=2,
        explain=("The input mix shifts after launch, so measurement has to continue and the strata must follow the mix. A "
           "cannot see a change that has not happened yet. B waits for customers to find the problem. D removes the "
           "automation benefit for six months and still stops afterwards."),
        scenarios=(1,), points=('5.5:S1',),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: the guide says to sample on an ongoing basis; the product-line change is my own situation.",
        qtype="choose", level="easy", principle="independent_check",
        situation="launch-only stratified review misses a doubled share of bundle orders",
        trap="rely on a one-off launch validation",
    ),
    MCQ(
        id="Q5.5-16",
        q=("A prompt change lifted overall extraction accuracy on the support team's labelled set from 95.4% to 97.1%, "
           "and the team wants to cut human review on the strength of it. The per-segment table shows typed emails up "
           "from 96% to 99% (92% of volume), but forwarded screenshots down from 88% to 75% (8% of volume). What should "
           "you do?"),
        opts=("Cut review for everything, because the overall figure improved and the screenshot slice is small.",
              "Cut review for typed emails only, keep screenshots in full review, and investigate the drop.",
              "Keep the old prompt for screenshots and the new one for typed emails, without further testing.",
              "Cut review for everything but ask the model to be careful with screenshots in the new prompt.",),
        ans=1,
        explain=("The overall gain came entirely from the dominant segment while a segment fell sharply, so review can reduce "
           "only where the segment-level result supports it. A trades a 13-point drop for a better average. C routes "
           "between prompts with no measurement of the combined set-up. D hopes a prompt line fixes a regression that "
           "has not been diagnosed."),
        scenarios=(1,), points=('5.5:S2', '5.5:K1'),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: checking each segment before reducing review is the guide's skill; the figures are my own (0.92 x 96 + 0.08 x 88 = 95.4; 0.92 x 99 + 0.08 x 75 = 97.1).",
        qtype="evaluate", level="hard", principle="calibrated_escalation",
        situation="overall accuracy rises to 97.1% while forwarded screenshots fall from 88% to 75%",
        trap="approve a release on the overall figure",
    ),
    MCQ(
        id="Q5.5-17",
        q=("The accuracy analysis by document type shows invoices at 98.0%, purchase orders at 97.5% and credit notes at"
           " 97.2%, all above the 97% bar, so the team prepares to cut review for all three. Reviewers report that "
           "corrections to the tax amount happen in every document type. What does the analysis miss?"),
        opts=("The type-level split is correct, so the corrections must come from reviewers who are too strict.",
              "Averaging within each type can hide a field that is weak in all of them, so split by field.",
              "The three types are too close to each other, so the analysis needs a fourth type to be meaningful.",
              "Accuracy should be measured on corrections made by reviewers, not on a labelled set.",),
        ans=1,
        explain=("A weak field spread across every type can be diluted by the strong fields of each type, so accuracy has to "
           "be broken down by type and by field before review is reduced. A dismisses the corrections without checking. "
           "C adds a type but not the field view. D swaps the labelled ground truth for a count that only covers queued "
           "items."),
        scenarios=(6,), points=('5.5:S2',),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: analysing accuracy by document type and by field is the guide's skill.",
        qtype="diagnose", level="medium", principle="root_cause",
        situation="all three document types pass 97% while tax amount is corrected in every type",
        trap="analyse by type alone",
    ),
    MCQ(
        id="Q5.5-18",
        q=("Reviewers cannot keep up: the queue grows by 300 items a day. A report on the last month's reviewed items "
           "shows that for supplier-A invoices the reviewers changed under 1% of the extracted values, while for "
           "handwritten notes they changed 35%. The team wants a defensible way to shrink the queue. What is the best "
           "step?"),
        opts=("Raise the global confidence threshold so fewer items enter the queue, whatever their type.",
              "Drop the oldest items from the queue so that reviewers are always working on the freshest cases.",
              "Take supplier-A invoices out of review once a labelled sample confirms them, and keep sampling.",
              "Ask reviewers to skim each item and approve it quickly unless something looks clearly wrong.",),
        ans=2,
        explain=("The correction rates are a lead, and a labelled sample confirms them for the segment before its review is "
           "reduced; sampling then keeps watching it. A shrinks the queue by dropping the checks of every type, "
           "including the 35% one. B drops items by age, not by risk. D lowers the quality of every review."),
        scenarios=(6,), points=('5.5:S2', '5.5:S4'),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: reducing review only after segment analysis is the guide's skill; the correction-rate lead is my illustration.",
        qtype="fix", level="medium", principle="proportionate",
        situation="queue grows 300 a day; supplier-A corrections under 1%, handwritten notes at 35%",
        trap="shrink the queue by a global threshold or by skimming",
    ),
    MCQ(
        id="Q5.5-19",
        q=("You are designing the extraction tool schema for invoices, and review must be routed per field. Which output"
           " design supports calibrating thresholds with labelled data and routing per field?"),
        opts=("One confidence number for the whole invoice, plus the list of field names the model finds hard.",
              "Each field returned with a free-text note on how sure the model is of its value.",
              "Each field returned with a yes-or-no flag saying whether a person should check it.",
              "Each field returned as an object holding its value and its own confidence score.",),
        ans=3,
        explain=("Calibration compares each field's reported confidence with labelled outcomes, so every field needs its own "
           "value and score in a structured form. A offers only a document score and a list the model chooses. B hides "
           "the signal in text that code cannot threshold or compare with labelled outcomes. C gives a decision the "
           "model has already made, so there is no score to calibrate a threshold on."),
        scenarios=(6,), points=('5.5:S3',),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: having the model output field-level confidence is the guide's skill; no official page prescribes the schema.",
        qtype="configure", level="easy", principle="fit_for_purpose",
        situation="schema for per-field review routing on invoices",
        trap="document score, free-text note or a yes-no flag per field",
    ),
    MCQ(
        id="Q5.5-20",
        q=("Thresholds were set from a 300-document labelled set that gave 98% accuracy above 0.88 confidence; the "
           "prompt was refined over several rounds, each checked against that same set. In production, a stratified "
           "sample of the auto-posted band finds 93% accuracy, with no model update and no change in document mix. What "
           "is the most likely root cause?"),
        opts=("The labelled set overlapped the documents used to tune the prompt, so calibration looked too good.",
              "Reviewers who produced the production labels are stricter than those who produced the validation labels.",
              "Confidence scores drift slowly over time, so a drop after a few weeks is unavoidable in any system.",
              "The threshold of 0.88 is too coarse, and a threshold of 0.885 would restore the 98%.",),
        ans=0,
        explain=("A validation set that the prompt was tuned on gives optimistic numbers, so the threshold looked safer than "
           "it was. B invents a labelling difference the stem does not mention. C asserts drift with no change to "
           "explain it. D treats five-thousandths of a point as the cause of a five-point gap."),
        scenarios=(6,), points=('5.5:S3',),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: keeping the calibration set independent is my judgment on the guide's skill, not an official statement.",
        qtype="diagnose", level="hard", principle="independent_check",
        situation="98% on the calibration set but 93% in production after tuning the prompt on the same documents",
        trap="blame labellers, drift or threshold granularity",
    ),
    MCQ(
        id="Q5.5-21",
        q=("A support agent extracts a refund form from emails and reports a confidence per field. The labelled set has "
           "600 fields. In the 0.5 to 0.7 band there are only 12 fields, and 11 are correct. A teammate proposes auto-"
           "posting that band, citing 92% accuracy. What is the right call?"),
        opts=("Auto-post the band, since 92% is above the 90% policy bar.",
              "Auto-post the band, but ask the model to explain each value before it is posted.",
              "Auto-post the band only for the fields that reviewers rate as easy, and review the rest.",
              "Keep the band in review and label more fields there before trusting it.",),
        ans=3,
        explain=("Twelve labelled fields are too few to say what accuracy the band really has, so the threshold for it cannot "
           "be calibrated yet and the band stays with people while labels accumulate. A treats a thin estimate as "
           "measured. B adds a self-explanation that is not evidence. C relies on reviewers' impressions instead of "
           "labelled data."),
        scenarios=(1,), points=('5.5:S3',),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: calibrating thresholds on labelled validation sets is the guide's skill; the thin-band case is my own.",
        qtype="evaluate", level="medium", principle="calibrated_escalation",
        situation="a confidence band with only 12 labelled fields suggests 92% accuracy",
        trap="trust a band estimate built on a handful of labels",
    ),
    MCQ(
        id="Q5.5-22",
        q=("Each day 1,500 fields fall below the review threshold, but reviewers can handle 400. Labelled data show that"
           " errors in the amount, tax and bank-account fields cost far more to fix after posting than errors in notes "
           "or reference fields. How should the queue be ordered?"),
        opts=("First in, first out, so that no item waits longer than another.",
              "By lowest confidence overall, whatever the field, until the 400 are used.",
              "By likelihood of error and cost of an error, with high-impact fields first.",
              "At random each day, so that every field type gets reviewed equally often over time.",),
        ans=2,
        explain=("With room for 400 of 1,500, attention should go where a wrong value is both likely and expensive; calibrated"
           " confidence gives the likelihood and the field type gives the cost. A ignores risk. B spends reviews on "
           "likely but cheap errors, such as notes fields. D spreads the limited capacity evenly over fields that are "
           "not equally important."),
        scenarios=(6,), points=('5.5:S4',),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: prioritising limited reviewer capacity is the guide's skill; the cost weighting is my illustration.",
        qtype="choose", level="easy", principle="calibrated_escalation",
        situation="1,500 flagged fields a day against capacity for 400",
        trap="order by arrival or by confidence alone",
    ),
    MCQ(
        id="Q5.5-23",
        q=("A contract extractor reports payment terms with 0.96 confidence. An audit finds that in 5% of contracts that"
           " have an amendment, the value taken is the superseded original term, and confidence is high on those too. "
           "The amendment conflicts with the original clause. Which routing rule addresses this?"),
        opts=("Raise the confidence threshold for payment terms to 0.99 and send everything below it to review.",
              "Ask the model to prefer the latest document, and route to review only when its confidence is low.",
              "Send to review any contract whose documents disagree on a field, whatever its confidence.",
              "Add a second extraction pass and route to review when the two passes give different values.",),
        ans=2,
        explain=("Confidence describes how sure the model is of the value it picked, not whether the sources agree, so "
           "conflict needs its own routing signal that overrides confidence. A relies on a score that is already 0.96 on"
           " the wrong value. B prefers a rule the model may apply wrongly and still ignores the conflict signal. D "
           "repeats the same reading, which usually returns the same term."),
        scenarios=(6,), points=('5.5:S4',),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: routing contradictory sources to people is the guide's skill; the amendment case is my own.",
        qtype="fix", level="hard", principle="calibrated_escalation",
        situation="superseded payment term extracted at 0.96 when an amendment conflicts with the original",
        trap="raise the threshold or rely on the second pass",
    ),
    MCQ(
        id="Q5.5-24",
        q=("A scanned delivery note has a handwritten quantity that could be read as 17 or 11, and the printed table on "
           "the same page gives 11. The model returns 11 at 0.82 confidence. The pipeline routes fields below 0.80 to "
           "people, so this one posts. Which change best handles this class of document?"),
        opts=("Change the instruction so that any ambiguous digit always returns the lower of the possible values.",
              "Raise the threshold to 0.85 for the quantity field only and keep every other field as it is now.",
              "Flag fields with an unclear or conflicting source and route them to review with the page region.",
              "Have the model re-read the page at a higher resolution until its confidence is above 0.95 again.",),
        ans=2,
        explain=("A field whose source is unclear or inconsistent should reach a person with the evidence, whatever its score."
           " A invents a bias for digits. B moves one cutoff by five hundredths without addressing the unclear source. D"
           " keeps re-reading until a number looks sure, which hides an ambiguity a person should resolve."),
        scenarios=(6,), points=('5.5:S4',),
        evidence=(Evidence("guide", ""),),
        community="Guide-only: routing ambiguous sources to people is the guide's skill; the delivery-note case is my own.",
        qtype="configure", level="medium", principle="preserve_information",
        situation="handwritten 17 or 11 against a printed 11 posts at 0.82 above a 0.80 cutoff",
        trap="move the cutoff or re-read until the score looks high",
    ),
)
