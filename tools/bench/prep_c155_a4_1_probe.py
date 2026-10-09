# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_155-a4-1.md
# ---
"""prep_c155_a4_1_probe - card 155-a4-1, OFFLINE read of the P5-1 graph 6716c499 (json only): the rows of every uid the P5-2
decisions name (PD374(c)(d), PD376(d)), so the plan rows can cite real uids. Read-only; writes nothing but its log.
PREDICTION CONTRACT: every named uid has an owners entry or object row; prints terminal rows with wires; RESULT line."""
import json, os, sys                                                                           # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
G = json.load(open(os.path.join(ROOT, "tools", "bench", "graph_ring_p5s01_20261009_125622.json"), encoding="utf-8"))
print("KEYS", sorted(G.keys()))
T, OWN, OBJ = G["terminals"], G.get("owners") or {}, dict((int(o["uid"]), o) for o in G.get("objs") or [])
print("TERM0", T[0])
print("OBJ0", (G.get("objs") or [None])[0])
NAMED = [23041, 23405, 23042, 23501, 376, 3052, 3453, 5204, 10404, 24083, 24150, 24357, 24361, 25223, 31258, 31222, 31225,
         10170, 686, 8486, 6384, 2048, 23166, 4866, 31213]
bad = []
W = {}
for r in T:
    if r.get("wire_uid"):
        W.setdefault(int(r["wire_uid"]), []).append(r)
for u in NAMED:
    rows = [r for r in T if int(r["owner_uid"]) == u]
    print("UID {0} owners {1} obj {2} rows {3}".format(u, OWN.get(str(u)), OBJ.get(u), len(rows)))
    if not rows and u not in OBJ and str(u) not in OWN:
        bad.append(u)
    for r in rows:
        peers = [(p["owner_uid"], p["owner_class"], p["term_name"], p["term_uid"], p["frame_diagram"]) for p in W.get(int(r["wire_uid"] or 0), [])
                 if p is not r] if r.get("wire_uid") else []
        print("   t{0} {1!r} {2} {3} src={4} diag={5} wire={6} -> {7}".format(r["term_uid"], r["term_name"], r["term_class"], r["owner_class"],
              r["is_source"], r["frame_diagram"], r["wire_uid"], peers))
# what sits on 1.7's body #23405
on = [r for r in T if int(r["frame_diagram"] or 0) == 23405]
print("BODY 23405 owners", sorted(set((int(r["owner_uid"]), r["owner_class"]) for r in on)))
print("OWNERS ->23405", [k for k, v in OWN.items() if int(v[1]) == 23405][:80])
print("OWNERS ->23041", [(k, v) for k, v in OWN.items() if int(v[1]) == 23041][:80])
print(protocol.result_line(protocol.make_result(1 if not bad else 0, 1 if bad else 0, bad and "uid missing", [])))
