r"""diag_c92_unstamped_leg.py - card 92-1 M2 (PD198(c)(2)): ONE real leg of the UNSTAMPED S1 copy D1_s1_copy.vi through
drive_m8 `replay_s1 --src` (fresh dated run copy beside it, v5 L1..L13 with the bead-pick GUI, own motor-gate session, stop
by the VI's own control, LabVIEW gone, TMX re-read), panel NORMAL (nothing minimized, no FPState write).
FOUND FIRST: diag_c91_step4_leg.py (the same leg for the STAMPED copy: MinCom minimize + K2/K3 stamp-file gates - both
inapplicable here, so they are dropped, nothing else changes); drive_m8_panelmin89_leg.py (hard-codes --leg s1).
NEW (both reads, no GUI act): the capture-holding window's CLASS/title/pid for every pick click, read with
GetClassNameW on the hwndCapture that lv_gui's clickprobe recorded in `gti_before_click` (review c91-step4-t12 §4 test 2,
the READ half only; the release half is a harness change that judgement has not taken).
    py -u tools/bench/diag_c92_unstamped_leg.py --src <vi> --picks N --run-s 120 --out <dir>
PREDICTION CONTRACT (GATE lines; drive_m8 M1..M8 stand unchanged): U1 the leg reached L9 (clicks recorded);
 U2 tra rows exact for N (the exact tra rule, review c91-step4-t12 s1) - reported, the SEQUENCER decides the rerun.
Registered picks = the tra row width: (bytes-8) == rows*(24+24N)."""
import ctypes as C, glob, json, os, re, shutil, struct, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                            # noqa: E402
A = sys.argv[1:]
SRC = os.path.normpath(A[A.index("--src") + 1]); OUT = os.path.normpath(A[A.index("--out") + 1])
NPICK = int(A[A.index("--picks") + 1]); RUN_S = A[A.index("--run-s") + 1] if "--run-s" in A else "120"
os.makedirs(OUT, exist_ok=True)
print("[c92 leg ctl] src %s picks %d run-s %s out %s" % (SRC, NPICK, RUN_S, OUT), flush=True)
import bench_prep                                                               # noqa: E402
bench_prep.restart_labview()
sys.argv = [sys.argv[0], "--leg", "replay_s1", "--src", SRC, "--picks", str(NPICK), "--run-s", RUN_S]
import drive_m8                                                                 # noqa: E402  (argv parsed here)
import drive_original_copy_v5 as v5                                             # noqa: E402
d4 = v5.d4
PM, FACTS = {}, {"mode": "ctl", "picks_target": NPICK, "clicks": []}
U32 = C.windll.user32


def win_class(h):
    """class / title / pid / alive of an HWND, by ctypes (a read; no GUI act)."""
    try:
        h = int(h)
        if not h: return None
        alive = bool(U32.IsWindow(C.c_void_p(h)))
        b = C.create_unicode_buffer(256); U32.GetClassNameW(C.c_void_p(h), b, 256)
        t = C.create_unicode_buffer(512); U32.GetWindowTextW(C.c_void_p(h), t, 512)
        pid = C.c_ulong(0); tid = U32.GetWindowThreadProcessId(C.c_void_p(h), C.byref(pid))
        return {"hwnd": h, "alive": alive, "class": b.value, "title": t.value, "pid": pid.value, "tid": tid}
    except Exception as e:                                                     # noqa: BLE001
        return {"hwnd": h, "err": repr(e)}


real_probe = d4.clickprobe


def probe_with_class(title, x, y, why):
    j = real_probe(title, x, y, why)          # drive_original_copy_v4.clickprobe returns the dict only (v4:447-465)
    rec = {"why": why[:80], "t": time.time()}
    try:
        for key in ("gti_before_focus", "gti_before_click", "gti_after_click"):
            g = (j or {}).get(key) or {}
            cap = g.get("hwndCapture", 0)
            rec[key] = {"hwndCapture": cap, "capture_win": win_class(cap) if cap else None, "hwndFocus": g.get("hwndFocus")}
        rec["target_hwnd"] = (j or {}).get("target", {}).get("hwnd")
    except Exception as e:                                                     # noqa: BLE001
        rec["err"] = repr(e)
    FACTS["clicks"].append(rec)
    print("[c92 leg ctl] CLICK %s: capture before-click %s" % (rec["why"], json.dumps(rec.get("gti_before_click"))), flush=True)
    return j


d4.clickprobe = probe_with_class

T_START = time.time()
ok = drive_m8.main()
m8p = os.path.join(HERE, "m8_replay_s1_p%d_r%d.json" % (NPICK, int(float(RUN_S))))
# review c92-unstamped-clickprobe 'Minor': the shared m8 json must be FRESH (it held cycle-91 data before this leg)
m8 = json.load(open(m8p)) if os.path.isfile(m8p) and os.path.getmtime(m8p) >= T_START else {}
FACTS["m8_json_fresh"] = bool(m8)
reg = None; tra = {}
for f, s in (m8.get("files") or {}).items():
    if f.lower().startswith("tra"):
        p = os.path.join(m8.get("run_dir", ""), f)
        try:
            b = open(p, "rb").read(); k = b.find(b"not in z!)"); d = len(b) - (k + 10)
            mm = re.search(rb"actual data points/nominal: (\d+)/(\d+)", b[:2000]); rows = int(mm.group(1)) if mm else 0
            pre = b[k + 10:k + 18]; dims = {"be": struct.unpack(">ii", pre), "le": struct.unpack("<ii", pre)} if len(pre) == 8 else None
            n_exact = (((d - 8) / rows) - 24) / 24 if rows else None
            exact = bool(rows) and (d - 8) == rows * (24 + 24 * NPICK)
            tra[f] = {"data_bytes": d, "rows_hdr": rows, "bytes_per_row": (d / rows) if rows else None, "n_beads": ((d / rows) - 24) / 24 if rows else None,
                      "n_beads_exact": n_exact, "exact_for_target": exact, "leftover_bytes": (d - 8) - rows * (24 + 24 * NPICK) if rows else None, "dims_prefix": dims}
            if n_exact is not None: reg = n_exact
        except Exception as e:                                                 # noqa: BLE001
            tra[f] = "ERR %r" % e
cal_n = None
for f, s in (m8.get("files") or {}).items():
    if f.lower().startswith("cal"): cal_n = (s - 96) / 57152.0
caps = []
try:
    cp = os.path.join(HERE, "m8_v5_replay_s1_p%d_r%d_clicks.json" % (NPICK, int(float(RUN_S))))
    if os.path.isfile(cp):
        shutil.copyfile(cp, os.path.join(OUT, "clicks.json"))
        caps = re.findall(r'"hwndCapture":\s*(\d+)', open(cp, encoding="utf-8", errors="replace").read())
except Exception as e:                                                         # noqa: BLE001
    caps = ["ERR %r" % e]
first = next((c for c in FACTS["clicks"] if "pick" in c["why"].lower() or "bead" in c["why"].lower()), FACTS["clicks"][0] if FACTS["clicks"] else None)
FACTS.update({"picks_registered_cal": cal_n, "hwndCapture_seq": caps, "foreign_capture_nonzero": [c for c in caps if c not in ("0",)],
              "first_click": first, "tra": tra, "picks_registered_tra": reg, "bandpass_answered": (m8.get("bandpass") or {}).get("answered"),
              "picks_markers": m8.get("picks"), "lost": m8.get("total_lost_frames"), "frames_delta": m8.get("frame_counter_delta"),
              "tra_header_points": m8.get("tra_header_points"), "motor_tmx_after": m8.get("motor_after"), "m8_gates": m8.get("gates"),
              "v5_failing": m8.get("v5_failing_steps"), "stop": m8.get("stop"), "run_dir": m8.get("run_dir"), "source_md5": m8.get("source_md5")})
PM["U1 leg reached the pick clicks (>=1 click recorded)"] = len(FACTS["clicks"]) >= 1
PM["U2 tra rows exact for target N (reported; sequencer decides the rerun)"] = any(isinstance(t, dict) and t.get("exact_for_target") for t in tra.values())
print("REGISTERED picks target=%d tra=%r cal=%r bandpass_answered=%r lost=%r hwndCapture=%s" % (NPICK, reg, cal_n, FACTS["bandpass_answered"], FACTS["lost"], caps), flush=True)
print("FIRST CLICK %s" % json.dumps(first, default=str), flush=True)
jp = os.path.join(OUT, "leg.json")
json.dump({"pm": PM, "facts": FACTS, "drive_m8_ok": ok, "m8": m8}, open(jp, "w"), indent=1, default=str)
for k, v in PM.items(): print("GATE %-52s %s" % (k, "PASS" if v else "FAIL"), flush=True)
bad = [k for k, v in PM.items() if not v and not k.startswith("U2")] + ([] if ok else ["drive_m8 M-gates"])
print(P.result_line(P.make_result(len(PM) + (1 if ok else 0), len(bad), bad[0] if bad else None,
                                  [{"path": os.path.relpath(jp, ROOT), "md5": drive_m8.md5(jp)}])), flush=True)
sys.stdout.flush(); os._exit(0 if not bad else 1)
