r"""diag_c123_graph_p2b - card 123-8 STEP 1 (brief_123-8.md): READ-ONLY graph of the SAVED P2b bed (plan diag_c123_graph_p2b_plan.json)
-> tools/bench/graph_ring_p2b_<ts>.json, + BufNum's representation (read_term_type on the BufNum terminal). The work copy is a never-saved
byte copy (Stage input = the bed, discard_work), deleted.
PRIOR ART (reused, not rewritten): diag_c122_route.py graph() (wiki_build.read_live + k_contract_79.mloops + build_d1_v0.owner_of
closure; fs_tunnel_pairs from graph_qrt_pool_20260928.json - P2a deleted queue objects only and P2b added constants +
indicators, no FS tunnel) and diag_c123_wired.py (Stage on the bed, discard_work). No new op.
PREDICTION: G1 rows > 0, every Diagram owner resolved; G2 the loop is a WhileLoop owned by an FS frame, its body owned by it;
G3 the BufNum terminal is the named source on its wire; G4 the five P2b labels each ONE ControlTerminal on the indicator frame;
T BufNum canon in {I32, U32} (recorded); X bed md5 unchanged; LabVIEW gone.
    py tools/bgrun.py --material --max-min 15 --log tools/bench/diag_c123_graph_p2b.log -- py -u tools/bench/diag_c123_graph_p2b.py"""
import json, os, sys                                                                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K, vigraph as V                                                           # noqa: E401,E402
g = K.g
PL = json.load(open(os.path.join(HERE, "diag_c123_graph_p2b_plan.json"), encoding="utf-8"))
BED, BEDM, FSP, LP, BN = os.path.join(g.CLAUDEDEV, PL["input"]["vi"]), PL["input"]["md5"], PL["fs_pairs_from"], PL["loop"], PL["bufnum"]
DRY = bool(getattr(g.report_all, "_dry", False))
s = K.Stage(BED, BEDM, "scratch_c123_graph_p2b", preload=False, deadline_min=13, reserve_s=120,
            out_json=os.path.join(HERE, "diag_c123_graph_p2b.json"), task="card 123-8 S1")


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
    ty = s.safe("read_term_type BufNum", lambda: g.read_term_type(W, BN["term"]))[0] or {}
    out = os.path.join(HERE, "graph_ring_p2b_{0}.json".format(s.stamp))
    gr = {"vi": BED, "md5": BEDM, "source": "tools/bench/diag_c123_graph_p2b.py (read_live + mloops + owner_of on a never-saved byte copy "
          "of the P2b bed, no edit; fs_tunnel_pairs from " + FSP + ")", "terminals": lv["terminals"], "objs": lv["objs"], "loops": loops,
          "fs_tunnel_pairs": fsp, "owners": dict((str(k), list(v)) for k, v in sorted(O.items())), "bufnum_type": ty}
    json.dump(gr, open(out, "w", encoding="utf-8"))
    s.fact("WROTE {0} md5 {1}: {2} rows, {3} objs, {4} loops".format(out, K.md5(out), len(lv["terminals"]), len(lv["objs"]), len(loops)))
    T = lv["terminals"]
    s.gate("G1 graph: rows > 0, every Diagram owner resolved", T and all(O[d][0] != "?" for d in diags), [d for d in diags if O[d][0] == "?"][:10])
    s.gate("G2 loop body owned by the While; While on an FS frame", O.get(LP["body"]) == ("WhileLoop", LP["uid"])
           and O.get(LP["owner"], ("", 0))[0] == "FlatSequenceFrame", (O.get(LP["body"]), O.get(LP["owner"])))
    bn = [r for r in T if int(r["term_uid"]) == BN["term"]]
    s.gate("G3 BufNum terminal = the node's named source on its wire", len(bn) == 1 and int(bn[0]["owner_uid"]) == BN["node"] and bn[0]["is_source"]
           and bn[0]["term_name"] == BN["name"] and int(bn[0]["wire_uid"] or 0) == BN["wire"], bn)
    ct = dict((lab, [r for r in T if r.get("term_class") == "ControlTerminal" and r["term_name"] == lab]) for lab in PL["labels"])
    s.gate("G4 P2b indicators: each label ONE ControlTerminal on the indicator frame",
           all(len(v) == 1 and int(v[0]["frame_diagram"] or 0) == PL["ind_frame"] for v in ct.values()),
           dict((k, [(r["term_uid"], r["wire_uid"], r["frame_diagram"]) for r in v]) for k, v in ct.items()))
    canon = (ty.get("types") or {}).get("canon")
    s.fact("BUFNUM TYPE {0}".format(json.dumps(ty, default=str)))
    s.gate("T BufNum representation read (canon I32 or U32)", canon in ("I32", "U32"), canon)
    s.R["graph"] = {"path": os.path.relpath(out, ROOT), "md5": K.md5(out), "bufnum_canon": canon}
    s.gate("X bed md5 unchanged", K.md5(BED) == BEDM, K.md5(BED))
    s.dump()


if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
