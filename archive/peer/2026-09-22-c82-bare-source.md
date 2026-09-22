# c82-bare-source

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $2.7640  in 22 / out 32090 / cache-create 120014 / cache-read 1205047  (420s, 25 turn(s))
- **date:** 2026-09-22 12:46:56
- **outcome:** ANSWERED (423s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# FAILED PREDICTION — `Terminal.Connect Wire` 6349C03 is a SILENT NO-OP when its `Wire Source` terminal is BARE

Log: `tools/bench/build_opfsinnertunnelconnect_v0.log` (45 gates pass / 2 fail, `BGRUN END rc=1 after 324s`).
The two failing lines are the same gate, G4f, plus its STOP echo.

## What was predicted, and by whom

`docs/cycle27-plan.md` Pre-decided 127 (the judgement session's design for D-2) predicted that a new op
`OpFsInnerTunnelConnect_v0.vi` — built as the smallest edit of `OpConnectFromWire_v0.vi`, with ONLY the
source-half acquisition changed from (`wire_uid`, `Wire.Terms[]` index) to
(`fsit_uid` → `UID to GObject Reference.vi` → TMSC `FlatSequenceInnerTunnel` → `LeftTerm` 1C3A9000) —
would, on a scratch copy of the bed, after wire **7506** is deleted, connect the FSIT LeftTerm **#7488**
into the NEW loop's shift-register OUTER terminal (`WhileLoop #23032`, `Nodes[21]`, `Terminals[1]`,
'Outgoing Handle'), so that the border terminal would go from wire 0 to a non-zero wire.

That prediction rested on `tools/bench/c80_rowd_routeA_r2.log:244`, where the SAME Invoke binding (the
Invoke on the border terminal, the FSIT terminal handed to `Wire Source`) DID make the border terminal go
BARE → wire 7506 — but there the source terminal #7488 was still carrying wire 7506.

## What was observed

The op was built and saved and is legal:

* `ExecState` 1 on the saved op, md5 `c0d5efe3389b0dea388ee565433fb683`, 17,881 B (`:78-84`).
* Both uid echoes are correct on EVERY call, with every error column empty: the resolver's own
  `uid_back` = **7468** (the uid passed in) and the LeftTerm's own uid `term_uid` = **7488**
  (`:92-93`, `:323`, `:325-326`).

**Arm 1 — wire 7506 ALIVE** (the 20-call handle scratch, bed unmodified, `:92-93`):
every one of the 20 calls returned `sink_wire=7506`, `is_broken=True`, `err=''`. So the border terminal
WAS attached, to the existing net, which then has multiple sources — the same branch behaviour
`c80_rowd_routeA_r2.log:253-261` measured. The verb fires. It also mints exactly **1.00 stray `Invoke`
node per call** in the target (`:97-99`, purged).

**Arm 2 — wire 7506 DELETED, both ends bare** (the exercise scratch, `:315-342`):

```
G4 Diagram[19].Nodes[21] uid echo 23032 (MATCH); t1 'Outgoing Handle' is_source=True wire=0
G4 deleted wire w7506 ; border t1 wire=0 (BARE)   <- PASS G4c
G4 CALL RETURN: {"err": "", "err_uidvi": "", "err_fsit": "", "err_termuid": "", "err_uidback": "",
                 "term_uid": 7488, "uid_back": 7468, "sink_wire_uid": 0, "is_broken": false,
                 "UID": 23032, "Name": "", "wire_delta": 0}
G4 AFTER the connect: border t1 wire=0 ; the op's own `UID 2` = 0 ; wire_delta 0
**FAIL** G4f the border terminal went BARE -> NON-ZERO   wire 0
```

No error, anywhere: the op's `error out`, and the per-stage indicators for the UID-to-GObject subVI, the
FSIT property node, the LeftTerm-UID node and the resolver-UID node, are ALL empty strings. One junk
`Invoke` was still minted (`:328`), so the Invoke node DID execute.

## The hypothesis you are asked to REFUTE

**`Terminal.Connect Wire` 6349C03 silently declines when the terminal handed to `Wire Source` carries no
wire.** On this reading the method does not create a wire between two bare terminals at all; what it does
is attach the Invoke's own terminal to the NET the `Wire Source` terminal already belongs to — which is
why arm 1 works (and branches) and arm 2 does nothing. If that is right, delete-THEN-connect cannot work
with this method no matter which op resolves the source terminal, and the whole Route-A family is bounded
by it.

## Already ruled out — do not re-derive these

1. **Not an addressing error.** The sink address was resolved LIVE with a node-uid echo (`23032` MATCH),
   the terminal name read back as `'Outgoing Handle'`, and gate G4c asserted `wire == 0` immediately
   before the call. The op's `UID` indicator echoed `23032` back out of the call.
2. **Not a source-resolution error.** On the SAME call, after the delete, `uid_back` = 7468 and
   `term_uid` = 7488 with every error column empty — so the `FlatSequenceInnerTunnel #7468` LeftTerm
   reference WAS obtained from a BARE tunnel terminal. (Independently consistent with
   `c80_rowd_routeA_r2.log:104,265`.)
3. **Not a stale/history echo.** Every readout (`uid_back`, `term_uid`, `UID 2`, `Is Broken?`) is poisoned
   before each run, `Is Broken?` to True, per Pre-decided 125.
4. **Not the "already-wired sink" hazard** (`tools/gscript.py:2522-2523`): the sink read wire 0.
5. **Not an op defect that breaks the VI**: `ExecState` 1, auto error handling OFF, 20/20 calls in arm 1
   returned the intended values, handle count +94 over 20 calls, private-bytes drift 0.03 MB, refs 22/22/0.

## What we want from you

1. The strongest reason the hypothesis above is WRONG.
2. An alternative explanation of arm 2's silent no-op that arm 1 does not already refute.
3. What would FALSIFY the hypothesis — stated as an observation, not an argument.
4. The CHEAPEST discriminating test, runnable on a dated scratch copy of a VI with the ops already on
   disk. Name the exact ops/inputs. Note that `tools/gscript.py` already has `connect_terminals`
   (6349C03 on two NODE-INDEX-addressed terminals) and `wire()` (the erdosmiller name-based route), so a
   test that decides whether 6349C03 EVER wires two bare terminals — on a trivial scratch VI, away from
   the bed — is available at near-zero cost.
5. If the hypothesis survives: is there a documented NI verb that creates a wire between two bare
   terminals given one of them only as a reference? (`Create Described Wire` and `Node.Connect Wires`
   were both examined on 2026-09-22 and are recorded as not fitting — say if that record is wrong.)

Answer with citations. A claim about LabVIEW's own semantics needs a source; a claim about OUR tools needs
a `file:line`.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

## 1. The single strongest reason the claim is WRONG

**This project has already recorded `Terminal.Connect Wire` 6349C03 creating a brand-new wire between two bare terminals.**

`tools/bench/build_harness_copyloop2.log:31-40`:

- `:33-34` a fresh empty For loop, its count terminal read `(0, '', False, 0)` — name `''`, `is_source=False`, **wire 0, BARE**.
- The source, `IMAQ GetImageSize` 'Y Resolution', was an output of a node dropped two steps earlier (`:24`); the only terminal wired on it was 'Image' (`:27-29`), and that step left the wire census at **9**, unchanged — a branch.
- `:37-40` `connect_terminals` (= `OpConnect_v0` = 6349C03, `tools/gscript.py:2518-2520`): **`Wire=9 → 10`**, `N check: loop terminal 0 wire 346, 'Y Resolution' wire 346`, `ExecState 0 → 1`.

A wire-count **+1** is by itself proof this was a creation and not a join: `tools/gscript.py:2521-2522` records the measured branch semantics — "an already-wired source is BRANCHED (wire count unchanged)". Count +1 ⇒ not a branch ⇒ the source was bare ⇒ **the method created a wire from a bare `Wire Source`.** The same shape appears again at `tools/recipes/build_opqueue.py:127,137` (creator `error out` → subVI input, predicted and gated as wire delta 1).

So "6349C03 silently declines when the `Wire Source` terminal carries no wire" is false as a property of the method. Whatever happened in arm 2 is specific to arm 2 — and the experiment cannot tell you what, because **arm 1 and arm 2 differ in three ways at once**, not one:

| | arm 1 | arm 2 |
|---|---|---|
| source terminal | wired | bare |
| operation required of LabVIEW | **join** an existing net | **create** a new wire |
| must LabVIEW determine a source/sink polarity? | **no** | **yes** |

The brief's hypothesis picks the first row. Rows two and three are equally consistent with the data, and row three is the one with independent evidence.

## 2. The alternative explanation arm 1 does not refute

**(a) Primary: the call asks for a wire that cannot legally exist — the roles are inverted.**

Measured on the bed, before any mutation:

- `Wire Source` = FSIT `LeftTerm` **#7488**, `is_source=**False**` — the true **SINK** of wire 7506 (`tools/bench/c80_rowd_routeA_r2.log:75`, `:95`, `:98`).
- The Invoke's own terminal = loop `#23032` `Terminals[1]` 'Outgoing Handle', `is_source=**True**`, BARE (`:91`, `:92`).

So the call says: *create a wire whose "original source" is this sink, and attach it to me, a source.* The method's required parameter is documented as **"Wire Source — The original source of the wire"** ([labviewwiki, Terminal class/Connect Wire method](https://labviewwiki.org/wiki/Terminal_class/Connect_Wire_method)). On a **create**, LabVIEW has to resolve a source; there isn't one — there are two sources and no sink. On a **join**, it never asks: it attaches the invoked terminal to the existing net, which is why arm 1 "worked" **and produced a broken 3-source net** — `[('RightShiftRegister', 23868), ('FlatSequenceInnerTunnel', 7468), ('RightShiftRegister', 4334)]`, `Is Broken? True`, `ExecState 0` (`c80_rowd_routeA_r2.log:259-261`, `:237`).

Arm 1 therefore cannot refute this: arm 1 never exercised source determination. And note what follows for the plan — **Pre-decided 119 (`docs/cycle27-plan.md:3467`) over-generalises**: what `:244` proved is that the roles may be exchanged *when joining an existing wire*, which is a different operation from creating one. Pre-decided 115's own warning ("a convention adopted from a wiki is evidence of how WE have written ops") cuts both ways here.

Critically, the copyloop2 counterexample is **polarity-correct** (node output → loop count input) — so it is evidence *for* this alternative, not just against the claim.

**(b) Second alternative: `Auto Route?` defaults to FALSE and no op in the fleet wires it.** The parameter list is `Wire Source` (req), `Auto Wire?`, `Wiring Specs`, `Auto Route?` ([labviewwiki](https://labviewwiki.org/wiki/Terminal_class/Connect_Wire_method); your own `docs/keystone-op-spec.md:354` records `Auto Route? (F)`). A join needs a short stub; a fresh wire from a flat-sequence inner tunnel to a While-loop border terminal on a 1,920-wire diagram needs a path. `tools/recipes/build_opfsinnertunnelconnect_v0.py` never mentions `Auto Route` — it is at default FALSE.

**(c) Third: "no error anywhere" may be unmeasured rather than measured.** The recipe wires indicators on the **three new** stages' `error out` (`build_opfsinnertunnelconnect_v0.py:542-552`) — the UID-to-GObject subVI, the FSIT property node, the LeftTerm node. Nothing in the log demonstrates that the **Invoke's own `error out`** reaches the op's `error out`, and auto error handling is OFF. This lineage has exactly this defect on record (`docs/NAMES.md:978`: an unwired `error in (no error)` that made a readback report the *old* wire). Until that one wire is shown to exist, "silent" is not established — only "quiet". Externally, the one NI-employee-answered thread on this exact situation reports the opposite behaviour: *"scripting `ConnectWire` on a loose terminal produces an error"* ([NI Forums 4195933](https://forums.ni.com/t5/LabVIEW/Script-connect-existing-loose-wires-to-case-tunnels/td-p/4195933)).

Where the evidence does not settle the question: **the log cannot distinguish (a), (b) and (c)**, because bareness, join-vs-create and polarity all changed together and the error path is unverified.

## 3. What would FALSIFY the claim — stated as an observation

> On any VI, a 6349C03 call whose `Wire Source` terminal reads wire 0 ends with **wire census +1** and the **same new wire uid on both terminals**.

That observation is already in your own bench directory (`build_harness_copyloop2.log:39-40`), so on the record the claim is falsified today; what is still open is the arm-2 cause.

The falsifier for **my** alternative (a): a call where the `Wire Source` terminal reads `is_source=False` and both ends are bare, which nevertheless produces wire census +1.

## 4. The cheapest discriminating test

A 2×2 on a **trivial scratch VI**, no new op, no bed, ~2 minutes, using only `gscript.connect_terminals` (`tools/gscript.py:2518`) — the copyloop2 shape from `tools/recipes/build_harness_copyloop2.py:133-134`. Drop two subVI nodes with unwired terminals on one top-level diagram and run four calls, reading the wire census before/after each:

| | invoke on | `Wire Source` | claim predicts | alternative (a) predicts |
|---|---|---|---|---|
| **T1** | bare **input** | bare **output** | 0 | **+1** |
| **T2** | bare **output** | bare **output** | 0 | **0** |
| **T3** | bare **input** | bare **input** | 0 | **0** |
| **T4** | bare **output** | bare **input** (arm 2's exact polarity) | 0 | **0** |

**T1 vs T4 is the whole experiment.** Same bareness on both, opposite polarity. If T1 creates a wire and T4 does not, the claim is dead and the cause is polarity — on a diagram with no FSIT, no shift register and no structure border, which also rules out (b). If T1 and T4 both fail, the claim survives and copyloop2 needs re-explaining. If both succeed, it is neither, and the FSIT/bed geometry is the suspect.

Then the decisive bed test, on a dated scratch copy: **swap the op's halves back** — put the uid-resolved `#7488` reference on the Invoke's `reference` input and the index-addressed border terminal on `Wire Source`, i.e. invoke on the true sink. That is a one-wire change to `OpFsInnerTunnelConnect_v0` (`build_opfsinnertunnelconnect_v0.py:509`, the `LeftTerm → Wire Source` wire), not a new op — and it already satisfies Pre-decided 119's "ONE missing capability: address a BARE terminal by UID at the Invoke", because `:323` proves the resolver returns #7488 from a bare tunnel with every error column empty.

## 5. Is there a documented NI verb for two bare terminals given one as a reference? — Yes, and your record of it is wrong

**`Terminal.Create Described Wire`**: *"Connects a wire to the terminal. **The wire source can only be another terminal.**"* Parameters: `Wire Source` (GObject refnum, **required**), `Wire Description` (**required** — 1D array of points, vertical then horizontal), `Auto Route?` (optional) — [labviewwiki, Terminal class/Create Described Wire method](https://labviewwiki.org/wiki/Terminal_class/Create_Described_Wire_method).

`docs/cycle27-plan.md:3448-3450` retires it with *"`Create Described Wire` is itself a `Terminal` method, so no NI verb wires anything without a terminal reference at one end."* That does not follow — **you have terminal references at both ends**: the border terminal is index-addressable (`c80_rowd_routeA_r2.log:92`) and #7488 is uid-resolvable (`build_opfsinnertunnelconnect_v0.log:323`). Being a Terminal method is the reason it fits, not the reason it doesn't.

And it is NI's own prescription **for this exact case**. Darren (NI), on connecting loose wires to structure tunnels: *"You can read the `Joints[]` property of the broken wire to get the coordinates of all the bends, then you can delete the broken wire, and re-create it with those same bend coordinates with the `Create Described Wire` method"* — marked solved ([NI Forums 4195933](https://forums.ni.com/t5/LabVIEW/Script-connect-existing-loose-wires-to-case-tunnels/td-p/4195933); [Wire class/Joints() property](https://labviewwiki.org/wiki/Wire_class/Joints()_property)).

⚠️ **Operational consequence, worth more than the rest of this review:** both runs deleted wire 7506 **without first reading its `Wire.Joints[]`** (`c80_rowd_routeA_r2.log:101-102`). Those coordinates are the required input to the documented route, and they die with the wire. On the next scratch copy, read `Joints[]` *before* the delete, unconditionally — it costs one property read and it is unrecoverable afterwards.

Second correction: `docs/NAMES.md:1143` and Pre-decided 118 say `Node.Connect Wires` *"needs both ends to be `Node`s"*. The wiki says *"The wire source can be either another node or a terminal"* ([Node class/Connect Wires method](https://labviewwiki.org/wiki/Node_class/Connect_Wires_method)). It is the **invoked object** that must be a Node — the source may be a Terminal. `WhileLoop #23032` is a Node, so the verb is type-legal here. It is still awkward for Row D: `Wiring Specs` addresses terminals by **name**, and 'Outgoing Handle' appears at both t1 and t2 of #23032 (`c80_rowd_routeA_r2.log:91`), so a name-addressed spec is ambiguous. Awkward is a different verdict from impossible, and the file currently records the wrong reason.

---

**Do I still believe the claim after all four? No.** It is refuted by `build_harness_copyloop2.log:39-40` as a statement about the method. The narrower, still-live question is why *this* call did nothing, and the measurement you have cannot separate polarity from routing from an unobserved error. What would change my mind: T1 above returning wire delta 0.

Sources: [Terminal class/Connect Wire method](https://labviewwiki.org/wiki/Terminal_class/Connect_Wire_method) · [Terminal class/Create Described Wire method](https://labviewwiki.org/wiki/Terminal_class/Create_Described_Wire_method) · [Node class/Connect Wires method](https://labviewwiki.org/wiki/Node_class/Connect_Wires_method) · [Wire class/Joints() property](https://labviewwiki.org/wiki/Wire_class/Joints()_property) · [NI Forums — Script connect existing loose wires to case tunnels](https://forums.ni.com/t5/LabVIEW/Script-connect-existing-loose-wires-to-case-tunnels/td-p/4195933) · [NI Forums — Connecting wires to build array through VI Scripting](https://forums.ni.com/t5/LabVIEW/Connecting-wires-to-build-array-through-VI-Scripting/td-p/3092615) · [NI — Connect Wire (API ref)](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/terminal/connectwire.html) (page returned only navigation shell to fetch — cited for completeness, not relied on)

## Sources

(extract from answer)

## What was done with it

Outcome **ANSWERED** (claude / `-Role hypothesis` / opus effort max, `tools/bench/peer_c82_bare_source.log`,
`BGRUN END rc=0 after 424s`). **The hypothesis this session put up is REFUTED, on our own evidence, and the
refutation is accepted.**

* **ACCEPTED, and it settles the framing:** `tools/bench/build_harness_copyloop2.log:31-40` records 6349C03
  creating a wire between two BARE terminals — wire census **9 → 10**, both ends on wire 346, `ExecState`
  0 → 1. A count of +1 cannot be a branch (`tools/gscript.py:2521-2522`). So *"the method silently declines
  when `Wire Source` is bare"* is FALSE as a property of the method, and cycle 82's G4f failure is specific
  to that call. This session's arm 1 / arm 2 differ in THREE ways at once (source wired vs bare · join vs
  create · polarity determined vs not), so the run cannot attribute the failure — that is a defect in the
  experiment's design, not in the op.
* **RECORDED, NOT ACTED ON — all three are judgement's, and the brief forbids improvising a route after a
  failed gate.** (a) the roles may be INVERTED: `Wire Source` is documented as *"the original source of the
  wire"*, and on the bed #7488 is `is_source=False` (the true sink) while the Invoke sits on a
  `is_source=True` terminal, so a CREATE has two sources and no sink — which also means **Pre-decided 119
  over-generalises**: `c80_rowd_routeA_r2.log:244` proved the roles may be exchanged when JOINING an
  existing net, not when creating a wire. (b) `Auto Route?` is at its default FALSE and no op in the fleet
  wires it. (c) the Invoke's own `error out` is not shown to reach the op's `error out`, so "silent" is so
  far only "quiet" — and NI Forums 4195933 reports the opposite (an error) for this situation.
* **THE CHEAPEST DISCRIMINATING TEST IS RECORDED AND WAS NOT RUN** (same reason): a 2×2 on a TRIVIAL scratch
  VI with `gscript.connect_terminals` alone — T1 invoke-on-bare-input / source-bare-output vs T4 the arm-2
  polarity. T1 vs T4 separates polarity from routing from geometry in ~2 minutes, touches no bed and builds
  nothing. The reviewer's follow-on (swap the op's halves so the Invoke sits on the true SINK — a ONE-WIRE
  change at `tools/recipes/build_opfsinnertunnelconnect_v0.py:509`, not a new op) is a DESIGN DECISION and
  is returned to judgement untouched.
* **CORRECTION THE REVIEWER OFFERS TO OUR RECORD, NOT APPLIED:** it says our note that
  `Terminal.Create Described Wire` does not fit is wrong — it takes a `Wire Source` GObject refnum plus a
  required `Wire Description`. Pre-decided 123's discipline (never edit a NAMES/doc line on a citation
  alone) applies, so nothing was edited.

(Claude fills in)
