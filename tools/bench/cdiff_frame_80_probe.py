"""Offline probe (no LabVIEW): layout of the graph/wiki sources for card 80-7."""
import json, os, sys, collections
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
os.chdir(ROOT)
sys.path.insert(0, "tools")
import jev_candidates as JC  # noqa: E402
print("S1_KEY", JC.S1_KEY, "BED_KEY", JC.BED_KEY)
w = json.load(open("docs/wiki/subvi/D1_s1_copy.json", encoding="utf-8"))
print("wiki keys", {k: (type(v).__name__, len(v) if hasattr(v, "__len__") else v) for k, v in w.items()})
g = json.load(open("tools/bench/l2a1_graph_k_80.json", encoding="utf-8"))
print("obj sample", g["objs"][0])
print("term sample", g["terminals"][0])
for name, T, O in (("S1", w.get("terminals"), w.get("objs")), ("K", g["terminals"], g["objs"])):
    cls = collections.Counter(o["class"] for o in (O or []))
    print(name, "CaseStructure", cls.get("CaseStructure"), "SelectorTunnel", cls.get("SelectorTunnel"), "Tunnel", cls.get("Tunnel"))
    for tu in (5680, 5702, 5725, 5825, 5967, 6016, 5603, 10465, 10584, 10750, 11336):
        rs = [r for r in T if r["owner_uid"] == tu]
        print(name, tu, [(r["term_uid"], r["term_class"] if "term_class" in r else "", r["is_source"], r["wire_uid"], r.get("frame_diagram")) for r in rs])
for k in ("case_frames", "frames", "structures"):
    if k in w:
        print(k, str(w[k])[:600])
