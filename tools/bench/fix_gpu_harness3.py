"""fix_gpu_harness3.py - HARNESS_gpu.vi: the donor's decorated export (?GPUTracking@@...PAPAUArray2d@@22...) makes X/Y/Z Output
2-D DBL arrays; their placeholder INDICATORS on the CLFN's output terminals (t29 'Y Output 2', t31 'Z Output 2') pin the
parameter type, so the 1-D win_h wire (t28) and the bool good-flags wire (t30) were removed as BAD every time.
Fix: delete the two indicator wires, wire W.Hilbert -> Y Output and Bead Is Good -> Z Output (branch), create a typed
indicator on t31, purge junk, verify by net_map, save.  Smoke runs separately (gpu_smoke_file.py, fresh client)."""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "gpu"))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
OP = os.path.join(g.CLAUDEDEV, "HARNESS_gpu.vi"); LABELS = os.path.join(HERE, "harness_gpu_labels.json")
g.report(OP, "SubVI"); g.open_panel(OP); time.sleep(1.0)
print("ExecState", g.exec_state(OP), "wires", g.count(OP, "Wire"), flush=True)
inv0 = g.uids(OP, "Invoke")


def clfn_map():
    nodes, nets = g.net_map(OP, 0, max_nodes=8, max_terms=48)
    return nodes, {t: w for t, nm, w in nodes[0][2]}


nodes, T = clfn_map(); print("CLFN t28..t31:", {t: T.get(t) for t in (28, 29, 30, 31)}, "t32", T.get(32), flush=True)
for t in (29, 31):
    w = T.get(t)
    if w:
        ws = [o["uid"] for o in g.report(OP, "Wire")]
        if w in ws:
            g.delete_object(OP, "Wire", ws.index(w)); print(f"deleted indicator wire {w} at t{t}; wires {g.count(OP, 'Wire')}", flush=True)
nW = next(n for n, (uid, _, terms) in nodes.items() if any(nm == "Cosine bandpass for Hilbert" for _, nm, _ in terms))
iW = [o["uid"] for o in g.report(OP, "SubVI")].index(nodes[nW][0])
print("wire W.Hilbert -> Y Output:", g.wire(OP, "SubVI", iW, "Cosine bandpass for Hilbert", "CallLibrary", 0, "Y Output"), "wires", g.count(OP, "Wire"), flush=True)
print("wire_control Bead Is Good Array -> Z Output (branch):", g.wire_control(OP, ["Bead Is Good Array"], "CallLibrary", 0, ["Z Output"], branch=True), "wires", g.count(OP, "Wire"), flush=True)
fp0 = {l for _, l, _ in g.fp_labels(OP)}
new = g.create_indicator(OP, 0, 31); labs = [l for _, l, _ in g.fp_labels(OP) if l not in fp0]
print("indicator on t31:", new, labs, flush=True)
for o in g.new_since(OP, "Invoke", inv0):
    ids = [x["uid"] for x in g.report(OP, "Invoke")]
    if o["uid"] in ids:
        g.delete_object(OP, "Invoke", ids.index(o["uid"]))
g.remove_bad_wires_scripted(OP)
es = g.exec_state(OP); nodes, T = clfn_map()
print("ExecState", es, "wires", g.count(OP, "Wire"), "CLFN t28..t31:", {t: T.get(t) for t in (28, 29, 30, 31)}, "t32", T.get(32), flush=True)
if es != 1 or not T.get(28) or not T.get(30):
    print("STOP: broken or wires rejected - NOT saving", flush=True); sys.exit(3)
print("saved", g.save(OP), flush=True)
lab = json.load(open(LABELS))
if labs:
    lab["outputs"]["Bead is good? array out"] = labs[-1]; json.dump(lab, open(LABELS, "w"), indent=1); print("labels:", lab["outputs"], flush=True)
