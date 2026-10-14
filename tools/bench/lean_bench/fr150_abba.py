# ---
# labview: read
# hardware: camera
# ---
r"""fr150_abba - fr90_abba.py (NOT edited; it is p64_abba.py unchanged + C1, with the leg script fr90_leg.py = p64_leg + the
`# of Auto-Reset` read + the C2 display-box check) plus the 150 Hz rate-line handling of task fr150 step 3:
  R1  before EVERY leg (and in the dry): the leg is REFUSED if <obs dir>\configgrab_rate150.txt exists (a stale line would be
      read as this leg's). Added to p64_abba's leg-start refusals, after C1.
  R2  after EVERY leg (any arm; after LabVIEW is gone, T6): the file is MOVED (never deleted) into the leg folder; recorded:
      line count, the fields, md5 before = after, source gone -> <leg>\fr150_rate.json. Rate gate (added to the leg's
      p64_leg.json gates, so p64_abba's "L leg gates all pass" includes it): exactly 1 line, readback within 150 +- 0.1,
      error code 0 - else the leg is INVALID (the 150 Hz setting did not take).
Same arguments as p64_abba.py (without --live = dry).
    py -u tools/bench/lean_bench/fr150_abba.py --a-src <vi> --a-md5 <m> --b-src <vi> --b-md5 <m> --o-src <vi> --o-md5 <m>
          --hz 150 --run-s 120 --order ABBAO [--live] --out-root <absolute dir under out_p64>
    py tools/bench/lean_bench/fr150_abba.py --r-selftest     (offline, TEMP stand-in paths; the real obs dir untouched)"""
import hashlib, json, os, shutil, sys, tempfile                                            # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fr90_abba as F9                                                                    # noqa: E402 (sets LEG_PY = fr90_leg.py, adds C1)
PA = F9.PA
RATE_NAME = "configgrab_rate150.txt"
RATE_HZ, RATE_TOL = 150.0, 0.1
_c1_start_checks = PA.start_checks                                                       # fr90_abba's (C1 + p64_abba's)
_orig_keep = PA.M8L.keep_leg_files


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.isfile(p) else None


def r1_check(obs_dir):
    p = os.path.join(obs_dir, RATE_NAME)
    ok = not os.path.exists(p)
    print("GATE R1 %s absent before the leg: %s" % (RATE_NAME, "PASS" if ok else "FAIL (stale file, %s lines)" % PA.lines_of(p)), flush=True)
    return [] if ok else ["R1 stale rate line: %s exists (%s lines) - would be read as this leg's" % (p, PA.lines_of(p))]


def start_checks(cfg, arm, src, pin):
    return _c1_start_checks(cfg, arm, src, pin) + r1_check(cfg["obs_dir"])


PA.start_checks = start_checks                                                           # run_leg and the dry look it up at call time


def rate_gate(lines):
    """(ok, fields, why) for the rate file's non-empty lines: exactly 1 line, readback within 150 +- 0.1, code 0."""
    if len(lines) != 1:
        return False, [ln.split() for ln in lines], "%d lines, not exactly 1" % len(lines)
    f = lines[0].split()
    try:
        req, rb, code = float(f[0]), float(f[1]), int(float(f[3]))
    except (IndexError, ValueError) as e:
        return False, f, "unreadable line (%s)" % e
    ok = abs(rb - RATE_HZ) <= RATE_TOL and code == 0
    return ok, f, "requested %s readback %s exposure %s code %s tick %s" % (req, rb, f[2], code, f[4] if len(f) > 4 else "?")


def r2_move(obs_dir, out):
    """Move the rate file into the leg folder (never delete) and judge it. Returns the record written to <out>\\fr150_rate.json."""
    src, dst = os.path.join(obs_dir, RATE_NAME), os.path.join(out, RATE_NAME)
    rec = {"from": src, "to": dst, "exists": os.path.exists(src)}
    lines = []
    if rec["exists"]:
        assert not os.path.exists(dst), "refusing to overwrite %s" % dst
        rec["md5"] = md5(src)
        lines = [ln for ln in open(src, encoding="utf-8", errors="replace").read().splitlines() if ln.strip()]
        shutil.move(src, dst)
        rec["md5_after"], rec["src_gone"] = md5(dst), not os.path.exists(src)
    rec["lines"] = len(lines)
    ok, fields, why = rate_gate(lines)
    moved_ok = (not rec["exists"]) or (rec["md5"] == rec["md5_after"] and rec["src_gone"])
    rec.update(fields=fields, why=why, rate_ok=ok, moved_ok=moved_ok, gate=bool(ok and moved_ok))
    json.dump(rec, open(os.path.join(out, "fr150_rate.json"), "w", encoding="utf-8"), indent=1)
    print("GATE R2 rate line moved + 1 line, readback 150 +- 0.1, code 0: %s  %s; moved md5 %s -> %s" % (
        "PASS" if rec["gate"] else "FAIL (leg INVALID)", why, rec.get("md5"), rec.get("md5_after")), flush=True)
    return rec


def _keep(out, picks, run_s, t0, log=print):
    """p64_abba's run_leg calls this right after T6 (LabVIEW gone) and P2, before it reads p64_leg.json: R2 goes here."""
    kept = _orig_keep(out, picks, run_s, t0, log)
    rec = r2_move(CFG_OBS[0], out)
    jp = os.path.join(out, "p64_leg.json")
    if os.path.isfile(jp):
        j = json.load(open(jp, encoding="utf-8"))
        j["facts"]["rate_line"] = {k: rec.get(k) for k in ("lines", "fields", "why", "md5", "md5_after")}
        j["gates"]["R2 rate line: 1 line, readback 150 +- 0.1, code 0, moved"] = rec["gate"]
        json.dump(j, open(jp, "w", encoding="utf-8"), indent=1, default=str)
    return kept


CFG_OBS = [PA.REAL["obs_dir"]]
PA.M8L.keep_leg_files = _keep


def selftest():
    """R1 / R2 on TEMP stand-ins (never the real obs dir), then fr90_abba's C1 self-test."""
    real = os.path.join(PA.REAL["obs_dir"], RATE_NAME)
    real0 = os.path.exists(real)
    tmp = tempfile.mkdtemp(prefix="fr150_rself_")
    bad = 0

    def case(name, got, want):
        nonlocal bad
        bad += got != want
        print("CASE %-58s got=%s want=%s %s" % (name, got, want, "OK" if got == want else "WRONG"), flush=True)
    try:
        obs = os.path.join(tmp, "standin_obs"); os.makedirs(obs)                          # noqa: E702
        assert os.path.normcase(obs) != os.path.normcase(PA.REAL["obs_dir"])
        case("R1 file absent -> leg may start", r1_check(obs) == [], True)
        open(os.path.join(obs, RATE_NAME), "w").write("150\t150\t1909\t0\t24904580\n")
        case("R1 stale file present -> REFUSED", bool(r1_check(obs)), True)
        cfg = {"stop": os.path.join(tmp, "no_stop"), "session": __file__, "obs_dir": obs, "picklog": os.path.join(tmp, "no_picklog"),
               "out_root": os.path.join(F9.OUT_P64, "fr150", "selftest"),
               "hooks": {"rig": lambda: "assembled", "lv": lambda: False}}
        why = PA.start_checks(cfg, "B", __file__, md5(__file__))
        case("R1 through p64_abba.start_checks (+C1) -> only R1", [w[:2] for w in why], ["R1"])
        for name, text, want in (("R2 good line 150 150 1909 0", "150\t150\t1909\t0\t24904580\n", True),
                                 ("R2 two lines (two camera opens)", "150\t150\t1909\t0\t1\n150\t150\t1909\t0\t2\n", False),
                                 ("R2 readback 90.0009 (setting did not take)", "150\t90.0009\t1909\t0\t1\n", False),
                                 ("R2 readback 150.2 (outside +-0.1)", "150\t150.2\t1909\t0\t1\n", False),
                                 ("R2 error code -1074360311", "150\t150\t1909\t-1074360311\t1\n", False),
                                 ("R2 file missing (0 lines)", None, False)):
            leg = tempfile.mkdtemp(prefix="leg_", dir=tmp)
            p = os.path.join(obs, RATE_NAME)
            if os.path.exists(p):
                os.remove(p)                                                              # stand-in only (TEMP)
            if text is not None:
                open(p, "w").write(text)
            m0 = md5(p)
            rec = r2_move(obs, leg)
            case(name + " -> gate", rec["gate"], want)
            if text is not None:
                case("   moved: src gone, md5 equal, in the leg folder", (rec["src_gone"], rec["md5_after"] == m0,
                                                                        os.path.isfile(os.path.join(leg, RATE_NAME))), (True, True, True))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    case("real obs dir untouched (%s exists before = after)" % RATE_NAME, os.path.exists(real), real0)
    print("R SELFTEST %s" % ("PASS" if not bad else "FAIL (%d wrong)" % bad), flush=True)
    rc = F9.selftest()
    return 1 if (bad or rc) else 0


if __name__ == "__main__":
    sys.exit(selftest() if "--r-selftest" in sys.argv else PA.main(sys.argv[1:]))
