---
type: reference
status: current
date: 2026-09-14
tags: [docs, rotor]
---

# Why the rotor needs a baseline: the read-back parses as UNSIGNED

> Diagnosis (morning) — **fixed the same evening on a COPY at the user's decision**: `claudeDev\SetCommand_signed.vi`,
> verified by injection (16/16) and on the real rotor (−7.2°, then −3 turns / origin return with the user watching);
> see the sections from "Corrections from the scripted read" onward. The instr.lib original is unchanged.

## The question

The user drives the rotor to negative angles — **−7200° (20 turns)** and **−14400° (40 turns)** — and recalled
setting an arbitrary midpoint as zero because *"컨트롤러 절대좌표가 아마 음수를 지원 안해줬을거임"*. I took that as
established and was wrong twice about why. Then the user proposed the sharper version:

> *"아 내가 시리얼 받을 때 음수값을 못받아서 그랬나? 그러면 이 부분은 개선해야겠는데"*

— i.e. the limitation may be in **receiving**, not in commanding. That turns out to fit the evidence.

## The controller commands negative positions — confirmed from the manual

PMC-1HS/2HS (the model the user confirms), §9.3, verbatim:

```
PAB   It drives a specified axis to an absolute position.
      Command [Absolute position coordinate on X-axis] [Y-axis] [CR]      (unit: Pulse)
[Example]  To move to the 10 pulse on X-axis, -1 pulse on Y-axis for 2-axis
      PAB 10, -1 [CR]
      Response: No-response
```

A negative coordinate is in Autonics' own example. Position parameters elsewhere in the manual are specified over
**−8,388,608 … +8,388,607**. So "the controller cannot take negative positions" is false, and my earlier claim
built on it is withdrawn.

Communication settings, same section: 9600–115200 bps, 8 data bits, 1 stop bit, no parity, no flow control,
control characters `0-9, A-Z, space, [CR]`.

## Where the sign is actually lost

`SetCommand.vi`'s `Ring` selects one frame of a Case Structure (diagram 0 holds only that structure, uid 188).
**Diagram 1 is the read path** — it is the only frame containing a VISA *Read*. Its nodes, by terminal signature:

| uid | terminals | what it is |
|---|---|---|
| 795 | `write buffer`, `return count`, `VISA resource name` | VISA **Write** — sends the query |
| 926 | `read buffer`, `byte count`, `return count` | VISA **Read** — the controller's reply |
| 979 | `substring`, `length (rest)`, **`offset (0)`**, `string` | String Subset — trims the reply |
| **1013** | `number`, `offset past number`, **`default (0uL)`**, `offset`, `string` | **Decimal String To Number** |
| 622 | `x`, `type`, `*(type *) &x` | **Type Cast** |
| 2841, 828, 2410, 784 | `x*y`, `x-y`, `x*y`, `x*y` | scaling and **one subtraction** |

**`default (0uL)` is the finding.** The `uL` suffix is LabVIEW's own rendering of an **unsigned long** constant,
so the string-to-number conversion is typed **U32**. A reply of `-1` cannot survive that conversion as −1.

The `Type Cast` immediately after (uid 622, whose output is the front-panel indicator literally labelled
`*(type *) &x`) is the classic workaround for exactly this: reinterpret the unsigned bits as signed. Whether it
fully recovers the sign, or only for part of the range, is **not established** — see the limits below.

And uid 828, the single `x-y` on this path, is where a baseline would be **subtracted** on read. Diagram 4 — a
write frame — contains the matching `x+y`. An offset added on write and removed on read is precisely the
coordinate shift the user described.

## So the picture is consistent, and the user's hypothesis is the one that survives

```
WRITE  degrees ──(× scale)──▶ (+ Baseline Startpoint) ──▶ decimal string ──▶ PAB ... [CR]
READ   reply string ──▶ subset ──▶ Decimal String To Number  default (0uL)  ◀── UNSIGNED
                                 └▶ Type Cast ──▶ (− Baseline) ──▶ (× scale) ──▶ Pos_degree
```

Keeping the controller coordinate positive means the unsigned read never has to represent a negative number.
That is a workaround for the parse, not a limitation of the hardware.

## Confidence, stated honestly

**Strong:** the read frame parses through a conversion whose default is unsigned; a Type Cast follows it; one
subtraction sits on the read path and one addition on a write path. All of this is read from terminal names
returned by LabVIEW itself.

**Not established, and not to be asserted:**
- the exact node *styles* — identity here is inferred from terminal signatures, not read from `Node.Style`. The
  per-diagram style reader (`OpReportNodes_v0`) is still unbuilt; until it exists this stays inferential.
- whether the Type Cast fully restores the sign, or the range over which it does;
- the unit of `Baseline Startpoint` (default **200.0**) — degrees, pulses and turns all remain open, and the peer
  review argued **degrees** is the most parsimonious given the neighbouring *"Converting degree into pulse"*;
- what the main VI actually wires into `Baseline Startpoint` — it may override the 200.0 default entirely.

## Corrections from the scripted read of the driver copy (2026-09-14 19:2x, `probe_setcommand*.log`)

- The conversion is **`Hexadecimal String To Number`** (label read by `node_labels`), not Decimal; its `default`
  input is **unwired** — `(0uL)` is the primitive's built-in U32 default (NI doc via codex,
  `archive/peer/2026-09-14-hex-string-to-number-signed-default.md`).
- The `Type Cast` (uid 622) is a **parallel** branch from the substring (wire 1183), not a stage after the conversion;
  its output feeds only the debug indicator `*(type *) &x` through one multiply. `Pos_degree` (case output tunnel,
  wire 1927) comes from the Hex-to-number path: `number` → ×k → − (Baseline × k′). A Type Cast of the ASCII bytes is
  not a hex parse (`'FFF6'` → 0x46464636), so that branch was never a working sign recovery.
- **Wiring an I32 default is NOT a fix:** NI documents out-of-range results as saturating to the type's maximum
  (`FFFFFFF6` → 2147483647), so the correct signed read is *parse as U32, then Type Cast the NUMBER to I32* (or
  subtract 2³² when bit 31 is set) — and if the controller replies 24-bit (6 hex digits), sign-extend at 2²³.
  The reply width is the open fact (protocol search dispatched; a position query on the hardware settles it).

## FIXED on a copy — 2026-09-14 19:5x, verified without hardware (INDEX row 31)

`claudeDev\SetCommand_signed.vi` (instr.lib original untouched, md5 checked): in the read frame the `Hexadecimal
String To Number` output (U32) now goes through the existing `Type Cast` (reinterpreted as the signed type) before the
scaling multiply; the debug branch and `read buffer 2` are kept. Injection test (`test_setcommand_signed.log`, the
reply fed through a string control on TEST copies of both VIs, VISA resource empty): **16/16** — five positive
vectors × two baselines identical to the original to the last bit; `FFFFFFF6` → −7.2°, `FFFFFFFF` → −0.72°,
`80000000` → −1.546e9°; the original returns +3.09e9° for `FFFFFFF6`. Facts read off the run: **Get Position =
`Ring` 2**, **k = 0.72 °/pulse (500 pulses per turn)**, the substring window is the 8 hex digits, and
**`Baseline Startpoint` is in TURNS** (200 → 72000° subtracted, i.e. the controller coordinate carries a
+100 000-pulse offset today).

**Hardware acceptance PASSED 20:22 (`archive/bench-2026-09-14-rotor-sign/hw_rotor_signed_test.log`, motion approved
by the user):** the controller is a two-axis PMC-2HS (`POS 000186A0,00000000`). `CLL X` cleared the counter without
motion, `PIC -10` moved the rotor −7.2° and the signed copy read **−7.2°** while the original read **+3 092 376 445.92°**
from the same reply `FFFFFFF6`; `PIC 10` brought it back to `00000000`. Completion was judged by two consecutive
identical `POS` reads. Raw commands went through `claudeDev\RAWCMD_rotor.vi` (a Configure.vi copy whose init constant
is replaced by a string control). **The controller counter was left at 0** — the new baseline-0 convention; the
original main VI (Baseline 200) would now command its first absolute move as a 200-turn trip, so either restore the
old coordinate (`PIC 100000`, 200 turns) before running the original again, or run only the new VI. Remaining:
repoint the NEW main VI's rotor calls to `SetCommand_signed.vi` (stage 2).

## (history) If it were to be fixed — DECIDED by the user 18:3x: fix it (on a copy, for the new VI)

The change would be inside a **vendor driver VI**, which this project never modifies in place. The shape would be:
give the string-to-number conversion a **signed** default (`0` as I32 rather than `0uL`) and drop the Type Cast,
so a `-1` reply parses as −1 directly. The baseline could then be 0 and the controller's own signed coordinate
used end to end.

Three cautions, because this is a working instrument:

1. **It changes behaviour.** Every stored schedule and every habit of the operator is expressed in the current
   coordinate. Changing the baseline meaning silently re-interprets them.
2. **Do it on a copy.** `instr.lib\Autonics Motor\SetCommand.vi` is the vendor original; a modified copy belongs
   under `claudeDev`, with the main VI repointed only after the numbers are verified.
3. **Acceptance is numeric, on hardware.** Command a known negative angle, read the position back, and require
   the returned degrees to match the commanded degrees — with the rotor detached, which it currently is.

**It is also not required for the restructuring.** The scheduler's rotor row calls `SetCommand.vi` exactly as the
existing `Send to Rot` path does, with the same `Baseline Startpoint` source. The workaround stays intact and
harmless, per the user's own instruction: *"configuration은 그대로 쓰면 되는데 왜 자꾸 바꾸려고 하는거야?"*

**20:28 visible test (user watching, "확인함"):** `PIC -1500` = −3 turns → the signed copy tracked −2.9 → −399.6 →
−788.4 → **−1080.0°** (`FFFFFA24`) in ≈1.7 s (≈ 850 pps at the current SPD), 5 s pause, `PAB 0` → **0.0°** in ≈2 s.
Direction confirmed by eye by the user; absolute origin return works with the counter at 0. `hw_rotor_visible.log`.
