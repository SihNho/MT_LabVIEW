r"""diag_c132_1_fp21 - card 132-1 (gate-fp fp-21): why does `stage_prerun --dry` on stage_d1_ring_p3b2.py read the P3a graph
instead of the provisional base? Prints plan_base_graphs, each candidate's header md5 / file md5 / pin / graph_shape_error, the
find_graph pick and FIND_SKIPPED, and the plan's base / sim_of. Offline, read-only."""
import json, os, re, sys                                                             # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stage_prerun as SP                                                            # noqa: E402
R = os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p3b2.py")
pl = json.load(open(os.path.join(B, "plan_ring_p3b2.json"), encoding="utf-8"))
print("PLAN base", json.dumps(pl.get("base"))[:600])
print("PLAN finalized.base", pl["finalized"]["base"])
for p, pin in SP.plan_base_graphs(R):
    head = open(p, encoding="utf-8", errors="replace").read(800)
    m = re.search(r'"md5"\s*:\s*"([0-9a-f]{32})"', head)
    try:
        why = SP.graph_shape_error(json.load(open(p, encoding="utf-8")))
    except Exception as e:                                                           # noqa: BLE001
        why = "ERR {0}".format(e)
    print("CAND", SP.rel(p), "header", m and m.group(1), "file", SP.md5(p), "pin", pin, "shape_error", why)
g = json.load(open(os.path.join(ROOT, pl["finalized"]["base"]["path"]), encoding="utf-8"))
print("PROV keys", sorted(g)[:30], "md5", g.get("md5"), "vi", g.get("vi"))
print("PICK", SP.find_graph(g.get("md5"), SP.plan_base_graphs(R)), "SKIPPED", SP.FIND_SKIPPED)
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":0,"fail":0},"first_fail":null,"artefacts":[]}')
