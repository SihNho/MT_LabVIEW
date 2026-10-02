r"""prep_c140_3_s01 - card 140-3 item 3 (offline, no LabVIEW, no COM). PD321(b): P4 LabVIEW SESSION 1 re-made from v15 ops 1..16
(p4_dw_23310, p4_dw_23255, p4_do_10171 .. p4_w_b_out; R 11, predicted 673.4); p4_x_i_rab1 (17) goes to session 2 with p4_rle_i_rab1 (18).
COPY of tools/bench/prep_c140_2_s01.py (67e57181, card 140-2) with ONLY the source plan changed (v14 -> v15 + meta15, md5 pins) and the
card id in names/strings (140-2 -> 140-3); the MS gate's first/last ids are unchanged (ops 2-3 are inside the cut). v15 is written
without `provisional` (PD321(d)), so gate PV only re-checks the measured base evidence.
Prior art checked: prep_c140_2_s01.py (this file's base), prep_c140_3_mkv15.py (v15, PASS 16/0).
PREDICTION CONTRACT:
  M0 input md5 == card;  MS the 16 actions = v15 #1..#16, first p4_dw_23310, last p4_w_b_out; no `of` pair and no new: symbol
  crosses the cut;  SA pass A replays to its end;  TIE every end row tied;  SB pass B FINAL, route check PASS, end rows == pass A;
  SP ops == 16 (== actions), X10 start measured (606.1), R 11, peak 673.4 <= 675; EL predicted_total (+ alternative) written.
    py tools/bgrun.py --material --max-min 20 --log tools/bench/prep_c140_3_s01.log -- py -u tools/bench/prep_c140_3_s01.py"""
import collections, copy, hashlib, json, os, sys, traceback                               # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagesim as SS, stagexec as SX, stage_prerun as SPR, census_predict as CPR      # noqa: E402,E401
B = os.path.join(ROOT, "tools", "bench")
V14, META14 = os.path.join(B, "plan_ring_p4_v15.json"), os.path.join(B, "plan_ring_p4_v15_meta.json")   # names kept from the base; v15
GRAPH = os.path.join(B, "graph_ring_p3b2b_20261002_133824.json")
BEDPLAN = os.path.join(B, "plan_ring_p3b2b.json")
S1DIR = os.path.join(B, "sim", "ring_p4_s01")
S1AIN, S1IN, S1P = os.path.join(S1DIR, "plan_ring_p4_s01a_in.json"), os.path.join(B, "plan_ring_p4_s01_in.json"), os.path.join(B, "plan_ring_p4_s01.json")
PP = os.path.join(B, "plan_ring_p4_s01_pred.json")
EL = os.path.join(B, "errorlist_expected_D1_ring_p3b2b_20261002_130007.json")
WANT = {V14: "eb4ffb6e2a27993a372064470c1c325b", META14: "d012bd2c2d065aed1e16ddab394010e7", GRAPH: "50595c62d0332a94bf066538cf20c0ae"}
NS, FIRST, LAST, LIMIT = 16, "p4_dw_23310", "p4_w_b_out", 675.0
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


gate("M0 input md5 == card", all(md5(p) == w for p, w in WANT.items()), dict((os.path.basename(p), md5(p)) for p in WANT))
if G["fail"]:
    done()
v14 = J(V14)
A14 = v14["actions"]
ids = [a["id"] for a in A14]
made = dict(("new:" + a["as"], a["id"]) for a in A14 if a.get("as"))
for a in A14:
    if a["op"] == "add_shift_reg" and a.get("as"):
        made["new:" + a["as"] + "R"] = made["new:" + a["as"] + "L"] = a["id"]


def syms(a):
    out = []
    for f in ("diagram", "src", "dst", "parent", "at", "on", "loop", "body", "dest_diagram", "born_on", "uid"):
        x = a.get(f)
        x = x.get("uid") if isinstance(x, dict) else x
        if isinstance(x, str) and x.startswith("new:"):
            out.append(x.split(".")[0])
    return out


IDS1 = ids[:NS]
S1 = set(IDS1)
of_cross = [(a["id"], a["of"]) for a in A14 if a.get("of") and ((a["id"] in S1) != (a["of"] in S1))]
late1 = [(a["id"], s) for a in A14 if a["id"] in S1 for s in syms(a) if s in made and made[s] not in S1]
print("SESSION1 ids", IDS1, "| of pairs crossing", of_cross, "| late refs", late1[:8], "| v15 #17 #18", ids[16:18])
gate("MS session 1 = v15 #1..#16 ({0} .. {1}); no `of` pair and no new: symbol crosses the cut".format(FIRST, LAST),
     len(IDS1) == NS and IDS1[0] == FIRST and IDS1[-1] == LAST and not of_cross and not late1, {"of_cross": of_cross, "late": late1[:6]})
if G["fail"]:
    done()
# ---- pass A (no open_rows) - prep_c139_7_s1.py:97-144
POS = dict((i, k) for k, i in enumerate(ids, 1))
keep = [copy.deepcopy(a) for a in A14 if a["id"] in S1]
TOP = dict((k, copy.deepcopy(v14[k])) for k in ("schema", "context", "base") if k in v14)
# v15's base is written WITHOUT the stale `provisional` (PD321(d), prep_c140_3_mkv15.py); gate PV still requires the measured evidence
# that the base graph is the read of the saved bed (review archive/peer/2026-10-02-c140-2-provisional-base.md sec. 1).
gr0, BEDVI, BEDMD5 = J(GRAPH), r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_ring_p3b2b_20261002_130007.vi", "395118775a52bc90073f4449b99f899d"
negs = [r for r in gr0["terminals"] for f in ("owner_uid", "term_uid", "wire_uid", "frame_diagram") if isinstance(r.get(f), int) and r[f] < 0]
GL = open(os.path.join(B, "diag_c136_1_graph.log"), encoding="utf-8", errors="replace").read()
ev = {"K1": "PASS  K1 input md5 == " + BEDMD5 in GL, "WROTE": ("graph_ring_p3b2b_20261002_133824.json md5 " + WANT[GRAPH]) in GL,
      "H2": ("before {0} / after {0}".format(BEDMD5)) in GL, "rc0": "BGRUN END rc=0" in GL, "bed_now": md5(BEDVI) == BEDMD5, "negs0": not negs}
gate("PV base graph = the measured read of the bed (diag_c136_1_graph.log K1/WROTE 50595c62/H2/rc 0; bed md5 now 39511877; 0 negative uids); base pin == graph",
     all(ev.values()) and TOP["base"]["path"].endswith(os.path.basename(GRAPH)) and TOP["base"]["md5"] == WANT[GRAPH], {"ev": ev, "base": TOP["base"]})
if G["fail"]:
    done()
TOP["base"] = {"path": TOP["base"]["path"], "md5": TOP["base"]["md5"]}
print("S01 ids", len(keep), [(POS[a["id"]], a["id"], a["op"], a.get("class")) for a in keep])
os.makedirs(S1DIR, exist_ok=True)
json.dump(dict(TOP, stage="ring_p4_s01a", goal="RING P4 session 1 PASS A (card 140-3): v15 #1..#16, no open_rows (row tying)", actions=keep),
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
step0 = set(steps[0].get("cdiff_rows") or [])
print("STEP0 rows", len(step0), "| END rows", len(end), "| step0 rows gone at end", sorted(step0 - set(end)))
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
        a = keep[n0 - 1]
        ties[key] = {"n": n0, "id": a["id"], "op": a["op"], "class": a.get("class") or a["op"], "pair": p}
    elif p in bed_pairs:
        ties[key] = {"n": 0, "id": "bed", "op": "base", "class": "bed-declared", "pair": p}
    else:
        untied.append((key, n0))
for k in sorted(ties):
    print("TIE", k, json.dumps(ties[k]))
for k, n0 in untied:
    print("UNTIED", k, "first at step", n0)
gate("TIE every end row tied to a session-1 action (n>=1) or to a bed-declared open pair (step 0, plan_ring_p3b2b.json open_rows)", not untied,
     {"untied": untied[:10], "own": sum(1 for t in ties.values() if t["n"] >= 1), "bed": sum(1 for t in ties.values() if t["n"] == 0)})
if G["fail"]:
    done()
# ---- pass B - prep_c139_7_s1.py:145-168
orows, seen = [], set()
for k in sorted(ties, key=lambda k: (ties[k]["n"], k)):
    t = ties[k]
    if t["pair"] in seen:
        continue
    seen.add(t["pair"])
    rows_p = sorted(x for x in ties if ties[x]["pair"] == t["pair"])
    why = ("c140-3 PD318/PD320/PD321: made by session-1 action {0} (#{1} {2} {3}); rows {4}".format(t["id"], t["n"], t["op"], t["class"], len(rows_p)) if t["n"] >= 1 else
           "c140-3 PD318(b): open on the P3b-2b bed at step 0 = declared open row of plan_ring_p3b2b.json; rows {0}".format(len(rows_p)))
    orows.append({"node": int(t["pair"][0]), "term": t["pair"][1], "why": why[:300]})
json.dump(dict(TOP, stage="ring_p4_s01", goal="RING P4 LabVIEW session 1 (card 140-3, PD320(c)/PD321(b)): v15 #1..#16 ({0} actions) on the P3b-2b bed graph; "
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
gate("PB0 written plan's top-level base is NOT provisional (check_launch:4033-4039)", not (p1.get("base") or {}).get("provisional"), p1.get("base"))
# ---- pred - prep_c139_7_s1.py:169-200
MODEL, gr = SPR.load_memory_model(), J(GRAPH)
start = SPR.x10_start(gr["md5"], MODEL)
ops1 = SX.compile_plan(p1)
bind = sorted(k for k, o in enumerate(ops1, 1) if o["kind"] in SX.BIND_KINDS)
cps = sorted(set([0, len(ops1)]) | set(bind))
mp = SPR.x10_model_peak([o["kind"] for o in ops1], cps, model=MODEL, start_mb=start[0]) if start else {"peak_mb": None, "ok": False}
rep = CPR.predict(p1, {}, J(os.path.join(B, "census_samples.json")))
el = J(EL)
last = J(SB["steps"][-1]["file"]["path"])["state"]
madeu = set(str(u) for u in (last.get("sym") or {}).values())
unw = sorted(set((str(r["owner_uid"]), r.get("term_name")) for r in last["terminals"] if str(r["owner_uid"]) in madeu and not r.get("is_source") and not r.get("wire_uid")))
print("EL bed total", el.get("total"), "| unwired created sinks", len(unw), unw[:20])
pred = {"schema": "ring-p3b-pred/1", "card": "140-3", "note": "P4 LabVIEW session 1 (v15 #1..#16, PD320/PD321); in-between file of P4 (D-2026-10-02-02)",
        "plan": {"path": rel(S1P), "md5": md5(S1P)}, "graph": {"path": rel(GRAPH), "md5": md5(GRAPH)}, "bed": gr.get("vi"), "bed_md5": gr.get("md5"),
        "census": dict(rep["derived"]), "census_overall": rep["overall"], "census_unpredicted": [p1["actions"][k - 1]["id"] for k in rep["unpredicted"]],
        "ops": [o["kind"] for o in ops1], "cdiff_rows": sorted(fz1.get("end_cdiff_rows") or []),
        "row_ties": dict((k, dict((x, y) for x, y in t.items() if x != "pair")) for k, t in ties.items()),
        "errorlist": {"bed_total": el.get("total"), "new_items_predicted": 0, "predicted_total": el.get("total"),
                      "alternative_total": el.get("total") + len(unw), "unwired_created_sinks": [list(x) for x in unw],
                      "rule": "stage_d1_ring_p3b1_el.py:6 (total in {pred, pred + unwired created sinks})", "base_file": rel(EL), "checked": False},
        "memory_pred": {"card": "140-3", "checkpoints": cps, "R": mp.get("R"), "N": mp.get("N"), "bind_ops": bind, "op_kinds": [o["kind"] for o in ops1],
                        "start_mb": mp.get("start_mb"), "start_cite": start and start[1], "peak_mb": mp.get("peak_mb"), "fail_above_mb": mp.get("fail_above_mb"),
                        "below_fail": mp.get("ok"), "card_limit_mb": LIMIT, "model": {"path": rel(SPR.MEMORY_MODEL), "md5": md5(SPR.MEMORY_MODEL)}},
        "summary": fz1.get("summary")}
json.dump(pred, open(PP, "w", encoding="utf-8"), indent=1)
ARTS.append({"path": rel(PP), "md5": md5(PP)})
print("S01 ops", dict(collections.Counter(pred["ops"])), "census", pred["census"], "unpredicted", pred["census_unpredicted"],
      "X10 N/bind/R/start/peak", mp.get("N"), len(bind), mp.get("R"), mp.get("start_mb"), mp.get("peak_mb"), start and start[1])
print("EL PREDICTED session-1 end total {0} (alternative {1})".format(el.get("total"), el.get("total") + len(unw)), flush=True)
gate("SP pred written: {0} ops == compile (each action once), X10 start measured, R 11, peak <= {1} (pred 673.4)".format(len(ops1), LIMIT),
     sorted(n for o in ops1 for n in o["acts"]) == list(range(1, len(keep) + 1)) and bool(start) and mp.get("R") == 11
     and mp.get("peak_mb") is not None and mp["peak_mb"] <= LIMIT, (mp.get("N"), mp.get("R"), mp.get("peak_mb"), start))
done()
