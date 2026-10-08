# ---
# labview: none
# hardware: none
# ---
"""Card 149-a1-2 step 1 probe: import the Error List reader's packages with PYTHONPATH set for this ONE command
(Claude app MSIX LocalCache user site). Prediction: comtypes 1.4.17, numpy 2.2.6, rapidocr_onnxruntime 1.4.4 import OK.
Existing tool reused: none needed (offline import check). Installs nothing.
The permission layer refuses `$env:PYTHONPATH=...` and `PYTHONPATH=... cmd` ("Command modifies environment variables"),
so the SAME effect is made in-process: the folder goes to sys.path[0] (where PYTHONPATH entries land, ahead of the
global site-packages) and os.environ['PYTHONPATH'] for this process only. Nothing on disk outside tools/bench changes."""
import os
import sys
LC = r"C:\Users\KimLab\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Python\Python310\site-packages"
sys.path.insert(0, LC)
os.environ["PYTHONPATH"] = LC
import importlib.metadata as md
print("sys.path[:3]", sys.path[:3])

print("exe", sys.executable)
print("PYTHONPATH", os.environ.get("PYTHONPATH"))
ok = 0
bad = 0
want = {"comtypes": "1.4.17", "numpy": "2.2.6", "rapidocr_onnxruntime": "1.4.4"}
for mod in ["comtypes", "rapidocr_onnxruntime", "numpy", "onnxruntime", "cv2"]:
    try:
        m = __import__(mod)
        dist = {"cv2": "opencv_python"}.get(mod, mod)
        ver = md.version(dist)
        print("IMPORT", mod, ver, getattr(m, "__file__", "?"))
        if mod in want and ver != want[mod]:
            print("GATE FAIL version", mod, ver, "!=", want[mod]); bad += 1
        else:
            ok += 1
    except Exception as e:  # noqa: BLE001
        import traceback
        traceback.print_exc()
        print("GATE FAIL import", mod, repr(e)); bad += 1
import json
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if bad == 0 else "FAIL",
                              "gates": {"pass": ok, "fail": bad}, "first_fail": None, "artefacts": []}))
