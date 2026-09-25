---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, archive, labview]
disposition: legacy
legacy_note: closed as legacy 2026-09-25 by card chat-L1 (cutoff 2026-09-22; user 2026-09-25 lint order before runner resume)
---

# probe0a-run1-two-gate-fails

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **date:** 2026-09-15
- **outcome:** ANSWERED (167s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS DIAGNOSIS of a failed prediction. Log: tools/bench/probe_relocate_route.log (run 1, 17:55), recipe
tools/recipes/probe_relocate_route.py.

STEP 0a asks whether work can be moved between loops inside one VI using only operations the fleet has proven,
WITHOUT a node-relocation primitive: create the destination loop, drop the same subVI into it, wire across the
border, delete the original. RESULT 5 pass / 2 fail:
  PASS G2  WhileLoop 0 -> 1 and Diagram 2 -> 3 (a new loop and its body exist)
  PASS G3  SubVI 6 -> 7, the subVI dropped onto the new loop's diagram index 2
  PASS G5  SubVI 7 -> 6, an existing subVI deleted
  FAIL G4  wire() raised "error 1057: To More Specific Class in OpWire_v1.vi"; LoopTunnel stayed 2
  FAIL G6  ExecState 0 at the end

MY DIAGNOSIS, which is what you must attack: BOTH failures are defects in the probe, not in the toolkit, so the
in-copy construct-and-delete route is NOT refuted by this run.
 - G4: I wired after the fact with a guessed source spec (class "Terminal", index 0, empty terminal name). The
   proven route on this very harness is while_loop(tunnels=["File Path"]), which creates the loop with the tunnel
   already made from a named front-panel control (archive/benchmarks/INDEX.md row 32, measured on HARNESS_copyloop).
 - G6: gscript.while_loop's own docstring says a new While loop's conditional terminal is UNWIRED, so ExecState 0
   is the documented expected state, not damage. I wrote a gate that contradicted a documented fact.
REPAIR APPLIED: G4 now uses while_loop(tunnels=["File Path"]); G6 now tests REVERSIBILITY instead - delete the added
loop and check ExecState returns to 1.

ATTACK SPECIFICALLY:
(a) Is "both failures are probe defects" self-serving? What evidence would show the toolkit is actually the
    problem - for instance that error 1057 indicates something structural about wiring into a scripted loop?
(b) Does G3 passing really establish that the subVI landed INSIDE the new loop's body, or only that a SubVI count
    rose somewhere in the VI? What check would settle it?
(c) Is reversibility the right G6, or am I replacing a gate I failed with an easier one?
(d) The cycle-8 retrospective said the approach should change at the SECOND failure of a class. This is failure 1
    for this probe. What would make repairing and rerunning the wrong move here?

--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

1. **Strongest reason the claim is wrong:** the repaired probe no longer tests construct?뱖ire?밺elete. It tests ?쐁reate a loop with a prebuilt tunnel, increment a global SubVI count, then delete objects.??Nothing proves that the new subVI consumes the tunnel or that the migrated configuration ever compiles. Thus success would merely repeat the already-known `while_loop(tunnels=...)` capability, not establish the proposed relocation substitute.

2. **Alternative explanations:**

   - G4?셲 1057 is not evidence of a structural LabVIEW prohibition, but it can be a real toolkit limitation: NI defines 1057 as ?쐎bject cannot be cast to the specified type.??[NI?셲 error-1057 article](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019OwLSAU). `gscript.wire()` itself says it cannot reach control terminals, yet run 1 invoked it with class `Terminal` ([gscript.py](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/gscript.py:1064)). Therefore OpWire may simply lack the source-reference type needed for this migration. Switching to another specialized operation bypasses that limitation; it does not prove the toolkit supports the general wiring required by the real restructure.
   - G3 proves only `SubVI: 6 ??7`. Its predicate never queries the selected diagram ([probe_relocate_route.py](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/recipes/probe_relocate_route.py:108)). ?쏰n diagram index 2??is printed from the input argument, not measured from the resulting object. Worse, `body_index = DiagramCount - 1` assumes traversal order implies newest diagram, while the toolkit elsewhere warns that traversal order is not a valid selector. Settle this with `AbstractDiagram.SubVIs[]` on the independently identified new body: require a new UID whose VI path equals `StrToPath.vi`.
   - There is a second instrumentation warning: `while_loop()` returns elapsed run time, not a loop UID ([gscript.py](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/gscript.py:995)). Run 1 nevertheless labels `0.1486?? as the loop UID. That weakens every ownership inference based on the wrapper?셲 reported result.

3. **Observation that would falsify ?쐀oth are merely probe defects??** use independently verified endpoint references?봠onfirmed source terminal, newly created body diagram, new `StrToPath.vi` UID and named sink terminal. If the identical source-to-sink connection succeeds when both nodes share a diagram but produces 1057 or no tunnel when the sink is in the loop, the failure is associated with the toolkit?셲 boundary-wiring path, not the guessed endpoint alone.

4. **G6 and rerunning:** reversibility is a worthwhile additional safety gate, but it is not a replacement for compilability of the migrated state. NI says required unwired terminals and broken wires make a VI nonexecutable and recommends reading the Error List for the specific cause. [NI debugging guidance](https://www.ni.com/getting-started/labview-basics/debug.htm). The correct functional gate is: wire a temporary Boolean to the new loop?셲 conditional terminal, complete the actual source?뭪unnel?뭤ew-subVI connection, and require `ExecState == 1` before cleanup. Then test reversibility separately.

   Current ?쐒eversibility??is also too weak: the recipe deletes an original subVI, then deletes the loop containing its replacement and removes bad wires. `ExecState == 1` afterward could mean ?쏿ll broken dependencies were erased,??not ?쐀aseline behavior was restored.??Require baseline equality of per-diagram subVI identities, tunnels and terminal wire connectivity?봭ot just executability.

Repairing and rerunning is the wrong move even at failure class 1 if the repair changes the tested capability into one already proven, retains the unverified diagram-index assumption, or lacks a compiled intermediate migrated state. That would spend the retry without discriminating the diagnosis.

**Cheapest discriminating test:** on the same scratch harness, identify the newly added diagram by UID delta, drop `StrToPath.vi`, confirm its new UID/path through that diagram?셲 nonrecursive `SubVIs[]`, wire the named control through the border into a named terminal of that exact UID, temporarily wire the While conditional, and check `ExecState == 1`?봲top there before deletion.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
