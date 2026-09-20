import sys, json, gc
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gscript as g
g._run = lambda vi, *a, **kw: g._invoke(vi, 'Run', hard_timeout_s=20)
try:
    target = str(Path(g.CLAUDEDEV)/'ASTRA_WIRING_20260913_v1.vi')
    print(json.dumps({'report':g.report(target,'IndexArray'), 'net':g.net_map(target,max_nodes=5,max_terms=3)}),flush=True)
finally:
    g._cache.clear(); g._lv=None; gc.collect()
