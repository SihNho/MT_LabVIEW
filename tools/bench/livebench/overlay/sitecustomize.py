# ---
# labview: none
# hardware: none
# ---
"""livebench write fence (card chat-B7). Loaded by EVERY Python process of a bench arm, because lb_setup/lb_run put this
directory first on PYTHONPATH (Python imports `sitecustomize` at start-up; the install has none of its own - measured
2026-10-06: importlib.util.find_spec('sitecustomize') is None on Python 3.10.9).

It installs a sys.addaudithook that classifies every WRITE-type file event (open in w/a/x/+ mode or with write flags,
shutil.copyfile/copy dst, os.rename/replace/remove/rmdir/mkdir, shutil.rmtree) by path:
  arm       under LIVEBENCH_CLAUDEDEV (claudeDev\\bench\\<arm>)                      -> allowed, logged
  fixture   under claudeDev\\NIScriptingExamples\\Moving Objects (gscript's move fixture, restored by gscript itself)
                                                                                    -> allowed, logged
  outside   under the claudeDev root but not one of the two above                   -> REFUSED (PermissionError), logged
  main      under the MAIN project tree (LIVEBENCH_MAIN)                            -> REFUSED, logged
  anything else (the arm's worktree, %TEMP%, ~/.claude)                             -> not logged
LIVEBENCH_CONTAIN=log only logs (the contain-dry check uses it). LabVIEW-side saves (COM SaveInstrument, GUI Ctrl+S)
are not file events of this process: gscript.save/gui_save are fenced by the CLAUDEDEV_OUT patch (lb_setup.PATCHES).
Log: LIVEBENCH_WRITELOG (jsonl), one line per classified event."""
import os
import sys
import threading

_OUT = os.environ.get("LIVEBENCH_CLAUDEDEV") or ""
_ROOT = os.environ.get("LIVEBENCH_CLAUDEDEV_ROOT") or ""
_MAIN = os.environ.get("LIVEBENCH_MAIN") or ""
_LOG = os.environ.get("LIVEBENCH_WRITELOG") or ""
_MODE = os.environ.get("LIVEBENCH_CONTAIN", "enforce")
_TL = threading.local()
_WFLAGS = getattr(os, "O_WRONLY", 1) | getattr(os, "O_RDWR", 2) | getattr(os, "O_APPEND", 8) | \
    getattr(os, "O_CREAT", 256) | getattr(os, "O_TRUNC", 512)


def _n(p):
    try:
        if isinstance(p, bytes):
            p = p.decode("utf-8", "replace")
        return os.path.normcase(os.path.abspath(os.fspath(p)))
    except Exception:                                                              # noqa: BLE001
        return None


def _under(p, d):
    return bool(d) and (p == d or p.startswith(d.rstrip("\\/") + os.sep))


_N_OUT, _N_ROOT, _N_MAIN = _n(_OUT) if _OUT else "", _n(_ROOT) if _ROOT else "", _n(_MAIN) if _MAIN else ""
_N_FIX = os.path.join(_N_ROOT, "niscriptingexamples", "moving objects") if _N_ROOT else ""


def classify(path):
    p = _n(path)
    if not p:
        return None
    if _under(p, _N_OUT):
        return "arm"
    if _under(p, _N_FIX):
        return "fixture"
    if _under(p, _N_ROOT):
        return "outside"
    if _under(p, _N_MAIN):
        return "main"
    return None


def _log(rec):
    if not _LOG:
        return
    import json
    import time
    rec["t"] = time.strftime("%Y-%m-%d %H:%M:%S")
    rec["pid"] = os.getpid()
    rec["argv0"] = (sys.argv[0] if sys.argv else "")[-120:]
    with open(_LOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")


def _paths(event, args):
    if event == "open":
        path, mode, flags = (list(args) + [None, None, None])[:3]
        if isinstance(path, int):
            return []
        w = (isinstance(mode, str) and any(c in mode for c in "wax+")) or (mode is None and isinstance(flags, int)
                                                                           and bool(flags & _WFLAGS))
        return [path] if w else []
    if event in ("shutil.copyfile", "shutil.copytree"):
        return [args[1]] if len(args) > 1 else []
    if event in ("os.rename", "os.replace"):
        return list(args[:2])
    if event in ("os.remove", "os.rmdir", "os.mkdir", "shutil.rmtree", "shutil.move"):
        return list(args[:1])
    return []


def _hook(event, args):
    if getattr(_TL, "busy", False):
        return
    try:
        paths = _paths(event, args)
    except Exception:                                                              # noqa: BLE001
        return
    if not paths:
        return
    _TL.busy = True
    try:
        for p in paths:
            if p is None or isinstance(p, int):
                continue
            c = classify(p)
            if c is None:
                continue
            refuse = c in ("outside", "main") and _MODE == "enforce"
            _log({"event": event, "path": str(p), "class": c, "refused": refuse})
            if refuse:
                raise PermissionError("livebench fence (card chat-B7): %s write refused for %s - this arm writes only "
                                      "under %s" % (c, p, _OUT))
    finally:
        _TL.busy = False


if _N_ROOT or _N_MAIN:
    sys.addaudithook(_hook)
