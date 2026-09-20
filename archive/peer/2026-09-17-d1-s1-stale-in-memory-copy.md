# d1-s1-stale-in-memory-copy

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-17
- **outcome:** ANSWERED (82s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

A gate that passed on the previous run failed on the next one with numbers that look like the PREVIOUS run's output, and I want my explanation attacked before I change the recipe again.

FACTS (LabVIEW 2026, VI Scripting over COM, one client):
- The recipe deletes its target file, copies the md5-verified original onto that same path, calls an open-panel, then censuses object counts.
- Run 2 (tools/bench/build_d1_v0_run2.log) censused the fresh copy as Diagram 170, Node 626, WhileLoop 3 - matching the original exactly - then created 3 While loops (Diagram 173, Node 630 after a later step, WhileLoop 6) and FAILED at its next gate, returning early WITHOUT closing the target.
- Run 3 (tools/bench/build_d1_v0_run3.log), same code path, same target PATH, deleted and re-copied the file, and censused: 'Diagram 173, Node 630, WhileLoop 6' - i.e. exactly run 2's EDITED state, on a file that had just been overwritten on disk with the unedited original.
- This project already recorded a matching failure once: archive/peer/2026-09-17-moveinto-stale-in-memory-vi.md, and its remedy is 'a uniquely named working copy per run'.

MY EXPLANATION, which I want refuted: LabVIEW served the VI from its own memory because run 2 left that path loaded and never closed it; a filesystem overwrite of a loaded VI's path does not change what a VI-Server open returns. The fix is a unique working-copy filename per run, plus restarting LabVIEW so nothing from the previous run remains loaded.

COMPETING EXPLANATIONS I CONSIDERED:
(i) the copy did not happen - I have no positive evidence it did in run 3 beyond the code path being the same one that worked in run 2;
(ii) the census reader is caching its own results in the Python process - ruled out for cross-process reasons: run 3 is a new process;
(iii) LabVIEW wrote its in-memory edits back to the path at some point, so the DISK file really was the edited one before the copy - I cannot rule this out from the logs, and it matters, because it would mean an unsaved edited VI can reach disk without an explicit save.

WHAT I NEED: the strongest reason my explanation is wrong; whether (iii) is possible in LabVIEW 2026; what would falsify mine; the cheapest discriminating test; and whether a unique filename per run is sufficient or whether the previously loaded VI must also be explicitly closed or the application restarted. Do not restate my reasoning back to me.

--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

1. **Strongest reason the claim is wrong:** it treats an unverified filesystem operation as established fact. Run 3 contains no post-copy hash, size, timestamp, or byte comparison. Therefore the observation does not distinguish “LabVIEW returned the resident VI” from “the target on disk was still the edited VI.” Reusing the same code path is not evidence that the copy succeeded.

2. **Alternative explanation:** run 2’s edited VI reached disk through a save operation, and run 3’s delete/copy failed, targeted a different resolved path, or was subsequently undone. LabVIEW’s documented persistence workflow requires a save after programmatic edits—NI’s examples explicitly modify the VI and then invoke Save Instrument ([NI: programmatically change VI properties](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019V5iSAE), [NI: set default values](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YHw5CAG)). Automatic recovery does not normally overwrite the source VI; it writes recovery files under `LVAutoSave` ([NI: Auto Recovery](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000x1g6CAA)). Thus (iii) is possible if some explicit or implicit save path ran—Save Instrument, Save All, or acceptance of a close-time save prompt—but I found no NI documentation supporting spontaneous replacement of the source file merely because an edited VI remains loaded. Also, (iii) alone cannot explain run 3 if the subsequent verified-original copy really succeeded.

3. **Observation that would falsify the claim:** start a demonstrably fresh LabVIEW application instance, verify the target’s disk hash equals the original immediately before opening it, then obtain the edited census. With no prior application memory to supply run 2’s object, that result would force another explanation—wrong target/reference, census defect, or disk mutation during the open. In a live instance, the equivalent is proving the target’s qualified VI name is absent from `All VIs in Memory` before opening; NI specifically recommends that property for monitoring unloading ([NI: Closing References](https://www.ni.com/en/support/documentation/supplemental/13/closing-references-in-labview.html)).

4. **Recipe implication:** a genuinely unique **VI filename/qualified name**, not merely a different directory, is sufficient to prevent this particular identity collision. LabVIEW cannot load two VIs with the same name in one application instance ([NI documentation](https://www.ni.com/docs/en-US/bundle/labview/page/comparing-vis-and-vi-hierarchies.html)). Still close every VI and child-object reference on every exit path: NI warns that leaked VI references keep whole VIs resident and can produce incorrect subsequent behavior. Closing is asynchronous, so a close immediately followed by same-name reopening is not a deterministic unload barrier ([NI: Closing References](https://www.ni.com/en/support/documentation/supplemental/13/closing-references-in-labview.html)). A restart is unnecessary when every run uses a unique qualified name, but it is the strongest reset when reusing names or when reference ownership is uncertain.

After trying to refute it, I still think the stale-resident-VI mechanism is the leading explanation: NI says Open VI Reference can return a VI already resident in the application instance or load it from disk ([NI: VI Server application](https://www.ni.com/docs/tr-CY/csh?context=lvcore_lvhowto_vi_server)). What would change my mind is a clean-instance reproduction with a verified-original disk hash.

**Cheapest discriminating test:** add exactly one assertion immediately after run 3’s copy and before any LabVIEW open: hash the destination and require it to equal the verified original. If that hash is original but the census is `173/630/6`, stale LabVIEW memory wins; if the hash is edited or missing, the copy/save-path alternative wins.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)

## What was done with it

**OUTCOME: ANSWERED (codex, gpt-5.6-sol, 82 s).** It could not refute the stale-resident-VI mechanism and cited
NI directly: `Open VI Reference` may return a VI **already resident in the application instance** rather than
loading from disk, and LabVIEW cannot hold two VIs of the same qualified name in one instance. On the question I
could not settle myself — explanation (iii), "could LabVIEW have written its unsaved edits to that path?" — it
answered by naming a one-line test rather than an opinion.

**ACCEPTED, and both halves applied:**
1. **A unique working-copy filename per run** (`Track_v6_D1_GPU_<HHMMSS>.vi`, created and deleted in the same
   run) — the remedy this project already recorded (`archive/peer/2026-09-17-moveinto-stale-in-memory-vi.md`,
   STATUS "START HERE" 4, plan §2a gate P1z) and did not apply here. The peer confirms a unique **qualified
   name** is sufficient for this collision; a restart is the stronger reset and is done anyway because handles
   stood at 54,384 against a ~31,500 baseline.
2. **The discriminating test, as gate `S1z`**: md5 the destination *after* the copy and *before* any LabVIEW
   open, asserting it equals the original. This is the point — run 3 could not tell "LabVIEW served memory" from
   "the disk file was already edited", and now the log answers it without a hypothesis.

**Failure budget: 1 of 2 used for this class** (a stale in-memory artefact served instead of a fresh copy).
