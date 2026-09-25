---
type: reference
status: current
date: 2026-09-25
tags: [autofocus, asi, main-vi, rule-1a, offline]
card: chat-F1
sources:
  - docs/wiki/subvi/D1_s1_copy.json (md5 5de014fe580b938328fa8662cf2b0652; VI D1_s1_copy.vi md5 3e3d23cefd3a334001aa9d6156bf1aee)
  - tools/bench/graph_objs_s1_20260923.json (object classes / owners, same VI md5)
  - tools/bench/opconstvaluen_scan.log (constant values, 2026-09-15 read; same object and wire uids)
---

# Autofocus — the body of `CaseStructure #10407`, read offline

For Pre-decided 190(d) (`docs/connectivity-map-plan.md`; numbered 148 until card chat-L2): the focus loop of 190(b) must copy this computation
exactly (rule 1a). Read entirely offline; **no LabVIEW was started**. Level: **structural** (wires and constant
values read from files) — nothing here has been run.

## Where it is

| item | uid | evidence |
|---|---|---|
| Case structure | `CaseStructure #10407` on the frame-loop body diagram **639** (S1 numbering; `camera-acquisition-facts.md` calls the same body "diagram 43") | `graph_objs_s1_20260923.json` (`class CaseStructure`, owner Diagram) |
| selector | `Tunnel #10429` ← wire 10799 ← `Function #10686` `x .and. y?` (the 25-frame schedule AND the enable) | wiki `wires` row 10799 |
| frame with the move | **`Diagram #10423`** (holds every node below) | wiki `terminals`, `frame_diagram` 10423 |
| other frame | `Diagram #10417`: pass-through only — `Out position` → `position [internal units]` (wire 5773), `Outgoing Handle` → `VISA out` (wire 11303) | wiki `terminals`, `frame_diagram` 10417 |

## Inputs (selector tunnels on the case border)

| tunnel | name | outer wire ← source | used in #10423 by |
|---|---|---|---|
| `#10978` | `Index of closest\ncal image slice, bead 2` | 10990 ← `IndexArray #10757` `element` ← wire 121 `pos in cal image out` of `Track N beads four-fold over-kernel-v3.vi #5058`; **index = `DigitalNumericConstant #10929` = 0 (I32)** | `#9703` x |
| `#9623` | `# slices in stack` | 9635 ← `LoopTunnel #9641` (calibration stack size) | `#9243` x |
| `#11220` | `Outgoing Handle` | 11232 ← `ASI_adjust focus-subvi.vi #48` | `Move Axis Relative #26539` `VISA in` |
| `#11348` | `Out position` | 7388 ← `#48` `Out position` | **unwired** in #10423 (used only by the pass-through frame) |
| control | `Focus Deviation from the Center` | its terminal sits **inside** #10423 (owner `Diagram #10423`, wire 9797) — read only when the case fires | `#9621` y |

## The computation (frame #10423)

| step | node | inputs | output wire | constant value (scan log line) |
|---|---|---|---|---|
| 1 | `Function #9243` `x/y` | x = `# slices in stack` (9612), y = `#9308` (9340) | 27156 | `#9308` = **2.0** DBL (`opconstvaluen_scan.log:65`) |
| 2 | `Function #9703` `x-y` | x = bead-index-0 slice index (27107), y = step 1 (27156) | 9769 | — |
| 3 | `Function #9621` `x+y` | x = step 2 (9769), y = `Focus Deviation from the Center` (9797) | 9853 | panel control, value not read here |
| 4 | `Function #9889` `x*y` | x = step 3 (9853), y = `#11011` (11029) | 11513 | `#11011` = **1.0** DBL (`:66`) |
| 5 | `InRangeAndCoerce #25455` | x = step 4 (11513), lower = `#26472` (26765), upper = `#25845` (26070) | `coerced(x)` 26993; **`In Range?` unwired** | lower **−0.2**, upper **+0.2** DBL (`:68`, `:67`) |
| 6 | `ASI TG-1000.lvlib:Move Axis Relative.vi #26539` | `Relative Position [internal units]` = step 5 (26993), `Axis` = `EnumConstant #18509` (18735), `VISA in` = `Outgoing Handle` (11209) | `VISA out` 11283 | Axis enum value **not read** |
| 7 | `ASI TG-1000.lvlib:Get Current Position.vi #19093` | `Axis` = same enum (18735), `VISA in` = 11283 | `position [internal units]` 13848; `VISA out` 29193 | — |

In one line:

```
move_rel = clamp( ( idx_bead0 − (#slices / 2) + FocusDeviationFromCenter ) × 1 , −0.2 , +0.2 )     → Move Axis Relative
```

## Outputs

| where | uid | wire | goes to |
|---|---|---|---|
| `Local #11574` `Focus Pos (Track)` (write) | 11574 | 13848 | the panel indicator (a local, inside the case) |
| out tunnel `position [internal units]` | `#2017` | 13848 → outer 9113 | `SelectorTunnel #12673` (another case) and `RightShiftRegister #4256` |
| out tunnel `VISA out` | `#11263` | 29193 → outer 7337 | `RightShiftRegister #4334` (the VISA session register) |
| `error in` / `error out` of #26539 and #19093 | — | wire 0 | **unwired** — errors are not chained or reported |

## What the table says about the design in force

1. **There is no threshold compare in #10407.** `Focus Deviation from the Center` is **added** to the error (an offset of
   the setpoint), not compared against it; the only bound is the **±0.2 clamp on the step**, and `In Range?` is unwired.
   Every time the case fires it commands a relative move — a zero move when the bead sits exactly on the setpoint.
2. **The setpoint is the centre of the calibration stack**: `# slices in stack / 2` in cal-slice-index units, shifted
   by `Focus Deviation from the Center`.
3. **The bead is index 0** of the kernel's `pos in cal image out` array (constant `#10929` = 0), despite the terminal label
   "bead 2" — consistent with the user's "first-clicked reference bead" **if** array index 0 is the first click (not
   verified here).
4. **`Focus Step (F1)` is not read by #10407.** Its terminal is bare (`docs/main-vi-panel-map.md:282`); it reaches
   `ASI_adjust focus-subvi.vi` by reference (`main-vi-panel-map.md:552`), i.e. the manual focus path, not this one.
5. The step multiplies the slice-index error by 1.0 into ASI "internal units" directly — no unit conversion sits in
   the case.

## Not read (name, not guess)

- the value of `EnumConstant #18509` (`Axis`) — enum constants are outside `opconstvaluen_scan` (numeric only);
- which case frame is TRUE — frame names are not in the wiki; #10423 = TRUE is inferred from its content (the move) and
  #10417 being a pass-through;
- the `Include upper/lower limit?` settings of `InRangeAndCoerce #25455` (irrelevant to the clamped value, relevant only
  to the unwired `In Range?`);
- the numeric representation of the index on wire 10990 (the wiki carries no data types);
- the constant values come from the 2026-09-15 scan (`BGRUN END rc=1` for that run as a whole; the per-constant rows are
  `rep_ok=True`), matched to S1 by identical object AND wire uids — not re-read on D1_s1_copy.vi itself.
