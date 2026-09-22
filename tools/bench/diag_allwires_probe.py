r"""diag_allwires_probe - STEP 0 for OpAllWires_v0. READ-ONLY. NOTHING BUILT, NOTHING SAVED.

Does `Traverse for GObjects` with class `Wire` return the wires of the bed, how many, and how long?
`Wire` is listed VALID in docs/toolkit-capabilities.md:283 but with no count and no timing; the tested
counts there are for other classes. This also times `Terminal` (5763 on the main VI, :283), because the
endpoint half of the table is read off terminals, and it censuses the two candidate DONORS so the build
recipe can be written from measured structure instead of from the recipe files' prose.

PREDICTION CONTRACT (desk-checked, Pre-decided 132 - nothing predicted that an earlier step forced):
  P1  `report_all(work, 'Wire')` (Traverse('Wire') -> For loop -> arrays, ONE op run) returns 1909-1920
      rows. Determined range, not a free prediction: c89 counted 1920 wires on this bed before Remove
      Bad Wires and 1909 after (`tools/bench/diag_c89_wirebirth.log`), and this probe MUTATES NOTHING,
      so 1920 is the expected value and anything in 1909..1920 is still consistent. FALSIFIED by 0 rows,
      by an error 109 (class name refused), or by a count outside that band.
  P2  Every uid in P1's census is distinct and > 0.
  P3  The 11 severed half-wires are all IN the census (c90 measured exactly this, `:25`) - a CONTROL on
      the reader, not a new fact; it fails only if this probe's route differs from c90's.
  P4  `report_all(work, 'Terminal')` returns > 1000 rows on this bed. Free prediction: no step has
      counted Terminal on THIS artefact (the 5763 in toolkit-capabilities.md:283 is the MAIN VI).
  P5  The donor `OpReportAll_v0.vi` carries exactly 1 ForLoop, >= 5 LoopTunnel, 2 Property, 1 SubVI
      (the Traverse) - from `build_opreportall_v1.py` steps 3/6/9/10. FALSIFIED by any other count,
      which would mean the donor on disk is not what that recipe describes.
  TIMING is measured, never predicted (no prior number exists for Traverse('Wire') on this bed).

WHAT ALREADY EXISTS (checked before writing: `grep "^def " tools/gscript.py`, ls tools/recipes,
docs/toolkit-capabilities.md): `report_all` (gscript.py:512, OpReportAll_v0 - Traverse + For loop +
auto-indexed arrays), `count` (:1045), `fp_labels` (:2558), `node_info` (:2580), `stagekit.Stage`
(pins/restart/handles/hygiene). NOTHING NEW IS WRITTEN HERE: this file is inputs, timers and gates.

NO VI is run, NO op is built, NO file is saved; the work copy is discarded. No motor, no ASI, no camera.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                               # noqa: E402
import gscript as g                                                                # noqa: E402

BED = os.path.join(K.CLAUDEDEV, "D1_s3b_m3a3b_rowD_20260922_161040.vi")
BED_MD5 = "0b84595245dd650c0e8fd3f57104782c"
SEVERED = [1731, 1893, 2819, 3947, 4833, 7337, 7388, 9635, 11232, 23502, 23540]
DONORS = ["OpReportAll_v0.vi", "OpWireSource_v5.vi", "OpReport_v3.vi"]


def timed(s, label, fn):
    t0 = time.time()
    val, err = s.safe(label, fn, None)
    dt = time.time() - t0
    s.fact("{0}: {1:.2f} s ; err={2!r}".format(label, dt, err))
    return val, dt, err


def main(s):
    s.start()
    s.discard_work()
    p = s.work

    s.head("[P1-P3] Traverse('Wire') on the bed - does it return the wires, how many, how fast?")
    n_trav, dt_trav, e_trav = timed(s, "P1a count(Wire) = Traverse only", lambda: g.count(p, "Wire"))
    rows, dt_all, e_all = timed(s, "P1b report_all(Wire) = Traverse + For loop + arrays",
                                lambda: g.report_all(p, "Wire"))
    rows = rows or []
    uids = [int(r["uid"]) for r in rows]
    s.fact("P1 rows={0} ; count(Wire)={1} ; first 5 uids={2!r} ; classes seen={3!r}".format(
        len(rows), n_trav, uids[:5], sorted({r["class"] for r in rows})[:6]))
    s.R["wire_rows"] = len(rows)
    s.R["wire_seconds_report_all"] = round(dt_all, 3)
    s.R["wire_seconds_count"] = round(dt_trav, 3)
    s.gate("P1 Traverse('Wire') returns 1909-1920 rows in ONE op run",
           1909 <= len(rows) <= 1920 and not e_all,
           "rows={0} err={1!r}".format(len(rows), e_all))
    s.gate("P2 every wire uid distinct and > 0",
           bool(uids) and len(set(uids)) == len(uids) and min(uids or [0]) > 0,
           "distinct {0} of {1}".format(len(set(uids)), len(uids)))
    missing = [w for w in SEVERED if w not in set(uids)]
    s.gate("P3 all 11 severed half-wires are IN the census (c90 control)", not missing,
           "absent {0!r}".format(missing))

    s.head("[P4] Traverse('Terminal') on the bed - the cost of the endpoint half of the table")
    trows, dt_term, e_term = timed(s, "P4 report_all(Terminal)", lambda: g.report_all(p, "Terminal"))
    trows = trows or []
    s.R["terminal_rows"] = len(trows)
    s.R["terminal_seconds"] = round(dt_term, 3)
    s.fact("P4 Terminal rows={0} ; owner classes (first 8)={1!r}".format(
        len(trows), sorted({r["owner"] for r in trows})[:8]))
    s.gate("P4 Traverse('Terminal') returns > 1000 rows", len(trows) > 1000,
           "rows={0} err={1!r}".format(len(trows), e_term))

    s.head("[P5] THE DONORS, as they are ON DISK (read-only; these are op VIs, never originals)")
    for name in DONORS:
        path = os.path.join(K.CLAUDEDEV, name)
        if not os.path.exists(path):
            s.fact("P5 {0}: NOT ON DISK".format(name))
            continue
        s.file_facts("P5 " + name, path)
        cen, _e = s.safe("P5 census " + name, lambda path=path: {
            c: g.count(path, c) for c in ("ForLoop", "WhileLoop", "LoopTunnel", "Property", "Invoke",
                                          "SubVI", "IndexArray", "Node", "Wire", "ControlTerminal",
                                          "Diagram", "Constant")}, {})
        labs, _e2 = s.safe("P5 fp_labels " + name,
                           lambda path=path: [(i, lab, bool(ind)) for i, lab, ind in g.fp_labels(path)], [])
        s.fact("P5 {0} census {1!r}".format(name, cen))
        s.fact("P5 {0} panel {1!r}".format(name, labs))
        s.R.setdefault("donors", {})[name] = {"census": cen, "panel": labs}
        if name == "OpReportAll_v0.vi":
            c = cen or {}
            s.gate("P5 OpReportAll_v0 is the loop-and-arrays donor build_opreportall_v1.py describes "
                   "(ForLoop 1, LoopTunnel >= 5, Property 2, SubVI 1)",
                   c.get("ForLoop") == 1 and (c.get("LoopTunnel") or 0) >= 5
                   and c.get("Property") == 2 and c.get("SubVI") == 1,
                   "census {0!r}".format(c))

    s.head("[COST] what a full fresh connectivity table costs today vs. in one round trip")
    s.fact("COST today: node_terms ~0.8 s/node x 635 nodes ~ 508 s (docs/toolkit-capabilities.md:23). "
           "This probe: Traverse('Wire') {0:.2f} s, Traverse('Terminal') {1:.2f} s, both ONE op run.".format(
               dt_all, dt_term))


S = K.Stage(BED, BED_MD5, "diag_allwires_probe", deadline_min=14.0, reserve_s=180.0,
            out_json=os.path.join(K.BENCH, "diag_allwires_probe.json"),
            task="STEP 0 for OpAllWires_v0: can Traverse return class Wire on the bed, how many, how "
                 "long; plus the donor census the build recipe needs. Read-only, nothing saved.")
sys.exit(K.run(main, S))
