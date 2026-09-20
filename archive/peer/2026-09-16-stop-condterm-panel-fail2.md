# stop-condterm-panel-fail2

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-16
- **outcome:** ANSWERED (106s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

SECOND FAILED PREDICTION in the same class, cycle 15 step 1(b)(iv). Attack the conclusion I am about to write.

RUN: tools/bench/diag_stop_condterm_panel.log / tools/bench/diag_stop_condterm_panel.py (30 s, 3/4 gates).
It was the discriminating test the previous review (archive/peer/2026-09-16-stop-condterm-failed-prediction.md)
named as cheapest: take the existing front-panel census (`panel_wiring`: every top-level front-panel object with
its diagram terminal's connected wire uid) on the read-only main VI and look for wire 3457.

PREDICTED (Q2): NO front-panel object carries wire 3457 or 15229 - i.e. both of wire 3457's diagram-owned sinks
would be non-panel terminals.
MEASURED: wire 3457 IS carried by exactly ONE panel object, the INDICATOR `TurnOff` (uid 24423). Wire 15229 is
carried by none. The two stop controls read back exactly as recorded (`stop (end)` uid 7 wire 6929, `stop (end) 2`
uid 19587 wire 15230). Main VI md5 unchanged.

STANDING FACTS (tools/bench/diag_stop_save_seam.log, OpWireSource_v5 / OpOwnerChain_v1):
  wire 3457 source = CompoundArithmetic#11639 (fed by `stop (end)` wire 6929), sinks = TWO terminals, both with
  owner class `Diagram`#639 (the frame While loop's body diagram; the loop is WhileLoop#637). The 626-node
  terminal census claims neither sink. panel_wiring now attributes ONE of the two to indicator `TurnOff`.

THE CONCLUSION I AM ABOUT TO WRITE, WHICH YOU SHOULD TRY TO BREAK:
  "wire 3457 fans out from the `stop (end)` OR to the front-panel indicator `TurnOff` AND to exactly one other
   diagram-owned terminal that nothing in the toolkit can name; the second sink is therefore still the open
   candidate for WhileLoop#637's conditional terminal, and the question cannot be closed without a new reader
   for `WhileLoop.Loop End Ref` (0x06362C00)."

Attack it on these points specifically:
 (a) is "exactly one other sink" even safe? A fan-out in LabVIEW is one Wire object with many terminals, but a
     branch across a structure border is a SEPARATE Wire object - so could wire 3457's true sink set be larger or
     smaller than the two terminals `Wire.Terms[]` reported, and would that change the conclusion?
 (b) could BOTH reported sinks be the same panel indicator counted twice (e.g. a terminal and its own owner), or
     could `panel_wiring` miss a panel object that carries 3457 - it is documented as NOT recursive (tab pages and
     cluster elements are not rows)?
 (c) is there any reader ALREADY in this toolkit that could name the second sink without building a new property
     node: GObject.Owner by uid, Wire.Terms[] (Is Source? / Connected Wire) by wire uid, Diagram.Nodes[] terminal
     lists by (diagram index, node index), the front-panel census above, `Loop.Shift Registers[]` via a
     WhileLoop-typed cast, and a node-LABEL reader for every node on a diagram?
 (d) if a new reader really is required, is `Loop End Ref` 0x06362C00 on class WhileLoop the right one, or is the
     conditional terminal reached another way in LabVIEW 2026 - and what is the cheapest way to verify the ID
     before building anything on it?
Name what would falsify the conclusion and the cheapest test that separates the surviving explanations.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

The conclusion is wrong because it treats a nonrecursive panel census as exhaustive. `Diagram` ownership does not distinguish a loop conditional terminal from a front-panel `ControlTerminal`: LabVIEW control terminals are diagram-owned, exactly matching the observed ownership of `TurnOff`. [NI’s Darren explains this ownership behavior explicitly.](https://forums.ni.com/t5/LabVIEW/Vi-Scripting-inconsistent-behaviour-of-terms-of-a-wire-owner/td-p/3309055)

### (a) “Exactly one other sink”

That wording is safe only as:

> “Wire 3457 has exactly one additional **direct, distinct, non-source terminal reference**.”

`Wire.Terminals[]` returns the terminals connected to that wire object; LabVIEW permits one source and multiple sinks. [Wire property reference](https://labviewwiki.org/wiki/Wire_class) [NI wiring documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)

A structure-border crossing can lead to another wire object whose downstream sinks are not in wire 3457’s `Terminals[]`. Therefore the complete signal fan-out may be larger, but wire 3457’s direct sink count is not. That distinction does not support identifying the remaining direct sink as the conditional terminal.

It could be smaller only if the reporter counted the same reference twice or misclassified the source. Before writing “exactly one other,” compare the two non-source terminal references for equality—not merely their owner class, wire UID, or coordinates.

### (b) Alternative explanation

The strongest alternative is:

> The unmatched sink is another front-panel `ControlTerminal`, belonging to a control or indicator nested on a tab page and omitted by `panel_wiring`.

NI documents that controls within tab pages require walking the tab’s `Pages` and each page’s `Controls[]`; a top-level census does not reach them. [NI tab-control traversal documentation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019O8LSAU) Controls placed on tab pages still have ordinary block-diagram terminals. [NI LabVIEW User Manual](https://download.ni.com/support/manuals/320999e.pdf)

This alternative explains all current evidence:

- both sinks report owner `Diagram#639`;
- one is already proven to be a `ControlTerminal` (`TurnOff`);
- the other is absent from a deliberately nonrecursive panel census;
- neither appears in the ordinary `Diagram.Nodes[]` terminal census.

Both reported sinks being `TurnOff` counted as “terminal plus owner” is not the normal API interpretation: `Wire.Terminals[]` returns terminal references, while the owner is obtained separately; a `ControlTerminal` simply happens to return its containing diagram as owner. [NI Community explanation](https://forums.ni.com/t5/LabVIEW/Vi-Scripting-inconsistent-behaviour-of-terms-of-a-wire-owner/td-p/3309055) Reference equality would cheaply rule out an actual duplicate.

### (c) Existing-reader question

The listed readers do not yet prove the unmatched sink is conditional:

- `Owner = Diagram#639` is nondiscriminating.
- Absence from `Diagram.Nodes[]` is nondiscriminating because the known `TurnOff` control terminal is also absent.
- The node-label reader helps only if the terminal is exposed through the node enumeration that already missed it.
- `Shift Registers[]` can exclude shift-register terminals but cannot positively identify the loop-end terminal.
- `Wire.Terminals[]` supplies the decisive sink reference, but nothing listed compares it with `WhileLoop#637`’s loop-end reference.

However, you do **not** yet need a new property node to test the strongest alternative. LabVIEW’s supplied `Traverse for GObjects.vi` recursively finds objects inside tabs, clusters, loops, and other containers. [NI Community description](https://forums.ni.com/t5/LabVIEW/get-references-to-all-controls-on-front-panel/m-p/694003/highlight/true) A recursive panel census followed by the existing `Connected Wire` check can determine whether another panel object carries 3457.

### (d) Correct property and verification

If recursive panel traversal finds no second carrier, `WhileLoop.Loop End Ref` is the correct direct API. The recorded property ID is `0x06362C00`, and it returns the While Loop’s end terminal. [WhileLoop class/property table](https://labviewwiki.org/wiki/WhileLoop_class) A practical VI-Scripting example likewise identifies `LoopEndRef` as the way to obtain a While Loop’s conditional terminal. [NI Community solved thread](https://forums.ni.com/t5/LabVIEW/VI-Scripting-locate-loop-iteration-and-conditional-terminals/td-p/4344904)

Before hard-coding the numeric ID, verify it in LabVIEW 2026’s VI Server Class Browser by selecting `WhileLoop` and locating `Loop End Ref`; NI documents that the Class Browser searches properties and can create the selected property directly. [NI Class Browser instructions](https://download.ni.com/evaluation/training/lvcore2_coursemanual_english_sample.pdf)

The claim is falsified if either:

- recursive panel traversal finds a second panel object whose diagram terminal has connected wire 3457; or
- the unmatched sink reference is unequal to `WhileLoop#637.Loop End Ref`.

The cheapest discriminating test is therefore **a recursive front-panel census using `Traverse for GObjects.vi`, reusing the existing terminal/Connected-Wire check for UID 3457**. Only if that returns no second carrier should you build the `Loop End Ref` reader and compare its reference directly with the two non-source references from `Wire.Terminals[]`.

## Sources

(extract from answer)

## What was done with it

**Outcome: ANSWERED (107 s, rc 0) — ACCEPTED, and it stops this thread.** The reviewer's decisive point is one
this session missed and the toolkit's own docstring states: **`panel_wiring` is NOT recursive** (tab pages and
cluster elements are not rows, `tools/gscript.py:632`). So "no panel object carries 3457" was never provable by
that reader, and the unmatched second sink of wire 3457 is fully explained by an ordinary front-panel
`ControlTerminal` belonging to a **tab-page-nested** control or indicator — no conditional terminal required.

Wording corrected in `docs/main-vi-stop-and-save.md:§1` to "exactly one additional direct, distinct, non-source
terminal reference on wire 3457", per (a).

**Ordering adopted, not executed** (measurement-only brief; the cycle-15 plan freezes new op VIs): the cheapest
test is a **recursive** front-panel census (`Traverse for GObjects` over `ControlTerminal`, then each terminal's
`Connected Wire` vs 3457), and only if that finds no second carrier is the `WhileLoop.Loop End Ref` 0x06362C00
reader worth building. Also adopted: compare the two non-source terminal REFERENCES for equality before writing
"two sinks" at all.

This is the **second** failed prediction of the same class (P5, then Q2), both explained by inference rather than
read from the machine — CLAUDE.md's "when a diagnosis is GUESSED twice, build the READER" now applies to this
question. Recorded in STATUS OPEN 13 for the judgement session; not built here.
