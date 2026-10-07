# ---
# labview: none
# hardware: none
# ---
r"""prep_c145_p1_pred - card 145-a1-P1 step 3 (OFFLINE, no LabVIEW). The md5-pinned pred file plan_ring_p4_s05v18_pred.json for the recipe
pair stage_d1_ring_p4_s05v18.py / _scratch.py, on the PROVISIONAL base (s04v18's simulated END; never launched, regenerated after --rebase).
COPIED from prep_c144_p1_pred.py (b1283893) with: s04 -> s05 names; RB sim_of = s04v18 9ff46b0e; action count from
prep_c145_p1_session.json; START 598.5 PROVISIONAL (s03 file's measured fresh load); EL base = s04v18's PREDICTED total
(plan_ring_p4_s04v18_pred.json, keyed to 9ff46b0e, PD349 rule, card 144-a2-2) - s04's Error List is measured later by card 145-a1-1;
owners also from s04's real base (sim/ring_p4_s04v18_base_real_fsmap.json a63f5929). Added: a FACT of the sessions left after s05 (the
same per-op X10 formula as prep_c145_p1_mk.py:83 at the same start, splitting no 'of' group) - an estimate, not a plan.
PREDICTION CONTRACT: RB plan FINAL on a provisional base (sim_of s04v18 9ff46b0e), open_rows_match, N actions == session table; EL0 s04 pred
  keyed to 9ff46b0e; C compile each action once; X10 peak at 598.5 <= 680; X17 PASS; EL by the rule (number printed, not typed); SP pred
  keyed to the plan md5.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c145_p1_pred.log -- py -u tools/bench/prep_c145_p1_pred.py"""
import collections, hashlib, json, os, sys                                                # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
from tools import protocol  # noqa: E402
import stagexec as SX, stage_prerun as SPR, census_predict as CPR                        # noqa: E401,E402
import prep_c143_3_elrule as ELR                                                            # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
RRP, PP = os.path.join(B, "plan_ring_p4_s05v18.json"), os.path.join(B, "plan_ring_p4_s05v18_pred.json")
S04, S04P = os.path.join(B, "plan_ring_p4_s04v18.json"), os.path.join(B, "plan_ring_p4_s04v18_pred.json")
V18 = os.path.join(B, "plan_ring_p4_v18.json")
SESS = os.path.join(B, "prep_c145_p1_session.json")
START, START_CITE = 598.5, ("PROVISIONAL 598.5 = session 3 file's measured fresh load (brief 145-a1-P1 step 1); REPLACE by session 4 file's measured load "
                            "at rebase (PD320(d))")
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
SJ = J(SESS)
NA = SJ["actions"]
fz = p.get("finalized") or {}
bp = (fz.get("base") or p.get("base") or {})
so = (p.get("base") or {}).get("sim_of") or {}
gate("RB plan FINAL on a provisional base {0} (sim_of {1}), open_rows_match, {2} actions == session table {3}".format(bp.get("path"), so, len(p["actions"]), NA),
     (p.get("base") or {}).get("provisional") is True and so.get("md5") == md5(S04) == "9ff46b0ece1f238c831d7786616c4f05" and p.get("final") is True
     and fz.get("open_rows_match") is True and len(p["actions"]) == NA, {"base": p.get("base")})
s4p = J(S04P)
gate("EL0 s04v18 pred keyed to 9ff46b0e", (s4p.get("plan") or {}).get("md5") == md5(S04), s4p.get("plan"))
EL_S4 = s4p["errorlist"]["predicted_total"]
EL_CITE = "session 4 (s04v18) PREDICTED total {0} by the PD349 rule (plan_ring_p4_s04v18_pred.json {1}, card 144-a2-2); re-derive from session 4's measured Error List at rebase".format(
    EL_S4, md5(S04P))
base = J(bp["path"])
s04 = J(S04)
rbase = J(((s04.get("finalized") or {}).get("base") or s04.get("base"))["path"])                # s04's real base (owners of base nodes)
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
# sessions left after s05: prep_c145_p1_mk.py:72-80 formula, greedy, same start (an estimate; every later start is measured)
v18 = J(V18)
VO = SX.compile_plan(v18)
VA = v18["actions"]
a2o = dict((n, k) for k, o in enumerate(VO, 1) for n in o["acts"])
vpos = dict((a["id"], k) for k, a in enumerate(VA, 1))
vgr = [(a2o[vpos[a["of"]]], a2o[vpos[a["id"]]]) for a in VA if a.get("of") and a["of"] in vpos]
VB = set(k for k, o in enumerate(VO, 1) if o["kind"] in SX.BIND_KINDS)
vv = lambda k: float(MODEL[k]["value"])                                                     # noqa: E731
pk = lambda a, b: round(START + len({a, b} | set(k for k in VB if a < k <= b)) * vv("read_mb") + (b - a) * (vv("edit_mb") + vv("other_mb")) + vv("final_read_mb"), 1)   # noqa: E731
cok = lambda b: b == len(VO) or not any(lo <= b < hi for lo, hi in vgr)                    # noqa: E731
segs, a0 = [], SJ["ops"][1]
while a0 < len(VO):
    b0 = max([b for b in range(a0 + 1, len(VO) + 1) if pk(a0, b) <= SPR.X10_FAIL_MB and cok(b)] or [None], key=lambda x: x or 0)
    if b0 is None:
        segs.append((a0 + 1, None))
        break
    segs.append((a0 + 1, b0, pk(a0, b0)))
    a0 = b0
print("FACT SESSIONS-LEFT after s05 (ops {0}..{1} of {2}): {3} session(s) {4} at start {5} (estimate)".format(SJ["ops"][1] + 1, len(VO), len(VO), len(segs), segs, START), flush=True)
ok17, det17 = SPR.x17_gate([p])
gate("X17 over s05v18", ok17, det17)
rep = CPR.predict(p, {}, J(os.path.join(B, "census_samples.json")))
sf = fz.get("step_files") or []
st0, last = J(sf[0]["path"])["state"], J(sf[-1]["path"])["state"]
madeu = set(int(u) for u in (last.get("sym") or {}).values() if isinstance(u, int)) - set(int(u) for u in (st0.get("sym") or {}).values() if isinstance(u, int))
ELP = ELR.predict(st0, last, EL_S4, madeu, extra_owner_states=(rbase,))
byc = collections.Counter(k[0] for k in ELP["new_items"]), collections.Counter(k[0] for k in ELP["closed_items"])
print("EL PD349 s05: base {0} new {1} closed {2} -> {3}; per class new {4} closed {5}; open at start {6}; uncertain {7}; detail_end {8}; created {9}; "
      "steps {10} -> {11}".format(EL_S4, ELP["new_items"], ELP["closed_items"], ELP["predicted_total"], dict(byc[0]), dict(byc[1]), ELP["open_at_start"],
                                  ELP["uncertain_base_newly_unwired_inputs"], ELP["detail_end"], sorted(madeu), sf[0]["path"], sf[-1]["path"]), flush=True)
print("FACT EL rule: {0}".format(ELP.get("rule")), flush=True)
pred = {"schema": "ring-p3b-pred/1", "card": "145-a1-P1", "note": "P4 v18 session 5 (v18 ops {0}) as one bed session on session 4's saved file; PROVISIONAL base = "
        "session 4's simulated end - regenerate after stage_prerun --rebase onto session 4's saved file (start = its MEASURED load, PD320(d)); "
        "Error List by the PD349 rule".format(SJ["ops"]),
        "plan": {"path": rel(RRP), "md5": md5(RRP)}, "graph": {"path": bp["path"], "md5": md5(os.path.join(ROOT, bp["path"]))}, "bed": base.get("vi"), "bed_md5": base.get("md5"),
        "census": dict(rep["derived"]), "census_overall": rep["overall"], "census_unpredicted": [p["actions"][k - 1]["id"] for k in rep["unpredicted"]],
        "ops": [o["kind"] for o in ops], "cdiff_rows": sorted(fz.get("end_cdiff_rows") or []),
        "cross_session_refs": "{0} refs to s03/s04 symbols -> real / provisional uids (prep_c145_p1_mk.log C2, R3)".format(len(SJ["cross_refs"])),
        "errorlist": {"bed_total": EL_S4, "new_items_predicted": len(ELP["new_items"]) - len(ELP["closed_items"]), "predicted_total": ELP["predicted_total"],
                      "alternative_total": None, "fixed": ELP, "rule": ELP["rule"] + "; base = " + EL_CITE,
                      "rule_source": {"path": "tools/bench/prep_c143_3_elrule.py", "md5": md5(os.path.join(B, "prep_c143_3_elrule.py")),
                                      "module": "tools/elrule.py", "module_md5": md5(os.path.join(ROOT, "tools", "elrule.py")), "pd": "PD349"},
                      "base_file": rel(S04P), "checked": False},
        "memory_pred": {"card": "145-a1-P1", "checkpoints": cps, "R": mp["R"], "N": mp["N"], "bind_ops": bind, "op_kinds": [o["kind"] for o in ops],
                        "start_mb": START, "start_cite": START_CITE, "peak_mb": mp["peak_mb"], "fail_above_mb": mp["fail_above_mb"], "below_fail": mp["ok"],
                        "prerun_start": xs, "prerun_peak_mb": mp2 and mp2["peak_mb"], "model": {"path": rel(SPR.MEMORY_MODEL), "md5": md5(SPR.MEMORY_MODEL)}},
        "sessions_left_estimate": segs,
        "summary": fz.get("summary")}
json.dump(pred, open(PP, "w", encoding="utf-8"), indent=1)
print("FACT ops", dict(collections.Counter(pred["ops"])), "census", pred["census"], "overall", pred["census_overall"], "unpredicted", len(pred["census_unpredicted"]),
      "| EL", pred["errorlist"]["predicted_total"], "| end rows", len(pred["cdiff_rows"]), "open pairs", len(p.get("open_rows") or []), flush=True)
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (RRP, PP))
gate("SP pred written, keyed to the plan md5", J(PP)["plan"]["md5"] == md5(RRP))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
sys.exit(1 if G["fail"] else 0)
