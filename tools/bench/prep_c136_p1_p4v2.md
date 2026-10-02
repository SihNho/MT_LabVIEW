# Card 136-P1 — P4 plan v2, OFFLINE (no LabVIEW, no VI opened)

Plan `tools/bench/plan_ring_p4_v2.json` md5 `0d67d704…` (stageplan/1 valid, `protocol.py validate` OK; never launched, PROVISIONAL
base). Per-action meta (group, unit, build step, LabVIEW session, route level, measured_by, cite):
`tools/bench/plan_ring_p4_v2_meta.json` md5 `f06bbd57…`. Base = the `state` of `sim/ring_p3b2b/step_18_wire_remove_loose_ends.json`
(md5 `81ed697b…`) extracted to `tools/bench/sim/ring_p4_v2_base_p3b2b_end.json` md5 `37598c84…` (stagesim.base_state takes a step
STATE, not a step file: first replay died `KeyError: 'terminals'`, `prep_c136_p1_sim.log:3-12`); `sim_of` = `plan_ring_p3b2b.json`.
Generator: scratchpad `gen_p4v2.py` (counts recomputed from the action list).

## 0. fp-30 (`selftest_c134_1_dry.py` 10/1)

- Failing gate found: **T7a**. Since 135-2 the recipe's CEN2 has a DECLARED census, and the dry prints
  `UNVERIFIED-DRY  CEN2 … (census not measured in a dry run; declared {…})` (`selftest_c134_1_dry_c136_p1_t2.log:75`), not
  `UNPREDICTED  CEN2`. Fixed at `tools/bench/selftest_c134_1_dry.py:85-91` (accepts UNPREDICTED or UNVERIFIED-DRY, still never PASS).
- The other gates re-run one by one in fresh processes, same commands: T0/T1 (`…_diag.log:3-4`), T2 (`…_t2.log` DRY PASS),
  T3 (`…_diag3.log:4`), T3b/T3c (`…_diag3b.log:4-7`), T4/T5/T6 (`…_diag46.log:3-5`) all as predicted. T7 (fake `_S` census gate) not
  re-run (needs `import stagekit`).
- The self-test itself was NOT run under this card: `guard_peer` refused it (hypothesis review owed for another card's
  `launch_p3b2_c135_e.log`; the script counts as LabVIEW-touching through `selftest_c134_1_dry.py:157 import stagekit`). Same class as
  fp-30 → logged **fp-32** (`gate_fp_queue.jsonl`). The release needs an OFFLINE_SELFTESTS entry in `tools/protocol.py:398` (not in
  this card's write flags). **fp-30 stays OPEN, not drained.**

## 1. What v2 changes against the draft d9d66246 (159 actions / 154 ops; draft 93 / 87)

| PD | change | actions |
|---|---|---|
| 293(b) | Select `valid ? new : old` on each of the **6** registers of `#10170` (graph step_18: R/L 23508/23792, 10850/25240, 25339/25344, 25371/25382, 9603/10544, 25545/25582). No single-sink disconnect op exists (stagesim OPS `stagesim.py:2107-2110`), so each = delete the new-value wire + re-wire its other sinks + Select + 4 wires | 43 (10/8/6/7/6/6) |
| 293(c) | valid = `n1==n2 AND n1>last`: GT2.y = `last` (branch of SL1L inner, `p4_w_last_gt`); draft `p4_k_m1` + `p4_w_km1_gt` dropped | −1 |
| 293(d) | W1 stop: Local `stop (end)` read in W1 body + Or (`$work #10247 'x .or. y?'`) of found/stop → W1.cond (replaces `p4_w_stop`) | +4 |
| 295(c) | 1.2 stop: delete w23310, delete scaffold `#10171`, RLE w23255, Local `stop (end)` on `#23166` → cond `#23246` | +5 |
| 295(d) | n2 FS input from a `#5058` output: the draft's `{diagram, border_only}` end is not a stageplan/1 address (`docs/protocol/stageplan.json:204-243`) and no tool has a route for it (`border_only` appears only in the draft) → written as a `decide` action (3 options), counted as 2 ops | 0 |
| 295(a) | `BufDiff`: I32[20] const + indicator on FS1 `#4866`; 1.1 write in frame 32464 (Local read, Replace Array Subset, Local write, index ← `#27373`, value ← `#5119 x-y`); 1.2 Local read + Index Array(TS1) → `#2626` t2832 | +16 |

Program stop control = `stop (end)` (CT 642 on `#639`, panel uid 7): the only real stop in the base; loops `#23041`/`#23032` still stop on
x==x scaffolds `#23042`/`#23035` (graph step_18, read by scratch `g5.py`).

## 2. Build steps (≤ 40 actions, units kept whole) and LabVIEW sessions (X10 ≤ 675, memory_model.json formula incl. final read 17.4)

| step | units | actions | sessions: actions / ops / X10 @578.0 flat | X10 if start grows 0.719 MB per applied op |
|---|---|---|---|---|
| 1 | 1.2 stop, BufDiff 1.1, registers, W1 creates | 33 | 1.1: 22/22/661.2 · 1.2: 11/11/640.9 | 661.2 · 656.8 |
| 2 | body creates, W1 wiring, W1 out tunnels, image, n2 | 39 | 2.1: 30/24/669.0 · 2.2: 9/10/624.4 | **692.7** · 665.4 |
| 3 | valid, C reads, C sinks | 39 | 3.1: 39/39/674.5 | **722.7** |
| 4 | BufDiff 1.2, rollback SR A-D | 36 | 4.1: 36/36/665.3 | **741.5** |
| 5 | rollback SR E-F | 12 | 5.1: 12/12/622.1 | **724.2** |

5 steps, 7 LabVIEW sessions, all ≤ 675 at the flat 578.0 start the brief names; with the one-pair load-growth model 4 sessions exceed
675 (and 690). Whole v2 in one run: 154 ops, X10 959.7.

## 3. Route levels (binary, per action in the meta file)

MEASURED 51 / UNMEASURED 108 (3-way: MEASURED 51, PRECEDENT 102, UNMEASURED 6). UNMEASURED named to a 136-1 item: item 1 = 3 (U1 Select
Boolean-array s, U2 MAX const on untyped f, U3 Greater?(array,scalar) → s); item 2 = 2 (Or create, Or → W1.cond); item 3 = 2 (U5 TS1
outer → FS4 frame, U6 FS4 frame → body exit); item 4 = 1 (1.2 cond mode). **Not covered by any 136-1 item: 100** — 96 routes that ran
only on another diagram class (inside a plan-made While body, tunnels/stop of a plan-made While inside a While body, the Select
rollback re-wires, the C consumers), plus: n2's border-only FS input (`decide`), `#5119`'s output type for BufDiff (no type reader), and
the mechanical action of `stop (end)` for both new Locals (a latch-action Boolean cannot have a local).

## 4. stagesim replay (`tools/bench/prep_c136_p1_sim.log:14-82`)

Actions 1–63 replayed ok, computation_diff 16 rows at every step (= the base's 16; `:16`, `:78`). **Action 64 `p4_x_pool` ERROR**:
`#23099 New Image` (diagram 23169) → `new:IAI1.array` (body 23166): "a border needs a tunnel/register action first" (`:79`). The draft
reuses P3b-1's multi-border `connect_term_uid`, which stagesim models only into a plan-made FS frame (`stagesim.py:1361-1368`).
`SUMMARY final=False`, no end cdiff (`:80`). Not diagnosed, not retried. Step files 0–64: `tools/bench/sim/ring_p4_v2/` (~2 MB each).

## 5. Rule-1a list — original terminals whose wiring changes in v2

| terminal | v2 source (was) | why the computation is kept |
|---|---|---|
| `#5058` Image In t5089 | Index Array(pool, slot i) (open row PD177(e)) | slot i holds the IMAQ Copy of that frame's image (P3b-1); valid frames track the same pixels, others are discarded (U9) |
| `#2626` t2832 / t4160 / t4165 | BufDiff(i) / TransPos(i) / RotPos(i) (was `#5119 x-y` / `#30117` / `#4580`) | each value is written in 1.1 for that frame and read back for the same slot (PD233(f)(1)(2)); n1==n2 rejects a torn slot |
| `#9503` t9508 (→ `#28083`) | TransPos(i) (was `#30117`) | as above |
| `#10068` / `#29240` x, y; outputs → t10182 / t29782 | x ← FrameIdx(i) (was `#637` i); y ← same `#686` controls across the `#10170` border | same operands per frame (PD233(f)(3)); controls cross non-indexed |
| 6 right-register inner faces of `#10170` (t23798, t25246, t25347, t25385, t22281, t25596) | Select(valid, new, old) (was new) | valid ⇒ new, the original value (U1); invalid ⇒ old = the frame did not happen (U9, U13) |
| other sinks of the 6 detached wires (t10871, t10975, t3173, t9519, t4168, t2811, t25573) | re-wired to the same sources | no change |
| `#10170` cond t23246 | Local `stop (end)` (was S2 scaffold `#10171`, not original) | loop lifetime only; the original tracking stop is `#648 ← #11639` (3-way OR) |
| `#5119` x-y, `#27373` x-y*floor, `#23099` New Image | gain a sink | adding a sink changes no value |

## OPEN (facts for judgement, nothing decided here)

- PD293(b)'s "handed to 1.7 only when valid": the base has no 1.2→1.7 hand-off (`#2626` appended array t2813 unwired; open row 376 is
  QRT/P5) — nothing to gate in P4; `valid` = `new:AND1.x .and. y?` is available to P5.
- The tracking body also publishes results outside the registers: `autofocus reseed flag` t25557, `autofocus reset count` t25573 (to
  1.1 by locals), `Pos within cal image` t3173, `Pos: Diffraction Pattern` t9519, `#2626`, display — v2 keeps them on the raw (not rolled
  back) values; PD293(b) names registers only.
- Whether 6 registers × ~7 actions (43) is wanted, or a cheaper rollback form; and D-2026-10-02-03 (5 build steps / 7 sessions).
