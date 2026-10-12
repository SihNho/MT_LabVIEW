---
card: 169-a1-1
status: current
date: 2026-10-12
---
# Facts 169-a1-1 - P6-1 BLOCKED before any LabVIEW launch: guard_cycle requires a prior-art review of the new recipe; card peers []

Result: BLOCKED. No LabVIEW session was started, no VI was opened or saved, no D1_ring_p6_* file exists in claudeDev.

1. Hash before: 8/0 (`diag_c169_a1_1_hash_before.log`): 23 card inputs + 7 VI pins equal (75773b0d 7f2582ae eb1d0f31 94ffff94 f9ae7751 564d8cbe 6dcd5c3d).
   `protocol.py requires` PASS 6/0 (`cards/requires_169-a1-1.json` 35b214ba).
2. Extraction (brief step 2, docs/script-writing.md rule 4) into `tools/bench/prep_c168_a1_2_lib.py` (88ddf8d6 -> 93e3bffb): `fs3_check`, `tunnels_read`,
   `fs4_check` (old inline copy `diag_c168_a1_2_rbwdel.py:138-150`, left as the record) and `cdiff_rowset_diff` (PD406(b), new). Self-test 10/0
   (`prep_c168_a1_2_lib_selftest_c169.log`): T7 F-S3 on 57f33e7c PASS = recorded; T8 F-S4 replay of the 168 tunnel reads PASS, altered IndexMode fails;
   T9 57f33e7c vs itself 30 rows, both differences empty; T10 57f33e7c vs 7815af09: only-57f33e7c sink t8323, only-7815af09 sinks #11261 array/element.
3. Recipe `tools/recipes/stage_d1_ring_p6.py` (85f2615f): rows `rbw_method410` + `delete_object` (class/uid from diag_c168_a1_2_plan.json); gates
   A0 A1 R1 D1 (labels per brief), E5 W22 G1 FS1, EL0-EL3, S-1..S-5 as real gates, save only if all pass (Stage.save broken_ok=False), PS, M, X.
   `--scratch` = same rows/gates, never saved.
4. Dry (`launch_c169_p6_dry.log`): `=== DRY PASS-UNVERIFIED A0 ...; A1 ...; R1 Wire count drop after RBW 2091 -> 2066; D1 #11261 absent after delete
   and Wire objects 2066: first_fail=None coverage 69/140 lines ... graph tools/bench/graph_ring_p5s02e_20261012_173009.json`.
5. Prerun (`launch_c169_p6_prerun.log`): `=== PRERUN PASS: 15 pass / 0 fail`; X10 `N 2 ops, BIND 0, R 2 reads, predicted peak 678.9 MB (fail above
   680.0)`, start 653.7 = load_by_vi 647.8 + op-0 5.9; WARN X14 rows 22, budget 15. memory_model.json unchanged (d12bcd3b).
6. `--scratch-required` (`launch_c169_p6_scratchreq.log`): `SCRATCH-REQUIRED | stage_d1_ring_p6.py | not a proven pattern (1 clean other stage(s)
   ['diag_c168_a1_2_rbwdel.py']; needs 2)`, rc=3 -> brief step 3: ONE scratch first (`--scratch`).
7. The scratch launch (bgrun --material --unverified-card ... stage_d1_ring_p6.py --scratch) was REFUSED by tools/hooks/guard_cycle.py:
   "this RECIPE HAS NO PRIOR-ART REVIEW NEWER THAN ITSELF ... newest priorart review archive\peer\2026-10-10-priorart-priorart-c165-a3-3-p5s02e.md"
   (guard_cycle.py:604; proven-pattern and diff-only releases did not apply, :572-593). The release is a prior-art review
   (`tools/prior_art_review.py --recipe tools/recipes/stage_d1_ring_p6.py`, a peer) - this card's flags.peers is []; not dispatched.
   168 ran the same rows as `tools/bench/diag_*.py`, which guard_cycle does not cover. Not a false positive: no review of this recipe exists.
8. Hygiene: no LabVIEW process (tasklist: none), no claudeDev file matching p6/c169, no scratch made, no original opened, no hooks edit,
   STATUS/INDEX/plan untouched, memory_model.json not edited (no saved file -> no load_by_vi entry).
9. Hash after (`diag_c169_a1_1_hash_after.log`): 7 VI pins equal; inputs 22/23 equal - the one drift is prep_c168_a1_2_lib.py (88ddf8d6 -> 93e3bffb),
   this card's own extraction (item 2).
10. Not reached: launch, ExecState values, MEM lines, S-1..S-5, save, post-save reads, load_by_vi entry.
