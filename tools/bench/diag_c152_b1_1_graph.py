# ---
# labview: none
# hardware: none
# offline-args: (none)
# evidence: tools/bench/graph_ring_p4s08_20261009_033522.json
# ---
r"""diag_c152_b1_1_graph - card 152-b1-1 STEP 2 (PD369(d)): OFFLINE read of graph_ring_p4s08_20261009_033522.json (44858dbf, read
only): (a) owner class/uid of LoopTunnel #30179; (b) the inner source feeding its loop-side face; (c) the other sink on w30166;
(d) #29879/#30002/#30016 on frame #29869 of FS #29721 on #23166, FS border tunnels. Prints every row touching those uids.
    py tools/bench/diag_c152_b1_1_graph.py > tools/bench/diag_c152_b1_1_graph.log"""
import hashlib, json, os, sys                                                                # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "graph_ring_p4s08_20261009_033522.json")
print("GRAPH md5", hashlib.md5(open(P, "rb").read()).hexdigest())
D = json.load(open(P, encoding="utf-8"))
print("TOP", type(D).__name__, sorted(D.keys()) if isinstance(D, dict) else len(D))
if isinstance(D, dict):
    for k, v in D.items():
        print("KEY", k, type(v).__name__, len(v) if hasattr(v, "__len__") else v,
              (json.dumps(v[0], default=str)[:300] if isinstance(v, list) and v else ""))
U = set(int(x) for x in (sys.argv[1:] or "30179 30192 30166 29879 30002 30016 29869 29721 23166".split()))
def walk(o, path):
    if isinstance(o, dict):
        vals = set()
        for v in o.values():
            if isinstance(v, (int, str)) and str(v).lstrip("-").isdigit():
                vals.add(int(v))
        if vals & U and not any(isinstance(v, (dict, list)) and len(v) > 50 for v in o.values()):
            print("ROW", path, json.dumps(o, default=str)[:600])
        for k, v in o.items():
            walk(v, path + "/" + str(k)[:20])
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, path + "[%d]" % i if len(path) < 60 else path)
walk(D, "")
for u in sorted(U):
    print("OWNER", u, "->", (D.get("owners") or {}).get(str(u)), "| loops", [l for l in D.get("loops") or [] if l.get("loop_uid") == u])
sys.path.insert(0, os.path.dirname(HERE))
import protocol as PR                                                                        # noqa: E402
ok = D.get("md5") is not None and hashlib.md5(open(P, "rb").read()).hexdigest().startswith("44858dbf")
print(PR.result_line(PR.make_result(int(ok), int(not ok), None if ok else "graph md5 != 44858dbf", [])), flush=True)
