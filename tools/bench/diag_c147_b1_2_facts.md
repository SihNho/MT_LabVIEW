---
type: facts
status: current
date: 2026-10-08
card: 147-b1-2
---
# Card 147-b1-2: stagekit D / TD / PB under PD356(b) - built, offline self-test 17/0
stagekit.py 9a3fceaf -> **06b8d844284deacab535a9ee442d4964**. Self-test `tools/bench/selftest_c147_b1_2.py` (24c56042), log `selftest_c147_b1_2.log` rc 0, RESULT 17/0.

## Diff (tools/stagekit.py)
- :1374 `term_identity_gates(base, sim, real, renames=None, bind=None)`; :1386-1387 either keyword not None -> `term_identity_356`; else the old body, unchanged.
- :1403-1411 comment; :1412 `licence_renames(lic)` -> {(uid, owner): (from, to)} from a pb-licence/1 `renames` list, None if the key is absent.
- :1432 `rename_check` (base terminals kept by sim and real, key (uid, owner), sim name vs real name; unlicensed = not listed or other from/to).
- :1450 `wire_keys_356` (source name '*' for a licensed (uid, owner)); :1464 `_ends` (wire -> sorted sources/sinks, sim uids mapped through bind).
- :1476 `term_identity_356`: TD on (uid, owner) + no unlicensed rename; D: plan-deleted wire uid present at end = REUSE-NOTED if sources+sinks == a sim
  wire and no sim-removed sink on it (counted +1 new/+1 lost when wire_keys saw it kept), else REUSE-BAD -> D fails. Adds renames, unlicensed_renames, reuse_noted, reuse_bad, d_new, d_lost.
- :1522 `pb_rename_rows(base, sim, real, renames)` -> (rows with the sim name back for licensed renames, restored, unlicensed); renames None -> (real, [], []).

## Licence shape chosen (next card writes it; this card did not)
`"renames": [{"node": 2626, "term_uids": [2832,4160,4165], "from": "array", "to": "element"}, {"node": 9503, "term_uids": [9505,9508], "from": "Value", "to": ""}]`
beside the existing `rename_by_uid` (keep it: stage_prerun.pb_licences reads only rename_by_uid, tools/stage_prerun.py:1276). from/to optional (None = any name).

## Call sites (s06 recipe pair) and what the next card must pass
- tools/recipes/stage_d1_ring_p4_s06v18.py:127 `K.term_identity_gates(BASE["terminals"], L["terminals"], real)` -> add `renames=K.licence_renames(<licence json>),
  bind={"term": x.bind["term"], "obj": x.bind["obj"]}` (x.bind["term"] maps sim -> real term uid, as used at :70). D gate :128-129, TD gate :131-133 read the same keys.
- :139 `V.build4(real, ...)` for PB -> build on `rows` from `K.pb_rename_rows(BASE["terminals"], L["terminals"], real, renames)`; PB gate :142-144 should AND `not unlicensed`.
- stage_d1_ring_p4_s06v18_scratch.py has no own call: it imports the recipe (:29) and returns `R.body(s)`.

## Self-tests (selftest_c147_b1_2.log)
- T0 s06 default call == verbatim pre-edit code == stored run verdict (D 15/16, 7/8; TD lost 5) :5; T0b today's licence file -> None :6. R1 6030 rows bind :7.
- T1 L5: D new 16==16, lost 8==8, reuse_noted [23807] :8; TD lost []==gone [], 5 renames, unlicensed [] :9; PB cdiff == pred 18 rows, unlicensed [] :10.
- T2 L3 (2832/4160/4165 only): TD FAIL, unlicensed (9505,9503),(9508,9503) 'Value'->'' :11; D PASS, PB FAIL (unlicensed, cdiff equal) :12.
- T3 w23807 + sink 9519: D FAIL, reuse_bad 23807 :13. T4 2832 owner 2626->9503: TD FAIL :15. T4b 2832 'array'->'index': TD FAIL :16.
- T5 s03 / s04 / s05 (diag_c143_p4s03v18_scratch.json, diag_c144_p4s04v18_scratch.json, diag_c145_p4s05v18_scratch.json; each names its adopted md5
  282301ca / 95e408ff / 3f9ac26b): default == pre-edit == stored verdict (9/9 1/1; 9/9 0/0; 11/11 1/1) :17,:19,:21; new rules + empty licence also PASS (info) :18,:20,:22.
- T6: selftest_rebind_c142_5 4/0 before and after (diag_c147_b1_2_t6_rebind_before/after.log); selftest_d4_l2b2a 19/0 before and after (diag_c147_b1_2_t6_d4_*.log);
  F1/F2 of selftest_stagekit (no % formatting, no bold-FAIL) PASS :23-24. selftest_stagekit.py and selftest_td_key_c141_3.py NOT RUN: guard_bash refuses
  them under this labview-none card (their migrated header says labview: read, selftest_stagekit.py:376 / selftest_td_key_c141_3.py:113) - logged fp-55.

## Pins after (selftest :3 before, :25 after == before)
stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, memory_model 88eeb037, plan cfbd9823, pred c4a6a35a, licence 7dce79aa, plan_in db72d8af,
recipe 9150f15b, scratch recipe 31009bfc. No LabVIEW (tasklist count 0).
OPEN: selftest_stagekit / selftest_td_key need a run under a labview-read card (or fp-55 resolved); whether PB should fail on an unlicensed rename that leaves cdiff equal (implemented: yes).
