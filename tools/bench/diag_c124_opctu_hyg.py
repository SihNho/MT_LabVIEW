r"""diag_c124_opctu_hyg - card 124-5 decision 1 (brief_124-5.md): the hygiene record of the SAVED claudeDev\OpConnectTermUid_v0.vi
(md5 34120e63..., built by card 124-4, NOT rebuilt here). EXISTING FIRST: the workload and the record format are 124-4's own
hygiene() (diag_c124_opconnecttermuid.py:99-132, never reached: it called g.op outside the probe, r2.log:37-45); the ONE exemption
is gscript.hygiene_probe (gscript.py:239-249), so every call here runs INSIDE `with g.hygiene_probe(OP):`. Criterion:
docs/violation-decisions.md 2026-09-28 10:37 (1) + PD242(b) (op_hygiene/OpConstInd_v0.json): >= 2,000 calls, 0 errors, handles +-100.
PREDICTION: K op md5 == 34120e63 / F1 an already-connected (sink, source) pair on a never-saved byte copy of OpPrimDonor_v0.vi ->
echoes == uids, UID 2 == that wire, Is Broken? False, wires +0 / H 2,000 calls, 0 errors, handles flat +-100, wires +0 / K2 op md5
unchanged after / X scratch deleted, LabVIEW gone. Invoke delta on the scratch is recorded as a FACT (not a criterion).
    py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c124_opctu_hyg.log -- py -u tools/bench/diag_c124_opctu_hyg.py"""
import hashlib, json, os, shutil, subprocess, sys, time, traceback                          # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, HERE)                    # noqa: E702
import protocol as P                                                                        # noqa: E402
import gscript as g                                                                         # noqa: E402
import bench_prep                                                                           # noqa: E402
import allterms                                                                             # noqa: E402
KEY, PIN = "OpConnectTermUid_v0", "34120e6314dc44522dee07dcb04ea55a"
OP = os.path.join(g.CLAUDEDEV, KEY + ".vi")
LAB = json.load(open(os.path.join(HERE, "opconnecttermuid_v0_labels.json"), encoding="utf-8"))[KEY]
HYG_P = os.path.join(HERE, "op_hygiene", KEY + ".json")
SCR = os.path.join(g.CLAUDEDEV, "scratch_c124_hyg_%s.vi" % time.strftime("%Y%m%d_%H%M%S"))
N_CALLS, G = 2000, {}
g._run.__defaults__ = (6.0, 120.0)


def md5(p): return hashlib.md5(open(p, "rb").read()).hexdigest()
def gate(k, ok, d=""):
    G[k] = bool(ok); print("%s  %s  %s" % ("PASS" if ok else "FAIL", k, str(d)[:600]), flush=True); return bool(ok)   # noqa: E702
def fact(k, v): print("FACT  %s: %s" % (k, str(v)[:900]), flush=True)                       # noqa: E704


def call(ti, src_uid):
    vi = g.op(OP)
    vi.SetControlValue(LAB["vi_path"], SCR); vi.SetControlValue(LAB["class_name"], "Terminal")   # noqa: E702
    vi.SetControlValue(LAB["index"], int(ti)); vi.SetControlValue(LAB["src_uid"], int(src_uid))  # noqa: E702
    g._run(vi)
    return dict((k, vi.GetControlValue(LAB[k])) for k in ("sink_echo", "src_echo", "wire_uid", "broken")), g._err(vi, LAB["Err"]) or ""


def hygiene():
    shutil.copyfile(os.path.join(g.CLAUDEDEV, "OpPrimDonor_v0.vi"), SCR); time.sleep(0.3)   # noqa: E702
    g.ensure_loaded(SCR)
    rows, _dt = allterms.read_terms(SCR, allterms.OP_ALLTERMS_V1)
    by = {}
    for r in rows:
        if r["wire_uid"]:
            by.setdefault(r["wire_uid"], []).append(r)
    w, pair = next((w, p) for w, p in sorted(by.items()) if len(p) == 2 and sum(x["is_source"] for x in p) == 1)
    snk, src = next(x for x in pair if not x["is_source"]), next(x for x in pair if x["is_source"])
    ti = g._uid_index(SCR, "Terminal", snk["term_uid"])
    wc0, iv0 = len(g.uids(SCR, "Wire")), set(g.uids(SCR, "Invoke"))
    r1, e1 = call(ti, src["term_uid"])
    fact("F1 pair w%s sink #%s (Traverse %s) <- source #%s" % (w, snk["term_uid"], ti, src["term_uid"]), (r1, e1))
    if not gate("F1 first call: echoes, UID 2 == w%s, Broken? False, wires +0" % w, not e1 and int(r1["sink_echo"]) == snk["term_uid"]
                and int(r1["src_echo"]) == src["term_uid"] and int(r1["wire_uid"]) == w and r1["broken"] is False
                and len(g.uids(SCR, "Wire")) == wc0, (r1, e1, len(g.uids(SCR, "Wire")), wc0)):
        return
    fact("F1 Invoke delta on the scratch", sorted(set(g.uids(SCR, "Invoke")) - iv0))
    h0, hs, errs, codes, t0 = bench_prep.labview_handles(), [], 0, [], time.time()
    for k in range(N_CALLS):
        _r, e = call(ti, src["term_uid"])
        if e:
            errs += 1; codes.append(str(e)[:80])                                             # noqa: E702
        if k % 100 == 99:
            hs.append(bench_prep.labview_handles())
    h1, wc1, iv1 = bench_prep.labview_handles(), len(g.uids(SCR, "Wire")), set(g.uids(SCR, "Invoke"))
    fact("H timing", "%.1f s for %d calls" % (time.time() - t0, N_CALLS))
    fact("H Invoke delta on the scratch after %d calls" % (N_CALLS + 1), len(iv1 - iv0))
    ok = errs == 0 and abs(h1 - h0) <= 100 and wc1 == wc0
    gate("H %d calls, 0 errors, handles flat +-100, wires +0" % N_CALLS, ok, (errs, h0, h1, wc1, wc0, hs))
    json.dump({"schema": "op-hygiene/1", "op": KEY, "path": OP, "md5": md5(OP), "status": "PASS" if ok else "FAIL", "calls": N_CALLS,
               "errors": errs, "error_codes": sorted(set(codes)), "handles_before": h0, "handles_after": h1, "handles_per_round": hs,
               "invoke_delta_on_target": len(iv1 - iv0),
               "workload": "1 first call + %d idempotent re-connects of w%s (sink #%s <- source #%s) on a never-saved byte copy of "
                           "OpPrimDonor_v0.vi, inside gscript.hygiene_probe" % (N_CALLS, w, snk["term_uid"], src["term_uid"]),
               "criterion": "docs/violation-decisions.md 2026-09-28 10:37 (1) + PD242(b): >= 2,000 consecutive calls, 0 errors, handles flat +-100",
               "card": "124-5", "log": "tools/bench/diag_c124_opctu_hyg.log", "build_log": "tools/bench/diag_c124_opconnecttermuid_r2.log"},
              open(HYG_P, "w", encoding="utf-8"), indent=1)
    fact("RECORD", HYG_P)


try:
    if gate("K op md5 == %s (saved by 124-4, not rebuilt)" % PIN[:8], md5(OP) == PIN, md5(OP)):
        bench_prep.restart_labview(); g.reset(); time.sleep(3)                              # noqa: E702
        fact("handles after restart", bench_prep.labview_handles())
        with g.hygiene_probe(OP):
            hygiene()
        gate("K2 op md5 unchanged after the probe", md5(OP) == PIN, md5(OP))
except Exception as e:                                                                      # noqa: BLE001
    traceback.print_exc(); gate("the run completed without an unhandled exception", False, repr(e)[:300])  # noqa: E702
finally:
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)  # noqa: E702
    gate("X LabVIEW gone", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower())
    for _k in range(5):
        if os.path.exists(SCR):
            try:
                os.remove(SCR)
            except OSError:
                time.sleep(2)
    gate("X scratch deleted", not os.path.exists(SCR), SCR)
    bad = [k for k, v in G.items() if not v]
    arts = [{"path": p, "md5": md5(p)} for p in (OP, HYG_P) if os.path.exists(p) and not bad]
    print("=== GATES: %d pass / %d fail; failing: %s" % (len(G) - len(bad), len(bad), bad), flush=True)
    print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, arts)), flush=True)
    sys.exit(1 if bad else 0)
