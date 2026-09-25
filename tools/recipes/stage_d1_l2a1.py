r"""stage_d1_l2a1 - cycle 81 STAGE L2-A1 (docs/d1-loop12-17-split-plan.md Pre-decided 181(d), 182, 183; executed, not re-decided).
INPUT the bed claudeDev\D1_k_20260925_100155.vi (6cf5b077..., named by the plan's base graph), FRESH LabVIEW -> claudeDev\D1_l2_a1_<ts>.vi
(rule-6 GUI save when ExecState 0 - the 9 PB rows are open by design). ROWS ONLY FROM THE FINALIZED PLAN tools/bench/sim/l2a1/plan_l2a1.json
(its finalized.plan_in = stageplan_l2a1.json md5 329d89ee, PD183(e) pos rows, sim_l2a1_81c.log); no uid and no terminal name is typed here, except
the PD183(d) sink-gate ACTION ID, looked up in the plan.
PRIOR ART: stage_d1_k.py (the skeleton), stagexec (sink_gates 80-3), diag_ctlterm_read_80.py (179(b) reader), sim_l2a1_81b.py (frame-keyed S1,
frame-uid set). No new op. PREDICTION: E1 each real op == its step (42 ops); CT 179(b) reader on every ControlTerminal row (ONE row, a
ControlTerminal, wire partners == the simulated end's) - also the rw_10988_17272 sink gate; P2 second pass (wire_delta 0, Is Broken? False)
on tunnel/register node sinks (PD184: connect sinks = E1 + RBW); FU frame-uid sets of moved Cases equal and non-empty; PB frame-keyed cdiff == the 9 open_rows (FATAL, pre-save);
RBW on a scratch of the saved file deletes no re-wired sink's wire; ES recorded; md5/pins unchanged; refs closed; LabVIEW gone at exit.
    MATERIAL=1 py tools/bgrun.py --max-min 80 --log tools/bench/stage_d1_l2a1.log -- py -u tools/recipes/stage_d1_l2a1.py"""
import copy, json, os, subprocess, sys, time                                       # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, vigraph as V, stagesim as SS, stagexec as SX, jev_candidates as JC, allterms as AT  # noqa: E401,E402
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                 # noqa: E731
PLAN = os.path.join(K.BENCH, "sim/l2a1/plan_l2a1.json")                             # ONE literal: stage_prerun.plan_files reads it
P = J(PLAN); BASE = J(K.ROOT, P["finalized"]["base"]["path"]); A = P["actions"]   # noqa: E702
DRY, CUT, LAB = bool(getattr(g.report_all, "_dry", False)), 10 ** 3, JC.node_labels_default()
WIRING = ("tunnel", "connect", "wire_sr", "branch")
SINK_GATE_IDS = ("rw_10988_17272",)                                                 # PD183(d): the ONLY sink_gates entry
MOVED = set(a["nodes"][0] for a in A if a["op"] == "move_in")
CT_UIDS = sorted(set(int(o["uid"]) for o in BASE["objs"] if o["class"] == "ControlTerminal") & MOVED)   # class from objs (sim_l2a1_81b.py:110)
D0 = set(int(d) for d, v in BASE["owners"].items() if v[0] == "CaseStructure" and int(v[1] or 0) in MOVED)   # 182(e): from the graph
SEL = set(r["owner_uid"] for r in BASE["terminals"] if r["owner_class"] == "SelectorTunnel" and r["term_class"] == "InnerTerminal" and int(r["frame_diagram"] or 0) in D0)
frames = lambda rows: sorted(set(int(r["frame_diagram"]) for r in rows if r["owner_uid"] in SEL and r["term_class"] == "InnerTerminal"))  # noqa: E731


class DryBE(SX.SimBackend):
    """stage_prerun's dry run: the plan's own simulated ops + one Stage op record per real op (stage_d1_k.DryBE)."""
    def __init__(self, s):
        SX.SimBackend.__init__(self, P, SS.base_state(BASE, P.get("context")), SS.load_models()); self.s = s   # noqa: E702

    def _apply(self, op, check=None):
        self.s._op(("wire_" if op["kind"] in WIRING else "") + op["kind"], lambda: {"err": None}, str(op["acts"]))
        return SX.SimBackend._apply(self, op, check)


def body(s):
    print(__doc__, flush=True)
    s.gate("L0 the executed plan is FINAL and its plan_in is the PD183(e) stageplan (md5 329d89ee)", P.get("final") is True and
           P["finalized"]["plan_in"]["md5"] == "329d89eecaa2706ccce38640dbede5aa", (K.md5(PLAN), P["finalized"]["plan_in"]), fatal=True)
    s.start(); s.discard_work(); bp = K.mod("bench_prep"); h0 = bp.labview_handles()   # noqa: E702
    ex, last = {}, lambda: ex["x"].step(len(A))["state"]

    def ct_read(uid, tag):                                                         # 179(b): the panel-terminal reader
        if DRY:
            return True, "dry"
        rows, cts = AT.read_terms(s.work, AT.OP_ALLTERMS_V1)[0], set(int(o["uid"]) for o in g.report_all(s.work, "ControlTerminal"))
        sim = [r for r in last()["terminals"] if r["term_uid"] == uid]; sw = sim[0]["wire_uid"] if sim else 0   # noqa: E702
        want = sorted(ex["x"].bind["term"].get(r["term_uid"], r["term_uid"]) for r in last()["terminals"] if sw and r["wire_uid"] == sw and r["term_uid"] != uid)
        hit = [r for r in rows if r["term_uid"] == uid]
        got = sorted(r["term_uid"] for r in rows if hit and hit[0]["wire_uid"] and r["wire_uid"] == hit[0]["wire_uid"] and r["term_uid"] != uid)
        ok = uid in cts and len(hit) == 1 and got == want
        s.fact("CT {0} #{1}: ControlTerminal {2} rows {3} partners real {4} sim {5}".format(tag, uid, uid in cts, len(hit), got, want))
        return ok, {"real": got, "sim": want, "rows": len(hit)}
    sg, nm = [a for a in A if a["id"] in SINK_GATE_IDS], dict((r["term_uid"], r["term_name"]) for r in BASE["terminals"])
    decl = [{"gate": "CT-" + a["id"], "sink": [a["dst"]["uid"], nm[a["dst"]["term_uid"]]]} for a in sg]
    gates = dict(("CT-" + a["id"], lambda e, u=a["dst"]["uid"]: ct_read(u, "sink gate")) for a in sg)
    be = DryBE(s) if DRY else SX.LVBackend(s, BASE["fs_tunnel_pairs"], sink_gates=decl, gates=gates)
    x = ex["x"] = SX.Executor(PLAN, be, log=lambda m: print(m, flush=True))
    OPS = [dict(o, id=A[o["acts"][0] - 1]["id"]) for o in x.ops]; acts = sorted(n for o in OPS for n in o["acts"])   # noqa: E702
    s.gate("L1 every plan action compiled into exactly one real op ({0} -> {1}); sink_gates {2}; CT rows {3}".format(len(A), len(OPS), decl, CT_UIDS),
           acts == list(range(1, len(A) + 1)) and len(sg) == len(SINK_GATE_IDS) and len(CT_UIDS) == 4, acts, fatal=True)
    try:
        real = x.run(); s.gate("E1 every real op's graph == its simulated step ({0} ops)".format(len(OPS)), True)   # noqa: E702
    except SX.ExecStop as e:
        s.R["stagexec"] = x.report; s.gate("E1 every real op's graph == its simulated step", False, str(e)[:CUT], fatal=True)   # noqa: E702
    s.R["stagexec"] = x.report; s.fact("BINDING obj {0}".format(x.bind["obj"]))    # noqa: E702
    for u in CT_UIDS:
        ok, d = ct_read(u, "row")
        s.gate("CT #{0} ControlTerminal row read by the 179(b) reader == simulated end".format(u), ok, d)
    L = last(); ob = x.bind["obj"]
    for d in OPS:                                                                   # P2 ordered second pass on node-terminal sinks
        a = A[d["acts"][-1] - 1]
        if d["kind"] not in ("tunnel", "wire_sr") or not isinstance(a["dst"], dict) or SS.obj_class(L, a["dst"]["uid"]) == "ControlTerminal":   # PD184(a): K precedent
            s.fact("P2 {0} ({1}): connect / register face / panel sink - E1 + RBW (+CT) only (PD184)".format(d["id"], d["kind"]))
            continue
        r = SS.resolve_addr(L, a["dst"], False)
        su = a["src"]["uid"] if isinstance(a["src"], dict) else L["sym"][a["src"].split(".")[0]]
        end = {"uid": a["dst"]["uid"], "term": nm.get(a["dst"]["term_uid"]), "verify_term_uid": x.bind["term"].get(r["term_uid"], r["term_uid"]),
               "diagram": r["frame_diagram"], "owner_class": "", "term_class": ""}
        s.expect_is_broken_false("P2 " + d["id"], lambda e=end, y=ob.get(su, su), i=d["id"]: s.safe("2nd pass " + i, lambda: s.cfw_second_pass(y, e), {})[0])
    fb, fe = frames(BASE["terminals"]), frames(real)
    s.gate("FU frame-diagram uid sets of moved CaseStructures equal before/after, non-empty (181(b))", fb == fe and bool(fb), (fb, fe), fatal=True)
    s.es("after all rows (warm, RECORDED - the PB rows are open by design)")
    loops = copy.deepcopy(L["loops"])
    for lp in loops or []:                                                          # register table = the simulation's, via the binding
        lp["right_uids"], lp["left_of"] = [ob.get(int(u), int(u)) for u in lp.get("right_uids") or []], dict((str(ob.get(int(k), int(k))), [ob.get(int(y), int(y)) for y in (v if isinstance(v, list) else [v])]) for k, v in (lp.get("left_of") or {}).items())
    s1p = J(JC.WIKI, JC.S1_KEY + ".json")
    S1f = V.build4(s1p["terminals"], J(JC._newest("graph_objs_s1_*.json"))["objects"], J(JC._newest("graph_loops_s1_*.json"))["loops"], LAB, s1p["fs_tunnel_pairs"], frame_keyed=True)
    G1 = V.build4(real, getattr(be, "last_objs", None) or be.st["objs"], loops, LAB, BASE["fs_tunnel_pairs"], frame_keyed=True)
    cd = V.computation_diff_frame(S1f, G1)
    for y in cd["rows"]: s.fact("CDIFF ROW {0}".format(dict((k, V.show(v) if k == "sink" else v) for k, v in y.items())))  # noqa: E701
    got = sorted(set((V.key_parts(y["sink"])[0], V.key_parts(y["sink"])[2]) for y in cd["rows"]))
    want = sorted(set((int(y["node"]), y["term"]) for y in P["open_rows"]))
    s.gate("PB frame-keyed cdiff(S1, real end) == the plan's {0} open_rows (FATAL, before save)".format(len(want)), got == want,
           {"extra": sorted(set(got) - set(want)), "missing": sorted(set(want) - set(got))}, fatal=True)
    s.census(tag="after L2-A1")
    h1 = bp.labview_handles(); s.fact("PH handles RECORDED: post-open {0} -> before-save {1}".format(h0, h1))   # noqa: E702
    shot = lambda n: g._lv_gui("-Action", "shot", "-Out", '"{0}"'.format(os.path.join(K.BENCH, "stage_d1_l2a1_{0}_{1}.png".format(s.stamp, n))))  # noqa: E731
    m = (shot("before_save"), s.save(broken_ok=True), shot("after_save"))[1]
    s.gate("PS artefact saved, md5 differs from the input; input unchanged", m and m != s.input_md5 and K.md5(s.input_vi) == s.input_md5, m)
    if m and not DRY:                                                              # RBW on a throwaway scratch of the SAVED file
        rb = s.scratch("rbw", s.work); w0 = set(AT.all_wire_uids(rb)[0]); s.broken_wire_count(target=rb, tag="RBW")   # noqa: E702
        rows = AT.read_terms(rb, AT.OP_ALLTERMS_V1)[0]; gone = w0 - set(AT.all_wire_uids(rb)[0])                     # noqa: E702
        sinks = set(x.bind["term"].get(t, t) for t in (a["dst"]["term_uid"] for a in A if a["op"] == "wire" and isinstance(a["dst"], dict)))
        s.fact("RBW deleted {0}".format(sorted(gone)))
        s.gate("RBW deletes no wire of a re-wired sink (scratch of the saved file)", not [r for r in rows if r["term_uid"] in sinks and r["wire_uid"] in gone], sorted(gone))
        s.drop_scratch(rb, "RBW")
    _x = m and m != s.input_md5 and s.work in s.scratches and s.scratches.remove(s.work)   # noqa: F841
    s.R["l2a1"] = {"final": s.work, "md5": m, "bytes": os.path.exists(s.work) and os.path.getsize(s.work), "cdiff_rows": got, "handles": [h0, h1]}; s.dump()   # noqa: E702


if __name__ == "__main__":
    st = K.Stage(BASE["vi"], BASE["md5"], "D1_l2_a1", preload=False, deadline_min=75, out_json=os.path.join(K.BENCH, "stage_d1_l2a1.json"), task="card 81-6")
    rc = K.run(body, st)
    if not DRY:
        subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4.0)   # noqa: E702
        print("LabVIEW gone at exit:", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower(), flush=True)
    sys.exit(rc)
