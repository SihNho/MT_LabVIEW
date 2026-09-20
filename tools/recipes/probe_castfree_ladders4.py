"""probe_castfree_ladders4.py - node fault or wire fault? ExecState at every step, on both ladders.

Run 3 (tools/bench/probe_castfree3.log) established, with the creator-checked builder: SubVIs[] 6375802 and
Control.Terminal 6332006 both ATTACH, their outputs are named 'SubVIs[]' and 'Terminal', and yet the VI reads
ExecState 0 right after the first `reference` wire in both ladders. Run 3 did not read ExecState BETWEEN creation
and wiring, so it cannot say whether the wire broke the VI or the node was already broken. Peer review of the
anomaly: archive/peer/2026-09-14-castfree-ladders-execstate0.md.

This run reads ExecState (and the wire count) at each point of a sequence designed to isolate the fault:

    E0  donor pristine                      expect 1  (control)
    E1  after build_property                expect 0  (a required `reference` is unwired - documented)
    E2  after wiring reference out -> ref   measured 0 in run 3 - the question
    E3  after Remove Bad Wires              1 and wires-1  -> the WIRE was illegal
                                            0             -> the NODE itself is the fault
    E4  after deleting the new node         1 -> the node was the only fault; 0 -> something else got mutated

Both ladders, same sequence, controls first, scratch deleted, nothing saved.
  py tools/bgrun.py --max-min 12 --log tools/bench/probe_castfree4.log -- py -u tools/recipes/probe_castfree_ladders4.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

CASES = [
    ("L1 SubVIs[] on AbstractDiagram from Nodes[]-node.reference out",
     os.path.join(g.CLAUDEDEV, "OpNodeInfo_v0.vi"), os.path.join(g.CLAUDEDEV, "SCRATCH_l4_subvis.vi"),
     "Nodes[]", "VI Server:AbstractDiagram", "6375802"),
    ("L2 Control.Terminal on Control from Control.Label-node.reference out",
     os.path.join(g.CLAUDEDEV, "OpFPLabels_v0.vi"), os.path.join(g.CLAUDEDEV, "SCRATCH_l4_ctlterm.vi"),
     "Label", "VI Server:Control", "6332006"),
    # A CONTROL for the whole sequence: a property the donor ALREADY uses on the same class, chained the same
    # way. If this also ends broken, the fault is the chaining method, not the questioned properties.
    ("CONTROL GObject.Position on GObject from Nodes[]-node.reference out",
     os.path.join(g.CLAUDEDEV, "OpNodeInfo_v0.vi"), os.path.join(g.CLAUDEDEV, "SCRATCH_l4_control.vi"),
     "Nodes[]", "VI Server:GObject", "632A800"),
]
g._run.__defaults__ = (6.0, 120.0)


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


def st(vi, tag):
    es, w = g.exec_state(vi), g.count(vi, "Wire")
    print(f"   {tag:44} ExecState={es} Wire={w}", flush=True)
    return es, w


def run_case(label, src, vi, up_term, cls, pid):
    print(f"\n######## {label} ########", flush=True)
    fresh(src, vi)
    e0, _ = st(vi, "E0 donor pristine (control, expect 1)")
    if e0 != 1:
        print("   INVALID: donor not runnable", flush=True)
        return
    up = node_with_terminal(vi, up_term)
    new = g.build_property(vi, cls, [(pid, False)], (1300, 300))[-1]["uid"]
    e1, w1 = st(vi, "E1 after build_property (expect 0: unwired ref)")
    g.wire(vi, "Property", pidx(vi, up), "reference out", "Property", pidx(vi, new), "reference")
    e2, w2 = st(vi, "E2 after reference wire (the question)")
    g.remove_bad_wires_scripted(vi)
    e3, w3 = st(vi, "E3 after Remove Bad Wires")
    g.delete_object(vi, "Property", pidx(vi, new))
    g.remove_bad_wires_scripted(vi)
    e4, w4 = st(vi, "E4 after deleting the new node")
    if e2 == 1:
        verdict = "OK - the ladder compiles (run 3 differed; see E-steps)"
    elif e3 == 1 and w3 < w2:
        verdict = "the WIRE was illegal (Remove Bad Wires fixed it) -> type/class mismatch at the reference input"
    elif e3 == 0 and e4 == 1:
        verdict = "the NODE itself is broken even when wired -> something on the node besides `reference`"
    else:
        verdict = "neither wire nor node alone explains it -> another mutation; do not conclude"
    print(f"   VERDICT: {verdict}", flush=True)
    try:
        g.close_panel(vi)
        time.sleep(0.3)
        os.remove(vi)
    except Exception as e:
        print("   cleanup:", str(e)[:80], flush=True)


def main():
    g._lv = None
    for c in CASES:
        try:
            run_case(*c)
        except Exception as e:
            print(f"   OBSERVED: EXC {str(e)[:220]}", flush=True)
    print("\nscratch deleted", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
