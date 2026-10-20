# ---
# labview: none
# hardware: motor
# ---
# hardware = imports tools/rig_session.py and tools/rig_recover.py (motor headers) but REPLACES their two device steps
# (motor_gate --session and the LabVIEW close) with in-process stubs: no port, no motion, no LabVIEW; the lock is a
# temporary directory, never the real G:\Codes\rig\rig_lock.json.
"""Self-test of rig_session.py (item 8) and rig_recover.py (item 11), user 2026-10-21, debate riglock-v6.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_rig_session.log -- py -u tools/bench/selftest_rig_session.py
"""
import json
import os
import subprocess
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
TMP = tempfile.mkdtemp(prefix="rig_session_test_")
os.environ["RIGLOCK_DIR"] = TMP                 # before riglock is imported
os.environ.pop("RIGLOCK_TOKEN", None)
sys.path.insert(0, TOOLS)
import rig_session as RS                                     # noqa: E402
import rig_recover as RR                                     # noqa: E402
rl = RS.riglock
RS.LOGDIR = TMP
RS.POLL_S = 1

ok = n = 0
calls = []
fail = {"start": False, "end": False}


def check(name, cond, detail=""):
    global ok, n
    n += 1
    ok += bool(cond)
    print("%s  %s %s" % ("PASS" if cond else "FAIL", name, detail), flush=True)


def fake_gate(which, env, log_path):
    calls.append((which, bool(env.get("RIGLOCK_TOKEN"))))
    open(log_path, "w").write("stub %s\n" % which)
    good = not fail[which]
    return good, ["SESSION %s %s" % (which.upper(), "OK" if good else "FAILED")]


def fake_close(log_path):
    calls.append(("labview", True))
    open(log_path, "w").write("stub close\n")
    return True, "stub: no LabVIEW.exe"


RS.gate_session, RS.close_labview = fake_gate, fake_close


def quiet(fn, argv):
    """The tools print their own lines and RESULT; keep them out of this test's output (bgrun reads RESULT lines)."""
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(argv)


def holder():
    return rl.status().get("holder")


def dead_pid():
    q = subprocess.Popen([sys.executable, "-c", "pass"])
    q.wait()
    return q.pid


NEEDS_TOKEN = [sys.executable, "-c", "import os,sys; sys.exit(0 if os.environ.get('RIGLOCK_TOKEN') else 9)"]
rl.set_state("assembled", "selftest", "init", init=True)

# ---- rig_session
calls.clear()
check("a normal job -> rc 0, token passed, start + labview + end, lock released",
      quiet(RS.main, ["--purpose", "t", "--", *NEEDS_TOKEN]) == 0
      and [c[0] for c in calls] == ["start", "labview", "end"] and all(c[1] for c in calls) and holder() is None)

other = rl.acquire("LabVIEW2Scr", "dev", pid=os.getpid())
calls.clear()
check("b another live holder -> rc 2, nothing touched", quiet(RS.main, ["--purpose", "t", "--", *NEEDS_TOKEN]) == 2
      and not calls)
rl.release(other)

rl.set_state("experiment", "selftest", "b")
calls.clear()
check("c experiment -> rc 2, nothing touched", quiet(RS.main, ["--purpose", "t", "--", *NEEDS_TOKEN]) == 2 and not calls)
rl.set_state("assembled", "selftest", "c")

fail["end"] = True
calls.clear()
check("d cleanup fails -> rc 3, lock KEPT", quiet(RS.main, ["--purpose", "t", "--", *NEEDS_TOKEN]) == 3
      and holder() is not None and holder()["name"] == "V6-chat")
fail["end"] = False
rl.release(holder()["token"])

fail["start"] = True
calls.clear()
check("e motor start fails -> command not run, cleanup run, lock released, rc 4",
      quiet(RS.main, ["--purpose", "t", "--", *NEEDS_TOKEN]) == 4 and [c[0] for c in calls] == ["start", "labview", "end"]
      and holder() is None)
fail["start"] = False

calls.clear()
threading.Timer(3.0, lambda: rl.set_state("experiment", "selftest", "user: 실험중 (mid-job)")).start()
t0 = time.time()
rc = quiet(RS.main, ["--purpose", "t", "--", sys.executable, "-c", "import time; time.sleep(90)"])
check("f experiment declared mid-job -> command killed, cleanup run, lock released, rc 4",
      rc == 4 and time.time() - t0 < 30 and [c[0] for c in calls] == ["start", "labview", "end"] and holder() is None,
      "%.0f s" % (time.time() - t0))
rl.set_state("assembled", "selftest", "f")

# ---- rig_recover
other = rl.acquire("LabVIEW2Scr", "dev", pid=os.getpid())
check("g live holder -> recovery refused (rc 2)", quiet(RR.main, ["--order", "user: 복구해"]) == 2)
rl.release(other)

rl.acquire("crashed", "x", pid=dead_pid())
rl.set_state("experiment", "selftest", "h")
calls.clear()
check("h stale holder during an experiment -> refused (rc 2), nothing touched",
      quiet(RR.main, ["--order", "user: 복구해"]) == 2 and not calls and holder()["name"] == "crashed")
rl.set_state("assembled", "selftest", "h")

fail["end"] = True
check("i a recovery check fails -> rc 3, lock kept in RECOVERING",
      quiet(RR.main, ["--order", "user: 복구해"]) == 3 and holder() is not None and holder().get("recovering"))
fail["end"] = False
# the V6-recover holder (this process) is alive -> a second recovery would be refused; finish it the manual way
tok = holder()["token"]
ev = os.path.join(TMP, "ev.log")
open(ev, "w").write("x")
rl.recovered(tok, {"devices_closed": ev, "limits_released": ev})
rl.release(tok)

rl.acquire("crashed", "x", pid=dead_pid())
calls.clear()
check("j stale holder, checks pass -> recovered + released (rc 0), log has 'recovered'",
      quiet(RR.main, ["--order", "user: 복구해"]) == 0 and holder() is None
      and '"recovered"' in open(os.path.join(TMP, "rig_lock.log"), encoding="utf-8").read())

print("NO MOTION COMMAND WAS SENT, NO PORT WAS OPENED AND LabVIEW WAS NOT TOUCHED BY THIS RUN.")
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if ok == n else "FAIL",
                              "gates": {"pass": ok, "fail": n - ok}, "first_fail": None, "artefacts": []}))
sys.exit(0 if ok == n else 1)
