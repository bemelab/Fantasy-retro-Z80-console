"""Build the ZL-80 board PCB (zl80.kicad_pcb) from the parts and nets in gen_schematic.py.

Run it with KiCad's own Python, with KiCad's bin folder on PATH:

    set PATH=D:\\Program Files\\KiCad\\9.0\\bin;%PATH%
    "D:\\Program Files\\KiCad\\9.0\\bin\\python.exe" gen_pcb.py place       -> zl80.kicad_pcb (parts, planes) and zl80.dsn
    "D:\\Program Files\\KiCad\\9.0\\bin\\python.exe" gen_pcb.py import FILE  -> adds the tracks from a Freerouting .ses file

The board has 4 copper layers: F.Cu, In2.Cu and B.Cu carry tracks (+5V and +12V as 0.4 mm tracks), In1.Cu is a whole
GND plane that only GND vias reach, and a +5V zone fills what the tracks leave free on In2.Cu.
Part positions come from layout() below (millimetres, origin at the board's top-left corner).

Running "place" again replaces the board and drops the tracks; "import zl80.ses" puts them back while the
placement is unchanged.
"""
import os
import sys

import wx

wx.DisableAsserts()  # a failed internal check would otherwise open a modal "Debug Alert" window and wait
import pcbnew  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_schematic  # noqa: E402

LIBS = os.environ.get("KICAD9_FOOTPRINT_DIR", "D:/Program Files/KiCad/9.0/share/kicad/footprints")
PCB = os.path.join(HERE, "zl80.kicad_pcb")
mm = pcbnew.FromMM

# design rules: well inside JLCPCB's 4-layer limits
RULES = dict(clearance=0.15, track=0.2, power_track=0.5, via=0.6, via_drill=0.3, edge=0.5)
POWER_NETS = ("+5V", "GND", "+12V", "+12V_IN", "VBUS")


def parts():
    """(ref, value, footprint, {pad: net}) for every part, from the schematic generator."""
    proj = gen_schematic.build()
    for sh, _, _ in proj.pages:
        for ref, part, value, conn, fp in sh.placed:
            if not part.power:
                yield ref, value, fp, {num: net for num, net in conn.items() if net}


def load(fp):
    lib, name = fp.split(":", 1)
    f = pcbnew.FootprintLoad(os.path.join(LIBS, lib + ".pretty"), name)
    assert f is not None, fp
    return f


def outline(b, w, h, r=2.0):
    """Board edge: a rectangle w x h mm with rounded corners of radius r."""
    def seg(x1, y1, x2, y2):
        s = pcbnew.PCB_SHAPE(b)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
        s.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(mm(0.1))
        b.Add(s)

    def arc(cx, cy, sx, sy, ex, ey):
        a = pcbnew.PCB_SHAPE(b)
        a.SetShape(pcbnew.SHAPE_T_ARC)
        a.SetCenter(pcbnew.VECTOR2I(mm(cx), mm(cy)))
        a.SetStart(pcbnew.VECTOR2I(mm(sx), mm(sy)))
        a.SetEnd(pcbnew.VECTOR2I(mm(ex), mm(ey)))
        a.SetLayer(pcbnew.Edge_Cuts)
        a.SetWidth(mm(0.1))
        b.Add(a)

    seg(r, 0, w - r, 0)
    seg(w, r, w, h - r)
    seg(w - r, h, r, h)
    seg(0, h - r, 0, r)
    arc(w - r, r, w - r, 0, w, r)
    arc(w - r, h - r, w, h - r, w - r, h)
    arc(r, h - r, r, h, 0, h - r)
    arc(r, r, 0, r, r, 0)


def plane_style(z):
    """Settings for the GND and +5V planes. Small gaps keep the plane in one piece between rows of vias and pins."""
    z.SetLocalClearance(mm(0.2))
    z.SetMinThickness(mm(0.2))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(mm(0.2))
    z.SetThermalReliefSpokeWidth(mm(0.35))


def plane(b, net, layer, w, h):
    z = pcbnew.ZONE(b)
    z.SetLayer(layer)
    z.SetNet(net)
    plane_style(z)
    e = RULES["edge"]
    chain = pcbnew.SHAPE_LINE_CHAIN()
    for x, y in ((e, e), (w - e, e), (w - e, h - e), (e, h - e)):
        chain.Append(mm(x), mm(y))
    chain.SetClosed(True)
    z.Outline().AddOutline(chain)
    b.Add(z)


def rules(b):
    ds = b.GetDesignSettings()
    nc = ds.m_NetSettings.GetDefaultNetclass()
    nc.SetClearance(mm(RULES["clearance"]))
    nc.SetTrackWidth(mm(RULES["track"]))
    nc.SetViaDiameter(mm(RULES["via"]))
    nc.SetViaDrill(mm(RULES["via_drill"]))
    ds.m_CopperEdgeClearance = mm(RULES["edge"])
    ds.m_MinThroughDrill = mm(RULES["via_drill"])
    ds.m_HoleClearance = mm(0.15)
    power = pcbnew.NETCLASS("Power")  # 0.4 mm tracks for the supplies routed on the signal layers
    power.SetClearance(mm(RULES["clearance"]))
    power.SetTrackWidth(mm(0.4))
    power.SetViaDiameter(mm(RULES["via"]))
    power.SetViaDrill(mm(RULES["via_drill"]))
    ns = ds.m_NetSettings
    ns.SetNetclass("Power", power)
    for name in ("+5V", "+12V", "+12V_IN", "GND"):
        ns.SetNetclassPatternAssignment(name, "Power")  # KiCad's USB4105 footprint has 0.19 mm between its NPTH pegs and the GND pads


def bbox(f):
    """Footprint outline (pads and drawings, no text) in mm: left, top, right, bottom."""
    r = f.GetBoundingBox(False, False)
    return tuple(pcbnew.ToMM(v) for v in (r.GetLeft(), r.GetTop(), r.GetRight(), r.GetBottom()))


def move_box(f, left, top):
    """Move f so its outline's top-left corner is at (left, top)."""
    l, t, _, _ = bbox(f)
    p = f.GetPosition()
    f.SetPosition(pcbnew.VECTOR2I(p.x + mm(left - l), p.y + mm(top - t)))


class Packer:
    """Places parts left to right in rows inside a list of rectangles (x0, y0, x1, y1), filling one before the next."""

    def __init__(self, name, regions, gap=0.8):
        self.name, self.regions, self.gap = name, list(regions), gap
        self.state = [[x0, y0, 0.0] for x0, y0, _, _ in self.regions]  # per region: x, y, height of the current row

    def add(self, f):
        """Put f in the first region with room for it."""
        l, t, r, b = bbox(f)
        w, h = r - l, b - t
        for (x0, y0, x1, y1), st in zip(self.regions, self.state):
            x, y, row = st
            if x + w > x1 and x > x0:  # it would go in a new row
                x, y, row = x0, y + row + self.gap, 0.0
            if x + w <= x1 and y + h <= y1:
                move_box(f, x, y)
                st[:] = [x + w + self.gap, y, max(row, h)]
                return
        raise RuntimeError(f"{self.name}: no room left for {f.GetReference()} ({w:.1f} x {h:.1f} mm)")


# ---- placement --------------------------------------------------------------------------------------------------------
# Top edge, left to right: 12 V jack, 5 V regulator, USB-C, power parts, joystick 1 and 2. Below that one row of the four
# DIP-40 sockets: 82C55 (keyboard, USB), Z80 (memory, decoding), TMS9918A (VRAM, video), AY-3-8910 (sound, joysticks).
# The surface-mount parts of each group are packed beside and below its socket, each chip followed by its 100 nF.
W, H = 138.0, 105.0
DIP_TOP = 17.0                          # top of the DIP socket outlines
COLS = (1.0, 34.0, 77.0, 107.0, W - 1.0)  # group boundaries in x
DIP_X = (15.0, 34.5, 77.5, 107.5)        # left of each socket outline
DIP_W, DIP_H = 18.4, 51.5
LOW = DIP_TOP + DIP_H + 1.5             # top of the area below the sockets

GROUPS = {
    "keyboard and USB": ("U21", [(COLS[0], DIP_TOP, DIP_X[0] - 0.8, DIP_TOP + DIP_H), (COLS[0], LOW, COLS[1], H - 1)],
                         ["J8", "J7", "J6", "U22", "R12", "R13", "R14", "C5", "U23", "C38", "C36", "C37", "R48", "R49", "R50",
                          "R51", "R52", "C39", "U27", "U28"]),
    "CPU and memory": ("U1", [(DIP_X[1] + DIP_W + 0.8, DIP_TOP, COLS[2], DIP_TOP + DIP_H), (COLS[1], LOW, COLS[2], H - 1)],
                       ["U4", "U5", "U6", "U7", "U8", "U9", "U10", "U11", "JP1", "U2@90", "U3"] + [f"R{i}" for i in range(1, 12)]),
    "video": ("U15", [(DIP_X[2] + DIP_W + 0.8, DIP_TOP, COLS[3], DIP_TOP + DIP_H), (COLS[2], LOW, COLS[3], H - 1)],
              ["Y1@90", "C30", "C31", "D3", "U26", "Q1", "R25", "R26", "R27", "FB1", "C29", "U16", "U17", "U24", "U25"]),
    "sound and joysticks": ("U18", [(DIP_X[3] + DIP_W + 0.8, DIP_TOP, COLS[4], DIP_TOP + DIP_H), (COLS[3], LOW, COLS[4], H - 1)],
                            ["J2", "R28", "R29", "U12", "U19", "U20", "C1", "C2"] + [f"R{i}" for i in range(16, 25)]
                            + ["R30", "R31"] + [f"R{i}" for i in range(33, 48)]),
    "power": (None, [(41.0, 1.0, W - 1 - 10.4 - 33.0 - 21.5 - 1.0, DIP_TOP - 0.8)], ["U13", "SW1", "R15", "D1", "D2", "R32", "C3", "C4"]),
}


def layout(fps):
    """Position every footprint in fps (ref -> footprint)."""
    def at(ref, x, y, rot):
        fps[ref].SetOrientationDegrees(rot)
        fps[ref].SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))

    # edge connectors: the KiCad footprints put the board edge 7.70 mm (D-sub) and 3.1 mm (USB-C) past pin 1, toward +y
    at("J5", W - 1 - 10.4, 7.7, 180)
    at("J4", W - 1 - 10.4 - 33.0, 7.7, 180)
    at("J10", 34.0, 3.1, 180)
    fps["J1"].SetOrientationDegrees(270)  # barrel jack opening, -x in the footprint, turned to face the top edge
    move_box(fps["J1"], 1.0, -1.0)
    fps["U14"].SetOrientationDegrees(0)
    move_box(fps["U14"], 14.0, 1.0)
    for ref, x in zip(("U21", "U1", "U15", "U18"), DIP_X):
        at(ref, x + 1.6, DIP_TOP + 1.6, 0)  # pin 1 sits 1.6 mm inside the socket outline
    caps = {}
    for ref, f in fps.items():
        v = f.GetValue()
        if v.startswith("100n (") and v.endswith(")"):
            caps[v[6:-1]] = ref
    done = {"J1", "J4", "J5", "J10", "U14", "U21", "U1", "U15", "U18"}
    for name, (dip, regions, refs) in GROUPS.items():
        pk = Packer(name, regions)
        units = [[caps[dip]]] if dip else []  # the socket's own capacitor goes first, next to the socket
        first = []
        for ref in refs:  # "REF@deg" turns a part; parts listed before the socket's chips stay at the front
            if "@" in ref:
                ref, deg = ref.split("@")
                fps[ref].SetOrientationDegrees(float(deg))
        refs = [r.split("@")[0] for r in refs]
        if name == "video":  # the crystal and its capacitors go next to the TMS9918A's XTAL pins, before anything else
            first, refs = [["Y1"], ["C30"], ["C31"]], refs[3:]
        rest = [[r for r in (ref, caps.get(ref)) if r] for ref in refs]
        rest.sort(key=lambda u: -(bbox(fps[u[0]])[3] - bbox(fps[u[0]])[1]))  # tallest first: rows waste less space
        units += first
        for unit in units + rest:
            for ref in unit:
                assert ref not in done, ref
                pk.add(fps[ref])
                done.add(ref)
    left = sorted(set(fps) - done)
    assert not left, f"parts with no place: {left}"


def place():
    b = pcbnew.NewBoard(PCB)
    b.SetCopperLayerCount(4)
    rules(b)
    nets, fps, nofp = {}, {}, []

    def net(name):
        if name not in nets:
            nets[name] = pcbnew.NETINFO_ITEM(b, name)
            b.Add(nets[name])
        return nets[name]

    for ref, value, fp, conn in parts():
        if not fp:
            nofp.append(ref)
            continue
        f = load(fp)
        f.SetReference(ref)
        f.SetValue(value)
        b.Add(f)
        for pad in f.Pads():
            name = conn.get(pad.GetNumber())
            if name:
                pad.SetNet(net(name))
        fps[ref] = f
    assert not nofp, f"no footprint: {nofp}"
    layout(fps)
    outline(b, W, H)
    plane(b, net("GND"), pcbnew.In1_Cu, W, H)
    plane(b, net("+5V"), pcbnew.In2_Cu, W, H)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(PCB, b)
    dsn = os.path.join(HERE, "zl80.dsn")
    pcbnew.ExportSpecctraDSN(b, dsn)
    # Freerouting has to keep In1.Cu a whole GND plane but still connect GND pads to it with vias. Marking the layer
    # as a power layer stops it from connecting them, so In1.Cu stays a signal layer and every class except GND may
    # only use F.Cu, In2.Cu and B.Cu. +5V is routed as 0.4 mm tracks; the +5V zone then fills what is left of In2.Cu.
    text = open(dsn, encoding="utf-8").read()
    lines = text.split("\n")
    keep = [ln for ln in lines if not ln.strip().startswith("(plane +5V ")]
    assert len(keep) == len(lines) - 1, "no +5V plane line in the DSN"
    text = "\n".join(keep)
    old = "    (class Power +12V +12V_IN +5V GND\n"
    assert old in text
    text = text.replace(old, "    (class Power +12V +12V_IN +5V\n")
    ground = ("    (class Ground GND\n      (circuit\n        (use_via \"Via[0-3]_600:300_um\")\n      )\n"
              "      (rule\n        (width 400)\n        (clearance 150)\n      )\n    )\n")
    use = "      (circuit\n        (use_via \"Via[0-3]_600:300_um\")\n"
    n_use = text.count(use)
    assert n_use == 2, n_use  # the default class and Power
    text = text.replace(use, use + "        (use_layer F.Cu In2.Cu B.Cu)\n")
    text = text.replace("    (class Power +12V +12V_IN +5V\n", ground + "    (class Power +12V +12V_IN +5V\n")
    # Freerouting keeps only the track clearance from the board edge; give it a boundary inset by the edge clearance
    start = text.index("    (boundary\n")
    end = text.index("    )\n", start) + len("    )\n")
    e = int((RULES["edge"] + 0.05) * 1000)
    x1, y1 = int(W * 1000) - e, int(H * 1000) - e
    text = (text[:start] + f"    (boundary\n      (path pcb 0  {e} -{e}  {x1} -{e}  {x1} -{y1}  {e} -{y1}  {e} -{e})\n    )\n"
            + text[end:])
    open(dsn, "w", encoding="utf-8", newline="\n").write(text)


def import_ses(path):
    b = pcbnew.LoadBoard(PCB)
    if path:
        assert pcbnew.ImportSpecctraSES(b, path), path
    for z in b.Zones():
        plane_style(z)
        if z.GetNetname() == "+5V":  # In2.Cu: a fill between tracks, so pads join it solidly instead of by spokes
            z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(PCB, b)


if __name__ == "__main__":
    if sys.argv[1:2] == ["import"]:
        import_ses(sys.argv[2])
    elif sys.argv[1:2] == ["refill"]:  # apply the plane settings again and refill, keeping the tracks
        import_ses(None)
    else:
        place()
        print(f"placed on {W} x {H} mm")


