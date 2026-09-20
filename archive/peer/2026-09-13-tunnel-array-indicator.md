---
type: peer-review
status: historical
date: 2026-09-13
tags: [peer-review]
disposition: legacy
---

# tunnel-array-indicator

- **agent:** codex
- **date:** 2026-09-13
- **outcome:** ANSWERED (74s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

LabVIEW 2026 VI Scripting question. GOAL: from code (no GUI clicking), put an ARRAY INDICATOR on the AUTO-INDEXED OUTPUT TUNNEL of a For Loop, so a scripted VI can return arrays to a COM caller. WHAT ALREADY WORKS in our toolkit (all verified today): erdosmiller lv-scripting 'Exit For Loop.vi' creates the auto-indexed output tunnel from a node's output terminal - it works even on a Property node, not just connector-pane subVI terminals. WHAT FAILED, measured: 'Terminal.Create Indicator' (VI Server id 6349C02) addressed as VI -> Block Diagram -> Nodes[] -> ForLoop -> Terminals[] -> index 0..13 creates a DANGLING front-panel indicator for indices 0-7 (front-panel object appears but NO new wire object, ExecState unchanged) and nothing for 8+. So the For Loop's Terminals[] does not expose the tunnel in a form Create Indicator will wire to. QUESTIONS: (1) What is the correct scripting path from a For Loop reference to its TUNNEL references - is there a Loop.Tunnels[] or Structure.Tunnels[] property, what is its exact property name/ID, and is the returned object class LoopTunnel or Tunnel? (2) Once I hold a tunnel reference, which method creates a correctly-typed indicator wired to it - does Terminal.Create Indicator work on a tunnel reference directly? (3) Is there a property to READ or SET whether a tunnel is auto-indexing (so I can VERIFY the tunnel auto-indexed rather than assume it)? (4) Alternative accepted: is there a documented way to create a front-panel ARRAY indicator with New VI Object and then wire a tunnel to it - and can wires be created to/from a tunnel reference with Connect Wire? Cite NI documentation, the VI Scripting property/method reference, or NI forum threads with concrete property names.

## Answer

The correct route is:

```text
ForLoop ref
  ??Structure.Tunnels[]                 property 6360801
  ??index/select the required Tunnel
  ??Tunnel.Outside Terminal             property 6356001
  ??Terminal.Create Indicator           method   6349C02
```

Before creating the indicator, downcast the tunnel to `LoopTunnel` and explicitly set/verify `IndexMode = 1`.

1. Getting the tunnel references

`Tunnels[]` belongs to the `Structure` class, not specifically to `Loop` or `ForLoop`. Because `ForLoop` inherits from `Structure`, wire the For Loop reference directly into a Structure property node configured as:

```text
Tunnels[]
Property ID: 6360801
Access: read-only
```

The property returns generic `Tunnel` references, not statically typed `LoopTunnel` references. For loop tunnels are runtime objects of class `LoopTunnel`, which inherits:

```text
Generic ??GObject ??Tunnel ??LoopTunnel
```

Therefore, index `Tunnels[]` and use `To More Specific Class` with a `LoopTunnel` class constant before accessing loop-specific properties. [Structure.Tunnels[] reference](https://labviewwiki.org/wiki/Structure_class/Tunnels%28%29_property), [LoopTunnel class hierarchy](https://labviewwiki.org/wiki/LoopTunnel_class), [NI forum example using `Tunnels[]` and casting to `LoopTunnel`](https://forums.ni.com/t5/LabVIEW/How-to-change-tunnel-mode-using-vi-scripting/m-p/3969392)

There is no separate `Loop.Tunnels[]` property needed.

2. Creating the wired indicator

Do not invoke `Create Indicator` on the `Tunnel` or `LoopTunnel` reference. A tunnel is a `GObject`, not a `Terminal`, and it does not inherit Terminal methods.

Instead use the tunnel property:

```text
Tunnel.Outside Terminal
Property ID: 6356001
Return type: Terminal ref
```

Then invoke this on that returned reference:

```text
Terminal.Create Indicator
Method ID: 6349C02
Return type: Control ref
```

`Create Indicator` is documented to create an indicator for the addressed terminal and return its control reference. Addressing the tunnel?셲 outside terminal should therefore produce the FP indicator and its diagram wire?봳he scripting equivalent of Create ??Indicator on the output side of the tunnel. [Tunnel properties, including `Outside Terminal`](https://labviewwiki.org/wiki/Tunnel_class), [`Terminal.Create Indicator`](https://labviewwiki.org/wiki/Terminal_class/Create_Indicator_method)

So the important distinction is:

```text
ForLoop.Terminals[]       ??loop infrastructure terminals; wrong target
Structure.Tunnels[]       ??actual border objects
Tunnel.Outside Terminal   ??correct Terminal on which to invoke Create Indicator
```

Set the indexing mode before calling `Create Indicator`, so the outside terminal already has the desired array datatype.

3. Reading and setting auto-indexing

After downcasting the selected tunnel to `LoopTunnel`, use:

```text
LoopTunnel.IndexMode
Property ID: 6356C00
Data name / short name: IndexMode
Type: U32
Access: read/write

0 = Regular / Last Value
1 = Auto Index
```

Thus the robust sequence is:

```text
tunnel = ForLoop.Structure:Tunnels[][selected]
loopTunnel = To More Specific Class(tunnel, LoopTunnel)
loopTunnel.IndexMode = 1
assert loopTunnel.IndexMode == 1
outsideTerminal = tunnel.Outside Terminal
indicator = outsideTerminal.Create Indicator()
```

The property cannot be set while the target VI is running. NI?셲 current API reference confirms both values and read/write access. [NI `IndexMode` reference](https://www.ni.com/docs/ko-KR/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/tunnel/looptunnel/indexmode.html), [property ID and class details](https://labviewwiki.org/wiki/LoopTunnel_class/Index_Mode_property)

This is preferable to assuming the default, although NI says For Loop output tunnels normally default to indexing when created by wiring. [NI auto-indexing explanation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000PAghSAG)

4. Explicit array-indicator fallback

There is a demonstrated fully scripted fallback:

1. Use `New VI Object` with the Panel as owner to create an empty/void array shell.
2. Use another `New VI Object` with that array reference as owner to insert the element control.
3. Make the resulting array an indicator.
4. Get the array indicator?셲 diagram terminal.
5. Invoke `Connect Wire` on that sink terminal, passing the tunnel?셲 `Outside Terminal` as `Wire Source`.

An NI employee demonstrated this exact pattern for scripting a loop?셲 array indicator: create a void array, create a numeric object owned by the array, obtain the relevant terminal references, and use `Connect Wire`. [NI forum: scripting an array indicator](https://forums.ni.com/t5/LabVIEW/scripting-create-array-indicator/m-p/3282707/highlight/true)

`Connect Wire` is a `Terminal` method:

```text
Method ID: 6349C03
Required input: Wire Source, a GObject reference
```

It accepts another terminal or node as the source. Again, use the tunnel?셲 `Outside Terminal`; do not pass the `LoopTunnel` itself as though it were a terminal. The method can create a broken wire if the endpoint datatypes disagree, so verify the resulting VI?셲 executable state and terminal connections. [`Terminal.Connect Wire` reference](https://labviewwiki.org/wiki/Terminal_class/Connect_Wire_method)

Recommended implementation: use `Structure.Tunnels[] ??LoopTunnel.IndexMode ??Tunnel.Outside Terminal ??Terminal.Create Indicator`. It avoids manually constructing the array shell and automatically derives the correct element type and array rank from the auto-indexed tunnel.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
