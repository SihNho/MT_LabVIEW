r"""prep_c141_3_census - card 141-3 pass item 3 (PD325(c), PD264(c) precedent): write the 141-2 scratch's MEASURED new-object census
into plan_ring_p4_s01_pred.json `census`, so CEN2 is predicted at the rerun and the launch. No number is typed: the census is parsed
from the ONE 'CENSUS-ALL new uids by class (every class) {...}' line of tools/bench/diag_c141_p4s01_scratch.log (cited by line number)
and must equal the run summary's census_all.new_by_class (diag_c141_p4s01_scratch_sum.json).
COPIED from tools/bench/diag_c134_5_census.py (card 134-5) with ONE change: C1 accepts the 141-2 log's FAIL because its only failing
gate is TD (the raw-uid key, PD325(a)), which does not touch the census; anything else fails C1.
Only `census`, `census_overall`, `census_source` change; the plan file and every other pred key are untouched. Touches no LabVIEW.
PREDICTION: C1-C4 PASS; pred census == {"GrowableFunction": 3, "Terminal": 9, "Wire": 2} (log :278).
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c141_3_census.log -- py -u tools/bench/prep_c141_3_census.py"""
import hashlib, json, os, sys                                                         # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol                                                                       # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
LOG = os.path.join(B, "diag_c141_p4s01_scratch.log")
SJ = os.path.join(B, "diag_c141_p4s01_scratch_sum.json")
PRED = os.path.join(B, "plan_ring_p4_s01_pred.json")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                         # noqa: E731
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:600]), flush=True)


gate("C0 inputs md5 == card (log 17c5caf6, pred fc87180a)", md5(LOG) == "17c5caf6fc8c1dece1a099a51e444e8e" and md5(PRED) == "fc87180a2fc31d5ae920f817591ee5f8",
     (md5(LOG), md5(PRED)))
lines = open(LOG, encoding="utf-8", errors="replace").read().splitlines()
res = [ln for ln in lines if ln.startswith("RESULT ")]
rj = json.loads(res[-1][7:]) if res else {}
gate("C1 the 141-2 RESULT fails ONLY on gate TD (fail 1, first_fail TD)", rj.get("gates", {}).get("fail") == 1 and str(rj.get("first_fail", "")).startswith("TD "),
     (rj.get("gates"), rj.get("first_fail")))
KEY = "CENSUS-ALL new uids by class (every class) "
hit = [(i + 1, ln) for i, ln in enumerate(lines) if KEY in ln]
gate("C2 exactly one '{0}' line in the log".format(KEY.strip()), len(hit) == 1, [h[0] for h in hit])
if all(ok for _l, ok in gates):
    ln_no, ln = hit[0]
    meas = json.loads(ln.split(KEY, 1)[1])
    sj = json.load(open(SJ, encoding="utf-8"))
    gate("C3 the log line == run summary census_all.new_by_class", meas == (sj.get("census_all") or {}).get("new_by_class"), (meas, sj.get("census_all")))
    if all(ok for _l, ok in gates):
        p = json.load(open(PRED, encoding="utf-8"))
        old = {"census": p.get("census"), "census_overall": p.get("census_overall")}
        p["census"] = dict(sorted(meas.items()))
        p["census_overall"] = "MEASURED-SCRATCH"
        p["census_source"] = {"card": "141-3", "decided": "PD325(c) / PD264(c): the scratch census becomes the launch prediction",
                              "log": os.path.relpath(LOG, ROOT).replace("\\", "/"), "line": ln_no, "expect": KEY.strip(), "log_md5": md5(LOG),
                              "what": "stagekit.census_gate counts NEW uids per class (after - before); re-used uids (28004, 28979, 28296) are not new",
                              "previous": old}
        json.dump(p, open(PRED, "w", encoding="utf-8"), indent=1)
        chk = json.load(open(PRED, encoding="utf-8"))
        gate("C4 pred census written == measured; plan md5 key unchanged", chk["census"] == meas and chk["plan"]["md5"] == "f4831031c738c997391b5bcace19d9f0", md5(PRED))
        print("  FACT measured new-by-class {0} (log line {1})".format(json.dumps(meas, sort_keys=True), ln_no), flush=True)
n = sum(1 for _l, ok in gates if ok)
ff = next((lab for lab, ok in gates if not ok), None)
arts = [{"path": os.path.relpath(PRED, ROOT), "md5": md5(PRED)}] if ff is None else []
print(protocol.result_line(protocol.make_result(n, len(gates) - n, ff, arts)), flush=True)
sys.exit(0 if ff is None else 1)
