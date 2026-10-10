# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_160-g1-1.md
# ---
r"""diag_c160_g1_1 - card 160-g1-1 (OFFLINE, json only, no LabVIEW): PD390(d) facts - fresh-instance MAIN per whole group of A41..A80 and the
greedy whole-group split (START_ASSUMED 603.4, MAIN <= 675, a GAP/BLOCKED group ends a step and gets no MAIN). No plan file is written.
Existing routes: the symbol / frame mapping and the compile are the calls prep_c159_c1_1_mk.py:84-122 makes (prep_c159_c1_1_lib map_symbols /
map_frames / apply_map / bound_from_cmap, stagexec.compile_plan / plan_base_owners, stage_prerun.load_creation_map); MAIN = prep_c156_a1_1_lib.main_of
(stage_prerun.x10_model_peak + 2 reads). No new logic beyond slicing ops by group.
PREDICTION CONTRACT: M0 pins (stagekit 0b5bb678, stagesim a3261b56, stagexec c4a6e0b6, stage_prerun 7605116f, plan input 56bfddd3, graph 7ac24924,
  memory_model 5b87de43); A24..A80 compiles; no op spans a group boundary; REPRO the cumulative MAIN of the 159 log (op kinds and MAIN at the I and J
  ends 678.3 / 694.4, prep_c159_c1_1_mk.log:63,71) on today's bytes; fresh MAIN printed for I, J, I+J; U pins unchanged.
    py tools/bgrun.py --material --max-min 10 --log tools/bench/diag_c160_g1_1.log -- py -u tools/bench/diag_c160_g1_1.py"""
import copy, json, os, re, sys                                                                # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for p_ in (ROOT, os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench")):
    sys.path.insert(0, p_)
import stagexec as SX, stage_prerun as SPR                                                     # noqa: E401,E402
import prep_c156_a1_1_lib as L                                                                 # noqa: E402
import prep_c159_c1_1_lib as M                                                                 # noqa: E402
md5, rel, J = L.md5, L.rel, L.J
B = os.path.join(ROOT, "tools", "bench")
GRAPH = os.path.join(B, "graph_ring_p5s02a_20261010_032547.json")
RIN, PA, PASESS = os.path.join(B, "plan_ring_p5s02r_in.json"), os.path.join(B, "plan_ring_p5s02a.json"), os.path.join(B, "prep_c156_a1_1_session.json")
LOG159 = os.path.join(B, "prep_c159_c1_1_mk.log")
WANT = {os.path.join(ROOT, "tools", "stagekit.py"): "0b5bb678", os.path.join(ROOT, "tools", "stagesim.py"): "a3261b56",
        os.path.join(ROOT, "tools", "stagexec.py"): "c4a6e0b6", os.path.join(ROOT, "tools", "stage_prerun.py"): "7605116f",
        os.path.join(B, "plan_ring_p5s02b_in.json"): "56bfddd3", GRAPH: "7ac24924", os.path.join(B, "memory_model.json"): "5b87de43",
        RIN: "d84634bd", PA: "4284c22a", PASESS: "e3117bf4"}
LIMIT, READS = 675.0, 2
gate = L.Gate(fatal_default=False)
M0 = dict((p, md5(p)) for p in WANT)
gate("M0 pins", all(M0[p].startswith(w) for p, w in WANT.items()), dict((os.path.basename(p), M0[p][:8]) for p in WANT), fatal=True)
RA, PAJ, SESS = J(RIN)["actions"], J(PA), J(PASESS)
K1 = len(PAJ["actions"])
POS = dict((a["id"], i) for i, a in enumerate(RA, 1))
GRPS = [(c["group"], c["status"], min(POS[x] for x in c["actions"]), max(POS[x] for x in c["actions"])) for c in SESS["census"]]
# ---- mapping + compile: the same calls as prep_c159_c1_1_mk.py:84-122 (without the delete action, whose compile is not needed here)
last = max((PAJ.get("finalized") or {}).get("step_files") or [], key=lambda x: int(x["n"]))
SYM = J(last["path"])["state"]["sym"]
GR = J(GRAPH)
cm, cwhy, cmeta = SPR.load_creation_map({"plan": rel(PA), "md5": md5(PA)}, GR)
_h, BOUND = M.bound_from_cmap(os.path.join(ROOT, cmeta["path"]))
RAW80 = copy.deepcopy(RA[K1:])
REAL, bad, _l = M.map_symbols(M.used_symbols(RAW80, M.made_symbols(RAW80)), SYM, BOUND, GR)
OWNERS = SX.plan_base_owners({"base": {"path": rel(GRAPH), "md5": md5(GRAPH)}})
FMAP, fbad, _f = M.map_frames(RAW80, RA, SYM, BOUND, OWNERS)
gate("MAP symbols and frames map", not bad and not fbad, (bad, fbad), fatal=True)
TOP = {"schema": "stageplan/1", "context": J(RIN).get("context") or {"s1_key": "D1_s1_copy"}}
OPS = SX.compile_plan(dict(TOP, actions=M.apply_map(RAW80, REAL, FMAP)), owners=OWNERS)
A = lambda k: k + K1                                                                            # noqa: E731  plan act k -> A number
gof = lambda a: next(g for g, _s, lo, hi in GRPS if lo <= a <= hi)                             # noqa: E731
span = [(o["kind"], [A(k) for k in o["acts"]]) for o in OPS if len(set(gof(A(k)) for k in o["acts"])) > 1]
gate("C A24..A80 compiles to {0} ops; no op spans a group boundary".format(len(OPS)), not span, span, fatal=True)
BYG = dict((g, [o["kind"] for o in OPS if gof(A(o["acts"][0])) == g]) for g, _s, _lo, _hi in GRPS)
# ---- REPRO the 159 cumulative table (log kinds and MAIN at group ends) on today's bytes
LG = [re.match(r"FACT MAINTAB op (\d+) (\S+) acts .*MAIN ([\d.]+)( \| group end (\S+))?", ln) for ln in open(LOG159, encoding="utf-8")]
LG = [m for m in LG if m]
lkinds = [m.group(2) for m in LG]
ckinds = lkinds[:1] + [k for g, _s, lo, hi in GRPS if 24 <= lo <= 60 for k in BYG[g]]
MODEL, START = SPR.load_memory_model(), SESS["start_mb"]
ends = dict((m.group(5), (int(m.group(1)), float(m.group(3)))) for m in LG if m.group(5))
rep = dict((g, (L.main_of(n, ckinds, SX, SPR, MODEL, START, READS)[0], v)) for g, (n, v) in ends.items())
gate("REPRO kinds == 159 log ops 1..24 and MAIN at group ends == log (prep_c159_c1_1_mk.log:48-71)",
     ckinds == lkinds and all(a == b for a, b in rep.values()), {"kinds_eq": ckinds == lkinds, "main(now, log)": rep})
gate("START_ASSUMED == 603.4", START == 603.4, START)
# ---- fresh-instance MAIN per group and the greedy whole-group split over A41..A80
def fresh(gs):
    ks = [k for g in gs for k in BYG[g]]
    return L.main_of(len(ks), ks, SX, SPR, MODEL, START, READS)[0], len(ks)
REM = [x for x in GRPS if x[2] >= 41]
for g, st, lo, hi in REM:
    m_, n_ = fresh([g]) if st == "OK" else (None, len(BYG[g]))
    print("FACT GROUP {0} {1} A{2}..A{3} actions {4} ops {5} kinds {6} fresh MAIN {7}".format(g, st, lo, hi, hi - lo + 1, n_, BYG[g], m_), flush=True)
steps, cur = [], []
for g, st, lo, hi in REM:
    if st != "OK":
        if cur:
            steps.append(cur)
            cur = []
        steps.append([g])
        continue
    if cur and fresh(cur + [g])[0] > LIMIT:
        steps.append(cur)
        cur = []
    cur.append(g)
if cur:
    steps.append(cur)
for i, s in enumerate(steps):
    lo, hi = min(x[2] for x in REM if x[0] in s), max(x[3] for x in REM if x[0] in s)
    ok = all(x[1] == "OK" for x in REM if x[0] in s)
    print("FACT STEP {0} groups {1} A{2}..A{3} actions {4} ops {5} MAIN {6}".format(i + 1, s, lo, hi, hi - lo + 1, sum(len(BYG[g]) for g in s),
          fresh(s)[0] if ok else "none (GAP/BLOCKED)"), flush=True)
if all(x[1] == "OK" for x in REM if x[0] in ("I", "J")):
    print("FACT PAIR I+J fresh MAIN {0} (limit {1})".format(fresh(["I", "J"])[0], LIMIT), flush=True)
gate("U pins unchanged", all(md5(q) == M0[q] for q in WANT))
sys.exit(gate.result())
