r"""diag_c117a_hyg - card 117-1 S0b/S0d: the op-hygiene proof of claudeDev\OpWireJoints_v1.vi (built by diag_c117a_opv1.py) through
gscript.wire_joints (now bound to v1; v0 is never called here), on ONE fresh dated BYTE COPY claudeDev\scratch_c117_bed_<ts>.vi of the R1 bed
(1,945 wires; the file whose 536-read v0 sweep died with error 1055 / error 2, review c116d-sweep). READ-ONLY on the copy; nothing saved; no VI run
except the op. Wire order = ONE report_all(Wire) (index passed, review c116d-sweep section 5).
PHASES: W 1 warm call (the op's first load); H20 20 calls on wire index 0; SW all 1,945 wires once; P2 the first 100 wires again
(total 2,066 op calls >= 2,000). Handles + LabVIEW private bytes sampled every 250 calls.
PREDICTION: every read echoes its uid with err '' (0 errors); H20 handles flat +-100; handles flat +-100 from after H20 to the end; P2 raws ==
SW raws; report_all(GObject) after the sweep answers (v0's run hit error 2 there); scratch deleted; R1 md5 unchanged; LabVIEW gone.
S0d REPORT-ONLY (PD233(b), never a gate): wires with a LOOSE joint (flags & 0x100, diag_c116d_decode.py:3-5) vs the 23 of diag_c116d_decode.log:41.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c117a_hyg.log -- py -u tools/bench/diag_c117a_hyg.py"""
import hashlib, json, os, shutil, subprocess, sys, time, traceback                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)  # noqa: E702
import protocol as P, gscript as g, bench_prep                                            # noqa: E401,E402
R1, R1_MD5 = os.path.join(g.CLAUDEDEV, "D1_l2_r1_20260928_055441.vi"), "f465196bb5016638b146e771ba54c5af"
OP = os.path.join(g.CLAUDEDEV, "OpWireJoints_v1.vi")
TS = time.strftime("%Y%m%d_%H%M%S"); SCR = os.path.join(g.CLAUDEDEV, "scratch_c117_bed_%s.vi" % TS)   # noqa: E702
FOUND23 = [10187, 11253, 11389, 12256, 1773, 25438, 25461, 28338, 29122, 29787, 3040, 3512, 3646, 373, 3912, 4027, 42, 4878, 5746, 5979, 628, 8590, 9051]
G, OUT, RAW = {}, {"ts": TS, "op": OP}, {}
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                             # noqa: E731


def gate(k, ok, d=""):
    G[k] = bool(ok); print("  %s  %s  %s" % ("PASS" if ok else "FAIL", k, str(d)[:600]), flush=True); return bool(ok)  # noqa: E702


def pbytes():
    r = subprocess.run(["powershell", "-NoProfile", "-Command", "(Get-Process LabVIEW -ErrorAction SilentlyContinue | Select-Object -First 1).PrivateMemorySize64"],
                       capture_output=True, text=True, timeout=60)
    try:
        return round(int(r.stdout.strip() or 0) / 1048576.0, 1)
    except ValueError:
        return None


CALLS, ERRS, SAMPLES = [0], [], []


def call(t, uid, i, tag):
    try:
        r = g.wire_joints(t, uid, index=i)
    except Exception as e:                                                                  # noqa: BLE001
        r = {"echo": 0, "joints": None, "err": "EXC " + repr(e)[:200]}
    CALLS[0] += 1
    if r["err"] or r["echo"] != int(uid):
        ERRS.append((CALLS[0], tag, uid, r["err"][:200]))
    if CALLS[0] % 250 == 0:
        SAMPLES.append((CALLS[0], bench_prep.labview_handles(), pbytes())); print("  FACT  sample calls/handles/privMB %r" % (SAMPLES[-1],), flush=True)  # noqa: E702
    return r


try:
    gate("K R1 md5 pinned; op v1 on disk", md5(R1) == R1_MD5 and os.path.exists(OP), (md5(R1), md5(OP) if os.path.exists(OP) else None))
    OUT["op_md5"] = md5(OP)
    shutil.copyfile(R1, SCR)
    bench_prep.restart_labview(); g.reset(); time.sleep(3)                                   # noqa: E702
    order = [int(o["uid"]) for o in g.report_all(SCR, "Wire")]
    print("  FACT  wires %d; handles %s privMB %s after load" % (len(order), bench_prep.labview_handles(), pbytes()), flush=True)
    call(SCR, order[0], 0, "W")
    hw, mw = bench_prep.labview_handles(), pbytes()
    for _k in range(20):
        call(SCR, order[0], 0, "H20")
    h20, m20 = bench_prep.labview_handles(), pbytes()
    gate("H20 20 calls: 0 errors, handles flat +-100 (after the warm call)", not ERRS and abs(h20 - hw) <= 100, (hw, h20, mw, m20, ERRS[:5]))
    t0 = time.time()
    for i, u in enumerate(order):
        RAW[str(u)] = call(SCR, u, i, "SW")
    print("  FACT  sweep %d reads in %.1f s" % (len(order), time.time() - t0), flush=True)
    rep = [str(order[i]) for i in range(min(100, len(order))) if call(SCR, order[i], i, "P2")["joints"] != RAW[str(order[i])]["joints"]]
    h1, m1 = bench_prep.labview_handles(), pbytes()
    gate("SW all %d wires + P2 100 re-reads: 0 errors (%d calls total)" % (len(order), CALLS[0]), not ERRS and CALLS[0] >= 2000, (CALLS[0], len(ERRS), ERRS[:5]))
    gate("HF handles flat +-100 from after H20 to the end", abs(h1 - h20) <= 100, (h20, h1, m20, m1))
    gate("P2 re-reads == sweep raws (100 wires)", not rep, rep[:10])
    try:
        n_go = len(g.report_all(SCR, "GObject")); ok = n_go > 0                              # noqa: E702
    except Exception as e:                                                                  # noqa: BLE001
        n_go, ok = repr(e)[:200], False
    gate("RA report_all(GObject) answers after the sweep (v0 hit error 2 here)", ok, n_go)
    loose = sorted(int(w) for w, r in RAW.items() if r["joints"] and any(int(j[1]) & 0x100 for j in r["joints"]))
    print("  FACT  S0d REPORT-ONLY: %d wires carry a LOOSE joint (R1 Error List loose-ends 24); not among the 23 of decode.log:41: %r; of the 23 not loose now: %r"
          % (len(loose), sorted(set(loose) - set(FOUND23)), sorted(set(FOUND23) - set(loose))), flush=True)
    for w in sorted(set(loose) - set(FOUND23)):
        print("  FACT  S0d w%s joints %s" % (w, json.dumps(RAW[str(w)]["joints"], default=str)[:600]), flush=True)
    OUT.update(calls=CALLS[0], errors=len(ERRS), error_list=ERRS[:50], handles=[hw, h20, h1], priv_mb=[mw, m20, m1], samples=SAMPLES, loose=loose,
               loose_new=sorted(set(loose) - set(FOUND23)), wires=len(order))
    json.dump(RAW, open(os.path.join(HERE, "diag_c117a_sweep_raw.json"), "w", encoding="utf-8"), default=str)
except Exception as e:                                                                       # noqa: BLE001
    traceback.print_exc(); gate("the run completed without an unhandled exception", False, repr(e)[:300])  # noqa: E702
finally:
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)  # noqa: E702
    for _i in range(5):
        try:
            os.path.exists(SCR) and os.remove(SCR); break                                    # noqa: E702
        except OSError:
            time.sleep(3)
    gate("H LabVIEW gone; scratch deleted; R1 md5 unchanged", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
         and not os.path.exists(SCR) and md5(R1) == R1_MD5)
    OUT["gates"] = G
    json.dump(OUT, open(os.path.join(HERE, "diag_c117a_hyg.json"), "w", encoding="utf-8"), indent=1, default=str)
    bad = [k for k, v in G.items() if not v]
    print("=== GATES: %d pass / %d fail; failing: %s" % (len(G) - len(bad), len(bad), bad), flush=True)
    print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, [{"path": "tools/bench/diag_c117a_hyg.json", "md5": md5(os.path.join(HERE, "diag_c117a_hyg.json"))}])), flush=True)
    sys.exit(1 if bad else 0)
