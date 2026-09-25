---
type: peer-review
status: historical
date: 2026-09-17
tags: [peer-review, archive, labview]
disposition: legacy
legacy_note: closed as legacy 2026-09-25 by card chat-L1 (cutoff 2026-09-22; user 2026-09-25 lint order before runner resume)
---

# moveinto-p1-execstate0

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-17
- **outcome:** ANSWERED (227s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

FAILED PREDICTION. Attack the diagnosis below; I am not asking whether it sounds reasonable.

WHAT WAS PREDICTED. tools/recipes/probe_move_into_v0.py gate P1: "OpMoveIn_v0.vi builds from OpMoveOut_v0.vi
(reference <- a UID-addressed GObject; owner <- the existing Traverse-'Diagram'[index] cast) and reads
ExecState 1."

WHAT WAS OBSERVED (tools/bench/probe_move_into_v0.log, run 2, the lines after the last BGRUN START):
  FACT Move Invoke uid 741: SINK owner = index 8 wire 872, SINK reference = index 0 wire 464
       (all 'owner' rows: [(8, False, 872), (9, True, 0)])
  FACT owner wire 872 is driven by [(744, 4, 'Diagram', True)]
  FACT deleted wire 464 (old Move.reference source)
  FACT deleted Property[0] uid 744 (old Move.owner source)
  FACT after the deletes, Move.owner SINK wire = 0 (bare, required)
  FACT Diagram cast uid 683 is Function[0], output terminal 'specific class reference'
  FACT wired Diagram cast -> Move.owner (branch)
  PASS P1a Move.owner is now driven by the Diagram cast  owner wire 645, other ends
       [(683,0,'specific class reference',True), (243,0,'Diagram in',False), (235,0,'reference',False)]
  FACT U2G terminals: [(0,'error out',T),(1,'',F),(2,'GObject',T),(3,'dup Owning VI',T),(4..7,'',F),
       (8,'error in (no error)',F),(9,'',F),(10,'UID',F),(11,'Owning VI',F)]
  FACT VI reference wire 467; its source terminal is 'vi reference' of node uid 43
  FACT wired the VI reference -> U2G 'Owning VI' (branch)
  FACT UID control created: 'UID 3' ([968])
  FACT wired U2G 'GObject' -> Move.reference
  **FAIL** P1 OpMoveIn_v0 builds and is runnable  ExecState 0
Every wire the script asked for was made, no exception was raised, and the script had already called
set_auto_error_handling(False) and then remove_bad_wires_scripted() before re-reading ExecState. It is still 0.

MY TWO COMPETING EXPLANATIONS, and I want them attacked, not ranked:
 (A) The creators' junk. OpConnect2/OpCreateControl carry the erdosmiller creator, which drops an untyped Invoke
     node on the TARGET per call (docs/keystone-op-spec.md:567-573 s33). docs/NAMES.md:307-313 states that an
     Invoke node with an unwired `reference` makes a VI non-executable even when every wire is good, and that
     Remove Bad Wires reports nothing - three OpBuildBA runs died this way. Phase 1 of this probe has NO purge on
     OpMoveIn_v0 (a purge was added in rev 6, but only on the PHASE 2 scratch copy, not on the op being built).
     Prediction if true: OpMoveIn_v0.vi on disk carries N>0 Invoke nodes that OpMoveOut_v0.vi does not.
 (B) A real type break at one of the two new wires - the Diagram-typed 'specific class reference' into
     GObject.Move's `owner`, or U2G's `GObject` into `reference`. Against it: the donor fed `owner` from
     VI.Block Diagram (also a Diagram reference), and the same cast output already feeds 'Diagram in' and a
     property node's 'reference' on the same wire (P1a's other-ends list).

ALREADY RULED OUT (do not re-raise):
 - the terminal-identification defects of run 1 (net_map truncation; name-only keying) - fixed, and P1a now
   proves `owner` is carried by a wire whose source is the Diagram cast, uid 683;
 - a silently declined connect on `owner` - P1a asserts the post-connect wiring, not the call's return;
 - the original VI - it is never opened for writing; md5 2a78e17c449cacdaf5da389818526859 verified before.

WHAT I NEED: the strongest reason BOTH of these are wrong; a third explanation for "every requested wire exists,
Remove Bad Wires changes nothing, ExecState stays 0" on a scripted LabVIEW VI; what would falsify (A); and the
single cheapest read that separates them. Note this project has no reader for WHY a VI is broken - VI.Get Errors
(method 452) is recorded as having FAILED twice here - so name a test that uses ordinary Traverse/property reads
if you can.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

1. **Strongest reason the A-or-B diagnosis is wrong**

Neither hypothesis accounts for the destructive graph changes. The log proves the two replacement sinks are connected, but it never reports **all terminals formerly attached to wire 464 before deleting that Wire object**.

A LabVIEW wire is one net with one source and potentially many sinks. Deleting the Wire object can therefore disconnect sinks other than `Move.reference`. If one was required, the result is exactly:

- both requested replacement wires exist;
- no broken wire remains for Remove Bad Wires to remove;
- `ExecState` remains 0 because a required terminal elsewhere is now bare.

NI explicitly distinguishes an unwired required terminal from a broken wire, and Remove Broken Wires addresses only the latter. [NI: wiring and wire branches](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html), [NI: common causes of broken VIs](https://www.ni.com/en/support/documentation/supplemental/12/debugging-techniques-in-labview.html).

Thus “every requested wire exists” is not evidence that the resulting graph preserved every required connection.

2. **Attack on each proposed explanation**

**(B) is substantially contradicted by the observations.** A datatype/class conflict produces a broken wire. NI says Remove Broken Wires deletes broken wires, yet both replacement wires survived that operation and were subsequently found connected. A direct scripted check is available as `Wire.Is Broken?`. [NI wiring documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html), [Wire scripting properties](https://labviewwiki.org/wiki/Wire_class).

The declared types also argue against B:

- `Diagram` inherits through `AbstractDiagram` from `GObject`.
- `Move` is a `GObject` method whose `owner` parameter takes an owning object.
- U2G’s output is already reported as `GObject`, matching the receiver of `GObject.Move`.

[VI Server class hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy), [Diagram inheritance](https://labviewwiki.org/wiki/Diagram_class), [GObject.Move contract](https://labviewwiki.org/wiki/GObject_class/Move_method).

B survives only if Remove Bad Wires operated on a different loaded instance, or if the post-cleanup wires report `Is Broken? = TRUE`. Endpoint existence alone is weaker than reading that property.

**(A) is not yet a diagnosis; it is an untested count prediction.** Calling the creators does not establish that extra Invoke nodes survived in the saved, subsequently loaded file. Conversely, finding an extra unwired Invoke would establish that A’s mechanism is present, but not that it is the only break. NI confirms that an Invoke node can break a VI through an unwired/bad terminal. [NI Invoke-node broken-VI example](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019N7CSAU&l=en-US).

**What falsifies A:** a cold traversal of the saved files showing that `OpMoveIn_v0.vi` and `OpMoveOut_v0.vi` have identical Invoke-node signatures—apart from intentionally changed nodes—and that `OpMoveIn_v0.vi` has no additional Invoke whose reference terminal has no connected wire. The scripting API exposes Invoke input terminals and each terminal’s connected wire. [Invoke properties](https://labviewwiki.org/wiki/Invoke_class), [Terminal connected-wire property](https://labviewwiki.org/wiki/Terminal_class/Connected_Wire_property).

3. **Alternative explanation**

The strongest third explanation is **collateral disconnection caused by deleting wire 464 as a whole net**. Read the donor’s `Wire.Terminals[]` for wire 464. If it had any sink besides `Move.reference`, that sink was also removed; if required, it alone explains `ExecState 0`. `Wire.Terminals[]` is explicitly available through VI Scripting. [Wire properties](https://labviewwiki.org/wiki/Wire_class).

A second read-only alternative is a broken or stale-linked subVI—particularly U2G. A caller is broken when a subVI is broken or its connector pane changed after placement, even when every visible caller wire is sound. [NI debugging guidance](https://www.ni.com/en/support/documentation/supplemental/12/debugging-techniques-in-labview.html). Ordinary properties can test `SubVI.Bad SubVI Linkage`, `Missing VI Path`, obtain its `VI Reference`, and then read the callee’s execution state. [SubVI scripting properties](https://labviewwiki.org/wiki/SubVI_class).

After attacking both: B is presently inconsistent with the cleanup-and-survival evidence. A remains plausible, but the supplied log has not yet performed A’s own decisive observation.

4. **Cheapest discriminating test**

Cold-load the saved `OpMoveIn_v0.vi` and `OpMoveOut_v0.vi`, Traverse **only class `Invoke`**, and compare `(class name, method, reference-terminal Connected Wire)`.

- Extra bare-reference Invoke(s) only in `OpMoveIn_v0`: A’s predicted artifact exists.
- No Invoke delta: A is falsified; inspect donor wire 464’s `Terminals[]` next for collateral sink loss.

That Invoke-only differential is the cheapest read because it tests A’s exact prediction without opening the Error List, invoking `Get Errors`, or modifying either VI.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)

## What was done with it

ANSWERED (codex, 227 s), and its **third explanation was the right one** — neither of my two was. The review's own
cheapest discriminating read was run immediately: `tools/bench/diag_movein_p1_break.py` (read-only, nothing built,
scratch copy deleted in the same run, MAIN md5 unchanged) → `tools/bench/diag_movein_p1_break.log`,
`tools/bench/movein_p1_break.json`. 5 pass / 0 fail, 2 s.

MEASURED, on an untouched copy of `OpMoveOut_v0.vi`:

* **(C) CONFIRMED — wire 464 is one net with ONE source and THREE sinks.** `OpWireSource_v5` over
  `Wire.Terms[]`: source `IndexArray` **#236**; sinks `Property` **#237**, `Property` **#240**, `Invoke` **#741**
  (the Move). `probe_move_into_v0.py` deletes the whole Wire object to bare `Move.reference`, so it also bares
  the `reference` inputs of property nodes #237 and #240 — a REQUIRED input on each. That is exactly the
  signature observed: both replacement wires exist, nothing is broken for Remove Bad Wires to remove, and
  `ExecState` stays 0. The peer's distinction between an unwired required terminal and a broken wire is the whole
  explanation.
* **(A) FALSIFIED.** `report_all('Invoke')` on both files: donor `[741]`, `OpMoveIn_v0` `[741]` — **zero extra
  Invoke nodes**. The creators left no junk on this target, so the missing phase-1 purge is not the cause. (The
  purge added in rev 6 for the phase-2 scratch stays; it is right for a different reason.)
* **(B) not needed.** The peer's type argument stands unchallenged and the measurement never reaches it.
* The peer's second alternative (stale/broken subVI link) is also negative: `subvis()` shows `OpMoveIn_v0` with
  `UID to GObject Reference.vi` #148 present alongside the donor's three calls, Node 15 / Wire 29 on both.

WHAT THIS LEAVES FOR JUDGEMENT (not decided here): the repair is to stop deleting wire 464 as a net — either bare
only the Move's own terminal, or re-wire `#237.reference` and `#240.reference` from `IndexArray#236` after the
delete. Both change the probe's construction, the probe's failure budget of 2 is spent, and which one is correct
is a design call.
