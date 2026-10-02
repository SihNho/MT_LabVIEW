r"""diag_c134_1_graph - card 134-1 (c) (PD287(b)(e)): READ-ONLY graph of a never-saved byte copy of the KEPT in-between file
claudeDev\scratch_c133_6_ring_p3b2a_20261002_093837.vi (md5 6cc69221; plan diag_c134_1_graph_plan.json), fresh LabVIEW
-> tools/bench/graph_ring_p3b2a_fs_<ts>.json = the shape of graph_ring_p3b2a_20261002_094927.json PLUS `fs_measured`:
{fs_frames: {fs: [frames LEFT TO RIGHT]} (one gscript.fs_frames = OpFsDiagrams_v0 read per Flat Sequence), borders: per
FlatSequenceOuterTunnel its faces with frames (stagesim.fs_measured_state over the rows)}.
PRIOR ART (reused): tools/bench/diag_c133_5_graph_p3b2a.py line for line (read_live + mloops + owner_of); gscript.fs_frames
(gscript.py:4902, measured in diag_c125_5_opfs.py); no new op.
PREDICTION: G1 rows > 0, every Diagram owner resolved; G2 loop body owned by While #637 on an FS frame; G3 case frames owned by
#22694; R rows (term_uid, wire_uid) == graph_ring_p3b2a_20261002_094927.json's; FS1 every FlatSequence read, frames > 0, no
frame in two FS; FS2 FS #27509 has 3 frames == {27641, 32464, 27722} (order REPORTED: f0 == 27641 is the question);
B every FlatSequenceOuterTunnel has one inner + one outer face; X input md5 unchanged; LabVIEW gone.
CARD 134-6 (PD288(b), PD291(d)): gate B is SCOPED (stagesim.fs_border_gate): UNMEASURED border tunnels (nested FS) are LISTED as a
FACT and gate B FAILS only if the plan named by the graph plan's optional `uses_plan` (or the carried map) uses one - no failing
log by design. R and FS2 are skipped (FACT) when the plan sets `same_rows_as` / `fs_watch` null (a caller that compares itself).
    py tools/bgrun.py --material --max-min 15 --log tools/bench/diag_c134_1_graph.log -- py -u tools/bench/diag_c134_1_graph.py"""
import json, os, sys                                                                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K, vigraph as V, stagesim as SS                                           # noqa: E401,E402
g = K.g
PL = json.load(open(os.path.join(HERE, "diag_c134_1_graph_plan.json"), encoding="utf-8"))
BED, BEDM, FSP, LP, CS, FW = PL["input"]["vi"], PL["input"]["md5"], PL["fs_pairs_from"], PL["loop"], PL["case"], PL.get("fs_watch")
DRY = bool(getattr(g.report_all, "_dry", False))
s = K.Stage(BED, BEDM, "scratch_c134_1_graph_p3b2a", preload=False, deadline_min=13, reserve_s=120,
            out_json=os.path.join(HERE, "diag_c134_1_graph.json"), task="card 134-1 (c)")


def mb():
    return round((K.private_bytes() or 0) / 1e6, 1)


def body(_):
    s.fact("input md5 before: {0}".format(K.md5(BED)))
    s.start(); s.discard_work(); W = s.work                                                  # noqa: E702
    if DRY:
        return s.dump()
    bp = K.mod("bench_prep"); h0 = bp.labview_handles()                                      # noqa: E702
    s.R["mem"] = {"after_load_mb": mb()}
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
    s.R["mem"]["after_fs_mb"] = mb()
    h1 = bp.labview_handles()
    s.fact("MEM after FS reads: {0} MB private; handles {1} -> {2}".format(s.R["mem"]["after_fs_mb"], h0, h1))
    gr = {"vi": BED, "md5": BEDM, "source": "tools/bench/diag_c134_1_graph.py (read_live + mloops + owner_of + gscript.fs_frames on a "
          "never-saved byte copy of the kept in-between file, no edit; fs_tunnel_pairs from " + FSP + ")", "terminals": lv["terminals"],
          "objs": lv["objs"], "loops": loops, "fs_tunnel_pairs": fsp, "owners": dict((str(k), list(v)) for k, v in sorted(O.items())),
          "fs_measured": {"fs_frames": ff, "read_err": ferr, "op": "OpFsDiagrams_v0 via gscript.fs_frames"}}
    m = SS.fs_measured_state(gr)
    gr["fs_measured"]["borders"] = dict((str(k), v) for k, v in m["borders"].items())
    out = os.path.join(HERE, "graph_ring_p3b2a_fs_{0}.json".format(s.stamp))
    json.dump(gr, open(out, "w", encoding="utf-8"))
    s.fact("WROTE {0} md5 {1}: {2} rows, {3} objs, {4} loops, {5} FS, {6} border tunnels, {7} border entries".format(
        out, K.md5(out), len(lv["terminals"]), len(lv["objs"]), len(loops), len(fsu), len(m["borders"]), len(m["fs_border_entries"])))
    T = lv["terminals"]
    s.gate("G1 graph: rows > 0, every Diagram owner resolved", T and all(O[d][0] != "?" for d in diags), [d for d in diags if O[d][0] == "?"][:10])
    s.gate("G2 loop body owned by the While; While on an FS frame", O.get(LP["body"]) == ("WhileLoop", LP["uid"])
           and O.get(LP["owner"], ("", 0))[0] == "FlatSequenceFrame", (O.get(LP["body"]), O.get(LP["owner"])))
    s.gate("G3 case frames owned by the case", all(O.get(f) == ("CaseStructure", CS["uid"]) for f in CS["frames"]),
           [(f, O.get(f)) for f in CS["frames"]])
    if PL["input"].get("same_rows_as"):                       # card 134-6: a caller that compares the whole graph itself sets None
        ref = json.load(open(os.path.join(ROOT, PL["input"]["same_rows_as"]), encoding="utf-8"))
        key = lambda rows: sorted((int(r["term_uid"]), int(r["wire_uid"] or 0)) for r in rows)   # noqa: E731
        s.gate("R rows (term_uid, wire_uid) == {0}'s ({1} vs {2})".format(PL["input"]["same_rows_as"], len(T), len(ref["terminals"])),
               key(T) == key(ref["terminals"]), {"only_new": sorted(set(key(T)) - set(key(ref["terminals"])))[:10],
                                                   "only_ref": sorted(set(key(ref["terminals"])) - set(key(T)))[:10]})
    else:
        s.fact("R not gated here: plan same_rows_as is null (the caller compares terminals/wires/fs_frames/borders itself)")
    allf = [f for v in ff.values() for f in v]
    s.gate("FS1 every FlatSequence read ({0}), each has >= 1 frame, no frame in two FS".format(len(fsu)),
           fsu and all(ff[str(u)] for u in fsu) and len(allf) == len(set(allf)), ff)
    if FW:
        w = ff.get(str(FW["uid"])) or []
        f0b = FW["frames_bound_by_elimination"][0]                                            # the plan file's f0, never re-typed
        s.R["fs_watch"] = {"frames": w, "f0_as_bound": bool(w) and w[0] == f0b}
        s.fact("FS #{0} frames LEFT TO RIGHT {1}; f0 == {2} (bound by elimination): {3}".format(FW["uid"], w, f0b, s.R["fs_watch"]["f0_as_bound"]))
        s.gate("FS2 FS #{0} frames as a set == {1}".format(FW["uid"], FW["frames_bound_by_elimination"]),
               sorted(w) == sorted(FW["frames_bound_by_elimination"]), w)
    else:
        s.fact("FS2 not gated here: plan fs_watch is null (the caller compares fs_frames itself)")
    # card 134-6 (PD288(b), PD291(d)): gate B SCOPED, never relaxed - UNMEASURED border tunnels are LISTED; the gate fails
    # only when the plan named by `uses_plan` (actions, fs_routes, route-check rows) or the graph's carried map uses one.
    up = PL.get("uses_plan")
    pu = json.load(open(os.path.join(ROOT, up), encoding="utf-8")) if up else {}
    fz = pu.get("finalized") or {}
    uses = {"actions": pu.get("actions"), "fs_routes": fz.get("fs_routes"), "route_check": (fz.get("route_check") or {}).get("rows"),
            "carried": gr.get("fs_carried")}
    gb = SS.fs_border_gate(gr, uses)
    s.R["fs_border_gate"] = gb
    s.fact("B UNMEASURED FS border tunnels (listed, PD288(b)): {0} of {1}".format(gb["unmeasured"], len(m["borders"])))
    s.gate("B gate B scoped: {0} UNMEASURED FS border tunnel(s) listed, none used by {1}".format(
        len(gb["unmeasured"]), up or "a plan (none named) or the carried map"), gb["status"] == "PASS", gb["used"])
    s.R["graph"] = {"path": os.path.relpath(out, ROOT), "md5": K.md5(out)}
    s.gate("X input md5 unchanged", K.md5(BED) == BEDM, K.md5(BED))
    s.dump()


if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
