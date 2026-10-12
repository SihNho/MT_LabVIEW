---
card: 169-a1-2
status: current
date: 2026-10-12
---
# Facts 169-a1-2 - P6-1 SAVED (all build gates PASS); post-save read FAIL on ONE self-check gate of the post script (script bug); returned before the Error List / load_by_vi

Result: FAIL (first unexpected result = post-save run RESULT fail 1; card chat-P2: return, no retry inside the card).

1. Hash before 8/0 (`diag_c169_a1_2_hash_before.log`): 25 inputs + 7 VI pins equal. requires PASS 6/0 (`cards/requires_169-a1-2.json`).
2. Prior-art review: `prior_art_review.py --plan-file brief_169-a1-2.md --slug priorart-c169-p6 --recipe stage_d1_ring_p6.py`
   (`diag_c169_a1_2_priorart.log`, 112 s) -> `archive/peer/2026-10-12-priorart-priorart-c169-p6.md:353` `PRIOR-ART: novel`;
   NOVEL RECORD for the recipe sha a096bccc249a. No objection; disposition written (same file, "What was done with it").
   Non-blocking notes: B2 fp-100 mislabel `gr["md5"] = BEDM` (stage_d1_ring_p6.py:97), header names task_169-a1-1 (:4,25). Recipe NOT edited.
3. Dry/prerun of 169-a1-1 stand (recipe 85f2615f unchanged): `launch_c169_p6_dry.log:54` DRY PASS-UNVERIFIED on exactly A0/A1/R1/D1,
   `--graph graph_ring_p5s02e_20261012_173009.json`; `launch_c169_p6_prerun.log:70,74` X10 678.9 < 680, PRERUN PASS 15/0; memory_model d12bcd3b.
4. Launch form: `--unverified-card` BEFORE `--` is rejected by bgrun argparse (rc 2, no LabVIEW); the accepted form is after the recipe path
   (as diag_c162_a1_2_checklaunch.py:18-22 records). check_launch on that form: ALLOW (`launch_c169_p6_checklaunch.log:3`).
5. SCRATCH (`launch_c169_p6_scratch.log`, rc 0, RESULT 29/0): copy scratch_c169_p6_20261012_212149.vi; ExecState before RBW 0 (:27), after RBW 0 (:33),
   after delete 1 (:42); Wire 2091->2066 (:35); MEM 599.9/600.1/600.2/607.5/582.0/583.9, peak 607.5 <= 675 (:377-378); E5 ok (:327);
   EL 0 items, window N 0 (:360); S-1..S-5 PASS (:368-372), S-5 rows 30 vs 30, both differences empty; scratch deleted (:386); refs 9/9 (:384).
6. `--scratch-required` re-run AFTER the scratch: still rc 3 "not a proven pattern (1 clean other stage(s) ['diag_c168_a1_2_rbwdel.py']; needs 2)"
   (`launch_c169_p6_scratchreq2.log:3-4`). The brief predicted 0; stage_prerun.py:4872-4877 counts only OTHER clean stages, so a scratch of
   the same recipe cannot change it. check_launch does not consult it (stage_prerun.py:5019-5026, advisory) -> launch proceeded.
7. LAUNCH (`launch_c169_p6.log`, rc 0, RESULT 32/0): ExecState before RBW 0 (:27), after RBW 0 (:33), after delete 1 (:42); Wire 2091->2066 (:35);
   MEM 603.4/603.6/603.7/610.9/585.8/587.4, peak 610.9 <= 675 (:385-386); E5/W22/G1/FS1 PASS (:328-331); presave graph
   graph_ring_p6_presave_20261012_212645.json 40a33490 (:332); EL errorlist_D1_ring_p6_presave_20261012_212645.json 0b3cece7: 0 items, N 0 (:360).
8. Pre-save gates (:368-372): S-1 ExecState 1 PASS; S-2 EL 0 items/N 0 PASS; S-3 #2626 4 inputs, sources == 7815af09 PASS;
   S-4 #5204/#10404 IndexMode+type == 7f2582ae PASS; S-5 30 vs 30 rows, only-this [] / only-57f33e7c [] PASS.
9. SAVED (:376-383): claudeDev\D1_ring_p6_20261012_212645.vi md5 c2d9c13cb40c0a5cab7433896d1df157, 511194 B; Stage.save S1/S2/S3
   (ExecState 1 re-read after save) PASS; input 75773b0d unchanged (:387,:393); refs 12/12 (:391); handles 45646 -> 51649 (:384).
10. POST-SAVE (`diag_c169_a1_2_post.py` 7cda957e; own dry `diag_c169_a1_2_post_dry2.log` DRY PASS, prerun `diag_c169_a1_2_post_prerun2.log:58`
    PASS 15/0, X10 592.5): run `diag_c169_a1_2_post.log` rc 1, RESULT 15/1, on byte copy scratch_c169_post_20261012_213318.vi (deleted, :328).
    MEM after load: 600.4 MB private (:27); ExecState on reload 1 (:28, ES PASS :309); E5 ok, deleted_nodes [11261] + 22 termless absent (:312-313);
    G1/FS1 PASS; graph `graph_ring_p6_20261012_212645.json` fbc7b7ee, 6221 rows / 10830 objs / 2066 Wire (:316); S-5 30 vs 30, both [] PASS (:317);
    peak 611.9 (:319-320); saved md5 c2d9c13c unchanged (:321, :329).
11. THE FAIL (:310-311): my own gate "DN exactly one node removed" got [11261, 11267, 11270, 11273]. The 3 extra uids are #11261's own
    Terminal objects (owner BuildArray, graph_ring_p5s02e_20261012_173009.json) - the gate counted terminals as nodes: a script bug, no
    machine claim. E5 itself used [11261] and passed.
    Jev: `diag_c169_a1_2_post.log | our-script-bug p=0.762 | NEXT-ACTION: patch the script and rerun | returned (chat-P2) | not rerun` (jev_gate.log:7477).
12. Not done (returned first): full Error List `errorlist_check.py --vi <saved> --role final`, errorlist_expected_D1_ring_p6_<ts>.json,
    the load_by_vi entry (memory_model.json untouched, d12bcd3b). The saved file STAYS on disk and is NOT adopted (brief step 6).
13. Gate-fp fp-101 (guard_peer): a `stage_prerun --check-launch` refusal (rc 2, `diag_c169_a1_2_post_checklaunch.log`, a decision while
    building the post script: dry PASS-UNVERIFIED on the unnamed ES gate + prerun X5 counting diag_c168_a1_2_plan.json as the read's plan)
    was held as a failed prediction; same class as fp-34 (guard_peer.py:189-193). Released once by RULE-GATE-FP (jev_gate.log:7473).
    The post script was then changed: ES gate after the DRY return (as diag_c165_a3_4_graph.py), deleted node from the two stored graphs.
14. Hash after (`diag_c169_a1_2_hash_after.log`): 7 VI pins equal; inputs 24/25 - drift docs/script-writing.md 0165fb24 -> 3583b9f3 by the
    chat's commit 02bdfa47 (21:35:57, rules 10-15 'Write less'), not by this card.
15. Hygiene: tasklist shows no LabVIEW; claudeDev holds only D1_ring_p6_20261012_212645.vi of this card (scratch_c169_p6_*, scratch_c169_post_*
    deleted, H4/H6); refs balanced in all 3 runs; no original opened (K2 pin 2a78e17c); no tools/hooks edit; STATUS/INDEX/plan untouched.
