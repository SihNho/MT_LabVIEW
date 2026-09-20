"""clfn_break_probe.py - why is a VI broken (ExecState 0) right after gscript.build_clfn?  Four scratch builds, same LabVIEW:
  A kernel32.dll / GetTickCount / [ret U32]                 -> DLL-independent structural problem if 0
  B GPU Tracking.dll / mt2_track_simple / full 15 records   -> the real case
  C GPU Tracking.dll / mt2_track_simple / [ret I32] only    -> parameter-list content vs DLL/function resolution
  D GPU Tracking.dll / mt2_close / [ret void-ish I32, ctx I64] -> another export of the same DLL
Each: FPTARGET copy -> clear -> build_clfn -> purge junk -> Remove Bad Wires -> ExecState / Invoke count / Wire count."""
import os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "gpu"))
import gscript as g
import clfn_params as cp
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
DLL = os.path.join(g.CLAUDEDEV, "Debug", "GPU Tracking.dll"); K32 = r"C:\Windows\System32\kernel32.dll"
CASES = [
    ("A kernel32/GetTickCount ret U32", K32, "GetTickCount", [("return value", "num", "U32", "value", 0)]),
    ("B ours/mt2_track_simple full15", DLL, "mt2_track_simple", cp.PARAMS),
    ("C ours/mt2_track_simple ret-only", DLL, "mt2_track_simple", cp.PARAMS[:1]),
    ("D ours/mt2_close ret I32 + ctx I64", DLL, "mt2_close", [("return value", "num", "I32", "value", 0), ("ctx", "num", "I64", "value", 0)]),
    ("E ours at NO-space path (+cufft beside), ret-only", r"C:\Users\KimLab\AppData\Local\Temp\mtnospace\mt_track.dll", "mt2_track_simple", cp.PARAMS[:1]),
    ("G version.dll copy at spaced path+name", r"C:\Users\KimLab\AppData\Local\Temp\mt spaced dir\ver sion.dll", "GetFileVersionInfoSizeW", [("return value", "num", "U32", "value", 0)]),
    ("H kernel32 by name only (no dir)", "kernel32.dll", "GetTickCount", [("return value", "num", "U32", "value", 0)]),
    ("I ours+cufft at spaced Temp path+name", r"C:\Users\KimLab\AppData\Local\Temp\mt spaced dir\GPU Tracking.dll", "mt2_track_simple", cp.PARAMS[:1]),
    ("J ours as claudeDev\\Debug\\mt_track.dll (Program Files, no-space name)", os.path.join(g.CLAUDEDEV, "Debug", "mt_track.dll"), "mt2_track_simple", cp.PARAMS[:1]),
    ("K ours as claudeDev\\Debug\\GPU Tracking.dll again", DLL, "mt2_track_simple", cp.PARAMS[:1]),
] + [(f"L{k:02d} mt_track.dll first {k} records (last = {cp.PARAMS[k - 1][0]})", os.path.join(g.CLAUDEDEV, "Debug", "mt_track.dll"), "mt2_track_simple", cp.PARAMS[:k]) for k in range(2, 16)] + [
    # M: return value + ONE parameter each (which record kinds are legal?)
    (f"M{i:02d} ret + {p[0]} ({p[1]} {p[2]} {p[3]} dims {p[4]})", os.path.join(g.CLAUDEDEV, "Debug", "mt_track.dll"), "mt2_track_simple", [cp.PARAMS[0], p]) for i, p in enumerate(cp.PARAMS[1:], 1)] + [
    # N: cal_path string-record variants (LabVIEW's own read-back form was dims 1 / numeric I32)
    ("N1 ret + cal_path dims1 numI32", os.path.join(g.CLAUDEDEV, "Debug", "mt_track.dll"), "mt2_track_simple", [cp.PARAMS[0], ("cal_path", "str", "I32", "cstr", 1)]),
    ("N2 ret + cal_path dims0 numI32", os.path.join(g.CLAUDEDEV, "Debug", "mt_track.dll"), "mt2_track_simple", [cp.PARAMS[0], ("cal_path", "str", "I32", "cstr", 0)]),
    ("N3 ret + cal_path dims1 numI8", os.path.join(g.CLAUDEDEV, "Debug", "mt_track.dll"), "mt2_track_simple", [cp.PARAMS[0], ("cal_path", "str", "I8", "cstr", 1)]),
    ("N4 ret + width I32 dims1", os.path.join(g.CLAUDEDEV, "Debug", "mt_track.dll"), "mt2_track_simple", [cp.PARAMS[0], ("width", "num", "I32", "value", 1)]),
]
SEL = sys.argv[1] if len(sys.argv) > 1 else "ABCD"
for tag, dll, fn, params in CASES:
    if tag[0] not in SEL:
        continue
    T = os.path.join(g.CLAUDEDEV, f"SCRATCH_cb{tag[0]}.vi")
    if os.path.exists(T):
        os.remove(T)
    shutil.copyfile(os.path.join(g.CLAUDEDEV, "FPTARGET_v0.vi"), T); g.report(T, "SubVI"); g.open_panel(T); time.sleep(0.8)
    while g.count(T, "Node"):
        try:
            g.delete_object(T, "Node", 0)
        except RuntimeError as e:
            if "expected 1 object gone" not in str(e):
                raise
            break
    g.remove_bad_wires_scripted(T)
    while g.count(T, "ControlTerminal"):
        g.delete_object(T, "ControlTerminal", 0)
    g.remove_bad_wires_scripted(T); es0 = g.exec_state(T); inv0 = g.uids(T, "Invoke")
    t0 = time.time()
    try:
        uid, nterms, errs = g.build_clfn(T, (400, 300), dll, fn, cp.compose(params).hex())
    except Exception as e:
        print(f"{tag}: build_clfn EXC {str(e)[:200]}", flush=True); continue
    for o in g.new_since(T, "Invoke", inv0):
        ids = [x["uid"] for x in g.report(T, "Invoke")]
        if o["uid"] in ids:
            g.delete_object(T, "Invoke", ids.index(o["uid"]))
    g.remove_bad_wires_scripted(T)
    print(f"{tag}: base ExecState {es0} -> after CLFN ExecState {g.exec_state(T)} | terms {nterms} errs {errs} | nodes {g.count(T, 'Node')} invokes {g.count(T, 'Invoke')} wires {g.count(T, 'Wire')} | {time.time() - t0:.1f} s", flush=True)
    try:
        g.close_panel(T); os.remove(T)
    except Exception as e:
        print("   cleanup:", str(e)[:80], flush=True)
