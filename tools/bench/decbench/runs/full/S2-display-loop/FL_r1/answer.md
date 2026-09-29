No — the NEXT act should change. The diagnosis it prescribes is well-formed, but it repairs a design that is the wrong structure for this project.

**What NEXT prescribes.** Re-run `stage_d1_fgate.py` to E3, save the broken intermediate, read the Error List, broken wires and Remove Bad Wires, then rebuild the gate (`STATUS.md:56-63`). The gate is a case structure inside For loop #1359 plus a second case on the frame loop's body, both driven by `i mod N` (`docs/d1-loop12-17-split-plan.md:1450-1457`).

**Why it is the wrong act.**

1. **The gated work stays on the frame path.** Measurement 96-3 shows the chain feeds only the indicator `Force (pN) vs Extension (nm)`; no path reaches the file writer, a motor call or the tracking kernel (`d1-loop12-17-split-plan.md:1402-1405`). It costs about 9.4–10.9 ms per frame at 15 beads (`:1408-1409`). With the gate, every Nth frame still pays that full cost inside the frame loop, so that frame period still spikes. Since the chain is display-only, it can leave the frame loop entirely.

2. **It rests on an unanswered user decision.** N = 9 is an assumption (`STATUS.md:66`, `d1-loop12-17-split-plan.md:1418-1420`). D-2026-09-26-02 is still `open` and blocks M8 (`tools/bench/decisions_pending.json:143-156`). If the answer is "no", the lever is lost (`:1419-1420`).

3. **The project's own architecture already points elsewhere.** The plan treats a separate display loop as the extraction target (`docs/restructure-plan-4.6.md:386`), and a display loop on `Last` cannot block acquisition (`docs/restructure-plan-4.6.md:31`). CLAUDE.md 1c'' says loop-to-loop signals go by local variable, with the consumer on its own clock. My session memory also records a 2026-09-26 user ruling that plots are drawn by a separate display loop fed by locals; I did not find that ruling in this checkout, so treat it as unverified here.

4. **The gate is already expensive and tool-bound.** 97-5 failed with retry cap and failure budget spent and nothing saved (`d1-loop12-17-split-plan.md:1480-1482`). The cause is suspected from arithmetic only (`STATUS.md:82`). The break appears after `move_into_frame`, whose self-test never checked ExecState (`d1-loop12-17-split-plan.md:1487-1488`). A further cycle buys a fix to a tool that the alternative design does not need.

**What to do instead.** Write a one-page plan for moving the graph chain into a separate display loop:
- The frame loop keeps the ring-history update and `Magnet2Force` every frame, as 206(b) requires (`d1-loop12-17-split-plan.md:1444-1445`), and publishes the ring array by local variable.
- The display loop, on its own time cadence, runs the same IndexArray → Subtract → Median → FIR → Bundler → BuildArray → indicator nodes unchanged (node set at `:1446-1447`).
- Rule 1a acceptance is the existing replay: tra columns bit-identical (`:1432-1433`).
- The refresh-rate question becomes a display-loop period and is reported with D-2026-09-26-02.

The plan gets its prior-art review and offline pre-run before any LabVIEW run. The one reading worth keeping is the ExecState-after-edit gate on diagram-editing functions (`STATUS.md:62`).

VERDICT: change NEXT
NEXT ACT: Write and prior-art-review a one-page stage plan that moves #1359's display-only graph chain and indicator #8323 out of the frame loop into a separate display loop on its own clock, fed by a local variable of the ring history, with the bit-identical replay as acceptance.