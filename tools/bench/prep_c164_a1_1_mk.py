# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_164-a1-1.md
# ---
r"""prep_c164_a1_1_mk - card 164-a1-1 Part 3 (OFFLINE, json only, never launched), PD397(c): plan_ring_p5s02d.json = P5-2 step 4 = the longest whole-group
prefix of J K3 K3f K4 K4f (A53..A80 of the EDITED plan_ring_p5s02r_in.json 4c8d3645, PD397(b)) with X10 MAIN <= 675 and rows <= 40, FINAL on the real
p5s02c graph 3d5196ab (VI 564d8cbe). Inputs + ONE call of prep_plan_flow_lib.make_step_plan (the 163-a1-1 flow, parametrised; self-test there).
Symbols: new:CQ7 / .f0 / .f1 by the p5s02a run's creation map, new:TD7 etc. by the p5s02c run's map (adopted chain), each on its own sim ids.
PREDICTION CONTRACT: M0 pins; OWN each used symbol made by one adopted step; MAP/FRM bound on 3d5196ab ('True' -> #31517); ROWS; X10 per prefix;
  plan = longest passing prefix (J alone <= 675 else FAIL); PROBE / TIE / SB final True, 0 PROVISIONAL, route PASS, 0 UNROUTABLE; X8 / X17 clean; U pins.
    py tools/bgrun.py --material --max-min 15 --log tools/bench/prep_c164_a1_1_mk.log -- py -u tools/bench/prep_c164_a1_1_mk.py"""
import os, sys                                                                               # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, B)
import prep_plan_flow_lib as FL                                                              # noqa: E402
L, J, md5, rel, CD, ROOT = FL.L, FL.J, FL.md5, FL.rel, FL.CD, FL.ROOT
P = lambda n: os.path.normpath(os.path.join(B, n))                                           # noqa: E731
WANT = dict((os.path.normpath(os.path.join(ROOT, i["path"])), i["md5"]) for i in J("tools/bench/cards/task_164-a1-1.json")["inputs"])
WANT[P("plan_ring_p5s02r_in.json")] = "4c8d3645"                                             # Part 2 edit (prep_c164_a1_1_cmp.log)
VIC, VIA = os.path.join(CD, "D1_ring_p5s02c_20261010_125755.vi"), os.path.join(CD, "D1_ring_p5s02a_20261010_023239.vi")
WANT.update({P("plan_ring_p5s02a.json"): "4284c22a", P("plan_ring_p5s02b.json"): "f4520b10", P("graph_ring_p5s02a_20261010_032547.json"): "7ac24924",
             P("graph_ring_p5s02b_20261010_111905.json"): "431cfd83", VIC: "564d8cbe", VIA: "94ffff94", os.path.join(CD, "D1_ring_p5s02b_20261010_105511.vi"): "f9ae7751"})
gate = L.Gate()
M0 = dict((p, md5(p)) for p in WANT)
gate("M0 input md5 == card / brief pins", all(M0[p].startswith(w) for p, w in WANT.items()), dict((os.path.basename(p), M0[p][:8]) for p in WANT))
GRAPH = P("graph_ring_p5s02c_20261010_131658.json")
SRC = [{"name": "p5s02a", "plan": P("plan_ring_p5s02a.json"), "graph_after": P("graph_ring_p5s02a_20261010_032547.json"), "vi": VIA},
       {"name": "p5s02b", "plan": P("plan_ring_p5s02b.json"), "graph_after": P("graph_ring_p5s02b_20261010_111905.json"), "vi": os.path.join(CD, "D1_ring_p5s02b_20261010_105511.vi")},
       {"name": "p5s02c", "plan": P("plan_ring_p5s02c.json"), "graph_after": GRAPH, "vi": VIC}]
goal = lambda lo, hi, cand, ch: ("RING P5-2 step 4 (card 164-a1-1, PD397(b)(c)): A{0}..A{1} of plan_ring_p5s02r_in.json 4c8d3645 on the REAL 564d8cbe graph 3d5196ab; "
                                 "plan {2} = longest whole-group prefix with MAIN <= 675, rows <= 40; MAIN per prefix {3}").format(
    lo, hi, ch, dict((k, v.get("main")) for k, v in cand.items()))[:400]                 # noqa: E731
F = FL.make_step_plan(gate, P("plan_ring_p5s02r_in.json"), ["J", "K3", "K3f", "K4", "K4f"], GRAPH, VIC, P("plan_ring_p5s02c.json"), SRC, "c164-a1-1",
                      "ring_p5s02d", P("plan_ring_p5s02d_in.json"), P("prep_c164_a1_1_session.json"), goal,
                      "card 164-a1-1 PROBE (fact only): step-4 rows on 564d8cbe", keep_prev=P("plan_ring_p5s02d_prev.json"))
cm = F["sources"]["p5s02a"]["cmap"]
for k, v in F["frame_map"].items():
    ln = [i for i, t in enumerate(open(os.path.join(ROOT, cm), encoding="utf-8"), 1) if '"sim": {0}, "real": {1},'.format(v["sim"], v["real_frame"]) in t]
    print("FACT CQ7FRAME {0}: frame {1!r} -> {2} -> sim {3} -> real {4}; record {5}:{6}".format(k, v["frame_name"], v["frame_sym"], v["sim"], v["addr"], cm, ln), flush=True)
gate("CQ7 every 'True' frame end -> one real frame uid from the p5s02a creation map", len(set(v["addr"] for v in F["frame_map"].values() if v["frame_name"] == "True")) == 1,
     F["frame_map"].keys())
gate("U inputs / VI / tool pins untouched", all(md5(q) == M0[q] for q in WANT), [os.path.basename(q) for q in WANT if md5(q) != M0[q]])
sys.exit(gate.result())
