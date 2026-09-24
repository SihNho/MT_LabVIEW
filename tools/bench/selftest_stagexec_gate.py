r"""selftest_stagexec_gate - card chat-S3: the LAUNCH GATE for `tools/stagexec.py run <plan>` (tools/stage_prerun.py
launched_plan_runs / plan_record / check_launch; guard_bash.prerun_gate delegates to it). No LabVIEW; records and logs in
a %TEMP% sandbox (PRERUN_RECORDS / PRERUN_LOG_DIR / STAGE_RUNS), never in tools/bench.
PREDICTION: G1-G7 PASS.
    MATERIAL=1 py tools/bgrun.py --max-min 3 --log tools/bench/selftest_stagexec_gate.log -- py -u tools/bench/selftest_stagexec_gate.py"""
import json, os, shutil, sys, time                                                 # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
SAND = os.path.join(os.environ.get("TEMP", "."), "sxg_selftest_{0}".format(os.getpid()))
os.makedirs(os.path.join(SAND, "logs"), exist_ok=True)
os.environ["PRERUN_RECORDS"] = os.path.join(SAND, "records.jsonl")
os.environ["PRERUN_LOG_DIR"] = os.path.join(SAND, "logs")
os.environ["STAGE_RUNS"] = os.path.join(SAND, "stage_runs.jsonl")
os.environ["STAGE_RUNS_CYCLE"] = "cycle 902"
sys.path.insert(0, TOOLS)
import stage_prerun as SP   # noqa: E402
import protocol as P        # noqa: E402
G = []


def gate(label, ok, detail=""):
    G.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:300]), flush=True)


plan = os.path.join(SAND, "plan_x.json")
shutil.copyfile(os.path.join(HERE, "plan_l7_split.json"), plan)
cmd = "MATERIAL=1 py tools/bgrun.py --max-min 60 --log tools/bench/x.log -- py -u tools/stagexec.py run {0}".format(plan)
u = SP.launched_plan_runs(cmd)
gate("G1 a bgrun'd `stagexec.py run <plan>` is ONE plan launch", len(u) == 1 and u[0][1] == os.path.normpath(plan), u)
gate("G2 reading/grepping stagexec.py or running its dry/prerun is not a launch",
     not SP.launched_plan_runs("grep run tools/stagexec.py") and not SP.launched_plan_runs("py tools/stagexec.py prerun " + plan)
     and not SP.launched_plan_runs("py tools/stagexec.py dry " + plan))
ok, why = SP.check_launch(cmd)
gate("G3 no dry/prerun record for the plan => refused, naming the plan", not ok and "plan_x.json" in why, why.splitlines()[0] if why else "")
SP.plan_record("dry", plan, "PASS", None)
ok, why = SP.check_launch(cmd)
gate("G4 dry only => still refused (prerun missing)", not ok and "prerun" in why, why.splitlines()[0] if why else "")
SP.plan_record("prerun", plan, "PASS", None)
ok, why = SP.check_launch(cmd)
gate("G5 dry + prerun PASS for this stagexec sha256 and plan md5 => allowed", ok, why)
with open(plan, "a", encoding="utf-8") as f:
    f.write(" ")
ok, why = SP.check_launch(cmd)
gate("G6 the plan changed after its records (md5) => refused", not ok and "no dry + prerun" in why, why.splitlines()[0] if why else "")
SP.plan_record("dry", plan, "PASS", None)
SP.plan_record("prerun", plan, "PASS", None)
time.sleep(1.1)
with open(os.path.join(SAND, "logs", "stagexec_x.log"), "w", encoding="utf-8") as f:
    f.write("BGRUN START 2026-09-24 00:00:00 limit 60.0 min: py -u tools/stagexec.py run {0}\n".format(plan))
    f.write(P.result_line(P.make_result(3, 1, "STEP-DIFF after real op 3")) + "\nBGRUN END rc=1 after 5s\n")
ok, why = SP.check_launch(cmd)
gate("G7 a FAILED stagexec run after the records => refused until re-pre-run (decision 4)", not ok and "FAILED" in why,
     why.splitlines()[0] if why else "")
n_pass = sum(1 for _l, o in G if o)
first = next((l for l, o in G if not o), None)
print("=== GATES: {0} pass / {1} fail{2}".format(n_pass, len(G) - n_pass, "; failing: " + first if first else ""))
print(P.result_line(P.make_result(n_pass, len(G) - n_pass, first)))
shutil.rmtree(SAND, ignore_errors=True)
sys.exit(0 if n_pass == len(G) else 1)
