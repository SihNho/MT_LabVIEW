r"""p6fix_legs - lean task p6fix: run P6 test legs on the fixed copies and align each with P6-2's S1 leg, column 0 included.
Lean rules (CLAUDE.md 1b, 2026-10-13): the QUEUE owns the motor session (limits set + PI reference + readback before this
session; released after it). So, unlike p63_legs.py, this runner never calls motor_gate's session verbs; before EVERY leg it
checks that tools/bench/motor_session.json exists (missing -> stop, no leg). The leg itself is unchanged: m8_legs.leg =
VISA precheck -> diag_c104_leg.py (v5 + its own built-in gate step) -> LabVIEW-gone wait, one rerun. The readback lines of
the leg's own gate call are copied from the leg's kept v5 json into the report json.
Pin: each leg VI's md5 == the md5 given (from p6fix_build.json) before and unchanged after. Then p6fix_align (mode same|gap).
    py -u tools/bench/lean_bench/p6fix_legs.py --out-root <abs dir> --leg TAG=<vi path>::<md5>::<same|gap> [--leg ...] [--run-s 150] [--picks 15]"""
import hashlib, json, os, sys, time                                                      # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); BENCH = os.path.dirname(HERE); ROOT = os.path.dirname(os.path.dirname(BENCH))
sys.path.insert(0, HERE); sys.path.insert(0, BENCH); sys.path.insert(0, os.path.join(ROOT, "tools"))
import m8_legs as L, drive_legguard as LG, p6fix_align as AL                              # noqa: E401,E402
S1_REF = os.path.join(HERE, "out_20261013d", "run", "replay_s1_20261013_142928")         # P6-2 S1 leg: 6321 rows, lost 0
S1_GAP = os.path.join(HERE, "out_p63_s1gap", "run", "replay_s1_20261013_171345")          # P6-3 S1 on the gapped source
SESSION = os.path.join(BENCH, "motor_session.json")


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.isfile(p) else None


def gate_lines(leg_dir):
    """The leg's own v5 gate-call record (facts.motor_start) from its kept m8_v5 json, if any."""
    out = {}
    for n in sorted(os.listdir(leg_dir)) if leg_dir and os.path.isdir(leg_dir) else []:
        if n.startswith("m8_v5_replay_s1") and n.endswith(".json") and "clicks" not in n:
            try:
                d = json.load(open(os.path.join(leg_dir, n), encoding="utf-8"))
            except ValueError:
                continue
            f = d.get("facts") or d.get("FACTS") or {}
            out[n] = f.get("motor_start") or d.get("motor_start")
    return out


def main(av):
    arg = lambda k, d: av[av.index(k) + 1] if k in av else d                              # noqa: E731
    root, run_s, picks = os.path.abspath(arg("--out-root", "")), int(arg("--run-s", 150)), int(arg("--picks", 15))
    legs = []
    for i, a in enumerate(av):
        if a == "--leg":
            tag, rest = av[i + 1].split("=", 1)
            p, m, mode = rest.rsplit("::", 2)
            legs.append((tag, p, m, mode))
    os.makedirs(os.path.join(root, "legs"), exist_ok=True)
    os.environ["M8_RUN_ROOT"], os.environ["M8_OUT_DIR"] = os.path.join(root, "run"), os.path.join(root, "m8json")
    log = lambda s: print(s, flush=True)                                                  # noqa: E731
    G, rep = {}, {"legs": {}, "s1_ref": os.path.relpath(S1_REF, ROOT), "run_s": run_s, "picks": picks}
    G["H0 no LabVIEW before leg 1"] = not LG.lv_running()
    for tag, src, pin, mode in legs:
        if not G["H0 no LabVIEW before leg 1"]:
            break
        G["S %s motor_session.json present (queue's session)" % tag] = os.path.isfile(SESSION)
        if not os.path.isfile(SESSION):
            log("STOP: tools/bench/motor_session.json missing before leg %s - no leg" % tag)
            break
        m0 = md5(src)
        G["P1 %s md5 == pin %s" % (tag, pin[:8])] = m0 == pin
        if m0 != pin:
            rep["legs"][tag] = {"stop": "pin mismatch %s" % m0}
            continue
        rows, rd, t0 = [], None, time.time()
        rd = L.leg(tag, src, picks, run_s, os.path.join(root, "legs"), G, rows, log)
        if rows:
            rows[-1]["kept"] = L.keep_leg_files(rows[-1]["dir"], picks, run_s, t0, log)
        G["P2 %s md5 unchanged by the leg" % tag] = md5(src) == m0
        row = rows[-1] if rows else {}
        r = {"src": src, "md5": m0, "mode": mode, "run_dir": rd, "leg_dir": row.get("dir"), "lost": row.get("lost"),
             "frames_delta": row.get("frames_delta"), "attempts": len(rows), "secs": row.get("secs"), "v5_failing": row.get("v5_failing"),
             "leg_gate_call": gate_lines(row.get("dir")), "session_json_after": os.path.isfile(SESSION)}
        if rd and os.path.isdir(rd):
            try:
                a = AL.main(S1_REF, rd, mode, S1_GAP if mode == "gap" else None, os.path.join(root, "align_%s.json" % tag))
                r["align"] = {k: a[k] for k in ("align", "col0", "transrot", "gap_classes") if k in a}
            except Exception as e:                                                        # noqa: BLE001
                r["align"] = {"error": repr(e)[:300]}
        rep["legs"][tag] = r
        log("LEG %s %s" % (tag, json.dumps({k: v for k, v in r.items() if k not in ("align", "leg_gate_call")}, default=str)))
    G["H LabVIEW gone at end"] = not LG.lv_running()
    rep["gates"] = G
    json.dump(rep, open(os.path.join(root, "p6fix_legs.json"), "w", encoding="utf-8"), indent=1, default=str)
    for k, v in G.items():
        print("GATE %-80s %s" % (k, "PASS" if v else "FAIL"), flush=True)
    return 0 if all(G.values()) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
