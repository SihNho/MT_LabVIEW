"""card 114-3 C4 self-test of stage_prerun X12 (recreated_wire_refs). Offline, no LabVIEW.
Prediction contract: T1-T6 synthetic as labelled; R1 plan_l2b3.json re-creates exactly {28392, 5174, 5336} and flags
nothing (each wire named once); R2 plan_l2b3.json + a delete_wire 5174 row appended is FLAGGED (recreated_by b3_t2_out);
R3 the same row placed BEFORE the group is not flagged; R4 every top-level tools/bench stageplan/1: listed, and none
flagged; S1 prerun() carries gate X12 (source check). Ends with a RESULT line."""
import copy
import glob
import inspect
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import stage_prerun as SP  # noqa: E402
import protocol as P  # noqa: E402

gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:400]), flush=True)


def T(name, is_src, tu, w, owner):
    return {"term_uid": tu, "term_name": name, "is_source": is_src, "wire_uid": w, "owner_uid": owner}


# toy base: SubVI #1 'out' on w50 (sink #2 'in'); SubVI #3 'q' unwired; SubVI #4 'x' sink unwired
BASE = ({1: "SubVI", 2: "SubVI", 3: "SubVI", 4: "SubVI"},
        {1: [T("out", True, 11, 50, 1)], 2: [T("in", False, 21, 50, 2)], 3: [T("q", True, 31, 0, 3)],
         4: [T("x", False, 41, 0, 4)]})
GROUP = [{"op": "tunnel", "id": "t", "loop": 9, "body": 8, "dir": "in", "as": "T1"},
         {"op": "wire", "id": "t_out", "src": {"uid": 1, "term_uid": 11}, "dst": "new:T1.outer"},
         {"op": "wire", "id": "t_in", "src": "new:T1.inner", "dst": {"uid": 4, "term_uid": 41}}]
DEL50 = {"op": "delete_wire", "id": "del50", "wire_uid": 50}


def run(actions):
    return SP.recreated_wire_refs({"actions": actions}, base=BASE)


r, f = run(GROUP + [DEL50])
gate("T1 group from wired #1.out (w50), then delete_wire 50 -> FLAG row del50 (recreated_by t_out)",
     [x["wire"] for x in r] == [50] and [(x["row"], x["wire"], x["recreated_by"]) for x in f] == [("del50", 50, "t_out")], (r, f))
r, f = run([DEL50] + GROUP)
gate("T2 the same delete_wire BEFORE the group -> clean", [x["wire"] for x in r] == [50] and f == [], (r, f))
r, f = run(GROUP)
gate("T3 group alone -> 1 re-created (w50), no flag", [x["wire"] for x in r] == [50] and f == [], (r, f))
g4 = copy.deepcopy(GROUP)
g4[1]["src"] = {"uid": 3, "term_uid": 31}
r, f = run(g4 + [dict(DEL50)])
gate("T4 group from an UNWIRED source (#3.q) -> nothing re-created, a later w50 row clean", r == [] and f == [], (r, f))
r, f = run([{"op": "wire", "id": "same", "src": {"uid": 1, "term_uid": 11}, "dst": {"uid": 4, "term_uid": 41}}, DEL50])
gate("T5 SAME-DIAGRAM connect from wired #1.out (no plan tunnel) then w50 row -> clean (uid kept, l7_1b_r3.log:92)",
     r == [] and f == [], (r, f))
g6 = copy.deepcopy(GROUP)
g6[1]["src"] = "1.out"
r, f = run(g6 + [{"op": "delete_object", "id": "delo", "uid": 50, "pos": [0, 0]}])
gate("T6 string address '1.out' + a later row naming 50 in ANY uid field -> FLAG", [x["row"] for x in f] == ["delo"], (r, f))
r, f = run(GROUP + [{"op": "move_in", "id": "mv", "nodes": [2], "dest_diagram": 8, "pos": [50, 50]}])
gate("T7 a later row whose only 50 is a POSITION -> clean", f == [], (r, f))

L = json.load(open(os.path.join(HERE, "plan_l2b3.json"), encoding="utf-8"))
r, f = SP.recreated_wire_refs(L)
gate("R1 plan_l2b3.json (md5 {0}): re-created == {{28392, 5174, 5336}} by b3_t1_out/b3_t2_out/b3_t3_out, no flag".format(
    SP.md5(os.path.join(HERE, "plan_l2b3.json"))),
     sorted((x["wire"], x["row"]) for x in r) == [(5174, "b3_t2_out"), (5336, "b3_t3_out"), (28392, "b3_t1_out")] and f == [],
     (r, f))
L2 = copy.deepcopy(L)
L2["actions"].append({"op": "delete_wire", "id": "late5174", "wire_uid": 5174})
r, f = SP.recreated_wire_refs(L2)
gate("R2 plan_l2b3 + a later delete_wire 5174 -> FLAGGED (recreated_by b3_t2_out)",
     [(x["row"], x["wire"], x["recreated_by"]) for x in f] == [("late5174", 5174, "b3_t2_out")], f)
L3 = copy.deepcopy(L)
L3["actions"].insert(0, {"op": "delete_wire", "id": "early5174", "wire_uid": 5174})
r, f = SP.recreated_wire_refs(L3)
gate("R3 plan_l2b3 with the same row FIRST -> clean", f == [], f)
listed, hits = [], []
for p in sorted(glob.glob(os.path.join(HERE, "*.json"))):
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:  # noqa: BLE001
        continue
    if not isinstance(d, dict) or d.get("schema") != "stageplan/1":
        continue
    r, f = SP.recreated_wire_refs(d)
    listed.append((os.path.basename(p), len(r)))
    hits += [(os.path.basename(p), x["row"], x["wire"]) for x in f]
print("  INFO top-level stageplans with re-created source wires: {0}".format([x for x in listed if x[1]]), flush=True)
gate("R4 every top-level tools/bench/*.json stageplan/1 ({0} files) flags nothing".format(len(listed)), not hits, hits[:10])
src = inspect.getsource(SP.prerun)
gate("S1 prerun() runs recreated_wire_refs as gate X12", "recreated_wire_refs(" in src and '"X12 ' in src,
     "X12" in src)
npass = sum(1 for g in gates if g[1])
first = next((g[0] for g in gates if not g[1]), None)
print(P.result_line(P.make_result(npass, len(gates) - npass, first, status="PASS" if npass == len(gates) else "FAIL")))
