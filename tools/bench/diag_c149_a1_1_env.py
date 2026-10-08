# ---
# labview: none
# hardware: none
# ---
r"""diag_c149_a1_1_env - card 149-a1-1 step 1 (OFFLINE, no LabVIEW): measure the Python environment the Error List reader runs in.
Prior art: none for an env probe (diag_c148_a2_4_check.py is the pin check; this only reads the interpreter state).
Prints: sys.executable/version/prefix, py launcher list (py -0p), env vars that move sys.path, import result + version + file
for comtypes, rapidocr_onnxruntime, onnxruntime, numpy, PIL, cv2, win32gui, winsdk; every site-packages dir's entries modified
on 2026-10-08 (name, mtime); pip cache entries for comtypes/rapidocr; other interpreters' site-packages carrying comtypes.
PREDICTION CONTRACT: comtypes and rapidocr_onnxruntime fail to import here (as diag_c148_a2_4_el.log:12-19) -> RESULT gates
count imports OK (facts, no build gate); fail = an import that is missing.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c149_a1_1_env.log -- py -u tools/bench/diag_c149_a1_1_env.py"""
import glob, importlib, os, site, subprocess, sys, time                               # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, d), flush=True)


def run(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return (r.stdout + r.stderr).strip()
    except Exception as e:  # noqa: BLE001
        return "RAISED %r" % e


print("EXE", sys.executable, sys.version.replace("\n", " "))
print("PREFIX", sys.prefix, "BASE", sys.base_prefix, "USERSITE", site.getusersitepackages(), "ENABLE_USER_SITE", site.ENABLE_USER_SITE)
print("SYSPATH", sys.path)
for k in ("PYTHONPATH", "PYTHONHOME", "PYTHONNOUSERSITE", "PY_PYTHON", "PY_PYTHON3", "VIRTUAL_ENV", "CONDA_PREFIX", "PATH"):
    print("ENV", k, "=", os.environ.get(k))
print("PY-0p", run(["py", "-0p"]).replace("\n", " | "))
for ini in (os.path.join(os.environ.get("LOCALAPPDATA", ""), "py.ini"), r"C:\Windows\py.ini"):
    print("PYINI", ini, os.path.exists(ini), open(ini, encoding="utf-8", errors="replace").read().replace("\n", " | ") if os.path.exists(ini) else "")
for mod in ("comtypes", "comtypes.client", "rapidocr_onnxruntime", "onnxruntime", "numpy", "PIL", "cv2", "win32gui", "winsdk", "yaml", "shapely", "pyclipper"):
    try:
        m = importlib.import_module(mod)
        gate("import " + mod, True, "%s %s" % (getattr(m, "__version__", "?"), getattr(m, "__file__", "?")))
    except Exception as e:  # noqa: BLE001
        gate("import " + mod, False, "%s: %s" % (type(e).__name__, e))
try:
    from importlib import metadata as md
    for d in ("comtypes", "rapidocr-onnxruntime", "rapidocr_onnxruntime", "onnxruntime", "numpy", "pillow", "opencv-python",
              "pywin32", "pyclipper", "shapely", "PyYAML", "six", "flatbuffers", "protobuf", "sympy", "coloredlogs"):
        try:
            print("DIST", d, md.version(d))
        except Exception as e:  # noqa: BLE001
            print("DIST", d, "absent", type(e).__name__)
except Exception as e:  # noqa: BLE001
    print("METADATA RAISED", e)
sp = set(site.getsitepackages() + [site.getusersitepackages()])
for d in sorted(sp):
    if not os.path.isdir(d):
        print("SITEDIR", d, "absent")
        continue
    ents = os.listdir(d)
    print("SITEDIR", d, "entries", len(ents), "dir mtime", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(d))))
    for e in sorted(ents):
        p = os.path.join(d, e)
        t = time.localtime(os.path.getmtime(p))
        if time.strftime("%Y-%m-%d", t) >= "2026-10-07" or any(k in e.lower() for k in ("comtypes", "rapidocr", "onnx")):
            print("  ENTRY", time.strftime("%Y-%m-%d %H:%M:%S", t), e)
print("PIPCACHE comtypes", run([sys.executable, "-m", "pip", "cache", "list", "comtypes*"]).replace("\n", " | ")[:600])
print("PIPCACHE rapidocr", run([sys.executable, "-m", "pip", "cache", "list", "rapidocr*"]).replace("\n", " | ")[:600])
for pat in (r"C:\Users\*\AppData\Local\Programs\Python\Python*\Lib\site-packages\comtypes*",
            r"C:\Users\*\AppData\Roaming\Python\Python*\site-packages\comtypes*",
            r"C:\Python*\Lib\site-packages\comtypes*", r"C:\Program Files\Python*\Lib\site-packages\comtypes*",
            r"C:\Users\*\AppData\Local\Programs\Python\Python*\Lib\site-packages\rapidocr*",
            r"C:\Users\*\AppData\Roaming\Python\Python*\site-packages\rapidocr*",
            r"C:\Program Files\Python*\Lib\site-packages\rapidocr*"):
    for p in glob.glob(pat):
        print("ELSEWHERE", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(p))), p)
MSIX = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Packages", "Claude_pzs8sxrjxfjjc", "LocalCache", "Roaming", "Python",
                    "Python310", "site-packages")
print("MSIX-USERSITE", MSIX, os.path.isdir(MSIX), "in sys.path", MSIX in sys.path)
if os.path.isdir(MSIX):
    for e in sorted(os.listdir(MSIX)):
        if e.endswith(".dist-info"):
            print("  MSIX", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(os.path.join(MSIX, e)))), e)
print(protocol.result_line({"status": "PASS" if G["fail"] == 0 else "FAIL", "gates": {"pass": G["pass"], "fail": G["fail"]},
                            "first_fail": G["first"], "artefacts": [], "card": "149-a1-1", "labview": "none"}), flush=True)
