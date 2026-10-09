# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_154-a3-2b.md
# ---
r"""prep_c154_a3_2b_mk - card 154-a3-2b (OFFLINE, json only, no LabVIEW, no COM): P5-1a = the LONGEST op prefix of the P5-1 form-S fragment
(card 154-a3-2, plan_ring_p5s01.json ed6ceb9e, 32 actions = 22 ops) whose X10 MAIN <= 680.0 (docs/d1/ring-p5.md PD374(e): the cut point is the plan
maker's, inside the same order), planned on the REAL s09 graph graph_ring_p4s09_20261009_062044.json 22f967b5 (VI eb1d0f31, never opened).
COPY of prep_c154_a3_2_mk.py (56976dd5). CHANGED lines, stated before the run:
  (d1) names / paths: plan_ring_p5s01a{_in,}.json, pass A under sim/ring_p5s01a/_passA (stage ring_p5s01ap), REALSIM stage ring_p5s01a (sim/ring_p5s01a),
       session table prep_c154_a3_2b_session.json; card id strings.
  (d2) ROW SOURCE: the actions are READ from plan_ring_p5s01_in.json (fabc4b9c = card 154-a3-2's census-derived list with its (c1)-(c3) changes
       already applied), not re-derived from the census AST; they are checked == plan_ring_p5s01.json's actions; P5-1a = actions[:k] UNCHANGED
       (no field edited, `why` text included). The census-exec / rename / data_stream / term-class gates of the copy are therefore not re-run; they
       passed on these exact rows (prep_c154_a3_2_mk.log:5-14).
  (d3) THE CUT (by rule): ops = stagexec.compile_plan(plan_ring_p5s01.json); for n = 1..22, MAIN(n) = x10_model_peak(kinds[:n], {0, n} + bind ops
       <= n, start = stage_prerun.x10_start(eb1d0f31)) + 2 x read_mb (the copy's formula); n* = the largest n with MAIN(n) <= 680.0; k = max action
       of ops[:n*]; REFUSE unless ops[:n*] cover exactly actions 1..k (an action boundary) and k <= 40. Predicted: n* 14, k 20, MAIN 677.3.
  (d4) the remainder (actions k+1.., their census rows from `why`, their op numbers) and the prefix's END-ROW (TIE) list (owner, terminal, made by)
       are PRINTED (FACT REMAINDER / FACT TIE-ROW) for a later P5-1b plan; no plan for them is written.
  (d5) X10 gate on the P5-1a plan itself (compiled again from the REALSIM plan): its kinds == ops[:n*] and MAIN == MAIN(n*).
Existing tools used (no new op, no tool edit): stagesim.simulate, stagexec.compile_plan / is_ct / BIND_KINDS, stage_prerun x10_start / x10_model_peak /
control_path_lint / x17_gate, protocol.validate_obj.
PREDICTION CONTRACT: M0 pins; R rows of plan_ring_p5s01_in == plan_ring_p5s01 (32); CUT n* 14, k 20, MAIN 677.3 <= 680, MAIN(15) 681.2 > 680;
  SA pass A replays 20 actions, failed None, 0 PROVISIONAL; TIE every end row tied to a P5-1a action or an s09 open row; SB REALSIM FINAL, route
  check PASS, states == pass A; X10 == MAIN(n*); X8 clean; X17 clean; U inputs untouched.
    py tools/bgrun.py --material --max-min 10 --log tools/bench/prep_c154_a3_2b_mk.log -- py -u tools/bench/prep_c154_a3_2b_mk.py"""
import collections, hashlib, json, os, re, sys                                                # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagesim as SS, stagexec as SX, stage_prerun as SPR                                   # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
SIM = os.path.join(B, "sim")
GRAPH = os.path.join(B, "graph_ring_p4s09_20261009_062044.json")
SRC_IN, SRC_PLAN = os.path.join(B, "plan_ring_p5s01_in.json"), os.path.join(B, "plan_ring_p5s01.json")
S09 = os.path.join(B, "plan_ring_p4_s09v18.json")
MMF = os.path.join(B, "memory_model.json")
PAROOT = os.path.join(SIM, "ring_p5s01a", "_passA")
AIN, IN, OUT = os.path.join(PAROOT, "plan_ring_p5s01ap_in.json"), os.path.join(B, "plan_ring_p5s01a_in.json"), os.path.join(B, "plan_ring_p5s01a.json")
FACTS = os.path.join(B, "prep_c154_a3_2b_session.json")
S09VI_MD5 = "eb1d0f3107bbba49c9ae67a47c0ee50f"
WANT = {GRAPH: "22f967b5", SRC_IN: "fabc4b9c", SRC_PLAN: "ed6ceb9e", S09: "9d622c95", MMF: "6f2b5687",
        os.path.join(ROOT, "docs", "d1", "ring-p5.md"): "9c5ba571", os.path.join(ROOT, "tools", "stagesim.py"): "78b8d5a1",
        os.path.join(ROOT, "tools", "stagexec.py"): "1bab9cf9", os.path.join(ROOT, "tools", "stage_prerun.py"): "9decb20f",
        os.path.join(ROOT, "tools", "vigraph.py"): "a7eb58c7"}
MAIN_SRC_READS = 2                                    # main recipe source census_snapshot reads (prep_c152_b2_1_mk.py:79)
MAXACT, LIMIT = 40, 680.0                             # brief_154-a3-2b.md change 2
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
gate("P no pre-existing P5-1a plan / plan_in / session file", not pre, pre)
# ---- (d2) the rows, read from card 154-a3-2's plan files
SIN, SPL = J(SRC_IN), J(SRC_PLAN)
ALL = SIN["actions"]
gate("R rows of plan_ring_p5s01_in.json ({0}) == plan_ring_p5s01.json's ({1}), field for field".format(len(ALL), len(SPL["actions"])),
     ALL == SPL["actions"], [a["id"] for a, b in zip(ALL, SPL["actions"]) if a != b])
rowof = lambda a: (re.search(r"row (\S+)$", a.get("why", "").split(";")[0]) or [None, "?"])[1]   # noqa: E731  census row from the why
# ---- (d3) the cut
MODEL = SPR.load_memory_model()
XS = SPR.x10_start(S09VI_MD5, MODEL)
START = XS[0] if XS else None
v = lambda k: float(MODEL[k]["value"])                                                        # noqa: E731
OPS = SX.compile_plan(SPL)
KINDS = [o["kind"] for o in OPS]


def main_of(n):
    cps = sorted({0, n} | set(k for k in range(1, n + 1) if KINDS[k - 1] in SX.BIND_KINDS))
    mp = SPR.x10_model_peak(KINDS[:n], cps, model=MODEL, start_mb=START)
    return round(mp["peak_mb"] + MAIN_SRC_READS * v("read_mb"), 1), mp, cps


TAB = [(n,) + main_of(n)[:1] for n in range(1, len(OPS) + 1)]
print("FACT CUT start {0} ({1}); ops {2}; per-prefix MAIN {3}".format(START, XS and XS[1], len(OPS), TAB), flush=True)
fit = [n for n, m in TAB if m <= LIMIT]
NS = max(fit) if fit else 0
gate("CUT longest prefix: n* {0} (MAIN {1} <= {2}); next n {3} MAIN {4}; prefix fit is contiguous".format(
     NS, NS and TAB[NS - 1][1], LIMIT, NS + 1, TAB[NS][1] if NS < len(TAB) else None), NS >= 1 and fit == list(range(1, NS + 1)), TAB)
cov = sorted(a for o in OPS[:NS] for a in o["acts"])
KA = max(cov)
gate("AB ops 1..{0} cover exactly actions 1..{1} (action boundary); k {1} <= {2}".format(NS, KA, MAXACT), cov == list(range(1, KA + 1)) and KA <= MAXACT,
     cov)
for k, o in enumerate(OPS, 1):
    print("FACT OP {0:02d} {1} acts {2} ids {3} {4}".format(k, o["kind"], o["acts"], [ALL[a - 1]["id"] for a in o["acts"]],
          "P5-1a" if k <= NS else "REMAINDER"), flush=True)
REM = [{"n": n, "id": ALL[n - 1]["id"], "op": ALL[n - 1]["op"], "row": rowof(ALL[n - 1]),
        "op_no": next(k for k, o in enumerate(OPS, 1) if n in o["acts"])} for n in range(KA + 1, len(ALL) + 1)]
print("FACT REMAINDER {0} actions (ops {1}..{2}): {3}".format(len(REM), NS + 1, len(OPS), [(r["n"], r["id"], r["op"], "row " + r["row"], "op " + str(r["op_no"])) for r in REM]),
      flush=True)
ACTS = ALL[:KA]
# ---- plan inputs (pattern of the copy)
TOP = {"schema": "stageplan/1", "context": SIN.get("context") or {"s1_key": "D1_s1_copy"}}
BASEREF = {"path": rel(GRAPH), "md5": md5(GRAPH)}
os.makedirs(PAROOT, exist_ok=True)
json.dump(dict(TOP, stage="ring_p5s01ap", goal="card 154-a3-2b PASS A: P5-1a = first {0} actions of P5-1 form S on the real s09 graph, no open_rows".format(len(ACTS)),
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
for k in sorted(ties, key=lambda k: (ties[k]["n"], k)):
    t = ties[k]
    print("FACT TIE-ROW owner #{0} term {1!r} made by {2} (step {3}, {4}) key {5}".format(t["pair"][0], t["pair"][1], t["id"], t["n"], t["class"], k), flush=True)
gate("TIE every end row ({0}) tied to a P5-1a action or an s09 open row".format(len(SA["end_cdiff_rows"])), not untied, untied[:10])
orows, seen = [], set()
for k in sorted(ties, key=lambda k: (ties[k]["n"], k)):
    t = ties[k]
    if t["pair"] not in seen:
        seen.add(t["pair"])
        orows.append({"node": int(t["pair"][0]), "term": t["pair"][1], "why": ("c154-a3-2b: made by P5-1a action {0} (#{1} {2} {3})".format(
            t["id"], t["n"], t["op"], t["class"]) if t["n"] >= 1 else "c154-a3-2b: open at step 0 = declared open row of plan_ring_p4_s09v18.json")[:300]})
GOAL = ("RING P5-1a (card 154-a3-2b, PD374(e) cut of P5-1 form S, PD376(a)): the first {0} actions ({1} ops, X10 MAIN <= 680) of plan_ring_p5s01.json - "
        "Obtain + const on 686, Case on RingSeqCheck valid + Enqueue(#2626), count SR through the case; on the REAL s09 graph 22f967b5").format(len(ACTS), NS)
json.dump(dict(TOP, stage="ring_p5s01a", goal=GOAL[:400], base=BASEREF, open_rows=orows, actions=ACTS), open(IN, "w", encoding="utf-8"), indent=1)
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
# ---- X10 (d5), X8, X17
ops = SX.compile_plan(p)
cps = sorted({0, len(ops)} | set(k for k, o in enumerate(ops, 1) if o["kind"] in SX.BIND_KINDS))
mp = SPR.x10_model_peak([o["kind"] for o in ops], cps, model=MODEL, start_mb=START)
MAIN = round(mp["peak_mb"] + MAIN_SRC_READS * v("read_mb"), 1)
print("FACT X10 start {0}; ops {1} kinds {2}; checkpoints {3}; N {4} R {5}; Executor peak {6}; MAIN {7}; fail_above {8}; MEMSTOP {9}".format(
      START, len(ops), dict(collections.Counter(o["kind"] for o in ops)), cps, mp["N"], mp["R"], mp["peak_mb"], MAIN, SPR.X10_FAIL_MB, SX.MEM_STOP_MB), flush=True)
gate("X10 P5-1a plan: kinds/acts == ops 1..{0} of P5-1; MAIN {1} == MAIN(n*) {2} <= {3} at start {4} (Executor {5}; MEMSTOP {6} unchanged)".format(
     NS, MAIN, TAB[NS - 1][1], LIMIT, START, mp["peak_mb"], SX.MEM_STOP_MB),
     [(o["kind"], o["acts"]) for o in ops] == [(o["kind"], o["acts"]) for o in OPS[:NS]] and MAIN == TAB[NS - 1][1] and MAIN <= LIMIT
     and SPR.X10_FAIL_MB == LIMIT and SX.MEM_STOP_MB == 695, mp)
lint = SPR.control_path_lint(p)
gate("X8 control_path_lint clean (queue creates carry data_stream + why; no edge detector)", not lint, lint)
ok17, det17 = SPR.x17_gate([p])
gate("X17 x17_gate over the plan", ok17, det17)
# ---- sink-gate census (prep_c152_b2_1_mk.py:416-435, copied)
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
json.dump({"card": "154-a3-2b", "plan": {"path": rel(OUT), "md5": md5(OUT)}, "source_plan": {"path": rel(SRC_PLAN), "md5": md5(SRC_PLAN)},
           "actions": len(ACTS), "ops": len(ops), "cut": {"n_ops": NS, "k_actions": KA, "per_prefix_main": TAB, "limit": LIMIT},
           "remainder": REM, "kinds": dict(collections.Counter(o["kind"] for o in ops)), "start_mb": START, "start_cite": XS and XS[1],
           "exec_peak_mb": mp["peak_mb"], "main_peak_mb": MAIN, "main_src_reads": MAIN_SRC_READS, "checkpoints": cps, "open_rows": len(orows),
           "end_rows": len(SA["end_cdiff_rows"]), "ties": dict((k, t) for k, t in ties.items()), "sink_gate_census": SGC, "passA_states": HA,
           "realsim_states": HB, "steps": [{"n": s["n"], "op": s.get("op"), "id": s.get("id"), "model_source": s.get("model_source"),
                                           "file": rel(s["file"]["path"]), "md5": s["file"]["md5"]} for s in SB["steps"]]},
          open(FACTS, "w", encoding="utf-8"), indent=1, default=str)
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (AIN, IN, OUT, FACTS))
gate("U inputs untouched", all(md5(q) == M0[q] for q in WANT))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
