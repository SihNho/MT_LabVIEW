r"""stage_d1_m4b - cycle 68 BUILD M4b, FROM M4a's SAVED FILE in a FRESH LabVIEW: `Wait (ms)` in loop 1.5's body #23058 with
input = constant 1 (U32, typed by the sink), from `tools/bench/decision_m4b.json` by `stagekit.from_decision`.
PRIOR ART (checked first): identical machinery to stage_d1_m4a.py (stagekit copy_in on the NI Moving-Objects pair,
const_row = OpCreateConstOnTerm_v0 `build_opcreateconstonterm_v0.create_const_on_term`:364, cfw_second_pass, live_graph,
vigraph.diff/computation_diff). No op VI built. Copier measured on this bed at MOVE_DST: q_m4_copy_probe.log:21,:50-52.
Saved as D1_s3b_m4b_<stamp>.vi, NOT D1_s3_loop15.vi: M4a's init_false row has no verb, the name is judgement's.
PREDICTION CONTRACT (differences from M4a, Pre-decided 132):
  P0 M4a ExecState 1 on a COLD open in a fresh LabVIEW (M4a measured only warm - this is the first cold read).
  P1 both rows no error; the const op's own error columns empty and created uid non-zero.
  P2 Function +1, Node +1, Wire +1 (constant -> Wait), Local/WhileLoop +0.   P3 ExecState 1 after the rows.
  P4 second pass on const->Wait: wire_delta 0, `Is Broken?` False.   P5 scripted save, RBW 0 on a scratch of it,
     ExecState 1 COLD in a fresh LabVIEW.   P6 diff(M4a,new) nodes_added == {wait, const}, nodes_removed []; wire/fs
     edges keyed by TERMINAL UID: none removed, every added one touches them (sr not gated: TOP-y pairing, q_m4a_diffuid).  P7 computation_diff(S1,new) rows VERBATIM.  P8 pins + M4a md5 unchanged.
    py tools/bgrun.py --material --max-min 45 --log tools/bench/stage_d1_m4b.log -- py -u tools/recipes/stage_d1_m4b.py
"""
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import stagekit as K                                                               # noqa: E402
import gscript as g                                                                # noqa: E402
import vigraph as V                                                                # noqa: E402
import jev_candidates as JC                                                        # noqa: E402

BED = os.path.join(K.CLAUDEDEV, "D1_s3b_m3a4_20260923_185345.vi")                  # the donor of Wait (ms) #22343
BED_MD5 = "fdd6d74ac8a5ba0c1a545ad89ff2996f"
M4A = json.load(open(os.path.join(K.BENCH, "stage_d1_m4a.json"), encoding="utf-8"))["m4a"]
IN, IN_MD5 = M4A["final"], M4A["md5"]
FINAL = os.path.join(K.CLAUDEDEV, "D1_s3b_m4b_{0}.vi".format(time.strftime("%Y%m%d_%H%M%S")))
REC = json.load(open(os.path.join(K.BENCH, "decision_m4b.json"), encoding="utf-8"))
RET = json.load(open(os.path.join(K.BENCH, "decision_m3a4_v2.json"), encoding="utf-8"))["predict"][
    "diff_bed_new_nodes_removed"]
CLS = ("Function", "Wire", "Node", "Local", "WhileLoop")
XR = {23032: [M4A["sym"]["sr"]["right"]]}


def body(s):
    s.start()                                         # restart first: the open below IS M4a's first COLD read
    shutil.copyfile(BED, g.MOVE_SRC)
    s.gate("K4 MOVE_SRC holds the bed's bytes", K.md5(g.MOVE_SRC) == BED_MD5, K.md5(g.MOVE_SRC), fatal=True)
    s.gate("P0 M4a ExecState 1 on a COLD open (fresh LabVIEW)", s.es("P0 cold open") == 1, fatal=True)
    b = dict((c, s.count(c)) for c in CLS)
    Gb = s.live_graph(s.work, RET, XR)
    out = s.from_decision(REC, "m4b")
    errs = [(r["id"], r.get("error")) for r in out if r.get("error")]
    s.gate("P1 both rows ran without an error", not errs, errs)
    cr = (s.sym.get("c1") or {}).get("result") or {}
    s.gate("P1b const op: error columns empty, created uid non-zero",
           not cr.get("err") and not cr.get("inv_err") and cr.get("created_uid"), cr)
    a = dict((c, s.count(c)) for c in CLS)
    dlt = dict((c, a[c] - b[c]) for c in CLS)
    s.fact("CENSUS {0} -> {1} ; delta {2}".format(b, a, dlt))
    s.gate("P2 Function +1, Node +1, Wire +1, Local/Loop +0",
           dlt == {"Function": 1, "Wire": 1, "Node": 1, "Local": 0, "WhileLoop": 0}, dlt)
    if not s.gate("P3 ExecState 1 after the rows", s.es("P3 after rows") == 1):
        s.fact("NOTHING SAVED - STOP (failed prediction P3)")
        return
    w, c = s.sym["wait"], int(cr["created_uid"])
    s.expect_is_broken_false("const->wait", lambda: s.cfw_second_pass(
        c, {"uid": w, "term": "milliseconds to wait", "diagram": 23058, "owner_class": "", "term_class": ""}))
    m = s.save()
    shutil.copyfile(s.work, FINAL)
    s.gate("P5a artefact == the saved Target bytes", K.md5(FINAL) == m, "{0} {1}".format(FINAL, m))
    sc = s.scratch("rbw", source=FINAL)
    rb = s.broken_wire_count(target=sc, tag="P5b scratch of the artefact")
    s.gate("P5b Remove Bad Wires removes 0 on the saved artefact", rb["bad"] == 0, rb)
    s.drop_scratch(sc)
    Gn = s.live_graph(s.work, RET, XR)
    d = V.diff(Gb, Gn)
    want = {w, c}
    ub, un = K.uid_edges(Gb), K.uid_edges(Gn)          # review c68-m4a-p6b: wire/fs keyed by TERMINAL UID
    rem, add = sorted(ub - un), sorted(un - ub)
    s.fact("diff(M4a,new) name-keyed counts {0}; UID-keyed wire/fs removed {1} added {2}".format(d["counts"], rem, add))
    s.gate("P6 nodes_added == {0}, nodes_removed []; uid-keyed wire/fs: none removed, every added touches them".format(
        sorted(want)), set(d["nodes_added"]) == want and not d["nodes_removed"] and not rem and
           all({e[1], e[3]} & want for e in add), (d["nodes_added"], d["nodes_removed"], rem, add))
    cd = V.computation_diff(JC.load(JC.S1_KEY), Gn)
    for r in cd["rows"]:
        s.fact("CDIFF ROW {0}".format(dict((k, V.show(v) if k == "sink" else v) for k, v in r.items())))
    s.fact("CDIFF rows {0}; computation_nodes_added {1}; removed {2}".format(
        len(cd["rows"]), [(x["node"], x.get("class")) for x in cd["computation_nodes_added"]],
        cd["computation_nodes_removed"]))
    s.head("[COLD] fresh LabVIEW, the artefact opened cold")
    s.restart()
    s.gate("P5c ExecState 1 COLD in a fresh LabVIEW", s.es("cold reopen", target=FINAL) == 1)
    s.gate("P8 M4a md5 unchanged", K.md5(IN) == IN_MD5, K.md5(IN))
    s.R["m4b"] = {"final": FINAL, "md5": m, "bytes": os.path.getsize(FINAL), "sym": s.sym, "cdiff_rows": len(cd["rows"])}
    s.dump()


class St(K.Stage):
    def close(self, expect_files=None):
        return K.Stage.close(self, [os.path.basename(FINAL)] if os.path.exists(FINAL) else [])


if __name__ == "__main__":
    g.restore_move_fixtures()
    FXL = K.fixture_listing()
    st = St(IN, IN_MD5, "stage_d1_m4b", preload=False, deadline_min=42, work_dir=os.path.dirname(g.MOVE_DST),
            work_name=os.path.basename(g.MOVE_DST),
            pins=tuple(K.DEFAULT_PINS) + (("M3a-4 bed", BED, BED_MD5), ("M4a", IN, IN_MD5)),
            task="cycle 68 M4b: Wait (ms) + constant 1 in loop 1.5, from the M4a artefact")
    rc = K.run(body, st)
    K.mod("bench_prep").restart_labview()
    g.reset()
    g.restore_move_fixtures()
    sys.exit(rc if K.fixtures_check((BED_MD5, IN_MD5, K.md5(FINAL) if os.path.exists(FINAL) else ""), FXL) else 1)
