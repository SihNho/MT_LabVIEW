# ---
# labview: none
# hardware: none
# ---
r"""prep_c144_p1_pred - card 144-P1 step 3 (OFFLINE, no LabVIEW). The md5-pinned pred file plan_ring_p4_s04v18_pred.json for the recipe
pair stage_d1_ring_p4_s04v18.py / _scratch.py, on the PROVISIONAL base (s03v18's simulated END; never launched, regenerated after --rebase).
COPIED from prep_c143_p1_pred.py (6d47056d; RB gate with sim_of, provisional start) with the Error List block of prep_c144_1_pred.py
(bbf12f62; PD349 rule via prep_c143_3_elrule.ELR.predict with extra_owner_states). Changes: s03 -> s04 names; RB sim_of = s03v18 da66a030;
action count from prep_c144_p1_session.json; START 596.0 PROVISIONAL; EL base = s03v18's PREDICTED total (plan_ring_p4_s03v18_pred.json,
keyed to da66a030, PD349 rule, card 144-1) - s03's Error List is measured later; owners also from s03's real base (fsmap c4a11939).
PREDICTION CONTRACT: RB plan FINAL on a provisional base (sim_of s03v18 da66a030), open_rows_match, N actions == session table; EL0 s03 pred
  keyed to da66a030; C compile each action once; X10 peak at 596.0 <= 680; X17 PASS; EL by the rule (number printed, not typed); SP pred
  keyed to the plan md5.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c144_p1_pred.log -- py -u tools/bench/prep_c144_p1_pred.py"""
import collections, hashlib, json, os, sys                                                # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
from tools import protocol  # noqa: E402
import stagexec as SX, stage_prerun as SPR, census_predict as CPR                        # noqa: E401,E402
import prep_c143_3_elrule as ELR                                                            # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
RRP, PP = os.path.join(B, "plan_ring_p4_s04v18.json"), os.path.join(B, "plan_ring_p4_s04v18_pred.json")
S03, S03P = os.path.join(B, "plan_ring_p4_s03v18.json"), os.path.join(B, "plan_ring_p4_s03v18_pred.json")
SESS = os.path.join(B, "prep_c144_p1_session.json")
START, START_CITE = 596.0, "PROVISIONAL 596.0 = session 2 file's measured load (brief 144-P1 step 1); REPLACE by session 3 file's measured load at rebase (PD320(d))"
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                 # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
G, ARTS = {"pass": 0, "fail": 0, "first": None}, []


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)
    if not ok:
        print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
        sys.exit(1)


p = J(RRP)
NA = J(SESS)["actions"]
fz = p.get("finalized") or {}
bp = (fz.get("base") or p.get("base") or {})
so = (p.get("base") or {}).get("sim_of") or {}
gate("RB plan FINAL on a provisional base {0} (sim_of {1}), open_rows_match, {2} actions == session table {3}".format(bp.get("path"), so, len(p["actions"]), NA),
     (p.get("base") or {}).get("provisional") is True and so.get("md5") == md5(S03) == "da66a0300851133d93881be3c28f2fdc" and p.get("final") is True
     and fz.get("open_rows_match") is True and len(p["actions"]) == NA, {"base": p.get("base")})
s3p = J(S03P)
gate("EL0 s03v18 pred keyed to da66a030", (s3p.get("plan") or {}).get("md5") == md5(S03), s3p.get("plan"))
EL_S3 = s3p["errorlist"]["predicted_total"]
EL_CITE = "session 3 (s03v18) PREDICTED total {0} by the PD349 rule (plan_ring_p4_s03v18_pred.json {1}, card 144-1); re-derive from session 3's measured Error List at rebase".format(
    EL_S3, md5(S03P))
base = J(bp["path"])
s03 = J(S03)
rbase = J(((s03.get("finalized") or {}).get("base") or s03.get("base"))["path"])                # s03's real base (owners of base nodes)
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
gate("X17 over s04v18", ok17, det17)
rep = CPR.predict(p, {}, J(os.path.join(B, "census_samples.json")))
sf = fz.get("step_files") or []
st0, last = J(sf[0]["path"])["state"], J(sf[-1]["path"])["state"]
madeu = set(int(u) for u in (last.get("sym") or {}).values() if isinstance(u, int)) - set(int(u) for u in (st0.get("sym") or {}).values() if isinstance(u, int))
ELP = ELR.predict(st0, last, EL_S3, madeu, extra_owner_states=(rbase,))
byc = collections.Counter(k[0] for k in ELP["new_items"]), collections.Counter(k[0] for k in ELP["closed_items"])
print("EL PD349 s04: base {0} new {1} closed {2} -> {3}; per class new {4} closed {5}; open at start {6}; uncertain {7}; detail_end {8}; created {9}; "
      "steps {10} -> {11}".format(EL_S3, ELP["new_items"], ELP["closed_items"], ELP["predicted_total"], dict(byc[0]), dict(byc[1]), ELP["open_at_start"],
                                  ELP["uncertain_base_newly_unwired_inputs"], ELP["detail_end"], sorted(madeu), sf[0]["path"], sf[-1]["path"]), flush=True)
print("FACT EL rule: {0}".format(ELP.get("rule")), flush=True)
pred = {"schema": "ring-p3b-pred/1", "card": "144-P1", "note": "P4 v18 session 4 (v18 ops {0}) as one bed session on session 3's saved file; PROVISIONAL base = "
        "session 3's simulated end - regenerate after stage_prerun --rebase onto session 3's saved file (start = its MEASURED load, PD320(d)); "
        "Error List by the PD349 rule".format(J(SESS)["ops"]),
        "plan": {"path": rel(RRP), "md5": md5(RRP)}, "graph": {"path": bp["path"], "md5": md5(os.path.join(ROOT, bp["path"]))}, "bed": base.get("vi"), "bed_md5": base.get("md5"),
        "census": dict(rep["derived"]), "census_overall": rep["overall"], "census_unpredicted": [p["actions"][k - 1]["id"] for k in rep["unpredicted"]],
        "ops": [o["kind"] for o in ops], "cdiff_rows": sorted(fz.get("end_cdiff_rows") or []),
        "cross_session_refs": "{0} refs to s03 symbols -> provisional uids (prep_c144_p1_mk.log C2)".format(len(J(SESS)["cross_refs"])),
        "errorlist": {"bed_total": EL_S3, "new_items_predicted": len(ELP["new_items"]) - len(ELP["closed_items"]), "predicted_total": ELP["predicted_total"],
                      "alternative_total": None, "fixed": ELP, "rule": ELP["rule"] + "; base = " + EL_CITE,
                      "rule_source": {"path": "tools/bench/prep_c143_3_elrule.py", "md5": md5(os.path.join(B, "prep_c143_3_elrule.py")),
                                      "module": "tools/elrule.py", "module_md5": md5(os.path.join(ROOT, "tools", "elrule.py")), "pd": "PD349"},
                      "base_file": rel(S03P), "checked": False},
        "memory_pred": {"card": "144-P1", "checkpoints": cps, "R": mp["R"], "N": mp["N"], "bind_ops": bind, "op_kinds": [o["kind"] for o in ops],
                        "start_mb": START, "start_cite": START_CITE, "peak_mb": mp["peak_mb"], "fail_above_mb": mp["fail_above_mb"], "below_fail": mp["ok"],
                        "prerun_start": xs, "prerun_peak_mb": mp2 and mp2["peak_mb"], "model": {"path": rel(SPR.MEMORY_MODEL), "md5": md5(SPR.MEMORY_MODEL)}},
        "summary": fz.get("summary")}
json.dump(pred, open(PP, "w", encoding="utf-8"), indent=1)
print("FACT ops", dict(collections.Counter(pred["ops"])), "census", pred["census"], "overall", pred["census_overall"], "unpredicted", len(pred["census_unpredicted"]),
      "| EL", pred["errorlist"]["predicted_total"], "| end rows", len(pred["cdiff_rows"]), "open pairs", len(p.get("open_rows") or []), flush=True)
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (RRP, PP))
gate("SP pred written, keyed to the plan md5", J(PP)["plan"]["md5"] == md5(RRP))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
sys.exit(1 if G["fail"] else 0)
