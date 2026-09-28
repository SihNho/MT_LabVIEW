r"""stage_d1_qrt_pool - card 119-2 (offline prep; run by the next launch card), STAGE QRT POOL (d1-loop12-17-split-plan.md PD234(a)-(k)). INPUT the
SAVED R2 bed D1_l2_r2_20260928_110756.vi, FRESH LabVIEW -> claudeDev\D1_qrt_pool_<ts>.vi (rule-6 GUI save, ExecState 0 by design, never run).
ROWS ONLY FROM plan_qrt_pool.json (stagesim FINAL of plan_qrt_pool_in.json); expected values only from plan_qrt_pool_pred.json.
PRIOR ART (checked before writing): stage_d1_l2a3.py / stage_d1_l2r2.py (Executor + DryPlanBE, PB cdiff, save); diag_c118_p1b.py (the pool's
creates, 8/9 landed on an R2 copy, diag_c118_p1b_r2.log:30-44); gscript.read_const_value (118-4, gscript.py:4226); diag_c118_p0.read_num (I32);
LVBackend.index_mode_fix (stagexec.py:2154-2163). No new op. Executor.run calls index_mode_fix for a tunnel op only inside `if lost:`
(stagexec.py:1559-1563), so gate TI calls it here with the plan's `indexing`.
PREDICTION: L1 15 actions -> 13 ops == pred; E1 every checkpoint == sim; TI names tunnel IndexMode 1; NV names == Cam_pool00..19; RV ring dup
value+type == #13245's; MX I32 == 20; D new wires == sim, none lost; TD base terminals keep their wires, only w14741 gains the 2 Obtain sinks;
FU base frames kept + ONE new body; PB cdiff(S1, end) == R2's 16 rows (FATAL, before save); PS saved, input unchanged.
    py tools/bgrun.py --material --max-min 45 --log tools/bench/stage_d1_qrt_pool.log -- py -u tools/recipes/stage_d1_qrt_pool.py"""
import copy, json, os, sys                                                         # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, vigraph as V, stagexec as SX, jev_candidates as JC   # noqa: E401,E402
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                 # noqa: E731
PLAN = os.path.join(K.BENCH, "plan_qrt_pool.json")                                  # ONE literal: stage_prerun.plan_files reads it
P = J(PLAN); BASE = J(K.ROOT, P["finalized"]["base"]["path"]); A = P["actions"]   # noqa: E702
PRED = J(K.BENCH, "plan_qrt_pool_pred.json")
DRY, LAB = bool(getattr(g.report_all, "_dry", False)), JC.node_labels_default()
TUN = next(a for a in A if a["op"] == "tunnel"); BY = dict((a["as"], a) for a in A if a.get("as"))   # noqa: E702
R2END = J(K.BENCH, "stage_d1_l2r2.json")["l2r2"]["cdiff_rows"]                      # the REAL R2 end's cdiff sinks
NET = PRED["existing_net_change"]
wires = lambda rows: set(int(r["wire_uid"]) for r in rows if r["wire_uid"])        # noqa: E731
frames = lambda rows: set(int(r["frame_diagram"] or 0) for r in rows)              # noqa: E731
nodry = lambda gid, why: print("GATE {0} NOT RUNNABLE IN DRY: {1}".format(gid, why), flush=True)   # noqa: E731


def body(s):
    print(__doc__, flush=True)
    s.gate("L0 plan FINAL, open_rows_match, plan_in = plan_qrt_pool_in; base graph md5 == pred == file; bed md5 == pred",
           P.get("final") is True and P["finalized"].get("open_rows_match") is True and os.path.splitext(P["finalized"]["plan_in"]["path"])[0].endswith("plan_qrt_pool_in")
           and P["finalized"]["base"]["md5"] == PRED["graph"]["md5"] == K.md5(os.path.join(K.ROOT, P["finalized"]["base"]["path"])) and BASE["md5"] == PRED["bed_md5"],
           (K.md5(PLAN), P["finalized"]["base"], BASE["md5"]), fatal=True)
    s.start(); s.discard_work(); bp = K.mod("bench_prep"); h0 = bp.labview_handles()   # noqa: E702
    be = SX.DryPlanBE(s, P, PLAN, BASE) if DRY else SX.LVBackend(s, BASE["fs_tunnel_pairs"], sink_gates=[], gates={}, mem_stop_mb=SX.MEM_STOP_MB)
    x = SX.Executor(PLAN, be, log=lambda m: print(m, flush=True))
    s.gate("L1 the {0} actions compile into {1} real ops == pred kinds, each action once".format(len(A), len(x.ops)),
           [o["kind"] for o in x.ops] == PRED["ops"] and sorted(n for o in x.ops for n in o["acts"]) == list(range(1, len(A) + 1)), [o["kind"] for o in x.ops], fatal=True)
    try:
        real = x.run(); s.gate("E1 every checkpoint's real graph == its simulated step ({0} ops)".format(len(x.ops)), True)   # noqa: E702
    except SX.ExecStop as e:
        return SX.report_stop(s, x, be, e)
    s.R["stagexec"] = x.report; s.fact("BINDING obj {0} term {1}".format(x.bind["obj"], x.bind["term"]))   # noqa: E702
    L = x.step(len(A))["state"]; ob = x.bind["obj"]; W = s.work                     # noqa: E702
    R = lambda a: ob.get(L["sym"]["new:" + a], L["sym"]["new:" + a])               # noqa: E731  sim alias -> real uid
    im, e_ = s.safe("TI index_mode_fix", lambda: be.index_mode_fix(R(TUN["as"]), bool(TUN["indexing"])), None)
    s.gate("TI names tunnel #{0} IndexMode == 1 (plan indexing {1}), set + read back by index_mode_fix".format(R(TUN["as"]), TUN["indexing"]), im == 1 and not e_, (im, e_), fatal=True)
    if DRY:
        nodry("NV/RV/MX", "read_const_value / read_num read the live constants (Constant.Value on a COM ref)")
    else:
        nv = g.read_const_value(W, R("NM1"))
        s.gate("NV names constant #{0} == Cam_pool00..19 (read_const_value), all distinct, none == 'Cam'".format(R("NM1")),
               list(nv.get("value") or []) == PRED["names"] and len(set(PRED["names"])) == 20 and "Cam" not in PRED["names"] and not nv.get("err"), nv)
        r0, r1 = g.read_const_value(W, PRED["ring_ref"]), g.read_const_value(W, R("RG1"))
        s.gate("RV ring dup #{0} value+type == #{1}'s ({2!r}, {3!r})".format(R("RG1"), PRED["ring_ref"], r0.get("value"), r0.get("type")),
               r0.get("cls") == r1.get("cls") == "RingConstant" and (r0.get("value"), r0.get("type")) == (r1.get("value"), r1.get("type")) and not r0.get("err") and not r1.get("err"), (r0, r1))
        _RD = g._run.__defaults__; P0M = K.mod("diag_c118_p0"); g._run.__defaults__ = _RD   # noqa: E702  (diag_c118_p1b.py:24)
        mx = (P0M.read_num(W, R("C20")).get("DigitalNumericConstant") or {})
        s.gate("MX I32 #{0} == {1} (read_num text {2!r})".format(R("C20"), PRED["max_size"], mx.get("text")), str(mx.get("text")).strip() == str(PRED["max_size"]) and not mx.get("err"), mx)
    sim_new, sim_lost = wires(L["terminals"]) - wires(BASE["terminals"]), wires(BASE["terminals"]) - wires(L["terminals"])
    new, lost = wires(real) - wires(BASE["terminals"]), wires(BASE["terminals"]) - wires(real)
    s.gate("D the end adds the simulated {0} new wire(s) and loses none".format(len(sim_new)), len(new) == len(sim_new) and not lost and not sim_lost,
           {"new": sorted(new), "lost": sorted(lost)[:20]})
    bw, rw = dict((int(r["term_uid"]), int(r["wire_uid"] or 0)) for r in BASE["terminals"]), dict((int(r["term_uid"]), int(r["wire_uid"] or 0)) for r in real)
    chg = [(t, w, rw.get(t)) for t, w in bw.items() if rw.get(t) != w]
    gain = sorted((int(r["owner_uid"]), r["term_name"]) for r in real if int(r["wire_uid"] or 0) == NET["wire"] and int(r["term_uid"]) not in bw)
    want = sorted((R(q.split(".")[0]), q.split(".", 1)[1]) for q in NET["gains"])
    s.gate("TD every base terminal keeps its wire uid; only w{0} gains {1}".format(NET["wire"], NET["gains"]), not chg and gain == want, {"changed": chg[:20], "gain": gain, "want": want})
    body_ = x.bind["diag"].get(L["sym"]["new:PF1.body"], L["sym"]["new:PF1.body"])
    s.gate("FU base frame diagrams all kept; exactly ONE new frame = the For body #{0}".format(body_), frames(BASE["terminals"]) <= frames(real)
           and frames(real) - frames(BASE["terminals"]) == {body_}, sorted(frames(BASE["terminals"]) ^ frames(real))[:20], fatal=True)
    s.es("after all rows (ExecState 0 expected: R2 is broken by design)")
    loops = copy.deepcopy(L["loops"])
    for lp in loops or []:                                                          # register table = the simulation's, via the binding (stage_d1_l2a3.py:79-80)
        lp["loop_uid"] = ob.get(int(lp["loop_uid"]), int(lp["loop_uid"])) if "loop_uid" in lp else lp.get("loop_uid")
    s1p = J(JC.WIKI, JC.S1_KEY + ".json")
    S1f = V.build4(s1p["terminals"], J(JC._newest("graph_objs_s1_*.json"))["objects"], J(JC._newest("graph_loops_s1_*.json"))["loops"], LAB, s1p["fs_tunnel_pairs"], frame_keyed=True)
    G1 = V.build4(real, getattr(be, "last_objs", None) or be.st["objs"], loops, LAB, BASE["fs_tunnel_pairs"], frame_keyed=True)
    cd = V.computation_diff_frame(S1f, G1)
    rk = sorted(str(y["sink"]) for y in cd["rows"])
    s.fact("CDIFF added computation nodes {0}".format([(y["node"], y["class"]) for y in cd["computation_nodes_added"]][:20]))
    s.gate("PB frame-keyed cdiff(S1, real end) == R2's {0} rows and the plan's {1} open (node, term) pairs (FATAL, before save)".format(len(R2END), len(P["open_rows"])),
           rk == sorted(R2END) and set((int(y["node"]), str(y["sink"]).split("|")[2]) for y in cd["rows"]) == set((int(y["node"]), y["term"]) for y in P["open_rows"]),
           {"extra": sorted(set(rk) - set(R2END)), "missing": sorted(set(R2END) - set(rk))}, fatal=True)
    s.census(tag="after QRT POOL")
    h1 = None if DRY else bp.labview_handles(); s.fact("PH handles RECORDED: post-open {0} -> before-save {1}".format(h0, h1))   # noqa: E702
    m = s.save(broken_ok=True)
    s.gate("PS artefact saved, md5 differs from the input; input unchanged", m and m != s.input_md5 and K.md5(s.input_vi) == s.input_md5, m)
    _x = m and m != s.input_md5 and s.work in s.scratches and s.scratches.remove(s.work)   # noqa: F841
    s.R["qrt_pool"] = {"final": s.work if m else None, "md5": m, "cdiff_rows": rk, "handles": [h0, h1], "errorlist_predicted_new": PRED["errorlist"]["new_items_predicted"],
                       "level": "STRUCTURAL, broken by design (R2), never run"}; s.dump()   # noqa: E702


if __name__ == "__main__":
    st = K.Stage(BASE["vi"], BASE["md5"], "D1_qrt_pool", preload=False, deadline_min=40, out_json=os.path.join(K.BENCH, "stage_d1_qrt_pool.json"), task="QRT POOL (card 119-2 prep)")
    rc = K.run(body, st)
    DRY or SX.kill_labview_at_exit()
    sys.exit(rc)
