---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# builder-leaves-artifact

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (68s)
- **why asked:** failed prediction: deleting everything a build added did not restore the target's ExecState.
- **verdict:** RESOLVED by measurement the same morning (probe_builder_artifact.log): the artefact was the WALKER's junk Invokes (spec s33), not the builder's; net_map now purges its own junk; later measured that junk lands only on an OPEN target (walk_junk_probe.log).

## Question

ATTACK this (LabVIEW 2026 VI Scripting; you reviewed castfree-ladders-execstate0 an hour ago and listed 'another creator artifact was added' as a suspect - it now looks like the answer). MEASURED, three cases incl. a CONTROL (GObject.Position 632A800, a property used successfully dozens of times): scratch target pristine ExecState 1, Wire 9 -> after ONE build_property call (our op OpBuildPN_v1 wrapping erdosmiller Create Property Node.vi): ExecState 0, Wire 9 -> after wiring the new node's reference from an upstream node's 'reference out': ExecState 0, Wire 10 -> after 'Block Diagram:Remove Bad Wires' (410): ExecState 0, Wire 10 -> after DELETING the new Property node and Remove Bad Wires again: ExecState 0, Wire 9. So removing everything I intentionally added does not restore the VI: the builder call leaves some OTHER mutation on the TARGET. Yesterday the same chain through the previous op version (OpBuildPN_v0) produced ExecState-1 results (e.g. OpReportAll_v0 was built and saved this way) - though those recipes always ran Remove Bad Wires between steps. What differs in v1: two front-panel indicators were added ON THE OP (creator 'error out' index-15 -> indicator; creator 'Outputs' -> indicator), nothing else; Python now also reads those two indicators after the run. QUESTIONS: (a) what does erdosmiller Create Property Node.vi (or its Create Constant / Wire helpers) put on the TARGET diagram besides the Property node - e.g. a class-specifier constant, a temporary wire, or a 'reference' constant for the class - and could exposing 'Outputs' (an array of the new node's terminal refnums) on the caller keep those terminal references OPEN so LabVIEW holds the target in an edit/reserved state that reads as not runnable? Is ExecState 0 possibly 'reserved/being edited' rather than 'broken' here - what are the numeric Execution.State values and can an open reference to a diagram object make a VI report Bad? (b) how do I detect the artifact by script without an error list: I plan report-by-class diffs (Constant, Invoke, Wire, Node, Terminal counts) pristine vs after build vs after delete - what classes would the erdosmiller helper leave behind? (c) is it plausible that v0 ALSO left the artifact and Remove Bad Wires between steps cleared it (i.e. the artifact is a broken/loose WIRE that RBW removes) - but in today's sequence RBW did not restore ExecState, so what kind of leftover survives RBW? (d) does closing the references held in the 'Outputs' indicator (Close Reference on each element) matter - i.e. should v1 wire Outputs -> Array Size -> I32 and then Close Reference on the array, as you originally advised? Short, cited.

## Answer

The ?쐎ther mutation??hypothesis is plausible, but your measurements do **not yet prove a persistent diagram object**. The strongest competing explanation is a stale compile state after scripted Remove Bad Wires?봞n externally reported VI Scripting behavior matching your sequence exactly.

**(a)** `ExecState 0` means **Bad/non-executable**, not ?쐒eserved for editing.??Values are `0 Bad`, `1 Idle`, `2 Run top level`, `3 Running/reserved by an active hierarchy`. An ordinary open GObject/Terminal reference does not map to state 0. [NI?셲 state definitions](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YIEJCA4), [numeric mapping](https://forums.ni.com/t5/LabVIEW/How-to-tell-if-VI-is-running/m-p/721963)

Crucially, there is a reported scripting defect/quirk where programmatic Remove Bad Wires deletes the wires but **does not retrigger compilation**: the VI continues reporting broken until an attempted run recompiles it, after which it works. That fits ?쏻ire 9, node gone, still ExecState 0??better than an invisible object does. [NI Community report](https://forums.ni.com/t5/LabVIEW/Undo-for-Programmatic-BD-cleanup/m-p/1019990)

The erdosmiller repository describes a code-generation library but does not expose a human-readable implementation of its compiled `Create Property Node.vi`; therefore I cannot substantiate that it creates a class constant or temporary node. [erdosmiller/lv-scripting](https://github.com/erdosmiller/lv-scripting)

**Cheap decisive test:** after delete + RBW, attempt `Run` once, then reread `ExecState`. If Run succeeds or changes it to 1, there was no persistent breaking artifact?봨ust stale compilation.

**(b)** Diff at least:

- `PropertyNode`, `InvokeNode`, `Constant`, `ClassSpecifierConstant`
- `Wire`, `Terminal`
- all `Node` subclasses and total `GObject` count
- ideally UID/class/owner tuples, not merely counts

But a completely clean object diff plus state 0 supports stale compilation. Also compare `BDModificationBitSet`; NI documents it as indicating diagram changes, though it does not identify their cause. [NI ActiveX VI properties](https://www.ni.com/docs/ar-SD/bundle/labview-api-ref/page/properties-and-methods/activex/vi-p.html)

**(c)** Yes, v0 could have left a broken/loose wire that the inter-step RBW removed. NI says RBW removes broken wires, including loose or incompatible connections. [NI wiring documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html) But today?셲 unchanged wire count after RBW makes a surviving loose wire unlikely. Survivors are more likely:

1. a non-wire node/constant, which RBW never promises to delete; or  
2. no artifact at all?봮nly the stale compile status above.

**(d)** Close the returned terminal references for hygiene, but do not expect that to repair `ExecState`. NI says closing a parent VI reference automatically closes its child-object references, and implicit/reference-out references may not require explicit closure. Open child references keep objects/VI data in memory; NI does not say they make valid diagrams Bad. [NI reference-lifetime guidance](https://www.ni.com/en/support/documentation/supplemental/13/closing-references-in-labview.html)

`Outputs ??Array Size ??I32` merely avoids exporting the refs; it does **not** close them. Best v1 design: consume `Outputs` internally, optionally close each element before the target VI reference closes, and expose only count/status. Do this for leak hygiene and isolation?봭ot as the leading fix. The first test should be **Run/recompile after delete + RBW**.

## Sources

(extract from answer)

## What was done with it

See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
