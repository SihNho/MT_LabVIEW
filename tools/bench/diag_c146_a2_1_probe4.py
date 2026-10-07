# ---
# labview: none
# hardware: none
# ---
r"""diag_c146_a2_1_probe4 - card 146-a3-1 (OFFLINE, read-only): can the s05 plan alone name the nodes an EARLIER counted session
made? Prints the s05 plan's `context`, the base doc's fs_carried.provisional (s04's simulated end) - its sym map and the owner uids
of its negative (sim-made) nodes - and whether the real base / st0 hold nodes with the same class whose uids are absent from the
s04 session's own start state (uids(st0 s05) - uids(st0 s04) = nodes s04 made, measured from two graph reads).
PREDICTION CONTRACT: none (a census).
  py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c146_a2_1_probe4.log -- py -u tools/bench/diag_c146_a2_1_probe4.py"""
import collections, json, os, sys                                                           # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
p5 = J("tools/bench/plan_ring_p4_s05v18.json")
print("CONTEXT {0}".format(json.dumps(p5.get("context"))[:1200]), flush=True)
print("PLAN base {0}".format(json.dumps(p5.get("base"))[:600]), flush=True)
b5 = J(p5["finalized"]["base"]["path"])
prov = (b5.get("fs_carried") or {}).get("provisional") or {}
try:
    pv = J(prov["path"])
    pvs = pv.get("state", pv)
    print("PROV keys {0}; sym {1}".format(sorted(pvs.keys())[:25], json.dumps(pvs.get("sym"))[:800]), flush=True)
    negown = sorted(set(int(r["owner_uid"]) for r in pvs.get("terminals") or [] if int(r["owner_uid"]) < 0))
    print("PROV negative owners {0}".format(negown), flush=True)
except Exception as e:                                                                       # noqa: BLE001
    print("PROV unreadable {0}".format(e), flush=True)
own = lambda st: dict((int(r["owner_uid"]), r.get("owner_class")) for r in st.get("terminals") or [])  # noqa: E731
st05 = J(p5["finalized"]["step_files"][0]["path"])["state"]
p4 = J("tools/bench/plan_ring_p4_s04v18.json")
st04 = J(p4["finalized"]["step_files"][0]["path"])["state"]
o5, o4 = own(st05), own(st04)
new = sorted((u, o5[u]) for u in o5 if u not in o4)
print("S04-MADE (uids in s05 start, not in s04 start) n {0}: {1}".format(len(new), new), flush=True)
p3 = J("tools/bench/plan_ring_p4_s03v18.json")
st03 = J(p3["finalized"]["step_files"][0]["path"])["state"]
o3 = own(st03)
print("S03-MADE (uids in s04 start, not in s03 start) n {0}: {1}".format(len([u for u in o4 if u not in o3]), sorted((u, o4[u]) for u in o4 if u not in o3)), flush=True)
print(protocol.result_line(protocol.make_result(0, 0, None, [])), flush=True)
