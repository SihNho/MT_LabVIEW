r"""diag_c135_2_resim - card 135-2 pass 1, second half: OFFLINE, no LabVIEW. Plan b ae6b6111 is valid only with the 19 step files
its finalize recorded (`finalized.step_files`, md5 each; stagexec.load_final_plan, stagexec.py:178-180). The failed finalize of
135-1 (launch_p3b2_c135_f.log, 12:33) REWROTE tools/bench/sim/ring_p3b2b/step_*.json (stagesim.simulate deletes and rewrites the
stage's step files, stagesim.py:2181-2182), so the dry of recipe b failed `19 step file(s) missing or changed since finalize`
(stage_prerun_c135_2_dry_b.log). The step files are not in git (git ls-files: candidates.json, summary.json only).
WHAT EXISTED: stagesim.simulate itself - the step files are a deterministic function of (plan_in, base graph, models, stagesim
code); stagesim.py last changed 11:05, plan b finalized 11:15 (its `at`), so the same code. Nothing new is decided: plan b's
bytes are NOT touched (the simulated plan goes to %TEMP%); only the step files are regenerated and each is md5-checked against
the pins plan b ae6b6111 holds. The failed finalize's sim files are kept under tools/bench/sim/ring_p3b2b_c135_1_fail/.
PREDICTION: S1 plan b ae6b6111, plan_in cccfee8f and base b885fa4a as pinned; S2 simulate on the base ends FINAL, failed None;
S3 all 19 regenerated step files md5 == plan b's step_files pins; S4 plan b still ae6b6111.
    py tools/bgrun.py --material --max-min 6 --log tools/bench/diag_c135_2_resim.log -- py -u tools/bench/diag_c135_2_resim.py"""
import glob, hashlib, json, os, shutil, sys, tempfile                              # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P, stagesim as SS                                               # noqa: E402,E401
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                      # noqa: E731
A = lambda p: os.path.join(ROOT, p)                                                # noqa: E731
ok = []


def gate(n, c, d=""):
    ok.append((n, bool(c)))
    print("  {0}  {1}  {2}".format("PASS" if c else "FAIL", n, json.dumps(d, default=str)[:900]), flush=True)
    return bool(c)


def finish():
    np_, nf = sum(1 for _n, c in ok if c), sum(1 for _n, c in ok if not c)
    print(P.result_line(P.make_result(np_, nf, next((n for n, c in ok if not c), None))), flush=True)
    sys.exit(1 if nf else 0)


PB = A("tools/bench/plan_ring_p3b2b.json")
pb = json.load(open(PB, encoding="utf-8"))
fz = pb["finalized"]
pins = dict((f["path"], f["md5"]) for f in fz["step_files"])
if not gate("S1 plan b ae6b6111; plan_in + base as its finalize recorded", md5(PB) == "ae6b6111d766a4ba27d0695f29958c23"
            and md5(A(fz["plan_in"]["path"])) == fz["plan_in"]["md5"] and md5(A(fz["base"]["path"])) == fz["base"]["md5"],
            {"plan_in": md5(A(fz["plan_in"]["path"])), "base": md5(A(fz["base"]["path"])), "n_steps": len(pins)}):
    finish()
SD = A("tools/bench/sim/ring_p3b2b")
KEEP = SD + "_c135_1_fail"
if not os.path.isdir(KEEP):
    shutil.copytree(SD, KEEP)
print("  FACT  failed finalize's sim files kept: {0} ({1} files)".format(os.path.relpath(KEEP, ROOT), len(os.listdir(KEEP))), flush=True)
tmp = tempfile.mkdtemp(prefix="c135_2_resim_")
S = SS.simulate(A(fz["plan_in"]["path"]), A(fz["base"]["path"]), plan_out_dir=tmp, log=lambda *x: None, route_check=False)
gate("S2 simulate FINAL, failed None", S["final"] and S["failed"] is None, {"final": S["final"], "failed": S["failed"]})
got = dict((os.path.relpath(p, ROOT).replace("\\", "/"), md5(p)) for p in glob.glob(os.path.join(SD, "step_*.json")))
bad = dict((p, [m, got.get(p)]) for p, m in pins.items() if got.get(p) != m)
gate("S3 {0} regenerated step files md5 == plan b's pins".format(len(pins)), not bad and len(got) == len(pins), bad)
gate("S4 plan b bytes untouched (ae6b6111)", md5(PB) == "ae6b6111d766a4ba27d0695f29958c23")
print("  FACT  summary.json now {0} (plan b records {1}; not checked by load_final_plan)".format(
    md5(os.path.join(SD, "summary.json")), fz["summary"]["md5"]), flush=True)
shutil.rmtree(tmp, ignore_errors=True)
finish()
