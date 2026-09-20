"""kb_com.py — run and configure LabVIEW driver VIs over the ActiveX/COM server, no GUI.

Why: KernelBuilder_v1.vi (the VI-Scripting driver that builds the parallel kernel) used to be
run by GUI automation (focus window, click Run, poll). LabVIEW's ActiveX server (enabled in
Tools>Options>VI Server, together with TCP port 3364 on this rig) lets an external script
set front-panel control values, run the VI synchronously, and read values back — replacing
every click and screenshot in the run/verify loop.

Hard-won COM notes (LabVIEW 2026 / pywin32 306+, discovered 2026-08-27):
  * `win32com.client.dynamic.Dispatch` MUST be used. Plain `Dispatch`/`EnsureDispatch` load the
    typed wrapper from the "LabVIEW 8.0 Type Library", whose _IApplication interface LACKS
    GetVIReference; once gencache is populated even plain Dispatch returns the typed stub.
  * On the returned VirtualInstrument CDispatch, `vi.Run` resolves as a property (None), not a
    method — invoke it by DISPID with DISPATCH_METHOD instead (dispid 1017 here, but always
    resolve via GetIDsOfNames).
  * GetControlValue/SetControlValue work through the normal dynamic dispatch and address
    front-panel controls BY LABEL — hence the standing rule: driver inputs belong on the front
    panel as controls, not as diagram constants.

Usage:
  py tools\\kb_com.py run  [vi_path]                 # run the driver once, print error out if present
  py tools\\kb_com.py get  <control> [vi_path]       # read one control
  py tools\\kb_com.py set  <control> <json> [vi_path]# set one control (value as JSON literal)
  py tools\\kb_com.py info [vi_path]                 # read the standard config controls
  py tools\\kb_com.py check <vi_path>                # BROKEN/OK verdict via ExecState (no GUI)
  py tools\\kb_com.py save <vi_path>                 # SaveInstrument (claudeDev files only)
  py tools\\kb_com.py runjob <target> [driver] [t]   # one clone, one target, watchdog-aborted run
  py tools\\kb_com.py batch <t1> <t2> ...            # parallel runjobs, one subprocess per target

Third-party: uses pywin32 (PSF/BSD-like licence, https://github.com/mhammond/pywin32) as a
dependency only; no third-party code is vendored here.
"""
import sys, json, time
import pythoncom
from win32com.client import dynamic

DEFAULT_VI = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\KernelBuilder_v1.vi"

KNOWN_CONTROLS = [
    "Shift Registers?", "Conditional Terminal?", "Loop Count?", "Stop Condition?",
    "Inputs Indexing?", "Loop Terminal Types", "Number of Static Parallel Instances",
]

def connect(vi_path, options=0):
    """options=0x40 asks for a reentrant-run reference: on a VI set to
    'Shared clone reentrant execution' each such call yields an independent
    clone, so several jobs can run the same driver concurrently."""
    lv = dynamic.Dispatch("LabVIEW.Application")
    vi = lv.GetVIReference(vi_path, "", False, options)
    return lv, vi

def invoke_method(com_obj, name, *args):
    ole = getattr(com_obj, "_oleobj_", com_obj)
    dispid = ole.GetIDsOfNames(0, name)
    return ole.Invoke(dispid, 0, pythoncom.DISPATCH_METHOD, 1, *args)

def run(vi):
    t0 = time.time()
    invoke_method(vi, "Run")
    return time.time() - t0

def run_robust(vi_path, timeout_s=90, retries=1):
    """Run with a watchdog: LabVIEW's scripting chain intermittently idles for many minutes
    (cause unknown; observed under GUI and COM alike, always AFTER the useful edits are made).
    A watchdog thread calls Abort on the same VI when the deadline passes; one retry usually
    succeeds. Returns (ok, seconds, note)."""
    import threading
    for attempt in range(retries + 1):
        pythoncom.CoInitialize()
        _, vi = connect(vi_path)
        done = threading.Event()

        def watchdog():
            if not done.wait(timeout_s):
                try:
                    pythoncom.CoInitialize()
                    _, vi2 = connect(vi_path)
                    invoke_method(vi2, "Abort")
                except Exception:
                    pass

        w = threading.Thread(target=watchdog, daemon=True)
        w.start()
        t0 = time.time()
        try:
            invoke_method(vi, "Run")
        finally:
            done.set()
        dt = time.time() - t0
        if dt < timeout_s:
            return True, dt, "clean run (attempt %d)" % (attempt + 1)
        if attempt < retries:
            time.sleep(2)
    return False, dt, "aborted by watchdog on final attempt (edits may still be complete)"

def get_ctl(vi, name):
    return vi.GetControlValue(name)

def set_ctl(vi, name, value):
    vi.SetControlValue(name, value)

def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "info"
    if cmd == "run":
        vi_path = args[1] if len(args) > 1 else DEFAULT_VI
        _, vi = connect(vi_path)
        dt = run(vi)
        print("RUN OK in %.1f s" % dt)
        for name in ("error out", "Error Out", "error"):
            try:
                print("%s = %r" % (name, get_ctl(vi, name)))
                break
            except Exception:
                pass
    elif cmd == "get":
        name = args[1]
        vi_path = args[2] if len(args) > 2 else DEFAULT_VI
        _, vi = connect(vi_path)
        print("%s = %r" % (name, get_ctl(vi, name)))
    elif cmd == "set":
        name, value = args[1], json.loads(args[2])
        if isinstance(value, list):
            value = tuple(value)
        vi_path = args[3] if len(args) > 3 else DEFAULT_VI
        _, vi = connect(vi_path)
        set_ctl(vi, name, value)
        print("SET %s -> read-back = %r" % (name, get_ctl(vi, name)))
    elif cmd == "runjob":
        # runjob <target_vi> [driver_vi] [timeout_s] — one clone, one target, synchronous.
        # Used directly for a single fire, and as the child process of `batch`.
        target = args[1]
        driver = args[2] if len(args) > 2 else DEFAULT_VI
        timeout_s = float(args[3]) if len(args) > 3 else 120
        pythoncom.CoInitialize()
        _, vi = connect(driver, 0x40)
        set_ctl(vi, "vi path", target)
        import threading
        done = threading.Event()
        def watchdog():
            if not done.wait(timeout_s):
                # Cross-thread Abort on the clone ref does NOT work (STA marshaling) —
                # verified 2026-08-27: two hung clones ignored it for 10 min. What DOES
                # work: Abort on the BASE VI ref from a fresh process; it released both
                # hung clone runs immediately.
                import subprocess
                code = ("from win32com.client import dynamic\n"
                        "import pythoncom\n"
                        "lv = dynamic.Dispatch('LabVIEW.Application')\n"
                        "vi = lv.GetVIReference(r'%s','',False,0)\n"
                        "o = vi._oleobj_\n"
                        "o.Invoke(o.GetIDsOfNames(0,'Abort'),0,pythoncom.DISPATCH_METHOD,0)\n" % driver)
                try:
                    subprocess.run([sys.executable, "-c", code], timeout=30)
                    print("WATCHDOG: base-ref Abort issued after %ds" % timeout_s, flush=True)
                except Exception as e:
                    print("WATCHDOG: abort failed: %s" % e, flush=True)
        threading.Thread(target=watchdog, daemon=True).start()
        t0 = time.time()
        try:
            invoke_method(vi, "Run")
        finally:
            done.set()
        dt = time.time() - t0
        status = "OK" if dt < timeout_s else "TIMEOUT-ABORTED"
        err = ""
        for name in ("error out", "Error Out"):
            try:
                err = repr(get_ctl(vi, name)); break
            except Exception:
                pass
        print("JOB %s  target=%s  %.1fs  error out=%s" % (status, target, dt, err))
    elif cmd == "batch":
        # batch <target1> <target2> ... — SEQUENTIAL jobs in one background process.
        # Concurrent clone dispatch was tried (2026-08-27) and does NOT work over ActiveX:
        # GetVIReference(...,0x40) hands every caller the same base VI (job2's SetControlValue
        # overwrote job1's config mid-run; job2's Run failed with 0x3E8). True parallelism needs
        # a G-native Start Asynchronous Call launcher. Sequential still gives fire-and-forget
        # (launch the batch in the background, inspect later), and VI Scripting edits serialize
        # through LabVIEW's root loop anyway, so little real speed is lost.
        import subprocess, os
        targets = args[1:]
        assert len(set(t.lower() for t in targets)) == len(targets), "duplicate targets forbidden"
        for t in targets:
            p = subprocess.run([sys.executable, os.path.abspath(__file__), "runjob", t],
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True, encoding="utf-8", errors="replace")
            print("=== %s ===\n%s" % (t, p.stdout.strip()), flush=True)
    elif cmd == "check":
        # check <vi_path> — programmatic wiring/validity verdict, no screenshots:
        # ExecState 0 = BROKEN (run arrow shattered), 1 = idle/runnable, 2/3 = running.
        vi_path = args[1] if len(args) > 1 else DEFAULT_VI
        _, vi = connect(vi_path)
        st = vi.ExecState
        names = {0: "BROKEN (bad wiring / missing subVI)", 1: "OK (idle, runnable)",
                 2: "RUNNING (top level)", 3: "RUNNING (as subVI)"}
        print("%s : ExecState=%s -> %s" % (vi_path, st, names.get(st, "?")))
    elif cmd == "save":
        # save <vi_path> — SaveInstrument via COM: persists in-memory scripted edits to disk.
        # ONLY for claudeDev-derived work; never point this at an original VI.
        vi_path = args[1]
        assert "claudedev" in vi_path.lower(), "refusing to save outside user.lib\\claudeDev"
        _, vi = connect(vi_path)
        invoke_method(vi, "SaveInstrument")
        print("SAVED %s" % vi_path)
    elif cmd == "info":
        vi_path = args[1] if len(args) > 1 else DEFAULT_VI
        _, vi = connect(vi_path)
        print("VI:", vi.Name)
        for name in KNOWN_CONTROLS:
            try:
                print("  %s = %r" % (name, get_ctl(vi, name)))
            except Exception as e:
                print("  %s : <no such control> (%s)" % (name, e))
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
