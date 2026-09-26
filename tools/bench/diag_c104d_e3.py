"""card 104-4 (OFFLINE, no LabVIEW): the E3 added-object check on the Part-B dry end - which added computation nodes are not
bound plan-created objects, and what their terminal rows / objs entries say (owner, diagram). Prediction: the 2 unbound
DiagramTerminals (23090, 23447) belong to the created loops (their loop-condition / iteration terminals)."""
import json
import os
import sys
T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, T)
os.chdir(os.path.dirname(T))
import vigraph as V  # noqa: E402
import stagexec as SX  # noqa: E402
import protocol  # noqa: E402
B = os.path.join(T, "bench")
rp, rb = os.path.join(B, "sim/disp/plan_disp.json"), os.path.join(B, "stage_d1_dispA.json")
P = json.load(open(rp, encoding="utf-8"))
k = int(json.load(open(rb, encoding="utf-8"))["partA"]["stop_after"])
st, ff, ex = SX.dry_run(rp, log=lambda *_a: None, from_step=k, binding=rb)
objs, real = ex.be.st["objs"], ex.be.read()
r = SX.e3_check(P, ex, objs, real, SX.e3_wiki(P), "diag")
print("dry", st, "E3", SX.e3_line(r), flush=True)
print("bad_added", r["bad_added"], flush=True)
print("bind obj", ex.bind["obj"], flush=True)
print("bind diag", ex.bind["diag"], flush=True)
print("bind term (sim<0)", dict((a, b) for a, b in ex.bind["term"].items() if int(a) < 0), flush=True)
L57 = ex.step(len(P["actions"]))["state"]["loops"]
print("step57 loops (created)", json.dumps([L for L in L57 if any(int(v) < 0 for v in L.values() if isinstance(v, int))], default=str)[:1500], flush=True)
for n, c in r["added"]:
    rows = [x for x in real if V.node_of(x) == n]
    print("ADDED", n, c, "rows", json.dumps(rows, default=str)[:700], flush=True)
    ob = [o for o in (objs if isinstance(objs, list) else objs.values() if isinstance(objs, dict) else []) if isinstance(o, dict) and n in (o.get("uid"), o.get("owner_uid"))]
    print("   objs", json.dumps(ob, default=str)[:500], flush=True)
print("objs type", type(objs).__name__, (list(objs.items())[:2] if isinstance(objs, dict) else objs[:2]), flush=True)
ok = st == "PASS"
print(protocol.result_line(protocol.make_result(int(ok), int(not ok), None if ok else ff)))
