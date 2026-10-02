r"""selftest_prim_gate_c141_1 - card 141-1 items 1-2 (offline, no LabVIEW, no COM): the created-node PRIM GATE, both halves.
RUN-TIME half (stagexec.prim_check + LVBackend.create's primitive route, driven with a recording fake stage as
stagexec._selftest_live_const does):
  R1 the 140-3 case: plan prim 'Replace Array Subset' / class GrowableFunction, read back #29489 label 'Insert Into Array'
     (diag_c140_3_scratch.log:225) -> FAIL; R2 label 'Replace Array Subset' -> PASS; R3 no read-back entry -> FAIL;
  R4 const_donor -> exempt; R5 LVBackend.create(route 'primitive') with the 140-3 read-back raises ExecStop 'PRIM-GATE FAIL' and
     records a FAIL gate; R6 the same with a matching read-back returns the uid and records a PASS gate.
OFFLINE half (stage_prerun.prim_donor_check / x17_gate):
  O1 create 'Replace Array Subset' from $work #29157 -> refused (label 'Insert Into Array', main_vi_node_labels.json);
  O2 from claudeDev\DonorRAS1D_v0.vi uid 175 -> passes (registry + md5 e8a9417c on disk);
  O3 a $work donor an earlier delete_object removes -> refused; O4 an unlisted external donor -> refused;
  O5 x17_gate over v15 (eb4ffb6e) refuses p4_ras_bufdiff (#29157) - the gate would have stopped cycle 131's donor.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_prim_gate_c141_1.log -- py -u tools/bench/selftest_prim_gate_c141_1.py"""
import json, os, sys                                                                     # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagexec as SX, stage_prerun as SPR                                                 # noqa: E401,E402
G = {"pass": 0, "fail": 0, "first": None}
DONOR = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\DonorRAS1D_v0.vi"


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:600]), flush=True)


RAS = {"op": "create", "id": "p4_ras_bufdiff", "class": "GrowableFunction", "diagram": 32464, "as": "RAB1", "prim": "Replace Array Subset",
       "donor": {"donor": "$work", "uid": 29157}, "terminals": [{"name": "array", "is_source": False, "term_class": "Terminal"}]}
IIA = {"uid": 29489, "class": "GrowableFunction", "label": "Insert Into Array", "n_terminals": 4, "n_wired": 0}
OK_ = dict(IIA, label="Replace Array Subset")
ok1, d1 = SX.prim_check(RAS, IIA, 29489)
gate("R1 140-3 case: 'Insert Into Array' read back where the plan says 'Replace Array Subset' -> FAIL", not ok1 and "FAIL" in d1, d1)
ok2, d2 = SX.prim_check(RAS, OK_, 29489)
gate("R2 matching label + class -> PASS", ok2, d2)
ok3, d3 = SX.prim_check(RAS, None, 29489)
gate("R3 no read-back entry -> FAIL", not ok3, d3)
ok4, d4 = SX.prim_check(dict(RAS, prim="const_donor", **{"class": "BooleanConstant"}), None, 1)
gate("R4 const_donor exempt", ok4 and "exempt" in d4, d4)
gate("R4b purge_entry finds the entry by uid", SX.purge_entry({"reported_not_deleted": [IIA]}, 29489) == IIA
     and SX.purge_entry({"reported_not_deleted": [IIA]}, 1) is None)


class _S(object):
    work = "selftest_fake.vi"

    def __init__(self, entry):
        self.entry, self.gates = entry, []

    def _op(self, verb, fn, detail=""):
        return {"verb": verb, "err": None, "result": 29489, "s": 0.0}

    def junk_purge(self, tag="", hints=()):
        return {"tag": tag, "new_uids": [(29489, "GrowableFunction", (0, 0))], "deleted": [], "reported_not_deleted": [self.entry]}

    def gate(self, label, ok, detail="", fatal=False):
        self.gates.append((label, bool(ok), detail))


class _B(object):
    def diag_index(self, W, d):
        return 59


def live(entry):
    be = SX.LVBackend.__new__(SX.LVBackend)
    be.g, be.s, be.B = None, _S(entry), _B()
    try:
        out = SX.LVBackend.create(be, "primitive", RAS, {"diagram": 32464}, [], {"kind": "create", "acts": [13]})
        return out, None, be.s.gates
    except SX.ExecStop as e:
        return None, str(e), be.s.gates


o5, e5, g5 = live(IIA)
gate("R5 LVBackend.create primitive with the 140-3 read-back: ExecStop 'PRIM-GATE FAIL' + one FAIL gate",
     o5 is None and "PRIM-GATE FAIL" in str(e5) and len(g5) == 1 and not g5[0][1], (e5, g5))
o6, e6, g6 = live(OK_)
gate("R6 the same with 'Replace Array Subset' read back: uid returned + one PASS gate",
     e6 is None and (o6 or {}).get("uid") == 29489 and len(g6) == 1 and g6[0][1], (o6, e6, g6))
L = SPR.prim_donor_labels()
gate("O0 main_vi_node_labels.json: #29157 = 'Insert Into Array'", L.get(29157) == "Insert Into Array", L.get(29157))
b1 = SPR.prim_donor_check({"actions": [RAS]}, L)
gate("O1 create 'Replace Array Subset' from $work #29157 refused", len(b1) == 1 and "Insert Into Array" in b1[0]["why"], b1)
R175 = dict(RAS, donor={"donor": DONOR, "uid": 175})
b2 = SPR.prim_donor_check({"actions": [R175]}, L)
gate("O2 from DonorRAS1D_v0.vi uid 175 passes (registry label + md5 e8a9417c on disk)", not b2 and os.path.isfile(DONOR)
     and SPR.md5(DONOR) == "e8a9417ce4b75d27e8fd2f172a5dc9cd", (b2, os.path.isfile(DONOR)))
EQ = {"op": "create", "id": "eq", "class": "Comparison", "diagram": 1, "prim": "Equal?", "donor": {"donor": "$work", "uid": 10171}}
L3 = dict(L)
L3[10171] = "Equal?"
b3 = SPR.prim_donor_check({"actions": [{"op": "delete_object", "id": "d", "uid": 10171}, EQ]}, L3)
gate("O3 a $work donor deleted by an earlier action is refused", len(b3) == 1 and "EARLIER" in b3[0]["why"], b3)
b4 = SPR.prim_donor_check({"actions": [dict(RAS, donor={"donor": "C:\\x\\Unknown_v0.vi", "uid": 5})]}, L)
gate("O4 an unlisted external donor is refused (UNMEASURED)", len(b4) == 1 and "UNMEASURED" in b4[0]["why"], b4)
v15 = json.load(open(os.path.join(ROOT, "tools", "bench", "plan_ring_p4_v15.json"), encoding="utf-8"))
ok5, d5 = SPR.x17_gate([v15], L)
ids5 = [x["action"] for x in (d5 if isinstance(d5, list) else [])]
gate("O5 x17_gate over v15 refuses p4_ras_bufdiff ($work #29157)", not ok5 and "p4_ras_bufdiff" in ids5, d5)
print("FACT O5 v15 refusals: {0}".format(json.dumps(d5)[:900]), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(0 if not G["fail"] else 1)
