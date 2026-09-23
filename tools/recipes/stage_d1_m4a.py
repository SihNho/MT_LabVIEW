r"""stage_d1_m4a - cycle 68 BUILD M4a: loop 1.5 (#23032, body #23058) takes the RISING EDGE of the schedule Local #23499
instead of its level: new boolean shift register, Not(SR-left) -> And.y, Local -> And.x, And -> #10407 t0 (case selector),
Local -> SR-right; executed from `tools/bench/decision_m4a.json` by `stagekit.from_decision` (Pre-decided 143 op_rule
checked per row). Row `init_false` is NOT executed (no verb: record's `why`) - the register is left UNINITIALISED.
PRIOR ART (checked first): stagekit (Stage, from_decision + the cycle-68 creator rows copy_in/add_sr_row/const_row,
cfw_second_pass, live_graph), gscript.copy_by_index's op OpMoveByIndex_v0 on the NI Moving-Objects pair, OpWireSR_*,
OpConnectNested_v1, OpConnectFromWire_v0, vigraph.diff/computation_diff (stage_d1_m3a4.py:103-129). No op VI built.
The copier's record (prior-art c68-m4a A4/B2): diag_s56_transport3.log:93-109 + cycle27-plan item (h) = copy_by_index's
own finish gate refusing an unwired duplicated Local; q_m4_copy_probe.log:21 = the bed at MOVE_DST reads ExecState 1
with no preload, :50-52 = copy_in + move_in place exactly one Not owned by #23058 (D2+D4 measured on this bed).
PREDICTION CONTRACT (as DIFFERENCES from the bed, Pre-decided 132; bed facts tools/bench/q_m4_probe.log):
  P0 bed ExecState 1 (determined by M3a-4, re-read, not a test).  P1 every executable row: no error; init_false NOT EXECUTED.
  P2 Function +2, Wire +3 (-w23847, +Local net, +SR-left->Not, +Not->And, +And->case), Node +2, strays purged.
  P3 ExecState after the rows = 1 (an uninitialised register is legal; nothing earlier determines this value).
  P4 ordered second pass: 4 wires, wire_delta 0 and `Is Broken?` False each.  P5 scripted save; RBW on a scratch of the
     saved file removes 0.  P6 diff(bed,new): nodes_added == {not, and, SR right, SR left}, nodes_removed []; every
     removed edge touches #23499/#10429/#10407; every added edge touches a new node.  P7 computation_diff(S1,new) rows
     REPORTED VERBATIM (ASSUMPTION A; no gate on their count).  P8 bed md5 + 6 pins unchanged; files left == [the artefact].
    py tools/bgrun.py --material --max-min 45 --log tools/bench/stage_d1_m4a.log -- py -u tools/recipes/stage_d1_m4a.py
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

BED = os.path.join(K.CLAUDEDEV, "D1_s3b_m3a4_20260923_185345.vi")
BED_MD5 = "fdd6d74ac8a5ba0c1a545ad89ff2996f"
FINAL = os.path.join(K.CLAUDEDEV, "D1_s3b_m4a_{0}.vi".format(time.strftime("%Y%m%d_%H%M%S")))
REC = json.load(open(os.path.join(K.BENCH, "decision_m4a.json"), encoding="utf-8"))
RET = json.load(open(os.path.join(K.BENCH, "decision_m3a4_v2.json"), encoding="utf-8"))["predict"][
    "diff_bed_new_nodes_removed"]
CLS = ("Function", "Wire", "Node", "Local", "WhileLoop")


def body(s):
    s.start()
    shutil.copyfile(BED, g.MOVE_SRC)                  # the donor = the bed's own bytes (a copy; the bed is never opened)
    s.gate("K4 MOVE_SRC holds the bed's bytes", K.md5(g.MOVE_SRC) == BED_MD5, K.md5(g.MOVE_SRC), fatal=True)
    s.gate("P0 bed ExecState 1 on open", s.es("P0 on open") == 1, fatal=True)
    b = dict((c, s.count(c)) for c in CLS)
    s.fact("CENSUS before {0}".format(b))
    Gb = s.live_graph(s.work, RET)
    s.head("[1] from_decision: {0} rows".format(len(REC["decisions"])))
    out = s.from_decision(REC, "m4a")
    errs = [(r["id"], r.get("error")) for r in out if r.get("error")]
    s.gate("P1 every executable row ran without an error", not errs, errs)
    s.gate("P1b init_false NOT EXECUTED (no verb)", "NOT EXECUTED" in str(out[-1].get("result")), out[-1].get("result"))
    a = dict((c, s.count(c)) for c in CLS)
    dlt = dict((c, a[c] - b[c]) for c in CLS)
    s.fact("CENSUS after {0} ; delta {1}".format(a, dlt))
    s.gate("P2 Function +2, Wire +3 (-1 +4; a branch adds no Wire), Node +2 (the copies; strays purged), Local/Loop +0",
           dlt == {"Function": 2, "Wire": 3, "Node": 2, "Local": 0, "WhileLoop": 0}, dlt)
    es = s.es("P3 after all rows")
    if not s.gate("P3 ExecState 1 after the rows", es == 1, es):
        s.fact("NOTHING SAVED - STOP (failed prediction P3); the unsaved Target is reverted by the fixture restore")
        return
    s.head("[2] ordered second pass (42(b)) on the four new wires")
    n, a_, sr = s.sym["not"], s.sym["and"], s.sym["sr"]
    E = lambda u, t: {"uid": u, "term": t, "diagram": 23058, "owner_class": "", "term_class": ""}
    for lab, src, dst in (("not->and.y", n, E(a_, "y")), ("and->case", a_, E(10407, "")),
                          ("sched->and.x (same net as sched->SR-right)", 23499, E(a_, "x")),
                          ("SR-left->not.x", sr["left"], E(n, "x"))):
        s.expect_is_broken_false(lab, lambda src=src, dst=dst: s.cfw_second_pass(src, dst))
    s.gate("P4b ExecState still 1 after the second pass", s.es("after 2nd pass") == 1)
    s.head("[3] save + copy to the artefact + RBW on a scratch")
    m = s.save()
    shutil.copyfile(s.work, FINAL)
    s.gate("P5a artefact == the saved Target bytes", K.md5(FINAL) == m, "{0} {1}".format(FINAL, m))
    sc = s.scratch("rbw", source=FINAL)
    rb = s.broken_wire_count(target=sc, tag="P5b scratch of the artefact")
    s.gate("P5b Remove Bad Wires removes 0 on the saved artefact", rb["bad"] == 0, rb)
    s.drop_scratch(sc)
    s.head("[4] live map -> diff(bed,new) / computation_diff(S1,new)")
    Gn = s.live_graph(s.work, RET, {23032: [sr["right"]]})
    d = V.diff(Gb, Gn)
    want = {n, a_, sr["right"], sr["left"]}
    s.gate("P6a nodes_added == {0}, nodes_removed []".format(sorted(want)),
           set(d["nodes_added"]) == want and not d["nodes_removed"], (d["nodes_added"], d["nodes_removed"]))
    nd = lambda k: V.key_parts(k)[0]
    sh = lambda es_: [(k, V.show(x), V.show(y)) for k, x, y in es_]
    s.fact("diff(bed,new) edges_removed {0}".format(sh(d["edges_removed"])))
    s.fact("diff(bed,new) edges_added {0}".format(sh(d["edges_added"])))
    rem = [e for e in d["edges_removed"] if not {nd(e[1]), nd(e[2])} & {23499, 10429, 10407}]
    add = [e for e in d["edges_added"] if not {nd(e[1]), nd(e[2])} & want]
    s.gate("P6b every removed edge touches #23499/#10429/#10407; every added edge touches a new node",
           not rem and not add, (sh(rem), sh(add)))
    cd = V.computation_diff(JC.load(JC.S1_KEY), Gn)
    for r in cd["rows"]:
        s.fact("CDIFF ROW {0}".format(dict((k, V.show(v) if k == "sink" else v) for k, v in r.items())))
    s.fact("CDIFF rows {0}; computation_nodes_added {1}; removed {2}".format(
        len(cd["rows"]), [(x["node"], x.get("class")) for x in cd["computation_nodes_added"]],
        cd["computation_nodes_removed"]))
    s.gate("P8a bed md5 unchanged", K.md5(BED) == BED_MD5, K.md5(BED))
    s.R["m4a"] = {"final": FINAL, "md5": m, "bytes": os.path.getsize(FINAL), "sym": s.sym, "cdiff_rows": len(cd["rows"])}
    s.dump()


class St(K.Stage):
    def close(self, expect_files=None):
        return K.Stage.close(self, [os.path.basename(FINAL)] if os.path.exists(FINAL) else [])


if __name__ == "__main__":
    g.restore_move_fixtures()
    FXL = K.fixture_listing()
    st = St(BED, BED_MD5, "stage_d1_m4a", preload=False, deadline_min=42, work_dir=os.path.dirname(g.MOVE_DST),
            work_name=os.path.basename(g.MOVE_DST), pins=tuple(K.DEFAULT_PINS) + (("M3a-4 bed", BED, BED_MD5),),
            task="cycle 68 M4a: rising-edge SR + Not + And in loop 1.5 from decision_m4a.json")
    rc = K.run(body, st)
    K.mod("bench_prep").restart_labview()
    g.reset()
    g.restore_move_fixtures()
    sys.exit(rc if K.fixtures_check((BED_MD5, K.md5(FINAL) if os.path.exists(FINAL) else ""), FXL) else 1)
