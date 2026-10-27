"""Generate the ZL-80 board schematic (docs/hardware.md) for KiCad.

    python gen_schematic.py

writes zl80.kicad_sch and zl80-netlist.txt next to this file. Connections are
made by net labels; zl80-netlist.txt lists every net with the pins on it, for
checking against the datasheets.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sch import Part, Sheet  # noqa: E402
P, I, O, B, PI, PO, OC = "passive", "input", "output", "bidirectional", "power_in", "power_out", "open_collector"
DIP = lambda n, w=7.62: f"Package_DIP:DIP-{n}_W{w:.2f}mm"
DIP6 = lambda n: DIP(n, 15.24)


def L(num, name, t=P):
    return (str(num), name, "L", t)


def R(num, name, t=P):
    return (str(num), name, "R", t)


# ---- parts ------------------------------------------------------------------------------------------------------
Z80 = Part("Z80_CPU", [L(30, "A0"), L(31, "A1"), L(32, "A2"), L(33, "A3"), L(34, "A4"), L(35, "A5"), L(36, "A6"), L(37, "A7"),
                       L(38, "A8"), L(39, "A9"), L(40, "A10"), L(1, "A11"), L(2, "A12"), L(3, "A13"), L(4, "A14"), L(5, "A15"),
                       None, L(6, "CLK", I), L(26, "~{RESET}", I), L(16, "~{INT}", I), L(17, "~{NMI}", I), L(24, "~{WAIT}", I),
                       L(25, "~{BUSRQ}", I), None, L(11, "VCC", PI), L(29, "GND", PI),
                       R(14, "D0", B), R(15, "D1", B), R(12, "D2", B), R(8, "D3", B), R(7, "D4", B), R(9, "D5", B), R(10, "D6", B),
                       R(13, "D7", B), ("gap", "R"), R(27, "~{M1}", O), R(19, "~{MREQ}", O), R(20, "~{IORQ}", O), R(21, "~{RD}", O),
                       R(22, "~{WR}", O), R(28, "~{RFSH}", O), R(18, "~{HALT}", O), R(23, "~{BUSACK}", O)],
           footprint=DIP6(40), width=22.86)

TMS = Part("TMS9918A", [L(24, "CD0 (MSB)", B), L(23, "CD1", B), L(22, "CD2", B), L(21, "CD3", B), L(20, "CD4", B), L(19, "CD5", B),
                         L(18, "CD6", B), L(17, "CD7 (LSB)", B), None, L(13, "MODE", I), L(14, "~{CSW}", I), L(15, "~{CSR}", I),
                         L(16, "~{INT}", O), L(34, "~{RESET}/SYNC", I), None, L(39, "XTAL1", I), L(40, "XTAL2", P),
                         L(38, "CPUCLK", O), L(37, "GROMCLK", O), None, L(33, "VCC", PI), L(12, "VSS", PI),
                         R(10, "AD0", O), R(9, "AD1", O), R(8, "AD2", O), R(7, "AD3", O), R(6, "AD4", O), R(5, "AD5", O),
                         R(4, "AD6", O), R(3, "AD7", O), ("gap", "R"), R(32, "RD0", I), R(31, "RD1", I), R(30, "RD2", I),
                         R(29, "RD3", I), R(28, "RD4", I), R(27, "RD5", I), R(26, "RD6", I), R(25, "RD7", I), ("gap", "R"),
                         R(1, "~{RAS}", O), R(2, "~{CAS}", O), R(11, "R/~{W}", O), ("gap", "R"), R(36, "COMVID", O),
                         R(35, "EXTVDP", I)],
           footprint=DIP6(40), width=25.4)

AY = Part("AY-3-8910", [L(37, "DA0", B), L(36, "DA1", B), L(35, "DA2", B), L(34, "DA3", B), L(33, "DA4", B), L(32, "DA5", B),
                         L(31, "DA6", B), L(30, "DA7", B), None, L(27, "BDIR", I), L(29, "BC1", I), L(28, "BC2", I),
                         L(25, "A8", I), L(24, "~{A9}", I), L(23, "~{RESET}", I), L(22, "CLOCK", I), None,
                         L(39, "TEST1", P), L(26, "TEST2", P), None, L(40, "VCC", PI), L(1, "VSS", PI),
                         R(4, "ANALOG A", O), R(3, "ANALOG B", O), R(38, "ANALOG C", O), ("gap", "R"),
                         R(21, "IOA0", B), R(20, "IOA1", B), R(19, "IOA2", B), R(18, "IOA3", B), R(17, "IOA4", B),
                         R(16, "IOA5", B), R(15, "IOA6", B), R(14, "IOA7", B), ("gap", "R"),
                         R(13, "IOB0", B), R(12, "IOB1", B), R(11, "IOB2", B), R(10, "IOB3", B), R(9, "IOB4", B),
                         R(8, "IOB5", B), R(7, "IOB6", B), R(6, "IOB7", B), R(2, "NC", P), R(5, "NC", P)],
          footprint=DIP6(40), width=25.4)

PPI = Part("82C55A", [L(34, "D0", B), L(33, "D1", B), L(32, "D2", B), L(31, "D3", B), L(30, "D4", B), L(29, "D5", B),
                       L(28, "D6", B), L(27, "D7", B), None, L(6, "~{CS}", I), L(5, "~{RD}", I), L(36, "~{WR}", I),
                       L(9, "A0", I), L(8, "A1", I), L(35, "RESET", I), None, L(26, "VCC", PI), L(7, "GND", PI),
                       R(4, "PA0", B), R(3, "PA1", B), R(2, "PA2", B), R(1, "PA3", B), R(40, "PA4", B), R(39, "PA5", B),
                       R(38, "PA6", B), R(37, "PA7", B), ("gap", "R"),
                       R(18, "PB0", B), R(19, "PB1", B), R(20, "PB2", B), R(21, "PB3", B), R(22, "PB4", B), R(23, "PB5", B),
                       R(24, "PB6", B), R(25, "PB7", B), ("gap", "R"),
                       R(14, "PC0", B), R(15, "PC1", B), R(16, "PC2", B), R(17, "PC3", B), R(13, "PC4", B), R(12, "PC5", B),
                       R(11, "PC6", B), R(10, "PC7", B)],
           footprint=DIP6(40), width=22.86)

ACIA = Part("MC68B50", [L(22, "D0", B), L(21, "D1", B), L(20, "D2", B), L(19, "D3", B), L(18, "D4", B), L(17, "D5", B),
                         L(16, "D6", B), L(15, "D7", B), None, L(8, "CS0", I), L(10, "CS1", I), L(9, "~{CS2}", I),
                         L(11, "RS", I), L(13, "R/~{W}", I), L(14, "E", I), L(7, "~{IRQ}", OC), None,
                         L(12, "VCC", PI), L(1, "VSS", PI),
                         R(4, "TXCLK", I), R(3, "RXCLK", I), ("gap", "R"), R(6, "TXDATA", O), R(2, "RXDATA", I),
                         R(5, "~{RTS}", O), R(24, "~{CTS}", I), R(23, "~{DCD}", I)],
            footprint=DIP6(24), width=22.86)

PAGE = Part("74HCT670", [L(15, "D0", I), L(1, "D1", I), L(2, "D2", I), L(3, "D3", I), None, L(14, "WA0", I), L(13, "WA1", I),
                          L(12, "~{WE}", I), None, L(5, "RA0", I), L(4, "RA1", I), L(11, "~{RE}", I), None,
                          L(16, "VCC", PI), L(8, "GND", PI),
                          R(10, "Q0", O), R(9, "Q1", O), R(7, "Q2", O), R(6, "Q3", O)], footprint=DIP(16))

MEM32 = lambda name, special: Part(name, [
    L(12, "A0", I), L(11, "A1", I), L(10, "A2", I), L(9, "A3", I), L(8, "A4", I), L(7, "A5", I), L(6, "A6", I), L(5, "A7", I),
    L(27, "A8", I), L(26, "A9", I), L(23, "A10", I), L(25, "A11", I), L(4, "A12", I), L(28, "A13", I),
    L(special["A14"], "A14", I), L(special["A15"], "A15", I), L(2, "A16", I), L(30, "A17", I), L(1, "A18", I), None,
    L(32, "VCC", PI), L(16, "VSS", PI),
    R(13, "DQ0", B), R(14, "DQ1", B), R(15, "DQ2", B), R(17, "DQ3", B), R(18, "DQ4", B), R(19, "DQ5", B), R(20, "DQ6", B),
    R(21, "DQ7", B), ("gap", "R"), R(22, "~{CE}", I), R(24, "~{OE}", I), R(special["WE"], "~{WE}", I)],
    footprint=DIP6(32), width=22.86)
FLASH = MEM32("SST39SF040", {"A14": 29, "A15": 3, "WE": 31})
SRAM = MEM32("AS6C4008", {"A14": 3, "A15": 31, "WE": 29})

SRAM32K = Part("62256", [L(10, "A0", I), L(9, "A1", I), L(8, "A2", I), L(7, "A3", I), L(6, "A4", I), L(5, "A5", I),
                          L(4, "A6", I), L(3, "A7", I), L(25, "A8", I), L(24, "A9", I), L(21, "A10", I), L(23, "A11", I),
                          L(2, "A12", I), L(26, "A13", I), L(1, "A14", I), None, L(28, "VCC", PI), L(14, "GND", PI),
                          R(11, "D0", B), R(12, "D1", B), R(13, "D2", B), R(15, "D3", B), R(16, "D4", B), R(17, "D5", B),
                          R(18, "D6", B), R(19, "D7", B), ("gap", "R"), R(20, "~{CS}", I), R(22, "~{OE}", I), R(27, "~{WE}", I)],
                footprint=DIP6(28), width=22.86)
HC574 = Part("74HCT574", [L(2, "D0", I), L(3, "D1", I), L(4, "D2", I), L(5, "D3", I), L(6, "D4", I), L(7, "D5", I), L(8, "D6", I),
                           L(9, "D7", I), None, L(11, "CLK", I), L(1, "~{OE}", I), None, L(20, "VCC", PI), L(10, "GND", PI),
                           R(19, "Q0", O), R(18, "Q1", O), R(17, "Q2", O), R(16, "Q3", O), R(15, "Q4", O), R(14, "Q5", O),
                           R(13, "Q6", O), R(12, "Q7", O)], footprint=DIP(20))

MCU = Part("ATmega328P", [L(1, "PC6/~{RESET}", I), None, L(23, "PC0", B), L(24, "PC1", B), L(25, "PC2", B), L(26, "PC3", B),
                           L(27, "PC4", B), L(28, "PC5", B), None, L(14, "PB0", B), L(15, "PB1", B), L(16, "PB2", B),
                           L(17, "PB3/MOSI", B), L(18, "PB4/MISO", B), L(19, "PB5/SCK", B), L(9, "PB6/XTAL1", B),
                           L(10, "PB7/XTAL2", B), None, L(7, "VCC", PI), L(20, "AVCC", PI), L(21, "AREF", P),
                           L(8, "GND", PI), L(22, "GND", PI),
                           R(2, "PD0", B), R(3, "PD1", B), R(4, "PD2", B), R(5, "PD3", B), R(6, "PD4", B), R(11, "PD5", B),
                           R(12, "PD6", B), R(13, "PD7", B)], footprint=DIP(28), width=22.86)

HC138 = Part("74HCT138", [L(1, "A", I), L(2, "B", I), L(3, "C", I), None, L(6, "G1", I), L(4, "~{G2A}", I), L(5, "~{G2B}", I),
                           None, L(16, "VCC", PI), L(8, "GND", PI),
                           R(15, "~{Y0}", O), R(14, "~{Y1}", O), R(13, "~{Y2}", O), R(12, "~{Y3}", O), R(11, "~{Y4}", O),
                           R(10, "~{Y5}", O), R(9, "~{Y6}", O), R(7, "~{Y7}", O)], footprint=DIP(16))
HC157 = Part("74HCT157", [L(1, "S", I), L(15, "~{E}", I), None, L(2, "1A", I), L(3, "1B", I), L(5, "2A", I), L(6, "2B", I),
                           L(11, "3A", I), L(10, "3B", I), L(14, "4A", I), L(13, "4B", I), None, L(16, "VCC", PI),
                           L(8, "GND", PI), R(4, "1Y", O), R(7, "2Y", O), R(9, "3Y", O), R(12, "4Y", O)], footprint=DIP(16))
HC74 = Part("74HCT74", [L(2, "1D", I), L(3, "1CLK", I), L(4, "~{1PRE}", I), L(1, "~{1CLR}", I), None,
                         L(12, "2D", I), L(11, "2CLK", I), L(10, "~{2PRE}", I), L(13, "~{2CLR}", I), None,
                         L(14, "VCC", PI), L(7, "GND", PI),
                         R(5, "1Q", O), R(6, "~{1Q}", O), ("gap", "R"), ("gap", "R"), ("gap", "R"), R(9, "2Q", O),
                         R(8, "~{2Q}", O)], footprint=DIP(14))
QUAD2 = lambda name, g: Part(name, [L(1, "1A", I), L(2, "1B", I), L(4, "2A", I), L(5, "2B", I), L(9, "3A", I), L(10, "3B", I),
                                     L(12, "4A", I), L(13, "4B", I), None, L(14, "VCC", PI), L(7, "GND", PI),
                                     R(3, f"1Y={g}", O), R(6, f"2Y={g}", O), R(8, f"3Y={g}", O), R(11, f"4Y={g}", O)],
                             footprint=DIP(14))
HC32 = QUAD2("74HCT32", "1A|1B")
HC02 = Part("74HCT02", [L(2, "1A", I), L(3, "1B", I), L(5, "2A", I), L(6, "2B", I), L(8, "3A", I), L(9, "3B", I), L(11, "4A", I),
                         L(12, "4B", I), None, L(14, "VCC", PI), L(7, "GND", PI),
                         R(1, "1Y=~{1A|1B}", O), R(4, "2Y", O), R(10, "3Y", O), R(13, "4Y", O)], footprint=DIP(14))
HC04 = Part("74HCT04", [L(1, "1A", I), L(3, "2A", I), L(5, "3A", I), L(9, "4A", I), L(11, "5A", I), L(13, "6A", I), None,
                         L(14, "VCC", PI), L(7, "GND", PI),
                         R(2, "1Y=~{1A}", O), R(4, "2Y", O), R(6, "3Y", O), R(8, "4Y", O), R(10, "5Y", O), R(12, "6Y", O)],
            footprint=DIP(14))

DS1813 = Part("DS1813", [L(2, "VCC", PI), L(3, "GND", PI), R(1, "~{RST}", OC)], footprint="Package_TO_SOT_THT:TO-92_Inline",
              width=15.24)
OSC = Part("Oscillator_DIP14", [L(14, "VCC", PI), L(7, "GND", PI), L(1, "EN/NC", P), R(8, "OUT", O)],
           footprint="Oscillator:Oscillator_DIP-14", width=17.78)
REG = Part("Regulator_5V", [L(1, "VIN", PI), L(2, "GND", PI), R(3, "VOUT", PO)], footprint="Package_TO_SOT_THT:TO-220-3_Vertical",
           width=15.24)
RES = Part("R", [L(1, "~"), R(2, "~")], ref="R", footprint="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal",
           width=5.08)
CAP = Part("C", [L(1, "~"), R(2, "~")], ref="C", footprint="Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm", width=5.08)
CPOL = Part("C_Polarized", [L(1, "+"), R(2, "-")], ref="C", footprint="Capacitor_THT:CP_Radial_D6.3mm_P2.50mm", width=5.08)
XTAL = Part("Crystal", [L(1, "1"), R(2, "2")], ref="Y", footprint="Crystal:Crystal_HC49-4H_Vertical", width=5.08)
FBEAD = Part("Ferrite_Bead", [L(1, "1"), R(2, "2")], ref="FB", footprint="Inductor_THT:L_Axial_L5.3mm_D2.2mm_P7.62mm_Horizontal_Vishay_IM-1",
              width=5.08)
DIODE = Part("D", [L(1, "K"), R(2, "A")], ref="D", footprint="Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal", width=5.08)
LED = Part("LED", [L(1, "K"), R(2, "A")], ref="D", footprint="LED_THT:LED_D3.0mm", width=5.08)
NPN = Part("NPN_BCE", [L(2, "B"), R(1, "C"), R(3, "E")], ref="Q", footprint="Package_TO_SOT_THT:TO-92_Inline", width=7.62)
BTN = Part("SW_Push", [L(1, "1"), R(2, "2")], ref="SW", footprint="Button_Switch_THT:SW_PUSH_6mm", width=5.08)
JMP = Part("Jumper_2", [L(1, "1"), R(2, "2")], ref="JP", footprint="Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
           width=5.08)
RNET = Part("R_Network08", [L(1, "COMMON")] + [R(i, f"R{i - 1}") for i in range(2, 10)], ref="RN",
            footprint="Resistor_THT:R_Array_SIP9", width=10.16)
PWR_FLAG = Part("PWR_FLAG", [L(1, "pwr", PO)], ref="#FLG", power=True)


def conn_part(name, pins, footprint=""):
    return Part(name, [L(num, nm) for num, nm in pins], ref="J", footprint=footprint, width=15.24)


SCART = conn_part("SCART", [(1, "Audio R out"), (2, "Audio R in"), (3, "Audio L out"), (4, "Audio GND"), (5, "Blue GND"),
                            (6, "Audio L in"), (7, "Blue"), (8, "Function switch"), (9, "Green GND"), (10, "Data 2"),
                            (11, "Green"), (12, "Data 1"), (13, "Red GND"), (14, "Data GND"), (15, "Red"), (16, "Blanking"),
                            (17, "Video GND"), (18, "Blanking GND"), (19, "Video out"), (20, "Video in"), (21, "Shield")])
DB9 = conn_part("DB9_Joystick", [(1, "Up"), (2, "Down"), (3, "Left"), (4, "Right"), (5, "+5V (Sega)"), (6, "Button 1"),
                                 (7, "+5V (Atari) / TH"), (8, "GND"), (9, "Button 2"), ("SH", "Shield")])
PS2 = conn_part("MiniDIN6_PS2", [(1, "Data"), (2, "NC"), (3, "GND"), (4, "+5V"), (5, "Clock"), (6, "NC"), ("SH", "Shield")])
FTDI = conn_part("Serial_FTDI6", [(1, "GND"), (2, "CTS"), (3, "VCC"), (4, "TXD"), (5, "RXD"), (6, "RTS")],
                 "Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical")
ISP = conn_part("AVR_ISP6", [(1, "MISO"), (2, "VCC"), (3, "SCK"), (4, "MOSI"), (5, "~{RESET}"), (6, "GND")],
                "Connector_PinHeader_2.54mm:PinHeader_2x03_P2.54mm_Vertical")
DCJACK = conn_part("Barrel_Jack", [(1, "+ (tip)"), (2, "- (sleeve)"), (3, "switch")], "Connector_BarrelJack:BarrelJack_Horizontal")
RGBHDR = conn_part("RGB_Header", [(1, "Red"), (2, "Green"), (3, "Blue"), (4, "Blanking"), (5, "GND"), (6, "+5V"),
                                    (7, "EXTVDP")], "Connector_PinHeader_2.54mm:PinHeader_1x07_P2.54mm_Vertical")
EXP = conn_part("Expansion_2x7", [(1, "PA0"), (2, "PA1"), (3, "PA2"), (4, "PA3"), (5, "PA4"), (6, "PA5"), (7, "PA6"),
                                  (8, "PA7"), (9, "PC4"), (10, "PC5"), (11, "PC6"), (12, "PC7"), (13, "+5V"), (14, "GND")],
                "Connector_PinHeader_2.54mm:PinHeader_2x07_P2.54mm_Vertical")


# ---- circuit ----------------------------------------------------------------------------------------------------
def bus(prefix, a, b):
    return [f"{prefix}{i}" for i in range(a, b + 1)]


def build():
    s = Sheet("ZL-80 board", "A1")
    cols = [40 + i * 116 for i in range(7)]
    cy = [45.0] * 7

    def put(col, part, ref, value, conn, gap=17.78, **kw):
        y = cy[col] + part.top + 5.08
        s.place(part, ref, value, cols[col], y, conn, **kw)
        cy[col] = y - part.bottom + gap

    grid = {}

    def grid_init(x, y, n_cols, dx=58.42, dy=12.7):
        grid.update(x0=x, y0=y, n=n_cols, dx=dx, dy=dy, i=0)

    def two(part, ref, value, a, b):
        i = grid["i"]
        grid["i"] += 1
        s.place(part, ref, value, grid["x0"] + (i % grid["n"]) * grid["dx"], grid["y0"] + (i // grid["n"]) * grid["dy"],
                {"1": a, "2": b})

    V, G = "+5V", "GND"
    A, D = bus("A", 0, 15), bus("D", 0, 7)

    # --- column 0: CPU and memory -----------------------------------------------------------------------------
    z = {str(p): nm for p, nm in zip([30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 1, 2, 3, 4, 5], A)}
    z.update({str(p): nm for p, nm in zip([14, 15, 12, 8, 7, 9, 10, 13], D)})
    z.update({"6": "ZCLK", "26": "~{RESET}", "16": "~{INT}", "17": "~{NMI}", "24": "~{WAIT}", "25": "~{BUSRQ}",
              "11": V, "29": G, "27": "~{M1}", "19": "~{MREQ}", "20": "~{IORQ}", "21": "~{RD}", "22": "~{WR}",
              "28": None, "18": None, "23": None})
    put(0, Z80, "U1", "Z84C0004 (Z80 CMOS)", z)

    def mem(part, ref, value, ce, we):
        c = {}
        for num, (x, y, side, p) in part.pins.items():
            nm = p[1]
            if nm[0] == "A" and nm[1:].isdigit():
                k = int(nm[1:])
                c[num] = f"A{k}" if k < 14 else f"PA{k}"  # A14-A18 come from the page registers
            elif nm.startswith("DQ"):
                c[num] = "D" + nm[2:]
            else:
                c[num] = {"VCC": V, "VSS": G, "~{CE}": ce, "~{OE}": "~{RD}", "~{WE}": we}[nm]
        put(0, part, ref, value, c)

    mem(FLASH, "U2", "SST39SF040 flash, pages 0-31", "~{ROMCS}", "~{FLWE}")
    mem(SRAM, "U3", "AS6C4008 SRAM, pages 32-63", "~{RAMCS}", "~{WR}")

    # --- column 1: page mapper and decoding --------------------------------------------------------------------
    put(1, PAGE, "U4", "74HCT670 page bits 0-3",
        {"15": "D0", "1": "D1", "2": "D2", "3": "D3", "14": "A0", "13": "A1", "12": "~{PGWR}", "5": "A14", "4": "A15",
         "11": "~{PGEN}", "16": V, "8": G, "10": "PA14", "9": "PA15", "7": "PA16", "6": "PA17"})
    put(1, PAGE, "U5", "74HCT670 page bits 4-5",
        {"15": "D4", "1": "D5", "2": G, "3": G, "14": "A0", "13": "A1", "12": "~{PGWR}", "5": "A14", "4": "A15",
         "11": "~{PGEN}", "16": V, "8": G, "10": "PA18", "9": "PA19", "7": None, "6": None})
    put(1, HC138, "U6", "74HCT138 I/O 80h-BFh",
        {"1": "A3", "2": "A4", "3": "A5", "6": "A7", "4": "A6", "5": "~{IOSEL}", "16": V, "8": G,
         "15": "~{ACIA_CS}", "14": None, "13": None, "12": "~{VDP_CS}", "11": "~{AY_CS}", "10": "~{PPI_CS}", "9": None, "7": None})
    put(1, HC138, "U7", "74HCT138 I/O 00h-7Fh",
        {"1": "A3", "2": "A4", "3": "A5", "6": "A6", "4": "A7", "5": "~{IOSEL}", "16": V, "8": G,
         "15": None, "14": None, "13": None, "12": None, "11": None, "10": None, "9": None, "7": "~{MAP_CS}"})
    put(1, HC32, "U8", "74HCT32",
        {"1": "~{IORQ}", "2": "M1", "3": "~{IOSEL}", "4": "~{MREQ}", "5": "PA19", "6": "~{ROMCS}",
         "9": "~{MREQ}", "10": "~{PA19}", "8": "~{RAMCS}", "12": "~{MAP_CS}", "13": "~{WR}", "11": "~{MAPWR}", "14": V, "7": G})
    put(1, HC32, "U9", "74HCT32",
        {"1": "~{MAPWR}", "2": "A2", "3": "~{PGWR}", "4": "~{MAPWR}", "5": "~{A2}", "6": "~{ENWR}",
         "9": "~{VDP_CS}", "10": "~{WR}", "8": "~{CSW}", "12": "~{VDP_CS}", "13": "~{RD}", "11": "~{CSR}", "14": V, "7": G})

    # --- column 2: inverters, flip-flops, AY bus control, power -------------------------------------------------
    put(2, HC04, "U10", "74HCT04",
        {"1": "~{M1}", "2": "M1", "3": "PA19", "4": "~{PA19}", "5": "A2", "6": "~{A2}", "9": "~{RESET}", "8": "RESET",
         "11": "CPUCLK", "10": "ZCLK", "13": "~{IORQ}", "12": "E_ACIA", "14": V, "7": G})
    put(2, HC74, "U11", "74HCT74 paging on / AY clock",
        {"2": "D0", "3": "~{ENWR}", "4": V, "1": "~{RESET}", "5": None, "6": "~{PGEN}",
         "12": "~{AYCLK}", "11": "CPUCLK", "10": V, "13": V, "9": "AYCLK", "8": "~{AYCLK}", "14": V, "7": G})
    put(2, HC02, "U12", "74HCT02 AY bus control",
        {"2": "~{AY_CS}", "3": "~{WR}", "1": "BDIR", "5": "~{AY_CS}", "6": "A0", "4": "BC1",
         "8": G, "9": G, "10": None, "11": G, "12": G, "13": None, "14": V, "7": G})
    put(2, DS1813, "U13", "DS1813-5 reset", {"2": V, "3": G, "1": "~{RESET}"})
    put(2, OSC, "X1", "7.3728 MHz oscillator", {"14": V, "7": G, "1": None, "8": "ACLK"})
    put(2, REG, "U14", "R-78E5.0-1.0 (or 7805)", {"1": "+12V", "2": G, "3": V})
    put(2, PWR_FLAG, "#FLG1", "PWR_FLAG", {"1": G}, gap=7.62)
    put(2, PWR_FLAG, "#FLG2", "PWR_FLAG", {"1": "+12V"}, gap=7.62)
    put(2, DCJACK, "J1", "12 V DC in", {"1": "+12V_IN", "2": G, "3": G})

    # --- column 3: video ---------------------------------------------------------------------------------------
    t = {"24": "D7", "23": "D6", "22": "D5", "21": "D4", "20": "D3", "19": "D2", "18": "D1", "17": "D0",  # CD0 is the MSB
         "13": "A0", "14": "~{CSW}", "15": "~{CSR}", "16": "VDP_INT", "34": "~{RESET}", "39": "VXT1", "40": "VXT2",
         "38": "CPUCLK", "37": None, "33": V, "12": G, "1": "~{VRAS}", "2": "~{VCAS}", "11": "VR~{W}", "36": "COMVID",
         "35": "EXTVDP"}
    t.update({str(p): f"VAD{i}" for i, p in enumerate([10, 9, 8, 7, 6, 5, 4, 3])})
    t.update({str(p): f"VRD{i}" for i, p in enumerate([32, 31, 30, 29, 28, 27, 26, 25])})
    put(3, TMS, "U15", "TMS9918A", t)
    # 16 KB VRAM: 62256 SRAM behind row, column and write-data latches (jblang/TMS9918A, after Tom LeMense).
    # The VDP puts the row address on AD1-AD7 at /RAS and the column address at /CAS; AD0 carries data only.
    vad = {str(p): f"VAD{i}" for i, p in enumerate([2, 3, 4, 5, 6, 7, 8, 9])}
    put(3, HC574, "U17", "74HCT574 VRAM row latch",
        dict(vad, **{"11": "VROW", "1": G, "20": V, "10": G, "19": None, "18": "VMA0", "17": "VMA1", "16": "VMA2", "15": "VMA3",
                     "14": "VMA10", "13": "VMA4", "12": "VMA5"}))
    put(3, HC574, "U24", "74HCT574 VRAM column latch",
        dict(vad, **{"11": "VCOL", "1": G, "20": V, "10": G, "19": None, "18": "VMA11", "17": "VMA6", "16": "VMA7", "15": "VMA9",
                     "14": "VMA12", "13": "VMA8", "12": "VMA13"}))
    put(3, HC574, "U25", "74HCT574 VRAM write data",
        dict(vad, **{"11": "~{VRW}", "1": "VR~{W}", "20": V, "10": G, "19": "VRD0", "18": "VRD1", "17": "VRD2", "16": "VRD3",
                     "15": "VRD4", "14": "VRD5", "13": "VRD6", "12": "VRD7"}))
    m = {"10": "VMA0", "9": "VMA1", "8": "VMA2", "7": "VMA3", "6": "VMA4", "5": "VMA5", "4": "VMA6", "3": "VMA7", "25": "VMA8",
         "24": "VMA9", "21": "VMA10", "23": "VMA11", "2": "VMA12", "26": "VMA13", "1": "VMA13", "28": V, "14": G,
         "20": "~{VCAS}", "22": "~{VRW}", "27": "VR~{W}"}
    m.update({str(p): f"VRD{i}" for i, p in enumerate([11, 12, 13, 15, 16, 17, 18, 19])})  # VRDn = RDn = data bit n of ADn
    put(3, SRAM32K, "U16", "62256 VRAM (16 KB used)", m)
    put(3, HC04, "U26", "74HCT04 VRAM strobes",
        {"1": "~{VRAS}", "2": "VROW", "3": "~{VCAS}", "4": "VCAS1", "5": "VCAS1", "6": "VCAS2", "9": "VCAS2", "8": "VCOL",
         "11": "VR~{W}", "10": "~{VRW}", "13": G, "12": None, "14": V, "7": G})  # VCOL: /CAS inverted and delayed by three gates
    put(6, NPN, "Q1", "2N4401 video buffer", {"2": "VID_B", "1": "VID_C", "3": "VID_OUT"})
    put(6, SCART, "J2", "SCART",
        {"1": None, "2": "AUD_R", "3": None, "4": G, "5": G, "6": "AUD_L", "7": "RGB_B", "8": "SCART_FS", "9": G, "10": None,
         "11": "RGB_G", "12": None, "13": G, "14": G, "15": "RGB_R", "16": "BLANK", "17": G, "18": G, "19": None,
         "20": "VID_OUT", "21": G})
    put(6, RGBHDR, "J3", "RGB board (later)", {"1": "RGB_R", "2": "RGB_G", "3": "RGB_B", "4": "BLANK", "5": G, "6": V,
                                                "7": "EXTVDP"})

    # --- column 4: sound and joysticks --------------------------------------------------------------------------
    a = {str(p): d for p, d in zip([37, 36, 35, 34, 33, 32, 31, 30], D)}
    a.update({"27": "BDIR", "29": "BC1", "28": V, "25": V, "24": G, "23": "~{RESET}", "22": "AYCLK", "39": None, "26": None,
              "40": V, "1": G, "4": "AY_A", "3": "AY_B", "38": "AY_C",
              "21": "IOA0", "20": "IOA1", "19": "IOA2", "18": "IOA3", "17": "IOA4", "16": "IOA5", "15": "IOA6", "14": "IOA7",
              "13": None, "12": None, "11": None, "10": None, "9": None, "8": None, "7": "JOYSEL", "6": None, "2": None, "5": None})
    put(4, AY, "U18", "AY-3-8910", a)
    put(4, HC157, "U19", "74HCT157 joystick directions",
        {"1": "JOYSEL", "15": G, "2": "J1_UP", "3": "J2_UP", "5": "J1_DOWN", "6": "J2_DOWN", "11": "J1_LEFT", "10": "J2_LEFT",
         "14": "J1_RIGHT", "13": "J2_RIGHT", "16": V, "8": G, "4": "IOA0", "7": "IOA1", "9": "IOA2", "12": "IOA3"})
    put(4, HC157, "U20", "74HCT157 joystick buttons",
        {"1": "JOYSEL", "15": G, "2": "J1_B1", "3": "J2_B1", "5": "J1_B2", "6": "J2_B2", "11": G, "10": G, "14": G, "13": G,
         "16": V, "8": G, "4": "IOA4", "7": "IOA5", "9": None, "12": None})
    for ref, j in (("J4", "J1"), ("J5", "J2")):
        put(4, DB9, ref, f"Joystick {j[1]} (Atari / Sega)",
            {"1": f"{j}_UP", "2": f"{j}_DOWN", "3": f"{j}_LEFT", "4": f"{j}_RIGHT", "5": V, "6": f"{j}_B1",
             "7": f"{j}_P7", "8": G, "9": f"{j}_B2", "SH": G})
    for ref, j in (("RN1", "J1"), ("RN2", "J2")):
        put(4, RNET, ref, "10k x 8",
            {"1": V, "2": f"{j}_UP", "3": f"{j}_DOWN", "4": f"{j}_LEFT", "5": f"{j}_RIGHT", "6": f"{j}_B1", "7": f"{j}_B2",
             "8": "IOA6" if j == "J1" else "IOA7", "9": "JOYSEL" if j == "J1" else None}, gap=10.16)

    # --- column 5: keyboard and expansion -------------------------------------------------------------------------
    pp = {str(p): d for p, d in zip([34, 33, 32, 31, 30, 29, 28, 27], D)}
    pp.update({"6": "~{PPI_CS}", "5": "~{RD}", "36": "~{WR}", "9": "A0", "8": "A1", "35": "RESET", "26": V, "7": G,
               "4": "PPA0", "3": "PPA1", "2": "PPA2", "1": "PPA3", "40": "PPA4", "39": "PPA5", "38": "PPA6", "37": "PPA7",
               "18": "KCOL0", "19": "KCOL1", "20": "KCOL2", "21": "KCOL3", "22": "KCOL4", "23": "KCOL5", "24": "KCOL6",
               "25": "KCOL7", "14": "KROW0", "15": "KROW1", "16": "KROW2", "17": "KROW3", "13": "PPC4", "12": "PPC5",
               "11": "PPC6", "10": "PPC7"})
    put(5, PPI, "U21", "82C55A", pp)
    put(5, MCU, "U22", "ATmega328P: PS/2 to key matrix",
        {"1": "KB_RST", "23": "KROW0", "24": "KROW1", "25": "KROW2", "26": "KROW3", "27": None, "28": None,
         "14": "PS2_CLK", "15": "PS2_DATA", "16": None, "17": "KB_MOSI", "18": "KB_MISO", "19": "KB_SCK", "9": None, "10": None,
         "7": V, "20": V, "21": "KB_AREF", "8": G, "22": G,
         "2": "KCOL0", "3": "KCOL1", "4": "KCOL2", "5": "KCOL3", "6": "KCOL4", "11": "KCOL5", "12": "KCOL6", "13": "KCOL7"})
    put(5, PS2, "J6", "PS/2 keyboard", {"1": "PS2_DATA", "2": None, "3": G, "4": V, "5": "PS2_CLK", "6": None, "SH": G})
    put(5, ISP, "J7", "ISP for the ATmega", {"1": "KB_MISO", "2": V, "3": "KB_SCK", "4": "KB_MOSI", "5": "KB_RST", "6": G})
    put(5, EXP, "J8", "Expansion (8255 PA, PC4-7)",
        {"1": "PPA0", "2": "PPA1", "3": "PPA2", "4": "PPA3", "5": "PPA4", "6": "PPA5", "7": "PPA6", "8": "PPA7",
         "9": "PPC4", "10": "PPC5", "11": "PPC6", "12": "PPC7", "13": V, "14": G})

    # --- column 6: serial, reset, crystal ---------------------------------------------------------------------
    ac = {str(p): d for p, d in zip([22, 21, 20, 19, 18, 17, 16, 15], D)}
    ac.update({"8": V, "10": V, "9": "~{ACIA_CS}", "11": "A0", "13": "~{WR}", "14": "E_ACIA", "7": None, "12": V, "1": G,
               "4": "ACLK", "3": "ACLK", "6": "SER_TX", "2": "SER_RX", "5": "SER_RTS", "24": G, "23": G})
    put(6, ACIA, "U23", "MC68B50 ACIA", ac)
    put(6, FTDI, "J9", "USB serial (FTDI cable, 5 V)", {"1": G, "2": "SER_RTS", "3": None, "4": "SER_RX", "5": "SER_TX", "6": None})
    put(6, BTN, "SW1", "Reset", {"1": "~{RESET}", "2": G})
    put(6, JMP, "JP1", "Flash write enable", {"1": "~{WR}", "2": "~{FLWE}"})
    put(6, XTAL, "Y1", "10.738635 MHz", {"1": "VXT1", "2": "VXT2"})

    # --- passives ------------------------------------------------------------------------------------------------
    grid_init(cols[0] - 10, 455, 12)
    for i, net in enumerate(["PA14", "PA15", "PA16", "PA17", "PA18", "PA19"]):
        two(RES, f"R{1 + i}", "10k", net, G)  # paging off: the page lines read 0
    for i, net in enumerate(["~{NMI}", "~{WAIT}", "~{BUSRQ}", "~{INT}", "~{FLWE}", "KB_RST", "PS2_CLK", "PS2_DATA", "~{RESET}"]):
        two(RES, f"R{7 + i}", "4.7k" if net.startswith("PS2") else "10k", V, net)
    nxt = iter(range(16, 100))
    for net in ("AY_A", "AY_B", "AY_C"):
        two(RES, f"R{next(nxt)}", "3k", net, G)  # load for the AY outputs (as electrified/rc2014-ym2149)
    for val, x, y in (("1k", "AY_A", "MIX_L"), ("2.2k", "AY_B", "MIX_L"), ("2.2k", "AY_B", "MIX_R"), ("1k", "AY_C", "MIX_R")):
        two(RES, f"R{next(nxt)}", val, x, y)
    two(CPOL, "C1", "10u", "MIX_L", "AUD_L")
    two(CPOL, "C2", "10u", "MIX_R", "AUD_R")
    for val, x, y in (("47k", "AUD_L", G), ("47k", "AUD_R", G), ("130", "COMVID", "VID_B"), ("470", "VID_B", G),
                      ("75", "VID_OUT", G), ("75", "BLANK", G), ("1k", "+12V", "SCART_FS"), ("1k", V, "J1_P7"),
                      ("1k", V, "J2_P7"), ("1k", V, "LED_A")):
        two(RES, f"R{next(nxt)}", val, x, y)
    two(LED, "D2", "Power", G, "LED_A")
    two(DIODE, "D1", "1N5819", "+12V", "+12V_IN")
    two(DIODE, "D3", "BAT85", "VDP_INT", "~{INT}")
    two(FBEAD, "FB1", "Ferrite bead", V, "VID_C")
    two(CAP, "C29", "100n", "VID_C", G)
    two(CAP, "C30", "22p", "VXT1", G)  # TI: 15-39 pF typical; jblang uses 16 pF
    two(CAP, "C31", "22p", "VXT2", G)
    two(CPOL, "C3", "100u", "+12V", G)
    two(CPOL, "C4", "100u", V, G)
    two(CAP, "C5", "100n", "KB_AREF", G)
    for c in range(6, 29):  # 100 nF next to each IC's supply pins; C32-C34 below cover the VRAM chips, placed next to its supply pins
        two(CAP, f"C{c}", "100n", V, G)
    for c in range(32, 35):
        two(CAP, f"C{c}", "100n", V, G)
    return s


def main():
    s = build()
    s.add_text(20, 20, "ZL-80 board, generated by hardware/kicad/gen_schematic.py from docs/hardware.md. Connections are by net name.\n"
                       "NOT BUILT OR TESTED. Check every pin against the datasheets before ordering a board.", 2.5)
    s.write(os.path.join(HERE, "zl80.kicad_sch"), date="2026-10-27", rev="0.1",
            comments=("Z80 3.58 MHz, TMS9918A + 16 KB SRAM VRAM, AY-3-8910, 512 KB flash + 512 KB SRAM, 82C55 + PS/2, MC68B50",
                      "Design only: not built or tested"))
    single = {k: v for k, v in s.nets.items() if len(v) < 2}
    with open(os.path.join(HERE, "zl80-netlist.txt"), "w", encoding="utf-8", newline="\n") as fh:
        for net in sorted(s.nets, key=lambda k: (k.strip("~{}").lower(), k)):
            fh.write(f"{net}: {' '.join(sorted(s.nets[net]))}\n")
    print(f"{len(s.refs)} parts, {len(s.nets)} nets")
    for k, v in single.items():
        print("NET WITH ONE PIN:", k, v)


if __name__ == "__main__":
    main()
