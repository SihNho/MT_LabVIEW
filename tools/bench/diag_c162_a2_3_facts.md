# diag_c162_a2_3_facts - card 162-a2-3 (offline, no LabVIEW) - status PASS
## 1. Copies (prep_c162_a2_3_copies.py -> prep_c162_a2_3_copies.log f9abe972, 6/0) - 15 copies, 14 files
- L licence rename table: 8 - c150_a3_1, c150_a3_6, c152_b2_1, c154_a3_2b, c155_a2_1, c155_a4_1, c160_c3_1 ARGUMENT-ONLY (the `why` text,
  one-line vs two-line `own, wr`); c156_a1_1 = the reference.
- P pred E1 table: 5 - c154_a3_2b, c155_a2_1, c155_a4_1, c156_a1_1 IDENTICAL (byte); c160_c3_1 DIFFERS: + `ids` field (-> optional argument).
- S stub-delete insertion: 2 - selftest_c160_regface (reference); prep_c160_b3_1_mk DIFFERS: same loop also rewrites the FRESH_IDS `why`
  (-> pre-map list comprehension + the shared call; proven equal, EQS below).
## 2. Module tools/stage_shared.py (new, b688edd4, labview none, imports only collections)
base_sink_renames(actions, base_terms, why_fmt) -> (ren, own, wr); checkpoint_step_table(ops, cps, sfn, actions=None) -> cpe;
insert_stub_deletes(actions, wire_by_id, why) -> new list. Not in stagekit/stagexec/stagesim/stage_prerun (brief step 2).
## 3. Equivalence BEFORE any rewrite (prep_c162_a2_3_equiv.py 0f5e86cc -> prep_c162_a2_3_equiv.log, 17/0; record prep_c162_a2_3_equiv.json e9625618)
Old block text exec'd from each caller's listed lines on that caller's real inputs vs the new function: 15/15 EQ (JSON), + EQS mk pre-map 1/1.
INFO (non-gating) all 15 also equal the stored outputs: 8 licence `renames`, 5 pred e1.checkpoints, plan_ring_p5s02b_in2.json actions.
## 4. Callers rewritten (Edit tool; md5 old -> new)
licence: c150_a3_1 da47cb38->999a55b3, c150_a3_6 efe26399->5a2ed76e, c152_b2_1 1a10fce5->e0e5385b, c154_a3_2b 0c045f1e->93fa45f6,
c155_a2_1 d286d438->69abfba9, c155_a4_1 8a35a601->c93963b7, c156_a1_1 43e40d7b->42812bdc, c160_c3_1 409e4c77->a4e46195.
pred: c154_a3_2b ff8ff19d->81132194, c155_a2_1 20726b40->81ad3bfd, c155_a4_1 9c587c75->98bd94f4, c156_a1_1 27fc52dc->cb43de5c, c160_c3_1 b5d596dc->89930da2.
prep_c160_b3_1_mk eff9188f->a08aadf5; selftest_c160_regface 679e901c->79fa33c9: 12/0 -> 12/0 (selftest_c160_regface_c162_a2_3_before/after.log), temp plan 73971108 both.
The prep writers were NOT re-run (each rewrites its licence / pred / plan json); grep found no selftest_c15*/c16* naming them.
## 5. selftest_c162_stage_shared.py (949c363a, 77 lines) -> selftest_c162_stage_shared_final.log 47/0
R 15 replays == recorded old output; A 15 callers call SH.<fn> once with the recorded argument, block line gone; C 15 compile; M module scope.
(selftest_c162_stage_shared.log holds a first 42/5 run: the self-test compared JSON text with int vs str keys; fixed to parsed compare.)
## 6. Pin re-sweep (prep_c162_a2_1_pinsweep.py -> prep_c162_a2_3_pinsweep.log, 5/0): TARGET 14, equal 13, stale 1 =
selftest_c159_a4_1.py:300 stagexec 7a712ccb (pre-existing, diag_c162_a2_1_facts.md:5) - NO new stale pin from these edits; nothing re-pinned.
## 7. Frozen files (prep_c162_a2_3_frozen.py): 489 files (plan_*/errorlist_expected_* json, 4 stage tools, recipes, hooks) before == after, 0 differ
(prep_c162_a2_3_frozen_before.json 6a574517; _before.log F0, _after.log F1 PASS).
## OPEN
- OPEN: md5 pins of edited prep scripts in 7 historical check scripts outside the sweep go stale: prep_c150_a3_5_check.py:52, prep_c150_a3_6_check.py:63
  (c150_a3_1 da47cb38); prep_c151_a3_2_check.py:48, prep_c152_a2_2_check.py:49, prep_c152_b2_1_check.py:52 (c150_a3_6 efe26399); prep_c155_a4_1_inv.py:32
  (c155_a2_1 pred/licence); prep_c156_a1_1_inv.py:37-38 (c155_a4_1 pred/licence). Not re-pinned (records of past checks).
- OPEN: docs/script-writing.md rule 4 says old scripts that ran stay as the record; brief step 4 said rewrite every copy - the brief was followed.
