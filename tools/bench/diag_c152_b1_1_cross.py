# ---
# labview: build
# hardware: none
# ---
r"""diag_c152_b1_1_cross - card 152-b1-1 PD369(d): mirrors v18 op 187 (graph 44858dbf, diag_c152_b1_1_graph.log: LoopTunnel #30179 of WhileLoop
#16483 on #23166, inner face fed by SubVI #29719 RingPickSlot 'min slot', outer face 'min slot' w30166 -> IndexArray.index sinks) in a NEW minimal
scratch = Stage.scratch byte copy of EMPTY_v0 (deleted): While + RingPickSlot_v0 in its body; P1 'min slot' -> Max & Min x in the body (source
WIRED, so LT's outer face is named as #30179's); P2 'min slot' -> IA_o.index on top (creates LT); 1-frame FS (DonorFs_v0) on top holding IA_f;
X = connect_term_uid(IA_f.index, LT outer face). Stage input = P3b2b bed: dry-run graph + Index Array donor (plan). Plan diag_c152_b1_1_cross_plan.json.
FOUND FIRST: diag_c127_1_fsinner.py, diag_c126_6_cross.py, build_ringpickslot_v2.py:45-47 (EMPTY_v0 top diagram), fntest release needs fntest_*.py.
PREDICTION: ops err '', echoes == uids; P2 +1 LoopTunnel, faces 'min slot'/'min slot'; X +1 FlatSequenceOuterTunnel whose faces are (i) 'min slot'
on BOTH faces (nearest rows: SubVI-named sources B1/A_bn/pin3 op 26); LT keeps 'min slot'. Names = ROW measurements. Scratch gone, pins same.
    py tools/bgrun.py --material --max-min 45 --log tools/bench/diag_c152_b1_1_cross.log -- py -u tools/bench/diag_c152_b1_1_cross.py"""
import json, os, sys                                                                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K; g = K.g                                                               # noqa: E402,E702
PL = json.load(open(os.path.join(HERE, "diag_c152_b1_1_cross_plan.json"), encoding="utf-8"))
CD, T, TN, DU = g.CLAUDEDEV, os.path.join(ROOT, "tools"), PL["terms"], PL["ia_donor_uid"]    # noqa: E702
PP = dict((k, tuple(v)) for k, v in PL["pos"].items())
BED, EMPTY, RPS = os.path.join(CD, PL["input"]["vi"]), os.path.join(CD, PL["minimal"]), os.path.join(CD, PL["subvi"])   # noqa: E702
PIN = {"stagekit": (os.path.join(T, "stagekit.py"), "604529e8"), "addrcheck": (os.path.join(T, "addrcheck.py"), "207beb0d"),
       "stagexec": (os.path.join(T, "stagexec.py"), "1bab9cf9"), "gscript": (os.path.join(T, "gscript.py"), "1a80236e"),
       "stage_prerun": (os.path.join(T, "stage_prerun.py"), "c739eb86"), "vigraph": (os.path.join(T, "vigraph.py"), "13be0847"),
       "stagesim": (os.path.join(T, "stagesim.py"), "c24bd39a"), "naming_tbl": (os.path.join(HERE, "fs_tunnel_naming_table.json"), "0c0ba43a"),
       "mem_model": (os.path.join(HERE, "memory_model.json"), "a28b6dd7"), "s08_vi": (os.path.join(CD, "D1_ring_p4s08_20261009_031503.vi"), "f99e8414"),
       "graph_s08": (os.path.join(HERE, "graph_ring_p4s08_20261009_033522.json"), "44858dbf"), "rps": (RPS, "6fcf153f"), "empty": (EMPTY, "6544be40"),
       "fs_donor": (os.path.join(CD, "DonorFs_v0.vi"), "d785a181"), "mm_donor": (os.path.join(CD, "OpPrimDonor_v0.vi"), "6e958063")}
NOW = dict((k, K.md5(p) if os.path.exists(p) else "MISSING") for k, (p, _w) in PIN.items())
DRY, OUT = bool(getattr(g.report_all, "_dry", False)), {"pins_now": NOW}                    # noqa: E702
s = K.Stage(BED, PL["input"]["md5"], "scratch_c152_b1_1", preload=False, deadline_min=40, reserve_s=150, pins=[(k, PIN[k][0], NOW[k]) for k in PIN],
            out_json=os.path.join(HERE, "diag_c152_b1_1_cross.json"), task="card 152-b1-1 PD369(d)")
def terms(W): return [] if DRY else K.mod("allterms").read_terms(W, K.mod("allterms").OP_ALLTERMS_V1)[0]   # noqa: E704
def row(r): return (r["term_uid"], r["owner_class"], r["owner_uid"], r["term_name"], r["is_source"], r["frame_diagram"], r["wire_uid"])
def by_class(c0, c1): return dict((c, sum(1 for u in set(c1) - set(c0) if c1[u] == c)) for c in set(c1[u] for u in set(c1) - set(c0)))
def faces(W, owners, tag):
    R = terms(W); o = dict((u, [row(r) for r in R if int(r["owner_uid"]) == int(u)]) for u in owners)   # noqa: E702
    s.fact("FACES %s %s" % (tag, json.dumps(o, default=str))); OUT.setdefault("faces", {})[tag] = o           # noqa: E702
    return o
def one(R, tag, **kw):
    m = [r for r in R if all(r.get(k) == v for k, v in kw.items())]
    s.gate("T %s one terminal %s" % (tag, kw), DRY or len(m) == 1, [row(r) for r in m][:4])
    return int(m[0]["term_uid"]) if len(m) == 1 else 0
def wire(W, tag, snk, src, lt=None):
    c0, w0 = s.census_snapshot(W), set(g.uids(W, "Wire"))
    cw = s._op("connect_term_uid", lambda: g.connect_term_uid(W, snk, src), "%s #%s <- #%s" % (tag, snk, src)); res = cw["result"] or {}   # noqa: E702
    if not s.gate("%s connect_term_uid op err '', echoes == uids" % tag, DRY or (res and not cw["err"] and not res.get("err")), cw) or DRY:
        return {"dry": True} if DRY else None
    c1, wn = s.census_snapshot(W), sorted(set(g.uids(W, "Wire")) - w0)
    o = {"op": res, "census": by_class(c0, c1), "gone": sorted(set(c0) - set(c1)), "new_wires": wn,
         "new_tunnels": sorted(u for u in set(c1) - set(c0) if "Tunnel" in c1[u]), "c1": c1}
    s.fact("CENSUS %s %s; Is Broken? %s; gone %s; new wires %s; new tunnels %s" % (tag, json.dumps(o["census"], sort_keys=True), res.get("broken"),
           o["gone"], wn, [(u, c1[u]) for u in o["new_tunnels"]]))
    o["pre"] = faces(W, [lt] + o["new_tunnels"], "AFTER %s before RLE" % tag) if lt else None
    o["rle"] = dict((w, g.wire_remove_loose_ends(W, w)) for w in wn)
    for w, r in o["rle"].items():
        s.gate("%s R RemoveLooseEnds w%s echo == uid, err ''" % (tag, w), r["echo"] == w and not r["err"], r)
    o["wires_after_rle"] = sorted(set(g.uids(W, "Wire")) & set(wn))
    s.fact("AFTER-RLE %s new wires still present %s; ES %s" % (tag, o["wires_after_rle"], g.exec_state(W)))
    OUT[tag] = dict((k, v) for k, v in o.items() if k != "c1")
    return o
def body(_):
    for k, (p, w) in PIN.items():
        s.gate("PIN-CARD %s md5 %s starts with %s" % (k, NOW[k], w), NOW[k].startswith(w), p)
    s.start(); s.discard_work(); DON = s.work                                                # noqa: E702
    W = s.scratch("min", source=EMPTY)
    top = 1 if DRY else int(g.report_all(W, "Diagram")[0]["uid"]); d0, l0 = g.uids(W, "Diagram"), g.uids(W, "WhileLoop")   # noqa: E702
    s._op("while_loop", lambda: g.while_loop(W, PP["while"]), "While on top #%s" % top)
    nd, nl = sorted(g.uids(W, "Diagram") - d0), sorted(g.uids(W, "WhileLoop") - l0)
    if not s.gate("L1 +1 WhileLoop %s, +1 Diagram (body) %s" % (nl, nd), DRY or (len(nd) == 1 and len(nl) == 1), (nd, nl)): return s.dump()   # noqa: E701
    bd = 2 if DRY else nd[0]; sv0 = g.uids(W, "SubVI")                                        # noqa: E702
    s._op("drop_subvi", lambda: g.drop_subvi(W, RPS, g._uid_index(W, "Diagram", bd), PP["subvi"]), "RingPickSlot_v0 -> body #%s" % bd)
    sv = sorted(g.uids(W, "SubVI") - sv0)
    mm = s._op("create_primitive_nested", lambda: g.create_primitive_nested(W, bd, "Max & Min", PP["mm"]), "Max & Min -> body")["result"]
    ia_o = s._op("create_primitive_nested", lambda: g.create_primitive_nested(W, top, "Index Array", PP["ia_o"], donor={"donor": DON, "uid": DU}),
                 "IA_o -> top")["result"]
    c0 = s.census_snapshot(W)
    cp = s._op("struct_copy_nested", lambda: g.struct_copy_nested(W, top, "FlatSequence", g.fs_donor(), PP["fs"]), "FS -> top")["result"] or {}
    fs = 3 if DRY else int(cp.get("uid") or 0); fr = [4] if DRY else g.fs_frames(W, fs)["frames"]   # noqa: E702
    s.census_gate("F1 census delta of FS copy == FlatSequence 1 + Diagram 1", c0, s.census_snapshot(W), {"FlatSequence": 1, "Diagram": 1})
    if not s.gate("F2 FS #%s has 1 frame %s; SubVI %s in body" % (fs, fr, sv), DRY or (fs and len(fr) == 1 and len(sv) == 1), (cp, fr, sv)): return s.dump()   # noqa: E701
    ia_f = s._op("create_primitive_nested", lambda: g.create_primitive_nested(W, fr[0], "Index Array", PP["ia_f"], donor={"donor": DON, "uid": DU}),
                 "IA_f -> FS frame #%s" % fr[0])["result"]
    R = terms(W); sv = sv[0] if sv else 0                                                     # noqa: E702
    B = OUT["built"] = {"top": top, "while": nl, "body": bd, "subvi": sv, "mm": mm, "ia_o": ia_o, "fs": fs, "frame": fr, "ia_f": ia_f}
    s.fact("BUILT %s" % B)
    ms = one(R, "SV.src", owner_uid=sv, term_name=TN["src"], is_source=True, frame_diagram=bd)
    mx = one(R, "MM.x", owner_uid=mm, term_name=TN["mm"], is_source=False, frame_diagram=bd)
    io = one(R, "IA_o.index", owner_uid=ia_o, term_name=TN["ia"], is_source=False, frame_diagram=top)
    ix = one(R, "IA_f.index", owner_uid=ia_f, term_name=TN["ia"], is_source=False, frame_diagram=fr[0])
    s.fact("FS border tunnels BEFORE: %s" % sorted(set(r["owner_uid"] for r in R if r["frame_diagram"] == fr[0] and "Tunnel" in str(r["owner_class"]))))
    p1 = wire(W, "P1", mx, ms)
    p2 = p1 and wire(W, "P2", io, ms)
    if not p2: return s.dump()                                                               # noqa: E701
    lt = [0] if DRY else p2["new_tunnels"]
    if not s.gate("P2 exactly one new tunnel, a LoopTunnel %s" % lt, DRY or (len(lt) == 1 and p2["c1"][lt[0]] == "LoopTunnel"), lt): return s.dump()   # noqa: E701
    lt = lt[0]; F0 = [] if DRY else faces(W, [lt], "LT BEFORE X")[lt]                        # noqa: E702
    out = [(0, "", 0, "", True, top, 0)] if DRY else [f for f in F0 if f[5] == top and f[4]]
    if not s.gate("P2 LT has ONE outer source face on top #%s" % top, len(out) == 1, F0): return s.dump()   # noqa: E701
    s.row("MIRROR LT outer face name (graph #30179 t30192)", out[0][3], TN["src"])
    x = wire(W, "X", ix, out[0][0], lt=lt)
    if x is None or DRY: return s.dump()                                                     # noqa: E701
    ft = x["new_tunnels"]; F1 = x["pre"]                                                       # noqa: E702
    s.gate("X exactly one new tunnel, a FlatSequenceOuterTunnel %s" % [(u, x["c1"][u]) for u in ft], len(ft) == 1 and x["c1"][ft[0]] == "FlatSequenceOuterTunnel", ft)
    for u in ft:
        for f in F1[u]:
            s.row("FSOT #%s face t%s on #%s source=%s name" % (u, f[0], f[5], f[4]), f[3], TN["src"])
    s.row("LT faces unchanged by X", [f[3] for f in F1[lt]] == [f[3] for f in F0], True)
    F2 = faces(W, [lt] + ft, "AFTER X RLE")
    s.row("names after RLE == before RLE", [(f[0], f[3]) for u in F1 for f in F1[u]] == [(f[0], f[3]) for u in F2 for f in F2[u]], True)
    json.dump(OUT, open(os.path.join(HERE, "diag_c152_b1_1_cross_out.json"), "w", encoding="utf-8"), default=str, indent=1)
    s.dump()
if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
