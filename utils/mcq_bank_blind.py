"""Blind review helpers for the exam bank.
  export:  python -m utils.mcq_bank_blind export 1.1 OUTFILE     stems and options only, shuffled per question, no answers
  score:   python -m utils.mcq_bank_blind score 1.1 ANSWERFILE   ANSWERFILE lines: "Q1.1-01 B" using the exported letters
  options: python -m utils.mcq_bank_blind options 1.1 OUTFILE    the four options only, NO stem: a guessing test for structural tells
           (score it the same way; a rate far above 25% means the options give the answer away)

Options are shuffled with a fixed seed so a reviewer cannot learn anything from position; `score` maps the letters back.
"""

import random
import re
import sys

from utils import mcq_bank


def order(q) -> list:
    idx = list(range(4))
    random.Random(q.id).shuffle(idx)
    return idx


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    cmd, ts, path = sys.argv[1:4]
    mod = mcq_bank.load(only=ts)[ts]
    if cmd == "export":
        with open(path, "w", encoding="utf-8") as f:
            for q in mod.QUESTIONS:
                f.write(f"{q.id}\n{q.q}\n")
                for i, o in enumerate(order(q)):
                    f.write(f"  {'ABCD'[i]}) {q.opts[o]}\n")
                f.write("\n")
        print(f"exported {len(mod.QUESTIONS)} questions to {path}")
        return 0
    if cmd == "options":
        with open(path, "w", encoding="utf-8") as f:
            for q in mod.QUESTIONS:
                f.write(f"{q.id}\n")
                for i, o in enumerate(order(q)):
                    f.write(f"  {'ABCD'[i]}) {q.opts[o]}\n")
                f.write("\n")
        print(f"exported {len(mod.QUESTIONS)} option sets to {path}")
        return 0
    got = dict(re.findall(r"^(Q[\d.]+-\d+)\s+([ABCD])", open(path, encoding="utf-8").read(), re.M))
    miss = [q.id for q in mod.QUESTIONS if q.id not in got or order(q)["ABCD".index(got[q.id])] != q.ans]
    print(f"blind score {len(mod.QUESTIONS) - len(miss)} of {len(mod.QUESTIONS)}; disagreements: {miss}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
