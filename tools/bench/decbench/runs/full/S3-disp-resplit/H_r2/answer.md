**No.** NEXT picks the right deliverable, but it retries the build in the wrong shape. The display-loop stage has now ended with no saved file several times, and the project's own rules say that the next act after that is to split the stage, not to run all 47 ops again.

**Why the target is right**
- The user chose the display loop (plan PD210, `docs/d1-loop12-17-split-plan.md:1568-1589`).
- The lever is measured: the moved computation costs at least 7.94 ms per frame at 15 beads (`:1667-1670`).
- The outcome review's steer requires a deliverable build first (`:1773-1775`).

**Why the shape is wrong**
1. **The stage keeps ending without a file.** Cycle 100 made two runs and saved nothing (`:1751-1756`). Cycle 101's r5 run did ops 1–25 of 47, stopped inside op 26, and returned `"artefacts":[]` (`tools/bench/stage_d1_disp_r5.log:457,477,479`). STATUS also says "NO FILE" (`STATUS.md:64`).
2. **The rule for that case is explicit.** When a stage ends without a saved file, the next cycle's first act is a decomposition plan: sub-steps, each with its saved file name and pass criterion. A full-length retry is forbidden (`CLAUDE.md:486`). Every step must leave a file (`CLAUDE.md:481`). NEXT instead prescribes "ONE record-mode run" of all 47 ops, saved only if everything matches (`STATUS.md:60`, `:1787`, `:1801`). That is the same all-or-nothing shape that has produced no file three times.
3. **Both escalation steps are used up.** Decision D-2026-09-27-01 is still open with the user (`tools/bench/decisions_pending.json:161-174`, `STATUS.md:65`). A split plan is also the better thing to show them than a fourth attempt at the same long run.
4. **Part of the work is already proven.** Ops 1–25 ran against LabVIEW, and their one step difference healed by k24 (`:1789`). Saving that prefix gives the user a file to open and a fixed starting point for the rest. Saving a broken intermediate through the GUI is allowed (`CLAUDE.md:493`).

**What stays from NEXT:** the offline half-wire measurement (214(b)), the WARN rule (214(c)) and the tunnel-flip seed fix (214(d)). They are offline fixes the later steps need anyway.

**Proposed split**
- **(a)** Ops 1–25 (create the display loop, the hidden indicators and the locals). Save `D1_s1_disp_a_<ts>.vi` with its md5, by GUI save if it is broken.
- **(b)** Ops 26–47 (local reads and the moves) in batches of 10–15. Each batch starts from the previous file and saves its own.
- **(c)** Final end gates: ExecState 1, cdiff equal to the 21 open rows plus the added objects, #25261 reads False, then a script save.

Each sub-step gets its own dry run, pre-run and pass criterion, and the plan gets one prior-art review.

VERDICT: change NEXT
NEXT ACT: Write a one-page split plan for the display-loop stage with a saved file and pass criterion per sub-step (first sub-step: ops 1–25 saved as `D1_s1_disp_a_<ts>.vi`), fold in the offline 214(b)–(d) fixes, then run only the first sub-step in LabVIEW.