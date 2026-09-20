"""build_opwhileloop.py - OpWhileLoop_v0.vi: OpForLoop_v0 with erdosmiller 'Create While Loop.vi' in place of
'Create For Loop.vi', and - unlike the For op, whose Get Controls 'Control Terminals' output was never wired into the
creator's 'Inputs' (probe_opforloop.log: both wire 0; that is why 'Control Names' never produced tunnels) - with
Get Controls.'Control Terminals' -> Create While Loop.'Inputs' wired, so tunnels by control name work.
Stage-2 toolkit gap 1 (docs/stage2-plan.md). No hardware.

Donor OpForLoop_v0 (probe): Open VI Reference -> PN VI[Block Diagram] -> Create Constant x3 chain (Diagram in/out
threaded) -> Create For Loop (Diagram in <- Create Constant 629.'Diagram out' wire 1031; 'Inputs Indexing?' <- control
1981; 'location' <- control 2357; 'Loop Count Terminal' <- Select 1446; error in 1098; error out 1217 -> Close
Reference) ; Get Controls (Diagram in 1126, Control Names <- control 1155).
STEPS: 1 copy -> OpWhileLoop_v0, open; 2 delete Create For Loop (+RBW); 3 drop Create While Loop.vi; 4 wire by name:
  Create Constant[last].'Diagram out' -> 'Diagram in'; controls 'Inputs Indexing?' / 'location (0, 0)' -> same names;
  Get Controls.'Control Terminals' -> 'Inputs'; error chain: source of the deleted node's error in -> 'error in
  (no error)'; 'error out' -> Close Reference.'error in (no error)'; 5 ExecState 1 -> save.
  py tools/bgrun.py --max-min 10 --log tools/bench/build_opwhileloop.log -- py -u tools/recipes/build_opwhileloop.py
"""
import hashlib
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = g.OP_FORLOOP
OP = os.path.join(g.CLAUDEDEV, "OpWhileLoop_v0.vi")
CWL = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting\Create While Loop.vi"
g._run.__defaults__ = (6.0, 120.0)
STEPS = []


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    t0 = time.time()
    try:
        r = fn()
        print(f"   result : {r}  ({time.time() - t0:.1f} s)", flush=True)
        STEPS.append((name, "ok"))
        return r
    except Exception as e:
        print(f"   OBSERVED: EXC {str(e)[:300]}", flush=True)
        STEPS.append((name, "exc"))
        return None


def snap(tag=""):
    return f"{tag} SubVI={len(g.report_all(OP, 'SubVI'))} Wire={len(g.report_all(OP, 'Wire'))} ExecState={g.exec_state(OP)}"


def nodes():
    labels = {r["uid"]: r["label"] for r in g.node_labels(OP, 0)}
    out = {}
    for cand in range(40):
        nu, rows = g.node_terms_uid(OP, 0, cand)
        if not nu:
            break
        out[nu] = (cand, labels.get(nu), {r["name"]: r for r in rows}, rows)
    return out


def si(uid):
    return [o["uid"] for o in g.report_all(OP, "SubVI")].index(uid)


def main():
    g._lv = None
    if os.path.exists(OP):
        os.remove(OP)
    md5 = hashlib.md5(open(SRC, "rb").read()).hexdigest()
    shutil.copyfile(SRC, OP); time.sleep(0.3); g.report_all(OP, "SubVI"); g.open_panel(OP); time.sleep(0.8)
    inv0 = g.uids(OP, "Invoke")
    print(snap("start:"), flush=True)
    nd = nodes()
    u_for = next(u for u, (n, l, t, r) in nd.items() if l == "Create For Loop.vi")
    u_gc = next(u for u, (n, l, t, r) in nd.items() if l == "Get Controls.vi")
    u_close = next(u for u, (n, l, t, r) in nd.items() if l == "Close Reference")
    t_for = nd[u_for][2]
    w_diag, w_err_in = t_for["Diagram in"]["wire"], t_for["error in (no error)"]["wire"]
    # who feeds Diagram in / error in of the For node
    src_diag = next((u, name) for u, (n, l, t, r) in nd.items() for name, rr in t.items() if rr["is_source"] and rr["wire"] == w_diag and u != u_for)
    src_err = next((u, name) for u, (n, l, t, r) in nd.items() for name, rr in t.items() if rr["is_source"] and rr["wire"] == w_err_in and u != u_for)
    print(f"   For node {u_for}: Diagram in <- {src_diag} (wire {w_diag}); error in <- {src_err} (wire {w_err_in}); Get Controls {u_gc}; Close Reference {u_close}", flush=True)
    step("2 delete Create For Loop + RBW", "SubVI -1", lambda: (g.delete_object(OP, "SubVI", si(u_for)), g.remove_bad_wires_scripted(OP), snap("after"))[2])
    before = g.uids(OP, "SubVI")
    step("3 drop Create While Loop.vi", "SubVI +1", lambda: (g.drop_subvi(OP, CWL, 0, (900, 300)), snap("after"))[1])
    u_w = [u for u in g.uids(OP, "SubVI") if u not in before][0]
    junk = [u for u in g.uids(OP, "Invoke") if u not in inv0]
    if junk:
        order = [o["uid"] for o in g.report_all(OP, "Invoke")]
        for i in sorted((order.index(u) for u in junk if u in order), reverse=True):
            g.delete_object(OP, "Invoke", i, verify=False)
        g.remove_bad_wires_scripted(OP)
    src_cls = "SubVI" if nd[src_diag[0]][1].endswith(".vi") else "Function"
    step("4a Diagram out -> While.'Diagram in'", "Wire +1", lambda: (g.wire(OP, src_cls, [o["uid"] for o in g.report_all(OP, src_cls)].index(src_diag[0]), src_diag[1], "SubVI", si(u_w), "Diagram in"), snap("after"))[1])
    err_cls = "SubVI" if (nd[src_err[0]][1] or "").endswith(".vi") else ("Property" if nd[src_err[0]][1] == "Property Node" else "Function")
    step("4b error chain in", "Wire +1", lambda: (g.wire(OP, err_cls, [o["uid"] for o in g.report_all(OP, err_cls)].index(src_err[0]), src_err[1], "SubVI", si(u_w), "error in (no error)", branch=True), snap("after"))[1])
    step("4c While.'error out' -> Close Reference.'error in (no error)'", "Wire +1", lambda: (g.wire(OP, "SubVI", si(u_w), "error out", "Function", [o["uid"] for o in g.report_all(OP, "Function")].index(u_close), "error in (no error)"), snap("after"))[1])
    step("4d controls -> 'Inputs Indexing?', 'location (0, 0)'", "ExecState toward 1", lambda: (g.wire_control(OP, ["Inputs Indexing?", "location (0, 0)"], "SubVI", si(u_w), ["Inputs Indexing?", "location (0, 0)"]), snap("after"))[1])
    step("4e Get Controls.'Control Terminals' -> While.'Inputs'", "Wire +1", lambda: (g.wire(OP, "SubVI", si(u_gc), "Control Terminals", "SubVI", si(u_w), "Inputs"), snap("after"))[1])
    junk = [u for u in g.uids(OP, "Invoke") if u not in inv0]
    if junk:
        order = [o["uid"] for o in g.report_all(OP, "Invoke")]
        for i in sorted((order.index(u) for u in junk if u in order), reverse=True):
            g.delete_object(OP, "Invoke", i, verify=False)
        g.remove_bad_wires_scripted(OP)
    nd2 = nodes()
    print(f"   While node terminals: {[(r['name'], r['wire']) for r in nd2[u_w][3]]}", flush=True)
    es = g.exec_state(OP)
    if es != 1 or any(k == "exc" for _, k in STEPS):
        print(f"\nVERDICT: BROKEN (ExecState {es}, steps {STEPS}) - NOT SAVING.", flush=True)
        try:
            g.close_panel(OP)
        except Exception:
            pass
        return 4
    g.save(OP)
    try:
        g.close_panel(OP)
    except Exception:
        pass
    print(f"donor md5 unchanged: {hashlib.md5(open(SRC, 'rb').read()).hexdigest() == md5}", flush=True)
    print("\nVERDICT: OpWhileLoop_v0 BUILT and SAVED (structural) - test next", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
