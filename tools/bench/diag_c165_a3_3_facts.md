---
card: 165-3-3
date: 2026-10-10
status: current
---
# 165-3-3 facts (offline; no LabVIEW) - step-5 (p5s02e) recipe pair + pred + licence + predicted EL on plan fd23974e; all gates PASS; prior art `novel`; NOT launched
- **1. md5 first** (`prep_c165_a3_3_hash.log:39` PASS 36/0, hashlib bytes only): 34 card inputs == pins; VI D1_ring_p5s02d_20261010_152518.vi 6dcd5c3d; stagexec 1d5309f4.
- **2. Recipes** (written directly on stagekit.RingSession, pair shape of p5s02d; NAME D1_ring_p5s02e, KEY ring_p5s02e, OUT_JSON launch_c165_p5s02e.json,
  scratch LOG diag_c165_p5s02e_scratch.log, OPS_CENSUS (2, 6, 7, 9)): main `stage_d1_ring_p5s02e.py` c9fd886a, scratch `..._scratch.py` 88c81f34.
- **3. Drivers** (CFG + one call of prep_c164_a2_3_lib): licence `prep_c165_a3_3_licence.log:14` 5/0 -> `plan_ring_p5s02e_licence.json` 8fda7b92, 0 renames,
  X11 CLEAN (`prep_c165_a3_3_x11.log:3`). EL `prep_c165_a3_3_el.log:27` 10/0 -> `errorlist_predicted_D1_ring_p5s02e_end.json` 2a8e2984:
  `EL COUNTS cleared 4 raised 0 unpredicted 2 standing 49 stale 0 total 49 (upper 51)` (:24); CLEARED item 6 nosource w10362 by A72 dw_10362, item 7 undirected
  #5204 by A73 w_k3f, item 8 undirected #10404 by A84 w_k4f, item 50 nosource w25232 by A83 dw_25232 (:13-16); UNPREDICTED A77 t_k4o, A80 t_k4i reb groups (:21);
  compare B / F / W extra 0 missing 0 (:11, :22, :25). Step-4 stale rows (clears_by A70 w_k3f / A80 w_k4f, :3-8): items 6/7/8/50 CLEARED above; items 4
  (nosource w4337) and 49 (whilesubvi w9636) STANDING - their uids are named by no action of this plan (lib rule).
- Pred `prep_c165_a3_3_pred.log:39` 17/0 -> pred + sink-gate census `prep_c165_a3_3_sg.json` 94fce45c (0 rows, :23); then `prep_c165_a3_3_pd402.log` 9/0 adds
  keys pd401b (2ea89c4b) and pd402 -> pred `plan_ring_p5s02e_pred.json` 825cbf65. C 13 actions -> 9 ops == session (:6); X1 start 609.8 == x10_start(6dcd5c3d) (:9);
  X10 MAIN 665.0 <= 675, peak 659.9 (:11); X17 (:12); DW dw_10362 / dw_25232 (:13); DO 0 (:14); OBJ SK4L/SK4R/KI4/OK4/IK4 (:15); FM w_k4pass #31517 (:16); RT (:18);
  census UNPREDICTED 13 rows (:20). **E1** [0,1,3,4,6,7,8,9] == checkpoint_ops == session, delete_wire ops [1,8], step files md5 == recorded (`pred.log:7-8`).
- **PD402** (`pd402.log:5-10`): t8776 w10362 step 0 -> 0 step 1 -> net w31792 src [31815] step 2..end; t24342 w25232 step 11 -> 0 step 12 -> net w-15 src [-11]
  step 13; expectation census in [{}, {'Wire': 1}], Is Broken? False (sim; nothing measured in LabVIEW).
- **4. Gates on the FINAL bytes** (second run in each log; the first run, before a docstring/LEVEL text edit, also PASSed):
  DRY main `prep_c165_a3_3_dry.log:136` `=== DRY PASS-UNVERIFIED CEN2 new-object census ... first_fail=None coverage 35/36`, rc 0 (:138);
  DRY scratch `prep_c165_a3_3_scr_dry.log:186` same, coverage 34/37, rc 0 (:188). PRIME-SKIP #8776 / #24342 in both (dry :97-98, scr :140-141).
  PB (dry :131 / scr :177) PASS by POSITION, [31, 31] rows == pred 26 + 5 RECORDED, 24 open pairs, blocked []; RECORD rows 376 'cal cluster path', 'file size',
  'selected path' class 1, 'error in', 'total data array in' class 3 (fp-86) (dry :126-130). No PB BLOCK.
  PRERUN main `prep_c165_a3_3_prerun.log:93` PASS 16/0: X8 (:69), X17 (:78), X10 peak 665.0 (:89), X14 INFO rows 13 budget 15 (:90). Scratch
  `prep_c165_a3_3_scr_prerun.log:118` PASS 16/0, X10 659.9 (:114), X14 (:115).
  `--scratch-required` `prep_c165_a3_3_scrreq.log:3` rc 3 (:4): `SCRATCH-REQUIRED | stage_d1_ring_p5s02e.py | CENSUS-UNPREDICTED ... rows [1..13]`.
  check_launch (`prep_c165_a3_3_release.log:9,11`): brief form ALLOW, step-4 form ALLOW; scratch log absent, task_165-3-4.json exists (:8).
  STOP RECORDs of both recipes: 0 found (:7); prior_art_review armed none (`prep_c165_a3_3_priorart.log:39`); fixed_claim False both (:5-6) - nothing to clear.
- **5. Prior art** `prep_c165_a3_3_priorart.log:7` VERDICT-CARD verdict=novel ($1.36, 97 s); archive `archive/peer/2026-10-10-priorart-priorart-c165-a3-3-p5s02e.md`,
  disposition written under `## What was done with it`; released_slugs [] rejected [] (`release.log:4`) - no finding slug to release.
- **bgrun parse** (`prep_c165_a3_3_argp.log:14-15`): the brief's form (`--unverified-card` BEFORE `--`) = REJECT SystemExit(2), "required: --log" (bgrun.py:148-166
  has no such option; REMAINDER swallows the rest); step-4 form (flag after the recipe path) ACCEPT. check_launch accepts both (regex anywhere).
- **Launch lines.** Scratch (working form): `py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c165_p5s02e_scratch.log -- py -u
  tools/recipes/stage_d1_ring_p5s02e_scratch.py --unverified-card tools/bench/cards/task_165-3-4.json`. Real: `py tools/bgrun.py --material --max-min 50
  --log tools/bench/launch_c165_p5s02e.log -- py -u tools/recipes/stage_d1_ring_p5s02e.py`.
- **UNCHANGED** (`prep_c165_a3_3_md5.log` U 16/16): stagexec 1d5309f4, stagesim 95a162ba, stagekit dd57c1ca, stage_prerun 7605116f, stage_shared b688edd4,
  memory_model ff0fabca, plan fd23974e, r_in 0b895983, graph 2a5fa0c4, EL c74200f2, VIs 6dcd5c3d/564d8cbe/f9ae7751/94ffff94/7f2582ae/eb1d0f31. No tool/hook/doc/plan edit.
- Failing log: `prep_c165_a3_3_argp.log` run 1 (:7, NO RESULT LINE) = my own measurement script's uncaught SystemExit; caught it, re-ran: PASS 2/0 (:16).
- OPEN: name of the adopted file - recipe NAME D1_ring_p5s02e per brief_165-3-3.md:19-20, but PD400(c) (`docs/d1/ring-p5c.md:171-173`) and task_165-3-4.json outputs name the full-prefix result `D1_ring_p5_<ts>.vi` (broken file 6 of 6).
- OPEN: launch form - brief_165-3-3.md:29 / 165-3-4 brief form fails bgrun's parser (`argp.log:14`); use the step-4 form above.
- OPEN: prior-art advisory A4 - PD402 does not cite the cycle-81 PRIME-skip precedent PD186 (`docs/d1-loop12-17-split-plan.md:803`); plan doc not editable here.
