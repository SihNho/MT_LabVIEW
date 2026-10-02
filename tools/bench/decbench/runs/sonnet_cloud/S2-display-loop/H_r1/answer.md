**Yes, NEXT is the right next act. Keep it.**

**Why it is the right act**

- **It goes after the largest measured cost.** At 15 beads, the frame loop spends about 9.4–10.9 ms per frame on #1359. Its only consumer is the display indicator #8323 (`docs/d1-loop12-17-split-plan.md:1402-1409`). Nothing on that path reaches the file writer, the motors or the kernel (`:1405`). The tracking loop is compute-bound at 13.1–16.7 ms per frame against the camera's 11.1 ms (`STATUS.md:110`).
- **The other levers are already ruled out by measurement.** The parallel For loop lost 13 % more frames (`:1391-1394`). The kernel swap changed nothing (`STATUS.md:165`). Minimizing the panel saved only about 16 % (`STATUS.md:155`), because it skips the drawing but not the Median and FIR maths.
- **It keeps rule 1a.**
  - At N = 1 the gated copy behaves exactly like the original (`:1415`, `:1457`).
  - Magnet2Force, which feeds the stored history, was correctly left ungated (`:1444-1449`).
  - The copy is not accepted until a replay of recorded frames gives bit-identical numbers (`:1432-1434`).
- **It follows the steering card.** `steer_95` requires a deliverable build or run as the next act, not tooling (`tools/bench/cards/steer_95.json`). A diagnosis on the stage's own artefact counts as that.
- **It reads instead of guessing.**
  - The failure is ExecState going from 1 to 0 right after `move_into_frame` (`:1480-1482`). The two reviews offered only arithmetic guesses about leftover cut wires (`:1483-1484`).
  - The plan correctly refuses a third guess (`:1486-1487`). Instead it saves the broken file, reads the Error List, reads the broken wires, and runs Remove Bad Wires on a scratch copy (`:1489-1494`).
  - This is the project's own rule: when a failure has been explained by guessing twice, the next step is to read it from the machine (CLAUDE.md, "When a diagnosis is GUESSED twice").
  - It also produces a saved file, which the "split big work" rule requires (`STATUS.md:59`).

**Caveats (none of them change the verdict)**

1. **The user's decision is still open.** D-2026-09-26-02 asks whether the force graph may refresh only every N frames, and it is still unanswered (`tools/bench/decisions_pending.json:143-156`). If the user says no, the default becomes N = 1 and the speed-up is lost (`:1419-1420`). Proceeding under the stated assumption is what rule 2c prescribes, and the work is not wasted either way, because the N = 1 build is still the rule-1a anchor. But the chat should get this question answered before the ABBA timing run (`STATUS.md:66-67`).
2. **The speed-up has no measured upper limit yet.**
   - A review estimated #1359's own share at only about +450 µs per bead (`:1398-1399`).
   - The ring insert and Magnet2Force stay ungated, so the full ~10 ms will not all come back.
   - The pass threshold of 0.8 × A may still be met, but nobody has measured whether it will.
3. **Pre-decided 207 and 208 do not exist.** The plan stops at 206 (`:1438-1501`). The question's "205–208" range is off by two.
4. **The card needs all three peers.** It must list `hypothesis`, `outcome` and `priorart` (`STATUS.md:61`). Leaving `priorart` out is what blocked card 97-4 (`STATUS.md:78`).

VERDICT: keep NEXT
NEXT ACT: Re-run `stage_d1_fgate.py` to E3 on a fresh S1 byte copy, save the broken copy by `gui_save` as `D1_s1_fgate_BROKEN_<ts>.vi`, then read its Error List uids, its broken wires and their owners, and ExecState after Remove Bad Wires on a scratch copy, so judgement can choose between a `move_into_frame` fix and a structure change.