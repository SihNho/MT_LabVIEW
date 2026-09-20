"""probe_castfree_ladders5.py - cycle 2 retry of the two cast-free ladders with a walker that cleans up after itself.

WHY RUNS 3-4 ARE VOID (tools/bench/probe_builder_artifact.log, peer archive/peer/2026-09-14-builder-leaves-artifact.md):
every earlier ladder run called `net_map` on the target right after its pristine read, and ONE net_map call drops ~75
untyped junk Invoke nodes on the target (docs/keystone-op-spec.md s33) - enough on its own to hold ExecState at 0.
So E1/E2 "ExecState 0" in runs 3-4 never measured the ladders; they measured the walker. `net_map` now purges its own
junk and runs Remove Bad Wires (gscript.py, 2026-09-14). This run repeats the ladders under that walker and, because
the walker now works, reads every new node's terminal names off the machine instead of guessing candidates.

PREDICTION CONTRACT (machine-checkable rows below; a miss on any CONTROL row voids the run):
    P0  donor pristine                                   ExecState 1            (control)
    P1  after node_with_terminal (one net_map)           ExecState 1, Invoke count == pristine   <- purge verified
    P2  after build_property                             ExecState 0 (required `reference` unwired - documented)
    P3  after reference wire                             ExecState 1            <- THE QUESTION (was 0 in runs 3-4)
    P4  new node's terminals read by net_map             names printed; exactly one non-generic output
    P5  after the second hop is wired                    ExecState 1            (identity / panel-wiring route compiles)
Controls: a GObject.Position ladder (a property the donor already uses) on the same sequence.
KNOWN DEFECT IN THE CONTROL (seen in tools/bench/probe_castfree5.log): its P5 wires the Position OUTPUT (a cluster)
into the second node's `reference` input, so the control's P5 is broken BY DESIGN and its FAIL is void - the control
is valid through P4 only. A correct control would feed the second hop from `reference out`. Left as is so the log and
the recipe agree; fix before reusing the control for a P5-level claim.

Scratch copies only, deleted at the end; nothing saved.
  py tools/bgrun.py --max-min 20 --log tools/bench/probe_castfree5.log -- py -u tools/recipes/probe_castfree_ladders5.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

GENERIC = {"reference", "reference out", "error in (no error)", "error out", "error in"}
P_SUBVIS, P_VINAME, P_VIPATH = "6375802", "635E401", "635E403"
P_CTLTERM, P_ISSRC, P_CONNW = "6332006", "634A003", "634A000"
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


def walk(vi):
    nodes, _w = g.net_map(vi, 0, max_nodes=80, max_terms=24)
    return {u: [t for _ti, t, _w2 in terms if t] for _i, (u, _l, terms) in nodes.items()}


def node_with_terminal(vi, name):
    for uid, terms in walk(vi).items():
        if name in terms:
            return uid
    return None


def pidx(vi, uid):
    return [o["uid"] for o in g.report_all(vi, "Property")].index(uid)


def st(vi, tag, expect):
    es = g.exec_state(vi)
    inv = len(g.report_all(vi, "Invoke"))
    print(f"   {tag:52} ExecState={es} Invoke={inv}", flush=True)
    rec(tag, es == expect, f"ExecState {es} (expected {expect}), Invoke {inv}")
    return es, inv


def new_node_output(vi, uid, tag):
    """P4: read the new node's terminal names with the (now self-purging) walker; return its one data output."""
    terms = walk(vi).get(uid)
    if terms is None:
        rec(f"{tag} new node visible to the walker", False, "not in walk")
        return None
    outs = [t for t in terms if t not in GENERIC]
    rec(f"{tag} new node terminals", len(outs) == 1, f"terms={terms} -> data terminals {outs}")
    return outs[0] if len(outs) == 1 else None


def ladder(label, src, vi, up_term, cls1, pid1, cls2, pids2):
    print(f"\n######## {label} ########", flush=True)
    fresh(src, vi)
    e0, inv0 = st(vi, "P0 donor pristine (control)", 1)
    if e0 != 1:
        print("   INVALID: donor not runnable", flush=True)
        return
    up = node_with_terminal(vi, up_term)
    e1, inv1 = st(vi, "P1 after one net_map (purge check)", 1)
    rec("P1 Invoke count back to pristine after net_map", inv1 == inv0, f"{inv0} -> {inv1}")
    if up is None:
        rec(f"upstream node with terminal {up_term!r} found", False, "walker did not list it")
        return
    n1 = g.build_property(vi, cls1, [(pid1, False)], (1300, 300))[-1]["uid"]
    st(vi, "P2 after build_property (unwired reference)", 0)
    g.wire(vi, "Property", pidx(vi, up), "reference out", "Property", pidx(vi, n1), "reference")
    st(vi, "P3 after reference wire (THE QUESTION)", 1)
    out1 = new_node_output(vi, n1, "P4")
    if out1 is None:
        return
    if cls2 == "IndexArray":
        ia = g.build_index_array(vi, (1500, 300))[-1]["uid"]
        ia_i = [o["uid"] for o in g.report_all(vi, "IndexArray")].index(ia)
        g.wire(vi, "Property", pidx(vi, n1), out1, "IndexArray", ia_i, "array")
        n2 = g.build_property(vi, "VI Server:SubVI", [(p, False) for p in pids2], (1700, 300))[-1]["uid"]
        g.wire(vi, "IndexArray", ia_i, "element", "Property", pidx(vi, n2), "reference")
    else:
        n2 = g.build_property(vi, cls2, [(p, False) for p in pids2], (1550, 300))[-1]["uid"]
        g.wire(vi, "Property", pidx(vi, n1), out1, "Property", pidx(vi, n2), "reference")
    st(vi, "P5 after second hop wired (route compiles?)", 1)
    terms2 = walk(vi).get(n2)
    rec("P5 second node terminals read", terms2 is not None, f"{terms2}")


CASES = [
    ("CONTROL: GObject.Position from Nodes[]-node (donor already uses it)",
     os.path.join(g.CLAUDEDEV, "OpNodeInfo_v0.vi"), os.path.join(g.CLAUDEDEV, "SCRATCH_l5_control.vi"),
     "Nodes[]", "VI Server:GObject", "632A800", "VI Server:GObject", ["632A813"]),
    ("L1 identity: Nodes[]-node -> AbstractDiagram.SubVIs[] -> IA -> SubVI.VI Name/VI Path",
     os.path.join(g.CLAUDEDEV, "OpNodeInfo_v0.vi"), os.path.join(g.CLAUDEDEV, "SCRATCH_l5_subvis.vi"),
     "Nodes[]", "VI Server:AbstractDiagram", P_SUBVIS, "IndexArray", [P_VINAME, P_VIPATH]),
    ("L2 panel wiring: Label-node -> Control.Terminal -> Terminal.Is Source?/Connected Wire",
     os.path.join(g.CLAUDEDEV, "OpFPLabels_v0.vi"), os.path.join(g.CLAUDEDEV, "SCRATCH_l5_ctlterm.vi"),
     "Label", "VI Server:Control", P_CTLTERM, "VI Server:Terminal", [P_ISSRC, P_CONNW]),
]


def main():
    g._lv = None
    for c in CASES:
        try:
            ladder(*c)
        except Exception as e:
            print(f"   OBSERVED: EXC {str(e)[:240]}", flush=True)
            RESULTS.append((c[0], False, f"exception {str(e)[:140]}"))
        try:
            g.close_panel(c[2])
            time.sleep(0.3)
            os.remove(c[2])
        except Exception as e:
            print("   cleanup:", str(e)[:80], flush=True)
    print("\n################ SUMMARY ################", flush=True)
    for name, ok, detail in RESULTS:
        print(f"  {'PASS' if ok else 'FAIL'}  {name:70} {detail}", flush=True)
    print("scratch deleted", flush=True)
    return 0 if all(ok for _n, ok, _d in RESULTS) else 3


if __name__ == "__main__":
    sys.exit(main())
