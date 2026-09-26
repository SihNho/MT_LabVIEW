r"""stage_d1_disp - card 100-6, PD213(f)4(iv) / PD212: THE DISPLAY-LOOP STAGE, executed, not re-decided. INPUT claudeDev\D1_s1_copy.vi
(named by the plan's base graph), FRESH LabVIEW -> claudeDev\D1_s1_disp_<ts>.vi saved BY SCRIPT at ExecState 1. ROWS ONLY FROM THE
FINALIZED PLAN tools/bench/sim/disp/plan_disp.json (from stageplan_disp_r4_open.json); no uid and no terminal name is typed here.
PRIOR ART: stage_d1_l2a1.py (DryBE), stagexec.lv_run (E1/E2/E3, cdiff), gscript.wire_health/_edge_pairs, stagekit RBW. No new op.
HELPERS (card 106-3, PD216(c)/(g)): DryPlanBE, w0_wires, report_stop, log_step_diffs, b1_gate, part_a_gates, w1_rbw, e3_gate,
kill_labview_at_exit live in tools/stagexec.py, moved from this file unchanged; this file keeps the gate order and the inputs.
PREDICTION: L1 one real op per action; E1 each checkpoint read == its simulated step (#25261 gate False first); RECORD MODE (101-4):
a diff is logged, the run goes on, nothing saved unless every diff is a PD214(c) WARN (dangling only, no later uid reference,
stagexec.classify_step_diff); reads only at CHECKPOINTS = binding ops + 4, 5, 12, last (PD193(a), memory: r4.log:88, r7.log:804);
W1 RBW removes only pre-existing wire uids, no lost edge; E2 ExecState 1; E3 (card 104-4, PD217(c), stagexec.e3_check): cdiff(S1, end)
== the plan's class 1-3 open rows (6 of 21), class-4 sources == S1 (15/15), added objects plan-created; also in the dry; PS by script.
PART-A MODE (card 103-1, PD215(b)): `--stop-after N` runs ops 1..N only (Executor stop_after, N a checkpoint): A1 no op > N, A2 step N
real == sim (WARN only), gui_save claudeDev\D1_s1_dispA_<ts>.vi (broken by design, never run), md5 + binding -> stage_d1_dispA.json.
PART-B MODE (card 103-4, PD215(b)/PD216(f)): `--from-step N --base <dispA file>`: input = the Part-A file (md5 from its JSON), binding
loaded by stagexec (plan md5 pinned, stop_after == N), B0 entry read == sim step N + gate re-read + parity/PRIME before op N+1, ops
N+1.. only; W1 pre-existing wires = S1's (the plan base graph, 1899 == Part A's W0); end gates E1/W1/E2/E3/PS unchanged.
    py tools/bgrun.py --material --max-min 40 --log tools/bench/stage_d1_dispA_r1.log -- py -u tools/recipes/stage_d1_disp.py --stop-after 40"""
import json, os, sys                                                                # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, stagexec as SX, jev_candidates as JC            # noqa: E401,E402
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                 # noqa: E731
PLAN = os.path.join(K.BENCH, "sim/disp/plan_disp.json")                             # ONE literal: stage_prerun.plan_files reads it
P = J(PLAN); BASE = J(K.ROOT, P["finalized"]["base"]["path"]); A = P["actions"]   # noqa: E702
WIKI = J(JC.WIKI, P["context"]["s1_key"] + ".json")
DRY, CUT = bool(getattr(g.report_all, "_dry", False)), SX.CUT
AV = sys.argv[1:]; STOP = int(AV[AV.index("--stop-after") + 1]) if "--stop-after" in AV else None   # noqa: E702  card 103-1 PART-A
FROM = int(AV[AV.index("--from-step") + 1]) if "--from-step" in AV else None       # card 103-4 PART-B
PARTA = os.path.join(K.BENCH, "stage_d1_dispA.json"); PA = J(PARTA)["partA"] if FROM else None   # noqa: E702
TAG = "stage_d1_disp end"


def body(s):
    print(__doc__, flush=True)
    s.gate("L0 the executed plan is FINAL, open_rows_match, plan_in = stageplan_disp_r4_open.json", P.get("final") is True and
           P["finalized"].get("open_rows_match") is True and P["finalized"]["plan_in"]["path"].endswith("stageplan_disp_r4_open.json"),
           (K.md5(PLAN), P["finalized"]["plan_in"]), fatal=True)
    FROM and s.gate("B0 PART-B binding: stop_after == --from-step {0}, file == --base, plan md5 == the executed plan's".format(FROM),
                    PA["stop_after"] == FROM and os.path.normcase(PA["file"]) == os.path.normcase(s.input_vi) and PA["plan_md5"] == K.md5(PLAN),
                    (PA["stop_after"], PA["file"], PA["plan_md5"]), fatal=True)
    s.start(); bp = K.mod("bench_prep"); h0 = bp.labview_handles()                 # noqa: E702
    w_pre = SX.w0_wires(s, BASE, FROM, DRY)
    s.fact("W0 pre-existing Wire uids: {0}{1}".format(len(w_pre), " (S1's, from the plan base graph - PART-B)" if FROM else ""))
    be = SX.DryPlanBE(s, P, PLAN, BASE, FROM, PA) if DRY else SX.LVBackend(s, WIKI["fs_tunnel_pairs"])
    ops0 = SX.compile_plan(P); cps = {0, 4, 5, 12, len(ops0)} | {STOP or 0} | set(k for k, o in enumerate(ops0, 1) if o["kind"] in SX.BIND_KINDS)   # noqa: E702
    try:
        x = SX.Executor(PLAN, be, log=lambda m: print(m, flush=True), checkpoints=cps, record=True, stop_after=STOP, from_step=FROM, binding=PA)
    except SX.ExecStop as e:
        return s.gate("B0 PART-B binding loads (stagexec.load_binding)", False, str(e)[:CUT], fatal=True)
    OPS = [dict(o, id=A[o["acts"][0] - 1]["id"]) for o in x.ops]; acts = sorted(n for o in OPS for n in o["acts"])   # noqa: E702
    s.gate("L1 every plan action compiled into exactly one real op ({0} -> {1})".format(len(A), len(OPS)), acts == list(range(1, len(A) + 1)), acts, fatal=True)
    s.fact("CHECKPOINTS {0} of {1} ops (record mode{2})".format(sorted(cps - {0}), len(OPS), ", PART-A stop after {0}".format(STOP) if STOP else ""))
    try:
        real = x.run()
    except SX.ExecStop as e:
        return SX.report_stop(s, x, be, e)
    s.R["stagexec"] = x.report; s.R["step_diffs"] = x.diffs; s.fact("BINDING obj {0}".format(x.bind["obj"]))   # noqa: E702
    FROM and SX.b1_gate(s, x, FROM)
    DRY or s.fact("METER SUMMARY {0}".format(json.dumps(be.meter.summary(), default=str)))
    fails = SX.log_step_diffs(s, x)                                                # PD214(c): WARN = dangling only, no later uid ref
    if STOP:
        return SX.part_a_gates(s, x, be, STOP)
    if fails:                                                                      # card 101-4: record, report, never save
        e3 = SX.e3_check(P, x, getattr(be, "last_objs", None) or be.st["objs"], real, WIKI, TAG)   # the LAST checkpoint read
        s.fact("E3-INFO {0}: extra {1} missing {2}".format(SX.e3_line(e3), e3["extra"], e3["missing"]))
        s.es("end (record mode, not saved)")
        s.gate("E1 every checkpoint's real graph == its simulated step (record mode, {0} FAIL diff(s), {1} WARN) - NOTHING SAVED".format(
            len(fails), len(x.diffs) - len(fails)), False, [(d["k"], d["diff"]["n"], d.get("class")) for d in x.diffs], fatal=True)
        return
    s.gate("E1 every checkpoint's real graph == its simulated step, or a PD214(c) WARN (record mode, {0} warn(s) at {1} reads)".format(
        len(x.diffs), len(x.reads_real)), True, [(d["k"], d["diff"]["n"]) for d in x.diffs])
    s.es("after all rows, BEFORE RBW (recorded)")
    if not DRY:                                                                    # W1: PD211(b) / PD212(f)
        real = SX.w1_rbw(s, be, w_pre)                                             # the backend's own reader, after RBW
    es = s.es("end (warm, after RBW)")
    s.gate("E2 ExecState 1 warm at the end", DRY or es == 1, es, fatal=True)
    got = SX.e3_gate(s, P, x, be, real, WIKI, DRY, TAG)["got"]                     # PD217(c): a dry E3 fail is a FAIL
    s.census(tag="after display stage")
    h1 = bp.labview_handles(); s.fact("PH handles RECORDED: post-open {0} -> before-save {1}".format(h0, h1))   # noqa: E702
    m = s.save(broken_ok=False)
    s.gate("PS saved by script, md5 differs from the input; input unchanged", m and m != s.input_md5 and K.md5(s.input_vi) == s.input_md5, m)
    s.R["disp"] = {"final": s.work, "md5": m, "cdiff_rows": got, "handles": [h0, h1], "level": "STRUCTURAL (never run)"}; s.dump()   # noqa: E702


if __name__ == "__main__":
    nm = "D1_s1_dispA" if STOP else "D1_s1_disp"
    vi, vm = (AV[AV.index("--base") + 1], PA["md5"]) if FROM else (BASE["vi"], BASE["md5"])   # PART-B: the input is the Part-A file
    st = K.Stage(vi, vm, nm, preload=False, deadline_min=36, out_json=os.path.join(K.BENCH, "stage_d1_disp{0}.json".format("A" if STOP else "")), task="card 103")
    rc = K.run(body, st)
    DRY or SX.kill_labview_at_exit()
    sys.exit(rc)
