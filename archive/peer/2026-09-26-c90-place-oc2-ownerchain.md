# c90-place-oc2-ownerchain

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.9383  in 38 / out 15068 / cache-create 142305 / cache-read 2470387  (168s, 32 turn(s))
- **date:** 2026-09-26 04:21:05
- **outcome:** ANSWERED (172s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim about the failed prediction OC2 in tools/bench/diag_c90_t0_place.py (log tools/bench/diag_c90_t0_place.log, run 1 at 04:14:04, gates 16 pass / 3 fail, all three OC2):

CLAIM: "`build_d1_v0.owner_of` (tools/recipes/build_d1_v0.py:338, op OpOwnerChain_v1.vi) cannot walk UP from a Diagram that is a flat-sequence FRAME: on the S1 scratch it answered #639 -> WhileLoop #637 (positive control OC1 PASS) and #637 -> Diagram #686, then on #686, #3121 and #15041 it returned `error 1055: Property Node in OpOwnerChain_v1.vi` with the uid echoed correctly (log:44-54). 1055 is 'object reference invalid' on the Property Node, which means the `Owner` of a FlatSequenceFrame diagram is the FRAME object, and the op's cast chain (Owner -> ClassName / To More Specific Class -> GObject.UID, build_opownerchain_v1.py:13-18) does not accept it - a sequence frame is not a GObject in VI Scripting's class tree (FlatSequenceFrame is a Structure-frame class, not GObject). So the failure is a reader limitation, not a property of the three diagrams, and the question 'is there a While loop above #3121 / #686 / #15041' stays UNMEASURED by this op. The placement verbs themselves worked (PL1-PL4: build_clfn lands on the top level, stagekit.move_in puts the CLFN into Diagram[43]=#639 and Diagram[99]=#15266 with uid echo and 10 terminal rows)."

Already ruled out: (1) a stale/previous-object answer - the op echoes the queried uid and the strict check raised instead of answering (build_d1_v0.py:351-353); (2) the scratch being wrong - K1/K3 byte-identical copy of D1_s1_copy.vi md5 3e3d23ce..., H2/H3 pins hold; (3) the op being broken in general - OC1 on #639 answered WhileLoop #637 and the next hop #637 -> #686 answered too.

Offline context: tools/bench/graph_objs_s1_20260923.json lists #686/#3121/#15041 as class Diagram owner 'FlatSequenceFrame'; FlatSequence #681 (pos -3623,102) has owner 'TopLevelDiagram'; #686 pos (1979,136). docs/wiki/subvi/D1_s1_copy.json has FlatSequenceInnerTunnel rows whose frame_diagram is known wrong for half of them (tools/vigraph.py:405-408).

Questions: strongest reason the claim is wrong (e.g. is 1055 instead the Owner property returning a valid reference of a class the op's ClassName read cannot handle, i.e. fixable inside the op?); an alternative explanation; what would falsify it; the cheapest discriminating test - offline files first, one LabVIEW read at most. Also: is there any EXISTING verb in tools/ (gscript.py, tools/recipes/*.py, docs/toolkit-capabilities.md) that returns a FlatSequence's frames (`Frames[]`) or a frame's owning structure, so the three gap diagrams could be placed without a new op?


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict: the mechanism in the claim is roughly right. Its conclusion is wrong: the question it calls "unmeasured" was already answered offline on 2026-09-24, and the failure was predictable from the repo's own documents.**

## 1. Strongest reason the claim is wrong

The claim ends by saying "is there a While loop above #3121 / #686 / #15041" stays unmeasured. That was already answered two days ago, with no LabVIEW:

- `tools/bench/p1_c70_f3a.log:44-60` (run 2026-09-24 02:45, rc=0) groups `[113, 124, 686, 759, 1817, 3121, 3628, 4866, 5031, 81548]` and `[12960, 13236, 14840, 15041, …]` as the frames of the two top-level flat sequences, both owned by `#536`, the top-level diagram.
- `:42` says 167 directed edges agree with that tree, with 0 contradictions. `:41` says 238 FlatSequenceInnerTunnel owner faces point at `#536`.
- `docs/d1-loop12-17-split-plan.md:114-117` records the same result as a plan fact.

So all three gap diagrams are frames of top-level flat sequences, and no While loop sits above them. OC2 did not need this op. The chain in the cycle-90 offline script stopped early because that script's tree is built only from LoopTunnel/Tunnel/SelectorTunnel/SR edges and leaves out the flat-sequence edges (`diag_c90_t0_sites_offline.py:110-111`). The gap was in that tree builder, not in the diagrams and not only in the reader.

The failure itself was also a known, measured limit before the run:

- `docs/toolkit-capabilities.md:65` (the OpOwnerChain row, "MEASURED LIMIT 2026-09-16")
- `docs/diagram-hierarchy.md:95-97, 158-175`
- `tools/bench/diag_owner_semantics.log:96-98`: diagram 113 → `FlatSequenceFrame#0`, error 1055, reproduced
- the review `archive/peer/2026-09-16-ownerchain-flatseqframe-1055-r2.md`

`build_d1_m3a1.py:274,1550` and `build_d1_m3a3.py:34,825` even carry the warning that "an owner chain terminates SILENTLY at a FlatSequenceFrame". Running OC2 as a prediction was a prior-art miss, and that miss is the real fault here.

## 2. Alternative explanation, and corrections to the mechanism

- **"1055 means the Owner reference is invalid" is wrong.** The Owner node's own error (`errO`) is empty. The 1055 appears only in `errG` (the UID read) and `errCO` (the ClassName read taken from the cast's output) (`docs/diagram-hierarchy.md:163-168`). The raw Owner reference is valid, which is why node 482 reads `'FlatSequenceFrame'` in this run too (log:43).
- **"FlatSequenceFrame is a Structure-frame class" is inaccurate.** It is a direct child of `Generic`, not of `GObject` or `Structure`. It exposes `Diagram` 18E76802, `Outer Tunnels[]`, inner-tunnel arrays and similar, and it has no UID property ([labviewwiki FlatSequenceFrame class](https://labviewwiki.org/wiki/FlatSequenceFrame_class); [VI Server class hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy)). The cast to GObject yields Not-A-Refnum, and every node that reads from it then raises 1055 ([NI: To More Specific Class](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/functions/to-more-specific-class.html)).
- **So it can be fixed inside the op, just not by changing the cast.** Casting to the reported class still gives no UID, because the frame has none. The fix is one more `Generic.Owner` hop on the uncast frame reference, which should reach the `FlatSequence` (a GObject with a UID); that was review r2's suggestion (`…-1055-r2.md:85`). That the frame's Owner is the FlatSequence is a hypothesis: it is inherited from `Generic`, but nobody has measured it on this rig.

## 3. What would falsify the claim's conclusion ("no data on the ancestry")

If `FlatSequence #681` → `Diagrams[]` returns 686 and 3121, and `#12938` → `Diagrams[]` returns 15041, the ancestry is measured and matches f3a. #681 and #12938 are the only two FlatSequences whose owner is `TopLevelDiagram` (`graph_objs_s1_20260923.json:16-22`, `:45547-45553`).

An independent cross-check, weaker because partly positional:

- The main VI has exactly 3 While loops (`diag_owner_semantics.log:10`), sitting on 686, 686 and 15041 (`:23`, `:31`, `:39`).
- So #686 cannot lie inside bodies 639 or 25392, since those loops sit on #686; the only body left that could contain it is 15266.
- #15041 sits at x = −15217, right beside the top-level FlatSequence #12938 at x = −17474. That makes f3a's grouping plausible, but position is not proof.
- Caveat: that census was taken on the main VI, not on S1. S1 is a copy, so that is probably fine, but it has not been re-counted.

A caveat against f3a too: it derives the grouping from FlatSequenceInnerTunnel owner faces, which `tools/vigraph.py:405-408` says are wrong for half the rows. It is a derivation with 0 contradictions, not a direct read.

## 4. Existing verbs, and the cheapest discriminating test

**Existing verbs:** none returns a FlatSequence's frames.

- `OpCaseFrames` uses `MultiFrameStructure.Frames[]` 6363801. On `VI Server:FlatSequence` the creator refuses that id with 1077 (`diag_flatseq_diagrams_attach.log:15-18`).
- `FlatSequence.Diagrams[]` 3578BC00 and `Frames[]` 3578BC07 both attach (`:7-14`), but no op wraps them. The grep only finds them in docs and bench logs.
- Every current owner walk stops at the frame with 1055.

**Cheapest test, offline first (zero LabVIEW):**

1. Load `p1_c70_f3a.py`'s derived groups.
2. Check that the cycle-90 sites' frame diagrams 686, 3121 and 15041 are members, with `[536]` as the parent group. This is already true at log:44-60.
3. Swap the cycle-90 script's tree for f3a's tree, which includes the flat-sequence edges, and re-run P2/OC2 offline.

**If a machine read is required, one LabVIEW read:** extend `OpOwnerChain_v1` with a second `Generic.Owner` hop on the uncast reference when `ClassName == 'FlatSequenceFrame'`, then cast to GObject and read the UID. Prediction: 686 → `FlatSequence#681`, 3121 → `#681`, 15041 → `#12938`, then 681/12938 → `TopLevelDiagram#536`.

- If that hop still returns 1055, the frame's Owner is not the FlatSequence. The route then becomes `#681.Diagrams[]` (3578BC00), a new small op.
- If it returns the predicted chain, f3a is confirmed by measurement and OC2 passes with no new reader.

**Recommendation:** pass placement PL1–PL4 as measured. Answer OC2 from f3a now and mark it "derived, 0 contradictions". Build the Owner-hop fix only if a later stage needs the ancestry proven by a machine read.

## Sources

(extract from answer)

## What was done with it

ACCEPTED (material session, card 90-4, 2026-09-26 04:2x). OC2 was a prior-art miss: the 1055 stop at a FlatSequenceFrame is a MEASURED LIMIT (`docs/toolkit-capabilities.md:65`, `archive/peer/2026-09-16-ownerchain-flatseqframe-1055-r2.md`) and the ancestry was already derived on 2026-09-24 (`tools/bench/p1_c70_f3a.log:44-60`). The mechanism corrections (1055 is on the UID/ClassName reads after the GObject cast, not on `Owner`; FlatSequenceFrame is a Generic child with no UID) are taken as stated.
FIXED: c90-place-oc2-ownerchain - tools/bench/diag_c90_t0_sites_offline.py:118-128 - the three chain ends #686/#3121/#15041 are classified by f3a's top-level frame groups (FS#681 / FS#12938, parent #536), rows carry `loop_proven_by: f3a-derived`, gate P7 asserts no holding loop is left UNPROVEN.
Not done (judgement): the `Generic.Owner` second hop inside OpOwnerChain_v1 and any `FlatSequence.Diagrams[]` op - a reader change, not this card's; the placement result PL1-PL4 stands as measured; no rerun of diag_c90_t0_place.py (OC2 is answered offline as the review recommends).
