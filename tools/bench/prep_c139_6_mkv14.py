r"""prep_c139_6_mkv14 - card 139-6 passes 1-2 (offline, no LabVIEW, no COM). PD317(b)(c).
(1) v14: the v13 meta's 28 unstepped ids get their step by the inheritance code of prep_c139_p2_mkv11.py:164-174 COPIED VERBATIM
    (KSF / NEW ids as defined at prep_c139_p2_mkv11.py:55-69). The stageplan/1 action schema has no `step` field
    (docs/protocol/stageplan.json additionalProperties false), so the step fields live in plan_ring_p4_v14_meta.json (= v13 meta +
    an `inherited_c139_6` list of {id, step, session, unit} entries, every older entry unchanged); plan_ring_p4_v14.json = v13 with its
    actions, open_rows and finalized block unchanged (goal text + a `meta` pointer in the goal only).
(2) step-1 plan: meta step 1 of v14 (v13 order) on the P3b-2b bed graph. Pass A simulates it with NO open_rows; every end cdiff row is
    tied to the action at which it first appears and stays to the end (stagesim's first_divergent rule, stagesim.py:2458-2470):
    n0 >= 1 -> the step-1 action (id, op, class); n0 == 0 -> open on the BED at step 0, accepted only when its (node, term) pair is a
    declared open row of the bed's own plan (plan_ring_p3b2b.json open_rows). A row tied to neither -> FAIL (rule 1a, PD317(c)).
    Pass B = the same actions with those rows as open_rows -> FINAL (legacy all-rows rule), plan_ring_p4s1.json + _pred.json.
Prior art: prep_c139_5_mkv13.py (meta walk, late-ref gate, step-1 sub-plan, pred fields, X10 via stage_prerun.x10_model_peak);
prep_c139_p2_mkv11.py:164-174 (inheritance); stage_d1_ring_p3b1_el.py:6 (EL total in {pred, pred + unwired created sinks}).
PREDICTION CONTRACT:
  M0 input md5 == card (v13, v13 meta, mkv11, mkv13) + graph 50595c62;
  MS every v13 id has a step; p4_w_last_gt with p4_t_last; no action names a symbol made in a LATER step; <= 42 per step; the 28 inherited
     ids are exactly the ids the v13 meta lacked;  V14 v14 actions/open_rows/finalized == v13; meta14 older entries unchanged;
  SA pass A replays to its end (no error); TIE every end row tied (step-1 action or bed-declared base pair); SB pass B FINAL,
     route check PASS, end rows == pass A's; SP pred written (ops == compile, X10 peak below fail).
    py tools/bgrun.py --material --max-min 20 --log tools/bench/prep_c139_6_mkv14.log -- py -u tools/bench/prep_c139_6_mkv14.py"""
import collections, copy, hashlib, json, os, shutil, sys, traceback                       # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagesim as SS, stagexec as SX, stage_prerun as SPR, census_predict as CPR      # noqa: E402,E401
B = os.path.join(ROOT, "tools", "bench")
V13, META13 = os.path.join(B, "plan_ring_p4_v13.json"), os.path.join(B, "plan_ring_p4_v13_meta.json")
V14, META14 = os.path.join(B, "plan_ring_p4_v14.json"), os.path.join(B, "plan_ring_p4_v14_meta.json")
GRAPH = os.path.join(B, "graph_ring_p3b2b_20261002_133824.json")
BEDPLAN = os.path.join(B, "plan_ring_p3b2b.json")
S1DIR = os.path.join(B, "sim", "ring_p4s1")
S1AIN, S1IN, S1P = os.path.join(S1DIR, "plan_ring_p4s1a_in.json"), os.path.join(B, "plan_ring_p4s1_in.json"), os.path.join(B, "plan_ring_p4s1.json")
PP = os.path.join(B, "plan_ring_p4s1_pred.json")
EL = os.path.join(B, "errorlist_expected_D1_ring_p3b2b_20261002_130007.json")
WANT = {V13: "88e3f33648f60ee24edd71774114d757", META13: "549f4e4518c2b7d0b7047447ffb36b74", GRAPH: "50595c62d0332a94bf066538cf20c0ae",
        os.path.join(B, "prep_c139_p2_mkv11.py"): "a582a5ca6fc7e6894e6d1931612e8813", os.path.join(B, "prep_c139_5_mkv13.py"): "6057e2b96e44b83809609b401202bac0"}
KSF = "p4_c_stopall_f"                                                              # prep_c139_p2_mkv11.py:55
NEW_IDS = ["p4_i_stopall_k", "p4_lw_stopall_639", "p4_w_stopall_639"]               # prep_c139_p2_mkv11.py:56-69 (the NEW list's ids)
MOVE, GRP0 = "p4_w_last_gt", "p4_t_last"
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
v13 = J(V13)
A13 = v13["actions"]
ids = [a["id"] for a in A13]
meta = J(META13)
stepof, sessof = {}, {}


def walk(o):
    if isinstance(o, dict):
        if "id" in o and "step" in o and "unit" in o:
            stepof[o["id"]] = o["step"]
            sessof[o["id"]] = o.get("session")
        for v in o.values():
            walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)


walk(meta)
nom13 = [i for i in ids if i not in stepof]
before = dict(stepof)
# ---- prep_c139_p2_mkv11.py:164-174, copied verbatim (KSF / NEW as at :55-69)
NEW = [{"id": x} for x in NEW_IDS]
for x, t, w in (("p4_x_fd", "p4_t_fd", "p4_w_fd_in"), ("p4_x_dt", "p4_t_dt", "p4_w_dt_in")):
    stepof[t] = stepof[w] = stepof.get(x)
for n in ["p4_rbR_dw", "p4_rbR_re0", "p4_rbR_sel", "p4_rbR_lr", "p4_rbR_t", "p4_rbR_f", "p4_rbR_s", "p4_rbR_out"]:
    stepof[n] = stepof.get("p4_dec_reseed")
for k, ids_ in (("p4_gt_last", ["p4_f_min"]), ("p4_k_max", ["p4_k_max_found"]),
                ("p4_w_num_sel", ["p4_t_fnum", "p4_t_fnum_in", "p4_t_fnum_out"]),
                ("p4_w_gt_sel", ["p4_t_fgt", "p4_t_fgt_in", "p4_t_fgt_out", "p4_w_max_sel"]),
                ("p4_w_sel_amm", ["p4_t_fsel", "p4_t_fsel_in", "p4_t_fsel_out"]),
                ("p4_lr_stop12", [KSF] + [x["id"] for x in NEW])):
    for x in ids_:
        stepof[x] = stepof.get(k)
# ---- end of the copy
SRCK = {}
for x, t, w in (("p4_x_fd", "p4_t_fd", "p4_w_fd_in"), ("p4_x_dt", "p4_t_dt", "p4_w_dt_in")):
    SRCK[t] = SRCK[w] = x
for n in ["p4_rbR_dw", "p4_rbR_re0", "p4_rbR_sel", "p4_rbR_lr", "p4_rbR_t", "p4_rbR_f", "p4_rbR_s", "p4_rbR_out"]:
    SRCK[n] = "p4_dec_reseed"
for k, ids_ in (("p4_gt_last", ["p4_f_min"]), ("p4_k_max", ["p4_k_max_found"]), ("p4_w_num_sel", ["p4_t_fnum", "p4_t_fnum_in", "p4_t_fnum_out"]),
                ("p4_w_gt_sel", ["p4_t_fgt", "p4_t_fgt_in", "p4_t_fgt_out", "p4_w_max_sel"]), ("p4_w_sel_amm", ["p4_t_fsel", "p4_t_fsel_in", "p4_t_fsel_out"]),
                ("p4_lr_stop12", [KSF] + NEW_IDS)):
    for x in ids_:
        SRCK[x] = k
changed = sorted(i for i in stepof if before.get(i) != stepof[i])
over = sorted(i for i in changed if i in before)
nom = [i for i in ids if stepof.get(i) is None]
print("INHERIT v13-meta unstepped", len(nom13), nom13)
print("INHERIT changed", len(changed), [(i, before.get(i), stepof[i], SRCK.get(i)) for i in changed])
print("INHERIT overwrote an existing meta step", over)
made = dict(("new:" + a["as"], a["id"]) for a in A13 if a.get("as"))
for a in A13:
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


late = [(a["id"], s) for a in A13 for s in syms(a) if s in made and (stepof.get(made[s]) or 0) > (stepof.get(a["id"]) or 0)]
cnt = collections.Counter(stepof.get(i) for i in ids)
print("META14 actions per step", dict(sorted(cnt.items(), key=str)), "late refs", late[:8])
gate("MS every v13 id has a step; p4_w_last_gt with p4_t_last; no symbol from a LATER step; <= 42 per step; inherited == the v13-meta gaps",
     not nom and stepof[MOVE] == stepof[GRP0] and not late and max(cnt.values()) <= 42 and sorted(set(nom13)) == sorted(set(nom13) & set(changed))
     and not [i for i in changed if i in ids and i not in nom13 and i not in over], {"nom": nom, "late": late[:6], "cnt": dict(cnt), "over": over,
                                                                                    "not_in_v13": [i for i in changed if i not in ids]})
meta14 = copy.deepcopy(meta)
meta14["inherited_c139_6"] = [{"id": i, "step": stepof[i], "session": sessof.get(SRCK.get(i)), "unit": "inherited from " + str(SRCK.get(i)),
                               "cite": "prep_c139_p2_mkv11.py:164-174 (copied by prep_c139_6_mkv14.py), card 139-6 PD317(b)"}
                              for i in ids if i in nom13 or i in over]
meta14["recut_c139_6"] = {"from_md5": md5(META13), "added": len(nom13), "why": "PD317(b): v13 maker did not copy the step inheritance"}
json.dump(meta14, open(META14, "w", encoding="utf-8"), indent=1)
chk = {}
stepof2 = {}


def walk2(o):
    if isinstance(o, dict):
        if "id" in o and "step" in o and "unit" in o:
            stepof2[o["id"]] = o["step"]
        for v in o.values():
            walk2(v)
    elif isinstance(o, list):
        for v in o:
            walk2(v)


walk2(J(META14))
v14 = copy.deepcopy(v13)
v14["goal"] = str(v13.get("goal", "")) + " | v14 (card 139-6, PD317(b)): actions unchanged; per-action steps in plan_ring_p4_v14_meta.json"
json.dump(v14, open(V14, "w", encoding="utf-8"), indent=1, default=str)
v14r = J(V14)
gate("V14 actions/open_rows/finalized == v13; meta14 = every id stepped, older entries unchanged; v14 validates",
     v14r["actions"] == A13 and v14r.get("open_rows") == v13.get("open_rows") and v14r.get("finalized") == v13.get("finalized")
     and all(stepof2.get(i) == stepof.get(i) for i in ids)
     and dict((k, v) for k, v in J(META14).items() if k not in ("inherited_c139_6", "recut_c139_6")) == meta and protocol.validate_obj(v14r)[0],
     protocol.validate_obj(v14r))
ARTS.extend({"path": rel(p), "md5": md5(p)} for p in (V14, META14))
if G["fail"]:
    done()
# ---- step 1, pass A (no open_rows)
IDS1 = [i for i in ids if stepof[i] == 1]
POS = dict((i, k) for k, i in enumerate(ids, 1))
keep = [copy.deepcopy(a) for a in A13 if a["id"] in IDS1]
TOP = dict((k, copy.deepcopy(v13[k])) for k in ("schema", "context", "base") if k in v13)
print("STEP1 ids", len(keep), [(POS[a["id"]], a["id"], a["op"], a.get("class")) for a in keep])
os.makedirs(S1DIR, exist_ok=True)
json.dump(dict(TOP, stage="ring_p4s1a", goal="RING P4 step 1 PASS A (card 139-6): meta step 1 of v14, no open_rows (row tying)", actions=keep),
          open(S1AIN, "w", encoding="utf-8"), indent=1)
gate("S0 step-1 pass-A input validates; {0} actions".format(len(keep)), *protocol.validate_obj(J(S1AIN)))
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
bedp = J(BEDPLAN)
bed_pairs = set((int(r["node"]), r["term"]) for r in bedp.get("open_rows") or [])
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
gate("TIE every end row tied to a step-1 action (n>=1) or to a bed-declared open pair (step 0, plan_ring_p3b2b.json open_rows)", not untied,
     {"untied": untied[:10], "own": sum(1 for t in ties.values() if t["n"] >= 1), "bed": sum(1 for t in ties.values() if t["n"] == 0)})
if G["fail"]:
    done()
# ---- pass B: open_rows = the tied pairs (one per (node, term))
orows, seen = [], set()
for k in sorted(ties, key=lambda k: (ties[k]["n"], k)):
    t = ties[k]
    if t["pair"] in seen:
        continue
    seen.add(t["pair"])
    rows_p = sorted(x for x in ties if ties[x]["pair"] == t["pair"])
    why = ("c139-6 PD317(c): made by step-1 action {0} (#{1} {2} {3}); rows {4}".format(t["id"], t["n"], t["op"], t["class"], len(rows_p)) if t["n"] >= 1 else
           "c139-6 PD317(c): open on the P3b-2b bed at step 0 = declared open row of plan_ring_p3b2b.json; rows {0}".format(len(rows_p)))
    orows.append({"node": int(t["pair"][0]), "term": t["pair"][1], "why": why[:300]})
json.dump(dict(TOP, stage="ring_p4s1", goal="RING P4 step 1 (card 139-6): meta step 1 of plan_ring_p4_v14.json ({0} actions, v14 #{1}) on the P3b-2b "
               "bed graph; open_rows = its own end rows tied per action (PD317(c))".format(len(keep), [POS[i] for i in IDS1]), open_rows=orows, actions=keep),
          open(S1IN, "w", encoding="utf-8"), indent=1)
gate("S0B step-1 input validates; {0} open pairs".format(len(orows)), *protocol.validate_obj(J(S1IN)))
SB = SS.simulate(S1IN, GRAPH, out_root=S1DIR, plan_out_dir=B, route_check=True)
p1 = J(S1P)
fz1 = p1.get("finalized") or {}
rc1 = fz1.get("route_check") or {}
print("STEP1 final", SB["final"], "failed", SB["failed"], "end", len(SB.get("end_cdiff_rows") or []), "match", fz1.get("open_rows_match"),
      "route", rc1.get("status"), str(rc1.get("first_fail"))[:300])
ARTS.extend({"path": rel(p), "md5": md5(p)} for p in (S1IN, S1P))
gate("SB step-1 FINAL, route check PASS, end rows == pass A", bool(SB["final"]) and rc1.get("status") == "PASS" and sorted(SB.get("end_cdiff_rows") or []) == sorted(end),
     {"final": SB["final"], "route": rc1.get("status"), "ff": str(rc1.get("first_fail"))[:300]})
# ---- pred (prep_c139_5_mkv13.py pred fields) + EL prediction
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
pred = {"schema": "ring-p3b-pred/1", "card": "139-6", "note": "P4 step 1 (meta step 1 of v14); in-between file of P4 (D-2026-10-02-02)",
        "plan": {"path": rel(S1P), "md5": md5(S1P)}, "graph": {"path": rel(GRAPH), "md5": md5(GRAPH)}, "bed": gr.get("vi"), "bed_md5": gr.get("md5"),
        "census": dict(rep["derived"]), "census_overall": rep["overall"], "census_unpredicted": [p1["actions"][k - 1]["id"] for k in rep["unpredicted"]],
        "ops": [o["kind"] for o in ops1], "cdiff_rows": sorted(SB.get("end_cdiff_rows") or []),
        "row_ties": dict((k, dict((x, y) for x, y in t.items() if x != "pair")) for k, t in ties.items()),
        "errorlist": {"bed_total": el.get("total"), "new_items_predicted": 0, "predicted_total": el.get("total"),
                      "alternative_total": el.get("total") + len(unw), "unwired_created_sinks": [list(x) for x in unw],
                      "rule": "stage_d1_ring_p3b1_el.py:6 (total in {pred, pred + unwired created sinks})", "base_file": rel(EL), "checked": False},
        "memory_pred": {"card": "139-6", "checkpoints": cps, "R": mp.get("R"), "N": mp.get("N"), "bind_ops": bind, "op_kinds": [o["kind"] for o in ops1],
                        "start_mb": mp.get("start_mb"), "start_cite": start and start[1], "peak_mb": mp.get("peak_mb"), "fail_above_mb": mp.get("fail_above_mb"),
                        "below_fail": mp.get("ok"), "model": {"path": rel(SPR.MEMORY_MODEL), "md5": md5(SPR.MEMORY_MODEL)}},
        "summary": fz1.get("summary")}
json.dump(pred, open(PP, "w", encoding="utf-8"), indent=1)
ARTS.append({"path": rel(PP), "md5": md5(PP)})
print("STEP1 ops", dict(collections.Counter(pred["ops"])), "census", pred["census"], "unpredicted", pred["census_unpredicted"],
      "X10", mp.get("N"), len(bind), mp.get("R"), mp.get("start_mb"), mp.get("peak_mb"), start and start[1])
gate("SP pred written: ops == compile (each action once), X10 start measured, peak below fail", sorted(n for o in ops1 for n in o["acts"]) ==
     list(range(1, len(keep) + 1)) and bool(start) and bool(mp.get("ok")), (mp.get("peak_mb"), start))
done()
