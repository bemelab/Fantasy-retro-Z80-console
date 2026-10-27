# ZL-80 board schematic

The KiCad schematic of the board described in [docs/hardware.md](../../docs/hardware.md).

**Not built or tested.** Check every pin against the datasheets before you order a board.

| File | What it is |
|---|---|
| `zl80.kicad_pro`, `zl80.kicad_sch` | The KiCad project and its root sheet (KiCad 7 format; KiCad 8 and 9 open it). The root sheet has one box per page; double-click a box to open the page. |
| `cpu_memory.kicad_sch` | Page 2: Z80, flash, SRAM, page registers, I/O decoding. |
| `video.kicad_sch` | Page 3: TMS9918A, VRAM (62256 and latches), crystal, video output stage. |
| `sound.kicad_sch` | Page 4: AY-3-8910, its bus control, joystick multiplexers, DB9 ports, audio mix. |
| `keyboard_usb.kicad_sch` | Page 5: 82C55, ATmega328P and PS/2 socket, expansion header, UM245R USB FIFO. |
| `power_tv.kicad_sch` | Page 6: 12 V input, 5 V regulator, reset, SCART and the RGB header. |
| `zl80.kicad_sym`, `sym-lib-table` | The board's symbols as a project library, so KiCad finds the `zl80` library. |
| `gen_schematic.py` | Generates the schematic. Change the circuit here, not in KiCad. |
| `sch.py` | The small schematic writer that `gen_schematic.py` uses. |
| `check_schematic.py` | Checks that the file parses and that every pin is either connected or marked as not connected. |
| `zl80-netlist.txt` | Every net with the pins on it, for checking against datasheets. |

To regenerate the schematic and run the check:

```
python gen_schematic.py
python check_schematic.py
```

With KiCad installed, also run its electrical rules check; it should report 0 violations. The netlist KiCad exports has the same 187 nets as `zl80-netlist.txt` (KiCad leaves out the PWR_FLAG markers).

```
kicad-cli sch erc --severity-all zl80.kicad_sch
```

## How the schematic is drawn

- Each chip is a box with a short wire and a net label on every pin. Pins with the same label are connected; there are no long wires.
- A signal that goes to another page has a global label (the label in a frame); KiCad lists the pages it reaches next to it. Signals that stay on one page have plain labels.
- Each chip's 100 nF decoupling capacitor is on the same page; its value says which chip it belongs to, for example `100n (U15)`.
- Active-low signals use KiCad's overbar syntax, for example `~{RD}`.
- The symbols are defined inside the schematic file, so no KiCad library is needed. Footprints are standard KiCad names for through-hole parts. The connectors (SCART, DB9, PS/2) have no footprint yet: pick the ones that match the parts you buy.

## Sources for the pinouts and circuits

- TMS9918A pins, the VRAM circuit (62256 SRAM, three 74HCT574 latches) and the video output stage: TI's TMS9918A data manual and [jblang/TMS9918A](https://github.com/jblang/TMS9918A).
- AY-3-8910 pins and bus control: the General Instrument datasheet and [electrified/rc2014-ym2149](https://github.com/electrified/rc2014-ym2149).
- UM245R pins, jumpers and self-powered wiring: FTDI's UM245R datasheet (DS_UM245R, FT_000202), sections 4.2 and 7.2.
- Other chips: the manufacturers' datasheets (Zilog, Microchip, Alliance, Renesas, TI).
