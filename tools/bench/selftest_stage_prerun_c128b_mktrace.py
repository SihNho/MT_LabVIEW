r"""selftest_stage_prerun_c128b_mktrace - card 130-5 (PD268(c)): write the c128b fixture trace. A FRESH-PROCESS
`stage_prerun --dry tools/recipes/stage_d1_ring_p3b.py --no-record --json-out <tmp>` on the RE-FINALIZED unsplit 70 (REFERENCE,
never launched), plus plan_md5 = plan_ring_p3b.json's md5 at trace time -> tools/bench/selftest_stage_prerun_c128b_trace.json.
PURE PYTHON, no LabVIEW (stage_prerun stubs COM). EXISTING FIRST: diag_c128_3_recipe_dry.json was made the same way (card 128-3).
Prediction: dry rc 0, DRY PASS, 70 ops, the Executor completed 70 of 70.
    py tools/bgrun.py --material --max-min 6 --log tools/bench/selftest_stage_prerun_c128b_mktrace.log -- py -u tools/bench/selftest_stage_prerun_c128b_mktrace.py
"""
import hashlib, json, os, subprocess, sys, tempfile    # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE); ROOT = os.path.dirname(TOOLS)  # noqa: E702
sys.path.insert(0, TOOLS)
import protocol    # noqa: E402
PLAN = os.path.join(HERE, "plan_ring_p3b.json")
REC = os.path.join(TOOLS, "recipes", "stage_d1_ring_p3b.py")
OUT = os.path.join(HERE, "selftest_stage_prerun_c128b_trace.json")
pm = hashlib.md5(open(PLAN, "rb").read()).hexdigest()
tmp = os.path.join(tempfile.gettempdir(), "c130_5_trace_{0}.json".format(os.getpid()))
p = subprocess.run([sys.executable, "-u", os.path.join(TOOLS, "stage_prerun.py"), "--dry", REC, "--no-record", "--json-out", tmp],
                   cwd=ROOT, capture_output=True, text=True, timeout=300)
dl = [ln for ln in p.stdout.splitlines() if ln.startswith("=== DRY")]
print("  FACT dry rc {0} | {1}".format(p.returncode, dl[-1][:600] if dl else p.stdout[-600:]), flush=True)
tr = json.load(open(tmp, encoding="utf-8"))
os.remove(tmp)
tr["plan_md5"] = pm
tr["made_by"] = "selftest_stage_prerun_c128b_mktrace.py (card 130-5)"
json.dump(tr, open(OUT, "w", encoding="utf-8"), indent=1, default=str)
ex = tr.get("executors") or []
print("  FACT ops {0}, executors {1}".format(len(tr["ops"]), json.dumps(ex, default=str)[:500]), flush=True)
ok = p.returncode == 0 and tr["status"] == "PASS" and len(tr["ops"]) == 70 and len(ex) == 1 and (ex[0].get("run") or {}).get("executed") == 70
print("  {0}  M1 fresh-process dry of the unsplit 70 reference: rc 0, PASS, 70 ops, Executor 70 of 70".format("PASS" if ok else "FAIL"), flush=True)
om = hashlib.md5(open(OUT, "rb").read()).hexdigest()
print(protocol.result_line(protocol.make_result(int(ok), int(not ok), None if ok else "M1 dry of the unsplit 70",
                                                [{"path": os.path.relpath(OUT, ROOT).replace("\\", "/"), "md5": om}])), flush=True)
sys.exit(0 if ok else 1)
