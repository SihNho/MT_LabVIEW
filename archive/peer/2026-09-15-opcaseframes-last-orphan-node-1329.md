---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, vi-scripting]
---

# opcaseframes-last-orphan-node-1329

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (21s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

VERY BRIEF (LabVIEW 2026 VI Scripting). tools/bench/build_opcaseframes_v0.log run 3: your identify-before-delete prescription worked (the frame-uid node was found by the wire it was fed from, the three TERMINAL readers were deleted, the stub wire was removed, and the Index Array element now feeds the frame-uid node - that gate passed). ExecState is still 0 and the dump now shows exactly ONE meaningful orphan: Property node 1329 with an unwired reference (everything else listed is an optional subVI input on Open VI Reference / Traverse for GObjects.vi / UID to GObject Reference.vi, which are legal). Node 1329 is inherited from the donor chain - in an earlier op version it was a Generic.Class Name reader used to prove which object a cast produced. MY PLAN: print that node data terminals and re-feed it by kind - a ClassName/UID reader belongs on the owner cast output (the object whose class is being reported), anything else on the Index Array element - then re-read ExecState. QUESTIONS: (1) is re-feeding by kind sound, or should an inherited reader whose purpose no longer exists simply be DELETED (my instinct now is: delete it, since its indicator is only meaningful for the old chain); (2) with the Index Array element carrying Diagram references, is Generic.Class Name on that element legal and useful (it would report Diagram for every frame, a weak but free sanity check); (3) any reason ExecState would stay 0 after every unwired required input is gone - I have no broken-wire reader yet and you earlier named VI.Get Errors 452 as the way to ask LabVIEW itself. Read-only.

## Answer

1. **Delete node 1329.** Its old diagnostic purpose and indicator no longer belong to this chain. Re-feeding by kind risks preserving semantically dead code merely to satisfy compilation.

2. **Generic.Class Name is legal on a Diagram reference**, because `Class Name` belongs to the Generic VI Server class. But reporting `Diagram` for every element adds little validation; use it only if you explicitly want an invariant check. [NI training manual](https://download.ni.com/evaluation/training/lvcore2_coursemanual_english_sample.pdf)

3. **Yes.** ExecState can remain bad because of broken wires, undefined structure tunnels, invalid casts/types, missing dependencies, or stale compilation?봭ot merely unwired required inputs. NI specifically identifies undefined tunnels and recompilation issues as causes. [NI troubleshooting](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000001DdHkSAK)

After deleting 1329, query **VI.Get Errors (method ID 452)** immediately. The hidden method is reported to expose useful compiler errors, though not always exactly the GUI Error List detail. [NI Community example](https://forums.ni.com/t5/LabVIEW/Error-list-in-VI-scripting/td-p/2263216/highlight/true)

## Sources

(extract from answer)

## What was done with it

(annotation below)

Taken: the inherited reader whose purpose was gone was DELETED, not re-fed to satisfy the compiler. That removed the
last unwired required input, but the VI was still broken — which is what pushed the diagnosis to the next level
(the cast was emitting the PARENT class) and, more importantly, made the missing `VI.Get Errors` 452 reader the
project's next build: three consecutive ExecState-0 diagnoses by inference is the pattern CLAUDE.md now names.
