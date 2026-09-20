"""c53_astcheck - AST + import check of cycle 53's D1 stage S3 recipe. Touches no LabVIEW: it parses and
imports only (all of the recipe's work is under `if __name__ == '__main__'`), and prints the signature of every
helper the recipe calls, so a signature mismatch is caught before a bgrun is spent on it."""
import ast
import hashlib
import inspect
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for p in ("tools", "tools/bench", "tools/recipes"):
    sys.path.insert(0, os.path.join(ROOT, p))

for rel in ("tools/recipes/stage_d1_s3_focus.py",):
    raw = open(os.path.join(ROOT, rel), "rb").read()
    src = raw.decode("utf-8")
    ast.parse(src)
    print("AST OK  %s  (%d lines, %d gate sites, sha256 %s)"
          % (rel, src.count("\n") + 1, src.count("gate("), hashlib.sha256(raw).hexdigest()))
    bold = src.count('"**FAIL**"') + src.count("'**FAIL**'")
    print("  gate format check (37(i)): occurrences of the BOLDED form in this file = %d (must be 0)" % bold)

import stage_d1_s3_focus as S                                                     # noqa: E402
print("IMPORT OK: target=%s  loop_a=%s body_a=%s frame_body=%s sibling=%s"
      % (os.path.basename(S.TARGET), S.LOOP_A_UID, S.BODY_A_UID, S.FRAME_BODY_UID, S.SIBLING_DIAG_UID))
print("  set uids %r; pre-move wired %r" % (S.SET_UIDS, S.PRE_MOVE_WIRED))
print("  internal jobs %d; shift registers %d; cross rows %d; batch size %d"
      % (len(S.INTERNAL_JOBS), len(S.SR_SPECS), len(S.CROSS_ROWS), S.BATCH_SIZE))
print("  S2 artefact on disk: %s" % os.path.exists(S.S2_ARTEFACT))
print("  ORIGINAL on disk: %s" % os.path.exists(S.ORIGINAL))
print("  D1_s3_loop15.vi already on disk: %s" % os.path.exists(S.TARGET))
print("  d1_rewire_sources.json on disk: %s" % os.path.exists(S.REWIRE_JSON))
print("  opconnectnested_v1 labels keys: %r" % sorted(S.V1_LABELS.keys()))
for name in ("OpMoveIn_v0.vi", "OpConnectNested_v1.vi", "OpAddShiftReg_v0.vi", "OpNodeTerms_v0.vi"):
    import gscript as _g
    print("  %s on disk: %s" % (name, os.path.exists(os.path.join(_g.CLAUDEDEV, name))))

rows = S.load_rewire_rows()
print("  dest-1.5 rows loaded from the measured file: %d" % len(rows))
by_action = {}
for r in rows:
    by_action[r.get("action")] = by_action.get(r.get("action"), 0) + 1
print("  by action: %r" % by_action)

import gscript as g                                                               # noqa: E402
import diag_s2_scaffold as D                                                      # noqa: E402
from build_d1_v0 import move_in, owner_of, diag_index                             # noqa: E402
from build_opstopfromnode_v0 import walk, loop_end_ref                            # noqa: E402
from build_opconnectnested_v1 import connect_nested_v1                            # noqa: E402
from stage_d1_s1 import cold_subvi_table, compare_subvi_tables                     # noqa: E402
for f in (g.count, g.report_all, g.node_terms_uid, g.op, g.open_panel, g.close_panel, g.save, g.exec_state,
          g.add_shift_reg, g.wire_sr, g.shift_reg, move_in, owner_of, diag_index, walk, loop_end_ref,
          connect_nested_v1, cold_subvi_table, compare_subvi_tables, D.fresh, D.read_state, D.try_save,
          D.file_facts, S.node_state, S.term_state, S.term_index, S.cond_read, S.census, S._wire_one):
    print("  %-22s %s" % (f.__name__, inspect.signature(f)))
print("OK")
