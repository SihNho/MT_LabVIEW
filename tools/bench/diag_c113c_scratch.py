r"""diag_c113c_scratch - card 113-2 T2: SCRATCH VERIFY of the two routes T1 widened (stagexec connect_route, self-test
selftest_stagexec_c113a.log 124/0) on a LOOP owner, live: 'ctltun' b2_04 (CT #28170 -> LoopTunnel #31051 outer face via ForLoop #1359
Terminals[]) and 'ctlsink' b2_07 (LoopTunnel #29172 outer face via ForLoop #29874 Terminals[] -> CT indicator #28786). Both run the EXISTING
op OpCtlSinkWire_v1 (gscript.wire_ctlsink; review archive/peer/2026-09-28-c113b-route.md s4). FIXTURE: the dated scratch byte copy
claudeDev\scratch_c113c_bed_<ts>.vi of the B2a bed (md5 107a3ef1), DELETED at close; nothing saved, no VI run. PLAN sim/c113c/plan_c113c_bed.json
(diag_c113c_plan.log: FINAL, routes ctltun / ctlsink). PRIOR ART: diag_c112c_t1t2.py (this is its cut: LVBackend + Executor RECORD MODE).
PREDICTION: L1 2 ops; E1 every checkpoint's real read == its sim step up to rule D4 (plan_l2b2b_d4.json, toward S1 only); R each sink's
wire has ONE source == the planned source (read back); IB b2_04's wire Is Broken? False on the ordered idempotent cfw second pass (sink on
#1359's Terminals[], wire_delta 0); RBW on a scratch-of-scratch deletes neither new wire (b2_07's sink is a panel terminal - no Nodes[]
second pass exists, so LabVIEW's own broken-wire removal is its Is Broken? reader); ES ExecState unchanged; HF handles flat (+-100) in steady
state (after op 1's first load; run 2); H bed md5 unchanged, scratches deleted, LabVIEW gone. PASS writes tools/bench/scratch_verify/stagexec.ctltun_loop_<ts>.json + .ctlsink_loop_<ts>.json.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c113c_scratch.log -- py -u tools/bench/diag_c113c_scratch.py"""
import json, os, sys, time                                                          # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, stagexec as SX, allterms as AT                  # noqa: E401,E402
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                 # noqa: E731
PLAN = os.path.join(K.BENCH, "sim/c113c/plan_c113c_bed.json")                       # ONE literal: stage_prerun.plan_files reads it
P = J(PLAN); BASE = J(K.ROOT, P["finalized"]["base"]["path"]); A = P["actions"]   # noqa: E702
DRY = bool(getattr(g.report_all, "_dry", False))
D4 = K.d4_load(os.path.join(K.BENCH, "plan_l2b2b_d4.json"))
REC = os.path.join(K.BENCH, "scratch_verify")


def body(s):
    print(__doc__, flush=True)
    s.gate("L0 the plan is FINAL and open_rows_match; routes ctltun/ctlsink", P.get("final") is True and P["finalized"].get("open_rows_match") is True
           and [r.get("route") for r in P["finalized"]["route_check"]["rows"]] == ["ctltun", "ctlsink"], (K.md5(PLAN), P["finalized"]["route_check"]["status"]), fatal=True)
    s.gate("L0b D4 S1 md5 pinned", D4["s1_md5_got"] == D4["s1"]["md5"], D4["s1_md5_got"], fatal=True)
    s.start(); s.discard_work(); es0 = s.es("before the rows"); bp = K.mod("bench_prep"); h0 = bp.labview_handles()   # noqa: E702
    be = SX.DryPlanBE(s, P, PLAN, BASE) if DRY else SX.LVBackend(s, BASE["fs_tunnel_pairs"], sink_gates=[], gates={}, mem_stop_mb=SX.MEM_STOP_MB)
    x = SX.Executor(PLAN, be, log=lambda m: print(m, flush=True), checkpoints=tuple(range(0, len(A) + 1)), record=True)
    s.gate("L1 2 plan actions -> 2 ops", len(x.ops) == len(A) == 2, [(o["kind"], o["acts"]) for o in x.ops], fatal=True)
    try:
        real = x.run()
    except SX.ExecStop as e:
        return SX.report_stop(s, x, be, e)
    h1 = None if DRY else bp.labview_handles()
    for r in x.report:
        s.fact("OP {0}".format(json.dumps(dict((k, r.get(k)) for k in ("k", "ids", "result")), default=str)[:700]))
    nm = dict((int(r["term_uid"]), (int(r["owner_uid"]), r["term_name"])) for k in range(len(A) + 1) for r in x.step(k)["state"]["terminals"])
    nm.update((int(r["term_uid"]), (int(r["owner_uid"]), r["term_name"])) for r in real)
    nm.update((int(t), (int(w[0]), w[2])) for d in x.diffs for t, w in (d["diff"].get("who") or {}).items() if w)
    e1ok, acc, bad = K.d4_e1([(d["k"], d["diff"]) for d in x.diffs], nm, D4)
    for k, t, n, nme in acc: s.fact("D4-ACCEPT ck {0} term t{1} node #{2} name {3!r} in-S1 yes".format(k, t, n, nme))  # noqa: E701
    s.gate("E1 every checkpoint's real read == its sim step up to D4 (toward S1 only)", e1ok, {"bad": bad[:30], "accepted": len(acc)})
    B, sw = x.bind["term"], {}
    for a in A:
        sk, sr = B.get(a["dst"]["term_uid"], a["dst"]["term_uid"]), B.get(a["src"]["term_uid"], a["src"]["term_uid"])
        hit = [r for r in real if int(r["term_uid"]) == sk]
        w = sw[a["id"]] = int(hit[0]["wire_uid"] or 0) if len(hit) == 1 else 0
        srcs = sorted(int(r["term_uid"]) for r in real if w and int(r["wire_uid"] or 0) == w and r["is_source"])
        s.gate("R {0}: sink t{1} has a wire whose ONE source is t{2} (read back)".format(a["id"], sk, sr), w != 0 and srcs == [sr], (w, srcs))
    s.gate("ES ExecState unchanged by the rows", s.es("after the rows") == es0, es0)
    if DRY:
        print("GATE IB/RBW/HF NOT RUNNABLE IN DRY: live readers", flush=True); s.dump(); return   # noqa: E702
    # run 1 (diag_c113c_scratch.log, 01:18): +211 over the run = +92 first graph read + +32 pre + +91 FIRST op call (the op VI's first
    # load), then +1/+1/+1 - so HF judges the STEADY STATE: from the read after op 1 (op VI loaded) to the last read, not first-load cost
    mr = [r for r in be.meter.rows if r["tag"] == "read" and r["handles"] is not None]
    hs = [r["handles"] for r in mr if r["k"] == 1][:1] + [mr[-1]["handles"]] if mr else []
    s.fact("HF handles: start {0} -> after the rows {1} (d {2}, incl. first loads); steady state read k1 -> last read {3}".format(h0, h1, (h1 or 0) - (h0 or 0), hs))
    s.gate("HF handle count flat (+-100) in steady state, from the read after op 1 to the last read", len(hs) == 2 and abs(hs[1] - hs[0]) <= 100, hs)
    ib = {"err": "not run"}
    try:                                                                            # b2_04: sink on #1359's Terminals[] -> cfw second pass
        F = K.mod("build_opconnectfromwire_v0")
        (dd, dn, dt), how = be.addr.triple(real, B.get(A[0]["dst"]["term_uid"], A[0]["dst"]["term_uid"]), False, x.loop_of)
        src = [h for h in F.wire_source_owner(s.work, sw["b2_04"], n=8) if h.get("is_source")]
        s.fact("IB b2_04 sink {0}; wire {1} source rows {2}".format(how, sw["b2_04"], src))
        w0 = g.count(s.work, "Wire")
        dw, _es, err, sub = F.connect_from_wire(s.work, sw["b2_04"], int(src[0]["i"]), dd, dn, dt, J(F.MAP_OUT)) if len(src) == 1 else (None, None, "sources {0}".format(len(src)), {})
        ib = {"delta": g.count(s.work, "Wire") - w0, "err": err, "is_broken": (sub or {}).get("Is Broken?"), "uid2": (sub or {}).get("UID 2")}
    except Exception as e:                                                          # noqa: BLE001
        ib = {"err": repr(e)[:300]}
    s.fact("IB b2_04 ORDERED SECOND PASS {0}".format(ib))
    s.gate("IB b2_04 Wire.Is Broken? False on the ordered idempotent second pass, wire_delta 0", ib.get("is_broken") is False and ib.get("delta") == 0, ib)
    rb = s.scratch("rbw", s.work); w_rb = set(AT.all_wire_uids(rb)[0])             # noqa: E702
    s.broken_wire_count(target=rb, tag="RBW"); gone = w_rb - set(AT.all_wire_uids(rb)[0])   # noqa: E702
    s.fact("RBW deleted {0}".format(sorted(gone)[:60]))
    s.gate("RBW Remove Bad Wires deletes neither new wire {0} (LabVIEW's own Is Broken? verdict)".format(sw), all(sw.values()) and not (set(sw.values()) & gone),
           {"new": sw, "gone_n": len(gone)})
    s.drop_scratch(rb, "RBW")
    s.R["c113c"] = {"ops": [(o["kind"], o["acts"]) for o in x.ops], "wires": sw, "is_broken_b2_04": ib, "rbw_gone": len(gone), "handles": [h0, h1], "d4_accepted": acc}
    s.dump()


if __name__ == "__main__":
    st = K.Stage(BASE["vi"], BASE["md5"], "scratch_c113c_bed", preload=False, deadline_min=25,
                 out_json=os.path.join(K.BENCH, "diag_c113c_scratch.json"), task="card 113-2 T2")
    rc = K.run(body, st)
    gone = DRY or SX.kill_labview_at_exit()
    if rc == 0 and gone and not DRY:
        os.makedirs(REC, exist_ok=True)
        for fn, route in (("stagexec.ctltun_loop", "b2_04 ctltun: CT #28170 -> LoopTunnel #31051 outer via ForLoop #1359 Terminals[]"),
                          ("stagexec.ctlsink_loop", "b2_07 ctlsink: LoopTunnel #29172 outer via ForLoop #29874 Terminals[] -> CT #28786")):
            json.dump({"function": fn, "status": "PASS", "t": time.time(), "card": "113-2", "route": route, "op": "OpCtlSinkWire_v1 (gscript.wire_ctlsink)",
                       "fixture": "scratch byte copy of claudeDev\\D1_l2_b2a_20260928_001426.vi (deleted)", "plan": {"path": os.path.relpath(PLAN, K.ROOT),
                       "md5": K.md5(PLAN)}, "facts": st.R.get("c113c"), "log": "tools/bench/diag_c113c_scratch.log"},
                      open(os.path.join(REC, "{0}_{1}.json".format(fn, st.stamp)), "w", encoding="utf-8"), indent=1, default=str)
    sys.exit(rc if gone else 1)
