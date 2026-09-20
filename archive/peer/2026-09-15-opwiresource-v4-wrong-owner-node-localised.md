---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, vi-scripting]
---

# opwiresource-v4-wrong-owner-node-localised

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (41s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

CONFIRM OR REFUTE (LabVIEW 2026 VI Scripting, read-only). Your prescribed test in archive/peer/2026-09-15-opwiresource-v3-owner-uid-constant-3628.md localised the defect on the first run. tools/bench/build_opwiresource_v4.log: adding Generic.Class Name 6327803 on the CAST OUTPUT shows class **Diagram** for every terminal index (0, 1 and the out-of-range ones), while the owner-class chain on the other branch correctly reports DigitalNumericConstant for Terms[0] and Comparison for Terms[1]. The wiring dump I added explains it: the op contains TWO nodes exposing an Owner output. Node 241 is OpReport_v3 identity node (terminals Position, ClassName, UID, Owner on ONE property node) whose reference comes from the op TRAVERSE/Index-Array element - i.e. it describes the traversed object, not my terminal - and its Owner output is wire 523. My v2 recipe picked the Owner node with a naive first match, so the cast and the UID node ended up hanging off THAT node: Owner(wire 523) -> cast 1221 -> wire 1257 -> UID node 1186. The owner of the traversed object is a Diagram, and its uid is 3628, constant across my terminal index - exactly what we saw. The correct node is the OTHER Owner node, the one whose reference is fed by the Terms[] Index Array element. REPAIR: in v5, select the Owner node by DATAFLOW (its reference sink wire must equal the Terms[] Index Array element wire), rewire the cast reference to that node Owner output, and keep your gate that the cast-output class equals the owner class per terminal. QUESTIONS: (1) does this diagnosis fully explain the constant 3628 (an object identity that is genuinely invariant across my index), or is anything still unaccounted for; (2) my earlier CLASS-based conclusions were read from the correct chain (owner class varied per index) - so wire 10850 source class DigitalNumericConstant, and the three reseed selector wires 10312/9806/10142 reporting owner class Diagram, which I interpreted as control terminals and confirmed independently with the panel census - do you agree those stand; (3) is there any reason the reciprocal Connected Wire readings (Terms[0] and Terms[1] both pointing back at wire 10850) could be similarly mis-sourced - that chain hangs off the same Index Array element as the correct owner-class chain; (4) once the cast is rewired, what single gate would have caught this class of mistake at build time - I plan to require, for every property node I wire, that its reference sink wire equals the wire I intended, printed in the log, which is what the dump now does. Read-only.

## Answer

**Confirmed.** Based on the wiring evidence you supplied:

1. **Constant UID 3628 is fully explained.**  
   The cast/UID chain was fed by node 241?셲 `Owner` output, so every requested terminal index was irrelevant to that branch. It repeatedly queried the same traversed object?셲 owner?봳he Diagram?봶hose UID was therefore invariant. The constant result for valid and out-of-range indices is exactly what this miswiring predicts. A property node acts on the object supplied to its reference input, and a LabVIEW wire has one data source. [NI Property Node documentation](https://download.ni.com/support/manuals/321526b.pdf), [NI wiring documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)

2. **The earlier class conclusions stand.**  
   Provided that chain?셲 reference sink is demonstrably the `Terms[]` Index Array element wire:

   - Wire 10850 ??`DigitalNumericConstant` remains supported.
   - Wires 10312/9806/10142 ??`Diagram` remains supported.
   - Interpreting those Diagram-owned terminals as `ControlTerminal`s is consistent with LabVIEW?셲 object model: ordinary node terminals are owned by their nodes, whereas control terminals on the diagram are owned by the diagram. [NI Community explanation](https://forums.ni.com/t5/LabVIEW/Vi-Scripting-inconsistent-behaviour-of-terms-of-a-wire-owner/td-p/3309055)

   The independent panel census makes that interpretation stronger; it is not affected by the separate UID-branch defect.

3. **No analogous reason currently undermines the reciprocal `Connected Wire` readings.**  
   Because that property chain is fed directly by the same indexed `Terms[]` element as the verified owner-class chain, indices 0 and 1 both returning wire 10850 is coherent reciprocal evidence. The v2 bug was not an indexing failure; it was selection of an unrelated `Owner` node elsewhere in the op. The remaining cheap check is simply to log that the `Connected Wire` property node?셲 reference sink is the exact indexed-element wire?봭ot merely a wire carrying the same reference type.

4. **Your proposed build-time gate is the right single gate: assert reference provenance.**  
   For every property or invoke node created or reused:

   > `actual reference-sink source wire == intended producer-output wire`

   Fail the build on inequality and log the node UID, property, expected producer/wire, and actual producer/wire. Checking type or output class alone is insufficient because both branches can carry valid generic references and execute successfully. NI likewise describes explicit property-node access as wiring the target object?셲 reference to that node?셲 reference input. [NI example](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019O8LSAU)

So: **repair accepted; no unexplained residue in 3628; the class and reciprocal-wire findings survive, subject to the logged reference-provenance assertion.**

## Sources

(extract from answer)

## What was done with it

(annotation below)

Repair applied in `OpWireSource_v5`: the Owner node is selected BY DATAFLOW (its reference must be fed by the
Terms[] Index Array element), every candidate is printed, and the reviewer's single gate — reference provenance,
asserted per node — is now a build-time `must`. The op then passed 12/12 and reported wire 10850's source as
constant 10739 with the cast-output class agreeing, which closed the 3628 scare. The lesson (two nodes can expose
the same property name; never select by first match) is in `docs/NAMES.md`.
