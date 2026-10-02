r"""prep_c141_1_s01 - card 141-1 item 5 (offline, no LabVIEW, no COM). (1) the X10 SESSION TABLE of the WHOLE v16
(plan_ring_p4_v16.json, prep_c141_1_mkv16.py) by PD320(c): each session = the longest prefix of the remaining compiled ops whose
predicted X10 peak <= 675 and that splits no `of` pair and no repair block (a repaired node's delete_wire .. reconnect, so no
in-between file holds a disconnected sink or uncleaned loose ends); start = stage_prerun.x10_start(bed md5) = measured bed load
600.2 + op-0 read for EVERY session (PD320(d): a later session's start is its input file's measured load - unknown until then);
(2) session 1 re-made as plan_ring_p4_s01.json FINAL from v16 ops 1..b1 (pass A ties the end rows, pass B finalizes with
open_rows + route check) - COPY of prep_c140_3_s01.py's pass A / pass B / pred code with the source plan changed;
(3) the pred file with the Error List predicted by PD322(e): bed total + ONE item per CREATED node with an unwired input at the
session's end (plus any BASE node that newly loses an input wire - predicted 0, gated).
Peak model (stage_prerun.x10_model_peak, the 140-1 table A form): start + R*read + N*(edit+other) + final, R = {a, b} + BIND ops.
PREDICTION CONTRACT:
  M0 v16 / meta16 md5 == the mkv16 RESULT line (prep_c141_1_mkv16.log), graph 50595c62;  T every session <= 675, the cuts split no
  group, sessions cover v16 once;  MS session 1 = v16 ops 1..b1, no `of` pair / new: symbol crosses the cut;  SA pass A to its end;
  TIE every end row tied;  SB FINAL, route check PASS, end rows == pass A;  SP X10 peak <= 675 at start 606.1;  EL predicted
  total = 51 + created nodes with an unwired input; base nodes newly unwired == 0.
    py tools/bgrun.py --material --max-min 20 --log tools/bench/prep_c141_1_s01.log -- py -u tools/bench/prep_c141_1_s01.py"""
import collections, copy, hashlib, json, os, re, sys, traceback                           # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagesim as SS, stagexec as SX, stage_prerun as SPR, census_predict as CPR      # noqa: E402,E401
B = os.path.join(ROOT, "tools", "bench")
V16, META16 = os.path.join(B, "plan_ring_p4_v16.json"), os.path.join(B, "plan_ring_p4_v16_meta.json")
GRAPH = os.path.join(B, "graph_ring_p3b2b_20261002_133824.json")
BEDPLAN = os.path.join(B, "plan_ring_p3b2b.json")
S1DIR = os.path.join(B, "sim", "ring_p4_s01")
S1AIN, S1IN, S1P = os.path.join(S1DIR, "plan_ring_p4_s01a_in.json"), os.path.join(B, "plan_ring_p4_s01_in.json"), os.path.join(B, "plan_ring_p4_s01.json")
PP, TAB = os.path.join(B, "plan_ring_p4_s01_pred.json"), os.path.join(B, "prep_c141_1_sessions.json")
EL = os.path.join(B, "errorlist_expected_D1_ring_p3b2b_20261002_130007.json")
MKLOG = os.path.join(B, "prep_c141_1_mkv16.log")
LIMIT = 675.0
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                             # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
G, ARTS = {"pass": 0, "fail": 0, "first": None}, []


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:700]), flush=True)
    return ok


def done():
    print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
    sys.exit(0 if not G["fail"] else 1)


res = [json.loads(m) for m in re.findall(r"^RESULT (\{.*\})$", open(MKLOG, encoding="utf-8", errors="replace").read(), re.M)]
pin = dict((a["path"], a["md5"]) for a in ((res[-1] if res else {}).get("artefacts") or []))
gate("M0 v16 / meta16 md5 == the mkv16 RESULT (PASS); graph 50595c62", bool(res) and res[-1].get("status") == "PASS"
     and pin.get(rel(V16)) == md5(V16) and pin.get(rel(META16)) == md5(META16) and md5(GRAPH) == "50595c62d0332a94bf066538cf20c0ae",
     {"pin": pin, "v16": md5(V16)})
if G["fail"]:
    done()
v16 = J(V16)
A = v16["actions"]
ids = [a["id"] for a in A]
OPS = SX.compile_plan(v16)
NOP = len(OPS)
act2op = dict((n, k) for k, o in enumerate(OPS, 1) for n in o["acts"])
BIND = set(k for k, o in enumerate(OPS, 1) if o["kind"] in SX.BIND_KINDS)
MODEL, gr = SPR.load_memory_model(), J(GRAPH)
xs = SPR.x10_start(gr["md5"], MODEL)
START = xs[0]
v = lambda k: float(MODEL[k]["value"])                                                      # noqa: E731
pos = dict((i, k) for k, i in enumerate(ids, 1))
groups = []                                                                                # [lo op, hi op] that a cut may not split
for a in A:
    if a.get("of"):
        groups.append((act2op[pos[a["of"]]], act2op[pos[a["id"]]]))
for n in sorted(set(i.split("_")[1] for i in ids if i.startswith("p4_rp"))):
    groups.append((act2op[pos["p4_{0}_dwo".format(n)]], act2op[pos["p4_{0}_out".format(n)]]))
cut_ok = lambda b: b == NOP or not any(lo <= b < hi for lo, hi in groups)                  # noqa: E731


def peak(a, b):
    reads = {a, b} | set(k for k in BIND if a < k <= b)
    return round(START + len(reads) * v("read_mb") + (b - a) * (v("edit_mb") + v("other_mb")) + v("final_read_mb"), 1), len(reads)


TABLE, a = [], 0
while a < NOP:
    best, b = None, a + 1
    while b <= NOP and peak(a, b)[0] <= LIMIT:
        if cut_ok(b):
            best = b
        b += 1
    if best is None:
        TABLE.append({"session": len(TABLE) + 1, "ops": [a + 1, None], "error": "no allowed cut <= {0}".format(LIMIT)})
        break
    pk, R_ = peak(a, best)
    acts = [n for k in range(a + 1, best + 1) for n in OPS[k - 1]["acts"]]
    TABLE.append({"session": len(TABLE) + 1, "ops": [a + 1, best], "first": ids[acts[0] - 1], "last": ids[acts[-1] - 1], "actions": len(acts),
                  "N": best - a, "R": R_, "start_mb": START, "peak_mb": pk, "kinds": dict(collections.Counter(OPS[k - 1]["kind"] for k in range(a + 1, best + 1)))})
    a = best
for r in TABLE:
    print("SESSION", json.dumps(r))
gate("T whole-v16 session table: every session <= {0}, cuts split no group, sessions cover v16 once ({1} sessions)".format(LIMIT, len(TABLE)),
     all("error" not in r and r["peak_mb"] <= LIMIT for r in TABLE) and TABLE and TABLE[-1].get("ops", [0, 0])[1] == NOP, TABLE[-1:])
json.dump({"card": "141-1", "plan": {"path": rel(V16), "md5": md5(V16)}, "ops": NOP, "actions": len(A), "start_mb": START, "start_cite": xs[1],
           "limit_mb": LIMIT, "groups": groups, "model": {"read": v("read_mb"), "edit+other": v("edit_mb") + v("other_mb"), "final": v("final_read_mb")},
           "table": TABLE}, open(TAB, "w", encoding="utf-8"), indent=1)
ARTS.append({"path": rel(TAB), "md5": md5(TAB)})
if G["fail"]:
    done()
b1 = TABLE[0]["ops"][1]
NS = len([n for k in range(1, b1 + 1) for n in OPS[k - 1]["acts"]])
made = dict(("new:" + x["as"], x["id"]) for x in A if x.get("as"))
for x in A:
    if x["op"] == "add_shift_reg" and x.get("as"):
        made["new:" + x["as"] + "R"] = made["new:" + x["as"] + "L"] = x["id"]


def syms(x):
    out = []
    for f in ("diagram", "src", "dst", "parent", "at", "on", "loop", "body", "dest_diagram", "born_on", "uid"):
        y = x.get(f)
        y = y.get("uid") if isinstance(y, dict) else y
        if isinstance(y, str) and y.startswith("new:"):
            out.append(y.split(".")[0])
    return out


IDS1 = ids[:NS]
S1 = set(IDS1)
of_cross = [(x["id"], x["of"]) for x in A if x.get("of") and ((x["id"] in S1) != (x["of"] in S1))]
late1 = [(x["id"], s) for x in A if x["id"] in S1 for s in syms(x) if s in made and made[s] not in S1]
print("SESSION1 ops 1..{0} = {1} actions {2} .. {3} | next {4}".format(b1, NS, IDS1[0], IDS1[-1], ids[NS:NS + 2]))
gate("MS session 1 = v16 ops 1..{0} ({1} actions, {2} .. {3}); no `of` pair and no new: symbol crosses the cut".format(b1, NS, IDS1[0], IDS1[-1]),
     not of_cross and not late1, {"of_cross": of_cross, "late": late1[:6]})
if G["fail"]:
    done()
# ---- pass A (no open_rows) - prep_c140_3_s01.py:79-136
keep = [copy.deepcopy(x) for x in A if x["id"] in S1]
TOP = dict((k, copy.deepcopy(v16[k])) for k in ("schema", "context", "base") if k in v16)
TOP["base"] = {"path": TOP["base"]["path"], "md5": TOP["base"]["md5"]}
gate("PV base = the measured bed graph (not provisional), pin == graph", TOP["base"]["path"].endswith(os.path.basename(GRAPH))
     and TOP["base"]["md5"] == md5(GRAPH) and not (v16.get("base") or {}).get("provisional"), TOP["base"])
os.makedirs(S1DIR, exist_ok=True)
json.dump(dict(TOP, stage="ring_p4_s01a", goal="RING P4 session 1 PASS A (card 141-1): v16 #1..#{0}, no open_rows (row tying)".format(NS), actions=keep),
          open(S1AIN, "w", encoding="utf-8"), indent=1)
gate("S0 pass-A input validates; {0} actions".format(len(keep)), *protocol.validate_obj(J(S1AIN)))
try:
    SA = SS.simulate(S1AIN, GRAPH, out_root=S1DIR, plan_out_dir=S1DIR, route_check=False)
except Exception as ex:                                                                         # noqa: BLE001
    traceback.print_exc()
    gate("SA pass A simulate returned", False, ex)
    done()
gate("SA pass A replays to its end", SA["failed"] is None and SA.get("end_cdiff_rows") is not None, SA["failed"])
if G["fail"]:
    done()
steps = SA["steps"]
end = list(SA["end_cdiff_rows"])
bed_pairs = set((int(r["node"]), r["term"]) for r in J(BEDPLAN).get("open_rows") or [])
ties, untied = {}, []
for key in end:
    n0 = steps[-1]["n"]
    for s in reversed(steps):
        if s.get("cdiff_rows") is not None and key in s["cdiff_rows"]:
            n0 = s["n"]
        else:
            break
    p = (SS.V.key_parts(key)[0], SS.V.key_parts(key)[2])
    if n0 >= 1:
        x = keep[n0 - 1]
        ties[key] = {"n": n0, "id": x["id"], "op": x["op"], "class": x.get("class") or x["op"], "pair": p}
    elif p in bed_pairs:
        ties[key] = {"n": 0, "id": "bed", "op": "base", "class": "bed-declared", "pair": p}
    else:
        untied.append((key, n0))
gate("TIE every end row tied to a session-1 action (n>=1) or to a bed-declared open pair (step 0)", not untied,
     {"untied": untied[:10], "own": sum(1 for t in ties.values() if t["n"] >= 1), "bed": sum(1 for t in ties.values() if t["n"] == 0)})
if G["fail"]:
    done()
orows, seen = [], set()
for k in sorted(ties, key=lambda k: (ties[k]["n"], k)):
    t = ties[k]
    if t["pair"] in seen:
        continue
    seen.add(t["pair"])
    rows_p = sorted(y for y in ties if ties[y]["pair"] == t["pair"])
    why = ("c141-1 PD318/PD320/PD323: made by session-1 action {0} (#{1} {2} {3}); rows {4}".format(t["id"], t["n"], t["op"], t["class"], len(rows_p)) if t["n"] >= 1 else
           "c141-1 PD318(b): open on the P3b-2b bed at step 0 = declared open row of plan_ring_p3b2b.json; rows {0}".format(len(rows_p)))
    orows.append({"node": int(t["pair"][0]), "term": t["pair"][1], "why": why[:300]})
json.dump(dict(TOP, stage="ring_p4_s01", goal="RING P4 LabVIEW session 1 (card 141-1, PD320(c)/PD323): v16 #1..#{0} ({0} actions) on the P3b-2b bed graph; "
               "open_rows = its own end rows tied per action (PD318)".format(len(keep)), open_rows=orows, actions=keep),
          open(S1IN, "w", encoding="utf-8"), indent=1)
gate("S0B session-1 input validates; {0} open pairs".format(len(orows)), *protocol.validate_obj(J(S1IN)))
SB = SS.simulate(S1IN, GRAPH, out_root=S1DIR, plan_out_dir=B, route_check=True)
p1 = J(S1P)
fz1 = p1.get("finalized") or {}
rc1 = fz1.get("route_check") or {}
print("S01 final", SB["final"], "failed", SB["failed"], "end", len(SB.get("end_cdiff_rows") or []), "match", fz1.get("open_rows_match"),
      "route", rc1.get("status"), str(rc1.get("first_fail"))[:300])
ARTS.extend({"path": rel(p), "md5": md5(p)} for p in (S1IN, S1P))
gate("SB session-1 FINAL, route check PASS, end rows == pass A", bool(SB["final"]) and p1.get("final") is True and rc1.get("status") == "PASS"
     and sorted(SB.get("end_cdiff_rows") or []) == sorted(end), {"final": SB["final"], "route": rc1.get("status"), "ff": str(rc1.get("first_fail"))[:300]})
gate("PB0 written plan's top-level base is NOT provisional", not (p1.get("base") or {}).get("provisional"), p1.get("base"))
ok17, det17 = SPR.x17_gate([p1])
gate("PG X17 over session 1: every created primitive's donor label == its prim", ok17, det17)
# ---- pred - prep_c140_3_s01.py:163-194, Error List by PD322(e)
ops1 = SX.compile_plan(p1)
bind = sorted(k for k, o in enumerate(ops1, 1) if o["kind"] in SX.BIND_KINDS)
cps = sorted(set([0, len(ops1)]) | set(bind))
mp = SPR.x10_model_peak([o["kind"] for o in ops1], cps, model=MODEL, start_mb=START)
rep = CPR.predict(p1, {}, J(os.path.join(B, "census_samples.json")))
el = J(EL)
st0 = J(SB["steps"][0]["file"]["path"])["state"]
last = J(SB["steps"][-1]["file"]["path"])["state"]
madeu = set(int(u) for u in (last.get("sym") or {}).values() if isinstance(u, int))


def unwired_in(state):
    out = collections.defaultdict(list)
    for r in state["terminals"]:
        if not r.get("is_source") and not r.get("wire_uid") and r.get("term_class") != "ControlTerminal":
            out[int(r["owner_uid"])].append(r.get("term_name"))
    return out


u0, u1 = unwired_in(st0), unwired_in(last)
created_unw = sorted((u, u1[u]) for u in u1 if u in madeu)
base_new = sorted((u, u1[u]) for u in u1 if u not in madeu and u not in u0)
print("EL bed total", el.get("total"), "| created nodes with an unwired input", created_unw, "| base nodes newly unwired", base_new)
gate("EL0 no BASE node newly loses an input wire at session 1's end (repair blocks are not split)", not base_new, base_new)
pred_total = el.get("total") + len(created_unw)
pred = {"schema": "ring-p3b-pred/1", "card": "141-1", "note": "P4 LabVIEW session 1 (v16 #1..#{0}, PD320/PD323); in-between file of P4 (D-2026-10-02-02)".format(NS),
        "plan": {"path": rel(S1P), "md5": md5(S1P)}, "graph": {"path": rel(GRAPH), "md5": md5(GRAPH)}, "bed": gr.get("vi"), "bed_md5": gr.get("md5"),
        "census": dict(rep["derived"]), "census_overall": rep["overall"], "census_unpredicted": [p1["actions"][k - 1]["id"] for k in rep["unpredicted"]],
        "ops": [o["kind"] for o in ops1], "cdiff_rows": sorted(fz1.get("end_cdiff_rows") or []),
        "row_ties": dict((k, dict((x, y) for x, y in t.items() if x != "pair")) for k, t in ties.items()),
        "errorlist": {"bed_total": el.get("total"), "new_items_predicted": len(created_unw), "predicted_total": pred_total, "alternative_total": None,
                      "created_nodes_unwired_input": [[u, n] for u, n in created_unw], "base_nodes_newly_unwired": [[u, n] for u, n in base_new],
                      "rule": "PD322(e): one 'unwired or bad terminal' item per CREATED node with an unwired input (140-3: 52 = 51 + 1)",
                      "base_file": rel(EL), "checked": False},
        "memory_pred": {"card": "141-1", "checkpoints": cps, "R": mp.get("R"), "N": mp.get("N"), "bind_ops": bind, "op_kinds": [o["kind"] for o in ops1],
                        "start_mb": mp.get("start_mb"), "start_cite": xs[1], "peak_mb": mp.get("peak_mb"), "fail_above_mb": mp.get("fail_above_mb"),
                        "below_fail": mp.get("ok"), "card_limit_mb": LIMIT, "model": {"path": rel(SPR.MEMORY_MODEL), "md5": md5(SPR.MEMORY_MODEL)}},
        "session_table": {"path": rel(TAB), "md5": md5(TAB)}, "summary": fz1.get("summary")}
json.dump(pred, open(PP, "w", encoding="utf-8"), indent=1)
ARTS.append({"path": rel(PP), "md5": md5(PP)})
print("S01 ops", dict(collections.Counter(pred["ops"])), "census", pred["census"], "unpredicted", len(pred["census_unpredicted"]),
      "X10 N/bind/R/start/peak", mp.get("N"), len(bind), mp.get("R"), mp.get("start_mb"), mp.get("peak_mb"))
print("EL PREDICTED session-1 end total {0} (= {1} + {2} created node(s) with an unwired input)".format(pred_total, el.get("total"), len(created_unw)), flush=True)
gate("SP pred written: {0} ops == compile (each action once), X10 start measured {1}, peak {2} <= {3}, == table session 1".format(
     len(ops1), START, mp.get("peak_mb"), LIMIT),
     sorted(n for o in ops1 for n in o["acts"]) == list(range(1, len(keep) + 1)) and mp.get("peak_mb") is not None and mp["peak_mb"] <= LIMIT
     and abs(mp["peak_mb"] - TABLE[0]["peak_mb"]) < 0.05, (mp.get("N"), mp.get("R"), mp.get("peak_mb"), TABLE[0]["peak_mb"]))
done()
