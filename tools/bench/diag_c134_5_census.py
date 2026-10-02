r"""diag_c134_5_census - card 134-5 step 4 (PD264(c), PD290(d)): write the scratch-b run's MEASURED new-object census into
plan_ring_p3b2b_pred.json `census`. No number is typed: the census is parsed from the ONE 'CENSUS-ALL new uids by class (every class)
{...}' line of tools/bench/stage_d1_ring_p3b2b_scratch_c134_5.log (cited by line number) and must equal the run summary's
census_all.new_by_class (stage_d1_ring_p3b2b_scratch_sum.json). plan_ring_p3b2a_pred.json is NOT written here: session a's scratch log
(stage_d1_ring_p3b2a_scratch_c133_6.log) carries no CENSUS-ALL line (its CEN2 at :354 measured {} over an empty class set), so there is
no measured census of a to cite - reported, not invented.
PRIOR ART: tools/bench/diag_c131_4_census.py (card 131-4; gates C1-C4 cut; no memory_pred change, no census_samples write).
Touches no LabVIEW.
PREDICTION: gates C1-C4 PASS; pred census == the measured dict; census_overall MEASURED-SCRATCH.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c134_5_census.log -- py -u tools/bench/diag_c134_5_census.py"""
import hashlib, json, os, sys                                                         # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol                                                                       # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
LOG = os.path.join(B, "stage_d1_ring_p3b2b_scratch_c134_5.log")
SJ = os.path.join(B, "stage_d1_ring_p3b2b_scratch_sum.json")
PRED = os.path.join(B, "plan_ring_p3b2b_pred.json")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                         # noqa: E731
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:600]), flush=True)


lines = open(LOG, encoding="utf-8", errors="replace").read().splitlines()
end = [ln for ln in lines if ln.startswith("BGRUN END")]
res = [ln for ln in lines if ln.startswith("RESULT ")]
gate("C1 scratch log ended BGRUN END rc=0 and its RESULT line is PASS", end and "rc=0" in end[-1] and res and json.loads(res[-1][7:]).get("status") == "PASS",
     (end[-1:], res[-1:]))
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
        old = p.get("census")
        p["census"] = dict(sorted(meas.items()))
        p["census_overall"] = "MEASURED-SCRATCH"
        p["census_source"] = {"card": "134-5", "decided": "PD264(c) / PD290(d): the scratch census becomes the launch prediction",
                              "log": os.path.relpath(LOG, ROOT).replace("\\", "/"), "line": ln_no, "expect": KEY.strip(), "log_md5": md5(LOG),
                              "what": "stagekit.census_gate counts NEW uids per class (after - before); the scratch measured it on every class",
                              "previous": old}
        json.dump(p, open(PRED, "w", encoding="utf-8"), indent=1)
        chk = json.load(open(PRED, encoding="utf-8"))
        gate("C4 pred census written == measured", chk["census"] == meas, md5(PRED))
        print("  FACT measured new-by-class {0} (log line {1})".format(json.dumps(meas, sort_keys=True), ln_no), flush=True)
n = sum(1 for _l, ok in gates if ok)
ff = next((lab for lab, ok in gates if not ok), None)
arts = [{"path": os.path.relpath(PRED, ROOT), "md5": md5(PRED)}] if ff is None else []
print(protocol.result_line(protocol.make_result(n, len(gates) - n, ff, arts)), flush=True)
sys.exit(0 if ff is None else 1)
