"""c52r3_astcheck - AST + import check of cycle 52's ROUND-3 diagnostics (measurements A and B). Touches no
LabVIEW: it parses and imports only (all work is under `if __name__ == '__main__'`), and prints the signature of
every helper the two diagnostics call, so a signature mismatch is caught before a bgrun is spent on it."""
import ast
import inspect
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for p in ("tools", "tools/bench", "tools/recipes"):
    sys.path.insert(0, os.path.join(ROOT, p))

for rel in ("tools/bench/diag_movein_set.py", "tools/bench/diag_donor_census.py"):
    src = open(os.path.join(ROOT, rel), encoding="utf-8").read()
    ast.parse(src)
    print("AST OK  %s  (%d lines, %d gate sites)" % (rel, src.count("\n") + 1, src.count("gate(")))

import diag_movein_set as A                                                       # noqa: E402
import diag_donor_census as B                                                     # noqa: E402
print("IMPORT OK A: scratch=%s  d686=%s sink=%s src=%s wire=%s use_loop=%s"
      % (os.path.basename(A.SCRATCH), A.SIBLING_DIAG_UID, A.SINK_UID, A.SRC_UID, A.WIRE_UID, A.USE_LOOP))
print("IMPORT OK B: scratch=%s  d686=%s frame=%s queues=%d"
      % (os.path.basename(B.SCRATCH), B.SIBLING_DIAG_UID, B.FRAME_LOOP_UID, len(B.QUEUE_TYPES)))
print("S2 artefact on disk: %s" % os.path.exists(A.S2_ARTEFACT))
print("OpMoveIn_v0.vi on disk: %s" % os.path.exists(A.OPIN))
for j in ("opwiresource_v5_labels.json",):
    print("labels %s: %s" % (j, os.path.exists(os.path.join(ROOT, "tools", "bench", j))))

import gscript as g                                                               # noqa: E402
import diag_s2_scaffold as D                                                      # noqa: E402
from build_d1_v0 import move_in, owner_of, diag_index, UID_LABEL                  # noqa: E402
from build_opstopfromnode_v0 import walk, cls_of                                  # noqa: E402
from diag_movein_p1_break import read_term                                        # noqa: E402
print("UID_LABEL = %r" % (UID_LABEL,))
for f in (g.count, g.report_all, g.node_terms_uid, g.fp_labels, g.op, g.open_panel, g.close_panel,
          g.save, g.exec_state, move_in, owner_of, diag_index, walk, cls_of, read_term,
          D.fresh, D.read_state, D.try_save, D.file_facts, A.terms_by_uid, A.wire_side, A.census,
          A.wire_present, B.census):
    print("  %-22s %s" % (f.__name__, inspect.signature(f)))
print("OK")
