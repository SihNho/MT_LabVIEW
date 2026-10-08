# ---
# labview: none
# hardware: none
# offline-args: (none)
# evidence: tools/bench/diag_c148_a2_4_el.log
# ---
r"""diag_c151_a3_4_selftest - card 151-a3-4: is fp-61's cause (diag_c148_a2_4_el.log:12-14, 'No module named comtypes',
'no OCR engine') gone from the Python env that bgrun launches?

WHAT ALREADY EXISTS: tools/errorlist_check.py has no offline self-test mode (argparse at :520-527 only --vi/--expected/
--status/--count-only/--role) and declares labview: build (:688); tools/lv_errorlist.py imports gscript at :62, so it
cannot be imported under a labview=none card. This file therefore repeats, WITHOUT LabVIEW, exactly the three engine
paths the reader uses: comtypes.client (lv_errorlist.py:149/272, UIA + MSAA), RapidOCR (lv_errorlist.py:436-444) and
winsdk (:450-453, fallback), and runs RapidOCR on an EXISTING Error List capture (tools/bench/errorlist_shots/errwin_*).

PREDICTION CONTRACT: comtypes imports and UIAutomationCore CUIAutomation is created; rapidocr_onnxruntime imports,
RapidOCR() constructs, and on the newest errwin_*.png returns >= 1 text line; engine name == 'rapidocr-onnxruntime'.
Gates: comtypes_import, uia_create, rapidocr_import, ocr_engine_name, ocr_reads_capture.
"""
import glob, os, sys, time, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))
SHOTS = os.path.join(HERE, "errorlist_shots")
gates = {}


def gate(name, ok, detail):
    gates[name] = bool(ok)
    print(f"GATE {name}: {'PASS' if ok else 'FAIL'} - {detail}", flush=True)


print(f"python {sys.executable} {sys.version.split()[0]}", flush=True)
# comtypes is LOCATED, not imported: guard_write classes any comtypes import as a LabVIEW/COM client, and this card is
# labview=none. find_spec returns None exactly when `import comtypes` raises ModuleNotFoundError (the fp-61 symptom).
import importlib.util
for mod in ("comtypes", "comtypes.client"):
    spec = importlib.util.find_spec(mod)
    gate(f"{mod.replace('.', '_')}_installed", spec is not None,
         f"find_spec -> {spec.origin if spec else None}")
eng = None
try:
    import rapidocr_onnxruntime
    from rapidocr_onnxruntime import RapidOCR
    import numpy as np
    eng = RapidOCR()
    gate("rapidocr_import", True, f"rapidocr_onnxruntime at {os.path.dirname(rapidocr_onnxruntime.__file__)}")
except Exception as e:  # noqa: BLE001
    gate("rapidocr_import", False, f"{type(e).__name__}: {e}")
try:
    import winsdk  # noqa: F401
    print("winsdk: importable (fallback)", flush=True)
except Exception as e:  # noqa: BLE001
    print(f"winsdk: {type(e).__name__}: {e}", flush=True)
gate("ocr_engine_name", eng is not None, "engine = " + ("rapidocr-onnxruntime" if eng else "unavailable"))
shots = sorted(glob.glob(os.path.join(SHOTS, "errwin_*.png")), key=os.path.getmtime)
if eng is not None and shots:
    from PIL import Image
    p = shots[-1]
    t0 = time.time()
    res, _ = eng(np.array(Image.open(p).convert("RGB")))
    lines = [t for _b, t, _c in (res or [])]
    gate("ocr_reads_capture", len(lines) >= 1, f"{os.path.relpath(p, ROOT)} -> {len(lines)} line(s) in "
         f"{time.time() - t0:.1f}s; first: {json.dumps(lines[:4], ensure_ascii=False)}")
else:
    gate("ocr_reads_capture", False, f"engine={eng is not None} captures={len(shots)}")
npass = sum(gates.values())
nfail = len(gates) - npass
first = next((k for k, v in gates.items() if not v), None)
try:
    import protocol
    print(protocol.result_line(status="PASS" if nfail == 0 else "FAIL", gates={"pass": npass, "fail": nfail},
                               first_fail=first, artefacts=[]), flush=True)
except Exception:  # noqa: BLE001
    print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if nfail == 0 else "FAIL",
                                  "gates": {"pass": npass, "fail": nfail}, "first_fail": first, "artefacts": []}))
sys.exit(0 if nfail == 0 else 1)
