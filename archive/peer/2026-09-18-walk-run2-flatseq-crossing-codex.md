# walk-run2-flatseq-crossing-codex

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-18 01:56:33
- **outcome:** ANSWERED (100s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS CLAIM. It is the conclusion a measurement run produced, and it will shape how a motor-safety
wiring check ("check A") is built, so a wrong reading here is expensive.

THE RUN. `tools/bench/probe_flatseq_walk.py`, log `tools/bench/probe_flatseq_walk_run2.log`, 9 of 9 gates pass,
read-only, nothing saved, both originals' md5 unchanged. LabVIEW 2026 VI Scripting over COM.

WHAT IT MEASURED (all first-hand, all in that log)
  A. `report_all(V6_working_copy, "FlatSequenceInnerTunnel")` returns **518 objects** (log:39). So Traverse for
     GObjects DOES enumerate that class.
  B. On a scratch VI, a Property Node whose class string is `VI Server:FlatSequenceInnerTunnel` accepts
     1C3A9000 -> data terminal short name `LeftTerm`, 1C3A9001 -> `RightTerm`, 1C3A9002 -> `LeftFrame`,
     1C3A9003 -> `RightFrame` (log:49-52). 1C3A9004, 1C3A9005, and the Tunnel-class ids 6356000 / 6356001 are
     each REFUSED with error 1077 from `Create Property Node.vi` (log:53-56).
  C. All 14 known FlatSequenceInnerTunnel uids resolve through `UID to GObject Reference.vi`: self-echo class
     `FlatSequenceInnerTunnel`, owner `FlatSequence` uid 681, cast class `FlatSequence`, NO error (log:60-73).
  D. A backward wire walk from block diagram 10, Nodes[1] (uid 44036 = the ASI `Move Axis to Position.vi`
     startup call site), reading `Wire.Terminals[]` + `Terminal.Is Source?`:
       - terminal 8 `Position [internal units]`, wire 44089: ONE hop, Terms[0] is the source, err '',
         reciprocal wire 44089, owner = **`FlatSequenceOuterTunnel` uid 43605** (log:79-83).
       - terminal 9 `Axis`, wire 44104: one hop to `EnumConstant` uid 43955 (log:86-90).
       - terminal 10 `VISA in`, wire 44107: TWO hops - `SubVI` uid 43997 (`Initialize.vi`), then wire 44110 to
         `VISAResourceNameConstant` uid 43937 (log:93-102).
     In every case the walk stopped with the message "owner uid N of class C is NOT a node on any of the 170
     cached diagrams - the walk cannot address it as Diagram[d].Nodes[n]".

THE CLAIM UNDER ATTACK (three parts - attack whichever is weakest)
  1. "The backward walk CAN cross a flat-sequence frame boundary. LabVIEW returned the boundary object cleanly
     (`FlatSequenceOuterTunnel` uid 43605, no error); the only thing that stopped the walk is OUR OWN
     addressing scheme, which indexes objects as Diagram[d].Nodes[n] and therefore cannot name an object that
     is not in a diagram's Nodes[] array. Switching the walk to UID-addressed references removes the stop."
  2. "Because the four class-specific property ids attach to the class and all 14 instances resolve by UID, a
     one-op reader (UID -> To More Specific Class(FlatSequenceInnerTunnel) -> LeftTerm/RightTerm) would let the
     walk continue THROUGH a flat-sequence tunnel to the wire on the other side."
  3. "For a motor-safety check that must trace every value arriving at a motion call site back to its origin,
     the flat sequence is therefore not a hard barrier - it is a missing reader."

WHAT IS ALREADY RULED OUT (do not re-raise without a new reason)
  - Not a path or load problem: an open control `count(V6,'Diagram')` returned 170 in the same run (log:37),
    and the V6 copy's md5 was verified equal to the one the cached census was taken from (log:28).
  - Not an instrumentation default: the previous run's ambiguous "NO terminals at all" line was fixed - every
    `Wire.Terminals[]` iteration now prints its own error clusters, and the hops above printed err='' stage={}.
  - Not a stale uid: the seed wires come from a cached census of the same file, md5 verified equal.

WHAT I WANT FROM YOU
  1. The single strongest reason claim 1 is WRONG - in particular, whether `FlatSequenceOuterTunnel` uid 43605
     being the SOURCE of wire 44089 is even the right reading, and whether an OUTER tunnel of a flat sequence
     can be followed to the value that feeds it from the enclosing diagram at all.
  2. An alternative explanation for what was observed, and specifically: is there a documented relationship
     between `FlatSequenceOuterTunnel` and `FlatSequenceInnerTunnel` (ids, properties, short names) that the
     walk would need, given that B measured only the INNER tunnel class? Name the property ids if they exist.
  3. Name what would FALSIFY claim 2 - i.e. an observation showing that reading `LeftTerm`/`RightTerm` on a
     real instance does NOT yield a usable Terminal reference, even though the ids attach to the class.
  4. The CHEAPEST discriminating test, given that building a new scripting op costs a whole cycle here.



--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

1. **Strongest refutation:** the walk did not cross the boundary; it reached the frame-side endpoint of the boundary.

`Wire.Terminals[]` documents only the endpoints of that particular wire; its first entry is the source when one exists. Therefore the measured statement should be: “the source terminal of wire 44089 is owned by `FlatSequenceOuterTunnel` 43605,” not “the ultimate source is tunnel 43605.” [Wire.Terminals[] documentation](https://labviewwiki.org/wiki/Wire_class/Terminals%28%29_property)

A flat-sequence outer tunnel contains two distinct terminal references:

- `3195B800` — **Outer Terminal**, short name `Out Term`
- `3195B801` — **Inner Terminal**, short name `In Term`
- `3195B802` — **Frame**

The outer terminal belongs to the enclosing diagram’s wire; the inner terminal belongs to the frame’s wire. [FlatSequenceOuterTunnel class](https://labviewwiki.org/wiki/FlatSequenceOuterTunnel_class)

Thus `Is Source? = TRUE` is entirely plausible for the **inner terminal** feeding the motion call inside the frame. It says nothing about the source on the separate enclosing-diagram wire. Merely changing `Diagram[d].Nodes[n]` addressing to UID addressing does not cross between those two terminal objects. The walk must explicitly map:

```text
internal wire
→ source Terminal
→ owner FlatSequenceOuterTunnel
→ Outer Terminal (3195B800)
→ Terminal.Connected Wire (634A000)
→ that wire’s source
```

`Terminal.Connected Wire` is the documented way to obtain the wire attached to a returned terminal reference. [Terminal class](https://labviewwiki.org/wiki/Terminal_class)

2. **Alternative explanation**

The observed hop terminated normally at the internal face of an outer tunnel. LabVIEW represents the tunnel as the source of the internal wire because the tunnel forwards a value entering through a separate external wire. That is boundary arrival, not boundary traversal.

More importantly, B measured the wrong class for this occurrence:

- `FlatSequenceInnerTunnel` represents a connection between adjacent flat-sequence frames. Its properties are `Left Terminal` `1C3A9000`, `Right Terminal` `1C3A9001`, `Left Frame` `1C3A9002`, and `Right Frame` `1C3A9003`. [FlatSequenceInnerTunnel class](https://labviewwiki.org/wiki/FlatSequenceInnerTunnel_class)
- `FlatSequenceOuterTunnel` represents an enclosure/frame boundary and exposes `Outer Terminal` `3195B800` and `Inner Terminal` `3195B801`. [FlatSequenceOuterTunnel class](https://labviewwiki.org/wiki/FlatSequenceOuterTunnel_class)

The documented anatomy explicitly depicts these as different object and terminal pairs. [Flat-sequence scripting anatomy](https://rajsite.github.io/unofficial-lvdocs/lvconcepts/anatomy.html)

Consequently, the proposed operation

```text
UID 43605 → cast to FlatSequenceInnerTunnel → LeftTerm/RightTerm
```

should fail: 43605 was reported as `FlatSequenceOuterTunnel`, and the two tunnel classes are separate children of `GObject`, not parent/child classes. An invalid `To More Specific Class` cast returns a type-cast error; NI describes error 1057 as “Object cannot be cast to the specified type.” [NI error-1057 explanation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019OwLSAU&l=en-US)

The 14 successfully resolved inner-tunnel UIDs therefore do not validate traversal of outer tunnel 43605.

3. **What would falsify claim 2**

On a genuine `FlatSequenceInnerTunnel`, claim 2 is falsified if either `LeftTerm` or `RightTerm`:

- is `Not A Refnum`,
- raises a property/read or cast error,
- is not a `Terminal` reference,
- has no `Connected Wire` despite a visibly connected side,
- returns a connected wire whose `Terminals[]` does not reciprocally contain that terminal, or
- points to the wrong adjacent frame/diagram.

Property-node creation proves only that the property ID is valid for the class. It does not prove that a particular runtime reference is that class or that the returned terminal is connected and usable.

For uid 43605 specifically, an error from casting it to `FlatSequenceInnerTunnel` already falsifies the proposed one-op reader, although it would not disprove an appropriately typed **outer-tunnel** reader.

4. **Cheapest discriminating test**

Do not build the inner-tunnel reader first. Reuse the existing scratch property-node probe and test `VI Server:FlatSequenceOuterTunnel` with `3195B800`, `3195B801`, and `3195B802`. Then make one real-instance read of uid 43605 and, for both returned terminals, print:

```text
valid ref?
Terminal.Diagram
Terminal.Is Source?
Terminal.Connected Wire UID
Does that wire’s Terminals[] contain this exact terminal?
```

One known tunnel is enough. If `3195B801` reproduces wire 44089 while `3195B800` yields a different enclosing-diagram wire, the alternative is proven and the correct traversal is `Inner Terminal → tunnel → Outer Terminal`, not UID addressing or `LeftTerm/RightTerm`.

The broader conclusion—flat sequences need not be hard barriers—may ultimately hold. But the run did **not** establish it: it demonstrated arrival at an outer tunnel and separately characterized the unrelated inner-tunnel class.

## Sources

(extract from answer)

## What was done with it

**ACCEPTED, and the half it called "cheapest" was run immediately** (material session, cycle 19, 2026-09-18;
the opus arm of the same `-Dual` dispatch carries the full table). Both arms independently found the same
defect in the claim — the run had characterised `FlatSequenceInnerTunnel` while the walk actually stopped on
`FlatSequenceOuterTunnel`, a SIBLING class, not a parent.

- "Do not build the inner-tunnel reader first. Reuse the existing scratch property-node probe and test
  `VI Server:FlatSequenceOuterTunnel` with `3195B800`, `3195B801`, `3195B802`" → done,
  `tools/bench/probe_flatseq_outer.log`, 5/5 gates: all three ATTACH, short names **`OuterTerminal`**,
  **`InnerTerminal`**, **`Frame`**. And the discriminator this arm named — `1C3A9000` must not attach to the
  outer class — came back **error 1077**, confirming the two classes are separate.
- "Property-node creation proves only that the property ID is valid for the class. It does not prove that a
  particular runtime reference is that class or that the returned terminal is connected and usable." —
  **accepted as written, and the report to the judgement session says exactly this.** The live read of 43605
  (valid ref? → `Terminal.Diagram` → `Is Source?` → `Connected Wire` → reciprocity) is NOT done: it needs a
  UID → `To More Specific Class(FlatSequenceOuterTunnel)` → property reader, i.e. a new op, and this cycle was
  measurement-only. It is the one `OPEN:` item this cycle returns.
- Its prediction that casting 43605 to `FlatSequenceInnerTunnel` would fail was never tested and is recorded
  as still open; nothing was built on the assumption either way.

One claim of this arm was checked and holds: the 14 inner-tunnel UIDs that resolved
(`probe_flatseq_walk_run2.log:60-73`) say nothing about 43605. The separate negative control
(`tools/bench/probe_walk_stop_control.log`, 3/3) shows 43605 IS Traverse-visible and UID-addressable — which is
necessary for such a reader, not sufficient for the read.

(Claude fills in)
