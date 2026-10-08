# c148-a3-1-unmask-clockstamp

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.8264  in 58 / out 16443 / cache-create 115355 / cache-read 2872350  (198s, 39 turn(s))
- **date:** 2026-10-08 16:27:38
- **outcome:** ANSWERED (202s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

Hypothesis review, card 148-a3-1. Attack the claim below. Read-only; project dir is the working directory.

CONTEXT
tools/bench/diag_c148_a2_3_unmask.py (card 148-a3-1 step 3) runs the same calls with the HEAD (07202624, md5 61d6f590) and the
disk (dcd45aba) tools/stage_prerun.py, each in its own child interpreter, the module built from the given source with
__file__ = the main tree's tools/stage_prerun.py (so data paths are identical). Log: tools/bench/diag_c148_a2_3_unmask.log.
- 4 rebase cases (p3b2_A/B on graph_ring_p3b1_20261002_073225, simulate; s03_A/B on graph_ring_p4s02_20261003_112505,
  simulate=False), the provisional base restored from plan_ring_p3b2_in.json / plan_ring_p4_s03v18_in.json: all EQUAL
  (log lines 89/89 and 4/4, both ok=True).
- c106e_noX17 (`main(["--prerun", tools/recipes/stage_d1_disp.py, "--no-record", "--from-step", "33", "--base", dispA])`,
  x17_gate replaced by a stub returning ok): both rc 1, 89/89 lines, gate summary 22 PASS / 1 FAIL (X5) / 6 WARN, but marked
  DIFFERENT. The first differing line (index 55) is:
  HEAD 'FACT  ExecState [after all rows, BEFORE RBW (recorded)] D1_s1_disp_20261008_161939.vi = <dry:g.exec_state>'
  DISK 'FACT  ExecState [after all rows, BEFORE RBW (recorded)] D1_s1_disp_20261008_162206.vi = <dry:g.exec_state>'
  The script's norm() (diag_c148_a2_3_unmask.py, function norm) replaced temp dir names but NOT a yyyymmdd_hhmmss clock stamp;
  the script printed only the FIRST differing line, so lines 56..88 were not shown.

CLAIM UNDER ATTACK
"The c106e_noX17 DIFFERENT verdict is a defect of my comparison script (the dry scratch VI name carries the run's wall clock,
two child runs ~2.5 min apart), not a behaviour difference between the HEAD and disk stage_prerun.py; after normalising
\d{8}_\d{6} the two outputs are identical. Also: with X17 skipped, E1 of selftest_stage_prerun_c106e would still FAIL at X5
at HEAD too, i.e. X17 masks an X5 failure that predates cycle 148."

WHAT I WANT FROM YOU
1. The strongest reason the claim is wrong - in particular, could a cycle-148 edit of stage_prerun.py (lines :592, :848 dry
   input-graph gate `dry_read_only`; :3150 sha256 pin; :3415 offline_run_of; :3433 check_cap; :4474 record_started; compare
   `git diff HEAD -- tools/stage_prerun.py`) change any gate line of a --prerun --no-record run AFTER index 55, hidden because
   only the first differing line was printed?
2. An alternative explanation of the evidence.
3. What observation would falsify the claim.
4. The cheapest discriminating test with no LabVIEW and no tool edit (only tools/bench/diag_c148_a2_3_unmask* may be edited).
End with one line: VERDICT-LINE: claim REFUTED | claim STANDS | claim UNDETERMINED - <one sentence>.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**The claim is refuted on its second half, and the first half is unproven.** "X17 masks an X5 failure that predates cycle 148" is contradicted by a log that already exists. The c106e_noX17 case did not run E1's configuration at all, so its HEAD-vs-disk comparison doesn't close review item 2(b) whatever the timestamp turns out to explain.

## 1. Strongest reason the claim is wrong

**The X5 FAIL comes from the comparison script. It was not there before cycle 148, and HEAD does not have it.**

- **A run from before cycle 148 shows X5 passing.** `tools/bench/s4_c106e_e1_full.log` (2026-10-03 07:48, same argv, fresh process) has:
  - `:88` `PASS X5 … ops 7 vs plan wire rows 0 + stageplan wiring real ops 7 among ops 34.. (PART-B from_step)`.
  - `:86` and `:98`: the only failure is **X17**.
  - `:97`: the dry ran on `graph tools/bench/sim/disp/graph_dispA_step33.json`, first mutation `Stage._op wire_branch`, coverage 58/70.
- **Your child run looks different.**
  - `diag_c148_a2_3_unmask.log:39`: X5 counts **ops 19**, which is the full recipe's wiring count (compare `diag_c103_prerun.log:136`).
  - `:41`: the dry ran on **`par1359_95_graph.json`**, first mutation `Stage._op gate`, coverage **56**/70.
  - So the recipe ran in full mode, not Part-B.
- **Mechanism: the recipe reads its mode from `sys.argv`, and the child never set it.**
  - The recipe reads `--from-step` and `--base` from `sys.argv[1:]` (`tools/recipes/stage_d1_disp.py:26-27,86`).
  - `stage_prerun.main(argv)` only parses the `argv` it is given (`stage_prerun.py:4930`, "pass through to the recipe's own sys.argv" at `:4928`). It never assigns `sys.argv`. The only `sys.argv` in the file is that comment.
  - In your child, `sys.argv` is `[diag…py, --child, TAG, src, out]` (`diag_c148_a2_3_unmask.py:96-97,138`).
  - Result: the recipe ran full (19 ops, base graph), while the X5 check was told `from_step=33` through `rest` (`stage_prerun.py:5036`). That mismatch is the X5 FAIL.
  - It is the same class as the in-process X5 artefact recorded in `diag_c130_4_c128b.log:8-10`.
- **"Masks" is the wrong word anyway.** X5 is evaluated independently of X17 (`stage_prerun.py:2947-2988`, no fatal stop). A real E1 prints its X5 line next to X17's, and that line is PASS.

**A second configuration difference: the log directory.** `LOG_DIR` is read when the module is imported (`stage_prerun.py:124`). Your child sets `PRERUN_LOG_DIR` only afterwards (`diag…py:66` vs `:92`). So both children read the live `tools/bench`, not an empty directory. That directory feeds X10 meter records (`:1905`), `last_failed_run_after` (`:3293`) and the scratch-run scan (`:4543`). It changes between the two child runs, which were about 2.5 min apart, and the diag's own log sits in it.

**On your question about the cycle-148 edits:** none of the lines you list should touch a `--prerun --no-record` gate line when the configuration is correct.
- `:848` only changes the dry-graph gate's detail when no graph is found (`G is None`) and the recipe is read-only.
- `:3150`, `:3415`, `:3433` and `:4474` are on the launch-gate / recording path.

I could not run `git diff HEAD` (no shell in this role), so I cannot rule out other changed sections. That is unverified.

## 2. Alternative explanation of the evidence

What both children measured was the wrong configuration (full recipe, live log directory), not E1. Under that configuration, lines 56..88 may differ in the timestamp only, or also in what the X10 / failed-run scans saw: the two children ran at different times against a log directory that changed in between. The printed summary cannot tell these apart.
- Only the first differing line was printed.
- The gate tally `22/1/6` and the tail are printed from **HEAD only** (`diag…py:155-164`). The brief's "both … 22 PASS / 1 FAIL / 6 WARN" is not supported by the log.

## 3. What would falsify the claim

- **The X5 half is already falsified** by `s4_c106e_e1_full.log:88`.
- **The timestamp half would be falsified** by a rerun with `\d{8}_\d{6}` normalised in which any line still differs, for example an X10 FACT, WARN or failed-run line.
- **Rule-compliance note:** `launches.jsonl:1549` shows `diag_c148_a2_3_unmask_r2.log` launched at 16:23:16 with the already-patched `norm()` (`diag…py:57`), and that log does not exist.
  - Brief `brief_148-a3-1.md:21` says "any difference -> RETURN".
  - `:24` says "Never … Retry after a first unexpected result."
  - So the "identical after normalising" part is a prediction, not a measurement.

## 4. Cheapest discriminating test (no LabVIEW; edits only in `diag_c148_a2_3_unmask*`)

Run the c106e case in its own child per variant, with no rebase cases first.
1. Set `PRERUN_LOG_DIR` to a fresh temp directory in the child's environment **before** the module is built (or set `m.LOG_DIR` after building it).
2. Set `sys.argv = [SPF, "--prerun", recipe, "--no-record", "--from-step", "33", "--base", part["file"]]` before `SP.main(...)`.
3. Keep the X17 stub. Normalise `\d{8}_\d{6}`. Print the number of differing lines and every one of them, plus each side's own gate tally.

Prediction if the code is equivalent: both sides show X5 PASS (`ops 7`), the `graph_dispA_step33.json` dry graph, 0 FAIL / RESULT PASS, and 0 differing lines. Any remaining difference is a real code difference and the card returns.

VERDICT-LINE: claim REFUTED - X5 passes on a pre-148 fresh-process E1 (`s4_c106e_e1_full.log:88`); the diag's X5 FAIL comes from not setting `sys.argv` (full recipe ran: ops 19, `par1359_95` graph) and from setting `PRERUN_LOG_DIR` after import, so this comparison says nothing about HEAD vs disk on E1's path.

## Sources

(extract from answer)

## What was done with it

Card 148-a3-1 (material). Accepted: claim REFUTED. Verified on disk: `tools/bench/diag_c148_a2_3_unmask.log` shows X5 `ops 19`, dry graph `par1359_95_graph.json`, coverage 56/70 (full-recipe mode), and the gate tally line is printed from HEAD only; the review's reading of `sys.argv` and the import-time `PRERUN_LOG_DIR` matches the script as run. The 16:23 `_r2` launch was REFUSED by guard_peer before it ran (no log), so no rerun happened. FIXED: c148-a3-1-unmask-clockstamp - tools/bench/diag_c148_a2_3_unmask.py:65 - the c106e case now runs in its own child per variant with PRERUN_LOG_DIR fresh in the child env before import, sys.argv set to the recipe argv, clock stamps normalised, both sides' gate tallies and up to 20 differing lines printed. The revised script is NOT run inside this card (card chat-P2: return at the first unexpected result); the four suites (step 2) and the stale-worktree removal were not run either. Returned to the judgement session.
