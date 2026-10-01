r"""diag_c125_graph_p3a - card 125-2 STEP A (brief_125-2.md): READ-ONLY graph of the SAVED P3a bed (plan diag_c125_graph_p3a_plan.json)
-> tools/bench/graph_ring_p3a_<ts>.json. The work copy is a never-saved byte copy (Stage input = the bed, discard_work), deleted.
PRIOR ART (reused, not rewritten): diag_c123_graph_p2b.py (card 123-8) line for line - read_live + mloops + owner_of closure,
fs_tunnel_pairs from graph_qrt_pool_20260928.json (P3a added no FS tunnel). No new op. The loose-end trace is OFFLINE
(diag_c125_loose.py) on the written JSON.
PREDICTION: G1 rows > 0, every Diagram owner resolved; G2 the loop body owned by While #637, the While on an FS frame;
G3 case #22694's two frame diagrams [27219, 27232] are owned by it; X bed md5 unchanged; LabVIEW gone.
    py tools/bgrun.py --material --max-min 15 --log tools/bench/diag_c125_graph_p3a.log -- py -u tools/bench/diag_c125_graph_p3a.py"""
import json, os, sys                                                                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K, vigraph as V                                                           # noqa: E401,E402
g = K.g
PL = json.load(open(os.path.join(HERE, "diag_c125_graph_p3a_plan.json"), encoding="utf-8"))
BED, BEDM, FSP, LP, CS = os.path.join(g.CLAUDEDEV, PL["input"]["vi"]), PL["input"]["md5"], PL["fs_pairs_from"], PL["loop"], PL["case"]
DRY = bool(getattr(g.report_all, "_dry", False))
s = K.Stage(BED, BEDM, "scratch_c125_graph_p3a", preload=False, deadline_min=13, reserve_s=120,
            out_json=os.path.join(HERE, "diag_c125_graph_p3a.json"), task="card 125-2 A")


def body(_):
    s.start(); s.discard_work(); W = s.work                                                  # noqa: E702
    if DRY:
        return s.dump()
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
    out = os.path.join(HERE, "graph_ring_p3a_{0}.json".format(s.stamp))
    gr = {"vi": BED, "md5": BEDM, "source": "tools/bench/diag_c125_graph_p3a.py (read_live + mloops + owner_of on a never-saved byte copy "
          "of the P3a bed, no edit; fs_tunnel_pairs from " + FSP + ")", "terminals": lv["terminals"], "objs": lv["objs"], "loops": loops,
          "fs_tunnel_pairs": fsp, "owners": dict((str(k), list(v)) for k, v in sorted(O.items()))}
    json.dump(gr, open(out, "w", encoding="utf-8"))
    s.fact("WROTE {0} md5 {1}: {2} rows, {3} objs, {4} loops".format(out, K.md5(out), len(lv["terminals"]), len(lv["objs"]), len(loops)))
    T = lv["terminals"]
    s.gate("G1 graph: rows > 0, every Diagram owner resolved", T and all(O[d][0] != "?" for d in diags), [d for d in diags if O[d][0] == "?"][:10])
    s.gate("G2 loop body owned by the While; While on an FS frame", O.get(LP["body"]) == ("WhileLoop", LP["uid"])
           and O.get(LP["owner"], ("", 0))[0] == "FlatSequenceFrame", (O.get(LP["body"]), O.get(LP["owner"])))
    s.gate("G3 case frames owned by the case", all(O.get(f) == ("CaseStructure", CS["uid"]) for f in CS["frames"]),
           [(f, O.get(f)) for f in CS["frames"]])
    s.R["graph"] = {"path": os.path.relpath(out, ROOT), "md5": K.md5(out)}
    s.gate("X bed md5 unchanged", K.md5(BED) == BEDM, K.md5(BED))
    s.dump()


if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
