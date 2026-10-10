# ---
# labview: none
# hardware: none
# offline-args: copy
# evidence: tools/bench/cards/task_165-1-1.json
# ---
"""Card 165-1-1 step 6 helper (no LabVIEW). `copy`: keep the 9dadb0c1 bytes of tools/bench/plan_ring_p5s02r_in.json under
%TEMP%\\c165_a1_1\\ (never overwritten). `compare`: JSON-compare the edited file against those bytes.

Prediction contract (compare): old md5 9dadb0c1...; the new action list == the old one with EXACTLY two actions added -
{op delete_wire, id dw_10362, wire_uid 10362} immediately before w_k3f (A70) and {op delete_wire, id dw_25232, wire_uid
25232} immediately before w_k4f (A80); every other top-level key and every other action byte-equal as JSON; both new rows
have the same key set as the existing delete_wire rows dw_cond / dw_23460. Existing tools: protocol.validate_obj (stageplan/1)."""
import hashlib
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402

P = os.path.join(HERE, "plan_ring_p5s02r_in.json")
OLD = os.path.join(tempfile.gettempdir(), "c165_a1_1", "plan_ring_p5s02r_in_9dadb0c1.json")
G = [0, 0, None]


def gate(lab, ok, d=""):
    G[0 if ok else 1] += 1
    if not ok and G[2] is None:
        G[2] = lab
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", lab, str(d)[:600]), flush=True)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


mode = sys.argv[1] if len(sys.argv) > 1 else "compare"
if mode == "copy":
    os.makedirs(os.path.dirname(OLD), exist_ok=True)
    if not os.path.isfile(OLD):
        open(OLD, "wb").write(open(P, "rb").read())
    gate("C1 kept copy md5 9dadb0c1 == file", md5(OLD).startswith("9dadb0c1") and md5(OLD) == md5(P), (md5(OLD), md5(P)))
else:
    o, n = json.load(open(OLD, encoding="utf-8")), json.load(open(P, encoding="utf-8"))
    print("FACT old {0} {1} actions; new {2} {3} actions".format(md5(OLD), len(o["actions"]), md5(P), len(n["actions"])), flush=True)
    gate("J0 old copy md5 9dadb0c1", md5(OLD).startswith("9dadb0c1"), md5(OLD))
    gate("J1 top-level keys other than actions equal", dict((k, v) for k, v in o.items() if k != "actions") ==
         dict((k, v) for k, v in n.items() if k != "actions"), sorted(set(o) ^ set(n)))
    ids = [a.get("id") for a in n["actions"]]
    added = [a for a in n["actions"] if a not in o["actions"]]
    rest = [a for a in n["actions"] if a.get("id") not in ("dw_10362", "dw_25232")]
    gate("J2 exactly 2 added actions, the rest byte-equal as JSON and in order", len(n["actions"]) == len(o["actions"]) + 2 and
         json.dumps(rest, sort_keys=True) == json.dumps(o["actions"], sort_keys=True), [a.get("id") for a in added])
    want = [("dw_10362", 10362, "w_k3f"), ("dw_25232", 25232, "w_k4f")]
    for rid, w, nxt in want:
        i = ids.index(rid) if rid in ids else None
        a = n["actions"][i] if i is not None else {}
        gate("J3 {0}: op delete_wire wire_uid {1}, immediately before {2} (A{3} -> new index {4})".format(
            rid, w, nxt, (ids.index(nxt) if nxt in ids else -1), i),
             i is not None and a.get("op") == "delete_wire" and a.get("wire_uid") == w and ids[i + 1] == nxt, a)
    shape = set(next(a for a in o["actions"] if a.get("id") == "dw_cond"))
    gate("J4 the new rows have the dw_cond / dw_23460 key set {0}".format(sorted(shape)),
         all(set(a) == shape for a in added) and set(next(a for a in o["actions"] if a.get("id") == "dw_23460")) == shape,
         [sorted(a) for a in added])
    ok, why = protocol.validate_obj(n)
    gate("J5 new plan validates (stageplan/1)", ok, why)
    print("FACT A70/A80 in the OLD numbering: w_k3f = action {0}, w_k4f = action {1} (1-based)".format(
        [a.get("id") for a in o["actions"]].index("w_k3f") + 1, [a.get("id") for a in o["actions"]].index("w_k4f") + 1), flush=True)
print(protocol.result_line(protocol.make_result(G[0], G[1], G[2], [{"path": os.path.relpath(P, ROOT), "md5": md5(P)}])), flush=True)
sys.exit(1 if G[1] else 0)
