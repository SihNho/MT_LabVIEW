# case-frame-identity-retry

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-16
- **outcome:** ANSWERED (142s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

LabVIEW 2026 VI Scripting. Failure record for the gate: tools/bench/diag_autofocus_panel2.log (a deliberate 2x2 grid whose FAIL rows were PREDICTED by the script's own contract; that conclusion is already reviewed and I am not re-asking it). A first attempt at this question timed out at 180s - answer compactly.

THE CLAIM TO ATTACK. We have a Case Structure on a running experiment VI whose boolean selector is (frameCount mod 25 == 0) AND NOT(a front-panel switch). One of its frames contains a serial stage-motion call. We assert, WITHOUT having read the frames, that selector TRUE means the axis is commanded. The instrument's owner tells us a DIFFERENT front-panel switch is the one that enables stage motion - so there is probably a further condition inside the frame, or our frame-to-value mapping is inverted.

1. How do I read WHICH FRAME corresponds to which selector value? Our notes name 'CaseStructure.Frame Names' (ID 6365002) but record it as never used. Is that the right property, what does it return for a BOOLEAN selector, and does its order match Diagram[] indices?
2. Is there a property for the DEFAULT frame, or the currently visible frame, and does either identify the TRUE frame?
3. Given a frame's Diagram reference, the cheapest scripting route to list subVI calls inside it INCLUDING nested structures.
4. Any way a subVI node can sit on a selected frame's diagram and still NOT execute?

Short answers with citations. If a property does not exist in 2026, say so plainly.

--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

The claim is wrong as stated: `TRUE` proves only that LabVIEW selects the True subdiagram?봭ot that a stage command is reached or succeeds. A Case Structure executes one selected subdiagram, whose internal dataflow may contain further gates. [NI: Case Structures](https://www.ni.com/docs/en-AS/bundle/labview/page/case-structures-executing-a-section-of-code-based-on-input-values.html)

1. **Mapping selector value ??frame**

`CaseStructure.Frame Names` is the correct property: ID `6365002`, returning a string array. For a Boolean selector, the frame labels are `False` and `True`. [Frame Names property](https://labviewwiki.org/wiki/CaseStructure_class/Frame_Names_property) [Boolean Case Structure](https://labviewwiki.org/wiki/Case_structure)

Do **not** assume its array order matches `Frames[]`; that correspondence is not documented. Use:

```text
index = CaseStructure.Get Frame Index("True")
trueDiagram = MultiFrameStructure.Frames[][index]
```

NI?셲 scripting anatomy explicitly prescribes `Get Frame Index` for mapping a frame-name string into `Frames[]`. [VI anatomy documentation](https://rajsite.github.io/unofficial-lvdocs/lvconcepts/anatomy.html) [Get Frame Index](https://labviewwiki.org/wiki/CaseStructure_class/Get_Frame_Index_method)

2. **Default and visible frames**

- `CaseStructure.Default Case` exists: ID `6365001`, I32 frame index. It identifies the fallback frame, not the Boolean-True frame. Boolean selectors already exhaust both possible values. [Default Case property](https://labviewwiki.org/wiki/CaseStructure_class/Default_Case_property)
- Inherited `MultiFrameStructure.Visible Frame` exists: ID `6363800`, U32, zero-based. It means the frame displayed in the editor; it is writable even while running, so it is not the runtime-selected frame. [Visible Frame property](https://labviewwiki.org/wiki/MultiFrameStructure_class/Visible_Frame_property)
- There is **no public LabVIEW 2026 scripting property for ?쐁urrently executing Case frame.??* The CaseStructure surface lists only Selector, Default Case, Frame Names, and Case Insensitive Match. [CaseStructure property list](https://labviewwiki.org/wiki/CaseStructure_class)

3. **Cheapest recursive subVI inventory**

Call `Traverse for GObjects.vi` with:

```text
Traverse Target = Other
Other Refnum    = selected frame's Diagram reference
Class Name      = "SubVI"
```

It recursively descends into nested container objects. Downcast each result to `SubVI`, then read `VI Name` or `VI Path`. [Traverse for GObjects](https://rajsite.github.io/unofficial-lvdocs/glang/TRef_Traverse_for_References.html) [SubVI properties](https://labviewwiki.org/wiki/SubVI_class)

4. **Yes, a found subVI can still not execute?봮r execute without moving**

A recursive result may lie inside an unselected nested Case/Disable Structure. A direct call may wait forever for required inputs, because nodes fire only when all required inputs arrive. A subroutine-priority call can also have `Skip Subroutine Call If Busy` enabled. [NI dataflow](https://www.ni.com/docs/en-GB/bundle/labview/page/block-diagram-data-flow.html) [SubVI Skip property](https://labviewwiki.org/wiki/SubVI_class) [NI disable structures](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P9NASA0)

More importantly, the call can execute while the motion operation does not: the owner?셲 second switch or an incoming error can select a no-op path inside the subVI. NI explicitly documents the pattern of passing an incoming error through without executing the subVI?셲 operational code. [NI Development Guidelines](https://download.ni.com/support/manuals/321393d.pdf)

**Alternative explanation:** the stage subVI is in the True frame but guarded by the owner?셲 motion-enable switch, an error case, or another nested condition; alternatively, it is actually in the False frame.

**Falsifying observation:** selector=`TRUE` while a breakpoint/probe or serial-write counter shows zero invocations of the actual stage-write operation.

**Cheapest discriminating test:** call `Get Frame Index("True")`, index `Frames[]`, then recursively traverse that one diagram for `SubVI` and report each node?셲 `VI Path` plus its owner ancestry. That single read distinguishes inverted frame mapping from a nested/internal motion-enable gate.

## Sources

(extract from answer)

## Annotation (2026-09-16, the session that asked)

**ACCEPTED.** The premise it attacked was mine and it was wrong: "the case fires" does not prove "the axis is
commanded". Two independent things then landed on the same hour — this answer, and an offline trace that showed the
motion *enable* is computed on diagram 43 (`Auto-Focus AND NOT(reseed-And) AND counter < Limit of Auto-Focus`) and
written into the control the case reads. So the inner-gate possibility the reviewer insisted on is exactly what the
VI does, one level further out than either of us was looking.

IDs and the `Get Frame Index` → `Frames[]` route recorded in `docs/NAMES.md` ("Case-structure frame identity"),
including the warning not to assume `Frame Names` order matches `Frames[]` — that is how a polarity gets inverted,
and `stage2-assembly-step-e.md:150` has carried "which diagram is the TRUE frame" as open since 2026-09-15.
The genuinely new capability is the **diagram-scoped traverse** (`Traverse Target = Other` + `Other Refnum`):
`OpReportAll_v0` passes Target = 1 (whole block diagram), so scoping a traverse to one frame is something the fleet
cannot do today. Queued, not built — the build gate is closed and this is not urgent.

The first attempt at this question **TIMED OUT at 180 s** (`tools/bench/peer_case_frame_identity.log`) and is
logged as a non-result; `-TimeoutSec 480` and a shorter prompt got the answer in 142 s.

## What was done with it

(Claude fills in)
