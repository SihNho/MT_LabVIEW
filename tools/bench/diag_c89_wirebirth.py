r"""diag_c89_wirebirth - (T1) the 0 -> 1 control for the `ExecState` reader, (T2) WHICH SAVED STAGE
ARTEFACT FIRST CARRIES A BROKEN WIRE. READ-ONLY; nothing built, saved, or mutated on any artefact.

WHAT ALREADY EXISTS (CLAUDE.md "check what exists first"; grep of tools/, toolkit-capabilities.md) - NO new
op, verb or helper is written: `tools/stagekit.py` (pins/restart/scratch/`es`/hygiene; this file is its
inputs only) * `diag_c88_brokenwires.py:89-102` the RBW set-difference METHOD, verbatim *
`diag_c89_bareterms.py:63-98` the 1 -> 0 half of this control * `build_d1_v0.wmap`:364 uid -> (Nodes[] index,
label, rows) * `build_opfsinnertunnelconnect_v0.del_wire`:336 * `gscript.connect_terminals`:2528 =
`OpConnect_v0`, THE project's existing connect helper for a flat diagram.

PREDICTION CONTRACT - ONLY T1c, T2-CTL3 AND T2-CTL10 ARE GATES; every other removed count is a CENSUS READ
reported as a VALUE (the brief: "do NOT invent a predicted count for them").  T1c: on a scratch of
`OpFsInnerTunnelConnect_v1.vi`, ExecState 1 -> delete the wire feeding the REQUIRED `vi path` input (#43 t6)
-> 0 -> re-create it with `connect_terminals` -> 1.  CTL3: `D1_s3a_boolcarrier_b3_...vi` (STATUS: ExecState
1, Is Broken? False) removes 0 wires.  CTL10: the rowD bed removes exactly the c88 baseline of 11.
Every probe runs on a dated scratch COPY deleted in the same run; each source's md5 is re-read and asserted
UNCHANGED after its probe. No motor, no ASI, no camera.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                               # noqa: E402
import gscript as g                                                                # noqa: E402

CD = K.CLAUDEDEV
BED = os.path.join(CD, "D1_s3b_m3a3b_rowD_20260922_161040.vi")
BED_MD5 = "0b84595245dd650c0e8fd3f57104782c"
PC_VI = os.path.join(CD, "OpFsInnerTunnelConnect_v1.vi")
PC_MD5 = "5b4e5f0fb3baae96361c33ce81bcd7b1"
PC_SINK_UID, PC_SINK_TERM = 43, 6
THE11 = [1731, 1893, 2819, 3947, 4833, 7337, 7388, 9635, 11232, 23502, 23540]
# (build-order #, tag, filename, control-expectation or None)
FILES = [(1, "s1copy", "D1_s1_copy.vi", None), (2, "s2loops", "D1_s2_loops.vi", None),
         (3, "s3aboolb3", "D1_s3a_boolcarrier_b3_20260921_010034.vi", 0),
         (4, "s3afocus", "D1_s3a_focus_ind.vi", None), (5, "s3brow1", "D1_s3b_row1_20260921_135932.vi", None),
         (6, "s3brow2", "D1_s3b_row2_20260921_160311.vi", None),
         (7, "m3a", "D1_s3b_m3a_BROKEN_20260922_005732.vi", None),
         (8, "m3a2", "D1_s3b_m3a2_20260922_023029.vi", None), (9, "m3a3", "D1_s3b_m3a3_20260922_081056.vi", None),
         (10, "rowD", "D1_s3b_m3a3b_rowD_20260922_161040.vi", 11)]
ORDER = [10, 3, 1, 2, 4, 5, 6, 7, 8, 9]          # the two CONTROLS first, so a deadline cannot lose them
SIBLINGS = ["D1_s3b_row1a_20260921_111413.vi", "D1_s3b_row1_20260921_111413.vi",
            "D1_s3b_row1a_20260921_135932.vi"]


def t1(s):
    s.head("[T1] THE 0 -> 1 CONTROL - can a scripted re-wire restore a VI headlessly on our route?")
    C82, V = K.mod("build_opfsinnertunnelconnect_v0"), K.mod("build_d1_v0")
    s.file_facts("T1 source", PC_VI)
    s.gate("T1a the positive-control source's md5 is {0}".format(PC_MD5), K.md5(PC_VI) == PC_MD5, K.md5(PC_VI))
    pc = s.scratch("pc", source=PC_VI)
    e0 = s.es("T1 untouched", target=pc)
    wm, _e = s.safe("T1 wmap(diagram 0)", lambda: V.wmap(pc, 0, fresh=True), {})
    rec = (wm or {}).get(PC_SINK_UID)
    s.gate("T1b node #{0} resolves on diagram 0 (uid echo)".format(PC_SINK_UID), rec is not None,
           "Nodes[{0}] label {1!r}".format(rec[0] if rec else None, rec[1] if rec else None))
    sink_i = rec[0] if rec else 0
    row = [r for r in (rec[2] if rec else []) if r["i"] == PC_SINK_TERM]
    w = (row[0]["wire"] if row else 0)
    s.fact("T1 sink row #{0} Nodes[{1}] t{2}: {3!r}; the wire feeding it is w{4}".format(
        PC_SINK_UID, sink_i, PC_SINK_TERM, row, w))
    # ROUTE 1: a NODE source on the same diagram. ROUTE 2 (run 1 measured route 1 EMPTY for w106): a
    # FRONT-PANEL control's own terminal, which `wmap`/`Diagram.Nodes[]` does not enumerate - `panel_wiring`
    # does, in the SAME Panel.Controls[] order `connect_ctl`'s `panel_index` takes (gscript.py:866/1023).
    src = [(u, rc[0], r["i"], r["name"]) for u, rc in sorted((wm or {}).items()) for r in rc[2]
           if r["wire"] == w and r["is_source"]]
    pw, _e = s.safe("T1 panel_wiring", lambda: g.panel_wiring(pc), [])
    psrc = [(i, r) for i, r in enumerate(pw or []) if r.get("wire") == w]
    s.fact("T1 sources for w{0}: NODE route {1!r} ; PANEL route {2!r}".format(w, src, psrc))
    n0 = g.count(pc, "Wire")
    _r, err = s.safe("T1 del_wire w{0}".format(w), lambda: C82.del_wire(pc, w, "T1 "))
    e1 = s.es("T1 after deleting w{0}".format(w), target=pc)
    if len(src) == 1:
        su, si, sti, sname = src[0]
        helper = "gscript.connect_terminals (OpConnect_v0): sink Nodes[{0}].t{1} <- #{2} Nodes[{3}].t{4} " \
                 "{5!r}".format(sink_i, PC_SINK_TERM, su, si, sti, sname)
        r2, err2 = s.safe("T1 " + helper, lambda: g.connect_terminals(pc, sink_i, PC_SINK_TERM, si, sti))
    elif len(psrc) == 1:
        pi, prow = psrc[0]
        helper = "gscript.connect_ctl (OpConnectCtl_v0): Panel.Controls[{0}] {1!r} -> Nodes[{2}].t{3}".format(
            pi, prow.get("label"), sink_i, PC_SINK_TERM)
        r2, err2 = s.safe("T1 " + helper, lambda: g.connect_ctl(pc, pi, sink_i, PC_SINK_TERM))
    else:
        helper, r2, err2 = "NO RE-WIRE ATTEMPTED - neither route named exactly one source", None, "no source"
        s.fact("T1 " + helper)
    e2 = s.es("T1 after re-creating the wire", target=pc)
    s.fact("T1 HELPER USED: {0} ; delete err {1!r} ; connect -> {2!r} err {3!r} ; Wire census {4} -> {5}".format(
        helper, err, r2, err2, n0, g.count(pc, "Wire")))
    s.row("T1 ExecState untouched / after delete / after re-wire", [e0, e1, e2], [1, 0, 1])
    s.gate("T1c ExecState went 1 -> 0 -> 1 (a scripted re-wire RESTORES a VI headlessly on our route)",
           (e0, e1, e2) == (1, 0, 1), "observed {0!r}".format((e0, e1, e2)))
    s.drop_scratch(pc, "H4 T1")


def probe(s, n, tag, fname, ctl):
    path = os.path.join(CD, fname)
    rec = s.file_facts("T2/{0} {1}".format(n, tag), path)
    if not rec["exists"] or s.left_s() < 95:
        s.fact("T2/{0} SKIPPED - {1}".format(n, "not on disk" if not rec["exists"] else
                                              "only {0:.0f} s left inside the deadline".format(s.left_s())))
        return
    sc = s.scratch(tag, source=path)
    es = s.es("T2/{0} {1}".format(n, tag), target=sc)
    before, _e = s.safe("T2/{0} report_all('Wire') before".format(n), lambda: g.report_all(sc, "Wire"), [])
    res, rerr = s.safe("T2/{0} remove_bad_wires_scripted".format(n), lambda: g.remove_bad_wires_scripted(sc))
    after, _e = s.safe("T2/{0} report_all('Wire') after".format(n), lambda: g.report_all(sc, "Wire"), [])
    aset = {r["uid"] for r in (after or [])}
    removed = sorted(r["uid"] for r in (before or []) if r["uid"] not in aset)
    sub = ("n/a (empty)" if not removed else "SUBSET of the 11" if set(removed) <= set(THE11) else
           "DISJOINT from the 11" if not set(removed) & set(THE11) else "OVERLAPS the 11 partially")
    s.fact("T2/{0} {1:<10} md5 {2} ExecState {3!r} | Wire {4} -> {5} | REMOVED {6} {7!r} | {8} | rbw {9!r} "
           "err {10!r}".format(n, tag, rec["md5"], es, len(before or []), len(after or []), len(removed),
                               removed, sub, res, rerr))
    s.R.setdefault("t2", []).append(
        {"n": n, "tag": tag, "file": fname, "md5": rec["md5"], "size": rec["size"], "exec_state": es,
         "wires_before": len(before or []), "wires_after": len(after or []), "removed_n": len(removed),
         "removed": removed, "vs_the11": sub})
    if ctl is not None:
        s.gate("T2-CTL{0} {1} removes exactly {2} wire(s){3}".format(
            n, tag, ctl, " and the set IS the c88 baseline" if ctl == 11 else ""),
            len(removed) == ctl and (ctl != 11 or removed == THE11), "got {0} {1!r}".format(len(removed), removed))
    s.drop_scratch(sc, "H4 T2/{0}".format(n))
    s.gate("T2/{0} the SOURCE {1} is md5-UNCHANGED after its probe".format(n, tag),
           K.md5(path) == rec["md5"], K.md5(path))
    s.dump()


def main(s):
    s.start()
    s.discard_work()
    # T1 IS RUN FIRST (the brief) BUT CANNOT COST T2: run 1 (`BGRUN END rc=1 after 114s`) fatal-stopped at
    # T1b2 and the bisection never ran. A T1 failure is now a FACT and a failed gate, never an abort.
    try:
        t1(s)
    except Exception as e:                                                         # noqa: BLE001
        s.gate("T1 completed without an unhandled exception", False, str(e)[:160])
    s.head("[T2] THE BISECTION - the RBW delete set on each saved stage artefact's own dated scratch")
    s.fact("T2/5 row-1 siblings found, NOT probed (one row-1 artefact only, deadline): {0!r}".format(
        [(f, K.md5(os.path.join(CD, f))) for f in SIBLINGS if os.path.exists(os.path.join(CD, f))]))
    by_n = {f[0]: f for f in FILES}
    for n in ORDER:
        probe(s, *by_n[n])
    s.head("[T2 SUMMARY] in BUILD ORDER")
    got = {r["n"]: r for r in s.R.get("t2", [])}
    for n, tag, fname, _c in FILES:
        r = got.get(n)
        s.fact("ROW {0:<2} {1:<52} {2}".format(n, fname, "NOT PROBED" if not r else
               "md5 {0} ExecState {1!r} wires {2}->{3} removed {4} {5!r} [{6}]".format(
                   r["md5"][:8], r["exec_state"], r["wires_before"], r["wires_after"], r["removed_n"],
                   r["removed"], r["vs_the11"])))
    first = sorted(r["n"] for r in got.values() if r["removed_n"] > 0)
    s.R["first_nonzero"] = first[0] if first else None
    s.fact("FIRST file in build order with a NON-ZERO removed count: {0}".format(
        (str(first[0]) + " = " + got[first[0]]["file"]) if first else "none of the probed files"))


S = K.Stage(BED, BED_MD5, "diag_c89_wirebirth", deadline_min=21.5, reserve_s=190.0,
            out_json=os.path.join(K.BENCH, "diag_c89_wirebirth.json"),
            task="0->1 ExecState control + which saved stage artefact first carries broken wires")
sys.exit(K.run(main, S))
