"""build_opexitwhile.py - OpExitWhile_v0.vi: OpExitLoop_v0 with erdosmiller 'Exit While Loop.vi' in place of
'Exit For Loop.vi' AND its 'Stop Condition' fed from a front-panel control chosen BY NAME: VI.Block Diagram ->
Get Controls(Control Names) -> Index Array[0] -> Stop Condition. Stage-2 toolkit (docs/stage2-plan.md): a scripted While
loop is only runnable once its conditional terminal is wired, and the loop node's Terminals[] is empty
(test_opwhileloop.log), so the library's Stop Condition is the route.

Donor OpExitLoop_v0 (probe_opexitloop.log): Open VI Reference(43) -> Traverse(Class Name,index)->IA->TMSC(683)->
Get Outputs 216 (Names) -> Exit For Loop 292 [Diagram in <- TMSC 788 (Class Name 2 / index 2 = the loop body),
Outputs <- 216, Shift Registers <- Get Outputs 348 (Names 2), error in <- 348.error out, error out -> Clear Errors 370
-> 'error out' indicator].
STEPS: 1 copy, preload, open; 2 delete Exit For Loop (+RBW); 3 drop Exit While Loop.vi; wire Diagram in / Outputs /
Shift Registers / error in / error out by name; 4 PN VI[Block Diagram] <- Open VI Reference.'vi reference' (branch);
5 drop Get Controls.vi, PN.'Diagram' -> 'Diagram in', create_control on 'Control Names'; 6 Index Array <- 'Control
Terminals', element -> 'Stop Condition' (fallback: the array itself); 7 ExecState 1 -> save; labels json.
  py tools/bgrun.py --max-min 12 --log tools/bench/build_opexitwhile.log -- py -u tools/recipes/build_opexitwhile.py
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

SRC = os.path.join(g.CLAUDEDEV, "OpExitLoop_v0.vi")
OP = os.path.join(g.CLAUDEDEV, "OpExitWhile_v0.vi")
LIB = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting"
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "opexitwhile_labels.json")
P_BLOCKDIAGRAM = "23C"
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
        out[nu] = (cand, labels.get(nu), {r["name"]: r for r in rows}, rows)
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
    by = lambda lab: [u for u, (n, l, t, r) in nd.items() if l == lab]
    u_exit = by("Exit For Loop.vi")[0]; u_open = by("Open VI Reference")[0]
    # run 1 (20:5x): 'Outputs' and 'Shift Registers' each name TWO terminals (input + output); a name-keyed dict kept
    # the output (wire 0) and the source search matched Traverse '# of Refs'. Key by (name, direction) instead.
    rows_exit = nd[u_exit][3]
    tin = {r["name"]: r for r in rows_exit if not r["is_source"]}
    tout = {r["name"]: r for r in rows_exit if r["is_source"]}
    srcs = {}
    for name in ("Diagram in", "Outputs", "Shift Registers", "error in (no error)"):
        w = tin[name]["wire"]
        srcs[name] = next(((u, nm) for u, (n, l, tt, r) in nd.items() for rr in r if rr["is_source"] and rr["wire"] == w and w and u != u_exit for nm in [rr["name"]]), None)
    w_err_out = tout["error out"]["wire"]
    sinks_err = [(u, nm) for u, (n, l, tt, r) in nd.items() for nm, rr in tt.items() if not rr["is_source"] and rr["wire"] == w_err_out and u != u_exit]
    err_ind = [r["label"] for r in g.panel_wiring(OP) if r["wire"] == w_err_out]
    print(f"   Exit For Loop {u_exit}: sources {srcs}; error out -> nodes {sinks_err}, indicators {err_ind}", flush=True)
    step("2 delete Exit For Loop + RBW", "SubVI -1", lambda: (g.delete_object(OP, "SubVI", idx("SubVI", u_exit)), g.remove_bad_wires_scripted(OP), snap("after"))[2])
    before = g.uids(OP, "SubVI")
    step("3 drop Exit While Loop.vi", "SubVI +1", lambda: (g.drop_subvi(OP, os.path.join(LIB, "Exit While Loop.vi"), 0, (1500, 700)), snap("after"))[1])
    u_w = [u for u in g.uids(OP, "SubVI") if u not in before][0]; purge()

    def cls_of(uid):
        lab = nd[uid][1] or ""
        return "SubVI" if lab.endswith(".vi") else ("Property" if lab == "Property Node" else "Function")
    for name in ("Diagram in", "Outputs", "Shift Registers", "error in (no error)"):
        su, sname = srcs[name]
        step(f"3-wire {sname} -> While.'{name}'", "Wire +1", lambda su=su, sname=sname, name=name: (g.wire(OP, cls_of(su), idx(cls_of(su), su), sname, "SubVI", idx("SubVI", u_w), name), snap("after"))[1])
    for su, sname in sinks_err:
        step(f"3-wire While.'error out' -> {nd[su][1]}.'{sname}'", "Wire +1", lambda su=su, sname=sname: (g.wire(OP, "SubVI", idx("SubVI", u_w), "error out", cls_of(su), idx(cls_of(su), su), sname), snap("after"))[1])
    purge()
    print("   " + snap("after swap:"), flush=True)
    pn = step("4 PN VI[Block Diagram]", "Property +1", lambda: g.build_property(OP, "VI Server:VI", [(P_BLOCKDIAGRAM, False)], (300, 900))[-1]["uid"])
    step("4-wire Open VI Reference.'vi reference' -> PN.reference (branch)", "ok", lambda: (g.wire(OP, "Function", idx("Function", u_open), "vi reference", "Property", idx("Property", pn), "reference", branch=True), snap("after"))[1])
    purge()
    before = g.uids(OP, "SubVI")
    step("5a drop Get Controls.vi", "SubVI +1", lambda: (g.drop_subvi(OP, os.path.join(LIB, "Get Controls.vi"), 0, (600, 900)), snap("after"))[1])
    u_gc = [u for u in g.uids(OP, "SubVI") if u not in before][0]; purge()
    step("5b PN.'Diagram' -> Get Controls.'Diagram in'", "Wire +1", lambda: (g.wire(OP, "Property", idx("Property", pn), "Diagram", "SubVI", idx("SubVI", u_gc), "Diagram in"), snap("after"))[1])
    nd2 = nodes(); n_gc, _l, t_gc, _r = nd2[u_gc]
    c0 = {l for _i, l, ind in g.fp_labels(OP) if not ind}
    step("5c create_control on Get Controls.'Control Names'", "a string-array control", lambda: g.create_control(OP, n_gc, t_gc["Control Names"]["i"]))
    purge()
    names_ctl = [l for _i, l, ind in g.fp_labels(OP) if not ind and l not in c0]
    print(f"   Control Names control: {names_ctl}", flush=True)
    ia = step("6a build_index_array", "IndexArray +1", lambda: g.build_index_array(OP, (900, 900))[-1]["uid"])
    purge()
    nd3 = nodes(); n_ia, _l, t_ia, _r = nd3[ia]; n_gc, _l, t_gc, _r = nd3[u_gc]
    step("6b connect Get Controls.'Control Terminals' -> IA.array", "(1, x)", lambda: g.connect_terminals(OP, n_ia, t_ia["array"]["i"], n_gc, t_gc["Control Terminals"]["i"]))
    purge()
    step("6c IA.element -> While.'Stop Condition'", "Wire +1, ExecState 1", lambda: (g.wire(OP, "IndexArray", idx("IndexArray", ia), "element", "SubVI", idx("SubVI", u_w), "Stop Condition"), snap("after"))[1])
    purge()
    if g.exec_state(OP) != 1:
        print("   element route broken - fallback: delete that wire and feed the whole 'Control Terminals' array", flush=True)
        nd4 = nodes(); w = nd4[u_w][2]["Stop Condition"]["wire"]
        if w:
            g.delete_object(OP, "Wire", [o["uid"] for o in g.report_all(OP, "Wire")].index(w), verify=False)
        step("6d Get Controls.'Control Terminals' -> While.'Stop Condition' (array)", "ExecState 1",
             lambda: (g.wire(OP, "SubVI", idx("SubVI", u_gc), "Control Terminals", "SubVI", idx("SubVI", u_w), "Stop Condition", branch=True), snap("after"))[1])
        purge()
    if err_ind and g.exec_state(OP) == 1:
        step("7 While.'error out' -> 'error out' indicator (last: wire_indicators needs ExecState 1)", "branch",
             lambda: g.wire_indicators(OP, idx("SubVI", u_w), ["error out"], err_ind, node_class="SubVI"))
        purge()
    es = g.exec_state(OP)
    nd5 = nodes()
    print(f"   Exit While Loop terminals: {[(r['name'], r['wire']) for r in nd5[u_w][3]]}", flush=True)
    if es != 1 or len(names_ctl) != 1:
        print(f"\nVERDICT: BROKEN (ExecState {es}, steps {STEPS}) - NOT SAVING.", flush=True)
        try:
            g.close_panel(OP)
        except Exception:
            pass
        return 4
    g.set_auto_error_handling(OP, False); g.save(OP)
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump({"stop_names": names_ctl[0]}, f, indent=2)
    try:
        g.close_panel(OP)
    except Exception:
        pass
    print(f"donor md5 unchanged: {hashlib.md5(open(SRC, 'rb').read()).hexdigest() == md5}", flush=True)
    print("\nVERDICT: OpExitWhile_v0 BUILT and SAVED (structural) - test next", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
