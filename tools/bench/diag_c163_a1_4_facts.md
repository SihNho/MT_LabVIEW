---
type: facts
status: current
date: 2026-10-10
card: 163-a1-4
---
# 163-a1-4: fp-86 fixed in stagekit PB (class 3 = class 2 carried from an adopted step); step-3 dry PASS-UNVERIFIED (CEN2), prerun PASS, scratch-required rc 3
## Part 1 - measured (diag_c163_a1_4_ctx.py -> diag_c163_a1_4_ctx.log, offline)
- ctx (plan_ring_p5s02c, dry bindings): chain 12 plans p5s02b..p4_s02v18, missing []; frames {376,3052,3453: [31506]}; cases {31308: [31506,31517],
  30726: [30914,30922]}; connects {(376,'frame index'): w_c7_fi}; made/tunnel_case = this plan's t_ci7/t_co7 on 31308 (ctx.log:3-7).
- Both blocked sinks: R0 == bound_end True; after0 = 4 sources (376 / 4910 'error out', resp. 376 'total data array out' / 781) on tunnels
  31593/31598 (31628/31640) x frames 31506/31517 (ctx.log:9-14). Class 1 fails on S1 uid MULTISET ([3934,3934,4965,4965] vs [3934,4965]) and frame
  31517 not inherited ([31506]); class 2 fails on (i) base after != [] / no connect of THIS plan, so cf = [] -> (ii) want [0], (iii).
## The change (tools/stagekit.py 9b8f82c1 -> dd57c1ca; only file of the tool chain edited; no hooks)
- pb_inherit_ctx (:2078-2083): per adopted plan in the chain (after the md5/json/bound checks) collect chain_connects {(node, term): (plan, wire
  action)} (newest plan wins) and chain_tunnel_case {real tunnel uid via THAT run's bindings: (plan, case)}; 2 new ctx keys (:2049-2050).
- pb_inherited_row (:2127-2150): no connect of this plan + a chain_connects entry -> class 2's checks with (i) = base PB == end, (iii) = tunnels
  of THAT adopted plan only; (ii)/(iv) unchanged -> class 3. Class 1 untouched; class 2 path identical (cc None). Docstrings updated.
- git diff --stat vs HEAD shows 847 lines, but HEAD (ab9773cc) != the card's input 9b8f82c1; this card's edit is 4 hunks (~+25 / -6 lines).
## Self-tests (logs tools/bench/diag_c163_a1_4_st_<name>.log; before = last stored log)
- NEW selftest_c163_pbchain.py (6f087675) 10/0: C0 chain, A1 #376 t0/t1 class 3 + PB ok, A2 ctx without chain = 163-a1-3 BLOCK reproduced, A3,
  N1 frame 999993, N2 source uid, N3 multiplicity 3 / 1, N4 foreign tunnel, N5 base != end, N6 wrong plan -> all BLOCK.
- Unchanged PASS: c161_pbinherit 10/0 -> 10/0, c158_gates386 16/0 -> 16/0, c158_runcheck 10/0 -> 10/0, t6_poskey 43/0 -> 43/0, t7_ring 35/0 -> 35/0,
  c160_stagemap 5/0 -> 5/0; c159_cen2_ends 6/0 -> 8/0, c157_innerface 12/1 -> 13/0 (test files grew since their last log).
- Stagekit PIN gates now fail (expected after any stagekit edit; 161-a3-1 re-pinned the same way): c160_delwire 12/0 -> 18/2 (P0, V1),
  c161_delckpt 11/0 -> 10/1 (P), c155_basecase_frame 21/0 -> 20/1 (P1). NOT re-pinned: those files are outside this card's write globs.
- Failing for reasons outside stagekit (pre-existing pins / stage_prerun only): c147_b1_2 17/0 -> 19/1 (P0 stagexec 1bab9cf9 pin), c159_a4_1
  12/0 -> 12/1 (G1 stagexec 7a712ccb pin), c155_gatefp73 10/0 -> 8/2 (G1/G5 discard_work; tests stage_prerun.vi_modifying_calls, 7605116f unchanged).
## Peer
- archive/peer/2026-10-10-c163-a1-4-pbchain.md (claude hypothesis, ANSWERED, $1.38): no wrong row in step-3 data; classes 1/2 not loosened;
  objections: class 3 trusts plan wire actions, not PB gate records (P4 plans pre-c158 never PB-gated); multiplicity rule != per-frame coverage
  (shared with class 2); chain_tunnel_case oldest-wins vs chain_connects newest-wins (fail-safe). Disposition written; nothing applied (OPEN).
- Prior-art: not run - no launch/check gate demanded it in this card.
## Part 2 (new stagekit bytes; 163-a1-3 pred / licence / EL reused unchanged - the pred carries no stagekit md5, no regeneration)
- DRY main prep_c163_a1_4_dry.log:61 `=== DRY PASS-UNVERIFIED CEN2 ...` rc 0; PB RECORD 5 rows (:51-55: 3 class 1, error in / total data array in class 3).
- DRY scratch prep_c163_a1_4_scr_dry.log:84 PASS-UNVERIFIED CEN2, same 5 RECORD rows (:70-74), rc 0.
- PRERUN main prep_c163_a1_4_prerun.log:87 PASS 16/0: X10 peak 658.3 <= 675 (:83), X14 12 rows budget 15 (:84), X17 PASS (:72), X8 PASS (:63).
- PRERUN scratch prep_c163_a1_4_scr_prerun.log:110 PASS 16/0 (X10 653.2).
- --scratch-required prep_c163_a1_4_scrreq.log:3 rc 3: `SCRATCH-REQUIRED | ... CENSUS-UNPREDICTED ... rows [1..12] - the scratch run measures the census`.
## md5 UNCHANGED
stagexec a4df7e15, stagesim 95a162ba, stage_prerun 7605116f, stage_shared b688edd4, memory_model def9e640, plan 930699ec, graph 431cfd83, pred fc908036,
licence c8fdf33a, EL 373e0bf4, recipes 6d1d5786 / a517557d, selftest_c161_pbinherit 9be05189 (not edited). Bed VI f9ae7751 by dry K1; LabVIEW never launched.
## OPEN
- Re-pin stagekit dd57c1ca in selftest_c160_delwire / c161_delckpt / c155_basecase_frame / prep_c163_a1_3_pred.py+_md5.py, and open cards 160-c3-2 /
  161-b3-1 (guard_write stale-pin warning) - outside this card's globs.
- Review items for judgement: add a provenance condition (adopted scratch log `RECORD PB <sink>` with after == after0) and/or per-frame coverage to class 3.
- check-launch needs a card naming `DRY-UNVERIFIED-OK: CEN2 new-object census`; next step is the scratch launch card.
