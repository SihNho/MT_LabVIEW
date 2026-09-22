r"""diag_c90d_outstanding - THE FOUR OUTSTANDING M3a-4 ROWS, READ FROM THE MACHINE. READ-ONLY.

PREDICTION CONTRACT. The three measurements are reported as VALUES; no gate below depends on their
answer, and nothing here classifies or recommends.
  M1  the four UNREAD wires on the BED - w23985 (`SubVI #48` t3 `VISA resource name`), w24002 (#48 t4
      `In position`), w24009 (`CaseStructure #10407` t1 `# slices in stack`), w23952 (#10407 t4 `VISA
      out`) - read through `Stage.net_sources` (OpWireSource_v5, WIRE-addressed, n=8), NEVER `wmap` /
      `Diagram.Nodes[]`: per row owner class / owner uid / `Terms[]` index / is_source / uid echo
      (`recip`) / error columns VERBATIM, plus `Generic.Owner` 6327806 -> GObject `UID` on every owner
      whose class is a tunnel or a shift register.
  M2  the four OLD border objects on the BED - `LeftShiftRegister` #4344 / #4274, `LoopTunnel` #9641,
      `RightShiftRegister` #4334: the owning structure (`Generic.Owner`, STRICT uid echo) and EVERY wire
      each terminal of theirs currently carries, with each such wire's other endpoints (one net read).
  M3  the same reads on the CLEAN artefact `D1_s3b_row2_20260921_160311.vi` - the before/after pair.
  CONTROLS on BOTH artefacts (values + gates): the negative uid 999983 must NOT echo back through strict
  `owner_of` (G2), and one machine-chosen intact wire must return >=1 real-owner row with PD85 0 (G3).
  GATES: K1/K2/K3 + the five md5 pins (stagekit), G0/G0b the CLEAN artefact's md5, G1 the four wire uids
  are in the BED's Wire census, G2/G3 the controls per artefact, G4a/G4b the BED's md5 before and after
  every read, G5 the v2 row table carries a `disposition_evidence` block on all 11 rows, H2-H6 hygiene.

NOTHING IS BUILT, SAVED, RE-WIRED, MOVED, DELETED OR RUN; no op is created; neither artefact is opened
for EXECUTION. Both inputs are used as dated scratch COPIES deleted in the same run (`THE FILES THIS RUN
LEFT ON DISK: []`, stagekit H6), and both md5s are asserted before and after. Rig ASSEMBLED: no motor,
no ASI, no camera. THE ARTEFACT IS A NEW FILE, `tools/bench/m3a4_row_table_v2.json` - v1 is read and
copied, never rewritten, so no existing cell is at risk.

WHAT ALREADY EXISTS (checked before a line was written): `tools/stagekit.py` `net_sources`:364,
`scratch`:406, `discard_work`:441, pins + hygiene; `tools/bench/c90c_rows.py` `tok`/`linemap`/`cite`/
`controls` (imported, not re-typed); `gscript.report_all`:512 / `loop_cast`:650 / `shift_reg_left`:826 /
`tunnels`:981; `build_d1_v0.owner_of`:338. The readers are in `c90d_reads.py` + `c90d_border.py`, the
v2 assembly in `c90d_table.py` - four files, each <=120 lines.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                               # noqa: E402
import gscript as g                                                                # noqa: E402
import c90d_reads as C                                                             # noqa: E402
import c90d_border as B                                                            # noqa: E402
import c90d_table as T                                                             # noqa: E402

BED = os.path.join(K.CLAUDEDEV, "D1_s3b_m3a3b_rowD_20260922_161040.vi")
BED_MD5 = "0b84595245dd650c0e8fd3f57104782c"
CLEAN = os.path.join(K.CLAUDEDEV, "D1_s3b_row2_20260921_160311.vi")
CLEAN_MD5 = "26c54ff784cb5cea21edbd214d2cc3a0"
LOGP = os.path.join(K.BENCH, "diag_c90d_outstanding.log")
SRC = os.path.join(K.BENCH, "m3a4_row_table.json")
OUTP = os.path.join(K.BENCH, "m3a4_row_table_v2.json")
R = {"m1": {}, "borders": {}, "repl_nets": {}, "controls": {}, "tokens": []}


def main(s):
    s.start()
    s.discard_work()
    p = s.work
    s.head("[T0] THE TWO INPUTS - md5 at both ends; the BED Wire census")
    s.file_facts("T0 CLEAN", CLEAN)
    s.gate("G0 the CLEAN artefact's md5 is {0}".format(CLEAN_MD5), K.md5(CLEAN) == CLEAN_MD5,
           K.md5(CLEAN), fatal=True)
    s.gate("G4a the BED's md5 is {0}".format(BED_MD5), K.md5(BED) == BED_MD5, K.md5(BED), fatal=True)
    bc, _e = s.safe("BED report_all('Wire')", lambda: g.report_all(p, "Wire"), [])
    bset = {r["uid"] for r in (bc or [])}
    s.fact("T0 BED Wire census: {0} wire(s)".format(len(bset)))
    s.gate("G1 the four briefed wire uids are in the BED's Wire census",
           all(w in bset for w, _u, _t, _n, _o in C.BEDW),
           "missing {0!r}".format([w for w, _u, _t, _n, _o in C.BEDW if w not in bset]))

    s.head("[M1] THE FOUR UNREAD WIRES ON THE BED (net_sources, n=8)")
    C.m1(s, p, R)
    s.head("[M1b] THE OTHER REPLACEMENT WIRES ON THE BED - so every one of the 11 rows can be compared")
    for w in sorted(set(C.REPL.values())):
        R["repl_nets"][str(w)] = C.net(s, p, "BED", w, R, "M1b")
    C.controls(s, p, "BED", bset, sorted(bset - set(C.REPL.values()))[0] if bset else 0, R)
    s.head("[M2] THE FOUR OLD BORDER OBJECTS ON THE BED")
    B.borders(s, p, "BED", R)
    s.gate("G4b the BED's md5 is STILL {0} after every read".format(BED_MD5), K.md5(BED) == BED_MD5,
           K.md5(BED))

    cp = s.scratch("clean", source=CLEAN)
    s.head("[M3] THE SAME FOUR BORDER OBJECTS ON THE CLEAN ARTEFACT")
    B.borders(s, cp, "CLEAN", R)
    cc, _e2 = s.safe("CLEAN report_all('Wire')", lambda: g.report_all(cp, "Wire"), [])
    cset = {r["uid"] for r in (cc or [])}
    s.fact("T0 CLEAN Wire census: {0} wire(s)".format(len(cset)))
    C.controls(s, cp, "CLEAN", cset, sorted(cset - set(C.REPL.keys()))[0] if cset else 0, R)
    s.gate("G0b the CLEAN artefact's md5 is STILL {0}".format(CLEAN_MD5), K.md5(CLEAN) == CLEAN_MD5,
           K.md5(CLEAN))

    s.head("[X] THE v2 ROW TABLE - every new cell cites this run's own log:line")
    T.assemble(s, R, SRC, OUTP, LOGP,
               {"bed": {"path": BED, "md5": BED_MD5}, "clean": {"path": CLEAN, "md5": CLEAN_MD5}})


S = K.Stage(BED, BED_MD5, "diag_c90d_outstanding", deadline_min=26.0, reserve_s=280.0,
            out_json=os.path.join(K.BENCH, "diag_c90d_outstanding.json"),
            task="the four unread BED wires, the four old border objects on BED and CLEAN, and the "
                 "disposition_evidence extension of the M3a-4 row table")
sys.exit(K.run(main, S))
