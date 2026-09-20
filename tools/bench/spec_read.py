"""spec_read.py - GPU step 1 raw material: for every analysis-VI COPY in claudeDev\SPEC read
  (a) front-panel control datatypes/defaults over COM (GetControlValue),
  (b) the reporter's object lists (Constant / Node positions + uids),
  (c) net_map of EVERY diagram (wiring: which terminal of which node shares a wire).
Nothing is saved; the copies are throwaway (OpNetInfo's junk Invokes are purged in memory only).
  py tools/bgrun.py --max-min 45 --log tools/bench/spec_read2.log -- py -u tools/bench/spec_read.py
"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
SPEC = os.path.join(g.CLAUDEDEV, "SPEC")
INV = json.load(open(os.path.join(HERE, "spec_inventory.json"), encoding="utf-8"))
OUT = os.path.join(HERE, "spec_wiring.json")
ORDER = ["rect coord from center.vi", "Tracking-fit prepped I of r to cal.vi", "tracking- quadratic fit to phase nghbrd.vi",
         "Tracking-prep I of r.vi", "tracking-calculate phase in neighborhood.vi", "tracking-fit parabola to avg profile.vi",
         "tracking-prep avgx,y profiles.vi", "tracking-average x,y in cross.vi", "tracking-calculate radial profile-openv2.vi",
         "tracking-find avg profile center.vi", "Track 1 of N bds xyz-kernel-reentrant.vi", "Omars IMAQ ImageToArray.vi"]


def describe(v, depth=0):
    if isinstance(v, (memoryview, bytes, bytearray)):
        return {"type": "bytes/" + type(v).__name__, "shape": [len(v)]}
    if isinstance(v, (tuple, list)):
        n = len(v)
        if n and isinstance(v[0], (tuple, list)):
            return {"type": "array2d", "shape": [n, len(v[0])], "sample": [list(r[:4]) for r in v[:2]]}
        return {"type": "array", "shape": [n], "sample": list(v[:6])}
    return {"type": type(v).__name__, "value": v if not isinstance(v, str) else v[:80]}


def purge_junk(target, before):
    junk = g.new_since(target, "Invoke", before)
    for o in junk:
        ids = [x["uid"] for x in g.report(target, "Invoke")]
        if o["uid"] in ids:
            g.delete_object(target, "Invoke", ids.index(o["uid"]))
    if junk:
        g.remove_bad_wires_scripted(target)
    return len(junk)


def main():
    res = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    for name in ORDER:
        if name in res and res[name].get("done"):
            print("skip (done):", name, flush=True); continue
        path = os.path.join(SPEC, name); t0 = time.time()
        print(f"\n=== {name}", flush=True)
        vi = g.op(path)
        fp = {}
        for i, label, is_ind in INV[name]["fp"]:
            try:
                fp[label] = describe(vi.GetControlValue(label)); fp[label]["indicator"] = is_ind
            except Exception as e:
                fp[label] = {"type": "ERR", "err": str(e)[:100], "indicator": is_ind}
        print("  fp:", {k[:24]: (d["type"], d.get("shape", d.get("value"))) for k, d in fp.items()}, flush=True)
        objs = {}
        for cls in ("Constant", "Node", "SubVI", "Structure", "Wire", "ControlTerminal"):
            try:
                objs[cls] = g.report(path, cls)
            except Exception as e:
                objs[cls] = f"ERR {str(e)[:80]}"
        print("  objects:", {k: (len(v) if isinstance(v, list) else v) for k, v in objs.items()}, flush=True)
        ndiag = INV[name]["counts"].get("Diagram", 1)
        g.open_panel(path); time.sleep(0.5)
        inv0 = g.uids(path, "Invoke")
        diags = {}
        for d in range(ndiag):
            t1 = time.time()
            try:
                nodes, nets = g.net_map(path, d, max_nodes=80, max_terms=40)
            except Exception as e:
                print(f"  diagram {d}: ERR {str(e)[:120]}", flush=True); nodes, nets = {}, {}
            diags[d] = {"nodes": {str(k): v for k, v in nodes.items()}, "nets": {str(k): v for k, v in nets.items()}}
            print(f"  diagram {d}: {len(nodes)} nodes, {len(nets)} nets, {time.time() - t1:.0f}s", flush=True)
        print("  junk Invokes left in memory (copies are never saved; purge costs ~4 s each):", len(g.new_since(path, "Invoke", inv0)), flush=True)
        res[name] = {"fp": fp, "objects": objs, "diagrams": diags, "done": True, "secs": round(time.time() - t0)}
        json.dump(res, open(OUT + ".tmp", "w", encoding="utf-8"), indent=1, default=str); os.replace(OUT + ".tmp", OUT)
        print(f"  saved ({time.time() - t0:.0f}s)", flush=True)
    print("ALL DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
