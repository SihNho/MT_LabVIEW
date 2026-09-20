"""call_probe.py - can a reentrant SPEC copy be executed over COM with VirtualInstrument.Call (names, values)?"""
import os, sys, threading, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, ROOT)
import gscript as g
import pythoncom, win32com.client
g._lv = None
path = os.path.join(g.CLAUDEDEV, "SPEC", "tracking- quadratic fit to phase nghbrd.vi")
for opt in (8, 0):
    try:
        vi = g.lv().GetVIReference(path, "", False, opt)
        print("opt", opt, "ref ok; ExecState", vi.ExecState, flush=True)
    except Exception as e:
        print("opt", opt, "GetVIReference failed:", str(e)[:150], flush=True); continue
    names = ["neighborhood phases", "index of best-fit\ncal image slice", "bead z pos as a cal image index"]
    vals = [[0.1, 0.05, 0.0, -0.05, -0.1], 29, 0.0]
    res = {}
    def worker():
        try:
            res["out"] = vi.Call(names, vals)
        except Exception as e:
            res["err"] = str(e)[:300]
    t = threading.Thread(target=worker, daemon=True); t.start(); t.join(20)
    print("opt", opt, "Call ->", res if res else "TIMEOUT 20s", flush=True)
    if "out" in res:
        break
