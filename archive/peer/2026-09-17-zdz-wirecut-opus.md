# zdz-wirecut-opus

- **agent:** claude
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $4.8500  in 38 / out 37482 / cache-create 267588 / cache-read 2390597  (536s, 30 turn(s))
- **date:** 2026-09-17 18:16:17
- **outcome:** ANSWERED (540s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK the explanation below. It is the one UNPREDICTED result in `tools/bench/build_d1_routeb_v0_run3.log`
(84 pass / 3 fail, 540 s). Read the files; do not take my summary on trust.

=== WHAT WAS PREDICTED AND WHAT HAPPENED ===

Row under test: `#2222` t0 (an UNNAMED sink on a `CaseStructure` that MOVES into new loop 1.2) whose source is
the front-panel control `Z/dZ`, uid 47. The plan (decision 2 of the session brief) was: use the control's OWN
wire if it has one, branch off it by index with `OpConnectFromWire_v0`; only if it has none, make a temporary
named sink.

MEASURED FIRST, read-only on a PRISTINE copy of the original — `tools/bench/diag_sr_transport.log`, 10 pass /
0 fail (`tools/bench/sr_transport.json`):
    P4  Z/dZ is on the panel exactly once as a CONTROL: {"label":"Z/dZ","indicator":false,"uid":47,
        "is_source":true,"wire":730,"term_err":0,"wire_err":0}
    P5  w730's terminals: [0] is_source=True owner Diagram#639 ; [1] is_source=False owner Tunnel#2276 ;
        [2] owner #0 (empty).  NO NAMED SINK on the net.
    P6  #2222 t0: name '' , is_source False , wire 730  -> the SAME net.

THEN, in the build (`build_d1_routeb_v0_run3.log:386`), AFTER S1t/S1d's deletes, S2's three new loops, S3's 21
node moves and 6 ControlTerminal reparents:
    NO-ROUTE #2222 t0 '' <- from-ctl 47   'Z/dZ' carries NO wire on this copy
`g.panel_wiring(TARGET)` reported `wire = 0` for the label `Z/dZ`. So the wire the pristine original has is gone
by the time the row is reached.

=== MY EXPLANATION, WHICH YOU MUST ATTACK ===

(G1) w730's only sink was `Tunnel #2276`. `#2222` (the Case structure) moved into 1.2's body, and whatever
     structure owned `Tunnel #2276` either moved with it or had the tunnel removed, so the net lost its sink and
     was deleted — either by the move itself or by one of the build's `remove_bad_wires_scripted` calls. A wire
     with a source and no sink is exactly what Remove Bad Wires removes.
(G2) Therefore the "use the control's own wire" branch of decision 2 can never fire in this build, and the
     TEMPORARY NAMED SINK is not a fallback but the only route.
(G3) The temporary-sink mechanism is currently disarmed (`TEMP_SINK_AUTHORISED = False`) because the way it was
     written — `OpCreateEqual_v0` with `src_names=()` — contradicts that op's recorded contract (both operands
     come from `Get Outputs`, `docs/toolkit-capabilities.md:52`) and `docs/NAMES.md:468-480` records that an
     invalid terminal refnum makes the creator call `Connect Wire` with an invalid reference and raise an
     **error-1055 MODAL DIALOG that an error-out indicator does not silence** — disqualifying in an unattended
     run under this project's bgrun discipline.
(G4) So the row needs a named sink that some EXISTING, MEASURED helper can create, and the candidates I know of
     are: `gscript.create_indicator(target, node_index, terminal_index)` (creates an indicator FROM a node's
     output terminal — wrong direction for a control), the "temporary indicator, branch, delete" trick recorded
     in `archive/bench-2026-09-09-gpu-dropin-kernel/build_gpu_kernel.py:14-15` and
     `docs/stage2-assembly-step-b.md:48-50,:63-67`, and `drop_subvi` of some VI with a named input of the right
     type. None of them is obviously right for a CONTROL terminal whose only consumer is an unnamed Case tunnel.

=== YOUR JOB ===
1. The strongest reason G1 is WRONG. What else destroys a front-panel control's wire during a sequence of
   deletes / loop creations / `GObject.Move` reparents? Could `Z/dZ`'s TERMINAL itself have been reparented by
   S3-ct (the build reparents 6 ControlTerminals, and `Z/dZ` is one of the six — see `CTLTERM_LABELS_12` in
   `tools/recipes/build_d1_routeb_v0.py`), and would `panel_wiring` then report wire 0 even though a wire still
   exists?  That would make G1 the wrong diagnosis entirely.
2. What would FALSIFY G1, using only readers this project already has (`gscript.panel_wiring`,
   `gscript.node_terms`, `gscript.tunnels`, `build_opconnectfromwire_v0.wire_source_owner` = `OpWireSource_v5`,
   `gscript.report_all`)?  Name the cheapest discriminating test and where in the build it must run.
3. An ALTERNATIVE route for this row that uses only mechanisms this project has ALREADY MEASURED — in
   particular, is there one that never needs a temporary object at all? Consider the ORDER of operations: the
   wire exists before the moves.
4. Is G3's modal-dialog risk real for `OpCreateEqual_v0` specifically, or am I over-reading a record about a
   different creator? Cite the op's own test log if it contradicts me.
5. This row is 1 of 66 and the VI cannot reach `ExecState 1` anyway (the 8 queues and the 3 sentinels are
   unbuilt, so three While loops have unwired conditional terminals). Argue the case that chasing this row now
   is the wrong work, and say what the right next measurement is.
Answer with file:line citations from this project wherever you assert something about its code.



--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**The single strongest reason G1 is wrong: the build destroyed `Z/dZ`'s wire itself, one step earlier, with an operation this project has already MEASURED to do exactly that — and G1 never mentions it.** `tools/bench/build_d1_routeb_v0_run3.log:163` records `PASS S3-ct ControlTerminal #403 ('Z/dZ') -> 1.2`. Moving a `ControlTerminal` to another diagram is measured to set its `panel_wiring` wire to 0: `tools/bench/probe_move_ctlterm_v0.log:134` reads `panel rows whose connected wire changed … [((7, 'stop (end)'), 6929, 0)]`, and `:136` says `ExecState now 0 (0 expected: wires were cut)`. Your own recipe states it as settled fact at `tools/recipes/build_d1_routeb_v0.py:39-41` — *"a move CUTS the wire and moving back does not restore it"* — and the whole S3-ct by-effect resolver **depends on that being true**. So `Z/dZ` carrying no wire is the predicted, already-recorded consequence of the build's own `move_in(#403)`, not evidence about `Tunnel #2276`, sink loss, or Remove Bad Wires.

---

## 1. Why G1 is wrong

**(a) The Remove Bad Wires clause is excluded by the recipe's own call sites.** `remove_bad_wires_scripted` is called exactly three times: `build_d1_routeb_v0.py:331` (S1t — *before* S2 creates any loop and before any move), `:1004` (inside the un-authorised temp-sink branch, never reached in run 3), and `:1288` (S5 — *after* the S3w ledger). **There is no RBW call between the moves and the `from_ctl_unnamed` read.** G1's "…or by one of the build's `remove_bad_wires_scripted` calls" is not merely unproven, it is contradicted by the file.

**(b) The "net lost its sink" mechanism is unnecessary.** w730 has exactly two live terminals — source `ControlTerminal #403`, sink `Tunnel #2276` (= `#2222` t0) — per `diag_sr_transport.log:21-23`. **Both endpoints move into loop 1.2's body** (`run3.log:124` for `#2222`, `:163` for `#403`). A wire cannot span two diagrams; whichever endpoint moves first kills it. G1 picks one endpoint, invents a deletion agent for it, and omits the other endpoint entirely — the one whose move is independently measured to zero the very reader that reported the failure.

**(c) G2 is wrong in the way that matters.** "The control's own wire branch can never fire in this build" is true, but *not* because the structure moves destroyed the net. It is true because `docs/d1-route-b-plan.md:193-194` fixes the ordering — *"reparent the 8 control terminals BEFORE any `wire_control`"* (a fix for run 7's six 5001s from `Get Controls.vi`) — and that ordering rule guarantees the control is bare by the time `from_ctl_unnamed` looks at it. **That is a decision, not a property of the VI**, and decisions can be reordered. G1's framing makes the blockage look structural and forces you toward the temporary sink; the real framing makes it a scheduling question.

**(d) Direct counter-example inside the same run.** `run3.log:369`:
```
WIRED #2222 t5 'Correction Factor' <- from-ctl 9289  wire_control … wire 0 -> 29307; reparented=True
```
`ControlTerminal #9306` was reparented at `:166` exactly like `#403`, its wire to `#2222` t5 was cut (`:254`, `cut #2222 t5 'Correction Factor' IN was w6096 [moved]`), **and a wire was then created from it anyway**. The difference between the WIRED row and the NO-ROUTE row is not the wire and not the move — it is that t5's sink carries a name and t0's does not. G1 diagnoses the wrong variable.

## 2. Alternative explanations of the same evidence

- **A1 (my primary): `move_in(#403)` cut it.** Measured mechanism, measured on this reader, applied to this object, logged at `run3.log:163`.
- **A2: `move_in(#2222)` cut it first** (G1's cause, minus the RBW story — the move alone suffices). Runs at `run3.log:124`, i.e. **before** A1, since `s3()` moves nodes at `:543-557` and ControlTerminals at `:559-574`.
- **A3 — the one that would make both A1 and G1 wrong: the read failed.** `panel_wiring` walks `Panel.Controls[] → Control[Terminal] → Terminal[Connected Wire]` (`gscript.py:772-781`) and returns `term_err` / `wire_err` per row (`:806-808`); a genuine bare terminal is documented to come back as `wire == 0` **with `wire_err == 1055` and `term_err == 0`**. `from_ctl_unnamed` reads **only** `row.get("wire")` (`build_d1_routeb_v0.py:955`) and discards both error columns. So run 3 cannot distinguish "the terminal is bare" from "`Control.Terminal` errored after the reparent and defaulted to 0". **The log sentence "MEASURED, reported, not guessed" overstates what was measured.**

I can exclude one candidate: a label mismatch. `:951` looks the row up by `label == 'Z/dZ'`; had it missed, the code would have printed the `:953` message instead of the `:957` one. The row was found.

**On your Q1 sub-question — would `panel_wiring` report 0 while a wire still exists?** On the evidence, no: `probe_move_ctlterm_v0.log:136` reports `ExecState 0` after the move with the comment *"wires were cut"*, so the 0 there was real. But that is a different VI state, and run 3 threw away the columns that would prove it here. Honest answer: **the run-3 measurement does not distinguish A1, A2 and A3.**

## 3. What would falsify the claim

G1 is falsified if **`Z/dZ` still carries a non-zero wire immediately after the 21 node moves and before the 6 ControlTerminal moves.** That observation kills A2 and G1 together and leaves A1. Conversely, `wire == 0` at that point with `wire_err == 1055` confirms A2 and refutes A1; `wire == 0` with any other error code, or `term_err != 0`, confirms A3 and refutes both.

## 4. The cheapest discriminating test

**One `g.panel_wiring(TARGET)` call inserted in `build_d1_routeb_v0.py` between line 557 (end of the node-move loop) and line 559 (`ct_before = g.count(...)`), printing the `Z/dZ` row in full — `wire`, `term_err`, `wire_err` — plus the same print immediately after the ControlTerminal loop at `:574`.** Cost ≈ 0.8 s each (`gscript.py:781`), no new op, no new build, read-only, and it separates A1 / A2 / A3 outright. Run 3 already called `panel_wiring` at `:638` and `:1384` and discarded the error columns both times — **the evidence was collected and thrown away**, so the marginal cost is a `print`.

---

## Your remaining questions

**Q3 — an alternative route.** Two corrections first. There is no ordering that *preserves* w730: both endpoints must leave Diagram #639, and a wire cannot span diagrams. And `OpConnectNested_v1` cannot substitute — `docs/d1-route-b-plan.md:191` and `docs/main-vi-startup.md:66` both record that a `ControlTerminal` is a `Terminal`, not a `Node`, so `Diagram.Nodes[]` does not list it (externally confirmed: [ControlTerminal class](https://labviewwiki.org/wiki/ControlTerminal_class) inherits from [Terminal class](https://labviewwiki.org/wiki/Terminal_class), a sibling of Node under [GObject](https://labviewwiki.org/wiki/GObject_class)).

What the evidence actually points at is one op, built the way `OpConnectFromWire_v0` was built: **`OpWireCtl_v0`'s source head + `OpConnectNested_v1`'s sink tail.** `OpWireCtl_v0` already turns a control *label* into a *terminal refnum* via `Get Controls.vi` (`gscript.py:1876-1877`) — that is precisely the ControlTerminal reference you cannot otherwise obtain. The only name-dependence is the sink half, `Wire Inputs.vi`. Replace that with the `Terminal.Connect Wire` 6349C03 invoke and the `Diagram → Nodes[] → Terms[]` ladder that `OpConnectNested_v1` already carries, and the row needs **no wire on the control, no temporary object, and no dependence on move order**. That is the same additive-donor technique recorded at `docs/toolkit-capabilities.md:58`, and it closes the whole R3 class, not one row. It is still a new op — say that plainly rather than calling it free.

A no-new-op option exists but is worse: `wire_control` `Z/dZ` → any bare **named** input on 1.2's body (the build already enumerates them via `bare_named_sinks`, `build_d1_v0.py:482`), branch that wire onto `#2222` t0 with `OpConnectFromWire_v0`, then remove the temporary segment. It is the same temporary-sink shape with an existing node instead of a created one, and it inherits the same "does deleting the segment take the branch with it" hazard your `:997-999` comment already names.

**Q4 — G3's modal-dialog risk: your citation is wrong, your caution is not.** `docs/NAMES.md:468` is the heading **"OpBuildCase_v0 (erdosmiller `Create Case Structure.vi`) — SUPERSEDED by v1"**; `:473-475` is about `SetControlValue` on that op's `Selector` **refnum control**, and `:478-480` about that specific error. It is not a statement about `OpCreateEqual_v0`. Worse, the row you cite as support says the opposite: `docs/toolkit-capabilities.md:52` describes `OpCreateEqual_v0` as *"both operands are fetched INSIDE the op, so no terminal refnum crosses COM (**the fix for `docs/NAMES.md:473-475`**, the 1055 modal that killed `OpBuildCase_v0`)"*. You cited the fix as evidence of the defect it fixes.

That said, the hazard is not zero, and the mechanism is not the one you wrote. `create_equal` passes `src_names=()` (`build_d1_routeb_v0.py:779`), which `create_node` turns into `Names = []` and `Names 2 = []` (`build_opsentinel_ops.py:397,400`). `Get Outputs` then yields an empty array, `Index Array[0]` of an empty array returns a **default refnum with no error**, and `Create Equal.vi`'s `x`(5) and `y`(7) are refnum inputs (`build_opsentinel_ops.py:66-67`). So an invalid refnum reaches the creator from *inside* — the same end state, reached by a different path. Whether `Create Equal.vi` guards it or calls `Connect Wire` unguarded is **not recorded anywhere in this project**, and I could find no external source that documents erdosmiller's internals. `TEMP_SINK_AUTHORISED = False` is defensible; the sentence in the log justifying it is not, and should be rewritten before it is cited again as a measured fact.

**Q5 — yes, this row is the wrong work, and your own files say so twice.**

- **It does not unblock anything.** STATUS.md:103-107 states it directly: *"THE LEDGER GATE IS NOT WHAT BLOCKS THE SAVE"* — `s1q` (8 queues) and `s4b` (3 sentinels) are unexecuted, so 1.2/1.5/1.7 have unwired conditional terminals (`run3.log:417-419`, all `wire 0`) and `ExecState 0` by construction (`:426`). Wiring this row yields 64 WIRED / 2 NO-ROUTE, `ExecState 0`, nothing saved. Zero change in deliverable state for one new op or one unmeasured op call.
- **The other two NO-ROUTE rows are worth more.** `#1359` t1 and `#29874` t3 block on a *computation* decision already made in principle (registers move with their nodes; `add_shift_reg` + `wire_sr`), and they sit on the critical path of the loop split. Two rows, and the decision is reusable.
- **A gate outranks all three.** STATUS.md:69-70 and :115: OPEN 32, **two consecutive `OUTCOME-VIOLATION`s ⇒ the work stops for a re-plan with the user**, *"Not answerable by a device"*, *"still stands above all three."* CLAUDE.md's outcome-review rule says a repeat is answered by a delivery cycle or a re-plan — not by another route-B row and not by another op.

**The right next measurement,** if any LabVIEW time is spent before that re-plan: the two-line `panel_wiring` probe of §4 (it costs seconds and settles this row's diagnosis permanently) folded into **one** read-only run whose real payload is STATUS NEXT #1 — **which named output terminal types each of the 8 queues**. That is the single undesigned item standing between this build and a saved `Track_v6_D1_GPU.vi`.

---

**Where I would change my mind:** if the mid-S3 `panel_wiring` read comes back with `Z/dZ` at `wire == 0`, `wire_err == 1055`, `term_err == 0` *before* `#403` moves, then A1 is dead, G1's cause is confirmed in substance (the structure move, though still not Remove Bad Wires — that clause stays refuted by the call sites), and the ordering route in Q3 is worthless. I do not think that is what you will see, but it is one read away and I am not willing to assert it without one.

**Sources:** [ControlTerminal class — LabVIEW Wiki](https://labviewwiki.org/wiki/ControlTerminal_class) · [Terminal class — LabVIEW Wiki](https://labviewwiki.org/wiki/Terminal_class) · [GObject class — LabVIEW Wiki](https://labviewwiki.org/wiki/GObject_class) · [VI Server Class Hierarchy — NI](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/class-hierarchy.html) · [Block Diagram.Remove Bad Wires method — LabVIEW Wiki](https://labviewwiki.org/wiki/VI_class/Block_Diagram.Remove_Bad_Wires_method)

## Sources

(extract from answer)

## What was done with it

**G1 is WITHDRAWN. My diagnosis was wrong and this arm's is right, on evidence from the build's own log.**
Both `-Dual` arms ANSWERED (codex 240 s, opus 540 s). No code was changed afterwards: the session's hard stop
arrived (user, 2026-09-17: an experiment in ~1 h, LabVIEW released, no instrument access), so this is recorded
for the next session rather than acted on.

What replaces G1, and it is better than G1 in the way that matters:

1. **The build cut `Z/dZ`'s wire itself, one step earlier.** `build_d1_routeb_v0_run3.log:163` —
   `PASS S3-ct ControlTerminal #403 ('Z/dZ') -> 1.2`. Moving a `ControlTerminal` to another diagram is MEASURED
   to zero its `panel_wiring` wire (`tools/bench/probe_move_ctlterm_v0.log:134,:136`), and the recipe's own
   header says so at `tools/recipes/build_d1_routeb_v0.py:39-41`. I built a story about a lost sink and Remove
   Bad Wires while the answer was a `PASS` line 220 lines above the failure.
2. **My RBW clause is contradicted by the file**: the three `remove_bad_wires_scripted` calls are at `:331`
   (before any loop or move), `:1004` (the unreached temp-sink branch) and `:1288` (S5, after the ledger) —
   there is NO RBW between the moves and the `from_ctl_unnamed` read.
3. **Both endpoints of w730 move into 1.2** (`#2222` at `run3.log:124`, `#403` at `:163`); a wire cannot span
   two diagrams, so whichever moves first kills it. I named one endpoint and invented an agent for it.
4. **G2 was right by accident and wrong in framing.** The control-wire branch cannot fire — but because of an
   ORDERING DECISION (`docs/d1-route-b-plan.md:193-194`, "reparent the 8 control terminals BEFORE any
   `wire_control`", itself a fix for run 7's six 5001s), not because of a structural property. Decisions can be
   reordered; my framing made it look structural and pushed toward the temporary sink.
5. **The counter-example that settles it, in the same run**: `run3.log:369` WIRED `#2222` **t5**
   `'Correction Factor'` from `ControlTerminal #9306`, reparented at `:166` exactly like `#403`, its wire cut at
   `:254`. The difference between the WIRED row and the NO-ROUTE row is that **t5's sink has a NAME and t0's
   does not** — so the variable is the sink name, not the wire and not the move.
6. **The gate above all of it**, which this arm put last and I put first here: STATUS OPEN 32 — two consecutive
   `OUTCOME-VIOLATION`s ⇒ the work stops for a re-plan with the user. Chasing 1 of 66 rows in a VI that cannot
   reach `ExecState 1` (the 8 queues and 3 sentinels are unbuilt, so three While loops have unwired conditional
   terminals) is the wrong work whatever the mechanism turns out to be.

FIXED: unread-evidence - `archive/2026-09-17-status-d1-route-b-3.md`:1 - the session archive records that the
Z/dZ wire was cut by the build's own S3-ct reparent of ControlTerminal #403, not by sink loss or Remove Bad
Wires, and that the blocker is the ordering decision plus the unnamed sink.
