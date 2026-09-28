r"""plan_ring_p2a_make - card 121-2 (offline, no LabVIEW): the RING P2a plan (PD238(a)(g)) from the graph of the SAVED pool bed
(graph_qrt_pool_20260928.json md5 d265b283, diag_c120_g.py on a byte copy of D1_qrt_pool_20260928_141055.vi). DELETE ROWS ONLY, L2-R2 shape
(plan_l2r2_make.py: wires first, then objects). PRIOR ART (checked): plan_l2r2_make.py (retire cut), stagexec.retire_check/retire_ends,
opmodels delete_wire.json (a LoopTunnel left with no wire is gone too, stagesim DROP_WHEN_UNWIRED) / delete_object.json (a branched wire the node
sank keeps its other sinks). No new op.
Retire set, found ON THE GRAPH (no re-typed uid): QF/QW = the 2 Functions on 13236 with 'element data type' on #13938.New Image's wire;
ENQ = the Function whose 'queue' is fed (through one LoopTunnel) by an Obtain's 'queue out'; C20 = the DigitalNumericConstant feeding both
Obtains' max queue size. KEEP: For (owner of the ENQ body), IMAQ Create (source of ENQ.element), ring (-> IMAQ Image Type), names tunnel
(-> IMAQ Image Name) and the names ArrayConstant (-> that tunnel's outer).
Rows: delete_wire of every wire whose EVERY terminal is on a retired node or on the Enqueue's queue tunnel, then of every wire whose kept
source feeds ONLY retired sinks (IMAQ New Image -> ENQ.element); shared nets with a kept sink (w14741) are NOT deleted - the object deletes
remove only the Obtains' branches. Then delete_object ENQ, QF, QW, C20. The queue tunnel is removed by LabVIEW when its last wire goes
(opmodel delete_wire.json) - predicted, not a plan row.
PREDICTION -> plan_ring_p2a_pred.json: objects lost == 4 + the queue tunnel; wires lost == the delete rows; w14741's terminal list == R2's
(graph_l2r2_saved_20260928.json); every other base terminal keeps its wire, except IMAQ.New Image -> 0; cdiff == the pool bed's 16 rows;
Error List 53 -> 54 (w14741 keeps a dangling branch: one loose-ends item per wire object, the L2-R1 accounting PD230(d)); alternative 53.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/plan_ring_p2a_make.log -- py -u tools/bench/plan_ring_p2a_make.py"""
import hashlib, json, os, sys                                                      # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import protocol as P  # noqa: E402
B = os.path.dirname(os.path.abspath(__file__))
J = lambda fn: json.load(open(os.path.join(B, fn), encoding="utf-8"))  # noqa: E731
GF, R2F = "graph_qrt_pool_20260928.json", "graph_l2r2_saved_20260928.json"
G, R2, POOL, PIN = J(GF), J(R2F), J("stage_d1_qrt_pool.json")["qrt_pool"], J("plan_qrt_pool_in.json")
EL = J("errorlist_expected_D1_qrt_pool_20260928_141055.json")
BED, BED_MD5 = G["vi"], G["md5"]
ok = []


def gate(name, c, det):
    ok.append((name, bool(c)))
    print("{0}  {1}  {2}".format("PASS" if c else "FAIL", name, json.dumps(det, default=str)[:1200]), flush=True)


T = G["terminals"]
byw, own = {}, {}
for r in T:
    own.setdefault(int(r["owner_uid"]), []).append(r)
    if r["wire_uid"]:
        byw.setdefault(int(r["wire_uid"]), []).append(r)
cls = dict((int(o["uid"]), o["class"]) for o in G["objs"])
term = lambda u, n: [r for r in own.get(u, []) if r["term_name"] == n]      # noqa: E731
src_of = lambda w: [int(x["owner_uid"]) for x in byw.get(w, []) if x["is_source"]]   # noqa: E731
W_IMG = int(term(13938, "New Image")[0]["wire_uid"])
OBT = sorted(set(int(r["owner_uid"]) for r in byw[W_IMG] if r["owner_class"] == "Function" and r["term_name"] == "element data type"
                 and int(r["frame_diagram"] or 0) == 13236))
gate("M0 two Obtain Queue Functions on 13236 sink #13938.New Image's wire w{0}".format(W_IMG), len(OBT) == 2, OBT)
QT = [int(x["owner_uid"]) for u in OBT for r in term(u, "queue out") if r["wire_uid"] for x in byw[int(r["wire_uid"])] if x["owner_class"] == "LoopTunnel"]
QF = [u for u in OBT if any(r["wire_uid"] for r in term(u, "queue out"))]
QW = [u for u in OBT if u not in QF]
ENQ = [int(x["owner_uid"]) for t in QT for r in own[t] if r["is_source"] and r["wire_uid"] for x in byw[int(r["wire_uid"])]
       if x["owner_class"] == "Function" and x["term_name"] == "queue"]
C20 = sorted(set(s for u in OBT for r in term(u, "max queue size (-1, unlimited)") if r["wire_uid"] for s in src_of(int(r["wire_uid"]))))
gate("M1 Q_free (queue out wired) / Q_work (not) / ONE queue LoopTunnel / ONE Enqueue behind it / ONE I32 constant on both max sizes",
     len(QF) == 1 and len(QW) == 1 and len(QT) == 1 and len(ENQ) == 1 and len(C20) == 1 and cls.get(C20[0]) == "DigitalNumericConstant",
     {"QF": QF, "QW": QW, "QT": QT, "ENQ": ENQ, "C20": C20})
RET = [ENQ[0], QF[0], QW[0], C20[0]]
IMQ = src_of(int(term(ENQ[0], "element")[0]["wire_uid"]))[0]
RING = src_of(int(term(IMQ, "Image Type")[0]["wire_uid"]))[0]
TUN = src_of(int(term(IMQ, "Image Name")[0]["wire_uid"]))[0]
NAMES = [s for r in own[TUN] if not r["is_source"] and r["wire_uid"] for s in src_of(int(r["wire_uid"]))][0]
BODY = int(term(ENQ[0], "queue")[0]["frame_diagram"])
FOR = int(G["owners"][str(BODY)][1])
KEEP = {"p_for": FOR, "p_imaq": IMQ, "p_names": NAMES, "p_ring": RING, "p_tun": TUN}
gate("M2 keep set = ForLoop / SubVI / ArrayConstant / RingConstant / LoopTunnel, none retired",
     [cls.get(u) for u in (FOR, IMQ, NAMES, RING, TUN)] == ["ForLoop", "SubVI", "ArrayConstant", "RingConstant", "LoopTunnel"] and not set(KEEP.values()) & set(RET + QT),
     KEEP)
GONE = set(RET) | set(QT)
ws = sorted(set(int(r["wire_uid"]) for u in GONE for r in own[u] if r["wire_uid"]))
stubs = [w for w in ws if all(int(x["owner_uid"]) in GONE for x in byw[w])]
orphan = [w for w in ws if w not in stubs and all(int(x["owner_uid"]) in GONE for x in byw[w] if not x["is_source"])
          and not any(int(x["owner_uid"]) in GONE for x in byw[w] if x["is_source"])]
shared = [w for w in ws if w not in stubs and w not in orphan]
gate("M3 wires: stubs (every end retired) + ONE orphaned kept output (IMAQ New Image -> ENQ) + ONE shared net (w{0}) with kept sinks".format(W_IMG),
     len(orphan) == 1 and shared == [W_IMG] and not any(x["is_source"] and int(x["owner_uid"]) in GONE for x in byw[W_IMG]),
     {"stubs": stubs, "orphan": orphan, "shared": shared})
cons = [(u, int(x["owner_uid"])) for u in RET for r in own[u] if r["is_source"] and r["wire_uid"] for x in byw[int(r["wire_uid"])]
        if not x["is_source"] and int(x["owner_uid"]) not in GONE]
gate("M4 no retired node sources a kept sink (rule 1a: nothing kept loses its source)", not cons, cons)
r2w = sorted((int(x["term_uid"]), bool(x["is_source"])) for x in R2["terminals"] if int(x["wire_uid"] or 0) == W_IMG)
after = sorted((int(x["term_uid"]), bool(x["is_source"])) for x in byw[W_IMG] if int(x["owner_uid"]) not in GONE)
gate("M5 w{0} after the deletes == R2's terminal list (only the 2 Obtain type branches go)".format(W_IMG), after == r2w and len(byw[W_IMG]) - len(after) == 2, {"r2": r2w, "after": after})
acts = [{"op": "delete_wire", "id": "p2a_w{0}".format(w), "wire_uid": w, "why": "stub: every terminal on a retired node or the Enqueue's queue tunnel #{0}".format(QT[0])} for w in stubs]
acts += [{"op": "delete_wire", "id": "p2a_w{0}".format(w), "wire_uid": w, "why": "kept IMAQ Create #{0} New Image fed ONLY the Enqueue #{1}; P3 wires the images".format(IMQ, ENQ[0])} for w in orphan]
names = {ENQ[0]: "p_enq Enqueue(Q_free)", QF[0]: "p_qfree Obtain Q_free", QW[0]: "p_qwork Obtain Q_work", C20[0]: "p_i32 I32 20"}
acts += [{"op": "delete_object", "id": "p2a_o{0}".format(u), "uid": u, "why": "PD238(a)(g) P2a: {0} (ring buffer, no queues)".format(names[u])} for u in RET]
GMD5 = hashlib.md5(open(os.path.join(B, GF), "rb").read()).hexdigest()
lost_rows = sorted(int(r["term_uid"]) for u in GONE for r in own[u])
unwired = sorted(int(x["term_uid"]) for w in orphan for x in byw[w] if int(x["owner_uid"]) not in GONE)
pel = {"bed_total": EL["total"], "predicted_total": EL["total"] + 1, "new_items_predicted": 1, "alternative_total": EL["total"],
       "derivation": "w{0} loses 2 of its 4 terminals by delete_object; one 'Wire: has loose ends' item per wire object (L2-R1 accounting, PD230(d)); every other retired wire is deleted whole".format(W_IMG)}
pred = {"schema": "ring-p2a-pred/1", "graph": {"path": "tools/bench/" + GF, "md5": GMD5}, "bed": BED, "bed_md5": BED_MD5,
        "retire": RET, "auto_removed": QT, "keep": KEEP, "stubs": stubs, "orphan": orphan, "shared": shared, "w_img": W_IMG, "w_img_after": after,
        "terminal_rows_lost": lost_rows, "terminal_unwired": unwired, "census": {"LoopTunnel": -1, "Wire": -(len(stubs) + len(orphan))},
        "cdiff_rows": sorted(POOL["cdiff_rows"]), "errorlist": pel, "ops": ["delete_wire"] * (len(stubs) + len(orphan)) + ["delete_object"] * 4}
plan = {"schema": "stageplan/1", "stage": "ring_p2a",
        "goal": "RING P2a (PD238(a)(g), card 121-2): on the SAVED pool bed {0} delete Obtain Q_free/Q_work, the For-body Enqueue and the I32 20 (+ wires); "
                "keep the For, IMAQ Create, names constant, ring and names tunnel; deletes only, wires first".format(os.path.basename(BED)),
        "base": {"path": "tools/bench/" + GF, "md5": GMD5}, "context": PIN["context"], "actions": acts, "open_rows": PIN["open_rows"]}
if all(c for _n, c in ok):
    json.dump(plan, open(os.path.join(B, "plan_ring_p2a_in.json"), "w", encoding="utf-8"), indent=1)
    json.dump(pred, open(os.path.join(B, "plan_ring_p2a_pred.json"), "w", encoding="utf-8"), indent=1)
    print("  FACT WROTE plan_ring_p2a_in.json ({0} actions) + plan_ring_p2a_pred.json; retire {1}, auto-removed {2}".format(len(acts), RET, QT), flush=True)
np_, nf = sum(1 for _n, c in ok if c), sum(1 for _n, c in ok if not c)
print(P.result_line(P.make_result(np_, nf, next((n for n, c in ok if not c), None))), flush=True)
sys.exit(1 if nf else 0)
