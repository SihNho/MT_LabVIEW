FAILED PREDICTION (connectivity-map plan step 5b, bench item 4: which EXISTING writer can re-make S1's wire 9635 on a dated
scratch of `claudeDev\D1_s1_copy.vi`, the original's bytes). Attack the DIAGNOSIS below; find the strongest reason it is wrong.

THE WIRE (S1 graph, `tools/jev_candidates.load("D1_s1_copy")`): w9635 = LoopTunnel #9641 InnerTerminal '# slices in stack'
(source, diagram uid 639 = frame-loop body of WhileLoop #637) -> SelectorTunnel #9623 OuterTerminal '# slices in stack'
(sink, diagram 639; its case structure is #10407). #9641's OUTER terminal is fed by w9649 from FlatSequenceInnerTunnel #9655
on diagram 686. #9623's inner [1] feeds #9243 'x' by w9612. w9635 is #9641 inner's ONLY wire.

WHAT RAN (`tools/bench/bench_map_20260923/w9635_writers.py`, log `tools/bench/bench_map_w9635.log`). Three cells, each on a
FRESH scratch with w9635 deleted (ExecState 1 -> 0, 132 LoopTunnels); sink addressed as `D[43].N[24].t1` (structure #10407)
by `stagekit.address`:
  C1 `OpConnectFromWire_v0` (Terminal.Connect Wire on the sink, Wire Source = Wire(uid 9649).Terms[1] = #9641's OUTER term)
  C2 same op, Wire Source = Wire(9649).Terms[0] = FSIT #9655's source terminal
  C3 `OpConnectNested_v1`, source = D[19].N[4].t45 = WhileLoop #637's node terminal carrying w9649 (the #9641 outer face)
PREDICTED (docstring): C1 and C3 -> op error or no wire; C2 -> a NEW LoopTunnel; all three fail the uid gate.
OBSERVED: all three: op error '', a new wire (C1/C2 uid 22997, C3 23042), `Wire.Is Broken?` False, ExecState 0 -> 1, and
its source owner a NEW LoopTunnel (#23014 in C1/C2, #23058 in C3), LoopTunnel count 132 -> 133; #9641 left in place with
its inner terminal unwired. The C1/C3 part of the prediction failed.

DIAGNOSIS UNDER ATTACK: (a) Terminal.Connect Wire given ANY terminal outside the loop (the tunnel's outer face, the feed's
source, or the loop node's border terminal) routes a new wire from the NET's source across the border, and LabVIEW always
mints a new tunnel rather than reusing an existing one whose inner side is free; (b) therefore no existing writer on disk
(`docs/toolkit-capabilities.md` rows 54/67/68/70; `OpFsInnerTunnelConnect_v1` casts to FlatSequenceInnerTunnel,
`tools/recipes/build_d1_m3a3b_d3.py:33`) can make a wire whose source is an EXISTING LoopTunnel's inner terminal;
(c) the result is computation-equivalent (same FSIT #9655 source -> same #9623/#9243 sink) and only the tunnel uid differs.
QUESTIONS: is there an existing route (VI Scripting property/method, a Loop/Tunnel `Inside Terminals[]` read such as
`OpTunnelRead_v0`'s cast(Tunnel) -> Inside Terminals[] 6356000, a wire-typed trick, or ordering, e.g. connecting FROM the
sink side with the tunnel inner as the invoke target) that makes the wire reuse #9641? Is (c) wrong in any way that
matters to the computation (indexing mode of the new tunnel vs #9641, tunnel position, a second consumer)?
