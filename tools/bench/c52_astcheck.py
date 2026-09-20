"""c52_astcheck - AST + import check of this cycle's two DIAGNOSTICS. Touches no LabVIEW: it only parses and
imports (every module's work is under `if __name__ == '__main__'`), and prints the helper signatures the two
diagnostics call, so a signature mismatch is caught before a bgrun is spent on it."""
import ast
import inspect
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for p in ("tools", "tools/bench", "tools/recipes"):
    sys.path.insert(0, os.path.join(ROOT, p))

for rel in sys.argv[1:]:
    src = open(os.path.join(ROOT, rel), encoding="utf-8").read()
    ast.parse(src)
    print("AST OK  %s  (%d lines, %d gate sites)" % (rel, src.count("\n") + 1, src.count("gate(")))

import verify_d1_s2 as V                                                          # noqa: E402
print("IMPORT OK verify_d1_s2: S1=%s S2=%s" % (os.path.basename(V.S1), os.path.basename(V.S2)))
if os.path.exists(os.path.join(ROOT, "tools", "bench", "diag_queue_donor.py")):
    import diag_queue_donor as Q                                                  # noqa: E402
    print("IMPORT OK diag_queue_donor: scratch=%s" % os.path.basename(Q.SCRATCH))

import diag_d1_execstate_preload as E                                             # noqa: E402
import hash_probe                                                                 # noqa: E402
import gscript as g                                                               # noqa: E402
from build_d1_v0 import owner_of, terms_of                                        # noqa: E402
from build_opstopfromnode_v0 import loop_end_ref, wire_source                     # noqa: E402
from build_opsentinel_ops import create_node                                      # noqa: E402
for f in (E.run_condition, hash_probe.probe, g.queue_node, g.count, owner_of, terms_of, loop_end_ref,
          wire_source, create_node):
    print("  %-22s %s" % (f.__name__, inspect.signature(f)))
print("OK")
