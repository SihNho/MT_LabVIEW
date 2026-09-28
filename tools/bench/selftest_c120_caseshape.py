"""card 120-3: READ-ONLY measurement of the shape of existing Case structures in a graph JSON (selector 'Tunnel' and data
SelectorTunnel rows per frame, owners of the frame diagrams) - the source of stagesim's case model. No LabVIEW.
Usage: py tools/bench/selftest_c120_caseshape.py <graph.json>"""
import atexit
import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import protocol  # noqa: E402
atexit.register(lambda: print(protocol.result_line(protocol.make_result(1, 0, None, [])), flush=True))
p = sys.argv[1]
g = json.load(open(p, encoding="utf-8"))
print(list(g.keys()))
own = g.get("owners") or {}
print("owners n", len(own), list(own.items())[:3])
cs = [o for o in g["objs"] if o["class"] == "CaseStructure"]
print("n cases", len(cs), cs[:2])
done = 0
for c in cs:
    u = int(c["uid"])
    frames = [k for k, v in own.items() if int(v[1] or 0) == u]
    rows = [r for r in g["terminals"] if r["owner_class"] in ("Tunnel", "SelectorTunnel") and str(r["frame_diagram"]) in frames]
    owners = sorted(set(r["owner_uid"] for r in rows))
    if not owners:
        continue
    print("case", u, "frames", frames, [own[k] for k in frames])
    for ou in owners[:5]:
        rr = [r for r in g["terminals"] if r["owner_uid"] == ou]
        print("  tun", ou, [(r["owner_class"], r["term_class"], r["is_source"], r["frame_diagram"], r["term_name"], r["wire_uid"]) for r in rr])
    ob = [o for o in g["objs"] if int(o["uid"]) in owners]
    print("  objs", ob[:5])
    done += 1
    if done >= 3:
        break
