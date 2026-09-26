"""selftest_stage_prerun_graphload - card 95-1: stage_prerun's graph loader accepts ONLY the terminal-list graph
shape and refuses every other shape with a clear message (no KeyError 'terminals'). Offline, no LabVIEW.

    py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_stage_prerun_graphload.log -- py -u tools/bench/selftest_stage_prerun_graphload.py

Prediction contract: 18 gates, all PASS. Positive per accepted shape (plain terminal-list; terminal-list with extra
keys), negative per refused shape (edge graph, loop census, object census, malformed rows, empty list, not JSON,
not an object), find_graph per md5 (S1 -> None + skipped list; K-S4 -> graph_k_s4 not graph_loops_k_s4; S3 ->
graph_s3_loop15; L2-A1 -> sim graph), and _graph() with a wrong-shape override -> None + graph_error, no raise."""
import json, os, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
os.chdir(ROOT)
import stage_prerun as SP                                                           # noqa: E402

B = "tools/bench/"
RES = []


def gate(label, ok, detail=""):
    RES.append(bool(ok))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:300]), flush=True)


def load(p):
    return json.load(open(p, encoding="utf-8"))


def md5_of(p):
    return load(p)["md5"]


def shape(p):
    return SP.graph_shape_error(load(p))


# accepted shapes
gate("G1 terminal-list graph (graph_s3_loop15) accepted", shape(B + "graph_s3_loop15_20260924.json") is None)
gate("G2 terminal-list + extra keys (sim/l2a1/graph_k_80_owners) accepted",
     shape(B + "sim/l2a1/graph_k_80_owners.json") is None)
og = SP.OfflineGraph(B + "graph_k_s4_20260925.json")
gate("G3 OfflineGraph(graph_k_s4) loads", len(og.terms) > 1000 and len(og.objs) > 1000,
     "terms {0} objs {1}".format(len(og.terms), len(og.objs)))
# refused shapes
r = shape(B + "graph_s1_20260924.json")
gate("G4 edge graph (graph_s1_20260924) refused, reason names terminals", r and "terminals" in r, r)
r = shape(B + "graph_loops_k_s4_20260925.json")
gate("G5 loop census (graph_loops_k_s4) refused", r and "terminals" in r, r)
r = shape(B + "graph_objs_s1_20260923.json")
gate("G6 object census (graph_objs_s1) refused", r and "objs" in r, r)
try:
    SP.OfflineGraph(B + "graph_s1_20260924.json")
    gate("G7 OfflineGraph(graph_s1) raises GraphShapeError", False, "no exception")
except SP.GraphShapeError as e:
    gate("G7 OfflineGraph(graph_s1) raises GraphShapeError naming the file", "graph_s1_20260924.json" in str(e), e)
except KeyError as e:
    gate("G7 OfflineGraph(graph_s1) raises GraphShapeError", False, "KeyError %s" % e)
# malformed synthetic
tmp = tempfile.mkdtemp(prefix="graphload95_")
cases = {
    "rows": {"md5": "0" * 32, "terminals": [{"term_uid": 1, "term_name": "x", "is_source": 0, "wire_uid": 0}],
             "objs": [{"uid": 1, "class": "Add"}]},
    "empty": {"md5": "0" * 32, "terminals": [], "objs": [{"uid": 1, "class": "Add"}]},
    "list": [1, 2, 3],
}
for name, d in cases.items():
    p = os.path.join(tmp, "graph_%s.json" % name)
    json.dump(d, open(p, "w", encoding="utf-8"))
    try:
        SP.OfflineGraph(p)
        gate("G8-%s malformed graph refused" % name, False, "loaded")
    except SP.GraphShapeError as e:
        gate("G8-%s malformed graph refused with a clear message" % name, True, e)
    except Exception as e:                                                         # noqa: BLE001
        gate("G8-%s malformed graph refused with GraphShapeError" % name, False, "%s %s" % (type(e).__name__, e))
p = os.path.join(tmp, "graph_nojson.json")
open(p, "w", encoding="utf-8").write('{"md5": "' + "0" * 32 + '", "terminals": [')
try:
    SP.OfflineGraph(p)
    gate("G9 truncated JSON refused", False, "loaded")
except SP.GraphShapeError as e:
    gate("G9 truncated JSON refused with GraphShapeError", True, e)
except Exception as e:                                                             # noqa: BLE001
    gate("G9 truncated JSON refused with GraphShapeError", False, "%s %s" % (type(e).__name__, e))
# find_graph per md5
s1 = md5_of(B + "graph_s1_20260924.json")
f = SP.find_graph(s1)
gate("G10 find_graph(S1 md5) -> None (no terminal-list S1 graph on disk)", f is None, f)
gate("G11 ... and FIND_SKIPPED lists graph_s1_20260924.json", any("graph_s1_20260924.json" in a for a, _ in SP.FIND_SKIPPED),
     [a for a, _ in SP.FIND_SKIPPED])
f = SP.find_graph(md5_of(B + "graph_k_s4_20260925.json"))
gate("G12 find_graph(K-S4 md5) -> graph_k_s4 (not the newer graph_loops_k_s4)",
     f and os.path.basename(f) == "graph_k_s4_20260925.json", f)
f = SP.find_graph(md5_of(B + "graph_s3_loop15_20260924.json"))
gate("G13 find_graph(S3 md5) -> graph_s3_loop15", f and os.path.basename(f) == "graph_s3_loop15_20260924.json", f)
f = SP.find_graph(md5_of(B + "sim/l2a1/graph_k_80_owners.json"))
gate("G14 find_graph(L2-A1 md5) -> sim/l2a1/graph_k_80_owners", f and f.replace("\\", "/").endswith("sim/l2a1/graph_k_80_owners.json"), f)
# _graph() with a wrong-shape override: None + graph_error, no exception
SP.D.graph, SP.D.graph_override, SP.D.input_md5 = None, B + "graph_s1_20260924.json", s1
try:
    g = SP._graph()
    gate("G15 _graph() with --graph graph_s1 -> None + graph_error", g is None and SP.D.graph_error, SP.D.graph_error)
except Exception as e:                                                             # noqa: BLE001
    gate("G15 _graph() with --graph graph_s1 -> None + graph_error", False, "%s %s" % (type(e).__name__, e))
SP.D.graph, SP.D.graph_override, SP.D.input_md5 = None, None, s1
g = SP._graph()
gate("G16 _graph() without --graph on S1 md5 -> None + graph_error listing skipped shapes",
     g is None and SP.D.graph_error and "skipped" in SP.D.graph_error, SP.D.graph_error)
npass = sum(RES)
nfail = len(RES) - npass
print("=== GATES: {0} pass / {1} fail".format(npass, nfail))
print('RESULT {"schema":"result-line/1","status":"%s","gates":{"pass":%d,"fail":%d},"first_fail":null,"artefacts":[]}'
      % ("PASS" if not nfail else "FAIL", npass, nfail))
sys.exit(0 if not nfail else 1)
