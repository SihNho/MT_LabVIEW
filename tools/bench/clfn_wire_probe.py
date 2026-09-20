"""clfn_wire_probe.py - codex test #1 (archive/peer/2026-09-09-clfn-scripted-node-broken-with-arguments.md): a scripted CLFN with
return + one I32 argument is broken; does wiring a typed control to the argument's INPUT terminal heal it (terminal datatype never
committed)?  Scratch VI, build_clfn(ret + width I32), then create_control on terminals 4.. and print ExecState after each."""
import os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "gpu"))
import gscript as g
import clfn_params as cp
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
T = os.path.join(g.CLAUDEDEV, "SCRATCH_wire.vi")
if os.path.exists(T):
    os.remove(T)
shutil.copyfile(os.path.join(g.CLAUDEDEV, "FPTARGET_v0.vi"), T); g.report(T, "SubVI"); g.open_panel(T); time.sleep(0.8)
while g.count(T, "Node"):
    try:
        g.delete_object(T, "Node", 0)
    except RuntimeError as e:
        if "expected 1 object gone" not in str(e):
            raise
        break
g.remove_bad_wires_scripted(T)
while g.count(T, "ControlTerminal"):
    g.delete_object(T, "ControlTerminal", 0)
g.remove_bad_wires_scripted(T); inv0 = g.uids(T, "Invoke")


def purge():
    for o in g.new_since(T, "Invoke", inv0):
        ids = [x["uid"] for x in g.report(T, "Invoke")]
        if o["uid"] in ids:
            g.delete_object(T, "Invoke", ids.index(o["uid"]))


uid, nterms, errs = g.build_clfn(T, (400, 300), os.path.join(g.CLAUDEDEV, "Debug", "mt_track.dll"), "mt2_track_simple",
                                 cp.compose([cp.PARAMS[0], ("width", "num", "I32", "value", 0)]).hex())
purge(); g.remove_bad_wires_scripted(T); n = g.count(T, "Node") - 1
print("node built: terms", nterms, "ExecState", g.exec_state(T), "Nodes[]", g.count(T, "Node"), flush=True)
for t in range(0, 10):
    w0 = g.count(T, "Wire"); new, lab = g.create_control(T, n, t); purge()
    if new and g.count(T, "Wire") > w0:
        print(f"  t{t}: control {lab!r} wired -> ExecState {g.exec_state(T)}", flush=True)
    else:
        if new:
            ct = [o["uid"] for o in g.report(T, "ControlTerminal")]
            for o in new:
                if o["uid"] in ct:
                    g.delete_object(T, "ControlTerminal", ct.index(o["uid"])); ct = [x["uid"] for x in g.report(T, "ControlTerminal")]
            g.remove_bad_wires_scripted(T)
        fp0 = {l for _, l, _ in g.fp_labels(T)}; w0 = g.count(T, "Wire"); new = g.create_indicator(T, n, t); purge()
        labs = [l for _, l, _ in g.fp_labels(T) if l not in fp0]
        if new and g.count(T, "Wire") > w0:
            print(f"  t{t}: indicator {labs[-1] if labs else '?'} wired -> ExecState {g.exec_state(T)}", flush=True)
        else:
            print(f"  t{t}: nothing", flush=True)
print("final ExecState", g.exec_state(T), "wires", g.count(T, "Wire"), flush=True)
g.close_panel(T); os.remove(T); print("scratch removed", flush=True)
