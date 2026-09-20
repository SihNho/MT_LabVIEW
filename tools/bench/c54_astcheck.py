"""c54_astcheck - offline syntax + resource check for tools/bench/diag_s3_focus_trial.py. No LabVIEW, no COM."""
import ast
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TGT = os.path.join(HERE, "diag_s3_focus_trial.py")
src = open(TGT, encoding="utf-8").read()
ast.parse(src)
print("AST OK  %s  %d lines, %d gate sites" % (os.path.basename(TGT), len(src.splitlines()), src.count("gate(")))
for f in ("opconnectnested_v1_labels.json", "opconnectfromwire_v0_labels.json", "opwiresource_v5_labels.json",
          "opaddshiftreg_labels.json", "opwiresr_labels.json", "opshiftregs_labels.json",
          "d1_rewire_sources.json", "c53_row_class.json"):
    p = os.path.join(HERE, f)
    ok = os.path.exists(p)
    if ok:
        json.load(open(p, encoding="utf-8"))
    print("  [%s]  %s" % ("ok" if ok else "MISSING", f))
for f in ("D1_s2_loops.vi", "OpConnectNested_v1.vi", "OpConnectFromWire_v0.vi", "OpWireSource_v5.vi",
          "OpMoveIn_v0.vi", "OpAddShiftReg_v0.vi", "OpWireSR_RightIn_v0.vi", "OpWireSR_LeftIn_v0.vi",
          "OpShiftRegs_v0.vi"):
    p = os.path.join(r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev", f)
    print("  [%s]  %s" % ("ok" if os.path.exists(p) else "MISSING", f))
