r"""stage_d1_disp - card 100-6, PD213(f)4(iv) / PD212: THE DISPLAY-LOOP STAGE, executed, not re-decided.
INPUT claudeDev\D1_s1_copy.vi (3e3d23ce..., named by the plan's base graph), FRESH LabVIEW -> claudeDev\D1_s1_disp_<ts>.vi,
saved BY SCRIPT at ExecState 1. ROWS ONLY FROM THE FINALIZED PLAN tools/bench/sim/disp/plan_disp.json (stageplan_disp_r4_open =
r3_open + the MEASURED Max & Min names/class, diag_c100_6_resim.log); no uid and no terminal name is typed here.
PRIOR ART: stage_d1_l2a1.py (skeleton, DryBE), stagexec.lv_run (E1/E2/E3 and the cdiff on the real end, :1965-2027),
gscript.wire_health + _edge_pairs (PD211(b) readers, card 98-2/98-3), stagekit.broken_wire_count (RBW). No new op.
PREDICTION: L1 every action compiles to exactly one real op; E1 each real op == its simulated step (the #25261 value gate
reads False first, else the plan stops); W1 after the batch: termless wires are all RECORDED, RBW (VI-level, on the work copy,
PD212(f)) removes ONLY wire uids that existed before the stage, and loses NO data edge; E2 ExecState 1 after RBW;
E3 computation_diff(S1, real end) == the plan's 21 open_rows (FATAL, before save); PS saved by script, md5 != input, input
unchanged; LabVIEW gone at exit. Level: STRUCTURAL (the VI is never run: card flag run_vi false).
CARD 101-4: RECORD MODE (Executor record=True) - a STEP-DIFF is logged and the run goes on on the unsaved scratch; any
diff => every diff listed + the E3 cdiff of the last read, E1 FAILS, NOTHING saved. READS only at CHECKPOINTS (PD193(a)) =
binding ops + 4, 5 (the moved constants, stagesim only_source) + 12 + last: every-op reads cost ~3.4 MB (meter_l2a1_86c.log,
error 2 at 695 MB) and r4 was at 594.6 MB after op 4 of 47 (stage_d1_disp_r4.log:88) - 47 reads would cross MEMSTOP 700.
CARD 101-5: create_local_read resolves the panel index by label (r5 stop); the k12 only_source gap is OPEN (review c101-5-onlysource).
    py tools/bgrun.py --material --max-min 35 --retry-card tools/bench/cards/task_101-5.json --log tools/bench/stage_d1_disp_r6.log -- py -u tools/recipes/stage_d1_disp.py"""
import copy, json, os, subprocess, sys, time                                       # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, vigraph as V, stagesim as SS, stagexec as SX, jev_candidates as JC, allterms as AT  # noqa: E401,E402
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                 # noqa: E731
PLAN = os.path.join(K.BENCH, "sim/disp/plan_disp.json")                             # ONE literal: stage_prerun.plan_files reads it
P = J(PLAN); BASE = J(K.ROOT, P["finalized"]["base"]["path"]); A = P["actions"]   # noqa: E702
WIKI = J(JC.WIKI, P["context"]["s1_key"] + ".json")
DRY, CUT = bool(getattr(g.report_all, "_dry", False)), 10 ** 3
WIRING = ("tunnel", "connect", "wire_sr", "branch")


class DryBE(SX.SimBackend):
    """stage_prerun's dry run: the plan's own simulated ops + one Stage op record per real op (stage_d1_l2a1.DryBE)."""
    def __init__(self, s):
        SX.SimBackend.__init__(self, P, SS.base_state(BASE, P.get("context")), SS.load_models()); self.s = s   # noqa: E702

    def _apply(self, op, check=None):
        self.s._op(("wire_" if op["kind"] in WIRING else "") + op["kind"], lambda: {"err": None}, str(op["acts"]))
        return SX.SimBackend._apply(self, op, check)


def cdiff(x, be, real):
    """computation_diff(S1, real) as (sink node, term) rows + the plan's open rows (stagexec.lv_run :2004-2008)."""
    loops = copy.deepcopy(x.step(len(A))["state"]["loops"]); ob = x.bind["obj"]   # noqa: E702
    for L in loops or []:
        L["right_uids"] = [ob.get(int(u), int(u)) for u in L.get("right_uids") or []]
        L["left_of"] = dict((str(ob.get(int(k), int(k))), [ob.get(int(y), int(y)) for y in (v if isinstance(v, list) else [v])])
                            for k, v in (L.get("left_of") or {}).items())
    Greal = JC.from_parts({"terminals": real, "graph_summary": WIKI["graph_summary"]}, getattr(be, "last_objs", None) or be.st["objs"],
                          loops, JC.node_labels_default(), WIKI["fs_tunnel_pairs"], "stage_d1_disp end")
    cd = V.computation_diff(SS.load_s1(P), Greal)
    return (sorted(set((V.key_parts(r["sink"])[0], V.key_parts(r["sink"])[2]) for r in cd["rows"])),
            sorted(set((int(r["node"]), r["term"]) for r in P["open_rows"])))


def body(s):
    print(__doc__, flush=True)
    s.gate("L0 the executed plan is FINAL, open_rows_match, plan_in = stageplan_disp_r4_open.json", P.get("final") is True and
           P["finalized"].get("open_rows_match") is True and P["finalized"]["plan_in"]["path"].endswith("stageplan_disp_r4_open.json"),
           (K.md5(PLAN), P["finalized"]["plan_in"]), fatal=True)
    s.start(); bp = K.mod("bench_prep"); h0 = bp.labview_handles()                 # noqa: E702
    w_pre = set() if DRY else set(int(u) for u in AT.all_wire_uids(s.work)[0])   # PD211(b): the pre-existing wire uids
    s.fact("W0 pre-existing Wire uids: {0}".format(len(w_pre)))
    be = DryBE(s) if DRY else SX.LVBackend(s, WIKI["fs_tunnel_pairs"])
    ops0 = SX.compile_plan(P); cps = {0, 4, 5, 12, len(ops0)} | set(k for k, o in enumerate(ops0, 1) if o["kind"] in SX.BIND_KINDS)   # noqa: E702
    x = SX.Executor(PLAN, be, log=lambda m: print(m, flush=True), checkpoints=cps, record=True)
    OPS = [dict(o, id=A[o["acts"][0] - 1]["id"]) for o in x.ops]; acts = sorted(n for o in OPS for n in o["acts"])   # noqa: E702
    s.gate("L1 every plan action compiled into exactly one real op ({0} -> {1})".format(len(A), len(OPS)),
           acts == list(range(1, len(A) + 1)), acts, fatal=True)
    s.fact("CHECKPOINTS {0} of {1} ops (record mode)".format(sorted(cps - {0}), len(OPS)))
    try:
        real = x.run()
    except SX.ExecStop as e:
        s.R["stagexec"] = x.report; s.R["meter"] = getattr(getattr(be, "meter", None), "rows", None); s.R["step_diffs"] = x.diffs   # noqa: E702
        [s.fact("STEP-DIFF k {0} {1} ids {2} ops since last read {3}: {4}".format(d["k"], d["op"], d["ids"], d["ops_since_last_read"],
                json.dumps(d["new_since_last_diff"], default=str)[:CUT])) for d in x.diffs]
        s.gate("E1 the run reached its last op (record mode; stopped IN op {0})".format(x.cur), False, str(e)[:CUT], fatal=True)
        [s.fact("UNROUTABLE acts {0} ids {1}: {2}".format(u["acts"], u["ids"], u["err"])) for u in getattr(be, "unroutable", None) or []]
        return
    s.R["stagexec"] = x.report; s.R["step_diffs"] = x.diffs; s.fact("BINDING obj {0}".format(x.bind["obj"]))   # noqa: E702
    if not DRY:
        s.fact("METER SUMMARY {0}".format(json.dumps(be.meter.summary(), default=str)))
    if x.diffs:                                                                    # card 101-4: record, report, never save
        [s.fact("STEP-DIFF k {0} {1} ids {2} ops since last read {3}: new {4} | whole {5}".format(
            d["k"], d["op"], d["ids"], d["ops_since_last_read"], json.dumps(d["new_since_last_diff"], default=str)[:CUT],
            json.dumps(dict((a, b) for a, b in d["diff"].items() if b and a not in ("n", "who")), default=str)[:CUT])) for d in x.diffs]
        got, want = cdiff(x, be, real)                                             # the LAST checkpoint read, no LabVIEW call
        s.fact("E3-INFO cdiff(S1, last read) vs open_rows: extra {0} missing {1}".format(sorted(set(got) - set(want)), sorted(set(want) - set(got))))
        s.es("end (record mode, not saved)")
        s.gate("E1 every checkpoint's real graph == its simulated step (record mode, {0} diff(s)) - NOTHING SAVED".format(len(x.diffs)),
               False, [(d["k"], d["diff"]["n"]) for d in x.diffs], fatal=True)
        return
    s.gate("E1 every checkpoint's real graph == its simulated step (record mode, 0 diffs at {0} reads)".format(len(x.reads_real)), True)
    s.es("after all rows, BEFORE RBW (recorded)")
    if not DRY:                                                                    # W1: PD211(b) / PD212(f)
        rows0 = AT.read_terms(s.work, AT.OP_ALLTERMS_V1)[0]; wh = g.wire_health(s.work, rows=rows0)   # noqa: E702
        s.fact("W1 termless after the batch: {0} (new-uid termless {1})".format(wh["termless"], sorted(set(wh["termless"]) - w_pre)))
        e0 = g._edge_pairs(rows0); rb = s.broken_wire_count(allow_mutation=True, tag="RBW work")   # noqa: E702
        rows1 = AT.read_terms(s.work, AT.OP_ALLTERMS_V1)[0]; w1 = set(int(u) for u in AT.all_wire_uids(s.work)[0])   # noqa: E702
        gone, lost = sorted((wh["wires"] - w1)), sorted(e0 - g._edge_pairs(rows1))
        s.fact("W1 RBW removed {0}; lost edges {1}".format(gone, lost[:20]))
        s.gate("W1 RBW removed only pre-existing wire uids and lost no data edge; no termless wire left",
               set(gone) <= w_pre and not lost and not g.wire_health(s.work, rows=rows1)["termless"],
               {"new_uid_removed": sorted(set(gone) - w_pre), "lost": lost[:20], "rbw": rb}, fatal=True)
        real = be.read()                                                           # the backend's own reader, after RBW
    es = s.es("end (warm, after RBW)")
    s.gate("E2 ExecState 1 warm at the end", DRY or es == 1, es, fatal=True)
    got, want = cdiff(x, be, real)
    s.gate("E3 computation_diff(S1, real end) == the plan's {0} open_rows (FATAL, before save)".format(len(want)), got == want,
           {"extra": sorted(set(got) - set(want)), "missing": sorted(set(want) - set(got))}, fatal=True)
    s.census(tag="after display stage")
    h1 = bp.labview_handles(); s.fact("PH handles RECORDED: post-open {0} -> before-save {1}".format(h0, h1))   # noqa: E702
    m = s.save(broken_ok=False)
    s.gate("PS saved by script, md5 differs from the input; input unchanged", m and m != s.input_md5 and K.md5(s.input_vi) == s.input_md5, m)
    s.R["disp"] = {"final": s.work, "md5": m, "cdiff_rows": got, "handles": [h0, h1], "level": "STRUCTURAL (never run)"}; s.dump()   # noqa: E702


if __name__ == "__main__":
    st = K.Stage(BASE["vi"], BASE["md5"], "D1_s1_disp", preload=False, deadline_min=36, out_json=os.path.join(K.BENCH, "stage_d1_disp.json"), task="card 101-5")
    rc = K.run(body, st)
    if not DRY:
        subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4.0)   # noqa: E702
        print("LabVIEW gone at exit:", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower(), flush=True)
    sys.exit(rc)
