# ---
# labview: none
# hardware: none
# offline-args: before
# evidence: tools/bench/cards/brief_152-a2-1.md
# ---
"""Card 152-a2-1 identity check (OFFLINE, no LabVIEW, no COM): stagesim.fs_measured_state(graph) and stagesim.base_state(graph)
for the two graphs WITHOUT the fs_owner_read key - graph_ring_p4s08_20261009_033522.json (44858dbf) and
graph_ring_p4s07_20261008_224835.json (71935a84) - serialised (json, sort_keys, default=repr).
argv[1] = 'before' -> writes tools/bench/diag_c152_a2_1_ident_before.json; 'after' -> recomputes and compares byte for byte.
EXISTING checked first: selftest_c134_4_owners.py / selftest_c134_1_fsmap.py call the same two functions; no saved dump exists.
PREDICTION: before = 4 dumps written (2 graphs x 2 functions), fs_unmeasured of 44858dbf = [2499, 14682, 29721, 43914];
after = all 4 dumps identical to the before file.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c152_a2_1_ident_<mode>.log -- py -u tools/bench/diag_c152_a2_1_ident.py <mode>"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagesim as SS                                                                         # noqa: E402
import protocol as P                                                                          # noqa: E402

MODE = sys.argv[1] if len(sys.argv) > 1 else "before"
OUT = os.path.join(HERE, "diag_c152_a2_1_ident_before.json")
GRAPHS = ["graph_ring_p4s08_20261009_033522.json", "graph_ring_p4s07_20261008_224835.json"]
cur = {}
for g in GRAPHS:
    G = json.load(open(os.path.join(HERE, g), encoding="utf-8"))
    print("  FACT  {0} has fs_owner_read: {1}; has fs_measured: {2}".format(g, "fs_owner_read" in G, "fs_measured" in G), flush=True)
    m = json.dumps(SS.fs_measured_state(G), sort_keys=True, default=repr)
    b = json.dumps(SS.base_state(G), sort_keys=True, default=repr)
    cur[g + "|fs_measured_state"] = m
    cur[g + "|base_state"] = b
    st = SS.base_state(G)
    print("  FACT  {0} fs_unmeasured {1}".format(g, st.get("fs_unmeasured")), flush=True)
    for k in ("fs_measured_state", "base_state"):
        print("  FACT  {0}|{1} md5 {2} len {3}".format(g, k, hashlib.md5(cur[g + "|" + k].encode()).hexdigest(),
                                                      len(cur[g + "|" + k])), flush=True)
res = []
if MODE == "before":
    json.dump(cur, open(OUT, "w", encoding="utf-8"))
    ok = len(cur) == 4
    res.append(ok)
    print("  {0}  4 dumps written to {1}".format("PASS" if ok else "FAIL", os.path.basename(OUT)), flush=True)
else:
    old = json.load(open(OUT, encoding="utf-8"))
    for k in sorted(cur):
        ok = old.get(k) == cur[k]
        res.append(ok)
        print("  {0}  identical {1}".format("PASS" if ok else "FAIL", k), flush=True)
nf = res.count(False)
print(P.result_line(P.make_result(res.count(True), nf, None if not nf else "diag_c152_a2_1_ident")), flush=True)
sys.exit(1 if nf else 0)
