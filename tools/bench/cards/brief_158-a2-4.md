---
card: 158-a2-4
status: current
date: 2026-10-10
---
# Brief 158-a2-4 (assignment 158-2) - OFFLINE: gate mutation table on the stored ring graph 6716c499 (steer debate:plan-overall-02, PD384(d), `docs/d1/ring-p5.md:277-286`)

No LabVIEW, no gate / tool / recipe / plan / pred / licence / hook edit. New files only: `tools/bench/mutation_table_p5.md`,
`tools/bench/mutation_table_p5.json`, `tools/bench/diag_c158_a2_4_*`. Read `docs/script-writing.md` (inputs and calls, no pasted copies), then
`docs/d1/ring-p5.md:277-286`, and `tools/bench/diag_c158_a2_3_facts.md` + `diag_c158_a2_3_measure.py` (it already builds graphs from
stored rows and calls the D / TD / PB / cdiff / E1 functions by CALL: reuse its calls, do not copy blocks).

## What to build
Take the stored graph `tools/bench/graph_ring_p5s01_20261009_125622.json` (md5 6716c499) and apply a FIXED mutation list, each mutation
on its own copy IN MEMORY (the file is never written):
M1 a wire dropped; M2 a wire re-sourced (same sink, another source terminal); M3 a node moved to another diagram; M4 a tunnel renamed with
owner and connectivity unchanged; M5 uids renumbered with connectivity unchanged; M6 a constant's value changed. Several instances per
kind (at least 3 distinct targets each, chosen by a stated deterministic rule, e.g. first / middle / last eligible row).
Score each mutated graph against the EXISTING gates by calling them (computation_diff, D / TD / PB, E1 edge comparison, invcheck - whichever
of these can be called on a graph pair offline; list any gate that cannot be called offline with the reason, file:line).
Class each mutation: **invariant** (changes computation, save, or safety: M1, M2, M3 when it changes a connection, M6) or **representation**
(M4, M5, M3 when connectivity is unchanged). State the class rule once, before the rows.

## Table (`mutation_table_p5.md`, <= 60 lines + the json with every row)
Columns: id, mutation, class, each gate's verdict (BLOCK / PASS / n.a.), net verdict. Then two lists, as the steer asks:
(1) rows where an INVARIANT mutation passes every gate (a gap); (2) rows where a REPRESENTATION mutation blocks (a false block).
Facts only, each row reproducible from the json. Do NOT propose or make gate edits; the gate changes are judged from the table by the
judgement session. `OPEN:` line per unresolved thing. Failure budget 2.

## Report `tools/bench/diag_c158_a2_4_facts.md` (<= 30 lines)
Counts per class and per gate, the two lists, gates not callable offline (file:line), md5 of the table files, md5 of graph 6716c499 before
and after (unchanged).
