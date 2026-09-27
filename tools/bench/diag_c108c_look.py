"""c108c look: dump group-B nodes' terminals and one-hop consumers from the L2-A1 bed graph (offline)."""
import json, collections
ROOT = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop"
g = json.load(open(ROOT + r"\tools\bench\graph_l2a1_bed_20260927.json", encoding="utf-8"))
B = [1359, 2222, 2626, 6104, 8885, 9833, 11261, 29874]
CTL = [47, 9289, 28148, 28996, 403, 9306, 28170, 29091]
objs = {o["uid"]: o for o in g["objs"]}
terms = g["terminals"]
by_owner = collections.defaultdict(list)
by_wire = collections.defaultdict(list)
for t in terms:
    by_owner[t["owner_uid"]].append(t)
    if t.get("wire_uid"):
        by_wire[t["wire_uid"]].append(t)
print("graph_summary", g["graph_summary"])
print("owners sample", list(g["owners"].items())[:5])
print("obj keys", set(k for o in g["objs"] for k in o))
print("term keys", set(k for t in terms for k in t))
for u in B + CTL:
    o = objs.get(u)
    print("\n### #%d obj=%s" % (u, o))
    # objects owned by u
    kids = [x for x in g["objs"] if str(x.get("owner")) == str(u) or x.get("owner") == u]
    print("  owned objs:", [(k["uid"], k["class"]) for k in kids][:40])
    for t in by_owner.get(u, []):
        others = [(x["owner_uid"], x["owner_class"], x["term_name"], x["is_source"], x["frame_diagram"]) for x in by_wire.get(t["wire_uid"], []) if x is not t]
        print("  t%s %r src=%s w=%s fd=%s -> %s" % (t["term_uid"], t["term_name"], t["is_source"], t["wire_uid"], t["frame_diagram"], others))
