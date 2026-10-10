# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_165-1-1.md
# ---
r"""selftest_c165_innerface - card 165-1-1 (docs/d1/ring-p5c.md PD400(b)), OFFLINE on the recorded graph 2a5fa0c4 (no LabVIEW, no COM).
Shared functions under test (stagexec): loop_inner_face_sink (called by connect_route, LVBackend.branch, SimBackend.branch),
route_on_state / state_addr (card 157/158), SimBackend.connect / .branch (the dry route check stagesim.route_report runs), compile_plan.
stagesim (unchanged by this card): base_state, op_delete_wire, op_wire, load_models / model_for.
WHAT EXISTED FIRST: selftest_c157_innerface.py (source-side twin, same STOP text), selftest_c158_wire0face.py (the wire-0 act shape).
PREDICTION (gates):
 A1  compile_plan(plan_ring_p5s02r_in.json): w_k3f / w_k4f (A70 / A80) compile to kind 'branch' (tunnel new:OK3 / new:OK4, side outer),
     each immediately preceded by its own op 'delete_wire' (dw_10362 / dw_25232).
 A2  the step-5 form of A70 (src bound to OK3's real outer face #31815 on SelectorTunnel #31803): compile_plan of
     [delete_wire 10362, wire #31815 -> 5204/8776] = kinds ['delete_wire', 'connect'].
 A3  stagesim on graph 2a5fa0c4: op_delete_wire w10362 = sourceless stub, Wire object removed, t8776 wire 0; op_wire #31815 -> t8776 =
     how 'branch' onto OK3's wire w31792 (t8776 on w31792). Same for w25232 / t24342.
 A4  route_on_state after the delete: (#31815 -> 8776) and (#31815 -> 24342) = 'connect_term_uid', act src 31815, dst 8776 / 24342,
     variant loop_inner_face_sink, census None, dst_loop 23041 WhileLoop, dst_diag 23405.
 A5  SimBackend.connect (connect op) and SimBackend.branch (branch op, tunnel #31803 as the stand-in for OK3 / OK4) on that state:
     check.route 'connect_term_uid', act as A4, nothing unroutable; the private state gets t8776 / t24342 on w31792.
 S1  wired face: t8776 still on the stub w10362 -> the existing STOP text verbatim (connect and branch).
 S2  Case-tunnel inner face (a SelectorTunnel InnerTerminal sink on 2a5fa0c4, zeroed, a wired source on its frame) -> the existing
     SelectorTunnel STOP text verbatim.
 S3  Flat-Sequence-tunnel inner face (a FlatSequenceInnerTunnel sink, zeroed, wired source on its diagram) -> its existing stop;
     if 2a5fa0c4 records none, a 'Tunnel' inner face on a Flat Sequence frame -> the existing Tunnel STOP text.
 S4  non-loop owner: owners['23405'] relabelled CaseStructure, t8776 zeroed -> the existing LoopTunnel STOP text.
 S5  unwired source on 23405 -> the existing LoopTunnel STOP text (the route needs a WIRED source).
 B1  stored plans p5s01a, p5s01b, p5s02a, p5s02b, p5s02c, p5s02d: compile_plan with the PRE-CHANGE stagexec (the pinned a4df7e15 bytes,
     %TEMP%\c165_a1_1\stagexec_pre.txt) and the new one -> byte-equal JSON; md5 of each plan and of each compile quoted.
 B2  the same six plans: dry_run (require_final as stored) before vs after -> equal (status, first_fail, per-op route / check, unroutable).
 P   pins: graph 2a5fa0c4, stagesim 95a162ba, stagekit dd57c1ca.
Usage: py tools/bgrun.py --material --max-min 20 --log tools/bench/selftest_c165_innerface.log -- py -u tools/bench/selftest_c165_innerface.py"""
import copy
import hashlib
import json
import os
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402
import stagexec as SX  # noqa: E402
import stagesim as SS  # noqa: E402

G = {"pass": 0, "fail": 0, "first": None}
GP = os.path.join(HERE, "graph_ring_p5s02d_20261010_154830.json")
RIN = os.path.join(HERE, "plan_ring_p5s02r_in.json")
PRE = os.path.join(tempfile.gettempdir(), "c165_a1_1", "stagexec_pre.txt")
PRE_PIN = "a4df7e15"
if "--pre" in sys.argv:                                 # card 165-3-1: B0-B2 against another pre-change copy (--pre <path> <md5 prefix>)
    PRE, PRE_PIN = sys.argv[sys.argv.index("--pre") + 1], sys.argv[sys.argv.index("--pre") + 2]
STOP_TXT = "ADDRESS: #{0} is an INNER face of {1} #{2}: only the outer face's owner route is measured (l2a1_faces_81.log)"
OK3, OK3_OUT, OK3_W = 31803, 31815, 31792


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(d)[:700]), flush=True)


def md5(p):
    with open(p, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def jl(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def row(st, t):
    return next(r for r in st["terminals"] if r["term_uid"] == t)


graph = jl(GP)
S0 = SS.base_state(graph)
MODELS = SS.load_models()
PW = SS.model_for("wire", MODELS)[0]
PD = SS.model_for("delete_wire", MODELS)[0]

print("---------- (a) A70 / A80 compile and route to connect_term_uid", flush=True)
rin = jl(RIN)
ids = [a.get("id") for a in rin["actions"]]
try:
    ops = SX.compile_plan(rin)
    kinds = dict((tuple(o["acts"]), o) for o in ops)
    res = {}
    for dw, wf, tun in (("dw_10362", "w_k3f", "new:OK3"), ("dw_25232", "w_k4f", "new:OK4")):
        i, j = ids.index(dw) + 1, ids.index(wf) + 1
        o_dw, o_wf = kinds.get((i,)), kinds.get((j,))
        res[wf] = (i, j, (o_dw or {}).get("kind"), o_wf)
    gate("A1 compile_plan(r_in): w_k3f / w_k4f = 'branch' (new:OK3 / new:OK4, outer), each right after its delete_wire op",
         all(v[1] == v[0] + 1 and v[2] == "delete_wire" and (v[3] or {}).get("kind") == "branch" and (v[3] or {}).get("side") == "outer"
             and v[3].get("tunnel") == t for v, t in ((res["w_k3f"], "new:OK3"), (res["w_k4f"], "new:OK4"))), res)
except SX.ExecStop as e:
    gate("A1 compile_plan(r_in)", False, "ExecStop {0}".format(e))
mini = {"actions": [{"op": "delete_wire", "id": "dw_10362", "wire_uid": 10362},
                    {"op": "wire", "id": "w_k3f", "src": {"uid": OK3, "term_uid": OK3_OUT}, "dst": {"uid": 5204, "term_uid": 8776}}]}
k2 = [o["kind"] for o in SX.compile_plan(mini)]
gate("A2 step-5 form of A70 (src = OK3's real outer face #31815): kinds ['delete_wire', 'connect']", k2 == ["delete_wire", "connect"], k2)

S = copy.deepcopy(S0)
e_d1, _c = SS.op_delete_wire(S, {"wire_uid": 10362}, PD, None, {})
e_d2, _c = SS.op_delete_wire(S, {"wire_uid": 25232}, PD, None, {})
S_del = copy.deepcopy(S)
e_w1, _c = SS.op_wire(copy.deepcopy(S), {"src": {"uid": OK3, "term_uid": OK3_OUT}, "dst": {"uid": 5204, "term_uid": 8776}}, PW, None, {})
e_w2, _c = SS.op_wire(copy.deepcopy(S), {"src": {"uid": OK3, "term_uid": OK3_OUT}, "dst": {"uid": 10404, "term_uid": 24342}}, PW, None, {})
gate("A3 stagesim: delete w10362 / w25232 = sourceless stubs (1 row, Wire object gone, face wire 0); wire #31815 -> face = 'branch' on w31792",
     e_d1.get("n_terminals") == 1 and e_d1.get("sourceless_wire_object") and e_d2.get("n_terminals") == 1 and e_d2.get("sourceless_wire_object")
     and row(S, 8776)["wire_uid"] == 0 and row(S, 24342)["wire_uid"] == 0 and row(S, OK3_OUT)["wire_uid"] == OK3_W
     and e_w1.get("how") == "branch" and e_w1.get("wire") == OK3_W and e_w2.get("how") == "branch" and e_w2.get("wire") == OK3_W,
     (e_d1, e_d2, e_w1, e_w2))
for lab, dst, tun in (("A70", 8776, 5204), ("A80", 24342, 10404)):
    k, info = SX.route_on_state(S, OK3_OUT, dst)
    act = (info or {}).get("act") if isinstance(info, dict) else None
    gate("A4 {0}: route_on_state(#31815 -> {1}) after the stub delete = 'connect_term_uid', act src 31815 / dst {1}, variant {2}".format(
        lab, dst, SX.LOOP_FACE_SINK), k == "connect_term_uid" and act and act["act"] == "connect_term_uid" and act["src_term"] == OK3_OUT
         and act["dst_term"] == dst and act["variant"] == SX.LOOP_FACE_SINK and act["census"] is None and info["dst_loop"] == 23041
         and info["dst_loop_cls"] == "WhileLoop" and info["dst_diag"] == 23405, (k, info))


def sim_be(st, actions):
    be = SX.SimBackend({"actions": actions}, st, MODELS)
    be.addr.owners = st.get("owners") or {}
    return be


acts = [{"op": "wire", "src": {"uid": OK3, "term_uid": OK3_OUT}, "dst": {"uid": 5204, "term_uid": 8776}},
        {"op": "wire", "src": {"uid": OK3, "term_uid": OK3_OUT}, "dst": {"uid": 10404, "term_uid": 24342}}]
be = sim_be(S, acts)
r1 = be.connect(OK3_OUT, 8776, be.read(), {}, {"kind": "connect", "acts": [1]})
r2 = be.branch(OK3, 24342, be.read(), {}, {"kind": "branch", "acts": [2]}, side="outer")
c1, c2 = r1.get("check") or {}, r2.get("check") or {}
gate("A5 SimBackend.connect (A70 form) / .branch (A80 form, stand-in tunnel #31803): route 'connect_term_uid', acts as A4, none "
     "unroutable, private state t8776 / t24342 on w31792",
     c1.get("route") == "connect_term_uid" and c2.get("route") == "connect_term_uid" and c1["act"]["dst_term"] == 8776
     and c2["act"]["dst_term"] == 24342 and c2["act"]["src_term"] == OK3_OUT and not be.unroutable
     and row(be.st, 8776)["wire_uid"] == OK3_W and row(be.st, 24342)["wire_uid"] == OK3_W, (c1, c2, be.unroutable))

print("---------- (b) every other inner face still stops", flush=True)
k, t = SX.route_on_state(S0, OK3_OUT, 8776)
be0 = sim_be(S0, acts)
rb = be0.branch(OK3, 8776, be0.read(), {}, {"kind": "branch", "acts": [1]}, side="outer")
gate("S1 wired face (t8776 on stub w10362): connect -> existing STOP verbatim; branch -> unroutable with it",
     k == "STOP" and t == STOP_TXT.format(8776, "LoopTunnel", 5204) and len(be0.unroutable) == 1
     and be0.unroutable[0]["err"] == STOP_TXT.format(8776, "LoopTunnel", 5204), (t, be0.unroutable))


def wired_src_on(st, diag, avoid=()):
    c = sorted((r for r in st["terminals"] if r["is_source"] and int(r["wire_uid"] or 0) and int(r["frame_diagram"] or 0) == diag
                and r["owner_class"] not in SX.FACE_ROUTED + SX.SR_CLS + (SX.FSIT_CLS, SX.FP) and r["term_uid"] not in avoid),
               key=lambda r: r["term_uid"])
    return c[0] if c else None


sel = sorted((r for r in S0["terminals"] if r["owner_class"] == "SelectorTunnel" and r["term_class"] == "InnerTerminal"
              and not r["is_source"]), key=lambda r: r["term_uid"])
done = False
for r0 in sel:
    s = wired_src_on(S0, int(r0["frame_diagram"] or 0))
    if s is None:
        continue
    k, t = SX.route_on_state(S0, s["term_uid"], r0["term_uid"], zero_terms=[r0["term_uid"]])
    gate("S2 Case-tunnel inner face #{0} (SelectorTunnel #{1}, frame #{2}, wire {3} -> 0) <- wired #{4} -> existing STOP verbatim".format(
        r0["term_uid"], r0["owner_uid"], r0["frame_diagram"], r0["wire_uid"], s["term_uid"]),
         k == "STOP" and t == STOP_TXT.format(r0["term_uid"], "SelectorTunnel", SX.V.node_of(r0)), t)
    done = True
    break
if not done:
    gate("S2 a SelectorTunnel inner sink with a wired source on its frame exists on 2a5fa0c4", False, len(sel))

fsit = sorted((r for r in S0["terminals"] if r["owner_class"] == SX.FSIT_CLS and not r["is_source"]), key=lambda r: r["term_uid"])
fs_frames = set(k_ for k_, v in (S0.get("owners") or {}).items() if v[0] in ("FlatSequenceFrame", SS.FS_CLS))
tun_fs = sorted((r for r in S0["terminals"] if r["owner_class"] == "Tunnel" and r["term_class"] == "InnerTerminal" and not r["is_source"]
                 and str(int(r["frame_diagram"] or 0)) in fs_frames), key=lambda r: r["term_uid"])
print("FACT S3 candidates on 2a5fa0c4: {0} FlatSequenceInnerTunnel sink row(s), {1} 'Tunnel' inner sink row(s) on {2} FS frame(s)".format(
    len(fsit), len(tun_fs), len(fs_frames)), flush=True)
done = False
for r0, want in [(r, "is a FlatSequenceInnerTunnel face") for r in fsit] + [(r, None) for r in tun_fs]:
    s = wired_src_on(S0, int(r0["frame_diagram"] or 0))
    if s is None:
        continue
    k, t = SX.route_on_state(S0, s["term_uid"], r0["term_uid"], zero_terms=[r0["term_uid"]])
    exp_ok = (want in str(t)) if want else (t == STOP_TXT.format(r0["term_uid"], "Tunnel", SX.V.node_of(r0)))
    gate("S3 Flat-Sequence-tunnel inner face #{0} ({1} #{2}, frame #{3}) <- wired #{4} -> its existing stop".format(
        r0["term_uid"], r0["owner_class"], r0["owner_uid"], r0["frame_diagram"], s["term_uid"]), k == "STOP" and exp_ok, t)
    done = True
    break
if not done:
    gate("S3 a Flat-Sequence tunnel inner sink with a wired source on its diagram exists on 2a5fa0c4", False, (len(fsit), len(tun_fs)))

Sc = copy.deepcopy(S0)
Sc["owners"]["23405"] = ["CaseStructure", Sc["owners"]["23405"][1]]
k, t = SX.route_on_state(Sc, OK3_OUT, 8776, zero_terms=[8776])
gate("S4 non-loop owner (body 23405 relabelled CaseStructure, t8776 -> 0) -> existing LoopTunnel STOP verbatim",
     k == "STOP" and t == STOP_TXT.format(8776, "LoopTunnel", 5204), t)
bare = sorted((r for r in S_del["terminals"] if r["is_source"] and not int(r["wire_uid"] or 0) and int(r["frame_diagram"] or 0) == 23405
               and r["owner_class"] not in SX.FACE_ROUTED + SX.SR_CLS + (SX.FSIT_CLS, SX.FP) and not SX.is_const(r)),
              key=lambda r: r["term_uid"])
if bare:
    k, t = SX.route_on_state(S_del, bare[0]["term_uid"], 8776)
    gate("S5 unwired source #{0} ({1} #{2}) on 23405 -> t8776 (wire 0) -> existing LoopTunnel STOP verbatim".format(
        bare[0]["term_uid"], bare[0]["owner_class"], bare[0]["owner_uid"]), k == "STOP" and t == STOP_TXT.format(8776, "LoopTunnel", 5204), t)
else:
    print("FACT S5 no bare non-constant source on 23405 in 2a5fa0c4", flush=True)

print("---------- (c) stored plans: compile and dry route before vs after", flush=True)
gate("B0 pre-change copy = the card's pinned stagexec {0}".format(PRE_PIN), os.path.isfile(PRE) and md5(PRE).startswith(PRE_PIN),
     md5(PRE) if os.path.isfile(PRE) else "missing")
OLD = types.ModuleType("stagexec_pre")                 # the pre-change source, run as if it sat at tools/stagexec.py (its
OLD.__file__ = os.path.join(ROOT, "tools", "stagexec.py")   # paths are relative to __file__)
sys.modules["stagexec_pre"] = OLD
exec(compile(open(PRE, encoding="utf-8").read(), PRE, "exec"), OLD.__dict__)


def dry_sig(mod, path):
    try:
        st_, ff, ex = mod.dry_run(path, log=lambda *_a: None, require_final=bool((jl(path).get("finalized") or {}).get("final", True)))
    except Exception as e:                                      # noqa: BLE001 - the exception itself is compared
        return {"exc": "{0}: {1}".format(type(e).__name__, e)[:500]}
    rows = [(r.get("k"), r.get("op"), (((r.get("result") or {}).get("check") or {}) if isinstance(r.get("result"), dict) else None))
            for r in ex.report]
    return {"status": st_, "first_fail": str(ff), "rows": rows, "unroutable": getattr(ex, "unroutable", None)}


for stg in ("p5s01a", "p5s01b", "p5s02a", "p5s02b", "p5s02c", "p5s02d"):
    pth = os.path.join(HERE, "plan_ring_{0}.json".format(stg))
    pl = jl(pth)
    outs = []
    for mod in (OLD, SX):
        try:
            outs.append(json.dumps(mod.compile_plan(copy.deepcopy(pl)), sort_keys=True, default=str))
        except Exception as e:                                  # noqa: BLE001
            outs.append("EXC {0}: {1}".format(type(e).__name__, e))
    h = [hashlib.md5(o.encode("utf-8")).hexdigest()[:8] for o in outs]
    gate("B1 {0} (plan {1}): compile pre == new byte-equal (compile md5 {2} / {3}, {4} bytes)".format(
        stg, md5(pth)[:8], h[0], h[1], len(outs[1])), outs[0] == outs[1] and not outs[1].startswith("EXC"), outs[1][:200])
    d0, d1 = dry_sig(OLD, pth), dry_sig(SX, pth)
    j0, j1 = json.dumps(d0, sort_keys=True, default=str), json.dumps(d1, sort_keys=True, default=str)
    gate("B2 {0}: dry_run pre == new (status {1}, {2} rows, dry md5 {3} / {4})".format(
        stg, d1.get("status", d1.get("exc")), len(d1.get("rows") or []), hashlib.md5(j0.encode()).hexdigest()[:8],
        hashlib.md5(j1.encode()).hexdigest()[:8]), j0 == j1, (str(d0.get("first_fail", d0.get("exc")))[:200], str(d1.get("first_fail", d1.get("exc")))[:200]))

PINS = {GP: "2a5fa0c4", os.path.join(ROOT, "tools", "stagesim.py"): "95a162ba", os.path.join(ROOT, "tools", "stagekit.py"): "dd57c1ca"}
got = dict((os.path.basename(p), md5(p)[:8]) for p in PINS)
gate("P pins unchanged", all(md5(p).startswith(v) for p, v in PINS.items()), got)
print("FACT md5 stagexec {0} (pre {2}), r_in {1}".format(md5(os.path.join(ROOT, "tools", "stagexec.py")), md5(RIN), PRE_PIN), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(0 if not G["fail"] else 1)
