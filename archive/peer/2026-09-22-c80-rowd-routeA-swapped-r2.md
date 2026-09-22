# c80-rowd-routeA-swapped-r2

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $4.3451  in 24 / out 49666 / cache-create 204608 / cache-read 2053739  (685s, 18 turn(s))
- **date:** 2026-09-22 11:13:31
- **outcome:** ANSWERED (689s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# REFUTE THIS: "Route A - `OpConnectFromWire_v0` with the roles SWAPPED - cannot write Row D, in EITHER ordering"

You are the failed-prediction reviewer. A prediction of ours failed; the explanation we formed under
pressure is below. **Attack it.** Find the cheapest route we have MISSED, or show the claim is wrong.
Do not confirm. The failing log is `tools/bench/c80_rowd_routeA.log`; the script is
`tools/recipes/build_d1_m3a3.py`.

## The situation, in one paragraph

We are restructuring a LabVIEW VI by VI Scripting over COM (behaviour-preserving refactor: scheduling may
change, computation may not). One wire ("Row D", uid **7506**) carries a VISA session handle out of the
OLD `WhileLoop #637` / `RightShiftRegister #4334` and must instead come out of the NEW `WhileLoop #23032`
/ `RightShiftRegister #23868`. The SINK is `FlatSequenceInnerTunnel #7468`'s **LeftTerm, terminal uid
#7488**, which is in no `Nodes[]` (a `FlatSequence` is `Generic -> GObject -> FlatSequence`, measured, and
your predecessor could not break that). The SOURCE is the NEW loop's border terminal, addressable as
`Diagram` traverse index **19**, `Nodes[21]`, `Terminals[1]`, name `'Outgoing Handle'`, `Is Source?` True,
BARE.

Your predecessor's review (`archive/peer/2026-09-22-c79-rowd-writer.md`, ANSWERED) showed that our
"`Terminal.Connect Wire` 6349C03 is invoked ON THE SINK" rule is an ADOPTED CONVENTION, not a
measurement, and proposed **the swapped call**: give `OpConnectFromWire_v0`'s already-uid-addressed
SOURCE half (`wire_uid` + a `Wire.Terms[]` index, property 6371003) the FSIT TERMINAL #7488 - the true
SINK - and give its `(diagram, Nodes[], Terminals[])` triple the NEW loop's BARE border terminal - the
true SOURCE - so the Invoke sits on the BARE terminal and receives #7488 as `Wire Source`. WE RAN THAT
TEST, both orderings, each on its own dated scratch copy of the bed. Both failed.

## What the machine returned, VERBATIM (`tools/bench/c80_rowd_routeA.log`)

Both arms first measured the source half identically and correctly (`:93-98`, `:229-234`):
`OpWireSource_v5(UID 2 = 7506)` -> `t0 is_source=True owner_class='RightShiftRegister' owner_uid=4334`,
`t1 is_source=False owner_class='FlatSequenceInnerTunnel' owner_uid=7468`, plus one all-zero padding row.
So `Wire.Terms[]` index **1** is the FSIT terminal, PD85 violations 0. The invoke triple resolved live as
`[19, 21, 1]`, BARE, as predicted.

**ARM A1 - DELETE first, then the swapped call** (`:102`, `:119`). The delete succeeded
(`{'index': 821, 'gone': [7506]}`); #7488 then read wire 0 / BARE. The swapped call then returned:
`wire_delta 0`, `exec_state 0`, `op_error_verbatim ""`, and in the op's own sub-returns
`err_uidvi ''`, **`err_wirepn 'error 1055: Property Node in OpConnectFromWire_v0.vi'`**, `UID 2` **0**,
`Is Broken? False`, `Name ''`. #7488 stayed BARE after the write and after the junk purge.

**ARM A2 - the swapped call while wire 7506 is ALIVE, then delete** (`:237`, `:239`). The call returned
`wire_delta 0`, `exec_state 0`, `op_error_verbatim ""`, `err_uidvi ''`, `err_wirepn ''`, and in its own
ORDERED readback (the op's gate W7b orders `Wire.Is Broken?` 6371004 AFTER the write):
**`UID 2` = 7506**, **`Name` = 'Outgoing Handle'**, **`Is Broken?` = True**. `wire_delta` 0, i.e. NO NEW
`Wire` OBJECT. We then deleted 7506 (it reported success), after which #7488 read wire 0 / BARE.

**Step 4, FACT-ONLY** (`:289-290`): handing the op the TERMINAL uid **7488** in its uid slot with the
index triple deliberately out of range returned `err_uidvi ''` (EMPTY) and
`err_wirepn 'error 1055: Property Node'`.

## The conclusion we drew, which you must attack

> (1) Route A is DEAD in both orderings. A1 dies because the op's source half reads `Wire.Terms[]` on the
> `wire_uid` it is given, and after the delete that uid is not a live `Wire`, so the property node raises
> 1055 and nothing is written. A2 dies because, with the wire alive, the swapped call does not CREATE a
> wire at all: `wire_delta` 0 and the op's own readback naming `UID 2` = **7506** (the pre-existing wire)
> with `Is Broken?` **True** mean it BRANCHED / extended the existing net - precisely the silent-branch
> failure mode your predecessor predicted - giving a net with TWO sources (`#4334` and the new loop
> border) which LabVIEW marks broken; deleting 7506 then removes the whole net and leaves both ends bare.
> (2) Therefore Pre-decided 116-A ("if A works, Row D proceeds on it and nothing new is built") is
> REFUTED by measurement, and Row D needs Route B: `OpConnectByUid` (uid -> `UID to GObject
> Reference.vi` -> TMSC on a **Terminal** seed -> the Invoke's `reference`), donor `OpConnectNested_v2`.
> (3) Separately: `err_uidvi` came back EMPTY on a *deleted* wire uid in A1 AND on the terminal uid in
> step 4, so "empty `err_uidvi`" does NOT establish that a uid resolved, and step 4 therefore does NOT
> clear Route B's first gate. Route B's uid-resolution assumption is still UNMEASURED.

## ALREADY RULED OUT - do not propose these

(a) A `Nodes[]`/index address for #7468 or #7488 - measured impossible (CLASS, not owner: 173/173
    diagrams, 635 nodes, `find_node` misses all three FlatSequences).
(b) An owner walk from the tunnel upward - `OpOwnerChain_v1` terminates SILENTLY at a
    `FlatSequenceFrame` (error 1055, `owner_uid` 0, empty cast echo; `docs/toolkit-capabilities.md:61`).
(c) A GUI fallback (clicking the wire) - forbidden for this work by a standing project decision.
(d) Re-pointing Row D at a different sink, or inserting/moving any structure, tunnel, Local or shift
    register - a STRUCTURAL change of the original's computation, refused by our rule 1a.
(e) `Tunnel.Inside Terminals[]` 6356000 / `Tunnel.Outside Terminal` 6356001 - DEAD BY CITATION, a
    `FlatSequenceInnerTunnel` is not a `Tunnel`; its properties are `Left Terminal` 1C3A9000 /
    `Right Terminal` 1C3A9001. `Node.Connect Wires` needs both ends to be `Node`s; `Create Described
    Wire` is itself a `Terminal` method.

## The questions, answer ALL of them explicitly

1. **Is our reading of ARM A2 right?** Does `UID 2` = the OLD wire uid + `Name` = 'Outgoing Handle' +
   `Is Broken?` True + `wire_delta` 0 really mean "branched the existing net and broke it"? Name at
   least one ALTERNATIVE reading of those four values (e.g. the readback reporting a stale/cached
   object, or `Connect Wire` having silently declined and the readback describing the wire it was
   merely *shown*), and say which reading the cheapest measurement would separate.
2. **Is there any ordering or parameterisation of the SWAPPED call that still works?** e.g. deleting
   only part of the net first; passing `Wire.Terms[]` index 0 (the `#4334` source row) instead of 1;
   invoking on the FSIT side with the BARE loop terminal as `Wire Source` (the ORIGINAL role
   assignment, which we have NEVER run because we had no uid-addressed sink - but the op's triple can
   address the loop border, and its uid half can address... only a wire). Say concretely why each does
   or does not work.
3. **Route B's first gate, now that step 4 is inconclusive:** what is the cheapest READ that actually
   establishes whether `UID to GObject Reference.vi` resolves a TERMINAL uid (#7488) as opposed to a
   tunnel or wire uid? Name the op and the exact indicator to read, and why that indicator is sound
   where `err_uidvi` is not.
4. **Is Route B even the smallest remaining shape?** If not, name what is.

## Output contract

In this order and nothing else:
- **STRONGEST REASON THE CONCLUSION IS WRONG** (one paragraph).
- **ALTERNATIVE EXPLANATION / ALTERNATIVE ROUTE** - concrete, or "none found, and here is the search I ran".
- **WHAT WOULD FALSIFY** the claim that Route A is dead in both orderings.
- **CHEAPEST DISCRIMINATING TEST** - read-only or scratch-copy, naming the exact op, inputs and the one
  indicator to read, settling it in under ~2 minutes.
- **VERDICT**: `ROUTE-A-ALIVE: <the exact call>` or `ROUTE-A-DEAD: <the smallest next shape>`.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

No write tools in this read-only reviewer role, so the review is the deliverable.

---

## STRONGEST REASON THE CONCLUSION IS WRONG

Your A2 reading inverts what the op's own readback measures. `UID 2` / `Is Broken?` / `Name` are **not** a return value of `Connect Wire` — your own recipe records that "`Terminal.Connect Wire` returns nothing" (`tools/recipes/build_opconnectfromwire_v0.py:44`), and labviewwiki confirms it ([Connect Wire method](https://labviewwiki.org/wiki/Terminal_class/Connect_Wire_method): inputs `Wire Source` (GObject refnum), `Auto Wire? (T)`, `Wiring Specs`, `Auto Route? (F)`; **no return value**; "Connects a wire to the terminal", with *no* statement about which end it is invoked on). What those three indicators actually are is written down twice: `build_opconnectfromwire_v0.py:51-57` — "node **#242** reads `UID` + `Broken?` off node **#241**'s `Wire` output, and **#241's `reference` is w572 — the SINK terminal itself**" — and `docs/NAMES.md:975-976`, "a property node reads `Wire` off the SINK terminal reference, and a second reads that wire's `UID` + `Broken?`… surfaced as `UID 2` \ `Is Broken?`"; gate **W7b** is what orders that read *after* the Invoke. In the op's vocabulary the "sink terminal" is the index-triple terminal — i.e. **the terminal the Invoke sits on**, which in the swapped call is the NEW loop's border terminal, measured **BARE, wire 0**, nine lines before the call (`c80_rowd_routeA.log:227-228`). It came back reading **wire 7506**, with `op_error_verbatim ""`. That is not "no wire was created" and it is not a return-value echo: it is the machine joining exactly the two terminals it was handed, in the swapped role assignment, direction ignored. So the convention is refuted on the machine as well as in the wiki, **Route A's verb works**, and what actually failed is the *residue* — `#4334` was still on the net, so the net had two sources, hence `Is Broken? True` and `exec_state 0`. "Route A is DEAD in both orderings" does not follow from that; "Route A connects but leaves the old source attached" does.

## ALTERNATIVE EXPLANATION / ALTERNATIVE ROUTE

**Alternative reading of the same four values (Q1).** #241's `reference` may in fact be the `Wire.Terms[]`-derived terminal (#7488) rather than the Invoke's own — the recipe's word "sink" is the op's *role name*, and under the swap the physical roles were exchanged. Then `UID 2 = 7506` is trivially the wire #7488 already carried, `Name` is that wire's label, `Is Broken?` is that wire's state, and **A2 measured nothing whatever about the connect**. Your third candidate (a stale/cached read) is excluded: a pre-write read of the Invoke terminal would have returned 0/False/'' exactly as A1 did. So there are two live readings, and **both refute your conclusion** — under mine Route A connected; under the other A2 is uninformative. Neither supports "dead". The reason no third possibility is decidable from this log is structural: **arm A2 destroyed the evidence before reading it.** Every read of #7488 and of the loop border in A2 happens *after* the delete (`:240-247`, `:276-285`), and the c79 review's own step 3 — `OpWireSource_v5` on the post-connect net (`archive/peer/2026-09-22-c79-rowd-writer.md:172`) — was never run. That is an instrumentation failure, not a route failure.

**Q2 — orderings and parameterisations of the swapped call, each concretely:**

- **Index 0 instead of 1** — useless. It hands the OLD source terminal (`RightShiftRegister #4334`) as `Wire Source` to an Invoke on the loop border, i.e. wires the new loop's output *from* the old register, and never touches #7488.
- **"Delete only part of the net first"** — this is `Wire.Disconnect Terminal` **6370C0D**, which `docs/NAMES.md:1035` calls "the per-sink primitive, if ever needed". ⚠️ **External evidence is against it, and this corrects two of your docs**: labviewwiki's [Wire class](https://labviewwiki.org/wiki/Wire_class) lists `Disconnect Terminal` among Wire's methods **marked "(Not Implemented)"**, and there is no method page for it; `Terminals[]` is confirmed **read-only**, so no write-side re-point exists either. `docs/NAMES.md:1035` and `docs/cycle27-plan.md:2468` should be annotated — the second already says "body text unverified". Treat 6370C0D as a one-call probe, never as a plan.
- **"Invoke on the FSIT side with the BARE loop terminal as `Wire Source`" — your brief says "its uid half can address… only a wire", and that is the error.** The uid half's *output* is a **Terminal** reference — it has to be, because it feeds `Wire Source`, which takes a GObject/Terminal refnum. `OpConnectFromWire_v0` therefore *already holds a live, uid-derived Terminal reference to #7488*; it is merely wired to the wrong input of the Invoke. **This is the untested cell of the 2×2** — exchange, inside a copy of the op, which of the two Terminal refs goes to the Invoke's `reference` and which goes to `Wire Source`. Both are Terminal refs, so it is type-legal: no new ladder, no new seed, no new cast, no `UID to GObject Reference.vi` on a terminal uid. Call it `OpConnectFromWire_v1`. Its one real hazard is that #7488 is then an already-wired **sink**, and `tools/gscript.py:2521-2523` / `docs/NAMES.md:245-246` say "LabVIEW re-routes and the VI breaks" — but that was measured once, in 2026-09-06, on a fresh Index Array, and **"re-routes" is exactly Row D's desired end state** here, where a bare `#4334` outer terminal is explicitly legal (Pre-decided 69, `c80_rowd_routeA.log:106`, `:243`). One scratch run settles it.
- **Untested inputs.** The fleet sets only `Wire Source`; `Auto Wire?` defaults **TRUE** and `Auto Route?` FALSE ([wiki](https://labviewwiki.org/wiki/Terminal_class/Connect_Wire_method)). If A2 did join the existing net, `Auto Wire? = FALSE` is the one parameter that plausibly changes that behaviour, and no op in the fleet has ever set it.

**Q3 — the cheapest sound READ for Route B's first gate.** `err_uidvi` is unsound for the reason you gave (A1 proves it is empty on a *dead* wire uid), and step 4 was worse than inconclusive: it was **uninformative by construction**, because its triple was deliberately `[9999,9999,9999]`, so the only downstream indicator (`err_wirepn` / `UID 2`) was *guaranteed* to fail whatever uid 7488 resolved to. The sound reader already exists: **`OpOwnerChain_v1`** (`tools/recipes/build_opownerchain_v1.py`, 20/20, functional read-only on the main VI) — it is `UID to GObject Reference.vi` (node **990**) → node **241**'s property read → ClassName/UID, i.e. `OpWireSource_v5` with the Wire cast removed. Run it with `uid_in = 7488` and read the **self echo**, `Class Name 3` / `cast_class` (and the self UID): `'Terminal'` + 7488 ⇒ resolved; `POISON` still standing, or an empty cast echo with `owner_uid 0` and 1055, ⇒ not resolved. It is sound where `err_uidvi` is not because it reports a property read taken **through** the resolved reference, and `read_owner()` **poisons every answer indicator before the run** (`build_opownerchain_v1.py:249-253`), so a read that never happened cannot be mistaken for an answer. The known FlatSequenceFrame limit (`docs/toolkit-capabilities.md:61`) does not bite: #7488's owner is the FSIT #7468, not a frame — and the self echo, not the owner, is the indicator.

**Q4 — Route B is not the smallest remaining shape, and your own point (3) says so.** You simultaneously conclude that Route B's uid-resolution gate is UNMEASURED and that Row D should go to Route B. Meanwhile the shape whose sink resolution is **measured five times in this very log** was withdrawn: `OpFsInnerTunnelTerm_v0` resolves #7468 → `Left Terminal` **1C3A9000** → terminal **#7488** with every error column empty, *including after wire 7506 has been deleted* (`:104`, `:141`, `:148`, `:265`) — a wire-independent sink address, which is precisely what A1 lacked. Built **additively on `OpConnectFromWire_v0`** (swap the Wire-typed head for the FSIT-typed head and seed that already exist in `OpFsInnerTunnelTerm_v0`, then the same two-wire exchange at the Invoke), candidate C is smaller in *risk* than Route B even if larger in parts, and the c79 objection to it (wrong donor `OpStopFromNode_v0`) evaporates because that donor is not used. Ranking: **A′ (two-wire swap) → A″ (A′ or the swapped call plus a residue-removal probe) → C′ (FSIT head) → B**. One more address nobody has costed: `Terminal` is a **valid traverse class with 5763 members** (`docs/toolkit-capabilities.md:285-286`), so a `Traverse('Terminal')[i]` sink ladder exists in principle — your ruled-out (a) forbids `Nodes[]`, not a GObject traverse. It still needs a Terminal-typed TMSC (the GObject→Terminal downcast is the measured `ExecState 0` trap, `:69`), and 5763 indices are fragile, so it is a fallback, not a lead.

## WHAT WOULD FALSIFY

"Route A is dead in both orderings" dies the moment a post-connect, **pre-delete** `OpWireSource_v5(UID 2 = 7506)` returns **three** real-owner rows — `#4334` (source), `#7468` (sink), and a third owned by the NEW loop `#23032` — or `node_terms(19, 21)` shows t1 `'Outgoing Handle'` carrying wire **7506** instead of 0. Either reading means the swapped call performed the connection and the whole failure is the un-removed old source. The claim *survives* if both reads come back unchanged from `:229-234` / `:227` (two rows, t1 bare) — then `UID 2` was an echo of the wire half, A2 did nothing, and A′ becomes the only live Route-A shape. It is further supported, though not proved, if A′ (the two-wire swap, invoke on #7488) returns a direction error or leaves #7488 wired to `#4334`.

## CHEAPEST DISCRIMINATING TEST

One fresh dated scratch copy of the bed, the A2 arm re-run verbatim with **two read-only insertions and the delete suppressed** — no new op, no build, the bed never opened:

1. `connect_from_wire(SCRATCH, wire_uid=7506, term_index=1, sink_diag=19, sink_node=21, sink_term=1)` — the identical A2 call (`build_opconnectfromwire_v0.py:381`).
2. **Immediately, before any delete:** `wire_source_owner(SCRATCH, 7506)` (`OpWireSource_v5`, `UID 2 = 7506`). **The one indicator: the count of rows with `Is Source? True`.** 2 ⇒ the connect joined the net, Route A's verb works, Row D reduces to removing `#4334`. 1 ⇒ nothing happened, `UID 2` was an echo, A2 was void.
3. Free, same run: `node_terms(SCRATCH, 19, 21)` → t1's wire uid (7506 vs 0), the terminal-side view of the same fact.
4. Free, same run, and it settles Q3 properly: `OpOwnerChain_v1` with `uid_in = 7488` → read `Class Name 3` / the self UID echo.

≈60 s of LabVIEW time; steps 2 and 3 are reads the run already performs, moved earlier by two lines in `tools/recipes/build_d1_m3a3.py`.

## VERDICT

**`ROUTE-A-ALIVE: connect_from_wire(bed_scratch, wire_uid=7506, term_index=1, sink_diag=19, sink_node=21, sink_term=1)` — the A2 call itself, re-read before the delete.** On the documented meaning of the op's readback it already connected the new loop's border terminal to net 7506 and only left `#4334` attached, so Route A was never shown dead; if step 2 says otherwise, the smallest next shape is **not** Route B but **`OpConnectFromWire_v1` — a copy of `OpConnectFromWire_v0` with the two Terminal references exchanged at the Invoke (wire-derived #7488 → `reference`; index triple → `Wire Source`)**, the untested cell of the 2×2 and a two-wire edit, with `OpFsInnerTunnelConnect_v0` built on `OpFsInnerTunnelTerm_v0`'s measured `Left Terminal` 1C3A9000 head as the fallback. Pre-decided 116-A is **not** refuted by this run. What would change my mind: step 2 returning one source row *and* A′ returning a direction error from `Connect Wire`.

**Sources:** [Terminal class/Connect Wire method — LabVIEW Wiki](https://labviewwiki.org/wiki/Terminal_class/Connect_Wire_method) · [Wire class — LabVIEW Wiki](https://labviewwiki.org/wiki/Wire_class) · [Wire class/Remove Probe method — LabVIEW Wiki](https://labviewwiki.org/wiki/Wire_class/Remove_Probe_method) · [Node class/Connect Wires method — LabVIEW Wiki](https://labviewwiki.org/wiki/Node_class/Connect_Wires_method) · [Disconnect wire through VI scripting — NI Community](https://forums.ni.com/t5/LabVIEW/Disconnect-wire-through-VI-scripting/td-p/3046807) · [Category:VI Scripting Method — LabVIEW Wiki](https://www.labviewwiki.org/wiki/Category:VI_Scripting_Method)

## Sources

(extract from answer)

## What was done with it

**CLASSIFIED: ANSWERED, ACCEPTED ON ITS CENTRAL POINT — the review's own cheapest discriminating test was
BUILT AND RUN IN THE SAME DISPATCH, and no op was built.** This is the mandatory failed-prediction review
of `tools/bench/c80_rowd_routeA.log` (47 pass / 5 fail), where both orderings of Pre-decided 116-A's
swapped call left the sink terminal #7488 BARE. The explanation this session had formed — *"Route A is
dead in both orderings; go to Route B"* — is **not** accepted. A first dispatch of this same review
(`archive/peer/2026-09-22-c80-rowd-routeA-swapped.md`) ended **TIMEOUT (780 s)** and therefore told us
nothing (CLAUDE.md §5); it was re-dispatched with a 28-minute budget and ANSWERED in 689 s.

What is ACCEPTED, and acted on:

- **Arm A2 destroyed its own evidence.** Every read of #7488 and of the loop border in A2 happened AFTER
  the delete (`c80_rowd_routeA.log:240-247`, `:276-285`), and the c79 review's step 3 — `OpWireSource_v5`
  on the POST-CONNECT net — was never run. The review calls this an instrumentation failure rather than a
  route failure, and that is correct: `UID 2` / `Name` / `Is Broken?` are **not** a return value of
  `Terminal.Connect Wire` (it returns nothing — `build_opconnectfromwire_v0.py:44`, and the wiki page
  confirms it), they are a property read taken off ONE of the two terminal references, so on this log
  alone there are two live readings and neither supports "dead".
- **ACTED ON, in `tools/recipes/build_d1_m3a3.py`:** arm A2 now performs, BETWEEN the connect and the
  delete, (step 2) `OpWireSource_v5` on the net the sink terminal carries, with the review's ONE indicator
  — **the count of `Is Source? True` rows** — printed as its own gate line, and (step 3) the loop border's
  full terminal table, which is the same fact from the terminal side. The delete still follows, because
  every decisive read now precedes it and the post-delete state was already measured in run 1.
- **`Wire.Disconnect Terminal` 6370C0D is marked "(Not Implemented)" on labviewwiki, and `Terminals[]` is
  read-only.** This CORRECTS two of our own documents — `docs/NAMES.md:1035` calls 6370C0D "the per-sink
  primitive, if ever needed" and `docs/cycle27-plan.md:2468` carries it — and it matters because
  "remove only the OLD source from the joined net" is exactly the step Route A would still need.
- **The c79 review's "step 4" probe is UNSOUND and is now removed from the recipe.** Measured: `err_uidvi`
  came back EMPTY for a DELETED wire uid too (`:119`), so empty never meant "resolved"; and the probe is
  uninformative by construction because its out-of-range triple guarantees the downstream indicator fails.
  Its sound replacement is `OpOwnerChain_v1` on `uid_in = 7488`, read on the SELF echo — **not run**: it
  needs a labels map that is not on disk and a `read_owner()` whose target is hard-coded to the MAIN VI.
- **Recorded as findings, NOT acted on (they are design decisions):** the untested cell of the 2x2 —
  `OpConnectFromWire_v1`, a copy of `OpConnectFromWire_v0` with the two Terminal references EXCHANGED at
  the Invoke (the wire-derived #7488 to `reference`, the index triple to `Wire Source`), which the review
  argues is a two-wire edit needing no new ladder, seed or cast; `Auto Wire?` (default TRUE) never having
  been set by any op in the fleet; the `Traverse('Terminal')` sink ladder (5,763 members); and the
  review's ranking **A' -> A'' -> C' (an FSIT-head op on the measured `Left Terminal` 1C3A9000) -> B**,
  i.e. Route B is NOT the smallest remaining shape. Building any of them is a NEW OP and a design
  decision — the judgement session's, not a material session's (CLAUDE.md §3).
- **Pre-decided 116-A is NOT refuted by run 1**, per this review. Whether it survives is decided by the
  indicator this dispatch then measured; see the run-2 log and the material report.

JEV-DISCHARGE: c80_rowd_routeA_r2.log (2026-09-22 11:24:45, p=0.800)
  This failing run was released without a NEW peer review: Jev judged, at the probability shown, that the failure above is the one this review already attacks (tools/bench/jev_gate.py, docs/jev-integration-plan.md row #1). The review itself is the evidence; this line only records which failure was charged to it.

JEV-DISCHARGE: c80_rowd_routeA_r2.log (2026-09-22 11:43:40, p=0.800)
  This failing run was released without a NEW peer review: Jev judged, at the probability shown, that the failure above is the one this review already attacks (tools/bench/jev_gate.py, docs/jev-integration-plan.md row #1). The review itself is the evidence; this line only records which failure was charged to it.
