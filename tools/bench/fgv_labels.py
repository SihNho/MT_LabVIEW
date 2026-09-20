import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); import gscript as g
g._lv = None
B = r"C:\Program Files\National Instruments\LabVIEW 2026\resource\importtools\sharedlib\VI\Block Diagram"
for rel in ("Attribute\Function Name.vi", "Attribute\Path.vi", "Attribute\Calling Convention.vi", "Attribute\Reentrant.vi", "Attribute\Parameter Info.vi",
            "Attribute\Error Convention.vi", "Attribute\Default Arrary Size.vi", "Attribute\Return Value Terminal.vi", "Attribute\Path Error Converter VI.vi",
            "Call Library Node\Attribute\Function Dec.vi", "Call Library Node\Attribute\Internal\Current Para Name.vi"):
    try: print(rel, "->", g.fp_labels(os.path.join(B, rel)), flush=True)
    except Exception as e: print(rel, "EXC", str(e)[:160], flush=True)
