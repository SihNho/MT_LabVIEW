"""bool_wire_probe.py - isolated test of the one suspect wire in GPU_kernel_v1: the kernel's BOOLEAN array control
'Bead is good? array in' into the scripted CLFN's U8-array parameter `good_in`.

GPU_kernel_v1 came out broken (ExecState 0) before any output wiring, with 13 wires where 14 were expected - consistent with
"the wire is created, then Remove Bad Wires deletes it as a type mismatch, leaving a required argument unwired".  This probe
answers it directly on a stripped copy of the kernel with just the CLFN on the diagram (~3 min instead of a 12-min rebuild):

  DBL  array control 'x,y,z array'            -> CLFN.xyz_in    (control case: types match)
  BOOL array control 'Bead is good? array in' -> CLFN.good_in   (the suspect)
  I32  array control 'pos in cal image in'    -> CLFN.idx_out   (control case: types match)

For each: wire count and ExecState immediately after the wire, and again after remove_bad_wires.
  py tools/bgrun.py --max-min 12 --log tools/bench/bool_wire_probe.log -- py -u tools/bench/bool_wire_probe.py
"""
import os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "gpu"))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
SRC = os.path.join(g.CLAUDEDEV, "PARALLEL_kernel_v3.vi"); T = os.path.join(g.CLAUDEDEV, "SCRATCH_boolwire.vi")
DLL = os.path.join(g.CLAUDEDEV, "Debug", "mt_track.dll"); FN = "mt2_track_simple"
FLAT = open(os.path.join(HERE, "paraminfo_mt2.hex")).read().strip()
if os.path.exists(T):
    os.remove(T)
shutil.copyfile(SRC, T); g.report(T, "SubVI"); g.open_panel(T); time.sleep(0.8)
while g.count(T, "Node"):
    try:
        g.delete_object(T, "Node", 0)
    except RuntimeError as e:
        if "expected 1 object gone" not in str(e):
            raise
        break
g.remove_bad_wires_scripted(T)
inv0 = g.uids(T, "Invoke")


def purge():
    for o in g.new_since(T, "Invoke", inv0):
        ids = [x["uid"] for x in g.report(T, "Invoke")]
        if o["uid"] in ids:
            g.delete_object(T, "Invoke", ids.index(o["uid"]))


print("stripped: nodes", g.count(T, "Node"), "wires", g.count(T, "Wire"), "ExecState", g.exec_state(T), flush=True)
uid, nterms, errs = g.build_clfn(T, (900, 300), DLL, FN, FLAT); purge()
print("CLFN built: terms", nterms, "errs", errs, "wires", g.count(T, "Wire"), "ExecState", g.exec_state(T), flush=True)
CASES = [("x,y,z array", "xyz_in", "DBL array -> DBL array (control case)"),
         ("Bead is good? array in", "good_in", "BOOL array -> U8 array (SUSPECT)"),
         ("pos in cal image in", "idx_out", "I32 array -> I32 array (control case)")]
for ctl, param, what in CASES:
    w0 = g.count(T, "Wire"); es0 = g.exec_state(T)
    try:
        g.wire_control(T, [ctl], "CallLibrary", 0, [param]); ok = "accepted"
    except Exception as e:
        ok = f"EXC {str(e)[:120]}"
    w1 = g.count(T, "Wire"); es1 = g.exec_state(T)
    g.remove_bad_wires_scripted(T); purge()
    w2 = g.count(T, "Wire"); es2 = g.exec_state(T)
    verdict = "BAD WIRE (removed)" if w2 < w1 else ("wired" if w1 > w0 else "no wire")
    print(f"  {ctl!r} -> {param}: {what}\n     {ok} | wires {w0}->{w1}->{w2} | ExecState {es0}->{es1}->{es2}  => {verdict}", flush=True)
print("final: wires", g.count(T, "Wire"), "ExecState", g.exec_state(T), flush=True)
try:
    g.close_panel(T); os.remove(T); print("scratch removed", flush=True)
except Exception as e:
    print("cleanup:", str(e)[:80], flush=True)
