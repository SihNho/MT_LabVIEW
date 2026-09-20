"""probe_castfree_ladders.py - cycle 1 of the autonomous loop: do the peer's cast-free ladders compile?

PEER VERDICT ON THE DAY'S PLAN (archive/peer/2026-09-14-autonomous-loop-plan.md), which this run tests:
  * Node.Label is NOT an identity - "you must display the label at least once before this property can return
    the text", and it is a user label, not the callee. REJECTED for identification.
  * `AbstractDiagram.SubVIs[]` (6375802) is documented as returning SubVI references - if statically SubVI-typed,
    `SubVI.VI Name` (635E401) / `VI Path` (635E403) attach with NO cast. That is the identity route, and the
    peer's condition is "prove it with one donor compile/run". This is that run.
  * `Control.Terminal` (6332006) returns a control's diagram terminal; `Terminal.Is Source?` (634A003) and
    `Terminal.Connected Wire` (634A000) then give wiring and direction. Same condition: prove it compiles.

Every claim below is a COMPILE result (ExecState after wiring), which is a measurement, and a CONTROL runs first:
the donors' own chains are ExecState 1 before anything is touched; if that baseline is not 1, the run is INVALID.

Terminal NAMES are never guessed - after each property node is created, its output terminal name is read back
with net_map and used verbatim (the trap that cost four build cycles yesterday: VIName, VIPath, ClassName,
Outer Term all differ from the documented long names).

SAFETY: two scratch copies, deleted at the end. Nothing existing is modified, nothing is saved.
  py tools/bgrun.py --max-min 15 --log tools/bench/probe_castfree.log -- py -u tools/recipes/probe_castfree_ladders.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

A_SRC = os.path.join(g.CLAUDEDEV, "OpNodeInfo_v0.vi")   # VI -> Block Diagram -> Nodes[] -> IA -> Node.Label
A = os.path.join(g.CLAUDEDEV, "SCRATCH_ladder_subvis.vi")
B_SRC = os.path.join(g.CLAUDEDEV, "OpFPLabels_v0.vi")   # VI -> Front Panel -> Panel.Controls[] -> IA -> Control.Label
B = os.path.join(g.CLAUDEDEV, "SCRATCH_ladder_ctlterm.vi")

P_SUBVIS = "6375802"     # AbstractDiagram.SubVIs[]
P_VINAME = "635E401"     # SubVI.VI Name
P_VIPATH = "635E403"     # SubVI.VI Path
P_CTLTERM = "6332006"    # Control.Terminal
P_ISSRC = "634A003"      # Terminal.Is Source?
P_CONNW = "634A000"      # Terminal.Connected Wire
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


def nodes_of(vi, diagram=0):
    nodes, _w = g.net_map(vi, diagram, max_nodes=80, max_terms=24)
    return {uid: [t for _ti, t, _w2 in terms if t] for _i, (uid, _l, terms) in nodes.items()}


def node_with_terminal(vi, name):
    for uid, terms in nodes_of(vi).items():
        if name in terms:
            return uid
    return None


def out_terminal_of(vi, uid):
    """The property node's method-specific output name, read back rather than guessed."""
    extra = [t for t in nodes_of(vi).get(uid, []) if t not in GENERIC]
    return extra[-1] if extra else None


def pidx(vi, uid):
    return [o["uid"] for o in g.report(vi, "Property")].index(uid)


def add_pn(vi, cls, props, loc):
    new = g.build_property(vi, cls, props, loc)
    uid = new[-1]["uid"]
    return uid, out_terminal_of(vi, uid)


def wire_pn(vi, src_uid, src_term, dst_uid):
    g.wire(vi, "Property", pidx(vi, src_uid), src_term, "Property", pidx(vi, dst_uid), "reference")


def record(name, ok, detail):
    print(f"   -> {'PASS' if ok else 'FAIL'}: {detail}", flush=True)
    RESULTS.append((name, ok, detail))


def ladder_subvis():
    print("\n######## LADDER 1: Block Diagram -> SubVIs[] -> SubVI.VI Name / VI Path ########", flush=True)
    fresh(A_SRC, A)
    es0 = g.exec_state(A)
    print(f"   CONTROL: donor chain ExecState = {es0} (must be 1)", flush=True)
    if es0 != 1:
        record("L1 control", False, "donor not runnable - INVALID")
        return
    record("L1 control", True, "donor ExecState 1")
    diag_pn = node_with_terminal(A, "Diagram")
    print(f"   the VI.Block Diagram property node is uid {diag_pn}", flush=True)
    if diag_pn is None:
        record("L1 SubVIs[]", False, "cannot find the Diagram node")
        return

    print("   predict: an AbstractDiagram-class node accepts the Diagram ref; ExecState stays 1", flush=True)
    sv_uid, sv_out = add_pn(A, "VI Server:AbstractDiagram", [(P_SUBVIS, False)], (1300, 300))
    print(f"   SubVIs[] node uid {sv_uid}, output terminal read back = {sv_out!r}", flush=True)
    wire_pn(A, diag_pn, "Diagram", sv_uid)
    es1 = g.exec_state(A)
    record("L1 SubVIs[] attaches", es1 == 1 and bool(sv_out), f"ExecState {es1}, out {sv_out!r}")

    print("   predict: Index Array on SubVIs[] then a SubVI-class node - ExecState 1 IF statically SubVI-typed",
          flush=True)
    ia = g.build_index_array(A, (1500, 300))
    ia_uid = ia[-1]["uid"] if ia else None
    g.wire(A, "Property", pidx(A, sv_uid), sv_out, "IndexArray",
           [o["uid"] for o in g.report(A, "IndexArray")].index(ia_uid), "array")
    name_uid, name_out = add_pn(A, "VI Server:SubVI", [(P_VINAME, False), (P_VIPATH, False)], (1700, 300))
    print(f"   SubVI node uid {name_uid}, outputs read back = {nodes_of(A).get(name_uid)}", flush=True)
    g.wire(A, "IndexArray", [o["uid"] for o in g.report(A, "IndexArray")].index(ia_uid), "element",
           "Property", pidx(A, name_uid), "reference")
    es2 = g.exec_state(A)
    record("L1 SubVI.VI Name on SubVIs[] element (NO cast)", es2 == 1,
           f"ExecState {es2} - {'no cast needed: IDENTITY ROUTE OPEN' if es2 == 1 else 'refused: cast still required'}")


def ladder_ctlterm():
    print("\n######## LADDER 2: Panel.Controls[] -> Control.Terminal -> Terminal.Is Source? / Connected Wire ########",
          flush=True)
    fresh(B_SRC, B)
    es0 = g.exec_state(B)
    print(f"   CONTROL: donor chain ExecState = {es0} (must be 1)", flush=True)
    if es0 != 1:
        record("L2 control", False, "donor not runnable - INVALID")
        return
    record("L2 control", True, "donor ExecState 1")
    ia_uids = [o["uid"] for o in g.report(B, "IndexArray")]
    print(f"   Index Arrays in donor: {ia_uids}", flush=True)
    if not ia_uids:
        record("L2 Control.Terminal", False, "no Index Array in donor")
        return
    ia_uid = ia_uids[0]

    print("   predict: a Control-class node accepts IA.element (Controls[] is Control-typed); ExecState 1",
          flush=True)
    ct_uid, ct_out = add_pn(B, "VI Server:Control", [(P_CTLTERM, False)], (1300, 300))
    print(f"   Control.Terminal node uid {ct_uid}, output read back = {ct_out!r}", flush=True)
    g.wire(B, "IndexArray", ia_uids.index(ia_uid), "element", "Property", pidx(B, ct_uid), "reference",
           branch=True)
    es1 = g.exec_state(B)
    record("L2 Control.Terminal attaches", es1 == 1 and bool(ct_out), f"ExecState {es1}, out {ct_out!r}")

    print("   predict: a Terminal-class node accepts Control.Terminal's output without a cast; ExecState 1",
          flush=True)
    tm_uid, _ = add_pn(B, "VI Server:Terminal", [(P_ISSRC, False), (P_CONNW, False)], (1550, 300))
    print(f"   Terminal node uid {tm_uid}, outputs read back = {nodes_of(B).get(tm_uid)}", flush=True)
    wire_pn(B, ct_uid, ct_out, tm_uid)
    es2 = g.exec_state(B)
    record("L2 Terminal.Is Source?/Connected Wire on Control.Terminal (NO cast)", es2 == 1,
           f"ExecState {es2} - {'WIRING+DIRECTION ROUTE OPEN' if es2 == 1 else 'refused'}")


def main():
    g._lv = None
    for fn in (ladder_subvis, ladder_ctlterm):
        try:
            fn()
        except Exception as e:
            print(f"   EXC {str(e)[:220]}", flush=True)
            RESULTS.append((fn.__name__, False, f"exception {str(e)[:120]}"))
    print("\n################ SUMMARY ################", flush=True)
    for name, ok, detail in RESULTS:
        print(f"  {'PASS' if ok else 'FAIL'}  {name:58} {detail}", flush=True)
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
