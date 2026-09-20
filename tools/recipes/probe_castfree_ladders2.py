"""probe_castfree_ladders2.py - cycle 1b: same two ladders, with the branch bug removed and the attach read first.

RUN 1 (tools/bench/probe_castfree.log) failed both ladders, and the failures were NOT the questions being asked:

  * `wire()` was asked to BRANCH from outputs that were already wired ('Diagram' -> Nodes[]; IA.element ->
    Control.Label). Branching from a wired source is declined silently (documented in wire()'s own docstring),
    and with branch=True the count check that would have caught it was skipped. Result: the new property node's
    REQUIRED `reference` input stayed unwired, which alone breaks a VI. So "ExecState 0" said nothing about the
    class question. Diagnosis under review: archive/peer/2026-09-14-castfree-ladders-fail1.md.
  * Separately, the AbstractDiagram.SubVIs[] node (6375802) came up with NO property terminal - it did not attach.
    That is a real finding about the ID, not about wiring, and it is recorded regardless of what follows.

THIS RUN removes the wiring confound: every new node is fed from the upstream property node's `reference out`
pass-through, which is UNWIRED in both donors and carries the same static type (peer question (b) - if the peer
says otherwise this run's positive results are void and are marked so). It also reads back each new node's
terminal list BEFORE wiring, so "did the property attach" and "does the class accept the ref" are answered
separately, which run 1 conflated.

Controls first, INVALID if they fail. Scratch copies, deleted at the end. Nothing saved.
  py tools/bgrun.py --max-min 15 --log tools/bench/probe_castfree2.log -- py -u tools/recipes/probe_castfree_ladders2.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

A_SRC = os.path.join(g.CLAUDEDEV, "OpNodeInfo_v0.vi")
A = os.path.join(g.CLAUDEDEV, "SCRATCH_ladder2_subvis.vi")
B_SRC = os.path.join(g.CLAUDEDEV, "OpFPLabels_v0.vi")
B = os.path.join(g.CLAUDEDEV, "SCRATCH_ladder2_ctlterm.vi")

P_SUBVIS, P_VINAME, P_VIPATH = "6375802", "635E401", "635E403"
P_CTLTERM, P_ISSRC, P_CONNW = "6332006", "634A003", "634A000"
GENERIC = {"reference", "reference out", "error in (no error)", "error out", "error in"}
g._run.__defaults__ = (6.0, 120.0)
RESULTS = []


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


def nodes_of(vi):
    nodes, _w = g.net_map(vi, 0, max_nodes=80, max_terms=24)
    return {uid: [(t, w) for _ti, t, w in terms if t] for _i, (uid, _l, terms) in nodes.items()}


def node_with_terminal(vi, name):
    for uid, terms in nodes_of(vi).items():
        if any(t == name for t, _w in terms):
            return uid
    return None


def pidx(vi, uid):
    return [o["uid"] for o in g.report(vi, "Property")].index(uid)


def add_pn(vi, cls, props, loc, label):
    """Create, then READ BACK the terminal list before any wiring: attach and accept are separate questions."""
    new = g.build_property(vi, cls, props, loc)
    uid = new[-1]["uid"]
    terms = nodes_of(vi).get(uid, [])
    extra = [t for t, _w in terms if t not in GENERIC]
    print(f"   {label}: uid {uid}, property terminals = {extra}", flush=True)
    rec(f"{label} ATTACHED", bool(extra), f"property terminals {extra}")
    return uid, (extra[-1] if extra else None)


def chain(vi, src_uid, dst_uid):
    """Feed dst.reference from src.'reference out' - unwired in these donors, so no branch is needed."""
    g.wire(vi, "Property", pidx(vi, src_uid), "reference out", "Property", pidx(vi, dst_uid), "reference")


def rec(name, ok, detail):
    print(f"   -> {'PASS' if ok else 'FAIL'}: {name}: {detail}", flush=True)
    RESULTS.append((name, ok, detail))


def ladder_subvis():
    print("\n######## LADDER 1b: Nodes[]-node.reference out -> SubVIs[] -> IA -> SubVI.VI Name ########", flush=True)
    fresh(A_SRC, A)
    es = g.exec_state(A)
    rec("L1 control (donor runnable)", es == 1, f"ExecState {es}")
    if es != 1:
        return
    nodes_pn = node_with_terminal(A, "Nodes[]")
    ro = [w for t, w in nodes_of(A)[nodes_pn] if t == "reference out"]
    print(f"   Nodes[] node uid {nodes_pn}; its 'reference out' wire = {ro} (0 = free to use)", flush=True)

    sv_uid, sv_out = add_pn(A, "VI Server:AbstractDiagram", [(P_SUBVIS, False)], (1300, 300), "SubVIs[] 6375802")
    if sv_out is None:
        # Second reading of the same ID failure, on a fresh instance: recorded, and the ladder stops here.
        rec("L1 SubVIs[] usable", False, "property did not attach (twice now, fresh LabVIEW) - ID dead for this creator")
        return
    chain(A, nodes_pn, sv_uid)
    es1 = g.exec_state(A)
    rec("L1 AbstractDiagram node accepts Diagram-typed ref via reference out", es1 == 1, f"ExecState {es1}")
    ia = g.build_index_array(A, (1500, 300))
    ia_uid = ia[-1]["uid"]
    ia_i = [o["uid"] for o in g.report(A, "IndexArray")].index(ia_uid)
    g.wire(A, "Property", pidx(A, sv_uid), sv_out, "IndexArray", ia_i, "array")
    nm_uid, _ = add_pn(A, "VI Server:SubVI", [(P_VINAME, False), (P_VIPATH, False)], (1700, 300), "SubVI.VI Name/Path")
    g.wire(A, "IndexArray", ia_i, "element", "Property", pidx(A, nm_uid), "reference")
    es2 = g.exec_state(A)
    rec("L1 SubVI-class node accepts SubVIs[] element WITHOUT cast", es2 == 1, f"ExecState {es2}")


def ladder_ctlterm():
    print("\n######## LADDER 2b: Control.Label-node.reference out -> Control.Terminal -> Terminal.Is Source?/Connected Wire ########",
          flush=True)
    fresh(B_SRC, B)
    es = g.exec_state(B)
    rec("L2 control (donor runnable)", es == 1, f"ExecState {es}")
    if es != 1:
        return
    lab_pn = node_with_terminal(B, "Label")
    ro = [w for t, w in nodes_of(B)[lab_pn] if t == "reference out"]
    print(f"   Control.Label node uid {lab_pn}; its 'reference out' wire = {ro} (0 = free to use)", flush=True)

    ct_uid, ct_out = add_pn(B, "VI Server:Control", [(P_CTLTERM, False)], (1300, 300), "Control.Terminal 6332006")
    if ct_out is None:
        return
    chain(B, lab_pn, ct_uid)
    es1 = g.exec_state(B)
    rec("L2 Control-class node accepts Control-typed ref via reference out", es1 == 1, f"ExecState {es1}")

    tm_uid, _ = add_pn(B, "VI Server:Terminal", [(P_ISSRC, False), (P_CONNW, False)], (1550, 300),
                       "Terminal.Is Source?/Connected Wire")
    g.wire(B, "Property", pidx(B, ct_uid), ct_out, "Property", pidx(B, tm_uid), "reference")
    es2 = g.exec_state(B)
    rec("L2 Terminal-class node accepts Control.Terminal output WITHOUT cast", es2 == 1, f"ExecState {es2}")


def main():
    g._lv = None
    for fn in (ladder_subvis, ladder_ctlterm):
        try:
            fn()
        except Exception as e:
            print(f"   OBSERVED: EXC {str(e)[:220]}", flush=True)
            RESULTS.append((fn.__name__, False, f"exception {str(e)[:120]}"))
    print("\n################ SUMMARY ################", flush=True)
    for name, ok, detail in RESULTS:
        print(f"  {'PASS' if ok else 'FAIL'}  {name:64} {detail}", flush=True)
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
