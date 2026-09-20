"""tmx_fallthrough_probe.py - PURE PARSER PROBE.  No COM, no motor, no port, no camera, no LabVIEW.

WHY: STATUS.md OPEN 55 / archive/peer/2026-09-18-tmx-lastfield-parse.md Q2 - when a `before:` line
carries no `TMX?=` token, drive_original_copy_v4.tmx_from() falls through to the `LIMITS` line, which
in `limits-set` mode tools/motor_send_pi.ps1 prints AFTER the SPA write (:58/:78), so the gate reads
back the value it has just written and PASSES without ever seeing what the controller held after the
LabVIEW run.  On an ASSEMBLED rig that is a motor-limit check that can pass falsely.

PRIOR ART CHECKED BEFORE WRITING THIS (2026-09-18):
  - tools/bench/drive_original_copy_v4.py:265 `selftest_tmx()` - the ONLY existing tmx test; its 10
    cases have no fall-through case at all, which is why the fault survived a 10/10 run.
  - tools/bench/selftest_motor_gate2.py - gate-level, feeds `LIMITS ...` strings only.
  - tools/bench/motor_gate2_live.py:120 and tools/motor_gate.py:281 `parse_pi_limits` - the two other
    limit parsers in the fleet; both anchored on `LIMITS`, neither reads `before:`.
  - grep over tools/: NO producer and NO consumer of a `PRELIMITS` line existed anywhere.

THIS FILE IS THE BEFORE/AFTER WITNESS.  It is run ONCE against the UNPATCHED v4 and again against the
PATCHED v4 with the SAME four fixtures, so the new self-test case is shown to be DISCRIMINATING (red
before, green after) rather than merely green.  It imports the live module - no transcription.

PREDICTION CONTRACT
  A fall-through  `before:` with no TMX?= token, plus a post-write `LIMITS ... TMX=39`
                  UNPATCHED -> (39.0, 'LIMITS ...')      <- THE FAULT: the value the gate just wrote
                  PATCHED   -> (None, 'before: ...')
  B normal        `before: ... TMX?=39.00000`            both -> 39.0
  C multi-'='     `before: ... TMX?=1=39.00000`          both -> 39.0   (cycle-31 gate-93 false red)
  D prelimits     `PRELIMITS TMN=0 TMX=39` + a `before:` with no TMX?= + `LIMITS ... TMX=12`
                  UNPATCHED -> (12.0, 'LIMITS ...')      <- false green AND the wrong number
                  PATCHED   -> (39.0, 'PRELIMITS TMN=0 TMX=39')
  Exit code is ALWAYS 0: this probe REPORTS, it does not judge.  The judging test is
  `py tools/bench/drive_original_copy_v4.py --selftest`.

  py tools/bgrun.py --material --max-min 5 --log tools/bench/<name>.log \
      -- py -u tools/bench/tmx_fallthrough_probe.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "tools"))
sys.path.insert(0, HERE)

import drive_original_copy_v4 as d4                                            # noqa: E402

# The post-write LIMITS line motor_send_pi.ps1:58 prints AFTER `SPA 1 0x15 <ExpectHi>`.
POST_WRITE_LIMITS_39 = "LIMITS TMN=0 TMX=39 SPA15=39 SPA30=0"
POST_WRITE_LIMITS_12 = "LIMITS TMN=0 TMX=12 SPA15=12 SPA30=0"

FIXTURES = [
    ("A fall-through: before: without a TMX?= token",
     "before: POS?=1=30.00000 TMN?=1=0.00000 ERR?=0\n" + POST_WRITE_LIMITS_39),
    ("B normal:      before: ... TMX?=39.00000",
     "before: POS?=1=30.00000 TMN?=1=0.00000 TMX?=39.00000 ERR?=0\n" + POST_WRITE_LIMITS_39),
    ("C multi-'=':   before: ... TMX?=1=39.00000",
     "before: POS?=1=30.00000 TMN?=1=0.00000 TMX?=1=39.00000 ERR?=0\n" + POST_WRITE_LIMITS_39),
    ("D prelimits:   PRELIMITS present, before: without TMX?=",
     "PRELIMITS TMN=0 TMX=39\nbefore: POS?=1=30.00000 TMN?=1=0.00000 ERR?=0\n" + POST_WRITE_LIMITS_12),
]


def main():
    print("PROBE of tmx_from in %s" % d4.__file__, flush=True)
    print("has prelimits_from = %s" % hasattr(d4, "prelimits_from"), flush=True)
    for label, text in FIXTURES:
        got, line = d4.tmx_from(text)
        print("  %-48s -> got=%r line=%r" % (label, got, line), flush=True)
        print("       input=%r" % text, flush=True)
    print("PROBE DONE (reporting only, rc 0)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
