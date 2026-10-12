---
type: facts
status: current
date: 2026-10-12
card: 166-a1-3
---
# 166-a1-3 facts (offline, no LabVIEW): adoption EL step judged by stagekit.el_advisory; EL predictor in tools/elpredict.py with rules 1 + 2; step-5 replay 47 / missing 0 / extra 0
## Part 1 - adoption step (PD403(d)(1))
- `tools/errorlist_check.py` (2b466a89 -> bfa0a387): main()'s verdict block (old :641-661) moved VERBATIM into `final_verdict` (:699), called at :641; lines before :641 unchanged.
- `final_verdict`: the old loose-end / by-design rules run first, then `advisory_inputs` (:673) looks for a PREDICTED step-end expected file (plan key) whose `<plan>_pred.json` is keyed to that plan md5 AND names this file (path + md5) as `errorlist.item_file`. Found -> `stagekit.el_advisory` prints EL-ADVISORY and its rc decides (0 OK / 1 MISMATCH); the by-design verdict goes to `R['verdict_by_design']` and is printed as RECORDED. Not found, or advisory rc 2 -> the old verdict, unchanged.
- `rejudge_read` (:745): replays a stored --role final read through compare + final_verdict offline (record=False writes nothing). The cycle-165 caller is `tools/bench/diag_c149_a1_2_elrun.py` (runs errorlist_check as __main__, unchanged); cycle_runner's `reverdict` (compare only) is not touched.
- Self-test `selftest_c166_eladv.py` (0ba14f93) -> `selftest_c166_eladv.log:97` `RESULT ... PASS 11/0`:
  A el_advisory(stored 47-item read 0c0664d8) rc 0 RECORDED, total diff -2, unseen [] (:58-59 of the last run); A2 advisory_inputs finds the pred from the literal relative `--expected` path;
  B planted 'Feedback Node: Initializer terminal is not wired' (class in neither start read nor prediction) rc 1, B2 through rejudge_read MISMATCH rc 1;
  C rejudge_read(stored read) -> `EL-ADVISORY DECIDES (PD403(d)(1)): step verdict OK (rc 0); by-design verdict MISMATCH RECORDED` (:71-72), where the literal log had `ERRORLIST-VERDICT: MISMATCH` / `BGRUN END rc=1` (diag_c165_a3_4_el.log:85-86);
  D stricter-only: diff -6 and +4 -> rc 1 both direct and via rejudge_read, +1 -> rc 0; E expected file without plan -> MISMATCH rc 1 == stored verdict, no advisory; E2 a byte copy at another path -> not applied, MISMATCH rc 1; F stored files unchanged.
- First run of the self-test died on `os.path.relpath` across drives (%TEMP% on C:, repo on G:) - fixed in advisory_inputs (another drive = not the pred's item file) before the passing run (same log, earlier block).
## Part 2 - predictor (PD403(d)(2))
- New shared module `tools/elpredict.py` (d2d7de21), not elrule.py: elrule.py's md5 is written into every predicted file (`elrule.module_md5`), so editing it would change every replay. `predict` (:106) = `prep_c164_a2_3_lib.el` (:118-235) + rule 1 `clears_by_in_plan` (:67) + rule 2 `tunnel_links` (:85, OuterTerminal of a cleared undirected tunnel on the row's wire in the BASE graph). Old prep scripts untouched.
- Self-test `py tools/elpredict.py --selftest` -> `diag_c166_a1_3_elpredict_selftest.log:145` `RESULT PASS 5/0`: C tunnel_links on graph 2a5fa0c4 = {4: #5204 t9631, 49: #10404 t24363}; D step-5 replay total 47; E rule 2 alone (rule 1 disabled on items 4/49 in a %TEMP% copy) total 47 again (:144).
- REPLAY (`diag_c166_a1_3_replay.py` 64129d55, log `diag_c166_a1_3_replay.log:427` `RESULT PASS 7/0`), outputs only under `tools/bench/diag_c166_a1_3_replay/`:
  - step 5 (inputs of prep_c165_a3_3_el.py, = elpredict.STEP5_CFG): total 49 -> **47**; compare(read 0c0664d8 47 items, re-made entries) **extra 0 missing 0** (:415). Re-made 1a67aeba.
  - differing items (:411-412): item 4 uid 4337 nosource STANDING -> CLEARED by A73 w_k3f; item 49 uid 9636 whilesubvi STANDING -> CLEARED by A84 w_k4f (rule 1; rule 2 links both too). Total moves TOWARD the adopted read (47).
  - P5 final expected file from card 166-a1-2 exists: `errorlist_expected_D1_ring_p5_20261010_172913.json` (c94be128, total 47): its 46 entries == re-made 46 by item, its dropped items [4, 49] == the items the new rules clear (:418).
  - step 4 (p5s02d, prep_c164_a3_6_el.py inputs): **byte-equal** 2c1edf78 (:385).
  - step 3 (p5s02c, prep_c163_a1_3_el.py inline flow) and step 2 (p5s02b, prep_c160_c3_1_el.py MERGE flow): bytes differ (format keys only: kind, bed_note, stale_step3/stale_changed, counts, cleared labels), entry item sets EQUAL, totals equal 53 / 51 (:334, :358). p5s02b items 3/5 (MERGE rows) are now cleared by rule 1 (clears_by w_gl / w_hl in plan) instead of the session MERGE table.
  - p5s01a / p5s01b / p5s02a: their preds carry `errorlist.item_file` None (totals 48 / 47 / 47 only) - no stored item-wise prediction exists to re-make (log, last FACT lines).
- No stored predicted file, read or pred changed (replay U gate, :422).
## Checks
- Hashes `diag_c166_a1_3_hash_before.log:12` / `_after.log:12` PASS 8/0: card inputs equal (after: errorlist_check.py excluded, the edited file), 7 VIs 75773b0d 7f2582ae eb1d0f31 94ffff94 f9ae7751 564d8cbe 6dcd5c3d unchanged; no LabVIEW process (tasklist 0).
- stagekit / stagexec / stagesim NOT touched -> stored-plan compile/dry checks not required by the brief; elrule.py not touched. No tools/hooks edit.
- `tools/lint.py --files shared` total 0 (diag_c166_a1_3_lint.log:5). `tools/dupcheck.py`: one 2 x 54-line pair = prep_c164_a2_3_lib.py:152-228 `el` vs elpredict.py:168-244 `predict` (diag_c166_a1_3_dupcheck.log:12) - the lib is the record (not rewritten); new makers call elpredict.predict.
- `docs/fn_descriptions.json` errorlist_check.main line updated (verdict now via final_verdict).
