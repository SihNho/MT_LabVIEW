# ownerchain-flatseqframe-1055-r2

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-16
- **outcome:** ANSWERED (147s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

Refute this diagnosis. Context: LabVIEW 2026 VI Scripting driven headlessly over COM. The failing run is
`tools/bench/diag_ownerchain_hop.log` (script `tools/bench/diag_ownerchain_hop.py`), gates P1a / P2 / P3.

MEASUREMENT (diag_ownerchain_hop.log, 2026-09-16, read-only against the main VI, md5 asserted unchanged):
The op `OpOwnerChain_v1.vi` takes an object UID, does `UID to GObject Reference.vi` -> Property `Generic.Owner`
-> reads the owner's `ClassName`, and separately casts the owner with `To More Specific Class` (class name
"GObject") and reads `GObject.UID` off the cast reference. Three reads in ONE run, same op, same target VI:

    uid 8634 (GrowableFunction) -> owner ClassName 'Diagram', cast class 'Diagram', owner UID 7911, NO error
    uid 8953 (GrowableFunction) -> owner ClassName 'Diagram', cast class 'Diagram', owner UID  686, NO error
    uid  686 (Diagram)          -> owner ClassName 'FlatSequenceFrame', cast class '' (EMPTY), owner UID 0,
                                   and `error 1055: Property Node in OpOwnerChain_v1.vi`

MY HYPOTHESIS, which you should try to destroy: the ClassName read succeeded, so the `Generic.Owner` reference
itself is valid; what failed is the `To More Specific Class` cast when the owner's runtime class is
`FlatSequenceFrame`, which left the downstream `GObject.UID` Property Node holding an invalid/NULL reference and
returning 1055. So the op resolves owners whose class casts cleanly but silently loses the UID for frame-like
classes, and the fix is to read `GObject.UID` off the UN-CAST Owner reference (or to cast to the class actually
reported) rather than to "GObject".

ALREADY RULED OUT (do not re-suggest):
 - not a permission or VI-loading issue: the same op, same client, same run resolved 8634 and 8953 with no error.
 - not a bad input uid: the op's own self-read echoed uid 686 with class 'Diagram', so 686 exists and is a Diagram.
 - not the target being modified: the main VI's md5 is identical before and after the run.

ANSWER THESE:
 1. The strongest reason my hypothesis is wrong.
 2. An alternative explanation for error 1055 here. In particular: what does LabVIEW scripting actually return
    for the `Owner` of a Diagram that belongs to a Flat Sequence frame, and is `FlatSequenceFrame` a descendant
    of `GObject` in the LabVIEW scripting class hierarchy at all? Cite NI documentation or the class hierarchy.
 3. What observation would falsify my hypothesis.
 4. The cheapest single discriminating test, using ONLY read-only scripting property reads.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

1. **Strongest reason the diagnosis is wrong as stated:** the proposed fix cannot work. `FlatSequenceFrame` is **not** a GObject or a descendant of GObject; it is a direct child of `Generic`, alongside `GObject`. Therefore it has no `GObject.UID` property to read—cast or uncast. The hierarchy is:

```text
Generic
├─ FlatSequenceFrame
└─ GObject
   ├─ AbstractDiagram → Diagram
   └─ FlatSequence
```

See the [VI Server class hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy) and the [FlatSequenceFrame class](https://labviewwiki.org/wiki/FlatSequenceFrame_class). Consequently, “read `GObject.UID` directly from the uncast Owner” is not a valid fix, and casting “to the class actually reported” still would not produce a UID because `FlatSequenceFrame` exposes frame properties—not `GObject.UID`.

There is also a measurement gap: the run did **not capture the cast’s own error output**. `read_owner()` gathers `errL`, `errT`, `errO`, `errU`, and `errG`, but omits the mapped cast error `errCO` ([build_opownerchain_v1.py](</G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/recipes/build_opownerchain_v1.py>)). Thus “the cast failed” is strongly implied, but not directly measured. NI says an incompatible `To More Specific Class` operation returns an error and `Not A Refnum`; the reported 1055 instead comes from a **Property Node** consuming an invalid reference. [NI: To More Specific Class](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/functions/to-more-specific-class.html)

2. **Alternative explanation:** this is not a transient or defective cast; it is a deterministic modelling error in `OpOwnerChain_v1`. For a `Diagram` belonging to a Flat Sequence frame, `Generic.Owner` legitimately returns a valid `Generic` reference whose runtime class is `FlatSequenceFrame`. `Generic.Owner` is expressly typed as `Generic`, and sequence containers can be owning objects. [Generic.Owner documentation](https://labviewwiki.org/wiki/Generic_class/Owner_property)

Because `FlatSequenceFrame` lies outside the GObject subtree, the op then performs an impossible cast to `GObject`. Per NI, that produces `Not A Refnum`; the downstream UID Property Node dereferences it and emits 1055, whose documented meaning is “object reference is invalid.” [NI: error 1055](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019L75SAE&l=en-US)

So the likely chain is:

```text
Diagram#686
  → Generic.Owner = valid FlatSequenceFrame ref
  → cast-to-GObject = incompatible / Not A Refnum
  → GObject.UID Property Node = error 1055
```

The correct traversal is therefore class-specific: from `FlatSequenceFrame`, use its read-only properties—particularly `Diagram`—or continue through `Generic.Owner` to reach the enclosing `FlatSequence`, which *is* a GObject. `FlatSequenceFrame` itself has no UID. [FlatSequenceFrame properties](https://labviewwiki.org/wiki/FlatSequenceFrame_class), [FlatSequence hierarchy](https://labviewwiki.org/wiki/FlatSequence_class)

3. **Observation that would falsify your hypothesis:** capture the cast’s error output and cast-result validity. If the input Owner reports `FlatSequenceFrame`, but `To More Specific Class → GObject` reports no error and its output is not `Not A Refnum`, while `GObject.UID` still returns 1055, then the cast-failure explanation is false. Likewise, if another raw-Owner Generic property such as `Class ID` fails with 1055, the Owner reference itself is invalid/stale despite the earlier ClassName result.

4. **Cheapest discriminating test:** without any cast, branch the raw `Generic.Owner` result and read only:

- `Generic.Class Name`
- `Generic.Class ID`
- `Generic.Owner`, followed by that owner’s `Generic.Class Name`

For uid 686, the decisive expected result is approximately:

```text
raw owner: FlatSequenceFrame, class ID 16479
raw owner’s owner: FlatSequence
no 1055
```

If that succeeds, the raw Owner reference is valid and the GObject cast/UID branch is conclusively the bad assumption. If either raw Generic read returns 1055, reference invalidation is the better explanation.

After trying to refute it: **the core mechanism of your hypothesis still holds**, but the suggested repair does not. The op must special-case the `FlatSequenceFrame` branch and traverse via Generic/frame properties; it cannot recover a `GObject.UID` from that frame itself.

## Sources

(extract from answer)

## What was done with it

**This is the review that discharges the failed prediction in `tools/bench/diag_ownerchain_hop.log`** (gates P1a,
P2, P3). `OUTCOME: ANSWERED (258s→147s on retry)`, agent codex — the first dispatch of the same question TIMED OUT
at 180 s and told us nothing (`2026-09-16-ownerchain-flatseqframe-1055.md`), so this is the review, not that one.

**Checked against our own files, not accepted on authority:**
- ✅ **The measurement gap is REAL and I confirmed it in the code.** `read_owner()` collects
  `("errL","errT","errO","errU","errG")` — `tools/recipes/build_opownerchain_v1.py:269` — while
  `tools/bench/opwiresource_v5_labels.json` also defines **`errCO` ("error out 10")**, the cast node's own error,
  which is never read. So "the cast failed" is **implied, not measured**, exactly as the reviewer says. That is a
  fact about our code, independent of anything about LabVIEW's class tree.
- ⚠️ **The hierarchy claim is a HYPOTHESIS, not confirmed.** `FlatSequenceFrame` being a sibling of `GObject`
  under `Generic` (so that it has no `GObject.UID` at all) comes from labviewwiki, not from the machine. CLAUDE.md
  rule 5: a peer answer is a hypothesis until confirmed against the machine or NI's own files. It is consistent
  with the measurement (`cast_class` came back EMPTY, and an empty cast output is what an incompatible
  `To More Specific Class` produces) but it is not verified here.
- The reviewer's cheapest discriminating test is recorded as-is and NOT run: branch the raw `Generic.Owner` and
  read `Generic.Class Name`, `Generic.Class ID`, and `Generic.Owner` → that owner's `Generic.Class Name`, with no
  cast anywhere. Predicted for uid 686: `FlatSequenceFrame` (class ID ~16479), its owner `FlatSequence`, no 1055.

**What was NOT done, deliberately:** `OpOwnerChain_v1` was not changed. Redesigning the op so the chain does not
terminate at a flat-sequence frame — and deciding whether the chain is even needed for STATUS OPEN 1 — is a design
decision reserved to the judgement session (CLAUDE.md §3; and question 7 of this cycle's retrospective fired
`judgement-in-material` for exactly this kind of act being taken inside a material run). Carried to OPEN.

The measured limit is recorded in `docs/toolkit-capabilities.md` (the `OpOwnerChain_v1.vi` row) and in
`STATUS.md` OPEN 1.
