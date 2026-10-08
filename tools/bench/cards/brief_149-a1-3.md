---
card: 149-a1-3
status: current
date: 2026-10-08
---
# Brief 149-a1-3 - MEASURE why the s06 Error List reads 51 (predicted 55), read-only (PD354(a), PD361(d))

Follow-up of 149-a1-2. Read `tools/bench/diag_c149_a1_2_facts.md` first (EL-ADVISORY section and the peer section). The environment is
solved there (LocalCache site on `sys.path[0]` in-process, `tools/bench/diag_c149_a1_2_elrun.py`). The s06 scratch file is final
(`claudeDev\D1_ring_p4s06_20261008_174730.vi`, md5 569ffbf5); **NO new scratch, NO edit of that file, NO adoption, NO stage-tool edit.**
You MEASURE and report; you do not decide whether to adopt.

## Measurements (facts only)
1. **Header check:** is the window's own count really 51? Capture the Error List header/last row of a byte copy of 569ffbf5 (same wrapper
   `diag_c149_a1_2_elrun.py`, copy it to `diag_c149_a1_3_*`) and quote what the capture shows (the OCR'd header "51" was the only support
   for the count; peer alternative B unchecked).
2. **Capture comparison:** put the s06 show-error captures of items 5 and 6 ("source void -> sink I32" is item 6, read json :322) next to
   the s05 read items 7, 8, 10-13 (`errorlist_D1_ring_p4s05_20261008_002621_20261008_012323.json`) and say which s05 items they match and
   which s06 items have no s05 or predicted counterpart.
3. **Wire read of w23807 (read-only, labview read):** is the wire broken in the saved s06 (`Wire.Is Broken?` read-back on the connect-op
   path, or the equivalent read the stagekit exposes), what are its source and sink terminals, and is it the same wire the op-21 "target BROKEN"
   line (`diag_c147_p4s06v18_scratch.log:990-994`) names. Quote both.
4. **Per-class table** (read vs pred vs s05) with each of the 4 net-negative classes marked "explained by <fact>" or "unexplained".

Return conditions: any LabVIEW hang (kill the instance, restart permitted), a read that returns 0 items. Do not retry in a loop.
Close: invariants as in `tools/bench/diag_c149_a1_2_inv.log` (s05 3f9ac26b, s04 95e408ff, s03 282301ca, bed 39511877, s06 569ffbf5,
stagekit, stagexec, gscript, elrule, errorlist_check, memory_model 88eeb037 unchanged); handles recorded; LabVIEW gone.

## Report (`tools/bench/diag_c149_a1_3_facts.md`, <= 40 lines)
Header count, capture comparison, w23807 read, per-class table, invariants. `OPEN:` line. Facts only; no recommendation to adopt.
