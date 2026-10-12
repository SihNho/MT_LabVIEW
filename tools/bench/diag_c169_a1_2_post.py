# ---
# labview: build
# hardware: none
# evidence: tools/bench/cards/task_169-a1-3.json
# ---
r"""diag_c169_a1_2_post - card 169-a1-2 step 6 (written by tools/bench/cards/task_169-a1-2.json; DN gate patched by card 169-a1-3) (brief_169-a1-2.md): post-save reads of the SAVED P6-1 file in a SECOND LabVIEW session
(the build run had no memory room for a second whole-VI read, X10 678.9). Saves nothing.

Found before writing (docs/script-writing.md): the read pattern is diag_c165_a3_4_graph.py:9-14 (load MB + graph + e5 of an adopted
file), whose graph block is now ONE call, prep_c167_a1_1_graphlib.read_graph; the e5 check is stagekit.e5_check; S-5 is
prep_c168_a1_2_lib.cdiff_rowset_diff(frame_cdiff(..)) against G168 (57f33e7c) exactly as stage_d1_ring_p6.py:146; the meter is
prep_c168_a1_2_lib.Meter. All CALLED, none pasted. Stage can only open a byte copy of its input (Stage.start), so the read runs on a dated
byte copy scratch_c169_post_<stamp>.vi (Stage.discard_work: deleted at close) and the saved file's md5 is re-checked unchanged.
The saved path + md5 come from the launch's own record tools/bench/launch_c169_p6.json["saved"] (no re-typed md5).
The full Error List of the saved file is NOT read here: it is the separate tool run `py tools/errorlist_check.py --vi <saved> --role final`
(brief step 6), its own LabVIEW session.
PREDICTION CONTRACT: K3 copy byte-identical; MEM after load ~600-650 MB (<= 675); ES ExecState on reload == 1; DN nodes_gone(7815af09, 57f33e7c) = the non-Wire objects absent from 57f33e7c not owned by
another absent object (its own Terminals excluded; assert self-check before the load) = [11261]; E5 stagekit.e5_check ok
(base 7815af09, deleted_nodes [11261], deleted_wires the 22 termless F1 uids); G1 rows > 0 every Diagram owner resolved; FS1 23 FS read;
S-5 frame cdiff(S1, saved) == frame cdiff(S1, 57f33e7c) 30 rows, both differences empty; M every MEM line <= 675; X saved md5 unchanged.
    py tools/bgrun.py --material --max-min 20 --log tools/bench/diag_c169_a1_2_post.log -- py -u tools/bench/diag_c169_a1_2_post.py"""
import json, os, sys                                                                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
for _p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "recipes"), HERE):
    _p in sys.path or sys.path.insert(0, _p)                                                  # noqa: E701
import stagekit as K                                                                         # noqa: E402
import prep_c167_a1_1_graphlib as GL                                                         # noqa: E402
import prep_c168_a1_2_lib as LB                                                              # noqa: E402
g = K.g

# ---- INPUTS -------------------------------------------------------------------------------------------------------------------------
SV = K.jload(HERE, "launch_c169_p6.json")["saved"]                                          # the launch's record of the save
SAVED, SAVEDM = SV["path"], SV["md5"]
STAMP = os.path.splitext(os.path.basename(SAVED))[0].replace("D1_ring_p6_", "")
PL = K.jload(HERE, "diag_c165_a3_4_graph_plan.json")                                        # fs_pairs_from (as the recipe)
FACTS = K.jload(HERE, "p6_facts.json")
TERMLESS = sorted(int(r["uid"]) for r in FACTS["rows"]["F1"] if r.get("class") == "notconnected")
MEM_LIMIT = 675.0
GOUT = os.path.join(HERE, "graph_ring_p6_{0}.json".format(STAMP))
DRY = bool(getattr(g.report_all, "_dry", False))
s = K.Stage(SAVED, SAVEDM, "scratch_c169_post", preload=False, deadline_min=18, reserve_s=120,
            out_json=os.path.join(HERE, "diag_c169_a1_2_post.json"), task="card 169-a1-2 post-save reads of the saved P6-1 file (no save)")
M = LB.Meter(s, K.private_bytes)


# ---- CALLS --------------------------------------------------------------------------------------------------------------------------
def nodes_gone(base, other):        # not "deleted_nodes": stage_prerun X10_RO_EDIT_RE reads 'delete' in a call name as an edit verb (fp-102)
    """Uids of the non-Wire objects of graph `base` absent from graph `other` that are NOT owned by another absent object (card 169-a1-3:
    a node's own Terminal objects carry "owner" = the node's class, e.g. #11267 owner "BuildArray"; a node on a diagram has "Diagram")."""
    keep = set(int(o["uid"]) for o in other["objs"])
    gone = [o for o in base["objs"] if o["class"] != "Wire" and int(o["uid"]) not in keep]
    # shortcut: "owner" is the owner's CLASS name (gscript.report "Class Name 3"), not its uid, so an absent object is matched to an absent
    # owner by class; a lone absent terminal of a SURVIVING node of the same class would be dropped too. Upgrade if objs ever carry an owner uid.
    cls = set(o["class"] for o in gone)
    return sorted(int(o["uid"]) for o in gone if o["owner"] not in cls)


def body(_):
    base = json.load(open(LB.BASE_GRAPH, encoding="utf-8"))
    g168 = json.load(open(LB.G168, encoding="utf-8"))
    one = {"objs": [{"uid": 1, "class": "Add", "owner": "Diagram"}]}
    assert nodes_gone(one, one) == [] and nodes_gone(one, {"objs": []}) == [1], "nodes_gone one-row edge case"
    dn = nodes_gone(base, g168)
    assert dn == [11261], "nodes_gone replay of 7815af09 vs 57f33e7c gave {0}, expected [11261]".format(dn)
    s.fact("SELF-CHECK nodes_gone: one-row pair no difference -> [], one-row removed -> [1], 7815af09 vs 57f33e7c -> {0}".format(dn))
    s.fact("saved file {0} md5 before: {1} (record {2})".format(SAVED, K.md5(SAVED), SAVEDM))
    s.start(); s.discard_work(); W = s.work                                                  # noqa: E702
    s.fact("READ COPY (never saved, deleted at close): {0}".format(os.path.basename(W)))
    bp = K.mod("bench_prep"); h0 = bp.labview_handles()                                      # noqa: E702
    s.R["handles_before"] = h0
    M.mem("after_load")
    s.fact("MEM after load: {0} MB private".format(M.lines[-1][1]))
    es = g.exec_state(W)
    s.R["exec_state_reload"] = es
    s.fact("EXECSTATE ON RELOAD: {0}".format(es))
    gr, info = GL.read_graph(s, W, PL["fs_pairs_from"], "tools/bench/diag_c169_a1_2_post.py (prep_c167_a1_1_graphlib.read_graph) on a "
                             "never-saved byte copy of the SAVED P6-1 file {0}".format(os.path.basename(SAVED)))
    gr["vi"], gr["md5"] = SAVED, SAVEDM                                                     # the graph IS of the saved bytes
    M.mem("after_graph_read")
    if DRY:
        return s.dump()
    s.gate("ES ExecState of the saved bytes on reload == 1", es == 1, es)
    # the deleted node(s) = the measured difference of the two stored graphs (not a re-typed uid and not the build plan, which the
    # prerun would count as this read's plan, X5); computed and self-checked before the load (BASE, G168, DN at the top of body)
    s.fact("DELETED NODES (7815af09 non-Wire objects absent from 57f33e7c, not owned by another absent object): {0}".format(dn))
    s.gate("DN exactly one node removed by the 168 measurement (the BuildArray of the plan)", len(dn) == 1, dn)
    DEL_UID = dn[0] if dn else None
    e5 = K.e5_check({"made": {}, "deleted_nodes": dn, "deleted_wires": TERMLESS, "new_wires": []}, gr, base)
    s.R["e5"] = e5
    s.fact("E5 stagekit.e5_check(edits={{deleted_nodes: [{0}], deleted_wires: 22 termless F1}}, saved, base 7815af09): ok {1} "
           "deleted_wires_present {2} deleted_nodes_present {3} uid_reused {4} rule {5}".format(
               DEL_UID, e5["ok"], e5["deleted_wires_present"], e5["deleted_nodes_present"], len(e5["uid_reused"]), e5["rule"]))
    s.gate("E5 stagekit.e5_check ok on the saved bytes", e5["ok"], {k: e5[k] for k in ("deleted_wires_present", "deleted_nodes_present")})
    O, diags, ff, fsu = info["owners"], info["diags"], info["ff"], info["fsu"]
    s.gate("G1 graph: rows > 0, every Diagram owner resolved", gr["terminals"] and all(O[d][0] != "?" for d in diags),
           [d for d in diags if O[d][0] == "?"][:10])
    allf = [f for v in ff.values() for f in v]
    s.gate("FS1 every FlatSequence read ({0}), each has >= 1 frame, no frame in two FS".format(len(fsu)),
           fsu and all(ff[str(u)] for u in fsu) and len(allf) == len(set(allf)), len(allf))
    json.dump(gr, open(GOUT, "w", encoding="utf-8"))
    wobj = sum(1 for o in gr["objs"] if o["class"] == "Wire")
    s.R["graph"] = {"path": os.path.relpath(GOUT, ROOT), "md5": K.md5(GOUT), "rows": len(gr["terminals"]), "objs": len(gr["objs"]), "wire_objs": wobj}
    s.fact("WROTE {0} md5 {1}: {2} rows, {3} objs, {4} Wire objs, {5} loops, {6} FS".format(
        GOUT, s.R["graph"]["md5"], len(gr["terminals"]), len(gr["objs"]), wobj, len(gr["loops"]), len(fsu)))
    s5 = LB.cdiff_rowset_diff(LB.frame_cdiff(gr), LB.frame_cdiff(g168))
    s.R["s5"] = s5
    s.gate("S-5 frame cdiff(S1, saved) == frame cdiff(S1, 57f33e7c) row for row", s5["ok"],
           "rows {0} vs {1}; only in saved {2}; only in 57f33e7c {3}".format(s5["rows_a"], s5["rows_b"], s5["only_a"], s5["only_b"]))
    h1 = bp.labview_handles()
    s.R["handles_after"] = h1
    s.fact("handles {0} -> {1}".format(h0, h1))
    s.R["mem"] = {"lines": M.lines, "peak": M.peak()}
    s.fact("PEAK MEM {0} MB private ({1})".format(M.peak(), M.lines))
    s.gate("M every MEM line <= {0}".format(MEM_LIMIT), M.peak() <= MEM_LIMIT, M.peak())
    s.gate("X saved md5 unchanged", K.md5(SAVED) == SAVEDM, K.md5(SAVED))
    s.dump()


if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
