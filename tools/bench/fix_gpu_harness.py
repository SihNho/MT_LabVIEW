"""fix_gpu_harness.py - HARNESS_gpu.vi: map the CLFN's terminals, re-wire W.Hilbert -> CLFN 'Y Output' (t28) if unwired
(the DLL saw yout=0 after the cluster-wire patch), purge junk Invokes, verify, save, then smoke two fixture frames."""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "gpu"))
import gscript as g
from fixture import read_cal, read_reference, DATA, CAL
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
OP = os.path.join(g.CLAUDEDEV, "HARNESS_gpu.vi")
g.report(OP, "SubVI"); g.open_panel(OP); time.sleep(1.0)
print("ExecState", g.exec_state(OP), "wires", g.count(OP, "Wire"), flush=True)
inv0 = g.uids(OP, "Invoke")
nodes, nets = g.net_map(OP, 0, max_nodes=30, max_terms=48)
subs = {o["uid"]: o for o in g.report(OP, "SubVI")}
for n, (uid, _, terms) in nodes.items():
    print(f"node {n} uid {uid} {'SubVI' if uid in subs else ''}:", [(t, nm, w) for t, nm, w in terms if w or t in (28, 29, 32, 33)][:60], flush=True)
clfn = nodes[0][2]; t28 = [w for t, nm, w in clfn if t == 28]; t32 = [w for t, nm, w in clfn if t == 32]
print("CLFN t28 (Y Output) wire", t28, "| t32 (Array Cal Cluster) wire", t32, flush=True)
nW = None
for n, (uid, _, terms) in nodes.items():
    if any(nm == "Cosine bandpass for Hilbert" for _, nm, _ in terms):
        nW = n; tW = [t for t, nm, _ in terms if nm == "Cosine bandpass for Hilbert"][0]; wW = [w for t, nm, w in terms if nm == "Cosine bandpass for Hilbert"][0]
print("W node", nW, "Hilbert terminal", tW if nW is not None else None, "wire", wW if nW is not None else None, flush=True)
changed = False
if t28 and t28[0] == 0 and nW is not None:
    w0 = g.count(OP, "Wire")
    print("connect_terminals CLFN t28 <- W.Hilbert ->", g.connect_terminals(OP, 0, 28, nW, tW), "wires", w0, "->", g.count(OP, "Wire"), flush=True)
    changed = True
elif t28 and t28[0]:
    print("t28 already wired: wire", t28[0], "net", nets.get(t28[0]), flush=True)
for o in g.new_since(OP, "Invoke", inv0):
    ids = [x["uid"] for x in g.report(OP, "Invoke")]
    if o["uid"] in ids:
        g.delete_object(OP, "Invoke", ids.index(o["uid"]))
g.remove_bad_wires_scripted(OP)
es = g.exec_state(OP); print("ExecState", es, "wires", g.count(OP, "Wire"), flush=True)
if es != 1:
    print("STOP: broken", flush=True); sys.exit(3)
if changed:
    print("saved", g.save(OP), flush=True)
lab = json.load(open(os.path.join(HERE, "harness_gpu_labels.json"))); C = lab["controls"]
xy0 = read_cal()["xy"]; rows = read_reference()["frames"]; nb = len(xy0)
ld = g.op(os.path.join(g.CLAUDEDEV, "HARNESS_loadcal.vi")); ld.SetControlValue("file (use dialog)", CAL); g._run(ld)
vi = g.op(OP); vi.SetControlValue(C["Image Name"], "gpu")
for k in (0, 1):
    row = rows[k]
    vi.SetControlValue(C["File Path"], os.path.join(DATA, f"img{row['frame']:05d}.tif"))
    vi.SetControlValue(C["x,y,z array"], [v for x, y in xy0 for v in (x, y, 0.0)]); vi.SetControlValue(C["Bead is good? array in"], [True] * nb)
    vi.SetControlValue(C["pos in cal image in"], [0] * nb); vi.SetControlValue(C["Error Message"], CAL + " " * 8)
    t0 = time.time(); g._run(vi); dt = time.time() - t0
    out = list(vi.GetControlValue(lab["outputs"]["x,y,z array out"])); msg = vi.GetControlValue(lab["outputs"]["Error Message out"])
    print(f"frame {row['frame']}: run {dt * 1e3:.0f} ms; msg {msg!r}; out {[round(v, 6) for v in out[:6]]}; ref {[round(v, 6) for v in row['ff'][:6]]}; "
          f"max|diff| {max(abs(a - b) for a, b in zip(out, row['ff'])):.2e}", flush=True)
    print("   pos", list(vi.GetControlValue(lab["outputs"]["pos in cal image out"])), "good", list(vi.GetControlValue(lab["outputs"]["Bead is good? array out"])), flush=True)
