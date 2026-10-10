# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_164-3-6.md
# ---
r"""prep_c164_a3_6_mk - card 164-3-6 step 1+2 (OFFLINE, json only): re-make plan_ring_p5s02d.json with the SAME single call of
prep_plan_flow_lib.make_step_plan as prep_c164_a3_1_mk.py:53-55 (same r_in 9dadb0c1, groups J+K3, graph 3d5196ab, VI 564d8cbe, base plan p5s02c,
sources, census prep_c164_a3_1_census.json bb30814a, card label and goal text), with ONLY plan_in = tools/bench/plan_ring_p5s02d_in2.json
(gate L0 name rule stagekit.py:3015-3022), session = prep_c164_a3_6_session.json, keep_prev = plan_ring_p5s02d_prev725cd68e.json.
Existing pieces found: prep_plan_flow_lib.make_step_plan / leaves (called); prep_c164_a3_1_mk.py (the call copied as parameters only).
PREDICTION CONTRACT: M0 pins; ASIDE prev == 725cd68e; plan final True, 19 rows A53..A71, 15 ops, checkpoints [0,1,2,6,7,11,12,14,15], MAIN 647.8;
  CMP vs 725cd68e: actions, open_rows, end_cdiff_rows, ops, checkpoints equal; differing leaf keys only under finalized/plan_in, finalized/summary,
  finalized/last_step md5 (step files re-written) or none else; END w23460 0 terminal rows (judgement 164-3: absent = 0 rows), w23519 sinks
  {23450, 23241, 7606} source 8494; U pins unchanged.
    py tools/bgrun.py --material --max-min 15 --log tools/bench/prep_c164_a3_6_mk.log -- py -u tools/bench/prep_c164_a3_6_mk.py"""
import json, os, sys                                                                         # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, B)
import prep_plan_flow_lib as FL                                                              # noqa: E402
L, J, md5, rel, CD, ROOT = FL.L, FL.J, FL.md5, FL.rel, FL.CD, FL.ROOT
P = lambda n: os.path.normpath(os.path.join(B, n))                                           # noqa: E731
OUT, PREV, PIN = P("plan_ring_p5s02d.json"), P("plan_ring_p5s02d_prev725cd68e.json"), P("plan_ring_p5s02d_in2.json")
WANT = dict((os.path.normpath(os.path.join(ROOT, i["path"])), i["md5"]) for i in J("tools/bench/cards/task_164-3-6.json")["inputs"])
WANT.pop(OUT)                                                                                # replaced here (prev kept aside, gate ASIDE)
VIC, VIA = os.path.join(CD, "D1_ring_p5s02c_20261010_125755.vi"), os.path.join(CD, "D1_ring_p5s02a_20261010_023239.vi")
VIB = os.path.join(CD, "D1_ring_p5s02b_20261010_105511.vi")
GRAPH = P("graph_ring_p5s02c_20261010_131658.json")
WANT.update({P("plan_ring_p5s02a.json"): "4284c22a", P("plan_ring_p5s02b.json"): "f4520b10", P("graph_ring_p5s02a_20261010_032547.json"): "7ac24924",
             P("graph_ring_p5s02b_20261010_111905.json"): "431cfd83", VIC: "564d8cbe", VIA: "94ffff94", VIB: "f9ae7751", GRAPH: "3d5196ab"})
gate = L.Gate()
M0 = dict((p, md5(p)) for p in WANT)
gate("M0 input md5 == card / brief pins", all(M0[p].startswith(w) for p, w in WANT.items()), dict((os.path.basename(p), M0[p][:8]) for p in WANT))
gate("M1 plan_ring_p5s02d.json before == 725cd68e; plan_in2 absent", md5(OUT).startswith("725cd68e") and not os.path.isfile(PIN), (md5(OUT), os.path.isfile(PIN)))
OLD = J(OUT)
SRC = [{"name": "p5s02a", "plan": P("plan_ring_p5s02a.json"), "graph_after": P("graph_ring_p5s02a_20261010_032547.json"), "vi": VIA},
       {"name": "p5s02b", "plan": P("plan_ring_p5s02b.json"), "graph_after": P("graph_ring_p5s02b_20261010_111905.json"), "vi": VIB},
       {"name": "p5s02c", "plan": P("plan_ring_p5s02c.json"), "graph_after": GRAPH, "vi": VIC}]
goal = lambda lo, hi, cand, ch: ("RING P5-2 step 4 (card 164-3-1, PD399(a)(b)): A{0}..A{1} of plan_ring_p5s02r_in.json 9dadb0c1 (J in the P4 delete form: "
                                 "dw_23460 before the deletes, rle_23519 after #23501; K3f/K4/K4f next step) on the REAL 564d8cbe graph 3d5196ab; plan {2} = "
                                 "longest whole-group prefix with MAIN <= 675, rows <= 40; MAIN per prefix {3}").format(
                                 lo, hi, ch, dict((k, v.get("main")) for k, v in cand.items()))[:400]   # noqa: E731  (same text as prep_c164_a3_1_mk.py:49-52)
F = FL.make_step_plan(gate, P("plan_ring_p5s02r_in.json"), ["J", "K3"], GRAPH, VIC, P("plan_ring_p5s02c.json"), SRC, "c164-3-1",
                      "ring_p5s02d", PIN, P("prep_c164_a3_6_session.json"), goal,
                      "card 164-3-1 PROBE (fact only): step-4 rows J+K3 on 564d8cbe", keep_prev=PREV, census=P("prep_c164_a3_1_census.json"))
gate("ASIDE previous plan kept as plan_ring_p5s02d_prev725cd68e.json == 725cd68e", md5(PREV).startswith("725cd68e"), md5(PREV))
NEW = J(OUT)
print("FACT NEW plan md5 {0}; plan_in2 md5 {1}".format(md5(OUT), md5(PIN)), flush=True)
gate("PLAN final True, chosen J+K3, 19 rows", NEW.get("final") is True and F["chosen"] == "J+K3" and len(NEW["actions"]) == 19, (NEW.get("final"), F["chosen"], len(NEW["actions"])))
gate("CK checkpoints [0,1,2,6,7,11,12,14,15], 15 ops, MAIN 647.8", F["compile"]["checkpoints"] == [0, 1, 2, 6, 7, 11, 12, 14, 15] and len(F["compile"]["ops"]) == 15
     and F["x10"]["main"] == 647.8, (F["compile"]["checkpoints"], len(F["compile"]["ops"]), F["x10"]["main"]))
for k in ("actions", "open_rows", "base", "context", "schema", "stage", "goal", "final"):
    gate("CMP {0} equal to 725cd68e".format(k), NEW.get(k) == OLD.get(k), None)
for k in ("end_cdiff_rows", "open_rows_match", "base", "route_check"):
    gate("CMP finalized/{0} equal to 725cd68e".format(k), (NEW["finalized"]).get(k) == (OLD["finalized"]).get(k),
         ((OLD["finalized"]).get(k), (NEW["finalized"]).get(k)) if not isinstance((OLD["finalized"]).get(k), list) else None)
lo, ln = FL.leaves(OLD), FL.leaves(NEW)
dk = sorted(k for k in set(lo) | set(ln) if lo.get(k) != ln.get(k))
for k in dk:
    print("FACT DIFFKEY {0}: {1} -> {2}".format(k, str(lo.get(k))[:90], str(ln.get(k))[:90]), flush=True)
gate("CMP differing leaf keys only under finalized/plan_in|summary|last_step|step_files md5 ({0} keys)".format(len(dk)),
     all(k.strip("/").startswith(("finalized/plan_in", "finalized/summary", "finalized/last_step", "finalized/step_files")) for k in dk), dk[:20])
sf = sorted((NEW.get("finalized") or {}).get("step_files") or [], key=lambda x: int(x["n"]))
END = J(os.path.join(ROOT, sf[-1]["path"]))["state"]
r60 = [r for r in END["terminals"] if r["wire_uid"] == 23460]
r19 = [r for r in END["terminals"] if r["wire_uid"] == 23519]
gate("END1 w23460 0 terminal rows in the sim end graph (judgement 164-3: absent = 0 rows)", not r60, [r["term_uid"] for r in r60])
snk = sorted(int(r["term_uid"]) for r in r19 if not r["is_source"])
gate("END2 w23519 source t8494, sinks {{23450, 23241, 7606}}: sinks {0}".format(snk),
     snk == sorted([23450, 23241, 7606]) and [int(r["term_uid"]) for r in r19 if r["is_source"]] == [8494])
gate("U inputs / VI / tool pins untouched", all(md5(q) == M0[q] for q in WANT), [os.path.basename(q) for q in WANT if md5(q) != M0[q]])
sys.exit(gate.result())
