r"""stage_d1_ring_p2a - card 121-2, RING P2a (d1-loop12-17-split-plan.md PD238(a)(g), docs/ring-buffer-design.md): from the SAVED pool bed
D1_qrt_pool_20260928_141055.vi DELETE the pool queues - Obtain Q_free, Obtain Q_work, the For-body Enqueue, the I32 20 (+ their wires) -
and KEEP the For, IMAQ Create, names constant, ring and names tunnel (the 20 images stay; P3 wires them). FRESH LabVIEW -> claudeDev\D1_ring_p2a_<ts>.vi
(rule-6 GUI save, ExecState 0 by design, never run). ROWS ONLY FROM plan_ring_p2a.json (stagesim FINAL of plan_ring_p2a_in.json, plan_ring_p2a_make.py);
expected values only from plan_ring_p2a_pred.json. PRIOR ART: stage_d1_l2r2.py (retire cut: RetireGuardBE live-consumer check before each delete,
retire_ends, terminal-list diff) + stage_d1_qrt_pool.py (Executor/LVBackend/DryPlanBE, PB cdiff, save). No new op.
PREDICTION: L1 8 actions -> 8 ops (4 delete_wire + 4 delete_object); LC x4; E1 every checkpoint == sim; D no new wire, lost == the 4 deleted wires;
CEN nodes lost == the 4 + the Enqueue's queue tunnel (auto-removed with its last wire, opmodel delete_wire.json); CEN2 LoopTunnel -1, Wire -4;
ENDS w14741 keeps uid/source/kept sink; TD every other base terminal keeps its wire, IMAQ New Image -> 0, w14741 list == R2's; FU frames unchanged;
PB cdiff(S1, end) == the pool bed's 16 rows (FATAL, before save); HB open->save handles <= +700 (PD236(b)); PS saved, input unchanged.
    py tools/bgrun.py --material --max-min 45 --log tools/bench/stage_d1_ring_p2a.log -- py -u tools/recipes/stage_d1_ring_p2a.py"""
import copy, json, os, sys                                                         # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, vigraph as V, stagexec as SX, jev_candidates as JC   # noqa: E401,E402
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                 # noqa: E731
PLAN = os.path.join(K.BENCH, "plan_ring_p2a.json")                                  # ONE literal: stage_prerun.plan_files reads it
P = J(PLAN); BASE = J(K.ROOT, P["finalized"]["base"]["path"]); A = P["actions"]   # noqa: E702
PRED = J(K.BENCH, "plan_ring_p2a_pred.json")
DRY, LAB, SAVE = bool(getattr(g.report_all, "_dry", False)), JC.node_labels_default(), True
RET = set(int(a["uid"]) for a in A if a["op"] == "delete_object"); GONE = RET | set(PRED["auto_removed"])   # noqa: E702
DW = [int(a["wire_uid"]) for a in A if a["op"] == "delete_wire"]
POOLEND = J(K.BENCH, "stage_d1_qrt_pool.json")["qrt_pool"]["cdiff_rows"]            # the REAL pool-bed end's cdiff sinks
SRC = ("LoopTunnel", "Wire", "WhileLoop", "Diagram", "SubVI", "Local", "ControlTerminal", "Node")
wires = lambda rows: set(int(r["wire_uid"]) for r in rows if r["wire_uid"])        # noqa: E731
frames = lambda rows: set(int(r["frame_diagram"] or 0) for r in rows)              # noqa: E731
nodes = lambda rows: set(int(r["owner_uid"]) for r in rows)                          # noqa: E731


def body(s):
    print(__doc__, flush=True)
    s.gate("L0 plan FINAL, open_rows_match, plan_in = plan_ring_p2a_in; base graph md5 == pred == file; bed md5 == pred; plan end cdiff == the pool bed's rows",
           P.get("final") is True and P["finalized"].get("open_rows_match") is True and os.path.splitext(P["finalized"]["plan_in"]["path"])[0].endswith("plan_ring_p2a_in")
           and P["finalized"]["base"]["md5"] == PRED["graph"]["md5"] == K.md5(os.path.join(K.ROOT, P["finalized"]["base"]["path"])) and BASE["md5"] == PRED["bed_md5"]
           and sorted(P["finalized"]["end_cdiff_rows"]) == sorted(POOLEND) == PRED["cdiff_rows"], (K.md5(PLAN), P["finalized"]["base"], BASE["md5"]), fatal=True)
    s.gate("L0c delete_object rows == pred retire (4), delete_wire rows == pred stubs + orphan, none on a kept node",
           sorted(RET) == sorted(PRED["retire"]) and len(RET) == 4 and sorted(DW) == sorted(PRED["stubs"] + PRED["orphan"]) and len(DW) == len(set(DW))
           and not GONE & set(PRED["keep"].values()), {"retire": sorted(RET), "dw": DW, "keep": PRED["keep"]}, fatal=True)
    s.start(); s.discard_work(); bp = K.mod("bench_prep"); h0 = bp.labview_handles(); c0 = s.census(SRC, tag="before P2a")   # noqa: E702
    be = SX.DryPlanBE(s, P, PLAN, BASE) if DRY else SX.LVBackend(s, BASE["fs_tunnel_pairs"], sink_gates=[], gates={}, mem_stop_mb=SX.MEM_STOP_MB)
    gb = SX.RetireGuardBE(be, s, dict((u, [u]) for u in RET), (lambda: [dict(r) for r in be.st["terminals"]]) if DRY else be.read)
    x = SX.Executor(PLAN, gb, log=lambda m: print(m, flush=True))
    s.gate("L1 the {0} actions compile into {1} real ops == pred kinds, each action once".format(len(A), len(x.ops)),
           [o["kind"] for o in x.ops] == PRED["ops"] and sorted(n for o in x.ops for n in o["acts"]) == list(range(1, len(A) + 1)), [o["kind"] for o in x.ops], fatal=True)
    try:
        real = x.run(); s.gate("E1 every checkpoint's real graph == its simulated step ({0} ops)".format(len(x.ops)), True)   # noqa: E702
    except SX.ExecStop as e:
        return SX.report_stop(s, x, be, e)
    s.R["stagexec"] = x.report
    s.gate("LC all {0} live-consumer checks PASS (each re-read before its delete)".format(len(RET)), len(gb.checks) == len(RET) and all(c["ok"] for c in gb.checks), gb.checks)
    L = x.step(len(A))["state"]
    sim_new, sim_lost = wires(L["terminals"]) - wires(BASE["terminals"]), wires(BASE["terminals"]) - wires(L["terminals"])
    new, lost = wires(real) - wires(BASE["terminals"]), wires(BASE["terminals"]) - wires(real)
    s.gate("D no new wire; lost == the simulated == the {0} deleted wires".format(len(DW)), new == sim_new == set() and lost == sim_lost == set(DW),
           {"new": sorted(new)[:20], "lost": sorted(lost), "sim_lost": sorted(sim_lost)})
    s.gate("CEN terminal-graph nodes lost == the 4 retired + the auto-removed queue tunnel {0}, none added".format(PRED["auto_removed"]),
           nodes(BASE["terminals"]) - nodes(real) == GONE and not nodes(real) - nodes(BASE["terminals"]),
           {"lost": sorted(nodes(BASE["terminals"]) - nodes(real)), "added": sorted(nodes(real) - nodes(BASE["terminals"]))})
    c1 = s.census(SRC, tag="after P2a")
    dc = dict((k, (c1.get(k) or 0) - (c0.get(k) or 0)) for k in SRC)
    s.fact("CENSUS DELTA {0} (Node recorded, not gated)".format(dc))
    s.gate("CEN2 class census: LoopTunnel {0}, Wire {1}, WhileLoop/Diagram/SubVI/Local/ControlTerminal 0".format(PRED["census"]["LoopTunnel"], PRED["census"]["Wire"]),
           DRY or (dc["LoopTunnel"] == PRED["census"]["LoopTunnel"] and dc["Wire"] == PRED["census"]["Wire"] and not any(dc[k] for k in ("WhileLoop", "Diagram", "SubVI", "Local", "ControlTerminal"))), dc)
    kept_nets = [dict(r, wire_uid=0 if int(r["wire_uid"] or 0) in DW else r["wire_uid"]) for r in BASE["terminals"]]   # the deleted wires are gate D's, not shared nets
    eok, ed = SX.retire_ends(kept_nets, real, GONE)
    s.gate("ENDS every net shared by a retired and a kept terminal keeps its uid, source(s) and kept sinks ({0})".format(sorted(ed["shared_wires"])),
           eok and sorted(ed["shared_wires"]) == PRED["shared"], ed)
    bw, rw = dict((int(r["term_uid"]), int(r["wire_uid"] or 0)) for r in BASE["terminals"]), dict((int(r["term_uid"]), int(r["wire_uid"] or 0)) for r in real)
    gone_rows, unw = set(PRED["terminal_rows_lost"]), set(PRED["terminal_unwired"])
    chg = [(t, w, rw.get(t)) for t, w in bw.items() if t not in gone_rows and rw.get(t) != (0 if t in unw else w)]
    wimg = sorted((int(r["term_uid"]), bool(r["is_source"])) for r in real if int(r["wire_uid"] or 0) == PRED["w_img"])
    s.gate("TD rows lost == the 5 nodes' rows, none added; every other base terminal keeps its wire, {0} -> 0; w{1} list == R2's".format(sorted(unw), PRED["w_img"]),
           set(bw) - set(rw) == gone_rows and not set(rw) - set(bw) and not chg and wimg == [tuple(x) for x in PRED["w_img_after"]],
           {"changed": chg[:20], "rows_lost_extra": sorted((set(bw) - set(rw)) ^ gone_rows)[:20], "w_img": wimg})
    s.gate("FU the set of frame diagrams is unchanged", frames(BASE["terminals"]) == frames(real), sorted(frames(BASE["terminals"]) ^ frames(real))[:20], fatal=True)
    s.es("after all rows (ExecState 0 expected: the pool bed is broken by design)")
    s1p = J(JC.WIKI, JC.S1_KEY + ".json")
    S1f = V.build4(s1p["terminals"], J(JC._newest("graph_objs_s1_*.json"))["objects"], J(JC._newest("graph_loops_s1_*.json"))["loops"], LAB, s1p["fs_tunnel_pairs"], frame_keyed=True)
    G1 = V.build4(real, getattr(be, "last_objs", None) or be.st["objs"], copy.deepcopy(L["loops"]), LAB, BASE["fs_tunnel_pairs"], frame_keyed=True)
    cd = V.computation_diff_frame(S1f, G1)
    rk = sorted(str(y["sink"]) for y in cd["rows"])
    s.gate("PB frame-keyed cdiff(S1, real end) == the pool bed's {0} rows and the plan's {1} open (node, term) pairs (FATAL, before save)".format(len(POOLEND), len(P["open_rows"])),
           rk == sorted(POOLEND) and set((int(y["node"]), str(y["sink"]).split("|")[2]) for y in cd["rows"]) == set((int(y["node"]), y["term"]) for y in P["open_rows"]),
           {"extra": sorted(set(rk) - set(POOLEND)), "missing": sorted(set(POOLEND) - set(rk))}, fatal=True)
    h1 = None if DRY else bp.labview_handles(); s.fact("PH handles: post-open {0} -> before-save {1}".format(h0, h1))   # noqa: E702
    s.gate("HB open->save handle growth <= +700 (PD236(b) band; refs balance is H5)", DRY or (h1 is not None and h0 is not None and h1 - h0 <= 700), (h0, h1))
    m = s.save(broken_ok=True) if SAVE else None
    SAVE and s.gate("PS artefact saved, md5 differs from the input; input unchanged", m and m != s.input_md5 and K.md5(s.input_vi) == s.input_md5, m)
    _x = m and m != s.input_md5 and s.work in s.scratches and s.scratches.remove(s.work)   # noqa: F841
    s.R["ring_p2a"] = {"final": s.work if m else None, "md5": m, "cdiff_rows": rk, "handles": [h0, h1], "census_delta": dc, "lc": gb.checks,
                       "errorlist_predicted_new": PRED["errorlist"]["new_items_predicted"], "level": "STRUCTURAL, broken by design (pool bed), never run"}; s.dump()   # noqa: E702


if __name__ == "__main__":
    st = K.Stage(BASE["vi"], BASE["md5"], "D1_ring_p2a", preload=False, deadline_min=40, out_json=os.path.join(K.BENCH, "stage_d1_ring_p2a.json"), task="card 121-2 RING P2a")
    rc = K.run(body, st)
    DRY or SX.kill_labview_at_exit()
    sys.exit(rc)
