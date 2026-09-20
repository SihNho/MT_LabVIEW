---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, stage2, reseed, plan]
---

# stage2-step-e-reseed-case-plan

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (112s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS PLAN (LabVIEW 2026 VI Scripting over COM, zero GUI; rule 1a: the original's computation reproduced case-for-case). Read docs/stage2-assembly-step-e.md (the plan), docs/stage2-plan.md item 3, docs/frame-loop-wire-graph.md (search '#5540', '#10950', '#10247', '#9647', '#17289'), tools/bench/run_fixture_compare.py (the --reseed=main rule that reproduced the .tra exactly), docs/toolkit-capabilities.md and tools/gscript.py build_case().
The plan: E0 = a read-only census of the selector chain of Case #5540 in the ORIGINAL frame loop (Less? / Or / And / an implicit 'min value' property) before building anything; then a sub-VI Reseed.vi built at top level from a detector + a Boolean Case with output tunnels, dropped inside the tracking loop between the kernel outputs and the registers; acceptance = all 10,043 frames exact, including the 25 after the first lost bead.
Attack: (1) Is a SUB-VI carrying the reseed Case a computation-preserving substitute for the original's inline Case (same DBL[] passthrough, no coercion, same evaluation order relative to the kernel: the original replaces the fed-back state for the NEXT frame - the plan applies Reseed to the kernel outputs before the right shift-register, i.e. the register carries the already-reseeded state: is that the same thing as the original, where the Case sits BEFORE the kernel on the fed-back wires? Think carefully about frame n vs n+1 and about what is SAVED/recorded (the reference 'ff' rows are the kernel's raw outputs, not the reseeded state)). (2) The 'periodic auto-reset' term in the Or: on this recording it never fired - is it safe to reproduce it structurally anyway, and what inputs does it need (a frame counter? a control)? (3) The 'min value' implicit property node reads a front-panel control - which one, and is its value part of the fixture (must be baked)? (4) erdosmiller creators for the detector: which of Create Less?.vi / Create Equal.vi / Create Or Array Elements.vi / Create And Array Elements.vi exist (list the library folder) and what do their panes look like (Diagram in, position, inputs?) - same shape as Create Index Array.vi (the OpBuildIA_v0 pattern)? (5) Case output tunnels: which library VI creates them (Exit Structure.vi? Exit Multi Frame Structure.vi?) and does it wire each frame's source? Can 'Create Case Structure (Boolean).vi' take its selector from a node output rather than a control? (6) Name the cheapest first test and the biggest risk. Read-only; cite what you read.


## Answer

The plan is directionally sound for lost-bead reseeding, but it is not yet rule-1a safe. The principal danger is not sub-VI encapsulation; it is silently changing the timing and source of the selector?봢specially the periodic reset and the implicit `min value` read.

1. Frame timing: conditionally equivalent, not automatically equivalent

The original iteration is:

```text
register state S??  ??Case #5540
  ??kernel input I??  ??raw kernel output O??  ??save/record O??  ??register receives O??```

The proposed design is:

```text
register state S??  ??kernel input S??  ??raw kernel output O??  ??save/record O??  ??Reseed(O??
  ??register receives transformed state S?쇺굤??```

For the lost-bead branch, these are observationally equivalent at the kernel boundary provided all of the following hold:

- The original Case decision at frame `n+1` depends only on raw output `O?? and stable configuration inputs.
- Nothing else consumes the raw left-register values before Case #5540.
- The result sink branches directly from the kernel outputs, before `Reseed.vi`.
- `pos in cal image out` remains raw feedback.
- The Case frames reproduce the original tunnel contents and defaults exactly.

The graph supports the second condition: the xyz and good-state left registers are read by Case #5540, while the kernel?셲 raw outputs write the right registers ([frame-loop-wire-graph.md](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/docs/frame-loop-wire-graph.md:402), [left-register census](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/docs/frame-loop-wire-graph.md:425)). The fixture driver also records `ff` before changing `state`, then feeds either raw or reseeded state into the following invocation ([run_fixture_compare.py](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/run_fixture_compare.py:81)).

Therefore, a sub-VI does not itself change DBL-array representation or evaluation semantics. The dangerous wiring error would be sending `Reseed.vi` outputs to the recorded result queue. The raw kernel outputs must fan out:

```text
kernel raw xyz/good/pos ????result queue
                      ?붴????Reseed ????xyz/good registers
kernel raw pos ???????????????????????pos register
```

However, this equivalence does not automatically cover the periodic branch. Moving a condition based on the current loop counter from before the kernel to after it shifts its effective frame unless the counter expression is correspondingly adjusted.

2. Periodic auto-reset must not simply be copied ?쐓tructurally??
?쏯o firing in this fixture??only proves that omitting or mis-phasing it will not be caught by the 10,043-frame acceptance run. It does not make either choice rule-1a compliant.

The graph identifies more of this path than the step-E plan acknowledges:

- `# of Auto-Reset`.Value property #9879
- Quotient & Remainder #10068
- Equal? #10019
- Or #10247
- several Not/And nodes

([frame-loop-wire-graph.md](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/docs/frame-loop-wire-graph.md:70)).

This strongly suggests the periodic term needs at least:

- the original frame/iteration count source;
- `# of Auto-Reset`;
- possibly an enable such as `Auto-Reset`;
- the exact quotient/remainder and Boolean polarity;
- its original off/zero behavior.

That is an inference from the node inventory, not yet proven wiring. E0 must include the complete slice through #9879, #10068, #10019 and the intervening Not/And nodes?봭ot only the five nodes named in the current plan. Test the periodic branch separately with a deliberately small reset interval; the full recording cannot validate it.

3. `min value` is not a control and must not be baked as fixture configuration

This is a concrete error in the plan.

`min value` is panel object 36 and is an indicator, not a control ([main-vi-panel-map.md](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/docs/main-vi-panel-map.md:309)). Its terminal is fed by wire 17287, whose source is the `min value` output of Array Max & Min #10969 ([frame-loop-wire-graph.md](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/docs/frame-loop-wire-graph.md:197)). That Array Max & Min consumes the kernel?셲 `pos in cal image out` ([frame-loop-wire-graph.md](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/docs/frame-loop-wire-graph.md:34)).

Property #17289 asynchronously reads that indicator?셲 `Value`. Consequently:

- it is computed state, not a fixture constant;
- baking one value would be wrong;
- its effective frame age must be measured;
- replacing the property read with a direct dataflow value may remove a one-iteration/UI-update delay.

This hidden timing is the largest rule-1a risk. E0 must establish whether Less? #10950 sees the previous iteration?셲 displayed minimum, the current raw minimum through some other path, or a value with UI-thread timing. Exact fixture agreement suggests `-1` in raw xyz is a useful behavioral proxy, but that does not prove structural equivalence.

4. Creator inventory: the plan names one VI that does not exist

The installed Erdos Miller folder contains:

- `Create Equal.vi`
- `Create Or Array Elements.vi`
- `Create And Array Elements.vi`
- `Create Index Array.vi`
- `Create Case Structure (Boolean).vi`
- `Exit Structure.vi`
- `Exit Multi Frame Structure.vi`

It does not contain `Create Less?.vi`. This makes the proposed `OpBuildLess_v0` route invalid as written. Use an existing primitive-copy donor or another verified creation path after E0 establishes whether Less? is actually required.

Only `Create Equal.vi` has a saved reporter result in the requested material. Its pane is:

```text
t0  IN  Diagram in
t2  IN  location (0, 0)
t4  OUT Diagram out
t5  IN  x
t6  OUT x = y?
t7  IN  y
t9  IN  Compare Aggregates?
t11 IN  error in (no error)
t15 OUT error out
```

([probe_queue_vis.log](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/probe_queue_vis.log:10)).

That has the same general creator shape as `Create Index Array.vi`: `Diagram in`, location, typed inputs/output, and error chain. But there is no saved pane evidence here for Or Array Elements, And Array Elements, or the Boolean Case creator. Their connector layouts must be reported rather than assumed.

5. Case creation and output tunnels remain unproven

The existing generic `Create Case Structure.vi` reporter shows:

```text
t0  IN  Diagram in
t2  IN  location (0, 0)
t4  OUT Selected Diagram
t5  IN  Selector
t6  OUT Selector
t7  IN  Inputs
t8  OUT Inputs
t9  IN  Frames
t11 IN  error in (no error)
t15 OUT error out
```

([read_case_panes.log](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/read_case_panes.log:5)).

`build_case()` currently restricts the selector to a front-panel control because its wrapper obtains terminals via `Get Controls.vi`; that is an implementation limitation, not evidence that the underlying Case creator requires a control ([gscript.py](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/gscript.py:2470)). A node-output terminal should be a plausible selector source, but it is not proven in the saved tests. It needs one scratch functional test.

The pane probe intended to inspect `Exit Multi Frame Structure.vi` and `Exit Structure.vi`, but the saved log stops after `Case Next Frame.vi`; it contains no results for either Exit VI. Therefore, the plan cannot yet claim that either creator:

- creates output tunnels;
- wires one source per frame;
- preserves tunnel identity while changing selected frames;
- supports the desired array and Boolean types.

Do not choose between those two VIs by name. Obtain their reporter output first, then run a two-frame scratch test verifying both frame sources, selector polarity, tunnel count, wire UIDs and `ExecState`.

6. Cheapest first test and biggest risk

The cheapest first test is a read-only extension of the existing pane reporter covering:

- `Create Equal.vi`
- `Create Or Array Elements.vi`
- `Create And Array Elements.vi`
- `Create Case Structure (Boolean).vi`
- `Exit Structure.vi`
- `Exit Multi Frame Structure.vi`

That immediately kills several unsupported construction assumptions without building an op.

The cheapest behavioral test is pure fixture logic: branch raw `ff` to comparison output, apply reseeding only to the next state, and confirm the already-established zero-deviation result. Then add a synthetic periodic-reset sequence to expose whether the proposed post-kernel placement is one frame late.

The biggest risk is the implicit `min value`.Value property. It reads a computed indicator through an implicit property node, so replacing it with clean dataflow may change which frame?셲 minimum controls Case #5540. The second-largest risk is the periodic-reset phase shift, which the supplied fixture cannot detect.

Verdict: proceed with E0, but expand its scope. Do not build `Reseed.vi` until E0 resolves the complete periodic chain, the actual source and frame age of `min value`, Case frame polarity, and raw-output branching. The current construction inventory is also short at least one valid Less? creation route and verified Case-exit tunnel semantics.

## Sources

(extract from answer)

## What was done with it

All four corrections adopted before E0 ran: (1) the reseed sits strictly between the RAW kernel outputs and the
registers; the result queues keep branching from the raw outputs (already the case in `build_track_v6_queue.py`),
and `pos` stays raw feedback; (2) the E0 census (`tools/bench/census_case5540.py`) now covers the full slice —
#5540, the lost-bead term (Less? #10950 ← `min value` #17289 ← Array Max & Min #10969 ← `pos in cal image out`),
the periodic term (# of Auto-Reset #9879, Quotient & Remainder #10068, Equal? #10019, Or #10247, And #9647) and
every feeder one hop up; the periodic branch will get its own small-interval test; (3) the plan's "bake `min
value`" was wrong — it is an INDICATOR computed from `pos in cal image out` and read back through a property node,
so E0 must establish its frame age (a one-iteration/UI-thread lag would be a rule-1a difference if replaced by a
direct dataflow value); (4) `Create Less?.vi` does not exist — the detector's comparison primitive will come from
`copy_by_index` of a donor or from `Create Equal.vi` if the census shows an equality is what the original computes.
Plan doc corrected (docs/stage2-assembly-step-e.md).
