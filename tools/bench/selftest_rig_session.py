# ---
# labview: none
# hardware: motor
# ---
# hardware = imports tools/rig_session.py and tools/rig_recover.py (motor headers) but REPLACES their two device steps
# (motor_gate --session and the LabVIEW close) with in-process stubs: no port, no motion, no LabVIEW; the lock is a
# temporary directory, never the real G:\Codes\rig\rig_lock.json; STATUS.md is a temporary copy with only `rig-state:`.
"""Self-test of rig_session.py (item 8) and rig_recover.py (item 11), user 2026-10-21, debate riglock-v6; plus the
fixes approved 2026-10-21 ("승인", G:\\Codes\\rig\\proposals\\2026-10-21-labview2scr-decisions.md): B1 (a failing
permitted() still kills the whole job tree - grandchildren and orphans - before cleanup), B2 (STATUS.md vs rig_lock.json
disagree -> refused), B3 (limits released only after the job is gone; "CLEANUP COMPLETE" notice after a mid-job
experiment), B4 (refused while LabVIEW runs; only our own LabVIEW counts as ours), A3 (no token from status()).
    py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_rig_session.log -- py -u tools/bench/selftest_rig_session.py
"""
import contextlib
import io
import json
import os
import signal
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
STATUS_TMP = os.path.join(TMP, "STATUS.md")
RS.motor_gate.STATUS_PATH = STATUS_TMP                       # B2 reads this copy, never the real STATUS.md

ok = n = 0
calls = []
fail = {"start": False, "end": False}
probe = {"file": None, "pids": [], "alive_at_end": None}


def check(name, cond, detail=""):
    global ok, n
    n += 1
    ok += bool(cond)
    print("%s  %s %s" % ("PASS" if cond else "FAIL", name, detail), flush=True)


def fake_gate(which, env, log_path):
    calls.append((which, bool(env.get("RIGLOCK_TOKEN"))))
    if which == "end" and probe["file"]:              # the job's pids, read at the moment the limits are released
        probe["pids"] = read_pids(probe["file"], 2, 5)
        probe["alive_at_end"] = [p for p in probe["pids"] if rl.pid_alive(p)]
    open(log_path, "w").write("stub %s\n" % which)
    good = not fail[which]
    return good, ["SESSION %s %s" % (which.upper(), "OK" if good else "FAILED")]


def fake_close(log_path, *a):
    calls.append(("labview", True))
    open(log_path, "w").write("stub close\n")
    return True, "stub: no LabVIEW.exe"


RS.gate_session, RS.close_labview = fake_gate, fake_close
apps = {"now": {}}
RS.running_apps = lambda: apps["now"]


def quiet(fn, argv, out=None):
    """The tools print their own lines and RESULT; keep them out of this test's output (bgrun reads RESULT lines)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = fn(argv)
    if out is not None:
        out.append(buf.getvalue())
    return rc


def both(state, note):
    """The chat records the user's word in BOTH places (riglock set-state + STATUS.md rig-state)."""
    rl.set_state(state, "selftest", note)
    with open(STATUS_TMP, "w", encoding="utf-8") as f:
        f.write("rig-state: %s\n" % state)


def holder():
    return rl.status().get("holder")


def held_token():
    """A3: status() no longer hands out the token - the test reads its own temp lock file instead."""
    with open(os.path.join(TMP, "rig_lock.json"), encoding="utf-8") as f:
        return json.load(f)["holder"]["token"]


def dead_pid():
    q = subprocess.Popen([sys.executable, "-c", "pass"])
    q.wait()
    return q.pid


def read_pids(path, k, wait_s=15):
    t_end = time.time() + wait_s
    while time.time() < t_end:
        try:
            v = [int(x) for x in open(path).read().split()]
            if len(v) >= k:
                return v
        except (OSError, ValueError):
            pass
        time.sleep(0.2)
    return []


NEEDS_TOKEN = [sys.executable, "-c", "import os,sys; sys.exit(0 if os.environ.get('RIGLOCK_TOKEN') else 9)"]
rl.set_state("assembled", "selftest", "init", init=True)
both("assembled", "init")

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

both("experiment", "b")
calls.clear()
check("c experiment -> rc 2, nothing touched", quiet(RS.main, ["--purpose", "t", "--", *NEEDS_TOKEN]) == 2 and not calls)
both("assembled", "c")

fail["end"] = True
calls.clear()
check("d cleanup fails -> rc 3, lock KEPT", quiet(RS.main, ["--purpose", "t", "--", *NEEDS_TOKEN]) == 3
      and holder() is not None and holder()["name"] == "V6-chat")
fail["end"] = False
rl.release(held_token())

fail["start"] = True
calls.clear()
check("e motor start fails -> command not run, cleanup run, lock released, rc 4",
      quiet(RS.main, ["--purpose", "t", "--", *NEEDS_TOKEN]) == 4 and [c[0] for c in calls] == ["start", "labview", "end"]
      and holder() is None)
fail["start"] = False

calls.clear()
threading.Timer(3.0, lambda: rl.set_state("experiment", "selftest", "user: 실험중 (mid-job)")).start()
t0 = time.time()
out = []
rc = quiet(RS.main, ["--purpose", "t", "--", sys.executable, "-c", "import time; time.sleep(90)"], out)
check("f experiment declared mid-job -> command killed, cleanup run, lock released, rc 4, CLEANUP COMPLETE notice (B3)",
      rc == 4 and time.time() - t0 < 30 and [c[0] for c in calls] == ["start", "labview", "end"] and holder() is None
      and "CLEANUP COMPLETE" in out[0] and '"notice": "CLEANUP COMPLETE"' in out[0], "%.0f s" % (time.time() - t0))
both("assembled", "f")

# ---- B2: the two records of the rig state disagree -> refused before anything is touched
with open(STATUS_TMP, "w", encoding="utf-8") as f:
    f.write("rig-state: 실험중\n")
calls.clear()
check("k B2 STATUS.md experiment, rig_lock.json assembled -> rc 2, nothing touched, no holder",
      quiet(RS.main, ["--purpose", "t", "--", *NEEDS_TOKEN]) == 2 and not calls and holder() is None)
with open(STATUS_TMP, "w", encoding="utf-8") as f:
    f.write("no machine key here\n")
check("k2 B2 STATUS.md without rig-state -> rc 2, nothing touched",
      quiet(RS.main, ["--purpose", "t", "--", *NEEDS_TOKEN]) == 2 and not calls and holder() is None)
both("assembled", "k")
tok = rl.acquire("selftest", "gate", pid=os.getpid())
os.environ["RIGLOCK_TOKEN"] = tok
ok_same = RS.motor_gate.rig_lock_ok("start", status_text="rig-state: 조립\n")[0]
ok_diff = RS.motor_gate.rig_lock_ok("start", status_text="rig-state: 분해\n")[0]
ok_end = RS.motor_gate.rig_lock_ok("end", status_text="rig-state: 분해\n")[0]
os.environ.pop("RIGLOCK_TOKEN", None)
rl.release(tok)
check("k3 B2 in motor_gate: agree -> start ok; disagree -> start refused; cleanup (end) not gated",
      ok_same and not ok_diff and ok_end)

# ---- B4: the experiment software is already running -> refused at start
apps["now"] = {"LabVIEW.exe": [4242]}
calls.clear()
check("l B4 LabVIEW already running -> rc 2, nothing touched", quiet(RS.main, ["--purpose", "t", "--", *NEEDS_TOKEN]) == 2
      and not calls and holder() is None)
apps["now"] = None
check("l2 B4 process list unreadable -> rc 2 (unsure = refuse)",
      quiet(RS.main, ["--purpose", "t", "--", *NEEDS_TOKEN]) == 2 and not calls and holder() is None)
apps["now"] = {}

# B4 ownership: started after the job began AND (job member OR COM /Automation); anything else is foreign
sleeper = [sys.executable, "-c", "import time; time.sleep(60)"]
old = subprocess.Popen(sleeper)
time.sleep(0.5)
t_job = RS._filetime_now()
time.sleep(0.5)
new_com, new_hand, new_member = (subprocess.Popen(sleeper) for _ in range(3))
real_cl = RS._cmdlines
RS._cmdlines = lambda image: {old.pid: "LabVIEW.exe /Automation", new_com.pid: "LabVIEW.exe /Automation",
                              new_hand.pid: "LabVIEW.exe C:\\x\\exp.vi", new_member.pid: "LabVIEW.exe"}
own, foreign = RS.own_labview([old.pid, new_com.pid, new_hand.pid, new_member.pid], t_job, [new_member.pid])
RS._cmdlines = real_cl
for q in (old, new_com, new_hand, new_member):
    q.kill()
    q.wait()
check("m B4 own = new COM-launched + new job member; foreign = older one + new hand-started",
      sorted(own) == sorted([new_com.pid, new_member.pid]) and sorted(foreign) == sorted([old.pid, new_hand.pid]),
      "own %s foreign %s" % (own, foreign))

# B4 for the cycle hooks (follow-up 2026-10-22): a LIVE descendant of the lock holder's process (root_pid) is own; an
# orphan whose parent already exited (the `Start-Process LabVIEW.exe` shape) is not provable -> foreign. Real child
# processes of this test (python sleepers named as LabVIEW by a faked command-line read), nothing is killed by RS.
t_job = RS._filetime_now()
time.sleep(0.5)
kid = subprocess.Popen(sleeper)
opid = os.path.join(TMP, "orphan_pid.txt")
mid = subprocess.Popen([sys.executable, "-c",
                        "import subprocess,sys\n"
                        "g = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'], "
                        "creationflags=0x00000008|0x00000200)\n"
                        "open(r'%s','w').write(str(g.pid))\n" % opid])
mid.wait()
orphan = read_pids(opid, 1)[0]
RS._cmdlines = lambda image: {kid.pid: "LabVIEW.exe", orphan: "LabVIEW.exe"}
own, foreign = RS.own_labview([kid.pid, orphan], t_job, [], root_pid=os.getpid())
own_other, _f = RS.own_labview([kid.pid], t_job, [], root_pid=dead_pid())
RS._cmdlines = real_cl
kid.kill()
kid.wait()
os.kill(orphan, signal.SIGTERM)                  # this test's own python sleeper (TerminateProcess on Windows)
ft = RS.iso_to_filetime("2026-10-22T10:00:00+09:00")
check("m2 B4 live descendant of root_pid = own; orphan (parent gone) = foreign; another root = not own",
      own == [kid.pid] and foreign == [orphan] and own_other == [],
      "own %s foreign %s other %s" % (own, foreign, own_other))
check("m3 iso_to_filetime: riglock `since` -> FILETIME (offset honoured; 1970-01-01Z = 116444736000000000)",
      ft == RS.iso_to_filetime("2026-10-22T01:00:00+00:00")
      and RS.iso_to_filetime("1970-01-01T00:00:00+00:00") == 116444736000000000
      and RS.iso_to_filetime(None) is None, "ft %s" % ft)

# ---- B1: permitted() raising (stuck mutex) must still kill the child AND its grandchild before the cleanup
pidfile = os.path.join(TMP, "tree_pids.txt")
TREE = [sys.executable, "-c",
        "import subprocess,sys,time,os\n"
        "g = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(120)'])\n"
        "open(r'%s','w').write('%%d %%d' %% (os.getpid(), g.pid))\n"
        "time.sleep(120)\n" % pidfile]
real_permitted = rl.permitted


def boom(*a, **k):
    raise TimeoutError("rig_lock.mutex busy for 10 s (simulated)")


rl.permitted = boom
calls.clear()
probe.update(file=pidfile, pids=[], alive_at_end=None)
t0 = time.time()
out = []
rc = quiet(RS.main, ["--purpose", "t", "--", *TREE], out)
rl.permitted = real_permitted
pids = probe["pids"]
check("n B1 permitted() raises TimeoutError -> child + grandchild killed BEFORE limits release, cleanup run, "
      "lock released, rc 4, RESULT line",
      rc == 4 and len(pids) == 2 and probe["alive_at_end"] == [] and not any(rl.pid_alive(p) for p in pids)
      and [c[0] for c in calls] == ["start", "labview", "end"] and holder() is None
      and "rig lock check failed (TimeoutError" in out[0] and "RESULT " in out[0],
      "pids %s, %.0f s" % (pids, time.time() - t0))
os.remove(pidfile)
probe["file"] = None

# B1: an ORPHAN (the child starts a detached grandchild and exits at once) is killed before the limits are released
ORPHAN = [sys.executable, "-c",
          "import subprocess,sys,os\n"
          "g = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(120)'], creationflags=0x00000008|0x00000200)\n"
          "open(r'%s','w').write('%%d %%d' %% (os.getpid(), g.pid))\n" % pidfile]
calls.clear()
probe.update(file=pidfile, pids=[], alive_at_end=None)
out = []
rc = quiet(RS.main, ["--purpose", "t", "--", *ORPHAN], out)
pids = probe["pids"]
check("o B1 orphaned grandchild (parent already exited, taskkill /T misses it) -> killed before limits release, rc 0",
      rc == 0 and len(pids) == 2 and probe["alive_at_end"] == [] and not any(rl.pid_alive(p) for p in pids)
      and holder() is None, "pids %s" % pids)
os.remove(pidfile)
probe["file"] = None

# B1/B3: the job cannot be verified gone -> limits NOT released, lock KEPT, rc 3
real_kill = RS.JobTree.kill
RS.JobTree.kill = lambda self, wait_s=0: (False, [1], [1])
calls.clear()
rc = quiet(RS.main, ["--purpose", "t", "--", *NEEDS_TOKEN])
RS.JobTree.kill = real_kill
check("p B3 job not verified gone -> limits NOT released (no 'end'), lock KEPT, rc 3",
      rc == 3 and "end" not in [c[0] for c in calls] and holder() is not None)
rl.release(held_token())

# B1: the guaranteed escape - the job starts SUSPENDED and joins the job before its first instruction
calls.clear()
check("q job membership: NEEDS_TOKEN job ran inside the job and passed", quiet(RS.main, ["--purpose", "t", "--",
                                                                                     *NEEDS_TOKEN]) == 0)

# ---- rig_recover
other = rl.acquire("LabVIEW2Scr", "dev", pid=os.getpid())
check("g live holder -> recovery refused (rc 2)", quiet(RR.main, ["--order", "user: 복구해"]) == 2)
rl.release(other)

rl.acquire("crashed", "x", pid=dead_pid())
both("experiment", "h")
calls.clear()
check("h stale holder during an experiment -> refused (rc 2), nothing touched",
      quiet(RR.main, ["--order", "user: 복구해"]) == 2 and not calls and holder()["name"] == "crashed")
both("assembled", "h")

fail["end"] = True
check("i a recovery check fails -> rc 3, lock kept in RECOVERING",
      quiet(RR.main, ["--order", "user: 복구해"]) == 3 and holder() is not None and holder().get("recovering"))
fail["end"] = False
# the V6-recover holder (this process) is alive -> a second recovery would be refused; finish it the manual way
tok = held_token()
ev = os.path.join(TMP, "ev.log")
open(ev, "w").write("x")
rl.recovered(tok, {"devices_closed": ev, "limits_released": ev})
rl.release(tok)

rl.acquire("crashed", "x", pid=dead_pid())
calls.clear()
out = []
check("j stale holder, checks pass -> recovered + released (rc 0), log has 'recovered', no token in the RESULT (A3)",
      quiet(RR.main, ["--order", "user: 복구해"], out) == 0 and holder() is None
      and '"recovered"' in open(os.path.join(TMP, "rig_lock.log"), encoding="utf-8").read()
      and '"token"' not in out[0])

print("NO MOTION COMMAND WAS SENT, NO PORT WAS OPENED AND LabVIEW WAS NOT TOUCHED BY THIS RUN.")
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if ok == n else "FAIL",
                              "gates": {"pass": ok, "fail": n - ok}, "first_fail": None, "artefacts": []}))
sys.exit(0 if ok == n else 1)
