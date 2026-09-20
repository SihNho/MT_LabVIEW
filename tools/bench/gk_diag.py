"""gk_diag.py - why is GPU_kernel_v1_partial.vi broken before any output wiring?  Hypothesis: the Boolean array control
'Bead is good? array in' makes a BAD wire into the CLFN's U8-array parameter good_in (the wire is created, then Remove Bad
Wires deletes it, leaving a required argument unwired).

Reports, on a scratch copy of the checkpoint:
  1. ExecState, wire count
  2. which CLFN terminals are still UNWIRED (create_control on each: a terminal that accepts a new wired control was unwired;
     the probe control is deleted again)
  3. a direct retest of the bool wire: wire it, ExecState + wire count immediately, then after remove_bad_wires
  py tools/bgrun.py --max-min 12 --log tools/bench/gk_diag.log -- py -u tools/bench/gk_diag.py
"""
import os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
CKPT = os.path.join(g.CLAUDEDEV, "GPU_kernel_v1_partial.vi")
if not os.path.exists(CKPT):
    print("no checkpoint:", CKPT, flush=True); sys.exit(2)
T = os.path.join(g.CLAUDEDEV, "SCRATCH_gkdiag.vi")
if os.path.exists(T):
    os.remove(T)
shutil.copyfile(CKPT, T); g.report(T, "SubVI"); g.open_panel(T); time.sleep(0.8)
inv0 = g.uids(T, "Invoke")


def purge():
    for o in g.new_since(T, "Invoke", inv0):
        ids = [x["uid"] for x in g.report(T, "Invoke")]
        if o["uid"] in ids:
            g.delete_object(T, "Invoke", ids.index(o["uid"]))


def del_terms(new):
    ct = [o["uid"] for o in g.report(T, "ControlTerminal")]
    for o in new:
        if o["uid"] in ct:
            g.delete_object(T, "ControlTerminal", ct.index(o["uid"])); ct = [x["uid"] for x in g.report(T, "ControlTerminal")]
    g.remove_bad_wires_scripted(T)


print("checkpoint: ExecState", g.exec_state(T), "nodes", g.count(T, "Node"), "wires", g.count(T, "Wire"),
      "fp", len(g.fp_labels(T)), flush=True)
uids = [o["uid"] for o in g.report(T, "Node")]; kuid = g.report(T, "CallLibrary")[0]["uid"]; n = uids.index(kuid)
print("CLFN Nodes[] index", n, flush=True)
unwired = []
for t in range(0, 40):
    w0 = g.count(T, "Wire"); new, lab = g.create_control(T, n, t); purge()
    if new and g.count(T, "Wire") > w0:
        unwired.append((t, lab)); del_terms(new)
    elif new:
        del_terms(new)
print("UNWIRED CLFN terminals:", unwired, flush=True)
# direct retest of the boolean wire
w0 = g.count(T, "Wire"); es0 = g.exec_state(T)
try:
    r = g.wire_control(T, ["Bead is good? array in"], "CallLibrary", 0, ["good_in"])
    print(f"   bool -> good_in: {r} | wires {w0} -> {g.count(T, 'Wire')} | ExecState {es0} -> {g.exec_state(T)}", flush=True)
except Exception as e:
    print(f"   bool -> good_in: EXC {str(e)[:200]}", flush=True)
g.remove_bad_wires_scripted(T)
print(f"   after remove_bad_wires: wires {g.count(T, 'Wire')} ExecState {g.exec_state(T)}", flush=True)
try:
    g.close_panel(T); os.remove(T); print("scratch removed", flush=True)
except Exception as e:
    print("cleanup:", str(e)[:80], flush=True)
