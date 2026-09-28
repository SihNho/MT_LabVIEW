r"""stage_d1_l2r2 - card 116-2 L2-R2 (PD228(f)(g), PD230(f)): RETIRE the 13 consumer-less LoopTunnels on #637 (#32572 stays) from the R1 bed D1_l2_r1_20260928_055441.vi,
FRESH LabVIEW -> claudeDev\D1_l2_r2_<ts>.vi (rule-6 GUI save, ExecState 0 by design, never run). ROWS ONLY FROM plan_l2r2.json (plan_l2r2_make.py on the SAVED R1 graph):
per tunnel, delete_wire of its inner stub, then delete_object. PRIOR ART: stage_d1_l2r1.py (its cut: SR pairs -> tunnels; Executor RECORD MODE, RetireGuardBE, D4 EMPTY).
PREDICTION (plan_l2r2_pred.json): L1 24 ops (11 + 13); LC x13; E1 == sim; D new 0, lost == 11 stubs; FU; CEN lost == 13 tunnels; census LoopTunnel -13, Wire -11, rest 0;
ENDS 13 shared nets; TD only the 13 tunnels' 26 rows go, each wire's list == base minus them; PB cdiff == R1's 16 rows; HF +-100; RBW(new) <= RBW(bed); PS.
    py tools/bgrun.py --material --max-min 50 --log tools/bench/stage_d1_l2r2.log -- py -u tools/recipes/stage_d1_l2r2.py"""
import copy, json, os, sys                                                         # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, vigraph as V, stagexec as SX, jev_candidates as JC, allterms as AT  # noqa: E401,E402
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                 # noqa: E731
PLAN = os.path.join(K.BENCH, "plan_l2r2.json")                                      # ONE literal: stage_prerun.plan_files reads it
P = J(PLAN); BASE = J(K.ROOT, P["finalized"]["base"]["path"]); A = P["actions"]   # noqa: E702
PRED, D4 = J(K.BENCH, "plan_l2r2_pred.json"), K.d4_load(os.path.join(K.BENCH, "plan_l2r2_d4.json"))
DRY, LAB, SAVE = bool(getattr(g.report_all, "_dry", False)), JC.node_labels_default(), True
RETIRE = set(int(a["uid"]) for a in A if a["op"] == "delete_object"); PAIRS = dict((u, [u]) for u in RETIRE)   # noqa: E702 (a tunnel delete removes it only)
ZL, KEEP = J(K.BENCH, "facts_c114e_inventory.json")["zero_live_tunnels"], int(PRED["keep"])   # prerun X6: no re-typed uid, the loop comes from the rows
LOOPS = set(int(t.get("owner_loop") or 0) for t in ZL if int(t["uid"]) in RETIRE); INV = set(int(t["uid"]) for t in ZL if int(t.get("owner_loop") or 0) in LOOPS)   # noqa: E702
R1END, R1REAL = P["finalized"]["end_cdiff_rows"], set((int(k.split("|")[0]), k.split("|")[2]) for k in J(K.BENCH, "stage_d1_l2r1.json")["l2r1"]["cdiff_rows"])   # REAL R1 end
SRC = ("RightShiftRegister", "LeftShiftRegister", "WhileLoop", "Diagram", "SubVI", "LoopTunnel", "Local", "ControlTerminal", "Wire", "Node")
wires, frames = (lambda rows: set(int(r["wire_uid"]) for r in rows if r["wire_uid"])), (lambda rows: set(int(r["frame_diagram"] or 0) for r in rows))
nodes = lambda rows: set(int(r["owner_uid"]) for r in rows)                          # noqa: E731
RW = set(int(r["wire_uid"]) for r in BASE["terminals"] if r["wire_uid"] and int(r["owner_uid"]) in RETIRE)   # wires with an end on a retired node
STUBS = set(w for w in RW if all(int(r["owner_uid"]) in RETIRE for r in BASE["terminals"] if int(r["wire_uid"] or 0) == w))   # every end retired
DW = [int(a["wire_uid"]) for a in A if a["op"] == "delete_wire"]
termlists = lambda rows: dict((w, set((int(r["term_uid"]), bool(r["is_source"])) for r in rows if int(r["wire_uid"] or 0) == w)) for w in wires(rows))   # noqa: E731


def rbw(s, target, tag):
    w0 = set(AT.all_wire_uids(target)[0]); s.broken_wire_count(target=target, allow_mutation=True, tag=tag)   # noqa: E702
    return w0 - set(AT.all_wire_uids(target)[0])


def body(s):
    print(__doc__, flush=True)
    s.gate("L0 plan FINAL, open_rows_match, plan_in = plan_l2r2_in, base md5 == pred graph md5; finalized end's pairs == the REAL R1 end's (stage_d1_l2r1.json)",
           P.get("final") is True and P["finalized"].get("open_rows_match") is True and os.path.splitext(P["finalized"]["plan_in"]["path"])[0].endswith("plan_l2r2_in")
           and set((int(k.split("|")[0]), k.split("|")[2]) for k in R1END) == R1REAL and sorted(R1END) == PRED["cdiff_rows"] and P["finalized"]["base"]["md5"] == PRED["graph"]["md5"]
           == K.md5(os.path.join(K.ROOT, P["finalized"]["base"]["path"])), (K.md5(PLAN), len(R1END), len(R1REAL)), fatal=True)
    s.gate("L0b D4 cites S1 md5 {0}, scope EMPTY (grants nothing), plan md5 pinned".format(D4["s1"]["md5"]),
           D4["s1_md5_got"] == D4["s1"]["md5"] and not D4["scope"] and D4["plan_md5"] == K.md5(PLAN), (D4["s1_md5_got"], D4["plan_md5"]), fatal=True)
    s.gate("L0c 13 tunnels, ONE owner loop {0}, == inventory zero_live_tunnels on it minus the kept #{1} == pred retire set".format(sorted(LOOPS), KEEP), len(LOOPS) == 1
           and RETIRE == INV - {KEEP} == set(PRED["retire"]) and len(RETIRE) == 13 and KEEP in INV, sorted(RETIRE ^ (INV - {KEEP})), fatal=True)
    s.gate("L0d the plan's delete_wire rows == the stubs whose EVERY terminal is on a retired node ({0}) == pred stubs, each once".format(len(STUBS)),
           sorted(DW) == sorted(STUBS) == sorted(PRED["stubs"]) and len(DW) == len(set(DW)), {"plan": sorted(DW), "stubs": sorted(STUBS)}, fatal=True)
    s.start(); s.discard_work(); bp = K.mod("bench_prep"); h0 = bp.labview_handles(); c0 = s.census(SRC, tag="before L2-R2")   # noqa: E702
    be = SX.DryPlanBE(s, P, PLAN, BASE) if DRY else SX.LVBackend(s, BASE["fs_tunnel_pairs"], sink_gates=[], gates={}, mem_stop_mb=SX.MEM_STOP_MB)
    gb = SX.RetireGuardBE(be, s, PAIRS, (lambda: [dict(r) for r in be.st["terminals"]]) if DRY else be.read)
    x = SX.Executor(PLAN, gb, log=lambda m: print(m, flush=True), checkpoints=tuple(range(len(A) + 1)), record=True)
    s.gate("L1 the {0} actions compile into {1} real ops (delete_wire / delete_object only, 13 delete_object), each action once".format(len(A), len(x.ops)),
           [o["kind"] for o in x.ops] == [a["op"] for a in A] and [a["op"] for a in A].count("delete_object") == 13 and set(a["op"] for a in A) <= {"delete_wire", "delete_object"}
           and sorted(n for o in x.ops for n in o["acts"]) == list(range(1, len(A) + 1)), [o["kind"] for o in x.ops], fatal=True)
    try:
        real = x.run()
    except SX.ExecStop as e:
        return SX.report_stop(s, x, be, e)
    s.gate("LC all 13 live-consumer checks PASS (each re-read before its delete)", len(gb.checks) == 13 and all(c["ok"] for c in gb.checks), gb.checks)
    nm = dict((int(r["term_uid"]), (int(r["owner_uid"]), r["term_name"])) for k in range(len(A) + 1) for r in x.step(k)["state"]["terminals"])
    nm.update((int(r["term_uid"]), (int(r["owner_uid"]), r["term_name"])) for r in real)
    e1ok, acc, bad = K.d4_e1([(d["k"], d["diff"]) for d in x.diffs], nm, D4)
    s.gate("E1 every checkpoint's real graph == its simulated step (D4 scope empty = exact)", e1ok and not acc, {"bad": bad[:40], "accepted": acc}, fatal=True)
    s.R["stagexec"] = x.report
    DRY or s.fact("METER SUMMARY {0}".format(json.dumps(be.meter.summary(), default=str)))
    L = x.step(len(A))["state"]
    sim_new, sim_lost = wires(L["terminals"]) - wires(BASE["terminals"]), wires(BASE["terminals"]) - wires(L["terminals"])
    new, lost = wires(real) - wires(BASE["terminals"]), wires(BASE["terminals"]) - wires(real)
    s.gate("D the end adds {0} wire(s) and loses exactly the simulated {1} stub(s)".format(len(sim_new), len(sim_lost)), new == sim_new == set() and lost == sim_lost == STUBS,
           {"new": sorted(new)[:20], "lost": sorted(lost), "sim_lost": sorted(sim_lost)})
    s.gate("FU the set of frame diagrams is unchanged", frames(BASE["terminals"]) == frames(real), sorted(frames(BASE["terminals"]) ^ frames(real))[:20], fatal=True)
    s.gate("CEN terminal-graph nodes lost == the retire set exactly, none added", nodes(BASE["terminals"]) - nodes(real) == RETIRE and not nodes(real) - nodes(BASE["terminals"]),
           {"lost": sorted(nodes(BASE["terminals"]) - nodes(real)), "added": sorted(nodes(real) - nodes(BASE["terminals"]))})
    c1 = s.census(SRC, tag="after L2-R2")
    dc = dict((k, (c1.get(k) or 0) - (c0.get(k) or 0)) for k in SRC)
    s.gate("CEN2 class census: LoopTunnel -13, Wire -{0} (the deleted stubs), SR/WhileLoop/Diagram/SubVI/Local/ControlTerminal/Node 0".format(len(DW)),
           DRY or (dc["LoopTunnel"] == -13 and dc["Wire"] == -len(DW) and not any(dc[k] for k in SRC if k not in ("LoopTunnel", "Wire"))), dc)
    eok, ed = SX.retire_ends(BASE["terminals"], real, RETIRE)
    s.gate("ENDS every net shared by a retired and a kept terminal keeps its uid, its source(s) and its kept sinks ({0} nets)".format(len(ed["shared_wires"])), eok, ed)
    tb, tr, gone = termlists(BASE["terminals"]), termlists(real), set(PRED["terminal_rows_lost"])
    tdbad = [(w, sorted(tb.get(w, ())), sorted(tr.get(w, ()))) for w in set(tb) | set(tr) if set(t for t in tb.get(w, ()) if t[0] not in gone) != tr.get(w, set())
             and not (w in STUBS and w not in tr)]
    rows_lost = set(int(r["term_uid"]) for r in BASE["terminals"]) - set(int(r["term_uid"]) for r in real)
    s.gate("TD whole-graph terminal-list diff: rows lost == the 13 tunnels' {0} rows, none added; each wire's list == base minus retired terminals".format(len(gone)),
           rows_lost == gone and not set(int(r["term_uid"]) for r in real) - set(int(r["term_uid"]) for r in BASE["terminals"]) and not tdbad, {"bad": tdbad[:20], "rows_lost_extra": sorted(rows_lost ^ gone)[:20]})
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
    s.gate("PB frame-keyed cdiff(S1, real end) == R1's {0} rows exactly (no row added or removed; FATAL, before save)".format(len(R1END)),
           pbok and rk == sorted(R1END) and gs == R1REAL, {"bad": pbad[:30], "extra": sorted(set(rk) - set(R1END)), "missing": sorted(set(R1END) - set(rk)), "vs_r1_real": sorted(gs ^ R1REAL)}, fatal=True)
    h1, mr = (None, []) if DRY else (bp.labview_handles(), [r for r in be.meter.rows if r["tag"] == "read" and r["handles"] is not None])
    hs = [r["handles"] for r in mr if r["k"] == 1][:1] + [mr[-1]["handles"]] if mr else []
    s.fact("HF handles: start {0} -> end {1}; steady state read k1 -> last read {2}".format(h0, h1, hs))
    s.gate("HF handle count flat (+-100) in steady state, from the read after op 1 to the last read", DRY or (len(hs) == 2 and abs(hs[1] - hs[0]) <= 100), hs)
    m = s.save(broken_ok=True) if SAVE else None
    SAVE and s.gate("PS artefact saved, md5 differs from the input; input unchanged", m and m != s.input_md5 and K.md5(s.input_vi) == s.input_md5, m)
    DRY and print("GATE RBW NOT RUNNABLE IN DRY: Remove Bad Wires (VI method 410) runs inside LabVIEW", flush=True)
    if not DRY and (m or not SAVE):
        rn = s.scratch("rbw", s.work) if SAVE else s.work                             # SAVE=False: the work copy IS a scratch
        gn = rbw(s, rn, "RBW(new)")
        rb = s.scratch("rbwbed", s.input_vi); gb_ = rbw(s, rb, "RBW(bed)")             # noqa: E702
        s.fact("RBW(new) deleted {0}; RBW(bed) deleted {1}".format(sorted(gn), sorted(gb_)))
        live = set(ed["shared_wires"])
        s.gate("RBW RBW(new) deletes nothing RBW(bed) keeps and no shared live net; RBW(bed) - RBW(new) only wires with an end on a retired node",
               not (gn - gb_) and not (gn & live) and (gb_ - gn) <= RW, {"new_only": sorted(gn - gb_), "live_hit": sorted(gn & live), "bed_only": sorted(gb_ - gn), "bed_only_not_retired": sorted((gb_ - gn) - RW)})
        SAVE and s.drop_scratch(rn, "RBW"); s.drop_scratch(rb, "RBW-bed")           # noqa: E702
    _x = m and m != s.input_md5 and s.work in s.scratches and s.scratches.remove(s.work)   # noqa: F841
    s.R["l2r2"] = {"final": s.work if m else None, "md5": m, "bytes": (not DRY) and bool(m) and os.path.getsize(s.work), "cdiff_rows": rk, "handles": [h0, h1], "census_delta": dc,
                   "lc": gb.checks, "level": "STRUCTURAL, broken by design, never run"}; s.dump()   # noqa: E702


if __name__ == "__main__":
    st = K.Stage(BASE["vi"], BASE["md5"], "D1_l2_r2", preload=False, deadline_min=50, out_json=os.path.join(K.BENCH, "stage_d1_l2r2.json"), task="card 116-2")
    rc = K.run(body, st)
    DRY or SX.kill_labview_at_exit()
    sys.exit(rc)
