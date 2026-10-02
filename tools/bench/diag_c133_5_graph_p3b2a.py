r"""diag_c133_5_graph_p3b2a - card 133-5 STEP 2 (PD283(d), PD284(c)): READ-ONLY graph of session a's SCRATCH saved file
(plan diag_c133_5_graph_p3b2a_plan.json; input path + md5 from tools/bench/stage_d1_ring_p3b2a_scratch_sum.json, step 1)
-> tools/bench/graph_ring_p3b2a_<ts>.json, same JSON shape as graph_ring_p3b1 (the --rebase input for session b).
PRIOR ART (reused, not rewritten): tools/bench/diag_c132_2_graph_p3b1.py line for line (input from step 1's summary, output name
changed). The 'MEM after load' line is the measured load of a's file that goes into memory_model.json load_by_vi (PD283(c)).
PREDICTION: G1 rows > 0, every Diagram owner resolved; G2 the loop body owned by While #637, the While on an FS frame;
G3 case #22694's two frame diagrams [27219, 27232] are owned by it; X input md5 unchanged; LabVIEW gone.
    py tools/bgrun.py --material --max-min 15 --log tools/bench/diag_c133_5_graph_p3b2a.log -- py -u tools/bench/diag_c133_5_graph_p3b2a.py"""
import json, os, sys                                                                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K, vigraph as V                                                           # noqa: E401,E402
g = K.g
PL = json.load(open(os.path.join(HERE, "diag_c133_5_graph_p3b2a_plan.json"), encoding="utf-8"))
SUM = json.load(open(os.path.join(ROOT, PL["input"]["from_summary"]), encoding="utf-8"))
BED, BEDM, FSP, LP, CS = SUM["final"], SUM["final_md5"], PL["fs_pairs_from"], PL["loop"], PL["case"]
DRY = bool(getattr(g.report_all, "_dry", False))
s = K.Stage(BED, BEDM, "scratch_c133_5_graph_p3b2a", preload=False, deadline_min=13, reserve_s=120,
            out_json=os.path.join(HERE, "diag_c133_5_graph_p3b2a.json"), task="card 133-5 step 2")


def mb():
    return round((K.private_bytes() or 0) / 1e6, 1)


def body(_):
    s.fact("input md5 before: {0}".format(K.md5(BED)))
    s.start(); s.discard_work(); W = s.work                                                  # noqa: E702
    if DRY:
        return s.dump()
    s.R["mem"] = {"after_load_mb": mb()}
    s.fact("MEM after load: {0} MB private".format(s.R["mem"]["after_load_mb"]))
    fsp = json.load(open(os.path.join(ROOT, FSP), encoding="utf-8"))["fs_tunnel_pairs"]
    lv = K.mod("wiki_build").read_live(W, fs_pairs=fsp)
    loops, BD = K.mod("k_contract_79").mloops(s, W), K.mod("build_d1_v0")
    diags, O = [int(o["uid"]) for o in lv["objs"] if o["class"] == "Diagram"], {}
    todo = list(diags)
    while todo:
        u = todo.pop(0)
        if u in O:
            continue
        v = s.safe("owner_of #{0}".format(u), lambda: BD.owner_of(W, u, strict=False), ("?", 0))[0] or ("?", 0)
        O[u] = (str(v[0]), int(v[1] or 0))
        O[u][1] and O[u][0] in V.STRUCT_OWNER and todo.append(O[u][1])                       # noqa: E701
    s.R["mem"]["after_read_mb"] = mb()
    s.fact("MEM after full read: {0} MB private".format(s.R["mem"]["after_read_mb"]))
    out = os.path.join(HERE, "graph_ring_p3b2a_{0}.json".format(s.stamp))
    gr = {"vi": BED, "md5": BEDM, "source": "tools/bench/diag_c133_5_graph_p3b2a.py (read_live + mloops + owner_of on a never-saved "
          "byte copy of session a's scratch file, no edit; fs_tunnel_pairs from " + FSP + ")", "terminals": lv["terminals"], "objs": lv["objs"],
          "loops": loops, "fs_tunnel_pairs": fsp, "owners": dict((str(k), list(v)) for k, v in sorted(O.items()))}
    json.dump(gr, open(out, "w", encoding="utf-8"))
    s.fact("WROTE {0} md5 {1}: {2} rows, {3} objs, {4} loops".format(out, K.md5(out), len(lv["terminals"]), len(lv["objs"]), len(loops)))
    T = lv["terminals"]
    s.gate("G1 graph: rows > 0, every Diagram owner resolved", T and all(O[d][0] != "?" for d in diags), [d for d in diags if O[d][0] == "?"][:10])
    s.gate("G2 loop body owned by the While; While on an FS frame", O.get(LP["body"]) == ("WhileLoop", LP["uid"])
           and O.get(LP["owner"], ("", 0))[0] == "FlatSequenceFrame", (O.get(LP["body"]), O.get(LP["owner"])))
    s.gate("G3 case frames owned by the case", all(O.get(f) == ("CaseStructure", CS["uid"]) for f in CS["frames"]),
           [(f, O.get(f)) for f in CS["frames"]])
    s.R["graph"] = {"path": os.path.relpath(out, ROOT), "md5": K.md5(out)}
    s.gate("X input md5 unchanged", K.md5(BED) == BEDM, K.md5(BED))
    s.dump()


if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
