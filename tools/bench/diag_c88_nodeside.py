# -*- coding: utf-8 -*-
"""D-1 READER, PART 2: ask the NODES which wire they carry - the c88 review's cheapest discriminating test.

MEASUREMENT ONLY, read-only, no mutation, no new op, nothing saved. Run verbatim from
`archive/peer/2026-09-22-c88-walk-1055.md` section (d), which is the ANSWERED mandatory failed-prediction
review of gate G3 in `tools/bench/diag_c88_brokenwires.log`. Its point: this project's own definition of an
orphan is "a wire NO NODE TERMINAL carries" (docs/NAMES.md:1014), so the wire-side walk tested the wrong side.

PRIOR ART: `tools/stagekit.py` (the kit); `gscript.node_terms():910` (ONE op run per node, 0 junk per call -
built for exactly this, preferred over `net_map` which leaves ~75 Invoke nodes); `gscript.panel_wiring():866`
(ONE run, every front-panel object's terminal and the wire on it - a node sweep structurally CANNOT see a
`ControlTerminal` endpoint, whose Owner is the diagram, not a node); `build_d1_v0.diag_index():357`.
Nothing new is written.

PREDICTION CONTRACT:
  N1  the node sweep covers every node of `Diagram #639` inside the budget (no truncation).
  N2  all FOUR wires the wire-side walk answered for (1731, 3947, 9635, 7337) are found on the node side.
  N3  NONE of the other seven (1893, 2819, 4833, 7388, 11232, 23502, 23540) is found on the node side
      nor in the panel-wiring table.
  Per the review: N3 holding ⇒ the wire-side reading is confirmed by an independent route; any of the seven
  appearing ⇒ it is REFUTED and `Wire.Terms[]` under-reports on broken wires. The READING is the deliverable;
  the interpretation is judgement's.
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import stagekit as K                                                               # noqa: E402
import gscript as g                                                                # noqa: E402

ART = os.path.join(K.CLAUDEDEV, "D1_s3b_m3a3b_rowD_20260922_161040.vi")
ART_MD5 = "0b84595245dd650c0e8fd3f57104782c"
BROKEN = [1731, 1893, 2819, 3947, 4833, 7337, 7388, 9635, 11232, 23502, 23540]
ANSWERED = [1731, 3947, 9635, 7337]          # the four the wire-side walk resolved
SILENT = [u for u in BROKEN if u not in ANSWERED]
DIAG = 639
BUDGET_S = 600.0


def body(s):
    s.start()
    s.discard_work()
    B = K.mod("build_d1_v0")

    s.head("[A] Diagram #{0} - the owning diagram of all 11 broken wires".format(DIAG))
    idx, _e = s.safe("diag_index(#{0})".format(DIAG), lambda: B.diag_index(s.work, DIAG))
    rows, _e = s.safe("node_labels(#{0})".format(DIAG), lambda: g.node_labels(s.work, idx), [])
    s.fact("Diagram #{0} = traverse index {1}, {2} node(s)".format(DIAG, idx, len(rows or [])))
    s.gate("N0 Diagram #{0} resolved and lists nodes".format(DIAG), bool(rows), "", fatal=True)

    s.head("[B] NODE SWEEP - g.node_terms per node, one op run each, 0 junk per call")
    want = set(BROKEN)
    hits, scanned, errors = {}, 0, 0
    t0 = time.time()
    for k, r in enumerate(rows):
        if time.time() - t0 > BUDGET_S:
            s.fact("SWEEP STOPPED at node {0}/{1} on the {2:.0f} s budget".format(k, len(rows), BUDGET_S))
            break
        terms, err = s.safe("node_terms[{0}]".format(k), lambda kk=k: g.node_terms(s.work, idx, kk), [])
        scanned += 1
        if err:
            errors += 1
            continue
        for t in (terms or []):
            if t.get("wire") in want:
                hits.setdefault(t["wire"], []).append(
                    {"node_index": k, "node_uid": t.get("node_uid"), "node_label": r.get("label"),
                     "t": t.get("i"), "name": t.get("name"), "is_source": t.get("is_source"),
                     "errs": [t.get("name_err"), t.get("src_err"), t.get("conn_err"), t.get("wire_err")]})
    s.fact("NODE SWEEP: {0} of {1} node(s) scanned, {2} read error(s), {3:.0f} s".format(
        scanned, len(rows), errors, time.time() - t0))
    s.gate("N1 the sweep covered every node of Diagram #{0}".format(DIAG), scanned == len(rows),
           "{0}/{1}".format(scanned, len(rows)))

    s.head("[C] PANEL WIRING - the ControlTerminal endpoints a node sweep cannot see")
    prows, perr = s.safe("panel_wiring", lambda: g.panel_wiring(s.work), [])
    phits = {}
    for p in (prows or []):
        if p.get("wire") in want:
            phits.setdefault(p["wire"], []).append(
                {"label": p.get("label"), "indicator": p.get("indicator"), "uid": p.get("uid"),
                 "is_source": p.get("is_source"), "errs": [p.get("term_err"), p.get("wire_err")]})
    s.fact("panel_wiring: {0} front-panel row(s) (err {1!r}); {2} of them carry a broken wire".format(
        len(prows or []), perr, sum(len(v) for v in phits.values())))

    s.head("[D] THE TABLE - every broken wire, its node-side endpoints, with TERMINAL NAMES")
    for u in BROKEN:
        n = hits.get(u, [])
        p = phits.get(u, [])
        s.fact("w{0:<6} node-side {1} endpoint(s) {2!r} | panel-side {3} {4!r}".format(
            u, len(n),
            [("#{0}".format(e["node_uid"]), e["node_label"], "t{0}".format(e["t"]), e["name"],
              "SRC" if e["is_source"] else "snk") for e in n],
            len(p), [(e["label"], "SRC" if e["is_source"] else "snk") for e in p]))
    s.R["node_side"] = {str(u): {"nodes": hits.get(u, []), "panel": phits.get(u, [])} for u in BROKEN}

    found_ans = [u for u in ANSWERED if hits.get(u) or phits.get(u)]
    found_sil = [u for u in SILENT if hits.get(u) or phits.get(u)]
    s.gate("N2 all four wire-side-ANSWERED wires are found on the node side",
           len(found_ans) == len(ANSWERED), "found {0!r} of {1!r}".format(found_ans, ANSWERED))
    s.gate("N3 none of the seven wire-side-SILENT wires is found on the node/panel side",
           not found_sil, "found {0!r} of {1!r}".format(found_sil, SILENT))
    s.fact("VERDICT ROUTE (review section (d)): answered-found {0}/4, silent-found {1}/7".format(
        len(found_ans), len(found_sil)))
    s.dump()


if __name__ == "__main__":
    st = K.Stage(ART, ART_MD5, "diag_c88_nodeside", fresh=True, deadline_min=26.0,
                 out_json=os.path.join(K.BENCH, "diag_c88_nodeside.json"),
                 task="the c88 review's cheapest discriminating test: ask the nodes which wire they carry")
    sys.exit(K.run(body, st))
