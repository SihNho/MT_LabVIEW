"""gscript.py - drive the Op-VI fleet over ActiveX to build LabVIEW code, with verification.

Every Op VI in user.lib\\claudeDev takes a *target VI path* as an argument, so this module is a thin
typed wrapper around "set the Op's front-panel controls, run it, read its error out". No GUI, no
screenshots, no coordinates.

Two rules this file exists to enforce, both learned the hard way (see the labview-automation skill):

  * VERIFY, DO NOT ASSUME. An Op returning a clean error cluster proves nothing about *where* its
    edit landed. Every mutating call here is meant to be bracketed by report() - counting objects,
    or checking an object's owner - because a wrong-but-clean run is the normal failure mode.
  * SAVE THE TARGET. Op VIs edit LabVIEW's in-memory copy. Nothing reaches disk until save() is
    called on the target, and a LabVIEW restart silently discards everything that was not saved.

TIMEOUT / POISON (2026-09-17, fixes the defect named in archive/peer/2026-09-17-connectnested-stall.md)

  A hard timeout here does NOT cancel the COM call - COM has no safe cancel, and a daemon thread is
  not stoppable (Python docs: daemons are only killed at process exit). So the call stays OUTSTANDING
  inside LabVIEW's single-threaded apartment, and every later call QUEUES BEHIND IT. Measured
  2026-09-17: `_run` reported a 120 s timeout on OpMoveIn_v0, the next *unguarded* COM call blocked,
  and the log printed nothing for 28 minutes until bgrun killed the tree.

  The fix is a module-level POISON flag, not a guard on each call site. `_deadline_call()` sets it on
  every expiry (both `_run` and `_invoke` go through it), and `_check_poison()` runs FIRST in every
  entry point that can reach COM - `lv()`, `op()` (including a cache HIT: that was the unguarded path),
  `_invoke()`, `_run()`, `_err()`. While the abandoned call is still alive the next call raises
  COMPoisoned in milliseconds instead of blocking; when the abandoned worker has since finished the
  flag clears itself (measured with `thread.is_alive()`, not assumed) and work continues.
  With GSCRIPT_POISON_RECOVER=1 the next call instead RESTARTS LabVIEW (`_recover_poison()` =
  kill + start + reset(); unsaved LabVIEW edits are lost, which is why it is opt-in).

  What was NOT done, and why: routing every `GetVIReference`/`SetControlValue` through the watchdog
  thread was tried on 2026-09-05 (tools/gscript.py.guarded_attempt_20260905) and ROLLED BACK - it
  itself blocked in cross-apartment marshalling. The PROCESS-level deadline of bgrun remains the last
  guarantee; the poison flag is what removes the silent gap between the per-call timeout and it.
  Tests: tools/bench/test_run_poison.py (A = fake blocking callable, no LabVIEW; B = one real
  sub-millisecond timeout on a scratch op) -> tools/bench/test_run_poison.log.

Third-party: uses pywin32 (https://github.com/mhammond/pywin32) as a dependency only.

Usage:
  py tools\\gscript.py report <target.vi> <ClassName>     # list objects of a class
  py tools\\gscript.py kernel <target.vi>                 # build the parallel tracking loop
"""
import contextlib
import os
import subprocess
import sys
import threading
import time

import pythoncom
from win32com.client import dynamic

PROJECT = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop"
LV_GUI = os.path.join(PROJECT, "tools", "lv_gui.ps1")
SHOT_DIR = os.environ.get("TEMP", ".")

CLAUDEDEV = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
BG_VIS = os.path.join(CLAUDEDEV, "background VIs_COPY")

# THE ORIGINAL'S IDENTITY HAS ONE OWNER, AND IT IS THIS MODULE (2026-09-22, accepted from
# `archive/peer/2026-09-22-c87-stagekit-k2.md` §1/§3: `tools/stagekit.py` RESTATED this path instead of
# importing it, restated it WRONG, and its md5 pin then pinned a file that is not there -
# `tools/bench/diag_c83_connect2x2_kit.log:10`). Every module that needs it should read it from here
# rather than re-derive it; the value is `tools/bench/diag_s2_scaffold.py:81-82`'s, unchanged.
# NOTE the two names in circulation: `…4.5_KimLabMTroom_3StateClamping.vi` (tools/callgraph.py:19,
# tools/motor_census.py:92) is a DIFFERENT file from this one; neither sits inside the project folder.
ORIGINAL = os.path.join(os.path.dirname(PROJECT), "Min_Track N beads V6_ParallelLoop.vi")
ORIG_MD5 = "2a78e17c449cacdaf5da389818526859"

OP_REPORT = os.path.join(CLAUDEDEV, "OpReport_v3.vi")
OP_FORLOOP = os.path.join(CLAUDEDEV, "OpForLoop_v1.vi")   # v1 (2026-09-15, INDEX row 39): control tunnels + indexing actually wired; v0's never were
OP_SUBVI = os.path.join(CLAUDEDEV, "OpSubVI_v1.vi")
# v1 = v0 plus a full internal error chain into Clear Errors sinks: a bad terminal
# name now returns in ~0.03 s with no wire instead of wedging LabVIEW behind a
# modal 5001 dialog. v0 is kept only as the pristine ancestor.
OP_WIRE = os.path.join(CLAUDEDEV, "OpWire_v1.vi")
# The donor-copier: copies ANY GObject by label across VIs (GObject.Move, Duplicate).
# Its source/target are FIXED static refs to the two MOVE_TEST files - move_by_label()
# below wraps the substitution protocol. Adapted 2026-08-28 from NI's Simple Move.vi.
OP_MOVE_LABEL = os.path.join(CLAUDEDEV, "OpMoveByLabel_v0.vi")   # copy/move-by-label op (NOT OpMove_v0, the position mover)
OP_EXITLOOP = os.path.join(CLAUDEDEV, "OpExitLoop_v0.vi")
OP_WIREIND = os.path.join(CLAUDEDEV, "OpWireInd_v0.vi")
# Same lineage, method retargeted Move -> Generic:Delete (Delete lives on Generic, NOT
# GObject - a GObject-typed Invoke offers only 'Move'). Removes an object by label.
OP_DELETE = os.path.join(CLAUDEDEV, "OpDeleteByLabel_v0.vi")
MOVE_DIR = os.path.join(CLAUDEDEV, "NIScriptingExamples", "Moving Objects")
MOVE_SRC = os.path.join(MOVE_DIR, "Test - Moving Objects Source.vi")
MOVE_DST = os.path.join(MOVE_DIR, "Test - Moving Objects Target.vi")
# Pristine copy of MOVE_SRC. The substitution protocol restores MOVE_SRC in a finally
# block - but a killed process (TaskStop, Ctrl+C) skips it and leaves the donor's bytes
# sitting in the example file, which then poisons every later run. Happened 2026-08-28.
MOVE_SRC_ORIG = MOVE_SRC + ".ORIG.bak"
MOVE_DST_ORIG = MOVE_DST + ".ORIG.bak"

_lv = None
_cache = {}

# --- the POISON flag: what a hard timeout leaves behind -----------------------------------------
# See the "TIMEOUT / POISON" block in this module's docstring. `_poison` is None, or a dict
# {what, timeout_s, when, thread} describing the COM call that blew its deadline and was ABANDONED
# ALIVE in its daemon worker.
_poison = None


class COMPoisoned(RuntimeError):
    """A previous COM call hit its hard timeout and is STILL OUTSTANDING inside LabVIEW.

    COM serialises calls into a single-threaded apartment, so the next call would queue behind that
    outstanding one and block with no output - which is exactly the 28 minutes of silence measured on
    2026-09-17 (archive/peer/2026-09-17-connectnested-stall.md, codex ANSWERED). Raising here is the
    fix: the caller fails in milliseconds instead of blocking until bgrun's process deadline.
    """


def poisoned():
    """The poison record (dict) or None. Read-only; never touches COM."""
    return _poison


def clear_poison():
    """Forget the poison WITHOUT restarting LabVIEW. Only correct when the abandoned call is known to
    have returned (`poisoned()['thread'].is_alive()` False) - _check_poison() does that automatically."""
    global _poison
    _poison = None


def _set_poison(what, timeout_s, thread):
    global _poison
    _poison = {"what": what, "timeout_s": timeout_s, "when": time.time(), "thread": thread}
    sys.stderr.write("POISONED: %s did not return within %.3fs and was abandoned alive; "
                     "the next COM call will raise COMPoisoned instead of blocking behind it.\n"
                     % (what, timeout_s))
    sys.stderr.flush()


def _check_poison():
    """Called FIRST by every entry point that can reach COM (`lv`, `op`, `_invoke`, `_run`, `_err`).

    Three outcomes:
      * not poisoned            -> return, nothing happens;
      * poisoned but the abandoned worker has since FINISHED -> the apartment queue is drained, so the
        poison is cleared and the call proceeds (this is measured, not assumed: `thread.is_alive()`);
      * poisoned and still outstanding -> raise COMPoisoned immediately, or, with
        GSCRIPT_POISON_RECOVER=1, restart LabVIEW (standing permission, CLAUDE.md 3) and continue.
    """
    p = _poison
    if p is None:
        return
    th = p.get("thread")
    if th is not None and not th.is_alive():
        clear_poison()
        sys.stderr.write("poison cleared: the abandoned %s returned after %.0fs; apartment drained.\n"
                         % (p["what"], time.time() - p["when"]))
        sys.stderr.flush()
        return
    if os.environ.get("GSCRIPT_POISON_RECOVER") == "1":
        _recover_poison()
        return
    raise COMPoisoned(
        "%s timed out %.0fs ago (cap %.3fs) and is STILL OUTSTANDING in LabVIEW's apartment; this call "
        "would block behind it. Restart LabVIEW (py tools/lv_restart.py) or set GSCRIPT_POISON_RECOVER=1."
        % (p["what"], time.time() - p["when"], p["timeout_s"]))


def _recover_poison():
    """Kill + restart LabVIEW, drop every cached proxy, clear the poison. The abandoned worker's RPC
    dies with the server, so it stops holding the apartment. Standing restart permission, CLAUDE.md 3.
    UNSAVED EDITS IN LABVIEW ARE LOST - which is why this is opt-in, not the default."""
    global _poison
    p = _poison
    _poison = None
    sys.stderr.write("RECOVERING from poison (%s): restarting LabVIEW.\n" % (p or {}).get("what"))
    sys.stderr.flush()
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"],
                   capture_output=True, timeout=60)
    time.sleep(6)
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    r"Start-Process 'C:\Program Files\National Instruments\LabVIEW 2026\LabVIEW.exe'"],
                   capture_output=True, timeout=60)
    reset()
    for _ in range(30):
        time.sleep(5)
        try:
            _lv_new = dynamic.Dispatch("LabVIEW.Application")
            _ = _lv_new.Version
            globals()["_lv"] = _lv_new
            time.sleep(45)          # lv_restart.py: never touch the startup window; just wait it out
            return
        except Exception:           # noqa: BLE001
            continue
    raise RuntimeError("poison recovery: LabVIEW did not answer COM within 150s after the restart")


def _deadline_call(target, timeout_s, what):
    """Run `target()` in a daemon thread; wait at most `timeout_s`. True if it finished in time.

    On expiry the module is POISONED (see _check_poison) - the one guarantee this helper exists to give.
    `target` is any callable, so the poison machinery is testable WITHOUT LabVIEW: pass a blocking fake.
    """
    t = threading.Thread(target=target, daemon=True)
    t.start()
    t.join(timeout=timeout_s)
    if t.is_alive():
        _set_poison(what, timeout_s, t)
        return False
    return True


def lv():
    global _lv
    _check_poison()
    if _lv is None:
        _lv = dynamic.Dispatch("LabVIEW.Application")
    return _lv


def op(path):
    """A cached VI reference. Op VIs are non-reentrant, so one reference each is correct."""
    _check_poison()            # a cache HIT reached COM unguarded too - that was the 2026-09-17 stall
    if path not in _cache:
        _cache[path] = lv().GetVIReference(path, "", False, 0)
    return _cache[path]


# --- REFERENCE HYGIENE, COUNTED IN-PROCESS (CLAUDE.md §3 "close every reference, and PROVE it") -----
# AUDIT, 2026-09-19 (cycle-38 P3). What crosses COM into Python, measured by reading every call site:
#   * `report_all()`/`report()` NEVER return a refnum. The `Traverse for GObjects` array lives and dies
#     INSIDE the op VI; Python reads only the scalar columns (pos/uid/class/owner, :451-463). So there is
#     no traverse refnum array for this module to close - that hygiene question belongs to the op VI.
#   * The ONE refnum class Python does hold is `Application.GetVIReference`: `_cache` (one per op VI,
#     bounded, long-lived BY DESIGN) and six per-call sites (open_panel, close_panel, revert, exec_state,
#     save, make_default) that used to open a reference and simply drop the name. Those six now go through
#     `vi_ref()`, which releases the COM pointer explicitly in a `finally` and COUNTS both events.
# The counters are IN-PROCESS and count this module's own VI Server references - they are NOT the kernel
# handle count (`bench_prep.labview_handles`), which cannot see VI Server refnums at all.
_REF_OPENED = 0
_REF_CLOSED = 0


def ref_counts():
    """{opened, closed, live, cached_op_vis} - VI Server references opened by THIS process through this
    module. `live` counts the six per-call classes only; `cached_op_vis` is the bounded op-VI cache.
    ⚠️ NOT EVIDENCE ABOUT THE `error 2` MECHANISM (cycle-38 dispatch 1, measured): no `Traverse for GObjects`
    refnum array ever crosses COM, so these counters CANNOT see refnum-class exhaustion inside an op VI and
    must never be cited as if a flat reading here excluded it."""
    return {"opened": _REF_OPENED, "closed": _REF_CLOSED, "live": _REF_OPENED - _REF_CLOSED,
            "cached_op_vis": len(_cache)}


@contextlib.contextmanager
def vi_ref(target):
    """A SHORT-LIVED, COUNTED VI reference to `target`, released when the block exits.

    LabVIEW's exported ActiveX `VirtualInstrument` has no Close method - the underlying VI Server
    reference is closed when the last COM pointer to it is released. The `finally` here drops the ONLY
    name that ever held it (the caller receives it for the duration of the `with` block and must not
    store it), which releases the pywin32 proxy and with it the COM pointer, on the exception path too."""
    global _REF_OPENED, _REF_CLOSED
    _check_poison()
    ref = lv().GetVIReference(target, "", False, 0)
    _REF_OPENED += 1
    try:
        yield ref
    finally:
        ref = None
        _REF_CLOSED += 1


def reset():
    """Forget the Application AND every cached op-VI proxy. Call after LabVIEW is killed/restarted mid-script:
    `_lv = None` alone leaves `_cache` pointing at the dead instance and the next call dies with 0x800706BA
    'RPC server is unavailable' (2026-09-14 22:35 and 2026-09-15 04:00, both after a kill inside a recipe)."""
    global _lv
    _lv = None
    _cache.clear()
    _loaded.clear()      # a killed/restarted LabVIEW has forgotten every OpenFrontPanel (see ensure_loaded)


def _lv_gui(*args):
    """Invoke lv_gui.ps1 (no COM - safe from any thread).

    REPAIRED 2026-09-22 (`archive/peer/2026-09-22-c72-guisave-foreground-r2.md` §2, CONFIRMED by its
    own discriminating test): args were joined UNQUOTED into the -Command string, so any argument
    carrying spaces or parentheses - every `-Evidence` sentence, i.e. every state-changing action
    this module ever requested - was a PowerShell PARSE ERROR ("The term 'skill' is not recognized")
    and the action never dispatched; `tools/gui_actions.log` has no state-changing row from these
    call sites. Each arg is now single-quoted for PowerShell unless the caller pre-quoted it."""
    def q(a):
        a = str(a)
        if a.startswith('"') and a.endswith('"'):
            return a                     # call sites pass titles pre-quoted: '"<name> Front Panel"'
        if a and not any(c in a for c in " ()'\"`,;&|"):
            return a
        return "'" + a.replace("'", "''") + "'"
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
           "& '{}' {}".format(LV_GUI, " ".join(q(a) for a in args))]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return (r.stdout or "") + (r.stderr or "")


def cluster_array(rows):
    """Build the COM VARIANT for a LabVIEW '1-D ARRAY OF CLUSTERS' control.

    `rows` is a sequence of tuples, one per cluster, fields in the cluster's tab order:
        vi.SetControlValue('Properties', cluster_array([('IndexMode', True)]))

    Passing the plain Python list instead RAISES NOTHING AND DOES NOTHING: pywin32 sees a
    sequence of equal-length sequences and marshals a 2-D SAFEARRAY, LabVIEW's coercion
    rejects the dimension mismatch, and SetControlValue still returns S_OK. LabVIEW wants a
    1-D SAFEARRAY of VARIANTs whose elements are themselves 1-D SAFEARRAYs of VARIANTs.
    Verified 2026-08-30: plain list leaves (), this form reads back (('IndexMode', True),).
    """
    from win32com.client import VARIANT
    V = pythoncom.VT_ARRAY | pythoncom.VT_VARIANT

    def field(x):
        if isinstance(x, bool):
            return VARIANT(pythoncom.VT_BOOL, x)
        if isinstance(x, int):
            return VARIANT(pythoncom.VT_I4, x)
        if isinstance(x, float):
            return VARIANT(pythoncom.VT_R8, x)
        return VARIANT(pythoncom.VT_BSTR, str(x))

    return VARIANT(V, [VARIANT(V, [field(f) for f in row]) for row in rows])


def _invoke(vi, method, *args, **kw):
    """Call any COM method under the SAME watchdog + hard cap as _run().

    The watchdog originally guarded only `Run`, so save / revert / OpenFrontPanel /
    CloseFrontPanel could still hang forever with no dialog - and did, repeatedly
    (2026-08-29). Every COM call now goes through here.
    """
    timeout = kw.pop("hard_timeout_s", 180.0)
    _check_poison()
    ole = vi._oleobj_
    stream = pythoncom.CoMarshalInterThreadInterfaceInStream(pythoncom.IID_IDispatch, ole)
    result = {}

    def call():
        pythoncom.CoInitialize()
        try:
            disp = pythoncom.CoGetInterfaceAndReleaseStream(stream, pythoncom.IID_IDispatch)
            result["ok"] = disp.Invoke(disp.GetIDsOfNames(0, method), 0,
                                       pythoncom.DISPATCH_METHOD, 1, *args)
        except Exception as e:                      # noqa: BLE001
            result["err"] = e
        finally:
            pythoncom.CoUninitialize()

    if not _deadline_call(call, timeout, "COM %s" % method):
        raise RuntimeError(
            "COM %s did not return within %.0fs (no dialog) - LabVIEW busy or a second "
            "client contending. MODULE POISONED: the call is still outstanding, so the next COM "
            "call raises COMPoisoned instead of blocking behind it." % (method, timeout))
    if "err" in result:
        raise result["err"]
    return result.get("ok")


def _run(vi, poll_s=6.0, hard_timeout_s=180.0):
    """Run the VI over COM under a watchdog AND an absolute time cap.

    Two independent failure modes, two guards:

    * A LabVIEW error dialog blocks the Run call indefinitely and is invisible to the
      caller. A watchdog thread polls the window list; on a modal dialog it screenshots
      the screen (the diagnosis), posts WM_CLOSE (which releases the call), and records
      the event so this function raises instead of returning a fake success.
    * A block that is NOT a dialog - LabVIEW busy, a second COM client contending, an
      editor operation pending - shows no dialog at all, so the watchdog never fires.
      With no cap, such a run waits forever: two clients sat blocked for 7 hours on
      2026-08-28 with ~0 CPU before anyone noticed. So the COM call now runs in a
      DAEMON thread and the caller waits at most `hard_timeout_s`; on expiry it raises
      and the abandoned thread dies with the process. Op VIs finish in well under a
      second, so any cap above a minute is generous.

    Only ONE COM client may drive LabVIEW at a time (project rule 3). Never start a
    second run while one is alive - that contention is itself a cause of no-dialog
    hangs.

    On expiry the module is POISONED as well as raising: the abandoned call still holds
    LabVIEW's apartment, so the NEXT call must not be allowed to queue behind it silently
    (see the TIMEOUT / POISON block in the module docstring).
    """
    _check_poison()
    done = threading.Event()
    hits = []

    def watchdog():
        while not done.wait(poll_s):
            try:
                out = _lv_gui("-Action", "dialogs")
            except Exception:
                continue
            if "VERDICT: BLOCKED" in out:
                shot = os.path.join(SHOT_DIR, "gscript_dialog_%d.png" % int(time.time()))
                try:
                    _lv_gui("-Action", "shot", "-Out", "'%s'" % shot)
                except Exception:
                    shot = "(screenshot failed)"
                try:
                    _lv_gui("-Action", "dismiss")
                except Exception:
                    pass
                hits.append(shot)

    w = threading.Thread(target=watchdog, daemon=True)
    w.start()
    ole = vi._oleobj_
    t0 = time.time()
    result = {}

    # COM is apartment-threaded: an interface pointer cannot simply be handed to
    # another thread ("called an interface that was marshalled for a different
    # thread"). Marshal it through a stream, which is the supported way.
    stream = pythoncom.CoMarshalInterThreadInterfaceInStream(pythoncom.IID_IDispatch, ole)

    def call():
        pythoncom.CoInitialize()
        try:
            disp = pythoncom.CoGetInterfaceAndReleaseStream(stream, pythoncom.IID_IDispatch)
            disp.Invoke(disp.GetIDsOfNames(0, "Run"), 0, pythoncom.DISPATCH_METHOD, 1)
            result["ok"] = True
        except Exception as e:                      # noqa: BLE001 - reported to caller
            result["err"] = e
        finally:
            pythoncom.CoUninitialize()

    timed_out = not _deadline_call(call, hard_timeout_s, "COM Run")
    done.set()
    w.join(timeout=2)
    dt = time.time() - t0

    if timed_out:
        shot = os.path.join(SHOT_DIR, "gscript_hang_%d.png" % int(time.time()))
        try:
            _lv_gui("-Action", "shot", "-Out", "'%s'" % shot)
        except Exception:
            shot = "(screenshot failed)"
        raise RuntimeError(
            "COM Run did not return within %.0fs and no modal dialog was found - "
            "LabVIEW is busy or another client is contending. MODULE POISONED: the Run is "
            "still outstanding, so the next COM call raises COMPoisoned instead of blocking "
            "behind it. Screenshot: %s" % (hard_timeout_s, shot))
    if "err" in result:
        raise result["err"]
    if hits:
        raise RuntimeError(
            "run blocked behind a modal dialog (dismissed by watchdog after %.0fs); "
            "screenshot(s): %s" % (dt, ", ".join(hits)))
    return dt


def _err(vi, name="error out"):
    """The FULL `error out` source string, never its first line only.

    CYCLE 38 (prior-art finding F2 `unread-evidence`, `archive/peer/2026-09-19-priorart-d1-routeb-run6.md`):
    this returned `src.splitlines()[0]`, which threw away the rest of LabVIEW's source string - and that
    remainder is exactly what separates the three branches of error 5001 from one another. Newlines are folded
    to ` | ` so a single log line still carries every segment; nothing is dropped."""
    _check_poison()      # outside the try: the except below would otherwise SWALLOW COMPoisoned
    try:
        status, code, src = tuple(vi.GetControlValue(name))
    except Exception:
        return None
    if not status:
        return None
    full = " | ".join(s.strip() for s in (src or "").splitlines() if s.strip())
    return f"error {code}: {full}"


# --- read -------------------------------------------------------------------------------------

def report(target, cls):
    """Every object of `cls` on target's block diagram, as dicts with class/uid/pos/owner."""
    vi = op(OP_REPORT)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", cls)
    vi.SetControlValue("index", 0)
    _run(vi)
    err = _err(vi)
    if err:
        raise RuntimeError(f"report({cls}) on {os.path.basename(target)}: {err}")
    n = int(vi.GetControlValue("# of Refs"))
    out = []
    for i in range(n):
        vi.SetControlValue("index", i)
        _run(vi)
        out.append({
            "i": i,
            "class": vi.GetControlValue("Class Name 2"),
            "uid": int(vi.GetControlValue("UID")),
            "pos": tuple(vi.GetControlValue("Position")),
            "owner": vi.GetControlValue("Class Name 3"),
        })
    return out


OP_REPORT_ALL = os.path.join(CLAUDEDEV, "OpReportAll_v0.vi")

# The op's four auto-indexed output tunnels, in the order build_opreportall_v1.py creates them. LabVIEW names the
# indicators itself ("Array", "Array 2", ...); the mapping was READ back from the machine at build time and is
# mirrored in tools/bench/opreportall_labels.json, not assumed.
_REPORT_ALL_FIELDS = [("Array", "pos"), ("Array 2", "uid"), ("Array 3", "class"), ("Array 4", "owner")]


def report_all(target, cls):
    """Every object of `cls` on target's block diagram in ONE op run - the array-returning form of report().

    WHY THIS EXISTS. `report()` runs the op once per object, and ~990 ms of every run is the FIXED cost of
    `Open VI Reference` on a large VI (measured 2026-09-13: 10.4 ms on a small VI, 960.8 ms on the main VI,
    while COM itself is 0.07 ms). A 626-node sweep therefore paid that 626 times - 618 s measured. This pays it
    once: the For Loop runs INSIDE LabVIEW and the results come back as arrays.

    Returns the same [{i, class, uid, pos, owner}] shape as report(), so it is a drop-in replacement.
    """
    vi = op(OP_REPORT_ALL)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", cls)
    _run(vi)
    err = _err(vi)
    if err:
        raise RuntimeError(f"report_all({cls}) on {os.path.basename(target)}: {err}")
    cols = {}
    for label, key in _REPORT_ALL_FIELDS:
        cols[key] = list(vi.GetControlValue(label))
    n = min(len(v) for v in cols.values()) if cols else 0
    out = []
    for i in range(n):
        out.append({
            "i": i,
            "class": cols["class"][i],
            "uid": int(cols["uid"][i]),
            "pos": tuple(cols["pos"][i]),
            "owner": cols["owner"][i],
        })
    return out


OP_SUBVIS = os.path.join(CLAUDEDEV, "OpSubVIs_v1.vi")
_SUBVIS_LABELS = None


def subvis(target, diagram_index, purge=False, strict=True, **controls):
    """Every subVI call on ONE diagram of `target`, as [{uid, name, path}] in one op run - the cast-free identity
    route (AbstractDiagram.SubVIs[] -> For loop -> SubVI[VI Name, VI Path, UID]), built 2026-09-14 by
    tools/recipes/build_opsubvis_v0.py on donor OpNetInfo_v1 (Traverse 'Diagram' by index -> To More Specific Class).
    `diagram_index` is the Traverse 'Diagram' index (0 = top level), the same index net_map and
    tools/bench/diagram_tree_main.json use. SubVIs[] is NOT recursive: calls inside a structure belong to that
    structure's own diagram - walk the tree and call per diagram.

    The donor's junk-dropping erdosmiller creator (docs/keystone-op-spec.md s33) was DELETED from this op at build
    time (build_opsubvis_v1.log step 2b) and tools/bench/test_opsubvis_v1.log T0 measured **0 junk Invokes per
    call**, so purge defaults to False; purge=True re-checks (two extra report_all runs on the target) and deletes
    whatever a call added. FUNCTIONALLY verified 2026-09-14 (test_opsubvis_v1.log, 14/14): main VI diagram 43 ==
    cache (6 calls, kernel uid 5058 = 'Track N beads four-fold over-kernel-v3.vi'), invalid index -> error 1055 on
    the node's own error out, empty diagram -> empty arrays. Cost: 0.17 s on a small VI, ~1.2 s on the main VI
    (one Open VI Reference); handle count grows ~0.9 per Open VI Reference on the main VI (OPEN, not SubVIs[]:
    the same growth appears with zero element refs). strict=False returns (rows, err) instead of raising on the
    SubVIs[] node's own error. Extra `controls` override the op's inputs (e.g. the vestigial `index 2`)."""
    global _SUBVIS_LABELS
    if _SUBVIS_LABELS is None:
        import json
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "bench", "opsubvis_v1_labels.json"),
                  encoding="utf-8") as f:
            _SUBVIS_LABELS = {v: k for k, v in json.load(f).items()}
    lab = _SUBVIS_LABELS
    inv0 = uids(target, "Invoke") if purge else None
    vi = op(OP_SUBVIS)
    vi.SetControlValue("vi path", target); vi.SetControlValue("Class Name", "Diagram")
    vi.SetControlValue("index", diagram_index); vi.SetControlValue("index 2", 0); vi.SetControlValue("index 3", 0)
    vi.SetControlValue("error in (no error)", (False, 0, "")); vi.SetControlValue("error in", (True, 1, "neutralised creator"))
    vi.SetControlValue("Class Name 3", ""); vi.SetControlValue("Class Name 2", "")
    for k, v in controls.items():
        vi.SetControlValue(k, v)
    _run(vi)
    err = _err(vi, lab["error"])
    names = list(vi.GetControlValue(lab["VIName"]))
    paths = list(vi.GetControlValue(lab["VIPath"]))
    ids = [int(u) for u in vi.GetControlValue(lab["UID"])]
    if purge:
        order = [o["uid"] for o in report_all(target, "Invoke")]
        junk = [u for u in order if u not in inv0]
        for idx in sorted((order.index(u) for u in junk), reverse=True):
            try:
                delete_object(target, "Invoke", idx, verify=False)
            except Exception:
                pass
        if junk:
            try:
                remove_bad_wires_scripted(target)
            except Exception:
                pass
    rows = [{"uid": u, "name": n, "path": p} for n, p, u in zip(names, paths, ids)]
    if not strict:
        return rows, err
    if err:
        raise RuntimeError(f"subvis({os.path.basename(target)}, {diagram_index}): {err}")
    return rows


OP_NODE_LABELS = os.path.join(CLAUDEDEV, "OpNodeLabels_v0.vi")
_NODE_LABELS_LABELS = None


def node_labels(target, diagram_index, strict=True, **controls):
    """The LABEL TEXT of every node on one diagram of `target`, as [{uid, label}] in one op run - cast-free
    (Diagram.Nodes[] -> For loop -> Node[Label 6359001, UID] -> Text.Text). Built 2026-09-14 by
    tools/recipes/build_opnodelabels_v0.py on donor OpNetInfo_v1 (creator deleted, as OpSubVIs_v1). Purpose: an
    IMPLICIT property node's header is its label (LabVIEW Wiki), so this attributes the main VI's implicit `Value`
    nodes to panel objects; peer caveat (archive/peer/2026-09-14-opnodelabels-v0-plan.md): a label that was never
    displayed may read '' - the functional test decides (tools/bench/test_opnodelabels.py). Nodes whose class holds
    no label give ''. `diagram_index` is the Traverse 'Diagram' index (0 = top level)."""
    global _NODE_LABELS_LABELS
    if _NODE_LABELS_LABELS is None:
        import json
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "bench", "opnodelabels_labels.json"),
                  encoding="utf-8") as f:
            _NODE_LABELS_LABELS = {v: k for k, v in json.load(f).items()}
    lab = _NODE_LABELS_LABELS
    vi = op(OP_NODE_LABELS)
    vi.SetControlValue("vi path", target); vi.SetControlValue("Class Name", "Diagram")
    vi.SetControlValue("index", diagram_index); vi.SetControlValue("index 2", 0); vi.SetControlValue("index 3", 0)
    vi.SetControlValue("error in (no error)", (False, 0, "")); vi.SetControlValue("error in", (True, 1, "neutralised creator"))
    vi.SetControlValue("Class Name 3", ""); vi.SetControlValue("Class Name 2", "")
    for k, v in controls.items():
        vi.SetControlValue(k, v)
    _run(vi)
    err = _err(vi, lab["error"]) if "error" in lab else ""
    texts = list(vi.GetControlValue(lab["Text"]))
    ids = [int(u) for u in vi.GetControlValue(lab["UID"])]
    rows = [{"uid": u, "label": t} for t, u in zip(texts, ids)]
    if not strict:
        return rows, err
    if err:
        raise RuntimeError(f"node_labels({os.path.basename(target)}, {diagram_index}): {err}")
    return rows


OP_LOOP_CAST = os.path.join(CLAUDEDEV, "OpLoopCast_v0.vi")
OP_WHILE_CAST = os.path.join(CLAUDEDEV, "OpWhileCast_v0.vi")
_LOOP_CAST_LABELS = None


def loop_cast(target, index, class_name="ForLoop"):
    """A ForLoop-TYPED look at the `index`-th loop of `target` (Traverse class `class_name`, 'ForLoop' or
    'WhileLoop'): {loop_uid, n_wire_uid, shift_reg_uids, errors}. Cast-free seed: the op's TMSC 'target class' is
    fed by a ForLoop-refnum CONTROL created from erdosmiller Create For Loop.vi's typed output (NI: TMSC accepts any
    wire of the target type). Built 2026-09-14 by tools/recipes/build_oploopcast_v0.py; plan review
    archive/peer/2026-09-14-loopcast-typed-terminal-seed-plan.md. n_wire_uid = the wire on the loop-count tunnel's
    outside terminal (0 when N is unwired); shift_reg_uids = GObject.UID of each Loop.Shift Registers[] element
    (side/terminals not resolved here). errors = the chain's own error-out texts ('' when clean)."""
    # A seed casts only its own class (test_oploopcast.log T3: the ForLoop seed on a WhileLoop ref -> error 1055
    # downstream), so WhileLoops go through OpWhileCast_v0 (WhileLoop seed, shift registers only, no N wire).
    global _LOOP_CAST_LABELS
    if _LOOP_CAST_LABELS is None:
        import json
        _LOOP_CAST_LABELS = {}
        for cls, fn in (("ForLoop", "oploopcast_labels.json"), ("WhileLoop", "opwhilecast_labels.json")):
            p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bench", fn)
            if os.path.exists(p):
                with open(p, encoding="utf-8") as f:
                    _LOOP_CAST_LABELS[cls] = {v: k for k, v in json.load(f).items()}
    if class_name not in _LOOP_CAST_LABELS:
        raise RuntimeError(f"loop_cast: no op for class {class_name!r} (build it with build_oploopcast_v0.py {class_name})")
    lab = _LOOP_CAST_LABELS[class_name]
    # ForLoop: v1 (parallelism properties) when built, else v0
    v1 = os.path.join(CLAUDEDEV, "OpLoopCast_v1.vi"); v1map = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bench", "oploopcast_v1_labels.json")
    use_v1 = class_name == "ForLoop" and os.path.exists(v1) and os.path.exists(v1map)
    if use_v1 and "ParEnabled" not in lab:
        import json
        with open(v1map, encoding="utf-8") as f:
            lab = _LOOP_CAST_LABELS[class_name] = {v: k for k, v in json.load(f).items()}
    vi = op(v1 if use_v1 else (OP_LOOP_CAST if class_name == "ForLoop" else OP_WHILE_CAST))
    vi.SetControlValue("vi path", target); vi.SetControlValue("Class Name", class_name); vi.SetControlValue("index", index)
    _run(vi)
    errs = {k: _err(vi, lab[k]) for k in ("LoopCountErr", "ConnWireErr", "ShiftRegsErr", "ParEnabledErr", "ParInstancesErr") if k in lab}
    out = {"loop_uid": int(vi.GetControlValue(lab["LoopUID"])),
           "n_wire_uid": int(vi.GetControlValue(lab["NWireUID"])) if "NWireUID" in lab else None,
           "shift_reg_uids": [int(u) for u in vi.GetControlValue(lab["ShiftRegUIDs"])],
           "errors": {k: v for k, v in errs.items() if v}}
    if "ParEnabled" in lab:
        out["parallel_enabled"] = bool(vi.GetControlValue(lab["ParEnabled"]))
        out["static_instances"] = int(vi.GetControlValue(lab["ParInstances"]))
    return out


OP_ADD_SHIFT_REG = os.path.join(CLAUDEDEV, "OpAddShiftReg_v0.vi")
_ADD_SHIFT_REG_LABELS = None


def add_shift_reg(target, loop_index, y_position=120, class_name="WhileLoop"):
    """CREATE a shift register on the loop_index-th loop of Traverse class `class_name`, returning the new
    RightShiftRegister's UID (OpAddShiftReg_v0, built 2026-09-14 - INDEX row 37).

    `Loop.Add Shift Register` 6361000 on the WhileLoop-TYPED reference OpWhileCast_v0 already holds (the cast-free
    typed-control seed). The method is PUBLIC - it attaches through the ordinary builder - and a Loop-class Invoke
    accepts a WhileLoop reference by inheritance (both measured, tools/bench/build_opaddshiftreg_v0_run3.log).
    Peer review that found this route after the plan proposed abusing erdosmiller's `Exit While Loop.vi`:
    archive/peer/2026-09-14-stage2-shiftreg-primitive.md.

    BOTH SIDES COME BACK UNWIRED, and an unwired register breaks the VI (ExecState 0) until they are wired - that is
    correct, not a failure. Read them with shift_reg / shift_reg_left; wire them with Terminal.Connect Wire (invoke on
    the SINK, `Wire Source` = the source): the LEFT register's OUTSIDE terminal is the sink of the initial value, its
    INSIDE terminal is the source into the body, and the RIGHT register's INSIDE terminal is the sink of the
    iteration's result.

    THE LOAD IS NOW FORCED: this wrapper calls ensure_loaded(target) before the run (2026-09-21), because without it
    the op ran, returned a uid and a clean error, and CREATED NOTHING. The "both sides come back unwired ... breaks
    the VI (ExecState 0)" behaviour above is what a CORRECTLY LOADED target does - the silent no-op was the bug, not
    that documented breakage."""
    # 2026-09-15 01:1x (build_track_v6_core.log run 3, error 1055): the op is chosen by class_name - the WhileLoop
    # seed cannot cast a ForLoop reference (row 28); the ForLoop twin OpAddShiftRegF_v0 exists since cycle 3 (row 39)
    global _ADD_SHIFT_REG_LABELS
    import json
    if _ADD_SHIFT_REG_LABELS is None:
        _ADD_SHIFT_REG_LABELS = {}
    if class_name not in _ADD_SHIFT_REG_LABELS:
        fn = "opaddshiftregF_labels.json" if class_name == "ForLoop" else "opaddshiftreg_labels.json"
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "bench", fn), encoding="utf-8") as f:
            _ADD_SHIFT_REG_LABELS[class_name] = json.load(f)
    lab = _ADD_SHIFT_REG_LABELS[class_name]
    # 2026-09-21 (cycle 67 material #3, tools/bench/diag_c67_opvi.log): with the target not fully loaded this op RUNS,
    # returns a uid and writes NO error, and creates NOTHING (legs L1/L4); with the panel opened first it mints the
    # register and takes ExecState 1 -> 0 exactly as the docstring predicts (L3). add_shift_reg was the one mutating
    # wrapper in this family that never reached ensure_loaded, while move_in (build_d1_v0.py:321) always did.
    ensure_loaded(target)   # edits are silently declined on a target that is not fully loaded
    vi = op(os.path.join(CLAUDEDEV, "OpAddShiftRegF_v0.vi") if class_name == "ForLoop" else OP_ADD_SHIFT_REG)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", class_name); vi.SetControlValue("index", loop_index)
    vi.SetControlValue(lab["y_position"], int(y_position))
    _run(vi)
    err = _err(vi, lab["error"]) if "error" in lab else ""
    if err:
        raise RuntimeError(f"add_shift_reg: {err}")
    return int(vi.GetControlValue(lab["uid"]))


_WIRESR_LABELS = None


def wire_sr(variant, target, loop_index, reg_index, node_index=None, term_index=None, ctl_index=None,
            class_name="WhileLoop"):
    """Wire ONE side of the reg_index-th shift register of the loop_index-th `class_name` loop (OpWireSR_*_v0,
    INDEX row 38, functional: a register wired by these three calls compiles and runs).
      'LeftIn'      : left INSIDE  -> Terminals[term_index] of Nodes[node_index] INSIDE the loop body (Loop.Diagram)
      'RightIn'     : Terminals[term_index] of body Nodes[node_index] -> right INSIDE
      'LeftOutNode' : Terminals[term_index] of TOP-LEVEL Nodes[node_index] -> left OUTSIDE (initial value)
      'LeftOutCtl'  : Panel.Controls[ctl_index]'s terminal -> left OUTSIDE (initial value from a control)
    Indices are creation-order Nodes[] / Terminals[] (read them with node_terms_uid on the right diagram just before
    the call) and Panel.Controls[] (= fp_labels order). An UNTYPED register takes the type of its first wire, so wire
    the typed side first. Terminal.Connect Wire is invoked on the SINK; verify by wire uid on both ends (shift_reg_left).

    THE LOAD IS NOW FORCED: this wrapper calls ensure_loaded(target) before the run (2026-09-21), for the same reason
    add_shift_reg does - a not-fully-loaded target silently declines the edit while the op still returns cleanly."""
    # 2026-09-15 01:1x: op family chosen by class_name (ForLoop -> OpWireSRF_*, WhileLoop -> OpWireSR_*); the
    # WhileLoop seed errors 1055 on a ForLoop reference (row 28) - the same wrapper defect as add_shift_reg's
    global _WIRESR_LABELS
    import json
    if _WIRESR_LABELS is None:
        _WIRESR_LABELS = {}
    if class_name not in _WIRESR_LABELS:
        fn = "opwiresrF_labels.json" if class_name == "ForLoop" else "opwiresr_labels.json"
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "bench", fn), encoding="utf-8") as f:
            _WIRESR_LABELS[class_name] = json.load(f)
    lab = _WIRESR_LABELS[class_name][variant]
    # 2026-09-21 (cycle 67 material #3, tools/bench/diag_c67_opvi.log): the measured cause of add_shift_reg's silent
    # no-op was the missing load, and wire_sr is its sibling in the same op family with the same omission.
    ensure_loaded(target)   # edits are silently declined on a target that is not fully loaded
    fam = "OpWireSRF" if class_name == "ForLoop" else "OpWireSR"
    vi = op(os.path.join(CLAUDEDEV, f"{fam}_{variant}_v0.vi"))
    vi.SetControlValue("vi path", target); vi.SetControlValue("Class Name", class_name); vi.SetControlValue("index", loop_index)
    vi.SetControlValue(lab["index_reg"], int(reg_index))
    if variant == "LeftOutCtl":
        vi.SetControlValue(lab["index_ctl"], int(ctl_index))
    else:
        vi.SetControlValue(lab["index_node"], int(node_index)); vi.SetControlValue(lab["index_term"], int(term_index))
    _run(vi)
    err = _err(vi, lab["error"])
    if err:
        raise RuntimeError(f"wire_sr({variant}): {err}")


OP_SHIFT_REGS = os.path.join(CLAUDEDEV, "OpShiftRegs_v0.vi")
_SHIFT_REGS_LABELS = None


def shift_reg(target, loop_index, reg_index, class_name="WhileLoop"):
    """The reg_index-th element of Loop.Shift Registers[] of the loop_index-th loop of Traverse class `class_name`
    (OpShiftRegs_v0, built 2026-09-14 on OpWhileCast_v0 - so class_name is WhileLoop unless a ForLoop-seeded copy
    exists): {uid, class, out: {name, is_source, wire}, inside: [{name, is_source, wire}, ...], errors}. Tunnel-only
    census (v0): outside terminal + one inside terminal per frame; left/right pairing is v1. wire 0 = unwired (an
    uninitialised register's outside terminal is legitimately unwired)."""
    global _SHIFT_REGS_LABELS
    if _SHIFT_REGS_LABELS is None:
        import json
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "bench", "opshiftregs_labels.json"),
                  encoding="utf-8") as f:
            _SHIFT_REGS_LABELS = {v: k for k, v in json.load(f).items()}
    lab = _SHIFT_REGS_LABELS
    vi = op(OP_SHIFT_REGS)
    vi.SetControlValue("vi path", target); vi.SetControlValue("Class Name", class_name); vi.SetControlValue("index", loop_index)
    vi.SetControlValue(lab["index2"], reg_index)
    _run(vi)
    errs = {k: _err(vi, lab[k]) for k in ("OuterErr", "OutConnErr", "InsideErr", "ShiftRegsErr") if k in lab}
    uids_ = [int(u) for u in vi.GetControlValue(lab["ShiftRegUIDs"])] if "ShiftRegUIDs" in lab else []
    names = list(vi.GetControlValue(lab["InName"])); srcs = list(vi.GetControlValue(lab["InIsSource"]))
    wires = [int(w) for w in vi.GetControlValue(lab["InWireUID"])]
    return {"uid": uids_[reg_index] if reg_index < len(uids_) else None,
            "class": str(vi.GetControlValue(lab["ClassName"])),
            "out": {"name": str(vi.GetControlValue(lab["OutName"])), "is_source": bool(vi.GetControlValue(lab["OutIsSource"])),
                    "wire": int(vi.GetControlValue(lab["OutWireUID"]))},
            "inside": [{"name": n, "is_source": bool(s), "wire": w} for n, s, w in zip(names, srcs, wires)],
            "errors": {k: v for k, v in errs.items() if v}}


OP_SHIFT_REGS_V1 = os.path.join(CLAUDEDEV, "OpShiftRegs_v1.vi")
_SHIFT_REGS_V1_LABELS = None


def shift_reg_left(target, loop_index, reg_index, left_index=0, class_name="WhileLoop"):
    """OpShiftRegs_v1: everything shift_reg() returns for the reg_index-th RIGHT register PLUS its LEFT side:
    {..., left_uids: [uid, ...] (stacked lefts, RightShiftRegister.Left Registers[] 6357800), left: {uid, class,
    out: {name, is_source, wire}, inside: [{name, is_source, wire}, ...]}} for the left_index-th left register.
    Left outside terminal = the initial value (sink; wire 0 = uninitialised), left inside terminal = the source into
    the body. Built 2026-09-14 (tools/recipes/build_opshiftregs_v1.py)."""
    global _SHIFT_REGS_V1_LABELS
    if _SHIFT_REGS_V1_LABELS is None:
        import json
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "bench", "opshiftregs_v1_labels.json"),
                  encoding="utf-8") as f:
            _SHIFT_REGS_V1_LABELS = {v: k for k, v in json.load(f).items()}
    lab = _SHIFT_REGS_V1_LABELS
    vi = op(OP_SHIFT_REGS_V1)
    vi.SetControlValue("vi path", target); vi.SetControlValue("Class Name", class_name); vi.SetControlValue("index", loop_index)
    vi.SetControlValue(lab["index2"], reg_index); vi.SetControlValue(lab["index3"], left_index)
    _run(vi)
    errs = {k: _err(vi, lab[k]) for k in ("OuterErr", "OutConnErr", "InsideErr", "ShiftRegsErr", "LeftRegsErr", "LeftOuterErr", "LeftInsideErr") if k in lab}
    uids_ = [int(u) for u in vi.GetControlValue(lab["ShiftRegUIDs"])]
    lefts = [int(u) for u in vi.GetControlValue(lab["LeftUIDs"])]

    def terms(pfx):
        names = list(vi.GetControlValue(lab[pfx + "InName"])); srcs = list(vi.GetControlValue(lab[pfx + "InIsSource"]))
        wires = [int(w) for w in vi.GetControlValue(lab[pfx + "InWireUID"])]
        return [{"name": n, "is_source": bool(s), "wire": w} for n, s, w in zip(names, srcs, wires)]

    def out(pfx):
        return {"name": str(vi.GetControlValue(lab[pfx + "OutName"])), "is_source": bool(vi.GetControlValue(lab[pfx + "OutIsSource"])),
                "wire": int(vi.GetControlValue(lab[pfx + "OutWireUID"]))}
    return {"uid": uids_[reg_index] if reg_index < len(uids_) else None, "class": str(vi.GetControlValue(lab["ClassName"])),
            "out": out(""), "inside": terms(""), "left_uids": lefts,
            "left": {"uid": lefts[left_index] if left_index < len(lefts) else None, "class": str(vi.GetControlValue(lab["LeftClassName"])),
                     "out": out("Left"), "inside": terms("Left")},
            "errors": {k: v for k, v in errs.items() if v}}


OP_PANEL_WIRING = os.path.join(CLAUDEDEV, "OpPanelWiring_v0.vi")
_PANEL_WIRING_LABELS = None


def panel_wiring(target):
    """Every TOP-LEVEL front-panel object of `target` with its diagram terminal's wiring, in one op run:
    [{label, indicator, uid, is_source, wire, term_err, wire_err}] in Panel.Controls[] (tabbing) order.
    `wire` = the connected wire's UID, 0 when the terminal is bare (then wire_err == 1055 and term_err == 0: the
    terminal exists, nothing is wired to it). A bare terminal is "not used via its terminal" - locals and Value
    property nodes are not seen here. Built 2026-09-14 (tools/recipes/build_oppanelwiring_v0.py, donor OpFPLabels_v0:
    Panel.Controls[] -> For loop -> Control[Label, Indicator, UID] + Control[Terminal] -> Terminal[Is Source?,
    Connected Wire] -> GObject[UID]); FUNCTIONALLY verified tools/bench/test_oppanelwiring.log 11/11 (main VI: 114
    rows, 60/54, constructed orphan = exactly +1). Not recursive: tab pages / cluster elements are not rows.
    Cost 0.1 s small VI, ~0.8 s main VI."""
    global _PANEL_WIRING_LABELS
    if _PANEL_WIRING_LABELS is None:
        import json
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "bench", "oppanelwiring_labels.json"),
                  encoding="utf-8") as f:
            _PANEL_WIRING_LABELS = {v: k for k, v in json.load(f).items()}
    lab = _PANEL_WIRING_LABELS
    vi = op(OP_PANEL_WIRING)
    vi.SetControlValue("vi path", target)
    _run(vi)
    err = _err(vi)
    if err:
        raise RuntimeError(f"panel_wiring({os.path.basename(target)}): {err}")
    cols = {k: list(vi.GetControlValue(lab[k])) for k in ("Text", "Indicator", "ControlUID", "IsSource", "WireUID")}
    errs = {}
    for k in ("TermErr", "WireErr"):
        if k in lab:
            try:
                errs[k] = [int(tuple(e)[1]) if tuple(e)[0] else 0 for e in vi.GetControlValue(lab[k])]
            except Exception:
                errs[k] = []
    rows = []
    for i in range(len(cols["Text"])):
        rows.append({"label": cols["Text"][i], "indicator": bool(cols["Indicator"][i]), "uid": int(cols["ControlUID"][i]),
                     "is_source": bool(cols["IsSource"][i]), "wire": int(cols["WireUID"][i]),
                     "term_err": (errs.get("TermErr") or [0] * len(cols["Text"]))[i],
                     "wire_err": (errs.get("WireErr") or [0] * len(cols["Text"]))[i]})
    return rows


OP_NODE_TERMS = os.path.join(CLAUDEDEV, "OpNodeTerms_v0.vi")
_NODE_TERMS_LABELS = None


def node_terms(target, diagram_index, node_index):
    """Every terminal of Nodes[node_index] on the `diagram_index`-th Diagram of `target`, in ONE op run:
    [{i, name, is_source, wire, name_err, src_err, conn_err, wire_err}] in Node.Terminals[] order (the same index
    net_map reads one by one). `is_source` TRUE = the terminal emits data (an output; on a global-variable node: a
    READ); `wire` = connected wire UID, 0 when bare (then conn_err/wire_err carry 1055 and name_err/src_err are 0).
    Each property sits on its own node with its own error chain, so one failing property never defaults the
    others (peer review 2026-09-14). Built by tools/recipes/build_opnodeterms_v0.py from donor OpNetInfo_v1 with
    its junk-dropping creator deleted (0 junk per call - the reason to prefer this over net_map for one node).
    Verification level: see tools/bench/test_opnodeterms.log."""
    global _NODE_TERMS_LABELS
    if _NODE_TERMS_LABELS is None:
        import json
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "bench", "opnodeterms_labels.json"),
                  encoding="utf-8") as f:
            _NODE_TERMS_LABELS = {v: k for k, v in json.load(f).items()}
    lab = _NODE_TERMS_LABELS
    vi = op(OP_NODE_TERMS)
    vi.SetControlValue("vi path", target); vi.SetControlValue("Class Name", "Diagram")
    vi.SetControlValue("index", diagram_index); vi.SetControlValue("index 2", node_index); vi.SetControlValue("index 3", 0)
    for k, v in (("error in (no error)", (False, 0, "")), ("error in", (True, 1, "neutralised creator")),
                 ("Class Name 3", ""), ("Class Name 2", "")):
        try:
            vi.SetControlValue(k, v)
        except Exception:
            pass
    _run(vi)
    # The donor's node-UID reader (PN 'UID' fed from Nodes[][index 2]) survives in this op: the NODE's own GObject.UID
    # comes back with the rows, so a caller can verify identity instead of trusting a cached Nodes[] order (peer
    # 2026-09-14: order is not documented to persist across a LabVIEW restart). 0 = the node index was out of range.
    try:
        node_uid = int(vi.GetControlValue("UID"))
    except Exception:
        node_uid = None
    names = list(vi.GetControlValue(lab["Name"]))
    src = [bool(x) for x in vi.GetControlValue(lab["IsSource"])]
    wire = [int(x) for x in vi.GetControlValue(lab["WireUID"])]

    def errs(key):
        if key not in lab:
            return [0] * len(names)
        try:
            return [int(tuple(e)[1]) if tuple(e)[0] else 0 for e in vi.GetControlValue(lab[key])]
        except Exception:
            return [0] * len(names)
    ne, se, ce, we = errs("NameErr"), errs("SrcErr"), errs("ConnErr"), errs("WireErr")
    rows = []
    for i in range(len(names)):
        rows.append({"i": i, "name": names[i], "is_source": src[i] if i < len(src) else None,
                     "wire": wire[i] if i < len(wire) else 0,
                     "name_err": ne[i] if i < len(ne) else 0, "src_err": se[i] if i < len(se) else 0,
                     "conn_err": ce[i] if i < len(ce) else 0, "wire_err": we[i] if i < len(we) else 0,
                     "node_uid": node_uid})
    return rows


def node_terms_uid(target, diagram_index, node_index):
    """(node_uid, rows) - node_terms plus the node's own UID even when it has no terminals (0 = index out of range)."""
    rows = node_terms(target, diagram_index, node_index)
    if rows:
        return rows[0]["node_uid"], rows
    vi = op(OP_NODE_TERMS)
    try:
        return int(vi.GetControlValue("UID")), rows
    except Exception:
        return None, rows


OP_TUNNELS = os.path.join(CLAUDEDEV, "OpTunnels_v0.vi")
_TUNNELS_LABELS = None


def tunnels(target, index):
    """The `index`-th LoopTunnel of `target` (Traverse 'LoopTunnel' order - an access index, not an identity):
    {uid, index_mode, out_name, out_is_source, out_wire, out_conn_err, out_wire_err, in_names, in_is_source,
    in_wires} - uid 0 = index past the end. Outer wire = the parent diagram's wire, inner wires = one per frame (a
    loop: exactly one). Built 2026-09-14 (tools/recipes/build_optunnels_v0.py, donor OpSetIndexMode_v0: Traverse ->
    IA -> To More Specific Class(LoopTunnel) -> Tunnel[Outside Terminal, Inside Terminals[], IndexMode, UID] ->
    per-property Terminal nodes). Verified tools/bench/test_optunnels.log. Shift registers are NOT LoopTunnels
    (LeftShiftRegister / RightShiftRegister) - not covered."""
    global _TUNNELS_LABELS
    if _TUNNELS_LABELS is None:
        import json
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "bench", "optunnels_labels.json"),
                  encoding="utf-8") as f:
            _TUNNELS_LABELS = {v: k for k, v in json.load(f).items()}
    lab = _TUNNELS_LABELS
    vi = op(OP_TUNNELS)
    vi.SetControlValue("vi path", target)
    try:
        vi.SetControlValue("vi path 2", target)
    except Exception:
        pass
    vi.SetControlValue("Class Name", "LoopTunnel"); vi.SetControlValue("index", int(index))
    _run(vi)

    def err(key):
        try:
            e = tuple(vi.GetControlValue(lab[key])); return int(e[1]) if e[0] else 0
        except Exception:
            return None
    return {"index": int(index), "uid": int(vi.GetControlValue(lab["TunnelUID"])),
            "index_mode": int(vi.GetControlValue(lab["IndexMode"])),
            "out_name": vi.GetControlValue(lab["OutName"]), "out_is_source": bool(vi.GetControlValue(lab["OutIsSource"])),
            "out_wire": int(vi.GetControlValue(lab["OutWireUID"])), "out_conn_err": err("OutConnErr"), "out_wire_err": err("OutWireErr"),
            "in_names": list(vi.GetControlValue(lab["InName"])),
            "in_is_source": [bool(x) for x in vi.GetControlValue(lab["InIsSource"])],
            "in_wires": [int(x) for x in vi.GetControlValue(lab["InWireUID"])]}


OP_CONNECT_CTL = os.path.join(CLAUDEDEV, "OpConnectCtl_v0.vi")
_CONNECT_CTL_LABELS = None


def connect_ctl(target, panel_index, node_index, terminal_index):
    """Wire Nodes[node_index].Terminals[terminal_index] (a SOURCE) into the terminal of front-panel object
    Panel.Controls[panel_index] (fp_labels order) with Terminal.Connect Wire invoked on the panel object's own terminal
    (Panel.Controls[] -> Control.Terminal, cast-free). Built 2026-09-14 for panel objects erdosmiller's Wire Indicators
    cannot see (a Vision IMAQ Image Display). Returns the invoke's error text (None = no error). Verify by EFFECT:
    panel_wiring(target) must show the object's terminal wire != 0 and exec_state == 1 BEFORE any Remove Bad Wires."""
    global _CONNECT_CTL_LABELS
    if _CONNECT_CTL_LABELS is None:
        import json
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "bench", "opconnectctl_labels.json"),
                  encoding="utf-8") as f:
            _CONNECT_CTL_LABELS = json.load(f)
    lab = _CONNECT_CTL_LABELS
    vi = op(OP_CONNECT_CTL)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("index", int(panel_index))
    vi.SetControlValue(lab["index_node"], int(node_index))
    vi.SetControlValue(lab["index_terminal"], int(terminal_index))
    _run(vi)
    return _err(vi, lab["error"])


def count(target, cls):
    vi = op(OP_REPORT)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", cls)
    vi.SetControlValue("index", 0)
    _run(vi)
    err = _err(vi)
    if err:
        raise RuntimeError(f"count({cls}) on {os.path.basename(target)}: {err}")
    return int(vi.GetControlValue("# of Refs"))


def uids(target, cls):
    # report_all, not report: one op run instead of one per object (rows verified IDENTICAL 2026-09-13). With
    # report() this was the hidden O(n) inside delete_object's before/after check, which made a J-object purge
    # O(J^2) op runs - the cause of the 12-min timeout in tools/bench/probe_attach_reader2c.log (2026-09-14).
    return {o["uid"] for o in report_all(target, cls)}


def new_since(target, cls, before):
    """The objects of `cls` that appeared since the `before` uid set.

    Use this, NOT position matching, to identify what a mutating Op just created. Positions inside a
    subdiagram are reported in a shifted coordinate space, and a pre-existing object can sit closer
    to the requested location than the new one - which is exactly how a wrong object gets reported
    as the result of a successful build.
    """
    return [o for o in report(target, cls) if o["uid"] not in before]


# A For Loop's body Diagram reports its position at exactly loop_pos + this offset.
# Measured 2026-08-28 on three loops 700 px apart: offset (10, 22) every time, with the
# nearest diagram 32 away and the next nearest 688+ - a 21x margin, so selecting a loop's
# subdiagram by position is unambiguous, not a heuristic.
LOOP_DIAGRAM_OFFSET = (10, 22)


def loop_diagram(target, loop_pos, min_margin=4.0):
    """The body Diagram of the For Loop at `loop_pos`, selected deterministically.

    Verifies the choice is unambiguous: the runner-up diagram must be at least
    `min_margin` times farther away. Raises rather than guessing.
    """
    want = (loop_pos[0] + LOOP_DIAGRAM_OFFSET[0], loop_pos[1] + LOOP_DIAGRAM_OFFSET[1])
    dias = [d for d in report(target, "Diagram") if d["owner"] == "ForLoop"]
    if not dias:
        raise RuntimeError("no ForLoop-owned Diagram in " + os.path.basename(target))
    scored = sorted((abs(d["pos"][0] - want[0]) + abs(d["pos"][1] - want[1]), d) for d in dias)
    best_d, best = scored[0][0], scored[0][1]
    if len(scored) > 1 and scored[1][0] < best_d * min_margin:
        raise RuntimeError(
            "ambiguous loop subdiagram near %s: nearest %d, runner-up %d"
            % (want, best_d, scored[1][0]))
    return best


def find_at(target, cls, pos, tol=40):
    """Index of the `cls` object nearest `pos` - the deterministic selector.

    Creation Ops take a `location`, so the caller always knows where its own structure is. Traverse
    order is unspecified and must never be used as a selector.
    """
    best, bestd = None, None
    for o in report(target, cls):
        d = abs(o["pos"][0] - pos[0]) + abs(o["pos"][1] - pos[1])
        if bestd is None or d < bestd:
            best, bestd = o, d
    if best is None or bestd > tol:
        raise RuntimeError(f"no {cls} within {tol} of {pos} in {os.path.basename(target)}")
    return best


# --- write ------------------------------------------------------------------------------------

OP_EXITWHILE = os.path.join(CLAUDEDEV, "OpExitWhile_v0.vi")
_EXITWHILE_LABELS = None


def exit_while(target, stop_control, diagram_index, node_index=0, output_names=(), node_class="SubVI",
               shift_names=()):
    """Finish a scripted While loop: wire its conditional terminal from the front-panel Boolean control labelled
    `stop_control` (erdosmiller Exit While Loop.vi 'Stop Condition' <- Get Controls by name) and, optionally, create
    output tunnels for `output_names` of Traverse node_class[node_index] inside the loop (as exit_loop does for For
    loops). `diagram_index` = the loop BODY's Traverse 'Diagram' index (identify it by UID, NAMES.md). OpExitWhile_v0,
    built 2026-09-14 (tools/recipes/build_opexitwhile.py).

    `shift_names` = outputs of the SAME node that become SHIFT REGISTERS instead of plain output tunnels (the op's
    'Names 2' -> the donor's second Get Outputs -> Exit While Loop's 'Shift Registers' input). Until 2026-09-14 this
    was hard-wired to [] and never exercised; stage 2 needs it for the kernel's x,y,z / good-flags / pos-in-cal
    feedback (docs/stage2-assembly-step-a.md). The LEFT side of a register created this way is left unwired - its
    initial value and its body reader are separate wiring steps."""
    global _EXITWHILE_LABELS
    if _EXITWHILE_LABELS is None:
        import json
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "bench", "opexitwhile_labels.json"),
                  encoding="utf-8") as f:
            _EXITWHILE_LABELS = json.load(f)
    ensure_loaded(target)   # edits are silently declined on a target that is not fully loaded
    vi = op(OP_EXITWHILE)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", node_class); vi.SetControlValue("index", node_index)
    vi.SetControlValue("Names", list(output_names))
    vi.SetControlValue("Class Name 2", "Diagram"); vi.SetControlValue("index 2", diagram_index)
    vi.SetControlValue("Names 2", [])
    vi.SetControlValue(_EXITWHILE_LABELS["stop_names"], [stop_control])
    dt = _run(vi)
    err = _err(vi)
    if err:
        raise RuntimeError(f"exit_while: {err}")
    return dt


_QUEUE_OPS = {"obtain": "OpQueueObtain_v0.vi", "enqueue": "OpQueueEnqueue_v0.vi",
              "dequeue": "OpQueueDequeue_v0.vi", "release": "OpQueueRelease_v0.vi"}
_QUEUE_LABELS = {}


def queue_node(kind, target, src_cls, src_index, src_name, diagram_index, location, element_name=None):
    """Place one queue primitive on Traverse 'Diagram'[diagram_index] of `target` (erdosmiller Create Obtain Queue /
    Enqueue Element / Dequeue Element / Release Queue through OpQueue*_v0, built 2026-09-14, stage-2 toolkit gap 3).
    The refnum input comes from an OUTPUT terminal of an existing node chosen by name: Traverse src_cls[src_index]
    . src_name -> 'element data type' (obtain: the terminal whose TYPE the queue takes) / 'queue' (the others).
    enqueue: `element_name` = a second output of the SAME node (the op's second Get Outputs); leave None and wire the
    element afterwards with wire(...,'element') when it comes from another node. Returns (wire delta, new node uids)."""
    import json
    kind = kind.lower()
    if kind not in _QUEUE_LABELS:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "bench", f"opqueue_{kind}_labels.json"),
                  encoding="utf-8") as f:
            _QUEUE_LABELS[kind] = json.load(f)
    lab = _QUEUE_LABELS[kind]
    before = uids(target, "Function")
    vi = op(os.path.join(CLAUDEDEV, _QUEUE_OPS[kind]))
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", src_cls); vi.SetControlValue("index", src_index)
    vi.SetControlValue("Names", [src_name])
    vi.SetControlValue("Class Name 2", "Diagram"); vi.SetControlValue("index 2", diagram_index)
    vi.SetControlValue("Names 2", [element_name] if element_name else [])
    vi.SetControlValue(lab["location"], list(location))
    _run(vi)
    err = _err(vi)
    new = [u for u in uids(target, "Function") if u not in before]
    if err:
        raise RuntimeError(f"queue_node({kind}): {err} (new nodes {new})")
    return new


_LOOPIN_LABELS = {}


def loop_in(kind, target, diagram_index, location, src_cls=None, src_index=0, src_names=(), indexing=(), parallel=0):
    """Create a For ('for') or While ('while') loop on Traverse 'Diagram'[diagram_index] of `target` (OpForLoopIn_v0 /
    OpWhileLoopIn_v0, built 2026-09-14 from the OpExitLoop_v0 donor - stage 2 needs loops INSIDE loops). Input
    tunnels come from OUTPUT terminals of one existing node: Traverse src_cls[src_index] . src_names (Get Outputs);
    `indexing` = per-tunnel auto-index flags; `parallel` = static parallel instances (For). `location` is body-relative.
    Identify the new body afterwards by Diagram UID (NAMES.md rule). Returns the new loop's uid."""
    import json
    kind = kind.lower()
    if kind not in _LOOPIN_LABELS:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "bench", f"oploopin_{kind}_labels.json"),
                  encoding="utf-8") as f:
            _LOOPIN_LABELS[kind] = json.load(f)
    lab = _LOOPIN_LABELS[kind]
    cls = "ForLoop" if kind == "for" else "WhileLoop"
    before = uids(target, cls)
    vi = op(os.path.join(CLAUDEDEV, "OpForLoopIn_v0.vi" if kind == "for" else "OpWhileLoopIn_v0.vi"))
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", src_cls or "SubVI"); vi.SetControlValue("index", src_index)
    vi.SetControlValue("Names", list(src_names))
    vi.SetControlValue("Class Name 2", "Diagram"); vi.SetControlValue("index 2", diagram_index)
    vi.SetControlValue("Names 2", [])
    vi.SetControlValue(lab["location (0, 0)"], list(location))
    vi.SetControlValue(lab["Inputs Indexing?"], list(indexing))
    if kind == "for":
        vi.SetControlValue(lab["Number of Static Parallel Instances"], parallel)
    _run(vi)
    err = _err(vi)
    new = [u for u in uids(target, cls) if u not in before]
    if err:
        raise RuntimeError(f"loop_in({kind}): {err} (new {new})")
    return new[0] if len(new) == 1 else new


OP_WHILELOOP = os.path.join(CLAUDEDEV, "OpWhileLoop_v0.vi")


def while_loop(target, location, tunnels=(), indexing=()):
    """Create a While loop on `target`'s top-level diagram at `location` (erdosmiller Create While Loop.vi through
    OpWhileLoop_v0, built 2026-09-14 from OpForLoop_v0 with Get Controls.'Control Terminals' wired into the creator's
    'Inputs' - the For op never had that wire, which is why its 'Control Names' produced no tunnels). `tunnels` =
    labels of EXISTING front-panel controls to bring in as input tunnels, `indexing` = per-tunnel auto-index flags.
    The new loop's conditional terminal is UNWIRED (ExecState 0 until OpExitWhile / a stop control is wired)."""
    ensure_loaded(target)   # edits are silently declined on a target that is not fully loaded
    vi = op(OP_WHILELOOP)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("location (0, 0)", list(location))
    vi.SetControlValue("Control Names", list(tunnels))
    vi.SetControlValue("Inputs Indexing?", list(indexing))
    dt = _run(vi)
    err = _err(vi)
    if err:
        raise RuntimeError(f"while_loop: {err}")
    return dt


def for_loop(target, location, tunnels=(), indexing=(), parallel=0):
    ensure_loaded(target)   # edits are silently declined on a target that is not fully loaded
    vi = op(OP_FORLOOP)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("location (0, 0)", list(location))
    vi.SetControlValue("Control Names", list(tunnels))
    vi.SetControlValue("Inputs Indexing?", list(indexing))
    vi.SetControlValue("Number of Static Parallel Instances", parallel)
    dt = _run(vi)
    err = _err(vi)
    if err:
        raise RuntimeError(f"for_loop: {err}")
    return dt


def drop_subvi(target, subvi_path, diagram_index, location):
    """Place `subvi_path` on the target's `diagram_index`-th Diagram. Get the index from find_at."""
    ensure_loaded(target)   # edits are silently declined on a target that is not fully loaded
    vi = op(OP_SUBVI)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("vi path 2", subvi_path)
    vi.SetControlValue("Class Name", "Diagram")
    vi.SetControlValue("index", diagram_index)
    vi.SetControlValue("location (0, 0)", list(location))
    dt = _run(vi)
    err = _err(vi)
    if err:
        raise RuntimeError(f"drop_subvi: {err}")
    return dt


def open_panel(target, activate=False):
    """Open the target's front panel - REQUIRED before wire() AND before drop_subvi().

    Wiring a target loaded only via GetVIReference is silently declined (count
    unchanged, no error): the diagram is not fully in memory. OpenFrontPanel forces
    the full load. Discovered 2026-08-28 after three silent failures.

    activate defaults to False since 2026-09-05: OpenFrontPanel(activate=True) followed by an
    lv_gui `focus` (Alt tap) left LabVIEW's UI loop in a state where the next COM Run blocked
    until a mouse click (test H5, 4/4 reproducible); activate=False never did (H6). Loading
    does not need activation. Pass activate=True only when the panel must come to the front.
    """
    with vi_ref(target) as r:                          # P3: counted + released (was an unclosed ref/call)
        _invoke(r, "OpenFrontPanel", bool(activate), 1)


def close_panel(target):
    """Close the target's front panel. SAVE FIRST: closing the panel of a modified VI
    while holding no other reference unloads it and silently discards every edit
    (a full chain build evaporated this way on 2026-08-28)."""
    with vi_ref(target) as r:                          # P3: counted + released
        _invoke(r, "CloseFrontPanel")


_loaded = set()


def ensure_loaded(target):
    """Put `target` into the state in which scripting EDITS actually land, before every edit. Idempotent, once
    per session per path. The state is reached by OPENING ITS FRONT PANEL, and the name of this function is a
    leftover from a mechanism that has since been REFUTED - read the second block below before changing it.

    ⚠️ THE MECHANISM IS NOT "THE DIAGRAM IS IN MEMORY" (measured 2026-09-16, tools/bench/diag_load_vs_editmode.log,
    after codex attacked the first explanation in archive/peer/2026-09-16-openpanel-ab.md). Same raw op, fresh copy
    of OpFPLabels_v0.vi per arm, class Property, index 0:

        nothing first                                        4 -> 4   NOTHING removed
        read VI.Block Diagram (23C) first, NO window opened   4 -> 4   NOTHING removed
        OpenFrontPanel(activate=False) first                  4 -> 3   removed uid 115
        23C-loaded, panel-less, GObject.Move instead          (853,300) -> (853,300)   DID NOT MOVE

    `VI.Block Diagram` is the property labviewwiki marks "Loads the block diagram into memory: Yes", and it opened
    no window (Win32 census inside the run: 6 windows after the 23C arm, 7 after the panel arm). It was NOT enough
    for either mutator. So the operational rule is: OPEN THE PANEL BEFORE ANY EDIT, and reading the documented
    load primitive is not a substitute - do not "optimise the window away" on the strength of NI's table.

    WHAT IS STILL NOT KNOWN, and must not be written as if it were: WHY the panel is what works. "OpenFrontPanel
    supplies edit-mode/UI context" is an INFERENCE. Codex refuted the measurement's reach
    (archive/peer/2026-09-16-load-vs-editmode-23c-r2.md, ANSWERED): the 23C read happened inside a SEPARATE op VI
    that then returned, and NI closes a top-level VI's references when it goes idle - so the diagram may have been
    unloaded again before the delete ran, and residency was never actually held at mutation time. Deciding it needs
    ONE op VI that reads 23C, reads Metrics:Block Diagram Loaded (292) and deletes, with the diagram ref kept live
    by data dependency and no window opened. Two attempts at a standalone flag reader failed identically
    (tools/bench/diag_bdloaded_reader.log): the branch into a VI-class Property Node's `reference` lands as a BAD
    wire (uid 467, ExecState 0, remove_bad_wires does not clear it).

    COSTS OF THIS CALL, from codex's harm list - accepted with it, not waved away: OpenFrontPanel activates the
    window by default (this project passes activate=False since 2026-09-05), a Run-When-Opened VI starts executing
    on open and then cannot be edited, an open panel conflicts with SubPanel Insert VI, panel redraw costs UI time
    on complex panels, and closing a panel can let the VI leave memory (see close_panel - a whole chain build was
    lost that way on 2026-08-28).

    The original A/B that justified inserting this call is still valid as a MEASUREMENT
    (tools/bench/diag_delete_matrix.log, 2026-09-16). Same op, same target, same class, same index - only this
    call differs:

        without open_panel   OpWireSource_v5 Property 12 -> 12   NOTHING REMOVED, run returned, error out clean
        with    open_panel   OpWireSource_v5 Property 12 -> 11   removed one
        without open_panel   OpFPLabels_v0   Property  4 ->  4   NOTHING REMOVED
        with    open_panel   OpFPLabels_v0   Property  4 ->  3   removed one

    and with it EVERY class works: Constant, Property, SubVI, IndexArray, Wire, ControlTerminal all removed
    exactly one, none removed an object of another class.

    The SYMPTOM was written down in `open_panel`'s own docstring on 2026-08-28 and never generalised beyond
    wire()/drop_subvi(): "Wiring a target loaded only via GetVIReference is SILENTLY DECLINED (count unchanged,
    no error)". That sentence's diagnosis - "the diagram is not fully in memory" - is the part now REFUTED by the
    23C arm above; the symptom and the cure it named are both still correct. NI's note that `Generic.Delete` is
    marked "Loads the block diagram into memory: No" (codex, archive/peer/2026-09-16-delete-silent-noop2.md)
    explains only why the method cannot help itself, not what OpenFrontPanel supplies. And because
    "Generic.Delete has no semantic return value at all - its contract is the side effect", a clean error cluster
    was never evidence that anything happened.

    WHY IT IS CACHED. OpenFrontPanel is ~0.1 s and idempotent, but a mutating recipe makes hundreds of calls; one
    per target per session is enough because nothing here ever closes a panel. `reset()` clears the cache, since a
    killed or restarted LabVIEW has forgotten every load.

    WHY READERS DO NOT CALL IT. report/report_all/subvis/node_terms/panel_wiring work perfectly on a
    GetVIReference-only load, and the main VI is read CONSTANTLY - popping its front panel would be both
    disruptive and contrary to rule 1d's "prefer headless COM reads". Only EDITS need this.
    """
    key = os.path.normcase(os.path.abspath(target))
    if key in _loaded:
        return False
    open_panel(target)
    _loaded.add(key)
    return True


def wire(target, src_cls, src_i, src_term, dst_cls, dst_i, dst_term, branch=False):
    """Node-to-node wire by terminal name. Call open_panel(target) first, and save
    before close_panel() - see those helpers. Control/indicator terminals are class
    Terminal, not Node, and this cannot reach them - see the skill.

    Semantics learned 2026-08-28: a MISSING destination name raises 5001 inside the
    Op (cleared silently by OpWire_v1's sinks; count check catches it); a FOUND name
    whose connect is illegal is declined silently; branching from an ALREADY-WIRED
    source terminal is also declined silently. Unwired error INPUTS are harmless -
    only an unwired error OUT that receives an error raises a dialog.

    BOUNDARY CROSSINGS - the count is a RANGE, not a formula (2026-09-13, corrected 09-14).
    Wiring into or out of a loop creates a TUNNEL, and the connection may be split into an
    outside segment and an inside segment. The original flat `+1` check rejected three probe
    runs whose wires had actually succeeded. The first fix assumed each crossing adds exactly
    one extra segment (`expected = 1 + tunnels`) - and that was rejected in turn by a real
    build: `Nodes[] -> reference` reported 14 -> 15 wires with ONE new tunnel, i.e. +1, not +2.

    Both happen, because LabVIEW is free to MERGE a new segment with an existing one. So the
    honest contract is a range: at least one new wire, at most one per boundary crossed.
    Tightening it further would be inventing a rule the observations do not support; the
    definitive check on a crossing is the EFFECT (ExecState, or the tunnel appearing), which
    the callers already make."""
    ensure_loaded(target)   # edits are silently declined on a target that is not fully loaded
    before = count(target, "Wire")
    tun_before = count(target, "LoopTunnel")
    vi = op(OP_WIRE)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", src_cls)
    vi.SetControlValue("index", src_i)
    vi.SetControlValue("Names", [src_term])
    vi.SetControlValue("Class Name 2", dst_cls)
    vi.SetControlValue("index 2", dst_i)
    vi.SetControlValue("Names 2", [dst_term])
    _run(vi)
    err = _err(vi)   # readable since 2026-08-29: error out indicator branched onto the chain
    if err:
        raise RuntimeError(f"wire {src_term}->{dst_term}: {err}")
    after = count(target, "Wire")
    crossings = max(0, count(target, "LoopTunnel") - tun_before)
    lo, hi = before + 1, before + 1 + crossings
    if not branch and not (lo <= after <= hi):
        expected = f"{lo}..{hi}" if hi > lo else str(lo)
        # A BRANCH from an already-wired source does NOT add a Wire object (the wire
        # owns all its sinks), so this check misreads a successful branch as a decline.
        # For branches pass branch=True and verify by effect (ExecState, probe).
        raise RuntimeError(
            f"wire {src_term}->{dst_term}: wire count {before}->{after} with {crossings} new tunnel(s), "
            f"expected {expected} (if the source is already wired this may be a successful BRANCH - "
            "re-call with branch=True)")
    return after


def revert(target):
    """Discard a VI's in-memory changes by reloading from disk (VI method Revert)."""
    with vi_ref(target) as r:                          # P3: counted + released
        _invoke(r, "Revert")


def copy_into(donor, label, target, prepare=None):
    """Copy the object labeled `label` from `donor` INTO `target`.

    move_by_label() drops the copy on the Move example's fixed Test-Target; this
    substitutes `target`'s bytes into that file first, so the copy lands in the real
    VI, then saves and copies it back. Both example files are restored afterwards.

    Used to give an Op an `error out` indicator. NOTE (2026-09-03): "the fleet cannot create
    front-panel objects" is a statement about THIS FLEET, not about LabVIEW - VI Scripting
    creates FP controls/indicators with `New VI Object` (front-panel owner + a control style
    from the ring: 'Numeric Indicator (classic)', 'Array (classic)', ...). We never built that
    op because the ring's style codes were unreadable; `RingConstant.Strings And Values[]`
    (confirmed 2026-09-01) removes that blocker. Until an OpNewFPObject exists, copying from a
    donor Op is the working path.
    """
    import shutil
    ensure_move_files_pristine()
    src_bak = MOVE_SRC + ".ci_src"
    dst_bak = MOVE_DST + ".ci_dst"
    shutil.copyfile(MOVE_SRC, src_bak)
    shutil.copyfile(MOVE_DST, dst_bak)
    try:
        for p, newbytes in ((MOVE_SRC, donor), (MOVE_DST, target)):
            try:
                revert(p)
            except Exception:
                pass
            shutil.copyfile(newbytes, p)
            try:
                revert(p)
            except Exception:
                pass
        if prepare:
            prepare(MOVE_SRC)          # e.g. set_node_label on an unlabeled donor node (2026-09-08)
        before = uids(MOVE_DST, "GObject")
        vi = op(OP_MOVE_LABEL)
        vi.SetControlValue("Add Label", label)
        _run(vi)
        added = new_since(MOVE_DST, "GObject", before)
        if not added:
            raise RuntimeError(f"copy_into({label!r}): nothing was copied")
        # A freshly copied primitive has unwired required inputs, so the target is legally
        # BROKEN at this instant. That is expected mid-assembly, not a failure - divert to
        # the editor's own File > Save, which handles a broken VI (see gui_save).
        save(MOVE_DST, allow_broken=True)
        shutil.copyfile(MOVE_DST, target)
        return added
    finally:
        shutil.copyfile(src_bak, MOVE_SRC)
        shutil.copyfile(dst_bak, MOVE_DST)
        os.remove(src_bak)
        os.remove(dst_bak)
        for p in (MOVE_SRC, MOVE_DST):
            try:
                revert(p)
            except Exception:
                pass


OP_MOVE_INDEX = os.path.join(CLAUDEDEV, "OpMoveByIndex_v0.vi")
_MOVE_INDEX_LABELS = None


MOVE_DST_ORIG = MOVE_DST + ".ORIG.bak"


def restore_move_fixtures():
    """Put the two Move-example files back to their pristine bytes - ONLY when nothing of theirs is loaded (call it
    at the START of a copy, never in a finally while a VI may still be in memory: peer
    archive/peer/2026-09-15-strtopath-fail4-gui-save-of-broken-target.md - restoring the disk under a loaded, dirty
    VI creates the changed-on-disk split-brain that needs a LabVIEW restart)."""
    import shutil
    # FILE OPERATIONS ONLY - no revert()/COM here: ensure_move_files_pristine() reverts (= loads) a restored file,
    # and a byte substitution after a load fails with EINVAL (queue run 2, 03:3x). The caller reverts afterwards.
    for live, orig in ((MOVE_SRC, MOVE_SRC_ORIG), (MOVE_DST, MOVE_DST_ORIG)):
        if not os.path.exists(orig):
            shutil.copyfile(live, orig)
        shutil.copyfile(orig, live)


def copy_by_index(donor, cls, index, target, expect_uid=None, finish=None):
    """Copy the `index`-th object of Traverse class `cls` (report() order) from `donor` INTO `target` BY REFERENCE —
    OpMoveByIndex_v0 (2026-09-15, built from OpMoveByLabel_v0 with the name lookup replaced by Traverse → Index
    Array; peer archive/peer/2026-09-15-strtopath-fail3-move-by-index-plan.md). Built-in primitives cannot be found by
    label or by name (error 1054 ×3), so this is the fleet's primitive-copier.

    Protocol (revised after ...-fail4-gui-save-of-broken-target): the two Move-example files are restored to pristine
    bytes and byte-substituted BEFORE anything is loaded; after the Move the substituted Target stays LOADED and
    `finish(MOVE_DST)` — the caller's hook — wires the copied primitive's required inputs (create_control /
    create_indicator / wire on that path) until the VI is RUNNABLE; then it is COM-saved ONCE (no keystroke save of a
    broken VI) and file-copied to `target`. Nothing is restored in a finally: on failure the run raises with the
    files left as they are and the next call's restore (with nothing loaded, or after a restart) cleans up.
    UID GUARD: the op exports the selected object's GObject.UID; when `expect_uid` differs the copy is REJECTED.
    Returns (added uids, selected uid)."""
    global _MOVE_INDEX_LABELS
    import shutil
    if _MOVE_INDEX_LABELS is None:
        import json
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "bench", "opmovebyindex_labels.json"),
                  encoding="utf-8") as f:
            _MOVE_INDEX_LABELS = json.load(f)
    lab = _MOVE_INDEX_LABELS
    # ORDER MATTERS (2026-09-15 03:3x, queue runs 1-2): close_panel() = GetVIReference() LOADS the example VI, and a
    # byte substitution attempted AFTER that load failed with a CRT-level EINVAL (errno 22, winerror None) - the
    # signature of a file the loaded VI holds. So: substitute the bytes FIRST, on an instance where nothing of
    # theirs is loaded (the caller restarts LabVIEW before a copy_by_index session), and only then touch them over COM.

    def _copy(label, src, dst):
        # 2026-09-15 03:16 (queue run 1): a bare "[Errno 22] Invalid argument: <Target path>" from one of these copies
        # could not be attributed (peer ...-queue-fail1-errno22: the winerror and which call were the missing data)
        try:
            if os.path.normcase(os.path.abspath(src)) == os.path.normcase(os.path.abspath(dst)):
                raise RuntimeError("source and destination are the same file")
            shutil.copyfile(src, dst)
        except Exception as e:
            raise RuntimeError(f"copy_by_index {label}: {type(e).__name__} errno={getattr(e, 'errno', None)} "
                               f"winerror={getattr(e, 'winerror', None)} src={src!r} ({os.path.getsize(src) if os.path.exists(src) else 'missing'} B) "
                               f"dst={dst!r} ({os.path.getsize(dst) if os.path.exists(dst) else 'missing'} B): {e}") from e
    restore_move_fixtures()
    _copy("donor -> MOVE_SRC", donor, MOVE_SRC); _copy("target -> MOVE_DST", target, MOVE_DST)
    for p in (MOVE_SRC, MOVE_DST):
        try:
            revert(p)
        except Exception:
            pass
    before = uids(MOVE_DST, "GObject")
    vi = op(OP_MOVE_INDEX)
    vi.SetControlValue(lab["class_name"], cls); vi.SetControlValue(lab["index"], int(index))
    vi.SetControlValue(lab["duplicate"], True)
    vi.SetControlValue(lab["traverse_target"], 1)          # 1 = BD (0 = FP): required ring on Traverse for GObjects
    _run(vi)
    sel = int(vi.GetControlValue(lab["selected_uid"]))
    added = new_since(MOVE_DST, "GObject", before)
    if expect_uid is not None and sel != expect_uid:
        raise RuntimeError(f"copy_by_index: selected uid {sel} != expected {expect_uid} - target rejected (rebuild it)")
    if not added:
        raise RuntimeError(f"copy_by_index({cls}[{index}]): nothing was copied (selected uid {sel})")
    if finish is not None:
        open_panel(MOVE_DST)
        # `added` is the ONLY authoritative identity of what this copy created: it is a before/after delta taken in
        # the same loaded object universe. A recipe that computes its own delta around the call compares uids across
        # a reload boundary and is invalid (peer 2026-09-15-opwiresource-v2-fail1-and-tunnelread-plan). Hooks that
        # accept a second argument receive it; one-argument hooks keep working.
        try:
            finish(MOVE_DST, added)                 # make the VI runnable here, on the loaded Target
        except TypeError as e:
            if "positional argument" not in str(e):
                raise
            finish(MOVE_DST)
    es = exec_state(MOVE_DST)
    if es != 1:
        raise RuntimeError(f"copy_by_index: Target still broken after finish (ExecState {es}) - not saved; "
                           "close without saving / restart before the next attempt")
    save(MOVE_DST)                                  # COM save of a RUNNABLE VI
    try:
        close_panel(MOVE_DST)
    except Exception:
        pass
    shutil.copyfile(MOVE_DST, target)
    return added, sel


def move_by_label(donor, label, harvest_to=None):
    """Copy the GObject labeled `label` out of `donor` via OpMoveByLabel_v0.

    Substitution protocol (the op's source/target are fixed static refs):
      1. revert the two Test files so stale in-memory copies cannot shadow new bytes,
      2. byte-substitute Test-Source with the donor,
      3. run the op (Add Label = label); the copy lands on Test-Target's top-level
         diagram at (0,75),
      4. verify by uid diff on Test-Target; optionally save it and file-copy the
         result to `harvest_to`,
      5. restore Test-Source's original bytes.

    Returns the new object's report dict. The caller usually follows with another
    edit pass that wires/moves the harvested object where it belongs.
    """
    import shutil
    ensure_move_files_pristine()
    bak = MOVE_SRC + ".move_bak"
    shutil.copyfile(MOVE_SRC, bak)
    try:
        try:
            revert(MOVE_DST)
        except Exception:
            pass
        shutil.copyfile(donor, MOVE_SRC)
        try:
            revert(MOVE_SRC)
        except Exception:
            pass
        before = uids(MOVE_DST, "GObject")
        vi = op(OP_MOVE_LABEL)
        vi.SetControlValue("Add Label", label)
        _run(vi)
        added = new_since(MOVE_DST, "GObject", before)
        roots = [o for o in added if o["owner"] == "TopLevelDiagram"]
        if not added:
            raise RuntimeError(f"move_by_label({label!r}): nothing copied")
        if harvest_to:
            size = save(MOVE_DST)
            shutil.copyfile(MOVE_DST, harvest_to)
        return (roots or added)[0]
    finally:
        shutil.copyfile(bak, MOVE_SRC)
        os.remove(bak)


def ensure_move_files_pristine():
    """Restore the Move example's Test-Source if a previous run left a donor in it.

    Call at the START of any substitution-protocol operation: a run killed mid-way
    never reaches its finally block, so the file may still hold foreign bytes.
    """
    import shutil
    restored = False
    for live, orig in ((MOVE_SRC, MOVE_SRC_ORIG), (MOVE_DST, MOVE_DST_ORIG)):
        if not os.path.exists(orig):
            shutil.copyfile(live, orig)            # first run: adopt current as pristine
            continue
        if os.path.getsize(live) != os.path.getsize(orig):
            shutil.copyfile(orig, live)
            try:
                revert(live)
            except Exception:
                pass
            restored = True
    return restored


def remove_bad_wires(target):
    """Edit > Remove Broken Wires on `target` (the Ctrl+B cleanup).

    Deleting a node leaves dangling wires, which break the VI, and save() refuses a
    BROKEN VI. The VI-class method 'Block Diagram:Remove Bad Wires' exists but is NOT
    exposed through the ActiveX VirtualInstrument interface (probed 2026-08-28: no
    dispid under any spelling), so this drives the menu bar - the one GUI route that
    works reliably (injected right-clicks open nothing; see the skill).

    Coordinates are stable because the window is first moved to a known geometry.
    """
    base = os.path.basename(target)
    open_panel(target)
    fp = base + " Front Panel"
    bd = base + " Block Diagram"
    # Move the panel to a known origin FIRST. Menu-bar coordinates are relative to the
    # window, and a panel that opened anywhere on screen sent the clicks into empty
    # space - the block diagram then never opened and the cleanup silently did nothing
    # (2026-08-28). Never click a menu without pinning the window first.
    _lv_gui("-Action", "movewin", "-Title", "'%s'" % fp,
            "-Left", "0", "-Top", "0", "-Width", "1000", "-Height", "700")
    _lv_gui("-Action", "focus", "-Title", "'%s'" % fp)
    _lv_gui("-Action", "click", "-X", "293", "-Y", "41", "-Exception", "Approved", "-Evidence", "remove_bad_wires: documented menu recipe (skill gui-recipes.md), no scripting path for Remove Broken Wires over COM")     # Window menu
    time.sleep(0.9)
    _lv_gui("-Action", "click", "-X", "343", "-Y", "62", "-Exception", "Approved", "-Evidence", "remove_bad_wires: documented menu recipe (skill gui-recipes.md), no scripting path for Remove Broken Wires over COM")     # Show Block Diagram
    time.sleep(1.2)
    _lv_gui("-Action", "movewin", "-Title", "'%s'" % bd,
            "-Left", "0", "-Top", "0", "-Width", "1400", "-Height", "900")
    _lv_gui("-Action", "focus", "-Title", "'%s'" % bd)
    _lv_gui("-Action", "click", "-X", "58", "-Y", "41", "-Exception", "Approved", "-Evidence", "remove_bad_wires: documented menu recipe (skill gui-recipes.md), no scripting path for Remove Broken Wires over COM")      # Edit menu
    time.sleep(1.2)
    _lv_gui("-Action", "click", "-X", "123", "-Y", "345", "-Exception", "Approved", "-Evidence", "remove_bad_wires: documented menu recipe (skill gui-recipes.md), no scripting path for Remove Broken Wires over COM")    # Remove Broken Wires
    time.sleep(0.8)
    return exec_state(target)


def delete_by_label(target, label, allow_broken=False):
    """Delete the object labeled `label` from `target` (Generic:Delete).

    `allow_broken` keeps going when the deletion legitimately leaves the VI broken -
    e.g. removing the node that fed a REQUIRED input of the node after it, which is the
    normal state mid-swap. Bad wires are still cleaned; only the refusal is lifted, and
    the save is routed through gui_save (COM SaveInstrument hangs on a broken VI).

    Like move_by_label this drives a fixed-static-ref Op through the substitution
    protocol, but here the edit happens IN the substituted source, so the result is
    saved and copied back over `target`.

    Returns the set of uids that disappeared. Deleting a node leaves its wires broken -
    LabVIEW's Edit > Remove Broken Wires (VI method 'Block Diagram:Remove Bad Wires')
    is the cleanup, not yet scripted here.
    """
    import shutil
    ensure_move_files_pristine()
    bak = MOVE_SRC + ".del_bak"
    shutil.copyfile(MOVE_SRC, bak)
    try:
        try:
            revert(MOVE_SRC)
        except Exception:
            pass
        shutil.copyfile(target, MOVE_SRC)
        try:
            revert(MOVE_SRC)
        except Exception:
            pass
        before = uids(MOVE_SRC, "GObject")
        vi = op(OP_DELETE)
        vi.SetControlValue("Add Label", label)
        _run(vi)
        after = uids(MOVE_SRC, "GObject")
        gone = before - after
        if not gone:
            raise RuntimeError(f"delete_by_label({label!r}): nothing was removed")
        if exec_state(MOVE_SRC) == 0:
            # deleting a node dangles its wires; clean them or save() will refuse
            remove_bad_wires(MOVE_SRC)
            if exec_state(MOVE_SRC) == 0 and not allow_broken:
                raise RuntimeError(
                    f"delete_by_label({label!r}): target still BROKEN after removing bad wires")
        save(MOVE_SRC, allow_broken=allow_broken)
        shutil.copyfile(MOVE_SRC, target)
        return gone
    finally:
        shutil.copyfile(bak, MOVE_SRC)
        os.remove(bak)
        try:
            revert(MOVE_SRC)
        except Exception:
            pass


def exit_loop(target, node_index, output_names, diagram_index, node_class="SubVI"):
    """Create AUTO-INDEXED output tunnels for `output_names` of a node inside a loop.

    Drives OpExitLoop_v0 (erdosmiller `Exit For Loop.vi`). Verified 2026-08-29: three
    tunnels + three wires in 0.26 s, and the tunnels draw with the hollow-bracket
    glyph - auto-indexing, which is what keeps `P` parallelism legal. `Loop Terminal
    Types` therefore does NOT need wiring; the default is already what we want.

    `output_names` must be terminals on the node's CONNECTOR PANE. A name that is only
    a front-panel label raises 5001 inside the Op, where the Clear Errors sinks eat it
    and the whole call becomes a silent no-op - which is why this checks the tunnel
    count and raises instead of trusting a clean return.
    """
    ensure_loaded(target)   # edits are silently declined on a target that is not fully loaded
    before = count(target, "LoopTunnel")
    vi = op(OP_EXITLOOP)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", node_class)
    vi.SetControlValue("index", node_index)
    vi.SetControlValue("Names", list(output_names))
    vi.SetControlValue("Class Name 2", "Diagram")
    vi.SetControlValue("index 2", diagram_index)
    vi.SetControlValue("Names 2", [])
    dt = _run(vi)
    err = _err(vi)   # readable since 2026-08-29: error out indicator branched onto the chain
    if err:
        raise RuntimeError(f"exit_loop: {err}")
    after = count(target, "LoopTunnel")
    if after != before + len(output_names):
        raise RuntimeError(
            "exit_loop: expected %d new tunnels, got %d - a name is probably not on the "
            "connector pane" % (len(output_names), after - before))
    return dt


def wire_indicators(target, node_index, src_terms, indicator_names,
                    diagram_index=0, node_class="SubVI"):
    """Branch a node's output terminals onto EXISTING front-panel indicators by label.

    Drives OpWireInd_v0 (erdosmiller `Wire Indicators.vi`). Contract proven 2026-08-29
    on a scratch copy of OpExitLoop_v0:

    - The indicators must ALREADY EXIST on the target's front panel; they are selected
      by label (`indicator_names`). Nothing is created.
    - Each source terminal MUST ALREADY BE WIRED: WI branches the indicator onto the
      wire attached to the source terminal. An UNWIRED source makes it extend an
      unrelated wire instead -> "This wire connects more than one data source" and the
      target breaks. Wiring a node's already-sunk `error out` therefore gives the
      indicator the error value while the Clear Errors sink stays attached - the
      error-visibility topology the fleet wants, with no dialog risk.
    - NO new Wire object is created (a branch joins an existing wire), so a wire-count
      check cannot verify success. This checks ExecState instead: a break raises; a
      swallowed 5001 (bad name) is still a silent no-op, same as exit_loop - when in
      doubt, probe the name with the sink-less OpWire_v0 trick (see the skill).
    - An Op CANNOT edit itself while running (silent no-op, ExecState stays 1) -
      to edit OpWireInd_v0.vi itself, file-copy the op and run the copy against it.
    """
    if os.path.normcase(target) == os.path.normcase(OP_WIREIND):
        raise RuntimeError("wire_indicators: an op cannot edit itself while running - "
                           "file-copy the op and drive the copy instead")
    ensure_loaded(target)   # edits are silently declined on a target that is not fully loaded
    vi = op(OP_WIREIND)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", node_class)
    vi.SetControlValue("index", node_index)
    vi.SetControlValue("Names", list(src_terms))
    vi.SetControlValue("Class Name 2", "Diagram")
    vi.SetControlValue("index 2", diagram_index)
    vi.SetControlValue("Names 2", list(indicator_names))
    dt = _run(vi)
    err = _err(vi)
    if err:
        raise RuntimeError(f"wire_indicators: {err}")
    if exec_state(target) != 1:
        raise RuntimeError(
            "wire_indicators: target BROKEN after wiring - a source terminal was "
            "probably unwired (WI then extends an unrelated wire; revert the target)")
    return dt


OP_LOOPKERNEL = os.path.join(CLAUDEDEV, "OpLoopKernel_v0.vi")


def loop_kernel(target, location, control_names, kernel_path, input_names, parallel=4):
    """ONE call: parallel For Loop + kernel subVI inside + named tunnel wiring.

    Drives OpLoopKernel_v0 (Create For Loop -> Create SubVI fused in one G dataflow).
    Mechanism proven 2026-08-29 (SCRATCH_h, ExecState 1 afterwards): Create SubVI wires
    each of `control_names`' FRONT-PANEL CONTROL terminals (found by Get Controls)
    straight to the same-index `input_names` terminal on the kernel dropped INSIDE the
    loop - the border crossing makes LabVIEW auto-create the tunnel, auto-indexed for
    array sources and plain for scalars (LabVIEW's wiring defaults).

    Learned limits:
    - The op's `Inputs Indexing?` control is DEAD in this design (tunnels are created by
      the border-crossing wire, not by Create For Loop's Inputs path, whose `Inputs`
      output arrives empty - root cause of the original zero-wire runs, never fixed,
      bypassed instead). Index modes follow LabVIEW defaults; a flat 1D array that must
      NOT be indexed per-element (e.g. x,y,z) needs separate handling.
    - Pairing is by array order: control_names[i] -> input_names[i].
    - A wrong OUTPUT name raises readable 5001; a wrong INPUT name pairs nothing.
    """
    before_loops = count(target, "ForLoop")
    before_subs = uids(target, "SubVI")
    before_wires = count(target, "Wire")
    vi = op(OP_LOOPKERNEL)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("location (0, 0)", list(location))
    vi.SetControlValue("Control Names", list(control_names))
    vi.SetControlValue("Inputs Indexing?", [])
    vi.SetControlValue("Number of Static Parallel Instances", parallel)
    vi.SetControlValue("vi path 2", kernel_path)
    vi.SetControlValue("Input Names", list(input_names))
    vi.SetControlValue("Output Names", [])
    dt = _run(vi)
    err = _err(vi)
    if err:
        raise RuntimeError(f"loop_kernel: {err}")
    if count(target, "ForLoop") != before_loops + 1:
        raise RuntimeError("loop_kernel: no new ForLoop")
    new_subs = new_since(target, "SubVI", before_subs)
    if len(new_subs) != 1 or new_subs[0]["owner"] != "Diagram":
        raise RuntimeError(f"loop_kernel: kernel not placed inside a structure: {new_subs}")
    dw = count(target, "Wire") - before_wires
    if dw != len(input_names):
        raise RuntimeError(
            "loop_kernel: expected %d new wires, got %d - an input name probably "
            "paired with nothing" % (len(input_names), dw))
    return new_subs[0]


OP_SETINDEXMODE = os.path.join(CLAUDEDEV, "OpSetIndexMode_v0.vi")


def set_index_mode(target, tunnel_index, mode):
    """Write a LoopTunnel's IndexMode in `target` (0 = regular/non-indexed, 1 = auto-indexed).

    Drives OpSetIndexMode_v0 (built 2026-08-31: Traverse('LoopTunnel', index) -> cast ->
    IndexMode WRITE property node <- 'index 2' control). IndexMode is U32; only 0 and 1
    are documented - anything else is rejected here (peer-verified, labviewwiki
    LoopTunnel.IndexMode). Not settable while the target runs. Verify by EFFECT
    (ExecState flip on a type mismatch) - there is no scripted read-back op yet.
    """
    if mode not in (0, 1):
        raise ValueError("IndexMode: only 0 (regular) and 1 (auto-index) are documented")
    ensure_loaded(target)   # edits are silently declined on a target that is not fully loaded
    vi = op(OP_SETINDEXMODE)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("vi path 2", target)
    vi.SetControlValue("Class Name", "LoopTunnel")
    vi.SetControlValue("index", int(tunnel_index))
    vi.SetControlValue("index 2", int(mode))
    _run(vi)
    err = _err(vi)
    if err:
        raise RuntimeError(f"set_index_mode(tunnel {tunnel_index}, mode {mode}): {err}")


OP_TUNNEL_IND = os.path.join(CLAUDEDEV, "OpTunnelInd_v0.vi")


def tunnel_indicator(target, tunnel_index):
    """Create a front-panel INDICATOR wired to LoopTunnel[tunnel_index] of `target`, typed by LabVIEW.

    This is how a scripted VI gets an ARRAY output: wire an auto-indexed output tunnel to an indicator and
    LabVIEW gives the indicator the tunnel's datatype - an array - so no front-panel object ever has to be
    built by hand. Drives OpTunnelInd_v0 (built 2026-09-13 from OpSetIndexMode_v0, whose front half
    `Traverse('LoopTunnel', index) -> IndexArray -> To More Specific Class` was already proven).

    WHY create_indicator() CANNOT DO THIS, measured 2026-09-13: it addresses Nodes[]->Terminals[], and a
    sweep of a For Loop's Terminals[0..13] produced DANGLING indicators for 0-7 (front-panel object, but no
    new wire) and nothing beyond. `ForLoop.Terminals[]` are the loop's own infrastructure terminals, and
    **a Tunnel is a GObject, not a Terminal**, so it inherits no Terminal methods. The documented route adds
    one hop, which is the whole content of this op:
        Tunnel.'Outer Term' (6356001) -> Terminal ref -> Terminal.'Create Indicator' (6349C02)

    SET THE INDEX MODE FIRST. The indicator's datatype is whatever the tunnel's outside terminal carries, so
    call `set_index_mode(target, tunnel_index, 1)` before this unless the tunnel is already auto-indexing.
    NI says For Loop output tunnels normally default to indexing when created by wiring - "normally" is not a
    contract, and the array-ness is the entire point.

    Verified by EFFECT, not by return code: a real success adds BOTH a ControlTerminal and a Wire. A new
    ControlTerminal on its own is a dangling indicator, which is the failure mode above.
    """
    before_ctl = uids(target, "ControlTerminal")
    before_wire = count(target, "Wire")
    ensure_loaded(target)   # edits are silently declined on a target that is not fully loaded
    vi = op(OP_TUNNEL_IND)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("vi path 2", target)
    vi.SetControlValue("Class Name", "LoopTunnel")
    vi.SetControlValue("index", int(tunnel_index))
    _run(vi)
    new = new_since(target, "ControlTerminal", before_ctl)
    dw = count(target, "Wire") - before_wire
    if not new:
        raise RuntimeError(f"tunnel_indicator(tunnel {tunnel_index}): no indicator created")
    if dw < 1:
        raise RuntimeError(
            f"tunnel_indicator(tunnel {tunnel_index}): indicator created but NOT WIRED (Wire +{dw}) - "
            "a dangling indicator, same failure mode as create_indicator on a loop terminal")
    return new


OP_WIRECTL = os.path.join(CLAUDEDEV, "OpWireCtl_v0.vi")


def wire_control(target, control_names, dst_cls, dst_i, dst_terms, branch=False,
                 src_diagram_index=0):
    """Wire FRONT-PANEL CONTROLS to a node's named inputs - the one thing OpWire_v1
    could never do, because it only ever sourced from Traverse + Get Outputs.

    `OpWireCtl_v0` swaps that source for `Get Controls.vi`, which turns control LABELS
    into terminal refnums and hands them to `Wire Inputs.vi`'s `Inputs` array. Pass the
    control labels and the destination terminal names positionally:

        wire_control(target, ['x,y,z array'], 'Unbundler', 0, ['array'])

    A destination name that does not exist raises 5001 inside the Op (loud); a control
    label that does not exist raises from Get Controls ("Control %s not found").
    """
    ensure_loaded(target)   # edits are silently declined on a target that is not fully loaded
    before = count(target, "Wire")
    vi = op(OP_WIRECTL)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", "Diagram")     # source side: find the block diagram
    # Get Controls only sees control TERMINALS living on the given diagram - a terminal
    # placed inside a loop/case needs that subdiagram's index (2026-09-01).
    vi.SetControlValue("index", src_diagram_index)
    vi.SetControlValue("Names", list(control_names))
    vi.SetControlValue("Class Name 2", dst_cls)
    vi.SetControlValue("index 2", dst_i)
    vi.SetControlValue("Names 2", list(dst_terms))
    _run(vi)
    err = _err(vi)
    if err:
        raise RuntimeError("wire_control %s -> %s.%s: %s"
                           % (list(control_names), dst_cls, list(dst_terms), err))
    after = count(target, "Wire")
    n = len(control_names)
    # 2026-09-14 (build_setcommand_signed.log run 5): a control wired into a node INSIDE a structure creates a
    # tunnel plus TWO Wire objects (outer + inner segment), so a crossing counts +2 per control - the old "exactly
    # +1" check raised on a successful wire (the sink was wired, ExecState 1). Accept +n .. +2n.
    if not branch and not (before + n <= after <= before + 2 * n):
        # A BRANCH from an already-wired control does NOT add a Wire object - the wire
        # owns all its sinks - so this check misreads a successful branch as a silent
        # decline (it did exactly that twice on 2026-08-31 while the branch succeeded).
        # For branches pass branch=True and verify by effect: ExecState 0->1, or probe.
        raise RuntimeError("wire_control %s -> %s.%s: Wire %d -> %d, expected +%d..+%d "
                           "(if the control is already wired elsewhere this may be a "
                           "successful BRANCH - re-call with branch=True)"
                           % (list(control_names), dst_cls, list(dst_terms),
                              before, after, n, 2 * n))
    return after


def exec_state(target):
    with vi_ref(target) as r:                          # P3: counted + released
        return int(r.ExecState)


def gui_save(target):
    """Save a BROKEN VI by focusing its window and sending Ctrl+S.

    COM `SaveInstrument` blocks forever on a VI whose ExecState is 0, but the editor's
    own File > Save handles one fine (the file shrinks, because a broken VI carries no
    compiled code - benign, the diagram is intact). Needed because copying a fresh
    primitive into a target ALWAYS leaves it briefly broken: the primitive's required
    inputs are not wired yet.

    Sending Ctrl+S to whatever happens to be focused is how an original VI would get
    saved by accident, so this is guarded three ways: the target must be inside
    claudeDev, `focus` must find a window whose title carries the target's own file
    name (it raises if not), and the save is only believed if the file's mtime moves.
    """
    if (os.path.normcase(CLAUDEDEV) not in os.path.normcase(target)
            and os.path.normcase(target) not in SAVE_ALLOWLIST):
        raise RuntimeError(f"refusing to gui_save outside claudeDev: {target}")
    name = os.path.basename(target)
    open_panel(target)
    before = os.path.getmtime(target)
    # A VI usually has BOTH a Front Panel and a Block Diagram window, and `focus` matches
    # the title as a SUBSTRING - so the bare file name is ambiguous. Ctrl+S landed nowhere
    # when it resolved to the Front Panel (2026-08-30); the Block Diagram window takes it.
    # The sleep matters too: SetForegroundWindow needs a moment before keys are accepted.
    # 2026-09-15 00:19 (cycle3b run 2): the Target had ONLY a Front Panel window open, so the BD candidate never
    # focused and Ctrl+S on the FP saved nothing (the 2026-08-30 finding). If no BD window exists, open it from the
    # FP with Ctrl+E (the fleet's existing approved keystroke, bench_prep 'open GUIBENCH BD') and save there.
    # REPAIRED per STATUS NEXT 2026-09-22 (archive/peer/2026-09-22-c71-run3.md Failure-2 §5) after run 4
    # (tools/bench/m3a1_save_before_20260922_002234.png) showed WHY the save failed with no dialog up:
    # after a fresh restart the Getting-Started home window (title exactly "LabVIEW") holds the FOREGROUND,
    # `focus` prints "focused" without verifying foreground, and SendKeys lands wherever the foreground is -
    # so Ctrl+E/Ctrl+S went to the home window and no keystroke ever reached the VI. Two adopted repairs:
    # (a) FAIL LOUDLY with what was OBSERVED per candidate - never invent a "modal dialog" cause;
    # (b) capture the window list at the moment of the save. Mechanism: the H5 blind `click` becomes a
    # `clickprobe`, whose JSON reports the real foreground window after the click - Ctrl+S is sent ONLY
    # when that foreground title contains the candidate's title, so "keystroke dispatched" is measured.
    import json as _json
    import re as _re
    windows_at_entry = " / ".join(l.strip() for l in _lv_gui("-Action", "windows").splitlines() if l.strip())
    attempts = []

    def _fg_click(title):
        """Title-bar clickprobe on `title`: activate by a REAL click, then report the measured
        foreground. Returns (foreground_is_this_window, observed_foreground_title)."""
        m = _re.search(r"left=(-?\d+) top=(-?\d+) right=(-?\d+)",
                       _lv_gui("-Action", "rect", "-Title", '"%s"' % title))
        if not m:
            return False, "(no rect for %r)" % title
        L, T, R = (int(x) for x in m.groups())
        fg = "(no probe ran)"
        for _try in (1, 2):
            pj = _lv_gui("-Action", "clickprobe", "-Title", '"%s"' % title,
                         "-X", str(min(L + 300, R - 120)), "-Y", str(T + 10),
                         "-Exception", "Approved",
                         "-Evidence", "gui_save: title-bar clickprobe, foreground MEASURED before Ctrl+S (save repair 2026-09-22)")
            line = next((l for l in pj.splitlines() if l.lstrip().startswith('{"probe"')), "")
            try:
                pr = _json.loads(line)
            except Exception:
                pr = {}
            fg = ((pr.get("fg_after_click") or {}).get("title")) or "(unreadable probe: %s)" % pj.strip()[:120]
            if title in fg:
                return True, fg
            time.sleep(0.5)
        return False, fg

    # A VI usually has BOTH a Front Panel and a Block Diagram window. Ctrl+S on a Front Panel saves
    # nothing (2026-08-30, 2026-09-15), so if no BD window exists, open it from the FP with Ctrl+E -
    # but ONLY once the FP is the measured foreground, else Ctrl+E lands on the home window too.
    if "focused" not in _lv_gui("-Action", "focus", "-Title", '"%s Block Diagram"' % name):
        fp_title = "%s Front Panel" % name
        if "focused" in _lv_gui("-Action", "focus", "-Title", '"%s"' % fp_title):
            time.sleep(0.8)
            ok, fg = _fg_click(fp_title)
            if ok:
                _lv_gui("-Action", "keys", "-Key", "^e", "-WaitMs", "1500", "-Exception", "Approved",
                        "-Evidence", "gui_save: open the Block Diagram window - Ctrl+S on a Front Panel saves nothing (2026-08-30, 2026-09-15)")
                time.sleep(0.8)
            else:
                attempts.append("Ctrl+E to open the BD was NOT DISPATCHED - foreground stayed %r" % fg)
    for title in ('%s Block Diagram' % name, '%s Front Panel' % name, name):
        out = _lv_gui("-Action", "focus", "-Title", '"%s"' % title)
        if "focused" not in out:
            attempts.append("%r: no such window (focus said %r)" % (title, out.strip()[:120]))
            continue
        time.sleep(0.8)
        # H5 (2026-09-05): after a programmatic activation + Alt-tap focus, LabVIEW's UI loop
        # ignores keys / blocks COM until a real mouse click lands. Click the window's TITLE BAR
        # (never the panel: a panel click can toggle a control) - and MEASURE the foreground.
        ok, fg = _fg_click(title)
        if not ok:
            attempts.append("%r: NO Ctrl+S DISPATCHED - foreground after the activating click was %r" % (title, fg))
            continue
        _lv_gui("-Action", "keys", "-Key", "^s", "-WaitMs", "2500", "-Exception", "Approved", "-Evidence", "gui_save: COM SaveInstrument hangs on broken VIs (skill com-driving.md)")
        # SendKeys '^s' leaves the File MENU ACTIVATED (it renders highlighted). While a
        # menu is active LabVIEW's UI is modal and EVERY subsequent COM call blocks until
        # the 180s watchdog fires - twice mistaken for a wedged LabVIEW on 2026-08-30.
        # Esc dismisses it. Always send it, whether or not the save appeared to work.
        _lv_gui("-Action", "key", "-Key", "esc")
        time.sleep(0.4)
        if os.path.getmtime(target) > before:
            return os.path.getsize(target)
        attempts.append("%r: Ctrl+S DISPATCHED (foreground %r) but the file mtime did not move" % (title, fg))
    raise RuntimeError(
        "gui_save(%s): saved nothing. OBSERVED per candidate: %s. Windows at entry: %s"
        % (name, " | ".join(attempts) or "(no candidate reached)", windows_at_entry))


# Files OUTSIDE claudeDev that the user explicitly authorized for direct modification.
# (2026-09-01: fixture recording went into the working copy itself - user: "카피한 메인 vi
# 자체를 변경하면 좋을 것 같은데". The ORIGINAL Min_Track N beads 4.5_... was always forbidden.)
#
# EMPTIED 2026-09-19, cycle 46 (judgement's decision on the cycle-46 material census): the one entry was
# `...\2. Tracking\Min_Track N beads V6_ParallelLoop.vi` - the file this project now treats as AN ORIGINAL
# (rule 1; every recipe pins its md5 `2a78e17c449cacdaf5da389818526859` and only ever COPIES it). The census
# measured that NO call site anywhere under `tools/**/*.py` passes `save()`/`gui_save()` a path outside
# claudeDev, so the entry granted nothing and cost the one thing rule 1 forbids: our own save function being
# ABLE to overwrite an original. The list stays - it is the mechanism - and it is now EMPTY, so both guards
# (`save()` below and `gui_save()` above) refuse every path outside claudeDev. Do not re-add a path here
# without the user saying so in writing.
SAVE_ALLOWLIST = set()


def save(target, allow_broken=False):
    """Persist the in-memory edits. Guarded to claudeDev + explicit allowlist: an
    original VI must never be saved.

    `allow_broken` diverts a broken VI to gui_save() instead of refusing it.
    """
    if (os.path.normcase(CLAUDEDEV) not in os.path.normcase(target)
            and os.path.normcase(target) not in SAVE_ALLOWLIST):
        raise RuntimeError(f"refusing to save outside claudeDev: {target}")
    if exec_state(target) == 0:
        if allow_broken:
            return gui_save(target)
        raise RuntimeError("refusing to save a BROKEN VI - SaveInstrument blocks forever on one")
    with vi_ref(target) as r:                          # P3: counted + released
        _invoke(r, "SaveInstrument", hard_timeout_s=300.0)
    return os.path.getsize(target)


# --- recipes ----------------------------------------------------------------------------------

def build_kernel(target, loop_at=(4000, 300), parallel=4,
                 tunnel="Array of cal clusters",
                 bead_vi="Track 1 of N bds xyz-kernel-reentrant.vi"):
    """SUPERSEDED by loop_kernel(). Places an UNWIRED loop + kernel; kept for regression.

    Its `tunnel`/`indexing` arguments are INERT: OpForLoop_v0's tunnel creation has never
    worked (Create For Loop's `Inputs` output arrives empty), and the "+1 Tunnel" this
    used to report was the loop's N terminal, which reports as class Tunnel. Use
    loop_kernel() for anything that must actually carry data. This entry point still
    exercises for_loop + loop_diagram + drop_subvi + the containment assert, which is
    why it is kept.
    """
    print("NOTE: build_kernel is superseded by loop_kernel() - it wires NOTHING.")
    print(f"target: {target}")
    print(f"  before: ForLoop={count(target,'ForLoop')} Diagram={count(target,'Diagram')} "
          f"SubVI={count(target,'SubVI')}")

    dt = for_loop(target, loop_at, tunnels=[tunnel], indexing=[True], parallel=parallel)
    print(f"  for_loop P={parallel} at {loop_at}: {dt:.2f}s")

    loop = find_at(target, "ForLoop", loop_at)
    print(f"  loop found: index={loop['i']} uid={loop['uid']} pos={loop['pos']}")

    inner = loop_diagram(target, loop_at)
    print(f"  inner diagram: index={inner['i']} uid={inner['uid']} pos={inner['pos']} "
          f"owner={inner['owner']} (offset-matched, margin-checked)")

    at = (loop_at[0] + 60, loop_at[1] + 60)
    before_subvis = uids(target, "SubVI")
    dt = drop_subvi(target, os.path.join(BG_VIS, bead_vi), inner["i"], at)
    print(f"  drop_subvi {bead_vi} -> diagram[{inner['i']}] at {at}: {dt:.2f}s")

    added = new_since(target, "SubVI", before_subvis)
    if len(added) != 1:
        raise RuntimeError(f"expected exactly 1 new SubVI, got {len(added)}: {added}")
    placed = added[0]
    print(f"  placed subVI: uid={placed['uid']} pos={placed['pos']} owner={placed['owner']}")
    if placed["owner"] != "Diagram":
        raise RuntimeError(
            "placed subVI's owner is %s, not a structure subdiagram" % placed["owner"])
    print("  containment: owner is a structure Diagram (not TopLevelDiagram), and the target "
          "diagram was offset-matched with a verified margin. For an identity-level proof see "
          "STATUS.md (Owner->GObject cast->UID, or AbstractDiagram 'All Objects[]').")
    print(f"  after:  ForLoop={count(target,'ForLoop')} Diagram={count(target,'Diagram')} "
          f"SubVI={count(target,'SubVI')}")
    print(f"  ExecState={exec_state(target)} (0=BROKEN, expected until the body is wired)")
    return placed


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    cmd, target = sys.argv[1], sys.argv[2]
    if cmd == "report":
        for o in report(target, sys.argv[3]):
            print("  [%d] %-18s uid=%-6d pos=%-14s owner=%s"
                  % (o["i"], o["class"], o["uid"], str(o["pos"]), o["owner"]))
    elif cmd == "kernel":
        build_kernel(target)
    elif cmd == "save":
        print("saved,", save(target), "bytes")
    else:
        print(f"unknown command {cmd!r}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())


# --- keystone: typed Invoke nodes (OpBuildInvoke_v0, 2026-09-06) -------------------------------

OP_BUILD_INVOKE = os.path.join(CLAUDEDEV, "OpBuildInvoke_v0.vi")


def build_invoke(target, cls, method_id, location, diagram_index=0):
    """Create an Invoke Node on `target`'s diagram: class `cls` ("VI Server:Terminal", "VI Server:VI",
    ...), method by Unique ID (e.g. "6349C03" = Terminal.Connect Wire, "6349C02" = Create
    Indicator), top-left at `location`. Returns the new Invoke object dicts (uid/pos).

    Facts (docs/keystone-op-spec.md §14): the op's `reference` is deliberately unwired — with a
    reference the erdosmiller creator writes the object's bare class name and fails silently.
    The skeleton's Create SubVI branch (source of an error-7 dialog per run) was deleted on
    2026-09-06 14:2x (GUI, user-approved); the op's `error out` indicator is now unwired, so
    read creator errors from the dialog watchdog, not from _err().
    """
    ensure_loaded(target)   # edits are silently declined on a target that is not fully loaded
    before = uids(target, "Invoke")
    vi = op(OP_BUILD_INVOKE)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", "Diagram")
    vi.SetControlValue("index", diagram_index)
    vi.SetControlValue("vi path 2", "")
    vi.SetControlValue("location (0, 0)", list(location))
    vi.SetControlValue("Class Name 3", cls)
    vi.SetControlValue("Class Name 2", method_id)
    try:
        _run(vi)
    except RuntimeError as e:
        if "modal dialog" not in str(e):        # the known error-7 dialog is dismissed by the watchdog
            raise
    new = new_since(target, "Invoke", before)
    if len(new) != 1:
        raise RuntimeError(f"build_invoke: expected 1 new Invoke, got {len(new)}")
    return new


OP_BUILD_PN = os.path.join(CLAUDEDEV, "OpBuildPN_v1.vi")   # v1 2026-09-14: creator error + Outputs exposed; v0 kept on disk


def build_property(target, cls, props, location, diagram_index=0):
    """Create a Property Node on `target`'s diagram: class `cls` ("VI Server:GObject", ...),
    items `props` = [(property_unique_id, is_write), ...] (IDs from docs/vi-server-ids.json, e.g.
    ("632A800", False) = GObject.Position read), top-left at `location`. Returns the new Property
    object dicts. Same rules as build_invoke: reference unwired, class by string, IDs not names.
    Verified 2026-09-06: ("632A800", False) with "VI Server:GObject" -> 'GObj / Position' node.
    """
    ensure_loaded(target)   # edits are silently declined on a target that is not fully loaded
    before = uids(target, "Property")
    vi = op(OP_BUILD_PN)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", "Diagram")
    vi.SetControlValue("index", diagram_index)
    vi.SetControlValue("location (0, 0)", list(location))
    vi.SetControlValue("Class Name 3", cls)
    vi.SetControlValue("Properties", cluster_array([(pid, bool(w)) for pid, w in props]))
    try:
        _run(vi)
    except RuntimeError as e:
        if "modal dialog" not in str(e):
            raise
    # OpBuildPN_v1 (2026-09-14) exposes the CREATOR's own error (indicator 'error out 2', from the creator's
    # real error-out terminal, index 15 - index 10 with the same name is a sink) and its 'Outputs' array. An
    # unsupported property ID raises error 1077 from Set Properties[] inside the creator; v0 sank that error
    # and returned a rows-less node indistinguishable from success - the mechanism behind every "did not
    # attach" mystery (Control.Value 09-12, Get Errors 09-09/14, SubVIs[]/Control.Terminal this morning, which
    # in fact DO attach). Peer contract: error status is the verdict; the count only corroborates a clean one.
    cerr = _err(vi, "error out 2")
    if cerr:
        raise RuntimeError(f"build_property({cls}, {[p for p, _w in props]}): creator refused - {cerr}")
    try:
        n_out = len(vi.GetControlValue("Outputs"))
    except Exception:
        n_out = None
    # MODE-AWARE POST-CONDITION (cycle 61, 2026-09-21). The creator's `Outputs` array carries the new node's
    # OUTPUT terminals only, so a WRITE-mode item is an INPUT and can never appear in it. Until today this test
    # read `n_out != len(props)` - it counted the wrong side and raised on EVERY is_write=True request while
    # LabVIEW created the node correctly: measured in tools/bench/diag_c61_localdir.log, where 6355401 AND the
    # known-good 6355400 both raised `Outputs count 0 != 1 requested` and both nodes were in fact present with a
    # correct `Write?` / `CtrlName` SINK row. The assertion is NOT weakened: read-mode items are still asserted
    # against Outputs exactly as before, and write-mode items are asserted against the node's own SINK terminals,
    # read back off the machine (a write item that did not attach leaves no extra sink and still raises).
    n_read = sum(1 for _pid, w in props if not bool(w))
    n_write = len(props) - n_read
    if n_out is not None and n_out != n_read:
        raise RuntimeError(f"build_property({cls}): creator error clean but Outputs count {n_out} != "
                           f"{n_read} read-mode item(s) requested - inconsistent, not trusted")
    new = new_since(target, "Property", before)
    if len(new) != 1:
        raise RuntimeError(f"build_property: expected 1 new Property, got {len(new)}")
    if n_write:
        uid = new[0]["uid"]
        standard = ("reference", "reference out", "error in (no error)", "error out")
        cand = []
        try:
            cand = [i for i, r in enumerate(node_labels(target, diagram_index)) if r.get("uid") == uid]
        except Exception:                                    # node_labels is a convenience, not the verdict
            cand = []
        rows = None
        for i in cand + [j for j in range(80) if j not in cand]:
            try:
                nu, tr = node_terms_uid(target, diagram_index, i)
            except Exception:
                continue
            if nu == uid:
                rows = tr
                break
        if rows is None:
            raise RuntimeError(f"build_property({cls}): {n_write} write-mode item(s) requested and the new node "
                               f"#{uid} could not be read back on diagram {diagram_index} - not trusted")
        sinks = [r for r in rows if not r.get("is_source") and r.get("name") not in standard]
        if len(sinks) != n_write:
            raise RuntimeError(f"build_property({cls}): creator error clean but the new node #{uid} carries "
                               f"{len(sinks)} non-standard SINK terminal(s) {[r.get('name') for r in sinks]} != "
                               f"{n_write} write-mode item(s) requested - inconsistent, not trusted")
    return new


OP_DELETE = os.path.join(CLAUDEDEV, "OpDelete_v0.vi")


def delete_object(target, cls, index, verify=True):
    """Delete the `index`-th object of Traverse class `cls` on `target` (Generic.Delete over a
    GObject reference — OpDelete_v0, built with build_invoke on 2026-09-06). Wires attached to the
    object are left broken: call remove_bad_wires() afterwards if the VI must run. Returns the uid
    set that disappeared (None when verify=False). Replaces delete_by_label (substitution protocol,
    unusable since the editor's Save became a no-op for scripted edits).

    verify=False skips the before/after uid snapshots (2 extra op runs per call): for bulk deletes take
    ONE snapshot around the whole batch instead - see net_map's purge.

    ⚠️ verify=False MEANS THIS CALL CANNOT TELL YOU WHETHER IT DELETED ANYTHING. On 2026-09-16 a build printed
    six "deleted #..." lines with verify=False and removed nothing at all; the same delete with verify=True
    raises `expected 1 object gone, got 0` immediately (tools/bench/diag_save_persists.log). Use verify=False
    only with a snapshot around the batch, and never as a way to make a failing delete quiet.
    """
    # THE ACTUAL BUG, found 2026-09-16 and measured in tools/bench/diag_delete_matrix.log: this wrapper never
    # forced the target's diagram into memory, so LabVIEW SILENTLY DECLINED every delete - count unchanged, no
    # error, no dialog. The op was never broken. See ensure_loaded() for the A/B and the two independent sources.
    ensure_loaded(target)
    before = uids(target, cls) if verify else None
    vi = op(OP_DELETE)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", cls)
    vi.SetControlValue("index", index)
    # DO NOT SWALLOW THE MODAL-DIALOG EXCEPTION (changed 2026-09-16). This used to read
    #     except RuntimeError as e:
    #         if "modal dialog" not in str(e): raise
    # i.e. it caught exactly the one signal LabVIEW gives when a delete is refused, and continued as if the call
    # had worked. Measured in tools/bench/diag_delete_error_control.log: two deletes that CANNOT succeed (an
    # out-of-range index; an unknown class name) both raised "run blocked behind a modal dialog (dismissed by
    # watchdog)" while `error out` stayed (False, 0, '') - the op's error indicator never moves for ANY input, so
    # the dialog is the only evidence there is, and this wrapper was discarding it. With verify=False on top, a
    # refused delete became a reported success.
    _run(vi)
    # READ THE OP'S OWN ERROR OUTPUT (added 2026-09-16). Until today this wrapper was the odd one out: it ran the
    # op and inspected nothing, while every neighbour here calls `_err`. A peer review made the consequence
    # explicit (archive/peer/2026-09-16-delete-object-noop-failed-prediction.md): `Generic.Delete` is an Invoke
    # Node with its OWN error cluster, so a returning Run says only that the op VI did not crash - if the method
    # errored, or was skipped because an upstream error reached its `error in`, nothing here would ever notice.
    # That is how the A1 build printed six "deleted #..." lines while the saved VI kept every one of those nodes
    # (tools/bench/build_opownerchain_v0.log vs diag_ownerchain_state.log).
    # MEASURED AFTERWARDS (diag_delete_error_control.log): this indicator is in fact DEAD - it reads
    # (False, 0, '') even for inputs that cannot possibly succeed - so OpDelete_v0 still needs rebuilding with the
    # Invoke Node's error actually wired out. The read is kept anyway: it costs one call, it is what every other
    # wrapper here does, and it starts reporting the moment the op is rebuilt.
    err = _err(vi)
    if err:
        raise RuntimeError(f"delete_object({cls}[{index}]): the op reported {err}")
    if not verify:
        return None
    gone = before - uids(target, cls)
    if len(gone) != 1:
        raise RuntimeError(f"delete_object({cls}[{index}]): expected 1 object gone, got {len(gone)}")
    return gone


OP_MOVE = os.path.join(CLAUDEDEV, "OpMove_v0.vi")


def move_object(target, cls, index, position):
    """Move the `index`-th object of class `cls` (Traverse order, same as report()) on `target` to the
    absolute diagram `position` (GObject.Move, Unique ID 632A400 — OpMove_v0, built entirely by script
    on 2026-09-06 from OpDelete_v0: build_invoke + wire + wire_control; verified IndexArray -> (1200,900)
    in 0.04 s). `owner` is left unwired (same diagram). Returns the object's reported position after.
    Replaces move_by_label (substitution protocol)."""
    ensure_loaded(target)   # edits are silently declined on a target that is not fully loaded
    vi = op(OP_MOVE)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", cls)
    vi.SetControlValue("index", index)
    vi.SetControlValue("location (0, 0)", list(position))
    try:
        _run(vi)
    except RuntimeError as e:
        if "modal dialog" not in str(e):
            raise
    return report(target, cls)[index]["pos"]


OP_BUILD_IA = os.path.join(CLAUDEDEV, "OpBuildIA_v0.vi")


def build_index_array(target, location, source_terminal_index=0):
    """Place an Index Array primitive on `target`'s top-level block diagram at `location` (erdosmiller
    `Create Index Array.vi`; OpBuildIA_v0 built by script on 2026-09-06 — Diagram from a VI-class
    Property Node `Block Diagram` (ID 23C, output terminal name = short name 'Diagram'), creator error
    out sunk into Clear Errors). The library's `array` input (Traverse class "Terminal", index
    `source_terminal_index`) raised error 1304 ("Index Count") for every terminal tried, so the node
    arrives UNWIRED; wire its `array` input afterwards with connect_terminals(). Returns the new
    IndexArray object dicts."""
    ensure_loaded(target)   # edits are silently declined on a target that is not fully loaded
    before = uids(target, "IndexArray")
    vi = op(OP_BUILD_IA)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", "Terminal")
    vi.SetControlValue("index", source_terminal_index)
    vi.SetControlValue("location (0, 0)", list(location))
    try:
        _run(vi)
    except RuntimeError as e:
        if "modal dialog" not in str(e):
            raise
    new = new_since(target, "IndexArray", before)
    if len(new) != 1:
        raise RuntimeError(f"build_index_array: expected 1 new IndexArray, got {len(new)}")
    return new


OP_CREATE_CONTROL = os.path.join(CLAUDEDEV, "OpCreateControl_v1.vi")
OP_CREATE_INDICATOR = os.path.join(CLAUDEDEV, "OpCreateIndicator_v0.vi")


def node_rank(target, uid):
    """WRONG in general — kept as a warning. Nodes[] is CREATION order; uid rank matched it on GUIBENCH_v0 only
    because that VI's nodes were created in uid order. Newly created nodes reuse low uids (90, 98 seen
    2026-09-06 20:0x) and go to the END of Nodes[]. Until a Nodes[]-order reporter exists, pass explicit
    indices (nodes you just created are the last entries: count(Node)-k)."""
    return sorted(o["uid"] for o in report(target, "Node")).index(uid)


def create_control(target, node_index, terminal_index):
    """Create a front-panel control wired to terminal `terminal_index` (Node.Terminals[] order = the Context
    Help terminal index) of Nodes[node_index] (CREATION order) on `target` (Terminal.Create Control, 6349C01 —
    OpCreateControl_v0, built by script 2026-09-06 on the ladder VI→Block Diagram→Nodes[]→IA→Terminals[]→IA).
    ~0.15 s; a wired terminal or an out-of-range index yields no control (dialog for out-of-range Nodes[]).
    Returns (new ControlTerminal dicts, label) — v1 (2026-09-06 20:3x) reports the label LabVIEW assigned
    (terminal name, " 2"/" 3" suffix on duplicates) through Control.Label → Text.Text. Replaces copy_into."""
    ensure_loaded(target)   # edits are silently declined on a target that is not fully loaded
    before = uids(target, "ControlTerminal")
    vi = op(OP_CREATE_CONTROL)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Names", []); vi.SetControlValue("Names 2", [])
    vi.SetControlValue("Class Name", ""); vi.SetControlValue("Class Name 2", "")
    vi.SetControlValue("index", node_index)
    vi.SetControlValue("index 2", terminal_index)
    # DO NOT SWALLOW THE MODAL-DIALOG EXCEPTION (changed 2026-09-20, cycle 56, mirroring delete_object:2264-2272).
    # This used to read `except RuntimeError as e: if "modal dialog" not in str(e): raise`, i.e. it caught exactly
    # the one signal LabVIEW gives when the call is refused, and returned an EMPTY list instead. Measured
    # (tools/bench/diag_s3a_ind_transport.log, 20 consecutive calls): the dialogs said "Error 1055 occurred at
    # Property Node in OpCreate{Control,Indicator}_v0.vi - Object reference is invalid", and the caller saw
    # `exception None` + no new ControlTerminal, so a REFUSAL read as a silent decline. The op has no error
    # indicator to read (same as OpDelete_v0), so the dialog text is the only evidence there is.
    _run(vi)
    new = new_since(target, "ControlTerminal", before)
    label = vi.GetControlValue("Text") if new else None      # v1 reports the label LabVIEW gave the control
    return new, label


def create_indicator(target, node_index, terminal_index):
    """Indicator wired to terminal `terminal_index` of Nodes[node_index] (Terminal.Create Indicator 6349C02 —
    OpCreateIndicator_v0, same ladder, built 2026-09-06). Returns the new ControlTerminal dicts."""
    ensure_loaded(target)   # edits are silently declined on a target that is not fully loaded
    before = uids(target, "ControlTerminal")
    vi = op(OP_CREATE_INDICATOR)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Names", []); vi.SetControlValue("Names 2", [])
    vi.SetControlValue("Class Name", ""); vi.SetControlValue("Class Name 2", "")
    vi.SetControlValue("index", node_index)
    vi.SetControlValue("index 2", terminal_index)
    # DO NOT SWALLOW THE MODAL-DIALOG EXCEPTION - see create_control just above (changed 2026-09-20, cycle 56;
    # the same repair delete_object:2264-2272 already carries). The dialog carried "Error 1055 ... Object
    # reference is invalid" on all 20 calls of tools/bench/diag_s3a_ind_transport.log and this wrapper discarded
    # it, reporting an empty ControlTerminal list with `exception None`.
    _run(vi)
    return new_since(target, "ControlTerminal", before)


OP_CONNECT = os.path.join(CLAUDEDEV, "OpConnect_v0.vi")


def connect_terminals(target, sink_node, sink_term, src_node, src_term):
    """Wire Nodes[src_node].Terminals[src_term] (source) into Nodes[sink_node].Terminals[sink_term] (sink) on
    `target` (Terminal.Connect Wire 6349C03 — OpConnect_v0, two script-built ladders, 2026-09-06; Nodes[] is
    CREATION order, Terminals[] the Context-Help index). ~0.04 s. Semantics verified on a fresh Index Array:
    an already-wired source is BRANCHED (wire count unchanged, ExecState 0→1); an already-wired SINK is not
    safe (LabVIEW re-routes and the VI breaks) — wire only unwired sinks. Type mismatches make a broken wire.
    Returns (wire count delta, exec_state after).
    KNOWN STALL (2026-09-08, twice: 08:43 t32 array-of-clusters, 09:06 t28 DBL array): a connect into a Call Library
    Function Node with Adapt-to-Type parameters returns normally, then LabVIEW spins one core (100 %, ~14 min the
    first time) and every following VI Server call blocks. The name-based erdosmiller route (`wire(..., "CallLibrary",
    0, "<param name>")`) wired the same node instantly at build time — use that for CLFN terminals."""
    ensure_loaded(target)   # edits are silently declined on a target that is not fully loaded
    w0 = count(target, "Wire")
    vi = op(OP_CONNECT)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Names", []); vi.SetControlValue("Names 2", [])
    vi.SetControlValue("Class Name", ""); vi.SetControlValue("Class Name 2", "")
    vi.SetControlValue("index", sink_node); vi.SetControlValue("index 2", sink_term)
    vi.SetControlValue("index 3", src_node); vi.SetControlValue("index 4", src_term)
    try:
        _run(vi)
    except RuntimeError as e:
        if "modal dialog" not in str(e):
            raise
    return count(target, "Wire") - w0, exec_state(target)


OP_FP_LABELS = os.path.join(CLAUDEDEV, "OpFPLabels_v0.vi")


def fp_labels(target, max_n=200):
    """[(index, label, is_indicator)] for every front-panel object of `target` in tabbing order
    (OpFPLabels_v0: VI -> Front Panel 23D -> Panel.Controls[] 6348801 -> Control.Label/Indicator -> Text.Text;
    built by script 2026-09-07). Stops at the first out-of-range index (one 8 s dialog)."""
    vi = op(OP_FP_LABELS)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Names", []); vi.SetControlValue("Names 2", [])
    vi.SetControlValue("Class Name", ""); vi.SetControlValue("Class Name 2", ""); vi.SetControlValue("index 2", 0)
    out = []
    for i in range(max_n):
        vi.SetControlValue("index", i)
        try:
            _run(vi)
        except RuntimeError:
            break
        out.append((i, vi.GetControlValue("Text"), bool(vi.GetControlValue("Indicator"))))
    return out


OP_NODE_INFO = os.path.join(CLAUDEDEV, "OpNodeInfo_v0.vi")


def node_info(target, max_n=400):
    """[(Nodes[] index, style name, label text)] for the top-level block-diagram nodes of `target` in
    Nodes[] (creation) order — OpNodeInfo_v0 (VI -> Block Diagram -> Nodes[] -> Node.Label 6359001 /
    Node.Style 6359009 -> Text.Text; built 2026-09-07). Style is the node TYPE name ('Index Array', 'File
    Dialog', 'For Loop', 'Read from Binary File'...), so primitives are finally nameable without GUI.
    Stops at the first out-of-range index (one 8 s dialog). Sub-diagram nodes are not listed."""
    vi = op(OP_NODE_INFO)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Names", []); vi.SetControlValue("Names 2", [])
    vi.SetControlValue("Class Name", ""); vi.SetControlValue("Class Name 2", ""); vi.SetControlValue("index 2", 0)
    out = []
    for i in range(max_n):
        vi.SetControlValue("index", i)
        try:
            _run(vi)
        except RuntimeError:
            break
        out.append((i, vi.GetControlValue("Style"), vi.GetControlValue("Text")))
    return out


OP_REMOVE_BAD_WIRES = os.path.join(CLAUDEDEV, "OpRemoveBadWires_v0.vi")


def remove_bad_wires_scripted(target):
    """LabVIEW's Ctrl+B by script: VI.'Block Diagram:Remove Bad Wires' (410) on `target` (OpRemoveBadWires_v0,
    2026-09-07). Returns (wire count after, exec_state). Use after deleting nodes instead of positional wire hunts."""
    ensure_loaded(target)   # edits are silently declined on a target that is not fully loaded
    vi = op(OP_REMOVE_BAD_WIRES)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Names", []); vi.SetControlValue("Names 2", [])
    vi.SetControlValue("Class Name", ""); vi.SetControlValue("Class Name 2", "")
    try:
        _run(vi)
    except RuntimeError as e:
        if "modal dialog" not in str(e):
            raise
    return count(target, "Wire"), exec_state(target)


OP_NET_INFO = os.path.join(CLAUDEDEV, "OpNetInfo_v1.vi")


def net_map(target, diagram_index=0, max_nodes=200, max_terms=40):
    """Connectivity of one diagram of `target` (Traverse "Diagram" index; 0 = top level), read headlessly with
    OpNetInfo_v0 (built 2026-09-07). Returns (nodes, nets): nodes = {n: (node_uid, "", [(t, term_name, wire_uid), ...])}
    (node_uid matches report()'s uid, so class/position come from the Traverse reporter),
    nets = {wire_uid: [(n, t, term_name), ...]} — every terminal touching the same wire UID is one net. A node's
    terminal list ends at the first out-of-range terminal (one 8 s dialog per node); wire_uid 0 = unwired."""
    vi = op(OP_NET_INFO)
    vi.SetControlValue("vi path", target); vi.SetControlValue("Class Name", "Diagram"); vi.SetControlValue("index", diagram_index)
    vi.SetControlValue("error in (no error)", (False, 0, "")); vi.SetControlValue("error in", (True, 1, "neutralised creator"))
    vi.SetControlValue("Class Name 3", ""); vi.SetControlValue("Class Name 2", "")   # creator: empty class/ID -> creates nothing
    nodes, nets = {}, {}
    # 2026-09-14, MEASURED (tools/bench/probe_builder_artifact.log): ONE net_map call added 75 untyped Invoke
    # nodes to the target (+450 terminals) and left it ExecState 0; deleting those Invokes + Remove Bad Wires
    # restored ExecState 1 with an object census identical to pristine. That is docs/keystone-op-spec.md s33 -
    # OpNetInfo's neutralised erdosmiller creator drops a junk Invoke per run - and it explains, in one stroke:
    # (a) why fresh nodes were "invisible": they sat in Nodes[] behind the walker's OWN junk, on which the
    # 'junk Invoke' end-of-nodes heuristic below stopped the walk; (b) why every ladder probe and three
    # OpReportNodes builds ended broken - they had called net_map on the target. build_property itself is
    # clean (v0 and v1 both leave exactly one Property node). So net_map now applies the s33 protocol itself:
    # snapshot Invoke uids first, purge what the walk added, Remove Bad Wires, and never trust a walk that
    # was not purged. The earlier "stale reference" reading recorded in STATUS was wrong.
    _junk_before = set(uids(target, "Invoke"))
    _t_walk = time.time()
    MISS_LIMIT = 4
    misses = 0
    for n in range(max_nodes):
        vi.SetControlValue("index 2", n); vi.SetControlValue("index 3", 0)
        try:
            _run(vi)
        except RuntimeError:
            misses += 1
            if misses >= MISS_LIMIT:
                break
            continue
        style, label = int(vi.GetControlValue("UID")), ""      # OpNetInfo reports the node's GObject.UID (no Style/Label: crash, spec §30)
        if style == 0:                                          # out-of-range node with auto error handling off
            misses += 1
            if misses >= MISS_LIMIT:
                break
            continue
        misses = 0
        # Progress line per node (2026-09-14, stall record stall_pid6164_121247.log): on the main VI a 21-node
        # walk was silent for 167 s and the stall detector - which now trusts the job log's freshness - flagged a
        # healthy client. A line per node is a REAL progress signal: it prints only after that node's COM calls
        # returned, so a hang shows as the line that never comes.
        print(f"net_map: node {n} uid {style} ({time.time() - _t_walk:.0f} s)", flush=True)
        terms = []; empties = 0
        for t in range(max_terms):
            vi.SetControlValue("index 3", t)
            if t:
                try:
                    _run(vi)
                except RuntimeError:
                    break
            name, uid = vi.GetControlValue("Name"), int(vi.GetControlValue("UID 2"))
            if name == "" and uid == 0:                         # out-of-range terminal - OR an unassigned connector-pane slot
                empties += 1                                    # of a subVI (2026-09-07: those truncated the list), so stop only
                if empties >= 3:                                # after 3 empties in a row; the empties are dropped below
                    break
                terms.append((t, name, uid)); continue
            empties = 0
            terms.append((t, name, uid))
            if t == 5 and [x[1] for x in terms[:6]] == ["reference", "reference out", "error in (no error)", "error out", "Method", "Method"]:
                terms = None; break                             # the op's own junk Invoke (spec §33): end of the real nodes
        if terms is None:
            break
        while terms and terms[-1][1] == "" and terms[-1][2] == 0:
            terms.pop()
        for t, name, uid in terms:                              # (bug fixed 2026-09-07: this block was dead code after `break`)
            if uid:
                nets.setdefault(uid, []).append((n, t, name))
        nodes[n] = (style, label, terms)
    # s33 protocol, now built in (2026-09-14): every per-node/per-terminal op run above dropped an untyped
    # Invoke on the target. Delete exactly those (highest report index first so indices stay valid), then
    # Remove Bad Wires. Measured: 75 junk Invokes from one walk of an 8-node diagram; purge restores ExecState 1.
    # Cost model (peer-attacked 2026-09-14, archive/peer/2026-09-14-stall-alert-wrappers-false-positive.md s4): the
    # first version used report() per object and delete_object's per-call before/after snapshots - O(J^2) op runs
    # for J junk nodes, which is what timed out probe_attach_reader2c at 12 min. Now: ONE report_all snapshot for
    # the order, J unverified deletes, ONE snapshot after. Phase times are printed so the next slow walk is
    # diagnosable from its log instead of guessed at.
    _t_purge = time.time()
    order = [o["uid"] for o in report_all(target, "Invoke")]
    junk = [u for u in order if u not in _junk_before]
    if junk:
        for k, idx in enumerate(sorted((order.index(u) for u in junk), reverse=True)):
            try:
                delete_object(target, "Invoke", idx, verify=False)
            except Exception:
                pass
            if k % 20 == 19:
                print(f"net_map: purged {k + 1}/{len(junk)} junk Invokes ({time.time() - _t_purge:.0f} s)", flush=True)
        try:
            remove_bad_wires_scripted(target)
        except Exception:
            pass
        left = [u for u in uids(target, "Invoke") if u not in _junk_before]
        if left:
            print(f"net_map: WARNING {len(left)} junk Invoke(s) could not be purged from {os.path.basename(target)}",
                  flush=True)
    print(f"net_map: {len(nodes)} nodes walked in {_t_purge - _t_walk:.1f} s; {len(junk)} junk Invoke(s) purged in "
          f"{time.time() - _t_purge:.1f} s", flush=True)
    return nodes, nets


def print_net_map(nodes, nets):
    for n, (style, label, terms) in nodes.items():
        print(f"[{n}] {style} | {label}")
        for t, name, uid in terms:
            others = [f"{m}.{tt} {nm!r}" for m, tt, nm in nets.get(uid, []) if (m, tt) != (n, t)] if uid else []
            print(f"     t{t} {name!r} -> " + (" ; ".join(others) if others else ("(wire %d, no other terminal in this diagram)" % uid if uid else "UNWIRED")))


OP_SET_AUTO_ERR = os.path.join(CLAUDEDEV, "OpSetAutoErr_v0.vi")


def set_auto_error_handling(target, enabled):
    """Write VI.'Automatic Error Handling' (242) of `target` — OpSetAutoErr_v0 (2026-09-07). FALSE silences the
    auto error dialog for every unwired error out in that VI (errors then just drop) — use on OPS whose creators
    or property nodes error by design, never on a VI whose errors you still need to see."""
    ensure_loaded(target)   # edits are silently declined on a target that is not fully loaded
    vi = op(OP_SET_AUTO_ERR)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Names", []); vi.SetControlValue("Names 2", [])
    vi.SetControlValue("Class Name", ""); vi.SetControlValue("Class Name 2", "")
    vi.SetControlValue("Automatic Error Handling", bool(enabled))
    _run(vi)


OP_CONNECT2 = os.path.join(CLAUDEDEV, "OpConnect2_v0.vi")


def connect2(target, diagram_index, sink_node, sink_term, src_node, src_term):
    """Wire top-level Nodes[src_node].Terminals[src_term] into Nodes[sink_node].Terminals[sink_term] of ANY diagram
    (Traverse "Diagram" index; a loop's inner diagram included) — OpConnect2_v0 (2026-09-07). LabVIEW creates the
    structure tunnel itself (non-indexed; flip with set_index_mode). Returns (wire delta, exec_state)."""
    ensure_loaded(target)   # edits are silently declined on a target that is not fully loaded
    w0 = count(target, "Wire")
    vi = op(OP_CONNECT2)
    vi.SetControlValue("vi path", target); vi.SetControlValue("Class Name", "Diagram"); vi.SetControlValue("index", diagram_index)
    vi.SetControlValue("error in (no error)", (False, 0, "")); vi.SetControlValue("error in", (True, 1, "neutralised creator"))
    vi.SetControlValue("Class Name 3", ""); vi.SetControlValue("Class Name 2", "")   # creator: empty class/ID -> creates nothing
    vi.SetControlValue("index 2", sink_node); vi.SetControlValue("index 3", sink_term)
    vi.SetControlValue("index 4", src_node); vi.SetControlValue("index 5", src_term)
    try:
        _run(vi)
    except RuntimeError as e:
        if "modal dialog" not in str(e):
            raise
    return count(target, "Wire") - w0, exec_state(target)


OP_SET_LABEL = os.path.join(CLAUDEDEV, "OpSetLabel_v0.vi")


def set_node_label(target, diagram_index, node_index, text):
    """Write the label of Nodes[node_index] of Traverse "Diagram"[diagram_index] on `target` (OpSetLabel_v0, built by
    script 2026-09-08 on the OpNetInfo_v1 ladder: Node.Label 6359001 -> Text.Text 632D800 write). Leaves the op's junk
    Invoke on the target like OpNetInfo (spec §33)."""
    ensure_loaded(target)   # edits are silently declined on a target that is not fully loaded
    vi = op(OP_SET_LABEL)
    vi.SetControlValue("vi path", target); vi.SetControlValue("Class Name", "Diagram"); vi.SetControlValue("index", diagram_index)
    vi.SetControlValue("index 2", node_index); vi.SetControlValue("index 3", 0)
    vi.SetControlValue("error in (no error)", (False, 0, "")); vi.SetControlValue("error in", (True, 1, "neutralised creator"))
    vi.SetControlValue("Class Name 3", ""); vi.SetControlValue("Class Name 2", "")
    vi.SetControlValue("Text", text)
    _run(vi)
    return vi.GetControlValue("UID")


OP_MOVE_OUT = os.path.join(CLAUDEDEV, "OpMoveOut_v0.vi")


def move_out(target, diagram_index, node_index, position):
    """Move Nodes[node_index] of Traverse "Diagram"[diagram_index] to the TOP-LEVEL diagram of `target` at `position`
    (OpMoveOut_v0: GObject.Move with owner = VI.Block Diagram; built by script 2026-09-08). Wires to the node break
    (call remove_bad_wires_scripted). Leaves the op's junk Invoke on the target (spec §33)."""
    ensure_loaded(target)   # edits are silently declined on a target that is not fully loaded
    vi = op(OP_MOVE_OUT)
    vi.SetControlValue("vi path", target); vi.SetControlValue("Class Name", "Diagram"); vi.SetControlValue("index", diagram_index)
    vi.SetControlValue("index 2", node_index); vi.SetControlValue("index 3", 0)
    vi.SetControlValue("error in (no error)", (False, 0, "")); vi.SetControlValue("error in", (True, 1, "neutralised creator"))
    vi.SetControlValue("Class Name 3", ""); vi.SetControlValue("Class Name 2", "")
    vi.SetControlValue("position", tuple(int(v) for v in position))
    _run(vi)
    return int(vi.GetControlValue("UID"))


# ---- Call Library Function Node, configured entirely by script (2026-09-09; docs/gpu-backend.md "scripted CLFN configuration") ----
OP_CLFN_PARAMS = os.path.join(CLAUDEDEV, "OpCLFNParams_v0.vi")
OP_CLFN_PRE = os.path.join(CLAUDEDEV, "OpCLFNPre_v0.vi")
OP_CLFN_BUILD = os.path.join(CLAUDEDEV, "OpCLFNBuild_v0.vi")
_BENCH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bench")


def build_clfn(target, location, dll, fn, flat_hex, calling_convention=0, reentrant=True):
    """Place a CLFN on `target` calling `fn` of `dll` with the parameter list `flat_hex` (flattened Parameter Info array,
    tools/gpu/clfn_params.py --compose).  Three ops in ONE LabVIEW session: OpCLFNParams_v0 fills the import wizard's Parameter
    Info global (an EMPTY one makes NI Create.vi kill LabVIEW), OpCLFNPre_v0 fills Function Name / Path / Calling Convention /
    Reentrant, OpCLFNBuild_v0 runs NI Create.vi + the attribute sets + Parameter Info Set + Parameter Terminals.
    Returns (new CallLibrary uid, number of parameter terminals, error tuple)."""
    import json
    labs = json.load(open(os.path.join(_BENCH, "opclfnparams_labels.json")))
    pv = op(OP_CLFN_PARAMS); pv.SetControlValue(labs["binary string"], bytes.fromhex(flat_hex).decode("latin-1")); pv.SetControlValue(labs["operation"], 1); _run(pv)
    err = pv.GetControlValue(labs["error out"])
    if err and err[0]:
        raise RuntimeError(f"build_clfn: Parameter Info global not set: {err}")
    table = json.load(open(os.path.join(_BENCH, "opclfnpre_labels.json"))); pre = op(OP_CLFN_PRE)
    values = {"function name": fn, "path": dll, "calling convention": calling_convention, "reentrant": bool(reentrant)}
    for vi_name, ls in table.items():
        do_set = any(vi_name.startswith(n) for n in ("Function Name", "Path", "Calling Convention", "Reentrant"))
        for l in ls:
            if l.lower().startswith("operation"):
                pre.SetControlValue(l, 1 if do_set else 0)
            else:
                for key, v in values.items():
                    if l.lower().startswith(key):
                        pre.SetControlValue(l, v)
    _run(pre)
    ensure_loaded(target)   # edits are silently declined on a target that is not fully loaded
    before = uids(target, "CallLibrary"); inv0 = uids(target, "Invoke")
    vi = op(OP_CLFN_BUILD)
    vi.SetControlValue("vi path", target); vi.SetControlValue("Class Name", "Terminal"); vi.SetControlValue("index", 0); vi.SetControlValue("location (0, 0)", list(location))
    vi.SetControlValue("path", dll); vi.SetControlValue("function name", fn); vi.SetControlValue("calling convention", calling_convention); vi.SetControlValue("reentrant", bool(reentrant))
    for lab in ("operation", "operation 2", "operation 3", "operation 4", "operation 5"):
        vi.SetControlValue(lab, 1)
    vi.SetControlValue("binary string", bytes.fromhex(flat_hex).decode("latin-1"))
    _run(vi)
    e1 = vi.GetControlValue("error out"); e2 = vi.GetControlValue("error out 2"); terms = vi.GetControlValue("Terms[]")
    for o in new_since(target, "Invoke", inv0):                        # the builder's junk Invoke on the target
        ids = [x["uid"] for x in report(target, "Invoke")]
        if o["uid"] in ids:
            delete_object(target, "Invoke", ids.index(o["uid"]))
    new = new_since(target, "CallLibrary", before)
    if len(new) != 1:
        raise RuntimeError(f"build_clfn: {len(new)} new CallLibrary nodes; errors {e1} {e2}")
    return new[0]["uid"], len(terms or ()), (e1, e2)


OP_CONPANE = os.path.join(CLAUDEDEV, "OpConPane_v0.vi")
OP_CONPANE_ASSIGN = os.path.join(CLAUDEDEV, "OpConPaneAssign_v0.vi")


def conpane(target, max_terminals=32):
    """The connector pane of `target` as {terminal index: control label}, with None for a FREE terminal (OpConPane_v0,
    built 2026-09-10: VI.Connector Pane:Reference 23E -> ConnectorPane.Controls[] 239A8403 -> Index Array -> Control.Label).
    Reading a free terminal costs one ~8 s automatic-error dialog, so this stops at `Number of Connection Terminals`."""
    vi = op(OP_CONPANE)
    vi.SetControlValue("vi path", target)
    for l in ("Names", "Names 2"):
        vi.SetControlValue(l, [])
    for l in ("Class Name", "Class Name 2"):
        vi.SetControlValue(l, "")
    out, n = {}, None
    for i in range(max_terminals):
        vi.SetControlValue("index", i)
        try:
            _run(vi); out[i] = vi.GetControlValue("Text")
        except RuntimeError:
            out[i] = None
        if n is None:
            try:
                n = int(vi.GetControlValue("Number of Connection Terminals"))
            except Exception:
                n = None
        if n and i >= n - 1:
            break
    return out


OP_REPLACE_GOBJ = os.path.join(CLAUDEDEV, "OpReplaceGObj_v0.vi")
_REPLACE_LABELS = None


def replace_object(target, uid, new_path):
    """Swap the object `uid` on `target`'s diagram for the subVI (or control) at `new_path`, in place - the callee-swap
    verb (card 75-4, m8 plan PD14(d)): OpReplaceGObj_v0 = OpOwnerChain_v1's `UID to GObject Reference.vi` -> Invoke
    `GObject.Replace` 632A402 (Path) -> `GObject.UID` 632A813 on the returned ref -> Close Reference (that ref).
    Built by tools/bench/diag_swap_build.py; labels in tools/bench/swap_verb_75_oplabels.json. Returns
    {"new_uid", "err_replace", "err_uid", "err"}; err_* are "" when clean. Wires are kept or not as LabVIEW decides -
    the caller MEASURES that (tools/bench/diag_swap_measure.py), this verb asserts nothing about it."""
    global _REPLACE_LABELS
    if _REPLACE_LABELS is None:
        import json
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "bench", "swap_verb_75_oplabels.json"),
                  encoding="utf-8") as f:
            _REPLACE_LABELS = json.load(f)
    lab = _REPLACE_LABELS
    ensure_loaded(target)   # edits are silently declined on a target that is not fully loaded
    vi = op(OP_REPLACE_GOBJ)
    vi.SetControlValue(lab["vi_path"], target)
    vi.SetControlValue(lab["class_name"], "Diagram"); vi.SetControlValue(lab["index"], 0)   # donor seed, keep legal
    vi.SetControlValue(lab["uid_in"], int(uid))
    vi.SetControlValue(lab["path"], new_path)
    vi.SetControlValue(lab["new_uid"], 0)
    _run(vi)
    return {"new_uid": int(vi.GetControlValue(lab["new_uid"])), "err_replace": _err(vi, lab["err_replace"]) or "",
            "err_uid": _err(vi, lab["err_uid"]) or "", "err": _err(vi, "error out") or ""}


def conpane_assign(target, control_label, terminal_index):
    """Assign the front-panel control `control_label` of `target` to connector-pane terminal `terminal_index`
    (ConnectorPane.Assign Control To Terminal 239A8000 — OpConPaneAssign_v0, 2026-09-10). Verified on TRACK_kernel_v1.

    Two rules this cost a run each to learn: the target's panel MUST be open first (an edit on a VI loaded only through
    GetVIReference is declined SILENTLY, with a clean error cluster and a byte-identical file), and the terminal must
    already be FREE — never change `Pattern`, which clears every assignment and breaks the callers. Returns the new map."""
    open_panel(target); time.sleep(0.5)
    labels = [l for _, l, _ in fp_labels(target)]
    if control_label not in labels:
        raise RuntimeError(f"conpane_assign: {control_label!r} is not a front-panel object of {os.path.basename(target)}")
    ensure_loaded(target)   # edits are silently declined on a target that is not fully loaded
    vi = op(OP_CONPANE_ASSIGN)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("index", labels.index(control_label))
    vi.SetControlValue("Terminal Index", int(terminal_index))
    for l in ("Names", "Names 2"):
        vi.SetControlValue(l, [])
    for l in ("Class Name", "Class Name 2"):
        vi.SetControlValue(l, "")
    _run(vi)
    err = _err(vi)
    if err:
        raise RuntimeError(f"conpane_assign: {err}")
    save(target)
    got = conpane(target)
    if got.get(int(terminal_index)) != control_label:
        raise RuntimeError(f"conpane_assign: terminal {terminal_index} holds {got.get(int(terminal_index))!r}, not {control_label!r}")
    return got


OP_MAKE_DEFAULT = os.path.join(CLAUDEDEV, "OpMakeDefault_v0.vi")


def make_default(target, values=None):
    """Set `values` ({control label: value}) on `target` through VI Server, then make ALL current front-panel values the
    defaults (VI method `Default Values:Make Current Default`, ID 3F3 — OpMakeDefault_v0, built 2026-09-10) and save.
    Why an op: the ActiveX VirtualInstrument has no MakeCurValsDefault, and a plain SetControlValue on a loaded subVI never
    reaches its calls. The touch loads the target's front panel and inflates its call time (~9 ms/frame measured on
    TRACK_kernel_v1) — RESTART LabVIEW before timing anything that calls `target` (docs/NAMES.md, timing protocol)."""
    with vi_ref(target) as vi:                         # P3: counted + released
        for lab, v in (values or {}).items():
            vi.SetControlValue(lab, v)
    o = op(OP_MAKE_DEFAULT); o.SetControlValue("vi path", target); _run(o)
    return save(target)


OP_BUILD_CASE = os.path.join(CLAUDEDEV, "OpBuildCase_v1.vi")


def build_case(target, location, selector_name, input_names=(), frame_names=("0, Default", "1")):
    """Place a Case Structure on `target`'s top-level diagram (erdosmiller `Create Case Structure.vi` via OpBuildCase_v1,
    built 2026-09-10) whose selector is the FRONT-PANEL CONTROL labelled `selector_name` and whose input tunnels come from the
    controls `input_names` — all given as plain label strings; the op resolves them to terminal refnums inside LabVIEW
    (`Get Controls.vi` x2 + Index Array). `frame_names` MUST have exactly one entry per frame the selector type creates
    (a numeric selector makes 2 frames: pass ("0, Default", "1") or ("0", "1, Default")); any other length — including the
    old integer "2" — trips error 1302 `Frame Names` INSIDE the library VI, an 8 s dialog no sink of ours can catch.
    Functional contract (tools/bench/case_v1_test.py, 2026-09-10): +1 CaseStructure, +2 Diagrams (frames = diagram_index 1, 2
    for drop_subvi), +1 wire per name (selector + each input tunnel), ExecState 1, no dialog, ~0.1 s.
    Never list the selector control in `input_names` as well. Returns the new CaseStructure dict."""
    ensure_loaded(target)   # edits are silently declined on a target that is not fully loaded
    before = uids(target, "CaseStructure"); inv0 = uids(target, "Invoke")
    vi = op(OP_BUILD_CASE)
    for lab, val in (("vi path", target), ("vi path 2", target), ("Class Name", "Terminal"), ("index", 0),
                     ("location (0, 0)", list(location)), ("Frames", list(frame_names)),
                     ("Control Names", [selector_name]), ("Control Names 2", list(input_names))):
        vi.SetControlValue(lab, val)
    _run(vi)
    errs = tuple(vi.GetControlValue(l) for l in ("error out", "error out 2"))
    for o in new_since(target, "Invoke", inv0):
        ids = [x["uid"] for x in report(target, "Invoke")]
        if o["uid"] in ids:
            delete_object(target, "Invoke", ids.index(o["uid"]))
    new = new_since(target, "CaseStructure", before)
    if len(new) != 1 or any(e and e[0] for e in errs):
        raise RuntimeError(f"build_case: {len(new)} new CaseStructure; errors {errs}")
    return new[0]


OP_CONNECT_NESTED_V2 = os.path.join(CLAUDEDEV, "OpConnectNested_v2.vi")
_CONNECT_NESTED_V2_LABELS = None


def connect_nested_v2(target, sink_diag, sink_node, sink_term, src_diag, src_node, src_term, labels=None):
    """Wire Diagram[src_diag].Nodes[src_node].Terminals[src_term] (SOURCE) into
    Diagram[sink_diag].Nodes[sink_node].Terminals[sink_term] (SINK) through OpConnectNested_v2.vi.
    Returns (wire delta, ExecState after, op error string) - the SAME contract as
    `connect_nested_v1` (tools/recipes/build_opconnectnested_v1.py:418), which this mirrors.

    ADDED 2026-09-21 (cycle 64 material #2). ADDITIVE ONLY: no existing function here was modified.
    The ONE difference from `connect_nested_v1` is that this wrapper reads NO `UID` / `Name` /
    `UID 2` / `Is Broken?` indicator back, because OpConnectNested_v2.vi is the byte-copy of
    OpConnectNested_v1.vi (donor rule 51(h), precedent OpCreateLocalRead_v0 on OpCreateLocal_v0)
    with the embedded `Wire.Is Broken?` 6371004 readback property node(s) DELETED. docs/NAMES.md:912-929
    records that reading `Is Broken?` perturbs the target, and that every op descended from
    OpNetInfo_v1 carries that reader by inheritance (tools/recipes/build_opnetinfo.py:151).

    `labels` defaults to tools/bench/opconnectnested_v2_labels.json - the same control-label map as
    v1's, because v2 is a file copy of v1 and its front panel is unchanged (the `UID 2` /
    `Is Broken?` indicators are left in place, unwired; deleting panel objects is an unproven verb).

    !! 2026-09-22 (cycle 65 repair): **OpConnectNested_v2.vi WAS NEVER BUILT.** It is the only one of
    the 51 OP_* constants in this file whose VI is absent from claudeDev (docs/cycle27-plan.md:2558
    already recorded it as not built; `tools/bench/diag_c64_connect_v2.py` is the diagnostic that was
    meant to create it and did not). Until 2026-09-22 this wrapper failed LATE, as
    `com_error 5507 File not found` raised from inside GetVIReference by `op()` - which in
    `build_d1_m3a3.py` run 1 happened AFTER a wire had already been deleted, leaving a dropped
    consumer on disk. It now raises at ENTRY, before touching LabVIEW, so a caller can never mutate a
    VI and then die on this. Use `connect_nested_v1`
    (tools/recipes/build_opconnectnested_v1.py:418, op VI claudeDev\\OpConnectNested_v1.vi, SHIPPED)
    instead. The public name is kept deliberately - deleting an API silently is worse than refusing it.
    """
    raise RuntimeError(
        "gscript.connect_nested_v2 IS A DANGLING WRAPPER - ITS OP VI WAS NEVER BUILT.\n"
        "  missing op VI : %s\n"
        "  use instead   : connect_nested_v1(target, sink_diag, sink_node, sink_term, "
        "src_diag, src_node, src_term, labels)\n"
        "                  from tools/recipes/build_opconnectnested_v1.py:418 "
        "(op VI OpConnectNested_v1.vi, SHIPPED)\n"
        "  why this raises at entry: this call used to fail LATE as com_error 5507 inside "
        "GetVIReference; in build_d1_m3a3.py run 1 that happened AFTER a wire delete, so the VI on "
        "disk was left with a dropped consumer. Nothing has been touched by this call.\n"
        "  evidence: docs/cycle27-plan.md:2558 (recorded not built); "
        "tools/bench/diag_c64_connect_v2.py (the build diagnostic that did not produce it)"
        % OP_CONNECT_NESTED_V2)


def _connect_nested_v2_body_UNREACHABLE(target, sink_diag, sink_node, sink_term,
                                        src_diag, src_node, src_term, labels=None):
    """The original body of `connect_nested_v2`, kept VERBATIM and unreachable so that the wrapper can
    be restored in one edit the day OpConnectNested_v2.vi is actually built. Never call this.
    """
    global _CONNECT_NESTED_V2_LABELS
    if labels is None:
        if _CONNECT_NESTED_V2_LABELS is None:
            import json
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "bench",
                                   "opconnectnested_v2_labels.json"), encoding="utf-8") as f:
                _CONNECT_NESTED_V2_LABELS = json.load(f)
        labels = _CONNECT_NESTED_V2_LABELS
    ensure_loaded(target)
    w0 = count(target, "Wire")
    vi = op(OP_CONNECT_NESTED_V2)
    vi.SetControlValue(labels["vi_path"], target)
    vi.SetControlValue(labels["class_name"], "Diagram")
    vi.SetControlValue(labels["sink_diag"], int(sink_diag))
    vi.SetControlValue(labels["sink_node"], int(sink_node))
    vi.SetControlValue(labels["sink_term"], int(sink_term))
    vi.SetControlValue(labels["src_diag"], int(src_diag))
    vi.SetControlValue(labels["src_node"], int(src_node))
    vi.SetControlValue(labels["src_term"], int(src_term))
    for k, v in (("error in (no error)", (False, 0, "")), ("error in", (True, 1, "neutralised creator")),
                 ("Class Name 3", ""), ("Class Name 2", "")):
        try:
            vi.SetControlValue(k, v)
        except Exception:
            pass
    err = ""
    try:
        _run(vi)
        err = _err(vi, "error out") or ""
    except RuntimeError as e:
        err = "modal dialog (dismissed)" if "modal dialog" in str(e) else f"EXC {str(e)[:140]}"
    return count(target, "Wire") - w0, exec_state(target), err
