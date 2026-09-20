# flatseq-frame-unreachable

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-16
- **outcome:** ANSWERED (125s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

FAILED PREDICTION, LabVIEW 2026 VI Scripting. Attack the claim below; do not agree with it.

THE CLAIM I am about to write into our docs, and want destroyed if it is wrong:
"In LabVIEW 2026 VI Scripting, a Flat Sequence's frames are unreachable from the VI Server GObject-traverse API
we use: you cannot get a flat-sequence frame's Diagram UID by any traverse-class + property route, because
FlatSequence is outside the subtree those calls enumerate."

WHAT WAS PREDICTED AND WHAT HAPPENED (all measured today on one 626-node VI, read-only,
tools/bench/diag_hierarchy_a3.log):
- PREDICTED: `OpTunnelRead_v0` (Tunnel -> Inside Terminals[] -> Terminal.Diagram 634A002 -> UID) would return the
  frame Diagram UIDs of a Flat Sequence, because it does exactly that for Case-structure tunnels (24/24 verified).
- OBSERVED instead:
  * Traverse class "Tunnel" WORKS and returns 468 objects, but their owner-class histogram is
    {CaseStructure 173, ForLoop 130, WhileLoop 91, Sequence 58, EventStructure 16} - **ZERO owned by a
    FlatSequence**. So there is no tunnel object to seed the reader with.
  * Traverse class "Structure" returns 63. Our structure census is 84 = 3 WhileLoop + 17 ForLoop +
    37 CaseStructure + 4 Sequence + 2 EventStructure + 21 FlatSequence. 84 - 21 = 63.
  * Traverse class "MultiFrameStructure" returns 43 = 37 + 4 + 2 (Case + stacked Sequence + Event). FlatSequence
    is not in it.
  * Traverse classes "SequenceTunnel" and "FlatSequenceTunnel" both fail with error 1092.
  * Creating a Property Node with class "VI Server:FlatSequence" and property id 6363801
    (MultiFrameStructure.Frames[]) is REFUSED with error 1077 from Create Property Node.vi. The same id on
    "VI Server:MultiFrameStructure" attaches fine and censuses as data terminal "Frames[]" (5 recorded runs).
  * Asking a flat-sequence frame's Diagram for its owner returns class name "FlatSequenceFrame" with UID 0. The
    `Generic.Owner` property node itself reports NO error; the 1055 appears only in the two property nodes
    DOWNSTREAM of the To-More-Specific-Class cast (a ClassName node and a UID node). So the Owner reference comes
    back, the ClassName reads off it, and only the cast's output is unusable.
  * Traversing class "FlatSequenceFrame" fails with error 1092; "FlatSequence" traverses and returns 21.

ALREADY RULED OUT, do not propose these:
- Rebuilding OpCaseFrames_v0 (it failed five times; the attach passed, the downstream chain did not).
- Position/geometry matching (this VI was run through Clean Up Diagram, so coordinates carry no meaning).
- Reading FlatSequenceFrame as a traverse class (error 1092, measured twice).

WHAT I WANT FROM YOU:
1. The strongest reason the claim is WRONG - name a concrete route in LabVIEW 2026 VI Scripting that gets a flat
   sequence frame's Diagram reference or UID. Property/method unique IDs or exact property names, with a source.
   Candidates I have not tested and want judged: FlatSequence's own frame accessor (if one exists under a
   different name than MultiFrameStructure.Frames[]); Diagram.Owner semantics for frame diagrams; going DOWN from
   the FlatSequence via any "Frames", "Sequence Frames", "Get Frame" property or method; reaching the frame
   diagram from an object INSIDE it (a node's Generic.Owner gives the Diagram directly - is the frame Diagram's
   own identity then enough without the frame object?); ClassSpecifierConstant.AllTypes[] as a way to read the
   real class tree instead of inferring it.
2. An ALTERNATIVE EXPLANATION of the 1077/1092/uid-0 pattern that does not mean "outside the subtree" - e.g. a
   scripting-permission, a private-property, or a version-specific gap.
3. What would FALSIFY the claim, stated as a single observable.
4. The CHEAPEST discriminating test I can run in one op call on a copy of a VI.

Answer with specifics and sources. If the claim survives your attack, say exactly which part survives and which
part is overstated - the phrase "by any traverse-class + property route" is the part I most suspect.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

1. The claim is wrong: `FlatSequence` has its own direct `Diagrams[]` accessor.

The concrete route is:

```text
Traverse "FlatSequence"
→ VI Server:FlatSequence.Diagrams[]       property ID 0x3578BC00
→ each returned Diagram reference
→ GObject.UID                             property ID 0x632A813
```

`FlatSequence` also has its own `Frames[]`, property ID `0x3578BC07`. These are FlatSequence-specific properties, separate from `MultiFrameStructure.Frames[]` (`0x6363801`). The class/property catalog explicitly lists both `Diagrams[]` and `Frames[]` on class `FlatSequence` (class ID 16459). [FlatSequence class property table](https://labviewwiki.org/wiki/FlatSequence_class)

That directly defeats “cannot get ... by any traverse-class + property route.” You already know the first step works and returns 21 FlatSequence references. `Diagrams[]` should return the actual frame-diagram references, bypassing `FlatSequenceFrame`, tunnels, `Owner`, and casts entirely. `Diagram` inherits from `GObject`, so its UID is readable through `GObject.UID` (`0x632A813`). [VI Server class hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy), [GObject.UID](https://labviewwiki.org/wiki/GObject_class/UID_property)

There is also a secondary route for frames that have an outer tunnel:

```text
Traverse "FlatSequenceOuterTunnel"        class ID 16481
→ Inner Terminal                          property ID 0x3195B801
→ Terminal.Diagram                        property ID 0x634A002
→ GObject.UID                             property ID 0x632A813
```

NI’s current API reference says `FlatSequenceOuterTunnel.Frame` returns the containing Flat Sequence frame, while the class catalog gives `Inner Terminal` and `Frame` IDs `0x3195B801` and `0x3195B802`. [NI: FlatSequenceOuterTunnel.Frame](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/flatsequenceoutertunnel/frame.html), [FlatSequenceOuterTunnel properties](https://labviewwiki.org/wiki/FlatSequenceOuterTunnel_class), [Terminal.Diagram](https://labviewwiki.org/wiki/Terminal_class/Diagram_property)

Candidate verdicts:

- FlatSequence-specific accessor: **yes—`Diagrams[]` and `Frames[]`.**
- Going down from FlatSequence: **yes—use `Diagrams[]` directly; it is better than `Frames[]` for UID retrieval.**
- `Diagram.Owner`: not the right downward route. Its returned `FlatSequenceFrame` is useful as an identity/reference but is not a `GObject`.
- Object inside a frame: viable if the frame is nonempty; its owning Diagram reference is enough to read the Diagram UID. It is not a complete census method because an empty frame supplies no seed object.
- `ClassSpecifierConstant.AllTypes[]`: useful to confirm the real class hierarchy, but unnecessary for access and not itself a route to instances.

2. Alternative explanation of the 1077/1092/UID-0 pattern

The evidence indicates a **parallel-class API**, not an unreachable subtree:

```text
Generic
├─ FlatSequenceFrame
└─ GObject
   ├─ AbstractDiagram → Diagram
   ├─ FlatSequence
   ├─ FlatSequenceInnerTunnel
   ├─ FlatSequenceOuterTunnel
   └─ Structure → MultiFrameStructure
```

The published hierarchy places `FlatSequenceFrame` directly under `Generic`, while `FlatSequence`, its special tunnel classes, diagrams, and ordinary structures are separate descendants under `GObject`. [VI Server class hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy)

That explains every symptom:

- `Structure` returning 63 is expected because `FlatSequence` is not a subclass of `Structure`.
- `MultiFrameStructure` returning 43 is expected because FlatSequence has its own API. NI explicitly describes FlatSequence as having been implemented as a separate scripting class because its frame/tunnel semantics differ from other structures. [NI Community explanation](https://forums.ni.com/t5/LabVIEW/Scripting-Connect-a-Terminal-to-a-Flat-Sequence-Structure/m-p/2672477)
- Error 1077 from attaching `0x6363801` to `VI Server:FlatSequence` means the property belongs to the wrong class. The correct FlatSequence properties are `0x3578BC00` and `0x3578BC07`.
- Error 1092 traversing `FlatSequenceFrame` is consistent with the traversal operation enumerating `GObject` instances while `FlatSequenceFrame` is not a `GObject`.
- UID 0 downstream of `To More Specific Class` is the default result of an invalid cast: `FlatSequenceFrame → GObject` is not a legal inheritance conversion. An NI Community diagnosis of this exact FlatSequenceFrame mistake says the cast fails because the class does not inherit from `GObject`. [NI Community: failed FlatSequenceFrame cast](https://forums.ni.com/t5/LabVIEW/Scripting-Positions-of-objects-in-Block-Diagram/td-p/3992381/page/2)

Thus “FlatSequence is outside the `Structure`/`MultiFrameStructure`/ordinary-`Tunnel` class branches” survives. “Its frame diagrams are unreachable by any traverse-class + property route” does not.

3. Single observation that falsifies the claim

> One LabVIEW 2026 read of `FlatSequence.Diagrams[]` (`0x3578BC00`) returns a valid Diagram reference whose `GObject.UID` (`0x632A813`) is nonzero.

One successful frame is enough to falsify the universal claim.

4. Cheapest discriminating test

In one read-only op call on the copied VI:

```text
Traverse class "FlatSequence"
→ take the first returned reference
→ read FlatSequence.Diagrams[] (0x3578BC00)
→ read GObject.UID (0x632A813) from every returned element
→ report property error, array length, UIDs, and ClassName values
```

Do not involve `Frames[]`, `Owner`, tunnels, or casts. If it returns `N > 0`, class names `Diagram`, and nonzero UIDs, the claim is dead. If creating or reading the correctly typed `0x3578BC00` property itself fails in LabVIEW 2026, that would instead support a 2026-specific API regression or permission gap—not the present “outside the subtree” explanation.

## Sources

(extract from answer)

## What was done with it

**verdict: REFUTED MY CLAIM, AND THE REFUTATION IS NOW CONFIRMED ON THE MACHINE.** Dispatched as the mandatory
review of cycle 13's one failed prediction (`diag_hierarchy_a3.log` gate B2, `12 pass / 1 fail`). The peer's
central assertion — that `FlatSequence` (class id 16459) carries its **own** accessors parallel to
`MultiFrameStructure`'s, and that error 1077 meant *wrong class*, not *unreachable subtree* — was tested the same
hour with `tools/bench/diag_flatseq_diagrams_attach.py`
(`tools/bench/diag_flatseq_diagrams_attach.log`, **`BGRUN END rc=0 after 33 s`, 5 gates pass / 0 fail**,
scratch VI created and deleted in the run, main VI never opened):

| class + property id | measured |
|---|---|
| `VI Server:FlatSequence` + **`3578BC00`** | **ATTACHED, data terminal `'Diagrams[]'`** |
| `VI Server:FlatSequence` + **`3578BC07`** | **ATTACHED, data terminal `'Frames[]'`** |
| `VI Server:FlatSequence` + `6363801` | refused, **error 1077** (reproduced in the same session) |
| `VI Server:MultiFrameStructure` + `6363801` | attached, data terminal `'Frames[]'` (the known-good control) |

So the sentence I was about to write — *"a flat sequence's frame Diagram UIDs are unreachable by any
traverse-class + property route"* — is **false and was not written**. What survives, and is what the docs now say,
is the narrower measured claim: **`FlatSequence` sits outside the `Structure` / `MultiFrameStructure` / ordinary
`Tunnel` branches** (63 = 84−21, 43 = 37+4+2, zero FlatSequence-owned `Tunnel` objects of 468), and
`FlatSequenceFrame` is not a `GObject`, which is why the cast's output is unreadable while the uncast
`Generic.Owner` read succeeds (`errO` empty; only the two downstream nodes carry 1055 — `diag_hierarchy_a3.log`
3c). The peer's class-tree explanation predicts every symptom we measured, including that one.

⚠️ **Not done, and it is a judgement call, not an oversight:** actually walking `Diagrams[]` to resolve the 57
`FlatSequenceFrame` diagrams needs a **new op VI**, which `docs/cycle13-plan.md`'s STOP condition reserves for the
judgement session. This exchange turns that from "is it possible?" into "is it worth one build?", with the two
property ids measured rather than guessed. Written into `docs/NAMES.md` and `docs/diagram-hierarchy.md`.
Sources the peer gave are labviewwiki + NI docs/forums; the ids above are **not** taken on their authority — they
are taken because the attach census reproduced them here.
