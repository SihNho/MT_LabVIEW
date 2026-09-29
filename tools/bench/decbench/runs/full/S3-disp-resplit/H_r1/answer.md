**No.** NEXT should change. The fixes it lists are reasonable, but ending in one all-or-nothing run of all 47 steps breaks the project's own re-split rule, and that rule has already been triggered.

**Why the NEXT act is wrong**

1. **The re-split trigger has fired.** When a stage "ends without a saved artefact", the next cycle's first act must be a one-page decomposition plan. A full-length retry is forbidden (`CLAUDE.md:486-490`). Every attempt at this stage has ended with nothing saved:
   - Cycle 100, run 1: stopped at E1 parity (`docs/d1-loop12-17-split-plan.md:1752`).
   - Cycle 100, run 2: stopped at op 2 (`:1753-1756`).
   - r4: stopped at op 4 over memory (`tools/recipes/stage_d1_disp.py:18`).
   - Cycle 101, r5: did ops 1–25 and stopped in op 26. "S1 is unchanged; NO FILE" (`STATUS.md:64`, plan `:1789`).

   NEXT still ends in "ONE record-mode run" of all 47 ops (`STATUS.md:60`, plan `:1801`).
2. **The recipe can only save at the very end.** In record mode, any step difference means nothing is saved (`stage_d1_disp.py:12-13`, `:80-87`). The only save is after E3 at ExecState 1 (`:106-111`). So another failure at op 30–47 leaves no file again, which is exactly the outcome the rule exists to prevent (`CLAUDE.md:481-485`: one saved file per natural stage, rewiring in batches of 10–15 rows).
3. **Resource headroom is thin.** The 700 MB memory stop drove the checkpoint-only reads (`stage_d1_disp.py:15-18`). r5 was already at 615.6 MB by op 8 (`stage_d1_disp_r5.log:170`), with about 54.7k handles against a fresh baseline of about 31.5k (`STATUS.md:31`). A shorter run with a fresh LabVIEW instance per step lowers that risk.
4. **Both escalation tries are used, and the user has not answered.** D-2026-09-27-01 is still `open` (`tools/bench/decisions_pending.json:161-174`). It asks the user to approve "retries the same build", which describes a full retry.
5. **The failure point is known, so a split is cheap.** r5's only step difference (at step 12) had healed by step 24 (plan `:1789`). The step 26 bug is fixed (`STATUS.md:64`). Steps 1–25 are therefore a natural first sub-stage that can already be saved.
6. **Broken intermediate files are allowed.** They may be saved with GUI Ctrl+S (`CLAUDE.md:493`), so a sub-stage does not need ExecState 1.

**What to keep:** the 214(b)–(d) simulator work (half-wire measurement, WARN rule, tunnel-flip seed fix, plan_disp md5 decision) is still needed. It just becomes a prerequisite of each sub-stage rather than of one 47-op run.

**What the next cycle should do**
1. Write the decomposition plan for `stage_d1_disp.py`:
   - **Sub-stage 1:** steps 1–25 (structures and moves), saved as `claudeDev\D1_s1_disp_s1_<ts>.vi`.
   - **Following sub-stages:** steps 26–47 (local reads/writes and rewiring) in batches of 10–15 steps. Each one starts from the previous file in a fresh LabVIEW instance and saves its own file.
   - **Each sub-stage** has its own pass check (the step comparison for its range) and its own md5.
   - The final E1/E3 checks (ExecState 1, cdiff equal to the 21 open rows plus the added objects, #25261 reads False) apply only to the last file.
2. Get one prior-art review of that plan.
3. Run sub-stage 1 and save its file.
4. Restate D-2026-09-27-01 to the user as "split and continue" rather than "retry as planned".

VERDICT: change NEXT
NEXT ACT: Write and prior-art-review a one-page decomposition plan that splits `stage_d1_disp.py`'s 47 ops into sub-stages, each saving its own `claudeDev` file (ops 1–25 first, then batches of 10–15), then run sub-stage 1 so it leaves a file.