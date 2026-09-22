# D-2 of M3a-3b — build, SAVE and EXERCISE `OpFsInnerTunnelConnect_v0.vi`

Recipe under review: `tools/recipes/build_opfsinnertunnelconnect_v0.py`
Decision already taken by the judgement session: `docs/cycle27-plan.md` Pre-decided 127 (with 124/125/126
for why). The CHOICE of op is NOT open in this dispatch; what is open is whether any of the work below has
already been done, measured or refuted in this project's own files.

## What is being built

`OpFsInnerTunnelConnect_v0.vi` in `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev`,
as the SMALLEST possible edit of the existing `OpConnectFromWire_v0.vi`:

* **Only the source-half acquisition changes.** Where `OpConnectFromWire_v0` derives a terminal from
  (`wire_uid`, `Wire.Terms[]` 6371003, index), the new op derives it from
  (`fsit_uid` → `UID to GObject Reference.vi` → `To More Specific Class` seeded
  `VI Server:FlatSequenceInnerTunnel` → **`Left Terminal` 1C3A9000** = the `LeftTerm` output).
  That is the reading half of `OpFsInnerTunnelTerm_v0.vi`, already on disk and already measured
  (Pre-decided 109/118).
* **Everything else keeps its role exactly.** The Invoke still carries `Terminal.Connect Wire` 6349C03,
  still sits on the terminal named by the (diagram index, `Nodes[]` index, `Terminals[]` index) TRIPLE,
  and still receives the other terminal as `Wire Source` — the binding the machine already accepted
  (`tools/bench/c80_rowd_routeA_r2.log:244`, Pre-decided 119).
* **LEFT terminal only.** No side selector, no second property, no extra inputs beyond `fsit_uid` +
  the index triple + the house error/status convention the sibling ops use.
* **One addition beyond the swap:** a `VI Server:GObject` + `632A813` (`GObject.UID`) property node
  branched off `LeftTerm`, with an indicator. Pre-decided 125 makes the uid echo a RULE for every
  uid-addressed op (`diag_c81_uidref.log:85`: a never-allocated uid returned a DIFFERENT previously
  resolved object with every error column empty), and Pre-decided 127's gate (3) asks for that value.

## The build steps (each one a named gate in the recipe)

B0 donor `OpConnectFromWire_v0.vi` on disk at `ExecState` 1, md5 recorded (never written).
B1 copy → the new op; the source ladder found BY WIRE TOPOLOGY from the Invoke's `Wire Source`
   (Invoke ← Index Array ← `Wire.Terms[]` PN ← TMSC ← `UID to GObject Reference.vi`), never by uid;
   a stale-in-memory guard asserts the copy carries none of this build's own additions.
B2 delete the Invoke's `Wire Source` net; that terminal reads 0.
B3 delete the Index Array and the `Wire.Terms[]` property node; the TMSC's `target class` and
   `specific class reference` both read 0.
B4 `build_property("VI Server:FlatSequenceInnerTunnel", 1C3A9000)` → one node whose single data output
   is read back and must be `LeftTerm`.
B5 `create_control` on that node's `reference` → exactly ONE new control = the FSIT-typed SEED; its own
   wire deleted; the seed re-wired to the TMSC's `target class` (the shape
   `build_opfstunnelterm_v2.py:617-636` uses).
B6/B7 TMSC `specific class reference` → the FSIT node's `reference`; `LeftTerm` → the Invoke's
   `Wire Source`.
B8 `build_property("VI Server:GObject", 632A813)`; `LeftTerm` BRANCHED into its `reference`; an
   indicator on its `UID` output and one on each new `error out`.
B9 auto error handling OFF; `ExecState` 1; `save()` by script; labels JSON; donor md5 unchanged.

## Acceptance — all four, each printing the value it compared (Pre-decided 127)

1. `ExecState` 1 on the SAVED op, re-read after the save.
2. **20 consecutive calls leave LabVIEW's handle count flat ±100** (CLAUDE.md reference hygiene), on a
   dated scratch copy of the bed.
3. A call with `fsit_uid` 7468 returns the LeftTerm reference whose OWN uid echoes **#7488**.
4. ONE end-to-end exercise on a DATED SCRATCH COPY of the bed
   `claudeDev\D1_s3b_m3a3_20260922_081056.vi` (md5 `33ef524e…`, 306,951 B): delete wire **7506**; call
   the op with `fsit_uid` 7468 and the index triple for the NEW loop's shift-register OUTER terminal
   (`WhileLoop #23032`, `Nodes[21]`, `Terminals[1]`, resolved LIVE with a uid echo); then assert with
   `OpWireSource_v5` that the net's SOURCE TERMINAL OWNER is **`RightShiftRegister #23868`** and that
   **`#4334` is OFF the net**, PD85 violations 0, `Wire.Is Broken?` False. Owner identity decides —
   never a wire count, never a wire delta (Pre-decided 117 as corrected by 120). Scratch deleted,
   nothing saved from it.

## Constraints this recipe operates under

* The bed is READ-ONLY: md5-pinned at entry AND exit, never opened for execution.
* Rig state 조립: no motor, no ASI, no camera. VI Scripting and COM only.
* LabVIEW restarted before the batch; handles reported before/after; refs opened/closed/live reported.
* One `bgrun` for the whole thing; files patched with Edit/Write, never a heredoc.
* A failed gate is the dispatch's result: no improvised second route, no variant op.

## What the reviewer is asked

Has any of this already been built, measured or refuted in this project's own files — in particular:
an op that reaches a `FlatSequenceInnerTunnel` terminal AND writes a wire; a `Terminal`-seeded or
`FlatSequenceInnerTunnel`-seeded connect; a uid-echo indicator on a connect-class op; or a measurement
that says this swap cannot work? Cite `file:line`.
