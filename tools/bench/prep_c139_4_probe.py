r"""prep_c139_4_probe - card 139-4, read-only offline probe (no LabVIEW): the graph rows / plan actions the v12 edits touch.
Reads graph_ring_p3b2b_20261002_133824.json + plan_ring_p4_v11.json + the measured analog plans; writes nothing.
PREDICTION: rows for t23246 / #10170 / t642 exist; v11 holds p4_w_stop12, p4_t_last(+in/out), p4_sr_last."""
import json, os, sys, glob                                                                   # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
G = json.load(open(os.path.join(B, "graph_ring_p3b2b_20261002_133824.json"), encoding="utf-8"))
print("graph keys", list(G.keys()))
T = G["terminals"]
print("row keys", list(T[0].keys()))
for r in T:
    if int(r["term_uid"]) in (23246, 642) or int(r.get("owner_uid") or 0) == 10170:
        print("ROW", r)
for k in ("loops", "objs", "objects"):
    v = G.get(k)
    if isinstance(v, dict):
        for kk, vv in v.items():
            if str(kk) in ("10170", "23166"):
                print(k.upper(), kk, json.dumps(vv)[:900])
    elif isinstance(v, list):
        for vv in v:
            s = json.dumps(vv)
            if '"uid": 10170' in s[:200] or '"uid": 23166' in s[:200]:
                print(k.upper(), s[:900])
P = json.load(open(os.path.join(B, "plan_ring_p4_v11.json"), encoding="utf-8"))
A = P["actions"]
for n, a in enumerate(A, 1):
    if a["id"] in ("p4_sr_last", "p4_k_last", "p4_w_klast", "p4_w1", "p4_gt_last", "p4_w_stop12", "p4_lr_stop12", "p4_t_n1", "p4_t_n1_in",
                   "p4_t_n1_out", "p4_t_slot", "p4_t_slot_in", "p4_t_slot_out", "p4_t_pool", "p4_x_pool", "p4_w_pool_in", "p4_w_or_cond"):
        print("ACT", n, json.dumps({k: v for k, v in a.items() if k != "why"}))
print("finalized keys", list((P.get("finalized") or {}).keys()))
print("route_check", json.dumps((P["finalized"].get("route_check") or {}).get("status")))
M = json.load(open(os.path.join(B, "plan_ring_p4_v3_meta.json"), encoding="utf-8"))
print("META keys", list(M.keys()) if isinstance(M, dict) else type(M))
print("META head", json.dumps(M)[:1500])
for f in sorted(glob.glob(os.path.join(B, "plan_ring_p4s*"))) + sorted(glob.glob(os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p4*"))):
    print("EXISTS", f)
print(protocol.result_line(protocol.make_result(1, 0, None, [])), flush=True)
