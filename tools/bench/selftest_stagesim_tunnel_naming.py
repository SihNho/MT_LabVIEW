"""card 131-1 Part B self-test (offline, no LabVIEW): the simulator's crossing-tunnel naming (stagesim.cross_face_names)
against EVERY row of tools/bench/fs_tunnel_naming_table.json - one case per row, each known face name compared, 'unknown'
cells skipped and counted (stagesim.naming_table_check; the same rows are gates G78/G78b/G79 of `stagesim.py selftest`).
FlatSequenceInnerTunnel rows (frame-to-frame) are outside the rule (never name-keyed, stagexec.py:963-993): listed, not tested.
PRIOR ART: stagesim selftest G74-G77 (card 129-7) tested the refuted net-name rule on 5 cases.
PREDICTION: 16 rows pass (card 152-b1-3 added the LoopTunnel row), 3 FSIT rows skipped; L1 the measured LoopTunnel shape
gives 'min slot' on both faces; L2-L4 a LoopTunnel on a ForLoop, with a Function inner source, or an entry (inner) face stay
refused UNMEASURED."""
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
gates.append(("C1 16 rule rows + 3 FSIT rows", len(nt["rows"]) == 16 and len(nt["skipped"]) == 3))


def lt_case(loop="WhileLoop", inner_cls="SubVI", src_tc="OuterTerminal"):
    """card 152-b1-3: a LoopTunnel source 'min slot' (diag_c152_b1_2_cross.log:93) -> face names or the refusal text."""
    src = {"term_uid": 1, "term_name": "min slot", "is_source": True, "wire_uid": 5, "owner_uid": 2, "owner_class": "LoopTunnel",
           "frame_diagram": 1, "term_class": src_tc}
    rows = [src, {"term_uid": 3, "term_name": "min slot", "is_source": False, "wire_uid": 6, "owner_uid": 2,
                  "owner_class": "LoopTunnel", "frame_diagram": 9, "term_class": "InnerTerminal"},
            {"term_uid": 4, "term_name": "min slot", "is_source": True, "wire_uid": 6, "owner_uid": 7, "owner_class": inner_cls,
             "frame_diagram": 9, "term_class": "Terminal"}]
    try:
        return SS.cross_face_names({"terminals": rows, "objs": [], "neg": 0, "owners": {"9": [loop, 8]}}, src,
                                   {"src": 1, "dst": "x"}, [{}])
    except SS.SimError as e:
        return str(e)


for lab, kw, ok in (("L1 measured LoopTunnel (WhileLoop, SubVI inner) -> 'min slot' both faces", {},
                     lambda g: g == [{"in": "min slot", "out": "min slot", "other": "min slot"}]),
                    ("L2 LoopTunnel on a ForLoop refused UNMEASURED", {"loop": "ForLoop"}, lambda g: "UNMEASURED" in str(g)),
                    ("L3 LoopTunnel with a Function inner source refused UNMEASURED", {"inner_cls": "Function"},
                     lambda g: "UNMEASURED" in str(g)),
                    ("L4 LoopTunnel source not an OuterTerminal refused UNMEASURED", {"src_tc": "InnerTerminal"},
                     lambda g: "UNMEASURED" in str(g))):
    g_ = lt_case(**kw)
    gates.append((lab, ok(g_)))
    print("  {0}  {1}  {2}".format("PASS" if ok(g_) else "FAIL", lab, str(g_)[:160]))
n_pass = sum(1 for _l, ok in gates if ok)
n_fail = len(gates) - n_pass
first = next((l for l, ok in gates if not ok), None)
print("=== GATES: {0} pass / {1} fail{2}".format(n_pass, n_fail, "; failing: " + first if first else ""))
print(protocol.result_line(protocol.make_result(n_pass, n_fail, first)))
sys.exit(0 if n_fail == 0 else 1)
# ---
# labview: none
# hardware: none
# ---
