r"""prep_c143_p1_pred - card 143-P1 step 3 (OFFLINE, no LabVIEW). The md5-pinned pred file plan_ring_p4_s03v18_pred.json for the recipe pair
stage_d1_ring_p4_s03v18.py / _scratch.py, on the PROVISIONAL base (s02v18's simulated END; never launched, regenerated after --rebase).
COPIED from prep_c142_5_pred.py with: the RB gate inverted (base IS provisional, sim_of = s02v18 e941ebbf), the action count 20, the start
596.5 marked PROVISIONAL, and the Error List base = s02v18's PREDICTED total (plan_ring_p4_s02v18_pred.json, not yet measured) as in
prep_c141_p1_mk.py:391-403 (provisional session 2).
PREDICTION CONTRACT: RB plan FINAL on a provisional base (sim_of s02v18 e941ebbf), open_rows_match, 20 actions; EL0 s02 pred keyed to
  e941ebbf; C compile each action once; X10 peak at 596.5 (676.9) <= 680; X17 PASS; EL counted (created nodes with an unwired input
  reported, not required 0); SP pred written keyed to the plan md5.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c143_p1_pred.log -- py -u tools/bench/prep_c143_p1_pred.py"""
import collections, hashlib, json, os, sys                                                # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagexec as SX, stage_prerun as SPR, census_predict as CPR                        # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
RRP, PP = os.path.join(B, "plan_ring_p4_s03v18.json"), os.path.join(B, "plan_ring_p4_s03v18_pred.json")
S02, S02P = os.path.join(B, "plan_ring_p4_s02v18.json"), os.path.join(B, "plan_ring_p4_s02v18_pred.json")
START, START_CITE = 596.5, "PROVISIONAL 596.5 = session 1 file's measured load (brief 143-P1 step 1); REPLACE by session 2 file's measured load at rebase (PD320(d))"
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                 # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
G, ARTS = {"pass": 0, "fail": 0, "first": None}, []


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:800]), flush=True)
    if not ok:
        print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
        sys.exit(1)


p = J(RRP)
fz = p.get("finalized") or {}
bp = (fz.get("base") or p.get("base") or {})
so = (p.get("base") or {}).get("sim_of") or {}
gate("RB plan FINAL on a provisional base {0} (sim_of {1}), open_rows_match, {2} actions".format(bp.get("path"), so, len(p["actions"])),
     (p.get("base") or {}).get("provisional") is True and so.get("md5") == md5(S02) == "e941ebbfaa3d98099bcd10d8c6237ef4" and p.get("final") is True
     and fz.get("open_rows_match") is True and len(p["actions"]) == 20, {"base": p.get("base")})
s2p = J(S02P)
gate("EL0 s02v18 pred keyed to e941ebbf", (s2p.get("plan") or {}).get("md5") == md5(S02), s2p.get("plan"))
EL_S2 = s2p["errorlist"]["predicted_total"]
EL_CITE = "session 2 (s02v18) PREDICTED total {0} (plan_ring_p4_s02v18_pred.json, alternative {1}); re-derive from session 2's measured Error List at rebase".format(
    EL_S2, s2p["errorlist"]["alternative_total"])
base = J(bp["path"])
ops = SX.compile_plan(p)
gate("C compile: {0} actions -> {1} ops, each action once".format(len(p["actions"]), len(ops)),
     sorted(n for o in ops for n in o["acts"]) == list(range(1, len(p["actions"]) + 1)))
bind = sorted(k for k, o in enumerate(ops, 1) if o["kind"] in SX.BIND_KINDS)
cps = sorted(set([0, len(ops)]) | set(bind))
MODEL = SPR.load_memory_model()
mp = SPR.x10_model_peak([o["kind"] for o in ops], cps, model=MODEL, start_mb=START)
xs = SPR.x10_plan_start(RRP, MODEL)
mp2 = SPR.x10_model_peak([o["kind"] for o in ops], cps, model=MODEL, start_mb=xs[0]) if xs else None
print("FACT X10 at start {0}: N {1} R {2} peak {3} fail_above {4} ok {5} | prerun's own start {6} -> peak {7}".format(
      START, mp["N"], mp["R"], mp["peak_mb"], mp["fail_above_mb"], mp["ok"], xs, mp2 and mp2["peak_mb"]), flush=True)
gate("X10 peak {0} at start {1} <= fail threshold {2} (memory_model.json)".format(mp["peak_mb"], START, mp["fail_above_mb"]), mp["ok"], mp)
ok17, det17 = SPR.x17_gate([p])
gate("X17 over s03v18", ok17, det17)
rep = CPR.predict(p, {}, J(os.path.join(B, "census_samples.json")))
sf = fz.get("step_files") or []
st0, last = J(sf[0]["path"])["state"], J(sf[-1]["path"])["state"]
madeu = set(int(u) for u in (last.get("sym") or {}).values() if isinstance(u, int)) - set(int(u) for u in (st0.get("sym") or {}).values() if isinstance(u, int))


def unwired_in(state):
    out = collections.defaultdict(list)
    for r in state["terminals"]:
        if not r.get("is_source") and not r.get("wire_uid") and r.get("term_class") != "ControlTerminal":
            out[int(r["owner_uid"])].append(r.get("term_name"))
    return out


u0, u2 = unwired_in(st0), unwired_in(last)
created_unw = sorted((u, u2[u]) for u in u2 if u in madeu)
base_new = sorted((u, u2[u]) for u in u2 if u not in madeu and u not in u0)
gone_unw = sorted(u for u in u0 if u not in u2)
print("EL created nodes with an unwired input", created_unw, "| base nodes newly unwired", base_new, "| nodes unwired at step 0 and gone/wired at end", gone_unw,
      "| sym", json.dumps(last.get("sym")), flush=True)
# card 143-3 (PD333(b)): the counted total comes from the FIXED predictor (unwired Local + While cond + created input; items open at
# step 0 and closed at the end DEBITED - `gone_unw` was never subtracted here). Superseded for s03 by prep_c143_3_pred.py (rebased base).
sys.path.insert(0, B)
import prep_c143_3_elrule as ELR                                                            # noqa: E402
ELP = ELR.predict(st0, last, EL_S2, madeu)
print("EL FIXED", ELP["predicted_total"], "new", ELP["new_items"], "closed", ELP["closed_items"], flush=True)
pred = {"schema": "ring-p3b-pred/1", "card": "143-P1", "note": "P4 v18 session 3 (v18 ops 59..78) as one bed session on session 2's saved file; PROVISIONAL base = "
        "session 2's simulated end - regenerate after stage_prerun --rebase onto session 2's saved file (start = its MEASURED load, PD320(d))",
        "plan": {"path": rel(RRP), "md5": md5(RRP)}, "graph": {"path": bp["path"], "md5": md5(os.path.join(ROOT, bp["path"]))}, "bed": base.get("vi"), "bed_md5": base.get("md5"),
        "census": dict(rep["derived"]), "census_overall": rep["overall"], "census_unpredicted": [p["actions"][k - 1]["id"] for k in rep["unpredicted"]],
        "ops": [o["kind"] for o in ops], "cdiff_rows": sorted(fz.get("end_cdiff_rows") or []), "cross_session_refs": "new:LRS2 -> -20 (prep_c143_p1_mk.log C2)",
        "errorlist": {"bed_total": EL_S2, "new_items_predicted": len(ELP["new_items"]) - len(ELP["closed_items"]), "predicted_total": ELP["predicted_total"],
                      "alternative_total": None, "fixed": ELP, "created_nodes_unwired_input": [[u, n] for u, n in created_unw],
                      "base_nodes_newly_unwired": [[u, n] for u, n in base_new], "nodes_unwired_at_step0_gone_at_end": gone_unw,
                      "rule": ELP["rule"] + "; base = " + EL_CITE, "base_file": rel(S02P), "checked": False},
        "memory_pred": {"card": "143-P1", "checkpoints": cps, "R": mp["R"], "N": mp["N"], "bind_ops": bind, "op_kinds": [o["kind"] for o in ops],
                        "start_mb": START, "start_cite": START_CITE, "peak_mb": mp["peak_mb"], "fail_above_mb": mp["fail_above_mb"], "below_fail": mp["ok"],
                        "prerun_start": xs, "prerun_peak_mb": mp2 and mp2["peak_mb"], "model": {"path": rel(SPR.MEMORY_MODEL), "md5": md5(SPR.MEMORY_MODEL)}},
        "summary": fz.get("summary")}
json.dump(pred, open(PP, "w", encoding="utf-8"), indent=1)
print("FACT ops", dict(collections.Counter(pred["ops"])), "census", pred["census"], "overall", pred["census_overall"], "unpredicted", pred["census_unpredicted"],
      "| EL", pred["errorlist"]["predicted_total"], "alt", pred["errorlist"]["alternative_total"], "| end rows", len(pred["cdiff_rows"]), "open pairs", len(p.get("open_rows") or []), flush=True)
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (RRP, PP))
gate("SP pred written, keyed to the plan md5", J(PP)["plan"]["md5"] == md5(RRP))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
