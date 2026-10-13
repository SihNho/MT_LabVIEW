r"""p63_legs - lean task P6-3: run P6 test legs (no S1 leg; P6-2's S1 leg is the reference) and align each with S1.
Per leg, as drive_m8_replay_p6.chain does: `motor_gate.py --session start` (readback re-checked) -> m8_legs.leg (VISA
precheck, diag_c104_leg.py, one rerun, LabVIEW-gone wait) -> `--session end` (ALWAYS after a start attempt) -> keep the m8
jsons. Pin: the leg VI's md5 before the leg == the md5 given (from p63_build.json) and unchanged after. Then p63_align on
(S1 reference run dir, the leg's run dir). Outputs under --out-root: legs/<TAG>_a<n>/, run/, m8json/, p63_legs.json.
    py -u tools/bench/lean_bench/p63_legs.py --out-root <abs dir> --leg TAG=<vi path>::<md5> [--leg ...] [--run-s 150] [--picks 15]"""
import hashlib, json, os, sys, time                                                      # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); BENCH = os.path.dirname(HERE); ROOT = os.path.dirname(os.path.dirname(BENCH))
sys.path.insert(0, HERE); sys.path.insert(0, BENCH); sys.path.insert(0, os.path.join(ROOT, "tools"))
import m8_legs as L, motor_gate as MG, drive_legguard as LG, p63_align as AL                  # noqa: E401,E402
S1_REF = os.path.join(HERE, "out_20261013d", "run", "replay_s1_20261013_142928")         # P6-2 S1 leg: 6321 rows, lost 0


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.isfile(p) else None


def main(av):
    arg = lambda k, d: av[av.index(k) + 1] if k in av else d                              # noqa: E731
    root, run_s, picks = os.path.abspath(arg("--out-root", "")), int(arg("--run-s", 150)), int(arg("--picks", 15))
    legs = []
    for i, a in enumerate(av):
        if a == "--leg":
            tag, rest = av[i + 1].split("=", 1)
            p, m = rest.rsplit("::", 1)
            legs.append((tag, p, m))
    os.makedirs(os.path.join(root, "legs"), exist_ok=True)
    os.environ["M8_RUN_ROOT"], os.environ["M8_OUT_DIR"] = os.path.join(root, "run"), os.path.join(root, "m8json")
    log = lambda s: print(s, flush=True)                                                  # noqa: E731
    limits = MG.load_limits()
    G, rep = {}, {"legs": {}, "s1_ref": os.path.relpath(S1_REF, ROOT), "run_s": run_s, "picks": picks}
    G["H0 no LabVIEW before leg 1"] = not LG.lv_running()
    for tag, src, pin in legs:
        if not G["H0 no LabVIEW before leg 1"]:
            break
        m0 = md5(src)
        G["P1 %s md5 == pin %s" % (tag, pin[:8])] = m0 == pin
        if m0 != pin:
            rep["legs"][tag] = {"stop": "pin mismatch %s" % m0}
            continue
        rows, rd = [], None
        ms = L.motor_session("start", limits=limits, log=log)
        G["MS %s motor session start verified by readback" % tag] = ms["ok"]
        try:
            if ms["ok"]:
                t0 = time.time()
                rd = L.leg(tag, src, picks, run_s, os.path.join(root, "legs"), G, rows, log)
                if rows:
                    rows[-1]["kept"] = L.keep_leg_files(rows[-1]["dir"], picks, run_s, t0, log)
        finally:
            me = L.motor_session("end", limits=limits, log=log)
            G["ME %s motor session end verified by readback" % tag] = me["ok"]
        G["P2 %s md5 unchanged by the leg" % tag] = md5(src) == m0
        row = rows[-1] if rows else {}
        r = {"src": src, "md5": m0, "run_dir": rd, "leg_dir": row.get("dir"), "lost": row.get("lost"),
             "frames_delta": row.get("frames_delta"), "attempts": len(rows), "secs": row.get("secs"),
             "motor_start": ms["lines"], "motor_end": me["lines"], "motor_start_ok": ms["ok"], "motor_end_ok": me["ok"]}
        if rd and os.path.isdir(rd):
            try:
                r["align"] = AL.main(S1_REF, rd, os.path.join(root, "align_%s.json" % tag))
                r["align"] = {k: r["align"][k] for k in ("align", "colB", "colB0", "col0_label", "gap_classes") if k in r["align"]}
            except Exception as e:                                                        # noqa: BLE001
                r["align"] = {"error": repr(e)[:300]}
        rep["legs"][tag] = r
        log("LEG %s %s" % (tag, json.dumps({k: v for k, v in r.items() if k not in ("motor_start", "motor_end", "align")}, default=str)))
        if not (ms["ok"] and me["ok"]):
            log("STOP: motor session start %s / end %s - no further leg" % (ms["ok"], me["ok"]))
            break
    G["H LabVIEW gone at end"] = not LG.lv_running()
    rep["gates"] = G
    json.dump(rep, open(os.path.join(root, "p63_legs.json"), "w", encoding="utf-8"), indent=1, default=str)
    for k, v in G.items():
        print("GATE %-80s %s" % (k, "PASS" if v else "FAIL"), flush=True)
    return 0 if all(G.values()) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
