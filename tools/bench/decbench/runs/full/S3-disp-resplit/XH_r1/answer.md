**No, change NEXT.** The fixes 214(b)–(d) ask for are worth doing, but NEXT then ends in another all-or-nothing run of all 47 build steps. The project's split rule forbids that after a stage has ended without a saved file, and this stage has now done so five times.

**Evidence**

- **Five runs, no file.** The display-loop build script `stage_d1_disp.py` has run five times in LabVIEW. Every run ended FAIL with `"artefacts":[]`:
  - `tools/bench/stage_d1_disp.log:62`
  - `stage_d1_disp_r2.log:78`
  - `stage_d1_disp_r3.log:90`
  - `stage_d1_disp_r4.log:111`
  - `stage_d1_disp_r5.log:477`

  Each one stopped at the gate that compares the real graph with the simulation after each step, in a different place each time: step 2, a tunnel, step 4, and step 26 (`r2:57`, `r3:69`, `r4:90`, `r5:456`).
- **The rule this breaks.** A stage that ends without a saved file means the next cycle's first act is a one-page decomposition plan: sub-steps, each with its saved file name and pass criterion. "A full-length retry under a new file name … is forbidden" (`CLAUDE.md:486-490`). A step is not done until it has left a file, and the next step starts from that file in a fresh LabVIEW instance (`CLAUDE.md:481-483`).
- **NEXT keeps the same shape.** NEXT asks for "ONE record-mode run" to produce `D1_s1_disp_<ts>.vi` (`STATUS.md:57-60`). Record mode saves only when every step matches (`docs/d1-loop12-17-split-plan.md:1787`), so it can again leave nothing behind.
- **Memory limit.** In run 4, LabVIEW was already at 594.6 MB after step 4 of 47. The stop limit is 700 MB, so run 5 could only afford checks at a few checkpoints (`r5.log:16-18`). Splitting into fresh instances resets memory and lets each piece be checked after every step.
- **Broken-by-design saves are allowed.** A broken-by-design intermediate may be saved by GUI Ctrl+S (`CLAUDE.md:493`). So needing ExecState 1 only at the end is not a reason to keep one monolithic run.
- **The open user question rests on the wrong reason.** D-2026-09-27-01 asks whether to retry the same build, and recommends yes because "each run gets further" (`decisions_pending.json:164-170`). That is the "felt" progress rule 3 rejects in favour of a machine trigger.
- **What stays valid.** The one-source half-wire rule is still unmeasured (`plan:1790-1793`). The WARN rule and the simulator fixes (`plan:1794-1801`) apply to any split, so they remain inputs to the new plan.

**What the next cycle should do**

1. **Write the decomposition plan first.** Cut the 47 build steps at their natural boundaries, for example:
   - (a) create the display While/For loop, the Wait, the `Display period` control and the #25261 check (step 25 is where r5 had already reached);
   - (b) the moves, then save;
   - (c) the local reads/writes and rewiring, clean-up, and the end checks, then the final save by script.

   Each piece names its `claudeDev\D1_s1_disp_<a|b|c>_<ts>.vi` file and its pass criteria.
2. **Get it prior-art reviewed once.** Do the 214(b)–(d) work as the offline preparation it already is.
3. **Run sub-step (a) in the same cycle and save its file.** This keeps the deliverable first.
4. **Rewrite D-2026-09-27-01** so the user is asked about the split plan, not about a full retry.

VERDICT: change NEXT
NEXT ACT: Write a one-page decomposition plan that cuts the 47-step display-loop build into saved sub-steps, get it prior-art reviewed once, then run sub-step (a) from `D1_s1_copy.vi` in a fresh LabVIEW and save `claudeDev\D1_s1_disp_a_<ts>.vi`, with the 214(b)–(d) fixes as offline preparation.