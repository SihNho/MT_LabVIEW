r"""prep_c138_p1_mkv9 - card 138-P1 (offline, no LabVIEW): plan_ring_p4_v9.json = plan_ring_p4_v8.json (059b5296) + PD312(c)(d)
(docs/d1/ring-p4.md:258-266): (1) KMX1/KMX2 const_donor marked to ONE donor claudeDev\DonorI32Max_v0.vi, uid 0 SENTINEL to bind
after card 138-6; (2) an IndexMode gate per auto-index tunnel TFN1/TFB1/TFS1 in PD235(c) form (recipe-level index_mode_fix +
read-back, stage_d1_qrt_pool.py:46-47) as recipe notes in plan_ring_p4_v9_recipe_gates.json + the tunnel whys; (3) the LATCH stop
route of PD298(e): new non-latch Boolean indicator StopAll born on 'stop (end)' CT t642 in #639 (written every iteration), W1's
and 1.2's Locals read StopAll instead of 'stop (end)'. Then stagesim replay of v9 on graph_ring_p3b2b_20261002_133824.json and
stagexec.compile_plan(v9).

Prior art checked: tools/bench/prep_c138_4_mkv8.py (v7 -> v8 maker: diff, meta step walk, simulate/compile calls - copied);
tools/bench/plan_ring_p4_v3_latch_in.json:94-122,560-575 (the latch form drafted in card 136-P2: p4_i_stopall + 2 StopAll locals
- copied, with born_on re-addressed by the CT's OWN uid {642, 642} per PD303(a), v8's p4_x_fd form {8936, 8936});
plan_qrt_pool_pred.json:18 (tunnel_rule note form). No tools/*.py is edited (card rule); stagesim/stagexec used unchanged.

PREDICTION CONTRACT:
  - inputs md5 as the card (v8 059b5296, graph 50595c62); v9 = 181 + 1 (p4_i_stopall) = 182 actions; removed none;
  - modified ids exactly {p4_k_max, p4_k_max_found, p4_t_fnum, p4_t_fgt, p4_t_fsel, p4_lr_stop12, p4_lr_stop_w1}, and in them only
    the keys why (all 7) and label + terminals (the 2 locals); every other v8 action identical and in v8 order; no top-level key changed;
  - compile_plan(v9) OK, 164 ops (v8 163 + 1), ops per meta step <= ~40;
  - replay END (base + 182 steps, no error); end cdiff rows == v8's 24 (StopAll is an added node, not a cdiff row - prediction).
"""
import copy
import hashlib
import json
import os
import sys
import traceback

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402

B = os.path.join(ROOT, "tools", "bench")
V8 = os.path.join(B, "plan_ring_p4_v8.json")
V9 = os.path.join(B, "plan_ring_p4_v9.json")
GATES = os.path.join(B, "plan_ring_p4_v9_recipe_gates.json")
META = os.path.join(B, "plan_ring_p4_v3_meta.json")
GRAPH = os.path.join(B, "graph_ring_p3b2b_20261002_133824.json")
V8SUM = os.path.join(B, "sim", "c138_4_v8", "ring_p4_v3", "summary.json")
SIMDIR = os.path.join(B, "sim", "c138_p1_v9")
WANT = {V8: "059b52964d4d05a67049add4798cb9b0", GRAPH: "50595c62d0332a94bf066538cf20c0ae"}
WHY_MAX = 400
PD = "PD312"
KWHY = ("ROUTE create | PENDING 138-6 | " + PD + "(c) ONE donor claudeDev\\DonorI32Max_v0.vi I32 2147483647 for KMX1 AND KMX2 "
        "(I32 type MEASURED diag_c137_7_types.log:212-216); built + read back by card 138-6; uid 0 = SENTINEL, BIND the donor "
        "object's uid from 138-6's record before launch (plan_ring_p4_v9_recipe_gates.json donor_bind)")
KMX = {"p4_k_max": "; KMX1 = Select.f inside the For",
       "p4_k_max_found": "; KMX2 = LT1.y; const_row REFUTED (DBL diag_c137_7_types.log:218)"}
TWHY = ("ROUTE tunnel | PRECEDENT | PD311(b) {0}: form plan_disp.json:425-468, For in plan-made While stage_d1_disp_r3.log:62-63 | "
        + PD + "(c) IndexMode GATE {1}: recipe calls be.index_mode_fix(tunnel, True) after Executor.run + read-back == 1 (PD235(c) "
        "stage_d1_qrt_pool.py:46-47; executor: only if lost, stagexec.py:2104-2109); plan_ring_p4_v9_recipe_gates.json")
TUN = {"p4_t_fnum": ("Num array -> Num[i] (auto-index IN)", "TFN1"),
       "p4_t_fgt": ("Num > last Boolean[] -> b[i] (auto-index IN)", "TFB1"),
       "p4_t_fsel": ("Select out -> I32 array (auto-index OUT)", "TFS1")}
LWHY = ("ROUTE local_read | PRECEDENT | " + PD + "(d)/PD298(e) LATCH branch: 'stop (end)' Mechanical Action 4 (diag_c138_5_facts.md, "
        "OpStopModeB_v0) -> Local of the non-latch indicator StopAll (U4); local of a plan-made indicator = P3b-2 p3b_lr_rotpos "
        "(v8 p4_lr_bufdiff11 form); local_read {0}")
LOC = {"p4_lr_stop12": "on a base While body ran (plan_l2a3_in.json:16)", "p4_lr_stop_w1": "in new W1.body = v8 LRS1 route; PD293(d) W1 exit"}
STOPALL = {"op": "create", "id": "p4_i_stopall", "class": "ControlTerminal", "diagram": 639, "as": "IS1", "label": "StopAll",
           "indicator": True, "born_on": {"uid": 642, "term_uid": 642},
           "why": ("ROUTE create indicator_nested | PRECEDENT | " + PD + "(d)/PD298(e) LATCH branch: ONE writer = #637 body 639 owning "
                   "'stop (end)' CT t642 (w6929 -> #11639); non-latch Boolean indicator StopAll born on t642 (branch), written every "
                   "iteration; create_indicator_nested on a node terminal ran (stage_d1_l2a3.log:47 #9647.t0); on a CT terminal "
                   "UNMEASURED; CT by own uid PD303(a)")}
INSERT_BEFORE = {"p4_lr_stop12": STOPALL}
MOD_IDS = sorted(list(KMX) + list(TUN) + list(LOC))


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def modify(a):
    a = copy.deepcopy(a)
    i = a["id"]
    if i in KMX:
        a["why"] = KWHY + KMX[i]
    elif i in TUN:
        a["why"] = TWHY.format(TUN[i][0], "TI-" + TUN[i][1])
    elif i in LOC:
        a["label"] = "StopAll"
        a["terminals"] = [{"name": "StopAll", "is_source": True, "term_class": "Terminal"}]
        a["why"] = LWHY.format(LOC[i])
    return a


def main():
    G = {"pass": 0, "fail": 0, "first": None}

    def gate(ok, label, detail=""):
        G["pass" if ok else "fail"] += 1
        if not ok and G["first"] is None:
            G["first"] = label
        print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(detail)[:400]))

    for p, w in WANT.items():
        gate(md5(p) == w, "input md5 " + os.path.basename(p), md5(p))
    v8 = json.load(open(V8, encoding="utf-8"))
    A8 = v8["actions"]
    ids8 = [a["id"] for a in A8]
    gate(all(k in ids8 for k in MOD_IDS + list(INSERT_BEFORE)), "anchor ids in v8")
    gate(STOPALL["as"] not in {a.get("as") for a in A8} and STOPALL["id"] not in ids8, "new as/id unused in v8")
    A9 = []
    for a in A8:
        if a["id"] in INSERT_BEFORE:
            A9.append(copy.deepcopy(INSERT_BEFORE[a["id"]]))
        A9.append(modify(a))
    long_ = [(a["id"], k, len(v)) for a in A9 for k, v in a.items() if isinstance(v, str) and len(v) > WHY_MAX]
    gate(not long_, "every action string <= 400 chars (stageplan/1)", long_)
    if long_:
        print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])))
        return 1
    v9 = copy.deepcopy(v8)
    v9["actions"] = A9
    with open(V9, "w", encoding="utf-8") as f:
        json.dump(v9, f, indent=1, default=str)
    print("v8 actions", len(A8), "v9 actions", len(A9), "v9 md5", md5(V9))
    okv, whyv = protocol.validate_obj(json.load(open(V9, encoding="utf-8")))
    gate(okv, "v9 validates against stageplan/1 (protocol.validate_obj)", whyv)
    gate(len(A9) == 182, "v9 = 181 + 1 = 182 actions", len(A9))
    d8, d9 = dict((a["id"], a) for a in A8), dict((a["id"], a) for a in A9)
    removed = [i for i in ids8 if i not in d9]
    added = [a["id"] for a in A9 if a["id"] not in d8]
    modified = [i for i in ids8 if i in d9 and d8[i] != d9[i]]
    print("DIFF removed", removed)
    print("DIFF added", [(A9.index(d9[i]) + 1, i, d9[i]["op"]) for i in added])
    print("DIFF modified", modified)
    keys = {}
    for i in modified:
        keys[i] = sorted(k for k in set(d8[i]) | set(d9[i]) if d8[i].get(k) != d9[i].get(k))
        print("  MOD", i, "keys", keys[i])
    gate(not removed and added == ["p4_i_stopall"], "removed none, added exactly p4_i_stopall", (removed, added))
    gate(sorted(modified) == MOD_IDS, "modified exactly the 7", modified)
    gate(all(keys[i] == (["label", "terminals", "why"] if i in LOC else ["why"]) for i in modified),
         "changed keys: why (all), label+terminals (2 locals)", keys)
    same8 = [i for i in ids8 if i not in modified]
    gate([i for i in [a["id"] for a in A9] if i in same8] == same8, "unchanged v8 actions keep v8 order", len(same8))
    top = sorted(x for x in set(v8) | set(v9) if x != "actions" and v8.get(x) != v9.get(x))
    gate(not top, "no top-level key changed", top)
    gate(all(d9[i]["donor"] == {"donor": "C:\\Program Files\\National Instruments\\LabVIEW 2026\\user.lib\\claudeDev\\DonorI32Max_v0.vi",
                                "uid": 0} for i in KMX), "KMX1/KMX2 donor DonorI32Max_v0 uid 0 SENTINEL kept")

    rg = {"schema_note": ("card 138-P1 (PD312(c)(d)): RECIPE NOTES for the v9 launch recipe - not plan rows (stageplan/1 has no "
                          "index-mode op). Form = PD235(c): stage_d1_qrt_pool.py:46-47, plan_qrt_pool_pred.json:18."),
          "plan": {"path": "tools/bench/plan_ring_p4_v9.json", "md5": md5(V9)},
          "index_mode_gates": [
              {"gate": "TI-" + TUN[i][1], "action_id": i, "as": TUN[i][1], "indexing": True, "want": 1,
               "call": "im, e_ = s.safe('TI-{0} index_mode_fix', lambda: be.index_mode_fix(R('{0}'), True), None)".format(TUN[i][1]),
               "pass": "im == 1 and not e_", "fatal": True, "when": "after Executor.run returns, before any save",
               "why": "Executor.run calls index_mode_fix for a tunnel only inside `if lost:` (stagexec.py:2104-2109); "
                      "LVBackend.index_mode_fix sets + reads back IndexMode (stagexec.py:2970-2979)"} for i in TUN],
          "donor_bind": {"ids": sorted(KMX), "donor": "claudeDev\\DonorI32Max_v0.vi", "value": 2147483647, "type": "I32",
                         "uid": 0, "rule": "uid 0 = SENTINEL; bind the donor object's uid from card 138-6's read-back record before "
                                           "the v9 launch; a launch with uid 0 is not allowed (PD312(c),(e))"},
          "stop_route": {"actions": ["p4_i_stopall", "p4_lr_stop12", "p4_lr_stop_w1"], "branch": "PD298(e) LATCH",
                         "evidence": "tools/bench/diag_c138_5_facts.md ('stop (end)' #7 Mechanical Action 4)",
                         "precondition": "PD312(d): latch reading of 4 confirmed by 138-6's scratch latch-local test before launch"}}
    with open(GATES, "w", encoding="utf-8") as f:
        json.dump(rg, f, indent=1)
    print("GATES file", GATES, md5(GATES))

    meta = json.load(open(META, encoding="utf-8"))
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
    # the same fill-ins as prep_c138_4_mkv8.py:190-196 (v6..v8 ids absent from the v3 meta)
    for x, t, w in (("p4_x_fd", "p4_t_fd", "p4_w_fd_in"), ("p4_x_dt", "p4_t_dt", "p4_w_dt_in")):
        stepof[t] = stepof[w] = stepof.get(x)
    for n in ["p4_rbR_dw", "p4_rbR_re0", "p4_rbR_sel", "p4_rbR_lr", "p4_rbR_t", "p4_rbR_f", "p4_rbR_s", "p4_rbR_out"]:
        stepof[n] = stepof.get("p4_dec_reseed")
    for k, ids in (("p4_gt_last", ["p4_f_min"]), ("p4_k_max", ["p4_k_max_found"]),
                   ("p4_w_num_sel", ["p4_t_fnum", "p4_t_fnum_in", "p4_t_fnum_out"]),
                   ("p4_w_gt_sel", ["p4_t_fgt", "p4_t_fgt_in", "p4_t_fgt_out", "p4_w_max_sel"]),
                   ("p4_w_sel_amm", ["p4_t_fsel", "p4_t_fsel_in", "p4_t_fsel_out"]), ("p4_lr_stop12", ["p4_i_stopall"])):
        for x in ids:
            stepof[x] = stepof.get(k)
    cnt, nometa = {}, []
    for a in A9:
        s = stepof.get(a["id"])
        if s is None:
            nometa.append(a["id"])
        cnt[s] = cnt.get(s, 0) + 1
    print("v9 ACTIONS per meta step", dict(sorted(cnt.items(), key=str)), "no meta step", nometa)

    import stagexec as SX
    try:
        ops = SX.compile_plan(v9)
        per, kinds = {}, {}
        for o in ops:
            s = stepof.get(A9[o["acts"][0] - 1]["id"])
            per[s] = per.get(s, 0) + 1
            kk = o["kind"] + ("/" + o["variant"] if o.get("variant") else "")
            kinds[kk] = kinds.get(kk, 0) + 1
        print("COMPILE v9 OK ops={0} per meta step {1}".format(len(ops), dict(sorted(per.items(), key=str))))
        print("COMPILE kinds", dict(sorted(kinds.items())))
        for o in ops:
            if any(A9[n - 1]["id"] in set(added) | set(modified) for n in o["acts"]):
                print("COMPILE NEW/MOD", o["kind"], o.get("route") or o.get("variant"), [A9[n - 1]["id"] for n in o["acts"]])
        gate(len(ops) == 164, "compile ops == 164 (v8 163 + 1)", len(ops))
        gate(max(per.values()) <= 42, "ops per meta step <= ~40 (re-cut above 42, PD306(c))", per)
    except SX.ExecStop as e:
        gate(False, "compile_plan(v9)", e)

    import stagesim as SS
    os.makedirs(SIMDIR, exist_ok=True)
    S = None
    try:
        S = SS.simulate(V9, GRAPH, out_root=SIMDIR, plan_out_dir=SIMDIR)
    except Exception as e:                                             # report, no retry
        print("SIM EXCEPTION", type(e).__name__, e)
        traceback.print_exc()
    gate(S is not None, "simulate returned")
    if S is not None:
        steps = S.get("steps") or []
        last = steps[-1] if steps else {}
        errs = [s for s in steps if s.get("error")]
        print("SIM final={0} failed={1} steps={2} last={3} {4} error={5}".format(
            S.get("final"), S.get("failed"), len(steps), last.get("n"), last.get("id"), str(last.get("error"))[:600]))
        print("SIM first stop", (errs[0].get("n"), errs[0].get("id"), str(errs[0].get("error"))[:600]) if errs else "none (END)")
        v8s = json.load(open(V8SUM, encoding="utf-8"))
        c8 = dict((s.get("id"), s.get("cdiff_rows")) for s in (v8s.get("steps") or []))
        dif = []
        for s in steps:
            if s.get("id") in set(added) | set(modified):
                print("STEP", s.get("n"), s.get("op"), s.get("id"), "error" if s.get("error") else "ok",
                      str(s.get("error") or s.get("effect_summary"))[:300], "cdiff", s.get("cdiff_rows"))
            if s.get("id") in c8 and c8[s.get("id")] != s.get("cdiff_rows"):
                dif.append((s.get("n"), s.get("id"), c8[s.get("id")], s.get("cdiff_rows")))
        print("PER-STEP cdiff count differs from v8 at", len(dif), "steps; first 12", dif[:12], "(v8 summary has steps:", bool(c8), ")")
        gate(not errs and len(steps) == len(A9) + 1, "replay END (base + 182 steps, no error)", len(steps))
        end = S.get("end_cdiff_rows") or []
        v8end = set(v8s.get("end_cdiff_rows") or [])
        print("END cdiff rows", len(end), "open_rows_match", S.get("open_rows_match"),
              "classed ok", (S.get("open_rows_classed") or {}).get("ok"), "first_divergent", S.get("first_divergent"))
        print("CDIFF only in v9", sorted(set(end) - v8end), "only in v8", sorted(v8end - set(end)))
        gate(set(end) == v8end and len(v8end) == 24, "end cdiff rows == v8's 24", sorted(set(end) ^ v8end))
        print("SIM plan_out", S.get("plan_out"), "candidates", S.get("n_candidates"), "undecided", S.get("undecided"))
    gate(md5(V8) == WANT[V8], "v8 not written", md5(V8))
    print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"],
                                                    [{"path": "tools/bench/plan_ring_p4_v9.json", "md5": md5(V9)},
                                                     {"path": "tools/bench/plan_ring_p4_v9_recipe_gates.json", "md5": md5(GATES)}])))
    return 0 if not G["fail"] else 1


if __name__ == "__main__":
    sys.exit(main())
