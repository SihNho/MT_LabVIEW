---
type: peer-review
status: historical
date: 2026-08-31
tags: [peer-review]
disposition: legacy
---

# 2026-08-31-createpropnode-reference-wiring

- **agent:** codex
- **date:** 2026-08-31
- **outcome:** ANSWERED (110s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

Attack this design before I build it. LabVIEW 2026, erdosmiller lv-scripting.

GOAL: an op VI that, at ITS runtime, flips a LoopTunnel's IndexMode in a TARGET VI. Design: inside the op, 'Create Property Node.vi' is used AT BUILD TIME to place a property node INTO THE OP ITSELF?? no - clarify: we call Create Property Node.vi with 'Diagram in' = the OP-UNDER-CONSTRUCTION's diagram, 'Properties' = [(IndexMode, write)], and its 'reference' input wired FROM a refnum wire-source inside the op-under-construction, namely the output terminal of a 'To More Specific Class' node (cast to LoopTunnel class) already present there. The library's Create *.vi family passes 'wire source refnums' in and terminal refnums out; Get Outputs.vi returns a node's output terminal refnums by name.

QUESTIONS (cite LAVA/NI/GitHub sources where possible; the library is github.com/erdosmiller/lv-scripting): (1) Does Create Property Node.vi's 'reference' input accept a TERMINAL refnum (as returned by Get Outputs) as the class-context source, wiring the new property node's reference input from that terminal? Or does it expect a different refnum kind (e.g. an object refnum, or a wire refnum)? (2) When the wired class is LoopTunnel and Properties=[('IndexMode', True)], will the created property node be a WRITE node with an input terminal for the value - and what is the IndexMode property's data TYPE on a write property node (enum? which values = disabled/indexing/concatenating)? (3) Error 1077 'Invalid property value' at Set Properties[] - we hit this when reference was UNWIRED; confirm wiring reference fixes name resolution. (4) Alternative simpler designs to score against: (a) skip property-node-in-op entirely - since the OP runs scripting anyway, put a STATIC property node (created once, by hand or by this method) in a reusable OpSetIndexMode that takes vi path + tunnel index + mode value as controls; (b) use LabVIEW's native 'Tunnel Mode' invoke/property if one exists on LoopTunnel (does 'TunnelMode'/'Disable Indexing' exist as scripting method?). Which design is most robust?

## Answer

Verdict: the design is viable for regular versus auto-indexing, but I would not dynamically construct the property node in the production op. Build and freeze one static `LoopTunnel.IndexMode` write node, then reuse it. The current design adds a fragile meta-scripting layer without buying runtime flexibility.

1. `reference` input: use the output `Terminal` refnum

The intended source is the output terminal returned by `Get Outputs.vi`, not the runtime LoopTunnel object reference itself and not a Wire refnum.

Conceptually:

```text
To More Specific Class.output Terminal ref
             ??             ??Create Property Node.vi.reference
```

`Create Property Node.vi` uses that terminal as the wire source and derives the property-node class context from the datatype carried by that terminal. This matches the library?셲 general abstraction: its create functions accept source-terminal references and create the connecting wire. The erdosmiller project explicitly describes itself as a code-generation wrapper around VI Scripting, with its examples being the authoritative usage reference. [erdosmiller/lv-scripting](https://github.com/erdosmiller/lv-scripting)

This is also consistent with the older LAVA scripting pattern: obtain a terminal reference and wire that terminal to the new property node. [LAVA: Creating Property Nodes](https://lavag.org/topic/1191-creating-property-nodes/)

Important distinction:

- The wire carries a runtime `LoopTunnel` object reference.
- The scripting operation receives a compile-time `Terminal` object reference representing the source endpoint of that wire.
- A Wire refnum would represent an already-created wire and is not the appropriate source endpoint here.
- Passing the actual LoopTunnel scripting refnum directly would describe the object being edited now, not create dataflow inside the generated op.

Your cast must therefore be genuinely typed as `LoopTunnel`. A generic `Tunnel` wire does not expose `IndexMode`; NI?셲 accepted forum answer specifically says to cast to `Loop Tunnel` with `To More Specific Class`. [NI Community: How to change tunnel mode using VI scripting](https://forums.ni.com/t5/LabVIEW/How-to-change-tunnel-mode-using-vi-scripting/m-p/3969536)

2. Write direction and datatype

`Properties = [("IndexMode", True)]` should create a write row and consequently a value input terminal, assuming `True` means ?쏧s Write???as recorded by the library API.

However, the value is not an enum. The published VI Server metadata says:

- Data type: `U32`
- `0`: Regular ??indexing disabled / last value
- `1`: Auto Index
- Read/write
- Not settable while the target VI is running

[LoopTunnel.IndexMode metadata](https://labviewwiki.org/wiki/LoopTunnel_class/Index_Mode_property)

Therefore the generated node should accept a scalar `U32`. I would expose the op?셲 mode input as `U32` or convert a friendly typedef enum to `U32` immediately before the property node.

Do not assume `2 = Concatenating`. The available scripting metadata documents only 0 and 1. Concatenating is a real editor tunnel mode, but it is not documented as a third `IndexMode` value. NI documents Concatenating separately as an output-tunnel mode. [NI documentation: automatically concatenating loop outputs](https://www.ni.com/docs/fr-FR/csh?context=lvcore_lvhowto_autocat_arraysnloops)

So the safe API is:

```text
0 = regular/non-indexed
1 = auto-indexed
anything else = reject before property write
```

If concatenating matters, have the manager inspect a LabVIEW 2026 reporter dump of a hand-created `LoopTunnel.IndexMode` property node and test value `2` only on a disposable VI. The public evidence does not justify shipping `2`.

Another critical constraint: ?쏿t the op?셲 runtime??is acceptable only if the target VI is idle/editable. `IndexMode` is explicitly not settable while the referenced target VI is running. The op itself may run while scripting another idle VI. [LoopTunnel.IndexMode metadata](https://labviewwiki.org/wiki/LoopTunnel_class/Index_Mode_property)

3. Error 1077

Wiring a specifically typed `LoopTunnel` reference is the correct fix for class/property resolution, but error 1077 alone does not prove that an unwired reference was the cause. NI defines 1077 generically as ?쏧nvalid property value?? it also occurs when an otherwise valid property receives a bad runtime value. [NI Community example of 1077 caused by an invalid property value](https://forums.ni.com/t5/LabVIEW/Error-1077-at-Property-Node-when-using-Dial-Control/td-p/3695356)

The likely sequence in your case is:

1. `reference` is unwired.
2. The created property node lacks `LoopTunnel` class context.
3. `Set Properties[]` cannot resolve `IndexMode` for the generic/default class.
4. It reports 1077.

Wiring the cast node?셲 output terminal supplies the missing class context and should fix that particular failure. Treat success as established only when all three effects are observed:

- a property node was created;
- its row displays `IndexMode` as a write row;
- the generated VI compiles with a `U32` wired to the value input.

A clean error chain alone is weak verification.

4. Design score

| Design | Robustness | Assessment |
|---|---:|---|
| Dynamically create the property node inside each op build | Low?뱈edium | Useful as a bootstrap experiment, but depends on terminal-ref plumbing, class inference, property-name strings and generated terminal discovery. |
| Static reusable `OpSetIndexMode` | High | Recommended. Build/verify the property node once; runtime only finds the target tunnel, casts it, writes `0/1`, saves and reports errors. |
| Direct `LoopTunnel` property/invoke operation | Same mechanism | `IndexMode` is already the native scripting property. There is no documented `TunnelMode` or `Disable Indexing` method on `LoopTunnel`; the published class lists `IndexMode`, `Is Conditional?`, and `Condition Terminal`, and no class-specific methods. [LoopTunnel class API](https://labviewwiki.org/wiki/LoopTunnel_class) |

My recommended production design is static `OpSetIndexMode`:

```text
target VI path
  ??open editable VI
  ??locate loop/tunnel deterministically
  ??To More Specific Class: LoopTunnel
  ??static IndexMode write property
  ??validated U32: 0 or 1
  ??save
  ??explicit error output
```

Prefer a stable tunnel identifier or topology-based selection over a bare array index if possible. `Structure.Tunnels[]` merely returns an array of tunnel references; its documentation does not promise a durable semantic ordering after diagram edits. [Structure.Tunnels[] metadata](https://www.labviewwiki.org/wiki/Structure_class/Tunnels%28%29_property)

Bottom line: use your dynamic construction only once to manufacture the static op if necessary. Freeze the verified property node afterward. Reject mode values outside `{0,1}`, keep the target VI stopped, and do not claim concatenating support without a LabVIEW 2026-specific experiment.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
