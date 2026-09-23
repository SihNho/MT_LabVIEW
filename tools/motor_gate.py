"""motor_gate.py - THE ONE GATEWAY for any motion command to the PI magnet motor, the ASI stage or the rotor.

WHY IT EXISTS (user ruling, 2026-09-17, rig = 조립/assembled): motors are allowed while the rig is assembled
**only inside a safe envelope, and only if the envelope is really enforced by code**. A survey found ~65 files
under tools/ that can reach a motor with no choke point. This file is the choke point; `tools/hooks/guard_bash.py`
refuses the other routes.

REWORKED 2026-09-18 (user present at the rig, verbatim intent): **THE REAL LIMITS ARE NOW IN THE CONTROLLERS,
NOT IN THIS SCRIPT.** P2 measured both (docs/motor-limit-assurance-plan.md "P2 live findings"):
  * PI C-863.11: `SPA 1 0x15 <hi>` / `SPA 1 0x30 <lo>` set TMX/TMN; `MOV 1 40` past TMX 39 answers ERR 7 and the
    axis does not move. RAM only (lost at controller power-cycle) - **never WPA**.
  * ASI Tiger: `SL`/`SU` (ABSOLUTE mm) stop motion at the boundary, joystick and HOME included, and persist across
    power cycles - **never SS Z** (nothing of ours saves settings).
So the script-level numeric envelope (the old PI 0..39 test and the old ASI 1.0 mm radial test, with the fixed
reference point and the "fresh position read" it needed) is DELETED: a second, weaker copy of a limit that the
hardware now enforces was only a place for the two to disagree. What this file still enforces:
  1. RIG STATE from STATUS.md (`rig-state:`): 실험중 => refuse everything; unreadable => refuse (default-deny).
  2. COMMAND CLASS default-deny. Refused for good: every ASI home/origin/zero/save/reset command and every PI
     home/reference/define command - **because a controller limit is ABSOLUTE, so shifting the coordinate zero
     would move the fence without changing a number in this file**. The rotor is refused entirely (no envelope
     has ever been declared for it). Read-only queries pass.
  3. THE SESSION CONTRACT. `--session start` writes the limits from tools/bench/motor_limits.json into both
     controllers and verifies them by readback; `--session end` releases them (PI 0..52, ASI +-500). `--execute`
     refuses unless a session file exists AND a FRESH readback of the controller limits, taken inside the same
     port open as the transmit and before it, matches the file within 0.001.
An abnormal exit therefore leaves the limits ON in the controllers, which is the safe direction.

UNITS - stated explicitly because getting this wrong is the whole risk:
  ASI  motion commands are in 0.1 um  =>  1.0 mm = 10 000 units, `M X=8000` is +0.8 mm.
       ASI SL/SU limits are in **mm, absolute**.
  PI   native unit = mm (M-126.PD1 through GCS `POS?`/`MOV`); SPA 0x15/0x30 are mm as well.
  rotor native unit = pulses, 0.72 deg/pulse (no envelope declared by the user => motion always refused).

  py tools/motor_gate.py --session start | end
  py tools/motor_gate.py --device asi --command "M X=8000" [--dry-run | --execute]
  exit 0 = ALLOW/OK, 3 = REFUSE, 4 = usage error, 5 = transmit not implemented, else the sender's own code.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LIMITS_PATH = os.path.join(ROOT, "tools", "bench", "motor_limits.json")
SESSION_PATH = os.path.join(ROOT, "tools", "bench", "motor_session.json")
LOG_PATH = os.path.join(ROOT, "tools", "bench", "motor_gate.log")
STATUS_PATH = os.path.join(ROOT, "STATUS.md")
PI_SENDER = os.path.join(HERE, "motor_send_pi.ps1")
ASI_IO = os.path.join(HERE, "motor_asi_io.ps1")

DEFAULT_TOL = 0.001
REF_ATTEMPTS = 3   # user 2026-09-23: reference + verify at session start, retried; refuse only after all attempts

PORTS = {"pi": ("COM3", 115200, "ASRL3::INSTR / alias PI"),
         "asi": ("COM4", 115200, "ASRL4::INSTR / alias ASI_Piezo"),
         "rotor": ("COM5", 9600, "ASRL5::INSTR / alias Rotor")}

# ---------------------------------------------------------------- command sets
# ASI: from archive/peer/2026-09-12-asi-tiger-readonly-commands.md. Bare-form queries only; any argument carrying
# '=' , '+' or '-' turns a "query" into a write (`BU Y=#`, `BU Z+` ...), which is the looks-like-a-query trap.
ASI_QUERIES = {"/", "STATUS", "W", "WHERE", "BU", "BUILD", "V", "VERSION", "RB", "RDSBYTE"}
ASI_ABS = {"M", "MOVE"}
ASI_REL = {"R", "MOVREL"}
# Named so the refusal says WHY, though default-deny would catch them anyway. A zero shift MOVES THE FENCE:
# SL/SU are absolute coordinates, so HOME/HERE/ZERO/AZERO/SETHOME would relocate the protected window.
ASI_ORIGIN = {"!": "HOME", "HOME": "HOME", "H": "HERE", "HERE": "HERE", "Z": "ZERO", "ZERO": "ZERO",
              "HM": "SETHOME", "SETHOME": "SETHOME", "AZ": "AZERO", "AZERO": "AZERO",
              "SP": "SAVEPOS", "SAVEPOS": "SAVEPOS", "SS": "SAVESET", "SAVESET": "SAVESET",
              "~": "RESET", "RESET": "RESET", "\\": "HALT", "HALT": "HALT",
              "MC": "MOTCTRL", "MOTCTRL": "MOTCTRL", "@": "SPIN", "SPIN": "SPIN",
              "MM": "MULTIMV", "MULTIMV": "MULTIMV", "VE": "VECTOR", "VECTOR": "VECTOR",
              "SN": "SCAN", "SCAN": "SCAN", "NR": "SCANR", "NV": "SCANV",
              "SL": "SETLOW limit", "SU": "SETUP limit"}   # SL/SU writes belong to --session only

# PI GCS (Mercury, M-126.PD1). Query list = the one already proven on this port by serial_roundtrip.ps1.
PI_QUERIES = {"POS?", "TMN?", "TMX?", "ERR?", "*IDN?", "VEL?", "SVO?", "ONT?", "HLP?", "RON?", "FRF?",
              "SPA?", "SAI?"}
PI_ABS = {"MOV"}
PI_REL = {"MVR"}
PI_HOME = {"GOH": "go to home", "FRF": "reference move", "FNL": "negative-limit move",
           "FPL": "positive-limit move", "DFH": "define home", "RON": "referencing mode",
           "POS": "define the current position - would SHIFT the coordinate zero under the absolute "
                  "controller limits (allowed only inside the session-start hook, which does not use it; the "
                  "axis is RON 0 with its position already defined - do not change it)",
           "SPA": "set a stage parameter, incl. the soft limits themselves (session hook only)",
           "WPA": "write parameters to non-volatile memory - NEVER (the controller limits are RAM by design)"}

ROTOR_QUERIES = {"POS"}          # Autonics PMC-2HS read; everything else refused (no envelope declared)

AXES = ("X", "Y", "Z")


class Decision(object):
    def __init__(self, allowed, reason, detail=None):
        self.allowed = bool(allowed)
        self.reason = reason
        self.detail = detail or {}

    def __repr__(self):
        return "<%s %s>" % ("ALLOW" if self.allowed else "REFUSE", self.reason)


# ---------------------------------------------------------------- rig state / files
def rig_state(status_text):
    """'disassembled' | 'assembled' | 'experiment' | 'unknown'.

    ONE machine-readable key, `rig-state: <value>`, is the source of truth - a substring search for 실험중 cannot
    work because the permission TABLE in STATUS.md contains that word on every rig state. A line that *starts* a
    STATUS banner with EXPERIMENT RUNNING still forces 'experiment': default-deny beats a stale key."""
    if re.search(r"(?m)^#+\s*\S*\s*EXPERIMENT RUNNING", status_text):
        return "experiment"
    m = re.search(r"(?m)^\s*(?:#\s*)?rig-state:\s*([^\s#]+)", status_text)
    if not m:
        return "unknown"
    v = m.group(1).strip().lower()
    if v in ("분해", "disassembled"):
        return "disassembled"
    if v in ("조립", "assembled"):
        return "assembled"
    if v in ("실험중", "experiment", "experiment-running"):
        return "experiment"
    return "unknown"


def read_status(path=None):
    try:
        with open(path or STATUS_PATH, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def load_limits(path=None):
    """The user-editable limit file. Returns None if missing/unreadable -> everything is refused."""
    try:
        with open(path or LIMITS_PATH, encoding="utf-8-sig") as f:
            lim = json.load(f)
    except (OSError, ValueError):
        return None
    try:
        float(lim["pi"]["lo_mm"]), float(lim["pi"]["hi_mm"]), float(lim["pi"]["release_hi_mm"])
        for k in ("sl", "su"):
            float(lim["asi"][k]["X"]), float(lim["asi"][k]["Y"])
        float(lim["asi"]["release"]["sl"]), float(lim["asi"]["release"]["su"])
    except (KeyError, TypeError, ValueError):
        return None
    lim.setdefault("tolerance", DEFAULT_TOL)
    return lim


def session_info(path=None):
    try:
        with open(path or SESSION_PATH, encoding="utf-8-sig") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


# ---------------------------------------------------------------- helpers
def _tokens(command):
    c = command.strip().strip("\r\n")
    if not c:
        return None, []
    # A leading '/' or '!' or '~' or '\' is a whole command on its own in the ASI set.
    if c[0] in "/!~\\@" and (len(c) == 1 or c[1] == " "):
        return c[0], c[1:].split()
    parts = c.split()
    return parts[0].upper(), parts[1:]


def _compound(command):
    """More than one command in one string is refused: the gate must decide exactly one thing."""
    return ("\r" in command.strip("\r\n")) or ("\n" in command.strip("\r\n")) or (";" in command)


def _axis_pairs(args):
    """['X=8000','Y=-200'] -> {'X': 8000.0, 'Y': -200.0}; None if anything is not AXIS=<number>."""
    out = {}
    for a in args:
        m = re.match(r"^([XYZ])\s*=\s*([+-]?\d+(?:\.\d+)?)$", a.strip().upper())
        if not m:
            return None
        out[m.group(1)] = float(m.group(2))
    return out or None


# ---------------------------------------------------------------- per-device decisions
def decide_asi(cmd, args, raw):
    if cmd is None:
        return Decision(False, "empty command")
    if cmd in ASI_ORIGIN:
        return Decision(False, "ASI home/origin/zero/save/reset class command %r (%s) - NEVER permitted: the "
                               "controller SL/SU limits are ABSOLUTE coordinates, so shifting the zero would move "
                               "the fence" % (cmd, ASI_ORIGIN[cmd]))
    if cmd in ASI_QUERIES:
        for a in args:
            if any(ch in a for ch in "=+-"):
                return Decision(False, "ASI %r with argument %r: an argument carrying '=', '+' or '-' is a WRITE, "
                                       "not a query (BU Y=#, BU Z+ ...)" % (cmd, a))
        if cmd in ("W", "WHERE", "RB", "RDSBYTE"):
            for a in args:
                if a.strip().upper() not in AXES:
                    return Decision(False, "ASI %r takes axis letters only, got %r" % (cmd, a))
        return Decision(True, "ASI read-only query %r" % cmd, {"kind": "query"})
    if cmd not in ASI_ABS and cmd not in ASI_REL:
        return Decision(False, "ASI command %r is not on the allow-list (default-deny)" % cmd)

    pairs = _axis_pairs(args)
    if not pairs:
        return Decision(False, "ASI %r: arguments must be AXIS=<number> in tenths of microns, got %r" % (cmd, args))
    relative = cmd in ASI_REL
    return Decision(True, "ASI %s move %s - the CONTROLLER's SL/SU limits bound it (verified by readback at "
                          "transmit time)" % ("relative" if relative else "absolute", pairs),
                    {"kind": "move", "axes": pairs, "relative": relative})


def decide_pi(cmd, args, raw):
    if cmd is None:
        return Decision(False, "empty command")
    if cmd in PI_HOME:
        return Decision(False, "PI %r (%s) - never permitted through this gate" % (cmd, PI_HOME[cmd]))
    if cmd in PI_QUERIES:
        return Decision(True, "PI read-only query %r" % cmd, {"kind": "query"})
    if cmd not in PI_ABS and cmd not in PI_REL:
        return Decision(False, "PI command %r is not on the allow-list (default-deny)" % cmd)
    nums = [float(t) for t in args if re.match(r"^[+-]?\d+(?:\.\d+)?$", t)]
    if not nums:
        return Decision(False, "PI %r: no numeric target found in %r" % (cmd, args))
    relative = cmd in PI_REL
    return Decision(True, "PI %s move to %s - the CONTROLLER's TMN/TMX soft limits bound it (verified by readback "
                          "at transmit time; a target outside them answers ERR 7 and does not move)"
                    % ("relative" if relative else "absolute", nums),
                    {"kind": "move", "targets_mm": nums, "relative": relative})


def decide_rotor(cmd, args, raw):
    if cmd is None:
        return Decision(False, "empty command")
    if cmd in ROTOR_QUERIES:
        return Decision(True, "rotor read-only query %r" % cmd, {"kind": "query"})
    return Decision(False, "rotor command %r refused: no envelope has ever been declared for the rotor and its "
                           "controller carries no soft limit we have verified (default-deny)" % cmd)


DEVICES = {"asi": decide_asi, "pi": decide_pi, "rotor": decide_rotor}


def decide(device, command, state=None):
    """The whole command-class decision, with no I/O to a port. `state` is injected so the self-test can run every
    case without touching hardware or the live STATUS.md. NUMERIC bounds are NOT decided here any more - the
    controllers hold them, and --execute proves by readback that they are in force."""
    device = (device or "").lower()
    if device not in DEVICES:
        return Decision(False, "unknown device %r (expected one of %s)" % (device, ", ".join(sorted(DEVICES))))
    if state is None:
        state = rig_state(read_status())
    if state == "experiment":
        # ASCII ONLY in every message: this machine's console is cp949 and a UnicodeEncodeError inside the gate
        # would turn a REFUSAL into a crash with a different exit code.
        return Decision(False, "STATUS.md says the rig state is EXPERIMENT RUNNING (experiment in progress) - no "
                               "motor and no instrument access at all (CLAUDE.md rule 1b)")
    if state == "unknown":
        return Decision(False, "STATUS.md carries no machine-readable `rig-state:` line - default-deny "
                               "(only the user announces a state change)")
    if _compound(command):
        return Decision(False, "compound command %r (contains ';' or an embedded terminator) - one command per "
                               "decision" % command)
    cmd, args = _tokens(command)
    d = DEVICES[device](cmd, args, command)
    if d.allowed and state == "assembled" and d.detail.get("kind") == "move":
        d.detail["state_note"] = ("rig assembled: motion allowed by the user's 2026-09-17 ruling, bounded by the "
                                  "CONTROLLER limits this gate installs and re-verifies")
    return d


# ---------------------------------------------------------------- limit readback parsing / checking
def parse_pi_limits(text):
    """'LIMITS TMN=0 TMX=39 SPA15=39 SPA30=0' -> dict, or None.  This is the POST-WRITE readback.

    ANCHORED at the START OF A LINE since 2026-09-18: motor_send_pi.ps1:52 now also prints
    'PRELIMITS TMN=<n> TMX=<n>' (the PRE-write limits), and an unanchored search would match the
    substring 'LIMITS TMN=0 TMX=39' inside 'PRE' + that line - and match it FIRST, because PRELIMITS
    is printed before the SPA write.  The gate would then verify the limits the controller had on
    arrival instead of the ones it just installed.  Case '2b' of
    tools/bench/selftest_motor_gate2.py asserts exactly that (STATUS.md OPEN 55).

    The LAST '^LIMITS' line is judged (cycle 69 repair (b)): limits-set prints one after the write
    (motor_send_pi.ps1:96) and another after the reference move + verify (:147); the last is the state the
    controller is left in."""
    ms = list(re.finditer(r"(?m)^LIMITS\s+TMN=([-+0-9.eE]+)\s+TMX=([-+0-9.eE]+)"
                          r"(?:\s+SPA15=([-+0-9.eE]+)\s+SPA30=([-+0-9.eE]+))?", text or ""))
    if not ms:
        return None
    m = ms[-1]
    out = {"TMN": float(m.group(1)), "TMX": float(m.group(2))}
    if m.group(3) is not None:
        out["SPA15"], out["SPA30"] = float(m.group(3)), float(m.group(4))
    return out


def parse_pi_ref(text):
    """'REFSTATE RON=0 FRF=1 POS=0.00000 POS_BEFORE=0.00000 ERR=0' -> dict, or None.

    The session-start hook performs a REAL reference move (SVO 1 1, RON 1 1, FNL 1 to the negative limit switch),
    requires FRF? 1 and POS 0, then a commanded-vs-readback verify move (0 -> 2 mm -> 0, tol 0.05 mm) - the
    user's 2026-09-23 rule. The retired restore that declared the current counter as zero was removed after it
    drove the magnet into the hard limit (tools/bench/pi_testmove_20260923e.log, ERR 216). Writing SPA 0x15/0x30
    leaves the axis UNREFERENCED (tools/bench/motor_gate2_live.log L2/L3), which is why the reference follows it."""
    m = re.search(r"REFSTATE\s+RON=([-+0-9.eE]+)\s+FRF=([-+0-9.eE]+)\s+POS=([-+0-9.eE]+)"
                  r"\s+POS_BEFORE=([-+0-9.eE]+)", text or "")
    if not m:
        return None
    return {"RON": float(m.group(1)), "FRF": float(m.group(2)),
            "POS": float(m.group(3)), "POS_BEFORE": float(m.group(4))}


def parse_asi_limits(text):
    """'LIMITS SL X=-3.847494 Y=-4.774393 SU X=0.152497 Y=-0.774402' -> dict, or None."""
    m = re.search(r"LIMITS\s+SL\s+X=([-+0-9.eE]+)\s+Y=([-+0-9.eE]+)\s+SU\s+X=([-+0-9.eE]+)\s+Y=([-+0-9.eE]+)",
                  text or "")
    if not m:
        return None
    return {"SL": {"X": float(m.group(1)), "Y": float(m.group(2))},
            "SU": {"X": float(m.group(3)), "Y": float(m.group(4))}}


def check_pi_readback(rb, lo, hi, tol=DEFAULT_TOL):
    """(ok, message). rb = parse_pi_limits() output. Every readback field present must match."""
    if not rb:
        return False, "PI limit readback unreadable (no 'LIMITS TMN=.. TMX=..' line)"
    bad = []
    for key, want in (("TMN", lo), ("TMX", hi), ("SPA30", lo), ("SPA15", hi)):
        if key in rb and abs(rb[key] - want) > tol:
            bad.append("%s=%.4f != %.4f" % (key, rb[key], want))
    if bad:
        return False, "PI controller limits do not match tools/bench/motor_limits.json: " + ", ".join(bad)
    return True, "PI controller limits match the file (TMN %.4f / TMX %.4f, tol %g)" % (lo, hi, tol)


def check_asi_readback(rb, sl, su, tol=DEFAULT_TOL):
    if not rb:
        return False, "ASI limit readback unreadable (no 'LIMITS SL .. SU ..' line)"
    bad = []
    for key, want in (("SL", sl), ("SU", su)):
        for ax in ("X", "Y"):
            if abs(rb[key][ax] - float(want[ax])) > tol:
                bad.append("%s %s=%.6f != %.6f" % (key, ax, rb[key][ax], float(want[ax])))
    if bad:
        return False, "ASI controller limits do not match tools/bench/motor_limits.json: " + ", ".join(bad)
    return True, "ASI controller limits match the file (SL %s / SU %s mm, tol %g)" % (sl, su, tol)


# ---------------------------------------------------------------- session hooks
def _run_ps(script, args, timeout=120):
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script] + args,
                       capture_output=True, text=True, timeout=timeout)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def _pi_limits_call(mode, lo, hi):
    return _run_ps(PI_SENDER, ["-Mode", mode, "-ExpectLo", "%g" % lo, "-ExpectHi", "%g" % hi])


def _asi_limits_call(mode, sl, su):
    return _run_ps(ASI_IO, ["-Mode", mode, "-ExpectSlX", "%g" % float(sl["X"]), "-ExpectSlY", "%g" % float(sl["Y"]),
                            "-ExpectSuX", "%g" % float(su["X"]), "-ExpectSuY", "%g" % float(su["Y"])])


def session_start(limits, pi_call=None, asi_call=None, session_path=None, out=print):
    """Write the file's limits into BOTH controllers and verify by readback. rc 0 = both verified, else 3.
    `pi_call`/`asi_call` are injected by the self-test: (mode, ...) -> (rc, text)."""
    pi_call = pi_call or (lambda mode, lo, hi: _pi_limits_call(mode, lo, hi))
    asi_call = asi_call or (lambda mode, sl, su: _asi_limits_call(mode, sl, su))
    tol = float(limits.get("tolerance", DEFAULT_TOL))
    lo, hi = float(limits["pi"]["lo_mm"]), float(limits["pi"]["hi_mm"])
    sl, su = limits["asi"]["sl"], limits["asi"]["su"]
    # PI: limits written, then a REAL reference move (FNL 1) and a commanded-vs-readback VERIFY, all inside the
    # sender's limits-set mode (user 2026-09-23: "원점 복귀하여 복원 시키고 사이클 시작한다 … 여러 차례 복원 시도해도
    # 문제가 생긴다면 그 때는 사이클 종료"). Up to REF_ATTEMPTS attempts; only when all fail is the session refused.
    pi_rb, pi_ref, ok_pi, rc, text, attempt = None, None, False, 3, "", 0
    for attempt in range(1, REF_ATTEMPTS + 1):
        rc, text = pi_call("limits-set", lo, hi)
        out(text.strip())
        pi_rb = parse_pi_limits(text)
        ok_lim, msg_pi = check_pi_readback(pi_rb, lo, hi, tol)
        pi_ref = parse_pi_ref(text)
        ok_ref = bool(pi_ref) and pi_ref["FRF"] == 1.0 and abs(pi_ref["POS"]) <= tol
        ok_ver = "VERIFY-RESULT: OK" in (text or "")
        out("PI  : %s (sender code=%d)" % (msg_pi, rc))
        out("PI  : reference %s -> %s; verify %s (attempt %d/%d)"
            % (json.dumps(pi_ref, sort_keys=True) if pi_ref else "NOT REPORTED",
               "REFERENCED at 0" if ok_ref else "NOT REFERENCED", "OK" if ok_ver else "FAILED", attempt, REF_ATTEMPTS))
        ok_pi = ok_lim and ok_ref and ok_ver and rc == 0
        if ok_pi:
            break
        out("PI  : reference/verify attempt %d failed - retrying" % attempt if attempt < REF_ATTEMPTS
            else "PI  : reference/verify failed %d times - giving up" % REF_ATTEMPTS)
        time.sleep(2)
    if not ok_pi:
        # cycle 69 repair (a): a PI refusal after all REF_ATTEMPTS ends the session here - the ASI port is not
        # opened and no ASI limits are written.
        out("ASI : not contacted - PI refused after %d attempts" % REF_ATTEMPTS)
        out("SESSION START REFUSED - no session file written, --execute stays closed")
        return 3
    rc2, text2 = asi_call("limits-set", sl, su)
    out(text2.strip())
    asi_rb = parse_asi_limits(text2)
    ok_asi, msg_asi = check_asi_readback(asi_rb, sl, su, tol)
    out("ASI : %s (sender code=%d)" % (msg_asi, rc2))
    if not (ok_pi and rc == 0 and ok_asi and rc2 == 0):
        out("SESSION START REFUSED - no session file written, --execute stays closed")
        return 3
    rec = {"started": time.strftime("%Y-%m-%d %H:%M:%S"),
           "pi_reference": pi_ref, "pi_reference_attempts": attempt, "pi_verify": "OK",
           "limits_readback": {"pi": pi_rb, "asi": asi_rb},
           "limits_file": {"pi": {"lo_mm": lo, "hi_mm": hi}, "asi": {"sl": sl, "su": su}},
           "tolerance": tol}
    with open(session_path or SESSION_PATH, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=2, sort_keys=True)
    out("SESSION START OK -> %s" % (session_path or SESSION_PATH))
    return 0


def session_end(limits, pi_call=None, asi_call=None, session_path=None, out=print):
    """Release the controller limits (PI lo..release_hi, ASI +-release) and delete the session file."""
    pi_call = pi_call or (lambda mode, lo, hi: _pi_limits_call(mode, lo, hi))
    asi_call = asi_call or (lambda mode, sl, su: _asi_limits_call(mode, sl, su))
    tol = float(limits.get("tolerance", DEFAULT_TOL))
    lo, hi = 0.0, float(limits["pi"]["release_hi_mm"])
    rel = limits["asi"]["release"]
    sl = {"X": float(rel["sl"]), "Y": float(rel["sl"])}
    su = {"X": float(rel["su"]), "Y": float(rel["su"])}
    rc, text = pi_call("limits-release", lo, hi)
    out(text.strip())
    ok_pi, msg_pi = check_pi_readback(parse_pi_limits(text), lo, hi, tol)
    out("PI  : %s (sender code=%d)" % (msg_pi, rc))
    rc2, text2 = asi_call("limits-release", sl, su)
    out(text2.strip())
    ok_asi, msg_asi = check_asi_readback(parse_asi_limits(text2), sl, su, tol)
    out("ASI : %s (sender code=%d)" % (msg_asi, rc2))
    path = session_path or SESSION_PATH
    if not (ok_pi and rc == 0 and ok_asi and rc2 == 0):
        out("SESSION END INCOMPLETE - the session file is KEPT so the mismatch stays visible; --execute will "
            "refuse anyway because the readback no longer matches the file")
        return 3
    if os.path.exists(path):
        os.remove(path)
    out("SESSION END OK - controller limits released, %s deleted" % path)
    return 0


# ---------------------------------------------------------------- transmit
def log(device, command, d, dry):
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write("%s\t%s\t%s\t%s\tcmd=%r\t%s\n" % (
                time.strftime("%Y-%m-%d %H:%M:%S"), device.upper(),
                "ALLOW" if d.allowed else "REFUSE", "DRY" if dry else "LIVE", command, d.reason))
    except OSError:
        pass


def _token_file(canon):
    fd, tok = tempfile.mkstemp(prefix="motor_gate_", suffix=".tok")
    with os.fdopen(fd, "w", encoding="ascii") as f:
        f.write(canon)
    return tok


def transmit(device, command, d, limits):
    """Send ONE decided motion command. The SENDER re-reads the controller limits inside the same port open,
    before the transmit, and refuses if they do not match the file (exit 7)."""
    tol = float(limits.get("tolerance", DEFAULT_TOL))
    if device == "asi":
        cmd_tok, cmd_args = _tokens(command)
        pairs = _axis_pairs(cmd_args) or {}
        if cmd_tok not in ASI_ABS or len(pairs) != 1 or "Z" in pairs:
            sys.stderr.write("TRANSMIT NOT IMPLEMENTED for this ASI command (only absolute single-axis "
                             "'M X=<int>' or 'M Y=<int>'; Z has no controller limit and is not transmittable "
                             "from here).\n")
            return 5
        axis, val = list(pairs.items())[0]
        canon = "M %s=%d" % (axis, int(round(val)))
        sl, su = limits["asi"]["sl"], limits["asi"]["su"]
        tok = _token_file(canon)
        try:
            rc, text = _run_ps(ASI_IO, ["-Mode", "send", "-Command", canon, "-TokenFile", tok,
                                        "-ExpectSlX", "%g" % float(sl["X"]), "-ExpectSlY", "%g" % float(sl["Y"]),
                                        "-ExpectSuX", "%g" % float(su["X"]), "-ExpectSuY", "%g" % float(su["Y"]),
                                        "-Tol", "%g" % tol])
        finally:
            if os.path.exists(tok):
                os.remove(tok)
        print(text.strip())
        ok, msg = check_asi_readback(parse_asi_limits(text), sl, su, tol)
        print("GATE re-check of the sender's readback: %s" % msg)
        _append_log("ASI", rc, text)
        return rc if ok else (rc or 3)
    if device != "pi" or d.detail.get("kind") != "move" or d.detail.get("relative"):
        sys.stderr.write("TRANSMIT NOT IMPLEMENTED for this device/command (only PI absolute 'MOV 1 <n>').\n")
        return 5
    lo, hi = float(limits["pi"]["lo_mm"]), float(limits["pi"]["hi_mm"])
    canon = "MOV 1 %s" % ("%.4f" % d.detail["targets_mm"][-1]).rstrip("0").rstrip(".")
    tok = _token_file(canon)
    try:
        rc, text = _run_ps(PI_SENDER, ["-Mode", "send", "-Command", canon, "-TokenFile", tok,
                                       "-ExpectLo", "%g" % lo, "-ExpectHi", "%g" % hi, "-Tol", "%g" % tol],
                           timeout=180)
    finally:
        if os.path.exists(tok):
            os.remove(tok)
    print(text.strip())
    ok, msg = check_pi_readback(parse_pi_limits(text), lo, hi, tol)
    print("GATE re-check of the sender's readback: %s" % msg)
    _append_log("PI", rc, text)
    return rc if ok else (rc or 3)


def _append_log(tag, rc, text):
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write("%s\t%s\tSENT\trc=%d\t%s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), tag, rc,
                                                  " | ".join(text.strip().splitlines()[-2:])))
    except OSError:
        pass


# ---------------------------------------------------------------- CLI
def main(argv=None):
    p = argparse.ArgumentParser(description="the single gateway for motion commands to PI / ASI / rotor")
    p.add_argument("--session", choices=["start", "end"], default=None,
                   help="start: write the controller limits from tools/bench/motor_limits.json and verify them; "
                        "end: release them (PI 0..release_hi, ASI +-500) and delete the session file")
    p.add_argument("--device", default=None, help="pi | asi | rotor")
    p.add_argument("--command", default=None, help="one raw controller command, e.g. 'M X=8000' or 'MOV 1 12.5'")
    p.add_argument("--dry-run", action="store_true", default=True, help="decide only, open no port (the DEFAULT)")
    p.add_argument("--execute", action="store_true", help="transmit (needs an open session and a matching readback)")
    p.add_argument("--limits", default=None, help="override the limits file path (tests)")
    p.add_argument("--status", default=None, help="override STATUS.md (tests)")
    p.add_argument("--reference", default=None, metavar="USER_ORDER",
                   help="USER-ORDERED PI reference move (FNL 1: 0 = negative limit switch). The value is the user's "
                        "own words ordering it, logged verbatim. Never automatic; the session hooks never call it.")
    a = p.parse_args(argv)

    limits = load_limits(a.limits)
    if limits is None:
        sys.stderr.write("REFUSED: limits file %s is missing, unreadable or incomplete - the gate installs and "
                         "verifies the CONTROLLER limits from it, so nothing is permitted without it\n"
                         % (a.limits or LIMITS_PATH))
        return 3
    state = rig_state(read_status(a.status))
    if a.session:
        if state != "assembled" and state != "disassembled":
            sys.stderr.write("REFUSED: rig state %r - the session hook opens both motor ports (CLAUDE.md 1b)\n"
                             % state)
            return 3
        return session_start(limits) if a.session == "start" else session_end(limits)
    if a.reference:
        # 2026-09-23: a power-cycled C-863 restarts with POS 0 at the stage's physical spot; the session-start hook
        # then cemented that false zero (RON 1 0 + POS 1 <current>) and a MOV +30 ran into the hard limit (ERR 216).
        # The only correct repair is a real reference move, which PI_HOME forbids on every other route.
        if state != "assembled" and state != "disassembled":
            sys.stderr.write("REFUSED: rig state %r - no reference move in this state\n" % state)
            return 3
        if len(a.reference.strip()) < 4:
            sys.stderr.write("REFUSED: --reference needs the user's order text\n")
            return 3
        print("USER-ORDERED REFERENCE MOVE: %r" % a.reference)
        rc, text = _run_ps(PI_SENDER, ["-Mode", "reference", "-SettleTimeoutS", "120"], timeout=180)
        print(text.strip())
        _append_log("PI-REFERENCE(user: %s)" % a.reference[:60], rc, text)
        return rc

    if not a.device or not a.command:
        sys.stderr.write("usage: --session start|end, or --device <d> --command <c> [--execute]\n")
        return 4
    d = decide(a.device, a.command, state=state)
    log(a.device, a.command, d, dry=not a.execute)
    if not d.allowed:
        sys.stderr.write("REFUSED (%s): %s\n" % (a.device, d.reason))
        return 3
    print("ALLOWED (%s): %s" % (a.device, d.reason))
    if d.detail:
        print(json.dumps(d.detail, sort_keys=True))
    if not a.execute:
        return 0
    if d.detail.get("kind") != "move":
        print("(query decisions are not transmitted by this gate)")
        return 5
    sess = session_info()
    if not sess:
        sys.stderr.write("REFUSED: no session file %s - run `py tools/motor_gate.py --session start` first, which "
                         "installs the CONTROLLER limits and verifies them\n" % SESSION_PATH)
        return 3
    print("session opened %s" % sess.get("started"))
    return transmit(a.device.lower(), a.command, d, limits)


EXIT_MEANING = {3: "REFUSED by the gate (rig state / command class / session / limit readback)",
                4: "usage error", 5: "transmit not implemented for this command",
                6: "sender could not read the controller", 7: "sender REFUSED (token / limits mismatch / servo)",
                8: "motion ended NOT at target", 9: "REJECTED BY THE CONTROLLER (ERR after send) or reference incomplete"}


def fail_line(rc):
    """One `FAIL:` line for a non-zero exit (cycle 69, device-failed repair). pi_testmove_20260923e.log:23/34 held a
    NOT-at-target and a REJECTED result, yet the chained bash run ended `BGRUN END rc=0` (:51) because a later command
    in the chain succeeded, so bgrun, audit_cycle and guard_peer never saw the failure. `^FAIL\\b` is the form all three
    scanners already match. Printed at PROCESS exit only, not inside main(), so in-process self-tests that call main()
    on purpose-refused commands do not print it. ASCII only (cp949 console)."""
    return "FAIL: motor_gate exit %d - %s" % (rc, EXIT_MEANING.get(rc, "sender's own non-zero code"))


if __name__ == "__main__":
    _rc = main()
    if _rc:
        print(fail_line(_rc), flush=True)
    sys.exit(_rc)
