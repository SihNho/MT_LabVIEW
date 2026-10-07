---
type: facts
status: current
date: 2026-10-07
---
# Card 145-a1-2 facts: SQ1 row corrected, s04 scratch FULL PASS 24/0, Error List 58 != predicted 60 -> RETURN, NOT adopted

## Plan fix (step 2) `tools/bench/prep_c145_2_fix.py`
- Run a `prep_c145_2_fix.log` rc=1 (16/1): my gate A compared non-SQ1 addr_pos rows whole; owners of TL1/TN1 moved. Review
  `archive/peer/2026-10-07-c145-2-fix-addrpos.md` (ANSWERED, $1.37): stagesim allocates symbolic ids per node AND terminal; disposition written.
- Run b `prep_c145_2_fix_b.log` rc=0 (20/0): only the SQ1 row changed (actions index 9, terminals + why); 12 rows in measured t-order from
  `diag_c144_p4s04v18_scratch_c145_1_log.txt:231-242` (the 145-a1-1 log, renamed from `diag_c144_p4s04v18_scratch.log`, md5 64a6b63b).
  Re-sim FINAL; end_cdiff_rows / open_rows / fs_routes / route_check rows / fs_border_gate == old; addr_pos SQ1 last 2->9, n1 0->11 (== real
  t-index); only other change: ids after SQ1 shift -4 (LRL1 -47->-51, IAZ1 -49->-53, TL1 -54->-58, TN1 -63->-67); step files 10..23 changed.
- plan_ring_p4_s04v18.json 9ff46b0e -> f349c39a (old bytes kept: `tools/bench/prep_c145_2_plan_9ff46b0e.json`). No later op addresses SQ1 by index
  (only `new:SQ1.last`, `new:SQ1.n1` by name).

## Re-derived (step 3)
- Pred `prep_c145_2_pred.py` (copy of prep_c144_a2_2_pred.py): 90eff870 -> 6a1faf56; EL by PD349 = 60 (base 55 MEASURED, new input x5 + local x2,
  closed cond 29699 + local 29720); X10 680.1 at 598.5 vs 680.0 (report-only FAIL, rc=1 as for 144-a2-2) -> gate-fp fp-46 logged (guard_peer).
- dry PASS both recipes (`prep_c145_2_dry.log`, `prep_c145_2_scr_dry.log`); prerun 16/0 both (`prep_c145_2_prerun.log`, `prep_c145_2_scr_prerun.log`),
  prerun X10 656.7; `--scratch-required` rc 3 (census unpredicted) `prep_c145_2_scrreq.log`. Recipes unchanged (fe3f630c / f5e4bdf8).

## Scratch (ONE run) `tools/bench/diag_c144_p4s04v18_scratch.log` (BGRUN END rc=0, 567 s)
- RESULT 24/0: E1 real == sim at all 19 ops; NG, FR, D (9 new / 0 lost), TD, PB (16 rows, 11 open pairs), HB, PS, H2, H3, H5 PASS; PRIM PASS on
  every created primitive (Wait, Or, 3 Index Array). SQ1 bound -38 -> #29724 (:246); LRL1 -51 -> #30001 (:275).
- Peak 619.3 MB (X10 680.1, d -60.8); MEM 680 stop not hit; MEM/MEML/IN/GONE PASS. Handles 45662 -> 46302 open->save (:364), exit 40224.
- Saved work copy `claudeDev\D1_ring_p4s04_20261007_215031.vi` md5 95e408ff (318509 B, broken by design) (:371).
- Census written into the pred from log :359 (`diag_c145_2_census.log` 5/0): pred 6a1faf56 -> a2bbc8bf.

## Error List (prediction MISSED) `tools/bench/diag_c145_2_el.log` (rc=1, 804 s, --role final, vs the s03 expected file)
- 58 items == window N 58 (pred 60). Verdict MISMATCH; extra 4 = 3 x "Index Array 'Index Array': Contains unwired or bad terminal" + 1 empty-raw
  local-variable row (item 3); missing 1 (While cond class) (`diag_c145_2_elfacts.log`). No SubVI 'required input' item appears for PS1 / SQ1.
- Read file `errorlist_D1_ring_p4s04_20261007_215031_20261007_220024.json` md5 5e53096a.

## Not done (return at the first miss): adopt, EL expected file, fresh load, graph read. Scripts ready, unrun: diag_c145_2_adopt.py,
   diag_c145_2_mkgraph.py, diag_c145_2_graph.py.
## After: `diag_c145_2_check_after.log` 6/0: plan, recipes, s03 282301ca, bed 39511877 unchanged; no LabVIEW process.
