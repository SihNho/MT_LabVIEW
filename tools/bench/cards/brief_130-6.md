# Brief 130-6 — finish P3b-1's offline checks, then the P3b-1 scratch run (pin3)

Decisions: PD269 (`docs/d1/ring-p3b.md:20-35`), PD268 (`docs/d1/tooling.md:20-38`), PD264(c)(e), PD265(a).
This is the cycle's LAST dispatch: do the steps in order and return at the first unexpected result.

## Step A — offline (target ≤ 15 min from bind)
1. P3b-1 recipe FS/FU gates (`tools/recipes/stage_d1_ring_p3b1.py:51-52,66`) compare each FS frame's terminal count with
   the simulator's predicted end state read from the finalized plan/pred (f0 0 / f1 16 / f2 18 today — read, never type);
   docstring `:1-11` updated to the 31-action cut. Same predicate in `tools/bench/stage_d1_ring_p3b1_scratch.py`.
2. Run `selftest_stage_prerun_c128b` (edited by 130-5, not yet run) and the stage_prerun self-test suite; list every FAIL
   (c106e E1 = known fp-20).
3. P3b-1 recipe + scratch helper: dry (all 31 ops executed) + prerun PASS, own processes; `--scratch-required` exit code.
4. Prior-art only if the launch gate asks for the new bytes.
Do NOT start Step B unless 1–4 all PASS.

## Step B — LabVIEW scratch run (target ≤ 40 min)
5. Scratch `pin` run of the P3b-1 helper on a dated byte copy of the bed (`claudeDev\D1_ring_p3a_20261001_180540.vi`,
   md5 4dfa44aa…), log `tools/bench/stage_d1_ring_p3b1_scratch_pin3.log`. **Wait for it in-turn** — quote and obey
   `.claude/agents/material.md:92-98`: never end your session while it lacks `BGRUN END|TIMEOUT` (129-2's agent exit
   killed its run). Use `py tools/wait_logs.py` ticks.
   Predictions (state them in the log before the run): every recipe gate PASS, including every new crossing tunnel named
   as the simulator predicts (PD265(a): `current image number` on the BufNum net); per-frame counts as Step A; measured
   peak memory ≤ the pred's `memory_pred` (663.4 MB).
6. Scratch Error List: `errorlist_check.py --count-only --role scratch`; prediction = the pred's predicted count (or its
   named alternative). Scratch VI deleted, LabVIEW closed and verified gone.
7. If the card is still under 55 min since bind: write the measured census into `plan_ring_p3b1_pred.json` by script
   citing the scratch log line (PD264(c)), then recipe dry + prerun again. Otherwise return with 7 undone and say so.
The real recipe is NOT launched in this card.
