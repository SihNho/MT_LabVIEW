"""card 131-1 Part B self-test (offline, no LabVIEW): the simulator's crossing-tunnel naming (stagesim.cross_face_names)
against EVERY row of tools/bench/fs_tunnel_naming_table.json - one case per row, each known face name compared, 'unknown'
cells skipped and counted (stagesim.naming_table_check; the same rows are gates G78/G78b/G79 of `stagesim.py selftest`).
FlatSequenceInnerTunnel rows (frame-to-frame) are outside the rule (never name-keyed, stagexec.py:963-993): listed, not tested.
PRIOR ART: stagesim selftest G74-G77 (card 129-7) tested the refuted net-name rule on 5 cases.
PREDICTION: 15 rows pass, 3 FSIT rows skipped."""
import os, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol
import stagesim as SS

gates = []
nt = SS.naming_table_check()
for lab, bad, cite in nt["rows"]:
    gates.append(("ROW {0}".format(lab), not bad))
    print("  {0}  ROW {1}  ({2}) {3}".format("PASS" if not bad else "FAIL", lab, cite[:90], bad or ""))
print("  FACT  rows {0}, face cells {1}, unknown {2}, skipped (FSIT) {3}".format(len(nt["rows"]), nt["cells"], nt["unknown"],
                                                                                nt["skipped"]))
gates.append(("C1 15 rule rows + 3 FSIT rows", len(nt["rows"]) == 15 and len(nt["skipped"]) == 3))
n_pass = sum(1 for _l, ok in gates if ok)
n_fail = len(gates) - n_pass
first = next((l for l, ok in gates if not ok), None)
print("=== GATES: {0} pass / {1} fail{2}".format(n_pass, n_fail, "; failing: " + first if first else ""))
print(protocol.result_line(protocol.make_result(n_pass, n_fail, first)))
sys.exit(0 if n_fail == 0 else 1)
