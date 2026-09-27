r"""stage_d1_l2r1 - card 115-2: STAGE L2-R1 (split plan PD228(g)(h)(j), PD229(d)): RETIRE the 6 dead shift-register pairs on loop #637 (facts_c114e_inventory.json:
0 live consumers each). INPUT the B3 bed D1_l2_b3_20260928_032703.vi, FRESH LabVIEW -> claudeDev\D1_l2_r1_<ts>.vi (rule-6 GUI save, ExecState 0 by design, never run).
ROWS ONLY FROM plan_l2r1.json: per pair, delete_wire of its stub wires (every terminal on the pair; R2 scratch run 1 measured delete_object leaves them as Wire
objects), then delete_object on the RIGHT register (Left goes with it, delete_object.json sr_pair). PRIOR ART: stage_d1_l2b3.py (its cut: RECORD MODE, D4 EMPTY
scope = exact), stage_d1_l7_r.py (retire + RBW), stagexec.RetireGuardBE (live-consumer gate re-read BEFORE EACH delete). SAVE=False (diag_c115b_scratch.py) = R2.
PREDICTION: L1 17 ops (11 delete_wire + 6 delete_object); LC x6; E1 == sim each checkpoint; D new 0, lost == sim's 11 stubs; FU; CEN nodes lost == 12 SR uids;
census SR -6/-6, Wire -11, others 0; ENDS 7 shared nets keep uid/source/sinks; PB cdiff == B3's 16 rows; HF +-100; RBW(new) <= RBW(bed), difference retired; PS.
    py tools/bgrun.py --material --max-min 50 --log tools/bench/stage_d1_l2r1.log -- py -u tools/recipes/stage_d1_l2r1.py"""
import copy, json, os, sys                                                         # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, vigraph as V, stagexec as SX, jev_candidates as JC, allterms as AT  # noqa: E401,E402
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                 # noqa: E731
PLAN = os.path.join(K.BENCH, "plan_l2r1.json")                                      # ONE literal: stage_prerun.plan_files reads it
P = J(PLAN); BASE = J(K.ROOT, P["finalized"]["base"]["path"]); A = P["actions"]   # noqa: E702
DRY, LAB, SAVE = bool(getattr(g.report_all, "_dry", False)), JC.node_labels_default(), True
D4 = K.d4_load(os.path.join(K.BENCH, "plan_l2r1_d4.json"))
LOOP = dict((int(a["uid"]), L) for a in A if a["op"] == "delete_object" for L in BASE["loops"] if str(a["uid"]) in (L.get("left_of") or {}))   # Right -> its loop
PAIRS = dict((u, [u] + [int(x) for x in L["left_of"][str(u)]]) for u, L in LOOP.items())
RETIRE = set(u for v in PAIRS.values() for u in v)
INV = dict((int(c["uid"]), c["live_consumers_n"]) for c in J(K.BENCH, "facts_c114e_inventory.json")["candidates"] if c.get("found"))
B3END = P["finalized"]["end_cdiff_rows"]                                             # == plan_l2b3's finalized end (diag_c115b_r1.log R1a)
B3REAL = set(tuple(p) for p in J(K.BENCH, "stage_d1_l2b3.json")["l2b3"]["cdiff_rows"])   # the REAL B3 end's (node, sink name) pairs
SRC = ("RightShiftRegister", "LeftShiftRegister", "WhileLoop", "Diagram", "SubVI", "LoopTunnel", "Local", "ControlTerminal", "Wire", "Node")
wires, frames = (lambda rows: set(int(r["wire_uid"]) for r in rows if r["wire_uid"])), (lambda rows: set(int(r["frame_diagram"] or 0) for r in rows))
nodes = lambda rows: set(int(r["owner_uid"]) for r in rows)                          # noqa: E731
RW = set(int(r["wire_uid"]) for r in BASE["terminals"] if r["wire_uid"] and int(r["owner_uid"]) in RETIRE)   # wires with an end on a retired node
STUBS = set(w for w in RW if all(int(r["owner_uid"]) in RETIRE for r in BASE["terminals"] if int(r["wire_uid"] or 0) == w))   # every end retired
DW = [int(a["wire_uid"]) for a in A if a["op"] == "delete_wire"]


def rbw(s, target, tag):
    w0 = set(AT.all_wire_uids(target)[0]); s.broken_wire_count(target=target, allow_mutation=True, tag=tag)   # noqa: E702
    return w0 - set(AT.all_wire_uids(target)[0])


def body(s):
    print(__doc__, flush=True)
    s.gate("L0 plan FINAL, open_rows_match, plan_in = plan_l2r1_in; its finalized end's (node, name) pairs == the REAL B3 end's (stage_d1_l2b3.json)", P.get("final") is True
           and P["finalized"].get("open_rows_match") is True and os.path.splitext(P["finalized"]["plan_in"]["path"])[0].endswith("plan_l2r1_in")
           and set((int(k.split("|")[0]), k.split("|")[2]) for k in B3END) == B3REAL, (K.md5(PLAN), len(B3END), len(B3REAL)), fatal=True)
    s.gate("L0b D4 cites S1 md5 {0}, scope EMPTY (grants nothing), plan md5 pinned".format(D4["s1"]["md5"]),
           D4["s1_md5_got"] == D4["s1"]["md5"] and not D4["scope"] and D4["plan_md5"] == K.md5(PLAN), (D4["s1_md5_got"], D4["plan_md5"]), fatal=True)
    s.gate("L0c 6 register pairs from ONE loop's register table ({0}) == 12 inventory uids, each with 0 live consumers (facts_c114e_inventory.json)".format(
           sorted(set(int(L["loop_uid"]) for L in LOOP.values()))), len(PAIRS) == 6 and len(set(int(L["loop_uid"]) for L in LOOP.values())) == 1
           and all(len(v) == 2 for v in PAIRS.values()) and all(INV.get(u) == 0 for u in RETIRE) and len(RETIRE) == 12, PAIRS, fatal=True)
    s.gate("L0d the plan's delete_wire rows == the stubs whose EVERY terminal is on a retired node ({0}), each once".format(len(STUBS)),
           sorted(DW) == sorted(STUBS) and len(DW) == len(set(DW)), {"plan": sorted(DW), "stubs": sorted(STUBS)}, fatal=True)
    s.start(); s.discard_work(); bp = K.mod("bench_prep"); h0 = bp.labview_handles(); c0 = s.census(SRC, tag="before L2-R1")   # noqa: E702
    be = SX.DryPlanBE(s, P, PLAN, BASE) if DRY else SX.LVBackend(s, BASE["fs_tunnel_pairs"], sink_gates=[], gates={}, mem_stop_mb=SX.MEM_STOP_MB)
    gb = SX.RetireGuardBE(be, s, PAIRS, (lambda: [dict(r) for r in be.st["terminals"]]) if DRY else be.read)
    x = SX.Executor(PLAN, gb, log=lambda m: print(m, flush=True), checkpoints=tuple(range(len(A) + 1)), record=True)
    s.gate("L1 the {0} actions compile into {1} real ops (delete_wire / delete_object only, 6 delete_object), each action once".format(len(A), len(x.ops)),
           [o["kind"] for o in x.ops] == [a["op"] for a in A] and [a["op"] for a in A].count("delete_object") == 6 and set(a["op"] for a in A) <= {"delete_wire", "delete_object"}
           and sorted(n for o in x.ops for n in o["acts"]) == list(range(1, len(A) + 1)), [o["kind"] for o in x.ops], fatal=True)
    try:
        real = x.run()
    except SX.ExecStop as e:
        return SX.report_stop(s, x, be, e)
    s.gate("LC all 6 live-consumer checks PASS (each re-read before its delete)", len(gb.checks) == 6 and all(c["ok"] for c in gb.checks), gb.checks)
    nm = dict((int(r["term_uid"]), (int(r["owner_uid"]), r["term_name"])) for k in range(len(A) + 1) for r in x.step(k)["state"]["terminals"])
    nm.update((int(r["term_uid"]), (int(r["owner_uid"]), r["term_name"])) for r in real)
    e1ok, acc, bad = K.d4_e1([(d["k"], d["diff"]) for d in x.diffs], nm, D4)
    s.gate("E1 every checkpoint's real graph == its simulated step (D4 scope empty = exact)", e1ok and not acc, {"bad": bad[:40], "accepted": acc}, fatal=True)
    s.R["stagexec"] = x.report
    DRY or s.fact("METER SUMMARY {0}".format(json.dumps(be.meter.summary(), default=str)))
    L = x.step(len(A))["state"]
    sim_new, sim_lost = wires(L["terminals"]) - wires(BASE["terminals"]), wires(BASE["terminals"]) - wires(L["terminals"])
    new, lost = wires(real) - wires(BASE["terminals"]), wires(BASE["terminals"]) - wires(real)
    s.gate("D the end adds {0} wire(s) and loses exactly the simulated {1} stub(s)".format(len(sim_new), len(sim_lost)), new == sim_new and lost == sim_lost,
           {"new": sorted(new)[:20], "lost": sorted(lost), "sim_lost": sorted(sim_lost)})
    s.gate("FU the set of frame diagrams is unchanged", frames(BASE["terminals"]) == frames(real), sorted(frames(BASE["terminals"]) ^ frames(real))[:20], fatal=True)
    s.gate("CEN terminal-graph nodes lost == the retire set exactly, none added", nodes(BASE["terminals"]) - nodes(real) == RETIRE and not nodes(real) - nodes(BASE["terminals"]),
           {"lost": sorted(nodes(BASE["terminals"]) - nodes(real)), "added": sorted(nodes(real) - nodes(BASE["terminals"]))})
    c1 = s.census(SRC, tag="after L2-R1")
    dc = dict((k, (c1.get(k) or 0) - (c0.get(k) or 0)) for k in SRC)
    s.gate("CEN2 class census: RightShiftRegister -6, LeftShiftRegister -6, Wire -{0} (the deleted stubs), WhileLoop/Diagram/SubVI/LoopTunnel/Local/ControlTerminal/Node 0".format(len(DW)),
           DRY or (dc["RightShiftRegister"] == -6 and dc["LeftShiftRegister"] == -6 and dc["Wire"] == -len(DW) and not any(dc[k] for k in SRC[2:8] + ("Node",))), dc)
    eok, ed = SX.retire_ends(BASE["terminals"], real, RETIRE)
    s.gate("ENDS every net shared by a retired and a kept terminal keeps its uid, its source(s) and its kept sinks ({0} nets)".format(len(ed["shared_wires"])), eok, ed)
    s.es("after all rows (ExecState 0 expected, PD228(h))")
    loops = copy.deepcopy(L["loops"])
    s1p = J(JC.WIKI, JC.S1_KEY + ".json")
    S1f = V.build4(s1p["terminals"], J(JC._newest("graph_objs_s1_*.json"))["objects"], J(JC._newest("graph_loops_s1_*.json"))["loops"], LAB, s1p["fs_tunnel_pairs"], frame_keyed=True)
    G1 = V.build4(real, getattr(be, "last_objs", None) or be.st["objs"], loops, LAB, BASE["fs_tunnel_pairs"], frame_keyed=True)
    cd = V.computation_diff_frame(S1f, G1)
    for y in cd["rows"]: s.fact("CDIFF ROW {0}".format(dict((k, V.show(v) if k == "sink" else v) for k, v in y.items())))  # noqa: E701
    gs, ws = set((int(y["node"]), str(y["sink"]).split("|")[2]) for y in cd["rows"]), set((int(y["node"]), y["term"]) for y in P["open_rows"])
    pbok, closed, grown, pbad = K.d4_pb(gs, ws, real, SX.translate(L["terminals"], x.bind), D4)
    rk = sorted(str(y["sink"]) for y in cd["rows"])
    s.gate("PB frame-keyed cdiff(S1, real end) == B3's {0} rows exactly (no row added or removed; FATAL, before save)".format(len(B3END)),
           pbok and rk == sorted(B3END) and gs == B3REAL, {"bad": pbad[:30], "extra": sorted(set(rk) - set(B3END)), "missing": sorted(set(B3END) - set(rk)), "vs_b3_real": sorted(gs ^ B3REAL)}, fatal=True)
    h1 = None if DRY else bp.labview_handles()
    mr = [] if DRY else [r for r in be.meter.rows if r["tag"] == "read" and r["handles"] is not None]
    hs = [r["handles"] for r in mr if r["k"] == 1][:1] + [mr[-1]["handles"]] if mr else []
    s.fact("HF handles: start {0} -> end {1}; steady state read k1 -> last read {2}".format(h0, h1, hs))
    s.gate("HF handle count flat (+-100) in steady state, from the read after op 1 to the last read", DRY or (len(hs) == 2 and abs(hs[1] - hs[0]) <= 100), hs)
    m = s.save(broken_ok=True) if SAVE else None
    SAVE and s.gate("PS artefact saved, md5 differs from the input; input unchanged", m and m != s.input_md5 and K.md5(s.input_vi) == s.input_md5, m)
    if DRY:
        print("GATE RBW NOT RUNNABLE IN DRY: Remove Bad Wires (VI method 410) runs inside LabVIEW", flush=True)
    elif m or not SAVE:
        rn = s.scratch("rbw", s.work) if SAVE else s.work                             # SAVE=False: the work copy IS a scratch
        gn = rbw(s, rn, "RBW(new)")
        rb = s.scratch("rbwbed", s.input_vi); gb_ = rbw(s, rb, "RBW(bed)")             # noqa: E702
        s.fact("RBW(new) deleted {0}; RBW(bed) deleted {1}".format(sorted(gn), sorted(gb_)))
        live = set(ed["shared_wires"])
        s.gate("RBW RBW(new) deletes nothing RBW(bed) keeps and no shared live net; RBW(bed) - RBW(new) only wires with an end on a retired node",
               not (gn - gb_) and not (gn & live) and (gb_ - gn) <= RW, {"new_only": sorted(gn - gb_), "live_hit": sorted(gn & live), "bed_only": sorted(gb_ - gn), "bed_only_not_retired": sorted((gb_ - gn) - RW)})
        SAVE and s.drop_scratch(rn, "RBW")
        s.drop_scratch(rb, "RBW-bed")
    _x = m and m != s.input_md5 and s.work in s.scratches and s.scratches.remove(s.work)   # noqa: F841
    s.R["l2r1"] = {"final": s.work if m else None, "md5": m, "bytes": (not DRY) and bool(m) and os.path.getsize(s.work), "cdiff_rows": rk, "handles": [h0, h1], "census_delta": dc,
                   "lc": gb.checks, "level": "STRUCTURAL, broken by design, never run"}; s.dump()   # noqa: E702


if __name__ == "__main__":
    st = K.Stage(BASE["vi"], BASE["md5"], "D1_l2_r1", preload=False, deadline_min=50, out_json=os.path.join(K.BENCH, "stage_d1_l2r1.json"), task="card 115-2")
    rc = K.run(body, st)
    DRY or SX.kill_labview_at_exit()
    sys.exit(rc)
