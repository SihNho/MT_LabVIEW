"""Self-test of the SCRATCH-VI gate in stage_prerun.check_launch (user 2026-09-27, card chat-N4). No LabVIEW.
Existing checked first: stage_prerun.check_cap / last_failed_run_after (same log-segment reading via protocol.segments),
selftest_cycle_runner_ladder.py (gate/RESULT pattern).
PREDICTION (7 gates):
  S1 last two runs of stage_x (v1, v2: same key) failed in gscript.wire_terminals (traceback), no scratch record -> REFUSED
  S2 same two failures + a scratch_verify PASS record for gscript.wire_terminals NEWER than the 2nd failure -> allowed
  S3 a PASS record OLDER than the 2nd failure, and a newer record with status FAIL -> still REFUSED
  S4 two failures in DIFFERENT functions -> allowed; last run PASSED after two same-function failures -> allowed
  E1 extraction: STEP-DIFF line -> stagexec.op:<kind>; Op VI in RESULT first_fail -> op:<Name>; a fleet traceback
     frame wins over a STEP-DIFF line; nothing recognisable -> None (no gate)
  E2 a `stage_prerun.py --dry` segment naming the stage is not counted as a run
  W1 _check_units calls check_scratch (the gate is wired into check_launch)
Usage: py tools/bench/selftest_scratch_verify.py"""
import inspect
import json
import os
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOGS = tempfile.mkdtemp(prefix="svlogs_")
SV = tempfile.mkdtemp(prefix="svrec_")
os.environ["PRERUN_LOG_DIR"] = LOGS
os.environ["SCRATCH_VERIFY_DIR"] = SV
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402
import stage_prerun as SP  # noqa: E402

gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("%s %s %s" % ("PASS" if ok else "**FAIL", label, detail))


def stamp(t):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))


def tb(func, module="gscript"):
    return ('Traceback (most recent call last):\n  File "C:\\x\\tools\\recipes\\stage_x.py", line 40, in main\n'
            '  File "C:\\x\\tools\\stagekit.py", line 1270, in run\n'
            '  File "C:\\x\\tools\\%s.py", line 812, in %s\nRuntimeError: boom\n' % (module, func))


def run_seg(t, script, ok, body=""):
    res = protocol.result_line(protocol.make_result(3, 0 if ok else 1, None if ok else "RuntimeError: boom"))
    return ("BGRUN START %s limit 10.0 min: py -u tools/recipes/%s\n%s%s\nBGRUN END rc=%d after 5s\n"
            % (stamp(t), script, body, res, 0 if ok else 1))


def fresh(segs, name="stage_x.log"):
    for fn in os.listdir(LOGS):
        os.remove(os.path.join(LOGS, fn))
    for fn in os.listdir(SV):
        os.remove(os.path.join(SV, fn))
    with open(os.path.join(LOGS, name), "w", encoding="utf-8") as f:
        f.write("".join(segs))


def scratch(function, status, t):
    with open(os.path.join(SV, "%s_%d.json" % (function.replace(":", "_"), int(t))), "w", encoding="utf-8") as f:
        json.dump({"function": function, "status": status, "t": t}, f)


now = time.time()
t1, t2 = now - 3600, now - 1800
two_same = [run_seg(t1, "stage_x_v1.py", False, tb("wire_terminals")), run_seg(t2, "stage_x_v2.py", False, tb("wire_terminals"))]

fresh(two_same)
ok, why = SP.check_scratch("tools/recipes/stage_x_v3.py")
gate("S1", not ok and "gscript.wire_terminals" in why, why[:160])

scratch("gscript.wire_terminals", "PASS", now - 60)
ok2, why2 = SP.check_scratch("tools/recipes/stage_x_v3.py")
gate("S2", ok2, why2[:160])

fresh(two_same)
scratch("gscript.wire_terminals", "PASS", t2 - 60)
scratch("gscript.wire_terminals", "FAIL", now - 60)
ok3, why3 = SP.check_scratch("tools/recipes/stage_x_v3.py")
gate("S3", not ok3, why3[:120])

fresh([run_seg(t1, "stage_x_v1.py", False, tb("wire_terminals")), run_seg(t2, "stage_x_v2.py", False, tb("create_node"))])
ok4a, _ = SP.check_scratch("tools/recipes/stage_x_v3.py")
fresh(two_same + [run_seg(now - 600, "stage_x_v2.py", True)])
ok4b, _ = SP.check_scratch("tools/recipes/stage_x_v3.py")
gate("S4", ok4a and ok4b, "different=%s passed-last=%s" % (ok4a, ok4b))

sd = "  FAIL E1 every real op's graph == its simulated step  STEP-DIFF after real op 7 (tunnel, plan actions [9]): {}\n"
opvi = "BGRUN START x limit 1 min: y\n" + protocol.result_line(protocol.make_result(0, 1, "OpWireConnect.vi returned error 1057"))
e1 = (SP.failure_function(sd), SP.failure_function(opvi), SP.failure_function(tb("move_in", "stagekit") + sd),
      SP.failure_function("no traceback, no diff\n"))
gate("E1", e1 == ("stagexec.op:tunnel", "op:OpWireConnect", "stagekit.move_in", None), e1)

dryseg = ("BGRUN START %s limit 5.0 min: py tools/stage_prerun.py --dry tools/recipes/stage_x_v2.py\n%s"
          "BGRUN END rc=1 after 2s\n" % (stamp(now - 300), tb("wire_terminals")))
fresh([run_seg(t1, "stage_x_v1.py", False, tb("wire_terminals")), run_seg(t2, "stage_x_v2.py", True), dryseg])
runs = SP.stage_run_segments("stage_x.py")
okd, _ = SP.check_scratch("tools/recipes/stage_x_v3.py")
gate("E2", len(runs) == 2 and okd, runs)

gate("W1", "check_scratch(" in inspect.getsource(SP._check_units))

n_pass = sum(ok for _, ok in gates)
first = next((l for l, ok in gates if not ok), None)
print("%d/%d PASS" % (n_pass, len(gates)))
print(protocol.result_line(protocol.make_result(n_pass, len(gates) - n_pass, first)))
sys.exit(0 if first is None else 1)
