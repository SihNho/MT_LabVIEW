"""c52r2_astcheck - AST + import check of cycle 52's ROUND-2 diagnostic. Touches no LabVIEW: it only parses and
imports (all work is under `if __name__ == '__main__'`), and prints the signatures of every helper the diagnostic
calls, so a signature mismatch is caught before a bgrun is spent on it."""
import ast
import inspect
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for p in ("tools", "tools/bench", "tools/recipes"):
    sys.path.insert(0, os.path.join(ROOT, p))

for rel in sys.argv[1:] or ["tools/bench/diag_queue_donor2.py"]:
    src = open(os.path.join(ROOT, rel), encoding="utf-8").read()
    ast.parse(src)
    print("AST OK  %s  (%d lines, %d gate sites)" % (rel, src.count("\n") + 1, src.count("gate(")))

import diag_queue_donor2 as Q                                                     # noqa: E402
print("IMPORT OK diag_queue_donor2: scratch=%s  d686=%s  frame=%s/%s"
      % (os.path.basename(Q.SCRATCH), Q.SIBLING_DIAG_UID, Q.FRAME_LOOP_UID, Q.FRAME_BODY_UID))
print("NUMVI on disk: %s" % os.path.exists(Q.NUMVI))
for j in ("opcreateconstonterm_labels.json", "opwiresource_v5_labels.json"):
    print("labels %s: %s" % (j, os.path.exists(os.path.join(ROOT, "tools", "bench", j))))

import gscript as g                                                               # noqa: E402
import build_opcreateconstonterm_v0 as COT                                        # noqa: E402
import build_opwiresource_v5 as WS                                                # noqa: E402
from build_d1_v0 import move_in, owner_of, diag_index, terms_of                   # noqa: E402
from build_opstopfromnode_v0 import walk, cls_of, idx                             # noqa: E402
for f in (g.create_control, g.build_index_array, g.drop_subvi, g.queue_node, g.delete_object, g.save,
          g.exec_state, move_in, owner_of, diag_index, terms_of, walk, cls_of, idx,
          COT.create_const_on_term, COT.read_const, WS.read_terminal, Q.const_on_term, Q.dependency_of_node,
          Q.walk_rows, Q.q_attempt, Q.wire_driver):
    print("  %-26s %s" % (f.__name__, inspect.signature(f)))
print("OK")
