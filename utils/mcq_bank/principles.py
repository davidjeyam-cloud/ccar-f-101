"""The judgments the exam is really testing, drawn from the guide's §9 sample explanations and §6 objectives. Paraphrased.
Every bank question names one, so a learner sees the idea behind the answer, not just the fact."""

PRINCIPLES = {
    "deterministic": "Code guarantees, prompts only persuade: when a rule must always hold, enforce it in code (hooks, gates), not instructions.",
    "root_cause": "Fix the root cause the evidence points to, and do not blame a component that is working.",
    "proportionate": "Take the smallest change that fixes the problem first; do not add infrastructure before the simple fix has been tried.",
    "least_privilege": "Give each agent and tool only what its role needs; extra capability gets misused.",
    "model_driven": "Let the model reason, and drive control flow from structured signals, not from parsing text or hard-coded sequences.",
    "explicit": "Nothing is inherited or inferred: state context, criteria and examples explicitly.",
    "preserve_information": "Keep facts, sources and failures intact as they move through the system; never let them vanish silently.",
    "fit_for_purpose": "Match the feature to the workload, and know what actually exists and what it does.",
    "independent_check": "Verify independently; self-review and self-reported confidence are not evidence.",
    "calibrated_escalation": "Escalate on customer requests, policy gaps and lack of progress, not on sentiment or a confidence score.",
}
QTYPES = ("diagnose", "fix", "choose", "configure", "evaluate")
LEVELS = ("easy", "medium", "hard")
