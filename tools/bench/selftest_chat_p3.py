r"""selftest_chat_p3 - card chat-P3 (user 2026-09-28 "A는 실행"): item A (no scratch build on a proven pattern) and the
fp-8 fix (protocol.RUNNER_CMD_RE anchored). Touches NO LabVIEW; every store is a temp sandbox (env set BEFORE import).
WHAT EXISTED: selftest_chat_p1.py t_proven (the proven_pattern fixture shape, reused here), selftest_launch_gate.py
(the sandbox env names PRERUN_RECORDS / PRERUN_LOG_DIR / STAGE_RUNS / STAGE_RUNS_CYCLE).

PREDICTION CONTRACT
  R1 RUNNER_CMD_RE does NOT match `tools/bench/selftest_cycle_runner.py` nor `selftest_cycle_runner_ff.py`
  R2 it matches `tools/cycle_runner.py`, `tools\cycle_runner.py`, a bare `cycle_runner.py`
  R3 protocol.check_command under a hardware:none card: the self-test launch passes the runner rule; a real runner
     launch is refused with the 'use --dry-run' message
  A1 proven (2 other clean stages) + dry + prerun PASS on the current sha/plan md5s -> scratch NOT required
  A2 check_launch ALLOWS that launch and writes `SCRATCH-SKIP-PROVEN | stage_p3new.py | proven: stage_a.py, stage_b.py`
  A3 a NEW structure class (create:EventStructure, no clean stage ran it) -> required, reason names the class
  A4 proven but no dry/prerun PASS for the current bytes -> required
  A5 after a FAILED real launch of the stage -> required again (no second skip); nothing logged by A3-A5
  A6 a recipe outside tools/recipes/stage_*.py -> required (rule unchanged)
    py tools/bgrun.py --material --max-min 3 --log tools/bench/selftest_chat_p3.log -- py -u tools/bench/selftest_chat_p3.py
"""
import json
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TMP = tempfile.mkdtemp(prefix="p3st_")
os.environ["PRERUN_RECORDS"] = os.path.join(TMP, "records.jsonl")
os.environ["PRERUN_LOG_DIR"] = os.path.join(TMP, "logs")
os.environ["STAGE_RUNS"] = os.path.join(TMP, "stage_runs.jsonl")
os.environ["STAGE_RUNS_CYCLE"] = "cycle 903"
os.environ["SCRATCH_SKIP_LOG"] = os.path.join(TMP, "skip.log")
os.environ["SCRATCH_VERIFY_DIR"] = os.path.join(TMP, "scratch_verify")
os.makedirs(os.environ["PRERUN_LOG_DIR"])
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P      # noqa: E402
import stage_prerun as SP  # noqa: E402

RES = []


def gate(label, ok, detail=""):
    RES.append((label, bool(ok)))
    print("  %-4s %-66s %s" % ("ok" if ok else "BAD", label, str(detail)[:220]), flush=True)


def wj(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1)
    return path


def recipe(name, plan, actions, extra=""):
    rdir = os.path.join(TMP, "pp", "tools", "recipes")
    os.makedirs(rdir, exist_ok=True)
    p = os.path.join(rdir, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write("import stagekit as K, stagexec as SX\nPLAN = %r\nx = SX.Executor(PLAN)\nK.run(x, None)\n%s" % (plan, extra))
    wj(os.path.join(rdir, plan), {"schema": "stageplan/1", "stage": name, "actions": actions})
    return p.replace("\\", "/")


def clean_log(path, ok=True, cmd="py -u tools/recipes/stage_x.py", start=None):
    with open(path, "w", encoding="utf-8") as f:
        f.write("BGRUN START %s limit 30.0 min: %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start or time.time() - 3600)), cmd))
        f.write(P.result_line(P.make_result(5 if ok else 4, 0 if ok else 1, None if ok else "G3")) + "\n")
        f.write("BGRUN END rc=%d after 60s\n" % (0 if ok else 1))
    return path


def skip_lines():
    try:
        return [ln.strip() for ln in open(os.environ["SCRATCH_SKIP_LOG"], encoding="utf-8") if ln.strip()]
    except OSError:
        return []


# ---------------------------------------------------------------- R: fp-8, RUNNER_CMD_RE anchored on the file name
R = P.RUNNER_CMD_RE
gate("R1 selftest_cycle_runner*.py is not a runner launch",
     not R.search("py -u tools/bench/selftest_cycle_runner.py") and not R.search("tools/bench/selftest_cycle_runner_ff.py"))
gate("R2 tools/cycle_runner.py, tools\\cycle_runner.py, bare cycle_runner.py match",
     all(R.search(c) for c in ("py -u tools/cycle_runner.py --budget-min 480", "py tools\\cycle_runner.py", "py cycle_runner.py")))
card = {"schema": "task/1", "id": "p3-r3", "kind": "build", "goal": "g", "why": "w", "inputs": [], "pass": ["x"],
        "outputs": [], "flags": {"labview": "none", "gui": False, "hardware": "none", "run_vi": False, "write": ["tools/**"],
                                 "status_edit": False, "git_commit": False, "peers": []},
        "budget": {"failures": 2, "minutes": 60}, "rules": [], "unblocks": "M3"}
w1 = P.check_command(card, "py tools/bgrun.py --material --max-min 3 --log tools/bench/x.log -- py -u tools/bench/selftest_cycle_runner.py")
w2 = P.check_command(card, "py tools/bgrun.py --max-min 720 --log tools/bench/x.log -- py -u tools/cycle_runner.py")
gate("R3 check_command: self-test not refused by the runner rule; the real runner is", not (w1 and "cycle_runner" in str(w1))
     and bool(w2) and "use --dry-run" in str(w2), (w1, w2))

# ---------------------------------------------------------------- A: scratch build requirement
ACTS = [{"op": "wire", "src": "1.a", "dst": "2.b"}, {"op": "create", "class": "Local", "diagram": 3}]
rec = recipe("stage_p3new.py", "plan_p3pp.json", ACTS)
sig = SP.pattern_signature(rec)
big = sig + ["op:tunnel", "K.save"]
la, lb = (clean_log(os.path.join(TMP, n)) for n in ("a.log", "b.log"))
with open(os.environ["STAGE_RUNS"], "w", encoding="utf-8") as f:
    for st, lg in (("stage_a.py", la), ("stage_b.py", lb)):
        f.write(json.dumps({"by": "bgrun", "stage": st, "pattern": big, "log": lg, "cycle": "cycle 800"}) + "\n")
SP.write_record("dry", rec, "PASS", None)
SP.write_record("prerun", rec, "PASS", None)
req, why, st = SP.scratch_requirement(rec)
gate("A1 proven + dry/prerun PASS on the current bytes -> scratch NOT required", not req and st == ["stage_a.py", "stage_b.py"], (req, why))
ok, why_l = SP.check_launch("py tools/bgrun.py --material --max-min 30 --log x.log -- py -u " + rec)
sk = skip_lines()
gate("A2 check_launch ALLOWS and logs SCRATCH-SKIP-PROVEN", ok and len(sk) == 1
     and sk[0].startswith("SCRATCH-SKIP-PROVEN | stage_p3new.py | proven: stage_a.py, stage_b.py | "), (ok, why_l[:120], sk))
rec2 = recipe("stage_p3cls.py", "plan_p3cls.json", ACTS + [{"op": "create", "class": "EventStructure", "diagram": 3}])
req, why, _st = SP.scratch_requirement(rec2)
gate("A3 a NEW structure class -> required, reason names it", req and "create:EventStructure" in why, why)
rec3 = recipe("stage_p3norec.py", "plan_p3norec.json", ACTS, extra="# different bytes, no records\n")
req, why, _st = SP.scratch_requirement(rec3)
gate("A4 proven but no dry/prerun PASS for these bytes -> required", req and "no dry + prerun PASS" in why, why)
clean_log(os.path.join(os.environ["PRERUN_LOG_DIR"], "stage_p3new.log"), ok=False,
          cmd="py -u tools/recipes/stage_p3new.py", start=time.time() - 120)
req, why, _st = SP.scratch_requirement(rec)
gate("A5 after a FAILED real launch -> required again (no second skip)", req and "FAILED" in why, why)
gate("A5b nothing new logged by A3-A5 (the log still holds A2's one line)", len(skip_lines()) == 1, skip_lines())
req, why, _st = SP.scratch_requirement(os.path.join(ROOT, "tools", "bench", "diag_foo.py"))
gate("A6 a non-stage recipe -> required (rule unchanged)", req and "not a tools/recipes/stage_" in why, why)

shutil.rmtree(TMP, ignore_errors=True)
n_pass = sum(1 for _l, o in RES if o)
n_fail = len(RES) - n_pass
first = next((l for l, o in RES if not o), None)
print("=== GATES: %d pass / %d fail" % (n_pass, n_fail))
print(P.result_line(P.make_result(n_pass, n_fail, first)))
sys.exit(0 if n_fail == 0 else 1)
