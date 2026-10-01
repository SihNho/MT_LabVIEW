r"""diag_c124_p3a_termclass - card 124-8 (offline, no LabVIEW): list the MEASURED term_class of the terminals that the P3a plan's
created nodes declare, from LabVIEW-read graphs (the P2b bed graph's $work donors, constant rows) and from plans that already
declared a term_class. Read-only. PREDICTION: donors #10019/#1978/#2136 rows are ParameterTerminal; DigitalNumericConstant rows
carry one class.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c124_p3a_termclass.log -- py -u tools/bench/diag_c124_p3a_termclass.py"""
import collections, glob, json, os, sys  # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import protocol as P  # noqa: E402
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
GF = "tools/bench/graph_ring_p2b_20261001_154542.json"
g = json.load(open(GF, encoding="utf-8"))
rows = g["terminals"]
for u in (10019, 1978, 2136):
    print("DONOR", u, [(r["term_name"], r["is_source"], r["owner_class"], r["term_class"]) for r in rows if r["owner_uid"] == u], flush=True)
print("CONSTANTS", dict(collections.Counter((r["owner_class"], r["term_class"]) for r in rows if "Constant" in r["owner_class"])))
print("PRIMS", dict(collections.Counter((r["owner_class"], r["term_class"]) for r in rows
                                       if r["owner_class"] in ("Function", "Comparison", "IndexArray"))))
n = 0
for f in sorted(glob.glob("tools/bench/plan_*.json")):
    try:
        p = json.load(open(f, encoding="utf-8"))
    except Exception:
        continue
    for a in (p.get("actions") or []) if isinstance(p, dict) else []:
        for t in a.get("terminals") or []:
            if t.get("term_class"):
                n += 1
                print("DECL", f, a.get("id"), a.get("class"), a.get("prim"), repr(t.get("name")), t["term_class"])
print(P.result_line(P.make_result(1, 0, None)), flush=True)
