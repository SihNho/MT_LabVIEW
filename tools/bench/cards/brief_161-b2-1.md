---
card: 161-b2-1
status: current
date: 2026-10-10
---
# Brief 161-b2-1 (assignment 161-3) - OFFLINE PRE-CHECK of the p5s02b step-2 launch: dry of both recipes, prerun, `--check-launch`, `--scratch-required`, hashes of the four VIs; NOT launched

`labview: none` (no LabVIEW process; `tasklist` may be refused - say so), no `--launch`, no `tools/hooks` edit, no `tools/*.py` edit, no plan / recipe / pred / licence / EL edit. This is the c3-3 / b1-1 pass of the same card
(`tools/bench/brief_160-c3-3.md` items 2-5 and `tools/bench/cards/brief_161-b1-1.md` items 3-5; logs `prep_c161_b1_1_dry.log`, `prep_c160_c3_3_dry.log`) run on the NOW-FINAL tools: stagekit **9b8f82c1** (PB class 1/2, 161-a3-1),
pred **a1fd43fb** (X10 on the shared checkpoint rule, 161-a3-2: MAIN 665.0 at START_ASSUMED, peak 659.9). Read `tools/bench/diag_c161_a3_1_facts.md` and `tools/bench/diag_c161_a3_2_facts.md` first, and
`docs/d1/ring-p5b.md` PD393(c), PD395. Unchanged and must stay: plan f4520b10, licence f61a2514, EL 79ec3207, recipes 083fda6d / 3f6fb898, stagesim 95a162ba, stagexec a4df7e15, stage_prerun 7605116f.

## Decisions already taken (PD393(c), PD395(d)) - apply, do not ask
- The dry of the p5s02b recipe and of `_scratch.py` may end `PASS-UNVERIFIED` only when the ONLY unverified gate is CEN2 with the census UNPREDICTED (no census sample exists yet; the step-2 scratch measures it).
  PB must PASS (the 5 `#376` rows RECORDED as class 1 / class 2). Any other unverified gate, a dry FAIL, or a refusal by prerun / `--check-launch` is NOT worked around: quote the line verbatim and stop (hand-back).
- X10 is a READ-ONLY check: prerun reports the planned MAIN against 675 (expected 665.0). Above 675 = quote and stop. No gate loosened, no census sample added.

## Do
1. Dry of the recipe pair with the SAME command forms as `prep_c161_b1_1_dry.log`: `tools/recipes/stage_d1_ring_p5s02b.py`, then `_scratch.py`; log names `prep_c161_b2_1_dry*.log`. Quote word-for-word: PASS / PASS-UNVERIFIED,
   the unverified count and each unverified label, the PB gate line (RECORDED count, `pairs_extra_left`), and that the dry runs past ops 5 and 9.
2. Prerun (X10 read-only, X14, X17, X8) on the final tool md5s, then `--check-launch` (no `--launch`), forms from `prep_c156_a1_1_prerun.log` / `prep_c156_a1_1_checklaunch.log`: quote every rc and reason line.
3. `py tools/stage_prerun.py --scratch-required tools/recipes/stage_d1_ring_p5s02b.py` (form `prep_c156_a1_1_scrreq.log`): quote the exit code and reason (expected 3, PD391(e)).
4. Re-run `tools/bench/prep_c160_c3_3_hash.py` (hashlib, bytes only): s09 eb1d0f31, P5-1a 2482fe7b, P5-1 7f2582ae, p5s02a 94ffff94: quote equal / unequal. Also list `claudeDev` for the exact name of the p5s02a file (the scratch card copies it).
5. Hook false positive on your own command text: `py tools/gate_fp.py log ...`, report, no env bypass, never edit a hook. Background anything slow under `py tools/bgrun.py --material --max-min N --log ... -- ...`.

## Report `tools/bench/diag_c161_b2_1_facts.md` (<= 35 lines, facts only)
dry (both recipes) / prerun / check-launch / scratch-required lines with rc, unverified count + labels, PB line, MAIN vs 675, the four VI hashes with the claudeDev file name of p5s02a; md5 UNCHANGED list; `OPEN:` lines
(measurements only).
