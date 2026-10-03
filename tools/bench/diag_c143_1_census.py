r"""diag_c143_1_census - card 143-1 (PD332(c), PD264(c)/PD325(c) precedent): write the P4 v18 session-2 scratch's MEASURED new-object
census into plan_ring_p4_s02v18_pred.json `census` (was derived {} = all 34 actions census-unpredicted). No number is typed: the
census is parsed from the ONE 'CENSUS-ALL new uids by class (every class) {...}' line of tools/bench/diag_c143_1_scratch.log (cited
by line number) and must equal the run summary's census_all.new_by_class (diag_c143_1_scratch_sum.json).
COPIED from tools/bench/prep_c141_3_census.py (card 141-3) with names changed and C1 = the scratch RESULT has fail 0 (no exception).
Only `census`, `census_overall`, `census_source` change; the plan file and every other pred key are untouched. Touches no LabVIEW.
PREDICTION: C0-C4 PASS.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c143_1_census.log -- py -u tools/bench/diag_c143_1_census.py"""
import hashlib, json, os, sys                                                         # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol                                                                       # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
LOG = os.path.join(B, "diag_c143_1_scratch.log")
SJ = os.path.join(B, "diag_c143_1_scratch_sum.json")
PRED = os.path.join(B, "plan_ring_p4_s02v18_pred.json")
PLAN = os.path.join(B, "plan_ring_p4_s02v18.json")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                         # noqa: E731
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:600]), flush=True)


gate("C0 inputs md5 == card (pred 518b01b8, plan e941ebbf)", md5(PRED) == "518b01b8e4ec7046af7bb8ed781e62c6" and md5(PLAN) == "e941ebbfaa3d98099bcd10d8c6237ef4",
     (md5(PRED), md5(PLAN)))
lines = open(LOG, encoding="utf-8", errors="replace").read().splitlines()
res = [ln for ln in lines if ln.startswith("RESULT ")]
rj = json.loads(res[-1][7:]) if res else {}
gate("C1 the scratch RESULT has fail 0 and no first_fail", rj.get("gates", {}).get("fail") == 0 and not rj.get("first_fail"), (rj.get("gates"), rj.get("first_fail")))
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
        p["census_source"] = {"card": "143-1", "decided": "PD332(c) / PD264(c): the scratch census becomes the launch prediction",
                              "log": os.path.relpath(LOG, ROOT).replace("\\", "/"), "line": ln_no, "expect": KEY.strip(), "log_md5": md5(LOG),
                              "what": "stagekit.census_gate counts NEW uids per class (after - before); re-used uids are not new",
                              "previous": old}
        json.dump(p, open(PRED, "w", encoding="utf-8"), indent=1)
        chk = json.load(open(PRED, encoding="utf-8"))
        gate("C4 pred census written == measured; plan md5 key unchanged", chk["census"] == meas and chk["plan"]["md5"] == md5(PLAN), md5(PRED))
        print("  FACT measured new-by-class {0} (log line {1})".format(json.dumps(meas, sort_keys=True), ln_no), flush=True)
n = sum(1 for _l, ok in gates if ok)
ff = next((lab for lab, ok in gates if not ok), None)
arts = [{"path": os.path.relpath(PRED, ROOT), "md5": md5(PRED)}] if ff is None else []
print(protocol.result_line(protocol.make_result(n, len(gates) - n, ff, arts)), flush=True)
sys.exit(0 if ff is None else 1)
