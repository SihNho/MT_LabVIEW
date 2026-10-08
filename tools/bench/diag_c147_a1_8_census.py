# ---
# labview: none
# hardware: none
# ---
r"""diag_c147_a1_8_census - card 147-a1-8 (PD352, PD264(c)): write the P4 v18 session-6 RETRY scratch's MEASURED new-object census into
plan_ring_p4_s06v18_pred.json `census`. COPIED from tools/bench/diag_c147_a1_4_census.py (written by card 147-a1-4, unrun) with ONE change:
tools/bench/diag_c147_p4s06v18_scratch.log is APPENDED by bgrun and also holds card 147-a1-4's stopped run, so every line search is restricted
to the LAST segment (from the last 'BGRUN START' line); line numbers cited are whole-file line numbers.
No number is typed: the census is parsed from the ONE 'CENSUS-ALL new uids by class (every class) {...}' line of the last segment and must equal
the run summary's census_all.new_by_class (diag_c147_p4s06v18_scratch_sum.json). Only `census`, `census_overall`, `census_source` change.
PREDICTION: C0-C4 PASS.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c147_a1_8_census.log -- py -u tools/bench/diag_c147_a1_8_census.py"""
import hashlib, json, os, sys                                                         # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol                                                                       # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
LOG = os.path.join(B, "diag_c147_p4s06v18_scratch.log")
SJ = os.path.join(B, "diag_c147_p4s06v18_scratch_sum.json")
PRED = os.path.join(B, "plan_ring_p4_s06v18_pred.json")
PLAN = os.path.join(B, "plan_ring_p4_s06v18.json")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                         # noqa: E731
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:600]), flush=True)


gate("C0 inputs md5 == card (pred c4a6a35a, plan cfbd9823)", md5(PRED) == "c4a6a35aff6f71d508ea2c43c24ec510" and md5(PLAN) == "cfbd9823d3b47be39de94f2125ad6b66",
     (md5(PRED), md5(PLAN)))
alll = open(LOG, encoding="utf-8", errors="replace").read().splitlines()
seg0 = max(i for i, ln in enumerate(alll) if ln.startswith("BGRUN START"))
lines = [(i + 1, ln) for i, ln in enumerate(alll) if i >= seg0]
print("  FACT last segment starts at log line {0}".format(seg0 + 1), flush=True)
res = [ln for _n, ln in lines if ln.startswith("RESULT ")]
rj = json.loads(res[-1][7:]) if res else {}
gate("C1 the scratch RESULT has fail 0 and no first_fail", rj.get("gates", {}).get("fail") == 0 and not rj.get("first_fail"), (rj.get("gates"), rj.get("first_fail")))
KEY = "CENSUS-ALL new uids by class (every class) "
hit = [(n, ln) for n, ln in lines if KEY in ln]
gate("C2 exactly one '{0}' line in the last segment".format(KEY.strip()), len(hit) == 1, [h[0] for h in hit])
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
        p["census_source"] = {"card": "147-a1-8", "decided": "PD352 / PD264(c): the scratch census becomes the launch prediction",
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
