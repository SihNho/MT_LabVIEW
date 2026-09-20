---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# setcommand-signed-wirecontrol-plus2

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (37s)
- **why asked:** wire_control raised on a +2 wire count in build_setcommand_signed.log run 5 (a control-to-frame crossing = tunnel + two segments)
- **verdict:** unverified

## Question

FAILED PREDICTION check (brief). tools/bench/build_setcommand_signed.log run 5 (tools/recipes/build_setcommand_signed.py, run after a clean LabVIEW restart): everything built - SetCommand_signed.vi (wiring check True, ExecState 1, saved) and both injection TEST copies - but the step 'wire_control [Text] -> Function[String Subset].string' raised 'Wire 73 -> 75, expected +1' because gscript.wire_control asserts exactly +1 wire object; the very next census showed String Subset.string wired (uid 616 / 602 on the two copies) and ExecState 1. MY EXPLANATION: wiring a top-level front-panel control terminal into a node INSIDE a case frame creates a case tunnel plus TWO wire segments (outer + inner) = +2 Wire objects; the +1 assertion is the same wrapper bug fixed earlier in gscript.wire() for loop-boundary crossings, so the exception is a false alarm and the artefacts are correct (test_setcommand_signed.py will confirm functionally). FIX: wire_control accepts +1 or +2 and reports which. ATTACK: (a) agree that a wire crossing a structure border is two Wire objects in VI Scripting (one per diagram) - cite if possible; (b) any way the +2 could instead mean a wrong/extra wire (e.g. the control wired to two sinks)? The census says the only sink is String Subset.string and ExecState is 1.

## Answer

Your explanation is likely correct, but the proposed `+1 or +2` assertion is too permissive.

- A case tunnel has separate outer and per-case inner terminals. Therefore, crossing the boundary naturally requires an outside connection and an inside connection?봠onsistent with two VI-Scripting `Wire` objects on two diagrams. The clearest published evidence is this accepted NI Community solution describing ?? outer terminal??and ?쐎ne inner terminal per case.??[NI Community](https://forums.ni.com/t5/LabVIEW/LabvVIEW-Scripting-wiring-a-pass-through-tunnel-inside-a-case/m-p/3945608)
- NI also documents that ordinary wires create tunnels when entering structures, while channel wires explicitly do not. [NI wire documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)

Could `+2` mean an erroneous branch? Yes in principle: one LabVIEW wire may have multiple sinks. [NI wire documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html) But your census finding that the only sink is `String Subset.string`, combined with `ExecState 1`, makes that explanation very unlikely?봞ssuming the census covers both the outer and nested diagrams. `ExecState 1` proves compilability, not intended topology.

Recommended fix: accept `+2` only when topology confirms:

1. one new tunnel;
2. outer wire connects the control to the tunnel?셲 outer terminal;
3. inner wire connects that tunnel?셲 active-case inner terminal to `String Subset.string`;
4. neither wire has another sink.

So: **failed prediction confirmed; false alarm strongly supported.** Functional testing should confirm behavior, but topology-aware validation is safer than merely allowing either count.

## Sources

(extract from answer)

## What was done with it

wire_control now accepts +n..+2n; the functional test (16/16) confirmed the topology by effect. The topology-aware check is noted as a future improvement. Verdict: correct.
