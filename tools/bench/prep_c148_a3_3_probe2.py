# ---
# labview: none
# hardware: none
# ---
"""prep_c148_a3_3_probe2 - card 148-a3-3 (OFFLINE, read-only): the shape of one s06 step file (keys of the step and of its
state), the v18 ops after op 135 (kind, acts, ids, refs), and how the s06 dry recorded the sink-gate route. Writes nothing.
PREDICTION CONTRACT: prints only; RESULT 1/0."""
import json, os, sys                                                                        # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagexec as SX                                                                       # noqa: E402
J = lambda p: json.load(open(os.path.join(ROOT, p), encoding="utf-8"))                       # noqa: E731
st = J("tools/bench/sim/ring_p4_s06v18/step_25_wire.json")
print("step keys", list(st), "state keys", list(st["state"]))
for k, v in st.items():
    if k != "state":
        print("STEP", k, json.dumps(v, default=str)[:600])
print("terminal row", st["state"]["terminals"][0])
print("sym", st["state"].get("sym"), "neg", st["state"].get("neg"), "md5", st["state"].get("md5"), "vi", st["state"].get("vi"))
v18 = J("tools/bench/plan_ring_p4_v18.json")
A, OPS = v18["actions"], SX.compile_plan(v18)
print("NOP", len(OPS))
for k in range(136, len(OPS) + 1):
    o = OPS[k - 1]
    print("OP", k, o["kind"], o.get("route"), [A[n - 1]["id"] for n in o["acts"]],
          json.dumps([dict((f, A[n - 1].get(f)) for f in ("op", "src", "dst", "as", "class", "label", "indicator", "born_on", "of", "loop", "diagram", "nodes")
                           if A[n - 1].get(f) is not None) for n in o["acts"]])[:700])
print(protocol.result_line(protocol.make_result(1, 0, None, [])))
