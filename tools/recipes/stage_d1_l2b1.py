r"""stage_d1_l2b1 - cards 110-2/110-4, STAGE L2-B1 (d1-loop12-17-split-plan.md PD223(b); briefs 110-1 D/B, 110-2 J1/J3, 110-4 items 1-2). INPUT the
plan base graph's VI (L2-A3 bed D1_l2_a3_20260927_151224.vi), FRESH LabVIEW -> claudeDev\D1_l2_b1_<ts>.vi (rule-6 GUI save, ExecState 0 by design,
never run). ROWS ONLY FROM plan_l2b1.json: group B's 8 nodes + 4 CTs + (J1) indicators #8323/#28786 and constants #6404/#9050/#9906 into 1.2 body
#23166, 2 group-B-only SR pairs re-created on #10170 (unwired: B2), wire rows with node/CT ends. J3: CHECKPOINTS = the rule below UNION every compiled
op whose kind is in stagexec BIND_KINDS. PRIOR ART: stage_d1_l2a3.py (DryPlanBE, 179(b) CT reader, LB/PB/IB/RBW, every gate in dry), stage_d1_l2a1.py
(moves + add_shift_reg + CHECKPOINTS, PD193(a); panel sinks skip the 2nd pass, :84). No new op. PREDICTION: L1 one op per action, 6 moved CTs; E1
every checkpoint == its sim step; CT each moved CT: one row, partners == sim end; D new/lost wires == sim; FU frame diagrams unchanged; PB cdiff(S1,
end) == the plan's open_rows (FATAL, before save) UNDER THE 110-4 LICENCE (uid keying = PD173, split-plan :360-363; review c68-m4a-p6b-rename :85):
data in plan_l2b1_licence.json (decision 8/X6: no uid re-typed here), mapping in PB: real rows on the licensed term uids (#2626's 3 UNWIRED QRT-owed
inputs) keyed by their BASE name; void unless all are unwired inputs of their node; no other row. L3: those nodes' inputs logged after op 27 and after the save. PS saved, md5 != input,
input unchanged; IB after the save per re-wired NODE sink: wire_delta 0 + Is Broken? False (face/panel sinks: E1 + RBW (+CT), PD184(a)); RBW (scratch)
deletes no re-wired sink's wire.    py tools/bgrun.py --material --max-min 90 --log tools/bench/stage_d1_l2b1_c110d.log -- py -u tools/recipes/stage_d1_l2b1.py"""
import copy, json, os, sys                                                         # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, vigraph as V, stagexec as SX, jev_candidates as JC, allterms as AT  # noqa: E401,E402
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                 # noqa: E731
PLAN = os.path.join(K.BENCH, "plan_l2b1.json")                                      # ONE literal: stage_prerun.plan_files reads it
P = J(PLAN); BASE = J(K.ROOT, P["finalized"]["base"]["path"]); A = P["actions"]; LICF = J(K.BENCH, "plan_l2b1_licence.json")   # noqa: E702
DRY, LAB = bool(getattr(g.report_all, "_dry", False)), JC.node_labels_default()
KIND = [a["op"] for a in A]                  # PD193(a) read set, DERIVED from the plan (never typed): 0, every op-kind change, every 4th
BIND = set(k for k, o in enumerate(SX.compile_plan(P), 1) if o["kind"] in SX.BIND_KINDS)   # J3: every op that creates/binds an object
CHECKPOINTS = tuple(sorted({0, len(A)} | {i + 1 for i in range(len(A) - 1) if KIND[i] != KIND[i + 1]} | set(range(4, len(A), 4 if len(A) < 30 else 6)) | BIND))   # op, the end
TUNSR, LIC = ("LoopTunnel", "Tunnel", "SelectorTunnel", "LeftShiftRegister", "RightShiftRegister"), dict((int(u), int(e["node"])) for e in LICF["rename_by_uid"] for u in e["term_uids"])   # LIC: term uid -> owner, the ONLY rows PB keys by uid
CLS = dict((int(o["uid"]), o["class"]) for o in BASE["objs"])
MOVED_CT = [a["nodes"][0] for a in A if a["op"] == "move_in" and CLS.get(a["nodes"][0]) == "ControlTerminal"]
WIR = [a for a in A if a["op"] == "wire" and isinstance(a["dst"], dict)]
wires, frames = (lambda rows: set(int(r["wire_uid"]) for r in rows if r["wire_uid"])), (lambda rows: set(int(r["frame_diagram"] or 0) for r in rows))
nodry = lambda gid, why: print("GATE {0} NOT RUNNABLE IN DRY: {1}".format(gid, why), flush=True)   # noqa: E731
L3 = lambda s, rr, tag: s.fact("L3 licensed node(s) {0} inputs {1} (uid, name, wire): {2}; data type string NOT READ - no Terminal.Data Type (634A008) reader op exists (docs/NAMES.md:477-485)".format(sorted(set(LIC.values())), tag, sorted(set((int(r["term_uid"]), r["term_name"], int(r["wire_uid"] or 0)) for r in rr if int(r["owner_uid"]) in LIC.values() and not r["is_source"]))))   # noqa: E731


def body(s):
    print(__doc__, flush=True)
    s.gate("L0 the executed plan is FINAL, open_rows_match, plan_in = the plan_l2b1_in stageplan", P.get("final") is True and P["finalized"].get("open_rows_match") is True
           and os.path.splitext(P["finalized"]["plan_in"]["path"])[0].endswith("plan_l2b1_in"), (K.md5(PLAN), P["finalized"]["plan_in"]), fatal=True)
    s.start(); s.discard_work(); bp = K.mod("bench_prep"); h0 = bp.labview_handles()   # noqa: E702
    ex, last = {}, lambda: ex["x"].step(len(A))["state"]

    def ct_read(uid, rows, cts):                                                   # 179(b): the panel-terminal reader
        b = ex["x"].bind["term"]; L = last()                                       # noqa: E702
        sim = [r for r in L["terminals"] if r["term_uid"] == uid]; sw = sim[0]["wire_uid"] if sim else 0   # noqa: E702
        want = sorted(b.get(r["term_uid"], r["term_uid"]) for r in L["terminals"] if sw and r["wire_uid"] == sw and r["term_uid"] != uid)
        hit = [r for r in rows if r["term_uid"] == uid]
        got = sorted(r["term_uid"] for r in rows if hit and hit[0]["wire_uid"] and r["wire_uid"] == hit[0]["wire_uid"] and r["term_uid"] != uid)
        s.fact("CT #{0}: ControlTerminal {1} rows {2} partners real {3} sim {4}{5}".format(uid, uid in cts, len(hit), got, want, " (DRY: simulated end rows)" if DRY else ""))
        return uid in cts and len(hit) == 1 and got == want, {"real": got, "sim": want, "rows": len(hit)}
    be = SX.DryPlanBE(s, P, PLAN, BASE) if DRY else SX.LVBackend(s, BASE["fs_tunnel_pairs"], sink_gates=[], gates={}, mem_stop_mb=SX.MEM_STOP_MB)
    x = ex["x"] = SX.Executor(PLAN, be, log=lambda m: print(m, flush=True), checkpoints=CHECKPOINTS or None)
    OPS = [dict(o, id=A[o["acts"][0] - 1]["id"]) for o in x.ops]; acts = sorted(n for o in OPS for n in o["acts"])   # noqa: E702
    s.gate("L1 every plan action compiled into exactly one real op ({0} -> {1}); checkpoints {2}; moved CTs {3}".format(len(A), len(OPS), CHECKPOINTS, MOVED_CT),
           acts == list(range(1, len(A) + 1)) and len(OPS) == len(A) and len(MOVED_CT) == 6, acts, fatal=True)   # D2 4 + J1 #8323/#28786
    try:
        real = x.run(); s.gate("E1 every checkpoint's real graph == its simulated step ({0} ops)".format(len(OPS)), True)   # noqa: E702
    except SX.ExecStop as e:
        return SX.report_stop(s, x, be, e)
    s.R["stagexec"] = x.report; s.fact("BINDING obj {0} term {1}".format(x.bind["obj"], x.bind["term"])); L3(s, real, "after op {0} (the executor's last read)".format(len(OPS)))   # noqa: E702
    DRY or s.fact("METER SUMMARY {0}".format(json.dumps(be.meter.summary(), default=str)))
    L = last(); ob = x.bind["obj"]                                                  # noqa: E702
    rows = real if DRY else AT.read_terms(s.work, AT.OP_ALLTERMS_V1)[0]
    cts = set(int(o["uid"]) for o in be.st["objs"] if o.get("class") == "ControlTerminal") if DRY else set(int(o["uid"]) for o in g.report_all(s.work, "ControlTerminal"))
    for u in MOVED_CT:
        ok, d = ct_read(u, rows, cts)
        s.gate("CT #{0}: moved ControlTerminal read by the 179(b) reader == simulated end".format(u), ok, d)
    sim_new, sim_lost = wires(L["terminals"]) - wires(BASE["terminals"]), wires(BASE["terminals"]) - wires(L["terminals"])
    new, lost = wires(real) - wires(BASE["terminals"]), wires(BASE["terminals"]) - wires(real)
    s.gate("D the end adds the plan's {0} new wire(s) and loses exactly the simulated base wires ({1})".format(len(sim_new), len(sim_lost)),
           len(new) == len(sim_new) and lost == sim_lost, {"new": sorted(new)[:30], "lost-extra": sorted(lost - sim_lost)[:20], "lost-missing": sorted(sim_lost - lost)[:20]})
    s.gate("FU the set of frame diagrams is unchanged", frames(BASE["terminals"]) == frames(real), (sorted(frames(BASE["terminals"]) ^ frames(real))[:20]), fatal=True)
    s.es("after all rows (warm, RECORDED - the plan's open rows stay open by design)")
    loops = copy.deepcopy(L["loops"])
    for lp in loops or []:                                                          # register table = the simulation's, via the binding
        lp["right_uids"], lp["left_of"] = [ob.get(int(u), int(u)) for u in lp.get("right_uids") or []], dict((str(ob.get(int(k), int(k))), [ob.get(int(y), int(y)) for y in (v if isinstance(v, list) else [v])]) for k, v in (lp.get("left_of") or {}).items())
    s1p = J(JC.WIKI, JC.S1_KEY + ".json")
    S1f = V.build4(s1p["terminals"], J(JC._newest("graph_objs_s1_*.json"))["objects"], J(JC._newest("graph_loops_s1_*.json"))["loops"], LAB, s1p["fs_tunnel_pairs"], frame_keyed=True)
    bn, lic = dict((r["term_uid"], r["term_name"]) for r in BASE["terminals"]), sorted(set(int(r["term_uid"]) for r in real if int(r["term_uid"]) in LIC and int(r["owner_uid"]) == LIC[int(r["term_uid"])] and not r["is_source"] and not r["wire_uid"]))
    realL = [dict(r, term_name=bn[int(r["term_uid"])]) if lic == sorted(LIC) and int(r["term_uid"]) in LIC else r for r in real]; s.fact("LICENCE (brief_110-4 item 1; data plan_l2b1_licence.json, mapping here in PB): unwired licensed inputs {0} of {1} -> {2}; PB names {3}".format(lic, sorted(LIC), "APPLIED" if lic == sorted(LIC) else "VOID (not every licensed uid is an unwired input of its node)", sorted(set((int(r["term_uid"]), r["term_name"]) for r in realL if int(r["owner_uid"]) in LIC.values() and not r["is_source"]))))   # noqa: E702
    G1 = V.build4(realL, getattr(be, "last_objs", None) or be.st["objs"], loops, LAB, BASE["fs_tunnel_pairs"], frame_keyed=True)
    cd = V.computation_diff_frame(S1f, G1)
    for y in cd["rows"]: s.fact("CDIFF ROW {0}".format(dict((k, V.show(v) if k == "sink" else v) for k, v in y.items())))  # noqa: E701
    got = sorted(set((int(y["node"]), str(y["sink"]).split("|")[2]) for y in cd["rows"]))
    want = sorted(set((int(y["node"]), y["term"]) for y in P["open_rows"]))
    s.gate("PB frame-keyed cdiff(S1, real end) == the plan's {0} open_rows under the uid licence {1} (FATAL, before save)".format(len(want), sorted(LIC)), got == want,
           {"extra": sorted(set(got) - set(want)), "missing": sorted(set(want) - set(got)), "licence_applied": lic == sorted(LIC)}, fatal=True)
    s.census(tag="after L2-B1")
    h1 = bp.labview_handles(); s.fact("PH handles RECORDED: post-open {0} -> before-save {1}".format(h0, h1))   # noqa: E702
    m = s.save(broken_ok=True)
    s.gate("PS artefact saved, md5 differs from the input; input unchanged", m and m != s.input_md5 and K.md5(s.input_vi) == s.input_md5, m)
    m and L3(s, real if DRY else AT.read_terms(s.work, AT.OP_ALLTERMS_V1)[0], "after the save" + (" (DRY: simulated end rows)" if DRY else " (fresh whole-VI read of the saved VI)"))
    nm, ends = dict((r["term_uid"], r["term_name"]) for r in BASE["terminals"]), []
    for a in WIR:                                                                   # the re-wired NODE sinks, from the plan's wire rows
        if CLS.get(a["dst"]["uid"]) in TUNSR + ("ControlTerminal",):              # panel sink: the CT gate (stage_d1_l2a1.py:84)
            s.fact("IB {0}: sink #{1} is a {2} (face / panel sink) - E1 + RBW (+CT) only (PD184(a))".format(a["id"], a["dst"]["uid"], CLS.get(a["dst"]["uid"])))
            continue
        r = SX.SS.resolve_addr(L, a["dst"], False); tu = x.bind["term"].get(r["term_uid"], r["term_uid"])   # noqa: E702
        su = a["src"]["uid"] if isinstance(a["src"], dict) else L["sym"][a["src"].split(".")[0]]
        wu = ([int(q["wire_uid"]) for q in rows if int(q["term_uid"]) == tu] or [0])[0]
        ends.append((a["id"], ob.get(su, su), {"uid": a["dst"]["uid"], "term": nm.get(a["dst"]["term_uid"]), "verify_term_uid": tu,
                                                "diagram": r["frame_diagram"], "owner_class": "", "term_class": ""}, wu, tu))
    s.fact("IB ENDS (after the save): {0}".format([(i, y, e["uid"], e["term"], w) for i, y, e, w, _t in ends]))
    DRY and (nodry("IB", "the ordered second pass is a live Connect Wire + Is Broken? readback on the saved VI (no dry model)"), nodry("RBW", "Remove Bad Wires (VI method 410) runs inside LabVIEW on a scratch copy of the saved file"))
    if m and not DRY:
        for i, y, e, w, _t in ends:                                                 # ORDERED second pass, below the save point (NAMES.md:1098)
            s.expect_is_broken_false("IB " + i, lambda e=e, y=y, i=i: s.safe("2nd pass " + i, lambda: s.cfw_second_pass(y, e), {})[0], wire_uid=w)
        rb = s.scratch("rbw", s.work); w0 = set(AT.all_wire_uids(rb)[0]); s.broken_wire_count(target=rb, tag="RBW")   # noqa: E702
        rr = AT.read_terms(rb, AT.OP_ALLTERMS_V1)[0]; gone = w0 - set(AT.all_wire_uids(rb)[0])                        # noqa: E702
        sinks = set(x.bind["term"].get(a["dst"]["term_uid"], a["dst"]["term_uid"]) for a in WIR)
        s.fact("RBW deleted {0}".format(sorted(gone)))
        s.fact("RBW ENDS (pre-save read, PD223(a) attribution; [] = termless) {0}".format(dict((w, sorted((q["owner_uid"], q["owner_class"], q["term_name"], q["is_source"]) for q in rows if q["wire_uid"] == w)) for w in sorted(gone))))
        s.gate("RBW deletes no wire of a re-wired sink (scratch of the saved file)", not [q for q in rr if q["term_uid"] in sinks and q["wire_uid"] in gone], sorted(gone))
        s.drop_scratch(rb, "RBW")
    _x = m and m != s.input_md5 and s.work in s.scratches and s.scratches.remove(s.work)   # noqa: F841
    s.R["l2b1"] = {"final": s.work, "md5": m, "bytes": (not DRY) and os.path.exists(s.work) and os.path.getsize(s.work), "cdiff_rows": got, "handles": [h0, h1], "level": "STRUCTURAL, broken by design, never run"}; s.dump()   # noqa: E702


if __name__ == "__main__":
    st = K.Stage(BASE["vi"], BASE["md5"], "D1_l2_b1", preload=False, deadline_min=80, out_json=os.path.join(K.BENCH, "stage_d1_l2b1.json"), task="card 110-4")
    rc = K.run(body, st)
    DRY or SX.kill_labview_at_exit()
    sys.exit(rc)
