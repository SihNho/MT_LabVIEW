# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_154-a3-2.md
# ---
r"""prep_c154_a3_2_mk - card 154-a3-2 steps 1-2 (OFFLINE, json only, no LabVIEW, no COM): the P5-1 plan (form S, docs/d1/ring-p5.md PD374(a)(c),
PD376(a)) on the REAL s09 graph graph_ring_p4s09_20261009_062044.json 22f967b5 (VI claudeDev\D1_ring_p4s09_20261009_060515.vi eb1d0f31, never opened).
ROW CONTENT: the census action lists of tools/bench/diag_c154_a3_1_census.py (pinned 3904fb9d) - its assignments CD, DQ, dq, role, T, DN, K, PRIM,
Q, QK, W, LOC, OBT, A0, S_REF, L_REF, FORMS are EXECUTED from that file's own AST (no uid / terminal name retyped here); actions = FORMS["S"]
(= OBT(686) + A0 + S_REF, the CHOSEN form, census log :90). CHANGED versus the census, each stated before the run:
  (c1) aliases that the stageplan/1 schema refuses (`as` pattern ^[A-Za-z]+[0-9]+$, docs/protocol/stageplan.json:317-320, enforced by
       protocol.validate_obj, protocol.py:142) are renamed, references included: SQR->QS1 (SR, L/R faces QS1L/QS1R), TCI->TC1, TCO->TC2,
       TQI->TQ1, TQO->TQ2 - symbols only, no uid / terminal / diagram changes; the census never validated (it applied rows directly);
  (c2) c_obt and c_enq get `data_stream: true` + a why (prerun X8 control_path_lint refuses a queue create without them, stage_prerun.py:1180-1188;
       PD374(a): the queue carries the 1.2 -> 1.7 DATA stream only);
  (c3) every action gets a `why` citing its census row (tools/bench/p5_route_census.md);
  (c4) declared term_class values are CHECKED against measured graphs (queue Function terminals: graph_qrt_pool_20260928.json, LabVIEW-read;
       ArrayConstant / DigitalNumericConstant / Increment #1978: the s09 graph) - a mismatch is a FAIL, never an edit.
Existing tools used (no new op, no tool edit): stagesim.simulate (pass A + REALSIM), stagexec.compile_plan / is_ct / BIND_KINDS, stage_prerun
x10_start / x10_model_peak / control_path_lint / x17_gate / prim_donor_check; pattern copied from prep_c152_b2_1_mk.py (TIE, open_rows, SG census).
PASS A = the plan without open_rows on the real graph (sim/ring_p5s01/_passA); REALSIM = the plan with open_rows on the same real graph, the
finalize run (sim/ring_p5s01, route check on) that writes tools/bench/plan_ring_p5s01.json. Per-step state compare pass A vs REALSIM.
PREDICTION CONTRACT: M0 pins; V raw census list fails validation only on (c1) aliases; N actions 32 <= 40; TC term classes == measured;
  SA pass A replays all 32 actions, failed None, 0 collect-all PROVISIONAL; TIE every end row tied to a P5-1 action or an s09 open row;
  SB REALSIM FINAL, route check PASS, states == pass A per step; X10 MAIN <= 680 (MEMSTOP 695); X8 lint clean; X17 clean; U inputs untouched.
    py tools/bgrun.py --material --max-min 10 --log tools/bench/prep_c154_a3_2_mk.log -- py -u tools/bench/prep_c154_a3_2_mk.py"""
import ast, collections, copy, hashlib, json, os, re, sys                                    # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagesim as SS, stagexec as SX, stage_prerun as SPR                                   # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
SIM = os.path.join(B, "sim")
GRAPH = os.path.join(B, "graph_ring_p4s09_20261009_062044.json")
CENSUS = os.path.join(B, "diag_c154_a3_1_census.py")
POOL = os.path.join(B, "graph_qrt_pool_20260928.json")
S09 = os.path.join(B, "plan_ring_p4_s09v18.json")
DQJ = os.path.join(B, "donor_queue_v0.json")
MMF = os.path.join(B, "memory_model.json")
PAROOT = os.path.join(SIM, "ring_p5s01", "_passA")
AIN, IN, OUT = os.path.join(PAROOT, "plan_ring_p5s01a_in.json"), os.path.join(B, "plan_ring_p5s01_in.json"), os.path.join(B, "plan_ring_p5s01.json")
FACTS = os.path.join(B, "prep_c154_a3_2_session.json")
S09VI_MD5 = "eb1d0f3107bbba49c9ae67a47c0ee50f"
WANT = {GRAPH: "22f967b5", CENSUS: "3904fb9d", DQJ: "15269b6c", S09: "9d622c95", MMF: "6f2b5687",
        os.path.join(ROOT, "docs", "d1", "ring-p5.md"): "9c5ba571", os.path.join(ROOT, "tools", "bench", "p5_route_census.md"): "dba7e3f0"}
MAIN_SRC_READS = 2                                    # main recipe source census_snapshot reads (prep_c152_b2_1_mk.py:79)
MAXACT = 40                                           # brief_154-a3-2.md step 1
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                                # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                   # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
G, ARTS = {"pass": 0, "fail": 0, "first": None}, []


def gate(label, ok, d="", fatal=True):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)
    if not ok and fatal:
        print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
        sys.exit(1)


M0 = dict((p, md5(p)) for p in WANT)
gate("M0 input md5 == card pins", all(M0[p].startswith(w) for p, w in WANT.items()), dict((os.path.basename(p), M0[p][:8]) for p in WANT))
pre = [p for p in (AIN, IN, OUT, FACTS) if os.path.exists(p)]
gate("P no pre-existing P5-1 plan / plan_in / session file", not pre, pre)
# ---- the census action lists, executed from the census file's own AST (row content is never retyped here)
NAMES = ("CD", "DQ", "dq", "role", "T", "DN", "K", "PRIM", "Q", "QK", "W", "LOC", "OBT", "A0", "S_REF", "L_REF", "FORMS")
tree = ast.parse(open(CENSUS, encoding="utf-8").read())
picked = [n for n in tree.body if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and n.targets[0].id in NAMES]
ns = {"os": os, "json": json, "ROOT": ROOT}
exec(compile(ast.Module(body=picked, type_ignores=[]), CENSUS, "exec"), ns)                    # noqa: S102 - the census's own definitions
gate("CE census assignments executed: {0} of {1} names, lines {2}".format(len(picked), len(NAMES), [n.lineno for n in picked]),
     sorted(n.targets[0].id for n in picked) == sorted(NAMES), [n.targets[0].id for n in picked])
RAW = ns["FORMS"]["S"]
print("FACT census form S: {0} actions (OBT {1} + A0 {2} + S_REF {3}); ids {4}".format(len(RAW), len(ns["OBT"](686)), len(ns["A0"]), len(ns["S_REF"]),
      [a["id"] for a in RAW]), flush=True)
gate("N action count {0} <= {1} (brief step 1)".format(len(RAW), MAXACT), len(RAW) <= MAXACT, len(RAW))
# ---- (c1) aliases the schema refuses
PAT = re.compile(r"^[A-Za-z]+[0-9]+$")
bad_as = sorted(set(a[k] for a in RAW for k in ("as", "selector_as") if a.get(k) and not PAT.match(a[k])))
REN = {"SQR": "QS1", "TCI": "TC1", "TCO": "TC2", "TQI": "TQ1", "TQO": "TQ2"}
SRS = set(a["as"] for a in RAW if a["op"] == "add_shift_reg")
used = set(a[k] for a in RAW for k in ("as", "selector_as") if a.get(k))
gate("V (c1) aliases refused by the schema pattern == the declared rename set {0}; new names unused".format(sorted(REN)),
     bad_as == sorted(REN) and not (set(REN.values()) & used), {"bad": bad_as, "collide": sorted(set(REN.values()) & used)})


def ren_sym(s):
    if not (isinstance(s, str) and s.startswith("new:")):
        return s
    head, dot, tail = s[4:].partition(".")
    if head in REN:
        head = REN[head]
    elif head[:-1] in REN and head[:-1] in SRS and head[-1] in "LR":
        head = REN[head[:-1]] + head[-1]
    return "new:" + head + dot + tail


def ren_any(x):
    if isinstance(x, dict):
        return dict((k, (REN.get(v, v) if k in ("as", "selector_as") else ren_any(v))) for k, v in x.items())
    if isinstance(x, list):
        return [ren_any(v) for v in x]
    return ren_sym(x)


ACTS = [ren_any(copy.deepcopy(a)) for a in RAW]
chg = [(a["id"], k) for a, b in zip(RAW, ACTS) for k in a if a[k] != b[k]]
print("FACT (c1) renamed fields (action, field): {0}".format(chg), flush=True)
# ---- (c2) + (c3): data_stream + why
ROW = {"c_qk": "S1", "c_obt": "S2", "w_qk_obt": "S3", "c_km1": "4", "i_rec": "5", "c_case": "6", "c_enq": "7", "t_el": "8", "w_el_in": "8",
       "w_el_enq": "8", "sr_n": "11", "c_k0": "12", "w_k0": "12", "c_inc": "13", "t_ci": "14", "w_ci_in": "14", "w_ci_inc": "14", "t_co": "15",
       "w_inc_co": "15", "w_co_r": "15", "w_false_pass": "16", "c_lw": "17", "w_final": "18", "sr_q": "S4", "w_obt_srq": "S5", "t_qi": "S6",
       "w_srq_qi": "S6", "w_qi_enq": "S6", "t_qo": "S7", "w_enq_qo": "S7", "w_qo_srq": "S7", "w_q_false": "S8"}
gate("W every action has a census row reference", sorted(ROW) == sorted(a["id"] for a in ACTS), sorted(set(a["id"] for a in ACTS) ^ set(ROW)))
for a in ACTS:
    src = "S_REF" if ROW[a["id"]].startswith("S") and a["id"] not in ("c_qk", "c_obt", "w_qk_obt") else ("OBT(686)" if a["id"] in ("c_qk", "c_obt", "w_qk_obt") else "A0")
    a["why"] = ("c154-a3-2 P5-1 form S (PD374(a)(c), PD376(a)): census diag_c154_a3_1_census.py {0}, p5_route_census.md row {1}".format(src, ROW[a["id"]]))
    if a["id"] in ("c_obt", "c_enq"):
        a["data_stream"] = True
        a["why"] += "; DATA stream 1.2 -> 1.7 results FIFO (PD374(a), CLAUDE.md 1c'': queues for lossless data only)"
gate("DS (c2) data_stream true on exactly c_obt, c_enq", sorted(a["id"] for a in ACTS if a.get("data_stream")) == ["c_enq", "c_obt"])
# ---- (c4) declared term classes vs measured graphs
GR, PG = J(GRAPH), J(POOL)
dq = ns["role"]
qnames = set(t["name"] for r in ("obtain", "enqueue", "dequeue", "release") for t in dq[r]["terminals"])
pq = collections.Counter(r["term_class"] for r in PG["terminals"] if r["owner_class"] == "Function" and r["term_name"] in qnames)
ac = collections.Counter(r["term_class"] for r in GR["terminals"] if r["owner_class"] == "ArrayConstant")
dn = collections.Counter(r["term_class"] for r in GR["terminals"] if r["owner_class"] == "DigitalNumericConstant")
inc = dict(((r["term_name"], bool(r["is_source"])), r["term_class"]) for r in GR["terminals"] if int(r["owner_uid"]) == 1978)
print("FACT TC pool graph {0} md5 {1}: queue-name Function terminal classes {2}; s09 ArrayConstant {3}; DigitalNumericConstant {4}; #1978 {5}".format(
      rel(POOL), md5(POOL), dict(pq), dict(ac), dict(dn), inc), flush=True)
decl = []
for a in ACTS:
    for t in a.get("terminals") or []:
        if a.get("prim") in ns["PRIM"].values():
            m = "ParameterTerminal" if list(pq) == ["ParameterTerminal"] else None
        elif a.get("class") == "ArrayConstant":
            m = list(ac)[0] if len(ac) == 1 else None
        elif a.get("class") == "DigitalNumericConstant":
            m = list(dn)[0] if len(dn) == 1 else None
        elif a.get("prim") == "Increment":
            m = inc.get((t["name"], bool(t["is_source"])))
        elif a.get("class") == "Local":
            m = "Terminal"                                       # census LOC; local rows of the s09 graph checked below
        else:
            m = None
        decl.append((a["id"], t["name"], t.get("term_class"), m))
lc = collections.Counter(r["term_class"] for r in GR["terminals"] if r["owner_class"] in ("Local", "LocalVariable"))
print("FACT TC s09 Local terminal classes {0}".format(dict(lc)), flush=True)
gate("TC every declared term_class == the measured one ({0} terminals)".format(len(decl)),
     all(d[2] == d[3] for d in decl) and (not lc or list(lc) == ["Terminal"]), [d for d in decl if d[2] != d[3]])
# ---- plan inputs
TOP = {"schema": "stageplan/1", "context": {"s1_key": "D1_s1_copy"}}
BASEREF = {"path": rel(GRAPH), "md5": md5(GRAPH)}
os.makedirs(PAROOT, exist_ok=True)
json.dump(dict(TOP, stage="ring_p5s01a", goal="card 154-a3-2 PASS A: P5-1 form S ({0} actions) on the real s09 graph, no open_rows".format(len(ACTS)),
               base=BASEREF, actions=ACTS), open(AIN, "w", encoding="utf-8"), indent=1)
ok_, why_ = protocol.validate_obj(J(AIN))
gate("S0 pass-A input validates against stageplan/1 ({0} actions)".format(len(ACTS)), ok_, why_)
SA = SS.simulate(AIN, GRAPH, out_root=PAROOT, plan_out_dir=PAROOT, log=lambda *x: None, route_check=False)


def step_facts(tag, R_):
    out = {}
    for st in (R_ or {}).get("steps") or []:
        p_ = (st.get("file") or {}).get("path")
        sj = J(p_)
        out[st["n"]] = hashlib.md5(json.dumps(sj["state"], sort_keys=True, default=str).encode("utf-8")).hexdigest()
        print("FACT STEP {0} n {1:02d} op {2} id {3}: {4} model {5}; file {6} md5 {7}; state {8}".format(
              tag, st["n"], st.get("op"), st.get("id"), "ERROR " + str(st.get("error")) if st.get("error") else ("PROVISIONAL" if st.get("provisional") else "ok"),
              st.get("model_source"), p_ and rel(p_), p_ and md5(p_), out[st["n"]][:8]), flush=True)
    return out


HA = step_facts("PASSA", SA)
provA = [s["n"] for s in SA["steps"] if s.get("provisional")]
gate("SA pass A replays every action to its end: failed {0}; steps {1} == actions + 1; collect-all PROVISIONAL steps {2}".format(
     json.dumps(SA.get("failed")), len(SA["steps"]), provA), SA["failed"] is None and len(SA["steps"]) == len(ACTS) + 1 and not provA
     and SA.get("end_cdiff_rows") is not None, SA.get("failed"))
s09 = J(S09)
ok_pairs = dict(((int(r["node"]), r["term"]), "s09-open") for r in s09.get("open_rows") or [])
ties, untied = {}, []
for key in SA["end_cdiff_rows"]:                                                              # prep_c152_b2_1_mk.py:337-350, copied
    n0 = SA["steps"][-1]["n"]
    for st in reversed(SA["steps"]):
        if st.get("cdiff_rows") is not None and key in st["cdiff_rows"]:
            n0 = st["n"]
        else:
            break
    p = (SS.V.key_parts(key)[0], SS.V.key_parts(key)[2])
    if n0 >= 1:
        ties[key] = {"n": n0, "id": ACTS[n0 - 1]["id"], "op": ACTS[n0 - 1]["op"], "class": ACTS[n0 - 1].get("class") or ACTS[n0 - 1]["op"], "pair": p}
    elif p in ok_pairs:
        ties[key] = {"n": 0, "id": ok_pairs[p], "op": "base", "class": "step0-declared", "pair": p}
    else:
        untied.append((key, n0))
print("FACT TIE end rows {0}: by action {1}; step-0 declared {2}".format(len(SA["end_cdiff_rows"]),
      sorted((k, t["id"]) for k, t in ties.items() if t["n"] >= 1), sum(1 for t in ties.values() if t["n"] == 0)), flush=True)
gate("TIE every end row ({0}) tied to a P5-1 action or an s09 open row".format(len(SA["end_cdiff_rows"])), not untied, untied[:10])
orows, seen = [], set()
for k in sorted(ties, key=lambda k: (ties[k]["n"], k)):
    t = ties[k]
    if t["pair"] not in seen:
        seen.add(t["pair"])
        orows.append({"node": int(t["pair"][0]), "term": t["pair"][1], "why": ("c154-a3-2: made by P5-1 action {0} (#{1} {2} {3})".format(
            t["id"], t["n"], t["op"], t["class"]) if t["n"] >= 1 else "c154-a3-2: open at step 0 = declared open row of plan_ring_p4_s09v18.json")[:300]})
GOAL = ("RING P5-1 (card 154-a3-2, PD374(a)(c) + PD376(a) form S): Obtain + const on 686, refnum SR on loop 1.2, Case on RingSeqCheck valid + Enqueue(#2626) "
        "+ count SR, records final -1 on #4866 + local after 1.2; {0} actions from the diag_c154_a3_1 census, on the REAL s09 graph 22f967b5").format(len(ACTS))
json.dump(dict(TOP, stage="ring_p5s01", goal=GOAL[:400], base=BASEREF, open_rows=orows, actions=ACTS), open(IN, "w", encoding="utf-8"), indent=1)
ok_, why_ = protocol.validate_obj(J(IN))
gate("S1 plan input validates ({0} actions, {1} open pairs)".format(len(ACTS), len(orows)), ok_, why_)
SB = SS.simulate(IN, GRAPH, out_root=SIM, plan_out_dir=B, log=lambda m: print(m, flush=True), route_check=True)
HB = step_facts("REALSIM", SB)
p = J(OUT) if os.path.isfile(OUT) else {}
fz = p.get("finalized") or {}
provB = [s["n"] for s in SB["steps"] if s.get("provisional")]
gate("SB REALSIM plan FINAL on the real graph: failed {0}; route check {1}; fs_border_gate {2}; open_rows_match; end rows == pass A; PROVISIONAL {3}".format(
     SB.get("failed"), (fz.get("route_check") or {}).get("status"), (fz.get("fs_border_gate") or {}).get("status"), provB),
     bool(SB["final"]) and p.get("final") is True and fz.get("open_rows_match") is True and (fz.get("route_check") or {}).get("status") == "PASS"
     and sorted(SB.get("end_cdiff_rows") or []) == sorted(SA["end_cdiff_rows"]) and not provB, {"final": SB["final"], "rc": fz.get("route_check")})
gate("SAME pass A and REALSIM step states equal at every step ({0} steps)".format(len(HA)), HA == HB,
     [n for n in sorted(set(HA) | set(HB)) if HA.get(n) != HB.get(n)])
for r in (fz.get("route_check") or {}).get("rows") or []:
    print("FACT ROUTE k {0} {1} {2}: {3} {4}".format(r.get("k"), r.get("op"), r.get("ids"), r.get("route"), (r.get("how") or "")[:80]), flush=True)
# ---- X10, X8, X17
MODEL = SPR.load_memory_model()
XS = SPR.x10_start(S09VI_MD5, MODEL)
START = XS[0] if XS else None
ops = SX.compile_plan(p)
cps = sorted({0, len(ops)} | set(k for k, o in enumerate(ops, 1) if o["kind"] in SX.BIND_KINDS))
mp = SPR.x10_model_peak([o["kind"] for o in ops], cps, model=MODEL, start_mb=START)
v = lambda k: float(MODEL[k]["value"])                                                        # noqa: E731
MAIN = round(mp["peak_mb"] + MAIN_SRC_READS * v("read_mb"), 1)
print("FACT X10 start {0} ({1}); ops {2} kinds {3}; checkpoints {4}; N {5} R {6}; Executor peak {7}; MAIN {8}; fail_above {9}; MEMSTOP {10}".format(
      START, XS and XS[1], len(ops), dict(collections.Counter(o["kind"] for o in ops)), cps, mp["N"], mp["R"], mp["peak_mb"], MAIN, SPR.X10_FAIL_MB,
      SX.MEM_STOP_MB), flush=True)
gate("X10 MAIN {0} <= {1} at the measured s09 start {2} (Executor {3}; MEMSTOP {4} unchanged)".format(MAIN, SPR.X10_FAIL_MB, START, mp["peak_mb"], SX.MEM_STOP_MB),
     START is not None and MAIN <= 680.0 and SPR.X10_FAIL_MB == 680.0 and SX.MEM_STOP_MB == 695, mp)
lint = SPR.control_path_lint(p)
gate("X8 control_path_lint clean (queue creates carry data_stream + why; no edge detector)", not lint, lint)
ok17, det17 = SPR.x17_gate([p])
gate("X17 x17_gate over the plan", ok17, det17)
# ---- sink-gate census (prep_c152_b2_1_mk.py:416-435, copied): wire rows whose dst is a ControlTerminal in the sim state before
SF = dict((int(x["n"]), x["path"]) for x in fz.get("step_files") or [])
SGC = []
for n, a in enumerate(p["actions"], 1):
    if a.get("op") != "wire" or n not in SF or (n - 1) not in SF:
        continue
    eff = J(SF[n]).get("effect") or {}
    prev = J(SF[n - 1])["state"]["terminals"]
    du, su = eff.get("dst_term_uid"), eff.get("src_term_uid")
    rd = next((r for r in prev if r["term_uid"] == du), None)
    rs = next((r for r in prev if r["term_uid"] == su), None)
    if rd is not None and SX.is_ct(rd):
        route = "indicator" if (rs is not None and rs.get("wire_uid")) else "ctlsink"
        SGC.append({"n": n, "id": a["id"], "sink": [rd["owner_uid"], rd["term_name"]], "dst_term_uid": du, "src_term_uid": su, "route": route,
                    "needs_sink_gate": route == "indicator"})
print("FACT SG-CENSUS {0} ControlTerminal-sink row(s); {1} need a declared sink gate: {2}".format(
      len(SGC), sum(1 for e in SGC if e["needs_sink_gate"]), SGC), flush=True)
json.dump({"card": "154-a3-2", "plan": {"path": rel(OUT), "md5": md5(OUT)}, "actions": len(ACTS), "ops": len(ops), "kinds": dict(collections.Counter(o["kind"] for o in ops)),
           "census_source": {"path": rel(CENSUS), "md5": md5(CENSUS), "names": list(NAMES)}, "renames_c1": REN, "renamed_fields": chg,
           "data_stream_c2": ["c_obt", "c_enq"], "term_class_c4": decl, "start_mb": START, "start_cite": XS and XS[1], "exec_peak_mb": mp["peak_mb"],
           "main_peak_mb": MAIN, "main_src_reads": MAIN_SRC_READS, "checkpoints": cps, "open_rows": len(orows), "end_rows": len(SA["end_cdiff_rows"]),
           "ties": dict((k, t) for k, t in ties.items()), "sink_gate_census": SGC, "passA_states": HA, "realsim_states": HB,
           "steps": [{"n": s["n"], "op": s.get("op"), "id": s.get("id"), "model_source": s.get("model_source"), "file": rel(s["file"]["path"]),
                      "md5": s["file"]["md5"]} for s in SB["steps"]]},
          open(FACTS, "w", encoding="utf-8"), indent=1, default=str)
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (AIN, IN, OUT, FACTS))
gate("U inputs untouched", all(md5(q) == M0[q] for q in WANT))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
