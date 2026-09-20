"""READ-ONLY: does a For-loop NODE's Terminals[] list its tunnels' OUTER terminals (with wires)? Decides how the
step-C pool array (an auto-indexed OUTPUT tunnel) reaches Index Array: connect_terminals by index (if listed) or a
new op. Target: the saved step-B core (1 indexed input tunnel, 4 non-indexed inputs, 3 indexed outputs).
  py tools/bgrun.py --max-min 4 --log tools/bench/census_loop_node_terms.log -- py -u tools/bench/census_loop_node_terms.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

OP = os.path.join(g.CLAUDEDEV, "Track_v6_CPU_core_v0.vi")
g._lv = None
labels = {r["uid"]: r["label"] for r in g.node_labels(OP, 0)}
for n in range(40):
    u, rows = g.node_terms_uid(OP, 0, n)
    if not u:
        break
    if labels.get(u) == "For Loop":
        print(f"For Loop node n{n} uid {u}: {len(rows)} terminals", flush=True)
        for r in rows:
            print(f"   {r['i']:>3} | {r['name']!r:<24} | src={r['is_source']!s:<5} | wire={r['wire']}", flush=True)
print("tunnels:", flush=True)
for o in g.report_all(OP, "LoopTunnel"):
    t = g.tunnels(OP, o["i"])
    print(f"   tunnel {t['uid']}: mode {t['index_mode']} outer {t['out_name']!r} src={t['out_is_source']} wire {t['out_wire']} inner {t['in_wires']}", flush=True)
