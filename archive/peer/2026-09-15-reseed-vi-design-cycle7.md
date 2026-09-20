---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, reseed]
---

# reseed-vi-design-cycle7

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (127s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

PLAN REVIEW, ATTACK IT (LabVIEW 2026 VI Scripting; behaviour-preserving rebuild of a magnetic-tweezers bead tracker). Design of Reseed.vi, cycle 7 of docs/stage2-assembly-step-e.md. Everything below is MEASURED read-only on the original VI, never edited.

WHAT THE ORIGINAL DOES (Case #5540 on diagram 43 of the main VI, measured over three censuses + the new constant/wire readers):
- #5540 sits AFTER the tracking kernel and BEFORE the right-hand shift registers. Its data inputs are the kernel's RAW outputs: t5 = x,y,z array out (wire 1681), t3 = Bead is good? array out (6041), plus two values from outside the diagram (t1 5979, t4 5746, through tunnels 5569/5752 from outer wires 5812/2731). Its outputs 5975 (x,y,z array) and 5637 (Bead is good? array in) feed the right shift registers.
- Selector (wire 5709) = Or #10247 with x <- an inner Case #10445 (output 10573) and y <- wire 10312.
- Lost-bead term: Less? #10950 x <- an implicit property read of the front-panel INDICATOR min value (#17289), which is written in the same iteration by Array Max & Min #10969 whose array <- the kernel output pos in cal image out (wire 121); Less?.y <- wire 10850; Less? -> And #9647 .x; And.y <- wire 9806; And -> the inner Case #10445 selector and a Not #10382.
- Periodic term: a property read of # of Auto-Reset (#9879) -> Equal? #10019 .x, Equal?.y <- wire 10142; Quotient & Remainder #10068 (x <- 3268, y <- 10103 = # FD points through tunnel 2213/outer 2187) remainder 10187; Equal? -> Compound Arithmetic #11639.
- NEWLY MEASURED (2026-09-15, OpConstValueN_v1 + OpWireSource_v1 + panel_wiring, all read-only, main VI byte-identical): wire 10850 <- a DigitalNumericConstant, value I32 0 -> the lost test is min(pos in cal image out) < 0 (the fixture shows lost beads carry pos = -1). Wires 9806, 10312 and 10142 are NOT constants: their sources are front-panel CONTROLS - 9806 = Auto-Reset, 10312 = Reset Tracking, 10142 = Limit of Program (owner class Diagram = control-terminal signature, confirmed against the panel census).
- Reference behaviour on the recorded fixture (10,043 frames, driver run_fixture_compare.py --reseed=main, worst deviation 0.00000): if the PREVIOUS frame's kernel x,y,z array out contains -1.0, the next frame's kernel inputs become the loader's calibration x,y,(blank z), all-TRUE good flags, and the kernel's own pos in cal image out. 13 frames carry -1.0; 26 frames carry a FALSE good flag (so the good flag alone is NOT the trigger). Auto-reset NEVER fired on this recording.

PROPOSED DESIGN (Reseed.vi, built at top level by script because the fleet can only build cases/primitives at top level, then dropped into the tracking loop of Track_v6_CPU_queue_v0):
- Connector pane inputs: x,y,z in (the kernel's raw x,y,z array out), good in (raw Bead is good? array out), pos in (raw pos in cal image out), xyz0 (the loader's calibration x,y,blank-z array), auto reset? (Boolean, the Auto-Reset control's value), reset tracking? (Boolean, Reset Tracking), plus - only if the reviewer agrees it belongs here - # of auto reset and limit of program for the periodic term. Outputs: x,y,z next, good next, and reseeded? (Boolean, for logging).
- Body: min = Array Max & Min(pos in).min -> Less?(min, 0) -> And(that, auto reset?) -> Or(that, reset tracking?) -> selector of a Boolean Case. TRUE frame: xyz0 and an all-TRUE good array (built as Initialize Array of TRUE sized by Array Size(good in)). FALSE frame: pass x,y,z in and good in through.
- DELIBERATE DEVIATION, already flagged to the user as an OPEN item: the original reads min value through a property node on an INDICATOR written in the same iteration (a race). The rebuild computes the minimum by direct dataflow from pos in. On this recording the two agree exactly (the driver reproduced the .tra to 0.00000), and the racy read is not reproducible by construction.
- What is NOT included yet: the periodic auto-reset branch (# of Auto-Reset vs Limit of Program, and the Quotient & Remainder term). It never fired on the fixture, so it cannot be validated there.
- Toolkit gaps the build needs (each = one op + one functional test): a comparison primitive (the Erdos Miller library has Create Equal.vi but NO Create Less?.vi, so Less? must come from copy_by_index of a donor VI), Create Or Array Elements.vi / Create And Array Elements.vi wrappers, a Boolean Case builder whose SELECTOR comes from a node output (gscript.build_case today takes a front-panel control as selector), and Exit Structure (case output tunnels).
- Acceptance: the 10,043-frame fixture, XYZ/GOOD/POS bit-identical to the reference INCLUDING the 25 frames after the first lost bead (which the current core cannot match), run through the 1 -> 2 -> 200 -> full gate sequence.

ATTACK (cite what you read where it matters): (1) Is the interface right - specifically, should the periodic auto-reset term live INSIDE Reseed.vi (making it need # of Auto-Reset and Limit of Program plus a way to increment that counter), or does it belong outside in the loop, given the original computes it on diagram 43 next to the lost-bead term and feeds the same Or? What is the risk to rule 1a (never change the computation) of leaving it out of Reseed.vi for now? (2) The inner Case #10445 between the And and the Or: my design collapses it into a plain Or. Under what conditions can a Case that outputs a Boolean NOT be equivalent to the Boolean expression I inferred - and what read-only measurement settles it (I can read both frames' contents with the fleet's case/diagram readers)? (3) min(pos) < 0 vs the driver's rule (previous frame's x,y,z contains -1.0): these are different quantities (pos vs xyz) read at different times. Both reproduce the fixture exactly. Which is the faithful one to build, and what discriminating test would separate them on data I already have (a 10,043-frame jsonl with per-frame x,y,z, good, pos)? (4) all-TRUE good array: the original's TRUE frame contents were NOT read node-by-node yet. What is the cheapest read-only census that proves what each frame of #5540 puts on its two output tunnels, and should the build wait for it? (5) Anything in the proposed connector pane that would make a later parallel-instance (P>1) version wrong - e.g. state that must not be shared? (6) Is there a cheaper construction that avoids the four missing ops (for instance, computing the same selector with primitives the fleet already has, or using Select instead of a Case structure)?


## Answer

Verdict: do not build the proposed `Reseed.vi` yet. Two unresolved measurements?봀ase #10445 and both frames of Case #5540?봠an still invalidate the inferred selector and TRUE-frame outputs. The fixture cannot protect against either mistake because the periodic branch never fires and its two candidate loss predicates coincide.

1. Periodic reset: preserve it, but keep its state outside `Reseed.vi`

Where the Boolean expression is physically located does not determine behavior; wired data dependencies determine execution order in LabVIEW. Therefore, computing `periodic reset?` immediately outside the subVI and passing it in is computation-preserving if the complete measured network and frame timing are retained. [NI: Block Diagram Data Flow](https://www.ni.com/docs/en-GB/bundle/labview/page/block-diagram-data-flow.html)

I recommend separating detection from switching:

```text
periodic reset? ???lost reset? ??????쇄? exact measured selector ???ReseedMux.vi
manual reset? ?????```

`ReseedMux.vi` would have:

```text
xyz raw, good raw, xyz0, reseed?
    ??xyz next, good next
```

The loop-level selector logic would receive `pos`, `Auto-Reset`, `Reset Tracking`, `# of Auto-Reset`, `Limit of Program`, and any measured `# FD points`/frame-phase input.

Reasons:

- `# of Auto-Reset` is global per-frame state, not per-bead state.
- The counter should not be incremented inside `Reseed.vi` unless the unread contents prove that the original does so there.
- Passing `periodic reset?` avoids infecting the mux with counter ownership and later P-instance semantics.
- It also permits a separate small-interval periodic test.

Leaving the periodic term out is acceptable only for a deliberately labeled fixture-development stub. It is not a behavior-preserving rebuild and cannot pass rule 1a. The risk is not merely a missing occasional reset: the unread inner Case may gate, suppress, or phase the periodic condition, or update related state even when the final selector is false. The currently known incomplete chain is documented at [stage2-assembly-step-e.md:68](</G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/stage2-assembly-step-e.md:68>).

2. Case #10445 cannot yet be collapsed into an Or

A Boolean Case output is equivalent to a Boolean expression only after proving:

- which case label is True and which is False;
- the exact source connected to output 10573 in each frame;
- whether either output tunnel uses ?쐂efault if unwired??
- whether the output is a constant, passthrough, inversion, periodic predicate, or another value;
- whether either frame performs side effects or state updates;
- whether coercion or tunnel behavior changes the datatype/value.

LabVIEW executes only the selected Case subdiagram; a Boolean expression or Select replacement can change execution if either branch contains active code. [NI: Case Structures](https://www.ni.com/docs/en-AS/bundle/labview/page/case-structures-executing-a-section-of-code-based-on-input-values.html)

The current topology is particularly suspicious: the lost term feeds both #10445?셲 selector and Not #10382, while #10445 also passes an unidentified `Value`. That is not enough evidence for `lost OR periodic`.

The settling measurement is narrow:

1. Enumerate #10445?셲 case labels/default status.
2. For each frame, list every node and tunnel.
3. For output 10573, trace its inside source to the originating terminal/constant.
4. Trace every input tunnel consumed by that source.
5. Record any writes, locals, property nodes, shift registers, or counter-related nodes in either frame.
6. Record tunnel ?쐂efault if unwired??state.

Do this before construction.

3. Build from `min(pos) < 0`, not from `xyz contains -1`

The diagram measurement is the specification: `min(pos out) < 0`, gated by `Auto-Reset`, subject to the documented indicator-property race. The driver?셲 `xyz contains -1.0` rule is an observational surrogate that happens to agree on this fixture. See the measured chain at [stage2-assembly-step-e.md:45](</G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/stage2-assembly-step-e.md:45>) and the driver?셲 substitution at [run_fixture_compare.py:98](</G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/run_fixture_compare.py:98>).

The direct-dataflow version intentionally resolves the original property-node race. Without a wire dependency, LabVIEW does not guarantee read/write order; NI explicitly warns not to infer left-to-right execution. [NI: Block Diagram Data Flow](https://www.ni.com/docs/en-GB/bundle/labview/page/block-diagram-data-flow.html) Value-property reads and writes without ordering can therefore race. [NI Community discussion](https://forums.ni.com/t5/LabVIEW/Will-property-node-cause-race-condition/td-p/1185685)

The cheapest discriminating analysis on the existing JSONL is to tabulate, for every frame `n`:

```text
A[n] = min(pos[n]) < 0
B[n] = any(xyz[n] == -1.0)
C[n] = min(pos[n-1]) < 0
```

Then inspect:

```text
A XOR B   ??quantity discrimination
A XOR C   ??current-versus-previous-frame timing discrimination
```

For each disagreement, examine whether frame `n+1` shows the calibration-reset consequence. Apply the `Auto-Reset` gate when its per-frame value is available.

If both XOR sets are empty?봞s the reported 13/13 coincidence suggests?봳he recording cannot discriminate the hypotheses. Running two replay rules and getting the same output does not add evidence when their predicates are identical. A synthetic frame with negative `pos` but no `-1.0` in xyz, and the converse, is then required.

4. Prove both #5540 frames before building

Yes, wait. ?쏷RUE means `xyz0` plus all-TRUE good??is currently established by the driver, not by the original diagram.

The cheapest census is not a whole-frame recursive inventory. For each #5540 frame:

- identify the inside terminal of output tunnels 5975 and 5637;
- walk backward only along the two source cones;
- report originating controls/tunnels/constants and intervening nodes;
- report case-label polarity and ?쐂efault if unwired??
- for the good output, capture the complete source chain?봢specially Array Size, Initialize Array, Boolean constant value, and which input determines the size;
- for xyz, prove whether the source is exactly t1 or t4 and identify those outer values.

That directly proves the two outputs with minimal reporter work. Build should wait because a mistaken frame polarity or array-size source can pass all non-loss frames and fail only at the 13 reseeds.

5. Parallel-instance risks

The proposed subVI is parallel-safe only if it remains a pure, stateless array transformation and executes once per completed frame, after all bead results are assembled.

Do not:

- put `# of Auto-Reset` mutation inside each P instance;
- compute loss independently per bead partition if one lost bead resets the entire array;
- store frame state in an uninitialized shift register, feedback node, local, or property node inside a shared-clone subVI;
- permit multiple instances to write the same counter or logging target.

A non-reentrant subVI serializes simultaneous calls. Shared-clone reentrancy uses a clone pool, while preallocated clones give each call site separate persistent state; neither makes shared counter ownership automatically correct. [NI: VI Execution properties](https://www.ni.com/docs/en-AS/bundle/labview-api-ref/page/dialog-boxes/execution-page-vi-properties-dialog-box.html)

Thus:

- call the reseed decision/mux once at the loop aggregation level;
- keep it stateless;
- keep the auto-reset counter in one loop-level owner;
- log one `reseeded?` event per frame, not per partition.

Also, `reseeded?` should mean the final measured #5540 selector?봭ot merely the lost-bead predicate.

6. Cheaper construction: use Select, pending the frame census

If both #5540 frames contain only pure value selection, two Select primitives can replace the output Case:

```text
xyz next  = Select(reseed?, xyz0, xyz raw)
good next = Select(reseed?, true-array, good raw)
```

NI documents Select as returning either its true or false input according to the Boolean selector; Case is needed when the selected condition controls which code executes. [NI: Select versus Case](https://www.ni.com/en/support/documentation/supplemental/21/labview-equivalent-of-if--if-else--and-switch-statements.html)

This removes:

- the Boolean Case builder;
- node-output-to-Case-selector support;
- Exit Structure;
- Case output-tunnel construction.

It does not remove the need for:

- Array Max & Min;
- Less?;
- scalar And;
- scalar Or;
- Array Size and Initialize Array, unless a proven equivalent source already exists.

Do not use `Or Array Elements` or `And Array Elements` merely to combine two scalar Booleans. The original nodes are scalar And/Or according to the census, so substituting array-reduction nodes adds unnecessary shape/coercion risk. Copying known-good scalar Less/And/Or/Select primitives from a donor is the smaller construction route.

However, Select is safe only after proving that both #5540 frames are side-effect-free value sources. A Case executes only one subdiagram, whereas values feeding a Select can be computed regardless of which value is selected. [NI: Case execution semantics](https://www.ni.com/docs/en-AS/bundle/labview/page/case-structures-executing-a-section-of-code-based-on-input-values.html)

Final recommendation: perform the two targeted frame censuses first, finish the periodic chain, then implement a stateless `ReseedMux.vi` using two Select nodes and keep the exact selector/counter logic once per frame outside it. Until those measurements are complete, ?쐀ehavior-preserving??is not yet supportable.

## Sources

(extract from answer)

## What was done with it

Verdict accepted in full: **no build**. The design is restructured as the reviewer set it out — a stateless
`ReseedMux.vi` (`xyz raw`, `good raw`, `xyz0`, `reseed?` → `xyz next`, `good next`) built from two `Select`
primitives, with the selector expression AND the `# of Auto-Reset` counter kept once per frame at loop level, never
inside the mux (parallel-instance safety), and `reseeded?` defined as the final measured selector rather than the
lost-bead predicate alone. Scalar `And`/`Or` are kept scalar — no array-reduction substitutes. The periodic term is
NOT dropped: leaving it out would be a labelled stub, not a behaviour-preserving rebuild, so it is measured and
wired at loop level. Two censuses run BEFORE any construction: (a) Case #10445 — labels/polarity, per-frame
contents, the source of output 10573, tunnel "default if unwired", any side effects; (b) Case #5540 — for each
frame, the backward source cones of output tunnels 5975 and 5637 only, including what determines the good array's
size and whether the xyz source is t1 or t4. On the trigger question the reviewer agrees with the diagram
(`min(pos) < 0`) and notes correctly that the fixture cannot discriminate the two predicates because they coincide
on all 13 frames — recorded in step-e.md as a coincidence, not as evidence.
