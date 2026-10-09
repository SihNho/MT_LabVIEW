# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_chat-T7.md
# ---
r"""selftest_t7_ring - card chat-T7 (docs/d1/result-gates.md PD377): the ring-recipe logic extracted into tools/stagekit.py, each function
REPLAYED on recorded data. No LabVIEW, no COM (stagekit's pure functions only; RingSession is built but never run).
PRIOR ART: selftest_t6_poskey.py (its load / enrich are CALLED, not copied), selftest_c153_poskey_convert.py (converter cases),
diag_c153_a2_4_run.py R1/R2 (the real-PB replay on the stored s06 files).
DATA: the stored scratch end reads (diag_c1xx_*_scratch.json real_end_rows) + creation maps of P4 s03..s09 and P5-1a, the s06 147-a1-8
fixture, the stored plans / preds (byte-unchanged), diag_c150_p4s07v18_scratch.log (sink gates), diag_c149_a1_2_eladv.log (EL advisory).
PREDICTION:
 P1-P9  stagekit.pb_check PASSES on every stored batch end with NO licence (s06: the pred's 18 stored name rows = 14 slots);
 P0     the OLD name compare (rk == pred rows) FAILS on s06 (14 vs 18 - fp-70), so P1-P9 are not vacuous;
 M1-M5  on s06-c3: a pred row dropped / a pred row added / a kept computation sink rewired / an open pair dropped / an unlicensed
        rename listed -> each FAILS; C1 every real terminal renamed -> still PASSES;
 S1-S3  s07: sink_gate_spec reproduces the scratch log's SG per-row tuple (log :65); sink_gate_read reproduces both recorded PASS
        details character for character (log :358-359); the indicator unwired -> FAIL;
 R1-R2  RingSession on the s07 and P5-1a inputs: SG label + L1 checkpoints == the scratch logs' (:65, p5s01a :67); NC / SG rows;
 X1-X2  pred_x10 == the logged X10 (s07 673.7, P5-1a 672.2); a plan with another md5 -> None;
 E1-E2  el_advisory on the stored s06 Error List read reproduces diag_c149_a1_2_eladv.log:3 exactly (rc 1); el_advisory_selftest on the
        s06 pred 5/0 (its RESULT line);
 A1     census_all_install: two snapshots -> the three CENSUS-ALL lines and s.R['census_all'] (a stand-in Stage class)."""
import copy, io, json, os, sys                                                     # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path[:0] = [os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench")]
D = os.path.join(ROOT, "tools", "bench")
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))               # noqa: E731
CASES = (("s03", "plan_ring_p4_s03v18.json", os.path.join(D, "diag_c143_p4s03v18_scratch.json"), "plan_ring_p4_s03v18_da66a030_20261007_203225.jsonl"),
         ("s04", "plan_ring_p4_s04v18.json", os.path.join(D, "diag_c144_p4s04v18_scratch.json"), "plan_ring_p4_s04v18_f349c39a_20261007_215246.jsonl"),
         ("s05", "plan_ring_p4_s05v18.json", os.path.join(D, "diag_c145_p4s05v18_scratch.json"), "plan_ring_p4_s05v18_1fc9b486_20261008_002835.jsonl"),
         ("s06-a1-8", "plan_ring_p4_s06v18.json", os.path.join(D, "fixtures", "t6_s06_a1_8_end.json"), "plan_ring_p4_s06v18_cfbd9823_20261008_125817.jsonl"),
         ("s06-c3", "plan_ring_p4_s06v18.json", os.path.join(D, "diag_c147_p4s06v18_scratch.json"), "plan_ring_p4_s06v18_cfbd9823_20261008_175325.jsonl"),
         ("s07", "plan_ring_p4_s07v18.json", os.path.join(D, "diag_c150_p4s07v18_scratch.json"), "plan_ring_p4_s07v18_08c2ad4d_20261008_222936.jsonl"),
         ("s08", "plan_ring_p4_s08v18.json", os.path.join(D, "diag_c150_p4s08v18_scratch.json"), "plan_ring_p4_s08v18_c328fdaf_20261009_031742.jsonl"),
         ("s09", "plan_ring_p4_s09v18.json", os.path.join(D, "diag_c152_p4s09v18_scratch.json"), "plan_ring_p4_s09v18_9d622c95_20261009_060730.jsonl"),
         ("p5s01a", "plan_ring_p5s01a.json", os.path.join(D, "diag_c154_p5s01a_scratch.json"), "plan_ring_p5s01a_ed62e8d6_20261009_101431.jsonl"))
GATES = []


def gate(label, ok, detail=""):
    GATES.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:700]), flush=True)


def fact(s):
    print("  FACT  " + str(s)[:900], flush=True)


def log_line(name, n):
    return open(os.path.join(D, name), encoding="utf-8", errors="replace").read().splitlines()[n - 1]


def pb_cases(K, V, T6, S1f, LAB):
    keep = {}
    for tag, plan, rj, cmap in CASES:
        P, BASE, L, S, ob, tb, pins = T6.load(plan, rj, cmap)
        B, SIM = BASE["terminals"], L["terminals"]
        RE, unb = T6.enrich(B, SIM, S["real_end_rows"], ob, tb)
        PRED = J(D, plan.replace(".json", "_pred.json"))
        rows, restored, unl = K.pb_rename_rows(B, SIM, RE, None, bind={"term": tb, "obj": ob})
        objs = [dict(o, uid=ob.get(int(o["uid"]), int(o["uid"]))) for o in L["objs"]]
        FSP = BASE.get("fs_tunnel_pairs", BASE.get("fs_pairs"))
        G1 = V.build4(rows, objs, copy.deepcopy(L["loops"]), LAB, FSP, frame_keyed=True)
        Gp = K.pred_end_graph(L, LAB, FSP)
        r = K.pb_check(S1f, G1, Gp, PRED["cdiff_rows"], P["open_rows"], unl)
        gate("P {0} pb_check PASS, NO licence: pred {1} stored rows = {2} slots == cdiff {3} slots; open pairs {4} -> {5} == {6}; inputs pinned {7}, unbound {8}".format(
            tag, r["pred_rows"], r["slots_want"], r["slots_got"], len(P["open_rows"]), r["pairs_want"], r["pairs_got"], pins, len(unb)),
             r["ok"] and pins, {"extra": r["extra_sinks"], "missing": r["missing_sinks"], "pairs_missing": r["pairs_missing"]})
        cdp = sorted(str(y["sink"]) for y in V.computation_diff_frame(S1f, Gp)["rows"])
        nds = set(int(x.split("|")[0]) for x in PRED["cdiff_rows"] + cdp)
        conv = sorted(q["sink"] for q in K.pos_convert(PRED["cdiff_rows"], K.pos_slots(S1f, nds, V), K.pos_slots(Gp, nds, V)))
        gate("Q {0} the converted pred == cdiff(S1, the plan's simulated end) under the adopted vigraph ({1} vs {2} rows): the conversion "
             "reproduces vigraph a7eb58c7 on the pred's own graph".format(tag, len(conv), len(cdp)), conv == cdp,
             {"only_conv": sorted(set(conv) - set(cdp)), "only_cdiff": sorted(set(cdp) - set(conv))})
        keep[tag] = (P, PRED, B, SIM, RE, rows, objs, L, FSP, ob, tb, G1, r, Gp)
    P, PRED, B, SIM, RE, rows, objs, L, FSP, ob, tb, G1, r, Gp = keep["s06-c3"]
    rk = r["rows"]
    gate("P0 the OLD name compare (rk == pred rows) FAILS on s06-c3: {0} vs {1} rows (fp-70), so P is not vacuous".format(len(rk), len(PRED["cdiff_rows"])),
         rk != PRED["cdiff_rows"] and len(rk) == 14 and len(PRED["cdiff_rows"]) == 18 and r["slots_want"] == 14, sorted(set(PRED["cdiff_rows"]) - set(rk)))
    pc = lambda pred=None, op=None, unl=(), G=None, Gq=None: K.pb_check(S1f, G or G1, Gq or Gp, PRED["cdiff_rows"] if pred is None else pred,   # noqa: E731
                                                                     P["open_rows"] if op is None else op, unl)
    real_row = sorted(set(PRED["cdiff_rows"]) & set(rk))[0]
    gate("M1 pred row {0} dropped -> FAIL".format(real_row), not pc(pred=[x for x in PRED["cdiff_rows"] if x != real_row])["ok"])
    P1 = K.pos_slot_table(G1)
    cnodes = set(n for n in S1f["cls"] if not V.is_scheduling(S1f, n)) & set(n for n in G1["cls"] if not V.is_scheduling(G1, n))
    gs = set(int(x.split("|")[0]) for x in rk)
    # M2: the PLAN predicted a change the build did not make - the pred's own graph rewires a kept computation sink (the maker would list
    # the new cdiff row), the real end does not. Converting the pred on the REAL end would erase that row; on the pred's graph it stays.
    sim_sinks = [x for x in SIM if not x["is_source"] and x["wire_uid"] and int(x["owner_uid"]) in cnodes and int(x["owner_uid"]) not in gs]
    sim_srcs = [x for x in SIM if x["is_source"] and x["wire_uid"]]
    st_ = sim_sinks[len(sim_sinks) // 2]
    so_ = next(x for x in sim_srcs[len(sim_srcs) // 3:] if x["wire_uid"] != st_["wire_uid"] and x["owner_uid"] != st_["owner_uid"])
    Lm = dict(L, terminals=[dict(x, wire_uid=so_["wire_uid"]) if x["term_uid"] == st_["term_uid"] else x for x in SIM])
    Gpm = K.pred_end_graph(Lm, LAB, FSP)
    new_rows = sorted(set(str(y["sink"]) for y in V.computation_diff_frame(S1f, Gpm)["rows"]) - set(str(y["sink"]) for y in V.computation_diff_frame(S1f, Gp)["rows"]))
    m2 = pc(pred=PRED["cdiff_rows"] + new_rows, Gq=Gpm)
    m2r = pc(pred=PRED["cdiff_rows"] + new_rows, Gq=G1)
    gate("M2 the pred's graph rewires sim sink #{0} on #{1} (new pred row(s) {2}), the real end does not -> FAIL (missing {3}); converted on the REAL end instead it would PASS: {4}".format(
        st_["term_uid"], st_["owner_uid"], new_rows, m2["missing_sinks"], m2r["ok"]), new_rows and not m2["ok"] and m2["missing"])
    sinks_ = [x for x in rows if not x["is_source"] and x["wire_uid"] and int(x["owner_uid"]) in cnodes and int(x["owner_uid"]) not in gs]
    srcs = [x for x in rows if x["is_source"] and x["wire_uid"]]
    tgt = sinks_[len(sinks_) // 2]
    other = next(x for x in srcs[len(srcs) // 3:] if x["wire_uid"] != tgt["wire_uid"] and x["owner_uid"] != tgt["owner_uid"])
    G3 = V.build4([dict(x, wire_uid=other["wire_uid"]) if x["term_uid"] == tgt["term_uid"] else x for x in rows], objs, copy.deepcopy(L["loops"]), LAB, FSP, frame_keyed=True)
    m3 = pc(G=G3)
    gate("M3 kept computation sink #{0} on #{1} rewired to w{2} (source #{3}) -> FAIL (extra {4})".format(
        tgt["term_uid"], tgt["owner_uid"], other["wire_uid"], other["owner_uid"], m3["extra_sinks"][:3]), not m3["ok"] and m3["extra"], len(P1))
    gate("M4 an open pair dropped -> FAIL", not pc(op=P["open_rows"][1:])["ok"])
    gate("M5 an unlicensed rename listed -> FAIL", not pc(unl=[(1, 2, "a", "b")])["ok"])
    ren = [dict(x, term_name="renamed_" + str(x["term_uid"])) for x in RE]
    rows_c, _rs, unl_c = K.pb_rename_rows(B, SIM, ren, None, bind={"term": tb, "obj": ob})
    c1 = pc(G=V.build4(rows_c, objs, copy.deepcopy(L["loops"]), LAB, FSP, frame_keyed=True), unl=unl_c)
    gate("C1 every real terminal renamed -> PB still PASSES (names are report columns)", c1["ok"], {"extra": c1["extra_sinks"][:3], "missing": c1["missing_sinks"][:3]})


class _X(object):
    """The parts of a stagexec.Executor that sink_gate_read reads, rebuilt from the stored s07 run."""
    def __init__(self, ob, tb, L, n_ops):
        self.bind = {"term": tb, "obj": ob, "diag": {}}
        self.reads_real, self.ops, self._L = [n_ops], list(range(n_ops)), L

    def step(self, k):
        return {"state": self._L}


def sink_cases(K, T6):
    plan, rj, cmap = CASES[5][1:]
    P, BASE, L, S, ob, tb, pins = T6.load(plan, rj, cmap)
    census = [e for e in J(D, "prep_c150_a1_1_session.json")["sink_gate_census"] if e.get("needs_sink_gate")]
    SGS = [K.sink_gate_spec(e, P["actions"], BASE, L) for e in census]
    per = [(d["row"], d["terms"], [a["id"] for a in d["acts"]], [a["src"] for a in d["acts"]], d["src_name"]) for d in SGS]
    want = log_line("diag_c150_p4s07v18_scratch.log", 65)
    gate("S1 sink_gate_spec on the s07 census reproduces the logged per-row tuple (diag_c150_p4s07v18_scratch.log:65)", ("source name " + str(per)) in want, per)
    rows = [dict(term_uid=a, owner_uid=b, term_name=c, wire_uid=d, is_source=e) for a, b, c, d, e in S["real_end_rows"]]
    x = _X(ob, tb, L, len(J(D, plan.replace(".json", "_pred.json"))["ops"]))       # the pred's compiled op count (30 = log :358 "op 30 of 30")
    ok = True
    for d, ln, src in zip(SGS, (358, 359), ([5058, "pos in cal image out"], [4586, "s? t:f"])):
        e = {"gate": d["gate"], "sink": d["sink"], "source": src}
        got_ok, det = K.sink_gate_read(e, d, x, rows, len(P["actions"]))
        line = log_line("diag_c150_p4s07v18_scratch.log", ln)
        ok = ok and got_ok and line.endswith("  " + det)
        fact("S2 {0}: ok {1}; detail == log :{2} -> {3}".format(d["gate"], got_ok, ln, line.endswith("  " + det)))
    gate("S2 sink_gate_read reproduces both recorded PASS details character for character (log :358-359)", ok)
    d = SGS[0]
    bad = [dict(r, wire_uid=0) if r["term_uid"] == d["terms"][0] else r for r in rows]
    gate("S3 the indicator terminal unwired -> sink_gate_read FAILS", not K.sink_gate_read({"gate": d["gate"], "sink": d["sink"], "source": [5058, "pos in cal image out"]},
                                                                                          d, x, bad, len(P["actions"]))[0])


class _S(object):
    """A stand-in Stage: records gates / facts (RingSession.executor is NOT run here - only its label inputs)."""
    def __init__(self):
        self.R, self.lines = {}, []


def ring_cases(K):
    rs7 = K.RingSession(os.path.join(D, "plan_ring_p4_s07v18.json"), os.path.join(D, "plan_ring_p4_s07v18_pred.json"),
                        os.path.join(D, "plan_ring_p4_s07v18_licence.json"), os.path.join(D, "prep_c150_a1_1_session.json"))
    lab = "SG one declared sink gate per census row ({0} rows of {1}): ".format(len(rs7.SG_CENSUS), os.path.basename(rs7.census_path))
    gate("R1 RingSession(s07): SG label head + the 2 sink declarations == log :65; NC {0}; DRY {1}".format(rs7.NC, rs7.DRY),
         log_line("diag_c150_p4s07v18_scratch.log", 65).startswith("  PASS  " + lab + str(rs7.SINK_GATES)) and not rs7.DRY)
    rs5 = K.RingSession(os.path.join(D, "plan_ring_p5s01a.json"), os.path.join(D, "plan_ring_p5s01a_pred.json"),
                        os.path.join(D, "plan_ring_p5s01a_licence.json"), os.path.join(D, "prep_c154_a3_2b_session.json"))
    l1 = "L1 the {0} actions compile into {1} real ops == pred kinds, each action once; checkpoints {2}".format(len(rs5.A), len(rs5.PRED["ops"]), rs5.CHECKPOINTS)
    gate("R2 RingSession(P5-1a): L1 label (checkpoints) == diag_c154_p5s01a_scratch.log:67; SG rows 0; NC {0}".format(rs5.NC),
         log_line("diag_c154_p5s01a_scratch.log", 67).startswith("  PASS  " + l1) and rs5.SG_CENSUS == [] and rs5.NC > 0, l1)
    x7 = K.pred_x10(os.path.join(D, "plan_ring_p4_s07v18_pred.json"), os.path.join(D, "plan_ring_p4_s07v18.json"))
    x5 = K.pred_x10(os.path.join(D, "plan_ring_p5s01a_pred.json"), os.path.join(D, "plan_ring_p5s01a.json"))
    gate("X1 pred_x10 == the logged X10 (s07 {0}, P5-1a {1}; diag_c150_p4s07v18_scratch.log:24, diag_c154_p5s01a_scratch.log:24)".format(x7, x5),
         "pred {0};".format(x7) in log_line("diag_c150_p4s07v18_scratch.log", 24) and "pred {0};".format(x5) in log_line("diag_c154_p5s01a_scratch.log", 24))
    gate("X2 pred_x10 with another plan (md5 differs) -> None", K.pred_x10(os.path.join(D, "plan_ring_p4_s07v18_pred.json"), os.path.join(D, "plan_ring_p5s01a.json")) is None)


def el_cases(K):
    items = J(D, "errorlist_D1_ring_p4s06_20261008_174730_20261008_181243.json").get("items") or []
    rc, rep = K.el_advisory(items, os.path.join(D, "plan_ring_p4_s06v18_pred.json"), os.path.join(D, "plan_ring_p4_s06v18.json"))
    buf, old = io.StringIO(), sys.stdout
    sys.stdout = buf
    try:
        K.el_advisory_print(rc, rep)
    finally:
        sys.stdout = old
    gate("E1 el_advisory on the stored s06 Error List read == diag_c149_a1_2_eladv.log:3 exactly, rc {0} (1 recorded)".format(rc),
         buf.getvalue().rstrip("\n") == log_line("diag_c149_a1_2_eladv.log", 3) and rc == 1, buf.getvalue()[:200])
    buf = io.StringIO()
    sys.stdout = buf
    try:
        src = K.el_advisory_selftest(os.path.join(D, "plan_ring_p4_s06v18_pred.json"), os.path.join(D, "plan_ring_p4_s06v18.json"))
    finally:
        sys.stdout = old
    gate("E2 el_advisory_selftest on the s06 pred -> rc 0 and RESULT 5/0", src == 0 and '"pass": 5, "fail": 0' in buf.getvalue(), buf.getvalue()[-200:])


def census_case(K):
    class St(object):
        snaps = iter([{1: "Wire", 2: "Wire", 3: "Function"}, {1: "Wire", 3: "Function", 4: "Function", 5: "Wire"}])

        def __init__(self):
            self.R = {}

        def census_snapshot(self, target=None):
            return next(St.snaps)

        def census_gate(self, label, before, after, declared):
            return {"label": label}
    K._CENSUS_ALL["snaps"][:] = []
    K.census_all_install(St)
    s = St()
    buf, old = io.StringIO(), sys.stdout
    sys.stdout = buf
    try:
        a = s.census_snapshot()
        b = s.census_snapshot()
        got = s.census_gate("CEN2", a, b, {})
    finally:
        sys.stdout = old
    lines = buf.getvalue().splitlines()
    gate("A1 census_all_install: 3 CENSUS-ALL lines, net delta Function +1, new uids {Function 1, Wire 1}, lost 1; gate result passed through",
         s.R.get("census_all") == {"net_delta": {"Function": 1}, "new_by_class": {"Function": 1, "Wire": 1}, "lost": 1} and len(lines) == 3
         and got == {"label": "CEN2"}, lines)
    K._CENSUS_ALL["snaps"][:] = []


def main():
    import stagekit as K, vigraph as V, jev_candidates as JC                     # noqa: E401  pure functions only
    import selftest_t6_poskey as T6                                               # its load / enrich: called, not copied
    LAB = JC.node_labels_default()
    S1f = K.s1_frame_graph(LAB)
    pb_cases(K, V, T6, S1f, LAB)
    sink_cases(K, T6)
    ring_cases(K)
    el_cases(K)
    census_case(K)


if __name__ == "__main__":
    import protocol
    main()
    fails = [g for g, ok in GATES if not ok]
    print(protocol.result_line({"status": "PASS" if not fails else "FAIL", "gates": {"pass": len(GATES) - len(fails), "fail": len(fails)},
                                "first_fail": (fails[0][:180] if fails else None), "artefacts": []}), flush=True)
    sys.exit(0 if not fails else 1)
