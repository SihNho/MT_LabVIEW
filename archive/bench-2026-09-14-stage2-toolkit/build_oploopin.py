"""build_oploopin.py <for|while> - OpForLoopIn_v0 / OpWhileLoopIn_v0: create a For / While loop on ANY diagram of the
target (Traverse 'Diagram'[index 2]) with input tunnels taken from named OUTPUT terminals of an existing node
(Class Name / index / Names -> Get Outputs -> creator 'Inputs'), per-tunnel indexing flags, static parallel instances
(For). Stage 2 needs the P=4 kernel loop INSIDE the tracking While loop and a Case inside the acquisition loop; the
top-level-only creators (OpForLoop_v0 / OpWhileLoop_v0) cannot do that. Plan review:
archive/peer/2026-09-14-nested-structure-creators-plan.md.

Donor OpExitLoop_v0 (as the queue ops): Get Outputs 216 ('Names' of node A) -> its 'Outputs' array feeds the creator's
'Inputs'; TMSC 788 (Class Name 2 = 'Diagram', index 2) -> 'Diagram in'; new controls: 'location (0, 0)',
'Inputs Indexing?', and for For loops 'Number of Static Parallel Instances'; error chain by name (these creators have
one error pair). The unwired 'Loop Count Terminal' (For) stays unwired: the kernel loop is auto-indexed.
  py tools/bgrun.py --max-min 12 --log tools/bench/build_oploopin.log -- py -u tools/recipes/build_oploopin.py for
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

KIND = (sys.argv[1] if len(sys.argv) > 1 else "for").lower()
CREATOR, OPNAME = {"for": ("Create For Loop.vi", "OpForLoopIn_v0.vi"), "while": ("Create While Loop.vi", "OpWhileLoopIn_v0.vi")}[KIND]
SRC = os.path.join(g.CLAUDEDEV, "OpExitLoop_v0.vi")
OP = os.path.join(g.CLAUDEDEV, OPNAME)
LIB = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting"
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", f"oploopin_{KIND}_labels.json")
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
    pw = {r["label"]: r["wire"] for r in g.panel_wiring(OP)}
    go = [u for u, (n, l, r) in nd.items() if l == "Get Outputs.vi"]
    u216 = next(u for u in go if any(r["name"] == "Names" and r["wire"] == pw["Names"] for r in nd[u][2]))
    rows_exit = nd[u_exit][2]
    w_diag = next(r["wire"] for r in rows_exit if r["name"] == "Diagram in" and not r["is_source"])
    w_err_in = next(r["wire"] for r in rows_exit if r["name"] == "error in (no error)")
    w_err_out = next(r["wire"] for r in rows_exit if r["name"] == "error out" and r["is_source"])
    src = lambda w: next(((u, r["name"]) for u, (n, l, rr) in nd.items() for r in rr if r["is_source"] and w and r["wire"] == w and u != u_exit), None)
    s_diag, s_err = src(w_diag), src(w_err_in)
    sinks_err = [(u, r["name"]) for u, (n, l, rr) in nd.items() for r in rr if not r["is_source"] and r["wire"] == w_err_out and u != u_exit]
    err_ind = [r["label"] for r in g.panel_wiring(OP) if r["wire"] == w_err_out]

    def cls_of(uid):
        lab = nd[uid][1] or ""
        return "SubVI" if lab.endswith(".vi") else ("Property" if lab == "Property Node" else "Function")
    step("2 delete Exit For Loop + RBW", "SubVI -1", lambda: (g.delete_object(OP, "SubVI", idx("SubVI", u_exit)), g.remove_bad_wires_scripted(OP), snap("after"))[2])
    before = g.uids(OP, "SubVI")
    step(f"3 drop {CREATOR}", "SubVI +1", lambda: (g.drop_subvi(OP, os.path.join(LIB, CREATOR), 0, (1500, 700)), snap("after"))[1])
    u_c = [u for u in g.uids(OP, "SubVI") if u not in before][0]; purge()
    step("4a Diagram in <- TMSC (Class Name 2 / index 2)", "Wire +1", lambda: (g.wire(OP, cls_of(s_diag[0]), idx(cls_of(s_diag[0]), s_diag[0]), s_diag[1], "SubVI", idx("SubVI", u_c), "Diagram in"), snap("after"))[1])
    step("4b error in", "Wire +1", lambda: (g.wire(OP, cls_of(s_err[0]), idx(cls_of(s_err[0]), s_err[0]), s_err[1], "SubVI", idx("SubVI", u_c), "error in (no error)", branch=True), snap("after"))[1])
    for su, sname in sinks_err:
        step(f"4c error out -> {nd[su][1]}.'{sname}'", "Wire +1", lambda su=su, sname=sname: (g.wire(OP, "SubVI", idx("SubVI", u_c), "error out", cls_of(su), idx(cls_of(su), su), sname), snap("after"))[1])
    step("4d Get Outputs.'Outputs' -> creator 'Inputs'", "Wire +1", lambda: (g.wire(OP, "SubVI", idx("SubVI", u216), "Outputs", "SubVI", idx("SubVI", u_c), "Inputs"), snap("after"))[1])
    purge()
    c0 = {l for _i, l, ind in g.fp_labels(OP) if not ind}
    ndc = nodes(); n_c = ndc[u_c][0]
    want = ["location (0, 0)", "Inputs Indexing?"] + (["Number of Static Parallel Instances"] if KIND == "for" else [])
    labels = {}
    for tname in want:
        t = next(r["i"] for r in ndc[u_c][2] if r["name"] == tname)
        before_c = {l for _i, l, ind in g.fp_labels(OP) if not ind}
        step(f"5 create_control on '{tname}'", "one new control", lambda t=t: g.create_control(OP, n_c, t))
        purge()
        new = [l for _i, l, ind in g.fp_labels(OP) if not ind and l not in before_c]
        labels[tname] = new[0] if len(new) == 1 else None
    print(f"   controls: {labels}", flush=True)
    if err_ind and g.exec_state(OP) == 1:
        step("6 error out -> 'error out' indicator", "branch", lambda: g.wire_indicators(OP, idx("SubVI", u_c), ["error out"], err_ind, node_class="SubVI"))
        purge()
    es = g.exec_state(OP)
    print(f"   creator terminals: {[(r['name'], r['wire']) for r in nodes()[u_c][2] if r['name']]}", flush=True)
    if es != 1 or any(v is None for v in labels.values()) or any(k == "exc" for _, k in STEPS):
        print(f"\nVERDICT: BROKEN (ExecState {es}, controls {labels}, steps {STEPS}) - NOT SAVING.", flush=True)
        try:
            g.close_panel(OP)
        except Exception:
            pass
        return 4
    g.set_auto_error_handling(OP, False); g.save(OP)
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=2)
    try:
        g.close_panel(OP)
    except Exception:
        pass
    print(f"donor md5 unchanged: {hashlib.md5(open(SRC, 'rb').read()).hexdigest() == md5}", flush=True)
    print(f"\nVERDICT: {OPNAME} BUILT and SAVED (structural)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
