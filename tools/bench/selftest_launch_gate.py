r"""selftest_launch_gate - card chat-C1: the stage LAUNCH GATE (tools/stage_prerun.py check_launch, called from
tools/hooks/guard_bash.py.new prerun_gate) and the RETRO_RE false-close fix, tested on the .new file; only when every
case passes is it moved over guard_bash.py with os.replace (card: "edited on .new, self-tested, os.replace").
No LabVIEW. Records + logs live in a %TEMP% sandbox (PRERUN_RECORDS / PRERUN_LOG_DIR), never in tools/bench.
PREDICTION: L1-L9 and M1-M3, R1-R3 all PASS; then INSTALL replaces guard_bash.py (md5 changes to the .new's).
    py tools/bgrun.py --material --max-min 3 --log tools/bench/selftest_launch_gate.log -- py -u tools/bench/selftest_launch_gate.py
"""
import atexit
import hashlib
import importlib.machinery
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
HOOKS = os.path.join(TOOLS, "hooks")
# card 116-3 L1 (PD230(g)): the sandbox was %TEMP%/lg_selftest_<pid>, never deleted - a reused PID could meet the
# previous run's records.jsonl / stage_runs.jsonl (headcmp_79-6 H1, which runs this file twice, read 1/1 in 116-1 and
# 2/0 in diag_c116a_regress_before2.log; cause not measured). Now a fresh tempfile.mkdtemp, removed by the process-level finally (atexit runs on normal exit,
# sys.exit and an uncaught exception alike, so a failure anywhere below still cleans up).
SAND = tempfile.mkdtemp(prefix="lg_selftest_")
atexit.register(shutil.rmtree, SAND, True)
os.makedirs(os.path.join(SAND, "tools", "recipes"), exist_ok=True)
os.makedirs(os.path.join(SAND, "logs"), exist_ok=True)
os.environ["PRERUN_RECORDS"] = os.path.join(SAND, "records.jsonl")
os.environ["PRERUN_LOG_DIR"] = os.path.join(SAND, "logs")
os.environ["STAGE_RUNS"] = os.path.join(SAND, "stage_runs.jsonl")      # card chat-D: retry cap counts, sandboxed
os.environ["STAGE_RUNS_CYCLE"] = "cycle 901"
sys.path[:0] = [TOOLS, HOOKS]
import stage_prerun as SP   # noqa: E402
import protocol as P        # noqa: E402

REC = os.environ["PRERUN_RECORDS"]
STG = os.path.join(SAND, "tools", "recipes", "stage_lgtest.py")
open(STG, "w", encoding="utf-8").write("print('stage body')\n")
LAUNCH = 'py tools/bgrun.py --material --max-min 5 --log tools/bench/x.log -- py -u "{0}"'.format(STG)
res = []


def gate(label, ok, detail=""):
    res.append(bool(ok))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:300]), flush=True)


def records(*kinds_status, t=None):
    if os.path.exists(REC):
        os.remove(REC)
    for kind, st in kinds_status:
        r = SP.write_record(kind, STG, st, None)
        if t is not None:
            lines = open(REC, encoding="utf-8").read().splitlines()
            d = json.loads(lines[-1])
            d["t"] = t
            lines[-1] = json.dumps(d)
            open(REC, "w", encoding="utf-8").write("\n".join(lines) + "\n")


def clear_logs():
    for f in os.listdir(os.environ["PRERUN_LOG_DIR"]):
        os.remove(os.path.join(os.environ["PRERUN_LOG_DIR"], f))


print("---------- [L] check_launch (tools/stage_prerun.py)")
records()
ok, why = SP.check_launch(LAUNCH)
gate("L1 no records -> refused", not ok and "no dry + prerun PASS" in why, why.splitlines()[0] if why else "")
records(("dry", "PASS"))
ok, why = SP.check_launch(LAUNCH)
gate("L2 dry only -> refused (prerun missing)", not ok and "no prerun PASS" in why, why.splitlines()[0] if why else "")
records(("dry", "PASS"), ("prerun", "PASS"), t=time.time() - 100)
clear_logs()
ok, why = SP.check_launch(LAUNCH)
gate("L3 dry + prerun PASS, current sha, no later failure -> allowed", ok, why)
# card 121-5 (PD238(k)): the failing runs carry the CURRENT time (they are newer than the records by their own stamp),
# so L4/L4b test the script-name rule and decision 4, not a stale stamp; L4c = a failed --prerun segment is not a run.
NOW_STAMP = time.strftime("%Y-%m-%d %H:%M:%S")
open(os.path.join(os.environ["PRERUN_LOG_DIR"], "stage_lgtest.log"), "w", encoding="utf-8").write(
    "BGRUN START {1} limit 5.0 min: py -u {0}\nboom\nBGRUN END rc=1 after 3s\n".format(STG, NOW_STAMP))
ok, why = SP.check_launch(LAUNCH)
gate("L4 a FAILED run newer than the records -> refused (decision 4)", not ok and "decision 4" in why, why.splitlines()[0] if why else "")
clear_logs()
open(os.path.join(os.environ["PRERUN_LOG_DIR"], "other.log"), "w", encoding="utf-8").write(
    "BGRUN START {0} limit 5.0 min: py -u tools/recipes/stage_other.py\nBGRUN END rc=1 after 3s\n".format(NOW_STAMP))
ok, why = SP.check_launch(LAUNCH)
gate("L4b another script's failure does not invalidate these records", ok, why)
clear_logs()
open(os.path.join(os.environ["PRERUN_LOG_DIR"], "stage_lgtest_prerun.log"), "w", encoding="utf-8").write(
    "BGRUN START {1} limit 5.0 min: py -u tools/stage_prerun.py --prerun {0}\nPRERUN FAIL\nBGRUN END rc=1 after 3s\n".format(STG, NOW_STAMP))
ok, why = SP.check_launch(LAUNCH)
gate("L4c a FAILED --prerun segment of this stage is not a stage run -> allowed", ok, why)
clear_logs()
open(STG, "a", encoding="utf-8").write("print('edited')\n")
ok, why = SP.check_launch(LAUNCH)
gate("L5 script edited after the records (sha256 changed) -> refused", not ok and "sha256" in why, why.splitlines()[0] if why else "")
records(("dry", "PASS"), ("prerun", "FAIL"))
ok, why = SP.check_launch(LAUNCH)
gate("L6 prerun FAIL record -> refused", not ok, why.splitlines()[0] if why else "")
allowed = ['grep -n "x" "{0}"'.format(STG), 'cat "{0}"'.format(STG), 'py tools/stage_prerun.py --dry "{0}"'.format(STG),
           'py tools/bgrun.py --material --max-min 5 --log a.log -- py -u tools/stage_prerun.py --prerun "{0}"'.format(STG),
           "py -u tools/bench/diag_foo.py", "py -u tools/recipes/build_d1_m3a1.py", 'git add "{0}"'.format(STG)]
bad = [c for c in allowed if not SP.check_launch(c)[0]]
gate("L7 reads / dry / prerun / diagnostics / non-stage recipes / git are never refused ({0} commands)".format(len(allowed)), not bad, bad)
ok, why = SP.check_launch('py -u "{0}"'.format(STG))
gate("L8 a direct (non-bgrun) stage launch is gated too", not ok, why.splitlines()[0] if why else "")
ok, _w = SP.check_launch('cd x && py -u "{0}" ; echo done'.format(STG))
gate("L9 a stage launch inside a && / ; chain is found by argv", not ok)

print("---------- [C] RETRY CAP (card chat-D; RETRY_CAP={0})".format(SP.RETRY_CAP))
RUNS = os.environ["STAGE_RUNS"]
if os.path.exists(RUNS):
    os.remove(RUNS)
records(("dry", "PASS"), ("prerun", "PASS"), t=time.time() - 100)
clear_logs()


def nruns(cycle=None):
    return len([r for r in SP.read_stage_runs() if cycle is None or r.get("cycle") == cycle])


def launch(cmd):
    """The live path in miniature (card chat-L2): guard_bash CHECKS (check_launch, records nothing); only when it
    allows does bgrun start the child and RECORD it (record_started, `by: bgrun`) - the ONE recording place."""
    ok_, why_ = SP.check_launch(cmd)
    if ok_:
        SP.record_started(cmd, log="x.log", pid=0)
    return ok_, why_


ok, _w = SP.check_launch(LAUNCH)
gate("C0 check_launch records nothing (recording lives only in bgrun.record_started)", ok and nruns() == 0, nruns())
r1 = launch(LAUNCH)
r2 = launch(LAUNCH)
gate("C1 runs 1 and 2 of a stage in one cycle are allowed and recorded by bgrun",
     r1[0] and r2[0] and nruns() == 2 and all(r.get("by") == "bgrun" for r in SP.read_stage_runs()), (r1, r2, nruns()))
ok, why = launch(LAUNCH)
gate("C2 run 3 without a judgement card -> refused (RETRY CAP), not recorded", not ok and "RETRY CAP" in why and nruns() == 2,
     why.splitlines()[0] if why else "")


def task_card(cid, retry_of):
    c = {"schema": "task/1", "id": cid, "kind": "build", "goal": "retry the stage", "flags": {
        "labview": "build", "gui": False, "hardware": "none", "run_vi": False, "write": [], "status_edit": False,
        "git_commit": False, "peers": []}, "budget": {"failures": 1, "minutes": 30}, "unblocks": "M3"}
    if retry_of:
        c["retry_of"] = retry_of
    p = os.path.join(SAND, "task_{0}.json".format(cid))
    json.dump(c, open(p, "w", encoding="utf-8"))
    return p


good = task_card("lg-retry-1", "stage_lgtest.py")
ok, why = launch("RETRY_CARD={0} ".format(good) + LAUNCH)
gate("C3 run 3 WITH a task/1 card retry_of=stage_lgtest.py -> allowed, recorded with the card id",
     ok and nruns() == 3 and SP.read_stage_runs()[-1].get("card") == "lg-retry-1", why)
ok, why = launch("RETRY_CARD={0} ".format(good) + LAUNCH)
gate("C4 the SAME card again -> refused (one card, one run)", not ok and "one card, one run" in why, why.splitlines()[0] if why else "")
wrong = task_card("lg-retry-2", "stage_other.py")
ok, why = launch("RETRY_CARD={0} ".format(wrong) + LAUNCH)
gate("C5 a card whose retry_of names another stage -> refused", not ok and "retry_of" in why, why.splitlines()[0] if why else "")
plain = task_card("lg-retry-3", None)
ok, why = launch("$env:RETRY_CARD='{0}'; ".format(plain) + LAUNCH)
gate("C6 a task card without retry_of (PowerShell env form) -> refused", not ok and "retry_of" in why, why.splitlines()[0] if why else "")
os.environ["STAGE_RUNS_CYCLE"] = "cycle 902"
ok, why = launch(LAUNCH)
gate("C7 a new cycle starts a fresh count -> allowed", ok and nruns("cycle 902") == 1, why)
os.environ["STAGE_RUNS_CYCLE"] = "cycle 901"
gate("C8 stage key strips _vN (stage_x_v3.py == stage_x.py)", SP.stage_key("tools/recipes/stage_x_v3.py") == "stage_x.py")
if os.path.exists(RUNS):
    os.remove(RUNS)

print("---------- [M/R] guard_bash main() (the .new when one is staged, else the installed hook)")
NEW = os.path.join(HOOKS, "guard_bash.py.new")
STAGED = os.path.exists(NEW)
if not STAGED:
    NEW = os.path.join(HOOKS, "guard_bash.py")
spec = importlib.util.spec_from_file_location("guard_bash_new", NEW, loader=importlib.machinery.SourceFileLoader("guard_bash_new", NEW))
GB = importlib.util.module_from_spec(spec)
spec.loader.exec_module(GB)
sys.modules["guard_card"] = types.SimpleNamespace(decide=lambda data: (0, None))
GB.motor_gate_check = lambda cmd: 0
GB.stop_gate = lambda cmd: 0
GB.next_gate = lambda: 0
GB.note = lambda *a: None
closed = []
GB.guard_session.mark_retro_done = lambda sid: closed.append(sid)


def main_rc(cmd, extra=None, **ti):
    d = {"tool_name": "Bash", "tool_input": dict({"command": cmd, "timeout": 10000}, **ti), "session_id": "selftest"}
    d.update(extra or {})
    old_in, old_err = sys.stdin, sys.stderr
    sys.stdin, sys.stderr = io.StringIO(json.dumps(d)), io.StringIO()
    try:
        rc = GB.main()
        return rc, sys.stderr.getvalue()
    finally:
        sys.stdin, sys.stderr = old_in, old_err


records()
rc, err = main_rc(LAUNCH, run_in_background=True)
gate("M1 guard_bash.new refuses a bgrun stage launch with no records (rc 2, LAUNCH GATE text)", rc == 2 and "LAUNCH GATE" in err, err[:160])
rc, err = main_rc('grep -n "gate" "{0}"'.format(STG))
gate("M2 guard_bash.new passes a grep of the stage file", rc == 0, err[:160])
records(("dry", "PASS"), ("prerun", "PASS"), t=time.time() - 100)
rc, err = main_rc(LAUNCH, run_in_background=True)
gate("M3 guard_bash.new passes the same launch once dry + prerun PASS exist", rc == 0, err[:160])
gate("M4 the hook itself records nothing (bgrun is the one recorder, card 78-2 / chat-L2)", nruns() == 0, nruns())
SP.record_started(LAUNCH, log="x.log", pid=0)      # bgrun started that allowed launch
records()
rc, err = main_rc(LAUNCH, run_in_background=True)
gate("M5 a refused launch (no records) is NOT recorded", rc == 2 and nruns() == 1, nruns())
records(("dry", "PASS"), ("prerun", "PASS"), t=time.time() - 100)
rc2, _e = main_rc(LAUNCH, run_in_background=True)
if rc2 == 0:
    SP.record_started(LAUNCH, log="x.log", pid=0)  # run 2 started
rc, err = main_rc(LAUNCH, run_in_background=True)
gate("M6 guard_bash refuses the 3rd launch in the cycle with the RETRY CAP text",
     rc2 == 0 and rc == 2 and "RETRY CAP" in err and nruns() == 2, "run2 exit %d, run3 exit %d, %s" % (rc2, rc, err[:160]))
RETRO = "py tools/retrospective.py --cycle 99"
closed.clear()
main_rc(RETRO, {"agent_id": "a123", "agent_type": "material"})
gate("R1 a retrospective call carrying agent_id does NOT set retro_done", closed == [], closed)
closed.clear()
main_rc(RETRO + " --dry-run")
gate("R2 a --dry-run retrospective does NOT set retro_done", closed == [], closed)
closed.clear()
main_rc(RETRO)
gate("R3 the main session's real retrospective still sets retro_done", closed == ["selftest"], closed)

npass, nfail = sum(res), len(res) - sum(res)
print("=== GATES: {0} pass / {1} fail".format(npass, nfail))
if not STAGED:
    print("  FACT  tested the INSTALLED guard_bash.py (no .new staged) - nothing to install")
elif nfail == 0:
    old = os.path.join(HOOKS, "guard_bash.py")
    m0 = hashlib.md5(open(old, "rb").read()).hexdigest()
    os.replace(NEW, old)
    m1 = hashlib.md5(open(old, "rb").read()).hexdigest()
    print("  FACT  INSTALL os.replace(guard_bash.py.new -> guard_bash.py): md5 {0} -> {1}".format(m0, m1))
else:
    print("  FACT  NOT INSTALLED - guard_bash.py unchanged, the .new stays for inspection")
print(P.result_line(P.make_result(npass, nfail, None if nfail == 0 else "selftest case failed")))
sys.exit(0 if nfail == 0 else 1)
