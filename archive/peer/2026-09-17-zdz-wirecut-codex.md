# zdz-wirecut-codex

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-17 18:07:17
- **outcome:** ANSWERED (240s)
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

The explanation is wrong at its causal step: the build itself deliberately reparents the `Z/dZ` ControlTerminal, and this project has already measured that moving a ControlTerminal cuts its wire—even if it is moved back. The code says so explicitly at `tools/recipes/build_d1_routeb_v0.py:445-450`; the real run identifies `Z/dZ` as ControlTerminal `#403` and moves it into loop 1.2 at `tools/bench/build_d1_routeb_v0_run3.log:161-163`.

1. Strongest attack on G1

G1 blames loss of `Tunnel #2276` or Remove Bad Wires, but the chronology does not support that diagnosis:

- After S1t’s cleanup and after loop creation, `#2222 t0` still carried `w730`; the S3 before/after census records it as `cut … was w730` at `tools/bench/build_d1_routeb_v0_run3.log:249`. Therefore S1t’s `remove_bad_wires_scripted` at `tools/recipes/build_d1_routeb_v0.py:319-337` did not delete it.
- There is no Remove Bad Wires call between the S3 moves and the failed lookup. S3, S3c, and S3w execute consecutively at `tools/recipes/build_d1_routeb_v0.py:1379-1381`; the next unconditional cleanup is only in S5 at `:1278-1289`, after the ledger.
- During S3, both possible endpoints are moved: the CaseStructure and ControlTerminal `#403`. The build already knows that the latter operation cuts its terminal wire (`:445-450`).

Thus “the sink disappeared, so the net was deleted” is not established. An equally strong—and already independently observed—explanation is:

> Reparenting ControlTerminal `#403` disconnected `Z/dZ` from `w730`; `panel_wiring` subsequently reported that local disconnection.

Yes, `panel_wiring` can report `wire = 0` while a Wire object or the old sink-side segment still exists elsewhere. Its contract is specifically `Control.Terminal → Terminal.Connected Wire`; zero means that panel object’s diagram terminal is bare, not that no wire with UID 730 exists anywhere in the VI (`tools/bench/write_panel_wiring_section.py:4-8`, `:28-34`). Run 3 never checked global membership of UID 730 after the move.

2. Observation that would falsify G1

The clean falsifier is a ControlTerminal-only move:

- Keep `#2222` and `Tunnel #2276` untouched.
- Read `Z/dZ`, `#2222 t0`, and global wire UID 730.
- Move only ControlTerminal `#403`.
- Repeat the same reads.

If moving only `#403` changes `Z/dZ` from 730 to 0, G1’s proposed prerequisite—loss of the sink/tunnel—is false. This is especially cheap because `resolve_ctlterms()` already performs exactly that destructive move on a throwaway pristine copy at `tools/recipes/build_d1_routeb_v0.py:462-486`; it currently records only which panel row changed, not the before/after wire topology (`:486-495`).

Use the existing readers as follows:

- `panel_wiring`: does `Z/dZ` change 730→0?
- `node_terms`: does stationary `#2222 t0` remain on 730?
- `report_all("Wire")`: does UID 730 still exist globally?
- `wire_source_owner(730)`: which terminals, if any, remain attached?
- `tunnels` or `report_all`: is tunnel UID 2276 still present?

The current full-build census proves only that `#2222 t0` became bare after the combined moves (`build_d1_routeb_v0_run3.log:249`); it cannot identify which move caused it.

3. Alternative route without a temporary object

There is a plausible zero-temporary route using only the already-measured `OpConnectFromWire_v0`, but it depends on operation order:

1. Create loop 1.2.
2. Do not reparent `Z/dZ` ControlTerminal `#403`.
3. Move `#2222` into 1.2.
4. Immediately re-read `Z/dZ`.
5. If it still carries `w730`, use `OpWireSource_v5` plus `OpConnectFromWire_v0` to connect that existing source net to moved `#2222 t0` by index.
6. Leave `#403` on the original frame-body diagram.

This is not a speculative new writer: run 3 successfully used `OpConnectFromWire_v0` for sixteen nested sinks with `Is Broken? FALSE`, including two other unnamed terminals on `#2222` (`tools/bench/build_d1_routeb_v0_run3.log:390-405`). The missing fact is only whether moving `#2222` alone preserves the control-side `w730`.

The present order destroys that opportunity: all nodes are moved first at `tools/recipes/build_d1_routeb_v0.py:542-557`, then all six ControlTerminals at `:559-576`, and only much later does `from_ctl_unnamed()` inspect the control wire at `:942-961`.

If moving `#2222` alone also makes `Z/dZ` bare, this zero-object route is falsified. But that has not been measured separately.

4. G3 overstates the modal evidence

The 1055 modal is real, but the cited evidence concerns a different creator and a different refnum input:

- `docs/NAMES.md:463-475` documents `Create Case Structure.vi`, specifically its invalid `Selector` terminal refnum.
- It does not test `Create Equal.vi`, empty `Names` arrays, or `Get Outputs` returning no terminal.
- `OpCreateEqual_v0` deliberately obtains both terminal refnums inside the op, so no terminal refnum crosses COM (`docs/toolkit-capabilities.md:52`).
- Its own functional test completed 23/0: one Comparison was created, its owner chain was correct, its Boolean drove the loop stop, and the scratch reached `ExecState 1` (`tools/bench/build_opsentinel_ops_run3.log:39-50`).

That test used valid names—`["queue out", "element"]`—not `src_names=()` (`tools/recipes/build_opsentinel_ops.py:499-505`). Therefore it does not prove the empty-name call safe. But it does contradict transferring the Case-creator modal result wholesale to `OpCreateEqual_v0`.

The defensible conclusion is: `src_names=()` is unmeasured and may fail; a 1055 modal from this particular call is not established. Keeping `TEMP_SINK_AUTHORISED=False` is conservative, but G3’s claimed op-specific evidence is too strong.

5. This row is currently the wrong priority

Even a perfect repair of `#2222 t0` cannot produce a runnable or savable VI:

- `s1q` intentionally creates none of the eight queues because their type-source terminals are unspecified (`tools/recipes/build_d1_routeb_v0.py:1243-1258`).
- S4 then skips all three sentinel `Equal?` objects, leaving the three new loops’ conditional terminals unwired (`:1261-1275`).
- The recipe itself states that these omissions make `ExecState 1` impossible by construction (`:131-135`).
- `STATUS.md:100-113` correctly ranks queue element types first and this `Z/dZ` row third.

The right next measurement is the eight-row queue type-source table: for each of `Q_free`, `Q_work`, `Q_meta`, `Q_res`, `Q_good`, `Q_rmeta`, `Q_focus`, and `Q_focusback`, identify an existing, named output terminal of the correct payload type and record its diagram, class/index, terminal name, and current wire. Those eight queue definitions and bounds are at `tools/recipes/build_d1_v0.py:263-272`; `s1q` explains exactly why the missing named outputs block construction at `tools/recipes/build_d1_routeb_v0.py:1251-1257`. Building `VI.Get Errors` now would mostly rediscover the deliberately unwired loops.

Cheapest discriminating test: add four read-only snapshots inside the existing `resolve_ctlterms()` throwaway probe—immediately before and after moving ControlTerminal `#403`—using `panel_wiring("Z/dZ")`, `node_terms(#2222)`, `report_all("Wire")` membership for UID 730, and `wire_source_owner(730)`. If `Z/dZ` becomes bare while `#2222/#2276` were never moved, G1 is falsified without another 540-second build.

## Sources

(extract from answer)

## What was done with it

**G1 WITHDRAWN — full disposition in the opus arm of the same `-Dual` dispatch,
`archive/peer/2026-09-17-zdz-wirecut-opus.md`.** The wire was cut by the build's own S3-ct reparent of
`ControlTerminal #403 ('Z/dZ')` (`build_d1_routeb_v0_run3.log:163`), a measured consequence of moving a control
terminal, not by sink loss or Remove Bad Wires. No code was changed after this review: the session's hard stop
arrived (experiment imminent, LabVIEW released, no instrument access), so it is recorded for the next session.
