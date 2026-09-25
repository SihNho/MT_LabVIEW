r"""constsrc_l2a1_85 - card 85-1 P2: the new constant-source verb (gscript.wire_const = OpConstWire_v1, built and negative-
tested in tools/bench/constsrc_l2a1_85_build.log 31/0) exercised THROUGH the stagexec 'const' route at op 35 on a D1_k scratch.
PRIOR ART: tools/bench/constsrc_l2a1_82.py (same executor-to-op-35 skeleton, same read-back gates; C1/C2 failed there).
METHOD: the real executor (LVBackend, routing as in stagexec md5 after card 85-1) runs ops 1..K where K = the op carrying
rw_10943_10877 (both constant rows are routed 'const'); nothing is saved; the scratch is deleted.
PREDICTION CONTRACT:
  P0 every executed op's real graph == its plan step (diff 0), both constant rows routed 'const', no ExecStop
  per row (rw_10738_11055 #10739/#10738 -> #10950 #11055; rw_10943_10877 #10929/#10943 -> #10757 #10877):
     wire_const err '' and Wire +1; the new wire's ONLY source terminal == the constant's terminal, owner == the constant uid;
     ONLY sink == the plan sink; ordered second pass (connect_from_wire) wire_delta 0 and Is Broken? False
  H  D1_k md5 unchanged, scratch deleted, LabVIEW gone.
    py tools/bgrun.py --material --max-min 45 --log tools/bench/constsrc_l2a1_85.log -- py -u tools/bench/constsrc_l2a1_85.py"""
import json, os, subprocess, sys, time                                              # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, stagexec as SX                                                # noqa: E401,E402
PLAN = os.path.join(K.BENCH, "sim/l2a1/plan_l2a1.json")
P, _ = SX.load_final_plan(PLAN)
BASE = SX._j(SX._abs(P["finalized"]["base"]["path"]))
BED, BED_MD5, FS = BASE["vi"], BASE["md5"], BASE["fs_tunnel_pairs"]
ROWS = (("rw_10738_11055", 10739, 10738, 10950, 11055), ("rw_10943_10877", 10929, 10943, 10757, 10877))
T0 = time.time()


def stamp(s, what):
    s.fact("STAMP {0:7.1f} s {1}".format(time.time() - T0, what))


def body(s):
    print(__doc__, flush=True)
    s.start(); s.discard_work(); stamp(s, "started")                                # noqa: E702
    be = SX.LVBackend(s, FS)
    ex = SX.Executor(PLAN, be, log=lambda m: print(m, flush=True))
    A = ex.plan["actions"]
    k = next(i for i, o in enumerate(ex.ops) if "rw_10943_10877" in [A[n - 1].get("id") for n in o["acts"]])
    ex.ops = ex.ops[:k + 1]
    s.fact("EXECUTING ops 1..{0} (the last carries rw_10943_10877)".format(k + 1))
    stop = ""
    try:
        ex.run()
    except SX.ExecStop as e:
        stop = str(e)
    stamp(s, "executor done")
    diffs = [r["diff"]["n"] for r in ex.report if r.get("diff")]
    hows = [(r.get("ids"), (r.get("result") or {}).get("how")) for r in ex.report if any(i in (x[0] for x in ROWS) for i in (r.get("ids") or []))]
    s.gate("P0 ops 1..{0} diff 0, both constant rows routed 'const', no stop".format(k + 1),
           not stop and len(diffs) == k + 2 and not any(diffs) and len(hows) == 2 and all(h and h[0] == "const" for _i, h in hows),
           "stop {0!r}; diffs {1}; hows {2}".format(stop[:300], sum(diffs), json.dumps(hows, default=str)[:400]), fatal=True)
    wc = [o for o in s.R["ops"] if o["verb"] == "wire_const"]
    F = K.mod("build_opconnectfromwire_v0")
    lab = json.load(open(F.MAP_OUT, encoding="utf-8"))
    real, table = be.read(), []
    for j, (rid, cu, ct, nu, snk) in enumerate(ROWS):
        rc = [x for x in real if x["term_uid"] == ct][0]
        w = int(rc["wire_uid"] or 0)
        srcs = sorted(x["term_uid"] for x in real if w and x["wire_uid"] == w and x["is_source"])
        snks = sorted(x["term_uid"] for x in real if w and x["wire_uid"] == w and not x["is_source"])
        owner = sorted(set(x["owner_uid"] for x in real if w and x["wire_uid"] == w and x["is_source"]))
        ns = s.net_sources(w, tag=rid) if w else {"walk": []}
        hit = [x for x in (ns.get("walk") or []) if x.get("is_source")]
        d2, ib, err2 = None, None, None
        if w and len(hit) == 1:
            (dd, nn, tt), _how = be.addr.triple(real, snk, False)
            res, err2 = s.safe("second pass", lambda: F.connect_from_wire(s.work, w, int(hit[0]["i"]), dd, nn, tt, lab))
            s.junk_purge(rid + " 2nd")
            if res:
                d2, ib, err2 = res[0], (res[3] or {}).get("Is Broken?"), err2 or res[2]
        res1 = wc[j]["result"] if j < len(wc) else None
        row = {"row": rid, "op_err": wc[j]["err"] if j < len(wc) else "missing", "wire_const": res1, "wire": w, "sources": srcs,
               "source_owner": owner, "sinks": snks, "second_delta": d2, "is_broken": ib, "second_err": err2}
        ok = (j < len(wc) and not wc[j]["err"] and res1 and res1[0] == 1 and not res1[1] and srcs == [ct] and owner == [cu]
              and snks == [snk] and d2 == 0 and ib is False)
        s.gate("P2 {0}: wire_const Wire +1 no error; sole source #{1} (owner #{2}); sole sink #{3}; 2nd pass 0 / Is Broken? False".format(
            rid, ct, cu, snk), ok, json.dumps(row, default=str)[:600])
        table.append(dict(row, **{"pass": ok}))
        real = be.read()
    s.R["p2_table"] = table
    s.fact("P2 TABLE {0}".format(json.dumps(table, default=str)))
    s.dump(); stamp(s, "dumped")                                                     # noqa: E702


if __name__ == "__main__":
    st = time.strftime("%Y%m%d_%H%M%S")
    s = K.Stage(BED, BED_MD5, "constsrc85", work_name="D1_k_scratch_constsrc85_{0}.vi".format(st), preload=False,
                deadline_min=40, out_json=os.path.join(K.BENCH, "constsrc_l2a1_85.json"), task="card 85-1 P2")
    rc = K.run(body, s)
    stamp(s, "K.run returned")
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60)
    time.sleep(4.0)
    tl = subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
    s.gate("H1 LabVIEW process gone at the end", "labview.exe" not in tl)
    s.gate("H2 D1_k md5 unchanged", K.md5(BED) == BED_MD5, K.md5(BED))
    s.gate("H3 scratch copy deleted", not os.path.exists(s.work), s.work)
    s.summary()
    sys.exit(1 if s.fails else 0)
