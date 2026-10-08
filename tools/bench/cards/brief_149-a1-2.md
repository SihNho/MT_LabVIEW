---
card: 149-a1-2
status: current
date: 2026-10-08
---
# Brief 149-a1-2 - Error List read with the app-container site-packages on PYTHONPATH, then adopt s06 (PD354(a), PD361(d))

Retry of 149-a1-1 (`retry_of_card`). Read `tools/bench/diag_c149_a1_1_facts.md` first. Its finding: `comtypes`, `rapidocr_onnxruntime`,
`onnxruntime`, `cv2`, `winsdk`, `shapely`, `pyclipper` and numpy 2.2.6 are NOT uninstalled; they sit in the Claude app's MSIX user site
`%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Python\Python310\site-packages` (installed 2026-09-23). The runner was
relaunched through WMI at 12:31 (outside the app), so its `py` does not see that folder. Everything in `brief_149-a1-1.md` applies,
EXCEPT step 2, which is replaced:

## Step 2 (replaced): NO pip install. Make the existing packages visible to ONE command
1. **Probe first (offline, no LabVIEW):** run `py -c "import comtypes, rapidocr_onnxruntime, numpy; print(...versions...)"` with the
   environment variable `PYTHONPATH` set to that LocalCache `site-packages` folder FOR THAT ONE COMMAND ONLY (PowerShell:
   `$env:PYTHONPATH=...; py ...` in a single invocation, or a bgrun-wrapped command; do not set it user-wide, do not edit any config,
   `.pth`, `py.ini` or the global site-packages). Quote versions (expected comtypes 1.4.17, numpy 2.2.6, rapidocr_onnxruntime 1.4.4).
   If an import fails, RETURN with the traceback (no further route).
2. **Step 3 of brief 149-a1-1 (the Error List read) runs with the same one-command `PYTHONPATH`.** `tools/errorlist_check.py` is NOT
   edited. Quote the log lines that show which reader produced the 55 items (UIA / MSAA / OCR) and compare with
   `tools/bench/diag_c147_a1_1_el.log:12-26`.
3. Steps 4-6 of brief 149-a1-1 are unchanged (EL-ADVISORY, adopt, graph, `load_by_vi` only, invariants, LabVIEW gone). Adoption scripts
   are copied to `diag_c149_a1_2_*` (card id/names only).

## Return conditions (no retry inside the card)
Probe import failure; a read that again returns 0 items; any pass-item difference. The facts file ends with `OPEN:` naming what the
judgement session must decide (for example whether the runner must be launched from inside the app so every reader sees these packages).

## Report (`tools/bench/diag_c149_a1_2_facts.md`, <= 45 lines)
Probe output (versions), the PYTHONPATH command form used, EL read count + which reader, per-class diff, adopted file + md5 + load MB,
graph json + md5, `load_by_vi` key-by-key diff, invariants, handle counts, LabVIEW gone. `OPEN:` line. Facts only.
