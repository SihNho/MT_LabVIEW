r"""diag_c89_profiler_leg.py - card 89-4 Part 2 (tools/bench/profiler_run_plan_89.md with amendments A1 + A3): LabVIEW's own
Profile Performance and Memory window over an UNMODIFIED run of D1_s1_copy.vi. Nothing is built, no VI is edited.
FOUND FIRST: drive_m8.py + drive_original_copy_v5.leg (plan §1: a wrapper installed on v5.leg BEFORE drive_m8.main() is what
runs); tools/lv_errorlist.ocr_lines (RapidOCR, the project's label reader - used here as the plan's `locate_label`);
d0.gui / d0.shot / d0.win_rect / d0.win_present (lv_gui.ps1 wrappers). Every profiler act is capture -> locate (OCR on THAT
capture) -> act -> capture -> confirm; state-changing acts carry `-Exception NegativeSearch -Evidence <search record>`.
    --liveness            A1: open the copy (no run), Profile window -> Timing statistics/details ON, Time unit -> us, Start,
                          COM ExecState + SetControlValue round trip, Snapshot, Save, header check, Stop, LabVIEW closed.
    --picks N --run-s S   a profiled real leg: P-A..P-F before L1; Snapshot+Save #1 right after L9 (the L10 point, A3);
                          Snapshot+Save #2 after L12; the difference of the two tables is the experiment window.
PREDICTION CONTRACT (gates printed as `GATE PF..` lines; drive_m8's M1..M8 stand):
 PF1 Profile window listed <= 10 s after the menu click   PF2 Start clicked -> a `Stop` label is visible in the window
 PF3 COM alive after Start (state read <= 10 s, set/get round trip)   PF4 saved file exists, > 0 B, header has `VI Time`
 PF5 (leg) the kernel VI's row is present in table #2 (missing group names are PRINTED, not gated)   PF6 LabVIEW gone (M6)
 On any locate failure the act is NOT performed: RECOVERY_LOCKED (captures + `dialogs` only), the leg data stands.
"""
import json, os, re, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                            # noqa: E402
from lv_errorlist import ocr_lines                                              # noqa: E402
A = sys.argv[1:]; LIVE = "--liveness" in A
NPICK = int(A[A.index("--picks") + 1]) if "--picks" in A else 0
sys.argv = [sys.argv[0]] + [a for a in A if a != "--liveness"] + ["--leg", "s1"]
import drive_m8                                                                 # noqa: E402
import drive_original_copy_v5 as v5                                             # noqa: E402
d0 = v5.d0
EVID = "tools/bench/diag_c89_profiler_search.md"
PROF = "Profile Performance and Memory"
OUT = os.path.join(HERE, "diag_c89_profiler_out"); os.makedirs(OUT, exist_ok=True)
TS = time.strftime("%Y%m%d_%H%M%S"); TAG = "live" if LIVE else "p%d" % NPICK
PF, FACTS, LOCKED = {}, {"tag": TAG, "acts": [], "saved": []}, []
GROUPS = ["Find xy center", "Track xy", "check N bead pos", "median", "FIR", "Draw", "Flatten Pixmap", "N bead plot", "save trace", "save N xyz"]


def log(m):
    print("[profiler %s] %s" % (TAG, m), flush=True); FACTS["acts"].append("%.1f %s" % (time.time(), m))


def shot(name):
    d0.SHOTS = os.path.join(HERE, "m8_shots"); return v5.capture("prof_%s_%s" % (TAG, name))


def shotwin(name, title=PROF):
    p = os.path.join(d0.SHOTS, "%s_prof_%s_%s.png" % (d0.STAMP, TAG, name)); r = d0.gui("-Action", "shotwin", "-Title", "'%s'" % title, "-Out", "'%s'" % p)
    return p if os.path.isfile(p) else None


def ocr(png, rect=None):
    """[(text, cx, cy, x0, y0, y1)] in SCREEN coords; `rect` (l,t,r,b) crops the capture first (speed + fewer decoys)."""
    from PIL import Image
    im = Image.open(png); l, t = 0, 0
    if rect:
        l, t = max(0, rect[0]), max(0, rect[1]); im = im.crop((l, t, min(im.width, rect[2]), min(im.height, rect[3])))
    out = []
    for txt, conf, y0, y1, x0 in ocr_lines(im, scale=2):
        out.append((txt, l + x0 + 12, t + (y0 + y1) / 2.0, l + x0, t + y0, t + y1))
    return out


def find(png, rect, pat, why, lock=True):
    rows = ocr(png, rect); hit = next((r for r in rows if re.search(pat, r[0], re.I)), None)
    log("locate %-28s -> %s   (rows: %s)" % (why, hit and (hit[0], int(hit[1]), int(hit[2])), [r[0] for r in rows][:14]))
    if not hit and lock: LOCKED.append(why)            # lock=False: an OPTIONAL label (checkbox / unit) - recorded, not locking
    return hit


def click(x, y, why):
    log("CLICK (%d,%d) %s" % (x, y, why)); return d0.gui("-Action", "click", "-X", str(int(x)), "-Y", str(int(y)), "-Exception", "NegativeSearch", "-Evidence", "'%s'" % EVID)


def keys(s, why):
    log("KEYS %r %s" % (s, why)); return d0.gui("-Action", "keys", "-Key", "'%s'" % s, "-Exception", "NegativeSearch", "-Evidence", "'%s'" % EVID)


def esc(): d0.gui("-Action", "key", "-Key", "esc")


def activate(title):
    """`activate`, never `focus`: focus taps Esc, and the Profile window CLOSES on Esc (review c89-profiler-live §3); Esc in a
    Windows file dialog is Cancel (§2)."""
    out = d0.gui("-Action", "activate", "-Title", "'%s'" % title, "-Exception", "NegativeSearch", "-Evidence", "'%s'" % EVID); log("activate %s -> %s" % (title, out[:120])); return out


def box_dark(png, x0, cy):
    """dark fraction of the 12x12 interior of the checkbox predicted 4..22 px LEFT of a label's x0."""
    from PIL import Image
    im = Image.open(png).convert("L"); bx = int(x0) - 20; by = int(cy) - 6; n = d = 0
    for x in range(bx + 2, bx + 14):
        for y in range(by + 2, by + 14):
            if 0 <= x < im.width and 0 <= y < im.height:
                n += 1; d += im.getpixel((x, y)) < 110
    return round(d / max(n, 1), 3)


def open_profiler():
    """P-A..P-D. Returns True when the Profile window is listed."""
    d0.focus(d0.COPY_TITLE); time.sleep(0.8); esc(); time.sleep(0.5); pr = v5.panel_rect(); png = shot("pA")
    if not (pr and png): LOCKED.append("P-A panel rect/capture"); return False
    tools = find(png, (pr[0], pr[1], pr[0] + 700, pr[1] + 110), r"^Tools$", "P-B `Tools` menu label")
    if not tools: return False
    click(tools[1], tools[2], "Tools menu (P-B)"); time.sleep(1.2); png = shot("pB")
    prof = find(png, (int(tools[1]) - 60, int(tools[2]), int(tools[1]) + 360, int(tools[2]) + 700), r"^Profile", "P-C `Profile` row")
    if not prof: esc(); return False
    d0.gui("-Action", "move", "-X", str(int(prof[1])), "-Y", str(int(prof[2]))); time.sleep(1.2); png = shot("pC")
    pm = find(png, (int(prof[1]), int(prof[2]) - 60, int(prof[1]) + 620, int(prof[2]) + 420), r"Performance and Memory", "P-D `Performance and Memory...`")
    if not pm: esc(); esc(); return False
    click(pm[1], pm[2], "Performance and Memory... (P-D)")
    t0 = time.time()
    while time.time() - t0 < 10 and not d0.win_present(PROF): time.sleep(1)
    PF["PF1 Profile window listed <= 10 s"] = d0.win_present(PROF); return PF["PF1 Profile window listed <= 10 s"]


def checkbox(label, want_on, name):
    """P-E: crop-measured box state; click only when it differs from `want_on`; confirm by re-capture."""
    png = shotwin("chk_" + name); r = d0.win_rect(PROF)
    if not (png and r): LOCKED.append("P-E capture " + name); return None
    hit = find(png, None, label, "P-E `%s`" % name, lock=False)
    if not hit: return None
    # review c89-profiler-live §1: an EMPTY box reads 0.13 (border + glyph), so no absolute threshold decides the state.
    # State is decided by CHANGE: click once; if the dark fraction ROSE the box is now ON, if it FELL it was ON and is now OFF
    # (click again, require a rise). want_on=False boxes are never clicked (recorded only; A3/F3 say memory OFF).
    d_before = box_dark(png, hit[3], hit[2]); FACTS["chk_%s_before" % name] = d_before
    if not want_on: return True
    seq = [d_before]
    for i in range(2):
        click(r[0] + hit[3] - 12, r[1] + hit[2], "checkbox %s click %d" % (name, i + 1)); time.sleep(0.8)
        png2 = shotwin("chk%d_%s" % (i + 2, name)); d = box_dark(png2, hit[3], hit[2]) if png2 else None; seq.append(d)
        FACTS["chk_%s_seq" % name] = seq
        if d is None: return False
        if d > seq[-2] + 0.03: return True          # rose -> ON now
        if d < seq[-2] - 0.03: continue             # fell -> it WAS on; the second click turns it back ON
        return False                                # no visible change after a click -> the click did not land on the box
    return False


def setup_and_start():
    """P-E + P-F: Timing statistics ON, Timing details ON (A3), memory boxes OFF, Time unit -> us (A3), Start, COM liveness."""
    ok = True
    # OCR of the 2026 window (liveness run 1, diag_c89_profiler_live.log:13): labels carry a LEADING SPACE (' Timing details',
    # ' Profile memory usage'); the Time unit ring shows its VALUE as a word ('milliseconds'), beside the 'Size unit' ring ('kilobytes').
    for lab, want, nm in ((r"^\s*Timing statistics", True, "timing_stat"), (r"^\s*Timing details", True, "timing_det"),
                          (r"^\s*Profile memory usage", False, "prof_mem"), (r"^\s*Memory usage", False, "mem_usage")):
        res = checkbox(lab, want, nm); FACTS["chk_%s_ok" % nm] = res
        if want: PF["PF8 `%s` ON (A3)" % nm] = bool(res)
    png = shotwin("unit"); r = d0.win_rect(PROF)
    unit = find(png, None, r"^\s*(microseconds|milliseconds|seconds)\s*$", "Time unit ring value", lock=False) if png else None
    FACTS["time_unit_seen"] = unit and unit[0].strip()
    if unit and "milli" in unit[0].lower() and r:
        click(r[0] + unit[3] + 10, r[1] + unit[2], "Time unit ring (A3: -> microseconds)"); time.sleep(1.0); png = shot("unit_menu")
        us = find(png, (r[0] + unit[3] - 60, r[1] + unit[2] - 160, r[0] + unit[3] + 260, r[1] + unit[2] + 160), r"^\s*microseconds", "microseconds item", lock=False)
        if us: click(us[1], us[2], "microseconds (A3)"); time.sleep(0.8); png = shotwin("unit2"); u2 = find(png, None, r"^\s*(microseconds|milliseconds|seconds)\s*$", "Time unit after", lock=False); FACTS["time_unit_after"] = u2 and u2[0].strip()
        else: click(r[0] + unit[3] + 10, r[1] + unit[2], "Time unit ring again (closes an open dropdown on its current item; NEVER Esc here)"); time.sleep(0.8)
    png = shotwin("start"); r = d0.win_rect(PROF)
    if not (png and r): log("shotwin/rect of the Profile window failed: png=%s rect=%s windows=%s" % (png, r, d0.windows().splitlines()[:8])); LOCKED.append("P-F capture"); return False
    st = find(png, None, r"^\s*Start\s*$", "P-F `Start`")
    if not st: return False
    click(r[0] + st[3] + 12, r[1] + st[2], "Start profiling (P-F)"); time.sleep(1.5); png = shotwin("started")
    PF["PF2 Start -> `Stop` label visible"] = bool(png and find(png, None, r"^\s*Stop\s*$", "P-F `Stop` after Start"))
    try:
        t0 = time.time(); s = d0.com.call("state", timeout=10); d0.com.call("set", d0.C_STOP, False, timeout=10); v = d0.com.call("get", d0.C_STOP, timeout=10)
        PF["PF3 COM alive after Start"] = (v is False) and (time.time() - t0) < 10; FACTS["com_after_start"] = {"state": s, "stop": v, "s": round(time.time() - t0, 2)}
    except Exception as e:                                                     # noqa: BLE001
        PF["PF3 COM alive after Start"] = False; FACTS["com_after_start"] = repr(e)
    return ok and PF["PF2 Start -> `Stop` label visible"]


def snapshot_and_save(n):
    """P-G..P-J: focus the Profile window, Snapshot, Save to OUT/profile_<TAG>_<TS>_<n>.txt, verify the header."""
    activate(PROF); time.sleep(0.8)
    png = shotwin("pG%d" % n); r = d0.win_rect(PROF)
    if not (png and r): LOCKED.append("P-G"); return None
    sn = find(png, None, r"^\s*Snapshot\s*$", "P-H `Snapshot`")
    if not sn: return None
    click(r[0] + sn[3] + 12, r[1] + sn[2], "Snapshot #%d (P-H)" % n); time.sleep(2.0); png = shotwin("pH%d" % n)
    before = set(d0.windows().splitlines()); sv = find(png, None, r"^\s*Save\s*$", "P-I `Save`")
    if not sv: return None
    click(r[0] + sv[3] + 12, r[1] + sv[2], "Save #%d (P-I)" % n)
    t0 = time.time(); new = []
    while time.time() - t0 < 15 and not new: time.sleep(1); new = [w for w in d0.windows().splitlines() if w not in before]
    FACTS["save_dialog_%d" % n] = new
    if not new: LOCKED.append("P-I no dialog"); return None
    path = os.path.join(OUT, "profile_%s_%s_%d.txt" % (TAG, TS, n)); title = new[0].split("|")[-1].strip() if "|" in new[0] else new[0].strip()
    activate(title); time.sleep(0.8); keys("^a", "select name field"); time.sleep(0.4); keys(path, "profile path"); time.sleep(0.5); shot("pJ%d" % n); keys("{ENTER}", "confirm")
    for _ in range(16):
        time.sleep(1)
        if not d0.win_present(title): break
    else:
        shot("pJ%d_stuck" % n); activate(title); esc()      # Esc goes to the FILE DIALOG (activated first), never to the Profile window
    time.sleep(1.0); ok = os.path.isfile(path) and os.path.getsize(path) > 0
    head = open(path, "r", encoding="utf-8", errors="replace").readline() if ok else ""
    PF["PF4 table #%d saved, header has `VI Time`" % n] = ok and "VI Time" in head; FACTS["saved"].append({"n": n, "path": path, "header": head[:200]})
    return path if ok else None


def stop_profiler():
    png = shotwin("pK"); r = d0.win_rect(PROF)
    st = find(png, None, r"^\s*Stop\s*$", "P-K `Stop`", lock=False) if (png and r) else None
    if st: click(r[0] + st[3] + 12, r[1] + st[2], "Stop profiling (P-K)")


def table(path):
    rows = {}
    if not path: return rows
    hdr = None
    for ln in open(path, encoding="utf-8", errors="replace"):
        c = ln.rstrip("\n").split("\t")
        if hdr is None: hdr = c; continue
        if len(c) > 1 and c[0]: rows[c[0]] = dict(zip(hdr[1:], c[1:]))
    return rows


real_leg = v5.leg; real_save = d0.answer_save_dialog


def save_then_snapshot(tag, base_path):
    r = real_save(tag, base_path)
    FACTS["counters_L10"] = {"lost": v5.getv(d0.I_LOST), "frame": v5.getv(v5.I_FRAME)}; FACTS["table1"] = snapshot_and_save(1); return r


def profiled_leg(tag, n, base_path, cal_wait):
    if not open_profiler() or not setup_and_start():
        log("RECOVERY_LOCKED before Run: %s - leg NOT started" % LOCKED); return False
    d0.answer_save_dialog = save_then_snapshot
    ok = real_leg(tag, n, base_path, cal_wait)
    FACTS["counters_L12"] = {"lost": v5.getv(d0.I_LOST), "frame": v5.getv(v5.I_FRAME)}
    FACTS["table2"] = snapshot_and_save(2); stop_profiler()
    t2 = table(FACTS.get("table2")); t1 = table(FACTS.get("table1"))
    FACTS["rows_total"] = len(t2); FACTS["group_rows"] = {g: [k for k in t2 if g.lower() in k.lower()] for g in GROUPS}
    FACTS["missing_groups"] = [g for g, v in FACTS["group_rows"].items() if not v]
    PF["PF5 kernel row present in table #2"] = bool(FACTS["group_rows"]["Find xy center"] or FACTS["group_rows"]["Track xy"])
    diff = {}
    for k, v in t2.items():
        a = t1.get(k, {}); d = {}
        for col in ("VI Time", "Sub VIs Time", "Total Time", "# Runs"):
            try: d[col] = float(v.get(col, "nan")) - float(a.get(col, 0) or 0)
            except ValueError: d[col] = None
        d["Average_2"] = v.get("Average"); d["Display_2"] = v.get("Display"); d["Draw_2"] = v.get("Draw"); diff[k] = d
    FACTS["diff_L10_L12"] = diff
    return ok


if LIVE:
    d0.SHOTS = os.path.join(HERE, "m8_shots"); CD = drive_m8.CD
    copy = os.path.join(CD, "D1_s1_copy_live_%s.vi" % TS); shutil.copyfile(drive_m8.S1, copy)
    for m in (v5, v5.d4, d0): m.COPY = copy
    d0.COPY_TITLE = os.path.basename(copy); ok = False
    try:
        log(d0.com.call("app", timeout=240)); d0.com.call("open", copy, timeout=300); d0.com.call("panel", False, timeout=180)
        log("ExecState=%s" % v5.state())
        if open_profiler() and setup_and_start():
            p = snapshot_and_save(1); stop_profiler(); ok = bool(p)
            rows = table(p); FACTS["rows_total"] = len(rows); FACTS["row_sample"] = list(rows.items())[:5]
            if p: FACTS["file_head"] = open(p, encoding="utf-8", errors="replace").read(600)
        else:
            log("RECOVERY_LOCKED: %s" % LOCKED); shot("locked"); FACTS["dialogs"] = d0.dialogs()[-300:]
    finally:
        try: d0.com.call("closepanel", timeout=30)
        except Exception as e: log("closepanel %r" % e)                       # noqa: BLE001
        try: d0.com.call("release", timeout=10)
        except Exception: pass                                                 # noqa: BLE001
        import subprocess
        t0 = time.time()
        while v5.labview_running() and time.time() - t0 < 60: time.sleep(5)
        if v5.labview_running():
            subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"], capture_output=True); time.sleep(10)
        PF["PF6 LabVIEW gone"] = not v5.labview_running()
        try: os.remove(copy)
        except OSError as e: log("copy delete %r" % e)
        PF["PF7 live copy deleted, S1 md5 unchanged"] = (not os.path.exists(copy)) and drive_m8.md5(drive_m8.S1) == drive_m8.S1_MD5
else:
    v5.leg = profiled_leg
    ok = drive_m8.main()
    PF["PF6 LabVIEW gone"] = not v5.labview_running()
FACTS["locked"] = LOCKED
jp = os.path.join(HERE, "profile_89_%s_%s.json" % (TAG, TS)); json.dump({"pf": PF, "facts": FACTS, "ok": ok}, open(jp, "w"), indent=1, default=str)
for k, v in PF.items(): print("GATE %-50s %s" % (k, "PASS" if v else "FAIL"), flush=True)
bad = [k for k, v in PF.items() if not v] + ([] if ok else ["leg/liveness not ok"]) + (["RECOVERY_LOCKED"] if LOCKED else [])
print(P.result_line(P.make_result(len(PF) + (1 if ok else 0), len(bad), bad[0] if bad else None, [{"path": os.path.relpath(jp, ROOT), "md5": drive_m8.md5(jp)}])), flush=True)
sys.stdout.flush(); os._exit(0 if not bad else 1)
