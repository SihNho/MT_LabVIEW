"""diag_c112a_fixgraph - card 112-1: the DRY graph for the T2 scratch fixture (no LabVIEW). stage_prerun.find_graph accepts
tools/bench/sim/<stage>/graph_*.json by top-level md5; the wiki record docs/wiki/subvi/Motor control.json was read LIVE from
the same file (its md5 3bf4ec68... == the fixture's), so its terminal table is re-shaped, not re-read.
    py tools/bgrun.py --material --max-min 1 --log tools/bench/diag_c112a_fixgraph.log -- py -u tools/bench/diag_c112a_fixgraph.py"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
W = json.load(open(os.path.join(ROOT, "docs", "wiki", "subvi", "Motor control.json"), encoding="utf-8"))
print("wiki keys", sorted(W.keys()))
fix = W["file"]
md5 = hashlib.md5(open(fix, "rb").read()).hexdigest()
ok = md5 == W["md5"]
print("fixture md5", md5, "wiki md5", W["md5"], "match", ok)
G = {"vi": fix, "md5": W["md5"], "source": "docs/wiki/subvi/Motor control.json (re-shaped by diag_c112a_fixgraph.py)",
     "terminals": W.get("terminals") or [], "objs": W.get("objs") or W.get("gobjects") or [],
     "owners": W.get("owners") or {}, "loops": W.get("loops") or [], "fs_tunnel_pairs": W.get("fs_tunnel_pairs")}
if not G["objs"]:
    # the wiki record carries no GObject census: the DRY-ONLY object list is DERIVED from the terminal table (every owner
    # uid with its owner class, every frame diagram as 'Diagram') - marked as derived; the LabVIEW run reads its own census
    seen = {}
    for r in G["terminals"]:
        seen.setdefault(int(r["owner_uid"]), r["owner_class"])
        if r.get("frame_diagram"):
            seen.setdefault(int(r["frame_diagram"]), "Diagram")
    G["objs"] = [{"uid": u, "class": c, "pos": [0, 0], "owner": "derived-from-terminals"} for u, c in sorted(seen.items())]
    G["objs_derived"] = True
out = os.path.join(HERE, "sim", "c112a_ctltun")
os.makedirs(out, exist_ok=True)
p = os.path.join(out, "graph_motorcontrol.json")
json.dump(G, open(p, "w", encoding="utf-8"), indent=0)
print("wrote", p, "terminals", len(G["terminals"]), "objs", len(G["objs"]), "owners", len(G["owners"]))
st = "PASS" if ok and G["terminals"] else "FAIL"
print('RESULT {"schema":"result-line/1","status":"%s","gates":{"pass":%d,"fail":%d},"first_fail":%s,"artefacts":[]}'
      % (st, 1 if st == "PASS" else 0, 0 if st == "PASS" else 1, "null" if st == "PASS" else '"md5 or terminals"'))
