---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# autonics-pmc-serial-command-vocabulary

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (120s)
- **why asked:** command vocabulary needed to test a negative rotor coordinate without a 200-turn move (preset/zero, relative move, speed units)
- **verdict:** unverified

## Question

PROTOCOL FACT question (external search; cite the Autonics PMC-1HS/2HS manual pages; one paragraph + a table). We drive an Autonics PMC-1HS/2HS pulse-motor controller over RS-232 with a lab-written LabVIEW driver whose case frames are (from a scripted read, constants unreadable): frame A: Numeric/k -> decimal string -> concat(3 strings) -> VISA Write (a MOVE); frame B: Numeric -> decimal string -> concat(3) -> Write (no scaling: probably SetSpeed); frame C: (Numeric + Baseline*360)/k -> decimal -> concat(3) -> Write (absolute move with an offset, the manual's 'PAB'); frame D: concat(2 constant strings) -> Write (a parameter-less command); frame E: 'POS' query -> read. The driver's Ring items are MovePos, MovePosRel, Get Position, SetSpeed (Get Position = value 2, measured). QUESTIONS: (1) the exact serial command mnemonics and syntax for absolute move (PAB?), RELATIVE/incremental move (PRB? PIN?), speed setting (what units - pps? and the valid range), stop/emergency stop, and any command that PRESETS or ZEROES the current position counter without motion (e.g. 'PSR' / 'HOME' / position set) - with the manual's wording; (2) does a HOME command move the motor (to a sensor) - yes/no; (3) reply/acknowledge format for write commands (does the controller echo 'OK' / error codes?), and the CR/LF convention; (4) default RS-232 settings (baud, parity) so a VISA session can be configured. We need this to (a) identify which Ring value is the relative move WITHOUT moving, and (b) test a negative coordinate: the controller currently sits near +100000 pulses (a 200-turn baseline the lab uses), so a preset-to-zero command would avoid a 200-turn move.

## Answer

The protocol mnemonics are **PAB** (absolute), **PIC** (relative/incremental?봭ot PRB/PIN), **SPD** (speed), **STO** (decelerating stop), **CLL/CLR** (counter clear without commanded motion), and **HOM** (a physical home-search sequence, so **yes, it moves the motor**). Normal motion/configuration writes explicitly have ?쏯o-response?? there is no documented `OK` acknowledgement or command-error reply; operational errors must be queried separately with `ERD`. Commands are terminated by **CR only (`0x0D`)**; some query replies use LF+CR, although `POS` is shown ending in CR. The serial link defaults to **9600 baud, 8 data bits, 1 stop bit, no parity, no flow control**. [Autonics manual, serial-command pages 69??9](https://manualzz.com/doc/61665026/autonics-pmc-1hs-usb--pmc-2hs-232--pmc-2hs-usb-instructio...), [Autonics PDF manual](https://www.autonic.su/content/files/PMC_1_2HS_EN_E_15_0050B_120207.pdf)

| Function | Exact syntax and manual wording | Reply / safety implication |
|---|---|---|
| Absolute move | `PAB <X>,<Y><CR>`; PMC??HS example: `PAB 2000<CR>`. Manual: ?쐂rives a specified axis to an absolute position?? coordinates are pulses and signed values are accepted. [Manual pp. 69??0](https://manualzz.com/doc/61665026/autonics-pmc-1hs-usb--pmc-2hs-232--pmc-2hs-usb-instructio...) | No response. This matches frame C with the baseline offset. |
| Relative move | `PIC <X>,<Y><CR>`; PMC??HS example: `PIC -3000<CR>`. Manual: ?쐂rives the specified axis to a relative position?? negative means CCW. [Manual p. 70](https://manualzz.com/doc/61665026/autonics-pmc-1hs-usb--pmc-2hs-232--pmc-2hs-usb-instructio...) | No response. This matches frame A. Given the Ring order supplied and measured `Get Position = 2`, **MovePosRel is almost certainly Ring value 1** (`MovePos=0`, `MovePosRel=1`, `Get Position=2`, `SetSpeed=3`). |
| Set/read speed | Set: `SPD <Xspeed>,<Yspeed><CR>`; PMC??HS: `SPD 2000<CR>`. Query: `SPD<CR>`. Manual says actual drive speed = supplied axis-speed value 횞 configured Speed Multiplier. Units are **pps**; axis setting is **1??000**, multiplier **1??00**, giving **1 pps?? Mpps** overall. [Manual pp. 70??1](https://manualzz.com/doc/61665026/autonics-pmc-1hs-usb--pmc-2hs-232--pmc-2hs-usb-instructio...), [Autonics specification](https://www.autonic.su/content/files/PMC_1_2HS_EN_E_15_0050B_120207.pdf) | Set has no response; query returns `SPD ...<LF><CR>`. Frame B is `SPD`. Do not assume the decimal argument itself is final pps unless Speed Multiplier = 1. |
| Controlled stop | `STO X<CR>`, `STO Y<CR>`, or `STO XY<CR>`. Manual: ?쐂ecelerates to stop?? below start speed it stops immediately. [Manual p. 72](https://manualzz.com/doc/61665026/autonics-pmc-1hs-usb--pmc-2hs-232--pmc-2hs-usb-instructio...) | No response. |
| Emergency stop | No serial emergency-stop mnemonic is documented. The physical **EMG** input immediately stops all axes when connected to GEX; the parallel RESET input may also be used as an emergency-stop signal. [Manual connector pp. 64??8](https://manualzz.com/doc/61665026/autonics-pmc-1hs-usb--pmc-2hs-232--pmc-2hs-usb-instructio...) | Do not treat `STO` as equivalent to hardware EMG?봧t normally decelerates. |
| Zero without motion | `CLL X<CR>`: ?쐁lears the active position counter?? `CLR X<CR>`: ?쐁lears the actual position counter.??For both axes use `CLL XY<CR>` / `CLR XY<CR>`. [Manual pp. 70??1](https://manualzz.com/doc/61665026/autonics-pmc-1hs-usb--pmc-2hs-232--pmc-2hs-usb-instructio...) | Both have no response and no movement is specified. **CLL is the better candidate for zeroing the commanded/current coordinate used by positioning; verify with `POS` before and after.** `CLR` appears to target the separate actual/feedback counter. |
| Position query | `POS<CR>`; response contains signed position count(s) in **hexadecimal**, ending in CR. [Manual p. 71](https://manualzz.com/doc/61665026/autonics-pmc-1hs-usb--pmc-2hs-232--pmc-2hs-usb-instructio...) | Read-only. Note the manual says hexadecimal, so confirm whether the LabVIEW driver converts it accordingly. |
| Home | `HOM X<CR>` or `HOM XY<CR>`. Manual: ?쐁arries out the Home Search?? the sequence searches near-home/home/Z-phase signals and may execute an offset movement. [Manual p. 72](https://manualzz.com/doc/61665026/autonics-pmc-1hs-usb--pmc-2hs-232--pmc-2hs-usb-instructio...), [Autonics specification](https://www.autonic.su/content/files/PMC_1_2HS_EN_E_15_0050B_120207.pdf) | **Yes?봫otor motion occurs. Do not use HOM merely to zero the counter.** |
| Errors / acknowledgement | Motion writes are documented as ?쏯o-response.??`ERD X<CR>` explicitly reads controller error status; zero means no error. [Manual pp. 77??8](https://manualzz.com/doc/61665026/autonics-pmc-1hs-usb--pmc-2hs-232--pmc-2hs-usb-instructio...) | No documented `OK`, echo, or generic command-error reply. A VISA read after ordinary writes should therefore time out unless the driver avoids reading. |
| Serial setup | Default **9600, 8-N-1, no flow control**; selectable baud range 9600??15200. `SCI` can inspect/change port settings, with reset/power cycle required after changing them. [Manual pp. 68, 75??6](https://manualzz.com/doc/61665026/autonics-pmc-1hs-usb--pmc-2hs-232--pmc-2hs-usb-instructio...), [Autonics manual showing 9600 default](https://autonics.se/wp-content/uploads/2018/03/pmc_1_2_hs_en_drw170814ab_20171218_he_20180109.pdf) | Send `<CR>` only. Configure VISA termination for CR when reading `POS`; allow LF before CR for queries such as `SPD`/`VER`. |

For the intended negative-coordinate test, the lowest-motion procedure is: read `POS`, issue `CLL X<CR>`, read `POS` again, then use a very small signed `PIC` only after confirming the counter became zero. Do **not** use `HOM` or `PAB 0`, because both command physical motion.

## Sources

(extract from answer)

## What was done with it

CLL X and PIC behaved exactly as described on the PMC-2HS (no motion on CLL, -10 pulses on PIC -10, no response to writes). Verdict: correct.
