"""Small writer for KiCad 7 schematics (.kicad_sch), used by gen_schematic.py.

Every symbol is drawn as a box with its pins on the left and right. Each pin
gets a short wire and a net label, so connections are made by net names
rather than by drawn wires. KiCad 7, 8 and 9 open the file.
"""
import uuid

GRID = 2.54
NS = uuid.UUID("6f1c2d8e-2a3b-4c5d-9e8f-7a6b5c4d3e2f")


def uid(*parts):
    return str(uuid.uuid5(NS, "/".join(str(p) for p in parts)))


def q(s):
    # KiCad strings stay on one line: a line break is written as \n
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def n(v):
    v = round(v, 4)
    return str(int(v)) if v == int(v) else repr(v)


FONT = "(effects (font (size 1.27 1.27)))"
FONT_HIDE = "(effects (font (size 1.27 1.27)) hide)"


class Part:
    """A schematic symbol: pins is a list of (number, name, side, type).

    side is "L" or "R"; a None entry leaves a gap on the left side, ("gap", "R") on the right.
    type is a KiCad pin type: passive, input, output, bidirectional, power_in, power_out ...
    """

    def __init__(self, name, pins, ref="U", footprint="", width=20.32, power=False, datasheet=""):
        self.name, self.ref, self.footprint, self.width, self.power = name, ref, footprint, width, power
        self.datasheet = datasheet
        self.left, self.right = [], []
        for p in pins:
            if p is None:
                self.left.append(None)
            elif p == ("gap", "R"):
                self.right.append(None)
            else:
                (self.left if p[2] == "L" else self.right).append(p)
        rows = max(len(self.left), len(self.right), 1)
        self.top = (rows - 1) * GRID / 2
        self.top = round(self.top / GRID) * GRID
        self.pins = {}  # number -> (x, y, side) in symbol coordinates (y up)
        for side, lst in (("L", self.left), ("R", self.right)):
            for i, p in enumerate(lst):
                if p is None:
                    continue
                x = -(width / 2 + GRID * 2) if side == "L" else width / 2 + GRID * 2
                self.pins[p[0]] = (x, self.top - i * GRID, side, p)
        self.bottom = self.top - (rows - 1) * GRID

    def lib(self, prefix="zl80:"):
        w2 = self.width / 2
        out = [f"(symbol {q(prefix + self.name)}" + (" (power)" if self.power else "")
               + " (pin_names (offset 1.016)) (in_bom yes) (on_board yes)"]
        out.append(f"  (property \"Reference\" {q(self.ref)} (at 0 {n(self.top + 3.81)} 0) {FONT})")
        out.append(f"  (property \"Value\" {q(self.name)} (at 0 {n(self.bottom - 3.81)} 0) {FONT})")
        out.append(f"  (property \"Footprint\" {q(self.footprint)} (at 0 0 0) {FONT_HIDE})")
        out.append(f"  (property \"Datasheet\" {q(self.datasheet)} (at 0 0 0) {FONT_HIDE})")
        if not self.power:
            out.append(f"  (symbol {q(self.name + '_0_1')} (rectangle (start {n(-w2)} {n(self.top + GRID)})"
                       f" (end {n(w2)} {n(self.bottom - GRID)}) (stroke (width 0.254) (type default)) (fill (type background))))")
        pins = []
        for num, (x, y, side, p) in self.pins.items():
            ang = 0 if side == "L" else 180
            hide = " hide" if self.power else ""
            pins.append(f"    (pin {p[3]} line (at {n(x)} {n(y)} {ang}) (length {n(0 if self.power else GRID * 2)}){hide}"
                        f" (name {q(p[1])} {FONT}) (number {q(num)} {FONT}))")
        out.append(f"  (symbol {q(self.name + '_1_1')}\n" + "\n".join(pins) + ")")
        out.append(")")
        return "\n".join(out)


class Sheet:
    def __init__(self, title, paper="A1", project="zl80"):
        self.title, self.paper, self.project = title, paper, project
        self.root = uid("root", title)
        self.parts, self.items, self.used, self.refs = {}, [], {}, set()
        self.nets = {}  # net -> list of "REF.pin"

    def add_text(self, x, y, text, size=1.8):
        self.items.append(f"(text {q(text)} (at {n(x)} {n(y)} 0) (effects (font (size {size} {size})) (justify left top))"
                          f" (uuid {q(uid('text', x, y, text))}))")

    def place(self, part, ref, value, x, y, conn, footprint=None, stub=GRID * 2):
        """Place part at (x, y). conn maps pin number -> net name, or None for a no-connect.
        Every pin of the part must be listed, so nothing is left floating by mistake."""
        assert ref not in self.refs, ref
        self.refs.add(ref)
        missing = set(part.pins) - set(conn)
        extra = set(conn) - set(part.pins)
        assert not missing and not extra, (ref, sorted(missing), sorted(extra))
        self.parts[part.name] = part
        x, y = round(x / GRID) * GRID, round(y / GRID) * GRID
        fp = part.footprint if footprint is None else footprint
        su = uid("sym", ref)
        s = [f"(symbol (lib_id {q('zl80:' + part.name)}) (at {n(x)} {n(y)} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no)",
             f"  (uuid {q(su)})",
             f"  (property \"Reference\" {q(ref)} (at {n(x)} {n(y - part.top - 3.81)} 0) {FONT_HIDE if part.power else FONT})",
             f"  (property \"Value\" {q(value)} (at {n(x)} {n(y - part.bottom + 3.81)} 0) {FONT})",
             f"  (property \"Footprint\" {q(fp)} (at {n(x)} {n(y)} 0) {FONT_HIDE})",
             f"  (property \"Datasheet\" {q(part.datasheet)} (at {n(x)} {n(y)} 0) {FONT_HIDE})"]
        for num in part.pins:
            s.append(f"  (pin {q(num)} (uuid {q(uid('pin', ref, num))}))")
        s.append(f"  (instances (project {q(self.project)} (path {q('/' + self.root)} (reference {q(ref)}) (unit 1))))")
        s.append(")")
        self.items.append("\n".join(s))
        for num, (px, py, side, p) in part.pins.items():
            ax, ay = x + px, y - py  # schematic y grows downwards
            net = conn[num]
            if net is None:
                self.items.append(f"(no_connect (at {n(ax)} {n(ay)}) (uuid {q(uid('nc', ref, num))}))")
                continue
            self.nets.setdefault(net, []).append(f"{ref}.{num}")
            if part.power:
                self.items.append(self._label(net, ax, ay, "R", ref, num))
                continue
            ex = ax - stub if side == "L" else ax + stub
            self.items.append(f"(wire (pts (xy {n(ax)} {n(ay)}) (xy {n(ex)} {n(ay)})) (stroke (width 0) (type default))"
                              f" (uuid {q(uid('w', ref, num))}))")
            self.items.append(self._label(net, ex, ay, side, ref, num))

    def _label(self, net, x, y, side, ref, num):
        ang, just = (180, "right bottom") if side == "L" else (0, "left bottom")
        return (f"(label {q(net)} (at {n(x)} {n(y)} {ang}) (fields_autoplaced)"
                f" (effects (font (size 1.27 1.27)) (justify {just})) (uuid {q(uid('lbl', ref, num))}))")

    def write(self, path, date="", rev="", comments=()):
        out = ["(kicad_sch (version 20230121) (generator eeschema)", f"  (uuid {q(self.root)})", f"  (paper {q(self.paper)})",
               f"  (title_block (title {q(self.title)}) (date {q(date)}) (rev {q(rev)})"]
        for i, c in enumerate(comments, 1):
            out.append(f"    (comment {i} {q(c)})")
        out.append("  )")
        out.append("  (lib_symbols")
        for part in self.parts.values():
            out.append(part.lib())
        out.append("  )")
        out.extend(self.items)
        out.append(f"  (sheet_instances (path \"/\" (page \"1\")))")
        out.append(")")
        text = "\n".join(out) + "\n"
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        return text

    def write_library(self, folder, name="zl80"):
        """Write the symbols as a project library and the sym-lib-table that points KiCad at it."""
        with open(f"{folder}/{name}.kicad_sym", "w", encoding="utf-8", newline="\n") as fh:
            fh.write("(kicad_symbol_lib (version 20220914) (generator gen_schematic)\n")
            for part in self.parts.values():
                fh.write(part.lib(prefix="") + "\n")
            fh.write(")\n")
        with open(f"{folder}/sym-lib-table", "w", encoding="utf-8", newline="\n") as fh:
            fh.write(f'(sym_lib_table\n  (version 7)\n  (lib (name "{name}")(type "KiCad")(uri "${{KIPRJMOD}}/{name}.kicad_sym")'
                     f'(options "")(descr "ZL-80 board symbols, written by gen_schematic.py"))\n)\n')
