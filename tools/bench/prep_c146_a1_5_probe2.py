# ---
# labview: none
# hardware: none
# ---
r"""prep_c146_a1_5_probe2 - card 146-a1-5 (OFFLINE, read-only). Prints #2626 / #11261 terminals in the s05 sim END state
(sim/ring_p4_s05v18/step_21_create.json) and the v18 rows 118/119/132/150 dst, so the licence draft is keyed by uid.
PREDICTION CONTRACT: reads only; prints FACT lines; writes nothing.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c146_a1_5_probe2.log -- py -u tools/bench/prep_c146_a1_5_probe2.py"""
import json, os, sys                                                                       # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagexec as SX, stagesim as SS                                                      # noqa: E401,E402
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
B = os.path.join(ROOT, "tools", "bench")
e = J(os.path.join(B, "sim", "ring_p4_s05v18", "step_21_create.json"))["state"]
print("FACT terminals type", type(e["terminals"]).__name__, "n", len(e["terminals"]))
tl = e["terminals"] if isinstance(e["terminals"], list) else list(e["terminals"].values())
print("FACT terminal sample", json.dumps(tl[0])[:600])
for n in (2626, 11261):
    print("FACT class", n, SS.obj_class(e, n))
    for t in tl:
        if isinstance(t, dict) and t.get("owner_uid") == n:
            print("FACT T", n, json.dumps(t)[:500])
print("FACT objs type", type(e["objs"]).__name__, "sample", json.dumps(e["objs"][0] if isinstance(e["objs"], list) else list(e["objs"].items())[0])[:500])
v18 = J(os.path.join(B, "plan_ring_p4_v18.json"))
A, OPS = v18["actions"], SX.compile_plan(v18)
for k in (117, 118, 119, 132, 150):
    for n in OPS[k - 1]["acts"]:
        print("FACT V18 op", k, json.dumps(A[n - 1])[:600])
print("FACT v18 open_rows", json.dumps(v18.get("open_rows"))[:1500])
print(protocol.result_line(protocol.make_result(1, 0, None, [])), flush=True)
