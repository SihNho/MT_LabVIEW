# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_159-e1-1.md
# ---
r"""selftest_c159_cen2_ends - card 159-e1-1 (docs/d1/ring-p5b.md PD389(b)), OFFLINE: no LabVIEW, no COM. Under test (called, not copied):
stagekit.RingSession.gate_cen2 / Stage.census_gate(judged=) / cen2_wire_ends / wire_end_pairs / stub_sides / sim_census_snapshot.
Data: real end = tools/bench/graph_ring_p5s02a_20261010_032547.json (read of 94ffff94); base = the plan's finalized base graph_ring_p5s01
6716c499; sim end = plan_ring_p5s02a.json finalized.step_files[-1] (sim/ring_p5s02a/step_23_wire.json b1892ad9), the plan md5 4284c22a
that the p5s02a dry record pins (prerun_records.jsonl:1073). Real-run census proxy = sim_census_snapshot of a graph (objs + term rows + wires).
Pre-edit gate = stagekit bytes 9cd8822e kept as selftest_c159_cen2_ends_stagekit_9cd8822e.txt, imported from %TEMP%.
PREDICTION: P0 pins; C1 end-pair CEN2 (gate_cen2, real-run path) PASS and the old uid CEN2 reads Wire 11 sim / 12 real; C2 real rows minus
ONE new pair (wire 31587's sink row) -> FAIL naming exactly that pair; C3 stub 24091 RECORDED sim-only (a FACT line), CEN2 still PASS;
C4 non-Wire classes: new gate diff == pre-edit gate diff without Wire, verdicts equal, on the pred and on a SelectorTunnel+1 fixture."""
import contextlib, hashlib, importlib.util, io, json, os, shutil, sys, tempfile  # noqa: E401

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402
import stagekit as K  # noqa: E402

G = {"pass": 0, "fail": 0, "first": None}
B = "tools/bench/"
md5 = lambda p: hashlib.md5(open(os.path.join(ROOT, p), "rb").read()).hexdigest()   # noqa: E731
jl = lambda p: json.load(open(os.path.join(ROOT, p), encoding="utf-8"))              # noqa: E731


def gate(label, ok, detail=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:900]), flush=True)


PINS = {B + "graph_ring_p5s02a_20261010_032547.json": "7ac24924", B + "graph_ring_p5s01_20261009_125622.json": "6716c499",
        B + "plan_ring_p5s02a.json": "4284c22a", B + "sim/ring_p5s02a/step_23_wire.json": "b1892ad9", B + "plan_ring_p5s02a_pred.json": "ed84b5fd",
        B + "selftest_c159_cen2_ends_stagekit_9cd8822e.txt": "9cd8822e"}
got = dict((p, md5(p)[:8]) for p in PINS)
gate("P0 input pins (real graph, base graph, plan, sim end, pred, pre-edit stagekit)", got == PINS, got)
CD = os.path.join(r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev", "D1_ring_")   # read as bytes only, never opened in LabVIEW
VIS = {"p5s02a_20261010_023239": "94ffff94", "p4s09_20261009_060515": "eb1d0f31", "p5s01a_20261009_101219": "2482fe7b", "p5s01_20261009_124542": "7f2582ae"}
vi_md5 = lambda: dict((k, md5(CD + k + ".vi")[:8]) for k in VIS)                     # noqa: E731
V0 = vi_md5()
gate("V0 claudeDev VI pins before (94ffff94, s09, P5-1a, P5-1)", V0 == VIS, V0)
P, PRED = jl(B + "plan_ring_p5s02a.json"), jl(B + "plan_ring_p5s02a_pred.json")
BASE, REALG = jl(P["finalized"]["base"]["path"]), jl(B + "graph_ring_p5s02a_20261010_032547.json")
SIM_END, S0 = jl(P["finalized"]["step_files"][-1]["path"])["state"], jl(P["finalized"]["step_files"][0]["path"])["state"]
REAL = K.pure("vigraph").dedupe_rows(REALG["terminals"])[0]                          # the backend's read is deduped (stagexec LVBackend.read)
SRC = tuple(PRED["census"])
c0, c1 = dict(K.sim_census_snapshot(BASE, SRC)), dict(K.sim_census_snapshot(REALG, SRC))   # plain dicts: real-run path of census_gate
tmp = tempfile.mkdtemp(prefix="c159_e1_1_")
shutil.copy(os.path.join(HERE, "selftest_c159_cen2_ends_stagekit_9cd8822e.txt"), os.path.join(tmp, "stagekit_pre.py"))
spec = importlib.util.spec_from_file_location("stagekit_pre", os.path.join(tmp, "stagekit_pre.py"))
PRE = importlib.util.module_from_spec(spec)
spec.loader.exec_module(PRE)
st = K.Stage(PRED["bed"], PRED["bed_md5"], "c159_e1_1", out_json=os.path.join(tmp, "st.json"))
REC = []
st.gate = lambda label, ok, detail="", fatal=False, kind=None: REC.append((label, bool(ok), detail)) or ok


def ring(real_rows, pred=PRED):
    rs = object.__new__(K.RingSession)
    rs.P, rs.PRED, rs.SRC, rs.DRY, rs.pred_path, rs.BASE, rs.SIM_END, rs.real = P, pred, SRC, False, B + "plan_ring_p5s02a_pred.json", BASE, SIM_END, real_rows
    return rs


def run_gate(fn):
    REC[:] = []
    del st.facts[:]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        fn()
    return REC[-1], list(st.facts), buf.getvalue()


# C1 -----------------------------------------------------------------------------------------------------------------------
(lab, ok, det), facts, _o = run_gate(lambda: ring(REAL).gate_cen2(st, c0, c1))
sim_w = sum(1 for u, c in K.sim_census_snapshot(SIM_END, SRC).items() if c == "Wire" and u not in K.sim_census_snapshot(S0, SRC))
wobj = lambda gr: set(o["uid"] for o in gr["objs"] if o.get("class") == "Wire")      # noqa: E731
real_w = len(wobj(REALG) - wobj(BASE))
(_l, ok_old, det_old), _f, _o2 = run_gate(lambda: PRE.Stage.census_gate(st, lab, c0, c1, PRED["census"]))
print("FACT C1 new gate detail: {0}".format(json.dumps(det, default=str)[:1500]), flush=True)
print("FACT C1 pre-edit gate on the same data: ok {0} diff {1}".format(ok_old, det_old.get("diff (measured, declared)")), flush=True)
print("FACT C1 " + " | ".join(f for f in facts if f.startswith(("UID-REUSE", "RECORD"))), flush=True)
jw = det.get("judged by ends (PD389(b))", {}).get("Wire", {})
gate("C1 end-pair CEN2 PASS on 94ffff94 vs the p5s02a sim end (new pairs sim {0} == real {1}); old uid CEN2 Wire sim {2} / real {3} (want 11 / 12)".format(
    jw.get("new_pairs_sim"), jw.get("new_pairs_real"), sim_w, real_w), ok and sim_w == 11 and real_w == 12 and any(f.startswith("UID-REUSE") for f in facts), lab)

# C2 -----------------------------------------------------------------------------------------------------------------------
drop = [r for r in REAL if r.get("wire_uid") == 31587 and not r.get("is_source")]
cut = [r for r in REAL if r not in drop]
bt = dict((r["term_uid"], r["owner_class"]) for r in K.pure("vigraph").dedupe_rows(BASE["terminals"])[0])
bf = set(r.get("frame_diagram") or 0 for r in BASE["terminals"]) | set(int(k) for k in BASE.get("owners") or {})
gone = sorted((K.wire_end_pairs(REAL, bt, bf)[0] - K.wire_end_pairs(cut, bt, bf)[0]).elements(), key=str)
(lab2, ok2, det2), _f2, _o3 = run_gate(lambda: ring(cut).gate_cen2(st, c0, c1))
named = det2.get("judged by ends (PD389(b))", {}).get("Wire", {}).get("only_sim")
gate("C2 one real pair removed (wire 31587 sink row, {0} row(s)) -> FAIL naming exactly it: removed {1}; only_sim {2}".format(len(drop), gone, named),
     len(drop) == 1 and not ok2 and len(gone) == 1 and named == gone)

# C3 -----------------------------------------------------------------------------------------------------------------------
e = K.cen2_wire_ends(BASE["terminals"], SIM_END["terminals"], REAL, BASE.get("owners") or {})
rec = [f for f in facts if f.startswith("RECORD CEN2") and "wire 24091 " in f]
gate("C3 sim-only source-only stub 24091 RECORDED (FACT line), not counted: stubs {0}; CEN2 C1 PASS {1}".format(e["stubs"], ok),
     [d["wire"] for d in e["stubs"]["sim_only"]] == [24091] and not e["stubs"]["real_only"] and len(rec) == 1 and ok, rec)

# C4 -----------------------------------------------------------------------------------------------------------------------
for tag, pr in (("pred as is", PRED), ("SelectorTunnel+1", dict(PRED, census=dict(PRED["census"], SelectorTunnel=PRED["census"]["SelectorTunnel"] + 1)))):
    (_a, okn, dn), _f4, _o4 = run_gate(lambda: ring(REAL, pr).gate_cen2(st, c0, c1))
    (_b, oko, do), _f5, _o5 = run_gate(lambda: PRE.Stage.census_gate(st, _a, c0, c1, pr["census"]))   # pre-edit gate_cen2's real path
    nw = dict((c, v) for c, v in do["diff (measured, declared)"].items() if c != "Wire")
    gate("C4 {0}: non-Wire diff new {1} == pre-edit {2}; verdict new {3} / pre-edit without Wire {4}".format(
        tag, dn["diff (measured, declared)"], nw, okn, not nw), dn["diff (measured, declared)"] == nw and okn == (not nw))

gate("V1 claudeDev VI pins after == before", vi_md5() == V0, vi_md5())
print("FACT md5 stagekit {0} stagesim {1} stagexec {2} stage_prerun {3}; temp {4}".format(*[md5("tools/" + m)[:8] for m in (
    "stagekit.py", "stagesim.py", "stagexec.py", "stage_prerun.py")] + [tmp]), flush=True)
print("=== TOTALS {0} pass / {1} fail".format(G["pass"], G["fail"]), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
