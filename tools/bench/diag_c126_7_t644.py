r"""diag_c126_7_t644 - card 126-7 (OFFLINE, read-only, no LabVIEW): the facts behind 126-5's M1 FAIL (t644 two rows) and the
graph facts owed by PD255(e)(f), read from files only.
PREDICTION: t644 appears as 2 terminal rows that are byte-identical (a vigraph duplicate), every other bound uid once.
    py -u tools/bench/diag_c126_7_t644.py"""
import collections, json, os, sys    # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
GR = os.path.join(B, "graph_ring_p3a_20261001_190155.json")
G = json.load(open(GR, encoding="utf-8"))
T = G["terminals"]
print("keys", list(G.keys()))
rows644 = [r for r in T if r["term_uid"] == 644]
for r in rows644:
    print("T644", json.dumps(r, sort_keys=True))
c = collections.Counter(json.dumps(r, sort_keys=True) for r in T)
d = [k for k, v in c.items() if v > 1]
print("DUP identical rows:", len(d), "of", len(T))
for k in d[:20]:
    print("  DUP x{0} {1}".format(c[k], k[:300]))
cu = collections.Counter(r["term_uid"] for r in T)
print("term_uids with >1 rows:", sum(1 for v in cu.values() if v > 1))
print("objs 637/639:", [o for o in G["objs"] if int(o["uid"]) in (637, 639)])
