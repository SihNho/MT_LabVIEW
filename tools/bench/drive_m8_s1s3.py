r"""drive_m8_s1s3.py - card 77-6: S1 vs S3 REAL-RUN legs at 3, 1, 6 bead picks (steer 77 / outcome review 2026-09-25).

FOUND FIRST: tools/bench/drive_m8.py (the M8 one-leg wrapper of drive_original_copy_v5.py, cycle 74, 8/0 on bed/base/s3).
This file only SEQUENCES it: each leg is `py -u tools/bench/drive_m8.py --leg s1|s3 --picks N` in its OWN process, which
makes a fresh dated byte copy, runs motor_gate --session start (PI reference + verify + limits readback), launches its
own LabVIEW, runs 35 s of experiment loop (same RUN_S as cycle 74), stops by the VI's own control, waits for LabVIEW
to exit (v5 G92), re-reads TMX, deletes the copy. drive_m8.py was extended (s1 leg, --picks, per-N output name).
Census (read-only, offline): S1 carries NO fixture TIFF writer - wiki of D1_s1_copy.vi md5 3e3d23ce (docs/wiki/index.json:1887)
has 0 hits for uid 22700/23020/TIFF (tools/bench/m8b_facts_74.log:8-10); the per-leg TIFF count re-measures it.
PREDICTION CONTRACT (per leg; T = this sequencer's gates):
 T1 leg rc == 0 (drive_m8 M1..M8 all pass; M2 = L7+L9+L11 when --picks given)
 T2 LabVIEW not running before the next leg starts      T3 0 TIFFs in S1 and S3 legs (no fixture writer)
 Order s1@3, s3@3, s1@1, s3@1, s1@6, s3@6; a leg is not STARTED after HARD_MIN (card hard stop 55 min).
"""
import json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                            # noqa: E402
LEGS = [("s1", 3), ("s3", 3), ("s1", 1), ("s3", 1), ("s1", 6), ("s3", 6)]
HARD_MIN, LEG_MAX_MIN = 55.0, 7.0          # do not start a leg that could run past the hard stop
T0 = time.time()

def lv_running():
    return "labview.exe" in subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()

def md5(p):
    import hashlib; return hashlib.md5(open(p, "rb").read()).hexdigest()

rows, gates = [], {}
for leg, n in LEGS:
    tag = "%s@%d" % (leg, n); el = (time.time() - T0) / 60
    if el + LEG_MAX_MIN > HARD_MIN:
        print("SKIP %s: elapsed %.1f min + %.0f > hard stop %.0f" % (tag, el, LEG_MAX_MIN, HARD_MIN), flush=True)
        rows.append({"leg": tag, "skipped": "hard stop"}); continue
    gates["T2 %s LabVIEW gone before start" % tag] = not lv_running()
    print("=== LEG %s start at %.1f min ===" % (tag, el), flush=True)
    t = time.time()
    r = subprocess.run([sys.executable, "-u", os.path.join(HERE, "drive_m8.py"), "--leg", leg, "--picks", str(n)],
                       capture_output=True, text=True, timeout=LEG_MAX_MIN * 60 + 120)
    out = r.stdout or ""
    for ln in out.splitlines():
        if ln.startswith(("GATE ", "RESULT ", "|")) or "FAILING" in ln or "=== D0" in ln: print("  " + ln[:300], flush=True)
    if r.stderr: print("  STDERR tail: " + r.stderr[-800:], flush=True)
    jp = os.path.join(HERE, "m8_%s_p%d.json" % (leg, n))
    j = json.load(open(jp)) if os.path.isfile(jp) and os.path.getmtime(jp) >= t else {}
    hdr = j.get("tra_header_points") or {}
    row = {"leg": tag, "rc": r.returncode, "secs": round(time.time() - t), "json": os.path.relpath(jp, ROOT) if j else None,
           "reached_experiment_loop": (j.get("gates") or {}).get("M2 reached experiment loop"),
           "frames_delta": j.get("frame_counter_delta"), "lost_frames": j.get("total_lost_frames"),
           "tra_rows_header": {k: (v[0] if v else None) for k, v in hdr.items()}, "tra_rows_bytes": j.get("tra_rows"),
           "tiffs": (j.get("tiffs_deleted") or {}).get("count"), "stop_latency_s": (j.get("stop") or {}).get("latency_s"),
           "stop_mechanism": (j.get("stop") or {}).get("mechanism"),
           "labview_exited": (j.get("gates") or {}).get("M6 LabVIEW gone (tasklist)"),
           "picks": j.get("picks"), "bandpass": j.get("bandpass"), "motor_tmx_after": j.get("motor_after"),
           "gates": j.get("gates"), "v5_failing": j.get("v5_failing_steps")}
    rows.append(row); print("ROW " + json.dumps(row, default=str)[:900], flush=True)
    gates["T1 %s leg rc 0" % tag] = r.returncode == 0
    gates["T3 %s 0 TIFFs" % tag] = row["tiffs"] == 0
    t2 = time.time()
    while lv_running() and time.time() - t2 < 90: time.sleep(5)
out = {"schema": "m8-s1s3/1", "card": "77-6", "run_s": 35.0, "rows": rows, "gates": gates,
       "census_s1_tiff_writer": "absent (wiki md5 3e3d23ce, tools/bench/m8b_facts_74.log:8-10)",
       "lv_running_at_end": lv_running(), "minutes": round((time.time() - T0) / 60, 1)}
jp = os.path.join(HERE, "m8_s1s3_77.json"); json.dump(out, open(jp, "w"), indent=1, default=str)
for k, v in gates.items(): print("GATE %-45s %s" % (k, "PASS" if v else "FAIL"), flush=True)
bad = [k for k, v in gates.items() if not v]
print(P.result_line(P.make_result(len(gates) - len(bad), len(bad), bad[0] if bad else None,
                                  [{"path": os.path.relpath(jp, ROOT), "md5": md5(jp)}])), flush=True)
sys.exit(1 if bad else 0)
