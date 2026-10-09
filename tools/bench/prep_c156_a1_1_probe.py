# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_156-a1-1.md
# ---
"""prep_c156_a1_1_probe - card 156-a1-1 (OFFLINE, json only): read-only probe of the P5-1 graph 6716c499 rows the P5-2 re-plan needs:
the out-tunnels #5204 / #10404 and their outer sinks, the scaffold stop #23042 and loop #23041's cond terminal (stop mode), types of
#376 t3 / t4, and every graph field naming a stop mode. Prediction: every row prints; RESULT 1/0.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c156_a1_1_probe.log -- py -u tools/bench/prep_c156_a1_1_probe.py"""
import collections, json, os, sys                                                          # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
GP = os.path.join(ROOT, "tools", "bench", "graph_ring_p5s01_20261009_125622.json")
G = json.load(open(GP, encoding="utf-8"))
print("KEYS", sorted(G.keys()))
T = G["terminals"]
print("ROW0", json.dumps(T[0]))
OBJ = dict((int(o["uid"]), o) for o in G["objs"])
BYW = collections.defaultdict(list)
for r in T:
    if r.get("wire_uid"):
        BYW[r["wire_uid"]].append(r)
for u in (23041, 23405, 23042, 23501, 5204, 10404, 376, 6384, 2048, 3453):
    print("OBJ", u, json.dumps(OBJ.get(u)), "owner", G.get("owners", {}).get(str(u)))
for u in (23041, 23405, 23042, 5204, 10404, 376):
    for r in T:
        if int(r["owner_uid"]) == u:
            print("  T", u, r["term_uid"], repr(r["term_name"]), r["term_class"], r["is_source"], r.get("wire_uid"), r.get("frame_diagram"),
                  dict((k, v) for k, v in r.items() if k not in ("owner_uid", "term_uid", "term_name", "term_class", "is_source", "wire_uid", "frame_diagram")),
                  [(x["owner_uid"], x["owner_class"], x["term_name"], x["term_uid"]) for x in BYW.get(r.get("wire_uid"), []) if x["term_uid"] != r["term_uid"]])
for k in G:
    if k not in ("terminals", "objs", "owners"):
        s = json.dumps(G[k], default=str)
        print("FIELD", k, len(s), s[:300])
hits = [(k, i) for k in G for i, x in enumerate(G[k] if isinstance(G[k], list) else []) if "stop" in json.dumps(x, default=str).lower()][:20]
print("STOP-MENTIONS", hits)
for k, i in hits[:8]:
    print("  ", k, i, json.dumps(G[k][i], default=str)[:400])
print(protocol.result_line(protocol.make_result(1, 0, None, [])))
