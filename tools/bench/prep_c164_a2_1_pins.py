# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_164-a2-1.md
# ---
r"""prep_c164_a2_1_pins - card 164-a2-1 Part 4 (OFFLINE, read only), PD398(d): call guard_write.open_card_pins (tools/hooks/guard_write.py:77-128,
read-only, the hook is not edited) on plan_ring_p5s02r_in.json after result_158-a3-3.json was written, and show 158-a3-3 no longer pins it.
PREDICTION: result_158-a3-3.json exists; open_card_pins lists no '158-a3-3' entry (exit 0).
    py tools/bgrun.py --material --max-min 2 --log tools/bench/prep_c164_a2_1_pins.log -- py -u tools/bench/prep_c164_a2_1_pins.py"""
import os, sys                                                                               # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for _p in (ROOT, os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "hooks")):
    sys.path.insert(0, _p)
import guard_write as G                                                                      # noqa: E402
from tools import protocol                                                                   # noqa: E402
res = os.path.join(ROOT, "tools", "bench", "cards", "result_158-a3-3.json")
r = G.open_card_pins(os.path.join(ROOT, "tools", "bench", "plan_ring_p5s02r_in.json"))
print("FACT RESULT result_158-a3-3.json exists: {0}".format(os.path.isfile(res)), flush=True)
print("FACT OPEN_CARD_PINS plan_ring_p5s02r_in.json -> {0}".format(r), flush=True)
bad = [x for x in r if "158-a3-3" in x]
print(protocol.result_line(protocol.make_result(1 if not bad and os.path.isfile(res) else 0, 1 if bad or not os.path.isfile(res) else 0,
                                                bad[0] if bad else None, [])), flush=True)
sys.exit(1 if bad else 0)
