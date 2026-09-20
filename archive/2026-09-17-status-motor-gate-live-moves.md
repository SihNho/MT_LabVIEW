---
type: archive
status: historical
date: 2026-09-17
tags: [status, motor, gate, anchor, hardware]
---

# STATUS narrative relocated 2026-09-17 (rule 4) — the motor gate's build and its first live moves

Moved VERBATIM out of `STATUS.md`'s HARDWARE block, which had reached 130 lines (threshold ~110).
Nothing is rewritten. STATUS keeps the policy lines (envelope, rig-state key) and one pointer here.

```
✅ **BUILT + SELF-TESTED 70/70 (`tools/bench/selftest_motor_gate.log`, `BGRUN END rc=0`, no port opened):**
`tools/motor_gate.py` = the one gateway (default-deny; PI 0–39 mm, ASI x/y ≤1.0 mm from the FIXED anchor and no
home/origin/zero/save command, ASI **z free**; **1.0 mm = 10 000 ASI units**, native 0.1 µm) + `guard_bash.py`'s
motor gate refusing `hw_rotor_signed_test/visible.py`, `build_rawcmd.py`, `drive_original_copy.py`, inline
`SerialPort`/pyserial and raw `MOV/MOVREL/GOH/PIC` one-liners (read-only query scripts pass).
✅ **23:02 ANCHOR WRITTEN** (`tools/bench/motor_anchor.json`: ASI x −1.8477 / y −2.7745 mm, z 0; PI 0 mm, TMN 0,
**TMX 52 > 40.94 ⇒ the controller does NOT protect the rig**). ✅ **23:07 FIRST LIVE MOVES, PI only, via
`motor_gate.py --execute` → `tools/motor_send_pi.ps1` (token + own 0–39 re-check):** 0→30 (4.1 s) →35 (2.6 s),
ONT=1, ERR=0, VEL 15 mm/s; **40 REFUSED before any port opened.** PI returned to **0** (0.00005) at 23:09.
✅ **23:10 ASI x then y, via `tools/motor_asi_io.ps1` (absolute single-axis `M X=`/`M Y=` only; fresh read + own
1 mm re-check): ±0.4 mm and 0 MOVED (read back within 2 units = 0.2 µm, ~1.3 s each), ±2 mm REFUSED, 0 unexpected**
(`tools/bench/asi_xy_check_{X,Y}.log`). Stage is back at the anchor (+0.0002, +0.0001 mm). Rotor transmit not built. Known wart: the gate lists the axis id `1` among `targets_mm` (harmless, inside 0–39).
```
