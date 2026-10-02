**Yes, keep NEXT.** Reading why the gated copy breaks, then rebuilding it, is the right next act. Some caveats follow.

**Why it is the right act**

1. **It targets the biggest frame-loss cost found so far.**
   - At 15 picks over 120 s, the S1 copy loses about 3,400 frames (`STATUS.md:86`).
   - Most of that per-frame time (about 9.4–10.9 ms at 15 beads) goes to one live graph, #8323 'Force (pN) vs Extension (nm)' (`docs/d1-loop12-17-split-plan.md:1402-1409`).
   - That graph feeds no data file, no motor or instrument call, and no kernel input (`:1405`).
   - Losing no frames is requirement R4 (`docs/goalmap.json:48-51`). It is also the user's own data-quality rule 1c.
   - The alternative lever, the parallel For loop, has already been measured and rejected (`:1390-1394`).
2. **It keeps the computation the same (rule 1a).**
   - Only how often the graph is redrawn changes.
   - At N = 1 the copy reproduces the original exactly (`:1415`, `:1457`).
   - Acceptance needs a numeric replay first (`:1432-1434`).
3. **It does what the latest steering card requires.** The card asks for "a deliverable build or run", not tooling (`tools/bench/cards/steer_95.json`). Gating the display is milestone M7's done-when ("display gated outside the frame budget", `docs/goalmap.json:160`).
4. **It reads the cause instead of guessing a third time.**
   - The last stage run ended with ExecState 0 after the moves and nothing saved (`:1480-1482`).
   - The two reviews offered two explanations, both untested (`:1483-1487`).
   - So reading the Error List, the broken-wire owners and a Remove Bad Wires check is the right step. CLAUDE.md's "when a diagnosis is GUESSED twice, build the reader" says the same.
   - Saving the broken intermediate (`STATUS.md:59`) also meets the "a step is not done until it has left a file" rule. The last stage ended with no file.

**Caveats (none of them change the act)**

- **Pre-decided 207 and 208 do not exist.** The plan's numbered items stop at 206; the next heading is `## OPEN` (`:1502`). NEXT really rests on 205 and 206(h).
- **The user hasn't answered the default-N question.** D-2026-09-26-02 is still open (`tools/bench/decisions_pending.json:143-156`). Proceeding with default 9 is allowed under rule 2c (`STATUS.md:66`). N = 1 is always available on the panel, so the build is useful either way.
- **The gate is built on an S1 copy, not the current bed.**
   - It is built from a copy of `D1_s1_copy.vi` (`:1421`).
   - The current bed is `D1_l2_a1_20260925_235224.vi` (`STATUS.md:54`).
   - Once it is accepted, it still has to be carried onto the bed. The plan should record that port as its own step.
- **Owed tooling waits.** The `loss_usd` and audit fixes (`STATUS.md:64`) should come after this act, not before (`steer_95.json`).
- **Gate edits on ExecState from now on.** The tool's own self-test never checked ExecState or leftover wires (`:1487-1488`). Retrospective 97 requires an ExecState read after every diagram edit (`STATUS.md:62`), so the rebuild should do that.

VERDICT: keep NEXT
NEXT ACT: Re-run `stage_d1_fgate.py` up to the point where ExecState went to 0, on a fresh S1 byte copy; save the broken file by `gui_save`; read its Error List, broken-wire owners, and the Remove-Bad-Wires ExecState on a scratch copy; then judgement chooses a `move_into_frame` fix or a structure change, and the stage, the timing comparison and the N = 1 replay follow.