"""Self-test of card 123-7 STEP 2 (PD247(e), brief_123-5.md STEP 3): the census hook-in. Offline, no LabVIEW.

WHAT EXISTED FIRST: tools/census_predict.py + census_samples.json (card 123-4, selftest_census_predict.py 14/0); stage_prerun's
gates X1-X14 and scratch_requirement (card chat-P3). Added: stage_prerun.census_check / census_gate / census_unpredicted (gate
X15 in --prerun, CENSUS-UNPREDICTED in --scratch-required), census_predict `record` (a scratch run's measured census -> a
sample, cites checked), stagekit Stage.census_snapshot / census_gate (UNVERIFIED-DRY in a dry run), census_predict's
case_wired row (new_wire sample from diag_c123_wired.log:88; branch unsampled).
PREDICTION (12 gates): H01-H04 the prerun gate (c122 fixture FAIL with one CENSUS FAIL line, current pred PASS, P2a/pool
no FAIL + an ADVISORY line); H05-H06 --scratch-required exit 3 + CENSUS-UNPREDICTED for stage_d1_ring_p2a.py; H07-H08 record
(a bad cite refused and nothing written, a good one written); H09-H10 stagekit helper (UNVERIFIED-DRY / real compare);
H11-H12 case_wired rows (new_wire sampled, a second case on the same source = branch = unpredicted).
Usage: py tools/bench/selftest_census_hookin_c123.py"""
import copy
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
os.chdir(ROOT)
import census_predict as CP   # noqa: E402
import protocol   # noqa: E402
import stage_prerun as SP   # noqa: E402

gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, str(detail)[:300]), flush=True)


def load(p):
    return json.load(open(os.path.join(ROOT, p), encoding="utf-8"))


tmp = tempfile.mkdtemp(prefix="census_hookin_")
P2B, P2A, POOL = (os.path.join(ROOT, "tools", "bench", n) for n in ("plan_ring_p2b.json", "plan_ring_p2a.json", "plan_qrt_pool.json"))
fx = copy.deepcopy(load("tools/bench/plan_ring_p2b_pred.json"))
fx["census"]["DigitalNumericConstant"] = 1
fx_p = os.path.join(tmp, "plan_ring_p2b_pred_c122.json")
json.dump(fx, open(fx_p, "w", encoding="utf-8"))
out = []
ok, det, lines = SP.census_gate([P2B], pred_override={P2B: fx_p}, out=out.append)
gate("H01 prerun census gate, cycle-122 fixture (DNC +1): FAIL with ONE line 'CENSUS FAIL <plan> DigitalNumericConstant derived +5 "
     "declared +1'", not ok and [l for l in lines if l.startswith("CENSUS FAIL")] ==
     ["CENSUS FAIL tools/bench/plan_ring_p2b.json DigitalNumericConstant derived +5 declared +1"], lines)
ok, det, lines = SP.census_gate([P2B], out=out.append)
gate("H02 corrected prediction (the current plan_ring_p2b_pred.json) -> PASS", ok and lines[0].startswith("INFO  CENSUS PASS"), lines)
ok, det, lines = SP.census_gate([P2A, POOL], out=out.append)
gate("H03 P2a + pool plans -> no FAIL (gate ok) and an ADVISORY CENSUS-UNPREDICTED line each", ok and len(lines) == 2
     and all(l.startswith("ADVISORY CENSUS-UNPREDICTED") for l in lines), lines)
gate("H04 census_check of a plan with no prediction file -> None (INFO, no gate)",
     SP.census_check(os.path.join(ROOT, "tools", "bench", "diag_c123_wired_plan.json")) is None)
req, why, _st = SP.scratch_requirement(os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p2a.py"))
gate("H05 scratch_requirement(stage_d1_ring_p2a.py) -> required, reason CENSUS-UNPREDICTED", req and why.startswith("CENSUS-UNPREDICTED"), why)
r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "stage_prerun.py"), "--scratch-required",
                    os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p2a.py")], capture_output=True, text=True, cwd=ROOT)
gate("H06 CLI --scratch-required stage_d1_ring_p2a.py exits 3 naming CENSUS-UNPREDICTED", r.returncode == 3 and "CENSUS-UNPREDICTED" in r.stdout,
     (r.returncode, r.stdout[-200:], r.stderr[-200:]))
sp = os.path.join(tmp, "samples.json")
json.dump(load("tools/bench/census_samples.json"), open(sp, "w", encoding="utf-8"))
before = open(sp, encoding="utf-8").read()
try:
    CP.record_sample(sp, "xop", "v", {"Wire": 1}, [{"file": "tools/bench/diag_c123_wired.log", "line": 88, "expect": "NOT ON THAT LINE"}])
    e = "no error"
except ValueError as x:
    e = str(x)
gate("H07 record with a cite that does not hold -> refused, samples file unchanged", "do not hold" in e and open(sp, encoding="utf-8").read() == before, e)
v = CP.record_sample(sp, "xop", "v", {"Wire": 1, "Foo": 2}, [{"file": "tools/bench/diag_c123_wired.log", "line": 88, "expect": "\"Wire\": 1"}])
S2 = json.load(open(sp, encoding="utf-8"))
gate("H08 record with a holding cite -> variant written, its classes added to classes_measured",
     S2["ops"]["xop"]["variants"][0]["delta"] == {"Wire": 1, "Foo": 2} and "Foo" in S2["classes_measured"], v)
import stagekit as K   # noqa: E402
st = object.__new__(K.Stage)
st.passes, st.fails = [], []
old = K.g.report_all
try:
    fake = lambda *a, **k: []   # noqa: E731
    fake._dry = True
    K.g.report_all = fake
    import io
    buf, so = io.StringIO(), sys.stdout
    sys.stdout = buf
    rd = st.census_gate("CEN x", st.census_snapshot("w"), {}, {"Wire": 1})
    sys.stdout = so
finally:
    K.g.report_all = old
gate("H09 stagekit census_gate in a DRY run prints UNVERIFIED-DRY, returns None, records no PASS",
     rd is None and "UNVERIFIED-DRY" in buf.getvalue() and not st.passes and not st.fails, buf.getvalue().strip())
sys.stdout = io.StringIO()          # the helper's own PASS/FAIL lines stay out of this log (a FAIL line would arm guard_peer)
got = st.census_gate("CEN real", {1: "Wire"}, {1: "Wire", 2: "Wire", 3: "CaseStructure"}, {"Wire": 1, "CaseStructure": 1})
bad = st.census_gate("CEN real bad", {1: "Wire"}, {1: "Wire", 2: "Wire"}, {"Wire": 2})
sys.stdout = so
gate("H10 stagekit census_gate real: measured {Wire 1, CaseStructure 1} == declared -> PASS; Wire 1 vs 2 -> FAIL",
     got == {"Wire": 1, "CaseStructure": 1} and st.passes == ["CEN real"] and st.fails == ["CEN real bad"], (got, bad, st.passes, st.fails))
SAM = load("tools/bench/census_samples.json")
PL = {"actions": [{"op": "create", "id": "e1", "class": "Comparison", "prim": "Equal?", "diagram": 639, "as": "E1"},
                  {"op": "create", "id": "c1", "class": "CaseStructure", "diagram": 639, "as": "C1", "selector_as": "S1", "src": "new:E1.x = y?"},
                  {"op": "create", "id": "c2", "class": "CaseStructure", "diagram": 639, "as": "C2", "selector_as": "S2", "src": "new:E1.x = y?"}]}
rep = CP.predict(PL, {"census": {}}, SAM)
rw = dict((r["id"], r) for r in rep["rows"])
gate("H11 case_wired on a fresh source -> SAMPLED variant new_wire with the measured delta (diag_c123_wired.log:88)",
     rw["c1"]["variant"] == "new_wire" and rw["c1"]["delta"] == {"CaseStructure": 1, "Diagram": 2, "Tunnel": 1, "OuterTerminal": 1,
                                                                    "InnerTerminal": 2, "Wire": 1}, rw["c1"])
gate("H12 a second case_wired on the SAME source = branch -> CENSUS-UNPREDICTED (never measured)",
     rw["c2"]["verdict"] == "CENSUS-UNPREDICTED" and "branch" in rw["c2"]["why"], rw["c2"])

bad_ = [l for l, ok_ in gates if not ok_]
print("=== GATES: %d pass / %d fail%s" % (len(gates) - len(bad_), len(bad_), "; failing: " + bad_[0] if bad_ else ""), flush=True)
print(protocol.result_line(protocol.make_result(len(gates) - len(bad_), len(bad_), bad_[0] if bad_ else None, [])), flush=True)
sys.exit(1 if bad_ else 0)
