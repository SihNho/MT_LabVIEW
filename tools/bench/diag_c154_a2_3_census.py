# ---
# labview: none
# hardware: none
# ---
r"""diag_c154_a2_3_census - card 154-a2-3 step 1-3 (offline, json only, no LabVIEW, no COM): ROUTE CENSUS of the P5-1 rows
(docs/d1/ring-p5.md PD374(a)(c) + PD375(a)). Existing things used (no new route/op): stagesim.base_state / OPS / model_for
(the replay's own per-action calls, stagesim.py:2597-2603), stagexec.create_route / compile_plan (stagexec.py:389, 729),
stage_prerun.prim_donor_check (X17, stage_prerun.py:2827). The P5-1 fragment is applied IN MEMORY to the s09 graph 22f967b5
(no step file, no plan file written). Forms copied from launched plans: plan_ring_p3a.json (case_wired / add_shift_reg /
const_sr / R1-R2 case tunnels / frame pass-through / Increment $work #1978), plan_ring_p4_s02v18.json (const_donor +
indicator born_on const on #4866, local_write), plan_ring_p4_s05v18.json (tunnel on base loop #10170).
PREDICTIONS: P1 every create row applies in stagesim; P2 the refnum from #4866 into loop 1.2 has no applicable form
(direct wire / case tunnel refused by the FS-exit rule stagesim.py:2150-2152); P3 X17 refuses the DonorQueue_v0 prims
(not in PRIM_DONORS, stage_prerun.py:2860-2861); P4 protected md5s unchanged.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c154_a2_3_census.log -- py -u tools/bench/diag_c154_a2_3_census.py"""
import copy, hashlib, json, os, sys                                                       # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagesim as SS, stagexec as SX, stage_prerun as SPR                                # noqa: E401,E402
G = {"pass": 0, "fail": 0, "first": None}
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
GRAPH = os.path.join(ROOT, "tools", "bench", "graph_ring_p4s09_20261009_062044.json")
DQ = os.path.join(CD, "DonorQueue_v0.vi")
PINS = {"tools/stagekit.py": "604529e8", "tools/addrcheck.py": "207beb0d", "tools/gscript.py": "1a80236e", "tools/vigraph.py": "a7eb58c7",
        "tools/bench/memory_model.json": "6f2b5687", "tools/bench/graph_ring_p4s09_20261009_062044.json": "22f967b5",
        "docs/d1/ring-p5.md": "81df09ca", "tools/stage_prerun.py": "c739eb86", "tools/stagexec.py": "1bab9cf9",
        "tools/stagesim.py": "78b8d5a1", DQ: "81dba822"}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:700]), flush=True)


def md5s():
    return dict((k, hashlib.md5(open(k if os.path.isabs(k) else os.path.join(ROOT, k), "rb").read()).hexdigest()) for k in PINS)


m0 = md5s()
gate("P4a protected md5s == card pins (before)", all(m0[k].startswith(v) for k, v in PINS.items()), {k: m0[k][:8] for k in m0})
g = json.load(open(GRAPH, encoding="utf-8"))
dq = json.load(open(os.path.join(ROOT, "tools", "bench", "donor_queue_v0.json"), encoding="utf-8"))
role = dict((o["role"], o) for o in dq["objects"])
own = g.get("owners") or {}
print("FACT owners 4866={0} 686={1} 23166={2} 10170={3} 681={4}".format(*[own.get(str(u)) for u in (4866, 686, 23166, 10170, 681)]))
print("FACT fs_measured 681 frames {0}".format(((g.get("fs_measured") or {}).get("fs_frames") or {}).get("681")))
objs = dict((int(o["uid"]), o.get("class")) for o in g.get("objs") or [])
print("FACT s09 objs #1978 {0!r} #29724 {1!r} #2626 {2!r}".format(objs.get(1978), objs.get(29724), objs.get(2626)))
st0 = SS.base_state(g)
print("FACT stagesim fs_of 4866={0} 686={1} 23166={2}".format(SS.fs_of(st0, 4866), SS.fs_of(st0, 686), SS.fs_of(st0, 23166)))
T = lambda r: [{"name": t["name"], "is_source": t["is_source"], "term_class": "ParameterTerminal"} for t in role[r]["terminals"]]  # noqa: E731
DN = lambda r: {"donor": DQ, "uid": role[r]["uid"]}                                                                            # noqa: E731
K = lambda f, u: {"donor": os.path.join(CD, f), "uid": u}                                                                       # noqa: E731
A = [
    {"op": "create", "id": "c_qk", "class": "ArrayConstant", "diagram": 4866, "as": "QK1", "prim": "const_donor", "donor": DN("dbl_const"),
     "terminals": [{"name": role["dbl_const"]["terminals"][0]["name"], "is_source": True, "term_class": "Terminal"}]},
    {"op": "create", "id": "c_obt", "class": "Function", "diagram": 4866, "as": "QO1", "prim": "Obtain Queue", "donor": DN("obtain"), "terminals": T("obtain")},
    {"op": "wire", "id": "w_qk_obt", "src": "new:QK1.value", "dst": "new:QO1.element data type"},
    {"op": "create", "id": "c_km1", "class": "DigitalNumericConstant", "diagram": 4866, "as": "KM1", "prim": "const_donor",
     "donor": K("DonorRingConst_v0.vi", 249), "terminals": [{"name": "", "is_source": True, "term_class": "Terminal"}]},
    {"op": "create", "id": "i_rec", "class": "ControlTerminal", "diagram": 4866, "as": "IR1", "label": "records final (1.2 to 1.7)",
     "indicator": True, "born_on": {"uid": "new:KM1"}},
    {"op": "create", "id": "c_case", "class": "CaseStructure", "diagram": 23166, "as": "CQ1", "selector_as": "SQ1", "frames": ["False", "True"],
     "src": {"uid": 29724, "term": "valid"}},
    {"op": "create", "id": "c_enq", "class": "Function", "diagram": "new:CQ1.f1", "as": "EQ1", "prim": "Enqueue Element", "donor": DN("enqueue"),
     "terminals": T("enqueue")},
    {"op": "tunnel", "id": "t_el", "loop": "new:CQ1", "body": "new:CQ1.f1", "parent": 23166, "dir": "in", "as": "TE1"},
    {"op": "wire", "id": "w_el_in", "src": {"uid": 2626, "term": "appended array"}, "dst": "new:TE1.outer"},
    {"op": "wire", "id": "w_el_enq", "src": "new:TE1.inner", "dst": "new:EQ1.element"},
    {"op": "add_shift_reg", "id": "sr_n", "loop": 10170, "body": 23166, "parent": 686, "as": "SN1"},
    {"op": "create", "id": "c_k0", "class": "DigitalNumericConstant", "diagram": 686, "as": "K01", "prim": "const_donor",
     "donor": K("DonorSRInit_v0.vi", 248), "terminals": [{"name": "", "is_source": True, "term_class": "Terminal"}]},
    {"op": "wire", "id": "w_k0", "src": "new:K01.value", "dst": "new:SN1L.outer"},
    {"op": "create", "id": "c_inc", "class": "Function", "diagram": "new:CQ1.f1", "as": "IN1", "prim": "Increment", "donor": {"donor": "$work", "uid": 1978},
     "terminals": [{"name": "x+1", "is_source": True, "term_class": "OverridableParameterTerminal"},
                   {"name": "x", "is_source": False, "term_class": "ParameterTerminal"}]},
    {"op": "tunnel", "id": "t_ci", "loop": "new:CQ1", "body": "new:CQ1.f1", "parent": 23166, "dir": "in", "as": "TCI"},
    {"op": "wire", "id": "w_ci_in", "src": "new:SN1L.inner", "dst": "new:TCI.outer"},
    {"op": "wire", "id": "w_ci_inc", "src": "new:TCI.inner", "dst": "new:IN1.x"},
    {"op": "tunnel", "id": "t_co", "loop": "new:CQ1", "body": "new:CQ1.f1", "parent": 23166, "dir": "out", "as": "TCO"},
    {"op": "wire", "id": "w_inc_co", "src": "new:IN1.x+1", "dst": "new:TCO.inner"},
    {"op": "wire", "id": "w_co_r", "src": "new:TCO.outer", "dst": "new:SN1R.inner"},
    {"op": "wire", "id": "w_false_pass", "src": {"uid": "new:TCI", "side": "inner", "frame": "False"},
     "dst": {"uid": "new:TCO", "side": "inner", "frame": "False"}},
    {"op": "create", "id": "c_lw", "class": "Local", "diagram": 686, "as": "LW1", "label": "records final (1.2 to 1.7)", "mode": "write",
     "terminals": [{"name": "records final (1.2 to 1.7)", "is_source": False, "term_class": "Terminal"}]},
    {"op": "wire", "id": "w_final", "src": "new:SN1R.outer", "dst": "new:LW1.value"}]
REF = {  # the refnum rows, each form tried on a COPY of the state after the fragment
    "Va direct wire Obtain->Enqueue.queue": [{"op": "wire", "id": "va", "src": "new:QO1.queue out", "dst": "new:EQ1.queue"}],
    "Vb loop tunnel on #10170 (outer on 686)": [{"op": "tunnel", "id": "vb_t", "loop": 10170, "body": 23166, "parent": 686, "dir": "in", "as": "TQ1"},
                                                {"op": "wire", "id": "vb_in", "src": "new:QO1.queue out", "dst": "new:TQ1.outer"}],
    "Vc case tunnel on CQ1 (outer on 23166)": [{"op": "tunnel", "id": "vc_t", "loop": "new:CQ1", "body": "new:CQ1.f1", "parent": 23166,
                                                "dir": "in", "as": "TQ2"},
                                               {"op": "wire", "id": "vc_in", "src": "new:QO1.queue out", "dst": "new:TQ2.outer"}]}
models = SS.load_models()


def apply(st, a):
    P = SS.model_for(a["op"], models)[0]
    s2 = copy.deepcopy(st)
    try:
        eff, _c = SS.OPS[a["op"]](s2, a, P, None, {})
        return s2, None, eff
    except SS.SimError as e:
        return st, str(e), None
    except Exception as e:                    # noqa: BLE001 - a simulator CRASH on a form is a census fact, recorded as such
        return st, "CRASH {0}: {1} (stagesim raised, not a SimError)".format(type(e).__name__, e), None


st, errs = st0, []
for a in A:
    st, err, eff = apply(st, a)
    if err:
        errs.append(a["id"])
    e = eff or {}
    print("ROW {0:<12} {1:<13} {2} | how={3} variant={4} node={5} terms={6}".format(a["id"], a["op"], "SIMERROR " + err if err else "ok",
          e.get("how"), e.get("variant") or (e.get("case_frame") or {}).get("variant"), e.get("node"),
          [r["term_name"] for r in st["terminals"] if r["term_uid"] in (e.get("terminals") or [])][:8]), flush=True)
gate("P1 every P5-1 fragment row except the refnum applies in stagesim", not errs, errs)
nm = lambda u: sorted((r["term_name"], r["is_source"], r["term_class"]) for r in st["terminals"] if r["owner_uid"] == st["sym"][u])  # noqa: E731
for u, r in (("new:QO1", "obtain"), ("new:EQ1", "enqueue")):
    gate("P1b {0} sim terminals == donor json names (class ParameterTerminal)".format(u),
         [x[:2] for x in nm(u)] == sorted((t["name"], t["is_source"]) for t in role[r]["terminals"]) and all(x[2] == "ParameterTerminal" for x in nm(u)), nm(u))
ok_ref = []
for lab, acts in REF.items():
    s2, last = st, None
    for a in acts:
        s2, err, eff = apply(s2, a)
        last = err or "ok how={0} variant={1}".format((eff or {}).get("how"), (eff or {}).get("variant"))
        if err:
            break
    ok_ref.append(not last.startswith("ok"))
    print("REF {0} | {1}".format(lab, last[:600]), flush=True)
gate("P2 the direct wire and the case-tunnel form of the refnum are refused by stagesim", ok_ref[0] and ok_ref[2], ok_ref)
for a in A + [x for v in REF.values() for x in v]:
    if a["op"] == "create":
        try:
            r = SX.create_route(a)
        except SX.ExecStop as e:
            r = "ExecStop " + str(e)[:120]
        print("ROUTE {0:<8} -> {1}".format(a["id"], r))
for lab, extra in (("fragment", []), ("fragment+Vb+out", REF["Vb loop tunnel on #10170 (outer on 686)"]
                                      + [{"op": "wire", "id": "vb_out", "src": "new:TQ1.inner", "dst": "new:EQ1.queue"}])):
    try:
        ops = SX.compile_plan({"stage": "p5s01_census", "actions": A + extra})
        print("COMPILE {0}: {1} ops kinds {2}".format(lab, len(ops), [(o["kind"], o.get("variant")) for o in ops]))
    except SX.ExecStop as e:
        print("COMPILE {0}: ExecStop {1}".format(lab, str(e)[:300]))
bad = SPR.prim_donor_check({"actions": A}, base_uids=set(objs))
print("FACT X17 prim_donor_check: {0}".format(json.dumps(bad)))
gate("P3 X17 refuses the DonorQueue_v0 prims as UNMEASURED (not in PRIM_DONORS)",
     sorted(x["action"] for x in bad if "UNMEASURED" in x["why"]) == ["c_enq", "c_obt"], bad)
m1 = md5s()
gate("P4b protected md5s unchanged (after)", m1 == m0, [k for k in m0 if m0[k] != m1[k]])
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(0 if not G["fail"] else 1)
