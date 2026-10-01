"""card 131-1 Part A helper (read-only, no LabVIEW): on the P3a base graph (graph_ring_p3a_20261001_190155.json), for every
tunnel face that is a SINK, compare its name with the name of the SOURCE terminal on the same wire, grouped by the source's
owner class. Also every tunnel object's source face vs its sink face(s). PRIOR ART: stagesim._cross_tunnel_name (129-7) used
only the net's existing tunnel names. PREDICTION: SubVI sources -> sink faces carry the source name; Function sources -> ''."""
import collections, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import protocol
B = os.path.dirname(os.path.abspath(__file__))
TUN = ("SelectorTunnel", "LoopTunnel", "FlatSequenceOuterTunnel", "FlatSequenceInnerTunnel", "Tunnel",
       "LeftShiftRegister", "RightShiftRegister")
g = json.load(open(os.path.join(B, "graph_ring_p3a_20261001_190155.json"), encoding="utf-8"))
T = g["terminals"]
byw = collections.defaultdict(list)
for r in T:
    if r["wire_uid"]:
        byw[r["wire_uid"]].append(r)
agg = collections.Counter()
ex = collections.defaultdict(list)
for w, rs in byw.items():
    src = [r for r in rs if r["is_source"]]
    if len(src) != 1:
        continue
    s = src[0]
    for r in rs:
        if r is s or r["owner_class"] not in TUN or r["is_source"]:
            continue
        rel = "same" if r["term_name"] == s["term_name"] else ("empty" if r["term_name"] == "" else "other")
        k = (s["owner_class"], "src_named" if s["term_name"] else "src_empty", r["owner_class"], r["term_class"], rel)
        agg[k] += 1
        if len(ex[k]) < 4:
            ex[k].append((w, s["term_uid"], s["term_name"], r["owner_uid"], r["term_uid"], r["term_name"]))
for k in sorted(agg):
    print("AGG", k, agg[k], "e.g.", ex[k][:3])
# tunnel objects: names across their faces
byo = collections.defaultdict(list)
for r in T:
    if r["owner_class"] in TUN:
        byo[r["owner_uid"]].append(r)
fc = collections.Counter()
fex = collections.defaultdict(list)
for o, rs in byo.items():
    names = sorted(set(r["term_name"] for r in rs))
    k = (rs[0]["owner_class"], "uniform" if len(names) == 1 else "mixed")
    fc[k] += 1
    if k[1] == "mixed" and len(fex[k]) < 6:
        fex[k].append((o, [(r["term_class"], r["is_source"], r["term_name"], r["frame_diagram"], r["wire_uid"]) for r in rs]))
for k in sorted(fc):
    print("FACES", k, fc[k], fex.get(k, [])[:6])
for w in (3040, 653, 3747, 3268):
    print("NET", w, [(r["term_uid"], r["term_name"], r["is_source"], r["owner_uid"], r["owner_class"], r["frame_diagram"]) for r in byw.get(w, [])])
for t in (30145, 4728, 644, 6865, 6897, 23289, 27401, 6814):
    r = next((x for x in T if x["term_uid"] == t), None)
    print("TERM", t, r and (r["term_name"], r["owner_uid"], r["owner_class"], r["wire_uid"], r["frame_diagram"]),
          r and [(x["term_uid"], x["term_name"], x["owner_class"], x["term_class"], x["is_source"]) for x in byw.get(r["wire_uid"], [])
                 if x["owner_class"] in TUN])
print(protocol.result_line(protocol.make_result(1, 0, None)))
