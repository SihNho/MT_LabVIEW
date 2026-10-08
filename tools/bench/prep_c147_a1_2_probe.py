# ---
# labview: none
# hardware: none
# ---
r"""prep_c147_a1_2_probe - card 147-a1-2 read-only probe (OFFLINE): where does v18's own simulated per-op cdiff live, so the s06 end can be
compared with v18 over the same ops. Prints v18 plan keys / finalized metadata and the s06 summary end rows. Writes nothing.
PREDICTION CONTRACT: P0 v18 plan loads; prints facts only.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c147_a1_2_probe.log -- py -u tools/bench/prep_c147_a1_2_probe.py"""
import json, os, sys                                                                         # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
J = lambda p: json.load(open(os.path.join(ROOT, p), encoding="utf-8"))                     # noqa: E731
p = J("tools/bench/plan_ring_p4_v18.json")
print("FACT v18 stage", p.get("stage"), "keys", list(p.keys()))
print("FACT v18 base", json.dumps(p.get("base"))[:400])
print("FACT v18 context", json.dumps(p.get("context"))[:600])
f = p.get("finalized") or {}
for k, v in f.items():
    if k in ("cdiff_inputs", "open_rows_classed"):
        continue
    print("FACT v18 finalized", k, json.dumps(v if not isinstance(v, list) else (len(v), v[:2], v[-2:]), default=str)[:600])
sp = (f.get("summary") or {}).get("path")
if sp and os.path.isfile(os.path.join(ROOT, sp)):
    s = J(sp)
    print("FACT v18 summary", sp, "steps", len(s["steps"]), "end rows", len(s.get("end_cdiff_rows") or []))
else:
    print("FACT v18 summary missing", sp)
s6 = J("tools/bench/sim/ring_p4_s06v18/summary.json")
print("FACT s06 summary end rows", len(s6.get("end_cdiff_rows") or []), s6.get("end_cdiff_rows"))
print("FACT s06 context", json.dumps((J("tools/bench/plan_ring_p4_s06v18.json").get("context")))[:600])
print(protocol.result_line(protocol.make_result(1, 0, None, [])), flush=True)
