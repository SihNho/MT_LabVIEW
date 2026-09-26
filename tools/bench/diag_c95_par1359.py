r"""diag_c95_par1359.py - card 95-4, docs/d1-loop12-17-split-plan.md PD202(d) step 2: claudeDev\D1_s1_par1359_<ts>.vi = BYTE COPY
of S1 (D1_s1_copy.vi, 3e3d23ce) with ONLY ForLoop #1359's parallelism enabled (OpForLoopParSet_v0 via gscript.loop_par_set;
'Number of Static Parallel Instances' NOT written = LabVIEW default, RECORDED). Same route as diag_c92b_anythread.py (cycle 92's
deliverable copy D1_s1_t0at: edit on the stage copy, separate reader, computation_diff vs S1, scripted save, cold re-open).
NOT hidden from the launch gate: stagekit + save => classified; dry + prerun PASS on tools/bench/par1359_95_graph.json with the
FINALIZED plan tools/bench/par1359_95_setplan.json (no uid or terminal name typed here). Rule-1a replay (step 3) is NOT here.
PREDICTION: A 17 ForLoops, #1359 parallel False before; B1 op echo #1359, read-back True, err ''; B2 separate reader
(OpLoopCast_v1) #1359 True, P RECORDED; B3 other 16 loops (uid, parallel, P) identical to BEFORE; C1 ES 1 warm;
D1 computation_diff(S1, copy) 0 rows (added/removed RECORDED); F1 #28233 'init/cont (init:F)' wire == offline (0);
V1 scripted save, md5 != S1; R4 ES 1 COLD + #1359 True cold, P == warm; S1 md5 unchanged; LabVIEW gone at exit.
    py tools/bgrun.py --material --max-min 25 --log tools/bench/diag_c95_par1359.log -- py -u tools/bench/diag_c95_par1359.py"""
import json, os, subprocess, sys, time                                                   # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))  # noqa: E702
import stagekit as K                                                                     # noqa: E402
g = K.g
PL = json.load(open(os.path.join(K.BENCH, "par1359_95_setplan.json"), encoding="utf-8"))
LP, FIR, ROWS = PL["loop"], PL["fir_call"], dict((r["id"], r) for r in PL["decisions"])  # noqa: E702
DRY = bool(getattr(g.report_all, "_dry", False))
g._run.__defaults__ = (6.0, 120.0)
s = K.Stage(os.path.join(g.CLAUDEDEV, PL["input"]["vi"]), PL["input"]["md5"], "par1359_95_stage", preload=False,
            work_name="{0}_{1}.vi".format(PL["output_prefix"], time.strftime("%Y%m%d_%H%M%S")), deadline_min=25.0,
            reserve_s=180.0, out_json=os.path.join(K.BENCH, "par1359_95_stage.json"), task="95-4")


def loops(tag):
    out = []
    for i in range(s.count(LP["class"])):
        r, err = s.safe("loop_cast[{0}] {1}".format(i, tag), lambda i=i: g.loop_cast(s.work, i, LP["class"]))
        r = r or {}
        out.append({"i": i, "uid": r.get("loop_uid"), "par": r.get("parallel_enabled"), "P": r.get("static_instances"),
                    "err": err or r.get("errors")})
    s.fact("LOOPS {0}: {1}".format(tag, json.dumps(out, default=str)))
    return out


def key(rows):
    return [(x["uid"], x["par"], x["P"]) for x in rows if x["uid"] != LP["uid"]]


def body(_):
    s.start(); s.discard_work()                                       # a scratch until the save lands  # noqa: E702
    s.gate("A0 copy ExecState 1 after open", s.es("start") == 1, fatal=True)
    n = s.count(LP["class"])
    s.gate("A {0} ForLoops == plan {1}".format(n, PL["n_forloops"]), n == PL["n_forloops"], fatal=True)
    before = loops("BEFORE")
    mine = [x for x in before if x["uid"] == LP["uid"]]
    s.gate("A2 #{0} present once, parallel False before".format(LP["uid"]), len(mine) == 1 and mine[0]["par"] is False, repr(mine), fatal=True)
    i = s.uid_index(LP["class"], LP["uid"])
    rec = s._op("set_parallel S1", lambda: g.loop_par_set(s.work, i, True, LP["class"]), ROWS["S1"]["what"])
    r = rec["result"] or {}
    s.fact("S1 loop_par_set({0}[{1}], True) -> {2!r} raised {3!r}".format(LP["class"], i, r, rec["err"]))
    s.gate("B1 op echo #{0}, read-back True, err ''".format(LP["uid"]), r.get("loop_uid") == LP["uid"] and r.get("parallel_enabled") is True
           and not r.get("err") and not rec["err"], repr(r)[:99])
    after = loops("AFTER")
    mine = [x for x in after if x["uid"] == LP["uid"]]
    s.gate("B2 separate reader: #{0} parallel True, P recorded".format(LP["uid"]), len(mine) == 1 and mine[0]["par"] is True, repr(mine))
    s.gate("B3 the other {0} loops (uid, parallel, P) identical to BEFORE".format(len(key(before))),
           len(key(before)) == PL["n_forloops"] - 1 and key(after) == key(before), repr([a for a, b in zip(key(after), key(before)) if a != b])[:99])
    s.R["loops"] = {"before": before, "after": after}
    s.gate("C1 ExecState 1 warm after the write", s.es("after S1") == 1, fatal=True)
    JC, V = K.mod("jev_candidates"), K.mod("vigraph")
    G1 = JC.load(JC.S1_KEY)
    lv = K.mod("wiki_build").read_live(s.work, fs_pairs=G1["wiki"]["fs_tunnel_pairs"])
    census = json.load(open(JC._newest("graph_loops_s1_*.json"), encoding="utf-8"))["loops"]
    G2 = JC.from_parts({"terminals": lv["terminals"], "graph_summary": G1["wiki"]["graph_summary"]}, lv["objs"], census,
                       JC.node_labels_default(), lv["fs_tunnel_pairs"], "par1359")
    cd = V.computation_diff(G1, G2)
    s.R["cdiff"] = {"rows": cd["rows"][:20], "added": cd["computation_nodes_added"], "removed": cd["computation_nodes_removed"]}
    s.fact("CDIFF rows {0} added {1!r} removed {2!r}".format(len(cd["rows"]), cd["computation_nodes_added"], cd["computation_nodes_removed"]))
    s.gate("D1 computation_diff(S1, copy): 0 rows", not cd["rows"], repr(cd["rows"][:3])[:99])
    init = [(t["term_uid"], t["wire_uid"]) for t in lv["terminals"] if int(t["owner_uid"]) == FIR["uid"] and t["term_name"] == FIR["init_term"]]
    s.R["fir_call"] = {"init": init, "terms": [(t["term_name"], t["is_source"], t["wire_uid"]) for t in lv["terminals"] if int(t["owner_uid"]) == FIR["uid"]]}
    s.fact("FIR call #{0} terminals {1!r}".format(FIR["uid"], s.R["fir_call"]["terms"]))
    s.gate("F1 #{0} {1!r}: one terminal, wire == offline {2}".format(FIR["uid"], FIR["init_term"], FIR["offline_wire"]),
           len(init) == 1 and int(init[0][1] or 0) == FIR["offline_wire"], repr(init))
    s.R["census"] = {"S1": s.census(PL["census"], "S1", target=s.input_vi), "copy": s.census(PL["census"], "copy")}
    md = s.save()
    s.gate("V1 saved by script, md5 != S1", bool(md) and md != s.input_md5, repr(md), fatal=True)
    s.scratches.remove(s.work)                                        # saved: no longer a scratch
    s.restart()
    s.gate("R4a ExecState 1 COLD (fresh LabVIEW)", s.es("cold") == 1)
    ic = s.uid_index(LP["class"], LP["uid"])
    rc_, err = s.safe("loop_cast cold", lambda: g.loop_cast(s.work, ic, LP["class"]))
    rc_ = rc_ or {}
    warm = [x for x in after if x["uid"] == LP["uid"]]
    s.gate("R4b #{0} COLD: parallel True, P == warm".format(LP["uid"]), rc_.get("loop_uid") == LP["uid"] and rc_.get("parallel_enabled") is True
           and bool(warm) and rc_.get("static_instances") == warm[0]["P"], repr(rc_)[:99])
    s.R["cold"] = rc_


rc = K.run(body, s)
if not DRY:
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4.0)   # noqa: E702
    gone = "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
    s.gate("Z LabVIEW gone at exit", gone)
    s.gate("Z2 S1 md5 unchanged at exit", K.md5(s.input_vi) == s.input_md5)
    s.dump(); rc = s.summary()                                                             # noqa: E702
sys.exit(rc)
