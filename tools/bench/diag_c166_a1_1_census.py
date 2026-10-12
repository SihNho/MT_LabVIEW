# ---
# labview: none
# hardware: none
# evidence: tools/bench/diag_c165_p5s02e_scratch.log
# ---
r"""diag_c166_a1_1_census - card 166-a1-1 step 7 (OFFLINE, files only): plan_ring_p5s02e_pred.json `census` = the step-5 scratch's
MEASURED new-object census, parsed by the shared stagekit.scratch_census (the ONE `CENSUS-ALL new uids by class` line of the last bgrun
segment of diag_c165_p5s02e_scratch.log, == its _sum.json); `census_overall` MEASURED-SCRATCH, `census_source` cites the log and the
graph read; nothing else changes - the same three keys card 164-3-7 wrote for step 4 (prep_c164_a3_7_write.py (b),
plan_ring_p5s02d_pred.json:15-28,1013-1032). Calls stagekit.scratch_census, prep_c156_a1_1_lib (md5, Gate), diag_c166_a1_1_lib.
Order (retrospective-cycle165 fault 2): runs only after diag_c166_a1_1_mm.log ended RESULT PASS.
PREDICTION CONTRACT: C0 mm PASS; C1 pred 825cbf65; C2 census line 148 == {DigitalNumericConstant 1, InnerTerminal 6, LeftShiftRegister 1,
OuterTerminal 4, RightShiftRegister 1, SelectorTunnel 2, Terminal 1, Wire 5} (diag_c165_a3_4_facts.md:17); C3 the graph read shows the
made objects (E5 PASS line); C4 written in the old layout; C5 only census / census_overall / census_source differ, census == measured.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c166_a1_1_census.log -- py -u tools/bench/diag_c166_a1_1_census.py"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import stagekit as K  # noqa: E402
import prep_c156_a1_1_lib as L  # noqa: E402
import diag_c166_a1_1_lib as J  # noqa: E402

B = os.path.join(ROOT, "tools", "bench")
PRED, PRB = os.path.join(B, "plan_ring_p5s02e_pred.json"), os.path.join(B, "diag_c166_a1_1_pred_before.json")
SLOG, SJ = os.path.join(B, "diag_c165_p5s02e_scratch.log"), os.path.join(B, "diag_c165_p5s02e_scratch_sum.json")
MMLOG, GLOG = os.path.join(B, "diag_c166_a1_1_mm.log"), os.path.join(B, "diag_c165_a3_4_graph.log")
GRAPH = "tools/bench/graph_ring_p5s02e_20261012_173009.json"
WANT = {"DigitalNumericConstant": 1, "InnerTerminal": 6, "LeftShiftRegister": 1, "OuterTerminal": 4, "RightShiftRegister": 1,
        "SelectorTunnel": 2, "Terminal": 1, "Wire": 5}
gate = L.Gate(fatal_default=False)


def lines_with(path, token):
    return [(i, ln.rstrip()) for i, ln in enumerate(open(path, encoding="utf-8", errors="replace"), 1) if token in ln]


mmr = [ln for _i, ln in lines_with(MMLOG, "RESULT ")]
gate("C0 order: diag_c166_a1_1_mm.log ended RESULT PASS (load_by_vi written first)", bool(mmr) and json.loads(mmr[-1][7:])["status"] == "PASS", mmr[-1:])
gate("C1 plan_ring_p5s02e_pred.json md5 825cbf65", L.md5(PRED).startswith("825cbf65"), L.md5(PRED))
meas, ln_no, seg0 = K.scratch_census(SLOG, SJ)
gate("C2 scratch census = line {0} of diag_c165_p5s02e_scratch.log (stagekit.scratch_census, == _sum.json) == diag_c165_a3_4_facts.md:17".format(ln_no),
     ln_no == 148 and meas == WANT, (ln_no, seg0, meas))
net = lines_with(SLOG, "CENSUS-ALL net delta")
lost = lines_with(SLOG, "CENSUS-ALL lost uids")
e5 = [x for x in lines_with(GLOG, "PASS  E5 ")]
gr = os.path.join(ROOT, GRAPH)
G = json.load(open(gr, encoding="utf-8"))
cls = dict((int(o["uid"]), o["class"]) for o in G["objs"])
made = {31812: "RightShiftRegister", 31817: "LeftShiftRegister", 31824: "DigitalNumericConstant", 31847: "SelectorTunnel", 31855: "SelectorTunnel"}
seen = dict((u, cls.get(u)) for u in made)
gate("C3 the graph read shows the made objects with their classes (graph E5 PASS line + {0})".format(GRAPH), bool(e5) and seen == made, (e5[:1], seen))
if gate.G["fail"] == 0:
    new = json.load(open(PRED, encoding="utf-8"))
    prev = {"census": new.get("census"), "census_overall": new.get("census_overall")}
    new["census"] = dict(sorted(meas.items()))
    new["census_overall"] = "MEASURED-SCRATCH"
    new["census_source"] = {"card": "166-a1-1", "decided": "docs/d1/ring-p5c.md:252-256 PD403(b) + brief_166-a1-1.md step 7: the step-5 scratch census is "
                            "recorded into the pred after the close-out graph read and the load_by_vi entry; CEN2 stays an equality",
                            "log": "tools/bench/diag_c165_p5s02e_scratch.log", "line": ln_no, "segment_from": seg0, "log_md5": L.md5(SLOG),
                            "net_line": net[-1][0] if net else None, "lost_line": lost[-1][0] if lost else None,
                            "expect": "CENSUS-ALL new uids by class (every class)",
                            "graph_reads": ["tools/bench/diag_c165_a3_4_graph.log:{0}".format(e5[0][0]), "{0} (md5 {1}) objs {2}".format(
                                GRAPH, L.md5(gr), sorted(made))],
                            "what": "stagekit.census_gate counts NEW uids per class (after - before); the graph read shows the 5 made objects "
                                    "(RSR 31812, LSR 31817, DNC 31824, SelectorTunnel 31847 / 31855) with these classes",
                            "previous": prev}
    ok, _o = J.rewrite_json(PRED, new, PRB)
    gate("C4 plan_ring_p5s02e_pred.json written in its old layout and line ending (backup {0})".format(os.path.basename(PRB)), ok)
    if ok:
        a, b = json.load(open(PRB, encoding="utf-8")), json.load(open(PRED, encoding="utf-8"))
        ch = J.changed_keys(a, b)
        gate("C5 pred compare: only census / census_overall / census_source differ; census == measured", ch == ["census", "census_overall", "census_source"]
             and b["census"] == meas, ch)
        print("FACT pred {0} -> {1}; census {2}".format(L.md5(PRB), L.md5(PRED), json.dumps(b["census"], sort_keys=True)), flush=True)
else:
    print("FACT a precondition failed: pred NOT written", flush=True)
sys.exit(gate.result([{"path": "tools/bench/plan_ring_p5s02e_pred.json", "md5": L.md5(PRED)}]))
