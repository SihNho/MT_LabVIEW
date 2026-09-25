"""k_selfwire_79 - card 79-5 R5, Pre-decided 178(f) side check (read-only, offline, no LabVIEW).
Question: the review archive/peer/2026-09-25-c79-k-x4.md:68-76 flags FSITs #6239/#3862/#5659 whose own source terminal
and own sink terminal share one wire on diagram 536 in the S4 bed graph. Are the same self-wires present in S1?
Inputs: bed tools/bench/graph_k_s4_20260925.json (raw terminal rows); S1 docs/wiki/subvi/D1_s1_copy.json (raw terminal rows).
PREDICTION CONTRACT: none on the answer (either is a legitimate finding); gates only check the inputs were read:
G1 both files load with terminal rows; G2 each of the three FSITs has rows in both graphs.
Prior art: the rows are the same shape vigraph/stage_prerun read (term_uid, owner_uid, wire_uid, is_source, frame_diagram).
"""
import json, os, sys                                                               # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol                                                                    # noqa: E402
SRC = {"bed": os.path.join(HERE, "graph_k_s4_20260925.json"), "s1": os.path.join(ROOT, "docs", "wiki", "subvi", "D1_s1_copy.json")}
FSIT = [6239, 3862, 5659]
G = []


def gate(l, ok, d=""):
    G.append((l, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", l, d), flush=True)


T = {}
for k, p in SRC.items():
    T[k] = json.load(open(p, encoding="utf-8")).get("terminals") or []
gate("G1 both graphs have terminal rows", all(T.values()), dict((k, len(v)) for k, v in T.items()))
for k, rows in T.items():
    byw = {}
    for r in rows:
        if r.get("wire_uid"):
            byw.setdefault(int(r["wire_uid"]), []).append(r)
    for u in FSIT:
        mine = [r for r in rows if int(r.get("owner_uid") or 0) == u]
        for r in mine:
            print("ROW {0} #{1} term {2} src {3} wire {4} diag {5} name {6!r}".format(k, u, r["term_uid"], r["is_source"],
                  r.get("wire_uid"), r.get("frame_diagram"), r.get("term_name")), flush=True)
        self_w = sorted(set(int(r["wire_uid"]) for r in mine if r.get("wire_uid") and
                            len(set((int(x["term_uid"]), bool(x["is_source"])) for x in byw.get(int(r["wire_uid"]), [])
                                    if int(x.get("owner_uid") or 0) == u)) >= 2 and
                            {bool(x["is_source"]) for x in byw[int(r["wire_uid"])] if int(x.get("owner_uid") or 0) == u} == {True, False}))
        print("SELFWIRE {0} #{1}: {2}".format(k, u, [(w, [(x["term_uid"], x["is_source"], x.get("frame_diagram"), x.get("owner_uid"))
                                                         for x in byw[w]]) for w in self_w]), flush=True)
        gate("G2 {0} #{1} has terminal rows".format(k, u), mine, len(mine))
n_pass = sum(1 for _l, ok in G if ok); n_fail = len(G) - n_pass
print(protocol.result_line(protocol.make_result(n_pass, n_fail, next((l for l, ok in G if not ok), None))))
sys.exit(0 if not n_fail else 1)
