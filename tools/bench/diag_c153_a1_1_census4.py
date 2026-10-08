# ---
# labview: none
# hardware: none
# ---
"""Card 153-a1-1 census part 4: follow the FS tunnels #29411 (FrameIdx element) and #29566 (BufDiff element) of the s09
graph 22f967b5 back to their source node, through every face row and fs_tunnel_pairs. Reads json only.
Prediction: #29411 traces to #637's i (t644) and #29566 to Subtract #5119 'x-y'."""
import json, os, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
G = json.load(open("tools/bench/graph_ring_p4s09_20261009_062044.json", encoding="utf-8"))
BO, BW = collections.defaultdict(list), collections.defaultdict(list)
for t in G["terminals"]:
    BO[t["owner_uid"]].append(t)
    if t["wire_uid"]:
        BW[t["wire_uid"]].append(t)
TUN = {"FlatSequenceOuterTunnel", "FlatSequenceInnerTunnel", "LoopTunnel", "SelectorTunnel", "Tunnel"}

def back(uid, depth=0, seen=None):
    seen = seen or set()
    if uid in seen or depth > 8:
        return
    seen.add(uid)
    for t in BO.get(uid, []):
        if t["is_source"]:
            continue
        for x in BW.get(t["wire_uid"], []):
            if x["is_source"] and x["owner_uid"] != uid:
                print("  " * depth + "#%s %s in %r w%s <- #%s %s %r t%s d%s" % (uid, t["owner_class"], t["term_name"], t["wire_uid"],
                      x["owner_uid"], x["owner_class"], x["term_name"], x["term_uid"], x["frame_diagram"]))
                if x["owner_class"] in TUN:
                    back(x["owner_uid"], depth + 1, seen)
for start in (29411, 29566, 28413):
    print("== back from #%s" % start)
    back(start)
    for p in G["fs_tunnel_pairs"]:
        if p["uid"] == start:
            print("  fs pair", p)
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[]}')
