# Brief 132-2 — real graph read of the P3b-1 bed (LabVIEW, READ ONLY)

Decision: PD264(b) (`docs/d1/INDEX.md`), PD274 (`docs/d1/ring-p3b.md:64`). The bed
`claudeDev\D1_ring_p3b1_20261002_060910.vi` (md5 `9d7bf28738b7c154280e5e7c2c9d4961`) is never edited or saved.
Card 132-1 runs beside you OFFLINE and edits `tools/stage_prerun.py`; you do not run stage_prerun.

## A — graph read (LabVIEW)
Read the bed's graph with the same reader that produced `tools/bench/graph_ring_p3a_20261001_190155.json`
(`tools/bench/diag_c125_graph_p3a.py`; copy it to `diag_c132_2_graph_p3b1.py`, change only the input path / output name)
→ `tools/bench/graph_ring_p3b1_<ts>.json`. Same JSON shape as the P3a graph (the `--rebase` reader expects it).
MEASUREMENT on the way (no extra LabVIEW act): LabVIEW private bytes right after the VI is loaded and after the full read
(the same meter the stage recipes log), so X10's base term for a stage starting FROM P3b-1 is measured, not assumed.
Bed md5 before and after; LabVIEW closed and verified gone.

## B — offline comparison (no LabVIEW)
Compare the real graph with the simulator's END graph of P3b-1 (`tools/bench/sim/ring_p3b1/`, last step): object / node /
terminal / wire counts, and the set of wires with a loose end on the nets of `#6810` (Image Out, error out) — list each
loose-end wire uid with its connected terminal on both sides. This answers 131-6's open point (a swap inside the loose-end
class would be invisible to the class totals). Report differences as facts; do not decide whether they matter.

## Return
`result/1`: graph file path + md5, the two memory readings, the count table real vs sim, the loose-end wire lists, bed md5
before/after, LabVIEW gone. Return at the first unexpected result.
