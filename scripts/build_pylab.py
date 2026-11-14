"""Packs the lab runtime for the browser: web/public/pylab/utils.zip holds utils/*.py (flat). Pyodide unpacks it into its
virtual file system and web/public/pylab/runner.py runs a learner program against it. Standard library only (checked
2026-11-14 for every lab, playground and core module), so Pyodide needs no extra packages."""
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "web" / "public" / "pylab" / "utils.zip"


def build() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    files = sorted((ROOT / "utils").glob("*.py")) + sorted((ROOT / "utils" / "concepts_content").glob("*.py"))
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(f, f.relative_to(ROOT).as_posix())   # utils/x.py and utils/concepts_content/y.py
    print(f"pylab/utils.zip: {len(files)} modules, {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    build()
