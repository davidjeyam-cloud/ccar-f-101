"""Export the course data the React app (web/) reads as static JSON: the exam question bank, the course map and the concept list.
Run from the repo root:  python scripts/export_web_data.py
The Python modules stay the single source of truth; web/public/data/*.json is generated, never hand-edited."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from utils import concepts_map as cm, mcq_bank, mock_exam
from utils.course_map import DOMAINS, PHASES, SCENARIOS
from utils.guide_index import SCENARIO_NAME, pages, point_ref
from utils.mcq_bank.principles import PRINCIPLES

OUT = ROOT / "web" / "public" / "data"
OUT.mkdir(parents=True, exist_ok=True)


def write(name: str, data) -> None:
    path = OUT / name
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{name}: {path.stat().st_size // 1024} KB")


bank = mcq_bank.load()
questions = []
for ts, mod in bank.items():
    for q in mod.QUESTIONS:
        questions.append({
            "id": q.id, "ts": ts, "domain": int(ts.split(".")[0]), "scenarios": list(q.scenarios),
            "q": q.q, "opts": list(q.opts), "ans": q.ans, "explain": q.explain,
            "tests": [point_ref(p.split(":")[0], p.split(":")[1][0], int(p.split(":")[1][1:])) for p in q.points],
            "bullets": [mod.BULLETS[p.split(":")[1]] for p in q.points if p.split(":")[1] in mod.BULLETS],
            "principle": PRINCIPLES.get(q.principle, ""), "level": q.level, "docs": q.basis == "docs",
        })
write("bank.json", {"questions": questions})

task_statements = []
for domain, (dname, weight, _) in DOMAINS.items():
    for e in (x for entries in PHASES.values() for x in entries if x.domain == domain and x.task_statement):
        ts = e.task_statement
        task_statements.append({
            "ts": ts, "title": e.title.split(" ", 1)[1], "domain": domain, "pages": pages(ts),
            "labs": [c.code for c in cm.CONCEPTS if ts in c.guide_refs and c.code and cm.is_built(c.slug)],
            "pending": [c.title for c in cm.CONCEPTS if ts in c.guide_refs and not c.code and cm.kind(c) == "exam" and not cm.is_built(c.slug)],
            "questions": len(bank[ts].QUESTIONS) if ts in bank else 0,
        })

concepts = [{
    "slug": c.slug, "code": c.code, "title": c.title, "domain": c.domain, "kind": cm.kind(c), "status": c.status,
    "built": cm.is_built(c.slug), "guide": cm.guide_alignment(c),
} for c in cm.CONCEPTS]

write("course.json", {
    "domains": [{"n": d, "name": n, "weight": w} for d, (n, w, _) in DOMAINS.items()],
    "taskStatements": task_statements,
    "scenarios": [{"n": n, "name": SCENARIO_NAME[n]} for n in sorted(SCENARIO_NAME)],
    "concepts": concepts,
    "mock": {"items": mock_exam.ITEMS, "minutes": mock_exam.MINUTES, "weights": mock_exam.WEIGHTS,
             "passScaled": mock_exam.PASS_SCALED, "scaleNote": mock_exam.SCALE_NOTE},
})
