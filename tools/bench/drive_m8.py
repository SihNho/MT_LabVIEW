r"""drive_m8.py - M8 (a): one REAL RUN leg of a dated byte copy, driven by the D0 driver v5 (card 74-1).

FOUND FIRST: tools/bench/drive_original_copy_v5.py (the whole D0 leg: picks, done, bandpass, save dialog,
experiment loop, stop by the VI's own control, LabVIEW exit, post-run gate re-read) + d0_locate.py. This file is
the THIN WRAPPER of docs/m8-real-run-plan.md Pre-decided 1: v5 is imported and its module globals retargeted
(COPY/ORIGINAL/RUN_DIR/json paths) - v5 itself is NOT edited. Only its FIRST leg runs (plan: "full leg once").
    --leg bed   copy of claudeDev\D1_s4_loop17.vi (md5 4b621946...) -> claudeDev\D1_s4_loop17_run_<ts>.vi
    --leg base  copy of the bed's own source original `Min_Track N beads V6_ParallelLoop.vi` (2a78e17c...,
                tools/recipes/stage_d1_s1.py:226) -> claudeDev\m8_orig_copy_<ts>.vi
    --leg s3    card 74-4 (M8', plan PD 9): copy of claudeDev\D1_s3_loop15.vi (1a11d92a...) -> ..._run_<ts>.vi;
                --table --s3 merges bed+base+s3 -> tools/bench/m8s3_run.json (m8_run1.json left as it is)
    --dry       the whole path with COM/GUI/motor/process stubbed (P0); nothing reaches LabVIEW or a port
    --table     merge tools/bench/m8_bed.json + m8_base.json -> tools/bench/m8_run1.json
PREDICTION CONTRACT (M = this wrapper's gates; v5's own steps are printed too but are not these gates):
 M1 run copy md5 == source md5 before launch      M2 v5 leg reaches the experiment loop (L7+L8+L9 pass)
 M3 frames >= 2000 (tra header 'actual data points', else frame-counter delta)
 M4 stopped by the VI's own control (mechanism starts 'VI SERVER')   M5 cal* and tra* written, size > 0
 M6 LabVIEW gone (tasklist)   M7 bed md5 unchanged   M8 run copy deleted
"""
import json, os, re, shutil, subprocess, sys, tempfile, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                            # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
BED, BED_MD5 = os.path.join(CD, "D1_s4_loop17.vi"), "4b621946492da3d2fbb96b6053e715ec"
S3, S3_MD5 = os.path.join(CD, "D1_s3_loop15.vi"), "1a11d92aacabf7ec844d65b8af19f39f"   # card 74-4 (M8', plan PD 9)
ORIG = os.path.join(os.path.dirname(ROOT), "Min_Track N beads V6_ParallelLoop.vi")
ORIG_MD5 = "2a78e17c449cacdaf5da389818526859"
A = sys.argv[1:]; DRY = "--dry" in A; LEG = A[A.index("--leg") + 1] if "--leg" in A else None
TS = time.strftime("%Y%m%d_%H%M%S")

def md5(p):
    import hashlib; return hashlib.md5(open(p, "rb").read()).hexdigest()

def tra_rows(p, ncol=12):          # binary f64 rows after the text header: time,trans,rot + 3 beads x (x,y,z)
    b = open(p, "rb").read(); k = b.find(b"not in z!)")
    d = len(b) - (k + 10) if k >= 0 else None
    return {"data_bytes": d, "rows_f64x%d" % ncol: (d // (8 * ncol)) if d else 0, "rem": (d % (8 * ncol)) if d else None}

def lv_running():
    out = subprocess.run(["tasklist"], capture_output=True, text=True).stdout
    return "labview.exe" in out.lower()

def table(s3=False):
    ks = ("bed", "base", "s3") if s3 else ("bed", "base")
    legs = {("s3_loop15" if k == "s3" else k): json.load(open(os.path.join(HERE, "m8_%s.json" % k))) for k in ks}
    jp = os.path.join(HERE, "m8s3_run.json" if s3 else "m8_run1.json")
    json.dump({"schema": "m8-run1/1", "legs": legs}, open(jp, "w"), indent=1)
    print(P.result_line(P.make_result(1, 0, None, [{"path": os.path.relpath(jp, ROOT), "md5": md5(jp)}])))

def main():
    import drive_original_copy_v5 as v5
    d4, d0 = v5.d4, v5.d0
    src, smd5, name = {"bed": (BED, BED_MD5, "D1_s4_loop17_run_%s.vi"), "base": (ORIG, ORIG_MD5, "m8_orig_copy_%s.vi"),
                       "s3": (S3, S3_MD5, "D1_s3_loop15_run_%s.vi")}[LEG]
    name = name % TS
    copy = os.path.join(tempfile.gettempdir() if DRY else CD, name)
    shutil.copyfile(src, copy)
    G = {"M1 run copy md5 == source": md5(copy) == smd5 == md5(src)}
    run_dir = os.path.join(HERE, "m8_out", "%s_%s%s" % (LEG, TS, "_dry" if DRY else ""))
    for m in (v5, d4, d0):
        m.COPY, m.ORIGINAL, m.ORIGINAL_MD5, m.RUN_DIR = copy, ORIG, ORIG_MD5, run_dir
        m.SHOTS = os.path.join(HERE, "m8_shots")
    d0.COPY_TITLE = name; v5.EVID = os.path.join(HERE, "m8_shots")
    v5.D0_JSON = d0.D0_JSON = os.path.join(HERE, "m8_v5_%s%s.json" % (LEG, "_dry" if DRY else ""))
    v5.PROBE_JSON = os.path.join(HERE, "m8_v5_%s_clicks.json" % LEG)
    v5.RUN_S = 35.0                                           # ~84 Hz measured -> ~2900 frames (>= 2000)
    if DRY: import m8_dry; m8_dry.stub(v5, d4, d0)
    real_leg, n = v5.leg, [0]
    def one_leg(tag, *a):                                      # plan step 2: the full leg ONCE
        n[0] += 1
        return real_leg(tag, *a) if n[0] == 1 else True
    v5.leg = one_leg
    if not G["M1 run copy md5 == source"]:
        v5.rec("M1 REFUSED", "FILE", False, "copy md5 mismatch"); v5.report()
    else:
        v5.main()
    S = {s["step"].split(" ")[1] if " " in s["step"] else s["step"]: s["ok"] for s in d0.STEPS}
    F = d0.FACTS
    G["M2 reached experiment loop"] = all(S.get("run1.L%d" % i) for i in (7, 8, 9))
    files, hdr = {}, {}
    for f in sorted(os.listdir(run_dir)) if os.path.isdir(run_dir) else []:
        p = os.path.join(run_dir, f); files[f] = os.path.getsize(p)
        if f.lower().startswith("tra"):
            m = re.search(rb"actual data points/nominal: (\d+)/(\d+)", open(p, "rb").read(2000))
            hdr[f] = [int(m.group(1)), int(m.group(2))] if m else None
    fr = F.get("frames_run1") or []; num = [v for v in fr if isinstance(v, (int, float))]
    pts = max([h[0] for h in hdr.values() if h] or [0]); delta = (num[-1] - num[0]) if len(num) > 1 else 0
    G["M3 frames >= 2000"] = max(pts, delta) >= 2000
    l11 = [s["detail"] for s in d0.STEPS if "run1.L11" in s["step"]]
    m = re.search(r"\(lost=(.*?)\)$", l11[0]) if l11 else None; lost = m.group(1) if m else None
    stop = F.get("stop_run1") or {}
    G["M4 stopped by the VI's own control"] = str(stop.get("mechanism", "")).startswith("VI SERVER")
    G["M5 cal+tra written"] = any(f.lower().startswith("cal") and s > 0 for f, s in files.items()) and \
        any(f.lower().startswith("tra") and s > 0 for f, s in files.items())
    t0 = time.time()
    while not DRY and lv_running() and time.time() - t0 < 60: time.sleep(5)
    G["M6 LabVIEW gone (tasklist)"] = DRY or not lv_running()
    G["M7 bed md5 unchanged"] = md5(BED) == BED_MD5 and md5(S3) == S3_MD5 and md5(ORIG) == ORIG_MD5
    try: os.remove(copy)
    except OSError as e: print("delete copy failed: %r" % e)
    G["M8 run copy deleted"] = not os.path.exists(copy)
    out = {"leg": LEG, "dry": DRY, "copy": copy, "source": src, "source_md5": smd5, "run_dir": run_dir,
           "gates": G, "frame_counter_series": fr, "frame_counter_delta": delta, "tra_header_points": hdr,
           "total_lost_frames": lost, "stop": stop, "files": files,
           "v5_failing_steps": [k for k, v in S.items() if not v], "picks": F.get("picks_run1"),
           "bandpass": F.get("bandpass_run1"), "motor_after": (F.get("motor_after") or {}).get("tmx"),
           "handles": [F.get("handles_before"), F.get("handles_after")], "v5_json": v5.D0_JSON,
           "run_dir_stats": F.get("run_dir"), "tiffs_deleted": F.get("tiffs_deleted"),
           "tra_rows": {f: tra_rows(os.path.join(run_dir, f)) for f in files if f.lower().startswith("tra")}}
    json.dump(out, open(os.path.join(HERE, "m8_%s%s.json" % (LEG, "_dry" if DRY else "")), "w"), indent=1,
              default=str)
    for k, v in G.items(): print("GATE %-40s %s" % (k, "PASS" if v else "FAIL"))
    bad = [k for k, v in G.items() if not v]; jp = os.path.join(HERE, "m8_%s%s.json" % (LEG, "_dry" if DRY else ""))
    print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None,
                                      [{"path": os.path.relpath(jp, ROOT), "md5": md5(jp)}])), flush=True)
    return not bad

if __name__ == "__main__":
    if "--table" in A: table("--s3" in A); sys.exit(0)
    assert LEG in ("bed", "base", "s3"), "--leg bed|base|s3"
    ok = main(); sys.stdout.flush(); os._exit(0 if ok else 1)     # os._exit: v2's COM daemon threads
