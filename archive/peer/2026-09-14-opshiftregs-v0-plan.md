---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review, plan]
---

# opshiftregs-v0-plan

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (82s)
- **why asked:** plan review before OpShiftRegs_v0 (per-register wiring reader on the frame loop's 14 shift registers, via the new WhileLoop cast)
- **verdict:** unverified

## Question

PLAN REVIEW (attack; one paragraph). CONTEXT: LabVIEW 2026 VI Scripting from Python; we now hold a WhileLoop-typed cast (OpWhileCast_v0: Traverse WhileLoop by index -> TMSC seeded by a WhileLoop refnum control -> Loop.Shift Registers[] 6361402 -> For loop -> GObject.UID). On the main VI's frame loop it returns 14 shift-register UIDs (tools/bench/test_oploopcast.log). GOAL: resolve the frame loop's 54 half-edges (docs/frame-loop-wire-graph.md) = for every shift register: its OUTER wire(s) (initial value in on the left, final value out on the right) and its INNER wire(s) (the body-side terminals), plus left<->right pairing. PLAN OpShiftRegs_v0 (copy of OpWhileCast_v0;  = register index): Shift Registers[] -> Index Array (erdosmiller Create Index Array on the top diagram, index control) -> element -> PN_T class Tunnel [Outside Terminal 6356001] and [Inside Terminals[] 6356000] as SEPARATE single-property nodes (project rule: one property per node so a failing row cannot default the next) -> outer chain Terminal[Name 634A004] / [Is Source? 634A003] / [Connected Wire 634A000] -> Wire GObject.UID; inner: For loop over Inside Terminals[] with the same three reads -> auto-indexed arrays; pairing: PN class LeftShiftRegister [Right Shift Register 6374C00] on the same element -> Tunnel[Outside Terminal] -> Terminal[Connected Wire] -> UID (the right register's outer wire) and its Inside Terminals[] likewise. UNKNOWNS: (1) what is the ELEMENT TYPE of Loop.Shift Registers[] - LeftShiftRegister? a generic ShiftRegister/Tunnel? does it include RIGHT registers too (14 = 7 pairs or 14 lefts)? If the element type is Tunnel/generic, a LeftShiftRegister-class property node will not compile on it and pairing needs another seed (a LeftShiftRegister-typed input somewhere in NI's examples? which example has 'Shift Register' property nodes: the While Loop example did not); (2) does Tunnel.Inside Terminals[] on a shift register return one terminal per frame (like tunnels) or the stacked-element terminals; (3) Is Source? semantics on a left register's outside terminal (sink = initial value input) vs right (source = final output). ATTACK the plan, answer 1-3 with LabVIEW Wiki / NI citations, and propose the cheapest discriminating first build (e.g. Tunnel-only v0, then pairing v1).

## Answer

The plan is directionally sound, but it prematurely assumes both the array?셲 concrete type and that every terminal has a valid `Connected Wire`; make **v0 a Tunnel-only census** and postpone pairing. (1) NI/LabVIEW Wiki documents `Loop.Shift Registers[]` only as ?쐒eferences to the shift registers,??without publishing its element refnum type, so neither ??4 left registers??nor ?? pairs??is established by that property alone ([Loop class](https://www.labviewwiki.org/wiki/Loop_class)); however, `LeftShiftRegister` inherits `Tunnel` and uniquely exposes `Right Shift Register`, while right registers are separately represented as `RightShiftRegister`, making **14 left objects / 14 pairs** the likelier interpretation?봢specially because 14 pairs yield 56 possible outer/inner connections, close to your observed 54?봟ut that remains an inference until runtime class names or the wire type are observed ([Tunnel hierarchy](https://labviewwiki.org/wiki/Tunnel_class), [LeftShiftRegister.Right Shift Register](https://www.labviewwiki.org/wiki/LeftShiftRegister_class/Right_Shift_Register_property)). (2) `Tunnel.Inside Terminals[]` explicitly returns **one terminal per structure frame**, not the stacked-history elements; a While Loop has one body/frame, so expect one inner terminal per left or right register, while stacked elements should appear as distinct left-register objects because stacking adds elements only on the left ([Inside Terminals[]](https://labviewwiki.org/wiki/Tunnel_class/Inside_Terminals%28%29_property), [NI stacked-register description](https://download.ni.com/support/manuals/320999e.pdf)). (3) `Is Source?` means exactly source versus sink ([Terminal.Is Source?](https://labviewwiki.org/wiki/Terminal_class/Is_Source%3F_property)): therefore left-outside is a sink when initialized, left-inside is a source, right-inside is a sink, and right-outside is a source, matching NI?셲 documented flow?봧nitial data enters the left register from outside, body data enters the right register, and the final value exits right ([NI initialization](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019OlISAU), [NI shift-register flow](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YKYuCAO&l=en-US)). Cheapest discriminator: build **v0 entirely against `Tunnel`**, emitting for all 14 elements their UID/runtime class identity plus separate `Outside Terminal` and `Inside Terminals[]` rows, and for every terminal emit name, source flag, and nullable wire UID; `Connected Wire` is only a reference to a connected wire, so unwired initializers must be treated as valid nulls rather than failures ([Terminal properties](https://labviewwiki.org/wiki/Terminal_class)). If v0 reports 14 `LeftShiftRegister`s and one inner terminal each, v1 can safely cast each element to `LeftShiftRegister`, follow `Right Shift Register`, and run the same Tunnel-only reader on the returned right object; if the array is generic or mixed, obtain/cast the left type before attempting property `6374C00`. Also, wire UID alone identifies a net, not each half-edge: preserve terminal UID and side/source metadata, and optionally use `Wire.Terminals[]` when validating that all 54 half-edges were recovered ([Wire class](https://labviewwiki.org/wiki/Wire_class)).

## Sources

(extract from answer)

## What was done with it

Built v0 as the Tunnel-only census the reviewer asked for (test_opshiftregs.log): all 14 elements accepted by a
Tunnel-class node, one inside terminal each; the element class turned out to be RightShiftRegister (the reviewer's
'14 lefts' inference was wrong, its Is Source? reading for the right side was right). v1 then followed the reviewer's
own fallback (right → left via Left Registers[]) and passed 8/8. Verdict: sound plan; one inference refuted by measurement.
