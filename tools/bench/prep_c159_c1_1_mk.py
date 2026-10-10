# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_159-c1-1.md
# ---
r"""prep_c159_c1_1_mk - card 159-c1-1 (OFFLINE, json only, no LabVIEW, never launched): PD388(h) split check on the REAL 94ffff94 graph
(graph_ring_p5s02a_20261010_032547.json 7ac24924) and P5-2 step 2 = plan_ring_p5s02b.json: action 1 delete_wire <the A13 remnant> (PD388(a)),
then A24..A60 of plan_ring_p5s02r_in.json d84634bd or the last whole-group cut that fits (PD387(f)); MERGE assumption on A28/A35/A32/A39
(PD388(c), PD389(b)(c)).
Existing routes checked before writing: stage_prerun --rebase (stage_prerun.py:4353) re-binds a PROVISIONAL plan but _remap_plan
(:4199-4248) maps uid fields only, never a `frame` NAME, and a case already in the base graph answers frames only as '#<diagram uid>'
(stagesim.py:691-699, PD378(a)) - so the step-1 case's frame wires cannot cross a rebase. The route used is P5-1b's (PD378(b)): symbols ->
real uids by the step-1 sim end + the run's creation map, frame names -> '#<uid>'; that block was inline in prep_c154_a4_1_mk.py:95-172 /
prep_c155_a2_1_mk.py:95-181 and is now CALLED from prep_c159_c1_1_lib.py (self-test 3/0 on 155's case). Gate / main_of / tie_rows / step_facts /
sg_census from prep_c156_a1_1_lib.py; stagesim.simulate / base_case_frames, stagexec.compile_plan / plan_base_owners, stage_prerun
load_creation_map / x10_start / control_path_lint / x17_gate. No tool edit, no new op.
PREDICTION CONTRACT: M0 pins; R0 p5s02a actions == A1..A23; GRP no census group crosses A60/A61 (J ends at A60, K3 starts at A61);
  CM creation map of the 023239 run; MAP step-1 symbols (CQ7, CQ7.f0, frames) -> real; FRM 'True'/'False' -> '#<uid>' == base_case_frames;
  DW the remnant = P5-1's #3052 'File # Saved' wire, a Wire obj with NO terminal row in 94ffff94; C full compile passes;
  CUT: MAIN(delete + A24..A60) at START 603.4 > 675 expected -> the last whole-group cut that fits (verdict printed, not assumed);
  PROBE (plan without action 1) replays to its end, failed None; MERGE each of A28/A35/A32/A39 inside the cut: the stub terminal carries one wire
  after the action, uid printed; SB REALSIM of the plan: REFUSED at action 1 - stagesim op_delete_wire needs terminal rows of the wire
  (stagesim.py:1424-1426; stagexec resolves it by terminals too, stagexec.py:2843-2851) and w<remnant> has none -> final False (GAP, OPEN);
  U pins untouched.
    py tools/bgrun.py --material --max-min 15 --log tools/bench/prep_c159_c1_1_mk.log -- py -u tools/bench/prep_c159_c1_1_mk.py"""
import collections, copy, json, os, sys                                                      # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
from tools import protocol  # noqa: E402
import stagesim as SS, stagexec as SX, stage_prerun as SPR                                   # noqa: E401,E402
import prep_c156_a1_1_lib as L                                                               # noqa: E402
import prep_c159_c1_1_lib as M                                                               # noqa: E402
md5, rel, J = L.md5, L.rel, L.J
B = os.path.join(ROOT, "tools", "bench")
SIM = os.path.join(B, "sim")
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
GRAPH = os.path.join(B, "graph_ring_p5s02a_20261010_032547.json")
GRAPH51 = os.path.join(B, "graph_ring_p5s01_20261009_125622.json")
RIN, PA, PASESS = os.path.join(B, "plan_ring_p5s02r_in.json"), os.path.join(B, "plan_ring_p5s02a.json"), os.path.join(B, "prep_c156_a1_1_session.json")
MMF = os.path.join(B, "memory_model.json")
PRROOT = os.path.join(SIM, "ring_p5s02b", "_probe")
QIN = os.path.join(PRROOT, "plan_ring_p5s02bq_in.json")
IN, OUT = os.path.join(B, "plan_ring_p5s02b_in.json"), os.path.join(B, "plan_ring_p5s02b.json")
FACTS = os.path.join(B, "prep_c159_c1_1_session.json")
VI2A = os.path.join(CD, "D1_ring_p5s02a_20261010_023239.vi")
WANT = {os.path.join(B, "cards", "brief_159-c1-1.md"): "2643ca7ec111032c09a0878a844bff58",
        os.path.join(ROOT, "docs", "d1", "ring-p5b.md"): "8ff5f8f20370121fd22ae3cf0d2e6008",
        os.path.join(ROOT, "docs", "d1", "ring-p5.md"): "99c812e6800d73ecace89270b1ec8f37",
        GRAPH: "7ac24924f979afde964e63fb27957b45", RIN: "d84634bdbe0f4f94669d2443af116b8e", PA: "4284c22a540f9e3f39c7092affe516af",
        os.path.join(B, "prep_c156_a1_1_mk.py"): "3cbe8fc83a18ecfaad17387c4daebc4f", PASESS: "e3117bf4a3c0e92c61e8ecea8572b018",
        os.path.join(B, "attrib_c159_p5s02a.md"): "f5a17ff88f891f32655e07c265c590f7", os.path.join(B, "diag_c159_cen2_wire.md"): "158a22fcbe732de7e98a07b4c7037ac9",
        MMF: "5b87de43b3b3653c9ed1d9a576ddd167", os.path.join(ROOT, "tools", "stage_prerun.py"): "7605116f1dfe1c6fd4963dbfcf259de1",
        os.path.join(ROOT, "tools", "stagekit.py"): "9cd8822e7605cc6f6a1f899323c9d54b", os.path.join(ROOT, "tools", "stagexec.py"): "7a712ccb4c1f754d8bee4557f632177f",
        os.path.join(ROOT, "tools", "stagesim.py"): "eb99c6bab81633f9bdd7c10dce6bfc0a", os.path.join(ROOT, "tools", "vigraph.py"): "a7eb58c7",   # card pin 'a7eb58c7eb35a134f93df168ea4cdea80' is 33 chars (typo); prefix used
        os.path.join(ROOT, "tools", "addrcheck.py"): "207beb0d09102c78b1e06d1f076eec7e", GRAPH51: "6716c499",
        VI2A: "94ffff9413599d5153a5e6fb409294ab", os.path.join(CD, "D1_ring_p4s09_20261009_060515.vi"): "eb1d0f31",
        os.path.join(CD, "D1_ring_p5s01a_20261009_101219.vi"): "2482fe7b", os.path.join(CD, "D1_ring_p5s01_20261009_124542.vi"): "7f2582ae"}
MAIN_SRC_READS, LIMIT, MAXACT = 2, 675.0, 40
MERGE_POS = (28, 35, 32, 39)                                   # PD388(c): A28, A35, A32, A39 (attrib_c159_p5s02a.md:54-55)
CARD = "c159-c1-1"
gate = L.Gate()
ARTS = gate.ARTS
M0 = dict((p, md5(p)) for p in WANT)
gate("M0 input md5 == card pins / VI pins", all(M0[p].startswith(w) for p, w in WANT.items()), dict((os.path.basename(p), M0[p][:8]) for p in WANT))
pre = [rel(p) for p in (IN, OUT, FACTS) if os.path.exists(p)]
gate("P no pre-existing plan_ring_p5s02b{_in,}.json / session file", not pre, pre)
# ---- rows and groups
RA, PAJ, SESS = J(RIN)["actions"], J(PA), J(PASESS)
gate("R0 p5s02a actions == A1..A{0} of plan_ring_p5s02r_in.json, field for field".format(len(PAJ["actions"])),
     PAJ["actions"] == RA[:len(PAJ["actions"])], [a["id"] for a, b in zip(PAJ["actions"], RA) if a != b])
K1 = len(PAJ["actions"])
POS = dict((a["id"], i) for i, a in enumerate(RA, 1))
GRPS = [(c["group"], c["status"], min(POS[x] for x in c["actions"]), max(POS[x] for x in c["actions"])) for c in SESS["census"]]
for g_, st_, lo, hi in GRPS:
    if hi > K1:
        print("FACT GROUP {0} status {1}: A{2}..A{3} ({4} actions; first {5}, last {6})".format(g_, st_, lo, hi, hi - lo + 1, RA[lo - 1]["id"], RA[hi - 1]["id"]), flush=True)
CROSS = [(g_, lo, hi) for g_, _s, lo, hi in GRPS if lo <= 60 < hi]
TOUCH = [(g_, lo, hi) for g_, _s, lo, hi in GRPS if lo <= 61 and hi >= 60]
gate("GRP census groups contiguous and disjoint over A1..A{0}; groups touching A60/A61 {1}; crossing {2}".format(len(RA), TOUCH, CROSS),
     sorted(x for _g, _s, lo, hi in GRPS for x in range(lo, hi + 1)) == list(range(1, len(RA) + 1)), GRPS, fatal=False)
# ---- symbol map: step-1 sim end + the creation map of the run that saved 94ffff94
last = max((PAJ.get("finalized") or {}).get("step_files") or [], key=lambda x: int(x["n"]))
gate("E1 p5s02a finalized last step file {0} md5 == recorded {1}".format(last["path"], last["md5"][:8]), md5(os.path.join(ROOT, last["path"])) == last["md5"])
SYM = J(last["path"])["state"]["sym"]
GR = J(GRAPH)
cm, cwhy, cmeta = SPR.load_creation_map({"plan": rel(PA), "md5": md5(PA)}, GR)
gate("CM creation map of the p5s02a run that saved 023239.vi: {0} ({1})".format(cmeta.get("path"), cwhy),
     cm is not None and os.path.normcase((cmeta.get("head") or {}).get("work") or "") == os.path.normcase(VI2A), cmeta.get("head"))
HEAD, BOUND = M.bound_from_cmap(os.path.join(ROOT, cmeta["path"]))
RAW = copy.deepcopy(RA[K1:60])
RAW80 = copy.deepcopy(RA[K1:])
used = M.used_symbols(RAW80, M.made_symbols(RAW80))
REAL, bad, lines = M.map_symbols(used, SYM, BOUND, GR)
for ln in lines:
    print("FACT " + ln, flush=True)
gate("MAP every step-1 symbol A24..A80 uses ({0}) -> a real uid in 94ffff94".format(used), not bad, bad)
OWNERS = SX.plan_base_owners({"base": {"path": rel(GRAPH), "md5": md5(GRAPH)}})
FMAP, fbad, flines = M.map_frames(RAW80, RA, SYM, BOUND, OWNERS)
for ln in flines:
    print("FACT " + ln, flush=True)
gate("FRM every `frame` name on a step-1 case ({0} ends) -> '#<real frame uid>' == base_case_frames: {1}".format(
     len(FMAP), sorted(set((v["frame_name"], v["addr"]) for v in FMAP.values()))), not fbad, fbad)
# ---- the A13 remnant (PD388(a)), read from the graphs, never typed
G51 = J(GRAPH51)
r51 = [r for r in G51["terminals"] if int(r["owner_uid"]) == 3052 and r["term_name"] == "File # Saved" and r["is_source"]]
W_OLD = int(r51[0]["wire_uid"]) if len(r51) == 1 else None
rnow = [r for r in GR["terminals"] if int(r["owner_uid"]) == 3052 and r["term_name"] == "File # Saved" and r["is_source"]]
wobj = [o for o in GR.get("objs") or [] if int(o["uid"]) == (W_OLD or 0)]
wrows = [r for r in GR["terminals"] if int(r.get("wire_uid") or 0) == (W_OLD or 0)]
print("FACT DW P5-1 #3052 'File # Saved' wire w{0}; in 94ffff94: obj {1}, terminal rows {2}; #3052 now on w{3}".format(
      W_OLD, wobj, len(wrows), [r["wire_uid"] for r in rnow]), flush=True)
gate("DW remnant w{0} = P5-1's #3052 -> #376 wire: a Wire obj in 94ffff94 with NO terminal row; #3052 now feeds another wire".format(W_OLD),
     W_OLD is not None and len(wobj) == 1 and wobj[0]["class"] == "Wire" and not wrows and len(rnow) == 1 and int(rnow[0]["wire_uid"]) != W_OLD)
DEL = {"op": "delete_wire", "id": "dw_a13", "wire_uid": W_OLD,
       "why": "PD388(a): step-1 A13 w_ref re-made #3052 'File # Saved' -> #376 'saved file refnum' as a new wire; the old segment stayed, termless, carries no data (U1)"}
TOP = {"schema": "stageplan/1", "context": J(RIN).get("context") or {"s1_key": "D1_s1_copy"}}
BASEREF = {"path": rel(GRAPH), "md5": md5(GRAPH)}
FULL80 = [DEL] + M.apply_map(RAW80, REAL, FMAP)
try:
    O80 = SX.compile_plan(dict(TOP, actions=FULL80), owners=OWNERS)
    span = [(o["kind"], o["acts"]) for o in O80 if min(o["acts"]) - 1 + K1 <= 60 < max(o["acts"]) - 1 + K1]
    print("FACT C80 delete + A24..A80 compiles on the real owners: {0} ops; ops spanning A60/A61 {1}".format(len(O80), span), flush=True)
except SX.ExecStop as e:
    print("FACT C80 delete + A24..A80 compile refused: {0}".format(str(e)[:500]), flush=True)
FULL = FULL80[:1 + 60 - K1]
for a, r in zip(FULL[1:], RAW):
    ch = dict((k, [r[k], a[k]]) for k in a if a[k] != r[k])
    if ch:
        print("FACT ROW A{0} {1}: changed {2}".format(POS[r["id"]], r["id"], ch), flush=True)
try:
    OPS, cerr = SX.compile_plan(dict(TOP, actions=FULL), owners=OWNERS), None
except SX.ExecStop as e:
    OPS, cerr = None, str(e)
gate("C delete + A24..A60 ({0} actions) compiles (stagexec.compile_plan, real owners)".format(len(FULL)), cerr is None, cerr)
KINDS = [o["kind"] for o in OPS]
# ---- PD388(h): planned MAIN at START_ASSUMED and the cut
MODEL = SPR.load_memory_model()
START = SESS["start_mb"]
XS2 = SPR.x10_start(md5(VI2A), MODEL)
print("FACT START START_ASSUMED {0} (prep_c156_a1_1_session.json start_mb: {1}); x10_start(94ffff94) = {2}".format(START, SESS.get("start_cite"), XS2), flush=True)
gate("XS START_ASSUMED == 603.4 (PD388(e), unchanged)", START == 603.4, START)
OWNA = ["DEL"] + [next(g_ for g_, _s, lo, hi in GRPS if lo <= POS[r["id"]] <= hi) for r in RAW]
GEND = set(i for i in range(1, len(FULL) + 1) if i == len(FULL) or OWNA[i] != OWNA[i - 1])
TAB = [(n, L.main_of(n, KINDS, SX, SPR, MODEL, START, MAIN_SRC_READS)[0], max(OPS[n - 1]["acts"])) for n in range(1, len(OPS) + 1)]
for n, m_, ka in TAB:
    print("FACT MAINTAB op {0} {1} acts {2} (A{3}) MAIN {4}{5}".format(n, OPS[n - 1]["kind"], OPS[n - 1]["acts"], "-" if ka == 1 else ka - 1 + K1, m_,
          " | group end {0}".format(OWNA[ka - 1]) if ka in GEND else ""), flush=True)
contig = lambda n, ka: sorted(x for o in OPS[:n] for x in o["acts"]) == list(range(1, ka + 1))     # noqa: E731
fit = [n for n, m_, ka in TAB if m_ <= LIMIT and ka in GEND and ka <= MAXACT and contig(n, ka)]
KEEP = not CROSS and TAB[-1][1] <= LIMIT
NS = len(OPS) if KEEP else (max(fit) if fit else 0)
KA = TAB[NS - 1][2] if NS else 0
VERDICT = ("KEEP A24..A60: no group crosses A60/A61 and MAIN {0} <= {1}".format(TAB[-1][1], LIMIT) if KEEP else
           "CUT at A{0} (group {1} end; ops 1..{2}, MAIN {3} <= {4}); A24..A60 MAIN {5} > {4}{6}".format(
               KA - 1 + K1, OWNA[KA - 1], NS, TAB[NS - 1][1] if NS else None, LIMIT, TAB[-1][1], "; groups crossing A60/A61 {0}".format(CROSS) if CROSS else ""))
print("FACT VERDICT PD388(h): " + VERDICT, flush=True)
gate("CUT a whole-group prefix fits: n* {0}, actions 1..{1} (delete + A24..A{2})".format(NS, KA, KA - 1 + K1), NS >= 1, TAB)
STEP = FULL[:KA]
REM = [r["id"] for r in RA[KA - 1 + K1:]]
print("FACT REMAINDER after step 2: A{0}..A{1} ({2} actions) groups {3}".format(KA + K1, len(RA), len(REM),
      sorted(set(g_ for g_, _s, lo, hi in GRPS if hi >= KA + K1), key=[x[0] for x in GRPS].index)), flush=True)
# ---- PROBE: the same rows WITHOUT action 1, on the real graph (FACT; the MERGE uids are read off its end)
os.makedirs(PRROOT, exist_ok=True)
json.dump(dict(TOP, stage="ring_p5s02bq", goal="card 159-c1-1 PROBE (fact only): step 2 rows without action 1 (delete of the termless remnant) on 94ffff94",
               base=BASEREF, actions=STEP[1:]), open(QIN, "w", encoding="utf-8"), indent=1)
SQ = SS.simulate(QIN, GRAPH, out_root=PRROOT, plan_out_dir=PRROOT, log=lambda *x: None, route_check=False)
HQ = L.step_facts("PROBE", SQ)
provQ = [s["n"] for s in SQ["steps"] if s.get("provisional")]
gate("PROBE rows A24..A{0} replay on 94ffff94 to their end: failed {1}; PROVISIONAL {2}".format(KA - 1 + K1, json.dumps(SQ.get("failed"), default=str)[:400], provQ),
     SQ["failed"] is None and len(SQ["steps"]) == len(STEP) and not provQ, SQ.get("failed"), fatal=False)
QEND = J(SQ["steps"][-1]["file"]["path"])["state"] if SQ["failed"] is None else None
MERGE = []
for p_ in MERGE_POS:
    a = FULL[p_ - K1]
    if p_ - K1 >= KA:
        MERGE.append({"pos": p_, "id": a["id"], "in_step": False})
        continue
    side = "src" if isinstance(a["src"], dict) and isinstance(a["src"].get("uid"), int) else "dst"
    tu = int(a[side]["term_uid"])
    stub = next(int(r["wire_uid"] or 0) for r in GR["terminals"] if int(r["term_uid"]) == tu)
    wend = sorted(set(int(r.get("wire_uid") or 0) for r in (QEND or {}).get("terminals") or [] if int(r["term_uid"]) == tu))
    other = a["dst" if side == "src" else "src"]
    sf = J(SQ["steps"][p_ - K1]["file"]["path"]) if QEND is not None else {}           # steps[0] = base; probe action k = A(k + K1)
    net = sorted((int(r["owner_uid"]), r["term_name"], int(r["term_uid"]), r["term_class"], bool(r["is_source"]))
                 for r in (QEND or {}).get("terminals") or [] if len(wend) == 1 and int(r.get("wire_uid") or 0) == wend[0])
    MERGE.append({"pos": p_, "id": a["id"], "in_step": True, "side": side, "stub_term": tu, "stub_wire": stub, "end_wires_on_term": wend,
                  "end_net": net, "other_end": other, "effect": sf.get("effect"), "step_id": (SQ["steps"][p_ - K1] or {}).get("id"),
                  "step_file": sf and rel(SQ["steps"][p_ - K1]["file"]["path"])})
    print("FACT MERGE A{0} {1}: {2} end t{3} carries stub w{4} in 94ffff94; probe sim end: wire(s) on t{3} = {5}, net {6}; step {7} effect {8}".format(
          p_, a["id"], side, tu, stub, wend, net, SQ["steps"][p_ - K1].get("id"), json.dumps(sf.get("effect"), default=str)[:300]), flush=True)
mrg_ok = all((not m_["in_step"]) or (m_["stub_wire"] and len(m_["end_wires_on_term"]) == 1) for m_ in MERGE)
gate("MERGE each in-step A28/A35/A32/A39: the stub terminal carries a stub in 94ffff94 and ONE wire at the probe sim end", mrg_ok and QEND is not None,
     [(m_["pos"], m_.get("stub_wire"), m_.get("end_wires_on_term")) for m_ in MERGE], fatal=False)
for m_ in MERGE:
    if m_["in_step"]:
        a = STEP[m_["pos"] - K1]
        m_["why_added"] = ("ASSUMPTION (PD388(c), not measured; the next scratch measures it): MERGE - this connect lands on t{0}, which carries stub "
                           "w{1}; one ok wire expected, sim-end uid w{2} (probe {3}); CEN2 judges by wire ENDS, not uid (PD389(b))").format(
            m_["stub_term"], m_["stub_wire"], m_["end_wires_on_term"][0] if len(m_["end_wires_on_term"]) == 1 else m_["end_wires_on_term"], rel(QIN))
        a["why"] = ((a.get("why") or "") + " | " + m_["why_added"])[:400]
        m_["why_len"] = len(a["why"])
# ---- open rows from the probe (pass A without action 1): the delete touches no terminal, so its rows are the plan's
ok_pairs = dict(((int(r["node"]), r["term"]), "p5s02a-open") for r in PAJ.get("open_rows") or [])
ties, untied, orows = L.tie_rows(SQ, STEP[1:], ok_pairs, SS.V.key_parts, CARD) if QEND is not None else ({}, ["no probe end"], [])
gate("TIE every probe end row ({0}) tied to a step-2 action or a p5s02a open row".format(len(SQ.get("end_cdiff_rows") or [])), not untied, untied[:10], fatal=False)
GOAL = ("RING P5-2 step 2 (card 159-c1-1, PD388(a)(c)(h) + PD389): delete of the A13 remnant w{0}, then A24..A{1} of plan_ring_p5s02r_in.json "
        "on the REAL 94ffff94 graph 7ac24924; {2}").format(W_OLD, KA - 1 + K1, VERDICT)[:400]
json.dump(dict(TOP, stage="ring_p5s02b", goal=GOAL, base=BASEREF, open_rows=orows, actions=STEP), open(IN, "w", encoding="utf-8"), indent=1)
ok_, why_ = protocol.validate_obj(J(IN))
gate("S1 plan input validates ({0} actions, {1} open pairs)".format(len(STEP), len(orows)), ok_, why_)
SB = SS.simulate(IN, GRAPH, out_root=SIM, plan_out_dir=B, log=lambda m: print(m, flush=True), route_check=True)
HB = L.step_facts("REALSIM", SB)
p = J(OUT) if os.path.isfile(OUT) else {}
fz = p.get("finalized") or {}
print("FACT REALSIM plan {0}: final {1}; failed {2}; steps {3}; route check {4}".format(rel(OUT), SB["final"], json.dumps(SB.get("failed"), default=str)[:500],
      len(SB["steps"]), (fz.get("route_check") or {}).get("status")), flush=True)
pred_ref = (SB.get("failed") or {}).get("n") == 1 and "not in the current graph" in str((SB.get("failed") or {}).get("error"))
print("FACT PRED SB refusal at action 1 as predicted (stagesim.py:1424-1426 'not in the current graph'): {0}".format(pred_ref), flush=True)
gate("SB REALSIM plan FINAL on 94ffff94 (route check PASS, open_rows_match)", bool(SB["final"]) and p.get("final") is True
     and (fz.get("route_check") or {}).get("status") == "PASS", {"final": SB["final"], "failed": SB.get("failed")}, fatal=False)
ops = SX.compile_plan(p, owners=OWNERS)
MAIN, mp, cps = L.main_of(len(ops), [o["kind"] for o in ops], SX, SPR, MODEL, START, MAIN_SRC_READS)
print("FACT X10 plan ops {0} kinds {1}; checkpoints {2}; N {3} R {4}; Executor peak {5}; MAIN {6}; limit {7}; stage_prerun fail_above {8}; MEMSTOP {9}".format(
      len(ops), dict(collections.Counter(o["kind"] for o in ops)), cps, mp["N"], mp["R"], mp["peak_mb"], MAIN, LIMIT, SPR.X10_FAIL_MB, SX.MEM_STOP_MB), flush=True)
gate("X10 plan ops == ops 1..{0} of the split table; MAIN {1} == MAIN(n*) {2} <= {3}".format(NS, MAIN, TAB[NS - 1][1], LIMIT),
     [(o["kind"], o["acts"]) for o in ops] == [(o["kind"], o["acts"]) for o in OPS[:NS]] and MAIN == TAB[NS - 1][1] and MAIN <= LIMIT, mp, fatal=False)
lint = SPR.control_path_lint(p)
gate("X8 control_path_lint clean", not lint, lint, fatal=False)
ok17, det17 = SPR.x17_gate([p])
gate("X17 x17_gate over the plan", ok17, det17, fatal=False)
json.dump({"card": "159-c1-1", "plan_in": {"path": rel(IN), "md5": md5(IN)}, "plan": {"path": rel(OUT), "md5": md5(OUT) if os.path.isfile(OUT) else None},
           "probe_in": {"path": rel(QIN), "md5": md5(QIN)}, "creation_map": cmeta.get("path"), "symbol_map": REAL,
           "frame_map": dict(("{0}|{1}".format(*k), v) for k, v in FMAP.items()), "groups": GRPS, "crossing_a60": CROSS, "remnant_wire": W_OLD,
           "start_mb": START, "x10_start_94ffff94": XS2, "split_table": TAB, "verdict": VERDICT, "n_ops": NS, "k_actions": KA, "remainder": REM,
           "merge": MERGE, "open_rows": len(orows), "untied": untied, "realsim": {"final": SB["final"], "failed": SB.get("failed"), "pred_refusal": pred_ref},
           "x10": {"main": MAIN, "exec_peak": mp["peak_mb"], "checkpoints": cps}, "probe_states": HQ, "realsim_states": HB},
          open(FACTS, "w", encoding="utf-8"), indent=1, default=str)
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (QIN, IN, OUT, FACTS) if os.path.isfile(x))
gate("U inputs / VI pins untouched", all(md5(q) == M0[q] for q in WANT))
sys.exit(gate.result())
