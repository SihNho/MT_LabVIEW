# D-3 of M3a-3b — `OpFsInnerTunnelConnect_v1.vi` (roles exchanged) and the missing cell

Recipe under review: `tools/recipes/build_d1_m3a3b_d3.py`
The judgement session has already taken the route decision after reading the c83 2×2; it is NOT open in
this dispatch. What is open is whether any of the work below has already been built, measured or refuted
in this project's own files.

## What is being built

1. **`claudeDev\OpFsInnerTunnelConnect_v1.vi`** — `OpFsInnerTunnelConnect_v0.vi` (md5
   `50a1e58a4825c2ce030ed9a41e204931`, never modified, never deleted) with **the two Invoke feeds
   EXCHANGED**: the `Terminal.Connect Wire` 6349C03 Invoke sits on the FSIT `LeftTerm` (uid →
   `UID to GObject Reference.vi` → `To More Specific Class`(FlatSequenceInnerTunnel) → `Left Terminal`
   1C3A9000), and the terminal named by the (diagram, `Nodes[]`, `Terminals[]`) INDEX TRIPLE is passed as
   `Wire Source`. v0's repaired error path is kept (the Invoke's OWN `error out` reaches `error out 7`),
   and `Auto Route?` is exposed as a front-panel control.
   The construction is not new: `tools/bench/diag_c83_connect2x2_r2.py:340` `make_swap` already built this
   exact swap as a SCRATCH and it was legal (`diag_c83_connect2x2_r2.log:36-46` — nets w572 and w1337
   exchanged, the two other consumers `#241.reference` / `#187.reference` re-branched, Remove Bad Wires
   removed 0, ExecState 1). This recipe re-cuts it against the LIVE topology so it can be SAVED as v1.

2. **The measurement nobody has run**: the same op called with wire **7506 LEFT ALIVE** — i.e. the Invoke
   on the SINK terminal while that sink is still wired. Every wire-alive cell so far (R0/R0b) put the
   Invoke on the SOURCE terminal and BRANCHED; every swapped cell (R3/R4) had 7506 deleted first and
   returned `error 1055` because the deletion makes `#7468` unresolvable.

3. **If, and only if, a cell passes**: Row D landed as a NEW file `claudeDev\D1_s3b_m3a3b_<stamp>.vi`,
   built from the bed `claudeDev\D1_s3b_m3a3_20260922_081056.vi` (md5 `33ef524e…`, 306,951 B), which stays
   byte-unchanged.

## The gates

B1–B5 build v1: the copy at ExecState 1 with both Invoke feeds wired → both nets deleted → the two crossed
feeds + every other consumer re-branched, each verified by the SAME wire uid on both ends → Remove Bad
Wires removes 0 (so the crossed feeds are not type-broken) → `Auto Route?` control → ExecState 1 → script
save → ExecState 1 RE-READ → labels JSON → the donor v0's md5 unchanged.
G2 20 consecutive calls leave the handle count flat ±100 (regression check against the S0 baseline
`docs/toolkit-capabilities.md:460-478`; private-bytes drift reported beside it per `:484-485`); the junk
`Invoke` rate is measured and purged.
G3 both uid echoes on every call: `uid_back` == 7468 (input side, Pre-decided 125) and `term_uid` == 7488.

**GATE S**, per cell (S-T `Auto Route?` TRUE, S-F FALSE), each on its OWN dated scratch copy of the bed
with 7506 alive, each printing the value compared:
(a) the FSIT `LeftTerm`'s net has EXACTLY ONE source terminal and its OWNER is `RightShiftRegister #23868`
    (`OpWireSource_v5`; owner identity decides, never a wire count or delta — Pre-decided 117 as corrected
    by 120);
(b) `#4334` is OFF that net;
(c) PD85 violations 0 on the walk;
(d) `Wire.Is Broken?` False on that wire, AND the diagram-wide broken-wire count is not HIGHER than the
    same count on the bed's bytes before the call. The count is taken as
    `wires before − wires after Remove Bad Wires` (`gscript.remove_bad_wires_scripted`, VI method 410),
    which MUTATES — so the baseline runs on its own byte-identical control copy that is then discarded,
    the cell's number is taken as that scratch's last act, and on the artefact the probe runs on a
    THROWAWAY COPY OF THE SAVED FILE. The bed is broken BY DESIGN, so absolute `ExecState` is not a gate.
(e) the FSIT `Right Terminal` `#7471` still carries its inner wire 7448 (the Row C lesson — a dropped
    consumer is a silent failure).
Step 3 re-asserts (a)–(e) on the artefact plus the ORDERED IDEMPOTENT SECOND PASS of Pre-decided 106
(`wire_delta` 0 on an identical second connect, identity read on THAT pass).

## Constraints

* The bed is READ-ONLY: md5-pinned at entry AND exit, never opened for execution.
* `OpFsInnerTunnelConnect_v0.vi` is never modified or deleted; wire 7506 is never deleted anywhere.
* Rig 조립: no motor, no ASI, no camera. VI Scripting and COM only. LabVIEW restarted first.
* One `bgrun`, one notification; handles before/after; refs opened/closed/live; every scratch deleted.
* If NEITHER cell passes GATE S: nothing is saved, and the run stops. No third configuration is
  improvised, no terminal is removed from a net, no tunnel is re-created, `Wire.Disconnect Terminal` is
  not touched — those are judgement's and none is authorised.
* Save route: script when `ExecState` is 1, else `save(allow_broken=True)` → `gui_save`, the approved
  broken-intermediate route (CLAUDE.md §3 item 6, user 2026-09-22).

## What the reviewer is asked

Has any of this already been built, measured or refuted in this project's own files — in particular:
a SAVED op with the connect roles exchanged (as opposed to c83's scratch); a call of any connect op onto
an ALREADY-WIRED sink terminal on this VI or any other, and what it did; a diagram-wide broken-wire count
already implemented somewhere other than `remove_bad_wires_scripted`; a measurement that already says the
swapped-with-wire-alive configuration cannot work; or an existing artefact that already lands Row D?
Cite `file:line`.
