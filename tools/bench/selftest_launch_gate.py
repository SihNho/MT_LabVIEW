r"""selftest_launch_gate - card chat-C1: the stage LAUNCH GATE (tools/stage_prerun.py check_launch, called from
tools/hooks/guard_bash.py.new prerun_gate) and the RETRO_RE false-close fix, tested on the .new file; only when every
case passes is it moved over guard_bash.py with os.replace (card: "edited on .new, self-tested, os.replace").
No LabVIEW. Records + logs live in a %TEMP% sandbox (PRERUN_RECORDS / PRERUN_LOG_DIR), never in tools/bench.
PREDICTION: L1-L9 and M1-M3, R1-R3 all PASS; then INSTALL replaces guard_bash.py (md5 changes to the .new's).
    py tools/bgrun.py --material --max-min 3 --log tools/bench/selftest_launch_gate.log -- py -u tools/bench/selftest_launch_gate.py
"""
import hashlib
import importlib.machinery
import importlib.util
import io
import json
import os
import sys
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
HOOKS = os.path.join(TOOLS, "hooks")
SAND = os.path.join(os.environ.get("TEMP", "."), "lg_selftest_{0}".format(os.getpid()))
os.makedirs(os.path.join(SAND, "tools", "recipes"), exist_ok=True)
os.makedirs(os.path.join(SAND, "logs"), exist_ok=True)
os.environ["PRERUN_RECORDS"] = os.path.join(SAND, "records.jsonl")
os.environ["PRERUN_LOG_DIR"] = os.path.join(SAND, "logs")
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
open(os.path.join(os.environ["PRERUN_LOG_DIR"], "stage_lgtest.log"), "w", encoding="utf-8").write(
    "BGRUN START 2026-09-24 20:00:00 limit 5.0 min: py -u {0}\nboom\nBGRUN END rc=1 after 3s\n".format(STG))
ok, why = SP.check_launch(LAUNCH)
gate("L4 a FAILED run newer than the records -> refused (decision 4)", not ok and "decision 4" in why, why.splitlines()[0] if why else "")
clear_logs()
open(os.path.join(os.environ["PRERUN_LOG_DIR"], "other.log"), "w", encoding="utf-8").write(
    "BGRUN START 2026-09-24 20:00:00 limit 5.0 min: py -u tools/recipes/stage_other.py\nBGRUN END rc=1 after 3s\n")
ok, why = SP.check_launch(LAUNCH)
gate("L4b another script's failure does not invalidate these records", ok, why)
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

print("---------- [M/R] guard_bash.py.new main()")
NEW = os.path.join(HOOKS, "guard_bash.py.new")
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
if nfail == 0:
    old = os.path.join(HOOKS, "guard_bash.py")
    m0 = hashlib.md5(open(old, "rb").read()).hexdigest()
    os.replace(NEW, old)
    m1 = hashlib.md5(open(old, "rb").read()).hexdigest()
    print("  FACT  INSTALL os.replace(guard_bash.py.new -> guard_bash.py): md5 {0} -> {1}".format(m0, m1))
else:
    print("  FACT  NOT INSTALLED - guard_bash.py unchanged, the .new stays for inspection")
print(P.result_line(P.make_result(npass, nfail, None if nfail == 0 else "selftest case failed")))
sys.exit(0 if nfail == 0 else 1)
