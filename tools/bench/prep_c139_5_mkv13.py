r"""prep_c139_5_mkv13 - card 139-5 passes 4-5 (offline, no LabVIEW, no COM): plan_ring_p4_v13.json = v12 (831d899b) with ONE edit,
p4_w_stop12's dst {uid 23166, term_uid 23246} (a Diagram row addressed as a node - UNROUTABLE) -> {uid 10170, term "cond"} (the base
While that owns body #23166; stagexec.base_cond -> kind 'stop' -> OpStopFromNode_v0, card 139-5 pass 1), and the meta step re-cut of
PD316(a): p4_w_last_gt step 3 -> 2 (session of p4_t_last). Then the STEP-1 plan (meta step 1, v13 order) on v12's base + its pred.
Prior art (copied, nothing new): prep_c139_4_mkv12.py (diff by id, simulate = the finalize path, compile, route compare by action-id tuple,
meta walk); plan_ring_p3b_split_p3b2.py (sub-plan with re-indexed fs_routes, pred() fields, X10 via stage_prerun.x10_model_peak).
PREDICTION CONTRACT:
  M0 input md5 == card; V1 v13 = 185 actions, order == v12, modified exactly {p4_w_stop12}; v13_in validates;
  V2 replay END 186 steps; per-step cdiff == v12 at every id; end cdiff == v12's 24; fs_routes ids == v12's;
  V3 compile 167 ops; route compare v12 -> v13 differs only on (p4_w_stop12,), now kind 'stop' loop 10170;
  V4 advisory route check: 0 UNROUTABLE;  MS meta: every id has a step; p4_w_last_gt with p4_t_last in step 2; no action names a
     symbol created in a LATER step; actions per step <= 42;
  S1 step-1 sub-plan simulates to its end (no error), route check PASS; S1F FINAL (open_rows carried from v12 as in the P3b-2a pattern
     - the open_rows match is NOT predicted: v12 itself is not final, open_rows_match False); S1P pred written (ops == compile, X10).
    py tools/bgrun.py --material --max-min 15 --log tools/bench/prep_c139_5_mkv13.log -- py -u tools/bench/prep_c139_5_mkv13.py"""
import collections, copy, hashlib, json, os, shutil, sys, traceback                       # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagesim as SS, stagexec as SX, stage_prerun as SPR, census_predict as CPR      # noqa: E402,E401
B = os.path.join(ROOT, "tools", "bench")
V12, V13IN, V13 = (os.path.join(B, "plan_ring_p4_v{0}.json".format(x)) for x in ("12", "13_in", "13"))
META, META13 = os.path.join(B, "plan_ring_p4_v3_meta.json"), os.path.join(B, "plan_ring_p4_v13_meta.json")
GRAPH = os.path.join(B, "graph_ring_p3b2b_20261002_133824.json")
V12SUM = os.path.join(B, "sim", "ring_p4_v12", "ring_p4_v3", "summary.json")
SIMDIR, S1DIR = os.path.join(B, "sim", "ring_p4_v13"), os.path.join(B, "sim", "ring_p4s1")
S1IN, S1P = os.path.join(B, "plan_ring_p4s1_in.json"), os.path.join(B, "plan_ring_p4s1.json")
EL = os.path.join(B, "errorlist_expected_D1_ring_p3b2b_20261002_130007.json")
WANT = {V12: "831d899be8a470fae188261adb7fd53d", GRAPH: "50595c62d0332a94bf066538cf20c0ae",
        os.path.join(B, "prep_c139_4_mkv12.py"): "55aebef4933018b68996304fecf765a6"}
EDIT, MOVE, GRP0 = "p4_w_stop12", "p4_w_last_gt", "p4_t_last"
NEWDST = {"uid": 10170, "term": "cond"}
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                             # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
sig = lambda o: json.dumps(dict((k, v) for k, v in o.items() if k not in ("acts", "in_act", "out_act", "of_act")), sort_keys=True, default=str)   # noqa: E731
G, ARTS = {"pass": 0, "fail": 0, "first": None}, []


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:600]), flush=True)
    return ok


def done():
    print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
    sys.exit(0 if not G["fail"] else 1)


def unroutable(plan):
    rc = ((plan.get("finalized") or {}).get("route_check") or {})
    return rc.get("status"), sorted(set(i for r in (rc.get("rows") or []) if r.get("unroutable") for i in (r.get("ids") or ["?acts"])))


gate("M0 input md5 == card", all(md5(p) == w for p, w in WANT.items()), dict((os.path.basename(p), md5(p)) for p in WANT))
v12 = J(V12)
A12 = v12["actions"]
ids = [a["id"] for a in A12]
A13 = copy.deepcopy(A12)
e = A13[ids.index(EDIT)]
old = e["dst"]
e["dst"] = dict(NEWDST)
e["why"] = ("ROUTE stop | MEASURED verb | card 139-5 (PD316(b)): base While #10170 (owner of body #23166, graph owners) cond <- LRS2.value; "
            "compile kind 'stop' (stagexec.base_cond) = OpStopFromNode_v0 by WhileLoop index (ran onto #23246 in S2, stage_d1_s2_loops.log:61-69); "
            "the scaffold wire w23310 on the cond is deleted by p4_dw_23310 (action 1, prep_c139_5_probe.log); was dst " + json.dumps(old))
mod = [i for i, a, b in zip(ids, A12, A13) if a != b]
gate("V1 v13 = 185 actions, order == v12, modified exactly {p4_w_stop12}", len(A13) == 185 and [a["id"] for a in A13] == ids and mod == [EDIT], mod)
raw = copy.deepcopy(v12)
raw.update(actions=A13, goal="P4 v13 (card 139-5, PD316(b)): v12 831d899b with p4_w_stop12 -> {uid 10170, term cond} (base-loop stop route); "
           "meta re-cut p4_w_last_gt -> step 2 (PD316(a)); never launched")
raw.pop("finalized", None)
raw.pop("final", None)
json.dump(raw, open(V13IN, "w", encoding="utf-8"), indent=1, default=str)
gate("V1b v13_in validates (stageplan/1)", *protocol.validate_obj(J(V13IN)))
# ---- meta re-cut (PD316(a)) and the meta-step gate
meta = J(META)
entries = []


def walk(o):
    if isinstance(o, dict):
        if "id" in o and "step" in o and "unit" in o:
            entries.append(o)
        for v in o.values():
            walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)


walk(meta)
ent = dict((x["id"], x) for x in entries)
print("META", MOVE, ent[MOVE]["step"], ent[MOVE].get("session"), "|", GRP0, ent[GRP0]["step"], ent[GRP0].get("session"))
for x in entries:
    if x["id"] == MOVE:
        x["step"], x["session"] = ent[GRP0]["step"], ent[GRP0].get("session")
        x["cite"] = str(x.get("cite", "")) + " | card 139-5 PD316(a): moved step 3 -> 2 (before p4_t_last)"
meta["recut_c139_5"] = {"moved": MOVE, "to_step": ent[GRP0]["step"], "from_md5": md5(META), "why": "PD316(a), docs/d1/ring-p4.md:329-331"}
json.dump(meta, open(META13, "w", encoding="utf-8"), indent=1)
stepof = dict((x["id"], x["step"]) for x in entries)
nom = [i for i in ids if i not in stepof]
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


late = [(a["id"], s) for a in A13 for s in syms(a) if s in made and stepof.get(made[s], 0) > stepof.get(a["id"], 0)]
cnt = collections.Counter(stepof.get(i) for i in ids)
print("META13 actions per step", dict(sorted(cnt.items(), key=str)), "no step", nom, "late refs", late[:8])
gate("MS meta step gate: every id has a step; p4_w_last_gt with p4_t_last; no action names a symbol made in a LATER step; <= 42 per step",
     not nom and stepof[MOVE] == stepof[GRP0] and not late and max(cnt.values()) <= 42, {"nom": nom, "late": late[:6], "cnt": dict(cnt)})
# ---- replay v13 (finalize path)
os.makedirs(SIMDIR, exist_ok=True)
try:
    S = SS.simulate(V13IN, GRAPH, out_root=SIMDIR, plan_out_dir=SIMDIR)
except Exception as ex:                                                                         # noqa: BLE001
    traceback.print_exc()
    gate("V2 simulate returned", False, ex)
    done()
shutil.copyfile(S["plan_out"]["path"] if os.path.isabs(S["plan_out"]["path"]) else os.path.join(ROOT, S["plan_out"]["path"]), V13)
v13 = J(V13)
steps = S.get("steps") or []
errs = [s for s in steps if s.get("error")]
c12 = dict((s.get("id"), s.get("cdiff_rows")) for s in J(V12SUM).get("steps") or [])
dif = [(s.get("n"), s.get("id")) for s in steps if s.get("id") in c12 and c12[s.get("id")] != s.get("cdiff_rows")]
for s in steps:
    if s.get("id") == EDIT:
        print("STEP", s.get("n"), s.get("op"), EDIT, str(s.get("error") or s.get("effect_summary") or s.get("effect"))[:400])
fr, fr12 = (v13.get("finalized") or {}).get("fs_routes") or {}, (v12.get("finalized") or {}).get("fs_routes") or {}
gate("V2 replay END 186 steps, per-step cdiff == v12 at every id, fs_routes ids == v12's",
     not errs and len(steps) == 186 and not dif and sorted(r["id"] for r in fr.values()) == sorted(r["id"] for r in fr12.values()),
     {"steps": len(steps), "err": (errs[0].get("n"), errs[0].get("id"), str(errs[0].get("error"))[:300]) if errs else None, "dif": dif[:6]})
gate("V2b end cdiff == v12's 24", sorted(S.get("end_cdiff_rows") or []) == sorted(v12["finalized"]["end_cdiff_rows"]) and len(v12["finalized"]["end_cdiff_rows"]) == 24,
     len(S.get("end_cdiff_rows") or []))
o12, o13 = SX.compile_plan(v12), SX.compile_plan(v13)
m12 = dict((tuple(A12[n - 1]["id"] for n in o["acts"]), sig(o)) for o in o12)
m13 = dict((tuple(A13[n - 1]["id"] for n in o["acts"]), sig(o)) for o in o13)
diffs = sorted(k for k in set(m12) | set(m13) if m12.get(k) != m13.get(k))
for k in diffs:
    print("ROUTE-DIFF", k, "| v12", m12.get(k), "| v13", m13.get(k))
gate("V3 compile 167 ops; route compare v12->v13 only on (p4_w_stop12,) = stop loop 10170", len(o13) == len(o12) == 167 and diffs == [(EDIT,)]
     and json.loads(m13[(EDIT,)]) == {"kind": "stop", "loop": 10170}, (len(o12), len(o13), diffs))
st13, un13 = unroutable(v13)
print("ROUTE CHECK v12", unroutable(v12), "| v13", st13, un13)
for r in ((v13.get("finalized") or {}).get("route_check") or {}).get("rows") or []:
    if EDIT in (r.get("ids") or []):
        print("ROUTE-ROW", json.dumps(r)[:400])
gate("V4 advisory route check: 0 UNROUTABLE", un13 == [], (st13, un13))
ARTS.extend({"path": rel(p), "md5": md5(p)} for p in (V13IN, V13, META13))
if G["fail"]:
    done()
# ---- step 1 (meta step 1, v13 order) on v12's base
IDS1 = [i for i in ids if stepof[i] == 1]
POS = dict((i, k) for k, i in enumerate(ids, 1))
keep = [copy.deepcopy(a) for a in A13 if a["id"] in IDS1]
TOP = dict((k, copy.deepcopy(v12[k])) for k in ("schema", "context", "open_rows", "base") if k in v12)
json.dump(dict(TOP, stage="ring_p4s1", goal="RING P4 step 1 (card 139-5): meta step 1 of plan_ring_p4_v13.json ({0} actions, v13 #{1}) on the P3b-2b "
               "bed graph; open_rows carried from v13 (P3b-2a pattern)".format(len(keep), [POS[i] for i in IDS1]), actions=keep),
          open(S1IN, "w", encoding="utf-8"), indent=1)
gate("S0 step-1 input validates; {0} actions".format(len(keep)), protocol.validate_obj(J(S1IN))[0], protocol.validate_obj(J(S1IN)))
os.makedirs(S1DIR, exist_ok=True)
S1 = SS.simulate(S1IN, GRAPH, out_root=S1DIR, plan_out_dir=B, route_check=True)
p1 = J(S1P)
rc1 = (p1.get("finalized") or {}).get("route_check") or {}
fz1 = p1.get("finalized") or {}
print("STEP1 final", S1["final"], "failed", S1["failed"], "end cdiff", len(S1.get("end_cdiff_rows") or []), "open_rows_match", fz1.get("open_rows_match"),
      "classed", json.dumps(fz1.get("open_rows_classed"))[:400], "route", rc1.get("status"), str(rc1.get("first_fail"))[:300])
ARTS.extend({"path": rel(p), "md5": md5(p)} for p in (S1IN, S1P))
gate("S1 step-1 replays to its end, route check PASS", S1["failed"] is None and rc1.get("status") == "PASS",
     {"failed": S1["failed"], "route": rc1.get("status"), "first_fail": str(rc1.get("first_fail"))[:300]})
gate("S1F step-1 plan FINAL (open_rows_match)", bool(S1["final"]), {"open_rows_match": fz1.get("open_rows_match"), "end": S1.get("end_cdiff_rows")})
# ---- pred (plan_ring_p3b_split_p3b2.pred fields), written even when S1F fails so the facts are on disk
MODEL, gr = SPR.load_memory_model(), J(GRAPH)
start = SPR.x10_start(gr["md5"], MODEL)
ops1 = SX.compile_plan(p1)
bind = sorted(k for k, o in enumerate(ops1, 1) if o["kind"] in SX.BIND_KINDS)
cps = sorted(set([0, len(ops1)]) | set(bind))
mp = SPR.x10_model_peak([o["kind"] for o in ops1], cps, model=MODEL, start_mb=start[0]) if start else {"peak_mb": None, "ok": False}
rep = CPR.predict(p1, {}, J(os.path.join(B, "census_samples.json")))
el = J(EL)
pred = {"schema": "ring-p3b-pred/1", "card": "139-5", "note": "P4 step 1 (meta step 1 of v13); in-between file of P4 (D-2026-10-02-02)",
        "plan": {"path": rel(S1P), "md5": md5(S1P)}, "graph": {"path": rel(GRAPH), "md5": md5(GRAPH)}, "bed": gr.get("vi"), "bed_md5": gr.get("md5"),
        "census": dict(rep["derived"]), "census_overall": rep["overall"], "census_unpredicted": [p1["actions"][k - 1]["id"] for k in rep["unpredicted"]],
        "ops": [o["kind"] for o in ops1], "cdiff_rows": sorted(S1.get("end_cdiff_rows") or []),
        "errorlist": {"bed_total": el.get("total"), "new_items_predicted": 0, "predicted_total": el.get("total"), "base_file": rel(EL), "checked": False},
        "memory_pred": {"card": "139-5", "checkpoints": cps, "R": mp.get("R"), "N": mp.get("N"), "bind_ops": bind, "op_kinds": [o["kind"] for o in ops1],
                        "start_mb": mp.get("start_mb"), "start_cite": start and start[1], "peak_mb": mp.get("peak_mb"), "fail_above_mb": mp.get("fail_above_mb"),
                        "below_fail": mp.get("ok"), "model": {"path": rel(SPR.MEMORY_MODEL), "md5": md5(SPR.MEMORY_MODEL)}},
        "summary": fz1.get("summary")}
PP = os.path.join(B, "plan_ring_p4s1_pred.json")
json.dump(pred, open(PP, "w", encoding="utf-8"), indent=1)
ARTS.append({"path": rel(PP), "md5": md5(PP)})
creates = collections.Counter(a.get("class") for a in keep if a["op"] == "create")
print("STEP1 ops", dict(collections.Counter(pred["ops"])), "creates", dict(creates), "census", pred["census"], "unpredicted", pred["census_unpredicted"],
      "X10", mp.get("N"), len(bind), mp.get("R"), mp.get("start_mb"), mp.get("peak_mb"), start and start[1])
gate("S1P pred written: ops == compile (each action once), X10 start measured, peak below fail", sorted(n for o in ops1 for n in o["acts"]) ==
     list(range(1, len(keep) + 1)) and bool(start) and bool(mp.get("ok")), (mp.get("peak_mb"), start))
done()
