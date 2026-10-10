---
card: 160-c3-3
status: current
date: 2026-10-10
---
# Brief 160-c3-3 (assignment 160-3) - OFFLINE re-issue of 160-c3-2 (never ran: the assignment hook read a wording false positive, fp-83): re-pin the c3 makers to the final stagekit, run the dry / prerun / check-launch / scratch-required gates, hash four VIs; NOT launched

`labview: none` (no LabVIEW process; `tasklist` may be refused - say so), no `--launch`, no `tools/hooks` edit, no `tools/*.py` edit, no plan / recipe-text edit unless a gate forces it (see 3).
Read `tools/bench/diag_c160_c3_1_facts.md` (c3-1: pred 14/0, licence 5/0, EL 9/0 done; dry FAIL at gate L0 only) and `docs/d1/ring-p5b.md` PD390(c), PD391(d)(e), PD392.

## Decisions already taken (PD392, judgement 2026-10-10) - apply, do not ask
- X10 is a READ-ONLY check in this card: prerun reports the planned MAIN against the 675 MB limit; the limit value stays as it is in the tool. Nothing about X10 is written.
- The dry may end `PASS-UNVERIFIED` when the ONLY unverified gate is CEN2 and the census is UNPREDICTED (no census sample exists yet; the step-2 scratch measures it, precedent PD261(c)/PD292(c)).
  Any other unverified gate, a dry FAIL, or a refusal by prerun / check-launch is NOT to be worked around: quote the line verbatim and stop (hand-back).
- No census sample is added and no gate is loosened to make the dry pass.

## What changed since c3-1
- Card 160-e4-1 made `RingSession.gate_l0` accept `plan_in` = `<stem>_in` or `<stem>_in<digits>` (self-test `selftest_c160_l0stem.py` 14/0). stagekit md5 is now
  **0b5bb678169d659feed7408648a63354** (was 1441bb4c). stagesim 95a162ba, stagexec ddf23a31, stage_prerun 7605116f unchanged. Facts: `tools/bench/diag_c160_e4_1_facts.md`.
- Do not touch the files card 160-e5-1 re-pinned (selftest_c155/c156/c160_*, diag_c160_b2/g1/h1, prep_c160_b1_1_mk / b3_1_mk) and do not read their results as yours.

## Do
1. Re-pin your own makers to the final stagekit: `prep_c160_c3_1_md5.py:17`, `prep_c160_c3_1_pred.py:39` (1441bb4c -> 0b5bb678). Re-run `prep_c160_c3_1_md5.py` (expect all pins hold), `prep_c160_c3_1_pred.py`,
   `prep_c160_c3_1_licence.py`, `prep_c160_c3_1_el.py` in the c3-1 order. **Expected: plan_ring_p5s02b_pred.json (48b50b29), plan_ring_p5s02b_licence.json (f61a2514),
   errorlist_predicted_D1_ring_p5s02b_end.json (79ec3207) are byte-identical to c3-1**; if the pred embeds the stagekit md5, name each changed byte-range and its cause. Other content differences are a FAIL.
2. Dry on the recipe pair with the SAME command forms as c3-1 (`prep_c160_c3_1_dry.log`, `prep_c156_a1_1_dry.log`): recipe `tools/recipes/stage_d1_ring_p5s02b.py`, then `_scratch.py`.
   Quote the result word-for-word: PASS / PASS-UNVERIFIED, the unverified count and the label of each unverified item.
3. Prerun (X10 read-only, MAIN <= 675; X14, X17, X8) on the final tool md5s, then `--check-launch` (no `--launch`), command forms from `prep_c156_a1_1_prerun.log` / `_checklaunch.log`.
   The prior-art review `archive/peer/2026-10-10-priorart-priorart-c160-d4-1-p5s02b.md` was run on recipe bytes 083fda6d: the recipe text (md5 083fda6d / 3f6fb898) stays as it is;
   if a gate would need a recipe text modification, stop and report the gate line instead.
4. `py tools/stage_prerun.py --scratch-required tools/recipes/stage_d1_ring_p5s02b.py` (form from `prep_c156_a1_1_scrreq.log`): quote the exit code and the reason line (expected 3, PD391(e)).
5. Hash four VIs with ONE small hashlib script `tools/bench/prep_c160_c3_3_hash.py` (reads bytes only, md5, prints name + md5; never opens them in LabVIEW): `D1_ring_p4s09_*` (eb1d0f31),
   P5-1a `D1_ring_p5s01a_*` (2482fe7b), P5-1 `D1_ring_p5s01_20261009_124542.vi` (7f2582ae), `D1_ring_p5s02a_20261010_023239.vi` (94ffff94), all in
   `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev`. List the directory to get exact names; quote name + md5 + equal/unequal.
6. A hook false positive on your own command text: `py tools/gate_fp.py log ...`, report, no env bypass, never edit a hook. Background anything slow under
   `py tools/bgrun.py --material --max-min N --log ... -- ...`.

## Report `tools/bench/diag_c160_c3_3_facts.md` (<= 35 lines, facts only)
md5 of every file written or re-run output; pred/licence/EL md5 vs c3-1; dry (both recipes) / prerun / check-launch / scratch-required lines quoted with rc, **unverified count + labels**;
md5 UNCHANGED: stagesim 95a162ba, stagexec ddf23a31, stage_prerun 7605116f, stagekit 0b5bb678, plan f4520b10, in 56bfddd3, in2 927b805c, graph 7ac24924, recipes 083fda6d / 3f6fb898,
the four VIs (step 5); `OPEN:` lines.
