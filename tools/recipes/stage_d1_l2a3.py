r"""stage_d1_l2a3 - cards 108-2/109-2, STAGE L2-A3 (d1-loop12-17-split-plan.md PD221(d), PD222(g)). INPUT the plan base graph's VI (L2-A2
file), FRESH LabVIEW -> claudeDev\D1_l2_a3_<ts>.vi (rule-6 GUI save, ExecState 0 by design, never run). ROWS ONLY FROM plan_l2a3.json.
CARRIER (PD221(d), CLAUDE.md 1c''): 2 hidden indicators in the 1.2 body + 2 Local READS in the 1.1 body; no queue, no edge detection.
PRIOR ART: stage_d1_l2a2.py (DryBE, 179(b) CT reader, PB cdiff, RBW on a scratch of the saved file); stage_d1_l2a1.py:82-91 (ordered
second pass: SS.resolve_addr + stagekit.cfw_second_pass + expect_is_broken_false); stagexec CREATE_ROUTES. No new op.
109-2 FIXES: LB reads no `term_class` (read_terms rows lack it, allterms.py:45-46,85): ControlTerminal = term_uid in report_all(
'ControlTerminal') live / the simulated ControlTerminal objects dry; Local = owner_class 'Local'. Every gate runs in dry on the simulated
end rows or prints 'GATE <id> NOT RUNNABLE IN DRY: <why>'. PREDICTION: L1 action -> one op; E1 checkpoints == sim; CT created indicator's
real partners == sim; LB each label on exactly 1 ControlTerminal + 1 Local; D new wires == sim, lost == sim; FU frame diagrams unchanged;
PB cdiff(S1, end) == the 6 open_rows (FATAL, before save); PS saved, md5 != input, input unchanged; IB AFTER the save (in memory, never
re-saved) per re-wired sink: wire_delta 0 + Is Broken? False on the sink's wire uid; RBW on a scratch deletes no re-wired sink's wire.
    py tools/bgrun.py --material --max-min 60 --log tools/bench/stage_d1_l2a3.log -- py -u tools/recipes/stage_d1_l2a3.py"""
import copy, json, os, sys                                                         # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, vigraph as V, stagexec as SX, jev_candidates as JC, allterms as AT  # noqa: E401,E402
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                 # noqa: E731
PLAN = os.path.join(K.BENCH, "plan_l2a3.json")                                      # ONE literal: stage_prerun.plan_files reads it
P = J(PLAN); BASE = J(K.ROOT, P["finalized"]["base"]["path"]); A = P["actions"]   # noqa: E702
DRY, LAB = bool(getattr(g.report_all, "_dry", False)), JC.node_labels_default()
IND = [a for a in A if a["op"] == "create" and a["class"] == "ControlTerminal" and a.get("indicator")]   # from the plan
LOC = [a for a in A if a["op"] == "create" and a["class"] == "Local"]
WIR = [a for a in A if a["op"] == "wire" and isinstance(a["dst"], dict)]
wires = lambda rows: set(int(r["wire_uid"]) for r in rows if r["wire_uid"])        # noqa: E731
frames = lambda rows: set(int(r["frame_diagram"] or 0) for r in rows)              # noqa: E731
nodry = lambda gid, why: print("GATE {0} NOT RUNNABLE IN DRY: {1}".format(gid, why), flush=True)   # noqa: E731


def body(s):
    print(__doc__, flush=True)
    s.gate("L0 the executed plan is FINAL, open_rows_match, plan_in = the plan_l2a3_in stageplan", P.get("final") is True and   # no .json literal:
           P["finalized"].get("open_rows_match") is True and os.path.splitext(P["finalized"]["plan_in"]["path"])[0].endswith("plan_l2a3_in"),  # plan_files (X2)
           (K.md5(PLAN), P["finalized"]["plan_in"]), fatal=True)
    s.start(); s.discard_work(); bp = K.mod("bench_prep"); h0 = bp.labview_handles()   # noqa: E702
    ex, last = {}, lambda: ex["x"].step(len(A))["state"]

    def ct_set(be, real):                                                          # live: report_all; dry: sim objs + sim CT rows
        if DRY:                                                                    # (stagesim.py:976-983 makes a created CT a row, no obj)
            return set(int(o["uid"]) for o in be.st["objs"] if o.get("class") == "ControlTerminal") | set(int(r["term_uid"]) for r in real if r.get("term_class") == "ControlTerminal")
        return set(int(o["uid"]) for o in g.report_all(s.work, "ControlTerminal"))

    def ct_read(sim_uid, tag, rows, cts):                                          # 179(b): the panel-terminal reader
        b = ex["x"].bind["term"]; real_uid = b.get(sim_uid, sim_uid)               # noqa: E702
        sim = [r for r in last()["terminals"] if r["term_uid"] == sim_uid]; sw = sim[0]["wire_uid"] if sim else 0   # noqa: E702
        want = sorted(b.get(r["term_uid"], r["term_uid"]) for r in last()["terminals"] if sw and r["wire_uid"] == sw and r["term_uid"] != sim_uid)
        hit = [r for r in rows if r["term_uid"] == real_uid]
        got = sorted(r["term_uid"] for r in rows if hit and hit[0]["wire_uid"] and r["wire_uid"] == hit[0]["wire_uid"] and r["term_uid"] != real_uid)
        s.fact("CT {0} sim #{1} real #{2}: ControlTerminal {3} rows {4} partners real {5} sim {6}{7}".format(tag, sim_uid, real_uid, real_uid in cts, len(hit), got, want, " (DRY: simulated end rows)" if DRY else ""))
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
    L = last(); ob = x.bind["obj"]                                                  # noqa: E702
    rows, cts = (real if DRY else AT.read_terms(s.work, AT.OP_ALLTERMS_V1)[0]), ct_set(be, real)
    for a in IND:
        ok, d = ct_read(L["sym"]["new:" + a["as"]], "row " + a["id"], rows, cts)
        s.gate("CT {0}: created indicator read by the 179(b) reader == simulated end".format(a["id"]), ok, d)
    s.fact("LB ROUTE: ControlTerminal = term_uid in {0} ({1} uids); Local = owner_class 'Local'; rows = {2} ({3})".format(
        "the simulated ControlTerminal objects + simulated ControlTerminal rows" if DRY else "report_all('ControlTerminal')", len(cts), "the simulated end" if DRY else "allterms.read_terms", len(rows)))
    for a in IND + LOC:
        n_ct = sum(1 for r in rows if int(r["term_uid"]) in cts and r["term_name"] == a["label"])
        n_lo = sum(1 for r in rows if r["owner_class"] == "Local" and r["term_name"] == a["label"])
        s.gate("LB {0}: label {1!r} on exactly 1 ControlTerminal and 1 Local (counted CT {2}, Local {3})".format(a["id"], a["label"], n_ct, n_lo), n_ct == 1 and n_lo == 1, (n_ct, n_lo))
    sim_new, sim_lost = wires(L["terminals"]) - wires(BASE["terminals"]), wires(BASE["terminals"]) - wires(L["terminals"])
    new, lost = wires(real) - wires(BASE["terminals"]), wires(BASE["terminals"]) - wires(real)
    s.gate("D the end adds the plan's {0} new wire(s) and loses exactly the simulated base wires {1}".format(len(sim_new), sorted(sim_lost)),
           len(new) == len(sim_new) and lost == sim_lost, {"new": sorted(new), "lost": sorted(lost)[:20]})
    s.gate("FU the set of frame diagrams is unchanged", frames(BASE["terminals"]) == frames(real),
           (sorted(frames(BASE["terminals"]) ^ frames(real))[:20]), fatal=True)
    s.es("after all rows (warm, RECORDED - the plan's open rows stay open by design)")
    loops = copy.deepcopy(L["loops"])
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
    nm, ends = dict((r["term_uid"], r["term_name"]) for r in BASE["terminals"]), []
    for a in WIR:                                                                   # the re-wired sinks, from the plan's wire rows
        r = SX.SS.resolve_addr(L, a["dst"], False); tu = x.bind["term"].get(r["term_uid"], r["term_uid"]); su = L["sym"][a["src"].split(".")[0]]   # noqa: E702
        wu = ([int(q["wire_uid"]) for q in rows if int(q["term_uid"]) == tu] or [0])[0]
        ends.append((a["id"], ob.get(su, su), {"uid": a["dst"]["uid"], "term": nm.get(a["dst"]["term_uid"]), "verify_term_uid": tu,
                                                "diagram": r["frame_diagram"], "owner_class": "", "term_class": ""}, wu, tu))
    s.fact("IB ENDS (after the save): {0}".format([(i, y, e["uid"], e["term"], w) for i, y, e, w, _t in ends]))
    DRY and (nodry("IB", "the ordered second pass is a live Connect Wire + Is Broken? readback on the saved VI (no dry model)"),
             nodry("RBW", "Remove Bad Wires (VI method 410) runs inside LabVIEW on a scratch copy of the saved file"))
    if m and not DRY:
        for i, y, e, w, _t in ends:                                                 # ORDERED second pass, below the save point (NAMES.md:1098)
            s.expect_is_broken_false("IB " + i, lambda e=e, y=y, i=i: s.safe("2nd pass " + i, lambda: s.cfw_second_pass(y, e), {})[0], wire_uid=w)
        rb = s.scratch("rbw", s.work); w0 = set(AT.all_wire_uids(rb)[0]); s.broken_wire_count(target=rb, tag="RBW")   # noqa: E702
        rr = AT.read_terms(rb, AT.OP_ALLTERMS_V1)[0]; gone = w0 - set(AT.all_wire_uids(rb)[0])                        # noqa: E702
        sinks = set(t for _i, _y, _e, _w, t in ends)
        s.fact("RBW deleted {0}".format(sorted(gone)))
        s.gate("RBW deletes no wire of a re-wired sink (scratch of the saved file)", not [q for q in rr if q["term_uid"] in sinks and q["wire_uid"] in gone], sorted(gone))
        s.drop_scratch(rb, "RBW")
    _x = m and m != s.input_md5 and s.work in s.scratches and s.scratches.remove(s.work)   # noqa: F841
    s.R["l2a3"] = {"final": s.work, "md5": m, "bytes": (not DRY) and os.path.exists(s.work) and os.path.getsize(s.work), "cdiff_rows": got, "handles": [h0, h1], "level": "STRUCTURAL, broken by design, never run"}; s.dump()   # noqa: E702


if __name__ == "__main__":
    st = K.Stage(BASE["vi"], BASE["md5"], "D1_l2_a3", preload=False, deadline_min=45, out_json=os.path.join(K.BENCH, "stage_d1_l2a3.json"), task="card 109-2")
    rc = K.run(body, st)
    DRY or SX.kill_labview_at_exit()
    sys.exit(rc)
