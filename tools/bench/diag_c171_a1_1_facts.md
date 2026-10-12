# diag_c171_a1_1 facts (cards 171-a1-1 and its retry 171-a1-2, 2026-10-13)
## 171-a1-1 (FAIL at step 2.2, returned) - condensed
Step 0 re-hash: 17/19 equal; the 2 DIFF rows are the brief's swapped labels (disk replay_imaqdx_get_image_buf.vi = a89dafc1,
replay_get_buff_image.vi = 842ecad9 = docs/d1/ring-p6.md:313-315), not drift (`diag_c171_a1_1_hash.log`, `_hash_end.log`).
Name-taint patch db81a1d3 -> 8d25c12c (`diag_c171_a1_1_patch.diff`): plan-170 A2 UNVERIFIED (`_dry170.log:10,28`), but
selftest_c134_1_dry T1 ended first_fail=GATE PB, unverified 2 (`_st134.log:4`; record GATE FR, unverified 0). Reverted.
Pre-edit baselines (db81a1d3, --no-record): 78 FAIL A2 s3 (`_pre78.log:12`), 95 FAIL no graph for 5bef83f0 (`_pre95.log:8`),
110 FAIL A2 disp (`_pre110.log:12`), ring stage_d1_ring_p5s02c DRY PASS unverified 0 (`_pre_ring.log:62`).
## 171-a1-2 (retry) - step 1a diagnosis (`diag_c171_a1_2_which.py`, logs `diag_c171_a1_2_which_t1.log:160`, `_p170.log:10`)
T1 (reconstructed 133-3 bytes 8976588c): ONE gate name-tainted - FR (recipe :56-57, ok=False, statement taint False) reads
  `real`, bound at :45 `real = x.run(); s.gate("E1 ..", True)`; value list[5911] simulated graph rows, no Fake; the unit
  moved taint +21, all Fake uses (graph-after-mutation +0). FR UNVERIFIED -> not fatal -> run reached PB (the PB FAIL).
Plan 170: A2 (stage_replay_swap.py:40-41) reads `c0`, bound at :39 `c0 = L.census(path)`; value dict[0] (empty), taint
  +185, all Fake. Also A4 reads dd (:48, dict[0]), A5 reads E1 (:53, set[2426], +1 graph-after-mutation, ok=True), C2 cc (:74, dict[0]).
Separating criterion (both bound by Fake-touching statements, so "kind of touch" does not separate): the bound VALUE.
  c0 = empty container (what iterating/len() of a Fake yields); real = non-empty, Fake-free data from the dry's simulator.
## step 1b edit (`diag_c171_a1_2_patch.diff`, md5 f8f1fd95; +136/-0): db81a1d3 -> af6937e8
= the 171-a1-1 patch + `_stub_shaped(v)`: a name bound in a stub-touching unit is tainted only when its value is a Fake,
  holds a Fake (2 levels), is an EMPTY dict/list/tuple/set, or is no longer bound; scalars and non-empty Fake-free data are clean.
## step 2 results on af6937e8
2.1 plan 170 (recorded): `diag_c171_a1_2_dry170.log:10 UNVERIFIED A2 p6 BEFORE ...`; ends `:28 === DRY PASS-UNVERIFIED ...
    first_fail=None coverage 65/69, unverified 7`; no FAIL.
2.2 selftest_c134_1_dry 11/0 (`diag_c171_a1_2_st134.log:15`) = record; T1 `:4 first_fail=GATE FR ... coverage 45/80, unverified 0`
    identical to `selftest_c134_1_dry_c160_f3_1.log:4`. selftest_c171_a1_1_taint.py (2107d4e2) 9/0 (`selftest_c171_a1_1_taint.log`):
    U, S, ZA FAIL, ZC UNVERIFIED (plan-170 shape), ZB FAIL, ZD FAIL, ZT FAIL (T1 shape), ZF UNVERIFIED, ends GATE ZA.
2.3 (--no-record)  | post-edit                              | pre-edit baseline | stored record
    plan 78  | PASS-UNVERIFIED 14 (`_post78.log:45`) | FAIL A2 s3   | PASS unv 14 (`stage_replay_swap_110_dry78.log:45`), same 14 labels
    plan 95  | FAIL no graph 5bef83f0 (`_post95.log`) | same        | none stored
    plan 110 | PASS-UNVERIFIED 7 (`_post110.log:28`) | FAIL A2 disp | PASS unv 7 (`stage_replay_swap_110_dryc.log:28`), same 7 labels
    ring     | DRY PASS unv 0 (`_post_ring.log`)     | same         | FAIL PB (`prep_c163_a1_3_dry.log:56`); coverage 78/110 +1 line (recipe grew)
2.4 selftest_dry_c130_5 2/1 (`diag_c171_a1_2_c130_5.log:10`), record 3/0 (`selftest_dry_c130_5_c134_2.log:10`,
    `diag_c152_a2_1_regress_after.log`): FAIL T3 `:8` full run stage_d1_ring_p3a.py -> `DRY FAIL first_fail=GATE PB frame-keyed
    cdiff(S1, real end) == the P2b bed's 16 rows ... unverified 1`. NOT diagnosed (first unexpected result -> return):
    no pre-edit baseline of c130_5 was run, so whether the edit or an older change (vigraph a7eb58c7 / PD370(b), the
    same class as c134_1 T2's PB conversion) causes it is unknown.
## state left
stage_prerun.py REVERTED to db81a1d3 (Edit tool; `git diff --stat` empty); final patch kept in `diag_c171_a1_2_patch.diff`.
Newest plan-170 record = reverted checker: FAIL A2 (`diag_c171_a1_2_dry170_reverted.log:12`, dry_rule 3).
Not done (returned first): prior-art review, fp-103 drain. fp-102 untouched. No hook edit, no LabVIEW (tasklist 0), no VISA;
recipe fa94e80c, plans 78/95/110/170 unchanged; guard_write pin warning per edit (card 170-a2-5 pins db81a1d3; valid again).
