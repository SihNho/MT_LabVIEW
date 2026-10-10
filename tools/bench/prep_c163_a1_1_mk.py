# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_163-a1-1.md
# ---
r"""prep_c163_a1_1_mk - card 163-a1-1 (OFFLINE, json only, never launched), PD396(b)(c): plan_ring_p5s02c.json = P5-2 step 3 = A41..A60 (groups I+J)
or A41..A52 (group I) of plan_ring_p5s02r_in.json d84634bd, made FINAL on the REAL p5s02b graph 431cfd83 (VI f9ae7751). Flow of prep_c160_b3_1_mk.py /
prep_c159_c1_1_mk.py, by CALLS: stagekit made/used/map_symbols, map_frames, apply_map, bound_from_cmap; prep_c156_a1_1_lib Gate / main_of (X10 on
SX.checkpoint_ops) / tie_rows / step_facts; stagesim.simulate (pass A probe -> tie -> open_rows -> REALSIM with route check); stagexec.compile_plan /
plan_base_owners; stage_prerun load_creation_map / x10_start / control_path_lint / x17_gate. Existing tools checked: no shared 'choose the whole-group
cut' function exists (c159 had it inline, prep_c159_c1_1_mk.py:144-157); here the memory rule is two candidates only (PD396(c)), no cut search.
Symbols used by A41..A60 are made by p5s02a (A9 CQ7) -> bound by the p5s02a run's creation map (adopted chain), checked on 431cfd83.
PREDICTION CONTRACT: M0 pins; MAP CQ7/CQ7.f0 -> real uids present in 431cfd83, none made by p5s02b; FRM 'False'/'True' -> '#<frame>'
  == base_case_frames; GRP I = A41..A52, J = A53..A60 (census); STUB fact per base sink end (no invented stub delete); C both candidates compile,
  every delete_wire a checkpoint, J's delete_object compiles (kind printed); X10 MAIN(I+J), MAIN(I) at START 601.2 (+ x10_start figure); plan by
  the rule; PROBE replays; TIE all end rows tied; SB REALSIM final True, failed None, 0 PROVISIONAL, route PASS, 0 UNROUTABLE; X8 / X17 clean.
    py tools/bgrun.py --material --max-min 15 --log tools/bench/prep_c163_a1_1_mk.log -- py -u tools/bench/prep_c163_a1_1_mk.py"""
import collections, copy, json, os, shutil, sys                                              # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for _p in (ROOT, os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench")):
    sys.path.insert(0, _p)
from tools import protocol                                                                   # noqa: E402
import stagekit as K                                                                         # noqa: E402
import stagesim as SS, stagexec as SX, stage_prerun as SPR                                   # noqa: E401,E402
import prep_c156_a1_1_lib as L                                                               # noqa: E402
md5, rel, J = L.md5, L.rel, L.J
B, T, SIM = os.path.join(ROOT, "tools", "bench"), os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench", "sim")
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
GRAPH, GRAPH2A = os.path.join(B, "graph_ring_p5s02b_20261010_111905.json"), os.path.join(B, "graph_ring_p5s02a_20261010_032547.json")
RIN, PA, PB2, PASESS = (os.path.join(B, x) for x in ("plan_ring_p5s02r_in.json", "plan_ring_p5s02a.json", "plan_ring_p5s02b.json", "prep_c156_a1_1_session.json"))
IN, OUT, OLDP, FACTS = (os.path.join(B, x) for x in ("plan_ring_p5s02c_in.json", "plan_ring_p5s02c.json", "plan_ring_p5s02c_prev.json", "prep_c163_a1_1_session.json"))
PRROOT = os.path.join(SIM, "ring_p5s02c", "_probe")
QIN = os.path.join(PRROOT, "plan_ring_p5s02cq_in.json")
VI2A, VI2B = os.path.join(CD, "D1_ring_p5s02a_20261010_023239.vi"), os.path.join(CD, "D1_ring_p5s02b_20261010_105511.vi")
WANT = dict((os.path.join(ROOT, i["path"]), i["md5"]) for i in J("tools/bench/cards/task_163-a1-1.json")["inputs"])
WANT.update({GRAPH2A: "7ac24924", PA: "4284c22a", PB2: "f4520b10", PASESS: "e3117bf4", VI2A: "94ffff94", VI2B: "f9ae7751",
             os.path.join(CD, "D1_ring_p5s01_20261009_124542.vi"): "7f2582ae", os.path.join(CD, "D1_ring_p4s09_20261009_060515.vi"): "eb1d0f31"})
LIMIT, READS, START, LO, I_END, J_END = 675.0, 2, 601.2, 41, 52, 60          # PD396(c): limit unchanged, START = load_by_vi f9ae7751
CARD = "c163-a1-1"
gate = L.Gate()
M0 = dict((p, md5(p)) for p in WANT)
gate("M0 input md5 == card / brief pins", all(M0[p].startswith(w) for p, w in WANT.items()), dict((os.path.basename(p), M0[p][:8]) for p in WANT))
if os.path.isfile(OUT):
    shutil.copyfile(OUT, OLDP)                                  # keep a previous step-3 plan aside; the plan below is written by simulate only
    os.remove(OUT)
print("FACT OLD previous plan_ring_p5s02c.json kept as {0}: {1}".format(rel(OLDP), md5(OLDP) if os.path.isfile(OLDP) else "none existed"), flush=True)
RA, PAJ, SESS, GR, PBJ = J(RIN)["actions"], J(PA), J(PASESS), J(GRAPH), J(PB2)
POS = dict((a["id"], i) for i, a in enumerate(RA, 1))
GRPS = dict((c["group"], (min(POS[x] for x in c["actions"]), max(POS[x] for x in c["actions"]))) for c in SESS["census"])
gate("GRP census I = A41..A52, J = A53..A60 (groups I {0}, J {1})".format(GRPS.get("I"), GRPS.get("J")), GRPS.get("I") == (LO, I_END) and GRPS.get("J") == (I_END + 1, J_END))
# ---- symbols: p5s02a sim end + the creation map of the adopted p5s02a run (the only step whose symbols A41..A60 use)
last = max((PAJ.get("finalized") or {}).get("step_files") or [], key=lambda x: int(x["n"]))
gate("E1 p5s02a last step file md5 == recorded {0}".format(last["md5"][:8]), md5(os.path.join(ROOT, last["path"])) == last["md5"])
SYM = J(last["path"])["state"]["sym"]
cm, cwhy, cmeta = SPR.load_creation_map({"plan": rel(PA), "md5": md5(PA)}, J(GRAPH2A))
gate("CM creation map of the p5s02a run that saved 023239.vi: {0} ({1})".format(cmeta.get("path"), cwhy),
     cm is not None and os.path.normcase((cmeta.get("head") or {}).get("work") or "") == os.path.normcase(VI2A), cmeta.get("head"))
HEAD, BOUND = K.bound_from_cmap(os.path.join(ROOT, cmeta["path"]))
RAW = copy.deepcopy(RA[LO - 1:J_END])
used = K.used_symbols(RAW, K.made_symbols(RAW))
by2b = sorted(set(used) & K.made_symbols(PBJ["actions"]))
REAL, bad, lines = K.map_symbols(used, SYM, BOUND, GR)
for ln in lines:
    print("FACT " + ln, flush=True)
gate("MAP A41..A60 symbols {0} -> real uids in 431cfd83; made by p5s02b: {1}".format(used, by2b), not bad and not by2b, bad)
OWNERS = SX.plan_base_owners({"base": {"path": rel(GRAPH), "md5": md5(GRAPH)}})
FMAP, fbad, flines = K.map_frames(RAW, RA, SYM, BOUND, OWNERS)
for ln in flines:
    print("FACT " + ln, flush=True)
gate("FRM frame ends ({0}) -> '#<real frame uid>': {1}".format(len(FMAP), sorted(set((v["frame_name"], v["addr"]) for v in FMAP.values()))), not fbad, fbad)
FULL = K.apply_map(RAW, REAL, FMAP)


def leaves(x, pre=""):
    if isinstance(x, dict):
        return dict(kv for k, v in x.items() for kv in leaves(v, pre + "/" + k).items())
    if isinstance(x, list):
        return dict(kv for i, v in enumerate(x) for kv in leaves(v, pre + "/" + str(i)).items())
    return {pre: x}


diff = []
for r, a in zip(RAW, FULL):
    lr, la = leaves(r), leaves(a)
    ch = sorted(k for k in set(lr) | set(la) if lr.get(k) != la.get(k))
    anc = lambda k: k if k in lr or "/" not in k.strip("/") else anc(k.rsplit("/", 1)[0])           # noqa: E731 - the input leaf a mapped leaf replaced
    okc = all(k.endswith("/frame") or str(lr.get(anc(k))).startswith("new:") for k in ch)
    if ch:
        print("FACT ROW A{0} {1}: mapped {2}".format(POS[r["id"]], r["id"], [(k, lr.get(k), la.get(k)) for k in ch])[:400], flush=True)
    if not okc:
        diff.append(r["id"])
gate("ROWS stagekit.apply_map(A41..A60) == the input except symbol -> uid and frame -> '#uid' leaves", len(FULL) == 20 and not diff, diff)
# ---- base sink ends: wires on them in 431cfd83 (fact; a sink-only stub would need stage_shared.insert_stub_deletes - none is invented)
STUBS = []
for a in FULL:
    for side in ("src", "dst"):
        e = a.get(side)
        if isinstance(e, dict) and isinstance(e.get("uid"), int) and e.get("term_uid") is not None:
            ws = sorted(set(int(r.get("wire_uid") or 0) for r in GR["terminals"] if int(r["term_uid"]) == int(e["term_uid"])) - {0})
            STUBS.append((a["id"], side, e["term_uid"], ws))
            print("FACT END {0} {1} t{2}: wires in 431cfd83 {3}".format(a["id"], side, e["term_uid"], ws), flush=True)
DW = [a for a in FULL if a["op"] == "delete_wire"]
for a in DW:
    rows = [(int(r["owner_uid"]), r["term_name"], bool(r["is_source"])) for r in GR["terminals"] if int(r.get("wire_uid") or 0) == int(a["wire_uid"])]
    print("FACT DW {0} w{1} in 431cfd83: rows {2}; sourceless {3}".format(a["id"], a["wire_uid"], rows, SS.sourceless_wire(SS.base_state(GR), a["wire_uid"])), flush=True)
DO = [(a["id"], a["uid"], [o["class"] for o in GR.get("objs") or [] if int(o["uid"]) == int(a["uid"])], (GR.get("owners") or {}).get(str(a["uid"]))) for a in FULL if a["op"] == "delete_object"]
print("FACT DO delete_object rows (id, uid, obj class, owners entry): {0}".format(DO), flush=True)
sink_stub = [s for s in STUBS if s[1] == "dst" and s[3] and not any(int(d["wire_uid"]) in s[3] for d in DW)]
gate("STUB no base sink end of A41..A60 carries a wire that no plan delete_wire removes (no stub delete needed)", not sink_stub, sink_stub, fatal=False)
# ---- PD396(c): compile both candidates, X10 MAIN on SX.checkpoint_ops, START 601.2
TOP = {"schema": "stageplan/1", "context": J(RIN).get("context") or {"s1_key": "D1_s1_copy"}}
MODEL = SPR.load_memory_model()
XS = SPR.x10_start(md5(VI2B), MODEL)
CAND = {}
for nm, hi in (("I+J", J_END), ("I", I_END)):
    try:
        ops = SX.compile_plan(dict(TOP, actions=FULL[:hi - LO + 1]), owners=OWNERS)
        m_, mp, cps = L.main_of(len(ops), [o["kind"] for o in ops], SX, SPR, MODEL, START, READS)
        mx = L.main_of(len(ops), [o["kind"] for o in ops], SX, SPR, MODEL, XS[0], READS)[0] if XS else None
        CAND[nm] = {"ops": [(o["kind"], o.get("variant"), o["acts"]) for o in ops], "cps": cps, "main": m_, "peak": mp["peak_mb"], "N": mp["N"], "R": mp["R"], "main_at_x10_start": mx}
        dwk = [k for k, o in enumerate(ops, 1) if o["kind"] == "delete_wire"]
        print("FACT C {0} A41..A{1}: {2} ops {3}; kinds {4}; checkpoints {5}; delete_wire ops {6}".format(nm, hi, len(ops), CAND[nm]["ops"],
              dict(collections.Counter(o["kind"] for o in ops)), cps, dwk), flush=True)
        print("FACT X10 {0}: START {1} N {2} R {3} Executor peak {4} MAIN {5} (limit {6}); at x10_start {7}: MAIN {8}".format(
              nm, START, mp["N"], mp["R"], mp["peak_mb"], m_, LIMIT, XS, mx), flush=True)
        gate("C {0} compiles; every delete_wire op {1} is a checkpoint".format(nm, dwk), set(dwk) <= set(cps), cps)
    except SX.ExecStop as e:
        CAND[nm] = {"error": str(e)[:500]}
        print("FACT C {0} compile refused: {1}".format(nm, str(e)[:500]), flush=True)
gate("C group I compiles", "main" in CAND.get("I", {}), CAND.get("I"))
CHOSEN = "I+J" if "main" in CAND["I+J"] and CAND["I+J"]["main"] <= LIMIT else "I"
WHY = ("MAIN(I+J) {0} <= {1}".format(CAND["I+J"].get("main"), LIMIT) if CHOSEN == "I+J" else
       "MAIN(I+J) {0} > {1} (or compile refused: {2}); group I alone MAIN {3}".format(CAND["I+J"].get("main"), LIMIT, CAND["I+J"].get("error"), CAND["I"]["main"]))
print("FACT RULE PD396(c): plan = {0} because {1}".format(CHOSEN, WHY), flush=True)
gate("X10 chosen plan {0} MAIN {1} <= {2} (START {3}, limit unchanged)".format(CHOSEN, CAND[CHOSEN]["main"], LIMIT, START), CAND[CHOSEN]["main"] <= LIMIT, CAND)
HI = J_END if CHOSEN == "I+J" else I_END
STEP = FULL[:HI - LO + 1]
gate("SPLIT no group split: A{0}..A{1} ends at a census group end".format(LO, HI), HI in (I_END, J_END) and [a["id"] for a in STEP] == [r["id"] for r in RA[LO - 1:HI]])
# ---- PROBE (pass A, no open rows) -> tie -> open_rows -> REALSIM
os.makedirs(PRROOT, exist_ok=True)
BASEREF = {"path": rel(GRAPH), "md5": md5(GRAPH)}
json.dump(dict(TOP, stage="ring_p5s02cq", goal="card 163-a1-1 PROBE (fact only): step-3 rows on f9ae7751", base=BASEREF, actions=STEP), open(QIN, "w", encoding="utf-8"), indent=1)
SQ = SS.simulate(QIN, GRAPH, out_root=PRROOT, plan_out_dir=PRROOT, log=lambda *x: None, route_check=False)
L.step_facts("PROBE", SQ, quiet=True)
gate("PROBE A{0}..A{1} replay on 431cfd83: failed {2}".format(LO, HI, json.dumps(SQ.get("failed"), default=str)[:400]), SQ["failed"] is None and len(SQ["steps"]) == len(STEP) + 1)
ok_pairs = dict(((int(r["node"]), r["term"]), "p5s02b-open") for r in PBJ.get("open_rows") or [])
ties, untied, orows = L.tie_rows(SQ, STEP, ok_pairs, SS.V.key_parts, CARD)
print("FACT TIE {0} end rows; open pairs {1}: {2}".format(len(SQ.get("end_cdiff_rows") or []), len(orows), [(o["node"], o["term"], o["why"][:60]) for o in orows])[:900], flush=True)
gate("TIE every probe end row tied to a step-3 action or a p5s02b open row", not untied, untied[:10])
GOAL = "RING P5-2 step 3 (card 163-a1-1, PD396(b)(c)): A{0}..A{1} of plan_ring_p5s02r_in.json on the REAL f9ae7751 graph 431cfd83; {2}: {3}".format(LO, HI, CHOSEN, WHY)[:400]
json.dump(dict(TOP, stage="ring_p5s02c", goal=GOAL, base=BASEREF, open_rows=orows, actions=STEP), open(IN, "w", encoding="utf-8"), indent=1)
ok_, why_ = protocol.validate_obj(J(IN))
gate("S1 plan input validates ({0} actions, {1} open pairs)".format(len(STEP), len(orows)), ok_, why_)
SB = SS.simulate(IN, GRAPH, out_root=SIM, plan_out_dir=B, log=lambda m: print(m, flush=True), route_check=True)
HB = L.step_facts("REALSIM", SB)
p = J(OUT) if os.path.isfile(OUT) else {}
rc = (p.get("finalized") or {}).get("route_check") or {}
prov = [s["n"] for s in SB["steps"] if s.get("provisional")]
for x in rc.get("rows") or []:
    print("FACT ROUTE k={0} {1} {2}: route {3}{4}".format(x.get("k"), x.get("op"), x.get("ids"), x.get("route"), "  UNROUTABLE " + str(x["unroutable"])[:300] if x.get("unroutable") else ""), flush=True)
nun = sum(1 for x in rc.get("rows") or [] if x.get("unroutable"))
print("FACT REALSIM plan {0} md5 {1}: final {2}; failed {3}; steps {4}; provisional {5}; route check {6}; UNROUTABLE {7}".format(
      rel(OUT), md5(OUT) if p else None, SB["final"], json.dumps(SB.get("failed"), default=str)[:500], len(SB["steps"]) - 1, prov, rc.get("status"), nun), flush=True)
gate("SB REALSIM FINAL on 431cfd83: failed None, {0}/{1} replayed, 0 PROVISIONAL, route PASS, 0 UNROUTABLE".format(len(SB["steps"]) - 1, len(STEP)),
     bool(SB["final"]) and p.get("final") is True and SB.get("failed") is None and not prov and len(SB["steps"]) - 1 == len(STEP) and rc.get("status") == "PASS" and nun == 0,
     {"final": SB["final"], "failed": SB.get("failed"), "route": rc.get("status"), "first_fail": rc.get("first_fail")})
ops = SX.compile_plan(p, owners=OWNERS)
MAIN, mp, cps = L.main_of(len(ops), [o["kind"] for o in ops], SX, SPR, MODEL, START, READS)
gate("C-OUT compile of plan_ring_p5s02c.json == candidate {0} ops/checkpoints; MAIN {1}".format(CHOSEN, MAIN),
     [(o["kind"], o.get("variant"), o["acts"]) for o in ops] == [tuple(x) for x in CAND[CHOSEN]["ops"]] and cps == CAND[CHOSEN]["cps"] and MAIN == CAND[CHOSEN]["main"], (cps, MAIN))
gate("IDS plan action ids == A{0}..A{1} in order".format(LO, HI), [a["id"] for a in p["actions"]] == [r["id"] for r in RA[LO - 1:HI]], [a["id"] for a in p["actions"]])
lint = SPR.control_path_lint(p)
gate("X8 control_path_lint clean", not lint, lint, fatal=False)
ok17, det17 = SPR.x17_gate([p])
gate("X17 x17_gate over the plan", ok17, det17, fatal=False)
json.dump({"card": "163-a1-1", "plan_in": {"path": rel(IN), "md5": md5(IN)}, "plan": {"path": rel(OUT), "md5": md5(OUT)}, "probe_in": {"path": rel(QIN), "md5": md5(QIN)},
           "creation_map": cmeta.get("path"), "symbol_map": REAL, "frame_map": dict(("{0}|{1}".format(*k), v) for k, v in FMAP.items()), "ends": STUBS,
           "delete_objects": DO, "start_mb": START, "x10_start_f9ae7751": XS, "candidates": CAND, "chosen": CHOSEN, "why": WHY, "actions": [a["id"] for a in STEP],
           "open_rows": orows, "realsim": {"final": SB["final"], "failed": SB.get("failed"), "provisional": prov, "route_check": rc},
           "compile": {"ops": [(o["kind"], o.get("variant"), o["acts"]) for o in ops], "checkpoints": cps}, "x10": {"main": MAIN, "exec_peak": mp["peak_mb"]},
           "realsim_states": HB}, open(FACTS, "w", encoding="utf-8"), indent=1, default=str)
gate.ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (QIN, IN, OUT, FACTS) if os.path.isfile(x))
gate("U inputs / VI / tool pins untouched", all(md5(q) == M0[q] for q in WANT))
sys.exit(gate.result())
