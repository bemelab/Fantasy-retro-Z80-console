# ZL-80 board schematic

The KiCad schematic of the board described in [docs/hardware.md](../../docs/hardware.md).

**Not built or tested.** Check every pin against the datasheets before you order a board.

| File | What it is |
|---|---|
| `zl80.kicad_pro`, `zl80.kicad_sch` | The KiCad project and schematic (KiCad 7 format; KiCad 8 and 9 open it). |
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
- Active-low signals use KiCad's overbar syntax, for example `~{RD}`.
- The symbols are defined inside the schematic file, so no KiCad library is needed. Footprints are standard KiCad names for through-hole parts. The connectors (SCART, DB9, PS/2) have no footprint yet: pick the ones that match the parts you buy.

## Sources for the pinouts and circuits

- TMS9918A pins, the VRAM circuit (62256 SRAM, three 74HCT574 latches) and the video output stage: TI's TMS9918A data manual and [jblang/TMS9918A](https://github.com/jblang/TMS9918A).
- AY-3-8910 pins and bus control: the General Instrument datasheet and [electrified/rc2014-ym2149](https://github.com/electrified/rc2014-ym2149).
- UM245R pins, jumpers and self-powered wiring: FTDI's UM245R datasheet (DS_UM245R, FT_000202), sections 4.2 and 7.2.
- Other chips: the manufacturers' datasheets (Zilog, Microchip, Alliance, Renesas, TI).
