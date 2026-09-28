r"""diag_c116d_j3 - card 116-4 J2 + J3: Wire.Joints[] (gscript.wire_joints, OpWireJoints_v0) on the R1 bed BEFORE and AFTER the L2-R2
rows, on ONE fresh dated byte copy claudeDev\scratch_c116d_bed_<ts>.vi. It runs the stage recipe's OWN body (tools/recipes/
stage_d1_l2r2.py, imported, SAVE=False: nothing is saved, the work copy is a scratch deleted at close) exactly as diag_c116b_scratch.py
did, with two READ-ONLY hooks: (J2) before the Executor's first op, joints of the 13 outer nets, the 7 PD230(d) nets, the 11 stubs and
every wire the saved R1 graph shows with no sink or no source (candidates for a loose end), then a TIME-CAPPED sweep of the other wires
(coverage recorded); (J3) after all rows, before Remove Bad Wires touches the copy, the same wires again (stubs are gone by design).
PRIOR ART: diag_c116b_scratch.py (this is its cut; SAVE=False + the two hooks are new). No launch, no save, no VI run.
ATTEMPT 2 (after diag_c116d_j3.log 08:58: the whole-graph sweep exhausted refnums at read 536 -> error 1055, then error 2):
sweep_s = 0 (diag_c116d_nets.json) - the 37 target wires only, ~63 op calls; raw -> diag_c116d_j3_raw2.json (attempt 1 kept).
PREDICTION: every read echoes its uid with err ''; the recipe's gates behave as in 116-2 (43/0, diag_c116b_scratch.log:340); raw
joints -> tools/bench/diag_c116d_j3_raw.json for the offline decode (diag_c116d_decode.py); scratch deleted; LabVIEW gone.
    py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c116d_j3.log -- py -u tools/bench/diag_c116d_j3.py"""
import json, os, sys, time                                                          # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "recipes"))
import stagekit as K, stagexec as SX                                                # noqa: E401,E402
import stage_d1_l2r2 as R                                                           # noqa: E402
g = K.g
PLAN = os.path.join(K.BENCH, "plan_l2r2.json")                                      # the recipe's plan (stage_prerun.plan_files reads it)
PRED = json.load(open(os.path.join(K.BENCH, "plan_l2r2_pred.json"), encoding="utf-8"))
NETS = json.load(open(os.path.join(K.BENCH, "diag_c116d_nets.json"), encoding="utf-8"))
PD230, SWEEP_S = [int(w) for w in NETS["pd230"]], float(NETS["sweep_s"])            # plan_l2r2_make.py:73 (PD230(d), INFERRED)
RAW, ST = {"before": {}, "after": {}, "coverage": {}}, {}
CNT = {}
for r in R.BASE["terminals"]:
    if r["wire_uid"]:
        c = CNT.setdefault(int(r["wire_uid"]), [0, 0]); c[0 if r["is_source"] else 1] += 1    # noqa: E702
ODD = sorted(w for w, (a, b) in CNT.items() if a == 0 or b == 0)
TARGET = sorted(set(PRED["shared_sink_nets"]) | set(PD230) | set(PRED["stubs"]) | set(ODD))


def phase(s, t, tag, sweep):
    order = [int(o["uid"]) for o in g.report_all(t, "Wire")]
    pos, t0, n = dict((u, i) for i, u in enumerate(order)), time.time(), 0
    for w in TARGET:
        if w not in pos:
            RAW[tag][str(w)] = None
            continue
        r = g.wire_joints(t, w, index=pos[w]); RAW[tag][str(w)] = r; n += 1           # noqa: E702
        s.fact("JOINTS [{0}] w{1} echo {2} err {3!r} n={4} raw={5}".format(tag, w, r["echo"], r["err"], len(r["joints"] or ()), json.dumps(r["joints"], default=str)[:700]))
    dt = time.time() - t0
    s.fact("JOINTS [{0}] {1} target wires read in {2:.1f} s ({3:.2f} s/read); {4} target uids absent".format(tag, n, dt, dt / max(n, 1), sum(1 for w in TARGET if w not in pos)))
    rest, t1, k = [u for u in order if u not in set(TARGET)], time.time(), 0
    while sweep and k < len(rest) and time.time() - t1 < SWEEP_S:
        RAW[tag][str(rest[k])] = g.wire_joints(t, rest[k], index=pos[rest[k]]); k += 1    # noqa: E702
    RAW["coverage"][tag] = {"wires": len(order), "target_read": n, "sweep_read": k, "sweep_total": len(rest)}
    s.fact("JOINTS [{0}] coverage {1}".format(tag, RAW["coverage"][tag]))
    bad = [w for w, r in RAW[tag].items() if r and (r["err"] or r["echo"] != int(w))]
    s.gate("J-{0} every read echoes its uid with err '' ({1} reads)".format(tag, sum(1 for r in RAW[tag].values() if r)), not bad, bad[:20])
    json.dump(RAW, open(os.path.join(K.BENCH, "diag_c116d_j3_raw2.json"), "w", encoding="utf-8"), indent=1, default=str)   # attempt 1 kept in _raw.json


_Exe = SX.Executor


class JExecutor(_Exe):
    def run(self, *a, **kw):
        phase(ST["s"], ST["s"].work, "before", True)
        return _Exe.run(self, *a, **kw)


_rbw = R.rbw


def rbw_hooked(s, target, tag):
    if tag == "RBW(new)" and not RAW["after"]:
        phase(s, target, "after", True)
    return _rbw(s, target, tag)


def body(s):
    print(__doc__, flush=True)
    s.fact("TARGET {0} wires: 13 outer {1} | PD230 {2} | stubs {3} | no-sink/no-source in the saved R1 graph {4}".format(
        len(TARGET), PRED["shared_sink_nets"], PD230, PRED["stubs"], ODD))
    ST["s"] = s
    SX.Executor, R.rbw, R.SAVE = JExecutor, rbw_hooked, False
    try:
        return R.body(s)
    finally:
        SX.Executor, R.rbw = _Exe, _rbw
        s.gate("J3 the after-rows read ran (before Remove Bad Wires)", bool(RAW["after"]), len(RAW["after"]))


if __name__ == "__main__":
    st = K.Stage(R.BASE["vi"], R.BASE["md5"], "scratch_c116d_bed", preload=False, deadline_min=46,
                 out_json=os.path.join(K.BENCH, "diag_c116d_j3.json"), task="card 116-4 J2/J3")
    rc = K.run(body, st)
    gone = R.DRY or SX.kill_labview_at_exit()
    lo = os.path.join(K.CLAUDEDEV, NETS["leftover"])                               # attempt 1's work copy (its run died before close)
    if not R.DRY and os.path.basename(lo).startswith("scratch_c116") and os.path.exists(lo):
        for _k in range(5):
            try:
                os.remove(lo); break                                                 # noqa: E702
            except OSError:
                time.sleep(3)
        print("  FACT  attempt-1 leftover {0} deleted: {1}".format(NETS["leftover"], not os.path.exists(lo)), flush=True)
    sys.exit(rc if gone else 1)
