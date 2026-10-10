# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_164-3-1.md
# ---
r"""prep_c164_a3_1_cmp - card 164-3-1 part 3 (OFFLINE, read-only): plan_ring_p5s02r_in.json (edited) vs the aside copy plan_ring_p5s02r_in_pre164r3.json
(4d93c82d). Gates: aside == 4d93c82d; every top-level key except `actions` equal; the new action list minus {dw_23460, rle_23519} == the old list (deep
equal, same order); dw_23460 sits right after dw_cond and right before do_23042; rle_23519 right after do_23501 and right before c_lr7; both use only the
fields of the adopted P4 rows (op, id, wire_uid, why: plan_ring_p4_s07v18_prov148.json:184-187, plan_ring_p4_s01.json:148-151). Prints every action's
position old -> new (the A-number = 1-based position) and checks that no action carries a numeric reference to another action.
PREDICTION CONTRACT: all gates PASS; positions A1..A53 unchanged, every later action +1 (after dw_23460) or +2 (after rle_23519).
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c164_a3_1_cmp.log -- py -u tools/bench/prep_c164_a3_1_cmp.py"""
import os, sys                                                                               # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, B)
import prep_c156_a1_1_lib as L                                                               # noqa: E402
import prep_plan_flow_lib as FL                                                              # noqa: E402
md5, J = L.md5, L.J
gate = L.Gate(fatal_default=False)
OLDP, NEWP = os.path.join(B, "plan_ring_p5s02r_in_pre164r3.json"), os.path.join(B, "plan_ring_p5s02r_in.json")
gate("ASIDE copy == 4d93c82d (unmodified)", md5(OLDP).startswith("4d93c82d"), md5(OLDP))
print("FACT MD5 r_in old {0} -> new {1}".format(md5(OLDP), md5(NEWP)), flush=True)
O, N = J(OLDP), J(NEWP)
gate("TOP every key except actions equal", all(O.get(k) == N.get(k) for k in set(O) | set(N) if k != "actions"),
     [k for k in set(O) | set(N) if k != "actions" and O.get(k) != N.get(k)])
NEW = {"dw_23460", "rle_23519"}
oid, nid = [a["id"] for a in O["actions"]], [a["id"] for a in N["actions"]]
added = [i for i in nid if i not in oid]
gate("ADD added ids == {{dw_23460, rle_23519}}; counts {0} -> {1}".format(len(oid), len(nid)), sorted(added) == sorted(NEW) and len(nid) == len(oid) + 2, added)
gate("REST new actions minus the 2 == old actions (deep equal, same order)", [a for a in N["actions"] if a["id"] not in NEW] == O["actions"])
pos = dict((i, k) for k, i in enumerate(nid, 1))
gate("ORD dw_cond < dw_23460 < do_23042 adjacent: A{0}, A{1}, A{2}".format(pos["dw_cond"], pos["dw_23460"], pos["do_23042"]),
     pos["dw_23460"] == pos["dw_cond"] + 1 and pos["do_23042"] == pos["dw_23460"] + 1)
gate("ORD do_23501 < rle_23519 < c_lr7 adjacent: A{0}, A{1}, A{2}".format(pos["do_23501"], pos["rle_23519"], pos["c_lr7"]),
     pos["rle_23519"] == pos["do_23501"] + 1 and pos["c_lr7"] == pos["rle_23519"] + 1)
byid = dict((a["id"], a) for a in N["actions"])
gate("FIELDS new rows {0}".format([(i, byid[i]) for i in sorted(NEW)]),
     byid["dw_23460"]["op"] == "delete_wire" and byid["dw_23460"]["wire_uid"] == 23460 and byid["rle_23519"]["op"] == "wire_remove_loose_ends"
     and byid["rle_23519"]["wire_uid"] == 23519 and all(set(byid[i]) == {"op", "id", "wire_uid", "why"} for i in NEW))
opos = dict((i, k) for k, i in enumerate(oid, 1))
shift = {}
for i in nid:
    d = pos[i] - opos[i] if i in opos else None
    shift.setdefault(d, []).append(i)
    if pos[i] >= 50:
        print("FACT POS {0}: A{1} -> A{2}".format(i, opos.get(i, "new"), pos[i]), flush=True)
print("FACT SHIFT {0}".format(dict((d, (len(v), v[0], v[-1])) for d, v in shift.items())), flush=True)
numref = [(a["id"], k, v) for a in N["actions"] for k, v in FL.leaves(a).items() if k.split("/")[-1] in ("of", "act", "in_act", "out_act", "after", "before")]
gate("NUM no action field refers to another action by number (resolved by id / uid)", not numref, numref)
sys.exit(gate.result([{"path": "tools/bench/plan_ring_p5s02r_in.json", "md5": md5(NEWP)}]))
