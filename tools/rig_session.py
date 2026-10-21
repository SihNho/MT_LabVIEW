# ---
# labview: read
# hardware: motor
# ---
# labview = close-only at the end (its OWN LabVIEW only: COM Quit / taskkill by pid, tasklist); never opens or edits.
# hardware = PI + ASI limits through tools/motor_gate.py --session start|end only; any motion inside the wrapped command
# goes through motor_gate.py itself (this file sends nothing to a device).
"""rig_session.py - one rig job OUTSIDE the lean queue (chat checks, one-off cards) under the shared rig lock
(user 2026-10-21, debate riglock-v6 item 8; G:\\Codes\\rig\\riglock.py; fixes B1-B4 approved 2026-10-21 "승인",
G:\\Codes\\rig\\proposals\\2026-10-21-labview2scr-decisions.md):

  0. refuse before touching anything: STATUS.md `rig-state:` and rig_lock.json disagree (B2), or LabVIEW (the
     experiment software) is already running (B4 - it may be a user's experiment)
  1. acquire the lock (holder V6-chat, this process's pid) - refused: experiment / another live holder / stale / error
  2. motor_gate --session start (limits set, PI reference move, readback)        [skipped with --no-motor-session]
  3. run the command with RIGLOCK_TOKEN in its environment inside a Windows JOB OBJECT (B1: every process it starts
     belongs to the job, also a grandchild whose parent already exited - taskkill /T misses those); every 30 s ask
     riglock.permitted - experiment declared, lock lost, or the check itself failing (TimeoutError, any exception)
     stops the command
  4. cleanup, ALWAYS, also after a kill or a failure:
     a. every process of the job is killed and VERIFIED gone (B1/B3); not verified -> limits NOT released, lock KEPT
     b. LabVIEW closed - only the LabVIEW this job started (B4: started after the job began AND launched by COM
        `/Automation` or a member of the job); any other LabVIEW is left alone and the cleanup is reported INCOMPLETE
     c. motor_gate --session end (limits released + readback) - the rig back at its initial condition (user item 9)
  5. cleanup verified -> release the lock; when an experiment was declared mid-job a "CLEANUP COMPLETE" notice follows
     (B3); cleanup FAILED or incomplete -> the lock is KEPT (exit 3) so the next user sees it

The guards still apply: the wrapped command is a normal command (guard_bash checks the Bash line that contains it), and
nothing here bypasses motor_gate. Run it like any LabVIEW / motor job, backgrounded through bgrun:
  py tools/bgrun.py --max-min 20 --log tools/bench/<name>.log -- py -u tools/rig_session.py --purpose "<why>" --max-min 15 -- <command ...>
Exit: 0 ok; 2 refused (nothing touched); 3 cleanup failed or incomplete (lock kept); 4 command failed or was stopped
(cleanup ok, lock released). Last line: RESULT {...}.
"""
import argparse
import ctypes
import json
import os
import subprocess
import sys
import time
from ctypes import wintypes

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STATUS = os.path.join(ROOT, "STATUS.md")
LOGDIR = os.path.join(HERE, "bench")
sys.path.insert(0, HERE)
import motor_gate                                            # noqa: E402  (RIG_DIR, rig_lock_ok, rig_state_agree)
sys.path.insert(0, motor_gate.RIG_DIR)
import riglock                                               # noqa: E402

POLL_S = 30
JOB_GONE_S = 30.0         # after TerminateJobObject, wait this long for every member to be gone
# The experiment software: a running copy at start means the rig may be in a user's hands (B4 / CR-5 final). The
# LabVIEW2Scr experiment app joins this list when it exists.
EXPERIMENT_APPS = ("LabVIEW.exe",)


def say(line):
    print("%s | %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), line), flush=True)


def gate_session(which, env, log_path):
    with open(log_path, "w", encoding="utf-8") as f:
        rc = subprocess.call([sys.executable, os.path.join(HERE, "motor_gate.py"), "--session", which],
                             cwd=ROOT, env=env, stdout=f, stderr=subprocess.STDOUT, timeout=600)
    tail = [ln.strip() for ln in open(log_path, encoding="utf-8", errors="replace") if ln.strip()][-2:]
    return rc == 0 and any(("SESSION %s OK" % which.upper()) in t for t in tail), tail


# ---------------------------------------------------------------- B1: the job object
_k32 = ctypes.WinDLL("kernel32", use_last_error=True) if os.name == "nt" else None
CREATE_SUSPENDED = 0x00000004
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000


class _BasicLimit(ctypes.Structure):
    _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64),
                ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD), ("SchedulingClass", wintypes.DWORD)]


class _ExtendedLimit(ctypes.Structure):
    _fields_ = [("BasicLimitInformation", _BasicLimit), ("IoInfo", ctypes.c_uint64 * 6),
                ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]


class JobTree:
    """The wrapped command and EVERY process it starts, held in one Windows job object (B1, 2026-10-21).
    The command starts SUSPENDED, joins the job, then resumes - no grandchild can be born outside it. A job does not
    allow breakaway, so `bgrun --detach` inside the command stays in it too. KILL_ON_JOB_CLOSE: if this wrapper itself
    dies, Windows kills the members when the handle closes (the lock then goes stale -> rig_recover.py)."""

    def __init__(self):
        k = _k32
        k.CreateJobObjectW.restype = wintypes.HANDLE
        self.h = k.CreateJobObjectW(None, None)
        if not self.h:
            raise OSError("CreateJobObject failed (error %d)" % ctypes.get_last_error())
        info = _ExtendedLimit()
        info.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not k.SetInformationJobObject(wintypes.HANDLE(self.h), 9, ctypes.byref(info), ctypes.sizeof(info)):
            raise OSError("SetInformationJobObject failed (error %d)" % ctypes.get_last_error())

    def start(self, cmd, **kw):
        p = subprocess.Popen(cmd, creationflags=CREATE_SUSPENDED, **kw)
        if not _k32.AssignProcessToJobObject(wintypes.HANDLE(self.h), wintypes.HANDLE(int(p._handle))):
            err = ctypes.get_last_error()
            _k32.TerminateProcess(wintypes.HANDLE(int(p._handle)), 1)
            p.wait(30)
            raise OSError("AssignProcessToJobObject failed (error %d) - the command was never resumed" % err)
        ntdll = ctypes.WinDLL("ntdll")
        if ntdll.NtResumeProcess(wintypes.HANDLE(int(p._handle))) != 0:
            _k32.TerminateJobObject(wintypes.HANDLE(self.h), 1)
            raise OSError("NtResumeProcess failed - the job was terminated")
        return p

    def pids(self):
        """The pids still in the job ([] = every process it ever held is gone)."""
        n = 1024

        class _List(ctypes.Structure):
            _fields_ = [("Assigned", wintypes.DWORD), ("InList", wintypes.DWORD), ("Ids", ctypes.c_size_t * n)]
        lst = _List()
        if not _k32.QueryInformationJobObject(wintypes.HANDLE(self.h), 3, ctypes.byref(lst), ctypes.sizeof(lst), None):
            raise OSError("QueryInformationJobObject failed (error %d)" % ctypes.get_last_error())
        return [int(lst.Ids[i]) for i in range(lst.InList)]

    def kill(self, wait_s=JOB_GONE_S):
        """Terminate every member and VERIFY the job is empty. -> (gone, pids_before, pids_left)."""
        try:
            before = self.pids()
        except OSError:
            before = None
        _k32.TerminateJobObject(wintypes.HANDLE(self.h), 1)
        t0 = time.time()
        while True:
            try:
                left = self.pids()
            except OSError:
                left = None
            if left == []:
                return True, before, []
            if time.time() - t0 >= wait_s:
                return False, before, left
            time.sleep(0.2)

    def close(self):
        if self.h:
            _k32.CloseHandle(wintypes.HANDLE(self.h))
            self.h = None


def kill_tree(job):
    """Kept name (debate riglock-cr1): the whole tree is the job, grandchildren and orphans included."""
    return job.kill()


# ---------------------------------------------------------------- B4: whose LabVIEW is it?
def _filetime_now():
    ft = wintypes.FILETIME()
    _k32.GetSystemTimeAsFileTime(ctypes.byref(ft))
    return (ft.dwHighDateTime << 32) | ft.dwLowDateTime


def running_apps():
    """{image: [pid, ...]} of the experiment software running now; None when tasklist cannot be read (unsure)."""
    out = {}
    for image in EXPERIMENT_APPS:
        try:
            r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq %s" % image, "/FO", "CSV", "/NH"],
                               capture_output=True, text=True, timeout=30)
        except Exception:                                    # noqa: BLE001
            return None
        if r.returncode != 0:
            return None
        pids = [int(ln.split('","')[1]) for ln in (r.stdout or "").splitlines()
                if ln.lower().startswith('"%s","' % image.lower())]
        if pids:
            out[image] = pids
    return out


def _cmdlines(image):
    """{pid: command line} for one image name (CIM); {} when it cannot be read - then nothing counts as our own."""
    ps = ("Get-CimInstance Win32_Process -Filter \"Name='%s'\" | ForEach-Object { '{0}|{1}' -f $_.ProcessId, "
          "$_.CommandLine }" % image)
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=60)
    except Exception:                                        # noqa: BLE001
        return {}
    res = {}
    for ln in (r.stdout or "").splitlines():
        pid, _, cl = ln.partition("|")
        if pid.strip().isdigit():
            res[int(pid.strip())] = cl
    return res


def iso_to_filetime(s):
    """riglock's `since` (ISO time with offset, riglock._now) -> Windows FILETIME, comparable with proc_created().
    None when unreadable."""
    import datetime
    try:
        return int((datetime.datetime.fromisoformat(s).timestamp() + 11644473600) * 10 ** 7)
    except (TypeError, ValueError):
        return None


def _parents():
    """{pid: parent pid} of every running process (CIM); {} when it cannot be read - then no descent is proven."""
    ps = "Get-CimInstance Win32_Process | ForEach-Object { '{0}|{1}' -f $_.ProcessId, $_.ParentProcessId }"
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=60)
    except Exception:                                        # noqa: BLE001
        return {}
    res = {}
    for ln in (r.stdout or "").splitlines():
        a, _, b = ln.strip().partition("|")
        if a.isdigit() and b.isdigit():
            res[int(a)] = int(b)
    return res


def descends_from(pid, root_pid, parents, max_depth=32):
    """True when `pid`'s LIVE parent chain reaches root_pid. Each parent must be alive and created no later than its
    child (a reused pid number is not a parent); a dead link ends the chain -> False (not proven)."""
    if not root_pid:
        return False
    child, child_t = pid, riglock.proc_created(pid)
    for _ in range(max_depth):
        par = parents.get(child)
        if not par or par == child or child_t is None:
            return False
        par_t = riglock.proc_created(par)
        if par_t is None or par_t > child_t:
            return False
        if par == root_pid:
            return True
        child, child_t = par, par_t
    return False


def own_labview(pids, t0, members, root_pid=None):
    """Split running LabVIEW pids into (own, foreign). OWN = created after the job began (t0, FILETIME) AND either a
    member of the job, launched by COM (`/Automation`, the LabVIEW.Application LocalServer32 command line), or (cycle
    hooks, follow-up 2026-10-22) a live descendant of root_pid, the lock holder's process. A pid alone is not proof
    (debate l2s-conflict-01), so anything not proven ours is foreign and left alone."""
    cls = _cmdlines("LabVIEW.exe")
    parents = _parents() if root_pid else {}
    own, foreign = [], []
    for pid in pids:
        created = riglock.proc_created(pid)
        new = created is not None and created > t0
        com = "/automation" in (cls.get(pid) or "").lower()
        mine = new and (pid in (members or ()) or com or descends_from(pid, root_pid, parents))
        (own if mine else foreign).append(pid)
    return own, foreign


def close_labview(log_path, t0=None, members=None, root_pid=None, who="rig_session"):
    """Close the LabVIEW this job started, verified gone (B4). -> (ok, why); ok False = failed OR incomplete (a
    LabVIEW that is not provably ours is still running - it may be a user's, so it is never touched). The verdict
    starts with OK: / FAIL: (own LabVIEW not gone, or unreadable) / INCOMPLETE: (own gone, a foreign one left)."""
    import cycle_runner as CR
    pids = CR._lv_pids()
    if pids is None:
        verdict, ok = "FAIL: tasklist could not be read", False
    elif not pids:
        verdict, ok = "OK: no LabVIEW.exe was running", True
    else:
        own, foreign = own_labview(pids, t0 or 0, members, root_pid)
        steps = []

        def own_alive():                                 # unreadable tasklist = assume still alive
            now = CR._lv_pids()
            return sorted(set(own) & set(own if now is None else now))
        if own and not foreign:                          # only ours exists -> COM Quit reaches ours; then force
            steps.append(CR._lv_quit_graceful(CR.LV_GRACE_S))
        if own:
            t_end = time.time() + CR.LV_GRACE_S
            while time.time() < t_end and own_alive():
                time.sleep(2)
            for pid in own_alive():
                r = subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True, text=True, timeout=30)
                steps.append("taskkill %d rc=%d" % (pid, r.returncode))
            t_end = time.time() + CR.LV_FORCE_WAIT_S
            while time.time() < t_end and own_alive():
                time.sleep(2)
        own_left = own_alive()
        if own_left:
            verdict, ok = "FAIL: own LabVIEW still running (pids %s; %s)" % (own_left, "; ".join(steps)), False
        elif foreign:
            verdict, ok = ("INCOMPLETE: LabVIEW pids %s are not provably this job's (maybe a user's) - left running, "
                           "lock kept for the user to look (own closed: %s; %s)" % (foreign, own, "; ".join(steps))), False
        else:
            verdict, ok = "OK: own LabVIEW closed (pids %s; %s)" % (own, "; ".join(steps)), True
    CR.log_line(log_path, "LABVIEW-CLOSE | %s | %s | %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), who, verdict))
    return ok, verdict


def _step(fn, *a):
    """A cleanup step that raises counts as FAILED (the lock is then kept), never as an escape past the cleanup."""
    try:
        return fn(*a)
    except Exception as e:                                   # noqa: BLE001
        return False, ["%s: %s" % (type(e).__name__, e)]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--purpose", required=True)
    ap.add_argument("--max-min", type=float, default=15.0)
    ap.add_argument("--no-motor-session", action="store_true", help="camera-only job: no motor_gate session")
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args(argv)
    cmd = a.cmd[1:] if a.cmd[:1] == ["--"] else a.cmd
    if not cmd:
        ap.error("no command after --")
    res = {"purpose": a.purpose, "cmd": " ".join(cmd)[:200]}
    stamp = time.strftime("%Y%m%d_%H%M%S")

    def refuse(why):
        res.update(status="REFUSED", why=why)
        say("refused - nothing touched: %s" % why)
        print("RESULT " + json.dumps(res, ensure_ascii=False))
        return 2

    agree, why = motor_gate.rig_state_agree()                # B2: the two records of the rig state must agree
    if not agree:
        return refuse(why)
    apps = running_apps()                                    # B4: the experiment software must not be running
    if apps is None:
        return refuse("cannot read the process list - unsure whether LabVIEW (a user's experiment?) is running")
    if apps:
        return refuse("experiment software already running %s - it may be a user's; this job does not start "
                      "(close it yourself if it is yours)" % apps)
    try:
        token = riglock.acquire("V6-chat", a.purpose, pid=os.getpid())
    except (riglock.Refused, OSError, RuntimeError, TimeoutError) as e:
        return refuse("RIGLOCK: %s" % e)
    say("RIGLOCK acquired (V6-chat, pid %d)" % os.getpid())
    env = dict(os.environ, RIGLOCK_TOKEN=token)
    cmd_rc, stopped, started, experiment, job, t0, members = None, "", False, False, None, _filetime_now(), []

    try:
        if not a.no_motor_session:
            started = True
            ok, tail = gate_session("start", env, os.path.join(LOGDIR, "rig_session_start_%s.log" % stamp))
            say("motor session start: %s %s" % ("OK" if ok else "FAILED", " / ".join(tail)))
            if not ok:
                stopped = "motor session start failed"
        if not stopped:
            job = JobTree()
            p = job.start(cmd, cwd=ROOT, env=env)
            t_end = time.time() + a.max_min * 60
            while True:
                try:
                    cmd_rc = p.wait(POLL_S)
                    break
                except subprocess.TimeoutExpired:
                    pass
                try:                                         # B1: a failing check is a stop, never an escape
                    allowed = riglock.permitted(token, motor_gate.RIG_STATES_OK)
                    if not allowed:
                        experiment = (riglock.status().get("rig_state") or {}).get("value") == "experiment"
                except Exception as e:                       # noqa: BLE001 - TimeoutError (stuck mutex) and the rest
                    allowed = False
                    stopped = "rig lock check failed (%s: %s)" % (type(e).__name__, e)
                if not allowed and not stopped:
                    stopped = ("experiment declared by the user" if experiment
                               else "rig lock no longer permits work (lock lost)")
                elif not stopped and time.time() > t_end:
                    stopped = "time limit %.0f min" % a.max_min
                if stopped:
                    say("stopping the command: %s" % stopped)
                    break
    except Exception as e:                                   # noqa: BLE001 - reported, the cleanup below still runs
        stopped = stopped or "wrapper error (%s: %s)" % (type(e).__name__, e)
        say("ERROR: %s" % stopped)
    finally:
        # cleanup ALWAYS. a. the job's processes gone FIRST (B1/B3: no limit release under a running job)
        tree_ok, tree_why = True, "no command was started"
        if job is not None:
            try:
                gone, before, left = kill_tree(job)
                members = before or []
                tree_ok = gone
                tree_why = ("all job processes gone (were %s)" % (before or "none") if gone
                            else "job processes STILL ALIVE after terminate: %s" % left)
            except Exception as e:                           # noqa: BLE001
                tree_ok, tree_why = False, "job kill failed (%s: %s)" % (type(e).__name__, e)
        say("job processes: %s %s" % ("OK" if tree_ok else "FAILED", tree_why))
        # b. LabVIEW: only our own (B4), also in the experiment state (B3)
        lv_ok, lv_why = _step(close_labview, os.path.join(LOGDIR, "rig_session_labview_%s.log" % stamp), t0, members)
        say("LabVIEW close: %s %s" % ("OK" if lv_ok else "FAILED", lv_why))
        # c. limits released ONLY once the job is verified gone (B3)
        end_ok, end_tail = True, []
        if started and not tree_ok:
            end_ok, end_tail = False, ["limits NOT released: the job may still be driving motors"]
        elif started:
            end_ok, end_tail = _step(gate_session, "end", env, os.path.join(LOGDIR, "rig_session_end_%s.log" % stamp))
        if started:
            say("motor session end: %s %s" % ("OK" if end_ok else "FAILED", " / ".join(end_tail)))
        clean = tree_ok and lv_ok and end_ok
        if clean:
            try:
                riglock.release(token)
                say("RIGLOCK released")
            except Exception as e:                           # noqa: BLE001
                clean = False
                say("RIGLOCK release FAILED (%s: %s) - the lock stays" % (type(e).__name__, e))
        else:
            say("RIGLOCK KEPT - cleanup not verified; the user must look before anyone uses the rig")
        if job is not None:
            job.close()
        if experiment:                                       # B3: tell the user the rig is back for the experiment
            say("CLEANUP COMPLETE - experiment declared mid-job: job stopped, LabVIEW (own) closed, limits released, "
                "lock released; the rig is at its initial condition" if clean else
                "CLEANUP INCOMPLETE - experiment declared mid-job but the cleanup was not verified; LOCK KEPT - the "
                "user must look before the experiment")

    res.update(cmd_rc=cmd_rc, stopped=stopped or None, job=tree_why, labview=lv_why,
               limits_released=end_ok if started else None, lock="released" if clean else "KEPT")
    if experiment:
        res["notice"] = "CLEANUP COMPLETE" if clean else "CLEANUP INCOMPLETE"
    rc = 3 if not clean else (4 if (stopped or cmd_rc) else 0)
    res["status"] = {0: "PASS", 3: "CLEANUP-FAILED", 4: "COMMAND-FAILED"}[rc]
    print("RESULT " + json.dumps(res, ensure_ascii=False))
    return rc


if __name__ == "__main__":
    sys.exit(main())
