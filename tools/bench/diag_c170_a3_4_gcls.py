# ---
# labview: none
# hardware: none
# offline-args: tools/bench/graph_ring_p6_20261012_212645.json tools/bench/graph_disp_20260927.json
# evidence: tools/bench/cards/task_170-a3-4.json
# ---
"""diag_c170_a3_4_gcls - card 170-a3-4, files only: class counts of graph JSONs (Diagram / TopLevelDiagram / SubVI) and
the objs rows of #6810 / #22692. Why the plan-170 dry census read {6810: None, 22692: None} with 0 taint while plan 110's
read stub data (UNVERIFIED): diag_replay_lib.census walks g.report_all(t, 'Diagram'), which the dry answers from the graph
(stage_prerun.OfflineGraph.report_all:320-323). PREDICTION: none - a read."""
import json, collections, sys                                                            # noqa: E401
sys.path.insert(0, "tools")
import protocol                                                                          # noqa: E402

n = 0
for p in sys.argv[1:]:
    d = json.load(open(p, encoding="utf-8"))
    c = collections.Counter(o.get("class") for o in d.get("objs") or [])
    print(p, "keys", sorted(d.keys()), "md5", d.get("md5"), "objs", len(d.get("objs") or []), "terms", len(d.get("terminals") or []))
    print("  TopLevelDiagram", c.get("TopLevelDiagram"), "Diagram", c.get("Diagram"), "SubVI", c.get("SubVI"))
    print("  uids", [o for o in d.get("objs") or [] if o.get("uid") in (6810, 22692)])
    print("  top classes", c.most_common(10))
    n += 1
print(protocol.result_line({"status": "PASS", "gates": {"pass": n, "fail": 0}, "first_fail": None, "artefacts": []}))
