# ---
# labview: read
# hardware: camera
# offline-args: --dry
# ---
r"""p64_leg - ONE P6-4 leg (plan section 3 item 2): runs the unchanged leg script `tools/bench/diag_c104_leg.py` (v5 + drive_m8:
byte copy of --src, picks, Done, bandpass, save dialog, L11, stop, G92/G93; v5 G0 = the approved per-leg `motor_gate --session
start`, `user_notes.md:3`) in a CHILD process, then judges the leg from its files. Nothing of the leg script is copied:
  child   pre-imports drive_m8 with the argv diag_c104_leg gives it (diag_c104_leg.py:33) so that, with --fracs-json, the bead-map
          picks replace drive_m8.FRACS_ALL[:N] in place (drive_m8.py:88 sets v5.PICK_FRACS from it), then runs diag_c104_leg.py
          with runpy. Without --fracs-json the picks are drive_m8's 15 fixed fractions (the earlier ABBA's).
  parent  after the child: leg.json -> gates of plan 5.4 / 9.2 (D1, F1, F2 RECORDED only, section 3 items 1-2):
          L1 drive_m8 M-gates (M2 = L7 + L9 + L11 for --picks N)   L2 leg PM gates H1 H2 U1 P1 (U2 reported, D1 recorded)
          L3 picks registered (tra) == panels closed (bandpass answered) == N   L4 tra cols == 3 + 3N and column 0 strictly increasing
          L5 v5 steps: every step passes except run1.L8 (the 3-panel contract, plan 5.4)   L6 0 TIFFs   L7 TMX 39 after
          lost = column-0 gaps (p64_sum.run_sum, the same formula for both arms); the `Total Lost Frames` indicator recorded beside it.
The caller (p64_abba.py) owns the leg-start refusals, the VISA precheck and the LabVIEW-gone wait; this file never runs motor_gate.
    py -u tools/bench/lean_bench/p64_leg.py --src <vi> --picks 15 --run-s 120 --hz 90 --out <dir> [--fracs-json <beadmap json>]
    py -u tools/bench/lean_bench/p64_leg.py --dry [--from-leg <recorded leg dir>]   (no child: post-processing + the pick injection)"""
import json, os, runpy, subprocess, sys                                                   # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); BENCH = os.path.dirname(HERE); ROOT = os.path.dirname(os.path.dirname(BENCH))
sys.path.insert(0, HERE); sys.path.insert(0, BENCH); sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P, p64_sum as PS, p6close_sum                                         # noqa: E401,E402
LEG_PY = os.path.join(BENCH, "diag_c104_leg.py")
REC_LEG = os.path.join(HERE, "out_p6close", "legs", "W100_a1")


def load_fracs(path, npick):
    """The bead map's picks as [(fx, fy)] * npick (p64_beadmap.py json key 'picks_frac')."""
    f = [tuple(map(float, p)) for p in json.load(open(path, encoding="utf-8"))["picks_frac"]]
    assert len(f) == npick and all(0.0 < x < 1.0 and 0.0 < y < 1.0 for x, y in f), "bead map must hold %d fractions in (0,1)" % npick
    return f


def inject(src, npick, run_s, fracs):
    """Import drive_m8 under the leg argv and put `fracs` into FRACS_ALL[:npick] in place; returns the module."""
    keep = sys.argv
    sys.argv = [LEG_PY, "--leg", "replay_s1", "--src", src, "--picks", str(npick), "--run-s", str(run_s)]
    import drive_m8
    sys.argv = keep
    if fracs:
        drive_m8.FRACS_ALL[:npick] = list(fracs)
    return drive_m8


def child(av):
    arg = lambda k, d=None: av[av.index(k) + 1] if k in av else d                        # noqa: E731
    src, npick, run_s, out = arg("--src"), int(arg("--picks")), arg("--run-s"), arg("--out")
    fr = load_fracs(arg("--fracs-json"), npick) if arg("--fracs-json") else None
    m = inject(src, npick, run_s, fr)
    print("[p64 leg child] picks %s" % (m.FRACS_ALL[:npick],), flush=True)
    sys.argv = [LEG_PY, "--src", src, "--picks", str(npick), "--run-s", str(run_s), "--out", out]
    runpy.run_path(LEG_PY, run_name="__main__")                                          # ends the process (os._exit in the leg script)


def judge(out, npick, hz, run_s):
    """The leg's gates from <out>/leg.json (plan 5.4 / 9.2). Returns (gates, facts)."""
    lj = os.path.join(out, "leg.json")
    j = json.load(open(lj, encoding="utf-8")) if os.path.isfile(lj) else {}
    F, pm = j.get("facts") or {}, j.get("pm") or {}
    rs = PS.run_sum(F.get("run_dir") or "", npick, hz, run_s) if F.get("run_dir") else {"error": "no run_dir"}
    fd = F.get("frames_delta")
    fails = list(F.get("v5_failing") or [])
    G = {"L0 leg.json read": bool(j),
         "L1 drive_m8 M-gates": j.get("drive_m8_ok") is True,
         "L2 leg PM gates H1 H2 U1 P1": all(v for k, v in pm.items() if k[:2] in ("H1", "H2", "U1", "P1")) and len(pm) > 0,
         "L3 picks registered == panels closed == %d" % npick: F.get("picks_registered_tra") == npick and F.get("bandpass_answered") == npick,
         "L4 tra cols 3+3N, column 0 strictly increasing": rs.get("cols_eq_3_3N") is True and rs.get("strictly_increasing") is True,
         "L5 v5 steps all pass except run1.L8": bool(F) and all(s == "run1.L8" for s in fails),
         "L6 0 TIFFs": F.get("tiffs") == 0,
         "L7 TMX 39 after": F.get("motor_tmx_after") == 39.0}
    facts = {"run_dir": F.get("run_dir"), "lost_col0": rs.get("lost"), "rows": rs.get("rows"), "steps": rs.get("steps"),
             "lost_indicator": F.get("lost"), "frames_delta": fd, "measured_hz": round(fd / float(run_s), 2) if isinstance(fd, (int, float)) and fd else None,
             "picks_registered_tra": F.get("picks_registered_tra"), "picks_clicked": len(F.get("clicks") or []), "bandpass_answered": F.get("bandpass_answered"), "v5_failing": fails,
             "recorded_only": {k: v for k, v in pm.items() if k[:2] in ("D1", "U2")}, "tmx_after": F.get("motor_tmx_after"),
             "frame_at_stop": p6close_sum.leg_facts(lj).get("frame_at_stop") if j else None, "sum": rs}
    return G, facts


def parent(av):
    arg = lambda k, d=None: av[av.index(k) + 1] if k in av else d                        # noqa: E731
    npick, run_s, hz = int(arg("--picks", 15)), float(arg("--run-s", 120)), float(arg("--hz", 90))
    G = {}
    if "--dry" in av:
        out = arg("--from-leg", REC_LEG)
        fixed = list(inject("dry.vi", npick, run_s, None).FRACS_ALL[:npick])
        test = [(0.1 + 0.05 * i, 0.9 - 0.05 * i) for i in range(npick)]
        m = inject("dry.vi", npick, run_s, test)
        G["J1 without a bead map FRACS_ALL[:N] = drive_m8's fixed fractions (FRACS6 first)"] = len(fixed) == npick and fixed[:6] == m.FRACS6
        G["J2 with a bead map FRACS_ALL[:N] == the map"] = m.FRACS_ALL[:npick] == test
        m.FRACS_ALL[:npick] = fixed
        print("FIXED PICKS %s" % json.dumps(fixed), flush=True)
    else:
        out = arg("--out"); os.makedirs(out, exist_ok=True)                               # noqa: E702
        cmd = [sys.executable, "-u", os.path.abspath(__file__), "--child"] + [x for x in av if x not in ("--dry",)]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=18 * 60)
            rc, o = r.returncode, (r.stdout or "") + (r.stderr or "")
        except subprocess.TimeoutExpired as e:
            rc, o = "TIMEOUT", str(e.stdout or "")[-4000:]
        open(os.path.join(out, "leg_child.log"), "w", encoding="utf-8").write(o)
        for ln in o.splitlines():
            if ln.startswith(("GATE ", "RESULT ", "REGISTERED", "[p64 leg child]")):
                print("  " + ln[:500], flush=True)
        G["L-1 leg child rc 0"] = rc == 0
    g, facts = judge(out, npick, hz, run_s)
    G.update(g)
    if "--dry" not in av:                                                                 # a dry run writes nothing into the recorded leg dir
        json.dump({"gates": G, "facts": facts, "out": out}, open(os.path.join(out, "p64_leg.json"), "w", encoding="utf-8"), indent=1, default=str)
    print("FACTS %s" % json.dumps({k: v for k, v in facts.items() if k != "sum"}, default=str), flush=True)
    for k, v in G.items():
        print("GATE %-60s %s" % (k, "PASS" if v else "FAIL"), flush=True)
    bad = [k for k, v in G.items() if not v]
    print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None)), flush=True)
    return 1 if bad else 0


if __name__ == "__main__":
    if "--child" in sys.argv:
        child(sys.argv[1:])
    else:
        sys.exit(parent(sys.argv[1:]))
