# Brief 127-3 — offline: P3b FINAL plan (PD258(c)–(e))

Plan: `docs/d1-loop12-17-split-plan.md` Pre-decided 255–258 (read 258 first). OFFLINE ONLY: no LabVIEW, no COM.
Base = the P3a bed graph (`tools/bench/graph_ring_p3a_20261001_190155.json`), plan input `tools/bench/plan_ring_p3b_in.json`
(127-2, md5 `6e52b85d…`), maker `tools/bench/plan_ring_p3b_make.py`.

## STEP 1 — rows for PD258(c) (IMAQ Copy's error terminals)
- `IMAQ Copy` error in ← `#6810` error out: a branch of the existing net (today → LoopTunnel `#649` on `#639`), crossing
  `#639` → case `#22694` False → FS frame 2 (measured crossing kind, `connect_term_uid`, then RLE). Old sink `#649` must
  stay connected (M11 / PD256(c)).
- `IMAQ Copy` error out → FS frame 3 (`fs_frame_to_frame`) → `Unbundle By Name` (`status`) → `Select` (s = status,
  t = constant −1 (I32), f = BufNum in frame 3) → the element input of frame 3's `Num(i)` Replace Array Subset (replacing
  the direct BufNum wire there). `Latest = BufNum` unchanged.
- Find the creation route for `Unbundle By Name` and `Select` (gscript `create_primitive_nested` with or without a donor;
  `docs/NAMES.md`, `docs/toolkit-capabilities.md`, recorded graphs); declare every created terminal's measured
  `term_class` and name (PD251(b)). If a route or a terminal fact is not recorded anywhere, mark the row UNMEASURED and
  RETURN that as OPEN (the scratch run will measure it) — do not guess.

## STEP 2 — fix dry FAIL / prerun X4
`IMAQ Copy` create declares 3 unnamed sink terminals (`diag_c127_2_checks.log:5-8`). Name its terminals from a recorded
graph that contains IMAQ Copy (search `tools/bench/graph_*.json`, `main_vi_nodeterms.json`, `docs/wiki/`), with their
classes. Same rule: not recorded ⇒ OPEN, not a guess.

## STEP 3 — FINAL plan and predictions
- Census prediction (stagesim end graph) and Error List prediction: 54 (P3a's 55 minus w27378's loose end) plus the items
  P3b's own open ends leave (count them by kind from the plan's end cdiff; say which rows they come from).
- `py tools/stage_prerun.py` dry + prerun PASS on the final recipe; then `--scratch-required <recipe>` (expect exit 3:
  new classes) — record the output.
- Prior-art review for the new classes (FS / GrowableFunction / IndexArray / Unbundle By Name / Select) through
  `tools/prior_art_review.py` as the gate requires; annotate the review file per its rules.
- Write the recipe `tools/recipes/stage_d1_ring_p3b.py` (≤ 120 lines on stagekit, rows only from the final plan file)
  but DO NOT LAUNCH it.

## STEP 4 — self-test
`tools/bench/selftest_errorlist_reuse_81*` K0/K9 expect the pre-125-1 refusal of `stagexec selftest` under labview none;
card 125-1 allowed it (`protocol.py:398-403`). Update the expectation and rerun green. If `guard_peer` still owes a review
on the old failing log, dispatch it (`-Agent claude -Role hypothesis`, review card) and annotate it.

## Return
`result/1`: final plan path + md5, recipe path + md5, census/Error List predictions, dry/prerun/scratch-required outputs,
prior-art verdict, self-test counts, OPEN list. Return at the first unexpected result.
