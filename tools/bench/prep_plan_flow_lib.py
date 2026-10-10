# ---
# labview: none
# hardware: none
# offline-args: --selftest
# evidence: tools/bench/cards/brief_164-a1-1.md
# ---
r"""prep_plan_flow_lib - card 164-a1-1 (OFFLINE, json only): the step-plan maker flow of prep_c163_a1_1_mk.py (run by prep_c163_a1_2_mk.py through text
substitutions), ONCE and parametrised, so a step maker is inputs + one call (docs/script-writing.md rules 1, 4). Nothing of the 163 files is changed.
  make_step_plan(...) == prep_c163_a1_1_mk.py:47-183 with: groups / action range / base graph / base VI / card / session file / plan names as arguments;
    START = stage_prerun.x10_start(md5(base VI)) (called, never typed); symbols bound per ADOPTED step (each step's last sim step file `sym` + the
    creation map of the run that saved its VI, stagekit.bound_from_cmap) - sim uids of different runs are never mixed; memory rule = the LONGEST
    prefix of whole groups with MAIN (X10 on SX.checkpoint_ops) <= limit and rows <= max_rows, tried in order, stopping at the first prefix that fails
    (163's two-candidate rule is the 2-group case). Calls: stagekit made/used/map_symbols, map_frames, apply_map, bound_from_cmap; prep_c156_a1_1_lib
    Gate / main_of / tie_rows / step_facts; stagesim.simulate; stagexec.compile_plan / plan_base_owners; stage_prerun load_creation_map / x10_start /
    load_memory_model / control_path_lint / x17_gate.
Self-test (--selftest): replays card 163-a1-2 (plan_ring_p5s02c.json 930699ec) from graph 431cfd83 and the UNEDITED input copy
plan_ring_p5s02r_in_pre164.json (d84634bd), into tools/bench/sim/ring_p5s02d/_replay163/: plan_in md5 == eb48fabc (163-a1-2's), every step-file md5 ==
930699ec's, the plan JSON equal after the replay path prefix is mapped back, except `finalized.at` and the summary md5 (the summary records the plan path).
PREDICTION: chosen I (A41..A52), MAIN(I) 658.3, MAIN(I+J) 677.0 > 675, REALSIM final True; replay compare PASS.
    py tools/bgrun.py --material --max-min 10 --log tools/bench/prep_plan_flow_lib.log -- py -u tools/bench/prep_plan_flow_lib.py --selftest"""
import collections, copy, json, os, shutil, sys                                              # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for _p in (ROOT, os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from tools import protocol                                                                   # noqa: E402
import stagekit as K                                                                         # noqa: E402
import stagesim as SS, stagexec as SX, stage_prerun as SPR                                   # noqa: E401,E402
import prep_c156_a1_1_lib as L                                                               # noqa: E402
md5, rel, J = L.md5, L.rel, L.J
B, SIM = os.path.join(ROOT, "tools", "bench"), os.path.join(ROOT, "tools", "bench", "sim")
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"


def leaves(x, pre=""):
    """{'/path': scalar} of a JSON value (dict keys / list indices joined by '/'). Same as prep_c163_a1_1_mk.py:74-79."""
    if isinstance(x, dict):
        return dict(kv for k, v in x.items() for kv in leaves(v, pre + "/" + k).items())
    if isinstance(x, list):
        return dict(kv for i, v in enumerate(x) for kv in leaves(v, pre + "/" + str(i)).items())
    return {pre: x}


def bind_sources(gate, sources, used, GR):
    """(REAL {symbol: real uid}, per-source info): each used symbol is bound by the ONE adopted step whose actions make it - that step's last sim step
    `sym` (sim uid) -> the creation map of the run that saved its VI (real uid), checked on the base graph GR by stagekit.map_symbols.
    sources = [{'name', 'plan', 'graph_after', 'vi'}]; a symbol made by no source or by two is a gate FAIL. Self-test: --selftest (163 replay, MAP gate)."""
    REAL, info, owner = {}, {}, collections.defaultdict(list)
    for s in sources:
        pj = J(s["plan"])
        mk = K.made_symbols(pj["actions"])
        for u in used:
            if u in mk or u.rsplit(".f", 1)[0] in mk:
                owner[u].append(s["name"])
        info[s["name"]] = {"plan": rel(s["plan"]), "plan_md5": md5(s["plan"]), "made_used": sorted(u for u in used if s["name"] in owner[u])}
    gate("OWN every used symbol is made by exactly one adopted step: {0}".format(dict(owner)), all(len(owner[u]) == 1 for u in used),
         [u for u in used if len(owner[u]) != 1])
    for s in sources:
        mine = info[s["name"]]["made_used"]
        if not mine:
            continue
        pj = J(s["plan"])
        last = max((pj.get("finalized") or {}).get("step_files") or [], key=lambda x: int(x["n"]))
        gate("E1 {0} last step file md5 == recorded {1}".format(s["name"], last["md5"][:8]), md5(os.path.join(ROOT, last["path"])) == last["md5"])
        sym = J(last["path"])["state"]["sym"]
        cm, cwhy, cmeta = SPR.load_creation_map({"plan": rel(s["plan"]), "md5": md5(s["plan"])}, J(s["graph_after"]))
        gate("CM creation map of the {0} run that saved {1}: {2} ({3})".format(s["name"], os.path.basename(s["vi"]), cmeta.get("path"), cwhy),
             cm is not None and os.path.normcase((cmeta.get("head") or {}).get("work") or "") == os.path.normcase(s["vi"]), cmeta.get("head"))
        _h, bound = K.bound_from_cmap(os.path.join(ROOT, cmeta["path"]))
        real, bad, lines = K.map_symbols(mine, sym, bound, GR)
        for ln in lines:
            print("FACT {0} {1}".format(s["name"], ln), flush=True)
        gate("MAP {0} symbols {1} -> real uids in the base graph".format(s["name"], mine), not bad, bad)
        REAL.update(real)
        info[s["name"]].update(sym=sym, bound=bound, cmap=cmeta.get("path"), work=(cmeta.get("head") or {}).get("work"), last_step=last)
    return REAL, info


def make_step_plan(gate, rin, groups, graph, base_vi, base_plan, sources, card, stage, plan_in, session, goal_fn, probe_goal,
                   plan_out_dir=B, sim_root=SIM, keep_prev=None, census=os.path.join(B, "prep_c156_a1_1_session.json"),
                   limit=675.0, max_rows=40, reads=2):
    """Make plan_<stage>.json (written ONLY by stagesim.simulate) from the rows of the whole `groups` (census names, in plan order) of `rin`, on the
    REAL `graph` of `base_vi`, chosen by the X10 prefix rule; returns the facts dict (also written to `session`). goal_fn(lo, hi, cand, chosen) ->
    plan goal text. Self-test: --selftest (replay of card 163-a1-2 -> 930699ec)."""
    RIN = J(rin)
    RA = RIN["actions"]
    POS = dict((a["id"], i) for i, a in enumerate(RA, 1))
    SESS = J(census)
    GRPS = dict((c["group"], (min(POS[x] for x in c["actions"]), max(POS[x] for x in c["actions"]), len(c["actions"]))) for c in SESS["census"])
    rng = [GRPS.get(g) for g in groups]
    gate("GRP census {0}: {1}; contiguous whole groups".format(groups, rng), all(rng) and all(r[1] - r[0] + 1 == r[2] for r in rng)
         and all(rng[i + 1][0] == rng[i][1] + 1 for i in range(len(rng) - 1)))
    LO, HI_ALL = rng[0][0], rng[-1][1]
    OUT = os.path.join(plan_out_dir, "plan_{0}.json".format(stage))
    if os.path.isfile(OUT) and keep_prev:
        shutil.copyfile(OUT, keep_prev)                         # keep a previous plan aside; the plan below is written by simulate only
        os.remove(OUT)
    print("FACT OLD previous {0} kept as {1}: {2}".format(rel(OUT), keep_prev and rel(keep_prev), md5(keep_prev) if keep_prev and os.path.isfile(keep_prev)
          else "none existed"), flush=True)
    GR, BP = J(graph), J(base_plan)
    RAW = copy.deepcopy(RA[LO - 1:HI_ALL])
    used = K.used_symbols(RAW, K.made_symbols(RAW))
    REAL, SRC = bind_sources(gate, sources, used, GR)
    gate("MAPALL every used symbol {0} bound".format(used), set(used) <= set(REAL), sorted(set(used) - set(REAL)))
    OWNERS = SX.plan_base_owners({"base": {"path": rel(graph), "md5": md5(graph)}})
    FMAP, fbad = {}, []
    fr_rows = [a for a in RAW if any(isinstance(a.get(k), dict) and a[k].get("frame") is not None for k in ("src", "dst"))]
    for s in sources:
        si = SRC[s["name"]]
        if "sym" in si:
            fm, fb, fl = K.map_frames(fr_rows, RA, si["sym"], si["bound"], OWNERS)
            for ln in fl:
                print("FACT {0} {1}".format(s["name"], ln), flush=True)
            mine = dict((k, v) for k, v in fm.items() if v["case_sym"] in si["made_used"])
            FMAP.update(mine)
            fbad += [b for b in fb if (b[0], b[1].get("uid")) not in fm or (b[0], b[1].get("uid")) in mine]
    nfe = sum(1 for a in fr_rows for k in ("src", "dst") if isinstance(a.get(k), dict) and a[k].get("frame") is not None)
    gate("FRM frame ends ({0} mapped of {1}) -> '#<real frame uid>': {2}".format(len(FMAP), nfe, sorted(set((v["frame_name"], v["addr"]) for v in FMAP.values()))),
         not fbad and all(v["ok"] for v in FMAP.values()), fbad)
    FULL = K.apply_map(RAW, REAL, FMAP)
    diff = []
    for r, a in zip(RAW, FULL):
        lr, la = leaves(r), leaves(a)
        ch = sorted(k for k in set(lr) | set(la) if lr.get(k) != la.get(k))
        anc = lambda k: k if k in lr or "/" not in k.strip("/") else anc(k.rsplit("/", 1)[0])           # noqa: E731
        okc = all(k.endswith("/frame") or str(lr.get(anc(k))).startswith("new:") for k in ch)
        if ch:
            print("FACT ROW A{0} {1}: mapped {2}".format(POS[r["id"]], r["id"], [(k, lr.get(k), la.get(k)) for k in ch])[:400], flush=True)
        if not okc:
            diff.append(r["id"])
    gate("ROWS stagekit.apply_map(A{0}..A{1}) == the input except symbol -> uid and frame -> '#uid' leaves".format(LO, HI_ALL), len(FULL) == len(RAW) and not diff, diff)
    STUBS = []
    for a in FULL:
        for side in ("src", "dst"):
            e = a.get(side)
            if isinstance(e, dict) and isinstance(e.get("uid"), int) and e.get("term_uid") is not None:
                ws = sorted(set(int(r.get("wire_uid") or 0) for r in GR["terminals"] if int(r["term_uid"]) == int(e["term_uid"])) - {0})
                STUBS.append((a["id"], side, e["term_uid"], ws))
                print("FACT END {0} {1} t{2}: wires in base graph {3}".format(a["id"], side, e["term_uid"], ws), flush=True)
    DW = [a for a in FULL if a["op"] == "delete_wire"]
    for a in DW:
        rows = [(int(r["owner_uid"]), r["term_name"], bool(r["is_source"])) for r in GR["terminals"] if int(r.get("wire_uid") or 0) == int(a["wire_uid"])]
        print("FACT DW {0} w{1} in base graph: rows {2}; sourceless {3}".format(a["id"], a["wire_uid"], rows, SS.sourceless_wire(SS.base_state(GR), a["wire_uid"])), flush=True)
    DO = [(a["id"], a["uid"], [o["class"] for o in GR.get("objs") or [] if int(o["uid"]) == int(a["uid"])], (GR.get("owners") or {}).get(str(a["uid"]))) for a in FULL if a["op"] == "delete_object"]
    print("FACT DO delete_object rows (id, uid, obj class, owners entry): {0}".format(DO), flush=True)
    sink_stub = [s for s in STUBS if s[1] == "dst" and s[3] and not any(int(d["wire_uid"]) in s[3] for d in DW)]
    gate("STUB no base sink end carries a wire that no plan delete_wire removes (no stub delete needed)", not sink_stub, sink_stub, fatal=False)
    TOP = {"schema": "stageplan/1", "context": RIN.get("context") or {"s1_key": "D1_s1_copy"}}
    MODEL = SPR.load_memory_model()
    XS = SPR.x10_start(md5(base_vi), MODEL)
    gate("XS START = stage_prerun.x10_start(md5 {0}) = {1}".format(md5(base_vi)[:8], XS), XS is not None)
    START = XS[0]
    CAND, CHOSEN = collections.OrderedDict(), None
    for i in range(len(groups)):
        nm, hi = "+".join(groups[:i + 1]), rng[i][1]
        try:
            ops = SX.compile_plan(dict(TOP, actions=FULL[:hi - LO + 1]), owners=OWNERS)
            m_, mp, cps = L.main_of(len(ops), [o["kind"] for o in ops], SX, SPR, MODEL, START, reads)
            CAND[nm] = {"hi": hi, "rows": hi - LO + 1, "ops": [(o["kind"], o.get("variant"), o["acts"]) for o in ops], "cps": cps, "main": m_,
                        "peak": mp["peak_mb"], "N": mp["N"], "R": mp["R"]}
            dwk = [k for k, o in enumerate(ops, 1) if o["kind"] == "delete_wire"]
            print("FACT C {0} A{1}..A{2}: {3} ops {4}; kinds {5}; checkpoints {6}; delete_wire ops {7}".format(nm, LO, hi, len(ops), CAND[nm]["ops"],
                  dict(collections.Counter(o["kind"] for o in ops)), cps, dwk), flush=True)
            print("FACT X10 {0}: rows {1} START {2} N {3} R {4} Executor peak {5} MAIN {6} (limit {7}, rows <= {8})".format(
                  nm, hi - LO + 1, START, mp["N"], mp["R"], mp["peak_mb"], m_, limit, max_rows), flush=True)
            gate("C {0} compiles; every delete_wire op {1} is a checkpoint".format(nm, dwk), set(dwk) <= set(cps), cps)
        except SX.ExecStop as e:
            CAND[nm] = {"hi": hi, "rows": hi - LO + 1, "error": str(e)[:500]}
            print("FACT C {0} compile refused: {1}".format(nm, str(e)[:500]), flush=True)
        c = CAND[nm]
        if "main" not in c or c["main"] > limit or c["rows"] > max_rows:
            print("FACT RULE prefix {0} fails (MAIN {1}, rows {2}, error {3}); longer prefixes not tried".format(nm, c.get("main"), c["rows"], c.get("error")), flush=True)
            break
        CHOSEN = nm
    gate("X10 first group {0} alone fits: MAIN {1} <= {2}, rows {3} <= {4}".format(groups[0], CAND[groups[0]].get("main"), limit, CAND[groups[0]]["rows"], max_rows),
         CHOSEN is not None, CAND[groups[0]])
    HI = CAND[CHOSEN]["hi"]
    print("FACT RULE plan = {0} (A{1}..A{2}, {3} rows, MAIN {4}) = longest whole-group prefix with MAIN <= {5} and rows <= {6}".format(
          CHOSEN, LO, HI, CAND[CHOSEN]["rows"], CAND[CHOSEN]["main"], limit, max_rows), flush=True)
    STEP = FULL[:HI - LO + 1]
    gate("SPLIT no group split: A{0}..A{1} ends at a census group end".format(LO, HI), HI in [r[1] for r in rng] and [a["id"] for a in STEP] == [r["id"] for r in RA[LO - 1:HI]])
    PRROOT = os.path.join(sim_root, stage, "_probe")
    QIN = os.path.join(PRROOT, "plan_{0}q_in.json".format(stage))
    os.makedirs(PRROOT, exist_ok=True)
    BASEREF = {"path": rel(graph), "md5": md5(graph)}
    json.dump(dict(TOP, stage=stage + "q", goal=probe_goal, base=BASEREF, actions=STEP), open(QIN, "w", encoding="utf-8"), indent=1)
    SQ = SS.simulate(QIN, graph, out_root=PRROOT, plan_out_dir=PRROOT, log=lambda *x: None, route_check=False)
    L.step_facts("PROBE", SQ, quiet=True)
    gate("PROBE A{0}..A{1} replay on the base graph: failed {2}".format(LO, HI, json.dumps(SQ.get("failed"), default=str)[:400]), SQ["failed"] is None and len(SQ["steps"]) == len(STEP) + 1)
    ok_pairs = dict(((int(r["node"]), r["term"]), "base-open") for r in BP.get("open_rows") or [])
    ties, untied, orows = L.tie_rows(SQ, STEP, ok_pairs, SS.V.key_parts, card)
    print("FACT TIE {0} end rows; open pairs {1}: {2}".format(len(SQ.get("end_cdiff_rows") or []), len(orows), [(o["node"], o["term"], o["why"][:60]) for o in orows])[:900], flush=True)
    gate("TIE every probe end row tied to a step action or a base-plan open row", not untied, untied[:10])
    json.dump(dict(TOP, stage=stage, goal=goal_fn(LO, HI, CAND, CHOSEN), base=BASEREF, open_rows=orows, actions=STEP), open(plan_in, "w", encoding="utf-8"), indent=1)
    ok_, why_ = protocol.validate_obj(J(plan_in))
    gate("S1 plan input validates ({0} actions, {1} open pairs)".format(len(STEP), len(orows)), ok_, why_)
    SB = SS.simulate(plan_in, graph, out_root=sim_root, plan_out_dir=plan_out_dir, log=lambda m: print(m, flush=True), route_check=True)
    HB = L.step_facts("REALSIM", SB)
    p = J(OUT) if os.path.isfile(OUT) else {}
    rc = (p.get("finalized") or {}).get("route_check") or {}
    prov = [s["n"] for s in SB["steps"] if s.get("provisional")]
    for x in rc.get("rows") or []:
        print("FACT ROUTE k={0} {1} {2}: route {3}{4}".format(x.get("k"), x.get("op"), x.get("ids"), x.get("route"), "  UNROUTABLE " + str(x["unroutable"])[:300] if x.get("unroutable") else ""), flush=True)
    nun = sum(1 for x in rc.get("rows") or [] if x.get("unroutable"))
    print("FACT REALSIM plan {0} md5 {1}: final {2}; failed {3}; steps {4}; provisional {5}; route check {6}; UNROUTABLE {7}".format(
          rel(OUT), md5(OUT) if p else None, SB["final"], json.dumps(SB.get("failed"), default=str)[:500], len(SB["steps"]) - 1, prov, rc.get("status"), nun), flush=True)
    gate("SB REALSIM FINAL on the base graph: failed None, {0}/{1} replayed, 0 PROVISIONAL, route PASS, 0 UNROUTABLE".format(len(SB["steps"]) - 1, len(STEP)),
         bool(SB["final"]) and p.get("final") is True and SB.get("failed") is None and not prov and len(SB["steps"]) - 1 == len(STEP) and rc.get("status") == "PASS" and nun == 0,
         {"final": SB["final"], "failed": SB.get("failed"), "route": rc.get("status"), "first_fail": rc.get("first_fail")})
    ops = SX.compile_plan(p, owners=OWNERS)
    MAIN, mp, cps = L.main_of(len(ops), [o["kind"] for o in ops], SX, SPR, MODEL, START, reads)
    gate("C-OUT compile of {0} == candidate {1} ops/checkpoints; MAIN {2}".format(os.path.basename(OUT), CHOSEN, MAIN),
         [(o["kind"], o.get("variant"), o["acts"]) for o in ops] == [tuple(x) for x in CAND[CHOSEN]["ops"]] and cps == CAND[CHOSEN]["cps"] and MAIN == CAND[CHOSEN]["main"], (cps, MAIN))
    gate("IDS plan action ids == A{0}..A{1} in order".format(LO, HI), [a["id"] for a in p["actions"]] == [r["id"] for r in RA[LO - 1:HI]], [a["id"] for a in p["actions"]])
    lint = SPR.control_path_lint(p)
    gate("X8 control_path_lint clean", not lint, lint, fatal=False)
    ok17, det17 = SPR.x17_gate([p])
    gate("X17 x17_gate over the plan", ok17, det17, fatal=False)
    F = {"card": card, "plan_in": {"path": rel(plan_in), "md5": md5(plan_in)}, "plan": {"path": rel(OUT), "md5": md5(OUT)}, "probe_in": {"path": rel(QIN), "md5": md5(QIN)},
         "sources": dict((k, dict((x, v[x]) for x in ("plan", "plan_md5", "made_used", "cmap", "work") if x in v)) for k, v in SRC.items()),
         "symbol_map": REAL, "frame_map": dict(("{0}|{1}".format(*k), v) for k, v in FMAP.items()), "ends": STUBS, "delete_objects": DO,
         "start": XS, "candidates": CAND, "chosen": CHOSEN, "actions": [a["id"] for a in STEP], "open_rows": orows,
         "realsim": {"final": SB["final"], "failed": SB.get("failed"), "provisional": prov, "route_check": rc},
         "compile": {"ops": [(o["kind"], o.get("variant"), o["acts"]) for o in ops], "checkpoints": cps}, "x10": {"main": MAIN, "exec_peak": mp["peak_mb"]},
         "realsim_states": HB}
    json.dump(F, open(session, "w", encoding="utf-8"), indent=1, default=str)
    gate.ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (QIN, plan_in, OUT, session) if os.path.isfile(x))
    return F


def _selftest():
    """Replay card 163-a1-2 into tools/bench/sim/ring_p5s02d/_replay163 and compare with plan_ring_p5s02c.json 930699ec."""
    gate = L.Gate()
    RR = os.path.join(SIM, "ring_p5s02d", "_replay163")
    os.makedirs(RR, exist_ok=True)
    ORIG, RIN0 = os.path.join(B, "plan_ring_p5s02c.json"), os.path.join(B, "plan_ring_p5s02r_in_pre164.json")
    PINS = {ORIG: "930699ec", RIN0: "d84634bd", os.path.join(B, "graph_ring_p5s02b_20261010_111905.json"): "431cfd83",
            os.path.join(CD, "D1_ring_p5s02b_20261010_105511.vi"): "f9ae7751", os.path.join(B, "plan_ring_p5s02b.json"): "f4520b10",
            os.path.join(B, "plan_ring_p5s02a.json"): "4284c22a", os.path.join(B, "graph_ring_p5s02a_20261010_032547.json"): "7ac24924"}
    gate("T0 replay input pins {0}".format(dict((os.path.basename(p), md5(p)[:8]) for p in PINS)), all(md5(p).startswith(w) for p, w in PINS.items()))

    def goal163(lo, hi, cand, chosen):                     # the goal text of prep_c163_a1_2_mk.py (its SUBS on prep_c163_a1_1_mk.py:131-133,150)
        why = ("MAIN(I+J) {0} <= {1}".format(cand["I+J"].get("main"), 675.0) if chosen == "I+J" else
               "MAIN(I+J) {0} > {1} (or compile refused: {2}); group I alone MAIN {3}".format(cand["I+J"].get("main"), 675.0, cand["I+J"].get("error"), cand["I"]["main"]))
        return ("RING P5-2 step 3 (card 163-a1-2, PD396(c), START = x10_start): A{0}..A{1} of plan_ring_p5s02r_in.json on the REAL f9ae7751 graph 431cfd83; "
                "{2}: {3}").format(lo, hi, chosen, why)[:400]
    IN = os.path.join(RR, "plan_ring_p5s02c_in.json")
    F = make_step_plan(gate, RIN0, ["I", "J"], os.path.join(B, "graph_ring_p5s02b_20261010_111905.json"), os.path.join(CD, "D1_ring_p5s02b_20261010_105511.vi"),
                       os.path.join(B, "plan_ring_p5s02b.json"),
                       [{"name": "p5s02a", "plan": os.path.join(B, "plan_ring_p5s02a.json"), "graph_after": os.path.join(B, "graph_ring_p5s02a_20261010_032547.json"),
                         "vi": os.path.join(CD, "D1_ring_p5s02a_20261010_023239.vi")},
                        {"name": "p5s02b", "plan": os.path.join(B, "plan_ring_p5s02b.json"), "graph_after": os.path.join(B, "graph_ring_p5s02b_20261010_111905.json"),
                         "vi": os.path.join(CD, "D1_ring_p5s02b_20261010_105511.vi")}],
                       "c163-a1-2", "ring_p5s02c", IN, os.path.join(RR, "replay163_session.json"), goal163,
                       "card 163-a1-2 PROBE (fact only): step-3 rows on f9ae7751", plan_out_dir=RR, sim_root=RR)
    gate("T1 chosen I with MAIN(I) 658.3, MAIN(I+J) 677.0 (as prep_c163_a1_2_mk.log:28-34)", F["chosen"] == "I" and F["candidates"]["I"]["main"] == 658.3
         and F["candidates"]["I+J"]["main"] == 677.0, dict((k, v.get("main")) for k, v in F["candidates"].items()))
    gate("T2 replay plan_in md5 {0} == 163-a1-2's eb48fabc".format(F["plan_in"]["md5"][:8]), F["plan_in"]["md5"].startswith("eb48fabc"))
    O, R = J(ORIG), J(os.path.join(RR, "plan_ring_p5s02c.json"))
    pre_r = rel(RR) + "/"
    pmap = lambda v: (v.replace(pre_r + "ring_p5s02c/", "tools/bench/sim/ring_p5s02c/").replace(pre_r, "tools/bench/")      # noqa: E731 - rel paths
                      .replace(os.path.join(RR, "ring_p5s02c"), os.path.join(SIM, "ring_p5s02c")) if isinstance(v, str) else v)        # abs (step `prev`)
    so = dict((x["n"], x) for x in O["finalized"]["step_files"])
    sr = dict((x["n"], x) for x in R["finalized"]["step_files"])
    smd5 = [n for n in so if so[n]["md5"] != sr[n]["md5"]]
    disk = [n for n in so if md5(os.path.join(ROOT, so[n]["path"])) != so[n]["md5"]]
    gate("T3a 930699ec's step files on disk still have their recorded md5 (changed: {0})".format(disk), not disk)
    sdiff = []
    for n in so:                                           # a step file records `prev` = {path, md5} of the previous step file -> paths differ
        lo_s, lr_s = leaves(J(so[n]["path"])), dict((k, pmap(v)) for k, v in leaves(J(sr[n]["path"])).items())
        sdiff += [(n, k) for k in set(lo_s) | set(lr_s) if lo_s.get(k) != lr_s.get(k) and not k.startswith("/prev/md5")]
    print("FACT REPLAY step files with another md5: {0}; content differences after the path map (other than prev/md5): {1}".format(smd5, sdiff[:20]), flush=True)
    gate("T3 every step file equal after the path map; only `prev` (path -> md5 chain) differs ({0} steps)".format(len(so)), set(so) == set(sr) and not sdiff, sdiff[:20])
    lo_, lr_ = leaves(O), dict((k, pmap(v)) for k, v in leaves(R).items())
    dk = sorted(k for k in set(lo_) | set(lr_) if lo_.get(k) != lr_.get(k))
    print("FACT REPLAY byte-equal {0}; JSON differences after the path map: {1}".format(md5(ORIG) == md5(os.path.join(RR, "plan_ring_p5s02c.json")),
          [(k, lo_.get(k), lr_.get(k)) for k in dk])[:1500], flush=True)
    okk = set(["/finalized/at", "/finalized/summary/md5", "/finalized/last_step/md5"] + ["/finalized/step_files/{0}/md5".format(i) for i in range(1, len(so))])
    gate("T4 replay == 930699ec except finalized.at, the summary md5 (it records the plan path) and the step-file md5 chain of T3", set(dk) <= okk, sorted(set(dk) - okk))
    return gate.result()


if __name__ == "__main__" and "--selftest" in sys.argv:
    sys.exit(_selftest())
