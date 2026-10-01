# Brief 125-4 — Flat Sequence creator (FIRST), then the wire-joint diff for the 55th item (LabVIEW)

Decisions: `docs/d1-loop12-17-split-plan.md` Pre-decided **252** (this cycle), **251(c)(d)**, **248(c)**, **246(c) A1**.
Previous card: `tools/bench/cards/result_125-2.json` (P3a graph `tools/bench/graph_ring_p3a_20261001_190155.json`; the
P3a case is `#22694`, frames `27219` / `27232` — check which is False). Bed `claudeDev\D1_ring_p3a_20261001_180540.vi`
(md5 `4dfa44aac8fb32f706b3eb792ee7d3cc`) and P2b bed `claudeDev\D1_ring_p2b_20261001_140658.vi` (md5
`652b1447ebbda761a7d5ba36455a0fa1`) are NEVER saved over; building happens on BYTE COPIES. Scripts <= 120 lines on stagekit.

## STEP B (first) — Flat Sequence creator, on a P3a byte copy
1. Run the written probe `tools/bench/diag_c125_fsmethods.py` (125-2 wrote it, not run) to MEASURE the FlatSequence
   frame-add method (the gemini fact answer, unsourced: `Add Frame` with inputs Frame Index / After?, returns a frame
   reference; `archive/peer/2026-10-01-c125-2-flatseq-addframe-gemini.md`). Record the method id and its terminal names.
   If no such method can be invoked, the alternative is a donor VI holding a 3-frame Flat Sequence + `struct_copy_nested`
   (the `case_wired` / `DonorCase_v0` pattern) — your choice, state it.
2. Create a Flat Sequence with 3 frames inside the **False (new-frame) frame** of case `#22694`. Read back: frame count,
   left-to-right order, per-frame diagram uid, census delta (classes created).
3. Wire a frame-1 node output to a frame-2 node input through a sequence tunnel (any two cheap primitives / constants);
   read back the tunnel class and `Is Broken?` False.
4. Deliver: the gscript function, a census sample in `census_samples.json`, a `tools/bench/scratch_verify/` record. A NEW
   op VI gets its hygiene record (>= 2,000 consecutive calls, 0 errors, handles flat ±100, `tools/bench/op_hygiene/`).
5. In the result, list what the stagexec route / stagesim model need: arguments, returned uids, created classes, how
   frames are named/addressed (index), and how a sequence tunnel shows in a graph read.

## STEP C (second) — wire-joint diff, READ-ONLY, measurement only (no prediction on the count)
The review (`archive/peer/2026-10-01-c125-2-loose-hyp.md` §1) names the existing reader `gscript.wire_joints`
(`OpWireJoints_v1`, hygiene 2,066 calls). For each net that P3a's stage touched — w3747 (BufNum → `Equal?` branch, sinks
27084/27161), the register right-in from BufNum, w27331 (`case_frame_wire` branch), and the `connect_term_uid` nets across
the case border (from `stage_d1_ring_p3a.log`) — read the joints on BOTH the P2b bed and the P3a bed, and list every
segment end that has no terminal on it. Report the nets where P3a has an extra free segment end versus P2b (uid, the
end's position, which plan row made the net). Zero, one or several — all are results; report facts only.

## Rules
- No stage recipe is run; nothing saved over either bed; scratch copies deleted or md5-recorded; LabVIEW closed and gone.
- STEP C runs even if STEP B fails, provided LabVIEW is in a clean state (STEP C is read-only on the beds).
- Return at the first unexpected result in STEP B (finish the step, close LabVIEW, record facts), then still do STEP C.
- A failing log → Jev ladder row; an owed hypothesis review is dispatched (`-Agent claude -Role hypothesis`).
