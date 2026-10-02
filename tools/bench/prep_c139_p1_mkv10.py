r"""prep_c139_p1_mkv10 - card 139-P1 (offline, no LabVIEW): plan_ring_p4_v10.json = plan_ring_p4_v8.json (059b5296) + PD313(c)(d)(a)
(docs/d1/ring-p4.md:282-292) + PD312(c):
  (1) v9's latch stop route BY ID (p4_i_stopall added; p4_lr_stop12 / p4_lr_stop_w1 relabelled to StopAll) - copied from v9 b91cf4d7;
  (2) StopAll := False on FS1 frame #4866 every run (PD313(d), PD240(b)(c) mechanism): a Boolean const_donor + a Local WRITE of StopAll
      + one wire, all on #4866 (outside the loops; the FS orders it before the loops by structure);
  (3) KMX1/KMX2 donor uid 0 -> 127 (PD313(a), measured by 138-6, diag_c138_6_facts.md);
  (4) IndexMode gates TI-TFN1/TFB1/TFS1 (v9's recipe notes, now plan_ring_p4_v10_recipe_gates.json) + v9's tunnel whys.
The maker never copies `finalized`: the raw v10 (finalized POPPED) is written to plan_ring_p4_v10_in.json and run through the
EXISTING finalize path stagesim.simulate (stagesim.py:2492-2510, fs_routes_of), whose plan_out IS plan_ring_p4_v10.json.

Prior art checked: prep_c138_p1_mkv9.py (diff, meta walk, simulate/compile calls - copied); review
archive/peer/2026-10-02-c138-6-p1cmp-routes.md (stale position-keyed fs_routes = the v9 defect; test (a)/(b) form); P2b
plan_ring_p2b.json (#4866 init form), v8 p4_lw_bufdiff (local_write form), v9 p4_k_max (const_donor scalar + uid-sentinel form).
No measured Boolean-False donor exists (claudeDev Donor*.vi: none Boolean; docs grep) -> KSF1 donor claudeDev\DonorBoolF_v0.vi uid 0
SENTINEL, PENDING a LabVIEW card (OPEN). No tools/*.py edited.

PREDICTION CONTRACT:
  - inputs md5 as the card; v10 = 181 + 4 = 185 actions (p4_i_stopall, p4_c_stopall_f, p4_lw_stopall_init, p4_w_stopall_init);
  - modified exactly the 7 of v9 (why; label+terminals for the 2 locals; donor+why for KMX1/KMX2); others identical, v8 order;
  - finalized.fs_routes of v10 regenerated: every key k has A[k-1].id == its stored id;
  - compile_plan(v10) OK, 167 ops (v8 163 + 4), ops per meta step <= 42;
  - route compare v8 -> v10 by action-id tuple: every differing op contains an added/modified id;
  - replay END (base + 185 steps); per-step cdiff equal to v8 at every shared id; end cdiff == v8's 24 (prediction).
"""
import copy
import hashlib
import json
import os
import shutil
import sys
import traceback

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402

B = os.path.join(ROOT, "tools", "bench")
V8 = os.path.join(B, "plan_ring_p4_v8.json")
V9 = os.path.join(B, "plan_ring_p4_v9.json")
G9 = os.path.join(B, "plan_ring_p4_v9_recipe_gates.json")
V10IN = os.path.join(B, "plan_ring_p4_v10_in.json")
V10 = os.path.join(B, "plan_ring_p4_v10.json")
G10 = os.path.join(B, "plan_ring_p4_v10_recipe_gates.json")
META = os.path.join(B, "plan_ring_p4_v3_meta.json")
GRAPH = os.path.join(B, "graph_ring_p3b2b_20261002_133824.json")
V8SUM = os.path.join(B, "sim", "c138_4_v8", "ring_p4_v3", "summary.json")
V8SIMPLAN = os.path.join(B, "sim", "c138_4_v8", "plan_ring_p4_v3.json")
V9SIMPLAN = os.path.join(B, "sim", "c138_p1_v9", "plan_ring_p4_v3.json")
SIMDIR = os.path.join(B, "sim", "c139_p1_v10")
WANT = {V8: "059b52964d4d05a67049add4798cb9b0", V9: "b91cf4d7e1d0e04ec6b1f5f6a6c777f0", G9: "d9d0f2695c47569c43aa7601ac97e5f2",
        GRAPH: "50595c62d0332a94bf066538cf20c0ae"}
CD = "C:\\Program Files\\National Instruments\\LabVIEW 2026\\user.lib\\claudeDev\\"
FROM_V9 = ["p4_i_stopall", "p4_lr_stop12", "p4_lr_stop_w1", "p4_t_fnum", "p4_t_fgt", "p4_t_fsel"]
KMX = {"p4_k_max": "; KMX1 = Select.f inside the For",
       "p4_k_max_found": "; KMX2 = LT1.y; const_row REFUTED (DBL diag_c137_7_types.log:218)"}
KWHY = ("ROUTE create | MEASURED | PD313(a)/PD312(c) ONE donor claudeDev\\DonorI32Max_v0.vi (md5 c0c8db65) constant uid 127, I32 "
        "2147483647, ExecState 1, read back by card 138-6 (tools/bench/diag_c138_6_facts.md) - for KMX1 AND KMX2")
INIT = [
    {"op": "create", "id": "p4_c_stopall_f", "class": "BooleanConstant", "diagram": 4866, "as": "KSF1", "prim": "const_donor",
     "donor": {"donor": CD + "DonorBoolF_v0.vi", "uid": 0},
     "terminals": [{"name": "", "is_source": True, "term_class": "Terminal"}],
     "why": ("ROUTE create const_donor | PENDING donor | PD313(d)/PD240(b)(c): False constant on FS1 frame #4866 (P2b p2b_c_Num form, "
             "launched); NO Boolean-False donor exists in claudeDev -> DonorBoolF_v0.vi uid 0 = SENTINEL, build + read back + BIND "
             "before launch (plan_ring_p4_v10_recipe_gates.json donor_bind)")},
    {"op": "create", "id": "p4_lw_stopall_init", "class": "Local", "diagram": 4866, "as": "LWS1", "label": "StopAll",
     "mode": "write", "terminals": [{"name": "StopAll", "is_source": False, "term_class": "Terminal"}],
     "why": ("ROUTE local_write | PRECEDENT | PD313(d): StopAll := False every run on FS1 frame #4866, before the loops by FS order "
             "(PD240(c)); local_write in a FS frame = v8 p4_lw_bufdiff / P3b-2 p3b_lw_rotpos (32464); on #4866 UNMEASURED")},
    {"op": "wire", "id": "p4_w_stopall_init", "src": "new:KSF1.value", "dst": "new:LWS1.value",
     "why": "ROUTE connect | PRECEDENT | PD313(d) False -> Local write StopAll, same frame #4866 (v8 p4_w_b_out form, one diagram)"},
]
INSERT_AFTER = "p4_i_stopall"


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def J(p):
    return json.load(open(p, encoding="utf-8"))


def sig(o, A):
    s = dict((k, v) for k, v in o.items() if k not in ("acts", "in_act", "out_act", "of_act"))
    return json.dumps(s, sort_keys=True, default=str)


def by_ids(ops, A):
    return dict((tuple(A[n - 1]["id"] for n in o["acts"]), sig(o, A)) for o in ops)


def main():
    G = {"pass": 0, "fail": 0, "first": None}

    def gate(ok, label, detail=""):
        G["pass" if ok else "fail"] += 1
        if not ok and G["first"] is None:
            G["first"] = label
        print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(detail)[:400]))

    for p, w in WANT.items():
        gate(md5(p) == w, "input md5 " + os.path.basename(p), md5(p))
    v8, v9 = J(V8), J(V9)
    A8, d9 = v8["actions"], dict((a["id"], a) for a in v9["actions"])
    ids8 = [a["id"] for a in A8]
    gate(all(i in d9 for i in FROM_V9) and all(i in ids8 for i in list(KMX) + FROM_V9[1:]), "anchor ids in v8/v9")
    used_as = {a.get("as") for a in A8}
    gate(not ({"IS1", "KSF1", "LWS1"} & used_as) and not ({x["id"] for x in INIT} & set(ids8)), "new as/ids unused in v8")
    A10 = []
    for a in A8:
        if a["id"] in KMX:
            b = copy.deepcopy(a)
            b["donor"] = {"donor": CD + "DonorI32Max_v0.vi", "uid": 127}
            b["why"] = KWHY + KMX[a["id"]]
            A10.append(b)
        elif a["id"] in d9:
            if a["id"] == FROM_V9[1]:                                   # p4_lr_stop12: v9 inserted p4_i_stopall before it
                A10.append(copy.deepcopy(d9[INSERT_AFTER]))
                A10 += copy.deepcopy(INIT)
            b = copy.deepcopy(d9[a["id"]])
            if a["id"] in ("p4_t_fnum", "p4_t_fgt", "p4_t_fsel"):
                b["why"] = b["why"].replace("plan_ring_p4_v9_recipe_gates.json", "plan_ring_p4_v10_recipe_gates.json")
            A10.append(b)
        else:
            A10.append(copy.deepcopy(a))
    long_ = [(a["id"], k, len(v)) for a in A10 for k, v in a.items() if isinstance(v, str) and len(v) > 400]
    gate(not long_, "every action string <= 400 chars", long_)
    if long_:
        print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])))
        return 1
    raw = copy.deepcopy(v8)
    raw["actions"] = A10
    raw["goal"] = ("P4 v10 (card 139-P1): v8 059b5296 + PD313(c)(d)(a)/PD312(c): latch stop route via StopAll (from v9 by id), "
                   "StopAll:=False on #4866, KMX donor uid 127, IndexMode gates; fs_routes regenerated by stagesim; never launched")
    raw.pop("finalized", None)
    raw.pop("final", None)
    with open(V10IN, "w", encoding="utf-8") as f:
        json.dump(raw, f, indent=1, default=str)
    okv, whyv = protocol.validate_obj(J(V10IN))
    gate(okv, "v10_in validates (stageplan/1)", whyv)
    gate(len(A10) == 185, "v10 = 181 + 4 = 185 actions", len(A10))

    d8, d10 = dict((a["id"], a) for a in A8), dict((a["id"], a) for a in A10)
    removed = [i for i in ids8 if i not in d10]
    added = [a["id"] for a in A10 if a["id"] not in d8]
    modified = [i for i in ids8 if i in d10 and d8[i] != d10[i]]
    keys = dict((i, sorted(k for k in set(d8[i]) | set(d10[i]) if d8[i].get(k) != d10[i].get(k))) for i in modified)
    print("DIFF removed", removed)
    print("DIFF added", [(A10.index(d10[i]) + 1, i, d10[i]["op"]) for i in added])
    for i in modified:
        print("  MOD", i, "keys", keys[i])
    want_add = [INSERT_AFTER] + [x["id"] for x in INIT]
    gate(not removed and added == want_add, "removed none, added exactly the 4", (removed, added))
    gate(sorted(modified) == sorted(list(KMX) + FROM_V9[1:]), "modified exactly the 7", modified)
    want_k = dict([(i, ["donor", "why"]) for i in KMX] + [(i, ["label", "terminals", "why"]) for i in FROM_V9[1:3]]
                  + [(i, ["why"]) for i in FROM_V9[3:]])
    gate(keys == want_k, "changed keys per modified action", keys)
    same8 = [i for i in ids8 if i not in modified]
    gate([i for i in [a["id"] for a in A10] if i in same8] == same8, "unchanged v8 actions identical, v8 order", len(same8))
    gate(all(d10[i] == d9[i] for i in FROM_V9[:3]), "stop-route actions == v9's by id")

    g9 = J(G9)
    g10 = copy.deepcopy(g9)
    g10["schema_note"] = g9["schema_note"].replace("card 138-P1 (PD312(c)(d))", "card 139-P1 (PD313, from v9's)").replace("v9", "v10")
    g10["plan"] = {"path": "tools/bench/plan_ring_p4_v10.json", "md5": None}
    g10["donor_bind"] = [
        dict(g9["donor_bind"], uid=127, rule="BOUND: uid 127 measured by card 138-6 (diag_c138_6_facts.md; PD313(a))"),
        {"ids": ["p4_c_stopall_f"], "donor": "claudeDev\\DonorBoolF_v0.vi", "value": False, "type": "Boolean", "uid": 0,
         "rule": "uid 0 = SENTINEL; the donor VI does not exist yet; build + read back + bind before the v10 launch (PD313(d))"}]
    g10["stop_route"]["actions"] = [INSERT_AFTER] + [x["id"] for x in INIT] + FROM_V9[1:3]
    g10["stop_route"]["init"] = "PD313(d): StopAll := False on FS1 frame #4866 every run (PD240(b)(c))"

    meta = J(META)
    stepof = {}

    def walk(o):
        if isinstance(o, dict):
            if "id" in o and "step" in o and "unit" in o:
                stepof[o["id"]] = o["step"]
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(meta)
    for x, t, w in (("p4_x_fd", "p4_t_fd", "p4_w_fd_in"), ("p4_x_dt", "p4_t_dt", "p4_w_dt_in")):
        stepof[t] = stepof[w] = stepof.get(x)
    for n in ["p4_rbR_dw", "p4_rbR_re0", "p4_rbR_sel", "p4_rbR_lr", "p4_rbR_t", "p4_rbR_f", "p4_rbR_s", "p4_rbR_out"]:
        stepof[n] = stepof.get("p4_dec_reseed")
    for k, ids in (("p4_gt_last", ["p4_f_min"]), ("p4_k_max", ["p4_k_max_found"]),
                   ("p4_w_num_sel", ["p4_t_fnum", "p4_t_fnum_in", "p4_t_fnum_out"]),
                   ("p4_w_gt_sel", ["p4_t_fgt", "p4_t_fgt_in", "p4_t_fgt_out", "p4_w_max_sel"]),
                   ("p4_w_sel_amm", ["p4_t_fsel", "p4_t_fsel_in", "p4_t_fsel_out"]),
                   ("p4_lr_stop12", [INSERT_AFTER] + [x["id"] for x in INIT])):
        for x in ids:
            stepof[x] = stepof.get(k)
    cnt = {}
    for a in A10:
        cnt[stepof.get(a["id"])] = cnt.get(stepof.get(a["id"]), 0) + 1
    print("v10 ACTIONS per meta step", dict(sorted(cnt.items(), key=str)), "no meta step", [a["id"] for a in A10 if a["id"] not in stepof])

    # ---- finalize path (stagesim.simulate -> plan_out with regenerated finalized.fs_routes) = v10
    import stagesim as SS
    import stagexec as SX
    os.makedirs(SIMDIR, exist_ok=True)
    S = None
    try:
        S = SS.simulate(V10IN, GRAPH, out_root=SIMDIR, plan_out_dir=SIMDIR)
    except Exception as e:                                             # report, no retry
        print("SIM EXCEPTION", type(e).__name__, e)
        traceback.print_exc()
    gate(S is not None, "simulate returned")
    if S is None:
        print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])))
        return 1
    po = S["plan_out"]["path"]
    po = po if os.path.isabs(po) else os.path.join(ROOT, po)
    print("SIM plan_out", po, md5(po))
    shutil.copyfile(po, V10)
    v10 = J(V10)
    gate(v10["actions"] == A10, "v10 actions == maker actions (plan_out of the finalize)")
    fr = (v10.get("finalized") or {}).get("fs_routes") or {}
    bad = [(k, r.get("id"), A10[int(k) - 1]["id"]) for k, r in fr.items() if A10[int(k) - 1]["id"] != r.get("id")]
    print("FS_ROUTES v10", dict((k, (r["id"], r["how"])) for k, r in fr.items()))
    print("FS_ROUTES v8 (stored)", dict((k, (r["id"], r["how"])) for k, r in (v8["finalized"].get("fs_routes") or {}).items()))
    gate(fr and not bad, "v10 fs_routes regenerated: every key's action id == stored id", bad)
    g10["plan"]["md5"] = md5(V10)
    with open(G10, "w", encoding="utf-8") as f:
        json.dump(g10, f, indent=1)
    print("GATES file", G10, md5(G10))

    steps = S.get("steps") or []
    errs = [s for s in steps if s.get("error")]
    last = steps[-1] if steps else {}
    print("SIM final={0} failed={1} steps={2} last={3} {4}".format(S.get("final"), S.get("failed"), len(steps), last.get("n"),
                                                                   last.get("id")))
    print("SIM first stop", (errs[0].get("n"), errs[0].get("id"), str(errs[0].get("error"))[:600]) if errs else "none (END)")
    v8s = J(V8SUM)
    c8 = dict((s.get("id"), s.get("cdiff_rows")) for s in (v8s.get("steps") or []))
    dif = []
    for s in steps:
        if s.get("id") in set(added) | set(modified):
            print("STEP", s.get("n"), s.get("op"), s.get("id"), "error" if s.get("error") else "ok",
                  str(s.get("error") or s.get("effect_summary"))[:300], "cdiff", len(s.get("cdiff_rows") or []))
        if s.get("id") in c8 and c8[s.get("id")] != s.get("cdiff_rows"):
            dif.append((s.get("n"), s.get("id"), len(c8[s.get("id")] or []), len(s.get("cdiff_rows") or [])))
    print("PER-STEP cdiff differs from v8 at", len(dif), "steps; first 12", dif[:12])
    gate(not errs and len(steps) == len(A10) + 1, "replay END (base + 185 steps, no error)", len(steps))
    gate(not dif, "per-step cdiff == v8 at every shared id", dif[:6])
    end, v8end = S.get("end_cdiff_rows") or [], set(v8s.get("end_cdiff_rows") or [])
    print("END cdiff rows", len(end), "open_rows_match", S.get("open_rows_match"), "classed ok",
          (S.get("open_rows_classed") or {}).get("ok"), "route_check", ((v10.get("finalized") or {}).get("route_check") or {}).get("status"))
    gate(set(end) == v8end and len(v8end) == 24, "end cdiff rows == v8's 24", sorted(set(end) ^ v8end))

    # ---- compile + route compare by action id
    try:
        o8, o10 = SX.compile_plan(v8), SX.compile_plan(v10)
    except SX.ExecStop as e:
        gate(False, "compile_plan v8/v10", e)
        print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])))
        return 1
    per = {}
    for o in o10:
        s_ = stepof.get(A10[o["acts"][0] - 1]["id"])
        per[s_] = per.get(s_, 0) + 1
    print("COMPILE v8 ops", len(o8), "v10 ops", len(o10), "v10 per meta step", dict(sorted(per.items(), key=str)))
    gate(len(o10) == len(o8) + 4, "compile ops v10 == v8 + 4", (len(o8), len(o10)))
    gate(max(per.values()) <= 42, "ops per meta step <= ~40 (re-cut above 42)", per)
    m8, m10 = by_ids(o8, A8), by_ids(o10, A10)
    ch = set(added) | set(modified)
    diffs = sorted(set(k for k in set(m8) | set(m10) if m8.get(k) != m10.get(k)))
    on_edit = [k for k in diffs if set(k) & ch]
    other = [k for k in diffs if not set(k) & ch]
    for k in diffs:
        print("ROUTE-DIFF", "EDITED" if k in on_edit else "OTHER", k, "| v8", m8.get(k), "| v10", m10.get(k))
    gate(not other, "route compare v8->v10: every changed route on an added/edited action", other)
    # side facts (review c138-6-p1cmp-routes): v8's stored table vs v8's regenerated one; v9 sim plan_out vs v8
    try:
        ov8s = by_ids(SX.compile_plan(J(V8SIMPLAN)), J(V8SIMPLAN)["actions"])
        print("SIDE v8 stored vs v8 regenerated fs_routes: differing ops", [k for k in set(m8) | set(ov8s) if m8.get(k) != ov8s.get(k)])
        p9 = J(V9SIMPLAN)
        ov9 = by_ids(SX.compile_plan(p9), p9["actions"])
        print("SIDE v9 sim plan_out vs v8: differing ops", sorted(k for k in set(m8) | set(ov9) if m8.get(k) != ov9.get(k)))
    except Exception as e:
        print("SIDE EXCEPTION", type(e).__name__, e)
    gate(md5(V8) == WANT[V8] and md5(V9) == WANT[V9], "v8/v9 not written")
    print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"],
                                                    [{"path": "tools/bench/plan_ring_p4_v10.json", "md5": md5(V10)},
                                                     {"path": "tools/bench/plan_ring_p4_v10_in.json", "md5": md5(V10IN)},
                                                     {"path": "tools/bench/plan_ring_p4_v10_recipe_gates.json", "md5": md5(G10)}])))
    return 0 if not G["fail"] else 1


if __name__ == "__main__":
    sys.exit(main())
