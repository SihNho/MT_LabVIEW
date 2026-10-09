# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_157-a1-4.md
# ---
r"""prep_c157_a1_4_cut - card 157-a1-4 (OFFLINE, json only, no LabVIEW): planned X10 MAIN / Executor-only peak of the P5-2 all-groups plan
plan_ring_p5s02r_all.json (15da9551) cut at action 20 (end F1) and action 26 (end F3), with the CURRENT checkpoint rule.
Found before writing (docs/script-writing.md rule 8): the cut loop of prep_c156_a1_1_mk.py:411-441 is module-level (importing it runs the maker)
and its main_of (prep_c156_a1_1_lib.py:95-100) uses the OLD checkpoint rule (BIND only); no shared plan cutter exists. So this script only
CALLS: stagexec.compile_plan (stagexec.py:803), stagexec.checkpoint_ops (stagexec.py:2028 = RingSession.CHECKPOINTS, stagekit.py:1929),
stage_prerun.x10_model_peak (stage_prerun.py:2096, Executor-only) and stage_prerun.x10_gate (stage_prerun.py:2548, MAIN = Executor + the
recipe's source-counted whole-VI reads; the function behind 679.7 in diag_c157_a1_2_prerun.log:99-101). The cut is the action list ONLY:
every other key of the all-plan is copied unchanged. Cut plans are written under tools/bench/sim/ring_p5s02a_c157/cut20|cut26/ only.
PREDICTION CONTRACT: M0 pins; C23 control: the stored 23-action plan reproduces 679.7 / 674.6, R 14 / 12 (diag_c157_a1_2_prerun.log:99-100) and
its cut copy from the all-plan compiles to the same ops; CUT20 / CUT26: the cut ends at a group end and its ops cover exactly actions 1..k
(no group split); numbers printed as FACT lines; V23 the 23-plan meter without checkpoints {12}, {11,12}, {10,11,12}, one read = read_mb.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c157_a1_4_cut.log -- py -u tools/bench/prep_c157_a1_4_cut.py"""
import json, os, sys                                                                         # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for p_ in (ROOT, os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench")):
    sys.path.insert(0, p_)
import stagexec as SX, stage_prerun as SPR                                                   # noqa: E401,E402
import prep_c156_a1_1_lib as L                                                               # noqa: E402
md5, rel, J = L.md5, L.rel, L.J
B = os.path.join(ROOT, "tools", "bench")
OUTD = os.path.join(B, "sim", "ring_p5s02a_c157")
ALLF, STEP1 = os.path.join(B, "plan_ring_p5s02r_all.json"), os.path.join(B, "plan_ring_p5s02a.json")
SESS = os.path.join(B, "prep_c156_a1_1_session.json")
RECIPE = os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p5s02a.py")
WANT = {ALLF: "15da9551", os.path.join(B, "memory_model.json"): "c87d170a", os.path.join(ROOT, "tools", "stagexec.py"): "69b1a301",
        os.path.join(ROOT, "tools", "stagekit.py"): "0d8f6d25", os.path.join(ROOT, "tools", "stage_prerun.py"): "9decb20f"}
# OK groups in plan order, diag_c156_a1_1_facts.md:15; their ends are read from the session file (cut.group_ends)
GROUPS = ["A", "B", "C", "D", "E", "F1", "F2", "F3", "G", "H", "I", "J"]
gate = L.Gate(fatal_default=False)
M0 = dict((p, md5(p)) for p in WANT)
gate("M0 input md5 == card pins", all(M0[p].startswith(w) for p, w in WANT.items()), dict((os.path.basename(p), M0[p][:8]) for p in WANT), fatal=True)
P = J(ALLF)
A = P["actions"]
GEND = sorted(J(SESS)["cut"]["group_ends"])
gate("G group ends from the session file == 12 groups", len(GEND) == len(GROUPS) and GEND[-1] == len(A), GEND, fatal=True)
OWN = dict((e, g) for e, g in zip(GEND, GROUPS))
MODEL = SPR.load_memory_model()
RD = float(MODEL["read_mb"]["value"])


def meter(plan_path, kinds, cps):
    """(Executor-only dict, MAIN dict) of one run: x10_model_peak at the plan's measured start, and x10_gate's MAIN run."""
    xs = SPR.x10_plan_start(plan_path, MODEL)
    ex = SPR.x10_model_peak(kinds, list(cps), model=MODEL, start_mb=xs[0] if xs else None)
    ok, det = SPR.x10_gate(RECIPE, [{"plan": rel(plan_path), "kinds": kinds, "checkpoints": sorted(cps), "stop_after": None,
                                     "from_step": None, "error": None}], model=MODEL)
    return ex, det["runs"][0], xs


def cut(k):
    """Write the all-plan with actions 1..k under OUTD/cut<k>/ and return (path, ops)."""
    d = os.path.join(OUTD, "cut{0}".format(k))
    os.makedirs(d, exist_ok=True)
    f = os.path.join(d, "plan_ring_p5s02a_cut{0}.json".format(k))
    json.dump(dict(P, stage="ring_p5s02a_cut{0}".format(k), goal="card 157-a1-4 MEASURE ONLY: plan_ring_p5s02r_all.json actions 1..{0}".format(k),
                   actions=A[:k]), open(f, "w", encoding="utf-8"), indent=1)
    gate.ARTS.append({"path": rel(f), "md5": md5(f)})
    return f, SX.compile_plan(J(f))


# ---- C23 control: the stored step-1 plan and its cut copy
S1 = J(STEP1)
ops1 = SX.compile_plan(S1)
k1 = [o["kind"] for o in ops1]
cp1 = SX.checkpoint_ops(ops1)
ex1, mn1, xs1 = meter(STEP1, k1, cp1)
print("FACT C23 stored plan: ops {0} checkpoints {1} start {2}; Executor {3} R {4}; MAIN {5} R {6}".format(len(ops1), cp1, xs1, ex1["peak_mb"], ex1["R"], mn1["peak_mb"], mn1["R"]), flush=True)
gate("C23 control reproduces diag_c157_a1_2_prerun.log:99-100 (679.7 R14 / 674.6 R12)", (mn1["peak_mb"], mn1["R"], ex1["peak_mb"], ex1["R"]) == (679.7, 14, 674.6, 12),
     (mn1["peak_mb"], mn1["R"], ex1["peak_mb"], ex1["R"]), fatal=True)
for k in (23, 20, 26):
    f, ops = cut(k)
    kinds = [o["kind"] for o in ops]
    cps = SX.checkpoint_ops(ops)
    ex, mn, xs = meter(f, kinds, cps)
    cover = sorted(x for o in ops for x in o["acts"]) == list(range(1, k + 1))
    gate("CUT{0} ends at a group end ({1}) and its ops cover exactly actions 1..{0} (no group split)".format(k, OWN.get(k)), k in OWN and cover, (k, cover))
    prev = max([e for e in GEND if e < k] or [0])
    last = [(n, o["kind"], o["acts"]) for n, o in enumerate(ops, 1) if min(o["acts"]) > prev]
    print("FACT CUT{0}: actions {0}, ops {1}, kinds {2}; last group {3} = actions {4}..{0}, ops in it {5}".format(
        k, len(ops), kinds, OWN.get(k), prev + 1, last), flush=True)
    print("FACT CUT{0}: checkpoints {1}; start {2}; Executor-only {3} MB R {4} N {5}; MAIN {6} MB R {7} (src reads {8}); fail_above {9}".format(
        k, cps, xs, ex["peak_mb"], ex["R"], ex["N"], mn["peak_mb"], mn["R"], mn.get("src_reads"), mn["fail_above_mb"]), flush=True)
    if k == 23:
        gate("C23b the cut copy of the all-plan compiles to the stored step-1 ops and the same meter", [(o["kind"], o["acts"]) for o in ops] == [(o["kind"], o["acts"]) for o in ops1]
             and (mn["peak_mb"], ex["peak_mb"]) == (mn1["peak_mb"], ex1["peak_mb"]), (mn["peak_mb"], ex["peak_mb"]))
# ---- V23: the stored 23-plan without some move_in checkpoints
for drop in ((12,), (11, 12), (10, 11, 12)):
    c = tuple(x for x in cp1 if x not in drop)
    ex, mn, _ = meter(STEP1, k1, c)
    print("FACT V23 without {0}: checkpoints {1}; Executor-only {2} R {3}; MAIN {4} R {5}; delta MAIN vs 679.7 = {6}".format(
        drop, c, ex["peak_mb"], ex["R"], mn["peak_mb"], mn["R"], round(mn["peak_mb"] - mn1["peak_mb"], 2)), flush=True)
print("FACT one whole-VI checkpoint read = read_mb {0} MB ({1})".format(RD, MODEL["read_mb"]["cite"]), flush=True)
sys.exit(gate.result())
