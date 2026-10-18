---
type: reference
status: current
date: 2026-10-19
tags: [docs, rotor, motor, hardware]
---

# Rotor (Autonics PMC-2HS) - serial protocol and the motor_gate envelope

User decision 2026-10-19: rotor envelope **-5 .. +5 turns** ("-5바퀴 에서 + 5바퀴"); the controller returns pulses, so
the gate must convert ("기계 리턴은 펄스로 주는지라 각도로 환산해야함"). Nothing in this document was transmitted to the
rotor; the facts below are from the manual, the driver VI read earlier, and the 2026-09-14 hardware logs.

## Protocol facts

Primary source: **Autonics PMC-1HS/PMC-2HS user manual, DRW170814AB**, chapter 8 "Serial Communication Commands"
(pp. 67-78) and chapter 3 / 6 (parameters). Fetched 2026-10-19 from
<https://autonics.se/wp-content/uploads/2018/03/pmc_1_2_hs_en_drw170814ab_20171218_he_20180109.pdf> and converted with
`pdftotext -layout` (Git for Windows). Same manual family: <https://www.autonic.su/content/files/PMC_1_2HS_EN_E_15_0050B_120207.pdf>,
<https://idom.ru/wp-content/uploads/PMC_1HS_2HS_EN_MA_180822_W.pdf> (encrypted PDF, not text-extracted here).
Earlier peer extracts: `archive/peer/2026-09-14-autonics-pmc-serial-command-vocabulary.md`,
`archive/peer/2026-09-14-autonics-pmc-serial-position-reply-format.md` (both later confirmed on hardware).

| item | fact | source |
|---|---|---|
| link | 9600 (default) .. 115200 bps, 8 data bits, 1 stop, no parity, no flow control; characters `0-9 A-Z space CR` | manual 8.1 p. 67; `tools/motor_gate.py` PORTS (COM5 9600) |
| frame | ASCII command, arguments separated by space, axis fields by comma, terminated by **CR (0x0D)**; motion/setting writes have **no response** | manual 8.2-8.3 pp. 67-70 |
| model | **two-axis PMC-2HS**: `POS` reply carries X and Y; the rotor is **X** | `tools/bench/hw_rotor_read.log`, `docs/instrument-libraries.md:318-319` |
| absolute move | `PAB <X>,<Y>[CR]`, signed **decimal pulses**; `PAB 10, -1`; a 1-axis form `PAB 2000` | manual p. 68 |
| relative move | `PIC <X>,<Y>[CR]`, signed decimal pulses, `-` = CCW; `PIC -3000` | manual p. 68 |
| speed | `SPD <X>,<Y>[CR]` sets the drive speed (no response); `SPD[CR]` queries -> `SPD x,y[LF][CR]`; **drive pps = value x speed multiplier** (multiplier 1..500, default 10; drive speed 1..8000) | manual p. 69, 3.3.1 p. 13, 3.3.5 p. 14 |
| position query | `POS[CR]` -> `POS hhhhhhhh,hhhhhhhh[CR]`, **8 hex digits per axis**, two's complement (manual: "composed of hexadecimal"; sign behaviour measured) | manual p. 70; `docs/rotor-sign-diagnosis.md:119-122` (`FFFFFFF6` = -10 pulses = -7.2 deg on hardware) |
| scale | **0.72 deg/pulse, 500 pulses/turn** (driver constant, measured) | `docs/rotor-sign-diagnosis.md:115`, `docs/instrument-libraries.md:315` |
| range | position / soft limit -8 388 608 .. +8 388 607 pulses | manual 3.3.10-11 p. 15 |
| counter clear | `CLL X` clears the active counter, `CLR X` the actual counter (no motion) | manual pp. 68-69; `CLL X` used on hardware 2026-09-14 |
| home | `HOM X` = home search (**moves**; the soft limit does NOT act during it); `OGE X` force-ends it | manual p. 70, 3.2.6 p. 12 |
| stop | `STO X` decelerating stop | manual p. 70 |
| others | `JOG` continuous drive, `PRG/PST/PRS/EDP/PSP` stored programs, `SSM` select stored speed 1-4, `RST` reset motion IC, `SCI` port settings (write needs reset), `OUT`, `INR`, `IDC`, `VER`, `ERD X` (error bits incl. bit 9/8 = software limit -/+ error) | manual pp. 67-76 |
| parameter I/O | `IHR X<addr>` / `IXR X<addr>` read 2-/4-byte **EEPROM** data (hex); `IHS` / `IXS` write them (reply echoes the data). Example: `IXS X79,00000064` = home search offset 100; `IHS XE6,0064` = speed multiplier 100 | manual pp. 76-77 |

### The SetCommand.vi path (read earlier, never re-opened here)

`instr.lib\Autonics Motor\SetCommand.vi` Ring: `MovePos` (PAB with `+ Baseline Startpoint` turns, deg/k), `MovePosRel`
(PIC, deg/k), `Get Position` (= Ring 2, writes `POS`, takes substring [4,8] = the X field), `SetSpeed` (the only frame
whose number is formatted with **no arithmetic**: `SPD <Numeric>`) - `tools/bench/setcommand_diagram.log:33-48`,
`docs/rotor-sign-diagnosis.md:93-117`. The unsigned parse was fixed on `claudeDev\SetCommand_signed.vi`
(`tools/bench/test_setcommand_signed.log`: `FFFFFFF6` -> -7.2 deg).

**Speed default.** SetCommand.vi's own `Numeric` default is 0 (`tools/bench/autonics_defaults.log`); the value the main VI
sends with every rotation command is the panel control `Rot \nSpeed`, **default 100.0** (`docs/rotor-scheduler-design.md:29`,
`tools/bench/diag_c104f_leg.log:144`, read on diagrams 32/111 per `docs/main-vi-panel-map.md:556-559`). So `SPD 100`;
with the default multiplier 10 that is 1000 pps, consistent with the measured ~880 pps for 1500 pulses incl.
acceleration (`tools/bench/hw_rotor_visible.log`). The multiplier actually stored in this controller was NOT read.

### Hardware soft limits - they EXIST

Manual 3.2.6 (p. 12), 3.3.10-11 (p. 15), 6.1.2 (p. 51), 6.1.4 (p. 54), [Data] table (p. 78):

* "Software Limit" mode **Enable/Disable, default Disable**; when enabled and a drive exceeds Soft limit + or -, the
  controller **decelerates to stop**; drive in the reverse direction to leave it; **not applied during home search**.
* `Software Limit +` default +8 388 607, `Software Limit -` default -8 388 608 (pulses at pulse scale 1000/1000).
* Teaching-unit registers: REG88 = soft limit +, REG89 = soft limit -, REG72 digit 6 = Soft Limit
  **(0 = Enable, 1 = Disable - "the configuration logic is reversed")**.
* They live in **EEPROM** (written with `IXS`/`IHS`, read with `IXR`/`IHR`). From the [Data] table, whose columns are
  scrambled by the text extraction: EEPROM byte addresses `F5/F4` (soft limit +) and `F7/F6` (soft limit -); the
  `IXS/IXR` register numbers follow home-search offset `79` (confirmed by the manual's own example), i.e. **most
  likely `7A` and `7B`** - inferred from row order, NOT confirmed.

## Envelope design

**Kind chosen: RELATIVE envelope enforced by the gate (script + sender), not the controller's soft limit.**

Why not the controller limit now, although it exists:
1. **Persistence.** The soft limit is EEPROM-only - every session start/end would be an EEPROM write (wear, and a
   crash leaves a non-default limit persisting across power cycles in a controller the original main VI also uses).
   For PI the rule is "never WPA" (RAM only); for ASI the persistent SL/SU was accepted. The rotor needs the user's call.
2. **Unverified addresses.** `IXS/IXR 7A/7B` and the mode-bit address (REG72, likely 2-byte `IHS X..`) are inferred from a
   garbled table; writing a wrong EEPROM address could change speed multiplier, home mode or program data.
3. **Unknown activation.** The manual does not say whether an EEPROM write takes effect in the running motion IC or
   only after `RST`/power-cycle; `RST`'s effect on the position counter is undocumented.
4. **Home ignores it**, and the counter coordinate it is measured in can be cleared by `CLL`/`CLR` - so the gate's
   command-class refusals are needed either way.

The relative envelope (implemented):
* `--session start` (after PI and ASI succeed) runs `tools/motor_rotor_io.ps1 -Mode read` (one dummy `POS` for the
  first-read timeout, then `POS`), records `rotor_window = {center_pulses, lo_pulses = c-2500, hi_pulses = c+2500,
  half_width_pulses, deg_per_pulse}` in `tools/bench/motor_session.json`. **Nothing is written to the controller.** A
  failed rotor read does not refuse the PI/ASI session; it records `rotor_window: null`, so every rotor move is refused.
* `PAB <x>` allowed only if lo <= x <= hi. `PIC <d>`: the decision without a position refuses |d| > 5000; the binding
  check is in the sender, **inside the same port open as the transmit**: two `POS` reads must be identical
  (stationary), target = fresh POS + d must be in lo..hi, else exit 7 before anything is sent. The gate re-parses the
  sender's `FRESH RAW='..' POS=n` line in Python and refuses (rc 3) if its own sign conversion disagrees or the target
  is outside.
* X axis only (any Y field refused). Speed: the sender sends `SPD <max_speed>` (100) before every move; `SPD n` is
  allowed by class only for 1..100 (not transmittable on its own).
* Refused for good (`ROTOR_FENCE`): `CLL CLR HOM OGE RST IHS IXS PRG PST PRS EDP PSP JOG SSM OUT STO`, and `SCI` with
  arguments - counter clear/home move the fence, EEPROM writes / programs / jog / stored speeds bypass it.
* Reads allowed: `POS SPD VER SCI` (bare), `ERD X`, `INR X`, `IDC X`, `IHR X<hex>`, `IXR X<hex>`.
* Watchdog: the sender polls `POS` every 300 ms; outside lo-25..hi+25 it sends `STO X` and exits 8; the final POS must
  equal the target (exit 0) else exit 8.
* `--session end`: nothing to release for the rotor; deleting the session file removes the window.
* `tools/bench/motor_limits.json` "rotor": `mode relative, half_width_pulses 2500, deg_per_pulse 0.72, max_speed 100`;
  `load_limits` refuses the whole file if half width is not an int in 1..2500, deg/pulse != 0.72, speed not int in
  1..100, or mode != relative.

Upgrade path to the controller limit (needs the user): read-only probe `IXR X7A`, `IXR X7B`, `IHR X..` for REG72
(expect +8388607 / -8388608 / soft limit disabled) to confirm addresses; then decide EEPROM writes per session or once.

## Open

* `tools/hooks/guard_bash.py` MOTOR_BLOCKED_RE does not name `motor_rotor_io.ps1` (the PI/ASI senders are blocked by
  name). The sender refuses `send` without the gate's token, but `-Mode read` opens COM5 directly. Hook edits are for
  the chat, not this card.
* `motor_rotor_io.ps1` is syntax-checked only (PowerShell parser, 0 errors); it has never opened COM5. First hardware
  use should be `-Mode read` via `--session start`.
* The controller's stored speed multiplier, and whether the `SPD` query returns the set speed at rest, were not read.
* The rotor coordinate: counter was left at 0 on 2026-09-14 (baseline-0 convention); the main VI's +200-turn baseline
  is not restored. The relative window does not depend on it.
