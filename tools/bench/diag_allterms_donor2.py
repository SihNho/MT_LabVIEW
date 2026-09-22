r"""diag_allterms_donor2 - REPAIR of the ONE invalid measurement in diag_allterms_donor.

`tools/bench/diag_allterms_donor.log` (12 pass / 1 fail, rc=1, 134 s) settled three of its four
questions and one it could not:
  PASS A1 `copy_by_index` has NO destination-diagram parameter  -> route (c) needs a NEW op.
  PASS A2 `loop_in` creates an EMPTY loop                        -> route (b) cannot enclose a TMSC.
  PASS A3 `drop_subvi` + `conpane_assign` + `create_control` all exist -> route (S) is available.
  PASS B1 the SAME Traverse wire into a `VI Server:GObject` node in the body reads `ExecState` **1**
          (`:33`), while `diag_allterms_cast` D1 read **0** into a `VI Server:Terminal` node - one
          variable, the node's class. The border tunnel is NOT the confound.
  FAIL C1 "some op VI carries a `To More Specific Class` inside a loop body": 0 hits - **but 16 of the
          26 candidates never got walked.** `net_map` raised LabVIEW **6503** ("The VI is not
          executable") on 20 diagrams, starting at `OpReportAll_v0` (`:116-135`), and every one of the
          16 is a LIVE gscript op VI. So C1's answer covers 10 op VIs, not 26, and "no donor exists"
          would be INFERENCE, not measurement.

THIS STAGE MEASURES ONLY THE 16, AND ON DATED SCRATCH COPIES so the target is never the very file
gscript is running ops out of. It builds no op and saves no deliverable.

PREDICTION CONTRACT (desk-checked, Pre-decided 132):
  R1 every one of the 16 scratch copies loads with `ExecState` **1** - they are the fleet's working
     ops, all ExecState-1 on disk, and a copy under a fresh name has no identity collision. A FAIL
     here would mean the 6503 was the op VI's own state, not the collision, and the diagnosis changes.
  R2 `net_map` returns rows (>=1 node) for at least 14 of the 20 loop-body diagrams - the same call
     that raised 6503 in place. A number, not a yes/no, because two of these ops (`OpShiftRegs_v1`)
     have 4 loop diagrams of which some may legitimately be empty.
  R3 THE DECIDER, re-asked over all 26 (10 already walked + these 16): at least one op VI carries a
     TMSC (`target class` / `specific class reference`, docs/NAMES.md:832) INSIDE a loop body.
     ⚠️ FREE, and the standing expectation is NO: the fleet's measured pattern is "cast ONCE on the
     root diagram, then loop over a TYPED array" - `subvis()` is documented as exactly that
     ("the cast-free identity route: AbstractDiagram.SubVIs[] -> For loop -> SubVI[...]",
     gscript.py:550-552) and `OpReportAll_v0` was walked in run 1 with no cast at all. A PASS makes
     route (a) the construction; a FAIL leaves route (S), the subVI-in-loop, as the only route left
     that Pre-decided 139 permits.

WHAT ALREADY EXISTS (checked first): `net_map`, `report`, `count`, `exec_state`, `stagekit.Stage`
(`scratch`/`drop_scratch`). NOTHING NEW IS WRITTEN HERE - inputs, gates, facts.

NO RESTART (`fresh=False`): a parallel material session may be driving LabVIEW's GUI. Originals
untouched (rule 1); every surface is a dated scratch copy under claudeDev, deleted at close. No
motor, no ASI, no camera; no VI is run.
  MATERIAL=1 py tools/bgrun.py --max-min 20 --log tools/bench/diag_allterms_donor2.log -- py -u tools/bench/diag_allterms_donor2.py
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                               # noqa: E402
import gscript as g                                                                # noqa: E402

SRC = os.path.join(K.CLAUDEDEV, "OpReport_v3.vi")
SRC_MD5 = "0743701a249b6ac20a5dab9ee676c09c"
TMSC_MARKS = ("target class", "specific class reference")
# the 16 that raised 6503 in run 1 (diag_allterms_donor.log:116-135), in that order
UNWALKED = ["OpReportAll_v0.vi", "OpShiftRegs_v0.vi", "OpShiftRegs_v1.vi", "OpStopFromNode_v0.vi",
            "OpSubVIs_v0.vi", "OpSubVIs_v1.vi", "OpTunnels_v0.vi", "OpWhileCast_v0.vi",
            "OpWireSRF_LeftIn_v0.vi", "OpWireSRF_LeftOutCtl_v0.vi", "OpWireSRF_LeftOutNode_v0.vi",
            "OpWireSRF_RightIn_v0.vi", "OpWireSR_LeftIn_v0.vi", "OpWireSR_LeftOutCtl_v0.vi",
            "OpWireSR_LeftOutNode_v0.vi", "OpWireSR_RightIn_v0.vi"]
WALKED_RUN1 = 10          # op VIs already walked clean, 0 hits (diag_allterms_donor.log:136)


def main(s):
    s.start()
    s.discard_work()

    s.head("[R] the 16 unwalked op VIs, each on a DATED SCRATCH COPY")
    loaded, rows_ok, diagrams, hits, per_vi = 0, 0, 0, [], []
    for name in UNWALKED:
        if s.left_s() < 120:
            s.fact("R deadline reserve reached - {0} of {1} done".format(len(per_vi), len(UNWALKED)))
            break
        src = os.path.join(K.CLAUDEDEV, name)
        dst = os.path.join(K.CLAUDEDEV, "donor2_{0}_{1}".format(s.stamp, name))
        shutil.copyfile(src, dst)
        s.scratches.append(dst)
        es = s.es("scratch " + name, target=dst)
        if es == 1:
            loaded += 1
        dias, _e = s.safe("R report(Diagram) " + name,
                          lambda q=dst: [(i, str(d.get("owner"))) for i, d in enumerate(g.report(q, "Diagram"))], [])
        bodies = [d for d in (dias or []) if "Loop" in d[1]]
        vi_rec = {"vi": name, "exec_state": es, "diagrams": dias, "bodies": [b[0] for b in bodies],
                  "walked": [], "hits": []}
        for i, owner in bodies:
            diagrams += 1
            rows, err = s.safe("R net_map {0} d{1}".format(name, i),
                               lambda q=dst, i=i: g.net_map(q, i, max_nodes=40, max_terms=10)[0], {})
            if rows:
                rows_ok += 1
            vi_rec["walked"].append({"diagram": i, "owner": owner, "nodes": len(rows or {}),
                                     "err": err[:90]})
            for _idx, row in (rows or {}).items():
                tnames = [t[1] for t in row[2]]
                if any(m in tnames for m in TMSC_MARKS):
                    hit = {"vi": name, "diagram_index": i, "diagram_owner": owner,
                           "node_uid": row[0], "label": row[1], "terminals": row[2]}
                    hits.append(hit)
                    vi_rec["hits"].append(hit)
                    s.fact("R HIT {0} diagram[{1}] owner={2} node uid={3} terms={4!r}".format(
                        name, i, owner, row[0], row[2]))
        per_vi.append(vi_rec)
        s.fact("R {0} ExecState={1!r} diagrams={2!r} bodies={3!r} walked={4!r}".format(
            name, es, dias, vi_rec["bodies"], [(w["diagram"], w["nodes"]) for w in vi_rec["walked"]]))
        s.drop_scratch(dst, tag="R-scratch")

    s.R["per_vi"] = per_vi
    s.R["tmsc_in_loop_body"] = hits
    s.R["totals"] = {"vis": len(per_vi), "loaded_es1": loaded, "loop_diagrams": diagrams,
                     "net_map_nonempty": rows_ok, "hits": len(hits)}
    s.fact("R TOTALS {0!r}".format(s.R["totals"]))

    s.gate("R1 all {0} scratch copies load with ExecState 1 (a FAIL moves the 6503 diagnosis from "
           "'identity collision with a live op' to 'the op VI's own state')".format(len(per_vi)),
           len(per_vi) > 0 and loaded == len(per_vi),
           "{0} of {1} at ExecState 1".format(loaded, len(per_vi)))
    s.gate("R2 net_map returns rows for >= 14 of the loop-body diagrams that raised 6503 in place",
           rows_ok >= 14, "{0} non-empty of {1} loop-body diagram(s)".format(rows_ok, diagrams))
    s.gate("R3 at least one op VI of the FULL 26 carries a To More Specific Class INSIDE a loop body "
           "(free; a PASS makes route (a) the construction, a FAIL leaves route (S))",
           bool(hits), "hits={0!r}; {1} op VIs walked clean in run 1 with 0 hits".format(
               [(h["vi"], h["diagram_index"], h["node_uid"]) for h in hits], WALKED_RUN1))


S = K.Stage(SRC, SRC_MD5, "diag_allterms_donor2", fresh=False, deadline_min=18.0, reserve_s=150.0,
            out_json=os.path.join(K.BENCH, "diag_allterms_donor2.json"),
            task="Re-walk the 16 op VIs whose net_map raised 6503 in diag_allterms_donor, on dated "
                 "scratch copies: does ANY op VI carry a To More Specific Class inside a loop body? "
                 "Read-only; every scratch deleted at close. Nothing saved.")
sys.exit(K.run(main, S))
