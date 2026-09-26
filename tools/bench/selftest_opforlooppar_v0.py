r"""selftest_opforlooppar_v0.py - card 95-4: FUNCTIONAL self-test of OpForLoopParSet_v0 (gscript.loop_par_set) on its OWN
scratch VI: a unique byte copy of claudeDev\HARNESS_copyloop.vi (1 For loop #239, 0 While loops - graph
tools/bench/graph_harness_copyloop_c95.json). Never saved; deleted by stagekit close(); the donor's md5 is gated unchanged.
ROWS ONLY FROM THE FINALIZED PLAN tools/bench/par1359_95_stplan.json. Independent cross-check reader: OpLoopCast_v1
(g.loop_cast) - a different op reads the same property after each write.
PREDICTION: R0 uid echo + parallel False; S1 set True -> op True, uid echo, err '', R1 loop_cast True, static P RECORDED;
S2 set False -> False/False; N1 WhileLoop[0] and N2 Diagram[0] -> err non-empty (refused), R3 the For loop still False;
H1 20 calls no error, handles flat +-100 after 20 s idle; ExecState recorded after each write (not gated).
    py tools/bgrun.py --material --max-min 15 --log tools/bench/selftest_opforlooppar_v0.log -- py -u tools/bench/selftest_opforlooppar_v0.py"""
import json, os, subprocess, sys, time                                                   # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))  # noqa: E702
import stagekit as K                                                                     # noqa: E402
g = K.g
PL = json.load(open(os.path.join(K.BENCH, "par1359_95_stplan.json"), encoding="utf-8"))
LP, ROWS = PL["loop"], dict((r["id"], r) for r in PL["decisions"])                       # noqa: E702
DRY = bool(getattr(g.report_all, "_dry", False))
g._run.__defaults__ = (6.0, 90.0)
s = K.Stage(os.path.join(g.CLAUDEDEV, PL["input"]["vi"]), PL["input"]["md5"], "selftest_opforlooppar_v0",
            work_name="{0}_{1}.vi".format(PL["work_prefix"], time.strftime("%Y%m%d_%H%M%S")), preload=False,
            deadline_min=13.0, reserve_s=150.0, task="95-4")


def setp(rid, enable, cls, index):
    rec = s._op("set_parallel {0}".format(rid), lambda: g.loop_par_set(s.work, index, enable, cls), ROWS[rid]["what"])
    r = rec["result"] or {}
    s.fact("{0} loop_par_set({1}[{2}], {3!r}) -> {4!r} raised {5!r}".format(rid, cls, index, enable, r, rec["err"]))
    s.es("after " + rid)
    return r, rec["err"]


def xread(rid):
    r, err = s.safe("loop_cast " + rid, lambda: g.loop_cast(s.work, LP["index"], LP["class"]))
    r = r or {}
    s.fact("{0} loop_cast -> uid {1!r} parallel {2!r} P {3!r} errors {4!r} {5}".format(
        rid, r.get("loop_uid"), r.get("parallel_enabled"), r.get("static_instances"), r.get("errors"), err))
    return r


def body(_):
    s.start(); s.discard_work()                                                          # noqa: E702
    nf, nw = s.count(LP["class"]), s.count("WhileLoop")
    s.fact("scratch census {0} {1} WhileLoop {2}".format(LP["class"], nf, nw))
    x = xread("R0")
    s.gate("R0 scratch has one For loop #{0}, parallel False before".format(LP["uid"]),
           nf == 1 and x.get("loop_uid") == LP["uid"] and x.get("parallel_enabled") is False, repr(x))
    r, e = setp("S1", True, LP["class"], LP["index"])
    x = xread("R1")
    s.gate("S1 set True: op reads True, err '', uid echo", r.get("parallel_enabled") is True and not r.get("err") and not e
           and r.get("loop_uid") == LP["uid"], repr(r))
    s.gate("R1 independent reader (OpLoopCast_v1) reads True", x.get("parallel_enabled") is True, repr(x.get("parallel_enabled")))
    s.R["S1"] = {"op": r, "loop_cast": x}
    r, e = setp("S2", False, LP["class"], LP["index"])
    x = xread("R2")
    s.gate("S2 set False: op reads False, err ''", r.get("parallel_enabled") is False and not r.get("err") and not e, repr(r))
    s.gate("R2 independent reader reads False", x.get("parallel_enabled") is False, repr(x.get("parallel_enabled")))
    s.R["S2"] = {"op": r, "loop_cast": x}
    for rid, neg in zip(("N1", "N2"), PL["negative"]):
        r, e = setp(rid, True, neg["class"], neg["index"])
        s.gate("{0} {1}[{2}] REFUSED: error out non-empty".format(rid, neg["class"], neg["index"]), bool(r.get("err") or e),
               repr(r.get("err") or e)[:99])
        s.R[rid] = r
    x = xread("R3")
    s.gate("R3 the For loop is still False after the refused calls", x.get("parallel_enabled") is False, repr(x.get("parallel_enabled")))
    bp = K.mod("bench_prep")
    for _ in range(3):
        g.loop_par_set(s.work, LP["index"], False, LP["class"])
    h0 = bp.labview_handles()
    errs = sum(1 for _ in range(PL["calls"]) if (g.loop_par_set(s.work, LP["index"], False, LP["class"]) or {}).get("err"))
    h1 = bp.labview_handles(); time.sleep(0.0 if DRY else 20.0); h2 = bp.labview_handles()  # noqa: E702
    s.R["H1"] = {"h0": h0, "h1": h1, "h2": h2, "errs": errs}
    s.gate("H1 {0} calls: no errors, handles flat +-{1} after idle".format(PL["calls"], PL["handle_tolerance"]),
           errs == 0 and h0 and h2 and abs(h2 - h0) <= PL["handle_tolerance"], "{0!r} -> {1!r} -> idle {2!r}".format(h0, h1, h2))
    s.gate("Z2 S1 md5 unchanged", K.md5(os.path.join(g.CLAUDEDEV, "D1_s1_copy.vi")) == "3e3d23cefd3a334001aa9d6156bf1aee")


rc = K.run(body, s)
if not DRY:
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4.0)   # noqa: E702
    print("LabVIEW gone at exit:", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower(), flush=True)
sys.exit(rc)
