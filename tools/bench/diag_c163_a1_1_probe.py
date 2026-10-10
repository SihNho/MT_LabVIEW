# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_163-a1-1.md
# ---
r"""diag_c163_a1_1_probe - card 163-a1-1 (OFFLINE, json read only): list the actions of plan_ring_p5s02r_in.json (id, op, alias, ends) and
the keys / finalized step files of plan_ring_p5s02b.json, so the maker reads the real structure instead of guessing. No write besides its log.
PREDICTION: 80 actions; p5s02b final True with step_files.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c163_a1_1_probe.log -- py -u tools/bench/diag_c163_a1_1_probe.py"""
import json, os, sys                                                                         # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol                                                                   # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
R = json.load(open(os.path.join(B, "plan_ring_p5s02r_in.json"), encoding="utf-8"))
print("RIN keys", [k for k in R if k != "actions"])
for i, a in enumerate(R["actions"], 1):
    print("A{0:02d} {1} {2} as={3} {4}".format(i, a.get("id"), a.get("op"), a.get("as"),
          json.dumps(dict((k, v) for k, v in a.items() if k not in ("id", "op", "why", "as")))[:260]))
    if 41 <= i <= 60:
        print("     why: {0}".format((a.get("why") or "")[:260]))
P = json.load(open(os.path.join(B, "plan_ring_p5s02b.json"), encoding="utf-8"))
fz = P.get("finalized") or {}
print("P5S02B keys", list(P), "final", P.get("final"), "base", P.get("base"), "fz keys", list(fz))
print("P5S02B step_files last", (fz.get("step_files") or [])[-1:])
print("P5S02B actions", [a.get("id") for a in P["actions"]])
S = json.load(open(os.path.join(B, "prep_c160_b3_1_session.json"), encoding="utf-8"))
print("B3 SESSION keys", list(S), "creation_map", S.get("creation_map"))
print(protocol.result_line(protocol.make_result(1, 0, None, [])))
