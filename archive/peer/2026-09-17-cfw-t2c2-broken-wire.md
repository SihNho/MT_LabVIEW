# cfw-t2c2-broken-wire

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-17
- **outcome:** ANSWERED (160s)
- **why asked:** mandatory review of the FAILED PREDICTION at gate T2c2 of `tools/bench/build_opconnectfromwire_v0_run2.log` (the wire the new op created on a copy of the real VI reads `Wire.Is Broken? TRUE`)
- **verdict:** PARTLY REFUTED - the two-source diagnosis stands; my asserted CAUSE (index drift from restructuring) is unproven and a better alternative was supplied

## Question

LabVIEW VI Scripting (LabVIEW 2026, VI Server over COM). Attack the reading below of a FAILED PREDICTION.

## The prediction that failed
`tools/bench/build_opconnectfromwire_v0_run2.log` gate T2c2 predicted: "the wire this op creates reads
`Wire.Is Broken?` (6371004) == FALSE". Observed TRUE. 42 gates pass, this one fails.

## What the op does
`Terminal.Connect Wire` 6349C03. SOURCE = a terminal taken from an existing wire via `Wire.Terms[]` 6371003,
filtered by `Terminal.Is Source?` 634A003. SINK = `Diagram[d].Nodes[n].Terminals[t]`, pure index addressing.
In the SAME run, on a small scratch VI, the identical op created a wire from an outer-diagram wire's source
terminal into a node inside a new While loop body and read `Is Broken? FALSE`, `error ''`, wire 0 -> 229,
LoopTunnel 0 -> 1. So the op works at least once.

## The failing case, raw
Target: a throwaway copy of a large real VI, UNMODIFIED (no restructuring done to it).
SOURCE wire w5812. Its terminals, read with the same fleet immediately before the call:

    i=0  Is Source? TRUE   owner FlatSequenceInnerTunnel #5818   reciprocal wire 5812
    i=1  Is Source? FALSE  owner LeftShiftRegister     #5805
    i=2  Is Source? FALSE  owner LoopTunnel            #5569

SINK: node uid 5540 (a Case Structure inside a While loop body, Diagram traverse index 43), terminal index 1,
deleted down to `Connected Wire == 0` first (verified: the sequence was 5979 -> 5637 -> 0).

Result: op `error out` EMPTY; the sink terminal went 0 -> wire 1231; wire count delta +1; and the op's own
ordered readback said:

    UID 2 = 1231    Is Broken? = True    Name = 'Bead is good? array out'

`Name` there is `Terminal.Name` of the sink terminal the op actually resolved. Reading the created wire w1231
back with `Wire.Terms[]` gives TWO terminals that both report `Is Source? TRUE`:

    i=0  Is Source? TRUE  owner SelectorTunnel #5680  reciprocal 1231
    i=1  Is Source? TRUE  owner LoopTunnel     #2497  reciprocal 1231

## OUR READING, which you must try to destroy
"The terminal index 1 came from a census taken on a RESTRUCTURED copy of this VI and was applied to an
UNRESTRUCTURED one, so index 1 no longer denotes the unnamed input tunnel we meant - it denotes the Case
structure's OUTPUT tunnel `Bead is good? array out`. Connecting a second driver onto an already-driven output
net is what makes the wire broken, and the two `Is Source? TRUE` terminals on w1231 are that. The op is fine;
the caller addressed the wrong terminal."

## Already ruled out here (do not spend your answer on these)
* Not an op error: `error out` and both sub-VI error indicators came back empty.
* Not a stale readback: the `Is Broken?` read is forced AFTER the write by branching the Invoke's own `error out`
  into the reading property node's `error in`; it returned the newly created wire's uid (1231), not 0.
* Not an unbared sink: the sink was deleted down to `Connected Wire == 0` and asserted before the call.

## What we need from you
1. The strongest reason our reading is WRONG.
2. At least one alternative explanation - in particular, whether `Terminal.Connect Wire` into a structure TUNNEL
   from outside that structure is expected to produce a broken wire regardless of direction, and whether two
   terminals reporting `Is Source? TRUE` on one wire has any meaning OTHER than "two drivers".
3. What observation would falsify our reading.
4. The cheapest discriminating test through VI Server scripting, naming properties/methods and their numeric ids.
Cite NI documentation, labviewwiki property pages or forum threads by URL where you have them.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

1. **Strongest reason the claim is wrong**

The evidence does **not** establish that restructuring changed terminal index 1. It establishes only that, in the unrestructured VI, index 1 resolved to a source terminal named `Bead is good? array out`.

That is a causal gap: no before/after terminal census demonstrates that the same index selected the intended unnamed input on the restructured copy. `Node.Terminals[]` explicitly uses terminal indexes, but the documentation does not promise that those indexes preserve semantic identity across separately modified copies. Likewise, UIDs are guaranteed unique only *within one VI*, so matching raw UIDs across copies would not prove identity. [Node.Terminals[]](https://www.labviewwiki.org/wiki/Node_class/Terminals%28%29_property), [GObject.UID](https://labviewwiki.org/wiki/GObject_class/UID_property)

There is also a more immediate discrepancy: the new wire’s reported terminals are `SelectorTunnel #5680` and `LoopTunnel #2497`, not the supplied source terminal `FlatSequenceInnerTunnel #5818`. That makes the exact topology—especially which automatically traversed structure boundary supplied the second source—less certain than the proposed explanation implies.

2. **Alternative explanation**

`Connect Wire` may have routed the cross-diagram connection through the enclosing While-loop tunnel. On the While-body diagram, the inside terminal of an **input** loop tunnel is itself a source. If terminal 1 is the outside terminal of a Case **output** tunnel, that terminal is also a source. The resulting local wire would therefore connect:

```text
While input tunnel, inside side (source)
        → broken wire ←
Case output tunnel, outside side (source)
```

That exactly fits the returned `LoopTunnel + SelectorTunnel`, both `Is Source? = TRUE`, without requiring an “already-wired output net.” Your precondition `Connected Wire == 0` means the Case terminal had no outside wire; its *source direction* can nevertheless already be established by wiring inside the Case.

Connecting a wire to a structure tunnel from outside is **not inherently broken**. Direction and side matter:

- A source wired to the outside terminal of an **input** tunnel is normal.
- A source wired to the outside terminal of an **output** tunnel creates a source-to-source conflict.
- NI describes tunnels as either structure inputs or outputs and says a tunnel becomes undirected when a source exists on both sides—or neither side. [NI: Undirected Tunnel Error](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019L9BSAU)
- VI Scripting exposes the sides separately as `Tunnel.Outside Terminal` and `Tunnel.Inside Terminals[]`. Case structures have one outside terminal and an inside terminal for each case. [Tunnel class](https://labviewwiki.org/wiki/Tunnel_class), [case-tunnel scripting discussion](https://forums.ni.com/t5/LabVIEW/LabvVIEW-Scripting-wiring-a-pass-through-tunnel-inside-a-case/td-p/3945608)

As for the two `Is Source? = TRUE` results: there is no credible benign wire-level interpretation. The documented contract for `Wire.Terminals[]` says that more than one source means the wire is broken. However, “two source terminals” does **not necessarily mean two ordinary computational producer nodes**; one or both can be structure-boundary terminals representing dataflow across diagrams. [Wire.Terminals[]](https://labviewwiki.org/wiki/Wire_class/Terminals%28%29_property), [Terminal.Is Source?](https://labviewwiki.org/wiki/Terminal_class/Is_Source%3F_property)

3. **Observation that would falsify the claim**

The restructuring/index-drift explanation is falsified if a read-only census of both copies shows that `Node.Terminals[1]` resolves to the same semantic terminal in each:

- same terminal name;
- same `Is Source?` value;
- same inside/outside relationship to the same Case tunnel;
- same owning-diagram role.

It would be even more decisively falsified if the restructured copy’s index 1 is also `Bead is good? array out` and reports `Is Source? = TRUE`. Then restructuring did not redirect the index; the caller’s terminal assumption was wrong independently of restructuring.

Conversely, finding that index 1 is an unnamed sink in the restructured copy but the named output source in the unrestructured copy would strongly support your reading.

4. **Cheapest discriminating test**

Do a **read-only, pre-connect terminal-side census** on both copies. No wiring or deletion is required:

1. Read Case node `Terminals[]` — `6359000`.
2. For element 1, read:
   - `Name` — `634A004`
   - `Is Source?` — `634A003`
   - `Diagram` — `634A002`
   - `Connected Wire` — `634A000`
   - `Owner` — `6327806`
   - `Class Name` — `6327803`
   - `UID` — `632A813`
3. Read Case `Tunnels[]` — `6360801`.
4. For every tunnel, read:
   - `Outside Terminal` — `6356001`
   - `Inside Terminals[]` — `6356000`
5. Compare the terminal-1 reference against each outside and inside terminal reference, then report the matched side and that side’s `Is Source?`.

These property meanings and IDs are documented here: [Terminal class](https://labviewwiki.org/wiki/Terminal_class), [Structure.Tunnels[]](https://www.labviewwiki.org/wiki/Structure_class/Tunnels%28%29_property), [Tunnel class](https://labviewwiki.org/wiki/Tunnel_class), [Generic.Owner](https://labviewwiki.org/wiki/Generic_class/Owner_property).

After trying to refute it: the **core diagnosis—source was connected to a Case output source, producing a two-source broken wire—still holds strongly**. What does **not** yet hold is the asserted cause that restructuring changed index 1. The read-only two-copy census above would change that assessment.

## Sources

(extract from answer)

## What was done with it

**verdict: the CONCLUSION survives, the CAUSE I gave does not, and the peer supplied a better mechanism.**
Dispatched as the mandatory review of `build_opconnectfromwire_v0_run2.log` gate T2c2 (42 pass / 1 fail). codex,
`-Kind review`, ANSWERED in 161 s (`tools/bench/peer_cfw_t2c2.log`, `BGRUN END rc=0 after 161s`).

**What stands, and it is the important half: the op is not the fault.** The wire is broken because it has TWO
source terminals, and the peer confirms there is no benign reading of that - `Wire.Terminals[]` reporting more
than one `Is Source? TRUE` means broken. `Terminal.Connect Wire` into a structure tunnel from outside is NOT
inherently broken; direction and SIDE decide it. A source onto the outside terminal of an INPUT tunnel is normal;
a source onto the outside terminal of an OUTPUT tunnel is a source-to-source conflict. The op resolved a terminal
whose `Terminal.Name` is `Bead is good? array out`, and the run's own readback printed that name.

**What is WITHDRAWN: my cause.** I wrote that terminal index 1 means something different on the restructured copy,
so the index drifted. **Nothing in this run measures that** - there is no before/after census of `Node.Terminals[]`
on the two copies, and the peer is right that `Node.Terminals[]` indexes carry no documented semantic identity
across separately modified copies, so the claim is unsupported either way.

**The peer's alternative, which fits the data better than mine and costs nothing to believe:** `Connect Wire`
routed the cross-diagram connection through the enclosing While loop, and on the loop's BODY diagram the inside
terminal of an INPUT loop tunnel is itself a SOURCE. So the local wire joined `LoopTunnel #2497` (inside, source)
to `SelectorTunnel #5680` (a Case OUTPUT tunnel's outside terminal, also a source) - which is exactly the pair the
run printed, and it needs no already-wired net. My precondition (`Connected Wire == 0`) only proved the Case
terminal had no OUTSIDE wire; its source DIRECTION can already be fixed by wiring inside the Case.

**What this costs the route-B plan, stated so it is not lost:** the `from-tunnel` rows cannot be addressed by a
`(node, terminal index)` pair alone. A tunnel has an OUTSIDE terminal and one INSIDE terminal per frame
(`Tunnel.Outside Terminal` 6356001, `Tunnel.Inside Terminals[]` 6356000, both already used by `OpTunnelRead_v0`),
and the SINK for these rows must be the correct SIDE, not merely the correct index. That is a change to how the
recipe ADDRESSES its sinks, not to the op - and it is a judgement call, so it is recorded and left.

**Cheapest next step, which this session did NOT take** (it is the third build attempt and the budget is two): the
peer's read-only two-copy census - `Node.Terminals[]` index 1 of `#5540` on an unrestructured copy AND on a
restructured one, comparing `Terminal.Name` 634A004, `Is Source?` 634A003, and the inside/outside relationship.
It costs one diagnostic and it settles whether the index drifted or the caller's terminal assumption was simply
wrong from the start.

**Not adopted:** nothing was rejected. Note the peer's own closing line - *"the core diagnosis still holds
strongly; what does not yet hold is the asserted cause that restructuring changed index 1"* - is recorded here
verbatim so the next session does not re-derive it.
