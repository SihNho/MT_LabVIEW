r"""diag_c125_5_fsfind - card 125-5 STEP 1 pre-measurement (READ-ONLY): find a SMALL VI that already holds a Flat Sequence, to serve
as (a) the byte-copied scratch target of the 2,000-call hygiene probes of the two new ops (a big VI costs ~1 s of Open VI Reference
per op run, gscript.report_all docstring) and (b) a 1-frame FS donor for struct_copy_nested (the first frame; brief_125-5 STEP 1).
EXISTING FIRST: no FS donor exists (diag_c123_struct.log:47; claudeDev holds DonorCase/DonorSRInit/DonorPool/DonorRingConst only);
no New VI Object op for diagram structures (docs/toolkit-capabilities.md:121); report_all(cls='FlatSequence') works
(toolkit-capabilities.md:614) and report_all('Diagram') gives each diagram's owner CLASS ('FlatSequenceFrame' for an FS frame).
Candidates are only READ (report_all), never saved: claudeDev\NIScriptingExamples\**, vi.lib\Erdos Miller\LV-Scripting\*.vi,
claudeDev\Op*.vi / Donor*.vi. MEASUREMENT ONLY - per file: #FlatSequence, #FS-frame diagrams, #GObject; no count predicted.
Gates: R >= 1 candidate read without error; X LabVIEW gone. Result -> tools/bench/diag_c125_5_fsfind.json.
    py tools/bgrun.py --material --max-min 12 --log tools/bench/diag_c125_5_fsfind.log -- py -u tools/bench/diag_c125_5_fsfind.py"""
import glob, json, os, subprocess, sys, time, traceback                                     # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)  # noqa: E702
import protocol as P, gscript as g, bench_prep                                              # noqa: E401,E402
CD = g.CLAUDEDEV
EM = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting"
CANDS = (sorted(glob.glob(os.path.join(CD, "NIScriptingExamples", "**", "*.vi"), recursive=True))
         + sorted(glob.glob(os.path.join(EM, "*.vi")))
         + sorted(glob.glob(os.path.join(CD, "Donor*.vi"))) + sorted(glob.glob(os.path.join(CD, "Op*.vi"))))
DEADLINE = time.time() + 9 * 60
G, ROWS = {}, []


def gate(k, ok, d=""):
    G[k] = bool(ok); print("  %s  %s  %s" % ("PASS" if ok else "FAIL", k, str(d)[:800]), flush=True); return bool(ok)  # noqa: E702


try:
    bench_prep.restart_labview(); g.reset(); time.sleep(3)                                   # noqa: E702
    print("  FACT  %d candidate files" % len(CANDS), flush=True)
    for f in CANDS:
        if time.time() > DEADLINE:
            print("  FACT  STOP: time budget reached", flush=True)
            break
        r = {"file": f}
        try:
            fs = g.report_all(f, "FlatSequence")
            r["fs"] = [o["uid"] for o in fs]
            if fs:
                ds = g.report_all(f, "Diagram")
                r["fs_frames"] = sum(1 for o in ds if o["owner"] == "FlatSequenceFrame")
                r["gobjects"] = len(g.report_all(f, "GObject"))
                r["fs_owner"] = [o["owner"] for o in fs]
        except Exception as e:                                                               # noqa: BLE001
            r["err"] = str(e)[:160]
        ROWS.append(r)
        if r.get("fs"):
            print("  HIT   %s" % json.dumps(r), flush=True)
    hits = [r for r in ROWS if r.get("fs")]
    gate("R %d candidates read, %d without error" % (len(ROWS), sum(1 for r in ROWS if "err" not in r)),
         any("err" not in r for r in ROWS))
    best = sorted((r for r in hits if len(r["fs"]) == 1 and r.get("fs_frames") == 1), key=lambda r: r.get("gobjects", 1e9))
    print("  FACT  files with FS: %d; single 1-frame FS files (smallest first): %s" % (len(hits), [(os.path.basename(r["file"]), r["gobjects"]) for r in best][:8]), flush=True)
    json.dump({"rows": ROWS, "hits": hits, "best": best}, open(os.path.join(HERE, "diag_c125_5_fsfind.json"), "w", encoding="utf-8"), indent=1)
except Exception as e:                                                                       # noqa: BLE001
    traceback.print_exc(); gate("the run completed without an unhandled exception", False, repr(e)[:300])  # noqa: E702
finally:
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)  # noqa: E702
    gate("X LabVIEW gone", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower())
    bad = [k for k, v in G.items() if not v]
    print("=== GATES: %d pass / %d fail; failing: %s" % (len(G) - len(bad), len(bad), bad), flush=True)
    print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, [])), flush=True)
    sys.exit(1 if bad else 0)
