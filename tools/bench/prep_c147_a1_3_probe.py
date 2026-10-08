# ---
# labview: none
# hardware: none
# ---
r"""prep_c147_a1_3_probe - card 147-a1-3 (OFFLINE, read-only). Prints the rebased s06 plan's finalized keys, base, end cdiff rows, the v18
sim rows after action #147, the rebase uid binding, and the plan's open rows on #2626. Nothing written.
PREDICTION: files readable -> RESULT 1/0.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/prep_c147_a1_3_probe.log -- py -u tools/bench/prep_c147_a1_3_probe.py"""
import json, os, sys                                                                     # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
J = lambda p: json.load(open(os.path.join(ROOT, p), encoding="utf-8"))                     # noqa: E731
p = J("tools/bench/plan_ring_p4_s06v18.json")
fz = p["finalized"]
print("KEYS", sorted(fz.keys()))
print("BASE", p.get("base"), "| FZBASE", fz.get("base"))
print("END", len(fz["end_cdiff_rows"]), sorted(fz["end_cdiff_rows"]))
s = J("tools/bench/sim/ring_p4_v18/ring_p4_v3/summary.json")
st = dict((x["n"], x) for x in s["steps"])
print("V18", len(st[147]["cdiff_rows"]), sorted(st[147]["cdiff_rows"]))
print("ONLY-S06", sorted(set(fz["end_cdiff_rows"]) - set(st[147]["cdiff_rows"])))
print("ONLY-V18", sorted(set(st[147]["cdiff_rows"]) - set(fz["end_cdiff_rows"])))
rb = fz.get("rebase")
print("REBASE", json.dumps(rb)[:3000])
print("OPEN2626", [r for r in p.get("open_rows") or [] if r.get("node") == 2626])
print("OPENALL", [(r.get("node"), r.get("term")) for r in p.get("open_rows") or []])
print("STEPS", [x["path"] for x in fz.get("step_files") or []][:2], len(fz.get("step_files") or []))
print(protocol.result_line(protocol.make_result(1, 0, None, [])), flush=True)
