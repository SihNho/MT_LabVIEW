I've finished reading and the verdict is written. In short: NEXT should change. Another full 47-op run with no saved steps breaks a standing project rule and has a memory problem.

**Why another full run is the wrong next act**

1. **The project's own split rule applies.** CLAUDE.md:473-490 says that when a stage "ends without a saved artefact", the next cycle's first act is a **decomposition plan** for that stage: sub-steps, each with its own saved file and pass test. Repeating the whole thing "under a new file name is forbidden". It also says "A step is not done until it has left a file". The display stage has now run in LabVIEW four times and saved nothing each time:
   - r2 stopped at op 2 (`tools/bench/stage_d1_disp_r2.log:57`).
   - r3 stopped at its E1 gate (`tools/bench/stage_d1_disp_r3.log:88`).
   - r4 stopped at op 4 (`tools/bench/stage_d1_disp_r4.log:90`).
   - r5 stopped in op 26 (`tools/bench/stage_d1_disp_r5.log:456`, `:477`, with `"artefacts":[]`).

   Cycle 100's two runs saved nothing either (STATUS.md:81-82). NEXT (STATUS.md:57-60, PD214(d), plan:1798-1801) asks for one more all-or-nothing run. Record mode makes it worse: the file is saved "only when every step matches" (plan:1787). One leftover step difference still costs all 47 ops.

2. **Memory may run out.** The recipe notes the error-2 failure at 695 MB, with MEMSTOP at 700 (`tools/recipes/stage_d1_disp.py:13-15`). r5 was already at 647 MB by op 25 (`stage_d1_disp_r5.log:447-449`), and 22 ops plus the end reads were still to come. A single run has no measured headroom. Saving at a few points, with a fresh LabVIEW for each step (CLAUDE.md:477-480), resets memory each time.

3. **The user's go-ahead is still pending.** Both extra tries (Opus max, then Fable low) were used up, and the escalation rule says the card then goes to `decisions_pending` and stops (CLAUDE.md "INTRA-CYCLE ESCALATION"). D-2026-09-27-01, "retry the same build … continue that way?", is still `"status": "open"` (`tools/bench/decisions_pending.json:161-178`). NEXT treats it as answered yes.

4. **The open model question can be split off cleanly.** PD214(b)'s half-wire rule (plan:1790-1793) first comes up at ops 4–5 and op 12. In a split plan it is settled inside one small step instead of risking all 47.

**What still holds:** the design itself (PD212, plan:1607-1689), the 214(c) WARN rule and the tunnel-flip seed fix (plan:1794-1799). They become part of the steps rather than the preamble to one big run.

**What cycle 102 should do instead.** Write a one-page decomposition plan for `plan_disp.json`'s 47 ops, following the split rule's default stages:
- **(a) Structures.** Create the While/For loops, the `Display period` control and the locals. Check the result against the simulator and save by script while it is still runnable (ExecState 1), e.g. `claudeDev\D1_s1_disp_a_<ts>.vi`.
- **(b) Moves**, ops 4–12. Measure the half-wire rule right here. Save with `gui_save` if the file is broken by design.
- **(c) Rewiring**, in batches of 10–15 ops, each saved.
- **(d) The end gates and a scripted save** of `D1_s1_disp_<ts>.vi`, then the ABBA comparison (210(c)).

Run the plan through one prior-art review, then execute step (a) only. Each step starts from the previous step's file. Report the step (a) file to the user with D-2026-09-27-01, rewritten as "continue in saved steps?".

VERDICT: change NEXT
NEXT ACT: Write and prior-art-review a decomposition plan that splits the 47-op display-loop stage into saved sub-steps (structures → moves → rewiring batches → final save), then run only step (a) from `D1_s1_copy.vi` and save its intermediate file in claudeDev.