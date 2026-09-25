---
type: peer-review
status: historical
date: 2026-09-17
tags: [peer-review, archive, labview]
disposition: legacy
legacy_note: closed as legacy 2026-09-25 by card chat-L1 (cutoff 2026-09-22; user 2026-09-25 lint order before runner resume)
---

# flatseq-tunnel-source-addressing

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-17
- **outcome:** TIMEOUT (180s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

LabVIEW VI Scripting. A prediction failed and the explanation I formed under pressure needs attacking.

## The measurement (read-only, on the real VI, `tools/bench/diag_tunnelsource_onehop.log`, 7 pass / 2 fail)

We are restructuring one big VI: a frame loop (`While` uid 637, body diagram at Traverse index 43) is being split
into four parallel While loops that all sit on the SAME parent diagram (Traverse index 19, whose owner class is
`FlatSequenceFrame` - it is one frame of the top-level flat sequence). Nodes are reparented into the new loop
bodies with `GObject.Move`; every wire the move cut must then be re-created.

18 of the cut inputs were fed, in the original, by a `LoopTunnel` on the old loop's border. For each I read the
tunnel's OUTSIDE wire and walked `Wire.Terminals[]` with `Is Source?` + `Generic.Owner` (property reads, no edit).
The owner of the single SOURCE terminal came back as:

  * **14 rows: `FlatSequenceInnerTunnel`** (e.g. wire 3853 Terms[0] source=True owner FlatSequenceInnerTunnel 3862)
  * **2 rows: `LeftShiftRegister`** of the old frame loop (uids 9025, 29512) - registers that STAY in loop 1.1
  * **1 row: `SubVI`** uid 27605 on diagram 19 - resolved to (diagram 19, Nodes[16], Terminals[0])
  * 1 row: the hop did not advance (`#376` t7; its outer wire's source is reported by an older census as a
    terminal of the loop node 637 itself)

## The claim I want refuted

> The 16 non-`SubVI` rows cannot be re-wired with the wire creator this project has: `OpConnectNested_v1.vi`
> invokes `Terminal.Connect Wire` (6349C03) with BOTH ends addressed as
> `Diagram[d].Nodes[n].Terminals[t]`. A `FlatSequenceInnerTunnel` and a `LeftShiftRegister` are **not** nodes on
> diagram 19, so neither can be named as the `Wire Source`. Therefore the relocate-and-re-wire route ("route A")
> cannot close its re-wire with the ops that are authorised, and the values that enter the frame-loop diagram from
> the enclosing sequence frame have no addressable source terminal at all.

Already ruled out here, so do not propose them as if they were new:
  * name-addressed wiring (`Get Controls.vi` / `Get Outputs.vi` wrappers) - it fails 5001 on unnamed terminals,
    and 8 of these terminals have an empty name;
  * `connect_terminals` / `connect2` - both take a TOP-LEVEL source only;
  * wiring from the old tunnel's INNER terminal (inside loop 1.1's body) into the new loop's body - that would
    create a data dependency between two loops meant to run in parallel, which is a design defect, not a fix.

## Attack these, specifically

1. Is there a scripting route that names a **tunnel terminal** or a **shift-register terminal** as the SOURCE of
   `Terminal.Connect Wire`? Vendor-documented property/method names and IDs, please - e.g. is
   `Tunnel.Inside Terminals[]` / `Outside Terminal`, `ShiftRegister.Terminals[]`, or a `Diagram.Terminals[]`
   enumeration reachable, and does a terminal reference obtained that way work as `Wire Source`?
2. Is my premise wrong that a `FlatSequenceInnerTunnel` is not addressable through `Diagram[d].Nodes[n]`? Could
   the enclosing `FlatSequence` structure node (on the top-level diagram) expose that same terminal in its own
   `Terminals[]`, so the wire could be made from the outer side and LabVIEW would create the inner tunnel?
3. What is the cheapest experiment that would DISCRIMINATE between "no route exists" and "a route exists we have
   not tried"? Name the exact property/method chain to run on a scratch VI.
4. A wire's source terminal reference can also be obtained from `Wire.Terminals[]` + `Is Source?`. If that
   reference is fed straight into `Terminal.Connect Wire`'s `Wire Source` input, does LabVIEW accept it for a
   terminal whose owner is a tunnel or a shift register? Any evidence either way.

Answer with citations (NI documentation, labviewwiki, forum threads, the VI Server property/method IDs).


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

(no answer within 180s — job stopped)

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
