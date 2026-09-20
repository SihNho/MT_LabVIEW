"""patch_gpu_harness.py - HARNESS_gpu.vi: wire the loader's 'Array of cal clusters' into the CLFN's 'Array Cal Cluster' by
terminal INDEX (connect_terminals; the name route raised 5001), purge OpNetInfo junk, verify, save; then smoke one frame."""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "gpu"))
import gscript as g
from fixture import read_cal, read_reference, DATA
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
OP = os.path.join(g.CLAUDEDEV, "HARNESS_gpu.vi")
g.report(OP, "SubVI"); g.open_panel(OP); time.sleep(1.0)
print("ExecState", g.exec_state(OP), "wires", g.count(OP, "Wire"), flush=True)
inv0 = g.uids(OP, "Invoke")
nodes, nets = g.net_map(OP, 0, max_nodes=30, max_terms=48)
nL = tL = None
for n, (uid, _, terms) in nodes.items():
    for t, nm, w in terms:
        if nm == "Array of cal clusters":
            nL, tL = n, t
print("loader node/terminal:", nL, tL, "| CLFN t32:", [x for x in nodes[0][2] if x[0] == 32], flush=True)
if nL is None:
    print("STOP: loader terminal not found", flush=True); sys.exit(2)
w0 = g.count(OP, "Wire")
print("connect_terminals ->", g.connect_terminals(OP, 0, 32, nL, tL), "wires", w0, "->", g.count(OP, "Wire"), flush=True)
for o in g.new_since(OP, "Invoke", inv0):
    ids = [x["uid"] for x in g.report(OP, "Invoke")]
    if o["uid"] in ids:
        g.delete_object(OP, "Invoke", ids.index(o["uid"]))
g.remove_bad_wires_scripted(OP)
es = g.exec_state(OP); print("ExecState", es, "wires", g.count(OP, "Wire"), flush=True)
if es != 1:
    print("STOP: broken", flush=True); sys.exit(3)
print("saved", g.save(OP), flush=True)
# smoke: one fixture frame
lab = json.load(open(os.path.join(HERE, "harness_gpu_labels.json")))
xy0 = read_cal()["xy"]; row = read_reference()["frames"][0]; nb = len(xy0)
vi = g.op(OP); C = lab["controls"]
vi.SetControlValue(C["Image Name"], "gpu"); vi.SetControlValue(C["File Path"], os.path.join(DATA, f"img{row['frame']:05d}.tif"))
vi.SetControlValue(C["x,y,z array"], [v for x, y in xy0 for v in (x, y, 0.0)]); vi.SetControlValue(C["Bead is good? array in"], [True] * nb)
vi.SetControlValue(C["pos in cal image in"], [0] * nb); vi.SetControlValue(C["Error Message"], " " * 64)
t0 = time.time(); g._run(vi); dt = time.time() - t0
out = list(vi.GetControlValue(lab["outputs"]["x,y,z array out"])); msg = vi.GetControlValue(lab["outputs"]["Error Message out"])
print(f"run {dt * 1e3:.0f} ms; msg {msg!r}; out {[round(v, 6) for v in out[:6]]}; ref {[round(v, 6) for v in row['ff'][:6]]}; max|diff| {max(abs(a - b) for a, b in zip(out, row['ff'])):.2e}", flush=True)
print("pos", vi.GetControlValue(lab["outputs"]["pos in cal image out"]), "good", vi.GetControlValue(lab["outputs"]["Bead is good? array out"]), flush=True)
