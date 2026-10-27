"""Small writer for KiCad 7 schematics (.kicad_sch), used by gen_schematic.py.

Every symbol is drawn as a box with its pins on the left and right. Each pin
gets a short wire and a net label, so connections are made by net names
rather than by drawn wires. A Project holds several pages: a net that appears
on more than one page gets global labels, the others local labels. The root
sheet shows one box per page. KiCad 7, 8 and 9 open the files.
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


PAPER = {"A4": (297, 210), "A3": (420, 297), "A2": (594, 420), "A1": (841, 594)}


class Sheet:
    """One page of the schematic."""

    def __init__(self, title, path, project="zl80"):
        self.title, self.path, self.project = title, path, project
        self.paper = "A3"
        self.parts, self.items, self.refs, self.labels, self.placed = {}, [], set(), [], []
        self.nets = {}  # net -> list of "REF.pin"
        self.extent = [0, 0]

    def add_text(self, x, y, text, size=1.8):
        self.items.append(f"(text {q(text)} (at {n(x)} {n(y)} 0) (effects (font (size {size} {size})) (justify left top))"
                          f" (uuid {q(uid('text', self.title, x, y, text))}))")

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
        self.placed.append((ref, part, value, conn, fp))  # for the PCB and the footprint check
        s = [f"(symbol (lib_id {q('zl80:' + part.name)}) (at {n(x)} {n(y)} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no)",
             f"  (uuid {q(uid('sym', ref))})",
             f"  (property \"Reference\" {q(ref)} (at {n(x)} {n(y - part.top - 3.81)} 0) {FONT_HIDE if part.power else FONT})",
             f"  (property \"Value\" {q(value)} (at {n(x)} {n(y - part.bottom + 3.81)} 0) {FONT})",
             f"  (property \"Footprint\" {q(fp)} (at {n(x)} {n(y)} 0) {FONT_HIDE})",
             f"  (property \"Datasheet\" {q(part.datasheet)} (at {n(x)} {n(y)} 0) {FONT_HIDE})"]
        for num in part.pins:
            s.append(f"  (pin {q(num)} (uuid {q(uid('pin', ref, num))}))")
        s.append(f"  (instances (project {q(self.project)} (path {q(self.path)} (reference {q(ref)}) (unit 1))))")
        s.append(")")
        self.items.append("\n".join(s))
        for num, (px, py, side, p) in part.pins.items():
            ax, ay = x + px, y - py  # schematic y grows downwards
            self.extent = [max(self.extent[0], ax + 40), max(self.extent[1], y - part.bottom + 8)]
            net = conn[num]
            if net is None:
                self.items.append(f"(no_connect (at {n(ax)} {n(ay)}) (uuid {q(uid('nc', ref, num))}))")
                continue
            self.nets.setdefault(net, []).append(f"{ref}.{num}")
            if part.power:
                self.labels.append((net, ax, ay, "R", ref, num))
                continue
            ex = ax - stub if side == "L" else ax + stub
            self.items.append(f"(wire (pts (xy {n(ax)} {n(ay)}) (xy {n(ex)} {n(ay)})) (stroke (width 0) (type default))"
                              f" (uuid {q(uid('w', ref, num))}))")
            self.labels.append((net, ex, ay, side, ref, num))

    @staticmethod
    def _label(net, x, y, side, ref, num, glob):
        ang, just = (180, "right") if side == "L" else (0, "left")
        u = q(uid("lbl", ref, num))
        if glob:  # the net reaches other pages
            return (f"(global_label {q(net)} (shape passive) (at {n(x)} {n(y)} {ang}) (fields_autoplaced)"
                    f" (effects (font (size 1.27 1.27)) (justify {just})) (uuid {u})"
                    f" (property \"Intersheetrefs\" \"${{INTERSHEET_REFS}}\" (at {n(x)} {n(y)} 0) {FONT_HIDE}))")
        return (f"(label {q(net)} (at {n(x)} {n(y)} {ang}) (fields_autoplaced)"
                f" (effects (font (size 1.27 1.27)) (justify {just} bottom)) (uuid {u}))")

    def text(self, file_uuid, global_nets, date="", rev="", comments=(), extra=(), root=False):
        out = ["(kicad_sch (version 20230121) (generator eeschema)", f"  (uuid {q(file_uuid)})", f"  (paper {q(self.paper)})",
               f"  (title_block (title {q(self.title)}) (date {q(date)}) (rev {q(rev)})"]
        for i, c in enumerate(comments, 1):
            out.append(f"    (comment {i} {q(c)})")
        out.append("  )")
        out.append("  (lib_symbols")
        for part in self.parts.values():
            out.append(part.lib())
        out.append("  )")
        out.extend(self.items)
        out.extend(self._label(*lb, lb[0] in global_nets) for lb in self.labels)
        out.extend(extra)
        if root:
            out.append("  (sheet_instances (path \"/\" (page \"1\")))")
        out.append(")")
        return "\n".join(out) + "\n"


class Project:
    """The root sheet plus one sub-sheet per page."""

    def __init__(self, title, name="zl80"):
        self.title, self.name = title, name
        self.root = uid("root", title)
        self.pages = []  # (sheet, file, sheet uuid)
        self.notes = []  # (x, y, text, size) on the root sheet

    def page(self, title, file):
        su = uid("sheet", file)
        sh = Sheet(title, f"/{self.root}/{su}", self.name)
        self.pages.append((sh, file, su))
        return sh

    @property
    def nets(self):
        out = {}
        for sh, _, _ in self.pages:
            for k, v in sh.nets.items():
                out.setdefault(k, []).extend(v)
        return out

    @property
    def refs(self):
        return set().union(*(sh.refs for sh, _, _ in self.pages))

    def write(self, folder, date="", rev="", comments=()):
        count = {}
        for sh, _, _ in self.pages:
            for k in sh.nets:
                count[k] = count.get(k, 0) + 1
        glob = {k for k, c in count.items() if c > 1}
        for sh, file, su in self.pages:
            w, h = sh.extent
            sh.paper = next(p for p in ("A3", "A2", "A1") if w <= PAPER[p][0] - 10 and h <= PAPER[p][1] - 40)
            with open(f"{folder}/{file}", "w", encoding="utf-8", newline="\n") as fh:
                fh.write(sh.text(uid("file", file), glob, date, rev, comments))
        boxes = []  # root sheet: a box per page, two columns
        for i, (sh, file, su) in enumerate(self.pages):
            x, y = 25.4 + (i % 2) * 127, 63.5 + (i // 2) * 38.1
            boxes.append(f"(sheet (at {n(x)} {n(y)}) (size 101.6 25.4) (fields_autoplaced)"
                         f" (stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0.0000)) (uuid {q(su)})"
                         f" (property \"Sheetname\" {q(sh.title)} (at {n(x)} {n(y - 0.7112)} 0)"
                         f" (effects (font (size 1.8 1.8)) (justify left bottom)))"
                         f" (property \"Sheetfile\" {q(file)} (at {n(x)} {n(y + 26.0112)} 0)"
                         f" (effects (font (size 1.27 1.27)) (justify left top)))"
                         f" (instances (project {q(self.name)} (path {q('/' + self.root)} (page {q(str(i + 2))})))))")
        root = Sheet(self.title, "/" + self.root, self.name)
        root.paper = "A4"
        for x, y, t, size in self.notes:
            root.add_text(x, y, t, size)
        with open(f"{folder}/{self.name}.kicad_sch", "w", encoding="utf-8", newline="\n") as fh:
            fh.write(root.text(self.root, glob, date, rev, comments, extra=boxes, root=True))
        return glob

    def write_library(self, folder):
        """Write the symbols as a project library and the sym-lib-table that points KiCad at it."""
        parts = {}
        for sh, _, _ in self.pages:
            parts.update(sh.parts)
        with open(f"{folder}/{self.name}.kicad_sym", "w", encoding="utf-8", newline="\n") as fh:
            fh.write("(kicad_symbol_lib (version 20220914) (generator gen_schematic)\n")
            for part in parts.values():
                fh.write(part.lib(prefix="") + "\n")
            fh.write(")\n")
        with open(f"{folder}/sym-lib-table", "w", encoding="utf-8", newline="\n") as fh:
            fh.write(f'(sym_lib_table\n  (version 7)\n  (lib (name "{self.name}")(type "KiCad")(uri "${{KIPRJMOD}}/{self.name}.kicad_sym")'
                     f'(options "")(descr "ZL-80 board symbols, written by gen_schematic.py"))\n)\n')


