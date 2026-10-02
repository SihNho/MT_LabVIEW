r"""diag_c134_1_finalize_b - card 134-1 (d) (PD287(c)): OFFLINE (no LabVIEW, no COM). Finalize P3b-2 session b DIRECTLY on the
REAL graph of session a's kept in-between file read with Flat Sequence frames (diag_c134_1_graph.py -> graph_ring_p3b2a_fs_<ts>.json,
argv[1]) - not rebased from a's simulated end, so no simulator uid of a's objects is left to bind (133-6's -30).
WHAT EXISTED FIRST (reused, not rewritten): plan_ring_p3b_split_p3b2.py S4/S5/pred() (stagesim.simulate + the end-shape compare + the
pred file fields), stage_prerun.x10_start / x10_model_peak, census_predict.predict. b's 18 actions are copied UNCHANGED from
plan_ring_p3b2b_in.json (1451ba90's input); only `base` changes (rule 1a, PD287(c)).
PREDICTION: F0 b's actions name no negative (simulator) uid; F1 stagesim FINAL on the real graph, route check PASS, 0 unbound;
F2 end cdiff == plan_ring_p3b2.json 04204133's 16 rows; F3 end object / terminal / wire counts == 04204133's end (10334 / 5933 /
1974) or the diff listed; F4 pred written, ops == compile, X10 start = a's MEASURED load (memory_model load_by_vi) + op-0, peak <= 690.
    py tools/bgrun.py --material --max-min 6 --log tools/bench/diag_c134_1_finalize_b.log -- py -u tools/bench/diag_c134_1_finalize_b.py <graph>
CARD 135-2 (docs/violation-decisions.md 2026-10-02 12:2x device; PD294(c)): (1) FC base-graph COMPLETENESS gate
(stagesim.completeness_gate, uses = b's actions) runs BEFORE anything is written or simulated; (2) every file this script writes
(plan b, _in, _pred, the provisional copy, the stage's sim step dir) is snapshotted by stagesim.WriteGuard and RESTORED byte for byte
when any gate FAILS - the plan files are written only on success (135-1 wrote fae25fb3 / c1c50529 / 509554bb and 19 step files
despite F3 FAIL, launch_p3b2_c135_f.log:13). `--bench DIR` (self-tests only) reads/writes the plan files in DIR and simulates
into DIR/sim instead of tools/bench (selftest_c135_2_device.py)."""
import collections, copy, hashlib, json, os, shutil, sys                                     # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P, stagesim as SS, stagexec as SX, census_predict as CPR, stage_prerun as SPR   # noqa: E402,E401
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                    # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                       # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
ok, arts = [], []
SIM_OUT = SS.SIM_ROOT
if "--bench" in sys.argv:
    B = os.path.abspath(sys.argv[sys.argv.index("--bench") + 1])
    SIM_OUT = os.path.join(B, "sim")
GUARD = []


def gate(name, c, det=""):
    ok.append((name, bool(c)))
    print("{0}  {1}  {2}".format("PASS" if c else "FAIL", name, str(det)[:1500]), flush=True)


def finish():
    np_, nf = sum(1 for _n, c in ok if c), sum(1 for _n, c in ok if not c)
    if nf and GUARD:
        print("  FACT  WRITE-GUARD: a gate FAILED -> plan files + sim step dir restored, bytes unchanged = {0}".format(
            GUARD[0].restore()), flush=True)
        del arts[:]
    print(P.result_line(P.make_result(np_, nf, next((n for n, c in ok if not c), None), arts)), flush=True)
    sys.exit(1 if nf else 0)


def _restore_on_exception(t, v, tb):
    if GUARD:
        print("  FACT  WRITE-GUARD: exception -> plan files + sim step dir restored, bytes unchanged = {0}".format(
            GUARD[0].restore()), flush=True)
    sys.__excepthook__(t, v, tb)


sys.excepthook = _restore_on_exception
G = os.path.abspath(sys.argv[1])
REF = os.path.join(B, "plan_ring_p3b2.json")
PBI, PB = os.path.join(B, "plan_ring_p3b2b_in.json"), os.path.join(B, "plan_ring_p3b2b.json")
PBI_OLD = os.path.join(B, "plan_ring_p3b2b_in_provisional_c134_1.json")
EXP1 = os.path.join(B, "errorlist_expected_D1_ring_p3b1_20261002_060910.json")
PINS = {REF: "04204133d6c55929f368ec3761f70445", PB: "1451ba90aadc594fe74f97793eb04e92"}
gate("F-1 inputs md5 == card (plan_ring_p3b2 04204133, plan_ring_p3b2b 1451ba90)", all(md5(p) == m for p, m in PINS.items()),
     dict((rel(p), md5(p)) for p in PINS))
if not ok[-1][1]:
    finish()
GJ, REFP = J(G), J(REF)
FZ = REFP["finalized"]
STAGE = J(PBI).get("stage") or "ring_p3b2b"
GUARD.append(SS.WriteGuard(files=(PBI, PB, PBI_OLD, os.path.join(B, "plan_ring_p3b2b_pred.json")), dirs=(os.path.join(SIM_OUT, STAGE),)))
_old_acts = J(PBI_OLD if os.path.isfile(PBI_OLD) else PBI)["actions"]
CG = SS.completeness_gate(GJ, uses={"actions": _old_acts})
gate("FC base-graph completeness (violation-decisions 2026-10-02 12:2x): {0} FS / {1} frames, UNMEASURED {2} unused".format(
    CG.get("fs"), CG.get("frames"), CG.get("unmeasured")), CG["status"] == "PASS",
    dict((k, CG.get(k)) for k in ("status", "why", "bad_owner", "stuck", "inferred", "used") if CG.get(k)))
if CG["status"] != "PASS":
    finish()
if not os.path.isfile(PBI_OLD):
    shutil.copyfile(PBI, PBI_OLD)                                     # the provisional input, kept verbatim
old = J(PBI_OLD)
AB = copy.deepcopy(old["actions"])


def negs(x):
    if isinstance(x, bool):
        return []
    if isinstance(x, int):
        return [x] if x < 0 else []
    if isinstance(x, dict):
        return [n for v in x.values() for n in negs(v)]
    if isinstance(x, list):
        return [n for v in x for n in negs(v)]
    return []


gate("F0 b's {0} actions name no negative (simulator) uid".format(len(AB)), not negs(AB), negs(AB)[:10])
new_in = dict((k, copy.deepcopy(v)) for k, v in old.items() if k not in ("base", "goal", "actions"))
new_in.update(goal="RING P3b-2 session b (card 134-1, PD287(c)): the same {0} actions as {1} finalized DIRECTLY on the real graph of "
                   "session a's kept in-between file (FS frames measured)".format(len(AB), rel(PBI_OLD)),
              base={"path": rel(G), "md5": md5(G)}, actions=AB)
json.dump(new_in, open(PBI, "w", encoding="utf-8"), indent=1)
gate("F0b b input validates (stageplan/1, real base)", P.validate_obj(J(PBI))[0], P.validate_obj(J(PBI)))
SB = SS.simulate(PBI, G, out_root=SIM_OUT, plan_out_dir=B, log=lambda *x: None, route_check=True)
pb = J(PB)
rc = (pb.get("finalized") or {}).get("route_check") or {}
unb = [x for x in rc.get("rows") or [] if "unbound" in json.dumps(x).lower()]
END16 = sorted(FZ["end_cdiff_rows"])
gate("F1 b FINAL on the real graph, route check {0} ({1} rows, {2} unbound), fs_routes {3}".format(
    rc.get("status"), len(rc.get("rows") or []), len(unb), len((pb.get("finalized") or {}).get("fs_routes") or {})),
    SB["failed"] is None and SB["final"] and rc.get("status") == "PASS" and not unb,
    {"failed": SB["failed"], "final": SB["final"], "md5": md5(PB), "unbound": unb[:5]})
gbz = (pb.get("finalized") or {}).get("fs_border_gate") or {}        # card 134-2 (PD288(b)): gate B scoped, in simulate
gate("FB gate B scoped: {0} UNMEASURED border tunnel(s) listed, none used by an action / route / entry".format(
    len(gbz.get("unmeasured") or [])), gbz.get("status") == "PASS", gbz)
if not SB["final"]:
    finish()
gate("F2 end cdiff == 04204133's 16 rows", sorted(SB["end_cdiff_rows"] or []) == END16,
     {"extra": sorted(set(SB["end_cdiff_rows"] or []) - set(END16)), "missing": sorted(set(END16) - set(SB["end_cdiff_rows"] or []))})
ENDB, ENDR = J(SB["steps"][-1]["file"]["path"])["state"], J(FZ["step_files"][-1]["path"])["state"]


def cnt(st):
    return {"objects": len(st["objs"]), "owners": len(set(r["owner_uid"] for r in st["terminals"])), "terminals": len(st["terminals"]),
            "wires": len(set(r["wire_uid"] for r in st["terminals"] if r["wire_uid"]))}


CR, CB = cnt(ENDR), cnt(ENDB)
ccr, ccb = (collections.Counter(o.get("class") for o in s_["objs"]) for s_ in (ENDR, ENDB))   # card 134-2: every diff LISTED
tcr, tcb = (collections.Counter(r.get("owner_class") for r in s_["terminals"]) for s_ in (ENDR, ENDB))
gate("F3 end counts == 04204133's end {0}".format(CR), CR == CB, {
    "ref": CR, "b_on_real": CB, "diff": [k for k in CR if CR[k] != CB[k]],
    "obj_class_diff": dict((k, ccb[k] - ccr[k]) for k in set(ccr) | set(ccb) if ccb[k] != ccr[k]),
    "term_owner_class_diff": dict((k, tcb[k] - tcr[k]) for k in set(tcr) | set(tcb) if tcb[k] != tcr[k])})
# ---- pred (plan_ring_p3b_split_p3b2.py pred(), part b, start = a's MEASURED load)
SAMP, E1, MODEL = J(os.path.join(B, "census_samples.json")), J(EXP1), SPR.load_memory_model()
xs = SPR.x10_start(GJ.get("md5"), MODEL)
gate("F4a X10 start from a's MEASURED load (memory_model load_by_vi[{0}])".format(GJ.get("md5")), xs is not None, xs)
if xs is None:
    finish()
pl, fz = pb, pb["finalized"]
end = ENDB
dd = dict(("new:" + a["as"], a["id"]) for a in pl["actions"] if a["op"] == "create" and a.get("as"))
born = dict((int(u), dd.get(s)) for s, u in end["sym"].items())
bo = set(int(r["owner_uid"]) for r in GJ["terminals"])
unw = sorted("{0} '{1}' ({2} #{3})".format(born.get(int(r["owner_uid"]), "?"), r["term_name"], r["owner_class"], r["owner_uid"])
             for r in end["terminals"] if int(r["owner_uid"]) not in bo and not r["is_source"] and not r["wire_uid"])
rep = CPR.predict(pl, {}, SAMP)
ops = SX.compile_plan(pl)
bind = sorted(k for k, o in enumerate(ops, 1) if o["kind"] in SX.BIND_KINDS)
cps = sorted(set([0, len(ops)]) | set(bind))
mp = SPR.x10_model_peak([o["kind"] for o in ops], cps, model=MODEL, start_mb=xs[0])
prev = J(os.path.join(B, "plan_ring_p3b2b_pred.json"))
el = dict(prev["errorlist"], unwired_created_sinks=unw)
d = {"schema": "ring-p3b-pred/1", "card": "134-1", "note": "P3b-2 session b (PD287(c)): base = the REAL graph of session a's kept in-between "
     "file read with FS frames (diag_c134_1_graph.py); finalized directly on it, not rebased",
     "plan": {"path": rel(PB), "md5": md5(PB)}, "graph": {"path": rel(G), "md5": md5(G)},
     "bed": GJ.get("vi"), "bed_md5": GJ.get("md5"), "census": dict(rep["derived"]), "census_overall": rep["overall"],
     "census_unpredicted": [pl["actions"][k - 1]["id"] for k in rep["unpredicted"]],
     "census_rows": [dict((k, r[k]) for k in ("k", "id", "op", "variant", "delta", "verdict")) for r in rep["rows"]],
     "ops": [o["kind"] for o in ops], "cdiff_rows": sorted(fz["end_cdiff_rows"]), "errorlist": el,
     "readback": prev.get("readback"),
     "memory_pred": {"card": "134-1", "checkpoints": cps, "R": mp["R"], "N": mp["N"], "bind_ops": bind, "op_kinds": [o["kind"] for o in ops],
                     "start_mb": mp["start_mb"], "start_cite": xs[1], "peak_mb": mp["peak_mb"], "fail_above_mb": mp["fail_above_mb"],
                     "below_fail": mp["ok"], "model": {"path": rel(SPR.MEMORY_MODEL), "md5": md5(SPR.MEMORY_MODEL)},
                     "how": "stage_prerun.x10_model_peak on the compiled plan, checkpoints {0, len} | BIND, start = x10_start(a's file md5)"},
     "summary": {"path": fz["summary"]["path"], "md5": fz["summary"]["md5"]}}
po = os.path.join(B, "plan_ring_p3b2b_pred.json")
json.dump(d, open(po, "w", encoding="utf-8"), indent=1)
print("  FACT  pred {0}: ops {1}; census {2} unpredicted {3}; X10 N {4} BIND {5} R {6} start {7} ({8}) peak {9}; unwired created sinks {10}".format(
    d["plan"]["md5"][:8], dict(collections.Counter(d["ops"])), d["census"], d["census_unpredicted"], mp["N"], len(bind), mp["R"],
    mp["start_mb"], xs[1], mp["peak_mb"], unw), flush=True)
gate("F4 pred written: ops == compile (each action once); X10 peak {0} <= {1}".format(mp["peak_mb"], mp["fail_above_mb"]),
     sorted(n for o in ops for n in o["acts"]) == list(range(1, len(pl["actions"]) + 1)) and mp["ok"], mp["peak_mb"])
arts.extend({"path": rel(p), "md5": md5(p)} for p in (PBI, PB, po))
finish()
