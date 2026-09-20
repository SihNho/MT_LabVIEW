import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); import gscript as g
g._lv = None
B = r"C:\Program Files\National Instruments\LabVIEW 2026\resource\importtools\sharedlib"
for rel in (r"VI\Block Diagram\Method\Create.vi", r"VI\Block Diagram\Attribute\Parameter Info.vi", r"VI\Block Diagram\Attribute\Function Name.vi",
            r"VI\Block Diagram\Call Library Node\Attribute\Function Dec.vi", r"VI Generator\Generate VIs\Generate VIs.vi", r"Header Parser\Function\Method\Open Parameter.vi",
            r"VI\Block Diagram\Call Library Node\Method\Connect Terminals.vi"):
    try: print(rel, "->", g.fp_labels(os.path.join(B, rel)), flush=True)
    except Exception as e: print(rel, "EXC", str(e)[:160], flush=True)
EM = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting"
for n in ("Create Flatten to String.vi", "Create Unflatten from String.vi", "Create Bundle by Name.vi", "Create Constant.vi"):
    try: print(n, "->", g.fp_labels(os.path.join(EM, n)), flush=True)
    except Exception as e: print(n, "EXC", str(e)[:160], flush=True)
