r"""selftest_rebase_c133_3 - card 133-3 pass 2 (OFFLINE, temp dir only; tools/bench files are READ, never written): stage_prerun.rebase
records the ORIGINAL plan_in (the stage input `*_in.json`), not its temp copy (133-1 first_fail, plan_ring_p3b2.json:637-640).
WHAT EXISTED: selftest_rebase_c132_6.py (rebase on temp copies), stagesim.simulate (provisional finalize as plan_ring_p3b_split.py:173-174).
CASE: re-finalize plan_ring_p3b2_in.json (4df60e63) on its provisional base into a temp dir (route_check off, as the split did), then
--rebase that temp plan onto the real P3b-1 graph (6cfa6ecb) with out_root = temp.
PREDICTION: T1 provisional finalize FINAL, plan_in = tools/bench/plan_ring_p3b2_in.json; T2 rebase ok, finalized.plan_in.path ==
tools/bench/plan_ring_p3b2_in.json with its file md5, `rebase.sim_input` md5 recorded; T3 the recipe's L0 plan_in clause
(stage_d1_ring_p3b2.py:33: splitext(path)[0].endswith('plan_ring_p3b2_in')) and final / open_rows_match hold; T4 the rebased actions ==
04204133's actions (same 39 rows); T5 tools/bench/plan_ring_p3b2.json is untouched (md5 04204133).
    py tools/bgrun.py --material --max-min 6 --log tools/bench/selftest_rebase_c133_3.log -- py -u tools/bench/selftest_rebase_c133_3.py"""
import hashlib, json, os, shutil, sys, tempfile                                     # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P, stagesim as SS, stage_prerun as SPR                           # noqa: E402,E401
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                    # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
ok = []


def gate(name, c, det=""):
    ok.append((name, bool(c)))
    print("{0}  {1}  {2}".format("PASS" if c else "FAIL", name, str(det)[:900]), flush=True)


REF, PIN_ = os.path.join(B, "plan_ring_p3b2.json"), os.path.join(B, "plan_ring_p3b2_in.json")
GR = os.path.join(B, "graph_ring_p3b1_20261002_073225.json")
ref0 = md5(REF)
tmp = tempfile.mkdtemp(prefix="st_rebase_c133_3_")
try:
    pin = J(PIN_)
    S = SS.simulate(PIN_, os.path.join(ROOT, pin["base"]["path"]), out_root=os.path.join(tmp, "sim"), plan_out_dir=tmp,
                    log=lambda *x: None, route_check=False)
    tp = os.path.join(tmp, "plan_ring_p3b2.json")
    fz = J(tp).get("finalized") or {}
    gate("T1 provisional finalize FINAL, plan_in = plan_ring_p3b2_in.json", S["final"] and fz.get("plan_in", {}).get("path") ==
         "tools/bench/plan_ring_p3b2_in.json", (S["final"], S["failed"], fz.get("plan_in")))
    okr, det = SPR.rebase(tp, GR, log=lambda *x: None, out_root=os.path.join(tmp, "sim"))
    rp = J(tp)
    rz = rp.get("finalized") or {}
    gate("T2 rebase ok; finalized.plan_in = the ORIGINAL stage input with its md5; rebase.sim_input md5 recorded",
         okr and rz.get("plan_in") == {"path": "tools/bench/plan_ring_p3b2_in.json", "md5": md5(PIN_)}
         and len((rz.get("rebase") or {}).get("sim_input", {}).get("md5") or "") == 32, (okr, det[-300:], rz.get("plan_in"), rz.get("rebase")))
    gate("T3 recipe L0 clauses hold on the rebased plan (final, open_rows_match, plan_in suffix *_in)",
         rp.get("final") is True and rz.get("open_rows_match") is True
         and os.path.splitext(rz["plan_in"]["path"])[0].endswith("plan_ring_p3b2_in"), (rp.get("final"), rz.get("open_rows_match")))
    gate("T4 rebased actions == 04204133's 39 actions", rp["actions"] == J(REF)["actions"], len(rp["actions"]))
finally:
    shutil.rmtree(tmp, ignore_errors=True)
gate("T5 tools/bench/plan_ring_p3b2.json untouched (04204133)", md5(REF) == ref0 == "04204133d6c55929f368ec3761f70445", md5(REF))
np_, nf = sum(1 for _n, c in ok if c), sum(1 for _n, c in ok if not c)
print(P.result_line(P.make_result(np_, nf, next((n for n, c in ok if not c), None), [])), flush=True)
sys.exit(1 if nf else 0)
