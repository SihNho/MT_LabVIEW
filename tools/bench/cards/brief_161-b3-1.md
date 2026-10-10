---
card: 161-b3-1
status: current
date: 2026-10-10
---
# Brief 161-b3-1 (assignment 161-3) - P5-2 STEP-2 SCRATCH (ONE run), adopt as `D1_ring_p5s02b_<ts>.vi`, record the measured census into the pred; the ONE LabVIEW card

This is `tools/bench/cards/brief_158-a3-2.md` again (read it, and through it brief_158-a2-2 / 156-a2-1 / 155-a3-1 / 155-a3-2 / 154-a3-3 / 3b: launch, adopt, final Error List,
graph read, `load_by_vi`, invariants, LabVIEW-gone) with ONLY the deltas below. Step 1 (p5s02a) was adopted by that card; this is step 2 (p5s02b) on its adopted file.
Read `tools/bench/diag_c161_b2_1_facts.md` (all gates as expected: dries PASS-UNVERIFIED with CEN2 the only unverified gate, PB 5 RECORDED, prerun 16/0, check-launch ALLOW, scratch-required rc 3)
and `docs/d1/ring-p5b.md` PD393(c)(d), PD394, PD395. Helper scripts: copy `diag_c158_a2_2_adopt.py`, `diag_c158_a3_2_inv.py`, `diag_c158_a3_2_checklaunch.py` (+ the `diag_c155_a3_2_*` family)
to `diag_c161_b3_1_*` (names, ids, pins, paths ONLY; say which lines changed). Call shared functions, do not paste a block you can import (`docs/script-writing.md`).

## Pins (md5 in the task; a mismatch is a RETURN)
stagekit 9b8f82c1, stagesim 95a162ba, stagexec a4df7e15, stage_prerun 7605116f; plan_ring_p5s02b f4520b10, pred **a1fd43fb**, licence f61a2514, EL 79ec3207,
MAIN recipe 083fda6d, scratch recipe 3f6fb898. Base = adopted p5s02a `claudeDev\D1_ring_p5s02a_20261010_023239.vi` 94ffff94 (NEVER edited; the scratch runs on a NEW byte copy).
s09 eb1d0f31, P5-1a 2482fe7b, P5-1 7f2582ae are hashed before and after.

## Deltas against brief_158-a3-2
1. **Pre-checks:** the same dry / prerun / `--check-launch` / `--scratch-required` as `prep_c161_b2_1_*.log` on UNCHANGED bytes (a re-run is not an edit). Any md5 above differs or any
   gate differs from `diag_c161_b2_1_facts.md`: RETURN with the line, no launch.
2. **Launch command** exactly as `prep_c161_b2_1_checklaunch.log` (ALLOW): `py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c161_p5s02b_scratch.log -- py -u
   tools/recipes/stage_d1_ring_p5s02b_scratch.py`, plus the `--unverified-card tools/bench/cards/task_161-b3-1.json` argument that the gate asks for (the rules text carries
   `DRY-UNVERIFIED-OK: CEN2 census unpredicted`). Nothing else is relaxed. A gate refusing your own command text is a false positive: `py tools/gate_fp.py log`, no env bypass; RETURN with the refusal text.
3. **ONE scratch** under `bgrun --material` on a NEW byte copy of 94ffff94, ops 0..10 as the recipe prints them. Quote: E1 real == sim (diff 0) at every checkpoint (ops 0,1,2,3,4,5,7,8,9,10 - the
   `SX.checkpoint_ops` set; ops 1, 4, 8 are the `delete_wire` reads); ops 5 and 9 (`connect_term_uid`) must pass their sink check; the per-op CLASS census; the final census vs the pred
   (CEN2 is UNPREDICTED: quote the measured per-class numbers, they are the measurement, not a pass/fail against a prediction).
4. **Gates.** Quote the outcome of PB (5 RECORDED rows with ids), D, TD, CD, INV, E1, X10 (metered start / peak vs planned MAIN 665.0, limit 675). **Any BLOCK gate FAIL (other than the
   unpredicted CEN2) = RETURN with the facts; NO second run in this card and none by anyone: the work copy is kept, NEVER loaded, and the assignment session hands the stop back.**
5. **Adopt** (structural PASS only): `claudeDev\D1_ring_p5s02b_<ts>.vi` (hashlib md5; an in-between file, not counted toward the 6, D-2026-10-02-02), the FULL Error List of the adopted file compared ITEM BY ITEM with
   `errorlist_predicted_D1_ring_p5s02b_end.json` 79ec3207 (total, per class; predicted 51; the 2 UNPREDICTED are A32 `w_gr` / A39 `w_hr` - say which items are extra / missing), fresh-instance load + graph json +
   md5 (`tools/bench/graph_ring_p5s02b_<ts>.json`), `load_by_vi` entry (only that entry of `memory_model.json`; key-by-key diff quoted), invariants md5 before = after, handles, LabVIEW closed AND verified gone.
   Write the adopted file path + md5 on one line in the facts.
6. **Record the measured step-2 census into the pred (PD392(c)):** only AFTER adoption, by a script `tools/bench/prep_c161_b3_1_census.py` (<= 60 lines, calls the pred maker's / lib's functions, no pasted
   arithmetic) that reads the scratch graph reads and writes the per-class census into the pred's census block, producing a NEW pred md5. Quote old -> new md5 and the key diff (census keys only).
   The pred maker's other keys, plan, licence, EL stay byte-identical. The gate stays an equality (no loosening).
7. No `tools/hooks` edit, no recipe / plan / licence / EL / stage-tool edit, no original opened, no motor or camera. Concurrent cards: none. Failed-copy cleanup only after adoption and only for a failed
   p5s02b copy of this card (none expected).

## Report `tools/bench/diag_c161_b3_1_facts.md` (<= 45 lines)
Pre-check lines; gate outcomes per op class; E1 per checkpoint; ops 5/9 sink checks; per-op census + final measured census; PB 5 RECORDED; metered start / peak vs 665.0 / 675; adopted file + md5 + load MB;
EL total + per-class + item diff vs 79ec3207; graph json + md5; `load_by_vi` diff; invariants; handles; pred old -> new md5 + key diff; LabVIEW gone. `OPEN:` lines (measurements only).
Dispatch a hypothesis peer only if a gate FAILS.
