r"""diag_c129_2_census - card 129-2 step 5 (PD264(c)): write the scratch run's MEASURED new-object census into plan_ring_p3b1_pred.json
`census` and record the run in census_samples.json `runs`. No number is typed: the census is parsed from the ONE
'CENSUS-ALL new uids by class (every class) {...}' line of tools/bench/stage_d1_ring_p3b1_scratch_pin.log (cited by line number) and
must equal the stage JSON's census_all.new_by_class. Refuses unless that log ended BGRUN END rc=0 with a PASS RESULT line.
The recipe's CEN2 (stagekit.census_gate) counts NEW uids per class, which is what this line measured (lost uids are not counted).
census_predict keeps the rows CENSUS-UNPREDICTED (no per-op sample exists), so X15 stays advisory; the launch's CEN2 compares
against this measured whole-stage census. Touches no LabVIEW.
PREDICTION: gates C1-C5 PASS; pred census == the measured dict; census_samples runs +1 (idempotent by log path).
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c129_2_census.log -- py -u tools/bench/diag_c129_2_census.py"""
import hashlib, json, os, re, sys                                                     # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol                                                                       # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
LOG = os.path.join(B, "stage_d1_ring_p3b1_scratch_pin.log")
SJ = os.path.join(B, "stage_d1_ring_p3b1_scratch_pin.json")
PRED = os.path.join(B, "plan_ring_p3b1_pred.json")
SAMP = os.path.join(B, "census_samples.json")
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
    gate("C3 the log line == stage JSON census_all.new_by_class", meas == (sj.get("census_all") or {}).get("new_by_class"), (meas, sj.get("census_all")))
    net = re.search(r"CENSUS-ALL net delta \(every class\) (\{.*\})", "\n".join(lines))
    print("  FACT measured new-by-class {0} (log line {1}); net delta {2}".format(json.dumps(meas, sort_keys=True), ln_no, net.group(1) if net else None), flush=True)
    if all(ok for _l, ok in gates):
        p = json.load(open(PRED, encoding="utf-8"))
        old = p.get("census")
        p["census"] = dict(sorted(meas.items()))
        p["census_overall"] = "MEASURED-SCRATCH"
        p["census_source"] = {"card": "129-2", "decided": "PD264(c): the scratch census becomes the launch prediction",
                              "log": os.path.relpath(LOG, ROOT).replace("\\", "/"), "line": ln_no, "expect": KEY.strip(), "log_md5": md5(LOG),
                              "what": "stagekit.census_gate counts NEW uids per class (after - before); the scratch measured it on every class",
                              "previous": old}
        json.dump(p, open(PRED, "w", encoding="utf-8"), indent=1)
        gate("C4 pred census written == measured", json.load(open(PRED, encoding="utf-8"))["census"] == meas, md5(PRED))
        rel = os.path.relpath(LOG, ROOT).replace("\\", "/")
        txt = open(SAMP, encoding="utf-8", newline="").read()                       # text insert: keeps every existing line (and its number)
        nl = "\r\n" if "\r\n" in txt else "\n"
        mk = nl + ' ],' + nl + ' "ops": {'
        gate("C5a census_samples has ONE runs/ops boundary to insert at", txt.count(mk) == 1, txt.count(mk))
        if rel not in [r.get("log") for r in json.loads(txt)["runs"]] and txt.count(mk) == 1:
            ent = {"log": rel, "md5": md5(LOG),
                   "what": "card 129-2 scratch of the RING P3b-1 recipe (40 rows) on a P3a byte copy; whole-stage new-object census, all 40 rows "
                           "CENSUS-UNPREDICTED per op (no per-op split measured)",
                   "census_new_by_class": dict(sorted(meas.items())), "cite": {"file": rel, "line": ln_no, "expect": KEY.strip()}}
            txt = txt.replace(mk, "," + nl + "  " + json.dumps(ent, ensure_ascii=False) + mk)
            json.loads(txt)
            open(SAMP, "w", encoding="utf-8", newline="").write(txt)
        gate("C5 census_samples runs carries this log once", sum(1 for r in json.load(open(SAMP, encoding="utf-8"))["runs"] if r.get("log") == rel) == 1, md5(SAMP))
n = sum(1 for _l, ok in gates if ok)
ff = next((lab for lab, ok in gates if not ok), None)
arts = [{"path": os.path.relpath(x, ROOT), "md5": md5(x)} for x in (PRED, SAMP)] if ff is None else []
print(protocol.result_line(protocol.make_result(n, len(gates) - n, ff, arts)), flush=True)
sys.exit(0 if ff is None else 1)
