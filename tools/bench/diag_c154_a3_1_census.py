# ---
# labview: none
# hardware: none
# offline-args: --registered
# evidence: tools/bench/cards/brief_154-a3-1.md
# ---
r"""diag_c154_a3_1_census - card 154-a3-1 steps 1-4 + 6 (offline, json only, no LabVIEW, no COM): ROUTE CENSUS of the queue-
refnum forms S and L (docs/d1/ring-p5.md PD376(a)(b)(d)). COPY of diag_c154_a2_3_census.py (card 154-a2-3): same skeleton
(stagesim.base_state / OPS / model_for, stagexec.create_route / compile_plan, stage_prerun.prim_donor_check); changed: card id,
pins (ring-p5.md 9c5ba571, donor_queue_v0.json 15269b6c; stage_prerun checked before == after only, it is edited by this card),
and the action lists: the common rows A0 (unchanged rows of the old census), form S (Obtain + const on 686, refnum SR on #10170,
R1/R2 case tunnels, False pass-through), form L (Obtain on #4866, refnum indicator born on 'queue out', local read in the True
frame), and the P5-2 refnum rows (report-only, PD376(d)): S-mirror (SR on 1.7 #23041 / body #23405, Dequeue on L.inner,
R.outer -> Release on 686) and an L-mirror (local reads -> Dequeue in #23405 and -> Release on 686).
PREDICTIONS: P1 the common rows apply in stagesim; P2 form S applies + compiles (every link an existing route, PD376(a));
P3 form L applies + compiles; P4 X17 on the queue creates: refused UNMEASURED without --registered, NO refusal with it;
P5 protected md5s (and stage_prerun) unchanged during the run. A SimError / crash on a row is a row RESULT (GAP), not a stop.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c154_a3_1_census.log -- py -u tools/bench/diag_c154_a3_1_census.py"""
import copy, hashlib, json, os, sys                                                       # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagesim as SS, stagexec as SX, stage_prerun as SPR                                # noqa: E401,E402
G = {"pass": 0, "fail": 0, "first": None}
REG = "--registered" in sys.argv
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
GRAPH = os.path.join(ROOT, "tools", "bench", "graph_ring_p4s09_20261009_062044.json")
DQ = os.path.join(CD, "DonorQueue_v0.vi")
PINS = {"tools/stagekit.py": "604529e8", "tools/addrcheck.py": "207beb0d", "tools/gscript.py": "1a80236e", "tools/vigraph.py": "a7eb58c7",
        "tools/bench/memory_model.json": "6f2b5687", "tools/bench/graph_ring_p4s09_20261009_062044.json": "22f967b5",
        "docs/d1/ring-p5.md": "9c5ba571", "tools/stagexec.py": "1bab9cf9", "tools/stagesim.py": "78b8d5a1",
        "tools/bench/donor_queue_v0.json": "15269b6c", DQ: "81dba822"}
md = lambda k: hashlib.md5(open(k if os.path.isabs(k) else os.path.join(ROOT, k), "rb").read()).hexdigest()  # noqa: E731


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:700]), flush=True)


m0 = dict((k, md(k)) for k in PINS)
spr0 = md("tools/stage_prerun.py")
gate("P5a protected md5s == card pins (before)", all(m0[k].startswith(v) for k, v in PINS.items()), {k[-28:]: m0[k][:8] for k in m0})
print("FACT stage_prerun.py md5 {0} registered-run={1}".format(spr0, REG))
g = json.load(open(GRAPH, encoding="utf-8"))
dq = json.load(open(os.path.join(ROOT, "tools", "bench", "donor_queue_v0.json"), encoding="utf-8"))
role = dict((o["role"], o) for o in dq["objects"])
own = g.get("owners") or {}
print("FACT owners 4866={0} 686={1} 23166={2} 10170={3} 23405={4} 23041={5}".format(*[own.get(str(u)) for u in (4866, 686, 23166, 10170, 23405, 23041)]))
objs = dict((int(o["uid"]), o.get("class")) for o in g.get("objs") or [])
st0 = SS.base_state(g)
T = lambda r: [{"name": t["name"], "is_source": t["is_source"], "term_class": "ParameterTerminal"} for t in role[r]["terminals"]]  # noqa: E731
DN = lambda r: {"donor": DQ, "uid": role[r]["uid"]}                                                                            # noqa: E731
K = lambda f, u: {"donor": os.path.join(CD, f), "uid": u}                                                                       # noqa: E731
PRIM = {"obtain": "Obtain Queue", "enqueue": "Enqueue Element", "dequeue": "Dequeue Element", "release": "Release Queue"}
Q = lambda i, r, dg, s: {"op": "create", "id": i, "class": "Function", "diagram": dg, "as": s, "prim": PRIM[r], "donor": DN(r), "terminals": T(r)}  # noqa: E731
QK = lambda dg: {"op": "create", "id": "c_qk", "class": "ArrayConstant", "diagram": dg, "as": "QK1", "prim": "const_donor", "donor": DN("dbl_const"),  # noqa: E731
                 "terminals": [{"name": role["dbl_const"]["terminals"][0]["name"], "is_source": True, "term_class": "Terminal"}]}
W = lambda i, s, d: {"op": "wire", "id": i, "src": s, "dst": d}                                                                 # noqa: E731
LOC = lambda i, dg, s, lab, mode: {"op": "create", "id": i, "class": "Local", "diagram": dg, "as": s, "label": lab, "mode": mode,  # noqa: E731
                                   "terminals": [{"name": lab, "is_source": mode == "read", "term_class": "Terminal"}]}
OBT = lambda dg: [QK(dg), Q("c_obt", "obtain", dg, "QO1"), W("w_qk_obt", "new:QK1.value", "new:QO1.element data type")]  # noqa: E731
A0 = [  # the unchanged rows of the old census (rows 4-8, 11-18)
    {"op": "create", "id": "c_km1", "class": "DigitalNumericConstant", "diagram": 4866, "as": "KM1", "prim": "const_donor",
     "donor": K("DonorRingConst_v0.vi", 249), "terminals": [{"name": "", "is_source": True, "term_class": "Terminal"}]},
    {"op": "create", "id": "i_rec", "class": "ControlTerminal", "diagram": 4866, "as": "IR1", "label": "records final (1.2 to 1.7)",
     "indicator": True, "born_on": {"uid": "new:KM1"}},
    {"op": "create", "id": "c_case", "class": "CaseStructure", "diagram": 23166, "as": "CQ1", "selector_as": "SQ1", "frames": ["False", "True"],
     "src": {"uid": 29724, "term": "valid"}},
    Q("c_enq", "enqueue", "new:CQ1.f1", "EQ1"),
    {"op": "tunnel", "id": "t_el", "loop": "new:CQ1", "body": "new:CQ1.f1", "parent": 23166, "dir": "in", "as": "TE1"},
    W("w_el_in", {"uid": 2626, "term": "appended array"}, "new:TE1.outer"), W("w_el_enq", "new:TE1.inner", "new:EQ1.element"),
    {"op": "add_shift_reg", "id": "sr_n", "loop": 10170, "body": 23166, "parent": 686, "as": "SN1"},
    {"op": "create", "id": "c_k0", "class": "DigitalNumericConstant", "diagram": 686, "as": "K01", "prim": "const_donor",
     "donor": K("DonorSRInit_v0.vi", 248), "terminals": [{"name": "", "is_source": True, "term_class": "Terminal"}]},
    W("w_k0", "new:K01.value", "new:SN1L.outer"),
    {"op": "create", "id": "c_inc", "class": "Function", "diagram": "new:CQ1.f1", "as": "IN1", "prim": "Increment", "donor": {"donor": "$work", "uid": 1978},
     "terminals": [{"name": "x+1", "is_source": True, "term_class": "OverridableParameterTerminal"},
                   {"name": "x", "is_source": False, "term_class": "ParameterTerminal"}]},
    {"op": "tunnel", "id": "t_ci", "loop": "new:CQ1", "body": "new:CQ1.f1", "parent": 23166, "dir": "in", "as": "TCI"},
    W("w_ci_in", "new:SN1L.inner", "new:TCI.outer"), W("w_ci_inc", "new:TCI.inner", "new:IN1.x"),
    {"op": "tunnel", "id": "t_co", "loop": "new:CQ1", "body": "new:CQ1.f1", "parent": 23166, "dir": "out", "as": "TCO"},
    W("w_inc_co", "new:IN1.x+1", "new:TCO.inner"), W("w_co_r", "new:TCO.outer", "new:SN1R.inner"),
    W("w_false_pass", {"uid": "new:TCI", "side": "inner", "frame": "False"}, {"uid": "new:TCO", "side": "inner", "frame": "False"}),
    LOC("c_lw", 686, "LW1", "records final (1.2 to 1.7)", "write"), W("w_final", "new:SN1R.outer", "new:LW1.value")]
S_REF = [  # PD376(a) form S refnum rows
    {"op": "add_shift_reg", "id": "sr_q", "loop": 10170, "body": 23166, "parent": 686, "as": "SQR"},
    W("w_obt_srq", "new:QO1.queue out", "new:SQRL.outer"),
    {"op": "tunnel", "id": "t_qi", "loop": "new:CQ1", "body": "new:CQ1.f1", "parent": 23166, "dir": "in", "as": "TQI"},
    W("w_srq_qi", "new:SQRL.inner", "new:TQI.outer"), W("w_qi_enq", "new:TQI.inner", "new:EQ1.queue"),
    {"op": "tunnel", "id": "t_qo", "loop": "new:CQ1", "body": "new:CQ1.f1", "parent": 23166, "dir": "out", "as": "TQO"},
    W("w_enq_qo", "new:EQ1.queue out", "new:TQO.inner"), W("w_qo_srq", "new:TQO.outer", "new:SQRR.inner"),
    W("w_q_false", {"uid": "new:TQI", "side": "inner", "frame": "False"}, {"uid": "new:TQO", "side": "inner", "frame": "False"})]
L_REF = [  # PD376(b) form L refnum rows
    {"op": "create", "id": "i_q", "class": "ControlTerminal", "diagram": 4866, "as": "IQ1", "label": "queue (1.2 to 1.7)",
     "indicator": True, "born_on": "new:QO1.queue out"},
    LOC("c_lrq", "new:CQ1.f1", "LRQ1", "queue (1.2 to 1.7)", "read"), W("w_lrq_enq", "new:LRQ1.value", "new:EQ1.queue")]
P52 = {"S": [{"op": "add_shift_reg", "id": "sr_q7", "loop": 23041, "body": 23405, "parent": 686, "as": "SQ7"},
             W("w_obt_sq7", "new:QO1.queue out", "new:SQ7L.outer"), Q("c_deq", "dequeue", 23405, "DQ1"),
             W("w_sq7_deq", "new:SQ7L.inner", "new:DQ1.queue"), W("w_deq_sq7", "new:DQ1.queue out", "new:SQ7R.inner"),
             Q("c_rel", "release", 686, "RL1"), W("w_sq7_rel", "new:SQ7R.outer", "new:RL1.queue")],
       "L": [Q("c_deq", "dequeue", 23405, "DQ1"), LOC("c_lrq7", 23405, "LRQ7", "queue (1.2 to 1.7)", "read"),
             W("w_lrq7_deq", "new:LRQ7.value", "new:DQ1.queue"), Q("c_rel", "release", 686, "RL1"),
             LOC("c_lrq8", 686, "LRQ8", "queue (1.2 to 1.7)", "read"), W("w_lrq8_rel", "new:LRQ8.value", "new:RL1.queue")]}
FORMS = {"S": OBT(686) + A0 + S_REF, "L": OBT(4866) + A0 + L_REF}
models = SS.load_models()


def apply(st, a):
    P = SS.model_for(a["op"], models)[0]
    s2 = copy.deepcopy(st)
    try:
        eff, _c = SS.OPS[a["op"]](s2, a, P, None, {})
        return s2, None, eff
    except SS.SimError as e:
        return st, "SIMERROR " + str(e), None
    except Exception as e:                    # noqa: BLE001 - a simulator CRASH on a row is a census fact
        return st, "CRASH {0}: {1} (stagesim raised, not a SimError)".format(type(e).__name__, e), None


def census(tag, acts, st=None):
    st, bad = (st if st is not None else st0), []
    for a in acts:
        st, err, eff = apply(st, a)
        e = eff or {}
        if err:
            bad.append((a["id"], err[:400]))
        print("ROW {0} {1:<12} {2:<13} {3} | how={4} variant={5} node={6}".format(tag, a["id"], a["op"], err or "ok", e.get("how"),
              e.get("variant") or (e.get("case_frame") or {}).get("variant"), e.get("node")), flush=True)
        if a["op"] == "create":
            try:
                print("ROUTE {0} {1:<8} -> {2}".format(tag, a["id"], SX.create_route(a)))
            except SX.ExecStop as x:
                bad.append((a["id"], "route ExecStop " + str(x)[:300]))
                print("ROUTE {0} {1:<8} -> ExecStop {2}".format(tag, a["id"], str(x)[:300]))
    try:
        ops = SX.compile_plan({"stage": "p5_census_" + tag, "actions": acts})
        print("COMPILE {0}: {1} ops kinds {2}".format(tag, len(ops), [(o["kind"], o.get("variant")) for o in ops]), flush=True)
    except SX.ExecStop as x:
        bad.append(("compile", "ExecStop " + str(x)[:400]))
        print("COMPILE {0}: ExecStop {1}".format(tag, str(x)[:400]), flush=True)
    except Exception as x:                    # noqa: BLE001
        bad.append(("compile", "CRASH {0}: {1}".format(type(x).__name__, x)))
        print("COMPILE {0}: CRASH {1}: {2}".format(tag, type(x).__name__, x), flush=True)
    print("GAPS {0}: {1}".format(tag, json.dumps(bad)), flush=True)
    return st, bad


res, end = {}, {}
for f in ("S", "L"):
    end[f], res[f] = census(f, FORMS[f])
gate("P2 form S: every row applies in stagesim, routes and compiles", not res["S"], res["S"])
gate("P3 form L: every row applies in stagesim, routes and compiles", not res["L"], res["L"])
chosen = "S" if not res["S"] else ("L" if not res["L"] else "NONE")
print("CHOSEN: {0}".format(chosen), flush=True)
for f in ("S", "L"):        # P5-2 refnum rows, report-only (PD376(d)): the GAPs do not change CHOSEN
    _s, b = census("P52" + f, FORMS[f] + P52[f])
    print("P52 {0}: {1}".format(f, "all OK" if not b else json.dumps(b)), flush=True)
for f in ("S", "L"):
    bad = SPR.prim_donor_check({"actions": FORMS[f] + P52[f]}, base_uids=set(objs))
    q = [x for x in bad if "DonorQueue_v0" in x["why"]]
    print("FACT X17 form {0} (+P5-2): {1}".format(f, json.dumps(bad)), flush=True)
    want = [] if REG else sorted(["c_obt", "c_enq", "c_deq", "c_rel"])
    gate("P4 X17 form {0} DonorQueue_v0 creates: {1}".format(f, "no refusal (registered)" if REG else "refused UNMEASURED"),
         sorted(x["action"] for x in q) == want and (REG or all("UNMEASURED" in x["why"] for x in q)) and len(bad) == len(q), bad)
m1 = dict((k, md(k)) for k in PINS)
gate("P5b protected md5s + stage_prerun unchanged during the run", m1 == m0 and md("tools/stage_prerun.py") == spr0, [k for k in m0 if m0[k] != m1[k]])
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(0 if not G["fail"] else 1)
