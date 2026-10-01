r"""stage_d1_ring_p3b1 - card 129-1 (WRITTEN, NOT LAUNCHED), RING P3b-1 (d1-loop12-17-split-plan.md PD246(c) A1/A2, PD254(d),
PD256(b)(c), PD258(a)(c), PD261(a)(d), PD262(b), PD263(b); cut re-set by docs/d1/ring-p3b.md PD269(a)-(c), card 130-6): on the
SAVED P3a bed D1_ring_p3a_20261001_180540.vi (md5 4dfa44aa) build, in case #22694's False frame 27219, a 3-frame Flat Sequence
whose frame f0 stays EMPTY here (its [Num(i) = -1] group, 9 rows, moved to P3b-2 by the memory cut, PD269(a)(b)) ->
f1 [IMAQ Copy #6810 Image Out -> Img(i), error in <- #6810 error out] -> f2 [Num(i) = status ? -1 : BufNum (Unbundler #157
element#0 -> Select #529 s, I32 -1 -> t, BufNum -> f)]; wire_remove_loose_ends on w27378 and after every crossing. 31 actions
(N 31, BIND 18, R 20, predicted peak 663.4 MB). f0's Num(i)=-1, TransPos/RotPos/FrameIdx and Latest are P3b-2's.
FRESH LabVIEW -> claudeDev\D1_ring_p3b1_<ts>.vi (rule-6 GUI save, ExecState 0 by design: the P3a bed is broken, never run) +
tools\bench\errorlist_expected_D1_ring_p3b1_<ts>.json (54 = P3a's 55 - w27378, + 0 own). ROWS ONLY FROM plan_ring_p3b1.json
(stagesim FINAL of plan_ring_p3b1_in.json, plan_ring_p3b_split.py); expected values only from plan_ring_p3b1_pred.json.
PRIOR ART: stage_d1_ring_p3a.py (Executor/LVBackend/DryPlanBE skeleton, D/TD/FU/PB/HB/PS/EL gates). No new op.
PREDICTION: L1 31 actions -> pred ops; E1 every checkpoint == sim; FS 1 FlatSequence with 3 frames on 27219, terminals per frame ==
the simulator's end state read from the plan's last step (f0 0 / f1 16 / f2 18 at plan 6934a0ed, PD269(c)); RB the Unbundler
terminal on Select.s's wire reads back `status` (PD262(b); FAILS otherwise, UNVERIFIED-DRY in a dry run); D new/lost wires == sim's;
TD every base terminal that was wired stays wired; CEN2 == pred census (CENSUS-UNPREDICTED rows: the scratch run pins them);
PB cdiff(S1, end) == P3a's 16 rows (FATAL, before save); HB handles <= +700; PS saved, input unchanged; EL 54.
    py tools/bgrun.py --material --max-min 50 --log tools/bench/stage_d1_ring_p3b1.log -- py -u tools/recipes/stage_d1_ring_p3b1.py"""
import copy, json, os, sys                                                         # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, vigraph as V, stagexec as SX, jev_candidates as JC   # noqa: E401,E402
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                 # noqa: E731
PLAN = os.path.join(K.BENCH, "plan_ring_p3b1.json")                                 # ONE literal: stage_prerun.plan_files reads it
P = J(PLAN); BASE = J(K.ROOT, P["finalized"]["base"]["path"]); A = P["actions"]   # noqa: E702
PRED = J(K.BENCH, "plan_ring_p3b1_pred.json")
DRY, LAB, SAVE = bool(getattr(g.report_all, "_dry", False)), JC.node_labels_default(), True
SRC = tuple(PRED["census"])
BIND = set(k for k, o in enumerate(SX.compile_plan(P), 1) if o["kind"] in SX.BIND_KINDS)   # card 129-8 PD265(c): every op that creates/binds an object
CHECKPOINTS = tuple(sorted({0, len(SX.compile_plan(P))} | BIND))                  # as stage_d1_l2b3.py:16-18 (stagexec.py:1726-1733 refuses a set missing a bind op)
wires = lambda rows: set(int(r["wire_uid"]) for r in rows if r["wire_uid"])        # noqa: E731
frames = lambda rows: set(int(r["frame_diagram"] or 0) for r in rows)              # noqa: E731
snap = lambda s: dict((u, c) for u, c in s.census_snapshot().items() if c in SRC)   # noqa: E731


def body(s):
    print(__doc__, flush=True)
    s.gate("L0 plan FINAL, open_rows_match, plan_in = plan_ring_p3b1_in; base graph md5 == pred == file; bed md5 == pred; plan end cdiff == pred; pred keyed to this plan",
           P.get("final") is True and P["finalized"].get("open_rows_match") is True and os.path.splitext(P["finalized"]["plan_in"]["path"])[0].endswith("plan_ring_p3b1_in")
           and P["finalized"]["base"]["md5"] == PRED["graph"]["md5"] == K.md5(os.path.join(K.ROOT, P["finalized"]["base"]["path"])) and BASE["md5"] == PRED["bed_md5"]
           and sorted(P["finalized"]["end_cdiff_rows"]) == PRED["cdiff_rows"] and PRED["plan"]["md5"] == K.md5(PLAN), (K.md5(PLAN), P["finalized"]["base"], BASE["md5"]), fatal=True)
    s.start(); s.discard_work(); bp = K.mod("bench_prep"); h0 = bp.labview_handles(); c0 = snap(s)   # noqa: E702
    be = SX.DryPlanBE(s, P, PLAN, BASE) if DRY else SX.LVBackend(s, BASE["fs_tunnel_pairs"], sink_gates=[], gates={}, mem_stop_mb=SX.MEM_STOP_MB)
    x = SX.Executor(PLAN, be, log=lambda m: print(m, flush=True), checkpoints=CHECKPOINTS)
    s.gate("L1 the {0} actions compile into {1} real ops == pred kinds, each action once; checkpoints {2}".format(len(A), len(x.ops), CHECKPOINTS),
           [o["kind"] for o in x.ops] == PRED["ops"] and sorted(n for o in x.ops for n in o["acts"]) == list(range(1, len(A) + 1)), [o["kind"] for o in x.ops], fatal=True)
    try:
        real = x.run(); s.gate("E1 every checkpoint's real graph == its simulated step ({0} ops)".format(len(x.ops)), True)   # noqa: E702
    except SX.ExecStop as e:
        return SX.report_stop(s, x, be, e)
    s.R["stagexec"] = x.report
    L = x.step(len(A))["state"]
    rb = lambda sym: x.bind["obj"].get(L["sym"][sym], x.bind["diag"].get(L["sym"][sym], L["sym"][sym]))   # noqa: E731 - frames: bind['diag']
    term = lambda sym, nm: [r for r in real if r["owner_uid"] == rb(sym) and r["term_name"] == nm]   # noqa: E731
    fs, fr = rb("new:FS1"), [rb("new:FS1.f{0}".format(k)) for k in range(3)]
    fsim = [int(L["sym"]["new:FS1.f{0}".format(k)]) for k in range(3)]             # PD269(c): the simulated end state's frame uids
    nexp = [sum(1 for r in L["terminals"] if int(r["frame_diagram"] or 0) == f) for f in fsim]   # read from the plan's last step, never typed
    nreal = [sum(1 for r in real if int(r["frame_diagram"] or 0) == f) for f in fr]
    s.gate("FS one FlatSequence #{0} with 3 distinct frames {1}; terminals per frame {2} == simulated end state {3} (PD269(c))".format(fs, fr, nreal, nexp),
           len(set(fr)) == 3 and nreal == nexp, {"frames": fr, "real": nreal, "sim": nexp, "sim_uids": fsim}, fatal=True)
    sw = term("new:SEL1", "s")
    ub = [r for r in real if r["owner_uid"] == rb("new:UB1") and r["is_source"] and len(sw) == 1 and sw[0]["wire_uid"] and r["wire_uid"] == sw[0]["wire_uid"]]
    s.gate("RB PD262(b) read-back: the Unbundler terminal on Select.s's wire reads `{0}`, expected `{1}`{2}".format(
           ub[0]["term_name"] if len(ub) == 1 else None, PRED["readback"]["expect_name"], " (UNVERIFIED-DRY)" if DRY else ""),
           len(sw) == 1 and len(ub) == 1 and (DRY or ub[0]["term_name"] == PRED["readback"]["expect_name"]), {"sel_s": sw, "ub": ub})
    sim_new, sim_lost = wires(L["terminals"]) - wires(BASE["terminals"]), wires(BASE["terminals"]) - wires(L["terminals"])
    new, lost = wires(real) - wires(BASE["terminals"]), wires(BASE["terminals"]) - wires(real)
    s.gate("D new wires {0} == sim's {1}; lost {2} == sim's {3} (re-created source nets, PD256(c))".format(len(new), len(sim_new), len(lost), len(sim_lost)),
           len(new) == len(sim_new) and len(lost) == len(sim_lost), {"new": sorted(new), "lost": sorted(lost)[:20]})
    dc = s.census_gate("CEN2 new-object census (classes of the pred) == plan_ring_p3b1_pred.json census", c0, snap(s), PRED["census"])
    bw, rw = dict((int(r["term_uid"]), int(r["wire_uid"] or 0)) for r in BASE["terminals"]), dict((int(r["term_uid"]), int(r["wire_uid"] or 0)) for r in real)
    unw = [t for t, w_ in bw.items() if w_ and not rw.get(t)]
    s.gate("TD every base terminal that was wired is still wired, no base row lost", not unw and not set(bw) - set(rw), {"unwired": unw[:20], "lost_rows": sorted(set(bw) - set(rw))[:20]})
    fu = frames(BASE["terminals"]) | set(f for f, n in zip(fr, nexp) if n)         # PD269(c): only the frames the sim end state fills
    s.gate("FU frame diagrams == base + the FS frames holding terminals in the simulated end state ({0} of 3)".format(sum(1 for n in nexp if n)),
           frames(real) == fu, sorted(fu ^ frames(real))[:20], fatal=True)
    s.es("after all rows (ExecState 0 expected: the P3a bed is broken by design)")
    s1p = J(JC.WIKI, JC.S1_KEY + ".json")
    S1f = V.build4(s1p["terminals"], J(JC._newest("graph_objs_s1_*.json"))["objects"], J(JC._newest("graph_loops_s1_*.json"))["loops"], LAB, s1p["fs_tunnel_pairs"], frame_keyed=True)
    G1 = V.build4(real, getattr(be, "last_objs", None) or be.st["objs"], copy.deepcopy(L["loops"]), LAB, BASE["fs_tunnel_pairs"], frame_keyed=True)
    cd = V.computation_diff_frame(S1f, G1)
    rk = sorted(str(y["sink"]) for y in cd["rows"])
    s.gate("PB frame-keyed cdiff(S1, real end) == the P3a bed's {0} rows and the plan's {1} open (node, term) pairs (FATAL, before save)".format(len(PRED["cdiff_rows"]), len(P["open_rows"])),
           rk == PRED["cdiff_rows"] and set((int(y["node"]), str(y["sink"]).split("|")[2]) for y in cd["rows"]) == set((int(y["node"]), y["term"]) for y in P["open_rows"]),
           {"extra": sorted(set(rk) - set(PRED["cdiff_rows"])), "missing": sorted(set(PRED["cdiff_rows"]) - set(rk))}, fatal=True)
    h1 = None if DRY else bp.labview_handles(); s.fact("PH handles: post-open {0} -> before-save {1}".format(h0, h1))   # noqa: E702
    s.gate("HB open->save handle growth <= +700 (PD236(b) band; refs balance is H5)", DRY or (h1 is not None and h0 is not None and h1 - h0 <= 700), (h0, h1))
    m = s.save(broken_ok=True) if SAVE else None
    SAVE and s.gate("PS artefact saved, md5 differs from the input; input unchanged", m and m != s.input_md5 and K.md5(s.input_vi) == s.input_md5, m)
    _x = m and m != s.input_md5 and s.work in s.scratches and s.scratches.remove(s.work)   # noqa: F841
    el = PRED["errorlist"]
    if m and not DRY:                                                              # P3a's licences - w27378 + the predicted new items
        ex = dict(J(K.ROOT, el["base_file"]), bed=s.work, bed_md5=m, total=el["predicted_total"], measured_from=None,
                  decided_by="card 129-1 plan prediction (plan_ring_p3b1_pred.json errorlist): P3a's {0} - w27378 ({1}) + {2} new; "
                             "pin on the scratch run's Error List (PD235(f))".format(el["bed_total"], sum(el["removed"].values()), el["new_items_predicted"]))
        ep = os.path.join(K.BENCH, "errorlist_expected_{0}.json".format(os.path.splitext(os.path.basename(s.work))[0]))
        json.dump(ex, open(ep, "w", encoding="utf-8"), indent=1)
        s.gate("EL errorlist_expected written: total {0} == P3a {1} - {2} + predicted new {3}".format(ex["total"], el["bed_total"], sum(el["removed"].values()), el["new_items_predicted"]),
               ex["total"] == el["bed_total"] - sum(el["removed"].values()) + el["new_items_predicted"], ep)
    s.R["ring_p3b1"] = {"final": s.work if m else None, "md5": m, "cdiff_rows": rk, "handles": [h0, h1], "census_delta": dc, "fs": fs, "frames": fr,
                        "readback": ub[0]["term_name"] if len(ub) == 1 else None, "errorlist_predicted_total": el["predicted_total"],
                        "level": "STRUCTURAL, broken by design (P3a bed), never run"}; s.dump()   # noqa: E702


if __name__ == "__main__":
    st = K.Stage(BASE["vi"], BASE["md5"], "D1_ring_p3b1", preload=False, deadline_min=45, out_json=os.path.join(K.BENCH, "stage_d1_ring_p3b1.json"), task="card 129-1 RING P3b-1")
    rc = K.run(body, st)
    DRY or SX.kill_labview_at_exit()
    sys.exit(rc)
