# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_160-b1-1.md
# ---
r"""prep_c160_b1_1_mk - card 160-b1-1 (OFFLINE, json only, no LabVIEW, never launched), PD390(c): plan_ring_p5s02b.json = P5-2 step 2
(action 1 delete_wire of the A13 remnant, then A24..A40) made FINAL on the REAL 94ffff94 graph (graph_ring_p5s02a_20261010_032547.json 7ac24924).
Flow of prep_c159_c1_1_mk.py, with the mapping CALLED from stagekit (made_symbols / used_symbols / map_symbols / map_frames / apply_map /
bound_from_cmap, self-test selftest_c160_stagemap.py) instead of prep_c159_c1_1_lib. Input = plan_ring_p5s02b_in.json 56bfddd3 (made by 159-c1-1,
report diag_c159_c1_1_facts.md); the rows are re-derived here and must equal it (MERGE `why` suffix aside). Gate / main_of / step_facts from
prep_c156_a1_1_lib.py; stagesim.simulate (termless-Wire delete branch, card 160-a1-1), stagexec.compile_plan / plan_base_owners, stage_prerun
load_creation_map / x10_start / control_path_lint / x17_gate. No tool edit, no new op. The old plan caef7e1c (final False) is kept as
plan_ring_p5s02b_c159.json first.
PREDICTION CONTRACT: M0 pins; E1 step-1 sim end; CM creation map of the run that saved 94ffff94; MAP/FRM all symbols / frame ends map;
  DW w10394 = P5-1's #3052 'File # Saved' wire, a Wire obj with no terminal row in 94ffff94; ROWS delete + stagekit-mapped A24..A40 == the input
  (18 actions) except the four MERGE `why` suffixes; MERGE A28 A32 A35 A39 why = ASSUMPTION / MERGE / w24285 w24264 w24312 w24300 / CEN2 ends;
  SB REALSIM final True, failed None, 18/18 steps, 0 PROVISIONAL, route check PASS; MERGE-END each stub terminal carries the expected uid at the
  sim end; C compile 8 ops {delete_wire 1, tunnel 5, case_frame_wire 2}, checkpoints [0,2,3,4,6,7,8]; X10 MAIN 654.6 <= 675 at START 603.4;
  X8 / X17 clean; U pins untouched.
    py tools/bgrun.py --material --max-min 15 --log tools/bench/prep_c160_b1_1_mk.log -- py -u tools/bench/prep_c160_b1_1_mk.py"""
import collections, copy, json, os, re, shutil, sys                                         # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import stagekit as K                                                                         # noqa: E402
import stagesim as SS, stagexec as SX, stage_prerun as SPR                                   # noqa: E401,E402
import prep_c156_a1_1_lib as L                                                               # noqa: E402
md5, rel, J = L.md5, L.rel, L.J
B = os.path.join(ROOT, "tools", "bench")
T = os.path.join(ROOT, "tools")
SIM = os.path.join(B, "sim")
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
GRAPH, GRAPH51 = os.path.join(B, "graph_ring_p5s02a_20261010_032547.json"), os.path.join(B, "graph_ring_p5s01_20261009_125622.json")
RIN, PA, PASESS = os.path.join(B, "plan_ring_p5s02r_in.json"), os.path.join(B, "plan_ring_p5s02a.json"), os.path.join(B, "prep_c156_a1_1_session.json")
IN, OUT, OLDP = os.path.join(B, "plan_ring_p5s02b_in.json"), os.path.join(B, "plan_ring_p5s02b.json"), os.path.join(B, "plan_ring_p5s02b_c159.json")
FACTS, VI2A = os.path.join(B, "prep_c160_b1_1_session.json"), os.path.join(CD, "D1_ring_p5s02a_20261010_023239.vi")
WANT = {os.path.join(B, "cards", "brief_160-b1-1.md"): "41de595c", GRAPH: "7ac24924", IN: "56bfddd3", RIN: "d84634bd", PA: "4284c22a", PASESS: "e3117bf4",
        os.path.join(B, "memory_model.json"): "5b87de43", os.path.join(T, "stage_prerun.py"): "7605116f", os.path.join(T, "stagekit.py"): "0b5bb678",  # re-pinned 160-e5-1 from 1441bb4c
        os.path.join(T, "stagexec.py"): "c4a6e0b6", os.path.join(T, "stagesim.py"): "a3261b56", os.path.join(T, "vigraph.py"): "a7eb58c7",
        os.path.join(T, "addrcheck.py"): "207beb0d", os.path.join(B, "prep_c159_c1_1_lib.py"): "218af76c", GRAPH51: "6716c499", VI2A: "94ffff94",
        os.path.join(CD, "D1_ring_p4s09_20261009_060515.vi"): "eb1d0f31", os.path.join(CD, "D1_ring_p5s01a_20261009_101219.vi"): "2482fe7b",
        os.path.join(CD, "D1_ring_p5s01_20261009_124542.vi"): "7f2582ae"}
LIMIT, READS, MERGE_POS, MERGE_UID = 675.0, 2, (28, 32, 35, 39), {28: 24285, 32: 24264, 35: 24312, 39: 24300}
gate = L.Gate()
ARTS = gate.ARTS
M0 = dict((p, md5(p)) for p in WANT)
gate("M0 input md5 == card pins / VI pins", all(M0[p].startswith(w) for p, w in WANT.items()), dict((os.path.basename(p), M0[p][:8]) for p in WANT))
if os.path.isfile(OUT) and not os.path.isfile(OLDP):
    shutil.copyfile(OUT, OLDP)                                  # keep 159-c1-1's plan (final False) before the rebuild
gate("K old plan kept as {0} (md5 {1})".format(rel(OLDP), md5(OLDP) if os.path.isfile(OLDP) else None),
     os.path.isfile(OLDP) and md5(OLDP).startswith("caef7e1c"))
if os.path.isfile(OUT):
    os.remove(OUT)                                              # the plan below is written by stagesim.simulate only
# ---- mapping, by the stagekit calls
RA, PAJ, SESS, INJ = J(RIN)["actions"], J(PA), J(PASESS), J(IN)
K1, NA = len(PAJ["actions"]), len(INJ["actions"])
last = max((PAJ.get("finalized") or {}).get("step_files") or [], key=lambda x: int(x["n"]))
gate("E1 p5s02a finalized last step file md5 == recorded {0}".format(last["md5"][:8]), md5(os.path.join(ROOT, last["path"])) == last["md5"])
SYM, GR = J(last["path"])["state"]["sym"], J(GRAPH)
cm, cwhy, cmeta = SPR.load_creation_map({"plan": rel(PA), "md5": md5(PA)}, GR)
gate("CM creation map of the p5s02a run that saved 023239.vi: {0} ({1})".format(cmeta.get("path"), cwhy),
     cm is not None and os.path.normcase((cmeta.get("head") or {}).get("work") or "") == os.path.normcase(VI2A), cmeta.get("head"))
HEAD, BOUND = K.bound_from_cmap(os.path.join(ROOT, cmeta["path"]))
RAW80 = copy.deepcopy(RA[K1:])
used = K.used_symbols(RAW80, K.made_symbols(RAW80))
REAL, bad, lines = K.map_symbols(used, SYM, BOUND, GR)
for ln in lines:
    print("FACT " + ln, flush=True)
gate("MAP every step-1 symbol A24..A80 uses ({0}) -> a real uid in 94ffff94".format(used), not bad, bad)
OWNERS = SX.plan_base_owners({"base": {"path": rel(GRAPH), "md5": md5(GRAPH)}})
FMAP, fbad, flines = K.map_frames(RAW80, RA, SYM, BOUND, OWNERS)
for ln in flines:
    print("FACT " + ln, flush=True)
gate("FRM frame ends ({0}) -> '#<real frame uid>': {1}".format(len(FMAP), sorted(set((v["frame_name"], v["addr"]) for v in FMAP.values()))), not fbad, fbad)
# ---- the A13 remnant (PD388(a)): read from the P5-1 graph, never typed
r51 = [r for r in J(GRAPH51)["terminals"] if int(r["owner_uid"]) == 3052 and r["term_name"] == "File # Saved" and r["is_source"]]
W_OLD = int(r51[0]["wire_uid"]) if len(r51) == 1 else None
wobj = [o for o in GR.get("objs") or [] if int(o["uid"]) == (W_OLD or 0)]
wrows = [r for r in GR["terminals"] if int(r.get("wire_uid") or 0) == (W_OLD or 0)]
gate("DW remnant w{0} = P5-1's #3052 'File # Saved' wire: Wire obj in 94ffff94 ({1}), terminal rows {2}; input action 1 = delete_wire w{3}".format(
     W_OLD, [o["class"] for o in wobj], len(wrows), INJ["actions"][0].get("wire_uid")),
     W_OLD is not None and len(wobj) == 1 and wobj[0]["class"] == "Wire" and not wrows and INJ["actions"][0] == dict(INJ["actions"][0], op="delete_wire", wire_uid=W_OLD))
# ---- the rows: delete + stagekit-mapped A24..A40 == the input; only the MERGE `why` suffix differs
MAPPED = [INJ["actions"][0]] + K.apply_map(RAW80, REAL, FMAP)[:NA - 1]
strip = lambda a: dict(a, why=re.sub(r" \| ASSUMPTION \(PD388\(c\).*$", "", a.get("why") or ""))    # noqa: E731
diff = [a["id"] for a, b in zip(MAPPED, INJ["actions"]) if a != strip(b)]
gate("ROWS delete + stagekit.apply_map(A24..A{0}) == plan_ring_p5s02b_in.json actions ({1}), MERGE why suffix aside".format(NA - 1 + K1, NA),
     len(MAPPED) == NA == 18 and not diff, diff)
MERGE = []
for p_ in MERGE_POS:
    a = INJ["actions"][p_ - K1]
    w = a.get("why") or ""
    ok = all(s in w for s in ("ASSUMPTION", "MERGE", "w{0}".format(MERGE_UID[p_]), "CEN2 judges by wire ENDS"))
    side = "src" if isinstance(a["src"], dict) and isinstance(a["src"].get("uid"), int) else "dst"
    MERGE.append({"pos": p_, "id": a["id"], "stub_term": int(a[side]["term_uid"]), "expect": MERGE_UID[p_], "why_ok": ok, "why": w})
    print("FACT MERGE A{0} {1}: why = {2!r}".format(p_, a["id"], w), flush=True)
gate("MERGE A28 A32 A35 A39 carry ASSUMPTION MERGE text with w24285/w24264/w24312/w24300 and CEN2-by-ends", all(m_["why_ok"] for m_ in MERGE),
     [(m_["pos"], m_["why_ok"]) for m_ in MERGE])
# ---- REALSIM of the plan on the real graph (route check on): writes plan_ring_p5s02b.json
SB = SS.simulate(IN, GRAPH, out_root=SIM, plan_out_dir=B, log=lambda m: print(m, flush=True), route_check=True)
HB = L.step_facts("REALSIM", SB)
p = J(OUT) if os.path.isfile(OUT) else {}
fz = p.get("finalized") or {}
prov = [s["n"] for s in SB["steps"] if s.get("provisional")]
print("FACT REALSIM plan {0}: final {1}; failed {2}; steps {3}; provisional {4}; route check {5}".format(
      rel(OUT), SB["final"], json.dumps(SB.get("failed"), default=str)[:500], len(SB["steps"]) - 1, prov, (fz.get("route_check") or {}).get("status")), flush=True)
gate("SB REALSIM plan FINAL on 94ffff94: failed None, {0}/{1} actions replayed, 0 PROVISIONAL, route check PASS".format(len(SB["steps"]) - 1, NA),
     bool(SB["final"]) and p.get("final") is True and SB.get("failed") is None and not prov and len(SB["steps"]) - 1 == NA
     and (fz.get("route_check") or {}).get("status") == "PASS", {"final": SB["final"], "failed": SB.get("failed"), "route": fz.get("route_check")})
END = J(SB["steps"][-1]["file"]["path"])["state"] if SB.get("failed") is None else {}
for m_ in MERGE:
    m_["end_wires"] = sorted(set(int(r.get("wire_uid") or 0) for r in END.get("terminals") or [] if int(r["term_uid"]) == m_["stub_term"]))
    print("FACT MERGE-END A{0} {1}: wires on t{2} at the REALSIM end {3} (expected w{4})".format(m_["pos"], m_["id"], m_["stub_term"], m_["end_wires"], m_["expect"]), flush=True)
gate("MERGE-END each stub terminal carries exactly the expected uid at the REALSIM end", all(m_["end_wires"] == [m_["expect"]] for m_ in MERGE),
     [(m_["pos"], m_["end_wires"]) for m_ in MERGE], fatal=False)
# ---- compile on the real owners + planned MAIN at START_ASSUMED
ops = SX.compile_plan(p, owners=OWNERS) if p else []
KC = dict(collections.Counter(o["kind"] for o in ops))
MODEL, START = SPR.load_memory_model(), SESS["start_mb"]
MAIN, mp, cps = L.main_of(len(ops), [o["kind"] for o in ops], SX, SPR, MODEL, START, READS) if ops else (None, {}, [])
print("FACT C plan ops {0}: {1}; kinds {2}; checkpoints {3}".format(len(ops), [(o["kind"], o["acts"]) for o in ops], KC, cps), flush=True)
print("FACT X10 START_ASSUMED {0} (x10_start(94ffff94) {1}); Executor peak {2}; MAIN {3}; limit {4}".format(
      START, SPR.x10_start(md5(VI2A), MODEL), mp.get("peak_mb"), MAIN, LIMIT), flush=True)
gate("C compile 8 ops {delete_wire 1, tunnel 5, case_frame_wire 2}, checkpoints [0,2,3,4,6,7,8]",
     len(ops) == 8 and KC == {"delete_wire": 1, "tunnel": 5, "case_frame_wire": 2} and cps == [0, 2, 3, 4, 6, 7, 8], (KC, cps))
gate("X10 START 603.4, MAIN {0} <= {1}".format(MAIN, LIMIT), START == 603.4 and MAIN is not None and MAIN <= LIMIT, mp)
lint = SPR.control_path_lint(p)
gate("X8 control_path_lint clean", not lint, lint, fatal=False)
ok17, det17 = SPR.x17_gate([p])
gate("X17 x17_gate over the plan", ok17, det17, fatal=False)
json.dump({"card": "160-b1-1", "plan_in": {"path": rel(IN), "md5": md5(IN)}, "plan": {"path": rel(OUT), "md5": md5(OUT) if os.path.isfile(OUT) else None},
           "old_plan": {"path": rel(OLDP), "md5": md5(OLDP)}, "creation_map": cmeta.get("path"), "symbol_map": REAL, "remnant_wire": W_OLD,
           "frame_map": dict(("{0}|{1}".format(*k), v) for k, v in FMAP.items()), "merge": MERGE, "start_mb": START,
           "realsim": {"final": SB["final"], "failed": SB.get("failed"), "provisional": prov, "route_check": fz.get("route_check")},
           "compile": {"ops": [(o["kind"], o["acts"]) for o in ops], "checkpoints": cps}, "x10": {"main": MAIN, "exec_peak": mp.get("peak_mb")},
           "realsim_states": HB}, open(FACTS, "w", encoding="utf-8"), indent=1, default=str)
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (OLDP, OUT, FACTS) if os.path.isfile(x))
gate("U inputs / VI / tool pins untouched", all(md5(q) == M0[q] for q in WANT))
sys.exit(gate.result())
