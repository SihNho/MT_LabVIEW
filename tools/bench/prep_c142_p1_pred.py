r"""prep_c142_p1_pred - card 142-P1 pass 2b (OFFLINE, no LabVIEW). After `stage_prerun.py --rebase plan_ring_p4_rasrest.json --graph
graph_ring_p4s01_20261002_234419.json`: the md5-pinned pred file plan_ring_p4_rasrest_pred.json for the recipe pair
(stage_d1_ring_p4_rasrest.py / _scratch.py), same schema and fields as plan_ring_p4_s02_pred.json (prep_c141_p1_mk.py:363-411, copied).
X10 at start 596.5 MB (session 1 file's MEASURED load, PD326(a)(c)) against memory_model.json's fail threshold; Error List predicted by
PD322(e) (one item per CREATED node with an unwired input) on session 1's measured full Error List 51 (PD326(a)).
PREDICTION CONTRACT: RB plan rebased (base not provisional, == the s01 graph or its fsmap copy, FINAL, open_rows_match, 26 actions, no
  negative uid left); C compile each action once; X10 peak at 596.5 <= fail threshold; X17 PASS; EL created nodes with an unwired input
  == 0 (RX4/RX5 get all 4 terminals wired) -> predicted 51; SP pred written.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c142_p1_pred.log -- py -u tools/bench/prep_c142_p1_pred.py"""
import collections, hashlib, json, os, sys                                                # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagexec as SX, stage_prerun as SPR, census_predict as CPR                        # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
RRP, PP = os.path.join(B, "plan_ring_p4_rasrest.json"), os.path.join(B, "plan_ring_p4_rasrest_pred.json")
GR, S01PRED = os.path.join(B, "graph_ring_p4s01_20261002_234419.json"), os.path.join(B, "plan_ring_p4_s01_pred.json")
START, START_CITE = 596.5, "session 1 file D1_ring_p4s01_20261002_232547.vi measured load 596.5 MB (diag_c141_3_facts.md:16; PD326(a)(c))"
EL_S1, EL_CITE = 51, "session 1 launch full Error List 51 == expected (PD326(a), diag_c141_3_facts.md)"
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                 # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
G, ARTS = {"pass": 0, "fail": 0, "first": None}, []


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:800]), flush=True)
    return ok


def done():
    print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
    sys.exit(0 if not G["fail"] else 1)


p = J(RRP)
fz = p.get("finalized") or {}
bp = (fz.get("base") or p.get("base") or {})
neg = SPR.negative_uids_left(p)          # card chat-S5 (PD337(d)): machine fields only - the old token scan read `why` text
gate("RB plan rebased: base {0} not provisional, FINAL, open_rows_match, {1} actions; no negative uid left".format(bp.get("path"), len(p["actions"])),
     not (p.get("base") or {}).get("provisional") and p.get("final") is True and fz.get("open_rows_match") is True and len(p["actions"]) == 26 and not neg,
     {"base": p.get("base"), "rebase": fz.get("rebase"), "neg": neg[:6]})
if G["fail"]:
    done()
base = J(bp["path"])
gate("RB2 base graph's vi md5 == session 1 file dc61e193", base.get("md5") == "dc61e193e0376ce760f88fdfcda7087b", base.get("md5"))
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
gate("X17 over rasrest", ok17, det17)
rep = CPR.predict(p, {}, J(os.path.join(B, "census_samples.json")))
sf = fz.get("step_files") or []
st0, last = J(sf[0]["path"])["state"], J(sf[-1]["path"])["state"]
madeu = set(int(u) for u in (last.get("sym") or {}).values() if isinstance(u, int))


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
gate("EL created nodes with an unwired input == 0 -> predicted {0}".format(EL_S1 + len(created_unw)), not created_unw, created_unw)
pred = {"schema": "ring-p3b-pred/1", "card": "142-P1", "note": "P4 slot-write repair REST (v17 #25..#50) as one bed session on session 1's saved file; "
        "rebased onto its real graph; start = its MEASURED load (PD320(d), PD326(c))",
        "plan": {"path": rel(RRP), "md5": md5(RRP)}, "graph": {"path": bp["path"], "md5": md5(os.path.join(ROOT, bp["path"]))}, "bed": base.get("vi"), "bed_md5": base.get("md5"),
        "census": dict(rep["derived"]), "census_overall": rep["overall"], "census_unpredicted": [p["actions"][k - 1]["id"] for k in rep["unpredicted"]],
        "ops": [o["kind"] for o in ops], "cdiff_rows": sorted(fz.get("end_cdiff_rows") or []), "cross_session_refs": "bound by stage_prerun --rebase (finalized.rebase)",
        "errorlist": {"bed_total": EL_S1, "new_items_predicted": len(created_unw), "predicted_total": EL_S1 + len(created_unw),
                      "alternative_total": EL_S1 + len(created_unw) + len(base_new), "created_nodes_unwired_input": [[u, n] for u, n in created_unw],
                      "base_nodes_newly_unwired": [[u, n] for u, n in base_new], "rule": "PD322(e) per created node; base = " + EL_CITE, "checked": False},
        "memory_pred": {"card": "142-P1", "checkpoints": cps, "R": mp["R"], "N": mp["N"], "bind_ops": bind, "op_kinds": [o["kind"] for o in ops],
                        "start_mb": START, "start_cite": START_CITE, "peak_mb": mp["peak_mb"], "fail_above_mb": mp["fail_above_mb"], "below_fail": mp["ok"],
                        "prerun_start": xs, "prerun_peak_mb": mp2 and mp2["peak_mb"], "model": {"path": rel(SPR.MEMORY_MODEL), "md5": md5(SPR.MEMORY_MODEL)}},
        "summary": fz.get("summary")}
json.dump(pred, open(PP, "w", encoding="utf-8"), indent=1)
print("FACT ops", dict(collections.Counter(pred["ops"])), "census", pred["census"], "unpredicted", len(pred["census_unpredicted"]),
      "| EL", pred["errorlist"]["predicted_total"], "alt", pred["errorlist"]["alternative_total"], "| end rows", len(pred["cdiff_rows"]), "open pairs", len(p.get("open_rows") or []), flush=True)
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (RRP, PP))
gate("SP pred written, keyed to the plan md5", J(PP)["plan"]["md5"] == md5(RRP))
done()
