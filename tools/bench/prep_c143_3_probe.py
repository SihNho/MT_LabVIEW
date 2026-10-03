r"""prep_c143_3_probe - card 143-3 (OFFLINE, read-only): print the schema of a sim step state and of a graph json (keys, one terminal
row, owner classes available) so the fixed EL predictor reads the right fields. No LabVIEW. Prints a RESULT line.
    py -u tools/bench/prep_c143_3_probe.py"""
import json, os, sys                                                                        # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stage_prerun as SPR                                                                  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
J = lambda p: json.load(open(os.path.join(ROOT, p), encoding="utf-8"))                     # noqa: E731
for rec in ("tools/recipes/stage_d1_ring_p4_s02v18_scratch.py", "tools/recipes/stage_d1_ring_p4_s02v18.py",
            "tools/recipes/stage_d1_ring_p4_s03v18.py"):
    print("PLAN_MD5S", rec, SPR.plan_md5s(os.path.join(ROOT, rec)), flush=True)
st = J("tools/bench/sim/ring_p4_s02v18/step_34_create.json")
print("STEP keys", list(st.keys()), "state keys", list(st["state"].keys()), flush=True)
s = st["state"]
print("TERM row", s["terminals"][0], flush=True)
for k in s:
    if k != "terminals":
        v = s[k]
        print("STATE", k, type(v).__name__, (list(v.items())[:3] if isinstance(v, dict) else (v[:2] if isinstance(v, list) else v)), flush=True)
g = J("tools/bench/graph_ring_p4s02_20261003_112505.json")
print("GRAPH keys", list(g.keys()), flush=True)
for k in g:
    v = g[k]
    print("GRAPH", k, type(v).__name__, (list(v.items())[:3] if isinstance(v, dict) else (v[:2] if isinstance(v, list) else v)), flush=True)
print(protocol.result_line(protocol.make_result(1, 0, None, [])), flush=True)
