---
card: 149-a3-3
status: current
date: 2026-10-08
---
# Brief 149-a3-3 - complete the Void-type census (PD363(c)) after 149-a3-2 stopped at COV 1112/4379

Escalation rung 1 (`material-opus-max`) of card 149-a3-2. Read `tools/bench/diag_c149_a3_2_facts.md` step 5 and the peer answer
`archive/peer/2026-10-08-c149-a3-2-void.md` (sec. 1, 2, 4) first. DONE and NOT repeated: s06 adopted, expected file, plan data fix, graph read
(`graph_ring_p4s06_20261008_192149.json` a3ecb92b), `load_by_vi` entry (memory_model 8eec443c). Do not touch any of them.

## Facts already measured (do not re-measure)
- Per-terminal `read_term_type` costs 0.54-0.63 s flat; s06 has 4379 wired terminals (about 40 min per file); 1112 were read in 600 s.
- The script's `'void' in name` test cannot fire: `gscript.py:4585-4588` TD_NAMES has no 0x00, so a Void descriptor is named `"0x00"` (peer sec. 1).
- In the 1112 read terminals: 0 with TD code 0x00, 0 with no TD, 0 read errors. Uncovered new wires of s06: w10166, w23807.

## Steps (card-local copies `diag_c149_a3_3_*`; names only changed from `diag_c149_a3_void.py` / `_md.py`)
1. **Offline, no LabVIEW:** (a) run the peer's `parse_type_descriptors` calibration string (sec. 4 step 1) and quote what a Void descriptor parses to;
   (b) read `allterms`' `read_terms` op in `tools/gscript.py` (and the op VI it calls, by plain read of the op list / `docs/NAMES.md`) and quote
   whether it returns a Data Type field per row, with file:line. Quote both.
2. **Calibration on a known Void (one short LabVIEW read on a scratch or byte copy, never the bed, s03-s06 or any original):** a terminal whose type is
   known Void; run `read_term_type` and record its raw bytes, code and descriptor count. This decides which raw condition the census flags.
3. **Census of (i) a byte copy of the adopted s06 and (ii) a byte copy of s05 3f9ac26b** (copy the bytes first, never open an original), over EVERY wired
   terminal (the 4379 of s06 and the s05 count), flagging on the RAW code calibrated in step 2, not on the name. Plain gscript reads, no edit verb, no
   `Is Broken?`, not the stagekit `discard_work` path (fp-63). The route (bulk if step 1b shows one, otherwise per-terminal, both files in one LabVIEW
   instance or two) is chosen by the card; the pass criterion is COVERAGE 100 % of wired terminals of both files, stated per file.
4. **Write `tools/bench/diag_c149_a3_void_census.md`** (replacing the partial one; keep the partial as `diag_c149_a3_void_census_partial.md` first): per
   file the count of wired terminals, read, Void by raw code, errors; both Void lists (wire, terminal, owner node uid / class / label, name, type);
   the s06-only entries listed separately; counts. FACTS ONLY, no claim whether item 6 ("source void -> sink I32") is among them.
5. **Invariants** (`diag_c149_a3_2_inv.py` form, copy to `diag_c149_a3_3_inv.py`): stage tools, errorlist_check, s05 3f9ac26b, s04 95e408ff,
   s03 282301ca, bed 39511877, s06 569ffbf5 unchanged; memory_model 8eec443c unchanged; no byte copy left; handles recorded; `tasklist` LabVIEW 0.

## Return conditions (no retry inside the card)
Step 1 (a) not parsing as a Void, or step 2 unable to produce a known-Void terminal; coverage under 100 % of either file at the minute cap; an
invariant md5 that moved; any step needing an edit verb or a stage-tool edit. A peer (hypothesis) only if a gate FAILS.

## Report (`tools/bench/diag_c149_a3_3_facts.md`, <= 45 lines)
Step 1 (a)(b) quoted, calibration bytes/code, route chosen and why, per-file coverage and seconds, Void counts, s06-only list head, invariants, handles,
LabVIEW gone. `OPEN:` line. Facts only.
