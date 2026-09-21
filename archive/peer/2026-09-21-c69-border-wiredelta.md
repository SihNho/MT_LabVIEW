# c69-border-wiredelta

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.3552  in 16 / out 49657 / cache-create 159231 / cache-read 833115  (632s, 16 turn(s))
- **date:** 2026-09-21 21:38:17
- **outcome:** ANSWERED (636s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

QUESTION 1 (primary): is this cross-border wire actually correct, or does `wire_delta 1` mean it is not the wire we think it is?

A LabVIEW VI Scripting run wired a CaseStructure input tunnel that sits inside a While loop body from a source terminal on a wire OUTSIDE that loop, using our own op `OpConnectFromWire_v0.vi` (SOURCE = an existing wire's uid + which terminal on that wire; SINK = diagram index / `Nodes[]` index / `Terminals[]` index).

Call: `connect_from_wire(wire=9649, wire_term=0, sink_diag=22, sink_node=5, sink_term=1)`.

Observed:
- `op_error ''`
- readback `UID 2` = 24009, `Is Broken?` False, `Name` = '# slices in stack'
- SOURCE-side wire uid 9649 vs SINK-side wire uid 24009 (two different uids)
- the sink node's wired-terminal count went 6 -> 7
- diagram counts moved `LoopTunnel 135->136`, `Tunnel 475->476`, `Wire 1918->1919`, and the target loop's terminal count 5 -> 6
- **`wire_delta` 1, where our acceptance test predicted 3**

Where the 3 came from: our other op `OpConnectNested_v1` measured `wire_delta 3` with `LoopTunnel 0 -> 2` when wiring two terminals on two different nested diagrams (`docs/toolkit-capabilities.md:68`, `docs/cycle27-plan.md:2477-2479`). `OpConnectFromWire_v0`'s own recorded T1 result is `sink wire 0 -> 229` with `LoopTunnel 0 -> 1` (`docs/toolkit-capabilities.md:70`).

The claim to attack: *the row landed correctly, and `wire_delta 1` is the right expectation for a ONE-border crossing, so the acceptance test was mis-specified rather than the wire being wrong.*

Attack it. In particular: can `Is Broken?` read False on the sink-side segment while the OUTER segment is not actually connected to the intended source — i.e. does this evidence prove the value traverses the border, or only that a well-formed wire exists on the inside?

Name the cheapest read, using only a VI-Server/ActiveX property or method, that would DISCRIMINATE "the value reaches the tunnel from wire 9649's source" from "a legal-looking wire that does not carry it". We can read wire uids, `Wire.Is Broken?`, a wire's `Terms[]` walk by uid, node terminal names/indices via `Diagram[d].Nodes[n].Terminals[t]`, diagram object counts by class, and `ExecState`. We cannot address a tunnel through `Nodes[]`, and we do not run the VI (it is a mid-restructure intermediate that is never executed).

ALREADY RULED OUT, do not re-propose:
- the source was measured non-empty immediately before the write (wire 9649's `Terms[]` walk returned source owner `FlatSequenceInnerTunnel #9655`)
- the sink terminal index was re-read on the LIVE post-move target by name, not carried from a pre-move census
- a junk `Invoke` node minted during the call was purged and the diagram census returned to its prior 632 objects

QUESTION 2 (secondary, one paragraph is enough): is there ANY route to re-create a dropped SINK that is a tunnel?

The same restructure must re-connect `SelectorTunnel #12673` (`Q_focusback`) as a SECOND sink of `#10407` t6 `'position [internal units]'`; in the untouched original that terminal fed both a shift register and #12673 (one wire, one source, two sinks). Our writers address a SINK only as `Diagram[d].Nodes[n].Terminals[t]`, and a tunnel is not a `Nodes[]` entry — `OpConnectFromWire_v0` relaxes only the SOURCE side. Is there a VI-Scripting route to a tunnel-owned SINK terminal (by class traversal, by a wire's `Terms[]`, by branching an existing wire, by `Connect Wire` with a tunnel reference, or otherwise)? If the honest answer is that it needs a new op, say which property/method that op would have to call. Cite NI documentation rather than inferring from our files.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write is disabled in this session — correct for the read-only reviewer role — so the review is the answer itself.

---

# Verdict: the claim does not survive

Not because "1" is the wrong number — it is probably the right number — but because **the acceptance test contains no post-write measurement of the source side at all**, and every alternative that would make this row *wrong* also produces `wire_delta 1`.

## 1. Strongest reason the claim is wrong: the acceptance line quotes an input argument as if it were an observation

`tools/bench/build_d1_m3a1.log:488`:
> `BORDER-ROW ACCEPTANCE (A3): wire_delta 1 (expect 3) ; SOURCE-side wire 9649 vs SINK-side wire 24009 -> TWO DIFFERENT uids True ; Wire.Is Broken? False ; sink WIRED-terminal count 6 -> 7 ; LANDED True`

"SOURCE-side wire 9649" was never read after the write — it is the argument passed in at `:473`. The last time the machine was asked anything about 9649 is `:468`, **before** the write. Four of the five items are measured on the sink side of the new border; the fifth is a memory. The row's actual question — *does the new tunnel's outside draw from 9649's net* — has zero evidence either way.

So "1 vs 3" is a debate about calibrating an instrument that is not pointed at the thing being measured. And "1" is itself unmeasured here: the only recorded one-border from-wire connect, T1 at `docs/toolkit-capabilities.md:70`, records `sink wire 0 → 229`, `Is Broken? FALSE`, `LoopTunnel 0 → 1` — **and no wire delta**. The "3" came from a different op with a different source topology (unwired node terminal, two borders, `LoopTunnel 0 → 2`, `:68`). One unmeasured expectation was swapped for another and the difference was called a spec bug.

**Direct answer to the sub-question: no.** The op reads `UID 2` from `Terminal.Connected Wire` on the **sink**, then `Wire.Is Broken?` on that uid (`:70`). `Is Broken?` is per-Wire ([LabVIEW Wiki](https://labviewwiki.org/wiki/Wire_class/Is_Broken%3F_property)); 24009 lives on diagram 22, and the outer segment is a different object on a different diagram the readback never touches. What `False` *does* buy, and it is worth keeping: it rules out the T2c2 two-source pathology and a type conflict on the inner segment — i.e. the sink was an input, not an output. Nothing about the border.

## 2. Alternative explanations of the same evidence

**(a) The outer wire was destroyed and re-created; uid 9649 was recycled.** Then Δwire = −1 + 1 + 1 = **+1**, identical arithmetic, and `Is Broken? False` equally expected. The evidence sits unexamined at `:475`:
> `CENSUS DIFF: Node 632 -> 633 ; 1 new uid(s): [(9649, 'Invoke', (4593, 2718))]`

**The junk node was minted carrying uid 9649 — the uid of the wire the call was told to branch.** Every other object created in this run took a monotonic uid in the 23 800–24 009 band (`:498–:526`; the new wire is 24009). A new object on 9649 is a recycled uid, and LabVIEW recycles only when the holder is gone. **This is not the ruled-out item**: what you ruled out is the census accounting (632 → 633 → 632), and that is genuinely sound — `:477–:485` show the junk node had 0 wired terminals, so the purge destroyed no wires, and `:556` confirms `Wire 1919`. What nobody examined is *which uid it was given*. Either wire 9649 ceased to exist during the call, or this fleet can mint an object bearing a live object's uid — in which case every uid-keyed census in the D1 rewire is unsafe. Both kill the premise that 9649 still means what `:468` said.

**(b) The outer side was never wired** (+1 inner only). Not exotic here: the sink was itself a legal **unwired** case tunnel immediately before the write — `:470` *"it currently carries wire 0"* — and `ExecState` is 0 at every boundary anyway. Whether LabVIEW propagates "unwired tunnel" into the inner wire's `Is Broken?` is **not settled by your measurement and not settled by NI's docs**: the `Connect Wire` reference ([6349C03](https://labviewwiki.org/wiki/Terminal_class/Connect_Wire_method)) documents `Wire Source`, `Auto Wire?`, `Wiring Specs`, `Auto Route?` and says *nothing* about cross-diagram behaviour or auto-tunnels. "LabVIEW makes the tunnel itself, correctly" is your observation, not a documented contract.

**(c) Wire-identity drift, already measured and never explained.** `docs/toolkit-capabilities.md:68`: of 8 wires made this way, *"at most 2 of 8 became null and 1 of 8 changed wire identity"* (`26189 → 26412`), plus the standing warning **"Do not cite RBW-survival as evidence a wire is good."**

I am *not* claiming the junk node corrupted the counts (the log rules that out), nor that the "+1 for one border off an existing wire" arithmetic is wrong. It is probably right. It is just not evidence.

## 3. What would falsify the claim

Re-walk **9649's `Terms[]`**. At `:468` it held exactly two real terminals + terminator: `i0 source FlatSequenceInnerTunnel #9655`, `i1 sink LoopTunnel #9641`. A correct branch must now show a **third**, `is_source=False`, `owner_class LoopTunnel`, owner = the new tunnel on loop #23032 (the loop that went 5 → 6 at `:490`). Falsified if: 9649 still has two terminals; 9649 no longer resolves as a `Wire`; or that owner uid ≠ the LoopTunnel that sources 24009.

## 4. Cheapest discriminating test — two calls, ~0.2 s each, nothing new built

`OpWireSource_v5` is UID-addressed (`:60`) and already ran twice this session (`:468`, `:549`). This is just taking the "after" of a "before" you already have.

1. `OpWireSource_v5(UID 2 = 9649)` → expect **3** real terminals; record the new one's `owner_uid` as **T**.
2. `OpWireSource_v5(UID 2 = 24009)` → expect **exactly one** `is_source=True`, `owner_class LoopTunnel`, `owner_uid == T`.

**Pass = the same LoopTunnel uid is a SINK on 9649 and the SOURCE of 24009** — the value path proven by object identity, end to end. It also re-tests the T2c2 two-source pathology and the uid-recycling alternative. Properties all built: `Wire.Terms[]` 6371003, `Is Source?` 634A003, `Connected Wire` 634A000, `Generic.Owner` 6327806, `GObject.UID` 632A813.

⚠️ Do **not** substitute `ExecState`: `docs/cycle27-plan.md:2501-2507` measured `OpConnectNested_v1` driving `ExecState` 1 → 0 on an *unchanged* VI with `wire_delta 0`, and these ops perform a perturbing `Is Broken?` read internally.

**What would change my mind:** step 1 returning that third terminal with `owner_uid == T`. Then the row is correct and `wire_delta 1` is vindicated — and the acceptance test should be rewritten to assert *that identity*, not re-tuned to a different integer. The number was never the instrument.

## Q2 — **no new op and no new property are needed**

The premise is true but does not bite: a tunnel is not a `Nodes[]` entry, yet **its terminal is an entry in its owning structure node's `Terminals[]`**, and this run proves it twice. The sink you just wrote, `#10407 Nodes[5].Terminals[1] '# slices in stack'` (`:521`), *is* a case tunnel; and at `:526`/`:549` the same node's `Terminals[6]` carries wire 23963 whose source terminal reads `owner_class SelectorTunnel, owner_uid 2017`. So structure-node terminals *are* tunnel terminals, with the Tunnel uid visible as owner. Route for #12673: `OpOwnerChain_v1(12673)` → its owning Case Structure → walk that node's `Terms[]` → take the entry named `Q_focusback` (name resolution as `:470` did, never a carried index — that is what broke T2c2) → feed the **existing** `OpConnectFromWire_v0`, source = wire **23963** (`:548`; the live net is 23963, *not* the original 9113 the inventory names). Hazard: owner chains terminate silently at a `FlatSequenceFrame` (`:61`). If that walk does not expose it, the fallback costs exactly one unbuilt property: `Tunnel` descends from **GObject, not Terminal** ([Tunnel class](https://labviewwiki.org/wiki/Tunnel_class)), so a Tunnel refnum can never receive `Connect Wire` — but it hands out Terminal refs via `Inside Terminals[]` (already built, 6356000, `:72`) and **`Outside Terminal`**, and for an *input* tunnel the sink is the **outside** one ([NI forum](https://forums.ni.com/t5/LabVIEW/LabvVIEW-Scripting-wiring-a-pass-through-tunnel-inside-a-case/td-p/3945608) warns the wrong choice wires the wrong side of the structure). Read that property's short name off the machine — the wiki returned a numeric that does not reconcile with its own decimal. And note `Connect Wire`'s `Wire Source` is typed **GObject**, not Terminal: the source side was never the constrained one.

**Sources:** [Tunnel class](https://labviewwiki.org/wiki/Tunnel_class) · [Terminal/Connect Wire 6349C03](https://labviewwiki.org/wiki/Terminal_class/Connect_Wire_method) · [NI Connect Wire API ref](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/terminal/connectwire.html) · [Wire/Is Broken?](https://labviewwiki.org/wiki/Wire_class/Is_Broken%3F_property) · [NI forum: tunnels in case structures](https://forums.ni.com/t5/LabVIEW/LabvVIEW-Scripting-wiring-a-pass-through-tunnel-inside-a-case/td-p/3945608) · local: `build_d1_m3a1.log:468,470,473,475,477-485,488,490,521,526,548-552,556`; `toolkit-capabilities.md:60,61,68,70,72`; `cycle27-plan.md:2501-2507`

## Sources

(extract from answer)

## What was done with it

**The verdict is ACCEPTED IN FULL against this cycle's own work. The claim it attacked was mine, written
this cycle, and it does not survive.**

- **Q1 accepted.** `tools/bench/build_d1_m3a1.log:488` quotes "SOURCE-side wire 9649" as though it were an
  observation; it is the argument passed in at `:473`, and the machine was last asked about 9649 at `:468`,
  **before** the write. Four of the five items in that acceptance line are sink-side, and the fifth is a
  memory — so the row's real question, *does the new tunnel's outside draw from 9649's net*, has no evidence
  either way. The sub-question is answered no: `Is Broken?` is per-Wire, 24009 lives on diagram 22, and the
  outer segment is a different object the readback never touches. What it does buy is kept — it rules out the
  T2c2 two-source pathology and a type conflict on the inner segment.
- **Pre-decided 66's acceptance test is WITHDRAWN and replaced** (new Pre-decided 70). Re-tuning `wire_delta`
  from 3 to 1 would have been calibrating an instrument that is not pointed at the thing being measured; the
  number was never the instrument. `wire_delta 1` is probably right and is no longer asserted either way.
- **Alternative (a) is accepted as a LIVE HAZARD, not a curiosity** (new Pre-decided 71). The junk node was
  minted carrying uid **9649** — the uid of the wire the call was told to branch — while every other object
  this run created took a monotonic uid in the 23,800–24,009 band. Either wire 9649 ceased to exist during
  the call, or this fleet can mint an object bearing a live object's uid, in which case **every uid-keyed
  census in the D1 rewire is unsafe**. The review is explicit that this is NOT the item we ruled out: our
  census accounting (632 → 633 → 632) is sound and was never the question; which uid the junk node was given
  is what nobody examined. Until the test below settles it, the t1 row is **WRITTEN, NOT VERIFIED**, and no
  claim of computational equivalence rests on it.
- **The discriminating test is adopted verbatim** as an IN-RUN gate, because it cannot be run on this run's
  artefact — `ExecState` 0 blocked the save and the scratch was deleted, so there is nothing left to read.
  Two `OpWireSource_v5` calls, both properties already built: `(UID 2 = 9649)` must now show a **third** real
  terminal, `is_source=False`, `owner_class LoopTunnel`, owner uid **T**; `(UID 2 = 24009)` must show exactly
  one `is_source=True`, `owner_class LoopTunnel`, `owner_uid == T`. Pass = the same LoopTunnel uid is a SINK
  on 9649 and the SOURCE of 24009. `ExecState` is NOT substituted (`docs/cycle27-plan.md:2501-2507`).
- **Q2 accepted, and it removes the sixth row's blocker** (new Pre-decided 72). A tunnel is not a `Nodes[]`
  entry, but its terminal IS an entry in its owning structure node's `Terminals[]` — this run proves it twice
  (`:521`, `:526`/`:549`). So `#12673` is reachable with **no new op**: `OpOwnerChain_v1(12673)` → its owning
  Case Structure → walk that node's `Terms[]` → take the entry named `Q_focusback` **by name, never a carried
  index** (the T2c2 failure) → `OpConnectFromWire_v0` with source = the **live** net **23963**, not the
  original 9113 the inventory names. The `FlatSequenceFrame` silent-termination hazard and the
  `Outside Terminal` fallback are carried into the plan as written, including the instruction to read that
  property's short name off the machine rather than from the wiki.
- **Not accepted as blocking, and not disputed:** the wire-identity-drift warning (`toolkit-capabilities.md:68`)
  is already standing project doctrine and needed no change here.
