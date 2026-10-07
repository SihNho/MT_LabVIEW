# ---
# labview: none
# hardware: none
# ---
r"""diag_c146_a2_1_probe3 - card 146-a3-1 (OFFLINE, read-only): what the s05 PLAN itself says about the rows it wires on base nodes
#5058 / #29843 / #29724 (actions p4_w_img_trk, p4_t_slot_out, p4_w_pool_in; open_rows; finalized.open_rows_classed), and how
many start-state SubVI nodes carry an unwired sink named 'Image In'. PREDICTION CONTRACT: none (a census).
  py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c146_a2_1_probe3.log -- py -u tools/bench/diag_c146_a2_1_probe3.py"""
import json, os, sys                                                                        # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
p = J("tools/bench/plan_ring_p4_s05v18.json")
fz = p["finalized"]
for a in p["actions"]:
    s = json.dumps(a)
    if any(k in s for k in ("5058", "29843", "29724", "p4_w_img_trk", "p4_t_slot_out", "p4_w_pool_in")):
        print("ACTION {0}".format(s[:700]), flush=True)
print("OPEN_ROWS {0}".format(json.dumps(p.get("open_rows"))[:1500]), flush=True)
print("OPEN_ROWS_CLASSED {0}".format(json.dumps(fz.get("open_rows_classed"))[:2500]), flush=True)
st0 = J(fz["step_files"][0]["path"])["state"]
hits = [(r["owner_uid"], r.get("wire_uid")) for r in st0.get("terminals") or [] if r.get("term_name") == "Image In" and not r.get("is_source")]
print("IMAGE_IN sink rows at start (owner, wire) {0}".format(hits), flush=True)
print(protocol.result_line(protocol.make_result(0, 0, None, [])), flush=True)
