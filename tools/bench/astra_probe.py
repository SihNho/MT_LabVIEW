"""Read the safe template through the reporter; never execute the template."""
import sys, gc, json
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gscript as g

# No automatic UI recovery: stop and inspect any unexpected dialog instead.
def run(vi, *args, **kwargs):
    return g._invoke(vi, 'Run', hard_timeout_s=20)
g._run = run
try:
    target = str(Path(g.CLAUDEDEV) / 'FPTARGET_v0.vi')
    print(json.dumps({'nodes': g.report(target, 'Node'),
                      'controls': g.report(target, 'ControlTerminal'),
                      'state': g.exec_state(target)}), flush=True)
finally:
    g._cache.clear()
    g._lv = None
    gc.collect()
