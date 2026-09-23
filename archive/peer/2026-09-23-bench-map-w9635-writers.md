# bench-map-w9635-writers

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.4036  in 32 / out 13315 / cache-create 99079 / cache-read 1613405  (566s, 25 turn(s))
- **date:** 2026-09-23 18:31:05
- **outcome:** ANSWERED (570s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

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


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict: part (a) of the diagnosis holds for the three calls that ran. Parts (b) and (c) go further than the evidence, and (c) was never measured at all.**

## 1. The strongest reason the claim is wrong

**(b) generalises from the wrong source reference.** None of the three cells ever gave `Terminal.Connect Wire` a reference to #9641's *inner* terminal:
- C1 used w9649's term [1], which is #9641's outer face.
- C2 used #9655's source terminal.
- C3 used the WhileLoop node's border terminal t45, which is again the outer face.

All three sources are outside the loop, so a new tunnel at the border is the expected result. The run did not test "wire the existing inner terminal"; it tested "wire from outside" three times.

The source reference that was never tried is already a known, working technique here:
- `Tunnel.Inside Terminals[]` 6356000 returns Terminal references (`docs/cycle27-plan.md:2890-2891`, `docs/NAMES.md:1125`).
- `OpWireSR_*` `LeftOutNode` already passes a Tunnel-subclass **inside** terminal as the `Wire Source` of `Connect Wire` into a body-node sink, measured at ExecState 0→1 (`docs/toolkit-capabilities.md:54`, `docs/stage2-assembly-step-a.md:44-47,84-85`). `LeftShiftRegister` derives from `Tunnel`, and so does `LoopTunnel`. The reach to #9641 by uid is the cast used in `OpTunnelRead_v0` (`docs/toolkit-capabilities.md:72`).

So the honest version of (b) is: *no op on disk combines a LoopTunnel-by-uid seed with Connect Wire.* It is not "no route". The new op would be a seed swap on a writer already proven for this class of terminal. Note that the "dead end" in `docs/cycle27-plan.md:3510` applies only to `FlatSequenceInnerTunnel`, not to `LoopTunnel`.

Forum evidence says the same thing: which terminal is the reference and which is the `Wire Source` changes where LabVIEW routes the wire and whether it re-uses or creates tunnels ([Script connect existing loose wires to case tunnels](https://forums.ni.com/t5/LabVIEW/Script-connect-existing-loose-wires-to-case-tunnels/td-p/4195933), [wiring a pass-through tunnel inside a case](https://forums.ni.com/t5/LabVIEW/LabvVIEW-Scripting-wiring-a-pass-through-tunnel-inside-a-case/td-p/3945608)). Tunnels appear automatically only when the two terminals sit on different diagrams ([Programmatically creating a tunnel](https://forums.ni.com/t5/LabVIEW/Programmatically-creating-a-tunnel-with-LV-scripting/td-p/1830745)). #9641's inner terminal and #9623's outer terminal are both on diagram 639, so no border needs crossing.

**(c) is asserted, not read.** After the writes, the log reads only the inner net. `NET w22997` and `NET w23042` list two owners each: the new tunnel and #9623 (`bench_map_w9635.log:51,85,120`). Nothing after a write reads:
- the new tunnel's outer face or its feed;
- #9641 in any form (grep of the log: 9641 appears only at `:28` and `:62`, both before the writes);
- `IndexMode` of either tunnel (the wiki has no index-mode field for #9641 either).

So "same FSIT #9655 source" and "#9641 left in place with its inner terminal unwired" are inferences written as facts. `ExecState 1` together with `Is Broken? False` shows only that the new tunnel's outer face has *some* legal source.

## 2. An alternative explanation of the same evidence

The connect may have re-segmented the source-side net rather than just branching w9649. In C3 the junk Invoke node that appeared was given uid **9649**, the feed wire's own uid (`:102,112`). In C1 and C2 the junk node got 9205, and 9205 does not appear in the S1 wiki. If uids are unique across GObjects within a VI, 9649 being handed out means w9649 no longer existed under that uid after C3. The outer topology then changed (a new wire and new uids from #9655 to #9641 outer and #23058 outer, or something else) and was never observed.

Two things follow:
- **The rule-1a equivalence of C3 is unverified**, not merely "only the uid differs".
- **"LabVIEW always mints a new tunnel" confounds two things**: the side the source reference was on, and LabVIEW's policy on re-using a tunnel. The run cannot separate them.

On indexing: in a While Loop a tunnel created by wiring defaults to non-indexing, and indexing has no effect on a scalar anyway ([how to change tunnel mode using VI scripting](https://forums.ni.com/t5/LabVIEW/How-to-change-tunnel-mode-using-vi-scripting/td-p/3969392) shows the mode is a settable LoopTunnel property). This matters only if `# slices in stack` is an array, or if #9641 had been set to indexing. Neither was read. The lone leftover #9641 (outer wired, inner free) is not a second consumer and is probably harmless, but it is also unverified.

## 3. What would falsify the claim

- Falsifies (a)+(b): `Connect Wire` invoked on the sink terminal (D[43].N[24].t1) with `Wire Source` = `Tunnel(9641).Inside Terminals[0]` produces a wire whose source owner is `LoopTunnel #9641`, with the LoopTunnel count staying at 132.
- Falsifies (c): after C1, C2 or C3, walking the new tunnel's outer net shows a source other than FSIT #9655, or the IndexMode of the new tunnel differs from #9641's, or #9641's outer is no longer on the #9655 net.

## 4. Cheapest discriminating test

**Test 1 (settles (c) with existing readers, no new op, about 3 minutes).** Re-run cell C1 only and add three reads after the write:
- `OpTunnels_v0`-style read of LoopTunnel #23014 and #9641: outer wire uid and IndexMode, for each.
- `OpWireSource_v5` / `net_sources` on the new tunnel's outer wire. Gate: `source_owners == [('FlatSequenceInnerTunnel', 9655)]`.
- Existence of uid 9649 after the write.

**Test 2 (settles (b), needs one small op).** Take a copy of an existing `OpWireSR_*` `LeftOutNode` writer. Swap its source seed from `Shift Registers[]→Left Registers[]` to the `OpTunnelRead_v0` cast `(uid→Tunnel)→Inside Terminals[0]`. Point it at #9641 with sink = #9623's outer via structure #10407, on a scratch copy. Gate: source owner #9641, 132 LoopTunnels, ExecState 1.

- If test 2 passes, (a) and (b) are refuted and the op-rule entry is a single seed swap.
- If LabVIEW still mints a new tunnel when given an inner-terminal reference on the same diagram, then (a) is genuinely true, and I would accept it.

What would change my mind on (c): test 1 showing the #9655 source, a matching IndexMode, and w9649 intact.

**Local evidence:** `tools/bench/bench_map_w9635.log:28,47-53,81-87,102-122`; `tools/bench/bench_map_20260923/w9635_writers.py:38-51`; `docs/toolkit-capabilities.md:54,72`; `docs/stage2-assembly-step-a.md:44-47`; `docs/cycle27-plan.md:2890,3510`; `docs/NAMES.md:1125`; `docs/wiki/subvi/D1_s1_copy.json:24844-24853`.

Sources:
- [Programmatically creating a tunnel with LV scripting – NI Community](https://forums.ni.com/t5/LabVIEW/Programmatically-creating-a-tunnel-with-LV-scripting/td-p/1830745)
- [Script connect existing loose wires to case tunnels – NI Community](https://forums.ni.com/t5/LabVIEW/Script-connect-existing-loose-wires-to-case-tunnels/td-p/4195933)
- [LabVIEW Scripting: wiring a pass-through tunnel inside a case structure – NI Community](https://forums.ni.com/t5/LabVIEW/LabvVIEW-Scripting-wiring-a-pass-through-tunnel-inside-a-case/td-p/3945608)
- [How to change tunnel mode using VI scripting – NI Community](https://forums.ni.com/t5/LabVIEW/How-to-change-tunnel-mode-using-vi-scripting/td-p/3969392)

## Sources

(extract from answer)

## What was done with it

Material session, 2026-09-23 18:3x. The review is PARTLY ACCEPTED. Its point (b) is right: none of the three cells gave `Connect Wire` a reference to #9641's INNER terminal. So "no existing writer can reuse #9641" is true only of the writers as they are wired. It does not show that LabVIEW always mints a new tunnel.

- **Test 2** needs a new op: a seed swap on an `OpWireSR_*` `LeftOutNode` copy that puts `Tunnel.Inside Terminals[]` 6356000 behind the `Wire Source`. Building a new op is a judgement call, so it was NOT built. It is reported to the judgement session as the route that would reuse #9641.
- **Test 1** (settles (c) with existing readers) was folded into B run 4 on the 9635 row, in `stagekit._cfw_row`. It reads the new tunnel's uid, IndexMode and outer wire, `net_sources` on that outer wire, the old tunnel's IndexMode and outer wire, and whether w9649 still exists. The row gate is keyed beyond the tunnel (Pre-decided 146: the sink's `effective_sources`, S1 vs repaired). Results: `tools/bench/bench_map_b4.log` (`PD146 new tunnel vs old`).
- The judgement session's Pre-decided 146 (accept the new tunnel and delete the orphan) was applied as instructed.
