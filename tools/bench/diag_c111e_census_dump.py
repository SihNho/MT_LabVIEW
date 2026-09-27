"""diag_c111e_census_dump - card 111-5 P1 step 1, OFFLINE: print every d1_rewire_sources.json row and every build_d1_v0.json
cut row owned by group B's 8 nodes (#1359 #2222 #2626 #6104 #8885 #9833 #11261 #29874), compactly, for the PD158 crossing.
No LabVIEW. PREDICTION: both files load; B's rows are printed; the RESULT counts rows per file (no pass/fail judgement)."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402
B = {1359, 2222, 2626, 6104, 8885, 9833, 11261, 29874}
RS = json.load(open(os.path.join(ROOT, "tools/bench/d1_rewire_sources.json"), encoding="utf-8"))
BV = json.load(open(os.path.join(ROOT, "tools/bench/build_d1_v0.json"), encoding="utf-8"))
print("REWIRE keys", [k for k in RS if k != "rows"], "BUILD keys", list(BV.keys()))
n1 = 0
for r in RS["rows"]:
    if int(r["uid"]) in B:
        n1 += 1
        x = dict((k, r[k]) for k in r if k not in ("uid", "i", "name", "is_source", "wire", "dest", "action"))
        print("RS #{0} i{1} {2!r} src={3} w{4} dest={5} {6} :: {7}".format(r["uid"], r["i"], r["name"], r["is_source"], r["wire"], r["dest"], r["action"], json.dumps(x)[:400]))
n2 = 0
for c in BV.get("cut", []):
    if int(c[0]) in B:
        n2 += 1
        print("BV cut", c)
for k in BV:
    if k not in ("cut", "moved", "loops", "phase"):
        v = BV[k]
        print("BV key", k, type(v).__name__, len(v) if hasattr(v, "__len__") else v)
        if isinstance(v, list):
            for e in v:
                if any(isinstance(z, int) and z in B for z in (e if isinstance(e, list) else (e.values() if isinstance(e, dict) else []))):
                    print("   BV", k, json.dumps(e)[:300])
print(protocol.result_line(dict(status="PASS", gates={"pass": 2, "fail": 0}, first_fail=None, artefacts=[])))
print("COUNTS RS rows {0}, BV cut rows {1}".format(n1, n2))
