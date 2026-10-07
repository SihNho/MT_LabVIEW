---
type: brief
status: current
date: 2026-10-07
---
# Brief 146-a1-2 — s05 RE-CUT under ONE X10 start rule (+ load record, + #2626 licence if needed) — offline, ALONE

Decided by `docs/d1/ring-p4b.md` PD352(b)(d) (lines 280-299): ONE X10 start rule = the gate tool's own `x10_start`
(`tools/stage_prerun.py:2043-2052`, `memory_model.json:69`) = MEASURED fresh load + the op-0 read. s04's adopted file
`claudeDev\D1_ring_p4s04_20261007_215031.vi` 95e408ff has fresh load **605.4 MB** (`diag_c145_a2_1_facts.md`).
The 145-a2-6 result: s05 = v18 ops 98..124 (33 actions / 27 ops) on the real s04 graph 094ba298, X10 peak 685.4 vs 680 at 605.4,
first op over 680 = 121, longest cut <= 680 = op 120 (679.8) under the PREDICTION script's start; the review
`archive/peer/2026-10-07-c145-s05-x10.md` says the gate's own start may make that op 120 cut fail too (about op 116).
Facts: `tools/bench/diag_c145_a2_6_facts.md`, `tools/bench/diag_c145_a2_x_facts.md`. Previous maker: `tools/bench/prep_c145_a2_6_mk.py`.

## Do
1. **Record the load.** Add `95e408ff` (the s04 adopted file's md5 key in the format `load_by_vi` already uses — read
   `tools/bench/memory_model.json` and match it) = 605.4 to `load_by_vi`. Record ONLY: `fail_above` 680, MEMSTOP 695 and every
   other parameter unchanged (diff before/after shows exactly one added key).
2. **ONE start.** Make the s05 prediction script and the prerun's X10 use the SAME start (the gate's `x10_start` at 605.4);
   report any remaining place that computes a start differently (file:line). Do not edit `tools/stage_prerun.py` or any stage
   tool for this — if the prediction script is a card-local `prep_c146_*` copy of the maker, edit only that copy; if a stage tool
   must change, RETURN with the line.
3. **Re-cut s05.** From the maker's op table: the longest v18 prefix starting at op 98 that (a) splits no 'of' group, (b) has X10 <= 680
   at the one start. Report cut op, peak, margin to 680 and to MEMSTOP 695, and the first op that would exceed 680. Rebase on the
   real s04 graph exactly like 145-a2-6 (`stage_prerun.py --rebase`, no hand patch; a refusal is quoted, not patched around).
   Keep the old s05 plan/pred/in as `*_prov2` copies first (md5 recorded).
4. **Pred** EL by `tools/elrule.py` (base 58, the fixed rule); report total and counted classes. Regenerate `plan_ring_p4_s05v18_pred.json`.
5. **Recipes**: dry (sandbox) and prerun of BOTH `tools/recipes/stage_d1_ring_p4_s05v18.py` and `_scratch.py` on the new bytes; 0 FAIL
   required. The scratch recipe's MEM_STOP stays 680.0.
6. **X11 / #2626.** Report whether the cut carries ops 118/119 (`p4_w_tp_row` / `p4_w_rp_row`, Build Array #2626 `array`).
   - If it does: write `tools/bench/plan_ring_p4_s05v18_licence.json`, schema `pb-licence/1`, modelled on
     `tools/bench/plan_l2b1_licence.json`: `plan` = the s05 plan path, `rename_by_uid` node 2626, `term_uids` = the still-open #2626 input
     uids by uid (read from the real s04 graph), `require` = "every listed uid is an input of #2626 in the real end read with the same
     uid, unwired unless this session wires it, else the licence is void", `decided_by` = "PD352(d)". Prerun must then read X11 as licensed.
   - If it does not: X11 must PASS unlicensed; no licence file. Report which session (s06, ...) will carry ops 118/119 and 132/150.
7. **Housekeeping.** Copy `tools/bench/build_opwiringrules_v0_hygiene.json` into `tools/bench/op_hygiene/` (create nothing else there),
   md5 equal; the original stays.
8. md5 before/after: s04 plan/pred/recipes-of-s04, v18 plan, the s04 adopted VI, s03 282301ca, bed 39511877, every stage tool = unchanged.
   No LabVIEW process started (`tasklist` after). Nothing launched.

## Never
LabVIEW, camera, motor; a scratch or real launch; editing a stage tool, the X11 gate, v18, any s04 file; changing a parameter of
`memory_model.json` other than the one `load_by_vi` key; clearing a refusal by editing the plan.

## Return
`result/1`; facts file `tools/bench/diag_c146_a1_2_facts.md`: cut op / peak / margins, the one start and where it is used, new s05 file
md5s, pred EL total + classes, dry/prerun counts per recipe with every non-PASS line quoted, licence state, op 118/119/132/150 session
assignment, md5 table, hygiene copy md5s.
