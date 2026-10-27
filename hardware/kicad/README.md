# ZL-80 board schematic

The KiCad schematic of the board described in [docs/hardware.md](../../docs/hardware.md).

**Not built or tested.** Check every pin against the datasheets before you order a board.

| File | What it is |
|---|---|
| `zl80.kicad_pro`, `zl80.kicad_sch` | The KiCad project and its root sheet (KiCad 7 format; KiCad 8 and 9 open it). The root sheet has one box per page; double-click a box to open the page. |
| `cpu_memory.kicad_sch` | Page 2: Z80, flash, SRAM, page registers, I/O decoding. |
| `video.kicad_sch` | Page 3: TMS9918A, VRAM (62256 and latches), crystal, video output stage. |
| `sound.kicad_sch` | Page 4: AY-3-8910, its bus control, joystick multiplexers, DB9 ports, audio mix. |
| `keyboard_usb.kicad_sch` | Page 5: 82C55, ATmega328P and the PS/2 header, expansion header, FT245RL USB FIFO and USB-C socket. |
| `power_tv.kicad_sch` | Page 6: 12 V input, 5 V regulator, reset, and the TV header for a SCART cable. |
| `zl80.kicad_sym`, `sym-lib-table` | The board's symbols as a project library, so KiCad finds the `zl80` library. |
| `gen_schematic.py` | Generates the schematic. Change the circuit here, not in KiCad. |
| `sch.py` | The small schematic writer that `gen_schematic.py` uses. |
| `check_schematic.py` | Checks that the file parses and that every pin is either connected or marked as not connected. |
| `zl80-netlist.txt` | Every net with the pins on it, for checking against datasheets. |
| `check_footprints.py` | Checks that every part's footprint exists in KiCad's library and has a pad for each symbol pin. |
| `zl80.kicad_pcb` | The routed 4-layer board, 138 x 105 mm: tracks on F.Cu, In2.Cu and B.Cu, a whole GND plane on In1.Cu, a +5V fill on In2.Cu. |
| `zl80.dsn`, `zl80.ses` | What went to Freerouting and the routes it sent back. `gen_pcb.py import zl80.ses` restores the tracks after `gen_pcb.py` has placed the parts again. |
| `gen_pcb.py` | Builds the board with KiCad's Python: places the parts, draws the outline and planes, writes `zl80.dsn` for Freerouting, and reads the routed `.ses` back. |

To regenerate the schematic and run the check:

```
python gen_schematic.py
python check_schematic.py
```

With KiCad installed, also run its electrical rules check; it should report 0 violations. The netlist KiCad exports has the same 187 nets as `zl80-netlist.txt` (KiCad leaves out the PWR_FLAG markers).

```
kicad-cli sch erc --severity-all zl80.kicad_sch
```

## The PCB

`gen_pcb.py` runs with KiCad's own Python (KiCad's `bin` folder must be on PATH). It reads the parts and nets from `gen_schematic.py`, so the board always matches the schematic.

```
set PATH=D:\Program Files\KiCad\9.0\bin;%PATH%
python gen_pcb.py                      (KiCad's python.exe) places the parts, writes zl80.kicad_pcb and zl80.dsn
freerouting-cli -de zl80.dsn -do zl80.ses -mp 100
python gen_pcb.py import zl80.ses      adds the routed tracks to zl80.kicad_pcb
kicad-cli pcb drc zl80.kicad_pcb
```

Freerouting 2.5.0 routed the board in about 25 minutes (`-mp 200`). Two settings in the DSN that `gen_pcb.py` writes make that work: only the GND net may use In1.Cu, so the GND plane stays whole and GND pads reach it through vias, and the routing boundary sits 0.55 mm inside the board edge. KiCad's DRC with the schematic parity check reports 0 violations, 0 unconnected pads and 0 footprint errors; what is left are silkscreen warnings (labels over pads and over each other), which the board maker clips.

Placement: the 12 V jack, the regulator, the USB-C socket and both joystick ports along the top edge; below them one row of the four DIP-40 sockets (82C55, Z80, TMS9918A, AY-3-8910 from left to right); each group's surface-mount parts are packed beside and below its socket, each chip next to its own 100 nF capacitor. All surface-mount parts are on the top side, so the board needs assembly on one side only. Design rules: 0.15 mm clearance, 0.2 mm tracks, 0.6/0.3 mm vias, all inside JLCPCB's 4-layer limits.

## How the schematic is drawn

- Each chip is a box with a short wire and a net label on every pin. Pins with the same label are connected; there are no long wires.
- A signal that goes to another page has a global label (the label in a frame); KiCad lists the pages it reaches next to it. Signals that stay on one page have plain labels.
- Each chip's 100 nF decoupling capacitor is on the same page; its value says which chip it belongs to, for example `100n (U15)`.
- Active-low signals use KiCad's overbar syntax, for example `~{RD}`.
- The symbols are defined inside the schematic file, so no KiCad library is needed. Footprints are standard KiCad names for through-hole parts. The connectors (SCART, DB9, PS/2) have no footprint yet: pick the ones that match the parts you buy.

## Sources for the pinouts and circuits

- TMS9918A pins, the VRAM circuit (62256 SRAM, three 74HCT574 latches) and the video output stage: TI's TMS9918A data manual and [jblang/TMS9918A](https://github.com/jblang/TMS9918A).
- AY-3-8910 pins and bus control: the General Instrument datasheet and [electrified/rc2014-ym2149](https://github.com/electrified/rc2014-ym2149).
- FT245RL pins and its self-powered circuit: FTDI DS_FT245R (FT_000052) v2.14, the SSOP-28 pin table and figure 6.2.
- SMD packages: Microchip DS20005022F (SST39SF040 PLCC-32), DS40002061B (ATmega328P TQFP-32), Alliance AS6C4008 and AS6C62256, onsemi MMBT4401, GCT USB4105 drawing.
- Other chips: the manufacturers' datasheets (Zilog, Microchip, Alliance, Renesas, TI).
