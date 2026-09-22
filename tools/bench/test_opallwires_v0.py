r"""test_opallwires_v0 - STEP 2: is OpAllWires_v0 (stage A) FUNCTIONAL on the bed, and what does it cost?

READ-ONLY on a dated work copy of the bed, which is discarded. The op itself only reads its target
(`Open VI Reference` -> `Traverse` -> property reads); it is CALLED here for the first time, so this is the
FUNCTIONAL level, not the structural one (skill: "name the level of verification").

DESK CHECK OF EVERY GATE (Pre-decided 132 - a gate whose value an earlier step already determined is re-cut
as the predicted DIFFERENCE, or labelled a CONTROL):
  T1  CONTROL, determined by `tools/bench/diag_allwires_probe.log` (1920 wires via `report_all`): the op's
      own UID array has 1920 rows. It rides the same `Traverse for GObjects` call, so this checks the NEW
      loop body did not truncate or duplicate the array - not "are there 1920 wires".
  T2  THE REAL PREDICTION: the `Is Broken?` column is True for EXACTLY the 11 wires LabVIEW's own Remove Bad
      Wires removed on four artefacts (`tools/bench/diag_c89_wirebirth.log`, the set
      [1731,1893,2819,3947,4833,7337,7388,9635,11232,23502,23540]). This can genuinely fail: `Wire.Is Broken?`
      6371004 catches a type-INCOMPATIBLE connection (`docs/NAMES.md:395`), while RBW also removes DANGLING
      wires, and 7 of the 11 resolve as `Wire` objects with an EMPTY `Wire.Terms[]` (`diag_c90_endpoints.log`).
      A mismatch is a FINDING about what 6371004 means, not a build defect - reported either way.
  T3  the op's UID set EQUALS `report_all(work,'Wire')`'s UID set, element for element (the identity check
      that makes T2's uids addressable at all).
  T4  MEASURED, NOT PREDICTED: seconds per full call, and the 508 s (635 nodes x 0.8 s) that `node_terms`
      costs for the same sweep (`docs/toolkit-capabilities.md:23`).
  T5  20 consecutive calls, COUNTED FROM CALL 1, leave BOTH meters flat: LabVIEW handles within +/-100 AND
      private-byte drift <= 5 MB - "both meters or neither" (`docs/cycle27-plan.md:408`; the standing
      disposition on this op family, `docs/REFERENCES.md:225-227`; CLAUDE.md reference hygiene). Added after
      `archive/peer/2026-09-23-priorart-allwires.md` A1 found the build recipe carried no hygiene gate at all.
  T6  the op answers on a SECOND, unrelated target (its own donor `OpReportAll_v0.vi`, 18 wires) - so the
      reader is not bed-specific. Wire count there is read from `count()` in the same run, not predicted.
  NOT REACHED BY STAGE A, reported as such, never as a pass: the brief's gates (c) the four known ENDPOINTS
      and (d) the 5-wire spot check against `node_terms`. Stage A has no endpoint columns.

WHAT ALREADY EXISTS: `gscript.op/_run/_err` (the op-calling path), `report_all`, `count`,
`bench_prep.labview_handles`, `stagekit.Stage`. Nothing new is written here beyond the four-line reader.
NOTHING IS SAVED, NO VI OF THE PROJECT IS MODIFIED. No motor, no ASI, no camera.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                               # noqa: E402
import gscript as g                                                                # noqa: E402

BED = os.path.join(K.CLAUDEDEV, "D1_s3b_m3a3b_rowD_20260922_161040.vi")
BED_MD5 = "0b84595245dd650c0e8fd3f57104782c"
OP = os.path.join(K.CLAUDEDEV, "OpAllWires_v0.vi")
DONOR = os.path.join(K.CLAUDEDEV, "OpReportAll_v0.vi")
MAPF = os.path.join(K.BENCH, "opallwires_labels.json")
RBW11 = [1731, 1893, 2819, 3947, 4833, 7337, 7388, 9635, 11232, 23502, 23540]


def all_wires(target, uid_label, broken_label):
    """ONE COM round trip: every wire's uid and Is Broken? off OpAllWires_v0."""
    vi = g.op(OP)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", "Wire")
    g._run(vi)
    err = g._err(vi)
    uids = [int(x) for x in list(vi.GetControlValue(uid_label))]
    broken = [bool(x) for x in list(vi.GetControlValue(broken_label))]
    return uids, broken, err


def main(s):
    s.start()
    s.discard_work()
    p = s.work

    s.head("[T0] the op as it is ON DISK, and its label map")
    s.file_facts("T0 OpAllWires_v0", OP)
    lab = json.load(open(MAPF, encoding="utf-8"))
    s.fact("T0 label map {0!r}".format(lab))
    uid_lab, brk_lab = lab.get("wire_uid"), lab.get("is_broken")
    s.gate("T0 the map names both columns", bool(uid_lab) and bool(brk_lab),
           "{0!r} / {1!r}".format(uid_lab, brk_lab), fatal=True)
    es = s.es("T0 the op, cold", target=OP)
    s.gate("T0b the op reads ExecState 1 COLD in this restarted LabVIEW", es == 1,
           "ExecState {0!r}".format(es), fatal=True)

    s.head("[T1-T4] ONE call on the bed - the whole wire table in one round trip")
    t0 = time.time()
    (uids, broken, err), ferr = s.safe("T1 all_wires(bed)",
                                       lambda: all_wires(p, uid_lab, brk_lab), ([], [], "no call"))
    dt = time.time() - t0
    s.fact("T1 {0} uid rows, {1} broken rows, {2:.2f} s, op error {3!r}{4}".format(
        len(uids), len(broken), dt, err, (" ; raised " + ferr) if ferr else ""))
    s.R["call_seconds"] = round(dt, 3)
    s.R["rows"] = len(uids)
    s.gate("T1 CONTROL: 1920 uid rows and 1920 broken rows, op error empty",
           len(uids) == 1920 and len(broken) == 1920 and not err and not ferr,
           "uids {0} broken {1} err {2!r}".format(len(uids), len(broken), err))

    ref = []
    if uids:
        ref = [int(o["uid"]) for o in g.report_all(p, "Wire")]
    s.gate("T3 the op's uid SET equals report_all(work,'Wire')'s", bool(ref) and set(uids) == set(ref),
           "op {0} / report_all {1} / symmetric difference {2}".format(
               len(set(uids)), len(set(ref)), len(set(uids) ^ set(ref))))

    flagged = sorted(u for u, b in zip(uids, broken) if b)
    s.R["broken_uids"] = flagged
    s.fact("T2 Is Broken? TRUE for {0} wire(s): {1!r}".format(len(flagged), flagged[:40]))
    s.fact("T2 the RBW set (c89) is {0!r}".format(RBW11))
    s.fact("T2 in RBW but NOT flagged: {0!r} ; flagged but NOT in RBW: {1!r}".format(
        [u for u in RBW11 if u not in flagged], [u for u in flagged if u not in RBW11]))
    s.gate("T2 `Is Broken?` is TRUE for exactly the 11 wires Remove Bad Wires removed (c89)",
           flagged == sorted(RBW11), "{0} flagged".format(len(flagged)))

    s.head("[T4] cost")
    s.fact("T4 one full table = {0:.2f} s. The same connectivity sweep with `node_terms` is ~0.8 s/node x "
           "635 nodes ~ 508 s (docs/toolkit-capabilities.md:23); `report_all(Wire)` alone was 1.67 s "
           "(tools/bench/diag_allwires_probe.log).".format(dt))

    s.head("[T5] 20 consecutive calls, COUNTED FROM CALL 1, on BOTH meters - the op's acceptance")
    # The prior-art review's A1 (archive/peer/2026-09-23-priorart-allwires.md) is right that a new traverse
    # op's acceptance is already decided and is a MEASUREMENT: handles flat +/-100 counted from call 1 AND
    # private-byte drift <= 5 MB, "both meters or neither" (docs/cycle27-plan.md:408; the standing
    # disposition on this op family, docs/REFERENCES.md:225-227). Call 1 is inside the window, not before it.
    bp = K.mod("bench_prep")
    h0, _ = s.safe("handles before call 1", bp.labview_handles)
    pb0, _ = s.safe("private bytes before call 1", K.private_bytes)
    t0 = time.time()
    counts = []
    for _k in range(20):
        r, e2 = s.safe("T5 call", lambda: all_wires(p, uid_lab, brk_lab), None)
        counts.append(len(r[0]) if r else -1)
        if e2:
            break
    dt20 = time.time() - t0
    h1, _ = s.safe("handles after 20 calls", bp.labview_handles)
    pb1, _ = s.safe("private bytes after 20 calls", K.private_bytes)
    dmb = ((pb1 - pb0) / 1048576.0) if (pb0 and pb1) else None
    s.fact("T5 20 calls in {0:.1f} s ({1:.2f} s/call); row counts {2!r}".format(
        dt20, dt20 / 20.0, sorted(set(counts))))
    s.fact("T5 handles {0!r} -> {1!r} (delta {2}) ; private bytes {3!r} -> {4!r} (delta {5})".format(
        h0, h1, (h1 - h0) if (h0 and h1) else "n/a", pb0, pb1,
        "{0:+.1f} MB".format(dmb) if dmb is not None else "n/a"))
    s.R["acceptance_20calls"] = {"handles": [h0, h1], "private_bytes": [pb0, pb1],
                                 "private_mb_delta": dmb, "seconds": round(dt20, 2)}
    s.gate("T5 20 calls from call 1: handles flat within +/-100 AND private bytes within 5 MB "
           "(both meters or neither)",
           bool(h0) and bool(h1) and abs(h1 - h0) <= 100 and dmb is not None and abs(dmb) <= 5.0,
           "handles {0!r} -> {1!r} ; private {2}".format(
               h0, h1, "{0:+.1f} MB".format(dmb) if dmb is not None else "NOT MEASURED"))
    s.gate("T5b all 20 calls returned the same row count", len(set(counts)) == 1 and counts[0] > 0,
           "{0!r}".format(sorted(set(counts))))

    s.head("[T6] a SECOND target - the reader is not bed-specific")
    n_ref = g.count(DONOR, "Wire")
    (u2, b2, e3), _ = s.safe("T6 all_wires(OpReportAll_v0)",
                             lambda: all_wires(DONOR, uid_lab, brk_lab), ([], [], "no call"))
    s.fact("T6 donor has count(Wire)={0}; the op returned {1} rows, {2} flagged broken, err {3!r}".format(
        n_ref, len(u2), sum(1 for x in b2 if x), e3))
    s.gate("T6 the op answers on a second target with count(Wire) rows", len(u2) == n_ref and not e3,
           "{0} vs {1}".format(len(u2), n_ref))

    s.head("[NOT REACHED BY STAGE A]")
    s.fact("The brief's gate (c) - the four known ENDPOINTS (w1731 SRC LeftShiftRegister #4344, w3947 SRC "
           "LeftShiftRegister #4274, w9635 SRC LoopTunnel #9641, w7337 SINK RightShiftRegister #4334) - and "
           "gate (d), the 5-wire spot check against node_terms, are NOT MEASURED: stage A has no endpoint "
           "columns. They belong to stage B (the second To More Specific Class for the owner UID).")
    out = os.path.join(K.BENCH, "allwires_rowD_{0}.json".format(time.strftime("%Y%m%d")))
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"target": BED, "target_md5": BED_MD5, "op": OP, "seconds": round(dt, 3),
                   "rows": len(uids), "wire_uid": uids, "is_broken": broken,
                   "broken_uids": flagged, "rbw_set_c89": RBW11}, f)
    s.fact("THE TABLE: {0} ({1} rows)".format(out, len(uids)))


S = K.Stage(BED, BED_MD5, "test_opallwires_v0", deadline_min=22.0, reserve_s=240.0,
            out_json=os.path.join(K.BENCH, "test_opallwires_v0.json"),
            task="STEP 2: call OpAllWires_v0 on the bed - row count, Is Broken? set, seconds per call, "
                 "handle flatness over 20 calls, and a second target. Read-only, nothing saved.")
sys.exit(K.run(main, S))
