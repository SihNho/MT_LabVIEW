r"""plan_ring_p3b_split_p3b2 - card 133-3 (OFFLINE, no LabVIEW, no COM; PD283(c)(e)): cut the 39 actions of the rebased, FINAL
P3b-2 plan (plan_ring_p3b2.json 04204133, REFERENCE, never launched, not written here) into two LabVIEW sessions a / b.
WHAT EXISTED FIRST: plan_ring_p3b_split.py (the 70 -> 31/39 cut: closure, x10_of, sim(), shape(), pred()), stagesim.simulate
(finalize + fs_routes + route check), stage_prerun.x10_model_peak / x10_start (card 133-3: measured load of the input VI),
diag_c133_1_pred_p3b2.py (the pred fields of a rebased plan). Nothing new is built here; the cut is the only free variable.
RULE (stated before the run): units = connected components of the actions over their `new:` symbols and `of` links, plus a
route edge: an `fs_inner_branch` crossing depends on the unit holding this plan's `fs_border` crossing from the same source uid
(finalized.fs_routes). Part a = a dependency-closed set of units (actions in plan order), b = the rest (plan order); b names
nothing a creates (else refused). X10 per session (checkpoints {0,len}|BIND, compiled WITH the reindexed fs_routes):
start a = load(P3b-1 file 9d7bf287, 584.1) + op-0 read 5.9 = 590.0 (memory_model.json load_by_vi / op0_read_mb);
start b = a's PREDICTED load + op-0 read, load = 584.1 + load_growth_mb_per_op 0.719 x N_a (one measured pair, stated).
Best cut = smallest LARGER peak (ties: fewer a actions); FAIL if > 690 (no cut is then written; judgement decides).
PREDICTION: S0 pins; S1 P3b-1's X10 with the P3a measured start 567.7 = 678.5 within 680.4 +- 3, unsplit P3b-2 at 590 ~722;
S2 5 units, best cut larger peak <= 690; S3 a finalized on the fsmap base, route check PASS, 0 unbound, end cdiff 16;
S4 b provisional (a's sim end) final, end cdiff 16; S5 a+b end == 04204133's end (shape, cdiff 16); S6 preds written, ops ==
compile, memory_pred start stated; S7 EL range (rule of errorlist_expect_p3b2.py) on a.step_00 -> b.last == the unsplit's.
    py tools/bgrun.py --material --max-min 8 --log tools/bench/plan_ring_p3b_split_p3b2_c133_3.log -- py -u tools/bench/plan_ring_p3b_split_p3b2.py"""
import collections, copy, hashlib, itertools, json, os, sys                            # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P, stagesim as SS, stagexec as SX, census_predict as CPR, stage_prerun as SPR   # noqa: E402,E401
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                    # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                       # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
ok, arts = [], []


def gate(name, c, det=""):
    ok.append((name, bool(c)))
    print("{0}  {1}  {2}".format("PASS" if c else "FAIL", name, str(det)[:1500]), flush=True)


def finish():
    np_, nf = sum(1 for _n, c in ok if c), sum(1 for _n, c in ok if not c)
    print(P.result_line(P.make_result(np_, nf, next((n for n, c in ok if not c), None), arts)), flush=True)
    sys.exit(1 if nf else 0)


REF, PIN_ = os.path.join(B, "plan_ring_p3b2.json"), os.path.join(B, "plan_ring_p3b2_in.json")
FSM = os.path.join(B, "sim", "ring_p3b2_base_real_fsmap.json")
P3A_G, P1PRED = os.path.join(B, "graph_ring_p3a_20261001_190155.json"), os.path.join(B, "plan_ring_p3b1_pred.json")
EXP1 = os.path.join(B, "errorlist_expected_D1_ring_p3b1_20261002_060910.json")
PINS = {REF: "04204133d6c55929f368ec3761f70445", PIN_: "4df60e63ae0cb220345f1ee6d437868f", FSM: "75e64374c76f11a36de096afa5ebda37"}
gate("S0 inputs md5 == card (plan_ring_p3b2 04204133, _in 4df60e63, fsmap 75e64374)", all(md5(p) == m for p, m in PINS.items()),
     dict((rel(p), md5(p)) for p in PINS))
REFP = J(REF)
A, FZ = REFP["actions"], REFP["finalized"]
MODEL = SPR.load_memory_model()
v = lambda k: float(MODEL[k]["value"])                                            # noqa: E731
G3A, GF = J(P3A_G), J(FSM)
sA, cA = SPR.x10_start(G3A["md5"], MODEL) or (None, "P3a load NOT in memory_model")
sB, cB = SPR.x10_start(GF["md5"], MODEL) or (None, "P3b-1 load NOT in memory_model")
p1 = J(P1PRED)["memory_pred"]
x1 = SPR.x10_model_peak(p1["op_kinds"], p1["checkpoints"], model=MODEL, start_mb=sA) if sA else {"peak_mb": None}
ops_ref = SX.compile_plan(REFP)
cps_ref = sorted(set([0, len(ops_ref)]) | set(k for k, o in enumerate(ops_ref, 1) if o["kind"] in SX.BIND_KINDS))
xr = SPR.x10_model_peak([o["kind"] for o in ops_ref], cps_ref, model=MODEL, start_mb=sB) if sB else {"peak_mb": None}
print("  FACT  X10 START P3a bed {0}: {1} = {2}".format(G3A["md5"][:8], sA, cA), flush=True)
print("  FACT  X10 START P3b-1 file {0}: {1} = {2}".format(GF["md5"][:8], sB, cB), flush=True)
gate("S1 X10 start from the MEASURED load of the input VI: P3b-1 re-modelled at {0} -> {1} MB within 680.4 +- 3 (stage_d1_ring_p3b1.log:430); "
     "P3b-2 starts at {2}; unsplit P3b-2 (N {3}, R {4}) = {5} MB".format(sA, x1["peak_mb"], sB, xr.get("N"), xr.get("R"), xr["peak_mb"]),
     sA and sB and abs(x1["peak_mb"] - 680.4) <= 3.0 and sB == 590.0, {"p3b1": x1, "p3b2_unsplit": xr})
if not (sA and sB):
    finish()

# ---- units: components over new: symbols + of links, plus the fs route edge
DEF = dict(("new:" + a["as"], a["id"]) for a in A if a["op"] == "create" and a.get("as"))
POS = dict((a["id"], k) for k, a in enumerate(A, 1))


def syms(a):
    out = []
    for f in ("diagram", "src", "dst", "parent", "at", "on"):
        x = a.get(f)
        if isinstance(x, str) and x.startswith("new:"):
            out.append(x.split(".")[0])
    return out


par = dict((a["id"], a["id"]) for a in A)


def find(x):
    while par[x] != x:
        x = par[x]
    return x


for a in A:
    for s in syms(a):
        if s in DEF:
            par[find(a["id"])] = find(DEF[s])
    if a.get("of"):
        par[find(a["id"])] = find(a["of"])
UNITS = collections.OrderedDict()
for a in A:
    UNITS.setdefault(find(a["id"]), []).append(a["id"])
uof = dict((i, r) for r, ids in UNITS.items() for i in ids)
FR = FZ.get("fs_routes") or {}
src_uid = lambda a: (a.get("src") or {}).get("uid") if isinstance(a.get("src"), dict) else None   # noqa: E731
border = dict((src_uid(A[int(k) - 1]), A[int(k) - 1]["id"]) for k, r in FR.items() if r.get("how") == "fs_border")
DEP = collections.defaultdict(set)
for k, r in FR.items():
    a = A[int(k) - 1]
    if r.get("how") == "fs_inner_branch" and src_uid(a) in border and uof[border[src_uid(a)]] != uof[a["id"]]:
        DEP[uof[a["id"]]].add(uof[border[src_uid(a)]])
for r, ids in UNITS.items():
    print("  FACT  UNIT {0}: {1} actions {2}; depends on {3}".format(r, len(ids), [POS[i] for i in ids], sorted(DEP[r])), flush=True)


def sub_plan(ids):
    keep = [a for a in A if a["id"] in ids]
    fr = {}
    for k, a in enumerate(keep, 1):
        o = POS[a["id"]]
        if str(o) in FR:
            fr[str(k)] = FR[str(o)]
    return keep, fr


def x10(ids, start):
    keep, fr = sub_plan(ids)
    ops = SX.compile_plan({"actions": keep, "finalized": {"fs_routes": fr}})
    cps = sorted(set([0, len(ops)]) | set(k for k, o in enumerate(ops, 1) if o["kind"] in SX.BIND_KINDS))
    return dict(SPR.x10_model_peak([o["kind"] for o in ops], cps, model=MODEL, start_mb=start), ops=len(ops))


GROWTH, OP0, LOAD_B = v("load_growth_mb_per_op"), v("op0_read_mb"), float(MODEL["load_by_vi"][GF["md5"]]["value"])
rows = []
U = list(UNITS)
for n in range(1, len(U)):
    for combo in itertools.combinations(U, n):
        Sa = set(combo)
        if any(not DEP[u] <= Sa for u in Sa):
            continue
        ia = set(i for u in Sa for i in UNITS[u])
        ib = set(a["id"] for a in A) - ia
        xa = x10(ia, sB)
        load_a = round(LOAD_B + GROWTH * xa["N"], 1)
        xb = x10(ib, round(load_a + OP0, 1))
        rows.append((max(xa["peak_mb"], xb["peak_mb"]), len(ia), sorted(POS[i] for i in ia), xa, xb, load_a))
rows.sort(key=lambda r: (r[0], r[1], r[2]))
for r in rows:
    print("  CUT  a actions {0} | a N {1} BIND {2} R {3} start {4} peak {5} | a predicted load {6} | b N {7} BIND {8} R {9} start {10} "
          "peak {11} | larger {12}".format(r[2], r[3]["N"], r[3]["bind"], r[3]["R"], r[3]["start_mb"], r[3]["peak_mb"], r[5], r[4]["N"],
                                         r[4]["bind"], r[4]["R"], r[4]["start_mb"], r[4]["peak_mb"], r[0]), flush=True)
FAIL_ABOVE = v("fail_above_mb")
BEST = rows[0] if rows else None
gate("S2 {0} unit(s), {1} dependency-closed cut(s) scored; best: a {2} actions, b {3}; larger X10 {4} <= {5} (a {6} at start {7}; b {8} at "
     "start {9} = a's predicted load {10} + op-0 {11})".format(len(U), len(rows), BEST and len(BEST[2]), BEST and 39 - len(BEST[2]),
                                                              BEST and BEST[0], FAIL_ABOVE, BEST and BEST[3]["peak_mb"], sB,
                                                              BEST and BEST[4]["peak_mb"], BEST and BEST[4]["start_mb"], BEST and BEST[5], OP0),
     BEST and BEST[0] <= FAIL_ABOVE and len(U) == 5)
if not (BEST and BEST[0] <= FAIL_ABOVE):
    finish()
IA = set(A[k - 1]["id"] for k in BEST[2])
AA, AB = [a for a in A if a["id"] in IA], [a for a in A if a["id"] not in IA]
bad = [(a["id"], s) for a in AB for s in syms(a) if s in DEF and DEF[s] in IA]
TOP = dict((k, copy.deepcopy(REFP[k])) for k in ("schema", "context", "open_rows") if k in REFP)   # as plan_ring_p3b_split.py:92
PAI = os.path.join(B, "plan_ring_p3b2a_in.json")
json.dump(dict(TOP, stage="ring_p3b2a", goal="RING P3b-2 session a (card 133-3, PD283(c)): actions {0} of plan_ring_p3b2.json 04204133 "
               "({1}) on P3b-1's real graph + carried FS map".format(BEST[2], md5(REF)), base={"path": rel(FSM), "md5": md5(FSM)}, actions=AA),
          open(PAI, "w", encoding="utf-8"), indent=1)
SA = SS.simulate(PAI, FSM, plan_out_dir=B, log=lambda *x: None, route_check=True)
PA = os.path.join(B, "plan_ring_p3b2a.json")
pa = J(PA)
rc = (pa.get("finalized") or {}).get("route_check") or {}
unb = [x for x in rc.get("rows") or [] if "unbound" in json.dumps(x).lower()]
END16 = sorted(FZ["end_cdiff_rows"])
gate("S3 a ({0} actions) FINAL on the fsmap base, route check {1} ({2} rows, {3} unbound), fs_routes {4}, end cdiff == 16 rows, b names "
     "nothing a creates".format(len(AA), rc.get("status"), len(rc.get("rows") or []), len(unb), len((pa.get("finalized") or {}).get("fs_routes") or {})),
     SA["failed"] is None and SA["final"] and rc.get("status") == "PASS" and not unb and sorted(SA["end_cdiff_rows"] or []) == END16 and not bad,
     {"failed": SA["failed"], "final": SA["final"], "bad": bad, "md5": md5(PA)})
if not SA["final"]:
    finish()
ENDA = J(SA["steps"][-1]["file"]["path"])["state"]
PROVB = os.path.join(B, "sim", "ring_p3b2b_base_provisional.json")
json.dump(ENDA, open(PROVB, "w", encoding="utf-8"), separators=(",", ":"), default=str)
PBI = os.path.join(B, "plan_ring_p3b2b_in.json")
json.dump(dict(TOP, stage="ring_p3b2b", goal="RING P3b-2 session b (card 133-3, PD283(c)): actions {0} of plan_ring_p3b2.json 04204133 on "
               "session a's END graph (provisional until a's artefact exists; stage_prerun --rebase)".format(
                   sorted(POS[a["id"]] for a in AB)),
               base={"path": rel(PROVB), "md5": md5(PROVB), "provisional": True, "sim_of": {"plan": rel(PA), "md5": md5(PA)}}, actions=AB),
          open(PBI, "w", encoding="utf-8"), indent=1)
gate("S4a b input validates (stageplan/1, provisional baseref)", P.validate_obj(J(PBI))[0], P.validate_obj(J(PBI)))
SB = SS.simulate(PBI, PROVB, plan_out_dir=B, log=lambda *x: None, route_check=False)
PB = os.path.join(B, "plan_ring_p3b2b.json")
gate("S4 b ({0} actions) FINAL on a's simulated end (provisional; route check after --rebase, PD264(b)), end cdiff == 16, no created uid "
     "reused".format(len(AB)), SB["failed"] is None and SB["final"] and sorted(SB["end_cdiff_rows"] or []) == END16
     and not (set(J(SB["steps"][-1]["file"]["path"])["state"]["sym"].values()) & set(ENDA["sym"].values()) - set([None])),
     {"failed": SB["failed"], "final": SB["final"], "md5": md5(PB)})
if not SB["final"]:
    finish()
ENDB = J(SB["steps"][-1]["file"]["path"])["state"]
ENDR = J(FZ["step_files"][-1]["path"])["state"]


def shape(st):
    objs = st["objs"]
    wires = set(r["wire_uid"] for r in st["terminals"] if r["wire_uid"])
    new_cls = collections.Counter(o["class"] for o in objs if int(o["uid"]) < 0)
    new_term = collections.Counter((r["owner_class"], r["term_name"], bool(r["is_source"]), r["term_class"], bool(r["wire_uid"]))
                                   for r in st["terminals"] if int(r["owner_uid"]) < 0)
    base_w = sorted((r["term_uid"], bool(r["wire_uid"])) for r in st["terminals"] if int(r["term_uid"]) > 0)
    return {"objects": len(objs), "owners": len(set(r["owner_uid"] for r in st["terminals"])), "terminals": len(st["terminals"]),
            "wires": len(wires), "new_classes": dict(new_cls), "new_term_sig": new_term, "base_wired": base_w}


SR, S2 = shape(ENDR), shape(ENDB)
cnt = lambda s: dict((k, s[k]) for k in ("objects", "owners", "terminals", "wires"))   # noqa: E731
gate("S5 a then b == 04204133's end: cdiff 16, object/owner/terminal/wire counts, created classes, created-terminal signatures, base "
     "terminals' wired state", sorted(SB["end_cdiff_rows"]) == END16 and all(SR[k] == S2[k] for k in SR),
     {"ref": cnt(SR), "split": cnt(S2), "diff": [k for k in SR if SR[k] != S2[k]], "new_classes": S2["new_classes"]})
SAMP, E1 = J(os.path.join(B, "census_samples.json")), J(EXP1)


def pred(plan_path, graph_path, start, start_cite, part):
    pl, g = J(plan_path), J(graph_path)
    fz = pl["finalized"]
    end = J(fz["step_files"][-1]["path"])["state"]
    dd = dict(("new:" + a["as"], a["id"]) for a in pl["actions"] if a["op"] == "create" and a.get("as"))
    born = dict((int(u), dd.get(s)) for s, u in end["sym"].items())
    bo = set(int(r["owner_uid"]) for r in g["terminals"])
    unw = sorted("{0} '{1}' ({2} #{3})".format(born.get(int(r["owner_uid"]), "?"), r["term_name"], r["owner_class"], r["owner_uid"])
                 for r in end["terminals"] if int(r["owner_uid"]) not in bo and not r["is_source"] and not r["wire_uid"])
    rep = CPR.predict(pl, {}, SAMP)
    ops = SX.compile_plan(pl)
    bind = sorted(k for k, o in enumerate(ops, 1) if o["kind"] in SX.BIND_KINDS)
    cps = sorted(set([0, len(ops)]) | set(bind))
    mp = SPR.x10_model_peak([o["kind"] for o in ops], cps, model=MODEL, start_mb=start)
    el = {"bed_total": E1["total"], "removed": {}, "new_items_predicted": 0, "predicted_total": E1["total"], "base_file": rel(EXP1),
          "unwired_created_sinks": unw, "checked": part == "b",
          "class_range": "tools/bench/errorlist_expect_p3b2ab.json (this script, S7) - the step's FINAL file only (session b)"}
    d = {"schema": "ring-p3b-pred/1", "card": "133-3", "note": "P3b-2 session {0} (PD283(c)); {1}".format(part, "base = P3b-1's real graph + "
         "carried FS map" if part == "a" else "PROVISIONAL base = session a's simulated end; regenerate after stage_prerun --rebase onto a's saved file"),
         "plan": {"path": rel(plan_path), "md5": md5(plan_path)}, "graph": {"path": rel(graph_path), "md5": md5(graph_path)},
         "bed": g.get("vi"), "bed_md5": g.get("md5"), "census": dict(rep["derived"]), "census_overall": rep["overall"],
         "census_unpredicted": [pl["actions"][k - 1]["id"] for k in rep["unpredicted"]],
         "census_rows": [dict((k, r[k]) for k in ("k", "id", "op", "variant", "delta", "verdict")) for r in rep["rows"]],
         "ops": [o["kind"] for o in ops], "cdiff_rows": sorted(fz["end_cdiff_rows"]), "errorlist": el,
         "readback": J(os.path.join(B, "plan_ring_p3b2_pred.json")).get("readback"),
         "memory_pred": {"card": "133-3", "checkpoints": cps, "R": mp["R"], "N": mp["N"], "bind_ops": bind, "op_kinds": [o["kind"] for o in ops],
                         "start_mb": mp["start_mb"], "start_cite": start_cite, "peak_mb": mp["peak_mb"], "fail_above_mb": mp["fail_above_mb"],
                         "below_fail": mp["ok"], "model": {"path": rel(SPR.MEMORY_MODEL), "md5": md5(SPR.MEMORY_MODEL)},
                         "how": "stage_prerun.x10_model_peak on the compiled plan, checkpoints {0, len} | BIND, measured start of the input VI"},
         "summary": {"path": fz["summary"]["path"], "md5": fz["summary"]["md5"]}}
    po = plan_path[:-5] + "_pred.json"
    json.dump(d, open(po, "w", encoding="utf-8"), indent=1)
    return po, d


poa, da = pred(PA, FSM, sB, cB, "a")
pob, db = pred(PB, PROVB, BEST[4]["start_mb"], "PREDICTED: a's load {0} = {1} + {2} x N_a {3} (load_growth_mb_per_op) + op-0 {4}; re-check "
               "with the MEASURED load of a's saved file before b's prerun (PD283(c))".format(BEST[5], LOAD_B, GROWTH, BEST[3]["N"], OP0), "b")
for tag, d in (("a", da), ("b", db)):
    mp = d["memory_pred"]
    print("  FACT  {0} pred {1}: ops {2}; census {3} unpredicted {4}; X10 N {5} BIND {6} R {7} start {8} peak {9}; unwired created sinks {10}".format(
        tag, d["plan"]["md5"][:8], dict(collections.Counter(d["ops"])), d["census"], d["census_unpredicted"], mp["N"], len(mp["bind_ops"]),
        mp["R"], mp["start_mb"], mp["peak_mb"], d["errorlist"]["unwired_created_sinks"]), flush=True)
gate("S6 preds written: ops == compile of each plan (each action once); memory_pred == the S2 score; both <= 690",
     all(sorted(n for o in SX.compile_plan(J(pp)) for n in o["acts"]) == list(range(1, len(J(pp)["actions"]) + 1)) for pp in (PA, PB))
     and da["memory_pred"]["peak_mb"] == BEST[3]["peak_mb"] and db["memory_pred"]["peak_mb"] == BEST[4]["peak_mb"]
     and da["memory_pred"]["below_fail"] and db["memory_pred"]["below_fail"], [da["memory_pred"]["peak_mb"], db["memory_pred"]["peak_mb"]])

# ---- S7 Error List class range for the step's FINAL file: errorlist_expect_p3b2.py's rule, step_00 of a -> last step of b
LOOSE, NOSRC = "wirewirehaslooseends", "thiswireconnectsoneormoredatasinksbuthasnosource"


def prof(terms):
    w = collections.defaultdict(lambda: [0, 0])
    for t in terms:
        if t.get("wire_uid") not in (None, 0, -1):
            w[int(t["wire_uid"])][0 if t.get("is_source") else 1] += 1
    return w


def debit(t0, t1):
    b, e = prof(t0), prof(t1)
    cert, unc = collections.Counter(), collections.Counter()
    for k in sorted(set(b) - set(e)):
        s_, n_ = b[k]
        if k < 0:
            continue
        if s_ and not n_:
            cert[LOOSE] -= 1
        elif n_ and not s_:
            cert[NOSRC] -= 1
        else:
            unc[LOOSE] -= 1
    for k in sorted(set(e) - set(b)):
        if not e[k][0] or not e[k][1]:
            cert[LOOSE if e[k][0] else NOSRC] += 1
    meas = E1["per_class_read"]
    lo, hi = dict(meas), dict(meas)
    for c, x in cert.items():
        lo[c] = lo.get(c, 0) + x
        hi[c] = hi.get(c, 0) + x
    for c, x in unc.items():
        lo[c] = lo.get(c, 0) + x
    return {"per_class_lo": lo, "per_class_hi": hi, "total_lo": sum(lo.values()), "total_hi": sum(hi.values()),
            "lost": sorted(set(b) - set(e))}


st0 = lambda d: J(sorted(f for f in (os.path.join(B, "sim", d, x) for x in os.listdir(os.path.join(B, "sim", d))) if os.path.basename(f).startswith("step_"))[0])["state"]["terminals"]   # noqa: E731
ab = debit(st0("ring_p3b2a"), ENDB["terminals"])
un = debit(st0("ring_p3b2"), ENDR["terminals"])
OUT = os.path.join(B, "errorlist_expect_p3b2ab.json")
json.dump(dict(ab, schema="errorlist-expect-computed/1", card="133-3", stage="D1_ring_p3b2 (sessions a+b, final file)", base_file=rel(EXP1),
               rule="errorlist_expect_p3b2.py RULE (lines 3-12), applied from sim/ring_p3b2a step_00 to sim/ring_p3b2b last step",
               plans={"a": {"path": rel(PA), "md5": md5(PA)}, "b": {"path": rel(PB), "md5": md5(PB)}}, unsplit=un),
          open(OUT, "w", encoding="utf-8"), indent=1)
gate("S7 Error List range of the FINAL file: total {0}..{1}, loose ends {2}..{3} (split a.step_00 -> b.last) == the unsplit 04204133 sim's "
     "{4}..{5}".format(ab["total_lo"], ab["total_hi"], ab["per_class_lo"].get(LOOSE), ab["per_class_hi"].get(LOOSE), un["total_lo"], un["total_hi"]),
     (ab["total_lo"], ab["total_hi"], ab["per_class_lo"], ab["per_class_hi"]) == (un["total_lo"], un["total_hi"], un["per_class_lo"], un["per_class_hi"]),
     {"lost_split": ab["lost"], "lost_unsplit": un["lost"]})
arts.extend({"path": rel(p), "md5": md5(p)} for p in (PAI, PA, poa, PROVB, PBI, PB, pob, OUT))
finish()
