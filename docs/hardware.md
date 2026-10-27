# ZL-80 hardware, version 1

This is the plan for a real ZL-80 console that runs the same machine code as the emulator in `index.html`. The rule is simple: **the emulator copies this board exactly**. A program that runs in the emulator's hardware mode must run on the board without changes, and the emulator must refuse anything the board cannot do.

Status: design. Nothing here is built or tested yet. The schematic is in `hardware/kicad/` (see "Schematic"). The items in "Check before building" must be confirmed against the datasheets.

## Overview

```
                 +-----------------------------+
 10.738635 MHz --| TMS9918A VDP                |--- composite video --> SCART pin 20
   crystal       |  16 KB VRAM: 62256 + latches|
                 |  CPUCLK 3.58 MHz -----------|---+
                 |  /INT (every frame) --------|---|--+
                 +-----------------------------+   |  |
                                                   v  v
 512 KB flash --+                              +---------+
 512 KB SRAM ---+-- 16 KB page mapper ---------|  Z80    |
                                               | 3.58 MHz|
 AY-3-8910 <-- 1.79 MHz (CPUCLK / 2)           +---------+
   A B C ----> stereo mix --> SCART audio L/R      |
   port A <--- 2 joysticks (DB9)                   |
 8255 PPI <--- ATmega328P <--- PS/2 PC keyboard    |
 UM245R USB FIFO <-- USB <-- PC / browser ---------+
```

## Main parts

| Part | Choice | Why |
|---|---|---|
| CPU | Z80 (CMOS, Z84C00), 3.579545 MHz | Clocked from the VDP's CPUCLK pin, so one crystal drives CPU, video and sound in step. A 74HCT04 gate brings CPUCLK to the full 5 V swing the CMOS Z80 needs. |
| Video | TMS9918A | NTSC composite video on one pin, and CPUCLK for the Z80. The TMS9928A (RGB through a converter) is software-identical but has no CPUCLK pin, so it would need its own CPU clock; it is left for a later RGB version. |
| VRAM | 16 KB: 62256 SRAM, three 74HCT574 latches, one 74HCT04 | A TMS9918A cannot drive two 16Kx4 DRAMs (TMS4416) directly. This SRAM circuit is the one on jblang/TMS9918A (after Tom LeMense), a board people have built. |
| Sound | AY-3-8910, 1.789773 MHz | 40 pins: I/O port A for the joysticks, port B bit 6 to choose joystick 1 or 2. (The emulator also offers the AY-3-8912; see "Joysticks".) |
| ROM | 512 KB flash, SST39SF040 (DIP-32) | The largest common 5 V parallel flash in DIP. It can be rewritten in the console. |
| RAM | 512 KB SRAM, AS6C4008-55PCN (DIP-32) | The largest common 5 V SRAM in DIP. Its pins 3, 29 and 31 differ from the flash, so the sockets are not interchangeable. The "AS6C4008A" is 3.3 V only. |
| Keyboard | PS/2 PC keyboard, ATmega328P, 8255 PPI | See "Keyboard". |
| Joysticks | 2 x DB9 (Atari/Sega pinout), two 74HCT157 | Same wiring idea as MSX. |
| USB | UM245R module (FTDI FT245R USB FIFO, 24-pin DIP footprint) | Loads programs from a PC or straight from the browser (Web Serial): the PC sees a serial port. 256-byte receive and 128-byte transmit FIFOs; when the receive FIFO is full the PC waits, so no byte is lost. Up to about 1 MB/s. |
| TV | SCART: composite video, stereo audio, 4:3 switching | See "SCART". |
| Glue | 74HCT138 x2, 74HCT32 x3, 74HCT02, 74HCT04, 74HCT74, 74HCT125, 74HCT670 x2 | See "Address decoding". HCT parts accept the TTL-level outputs of the NMOS TMS9918A and AY-3-8910. |

## Clocks and timing

- VDP crystal: 10.738635 MHz between XTAL1 and XTAL2, with 22 pF to ground on each side (TI gives 15-39 pF; jblang uses 16 pF).
- Z80: CPUCLK = 10.738635 / 3 = **3.579545 MHz**, through one 74HCT04 gate.
- AY: CPUCLK / 2 = **1.789773 MHz** from the second half of the 74HCT74.
- Frame: 262 lines x 342 pixel clocks, **59.92 frames per second**. The Z80 runs at 2/3 of the pixel clock, so a frame is exactly **59,736 Z80 T-states**.

## Memory

The Z80 sees 64 KB, split into four 16 KB banks. Each bank can show any of 64 pages: pages 0 to 31 are flash, pages 32 to 63 are RAM. This page mapper is the same as on the Zeta SBC v2 and the RC2014 512K ROM 512K RAM module (two 74HCT670 page registers).

| Port | Use |
|---|---|
| 0x78 | Page for bank 0 (0x0000-0x3FFF) |
| 0x79 | Page for bank 1 (0x4000-0x7FFF) |
| 0x7A | Page for bank 2 (0x8000-0xBFFF) |
| 0x7B | Page for bank 3 (0xC000-0xFFFF) |
| 0x7C | Bit 0 = 1 turns paging on. After reset it is off: flash page 0 shows in all four banks and writes go nowhere. |

Normal map after the kernel starts:

| Address | Page | Contents |
|---|---|---|
| 0x0000-0x3FFF | flash 0 | Kernel: reset, interrupt handler at 0x0038, serial loader, runtime library, font, note table. Always mapped. |
| 0x4000-0xBFFF | RAM 32, 33 | Program code (up to 32 KB). |
| 0xC000-0xFFFF | RAM 34 | 0xC000 variables (1024), 0xC400 arrays (44 of up to 256 bytes), 0xF000 sprite rows, 0xF100-0xFEFF stack (starts at 0xFF00), 0xFF00 kernel variables. |

The other pages (flash 1 to 31, RAM 35 to 63, about 900 KB) hold stored programs, levels, music and pictures. A later `bank` command in ZL can switch banks 1 to 3. Bank 0 never changes, so the interrupt handler is always there.

## Address decoding

All decoding uses HCT logic.

- **Memory:** two 74HCT670 hold a 6-bit page number for each bank. Their read address is A14 and A15 (the bank). The outputs PA14-PA19 go to address lines A14-A18 of both memory chips, and PA19 chooses the chip: 0 = flash, 1 = RAM. Flash /CE = /MREQ OR PA19; RAM /CE = /MREQ OR NOT PA19.
- **Paging off at reset:** a 74HCT74 flip-flop (cleared by /RESET) drives the 670 output enables. With paging off the outputs float, and six 10 kohm pull-downs make PA14-PA19 read 0: flash page 0 in every bank.
- **Flash writes:** flash /WE goes through jumper JP1 from /WR. With JP1 open, nothing can write the flash. With it closed the flash still needs its unlock sequence.
- **I/O:** IOSEL = /IORQ OR M1, so interrupt-acknowledge cycles select nothing. One 74HCT138 (A7 = 1, A6 = 0) gives 80h-87h (USB FIFO), 98h-9Fh (VDP), A0h-A7h (AY) and A8h-AFh (8255). A second 74HCT138 (A7 = 0, A6 = 1) gives 78h-7Fh for the page registers (A2 = 0) and the paging flip-flop (A2 = 1).
- **VDP:** /CSW = VDPSEL OR /WR, /CSR = VDPSEL OR /RD, MODE = A0. CD0 is the VDP's most significant bit, so CD0-CD7 go to D7-D0.
- **AY:** BC2 = A8 = +5 V, /A9 = GND. BDIR = NOR(AYSEL, /WR) and BC1 = NOR(AYSEL, A0): A0h write = latch address, A1h write = write data, A2h read = read data.
- **USB FIFO (UM245R):** RD# = USBSEL OR /RD OR A0 (port 80h read); WR = NOR(USBSEL OR /WR, A0) (port 80h write; the FT245R latches the byte when WR falls); a 74HCT125 puts RXF# on D0 and TXE# on D1 when port 81h is read (USBSEL OR /RD OR NOT A0). The FT245R timing (RD# and WR pulses of at least 50 ns, data valid 50 ns after RD#) is well inside a Z80 I/O cycle.
- **UM245R power (self powered, DS_UM245R section 7.2):** jumper J2 open, the board's 5 V on VCC (pins 15 and 21), jumper J1 on pins 2-3 so VIO = VCC = 5 V logic. Pin 14 (USB 5 V) goes to PU2 (pin 16) and PU1 (pin 17) to RST# (pin 20), so the FT245R stays in reset while the PC is off. FTDI also recommends setting the power descriptor in its EEPROM to self powered (FT_PROG).
- **8255:** RESET (active high) = NOT /RESET.
- **Interrupt:** the VDP /INT reaches the Z80 /INT through a BAT85 Schottky diode (cathode at the VDP) with a 10 kohm pull-up, as on jblang's board, so other sources can be added later.

## I/O ports

The Z80 decodes the low 8 address bits for I/O. The video, sound and keyboard ports are the MSX1 numbers, so MSX documentation and example code apply directly.

| Port | Device | Use |
|---|---|---|
| 0x78-0x7C | Page mapper | See "Memory". |
| 0x80 | UM245R | USB data: read takes a byte from the receive FIFO, write puts one in the transmit FIFO |
| 0x81 | UM245R | USB status (read only): bit 0 = RXF# (0: a byte is waiting), bit 1 = TXE# (0: room to send); bits 2-7 are not driven |
| 0x98 | TMS9918A | VRAM data |
| 0x99 | TMS9918A | Control: register write and VRAM address (write), status (read) |
| 0xA0 | AY-3-8910/8912 | Register select |
| 0xA1 | AY-3-8910/8912 | Data write |
| 0xA2 | AY-3-8910/8912 | Data read |
| 0xA8 | 8255 port A | Free, 8 outputs (LEDs, expansion) |
| 0xA9 | 8255 port B | Keyboard row bits (read, 0 = key down) |
| 0xAA | 8255 port C | Bits 0-3: keyboard row select (write). Bit 4: joystick select on the AY-3-8912 board. Bits 5-7 free. |
| 0xAB | 8255 control | Write 0x82 at start: A out, B in, C out |

Any other port does nothing on the board. In the emulator's hardware mode it stops the program with an error.

## Interrupts

- TMS9918A /INT goes to the Z80 /INT. It fires once per frame when register 1 bit 5 is set.
- Mode IM 1: every interrupt calls 0x0038 in the kernel.
- The handler saves the registers, reads the VDP status at port 0x99 (this clears the interrupt), counts frames, scans the keyboard and joysticks into RAM, and returns with `EI` and `RETI`.
- ZL's `wait` becomes `HALT` loops that wake on this interrupt. That is why the emulator's hardware mode must emulate the interrupt and must never continue a `HALT` on its own.

## Keyboard

Choice: **a PS/2 PC keyboard, read by an ATmega328P that presents the MSX key matrix to an 8255 PPI.**

- The program writes a row number (0 to 10) to port 0xAA and reads that row's 8 keys from port 0xA9, with 0 meaning pressed. Every key has its own bit, so a game can see several keys held at once. A keyboard that only sends the last character cannot do this.
- Row 8 holds space and the arrow keys (bit 0 space, bit 4 left, bit 5 up, bit 6 down, bit 7 right), so ZL's `key` command keeps working.
- Wiring: 8255 PC0-PC3 (row select) go to ATmega PC0-PC3; ATmega PD0-PD7 drive the 8255 PB0-PB7 (columns); the PS/2 clock and data go to ATmega PB0 and PB1 with 4.7 kohm pull-ups. The ATmega runs on its internal 8 MHz oscillator and has its own ISP header.
- The ATmega firmware is not written yet. It must change the column lines within a few microseconds of a row change, because an `OUT` followed by an `IN` at 3.58 MHz leaves little time.
- A USB keyboard works only if it also speaks PS/2 (then a passive USB-to-PS/2 adapter is enough). Otherwise it would need a USB host converter.
- The emulator maps the PC keyboard to the same matrix.

## Joysticks

- Two DB9 ports, Atari/Sega pinout: up, down, left, right, two buttons.
- AY port A is the input: bits 0-3 directions, bits 4-5 buttons, 0 = pressed.
- Choosing joystick 1 or 2 depends on the sound chip:
  - **AY-3-8910:** port B is an output, and its bit 6 selects the joystick (0 = joystick 1). While port B is still an input after reset, a pull-up selects joystick 2, until the kernel sets register 7.
  - **AY-3-8912:** there is no port B. A 74HC157 switches port A between the two DB9 ports, and 8255 PC4 drives its select input (0 = joystick 1). Put a 10 kohm pull-down on PC4, because the 8255 pins float until the kernel sets them. With only one joystick, wire it straight to port A and leave out the 74HC157.
- In both boards 0 selects joystick 1, and the kernel leaves both select lines at 0. So one kernel ROM runs on both boards, and `key` reads joystick 1 on either.
- The AY mixer register 7 must keep bit 6 = 0 (port A input). The kernel also keeps bit 7 = 1 (port B output). On the AY-3-8912 bit 7 has no effect.
- On the AY-3-8912 register 15 is still there and reads back what was written, but it has no pins. On the AY-3-8910 it reads the port B pins while port B is an input. The emulator does both.

## SCART

SCART carries video, stereo audio and an "AV on" signal on one cable.

| SCART pin | Signal | Source |
|---|---|---|
| 20 | Composite video in | TMS9918A COMVID through a 2N4401 emitter follower |
| 16 | Blanking: 0-0.4 V = composite | 75 ohm to GND (an RGB board can drive it later) |
| 8 | Function switch: 9.5-12 V = 4:3 (4.5-7 V would mean 16:9) | 12 V through 1 kohm |
| 6 | Audio left in | AY mix |
| 2 | Audio right in | AY mix |
| 15, 11, 7 | Red, green, blue | RGB header J3, for a later RGB board |
| 4, 5, 9, 13, 14, 17, 18, 21 | Grounds | |

- **Video stage** (jblang/TMS9918A): COMVID, 130 ohm to the base of a 2N4401, 470 ohm from the base to GND; the collector to +5 V through a ferrite bead with 100 nF to GND; the emitter drives SCART pin 20 with 75 ohm to GND. jblang notes that 0 ohm instead of 130 ohm gives a level above the NTSC spec; a larger value gives a dimmer picture.
- **Colour:** the TMS9918A sends NTSC. Most European SCART TVs made since about 2000 show NTSC 60 Hz, but it is worth testing the TV first. For RGB, a later board can take the TMS9928A's Y, R-Y and B-Y outputs to the RGB header J3.
- **Audio mix:** each AY output has a 3 kohm load to GND. The left mix is A through 1 kohm and B through 2.2 kohm; the right mix is C through 1 kohm and B through 2.2 kohm. Each mix goes through 10 uF to the SCART input, with 47 kohm to GND.

## Power

- 12 V DC input (barrel jack), through a 1N5819 against reverse polarity.
- An R-78E5.0-1.0 switching regulator (pin-compatible with a 7805, without its heat) makes 5 V. 12 V also goes to SCART pin 8.
- DS1813-5 reset supervisor (pin 1 /RST, 2 VCC, 3 GND) with a push button to GND, a 10 kohm pull-up on /RESET, and a power LED.
- 100 nF next to the supply pins of every chip, 100 uF on 12 V and on 5 V.

## Software on the board

- **Kernel (flash page 0):** starts the hardware, then either runs the program stored in flash pages 1 and 2 or waits for a program on the serial port.
- **Loading:** in the ZL-80 board display, **Send to board** sends the compiled program over the board's USB port (Web Serial, Chrome or Edge on a desktop). The kernel's serial loader writes it to RAM at 0x4000 and runs it. This works while another program is running. **Send to emulator** does the same into the emulated board.
- **Saving:** **ROM .bin** saves a 512 KB flash image (kernel in page 0, the program from page 1) for an EEPROM programmer. **HEX** saves the program as Intel HEX at 0x4000, which a terminal program can also send to the loader. Later, the kernel can write a received program into flash itself.

## Kernel

The kernel is built by `buildKernel()` in `index.html` and fills flash page 0. On reset it:

1. Maps flash 0 and RAM 32, 33, 34 into the four banks and turns paging on.
2. Clears RAM 0xC000-0xFFFF (RAM holds random values at power-on, and ZL variables start at 0), sets the stack to 0xFF00 and IM 1.
3. Sets up the 8255 (control word 0x82) and the AY mixer (R7 = 0xBF).
4. Writes R0-R7 of the VDP with the display off, clears the 16 KB of VRAM, writes the name table (0-255 three times), the colour table (0xF1) and ends the sprite list (0xD0 at 0x1B00). Then it turns on the display and the frame interrupt (R1 = 0xE0). VDP registers cannot be read back, so the kernel keeps copies at 0xFF10-0xFF17.
5. Copies the program from flash pages 1 and 2 to RAM at 0x4000 and runs it. If flash page 1 is erased (first byte 0xFF), it waits for a program on the serial port.

The FT245R needs no setting up. After the serial loader the kernel starts warm (I register = 1): the same steps without the copy from flash.

This takes about 34 frames (0.6 s).

The interrupt handler at 0x0038 reads the VDP status (which clears the interrupt) and keeps it at 0xFF02 for `vstat`. It also looks at the USB FIFO: a received 0x03 (Ctrl-C) starts the serial loader, any other byte is dropped.

### Serial loader

The loader takes Intel HEX records over the USB FIFO and answers each one with a single character:

| Sent | Board answers |
|---|---|
| 0x03 (Ctrl-C) | `>` ready, now in the loader (also sent again on each later 0x03) |
| a data record (type 00) | `.` stored, or `!` if the checksum is wrong or an address is outside 0x4000-0xBFFF |
| the end record `:00000001FF` | `*`, then a warm start that runs the program |

Other characters between records (CR, LF, spaces) are ignored, and hex digits can be upper or lower case. The browser still waits for the answer to each record before sending the next, so an error stops the transfer at once; the FT245R's FIFO and USB flow control would also take a whole file sent without pauses (the emulator tests both). The browser sends 32 data bytes per record and nothing after the end record. The board's answer to the end record comes before its restart.

Compiled ZL calls kernel routines for everything that touches a chip. Arguments go in 0xFF00 (ARGX), 0xFF01 (ARGY) and A:

| ZL | Kernel routine |
|---|---|
| `plot`, `get`, `cls`, `fill` | PLOT, GET, FILL: read-modify-write of the Graphics II pattern and colour tables, using the table addresses in the register copies |
| `key` | KEY: keyboard row 8 (arrows, space) or joystick 1, as 1 left, 2 right, 4 up, 8 down, 16 fire |
| `rnd` | RND: 16-bit LFSR mixed with the R register |
| `beep` | BEEP: a short tone with a decay envelope on AY channel C |
| `note` | NOTE: tone period from a table of 256 MIDI notes |
| `ay`, `ayget` | AYW, AYRD. Writes to R7 always keep port A as input and port B as output, so the AY never drives the joystick lines. |
| `vreg`, `vaddr`, `vrd`, `vdata`, `vget`, `vfont` | VREG, VAW, VAR, VWR, VRD, VFONT. Two-byte VDP control writes run with interrupts off, because the interrupt handler's status read resets the VDP's byte latch. |

Rules for programs on the board:

- **VRAM timing.** During the active display the TMS9918A needs 8 us (29 T-states at 3.58 MHz) between VRAM accesses, and 2 us otherwise. The kernel loops keep to this, and `vdata` goes through a call, which spaces the writes. The emulator stops a program that accesses VRAM faster.
- **VDP register 1 bit 5** turns on the frame interrupt. Without it `wait` never ends, so `vreg 1 n` must keep 0x20 set.
- **Not on the board:** the MC6845 and MC6847 commands (`crtc`, `crtcget`, `tcolor`, `locate`, `thex`, `tcls`, `tprint`, `vdg`, `vbase`, `vprint`).
- `plot` on the TMS9918A is a read-modify-write of two VRAM bytes, so it is much slower than on the fantasy displays: a few hundred T-states per pixel, so only around a hundred pixels fit in a frame.

## Emulator

The display list in `index.html` has "ZL-80 board (real hardware)". In that mode:

- The Z80 runs 59,736 T-states per frame. The frame interrupt comes at line 192 (T-state 43,776), when the picture is finished.
- Memory goes through the page mapper: 512 KB flash (cannot be written) and 512 KB RAM, which starts with random values.
- Only the ports in the I/O table work. Any other port stops the program with an error.
- The USB FIFO holds 256 received bytes and makes the PC wait when it is full, as the FT245R does. Reading port 80h while the FIFO is empty, or writing port 81h, stops the program.
- The PC keyboard is the MSX matrix (keys by position), and the on-screen pad and the arrow keys are joystick 1.
- The emulator also stops on VRAM accesses that are too fast, a stack overflow, and `return` without `gosub`.

Still to do:

1. Try **Send to board** with a real board. It is tested only against the emulated USB FIFO so far.
2. Writing programs into flash from the console.
3. A `bank` command for the extra RAM and flash pages.

The existing display modules (OLED, TFT, Nokia, MC6845, MC6847) stay as fantasy modes for learning. They are not part of this board.

## Check before building

- Every pin in `hardware/kicad/zl80-netlist.txt` against the datasheets. The pin tables were checked against datasheets and two open designs (jblang/TMS9918A and electrified/rc2014-ym2149), but no board has been built from this schematic.
- The VRAM latch timing at this board's clock. jblang's circuit runs on an RC2014 with the same VDP and crystal.
- The video level on the TV (the 130 ohm base resistor) and whether the TV shows NTSC colour.
- The 74HCT670 page mapper against the Zeta SBC v2 schematic.
- The SCART pin numbers against a SCART pinout sheet before connecting a TV (only one source was used).
- DB9 pin 7: +5 V on Atari joysticks is not confirmed. It goes to +5 V through 1 kohm, which also holds a Mega Drive pad's select line high (B on pin 6, C on pin 9).
- The DS1813 pin order against its TO-92 footprint.
- The AS6C4008 part suffix (5 V part, not the 3.3 V "A" version).
- For an AY-3-8912 board: its 28-pin pinout (1 C, 2 TEST1, 3 VCC, 4 B, 5 A, 6 GND, IOA7-IOA0 on 7-14, 15 CLOCK, 16 /RESET, 17 A8, 18 BDIR, 19 BC2, 20 BC1, DA7-DA0 on 21-28), and that register 15 reads back as the emulator assumes.
- That the ATmega firmware answers a row change before the Z80 reads the row.

## Schematic

`hardware/kicad/` holds the KiCad schematic of this board (`zl80.kicad_sch`, KiCad 7 format; KiCad 8 and 9 open it). It is generated by `gen_schematic.py`; edit that file and run it again rather than editing the schematic by hand. `check_schematic.py` checks that the file parses and that no pin is left floating, and `zl80-netlist.txt` lists every net with its pins.

