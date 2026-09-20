---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review, main-vi]
---

# panelwiring-step6-execstate0

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (16s)
- **why asked:** failed prediction at build step 6 (ExecState 1 predicted, 0 observed) - rule: attack the explanation before the rebuild.
- **verdict:** explanation accepted (recipe order: PN1b's required `reference` unwired before the check); fix = create PN1b after step 6; rebuilt as run 2.

## Question

FAILED PREDICTION check, be brief. Log tools/bench/build_oppanelwiring_v0.log (recipe tools/recipes/build_oppanelwiring_v0.py): step 6 wired the Controls[] array into the For loop's inner property node PN1 and predicted ExecState 1, observed 0 (ForLoop=1 LoopTunnel=1 Property=4 Wire=5). MY EXPLANATION: my own step order - step 5b had already created PN1b (a Control-class property node with the single row Terminal) inside the loop body with its required  input UNWIRED (it gets wired in step 7d2), and an unwired required input is exactly what held every P2 step at ExecState 0 all day (probe_castfree5.log); so the VI could not be runnable at step 6 whatever the loop input did. Fix: create PN1b after step 6 (or check ExecState only after 7f). ATTACK: any alternative reading of the same counts (Wire=5: after deleting the Text/Control/Index Array nodes in step 3 the op had 3 wires; +2 for the boundary-crossing wire = 5 - consistent?), and is there a cheaper discriminator than re-running (e.g. the same counts from OpSubVIs_v1's step 8 where the inner node was the ONLY body node and ExecState went 1)? One paragraph.

## Answer

Your explanation fits, and the counts do not provide a credible alternative: Wire=5 is consistent with 3 surviving wires plus the two segments created by crossing the loop boundary, but counts alone cannot prove correct endpoints or distinguish that new wiring fault from PN1b?셲 already-unwired required input. OpSubVIs_v1 step 8 is a cheap discriminator only if its sole body node had the same class, Terminal property, direction, and required-input state; ExecState 1 there would then support ?쐔he boundary wire is valid, PN1b caused step 6 to remain 0,??though it cannot prove this VI?셲 exact topology. The cheapest decisive check is existing step-by-step reporter output showing PN1b present and its required input unwired before step 6?봭o rerun needed. Move PN1b after step 6 or defer the ExecState prediction until 7f.

## Sources

(extract from answer)

## What was done with it

See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
