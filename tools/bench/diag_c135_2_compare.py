r"""diag_c135_2_compare - card 135-2 pass 3 (PD294(b)): OFFLINE compare of the launch's in-between graph
graph_ring_p3b2a_fs_20261002_123012.json (d0a32178, read of the a-file 49cf7f77) with the reference read
graph_ring_p3b2a_fs_20261002_102553.json (b885fa4a), both re-annotated (launch_p3b2_resume_c135_compare.compare).
PREDICTION: K1 both md5 as pinned; K2 EQUAL (diff {}); re-annotation changes: new 0, ref 7 (status added on the nested-FS
borders 14430 31050 34409 34489 43605 44160 44164, result_135-1.json). Writes tools/bench/diag_c135_2_compare.json.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c135_2_compare.log -- py -u tools/bench/diag_c135_2_compare.py"""
import hashlib, json, os, sys                                                      # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(B))
sys.path.insert(0, B)
import protocol as P                                                               # noqa: E402
import launch_p3b2_resume_c135_compare as CMP                                      # noqa: E402
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                      # noqa: E731
NEW, REF = (os.path.join(B, n) for n in ("graph_ring_p3b2a_fs_20261002_123012.json", "graph_ring_p3b2a_fs_20261002_102553.json"))
PIN = {NEW: "d0a32178a87b2c9593b0d0773d332215", REF: "b885fa4af1df203a8dd68b631ab86752"}
ok = []


def gate(n, c, d=""):
    ok.append((n, bool(c)))
    print("  {0}  {1}  {2}".format("PASS" if c else "FAIL", n, json.dumps(d, default=str)[:900]), flush=True)


gate("K1 graphs md5 as pinned", all(md5(p) == m for p, m in PIN.items()), dict((os.path.basename(p), md5(p)) for p in PIN))
eq, diff, ch = CMP.compare(json.load(open(NEW, encoding="utf-8")), json.load(open(REF, encoding="utf-8")))
out = os.path.join(B, "diag_c135_2_compare.json")
json.dump({"new": {"path": "tools/bench/" + os.path.basename(NEW), "md5": PIN[NEW]}, "ref": {"path": "tools/bench/" + os.path.basename(REF),
          "md5": PIN[REF]}, "result": "EQUAL" if eq else "DIFFERENT", "diff": diff, "reannotation_changes": ch}, open(out, "w", encoding="utf-8"), indent=1)
print("  FACT  re-annotation changes: new {0}, ref {1}: {2}".format(ch["n_new"], ch["n_ref"], json.dumps(ch["ref"])[:600]), flush=True)
gate("K2 compare 123012 vs re-annotated 102553: {0}".format("EQUAL" if eq else "DIFFERENT"), eq, diff)
np_, nf = sum(1 for _n, c in ok if c), sum(1 for _n, c in ok if not c)
print(P.result_line(P.make_result(np_, nf, next((n for n, c in ok if not c), None), [{"path": "tools/bench/diag_c135_2_compare.json", "md5": md5(out)}])), flush=True)
sys.exit(1 if nf else 0)
