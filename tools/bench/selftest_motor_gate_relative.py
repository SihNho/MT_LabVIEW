# ---
# labview: none
# hardware: none
# ---
"""selftest_motor_gate_relative.py - NO MOTION, NO PORT, NO LabVIEW. Self-test of the ASI RELATIVE window (user
2026-10-15 "그냥 실행 당시 위치를 기준으로 하자"): the session-start hook reads the ASI X/Y (read-only) and sets
SL/SU = position +- half_width_mm. Every controller call is injected. The absolute path keeps its own self-test
(tools/bench/selftest_motor_gate2.py, which uses its own absolute LIMITS and is unaffected).

  R1 load_limits: relative + half widths 2/2 accepted; half width 0, 10 or a bogus mode -> None (everything refused)
  R2 session start, read X=-52899 Y=-41518 (the 2026-10-15 joystick spot) -> rc 0; SL X -7.2899 Y -6.1518,
     SU X -3.2899 Y -2.1518 written and read back; the session file records the window and its centre
  R3 the position read fails (rc 6 / no FRESH line) -> rc 3, ASI limits NOT written, no session file
  R4 absolute mode: no position read; the file's sl/su are written
  R5 asi_window(): relative -> the open session's window; relative without a session -> (None, None); absolute -> file
Ends with a RESULT line.
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import motor_gate as mg  # noqa: E402

PI_TEXT = ("before: POS?=1=0.00000 TMN?=1=0.00000 TMX?=1=52.00000 ERR?=0\nPRELIMITS TMN=0 TMX=52\n"
           "LIMITS TMN=0 TMX=39 SPA15=39 SPA30=0\nREFERENCE: POS before=0 -> SENT FNL 1\n"
           "REFSTATE RON=1 FRF=1 POS=0 POS_BEFORE=0 ERR=0 travelled=0.000\n"
           "VERIFY: commanded=2 readback=2.0001 delta=0.0001 err=0 -> OK\n"
           "VERIFY: commanded=0 readback=0 delta=0.0000 err=0 -> OK\n"
           "VERIFY-RESULT: OK - reference move done and the stage follows commands\n"
           "LIMITS TMN=0 TMX=39 SPA15=39 SPA30=0\nRESULT: controller limits set (mode limits-set)\n")
BASE = {"pi": {"lo_mm": 0.0, "hi_mm": 39.0, "release_hi_mm": 52.0},
        "asi": {"sl": {"X": -3.8475, "Y": -4.7744}, "su": {"X": 0.1525, "Y": -0.7744},
                "release": {"sl": -500, "su": 500}},
        "tolerance": 0.001}


def rel(hw=(2.0, 2.0), mode="relative"):
    lim = json.loads(json.dumps(BASE))
    lim["asi"]["mode"] = mode
    lim["asi"]["half_width_mm"] = {"X": hw[0], "Y": hw[1]}
    return lim


def main():
    ok, n, rows = 0, 0, []

    def check(name, cond, got=""):
        nonlocal ok, n
        n += 1
        ok += bool(cond)
        rows.append("%s  %s %s" % ("PASS" if cond else "FAIL", name, got))
        print(rows[-1])

    tmp = tempfile.mkdtemp()

    def lim_file(obj):
        p = os.path.join(tmp, "lim_%d.json" % len(os.listdir(tmp)))
        json.dump(obj, open(p, "w"))
        return p

    # R1
    check("R1a relative 2/2 accepted", mg.load_limits(lim_file(rel())) is not None)
    check("R1b half width 0 refused", mg.load_limits(lim_file(rel((0, 2)))) is None)
    check("R1c half width 10 refused", mg.load_limits(lim_file(rel((10, 2)))) is None)
    check("R1d bogus mode refused", mg.load_limits(lim_file(rel(mode="floating"))) is None)
    check("R1e absolute file (no mode) still accepted", mg.load_limits(lim_file(BASE)) is not None)

    # R2
    written = []

    def asi_call(mode, sl, su):
        written.append((mode, sl, su))
        return 0, ("LIMITS SL X=%s Y=%s SU X=%s Y=%s\nposition after (must be unchanged): X=-52899 Y=-41518\n"
                   "RESULT: controller limits set (mode %s)\n" % (sl["X"], sl["Y"], su["X"], su["Y"], mode))

    sess = os.path.join(tmp, "sess.json")
    rc = mg.session_start(rel(), pi_call=lambda m, lo, hi: (0, PI_TEXT), asi_call=asi_call, session_path=sess,
                          out=lambda s: None, asi_read=lambda: (0, "FRESH X=-52899 Y=-41518\n"))
    want_sl, want_su = {"X": -7.2899, "Y": -6.1518}, {"X": -3.2899, "Y": -2.1518}
    got = written[-1] if written else None
    check("R2a relative start rc 0", rc == 0, rc)
    check("R2b window = position +- 2 mm", got and got[1] == want_sl and got[2] == want_su, got)
    s = json.load(open(sess)) if os.path.exists(sess) else {}
    check("R2c session records the window and centre",
          s.get("asi_window", {}).get("mode") == "relative"
          and s.get("asi_window", {}).get("center_units") == {"X": -52899.0, "Y": -41518.0}
          and s.get("limits_file", {}).get("asi") == {"sl": want_sl, "su": want_su})

    # R3
    for label, reply in (("rc 6", (6, "READ FAILED\n")), ("no FRESH line", (0, "garbage\n"))):
        written.clear()
        sess3 = os.path.join(tmp, "sess3.json")
        rc = mg.session_start(rel(), pi_call=lambda m, lo, hi: (0, PI_TEXT), asi_call=asi_call, session_path=sess3,
                              out=lambda s: None, asi_read=lambda r=reply: r)
        check("R3 read fails (%s) -> rc 3, no ASI write, no session" % label,
              rc == 3 and not written and not os.path.exists(sess3), (rc, len(written)))

    # R4
    written.clear()
    reads = []
    sess4 = os.path.join(tmp, "sess4.json")
    rc = mg.session_start(json.loads(json.dumps(BASE)), pi_call=lambda m, lo, hi: (0, PI_TEXT), asi_call=asi_call,
                          session_path=sess4, out=lambda s: None, asi_read=lambda: (reads.append(1), (0, ""))[1])
    check("R4 absolute: no read, file window written",
          rc == 0 and not reads and written and written[-1][1] == BASE["asi"]["sl"] and written[-1][2] == BASE["asi"]["su"])

    # R5
    check("R5a relative -> session window", mg.asi_window(rel(), s) == (want_sl, want_su))
    check("R5b relative without a session -> (None, None)", mg.asi_window(rel(), {}) == (None, None))
    check("R5c absolute -> file window", mg.asi_window(BASE, {}) == (BASE["asi"]["sl"], BASE["asi"]["su"]))

    print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if ok == n else "FAIL",
                                  "gates": {"pass": ok, "fail": n - ok}, "first_fail": None, "artefacts": []}))
    return 0 if ok == n else 1


if __name__ == "__main__":
    sys.exit(main())
