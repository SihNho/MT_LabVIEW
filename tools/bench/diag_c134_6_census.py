r"""diag_c134_6_census - card 134-6 step 1 (PD291(b)): session a's census = the per-class difference of the object rows of the two
REAL graph reads by the same reader family (read_live objs):
  BEFORE tools/bench/graph_ring_p3b1_20261002_073225.json   (bed P3b-1, 9d7bf287)
  AFTER  tools/bench/graph_ring_p3b2a_fs_20261002_102553.json (the in-between file of session a, 6cc69221)
Two measures are computed and both written: `new_by_class` (uids in AFTER not in BEFORE, by class = the semantics of
stagekit.census_gate, stagekit.py:289-292, which the launch's CEN2 compares) and `count_diff_by_class` (row count after - before,
by class; PD291(b)'s wording). The pred `census` gets new_by_class; `census_source` cites both files + md5 and keeps the other.
PRIOR ART: diag_c134_5_census.py (same pred write shape, census_overall / census_source). Touches no LabVIEW.
PREDICTION: C1 both inputs at their card md5; C2 new_by_class non-empty; C3 removed-uid set reported (FACT, either value);
C4 pred census written == new_by_class.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c134_6_census.log -- py -u tools/bench/diag_c134_6_census.py"""
import collections, hashlib, json, os, sys                                             # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol                                                                       # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
G0 = ("tools/bench/graph_ring_p3b1_20261002_073225.json", "6cfa6ecb25d9bd98fe31a6cb703679cb")
G1 = ("tools/bench/graph_ring_p3b2a_fs_20261002_102553.json", "b885fa4af1df203a8dd68b631ab86752")
PRED = os.path.join(B, "plan_ring_p3b2a_pred.json")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                         # noqa: E731
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:900]), flush=True)


gate("C1 inputs at card md5", all(md5(os.path.join(ROOT, p)) == m for p, m in (G0, G1)), [md5(os.path.join(ROOT, p)) for p, _m in (G0, G1)])
a0, a1 = (dict((int(o["uid"]), str(o["class"])) for o in json.load(open(os.path.join(ROOT, p), encoding="utf-8"))["objs"]) for p, _m in (G0, G1))
new = collections.Counter(a1[u] for u in set(a1) - set(a0))
gone = collections.Counter(a0[u] for u in set(a0) - set(a1))
recl = sorted((u, a0[u], a1[u]) for u in set(a0) & set(a1) if a0[u] != a1[u])
c0, c1 = collections.Counter(a0.values()), collections.Counter(a1.values())
cdiff = dict((c, c1[c] - c0[c]) for c in sorted(set(c0) | set(c1)) if c1[c] != c0[c])
print("  FACT rows before {0} after {1}; new uids {2}, removed uids {3}, uid reclassed {4}".format(
    len(a0), len(a1), sum(new.values()), sum(gone.values()), len(recl)), flush=True)
print("  FACT new_by_class {0}".format(json.dumps(dict(sorted(new.items())))), flush=True)
print("  FACT removed_by_class {0}".format(json.dumps(dict(sorted(gone.items())))), flush=True)
print("  FACT count_diff_by_class {0}".format(json.dumps(cdiff)), flush=True)
print("  FACT reclassed {0}".format(recl[:10]), flush=True)
gate("C2 new_by_class non-empty", bool(new), dict(new))
gate("C3 no uid changed class between the reads", not recl, recl[:10])
if all(ok for _l, ok in gates):
    p = json.load(open(PRED, encoding="utf-8"))
    old = [p.get("census"), p.get("census_overall")]
    p["census"] = dict(sorted(new.items()))
    p["census_overall"] = "MEASURED-GRAPH-DIFF"
    p["census_source"] = {"card": "134-6", "decided": "PD291(b): a's census = difference of the two REAL graph reads",
                          "before": {"path": G0[0], "md5": G0[1]}, "after": {"path": G1[0], "md5": G1[1]},
                          "script": "tools/bench/diag_c134_6_census.py",
                          "what": "new uids (after - before) by class over the graphs' objs rows = stagekit.census_gate semantics",
                          "count_diff_by_class": cdiff, "removed_by_class": dict(sorted(gone.items())), "previous": old}
    json.dump(p, open(PRED, "w", encoding="utf-8"), indent=1)
    gate("C4 pred census written == new_by_class", json.load(open(PRED, encoding="utf-8"))["census"] == dict(new), md5(PRED))
n = sum(1 for _l, ok in gates if ok)
ff = next((lab for lab, ok in gates if not ok), None)
arts = [{"path": os.path.relpath(PRED, ROOT), "md5": md5(PRED)}] if ff is None else []
print(protocol.result_line(protocol.make_result(n, len(gates) - n, ff, arts)), flush=True)
sys.exit(0 if ff is None else 1)
