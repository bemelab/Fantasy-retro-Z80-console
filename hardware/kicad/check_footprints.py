"""Check every placed symbol against its KiCad footprint: the footprint must exist in the
KiCad library, and every symbol pin number must be a pad of that footprint. Pads that
have no symbol pin (for example a connector shell) are listed so they can be checked.

    python check_footprints.py ["D:/Program Files/KiCad/9.0/share/kicad/footprints"]
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_schematic  # noqa: E402

LIBS = sys.argv[1] if len(sys.argv) > 1 else "D:/Program Files/KiCad/9.0/share/kicad/footprints"
PAD = re.compile(r'\(pad\s+"([^"]*)"')


def pads(footprint):
    lib, name = footprint.split(":", 1)
    path = os.path.join(LIBS, lib + ".pretty", name + ".kicad_mod")
    if not os.path.exists(path):
        return None
    return {p for p in PAD.findall(open(path, encoding="utf-8").read()) if p}


def main():
    proj = gen_schematic.build()
    bad = 0
    for sh, _, _ in proj.pages:
        for ref, part, value, conn, fp in sh.placed:
            if part.power:
                continue
            if not fp:
                print(f"{ref:6} {part.name:22} no footprint")
                bad += 1
                continue
            have = pads(fp)
            if have is None:
                print(f"{ref:6} {part.name:22} footprint not in the library: {fp}")
                bad += 1
                continue
            missing = sorted(set(part.pins) - have)
            extra = sorted(have - set(part.pins))
            if missing:
                print(f"{ref:6} {part.name:22} pins with no pad: {missing}  ({fp})")
                bad += 1
            if extra:
                print(f"{ref:6} {part.name:22} pads with no pin (check): {extra}")
    print("footprint problems:", bad)
    return bad


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
