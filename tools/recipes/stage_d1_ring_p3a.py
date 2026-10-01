r"""stage_d1_ring_p3a - card 124-6, RING P3a (d1-loop12-17-split-plan.md PD246(c)(d), 247, 248(a), 249(c), 250(c)(d)): on the SAVED P2b bed
D1_ring_p2b_20261001_140658.vi (md5 652b1447) build loop 1.1's control in While #637 (body #639): Wait (ms) 1; previous-BufNum register
(I32 -1) + Equal?(BufNum, prev) -> case_wired; new-frame counter register (I32 0) through the case (False: +1 by Increment, True:
pass-through) and Quotient & Remainder(count, 20) in the False frame. FRESH LabVIEW -> claudeDev\D1_ring_p3a_<ts>.vi (rule-6 GUI save,
ExecState 0 by design: the P2b bed is broken, never run) + tools\bench\errorlist_expected_D1_ring_p3a_<ts>.json (P2b's 54 + the
predicted new items). ROWS ONLY FROM plan_ring_p3a.json (stagesim FINAL of plan_ring_p3a_in_v3.json, plan_ring_p3a_make_v3.py);
expected values only from plan_ring_p3a_pred.json. PRIOR ART: stage_d1_ring_p2b.py (Executor/LVBackend/DryPlanBE, D/TD/FU/PB/HB/PS
gates, save); routes connect_term_uid (R1/R2) and case_frame_wire new_wire/branch (R3/R4) measured by card 124-5
(diag_c124_p3a_scratch.log:53,61,71,77). No new op.
PREDICTION: L1 25 actions -> 21 ops == pred kinds; E1 every checkpoint == sim; ST 2 new SelectorTunnels, each one inner face per case
frame; R4 Q&R.x on Increment.x's wire; D new wires == sim's, none lost; CEN2 == pred census (UNVERIFIED-DRY in a dry run); TD every
base terminal keeps its wire; FU frames == base + the case's 2; PB cdiff(S1, end) == the P2b bed's 16 rows (FATAL, before save);
HB open->save handles <= +700; PS saved, input unchanged; EL errorlist_expected written (54 + 0).
    py tools/bgrun.py --material --max-min 45 --log tools/bench/stage_d1_ring_p3a.log -- py -u tools/recipes/stage_d1_ring_p3a.py"""
import copy, json, os, sys                                                         # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, vigraph as V, stagexec as SX, jev_candidates as JC   # noqa: E401,E402
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                 # noqa: E731
PLAN = os.path.join(K.BENCH, "plan_ring_p3a.json")                                  # ONE literal: stage_prerun.plan_files reads it
P = J(PLAN); BASE = J(K.ROOT, P["finalized"]["base"]["path"]); A = P["actions"]   # noqa: E702
PRED = J(K.BENCH, "plan_ring_p3a_pred.json")
DRY, LAB, SAVE = bool(getattr(g.report_all, "_dry", False)), JC.node_labels_default(), True
SRC = tuple(PRED["census"])
wires = lambda rows: set(int(r["wire_uid"]) for r in rows if r["wire_uid"])        # noqa: E731
frames = lambda rows: set(int(r["frame_diagram"] or 0) for r in rows)              # noqa: E731
snap = lambda s: dict((u, c) for u, c in s.census_snapshot().items() if c in SRC)   # noqa: E731


def body(s):
    print(__doc__, flush=True)
    s.gate("L0 plan FINAL, open_rows_match, plan_in = plan_ring_p3a_in_v3; base graph md5 == pred == file; bed md5 == pred; plan end cdiff == P2b's rows",
           P.get("final") is True and P["finalized"].get("open_rows_match") is True and os.path.splitext(P["finalized"]["plan_in"]["path"])[0].endswith("plan_ring_p3a_in_v3")
           and P["finalized"]["base"]["md5"] == PRED["graph"]["md5"] == K.md5(os.path.join(K.ROOT, P["finalized"]["base"]["path"])) and BASE["md5"] == PRED["bed_md5"]
           and sorted(P["finalized"]["end_cdiff_rows"]) == PRED["cdiff_rows"], (K.md5(PLAN), P["finalized"]["base"], BASE["md5"]), fatal=True)
    s.start(); s.discard_work(); bp = K.mod("bench_prep"); h0 = bp.labview_handles(); c0 = snap(s)   # noqa: E702
    be = SX.DryPlanBE(s, P, PLAN, BASE) if DRY else SX.LVBackend(s, BASE["fs_tunnel_pairs"], sink_gates=[], gates={}, mem_stop_mb=SX.MEM_STOP_MB)
    x = SX.Executor(PLAN, be, log=lambda m: print(m, flush=True))
    s.gate("L1 the {0} actions compile into {1} real ops == pred kinds, each action once".format(len(A), len(x.ops)),
           [o["kind"] for o in x.ops] == PRED["ops"] and sorted(n for o in x.ops for n in o["acts"]) == list(range(1, len(A) + 1)), [o["kind"] for o in x.ops], fatal=True)
    try:
        real = x.run(); s.gate("E1 every checkpoint's real graph == its simulated step ({0} ops)".format(len(x.ops)), True)   # noqa: E702
    except SX.ExecStop as e:
        return SX.report_stop(s, x, be, e)
    s.R["stagexec"] = x.report
    L = x.step(len(A))["state"]
    rb = lambda sym: x.bind["obj"].get(L["sym"][sym], x.bind["diag"].get(L["sym"][sym], L["sym"][sym]))   # noqa: E731 - frames: bind['diag']
    term = lambda sym, nm: [r for r in real if r["owner_uid"] == rb(sym) and r["term_name"] == nm]   # noqa: E731
    cs, fr = rb("new:CS1"), [rb("new:CS1.f0"), rb("new:CS1.f1")]
    st_ = [[r for r in real if r["owner_uid"] == rb(t)] for t in ("new:TI1", "new:TO1")]
    s.gate("ST 2 new SelectorTunnels (TI1 in, TO1 out) on case #{0}, each ONE outer face + ONE inner face on each frame {1}".format(cs, fr),
           all(len(t) == 3 and set(r["owner_class"] for r in t) == {"SelectorTunnel"} and sorted(int(r["frame_diagram"] or 0) for r in t
               if r["term_class"] == "InnerTerminal") == sorted(fr) for t in st_), st_)
    qx, ix = term("new:QR1", "x"), term("new:INC1", "x")
    s.gate("R4 Q&R.x sits on Increment.x's wire (the False face BRANCHED, PD250(c))", len(qx) == len(ix) == 1 and qx[0]["wire_uid"]
           and qx[0]["wire_uid"] == ix[0]["wire_uid"], (qx, ix))
    sim_new, sim_lost = wires(L["terminals"]) - wires(BASE["terminals"]), wires(BASE["terminals"]) - wires(L["terminals"])
    new, lost = wires(real) - wires(BASE["terminals"]), wires(BASE["terminals"]) - wires(real)
    s.gate("D new wires {0} == sim's {1}; lost {2} == sim's {3}".format(len(new), len(sim_new), len(lost), len(sim_lost)),
           len(new) == len(sim_new) and len(lost) == len(sim_lost) == 0, {"new": sorted(new), "lost": sorted(lost)[:20]})
    dc = s.census_gate("CEN2 new-object census (classes of the pred) == plan_ring_p3a_pred.json census", c0, snap(s), PRED["census"])
    bw, rw = dict((int(r["term_uid"]), int(r["wire_uid"] or 0)) for r in BASE["terminals"]), dict((int(r["term_uid"]), int(r["wire_uid"] or 0)) for r in real)
    chg = [(t, w_, rw.get(t)) for t, w_ in bw.items() if rw.get(t) != w_]
    s.gate("TD every base terminal keeps its wire, none lost", not chg and not set(bw) - set(rw), {"changed": chg[:20], "lost_rows": sorted(set(bw) - set(rw))[:20]})
    s.gate("FU frame diagrams == base + the case's 2 frames", frames(real) == frames(BASE["terminals"]) | set(fr), sorted(frames(BASE["terminals"]) ^ frames(real))[:20], fatal=True)
    s.es("after all rows (ExecState 0 expected: the P2b bed is broken by design)")
    s1p = J(JC.WIKI, JC.S1_KEY + ".json")
    S1f = V.build4(s1p["terminals"], J(JC._newest("graph_objs_s1_*.json"))["objects"], J(JC._newest("graph_loops_s1_*.json"))["loops"], LAB, s1p["fs_tunnel_pairs"], frame_keyed=True)
    G1 = V.build4(real, getattr(be, "last_objs", None) or be.st["objs"], copy.deepcopy(L["loops"]), LAB, BASE["fs_tunnel_pairs"], frame_keyed=True)
    cd = V.computation_diff_frame(S1f, G1)
    rk = sorted(str(y["sink"]) for y in cd["rows"])
    s.gate("PB frame-keyed cdiff(S1, real end) == the P2b bed's {0} rows and the plan's {1} open (node, term) pairs (FATAL, before save)".format(len(PRED["cdiff_rows"]), len(P["open_rows"])),
           rk == PRED["cdiff_rows"] and set((int(y["node"]), str(y["sink"]).split("|")[2]) for y in cd["rows"]) == set((int(y["node"]), y["term"]) for y in P["open_rows"]),
           {"extra": sorted(set(rk) - set(PRED["cdiff_rows"])), "missing": sorted(set(PRED["cdiff_rows"]) - set(rk))}, fatal=True)
    h1 = None if DRY else bp.labview_handles(); s.fact("PH handles: post-open {0} -> before-save {1}".format(h0, h1))   # noqa: E702
    s.gate("HB open->save handle growth <= +700 (PD236(b) band; refs balance is H5)", DRY or (h1 is not None and h0 is not None and h1 - h0 <= 700), (h0, h1))
    m = s.save(broken_ok=True) if SAVE else None
    SAVE and s.gate("PS artefact saved, md5 differs from the input; input unchanged", m and m != s.input_md5 and K.md5(s.input_vi) == s.input_md5, m)
    _x = m and m != s.input_md5 and s.work in s.scratches and s.scratches.remove(s.work)   # noqa: F841
    el = PRED["errorlist"]
    if m and not DRY:                                                              # the P2b licences + the predicted new items
        ex = dict(J(K.ROOT, el["base_file"]), bed=s.work, bed_md5=m, total=el["predicted_total"], measured_from=None,
                  decided_by="card 124-6 plan prediction (plan_ring_p3a_pred.json errorlist): the P2b bed's {0} licences + {1} new; "
                             "pin on the scratch run's Error List (PD235(f))".format(el["bed_total"], el["new_items_predicted"]))
        ep = os.path.join(K.BENCH, "errorlist_expected_{0}.json".format(os.path.splitext(os.path.basename(s.work))[0]))
        json.dump(ex, open(ep, "w", encoding="utf-8"), indent=1)
        s.gate("EL errorlist_expected written: total {0} == P2b {1} + predicted new {2}".format(ex["total"], el["bed_total"], el["new_items_predicted"]),
               ex["total"] == el["bed_total"] + el["new_items_predicted"], ep)
    s.R["ring_p3a"] = {"final": s.work if m else None, "md5": m, "cdiff_rows": rk, "handles": [h0, h1], "census_delta": dc, "case": cs, "frames": fr,
                       "errorlist_predicted_new": el["new_items_predicted"], "level": "STRUCTURAL, broken by design (P2b bed), never run"}; s.dump()   # noqa: E702


if __name__ == "__main__":
    st = K.Stage(BASE["vi"], BASE["md5"], "D1_ring_p3a", preload=False, deadline_min=40, out_json=os.path.join(K.BENCH, "stage_d1_ring_p3a.json"), task="card 124-6 RING P3a")
    rc = K.run(body, st)
    DRY or SX.kill_labview_at_exit()
    sys.exit(rc)
