r"""stage_d1_k - cycle 79 STAGE K (docs/d1-loop12-17-split-plan.md Pre-decided 177, executed, not re-decided). INPUT the S4 bed
claudeDev\D1_s4_loop17.vi (4b621946...), FRESH LabVIEW -> claudeDev\D1_k_<ts>.vi (scripted save if ExecState 1, else the
rule-6 GUI save). ROWS ONLY FROM THE FINALIZED SIMULATOR PLAN plan_k_split.json (tools/bench/sim_k_split.py): the stagexec
Executor runs its compiled ops one by one and compares the REAL graph after every op with the simulated step file
(docs/stage-simulator-plan.md step 6). No uid and no terminal name is written in this file. ROUTE (c), Pre-decided 178(f):
plan_k_split.json is the plan this recipe executes AND presents; plan_k_rows.json is a derived report, not read here.
PRIOR ART: tools/stagexec.py (Executor + LVBackend + lv_run's end-cdiff code; L7 bench 14/0, never saved), stage_d1_l7_r.py
(IndexMode gate, ordered second pass via cfw_second_pass, shots + save), stagekit. No new op.
PREDICTION CONTRACT (177(g)): E1 every real op's graph == its simulated step, every created object bound; IM each new
tunnel's IndexMode == its original's (the plan's tunnel `indexing`, 178(a) from k_contract_79); P2 the ordered second pass
(wire_delta 0, Wire.Is Broken? False) on every row whose SINK is a node terminal (6 tunnel rows + the chain's left row),
addressed by verify_term_uid; the 2 register-face rows and the 2 indicator rows are covered by E1 only (recorded);
PB computation_diff(S1, real end) == the plan's open_rows exactly (FATAL, before the save); KN the moved kernel's VI name
read on its new diagram (gscript.subvis) == the CPU kernel (31(a), FATAL, before the save); ES measured, NOT gated;
handles recorded (176(a)); input md5 + pins unchanged (H2/H3); refs opened == closed (H5).
DRY RUN (tools/stage_prerun.py): the COM layer is stubbed, so the Executor runs on stagexec's SIMULATED backend, which
records each real op once as a Stage op (wiring ops as wire_<kind>).
    py tools/bgrun.py --material --max-min 55 --log tools/bench/stage_d1_k.log -- py -u tools/recipes/stage_d1_k.py"""
import copy, json, os, sys                                                         # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, vigraph as V, stagesim as SS, stagexec as SX, jev_candidates as JC  # noqa: E401,E402
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                 # noqa: E731
PLAN = os.path.join(K.BENCH, "plan_k_split.json")
P = J(PLAN); BASE = J(K.ROOT, P["finalized"]["base"]["path"]); WIKI = J(K.ROOT, P["context"]["fs_pairs_wiki"]["path"])  # noqa: E702
DRY, CUT = bool(getattr(g.report_all, "_dry", False)), 10 ** 3
WIRING = ("tunnel", "connect", "wire_sr", "branch")
KERNEL_NAME = "Track N beads four-fold over-kernel-v3.vi"   # 31(a): what #5058 IS (a VI name, not a terminal name)


class DryBE(SX.SimBackend):
    """stage_prerun's dry run: the plan's own simulated ops (stagexec.dry_run's backend) + one Stage op record per real op."""
    def __init__(self, s):
        SX.SimBackend.__init__(self, P, SS.base_state(BASE, P.get("context")), SS.load_models())
        self.s = s

    def _apply(self, op, check=None):
        self.s._op(("wire_" if op["kind"] in WIRING else "") + op["kind"], lambda: {"err": None}, str(op["acts"]))
        return SX.SimBackend._apply(self, op, check)


def end_graph(ex, be, real):
    last = ex.step(len(P["actions"]))["state"]
    loops, ob = copy.deepcopy(last["loops"]), ex.bind["obj"]
    for L in loops or []:
        L["right_uids"] = [ob.get(int(u), int(u)) for u in L.get("right_uids") or []]
        L["left_of"] = dict((str(ob.get(int(k), int(k))), [ob.get(int(x), int(x)) for x in (v if isinstance(v, list) else [v])])
                            for k, v in (L.get("left_of") or {}).items())
    objs = getattr(be, "last_objs", None) or be.st["objs"]
    return JC.from_parts({"terminals": real, "graph_summary": WIKI["graph_summary"]}, objs, loops, JC.node_labels_default(),
                         WIKI["fs_tunnel_pairs"], "stage K end"), last


def body(s):
    print(__doc__, flush=True)
    s.gate("K0 the executed plan is a FINAL stageplan (178(f) route c)", P.get("schema") == "stageplan/1" and P.get("final") is True,
           (P.get("schema"), P.get("final"), K.md5(PLAN)), fatal=True)
    s.start(); s.discard_work(); bp = K.mod("bench_prep")                          # noqa: E702
    h0 = bp.labview_handles(); s.fact("HANDLES after open {0!r}".format(h0))       # noqa: E702
    be = DryBE(s) if DRY else SX.LVBackend(s, WIKI["fs_tunnel_pairs"])
    ex = SX.Executor(PLAN, be, log=lambda m: print(m, flush=True))
    s.fact("COMPILED {0} real ops: {1}".format(len(ex.ops), [(o["kind"], o["acts"]) for o in ex.ops]))
    A = P["actions"]; OPS = [dict(o, id=A[o["acts"][0] - 1]["id"]) for o in ex.ops]; acts = sorted(x for o in OPS for x in o["acts"])  # noqa: E702
    s.gate("K1b every plan action is compiled into exactly one real op ({0} actions -> {1} ops, {2} wired)".format(
           len(A), len(OPS), sum(1 for o in OPS if o["kind"] in WIRING)), acts == list(range(1, len(A) + 1)), acts, fatal=True)
    try:
        real = ex.run()
        s.gate("E1 every real op's graph == its simulated step ({0} ops)".format(len(ex.ops)), True)
    except SX.ExecStop as e:
        s.R["stagexec"] = ex.report
        s.gate("E1 every real op's graph == its simulated step", False, str(e)[:CUT], fatal=True)
    s.R["stagexec"] = ex.report; s.fact("BINDING obj {0}".format(ex.bind["obj"]))  # noqa: E702
    G1, last = end_graph(ex, be, real)
    sym = lambda nm: ex.bind["obj"].get(last["sym"]["new:" + nm])                  # noqa: E731
    for t in [A[o["acts"][0] - 1] for o in OPS if o["kind"] == "tunnel"]:           # IM: 177(c)/178(a) IndexMode == original's
        u, want = sym(t["as"]), int(bool(t["indexing"]))
        before = s.safe("tunnels #{0}".format(u), lambda: g.tunnels(s.work, s.uid_index("LoopTunnel", u)))[0]
        got, err = s.safe("index_mode_fix #{0}".format(u), lambda: be.index_mode_fix(u, bool(want)))
        s.gate("IM {0} ({1}) new tunnel #{2} IndexMode == the original's {3} (read {4})".format(t["as"], t["id"], u, want,
               (before or {}).get("index_mode") if isinstance(before, dict) else before), not err and got == want, err)
    for d in OPS:                                                                   # P2: ordered second pass on node-terminal sinks
        if d["kind"] not in ("tunnel", "wire_sr") or (d["kind"] == "wire_sr" and not isinstance(A[d["acts"][0] - 1]["dst"], dict)):
            s.fact("P2 {0} ({1}): sink is not a node terminal - covered by E1 only".format(d["id"], d["kind"]))
            continue
        a = A[d["acts"][-1] - 1]
        r = SS.resolve_addr(last, a["dst"], False)
        src = sym(a["src"].split(".")[0][len("new:"):])
        end = {"uid": a["dst"]["uid"], "term": a["dst"]["term"], "verify_term_uid": ex.bind["term"].get(r["term_uid"], r["term_uid"]),
               "diagram": r["frame_diagram"], "owner_class": "", "term_class": ""}
        s.expect_is_broken_false("P2 " + d["id"], lambda e=end, x=src, i=d["id"]: s.safe("2nd pass " + i, lambda: s.cfw_second_pass(x, e), {})[0])
    s.es("after all rows (warm, RECORDED - the (e) rows are open by design)")
    cd = V.computation_diff(SS.load_s1(P), G1)
    for x in cd["rows"]: s.fact("CDIFF ROW {0}".format(dict((k, V.show(v) if k == "sink" else v) for k, v in x.items())))  # noqa: E701
    got = sorted(set((V.key_parts(x["sink"])[0], V.key_parts(x["sink"])[2]) for x in cd["rows"]))
    want = sorted(set((int(x["node"]), x["term"]) for x in P["open_rows"]))
    s.gate("PB computation_diff(S1, real end) rows == the plan's {0} open_rows (FATAL, before save)".format(len(want)), got == want,
           {"extra": sorted(set(got) - set(want)), "missing": sorted(set(want) - set(got))}, fatal=True)
    mk = next(a for a in A if a["id"] == "move_kernel")                             # KN: 31(a) name gate (prior-art c79-k)
    ku, kb = ex.bind["obj"].get(mk["nodes"][0], mk["nodes"][0]), ex.bind["obj"].get(mk["dest_diagram"], mk["dest_diagram"])
    di = s.uid_index("Diagram", kb)
    rows, err = s.safe("subvis on #{0}[{1}]".format(kb, di), lambda: g.subvis(s.work, di), [])
    kn = next((r for r in rows or [] if isinstance(r, dict) and r.get("uid") == ku), {})
    s.fact("KN #{0} on Diagram #{1}[{2}] reads name {3!r} path {4!r}".format(ku, kb, di, kn.get("name"), kn.get("path")))
    s.gate("KN the moved node #{0} on #{1} is the CPU kernel {2!r} (Pre-decided 31(a), docs/cycle27-plan.md:754-755; FATAL)".format(ku, kb, KERNEL_NAME),
           str(kn.get("name", "")).strip().lower() == KERNEL_NAME.lower(), err or kn, fatal=True)
    G0 = JC.from_parts({"terminals": ex.step(0)["state"]["terminals"], "graph_summary": WIKI["graph_summary"]}, BASE["objs"],
                       ex.step(0)["state"]["loops"], JC.node_labels_default(), WIKI["fs_tunnel_pairs"], "stage K base")
    E0, E1 = K.uid_edges(G0), K.uid_edges(G1)
    s.fact("DIFF(bed,new) uid edges removed {0}: {1}".format(len(E0 - E1), sorted(E0 - E1, key=repr)))
    s.fact("DIFF(bed,new) uid edges added {0}: {1}".format(len(E1 - E0), sorted(E1 - E0, key=repr)))
    s.census(tag="after K")
    h1 = bp.labview_handles(); s.fact("PH handles RECORDED, not gated (176(a)): post-load {0} -> before-save {1}".format(h0, h1))  # noqa: E702
    shot = lambda n: g._lv_gui("-Action", "shot", "-Out", '"{0}"'.format(os.path.join(K.BENCH, "stage_d1_k_{0}_{1}.png".format(s.stamp, n))))  # noqa: E731
    m = (shot("before_save"), s.save(broken_ok=True), shot("after_save"))[1]
    s.gate("PS artefact saved, md5 differs from the input; input unchanged", m and m != s.input_md5 and K.md5(s.input_vi) == s.input_md5, m)
    _x = m and m != s.input_md5 and s.work in s.scratches and s.scratches.remove(s.work)   # noqa: F841
    s.R["k"] = {"final": s.work, "md5": m, "cdiff_rows": got, "handles": [h0, h1], "binding": ex.bind["obj"]}; s.dump()  # noqa: E702

if __name__ == "__main__":
    st = K.Stage(BASE["vi"], BASE["md5"], "D1_k", preload=False, deadline_min=52, out_json=os.path.join(K.BENCH, "stage_d1_k.json"))
    sys.exit(K.run(body, st))
