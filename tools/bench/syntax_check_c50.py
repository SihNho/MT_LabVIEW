"""AST + import gate for tools/bench/diag_s2_scaffold.py — no LabVIEW call, no COM, main() is never entered."""
import ast
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
P = os.path.join(HERE, "diag_s2_scaffold.py")
src = open(P, "rb").read()
ast.parse(src.decode("utf-8"))
print("AST OK  %d lines  sha256 %s" % (len(src.decode("utf-8").splitlines()),
                                       hashlib.sha256(src).hexdigest()[:12]))
sys.path.insert(0, HERE)
import diag_s2_scaffold as D                                                     # noqa: E402
print("IMPORT OK")
for name in ("ORIGINAL", "S1_ARTEFACT", "SCRATCH", "OUT"):
    v = getattr(D, name)
    print("  %-12s %s  exists=%s" % (name, v, os.path.exists(v)))
for op in ("OpCreateEqual_v0.vi", "OpStopFromNode_v0.vi", "OpMoveIn_v0.vi"):
    p = os.path.join(D.CLAUDEDEV, op)
    print("  op %-24s exists=%s" % (op, os.path.exists(p)))
print("  OPIN (move_in op) ->", getattr(__import__("build_d1_v0"), "OPIN", None))
for j in ("opcreate_equal_labels.json", "opstopfromnode_labels.json"):
    print("  labels %-30s exists=%s" % (j, os.path.exists(os.path.join(HERE, j))))
print("CHECK DONE")
