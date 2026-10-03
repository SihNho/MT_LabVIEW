r"""stage_d1_ring_p4_s03v18 - card 143-P1 (WRITTEN, NOT LAUNCHED; PROVISIONAL plan - never launched before --rebase), RING P4 LabVIEW
SESSION 3 of plan v18 (PD330(d), PD331(c); D-2026-10-01-01, D-2026-10-02-02/04): on session 2's SAVED in-between file (adopted by card
143-1), apply the actions of plan_ring_p4_s03v18.json = v18 ops 59..78 (20 actions, p4_w_stop12..p4_lr_num_a, up to the X10 cut 676.9
<= 680 at the provisional start 596.5), planned on session 2's simulated end and to be REBASED onto session 2's real graph by stage_prerun
--rebase (then --dry/--prerun again; this .py is unchanged by a rebase).
COPIED from stage_d1_ring_p4_s02v18.py (card 142-5, identity-keyed D / TD) with ONLY names changed (plan, pred, card id, out json, stage
name, docstring); card 143-P2 then ported card 143-1's one recipe change: SX.save_for_resume before SX.report_stop on ExecStop (PD329(b)). FRESH LabVIEW -> claudeDev\D1_ring_p4s03v18_<ts>.vi (rule-6 GUI save, ExecState 0 by design) = an IN-BETWEEN file of
step P4 (not counted, D-2026-10-02-02/04). The FIRST run is the full SCRATCH run on a byte copy (stage_d1_ring_p4_s03v18_scratch.py).
ROWS ONLY FROM plan_ring_p4_s03v18.json; expected values only from plan_ring_p4_s03v18_pred.json. No new op.
PREDICTION (numbers in the pred file): L1 actions -> pred ops; E1 every checkpoint == sim; NG crossing tunnel names == step files';
PRIM every created primitive's label == plan prim; FR created objects on the sim end's frames; D new/lost wires == sim's; TD every base
terminal that was wired stays wired, identities lost == plan deletes; CEN2 == pred census; PB cdiff(S1, end) == pred rows (FATAL, before save); HB handles <= +700;
PS saved, input unchanged. X10 = pred memory_pred. Error List of the end = pred errorlist.predicted_total (PD322(e) per-node rule).
    py tools/bgrun.py --material --max-min 50 --log tools/bench/launch_c143_p4s03v18.log -- py -u tools/recipes/stage_d1_ring_p4_s03v18.py"""
import copy, json, os, sys                                                         # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, vigraph as V, stagexec as SX, jev_candidates as JC   # noqa: E401,E402
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                 # noqa: E731
PLAN = os.path.join(K.BENCH, "plan_ring_p4_s03v18.json")                            # ONE literal: stage_prerun.plan_files reads it
P = J(PLAN); BASE = J(K.ROOT, P["finalized"]["base"]["path"]); A = P["actions"]   # noqa: E702
PRED = J(K.BENCH, "plan_ring_p4_s03v18_pred.json")
NC = sum(1 for a in A if a["op"] == "create" and a.get("as"))                       # created objects, from the plan (FR gate)
DRY, LAB, SAVE = bool(getattr(g.report_all, "_dry", False)), JC.node_labels_default(), True
SRC = tuple(PRED["census"])
BIND = set(k for k, o in enumerate(SX.compile_plan(P), 1) if o["kind"] in SX.BIND_KINDS)   # card 129-8 PD265(c): every op that creates/binds an object
CHECKPOINTS = tuple(sorted({0, len(SX.compile_plan(P))} | BIND))                  # as stage_d1_l2b3.py:16-18 (stagexec refuses a set missing a bind op)
FSPAIRS = BASE.get("fs_tunnel_pairs", BASE.get("fs_pairs"))                         # a real graph / the provisional simulated state
wires = lambda rows: set(int(r["wire_uid"]) for r in rows if r["wire_uid"])        # noqa: E731
frames = lambda rows: set(int(r["frame_diagram"] or 0) for r in rows)              # noqa: E731
snap = lambda s: dict((u, c) for u, c in s.census_snapshot().items() if c in SRC)   # noqa: E731


def body(s):
    print(__doc__, flush=True)
    s.gate("L0 plan FINAL, open_rows_match, plan_in = plan_ring_p4_s03v18_in; base graph md5 == pred == file; bed md5 == pred; plan end cdiff == pred; pred keyed to this plan",
           P.get("final") is True and P["finalized"].get("open_rows_match") is True and os.path.splitext(P["finalized"]["plan_in"]["path"])[0].endswith("plan_ring_p4_s03v18_in")
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
        try:                                                                        # card 143-P2 (PD329(b), prior-art c143-p1 B3; as s02v18.py:47-50): keep ops 1..k-1 for a same-cycle resume
            SX.save_for_resume(s, x, e)
        except Exception as ee:                                                     # noqa: BLE001 - the stop report must still be written
            s.fact("RESUME save failed: {0!r}".format(ee))
        return SX.report_stop(s, x, be, e)
    s.R["stagexec"] = x.report
    s.gate("NG every crossing op's NEW tunnel names == the simulator's (stagexec.tunnel_name_check, per op, from the step files): {0} op(s) {1}".format(
        len(x.name_checks), [c["k"] for c in x.name_checks]), all(c["ok"] for c in x.name_checks), x.name_checks[:6])
    L = x.step(len(A))["state"]
    rb = lambda sym: x.bind["obj"].get(L["sym"][sym], x.bind["diag"].get(L["sym"][sym], L["sym"][sym]))   # noqa: E731
    made = [rb("new:" + a["as"]) for a in A if a["op"] == "create" and a.get("as")]
    on = sorted(set(int(r["frame_diagram"] or 0) for r in real if r["owner_uid"] in made))
    sf = set(int(x.bind["diag"].get(f, f)) for f in frames(L["terminals"]))     # the simulated end's frames, through the diagram binding
    s.gate("FR the {0} created objects sit on {1} frame(s) of the simulated end; real frames == the sim end's".format(len(made), on),
           len(made) == NC and on and set(on) <= sf and frames(real) == sf, {"on": on, "extra": sorted(frames(real) - sf), "missing": sorted(sf - frames(real))}, fatal=True)
    # card 141-3 (PD325(b)): D / TD / unwired keyed by IDENTITY (term uid, owner uid, name) - LabVIEW re-uses deleted uids in-session
    ti = K.term_identity_gates(BASE["terminals"], L["terminals"], real)
    s.gate("D new wires {0} == sim's {1}; lost {2} == sim's {3} (wire uid + source identity, stagekit.wire_keys)".format(
        len(ti["new"]), len(ti["sim_new"]), len(ti["lost_w"]), len(ti["sim_lost_w"])), ti["d_ok"], {"new": ti["new"], "lost": ti["lost_w"][:20]})
    dc = s.census_gate("CEN2 new-object census (classes of the pred) == plan_ring_p4_s03v18_pred.json census", c0, snap(s), PRED["census"])
    s.gate("TD every base terminal the sim keeps wired is still wired; identities lost == the plan's deletes (key uid/owner/name, stagekit.term_identity_gates)",
           ti["td_ok"], {"unwired": ti["unwired"][:20], "lost": ti["lost"][:20], "plan_deletes": ti["gone"][:20], "recycled_uids": ti["recycled"][:20],
                         "raw_lost": ti["raw_lost"][:20]})
    s.R["term_identity"] = ti
    s.R["real_end_rows"] = [[r["term_uid"], r.get("owner_uid"), r.get("term_name"), r.get("wire_uid"), bool(r.get("is_source"))] for r in real]   # review c141-2 s4.2
    s.es("after all rows (ExecState 0 expected: session 2's in-between file is broken by design)")
    s1p = J(JC.WIKI, JC.S1_KEY + ".json")
    S1f = V.build4(s1p["terminals"], J(JC._newest("graph_objs_s1_*.json"))["objects"], J(JC._newest("graph_loops_s1_*.json"))["loops"], LAB, s1p["fs_tunnel_pairs"], frame_keyed=True)
    G1 = V.build4(real, getattr(be, "last_objs", None) or be.st["objs"], copy.deepcopy(L["loops"]), LAB, FSPAIRS, frame_keyed=True)
    cd = V.computation_diff_frame(S1f, G1)
    rk = sorted(str(y["sink"]) for y in cd["rows"])
    s.gate("PB frame-keyed cdiff(S1, real end) == the pred's {0} rows and the plan's {1} open (node, term) pairs (FATAL, before save)".format(len(PRED["cdiff_rows"]), len(P["open_rows"])),
           rk == PRED["cdiff_rows"] and set((int(y["node"]), str(y["sink"]).split("|")[2]) for y in cd["rows"]) == set((int(y["node"]), y["term"]) for y in P["open_rows"]),
           {"extra": sorted(set(rk) - set(PRED["cdiff_rows"])), "missing": sorted(set(PRED["cdiff_rows"]) - set(rk))}, fatal=True)
    h1 = None if DRY else bp.labview_handles(); s.fact("PH handles: post-open {0} -> before-save {1}".format(h0, h1))   # noqa: E702
    s.gate("HB open->save handle growth <= +700 (PD236(b) band; refs balance is H5)", DRY or (h1 is not None and h0 is not None and h1 - h0 <= 700), (h0, h1))
    m = s.save(broken_ok=True) if SAVE else None
    SAVE and s.gate("PS artefact saved, md5 differs from the input; input unchanged", m and m != s.input_md5 and K.md5(s.input_vi) == s.input_md5, m)
    _x = m and m != s.input_md5 and s.work in s.scratches and s.scratches.remove(s.work)   # noqa: F841
    el = PRED["errorlist"]                                                          # in-between file: checked False, no EL file written
    s.R["ring_p4_s03v18"] = {"final": s.work if m else None, "md5": m, "cdiff_rows": rk, "handles": [h0, h1], "census_delta": dc, "frames": on,
                             "errorlist_predicted_total": el["predicted_total"], "errorlist_alternative_total": el["alternative_total"],
                             "level": "STRUCTURAL, in-between file of P4 (v18 session 3), broken by design, never run"}; s.dump()   # noqa: E702


if __name__ == "__main__":
    st = K.Stage(BASE["vi"], BASE["md5"], "D1_ring_p4s03v18", preload=False, deadline_min=45, out_json=os.path.join(K.BENCH, "launch_c143_p4s03v18.json"), task="card 143-P1 RING P4 v18 session 3")
    rc = K.run(body, st)
    DRY or SX.kill_labview_at_exit()
    sys.exit(rc)
