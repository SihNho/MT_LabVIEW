"""params_dump_td.py - run OpCLFNParams_v0 in Get mode and save the full 'type string (7.x only)' to tools/bench/paraminfo_td.json"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 45.0)
labs = json.load(open(os.path.join(HERE, "opclfnparams_labels.json")))
vi = g.op(os.path.join(g.CLAUDEDEV, "OpCLFNParams_v0.vi")); vi.SetControlValue(labs["binary string"], ""); vi.SetControlValue(labs["operation"], 0)
try:
    g._run(vi)
except Exception as e:
    print("run:", str(e)[:200], flush=True)
td = list(vi.GetControlValue(labs["type string"]) or []); ds = vi.GetControlValue(labs["data string"])
print("data string", ds.encode("latin-1").hex(), "type string words", len(td), flush=True)
json.dump(td, open(os.path.join(HERE, "paraminfo_td.json"), "w")); print("td saved", flush=True)
