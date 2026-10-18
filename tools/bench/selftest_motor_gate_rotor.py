# ---
# labview: none
# hardware: none
# ---
"""selftest_motor_gate_rotor.py - NO MOTION, NO PORT, NO LabVIEW. Self-test of the ROTOR relative envelope
(user 2026-10-19 "-5바퀴 에서 + 5바퀴", "기계 리턴은 펄스로 주는지라 각도로 환산해야함"): Autonics PMC-2HS X axis,
0.72 deg/pulse, window = POS at session start +- 2500 pulses. Every port call is injected; the sender script is
never started (a fake `run` stands in for tools/motor_rotor_io.ps1).

  L  load_limits: the live file (rotor block) accepted; half width 2501 / 0, deg 0.70, speed 101, mode 'controller',
     a float half width -> whole file refused; a file without a rotor block still accepted
  S  sign: FFFFFFF6 -> -10 pulses -> -7.2 deg; FFFFFA24 -> -1500 (-1080 deg); 000186A0 -> 100000; 7FFFFFFF;
     80000000; a 4-digit field -> None; 'POS FFFFFFF6,00000000' -> -10; the sender's FRESH line accepted only if
     the gate's own parse of RAW agrees
  W  session start: FRESH POS=1000 -> window -1500..3500 recorded; read fails -> rc 0, rotor_window None;
     no rotor block -> rotor read never called, no rotor_window key
  A  absolute PAB in/out of the window, both signs (edges inclusive)
  R  relative PIC with a fresh position in/out, both signs; without one: |step| <= 5000 allowed-by-class,
     larger refused; rotor_target_check refuses a PIC with no fresh position
  Y  any Y component refused
  F  fence class refused: CLL CLR HOM OGE IHS IXS RST PRG PST JOG SSM OUT STO, SCI write
  Q  reads allowed: POS SPD VER ERD X INR X IXR X7A IHR XE6; IXR Y7A refused
  V  speed cap: SPD 100 allowed, 101 / 0 / '100,100' refused
  M  missing session / rotor_window None / half-width mismatch -> refused
  E  rig state experiment / unknown -> refused (move and query); compound refused
  T  transmit_rotor (fake sender): in-window passes rc through; sender says rc 0 but its FRESH puts the target
     outside -> gate rc 3; FRESH sign disagreement -> rc 3; no session -> rc 3 and the sender is never run
  C  CLI --execute rotor with no session -> rc 3, transmit never called
Ends with a RESULT line.
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import motor_gate as mg  # noqa: E402

PI_TEXT = ("before: POS?=1=0.00000 TMN?=1=0.00000 TMX?=1=52.00000 ERR?=0\nPRELIMITS TMN=0 TMX=52\n"
           "LIMITS TMN=0 TMX=39 SPA15=39 SPA30=0\nREFERENCE: POS before=0 -> SENT FNL 1\n"
           "REFSTATE RON=1 FRF=1 POS=0 POS_BEFORE=0 ERR=0 travelled=0.000\n"
           "VERIFY-RESULT: OK - reference move done and the stage follows commands\n"
           "LIMITS TMN=0 TMX=39 SPA15=39 SPA30=0\nRESULT: controller limits set (mode limits-set)\n")
ASI_TEXT = "LIMITS SL X=-3.8475 Y=-4.7744 SU X=0.1525 Y=-0.7744\nRESULT: ok\n"
BASE = {"pi": {"lo_mm": 0.0, "hi_mm": 39.0, "release_hi_mm": 52.0},
        "asi": {"sl": {"X": -3.8475, "Y": -4.7744}, "su": {"X": 0.1525, "Y": -0.7744},
                "release": {"sl": -500, "su": 500}},
        "rotor": {"mode": "relative", "half_width_pulses": 2500, "deg_per_pulse": 0.72, "max_speed": 100},
        "tolerance": 0.001}
FRESH_1000 = "FRESH RAW='POS 000003E8,00000000' POS=1000\n"


def lim(**rotor):
    x = json.loads(json.dumps(BASE))
    x["rotor"].update(rotor)
    return x


def main():
    ok, n = 0, 0

    def check(name, cond, got=""):
        nonlocal ok, n
        n += 1
        ok += bool(cond)
        print(("PASS" if cond else "FAIL") + "  " + name + "  " + str(got).encode("ascii", "replace").decode())

    tmp = tempfile.mkdtemp(prefix="selftest_rotor_")

    def lim_file(obj):
        p = os.path.join(tmp, "lim_%d.json" % len(os.listdir(tmp)))
        with open(p, "w") as f:
            json.dump(obj, f)
        return p

    # ---- L ----
    live = mg.load_limits()
    check("L1 live motor_limits.json accepted with rotor block",
          live is not None and live.get("rotor", {}).get("half_width_pulses") == 2500
          and live["rotor"]["max_speed"] == 100 and live["rotor"]["deg_per_pulse"] == 0.72, live and live.get("rotor"))
    for label, bad in (("half width 2501", lim(half_width_pulses=2501)), ("half width 0", lim(half_width_pulses=0)),
                       ("half width 2500.0 float", lim(half_width_pulses=2500.0)),
                       ("deg 0.70", lim(deg_per_pulse=0.70)), ("speed 101", lim(max_speed=101)),
                       ("mode controller", lim(mode="controller"))):
        check("L2 %s -> file refused" % label, mg.load_limits(lim_file(bad)) is None)
    norot = json.loads(json.dumps(BASE))
    del norot["rotor"]
    check("L3 no rotor block -> still accepted", mg.load_limits(lim_file(norot)) is not None)

    # ---- S ----
    p = mg.rotor_hex_to_pulses("FFFFFFF6")
    check("S1 FFFFFFF6 -> -10 pulses -> -7.2 deg", p == -10 and abs(p * 0.72 - (-7.2)) < 1e-9, p)
    check("S2 FFFFFA24 -> -1500 (-1080 deg)", mg.rotor_hex_to_pulses("FFFFFA24") == -1500)
    check("S3 000186A0 -> 100000", mg.rotor_hex_to_pulses("000186A0") == 100000)
    check("S4 7FFFFFFF / 80000000", mg.rotor_hex_to_pulses("7FFFFFFF") == 2147483647
          and mg.rotor_hex_to_pulses("80000000") == -2147483648)
    check("S5 4-digit field -> None", mg.rotor_hex_to_pulses("FFF6") is None)
    check("S6 POS FFFFFFF6,00000000 -> -10", mg.parse_rotor_pos_reply("POS FFFFFFF6,00000000") == -10)
    check("S7 FRESH line agreeing -> -10", mg.parse_rotor_fresh("FRESH RAW='POS FFFFFFF6,00000000' POS=-10") == -10)
    check("S8 FRESH unsigned misread (4294967286) -> None",
          mg.parse_rotor_fresh("FRESH RAW='POS FFFFFFF6,00000000' POS=4294967286") is None)

    # ---- W ----
    mg.time.sleep = lambda *_a: None
    sess = os.path.join(tmp, "sess.json")
    rc = mg.session_start(BASE, pi_call=lambda *a: (0, PI_TEXT), asi_call=lambda *a: (0, ASI_TEXT),
                          session_path=sess, out=lambda s: None, rotor_read=lambda: (0, FRESH_1000))
    rec = json.load(open(sess)) if os.path.exists(sess) else {}
    w = rec.get("rotor_window") or {}
    check("W1 start rc 0, window -1500..3500 around 1000",
          rc == 0 and w.get("center_pulses") == 1000 and w.get("lo_pulses") == -1500 and w.get("hi_pulses") == 3500,
          (rc, w))
    sess_f = os.path.join(tmp, "sess_f.json")
    rc = mg.session_start(BASE, pi_call=lambda *a: (0, PI_TEXT), asi_call=lambda *a: (0, ASI_TEXT),
                          session_path=sess_f, out=lambda s: None, rotor_read=lambda: (6, "READ FAILED\n"))
    rec_f = json.load(open(sess_f)) if os.path.exists(sess_f) else {}
    check("W2 rotor read fails -> PI/ASI session ok, rotor_window None",
          rc == 0 and "rotor_window" in rec_f and rec_f["rotor_window"] is None, rc)
    called = []
    sess_n = os.path.join(tmp, "sess_n.json")
    rc = mg.session_start(norot, pi_call=lambda *a: (0, PI_TEXT), asi_call=lambda *a: (0, ASI_TEXT),
                          session_path=sess_n, out=lambda s: None,
                          rotor_read=lambda: (called.append(1), (0, FRESH_1000))[1])
    rec_n = json.load(open(sess_n)) if os.path.exists(sess_n) else {}
    check("W3 no rotor block -> no read, no rotor_window key", rc == 0 and not called and "rotor_window" not in rec_n)

    def dec(cmd, state="assembled", session=rec, fresh=None, limits=BASE):
        return mg.decide("rotor", cmd, state=state, limits=limits, session=session, fresh_pos=fresh)

    # ---- A ----
    for c, want in (("PAB 3500", True), ("PAB 3501", False), ("PAB -1500", True), ("PAB -1501", False),
                    ("PAB 0", True), ("PAB -10", True), ("PAB 100000", False), ("PAB -7200", False)):
        d = dec(c)
        check("A %s -> %s" % (c, "ALLOW" if want else "REFUSE"), d.allowed == want, d.reason)

    # ---- R ----
    for c, want in (("PIC 2500", True), ("PIC 2501", False), ("PIC -2500", True), ("PIC -2501", False)):
        d = dec(c, fresh=1000)
        check("R1 %s from fresh 1000 -> %s" % (c, "ALLOW" if want else "REFUSE"), d.allowed == want, d.reason)
    d = dec("PIC 1000", fresh=3000)
    check("R2 PIC +1000 from fresh 3000 (target 4000) -> REFUSE", not d.allowed, d.reason)
    d = dec("PIC -1500")
    check("R3 PIC -1500 without a fresh position -> allowed by class, needs_fresh_pos",
          d.allowed and d.detail.get("needs_fresh_pos"), d.reason)
    for c in ("PIC 5001", "PIC -5001"):
        d = dec(c)
        check("R4 %s larger than the whole window -> REFUSE" % c, not d.allowed, d.reason)
    okc, _t, msg = mg.rotor_target_check(rec["rotor_window"], "rel", 10, None)
    check("R5 rotor_target_check PIC without fresh -> refused", not okc, msg)

    # ---- Y ----
    for c in ("PAB 10, -1", "PAB , 1500", "PIC , -1500", "PIC 10,10", "PAB X=10"):
        d = dec(c, fresh=1000)
        check("Y %r refused" % c, not d.allowed, d.reason)

    # ---- F ----
    for c in ("CLL X", "CLL XY", "CLR X", "HOM X", "OGE X", "IHS XE6,0064", "IXS X7A,00000064", "RST",
              "PRG XY00", "PST X 00", "JOG +X", "SSM X1", "OUT 0001", "STO X", "SCI 19200,8,1,0"):
        d = dec(c)
        check("F %r refused" % c, not d.allowed, d.reason)

    # ---- Q ----
    for c in ("POS", "SPD", "VER", "ERD X", "INR X", "IXR X7A", "IHR XE6"):
        d = dec(c, session={})
        check("Q %r allowed (no session needed)" % c, d.allowed and d.detail.get("kind") == "query", d.reason)
    check("Q IXR Y7A refused", not dec("IXR Y7A").allowed)

    # ---- V ----
    for c, want in (("SPD 100", True), ("SPD 50", True), ("SPD 101", False), ("SPD 0", False),
                    ("SPD 100,100", False), ("SPD 8000", False)):
        d = dec(c)
        check("V %s -> %s" % (c, "ALLOW" if want else "REFUSE"), d.allowed == want, d.reason)

    # ---- M ----
    check("M1 no session -> PAB 0 refused", not dec("PAB 0", session={}).allowed)
    check("M2 rotor_window None -> refused", not dec("PAB 0", session=rec_f).allowed)
    check("M3 window half width != file -> refused", not dec("PAB 0", limits=lim(half_width_pulses=1000)).allowed)
    check("M4 limits without rotor block -> refused", not dec("PAB 0", limits=norot).allowed)

    # ---- E ----
    check("E1 experiment refuses a move", not dec("PAB 0", state="experiment").allowed)
    check("E2 experiment refuses POS", not dec("POS", state="experiment").allowed)
    check("E3 unknown state refuses", not dec("PAB 0", state="unknown").allowed)
    check("E4 compound refused", not dec("PAB 1;PAB 2").allowed)
    check("E5 disassembled allows an in-window PAB", dec("PAB 0", state="disassembled").allowed)

    # ---- T ----
    runs = []

    def fake(text, rc_=0):
        def run(script, args, timeout=120):
            runs.append((script, args))
            tok = args[args.index("-TokenFile") + 1]
            cmd = args[args.index("-Command") + 1]
            assert open(tok).read() == cmd
            return rc_, text
        return run

    d = dec("PIC -500")
    rc = mg.transmit_rotor("PIC -500", d, BASE, session=rec, run=fake(
        FRESH_1000 + "TARGET=500 window=-1500..3500\nSENT: SPD 100 ; PIC -500\nRESULT: reached 500 (target 500)\n"))
    a = runs[-1][1] if runs else []
    check("T1 in-window PIC -> rc 0; window and speed passed to the sender",
          rc == 0 and a[a.index("-Lo") + 1] == "-1500" and a[a.index("-Hi") + 1] == "3500"
          and a[a.index("-Speed") + 1] == "100" and runs[-1][0] == mg.ROTOR_IO, (rc, a))
    rc = mg.transmit_rotor("PIC 2400", dec("PIC 2400"), BASE, session=rec, run=fake(
        "FRESH RAW='POS 00000BB8,00000000' POS=3000\nRESULT: reached 5400\n"))
    check("T2 sender rc 0 but fresh 3000 + 2400 is outside -> gate rc 3", rc == 3, rc)
    rc = mg.transmit_rotor("PAB 0", dec("PAB 0"), BASE, session=rec, run=fake(
        "FRESH RAW='POS FFFFFFF6,00000000' POS=4294967286\nRESULT: reached 0\n"))
    check("T3 FRESH sign disagreement -> gate rc 3", rc == 3, rc)
    before = len(runs)
    rc = mg.transmit_rotor("PAB 0", dec("PAB 0"), BASE, session={}, run=fake(""))
    check("T4 no session -> rc 3, sender never run", rc == 3 and len(runs) == before, rc)
    rc = mg.transmit_rotor("PAB 0", dec("PAB 0"), BASE, session=rec, run=fake(
        "SEND REFUSED: target 0 outside\n", 7))
    check("T5 sender's own refusal (exit 7, no FRESH) passes through as non-zero", rc == 7, rc)

    # ---- C ----
    status = os.path.join(tmp, "STATUS.md")
    with open(status, "w", encoding="utf-8") as f:
        f.write("rig-state: assembled\n")
    calls = []
    real = (mg.transmit, mg.SESSION_PATH, mg.ROTOR_IO, mg._run_ps)
    mg.transmit = lambda *a, **k: (calls.append(a), 0)[1]
    mg.SESSION_PATH = os.path.join(tmp, "no_such_session.json")
    mg.ROTOR_IO = os.path.join(tmp, "no_such_sender.ps1")
    mg._run_ps = lambda *a, **k: (calls.append(a), (0, ""))[1]
    try:
        rc = mg.main(["--device", "rotor", "--command", "PAB 0", "--execute", "--status", status,
                      "--journal", os.path.join(tmp, "journal.log")])
    finally:
        mg.transmit, mg.SESSION_PATH, mg.ROTOR_IO, mg._run_ps = real
    check("C1 CLI --execute rotor without a session -> rc 3, nothing sent", rc == 3 and not calls, (rc, len(calls)))

    print("NO MOTION COMMAND WAS SENT AND NO PORT WAS OPENED BY THIS RUN.")
    print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if ok == n else "FAIL",
                                  "gates": {"pass": ok, "fail": n - ok}, "first_fail": None, "artefacts": []}))
    return 0 if ok == n else 1


if __name__ == "__main__":
    sys.exit(main())
