# ---
# labview: build
# hardware: none
# ---
r"""stage_d1_ring_p5s01a - card 154-a3-2b (WRITTEN, NOT LAUNCHED), RING P5-1a (docs/d1/ring-p5.md PD374(a)(c)(e), PD376(a)): on the ADOPTED
s09 file (claudeDev\D1_ring_p4s09_20261009_060515.vi eb1d0f31, path/md5 read from the plan's base graph), apply the actions of plan_ring_p5s01a.json
= the first 20 actions / 14 ops of P5-1 form S (card 154-a3-2 plan_ring_p5s01.json, cut at the longest op prefix with X10 MAIN <= 680:
MAIN 677.3 at the start 602.6 = measured s09 load 596.7 + op-0 read), planned DIRECTLY on the real s09 graph 22f967b5 (tools/bench/prep_c154_a3_2b_mk.py,
no rebase). X11 / licence plan_ring_p5s01a_licence.json (tools/bench/prep_c154_a3_2b_licence.py).
COPIED from stage_d1_ring_p4_s09v18.py (4be3ff28) with ONLY: plan / pred / licence / session-census names, card id, out json, stage name
(saved file D1_ring_p5s01a_<ts>.vi), result key, docstring. Every gate unchanged (FR keeps `(on or NC == 0)`; P5-1a creates objects, so `on`
must be non-empty by the same expression).
Sink gates: one per census row through wire_indicators, read by script - prep_c154_a3_2b_session.json has ZERO such rows.
FRESH LabVIEW -> claudeDev\D1_ring_p5s01a_<ts>.vi (rule-6 GUI save, ExecState 0 by design) = an
IN-BETWEEN file of step P5 (not counted, D-2026-10-02-02/04). The FIRST run is the full SCRATCH run on a byte copy
(stage_d1_ring_p5s01a_scratch.py).
ROWS ONLY FROM plan_ring_p5s01a.json; expected values only from plan_ring_p5s01a_pred.json. No new op.
(PD366(e)): one declared sink gate PER row of prep_c154_a3_2b_session.json `sink_gate_census` with needs_sink_gate (read by
script; measured 0: the census has no ControlTerminal sink), each with PD355(b)'s pass
rule (sg_read (a)-(d), unchanged); a symbolic source would be resolved on the plan's simulated END state by stagesim.resolve_addr.
PREDICTION (numbers in the pred file): SG one declared sink gate per census row; L1 actions -> pred ops; E1 every checkpoint == sim; NG crossing tunnel names == step files';
PRIM every created primitive's label == plan prim; FR created objects on the sim end's frames; D new/lost wires == sim's; TD every base
terminal that was wired stays wired, identities lost == plan deletes; CEN2 == pred census; PB cdiff(S1, end) == pred rows (FATAL, before save); HB handles <= +700;
PS saved, input unchanged. X10 = pred memory_pred. Error List of the end = a RECORDED cross-check against pred errorlist (PD354(a)).
    py tools/bgrun.py --material --max-min 50 --log tools/bench/launch_c154_p5s01a.log -- py -u tools/recipes/stage_d1_ring_p5s01a.py"""
import copy, json, os, re, sys                                                     # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, vigraph as V, stagexec as SX, jev_candidates as JC, allterms as AT   # noqa: E401,E402
import stagesim as SSIM                                                             # noqa: E402  card 150-a3-1: resolve_addr for a symbolic sink-gate source
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                 # noqa: E731
PLAN = os.path.join(K.BENCH, "plan_ring_p5s01a.json")                              # ONE literal: stage_prerun.plan_files reads it
P = J(PLAN); BASE = J(K.ROOT, P["finalized"]["base"]["path"]); A = P["actions"]   # noqa: E702
PRED = J(K.BENCH, "plan_ring_p5s01a_pred.json")
REN = K.licence_renames(J(K.BENCH, "plan_ring_p5s01a_licence.json"))             # card 150-a3-1 (PD365(d)): the licence's `renames`, read from the file
NC =sum(1 for a in A if a["op"] == "create" and a.get("as"))                       # created objects, from the plan (FR gate)
DRY, LAB, SAVE = bool(getattr(g.report_all, "_dry", False)), JC.node_labels_default(), True
SRC = tuple(PRED["census"])
BIND = set(k for k, o in enumerate(SX.compile_plan(P), 1) if o["kind"] in SX.BIND_KINDS)   # card 129-8 PD265(c): every op that creates/binds an object
CHECKPOINTS = tuple(sorted({0, len(SX.compile_plan(P))} | BIND))                  # as stage_d1_l2b3.py:16-18 (stagexec refuses a set missing a bind op)
FSPAIRS = BASE.get("fs_tunnel_pairs", BASE.get("fs_pairs"))                         # a real graph / the provisional simulated state
wires = lambda rows: set(int(r["wire_uid"]) for r in rows if r["wire_uid"])        # noqa: E731
frames = lambda rows: set(int(r["frame_diagram"] or 0) for r in rows)              # noqa: E731
snap = lambda s: dict((u, c) for u, c in s.census_snapshot().items() if c in SRC)   # noqa: E731
# card 147-a2-1 (PD355(b)): recipe-owned SINK GATES (stagexec.check_sink_gates / sink_gate_for, card 80-3; pattern stage_d1_l2a2.py:34-47).
# gscript.wire_indicators raises after wiring whenever ExecState != 1 (gscript.py:2148-2155) and this bed is ExecState 0 by design; the op
# error on each declared sink is deferred to its gate, which READS the wire back after the run (stagexec.py:2782-2789). Rows come from the plan.
# card 147-a1-7 (X6): each sink is DERIVED from its plan row's dst term in the base graph - no uid / terminal name typed here.
# card 147-a1-7 (X10): sg_read makes NO whole-VI read of its own; it uses the executor's final read (after the last op, stagexec.py:2385-2390,
# kept by SGBackend.read) and checks that this read is the one after the last op (x.reads_real[-1] == len(x.ops)).
# card 150-a3-6 (PD366(e)): the rows are READ from the session census (prep_c152_b2_1_session.json sink_gate_census, needs_sink_gate) - not typed.
SG_CENSUS_FILE = os.path.join(K.BENCH, "prep_c154_a3_2b_session.json")
SG_CENSUS = [e for e in J(SG_CENSUS_FILE).get("sink_gate_census") or [] if e.get("needs_sink_gate")]
SIM_END = J(K.ROOT, P["finalized"]["step_files"][-1]["path"])["state"]             # the plan's simulated end (resolves a symbolic source)


def _sg_spec(e):
    """One census row -> its declared sink gate spec: acts (the plan's wire row), terms (base dst term), sinks (owner, name) from BASE,
    src_name (the source terminal's name: BASE for a numeric source, the simulated end for a symbolic 'new:' source)."""
    acts = [a for a in A if a.get("id") == e["id"] and a["op"] == "wire" and isinstance(a.get("dst"), dict)]   # a symbolic dst is a str
    terms = sorted(set(a["dst"]["term_uid"] for a in acts))
    sinks = sorted(set((r["owner_uid"], r["term_name"]) for r in BASE["terminals"] if r["term_uid"] in terms))
    src = acts[0]["src"] if acts else None
    if isinstance(src, dict):
        sname = sorted(set(r["term_name"] for r in BASE["terminals"] if r["term_uid"] == src["term_uid"]))
    elif isinstance(src, str) and src.startswith("new:"):
        try:
            sname = [SSIM.resolve_addr(SIM_END, src, True)["term_name"]]
        except Exception as ex:                                                     # noqa: BLE001 - the SG gate reports it
            sname = ["UNRESOLVED: {0!r}".format(ex)]
    else:
        sname = []
    sink = list(sinks[0]) if len(sinks) == 1 else None                             # the sink key exactly as the run reports it
    slug = re.sub(r"[^a-z0-9]+", "-", str(sink[1] if sink else "").lower()).strip("-")
    return {"n": e["n"], "row": e["id"], "gate": "SG-{0}-{1}".format(e["id"], slug), "acts": acts, "terms": terms, "sink": sink,
            "census_sink": list(e["sink"]), "src_name": sname}


SGS = [_sg_spec(e) for e in SG_CENSUS]
EX = {}                                                                             # s, x and be, set in body (the gate needs the binding)


class SGBackend(SX.LVBackend):
    """LVBackend that KEEPS its last whole-VI read (no extra read; stagexec.LVBackend.read is called exactly as before)."""

    def read(self):
        self.last_terms = SX.LVBackend.read(self)
        return self.last_terms


def sg_read(e, d):
    """(ok, detail) for the deferred op error on sink d['sink']: (a) the indicator terminal exists with exactly ONE wire, (b) that wire is the
    net of the plan source (through x.bind; a symbolic source resolved on the simulated end), (c) that net has exactly ONE source = that
    terminal, (d) the rows are the executor's whole-VI read after its LAST op. Unchanged from the s06 recipe's sg_read except the spec `d`."""
    if DRY:
        return True, "dry"
    x, a = EX["x"], d["acts"][0]
    tb, ob = (lambda t: x.bind["term"].get(t, t)), (lambda u: x.bind["obj"].get(u, u))
    if isinstance(a["src"], dict):
        ts, so = tb(a["src"]["term_uid"]), ob(a["src"]["uid"])
    else:
        sr = SSIM.resolve_addr(x.step(len(A))["state"], a["src"], True)
        ts, so = tb(sr["term_uid"]), ob(sr["owner_uid"])
    td = tb(a["dst"]["term_uid"])
    rows = getattr(EX["be"], "last_terms", None) or []
    d_ok = bool(rows) and bool(x.reads_real) and x.reads_real[-1] == len(x.ops)
    ind = sorted(set((r["term_uid"], r["owner_uid"], r["term_name"], r["wire_uid"]) for r in rows if r["term_uid"] == td))
    src = sorted(set((r["term_uid"], r["owner_uid"], r["term_name"], r["wire_uid"]) for r in rows if r["term_uid"] == ts))
    w = ind[0][3] if len(ind) == 1 else None
    a_ok = len(ind) == 1 and bool(w) and [ind[0][1], ind[0][2]] == list(e.get("sink") or [])
    b_ok = (bool(w) and len(src) == 1 and src[0][3] == w and src[0][1] == so and [src[0][2]] == d["src_name"]
            and list(e.get("source") or []) == [so, d["src_name"][0]])
    srcs = sorted(set(r["term_uid"] for r in rows if w and r["wire_uid"] == w and r["is_source"]))
    c_ok = srcs == [ts]
    return a_ok and b_ok and c_ok and d_ok, ("(a) indicator t{0} rows {1} wire {2}: {3}; (b) source t{4} #{5} rows {6} wire(s) {7} entry source {8}: {9}; "
                                             "(c) sources on wire {2} {10} == [t{4}]: {11}; (d) rows {12} = read after op {13} of {14}: {15}").format(
        td, ind, w, a_ok, ts, so, src, sorted(set(y[3] for y in src)), e.get("source"), b_ok, srcs, c_ok,
        len(rows), (x.reads_real or [None])[-1], len(x.ops), d_ok)


SINK_GATES = [{"gate": d["gate"], "sink": d["sink"]} for d in SGS]                 # one declared sink per census row (PD366(e))
SINK_FNS = dict((d["gate"], (lambda e, _d=d: sg_read(e, _d))) for d in SGS)


def body(s):
    print(__doc__, flush=True)
    s.gate("L0 plan FINAL, open_rows_match, plan_in = plan_ring_p5s01a_in; base graph md5 == pred == file; bed md5 == pred; plan end cdiff == pred; pred keyed to this plan",
           P.get("final") is True and P["finalized"].get("open_rows_match") is True and os.path.splitext(P["finalized"]["plan_in"]["path"])[0].endswith("plan_ring_p5s01a_in")
           and P["finalized"]["base"]["md5"] == PRED["graph"]["md5"] == K.md5(os.path.join(K.ROOT, P["finalized"]["base"]["path"])) and BASE["md5"] == PRED["bed_md5"]
           and sorted(P["finalized"]["end_cdiff_rows"]) == PRED["cdiff_rows"] and PRED["plan"]["md5"] == K.md5(PLAN), (K.md5(PLAN), P["finalized"]["base"], BASE["md5"]), fatal=True)
    s.start(); s.discard_work(); bp = K.mod("bench_prep"); h0 = bp.labview_handles(); c0 = snap(s)   # noqa: E702
    sg = SX.check_sink_gates(SINK_GATES, SINK_FNS)                                 # card 147-a2-1: the same check LVBackend makes, run in dry too
    s.gate("SG one declared sink gate per census row ({0} rows of {1}): {2}; per row: sink term(s), plan action(s), source, source name {3}".format(
        len(SG_CENSUS), os.path.basename(SG_CENSUS_FILE), sg, [(d["row"], d["terms"], [a["id"] for a in d["acts"]], [a["src"] for a in d["acts"]], d["src_name"]) for d in SGS]),
           len(sg) == len(SG_CENSUS) == len(SGS) and len(set(d["gate"] for d in SGS)) == len(SGS)
           and all(sg[k]["sink"] == d["sink"] == d["census_sink"] and len(d["terms"]) == 1 and len(d["acts"]) == 1 and len(d["src_name"]) == 1
                   and not str(d["src_name"][0]).startswith("UNRESOLVED") for k, d in enumerate(SGS)), sg, fatal=True)
    be = EX["be"] = SX.DryPlanBE(s, P, PLAN, BASE) if DRY else SGBackend(s, FSPAIRS, sink_gates=SINK_GATES, gates=SINK_FNS, mem_stop_mb=SX.MEM_STOP_MB)
    x = EX["x"] = SX.Executor(PLAN, be, log=lambda m: print(m, flush=True), checkpoints=CHECKPOINTS, name_gate=True)   # card 132-1 PD275(c)
    EX["s"] = s
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
           len(made) == NC and (on or NC == 0) and set(on) <= sf and frames(real) == sf, {"on": on, "nc": NC, "extra": sorted(frames(real) - sf), "missing": sorted(sf - frames(real))}, fatal=True)   # card 152-b2-1: NC 0
    # card 141-3 (PD325(b)): D / TD / unwired keyed by IDENTITY (term uid, owner uid, name) - LabVIEW re-uses deleted uids in-session
    # card 147-c3-2 (PD356(d), PD357(f)): TD on (uid, owner) passing only the licensed renames; D's REUSE-NOTED rule through the executor's binding
    ti = K.term_identity_gates(BASE["terminals"], L["terminals"], real, renames=REN, bind={"term": x.bind["term"], "obj": x.bind["obj"]})
    s.gate("D new wires {0} == sim's {1}; lost {2} == sim's {3} (wire uid + source identity, stagekit.wire_keys_356); deleted uids re-used: noted {4}, bad {5}".format(
        ti["d_new"], len(ti["sim_new"]), ti["d_lost"], len(ti["sim_lost_w"]), [n["wire"] for n in ti["reuse_noted"]], [n["wire"] for n in ti["reuse_bad"]]), ti["d_ok"],
        {"new": ti["new"], "lost": ti["lost_w"][:20], "reuse_noted": ti["reuse_noted"][:6], "reuse_bad": ti["reuse_bad"][:6]})
    dc = s.census_gate("CEN2 new-object census (classes of the pred) == plan_ring_p5s01a_pred.json census", c0, snap(s), PRED["census"])
    s.gate("TD every base terminal the sim keeps wired is still wired; identities lost == the plan's deletes (key {0}, stagekit.term_identity_gates); renames {1}, unlicensed {2}".format(
        ti.get("td_key", "uid/owner/name"), len(ti.get("renames") or []), ti.get("unlicensed_renames")),
           ti["td_ok"], {"unwired": ti["unwired"][:20], "lost": ti["lost"][:20], "plan_deletes": ti["gone"][:20], "recycled_uids": ti["recycled"][:20],
                         "raw_lost": ti["raw_lost"][:20], "renames": (ti.get("renames") or [])[:10], "unlicensed_renames": ti.get("unlicensed_renames")})
    s.R["term_identity"] = ti
    s.R["real_end_rows"] = [[r["term_uid"], r.get("owner_uid"), r.get("term_name"), r.get("wire_uid"), bool(r.get("is_source"))] for r in real]   # review c141-2 s4.2
    s.es("after all rows (ExecState 0 expected: P5-1a's in-between file is broken by design)")
    s1p = J(JC.WIKI, JC.S1_KEY + ".json")
    S1f = V.build4(s1p["terminals"], J(JC._newest("graph_objs_s1_*.json"))["objects"], J(JC._newest("graph_loops_s1_*.json"))["loops"], LAB, s1p["fs_tunnel_pairs"], frame_keyed=True)
    pbr, restored, unlic = K.pb_rename_rows(BASE["terminals"], L["terminals"], real, REN)   # card 147-c3-2 (PD357(f)): licensed renames get the sim end's name back
    G1 = V.build4(pbr, getattr(be, "last_objs", None) or be.st["objs"], copy.deepcopy(L["loops"]), LAB, FSPAIRS, frame_keyed=True)
    cd = V.computation_diff_frame(S1f, G1)
    rk = sorted(str(y["sink"]) for y in cd["rows"])
    s.gate("PB frame-keyed cdiff(S1, real end) == the pred's {0} rows and the plan's {1} open (node, term) pairs; no unlicensed rename (FATAL, before save)".format(len(PRED["cdiff_rows"]), len(P["open_rows"])),
           rk == PRED["cdiff_rows"] and set((int(y["node"]), str(y["sink"]).split("|")[2]) for y in cd["rows"]) == set((int(y["node"]), y["term"]) for y in P["open_rows"]) and unlic == [],
           {"extra": sorted(set(rk) - set(PRED["cdiff_rows"])), "missing": sorted(set(PRED["cdiff_rows"]) - set(rk)), "restored": restored, "unlicensed": unlic}, fatal=True)
    h1 = None if DRY else bp.labview_handles(); s.fact("PH handles: post-open {0} -> before-save {1}".format(h0, h1))   # noqa: E702
    s.gate("HB open->save handle growth <= +700 (PD236(b) band; refs balance is H5)", DRY or (h1 is not None and h0 is not None and h1 - h0 <= 700), (h0, h1))
    m = s.save(broken_ok=True) if SAVE else None
    SAVE and s.gate("PS artefact saved, md5 differs from the input; input unchanged", m and m != s.input_md5 and K.md5(s.input_vi) == s.input_md5, m)
    _x = m and m != s.input_md5 and s.work in s.scratches and s.scratches.remove(s.work)   # noqa: F841
    el = PRED["errorlist"]                                                          # in-between file: checked False, no EL file written
    s.R["ring_p5s01a"] = {"final": s.work if m else None, "md5": m, "cdiff_rows": rk, "handles": [h0, h1], "census_delta": dc, "frames": on,
                             "errorlist_predicted_total": el["predicted_total"], "errorlist_alternative_total": el["alternative_total"],
                             "level": "STRUCTURAL, in-between file of P5 (P5-1a), broken by design, never run"}; s.dump()   # noqa: E702


if __name__ == "__main__":
    st = K.Stage(BASE["vi"], BASE["md5"], "D1_ring_p5s01a", preload=False, deadline_min=45, out_json=os.path.join(K.BENCH, "launch_c154_p5s01a.json"), task="card 154-a3-2b RING P5-1a")
    rc = K.run(body, st)
    DRY or SX.kill_labview_at_exit()
    sys.exit(rc)
