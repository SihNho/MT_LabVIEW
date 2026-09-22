# c80-rowd-routeA-swapped

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** 
- **date:** 2026-09-22 11:01:41
- **outcome:** TIMEOUT (780s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# REFUTE THIS: "Route A - `OpConnectFromWire_v0` with the roles SWAPPED - cannot write Row D, in EITHER ordering"

You are the failed-prediction reviewer. A prediction of ours failed; the explanation we formed under
pressure is below. **Attack it.** Find the cheapest route we have MISSED, or show the claim is wrong.
Do not confirm. The failing log is `tools/bench/c80_rowd_routeA.log`; the script is
`tools/recipes/build_d1_m3a3.py`.

## The situation, in one paragraph

We are restructuring a LabVIEW VI by VI Scripting over COM (behaviour-preserving refactor: scheduling may
change, computation may not). One wire ("Row D", uid **7506**) carries a VISA session handle out of the
OLD `WhileLoop #637` / `RightShiftRegister #4334` and must instead come out of the NEW `WhileLoop #23032`
/ `RightShiftRegister #23868`. The SINK is `FlatSequenceInnerTunnel #7468`'s **LeftTerm, terminal uid
#7488**, which is in no `Nodes[]` (a `FlatSequence` is `Generic -> GObject -> FlatSequence`, measured, and
your predecessor could not break that). The SOURCE is the NEW loop's border terminal, addressable as
`Diagram` traverse index **19**, `Nodes[21]`, `Terminals[1]`, name `'Outgoing Handle'`, `Is Source?` True,
BARE.

Your predecessor's review (`archive/peer/2026-09-22-c79-rowd-writer.md`, ANSWERED) showed that our
"`Terminal.Connect Wire` 6349C03 is invoked ON THE SINK" rule is an ADOPTED CONVENTION, not a
measurement, and proposed **the swapped call**: give `OpConnectFromWire_v0`'s already-uid-addressed
SOURCE half (`wire_uid` + a `Wire.Terms[]` index, property 6371003) the FSIT TERMINAL #7488 - the true
SINK - and give its `(diagram, Nodes[], Terminals[])` triple the NEW loop's BARE border terminal - the
true SOURCE - so the Invoke sits on the BARE terminal and receives #7488 as `Wire Source`. WE RAN THAT
TEST, both orderings, each on its own dated scratch copy of the bed. Both failed.

## What the machine returned, VERBATIM (`tools/bench/c80_rowd_routeA.log`)

Both arms first measured the source half identically and correctly (`:93-98`, `:229-234`):
`OpWireSource_v5(UID 2 = 7506)` -> `t0 is_source=True owner_class='RightShiftRegister' owner_uid=4334`,
`t1 is_source=False owner_class='FlatSequenceInnerTunnel' owner_uid=7468`, plus one all-zero padding row.
So `Wire.Terms[]` index **1** is the FSIT terminal, PD85 violations 0. The invoke triple resolved live as
`[19, 21, 1]`, BARE, as predicted.

**ARM A1 - DELETE first, then the swapped call** (`:102`, `:119`). The delete succeeded
(`{'index': 821, 'gone': [7506]}`); #7488 then read wire 0 / BARE. The swapped call then returned:
`wire_delta 0`, `exec_state 0`, `op_error_verbatim ""`, and in the op's own sub-returns
`err_uidvi ''`, **`err_wirepn 'error 1055: Property Node in OpConnectFromWire_v0.vi'`**, `UID 2` **0**,
`Is Broken? False`, `Name ''`. #7488 stayed BARE after the write and after the junk purge.

**ARM A2 - the swapped call while wire 7506 is ALIVE, then delete** (`:237`, `:239`). The call returned
`wire_delta 0`, `exec_state 0`, `op_error_verbatim ""`, `err_uidvi ''`, `err_wirepn ''`, and in its own
ORDERED readback (the op's gate W7b orders `Wire.Is Broken?` 6371004 AFTER the write):
**`UID 2` = 7506**, **`Name` = 'Outgoing Handle'**, **`Is Broken?` = True**. `wire_delta` 0, i.e. NO NEW
`Wire` OBJECT. We then deleted 7506 (it reported success), after which #7488 read wire 0 / BARE.

**Step 4, FACT-ONLY** (`:289-290`): handing the op the TERMINAL uid **7488** in its uid slot with the
index triple deliberately out of range returned `err_uidvi ''` (EMPTY) and
`err_wirepn 'error 1055: Property Node'`.

## The conclusion we drew, which you must attack

> (1) Route A is DEAD in both orderings. A1 dies because the op's source half reads `Wire.Terms[]` on the
> `wire_uid` it is given, and after the delete that uid is not a live `Wire`, so the property node raises
> 1055 and nothing is written. A2 dies because, with the wire alive, the swapped call does not CREATE a
> wire at all: `wire_delta` 0 and the op's own readback naming `UID 2` = **7506** (the pre-existing wire)
> with `Is Broken?` **True** mean it BRANCHED / extended the existing net - precisely the silent-branch
> failure mode your predecessor predicted - giving a net with TWO sources (`#4334` and the new loop
> border) which LabVIEW marks broken; deleting 7506 then removes the whole net and leaves both ends bare.
> (2) Therefore Pre-decided 116-A ("if A works, Row D proceeds on it and nothing new is built") is
> REFUTED by measurement, and Row D needs Route B: `OpConnectByUid` (uid -> `UID to GObject
> Reference.vi` -> TMSC on a **Terminal** seed -> the Invoke's `reference`), donor `OpConnectNested_v2`.
> (3) Separately: `err_uidvi` came back EMPTY on a *deleted* wire uid in A1 AND on the terminal uid in
> step 4, so "empty `err_uidvi`" does NOT establish that a uid resolved, and step 4 therefore does NOT
> clear Route B's first gate. Route B's uid-resolution assumption is still UNMEASURED.

## ALREADY RULED OUT - do not propose these

(a) A `Nodes[]`/index address for #7468 or #7488 - measured impossible (CLASS, not owner: 173/173
    diagrams, 635 nodes, `find_node` misses all three FlatSequences).
(b) An owner walk from the tunnel upward - `OpOwnerChain_v1` terminates SILENTLY at a
    `FlatSequenceFrame` (error 1055, `owner_uid` 0, empty cast echo; `docs/toolkit-capabilities.md:61`).
(c) A GUI fallback (clicking the wire) - forbidden for this work by a standing project decision.
(d) Re-pointing Row D at a different sink, or inserting/moving any structure, tunnel, Local or shift
    register - a STRUCTURAL change of the original's computation, refused by our rule 1a.
(e) `Tunnel.Inside Terminals[]` 6356000 / `Tunnel.Outside Terminal` 6356001 - DEAD BY CITATION, a
    `FlatSequenceInnerTunnel` is not a `Tunnel`; its properties are `Left Terminal` 1C3A9000 /
    `Right Terminal` 1C3A9001. `Node.Connect Wires` needs both ends to be `Node`s; `Create Described
    Wire` is itself a `Terminal` method.

## The questions, answer ALL of them explicitly

1. **Is our reading of ARM A2 right?** Does `UID 2` = the OLD wire uid + `Name` = 'Outgoing Handle' +
   `Is Broken?` True + `wire_delta` 0 really mean "branched the existing net and broke it"? Name at
   least one ALTERNATIVE reading of those four values (e.g. the readback reporting a stale/cached
   object, or `Connect Wire` having silently declined and the readback describing the wire it was
   merely *shown*), and say which reading the cheapest measurement would separate.
2. **Is there any ordering or parameterisation of the SWAPPED call that still works?** e.g. deleting
   only part of the net first; passing `Wire.Terms[]` index 0 (the `#4334` source row) instead of 1;
   invoking on the FSIT side with the BARE loop terminal as `Wire Source` (the ORIGINAL role
   assignment, which we have NEVER run because we had no uid-addressed sink - but the op's triple can
   address the loop border, and its uid half can address... only a wire). Say concretely why each does
   or does not work.
3. **Route B's first gate, now that step 4 is inconclusive:** what is the cheapest READ that actually
   establishes whether `UID to GObject Reference.vi` resolves a TERMINAL uid (#7488) as opposed to a
   tunnel or wire uid? Name the op and the exact indicator to read, and why that indicator is sound
   where `err_uidvi` is not.
4. **Is Route B even the smallest remaining shape?** If not, name what is.

## Output contract

In this order and nothing else:
- **STRONGEST REASON THE CONCLUSION IS WRONG** (one paragraph).
- **ALTERNATIVE EXPLANATION / ALTERNATIVE ROUTE** - concrete, or "none found, and here is the search I ran".
- **WHAT WOULD FALSIFY** the claim that Route A is dead in both orderings.
- **CHEAPEST DISCRIMINATING TEST** - read-only or scratch-copy, naming the exact op, inputs and the one
  indicator to read, settling it in under ~2 minutes.
- **VERDICT**: `ROUTE-A-ALIVE: <the exact call>` or `ROUTE-A-DEAD: <the smallest next shape>`.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

(no answer within 780s — job stopped)

## Sources

(extract from answer)

## What was done with it

**CLASSIFIED: TIMEOUT (780 s) — A NON-RESULT. It told us nothing and discharged nothing** (CLAUDE.md §5:
*"a call that failed, timed out or hit quota told you NOTHING"*). Nothing was read from it and nothing was
decided on it. The identical task file (`tools/bench/c80_rowd_routeA_task.txt`) was re-dispatched the same
minute with a 28-minute budget (`-TimeoutSec 1680`, bgrun `--max-min 32`) and **ANSWERED in 689 s** —
`archive/peer/2026-09-22-c80-rowd-routeA-swapped-r2.md` is the review of record for
`tools/bench/c80_rowd_routeA.log`, and its disposition is written there. Cause of the timeout: the task
carries four questions plus a verbatim evidence block, and 780 s (`peer.ps1`'s STATUS-recommended floor)
was simply under the answer's cost — the same task at 1,680 s needed 689 s, so nothing about the question
was wrong. Kept for the cost record only.
