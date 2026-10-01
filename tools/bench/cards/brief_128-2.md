# Brief for card 128-2 (cycle 128 judgement) — the detail behind the card's short pass lines

Plan: `docs/d1-loop12-17-split-plan.md` Pre-decided 258(c), 259(c), 260(c). The P3b ring-buffer build step needs the
U9 guard: `IMAQ Copy` error out → "did it fail?" → −1 (failed/skipped) or BufNum (ok) → the slot's `Num(i)` element.
127-5 found no Select / Unbundle-By-Name donor, but logged no per-file node counts.

## (A) the owed hypothesis review — do it FIRST, in the background while (B) runs
`guard_peer` blocks every build until 127-5's failure has an adversary review. Dispatch
`peer.ps1 -Agent claude -Role hypothesis -TimeoutSec 780` with a `-TaskFile` that NAMES `diag_c127_5_errsel.log` and
`diag_c127_5_errsel.py` and asks it to ATTACK the claim "no Select / Unbundle By Name donor is reachable over our
scripting path". Framing for it to attack: the census may have searched by the wrong class name (a primitive such as
Select may be VI-Server class `Function`/primitive with a name or PrimIndex, not a class called `Select`), and per-file
row counts were not logged, so empty reads look like absences. Wait for ANSWERED, archive, annotate.

## (B) node-class census of donor candidates (read-only)
Files:
1. the bed graph already on disk `tools/bench/graph_ring_p3a_20261001_190155.json` (offline);
2. a BYTE COPY, made inside claudeDev, of the ORIGINAL main VI `Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi`
   (rule 1: never open the original at its own path, never save it; Don't Save every prompt naming an original);
3. byte copies of up to 8 shipped vi.lib error-handling VIs (never edit vi.lib).

Per file: total node count; count per class name; for every Function/primitive-like node its name and PrimIndex if
readable; Select present? (uids); NamedUnbundler/Unbundler wired to an error cluster present? (uids). A file read with
0 nodes is reported as an EMPTY READ, not as "no node".

## (C1) scratch form 1 — Unbundle By Name + Select
New minimal VI in claudeDev. Error cluster source (HARNESS_copyloop's `IMAQ Copy #240` error out as in 127-5, or any
error-out terminal) → `Unbundle By Name` (`status`) → `Select` s; t = I32 −1 constant; f = an I32; output → I32 sink.
Nodes created by `create_primitive_nested(donor=...)` from whatever (B) found. Per create: census, every terminal name +
`term_class`. Per wire: `Is Broken?`. Unbundle's element name read back. If (B) found no donor for a node, record C1 as
NOT ATTEMPTED for that node with the reason — do not invent a route.

## (C2) scratch form 2 — error cluster on a Case Structure selector
Second scratch. Error cluster → the SELECTOR of a new Case Structure (the case-structure create route P3a already used).
Record the frame names after the wire (expected "No Error"/"Error" or similar) and the selector's `Is Broken?`. In one
frame an I32 −1 constant → output tunnel; in the other an I32 input → the same output tunnel → I32 sink. Census,
terminals, `Is Broken?` per wire.

## Close
ONE Error List read at the end per scratch (PD258(a)). Census samples + one `tools/bench/scratch_verify/` record per
form. Delete scratches and byte copies, except a donor file you register (name it `DonorErrSel_*.vi`, report path +
uids). LabVIEW closed and verified gone.

## Time
(A) ~12 min in the background during (B); (B) ≤ 15 min; (C1)+(C2) one launch ≤ 20 min including the Error List reads
(~7 min each). The 60-min backstop refuses new bgruns after that. Return at the first unexpected result.
