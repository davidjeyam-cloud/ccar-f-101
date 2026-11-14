"""Export every BUILT concept page as static JSON for the React app: web/public/data/concepts/<slug>.json.
Called by scripts/export_web_data.py (so push.ps1 and deploy_web.ps1 keep it fresh). The Python content modules stay the single
source of truth; the JSON is generated, never hand-edited. Only what a static site can show is exported: the reading content,
the flowcharts (as Graphviz DOT), the code variants with their expected observations, the practice questions and the playground's
sub-concept descriptions. The runnable lab and playground need Python and stay in Streamlit."""
import importlib
import json
from pathlib import Path

from utils import concepts_map as cm
from utils.guide_index import point_ref, resolve_source
from utils import mock_claude


def _dot(fn):
    return fn({}) if callable(fn) else ""


def _question(q) -> dict:
    return {
        "q": q.q, "opts": list(q.opts), "ans": q.ans, "explain": q.explain,
        "scenarios": list(q.scenarios), "docs": q.basis == "docs",
        "tests": [point_ref(p.split(":")[0], p.split(":")[1][0], int(p.split(":")[1][1:])) for p in q.points],
    }


def _distractors(rows) -> list:
    out = []
    for name, looks, fails, instead, source in rows:
        out.append({"name": name, "looks": looks, "fails": fails, "instead": instead,
                    "source": resolve_source(source) if source else "", "exam": source.startswith("guide")})
    return out


def _grounding(items) -> list:
    return [{"text": c.text, "kind": c.kind, "ref": c.ref} for c in items]


def _related(slugs) -> list:
    out = []
    for s in slugs:
        c = cm.get(s)
        if c:
            out.append({"slug": s, "title": c.title, "built": cm.is_built(s)})
    return out


def _full(c, obj) -> dict:
    scen = []
    for sid in (obj.scenarios or ()):
        sc = mock_claude.SCENARIOS.get(sid)
        scen.append({"id": sid, "title": getattr(sc, "title", sid), "description": getattr(sc, "description", "")})
    return {
        "awareness": False,
        "tldr": obj.tldr, "mentalModel": obj.mental_model, "whatItIs": obj.what_it_is, "howItWorks": obj.how_it_works,
        "whereSeen": obj.where_seen, "guideNote": obj.guide_note,
        "docsRefs": [{"title": d.title, "url": d.url} for d in obj.docs_refs], "docsVerifiedOn": obj.docs_verified_on,
        "grounding": _grounding(obj.grounding),
        "examPoints": [{"ref": point_ref(p.ts, p.kind, p.n), "text": p.text, "lab": p.lab} for p in obj.exam_points],
        "flowDot": _dot(obj.flow_dot), "flowMermaid": obj.flow_mermaid, "flowMermaidKey": obj.flow_mermaid_key,
        "labIntro": obj.lab_intro, "labScenarios": scen,
        "variants": [{"key": v.key, "label": v.label, "kind": v.kind, "code": v.code, "scenario": v.scenario,
                      "observe": v.observe, "why": v.why, "fix": v.fix,
                      "source": resolve_source(v.source) if v.source else "", "exam": v.source.startswith("guide")}
                     for v in obj.variants],
        "distractors": _distractors(obj.distractors),
        "sideBySide": {"headers": list(obj.side_by_side_headers), "rows": [list(r) for r in obj.side_by_side_rows]},
        "decisionDot": obj.decision_dot, "experiments": list(obj.experiments),
        "questions": [_question(q) for q in obj.questions],
        "faq": [{"q": q, "a": a} for q, a in obj.faq], "related": _related(obj.related),
        "playgroundIntro": obj.playground_intro,
        "playground": [{"key": t.key, "label": t.label, "mentalModel": t.mental_model,
                        "exam": resolve_source(t.exam_source) if t.exam_source else "", "meaning": t.meaning, "docs": t.docs,
                        "examples": list(t.examples), "tryThis": list(t.try_this)} for t in obj.playground],
    }


def _awareness(c, obj) -> dict:
    return {
        "awareness": True,
        "tldr": obj.tldr, "mentalModel": obj.mental_model, "examNote": obj.exam_note, "whatItIs": obj.what_it_is,
        "notExaminable": obj.not_examinable, "guideNote": obj.guide_note,
        "docsRefs": [{"title": d.title, "url": d.url} for d in obj.docs_refs], "docsVerifiedOn": obj.docs_verified_on,
        "grounding": _grounding(obj.grounding),
        "distractors": _distractors(obj.distractors),
        "sideBySide": {"headers": list(obj.side_by_side_headers), "rows": [list(r) for r in obj.side_by_side_rows]},
        "questions": [_question(q) for q in obj.questions],
        "faq": [{"q": q, "a": a} for q, a in obj.faq], "related": _related(obj.related),
    }


def export(out_dir: Path) -> None:
    dest = out_dir / "concepts"
    dest.mkdir(parents=True, exist_ok=True)
    keep = set()
    total = 0
    for c in cm.CONCEPTS:
        if not cm.is_built(c.slug):
            continue
        mod = importlib.import_module(f"utils.concepts_content.{cm.content_module_name(c.slug)}")
        obj = getattr(mod, "CONTENT", None) or getattr(mod, "AWARENESS")
        body = _full(c, obj) if hasattr(obj, "flow_dot") else _awareness(c, obj)
        body.update({"slug": c.slug, "code": c.code, "title": c.title, "kind": cm.kind(c), "domain": c.domain,
                     "guide": cm.guide_alignment(c)})
        path = dest / f"{c.slug}.json"
        path.write_text(json.dumps(body, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        keep.add(path.name)
        total += path.stat().st_size
    for old in dest.glob("*.json"):          # a concept that is no longer built must not linger on the site
        if old.name not in keep:
            old.unlink()
    print(f"concepts/: {len(keep)} files, {total // 1024} KB")
