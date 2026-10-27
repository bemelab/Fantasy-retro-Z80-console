"""Generate the ZL-80 board schematic (docs/hardware.md) for KiCad.

    python gen_schematic.py

writes the KiCad project files (a root sheet and one sheet per page) and
zl80-netlist.txt next to this file. Connections are
made by net labels; zl80-netlist.txt lists every net with the pins on it, for
checking against the datasheets.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sch import Part, Project  # noqa: E402
P, I, O, B, PI, PO, OC = "passive", "input", "output", "bidirectional", "power_in", "power_out", "open_collector"
DIP40 = "Package_DIP:DIP-40_W15.24mm_Socket"  # Z80, TMS9918A, AY-3-8910, 82C55: the DIP chips in hand, in sockets
SO14, SO16, SO20W = ("Package_SO:SOIC-14_3.9x8.7mm_P1.27mm", "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm",
                     "Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm")


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
           footprint=DIP40, width=22.86)

TMS = Part("TMS9918A", [L(24, "CD0 (MSB)", B), L(23, "CD1", B), L(22, "CD2", B), L(21, "CD3", B), L(20, "CD4", B), L(19, "CD5", B),
                         L(18, "CD6", B), L(17, "CD7 (LSB)", B), None, L(13, "MODE", I), L(14, "~{CSW}", I), L(15, "~{CSR}", I),
                         L(16, "~{INT}", O), L(34, "~{RESET}/SYNC", I), None, L(39, "XTAL1", I), L(40, "XTAL2", P),
                         L(38, "CPUCLK", O), L(37, "GROMCLK", O), None, L(33, "VCC", PI), L(12, "VSS", PI),
                         R(10, "AD0", O), R(9, "AD1", O), R(8, "AD2", O), R(7, "AD3", O), R(6, "AD4", O), R(5, "AD5", O),
                         R(4, "AD6", O), R(3, "AD7", O), ("gap", "R"), R(32, "RD0", I), R(31, "RD1", I), R(30, "RD2", I),
                         R(29, "RD3", I), R(28, "RD4", I), R(27, "RD5", I), R(26, "RD6", I), R(25, "RD7", I), ("gap", "R"),
                         R(1, "~{RAS}", O), R(2, "~{CAS}", O), R(11, "R/~{W}", O), ("gap", "R"), R(36, "COMVID", O),
                         R(35, "EXTVDP", I)],
           footprint=DIP40, width=25.4)

AY = Part("AY-3-8910", [L(37, "DA0", B), L(36, "DA1", B), L(35, "DA2", B), L(34, "DA3", B), L(33, "DA4", B), L(32, "DA5", B),
                         L(31, "DA6", B), L(30, "DA7", B), None, L(27, "BDIR", I), L(29, "BC1", I), L(28, "BC2", I),
                         L(25, "A8", I), L(24, "~{A9}", I), L(23, "~{RESET}", I), L(22, "CLOCK", I), None,
                         L(39, "TEST1", P), L(26, "TEST2", P), None, L(40, "VCC", PI), L(1, "VSS", PI),
                         R(4, "ANALOG A", O), R(3, "ANALOG B", O), R(38, "ANALOG C", O), ("gap", "R"),
                         R(21, "IOA0", B), R(20, "IOA1", B), R(19, "IOA2", B), R(18, "IOA3", B), R(17, "IOA4", B),
                         R(16, "IOA5", B), R(15, "IOA6", B), R(14, "IOA7", B), ("gap", "R"),
                         R(13, "IOB0", B), R(12, "IOB1", B), R(11, "IOB2", B), R(10, "IOB3", B), R(9, "IOB4", B),
                         R(8, "IOB5", B), R(7, "IOB6", B), R(6, "IOB7", B), R(2, "NC", P), R(5, "NC", P)],
          footprint=DIP40, width=25.4)

PPI = Part("82C55A", [L(34, "D0", B), L(33, "D1", B), L(32, "D2", B), L(31, "D3", B), L(30, "D4", B), L(29, "D5", B),
                       L(28, "D6", B), L(27, "D7", B), None, L(6, "~{CS}", I), L(5, "~{RD}", I), L(36, "~{WR}", I),
                       L(9, "A0", I), L(8, "A1", I), L(35, "RESET", I), None, L(26, "VCC", PI), L(7, "GND", PI),
                       R(4, "PA0", B), R(3, "PA1", B), R(2, "PA2", B), R(1, "PA3", B), R(40, "PA4", B), R(39, "PA5", B),
                       R(38, "PA6", B), R(37, "PA7", B), ("gap", "R"),
                       R(18, "PB0", B), R(19, "PB1", B), R(20, "PB2", B), R(21, "PB3", B), R(22, "PB4", B), R(23, "PB5", B),
                       R(24, "PB6", B), R(25, "PB7", B), ("gap", "R"),
                       R(14, "PC0", B), R(15, "PC1", B), R(16, "PC2", B), R(17, "PC3", B), R(13, "PC4", B), R(12, "PC5", B),
                       R(11, "PC6", B), R(10, "PC7", B)],
           footprint=DIP40, width=22.86)

# FT245RL USB FIFO (FTDI DS_FT245R v2.14, SSOP-28). WR latches on its falling edge; the data bus order is scrambled.
FT245 = Part("FT245RL", [L(1, "D0", B), L(5, "D1", B), L(3, "D2", B), L(11, "D3", B), L(2, "D4", B), L(9, "D5", B),
                         L(10, "D6", B), L(6, "D7", B), None, L(13, "~{RD}", I), L(14, "WR", I), L(19, "~{RESET}", I), None,
                         L(20, "VCC", PI), L(4, "VCCIO", PI), L(17, "3V3OUT", P), L(7, "GND", PI), L(18, "GND", PI),
                         L(21, "GND", PI), L(25, "AGND", PI), L(26, "TEST", P),
                         R(23, "~{RXF}", O), R(22, "~{TXE}", O), R(12, "~{PWREN}", O), ("gap", "R"), R(15, "USBDP", B),
                         R(16, "USBDM", B), ("gap", "R"), R(27, "OSCI", P), R(28, "OSCO", P), R(8, "NC", P), R(24, "NC", P)],
             footprint="Package_SO:SSOP-28_5.3x10.2mm_P0.65mm", width=22.86)
# USB-C receptacle, GCT USB4105-GF-A (LCSC C3020560), used as a USB 2.0 device
USBC = Part("USB_C", [L("A4", "VBUS"), L("A9", "VBUS"), L("B4", "VBUS"), L("B9", "VBUS"), None, L("A6", "D+"), L("B6", "D+"),
                      L("A7", "D-"), L("B7", "D-"), None, L("A5", "CC1"), L("B5", "CC2"), L("A8", "SBU1"), L("B8", "SBU2"), None,
                      L("A1", "GND"), L("A12", "GND"), L("B1", "GND"), L("B12", "GND"), L("S1", "SHIELD")], ref="J",
            footprint="Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal", width=15.24)

PAGE = Part("74HC670", [L(15, "D0", I), L(1, "D1", I), L(2, "D2", I), L(3, "D3", I), None, L(14, "WA0", I), L(13, "WA1", I),
                          L(12, "~{WE}", I), None, L(5, "RA0", I), L(4, "RA1", I), L(11, "~{RE}", I), None,
                          L(16, "VCC", PI), L(8, "GND", PI),
                          R(10, "Q0", O), R(9, "Q1", O), R(7, "Q2", O), R(6, "Q3", O)], footprint=SO16)

MEM32 = lambda name, special, fp: Part(name, [
    L(12, "A0", I), L(11, "A1", I), L(10, "A2", I), L(9, "A3", I), L(8, "A4", I), L(7, "A5", I), L(6, "A6", I), L(5, "A7", I),
    L(27, "A8", I), L(26, "A9", I), L(23, "A10", I), L(25, "A11", I), L(4, "A12", I), L(28, "A13", I),
    L(special["A14"], "A14", I), L(special["A15"], "A15", I), L(2, "A16", I), L(30, "A17", I), L(1, "A18", I), None,
    L(32, "VCC", PI), L(16, "VSS", PI),
    R(13, "DQ0", B), R(14, "DQ1", B), R(15, "DQ2", B), R(17, "DQ3", B), R(18, "DQ4", B), R(19, "DQ5", B), R(20, "DQ6", B),
    R(21, "DQ7", B), ("gap", "R"), R(22, "~{CE}", I), R(24, "~{OE}", I), R(special["WE"], "~{WE}", I)],
    footprint=fp, width=22.86)
# PLCC-32 and SOP-32 keep the PDIP-32 pin numbers (Microchip DS20005022F, Alliance AS6C4008 v1.4)
FLASH = MEM32("SST39SF040", {"A14": 29, "A15": 3, "WE": 31}, "Package_DIP:DIP-32_W15.24mm_Socket")  # in a socket, to program it
SRAM = MEM32("AS6C4008", {"A14": 3, "A15": 31, "WE": 29}, "Package_SO:SOP-32_11.305x20.495mm_P1.27mm")

SRAM32K = Part("62256", [L(10, "A0", I), L(9, "A1", I), L(8, "A2", I), L(7, "A3", I), L(6, "A4", I), L(5, "A5", I),
                          L(4, "A6", I), L(3, "A7", I), L(25, "A8", I), L(24, "A9", I), L(21, "A10", I), L(23, "A11", I),
                          L(2, "A12", I), L(26, "A13", I), L(1, "A14", I), None, L(28, "VCC", PI), L(14, "GND", PI),
                          R(11, "D0", B), R(12, "D1", B), R(13, "D2", B), R(15, "D3", B), R(16, "D4", B), R(17, "D5", B),
                          R(18, "D6", B), R(19, "D7", B), ("gap", "R"), R(20, "~{CS}", I), R(22, "~{OE}", I), R(27, "~{WE}", I)],
                footprint="Package_SO:SOP-28_8.4x18.16mm_P1.27mm", width=22.86)  # AS6C62256-55SCN, 330 mil SOP-28
HC574 = Part("74HCT574", [L(2, "D0", I), L(3, "D1", I), L(4, "D2", I), L(5, "D3", I), L(6, "D4", I), L(7, "D5", I), L(8, "D6", I),
                           L(9, "D7", I), None, L(11, "CLK", I), L(1, "~{OE}", I), None, L(20, "VCC", PI), L(10, "GND", PI),
                           R(19, "Q0", O), R(18, "Q1", O), R(17, "Q2", O), R(16, "Q3", O), R(15, "Q4", O), R(14, "Q5", O),
                           R(13, "Q6", O), R(12, "Q7", O)], footprint=SO20W)

MCU = Part("ATmega328P-AU", [L(29, "PC6/~{RESET}", I), None, L(23, "PC0", B), L(24, "PC1", B), L(25, "PC2", B),
                              L(26, "PC3", B), L(27, "PC4", B), L(28, "PC5", B), L(19, "ADC6", P), L(22, "ADC7", P), None,
                              L(12, "PB0", B), L(13, "PB1", B), L(14, "PB2", B), L(15, "PB3/MOSI", B), L(16, "PB4/MISO", B),
                              L(17, "PB5/SCK", B), L(7, "PB6/XTAL1", B), L(8, "PB7/XTAL2", B), None,
                              L(4, "VCC", PI), L(6, "VCC", PI), L(18, "AVCC", PI), L(20, "AREF", P),
                              L(3, "GND", PI), L(5, "GND", PI), L(21, "GND", PI),
                              R(30, "PD0", B), R(31, "PD1", B), R(32, "PD2", B), R(1, "PD3", B), R(2, "PD4", B), R(9, "PD5", B),
                              R(10, "PD6", B), R(11, "PD7", B)], footprint="Package_QFP:TQFP-32_7x7mm_P0.8mm", width=22.86)

HC138 = Part("74HCT138", [L(1, "A", I), L(2, "B", I), L(3, "C", I), None, L(6, "G1", I), L(4, "~{G2A}", I), L(5, "~{G2B}", I),
                           None, L(16, "VCC", PI), L(8, "GND", PI),
                           R(15, "~{Y0}", O), R(14, "~{Y1}", O), R(13, "~{Y2}", O), R(12, "~{Y3}", O), R(11, "~{Y4}", O),
                           R(10, "~{Y5}", O), R(9, "~{Y6}", O), R(7, "~{Y7}", O)], footprint=SO16)
HC157 = Part("74HCT157", [L(1, "S", I), L(15, "~{E}", I), None, L(2, "1A", I), L(3, "1B", I), L(5, "2A", I), L(6, "2B", I),
                           L(11, "3A", I), L(10, "3B", I), L(14, "4A", I), L(13, "4B", I), None, L(16, "VCC", PI),
                           L(8, "GND", PI), R(4, "1Y", O), R(7, "2Y", O), R(9, "3Y", O), R(12, "4Y", O)], footprint=SO16)
HC74 = Part("74HCT74", [L(2, "1D", I), L(3, "1CLK", I), L(4, "~{1PRE}", I), L(1, "~{1CLR}", I), None,
                         L(12, "2D", I), L(11, "2CLK", I), L(10, "~{2PRE}", I), L(13, "~{2CLR}", I), None,
                         L(14, "VCC", PI), L(7, "GND", PI),
                         R(5, "1Q", O), R(6, "~{1Q}", O), ("gap", "R"), ("gap", "R"), ("gap", "R"), R(9, "2Q", O),
                         R(8, "~{2Q}", O)], footprint=SO14)
QUAD2 = lambda name, g: Part(name, [L(1, "1A", I), L(2, "1B", I), L(4, "2A", I), L(5, "2B", I), L(9, "3A", I), L(10, "3B", I),
                                     L(12, "4A", I), L(13, "4B", I), None, L(14, "VCC", PI), L(7, "GND", PI),
                                     R(3, f"1Y={g}", O), R(6, f"2Y={g}", O), R(8, f"3Y={g}", O), R(11, f"4Y={g}", O)],
                             footprint=SO14)
HC32 = QUAD2("74HCT32", "1A|1B")
HC02 = Part("74HCT02", [L(2, "1A", I), L(3, "1B", I), L(5, "2A", I), L(6, "2B", I), L(8, "3A", I), L(9, "3B", I), L(11, "4A", I),
                         L(12, "4B", I), None, L(14, "VCC", PI), L(7, "GND", PI),
                         R(1, "1Y=~{1A|1B}", O), R(4, "2Y", O), R(10, "3Y", O), R(13, "4Y", O)], footprint=SO14)
HC04 = Part("74HCT04", [L(1, "1A", I), L(3, "2A", I), L(5, "3A", I), L(9, "4A", I), L(11, "5A", I), L(13, "6A", I), None,
                         L(14, "VCC", PI), L(7, "GND", PI),
                         R(2, "1Y=~{1A}", O), R(4, "2Y", O), R(6, "3Y", O), R(8, "4Y", O), R(10, "5Y", O), R(12, "6Y", O)],
            footprint=SO14)

DS1813 = Part("DS1813", [L(2, "VCC", PI), L(3, "GND", PI), R(1, "~{RST}", OC)], footprint="Package_TO_SOT_SMD:SOT-23-3",
              width=15.24)  # DS1813R-5
HC125 = Part("74HCT125", [L(1, "~{1OE}", I), L(2, "1A", I), L(4, "~{2OE}", I), L(5, "2A", I), L(10, "~{3OE}", I), L(9, "3A", I),
                           L(13, "~{4OE}", I), L(12, "4A", I), None, L(14, "VCC", PI), L(7, "GND", PI),
                           R(3, "1Y", O), R(6, "2Y", O), R(8, "3Y", O), R(11, "4Y", O)], footprint=SO14)
REG = Part("Regulator_5V", [L(1, "VIN", PI), L(2, "GND", PI), R(3, "VOUT", PO)], footprint="Converter_DCDC:Converter_DCDC_RECOM_R-78E-0.5_THT",
           width=15.24)
RES = Part("R", [L(1, "~"), R(2, "~")], ref="R", footprint="Resistor_SMD:R_0805_2012Metric",
           width=5.08)
CAP = Part("C", [L(1, "~"), R(2, "~")], ref="C", footprint="Capacitor_SMD:C_0805_2012Metric", width=5.08)
CPOL = Part("C_Polarized", [L(1, "+"), R(2, "-")], ref="C", footprint="Capacitor_SMD:CP_Elec_6.3x7.7", width=5.08)
XTAL = Part("Crystal", [L(1, "1"), R(2, "2")], ref="Y", footprint="Crystal:Crystal_SMD_HC49-SD", width=5.08)
FBEAD = Part("Ferrite_Bead", [L(1, "1"), R(2, "2")], ref="FB", footprint="Inductor_SMD:L_0805_2012Metric",
              width=5.08)
DIODE = Part("D", [L(1, "K"), R(2, "A")], ref="D", footprint="Diode_SMD:D_SOD-123", width=5.08)
LED = Part("LED", [L(1, "K"), R(2, "A")], ref="D", footprint="LED_SMD:LED_0805_2012Metric", width=5.08)
NPN = Part("NPN_SOT23", [L(1, "B"), R(3, "C"), R(2, "E")], ref="Q", footprint="Package_TO_SOT_SMD:SOT-23-3", width=7.62)
BTN = Part("SW_Push", [L(1, "1"), R(2, "2")], ref="SW", footprint="Button_Switch_SMD:SW_SPST_B3U-1000P", width=5.08)
JMP = Part("Jumper_2", [L(1, "1"), R(2, "2")], ref="JP", footprint="Jumper:SolderJumper-2_P1.3mm_Open_TrianglePad1.0x1.5mm",
           width=5.08)
PWR_FLAG = Part("PWR_FLAG", [L(1, "pwr", PO)], ref="#FLG", power=True)


def conn_part(name, pins, footprint=""):
    return Part(name, [L(num, nm) for num, nm in pins], ref="J", footprint=footprint, width=15.24)


# SCART and PS/2 have no KiCad footprints: they are panel sockets on short cables to these headers
TVHDR = conn_part("TV_Header", [(1, "Video (SCART 20)"), (2, "GND (SCART 17)"), (3, "Audio L (SCART 6)"), (4, "Audio R (SCART 2)"),
                                (5, "Audio GND (SCART 4)"), (6, "12V switch (SCART 8)"), (7, "Blanking (SCART 16)"),
                                (8, "GND (SCART 18, 21)"), (9, "EXTVDP"), (10, "+5V")],
                  "Connector_PinHeader_2.54mm:PinHeader_2x05_P2.54mm_Vertical")
DB9 = conn_part("DB9_Joystick", [(1, "Up"), (2, "Down"), (3, "Left"), (4, "Right"), (5, "+5V (Sega)"), (6, "Button 1"),
                                 (7, "+5V (Atari) / TH"), (8, "GND"), (9, "Button 2"), (0, "Shield")],
                "Connector_Dsub:DSUB-9_Male_Horizontal_P2.77x2.84mm_EdgePinOffset7.70mm_Housed_MountingHolesOffset9.12mm")
PS2 = conn_part("PS2_Header", [(1, "+5V (DIN 4)"), (2, "Clock (DIN 5)"), (3, "Data (DIN 1)"), (4, "GND (DIN 3, shell)")],
                "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical")
ISP = conn_part("AVR_ISP6", [(1, "MISO"), (2, "VCC"), (3, "SCK"), (4, "MOSI"), (5, "~{RESET}"), (6, "GND")],
                "Connector_PinHeader_2.54mm:PinHeader_2x03_P2.54mm_Vertical")
DCJACK = conn_part("Barrel_Jack", [(1, "+ (tip)"), (2, "- (sleeve)"), (3, "switch")], "Connector_BarrelJack:BarrelJack_Horizontal")
EXP = conn_part("Expansion_2x7", [(1, "PA0"), (2, "PA1"), (3, "PA2"), (4, "PA3"), (5, "PA4"), (6, "PA5"), (7, "PA6"),
                                  (8, "PA7"), (9, "PC4"), (10, "PC5"), (11, "PC6"), (12, "PC7"), (13, "+5V"), (14, "GND")],
                "Connector_PinHeader_2.54mm:PinHeader_2x07_P2.54mm_Vertical")


# ---- circuit ----------------------------------------------------------------------------------------------------
def bus(prefix, a, b):
    return [f"{prefix}{i}" for i in range(a, b + 1)]


class Layout:
    """Places parts on one page: ICs in columns, then two-pin parts in a grid below them."""

    def __init__(self, sheet, n_cols=4):
        self.s = sheet
        self.cols = [40 + i * 116 for i in range(n_cols)]
        self.cy = [35.0] * n_cols
        self.i = 0
        self.decouple = []

    def put(self, col, part, ref, value, conn, gap=17.78):
        y = self.cy[col] + part.top + 5.08
        self.s.place(part, ref, value, self.cols[col], y, conn)
        self.cy[col] = y - part.bottom + gap
        if ref.startswith("U") and any(p[3][1] in ("VCC", "VDD") for p in part.pins.values()):
            self.decouple.append(ref)

    def two(self, part, ref, value, a, b):
        if self.i == 0:
            self.y0 = max(self.cy) + 2.54
        n_grid = 6 if len(self.cols) <= 3 else 8
        x = self.cols[0] - 10 + (self.i % n_grid) * 50.8
        y = self.y0 + (self.i // n_grid) * 12.7
        self.i += 1
        self.s.place(part, ref, value, x, y, {"1": a, "2": b})


def build():
    proj = Project("ZL-80 board")
    V, G = "+5V", "GND"
    A, D = bus("A", 0, 15), bus("D", 0, 7)
    caps = iter([c for c in range(6, 36) if c not in (29, 30, 31)])  # 100 nF supply decoupling, one per chip

    def decouple(pg):
        for ref in pg.decouple:
            pg.two(CAP, f"C{next(caps)}", f"100n ({ref})", V, G)

    # --- page 2: CPU, memory and decoding ------------------------------------------------------------------------
    pg = Layout(proj.page("CPU, memory and decoding", "cpu_memory.kicad_sch"), 4)
    z = {str(p): nm for p, nm in zip([30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 1, 2, 3, 4, 5], A)}
    z.update({str(p): nm for p, nm in zip([14, 15, 12, 8, 7, 9, 10, 13], D)})
    z.update({"6": "ZCLK", "26": "~{RESET}", "16": "~{INT}", "17": "~{NMI}", "24": "~{WAIT}", "25": "~{BUSRQ}",
              "11": V, "29": G, "27": "~{M1}", "19": "~{MREQ}", "20": "~{IORQ}", "21": "~{RD}", "22": "~{WR}",
              "28": None, "18": None, "23": None})
    pg.put(0, Z80, "U1", "Z84C0004 (Z80 CMOS)", z)

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
        pg.put(1, part, ref, value, c)

    mem(FLASH, "U2", "SST39SF040 flash, pages 0-31", "~{ROMCS}", "~{FLWE}")
    mem(SRAM, "U3", "AS6C4008 SRAM, pages 32-63", "~{RAMCS}", "~{WR}")
    pg.put(2, PAGE, "U4", "74HCT670 page bits 0-3",
           {"15": "D0", "1": "D1", "2": "D2", "3": "D3", "14": "A0", "13": "A1", "12": "~{PGWR}", "5": "A14", "4": "A15",
            "11": "~{PGEN}", "16": V, "8": G, "10": "PA14", "9": "PA15", "7": "PA16", "6": "PA17"})
    pg.put(2, PAGE, "U5", "74HCT670 page bits 4-5",
           {"15": "D4", "1": "D5", "2": G, "3": G, "14": "A0", "13": "A1", "12": "~{PGWR}", "5": "A14", "4": "A15",
            "11": "~{PGEN}", "16": V, "8": G, "10": "PA18", "9": "PA19", "7": None, "6": None})
    pg.put(2, HC74, "U11", "74HCT74 paging on / AY clock",
           {"2": "D0", "3": "~{ENWR}", "4": V, "1": "~{RESET}", "5": None, "6": "~{PGEN}",
            "12": "~{AYCLK}", "11": "CPUCLK", "10": V, "13": V, "9": "AYCLK", "8": "~{AYCLK}", "14": V, "7": G})
    pg.put(3, HC138, "U6", "74HCT138 I/O 80h-BFh",
           {"1": "A3", "2": "A4", "3": "A5", "6": "A7", "4": "A6", "5": "~{IOSEL}", "16": V, "8": G,
            "15": "~{USB_CS}", "14": None, "13": None, "12": "~{VDP_CS}", "11": "~{AY_CS}", "10": "~{PPI_CS}", "9": None, "7": None})
    pg.put(3, HC138, "U7", "74HCT138 I/O 00h-7Fh",
           {"1": "A3", "2": "A4", "3": "A5", "6": "A6", "4": "A7", "5": "~{IOSEL}", "16": V, "8": G,
            "15": None, "14": None, "13": None, "12": None, "11": None, "10": None, "9": None, "7": "~{MAP_CS}"})
    pg.put(3, HC32, "U8", "74HCT32",
           {"1": "~{IORQ}", "2": "M1", "3": "~{IOSEL}", "4": "~{MREQ}", "5": "PA19", "6": "~{ROMCS}",
            "9": "~{MREQ}", "10": "~{PA19}", "8": "~{RAMCS}", "12": "~{MAP_CS}", "13": "~{WR}", "11": "~{MAPWR}", "14": V, "7": G})
    pg.put(0, HC32, "U9", "74HCT32",
           {"1": "~{MAPWR}", "2": "A2", "3": "~{PGWR}", "4": "~{MAPWR}", "5": "~{A2}", "6": "~{ENWR}",
            "9": "~{VDP_CS}", "10": "~{WR}", "8": "~{CSW}", "12": "~{VDP_CS}", "13": "~{RD}", "11": "~{CSR}", "14": V, "7": G})
    pg.put(0, HC04, "U10", "74HCT04",
           {"1": "~{M1}", "2": "M1", "3": "PA19", "4": "~{PA19}", "5": "A2", "6": "~{A2}", "9": "~{RESET}", "8": "RESET",
            "11": "CPUCLK", "10": "ZCLK", "13": "A0", "12": "~{A0}", "14": V, "7": G})
    pg.put(1, JMP, "JP1", "Flash write enable", {"1": "~{WR}", "2": "~{FLWE}"})
    for i, net in enumerate(["PA14", "PA15", "PA16", "PA17", "PA18", "PA19"]):
        pg.two(RES, f"R{1 + i}", "10k", net, G)  # paging off: the page lines read 0
    for i, net in enumerate(["~{NMI}", "~{WAIT}", "~{BUSRQ}", "~{INT}", "~{FLWE}"]):
        pg.two(RES, f"R{7 + i}", "10k", V, net)
    decouple(pg)
    cpu = pg

    # --- page 3: video -----------------------------------------------------------------------------------------------
    pg = Layout(proj.page("Video: TMS9918A and VRAM", "video.kicad_sch"), 4)
    t = {"24": "D7", "23": "D6", "22": "D5", "21": "D4", "20": "D3", "19": "D2", "18": "D1", "17": "D0",  # CD0 is the MSB
         "13": "A0", "14": "~{CSW}", "15": "~{CSR}", "16": "VDP_INT", "34": "~{RESET}", "39": "VXT1", "40": "VXT2",
         "38": "CPUCLK", "37": None, "33": V, "12": G, "1": "~{VRAS}", "2": "~{VCAS}", "11": "VR~{W}", "36": "COMVID",
         "35": "EXTVDP"}
    t.update({str(p): f"VAD{i}" for i, p in enumerate([10, 9, 8, 7, 6, 5, 4, 3])})
    t.update({str(p): f"VRD{i}" for i, p in enumerate([32, 31, 30, 29, 28, 27, 26, 25])})
    pg.put(0, TMS, "U15", "TMS9918A", t)
    pg.put(0, XTAL, "Y1", "10.738635 MHz", {"1": "VXT1", "2": "VXT2"})
    # 16 KB VRAM: 62256 SRAM behind row, column and write-data latches (jblang/TMS9918A, after Tom LeMense).
    # The VDP puts the row address on AD1-AD7 at /RAS and the column address at /CAS; AD0 carries data only.
    vad = {str(p): f"VAD{i}" for i, p in enumerate([2, 3, 4, 5, 6, 7, 8, 9])}
    pg.put(1, HC574, "U17", "74HCT574 VRAM row latch",
           dict(vad, **{"11": "VROW", "1": G, "20": V, "10": G, "19": None, "18": "VMA0", "17": "VMA1", "16": "VMA2", "15": "VMA3",
                        "14": "VMA10", "13": "VMA4", "12": "VMA5"}))
    pg.put(1, HC574, "U24", "74HCT574 VRAM column latch",
           dict(vad, **{"11": "VCOL", "1": G, "20": V, "10": G, "19": None, "18": "VMA11", "17": "VMA6", "16": "VMA7", "15": "VMA9",
                        "14": "VMA12", "13": "VMA8", "12": "VMA13"}))
    pg.put(2, HC574, "U25", "74HCT574 VRAM write data",
           dict(vad, **{"11": "~{VRW}", "1": "VR~{W}", "20": V, "10": G, "19": "VRD0", "18": "VRD1", "17": "VRD2", "16": "VRD3",
                        "15": "VRD4", "14": "VRD5", "13": "VRD6", "12": "VRD7"}))
    pg.put(2, HC04, "U26", "74HCT04 VRAM strobes",
           {"1": "~{VRAS}", "2": "VROW", "3": "~{VCAS}", "4": "VCAS1", "5": "VCAS1", "6": "VCAS2", "9": "VCAS2", "8": "VCOL",
            "11": "VR~{W}", "10": "~{VRW}", "13": G, "12": None, "14": V, "7": G})  # VCOL: /CAS inverted and delayed by three gates
    m = {"10": "VMA0", "9": "VMA1", "8": "VMA2", "7": "VMA3", "6": "VMA4", "5": "VMA5", "4": "VMA6", "3": "VMA7", "25": "VMA8",
         "24": "VMA9", "21": "VMA10", "23": "VMA11", "2": "VMA12", "26": "VMA13", "1": "VMA13", "28": V, "14": G,
         "20": "~{VCAS}", "22": "~{VRW}", "27": "VR~{W}"}
    m.update({str(p): f"VRD{i}" for i, p in enumerate([11, 12, 13, 15, 16, 17, 18, 19])})  # VRDn = RDn = data bit n of ADn
    pg.put(3, SRAM32K, "U16", "62256 VRAM (16 KB used)", m)
    pg.put(3, NPN, "Q1", "MMBT4401 video buffer", {"1": "VID_B", "3": "VID_C", "2": "VID_OUT"})
    pg.two(CAP, "C30", "22p", "VXT1", G)  # TI: 15-39 pF typical; jblang uses 16 pF
    pg.two(CAP, "C31", "22p", "VXT2", G)
    pg.two(DIODE, "D3", "1N5819HW", "VDP_INT", "~{INT}")
    pg.two(RES, "R25", "130", "COMVID", "VID_B")
    pg.two(RES, "R26", "470", "VID_B", G)
    pg.two(RES, "R27", "75", "VID_OUT", G)
    pg.two(FBEAD, "FB1", "Ferrite bead", V, "VID_C")
    pg.two(CAP, "C29", "100n", "VID_C", G)
    decouple(pg)

    # --- page 4: sound and joysticks --------------------------------------------------------------------------------
    pg = Layout(proj.page("Sound and joysticks", "sound.kicad_sch"), 4)
    a = {str(p): d for p, d in zip([37, 36, 35, 34, 33, 32, 31, 30], D)}
    a.update({"27": "BDIR", "29": "BC1", "28": V, "25": V, "24": G, "23": "~{RESET}", "22": "AYCLK", "39": None, "26": None,
              "40": V, "1": G, "4": "AY_A", "3": "AY_B", "38": "AY_C",
              "21": "IOA0", "20": "IOA1", "19": "IOA2", "18": "IOA3", "17": "IOA4", "16": "IOA5", "15": "IOA6", "14": "IOA7",
              "13": None, "12": None, "11": None, "10": None, "9": None, "8": None, "7": "JOYSEL", "6": None, "2": None, "5": None})
    pg.put(0, AY, "U18", "AY-3-8910", a)
    pg.put(1, HC02, "U12", "74HCT02 AY bus control, USB WR",
           {"2": "~{AY_CS}", "3": "~{WR}", "1": "BDIR", "5": "~{AY_CS}", "6": "A0", "4": "BC1",
            "8": "~{USBWRQ}", "9": "A0", "10": "USBWR", "11": G, "12": G, "13": None, "14": V, "7": G})
    pg.put(1, HC157, "U19", "74HCT157 joystick directions",
           {"1": "JOYSEL", "15": G, "2": "J1_UP", "3": "J2_UP", "5": "J1_DOWN", "6": "J2_DOWN", "11": "J1_LEFT", "10": "J2_LEFT",
            "14": "J1_RIGHT", "13": "J2_RIGHT", "16": V, "8": G, "4": "IOA0", "7": "IOA1", "9": "IOA2", "12": "IOA3"})
    pg.put(1, HC157, "U20", "74HCT157 joystick buttons",
           {"1": "JOYSEL", "15": G, "2": "J1_B1", "3": "J2_B1", "5": "J1_B2", "6": "J2_B2", "11": G, "10": G, "14": G, "13": G,
            "16": V, "8": G, "4": "IOA4", "7": "IOA5", "9": None, "12": None})
    for col, (ref, j) in ((2, ("J4", "J1")), (3, ("J5", "J2"))):
        pg.put(col, DB9, ref, f"Joystick {j[1]} (Atari / Sega)",
               {"1": f"{j}_UP", "2": f"{j}_DOWN", "3": f"{j}_LEFT", "4": f"{j}_RIGHT", "5": V, "6": f"{j}_B1",
                "7": f"{j}_P7", "8": G, "9": f"{j}_B2", "0": G})
    for r, net in zip((16, 17, 18), ("AY_A", "AY_B", "AY_C")):
        pg.two(RES, f"R{r}", "3k", net, G)  # load for the AY outputs (as electrified/rc2014-ym2149)
    for r, (val, x, y) in zip(range(19, 23), (("1k", "AY_A", "MIX_L"), ("2.2k", "AY_B", "MIX_L"), ("2.2k", "AY_B", "MIX_R"),
                                              ("1k", "AY_C", "MIX_R"))):
        pg.two(RES, f"R{r}", val, x, y)
    pg.two(CAP, "C1", "10u", "MIX_L", "AUD_L")
    pg.two(CAP, "C2", "10u", "MIX_R", "AUD_R")
    pg.two(RES, "R23", "47k", "AUD_L", G)
    pg.two(RES, "R24", "47k", "AUD_R", G)
    r = iter(range(33, 48))  # 10k pull-ups: joystick lines, the spare AY inputs and the joystick select
    for net in [f"{j}_{k}" for j in ("J1", "J2") for k in ("UP", "DOWN", "LEFT", "RIGHT", "B1", "B2")] + ["IOA6", "IOA7", "JOYSEL"]:
        pg.two(RES, f"R{next(r)}", "10k", V, net)
    pg.two(RES, "R30", "1k", V, "J1_P7")
    pg.two(RES, "R31", "1k", V, "J2_P7")
    decouple(pg)

    # --- page 5: keyboard and USB -----------------------------------------------------------------------------------
    pg = Layout(proj.page("Keyboard and USB", "keyboard_usb.kicad_sch"), 4)
    pp = {str(p): d for p, d in zip([34, 33, 32, 31, 30, 29, 28, 27], D)}
    pp.update({"6": "~{PPI_CS}", "5": "~{RD}", "36": "~{WR}", "9": "A0", "8": "A1", "35": "RESET", "26": V, "7": G,
               "4": "PPA0", "3": "PPA1", "2": "PPA2", "1": "PPA3", "40": "PPA4", "39": "PPA5", "38": "PPA6", "37": "PPA7",
               "18": "KCOL0", "19": "KCOL1", "20": "KCOL2", "21": "KCOL3", "22": "KCOL4", "23": "KCOL5", "24": "KCOL6",
               "25": "KCOL7", "14": "KROW0", "15": "KROW1", "16": "KROW2", "17": "KROW3", "13": "PPC4", "12": "PPC5",
               "11": "PPC6", "10": "PPC7"})
    pg.put(0, PPI, "U21", "82C55A", pp)
    pg.put(1, MCU, "U22", "ATmega328P-AU: PS/2 to key matrix",
           {"29": "KB_RST", "23": "KROW0", "24": "KROW1", "25": "KROW2", "26": "KROW3", "27": None, "28": None, "19": None,
            "22": None, "12": "PS2_CLK", "13": "PS2_DATA", "14": None, "15": "KB_MOSI", "16": "KB_MISO", "17": "KB_SCK",
            "7": None, "8": None, "4": V, "6": V, "18": V, "20": "KB_AREF", "3": G, "5": G, "21": G,
            "30": "KCOL0", "31": "KCOL1", "32": "KCOL2", "1": "KCOL3", "2": "KCOL4", "9": "KCOL5", "10": "KCOL6", "11": "KCOL7"})
    pg.put(1, PS2, "J6", "PS/2 keyboard (panel socket)", {"1": V, "2": "PS2_CLK", "3": "PS2_DATA", "4": G})
    pg.put(1, ISP, "J7", "ISP for the ATmega", {"1": "KB_MISO", "2": V, "3": "KB_SCK", "4": "KB_MOSI", "5": "KB_RST", "6": G})
    pg.put(0, EXP, "J8", "Expansion (8255 PA, PC4-7)",
           {"1": "PPA0", "2": "PPA1", "3": "PPA2", "4": "PPA3", "5": "PPA4", "6": "PPA5", "7": "PPA6", "8": "PPA7",
            "9": "PPC4", "10": "PPC5", "11": "PPC6", "12": "PPC7", "13": V, "14": G})
    usb = {str(p): d for p, d in zip([1, 5, 3, 11, 2, 9, 10, 6], D)}
    usb.update({"13": "~{USBRD}", "14": "USBWR", "19": "USB_RST", "20": V, "4": V, "17": "USB_3V3", "7": G, "18": G, "21": G,
                "25": G, "26": G, "23": "USB_RXF", "22": "USB_TXE", "12": "USB_PWREN", "15": "USB_DP", "16": "USB_DM",
                "27": None, "28": None, "8": None, "24": None})  # self powered, 5 V I/O (DS_FT245R figure 6.2)
    pg.put(2, FT245, "U23", "FT245RL USB FIFO", usb)
    pg.put(2, USBC, "J10", "USB-C (GCT USB4105-GF-A)",
           {"A4": "USB_VBUS", "A9": "USB_VBUS", "B4": "USB_VBUS", "B9": "USB_VBUS", "A6": "USB_DP", "B6": "USB_DP",
            "A7": "USB_DM", "B7": "USB_DM", "A5": "USB_CC1", "B5": "USB_CC2", "A8": None, "B8": None,
            "A1": G, "A12": G, "B1": G, "B12": G, "S1": "USB_SHIELD"})
    # USB FIFO strobes: 80h read = RD# (active low), 80h write = WR (active high, latches on its falling edge), 81h read = status
    pg.put(3, HC32, "U27", "74HCT32 USB FIFO strobes",
           {"1": "~{USB_CS}", "2": "~{RD}", "3": "~{USBRDQ}", "4": "~{USBRDQ}", "5": "A0", "6": "~{USBRD}",
            "9": "~{USBRDQ}", "10": "~{A0}", "8": "~{USBST}", "12": "~{USB_CS}", "13": "~{WR}", "11": "~{USBWRQ}", "14": V, "7": G})
    pg.put(3, HC125, "U28", "74HCT125 USB status on D0, D1",
           {"1": "~{USBST}", "2": "USB_RXF", "4": "~{USBST}", "5": "USB_TXE", "10": V, "9": G, "13": V, "12": G,
            "3": "D0", "6": "D1", "8": None, "11": None, "14": V, "7": G})
    pg.two(RES, "R12", "10k", V, "KB_RST")
    pg.two(RES, "R13", "4.7k", V, "PS2_CLK")
    pg.two(RES, "R14", "4.7k", V, "PS2_DATA")
    pg.two(CAP, "C5", "100n", "KB_AREF", G)
    # FT245RL: /RESET follows the PC's VBUS (4.7k / 10k), so the chip stays in reset while the PC is off
    pg.two(RES, "R48", "4.7k", "USB_VBUS", "USB_RST")
    pg.two(RES, "R49", "10k", "USB_RST", G)
    pg.two(RES, "R50", "10k", V, "USB_PWREN")
    pg.two(RES, "R51", "5.1k", "USB_CC1", G)  # Rd: tells a USB-C host this is a device
    pg.two(RES, "R52", "5.1k", "USB_CC2", G)
    pg.two(CAP, "C36", "100n", "USB_3V3", G)
    pg.two(CAP, "C37", "4.7u", V, G)
    pg.two(CAP, "C38", "100n (U23)", V, G)
    pg.two(CAP, "C39", "10n", "USB_SHIELD", G)
    decouple(pg)

    # --- page 6: power, reset and TV ----------------------------------------------------------------------------------
    pg = Layout(proj.page("Power, reset and TV", "power_tv.kicad_sch"), 3)
    pg.put(0, DCJACK, "J1", "12 V DC in", {"1": "+12V_IN", "2": G, "3": G})
    pg.put(0, REG, "U14", "R-78E5.0-1.0 (or 7805)", {"1": "+12V", "2": G, "3": V})
    pg.put(0, PWR_FLAG, "#FLG1", "PWR_FLAG", {"1": G}, gap=7.62)
    pg.put(0, PWR_FLAG, "#FLG2", "PWR_FLAG", {"1": "+12V"}, gap=7.62)
    pg.put(0, DS1813, "U13", "DS1813-5 reset", {"2": V, "3": G, "1": "~{RESET}"})
    pg.put(0, BTN, "SW1", "Reset", {"1": "~{RESET}", "2": G})
    pg.put(1, TVHDR, "J2", "TV: cable to a SCART plug",
           {"1": "VID_OUT", "2": G, "3": "AUD_L", "4": "AUD_R", "5": G, "6": "SCART_FS", "7": "BLANK", "8": G,
            "9": "EXTVDP", "10": V})
    pg.two(DIODE, "D1", "1N5819HW", "+12V", "+12V_IN")
    pg.two(CPOL, "C3", "100u", "+12V", G)
    pg.two(CPOL, "C4", "100u", V, G)
    pg.two(RES, "R15", "10k", V, "~{RESET}")
    pg.two(RES, "R28", "75", "BLANK", G)
    pg.two(RES, "R29", "1k", "+12V", "SCART_FS")
    pg.two(RES, "R32", "1k", V, "LED_A")
    pg.two(LED, "D2", "Power", G, "LED_A")
    return proj


def main():
    proj = build()
    proj.notes = [(20, 20, "ZL-80 board, generated by hardware/kicad/gen_schematic.py from docs/hardware.md.\n"
                           "Each box is a page. Labels with the same name are connected; the labels in a frame\n"
                           "(global labels) go to other pages.\n"
                           "NOT BUILT OR TESTED. Check every pin against the datasheets before ordering a board.", 2)]
    proj.write_library(HERE)
    proj.write(HERE, date="2026-10-27", rev="0.3",
               comments=("Z80 3.58 MHz, TMS9918A + 16 KB SRAM VRAM, AY-3-8910, 512 KB flash + 512 KB SRAM, 82C55 + PS/2, FT245RL USB-C",
                         "Design only: not built or tested"))
    nets = proj.nets
    with open(os.path.join(HERE, "zl80-netlist.txt"), "w", encoding="utf-8", newline="\n") as fh:
        for net in sorted(nets, key=lambda k: (k.strip("~{}").lower(), k)):
            fh.write(f"{net}: {' '.join(sorted(nets[net]))}\n")
    print(f"{len(proj.refs)} parts, {len(nets)} nets, pages: "
          + ", ".join(f"{sh.title} ({sh.paper})" for sh, _, _ in proj.pages))
    for k, v in nets.items():
        if len(v) < 2:
            print("NET WITH ONE PIN:", k, v)


if __name__ == "__main__":
    main()
