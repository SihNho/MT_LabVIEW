# c81-uidref-probe

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.4884  in 22 / out 38726 / cache-create 170362 / cache-read 1467692  (529s, 22 turn(s))
- **date:** 2026-09-22 11:54:32
- **outcome:** ANSWERED (533s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# REFUTE THIS: "The only thing still missing for Row D is `uid -> Terminal reference`, and the D-1 probe below measures it correctly"

You are the failed-prediction reviewer. Attack the claim. Do not confirm it. Name the strongest reason it
is wrong, an alternative explanation, what would falsify it, and the cheapest discriminating test.

The failing log is `tools/bench/c80_rowd_routeA_r2.log`; the script is `tools/recipes/build_d1_m3a3.py`.
Its first failing line is:

    FAIL  [A1 94 D VISA] the sink terminal carries a wire after the write   the sink terminal #7488 is
    BARE, so there is no wire to re-connect FROM - the swapped call's source half has no uid

## The situation, in one paragraph

A LabVIEW VI is being restructured by VI Scripting over COM (behaviour-preserving refactor: scheduling may
change, computation may not). One wire ("Row D", uid **7506**) carries a VISA session handle out of the OLD
`WhileLoop #637` / `RightShiftRegister #4334` and must instead come out of the NEW `WhileLoop #23032` /
`RightShiftRegister #23868`. The SINK is `FlatSequenceInnerTunnel #7468`'s LEFT terminal, terminal uid
**#7488**, which belongs to no `Nodes[]` (a `FlatSequence` is `Generic -> GObject -> FlatSequence`,
measured). The SOURCE is the NEW loop's border terminal at `Diagram` traverse index 19, `Nodes[21]`,
`Terminals[1]`, name `'Outgoing Handle'`, `Is Source?` True, currently BARE.

## What was measured in the two runs of the recipe (facts, not opinion)

* ARM A2 (connect first, delete after), `c80_rowd_routeA_r2.log:244,253-261`: the SWAPPED
  `OpConnectFromWire_v0` call DOES attach the intended new source. The loop border terminal went BARE ->
  wire 7506, and a pre-delete walk of net 7506 shows THREE source terminals - `RightShiftRegister #23868`
  (the intended new one), `FlatSequenceInnerTunnel #7468`, and `RightShiftRegister #4334` (the old one) -
  with 0 rule violations. So the connect BRANCHES; it does not REPLACE. `Wire.Is Broken?` True,
  `ExecState` 0. Deleting wire 7506 afterwards leaves BOTH ends bare (measured twice).
* ARM A1 (delete first, then connect), `c80_rowd_routeA_r2.log:119`: with 7506 already deleted, the op's
  `Wire.Terms[]` read raises `error 1055: Property Node in OpConnectFromWire_v0.vi`, `UID 2` 0, wire delta
  0, #7488 stays BARE. A dead wire uid cannot supply a terminal.

## The claim you must attack

"Every writer on disk addresses its terminals as (diagram index, `Nodes[]` index, `Terminals[]` index) or
by taking a terminal out of a live `Wire.Terms[]`. Row D needs a terminal that is in no `Nodes[]` (#7488)
and a terminal that is on no wire (the bare loop border terminal). Therefore the ONE missing capability is
`uid -> Terminal reference`, and the correct next measurement is: does
`vi.lib\VIServer\UID to GObject Reference.vi` resolve a TERMINAL uid (it is proven only on TUNNEL and WIRE
uids), and can the resulting reference be downcast to `Terminal`? A YES selects a general `OpConnectByUid`
(donor `OpConnectNested_v2`); a NO selects an op built on the `FlatSequenceInnerTunnel` property
`Left Terminal` 1C3A9000."

## Specific things to attack, with what we already ruled out

1. **Is the probe even decisive?** `UID to GObject Reference.vi` returns a `GObject` refnum. Suppose it
   resolves the terminal and `GObject.Class Name` reads `Terminal`. Does that actually license wiring an
   Invoke node of class `Terminal`, method `Connect Wire` **6349C03**, to that reference over VI Scripting -
   or is there a separate reason a terminal reference obtained this way cannot drive that Invoke?
2. **Is there a cheaper route we have missed that needs NO new op?** Already ruled out and why:
   (a) `Tunnel.Inside Terminals[]` 6356000 / `Outside Terminal` 6356001 cannot address #7488, because
   `FlatSequenceInnerTunnel` is not a `Tunnel`; its own properties are `Left Terminal` 1C3A9000 /
   `Right Terminal` 1C3A9001. (b) No `Nodes[]` address for a `FlatSequence` exists. (c)
   `Node.Connect Wires` needs both ends to be `Node`s. (d) `Wire.Disconnect Terminal` 6370C0D is reported
   by labviewwiki as "(Not Implemented)". Is any of (a)-(d) wrong, or is there an (e)?
3. **The branch-vs-replace problem may be the real fault, not the addressing.** If the swapped connect
   branches rather than replaces, would a uid-addressed Invoke behave any differently? If not, the whole
   D-1 probe is measuring the wrong thing and the missing capability is "remove ONE source terminal from a
   net without destroying the net". Argue this if you can support it.
4. **Anti-history-echo.** Our uid readers have echoed stale values before. What would make a `Class Name`
   of `Terminal` coming back from this probe UNSOUND evidence, and what extra column would close that hole?

Answer with: the strongest reason the claim is wrong; an alternative explanation; what would falsify it;
and the single cheapest discriminating test, expressed as reads we can run on a scratch copy.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write is disabled in this session, so the review is below rather than in a file.

---

# REFUTED — the capability the claim calls missing is already on disk, and the failing log measured it working

## 1. The single strongest reason the claim is WRONG

**A live `Terminal` reference for #7488 is already obtainable with an op on disk, *after* wire 7506 is deleted — and `c80_rowd_routeA_r2.log` records it twice.**

`OpFsInnerTunnelTerm_v0` reaches #7488 through neither of the two addressing modes the claim enumerates. It goes `uid #7468 → FlatSequenceInnerTunnel.Left Terminal 1C3A9000 → the Terminal`, and then reads that terminal's own **UID**, its **Connected Wire** and its **Is Source?** — three `Terminal`-class properties. It cannot read them without holding a Terminal refnum.

The decisive lines are the *post-delete* reads — exactly the state A1's ordering leaves behind:

```
:104  READ[IN] uid 7468 -> ... | LeftTerm #7488 wire #0 | ... | err '' A '' B '' | errs error 1055
:265  READ[IN] uid 7468 -> ... | LeftTerm #7488 wire #0 | ... | err '' A '' B '' | errs error 1055
```

`term_a_uid` = **7488**, `err_a` = **empty**, with wire 7506 already destroyed. A1 did not fail because LabVIEW cannot hand out that terminal. It failed because the *swapped* call insists on fetching it from `Wire.Terms[]` of the wire the ordering must delete first (`:119`, error 1055) — a circular dependency the recipe created, not a limit the machine imposed. `docs/NAMES.md:1141` already says so: *"the REAL property — this is what `OpFsInnerTunnelTerm_v0` already reads (`LeftTerm #7488` on uid 7468, every error column empty)."*

**So D-1's two branches are not a fork.** The NO branch is available today. The YES branch is *worse*: its donor `OpConnectNested_v2.vi` **is not on disk** — deleted, the only one of gscript's 51 `OP_*` constants missing (`docs/cycle27-plan.md:2558`; `archive/peer/2026-09-22-c75-m3a3-run1-failpred.md:142,199,201`) — and run 1 of this very recipe already died on that absence (`:12`, `com_error 5507`, *after* the wire had been deleted). A measurement whose favourable answer selects the more expensive, less-measured path, and whose unfavourable answer selects the path that was already open, is not a decision gate.

**And D-1 does not touch the unknown the two branches share:** *does a `Terminal` refnum drive a `VI Server:Terminal` Invoke's `reference` over this COM path?* The YES branch adds **two** unmeasured primitives on top — uid→ref, and a TMSC to `Terminal` that `diag_c81_uidref.py:26-31` admits **no op on disk can even perform**. So, to attack point 1 directly: a `Class Name` of `Terminal` licenses nothing. `gscript.py:2237-2239` names the concrete build-time trap neither branch escapes — wire a `reference` into the erdosmiller Invoke creator and "the creator writes the object's bare class name and **fails silently**."

## 2. Alternative explanation of the same evidence

**The roles were inverted. The addressing was never the problem.**

NI's own text for 6349C03: *"Connects a wire to the terminal. The wire source can be either another terminal or a node"* — the invoked-on terminal **receives**; the parameter is the **source**. This project's own *measured* convention says the same in three places: `gscript.py:698-699` ("invoke on the SINK, `Wire Source` = the source"), `:747`, and `:2518-2523`, whose measured semantics read *"an already-wired **source** is BRANCHED (wire count unchanged); an already-wired **sink** is not safe."*

The swapped call did the opposite: Invoke on the loop-border **source**, `Wire Source` = the FSIT **sink**. What followed is `gscript.py:2522` playing out verbatim — an already-wired terminal handed into the source slot, branched, `wire_delta 0`. The corroborating detail: the FSIT terminal's `Is Source?` flipped **False → True** across the call (`:231` → `:255`, and `:239`). LabVIEW was told that terminal is a source, so it made one; the net then had ≥2 real sources and broke.

On this reading the missing capability is **(i)** putting the roles back — Invoke on #7488 from `Left Terminal`, `Wire Source` = `Diagram[19].Nodes[21].Terminals[1]`, delete-first — which needs no uid resolver at all; or **(ii)** removing the old source instead of the whole net.

## 3. Your ruled-out list: (d) is factually wrong, and there is an (e)

**(d) is wrong.** `Wire.Disconnect Terminal` **6370C0D is not marked "(Not Implemented)"** on labviewwiki. The Not-Implemented markers on the Wire class page sit on **6370C02 / 03 / 04 / 09** (Create Constant / Control / Indicator, Insert Node By Ref). 6370C0D has its own method page, with one required parameter, `Terminal` (Terminal Refnum), and no such marker. `docs/NAMES.md:1035` already calls it *"the per-sink primitive … on a wire that must survive."*

`docs/cycle27-plan.md:3509-3515` (PD123) parked it on that same misreading **while forbidding exactly that move**: *"resolved by MEASUREMENT, NEVER BY CITATION … a wiki page is evidence of convention on both sides."* Its stated rationale was *"Row D needs no disconnect verb — delete-then-connect is the route."* A1 closed that route for the swapped call, so the rationale expired with it. Wiki accuracy is not machine truth — but the stated reason for ruling (d) out has evaporated, and (d) turns A2's already-working connect into a landing: connect → branch → disconnect #4334's outer terminal → one source.

**(a), (b), (c) stand** on the class hierarchy: `Terminal` is `Generic → GObject → Terminal`, `FlatSequenceInnerTunnel` is not a `Tunnel`, `Create Described Wire` is itself a `Terminal` method.

**(e), never tried:** `Terminal.Connect Wire` also takes **`Auto Wire?` (default TRUE)** and `Auto Route?` (default FALSE). No op in the fleet has ever set either (`archive/peer/2026-09-22-c80-rowd-routeA-swapped-r2.md:152`, from the prior review on this question). If branch-vs-replace is the fault, that is the one documented knob that plausibly changes it, and reaching it is an edit to one Invoke node — cheaper than either D-1 branch.

**On attack point 3:** yes, and the log supports it. A uid-addressed Invoke would branch identically — addressing has no bearing on join semantics, which `gscript.py:2522` measured on a fresh Index Array long before Row D. So a YES on D-1 does not land Row D.

## 4. Anti-history-echo — what makes `Class Name = Terminal` unsound

Two holes, both open:

1. **No negative control.** `diag_c81_uidref.py:441-442` probes four uids and **all four are live**. Nothing separates "the resolver resolved" from "the resolver returns something for anything" — and the project already measured that its error column is **empty on a dead uid** (`:119`, `err_uidvi: ''`, recorded as PD121). `summary.uidvi_error` is that same column.
2. **The uid echo is circular.** `uid_back == uid_in` proves the op ran, not that the uid still denotes what it denoted when captured — and **this log proves UIDs are recycled in this VI**: `:127`, the Invoke created in arm A1 was handed uid **7506**, the wire deleted seconds earlier. That is the silent-wrong-object mode a general `OpConnectByUid` would inherit, passing every count-shaped gate — a rule-1a computation change.

**The missing columns:** a **never-allocated** uid and a **known-other-class** uid as negative rows, plus a **cross-route identity check** — resolve #7488 by the uid route and by the structural route in one run, requiring agreement on `Name`, `Owner`, `Is Source?`, `Connected Wire`. Agreement between two independent addressings is soundness; agreement between a uid and its own echo is not.

## 5. What would falsify this review

I am wrong, and the claim survives, if **a `Terminal` refnum from `Left Terminal` 1C3A9000 cannot drive a `VI Server:Terminal` Invoke's `reference` while one from `UID to GObject Reference.vi` + TMSC can.** That is the only world in which the uid route is the unique key, and nothing measured so far bears on it either way for either route.

## 6. Cheapest discriminating test

**It has already been run:** `OpFsInnerTunnelTerm_v0` on #7468 *after* the delete returns `LeftTerm #7488`, `err_a` empty (`:104`, `:265`). Refuting the claim costs zero LabVIEW time.

For the part still genuinely open, three lines in the probe already written — no new op, no extra seconds:

1. `targets.append(("NEG never-allocated", 999983))` and `targets.append(("NEG known Diagram", 686))`. **One indicator:** `returned_class_name` + `uidvi_error` on row 1. A class name with an empty error on a never-allocated uid ⇒ D-1 is void whatever #7488 returns.
2. Print `err_bcw` beside `err_a` for #7468 (already in the returned dict, just not in the `READ[IN]` line) to attribute the aggregate `errs error 1055` on the post-delete reads — expected to be the `Connected Wire` read on a now-bare terminal.
3. Require `ownerchain(7488).ownercls/owner_uid` == `FlatSequenceInnerTunnel #7468` — cross-route agreement, not self-echo.

## 7. Where the evidence does not settle it

- **The three "source terminals" at `:259`: the measurement does not distinguish three genuine sources from a degenerate `Is Source?` read on a broken wire.** ≥2 is structurally certain (#4334 was never disconnected), so the branch conclusion survives — but the same reading PD119 uses to prove "the verb works" also says the *sink* became a source, and both cannot be taken at face value. The join itself is independently proven from the terminal side (`:244`).
- **Whether 6370C0D works on this LV2026 build.** The wiki removes the stated reason for ruling it out; it does not establish the method. PD123's own instruction — probe it — is right.
- **Which stage emitted `errs error 1055` on `:104`/`:265`.** `err`, `err_a`, `err_b` are all empty; the aggregate is unattributed. §6.2 settles it for free.

## Recommendation

**Do not gate D-2 on D-1.** Run the probe with the two negative rows (it costs nothing), and schedule D-2 on the FSIT-head op regardless — sink from `Left Terminal` 1C3A9000, `Wire Source` from `Diagram[19].Nodes[21].Terminals[1]`, Invoke on the **sink**, delete-then-connect. Let D-1 decide only whether a *later* general `OpConnectByUid` is worth building — noting it cannot be built at all until `OpConnectNested_v2.vi` is recreated.

**Sources** — local: `tools/bench/c80_rowd_routeA_r2.log:12,62-69,104,119,127,231,239,244,255,259,265` · `tools/gscript.py:698-699,747,2237-2239,2518-2523` · `docs/NAMES.md:1035,1141` · `docs/cycle27-plan.md:2558,3410-3418,3462-3474,3485-3497,3509-3515` · `tools/bench/diag_c81_uidref.py:26-31,441-442` · `archive/peer/2026-09-22-c75-m3a3-run1-failpred.md:142,199,201` · `archive/peer/2026-09-22-c80-rowd-routeA-swapped-r2.md:152` (checked per CLAUDE.md's "check `archive/peer/` for the same question before re-asking"). External: [NI Terminal.Connect Wire](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/terminal/connectwire.html) · [labviewwiki Terminal class](https://labviewwiki.org/wiki/Terminal_class) · [labviewwiki Connect Wire method](https://labviewwiki.org/wiki/Terminal_class/Connect_Wire_method) · [labviewwiki Wire class](https://labviewwiki.org/wiki/Wire_class) · [labviewwiki Wire.Disconnect Terminal](https://labviewwiki.org/wiki/Wire_class/Disconnect_Terminal_method) · [NI FlatSequenceInnerTunnel Left Terminal](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/flatsequenceinnertunnel/leftterminal.html)

## Sources

(extract from answer)

## What was done with it

Dispositioned by the cycle-81 MATERIAL session (D-1 of M3a-3b), 2026-09-22. This session measures; it does
not decide designs, so findings split into "applied here" (measurement quality) and "returned to judgement"
(design). Nothing from the second group was acted on.

**ACCEPTED AND APPLIED IN THIS DISPATCH — all three of section 6, all pure measurement, no design change:**

1. §6.1 / §4.1 *no negative control* — ACCEPTED. `tools/bench/diag_c81_uidref.py` now probes two extra uids
   with the identical columns: `NEG_UID = 999983` (never allocated) and `D686 = 686` (a known-OTHER-class
   uid, a `Diagram`). Without them nothing separates "the resolver resolved a terminal" from "the resolver
   returns something for anything", and `c80_rowd_routeA_r2.log:119` already measured the uid-VI's error
   column EMPTY for a DELETED wire uid, so the hole is not theoretical.
2. §6.2 *the aggregate `errs error 1055` is unattributed* — ACCEPTED. `err_bcw` is now read and reported as
   its own column beside `err_a`/`err_b` in `probe_fsit()`, so the FSIT op's per-stage errors are
   attributable instead of concatenated.
3. §6.3 / §4.2 *the uid echo is circular* — ACCEPTED. A new `[P-X] CROSS-ROUTE IDENTITY` phase asserts that
   TARGET A, reached STRUCTURALLY via `FlatSequenceInnerTunnel #7468`.`Left Terminal`, has that same tunnel
   as its owner when read back through the UID route. Agreement between two independent addressings is the
   soundness check; the self-echo is kept but is no longer the only one. The recycled-uid evidence the review
   cites (`c80_rowd_routeA_r2.log:127`, a new Invoke handed uid 7506) is quoted in the code comment.

**RETURNED TO THE JUDGEMENT SESSION, NOT ACTED ON — every one of these is a design decision (CLAUDE.md §3):**

4. §1 + Recommendation: *"do not gate D-2 on D-1; schedule the FSIT-head op regardless, and note that
   `OpConnectByUid`'s donor `OpConnectNested_v2.vi` is not on disk"*. This overturns Pre-decided 121's fork,
   which is judgement's to overturn, not this session's. Reported in the return summary under `OPEN:`.
5. §2: *the roles were inverted; invoke on the SINK #7488 with `Wire Source` = the loop border terminal*.
   A change to the recipe's call shape = a design change. Not made.
6. §3: *(d) is factually wrong — `Wire.Disconnect Terminal` 6370C0D is NOT marked "(Not Implemented)"; the
   Not-Implemented markers sit on 6370C02/03/04/09*. This contradicts Pre-decided 123, and PD123 itself
   forbids editing `docs/NAMES.md:1035` on a citation alone. No doc was edited; reported.
7. §3(e): *`Terminal.Connect Wire` also takes `Auto Wire?` (default TRUE) / `Auto Route?`, never set by any
   op in the fleet*. A new, unmeasured knob. Not touched.
8. §7: the three-source reading at `c80_rowd_routeA_r2.log:259` may be degenerate. Recorded, not re-measured
   — this dispatch is read-only on the bed and re-running arm A2 is explicitly forbidden by STATUS NEXT.

**NOT ACCEPTED:** nothing. No finding was refuted.
