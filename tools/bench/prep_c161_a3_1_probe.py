# ---
# labview: none
# hardware: none
# evidence: tools/bench/prep_c161_a2_1_measure.log
# ---
"""prep_c161_a3_1_probe - card 161-a3-1: read-only look at the shapes the PB inherit function needs (base graph keys, plan actions,
adopt record, step files). OFFLINE. PREDICTION: prints keys; no file written."""
import os, sys, json                                                                       # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                                       # noqa: E402
import protocol                                                                            # noqa: E402

B = K.BENCH
g = K.jload(B, "graph_ring_p5s02a_20261010_032547.json")
print("BASEKEYS", dict((k, v if not isinstance(v, (list, dict)) else type(v).__name__ + str(len(v))) for k, v in g.items()))
p = K.jload(B, "plan_ring_p5s02b.json")
print("PLANKEYS", list(p.keys()), list(p["finalized"].keys()))
print("STEP0", p["finalized"]["step_files"][0], len(p["finalized"]["step_files"]))
for i, a in enumerate(p["actions"]):
    print("ACT", i, json.dumps(a)[:260])
r = [json.loads(x) for x in open(os.path.join(B, "adopted_scratch.jsonl"), encoding="utf-8") if x.strip()][-1]
print("ADOPT", json.dumps(r)[:1600])
L = K.jload(K.ROOT, p["finalized"]["step_files"][-1]["path"])["state"]
print("SYM", dict((k, v) for k, v in (L.get("sym") or {}).items()))
pa = K.jload(B, "plan_ring_p5s02a.json")
La = K.jload(K.ROOT, pa["finalized"]["step_files"][-1]["path"])["state"]
print("SYM_A", dict((k, v) for k, v in (La.get("sym") or {}).items()))
for k in ("pass_through", "passthrough", "pd374", "registers"):
    print("PKEY", k, p.get(k), p["finalized"].get(k))
print(protocol.result_line(protocol.make_result(1, 0, None, [])), flush=True)
