# c109c-resim-disp-baseline

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $0.9261  in 12 / out 7642 / cache-create 84203 / cache-read 498146  (84s, 14 turn(s))
- **date:** 2026-09-27 15:30:39
- **outcome:** ANSWERED (88s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

FAILED PREDICTION - offline diagnostic tools/bench/diag_c109c_resim.py (card 109-3), log tools/bench/diag_c109c_resim_pre.log.
No LabVIEW involved: the script re-simulates three finalized stage plans with the CURRENT tools/stagesim.py (BEFORE the card's op_wire
change) and compares each with its recorded final.

Prediction (script docstring): l2a2, disp and l2a3 re-sims reproduce their recorded end_cdiff_rows.
Observed: l2a2 8 rows == recorded, l2a3 6 rows == recorded, but disp: 6 rows vs the 21 recorded in tools/bench/sim/disp/plan_disp.json
(finalized.at 2026-09-27 02:15:11). extra [] - the 6 are a subset of the 21; final/open_rows_match True in both.

My claim: this is a baseline error in MY diagnostic, not a simulator regression. plan_disp.json was finalized BEFORE card 106-3 changed the
finalize graph's cdiff inputs (stagesim.py:1166 `cdiff_inputs`, "card 106-3: the finalize graph = the E3 inputs": node_labels_default
626 labels + fs pairs). tools/bench/sim/c106c_resim_summary.json:65-66 already records exactly this re-sim of plan_disp: old_finalize_rows_n
21 -> new_finalize_rows_n 6, and its end_rows (from :13) are the same 6 keys the pre-fix re-sim produced
(8323 'Force (pN) vs Extension (nm) ', 8764 y, 27716 index, 28180 half-width, 29009 left rank, 29009 right rank;
tools/bench/sim/c109c_pre/plan_disp.json:856-863). The correct no-regression baseline for disp is therefore the c106c record (6 rows),
and the card's op_wire change is judged by pre-fix vs post-fix equality, not by the 02:15 file.

Already ruled out: input drift (plan_in md5 7eec1754 and base md5 143ad46c equal the recorded ones, diag_c109c_resim_pre.log);
the op_wire change (this run is BEFORE it, stagesim self-test 64/0 in tools/bench/selftest_stagesim_c109c_pre.log).

Files: tools/bench/diag_c109c_resim.py, tools/bench/diag_c109c_resim_pre.log, tools/bench/sim/disp/plan_disp.json,
tools/bench/sim/c106c_resim_summary.json, tools/bench/sim/c109c_pre/plan_disp.json, tools/stagesim.py (simulate, cdiff_inputs).


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict: I could not refute the claim. It holds on the evidence.** The 21-row number in the 02:15 `plan_disp.json` comes from the old finalize rule, not from a simulator regression. What is still unproven is narrower: the pre-run only shows the current simulator's result agrees with the 07:22 re-sim on the 6-row count and the six missing keys. It does not show the step states are unchanged.

**1. The strongest reason the claim could be wrong.** The claim treats the 07:22 re-sim record as the baseline, but that record belongs to the simulator as it stood at 07:22. `tools/stagesim.py` has changed since then (it shows as modified in git, and cycles 107 and 108 ran in between). The c106c run checked that every one of the 58 step states matched the pinned step files (`tools/bench/diag_c106c_resim_final.log:21`, gate R4). Today's pre-run did not repeat that check. `diag_c109c_resim.py:37-41` compares only the end rows, `final`, `open_rows_match` and `open_rows`.

So "6 rows, the same 6 keys" shows agreement on a coarse projection, not that the simulation behaves the same. Only the end rows are compared; the step-by-step row counts and step states were not checked. Everything the files show is also consistent with the claim:
- The recorded plan has no `cdiff_inputs` key under `finalized`. A grep of `tools/bench/sim/disp/plan_disp.json` finds none, while any simulation after card 106-3 writes that key (`stagesim.py:1285`). So the 02:15 file was finalized before 106-3.
- Its 21 end rows fit the old rule: the old "legacy" match needed the end rows to equal all 21 open rows, and the file records `open_rows_match` true (`plan_disp.json:856-877`, `:972`).
- The c106c run recorded that exact 21 → 6 drop (`c106c_resim_summary.json:65-66`).

**2. An alternative explanation of the same evidence.** Some change to `stagesim.py` or to the operation models after 07:22 altered the intermediate states of the disp simulation. The end rows still come out as the same 6 because the finalize graph only looks at labelled terminals and fs pairs.

Nothing in `diag_c109c_resim_pre.log` rules this out. The last-step md5 differs (recorded `7e307ba5`, re-sim `a588cb26`), but that proves nothing either way: each step file embeds the previous step's path (`stagesim.py:1187`), and the output folder is different, so the hashes would differ anyway.

**3. What would falsify the claim.** Any of these:
- A re-simulated step state (the `state` field only) differs from the pinned `tools/bench/sim/disp/step_NN_*.json`.
- The per-step row counts differ from `c106c_resim_summary.json:103-335` (rows_per_step).
- `plan_disp.json` no longer has md5 `c7d80fc9…`, the value pinned in `c106c_resim_summary.json:5`.

**4. The cheapest test that separates the two.** Re-run the existing script `tools/bench/diag_c106c_resim.py` unchanged, before the op_wire change. It is offline and took 64 s. It already checks R2 (end rows equal the 6 class 1–3 rows), R4 (all 58 step states equal the pinned files) and R5 (`plan_disp.json` and its step files byte-unchanged).
- **All PASS:** the claim is fully established. The 6-row c106c record is the correct baseline and the diagnostic's `rows_record` override (lines 26-29, not yet wired in at line 46) is legitimate.
- **R4 fails:** the alternative holds, and a change after 07:22 needs its own review before op_wire is judged.

For the op_wire change itself, "pre equals post" should compare step states in the same R4 style, not just end rows. A wiring change can alter a state without changing the end rows.

**What would change my mind:** an R4 or R5 failure in that re-run.

No external claims are involved: this is entirely about the project's own Python, so there was nothing to search and no URLs to cite. I did not run anything.

## Sources

(extract from answer)

## What was done with it

Accepted (card 109-3 material session, 2026-09-27 15:3x), including the narrowing in §1/§4. `diag_c106c_resim.py` was NOT re-run
as the reviewer's cheapest test, because it overwrites `tools/bench/sim/c106c_resim_summary.json` (its :77-78), the very record under
test, and the op_wire change was already applied. Instead its R4 check was built into `tools/bench/diag_c109c_resim.py` (:36-42, :58-69,
:82-89): for l2a2 and disp, the PRE-FIX re-sim step states are compared with the pinned step files the recorded plans name, and the
post-fix states with both; for l2a3, pre-fix vs pinned must be equal and post-fix may differ from pre-fix only at the two wire steps.
The disp end-row baseline is the card-106-3 record (`c106c_resim_summary.json:13`, 6 rows), stated in the script docstring (:6-8).
Result: see `tools/bench/diag_c109c_resim_post.log` and `tools/bench/cards/result_109-3.json`.
