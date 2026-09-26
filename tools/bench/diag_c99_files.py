"""diag_c99_files - card 99-1, FILES ONLY (no LabVIEW, no COM).

Existing tools checked first: par1359_95_graph.json (offline graph of D1_s1_copy, cycle 95), diag_c97_gatefacts.json
(145 COM-read labels, cycle 97), t0_sites_s1.json (cycle 90 site map), t0_step4v2_94.json (cycle 94 timings). No new
reader is needed for F1a/F2/F4; this script only joins them.

PREDICTION CONTRACT
 P1 graph json 'md5' == 3e3d23cefd3a334001aa9d6156bf1aee (it describes D1_s1_copy.vi)
 P2 wire 10908 has exactly 2 terminal records: sink = #8323 (owner 8323?), source = BuildArray #11261 output
 P3 #8323 and #11261 sit on diagram 639 (WhileLoop #637 body)
 P4 #6085 / #5696 are SubVI nodes each inside a case frame (2235 / 2265) of 639
 P5 no Local object in the graph resolves to #8323 (c97 labels: 8 locals, none named Force)
"""
import json, sys, hashlib, collections

B = "tools/bench/"
g = json.load(open(B + "par1359_95_graph.json", encoding="utf-8"))
lab = json.load(open(B + "diag_c97_gatefacts.json", encoding="utf-8"))["labels"]
sites = json.load(open(B + "t0_sites_s1.json", encoding="utf-8"))
out = {"gates": {"pass": [], "fail": []}}

def gate(name, ok, got):
    (out["gates"]["pass"] if ok else out["gates"]["fail"]).append(name)
    print(("  PASS  " if ok else "  FAIL  ") + name, " got", got)

objs = {o["uid"]: o for o in g["objs"]}
by_wire = collections.defaultdict(list)
by_owner = collections.defaultdict(list)
for t in g["terminals"]:
    by_wire[t["wire_uid"]].append(t)
    by_owner[t["owner_uid"]].append(t)

print("vi", g["vi"], "md5", g["md5"], "summary", {k: g["graph_summary"][k] for k in ("objects", "nodes", "wires", "locals", "globals", "diagrams")})
print("note", g.get("note", "")[:400])
gate("P1 graph md5 == S1", g["md5"].startswith("3e3d23ce"), g["md5"])

def o(uid):
    x = objs.get(uid)
    return f"#{uid} {x['class']} owner={x['owner']}" if x else f"#{uid} (not in objs)"

def wire_ends(w):
    if not w:
        return ["UNWIRED"]
    return [(t["term_uid"], t["term_name"], "SRC" if t["is_source"] else "sink", t["owner_uid"], t["owner_class"], t["frame_diagram"], t["term_class"]) for t in by_wire.get(w, [])]

print("\n[F1a] wire 10908 ends:")
for e in wire_ends(10908):
    print("   ", e)
print("   obj 8323:", o(8323)); print("   obj 11261:", o(11261))
ends = wire_ends(10908)
src = [e for e in ends if e[2] == "SRC"]
gate("P2 w10908 source is BuildArray #11261", len(src) == 1 and src[0][3] == 11261, src)
print("   #11261 terminals:")
for t in by_owner[11261]:
    print("     ", t["term_uid"], repr(t["term_name"]), "SRC" if t["is_source"] else "sink", "wire", t["wire_uid"], "->", [e for e in wire_ends(t["wire_uid"]) if e[3] != 11261])
print("   #8323 terminals / records owned by 8323:", [(t["term_uid"], t["term_name"], t["wire_uid"]) for t in by_owner[8323]])
print("   records whose term_uid == 8323:", [(t["term_name"], t["wire_uid"], t["owner_uid"], t["owner_class"], t["frame_diagram"]) for t in g["terminals"] if t["term_uid"] == 8323])

print("\n[F2] SubVI plot nodes 6085 / 5696:")
for n in (6085, 5696):
    print("   obj", o(n))
    for t in by_owner[n]:
        others = [e for e in wire_ends(t["wire_uid"]) if e[3] != n]
        print("     ", t["term_uid"], repr(t["term_name"]), "SRC" if t["is_source"] else "sink", "wire", t["wire_uid"], "frame", t["frame_diagram"], "->", others)

print("\n[F2] Local / Global / Property / Invoke / ControlReference objects with c97 labels:")
cc = collections.Counter(x["class"] for x in g["objs"])
print("   class census (subset):", {k: v for k, v in cc.items() if any(s in k for s in ("Local", "Global", "Property", "Invoke", "Reference", "Terminal", "Event"))})
hits = []
for uid, rec in lab.items():
    s = json.dumps(rec, ensure_ascii=False)
    if any(k in s for k in ("Force", "plot", "Plot", " Z", "dZ", "graph", "Graph", "Extension")):
        hits.append((uid, s[:220]))
print("   c97 labels matching Force/plot/Z/graph:", len(hits))
for h in hits:
    print("     ", h)
locs = [x for x in g["objs"] if "Local" in x["class"]]
print("   Local objs in graph:", [(x["uid"], x["class"], x["owner"]) for x in locs])
gate("P5 c97 label hits for 'Force' only #10313", all(("Force" not in h[1]) or h[0] == "10313" for h in hits), [h[0] for h in hits])

print("\n[F4] t0 sites in loop 637 (cycle 90 map):")
for s in sites["sites"]:
    if s.get("holding_loop") == 637:
        print("   ", s["group"], s["node_uid"], "diag", s["diagram"], "cases", s["case_frames_between_node_and_loop"], "every_iter", s["runs_every_iteration"], "stamp", s["stamp_terminal"])
for f in sites.get("facts", []):
    if any(k in f for k in ("plot", "Z", "Median", "FIR", "8323", "display")):
        print("   FACT", f[:300])

json.dump(out, open(B + "diag_c99_files.json", "w"), indent=1)
ng = out["gates"]
print(f"RESULT {json.dumps({'schema':'result-line/1','status':'PASS' if not ng['fail'] else 'FAIL','gates':{'pass':len(ng['pass']),'fail':len(ng['fail'])},'first_fail':ng['fail'][0] if ng['fail'] else None,'artefacts':[]})}")
