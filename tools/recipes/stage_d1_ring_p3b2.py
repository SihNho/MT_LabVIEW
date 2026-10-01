r"""stage_d1_ring_p3b2 - card 129-1 (WRITTEN, NOT LAUNCHED), RING P3b-2 (d1-loop12-17-split-plan.md PD246(c) A2, PD238(c), PD240(a),
PD257(a), PD258(a), PD261(d), PD263(b)): on P3b-1's SAVED artefact, in the Flat Sequence P3b-1 built on case #22694's False frame,
add TransPos/RotPos/FrameIdx at i in frame f1 (local read -> Replace Array Subset -> local write; i by the INNER-FACE branch of
P3b-1's entry tunnel; values #30117 Value, #4580 Value, #637 i) and Latest = BufNum in frame f2 (inner branch of P3b-1's BufNum
tunnel); wire_remove_loose_ends after every crossing. BASE IS PROVISIONAL (P3b-1's simulated end, stage_prerun refuses the launch):
`py tools/stage_prerun.py --rebase tools/bench/plan_ring_p3b2.json --graph <graph of P3b-1's saved VI>` first, then the pred again.
FRESH LabVIEW -> claudeDev\D1_ring_p3b2_<ts>.vi (rule-6 GUI save, ExecState 0 by design) + errorlist_expected (54 + 0 own).
ROWS ONLY FROM plan_ring_p3b2.json (stagesim FINAL of plan_ring_p3b2_in.json, plan_ring_p3b_split.py); expected values only from
plan_ring_p3b2_pred.json. PRIOR ART: stage_d1_ring_p3b1.py / stage_d1_ring_p3a.py (same skeleton and gates). No new op.
PREDICTION: L1 30 actions -> pred ops; E1 every checkpoint == sim; NG (card 132-1, PD275(c)) every crossing op's new tunnel
names == the step files' (a mismatch = ExecStop NAME-GATE at that op); FR every created object sits on a frame of the base's FS, no
new frame; D new/lost wires == sim's; TD every base terminal that was wired stays wired; CEN2 == pred census; PB cdiff(S1, end)
== the 16 rows (FATAL, before save); HB handles <= +700; PS saved, input unchanged; EL 54.
    py tools/bgrun.py --material --max-min 50 --log tools/bench/stage_d1_ring_p3b2.log -- py -u tools/recipes/stage_d1_ring_p3b2.py"""
import copy, json, os, sys                                                         # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, vigraph as V, stagexec as SX, jev_candidates as JC   # noqa: E401,E402
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                 # noqa: E731
PLAN = os.path.join(K.BENCH, "plan_ring_p3b2.json")                                 # ONE literal: stage_prerun.plan_files reads it
P = J(PLAN); BASE = J(K.ROOT, P["finalized"]["base"]["path"]); A = P["actions"]   # noqa: E702
PRED = J(K.BENCH, "plan_ring_p3b2_pred.json")
DRY, LAB, SAVE = bool(getattr(g.report_all, "_dry", False)), JC.node_labels_default(), True
SRC = tuple(PRED["census"])
BIND = set(k for k, o in enumerate(SX.compile_plan(P), 1) if o["kind"] in SX.BIND_KINDS)   # card 129-8 PD265(c): every op that creates/binds an object
CHECKPOINTS = tuple(sorted({0, len(SX.compile_plan(P))} | BIND))                  # as stage_d1_l2b3.py:16-18 (stagexec.py:1726-1733 refuses a set missing a bind op)
FSPAIRS = BASE.get("fs_tunnel_pairs", BASE.get("fs_pairs"))                         # a real graph / the provisional simulated state
wires = lambda rows: set(int(r["wire_uid"]) for r in rows if r["wire_uid"])        # noqa: E731
frames = lambda rows: set(int(r["frame_diagram"] or 0) for r in rows)              # noqa: E731
snap = lambda s: dict((u, c) for u, c in s.census_snapshot().items() if c in SRC)   # noqa: E731


def body(s):
    print(__doc__, flush=True)
    s.gate("L0 plan FINAL, open_rows_match, plan_in = plan_ring_p3b2_in; base graph md5 == pred == file; bed md5 == pred; plan end cdiff == pred; pred keyed to this plan",
           P.get("final") is True and P["finalized"].get("open_rows_match") is True and os.path.splitext(P["finalized"]["plan_in"]["path"])[0].endswith("plan_ring_p3b2_in")
           and P["finalized"]["base"]["md5"] == PRED["graph"]["md5"] == K.md5(os.path.join(K.ROOT, P["finalized"]["base"]["path"])) and BASE["md5"] == PRED["bed_md5"]
           and sorted(P["finalized"]["end_cdiff_rows"]) == PRED["cdiff_rows"] and PRED["plan"]["md5"] == K.md5(PLAN), (K.md5(PLAN), P["finalized"]["base"], BASE["md5"]), fatal=True)
    s.start(); s.discard_work(); bp = K.mod("bench_prep"); h0 = bp.labview_handles(); c0 = snap(s)   # noqa: E702
    be = SX.DryPlanBE(s, P, PLAN, BASE) if DRY else SX.LVBackend(s, FSPAIRS, sink_gates=[], gates={}, mem_stop_mb=SX.MEM_STOP_MB)
    x = SX.Executor(PLAN, be, log=lambda m: print(m, flush=True), checkpoints=CHECKPOINTS, name_gate=True)   # card 132-1 PD275(c)
    s.gate("L1 the {0} actions compile into {1} real ops == pred kinds, each action once; checkpoints {2}".format(len(A), len(x.ops), CHECKPOINTS),
           [o["kind"] for o in x.ops] == PRED["ops"] and sorted(n for o in x.ops for n in o["acts"]) == list(range(1, len(A) + 1)), [o["kind"] for o in x.ops], fatal=True)
    try:
        real = x.run(); s.gate("E1 every checkpoint's real graph == its simulated step ({0} ops)".format(len(x.ops)), True)   # noqa: E702
    except SX.ExecStop as e:
        return SX.report_stop(s, x, be, e)
    s.R["stagexec"] = x.report
    s.gate("NG every crossing op's NEW tunnel names == the simulator's (stagexec.tunnel_name_check, per op, from the step files): {0} op(s) {1}".format(
        len(x.name_checks), [c["k"] for c in x.name_checks]), all(c["ok"] for c in x.name_checks), x.name_checks[:6])
    L = x.step(len(A))["state"]
    rb = lambda sym: x.bind["obj"].get(L["sym"][sym], x.bind["diag"].get(L["sym"][sym], L["sym"][sym]))   # noqa: E731
    made = [rb("new:" + a["as"]) for a in A if a["op"] == "create" and a.get("as")]
    on = sorted(set(int(r["frame_diagram"] or 0) for r in real if r["owner_uid"] in made))
    bf = frames(BASE["terminals"])
    s.gate("FR the {0} created objects sit on {1} frame(s) of the base, no new frame".format(len(made), on),
           len(made) == 10 and on and set(on) <= bf and frames(real) == bf, {"on": on}, fatal=True)
    sim_new, sim_lost = wires(L["terminals"]) - wires(BASE["terminals"]), wires(BASE["terminals"]) - wires(L["terminals"])
    new, lost = wires(real) - wires(BASE["terminals"]), wires(BASE["terminals"]) - wires(real)
    s.gate("D new wires {0} == sim's {1}; lost {2} == sim's {3} (re-created source nets, PD256(c))".format(len(new), len(sim_new), len(lost), len(sim_lost)),
           len(new) == len(sim_new) and len(lost) == len(sim_lost), {"new": sorted(new), "lost": sorted(lost)[:20]})
    dc = s.census_gate("CEN2 new-object census (classes of the pred) == plan_ring_p3b2_pred.json census", c0, snap(s), PRED["census"])
    bw, rw = dict((int(r["term_uid"]), int(r["wire_uid"] or 0)) for r in BASE["terminals"]), dict((int(r["term_uid"]), int(r["wire_uid"] or 0)) for r in real)
    unw = [t for t, w_ in bw.items() if w_ and not rw.get(t)]
    s.gate("TD every base terminal that was wired is still wired, no base row lost", not unw and not set(bw) - set(rw), {"unwired": unw[:20], "lost_rows": sorted(set(bw) - set(rw))[:20]})
    s.es("after all rows (ExecState 0 expected: the P3b-1 bed is broken by design)")
    s1p = J(JC.WIKI, JC.S1_KEY + ".json")
    S1f = V.build4(s1p["terminals"], J(JC._newest("graph_objs_s1_*.json"))["objects"], J(JC._newest("graph_loops_s1_*.json"))["loops"], LAB, s1p["fs_tunnel_pairs"], frame_keyed=True)
    G1 = V.build4(real, getattr(be, "last_objs", None) or be.st["objs"], copy.deepcopy(L["loops"]), LAB, FSPAIRS, frame_keyed=True)
    cd = V.computation_diff_frame(S1f, G1)
    rk = sorted(str(y["sink"]) for y in cd["rows"])
    s.gate("PB frame-keyed cdiff(S1, real end) == the bed's {0} rows and the plan's {1} open (node, term) pairs (FATAL, before save)".format(len(PRED["cdiff_rows"]), len(P["open_rows"])),
           rk == PRED["cdiff_rows"] and set((int(y["node"]), str(y["sink"]).split("|")[2]) for y in cd["rows"]) == set((int(y["node"]), y["term"]) for y in P["open_rows"]),
           {"extra": sorted(set(rk) - set(PRED["cdiff_rows"])), "missing": sorted(set(PRED["cdiff_rows"]) - set(rk))}, fatal=True)
    h1 = None if DRY else bp.labview_handles(); s.fact("PH handles: post-open {0} -> before-save {1}".format(h0, h1))   # noqa: E702
    s.gate("HB open->save handle growth <= +700 (PD236(b) band; refs balance is H5)", DRY or (h1 is not None and h0 is not None and h1 - h0 <= 700), (h0, h1))
    m = s.save(broken_ok=True) if SAVE else None
    SAVE and s.gate("PS artefact saved, md5 differs from the input; input unchanged", m and m != s.input_md5 and K.md5(s.input_vi) == s.input_md5, m)
    _x = m and m != s.input_md5 and s.work in s.scratches and s.scratches.remove(s.work)   # noqa: F841
    el = PRED["errorlist"]
    if m and not DRY:                                                              # P3b-1's licences + the predicted new items
        ex = dict(J(K.ROOT, el["base_file"]), bed=s.work, bed_md5=m, total=el["predicted_total"], measured_from=None,
                  decided_by="card 129-1 plan prediction (plan_ring_p3b2_pred.json errorlist): P3b-1's {0} + {1} new; "
                             "pin on the scratch run's Error List (PD235(f))".format(el["bed_total"], el["new_items_predicted"]))
        ep = os.path.join(K.BENCH, "errorlist_expected_{0}.json".format(os.path.splitext(os.path.basename(s.work))[0]))
        json.dump(ex, open(ep, "w", encoding="utf-8"), indent=1)
        s.gate("EL errorlist_expected written: total {0} == P3b-1 {1} + predicted new {2}".format(ex["total"], el["bed_total"], el["new_items_predicted"]),
               ex["total"] == el["bed_total"] + el["new_items_predicted"], ep)
    s.R["ring_p3b2"] = {"final": s.work if m else None, "md5": m, "cdiff_rows": rk, "handles": [h0, h1], "census_delta": dc, "frames": on,
                        "errorlist_predicted_total": el["predicted_total"], "level": "STRUCTURAL, broken by design (P3b-1 bed), never run"}; s.dump()   # noqa: E702


if __name__ == "__main__":
    st = K.Stage(BASE["vi"], BASE["md5"], "D1_ring_p3b2", preload=False, deadline_min=45, out_json=os.path.join(K.BENCH, "stage_d1_ring_p3b2.json"), task="card 129-1 RING P3b-2")
    rc = K.run(body, st)
    DRY or SX.kill_labview_at_exit()
    sys.exit(rc)
