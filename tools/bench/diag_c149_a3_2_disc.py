# ---
# labview: none
# hardware: none
# ---
r"""diag_c149_a3_2_disc - card 149-a3-2 step 1 (OFFLINE, pure Python, no LabVIEW): the peer's discriminating test
(archive/peer/2026-10-08-c149-a3-1-mkgraph.md sec. 4) on the scratch json of P4 session 6 (tools/bench/diag_c147_p4s06v18_scratch.json).
WHAT EXISTS: the scratch json already holds term_identity.new / d_new / reuse_noted and real_end_rows ([term, owner, name, wire, is_source],
the scratch's real terminal table of the saved session-6 file); E5 is diag_c149_a3_1_graph.py:63-64 (wset = wire uids of the terminal rows).
(a) set(new) | {kept_by_key reuse_noted wires} has 16 members == d_new 16 (the D line, diag_c147_p4s06v18_scratch.log:1002);
(b) real_end_rows hold w23807 with source {(5171,5058)} and sinks {(3173,23166),(10975,10969)};
(c) E5's expression on wset = real_end_rows wire uids, run with the plan as written (diag_c149_a3_1_graph_plan.json: deleted [23807], 15 new)
    and with 23807 moved deleted -> new. PREDICTION: (a) PASS, (b) PASS, (c) as-written FAILS (23807 present), moved PASSES.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c149_a3_2_disc.log -- py -u tools/bench/diag_c149_a3_2_disc.py"""
import json, os, sys                                                                          # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
scr = json.load(open(os.path.join(B, "diag_c147_p4s06v18_scratch.json"), encoding="utf-8"))
pl = json.load(open(os.path.join(B, "diag_c149_a3_1_graph_plan.json"), encoding="utf-8"))
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)
    return ok


ti = scr["term_identity"]
new = set(int(w) for w in ti["new"])
kept = set(int(n["wire"]) for n in ti["reuse_noted"] if n.get("kept_by_key"))
u = new | kept
gate("a set(new)|{kept_by_key} has 16 members == d_new", len(u) == 16 == ti["d_new"],
     {"new": len(new), "kept": sorted(kept), "union": len(u), "d_new": ti["d_new"]})
rows = scr["real_end_rows"]
on = [r for r in rows if int(r[3] or 0) == 23807]
src = set((int(r[0]), int(r[1])) for r in on if r[4])
snk = set((int(r[0]), int(r[1])) for r in on if not r[4])
gate("b real_end_rows: w23807 source {(5171,5058)}, sinks {(3173,23166),(10975,10969)}",
     src == {(5171, 5058)} and snk == {(3173, 23166), (10975, 10969)}, {"rows": on})
wset = set(int(r[3]) for r in rows if r[3])
print("FACT real_end_rows {0} rows, {1} distinct wire uids".format(len(rows), len(wset)), flush=True)


def e5(ed):   # diag_c149_a3_1_graph.py:63-64, the deleted/new wire part (made/deleted_nodes need the LabVIEW object table)
    return {"deleted_wires_present": [w for w in ed["deleted_wires"] if w in wset],
            "new_wires_missing": [w for w in ed["new_wires"] if w not in wset]}


ed1 = {"deleted_wires": list(pl["edits"]["deleted_wires"]), "new_wires": list(pl["edits"]["new_wires"])}
ed2 = {"deleted_wires": [w for w in ed1["deleted_wires"] if w != 23807], "new_wires": sorted(set(ed1["new_wires"]) | {23807})}
r1, r2 = e5(ed1), e5(ed2)
ok1 = not r1["deleted_wires_present"] and not r1["new_wires_missing"]
ok2 = not r2["deleted_wires_present"] and not r2["new_wires_missing"]
print("FACT c1 plan as written (deleted {0}, {1} new): E5 {2} -> {3}".format(ed1["deleted_wires"], len(ed1["new_wires"]), r1,
                                                                           "PASS" if ok1 else "FAIL"), flush=True)
print("FACT c2 23807 moved deleted->new (deleted {0}, {1} new): E5 {2} -> {3}".format(ed2["deleted_wires"], len(ed2["new_wires"]), r2,
                                                                                    "PASS" if ok2 else "FAIL"), flush=True)
gate("c1 E5 on the plan as written FAILS (predicted: 23807 present)", not ok1, r1)
gate("c2 E5 with 23807 moved deleted -> new PASSES", ok2, r2)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
