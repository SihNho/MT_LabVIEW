r"""stage_d1_m3a4 - connectivity-map-plan STEP 6.1-6.3: M3a-4 = the RETIREMENT (Pre-decided 142/143/146), executed from
the re-verified record `tools/bench/decision_m3a4_v2.json` (6.0, `tools/bench/m3a4_reverify.py`, 0 verdicts changed).

PRIOR ART, NOT RE-TYPED: stagekit.Stage (pins, dated work copy, from_decision, broken_wire_count = Remove Bad Wires,
save, restart, close), wiki_build.read_live + jev_candidates.from_parts (the live map, as bench B), vigraph.diff/
computation_diff, lv_errorlist.read (only if ExecState 0). No op VI is built; no original is opened (preload=False).

PREDICTION CONTRACT (every number desk-checked against the step that determines it - Pre-decided 132; the record's
`predict` block was computed OFFLINE from the completed bed graph, and 635/1920/the RBW set were MEASURED on this bed by
diag_c88/diag_c89):
  P0  bed census Node 635, Wire 1920 (re-measured, determined by the bed) ; each carrier is in its OWN class traverse
      (prior-art m3a4-step6 B4: tunnels/registers are not in `Node`)
  P1  from_decision: 4 half-wire deletes (1731 3947 9635 7337) + 8 retires -> per class gone == exactly its carriers,
      Node 635 -> 632 (the 3 Invokes only), no new uid in any class ;
      Wire gone == exactly the 4 -> 1916 (a register-pair delete may take its partner: counted by census, not by op)
  P2  Remove Bad Wires removes exactly the 7 termless leftovers [1893 2819 4833 7388 11232 23502 23540] -> 1909,
      Node unchanged ; P3 ExecState 1 (if 0: Error List read, nothing saved, STOP)
  P4  scripted save -> ExecState 1 warm; fresh LabVIEW -> ExecState 1 cold; the bed's md5 unchanged
  P5  live map of the saved file: diff(bed,new) nodes_removed == the 8, nodes_added [], edges_added [], edges_removed ==
      the 6 predicted ; computation_diff(S1,new) rows 0, added == [10171 23035 23042 23541 23576] (S3a/S3b), removed []

    MATERIAL=1 py tools/bgrun.py --max-min 45 --log tools/bench/stage_d1_m3a4.log -- py -u tools/recipes/stage_d1_m3a4.py
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import stagekit as K                                                               # noqa: E402
import gscript as g                                                                # noqa: E402
import vigraph as V                                                                # noqa: E402
import jev_candidates as JC                                                        # noqa: E402

BED = os.path.join(K.CLAUDEDEV, "D1_s3b_m3a3b_rowD_20260922_161040.vi")
BED_MD5 = "0b84595245dd650c0e8fd3f57104782c"
REC = json.load(open(os.path.join(K.BENCH, "decision_m3a4_v2.json"), encoding="utf-8"))
P = REC["predict"]
# prior-art m3a4-step6 B4 (already measured: c89 :141, plan 4b): tunnels and shift registers are NOT in the `Node`
# traverse - each carrier class is counted in its OWN traverse; `Node` loses only the 3 Invokes (c89: 635 -> 632).
CR = P["class_removed"]
CLS = ("Node", "Wire") + tuple(k for k in sorted(CR) if k != "Node")


def snap(s):
    return dict((c, set(g.uids(s.work, c))) for c in CLS)


def body(s):
    s.start()
    s.gate("K4 the record was re-verified on THIS bed", REC["bed_md5"] == BED_MD5 and not REC["changed_vs_142"],
           REC["changed_vs_142"], fatal=True)
    b = snap(s)
    s.fact("CENSUS before: {0}".format(dict((c, len(v)) for c, v in b.items())))
    s.gate("P0a bed Node {0} == {1}".format(len(b["Node"]), P["node_before"]), len(b["Node"]) == P["node_before"])
    s.gate("P0b bed Wire {0} == {1}".format(len(b["Wire"]), P["wire_before"]), len(b["Wire"]) == P["wire_before"])
    ret = set(P["diff_bed_new_nodes_removed"])
    miss = [(k, u) for k, us in CR.items() for u in us if u not in b[k]]
    s.gate("P0c every carrier is in its OWN class traverse", not miss, miss, fatal=True)
    s.head("[3] from_decision: {0} rows".format(len(REC["decisions"])))
    out = s.from_decision(REC, "m3a4")
    a = snap(s)
    s.fact("CENSUS after the deletes: {0}".format(dict((c, len(v)) for c, v in a.items())))
    s.es("after the deletes")
    for k, us in CR.items():
        s.gate("P1a {0} gone == {1}, nothing new".format(k, us), sorted(b[k] - a[k]) == us and not a[k] - b[k],
               "gone {0} new {1}".format(sorted(b[k] - a[k]), sorted(a[k] - b[k])))
    s.gate("P1a Node {0} -> {1} (only the Invokes), nothing new".format(len(b["Node"]), P["node_after"]),
           len(a["Node"]) == P["node_after"] and not a["Node"] - b["Node"],
           "gone {0} new {1}".format(sorted(b["Node"] - a["Node"]), sorted(a["Node"] - b["Node"])))
    dw = set(x["exec"]["wire_uid"] for x in REC["decisions"] if x["action"] == "delete")
    s.gate("P1b Wire gone == {0} -> {1}".format(sorted(dw), P["wire_after_deletes"]),
           b["Wire"] - a["Wire"] == dw and not a["Wire"] - b["Wire"],
           "gone {0} new {1}".format(sorted(b["Wire"] - a["Wire"]), sorted(a["Wire"] - b["Wire"])))
    s.gate("P1c every row executed without an error", not any(r.get("error") for r in out),
           [r.get("error") for r in out if r.get("error")])
    s.head("[4] Remove Bad Wires (scripted)")
    rb = s.broken_wire_count(allow_mutation=True, tag="m3a4")
    c = snap(s)
    s.gate("P2a RBW removed exactly {0}".format(P["rbw_removes"]),
           sorted(a["Wire"] - c["Wire"]) == P["rbw_removes"] and not c["Wire"] - a["Wire"],
           "removed {0} new {1}".format(sorted(a["Wire"] - c["Wire"]), sorted(c["Wire"] - a["Wire"])))
    s.gate("P2b every class census unchanged by RBW (tunnels/registers included)",
           all(c[k] == a[k] for k in CLS if k != "Wire"), dict((k, len(c[k])) for k in CLS))
    es = s.es("after Remove Bad Wires")
    if not s.gate("P3 ExecState 1 after the retirement", es == 1, es):
        import lv_errorlist as E
        s.safe("open_panel", lambda: g.open_panel(s.work))
        el, err = s.safe("Error List", lambda: E.read(s.work, os.path.join(K.BENCH, "errorlist_m3a4_{0}.json".format(
            s.stamp)), log=s.fact), {})
        for i in (el or {}).get("items") or []:
            s.fact("ERRORLIST {0}: {1!r} | {2!r} | {3!r}".format(i.get("index"), i.get("object"), i.get("reason"),
                                                                 (i.get("detail") or "")[:160]))
        s.fact("ERRORLIST count {0!r} (window N {1!r}); NOTHING SAVED - STOP".format(
            len((el or {}).get("items") or []), (el or {}).get("n_reported")))
        s.discard_work()
        return
    s.head("[5] save + cold reopen")
    m = s.save()
    s.restart()
    s.gate("P4 ExecState 1 COLD in a fresh LabVIEW", s.es("cold reopen, fresh instance") == 1)
    s.head("[6] live map of the saved file -> diff / computation_diff")
    import wiki_build as W
    Gb, Gs = JC.load(JC.BED_KEY), JC.load(JC.S1_KEY)
    live = W.read_live(s.work, fs_pairs=Gb["wiki"]["fs_tunnel_pairs"])
    loops = [dict(l, right_uids=[u for u in l["right_uids"] if u not in ret]) for l in
             json.load(open(JC._newest("graph_loops_bed_*.json"), encoding="utf-8"))["loops"]]
    Gn = JC.from_parts({"terminals": live["terminals"], "graph_summary": Gb["wiki"]["graph_summary"]}, live["objs"],
                       loops, JC.node_labels_default(), live["fs_tunnel_pairs"], "m3a4")
    d = V.diff(Gb, Gn)
    er = sorted([k, V.show(x), V.show(y)] for k, x, y in d["edges_removed"])
    s.gate("P5a diff(bed,new) nodes_removed == the 8, nodes_added []", set(d["nodes_removed"]) == ret and
           not d["nodes_added"], "removed {0} added {1}".format(d["nodes_removed"], d["nodes_added"]))
    s.gate("P5b diff(bed,new) edges_removed == the 6 predicted, edges_added []",
           er == sorted(P["diff_bed_new_edges_removed"]) and not d["edges_added"],
           "removed {0} added {1}".format(er, [[k, V.show(x), V.show(y)] for k, x, y in d["edges_added"]][:6]))
    d1, d0 = V.diff(Gs, Gn), V.diff(Gs, Gb)
    un = sorted(set(d1["edges_added"]) - set(d0["edges_added"])) + sorted(set(d1["edges_removed"]) -
                                                                         set(d0["edges_removed"]) - set(d["edges_removed"]))
    s.gate("P5c every diff(S1,new) edge row = a delivered stage (in diff(S1,bed)) or this retirement", not un,
           [[k, V.show(x), V.show(y)] for k, x, y in un][:6])
    s.fact("diff(S1,new) counts {0}; diff(S1,bed) counts {1}".format(d1["counts"], d0["counts"]))
    cd = V.computation_diff(Gs, Gn)
    add = sorted(x["node"] for x in cd["computation_nodes_added"])
    s.gate("P5d computation_diff(S1,new): rows 0, added == {0}, removed []".format(P["cdiff_s1_new"]["added"]),
           not cd["rows"] and add == P["cdiff_s1_new"]["added"] and not cd["computation_nodes_removed"],
           "rows {0} added {1} removed {2}".format([(r["node"], V.show(r["sink"])) for r in cd["rows"]][:6], add,
                                                  cd["computation_nodes_removed"]))
    s.gate("P5e the saved file's md5 is unchanged by the read", K.md5(s.work) == m, K.md5(s.work))
    s.R["m3a4"] = {"saved_md5": m, "bytes": os.path.getsize(s.work), "diff_bed_new": d["counts"],
                   "diff_s1_new": d1["counts"], "cdiff_rows": len(cd["rows"]), "cdiff_added": add,
                   "live_read_s": live["secs"]}
    s.dump()


if __name__ == "__main__":
    st = K.Stage(BED, BED_MD5, "stage_d1_m3a4", preload=False, deadline_min=42,
                 work_name="D1_s3b_m3a4_{0}.vi".format(time.strftime("%Y%m%d_%H%M%S")),
                 task="connectivity-map step 6: M3a-4 retirement from decision_m3a4_v2.json")
    sys.exit(K.run(body, st))
