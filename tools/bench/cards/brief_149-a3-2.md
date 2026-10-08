---
card: 149-a3-2
status: current
date: 2026-10-08
---
# Brief 149-a3-2 - retry of 149-a3-1: fix the graph-plan DATA for the re-used wire uid 23807, then graph read, `load_by_vi`, Void census (PD363(b)(c))

Retry of 149-a3-1 (`retry_of_card`). Read `tools/bench/diag_c149_a3_1_facts.md` and the peer answer `archive/peer/2026-10-08-c149-a3-1-mkgraph.md`
(sec. 1 and 4) first. DONE and NOT repeated: s06 is adopted (`diag_c149_a3_1_adopt.log` 3/0, artefact 569ffbf5, `adopted_scratch.jsonl` 658fe5b9) and the
51-item expected file is written (`errorlist_expected_D1_ring_p4s06_20261008_174730.json` b47995c8, 5/0). Do not re-run either. The judgement
(PD363) has decided s06 is adopted; nothing is rebuilt, no second scratch, 569ffbf5 is never edited.

## The fault (our script, not LabVIEW)
`tools/bench/diag_c149_a3_1_mkgraph.py` (a names-only copy of a template that never ran) emitted `new_wires` with 15 uids and `deleted_wires = [23807]`.
The scratch log's D line counts 16 new wires because LabVIEW RE-USED uid 23807 (`kept_by_key`, `stagekit.py:1480-1481`: "one lost + one new").
The graph read's E5 (`graph.py:64-69`) requires every `deleted_wires` entry to be ABSENT from the file, and w23807 IS present in the saved s06
(`diag_c149_a1_3_wire.log` W1 PASS: source t5171 #5058, sinks t3173 #23166 and t10975 #10969).

## Steps
1. **Offline discriminating test FIRST (peer sec. 4, no LabVIEW, pure Python; copy to `diag_c149_a3_2_disc.py`, log `diag_c149_a3_2_disc.log`):**
   (a) from `tools/bench/diag_c147_p4s06v18_scratch.json`: `set(new) | {kept_by_key reuse_noted uids}` has 16 members and equals the D line's 16;
   (b) `real_end_rows` hold w23807 with source (5171, 5058) and sinks {(3173,23166),(10975,10969)};
   (c) E5's own expression (`graph.py:64`) run on the plan wire set twice: as written, and with 23807 moved from `deleted_wires` to `new_wires`.
   Quote all three. If (a) or (b) fails, or (c) passes in NEITHER variant, RETURN with the facts (no LabVIEW).
2. **Fix the DATA in the card-local copy only:** in a copy `diag_c149_a3_2_mkgraph.py` of `diag_c149_a3_1_mkgraph.py`, a kept_by_key re-used uid goes to
   `new_wires` and NOT to `deleted_wires` (the W gate then reads 16 == 16 honestly). No edit of `stagekit.py`, `graph.py` or any stage tool. Run it
   under bgrun; quote the gate lines and the new plan json path + md5 (`diag_c149_a3_2_graph_plan.json`).
3. **Fresh-instance load + graph read** with `diag_c149_a3_1_graph.py` copied to `diag_c149_a3_2_graph.py` (names/plan path only) ->
   `tools/bench/graph_ring_p4s06_<stamp>.json` + md5 + load MB. Run it under bgrun (`--material`), a LabVIEW card: background it and hold the turn.
   A gate that fails here is a RETURN with the failing gate line, no retry.
4. **`memory_model.json`: ONLY one `load_by_vi` entry** for 569ffbf5 from the measured load (`diag_c149_a1_2_memload.py` copied to
   `diag_c149_a3_2_memload.py`, names only). Key-by-key diff quoted; no limit, coefficient, MEMSTOP or X10 change.
5. **Void-type census (PD363(c)) - plain gscript reads, no edit verb, no `Is Broken?`, NOT the stagekit `discard_work` path (fp-63).** Model:
   `tools/bench/diag_c149_a1_3_types.py` / `_wire.py` (both ran plain gscript reads). On (i) the adopted s06 and (ii) a BYTE COPY of s05 3f9ac26b
   (copy the bytes first, never open the s05 original; delete the copy after). For every wire terminal whose type is Void or whose type string
   contains `Void`: wire uid, terminal uid, owner node uid / class / label, terminal name, type string. Write `tools/bench/diag_c149_a3_void_census.md`:
   both lists, the s06-only entries listed separately, counts. FACTS ONLY; no claim whether item 6 is among them.
6. **Invariants** (`diag_c149_a3_1_inv.py` form, before/after): stage tools, errorlist_check, s05 3f9ac26b, s04 95e408ff, s03 282301ca, bed 39511877,
   s06 569ffbf5 unchanged; memory_model differs by the one entry only; no byte copy left; handles recorded; `tasklist` LabVIEW count 0.

## Return conditions (no retry inside the card)
Step 1 (a)/(b) false or (c) fails in both variants; any gate of the graph read failing; an invariant md5 that moved; any step needing an edit verb or a
stage-tool edit. A peer (hypothesis) only if a gate FAILS.

## Report (`tools/bench/diag_c149_a3_2_facts.md`, <= 45 lines)
Step 1 results (a)(b)(c), the fix (file:line), plan json md5, graph json path + md5 + load MB, `load_by_vi` key-by-key diff, census counts + the s06-only
list head, invariants, handles, LabVIEW gone. `OPEN:` line. Facts only.
