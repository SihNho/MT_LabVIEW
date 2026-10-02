r"""prep_c140_p1_s02 - card 140-P1 (OFFLINE, no LabVIEW, no COM, never launched). PD320(c)(e): P4 LabVIEW SESSION 2, planned on a
PROVISIONAL base = stagesim's END graph of v14 ops 1..16 (session 1, card 140-2), rebased on the real graph of session 1's in-between
file later (stage_prerun --rebase).
FOUND FIRST (copied, nothing new built): plan_ring_p3b_split_p3b2.py:200-222 (provisional base = a sim end state dumped; b's plan with
base {path, md5, provisional, sim_of}); prep_c139_7_s1.py (pass A row tying / pass B FINAL / pred fields); prep_c140_1_sessions.py:69-72
(table-A X10 window: reads {from, last} | BIND, start 606.1); stagesim.base_state keeps a provisional state's simulator keys and RESETS
sym (stagesim.py:330-338) => a session-2 action naming a session-1 `new:` symbol is rewritten to that symbol's negative uid in the
provisional base ({"uid": -n, "term": t}), the form --rebase re-binds (stage_prerun.py:3584-3594).
CUT RULE (PD320(c)): longest prefix of v14 ops from 17 with table-A X10 peak <= 675 at start 606.1 that splits no `of` pair.
PREDICTION: M0 pins; B1 ops 1..16 replay to their end on the P3b-2b graph, every end row a bed-declared open pair; C1 cut found, peak <= 675,
no `of` crosses either cut; C2 every cross-session ref resolves in the provisional base; SA s02 pass A replays to its end; TIE every end
row tied (s02 action, or step-0 bed/session-1 pair); SB FINAL; X10 compiled s02 at 606.1 == the cut table's peak, <= 675; SP pred written.
    py tools/bgrun.py --material --max-min 10 --log tools/bench/prep_c140_p1_s02.log -- py -u tools/bench/prep_c140_p1_s02.py"""
import collections, copy, hashlib, json, os, sys, traceback                               # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol, stagesim as SS, stagexec as SX, stage_prerun as SPR, census_predict as CPR   # noqa: E402,E401
B = os.path.join(ROOT, "tools", "bench")
SIM = os.path.join(B, "sim")
V14, META14 = os.path.join(B, "plan_ring_p4_v14.json"), os.path.join(B, "plan_ring_p4_v14_meta.json")
GRAPH, BEDPLAN = os.path.join(B, "graph_ring_p3b2b_20261002_133824.json"), os.path.join(B, "plan_ring_p3b2b.json")
EL = os.path.join(B, "errorlist_expected_D1_ring_p3b2b_20261002_130007.json")
D1 = os.path.join(SIM, "ring_p4_v14_ops1_16")
B1IN, PROVB = os.path.join(D1, "plan_ring_p4_v14_ops1_16_in.json"), os.path.join(D1, "base_provisional.json")
DA = os.path.join(SIM, "ring_p4_s02a")
S2AIN, S2IN, S2P, PP = (os.path.join(DA, "plan_ring_p4_s02a_in.json"), os.path.join(B, "plan_ring_p4_s02_in.json"),
                        os.path.join(B, "plan_ring_p4_s02.json"), os.path.join(B, "plan_ring_p4_s02_pred.json"))
WANT = {V14: "22f582715e3d303ea0625fbe98bb590e", META14: "29f6535b1f280b3a33a07dbdeeff8893", GRAPH: "50595c62d0332a94bf066538cf20c0ae",
        os.path.join(B, "diag_c140_1_sessions.json"): "4e2d72c6763df8669d464065935c8b3b",
        os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p4s1.py"): "9f60aeba54c83b850b532c9b9b31ee6e"}
S1N, START, LIM = 16, 606.1, 675.0
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                             # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
G, ARTS = {"pass": 0, "fail": 0, "first": None}, []


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)
    return ok


def done():
    print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
    sys.exit(0 if not G["fail"] else 1)


def tie_rows(S, keep, ok_pairs):
    """prep_c139_7_s1.py:139-160: each end row -> the action at which it first appears and stays; step-0 rows need ok_pairs."""
    ties, untied = {}, []
    for key in S["end_cdiff_rows"]:
        n0 = S["steps"][-1]["n"]
        for s in reversed(S["steps"]):
            if s.get("cdiff_rows") is not None and key in s["cdiff_rows"]:
                n0 = s["n"]
            else:
                break
        p = (SS.V.key_parts(key)[0], SS.V.key_parts(key)[2])
        if n0 >= 1:
            a = keep[n0 - 1]
            ties[key] = {"n": n0, "id": a["id"], "op": a["op"], "class": a.get("class") or a["op"], "pair": p}
        elif p in ok_pairs:
            ties[key] = {"n": 0, "id": ok_pairs[p], "op": "base", "class": "step0-declared", "pair": p}
        else:
            untied.append((key, n0))
    return ties, untied


gate("M0 input md5 == card", all(md5(p) == w for p, w in WANT.items()), dict((os.path.basename(p), md5(p)) for p in WANT))
if G["fail"]:
    done()
v14 = J(V14)
A, M = v14["actions"], SPR.load_memory_model()
OPS = SX.compile_plan(v14)
NOP, KIND = len(OPS), [o["kind"] for o in OPS]
POS = dict((a["id"], k) for k, a in enumerate(A, 1))
OPOF = dict((n, k) for k, o in enumerate(OPS, 1) for n in o["acts"])
TOP = dict((k, copy.deepcopy(v14[k])) for k in ("schema", "context") if k in v14)
# ---- B1: the provisional base = stagesim's end of v14 ops 1..16 on the P3b-2b graph (session 1's actions)
ids1 = [A[n - 1]["id"] for k in range(1, S1N + 1) for n in OPS[k - 1]["acts"]]
keep1 = [copy.deepcopy(a) for a in A if a["id"] in ids1]
os.makedirs(D1, exist_ok=True)
json.dump(dict(TOP, stage="ring_p4_v14_ops1_16", goal="card 140-P1: v14 ops 1..16 (session 1 of P4, PD320(c)) simulated on the P3b-2b graph; "
               "its end state = session 2's provisional base", base={"path": rel(GRAPH), "md5": md5(GRAPH)}, actions=keep1),
          open(B1IN, "w", encoding="utf-8"), indent=1)
try:
    S1 = SS.simulate(B1IN, GRAPH, out_root=SIM, plan_out_dir=D1, log=lambda *x: None, route_check=False)
except Exception as ex:                                                                         # noqa: BLE001
    traceback.print_exc()
    gate("B1 ops 1..16 simulate returned", False, ex)
    done()
bed_pairs = dict(((int(r["node"]), r["term"]), "bed") for r in J(BEDPLAN).get("open_rows") or [])
t1, u1 = tie_rows(S1, keep1, bed_pairs) if S1["failed"] is None else ({}, ["not replayed"])
s01 = os.path.join(B, "plan_ring_p4_s01.json")
same01 = os.path.isfile(s01) and [a["id"] for a in J(s01)["actions"]] == ids1
print("FACT session-1 ids", len(ids1), ids1[0], "..", ids1[-1], "| plan_ring_p4_s01.json present", os.path.isfile(s01), "same ids", same01,
      "md5", md5(s01) if os.path.isfile(s01) else None)
gate("B1 v14 ops 1..16 ({0} actions) replay to their end; every end row tied ({1} rows: own {2}, bed {3})".format(
    len(keep1), len(t1), sum(1 for t in t1.values() if t["n"] >= 1), sum(1 for t in t1.values() if t["n"] == 0)),
     S1["failed"] is None and not u1 and len(keep1) == S1N, {"failed": S1["failed"], "untied": u1[:6]})
if G["fail"]:
    done()
END1 = J(S1["steps"][-1]["file"]["path"])["state"]
json.dump(END1, open(PROVB, "w", encoding="utf-8"), separators=(",", ":"), default=str)
ok_pairs = dict(bed_pairs, **dict((t["pair"], t["id"]) for t in t1.values() if t["n"] >= 1))
# ---- C1: the cut (prep_c140_1_sessions.py:69-72 table A, from op 16)
BIND = set(k for k in range(1, NOP + 1) if KIND[k - 1] in SX.BIND_KINDS)
pk = lambda a, b: round(START + len({a, b} | set(k for k in BIND if a < k <= b)) * float(M["read_mb"]["value"]) + (b - a) * (   # noqa: E731
    float(M["edit_mb"]["value"]) + float(M["other_mb"]["value"])) + float(M["final_read_mb"]["value"]), 1)
b = S1N + 1
while b < NOP and pk(S1N, b + 1) <= LIM:
    b += 1
b_x10 = b
ofp = lambda b_: [(a["id"], a["of"]) for a in A if a.get("of") and (OPOF[POS[a["id"]]] > b_) != (OPOF[POS[a["of"]]] > b_)   # noqa: E731
                  and S1N < min(OPOF[POS[a["id"]]], OPOF[POS[a["of"]]]) <= b_]
while ofp(b) and b > S1N + 1:
    b -= 1
ids2 = [A[n - 1]["id"] for k in range(S1N + 1, b + 1) for n in OPS[k - 1]["acts"]]
cross1 = [(a["id"], a["of"]) for a in A if a.get("of") and (OPOF[POS[a["id"]]] <= S1N) != (OPOF[POS[a["of"]]] <= S1N)]
R2 = len({S1N, b} | set(k for k in BIND if S1N < k <= b))
print("FACT cut table-A from op {0}: x10-longest {1} (peak {2}), next op {3} peak {4}; of-adjusted {5}".format(
    S1N + 1, b_x10, pk(S1N, b_x10), b_x10 + 1, pk(S1N, b_x10 + 1) if b_x10 < NOP else None, b), flush=True)
gate("C1 session 2 = v14 ops {0}..{1} ({2}..{3}), N {4}, R {5}, peak {6} <= {7}; no `of` crosses the s1|s2 or s2|s3 cut".format(
    S1N + 1, b, ids2[0], ids2[-1], b - S1N, R2, pk(S1N, b), LIM), pk(S1N, b) <= LIM and not ofp(b) and not cross1,
     {"of_cross_s2s3": ofp(b), "of_cross_s1s2": cross1, "ops": [(k, KIND[k - 1]) for k in range(S1N + 1, b + 1)]})
if G["fail"]:
    done()
# ---- C2: session-2 actions with session-1 symbols -> provisional negative uids (rebase re-binds them)
made1 = set("new:" + a["as"] for a in keep1 if a.get("as"))
UIDF, ADDRF = ("dest_diagram", "loop", "body", "parent", "uid", "diagram"), ("at", "src", "dst", "born_on", "on")
CROSS, bad = [], []


def sub(a):
    for f in UIDF + ADDRF:
        x = a.get(f)
        s = x.get("uid") if isinstance(x, dict) else x
        if not (isinstance(s, str) and s.startswith("new:")):
            continue
        root = s.split(".")[0]
        if root not in made1 and root[:-1] not in made1:
            continue
        if f in ADDRF and isinstance(x, str):
            sym, term = root, s.split(".", 1)[1]
            u = END1["sym"].get(sym)
            a[f] = {"uid": u, "term": term}
        elif isinstance(x, dict):
            sym, u = s, END1["sym"].get(s)
            a[f]["uid"] = u
        else:
            sym, u = s, END1["sym"].get(s)
            a[f] = u
        CROSS.append({"action": a["id"], "field": f, "symbol": s, "provisional_uid": u})
        (isinstance(u, int) and u < 0) or bad.append((a["id"], f, s, u))
    return a


keep2 = [sub(copy.deepcopy(a)) for a in A if a["id"] in ids2]
for c in CROSS:
    print("CROSS", json.dumps(c), flush=True)
gate("C2 {0} session-2 ref(s) to session-1 symbols, each a negative uid of the provisional base".format(len(CROSS)), not bad, bad)
BASEREF = {"path": rel(PROVB), "md5": md5(PROVB), "provisional": True, "sim_of": {"plan": rel(B1IN), "md5": md5(B1IN)}}
os.makedirs(DA, exist_ok=True)
json.dump(dict(TOP, stage="ring_p4_s02a", goal="card 140-P1 PASS A: P4 session 2 (v14 ops {0}..{1}), no open_rows".format(S1N + 1, b),
               base=BASEREF, actions=keep2), open(S2AIN, "w", encoding="utf-8"), indent=1)
gate("S0 pass-A input validates", *protocol.validate_obj(J(S2AIN)))
try:
    SA = SS.simulate(S2AIN, PROVB, out_root=SIM, plan_out_dir=DA, log=lambda *x: None, route_check=False)
except Exception as ex:                                                                         # noqa: BLE001
    traceback.print_exc()
    gate("SA pass A simulate returned", False, ex)
    done()
gate("SA pass A replays to its end", SA["failed"] is None and SA.get("end_cdiff_rows") is not None, SA["failed"])
if G["fail"]:
    done()
ties, untied = tie_rows(SA, keep2, ok_pairs)
for k in sorted(ties):
    print("TIE", k, json.dumps(dict((x, y) for x, y in ties[k].items() if x != "pair")))
gate("TIE every end row tied to a session-2 action or to a step-0 pair (bed-declared / session-1 action)", not untied,
     {"untied": untied[:10], "own": sum(1 for t in ties.values() if t["n"] >= 1), "step0": sum(1 for t in ties.values() if t["n"] == 0)})
if G["fail"]:
    done()
orows, seen = [], set()
for k in sorted(ties, key=lambda k: (ties[k]["n"], k)):
    t = ties[k]
    if t["pair"] in seen:
        continue
    seen.add(t["pair"])
    why = ("c140-P1 PD320: made by session-2 action {0} (#{1} {2} {3})".format(t["id"], t["n"], t["op"], t["class"]) if t["n"] >= 1 else
           "c140-P1 PD320: open at step 0 of session 2 = {0}".format("declared open row of plan_ring_p3b2b.json" if t["id"] == "bed"
                                                                       else "made by session-1 action " + t["id"]))
    orows.append({"node": int(t["pair"][0]), "term": t["pair"][1], "why": why[:300]})
json.dump(dict(TOP, stage="ring_p4_s02", goal="RING P4 LabVIEW session 2 (card 140-P1, PD320(c)(e)): v14 ops {0}..{1} ({2} actions) on session 1's "
               "SIMULATED end (provisional; stage_prerun --rebase onto session 1's saved in-between file)".format(S1N + 1, b, len(keep2)),
               base=BASEREF, open_rows=orows, actions=keep2), open(S2IN, "w", encoding="utf-8"), indent=1)
SB = SS.simulate(S2IN, PROVB, out_root=SIM, plan_out_dir=B, log=lambda *x: None, route_check=False)
p2 = J(S2P)
gate("SB session-2 plan FINAL on the provisional base, end rows == pass A, open_rows_match ({0} pairs)".format(len(orows)),
     bool(SB["final"]) and p2.get("final") is True and (p2.get("finalized") or {}).get("open_rows_match") is True
     and sorted(SB.get("end_cdiff_rows") or []) == sorted(SA["end_cdiff_rows"]), {"final": SB["final"], "failed": SB["failed"]})
if G["fail"]:
    done()
ops2 = SX.compile_plan(p2)
bind2 = sorted(k for k, o in enumerate(ops2, 1) if o["kind"] in SX.BIND_KINDS)
cps = sorted(set([0, len(ops2)]) | set(bind2))
mp = SPR.x10_model_peak([o["kind"] for o in ops2], cps, model=M, start_mb=START)
gate("X10 compiled session-2 plan at start {0}: N {1} R {2} peak {3} == cut table {4}, <= {5}; kinds == v14 ops {6}..{7}".format(
    START, mp["N"], mp["R"], mp["peak_mb"], pk(S1N, b), LIM, S1N + 1, b), mp["peak_mb"] == pk(S1N, b) and mp["peak_mb"] <= LIM
     and [o["kind"] for o in ops2] == KIND[S1N:b], {"ops2": [o["kind"] for o in ops2], "v14": KIND[S1N:b]})
rep = CPR.predict(p2, {}, J(os.path.join(B, "census_samples.json")))
el = J(EL)
last = J(SB["steps"][-1]["file"]["path"])["state"]
madeu = set(str(u) for s_, u in (last.get("sym") or {}).items())
unw = sorted(set((str(r["owner_uid"]), r.get("term_name")) for r in last["terminals"] if str(r["owner_uid"]) in madeu and not r.get("is_source")
                 and not r.get("wire_uid")))
pv = J(PROVB)
pred = {"schema": "ring-p3b-pred/1", "card": "140-P1", "note": "P4 LabVIEW session 2 (in-between file, D-2026-10-02-02); PROVISIONAL base = session 1's "
        "simulated end - regenerate after stage_prerun --rebase onto session 1's saved file (start = its MEASURED load, PD320(d))",
        "plan": {"path": rel(S2P), "md5": md5(S2P)}, "graph": {"path": rel(PROVB), "md5": md5(PROVB)}, "bed": pv.get("vi"), "bed_md5": pv.get("md5"),
        "census": dict(rep["derived"]), "census_overall": rep["overall"], "census_unpredicted": [p2["actions"][k - 1]["id"] for k in rep["unpredicted"]],
        "ops": [o["kind"] for o in ops2], "cdiff_rows": sorted(SB.get("end_cdiff_rows") or []), "cross_session_refs": CROSS,
        "row_ties": dict((k, dict((x, y) for x, y in t.items() if x != "pair")) for k, t in ties.items()),
        "errorlist": {"bed_total": el.get("total"), "new_items_predicted": 0, "predicted_total": el.get("total"), "alternative_total": el.get("total") + len(unw),
                      "unwired_created_sinks": [list(x) for x in unw], "rule": "stage_d1_ring_p3b1_el.py:6; base = P3b-2b bed EL (session 1's EL not yet "
                      "measured: re-derive at rebase)", "base_file": rel(EL), "checked": False},
        "memory_pred": {"card": "140-P1", "checkpoints": cps, "R": mp["R"], "N": mp["N"], "bind_ops": bind2, "op_kinds": [o["kind"] for o in ops2],
                        "start_mb": START, "start_cite": "PD320(c) planning start 606.1 = bed load 600.2 + op-0 5.9 (memory_model.json); REPLACE by "
                        "session 1 file's measured load + op-0 at rebase (PD320(d))", "peak_mb": mp["peak_mb"], "fail_above_mb": mp["fail_above_mb"],
                        "below_fail": mp["ok"], "model": {"path": rel(SPR.MEMORY_MODEL), "md5": md5(SPR.MEMORY_MODEL)}},
        "summary": (p2.get("finalized") or {}).get("summary")}
json.dump(pred, open(PP, "w", encoding="utf-8"), indent=1)
print("FACT s02 ops", dict(collections.Counter(pred["ops"])), "census", pred["census"], "unpredicted", pred["census_unpredicted"],
      "| EL", el.get("total"), "alt", el.get("total") + len(unw), "| end rows", len(pred["cdiff_rows"]), "open pairs", len(orows), flush=True)
ARTS.extend({"path": rel(p), "md5": md5(p)} for p in (B1IN, PROVB, S2IN, S2P, PP))
gate("SP pred written: ops == compile, each action once", sorted(n for o in ops2 for n in o["acts"]) == list(range(1, len(keep2) + 1)), len(ops2))
done()
