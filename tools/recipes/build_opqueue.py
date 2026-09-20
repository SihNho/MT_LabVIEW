"""build_opqueue.py <obtain|enqueue|dequeue|release> - OpQueueObtain_v0 / OpQueueEnqueue_v0 / OpQueueDequeue_v0 /
OpQueueRelease_v0: place one erdosmiller queue node on a diagram of the target, its refnum inputs taken from OUTPUT
TERMINALS of existing nodes chosen by name (stage-2 toolkit gap 3, docs/stage2-plan.md; connectors in
tools/bench/probe_queue_vis.log).

Donor OpExitLoop_v0: Open VI Reference -> Traverse(Class Name, index) -> IA -> TMSC 683 -> Get Outputs 216 (Names)
'Outputs' [terminal refs of node A]; Traverse(Class Name 2, index 2) -> IA -> TMSC 788 -> (Diagram) ; Get Outputs 348
(Names 2, Node in <- 216.'Node out') 'Outputs' [more terminal refs of node A]. Exit For Loop consumed them.
Here: delete Exit For Loop; drop the creator; 'Diagram in' <- TMSC 788 (Class Name 2 = 'Diagram', index 2 = target
diagram); the refnum inputs <- Index Array[0] of Get Outputs 216 (first named output of node A) and, for enqueue,
Index Array[0] of Get Outputs 348 (the element terminal: its Node in is 216's node too - so element and queue must come
from the SAME node A; the wrapper passes Names=[queue name], Names 2=[element name]); 'location (0, 0)' <- new control.
  obtain : 'element data type' <- IA(216)[0]
  enqueue: 'queue' <- IA(216)[0], 'element' <- IA(348)[0]
  dequeue: 'queue' <- IA(216)[0]          (timeout left at the primitive's default; a control is created on the
                                            TARGET's node afterwards by the wrapper if wanted)
  release: 'queue' <- IA(216)[0]
  py tools/bgrun.py --max-min 25 --log tools/bench/build_opqueue.log -- py -u tools/recipes/build_opqueue.py obtain
"""
import hashlib
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

KIND = sys.argv[1].lower() if len(sys.argv) > 1 else "obtain"
SPEC = {"obtain": ("Create Obtain Queue.vi", "OpQueueObtain_v0.vi", {"element data type": 216}),
        "enqueue": ("Create Enqueue Element.vi", "OpQueueEnqueue_v0.vi", {"queue": 216, "element": 348}),
        "dequeue": ("Create Dequeue Element.vi", "OpQueueDequeue_v0.vi", {"queue": 216}),
        "release": ("Create Release Queue.vi", "OpQueueRelease_v0.vi", {"queue": 216})}[KIND]
CREATOR, OPNAME, INPUTS = SPEC
SRC = os.path.join(g.CLAUDEDEV, "OpExitLoop_v0.vi")
OP = os.path.join(g.CLAUDEDEV, OPNAME)
LIB = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting"
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", f"opqueue_{KIND}_labels.json")
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
    return f"{tag} SubVI={len(g.report_all(OP, 'SubVI'))} IndexArray={len(g.report_all(OP, 'IndexArray'))} Wire={len(g.report_all(OP, 'Wire'))} ExecState={g.exec_state(OP)}"


def nodes():
    labels = {r["uid"]: r["label"] for r in g.node_labels(OP, 0)}
    out = {}
    for cand in range(60):
        nu, rows = g.node_terms_uid(OP, 0, cand)
        if not nu:
            break
        out[nu] = (cand, labels.get(nu), rows)
    return out


def idx(cls, uid):
    return [o["uid"] for o in g.report_all(OP, cls)].index(uid)


def main():
    g._lv = None
    if os.path.exists(OP):
        os.remove(OP)
    md5 = hashlib.md5(open(SRC, "rb").read()).hexdigest()
    shutil.copyfile(SRC, OP); time.sleep(0.3); g.report_all(OP, "SubVI"); g.open_panel(OP); time.sleep(0.8)
    inv0 = g.uids(OP, "Invoke")

    def purge():
        junk = [u for u in g.uids(OP, "Invoke") if u not in inv0]
        if junk:
            order = [o["uid"] for o in g.report_all(OP, "Invoke")]
            for i in sorted((order.index(u) for u in junk if u in order), reverse=True):
                g.delete_object(OP, "Invoke", i, verify=False)
            g.remove_bad_wires_scripted(OP)

    print(snap("start:"), flush=True)
    nd = nodes()
    u_exit = next(u for u, (n, l, r) in nd.items() if l == "Exit For Loop.vi")
    go = [u for u, (n, l, r) in nd.items() if l == "Get Outputs.vi"]
    # identify the two Get Outputs by their 'Names' wire: 216 <- control 'Names', 348 <- 'Names 2' (panel wiring)
    pw = {r["label"]: r["wire"] for r in g.panel_wiring(OP)}
    u216 = next(u for u in go if any(r["name"] == "Names" and r["wire"] == pw["Names"] for r in nd[u][2]))
    u348 = next(u for u in go if u != u216)
    rows_exit = nd[u_exit][2]
    w_diag = next(r["wire"] for r in rows_exit if r["name"] == "Diagram in" and not r["is_source"])
    w_err_in = next(r["wire"] for r in rows_exit if r["name"] == "error in (no error)")
    w_err_out = next(r["wire"] for r in rows_exit if r["name"] == "error out")
    src = lambda w: next(((u, r["name"]) for u, (n, l, rr) in nd.items() for r in rr if r["is_source"] and w and r["wire"] == w and u != u_exit), None)
    s_diag, s_err = src(w_diag), src(w_err_in)
    sinks_err = [(u, r["name"]) for u, (n, l, rr) in nd.items() for r in rr if not r["is_source"] and r["wire"] == w_err_out and u != u_exit]
    err_ind = [r["label"] for r in g.panel_wiring(OP) if r["wire"] == w_err_out]
    print(f"   Get Outputs 216={u216} 348={u348}; Diagram in <- {s_diag}; error in <- {s_err}; error out -> {sinks_err} + {err_ind}", flush=True)

    def cls_of(uid):
        lab = nd[uid][1] or ""
        return "SubVI" if lab.endswith(".vi") else ("Property" if lab == "Property Node" else "Function")
    step("2 delete Exit For Loop + RBW", "SubVI -1", lambda: (g.delete_object(OP, "SubVI", idx("SubVI", u_exit)), g.remove_bad_wires_scripted(OP), snap("after"))[2])
    before = g.uids(OP, "SubVI")
    step(f"3 drop {CREATOR}", "SubVI +1", lambda: (g.drop_subvi(OP, os.path.join(LIB, CREATOR), 0, (1500, 700)), snap("after"))[1])
    u_c = [u for u in g.uids(OP, "SubVI") if u not in before][0]; purge()
    step("4a Diagram in", "Wire +1", lambda: (g.wire(OP, cls_of(s_diag[0]), idx(cls_of(s_diag[0]), s_diag[0]), s_diag[1], "SubVI", idx("SubVI", u_c), "Diagram in"), snap("after"))[1])
    step("4b error in", "Wire +1", lambda: (g.wire(OP, cls_of(s_err[0]), idx(cls_of(s_err[0]), s_err[0]), s_err[1], "SubVI", idx("SubVI", u_c), "error in (no error)", branch=True), snap("after"))[1])
    # run 1: the creator has TWO 'error out' terminals - 10 = refnum of the CREATED node's error terminal, 15 = its own
    # error chain; wiring by name hit 10 and fed a refnum into Clear Errors. Wire 15 by terminal INDEX (top-level Nodes[]).
    ndc = nodes(); n_c0 = ndc[u_c][0]
    t15 = max(r["i"] for r in ndc[u_c][2] if r["name"] == "error out" and r["is_source"])
    for su, sname in sinks_err:
        n_s = ndc[su][0]; t_s = next(r["i"] for r in ndc[su][2] if r["name"] == sname and not r["is_source"])
        step(f"4c creator terminal {t15} (own error out) -> {nd[su][1]}.'{sname}' (by index)", "(1, x)", lambda n_s=n_s, t_s=t_s: g.connect_terminals(OP, n_s, t_s, n_c0, t15))
    purge()
    # refnum inputs through Index Array[0] of the chosen Get Outputs
    ias = {}
    for inp, which in INPUTS.items():
        u_go = u216 if which == 216 else u348
        ia = step(f"5 Index Array for '{inp}'", "IndexArray +1", lambda: g.build_index_array(OP, (1200, 900 + 150 * len(ias)))[-1]["uid"])
        purge(); ias[inp] = ia
        nd2 = nodes(); n_ia = nd2[ia][0]; t_arr = next(r["i"] for r in nd2[ia][2] if r["name"] == "array")
        n_go = nd2[u_go][0]; t_out = next(r["i"] for r in nd2[u_go][2] if r["name"] == "Outputs" and r["is_source"])
        step(f"5-wire Get Outputs.'Outputs' -> IA.array", "(1, x)", lambda: g.connect_terminals(OP, n_ia, t_arr, n_go, t_out))
        purge()
        step(f"5-wire IA.element -> '{inp}'", "Wire +1", lambda: (g.wire(OP, "IndexArray", idx("IndexArray", ia), "element", "SubVI", idx("SubVI", u_c), inp), snap("after"))[1])
        purge()
    c0 = {l for _i, l, ind in g.fp_labels(OP) if not ind}
    nd3 = nodes(); n_c = nd3[u_c][0]; t_loc = next(r["i"] for r in nd3[u_c][2] if r["name"] == "location (0, 0)")
    step("6 create_control on 'location (0, 0)'", "a cluster control", lambda: g.create_control(OP, n_c, t_loc))
    purge()
    loc = [l for _i, l, ind in g.fp_labels(OP) if not ind and l not in c0]
    print(f"   location control: {loc}", flush=True)
    if err_ind and g.exec_state(OP) == 1:
        nd7 = nodes(); n_c7 = nd7[u_c][0]; t15b = max(r["i"] for r in nd7[u_c][2] if r["name"] == "error out" and r["is_source"])
        pi = [i for i, l, ind in g.fp_labels(OP) if l == err_ind[0]]
        step("7 creator own 'error out' -> 'error out' indicator (connect_ctl, branch)", "no error text",
             lambda: g.connect_ctl(OP, pi[0], n_c7, t15b))
        purge()
    es = g.exec_state(OP)
    print(f"   creator terminals: {[(r['name'], r['wire']) for r in nodes()[u_c][2] if r['name']]}", flush=True)
    if es != 1 or len(loc) != 1 or any(k == "exc" for _, k in STEPS):
        print(f"\nVERDICT: BROKEN (ExecState {es}, steps {STEPS}) - NOT SAVING.", flush=True)
        try:
            g.close_panel(OP)
        except Exception:
            pass
        return 4
    g.set_auto_error_handling(OP, False); g.save(OP)
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump({"location": loc[0], "inputs": INPUTS}, f, indent=2)
    try:
        g.close_panel(OP)
    except Exception:
        pass
    print(f"donor md5 unchanged: {hashlib.md5(open(SRC, 'rb').read()).hexdigest() == md5}", flush=True)
    print(f"\nVERDICT: {OPNAME} BUILT and SAVED (structural)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
