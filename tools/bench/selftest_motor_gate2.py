"""selftest_motor_gate2.py - NO MOTION, NO PORT, NO LabVIEW. The self-test of the REWORKED gate (2026-09-18),
where the real limits live in the CONTROLLERS and this script only (a) checks the rig state, (b) refuses whole
command CLASSES that would move the fence, and (c) proves by readback that the controller limits are the ones in
tools/bench/motor_limits.json. Replaces tools/bench/selftest_motor_gate.py (deleted with the numeric envelope it
tested: PI 0..39, ASI 1.0 mm from motor_anchor.json, the "fresh read" requirement).

PRIOR ART CHECKED: tools/bench/selftest_motor_gate.py (the file this replaces - its case shape, `asc()`,
`hook_case()` JSON-on-stdin form and the `code=` column spelling are reused), tools/bench/p2_pi_softlimit_test.ps1
and tools/bench/p2_asi_set_limits.ps1 (the measured controller-limit behaviour these cases encode). Nothing else
under tools/ decides a motor command; that is why the gate exists.

PREDICTION CONTRACT (each numbered line is one case; the run FAILS if any case's outcome differs):
  SESSION HOOK, no port (injected sender output):
   1  --session start, both readbacks match the file            rc 0, session file written with limits_readback
   2  --session start, PI readback TMX=52 (mismatch)            rc 3, NO session file
   2b --session start, a PRE-write 'PRELIMITS TMN=0 TMX=39'     rc 3, NO session file, and
      line in front of a MISMATCHED 'LIMITS .. TMX=52'          parse_pi_limits still reads TMX=52
                                                               [2026-09-18, STATUS.md OPEN 55]
   3  --session start, ASI readback SL X off by 0.01 mm         rc 3, NO session file
   3b --session start, the axis is still UNREFERENCED (FRF 0)   rc 3, NO session file  [added after the 15:37
   3c --session start, POS changed during the RON/POS restore   rc 3, NO session file   live run: SPA leaves
                                                                                        the axis unreferenced]
   4  --session end, both releases read back                    rc 0, session file deleted
  EXECUTE PRECONDITIONS:
   5  --execute with no session file                            rc 3, transmit NEVER called
   6  transmit() when the sender reports LIMITS != the file     rc != 0 and the gate says MISMATCH
   7  transmit() when the sender reports LIMITS == the file     the sender's own rc is passed through
  COMMAND CLASS (decide(), injected rig state, no port):
   8  ASI ! HOME H HERE Z ZERO HM AZ SP SS ~ \\ MC SL SU         REFUSE  (15 cases: zero/save shift the fence)
   9  PI GOH FRF FNL FPL DFH RON POS SPA WPA                    REFUSE  (9 cases)
  10  PI MOV 1 40 / MOV 1 45 / MOV 1 5                          ALLOW   - NO numeric envelope here any more;
                                                                        the CONTROLLER answers ERR 7 past TMX
  11  ASI M X=-16475 / M Z=5000000 / R X=8000                   ALLOW
  12  queries PI POS?/TMN?/TMX?, ASI '/','W X', rotor POS       ALLOW
  13  rotor MOVE/PIC -1500/HOME                                 REFUSE  (no envelope ever declared)
  14  rig-state 실험중 / unknown                                 REFUSE  everything
  15  ASI 'BU Y=3' (query-looking WRITE), compound, unknown cmd REFUSE
  16  limits file missing/broken                                REFUSE  (CLI rc 3)
  17  the gate source no longer mentions the anchor or 0..39    (grep assertion)
  HOOK, tools/hooks/guard_bash.py fed a PreToolUse JSON on stdin:
  18  raw-serial one-liner, motor_send_pi.ps1, motor_asi_io.ps1 rc 2
  19  the gateway itself, this self-test, the p2_*.ps1 queries  rc 0

  py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_motor_gate2.log -- py -u tools/bench/selftest_motor_gate2.py
  (the `MATERIAL=1` env prefix this line used to carry is DEAD - `--material` is the only form that runs;
   STATUS.md OPEN 52a)
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import motor_gate as mg  # noqa: E402

GATE = os.path.join(ROOT, "tools", "motor_gate.py")
HOOK = os.path.join(ROOT, "tools", "hooks", "guard_bash.py")
LIMITS = {"pi": {"lo_mm": 0.0, "hi_mm": 39.0, "release_hi_mm": 52.0},
          "asi": {"sl": {"X": -3.8475, "Y": -4.7744}, "su": {"X": 0.1525, "Y": -0.7744},
                  "release": {"sl": -500, "su": 500}},
          "tolerance": 0.001}
rows = []


def asc(s):
    """This console is cp949; a self-test must never die on a character in a message it is reporting."""
    return str(s).encode("ascii", "replace").decode("ascii")


def row(ok, label, dev, what, got, want, reason=""):
    rows.append((bool(ok), label, dev, str(what)[:60], str(got)[:22], str(want)[:22], asc(reason)))


def case(label, device, command, expect_allow, state="assembled"):
    d = mg.decide(device, command, state=state)
    row(d.allowed == expect_allow, label, device, command,
        "ALLOW" if d.allowed else "REFUSE", "ALLOW" if expect_allow else "REFUSE", d.reason)
    return d


def hook_case(label, command, expect_rc, timeout=25000, background=False):
    payload = {"tool_name": "Bash", "tool_input": {"command": command, "timeout": timeout,
                                                   "run_in_background": background}}
    p = subprocess.run([sys.executable, HOOK], input=json.dumps(payload).encode("utf-8"),
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # NOTE the column spelling: bgrun.py's inner-failure scan treats a literal `rc=<non-zero>` anywhere in the
    # output as a failed run, and this self-test's PASSING rows are full of expected non-zero exits.
    row(p.returncode == expect_rc, label, "hook", command, "code=%d" % p.returncode, "code=%d" % expect_rc,
        (p.stderr.decode("utf-8", "replace").strip().splitlines() or [""])[0][:90])


def cli_case(label, argv, expect_rc):
    p = subprocess.run([sys.executable, GATE] + argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    row(p.returncode == expect_rc, label, "cli", " ".join(argv), "code=%d" % p.returncode, "code=%d" % expect_rc,
        (p.stderr.decode("utf-8", "replace").strip().splitlines() or [""])[0][:90])


PI_REF = "REFSTATE RON=0 FRF=1 POS=0.00000 POS_BEFORE=0.00000 ERR=0\n"
PI_OK = "LIMITS TMN=0 TMX=39 SPA15=39 SPA30=0\n" + PI_REF + "RESULT: ok"
PI_BAD = "LIMITS TMN=0 TMX=52 SPA15=52 SPA30=0\n" + PI_REF + "RESULT: ok"
# the axis stayed UNREFERENCED after the restore (the 15:37 failure mode) / the restore SHIFTED the zero
PI_NOREF = "LIMITS TMN=0 TMX=39 SPA15=39 SPA30=0\nREFSTATE RON=0 FRF=0 POS=0.00000 POS_BEFORE=0.00000 ERR=5\nx"
PI_ZEROMOVED = "LIMITS TMN=0 TMX=39 SPA15=39 SPA30=0\nREFSTATE RON=0 FRF=1 POS=1.50000 POS_BEFORE=0.00000 ERR=0\nx"
PI_REL = "LIMITS TMN=0 TMX=52 SPA15=52 SPA30=0\nRESULT: ok"
# 2026-09-18, STATUS.md OPEN 55: motor_send_pi.ps1:52 now also prints a PRE-write `PRELIMITS TMN=..
# TMX=..` line.  It contains the substring "LIMITS TMN=0 TMX=39" and is printed FIRST, so an
# unanchored parse_pi_limits() would verify the limits the controller had ON ARRIVAL instead of the
# ones the hook just installed - and case 2 (PI_BAD, TMX=52) would flip from refuse to accept.
PI_PRE_DECOY = "PRELIMITS TMN=0 TMX=39\n" + PI_BAD
ASI_OK = "LIMITS SL X=-3.847494 Y=-4.774393 SU X=0.152497 Y=-0.774402\nRESULT: ok"
ASI_BAD = "LIMITS SL X=-3.837494 Y=-4.774393 SU X=0.152497 Y=-0.774402\nRESULT: ok"
ASI_REL = "LIMITS SL X=-500 Y=-500 SU X=500 Y=500\nRESULT: ok"


def quiet(*_a, **_k):
    pass


def main():
    tmpdir = tempfile.mkdtemp(prefix="selftest_motor_gate2_")
    sess = os.path.join(tmpdir, "motor_session.json")

    # ---- 1-4 session hooks, injected sender output, no port ----
    rc = mg.session_start(LIMITS, pi_call=lambda *a: (0, PI_OK), asi_call=lambda *a: (0, ASI_OK),
                          session_path=sess, out=quiet)
    wrote = os.path.exists(sess)
    rec = json.load(open(sess, encoding="utf-8")) if wrote else {}
    row(rc == 0 and wrote and rec.get("limits_readback", {}).get("pi", {}).get("TMX") == 39.0,
        "1 start, both readbacks match", "hook", "--session start", "code=%d file=%s" % (rc, wrote), "code=0 file=True",
        json.dumps(rec.get("limits_readback", {}), sort_keys=True))
    os.remove(sess)

    rc = mg.session_start(LIMITS, pi_call=lambda *a: (0, PI_BAD), asi_call=lambda *a: (0, ASI_OK),
                          session_path=sess, out=quiet)
    row(rc == 3 and not os.path.exists(sess), "2 start, PI readback TMX=52", "hook", "--session start",
        "code=%d file=%s" % (rc, os.path.exists(sess)), "code=3 file=False", "mismatched PI readback must refuse")

    rc = mg.session_start(LIMITS, pi_call=lambda *a: (0, PI_PRE_DECOY), asi_call=lambda *a: (0, ASI_OK),
                          session_path=sess, out=quiet)
    rb = mg.parse_pi_limits(PI_PRE_DECOY)
    row(rc == 3 and not os.path.exists(sess) and rb == {"TMN": 0.0, "TMX": 52.0, "SPA15": 52.0, "SPA30": 0.0},
        "2b start, a PRELIMITS line must not be read", "hook", "--session start",
        "code=%d rb=%s" % (rc, rb and rb.get("TMX")), "code=3 rb.TMX=52",
        "the PRE-write line is not the readback: parse_pi_limits is anchored at ^LIMITS")

    rc = mg.session_start(LIMITS, pi_call=lambda *a: (0, PI_OK), asi_call=lambda *a: (0, ASI_BAD),
                          session_path=sess, out=quiet)
    row(rc == 3 and not os.path.exists(sess), "3 start, ASI SL off by 0.01 mm", "hook", "--session start",
        "code=%d file=%s" % (rc, os.path.exists(sess)), "code=3 file=False", "mismatched ASI readback must refuse")

    rc = mg.session_start(LIMITS, pi_call=lambda *a: (0, PI_NOREF), asi_call=lambda *a: (0, ASI_OK),
                          session_path=sess, out=quiet)
    row(rc == 3 and not os.path.exists(sess), "3b start, axis still UNREFERENCED (FRF 0)", "hook",
        "--session start", "code=%d file=%s" % (rc, os.path.exists(sess)), "code=3 file=False",
        "a hook that leaves FRF=0 must refuse: every MOV would answer ERR 5")

    rc = mg.session_start(LIMITS, pi_call=lambda *a: (0, PI_ZEROMOVED), asi_call=lambda *a: (0, ASI_OK),
                          session_path=sess, out=quiet)
    row(rc == 3 and not os.path.exists(sess), "3c start, POS moved during the restore", "hook", "--session start",
        "code=%d file=%s" % (rc, os.path.exists(sess)), "code=3 file=False",
        "the zero must not shift under the ABSOLUTE controller limits")

    mg.session_start(LIMITS, pi_call=lambda *a: (0, PI_OK), asi_call=lambda *a: (0, ASI_OK),
                     session_path=sess, out=quiet)
    rc = mg.session_end(LIMITS, pi_call=lambda *a: (0, PI_REL), asi_call=lambda *a: (0, ASI_REL),
                        session_path=sess, out=quiet)
    row(rc == 0 and not os.path.exists(sess), "4 end releases and deletes", "hook", "--session end",
        "code=%d file=%s" % (rc, os.path.exists(sess)), "code=0 file=False", "release readback 0..52 / +-500")

    # ---- 5 --execute with no session file: transmit must never be reached ----
    called = []
    real_transmit, real_sess, real_pi, real_asi = mg.transmit, mg.SESSION_PATH, mg.PI_SENDER, mg.ASI_IO
    real_run, real_log = mg._run_ps, mg.LOG_PATH
    mg.transmit = lambda *a, **k: (called.append(a), 0)[1]
    mg.SESSION_PATH = os.path.join(tmpdir, "no_such_session.json")
    mg.LOG_PATH = os.path.join(tmpdir, "motor_gate.log")
    mg.PI_SENDER = mg.ASI_IO = os.path.join(tmpdir, "no_such_sender.ps1")   # belt and braces: cannot open a port
    try:
        rc = mg.main(["--device", "pi", "--command", "MOV 1 5", "--execute"])
        row(rc == 3 and not called, "5 execute without a session", "cli", "MOV 1 5 --execute",
            "code=%d calls=%d" % (rc, len(called)), "code=3 calls=0", "no session file => refuse before transmitting")

        # ---- 6/7 transmit()'s own readback re-check, injected sender output ----
        mg.transmit = real_transmit
        mg._run_ps = lambda script, args, timeout=120: (7, PI_BAD + "\nSEND REFUSED: limits do not match the file")
        d = mg.decide("pi", "MOV 1 5", state="assembled")
        rc = mg.transmit("pi", "MOV 1 5", d, LIMITS)
        row(rc != 0, "6 sender readback != file", "cli", "transmit MOV 1 5", "code=%d" % rc, "code!=0",
            "the gate re-checks the sender's LIMITS line")
        mg._run_ps = lambda script, args, timeout=120: (0, PI_OK + "\nRESULT: reached 5")
        rc = mg.transmit("pi", "MOV 1 5", d, LIMITS)
        row(rc == 0, "7 sender readback == file", "cli", "transmit MOV 1 5", "code=%d" % rc, "code=0",
            "matching readback passes the sender's rc through")
    finally:
        mg.transmit, mg.SESSION_PATH, mg.PI_SENDER, mg.ASI_IO = real_transmit, real_sess, real_pi, real_asi
        mg._run_ps, mg.LOG_PATH = real_run, real_log

    # ---- 8 ASI zero/home/save class ----
    for c in ["!", "HOME X", "H X", "HERE X", "Z", "ZERO X", "HM X", "AZ X", "SP", "SS Z", "~", "\\", "MC X",
              "SL X=-9 Y=-9", "SU X=9 Y=9"]:
        case("8 ASI zero/home/save %r" % c, "asi", c, False)
    # ---- 9 PI home/reference/define class ----
    for c in ["GOH", "FRF 1", "FNL 1", "FPL 1", "DFH 1", "RON 1 1", "POS 1 0", "SPA 1 0x15 52", "WPA 100 1 0x15"]:
        case("9 PI home/define %r" % c, "pi", c, False)
    # ---- 10 no numeric envelope in the gate any more ----
    for c in ["MOV 1 5", "MOV 1 40", "MOV 1 45"]:
        case("10 PI %r passes to the controller" % c, "pi", c, True)
    # ---- 11 ASI moves ----
    for c in ["M X=-16475", "M Z=5000000", "R X=8000"]:
        case("11 ASI %r" % c, "asi", c, True)
    # ---- 12 queries ----
    for dev, c in [("pi", "POS?"), ("pi", "TMN?"), ("pi", "TMX?"), ("asi", "/"), ("asi", "W X"), ("rotor", "POS")]:
        case("12 query %s %r" % (dev, c), dev, c, True)
    # ---- 13 rotor motion ----
    for c in ["MOVE 100", "PIC -1500", "HOME"]:
        case("13 rotor %r" % c, "rotor", c, False)
    # ---- 14 rig state ----
    case("14a experiment refuses a move", "pi", "MOV 1 5", False, state="experiment")
    case("14b experiment refuses a query", "pi", "POS?", False, state="experiment")
    case("14c unknown state refuses", "asi", "M X=-16475", False, state="unknown")
    st = mg.rig_state("rig-state: 실험중\n")
    row(st == "experiment", "14d rig_state() reads 실험중", "gate", "rig-state: 실험중", st, "experiment")
    st = mg.rig_state(open(os.path.join(ROOT, "STATUS.md"), encoding="utf-8").read())
    row(st == "assembled", "14e live STATUS.md", "gate", "rig-state:", st, "assembled")
    # ---- 15 write-in-query's clothing, compound, unknown ----
    case("15a ASI 'BU Y=3' is a write", "asi", "BU Y=3", False)
    case("15b compound", "asi", "M X=1 ; M Y=1", False)
    case("15c unknown ASI command", "asi", "FOO", False)
    case("15d unknown PI command", "pi", "BAR", False)
    case("15e unknown device", "piezo", "MOV 1 5", False)

    # ---- 16 limits file missing / broken (CLI) ----
    missing = os.path.join(tmpdir, "no_such_limits.json")
    broken = os.path.join(tmpdir, "broken_limits.json")
    open(broken, "w").write('{"pi": {"lo_mm": 0.0}}')
    cli_case("16a limits file missing", ["--limits", missing, "--device", "pi", "--command", "MOV 1 5"], 3)
    cli_case("16b limits file incomplete", ["--limits", broken, "--device", "pi", "--command", "MOV 1 5"], 3)
    cli_case("16c a normal dry decision", ["--device", "pi", "--command", "MOV 1 5"], 0)
    cli_case("16d a normal refusal", ["--device", "pi", "--command", "GOH"], 3)

    # ---- 17 the deleted envelope is really gone ----
    src = open(GATE, encoding="utf-8").read()
    row("motor_anchor" not in src, "17a no motor_anchor.json", "gate", "grep motor_anchor",
        "motor_anchor" in src, False)
    row("ASI_XY_LIMIT_MM" not in src and "PI_MAX_MM" not in src, "17b no script-side numeric envelope", "gate",
        "grep ASI_XY_LIMIT_MM/PI_MAX_MM", "present" if "PI_MAX_MM" in src else "absent", "absent")
    row(not os.path.exists(os.path.join(HERE, "selftest_motor_gate.py")), "17c old self-test deleted", "gate",
        "tools/bench/selftest_motor_gate.py", "present" if os.path.exists(
            os.path.join(HERE, "selftest_motor_gate.py")) else "absent", "absent")
    row(os.path.exists(os.path.join(HERE, "motor_limits.json")), "17d limits file exists", "gate",
        "tools/bench/motor_limits.json", "present", "present")

    # ---- 18/19 the hook ----
    hook_case("18a raw serial one-liner",
              "powershell -c \"$sp = New-Object System.IO.Ports.SerialPort COM3,115200\"", 2)
    hook_case("18b motor_send_pi.ps1 by hand",
              "powershell -File tools/motor_send_pi.ps1 -Command \"MOV 1 5\" -TokenFile t.tok", 2)
    hook_case("18c motor_asi_io.ps1 by hand", "powershell -File tools/motor_asi_io.ps1 -Mode send", 2)
    hook_case("18d a raw MOV typed into a one-liner", "echo MOV 1 40 > COM3", 2)
    hook_case("19a the gateway itself",
              "py tools/motor_gate.py --device asi --command \"M X=-16475\" --dry-run", 0)
    hook_case("19b the gateway's session hook", "py tools/motor_gate.py --session start", 0)
    hook_case("19c this self-test",
              "MATERIAL=1 py tools/bgrun.py --max-min 5 --log tools/bench/selftest_motor_gate2.log -- "
              "py -u tools/bench/selftest_motor_gate2.py", 0, background=False)
    hook_case("19d p2 PI query script",
              "powershell -NoProfile -ExecutionPolicy Bypass -File tools/bench/p2_pi_query_ron.ps1", 0)
    hook_case("19e p2 ASI query script",
              "powershell -NoProfile -ExecutionPolicy Bypass -File tools/bench/p2_asi_query_limits.ps1", 0)
    hook_case("19f grep of a blocked name", "grep -n SerialPort tools/motor_send_pi.ps1", 0)

    bad = [r for r in rows if not r[0]]
    print("\n%-4s %-38s %-6s %-60s %-22s %-22s %s" % ("ok", "case", "dev", "command", "got", "want", "reason"),
          flush=True)
    for ok, label, dev, what, got, want, reason in rows:
        print(asc("%-4s %-38s %-6s %-60s %-22s %-22s %s" % ("PASS" if ok else "FAIL", label, dev, what, got, want,
                                                            reason[:100])), flush=True)
    print("\n%d/%d PASS, %d FAIL" % (len(rows) - len(bad), len(rows), len(bad)), flush=True)
    for r in bad:
        print(asc("  FAILING: %s | %s | got %s want %s | %s" % (r[1], r[3], r[4], r[5], r[6])), flush=True)
    print("NO MOTION COMMAND WAS SENT AND NO PORT WAS OPENED BY THIS RUN.", flush=True)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
