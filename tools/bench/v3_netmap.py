"""v3_netmap.py - headless connectivity dump of PARALLEL_kernel_v3.vi diagrams (OpNetInfo_v0).
  py tools/bgrun.py --max-min 20 --log tools/bench/v3_netmap.log -- py -u tools/bench/v3_netmap.py [--diag=1]
Traverse "Diagram" order on v3 (2026-09-07): 0 top level, 1 ForLoop uid 3447 (the new P=4 loop at (-874,734)),
2..5 Case Structure frames, 6 ForLoop uid 248 (old four-fold).
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
V3 = os.path.join(g.CLAUDEDEV, "PARALLEL_kernel_v3.vi")
diag = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--diag=")), 1))
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
nodes, nets = g.net_map(V3, diag)
print(f"=== PARALLEL_kernel_v3 diagram {diag}: {len(nodes)} nodes, {len(nets)} wires", flush=True)
g.print_net_map(nodes, nets)
json.dump({"nodes": {str(k): v for k, v in nodes.items()}, "nets": {str(k): v for k, v in nets.items()}},
          open(os.path.join(HERE, f"v3_netmap_diag{diag}.json"), "w"), indent=1)
