# D-3b of M3a-3b — remove the c83 confound, then land Row D if it is removed

RECIPE: `tools/recipes/build_d1_m3a3b_d3b.py` (699 lines, ASTCHECK OK: 0 `%`-arity mismatches over 105
sites, 0 duplicate gate names, 0 `remove_bad_wires` call sites, 4 guard rebinds, no write naming the bed).

## What this dispatch does

**STEP A — the measurement.** On a dated scratch COPY of the bed `claudeDev\D1_s3b_m3a3_20260922_081056.vi`
(md5 `33ef524e0b6b193a158c9221474c68e3`, 306,951 B), delete wire **7506** with `del_wire` and **nothing
else**, then ask whether `FlatSequenceInnerTunnel #7468` still exists and still yields its `Left Terminal`
`#7488`, whether that terminal is BARE, and whether the inner wire **7448** on the `Right Terminal`
`#7471` survives. Decided by the UID ECHO (`uid_back == 7468`, `term_a_uid == 7488`), never by an empty
error column (Pre-decided 125), with c81's never-allocated-uid negative control (999983) run on the same
bytes to prove the echo still catches a ghost through this reader.

**STEP B — the landing, the only branch.** If `#7468` resolves and `#7488` comes back BARE, connect the
NEW loop's shift-register OUTER terminal (`WhileLoop #23032`, `Nodes[21]`, `Terminals[1]`, uid `#23906`,
owner `RightShiftRegister #23868`) into that bare terminal with the already-built
`claudeDev\OpFsInnerTunnelConnect_v1.vi` (md5 `5b4e5f0fb3baae96361c33ce81bcd7b1`), assert GATE S on the
scratch, and only then repeat the identical sequence FROM THE BED into a new file
`claudeDev\D1_s3b_m3a3b_<stamp>.vi` with the ordered idempotent second pass of Pre-decided 106.

GATE S: (a) the FSIT LeftTerm's net has EXACTLY ONE source terminal whose OWNER is `RightShiftRegister
#23868` (`OpWireSource_v5`; owner identity decides, never a count — Pre-decided 117 as corrected by 120);
(b) `#4334` is OFF that net; (c) PD85 violations 0; (d1) `Wire.Is Broken?` False on that wire and the op's
`UID 2` IS that wire; (d2) see the constraint below; (e) the FSIT `Right Terminal` `#7471` still carries
wire 7448.

## The constraint that shapes the whole file

`remove_bad_wires_scripted` (and any Remove Bad Wires call) is **FORBIDDEN** everywhere in this dispatch,
on scratch copies and on the artefact alike. It is the suspected cause of c83's `error 1055` (every c83
deleting cell called it ONE LINE after `del_wire` —
`tools/bench/diag_c83_connect2x2_r2.py:449-450`; c82's end-to-end arm did the same at
`tools/recipes/build_opfsinnertunnelconnect_v0.py:775`) and it is on record DELETING A TUNNEL
(`archive/2026-09-17-status-d1-route-b-2.md:44-46`), which is why it is refused as a rule-1a hazard at
`docs/cycle27-plan.md:1860-1862`. The ban is enforced MECHANICALLY: at import the recipe rebinds
`gscript.remove_bad_wires_scripted` and `gscript.remove_bad_wires` to a function that RAISES, and gate H7
reports whether the guard was ever tripped.

**Consequence, stated rather than argued away:** GATE S(d2) — "the diagram-wide broken-wire count is not
higher than the pre-delete baseline" — has **no non-mutating reader in this fleet**. The only construction
on disk is the Remove-Bad-Wires count delta (`tools/bench/broken_probe2.py:12`), forbidden here; a
per-wire `Wire.Is Broken?` 6371004 walk is impossible because no standalone reader op exists
(`docs/toolkit-capabilities.md:68`) and reading `Is Broken?` PERTURBS the target
(`docs/NAMES.md:984-995`), over ~1,9xx wires. So d2 is reported as **NOT MEASURED** and a weaker
non-mutating substitute d2' is gated instead (Wire-uid census: nothing lost, at most one gained;
`ExecState` non-regression).

## What is settled and is NOT re-tested

* `Terminal.Connect Wire` 6349C03 **MERGES** nets — c84, 4/4 cells, and the failed-prediction review
  `archive/peer/2026-09-22-c84-replace-vs-branch.md` §2. Connect-with-the-wire-alive is DEAD for Row D.
* Connecting **two BARE terminals CREATES** a wire — c83's trivial-VI cells, 4/4.
* `UID to GObject Reference.vi` resolves a TERMINAL uid — c81, `tools/bench/diag_c81_uidref.log`.

## What already exists and is imported rather than rebuilt

`build_d1_m3a3b_d3` (`fsit_call`, `fsit_read`, `gate_s` — called only with `probe_bad=False`, the branch
that never touches Remove Bad Wires), `build_opfsinnertunnelconnect_v0` (`md5`, `PINS`, `BED`, `del_wire`,
`purge_junk`, `resolve_triple`, every topology constant), `build_opfstunnelterm_v2.read_tunnel`,
`build_opconnectfromwire_v0.wire_source_owner`, `build_d1_m3a1` (`print_walk`, `pd85_violations`,
`node_census`, `new_nodes`, `node_view`, `delete_by_uid`), and `OpFsInnerTunnelConnect_v1.vi` itself.
**Nothing new is built: no op, no verb, no device, no third configuration.**

## Not done, deliberately

No Remove Bad Wires; no tunnel re-creation; no `Wire.Disconnect Terminal` 6370C0D (Pre-decided 123); no
third op; no rebuild of v1; the bed is never opened for EXECUTION and is md5-pinned at entry and exit; the
artefact is never run and never cold-loaded (34(f)). Rig is 조립: no motor, no ASI, no camera.

## Pre-decided

* The bed is broken BY DESIGN — `ExecState` is RECORDED, never a criterion (Pre-decided 89/97).
* Owner identity decides every source question, never a wire count or delta (117 corrected by 120).
* `Auto Route?` TRUE; c84 measured TRUE and FALSE identical on the merge cell.
* A negative STEP A is a FIRST-CLASS RESULT: save nothing, delete every scratch, report, stop.
