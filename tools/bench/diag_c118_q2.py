r"""diag_c118_q2 - card 118-3 (offline, no LabVIEW): the R2 graph rows of #13938 (IMAQ Create), its name constant #23583 and ring #13245,
plus the frame diagram 13236's parent - the terminal NAMES a constant's output row carries (for the wire rows of diag_c118_p1b).
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c118_q2.log -- py -u tools/bench/diag_c118_q2.py"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import protocol as P  # noqa: E402
B = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(B, "graph_l2r2_saved_20260928.json"), encoding="utf-8"))
print("keys", sorted(G))
for r in G["terminals"]:
    if int(r["owner_uid"]) in (23583, 13245, 13938):
        print("ROW", json.dumps(r))
print("OBJS", [o for o in G.get("objs", []) if int(o.get("uid", 0)) in (23583, 13245, 13938)])
print("OWNER of 13236:", (G.get("owners") or {}).get("13236"), "| parent:", (G.get("diagrams") or {}).get("13236"))
print("fs_tunnel_pairs n", len(G.get("fs_tunnel_pairs", [])))
print(P.result_line(P.make_result(1, 0, None)))
