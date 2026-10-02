r"""prep_c139_p2_mkv11 - card 139-P2 (offline, no LabVIEW): plan_ring_p4_v11.json = plan_ring_p4_v10.json (9032dfcd) with the StopAll
route of PD314 (judgement 139):
  DROP  p4_i_stopall (indicator born on CT t642 in #639: UNROUTABLE, prep_c139_p1_facts.md:26), p4_lw_stopall_init (Local write on
        #4866, unmeasured, :32) and p4_w_stopall_init;
  KEEP  p4_c_stopall_f = KSF1 BooleanConstant const_donor on #4866 (DonorBoolF_v0 uid 0 SENTINEL, unchanged);
  ADD   p4_i_stopall_k  : indicator StopAll born on new:KSF1 on #4866 = the P2b const-indicator action form (plan_ring_p2b.json:37-48,
                          p2b_i_Num; route const_born_on -> gscript.create_indicator_on_const, stage_d1_ring_p2b.py:8 - launched);
        p4_lw_stopall_639: Local WRITE StopAll in #639 (the #637 body that owns 'stop (end)' t642);
        p4_w_stopall_639 : t642 -> LWS2.value, a same-diagram BRANCH on #639 (old sink w6929 -> #11639 kept; src form = v10 p4_x_fd).
The maker never copies `finalized`: raw v11 (finalized POPPED) -> plan_ring_p4_v11_in.json -> the EXISTING finalize path
stagesim.simulate (fs_routes_of regenerates finalized.fs_routes) -> plan_out IS plan_ring_p4_v11.json.

Prior art checked: prep_c139_p1_mkv10.py (whole skeleton: diff by id, meta walk, simulate, compile, route compare by action-id tuple -
copied, not imported, because the card forbids editing it); plan_ring_p2b.json p2b_c_Num/p2b_i_Num (const + indicator born_on new:K);
v10 p4_x_fd (control CT as src {uid, term_uid} = branch). No tools/*.py edited.

PREDICTION CONTRACT:
  - inputs md5 as the card; v11 = 185 - 3 + 3 = 185 actions; removed exactly the 3, added exactly the 3, modified none;
    every kept action identical to v10, v10 relative order; exactly ONE ControlTerminal labelled StopAll (p4_i_stopall_k), no
    'StopAll' label in the base graph; the Local actions labelled StopAll = {p4_lw_stopall_639 (write), p4_lr_stop12, p4_lr_stop_w1};
  - replay on the bed graph: END (base + 185 steps, no error); per-step cdiff == v10 at every shared id; end cdiff == v10's 24 rows;
  - fs_routes regenerated, every key's action id == its stored id; keys == v10's keys;
  - compile_plan(v11) 167 ops (== v10), ops per meta step <= 42;
  - route compare v10 -> v11 by action-id tuple: every differing op contains an added/removed id (0 OTHER);
  - advisory route check: no UNROUTABLE on the 3 added ids; the UNROUTABLE id set == v10's minus p4_i_stopall
    (carried: p4_w_stop12, p4_t_last).
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
V10 = os.path.join(B, "plan_ring_p4_v10.json")
G10 = os.path.join(B, "plan_ring_p4_v10_recipe_gates.json")
MK10 = os.path.join(B, "prep_c139_p1_mkv10.py")
V11IN = os.path.join(B, "plan_ring_p4_v11_in.json")
V11 = os.path.join(B, "plan_ring_p4_v11.json")
G11 = os.path.join(B, "plan_ring_p4_v11_recipe_gates.json")
META = os.path.join(B, "plan_ring_p4_v3_meta.json")
GRAPH = os.path.join(B, "graph_ring_p3b2b_20261002_133824.json")
V10SUM = os.path.join(B, "sim", "c139_p1_v10", "ring_p4_v3", "summary.json")
SIMDIR = os.path.join(B, "sim", "c139_p2_v11")
WANT = {V10: "9032dfcd256fbdd351b80b58cd88eb06", G10: "386a05466dae7facc34b32022879f218", MK10: "0a5170db03c15d9d305650e807aa4bab",
        GRAPH: "50595c62d0332a94bf066538cf20c0ae"}
DROP = ["p4_i_stopall", "p4_lw_stopall_init", "p4_w_stopall_init"]
KSF = "p4_c_stopall_f"
NEW = [
    {"op": "create", "id": "p4_i_stopall_k", "class": "ControlTerminal", "diagram": 4866, "as": "ISK1", "label": "StopAll",
     "indicator": True, "born_on": {"uid": "new:KSF1"},
     "why": ("ROUTE create indicator on const | PRECEDENT | PD314: non-latch Boolean indicator StopAll born on its False constant KSF1 "
             "on FS1 frame #4866 (initial value False every run, PD313(d)); P2b const-indicator form p2b_i_Num (plan_ring_p2b.json, "
             "launched, stage_d1_ring_p2b.py const_born_on -> create_indicator_on_const); replaces v10 p4_i_stopall (UNROUTABLE on CT t642)")},
    {"op": "create", "id": "p4_lw_stopall_639", "class": "Local", "diagram": 639, "as": "LWS2", "label": "StopAll", "mode": "write",
     "terminals": [{"name": "StopAll", "is_source": False, "term_class": "Terminal"}],
     "why": ("ROUTE local_write | PRECEDENT | PD314: ONE writer of StopAll = #637 body #639 owning 'stop (end)' t642, written every "
             "iteration; local_write in a loop body = v8 p4_lw_bufdiff form (32464); on #639 UNMEASURED")},
    {"op": "wire", "id": "p4_w_stopall_639", "src": {"uid": 642, "term_uid": 642}, "dst": "new:LWS2.value",
     "why": ("ROUTE branch | PRECEDENT | PD314: 'stop (end)' t642 (w6929 -> #11639, sink kept) -> LWS2.value, same-diagram BRANCH on "
             "#639; src form of v10 p4_x_fd (control t8936 {uid, term_uid})")},
]


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def J(p):
    return json.load(open(p, encoding="utf-8"))


def sig(o):
    return json.dumps(dict((k, v) for k, v in o.items() if k not in ("acts", "in_act", "out_act", "of_act")), sort_keys=True, default=str)


def by_ids(ops, A):
    return dict((tuple(A[n - 1]["id"] for n in o["acts"]), sig(o)) for o in ops)


def unroutable_ids(plan):
    rc = ((plan.get("finalized") or {}).get("route_check") or {})
    return rc.get("status"), sorted(set(i for r in (rc.get("rows") or []) if r.get("unroutable") for i in (r.get("ids") or ["?acts"])))


def main():
    G = {"pass": 0, "fail": 0, "first": None}

    def gate(ok, label, detail=""):
        G["pass" if ok else "fail"] += 1
        if not ok and G["first"] is None:
            G["first"] = label
        print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(detail)[:400]), flush=True)

    def done(rc, arts=()):
        print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], list(arts))), flush=True)
        return rc

    for p, w in WANT.items():
        gate(md5(p) == w, "input md5 " + os.path.basename(p), md5(p))
    v10 = J(V10)
    A10 = v10["actions"]
    ids10 = [a["id"] for a in A10]
    gate(all(i in ids10 for i in DROP + [KSF]) and not ({x["id"] for x in NEW} & set(ids10))
         and not ({"ISK1", "LWS2"} & {a.get("as") for a in A10}), "drop/keep ids in v10; new ids/as unused")
    A11 = []
    for a in A10:
        if a["id"] in DROP:
            continue
        A11.append(copy.deepcopy(a))
        if a["id"] == KSF:
            A11 += copy.deepcopy(NEW)
    gate(len(A11) == 185, "v11 = 185 - 3 + 3 = 185 actions", len(A11))
    raw = copy.deepcopy(v10)
    raw["actions"] = A11
    raw["goal"] = ("P4 v11 (card 139-P2, PD314): v10 9032dfcd with StopAll born on its False const KSF1 on #4866 (P2b const-indicator "
                   "form) and written in #639 by a Local write branched from 'stop (end)' t642; fs_routes regenerated; never launched")
    raw.pop("finalized", None)
    raw.pop("final", None)
    with open(V11IN, "w", encoding="utf-8") as f:
        json.dump(raw, f, indent=1, default=str)
    okv, whyv = protocol.validate_obj(J(V11IN))
    gate(okv, "v11_in validates (stageplan/1)", whyv)

    d10, d11 = dict((a["id"], a) for a in A10), dict((a["id"], a) for a in A11)
    removed = [i for i in ids10 if i not in d11]
    added = [a["id"] for a in A11 if a["id"] not in d10]
    modified = [i for i in ids10 if i in d11 and d10[i] != d11[i]]
    print("DIFF removed", [(ids10.index(i) + 1, i) for i in removed])
    print("DIFF added", [(A11.index(d11[i]) + 1, i, d11[i]["op"]) for i in added])
    print("DIFF modified", modified)
    gate(removed == DROP and added == [x["id"] for x in NEW] and not modified, "removed the 3, added the 3, modified none",
         (removed, added, modified))
    kept = [i for i in ids10 if i in d11]
    gate([a["id"] for a in A11 if a["id"] in d10] == kept and all(d10[i] == d11[i] for i in kept),
         "every kept v10 action identical, v10 relative order", len(kept))
    cts = [a["id"] for a in A11 if a.get("class") == "ControlTerminal" and a.get("label") == "StopAll"]
    locs = [(A11.index(a) + 1, a["id"], a.get("mode"), a.get("diagram")) for a in A11 if a.get("class") == "Local" and a.get("label") == "StopAll"]
    print("STOPALL indicator", cts, "| Locals", locs)
    graw = open(GRAPH, encoding="utf-8").read()
    gate(cts == ["p4_i_stopall_k"] and "StopAll" not in graw, "ONE StopAll indicator (p4_i_stopall_k), no StopAll label in the bed graph", cts)
    gate(sorted(x[1] for x in locs) == sorted(["p4_lw_stopall_639", "p4_lr_stop12", "p4_lr_stop_w1"])
         and min(x[0] for x in locs) > A11.index(d11["p4_i_stopall_k"]) + 1, "StopAll Locals = LWS2 write + 1.2/W1 reads, all after the indicator", locs)

    meta, stepof = J(META), {}

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
                   ("p4_lr_stop12", [KSF] + [x["id"] for x in NEW])):
        for x in ids:
            stepof[x] = stepof.get(k)

    # ---- finalize path = v11
    import stagesim as SS
    import stagexec as SX
    os.makedirs(SIMDIR, exist_ok=True)
    S = None
    try:
        S = SS.simulate(V11IN, GRAPH, out_root=SIMDIR, plan_out_dir=SIMDIR)
    except Exception as e:
        print("SIM EXCEPTION", type(e).__name__, e)
        traceback.print_exc()
    gate(S is not None, "simulate returned")
    if S is None:
        return done(1)
    po = S["plan_out"]["path"]
    po = po if os.path.isabs(po) else os.path.join(ROOT, po)
    shutil.copyfile(po, V11)
    v11 = J(V11)
    print("SIM plan_out", po, md5(V11))
    gate(v11["actions"] == A11, "v11 actions == maker actions (plan_out of the finalize)")
    fr = (v11.get("finalized") or {}).get("fs_routes") or {}
    fr10 = (v10.get("finalized") or {}).get("fs_routes") or {}
    bad = [(k, r.get("id"), A11[int(k) - 1]["id"]) for k, r in fr.items() if A11[int(k) - 1]["id"] != r.get("id")]
    print("FS_ROUTES v11", dict((k, (r["id"], r["how"])) for k, r in fr.items()))
    gate(fr and not bad and sorted(fr) == sorted(fr10), "v11 fs_routes regenerated: key ids == stored ids, keys == v10's", bad)

    steps = S.get("steps") or []
    errs = [s for s in steps if s.get("error")]
    last = steps[-1] if steps else {}
    print("SIM final={0} failed={1} steps={2} last={3} {4}".format(S.get("final"), S.get("failed"), len(steps), last.get("n"), last.get("id")))
    print("SIM first stop", (errs[0].get("n"), errs[0].get("id"), str(errs[0].get("error"))[:600]) if errs else "none (END)")
    s10 = J(V10SUM)
    c10 = dict((s.get("id"), s.get("cdiff_rows")) for s in (s10.get("steps") or []))
    dif = []
    for s in steps:
        if s.get("id") in set(added) | {KSF}:
            print("STEP", s.get("n"), s.get("op"), s.get("id"), "error" if s.get("error") else "ok",
                  str(s.get("error") or s.get("effect_summary"))[:300], "cdiff", len(s.get("cdiff_rows") or []))
        if s.get("id") in c10 and c10[s.get("id")] != s.get("cdiff_rows"):
            dif.append((s.get("n"), s.get("id"), len(c10[s.get("id")] or []), len(s.get("cdiff_rows") or [])))
    print("PER-STEP cdiff differs from v10 at", len(dif), "steps; first 12", dif[:12])
    gate(not errs and len(steps) == len(A11) + 1, "replay END (base + 185 steps, no error)", len(steps))
    gate(not dif, "per-step cdiff == v10 at every shared id", dif[:6])
    end, e10 = S.get("end_cdiff_rows") or [], set(s10.get("end_cdiff_rows") or [])
    print("END cdiff rows", len(end), "open_rows_match", S.get("open_rows_match"), "classed ok", (S.get("open_rows_classed") or {}).get("ok"))
    gate(set(end) == e10 and len(e10) == 24, "end cdiff rows == v10's 24", sorted(set(end) ^ e10))
    st10, un10 = unroutable_ids(v10)
    st11, un11 = unroutable_ids(v11)
    print("ROUTE CHECK v10", st10, un10, "| v11", st11, un11)
    gate(not (set(un11) & set(added)), "advisory route check: no UNROUTABLE on the 3 added ids", un11)
    gate(un11 == sorted(set(un10) - {"p4_i_stopall"}), "UNROUTABLE ids v11 == v10's minus p4_i_stopall (carried)", (un10, un11))

    try:
        o10, o11 = SX.compile_plan(v10), SX.compile_plan(v11)
    except SX.ExecStop as e:
        gate(False, "compile_plan v10/v11", e)
        return done(1)
    per = {}
    for o in o11:
        s_ = stepof.get(A11[o["acts"][0] - 1]["id"])
        per[s_] = per.get(s_, 0) + 1
    print("COMPILE v10 ops", len(o10), "v11 ops", len(o11), "v11 per meta step", dict(sorted(per.items(), key=str)))
    gate(len(o11) == len(o10) == 167, "compile ops v11 == v10 == 167", (len(o10), len(o11)))
    gate(max(per.values()) <= 42, "ops per meta step <= ~40 (re-cut above 42)", per)
    m10, m11 = by_ids(o10, A10), by_ids(o11, A11)
    ch = set(added) | set(removed)
    diffs = sorted(set(k for k in set(m10) | set(m11) if m10.get(k) != m11.get(k)))
    other = [k for k in diffs if not set(k) & ch]
    for k in diffs:
        print("ROUTE-DIFF", "OTHER" if k in other else "CHANGED-ID", k, "| v10", m10.get(k), "| v11", m11.get(k))
    gate(not other, "route compare v10->v11: every changed op on an added/removed id", other)

    g11 = J(G10)
    g11["schema_note"] = str(g11.get("schema_note", "")).replace("v10", "v11") + " | card 139-P2 (PD314): StopAll born on KSF1"
    g11["plan"] = {"path": "tools/bench/plan_ring_p4_v11.json", "md5": md5(V11)}
    g11["stop_route"]["actions"] = [KSF] + [x["id"] for x in NEW] + ["p4_lr_stop12", "p4_lr_stop_w1"]
    g11["stop_route"]["init"] = "PD314: StopAll born on its False constant KSF1 on #4866 (initial value every run); writer LWS2 in #639 from t642"
    with open(G11, "w", encoding="utf-8") as f:
        json.dump(g11, f, indent=1)
    print("GATES file", G11, md5(G11))
    gate(md5(V10) == WANT[V10], "v10 not written")
    return done(0 if not G["fail"] else 1, [{"path": "tools/bench/plan_ring_p4_v11.json", "md5": md5(V11)},
                                            {"path": "tools/bench/plan_ring_p4_v11_in.json", "md5": md5(V11IN)},
                                            {"path": "tools/bench/plan_ring_p4_v11_recipe_gates.json", "md5": md5(G11)}])


if __name__ == "__main__":
    sys.exit(main())
