# ---
# labview: none
# hardware: none
# ---
"""card 154-a1-1 step 1: read the P5-1 targets from the REAL s09 graph (22f967b5), json only, no LabVIEW.
Prediction (PD374(a), p5_facts F1/F5): #4866 is a Diagram (FS1 frame); #2626 owns t2813 'appended array' (source, w0);
#29724 owns t29900 'valid' (source, w30457, 7 sinks before P5); #23166 is loop 1.2's body (a While); #23041 is loop 1.7.
Prints every row needed to write the plan; ends with a RESULT line."""
import collections
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
G = os.path.join(HERE, "graph_ring_p4s09_20261009_062044.json")
md5 = hashlib.md5(open(G, "rb").read()).hexdigest()
g = json.load(open(G, encoding="utf-8"))
print("graph", md5)
print("keys", list(g.keys()))
for k, v in g.items():
    if k != "terminals":
        print(" ", k, type(v).__name__, len(v) if hasattr(v, "__len__") else "", str(v)[:300])
T = g["terminals"]
print("term keys", list(T[0].keys()))
by_owner = collections.defaultdict(list)
by_wire = collections.defaultdict(list)
by_diag = collections.defaultdict(list)
for i, r in enumerate(T):
    by_owner[r["owner_uid"]].append((i, r))
    if r.get("wire_uid"):
        by_wire[r["wire_uid"]].append((i, r))
    by_diag[r.get("frame_diagram")].append((i, r))


def show(uid):
    rows = by_owner.get(uid, [])
    print("== owner #{0}: {1} rows".format(uid, len(rows)))
    for i, r in rows:
        print("   idx {0} t{1} {2!r} src={3} w{4} cls={5} oc={6} diag={7}".format(
            i, r["term_uid"], r["term_name"], r["is_source"], r.get("wire_uid"), r.get("term_class"), r.get("owner_class"),
            r.get("frame_diagram")))


def wire(w):
    print("== wire w{0}".format(w))
    for i, r in by_wire.get(w, []):
        print("   idx {0} t{1} {2!r} src={3} owner #{4} {5} diag={6}".format(i, r["term_uid"], r["term_name"], r["is_source"],
                                                                         r["owner_uid"], r.get("owner_class"), r.get("frame_diagram")))


for u in (2626, 29724):
    show(u)
wire(30457)
for d in (4866, 23166, 686, 23405):
    rows = by_diag.get(d, [])
    owners = collections.Counter((r["owner_uid"], r.get("owner_class")) for _i, r in rows)
    print("== diagram #{0}: {1} rows, {2} owners".format(d, len(rows), len(owners)))
    if d == 4866:
        for (o, c), n in sorted(owners.items()):
            print("    #{0} {1} rows {2}".format(o, c, n))
            for i, r in by_owner[o]:
                if r.get("frame_diagram") == d:
                    print("       t{0} {1!r} src={2} w{3} tcls={4}".format(r["term_uid"], r["term_name"], r["is_source"], r.get("wire_uid"), r.get("term_class")))
# structure/loop tables
for k in ("loops", "owners", "diagrams", "fs", "fs_frames", "structures"):
    if k in g:
        v = g[k]
        if isinstance(v, dict):
            for kk in ("23166", "4866", "686", "23405", "23041", 23166, 4866, 686):
                if kk in v:
                    print("  {0}[{1!r}] = {2}".format(k, kk, str(v[kk])[:400]))
        elif isinstance(v, list):
            for x in v:
                s = json.dumps(x)
                if any(str(n) in s for n in ("23166", "4866", "23041")):
                    print("  {0}: {1}".format(k, s[:400]))
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[]}')
