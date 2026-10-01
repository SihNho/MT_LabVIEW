# Brief 127-2 — offline: P3b plan tooling (PD257(c)) + two small tool debts

Plan: `docs/d1-loop12-17-split-plan.md` Pre-decided 254–257. OFFLINE ONLY: no LabVIEW, no COM. Facts come only from
recorded logs/records (126-4, 126-6, 126-8 results; `census_samples.json`). Do not edit `tools/gscript.py` (card 127-1 is
using it in LabVIEW). Existing routes and self-tests must stay green.

## STEP 1 — plan format and compile
- `docs/protocol/stageplan.json` (stageplan/1) gets a `wire_remove_loose_ends` op (target = a wire created by a named
  earlier row, or a pre-existing wire uid for P3a's `w27378`).
- `tools/stagexec.py` compiles a border-crossing wire (case frame → FS frame, `#639` source → FS frame, While `i` → FS
  frame, pool For exit → FS frame) to `gscript.connect_term_uid` (126-6's measured route), not generic `connect`; and
  `wire_remove_loose_ends` rows to `gscript.wire_remove_loose_ends`.
- `tools/stagesim.py` models those crossings from the census variants recorded by 126-4/126-6 under `connect_term_uid`
  in `census_samples.json` (per variant: tunnels created per border, Terminal/Wire deltas, index mode), and models
  `wire_remove_loose_ends` as census {}.
- The 4 rows "2nd+ sink into an FS frame the source already entered" (`i` → f1 ×3, BufNum → `Latest` f2): model them as
  PD257(d)'s route (same-frame wire from the existing FS tunnel's INNER face) with the R4-analogue census {}, tagged
  PROVISIONAL pending card 127-1's measurement (127-1 runs beside this card).

## STEP 2 — the P3b plan replays
- `tools/bench/plan_ring_p3b_make.py`: put the 2 RELEASED rows (`TransPos` ← `#30117` Value, `RotPos` ← `#4580` Value,
  PD257(a)) into the actions, and move the 14 `wire_remove_loose_ends` rows from `post_rows` into the plan at their
  positions (PD255(b)/256(b): after EVERY crossing row, plus one for `w27378`).
- `tools/bench/plan_ring_p3b_in.json` must replay END TO END in stagesim. Report: rows, end census, end
  `computation_diff` (P3a's 16 open rows minus what P3b closes), and that every old sink of re-created nets is still
  connected (PD256(c)).
- Run `dry` and `prerun` on what can be run offline; this is NOT the final plan (IMAQ Copy's error terminals and the
  Error List prediction come next cycle), so record the prerun result, do not chase X-checks that need those.
- Rerun `tools/bench/c125_1_offline_measure.py` (PD252(a)) after the stagexec/stagesim edits; 0 COM trips.

## STEP 3 — tool debts (do these LAST)
- `tools/errorlist_check.py` `norm()`: OCR aliases `vl`↔`vi`, `v`↔`y` (the `subvi`/`subvl` variant, review
  `archive/peer/2026-10-01-c126-4-elocr.md`); add-only, with a self-test over a few recorded Error List files.
- Log the unqueued gate refusal `tools/bench/cards/guard_card.log:549` (card 126-3, `flags.labview none` refused
  `tools/stagexec.py`) with `py tools/gate_fp.py log --gate guard_card --cmd ... --why "tools/bench/cards/guard_card.log:549" --card 127-2`.
- If cheap: add `selftest_fs_c126.py` to `protocol.OFFLINE_SELFTESTS`; add the measured Wire method ids (`6370C05`,
  `6370C08`, `6370C0B`, `6370C0D`, `diag_c126_2_op.log:8-16`) and FS method `3578B800` to `docs/NAMES.md`.

## Return
`result/1`: per step PASS/FAIL, end-of-replay census and cdiff, self-test counts, files changed with md5. Return at the
first unexpected result.
