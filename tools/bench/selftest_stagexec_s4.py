"""Self-test, card chat-S4 (user 2026-10-03: "A, B는 도입 ... 한 싸이클 내에서는 계속 이어서"). OFFLINE: no LabVIEW, no VI opened.
Existing pieces used: stagexec.SimBackend / Executor / part_a_record + load_binding (the Part-B entry of card 103-4), the display
plan tools/bench/sim/disp/plan_disp.json and the real P4 session-1 plan tools/bench/plan_ring_p4_s01.json (base = the recorded
graph of the P3b-2b bed), stage_prerun.check_launch / x10_model_peak.
PREDICTION CONTRACT (all must hold):
  A1 adopt_verdict PASS log + required present -> ok ; A2 a STOP-class FAIL -> not ok ; A3 required label missing -> not ok
  A4 a hard marker (Traceback) -> not ok ; A5 adopt_scratch writes adopt/1; adopted_launch finds it for the stage recipe AND its
     _scratch wrapper, not for other plan md5s, not when revoked ; A6 adopt_scratch refuses the input VI / a file outside claudeDev
  A7 stage_prerun.check_launch REFUSES the stage recipe after an adoption (no second run on the bed), allows nothing to slip
  R1 stop BEFORE mutation in op k -> resume_record(from_step k-1) -> write/load_resume -> Executor(from_step=k-1) on the stopped
     state reaches the last op with entry diff 0 and dispatches ops k.. only
  R2 stop AFTER op k mutated (drop_edge) -> the same resume is REFUSED at entry (FROM-STEP BASE)
  R3 another cycle refused ; R4 file md5 changed refused ; R5 actions 1..s_act changed refused, an action after s_act changed
     (a FIXED plan) accepted ; R6 the bed as the resume file refused
  B1/B2 partial_reads=True == whole reads: same binding, every step diff 0, reads_partial > 0, whole + partial == whole run's
     reads, on plan_disp (every op a checkpoint) and plan_ring_p4_s01 (its BIND + last checkpoints)
  B3 x10_model_peak(partial=) removes exactly the partial k from R (never k 0 / the last op)
  B4 a real change outside the simulated diff (extra_obj) is missed by the partial read and CAUGHT by the last whole read
Usage: py tools/bgrun.py --material --max-min 8 --log tools/bench/selftest_stagexec_s4.log -- py -u tools/bench/selftest_stagexec_s4.py
"""
import copy, json, os, shutil, sys, tempfile                                       # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagexec as SX, stagesim as SS, stage_prerun as SPR, protocol                # noqa: E401,E402
P, F = [0], []


def gate(label, ok, detail=""):
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:300]), flush=True)
    P[0] += bool(ok)
    ok or F.append(label)


q = lambda m: None                                                                  # noqa: E731
tmp = tempfile.mkdtemp(prefix="s4_")
PASSLOG = "BGRUN START x\n  PASS  E1 every checkpoint == sim\n  PASS  PB cdiff ok\n  PASS  PS saved\nRESULT {\"status\":\"PASS\"}\nBGRUN END rc=0\n"
v = SX.adopt_verdict(PASSLOG, ("E1", "PB", "PS"))
gate("A1 PASS log with E1/PB/PS -> ok", v["ok"], v)
v = SX.adopt_verdict(PASSLOG.replace("  PASS  PB cdiff ok", "  FAIL  PB frame-keyed cdiff == pred"), ("E1", "PS"))
gate("A2 a STOP-class FAIL -> not ok", not v["ok"] and v["stop_fails"], v)
v = SX.adopt_verdict(PASSLOG, ("E1", "EL"))
gate("A3 required EL without PASS -> not ok (E1 does not match E10)", not v["ok"] and v["missing"] == ["EL"]
     and not SX.adopt_verdict("  PASS  E10 x\nRESULT {}\n", ("E1",))["ok"], v)
gate("A4 a Traceback in the segment -> not ok", not SX.adopt_verdict(PASSLOG + "Traceback (most recent call last)\n", ("E1",))["ok"])
cd = os.path.join(tmp, "claudeDev"); os.makedirs(cd)                               # noqa: E702
art, inp, lg, alog = os.path.join(cd, "D1_x_s01_1.vi"), os.path.join(cd, "bed.vi"), os.path.join(tmp, "scr.log"), os.path.join(tmp, "adopt.jsonl")
open(art, "wb").write(b"artefact"); open(inp, "wb").write(b"bed"); open(lg, "w").write(PASSLOG)   # noqa: E702
REC = os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p4_s01.py")
pm = SPR.plan_md5s(REC)
ok, rec = SX.adopt_scratch(REC.replace(".py", "_scratch.py"), lg, art, inp, SX.md5(inp), pm, ("E1", "PB"), path=alog, claudedev=cd)
gate("A5 adopt_scratch writes adopt/1 under the stage key", ok and rec["stage"] == "stage_d1_ring_p4_s01.py", rec)
gate("A5b adopted_launch: stage recipe + scratch wrapper found; other md5s / revoked not",
     SX.adopted_launch(REC, pm, alog) and SX.adopted_launch(REC.replace(".py", "_scratch2.py"), pm, alog)
     and SX.adopted_launch(REC, {"x": "0" * 32}, alog) is None, pm)
ok2, why2 = SX.adopt_scratch(REC, lg, inp, inp, SX.md5(inp), pm, ("E1",), path=alog, claudedev=cd)
ok3, why3 = SX.adopt_scratch(REC, lg, lg, inp, SX.md5(inp), pm, ("E1",), path=alog, claudedev=cd)
gate("A6 refused: the input VI as artefact; a file outside claudeDev", not ok2 and not ok3, (why2, why3))
SPR.ADOPT_LOG = alog
okL, whyL = SPR.check_launch("py tools/bgrun.py --material --max-min 50 --log x.log -- py -u tools/recipes/stage_d1_ring_p4_s01.py")
gate("A7 check_launch refuses the stage recipe after the adoption (no second run on the bed)", not okL and "ADOPTED" in whyL, whyL[:200])
lines = open(alog).read().splitlines()
open(alog, "w").write("\n".join(json.dumps(dict(json.loads(x), revoked="selftest")) for x in lines) + "\n")
gate("A5c a revoked record is not an adoption", SX.adopted_launch(REC, pm, alog) is None)
# ------------------------------------------------------------------------------------------------ R: resume within a cycle
DISP = os.path.join(ROOT, "tools", "bench", "sim", "disp", "plan_disp.json")
pl = SX._j(DISP); ops = SX.compile_plan(pl); models = SS.load_models()             # noqa: E702
mk = lambda st=None, fault=None: SX.SimBackend(pl, st if st is not None else SS.base_state(SX._j(SX._abs(pl["finalized"]["base"]["path"])), pl.get("context")), models, fault)   # noqa: E731
k = 25
act = ops[k - 1]["acts"][-1]


def stopped(fault):
    be = mk(fault=fault)
    ex = SX.Executor(DISP, be, log=q)
    try:
        ex.run()
        return ex, be, None
    except SX.ExecStop as e:
        return ex, be, e


ex, be, e = stopped({"at": act, "kind": "stop_pre"})
r = ex.resume_record(str(e))
gate("R1a op error before mutation in op {0} -> resume_record from_step {1}".format(k, k - 1), e is not None and r and r["stop_after"] == k - 1, str(e)[:120])
scr = os.path.join(tmp, "scratch_saved.vi"); open(scr, "wb").write(b"saved as-is")   # noqa: E702
rp = SX.write_resume(r, scr, "cycle T", out_path=os.path.join(tmp, "resume.json"))
try:
    bd = SX.load_resume(rp, DISP, "cycle T")
    beB = mk(copy.deepcopy(be.st)); beB.next = be.next                             # noqa: E702
    exB = SX.Executor(DISP, beB, log=q, from_step=k - 1, binding=bd)
    exB.run()
    gate("R1 resume from_step {0}: entry diff 0, ops {1}..{2} only, last op reached".format(k - 1, k, len(ops)),
         exB.report[0]["diff"]["n"] == 0 and [x["k"] for x in exB.report[1:]] == list(range(k, len(ops) + 1)), exB.report[0]["diff"]["n"])
except SX.ExecStop as e1:
    gate("R1 resume from_step {0}".format(k - 1), False, str(e1)[:300])
ex2, be2, e2 = stopped({"at": act, "kind": "drop_edge"})
r2 = ex2.resume_record(str(e2))
rp2 = SX.write_resume(r2, scr, "cycle T", out_path=os.path.join(tmp, "resume2.json"))
try:
    beC = mk(copy.deepcopy(be2.st)); beC.next = be2.next                           # noqa: E702
    SX.Executor(DISP, beC, log=q, from_step=k - 1, binding=SX.load_resume(rp2, DISP, "cycle T")).run()
    gate("R2 op {0} already mutated -> resume refused at entry".format(k), False, "ran")
except SX.ExecStop as e3:
    gate("R2 op {0} already mutated -> resume refused at entry (FROM-STEP BASE)".format(k), "FROM-STEP BASE" in str(e3), str(e3)[:160])


def refused(label, fn, want):
    try:
        fn()
        gate(label, False, "accepted")
    except SX.ExecStop as x:
        gate(label, want in str(x), str(x)[:160])


refused("R3 another cycle refused", lambda: SX.load_resume(rp, DISP, "cycle U"), "new cycle")
shutil.copyfile(scr, scr + ".bak"); open(scr, "ab").write(b"x")                    # noqa: E702
refused("R4 the saved file changed refused", lambda: SX.load_resume(rp, DISP, "cycle T"), "missing or changed")
shutil.copyfile(scr + ".bak", scr)
bad = copy.deepcopy(pl); bad["actions"][0]["note_s4"] = "changed"                  # noqa: E702
fixed = copy.deepcopy(pl); fixed["actions"][k + 2]["note_s4"] = "fixed after the stop"   # noqa: E702
pb_, pf_ = os.path.join(tmp, "plan_bad.json"), os.path.join(tmp, "plan_fixed.json")
json.dump(bad, open(pb_, "w")); json.dump(fixed, open(pf_, "w"))                  # noqa: E702
refused("R5 actions 1..s_act changed refused", lambda: SX.load_resume(rp, pb_, "cycle T"), "changed actions")
try:
    bf = SX.load_resume(rp, pf_, "cycle T")
    gate("R5b a FIXED plan (change after s_act) accepted, md5 pin follows the plan", bf["plan_md5"] == SS.md5_file(pf_) != r["plan_md5"])
except SX.ExecStop as e4:
    gate("R5b a FIXED plan accepted", False, str(e4)[:160])
orig = SX.plan_bed_vi
SX.plan_bed_vi = lambda plan: scr
refused("R6 the bed as the resume file refused (write)", lambda: SX.write_resume(r, scr, "cycle T", out_path=os.path.join(tmp, "r6.json")), "bed")
refused("R6b the bed as the resume file refused (load)", lambda: SX.load_resume(rp, DISP, "cycle T"), "bed")
SX.plan_bed_vi = orig
# ------------------------------------------------------------------------------------------------ B: partial reads


def pair(plan_path, checkpoints):
    p_ = SX._j(plan_path)
    mk2 = lambda: SX.SimBackend(p_, SS.base_state(SX._j(SX._abs(p_["finalized"]["base"]["path"])), p_.get("context")), models)   # noqa: E731
    bw, bp = mk2(), mk2()
    for b_ in (bw, bp):
        SS.seed_base_flips_modelled(b_.st, models)
    xw = SX.Executor(plan_path, bw, log=q, checkpoints=checkpoints)
    xp = SX.Executor(plan_path, bp, log=q, checkpoints=checkpoints, partial_reads=True)
    xw.run(); xp.run()                                                             # noqa: E702
    return xw, xp


for lab, pp, cps in (("B1 plan_disp, every op a checkpoint", DISP, None),
                     ("B2 plan_ring_p4_s01, BIND + last checkpoints", os.path.join(ROOT, "tools", "bench", "plan_ring_p4_s01.json"), "bind")):
    try:
        if cps == "bind":
            o_ = SX.compile_plan(SX._j(pp))
            cps = sorted({0, len(o_)} | set(i for i, o in enumerate(o_, 1) if o["kind"] in SX.BIND_KINDS))
        xw, xp = pair(pp, cps)
        same = xw.bind == xp.bind and all(x["diff"]["n"] == 0 for x in xp.report) and all(x["diff"]["n"] == 0 for x in xw.report)
        gate(lab + ": partial == whole (binding, every diff 0), partial reads {0}, whole {1} -> {2}, fallbacks {3}".format(
            len(xp.reads_partial), len(xw.reads_real), len(xp.reads_real), len(xp.partial_fallbacks)),
             same and xp.reads_partial and sorted(xp.reads_real + xp.reads_partial) == sorted(xw.reads_real) and xp.reads_real[-1] == len(xp.ops),
             {"fallbacks": xp.partial_fallbacks[:4]})
    except SX.ExecStop as e5:
        gate(lab, False, str(e5)[:300])
kinds = [o["kind"] for o in ops]
m0 = SPR.x10_model_peak(kinds, None, model=SPR.load_memory_model())
m1 = SPR.x10_model_peak(kinds, None, model=SPR.load_memory_model(), partial=[0, 3, 4, len(kinds)])
gate("B3 X10: partial {3,4} leave R (k 0 and the last op stay whole)", m1["R"] == m0["R"] - 2 and m1["P"] == 2, (m0["R"], m1["R"], m1["P"]))
def b4(fault):
    bx = mk(fault=fault)
    SS.seed_base_flips_modelled(bx.st, models)                                     # as B1 (review s4-selftest-a7-b4 s2)
    xx = SX.Executor(DISP, bx, log=q, partial_reads=True)
    try:
        xx.run()
        return xx, None
    except SX.ExecStop as e_:
        return xx, e_


xc, ec = b4(None)
gate("B4a control: the same construction without a fault reaches op {0} with no stop".format(len(ops)), ec is None, str(ec)[:200])
xx, e6 = b4({"at": act, "kind": "extra_obj"})
ks = (xx.cur or {}).get("k")
first_whole = min([w for w in xx.reads_real if w > k] or [None])
print("  FACT  B4 stop message: {0}".format(str(e6)[:600]), flush=True)
gate("B4 extra_obj at op {0} (a partial read) is missed there and CAUGHT at the first whole read after it (op {1})".format(k, first_whole),
     e6 is not None and k in xx.reads_partial and ks == first_whole and ("99999999" in str(e6) or "99999998" in str(e6)),
     "stopped at op {0}; partial reads {1}".format(ks, xx.reads_partial[-4:]))
gate("A7a the absolute (space-containing) path is not a launch unit; the relative one is",
     SPR.launched_stage_scripts("py tools/bgrun.py --max-min 5 --log x.log -- py -u " + REC) == []
     and len(SPR.launched_stage_scripts("py tools/bgrun.py --max-min 5 --log x.log -- py -u tools/recipes/stage_d1_ring_p4_s01.py")) == 1)
shutil.rmtree(tmp, ignore_errors=True)
print(protocol.result_line(protocol.make_result(P[0], len(F), F[0] if F else None)))
sys.exit(1 if F else 0)
