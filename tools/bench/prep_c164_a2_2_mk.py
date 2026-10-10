# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_164-a2-2.md
# ---
r"""prep_c164_a2_2_mk - card 164-a2-2 (OFFLINE, json only, never launched), retry of 164-a2-1: plan_ring_p5s02d.json = P5-2 step 4 = the longest
whole-group prefix of J K3 ONLY (A53..A69 of plan_ring_p5s02r_in.json 4d93c82d; K3f/K4/K4f left for the next step - K3f/K4f inner-face sinks are
UNROUTABLE, diag_c164_a2_1_facts.md) with X10 MAIN <= 675 and rows <= 40, FINAL on the real p5s02c graph 3d5196ab (VI 564d8cbe). Copy of
prep_c164_a2_1_mk.py (not edited): same inputs + ONE call of prep_plan_flow_lib.make_step_plan; changes: group list ["J","K3"], card/session/goal names,
keep_prev = plan_ring_p5s02d_all28_false.json (the Final-False e3054ab6 is copied aside by the shared function; _jonly 1152ce60 is NOT overwritten),
and one read-only print of every plan action id with its compiled op kind (brief step 5).
PREDICTION CONTRACT: M0 pins; GRP; MAP / FRM ('True' -> #31517); ROWS; STUB PASS (K3f not in the rows); C J and J+K3 compile (K3 pass wire = kind
  connect_term_uid variant register_end_case_border); plan = J+K3 (17 rows, MAIN 642.5); PROBE / TIE / SB final True, 0 PROVISIONAL, route PASS,
  0 UNROUTABLE; C-OUT / IDS; X8 / X17 clean; JONLY 1152ce60; U pins unchanged.
    py tools/bgrun.py --material --max-min 15 --log tools/bench/prep_c164_a2_2_mk.log -- py -u tools/bench/prep_c164_a2_2_mk.py"""
import os, sys                                                                               # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, B)
import prep_plan_flow_lib as FL                                                              # noqa: E402
L, J, md5, rel, CD, ROOT = FL.L, FL.J, FL.md5, FL.rel, FL.CD, FL.ROOT
SX = FL.SX
P = lambda n: os.path.normpath(os.path.join(B, n))                                           # noqa: E731
WANT = dict((os.path.normpath(os.path.join(ROOT, i["path"])), i["md5"]) for i in J("tools/bench/cards/task_164-a2-2.json")["inputs"])
VIC, VIA = os.path.join(CD, "D1_ring_p5s02c_20261010_125755.vi"), os.path.join(CD, "D1_ring_p5s02a_20261010_023239.vi")
VIB = os.path.join(CD, "D1_ring_p5s02b_20261010_105511.vi")
WANT.update({P("plan_ring_p5s02a.json"): "4284c22a", P("plan_ring_p5s02b.json"): "f4520b10", P("graph_ring_p5s02a_20261010_032547.json"): "7ac24924",
             P("graph_ring_p5s02b_20261010_111905.json"): "431cfd83", VIC: "564d8cbe", VIA: "94ffff94", VIB: "f9ae7751"})
gate = L.Gate()
M0 = dict((p, md5(p)) for p in WANT)
gate("M0 input md5 == card / brief pins", all(M0[p].startswith(w) for p, w in WANT.items()), dict((os.path.basename(p), M0[p][:8]) for p in WANT))
GRAPH = P("graph_ring_p5s02c_20261010_131658.json")
SRC = [{"name": "p5s02a", "plan": P("plan_ring_p5s02a.json"), "graph_after": P("graph_ring_p5s02a_20261010_032547.json"), "vi": VIA},
       {"name": "p5s02b", "plan": P("plan_ring_p5s02b.json"), "graph_after": P("graph_ring_p5s02b_20261010_111905.json"), "vi": VIB},
       {"name": "p5s02c", "plan": P("plan_ring_p5s02c.json"), "graph_after": GRAPH, "vi": VIC}]
goal = lambda lo, hi, cand, ch: ("RING P5-2 step 4 (card 164-a2-2, retry of 164-a2-1, PD397(c)): A{0}..A{1} of plan_ring_p5s02r_in.json 4d93c82d (groups J+K3 "
                                 "only; K3f/K4/K4f next step) on the REAL 564d8cbe graph 3d5196ab; plan {2} = longest whole-group prefix with MAIN <= 675, rows <= 40; "
                                 "MAIN per prefix {3}").format(lo, hi, ch, dict((k, v.get("main")) for k, v in cand.items()))[:400]   # noqa: E731
F = FL.make_step_plan(gate, P("plan_ring_p5s02r_in.json"), ["J", "K3"], GRAPH, VIC, P("plan_ring_p5s02c.json"), SRC, "c164-a2-2",
                      "ring_p5s02d", P("plan_ring_p5s02d_in.json"), P("prep_c164_a2_2_session.json"), goal,
                      "card 164-a2-2 PROBE (fact only): step-4 rows J+K3 on 564d8cbe", keep_prev=P("plan_ring_p5s02d_all28_false.json"))
gate("ASIDE Final-False plan kept as plan_ring_p5s02d_all28_false.json == e3054ab6", md5(P("plan_ring_p5s02d_all28_false.json")).startswith("e3054ab6"), md5(P("plan_ring_p5s02d_all28_false.json")))
gate("JONLY J-alone plan plan_ring_p5s02d_jonly.json == 1152ce60", md5(P("plan_ring_p5s02d_jonly.json")).startswith("1152ce60"), md5(P("plan_ring_p5s02d_jonly.json")))
for k, v in F["frame_map"].items():
    print("FACT CQ7FRAME {0}: frame {1!r} -> {2} -> sim {3} -> real {4}".format(k, v["frame_name"], v["frame_sym"], v["sim"], v["addr"]), flush=True)
for nm, c in F["candidates"].items():
    print("FACT PREFIX {0}: rows {1}, MAIN {2}, error {3}".format(nm, c["rows"], c.get("main"), c.get("error")), flush=True)
PL = J(P("plan_ring_p5s02d.json"))
ops = SX.compile_plan(PL, owners=SX.plan_base_owners(PL))
for k, a in enumerate(PL["actions"], 1):
    o = next((o for o in ops if k in o["acts"]), None)
    print("FACT ACTOP k={0} {1} op={2}: compiled op {3} {4}/{5}".format(k, a["id"], a["op"], o and ops.index(o) + 1, o and o["kind"], o and o.get("variant")), flush=True)
for pid in ("w_k3pass", "w_k4pass"):
    k = next((i for i, a in enumerate(PL["actions"], 1) if a["id"] == pid), None)
    op = next((o for o in ops if k in o["acts"]), None) if k else None
    print("FACT PASS {0}: plan action {1}; op {2}".format(pid, k, op and dict((x, op.get(x)) for x in ("kind", "variant", "acts", "tunnel", "in_act", "out_act", "case"))), flush=True)
    if k:
        gate("PASS {0} is the out-wire of its in-tunnel group (case_pass_wire True): kind connect_term_uid / register_end_case_border, out_act {1}".format(pid, k),
             op is not None and op.get("out_act") == k and op["kind"] == "connect_term_uid" and op.get("variant") == "register_end_case_border", op)
gate("U inputs / VI / tool pins untouched", all(md5(q) == M0[q] for q in WANT if not q.endswith("plan_ring_p5s02d.json")),
     [os.path.basename(q) for q in WANT if md5(q) != M0[q]])
sys.exit(gate.result())
