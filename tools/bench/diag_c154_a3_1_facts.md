---
card: 154-a3-1
status: current
date: 2026-10-09
---
# 154-a3-1 facts - refnum forms S and L both clean; CHOSEN: S; X17 has the four DonorQueue_v0 entries (offline, LabVIEW 0)

## Census (`tools/bench/p5_route_census.md` section "Card 154-a3-1"; log `diag_c154_a3_1_census.log`, RESULT 6/0)
- Form S: 10 rows (S1-S10) OK, 0 GAP; with the unchanged rows the whole fragment compiles to 22 ops (log:47, `GAPS S: []` log:48).
- Form L: 7 rows (L1-L7) OK, 0 GAP; compile 20 ops (log:86, `GAPS L: []` log:87).
- `CHOSEN: S` (log:90; rule PD376(b): every S row OK). The registered re-run gives the same rows and CHOSEN (`..._registered.log:90`).
- OK with no launched precedent: S5 Obtain 'queue out' -> SR L.outer (no plan wires a node output into L.outer; only consts, census row 12);
  L5 local_read in a CASE frame (only FS frame / loop body launched). S6-S8 reuse rows 14-16's R1/R2/pass-through routes.
- P5-2 refnum rows (report-only): S-mirror 29 ops all OK (log:132-143: 1.7 SR #23041, 2nd branch of Obtain, Dequeue on L.inner
  wire_sr LeftIn, queue out -> R.inner RightIn, R.outer -> Release on 686); L-mirror 26 ops all OK (log:179-193). No GAP.
- No SimError, no crash in any row; Vb's TypeError (stagesim.py:1783, PD376(e)) is not on any S/L path.

## Script copy (step 1)
`diag_c154_a3_1_census.py` = copy of `diag_c154_a2_3_census.py`; changed: docstring/predictions, card pins (ring-p5.md 9c5ba571, +donor
json 15269b6c, stage_prerun checked before==after only), action lists (A0 common rows, S_REF, L_REF, P52), the census() loop and the
`--registered` X17 expectation. Old REF Va/Vb/Vc forms dropped.

## X17 registration (step 5)
- json check: roles obtain/enqueue/dequeue/release = uids 108/44/45/46, labels Obtain Queue/Enqueue Element/Dequeue Element/Release
  Queue, class "Function" (donor_queue_v0.json:34-37,99-102,157-160,215-218) - match, no return.
- `tools/stage_prerun.py:2809-2813` four entries added (md5 81dba822efec5226123b3b88ee4383bc, cite donor_queue_v0.json).
- stage_prerun.py md5 c739eb86e0aa3644a1008b8f3fa2af38 -> 9decb20f6d67793abad967347e2a37ab.
- Self-test `selftest_c154_a3_1_x17.py`: baseline (before edit) 7/0 (`selftest_c154_a3_1_x17_baseline.log`, O0-O5 + N0); after 11/0
  (`selftest_c154_a3_1_x17.log`: O0-O5 6/6 unchanged, N1-N5 pass: 4 uids pass, wrong label/class refuse, uid 999 UNMEASURED).
- `selftest_c154_a3_1_x17_baseline_after.log` 6/1: a deliberate post-edit re-run of baseline mode; N0 'keys ABSENT' fails because the
  keys are now present (negative control); O0-O5 6/6 = same as before.
- `selftest_prim_gate_c141_1.py` (the only other PRIM_DONORS self-test) NOT RUN: guard_bash refuses it under labview:none (its
  header says labview: read although it is offline) - logged gate-fp fp-74. Its O0-O5 are copied verbatim into section O (6/6
  before and after); its R1-R6 test stagexec.prim_check only (stagexec 1bab9cf9 unchanged). Last run 13/0 on 2026-10-02.
- Step 6: X17 on the CHOSEN form's queue creates (c_obt, c_enq + P5-2 c_deq, c_rel): no refusal (`..._registered.log:195`).
- guard_write on the edit: open cards 149-a3-4 (pins dcd45aba) and 150-a2-6 (pins c739eb86) pin stage_prerun.py and are now stale.

## Invariants (`diag_c154_a3_1_inv.log`, RESULT 3/0)
stagekit 604529e8, addrcheck 207beb0d, stagexec 1bab9cf9, stagesim 78b8d5a1, gscript 1a80236e, vigraph a7eb58c7, memory_model 6f2b5687,
s09 VI eb1d0f31 (never opened), graph 22f967b5, DonorQueue_v0.vi 81dba822, donor json 15269b6c, ring-p5.md 9c5ba571: held. tools/hooks,
tools/recipes, P4 plan/pred files unmodified (only hooks/material_marker.log, pre-existing). LabVIEW processes: 0.

OPEN: none from the census; stale stage_prerun pins on open cards 149-a3-4 / 150-a2-6 are for their owner.
