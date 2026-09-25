r"""ctsrc_l2a1_82 - card 82-2 P2: measure the ONE candidate verb for a BARE ControlTerminal SOURCE on nested #23166.
PRIOR ART / CANDIDATES (P1, checked before writing):
  C1 gscript.wire_control:1998 (OpWireCtl_v0: Get Controls on Diagram[src_diagram_index] by LABEL -> Wire Inputs onto
     Traverse(Class)[i].<name>) - wired 'Auto-Reset' from nested Diagram idx 43, sink wire 0->1231 (docs/d1-route-b-plan.md:99-101).
  C2 gscript.connect_ctl:1024 - CT is the SINK and the source is a TOP-LEVEL Nodes[] triple: not this shape.
  C3 gscript.connect_ctl_ind:1050 - both ends panel terminals: not this shape.  C4 connect_nested_v1 - Nodes[] triples only
     (a CT is not in Nodes[], stagexec.py:532).  C5 wire_indicators - panel SINK + wired source.  C6 probe_move_ctlterm_v0.py:327-351
     - Q4 identifies moved CTs by panel_wiring; no wiring verb.  => only C1 is measured.
METHOD: the real executor (stagexec.lv_run's skeleton) applies ops 1-30 on a D1_k scratch; op 31 stops OFFLINE-equivalently
(CONNECT-NO-VERB, before any mutation). Then each row is wired by C1 and READ BACK. No op VI built; nothing saved.
PREDICTION CONTRACT:
  P0 ops 1-30 diff 0 and the stop is op 31 CONNECT-NO-VERB     per row (rw_5634_10256, rw_17487_9676):
  R1 wire_control err None, Wire +1     R2 the new wire's ONLY source terminal == the CT uid, ONLY sink == the plan sink
  R3 ordered idempotent second pass (connect_from_wire on that wire): wire_delta 0, `Wire.Is Broken?` False
  R4 (row 1 only) the real graph == plan step of act 35 (compare n == 0)
  H D1_k md5 unchanged, scratch deleted, refs closed, handles recorded, LabVIEW gone.
    MATERIAL=1 py tools/bgrun.py --max-min 30 --log tools/bench/ctsrc_l2a1_82.log -- py -u tools/bench/ctsrc_l2a1_82.py"""
import json, os, subprocess, sys, time                                              # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, stagexec as SX                                  # noqa: E401,E402
PLAN = os.path.join(K.BENCH, "sim/l2a1/plan_l2a1.json")
P, _ = SX.load_final_plan(PLAN)
BASE = SX._j(SX._abs(P["finalized"]["base"]["path"]))
BED, BED_MD5 = BASE["vi"], BASE["md5"]
FS = BASE["fs_tunnel_pairs"]                        # the recipe's own source (stage_d1_l2a1.py:59)
ROWS = (("rw_5634_10256", 5634, 10256), ("rw_17487_9676", 17487, 9676))


def one(real, t):
    r = [x for x in real if x["term_uid"] == t]
    if len(r) != 1:
        raise SX.ExecStop("#{0}: {1} rows".format(t, len(r)))
    return r[0]


def body(s):
    print(__doc__, flush=True)
    s.start()
    s.discard_work()
    bp = K.mod("bench_prep")
    s.fact("handles after start {0}".format(bp.labview_handles()))
    be = SX.LVBackend(s, FS)
    ex = SX.Executor(PLAN, be, log=lambda m: print(m, flush=True))
    stop = ""
    try:
        ex.run()
    except SX.ExecStop as e:
        stop = str(e)
    ok30 = len(ex.report) == 31 and all(r["diff"]["n"] == 0 for r in ex.report)
    s.gate("P0 ops 1-30 diff 0 and the stop is op 31 CONNECT-NO-VERB", ok30 and stop.startswith("CONNECT-NO-VERB"),
           "{0} records; stop {1}".format(len(ex.report), stop[:160]), fatal=True)
    F = K.mod("build_opconnectfromwire_v0")
    lab = json.load(open(F.MAP_OUT, encoding="utf-8"))
    real = be.read()
    table = []
    for k, (rid, ct, snk) in enumerate(ROWS):
        rc, rs = one(real, ct), one(real, snk)
        s.fact("{0}: CT #{1} {2!r} wire {3} diag #{4}; sink #{5} {6!r} on {7} #{8} wire {9} diag #{10}".format(
            rid, ct, rc["term_name"], rc["wire_uid"], rc["frame_diagram"], snk, rs["term_name"], rs["owner_class"],
            rs["owner_uid"], rs["wire_uid"], rs["frame_diagram"]))
        didx = be.addr.rd.diagrams().index(int(rc["frame_diagram"]))
        di = s.uid_index(rs["owner_class"], int(rs["owner_uid"]))
        w0 = s.count("Wire")
        rec = s._op("wire_control", lambda: g.wire_control(s.work, [rc["term_name"]], rs["owner_class"], di,
                                                             [rs["term_name"]], src_diagram_index=didx),
                    "{0!r}@D[{1}] -> {2}[{3}].{4!r}".format(rc["term_name"], didx, rs["owner_class"], di, rs["term_name"]))
        s.junk_purge(rid)
        dw = s.count("Wire") - w0
        s.gate("R1 {0} wire_control err None, Wire +1".format(rid), not rec["err"] and dw == 1,
               "err {0!r} delta {1}".format(rec["err"], dw))
        real2 = be.read()
        w = int(one(real2, ct)["wire_uid"] or 0)
        srcs = sorted(x["term_uid"] for x in real2 if w and x["wire_uid"] == w and x["is_source"])
        snks = sorted(x["term_uid"] for x in real2 if w and x["wire_uid"] == w and not x["is_source"])
        s.gate("R2 {0} wire w{1}: sources {2} == [{3}], sinks {4} == [{5}]".format(rid, w, srcs, ct, snks, snk),
               w and srcs == [ct] and snks == [snk])
        ns = s.net_sources(w, tag=rid) if w else {"walk": []}
        hit = [x for x in (ns.get("walk") or []) if x.get("is_source")]
        ib, d2, err2 = None, None, None
        if w and len(hit) == 1:
            (dd, nn, tt), how = be.addr.triple(real2, snk, False)
            res, err2 = s.safe("second pass", lambda: F.connect_from_wire(s.work, w, int(hit[0]["i"]), dd, nn, tt, lab))
            s.junk_purge(rid + " 2nd")
            if res:
                d2, ib, err2 = res[0], (res[3] or {}).get("Is Broken?"), err2 or res[2]
        s.gate("R3 {0} ordered second pass: wire_delta 0, Is Broken? False".format(rid), d2 == 0 and ib is False,
               "delta {0!r} Is Broken? {1!r} err {2!r} walk-sources {3}".format(d2, ib, err2, hit[:2]))
        if k == 0:
            n = ex.ops[30]["acts"][-1]
            d = SX.compare(ex.step(n)["state"]["terminals"], real2, ex.bind, ex.allow)
            s.gate("R4 {0}: real graph == plan step {1} (compare n 0)".format(rid, n), d["n"] == 0,
                   json.dumps({a: b for a, b in d.items() if b and a != "n"}, default=str)[:600])
        table.append({"row": rid, "err": rec["err"], "wire_delta": dw, "wire": w, "sources": srcs, "sinks": snks,
                      "second_delta": d2, "is_broken": ib, "second_err": err2})
        real = real2
    s.R["p2_table"] = table
    s.fact("P2 TABLE {0}".format(json.dumps(table, default=str)))
    s.fact("handles after rows {0}".format(bp.labview_handles()))


if __name__ == "__main__":
    st = time.strftime("%Y%m%d_%H%M%S")
    s = K.Stage(BED, BED_MD5, "ctsrc82", work_name="D1_k_scratch_ctsrc82_{0}.vi".format(st), preload=False,
                deadline_min=27, out_json=os.path.join(K.BENCH, "ctsrc_l2a1_82.json"), task="card 82-2")
    rc = K.run(body, s)
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60)
    time.sleep(4.0)
    tl = subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
    s.gate("H1 LabVIEW process gone at the end", "labview.exe" not in tl)
    s.gate("H2 D1_k md5 unchanged", K.md5(BED) == BED_MD5, K.md5(BED))
    s.gate("H3 scratch copy deleted", not os.path.exists(s.work), s.work)
    s.summary()
    sys.exit(1 if s.fails else 0)
