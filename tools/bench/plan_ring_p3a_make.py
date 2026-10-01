r"""plan_ring_p3a_make - card 123-8 STEP 2 (offline, no LabVIEW): the RING P3a plan (PD246(c)(d), PD247(a)(b)(d), PD248(a)(d)) on the
REAL P2b graph graph_ring_p2b_20261001_154542.json (diag_c123_graph_p2b.log, 14/0; BufNum t6897 canon I32 -> prev-BufNum init =
DonorRingConst_v0 #249 I32 -1, PD246(c) A3). Rows (brief_123-8.md step 2), all in While #637 (body #639, owner FS1 frame #686):
Wait (ms) + const 1; prev-BufNum SR + init const + BufNum -> R; Equal? x <- BufNum, y <- SR L; case_wired <- Equal?; counter SR + I32 0
init; case tunnel in (count) -> Increment (False) -> case tunnel out -> counter R; True frame passes the count through; Q&R x <- count,
y <- I32 20 constant on the False frame. PRIOR ART: plan_ring_p2b_make.py (graph-derived plan + pred), plan_qrt_pool_in.json ($work
donor creates, tunnel groups), stagexec routes const_sr / case_wired / primitive / const_on_term. No new op.
PREDICTION -> plan_ring_p3a_in.json (<= 25 actions) + plan_ring_p3a_pred.json; stagesim FINAL is a separate step (stagesim simulate).
    py tools/bgrun.py --material --max-min 3 --log tools/bench/plan_ring_p3a_make.log -- py -u tools/bench/plan_ring_p3a_make.py"""
import hashlib, json, os, sys                                                      # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import protocol as P  # noqa: E402
B = os.path.dirname(os.path.abspath(__file__))
J = lambda fn: json.load(open(os.path.join(B, fn), encoding="utf-8"))  # noqa: E731
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()  # noqa: E731
GF = "graph_ring_p2b_20261001_154542.json"
G, P2B, OL = J(GF), J("plan_ring_p2b.json"), J("facts_c100_oplabels.json")
CD = "C:\\Program Files\\National Instruments\\LabVIEW 2026\\user.lib\\claudeDev\\"
LOOP, BODY, OWN, BN, BNW = 637, 639, 686, {"uid": 6810, "term": "current image number"}, 3747
ok = []


def gate(name, c, det):
    ok.append((name, bool(c)))
    print("{0}  {1}  {2}".format("PASS" if c else "FAIL", name, json.dumps(det, default=str)[:900]), flush=True)


T = G["terminals"]
gmd5 = md5(os.path.join(B, GF))
gate("M0 graph = the saved P2b bed (md5 652b1447), BufNum canon I32", G["md5"] == "652b1447ebbda761a7d5ba36455a0fa1"
     and (G["bufnum_type"].get("types") or {}).get("canon") == "I32", (gmd5, G["md5"]))
gate("M1 #639 body of While #637 on FS1 frame #686", G["owners"].get(str(BODY)) == ["WhileLoop", LOOP] and G["owners"].get(str(OWN), [""])[0] == "FlatSequenceFrame",
     (G["owners"].get(str(BODY)), G["owners"].get(str(OWN))))
bn = [r for r in T if r["owner_uid"] == BN["uid"] and r["term_name"] == BN["term"] and r["is_source"]]
gate("M2 BufNum = ONE source on w{0}".format(BNW), len(bn) == 1 and bn[0]["wire_uid"] == BNW, bn)
def _find(d, k):
    if isinstance(d, dict):
        if k in d and isinstance(d[k], dict) and "donor" in d[k]:
            return d[k]
        for v in d.values():
            r = _find(v, k)
            if r:
                return r
    return None


WD = _find(OL, "Wait (ms)")
gate("M3 Wait (ms) donor file md5 == record", os.path.exists(WD["donor"]) and md5(WD["donor"]) == WD["md5"], WD)
DRC, DSI = CD + "DonorRingConst_v0.vi", CD + "DonorSRInit_v0.vi"
gate("M4 DonorRingConst_v0 d8dc3013, DonorSRInit_v0 8b1a5afe", md5(DRC) == "d8dc30136c197bef836cd4622bbce61d" and md5(DSI) == "8b1a5afe59b035cd088735bdba6368dd",
     (md5(DRC), md5(DSI)))
t = lambda n, s: {"name": n, "is_source": s}                                       # noqa: E731
A = [
    {"op": "create", "id": "p3a_wait", "class": "Function", "diagram": BODY, "as": "WT1","pos": [3200, 60], "prim": "Wait (ms)",
     "donor": {"donor": WD["donor"], "uid": WD["uid"]}, "terminals": [t("milliseconds to wait", False), t("millisecond timer value", True)],
     "why": "PD246(d): Wait (ms) 1 in loop 1.1, no data dependency on the frame path (donor facts_c100_oplabels.json:266-273)"},
    {"op": "create", "id": "p3a_wait_k", "class": "DigitalNumericConstant", "diagram": BODY, "as": "WK1", "pos": [3150, 60], "on": "new:WT1.milliseconds to wait",
     "value": 1, "why": "PD246(d): the wait is 1 ms (const_on_term, a node in a While body)"},
    {"op": "add_shift_reg", "id": "p3a_sr_prev", "loop": LOOP, "body": BODY, "parent": OWN, "as": "SP1",
     "why": "PD246(c) A3: previous-BufNum register on #637"},
    {"op": "create", "id": "p3a_k_prev", "class": "DigitalNumericConstant", "diagram": OWN, "as": "KP1","pos": [-200, 400], "prim": "const_donor",
     "donor": {"donor": DRC, "uid": 249}, "terminals": [t("", True)], "why": "PD246(c) A3 / PD247(a): I32 -1 (BufNum is I32, t6897) = DonorRingConst_v0 #249"},
    {"op": "wire", "id": "p3a_w_kprev", "src": "new:KP1.value", "dst": "new:SP1L.outer", "why": "PD247(a): const_sr - register initialised at loop start"},
    {"op": "wire", "id": "p3a_w_bn_r", "src": BN, "dst": "new:SP1R.inner", "why": "PD246(c) A5: the register's right terminal takes BufNum (branch of w3747), outside the case"},
    {"op": "create", "id": "p3a_eq", "class": "Comparison", "diagram": BODY, "as": "EQ1","pos": [3300, 1500], "prim": "Equal?",
     "donor": {"donor": "$work", "uid": 10019}, "terminals": [t("x = y?", True), t("y", False), t("x", False)],
     "why": "PD246(c) A4 / PD247(b): Equal? $work dup of #10019 (Comparison {x = y?, y, x})"},
    {"op": "wire", "id": "p3a_w_bn_x", "src": BN, "dst": "new:EQ1.x", "why": "Equal? x = BufNum (branch of w3747; PD248(b) branch proven, diag_c123_wired.log:51)"},
    {"op": "wire", "id": "p3a_w_prev_y", "src": "new:SP1L.inner", "dst": "new:EQ1.y", "why": "Equal? y = previous BufNum"},
    {"op": "create", "id": "p3a_case", "class": "CaseStructure", "diagram": BODY, "as": "CS1", "selector_as": "SEL1", "pos": [3600, 1450],
     "frames": ["False", "True"], "src": "new:EQ1.x = y?", "why": "PD248(a): case_wired, True = duplicate (empty), False = new frame"},
    {"op": "add_shift_reg", "id": "p3a_sr_cnt", "loop": LOOP, "body": BODY, "parent": OWN, "as": "SC1", "why": "PD246(c) A3 / PD247(d): new-frame counter on #637"},
    {"op": "create", "id": "p3a_k_cnt", "class": "DigitalNumericConstant", "diagram": OWN, "as": "KC1","pos": [-200, 480], "prim": "const_donor",
     "donor": {"donor": DSI, "uid": 248}, "terminals": [t("", True)], "why": "PD247(d): counter I32 0 = DonorSRInit_v0 #248"},
    {"op": "wire", "id": "p3a_w_kcnt", "src": "new:KC1.value", "dst": "new:SC1L.outer", "why": "PD247(a): const_sr"},
    {"op": "tunnel", "id": "p3a_t_in", "loop": "new:CS1", "body": "new:CS1.f0", "parent": BODY, "dir": "in", "as": "TI1", "why": "count into the case (False frame)"},
    {"op": "wire", "id": "p3a_w_cnt_in", "src": "new:SC1L.inner", "dst": "new:TI1.outer", "why": "the register's left value enters the case"},
    {"op": "wire", "id": "p3a_w_cnt_inc", "src": "new:TI1.inner", "dst": "new:INC1.x", "why": "PD246(c) A5: +1 only on a new frame"},
]
A.insert(len(A) - 3,{"op": "create", "id": "p3a_inc", "class": "Function", "diagram": "new:CS1.f0", "as": "INC1", "pos": [60, 60], "prim": "Increment",
                      "donor": {"donor": "$work", "uid": 1978}, "terminals": [t("x+1", True), t("x", False)], "why": "PD247(b): Increment $work dup of #1978"})
A += [
    {"op": "tunnel", "id": "p3a_t_out", "loop": "new:CS1", "body": "new:CS1.f0", "parent": BODY, "dir": "out", "as": "TO1", "why": "count out of the case"},
    {"op": "wire", "id": "p3a_w_inc_out", "src": "new:INC1.x+1", "dst": "new:TO1.inner", "why": "False frame: count + 1"},
    {"op": "wire", "id": "p3a_w_out_r", "src": "new:TO1.outer", "dst": "new:SC1R.inner", "why": "the case output feeds the counter's right terminal"},
    {"op": "wire", "id": "p3a_w_true_pass", "src": {"uid": "new:TI1", "side": "inner", "frame": "new:CS1.f1"}, "dst": {"uid": "new:TO1", "side": "inner", "frame": "new:CS1.f1"},
     "why": "PD246(c) A5: the True (duplicate) frame passes the count straight through"},
    {"op": "create", "id": "p3a_qr", "class": "Function", "diagram": "new:CS1.f0", "as": "QR1", "pos": [60, 160], "prim": "Quotient & Remainder",
     "donor": {"donor": "$work", "uid": 2136}, "terminals": [t("floor(x/y)", True), t("x-y*floor(x/y)", True), t("y", False), t("x", False)],
     "why": "PD247(b): Q&R $work dup of #2136; remainder (i) unconnected until P3b"},
    {"op": "wire", "id": "p3a_w_qr_x", "src": "new:TI1.inner", "dst": "new:QR1.x", "why": "x = the count (left value through the case)"},
    {"op": "create", "id": "p3a_k20", "class": "DigitalNumericConstant", "diagram": "new:CS1.f0", "as": "K20", "pos": [0, 200], "prim": "const_donor",
     "donor": {"donor": CD + "DonorPool_v0.vi", "uid": 214}, "terminals": [t("", True)], "why": "y = I32 20 (DonorPool_v0 #214, plan_qrt_pool_in.json p_i32)"},
    {"op": "wire", "id": "p3a_w_k20", "src": "new:K20.value", "dst": "new:QR1.y", "why": "ring size 20"},
]
gate("M5 actions {0} <= 25".format(len(A)), len(A) <= 25, [a["id"] for a in A])
plan = {"schema": "stageplan/1", "stage": "ring_p3a", "goal": "RING P3a (PD246(c)(d), 247, 248): loop-1.1 control on the SAVED P2b bed",
        "base": {"path": "tools/bench/" + GF, "md5": gmd5}, "context": P2B.get("context", {"s1_key": "D1_s1_copy"}), "actions": A,
        "open_rows": P2B["open_rows"]}
pred = {"schema": "ring-p3a-pred/1", "graph": {"path": "tools/bench/" + GF, "md5": gmd5}, "bed": G["vi"], "bed_md5": G["md5"], "bufnum_canon": "I32",
        "errorlist": {"new_items_predicted": "see plan_ring_p3a_sim.log", "derivation": "pending stagesim"}}
if all(c for _n, c in ok):
    json.dump(plan, open(os.path.join(B, "plan_ring_p3a_in.json"), "w", encoding="utf-8"), indent=1)
    json.dump(pred, open(os.path.join(B, "plan_ring_p3a_pred.json"), "w", encoding="utf-8"), indent=1)
    print("  FACT WROTE plan_ring_p3a_in.json ({0} actions)".format(len(A)), flush=True)
np_, nf = sum(1 for _n, c in ok if c), sum(1 for _n, c in ok if not c)
print(P.result_line(P.make_result(np_, nf, next((n for n, c in ok if not c), None))), flush=True)
sys.exit(1 if nf else 0)
