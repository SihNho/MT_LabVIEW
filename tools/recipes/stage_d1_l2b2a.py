r"""stage_d1_l2b2a - card 111-5, STAGE L2-B2a (d1-loop12-17-split-plan.md PD225(f); split page tools/bench/cards/split_plan_111_l2b2.md). INPUT the
plan base graph's VI (the B1 bed D1_l2_b1_20260927_193100.vi, PD225(c)), FRESH LabVIEW -> claudeDev\D1_l2_b2a_<ts>.vi (rule-6 GUI save, ExecState 0
by design, never run). ROWS ONLY FROM plan_l2b2a.json (decision 8): 7 wire rows, no move/create - B2-09..14 feed the two 1.2 registers B1 made
(SRB1 R #9603 / L #10544, SRB2 R #25545 / L #25582 on #10170) and B2-15 wires CT #403 'Z/dZ' to case selector Tunnel #2276. PRIOR ART: stage_d1_l2b1.py
(this file is its cut: same checkpoints rule + J3 BIND, CT reader 179(b), D/FU/PB/PS, every gate in dry). No new op. CHANGED vs B1 (PD224(h) carry):
the RBW gate READS every re-wired sink's wire in the scratch BEFORE Remove Bad Wires (the B1 gate read after it, vacuous: split plan :1919), and its
pre-read half runs in dry on the simulated end. No #2626 uid licence: the base already names #2626's 4 inputs 'array' and the plan's open_rows carry
that (plan_l2b2a_in.json). PREDICTION: L1 one op per action, 1 CT end (#403); E1 every checkpoint == its sim step; CT #403 one row, partners == sim;
D new/lost == sim; FU unchanged; PB cdiff(S1, end) == the plan's open_rows (FATAL, before save); PS saved, md5 != input, input unchanged; RBW-PRE every
re-wired sink has a wire before RBW; RBW deletes none of those wires. IB: every sink here is a face/register (no node sink) -> E1 + RBW only (PD184(a)).
    py tools/bgrun.py --material --max-min 60 --log tools/bench/stage_d1_l2b2a.log -- py -u tools/recipes/stage_d1_l2b2a.py"""
import copy, json, os, sys                                                         # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, vigraph as V, stagexec as SX, jev_candidates as JC, allterms as AT  # noqa: E401,E402
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                 # noqa: E731
PLAN = os.path.join(K.BENCH, "plan_l2b2a.json")                                     # ONE literal: stage_prerun.plan_files reads it
P = J(PLAN); BASE = J(K.ROOT, P["finalized"]["base"]["path"]); A = P["actions"]   # noqa: E702
DRY, LAB = bool(getattr(g.report_all, "_dry", False)), JC.node_labels_default()
KIND = [a["op"] for a in A]                  # PD193(a) read set, DERIVED from the plan (never typed): 0, every op-kind change, every 4th
BIND = set(k for k, o in enumerate(SX.compile_plan(P), 1) if o["kind"] in SX.BIND_KINDS)   # J3: every op that creates/binds an object
CHECKPOINTS = tuple(sorted({0, len(A)} | {i + 1 for i in range(len(A) - 1) if KIND[i] != KIND[i + 1]} | set(range(4, len(A), 4 if len(A) < 30 else 6)) | BIND))
TUNSR = ("LoopTunnel", "Tunnel", "SelectorTunnel", "LeftShiftRegister", "RightShiftRegister")
CLS = dict((int(o["uid"]), o["class"]) for o in BASE["objs"])
WIR = [a for a in A if a["op"] == "wire" and isinstance(a["dst"], dict)]
CT_END = sorted(set(e["uid"] for a in WIR for e in (a["src"], a["dst"]) if isinstance(e, dict) and CLS.get(e["uid"]) == "ControlTerminal"))
wires, frames = (lambda rows: set(int(r["wire_uid"]) for r in rows if r["wire_uid"])), (lambda rows: set(int(r["frame_diagram"] or 0) for r in rows))
nodry = lambda gid, why: print("GATE {0} NOT RUNNABLE IN DRY: {1}".format(gid, why), flush=True)   # noqa: E731


def body(s):
    print(__doc__, flush=True)
    s.gate("L0 the executed plan is FINAL, open_rows_match, plan_in = the plan_l2b2a_in stageplan", P.get("final") is True and P["finalized"].get("open_rows_match") is True
           and os.path.splitext(P["finalized"]["plan_in"]["path"])[0].endswith("plan_l2b2a_in"), (K.md5(PLAN), P["finalized"]["plan_in"]), fatal=True)
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
    s.gate("L1 every plan action compiled into exactly one real op ({0} -> {1}); checkpoints {2}; CT ends {3}".format(len(A), len(OPS), CHECKPOINTS, CT_END),
           acts == list(range(1, len(A) + 1)) and len(OPS) == len(A) and CT_END == [403], acts, fatal=True)
    try:
        real = x.run(); s.gate("E1 every checkpoint's real graph == its simulated step ({0} ops)".format(len(OPS)), True)   # noqa: E702
    except SX.ExecStop as e:
        return SX.report_stop(s, x, be, e)
    s.R["stagexec"] = x.report; s.fact("BINDING obj {0} term {1}".format(x.bind["obj"], x.bind["term"]))   # noqa: E702
    DRY or s.fact("METER SUMMARY {0}".format(json.dumps(be.meter.summary(), default=str)))
    L = last(); ob = x.bind["obj"]                                                  # noqa: E702
    rows = real if DRY else AT.read_terms(s.work, AT.OP_ALLTERMS_V1)[0]
    cts = set(int(o["uid"]) for o in be.st["objs"] if o.get("class") == "ControlTerminal") if DRY else set(int(o["uid"]) for o in g.report_all(s.work, "ControlTerminal"))
    for u in CT_END:
        ok, d = ct_read(u, rows, cts)
        s.gate("CT #{0}: re-wired ControlTerminal read by the 179(b) reader == simulated end".format(u), ok, d)
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
    G1 = V.build4(real, getattr(be, "last_objs", None) or be.st["objs"], loops, LAB, BASE["fs_tunnel_pairs"], frame_keyed=True)
    cd = V.computation_diff_frame(S1f, G1)
    for y in cd["rows"]: s.fact("CDIFF ROW {0}".format(dict((k, V.show(v) if k == "sink" else v) for k, v in y.items())))  # noqa: E701
    got = sorted(set((int(y["node"]), str(y["sink"]).split("|")[2]) for y in cd["rows"]))
    want = sorted(set((int(y["node"]), y["term"]) for y in P["open_rows"]))
    s.gate("PB frame-keyed cdiff(S1, real end) == the plan's {0} open_rows (FATAL, before save)".format(len(want)), got == want,
           {"extra": sorted(set(got) - set(want)), "missing": sorted(set(want) - set(got))}, fatal=True)
    sinks = sorted(set(x.bind["term"].get(a["dst"]["term_uid"], a["dst"]["term_uid"]) for a in WIR))
    pre = dict((int(q["term_uid"]), int(q["wire_uid"] or 0)) for q in rows if int(q["term_uid"]) in sinks)
    s.gate("RBW-PRE every re-wired sink {0} carries a wire in the end read (pre-save{1})".format(sinks, "; DRY: simulated end rows" if DRY else ""),
           sorted(pre) == sinks and all(pre.values()), pre)
    for a in WIR:                                                                   # no node sink here: face/register sinks (PD184(a))
        s.fact("IB {0}: sink #{1} is a {2} - {3}".format(a["id"], a["dst"]["uid"], CLS.get(a["dst"]["uid"]), "face/register sink: E1 + RBW only (PD184(a))" if CLS.get(a["dst"]["uid"]) in TUNSR + ("ControlTerminal",) else "NODE SINK: no IB route in this recipe"))
    s.census(tag="after L2-B2a")
    h1 = bp.labview_handles(); s.fact("PH handles RECORDED: post-open {0} -> before-save {1}".format(h0, h1))   # noqa: E702
    m = s.save(broken_ok=True)
    s.gate("PS artefact saved, md5 differs from the input; input unchanged", m and m != s.input_md5 and K.md5(s.input_vi) == s.input_md5, m)
    DRY and nodry("RBW", "Remove Bad Wires (VI method 410) runs inside LabVIEW on a scratch copy of the saved file; its pre-read half ran above as RBW-PRE")
    if m and not DRY:
        rb = s.scratch("rbw", s.work); rr = AT.read_terms(rb, AT.OP_ALLTERMS_V1)[0]      # noqa: E702
        pw = dict((int(q["term_uid"]), int(q["wire_uid"] or 0)) for q in rr if int(q["term_uid"]) in sinks)   # READ BEFORE RBW (PD224(h))
        s.gate("RBW-PRE2 every re-wired sink carries a wire in the saved scratch, read BEFORE Remove Bad Wires", sorted(pw) == sinks and all(pw.values()), pw)
        w0 = set(AT.all_wire_uids(rb)[0]); s.broken_wire_count(target=rb, tag="RBW"); gone = w0 - set(AT.all_wire_uids(rb)[0])   # noqa: E702
        s.fact("RBW deleted {0}".format(sorted(gone)))
        s.gate("RBW deletes no wire of a re-wired sink (wires read before RBW)", not (set(pw.values()) & gone), {"sink_wires": pw, "gone": sorted(gone)[:40]})
        s.drop_scratch(rb, "RBW")
    _x = m and m != s.input_md5 and s.work in s.scratches and s.scratches.remove(s.work)   # noqa: F841
    s.R["l2b2a"] = {"final": s.work, "md5": m, "bytes": (not DRY) and os.path.exists(s.work) and os.path.getsize(s.work), "cdiff_rows": got, "handles": [h0, h1], "level": "STRUCTURAL, broken by design, never run"}; s.dump()   # noqa: E702


if __name__ == "__main__":
    st = K.Stage(BASE["vi"], BASE["md5"], "D1_l2_b2a", preload=False, deadline_min=50, out_json=os.path.join(K.BENCH, "stage_d1_l2b2a.json"), task="card 111-5")
    rc = K.run(body, st)
    DRY or SX.kill_labview_at_exit()
    sys.exit(rc)
