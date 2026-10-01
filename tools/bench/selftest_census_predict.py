"""selftest_census_predict - offline self-test of tools/census_predict.py + tools/bench/census_samples.json (card 123-4).

No LabVIEW. Fixtures are written to %TEMP% and deleted. PREDICTION (every gate PASS):
  S1 census_samples.json: every cite's file:line exists and carries its `expect` substring; run-log md5s match;
     OpConstInd_v0 has an `array` and a `scalar` variant (and so does const_donor).
  S2 census_predict.py imports none of stagesim / stagekit / stagexec / gscript.
  A  plan_ring_p2b.json + cycle 122's hand-typed prediction (the current pred 98ca9b30... with DigitalNumericConstant set
     back to +1) -> FAIL naming DigitalNumericConstant, derived +5 declared +1, the only failing class; exit 1; RESULT FAIL.
  B  plan_ring_p2b.json + the current pred (98ca9b30...) -> PASS on every class; exit 0; RESULT PASS.
  C  plan_ring_p2a.json + plan_ring_p2a_pred.json, plan_qrt_pool.json + plan_qrt_pool_pred.json -> no class FAIL, overall
     UNPREDICTED with the unsampled rows listed (8 and 15 rows); RESULT SKIP, never PASS.
  D  the P2b plan plus one fabricated row (op create, class Function, prim 'made_up') -> that row CENSUS-UNPREDICTED,
     overall UNPREDICTED, no class PASS; and a const_donor row with an unmeasured canon (Array1D<U8>) -> UNPREDICTED.
    py tools/bench/selftest_census_predict.py
"""
import ast
import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import census_predict as cp  # noqa: E402
import protocol  # noqa: E402

B = os.path.join(ROOT, "tools", "bench")
TOOL = os.path.join(ROOT, "tools", "census_predict.py")
SAMPLES = os.path.join(B, "census_samples.json")
PRED_P2B_MD5 = "98ca9b303451bef5d2e2164b5a98d170"
res = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, info=""):
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, info))
    res["pass" if ok else "fail"] += 1
    if not ok and res["first"] is None:
        res["first"] = label


def md5(p):
    with open(os.path.join(ROOT, p) if not os.path.isabs(p) else p, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def load(p):
    with open(os.path.join(ROOT, p), "r", encoding="utf-8") as f:
        return json.load(f)


def run_tool(plan_p, pred_p):
    r = subprocess.run([sys.executable, "-u", TOOL, plan_p, pred_p], cwd=ROOT, capture_output=True, text=True)
    rl = protocol.parse_result_line(r.stdout)
    return r.returncode, rl, r.stdout


samples = load("tools/bench/census_samples.json")
print("selftest_census_predict  samples md5 %s  tool md5 %s" % (md5(SAMPLES), md5(TOOL)))

# ---- S1 samples are cited and the cites hold
bad, n = [], 0
lines_cache = {}
for opk, op in samples["ops"].items():
    for v in op["variants"]:
        if not v.get("cites"):
            bad.append("%s/%s has no cite" % (opk, v["name"]))
        for c in v.get("cites") or []:
            n += 1
            if c["file"] not in lines_cache:
                with open(os.path.join(ROOT, c["file"]), "r", encoding="utf-8", errors="replace") as f:
                    lines_cache[c["file"]] = f.read().splitlines()
            L = lines_cache[c["file"]]
            if not (1 <= c["line"] <= len(L)) or c["expect"] not in L[c["line"] - 1]:
                bad.append("%s:%d" % (c["file"], c["line"]))
gate("S1a every sample cites log file:line and each cited line carries its expect string", not bad and n > 0,
     "%d cites, bad %s" % (n, bad))
gate("S1b run-log md5s == census_samples.json runs[]",
     all(md5(r["log"]) == r["md5"] for r in samples["runs"]), [r["log"] for r in samples["runs"]])
names = {k: sorted(v["name"] for v in op["variants"]) for k, op in samples["ops"].items()}
gate("S1c OpConstInd_v0 and const_donor each have array + scalar variants",
     names.get("OpConstInd_v0") == ["array", "scalar"] and names.get("create_primitive_nested:const_donor") == ["array", "scalar"],
     names)

# ---- S2 standalone
with open(TOOL, "r", encoding="utf-8") as f:
    tree = ast.parse(f.read())
imps = set()
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        imps |= {a.name.split(".")[0] for a in node.names}
    elif isinstance(node, ast.ImportFrom) and node.module:
        imps.add(node.module.split(".")[0])
gate("S2 census_predict.py imports none of stagesim/stagekit/stagexec/gscript",
     not (imps & {"stagesim", "stagekit", "stagexec", "gscript"}), sorted(imps))

tmp = tempfile.mkdtemp(prefix="census_selftest_")
made = []
try:
    pred_now = load("tools/bench/plan_ring_p2b_pred.json")
    gate("A0 current P2b pred md5 == 98ca9b30... and its census DigitalNumericConstant == +5",
         md5("tools/bench/plan_ring_p2b_pred.json") == PRED_P2B_MD5 and pred_now["census"].get("DigitalNumericConstant") == 5,
         pred_now["census"])
    # ---- A cycle 122's hand-typed +1
    fx = copy.deepcopy(pred_now)
    fx["census"]["DigitalNumericConstant"] = 1
    fx_p = os.path.join(tmp, "census_fixture_p2b_pred_c122.json")
    with open(fx_p, "w", encoding="utf-8") as f:
        json.dump(fx, f, indent=1)
    made.append(fx_p)
    rep = cp.predict(load("tools/bench/plan_ring_p2b.json"), fx, samples)
    fails = [p for p in rep["classes"] if p["verdict"] == "FAIL"]
    gate("A1 c122 prediction (+1) -> FAIL naming DigitalNumericConstant derived +5 declared +1, the only failing class",
         rep["overall"] == "FAIL" and [(p["class"], p["derived"], p["declared"]) for p in fails] == [("DigitalNumericConstant", 5, 1)],
         [(p["class"], p["derived"], p["declared"]) for p in fails])
    rc, rl, _ = run_tool("tools/bench/plan_ring_p2b.json", fx_p)
    gate("A2 CLI exit 1 and RESULT FAIL whose first_fail names DigitalNumericConstant +5",
         rc == 1 and rl and rl["status"] == "FAIL" and "DigitalNumericConstant derived +5" in (rl["first_fail"] or ""), (rc, rl))
    # ---- B the corrected prediction
    rep = cp.predict(load("tools/bench/plan_ring_p2b.json"), pred_now, samples)
    gate("B1 current pred -> PASS on every class, no unpredicted row",
         rep["overall"] == "PASS" and not rep["unpredicted"] and all(p["verdict"] == "PASS" for p in rep["classes"]),
         {"derived": rep["derived"], "declared": rep["declared"]})
    rc, rl, _ = run_tool("tools/bench/plan_ring_p2b.json", "tools/bench/plan_ring_p2b_pred.json")
    gate("B2 CLI exit 0 and RESULT PASS", rc == 0 and rl and rl["status"] == "PASS", (rc, rl))
    # ---- C P2a and pool: no FAIL, unpredicted rows listed
    for plan_p, pred_p, nrows in (("tools/bench/plan_ring_p2a.json", "tools/bench/plan_ring_p2a_pred.json", 8),
                                  ("tools/bench/plan_qrt_pool.json", "tools/bench/plan_qrt_pool_pred.json", 15)):
        rep = cp.predict(load(plan_p), load(pred_p), samples)
        rc, rl, _ = run_tool(plan_p, pred_p)
        gate("C %s -> no class FAIL, UNPREDICTED, %d unsampled rows listed, RESULT SKIP (never PASS)" % (os.path.basename(plan_p), nrows),
             rep["overall"] == "UNPREDICTED" and not any(p["verdict"] == "FAIL" for p in rep["classes"])
             and len(rep["unpredicted"]) == nrows and rc == 2 and rl and rl["status"] == "SKIP" and rl["gates"]["fail"] == 0,
             {"unpredicted": rep["unpredicted"], "rc": rc, "status": rl and rl["status"],
              "ops": sorted({r["op"] for r in rep["rows"]})})
    # ---- D a row with no sample
    plan_d = load("tools/bench/plan_ring_p2b.json")
    plan_d["actions"].append({"op": "create", "id": "fab_x", "class": "Function", "diagram": 4866, "as": "FX1",
                              "prim": "made_up"})
    rep = cp.predict(plan_d, pred_now, samples)
    row = [r for r in rep["rows"] if r["id"] == "fab_x"][0]
    gate("D1 fabricated row (create Function prim made_up) -> CENSUS-UNPREDICTED, overall UNPREDICTED, no class PASS",
         row["verdict"] == "CENSUS-UNPREDICTED" and rep["overall"] == "UNPREDICTED"
         and not any(p["verdict"] == "PASS" for p in rep["classes"]), (row, rep["overall"]))
    plan_e = load("tools/bench/plan_ring_p2b.json")
    pred_e = copy.deepcopy(pred_now)
    pred_e["rows"][0]["canon"] = "Array1D<U8>"  # Num's donor 130 -> an unmeasured canon
    for r in pred_e["rows"]:
        if r["donor_uid"] == 130:
            r["canon"] = "Array1D<U8>"
    rep = cp.predict(plan_e, pred_e, samples)
    gate("D2 const_donor row with unmeasured canon Array1D<U8> (and its indicator) -> UNPREDICTED, never PASS",
         rep["overall"] == "UNPREDICTED" and sorted(rep["unpredicted"]) == [1, 2, 7, 8], rep["unpredicted"])
    pd_p = os.path.join(tmp, "census_fixture_fab.json")
    with open(pd_p, "w", encoding="utf-8") as f:
        json.dump(plan_d, f, indent=1)
    made.append(pd_p)
    rc, rl, _ = run_tool(pd_p, "tools/bench/plan_ring_p2b_pred.json")
    gate("D3 CLI on the fabricated plan: exit 2, RESULT SKIP with fail 0 (never PASS)",
         rc == 2 and rl and rl["status"] == "SKIP" and rl["gates"]["fail"] == 0, (rc, rl))
finally:
    for p in made:
        try:
            os.remove(p)
        except OSError:
            pass
    try:
        os.rmdir(tmp)
    except OSError:
        pass

print("SELFTEST %d pass / %d fail" % (res["pass"], res["fail"]))
print(protocol.result_line(protocol.make_result(res["pass"], res["fail"], res["first"], artefacts=[
    {"path": "tools/census_predict.py", "md5": md5(TOOL)},
    {"path": "tools/bench/census_samples.json", "md5": md5(SAMPLES)}])))
sys.exit(1 if res["fail"] else 0)
