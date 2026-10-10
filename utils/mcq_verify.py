"""
Back-test for section 10 · MCQs.   Run:   .venv\\Scripts\\python.exe -m utils.mcq_verify

It needs internet access and checks, with no model involved:
  1. STRUCTURE   four options, a valid answer, the correct option is never the longest, correct positions are spread,
                 ids are unique, and every guide bullet exists (utils/guide_index.py; checked when utils/mcq_sets.py
                 is imported).
  2. EVIDENCE    every word-for-word quote in `Evidence` is downloaded again from the official page it names and found
                 there (markdown links, backticks and ** are ignored on both sides).
  3. COMMUNITY   the claims made about the community repositories (what they say, and what they leave out) are re-checked
                 against the raw files on GitHub.
A question passes only if all of its quotes are found. Exit code 1 if anything fails, so it can gate a commit.
The live CLI checks recorded in `MCQ.live` need Claude Code and are not repeated here.
"""

import collections
import re
import sys
import urllib.request

from utils.mcq_sets import SETS, SOURCES

UA = {"User-Agent": "ccar-f-101-verifier"}


def normalise(text: str) -> str:
    t = text.replace("’", "'").replace("“", '"').replace("”", '"')
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)          # [text](url) -> text
    t = t.replace("`", "").replace("*", "")
    return re.sub(r"\s+", " ", t).strip()


_cache: dict = {}


def fetch(url: str) -> str:
    if url not in _cache:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=40) as r:
            _cache[url] = r.read().decode("utf-8", errors="replace")
    return _cache[url]


def structure_report() -> list:
    rows, ids = [], collections.Counter()
    for key, qs in SETS.items():
        pos = collections.Counter("ABCD"[q.ans] for q in qs)
        rows.append((f"{key}: {len(qs)} questions", len(qs) == 10, f"correct positions {dict(sorted(pos.items()))}"))
        rows.append((f"{key}: positions spread (each of A–D used 2–3 times)", all(2 <= pos[c] <= 3 for c in "ABCD"), ""))
        for q in qs:
            ids[q.id] += 1
            lens = [len(o) for o in q.opts]
            rows.append((f"{q.id}: correct option is not the longest", lens.index(max(lens)) != q.ans, str(lens)))
            rows.append((f"{q.id}: options are all different", len(set(q.opts)) == 4, ""))
    rows.append(("ids are unique", all(v == 1 for v in ids.values()), ""))
    return rows


def evidence_report() -> list:
    rows = []
    for key, qs in SETS.items():
        for q in qs:
            for i, e in enumerate(q.evidence, 1):
                try:
                    page = normalise(fetch(SOURCES[e.src][2]))
                    ok = normalise(e.quote) in page
                    note = SOURCES[e.src][1]
                except Exception as exc:                      # a failed download is a failure, never a pass
                    ok, note = False, f"could not fetch {SOURCES[e.src][2]}: {type(exc).__name__}"
                rows.append((f"{q.id} evidence {i}/{len(q.evidence)} on {e.src}", ok, note if not ok else ""))
    return rows


# (label, raw URL, text that must be present, text that must be ABSENT, optional start marker, optional end marker)
RAW = "https://raw.githubusercontent.com"
PL = f"{RAW}/paullarionov/claude-certified-architect/main/guide_en.md"
DN2 = f"{RAW}/dnacenta/claude-certified-architect/main/domains/d2-tool-design-mcp.md"
DN3 = f"{RAW}/dnacenta/claude-certified-architect/main/domains/d3-claude-code-config.md"
OA = f"{RAW}/OlivierAlter/Claude-Certified-Architect-Foundations-Certification-Exam/main/Claude%20Certification%20Exam.md"
COMMUNITY = (
    ("paullarionov §5.5: allowed-tools “Restricts which tools are available”", PL, ("Restricts which tools are available",), (), None, None),
    ("paullarionov §5.5: argument-hint “asks for an argument when invoked without parameters”", PL, ("asks for an argument when invoked without parameters",), (), None, None),
    ("paullarionov §5.5: personal variants under different names", PL, ("Create personal variants under different names so you don't affect teammates",), (), None, None),
    ("paullarionov §4.2: tools from all connected servers available at once", PL, ("Tools from all connected servers are available at once",), (), "## 4.2", "## 4.3"),
    ("paullarionov §4.3: user configuration `~/.claude.json`, no local scope or precedence", PL, ("User configuration",), ("local scope", "precedence", "Local scope"), "## 4.3", "## 4.4"),
    ("paullarionov §4.3: prefer existing community servers", PL, ("prefer existing community MCP servers",), (), "## 4.3", "## 4.4"),
    ("paullarionov §4.3: no statement about an unset variable", PL, ("${GITHUB_TOKEN}",), ("unset", "isn't set", "not set"), "## 4.3", "## 4.4"),
    ("paullarionov §4.5: resources as a map that avoids exploratory calls", PL, ("does not need exploratory tool calls",), (), "## 4.5", "# Chapter 5"),
    ("paullarionov §4.1 lists prompts as a primitive", PL, ("Prompts",), (), "## 4.1", "## 4.2"),
    ("dnacenta §2.4: local scope is the default", DN2, ("Local** (default)",), (), None, None),
    ("dnacenta §2.4: truncation at 2,048 characters", DN2, ("2,048 characters",), (), None, None),
    ("dnacenta §2.4: headless runs load project servers without asking", DN2, ("load them without asking",), (), None, None),
    ("dnacenta §2.4: no precedence order between scopes", DN2, ("Installation Scopes",), ("precedence",), None, None),
    ("dnacenta §2.4: lists prompts as a server primitive", DN2, ("**Prompts**",), (), None, None),
    ("dnacenta §3.2: allowed-tools = pre-approved", DN3, ("Tools pre-approved while this skill is active",), (), None, None),
    ("dnacenta §3.2: argument-hint shown in autocomplete", DN3, ("Hint shown in autocomplete",), (), None, None),
    ("dnacenta §3.2: priority Enterprise > Personal > Project", DN3, ("Enterprise > Personal > Project",), (), None, None),
    ("dnacenta §3.2: lifecycle, file not re-read", DN3, ("does **not** re-read the file on later turns",), (), None, None),
    ("dnacenta §3.2: disable-model-invocation and user-invocable both listed", DN3, ("`disable-model-invocation`", "`user-invocable`"), (), None, None),
    ("OlivierAlter Q38: resources expose content catalogs", OA, ("MCP resources are designed to expose content catalogs",), (), None, None),
    ("OlivierAlter Q43: context: fork for a noisy skill", OA, ("context: fork",), (), None, None),
    ("OlivierAlter Q34: isError pattern", OA, ('"isError": true',), (), None, None),
)


def community_report() -> list:
    rows = []
    for label, url, must, must_not, start, end in COMMUNITY:
        try:
            text = fetch(url)
            if start:
                i = text.index(start)
                j = text.index(end, i + 1) if end else len(text)
                text = text[i:j]
            ok = all(m in text for m in must) and not any(m in text for m in must_not)
            note = "" if ok else f"missing {[m for m in must if m not in text]} / unexpected {[m for m in must_not if m in text]}"
        except Exception as exc:
            ok, note = False, f"{type(exc).__name__}: {exc}"
        rows.append((label, ok, note))
    return rows


def main() -> int:
    failures = 0
    for title, rows in (("STRUCTURE", structure_report()), ("EVIDENCE (word-for-word, official pages)", evidence_report()),
                        ("COMMUNITY CLAIMS (raw GitHub files)", community_report())):
        print(f"\n== {title}")
        for label, ok, note in rows:
            print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f"   [{note}]" if note and not ok else ""))
            failures += 0 if ok else 1
    print(f"\n{'ALL CHECKS PASSED' if not failures else str(failures) + ' CHECK(S) FAILED'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
