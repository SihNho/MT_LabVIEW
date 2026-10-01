# Brief for card 124-4 — retry of 124-1: build OpConnectTermUid_v0, then prove P3a's counter crossings on a scratch (cycle 124 judgement)

Retry of `tools/bench/cards/result_124-1.json` (FAIL 6/1). Jev row: `diag_c124_opconnecttermuid.log | our-script-bug p=0.854 |
patch the script and rerun` — applied, no new diagnosis. Card 124-3 (`result_124-3.json`) found the second gap this card covers.

## Decisions (judgement, cycle 124)
1. **Fix the script bug in the tool, precisely:** `gscript.create_primitive_nested`'s owner check (`tools/gscript.py:4726`)
   accepts class `TopLevelDiagram` when `diagram_uid` IS the VI's top-level diagram, and nothing else changes. Then rebuild
   `claudeDev\OpConnectTermUid_v0.vi` with `tools/bench/diag_c124_opconnecttermuid.py` (bench location ACCEPTED — op builds
   have lived there since c100/c122) and its hygiene record (≥ 2,000 calls, 0 errors, handles flat ±100).
2. **`ConditionalTunnel.Link Input Tunnel And Wire` is NOT used** — it wires every unwired frame and persists as a tunnel
   property; we want exactly one wire in exactly one frame.
3. **`connect_term_uid` is the general writer** and also answers 124-3's open (a): a shift register's inner face is not a
   Nodes[] entry, but it IS a terminal with a uid. Measure it across a case border; do not re-plan P3a around it.

## Scratch proof (one LabVIEW run on a byte copy of `claudeDev\D1_ring_p2b_20261001_140658.vi`, ≤ 120-line stagekit script)
This is P3a's counter subgraph (PD246(c) A3/A5), built with the functions P3a will use:
- On While `#637`: a new shift register (existing `add_shift_reg`), initialised from I32 0 (`DonorSRInit_v0` `#248`, route `const_sr`).
- On body `639`: a fresh `Equal?` and a `case_wired` case; `Increment` in the False frame.
- **R1** `connect_term_uid`: register LEFT inner face → `Increment.x` (False frame) — read back: the input tunnel created
  (class, uid, one inner face per frame), wire `Is Broken?` False.
- **R2** `connect_term_uid`: `Increment.x+1` (False) → register RIGHT inner face — read back the output tunnel likewise.
- **R3** `case_frame_wire` in the True frame: input tunnel inner face → output tunnel inner face (frame index read back, not assumed).
- **R4** `case_frame_wire` in the False frame: a SECOND sink on the input tunnel's inner face (a fresh `Quotient & Remainder`.x) —
  read back whether LabVIEW branched the existing wire.
- Per-frame read-back of every inner-face uid; `Is Broken?` False on every new wire; Invoke +0 (the purge in the two connect
  paths, now on LabVIEW); census samples for `connect_term_uid` (register ends) and `case_frame_wire` in
  `tools/bench/census_samples.json`; a `tools/bench/scratch_verify/` record. Bed md5 unchanged; scratch deleted; LabVIEW gone.

## Then
The stagexec self-test (not run by 124-1) and the self-tests 124-1 ran stay green. Return at the first unexpected result; R1–R4
are measurements — record what LabVIEW did even when it differs from the expectation, finish the run, return.
