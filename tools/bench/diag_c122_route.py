r"""diag_c122_route - card 122-4 (PD241(a)/(b), PD242): the route "valued constant on a diagram uid -> NEW labelled indicator",
scratch-verified on the P2a bed's FS frame, + the P2a bed's GRAPH (the offline 3-row plan needs it as its base).
PRIOR ART (reused): verify() = card 122-3's never-run version of this file; graph dump = diag_c120_g.py (read_live + mloops + owner_of,
fs_tunnel_pairs reused - P2a deleted queue objects only, no FS tunnel); donor = diag_c122_hyg.py's DonorRingConst_v0.vi (record
diag_c122_donor.json); OpConstInd_v0 is admitted by its op_hygiene record (no probe exemption here). Stage input = the saved R2 (a
scratch work copy, closed at once, as diag_c118_r1v.py); the P2a copy is a never-saved scratch, deleted.
PREDICTION: G1 graph rows > 0, every Diagram owner resolved, md5 field == the bed's; S0 #3121 owner FlatSequence*; per label: ONE new
wired indicator, label exact, canon I32 / Array1D<I32> / Array1D<DBL> on both ends, constant value == written, const term wire ==
indicator terminal wire != 0, Wire +1, indicator terminal on #3121; X bed md5 unchanged; LabVIEW gone.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c122_route.log -- py -u tools/bench/diag_c122_route.py"""
import json, os, sys, time                                                           # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K, vigraph as V                                                    # noqa: E401,E402
g = K.g
PL = json.load(open(os.path.join(HERE, "diag_c122_route_plan.json"), encoding="utf-8"))   # ONE literal: stage_prerun.plan_files
BED, BEDM, FRAME = os.path.join(g.CLAUDEDEV, PL["bed"]["vi"]), PL["bed"]["md5"], PL["bed"]["frame"]
OUTJ, OUTG, SV = os.path.join(HERE, "diag_c122_route.json"), os.path.join(HERE, "diag_c122_graph_p2a.json"), os.path.join(HERE, "scratch_verify")
DRY = bool(getattr(g.report_all, "_dry", False))
s = K.Stage(os.path.join(g.CLAUDEDEV, PL["input"]["vi"]), PL["input"]["md5"], "scratch_c122_route", preload=False, deadline_min=28, reserve_s=150,
            out_json=OUTJ, task="card 122-4")
AT = K.mod("allterms")
same = lambda a, b: tuple(a) == tuple(b) if isinstance(b, list) else a == b          # noqa: E731


def graph(W):
    fsp = json.load(open(os.path.join(ROOT, PL["bed"]["fs_pairs_from"]), encoding="utf-8"))["fs_tunnel_pairs"]
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
        O[u][1] and O[u][0] in V.STRUCT_OWNER and todo.append(O[u][1])              # noqa: E701
    gr = {"vi": BED, "md5": BEDM, "source": "tools/bench/diag_c122_route.py (read_live + mloops + owner_of on a never-saved byte copy of the P2a bed, "
          "before any edit; fs_tunnel_pairs from " + PL["bed"]["fs_pairs_from"] + ")", "terminals": lv["terminals"], "objs": lv["objs"], "loops": loops,
          "fs_tunnel_pairs": fsp, "owners": dict((str(k), list(v)) for k, v in sorted(O.items()))}
    json.dump(gr, open(OUTG, "w", encoding="utf-8"))
    s.fact("WROTE {0} md5 {1}: {2} rows, {3} objs, {4} loops".format(OUTG, K.md5(OUTG), len(lv["terminals"]), len(lv["objs"]), len(loops)))
    s.gate("G1 graph dump: rows > 0, every Diagram owner resolved", lv["terminals"] and all(O[d][0] != "?" for d in diags), [d for d in diags if O[d][0] == "?"][:10])


def verify(rec, W):
    OF = K.mod("build_d1_v0").owner_of
    own = s.safe("owner #frame", lambda: OF(W, FRAME, strict=True))[0]
    s.gate("S0 #{0} is a flat-sequence frame diagram".format(FRAME), own and str(own[0]).startswith("FlatSequence"), own, fatal=True)
    out = {}
    for k, (lab, key, canon, val) in enumerate(PL["rows"]):
        w0 = g.count(W, "Wire")
        r, e = s.safe("route " + lab, lambda: g.const_indicator_on_diagram(W, FRAME, {"donor": rec["path"], "uid": rec[key]}, lab, (40, 40 + 90 * k)), {})
        r = r or {"err": e}; rows = AT.read_terms(W)[0]; dw = g.count(W, "Wire") - w0   # noqa: E702
        ind = set(int(u) for u in (r.get("new_terminals") or []))
        ct = [x for x in rows if int(x["owner_uid"]) == int(r.get("const_uid") or -1)]
        it = [x for x in rows if int(x["owner_uid"]) in ind or int(x["term_uid"]) in ind]
        pw = [x for x in g.panel_wiring(W) if int(x["uid"]) == int(r.get("created_uid") or -1)]
        tt = [int(x["term_uid"]) for x in ct + it]
        tt = tt if it else tt + sorted(ind)[:1]                                      # a ControlTerminal may itself be the Terminal
        ty = [(s.safe("type", lambda: g.read_term_type(W, u))[0] or {}).get("types", {}).get("canon") for u in tt]
        io = s.safe("ind owner", lambda: OF(W, sorted(ind)[0], strict=False))[0] if ind else None
        cv = g.read_const_value(W, r["const_uid"]) if r.get("const_uid") else {}
        out[lab] = {"route": {k2: v for k2, v in r.items() if k2 != "new_panel"}, "const_terms": ct, "ind_terms": it, "canon": ty,
                    "value": cv.get("value"), "value_err": cv.get("err"), "wire_delta": dw, "panel": pw, "ind_owner": io}
        s.fact("S {0}: {1}".format(lab, json.dumps(out[lab], default=str)[:900]))
        s.gate("S {0}: no route error, ONE new wired indicator, label exact".format(lab), not r.get("err") and len(pw) == 1 and pw[0]["label"] == lab
               and int(pw[0]["wire"] or 0), r.get("err"))
        s.gate("S {0}: read_term_type canon == {1} on both ends".format(lab, canon), len(ty) == 2 and all(t == canon for t in ty), ty)
        s.gate("S {0}: constant value read == written".format(lab), same(cv.get("value"), val) and not cv.get("err"), cv.get("value"))
        s.gate("S {0}: ONE wire (const term wire == indicator terminal wire != 0, Wire +1)".format(lab), len(ct) == 1 and len(pw) == 1
               and int(ct[0]["wire_uid"] or 0) and int(ct[0]["wire_uid"]) == int(pw[0]["wire"] or -1) and dw == 1, (ct, pw, dw))
        s.gate("S {0}: indicator terminal on #{1}".format(lab, FRAME), (it and int(it[0]["frame_diagram"] or 0) == FRAME)
               or (io and int(io[1]) == FRAME), (it, io))
    return out


def body(_):
    s.start(); s.discard_work()                                                      # noqa: E702
    if DRY:
        return s.dump()
    g.close_panel(s.work)
    rec = json.load(open(os.path.join(ROOT, PL["donor"]), encoding="utf-8"))
    s.gate("D donor md5 == its record", K.md5(rec["path"]) == rec["md5"], rec["md5"], fatal=True)
    W = s.scratch("p2a", BED)
    graph(W)
    out = verify(rec, W)
    ok = not s.fails
    s.drop_scratch(W, "X-p2a")
    if ok:
        json.dump({"function": "gscript.const_indicator_on_diagram", "status": "PASS", "t": time.time(), "card": "122-4",
                   "log": "tools/bench/diag_c122_route.log", "input_md5": BEDM, "fixture": "never-saved byte copy of claudeDev\\" + os.path.basename(BED)
                   + " (deleted)", "frame_diagram": FRAME, "donor": rec, "rows": out},
                  open(os.path.join(SV, "gscript.const_indicator_on_diagram_c122_{0}.json".format(s.stamp)), "w", encoding="utf-8"), indent=1, default=str)
    s.gate("X bed md5 unchanged", K.md5(BED) == BEDM, K.md5(BED))
    s.dump()


if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
