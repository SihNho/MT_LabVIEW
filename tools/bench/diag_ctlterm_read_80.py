r"""diag_ctlterm_read_80 - card 80-2 (PD178(i) items 1+3): read the WIRING of panel terminals (ControlTerminals)
headlessly, prove the reader on a labelled case, then measure K's two indicator rows #3173/#9519 on the D1_k bed.

PRIOR ART (checked before writing; NO new op VI is built):
  * `allterms.read_terms(vi, OP_ALLTERMS_V1)` already returns ControlTerminal rows - `docs/wiki/subvi/D1_s1_copy.json`
    :36695 term_uid 3173 'Pos within cal image' wire_uid 121 owner Diagram #639 (term_class ControlTerminal). The
    ControlTerminal IS the terminal object (term_uid == the ControlTerminal uid), so the table is the reader.
  * `gscript.report_all(vi,'ControlTerminal')` gives the ControlTerminal uid set (term_class is not an op column).
  * `gscript.panel_wiring` (OpPanelWiring_v0) = an independent panel-side route (label -> wire).
  * `stagekit.net_sources` (OpWireSource_v5) = independent wire-owner walk.
  * `Wire.Is Broken?` 6371004 has NO read-only op (only embedded in connect ops) -> PROXY: LabVIEW's Remove Bad Wires
    on a throwaway scratch; the wire uid SURVIVES = not broken. Stated as a proxy, not the property.
PREDICTION CONTRACT:
  M1 on a scratch of D1_s4_loop17: #3173 and #9519 each ONE row, is_source False, wire_uid 121, w121 has >=1 source
     row (the kernel's 'pos in cal image out'). Fails -> the reader is not a reader: STOP (card rule).
  M2 on a scratch of D1_k: reported, not predicted (judgement decides) - term row, wire, source owner, RBW survival.
  M3 count of ControlTerminals whose terminal name is one of the two labels: reported (expected 2 if no duplicates).
  M4 inputs md5 unchanged (H2/H3), refs opened==closed (H5), no file left (H6 == []), LabVIEW gone at the end.
Run: MATERIAL=1 py tools/bgrun.py --max-min 45 --log tools/bench/k_ind_read_80.log -- py -u tools/bench/diag_ctlterm_read_80.py
"""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                               # noqa: E402
import allterms as A                                                               # noqa: E402
import gscript as g                                                                # noqa: E402

CD = K.CLAUDEDEV
BED, BED_MD5 = os.path.join(CD, "D1_k_20260925_100155.vi"), "6cf5b0777aafa12112d8a786a9eed1ed"
S4, S4_MD5 = os.path.join(CD, "D1_s4_loop17.vi"), "4b621946492da3d2fbb96b6053e715ec"
UIDS = (3173, 9519)
LABELS = ("Pos within cal image", "Pos: Diffraction Pattern")
PINS = tuple(K.DEFAULT_PINS) + (("S4 L7-R", S4, S4_MD5), ("K bed", BED, BED_MD5))


def read(s, tag, vi):
    rows, dt = A.read_terms(vi, A.OP_ALLTERMS_V1)
    wuids, _ = A.all_wire_uids(vi)
    wires = dict((w["wire_uid"], w) for w in A.join_wires(rows, wuids))
    cts = set(o["uid"] for o in g.report_all(vi, "ControlTerminal"))
    s.fact("{0}: {1} terminal rows ({2:.1f} s), {3} Wire objects, {4} ControlTerminals".format(
        tag, len(rows), dt, len(wuids), len(cts)))
    out = {}
    for u in UIDS:
        hit = [r for r in rows if r["term_uid"] == u]
        r = hit[0] if len(hit) == 1 else None
        w = wires.get(r["wire_uid"]) if r and r["wire_uid"] else None
        srcs = [(x["owner_class"], x["owner_uid"], x["term_name"], x["term_uid"]) for x in rows
                if r and r["wire_uid"] and x["wire_uid"] == r["wire_uid"] and x["is_source"]]
        sinks = [(x["owner_class"], x["owner_uid"], x["term_name"], x["term_uid"]) for x in rows
                 if r and r["wire_uid"] and x["wire_uid"] == r["wire_uid"] and not x["is_source"]]
        s.fact("{0} #{1}: rows {2} is_ControlTerminal {3} row {4!r}".format(tag, u, len(hit), u in cts, r))
        s.fact("{0} #{1}: wire {2} n_src {3} n_sink {4} SOURCES {5!r} SINKS {6!r}".format(
            tag, u, r and r["wire_uid"], w and w["n_src"], w and w["n_sink"], srcs, sinks))
        out[u] = {"row": r, "wire": w, "srcs": srcs, "sinks": sinks, "n_rows": len(hit)}
    dup = sorted((x["term_name"], x["term_uid"], x["wire_uid"], x["owner_class"], x["owner_uid"], x["is_source"])
                 for x in rows if x["term_uid"] in cts and x["term_name"] in LABELS)
    s.fact("{0} M3 ControlTerminals carrying the two labels: {1} -> {2!r}".format(tag, len(dup), dup))
    pw, _e = s.safe("{0} panel_wiring".format(tag), lambda: g.panel_wiring(vi), [])
    s.fact("{0} panel_wiring rows with the labels: {1!r}".format(tag, [p for p in (pw or []) if p["label"] in LABELS]))
    return out, dup, wuids


def body(s):
    s.start()
    s.discard_work()                                        # a diagnostic: nothing is saved
    s.head("M1 LABELLED CASE - scratch of D1_s4_loop17 (w121 expected)")
    s4 = s.scratch("s4", S4)
    m1, _d, _w = read(s, "M1 S4", s4)
    for u in UIDS:
        m = m1[u]
        ok = m["row"] is not None and m["row"]["wire_uid"] == 121 and not m["row"]["is_source"] and len(m["srcs"]) >= 1
        s.gate("M1 #{0} read wired from w121 with a source".format(u), ok, repr(m["srcs"]), fatal=True)
    s.drop_scratch(s4, "M1")
    s.head("M2/M3 D1_k (work copy = byte copy of the bed)")
    m2, dup, _w = read(s, "M2 K", s.work)
    for u in UIDS:
        wu = (m2[u]["row"] or {}).get("wire_uid") or 0
        s.row("M2 #{0} wire".format(u), wu)
        if wu:
            s.net_sources(wu, tag="M2 #{0} w{1}".format(u, wu))
    s.row("M3 ControlTerminals with the two labels", len(dup), 2)
    s.head("M2b broken-wire PROXY - Remove Bad Wires on a throwaway scratch of D1_k")
    rb = s.scratch("rbw", BED)
    before = set(A.all_wire_uids(rb)[0])
    res = s.broken_wire_count(target=rb, tag="M2b")
    after = set(A.all_wire_uids(rb)[0])
    s.fact("M2b wires deleted by RBW: {0!r}".format(sorted(before - after)))
    for u in UIDS:
        wu = (m2[u]["row"] or {}).get("wire_uid") or 0
        s.row("M2b #{0} w{1} survives Remove Bad Wires (proxy for Is Broken? False)".format(u, wu),
              bool(wu) and wu in after)
    s.R["m2"] = {str(u): m2[u] for u in UIDS}
    s.R["m3"] = dup
    s.R["rbw"] = {"res": res, "deleted": sorted(before - after)}
    s.drop_scratch(rb, "M2b")


if __name__ == "__main__":
    st = time.strftime("%Y%m%d_%H%M%S")
    s = K.Stage(BED, BED_MD5, "scratch_ctl80", work_name="scratch_ctl80_k_{0}.vi".format(st), pins=PINS,
                deadline_min=40, out_json=os.path.join(K.BENCH, "k_ind_read_80.json"), task="card 80-2")
    rc = K.run(body, s)
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60)
    time.sleep(4.0)
    tl = subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
    s.gate("M4 LabVIEW process gone at the end", "labview.exe" not in tl)
    s.summary()
    sys.exit(1 if s.fails else 0)
