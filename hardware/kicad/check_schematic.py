"""Basic checks on the ZL-80 schematic without KiCad: every sheet file
parses, has no line break inside a string, keeps its symbols on its paper,
and every pin of every placed symbol is either labelled or marked as not
connected. It starts at zl80.kicad_sch and follows the sub-sheets.

    python check_schematic.py
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
TOKEN = re.compile(r'"(?:[^"\\]|\\.)*"|[()]|[^\s()"]+')


def parse(text):
    stack, cur = [], []
    for t in TOKEN.findall(text):
        if t == "(":
            stack.append(cur)
            cur = []
        elif t == ")":
            done, cur = cur, stack.pop()
            cur.append(done)
        else:
            cur.append(t[1:-1] if t.startswith('"') else t)
    assert not stack and len(cur) == 1, "unbalanced"
    return cur[0]


PAPER = {"A4": (297, 210), "A3": (420, 297), "A2": (594, 420), "A1": (841, 594)}


def check(name):
    """Check one sheet file; return (symbols, loose pins, sub-sheet files)."""
    text = open(os.path.join(HERE, name), encoding="utf-8").read()
    for t in TOKEN.findall(text):
        assert not (t.startswith('"') and "\n" in t), "line break inside a string (KiCad rejects it): " + t[:60]
    root = parse(text)
    assert root[0] == "kicad_sch"
    w, h = PAPER[next(x[1] for x in root if isinstance(x, list) and x[0] == "paper")]
    libs = {s[1]: s for s in next(x for x in root if x[0] == "lib_symbols")[1:]}
    syms = [x for x in root if isinstance(x, list) and x[0] == "symbol"]
    subs = [next(p[2] for p in x if isinstance(p, list) and p[0] == "property" and p[1] == "Sheetfile")
            for x in root if isinstance(x, list) and x[0] == "sheet"]
    ends = set()
    for x in root:
        if isinstance(x, list) and x[0] in ("label", "global_label", "no_connect"):
            at = next(a for a in x if isinstance(a, list) and a[0] == "at")
            ends.add((round(float(at[1]), 2), round(float(at[2]), 2)))
        if isinstance(x, list) and x[0] == "wire":
            for xy in x[1][1:]:
                ends.add((round(float(xy[1]), 2), round(float(xy[2]), 2)))
    loose = 0
    for s in syms:
        lib = libs[next(a for a in s if a[0] == "lib_id")[1]]
        at = next(a for a in s if a[0] == "at")
        x0, y0 = float(at[1]), float(at[2])
        assert 0 < x0 < w and 0 < y0 < h, (name, x0, y0)
        ref = next(a[2] for a in s if a[0] == "property" and a[1] == "Reference")
        for sub in lib[1:]:
            if isinstance(sub, list) and sub[0] == "symbol":
                for p in sub[2:]:
                    if p[0] == "pin":
                        pa = next(a for a in p if isinstance(a, list) and a[0] == "at")
                        pt = (round(x0 + float(pa[1]), 2), round(y0 - float(pa[2]), 2))
                        if pt not in ends:
                            print("loose pin", name, ref, next(a for a in p if isinstance(a, list) and a[0] == "number")[1])
                            loose += 1
    return len(syms), loose, subs


def main():
    todo, total, loose = ["zl80.kicad_sch"], 0, 0
    while todo:
        name = todo.pop(0)
        n_sym, n_loose, subs = check(name)
        print(f"{name}: {n_sym} symbols, {n_loose} loose pins")
        total, loose = total + n_sym, loose + n_loose
        todo += subs
    print(f"total: {total} symbols, {loose} loose pins")


if __name__ == "__main__":
    main()
