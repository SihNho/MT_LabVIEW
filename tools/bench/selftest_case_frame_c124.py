"""Self-test of card 124-2 (PD249(d)): the `frame` field on case-tunnel wire ends (stageplan/1), its stagesim model and the
stagexec route `case_frame_wire`. No LabVIEW, no COM: stagesim/stagexec on the synthetic graph; the LabVIEW backend on fakes.

WHAT EXISTED FIRST: the case data tunnel of card 120-3 R2 (stagesim._case_tunnel: one inner face per frame, but only the body
frame's face addressable, stagesim.py resolve_addr `case_tunnel_frame`) and case_wired of card 123-7 (selftest_case_wired_c123.py,
whose fakes this file copies). Measured facts used: diag_c123_casetun.log:38,45 (a cross-border connect into a case_wired case =
SelectorTunnel +1, OuterTerminal +1, InnerTerminal +2). The LabVIEW verb gscript.case_frame_wire is card 124-1's (contract
tools/bench/cards/brief_124-2.md); where this test needs it present it stubs ROUTE_VERBS, and D03 states what the real table says.
PREDICTION (20 gates): S01-S02 schema; M01-M06 the model; C01-C03 compile; D01-D03 dry runs; L01-L03 the LabVIEW backend on
fakes; U01 census UNMEASURED -> census_predict UNPREDICTED; V01 plan_ring_p3a_in_v2.json simulates every action on the real P2b
graph with action 20 a True-frame wire; R01 the card's other routes untouched.
CARD 124-6 (PD250(c)), +9 gates (29; 30 once plan_ring_p3a_in_v3.json exists): C04-C06 compile of the register-inner-face
group (connect_term_uid) and the frame-wire variant (branch / new_wire); D04 dry run with the REAL verb table; M07 the R4 model;
L04-L05 the LabVIEW backend on fakes; P01 stage_prerun.SP_WIRING == stagexec.REC_WIRING; V02 v3 routes with no UNROUTABLE row.
U01/D01/L01 now expect the MEASURED census (census_samples.json, card 124-5) instead of UNMEASURED.
Usage: py tools/bench/selftest_case_frame_c124.py"""
import copy
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol   # noqa: E402
import stagesim as SS   # noqa: E402
import stagexec as SX   # noqa: E402
import census_predict as CP   # noqa: E402

gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, str(detail)[:300]), flush=True)


def raises(fn, exc):
    try:
        fn()
        return "no error"
    except exc as e:
        return "refused: " + str(e)


base = SS._synthetic()
for tu, nm, src in ((1025, "flag", True), (1026, "cnt", True), (1027, "cnt in", False)):
    base["terminals"].append({"term_uid": tu, "term_name": nm, "is_source": src, "wire_uid": 0, "owner_uid": 2,
                              "owner_class": "SubVI", "frame_diagram": 20, "term_class": "Terminal"})
INC = [{"name": "x+1", "is_source": True}, {"name": "x", "is_source": False}]
HEAD = [
    {"op": "create", "id": "cs", "class": "CaseStructure", "diagram": 20, "as": "C1", "selector_as": "S1", "src": "2.flag",
     "frames": ["False", "True"], "pos": [40, 40]},
    {"op": "create", "id": "inc", "class": "Function", "diagram": "new:C1.f0", "as": "INC1", "prim": "Increment",
     "terminals": INC, "pos": [10, 10]},
    {"op": "tunnel", "id": "ti", "loop": "new:C1", "body": "new:C1.f0", "parent": 20, "dir": "in", "as": "TI1"},
    {"op": "wire", "id": "w_in", "src": "2.cnt", "dst": "new:TI1.outer"},
    {"op": "wire", "id": "w_inc", "src": "new:TI1.inner", "dst": "new:INC1.x"},
    {"op": "tunnel", "id": "to", "loop": "new:C1", "body": "new:C1.f0", "parent": 20, "dir": "out", "as": "TO1"},
    {"op": "wire", "id": "w_out", "src": "new:INC1.x+1", "dst": "new:TO1.inner"},
    {"op": "wire", "id": "w_back", "src": "new:TO1.outer", "dst": "2.cnt in"}]
PASS_T = {"op": "wire", "id": "w_true", "src": {"uid": "new:TI1", "side": "inner", "frame": "True"},
          "dst": {"uid": "new:TO1", "side": "inner", "frame": "True"}}
PLAN_A = HEAD + [PASS_T]
PLAN_B = HEAD + [
    {"op": "create", "id": "inc2", "class": "Function", "diagram": "new:C1.f1", "as": "INC2", "prim": "Increment",
     "terminals": INC, "pos": [10, 10]},
    {"op": "wire", "id": "w_t_in", "src": {"uid": "new:TI1", "side": "inner", "frame": "True"}, "dst": "new:INC2.x"},
    {"op": "wire", "id": "w_t_out", "src": "new:INC2.x+1", "dst": {"uid": "new:TO1", "side": "inner", "frame": "True"}}]


def plan(acts, stage="xcf124"):
    return {"schema": "stageplan/1", "stage": stage, "actions": acts}


ok, why = protocol.validate_obj(plan(PLAN_B))
bad = copy.deepcopy(PLAN_A)
bad[-1]["src"]["frame"] = 1
ok2, why2 = protocol.validate_obj(plan(bad))
gate("S01 stageplan/1: `frame` (a frame NAME) on a wire end validates", ok, why)
gate("S02 stageplan/1: a non-string `frame` is refused", not ok2 and "frame" in why2, why2)


def sim(acts):
    st = SS.base_state(base)
    effs = [SS.OPS[a["op"]](st, a, SS.model_for(a["op"], {})[0], None, {})[0] for a in acts]
    return st, effs


st, effs = sim(PLAN_A)
F0, F1, TI, TO = st["sym"]["new:C1.f0"], st["sym"]["new:C1.f1"], st["sym"]["new:TI1"], st["sym"]["new:TO1"]
rows = lambda u: [r for r in st["terminals"] if r["owner_uid"] == u]          # noqa: E731
ti_shape = sorted((r["term_class"], r["is_source"], r["frame_diagram"]) for r in rows(TI))
gate("M01 the case data tunnel per 123-9: ONE SelectorTunnel, ONE outer face on the parent (20), ONE inner face per frame",
     ti_shape == sorted([("OuterTerminal", False, 20), ("InnerTerminal", True, F0), ("InnerTerminal", True, F1)])
     and [o["class"] for o in st["objs"] if o["uid"] == TI] == ["SelectorTunnel"], ti_shape)
ti1 = next(r for r in rows(TI) if r["frame_diagram"] == F1)
to1 = next(r for r in rows(TO) if r["frame_diagram"] == F1 and r["term_class"] == "InnerTerminal")
ti0 = next(r for r in rows(TI) if r["frame_diagram"] == F0)
inc_x = next(r for r in st["terminals"] if r["owner_uid"] == st["sym"]["new:INC1"] and r["term_name"] == "x")
gate("M02 the True-frame wire: TI1's True inner (source) and TO1's True inner (sink) on ONE new wire, effect case_frame "
     "{index 1, name True}", ti1["wire_uid"] and ti1["wire_uid"] == to1["wire_uid"] and ti1["wire_uid"] != ti0["wire_uid"]
     and effs[-1].get("how") == "new" and effs[-1].get("case_frame", {}).get("index") == 1
     and effs[-1]["case_frame"].get("name") == "True" and effs[-1]["case_frame"].get("diagram") == F1, effs[-1])
gate("M03 the False frame is untouched by it: TI1's False inner still on INC1.x's wire",
     ti0["wire_uid"] and ti0["wire_uid"] == inc_x["wire_uid"], (ti0, inc_x))
gate("M04 st['case_frames'] records the case's frame order [[False, f0], [True, f1]]; case_frame_of(f1) == (case, 1, True)",
     st["case_frames"][str(st["sym"]["new:C1"])] == [["False", F0], ["True", F1]]
     and SS.case_frame_of(st, F1) == (st["sym"]["new:C1"], 1, "True"), st.get("case_frames"))
stp = sim(HEAD)[0]
e1 = raises(lambda: SS.resolve_addr(stp, {"uid": "new:TI1", "side": "outer", "frame": "True"}, False), SS.SimError)
e2 = raises(lambda: SS.resolve_addr(stp, {"uid": "new:TI1", "side": "inner", "frame": "Maybe"}, True), SS.SimError)
e3 = raises(lambda: SS.resolve_addr(stp, {"uid": 2, "term": "cnt", "frame": "True"}, True), SS.SimError)
e4 = raises(lambda: SS.resolve_addr(stp, {"uid": 60, "side": "inner", "frame": "True"}, True), SS.SimError)
gate("M05 refusals: `frame` with side outer; an unknown frame name (lists the frames); `frame` on a node; on a LoopTunnel",
     "side 'outer'" in e1 and "'Maybe'" in e2 and "False" in e2 and "no case-tunnel inner face" in e3
     and "no case-tunnel inner face" in e4, (e1, e2, e3, e4))
stb, effb = sim(PLAN_B)
i2 = [r for r in stb["terminals"] if r["owner_uid"] == stb["sym"]["new:INC2"]]
gate("M06 node ends in the True frame: TI1 True inner -> INC2.x and INC2.x+1 -> TO1 True inner, both effects index 1",
     all(r["wire_uid"] for r in i2) and effb[-1]["case_frame"]["index"] == 1 and effb[-2]["case_frame"]["index"] == 1,
     [e.get("case_frame") for e in effb[-2:]])

ops = SX.compile_plan(plan(PLAN_A))
cf = [o for o in ops if o["kind"] == "case_frame_wire"]
gate("C01 compile: the frame wire = ONE case_frame_wire op {frame True, frame_index 1, case new:C1}; the tunnel groups unchanged",
     [o["kind"] for o in ops] == ["create", "create", "tunnel", "tunnel", "case_frame_wire"] and len(cf) == 1
     and cf[0]["frame"] == "True" and cf[0]["frame_index"] == 1 and cf[0]["case"] == "new:C1" and cf[0]["acts"] == [9], ops)
fa = copy.deepcopy(PASS_T)
fa["src"]["frame"] = fa["dst"]["frame"] = "False"
gate("C02 compile: frame 'False' -> frame_index 0; plan B's two node-end wires -> two case_frame_wire ops index 1",
     SX.compile_plan(plan(HEAD + [fa]))[-1]["frame_index"] == 0
     and [(o["kind"], o.get("frame_index")) for o in SX.compile_plan(plan(PLAN_B))][-2:]
     == [("case_frame_wire", 1), ("case_frame_wire", 1)])
mix = copy.deepcopy(PASS_T)
mix["dst"]["frame"] = "False"
lt = copy.deepcopy(PASS_T)
lt["src"] = {"uid": 60, "side": "inner", "frame": "True"}
ce = [raises(lambda p=p: SX.compile_plan(plan(p)), SX.ExecStop) for p in (HEAD + [mix], HEAD + [lt], HEAD + [
    {"op": "wire", "id": "w_x", "src": {"uid": "new:TI1", "side": "inner", "frame": "Maybe"}, "dst": "new:INC1.x"}])]
gate("C03 compile refuses: ends naming different frames; `frame` on a base LoopTunnel; a frame name the case does not have",
     "different frames" in ce[0] and "only a tunnel or selector" in ce[1] and "not a frame of" in ce[2], ce)

tmp = tempfile.mkdtemp(prefix="selftest_cf124_")
gp, md = os.path.join(tmp, "graph.json"), os.path.join(tmp, "models")
os.makedirs(md, exist_ok=True)
json.dump(base, open(gp, "w", encoding="utf-8"))
q = lambda *a, **k: None   # noqa: E731


def dry(acts, stage):
    p = dict(plan(acts, stage), context={"s1_graph": {"path": gp}})
    pp = os.path.join(tmp, "plan_in_%s.json" % stage)
    json.dump(p, open(pp, "w", encoding="utf-8"))
    S = SS.simulate(pp, gp, out_root=os.path.join(tmp, "sim_" + stage), plan_out_dir=tmp, model_dir=md, log=q)
    try:
        dst, dff, ex = SX.dry_run(os.path.join(tmp, "plan_%s.json" % stage), log=q, model_dir=md, require_final=False)
    except SX.ExecStop as e:
        return S, "STOP " + str(e), None, None
    chk = [r for r in ex.report if r.get("op") == "case_frame_wire"]
    return S, dst, dff, chk


saved = SX.ROUTE_VERBS["case_frame_wire"]
SX.ROUTE_VERBS["case_frame_wire"] = []                # stub: the verb is card 124-1's (D03 reads the real table)
try:
    SA, da, fa_, ca = dry(PLAN_A, "xcfa124")
    SB, db, fb_, cb = dry(PLAN_B, "xcfb124")
finally:
    SX.ROUTE_VERBS["case_frame_wire"] = saved
ck = (ca or [{}])[0].get("result", {}).get("check") or {}
gate("D01 plan A simulates (failed None) and DRY-RUNS PASS; the dry case_frame_wire check: frame_index 1, 'True', src/dst "
     "{'tunnel': <positive bound uid>}, variant new_wire, census {Wire 1} (card 124-6: measured R3)", SA["failed"] is None
     and da == "PASS" and ck.get("frame_index") == 1 and ck.get("frame_name") == "True" and ck.get("src", {}).get("tunnel", -1) > 0
     and ck.get("dst", {}).get("tunnel", -1) > 0 and ck.get("variant") == "new_wire" and ck.get("census") == {"Wire": 1},
     (SA["failed"], da, str(fa_)[:200], ck))
kb = [(c.get("result", {}).get("check") or {}) for c in (cb or [])]
gate("D02 plan B DRY-RUNS PASS: the node ends route as {'node': <uid>, 'term': 'x'} / {'node', 'term': 'x+1'}, both index 1",
     SB["failed"] is None and db == "PASS" and len(kb) == 2 and kb[0].get("dst", {}).get("term") == "x"
     and kb[1].get("src", {}).get("term") == "x+1" and kb[0].get("src", {}).get("tunnel", -1) > 0
     and all(k.get("frame_index") == 1 for k in kb), (SB["failed"], db, str(fb_)[:200], kb))
miss = SX.verbs_missing("case_frame_wire")
_s, dr, dfr, _c = dry(PLAN_A, "xcfr124")
gate("D03 the real ROUTE_VERBS: gscript.case_frame_wire %s -> dry %s" % ("MISSING" if miss else "defined",
                                                                         "FAILS naming CREATE-NO-VERB" if miss else "PASS"),
     (dr != "PASS" and "CREATE-NO-VERB case_frame_wire" in str(dfr) + str(dr)) if miss else dr == "PASS", (miss, dr, str(dfr)[:240]))


class FakeS(object):
    work = "C:/fake/work.vi"

    def _op(self, verb, fn, detail=""):
        try:
            return {"verb": verb, "err": None, "result": fn(), "s": 0.0}
        except Exception as x:   # noqa: BLE001
            return {"verb": verb, "err": str(x), "result": None, "s": 0.0}

    def junk_purge(self, tag="", hints=()):
        return None


class FakeG(object):
    def __init__(self, **over):
        self.log, self.over = [], over

    def case_frame_wire(self, target, case_uid, frame_index, src, dst):
        self.log.append((target, case_uid, frame_index, src, dst))
        r = {"wire_uid": 555, "src_term_uid": 11, "dst_term_uid": 12, "broken": False, "purged": 1, "invoke_left": 0}
        r.update(self.over)
        return r


def lvbe(g):
    be = object.__new__(SX.LVBackend)
    be.g, be.s = g, FakeS()
    return be


SX.ROUTE_VERBS["case_frame_wire"] = []
try:
    g1 = FakeG()
    out = lvbe(g1).case_frame_wire(900, 1, {"tunnel": 41}, {"tunnel": 42}, [], {"acts": [9]})
    eL2 = raises(lambda: lvbe(FakeG(broken=True)).case_frame_wire(900, 1, {"tunnel": 41}, {"node": 7, "term": "x"}, [],
                                                                    {"acts": [9]}), SX.ExecStop)
    eL3 = raises(lambda: lvbe(FakeG(invoke_left=2)).case_frame_wire(900, 1, {"tunnel": 41}, {"tunnel": 42}, [],
                                                                     {"acts": [9]}), SX.ExecStop)
finally:
    SX.ROUTE_VERBS["case_frame_wire"] = saved
gate("L01 LVBackend: gscript.case_frame_wire(work, 900, 1, {'tunnel': 41}, {'tunnel': 42}) called once; wire 555 back, variant "
     "new_wire, census {Wire 1}", g1.log == [("C:/fake/work.vi", 900, 1, {"tunnel": 41}, {"tunnel": 42})] and out.get("wire_uid") == 555
     and out.get("variant") == "new_wire" and out.get("census") == {"Wire": 1}, (g1.log, out))
gate("L02 NEGATIVE: a wire read back broken STOPS", "Is Broken? True" in eL2, eL2)
gate("L03 NEGATIVE: a junk Invoke left after the verb's purge STOPS", "junk Invoke" in eL3, eL3)

v2 = os.path.join(ROOT, "tools", "bench", "plan_ring_p3a_in_v2.json")
pv = json.load(open(v2, encoding="utf-8"))
rep = CP.predict(pv, {}, json.load(open(CP.DEFAULT_SAMPLES, encoding="utf-8")))
r20 = next(r for r in rep["rows"] if r["k"] == 21)
CS_ = json.load(open(CP.DEFAULT_SAMPLES, encoding="utf-8"))["ops"]
gate("U01 (card 124-6) ROUTE_CENSUS = the MEASURED samples of census_samples.json (case_frame_wire new_wire {Wire 1} / branch {}, "
     "connect_term_uid {SelectorTunnel 1, OuterTerminal 1, InnerTerminal 2, Wire 2}); census_predict (no rule for these rows): v2 "
     "row 21 CENSUS-UNPREDICTED, overall UNPREDICTED (=> --scratch-required keeps the scratch run)",
     SX.ROUTE_CENSUS["case_frame_wire"] == dict((v["name"], v["delta"]) for v in CS_["case_frame_wire"]["variants"])
     and SX.ROUTE_CENSUS["connect_term_uid"] == dict((v["name"], v["delta"]) for v in CS_["connect_term_uid"]["variants"])
     and r20["id"] == "p3a_w_true_pass" and r20["verdict"] == "CENSUS-UNPREDICTED" and rep["overall"] == "UNPREDICTED",
     (SX.ROUTE_CENSUS, r20, rep["overall"]))
SV = SS.simulate(v2, os.path.join(ROOT, pv["base"]["path"]), out_root=os.path.join(tmp, "sim_v2"), plan_out_dir=tmp, log=q)
ops_v2 = SX.compile_plan(pv)
o20 = [o for o in ops_v2 if o["kind"] == "case_frame_wire"]
gate("V01 plan_ring_p3a_in_v2.json simulates EVERY action on graph_ring_p2b (failed None) and its action 21 compiles to ONE "
     "case_frame_wire {True, index 1, new:CS1}", SV["failed"] is None and len(o20) == 1 and o20[0]["acts"] == [21]
     and o20[0]["frame_index"] == 1 and o20[0]["case"] == "new:CS1", (SV["failed"], o20))
gate("R01 every earlier ROUTE_VERBS route kept (case, case_wired, while, for, queue, stop, gate ...)",
     {"while", "for", "local_read", "local_write", "indicator", "control", "primitive", "copy_in", "const_on_term", "queue",
      "subvi", "case", "case_wired", "gate", "stop"} <= set(SX.ROUTE_VERBS)
     and SX.ROUTE_VERBS["case_wired"] == [("gscript", "case_wired"), ("gscript", "struct_copy_nested"), ("gscript", "case_frames")])

# ---------------------------------------------------------------- card 124-6 (PD250(c)): connect_term_uid + case_frame_wire branch
REG = [
    {"op": "add_shift_reg", "id": "sr", "loop": 100, "body": 20, "parent": 10, "as": "SR9"},
    {"op": "create", "id": "cs", "class": "CaseStructure", "diagram": 20, "as": "C1", "selector_as": "S1", "src": "2.flag",
     "frames": ["False", "True"], "pos": [40, 40]},
    {"op": "create", "id": "inc", "class": "Function", "diagram": "new:C1.f0", "as": "INC1", "prim": "Increment",
     "terminals": INC, "pos": [10, 10]},
    {"op": "create", "id": "inc3", "class": "Function", "diagram": "new:C1.f0", "as": "INC3", "prim": "Increment",
     "terminals": INC, "pos": [10, 90]},
    {"op": "tunnel", "id": "ti", "loop": "new:C1", "body": "new:C1.f0", "parent": 20, "dir": "in", "as": "TI1"},
    {"op": "wire", "id": "w_in", "src": "new:SR9L.inner", "dst": "new:TI1.outer"},
    {"op": "wire", "id": "w_inc", "src": "new:TI1.inner", "dst": "new:INC1.x"},
    {"op": "tunnel", "id": "to", "loop": "new:C1", "body": "new:C1.f0", "parent": 20, "dir": "out", "as": "TO1"},
    {"op": "wire", "id": "w_out", "src": "new:INC1.x+1", "dst": "new:TO1.inner"},
    {"op": "wire", "id": "w_back", "src": "new:TO1.outer", "dst": "new:SR9R.inner"},
    dict(PASS_T),
    {"op": "wire", "id": "w_br", "src": {"uid": "new:TI1", "side": "inner", "frame": "False"}, "dst": "new:INC3.x"}]
oR = SX.compile_plan(plan(REG))
ctu = [o for o in oR if o["kind"] == "connect_term_uid"]
gate("C04 compile: a register-inner-face group on a plan-made case = connect_term_uid (acts [5,6,7] in, [8,9,10] out, variant "
     "register_end_case_border); HEAD's node-end groups stay `tunnel`",
     [o["kind"] for o in oR] == ["add_sr", "create", "create", "create", "connect_term_uid", "connect_term_uid", "case_frame_wire",
                                 "case_frame_wire"] and [o["acts"] for o in ctu] == [[5, 6, 7], [8, 9, 10]]
     and all(o["variant"] == "register_end_case_border" and o["case"] == "new:C1" for o in ctu)
     and [o["kind"] for o in ops].count("tunnel") == 2, [(o["kind"], o["acts"]) for o in oR])
cfo = [o for o in oR if o["kind"] == "case_frame_wire"]
gate("C05 compile variant: the True pass-through (unwired face) = new_wire; the second sink on TI1's False face (its group wired "
     "it) = branch", [(o["frame"], o["variant"]) for o in cfo] == [("True", "new_wire"), ("False", "branch")], cfo)
badd = copy.deepcopy(REG)
badd[4]["dir"] = "out"
e6 = raises(lambda: SX.compile_plan(plan(badd)), SX.ExecStop)
gate("C06 compile refuses a left register (srL) on an OUTPUT tunnel group", "srL feeds an INPUT tunnel" in e6, e6)
SR, dr_, dfr_, _cr = dry(REG, "xctu124")
_x = SX.dry_run(os.path.join(tmp, "plan_xctu124.json"), log=q, model_dir=md, require_final=False)[2]
cks = dict((r["k"], (r.get("result") or {}).get("check") or {}) for r in _x.report if r.get("k"))
okD = SR["failed"] is None and dr_ == "PASS" and [cks[k].get("route") for k in (5, 6, 7, 8)] == [
    "connect_term_uid", "connect_term_uid", "case_frame_wire", "case_frame_wire"]
gate("D04 the register + case plan simulates and DRY-RUNS PASS with the REAL ROUTE_VERBS: routes connect_term_uid x2 (census "
     "SelectorTunnel 1, OuterTerminal 1, InnerTerminal 2, Wire 2) + case_frame_wire new_wire {Wire 1} / branch {}",
     okD and cks[5].get("census") == SX.ROUTE_CENSUS["connect_term_uid"]["register_end_case_border"]
     and cks[7].get("variant") == "new_wire" and cks[8].get("variant") == "branch" and cks[8].get("census") == {},
     (SR["failed"], dr_, str(dfr_)[:300], dict((k, (v.get("route"), v.get("variant"))) for k, v in cks.items())))
st_r = SS.simulate(os.path.join(tmp, "plan_in_xctu124.json"), gp, out_root=os.path.join(tmp, "sim_ctu2"), plan_out_dir=tmp,
                   model_dir=md, log=q)["_state"]
ti_r = [r for r in st_r["terminals"] if r["owner_uid"] == st_r["sym"]["new:TI1"]]
i3 = next(r for r in st_r["terminals"] if r["owner_uid"] == st_r["sym"]["new:INC3"] and r["term_name"] == "x")
i1 = next(r for r in st_r["terminals"] if r["owner_uid"] == st_r["sym"]["new:INC1"] and r["term_name"] == "x")
gate("M07 the model of R4: INC3.x sits on the SAME wire as INC1.x (TI1's False face branched), the True face on its own wire",
     i3["wire_uid"] and i3["wire_uid"] == i1["wire_uid"] and len(set(r["wire_uid"] for r in ti_r if r["term_class"] == "InnerTerminal")) == 2,
     (i1, i3))


class FakeT(object):
    def __init__(self, **over):
        self.log, self.over = [], over

    def connect_term_uid(self, target, sink_uid, src_uid):
        self.log.append((target, sink_uid, src_uid))
        r = {"wire_uid": 777, "broken": False, "sink_echo": sink_uid, "src_echo": src_uid, "err": "", "purged": 0, "invoke_left": []}
        r.update(self.over)
        return r


gt = FakeT()
o4 = lvbe(gt).connect_term_uid(31, 32, [], {"acts": [5, 6, 7], "variant": "register_end_case_border"})
e42 = raises(lambda: lvbe(FakeT(broken=True)).connect_term_uid(31, 32, [], {"acts": [5]}), SX.ExecStop)
e43 = raises(lambda: lvbe(FakeT(invoke_left=[9])).connect_term_uid(31, 32, [], {"acts": [5]}), SX.ExecStop)
gate("L04 LVBackend.connect_term_uid: gscript.connect_term_uid(work, SINK 32, SRC 31) once, wire 777, census R1/R2; broken / "
     "a junk Invoke left STOP", gt.log == [("C:/fake/work.vi", 32, 31)] and o4.get("wire_uid") == 777
     and o4.get("census") == SX.ROUTE_CENSUS["connect_term_uid"]["register_end_case_border"] and "Is Broken? True" in e42
     and "junk Invoke" in e43, (gt.log, o4, e42, e43))
real_b = [{"term_uid": 11, "wire_uid": 444}]
e45 = raises(lambda: lvbe(FakeG()).case_frame_wire(900, 0, {"tunnel": 41}, {"node": 7, "term": "x"}, real_b,
                                                    {"acts": [12], "variant": "branch"}), SX.ExecStop)
o45 = lvbe(FakeG(wire_uid=444)).case_frame_wire(900, 0, {"tunnel": 41}, {"node": 7, "term": "x"}, real_b,
                                                 {"acts": [12], "variant": "branch"})
gate("L05 LVBackend.case_frame_wire variant branch: a wire != the source face's live wire STOPS; == it passes, census {}",
     "!= the source face's wire" in e45 and o45.get("census") == {} and o45.get("variant") == "branch", (e45, o45))
import stage_prerun as SPR   # noqa: E402
gate("P01 stage_prerun.SP_WIRING has case_frame_wire and connect_term_uid and == stagexec.REC_WIRING (X5 counts what the dry "
     "trace records)", set(SPR.SP_WIRING) == set(SX.REC_WIRING) and {"case_frame_wire", "connect_term_uid"} <= set(SPR.SP_WIRING),
     (SPR.SP_WIRING, SX.REC_WIRING))
v3 = os.path.join(ROOT, "tools", "bench", "plan_ring_p3a_in_v3.json")
if os.path.exists(v3):
    p3 = json.load(open(v3, encoding="utf-8"))
    S3 = SS.simulate(v3, os.path.join(ROOT, p3["base"]["path"]), out_root=os.path.join(tmp, "sim_v3"), plan_out_dir=tmp, log=q)
    rc3 = S3.get("route_check") or {}
    un3 = [r for r in rc3.get("rows") or [] if r.get("unroutable")]
    gate("V02 plan_ring_p3a_in_v3.json: simulates every action, FINAL, route check PASS (no UNROUTABLE row); routes include "
         "connect_term_uid x2 and case_frame_wire new_wire + branch", S3["failed"] is None and S3["final"] and rc3.get("status") == "PASS"
         and not un3 and [r["route"] for r in rc3["rows"]].count("connect_term_uid") == 2
         and [r["route"] for r in rc3["rows"]].count("case_frame_wire") == 2, (S3["failed"], S3["final"], rc3.get("status"), un3[:3]))

bad = [l for l, ok in gates if not ok]
print("=== GATES: %d pass / %d fail%s" % (len(gates) - len(bad), len(bad), "; failing: " + bad[0] if bad else ""), flush=True)
print(protocol.result_line(protocol.make_result(len(gates) - len(bad), len(bad), bad[0] if bad else None, [])), flush=True)
sys.exit(1 if bad else 0)
