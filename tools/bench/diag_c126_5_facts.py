r"""diag_c126_5_facts - card 126-5, OFFLINE read-only (no LabVIEW, no COM): the P3a-graph facts P3b's plan input binds to.
Reads tools/bench/graph_ring_p3a_20261001_190155.json (md5 2fa6ce0c) and tools/bench/census_samples.json; writes nothing.
Prediction: case #22694 on 639 with frames 27219/27232; #6810 t6897/t6865 on 639; the 5 P2b indicators on #4866;
#23099 t23289 unwired in body 23169. Prints the rest as FACT lines. Ends with a RESULT line."""
import collections, json, os, sys
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(B))
import protocol as P  # noqa: E402
G = json.load(open(os.path.join(B, "graph_ring_p3a_20261001_190155.json"), encoding="utf-8"))
print("KEYS", sorted(G))
T = G["terminals"]
objs = G.get("objs") or G.get("objects") or []
print("N terminals", len(T), "objs", len(objs), "obj keys", sorted(objs[0]) if objs else None)
own = G.get("owners") or {}
print("owners sample", list(own.items())[:3])
byo = collections.defaultdict(list)
for r in T:
    byo[r["owner_uid"]].append(r)
cls_of = dict((int(o["uid"]), o.get("class")) for o in objs)
ok = []


def rows(u):
    return [(r["term_uid"], r["term_name"], r["term_class"], int(bool(r["is_source"])), r["wire_uid"], r["frame_diagram"]) for r in byo[u]]


def wsinks(w):
    return [(r["owner_uid"], r["owner_class"], r["term_name"], r["frame_diagram"]) for r in T if r["wire_uid"] == w and not r["is_source"]]


for u in (6810, 30117, 4580, 23099, 22694, 27344, 27365):
    print("NODE", u, cls_of.get(u), rows(u)[:12])
print("OWNERS 27219/27232/639/686/23169/4866/13236", [(k, own.get(str(k))) for k in (27219, 27232, 639, 686, 23169, 4866, 13236, 22694)])
for t in (6897, 6865, 6924, 30145, 4728, 644, 23289, 35255, 35215, 35319, 27025, 35418):
    r = next((x for x in T if x["term_uid"] == t), None)
    print("TERM", t, r and (r["owner_uid"], r["owner_class"], r["term_name"], r["term_class"], r["is_source"], r["wire_uid"], r["frame_diagram"]),
          "sinks", r and r["wire_uid"] and wsinks(r["wire_uid"]))
# everything on the case frames
for f in (27219, 27232):
    print("FRAME", f, sorted(set((r["owner_uid"], r["owner_class"]) for r in T if r["frame_diagram"] == f)))
    for r in T:
        if r["frame_diagram"] == f:
            print("   ROW", r["owner_uid"], r["owner_class"], repr(r["term_name"]), r["term_class"], int(bool(r["is_source"])), r["wire_uid"])
# donors: Index Array / Replace Array Subset candidates in the graph
names = collections.defaultdict(set)
for r in T:
    names[r["owner_uid"]].add(r["term_name"])
for u, ns in names.items():
    if ("index 0" in ns and "array" in ns) or "new element/subarray" in ns or "output array" in ns:
        print("DONOR?", u, cls_of.get(u), [(x[1], x[2], x[3], x[4], x[5]) for x in rows(u)])
# objects of interest
print("CLASS COUNTS", collections.Counter(cls_of.values()).most_common(40))
print("FS2/For #23093", cls_of.get(23093), "fs_pairs n", len(G.get("fs_pairs") or []))
cs = json.load(open(os.path.join(B, "census_samples.json"), encoding="utf-8"))
print("CENSUS keys", sorted(cs))
for k in ("samples", "ops"):
    if isinstance(cs.get(k), (list, dict)):
        it = cs[k].items() if isinstance(cs[k], dict) else enumerate(cs[k])
        for kk, v in it:
            print("  SAMPLE", kk, json.dumps(v)[:400])
ok.append(cls_of.get(22694) == "CaseStructure")
print(P.result_line(P.make_result(sum(ok), len(ok) - sum(ok), None if all(ok) else "case 22694 class")))
