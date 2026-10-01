# c124-1-casetun-innerface-hyp

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.9457  in 42 / out 14825 / cache-create 131571 / cache-read 2656822  (185s, 29 turn(s))
- **date:** 2026-10-01 16:15:45
- **outcome:** ANSWERED (186s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim (failed prediction in tools/bench/diag_c123_casetun.py -> tools/bench/diag_c123_casetun.log:69-70).

Setting: LabVIEW 2026 VI Scripting driven over COM from Python. A Case structure with a Boolean selector (frames False / True)
was dropped on a loop body; an INPUT tunnel and an OUTPUT tunnel were created by wiring across the case border with
`Terminal.Connect Wire` (op OpConnectNested_v1: sink terminal and source terminal each addressed as
diagram index / Diagram.Nodes[] index / Node.Terminals[] index). In the False frame the input feeds Increment, Increment feeds
the output tunnel. The prediction was: the case node's `Terminals[]` would then list one UNWIRED source (input tunnel's inner face
in True) and one UNWIRED sink (output tunnel's inner face in True), so the same op could wire True-frame inner -> inner.
Observed: case `Terminals[]` = 3 rows only: selector + the two OUTER faces (log:69). No inner face listed.

The explanation formed:
 (1) A structure node's `Terminals[]` lists only outer faces; a tunnel's per-frame inner terminals are reachable only through the
     tunnel object (`Tunnel.Inside Terminals[]` 6356000, one per frame, order not documented as frame order -> map by
     `Terminal.Diagram` 634A002), or through a whole-VI `Traverse('Terminal')` read whose rows carry owner uid = the tunnel and
     frame_diagram = the frame's Diagram uid (our OpAllTerms_v1).
 (2) The True-frame pass-through therefore needs a writer that takes the two terminals by TERMINAL REFERENCE (resolved from the
     terminal's UID via vi.lib `UID to GObject Reference.vi` -> To More Specific Class(Terminal)) and calls
     `Terminal.Connect Wire` on the output tunnel's True inner terminal with `Wire Source` = the input tunnel's True inner terminal.
 (3) The three junk `Invoke` nodes counted after the run (log:71) come from the cross-border connect ops, not from the case.

Strongest reason this is wrong? Alternatives to test: e.g. the frame diagram's `Nodes[]` already contains the tunnel objects
(so the existing index-triple op reaches the inner face with no new op); `Connect Wire` refuses an inner->inner wire whose two
ends belong to tunnels of the same structure; `UID to GObject Reference.vi` does not resolve a Terminal uid; the inner
terminal order of `Inside Terminals[]` is frame order after all. Name the cheapest discriminating test for each.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict: (1) is mostly right but already known. (2) is the wrong thing to build. (3) is contradicted by the run's own per-operation counts.** The strongest refutation: LabVIEW already has one scripting method that makes the True-frame pass-through. You don't need a new terminal-reference writer, and you don't need inner-face addressing to make this wire.

## 1. Strongest reason the claim is wrong: the built-in method `Link Input Tunnel And Wire`
- `ConditionalTunnel` has a method **`Link Input Tunnel And Wire`, ID 5D251802** (short name `LinkTunAndWire`). It takes one input, the input tunnel's ConditionalTunnel reference. It "creates a link between the input tunnel you specify and this tunnel and **wires the tunnels in all cases where they are unwired**." `SelectorTunnel` is ConditionalTunnel's only child class.
  - Method page: [labviewwiki: Link Input Tunnel And Wire](https://labviewwiki.org/wiki/ConditionalTunnel_class/Link_Input_Tunnel_And_Wire_method)
  - Class page: [labviewwiki: ConditionalTunnel class](https://labviewwiki.org/wiki/ConditionalTunnel_class)
  - The NI primary page would not render through my fetch. It still needs checking on the machine.
- This fits our run. Both new tunnels are `SelectorTunnel` (log:38 and log:45: one per tunnel). The False frame is already wired (log:47-48 and log:64-65), so only the True frame is "unwired". That is exactly the pass-through that card A5/P4 needs.
- Nobody here has considered it. The only mention in the repo is a passing class-hierarchy citation (`archive/peer/2026-09-25-parity-l2a1-82-hyp.md:46`).
- Rule-1a caveat: the method also leaves a persistent *link*, so frames added later would auto-wire. For a fixed two-frame case, the result should be the same as an explicit wire. That needs checking against the graph, not assuming.

## 2. Claim (2) also depends on a step the project recorded as unmeasured
The proposed route resolves a terminal UID and then casts it to `Terminal` (`To More Specific Class`). On 2026-09-22 this step was recorded as **unmeasurable**: no VI on disk had a `Terminal`-typed cast seed (`docs/cycle27-plan.md:3595-3600`, Pre-decided 124). I found no later record that it was measured. Pre-decided 125 (`:3603-3611`) adds the hazard that a UID lookup can silently return a *different* object.

Even without the method in §1, there is a route made only of already-measured steps:
- `OpTunnelRead_v0` already casts to `Tunnel` and reads `Inside Terminals[]` 6356000 → Index Array. That array element is already a Terminal reference, with no Terminal cast needed. It was measured on SelectorTunnels of case #5540, 24/24 (`docs/toolkit-capabilities.md:84`).
- Pick the frame with `Terminal.Diagram` 634A002, as the project already does (`archive/2026-09-15-status-stage2-cycles-1-7.md:413`).

## 3. Claim (1) adds nothing new
These facts are already recorded:
- Tunnels are not listed in `Diagram.Nodes[]` (`docs/d1-loop12-17-split-plan.md:784`, Pre-decided 185). This also rules out your first alternative.
- Case selectors are class `Tunnel` (`:801`). That explains the census line `"Tunnel": 1`.
- Owner `Terminals[]` lists outer faces only. The diagnostic's own header says so (`tools/bench/diag_c123_casetun.py:4-5`).
- Per-frame inner faces are already readable with `OpAllTerms_v1`'s `frame_diagram` column (`tools/gscript.py:4078-4103`).

So log:69 shows something we already knew, not a surprise. The diagnostic never ran `OpAllTerms_v1` or `OpTunnelRead_v0` on the new tunnels, so this run did not test (1)'s "reachable through the tunnel" half.

## 4. Claim (3) is contradicted by the per-operation counts
- Input-tunnel `connect_nested_v1` (log:38): **0** new `Invoke`.
- Output-tunnel `connect_nested_v1` (log:45): **1** new `Invoke`.
- The other 2 of the 3 appeared before `oa` (Equal? or `case_wired`), or after `oc` (two `connect_from_wire` calls and the `net_sources` reads).

The run cannot tell these apart. "From the cross-border connect ops" is supported for at most 1 of the 3.

## Alternative explanations
- **For the gap:** the pass-through belongs on the *tunnel* object (`Link Input Tunnel And Wire`, or `Inside Terminals[]` plus `Connect Wire`), never on the case node.
- **For the Invoke junk:** a side effect of whichever operation is not purged. The purge exists in `case_wired`, according to the script's header. It may fire only on certain tunnel directions.

## What would falsify each part
- **Claim (2) / the method in §1:** calling `LinkTunAndWire` leaves True unwired, returns an error, or cannot be reached through a typed `SelectorTunnel`/`ConditionalTunnel` reference. Then a writer by reference really is needed, built from `Inside Terminals[]`, not a Terminal cast.
- **Claim (3):** a per-operation census with the extra Invokes appearing outside the two `connect_nested_v1` calls.

## Cheapest discriminating tests
1. **Method test (one scratch run, settles (2)):**
   - On a byte copy at the state after log:62, resolve output tunnel #27301 and input tunnel #27170.
   - Use `UID to GObject Reference.vi` → cast to `SelectorTunnel`. Seed it the way the `"VI Server:Wire"` seed was made in `OpConnectFromWire_v0`.
   - Add the mandatory UID-echo gate (Pre-decided 125).
   - Invoke 5D251802 on #27301 with `Input Tunnel` = #27170.
   - Read back with `OpAllTerms_v1`, filtered to `frame_diagram == 27084` (True).
   - Pass if:
     - there is exactly one new wire;
     - its source is owned by 27170 and its sink by 27301;
     - `Is Broken?` reads False;
     - the False-frame wires 27158 and 27337 are unchanged.
   - Optionally, read `Linked Input Tunnel` 5D251C01 back.
2. **Frame-order test (the brief's fourth alternative, needs no new op):** run `OpTunnelRead_v0` on #27170 with term index 0 and 1. Compare the frame-diagram UID returned against `{False: 27051, True: 27084}` (log:31). Repeat after adding or reordering a frame if order matters.
3. **Invoke attribution test (settles (3)):** in the same script, take an `objs()` snapshot after *every* operation, including both `connect_from_wire` calls and `case_wired`.
4. **"Connect Wire refuses inner→inner" (your second alternative):** only worth testing if test 1 fails. Hand wiring tunnel to tunnel is ordinary LabVIEW, and the linked-tunnel feature exists because it is allowed.

**What would change my mind:** test 1 failing, either refused or leaving True unwired. Then (2)'s writer is needed, but built on `Inside Terminals[]` (already measured), not on a Terminal cast.

Sources:
- [labviewwiki: Link Input Tunnel And Wire method](https://labviewwiki.org/wiki/ConditionalTunnel_class/Link_Input_Tunnel_And_Wire_method)
- [labviewwiki: ConditionalTunnel class](https://labviewwiki.org/wiki/ConditionalTunnel_class)
- [labviewwiki: Linked Input Tunnel property](https://labviewwiki.org/wiki/ConditionalTunnel_class/Linked_Input_Tunnel_property)
- [labviewwiki: Tunnel class](https://labviewwiki.org/wiki/Tunnel_class)

## Sources

(extract from answer)

## What was done with it

Card 124-1 (material, 2026-10-01 16:2x). (1) accepted as already-known: tunnels are not in Nodes[]; inner faces per frame are
read from OpAllTerms_v1's frame_diagram - that is how `gscript.case_inner_face` was written (tools/gscript.py, after case_wired).
(2) `Link Input Tunnel And Wire` 5D251802 NOT used: brief_124-1.md fixes `case_frame_wire(src, dst)` with node ends too, and the
method leaves a persistent link (rule-1a question) - reported to the judgement session as an open alternative. The writer was
built as OpConnectTermUid_v0 (Traverse('Terminal') + U2G -> Terminal-seeded TMSC, both uid-echoed per PD125); its first build run
failed on a script post-condition before any Terminal cast was exercised (tools/bench/diag_c124_opconnecttermuid.log:37), so the
"Terminal cast unmeasured" objection is still open. (3) accepted: the Invoke attribution is not settled by 123-9; the purge was
put inside both connect functions (build_opconnectnested_v1.connect_nested_v1, build_opconnectfromwire_v0.connect_from_wire).
