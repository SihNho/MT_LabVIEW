r"""diag_c100_6_owners - card 100-6, archive/peer/2026-09-26-c100-6-jevgate2.md section 4 (offline, no LabVIEW): is D1_k's
owners map (sim/l2a1/graph_k_80_owners.json, used as plan_disp's context.owners stand-in) consistent with S1
(par1359_95_graph.json)? Per owners key k -> [cls, u]: k exists in S1 objs; u's class in S1 == cls; and S1's recorded
`owner` class name for k (objs[].owner) == cls. Reported for ALL keys and for the TOUCHED set (uids named in plan_disp.json's
actions + the structures on 639/686/7911 from diag_c100_6_parity's rebuilt real listing). Gate: 0 mismatches in the touched set.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c100_6_owners.log -- py -u tools/bench/diag_c100_6_owners.py"""
import json, os, sys                                                               # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P      # noqa: E402

J = lambda p: json.load(open(os.path.join(ROOT, p), encoding="utf-8"))            # noqa: E731
own = J("tools/bench/sim/l2a1/graph_k_80_owners.json")["owners"]
s1 = J("tools/bench/par1359_95_graph.json")
plan = J("tools/bench/sim/disp/plan_disp.json")
par = J("tools/bench/stage_d1_disp.json")["stagexec"][0]["parity"]
C = dict((int(o["uid"]), o) for o in s1["objs"])
TU = set()


def walk(v):
    if isinstance(v, dict):
        for k, x in v.items():
            if k in ("uid", "nodes", "loop", "diagram", "dest_diagram", "parent", "body") or k == "donor_uid":
                walk_ints(x)
            else:
                walk(x)
    elif isinstance(v, list):
        for x in v:
            walk(x)


def walk_ints(x):
    if isinstance(x, bool):
        return
    if isinstance(x, int):
        TU.add(x)
    elif isinstance(x, list):
        for y in x:
            walk_ints(y)
    elif isinstance(x, dict):
        walk(x)


walk(plan["actions"])
for row in par["rows"]:
    TU |= set(int(u) for _c, u in row["only_real"])
TU |= set(int(r["diagram"]) for r in par["rows"])
bad_all, bad_t = [], []
for k, (cls, u) in own.items():
    k, u = int(k), int(u or 0)
    why = []
    if k not in C:
        why.append("key not in S1 objs")
    if u and u in C and C[u]["class"] != cls:
        why.append("owner #{0} is {1} in S1".format(u, C[u]["class"]))
    if u and u not in C and cls != "?":
        why.append("owner #{0} not in S1 objs".format(u))
    if k in C and C[k].get("owner") not in (None, cls):
        why.append("S1 records owner class {0!r}".format(C[k].get("owner")))
    if why:
        bad_all.append((k, cls, u, why))
        if k in TU or u in TU:
            bad_t.append((k, cls, u, why))
print("  FACT owners keys {0}; mismatches all {1}; touched set {2} uids; mismatches touched {3}".format(
    len(own), len(bad_all), len(TU), len(bad_t)), flush=True)
for b in bad_t[:40]:
    print("  TOUCHED MISMATCH {0}".format(b), flush=True)
for b in bad_all[:15]:
    print("  ANY MISMATCH {0}".format(b), flush=True)
ok = not bad_t
print("  {0}  O1 0 owners mismatches in the touched set".format("PASS" if ok else "FAIL"), flush=True)
print(P.result_line(P.make_result(int(ok), int(not ok), None if ok else "O1 touched-set owners mismatches {0}".format(len(bad_t)))), flush=True)
sys.exit(0 if ok else 1)
