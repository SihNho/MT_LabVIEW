"""probe_castfree_ladders3.py - cycle 2: compile the two cast-free ladders, now that attach is deterministic.

WHAT CHANGED SINCE RUNS 1-2 (tools/bench/probe_castfree*.log): those runs judged "did the property attach" by
re-finding the new node through net_map - and net_map does not see nodes created by another op in the same
session (measured five ways, tools/bench/probe_stale_nodes.log). So every "not attached" they printed was void.
`build_property` now drives OpBuildPN_v1 and RAISES on the creator's own error (1077 for an unsupported ID), and
both questioned IDs were shown to attach cleanly (build_opbuildpn_v1c.log). This run therefore:

  * never consults the walker about a new node - attach is proven by build_property returning at all;
  * feeds every new node from the upstream node's unwired `reference out` (peer-approved, same static type);
  * resolves each new node's OUTPUT terminal name by TRYING candidates with wire() - a wrong name raises 5001
    (name absent) and costs one op run, an illegal-but-existing name is declined silently (count check catches
    it). Known from measurement: SubVI.VI Name -> 'VIName', VI Path -> 'VIPath', Control.Terminal -> 'Terminal'
    (seen once when the walker happened to list it). Unknown: SubVIs[] (by analogy with 'Nodes[]': 'SubVIs[]'),
    Is Source? and Connected Wire.
  * judges each ladder by ExecState after the LAST wire - the compile verdict the plan review asked for.

Controls: each donor is ExecState 1 before anything is touched (INVALID otherwise). Scratch copies, deleted;
nothing saved.
  py tools/bgrun.py --max-min 15 --log tools/bench/probe_castfree3.log -- py -u tools/recipes/probe_castfree_ladders3.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

A_SRC = os.path.join(g.CLAUDEDEV, "OpNodeInfo_v0.vi")
A = os.path.join(g.CLAUDEDEV, "SCRATCH_ladder3_subvis.vi")
B_SRC = os.path.join(g.CLAUDEDEV, "OpFPLabels_v0.vi")
B = os.path.join(g.CLAUDEDEV, "SCRATCH_ladder3_ctlterm.vi")

P_SUBVIS, P_VINAME, P_VIPATH = "6375802", "635E401", "635E403"
P_CTLTERM, P_ISSRC, P_CONNW = "6332006", "634A003", "634A000"
NAME_CANDIDATES = {
    P_SUBVIS: ["SubVIs[]", "SubVIs", "Sub VIs[]"],
    P_CTLTERM: ["Terminal", "Term"],
    P_ISSRC: ["IsSource?", "Is Source?", "IsSrc?", "Is Source", "IsSource"],
    P_CONNW: ["ConnectedWire", "Connected Wire", "ConnWire", "Wire"],
}
g._run.__defaults__ = (6.0, 120.0)
RESULTS = []


def rec(name, ok, detail):
    print(f"   -> {'PASS' if ok else 'FAIL'}: {name}: {detail}", flush=True)
    RESULTS.append((name, ok, detail))


def fresh(src, dst):
    try:
        g.close_panel(dst)
        time.sleep(0.3)
    except Exception:
        pass
    if os.path.exists(dst):
        try:
            os.remove(dst)
        except OSError:
            pass
    shutil.copyfile(src, dst)
    g.open_panel(dst)
    time.sleep(0.9)


def node_with_terminal(vi, name):
    nodes, _w = g.net_map(vi, 0, max_nodes=80, max_terms=24)
    for _i, (uid, _l, terms) in nodes.items():
        if any(t == name for _ti, t, _w2 in terms):
            return uid
    return None


def pidx(vi, uid):
    return [o["uid"] for o in g.report(vi, "Property")].index(uid)


def wire_by_candidates(vi, src_uid, cands, dst_cls, dst_i, dst_term):
    """Try each candidate output name; return the one that wired (5001 = name absent -> next candidate)."""
    for name in cands:
        try:
            g.wire(vi, "Property", pidx(vi, src_uid), name, dst_cls, dst_i, dst_term)
            return name
        except RuntimeError as e:
            if "5001" in str(e):
                continue
            raise RuntimeError(f"{name!r}: {str(e)[:120]}")
    return None


def ladder_subvis():
    print("\n######## LADDER 1c: Nodes[]-node.reference out -> SubVIs[] -> IA -> SubVI.VI Name/VI Path ########", flush=True)
    fresh(A_SRC, A)
    es = g.exec_state(A)
    rec("L1 control (donor runnable)", es == 1, f"ExecState {es}")
    if es != 1:
        return
    nodes_pn = node_with_terminal(A, "Nodes[]")
    sv = g.build_property(A, "VI Server:AbstractDiagram", [(P_SUBVIS, False)], (1300, 300))[-1]["uid"]
    rec("L1 SubVIs[] node created (creator error clean)", True, f"uid {sv}")
    g.wire(A, "Property", pidx(A, nodes_pn), "reference out", "Property", pidx(A, sv), "reference")
    es1 = g.exec_state(A)
    rec("L1 AbstractDiagram node accepts the Diagram ref", es1 == 1, f"ExecState {es1}")
    ia_uid = g.build_index_array(A, (1500, 300))[-1]["uid"]
    ia_i = [o["uid"] for o in g.report(A, "IndexArray")].index(ia_uid)
    sv_name = wire_by_candidates(A, sv, NAME_CANDIDATES[P_SUBVIS], "IndexArray", ia_i, "array")
    rec("L1 SubVIs[] output wired to Index Array", sv_name is not None, f"output terminal name = {sv_name!r}")
    if sv_name is None:
        return
    nm = g.build_property(A, "VI Server:SubVI", [(P_VINAME, False), (P_VIPATH, False)], (1700, 300))[-1]["uid"]
    g.wire(A, "IndexArray", ia_i, "element", "Property", pidx(A, nm), "reference")
    es2 = g.exec_state(A)
    rec("L1 SubVI-class node accepts SubVIs[] element WITHOUT cast (identity route)", es2 == 1, f"ExecState {es2}")


def ladder_ctlterm():
    print("\n######## LADDER 2c: Control.Label-node.reference out -> Control.Terminal -> Is Source?/Connected Wire ########",
          flush=True)
    fresh(B_SRC, B)
    es = g.exec_state(B)
    rec("L2 control (donor runnable)", es == 1, f"ExecState {es}")
    if es != 1:
        return
    lab_pn = node_with_terminal(B, "Label")
    ct = g.build_property(B, "VI Server:Control", [(P_CTLTERM, False)], (1300, 300))[-1]["uid"]
    rec("L2 Control.Terminal node created (creator error clean)", True, f"uid {ct}")
    g.wire(B, "Property", pidx(B, lab_pn), "reference out", "Property", pidx(B, ct), "reference")
    es1 = g.exec_state(B)
    rec("L2 Control-class node accepts the Control ref", es1 == 1, f"ExecState {es1}")
    tm = g.build_property(B, "VI Server:Terminal", [(P_ISSRC, False), (P_CONNW, False)], (1550, 300))[-1]["uid"]
    ct_name = wire_by_candidates(B, ct, NAME_CANDIDATES[P_CTLTERM], "Property", pidx(B, tm), "reference")
    rec("L2 Control.Terminal output wired to the Terminal node", ct_name is not None, f"output name = {ct_name!r}")
    es2 = g.exec_state(B)
    rec("L2 Terminal-class node accepts Control.Terminal output WITHOUT cast (wiring/direction route)",
        es2 == 1 and ct_name is not None, f"ExecState {es2}")


def main():
    g._lv = None
    for fn in (ladder_subvis, ladder_ctlterm):
        try:
            fn()
        except Exception as e:
            print(f"   OBSERVED: EXC {str(e)[:240]}", flush=True)
            RESULTS.append((fn.__name__, False, f"exception {str(e)[:140]}"))
    print("\n################ SUMMARY ################", flush=True)
    for name, ok, detail in RESULTS:
        print(f"  {'PASS' if ok else 'FAIL'}  {name:78} {detail}", flush=True)
    for vi in (A, B):
        try:
            g.close_panel(vi)
            time.sleep(0.3)
            os.remove(vi)
        except Exception as e:
            print("cleanup:", str(e)[:80], flush=True)
    print("scratch deleted", flush=True)
    return 0 if all(ok for _n, ok, _d in RESULTS) else 3


if __name__ == "__main__":
    sys.exit(main())
