---
card: 149-a1-1
status: current
date: 2026-10-08
---
# Brief 149-a1-1 - restore the Error List reader's Python modules, then finish the s06 adoption (docs/d1/ring-p4c.md PD361(d), PD354(a))

Retry of card 148-a2-4 (`retry_of_card`). That card's ONE scratch PASSED 22/0 and saved `claudeDev\D1_ring_p4s06_20261008_174730.vi`
(md5 569ffbf5). Its Error List read then failed on the environment, not on the build: `tools/bench/diag_c148_a2_4_el.log:12-14`
(`ModuleNotFoundError: No module named 'comtypes'`, no OCR engine), while the same reader worked at 01:23
(`tools/bench/diag_c147_a1_1_el.log:12-24`). Read `tools/bench/diag_c148_a2_4_facts.md` first; everything it says about the scratch is
final. **NO second scratch, no stage-tool edit, no hook edit.**

## Steps
1. **Measure the environment** (labview none): which interpreter `py` resolves to (`sys.executable`), `pip list` for `comtypes`,
   `rapidocr-onnxruntime` (and whatever else `tools/errorlist_check.py` imports in its UIA/MSAA/OCR paths); the install dates of
   those packages' site-packages entries; the pip log / `pip cache` / any `requirements` file or earlier log that names the versions
   that worked at 01:23; and what ran between 01:23 and 17:57 on 2026-10-08 that could have changed the environment (cycle-148 cards
   that spawned a different interpreter, a venv, or a pip/uninstall command; `tools/bench/*.log` grep for `pip`). Quote the facts.
2. **Restore only the missing packages at the version the 01:23 run used** (`py -m pip install <pkg>==<version>`). If the version
   cannot be established from the machine, or a restore would install a different version, RETURN with the facts (`OPEN:` line).
   No other package is installed, upgraded or removed. Verify `import comtypes` and the OCR engine import from the same `py`.
3. **Re-read the Error List** of a byte copy of `569ffbf5` with `tools/errorlist_check.py` exactly as in
   `diag_c148_a2_4_facts.md:30-31` (`--role final`, `--expected tools/bench/errorlist_expected_D1_ring_p4s05_20261008_002621.json`),
   under bgrun `--material --max-min 35`. 55 items, or a documented per-class difference, is the result. A read that again returns 0
   items is a RETURN (do not retry in a loop).
4. **EL-ADVISORY and adopt** by PD354(a), with the prepared scripts of 148-a2-4 (`diag_c148_a2_4_adopt.py`, `_elexp.py <read json>`,
   `_mkgraph.py`, `_graph.py`, `_memload.py`; copy them to `diag_c149_a1_1_*` with card id/names changed only): EL ADVISORY (fails only on
   a class seen in neither the s05 read nor the prediction, or |total diff| > 3) with the per-class diff explained; adopt as
   `claudeDev\D1_ring_p4s06_<stamp>.vi` (the scratch file 569ffbf5 is the artefact; no rerun); final EL expected file; fresh-instance
   load (MB) + graph read -> `tools/bench/graph_ring_p4s06_<stamp>.json` + md5.
5. **`memory_model.json`**: ONLY one `load_by_vi` entry for 569ffbf5 with the measured load (key-by-key diff in the facts); no limit,
   coefficient or X10/MEMSTOP value changes.
6. Close: s05 3f9ac26b, s04 95e408ff, s03 282301ca, bed 39511877, stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule
   a5ee7d5c unchanged; handles recorded; `tasklist` LabVIEW count 0.

## Report (`tools/bench/diag_c149_a1_1_facts.md`, <= 45 lines)
Environment facts (step 1), what was installed (exact versions), EL read count + per-class diff, adopted file + md5 + load MB, graph
json + md5, `load_by_vi` key-by-key diff, invariants, handle counts, LabVIEW gone. `OPEN:` line. Facts only.
