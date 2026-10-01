r"""stage_d1_ring_p2b - card 122-6, RING P2b (d1-loop12-17-split-plan.md PD240(a)-(e), PD241(b), PD244(a)-(d)): on the SAVED P2a bed
D1_ring_p2a_20260928_191739.vi ADD five indicators Num I32[20] / TransPos DBL[20] / RotPos DBL[20] / FrameIdx I32[20] / Latest I32, each born on a
VALUED donor constant (claudeDev\DonorRingConst_v0.vi: Num/FrameIdx -1 x20, TransPos/RotPos 0.0 x20, Latest -1) on FS1 frame #4866 (the frame
before #686), outside every loop; NO existing net touched. FRESH LabVIEW -> claudeDev\D1_ring_p2b_<ts>.vi (rule-6 GUI save, ExecState 0 by
design, never run). ROWS ONLY FROM plan_ring_p2b.json (stagesim FINAL of plan_ring_p2b_in.json, plan_ring_p2b_make.py); expected values only from
plan_ring_p2b_pred.json. PRIOR ART: stage_d1_ring_p2a.py (Executor/LVBackend/DryPlanBE, D/TD/FU/PB/HB/PS gates, save) + diag_c122_route.py
verify() (per-label read-back: panel_wiring label/wire, read_term_type canon, read_const_value, frame) + stagexec const_born_on route
(create_primitive_nested const_donor -> create_indicator_on_const = gscript.const_indicator_on_diagram's two calls). No new op.
Review archive/peer/2026-10-01-c122-route-s0.md: NO owner_of call on #4866; placement is gated by the live read (gate F, FATAL).
PREDICTION: L1 10 actions -> 10 create ops; E1 every checkpoint == sim; per label: ONE new indicator (panel label exact, wired), ONE new constant
on the same wire, both on #4866 (F), canon == pred on both ends (T), constant value == pred (V); D new wires == 5 == sim, none lost;
CEN2 ControlTerminal +5, Wire +5, ArrayConstant +4, DigitalNumericConstant +1, LoopTunnel/WhileLoop/Diagram/SubVI/Local 0; TD every base
terminal keeps its wire, rows added == the 10 new; FU frames unchanged; PB cdiff(S1, end) == the P2a bed's 16 rows (FATAL, before save);
HB open->save handles <= +700 (PD236(b)); PS saved, input unchanged.
    py tools/bgrun.py --material --max-min 45 --log tools/bench/stage_d1_ring_p2b.log -- py -u tools/recipes/stage_d1_ring_p2b.py"""
import copy, json, os, sys                                                         # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, vigraph as V, stagexec as SX, jev_candidates as JC   # noqa: E401,E402
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                 # noqa: E731
PLAN = os.path.join(K.BENCH, "plan_ring_p2b.json")                                  # ONE literal: stage_prerun.plan_files reads it
P = J(PLAN); BASE = J(K.ROOT, P["finalized"]["base"]["path"]); A = P["actions"]   # noqa: E702
PRED = J(K.BENCH, "plan_ring_p2b_pred.json")
DRY, LAB, SAVE = bool(getattr(g.report_all, "_dry", False)), JC.node_labels_default(), True
FRAME = int(PRED["frame"])
P2AEND = J(K.BENCH, "stage_d1_ring_p2a.json")["ring_p2a"]["cdiff_rows"]            # the REAL P2a-bed end's cdiff sinks
SRC = ("LoopTunnel", "Wire", "WhileLoop", "Diagram", "SubVI", "Local", "ControlTerminal", "ArrayConstant", "DigitalNumericConstant")
wires = lambda rows: set(int(r["wire_uid"]) for r in rows if r["wire_uid"])        # noqa: E731
frames = lambda rows: set(int(r["frame_diagram"] or 0) for r in rows)              # noqa: E731
CONSTS = ("ArrayConstant", "DigitalNumericConstant")


def same(a, b):
    try:
        if isinstance(b, list):
            return a is not None and len(list(a)) == len(b) and all(float(x) == float(y) for x, y in zip(list(a), b))
        return a is not None and float(a) == float(b)
    except (TypeError, ValueError):
        return False


def body(s):
    print(__doc__, flush=True)
    s.gate("L0 plan FINAL, open_rows_match, plan_in = plan_ring_p2b_in; base graph md5 == pred == file; bed md5 == pred; plan end cdiff == the P2a bed's rows",
           P.get("final") is True and P["finalized"].get("open_rows_match") is True and os.path.splitext(P["finalized"]["plan_in"]["path"])[0].endswith("plan_ring_p2b_in")
           and P["finalized"]["base"]["md5"] == PRED["graph"]["md5"] == K.md5(os.path.join(K.ROOT, P["finalized"]["base"]["path"])) and BASE["md5"] == PRED["bed_md5"]
           and sorted(P["finalized"]["end_cdiff_rows"]) == sorted(P2AEND) == PRED["cdiff_rows"], (K.md5(PLAN), P["finalized"]["base"], BASE["md5"]), fatal=True)
    labs = [a["label"] for a in A if a.get("class") == "ControlTerminal"]
    s.gate("L0c 10 create rows on #{0}: 5 constants (donor {1}, md5 pinned) + 5 indicators labelled == pred".format(FRAME, os.path.basename(PRED["donor"]["path"])),
           len(A) == 10 and all(a["op"] == "create" and int(a["diagram"]) == FRAME for a in A) and labs == [r["label"] for r in PRED["rows"]]
           and K.md5(PRED["donor"]["path"]) == PRED["donor"]["md5"], {"labels": labs}, fatal=True)
    s.start(); s.discard_work(); bp = K.mod("bench_prep"); h0 = bp.labview_handles(); c0 = s.census(SRC, tag="before P2b")   # noqa: E702
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
    bt = set(int(r["term_uid"]) for r in BASE["terminals"])
    newr = [r for r in real if int(r["term_uid"]) not in bt]
    sim_new = wires(L["terminals"]) - wires(BASE["terminals"])
    new, lost = wires(real) - wires(BASE["terminals"]), wires(BASE["terminals"]) - wires(real)
    s.gate("D new wires == {0} == sim's count, none lost".format(len(PRED["rows"])), len(new) == len(sim_new) == len(PRED["rows"]) and not lost,
           {"new": sorted(new), "sim_new": sorted(sim_new), "lost": sorted(lost)[:20]})
    W, pw = s.work, ([] if DRY else g.panel_wiring(s.work))
    ok_f, per = True, {}
    for row in PRED["rows"]:
        lab = row["label"]
        it = [r for r in newr if r.get("term_class") == "ControlTerminal" and r["term_name"] == lab]
        w = int(it[0]["wire_uid"] or 0) if len(it) == 1 else -1
        ct = [r for r in newr if r["owner_class"] in CONSTS and int(r["wire_uid"] or 0) == w and w > 0]
        pl = [p for p in pw if p["label"] == lab]
        f_ok = len(it) == 1 and len(ct) == 1 and not it[0]["is_source"] and ct[0]["is_source"] and ct[0]["owner_class"] == row["class"] \
            and int(it[0]["frame_diagram"] or 0) == FRAME and int(ct[0]["frame_diagram"] or 0) == FRAME
        ok_f = ok_f and f_ok
        s.gate("G {0}: ONE new indicator terminal (sink) + ONE new {1} (source) on ONE new wire, both on #{2}".format(lab, row["class"], FRAME), f_ok, (it, ct))
        if DRY or not f_ok:
            per[lab] = {"ind": it, "const": ct}
            continue
        s.gate("P {0}: panel object label exact, indicator, wired to that wire".format(lab), len(pl) == 1 and pl[0]["indicator"] and int(pl[0]["wire"] or 0) == w, pl)
        ty = [(s.safe("type #{0}".format(u), lambda u=u: g.read_term_type(W, u))[0] or {}).get("types", {}).get("canon")
              for u in (int(ct[0]["term_uid"]), int(it[0]["term_uid"]))]
        s.gate("T {0}: read_term_type canon == {1} on the constant and the indicator terminal".format(lab, row["canon"]), ty == [row["canon"]] * 2, ty)
        cv = s.safe("value #{0}".format(ct[0]["owner_uid"]), lambda: g.read_const_value(W, int(ct[0]["owner_uid"])))[0] or {}
        s.gate("V {0}: constant #{1} value == {2}".format(lab, ct[0]["owner_uid"], (row["value"][:2] + ["..."]) if isinstance(row["value"], list) else row["value"]),
               not cv.get("err") and same(cv.get("value"), row["value"]), {"value": str(cv.get("value"))[:200], "err": cv.get("err")})
        per[lab] = {"ind_term": int(it[0]["term_uid"]), "panel_uid": int(pl[0]["uid"]) if pl else None, "const": int(ct[0]["owner_uid"]),
                    "const_term": int(ct[0]["term_uid"]), "wire": w, "canon": ty, "value": str(cv.get("value"))[:200]}
    s.gate("F every new indicator and constant terminal reads frame_diagram == #{0} (FATAL; review c122-route-s0 (c))".format(FRAME), ok_f,
           sorted(set((r["owner_class"], int(r["frame_diagram"] or 0)) for r in newr)), fatal=True)
    c1 = s.census(SRC, tag="after P2b")
    dc = dict((k, (c1.get(k) or 0) - (c0.get(k) or 0)) for k in SRC)
    s.fact("CENSUS DELTA {0}".format(dc))
    exp = dict((k, PRED["census"].get(k, 0)) for k in SRC)
    s.gate("CEN2 class census == {0}".format(exp), DRY or dc == exp, dc)
    bw, rw = dict((int(r["term_uid"]), int(r["wire_uid"] or 0)) for r in BASE["terminals"]), dict((int(r["term_uid"]), int(r["wire_uid"] or 0)) for r in real)
    chg = [(t, w_, rw.get(t)) for t, w_ in bw.items() if rw.get(t) != w_]
    s.gate("TD every base terminal keeps its wire; rows added == the {0} new (5 constants + 5 indicators)".format(2 * len(PRED["rows"])),
           not chg and not set(bw) - set(rw) and len(newr) == 2 * len(PRED["rows"]), {"changed": chg[:20], "lost_rows": sorted(set(bw) - set(rw))[:20], "added": len(newr)})
    s.gate("FU the set of frame diagrams is unchanged", frames(BASE["terminals"]) == frames(real), sorted(frames(BASE["terminals"]) ^ frames(real))[:20], fatal=True)
    s.es("after all rows (ExecState 0 expected: the P2a bed is broken by design)")
    s1p = J(JC.WIKI, JC.S1_KEY + ".json")
    S1f = V.build4(s1p["terminals"], J(JC._newest("graph_objs_s1_*.json"))["objects"], J(JC._newest("graph_loops_s1_*.json"))["loops"], LAB, s1p["fs_tunnel_pairs"], frame_keyed=True)
    G1 = V.build4(real, getattr(be, "last_objs", None) or be.st["objs"], copy.deepcopy(L["loops"]), LAB, BASE["fs_tunnel_pairs"], frame_keyed=True)
    cd = V.computation_diff_frame(S1f, G1)
    rk = sorted(str(y["sink"]) for y in cd["rows"])
    s.gate("PB frame-keyed cdiff(S1, real end) == the P2a bed's {0} rows and the plan's {1} open (node, term) pairs (FATAL, before save)".format(len(P2AEND), len(P["open_rows"])),
           rk == sorted(P2AEND) and set((int(y["node"]), str(y["sink"]).split("|")[2]) for y in cd["rows"]) == set((int(y["node"]), y["term"]) for y in P["open_rows"]),
           {"extra": sorted(set(rk) - set(P2AEND)), "missing": sorted(set(P2AEND) - set(rk))}, fatal=True)
    h1 = None if DRY else bp.labview_handles(); s.fact("PH handles: post-open {0} -> before-save {1}".format(h0, h1))   # noqa: E702
    s.gate("HB open->save handle growth <= +700 (PD236(b) band; refs balance is H5)", DRY or (h1 is not None and h0 is not None and h1 - h0 <= 700), (h0, h1))
    m = s.save(broken_ok=True) if SAVE else None
    SAVE and s.gate("PS artefact saved, md5 differs from the input; input unchanged", m and m != s.input_md5 and K.md5(s.input_vi) == s.input_md5, m)
    _x = m and m != s.input_md5 and s.work in s.scratches and s.scratches.remove(s.work)   # noqa: F841
    s.R["ring_p2b"] = {"final": s.work if m else None, "md5": m, "cdiff_rows": rk, "handles": [h0, h1], "census_delta": dc, "objects": per,
                       "errorlist_predicted_new": PRED["errorlist"]["new_items_predicted"], "level": "STRUCTURAL, broken by design (P2a bed), never run"}; s.dump()   # noqa: E702


if __name__ == "__main__":
    st = K.Stage(BASE["vi"], BASE["md5"], "D1_ring_p2b", preload=False, deadline_min=40, out_json=os.path.join(K.BENCH, "stage_d1_ring_p2b.json"), task="card 122-6 RING P2b")
    rc = K.run(body, st)
    DRY or SX.kill_labview_at_exit()
    sys.exit(rc)
