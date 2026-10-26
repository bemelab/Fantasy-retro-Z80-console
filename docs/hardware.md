# ZL-80 hardware, version 1

This is the plan for a real ZL-80 console that runs the same machine code as the emulator in `index.html`. The rule is simple: **the emulator copies this board exactly**. A program that runs in the emulator's hardware mode must run on the board without changes, and the emulator must refuse anything the board cannot do.

Status: design. Nothing here is built or tested yet. The items in "Check before building" must be confirmed against the datasheets.

## Overview

```
                 +-----------------------------+
 10.738635 MHz --| TMS9928A VDP   16 KB VRAM   |--- Y, R-Y, B-Y --> RGB converter --> SCART (RGB + sync)
   crystal       |  CPUCLK 3.58 MHz -----------|---+
                 |  /INT (every frame) --------|---|--+
                 +-----------------------------+   |  |
                                                   v  v
 512 KB flash --+                              +---------+
 512 KB SRAM ---+-- 16 KB page mapper ---------|  Z80    |
                                               | 3.58 MHz|
 AY-3-8910 <-- 1.79 MHz (CPUCLK / 2)           +---------+
   A B C ----> stereo mix --> SCART audio L/R      |
   port A <--- 2 joysticks (DB9)                   |
 8255 PPI <--- keyboard (MSX matrix, PS/2 adapter) |
 68B50 ACIA <-- USB serial <-- PC / browser -------+
```

## Main parts

| Part | Choice | Why |
|---|---|---|
| CPU | Z80 (CMOS, Z84C00), 3.579545 MHz | Clocked from the VDP's CPUCLK pin, so one crystal drives CPU, video and sound in step. |
| Video | TMS9928A | Same registers and software as the TMS9918A. It outputs Y, R-Y, B-Y instead of NTSC composite, which converts cleanly to RGB for SCART. |
| VRAM | 16 KB | The most the TMS99x8A family can address. |
| Sound | AY-3-8910 (or YM2149), 1.789773 MHz | The 40-pin AY-3-8910 has two I/O ports (A and B), used for the joysticks. |
| ROM | 512 KB flash, SST39SF040 (DIP-32) | The largest common 5 V parallel flash in DIP. It can be rewritten in the console. |
| RAM | 512 KB SRAM, AS6C4008 (DIP-32) | The largest common 5 V SRAM in DIP. |
| Keyboard | 8255 PPI with the MSX key matrix | See "Keyboard". |
| Joysticks | 2 x DB9 (Atari/Sega pinout) on AY port A | Same wiring idea as MSX. |
| Serial | 68B50 ACIA, 115200 baud, 7.3728 MHz crystal | Loads programs from a PC or straight from the browser (Web Serial). |
| TV | SCART, RGB with sync | See "SCART". |

## Clocks and timing

- VDP crystal: 10.738635 MHz.
- Z80: CPUCLK = 10.738635 / 3 = **3.579545 MHz**.
- AY: CPUCLK / 2 = **1.789773 MHz** (one 74HC74 flip-flop).
- Frame: 262 lines x 342 pixel clocks, **59.92 frames per second**. The Z80 runs at 2/3 of the pixel clock, so a frame is exactly **59,736 Z80 T-states**.

The emulator today uses 4 MHz, 60 frames per second and a 1.7734 MHz AY clock. The hardware mode must switch to the numbers above.

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

## I/O ports

The Z80 decodes the low 8 address bits for I/O. The video, sound and keyboard ports are the MSX1 numbers, so MSX documentation and example code apply directly.

| Port | Device | Use |
|---|---|---|
| 0x78-0x7C | Page mapper | See "Memory". |
| 0x80 | 68B50 ACIA | Control (write), status (read) |
| 0x81 | 68B50 ACIA | Data |
| 0x98 | TMS9928A | VRAM data |
| 0x99 | TMS9928A | Control: register write and VRAM address (write), status (read) |
| 0xA0 | AY-3-8910 | Register select |
| 0xA1 | AY-3-8910 | Data write |
| 0xA2 | AY-3-8910 | Data read |
| 0xA8 | 8255 port A | Free, 8 outputs (LEDs, expansion) |
| 0xA9 | 8255 port B | Keyboard row bits (read, 0 = key down) |
| 0xAA | 8255 port C | Bits 0-3: keyboard row select (write). Bits 4-7 free. |
| 0xAB | 8255 control | Write 0x82 at start: A out, B in, C out |

Any other port does nothing on the board. In the emulator's hardware mode it stops the program with an error.

## Interrupts

- TMS9928A /INT goes to the Z80 /INT. It fires once per frame when register 1 bit 5 is set.
- Mode IM 1: every interrupt calls 0x0038 in the kernel.
- The handler saves the registers, reads the VDP status at port 0x99 (this clears the interrupt), counts frames, scans the keyboard and joysticks into RAM, and returns with `EI` and `RETI`.
- ZL's `wait` becomes `HALT` loops that wake on this interrupt. That is why the emulator's hardware mode must emulate the interrupt and must never continue a `HALT` on its own.

## Keyboard

Choice: **the MSX key matrix read through an 8255 PPI.**

- The program writes a row number (0 to 10) to port 0xAA and reads that row's 8 keys from port 0xA9, with 0 meaning pressed. Every key has its own bit, so a game can see several keys held at once. A keyboard that only sends the last character cannot do this.
- Row 8 holds space and the arrow keys (bit 0 space, bit 4 left, bit 5 up, bit 6 down, bit 7 right), so ZL's `key` command keeps working.
- Physical keyboard, two options:
  1. **PS/2 keyboard with a small converter.** An ATmega328P reads the PS/2 keyboard, watches the row select lines, and sets the 8 column lines. This is cheap and any PS/2 keyboard works. The converter firmware becomes part of this project.
  2. **A real matrix** (an old MSX keyboard, or a hand-built 88-key matrix) wired directly to the 8255.
- The emulator maps the PC keyboard to the same matrix.

## Joysticks

- Two DB9 ports, Atari/Sega pinout: up, down, left, right, two buttons.
- AY port A is the input: bits 0-3 directions, bits 4-5 buttons, 0 = pressed.
- AY port B is an output: bit 6 selects joystick 1 or 2.
- The AY mixer register 7 must keep bit 6 = 0 (port A input) and bit 7 = 1 (port B output).

## SCART

SCART carries RGB, sync, stereo audio and an "AV on" signal on one cable, and European TVs take 50 Hz and 60 Hz RGB.

| SCART pin | Signal | Source |
|---|---|---|
| 15 | Red, 0.7 V into 75 ohm | RGB converter |
| 11 | Green | RGB converter |
| 7 | Blue | RGB converter |
| 16 | RGB switch, 1 to 3 V | 5 V through a divider |
| 20 | Sync, about 0.3 V | Y output (luma with sync), buffered |
| 8 | AV switch: 9.5 to 12 V = 4:3 picture | 12 V through 1 kohm |
| 6 | Audio left in, 0.5 V RMS | AY mix |
| 2 | Audio right in | AY mix |
| 4 | Audio ground | |
| 5, 9, 13, 17, 18, 21 | Grounds | |

- **RGB converter:** an op-amp matrix (for example 3 x LM6172 or THS7374) turns Y, R-Y, B-Y into R, G, B. The MSX community has published circuits for this. A ready-made TMS9928A RGB board is another way.
- **Audio mix:** channel A plus half of B on the left, channel C plus half of B on the right. These are the same weights the emulator uses. Use resistors, then 10 uF coupling capacitors.
- **Plan B for the first breadboard:** a TMS9918A gives NTSC composite on one pin. Feed it to SCART pin 20 as composite video. Many European TVs show NTSC 60 Hz, but colour is not guaranteed.

## Power

- 12 V DC input. A 5 V switching regulator powers the board. 12 V also goes to SCART pin 8.
- Reset button with an RC delay (or a DS1813) on the Z80 /RESET line.

## Software on the board

- **Kernel (flash page 0):** starts the hardware, then either runs the program stored in flash page 1 (if it has a "ZL" header) or waits for a program on the serial port.
- **Loading:** the emulator gets a "Send to console" button. It uses Web Serial in Chrome or Edge to send the compiled program over USB serial. The kernel copies it to 0x4000 and runs it.
- **Saving:** a ROM file (.bin, 512 KB) for an EEPROM programmer, and an Intel HEX file. Later, the kernel can write a received program into flash itself.

## Kernel

The kernel is built by `buildKernel()` in `index.html` and fills flash page 0. On reset it:

1. Maps flash 0 and RAM 32, 33, 34 into the four banks and turns paging on.
2. Clears RAM 0xC000-0xFFFF (RAM holds random values at power-on, and ZL variables start at 0), sets the stack to 0xFF00 and IM 1.
3. Sets up the 8255 (control word 0x82) and the AY mixer (R7 = 0xBF).
4. Writes R0-R7 of the VDP with the display off, clears the 16 KB of VRAM, writes the name table (0-255 three times), the colour table (0xF1) and ends the sprite list (0xD0 at 0x1B00). Then it turns on the display and the frame interrupt (R1 = 0xE0). VDP registers cannot be read back, so the kernel keeps copies at 0xFF10-0xFF17.
5. Copies the program from flash pages 1 and 2 to RAM at 0x4000 and runs it. If flash page 1 is erased (first byte 0xFF), it waits.

This takes about 34 frames (0.6 s).

The interrupt handler at 0x0038 reads the VDP status (which clears the interrupt) and keeps it at 0xFF02 for `vstat`.

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
- `plot` on the TMS9928A is a read-modify-write of two VRAM bytes, so it is much slower than on the fantasy displays: a few hundred T-states per pixel, so only around a hundred pixels fit in a frame.

## Emulator

The display list in `index.html` has "ZL-80 board (real hardware)". In that mode:

- The Z80 runs 59,736 T-states per frame. The frame interrupt comes at line 192 (T-state 43,776), when the picture is finished.
- Memory goes through the page mapper: 512 KB flash (cannot be written) and 512 KB RAM, which starts with random values.
- Only the ports in the I/O table work. Any other port stops the program with an error. The 68B50 accepts output but has no input yet.
- The PC keyboard is the MSX matrix (keys by position), and the on-screen pad and the arrow keys are joystick 1.
- The emulator also stops on VRAM accesses that are too fast, a stack overflow, and `return` without `gosub`.

Still to do:

1. ROM and HEX download, and "Send to console" over Web Serial, with a serial loader in the kernel.
2. Writing programs into flash from the console.
3. A `bank` command for the extra RAM and flash pages.

The existing display modules (OLED, TFT, Nokia, MC6845, MC6847) stay as fantasy modes for learning. They are not part of this board.

## Check before building

- The TMS9928A pins for Y, R-Y, B-Y and CPUCLK, and the VRAM wiring. Copy a published TMS99x8A board (for example the RC2014 TMS9918A video card) rather than designing it from scratch.
- The RGB converter values for the TMS9928A output levels.
- The 74HCT670 page mapper against the Zeta SBC v2 schematic.
- The SCART pin numbers against a SCART pinout sheet before connecting a TV.
- That the ATmega converter answers a row change before the Z80 reads the row. An `OUT` followed straight away by `IN` leaves only a few microseconds at 3.58 MHz.
