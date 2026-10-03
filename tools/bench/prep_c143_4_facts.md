---
type: facts
status: current
date: 2026-10-03
---
# Card 143-4 facts: rebase uid-reuse FIXED (PD334(b)); s03 rebase now passes the UID-REUSE step and STOPS on the next check (named terminal -20.'value') = RETURN

OFFLINE only; no LabVIEW, nothing launched. Card inputs md5-checked (all 8 match). stagexec.py / stagekit.py unchanged.

## Step 1 - census: raw-uid comparisons of TWO graphs (stagexec.py 7e1f7cc5, stagekit.py, stage_prerun.py before the fix 5f0dd8fc)
Line numbers are the CURRENT file (stage_prerun.py 03cdd8c6 after the fix).

| site | two graphs | delete between? | keyed by (uid, owner, name)? | on rebase path | action |
|---|---|---|---|---|---|
| stage_prerun.py:3483 rebind -> stagexec.uid_reuse | N's base vs real end of N | YES (N's planned deletes) | no (raw) | yes | **FIXED** (fatal only when the plan names the uid; else REUSE-NOTED) |
| stage_prerun.py:3502-3508 rebind old_t / real_new | same | yes | YES (tkey, PD330(d)) | yes | none (already identity) |
| stage_prerun.py:3510 info['recycled'] | same | yes | raw on purpose (info only) | yes | none |
| stage_prerun.py:3531-3536 real_new_t / T pre-existing | prov vs real | yes | derived from identity real_new | yes | none |
| stage_prerun.py:3532 new_rf (frame_diagram sets) | N's base vs real | yes | no (raw) | yes | **FIXED** (+ frames whose obj (class, owner) changed) |
| stage_prerun.py:3640 rebind (D) new FS frames `bo` | N's base doc objs vs real doc objs | yes | no (raw) | yes | **FIXED** (_obj_id (uid, class, owner)) |
| stage_prerun.py:3749 carry_fs new FlatSequence `bo` | same | yes | no (raw) | yes | **FIXED** (_obj_id) |
| stage_prerun.py:3909 rebase `known` (plan positive uids in real) | plan/prov vs real | yes | no (raw) | yes | covered: a named re-issued uid now refuses earlier (rebind) |
| stagexec.py:872-888 compare | sim (translated) vs real at one checkpoint | no (same point) | raw after bind | no | listed |
| stagexec.py:942 uid_reuse (bind_new :970) | prev_real vs real, ONE op | no | raw | no (execution) | unchanged (card rule) |
| stagexec.py:984 bind_new old_t | one op | no | raw | no | listed |
| stagexec.py:1068 tunnel_name_check | one op | no | raw | no | listed |
| stagexec.py:1138 bind_fs_tunnel, :1178 bind_case_faces | one op | no | raw | no | listed |
| stagexec.py:2463-2471 delete_wire, :2479 delete_object missing_ok | sim prev vs live, same point | no | raw | no | listed |
| stagexec.py:4008-4016 w0_wires (Part-B W0 from base) | plan base vs live after Part A | yes | raw wire uids | no | listed |
| stagexec.py:4038 retire_ends | base rows vs read after deletes | YES | raw term/wire uid | no | listed |
| stagexec.py:4264 e3_eval (computation_diff S1 vs end) | S1 vs end graph | yes | raw node uids | no | listed |
| stagexec.py:4369 canon_diff base_nodes | two real reads | possible | raw for base nodes | no | listed |
| stagekit.py:1324 term_identity_gates (TD/unwired/D) | base vs sim vs real | yes | YES (term_key, PD325(b)) | no | none |

## Step 2 - fix (tools/stage_prerun.py, md5 5f0dd8fc -> 03cdd8c6)
- New `_obj_id` (:3438), `plan_named_uids` (:3445: positive ints in actions / open_rows / bindings, over-inclusive), `_reuse_uid` (:3456).
- `rebind(..., named=None)` (:3461): `named is None` (direct call) = old behaviour; with `named`: uid_reuse hits refuse only when named,
  else `info['reuse_noted']`; a terminal uid whose OWNER changed AND is named also refuses (28004 type). `rebase` passes
  `named=plan_named_uids(plan)` and logs `REUSE-NOTED <uid> <old>-><new>` (:3861-3863).

## Step 3 - self-tests
- `selftest_rebase_uidreuse_c143_4.log`: **5/1**. U2 (plan naming 23276 -> refused) PASS, U3 (named 28004 owner-moved -> refused;
  own named set binds) PASS, U4 (rasrest 28004/28979 bind, rebase PASS) PASS, U5 (direct rebind still refuses) PASS, U6 PASS.
  **U1 FAIL**: `REUSE-NOTED 23276 ('ParameterTerminal', 'Comparison')->('Terminal', 'Local')` logged, the UID-REUSE refusal is gone,
  then `REBASE REFUSED: plan-referenced terminal #-20.'value' does not bind uniquely (0 sim row(s), by unbound, real name None x0)`
  (stage_prerun.py:3904).
- Fact (prep_c143_4_probe2.log): provisional base `sim/ring_p4_s03v18_s02end/base_provisional.json` holds ONE row on Local -20:
  term -21 named 'StopAll' (source, unwired); s03 action `p4_w_stop12` src = {uid -20, term 'value'}.
- Old self-tests: selftest_rebind_c142_5 4/0, selftest_rebind_c132_5 7/0, selftest_rebase_c132_6 8/0, selftest_rebase_c133_3 5/0,
  c125_1_offline_measure 6/0 (logs `*_c143_4.log`).

## Step 4 - NOT done (depends on the rebase)
s03 rebase, X10 at 596.0, EL prediction (prep_c143_3_pred.py), dry/prerun on both s03v18 recipes, --scratch-required exit code.
Unchanged: plan_ring_p4_s03v18.json 9d5049d8 (PROVISIONAL), plan_ring_p4_s03v18_pred.json e2e69c04.
