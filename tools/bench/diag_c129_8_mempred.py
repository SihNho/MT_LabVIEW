r"""diag_c129_8_mempred - card 129-8 (brief_129-8.md s2, PD265(c)): OFFLINE, no LabVIEW. For RING P3b-1 and P3b-2 compute the
checkpoint set the recipes now pass (tools/recipes/stage_d1_ring_p3b1.py / _p3b2.py, the stage_d1_l2b3.py:16-18 form:
{0, len(ops)} | BIND, BIND = ops whose kind is in stagexec.BIND_KINDS), R = whole-VI reads (= the set's size, 0 and the end
included), N = op count, and the predicted peak private MB = 570 + R*2.53 + N*1.4, and WRITE it into plan_ring_p3b{1,2}_pred.json
under "memory_pred" with citations. Report only - the set is never tuned to reach a number (card rule 2).
PRIOR ART: none for a memory pred field in the preds (grep "memory_pred" tools: none before this card); X10 in stage_prerun.py:57-60
reads recorded stamps, not this field. PREDICTION: both preds written, plan md5 unchanged in each pred (recipe L0 keeps passing).
    py -u tools/bench/diag_c129_8_mempred.py"""
import json, os, sys                                                                # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagexec as SX, protocol as PR                                              # noqa: E401,E402
import stage_prerun as SP                                                           # noqa: E402  (X10_FAIL_MB only)
BENCH = os.path.join(ROOT, "tools", "bench")
K0, SLOPE_R, EDIT, UNATTR = 570.0, 2.53, 0.58, 0.8
CITE = {"k0": "tools/bench/stage_d1_ring_p3b1_scratch_pin2.log:55 (METER read k 0 private 570.0 MB)",
        "read_slope": "tools/bench/diag_c129_6_mem.log:55 (W1 slope 2.529 MB/rep)",
        "edit_slope": "tools/bench/diag_c129_6_mem.log:87 (W2 slope 0.576 MB/rep)",
        "unattributed": "pin2 3.9 MB/op - 2.53 - 0.58 (brief_129-8.md s2)",
        "formula": "peak = 570 + R*2.53 + N*1.4 MB (brief_129-8.md s2)",
        "set_form": "tools/recipes/stage_d1_l2b3.py:16-18; stagexec.py:1721 BIND_KINDS"}
out, npass, nfail, ff, arts = {}, 0, 0, None, []
for half in ("p3b1", "p3b2"):
    plan = os.path.join(BENCH, "plan_ring_{0}.json".format(half))
    predp = os.path.join(BENCH, "plan_ring_{0}_pred.json".format(half))
    P = json.load(open(plan, encoding="utf-8"))
    ops = SX.compile_plan(P)
    bind = sorted(k for k, o in enumerate(ops, 1) if o["kind"] in SX.BIND_KINDS)
    cps = tuple(sorted({0, len(ops)} | set(bind)))
    R, N = len(cps), len(ops)
    peak = round(K0 + R * SLOPE_R + N * (EDIT + UNATTR), 1)
    pred = json.load(open(predp, encoding="utf-8"))
    md5_ok = pred.get("plan", {}).get("md5") == SX.md5(plan)
    pred["memory_pred"] = {"card": "129-8", "checkpoints": list(cps), "R": R, "N": N, "bind_ops": bind,
                           "op_kinds": [o["kind"] for o in ops], "peak_mb": peak, "x10_fail_mb": SP.X10_FAIL_MB,
                           "below_x10": peak < SP.X10_FAIL_MB, "constants": {"k0": K0, "read": SLOPE_R, "edit": EDIT, "unattributed": UNATTR},
                           "cite": CITE, "note": "report only; the set is not tuned to the number (card 129-8 rule)"}
    json.dump(pred, open(predp, "w", encoding="utf-8"), indent=1)
    print("FACT {0}: N {1} ops, BIND {2}, checkpoints {3}, R {4}, peak {5} MB vs X10 {6} MB ({7})".format(
        half, N, len(bind), cps, R, peak, SP.X10_FAIL_MB, "below" if peak < SP.X10_FAIL_MB else "AT/ABOVE"), flush=True)
    ok = json.load(open(predp, encoding="utf-8"))["memory_pred"]["peak_mb"] == peak
    print("GATE {0} W pred written and read back: {1}; plan md5 still keyed: {2}".format(half, "PASS" if ok else "FAIL", md5_ok), flush=True)
    npass, nfail = npass + bool(ok), nfail + (not ok)
    ff = ff or (None if ok else half + " W")
    arts.append({"path": os.path.relpath(predp, ROOT).replace("\\", "/"), "md5": SX.md5(predp)})
    out[half] = {"R": R, "N": N, "peak": peak}
print(PR.result_line(PR.make_result(npass, nfail, ff, [a for a in arts if a["md5"]])), flush=True)
sys.exit(1 if nfail else 0)
