# Card 135-P1 — P4 (loop 1.2 reader) sizing, OFFLINE, provisional

Draft: `tools/bench/plan_ring_p4_draft.json` (provisional, `never_launch: true`, NOT simulated/finalized). Base = stagesim
END graph of P3b-2 b `tools/bench/sim/ring_p3b2b/step_18_wire_remove_loose_ends.json` md5 `81ed697b…` (P3b-2 not launched).
Generator: scratchpad `gen_p4.py` (counts are recomputed from the action list, not typed).

## Where loop 1.2 is (measured on the base graph)
- Loop 1.2 = While `#10170`, body `#23166`, on `#686` (owns `#5058`, `#2626`, `#11261`, For `#1359`/`#29874`). Loop 1.1 = `#637`/`#639`; 1.7 = `#23041`/`#23405` (`#376`).
- `#5058 Image In` t5089 unwired (open row PD177(e)); `#23166` iteration terminal t23225 unwired.
- **Stop of 1.2 = `#10171 Equal?` with x and y on the SAME wire 23255** (tunnel `#23417` ← `#8486 x+1` on `#686`) ⇒ TRUE for any value ⇒ loop 1.2 runs ONE iteration as built.
- `#10068`/`#29240` sit in loop 1.1 body `#639`; their `x` is on net -40 (= `#637` i t644, re-created by P3b-2 b), their outputs (w10187, w29787) have NO sink. Their consumers are For-loop tunnel faces in 1.2 left unwired: `#10177` t10182 (→ `#8634 index (col)`), `#29777` t29782 (→ `#29625`, `#29973`). `y` = `#686` controls `# FD points` t8936 / `# DT points` t28844 via 1.1 tunnels `#10114`/`#29415`.
- Unwired 1.2 tunnel faces for frame-paired values: `#9503` t9508 (→ `#28083 Magnet position`, was `#30117`), `#11363` t11369 (← `#11608`, display only, not a ring value). `#2626` element|0/1/2 = t2832/t4160/t4165 ← `#5119 x-y` / `#30117` / `#4580` (`facts_c117_qrt.json`).

## Draft shape (choices marked open in the JSON)
R (reader core, 68 actions / 62 ops): registers `last` (I32 −1) and discard count (I32 0) on `#10170`; an inner wait-for-new While W1
(local `Num` → `Greater?(Num,last)` → `Select(mask, Num, MAX)` → `Array Max & Min` → stop when `min < MAX`; `Wait (ms)` 1) giving n1 and
slot i; `Index Array(pool, i)` → `#5058 Image In` (pool crossing from `#23099 New Image`); n2 = second `Num` read inside a 1-frame FS
ordered after `#5058`; valid = `n1==n2 AND n1>-1`; `last := valid ? n1 : Latest−1` (jump); discard += NOT valid.
C (slot-value consumers, 25 actions): `TransPos/RotPos/FrameIdx(i)` → t9508, `#2626` t4160/t4165; MOVE `#10068`/`#29240` into `#23166`
with `x ← FrameIdx(i)` and `y` crossings; outputs → t10182 / t29782.

## Counts and X10 (formula `memory_model.json:5`, start = P3b-2 b scratch `stage_d1_ring_p3b2b_scratch_c134_5.log:57-58`, 572.5 + 5.5 = 578.0)
| scope | actions | ops N | R | X10 @578.0 | X10 @590.9 (+18 × 0.719 load growth, `memory_model.json:18`) |
|---|---|---|---|---|---|
| R + C | 93 | 87 | 43 | **824.2** | 837.1 |
| R only | 68 | 62 | 35 | **769.5** | 782.4 |
Largest op prefix ≤ 675 MB at 578.0 = **21 ops**, ≤ 690 = 24. ⇒ R alone needs ≥ 3 LabVIEW sessions, R+C ≥ 5; N ≤ 40 fails for R+C (93) and R (68).
Dropping `n1>-1` (implied: W1 only exits on `Num > last ≥ −1`) saves 7 ops — not applied (PD238(e) text keeps it).

## Route levels (per action in the JSON: `route_level` + `cite`)
R: MEASURED 20 / PRECEDENT 42 / UNMEASURED 6; C: MEASURED 2 (RLE) / PRECEDENT 23. UNMEASURED: Select with a Boolean ARRAY `s`
(only scalar measured, P3b-1), the I32 MAX constant on a not-yet-typed terminal, an ordering-only FS input tunnel with no inner sink
(PD237(d) assumed a count-1 For), a branch from a plan-made While tunnel across a plan-made FS border, an FS-frame EXIT to its parent.
Nested FS `2499`, `14682` (both in FS2 frame `13236`) and `43914` (FS1 frame `124`) are siblings, NOT on any P4 path; the pool path
crosses only FS2 `12938` / FS1 `681` borders measured by P3b-1 action 28.
