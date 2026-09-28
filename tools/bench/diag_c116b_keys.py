"""diag_c116b_keys - card 116-2 STEP 0b prep (offline, no LabVIEW): are the saved-graph dumps of B3 and R1 comparable object for object?
rev 1 predicted equal top-level key sets and FAILED (the two dumps come from different readers: diag_c114c_b3graph.py adds loops/owners,
diag_c115d_graph.py adds wire_census). rev 3 applies review archive/peer/2026-09-28-c116b-keys.md:69-75 (the rev-2 field-name check could
not fail). PREDICTION: K1 R1 objs uid - B3 objs uid == {}; K2 B3 - R1 == the 12 SR uids + the 11 stub wires (plan_l2r1.json delete_wire rows)
+ exactly 24 Inner/OuterTerminal objects (12 + 12); K3 every uid kept in both has equal class and owner; K4 terminal rows R1 - B3 == {} and
B3 - R1 == the rows owned by the 12 SR uids. Nothing is written."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import protocol as P  # noqa: E402
B = os.path.dirname(os.path.abspath(__file__))
J = lambda fn: json.load(open(os.path.join(B, fn), encoding="utf-8"))  # noqa: E731
G3, G1, PL = J("graph_l2b3_20260928.json"), J("graph_l2r1_20260928.json"), J("plan_l2r1.json")
SR = {9018, 9025, 29505, 29512, 1147, 1142, 5796, 5805, 119, 2972, 7311, 11001}
STUBS = set(int(a["wire_uid"]) for a in PL["actions"] if a["op"] == "delete_wire")
o3, o1 = dict((int(o["uid"]), o) for o in G3["objs"]), dict((int(o["uid"]), o) for o in G1["objs"])
ok = []


def gate(name, c, det):
    ok.append((name, bool(c)))
    print("{0}  {1}  {2}".format("PASS" if c else "FAIL", name, json.dumps(det, default=str)[:900]), flush=True)


gate("K1 R1 objs - B3 objs == {}", not (set(o1) - set(o3)), sorted(set(o1) - set(o3))[:30])
gone = set(o3) - set(o1)
rest = gone - SR - STUBS
cls = {}
for u in rest:
    cls[o3[u]["class"]] = cls.get(o3[u]["class"], 0) + 1
gate("K2 B3 - R1 == 12 SR + {0} stubs + 24 Inner/OuterTerminal".format(len(STUBS)), SR <= gone and STUBS <= gone and len(STUBS) == 11
     and cls == {"InnerTerminal": 12, "OuterTerminal": 12}, {"n_gone": len(gone), "rest_classes": cls})
chg = [(u, o3[u]["class"], o3[u]["owner"], o1[u]["class"], o1[u]["owner"]) for u in set(o1) & set(o3)
       if (o3[u]["class"], str(o3[u]["owner"])) != (o1[u]["class"], str(o1[u]["owner"]))]
gate("K3 every kept uid has equal class and owner ({0} kept)".format(len(set(o1) & set(o3))), not chg, chg[:20])
t3, t1 = set(int(r["term_uid"]) for r in G3["terminals"]), set(int(r["term_uid"]) for r in G1["terminals"])
srt = set(int(r["term_uid"]) for r in G3["terminals"] if int(r["owner_uid"]) in SR)
gate("K4 terminal rows: R1 - B3 == {{}}, B3 - R1 == the {0} rows owned by the 12 SR uids".format(len(srt)), not (t1 - t3) and t3 - t1 == srt,
     {"r1_only": sorted(t1 - t3)[:20], "b3_only_not_sr": sorted((t3 - t1) - srt)[:20], "sr_rows_kept": sorted(srt & t1)[:20]})
np_, nf = sum(1 for _n, c in ok if c), sum(1 for _n, c in ok if not c)
print(P.result_line(P.make_result(np_, nf, next((n for n, c in ok if not c), None))), flush=True)
sys.exit(1 if nf else 0)
