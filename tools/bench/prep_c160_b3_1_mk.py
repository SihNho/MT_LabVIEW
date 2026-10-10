# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_160-b3-1.md
# ---
r"""prep_c160_b3_1_mk - card 160-b3-1 (OFFLINE, json only, no LabVIEW, never launched), PD391(a)(d)(f): plan_ring_p5s02b.json = P5-2 step 2
(delete_wire w10394, A24..A40, plus the two PD391(a) sink-only stub deletes w24264 / w24300) made FINAL on the REAL 94ffff94 graph
(graph_ring_p5s02a_20261010_032547.json 7ac24924). Flow of prep_c160_b1_1_mk.py (4fe22a40, copied and edited, not imported - it runs at top
level): mapping CALLED from stagekit (made_symbols / used_symbols / map_symbols / map_frames / apply_map / bound_from_cmap), Gate / main_of /
step_facts from prep_c156_a1_1_lib.py, stagesim.simulate (95a162ba: sourceless-Wire delete branch, card 160-a2-1) + its route check,
stagexec.compile_plan / plan_base_owners (ddf23a31: a BASE register inner face compiles to connect_term_uid register_end_case_border),
stage_prerun load_creation_map / x10_start / control_path_lint / x17_gate. No tool edit, no new op. Existing tools checked: the insertion of the
two delete rows is the block of selftest_c160_regface.py:70-79 (no shared function exists; reported OPEN), here driven by plan positions.
Input plan_ring_p5s02b_in.json 56bfddd3 stays byte-unchanged; the simulate input is plan_ring_p5s02b_in2.json written here; the b1 output
09ebc7a6 (final False) is kept as plan_ring_p5s02b_b1.json first; plan_ring_p5s02b_c159.json caef7e1c only pinned.
PREDICTION CONTRACT: M0 pins; B1 b1 plan kept (09ebc7a6); E1 step-1 sim end; CM creation map; MAP/FRM all symbols / frame ends map; DW w10394
  termless Wire, input action 1; ROWS delete + stagekit-mapped A24..A40 == the input (18), MERGE `why` suffix aside; MERGE A28/A35 why keep
  ASSUMPTION MERGE w24285/w24312 CEN2-by-ends; STUB the sinks of A32/A39 (t24139 / t24235) carry exactly one base wire each, read from the graph
  rows = w24264 / w24300, sourceless (stagesim.sourceless_wire True); IN2 20 actions = input + dw_go before t_go + dw_ho before t_ho, the A32/A39
  why replaced, nothing else differs; SB REALSIM final True, failed None, 20/20 replayed, 0 PROVISIONAL, route check PASS, 0 UNROUTABLE, dw_go /
  dw_ho route delete_wire, t_go / t_ho groups route connect_term_uid; MERGE-END t24190 -> [24285], t24288 -> [24312]; STUB-END t24139 / t24235
  carry one wire != the stub, with a source row, the stub Wire objects gone; C compile 10 ops {delete_wire 3, tunnel 3, connect_term_uid 2,
  case_frame_wire 2} (b1's 8 + the 2 deletes; t_go / t_ho tunnel -> connect_term_uid), checkpoints [0,2,3,5,7,9,10]; X10 MAIN <= 675 at
  START 603.4; X8 / X17 clean; U pins untouched.
    py tools/bgrun.py --material --max-min 15 --log tools/bench/prep_c160_b3_1_mk.log -- py -u tools/bench/prep_c160_b3_1_mk.py"""
import collections, copy, json, os, re, shutil, sys                                         # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import stagekit as K                                                                         # noqa: E402
import stagesim as SS, stagexec as SX, stage_prerun as SPR                                   # noqa: E401,E402
import stage_shared as SH                                                                    # noqa: E402  insert_stub_deletes (card 162-a2-3)
import prep_c156_a1_1_lib as L                                                               # noqa: E402
md5, rel, J = L.md5, L.rel, L.J
B = os.path.join(ROOT, "tools", "bench")
T = os.path.join(ROOT, "tools")
SIM = os.path.join(B, "sim")
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
GRAPH, GRAPH51 = os.path.join(B, "graph_ring_p5s02a_20261010_032547.json"), os.path.join(B, "graph_ring_p5s01_20261009_125622.json")
RIN, PA, PASESS = os.path.join(B, "plan_ring_p5s02r_in.json"), os.path.join(B, "plan_ring_p5s02a.json"), os.path.join(B, "prep_c156_a1_1_session.json")
IN, OUT, OLDP = os.path.join(B, "plan_ring_p5s02b_in.json"), os.path.join(B, "plan_ring_p5s02b.json"), os.path.join(B, "plan_ring_p5s02b_c159.json")
IN2, B1P = os.path.join(B, "plan_ring_p5s02b_in2.json"), os.path.join(B, "plan_ring_p5s02b_b1.json")
FACTS, VI2A = os.path.join(B, "prep_c160_b3_1_session.json"), os.path.join(CD, "D1_ring_p5s02a_20261010_023239.vi")
WANT = {os.path.join(B, "cards", "brief_160-b3-1.md"): "d80ad29f", GRAPH: "7ac24924", IN: "56bfddd3", RIN: "d84634bd", PA: "4284c22a", PASESS: "e3117bf4",
        OLDP: "caef7e1c", os.path.join(B, "memory_model.json"): "5b87de43", os.path.join(T, "stage_prerun.py"): "7605116f",
        os.path.join(T, "stagekit.py"): "0b5bb678", os.path.join(T, "stagexec.py"): "a4df7e15", os.path.join(T, "stagesim.py"): "95a162ba",  # re-pinned 160-e5-1 from 1441bb4c; stagexec 161-b1-1 from ddf23a31
        os.path.join(T, "vigraph.py"): "a7eb58c7", os.path.join(T, "addrcheck.py"): "207beb0d", os.path.join(B, "prep_c156_a1_1_lib.py"): "fc6ce5f6",
        os.path.join(B, "prep_c160_b1_1_mk.py"): "4fe22a40", GRAPH51: "6716c499", VI2A: "94ffff94",
        os.path.join(CD, "D1_ring_p4s09_20261009_060515.vi"): "eb1d0f31", os.path.join(CD, "D1_ring_p5s01a_20261009_101219.vi"): "2482fe7b",
        os.path.join(CD, "D1_ring_p5s01_20261009_124542.vi"): "7f2582ae"}
LIMIT, READS, START_WANT = 675.0, 2, 603.4
MERGE_POS, MERGE_UID = (28, 35), {28: 24285, 35: 24312}          # PD391(d): MERGE stays only on the LSR faces
DEL_POS, STUB_UID = (32, 39), {32: 24264, 39: 24300}              # PD391(a): expectations only; the plan takes the uids read from the graph
WHY_ASSUME = re.compile(r" \| ASSUMPTION \(PD388\(c\).*$")
WHY_FRESH = "stub deleted first (PD391); fresh connect to the register inner face; uid NOT predicted; CEN2 judges by ends"
WHY_DEL = "PD391(a): sink-only stub on the base register inner face, deleted before the group's connect"
gate = L.Gate()
ARTS = gate.ARTS
M0 = dict((p, md5(p)) for p in WANT)
gate("M0 input md5 == card pins / VI pins", all(M0[p].startswith(w) for p, w in WANT.items()), dict((os.path.basename(p), M0[p][:8]) for p in WANT))
if os.path.isfile(OUT) and not os.path.isfile(B1P):
    shutil.copyfile(OUT, B1P)                                   # keep 160-b1-1's plan (final False) before the rebuild
gate("B1 b1 plan kept as {0} (md5 {1})".format(rel(B1P), md5(B1P) if os.path.isfile(B1P) else None),
     os.path.isfile(B1P) and md5(B1P).startswith("09ebc7a6"))
if os.path.isfile(OUT):
    os.remove(OUT)                                              # the plan below is written by stagesim.simulate only
# ---- mapping, by the stagekit calls (as b1)
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
strip = lambda a: dict(a, why=WHY_ASSUME.sub("", a.get("why") or ""))                      # noqa: E731
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
gate("MERGE A28 A35 (LSR faces, PD391(d)) carry ASSUMPTION MERGE text with w24285/w24312 and CEN2-by-ends", all(m_["why_ok"] for m_ in MERGE),
     [(m_["pos"], m_["why_ok"]) for m_ in MERGE])
# ---- PD391(a): the sink-only stubs of A32/A39, READ from the graph rows of their sink terminals
BASE = SS.base_state(GR)
STUB = []
for p_ in DEL_POS:
    a = INJ["actions"][p_ - K1]
    sink = a["dst"]
    ws = sorted(set(int(r.get("wire_uid") or 0) for r in GR["terminals"] if int(r["term_uid"]) == int(sink["term_uid"])))
    tsym = a["src"].split(":", 1)[1].split(".")[0] if isinstance(a["src"], str) else None      # 'new:TG2.outer' -> 'TG2'
    tun = next((x for x in INJ["actions"] if x.get("op") == "tunnel" and x.get("as") == tsym), None)
    w0 = ws[0] if len(ws) == 1 else None
    STUB.append({"pos": p_, "id": a["id"], "sink_term": int(sink["term_uid"]), "wire": w0, "expect": STUB_UID[p_], "tunnel": tun and tun["id"],
                 "sourceless": bool(w0 and SS.sourceless_wire(BASE, w0))})
    print("FACT STUB A{0} {1}: sink t{2} graph wires {3}; group tunnel {4}; sourceless {5}".format(p_, a["id"], sink["term_uid"], ws,
          STUB[-1]["tunnel"], STUB[-1]["sourceless"]), flush=True)
gate("STUB A32/A39 sinks carry one base wire each, read from the graph = w24264 / w24300, sourceless; group tunnels t_go / t_ho",
     all(s["wire"] == s["expect"] and s["sourceless"] and s["tunnel"] for s in STUB), [(s["pos"], s["wire"], s["sourceless"], s["tunnel"]) for s in STUB])
# ---- plan_ring_p5s02b_in2.json = input + the two delete rows (before each group's tunnel) + the A32/A39 why replaced
P2 = copy.deepcopy(INJ)
P2["goal"] = INJ["goal"] + " | card 160-b3-1 (PD391(a)(d)(f)): + delete_wire of the sink-only stubs on the RSR inner faces before groups t_go / t_ho; 20 actions"
DEL_BEFORE = dict((s["tunnel"], s) for s in STUB)
FRESH_IDS = set(s["id"] for s in STUB)
FRESHED = [dict(a, why=WHY_ASSUME.sub("", a.get("why") or "") + " | " + WHY_FRESH) if a.get("id") in FRESH_IDS else a for a in P2["actions"]]
acts = SH.insert_stub_deletes(FRESHED, dict((t, s["wire"]) for t, s in DEL_BEFORE.items()), WHY_DEL)   # card 162-a2-3: tools/stage_shared.py
P2["actions"] = acts
with open(IN2, "w", encoding="utf-8") as f:
    json.dump(P2, f, indent=1)
I2 = J(IN2)["actions"]
back = [a for a in I2 if a.get("id") not in ("dw_go", "dw_ho")]
nowhy = lambda a: dict(a, why=None) if a.get("id") in FRESH_IDS else a                       # noqa: E731 - only A32/A39's why may change
d2 = [a.get("id") for a, b in zip(back, INJ["actions"]) if nowhy(a) != nowhy(b)]
pos_ok = all(I2[i + 1].get("id") == t for i, a in enumerate(I2) for d, t in (("dw_go", "t_go"), ("dw_ho", "t_ho")) if a.get("id") == d)
why_ok = all(a["why"].endswith(WHY_FRESH) and "ASSUMPTION" not in a["why"] for a in I2 if a.get("id") in FRESH_IDS)
print("FACT IN2 {0} md5 {1}: {2} actions {3}".format(rel(IN2), md5(IN2), len(I2), [a.get("id") for a in I2]), flush=True)
for a in I2:
    if a.get("id") in ("dw_go", "dw_ho") or a.get("id") in FRESH_IDS:
        print("FACT IN2 {0}: {1}".format(a["id"], json.dumps(a)[:400]), flush=True)
gate("IN2 20 actions = input + dw_go before t_go + dw_ho before t_ho (wire uids from the graph), A32/A39 why replaced, nothing else differs",
     len(I2) == 20 and len(back) == NA and not d2 and pos_ok and why_ok and I2[0] == INJ["actions"][0]
     and sorted(a["wire_uid"] for a in I2 if a.get("id") in ("dw_go", "dw_ho")) == sorted(s["wire"] for s in STUB), {"diff": d2, "pos": pos_ok, "why": why_ok})
# ---- REALSIM of in2 on the real graph (route check on): writes plan_ring_p5s02b.json
SB = SS.simulate(IN2, GRAPH, out_root=SIM, plan_out_dir=B, log=lambda m: print(m, flush=True), route_check=True)
HB = L.step_facts("REALSIM", SB)
p = J(OUT) if os.path.isfile(OUT) else {}
fz = p.get("finalized") or {}
prov = [s["n"] for s in SB["steps"] if s.get("provisional")]
rc = fz.get("route_check") or {}
rrows = rc.get("rows") or []
for x in rrows:
    print("FACT ROUTE k={0} {1} {2}: route {3}{4}".format(x.get("k"), x.get("op"), x.get("ids"), x.get("route"),
                                                       "  UNROUTABLE " + str(x["unroutable"])[:300] if x.get("unroutable") else ""), flush=True)
nun = sum(1 for x in rrows if x.get("unroutable"))
print("FACT REALSIM plan {0}: final {1}; failed {2}; steps {3}; provisional {4}; route check {5}; UNROUTABLE {6}".format(
      rel(OUT), SB["final"], json.dumps(SB.get("failed"), default=str)[:500], len(SB["steps"]) - 1, prov, rc.get("status"), nun), flush=True)
rt = dict((k, next((x.get("route") for x in rrows if k in (x.get("ids") or ())), None)) for k in ("dw_go", "dw_ho", "t_go", "t_ho", "t_gi", "t_hi"))
gate("SB REALSIM plan FINAL on 94ffff94: failed None, {0}/20 actions replayed, 0 PROVISIONAL, route check PASS, 0 UNROUTABLE; routes {1}".format(
     len(SB["steps"]) - 1, rt), bool(SB["final"]) and p.get("final") is True and SB.get("failed") is None and not prov and len(SB["steps"]) - 1 == 20
     and rc.get("status") == "PASS" and nun == 0 and rt["dw_go"] == rt["dw_ho"] == "delete_wire" and rt["t_go"] == rt["t_ho"] == "connect_term_uid",
     {"final": SB["final"], "failed": SB.get("failed"), "route": rc.get("status"), "first_fail": rc.get("first_fail")})
END = J(SB["steps"][-1]["file"]["path"])["state"] if SB.get("failed") is None else {}
ET, EO = END.get("terminals") or [], set(int(o["uid"]) for o in END.get("objs") or [])
for m_ in MERGE:
    m_["end_wires"] = sorted(set(int(r.get("wire_uid") or 0) for r in ET if int(r["term_uid"]) == m_["stub_term"]))
    print("FACT MERGE-END A{0} {1}: wires on t{2} at the REALSIM end {3} (expected w{4})".format(m_["pos"], m_["id"], m_["stub_term"], m_["end_wires"], m_["expect"]), flush=True)
gate("MERGE-END A28/A35 stub terminal carries exactly the expected uid at the REALSIM end", all(m_["end_wires"] == [m_["expect"]] for m_ in MERGE),
     [(m_["pos"], m_["end_wires"]) for m_ in MERGE], fatal=False)
for s in STUB:
    s["end_wires"] = sorted(set(int(r.get("wire_uid") or 0) for r in ET if int(r["term_uid"]) == s["sink_term"]))
    s["end_src"] = [int(r["term_uid"]) for r in ET if s["end_wires"] and int(r.get("wire_uid") or 0) == s["end_wires"][0] and r.get("is_source")]
    s["stub_obj_gone"] = s["wire"] not in EO
    print("FACT STUB-END A{0} {1}: wires on t{2} {3} (stub w{4}, uid not predicted); source rows {5}; stub Wire obj gone {6}".format(
          s["pos"], s["id"], s["sink_term"], s["end_wires"], s["wire"], s["end_src"], s["stub_obj_gone"]), flush=True)
gate("STUB-END t24139 / t24235 carry one wire != the stub, with a source row; stub Wire objects gone",
     all(len(s["end_wires"]) == 1 and s["end_wires"][0] not in (0, s["wire"]) and len(s["end_src"]) == 1 and s["stub_obj_gone"] for s in STUB),
     [(s["pos"], s["end_wires"], s["end_src"], s["stub_obj_gone"]) for s in STUB], fatal=False)
# ---- compile on the real owners + planned MAIN at START_ASSUMED
ops = SX.compile_plan(p, owners=OWNERS) if p else []
KC = dict(collections.Counter(o["kind"] for o in ops))
MODEL, START = SPR.load_memory_model(), SESS["start_mb"]
MAIN, mp, cps = L.main_of(len(ops), [o["kind"] for o in ops], SX, SPR, MODEL, START, READS) if ops else (None, {}, [])
print("FACT C plan ops {0}: {1}; kinds {2}; checkpoints {3}".format(len(ops), [(o["kind"], o.get("variant"), o["acts"]) for o in ops], KC, cps), flush=True)
print("FACT X10 START_ASSUMED {0} (x10_start(94ffff94) {1}); Executor peak {2}; MAIN {3}; limit {4}".format(
      START, SPR.x10_start(md5(VI2A), MODEL), mp.get("peak_mb"), MAIN, LIMIT), flush=True)
gate("C compile 10 ops {delete_wire 3, tunnel 3, connect_term_uid 2, case_frame_wire 2} (b1 8 + 2 deletes; t_go/t_ho -> connect_term_uid), checkpoints [0,2,3,5,7,9,10]",
     len(ops) == 10 and KC == {"delete_wire": 3, "tunnel": 3, "connect_term_uid": 2, "case_frame_wire": 2} and cps == [0, 2, 3, 5, 7, 9, 10], (KC, cps))
gate("X10 START {0}, MAIN {1} <= {2}".format(START, MAIN, LIMIT), START == START_WANT and MAIN is not None and MAIN <= LIMIT, mp)
lint = SPR.control_path_lint(p)
gate("X8 control_path_lint clean", not lint, lint, fatal=False)
ok17, det17 = SPR.x17_gate([p])
gate("X17 x17_gate over the plan", ok17, det17, fatal=False)
json.dump({"card": "160-b3-1", "plan_in": {"path": rel(IN), "md5": md5(IN)}, "plan_in2": {"path": rel(IN2), "md5": md5(IN2)},
           "plan": {"path": rel(OUT), "md5": md5(OUT) if os.path.isfile(OUT) else None}, "b1_plan": {"path": rel(B1P), "md5": md5(B1P)},
           "old_plan": {"path": rel(OLDP), "md5": md5(OLDP)}, "creation_map": cmeta.get("path"), "symbol_map": REAL, "remnant_wire": W_OLD,
           "frame_map": dict(("{0}|{1}".format(*k), v) for k, v in FMAP.items()), "merge": MERGE, "stubs": STUB, "start_mb": START,
           "actions": [a.get("id") for a in I2],
           "realsim": {"final": SB["final"], "failed": SB.get("failed"), "provisional": prov, "route_check": rc},
           "compile": {"ops": [(o["kind"], o.get("variant"), o["acts"]) for o in ops], "checkpoints": cps}, "x10": {"main": MAIN, "exec_peak": mp.get("peak_mb")},
           "realsim_states": HB}, open(FACTS, "w", encoding="utf-8"), indent=1, default=str)
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (B1P, IN2, OUT, FACTS) if os.path.isfile(x))
gate("U inputs / VI / tool pins untouched", all(md5(q) == M0[q] for q in WANT))
sys.exit(gate.result())
