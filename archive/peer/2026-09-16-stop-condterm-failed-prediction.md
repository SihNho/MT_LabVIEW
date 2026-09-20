# stop-condterm-failed-prediction

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-16
- **outcome:** ANSWERED (126s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

FAILED PREDICTION, cycle 15 step 1(b)(iv). Attack the framing below, do not confirm it.

CONTEXT. `Min_Track N beads V6_ParallelLoop.vi` (LabVIEW 2026, read-only, md5 unchanged). Its frame loop is
`WhileLoop` uid 637; the loop BODY diagram is uid 639 = Traverse 'Diagram' index 43. Two front-panel Booleans exist,
`stop (end)` (control uid 7, diagram wire 6929) and `stop (end) 2` (control uid 19587, wire 15230).

WHAT WAS PREDICTED (P5, tools/bench/diag_stop_save_seam.py): the node that the OR-ed `stop (end) 2` wire 15229
feeds - uid 22082 - would be a loop CONDITIONAL terminal class, i.e. the stop Boolean would terminate the frame
While loop directly.

WHAT WAS MEASURED (tools/bench/diag_stop_save_seam.log, 29/30 gates; OpWireSource_v5 = wire uid -> the terminal
with `Is Source?` TRUE whose reciprocal `Connected Wire` is that wire; OpOwnerChain_v1 = uid -> Generic.Owner):
  * wire 6929  source owner ('Diagram', 639)          sinks [('CompoundArithmetic', 11639)]
  * wire 15230 source owner ('Diagram', 639)          sinks [('CompoundArithmetic', 17883)]
  * wire 3457  source ('CompoundArithmetic', 11639)   sinks [('Diagram', 639), ('Diagram', 639)]
  * wire 15229 source ('CompoundArithmetic', 17883)   sinks [('Tunnel', 22085)]
  * owner chains: 11639 -> Diagram#639 -> WhileLoop#637; 17883 -> Diagram#639 -> WhileLoop#637;
    22082 -> Diagram#639 -> WhileLoop#637, and 22082's own class reads `CaseStructure`, NOT a terminal class.
  * an independent full terminal census of all 626 nodes on all 170 diagrams
    (tools/bench/main_vi_nodeterms.json, 2026-09-14, same md5) contains NO node terminal on wire 3457 other than
    11639's `result`, and no node terminal on 6929/15230 other than the two CompoundArithmetic inputs.

THE FRAMING I AM ABOUT TO WRITE INTO A FACTS DOCUMENT, WHICH IS WHAT YOU SHOULD TRY TO BREAK:
  (1) both stop Booleans' diagram terminals sit ON the loop body diagram 639, therefore they are read on EVERY
      iteration rather than once through a pre-loop tunnel;
  (2) `stop (end) 2` does not stop the loop directly - it enters an input Tunnel (22085) of CaseStructure 22082
      inside the loop body;
  (3) wire 3457's two sinks are both reported with owner class `Diagram`#639 and are claimed by no node in the
      626-node census, so ONE OF THEM IS THE WHILE LOOP'S CONDITIONAL TERMINAL and the original therefore has a
      working in-loop Boolean stop. This third point is an INFERENCE from "owner is the diagram and no node claims
      it", not a direct read: no reader for `WhileLoop.Condition Terminal` exists in this toolkit.

Give me: the strongest reason (1)-(3) is wrong; at least one alternative explanation of the same measurements -
in particular, what ELSE in LabVIEW 2026 scripting is a terminal whose `Generic.Owner` is the Diagram and which no
node's `Terminals[]` enumerates (front-panel control/indicator terminals? a structure's own conditional or selector
terminal? something else?); whether a terminal sitting on the body diagram really implies a per-iteration read
(can a control terminal be placed inside a loop body and still be read once?); and what would falsify (3).
Then name the CHEAPEST DISCRIMINATING TEST that an existing reader can run - the toolkit has: GObject.Owner by uid,
Wire.Terms[] with Is Source?/Connected Wire by wire uid, Diagram.Nodes[] terminal lists by (diagram index, node
index), a front-panel object census that returns each panel object's label, uid and connected wire uid, and
`Loop.Shift Registers[]` through a WhileLoop-typed cast. If the only route is a new property reader, say which
property ID and on which class, and say plainly that no existing reader suffices.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

1. The strongest defect is that (3) treats a non-unique scripting signature as identification. “Terminal owner is Diagram and absent from every node’s `Terminals[]`” does **not** uniquely mean “While Loop conditional terminal.” Front-panel `ControlTerminal` objects have exactly that behavior: their generic owner is the diagram, not the corresponding front-panel control/indicator or a diagram node. This is explicitly described by NI’s Darren Nattinger in an accepted VI Scripting answer. [NI Community: wire terminal ownership](https://forums.ni.com/t5/LabVIEW/Vi-Scripting-inconsistent-behaviour-of-terms-of-a-wire-owner/td-p/3309055)

Therefore, the safe wording is: “wire 3457 has two diagram-owned sinks not claimed by `Diagram.Nodes[]`; one may be the loop conditional terminal.” The measurements do not establish “one is.”

2. A concrete alternative explanation is that one or both sinks are front-panel indicator terminals. A front-panel control terminal is a wire source; an indicator terminal is a sink, and both are represented on the block diagram as `ControlTerminal` objects rather than node terminals. [NI’s block-diagram documentation](https://www.ni.com/en/support/documentation/supplemental/08/labview-block-diagram-explained.html) This produces precisely the reported combination:

- terminal is a sink of wire 3457;
- `Generic.Owner` is Diagram 639;
- no entry in any node’s `Terminals[]` claims it.

Another unresolved category is a loop-owned special terminal—particularly the loop end/conditional terminal itself—but “diagram-owned” does not distinguish it from a `ControlTerminal`. I would not claim that Case selector terminals share this signature without a direct class read; the measured Case input already appears as the distinct `Tunnel` object 22085.

The available shift-register reader also matters: a right-hand shift-register element could consume an in-loop value. Checking `Loop.Shift Registers[]` can eliminate that possibility, but it cannot positively identify the conditional terminal unless the returned references expose their connected wires.

On (1): placement directly on body Diagram 639 does support per-iteration sampling at the language level. NI’s While Loop instructions specifically place the Stop control terminal inside the loop, while explaining that data entering through an external tunnel is supplied on the first iteration. [NI: Build and Configure a While Loop](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YJYUCA4) NI’s tutorial also demonstrates changing controls while a loop runs and seeing the results update. [NI LabVIEW tutorial](https://learn.ni.com/learn/article/labview-tutorial)

Thus, a control terminal directly owned by the loop-body diagram is not a pre-loop-tunnel read. It might repeatedly return the same Boolean value, and its precise sampling moment within an iteration is not ordered unless data dependencies impose ordering, but semantically it is available from inside each iteration. I see no credible “placed directly on Diagram 639 but read only once” alternative in the supplied topology.

On (2): the evidence supports it. Wire 15229 has only Tunnel 22085 as its sink, and that tunnel belongs to CaseStructure 22082. Nothing supplied connects that branch directly to WhileLoop 637’s end terminal.

3. The decisive falsification of (3) would be:

> `WhileLoop#637.Loop End Ref.Connected Wire` is not wire 3457, including an invalid/unwired reference.

A cheaper sufficient falsifier would be the existing front-panel census showing that **both** wire-3457 sinks correspond to front-panel indicators. One matching indicator only explains one branch and leaves the other unidentified.

No existing reader listed can conclusively identify the conditional terminal. The necessary new reader is the WhileLoop-class property:

- Property: `Loop End Ref`
- Property ID: `0x06362C00`
- Target: WhileLoop uid 637
- Then read the returned terminal’s `Connected Wire` and compare its UID with 3457.

The community-maintained scripting class table documents this property and ID, and an NI forum discussion independently identifies `Loop End Ref` as the route to the conditional terminal. [WhileLoop property table](https://labviewwiki.org/wiki/WhileLoop_class), [NI Community discussion](https://forums.ni.com/t5/LabVIEW/VI-Scripting-locate-loop-iteration-and-conditional-terminals/td-p/4344904)

**Cheapest discriminating test:** search the already-existing front-panel census for every object whose connected wire UID is 3457. If it returns two indicators, (3) is false and the alternative is confirmed. If it returns zero or one, the test is inconclusive; the conclusive next step is the new `WhileLoop.Loop End Ref` (`0x06362C00`) reader.

## Sources

(extract from answer)

## What was done with it

**Outcome: ANSWERED (126 s, rc 0) — the review was ACCEPTED, and its discriminating test was run the same turn.**
The inference it attacked ("a diagram-owned terminal that no node claims must be the loop's conditional
terminal") was withdrawn: the reviewer showed the same signature belongs to front-panel `ControlTerminal`
objects, so it identifies nothing.

Its cheapest test — the existing front-panel census, looking for wire 3457 — was run as
`tools/bench/diag_stop_condterm_panel.py` (`…panel.log`, 30 s, main VI md5 unchanged). Result: **one** of wire
3457's two sinks is the front-panel indicator `TurnOff` (uid 24423); wire 15229 and `Tunnel#22085` are carried by
no panel object. Per the reviewer's own rule ("one matching indicator only explains one branch"), that is
**inconclusive**, so the claim is written as open in `docs/main-vi-stop-and-save.md:§1` rather than as a fact.

Adopted and carried forward: the conclusive read is a **new op** for `WhileLoop.Loop End Ref` **0x06362C00** on
uid 637, then that terminal's `Connected Wire` vs 3457. Not built in this cycle (measurement-only brief, and the
cycle-15 plan freezes new op VIs) — recorded under STATUS OPEN for the judgement session.
