r"""diag_c136_1_graph - card 136-1 item 5 (+ item 4 READ part), PD295(e): READ-ONLY graph of a never-saved byte copy of the BED
claudeDev\D1_ring_p3b2b_20261002_130007.vi (md5 39511877; plan diag_c136_1_graph_plan.json), fresh LabVIEW
-> tools/bench/graph_ring_p3b2b_<ts>.json, the shape of graph_ring_p3b2a_fs_20261002_123012.json (terminals, objs, loops,
fs_tunnel_pairs, owners, fs_measured {fs_frames, read_err, borders}).
PRIOR ART (reused): tools/bench/diag_c134_1_graph.py line for line (read_live + mloops + owner_of + gscript.fs_frames per FS +
stagesim.fs_measured_state + fs_border_gate); build_d1_v0.loop_end_ref (OpLoopEndRef_v0, toolkit-capabilities.md:67) for the
conditional terminal of While #10170. NO reader of the conditional-terminal MODE (Stop/Continue if True) exists (grep of tools/,
docs/NAMES.md, docs/toolkit-capabilities.md: only OpLoopEndRef_v0 term/wire/IsSource) -> the mode is reported UNMEASURED, not built.
PREDICTION: G1 rows > 0, every Diagram owner resolved; G2 #639 owned by While #637 on an FS frame; G3 case #22694 frames owned;
FS1 every FlatSequence read, frames > 0, no frame in two FS; B no UNMEASURED border used (no plan named); E4 #10171 has sinks x, y
(both on ONE wire, PD295(c)) and a source 'x = y?'; L4 While #10170 cond term read, err '', its wire == #10171's out wire;
X bed md5 unchanged; LabVIEW gone.
    py tools/bgrun.py --material --max-min 15 --log tools/bench/diag_c136_1_graph.log -- py -u tools/bench/diag_c136_1_graph.py"""
import json, os, sys                                                                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K, vigraph as V, stagesim as SS                                           # noqa: E401,E402
g = K.g
PL = json.load(open(os.path.join(HERE, "diag_c136_1_graph_plan.json"), encoding="utf-8"))
BED, BEDM, FSP, LP, CS, R4 = PL["input"]["vi"], PL["input"]["md5"], PL["fs_pairs_from"], PL["loop"], PL["case"], PL["read4"]
DRY = bool(getattr(g.report_all, "_dry", False))
s = K.Stage(BED, BEDM, "scratch_c136_1_graph_p3b2b", preload=False, deadline_min=13, reserve_s=120,
            out_json=os.path.join(HERE, "diag_c136_1_graph.json"), task="card 136-1 item 5")


def mb():
    return round((K.private_bytes() or 0) / 1e6, 1)


def body(_):
    s.fact("input md5 before: {0}".format(K.md5(BED)))
    s.start(); s.discard_work(); W = s.work                                                  # noqa: E702
    if DRY:
        return s.dump()
    bp = K.mod("bench_prep"); h0 = bp.labview_handles()                                      # noqa: E702
    s.R["mem"] = {"after_load_mb": mb(), "handles_before": h0}
    s.fact("MEM after load: {0} MB private; handles {1}".format(s.R["mem"]["after_load_mb"], h0))
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
    fsu = sorted(int(o["uid"]) for o in lv["objs"] if o["class"] == "FlatSequence")
    ff, ferr = {}, {}
    for u in fsu:
        r = s.safe("fs_frames #{0}".format(u), lambda: g.fs_frames(W, u), None)[0]
        ff[str(u)] = list((r or {}).get("frames") or [])
        ferr[str(u)] = (r or {}).get("err") if r else "read failed"
        s.fact("FS #{0}: frames {1} (terminating err {2!r})".format(u, ff[str(u)], str(ferr[str(u)])[:80]))
    # item 4 READ part: #10171's rows and While #10170's conditional terminal (OpLoopEndRef_v0); the MODE has no reader
    T = lv["terminals"]
    eq = sorted(set((r["term_uid"], r["term_name"], bool(r["is_source"]), r["wire_uid"]) for r in T if int(r["owner_uid"]) == R4["eq"]))
    li = [int(o["uid"]) for o in g.report_all(W, "WhileLoop")].index(R4["loop"])
    le = s.safe("loop_end_ref #{0}".format(R4["loop"]), lambda: BD.loop_end_ref(W, li), {})[0] or {}
    s.R["read4"] = {"eq_rows": eq, "loop_end_ref": le, "cond_mode": "UNMEASURED - no reader op exists (OpLoopEndRef_v0 reads term/wire/IsSource only)"}
    s.fact("R4 #{0} rows (term, name, is_source, wire) {1}".format(R4["eq"], eq))
    s.fact("R4 While #{0} (index {1}) cond term {2}".format(R4["loop"], li, le))
    s.fact("R4 While #{0} conditional-terminal MODE: UNMEASURED (no reader op; not built under this card)".format(R4["loop"]))
    sx = [r for r in eq if not r[2]]
    so = [r for r in eq if r[2]]
    s.gate("E4 #{0}: sinks x, y on ONE wire and one source".format(R4["eq"]), sorted(r[1] for r in sx) == ["x", "y"]
           and len(set(r[3] for r in sx)) == 1 and len(so) == 1, eq)
    s.gate("L4 While #{0} cond term read, err '', its wire == #{1}'s out wire".format(R4["loop"], R4["eq"]),
           le.get("cond_term_uid") and not le.get("err") and so and le.get("cond_wire_uid") == so[0][3], le)
    h1 = bp.labview_handles()
    s.R["mem"].update(after_fs_mb=mb(), handles_after=h1)
    s.fact("MEM after FS reads: {0} MB private; handles {1} -> {2}".format(s.R["mem"]["after_fs_mb"], h0, h1))
    gr = {"vi": BED, "md5": BEDM, "source": "tools/bench/diag_c136_1_graph.py (read_live + mloops + owner_of + gscript.fs_frames on a "
          "never-saved byte copy of the bed, no edit; fs_tunnel_pairs from " + FSP + ")", "terminals": T,
          "objs": lv["objs"], "loops": loops, "fs_tunnel_pairs": fsp, "owners": dict((str(k), list(v)) for k, v in sorted(O.items())),
          "fs_measured": {"fs_frames": ff, "read_err": ferr, "op": "OpFsDiagrams_v0 via gscript.fs_frames"}}
    m = SS.fs_measured_state(gr)
    gr["fs_measured"]["borders"] = dict((str(k), v) for k, v in m["borders"].items())
    out = os.path.join(HERE, "{0}_{1}.json".format(PL["out_prefix"], s.stamp))
    json.dump(gr, open(out, "w", encoding="utf-8"))
    s.fact("WROTE {0} md5 {1}: {2} rows, {3} objs, {4} loops, {5} FS, {6} border tunnels, {7} border entries".format(
        out, K.md5(out), len(T), len(lv["objs"]), len(loops), len(fsu), len(m["borders"]), len(m["fs_border_entries"])))
    s.gate("G1 graph: rows > 0, every Diagram owner resolved", T and all(O[d][0] != "?" for d in diags), [d for d in diags if O[d][0] == "?"][:10])
    s.gate("G2 loop body owned by the While; While on an FS frame", O.get(LP["body"]) == ("WhileLoop", LP["uid"])
           and O.get(LP["owner"], ("", 0))[0] == "FlatSequenceFrame", (O.get(LP["body"]), O.get(LP["owner"])))
    s.gate("G3 case frames owned by the case", all(O.get(f) == ("CaseStructure", CS["uid"]) for f in CS["frames"]),
           [(f, O.get(f)) for f in CS["frames"]])
    allf = [f for v in ff.values() for f in v]
    s.gate("FS1 every FlatSequence read ({0}), each has >= 1 frame, no frame in two FS".format(len(fsu)),
           fsu and all(ff[str(u)] for u in fsu) and len(allf) == len(set(allf)), ff)
    gb = SS.fs_border_gate(gr, {"actions": None, "fs_routes": None, "route_check": None, "carried": gr.get("fs_carried")})
    s.R["fs_border_gate"] = gb
    s.fact("B UNMEASURED FS border tunnels (listed, PD288(b)): {0} of {1}".format(gb["unmeasured"], len(m["borders"])))
    s.gate("B gate B scoped: {0} UNMEASURED FS border tunnel(s) listed, none used (no plan named)".format(len(gb["unmeasured"])),
           gb["status"] == "PASS", gb["used"])
    s.R["graph"] = {"path": os.path.relpath(out, ROOT), "md5": K.md5(out)}
    s.gate("X input md5 unchanged", K.md5(BED) == BEDM, K.md5(BED))
    s.dump()


if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
