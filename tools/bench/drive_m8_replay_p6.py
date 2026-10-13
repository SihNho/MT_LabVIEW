# ---
# labview: read
# hardware: motor
# offline-args: --selftest --help
# evidence: tools/bench/drive_m8_replay_p6.py:139
# ---
r"""drive_m8_replay_p6 - card 170-a3-3 (ring-p6.md PD409(f), PD410(c)/(d)/(f), PD411(c)-(e)): the S1-vs-P6 replay leg chain.
    py -u tools/bench/drive_m8_replay_p6.py --p6 <P6 replay copy> [--s1-run-s 120] [--p6-run-s 150] [--picks 15]
    py -u tools/bench/drive_m8_replay_p6.py --selftest | --help          (offline: stubs + the stored 110-7 run dirs)
ORDER: P1 pins (S1 replay copy D1_s1_replay_20260925_075422.vi == 126f8497; the P6 copy == stage_replay_swap_170.json
copies.p6.md5, written by card 170-a3-2) -> mismatch = stop before any leg. Then per leg (S1 120 s, then P6 150 s):
`motor_gate.py --session start` (readback re-checked) -> the leg (m8_legs.leg = diag_c104_leg.py, VISA precheck, one rerun,
LabVIEW-gone wait) -> `--session end` (ALWAYS after a start attempt, readback re-checked), so no limits stay set after the last
leg. A refused start, a leg with no run_dir or a refused end stops the chain. Compare ONLY IF S1 lost == 0 and P6 tra rows
>= 1500 (PD409(c)/PD410(c)/(d)), else the numbers are written and the chain stops: m8b_replay_compare.compare_p6 (= compare_bc
+ init range + the other leg files) with D = 20 slots, docs/d1/ring-p4b.md:21 (U13, PD411(c)), no graph read.
MOTOR SESSION FACTS (tools/motor_gate.py:22-26, drive_original_copy_v5.py:51-52/:549-561): the leg's v5 runs `--session
start` itself before LabVIEW opens and NEVER `--session end`; the cycle runner opens one at cycle start and releases it at
cycle end. So this driver's END after each leg is the only release inside the chain; its START repeats the PI reference move
that v5's start then performs again (two reference moves per leg; none is skipped).
FOUND FIRST: drive_m8_replay_110.py (hard-coded legs, card 110-7 record, unchanged) - its leg runner is now m8_legs.leg;
m8b_replay_compare (tra, dir_files, compare_bc, compare_p6); motor_gate.load_limits.
PREDICTION (the next card's run): P1 PASS; MS/ME S1 and P6 PASS (readback); T1/T2/T3 per leg PASS; S1 lost 0; P6 rows >= 1500;
compare items are FACTS (ITEM lines + tools/bench/m8b_replay_p6.json), never re-run; P2 pins unchanged; H LabVIEW gone."""
import hashlib, json, os, shutil, struct, sys, time                                     # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P, m8_legs as L, m8b_replay_compare as CMP, motor_gate as MG, drive_legguard as LG   # noqa: E401,E402
RP = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\replay"
S1_PIN = (os.path.join(RP, "D1_s1_replay_20260925_075422.vi"), "126f84975fca9f6124432a7e4decd0c8")
SWAP_JSON = os.path.join(HERE, "stage_replay_swap_170.json")
D_SLOTS = 20            # docs/d1/ring-p4b.md:21 (U13; PD411(c)): the ring's 20 slots, uid #27433 -> Q&R #27373 y
MIN_P6_ROWS = 1500      # ring-p6.md PD410(d): >= 1500 tra rows for the P6 leg
USAGE = __doc__.splitlines()[1] + "\n" + __doc__.splitlines()[2]


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def pins(p6, s1=S1_PIN, swap_json=SWAP_JSON):
    """P1: the S1 copy's md5 == its pin and the P6 copy's md5 == copies.p6.md5 of swap_json; returns {S1, P6: [path, pin, disk md5],
    ok}. A missing file or key gives pin/disk None and ok False."""
    try:
        p6pin = json.load(open(swap_json, encoding="utf-8"))["copies"]["p6"]["md5"]
    except (OSError, ValueError, KeyError, TypeError):
        p6pin = None
    r = {}
    for k, (p, m) in (("S1", s1), ("P6", (os.path.normpath(p6), p6pin))):
        r[k] = [p, m, md5(p) if os.path.isfile(p) else None]
    r["ok"] = all(r[k][1] and r[k][1] == r[k][2] for k in ("S1", "P6"))
    return r


def lost0(v):
    """True only when leg.json facts.lost is a number equal to 0 (110-7 stored it as the string '0'); None/text -> False."""
    try:
        return float(v) == 0.0
    except (TypeError, ValueError):
        return False


assert lost0("0") and lost0(0) and not lost0(None) and not lost0("3") and not lost0("n/a")


def leg_report(rows, rd, ms, me, G, tag):
    """Per-leg facts (not gates): tra rows, Total Lost Frames, frame-counter delta, run-dir files (size, md5), LabVIEW gone,
    motor session start/end readback lines."""
    row = rows[-1] if rows else {}
    ti = CMP.tra(rd)[0] if rd and os.path.isdir(rd) else None
    return {"tra_rows": ti["dims"][0] if ti and ti["parsed"] else None, "tra_parsed": bool(ti and ti["parsed"]),
            "lost": row.get("lost"), "frames_delta": row.get("frames_delta"), "run_dir": rd, "leg_dir": row.get("dir"),
            "run_dir_files": CMP.dir_files(rd) if rd and os.path.isdir(rd) else None, "attempts": len(rows),
            "labview_gone": [v for k, v in G.items() if k.startswith("T3 %s " % tag)],
            "motor_start": {"ok": ms["ok"], "lines": ms["lines"]} if ms else None,
            "motor_end": {"ok": me["ok"], "lines": me["lines"]} if me else None}


def chain(p6, s1_run_s, p6_run_s, picks, legdir, out, G, log=print, s1=S1_PIN, swap_json=SWAP_JSON, limits=None,
          legfn=L.leg, motorfn=L.motor_session, keepfn=L.keep_leg_files, lv_fn=LG.lv_running):
    """The ordered chain (module doc). Writes gates into G; returns {pins, steps, legs, compare, stop}. Self-test: selftest()."""
    limits = limits or MG.load_limits()
    rep = {"pins": pins(p6, s1, swap_json), "steps": [], "legs": {}, "compare": None, "stop": None}
    G["P1 S1 copy == 126f8497 pin and P6 copy == stage_replay_swap_170.json copies.p6.md5"] = rep["pins"]["ok"]
    if not rep["pins"]["ok"]:
        rep["stop"] = "P1 pin mismatch or missing: no leg"
        return rep
    G["H0 no LabVIEW before leg 1"] = not lv_fn()
    if not G["H0 no LabVIEW before leg 1"]:
        rep["stop"] = "LabVIEW running before leg 1: no leg"
        return rep
    rds = {}
    for tag, src, run_s in (("S1", s1[0], s1_run_s), ("P6", rep["pins"]["P6"][0], p6_run_s)):
        rows, rd, me = [], None, None
        rep["steps"].append("start " + tag)
        ms = motorfn("start", limits=limits, log=log)
        G["MS %s motor session start verified by readback" % tag] = ms["ok"]
        try:
            if ms["ok"]:
                rep["steps"].append("leg " + tag)
                t0 = time.time()
                rd = legfn(tag, src, picks, run_s, legdir, G, rows, log)
                if rows:
                    rows[-1]["kept"] = keepfn(rows[-1]["dir"], picks, run_s, t0, log)
        finally:
            rep["steps"].append("end " + tag)
            me = motorfn("end", limits=limits, log=log)
            G["ME %s motor session end verified by readback" % tag] = me["ok"]
        rep["legs"][tag] = leg_report(rows, rd, ms, me, G, tag)
        print("LEG %s %s" % (tag, json.dumps({k: v for k, v in rep["legs"][tag].items() if k not in ("run_dir_files", "motor_start", "motor_end")},
                                             default=str)), flush=True)
        if not (ms["ok"] and rd and me["ok"]):
            rep["stop"] = "%s: motor start %s, run_dir %s, motor end %s - chain stopped" % (tag, ms["ok"], rd, me["ok"])
            return rep
        rds[tag] = (rd, rows[-1]["dir"])
    s1_lost, p6_rows = rep["legs"]["S1"]["lost"], rep["legs"]["P6"]["tra_rows"]
    if not lost0(s1_lost):
        rep["stop"] = "S1 Total Lost Frames %r != 0: no compare (PD409(c)/PD410(c))" % (s1_lost,)
    elif p6_rows is None or p6_rows < MIN_P6_ROWS:
        rep["stop"] = "P6 tra rows %r < %d: no compare (PD410(d))" % (p6_rows, MIN_P6_ROWS)
    else:
        rep["steps"].append("compare")
        R, I = CMP.compare_p6(rds["S1"][0], rds["P6"][0], D_SLOTS, out, rds["S1"][1], rds["P6"][1], limits)
        rep["compare"] = {"out": os.path.relpath(out, ROOT), "items": I, "common": (R.get("xyz") or {}).get("common"),
                          "rows_not_identical": (R.get("xyz") or {}).get("rows_not_identical"), "distinct": R.get("distinct")}
    G["R compare ran (S1 lost 0, P6 rows >= %d)" % MIN_P6_ROWS] = rep["compare"] is not None
    return rep


def _cut_tra(src_dir, dst_dir, n):
    """Self-test helper: a copy of src_dir's tra file truncated to its first n rows (same header, dims rewritten)."""
    f = [x for x in sorted(os.listdir(src_dir)) if x.lower().startswith("tra")][0]
    b = open(os.path.join(src_dir, f), "rb").read(); k = b.find(b"not in z!)") + 10                        # noqa: E702
    r, c = struct.unpack("<ii", b[k:k + 8])
    os.makedirs(dst_dir, exist_ok=True)
    open(os.path.join(dst_dir, f), "wb").write(b[:k] + struct.pack("<ii", n, c) + b[k + 8:k + 8 + 8 * n * c])


def selftest():
    """Offline, stubs only: legs = the stored 110-7 run dirs (A = m8_out/replay_s1_20260927_184651, B = leg B's run_dir), pins =
    two scratch files, motor_gate = a recorder. C1 order start/leg/end x2 then compare: 4443 rows, 0 X/Y/Z differ, DISTINCT
    4443/4443 at D 20; C2 pin mismatch -> no step; C3 S1 lost '3' -> both legs, no compare; C4 P6 1000 rows -> no compare;
    C5 S1 start refused -> end still called, no leg, chain stops; C6 the stored dirs unchanged."""
    G = {}
    tmp = os.path.join(HERE, "drive_m8_replay_p6_selftest_%s" % time.strftime("%Y%m%d_%H%M%S"))
    os.makedirs(tmp)
    s1f, p6f = os.path.join(tmp, "s1.bin"), os.path.join(tmp, "p6.bin")
    open(s1f, "wb").write(b"s1"); open(p6f, "wb").write(b"p6")                                              # noqa: E702
    good, bad = os.path.join(tmp, "swap_good.json"), os.path.join(tmp, "swap_bad.json")
    json.dump({"copies": {"p6": {"md5": md5(p6f)}}}, open(good, "w")); json.dump({"copies": {"p6": {"md5": "0" * 32}}}, open(bad, "w"))  # noqa: E702
    S1 = (s1f, md5(s1f))
    legs = os.path.join(HERE, "t0_legs", "c110f_replay_20260927_184600")
    A = os.path.join(HERE, "m8_out", "replay_s1_20260927_184651")
    B = CMP.run_dirs(os.path.join(legs, "B_dispreplay_a1", "leg.json"))[0]
    h0 = dict((d, CMP.dir_files(d)) for d in (A, B, os.path.join(legs, "A_S1replay_a1"), os.path.join(legs, "B_dispreplay_a1")))
    B1000 = os.path.join(tmp, "B_1000rows")
    _cut_tra(B, B1000, 1000)

    def run(case, lost="0", brd=B, start_ok=True, swap=good):
        calls, g = [], {}

        def motor(action, limits=None, log=print):
            calls.append(action)
            return {"ok": start_ok or action == "end", "lines": ["STUB %s" % action]}

        def legfn(tag, src, picks, run_s, legdir, G_, rows, log):
            calls.append("leg %s %s %d %d" % (tag, os.path.basename(src), picks, run_s))
            rows.append({"dir": os.path.join(legs, "A_S1replay_a1" if tag == "S1" else "B_dispreplay_a1"),
                         "lost": lost if tag == "S1" else "0", "frames_delta": 4081})
            G_["T3 %s a1 LabVIEW gone after" % tag] = True
            return A if tag == "S1" else brd
        rep = chain(p6f, 120, 150, 15, os.path.join(tmp, "legs"), os.path.join(tmp, "m8b_%s.json" % case), g, log=lambda s: None,
                    s1=S1, swap_json=swap, legfn=legfn, motorfn=motor, keepfn=lambda *a: {}, lv_fn=lambda: False)
        print("CASE %s steps %s calls %s stop %r" % (case, rep["steps"], calls, rep["stop"]), flush=True)
        return rep, calls
    full = ["start S1", "leg S1", "end S1", "start P6", "leg P6", "end P6"]
    r1, c1 = run("C1")
    cmp1 = r1["compare"] or {}
    print("FACT C1 compare %s" % json.dumps(cmp1, default=str)[:900], flush=True)
    G["C1 order start/leg/end S1 then P6, then compare"] = r1["steps"] == full + ["compare"] and c1 == [
        "start", "leg S1 s1.bin 15 120", "end", "start", "leg P6 p6.bin 15 150", "end"]
    G["C1 compare: 4443 rows, 0 X/Y/Z differ, DISTINCT 4443/4443 at D 20"] = (
        cmp1.get("common") == 4443 and cmp1.get("rows_not_identical") == 0 and (cmp1.get("distinct") or {}).get("pass") == 4443
        and (cmp1.get("distinct") or {}).get("slots") == 20 and cmp1["items"].get("C1 DISTINCT all common rows") is True)
    r2, c2 = run("C2", swap=bad)
    G["C2 pin mismatch: stop before any leg, no motor call"] = r2["steps"] == [] and c2 == [] and "P1" in (r2["stop"] or "")
    r3, _c3 = run("C3", lost="3")
    G["C3 S1 lost '3': both legs, no compare"] = r3["steps"] == full and r3["compare"] is None and "Lost" in (r3["stop"] or "")
    r4, _c4 = run("C4", brd=B1000)
    G["C4 P6 1000 tra rows: no compare"] = (r4["steps"] == full and r4["compare"] is None and r4["legs"]["P6"]["tra_rows"] == 1000
                                            and "1500" in (r4["stop"] or ""))
    r5, c5 = run("C5", start_ok=False)
    G["C5 S1 start refused: end still called, no leg, stop"] = r5["steps"] == ["start S1", "end S1"] and c5 == ["start", "end"] and r5["stop"]
    h1 = dict((d, CMP.dir_files(d)) for d in h0)
    G["C6 stored 110-7 run and leg dirs unchanged (name, size, md5)"] = h0 == h1
    shutil.rmtree(tmp, ignore_errors=True)
    return G


if __name__ == "__main__":
    A_ = sys.argv[1:]
    if "--help" in A_ or not A_:
        print(USAGE)
        print(P.result_line(P.make_result(1, 0, None, [])), flush=True)
        sys.exit(0)
    if "--selftest" in A_:
        G = selftest()
        arts = []
    else:
        def arg(k, d):
            return A_[A_.index(k) + 1] if k in A_ else d
        p6, s1s, p6s, npk = arg("--p6", None), int(arg("--s1-run-s", 120)), int(arg("--p6-run-s", 150)), int(arg("--picks", 15))
        if not p6:
            print("REFUSED: --p6 <P6 replay copy> is required\n" + USAGE)
            print(P.result_line(P.make_result(0, 1, "usage: --p6 missing", [])), flush=True)
            sys.exit(4)
        G, ts = {}, time.strftime("%Y%m%d_%H%M%S")
        # lean bench 2026-10-13: --out-root <dir> keeps legs, run dirs (M8_RUN_ROOT), m8 jsons (M8_OUT_DIR) and the compare out of
        # t0_legs / m8_out; --swap-json <json> gives the P6 copy's md5 pin (default stage_replay_swap_170.json)
        root, swj = arg("--out-root", None), arg("--swap-json", SWAP_JSON)
        legdir = os.path.join(root, "legs") if root else os.path.join(HERE, "t0_legs", "c170_p6_replay_%s" % ts)
        os.makedirs(legdir, exist_ok=True)
        if root:
            os.environ["M8_RUN_ROOT"], os.environ["M8_OUT_DIR"] = os.path.join(root, "run"), os.path.join(root, "m8json")
        out = os.path.join(root, "m8b_replay_p6.json") if root else os.path.join(HERE, "m8b_replay_p6.json")
        repp = os.path.join(root, "drive_m8_replay_p6.json") if root else os.path.join(HERE, "drive_m8_replay_p6.json")
        log = lambda s: print(s, flush=True)                                             # noqa: E731
        rep = chain(p6, s1s, p6s, npk, legdir, out, G, log=log, swap_json=swj)
        ma = pins(p6, swap_json=swj)
        G["P2 pins md5 after == before"] = [ma[k][2] for k in ("S1", "P6")] == [rep["pins"][k][2] for k in ("S1", "P6")]
        G["H LabVIEW gone at end"] = not LG.lv_running()
        rep.update({"card": "170-a3-3 driver", "gates": G, "args": {"p6": p6, "s1_run_s": s1s, "p6_run_s": p6s, "picks": npk},
                    "legdir": os.path.relpath(legdir, ROOT), "slots": D_SLOTS, "judgement_not_applied": "PD409(h)/PD411(d)"})
        json.dump(rep, open(repp, "w", encoding="utf-8"), indent=1, default=str)
        print("STOP %r" % rep["stop"], flush=True)
        arts = [repp] + ([out] if rep["compare"] else [])
    for k, v in G.items():
        print("GATE %-85s %s" % (k, "PASS" if v else "FAIL"), flush=True)
    bad = [k for k, v in G.items() if not v]
    print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None,
                                      [{"path": os.path.relpath(a, ROOT), "md5": md5(a)} for a in arts])), flush=True)
    sys.exit(1 if bad else 0)
