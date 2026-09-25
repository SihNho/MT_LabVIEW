r"""selftest_stage_prerun_stageplan - card 79-6 (PD178(g)): stage_prerun.py pre-runs a recipe against a named stageplan/1
ONLY if it is final and finalized PASS; X3 counts its actions; X5 == its compiled wiring real ops covering every wire
action. No LabVIEW; `dry` is replaced by a synthetic trace (the gates under test read only its `ops`), plans and recipes
live in a %TEMP% sandbox, records go to a sandbox file. Then the three existing stage_prerun self-tests are re-run.
PREDICTION: S1-S9 PASS, and selftest_launch_gate / selftest_retry_cap / selftest_stagexec_gate each rc 0.
    py tools/bgrun.py --material --max-min 6 --log tools/bench/selftest_stage_prerun_stageplan.log -- py -u tools/bench/selftest_stage_prerun_stageplan.py"""
import copy, json, os, re, shutil, subprocess, sys                                  # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS, ROOT = os.path.dirname(HERE), os.path.dirname(os.path.dirname(HERE))
SAND = os.path.join(os.environ.get("TEMP", "."), "spsp_selftest_{0}".format(os.getpid()))
os.makedirs(SAND, exist_ok=True)
os.environ["PRERUN_RECORDS"] = os.path.join(SAND, "records.jsonl")
sys.path.insert(0, TOOLS)
import stage_prerun as SP   # noqa: E402
import protocol as P        # noqa: E402
G = []
K = json.load(open(os.path.join(HERE, "plan_k_split.json"), encoding="utf-8"))


def gate(label, ok, detail=""):
    G.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:300]), flush=True)


def case(name, plan, n_wire_ops, key="stageplan"):
    pp = os.path.join(SAND, "plan_{0}.json".format(name))
    json.dump(plan, open(pp, "w", encoding="utf-8"), indent=1)
    rp = os.path.join(SAND, "stage_{0}.py".format(name))
    open(rp, "w", encoding="utf-8").write("PLAN = 'plan_{0}.json'\n".format(name))
    SP.dry = lambda recipe, graph=None: {"status": "PASS", "first_fail": None, "addresses": [], "jev": [], "input_md5": None,
                                         "ops": ["move_in"] * 3 + ["add_sr"] + ["wire_tunnel"] * n_wire_ops}
    print("--- case", name, flush=True)
    pr = SP.prerun(rp)["prerun"]
    return dict((g_[0][:2], g_[1]) for g_ in pr["gates"]), pr, rp, pp


g, pr, rp, pp = case("ok", K, 11)
gate("S1 the valid K plan (final, finalized PASS) is accepted: X2 X3 X5 PASS", g["X2"] and g["X3"] and g["X5"], pr["gates"][1:5])
gate("S2 X3 counts the 27 actions; X5 detail = 11 wiring real ops covering 17/17 wire actions",
     "27 stageplan actions" in pr["gates"][2][2] and "stageplan wiring real ops 11 (covering 17/17" in [x for x in pr["gates"] if x[0][:2] == "X5"][0][2],
     [pr["gates"][2][2], [x for x in pr["gates"] if x[0][:2] == "X5"][0][2]])
gate("S3 plan_md5s keys the records on the stageplan's md5", SP.plan_md5s(rp) == {SP.rel(pp): SP.md5(pp)}, SP.plan_md5s(rp))
g, pr, _r, _p = case("opmis", K, 10)
gate("S4 op-count mismatch (10 dry wiring ops vs 11) => X5 FAIL", g["X2"] and not g["X5"], [x for x in pr["gates"] if x[0][:2] == "X5"])
nf = dict(copy.deepcopy(K), final=False)
g, pr, _r, _p = case("notfinal", nf, 11)
gate("S5 final=false => X2 FAIL and X5 FAIL", not g["X2"] and not g["X5"], pr["gates"][1][2])
ff = copy.deepcopy(K); ff["finalized"]["failed"] = {"n": 5}
g, pr, _r, _p = case("failed", ff, 11)
gate("S6 finalized.failed set => X2 FAIL", not g["X2"] and "failed" in pr["gates"][1][2], pr["gates"][1][2])
om = copy.deepcopy(K); om["finalized"]["open_rows_match"] = False
g, pr, _r, _p = case("orm", om, 11)
gate("S7 open_rows_match false => X2 FAIL", not g["X2"], pr["gates"][1][2])
dr = copy.deepcopy(K); dr["actions"] = dr["actions"][:-1]
g, pr, _r, _p = case("drop", dr, 10)
gate("S8 an action removed after finalize (step files no longer match) => X2 FAIL", not g["X2"], pr["gates"][1][2])
dec = {"decisions": [{"id": "r1", "action": "wire"}, {"id": "r2", "action": "keep"}]}
g, pr, _r, _p = case("dec", dec, 1)
gate("S9 decisions-row path unchanged: 2 rows, 1 wire row == 1 dry wiring op => X2 X3 X5 PASS",
     g["X2"] and g["X3"] and g["X5"] and "2 rows + 0 stageplan actions" in pr["gates"][2][2], pr["gates"][1:5])
for t in ("selftest_launch_gate.py", "selftest_retry_cap.py", "selftest_stagexec_gate.py"):
    p_ = subprocess.run([sys.executable, "-u", os.path.join(HERE, t)], cwd=ROOT, capture_output=True, text=True, timeout=240)
    line = ([ln for ln in p_.stdout.splitlines() if ln.startswith("=== GATES") or ln.startswith("RESULT")] or ["(no summary)"])
    gate("EX {0} rc 0".format(t), p_.returncode == 0, " | ".join(line) + (" | " + p_.stderr[-200:] if p_.returncode else ""))
n_pass = sum(1 for _l, o in G if o)
first = next((l for l, o in G if not o), None)
print("=== GATES: {0} pass / {1} fail{2}".format(n_pass, len(G) - n_pass, "; failing: " + first if first else ""))
print(P.result_line(P.make_result(n_pass, len(G) - n_pass, first)))
shutil.rmtree(SAND, ignore_errors=True)
sys.stdout.flush()
os._exit(0 if n_pass == len(G) else 1)
