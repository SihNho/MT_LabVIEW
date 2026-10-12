# Lean-bench task: finish P6-2 (recorded-frame replay, rule 1a for P6) - one session, <= 180 min, <= $60

Read `CLAUDE.md` (the lean rules) first. Then the facts you need are already written down - use them, do not re-derive:
- `docs/d1/ring-p6.md` PD409 (lines ~200-289), PD410, PD411; `docs/d1/ring-p6b.md` PD412-413 (a dry-checker bug - the
  dry/prerun gate is NOT required in this arm, so you may ignore that whole detour).
- `tools/bench/p6_replay_facts.md` (F1-F6), `tools/bench/next.json` (the current arm's pass list - reference only).

## Starting state (all built, hashes in next.json pass[0-1])
- P6 bed (the work VI, read-only here): `claudeDev\D1_ring_p6_20261012_212645.vi` c2d9c13c.
- S1 replay copy: 126f8497 (plan 110; under `claudeDev\replay\`, find it by md5). Paced stand-ins built:
  `claudeDev\replay\replay_imaqdx_get_image_buf_paced60.vi` / `replay_get_buff_image_paced60.vi` (e40ec867 / 59ec66b6).
- Recipe `tools/recipes/stage_replay_swap.py` + plan literal 170 (01c21526): #6810 -> paced outer copy, #22692 -> afce0d04.
- Leg driver `tools/bench/drive_m8_replay_p6.py` (self-test 7/0) + `tools/bench/m8_legs.py`; compare
  `tools/bench/m8b_replay_compare.py` (extension accepted, self-test on 110-7: 4443 rows, 0 X/Y/Z differ, DISTINCT 4443/4443).
- Frames: `G:\m8_replay_frames` (manifest md5 9055d98a).

## Do
1. Build the P6 replay copy from a byte copy of c2d9c13c with plan 170's two swaps; save it ONLY under
   `claudeDev\bench\lean\` (create it), only with ExecState 1 (warm and cold); record md5.
2. `py tools/motor_gate.py --session start` (limits SET + read back, quoted).
3. S1 leg (120 s, as 110-7), then P6 leg (>= 1500 tra rows), each its own LabVIEW session, LabVIEW verified gone after
   each; per leg: tra rows, Total Lost Frames, frame-counter delta, every written file + md5. Leg outputs under a new
   folder of yours (not `tools/bench/m8_out/` of the main arm).
4. `py tools/motor_gate.py --session end` (RELEASED + read back, quoted).
5. Compare (only if S1 lost 0), D = 20 slots: DISTINCT count, MATCH (first miss + drop signature), cal outside the
   date/time field, trans/rot post-init, init inside motor_limits.json ranges (rotor finite), every other leg file.
   Each item PASS/FAIL as a fact.

You decide how to handle surprises yourself (fix a recipe/diagnostic, retry) - there is no hand-back. Do NOT edit
`tools/hooks/**`, `tools/motor_gate.py`, `tools/bench/motor_limits.json` or `CLAUDE.md`.

## Report (`tools/bench/lean_bench/lean_report.md`)
Timeline (clock time per step), what failed and how you fixed it, each compare item with its number, motor session
start/end readback lines, LabVIEW-gone check, md5s of the inputs at the end (must equal the start), then
`RESULT {"p6_2": "PASS|FAIL|INCOMPLETE", "items": {...}, "minutes": N}`.
