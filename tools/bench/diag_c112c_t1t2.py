r"""diag_c112c_t1t2 - card 112-3 W0: SCRATCH VERIFY of T1 (stagexec 'wire_sr' on a register that EXISTS on the base - SRB1, the
Void register B1 created, Shift Registers[4] of WhileLoop #10170) and T2 ('ctltun': CT #403 -> case-selector Tunnel #2276 outer,
OpCtlSinkWire_v1 roles reversed). FIXTURE: the dated scratch byte copy claudeDev\scratch_c112c_bed_<ts>.vi of the bed (graph
tools/bench/graph_l2b1_20260927.json, dumped by cycle 111), DELETED at close - nothing is saved, no VI is run (reviews
archive/peer/2026-09-27-c112c-fixture.md s2, -c112c-rows.md s5). PLAN sim/c112c/plan_c112c_bed.json (diag_c112c_plan.log: final,
route wire_sr:RightIn / wire_sr:LeftIn / ctltun, rows copied from plan_l2b2a_in.json). PRIOR ART: stage_d1_l2b2a.py (this is its
cut: LVBackend + Executor), stagexec RECORD MODE (card 101-4) so a step diff is logged, not fatal. No new op.
PREDICTION: L1 3 ops (connect x3 -> wire_sr RightIn, wire_sr LeftIn, connect/ctltun); E1 every op's real read == its sim step,
EXCEPT diffs whose terminals all sit on #8634/#29625 (split_plan_111_l2b2.md s3 cascade: allowed either way, logged); R each
re-wired sink's wire has exactly ONE source == the planned source; ES ExecState unchanged (0, broken by design); H bed md5
unchanged, scratch deleted, LabVIEW gone. PASS writes tools/bench/scratch_verify/{stagexec.op:wire_sr,stagexec.op:connect}_<ts>.json.
    py tools/bgrun.py --material --max-min 40 --log tools/bench/diag_c112c_t1t2.log -- py -u tools/bench/diag_c112c_t1t2.py"""
import json, os, sys, time                                                          # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, stagexec as SX                                  # noqa: E401,E402
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                 # noqa: E731
PLAN = os.path.join(K.BENCH, "sim/c112c/plan_c112c_bed.json")                       # ONE literal: stage_prerun.plan_files reads it
P = J(PLAN); BASE = J(K.ROOT, P["finalized"]["base"]["path"]); A = P["actions"]   # noqa: E702
DRY = bool(getattr(g.report_all, "_dry", False))
# split_plan_111_l2b2.md s3 allow-either owners = the nodes whose 'array' row the scratch leaves open (diag_c112c_plan.log ADDED)
CASCADE = tuple(sorted(set(int(r["node"]) for r in P["open_rows"] if "scratch c112c" in r.get("why", ""))))
REC = os.path.join(K.BENCH, "scratch_verify")


def uids_of(d):
    out = set()
    for k in ("only_sim_terms", "only_real_terms", "dangling_sim_only", "dangling_real_only"):
        out |= set(int(t) for t in d.get(k) or [])
    for k in ("only_sim_edges", "only_real_edges"):
        for e in d.get(k) or []:
            out |= set(int(t) for t in e)
    return out


def body(s):
    print(__doc__, flush=True)
    s.gate("L0 the plan is FINAL and open_rows_match", P.get("final") is True and P["finalized"].get("open_rows_match") is True,
           (K.md5(PLAN), P["finalized"].get("route_check", {}).get("status")), fatal=True)
    s.start(); s.discard_work(); es0 = s.es("before the rows")                       # noqa: E702
    be = SX.DryPlanBE(s, P, PLAN, BASE) if DRY else SX.LVBackend(s, BASE["fs_tunnel_pairs"], sink_gates=[], gates={}, mem_stop_mb=SX.MEM_STOP_MB)
    x = SX.Executor(PLAN, be, log=lambda m: print(m, flush=True), checkpoints=tuple(range(0, len(A) + 1)), record=True)
    s.gate("L1 3 plan actions -> 3 ops", len(x.ops) == len(A) == 3, [(o["kind"], o["acts"]) for o in x.ops], fatal=True)
    try:
        real = x.run()
    except SX.ExecStop as e:
        return SX.report_stop(s, x, be, e)
    s.R["stagexec"] = x.report
    for r in x.report:
        s.fact("OP {0}".format(json.dumps(dict((k, r.get(k)) for k in ("k", "kind", "ids", "result", "how")), default=str)[:700]))
    own = dict((int(r["term_uid"]), int(r["owner_uid"])) for r in list(real) + list(BASE["terminals"]))
    for st in range(len(A) + 1):
        own.update((int(r["term_uid"]), int(r["owner_uid"])) for r in x.step(st)["state"]["terminals"])
    bad, allowed = [], []
    for d in x.diffs:
        u = uids_of(d["diff"])
        owners = sorted(set(own.get(t, -1) for t in u))
        (allowed if owners and set(owners) <= set(CASCADE) else bad).append((d["k"], d["ids"], owners, sorted(u)[:20]))
        s.fact("STEP-{0} k {1} ids {2} owners {3} class {4}: {5}".format("ALLOW" if set(owners) <= set(CASCADE) else "DIFF", d["k"], d["ids"],
               owners, d.get("class"), json.dumps(dict((k, v) for k, v in d["diff"].items() if v and k != "who"), default=str)[:900]))
    s.gate("E1 every op's real read == its sim step, except #8634/#29625 cascade diffs (allow-either, logged: {0})".format(len(allowed)),
           not bad, bad)
    B = x.bind["term"]
    for a in A:
        sk, sr = B.get(a["dst"]["term_uid"], a["dst"]["term_uid"]), B.get(a["src"]["term_uid"], a["src"]["term_uid"])
        hit = [r for r in real if int(r["term_uid"]) == sk]
        w = int(hit[0]["wire_uid"] or 0) if len(hit) == 1 else 0
        srcs = sorted(int(r["term_uid"]) for r in real if w and int(r["wire_uid"] or 0) == w and r["is_source"])
        s.gate("R {0}: sink t{1} has a wire whose ONE source is t{2} (read back)".format(a["id"], sk, sr), w != 0 and srcs == [sr], (w, srcs))
    s.gate("ES ExecState unchanged by the rows", s.es("after the rows") == es0, es0)
    s.R["c112c"] = {"ops": [(o["kind"], o.get("variant"), o["acts"]) for o in x.ops], "allowed": allowed, "bad": bad}
    s.dump()


if __name__ == "__main__":
    st = K.Stage(BASE["vi"], BASE["md5"], "scratch_c112c_bed", preload=False, deadline_min=35,
                 out_json=os.path.join(K.BENCH, "diag_c112c_t1t2.json"), task="card 112-3 W0")
    rc = K.run(body, st)
    gone = DRY or SX.kill_labview_at_exit()
    if rc == 0 and gone and not DRY:
        os.makedirs(REC, exist_ok=True)
        for fn, route in (("stagexec.op:wire_sr", "T1 wire_sr RightIn/LeftIn on base register SRB1 (Void, Shift Registers[4] of #10170)"),
                          ("stagexec.op:connect", "T2 ctltun: CT #403 -> case selector Tunnel #2276 outer via owner #2222 Terminals[0]")):
            json.dump({"function": fn, "status": "PASS", "t": time.time(), "card": "112-3", "route": route, "fixture":
                       "scratch byte copy of claudeDev\\D1_l2_b1_20260927_193100.vi (deleted)", "plan": {"path": os.path.relpath(PLAN, K.ROOT),
                       "md5": K.md5(PLAN)}, "facts": st.R.get("c112c"), "log": "tools/bench/diag_c112c_t1t2.log"},
                      open(os.path.join(REC, "{0}_{1}.json".format(fn.replace(":", "_"), st.stamp)), "w", encoding="utf-8"), indent=1, default=str)
    sys.exit(rc if gone else 1)
