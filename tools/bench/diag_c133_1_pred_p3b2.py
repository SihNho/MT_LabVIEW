r"""diag_c133_1_pred_p3b2 - card 133-1 step 3: REGENERATE plan_ring_p3b2_pred.json for the REBASED, FINAL plan_ring_p3b2.json
(base = sim/ring_p3b2_base_real_fsmap.json = P3b-1's real graph + carried FS map). Offline, no LabVIEW.
WHAT EXISTED: plan_ring_p3b_split.py pred() (:259-287) wrote the old pred on the PROVISIONAL base; this file applies the same
fields to the rebased plan (census_predict.predict over census_samples.json, ops = compile_plan, memory_pred =
stage_prerun.x10_model_peak with checkpoints {0,len}|BIND - the recipe's set, stage_d1_ring_p3b2.py:24-25). Values are read,
never typed: bed / bed_md5 from the base graph's own vi/md5 (the recipe's L0 compares BASE["md5"] == PRED["bed_md5"]);
Error List base = P3b-1's measured expected file (errorlist_expected_D1_ring_p3b1_20261002_060910.json, PD274(b)).
PREDICTION: Q1 plan final, base == the fsmap file, md5s match; Q2 ops == compile (39 actions -> 39 ops), BIND = 14 creates + the
8 crossings now compiled connect_term_uid (card 133-1 fix) = 22; Q3 pred written, plan md5 == file. memory_pred is REPORTED
(X10 is card 133-3's), the peak is expected ABOVE the old 664.3 (8 more checkpoint reads).
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c133_1_pred_p3b2.log -- py -u tools/bench/diag_c133_1_pred_p3b2.py"""
import collections, hashlib, json, os, sys                                          # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P, stagexec as SX, census_predict as CPR, stage_prerun as SPR   # noqa: E402,E401
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                    # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                       # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
ok = []


def gate(name, c, det=""):
    ok.append((name, bool(c)))
    print("{0}  {1}  {2}".format("PASS" if c else "FAIL", name, str(det)[:1200]), flush=True)


PLAN = os.path.join(B, "plan_ring_p3b2.json")
OLD = os.path.join(B, "plan_ring_p3b2_pred.json")
EXP1 = os.path.join(B, "errorlist_expected_D1_ring_p3b1_20261002_060910.json")
pl, old = J(PLAN), J(OLD)
fz = pl.get("finalized") or {}
bp = os.path.join(ROOT, fz["base"]["path"])
base = J(bp)
gate("Q1 plan final, open_rows_match, route check PASS; base == fsmap file (md5 == finalized)", pl.get("final") is True
     and fz.get("open_rows_match") is True and (fz.get("route_check") or {}).get("status") == "PASS"
     and fz["base"]["path"].endswith("ring_p3b2_base_real_fsmap.json") and md5(bp) == fz["base"]["md5"],
     (md5(PLAN), fz.get("base"), (fz.get("route_check") or {}).get("status")))
end = J(fz["step_files"][-1]["path"])["state"]
summ = J(fz["summary"]["path"])
DEF = dict(("new:" + a["as"], a["id"]) for a in pl["actions"] if a["op"] == "create" and a.get("as"))
born = dict((int(u), DEF.get(s)) for s, u in end["sym"].items())
base_owners = set(int(r["owner_uid"]) for r in base["terminals"])
unw = sorted("{0} '{1}' ({2} #{3})".format(born.get(int(r["owner_uid"]), "?"), r["term_name"], r["owner_class"], r["owner_uid"])
             for r in end["terminals"] if int(r["owner_uid"]) not in base_owners and not r["is_source"] and not r["wire_uid"])
rep = CPR.predict(pl, {}, J(os.path.join(B, "census_samples.json")))
ops = SX.compile_plan(pl)
bind = sorted(k for k, o in enumerate(ops, 1) if o["kind"] in SX.BIND_KINDS)
cps = sorted(set([0, len(ops)]) | set(bind))
mp = SPR.x10_model_peak([o["kind"] for o in ops], cps, model=SPR.load_memory_model())
e1 = J(EXP1)
el = {"bed_total": e1["total"], "removed": {}, "new_items_predicted": 0, "predicted_total": e1["total"],
      "base_file": rel(EXP1), "unwired_created_sinks": unw,
      "alternative": "+{0} if LabVIEW flags an unwired created sink above as an item".format(len(unw)),
      "class_range": "tools/bench/errorlist_expect_p3b2.json (errorlist_expect_p3b2.py, computed after this pred)",
      "row_sources": old["errorlist"].get("row_sources")}
d = {"schema": "ring-p3b-pred/1", "card": "133-1", "note": "P3b-2 REBASED onto P3b-1's saved artefact (stage_prerun --rebase, "
     "card 133-1); FS crossings compile to connect_term_uid from finalized.fs_routes", "plan": {"path": rel(PLAN), "md5": md5(PLAN)},
     "graph": {"path": rel(bp), "md5": md5(bp)}, "bed": base.get("vi"), "bed_md5": base.get("md5"),
     "census": dict(rep["derived"]), "census_overall": rep["overall"],
     "census_unpredicted": [pl["actions"][k - 1]["id"] for k in rep["unpredicted"]],
     "census_rows": [dict((k, r[k]) for k in ("k", "id", "op", "variant", "delta", "verdict")) for r in rep["rows"]],
     "ops": [o["kind"] for o in ops], "cdiff_rows": sorted(fz["end_cdiff_rows"]), "errorlist": el, "readback": old.get("readback"),
     "memory_pred": {"card": "133-1", "checkpoints": cps, "R": mp["R"], "N": mp["N"], "bind_ops": bind,
                     "op_kinds": [o["kind"] for o in ops], "peak_mb": mp["peak_mb"], "fail_above_mb": mp["fail_above_mb"],
                     "below_fail": mp["ok"], "model": {"path": rel(SPR.MEMORY_MODEL), "md5": md5(SPR.MEMORY_MODEL)},
                     "how": "stage_prerun.x10_model_peak on the compiled plan, checkpoints {0, len} | BIND (the recipe's set)",
                     "note": "report only; start term / launch form = card 133-3 (PD282(c))"},
     "summary": {"path": fz["summary"]["path"], "md5": fz["summary"]["md5"]}}
print("  FACT  ops {0}; BIND {1} ({2}); R {3} N {4}; X10 peak {5} MB (fail above {6}) below_fail {7}".format(
    dict(collections.Counter(d["ops"])), len(bind), bind, mp["R"], mp["N"], mp["peak_mb"], mp["fail_above_mb"], mp["ok"]), flush=True)
print("  FACT  census {0} overall {1} unpredicted {2}; unwired created sinks {3}; bed {4} {5}; EL base {6}".format(
    d["census"], d["census_overall"], d["census_unpredicted"], unw, d["bed"], d["bed_md5"], e1["total"]), flush=True)
gate("Q2 ops == compile, each action once; BIND == 14 creates + 8 connect_term_uid crossings",
     sorted(n for o in ops for n in o["acts"]) == list(range(1, len(pl["actions"]) + 1)) and len(bind) == 22
     and sum(1 for k in bind if ops[k - 1]["kind"] == "connect_term_uid") == 8, (len(ops), len(bind)))
json.dump(d, open(OLD, "w", encoding="utf-8"), indent=1)
gate("Q3 pred written, plan md5 == file, graph md5 == finalized base", J(OLD)["plan"]["md5"] == md5(PLAN)
     and J(OLD)["graph"]["md5"] == fz["base"]["md5"], md5(OLD))
np_, nf = sum(1 for _n, c in ok if c), sum(1 for _n, c in ok if not c)
print(P.result_line(P.make_result(np_, nf, next((n for n, c in ok if not c), None),
                                  [{"path": rel(OLD), "md5": md5(OLD)}, {"path": rel(PLAN), "md5": md5(PLAN)}])), flush=True)
sys.exit(1 if nf else 0)
