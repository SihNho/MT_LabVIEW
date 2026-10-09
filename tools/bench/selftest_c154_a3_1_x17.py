# ---
# labview: none
# hardware: none
# offline-args: --baseline
# evidence: tools/bench/cards/brief_154-a3-1.md
# ---
r"""selftest_c154_a3_1_x17 - card 154-a3-1 step 5 (offline, json only, no LabVIEW, no COM): the X17 registration of
DonorQueue_v0 (docs/d1/ring-p5.md PD376(c)) in stage_prerun.PRIM_DONORS. Section O = the OFFLINE half of
selftest_prim_gate_c141_1.py (O0-O5, copied verbatim: the gates PRIM_DONORS can move; its R half tests stagexec.prim_check,
unchanged by this card). Section N = the new entries: N1 the four uids pass with the json's label/class (+ md5 81dba822 on disk);
N2 a wrong label refuses; N3 a wrong class refuses; N4 unknown uid 999 refuses UNMEASURED; N5 the registry labels/classes ==
tools/bench/donor_queue_v0.json. `--baseline` runs section O only plus N0 (the four keys ABSENT), before the edit.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/selftest_c154_a3_1_x17.log -- py -u tools/bench/selftest_c154_a3_1_x17.py"""
import json, os, sys                                                                     # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stage_prerun as SPR                                                                # noqa: E402
G = {"pass": 0, "fail": 0, "first": None}
BASE = "--baseline" in sys.argv
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
DONOR, DQ = os.path.join(CD, "DonorRAS1D_v0.vi"), os.path.join(CD, "DonorQueue_v0.vi")


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:600]), flush=True)


print("FACT stage_prerun md5 {0} mode={1}".format(SPR.md5(os.path.join(ROOT, "tools", "stage_prerun.py")), "baseline" if BASE else "full"))
RAS = {"op": "create", "id": "p4_ras_bufdiff", "class": "GrowableFunction", "diagram": 32464, "as": "RAB1", "prim": "Replace Array Subset",
       "donor": {"donor": "$work", "uid": 29157}, "terminals": [{"name": "array", "is_source": False, "term_class": "Terminal"}]}
L = SPR.prim_donor_labels()
gate("O0 main_vi_node_labels.json: #29157 = 'Insert Into Array'", L.get(29157) == "Insert Into Array", L.get(29157))
b1 = SPR.prim_donor_check({"actions": [RAS]}, L)
gate("O1 create 'Replace Array Subset' from $work #29157 refused", len(b1) == 1 and "Insert Into Array" in b1[0]["why"], b1)
b2 = SPR.prim_donor_check({"actions": [dict(RAS, donor={"donor": DONOR, "uid": 175})]}, L)
gate("O2 from DonorRAS1D_v0.vi uid 175 passes (registry label + md5 e8a9417c on disk)", not b2 and os.path.isfile(DONOR)
     and SPR.md5(DONOR) == "e8a9417ce4b75d27e8fd2f172a5dc9cd", (b2, os.path.isfile(DONOR)))
EQ = {"op": "create", "id": "eq", "class": "Comparison", "diagram": 1, "prim": "Equal?", "donor": {"donor": "$work", "uid": 10171}}
L3 = dict(L)
L3[10171] = "Equal?"
b3 = SPR.prim_donor_check({"actions": [{"op": "delete_object", "id": "d", "uid": 10171}, EQ]}, L3)
gate("O3 a $work donor deleted by an earlier action is refused", len(b3) == 1 and "EARLIER" in b3[0]["why"], b3)
b4 = SPR.prim_donor_check({"actions": [dict(RAS, donor={"donor": "C:\\x\\Unknown_v0.vi", "uid": 5})]}, L)
gate("O4 an unlisted external donor is refused (UNMEASURED)", len(b4) == 1 and "UNMEASURED" in b4[0]["why"], b4)
ok5, d5 = SPR.x17_gate([json.load(open(os.path.join(ROOT, "tools", "bench", "plan_ring_p4_v15.json"), encoding="utf-8"))], L)
gate("O5 x17_gate over v15 refuses p4_ras_bufdiff ($work #29157)", not ok5 and "p4_ras_bufdiff" in [x["action"] for x in (d5 if isinstance(d5, list) else [])], d5)
dq = json.load(open(os.path.join(ROOT, "tools", "bench", "donor_queue_v0.json"), encoding="utf-8"))
J = dict((o["uid"], (o["label"], o["class"])) for o in dq["objects"] if o["role"] in ("obtain", "enqueue", "dequeue", "release"))
KEYS = [("DonorQueue_v0.vi", u) for u in (108, 44, 45, 46)]
if BASE:
    gate("N0 the four DonorQueue_v0 keys are ABSENT from PRIM_DONORS (before the edit)", not any(k in SPR.PRIM_DONORS for k in KEYS), KEYS)
else:
    mk = lambda u, lab, cls: {"op": "create", "id": "q{0}".format(u), "class": cls, "diagram": 686, "prim": lab, "donor": {"donor": DQ, "uid": u}}  # noqa: E731
    b = SPR.prim_donor_check({"actions": [mk(u, J[u][0], J[u][1]) for u in (108, 44, 45, 46)]}, L)
    gate("N1 uids 108/44/45/46 with the json label + class 'Function' pass (md5 81dba822 on disk)", not b and SPR.md5(DQ) == "81dba822efec5226123b3b88ee4383bc", b)
    b = SPR.prim_donor_check({"actions": [mk(108, "Enqueue Element", "Function")]}, L)
    gate("N2 uid 108 declared 'Enqueue Element' (wrong label) refuses", len(b) == 1 and "!= plan prim" in b[0]["why"], b)
    b = SPR.prim_donor_check({"actions": [mk(44, "Enqueue Element", "GrowableFunction")]}, L)
    gate("N3 uid 44 declared class GrowableFunction (wrong class) refuses", len(b) == 1 and "!= plan prim" in b[0]["why"], b)
    b = SPR.prim_donor_check({"actions": [mk(999, "Obtain Queue", "Function")]}, L)
    gate("N4 unknown uid 999 still refuses UNMEASURED", len(b) == 1 and "UNMEASURED" in b[0]["why"], b)
    gate("N5 PRIM_DONORS label/class/md5 == donor_queue_v0.json for all four", all(
        SPR.PRIM_DONORS.get(("DonorQueue_v0.vi", u), ())[:3] == (J[u][0], J[u][1], dq["md5"]) for u in J) and len(J) == 4,
        [SPR.PRIM_DONORS.get(k) for k in KEYS])
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(0 if not G["fail"] else 1)
