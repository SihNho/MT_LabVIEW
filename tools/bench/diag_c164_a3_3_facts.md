---
card: 164-3-3
date: 2026-10-10
status: current
---
# 164-3-3 facts (offline, read-only; no LabVIEW) - `diag_c164_a3_3_dw.log` PASS 21/0 (:260, BGRUN END rc=0 :261)
Script `tools/bench/diag_c164_a3_3_dw.py` calls stagesim.wire_rows / md5_file / _j (`tools/stagesim.py:215-225,617-618`); "Wire object" =
uid in `objs` with class Wire (same expression as stagesim.py:625,637; no shared function for it). Sim end = each plan's `finalized.last_step`.
Real graphs (log :5-18, all "byte copy of the ... adopted file" except p4s01 = "session-1 in-between file" :5): p4s01 f697a0b2, p4s02 eda9db40,
p4s03 5638469b, p4s04 094ba298, p4s05 cbeeadf5, p4s06 a3ecb92b, p4s07 71935a84, p4s08 44858dbf, p4s09 22f967b5, p5s01 6716c499, p5s01a bd67a511,
p5s02a 7ac24924, p5s02b 431cfd83, p5s02c 3d5196ab. Plans scanned: p4_s01, s02, s02v18, s03v18..s09v18, p5s01, s01a, s01b, s02a, s02b, s02c, s02d
(docs/d1/ring-p4.md names only drafts v2..v15 + s01/s02; the later P4 plans were taken from the graph chain). 0 delete_wire in p4 s03/s04/s05/s09,
p5s01/s01a/s01b/s02a/s02c (log :72-76,157-165,219). p4_s02 and p4_s02v18 hold the same 5 delete_wire (:28-70); real-after for both = p4s02.

| stage | wire (action, plan:line) | sim rows | sim object | real-after graph object | real-after rows |
|---|---|---|---|---|---|
| p4 s01 | w28296 (p4_rp27928_dwo, plan_ring_p4_s01.json:137) | 0 | Y (:22) | N in p4s01 f697a0b2 and every graph (:23) | 0 |
| p4 s01 | w29144 (p4_rp28916_dwo, :242) | 0 | Y (:25) | N, every graph (:26) | 0 |
| p4 s02 | w29168 (p4_rp29048_dwo, plan_ring_p4_s02.json:77 / s02v18:72) | 0 | Y (:30,:52) | N in p4s02 eda9db40 (:32) | 0 |
| p4 s02 | w29391 (p4_rp29265_dwo, :185 / :180) | 0 | Y (:34,:56) | N in p4s02 (:36) | 0 |
| p4 s02 | w29397 (p4_rp29316_dwo, :290 / :285) | 0 | Y (:38,:60) | N in p4s02 (:40) | 0 |
| p4 s02 | w23310 (p4_dw_23310, :330 / :325) | 0 | Y (:42,:64) | N in p4s02 (:44) | 0 |
| p4 s02 | w23255 (p4_dw_23255, :336 / :331) | 0 | Y (:46,:68) | N in p4s02 (:48) | 0 |
| p4 s06 | w23807 (p4_rbA_dw, plan_ring_p4_s06v18.json:359) | 0 | Y (:80) | **Y** in p4s06 a3ecb92b (:86) | **3** (t10975, t5171 src, t3173; was 6 in p4s05 :85) |
| p4 s07 | w25283 (p4_rbB_dw, plan_ring_p4_s07v18.json:200) | 0 | Y (:99) | N in p4s07 71935a84 (:106) | 0 |
| p4 s07 | w25348 (p4_rbC_dw, :304) | 0 | Y (:108) | N in p4s07 (:115) | 0 |
| p4 s07 | w25386 (p4_rbD_dw, :385) | 0 | Y (:117) | N in p4s07 (:124) | 0 |
| p4 s07 | w25638 (p4_rbE_dw, :476) | 0 | Y (:126) | N in p4s07 (:133) | 0 |
| p4 s08 | w25645 (p4_rbF_dw, plan_ring_p4_s08v18.json:164) | 0 | Y (:137) | N in p4s08 44858dbf (:145) | 0 |
| p4 s08 | w25415 (p4_rbR_dw, :245) | 0 | Y (:147) | N in p4s08 (:155) | 0 |
| p5 s02b | w10394 (dw_a13, plan_ring_p5s02b.json:137) | 0 | **N** (:170) | N in p5s02b 431cfd83 (:183) | 0 |
| p5 s02b | w24264 (dw_go, :207) | 0 | **N** (:186) | **Y** in p5s02b (:199) | **2** (t31639 src #31593, t24139 #24083) |
| p5 s02b | w24300 (dw_ho, :292) | 0 | **N** (:204) | N in p5s02b (:217) | 0 |
| p5 s02d (new) | w23489 (dw_cond, plan_ring_p5s02d.json:137) | 0 | Y (:224) | no graph after (base 3d5196ab: Y, 3 rows :223) | - |
| p5 s02d (new) | w23460 (dw_23460, :143) | 0 | Y (:242) | no graph after (base 3d5196ab: Y, 3 rows :241) | - |

Sim drops the object only for the 3 p5s02b wires: base p5s02a w10394 0 rows+object (:169), w24264 / w24300 1 sink each (:185,:203) = termless / sourceless (stagesim.py:1440-1442,1461-1463); all others had a source row in the base and keep the object at sim end.
Real-after: 15 of 17 deleted wires absent (object and rows); 2 keep the uid: w23807 (3 of 6 rows, p4s06), w24264 (new source t31639, p5s02b). md5 plan 725cd68e / r_in 9dadb0c1 before (:3-4) and after (:258-259).
OPEN: w23489 / w23460 (plan p5s02d): no real graph after the stage exists - real object/rows not measurable until P5-2d is run and read.
OPEN: p4 s01 real-after graph p4s01 is an "in-between file" read (:5), not an adopted-file read; w28296/w29144 are absent from all 14 graphs read.
