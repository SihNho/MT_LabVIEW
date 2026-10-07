---
type: brief
status: current
date: 2026-10-08
---
# Brief 146-a2-1 — fix the Error List predictor's missing `carry` in `tools/elrule.py`, ALONE (offline, edits a stage tool)

OFFLINE (`labview: none`). Runs ALONE: no other card is live (it edits a stage tool, PD281(a)). No LabVIEW, camera, motor.

## Facts (round 1, `tools/bench/diag_c146_a1_4_facts.md`, review `archive/peer/2026-10-08-c146-a1-4-el55.md`, plan `docs/d1/ring-p4b.md` PD353(b)(c))
- The s05 scratch read 55 Error List items; the s05 pred said 57. Read file: `tools/bench/errorlist_D1_ring_p4s05_20261008_002621_20261008_003324.json`
  (md5 06a59001, `--role final`, 55 items, every item uid null).
- `elrule.session_prediction` (`tools/elrule.py:217-225`) calls `predict(st0, last, base_total, made, subvis=...)` with NO `carry`. In `predict`
  (`:170-192`), `carry` = uids an earlier session's prediction counted as A items that are still open; they are added to the `created` set when
  the END state is scored (`:177`) and are skipped at the start (`:176`). Round 1's review found two base input items that s05 closes
  (`#5058` SubVI 'Image In' by `p4_w_img_trk`; `#29843` by `p4_t_slot_out` / `p4_w_pool_in`) stayed counted.
- s01..s04 predictions are 51 / 53 / 55 / 58 and match their reads; `tools/bench/selftest_elpred.py` is the self-test (pinned fixtures).

## Do
1. Reproduce first: rerun the existing predictor path for s05 (the plan `tools/bench/plan_ring_p4_s05v18.json`, base total 58) and print its total (57)
   and per-class counts (`new_items` / `closed_items` / `open_at_end` by class). Quote the per-class counts of the READ file
   `errorlist_D1_ring_p4s05_..._003324.json` by the same classes the tool uses (`item_class`, `:201`; items of other classes by their text).
2. Find out from the code and the sim state which base input items the START state (`step_00`) counts as open and the END state does not, and why
   `items(st0, ...)` / `items(last, ...)` disagree about `#5058` / `#29843` (the `claimed` set / `created` set semantics at `:140-158`).
   The fix is whatever makes the START open-set the correct comparison base — `session_prediction` passing the base's open input items as `carry`
   is the named candidate (PD353(c)); if the code shows a different smallest correct change, say why and use it. Do NOT tune any constant to the
   answer.
3. Edit `tools/elrule.py` only (plus its self-test file for new cases). The self-test must re-derive **s01 = 51, s02 = 53, s03 = 55, s04 = 58
   UNCHANGED** (same totals AND same per-class items as before the edit — compare `new_items` / `closed_items` before and after) and **s05 = 55 with
   per-class counts equal to the read file**. A total match with a per-class mismatch is NOT a pass.
4. Run `tools/bench/selftest_elpred.py` (and any other self-test that imports elrule: grep `import elrule` / `elrule` under `tools/` and run the
   self-tests found) before and after; report counts.
5. md5 table old -> new for `tools/elrule.py` and every file you touched; unchanged: `tools/bench/plan_ring_p4_s05v18.json`, `plan_ring_p4_s06v18.json`
   (8f33ad75), `memory_model.json` (559be4cf), every s03/s04/s05 file, the bed (39511877), s04 95e408ff, s03 282301ca. No LabVIEW process (`tasklist`).

## Never
LabVIEW, camera, motor; editing any plan, pred, recipe, other stage tool, gate, or the read file; rerunning the s05 scratch; fitting the predictor to
the s05 answer by a special case keyed on uid or session name.

## Return
`result/1`; facts file `tools/bench/diag_c146_a2_1_facts.md`: reproduction (57 and classes), the cause in code with file:line, the change (diff
summary), per-session before/after table s01..s05 (total + per-class), self-test counts, md5 table. If the fix cannot be shown class-exact for s05,
RETURN with the per-class table and say which class differs; do not adopt a total-only match.
