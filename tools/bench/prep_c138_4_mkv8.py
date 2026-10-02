r"""prep_c138_4_mkv8 - card 138-4 (offline, no LabVIEW): plan_ring_p4_v8.json = plan_ring_p4_v7.json (01ab0893) with the
smallest-`Num > last` group re-cut per PD311(b) (docs/d1/ring-p4.md:233-237) and the Select output name per PD311(d); then
stagesim replay of v8 on graph_ring_p3b2b_20261002_133824.json (50595c62) and stagexec.compile_plan(v8).

Prior art checked: tools/bench/prep_c137_6_mkv7.py (v6 -> v7 maker: meta step walk, simulate/compile calls - copied) and
tools/bench/prep_c138_1_replay.py (replay + compile report - copied). Shapes copied: For inside a plan-made While +
explicit indexing / non-indexing tunnel groups = tools/bench/sim/disp/plan_disp.json:36-43,425-468 (r2_dlf, t_ring, t_base);
const_donor create with one unnamed source = v7 p4_k_disc (KD1). stagesim.simulate / stagexec.compile_plan used unchanged.

DESIGN of the re-cut (PD311(b)); one deviation from the PD's wording, forced by compile_plan, reported under OPEN:
  - `Greater?` GT1 STAYS on W1's body on the ARRAYS (v7 p4_gt_last unchanged: x = Num array, y = last) - MEASURED legal
    (diag_c137_7_types.log:220-224: x Array1D<I32>, y I32, out Array1D<Boolean>). Putting it inside the For needs `last`
    through a SECOND tunnel TL1.inner -> For; compile_plan's tunnel group (stagexec.py:685-694) needs each tunnel's out-wire
    right after it, and TL1.inner's only sink would be that later tunnel's outer face (undefined symbol) - not expressible.
  - NEW ForLoop FMN1 on W1's body; IN auto-index tunnels TFN1 (Num) and TFB1 (GT1's Boolean array); inside ONE scalar
    Select SW1 (s = b[i], t = Num[i], f = KMX1); OUT auto-index tunnel TFS1 -> AMM1.array (Array Max & Min, min value).
  - MAX = I32 2147483647 by const_donor: KMX1 on the For body (Select.f) and KMX2 on W1's body (LT1.y, was a branch of KMX1).
    The donor holding that value DOES NOT EXIST in claudeDev - donor uid null, flagged UNMEASURED.
  - removed v7 wires p4_w_num_sel / p4_w_gt_sel / p4_w_sel_amm (each replaced by a tunnel group); p4_w_max_lt src -> KMX2.

PREDICTION CONTRACT:
  - inputs md5 as the card; v8 = 172 - 3 + 2 (FMN1, KMX2) + 9 (3 tunnel groups) + 1 (KMX1 -> Select.f) = 181 actions;
  - modified ids exactly {p4_sel_mask, p4_k_max, p4_w_max_lt}; every other v7 action identical and in v7's order;
    no top-level key changed; 's? t: f' occurrences 0 in v8 (v7 has 0 too - PD311(d) needs no edit in v7's text);
  - compile_plan(v8) compiles; the 3 new groups compile as kind 'tunnel'; ops per meta step <= ~40 (reported);
  - replay: the 13 new / changed actions replay ok; last step, final, END or first stop, end cdiff rows reported as measured.
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
V7 = os.path.join(B, "plan_ring_p4_v7.json")
V8 = os.path.join(B, "plan_ring_p4_v8.json")
META = os.path.join(B, "plan_ring_p4_v3_meta.json")
GRAPH = os.path.join(B, "graph_ring_p3b2b_20261002_133824.json")
V7SUM = os.path.join(B, "sim", "c138_1_v7", "ring_p4_v3", "summary.json")
SIMDIR = os.path.join(B, "sim", "c138_4_v8")
WANT = {V7: "01ab0893f3a9440e02bbc180bc467bdf", GRAPH: "50595c62d0332a94bf066538cf20c0ae"}
CD = "C:\\Program Files\\National Instruments\\LabVIEW 2026\\user.lib\\claudeDev\\"
DMAX = {"donor": CD + "DonorI32Max_v0.vi", "uid": 0}   # SENTINEL 0: the VI is not on disk; stageplan/1 needs an integer uid
PD = "PD311(b)"
KWHY = ("ROUTE create | UNMEASURED | " + PD + " I32 2147483647 by const_donor (I32 type MEASURED diag_c137_7_types.log:212-216); "
        "no claudeDev donor holds it (#134 U32 max, #248 I32 0, #249 I32 -1; docs/NAMES.md:1384): donor UNBUILT, uid 0 sentinel")
TWHY = ("ROUTE tunnel | PRECEDENT | " + PD + " {0}: form plan_disp.json:425-468; For in a plan-made While ran "
        "stage_d1_disp_r3.log:62-63; indexing tunnel on a plan-made For never run; IndexMode set only if lost faces "
        "(stagexec.py:2104-2109): UNMEASURED")
WHY_MAX = 400                     # stageplan/1 string limit (runs 1-2 of this maker stopped on goal / why > 400)
KTERM = [{"name": "", "is_source": True, "term_class": "Terminal"}]
ADD_AFTER = {   # new actions inserted right after the v7 id
    "p4_gt_last": [
        {"op": "create", "id": "p4_f_min", "class": "ForLoop", "diagram": "new:W1.body", "as": "FMN1",
         "why": "ROUTE create | PRECEDENT | " + PD + " For loop on W1's body: loop_in('for') OpForLoopIn_v0 (stagexec.py:204); "
                "For in a plan-made While body = plan_disp.json:36-43 r2_dlf, created stage_d1_disp_r3.log:62-63 (ForLoop +1); "
                "N unwired (count = auto-indexed input length 20) UNMEASURED"}],
    "p4_k_max": [
        {"op": "create", "id": "p4_k_max_found", "class": "DigitalNumericConstant", "diagram": "new:W1.body", "as": "KMX2",
         "prim": "const_donor", "donor": dict(DMAX), "terminals": copy.deepcopy(KTERM),
         "why": KWHY + "; KMX2 = LT1.y (found = min < MAX), was a branch of KMX1 (now inside the For)"}],
}
REPLACE = {     # v7 id -> the actions replacing it
    "p4_w_num_sel": [
        {"op": "tunnel", "id": "p4_t_fnum", "loop": "new:FMN1", "body": "new:FMN1.body", "parent": "new:W1.body", "dir": "in",
         "as": "TFN1", "indexing": True, "why": TWHY.format("Num array -> Num[i] (auto-index IN)")},
        {"op": "wire", "id": "p4_t_fnum_in", "src": "new:LRN4.value", "dst": "new:TFN1.outer",
         "why": "ROUTE in_group | PRECEDENT | " + PD + " Num local -> For IN tunnel (branch: LRN4 also feeds GT1.x)"},
        {"op": "wire", "id": "p4_t_fnum_out", "src": "new:TFN1.inner", "dst": "new:SW1.t",
         "why": "ROUTE in_group | PRECEDENT | " + PD + " Num[i] -> Select t (scalar I32)"}],
    "p4_w_gt_sel": [
        {"op": "tunnel", "id": "p4_t_fgt", "loop": "new:FMN1", "body": "new:FMN1.body", "parent": "new:W1.body", "dir": "in",
         "as": "TFB1", "indexing": True, "why": TWHY.format("Boolean array Num > last -> b[i] (auto-index IN)")},
        {"op": "wire", "id": "p4_t_fgt_in", "src": "new:GT1.x > y?", "dst": "new:TFB1.outer",
         "why": "ROUTE in_group | PRECEDENT | " + PD + " GT1 Array1D<Boolean> (diag_c137_7_types.log:224) -> For IN tunnel"},
        {"op": "wire", "id": "p4_t_fgt_out", "src": "new:TFB1.inner", "dst": "new:SW1.s",
         "why": "ROUTE in_group | PRECEDENT | " + PD + "(a) SCALAR Boolean b[i] -> Select s (scalar s unbroken C5, "
                "diag_c137_7_types.log:171-189)"},
        {"op": "wire", "id": "p4_w_max_sel", "src": "new:KMX1.value", "dst": "new:SW1.f",
         "why": "ROUTE connect | PRECEDENT | " + PD + " MAX -> Select f, same For body (const route 188(c), stagexec.py:1330-1338: "
                "the constant by report_all(class), PD307(a) MEASURED findable that way)"}],
    "p4_w_sel_amm": [
        {"op": "tunnel", "id": "p4_t_fsel", "loop": "new:FMN1", "body": "new:FMN1.body", "parent": "new:W1.body", "dir": "out",
         "as": "TFS1", "indexing": True, "why": TWHY.format("Select out -> I32 array (auto-index OUT)")},
        {"op": "wire", "id": "p4_t_fsel_in", "src": "new:SW1.s? t:f", "dst": "new:TFS1.inner",
         "why": "ROUTE in_group | PRECEDENT | " + PD + "(d) Select 's? t:f' (diag_c128_2_donors.log:62) -> For OUT tunnel"},
        {"op": "wire", "id": "p4_t_fsel_out", "src": "new:TFS1.outer", "dst": "new:AMM1.array",
         "why": "ROUTE in_group | PRECEDENT | " + PD + " I32 array -> Array Max & Min (min value = smallest Num > last, MAX when none)"}],
}


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def modify(a):
    a = copy.deepcopy(a)
    if a["id"] == "p4_sel_mask":
        a["diagram"] = "new:FMN1.body"
        a["why"] = ("ROUTE create | MEASURED | vilib donor DonorErrSel_MergeErrors #529 Select, SCALAR s (P3b-1 p3b_sel launched; "
                    "diag_c128_2_donors.log:61-63); " + PD + " s = b[i] scalar (PD311(a)); created inside a plan-made For body never run")
    elif a["id"] == "p4_k_max":
        a = {"op": "create", "id": "p4_k_max", "class": "DigitalNumericConstant", "diagram": "new:FMN1.body", "as": "KMX1",
             "prim": "const_donor", "donor": dict(DMAX), "terminals": copy.deepcopy(KTERM),
             "why": KWHY + "; KMX1 = Select.f inside the For (replaces v7 const_row on SW1.f, measured DBL)"}
    elif a["id"] == "p4_w_max_lt":
        a["src"] = "new:KMX2.value"
        a["why"] = "ROUTE connect | PRECEDENT | " + PD + " found = min < MAX: KMX2 (W1 body) -> LT1.y (const route 188(c))"
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
    v7 = json.load(open(V7, encoding="utf-8"))
    A7 = v7["actions"]
    ids7 = [a["id"] for a in A7]
    new = [x for v in list(ADD_AFTER.values()) + list(REPLACE.values()) for x in v]
    used = {a.get("as") for a in A7}
    gate(not ({x.get("as") for x in new if x.get("as")} & used) and not ({x["id"] for x in new} & set(ids7)),
         "new as/ids unused in v7", sorted({x.get("as") for x in new if x.get("as")} & used))
    gate(all(k in ids7 for k in list(ADD_AFTER) + list(REPLACE) + ["p4_sel_mask", "p4_k_max", "p4_w_max_lt"]), "anchor ids in v7")
    A8 = []
    for a in A7:
        if a["id"] in REPLACE:
            A8 += copy.deepcopy(REPLACE[a["id"]])
            continue
        A8.append(modify(a))
        A8 += copy.deepcopy(ADD_AFTER.get(a["id"], []))
    long_ = [(a["id"], k, len(v)) for a in A8 for k, v in a.items() if isinstance(v, str) and len(v) > WHY_MAX]
    gate(not long_, "every action string <= 400 chars (stageplan/1)", long_)
    if long_:
        print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])))
        return 1
    v8 = copy.deepcopy(v7)
    v8["actions"] = A8
    # goal kept identical: stageplan/1 caps it at 400 chars and v7's is already near it (first run: 419 > 400)
    with open(V8, "w", encoding="utf-8") as f:
        json.dump(v8, f, indent=1, default=str)
    print("v7 actions", len(A7), "v8 actions", len(A8), "v8 md5", md5(V8))
    okv, whyv = protocol.validate_obj(json.load(open(V8, encoding="utf-8")))
    gate(okv, "v8 validates against stageplan/1 (protocol.validate_obj, as stagesim.py:2380)", whyv)
    gate(len(A8) == 181, "v8 = 172 - 3 + 2 + 9 + 1 = 181 actions", len(A8))
    d7, d8 = dict((a["id"], a) for a in A7), dict((a["id"], a) for a in A8)
    removed = [i for i in ids7 if i not in d8]
    added = [a["id"] for a in A8 if a["id"] not in d7]
    modified = [i for i in ids7 if i in d8 and d7[i] != d8[i]]
    print("DIFF removed", removed)
    print("DIFF added", [(A8.index(d8[i]) + 1, i, d8[i]["op"]) for i in added])
    print("DIFF modified", modified)
    for i in modified:
        print("  MOD", i, "keys", sorted(k for k in set(d7[i]) | set(d8[i]) if d7[i].get(k) != d8[i].get(k)))
    gate(sorted(removed) == sorted(REPLACE), "removed = the 3 replaced wires", removed)
    gate(sorted(modified) == ["p4_k_max", "p4_sel_mask", "p4_w_max_lt"], "modified exactly 3", modified)
    same7 = [i for i in ids7 if i in d8 and i not in modified]
    gate([i for i in [a["id"] for a in A8] if i in same7] == same7, "unchanged v7 actions keep v7 order", len(same7))
    top = sorted(x for x in set(v7) | set(v8) if x != "actions" and v7.get(x) != v8.get(x))
    gate(not top, "no top-level key changed", top)
    t8 = json.dumps(v8)
    gate(t8.count("s? t: f") == 0, "'s? t: f' occurrences in v8 = 0 (v7: {0})".format(json.dumps(v7).count("s? t: f")),
         t8.count("s? t:f"))

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
    for x, t, w in (("p4_x_fd", "p4_t_fd", "p4_w_fd_in"), ("p4_x_dt", "p4_t_dt", "p4_w_dt_in")):
        stepof[t] = stepof[w] = stepof.get(x)
    for n in ["p4_rbR_dw", "p4_rbR_re0", "p4_rbR_sel", "p4_rbR_lr", "p4_rbR_t", "p4_rbR_f", "p4_rbR_s", "p4_rbR_out"]:
        stepof[n] = stepof.get("p4_dec_reseed")
    for k, v in list(ADD_AFTER.items()) + list(REPLACE.items()):
        for x in v:
            stepof[x["id"]] = stepof.get(k)
    print("STEP of group anchors", {k: stepof.get(k) for k in list(ADD_AFTER) + list(REPLACE)})
    cnt, nometa = {}, []
    for a in A8:
        s = stepof.get(a["id"])
        if s is None:
            nometa.append(a["id"])
        cnt[s] = cnt.get(s, 0) + 1
    print("v8 ACTIONS per meta step", dict(sorted(cnt.items(), key=str)), "no meta step", nometa)

    import stagexec as SX
    try:
        ops = SX.compile_plan(v8)
        per, kinds = {}, {}
        for o in ops:
            s = stepof.get(A8[o["acts"][0] - 1]["id"])
            per[s] = per.get(s, 0) + 1
            kk = o["kind"] + ("/" + o["variant"] if o.get("variant") else "")
            kinds[kk] = kinds.get(kk, 0) + 1
        print("COMPILE v8 OK ops={0} per meta step {1}".format(len(ops), dict(sorted(per.items(), key=str))))
        print("COMPILE kinds", dict(sorted(kinds.items())))
        newops = [(o["kind"], o.get("route") or o.get("variant"), [A8[n - 1]["id"] for n in o["acts"]]) for o in ops
                  if any(A8[n - 1]["id"] in set(added) | set(modified) for n in o["acts"])]
        for x in newops:
            print("COMPILE NEW", x)
        gate(sum(1 for o in ops if o["kind"] == "tunnel" and o.get("tunnel") in ("new:TFN1", "new:TFB1", "new:TFS1")) == 3,
             "3 new tunnel groups compile as kind tunnel")
        gate(max(per.values()) <= 42, "ops per meta step <= ~40 (re-cut above 42, PD306(c))", per)
    except SX.ExecStop as e:
        gate(False, "compile_plan(v8)", e)

    import stagesim as SS
    os.makedirs(SIMDIR, exist_ok=True)
    S = None
    try:
        S = SS.simulate(V8, GRAPH, out_root=SIMDIR, plan_out_dir=SIMDIR)
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
        for s in steps:
            if s.get("id") in set(added) | set(modified):
                print("STEP", s.get("n"), s.get("op"), s.get("id"), "error" if s.get("error") else "ok",
                      str(s.get("error") or s.get("effect_summary"))[:300], "cdiff", s.get("cdiff_rows"))
        gate(not errs and len(steps) == len(A8) + 1, "replay END (base + 181 steps, no error)", len(steps))
        end = S.get("end_cdiff_rows") or []
        orows = set((int(n), t) for n, t in (S.get("open_rows") or []))
        v7end = set(json.load(open(V7SUM, encoding="utf-8")).get("end_cdiff_rows") or [])
        print("END cdiff rows", len(end), "open_rows", len(orows), "open_rows_match", S.get("open_rows_match"),
              "classed ok", (S.get("open_rows_classed") or {}).get("ok"), "first_divergent", S.get("first_divergent"))
        for r in end:
            n, _c, t, _k = r.split("|")
            print("  CDIFF {0:<45} open_row={1} in_v7_end={2}".format(r, (int(n), t) in orows, r in v7end))
        print("CDIFF only in v8", sorted(set(end) - v7end), "only in v7", sorted(v7end - set(end)))
        gate(set(end) == v7end, "end cdiff rows == v7's 24 (no new row from the re-cut)", sorted(set(end) ^ v7end))
        print("SIM plan_out", S.get("plan_out"), "candidates", S.get("n_candidates"), "undecided", S.get("undecided"))
    gate(md5(V7) == WANT[V7], "v7 not written", md5(V7))
    print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"],
                                                    [{"path": "tools/bench/plan_ring_p4_v8.json", "md5": md5(V8)}])))
    return 0 if not G["fail"] else 1


if __name__ == "__main__":
    sys.exit(main())
