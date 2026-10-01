r"""diag_c132_5_frames - card 132-5: RECORD how the P3b-2 plan's created frame diagrams (-2, -3, -4) appear in the provisional
base and which Diagram objects are new in the real P3b-1 graph (vs P3a). Offline, read only.
PREDICTION: F1 three new real Diagram objects; F2 -2/-3/-4 appear in the provisional base's objs (or fs structures).
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c132_5_frames.log -- py -u tools/bench/diag_c132_5_frames.py"""
import json, os, sys                                                                # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.dirname(B))
import protocol as P                                                                # noqa: E402
J = lambda p: json.load(open(os.path.join(R, p), encoding="utf-8"))               # noqa: E731
plan = J("tools/bench/plan_ring_p3b2.json")
pv = J(plan["base"]["path"])
bf = J("tools/bench/graph_ring_p3a_20261001_190155.json")
rl = J("tools/bench/graph_ring_p3b1_20261002_073225.json")
for nm, d in (("PROV", pv), ("BEFORE", bf), ("REAL", rl)):
    print("  FACT  {0} keys {1}".format(nm, sorted(d.keys())), flush=True)
    for k, v in d.items():
        if isinstance(v, list) and v and isinstance(v[0], dict):
            print("  FACT  {0}.{1}[0] = {2}".format(nm, k, json.dumps(v[0])[:300]), flush=True)


def hits(d, uids, path="", out=None, depth=0):
    out = [] if out is None else out
    if depth > 6:
        return out
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, int) and not isinstance(v, bool) and v in uids and k != "term_uid":
                out.append((path + "." + k, json.dumps(d)[:260]))
            else:
                hits(v, uids, path + "." + k, out, depth + 1)
    elif isinstance(d, list):
        for i, v in enumerate(d):
            if isinstance(v, int) and not isinstance(v, bool) and v in uids:
                out.append((path + "[]", json.dumps(d)[:260]))
            else:
                hits(v, uids, path + "[]", out, depth + 1)
    return out


seen = set()
for p, s in hits({k: v for k, v in pv.items() if k != "terminals"}, {-2, -3, -4}):
    if (p, s) not in seen:
        seen.add((p, s))
        print("  FACT  PROV ref {0}: {1}".format(p, s), flush=True)
fr = [r for r in pv.get("terminals") or [] if r.get("frame_diagram") in (-2, -3, -4)]
print("  FACT  PROV terminal rows per frame: {0}".format(dict((f, sum(1 for r in fr if r["frame_diagram"] == f)) for f in (-2, -3, -4))), flush=True)
ob = set(o.get("uid") for o in bf.get("objs") or [] if isinstance(o, dict))
newd = [o for o in rl.get("objs") or [] if isinstance(o, dict) and o.get("uid") not in ob and "Diagram" in str(o.get("class", o.get("cls", "")))]
for o in newd:
    print("  FACT  REAL new diagram obj {0}".format(json.dumps(o)[:300]), flush=True)
for p, s in hits({k: v for k, v in rl.items() if k not in ("terminals", "objs")}, set(o.get("uid") for o in newd)):
    if (p, s) not in seen:
        seen.add((p, s))
        print("  FACT  REAL ref {0}: {1}".format(p, s), flush=True)
ok = len(newd) == 3
print("{0}  F1 three new real Diagram objects  {1}".format("PASS" if ok else "FAIL", [o.get("uid") for o in newd]), flush=True)
print(P.result_line(P.make_result(int(ok), int(not ok), None if ok else "F1")), flush=True)
sys.stdout.flush()
os._exit(0 if ok else 1)
