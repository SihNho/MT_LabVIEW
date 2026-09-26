# Cycle 102 (firefighter, fable/low) - edit of tools/recipes/stage_d1_disp.py before its ONE record-mode run

The recipe was reviewed as `novel` in archive/peer/2026-09-27-priorart-c101-4-disp-record2.md for sha 3c39722d3240 and
ran r5 (tools/bench/stage_d1_disp_r5.log): ops 1-25 of 47, ONE step difference at k12 (`dangling_sim_only [11365]`,
LoopTunnel #11363's inner terminal, healed when op 23 deletes #11363), then a stop IN op 26 on the local-read index bug
that card 101-5 fixed (stagekit.create_local_read by label). S1 unchanged, nothing saved.

## What changed since that review (PD214(c)/(d), docs/d1-loop12-17-split-plan.md:1794-1801)
1. `tools/stagexec.py`: new `classify_step_diff(plan, last_act, d)` - a step difference made ONLY of dangling terminals
   (`dangling_sim_only` / `dangling_real_only`) whose uids NO later plan action names (ints collected from every later
   action, read from the plan file) is class `warn`; any terminal / edge / unbound entry, or a later reference, is `fail`.
   Executor.run (record mode) stores `class` and `later_refs` on each recorded diff and logs `RECORD WARN` / `RECORD
   STEP-DIFF`. Self-test gates T39e/T39f.
2. `tools/stagesim.py` `_move_one`: an outside sink whose wire the only-source rule DELETED now seeds the undirected-tunnel
   flip (PD214(d)1). The rule in force stays `{"constant": "delete", "default": "keep"}` (review c101-5-onlysource refuted
   both class rules), so this fix is latent for the display plan; the re-simulated plan is content-identical (diag_c101c_resim
   R6b). Self-test gate G56.
3. The recipe: after the run, diffs of class `warn` are logged as `STEP-WARN` facts and do NOT block; any `fail` diff keeps
   the card-101-4 path (every diff listed, E3-INFO cdiff, E1 FAIL, nothing saved). The end gates W1 (RBW only pre-existing
   wire uids, no lost edge, no termless wire), E2 (ExecState 1) and E3 (cdiff == the 21 open rows) decide the save exactly as
   before. Stage task label "cycle 102 firefighter". The `--retry-card` launch line in the docstring was dropped (a new
   cycle's retry count starts at 0).

## Why (PD214(c), decided by the cycle-101 judgement)
The per-step comparison exists to keep symbolic ids bound correctly; a sourceless half-wire carries no data (rule 1a).
The k12 difference is exactly that shape and op 23 removes the tunnel. Nothing else in the recipe changed.

## The plan it executes
tools/bench/sim/disp/plan_disp.json (md5 7c432e1b before this cycle's re-sim; content-identical to r5's b535071e at every
step, diag_c101c_resim run 2 REPLAY facts) from the unchanged stageplan_disp_r4_open.json.
