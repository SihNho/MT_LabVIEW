# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_155-a2-1.md
# ---
r"""prep_c155_a2_1_mk - card 155-a2-1 (OFFLINE, json only, no LabVIEW, no COM): P5-1b = actions 21..32 of the P5-1 form-S fragment
(plan_ring_p5s01_in.json fabc4b9c), planned on the REAL P5-1a graph graph_ring_p5s01a_20261009_103621.json bd67a511 (VI 2482fe7b, never opened).
COPY of prep_c154_a4_1_mk.py (e65b41d3). CHANGED lines, stated before the run (brief_155-a2-1.md items 1-4):
  (c1) pins stagexec 53e17623, stagesim eb99c6ba, docs/d1/ring-p5.md a4b596f0; session table prep_c155_a2_1_session.json; card strings.
       Gate P: the pass-A input left by card 154-a4-1's failed run (sim/ring_p5s01b/_passA/plan_ring_p5s01bp_in.json) is printed, not
       refused (it is this script's own scratch input and is overwritten); the plan / plan_in / session must not exist.
  (c2) FRAME MAP (brief item 3, nothing retyped): a `frame` NAME on an end whose tunnel (`tunnel` action, P5-1a's or P5-1b's) sits on the
       P5-1a case new:CQ1 -> its index in that case's `frames` list (plan_ring_p5s01_in.json c_case) -> symbol 'new:CQ1.f<k>' -> sim uid
       (P5-1a sim end) -> REAL diagram uid (STEPX bound) -> '#<uid>'; checked == stagesim.base_case_frames(graph owners, real case)[k].
  (c3) BASE seen by every compile (brief item 2): compile_plan(..., owners=stagexec.plan_base_owners({'base': graph ref})) - the
       existing helper (stagexec.py:621), not a re-implemented owner read; the plan_in / plan carry `base`, so pass A, REALSIM, the X10
       compile and the recipes' compile see it too.
  (c4) OPS gate (brief item 4): the 8 compiled kinds == the whole-P5-1 compile's ops 15..22 kinds (read, not typed); both
       connect_term_uid variant register_end_case_border on the real case; both case_frame_wire on the real case at the mapped frame.
Existing tools used (no new op, no tool edit): stagesim.simulate / base_case_frames, stagexec.compile_plan / plan_base_owners / is_ct /
BIND_KINDS, stage_prerun x10_start / x10_model_peak / control_path_lint / x17_gate, protocol.validate_obj.
PREDICTION CONTRACT: M0 pins; R 12 actions; MAP every P5-1a symbol used (TC1, TC2, SN1R, QO1, CQ1, EQ1) -> a real uid with rows; FRM
  'False' -> '#30914' == base_case_frames(30726)[0]; C compiles; OPS 8 ops as item 4; SA pass A 12 actions, failed None, 0 PROVISIONAL;
  CUT all 12 fit (X10 MAIN <= 680); TIE; SB REALSIM FINAL, route check PASS, states == pass A; X10 == MAIN(n*); X8 clean; X17 clean; U inputs.
    py tools/bgrun.py --material --max-min 10 --log tools/bench/prep_c155_a2_1_mk.log -- py -u tools/bench/prep_c155_a2_1_mk.py"""
import collections, copy, hashlib, json, os, re, sys                                          # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagesim as SS, stagexec as SX, stage_prerun as SPR                                   # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
SIM = os.path.join(B, "sim")
GRAPH = os.path.join(B, "graph_ring_p5s01a_20261009_103621.json")
SRC_IN, SRC_PLAN = os.path.join(B, "plan_ring_p5s01_in.json"), os.path.join(B, "plan_ring_p5s01.json")
PA_PLAN, PA_SESS = os.path.join(B, "plan_ring_p5s01a.json"), os.path.join(B, "prep_c154_a3_2b_session.json")
PA_SCR = os.path.join(B, "diag_c154_p5s01a_scratch.log")
MMF = os.path.join(B, "memory_model.json")
PAROOT, PRROOT = os.path.join(SIM, "ring_p5s01b", "_passA"), os.path.join(SIM, "ring_p5s01b", "_probe")
AIN, IN, OUT = os.path.join(PAROOT, "plan_ring_p5s01bp_in.json"), os.path.join(B, "plan_ring_p5s01b_in.json"), os.path.join(B, "plan_ring_p5s01b.json")
FACTS = os.path.join(B, "prep_c155_a2_1_session.json")
PAVI_MD5 = "2482fe7bf3426e18b0801c77ec629073"
WANT = {GRAPH: "bd67a511", SRC_IN: "fabc4b9c", SRC_PLAN: "ed6ceb9e", PA_PLAN: "ed62e8d6", PA_SESS: "a50bf0a5", MMF: "386a4cf4",
        os.path.join(ROOT, "docs", "d1", "ring-p5.md"): "a4b596f0", os.path.join(ROOT, "tools", "stagesim.py"): "eb99c6ba",
        os.path.join(ROOT, "tools", "stagexec.py"): "53e17623", os.path.join(ROOT, "tools", "stage_prerun.py"): "9decb20f",
        os.path.join(ROOT, "tools", "vigraph.py"): "a7eb58c7"}
MAIN_SRC_READS = 2                                    # main recipe source census_snapshot reads (prep_c152_b2_1_mk.py:79)
MAXACT, LIMIT = 40, 680.0
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
print("FACT P pre-existing pass-A scratch input (154-a4-1's failed run, overwritten here): {0}".format(
      [rel(p) for p in (AIN,) if os.path.exists(p)]), flush=True)
pre = [p for p in (IN, OUT, FACTS) if os.path.exists(p)]
gate("P no pre-existing P5-1b plan / plan_in / session file", not pre, pre)
# ---- rows
SIN, SPL, PSS = J(SRC_IN), J(SRC_PLAN), J(PA_SESS)
ALL = SIN["actions"]
gate("R rows of plan_ring_p5s01_in.json ({0}) == plan_ring_p5s01.json's ({1}), field for field".format(len(ALL), len(SPL["actions"])),
     ALL == SPL["actions"], [a["id"] for a, b in zip(ALL, SPL["actions"]) if a != b])
K0 = int(PSS["cut"]["k_actions"])
RAW = copy.deepcopy(ALL[K0:])
gate("R2 P5-1b = actions {0}..{1} ({2} actions): {3}".format(K0 + 1, len(ALL), len(RAW), [a["id"] for a in RAW]), len(RAW) == 12, len(RAW))
# ---- symbol map
PAP = J(PA_PLAN)
last = max((PAP.get("finalized") or {}).get("step_files") or [], key=lambda x: int(x["n"]))
SYM = J(last["path"])["state"]["sym"]
BOUND = {}
for ln in open(PA_SCR, encoding="utf-8", errors="replace"):
    m = re.search(r"STEPX\s+\d+\s+.*bound (\{[^}]*\})", ln)
    if m:
        BOUND.update(dict((int(k), int(v)) for k, v in re.findall(r"(-?\d+):\s*(-?\d+)", m.group(1))))
print("FACT MAP sources: sim end {0} md5 {1}; sym {2}; bound {3} (from {4} md5 {5})".format(
      rel(last["path"]), md5(last["path"])[:8], SYM, BOUND, rel(PA_SCR), md5(PA_SCR)[:8]), flush=True)
GR = J(GRAPH)
OWN = GR.get("owners") or {}
rows_of = lambda u: [r for r in GR["terminals"] if int(r["owner_uid"]) == int(u) or int(r["term_uid"]) == int(u)]   # noqa: E731
made = set("new:" + a["as"] for a in RAW if a.get("as")) | set("new:" + a["as"] + s for a in RAW if a.get("op") == "add_shift_reg" for s in "LR")


def refs(x, acc):
    if isinstance(x, str) and x.startswith("new:"):
        h = x if re.search(r"\.f[0-9]+$", x) else x.split(".", 1)[0]
        acc.add(h)
    elif isinstance(x, dict):
        for v in x.values():
            refs(v, acc)
    elif isinstance(x, list):
        for v in x:
            refs(v, acc)
    return acc


used = sorted(s for s in refs(RAW, set()) if s not in made)
REAL, bad = {}, []
for s in used:
    su = SYM.get(s)
    ru = BOUND.get(su) if su is not None else None
    if ru is None:
        bad.append((s, su, "no sim uid / no bound entry"))
        continue
    if re.search(r"\.f[0-9]+$", s):
        ow = OWN.get(str(ru))
        ok = bool(ow) and ow[0] == "CaseStructure" and int(ow[1]) == REAL.get(s.rsplit(".", 1)[0], BOUND.get(SYM.get(s.rsplit(".", 1)[0])))
        print("FACT MAP {0} -> sim {1} -> real diagram #{2}; owners entry {3}".format(s, su, ru, ow), flush=True)
    else:
        rr = rows_of(ru)
        ob = [o for o in GR.get("objs") or [] if int(o["uid"]) == int(ru)]     # a Case owns no terminal rows (diag_c154_a3_3_nodes.log:49)
        ok = bool(rr) or bool(ob)
        print("FACT MAP {0} -> sim {1} -> real #{2} ({3} rows; obj {4}): {5}".format(s, su, ru, len(rr), ob, [(r["term_uid"], r["term_name"],
              r["term_class"], r["frame_diagram"], r["wire_uid"], bool(r["is_source"])) for r in rr]), flush=True)
    REAL[s] = ru
    if not ok:
        bad.append((s, su, ru))
gate("MAP every P5-1a symbol P5-1b uses ({0}) -> a real uid present in the P5-1a graph".format(used), not bad, bad)
# ---- (c2) frame map: a frame NAME of the P5-1a case -> '#<real frame diagram uid>'
TUN_CASE = dict(("new:" + a["as"], a.get("loop")) for a in ALL if a.get("op") == "tunnel" and a.get("as"))
CASE_FR = dict(("new:" + a["as"], list(a.get("frames") or SS.CASE_FRAMES_DEFAULT)) for a in ALL if a.get("op") == "create"
               and a.get("class") == "CaseStructure" and a.get("as"))
FMAP, fbad = {}, []
for a in RAW:
    for e in (a.get("src"), a.get("dst")):
        if not (isinstance(e, dict) and e.get("frame") is not None):
            continue
        cs = TUN_CASE.get(e.get("uid"))
        fl = CASE_FR.get(cs) or []
        if cs is None or e["frame"] not in fl:
            fbad.append((a["id"], e))
            continue
        k = fl.index(e["frame"])
        fs = "{0}.f{1}".format(cs, k)
        ru = BOUND.get(SYM.get(fs))
        rc = BOUND.get(SYM.get(cs))
        gfr = SS.base_case_frames(OWN, rc) if rc is not None else []
        ok = ru is not None and len(gfr) > k and gfr[k] == ru
        FMAP[(a["id"], e["uid"])] = {"case_sym": cs, "frame_name": e["frame"], "index": k, "frame_sym": fs, "sim": SYM.get(fs), "real_frame": ru,
                                     "real_case": rc, "graph_frames": gfr, "ok": ok, "addr": "#{0}".format(ru)}
        print("FACT FRM {0} end {1}: frame {2!r} = index {3} of {4} {5} -> {6} -> sim {7} -> real diagram #{8}; graph frames of #{9} {10}[{3}] == {8}: {11}".format(
              a["id"], e["uid"], e["frame"], k, cs, fl, fs, SYM.get(fs), ru, rc, gfr, ok), flush=True)
        if not ok:
            fbad.append((a["id"], e, ru, gfr))
gate("FRM every `frame` name ({0} end(s)) -> '#<real frame uid>' == stagesim.base_case_frames(graph, case)[k]: {1}".format(
     len(FMAP), sorted(set((v["frame_name"], v["addr"]) for v in FMAP.values()))), FMAP and not fbad, fbad)


def sub(x, key=None):
    if isinstance(x, str) and x.startswith("new:"):
        h = x if re.search(r"\.f[0-9]+$", x) else x.split(".", 1)[0]
        if h in REAL:
            if key in ("src", "dst") and "." in x:
                return {"uid": REAL[h], "term": x.split(".", 1)[1]}
            return REAL[h]
        return x
    if isinstance(x, dict):
        return dict((k, sub(v, k)) for k, v in x.items())
    if isinstance(x, list):
        return [sub(v) for v in x]
    return x


ACTS = []
for r in RAW:
    a = sub(r)
    for k_ in ("src", "dst"):
        if isinstance(r.get(k_), dict) and r[k_].get("frame") is not None:
            a[k_] = dict(a[k_], frame=FMAP[(r["id"], r[k_]["uid"])]["addr"])
    ACTS.append(a)
for a, r in zip(ACTS, RAW):
    ch = dict((k, [r[k], a[k]]) for k in a if a[k] != r[k])
    print("FACT ROW {0} {1}: changed {2}".format(r["id"], r["op"], ch), flush=True)
TOP = {"schema": "stageplan/1", "context": SIN.get("context") or {"s1_key": "D1_s1_copy"}}
BASEREF = {"path": rel(GRAPH), "md5": md5(GRAPH)}
OWNERS = SX.plan_base_owners({"base": BASEREF})                                               # (c3) the existing helper, stagexec.py:621
gate("BO base owner map read by stagexec.plan_base_owners from {0} ({1} entries); case #{2} frames {3}".format(
     BASEREF["path"], len(OWNERS), REAL.get("new:CQ1"), SS.base_case_frames(OWNERS, REAL.get("new:CQ1"))), OWNERS == OWN and bool(OWNERS))


def try_compile(acts):
    try:
        ops = SX.compile_plan(dict(TOP, actions=acts), owners=OWNERS)
        return ops, None
    except SX.ExecStop as e:
        return None, str(e)


OPS, cerr = try_compile(ACTS)
if cerr:
    keep = [a for a in ACTS if not any(isinstance(e, dict) and e.get("frame") is not None for e in (a.get("src"), a.get("dst")))]
    pops, perr = try_compile(keep)
    print("FACT PROBE compile without the {0} `frame` wire(s): {1}".format(len(ACTS) - len(keep), perr or [(o["kind"], o["acts"],
          o.get("variant")) for o in pops]), flush=True)
gate("C the mapped P5-1b plan compiles (stagexec.compile_plan, base owners passed)", cerr is None, cerr)
KINDS = [o["kind"] for o in OPS]
WOPS = SX.compile_plan(SPL)
NA = int(PSS["cut"]["n_ops"])
print("FACT OPS P5-1b {0}".format([(o["kind"], o["acts"], o.get("variant"), o.get("case"), o.get("frame"), o.get("frame_index")) for o in OPS]), flush=True)
print("FACT OPS P5-1 ops {0}..{1} {2}".format(NA + 1, len(WOPS), [(o["kind"], [x - K0 for x in o["acts"]], o.get("variant")) for o in WOPS[NA:]]), flush=True)
cfw = [o for o in OPS if o["kind"] == "case_frame_wire"]
ctu = [o for o in OPS if o["kind"] == "connect_term_uid"]
RC = REAL.get("new:CQ1")
gate("OPS (brief item 4) {0} ops == P5-1 ops {1}..{2} kinds {3}; connect_term_uid x{4} register_end_case_border on #{5}; case_frame_wire x{6} on #{5} {7}".format(
     len(OPS), NA + 1, len(WOPS), [o["kind"] for o in WOPS[NA:]], len(ctu), RC, len(cfw), [(o.get("frame"), o.get("frame_index"), o.get("variant")) for o in cfw]),
     KINDS == [o["kind"] for o in WOPS[NA:]] and len(OPS) == 8
     and [[x - K0 for x in o["acts"]] for o in WOPS[NA:]] == [o["acts"] for o in OPS]
     and len(ctu) == 2 and all(o.get("variant") == "register_end_case_border" and o.get("case") == RC for o in ctu)
     and len(cfw) == 2 and all(o.get("case") == RC and o.get("frame") == "#{0}".format(BOUND[SYM["new:CQ1.f0"]]) and o.get("frame_index") == 0 for o in cfw),
     [(o["kind"], o["acts"], o.get("variant"), o.get("case")) for o in OPS])
# ---- the cut
MODEL = SPR.load_memory_model()
XS = SPR.x10_start(PAVI_MD5, MODEL)
START = XS[0] if XS else None
v = lambda k: float(MODEL[k]["value"])                                                        # noqa: E731


def main_of(n):
    cps = sorted({0, n} | set(k for k in range(1, n + 1) if KINDS[k - 1] in SX.BIND_KINDS))
    mp = SPR.x10_model_peak(KINDS[:n], cps, model=MODEL, start_mb=START)
    return round(mp["peak_mb"] + MAIN_SRC_READS * v("read_mb"), 1), mp, cps


TAB = [(n,) + main_of(n)[:1] for n in range(1, len(OPS) + 1)]
print("FACT CUT start {0} ({1}); ops {2}; per-prefix MAIN {3}".format(START, XS and XS[1], len(OPS), TAB), flush=True)
fit = [n for n, m in TAB if m <= LIMIT]
NS = max(fit) if fit else 0
gate("CUT longest prefix: n* {0} of {1} (MAIN {2} <= {3}); prefix fit is contiguous".format(NS, len(OPS), NS and TAB[NS - 1][1], LIMIT),
     NS >= 1 and fit == list(range(1, NS + 1)), TAB)
cov = sorted(a for o in OPS[:NS] for a in o["acts"])
KA = max(cov)
gate("AB ops 1..{0} cover exactly actions 1..{1} (action boundary); k {1} <= {2}".format(NS, KA, MAXACT), cov == list(range(1, KA + 1)) and KA <= MAXACT, cov)
REM = [{"n": K0 + n, "id": ACTS[n - 1]["id"]} for n in range(KA + 1, len(ACTS) + 1)]
print("FACT REMAINDER {0} actions: {1}".format(len(REM), REM), flush=True)
ACTS = ACTS[:KA]
os.makedirs(PAROOT, exist_ok=True)
json.dump(dict(TOP, stage="ring_p5s01bp", goal="card 155-a2-1 PASS A: P5-1b = actions {0}..{1} of P5-1 form S on the real P5-1a graph, no open_rows".format(
          K0 + 1, K0 + len(ACTS)), base=BASEREF, actions=ACTS), open(AIN, "w", encoding="utf-8"), indent=1)
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
     json.dumps(SA.get("failed"), default=str), len(SA["steps"]), provA), SA["failed"] is None and len(SA["steps"]) == len(ACTS) + 1 and not provA
     and SA.get("end_cdiff_rows") is not None, SA.get("failed"))
ok_pairs = dict(((int(r["node"]), r["term"]), "p5s01a-open") for r in PAP.get("open_rows") or [])
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
gate("TIE every end row ({0}) tied to a P5-1b action or a P5-1a open row".format(len(SA["end_cdiff_rows"])), not untied, untied[:10])
orows, seen = [], set()
for k in sorted(ties, key=lambda k: (ties[k]["n"], k)):
    t = ties[k]
    if t["pair"] not in seen:
        seen.add(t["pair"])
        orows.append({"node": int(t["pair"][0]), "term": t["pair"][1], "why": ("c155-a2-1: made by P5-1b action {0} (#{1} {2} {3})".format(
            t["id"], t["n"], t["op"], t["class"]) if t["n"] >= 1 else "c155-a2-1: open at step 0 = declared open row of plan_ring_p5s01a.json")[:300]})
GOAL = ("RING P5-1b (card 155-a2-1, PD374(e) remainder of P5-1 form S, PD378(b)): actions {0}..{1} ({2} ops) of plan_ring_p5s01.json - False-frame "
        "count pass-through, records-final local, refnum SR on loop 1.2 through the case to Enqueue; on the REAL P5-1a graph bd67a511, base case "
        "#{3} frames by diagram uid").format(K0 + 1, K0 + len(ACTS), NS, RC)
json.dump(dict(TOP, stage="ring_p5s01b", goal=GOAL[:400], base=BASEREF, open_rows=orows, actions=ACTS), open(IN, "w", encoding="utf-8"), indent=1)
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
ops = SX.compile_plan(p)                                                                      # the plan's own pinned base (plan_base_owners)
cps = sorted({0, len(ops)} | set(k for k, o in enumerate(ops, 1) if o["kind"] in SX.BIND_KINDS))
mp = SPR.x10_model_peak([o["kind"] for o in ops], cps, model=MODEL, start_mb=START)
MAIN = round(mp["peak_mb"] + MAIN_SRC_READS * v("read_mb"), 1)
print("FACT X10 start {0}; ops {1} kinds {2}; checkpoints {3}; N {4} R {5}; Executor peak {6}; MAIN {7}; fail_above {8}; MEMSTOP {9}".format(
      START, len(ops), dict(collections.Counter(o["kind"] for o in ops)), cps, mp["N"], mp["R"], mp["peak_mb"], MAIN, SPR.X10_FAIL_MB, SX.MEM_STOP_MB), flush=True)
gate("X10 P5-1b plan: kinds/acts == ops 1..{0}; MAIN {1} == MAIN(n*) {2} <= {3} at start {4} (Executor {5}; MEMSTOP {6} unchanged)".format(
     NS, MAIN, TAB[NS - 1][1], LIMIT, START, mp["peak_mb"], SX.MEM_STOP_MB),
     [(o["kind"], o["acts"]) for o in ops] == [(o["kind"], o["acts"]) for o in OPS[:NS]] and MAIN == TAB[NS - 1][1] and MAIN <= LIMIT
     and SPR.X10_FAIL_MB == LIMIT and SX.MEM_STOP_MB == 695, mp)
lint = SPR.control_path_lint(p)
gate("X8 control_path_lint clean (queue creates carry data_stream + why; no edge detector)", not lint, lint)
ok17, det17 = SPR.x17_gate([p])
gate("X17 x17_gate over the plan", ok17, det17)
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
json.dump({"card": "155-a2-1", "plan": {"path": rel(OUT), "md5": md5(OUT)}, "source_plan": {"path": rel(SRC_PLAN), "md5": md5(SRC_PLAN)},
           "symbol_map": REAL, "frame_map": dict(("{0}|{1}".format(*k), v_) for k, v_ in FMAP.items()), "actions": len(ACTS), "ops": len(ops),
           "cut": {"n_ops": NS, "k_actions": KA, "per_prefix_main": TAB, "limit": LIMIT},
           "remainder": REM, "kinds": dict(collections.Counter(o["kind"] for o in ops)), "start_mb": START, "start_cite": XS and XS[1],
           "exec_peak_mb": mp["peak_mb"], "main_peak_mb": MAIN, "main_src_reads": MAIN_SRC_READS, "checkpoints": cps, "open_rows": len(orows),
           "end_rows": len(SA["end_cdiff_rows"]), "ties": dict((k, t) for k, t in ties.items()), "sink_gate_census": SGC, "passA_states": HA,
           "realsim_states": HB, "steps": [{"n": s["n"], "op": s.get("op"), "id": s.get("id"), "model_source": s.get("model_source"),
                                           "file": rel(s["file"]["path"]), "md5": s["file"]["md5"]} for s in SB["steps"]]},
          open(FACTS, "w", encoding="utf-8"), indent=1, default=str)
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (AIN, IN, OUT, FACTS))
gate("U inputs untouched", all(md5(q) == M0[q] for q in WANT))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
