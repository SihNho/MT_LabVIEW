---
type: facts
status: current
date: 2026-10-10
card: 159-a3-1
---
# 159-a3-1: offline attribution of the 11 extra Error List items of P5-2a 94ffff94 (EL 56) vs P5-1 7f2582ae (EL 45)
Script `tools/bench/diag_c159_a3_1_attrib.py` (allterms.join_wires/severed, vigraph.build4/wire_terminals, errorlist_check.norm_ocr),
log `diag_c159_a3_1_attrib.log` RESULT PASS 6/0; data `attrib_c159_p5s02a.json`. Input md5 pins all equal (gate K). No LabVIEW.
## Graph recompute (join_wires + Wire objs, severed)
| | wires | termless | src-only | sink-only | severed | sourceless tunnels |
|---|---|---|---|---|---|---|
| P5-1 | 2061 | 22 | 2 (10103, 12256: base, loop 637) | 0 | 24 | 0 |
| P5-2a | 2071 | 23 | 4 | 6 | 33 | 2 (#5204, #10404) |
New severed (by endpoint term uids) 9, RESOLVED 0. Every new one is a P5-1 wire of #376 (or #3052) cut by the step-1 move (A10 mv_376 / A11 mv_3052).
## Per Error List class (class <- graph shape)
| class | P5-1 | P5-2a | new (graph) | resolved | graph objects |
|---|---|---|---|---|---|
| has no source | 0 | 5 | 5 | 0 | sink-only wires 4337, 10362, 24264, 24300, 25232 |
| undirected tunnel | 0 | 2 | 2 | 0 | LoopTunnels #5204, #10404 (no source terminal; P5-1 had one) |
| While input -> SubVI input | 0 | 1 | 1 | 0 | sink-only wire 9636 (sinks: #10404 outer + #6384 SubVI) |
| not connected to anything | 22 | 23 | 1 | 0 | termless wire 10394 |
| loose ends | 21 | 23 | 2 | 0 | source-only wires 24285, 24312 (count-level match, see OPEN) |
| unwired input / two types | 1 / 1 | 1 / 1 | 0 | 0 | - |
## The 8 new-class items
| item | class | object | source (P5-2a) | sinks | frame | clearing action | step |
|---|---|---|---|---|---|---|---|
| 1,2,4,6,50 | no source | w24264 | none (P5-1: #376 'error out' 3934) | RSR #24083 inner 24139 | 23405 (While 23041) | A32 w_gr | 2 |
| (set) | no source | w24300 | none (P5-1: #376 'total data array out' 3954) | RSR #24150 inner 24235 | 23405 | A39 w_hr | 2 |
| (set) | no source | w10362 | none (P5-1: #376 'file progress' 5704) | #5204 inner 8776 | 23405 | A70 w_k3f (term 8776) | 3 |
| (set) | no source | w25232 | none (P5-1: #376 'file number to append out' 5739) | #10404 inner 24342 | 23405 | A80 w_k4f (term 24342) | 3 |
| (set) | no source | w4337 | none (P5-1: #5204 outer 9631) | #2048 'length' 3182, #5204 outer 9631, #6384 'actual # data points' 6480 | 686 | A70 w_k3f (via #5204) | 3 |
| 7,8 | undirected | #5204 | no source term | outer 9631 (w4337), inner 8776 (w10362) | 23041 border | A70 w_k3f | 3 |
| (set) | undirected | #10404 | no source term | outer 24363 (w9636), inner 24342 (w25232) | 23041 border | A80 w_k4f | 3 |
| 49 | While->SubVI | w9636 | none (P5-1: #10404 outer 24363) | #6384 'file # to append' 6511, #10404 outer 24363 | 686 | A80 w_k4f (via #10404) | 3 |
Pairing: item 49 is exact (only sink-only wire with exactly {LoopTunnel outer, SubVI} sinks). Items 1,2,4,6,50 and 7,8 match their
object SETS by count; which item is which object is not readable (no uid route; `bd_024222_after1.png`, `bd_025044_after49.png` show only a
selected dashed wire with a red X near the bottom edge, no label or node). Every object in each set has an A24..A80 action, so the item is
attributed whatever the pairing; nos 1,2,4,6,50 clear at step 2 (two of them) or step 3 (three).
## Net +3 same-class items (no RESOLVED severed wire in the graph, so net = gross)
- not connected +1: termless wire 10394 = P5-1 w10394 #3052 'File # Saved' 3060 -> #376 'saved file refnum' 5772 (frame 23405). Step 1's
  A13 w_ref re-made the pair as NEW wire 11774 on case frame 31506; the old segment stayed behind with no terminal. NO A24..A80 action
  deletes or wires it (plan has no delete_wire 10394): UNATTRIBUTED; carries no data (no terminal).
- loose ends +2: source-only stubs 24285 (LSR #24133 'error out' 24190, P5-1 sink #376 'error in' 5683) -> A28 w_gl, step 2;
  24312 (LSR #24187 24288, P5-1 sink #376 'total data array in' 5782) -> A35 w_hl, step 2.
## Review hypothesis (archive/peer/2026-10-10-c158-a3-2b-el56.md) tested
- K3/K4 re-feed #5204/#10404: SUPPORTED by the graph (both lost their only source terminal; A70/A80 wire their inner terms 8776/24342).
- A48 / #376 'frame index' 5763: no new item touches it (consistent with the review).
- Falsifier ("a new-class object outside RSR 24083/24150 inner, #5204/#10404, wires sinking only into #2048/#376/#6384"): not met by the
  8 objects. The review's "remnant no later action re-feeds" exists, but in the same-class set: termless w10394.
- Step-1 move pattern (graph): #376 inputs from LSRs kept a source-side stub (24285, 24312); #376 outputs kept the sink-side stub
  (24264, 24300, 10362, 25232); tunnel sources #24357/#24361/#25223 kept no stub (25235 unwired in P5-2a; 24360/24367 re-wired by A19/A22).
OPEN: w10394 (termless, not-connected item) is cleared by no A24..A80 action - add a delete / Remove Broken Wires, or carry it as owed?
OPEN: whether A28/A35/A32/A39/A70/A80 (connect onto a terminal already carrying a stub wire) MERGE the stub or leave it is not measured;
the 24360/24367 precedent ends with one ok wire each, but their pre-A19/A22 state was not read.
OPEN: loose-end class vs graph shape is not 1:1 in the base (21 items vs 2 source-only wires); the +2 match is by count.
ATTRIBUTED 8/8 (5 + 2 by class set, 1 exact); NET3 explained 3/3 (1 UNATTRIBUTED to an action: w10394)
