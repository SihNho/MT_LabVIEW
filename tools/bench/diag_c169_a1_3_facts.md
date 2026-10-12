---
card: 169-a1-3
status: current
date: 2026-10-12
---
# Facts 169-a1-3 - post-save reads of the SAVED P6-1 file PASS (DN gate fixed), Error List --role final 0 items, load_by_vi entry written

1. Hash before 8/0 (`diag_c169_a1_3_hash_before.log`): 22 inputs + 7 VI pins equal. requires PASS 2/0 (`cards/requires_169-a1-3.json`).
2. PATCH `diag_c169_a1_2_post.py` (now 49ce40cd; was 7cda957e): new `nodes_gone(base, other)` (:47-55) = non-Wire objects of base absent
   from other whose `owner` class is not the class of another absent object (#11267/#11270/#11273 carry owner "BuildArray" = #11261's
   class, graph_ring_p5s02e_20261012_173009.json). `# shortcut:` at :52-53 (owner is a class name, not a uid). Self-check (asserts, :59-65,
   before the load): one-row pair no difference -> [], one-row removed -> [1], 7815af09 vs 57f33e7c -> [11261]. Contract line :17-18, header :4.
3. Named `nodes_gone`, not `deleted_nodes`: the first prerun (`diag_c169_a1_3_post_prerun.log:53`) FAILED X10 "not read-only: source calls
   edit verb(s) ['deleted_nodes']" - stage_prerun.py:2192 X10_RO_EDIT_RE matches 'delete' in any call name. Logged fp-102; renamed (:47 comment).
4. Dry `py tools/stage_prerun.py --dry tools/bench/diag_c169_a1_2_post.py --graph tools/bench/graph_ring_p6_presave_20261012_212645.json`:
   "=== DRY PASS: first_fail=None coverage 54/87 lines, first mutation None, unverified 0" (`diag_c169_a1_3_post_dry3.log:40`).
   Prerun (same with --prerun): X10 peak 592.5 <= 680 (:55); "=== PRERUN PASS: 15 pass / 0 fail; first None" (`diag_c169_a1_3_post_prerun3.log:59`).
   dry3/prerun3 repeat dry2/prerun2 because the launch gate read the run1 copy as a newer failing log ("records invalid - pre-run it again").
5. Old log kept: `diag_c169_a1_2_post_run1.log` 0512f85f == card pin (`diag_c169_a1_3_keep.log:3-4`, shutil.copyfile, no overwrite).
   bgrun APPENDS (bgrun.py:104): the new run is the second section of `diag_c169_a1_2_post.log` (:346-687), file now 55ee2038.
6. POST-SAVE RUN (`diag_c169_a1_2_post.log`, rc 0, 172 s, "GATES: 16 pass / 0 fail" :687) on byte copy scratch_c169_post_20261012_214915.vi
   (K3 identical :367; deleted H4 :674): MEM after load 603.7 MB (:373); ExecState on reload 1 (:374, ES PASS :655); DN [11261] PASS (:656-657);
   E5 ok, deleted_wires_present [] deleted_nodes_present [] uid_reused 0 (:658-659); G1 PASS (:660); FS1 23 FS PASS (:661);
   graph graph_ring_p6_20261012_212645.json fbc7b7ee = the old md5 (deterministic read), 6221 rows / 10830 objs / 2066 Wire (:662);
   S-5 30 vs 30, only-saved [] only-57f33e7c [] PASS (:663); MEM 603.7/615.1, peak 615.1 <= 675 (:665-666); saved md5 c2d9c13c unchanged (:667, H2 :675).
   Refs 5/5 (H5 :672); H6 nothing left / removed (:683); LabVIEW gone at exit.
7. ERROR LIST (`diag_c169_a1_3_errorlist.log`, rc 0, 63 s, RESULT 11/0): `errorlist_check.py --vi <saved> --role final` on scratch
   _elc_D1_ring_p6_20261012_212645_20261012_215225.vi (identical, deleted); "0 errors and warnings", items 0 / window N 0, extra 0 / missing 0,
   verdict OK (:35-37). Read: errorlist_D1_ring_p6_20261012_212645_20261012_215225.json af552310 (bed_md5_after c2d9c13c :279, refs 4/4 :281-286).
   Kept as `errorlist_expected_D1_ring_p6_20261012_212645.json` 5e2a4e6f: total 0, class counts {}, expected []; base f71773bc (0 items).
8. load_by_vi: `memory_model.json` +1 entry c2d9c13cb40c0a5cab7433896d1df157 = 603.7, cite diag_c169_a1_2_post.log:373; file d12bcd3b -> 8b4a9b48.
9. Hash after (`diag_c169_a1_3_hash_after.log`) 7/1: 7 VI pins equal; inputs 21/22 - the ONE drift is diag_c169_a1_2_post.log 0512f85f -> 55ee2038,
   the log step 3 ordered this card to run into (its old bytes are run1, item 5). docs/script-writing.md 3583b9f3 unchanged; graph fbc7b7ee unchanged.
10. Hygiene: claudeDev holds only D1_ring_p6_20261012_212645.vi of this cycle (glob *_20261012_2*.vi); scratch_c169_post_* and _elc_* deleted;
    tasklist shows no LabVIEW; no original opened (K2 2a78e17c :360); no recipe / tools/hooks / STATUS / INDEX / plan edit.
11. Jev: `diag_c169_a1_3_post_prerun.log | X10 fp (fp-102) | - | renamed the function, re-ran dry/prerun | PASS`;
    `diag_c169_a1_3_hash_after.log | new-problem p=0.916 (jev_gate.log:7509) | hypothesis review owed | card has peers []: not dispatched;
    `gate_fp.py log` for it refused 4x by guard_peer (JEV-BUDGET, 21:54-21:56); result file validated OK | open`.

skipped: no owner-uid route for nodes_gone (graph objs carry only the owner class; shortcut noted in place); no separate selftest file
(the asserts run with the script); no extra option or flag.
