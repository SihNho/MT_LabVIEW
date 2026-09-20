import sys, os, glob; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); import gscript as g
g._lv = None
B = r"C:\Program Files\National Instruments\LabVIEW 2026\resource\importtools\sharedlib\VI\Block Diagram\Call Library Node"
for p in sorted(glob.glob(os.path.join(B, "**", "*.vi"), recursive=True)):
    try: print(os.path.relpath(p, B), "->", g.fp_labels(p), flush=True)
    except Exception as e: print(os.path.relpath(p, B), "EXC", str(e)[:120], flush=True)
