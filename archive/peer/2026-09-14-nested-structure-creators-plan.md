---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review, plan]
---

# nested-structure-creators-plan

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (59s)
- **why asked:** plan review before diagram-indexed structure creators (nesting the kernel For loop and a Case inside While loops, stage 2)
- **verdict:** unverified

## Question

PLAN REVIEW (brief; one paragraph). LabVIEW 2026 VI Scripting from Python; our structure creators (OpForLoop_v0 / OpWhileLoop_v0 / OpBuildCase_v1) take the target diagram from VI.'Block Diagram' - i.e. they place ONLY on the top-level diagram. Stage 2 (docs/stage2-plan.md) needs a P=4 For loop (the kernel loop, made by our proven loop_kernel = Create For Loop + kernel subVI + tunnels) INSIDE a While loop body, and a Case structure (Replay?/live) inside the acquisition While loop. PLAN: diagram-indexed variants - copy each creator op, replace the 'VI.Block Diagram' property-node source of 'Diagram in' with the chain we already use elsewhere (OpExitLoop_v0: Traverse for GObjects class 'Diagram' by index -> Index Array -> To More Specific Class(Diagram) -> 'Diagram in'), i.e. a new 'Class Name 2'/'index 2' pair; identify the body by DIAGRAM UID (never by index across a creation, NAMES.md rule); tests: a While loop on the top level, then a For loop created in its body (census: the new ForLoop's diagram owner chain; ExecState after wiring N from a constant/terminal), then a Case inside the While body. ATTACK: (a) any reason erdosmiller's Create For Loop / Create While Loop / Create Case Structure refuse a sub-diagram 'Diagram in' (they are generic over AbstractDiagram? the library's Exit For Loop already takes a loop BODY diagram); (b) the tunnel semantics of 'Control Names' when the loop is nested (Get Controls resolves controls on the front panel; wiring from a top-level control terminal into a nested loop must cross TWO structure borders - does Wire Inputs create both tunnels?); (c) anything about 'location' being relative to the sub-diagram's origin.

## Answer

The plan is sound, with one important risk: (a) there is no architectural reason the creators should reject a loop-body `Diagram in`; NI?셲 own VI Scripting examples explicitly include dropping objects inside a While-loop diagram, so replacing only the owner-diagram acquisition should work?봯rovided the selected reference is the actual body `Diagram`, with UID re-resolution after every structure creation ([NI VI Scripting examples](https://forums.ni.com/t5/LabVIEW-APIs-Documents/LabVIEW-Scripting/ta-p/3535340)). (b) Do **not** assume `Wire Inputs` will synthesize both nested tunnels: LabVIEW can create tunnels when wiring across surrounding structures, but scripted case tunnels expose separate outer and per-case inner terminals, demonstrating that multi-border wiring has nontrivial semantics ([NI discussion of surrounding-loop tunnels](https://forums.ni.com/t5/LabVIEW/When-wiring-to-a-sequence-tunnels-are-automatically-created-in/td-p/724991), [case-tunnel terminal model](https://forums.ni.com/t5/LabVIEW/LabvVIEW-Scripting-wiring-a-pass-through-tunnel-inside-a-case/m-p/3945608)). Make the decisive test a top-level FP terminal ??kernel terminal inside nested For-inside-While, then census exactly one tunnel on each border, verify every wire segment/terminal owner, and require non-broken `ExecState`; if it fails, wire border-by-border explicitly. `Control Names` itself remains valid because it identifies FP controls?봳he uncertainty is solely the routing implementation. (c) Treat `location` as relative to the supplied owner/subdiagram, not top-level coordinates; that behavior is independently reported for `New VI Object`, while `Position` uses a different coordinate frame ([NI Community report](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Make-the-location-terminal-on-the-New-VI-Object-function/idi-p/4208374)). Therefore use conservative body-local coordinates or normalize placement after creation, and add a bounds/owner assertion to each nested-creation test.

## Sources

(extract from answer)

## What was done with it

Built both diagram-indexed creators from the OpExitLoop_v0 donor and ran the decisive routing test the reviewer asked for: a top-level control wired into a node inside a For loop nested in the outer loop produced exactly one tunnel per border with every segment accounted for (test_oploopin.log 6/6). location is passed body-relative. Verdict: correct.
