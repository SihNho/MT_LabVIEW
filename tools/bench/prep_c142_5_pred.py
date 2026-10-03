r"""prep_c142_5_pred - card 142-5 pass 3 (OFFLINE, no LabVIEW). After `stage_prerun.py --rebase plan_ring_p4_s02v18.json --graph
graph_ring_p4s01_20261002_234419.json` (prep_c142_5_rebase.log): the md5-pinned pred file plan_ring_p4_s02v18_pred.json for the recipe
pair stage_d1_ring_p4_s02v18.py / _scratch.py. COPIED from prep_c142_p1_pred.py (card 142-P1, written for rasrest, never run) with the
plan / pred / card names and the action count changed. X10 at start 596.5 MB (session 1 file's MEASURED load, PD326(a)(c)) against
memory_model.json's fail threshold; Error List predicted by PD322(e) (one item per CREATED node with an unwired input) on session 1's
measured full Error List 51 (PD326(a)).
PREDICTION CONTRACT: RB plan rebased (base not provisional, FINAL, open_rows_match, 34 actions, no negative uid left); RB2 base graph's vi
  md5 == session 1 file dc61e193; C compile each action once; X10 peak at 596.5 (678.5) <= fail threshold 680; X17 PASS; EL counted
  (created nodes with an unwired input reported, not required 0); SP pred written keyed to the plan md5.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c142_5_pred.log -- py -u tools/bench/prep_c142_5_pred.py"""
import collections, hashlib, json, os, sys                                                # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagexec as SX, stage_prerun as SPR, census_predict as CPR                        # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
RRP, PP = os.path.join(B, "plan_ring_p4_s02v18.json"), os.path.join(B, "plan_ring_p4_s02v18_pred.json")
START, START_CITE = 596.5, "session 1 file D1_ring_p4s01_20261002_232547.vi measured load 596.5 MB (diag_c141_3_facts.md:16; PD326(a)(c))"
EL_S1, EL_CITE = 51, "session 1 launch full Error List 51 == expected (PD326(a), diag_c141_3_facts.md)"
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
neg = SPR.negative_uids_left(p)          # card chat-S5 (PD337(d)): machine fields only - the old token scan read `why` text
gate("RB plan rebased: base {0} not provisional, FINAL, open_rows_match, {1} actions; no negative uid left".format(bp.get("path"), len(p["actions"])),
     not (p.get("base") or {}).get("provisional") and p.get("final") is True and fz.get("open_rows_match") is True and len(p["actions"]) == 34 and not neg,
     {"base": p.get("base"), "rebase": fz.get("rebase"), "neg": neg[:6]})
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
gate("X17 over s02v18", ok17, det17)
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
# card 143-3 (PD333(b)): the counted total comes from the FIXED predictor (unwired Local + While cond + created input; closed items debited);
# the PD322(e) lists above stay as report fields. selftest_elpred.py: this session re-derives to the measured 53.
sys.path.insert(0, B)
import prep_c143_3_elrule as ELR                                                            # noqa: E402
ELP = ELR.predict(st0, last, EL_S1, madeu)
print("EL FIXED", ELP["predicted_total"], "new", ELP["new_items"], "closed", ELP["closed_items"], flush=True)
pred = {"schema": "ring-p3b-pred/1", "card": "142-5", "note": "P4 v18 session 2 (v18 ops 25..58: rest of the slot-write repair + first non-repair ops) as one "
        "bed session on session 1's saved file; rebased onto its real graph; start = its MEASURED load (PD320(d), PD326(c))",
        "plan": {"path": rel(RRP), "md5": md5(RRP)}, "graph": {"path": bp["path"], "md5": md5(os.path.join(ROOT, bp["path"]))}, "bed": base.get("vi"), "bed_md5": base.get("md5"),
        "census": dict(rep["derived"]), "census_overall": rep["overall"], "census_unpredicted": [p["actions"][k - 1]["id"] for k in rep["unpredicted"]],
        "ops": [o["kind"] for o in ops], "cdiff_rows": sorted(fz.get("end_cdiff_rows") or []), "cross_session_refs": "bound by stage_prerun --rebase (finalized.rebase)",
        "errorlist": {"bed_total": EL_S1, "new_items_predicted": len(ELP["new_items"]) - len(ELP["closed_items"]), "predicted_total": ELP["predicted_total"],
                      "alternative_total": None, "fixed": ELP, "created_nodes_unwired_input": [[u, n] for u, n in created_unw],
                      "base_nodes_newly_unwired": [[u, n] for u, n in base_new], "nodes_unwired_at_step0_gone_at_end": gone_unw,
                      "rule": ELP["rule"] + "; base = " + EL_CITE, "checked": False},
        "memory_pred": {"card": "142-5", "checkpoints": cps, "R": mp["R"], "N": mp["N"], "bind_ops": bind, "op_kinds": [o["kind"] for o in ops],
                        "start_mb": START, "start_cite": START_CITE, "peak_mb": mp["peak_mb"], "fail_above_mb": mp["fail_above_mb"], "below_fail": mp["ok"],
                        "prerun_start": xs, "prerun_peak_mb": mp2 and mp2["peak_mb"], "model": {"path": rel(SPR.MEMORY_MODEL), "md5": md5(SPR.MEMORY_MODEL)}},
        "summary": fz.get("summary")}
json.dump(pred, open(PP, "w", encoding="utf-8"), indent=1)
print("FACT ops", dict(collections.Counter(pred["ops"])), "census", pred["census"], "unpredicted", pred["census_unpredicted"],
      "| EL", pred["errorlist"]["predicted_total"], "alt", pred["errorlist"]["alternative_total"], "| end rows", len(pred["cdiff_rows"]), "open pairs", len(p.get("open_rows") or []), flush=True)
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (RRP, PP))
gate("SP pred written, keyed to the plan md5", J(PP)["plan"]["md5"] == md5(RRP))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
