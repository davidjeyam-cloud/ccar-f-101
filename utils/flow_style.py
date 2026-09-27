"""
Readable sizing for concept flowcharts and decision trees (FLOWCHART RULE in CLAUDE.md; user, 2026-09-28, approved on
D1.2): node text 18pt, edge labels 16pt, key text 16pt, and at most 2 nodes per row.

Why: st.graphviz_chart scales a chart to the column width, so a wide chart shrinks its text until it can't be read. A tall,
narrow chart keeps its text size and the page simply scrolls. D1.2's approved chart is about 615 px at its widest row.

readable(dot) post-processes a DOT string:
- node / edge font sizes and the colour key's cell and font sizes;
- any node with more than 2 visible children that aren't already grouped gets its children grouped (a fan-out would
  otherwise put them all side by side);
- every `{ rank=same; ... }` group is re-cut into rows of at most 2 nodes — and a single node when the pair would be wider
  than ROW_BUDGET_PX (estimated from label length) — stacked with invisible edges.
It leaves labels, colours, real edges and node ids alone, so node_states() highlighting keeps working.
"""

from __future__ import annotations

import re

NODE_PT, EDGE_PT, KEY_PT, KEY_TITLE_PT, PER_ROW = 18, 16, 16, 18, 2
ROW_BUDGET_PX = 720

_RANK = re.compile(r"\{\s*rank\s*=\s*same\s*;([^{}]*)\}")
_EDGE = re.compile(r"(\w+)\s*->\s*(\w+)\s*(\[[^\]]*\])?")


def _label_chars(dot: str) -> dict:
    out = {}
    for m in re.finditer(r'^\s*(\w+)\s*\[label="((?:[^"\\]|\\.)*)"', dot, re.M):
        out[m.group(1)] = max(len(x) for x in m.group(2).split("\\n"))
    return out


def _px(chars: int) -> float:
    return (chars * NODE_PT * 0.55 + 30) * 1.333          # rough Helvetica width at 18pt, plus margins


def _rows(names: list, lab: dict) -> list:
    rows, cur = [], []
    for n in names:
        trial = cur + [n]
        width = sum(_px(lab.get(x, 12)) for x in trial) + (len(trial) - 1) * 34
        if cur and (len(trial) > PER_ROW or width > ROW_BUDGET_PX):
            rows.append(cur)
            cur = [n]
        else:
            cur = trial
    return rows + ([cur] if cur else [])


def _group_fanouts(dot: str) -> str:
    grouped = {n.strip() for g in _RANK.findall(dot) for n in g.split(";") if n.strip()}
    kids = {}
    for m in _EDGE.finditer(dot):
        if m.group(3) and ("invis" in m.group(3) or "constraint=false" in m.group(3)):
            continue
        kids.setdefault(m.group(1), [])
        if m.group(2) not in kids[m.group(1)]:
            kids[m.group(1)].append(m.group(2))
    extra = []
    for parent, ch in kids.items():
        free = [c for c in ch if c not in grouped]
        if len(free) > PER_ROW:
            extra.append("{ rank=same; " + "; ".join(free) + "; }")
            grouped.update(free)
    if not extra:
        return dot
    i = dot.rstrip().rfind("}")
    return dot[:i] + "  " + "\n  ".join(extra) + "\n" + dot[i:]


def readable(dot: str) -> str:
    s = re.sub(r"(node\s*\[[^\]]*?)fontsize\s*=\s*\d+", rf'\g<1>fontsize={NODE_PT}, margin="0.2,0.1"', dot)
    s = re.sub(r"(edge\s*\[[^\]]*?)fontsize\s*=\s*\d+", rf"\g<1>fontsize={EDGE_PT}, penwidth=1.5", s)
    s = re.sub(r'POINT-SIZE="1[0-2]"', f'POINT-SIZE="{KEY_PT}"', s)
    s = s.replace('WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14"', 'WIDTH="26" FIXEDSIZE="TRUE" HEIGHT="20"')
    s = s.replace("<B>Key</B>", f'<FONT POINT-SIZE="{KEY_TITLE_PT}"><B>Key</B></FONT>')
    s = s.replace('HEIGHT="20">⭐</TD>', f'HEIGHT="20"><FONT POINT-SIZE="{KEY_PT}">⭐</FONT></TD>')
    s = re.sub(r"nodesep\s*=\s*[\d.]+", "nodesep=0.35", s)
    s = _group_fanouts(s)
    lab = _label_chars(s)

    def split(m: re.Match) -> str:
        names = [n.strip() for n in m.group(1).split(";") if n.strip()]
        rows = _rows(names, lab)
        if len(rows) == 1:
            return "{ rank=same; " + "; ".join(names) + "; }"
        out = ["{ rank=same; " + "; ".join(r) + "; }" for r in rows]
        for upper, lower in zip(rows, rows[1:]):
            for j, node in enumerate(lower):
                out.append(f"{upper[min(j, len(upper) - 1)]} -> {node} [style=invis];")
        return " ".join(out)

    return _RANK.sub(split, s)


def max_row(dot: str) -> int:
    """Largest rank=same group left after readable() — used by the tests."""
    return max((len([n for n in m.group(1).split(";") if n.strip()]) for m in _RANK.finditer(dot)), default=0)


def widest_row_px(dot: str) -> int:
    """Estimated width of the widest rank=same row — used by the tests (D1.2's approved chart: about 615 px)."""
    lab = _label_chars(dot)
    rows = [[n.strip() for n in g.split(";") if n.strip()] for g in _RANK.findall(dot)]
    return int(max((sum(_px(lab.get(n, 12)) for n in r) + (len(r) - 1) * 34 for r in rows), default=0))
