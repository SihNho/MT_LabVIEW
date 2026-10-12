# ---
# labview: read
# hardware: motor
# offline-args: --selftest
# evidence: tools/bench/m8_legs.py:131
# ---
r"""m8_legs - the M8 replay-leg runner shared by the leg-chain drivers (card 170-a3-3; docs/script-writing.md rule 4).
leg() is MOVED from tools/bench/drive_m8_replay_110.py:33-59 (VISA precheck, diag_c104_leg.py, one rerun, LabVIEW-gone wait +
taskkill, leg.json facts). That file stays byte-unchanged (the record of what ran, card 110-7). Changes in the move: its globals
(G, rows, NPICK, RUN_S, LEGDIR) are parameters; the precheck, the leg subprocess and the LabVIEW test are injectable for the
offline self-test; the LabVIEW test and kill are drive_legguard.lv_running / kill_labview (110's :26 lambda is a copy of
drive_legguard.py:45-46, its :48 taskkill a copy of :51); the row also carries frames_delta (leg.json facts.frames_delta).
New: motor_session() = `py tools/motor_gate.py --session start|end`, its readback re-checked with motor_gate's own parsers and
checkers; keep_leg_files() keeps the leg's m8 jsons (shared names, overwritten by the next leg) in the leg's --out dir.
FOUND FIRST: drive_original_copy_v4.py:205-218 motor_gate(why) runs --session start only, and :221 parse_motor; v4 imports
drive_original_copy_v2 (a LabVIEW client), so neither is importable offline - motor_gate.parse_*/check_* are CALLED instead.
    py -u tools/bench/m8_legs.py --selftest      (offline: recorded motor_gate logs + the stored 110-7 leg.json files)"""
import glob, json, os, shutil, subprocess, sys, time                                    # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P, motor_gate as MG, drive_legguard as LG                             # noqa: E401,E402
LEG_PY = os.path.join(HERE, "diag_c104_leg.py")
GATE_PY = os.path.join(ROOT, "tools", "motor_gate.py")
KEEP = ("SESSION", "LIMITS", "PRELIMITS", "REFSTATE", "VERIFY-RESULT", "PI  :", "ASI :", "RESULT", "FAIL:", "REFUSED")


def wait_lv_gone(log=print, lv_fn=LG.lv_running, kill=LG.kill_labview, wait_s=90):
    """Wait up to wait_s for LabVIEW to exit, then kill it; returns True when no LabVIEW.exe is listed (moved: 110 :46-49)."""
    t2 = time.time()
    while lv_fn() and time.time() - t2 < wait_s:
        time.sleep(5)
    if lv_fn():
        kill(); log("  taskkill LabVIEW")                                               # noqa: E702
    return not lv_fn()


def leg(tag, src, picks, run_s, legdir, G, rows, log=print, precheck=None, run=None, lv_fn=LG.lv_running):
    """Run ONE replay leg: VISA precheck, `diag_c104_leg.py --src --picks --run-s --out <legdir>/<tag>_a<n>`, LabVIEW-gone wait,
    at most one rerun when the run_dir is missing or picks != `picks`. Writes gates V1/T1/T2/T3 into G, one ROW per attempt into
    rows; returns the run_dir or None. Moved from drive_m8_replay_110.py:33-59. Self-test: selftest() cases L1/L2."""
    precheck = precheck or (lambda: LG.visa_precheck(dry=False, log=lambda s: log("  " + s)))
    run = run or (lambda out: subprocess.run([sys.executable, "-u", LEG_PY, "--src", src, "--picks", str(picks), "--run-s", str(run_s),
                                              "--out", out], capture_output=True, text=True, errors="replace", timeout=18 * 60))
    for att in (1, 2):
        out = os.path.join(legdir, "%s_a%d" % (tag, att)); os.makedirs(out, exist_ok=True)                 # noqa: E702
        pc = precheck()
        G["V1 %s a%d VISA precheck 0" % (tag, att)] = pc["ok"]
        if not pc["ok"]:
            return None
        t = time.time()
        r = run(out)
        for ln in (r.stdout or "").splitlines():
            if ln.startswith(("GATE ", "RESULT ", "REGISTERED")):
                log("  " + ln[:500])
        G["T3 %s a%d LabVIEW gone after" % (tag, att)] = wait_lv_gone(log, lv_fn)
        F = (json.load(open(os.path.join(out, "leg.json"))) if os.path.isfile(os.path.join(out, "leg.json")) else {}).get("facts") or {}
        reg = F.get("picks_registered_tra")
        row = {"leg": tag, "attempt": att, "rc": r.returncode, "secs": round(time.time() - t), "run_dir": F.get("run_dir"),
               "registered": reg, "lost": F.get("lost"), "frames_delta": F.get("frames_delta"), "src": src,
               "source_md5": F.get("source_md5"), "v5_failing": F.get("v5_failing"), "dir": out}
        rows.append(row); log("ROW " + json.dumps(row, default=str))                    # noqa: E702
        if row["run_dir"] and reg == picks:
            G["T1 %s rc 0" % tag] = r.returncode == 0; G["T2 %s %d picks registered" % (tag, picks)] = True    # noqa: E702
            return row["run_dir"]
    G["T2 %s %d picks registered" % (tag, picks)] = False
    return None


def motor_session(action, limits=None, log=print, run=None):
    """`py tools/motor_gate.py --session start|end` (the gate verifies by readback itself; the readback lines are re-checked here
    with motor_gate.check_pi_readback / check_asi_readback against motor_limits.json: start = the session limits + PI referenced
    at 0, end = the release values). Returns {action, rc, ok, lines (kept readback lines), pi, asi, ref, checks}. Self-test: M1-M3."""
    limits = limits or MG.load_limits()
    run = run or (lambda: subprocess.run([sys.executable, GATE_PY, "--session", action], capture_output=True, text=True,
                                         errors="replace", timeout=300, cwd=ROOT))
    try:
        r = run()
        rc, text = r.returncode, (r.stdout or "") + (r.stderr or "")
    except Exception as e:                                                               # noqa: BLE001
        rc, text = 99, "motor_gate raised %r" % e
    for ln in text.splitlines():
        log("    | " + ln)
    pi, asi, ref = MG.parse_pi_limits(text), MG.parse_asi_limits(text), MG.parse_pi_ref(text)
    tol = float(limits.get("tolerance", MG.DEFAULT_TOL))
    if action == "start":
        lo, hi, sl, su = float(limits["pi"]["lo_mm"]), float(limits["pi"]["hi_mm"]), limits["asi"]["sl"], limits["asi"]["su"]
        ref_ok = bool(ref) and ref["FRF"] == 1.0 and abs(ref["POS"]) <= tol and "VERIFY-RESULT: OK" in text
    else:
        rel = limits["asi"]["release"]
        lo, hi = 0.0, float(limits["pi"]["release_hi_mm"])
        sl, su = {"X": float(rel["sl"]), "Y": float(rel["sl"])}, {"X": float(rel["su"]), "Y": float(rel["su"])}
        ref_ok = True
    cp, ca = MG.check_pi_readback(pi, lo, hi, tol), MG.check_asi_readback(asi, sl, su, tol)
    word = "SESSION %s OK" % action.upper()
    ok = rc == 0 and word in text and cp[0] and ca[0] and ref_ok
    return {"action": action, "rc": rc, "ok": ok, "pi": pi, "asi": asi, "ref": ref, "ref_ok": ref_ok,
            "checks": {"pi": cp[1], "asi": ca[1], word: word in text},
            "lines": [ln.strip() for ln in text.splitlines() if ln.strip().startswith(KEEP)]}


def keep_leg_files(out, picks, run_s, t0, log=print):
    """Copy the leg's tools/bench jsons written at or after t0 (m8_replay_s1_p<N>_r<S>.json, m8_v5_replay_s1_p<N>_r<S>[_clicks].json:
    shared names, so the next leg with the same picks overwrites them) into the leg's --out dir under the role name (the
    '_p<N>_r<S>' part removed). Returns {kept name: source}. An older file (not this leg's) is never copied."""
    tag = "_p%d_r%d" % (picks, int(float(run_s)))
    kept = {}
    for p in sorted(glob.glob(os.path.join(HERE, "m8*_replay_s1%s*.json" % tag))):
        if p.endswith("_dry.json") or os.path.getmtime(p) < t0:
            continue
        name = os.path.basename(p).replace(tag, "")
        shutil.copyfile(p, os.path.join(out, name)); kept[name] = os.path.relpath(p, ROOT)                # noqa: E702
    log("KEPT %s" % json.dumps(kept))
    return kept


class _R(object):
    def __init__(self, rc, stdout):
        self.returncode, self.stdout, self.stderr = rc, stdout, ""


def _logrun(path):
    """A recorded motor_gate run (bgrun log) as a CompletedProcess-like stub: rc from 'BGRUN END rc=', body without BGRUN lines."""
    t = open(path, encoding="utf-8", errors="replace").read()
    rc = int(t.split("BGRUN END rc=")[1].split()[0]) if "BGRUN END rc=" in t else 99
    return lambda: _R(rc, "\n".join(ln for ln in t.splitlines() if not ln.startswith("BGRUN")))


SELF_LEGS = os.path.join(HERE, "t0_legs", "c110f_replay_20260927_184600")


def selftest():
    """Offline: M1 recorded session start (motor_session_start_cycle170.log) ok with PI 0..39 and ASI SL/SU readback; M2 recorded
    end (motor_session_end_20260927_userstop.log) ok with the release values; M3 the start text with the reference line removed
    -> not ok; L1 leg() with a stub run that writes the stored 110-7 leg A leg.json -> returns its run_dir in 1 attempt; L2 a stub
    leg.json with 14 picks -> 2 attempts, None; L3 VISA precheck refused -> None, no run; K1 keep_leg_files copies nothing older
    than t0. Returns the gate dict."""
    G, logs = {}, []
    lg = logs.append
    m1 = motor_session("start", log=lg, run=_logrun(os.path.join(HERE, "motor_session_start_cycle170.log")))
    G["M1 recorded start: ok, PI TMX 39, ASI SL X -3.847494, referenced"] = (m1["ok"] and m1["pi"]["TMX"] == 39.0
                                                                             and m1["asi"]["SL"]["X"] == -3.847494 and m1["ref_ok"])
    m2 = motor_session("end", log=lg, run=_logrun(os.path.join(HERE, "motor_session_end_20260927_userstop.log")))
    G["M2 recorded end: ok, PI TMX 52, ASI +-500"] = m2["ok"] and m2["pi"]["TMX"] == 52.0 and m2["asi"]["SU"]["Y"] == 500.0
    st = _logrun(os.path.join(HERE, "motor_session_start_cycle170.log"))()
    noref = _R(0, "\n".join(ln for ln in st.stdout.splitlines() if not ln.startswith("REFSTATE")))
    G["M3 start text without REFSTATE -> not ok"] = motor_session("start", log=lg, run=lambda: noref)["ok"] is False
    tmp = os.path.join(HERE, "m8_legs_selftest_%s" % time.strftime("%Y%m%d_%H%M%S"))
    stored = json.load(open(os.path.join(SELF_LEGS, "A_S1replay_a1", "leg.json"), encoding="utf-8"))

    def stub(picks_reg):
        def run(out):
            d = dict(stored, facts=dict(stored["facts"], picks_registered_tra=picks_reg))
            json.dump(d, open(os.path.join(out, "leg.json"), "w"), default=str)
            return _R(0, "REGISTERED stub\nRESULT {}\n")
        return run
    ok_pc = lambda: {"ok": True}                                                         # noqa: E731
    g1, r1 = {}, []
    rd = leg("A", "stub.vi", 15, 120, tmp, g1, r1, log=lg, precheck=ok_pc, run=stub(15.0), lv_fn=lambda: False)
    G["L1 stored leg A: run_dir returned, 1 attempt, lost '0', frames_delta 4081"] = (
        rd == stored["facts"]["run_dir"] and len(r1) == 1 and r1[0]["lost"] == "0" and r1[0]["frames_delta"] == 4081 and all(g1.values()))
    g2, r2 = {}, []
    G["L2 14 of 15 picks: 2 attempts, None, T2 FAIL"] = (leg("B", "stub.vi", 15, 120, tmp, g2, r2, log=lg, precheck=ok_pc, run=stub(14.0),
                                                              lv_fn=lambda: False) is None and len(r2) == 2 and g2["T2 B 15 picks registered"] is False)
    g3, r3, calls = {}, [], []
    G["L3 VISA precheck refused: None, leg not run"] = (leg("C", "stub.vi", 15, 120, tmp, g3, r3, log=lg, precheck=lambda: {"ok": False},
                                                             run=lambda out: calls.append(out), lv_fn=lambda: False) is None and not calls and not r3)
    G["K1 keep_leg_files: nothing older than t0 copied"] = keep_leg_files(tmp, 15, 120, time.time() + 60, log=lg) == {}
    shutil.rmtree(tmp, ignore_errors=True)
    for ln in logs:
        if ln.startswith(("ROW", "KEPT")):
            print(ln[:300], flush=True)
    print("FACT M1 lines %s" % json.dumps(m1["lines"]), flush=True)
    for k, v in G.items():
        print("GATE %-75s %s" % (k, "PASS" if v else "FAIL"), flush=True)
    return G


if __name__ == "__main__" and "--selftest" in sys.argv:
    _G = selftest()
    _bad = [k for k, v in _G.items() if not v]
    print(P.result_line(P.make_result(len(_G) - len(_bad), len(_bad), _bad[0] if _bad else None, [])), flush=True)
    sys.exit(1 if _bad else 0)
