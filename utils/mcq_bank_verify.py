"""
Back-test for the exam bank. Run:  .venv\\Scripts\\python.exe -m utils.mcq_bank_verify [--ts 1.1] [--corpus DIR] [--community DIR]

Checks, with no model involved (exit 1 on any failure):
  STRUCTURE  target count, every guide bullet pinned, 4 options, correct option never the longest, A-D spread, valid scenario for the
             domain, type, level, principle, ledger fields, a variety of question types.
  EVIDENCE   every quote found word for word on the named official page, downloaded again (or read from --corpus, same files).
             Items with only guide evidence are listed, not failed: no official page covers them.
  NO REPEAT  against utils/question_bank.py, section 10, the guide's section 9 samples (local PDF text) and the rest of the bank:
             stems compared by word overlap, and the situation + trap ledger compared exactly.
  NO COPY    8-word runs shared with any file under --community (the downloaded study repositories).
  SCOPE      no out-of-scope term in the question text.
"""

import argparse
import collections
import glob
import html
import os
import re
import subprocess
import sys

from utils import mcq_bank
from utils.guide_index import _TS
from utils.mcq_bank.principles import LEVELS, PRINCIPLES, QTYPES
from utils.mcq_sets import SETS, source_info
from utils.mcq_verify import fetch, normalise

# guide section 5: primary domains of each scenario -> the scenarios allowed per domain
SCENARIOS_FOR_DOMAIN = {"1": {1, 3, 4}, "2": {1, 3, 4}, "3": {2, 4, 5}, "4": {5, 6}, "5": {1, 2, 3, 6}}
OUT_OF_SCOPE = (r"fine-tun", r"\bRLHF\b", r"constitutional ai", r"vector database", r"\bembedding", r"computer use", r"server-sent", r"\bSSE\b",
                r"rate limit", r"\bquota", r"\bOAuth\b", r"key rotation", r"\bAWS\b", r"\bGCP\b", r"\bAzure\b", r"tokeniz", r"benchmark",
                r"kubernetes", r"\bdocker\b", r"price per", r"cache_control")
JACCARD_MAX = 0.45


def words(text: str) -> list:
    return re.findall(r"[a-z0-9_]+", text.lower())


def shingles(text: str, n: int = 3) -> set:
    w = words(text)
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}


def jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if a and b else 0.0


def existing_stems() -> list:
    from utils.question_bank import QUESTION_BANK
    out = [(f"bank {ts}", q.get("q") or q.get("question") or q.get("stem") or "") for ts, items in QUESTION_BANK.items() for q in items]
    out += [(q.id, q.q) for qs in SETS.values() for q in qs]
    return out


def guide_samples() -> list:
    pdf = glob.glob("docs/source/*Guide*.pdf")
    if not pdf:
        return []
    try:
        text = subprocess.run(["pdftotext", "-layout", pdf[0], "-"], capture_output=True, encoding="utf-8", errors="replace").stdout
    except OSError:
        return []
    sec = text[text.find("9. Sample Questions"):text.find("How the Exam Is Scored")]
    return [(f"guide sample {m.group(1)}", m.group(2)) for m in re.finditer(r"Question (\d+):(.*?)(?=\n\s*A\.)", sec, re.S)]


def page_text(key: str, corpus: str) -> str:
    url = source_info(key)[2]
    if corpus:
        path = os.path.join(corpus, re.sub(r"^https://", "", url).replace("/", "_"))
        if os.path.exists(path):
            return open(path, encoding="utf-8", errors="replace").read()
    return fetch(url)


def community_index(root: str) -> set:
    seen = set()
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in (".git", "node_modules", "claude-cookbooks-main", "dist", "assets")]
        for f in fn:
            if f.rsplit(".", 1)[-1].lower() not in ("md", "json", "html", "ts", "js", "txt", "csv", "yaml", "yml"):
                continue
            p = os.path.join(dp, f)
            if os.path.getsize(p) > 3_000_000:
                continue
            w = words(html.unescape(open(p, encoding="utf-8", errors="replace").read()))
            seen.update(hash(" ".join(w[i:i + 8])) for i in range(len(w) - 7))
    return seen


def check_ts(ts: str, mod, fails: list) -> None:
    qs, tgt = mod.QUESTIONS, mcq_bank.target(ts)
    _, _, nk, ns = _TS[ts]
    need = {f"{ts}:K{i}" for i in range(1, nk + 1)} | {f"{ts}:S{i}" for i in range(1, ns + 1)}
    if len(qs) < tgt:
        fails.append(f"{ts}: {len(qs)} questions, target {tgt}")
    pinned = collections.Counter(p for q in qs for p in q.points)
    for b in sorted(need):
        if pinned[b] < 1:
            fails.append(f"{ts}: bullet {b} has no question")
        if b.split(":")[1] not in mod.BULLETS:
            fails.append(f"{ts}: bullet {b} has no label in BULLETS")
    pos = collections.Counter(q.ans for q in qs)
    lo, hi = len(qs) // 4 - 1, len(qs) // 4 + 2
    if not all(lo <= pos[i] <= hi for i in range(4)):
        fails.append(f"{ts}: correct positions not spread {dict(pos)}")
    if len({q.qtype for q in qs}) < 4:
        fails.append(f"{ts}: fewer than 4 question types")
    if len({q.scenarios[0] for q in qs}) < 2:
        fails.append(f"{ts}: only one scenario")
    docs = sum(q.basis == "docs" for q in qs)
    if docs > len(qs) * 0.2:
        fails.append(f"{ts}: {docs} docs-based questions, the cap is 20%: the bank must stay on what the guide tests")
    top = collections.Counter(q.qtype for q in qs).most_common(1)[0]
    if top[1] > len(qs) * 0.4:
        fails.append(f"{ts}: {top[1]} questions of type {top[0]}, the cap is 40%")
    allowed = SCENARIOS_FOR_DOMAIN[ts[0]]
    for q in qs:
        lens = [len(o) for o in q.opts]
        if lens[q.ans] == max(lens):
            fails.append(f"{q.id}: correct option is the longest {lens}")
        if len(set(q.opts)) != 4:
            fails.append(f"{q.id}: duplicate options")
        if q.scenarios[0] not in allowed:
            fails.append(f"{q.id}: scenario {q.scenarios[0]} is not a primary scenario for domain {ts[0]}")
        if q.points[0].split(":")[0] != ts:
            fails.append(f"{q.id}: first pin is not in TS {ts}")
        if q.qtype not in QTYPES or q.level not in LEVELS or q.principle not in PRINCIPLES:
            fails.append(f"{q.id}: bad qtype, level or principle")
        if not q.situation or not q.trap:
            fails.append(f"{q.id}: ledger fields missing")
        text = " ".join((q.q, *q.opts, q.explain))
        for pat in OUT_OF_SCOPE:
            if re.search(pat, text, re.I):
                fails.append(f"{q.id}: out-of-scope term /{pat}/")
        for i in range(4):
            letter = "ABCD"[i]
            if i != q.ans and not re.search(rf"\b{letter}\b", q.explain):
                fails.append(f"{q.id}: explanation does not address option {letter}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ts")
    ap.add_argument("--corpus", default="")
    ap.add_argument("--community", default="")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    mods = mcq_bank.load()
    chosen = {a.ts: mods[a.ts]} if a.ts else mods
    fails, guide_only = [], []
    for ts, mod in sorted(chosen.items()):
        check_ts(ts, mod, fails)
        for q in mod.QUESTIONS:
            real = [e for e in q.evidence if e.src != "guide"]
            if not real:
                guide_only.append(q.id)
            for e in real:
                try:
                    if normalise(e.quote) not in normalise(page_text(e.src, a.corpus)):
                        fails.append(f"{q.id}: quote not found on {e.src}: {e.quote[:70]}")
                except Exception as exc:
                    fails.append(f"{q.id}: could not fetch {e.src}: {type(exc).__name__}")
    # no repeat
    others = [(n, shingles(t)) for n, t in existing_stems() + guide_samples()]
    bank = [q for ts in sorted(mods) for q in mods[ts].QUESTIONS]
    shs = {q.id: shingles(q.q) for q in bank}
    ids = [q.id for q in bank]
    if len(set(ids)) != len(ids):
        fails.append("duplicate ids in the bank")
    chosen_ids = {q.id for m in chosen.values() for q in m.QUESTIONS}
    for q in bank:
        if q.id not in chosen_ids:
            continue
        for n, s in others:
            if jaccard(shs[q.id], s) > JACCARD_MAX:
                fails.append(f"{q.id}: stem repeats {n}")
    for i, x in enumerate(bank):
        for y in bank[i + 1:]:
            if {x.id, y.id} & chosen_ids and jaccard(shs[x.id], shs[y.id]) > JACCARD_MAX:
                fails.append(f"{x.id} and {y.id}: stems too similar")
    ledger = collections.Counter(normalise(q.situation + " | " + q.trap).lower() for q in bank)
    fails += [f"ledger repeat: {k}" for k, v in ledger.items() if v > 1]
    # no copy
    if a.community:
        seen = community_index(a.community)
        for m in chosen.values():
            for q in m.QUESTIONS:
                for part in (q.q, *q.opts):
                    w = words(part)
                    hits = sum(hash(" ".join(w[i:i + 8])) in seen for i in range(len(w) - 7))
                    if hits:
                        fails.append(f"{q.id}: {hits} 8-word run(s) shared with a community file: {part[:60]}")
    n = sum(len(m.QUESTIONS) for m in chosen.values())
    print(f"task statements checked: {sorted(chosen)}; questions: {n}; guide-only evidence: {len(guide_only)} {guide_only}")
    for f in fails:
        print("FAIL", f)
    print("ALL CHECKS PASSED" if not fails else f"{len(fails)} CHECK(S) FAILED")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
