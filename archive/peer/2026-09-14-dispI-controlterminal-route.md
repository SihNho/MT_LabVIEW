---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# dispI-controlterminal-route

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (33s)
- **why asked:** second route after H1: could Wire Inputs target a ControlTerminal by name?
- **verdict:** peer: no - a ControlTerminal is a Terminal, not a Node; Terminal.Connect Wire on the control's terminal is the clean route. Built as OpConnectCtl_v0 the same hour; source-already-wired produced a BRANCH (the ImageToArray wire stayed) - verified by panel_wiring + node_terms.

## Question

FAILED PREDICTION follow-up, brief. tools/bench/build_harness_dispI.log run 2 (recipe tools/recipes/build_harness_dispI.py): with 'Image Out' now WIRED (to IMAQ ImageToArray), wire_indicators(['Image Out'] -> ['Image']) still raised 5001, and your discriminating probe ('File Type out' -> 'Image') ALSO raised 5001 -> H1: erdosmiller's Wire Indicators.vi / Get Controls-by-label does not find the IMAQ Image Display indicator even though Control.Label -> Text.Text reads 'Image' for it (panel_wiring output in the log). NEXT ROUTE: gscript.wire() = OpWire_v1 (erdosmiller Wire Inputs.vi: destination NODE found by Traverse class + index, sink terminal by NAME) with destination class 'ControlTerminal' and the terminal name = the control's label ('Image'), branch=True because the source is already wired; the three ControlTerminals (Image, Image Name, File Path) are tried by index 0..2 - a wrong one should raise 5001 (name absent) or be declined silently; success is verified by EFFECT (panel_wiring: the Image control's terminal wire uid becomes non-zero, ExecState 1). ATTACK: (1) what is the Terminal.Name of a front-panel indicator's block-diagram terminal - the owned label, the caption, or empty? (labviewwiki/NI) - if empty, Wire Inputs cannot address it by name and the route is dead; (2) could Wire Inputs.vi reject a ControlTerminal as the 'node' (it calls Node.Terminals[] on it? a ControlTerminal IS a Node subclass?) ; (3) alternative: Terminal.Connect Wire invoke (OpConnect2: sink terminal = the control terminal's Terminal ref via Control.Terminal - a typed ref we CAN get cast-free through Panel.Controls[] -> Control.Terminal; source = ReadFile's 'Image Out' Terminal ref via Node.Terminals[] index) - is that the cleanest, and does 'Connect Wire' on an already-wired source create a branch? One paragraph.

## Answer

H1?셲 next route is probably dead: `Terminal.Name` is a separate, non-translatable identifier?봭ot the caption?봞nd the references do not guarantee that an IMAQ display?셲 value equals its front-panel label; inspect `Terminal.Name` directly rather than assuming `"Image"` ([Terminal class](https://labviewwiki.org/wiki/Terminal_class)). More decisively, `ControlTerminal` inherits from `Terminal`, not `Node`, and exposes no `Terminals[]`; therefore a routine that finds a `Node` and calls `Node.Terminals[]` cannot validly accept it ([ControlTerminal hierarchy](https://labviewwiki.org/wiki/ControlTerminal_class)). `OpConnect2` is the clean route: invoke the sink control terminal?셲 `Connect Wire`, passing ReadFile?셲 source terminal; the method explicitly accepts another terminal as its wire source ([Connect Wire](https://labviewwiki.org/wiki/Terminal_class/Connect_Wire_method)). Because LabVIEW permits one source to feed multiple sinks, this should create a branch rather than replace the existing connection, though that last behavior is an inference?봭ot explicitly guaranteed by the scripting reference?봞nd should be accepted only after `Connected Wire`/UID and ExecState verification ([NI wiring model](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)).

## Sources

(extract from answer)

## What was done with it

See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
