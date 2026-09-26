r"""diag_c105b_t0.py - card 105-2 T0: offline check that `lv_gui.ps1 -Action shotwin -Hwnd <n>` captures one exact
non-LabVIEW window by PrintWindow(flag 2) with no focus, and that the png is non-blank. No LabVIEW touched.
FOUND FIRST: lv_gui.ps1 ShotWindow (PrintWindow flag 2, existing), shotwin needed -Title + a LabVIEW pid; -Hwnd added.
PREDICTION: T0a exit 0 and png exists  T0b png has >= 16 distinct colours  T0c foreground hwnd unchanged  T0d secs recorded
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c105b_t0.log -- py -u tools/bench/diag_c105b_t0.py"""
import ctypes as C, ctypes.wintypes as W, hashlib, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools")); import protocol as P             # noqa: E402,E401
u = C.windll.user32; EP = C.WINFUNCTYPE(W.BOOL, W.HWND, W.LPARAM); cand = []
def cb(h, _):
    if u.IsWindowVisible(h):
        b = C.create_unicode_buffer(256); u.GetWindowTextW(h, b, 256); r = W.RECT(); u.GetWindowRect(h, C.byref(r))
        pid = W.DWORD(); u.GetWindowThreadProcessId(h, C.byref(pid))
        if b.value and r.right - r.left > 300 and r.bottom - r.top > 200: cand.append((int(h), b.value[:60], pid.value))  # noqa: E701
    return True
u.EnumWindows(EP(cb), 0); print("[t0] candidates", cand[:6], flush=True)
h, title, pid = cand[0]; fg0 = int(u.GetForegroundWindow() or 0)
out = os.path.join(HERE, "diag_c105b_out", "t0_hwnd_%d.png" % h); os.makedirs(os.path.dirname(out), exist_ok=True)
t = time.time()
r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
                    "& .\\tools\\lv_gui.ps1 -Action shotwin -Hwnd %d -Out '%s'" % (h, out)], cwd=ROOT, capture_output=True, text=True, timeout=60)
secs = round(time.time() - t, 2); fg1 = int(u.GetForegroundWindow() or 0)
print("[t0] rc", r.returncode, "secs", secs, "out", r.stdout.strip()[:300], "err", r.stderr.strip()[:300], flush=True)
ncol = 0
if os.path.isfile(out):
    from PIL import Image
    im = Image.open(out).convert("RGB"); cols = im.getcolors(maxcolors=1 << 20); ncol = len(cols) if cols else 1 << 20
print("[t0] window", h, repr(title), "pid", pid, "distinct_colours", ncol, "fg before/after", fg0, fg1, flush=True)
G = {"T0a exit 0 and png exists": r.returncode == 0 and os.path.isfile(out), "T0b png >=16 distinct colours": ncol >= 16,
     "T0c foreground unchanged": fg0 == fg1, "T0d secs recorded": secs > 0}
for k, v in G.items(): print("GATE %-40s %s" % (k, "PASS" if v else "FAIL"), flush=True)   # noqa: E701
bad = [k for k, v in G.items() if not v]
art = [{"path": os.path.relpath(out, ROOT), "md5": hashlib.md5(open(out, "rb").read()).hexdigest()}] if os.path.isfile(out) else []
print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, art)), flush=True)
sys.exit(1 if bad else 0)
