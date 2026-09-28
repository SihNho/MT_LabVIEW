# c120-fs-owner-frame

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.2379  in 18 / out 9828 / cache-create 100019 / cache-read 884754  (118s, 15 turn(s))
- **date:** 2026-09-28 15:43:56
- **outcome:** ANSWERED (122s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim about a failed gate in tools/bench/diag_c120_fs.log (script tools/bench/diag_c120_fs.py, card 120-2 Part F).

CONTEXT. Measure-only run on a never-saved byte copy of a LabVIEW VI: one connect (build_opconnectnested_v1.connect_nested_v1,
the 'nested' route of tools/stagexec.py connect_route) from a BARE Obtain Queue 'queue out' (#23118, t25591) on frame diagram #13236
of one Flat Sequence to a duplicated Enqueue 'queue' (#26300) inside While loop #637 body #639 on frame diagram #686 of another
Flat Sequence. Gate F1a failed (diag_c120_fs.log:30): it expected build_d1_v0.owner_of() to walk each frame diagram's owners up to
the TopLevelDiagram and find a FlatSequence ancestor on each side. Observed (:24-29): owner_of(#13236) and owner_of(#686) both
return ('FlatSequenceFrame', 0) with 'error 1055: Property Node in OpOwnerChain_v1.vi'; #639 -> WhileLoop #637 -> Diagram #686 read
fine. Every other gate passed (13/1): the connect returned no error; the after-graph shows 4 new wires, 1 LoopTunnel #26507 (owner
While #637), 2 FlatSequenceOuterTunnels #26775 (owner FlatSequence #12938; inner face on #13236, outer face w26702 on #536) and
#26549 (owner FlatSequence #681; outer face w26702 on #536, inner face on #686); the hop walk closes t25591 -> #26775 -> w26702 ->
#26549 -> #26507 -> #26300.'queue' (:49-52); all 4 hop wires survived LabVIEW's Remove Bad Wires (:54-56).

THE CLAIM. F1a failed because of OUR GATE's premise, not the VI or the route: OpOwnerChain_v1 cannot resolve the owner of a
FlatSequenceFrame (its owner-uid read errors 1055 and returns 0), so an owner_of walk stops at the frame. The nesting the gate meant
to confirm is nevertheless established by the tunnels LabVIEW created: #26775 is owned by FlatSequence #12938 with its inner face on
#13236 and #26549 by FlatSequence #681 with its inner face on #686, both outer faces on TopLevelDiagram #536, so source and sink are in
two different flat sequences on the top-level diagram. The route result (PASS: the wire crosses both sequences through one
FlatSequenceOuterTunnel each, no FlatSequenceInnerTunnel, plus one LoopTunnel) is unaffected.

Give: the strongest reason this claim is wrong (e.g. could error 1055 mean the frames are NOT flat-sequence frames, or that the
copy is corrupted?); an alternative explanation; what would falsify it; the cheapest discriminating test.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**The claim holds. The one failed check (F1a) failed because the check itself was built on a premise this project had already measured as false.** It does not show that the copy is corrupted or that the frames are something other than flat-sequence frames. What the claim overstates is the "route PASS". Here is the attack, in the four parts the brief requires.

**1. Strongest reason the claim could be wrong, and why it still holds.** The obvious worry is that error 1055 means these two diagrams are not flat-sequence frames, or that the copy is damaged. The evidence rules both out.
- **Error 1055 is explained by LabVIEW's class tree.** The VI Server class hierarchy puts `FlatSequenceFrame` directly under `Generic`, not under `GObject`. The sequence and its tunnels are all under `GObject`: `FlatSequence` directly, and both tunnel classes through `Tunnel` ([LabVIEW Wiki, VI Server Class Hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy)).
  - Our owner-reading tool reads `Owner` without error, and the class name taken from that uncast reference is `'FlatSequenceFrame'`.
  - The only errors come from the property nodes downstream of the cast (`docs/diagram-hierarchy.md:158-175`). That is the "cast returns an invalid reference, the next node reads it" pattern.
  - The class name the tool echoes is the machine saying these ARE flat-sequence frames.
- **The same result has been measured before, on other diagrams:** diagram #113 and #686 on 2026-09-16 (`docs/diagram-hierarchy.md:95-98`, `:86`).
- **The project's own plan already says the owner walk stops there:** "No owner-chain op. `OpOwnerChain_v1` stops at a FlatSequenceFrame (1055)" (`docs/d1-loop12-17-split-plan.md:1099`).
- **Corruption is ruled out by the log:** the work copy is byte-identical to the input (`diag_c120_fs.log:20`, K3), and #639 → #637 → #686 read cleanly in the same run (`:25-26`).

So F1a was a check that could never pass, written into a script whose plan documents say so. The honest classification is a prior-art miss at planning time, not a surprise.

**2. Alternative explanation, and where the claim goes too far.** The tunnel argument is partly circular. The tunnels were created by the route being tested, so they cannot on their own confirm the route's starting assumption about where source and sink sit.
- It is rescued by an independent measurement: a separate earlier run put #686 and #13236 in two different top-level flat sequences whose owner is #536 (`d1-loop12-17-split-plan.md:115-118`, from `p1_c70_f3a.log:44-60`). #681's owner has also been read cleanly as TopLevelDiagram #536 (`docs/cycle27-plan.md:3374`).
- Cite those as the proof of the nesting, not the new tunnels.

The "route PASS" is structural only, for three reasons:
- **The VI never compiled.** ExecState is 0 before and after the connect (`:35`, `:40`), and there are 29 bad wires elsewhere (`:54`). "Survived Remove Bad Wires" in a VI that is already broken is weaker evidence than a clean compile.
- **The plan predicted something else.** It says the pool-to-loop wire crosses 8 inner tunnels on each side, 16 in total, and states "No measured route creates FS tunnels" (`d1-loop12-17-split-plan.md:2233`). The run observed zero inner tunnels and two outer tunnels.
  - That is a second failed prediction.
  - The script sidesteps it by labelling the result "expected=measured, not predicted" (`:56`).
  - LabVIEW does allow this: data leaves each flat-sequence frame's own tunnel as soon as that frame finishes ([NI, Flat Sequence Structure](https://www.ni.com/docs/en-GD/bundle/labview-api-ref/page/structures/flat-sequence.html)). But the plan's model of the crossing was wrong and should be corrected, not passed over.
- **The wire adds a new timing dependency.** Frame 9 of sequence #681 now waits for frame 2 of sequence #12938 to finish. Under rule 1a, that change in execution order still needs a check against the original's order.

**3. What would falsify the claim:**
- #13236 is missing from the frame list (`Diagrams[]`) of sequence #12938, or #686 is missing from #681's.
- Or an owner read on a diagram known to be clean returns 1055 in the same session, which would point at the tool or the copy rather than the class.

**4. Cheapest test that separates the claim from the alternatives.** This needs no LabVIEW run: check that the earlier frame lists in `p1_c70_f3a.log:44-60` attribute #13236 to #12938 and #686 to #681 by uid. That run was on a different file, so confirm the uids carry over by byte copy.

If a live check is wanted, one read-only call is enough: read `FlatSequence.Diagrams[]` (property 3578BC00, already shown to attach, `docs/diagram-hierarchy.md:137-146`) on #12938 and #681 and test membership. Then rewrite F1a to check that membership, or to check each tunnel's owner and inner-face diagram, instead of walking owners.

**What would change my mind:** a membership mismatch in that test, or a clean diagram returning 1055 in the same session.

Sources:
- [VI Server Class Hierarchy – LabVIEW Wiki](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy)
- [Flat Sequence Structure – NI](https://www.ni.com/docs/en-GD/bundle/labview-api-ref/page/structures/flat-sequence.html)

## Sources

(extract from answer)

## What was done with it

Accepted (card 120-2 material). Test 4 was run offline: tools/bench/p1_c70_f3a.log:44-60 puts #686 in the frame group
{113,124,686,759,1817,3121,3628,4866,5031,81548} and #13236 in {12960,13236,14840,15041,19687,19887,20261,21134,25769,26117},
two different top-level flat sequences owned by #536 - so the nesting is proven by that earlier independent read, not by the new
tunnels. F1a is NOT re-run (its premise, an owner_of walk through a FlatSequenceFrame, is known to stop at 1055:
docs/d1-loop12-17-split-plan.md:1099); a later script should check FlatSequence.Diagrams[] membership instead. The route result is
reported as STRUCTURAL only (ExecState 0 before and after; 29 pre-existing bad wires). The two judgement items the review raised -
the plan's 8+8 FlatSequenceInnerTunnel model (d1-loop12-17-split-plan.md:2233) contradicted by 0 inner + 2 outer tunnels, and the
new frame-order dependency (FS #681 frame waits on FS #12938 frame 2) under rule 1a - are handed to judgement in result_120-2 OPEN.

(Claude fills in)
