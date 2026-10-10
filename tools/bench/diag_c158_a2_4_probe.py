# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_158-a2-4.md
# ---
"""diag_c158_a2_4_probe - card 158-a2-4 (OFFLINE): the stored graph 6716c499's shape (keys, field names, class counts) before the
mutation table is written. Reads only. PREDICTION: keys terminals / objs (+ loops, fs_tunnel_pairs); no value column."""
import os, sys, json, collections                                                       # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                                     # noqa: E402
import protocol                                                                          # noqa: E402

G = K.jload(K.BENCH, "graph_ring_p5s01_20261009_125622.json")
print("KEYS", [(k, type(v).__name__, len(v) if hasattr(v, "__len__") else v) for k, v in G.items()])
for k in ("terminals", "objs", "loops"):
    v = G.get(k) or []
    if v:
        print(k, "FIELDS", sorted(set(f for r in v for f in r)))
        print(k, "ROW0", json.dumps(v[0])[:300])
fs = G.get("fs_tunnel_pairs")
print("FS", type(fs).__name__, json.dumps(fs)[:300] if fs else None)
T = G["terminals"]
print("OWNER CLASSES", collections.Counter(r["owner_class"] for r in T).most_common())
print("TERM CLASSES", collections.Counter(r.get("term_class") for r in T).most_common())
print("OBJ CLASSES", collections.Counter(o.get("class") for o in G.get("objs") or []).most_common(40))
W = collections.defaultdict(lambda: [0, 0])
for r in T:
    if r.get("wire_uid"):
        W[r["wire_uid"]][0 if r["is_source"] else 1] += 1
print("WIRES", len(W), collections.Counter(tuple(v) for v in W.values()).most_common(8))
print("FRAME_DIAGRAM set on", sum(1 for r in T if r.get("frame_diagram")), "of", len(T))
print(protocol.result_line({"status": "PASS", "gates": {"pass": 1, "fail": 0}, "first_fail": None, "artefacts": []}))
