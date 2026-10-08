---
card: 151-a3-4
date: 2026-10-09
status: current
---
# 151-a3-4 facts (offline, no LabVIEW)

1. errorlist_check.py has no offline self-test (argparse :520-527) and declares labview: build (:688); guard_bash refused even `--help` under this labview=none card. Measured instead with tools/bench/diag_c151_a3_4_selftest.py (labview none).
2. guard_write refused `import comtypes` in a labview=none script (scope_header.py:280-285, comtypes in LV_DIRECT); comtypes was therefore LOCATED by importlib.util.find_spec, not imported - UIA object creation was NOT exercised.
3. Self-test PASS 5/0 (diag_c151_a3_4_selftest.log:4-10, BGRUN END rc=0): python 3.10.9 at ...\Python310\python.exe; comtypes + comtypes.client found; rapidocr_onnxruntime imports, RapidOCR() constructs; OCR of errwin_032933_b45_1.png -> 21 lines incl. "Error list", "Items with errors"; winsdk importable.
4. Both modules resolve ONLY from the Claude app's virtualised user site C:\Users\KimLab\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Python\Python310\site-packages (log :4-6); comtypes/__init__.py is absent from the base Python310\Lib\site-packages, and C:\Users\KimLab\AppData\Roaming\Python\Python310\site-packages does not exist (Glob).
5. Drain: `py tools/gate_fp.py drain --id fp-61 --fixed tools/bench/diag_c151_a3_4_selftest.log:6 --selftest tools/bench/diag_c151_a3_4_selftest.py` -> "DRAINED fp-61", rc 0. Nothing installed, no tool edited.
6. s08 scratch --dry: DRY PASS 1/0, first_fail None, coverage 59/135 (diag_c151_a3_4_scr_dry.log:109-111) == last session 1/0.
7. s08 scratch --prerun: PASS 16/0, X10 651.6 MB (fail above 680; recorded 645.4) (diag_c151_a3_4_scr_prerun.log:128-136) == last session 16/0, 651.6. ADVISORY CENSUS-UNPREDICTED rows 1-19 (:121), as before.
8. gate_fp list: fp-61 drained; fp-62..fp-70 all `open`.
9. Invariants md5 before == after: stagekit 604529e8, addrcheck 207beb0d, stagexec 1bab9cf9, gscript 1a80236e, stage_prerun c739eb86, vigraph 13be0847, stagesim 748bbf30, errorlist_check 2b466a89, elrule a5ee7d5c, s07 80dbdb41, s08 7cab5049. The brief's s07 b3f86b32 / s08 f99e8414 do not match the files (card input pins s08 7cab5049; b3f86b32 is the s07 ADOPTED VI md5 per prerun log :11).
10. No tools/hooks edit by this card; tasklist LabVIEW count 0.

OPEN: fp-61's cause is launch-context dependent (packages only in the MSIX-virtualised user site, item 4): a python started outside the Claude app package context would again miss comtypes/rapidocr - is "drained" right, or should the modules go into the base site-packages (or fp-61 be `close`d as an env fault, not a gate FP)?
