# d0v3-stop-heuristic

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-17
- **outcome:** ANSWERED (116s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim about a measured failure in tools/bench/drive_original_copy_v3.log (driver tools/bench/drive_original_copy_v3.py). CONTEXT (all measured, LabVIEW 2026, a COPY of a magnetic-tweezers acquisition VI driven over ActiveX VI Server plus scripted GUI clicks): the run scored 16 pass / 0 fail, but one 'pass' is believed spurious. Step R11 restarted the VI after a successful stop, waited 15 s, wrote the stop Booleans via SetControlValue('stop (end)', True) and 'stop (end) 2', and declared the stop successful because the front-panel indicator 'current image number' stopped advancing. ExecState was still 2 (running) and the cleanup path then needed the Abort fallback ('stop[cleanup]: VI-Server stop did NOT idle in 60s'). MY EXPLANATION, which you are asked to destroy: a restarted run re-enters the VI's bead-PICKING loop (an event-driven loop that takes no frames), so 'current image number' is frozen simply because no frames are being acquired; therefore the frozen-frame-counter progress predicate is invalid, the stop Booleans are only read inside the frame loop, and requirement 5 ('the VI can be stopped through its own control') holds ONLY in the frame loop. Earlier in the SAME run the identical stop mechanism did idle the VI in 2 s with one re-arm, and a trace file tra001-000 was written, which is why I believe the mechanism itself works. Give the strongest reason this explanation is wrong; give at least one alternative mechanism that produces the same observations (e.g. the Boolean control's mechanical action latching/re-arming, SetControlValue writing a control that a different loop owns, the restart leaving the VI in a state where the stop terminal was already read, a race between restart and the write, or the indicator being updated by a branch that the picking loop also drives); state what would falsify my explanation; and name the single cheapest discriminating test runnable over VI Server without any GUI click. Read-only: do not propose modifying the original VI.

--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

1. **The strongest reason the claim is wrong is that the frozen counter did not produce R11’s `PASS`.** The driver records R11 using `left2`—whether the restart left idle—not `st2`, the stop result. `st2` appears only in the detail string. Therefore R11 would still report `PASS` even if `stop_measured()` returned false and Abort performed the real stop. See [drive_original_copy_v3.py:404](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/drive_original_copy_v3.py:404) and [drive_original_copy_v3.py:417](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/drive_original_copy_v3.py:417). The frozen-counter predicate did create the false textual assertion `stopped=True`, but it does not explain the 16/0 score.

2. **Alternative explanation:** run 2 inherited stale front-panel and internal state, while the stop writes were consumed, overwritten, or irrelevant in some non-frame state. The driver calls `reset_controls()` before run 1 at line 248 but not before `rt2.start()`. NI explicitly documents that front-panel values can carry over between runs unless reinitialized ([NI: Programmatically Reset Control Values](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YH0zCAG&l=en-US)). Moreover, NI describes Control Value:Set as asynchronous—it sets a transfer buffer and returns without waiting for the panel update ([NI employee explanation](https://forums.ni.com/t5/LabVIEW/Dr-Damien-s-Development-Setting-Front-Panel-Controls/td-p/1166255))—and ordinary VI Server writes do not generate Value Change events ([NI knowledge article](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019N6xSAE&l=en-US)). Thus the same evidence is compatible with startup initialization overwriting the writes, a terminal consuming a latched Boolean before the relevant state examines it, or the VI waiting in some other non-frame phase. Nothing measured identifies the picking loop specifically.

3. **What would falsify the claim:** during a restarted run with the frame counter still frozen, observe either stop Boolean being consumed—`True → False` after one write, if it has latching mechanical action—while `ExecState` remains 2. A latched Boolean resets when its terminal is read ([NI explanation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P8WLSA0&l=en-US)); that observation would prove the stop terminal is read outside the claimed frame loop. Likewise, the VI becoming idle from one stop write before any frame-counter advance would directly falsify “stoppable only in the frame loop.”

4. **Cheapest discriminating test:** over VI Server only, set both stop controls `False` while idle and verify the readbacks; start run 2; after the counter remains frozen, write each stop control `True` once and poll both control values plus `ExecState` at short intervals—no re-arming and no GUI. `True` being consumed or the VI idling refutes the picking-loop-only claim; persistent `True` with `ExecState=2` supports “not read in the current phase,” although another positive phase marker would still be required to identify that phase specifically as bead picking.

## Sources

(extract from answer)

## What was done with it

**disposition: adopted (both findings CONFIRMED against our own source before adoption; no build followed).**

1. **The peer's citation is TRUE, and it refutes the causal half of my explanation.** Read at
   `tools/bench/drive_original_copy_v3.py:415-418`: `rec("12 R11 restart + %.0fs + stop", "COM", left2, ...)` — the
   PASS/FAIL flag passed to `rec` is **`left2`** (did the restart leave the idle state), while the stop result
   `st2` only ever reaches the **detail string** `"...; stopped=%s by %s"`, and `ok &= left2` on the next line.
   So R11 would have scored PASS even had the stop failed outright. **STATUS 17d's "the one real defect in v3 is
   R11's stop heuristic" is wrong about the mechanism: the scoring defect is that R11 never gated on the stop at
   all.** The frozen-counter predicate produced the false SENTENCE `stopped=True`, not the false PASS.
2. **The second citation is also TRUE**: `grep -n "reset_controls()"` returns exactly one call site, line 248,
   before run 1 — run 2 is started with no front-panel re-initialisation. That makes "stale/overwritten control
   state" a live alternative to "the picking loop never reads the stop Booleans", and **nothing measured in v3
   identifies the picking loop specifically**. I am recording that as UNKNOWN rather than keeping my phrasing.
3. **Not acted on here.** The peer's discriminating test (idle → write both stops `False` and read back → start
   run 2 → on a frozen counter write each stop `True` ONCE and poll both control values + `ExecState`, no re-arm,
   no GUI) needs a LabVIEW run against a copy of the original; this material session's task was the GPU
   divergence and the STATUS relocation. Queued as the next D0 step, VI-Server only, zero GUI actions.
4. Not adopted as fact, only noted: the peer's NI links about `Control Value:Set` being asynchronous and raising
   no Value Change event restate what `archive/peer/2026-09-17-d0-com-blocked-in-picking-loop.md` already
   established here — no new claim was accepted from a vendor forum post.
