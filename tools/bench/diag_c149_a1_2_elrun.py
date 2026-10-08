# ---
# labview: build
# hardware: none
# ---
r"""diag_c149_a1_2_elrun - card 149-a1-2 step 2: run tools/errorlist_check.py UNCHANGED, as __main__, with the Claude app's MSIX
LocalCache user site at sys.path[0] for THIS process only (the in-process equivalent of a one-command PYTHONPATH; the permission
layer refuses `$env:PYTHONPATH=` / `PYTHONPATH= cmd` as "modifies environment variables"; measured 18:1x). No install, no .pth,
no py.ini, no global site-packages change. Probe of the same folder: tools/bench/diag_c149_a1_2_probe.log:6-11 (comtypes 1.4.17,
rapidocr_onnxruntime 1.4.4, numpy 2.2.6).
WHAT EXISTS: errorlist_check.py (reader, byte-copy scratch `_elc_*`, expected comparison) is reused as-is; this file only sets the path.
PREDICTION CONTRACT: errorlist_check reports OCR engine rapidocr-onnxruntime and a window count of 55 (s05 read
diag_c147_a1_1_el.log:20-22), items == window count, verdict OK or MISMATCH with a per-class diff; bed md5 569ffbf5 unchanged.
    py tools/bgrun.py --material --max-min 35 --log tools/bench/diag_c149_a1_2_el.log -- py -u tools/bench/diag_c149_a1_2_elrun.py
       --vi <claudeDev>\D1_ring_p4s06_20261008_174730.vi --expected tools/bench/errorlist_expected_D1_ring_p4s05_20261008_002621.json --role final"""
import os
import runpy
import sys

LC = r"C:\Users\KimLab\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Python\Python310\site-packages"
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
EL = os.path.join(ROOT, "tools", "errorlist_check.py")
sys.path.insert(0, LC)
os.environ["PYTHONPATH"] = LC
print("ELRUN sys.path[0]", sys.path[0], "| runs", EL, sys.argv[1:], flush=True)
sys.argv = [EL] + sys.argv[1:]
runpy.run_path(EL, run_name="__main__")
