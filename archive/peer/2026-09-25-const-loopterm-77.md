# const-loopterm-77

- **agent:** claude
- **role:** fact
- **model:** fable (effort low; peer.ps1 default for role fact)
- **kind:** fact
- **cost:** $1.8739  in 226 / out 8430 / cache-create 38146 / cache-read 311804  (129s, 42 turn(s))
- **date:** 2026-09-25 05:56:48
- **outcome:** ANSWERED (131s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

LabVIEW VI Scripting (LabVIEW 2020+), API facts with NI doc / forum URLs for each answer:
(1) Is Terminal.Create Constant (method, unique id 6349C00) invocable on the Terminal returned by the WhileLoop property "Loop End Ref" (the conditional terminal)? Any documented restriction on inner/loop-owned terminals?
(2) For a For Loop, is the count terminal N reachable as a Terminal via ForLoop "Loop Count" (returns a Tunnel) then Tunnel "Outside Terminal"? Is it also listed in the loop node's own Node.Terminals[] array?
(3) Does Terminal.Create Constant have an optional Value input, and does the created constant take the sink terminal's datatype (e.g. I32 for N, Boolean for the conditional terminal)?
(4) Any known issue where a constant created by scripting loses its value on save/reload?


## Answer

**Summary:** Questions 1 and 3 are settled by NI/Wiki docs and forum evidence. Question 2 is only partly settled: the documented chain exists, but no source states the class of "Loop Count" or whether N appears in Terminals[]. Question 4 has no documented issue for scripted constants.

**(1) Create Constant on the While Loop conditional terminal**
- Terminal.Create Constant (id 6349C00, owning class Terminal 16385) "creates a constant for the terminal and returns a reference to it," with no listed restriction on loop-owned terminals: https://labviewwiki.org/wiki/Terminal_class/Create_Constant_method (NI mirror: https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/terminal/createconstant.html).
- WhileLoop "Loop End Ref" (6362C00) "returns a reference to the end terminal of the While Loop": https://labviewwiki.org/wiki/WhileLoop_class/Loop_End_Ref_property. The Wiki lists its data type only as a generic BD refnum, not explicitly as Terminal class.
- Forum evidence: the accepted answer for wiring a scripted While Loop's conditional terminal uses Loop End Ref as the terminal reference for Connect Wire, after a direct approach gave error 1062: https://forums.ni.com/t5/LabVIEW/Wiring-the-conditional-terminal-of-a-while-loop-created-by/td-p/2115512. A second thread confirms LoopEndRef and LoopCounter as the way to reach these terminals: https://forums.ni.com/t5/LabVIEW/VI-Scripting-locate-loop-iteration-and-conditional-terminals/td-p/4344904.
- I found no source that shows Create Constant actually invoked on Loop End Ref, and no documented restriction against it. The only documented loop-terminal restriction is unrelated: "Iteration Terminal Hidden?" errors if the iteration terminal is wired (https://labviewwiki.org/wiki/WhileLoop_class).

**(2) For Loop count terminal N**
- ForLoop "Loop Count" (6362000) "returns a reference to the loop count," typed only as a generic BD refnum on the Wiki: https://labviewwiki.org/wiki/ForLoop_class/Loop_Count_property (NI: https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/node/structure/loop/forloop/loopcount.html). Neither source states that it returns a Tunnel, so your premise is not confirmed by documentation.
- Tunnel "Outside Terminal" (6356001) is "reference to the outside terminal of the tunnel," and "Inside Terminals[]" gives one per frame: https://labviewwiki.org/wiki/Tunnel_class. So if Loop Count is a Tunnel, the chain Loop Count then Outside Terminal is the documented route to the external N terminal.
- Node.Terminals[] is documented only as "array of references to the terminals of the node," indexed per the Context Help window, with no statement about which loop terminals it includes: https://labviewwiki.org/wiki/Node_class. A forum thread on terminal indices likewise gives no loop-specific listing: https://forums.ni.com/t5/LabVIEW/Scripting-Terminal-Information/td-p/4303374. Whether N is in the loop's Terminals[] is not settled by any source I found.

**(3) Optional Value input and datatype**
- Yes. The method has one optional input, Value (LV Variant), "value to which you want to set the constant," and returns a Constant refnum: https://labviewwiki.org/wiki/Terminal_class/Create_Constant_method.
- The constant's type comes from the terminal, not the variant. An NI forum thread confirms "what you're feeding in is the data value only. The type is taken from the terminal," shown by a strict VI refnum variant producing a non-strict constant: https://forums.ni.com/t5/LabVIEW/Create-Constant-VI-Reference-Type/td-p/3189022. That implies I32 for N and Boolean for the conditional terminal, though no source states those two cases explicitly.

**(4) Scripted constant losing its value on save/reload**
- No documented issue found. The LabVIEW Wiki known-issues list has scripting entries but none about constant values after save: https://labviewwiki.org/wiki/List_of_known_issues.
- The only related report is LabVIEW class constants: a non-default class constant equal to the class default is replaced by a reference to the default and can change later. It is not scripting-specific and has no CAR: https://lavag.org/topic/11050-labview-constant-values-change/.
- Scripting threads on constants discuss the Value property on nested constants but not persistence: https://forums.ni.com/t5/LabVIEW/VI-Scripting-replace-class-constant/td-p/4005523.

Sources:
- [Terminal class/Create Constant method - LabVIEW Wiki](https://labviewwiki.org/wiki/Terminal_class/Create_Constant_method)
- [Create Constant - NI](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/terminal/createconstant.html)
- [WhileLoop class - LabVIEW Wiki](https://labviewwiki.org/wiki/WhileLoop_class)
- [WhileLoop class/Loop End Ref property - LabVIEW Wiki](https://labviewwiki.org/wiki/WhileLoop_class/Loop_End_Ref_property)
- [ForLoop class - LabVIEW Wiki](https://labviewwiki.org/wiki/ForLoop_class)
- [ForLoop class/Loop Count property - LabVIEW Wiki](https://labviewwiki.org/wiki/ForLoop_class/Loop_Count_property)
- [Loop Count - NI](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/node/structure/loop/forloop/loopcount.html)
- [Tunnel class - LabVIEW Wiki](https://labviewwiki.org/wiki/Tunnel_class)
- [Node class - LabVIEW Wiki](https://labviewwiki.org/wiki/Node_class)
- [Wiring the conditional terminal of a while loop created by LabVIEW Scripting - NI Community](https://forums.ni.com/t5/LabVIEW/Wiring-the-conditional-terminal-of-a-while-loop-created-by/td-p/2115512)
- [VI Scripting - locate loop iteration and conditional terminals - NI Community](https://forums.ni.com/t5/LabVIEW/VI-Scripting-locate-loop-iteration-and-conditional-terminals/td-p/4344904)
- [Create Constant VI Reference Type - NI Community](https://forums.ni.com/t5/LabVIEW/Create-Constant-VI-Reference-Type/td-p/3189022)
- [Scripting - Terminal Information - NI Community](https://forums.ni.com/t5/LabVIEW/Scripting-Terminal-Information/td-p/4303374)
- [List of known issues - LabVIEW Wiki](https://labviewwiki.org/wiki/List_of_known_issues)
- [LabVIEW constant values change - LAVA](https://lavag.org/topic/11050-labview-constant-values-change/)
- [VI Scripting - replace class constant - NI Community](https://forums.ni.com/t5/LabVIEW/VI-Scripting-replace-class-constant/td-p/4005523)

## Sources

(extract from answer)

## What was done with it

Written 2026-09-25 by card chat-L2 from the record already committed (3701ba5, "Cycle 77: session outputs"); no new
judgement. (1) ACCEPTED and MEASURED: `Terminal.Create Constant` on `WhileLoop.Loop End Ref` built a `BooleanConstant`
in the loop body wired to the conditional terminal (`tools/bench/cards/result_77-2.json:4`, `const_loopterm_77.log:24`).
(2) ANSWERED BY MEASUREMENT, not by the docs: `Create Constant` on the For loop's `Terminals[0]` (N) built a top-level
`DigitalNumericConstant` wired to N (`result_77-2.json:3`); the verb is `gscript.create_const_loop_term`
(`result_77-2.json:2`). (3) Type-from-terminal: consistent with the I32 `1` read cold (`docs/NAMES.md:320-328`).
(4) No documented save/reload loss: COLD read after save + restart kept both constants (task 77-3,
`const_loopterm_77c.log:10-14`, recorded at `docs/NAMES.md:320-328`).
