---
type: facts
status: current
date: 2026-10-03
---
# Card 142-5 facts: rebind key fix + P4 v18 session 2 plan (offline, no LabVIEW)

## (1) Rebind key - `tools/stage_prerun.py` md5 5f0dd8fc
- Offline owner check (`prep_c142_5_probe.log`): s01 BEFORE graph (P3b-2b 50595c62) has 28004 = #27928 'output array', 28979 =
  #28916 'output array' (both GrowableFunction); the REAL s01 graph has 28004 = #6942 'array', 28979 = #6805 'new element/subarray'.
  Same owner/term classes, so `stagexec.uid_reuse` does not flag them; the old raw-uid `old_t` filed them as old -> the shape refusal.
- Fix (`stage_prerun.py:3456-3471,3492-3493,3817`): `old_t` keyed by (term uid, owner uid, name); a pre-existing self-binding (T) is
  never given to a re-issued uid; REBIND log line now lists `re-issued uid(s)`. `uid_reuse` stays in front (K4).
- Self-test `selftest_rebind_c142_5.py`: BEFORE the fix 1/3 (`selftest_rebind_c142_5_before.log:3-8`, the 142-P1 refusal reproduced);
  AFTER 4/0 (`selftest_rebind_c142_5.log`): nodes -1->29407, -7->6942, -13->6805; re-issued [28004, 28979]; rebase(no-sim) of a
  rasrest copy PASS, 17 uids bound.
- Old self-tests: `selftest_rebind_c132_5` 7/0 and `selftest_rebase_c132_6` 8/0 (`*_c142_5b.log`) after a 3-line input fallback
  (plan_ring_p3b2.json was rebased in 133-3 and has no `sim_of`; both now read `plan_ring_p3b2_in.json`, the same 39 actions per
  selftest_rebase_c133_3 T4) - their first reruns (`*_c142_5.log`) died on that KeyError, as their c133_3 runs did on 10-02.
  `selftest_rebase_c133_3` 5/0, `c125_1_offline_measure` 6/0 (`*_c142_5.log`).

## (2) P4 v18 session 2 - `plan_ring_p4_s02v18.json` e941ebbf (provisional a797f577 -> rebased)
- Maker `prep_c142_5_mk.py` 10/0 (`prep_c142_5_mk.log`): v18 ops 1..24 == s01's 24 ids; cut = op 58 (ops 25..58, 34 actions,
  `p4_rp29048_dwo`..`p4_lr_stop12`), peak 678.5 <= 680 at 596.5; op 59 would be 682.4. Actions #25..#50 == rasrest_in's 26.
  One cross ref (p4_rp29048_out -> provisional -13). 16 end rows all tied; 11 open pairs; FINAL provisional.
- `--rebase` (`prep_c142_5_rebase.log`): REBIND 3 nodes, terminals conn 11 / pos 1, re-issued [28004, 28979]; 17 uids bound;
  base -> `sim/ring_p4_s02v18_base_real_fsmap.json` 830fa6c7; completeness PASS; re-sim final=True.
- Pred `prep_c142_5_pred.py` 6/0 -> `plan_ring_p4_s02v18_pred.json` 518b01b8: 34 ops (delete_wire 5, delete_object 4, RLE 9,
  connect 10, create 6), X10 678.5 at 596.5, X17 PASS. **Census: derived {} - all 34 actions census-UNPREDICTED** (CEN2 compares
  an empty class set). **Error List: predicted 51** (no created node with an unwired input), **alternative 52** (base node #23166
  newly unwired, term '').
- Dry `prep_c142_5_dry.log` PASS (L0, L1, E1 34 ops, FR, D 4/5, TD, PB 16 rows); prerun `prep_c142_5_prerun.log` 16/0 (prerun's own
  X10 657.1; X14 WARN rows 34 budget 15, proven: no). Scratch recipe dry `prep_c142_5_scr_dry.log` PASS, prerun 16/0.
- `--scratch-required`: exit **3** SCRATCH-REQUIRED (CENSUS-UNPREDICTED rows 1..34) (`prep_c142_5_scrreq.log:3`). The plain form was
  refused by guard_cycle (no prior-art review newer than the recipe) - logged gate-fp **fp-37**; run in the accepted
  `--prerun ... --scratch-required ...` form.
- Recipes WRITTEN, not launched: `tools/recipes/stage_d1_ring_p4_s02v18.py` (copy of the s01 recipe, identity-keyed D/TD) and
  `_scratch.py` (copy of s01's scratch; MEML 675 -> 680 per PD331(c)). Prior-art review for them: not dispatched (not in card peers).
