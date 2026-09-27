r"""stage_d1_l2a3 - card 108-2, STAGE L2-A3 (docs/d1-loop12-17-split-plan.md PD221(d); split page tools/bench/cards/split_plan_108_l2a3.md).
INPUT the L2-A2 file claudeDev\D1_l2_a2_20260927_132125.vi (named by the plan's base graph), FRESH LabVIEW -> claudeDev\D1_l2_a3_<ts>.vi
(rule-6 GUI save at ExecState 0 - the plan's 6 open rows stay open by design, never run).
ROWS ONLY FROM THE FINALIZED PLAN tools/bench/plan_l2a3.json (plan_in plan_l2a3_in.json, base graph_l2a2_20260927.json); no uid and no
terminal name or label is typed here; the created indicators and Locals are found through the plan's own `create` rows + the binding.
CARRIER (PD221(d), CLAUDE.md 1c''): 2 hidden indicators in the 1.2 body + 2 Local READS in the 1.1 body; no queue, no edge detection.
PRIOR ART: stage_d1_l2a2.py (the skeleton: DryBE, 179(b) CT reader, PB frame-keyed cdiff, RBW on a scratch of the saved file),
stage_d1_disp.py / plan_disp.json r5_ind_* + r6_lr_* (the create indicator born_on + create Local read routes, stagexec CREATE_ROUTES
'indicator' + 'local_read'). No new op.
PREDICTION: L1 each plan action -> exactly one real op; E1 every checkpoint read == its simulated step; CT the 179(b) reader on each
created indicator: real wire partners == simulated; LB each new label on exactly 1 ControlTerminal and exactly 1 Local; D the end adds the
plan's new wires and loses exactly the base wires the simulation loses; FU the set of frame diagrams is unchanged; PB frame-keyed cdiff(S1,
end) == the plan's open_rows (FATAL, before save); ES recorded (0 by design); PS saved, md5 != input, input unchanged; RBW on a scratch of
the saved file deletes no wire of a re-wired sink; LabVIEW gone at exit.
    py tools/bgrun.py --material --max-min 40 --log tools/bench/stage_d1_l2a3.log -- py -u tools/recipes/stage_d1_l2a3.py"""
import copy, json, os, sys                                                         # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, vigraph as V, stagexec as SX, jev_candidates as JC, allterms as AT  # noqa: E401,E402
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                 # noqa: E731
PLAN = os.path.join(K.BENCH, "plan_l2a3.json")                                      # ONE literal: stage_prerun.plan_files reads it
P = J(PLAN); BASE = J(K.ROOT, P["finalized"]["base"]["path"]); A = P["actions"]   # noqa: E702
DRY, LAB = bool(getattr(g.report_all, "_dry", False)), JC.node_labels_default()
IND = [a for a in A if a["op"] == "create" and a["class"] == "ControlTerminal" and a.get("indicator")]   # from the plan
LOC = [a for a in A if a["op"] == "create" and a["class"] == "Local"]
wires = lambda rows: set(int(r["wire_uid"]) for r in rows if r["wire_uid"])        # noqa: E731
frames = lambda rows: set(int(r["frame_diagram"] or 0) for r in rows)              # noqa: E731


def body(s):
    print(__doc__, flush=True)
    s.gate("L0 the executed plan is FINAL, open_rows_match, plan_in = the plan_l2a3_in stageplan", P.get("final") is True and   # no .json literal:
           P["finalized"].get("open_rows_match") is True and os.path.splitext(P["finalized"]["plan_in"]["path"])[0].endswith("plan_l2a3_in"),  # plan_files (X2)
           (K.md5(PLAN), P["finalized"]["plan_in"]), fatal=True)
    s.start(); s.discard_work(); bp = K.mod("bench_prep"); h0 = bp.labview_handles()   # noqa: E702
    ex, last = {}, lambda: ex["x"].step(len(A))["state"]

    def ct_read(sim_uid, tag, rows=None):                                          # 179(b): the panel-terminal reader
        if DRY:
            return True, "dry"
        b = ex["x"].bind["term"]; real_uid = b.get(sim_uid, sim_uid)               # noqa: E702
        rows = rows or AT.read_terms(s.work, AT.OP_ALLTERMS_V1)[0]
        cts = set(int(o["uid"]) for o in g.report_all(s.work, "ControlTerminal"))
        sim = [r for r in last()["terminals"] if r["term_uid"] == sim_uid]; sw = sim[0]["wire_uid"] if sim else 0   # noqa: E702
        want = sorted(b.get(r["term_uid"], r["term_uid"]) for r in last()["terminals"] if sw and r["wire_uid"] == sw and r["term_uid"] != sim_uid)
        hit = [r for r in rows if r["term_uid"] == real_uid]
        got = sorted(r["term_uid"] for r in rows if hit and hit[0]["wire_uid"] and r["wire_uid"] == hit[0]["wire_uid"] and r["term_uid"] != real_uid)
        s.fact("CT {0} sim #{1} real #{2}: ControlTerminal {3} rows {4} partners real {5} sim {6}".format(tag, sim_uid, real_uid, real_uid in cts, len(hit), got, want))
        return real_uid in cts and len(hit) == 1 and bool(got) and got == want, {"real": got, "sim": want, "rows": len(hit)}
    be = SX.DryPlanBE(s, P, PLAN, BASE) if DRY else SX.LVBackend(s, BASE["fs_tunnel_pairs"], sink_gates=[], gates={}, mem_stop_mb=SX.MEM_STOP_MB)
    x = ex["x"] = SX.Executor(PLAN, be, log=lambda m: print(m, flush=True))
    OPS = [dict(o, id=A[o["acts"][0] - 1]["id"]) for o in x.ops]; acts = sorted(n for o in OPS for n in o["acts"])   # noqa: E702
    s.gate("L1 every plan action compiled into exactly one real op ({0} -> {1})".format(len(A), len(OPS)),
           acts == list(range(1, len(A) + 1)) and len(OPS) == len(A), acts, fatal=True)
    try:
        real = x.run(); s.gate("E1 every checkpoint's real graph == its simulated step ({0} ops)".format(len(OPS)), True)   # noqa: E702
    except SX.ExecStop as e:
        return SX.report_stop(s, x, be, e)
    s.R["stagexec"] = x.report; s.fact("BINDING obj {0} term {1}".format(x.bind["obj"], x.bind["term"]))   # noqa: E702
    DRY or s.fact("METER SUMMARY {0}".format(json.dumps(be.meter.summary(), default=str)))
    L = last()
    rows = None if DRY else AT.read_terms(s.work, AT.OP_ALLTERMS_V1)[0]
    for a in IND:
        ok, d = ct_read(L["sym"]["new:" + a["as"]], "row " + a["id"], rows)
        s.gate("CT {0}: created indicator read by the 179(b) reader == simulated end".format(a["id"]), ok, d)
    for a in ([] if DRY else IND + LOC):
        n_ct = sum(1 for r in rows if r["term_class"] == "ControlTerminal" and r["term_name"] == a["label"])
        n_lo = sum(1 for r in rows if r["owner_class"] == "Local" and r["term_name"] == a["label"])
        s.gate("LB {0}: label {1!r} on exactly 1 ControlTerminal and 1 Local".format(a["id"], a["label"]), n_ct == 1 and n_lo == 1, (n_ct, n_lo))
    sim_new, sim_lost = wires(L["terminals"]) - wires(BASE["terminals"]), wires(BASE["terminals"]) - wires(L["terminals"])
    new, lost = wires(real) - wires(BASE["terminals"]), wires(BASE["terminals"]) - wires(real)
    s.gate("D the end adds the plan's {0} new wire(s) and loses exactly the simulated base wires {1}".format(len(sim_new), sorted(sim_lost)),
           len(new) == len(sim_new) and lost == sim_lost, {"new": sorted(new), "lost": sorted(lost)[:20]})
    s.gate("FU the set of frame diagrams is unchanged", frames(BASE["terminals"]) == frames(real),
           (sorted(frames(BASE["terminals"]) ^ frames(real))[:20]), fatal=True)
    s.es("after all rows (warm, RECORDED - the plan's open rows stay open by design)")
    loops, ob = copy.deepcopy(L["loops"]), x.bind["obj"]
    for lp in loops or []:                                                          # register table = the simulation's, via the binding
        lp["right_uids"], lp["left_of"] = [ob.get(int(u), int(u)) for u in lp.get("right_uids") or []], dict((str(ob.get(int(k), int(k))), [ob.get(int(y), int(y)) for y in (v if isinstance(v, list) else [v])]) for k, v in (lp.get("left_of") or {}).items())
    s1p = J(JC.WIKI, JC.S1_KEY + ".json")
    S1f = V.build4(s1p["terminals"], J(JC._newest("graph_objs_s1_*.json"))["objects"], J(JC._newest("graph_loops_s1_*.json"))["loops"], LAB, s1p["fs_tunnel_pairs"], frame_keyed=True)
    G1 = V.build4(real, getattr(be, "last_objs", None) or be.st["objs"], loops, LAB, BASE["fs_tunnel_pairs"], frame_keyed=True)
    cd = V.computation_diff_frame(S1f, G1)
    for y in cd["rows"]: s.fact("CDIFF ROW {0}".format(dict((k, V.show(v) if k == "sink" else v) for k, v in y.items())))  # noqa: E701
    got = sorted(set((int(y["node"]), str(y["sink"]).split("|")[2]) for y in cd["rows"]))
    want = sorted(set((int(y["node"]), y["term"]) for y in P["open_rows"]))
    s.gate("PB frame-keyed cdiff(S1, real end) == the plan's {0} open_rows (FATAL, before save)".format(len(want)), got == want,
           {"extra": sorted(set(got) - set(want)), "missing": sorted(set(want) - set(got))}, fatal=True)
    s.census(tag="after L2-A3")
    h1 = bp.labview_handles(); s.fact("PH handles RECORDED: post-open {0} -> before-save {1}".format(h0, h1))   # noqa: E702
    m = s.save(broken_ok=True)
    s.gate("PS artefact saved, md5 differs from the input; input unchanged", m and m != s.input_md5 and K.md5(s.input_vi) == s.input_md5, m)
    if m and not DRY:                                                              # RBW on a throwaway scratch of the SAVED file
        rb = s.scratch("rbw", s.work); w0 = set(AT.all_wire_uids(rb)[0]); s.broken_wire_count(target=rb, tag="RBW")   # noqa: E702
        rr = AT.read_terms(rb, AT.OP_ALLTERMS_V1)[0]; gone = w0 - set(AT.all_wire_uids(rb)[0])                        # noqa: E702
        sinks = set(x.bind["term"].get(t, t) for t in (SX.SS.resolve_addr(L, a["dst"], False)["term_uid"] for a in A if a["op"] == "wire"))
        s.fact("RBW deleted {0}".format(sorted(gone)))
        s.gate("RBW deletes no wire of a re-wired sink (scratch of the saved file)", not [r for r in rr if r["term_uid"] in sinks and r["wire_uid"] in gone], sorted(gone))
        s.drop_scratch(rb, "RBW")
    _x = m and m != s.input_md5 and s.work in s.scratches and s.scratches.remove(s.work)   # noqa: F841
    s.R["l2a3"] = {"final": s.work, "md5": m, "cdiff_rows": got, "handles": [h0, h1], "level": "STRUCTURAL, broken by design, never run"}; s.dump()   # noqa: E702


if __name__ == "__main__":
    st = K.Stage(BASE["vi"], BASE["md5"], "D1_l2_a3", preload=False, deadline_min=35, out_json=os.path.join(K.BENCH, "stage_d1_l2a3.json"), task="card 108-2")
    rc = K.run(body, st)
    DRY or SX.kill_labview_at_exit()
    sys.exit(rc)
