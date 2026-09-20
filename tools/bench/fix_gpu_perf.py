"""fix_gpu_perf.py - HARNESS_gpu.vi: delete the CLFN output-side wires that copy big arrays into placeholder indicators every
frame: t25 'Array of Images' -> 'Array of Images 2' (1.3 MB 3-D U8), t17 'X Array' -> 'X Array 4', t39 'Test Array' -> 'Test Array 2'.
Wire uids from the saved file's net map (2026-09-08): 718, 1989, 1548.  No net_map (junk)."""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
OP = os.path.join(g.CLAUDEDEV, "HARNESS_gpu.vi")
g.report(OP, "SubVI"); g.open_panel(OP); time.sleep(1.0)
w0 = g.count(OP, "Wire"); print("ExecState", g.exec_state(OP), "wires", w0, "Invokes", g.count(OP, "Invoke"), flush=True)
for uid in (718, 1989, 1548):
    ws = [o["uid"] for o in g.report(OP, "Wire")]
    if uid in ws:
        g.delete_object(OP, "Wire", ws.index(uid)); print("deleted wire", uid, "->", g.count(OP, "Wire"), flush=True)
    else:
        print("wire", uid, "not found", flush=True)
g.remove_bad_wires_scripted(OP); es = g.exec_state(OP); print("ExecState", es, "wires", g.count(OP, "Wire"), flush=True)
if es != 1 or g.count(OP, "Wire") != w0 - 3:
    print("STOP: not saving", flush=True); sys.exit(3)
print("saved", g.save(OP), flush=True)
