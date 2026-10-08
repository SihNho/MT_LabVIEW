# ---
# labview: none
# hardware: none
# ---
"""prep_c148_a3_3_probe - card 148-a3-3 (OFFLINE, read-only): print memory_model start inputs, the s06 plan's base / finalized
step files / actions shape, the s05 creation-map path, and the s06 licence. Writes nothing.
PREDICTION CONTRACT: prints only; RESULT 1/0."""
import json, os, sys, glob                                                                  # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
J = lambda p: json.load(open(os.path.join(ROOT, p), encoding="utf-8"))                       # noqa: E731
m = J("tools/bench/memory_model.json")
print("growth", m["load_growth_mb_per_op"])
print("load_by_vi", dict((k, v["value"]) for k, v in m["load_by_vi"].items()))
for k in ("op0_read_mb", "read_mb", "edit_mb", "other_mb", "final_read_mb", "fail_above_mb", "start_mb"):
    print(k, (m.get(k) or {}).get("value"))
p = J("tools/bench/plan_ring_p4_s06v18.json")
print("keys", list(p))
print("base", p["base"])
f = p.get("finalized") or {}
print("finalized keys", list(f))
print("finalized.base", f.get("base"), "plan_in", f.get("plan_in"))
print("step_files[-2:]", (f.get("step_files") or [])[-2:])
print("n actions", len(p["actions"]), "open_rows", p.get("open_rows"))
for a in p["actions"]:
    print("ACT", json.dumps(a)[:400])
print("cmaps", sorted(os.path.basename(x) for x in glob.glob(os.path.join(B, "creation_map", "plan_ring_p4_s0*"))))
print("licence", json.dumps(J("tools/bench/plan_ring_p4_s06v18_licence.json"))[:1500])
s5 = J("tools/bench/plan_ring_p4_s05v18.json")
print("s05 base", s5["base"], "final step", s5["finalized"]["step_files"][-1])
print(protocol.result_line(protocol.make_result(1, 0, None, [])))
