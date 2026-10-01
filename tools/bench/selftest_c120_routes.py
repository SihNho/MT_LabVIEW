"""Self-test of card 120-3 (PD237(k)): the stagexec plan routes + stagesim models for DEQUEUE (R1) and a CASE STRUCTURE
IN A LOOP BODY (R2: create, input tunnel into a frame, output tunnel out of a frame, a node placed in a frame). No
LabVIEW, no COM: stagesim/stagexec run on a synthetic graph; the LabVIEW backend's two new branches run on fakes.

WHAT EXISTED FIRST: gscript.queue_node('dequeue') (gscript.py:1339-1371), gscript.case_in / case_frames (:3479-3543),
the Enqueue queue route + auto tunnel (card 118-3, stagexec.py create_route / LVBackend.create 'queue'), the loop
`tunnel` group (compile_plan kind 'tunnel'), the case-selector owner route (stagexec T112e). The measured case shape
comes from tools/bench/selftest_c120_caseshape.log (graph_qrt_pool_20260928.json). The installed stageplan schema
(docs/protocol/stageplan.json) allows queue_kind obtain|enqueue and '.body' diagrams only: this test widens it IN PROCESS
and writes the widening to tools/bench/selftest_c120_stageplan_proposed.json (the card may not write the schema).

PREDICTION (29 gates): C01-C11 the full plan compiles to the expected routes, simulates, has the measured case shape,
the selector / input tunnel / output tunnel / frame placement / two dequeues as modelled, and DRY-RUNS PASS with the
case, its frames, selector and both case tunnels bound to positive uids; N01-N10 each malformed row is refused where a
real stage would stop; L01-L05 the LabVIEW backend's dequeue and case branches on fakes (incl. 2 negatives) and
bind_case_faces' {} on a loop-only op; A01-A03 existing routes unchanged.
Usage: py tools/bench/selftest_c120_routes.py"""
import copy
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol   # noqa: E402
import stagesim as SS   # noqa: E402
import stagexec as SX   # noqa: E402

gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, str(detail)[:260]), flush=True)


def raises(fn, exc):
    try:
        fn()
        return "no error"
    except exc as e:
        return "refused: " + str(e)


# ------------------------------------------------------------------ the widened schema (in process only)
def proposed():
    s = copy.deepcopy(protocol.load_schema("stageplan/1"))
    d = s["definitions"]
    d["diagref"]["anyOf"][1]["pattern"] = r"^new:[A-Za-z]+[0-9]+\.(body|f[0-9]+)$"
    P = d["action"]["properties"]
    P["queue_kind"] = dict(P["queue_kind"], enum=["obtain", "enqueue", "dequeue"])
    P["selector_as"] = {"type": "string", "pattern": "^[A-Za-z]+[0-9]+$",
                        "description": "card 120-3: create CaseStructure - the alias of its selector ('Tunnel') object"}
    P["frames"] = {"type": "array", "minItems": 2, "items": {"type": "string", "minLength": 1, "maxLength": 80},
                   "description": "card 120-3: create CaseStructure - frame names in order (default False/True); 'new:<as>.f<k>'"}
    s["description"] = "PROPOSED (card 120-3, widening only): " + s.get("description", "")
    return s


SP = protocol.schema_path("stageplan/1")
PROPOSED = proposed()
json.dump(PROPOSED, open(os.path.join(ROOT, "tools", "bench", "selftest_c120_stageplan_proposed.json"), "w", encoding="utf-8"), indent=1)
protocol._SCHEMAS.pop(SP, None)
protocol._SCHEMAS[SP] = PROPOSED


def row(t, n, s, w, o, oc, fd, tc="Terminal"):
    return {"term_uid": t, "term_name": n, "is_source": s, "wire_uid": w, "owner_uid": o, "owner_class": oc,
            "frame_diagram": fd, "term_class": tc}


base = SS._synthetic()
base["terminals"] += [row(5001, "Stop", True, 0, 10, "Diagram", 10, "ControlTerminal"),
                      row(5002, "Sel", True, 0, 10, "Diagram", 10, "ControlTerminal"),
                      row(1051, "queue out", True, 0, 5, "Function", 10, "ParameterTerminal")]
base["objs"].append({"uid": 5, "class": "Function", "pos": [0, 0], "owner": "Diagram"})
DQ_TERMS = [{"name": n, "is_source": s} for n, s in SS.QUEUE_TERM_TABLE["dequeue"]]
loc = lambda nm, d, mode="read": {"op": "create", "id": nm.lower(), "class": "Local", "diagram": d, "as": nm,  # noqa: E731
                                  "label": "Stop", "mode": mode, "pos": [5, 5],
                                  "terminals": [{"name": "Stop", "is_source": mode == "read"}]}
ACTS = [{"op": "create", "id": "dl", "class": "WhileLoop", "diagram": 10, "as": "DL1", "pos": [0, 0]},
        {"op": "create", "id": "case", "class": "CaseStructure", "diagram": "new:DL1.body", "as": "C1", "selector_as": "S1",
         "label": "Sel", "frames": ["False", "True"], "pos": [40, 40]},
        loc("LR1", "new:DL1.body"),
        {"op": "wire", "id": "sel", "src": "new:LR1.value", "dst": "new:S1.outer"},
        {"op": "create", "id": "cp", "class": "SubVI", "diagram": "new:C1.f1", "as": "CP1", "donor_uid": 4, "pos": [9, 9],
         "terminals": [{"name": "x", "is_source": False}, {"name": "y", "is_source": False}]},
        loc("LR2", "new:DL1.body"),
        {"op": "tunnel", "id": "t1", "loop": "new:C1", "body": "new:C1.f1", "parent": "new:DL1.body", "dir": "in", "as": "T1"},
        {"op": "wire", "id": "t1o", "src": "new:LR2.value", "dst": "new:T1.outer"},
        {"op": "wire", "id": "t1i", "src": "new:T1.inner", "dst": "new:CP1.x"},
        loc("LR3", "new:C1.f0"),
        loc("LW1", "new:DL1.body", "write"),
        {"op": "tunnel", "id": "t2", "loop": "new:C1", "body": "new:C1.f0", "parent": "new:DL1.body", "dir": "out", "as": "T2"},
        {"op": "wire", "id": "t2i", "src": "new:LR3.value", "dst": "new:T2.inner"},
        {"op": "wire", "id": "t2o", "src": "new:T2.outer", "dst": "new:LW1.value"},
        {"op": "create", "id": "dq1", "class": "Function", "diagram": "new:DL1.body", "as": "DQ1", "pos": [60, 60],
         "queue_kind": "dequeue", "src": "5.queue out", "src_into": "queue", "terminals": DQ_TERMS, "data_stream": True,
         "why": "self-test: a lossless data stream consumer"},
        {"op": "create", "id": "dq2", "class": "Function", "diagram": 10, "as": "DQ2", "pos": [70, 70],
         "queue_kind": "dequeue", "src": "5.queue out", "src_into": "queue", "terminals": DQ_TERMS, "data_stream": True,
         "why": "self-test: same-diagram dequeue"}]
PLAN = {"schema": "stageplan/1", "stage": "xc120", "actions": ACTS}

tmp = tempfile.mkdtemp(prefix="selftest_c120_")
gp = os.path.join(tmp, "graph.json")
json.dump(base, open(gp, "w", encoding="utf-8"))
PLAN["context"] = {"s1_graph": {"path": gp}}
md = os.path.join(tmp, "models")
os.makedirs(md, exist_ok=True)
q = lambda *a, **k: None   # noqa: E731

# ------------------------------------------------------------------ C: the full plan
ops = SX.compile_plan(PLAN)
got = [(o["kind"], o.get("route")) for o in ops]
want = [("create", "while"), ("create", "case"), ("create", "local_read"), ("connect", None), ("create", "copy_in"),
        ("create", "local_read"), ("tunnel", None), ("create", "local_read"), ("create", "local_write"), ("tunnel", None),
        ("create", "queue"), ("create", "queue")]
gate("C01 compile: case -> route 'case', both case tunnel groups -> ONE 'tunnel' op each, both dequeues -> 'queue'", got == want, got)
pp = os.path.join(tmp, "plan_in_xc120.json")
json.dump(PLAN, open(pp, "w", encoding="utf-8"))
ok_v = protocol.validate_obj(PLAN)
S = SS.simulate(pp, gp, out_root=os.path.join(tmp, "sim"), plan_out_dir=tmp, model_dir=md, log=q)
sym = S.get("sym") or {}
gate("C02 the plan validates (proposed schema) and SIMULATES to the end; symbols new:C1, .f0, .f1, new:S1 exist",
     ok_v[0] and S["failed"] is None and all(k in sym for k in ("new:C1", "new:C1.f0", "new:C1.f1", "new:S1")), (ok_v, S["failed"]))


def state(n):
    st = SS.base_state(base)
    out = []
    for a in ACTS[:n]:
        out.append(SS.OPS[a["op"]](st, a, SS.model_for(a["op"], {})[0], None, {})[0])
    return st, out


st, effs = state(len(ACTS))
C1, F0, F1, S1 = st["sym"]["new:C1"], st["sym"]["new:C1.f0"], st["sym"]["new:C1.f1"], st["sym"]["new:S1"]
BODY = st["sym"]["new:DL1.body"]
rows = lambda u: [r for r in st["terminals"] if r["owner_uid"] == u]   # noqa: E731
sel = rows(S1)
gate("C03 case shape (measured, selftest_c120_caseshape.log): CaseStructure + 2 frames owned by it on the body; selector 'Tunnel' = "
     "1 unnamed OUTER SINK on the body + 1 unnamed INNER SOURCE per frame",
     st["owners"][str(F0)] == ["CaseStructure", C1] and st["owners"][str(F1)] == ["CaseStructure", C1]
     and st["diagrams"][str(F0)] == BODY and sorted((r["term_class"], r["is_source"], r["frame_diagram"]) for r in sel)
     == sorted([("OuterTerminal", False, BODY), ("InnerTerminal", True, F0), ("InnerTerminal", True, F1)])
     and all(r["term_name"] == "" for r in sel), sel)
so = next(r for r in sel if r["term_class"] == "OuterTerminal")
lr1 = rows(st["sym"]["new:LR1"])[0]
gate("C04 selector wired by a plain `wire` (a connect op): outer sink on LR1's wire; its inner faces stay unwired",
     so["wire_uid"] and so["wire_uid"] == lr1["wire_uid"] and not any(r["wire_uid"] for r in sel if r["term_class"] == "InnerTerminal"))
T1r, T2r = rows(st["sym"]["new:T1"]), rows(st["sym"]["new:T2"])
cpx = next(r for r in rows(st["sym"]["new:CP1"]) if r["term_name"] == "x")
lr2 = rows(st["sym"]["new:LR2"])[0]
t1o = next(r for r in T1r if r["term_class"] == "OuterTerminal")
t1i = dict((r["frame_diagram"], r) for r in T1r if r["term_class"] == "InnerTerminal")
e_t1 = effs[6]
gate("C05 INPUT case tunnel T1: SelectorTunnel, outer SINK on the body on LR2's wire, inner SOURCE on f1 on CP1.x's wire, f0's inner "
     "unwired (effect unwired_frames == [f0])",
     T1r[0]["owner_class"] == "SelectorTunnel" and not t1o["is_source"] and t1o["wire_uid"] == lr2["wire_uid"]
     and t1i[F1]["is_source"] and t1i[F1]["wire_uid"] == cpx["wire_uid"] and not t1i[F0]["wire_uid"]
     and e_t1.get("unwired_frames") == [F0], e_t1)
t2o = next(r for r in T2r if r["term_class"] == "OuterTerminal")
t2i = dict((r["frame_diagram"], r) for r in T2r if r["term_class"] == "InnerTerminal")
lw1 = rows(st["sym"]["new:LW1"])[0]
lr3 = rows(st["sym"]["new:LR3"])[0]
e_t2 = effs[11]
gate("C06 OUTPUT case tunnel T2: outer SOURCE on LW1's wire, inner SINK on f0 on LR3's wire, f1's inner unwired; the model records "
     "use_default_if_unwired ASSUMED False and broken_unless_wired == [f1]",
     t2o["is_source"] and t2o["wire_uid"] == lw1["wire_uid"] and not t2i[F0]["is_source"] and t2i[F0]["wire_uid"] == lr3["wire_uid"]
     and not t2i[F1]["wire_uid"] and e_t2.get("broken_unless_wired") == [F1] and "ASSUMED" in e_t2.get("use_default_if_unwired", ""), e_t2)
gate("C07 nodes placed INSIDE frames: CP1 on f1, LR3 on f0", cpx["frame_diagram"] == F1 and lr3["frame_diagram"] == F0)
dq1 = dict((r["term_name"], r) for r in rows(st["sym"]["new:DQ1"]))
at = effs[14].get("auto_tunnel") or {}
q1 = next(r for r in base["terminals"] if r["term_uid"] == 1051)
qo = next(r for r in st["terminals"] if r["term_uid"] == 1051)
ao = next(r for r in st["terminals"] if r["term_uid"] == at.get("outer"))
ai = next(r for r in st["terminals"] if r["term_uid"] == at.get("inner"))
gate("C08 Dequeue in the loop body, src on the parent: the measured 7 terminals, ONE non-indexed auto LoopTunnel (outer sink on 10 on "
     "'queue out's wire, inner source on the body on DQ1.queue's wire) - the Enqueue rule of card 118-3",
     sorted(dq1) == sorted(n for n, _s in SS.QUEUE_TERM_TABLE["dequeue"]) and dq1["element"]["is_source"] and not dq1["queue"]["is_source"]
     and at.get("indexing") is False and ao["frame_diagram"] == 10 and ao["wire_uid"] == qo["wire_uid"] != 0 and q1["wire_uid"] == 0
     and ai["frame_diagram"] == BODY and ai["wire_uid"] == dq1["queue"]["wire_uid"], (at, effs[14].get("src_branch")))
dq2 = dict((r["term_name"], r) for r in rows(st["sym"]["new:DQ2"]))
gate("C09 same-diagram Dequeue BRANCHES the already-wired 'queue out' (no tunnel)", dq2["queue"]["wire_uid"] == qo["wire_uid"]
     and effs[15].get("src_branch") is True and "auto_tunnel" not in effs[15], effs[15])
fin = os.path.join(tmp, "plan_xc120.json")
dst, dff, ex = SX.dry_run(fin, log=q, model_dir=md, require_final=False)
bo, bd = ex.bind.get("obj") or {}, ex.bind.get("diag") or {}
ls = ex.step(len(ACTS))["state"]["sym"]
need_o = [ls[k] for k in ("new:C1", "new:S1", "new:T1", "new:T2", "new:DQ1", "new:DQ2", "new:CP1")]
gate("C10 DRY RUN PASS (non-final diagnostic mode): case + selector + both case tunnels + dequeues + frame node bound to POSITIVE uids; "
     "body + both frames bound", dst == "PASS" and all(bo.get(u, -1) > 0 for u in need_o)
     and all(bd.get(ls[k], -1) > 0 for k in ("new:DL1.body", "new:C1.f0", "new:C1.f1")), (dst, str(dff)[:300], need_o, bo, bd))
rt = dict((r["ids"][0], (r.get("result") or {}).get("check")) for r in ex.report[1:] if r.get("ids"))
gate("C11 dry route checks: case (selector control, frames), dq1 auto_tunnel True, dq2 False, selector connect resolved on the case's "
     "Terminals[] (owner route)", (rt.get("case") or {}).get("route") == "case" and (rt.get("case") or {}).get("selector_ct") == 5002
     and (rt.get("dq1") or {}).get("auto_tunnel") is True and (rt.get("dq2") or {}).get("auto_tunnel") is False
     and "Terminals" in str((rt.get("sel") or {}).get("how", "")) + str(rt.get("sel")), (rt.get("case"), rt.get("dq1"), rt.get("sel")))

# ------------------------------------------------------------------ N: negatives
def sim_one(extra, upto=2):
    s_, _e = state(upto)
    return raises(lambda: SS.OPS[extra["op"]](s_, extra, {}, None, {}), SS.SimError)


dq = dict(ACTS[14])
e = sim_one(dict(dq, terminals=[{"name": "queue", "is_source": False}, {"name": "element", "is_source": False}]))
gate("N01 dequeue declaring 'element' as a SINK is refused (measured direction: source)", "not in the measured Dequeue table" in e, e)
e = sim_one(dict(dq, terminals=[{"name": "queue", "is_source": False}, {"name": "timeout", "is_source": False}]))
gate("N02 dequeue declaring a GUESSED 'timeout' is refused (docs/NAMES.md:997)", "not in the measured Dequeue table" in e, e)
e = raises(lambda: SX.create_route(dict(dq, queue_kind="release")), SX.ExecStop)
gate("N03 queue_kind 'release' still has no route", "obtain|enqueue|dequeue" in e, e)
e = raises(lambda: SX.create_route({k: v for k, v in ACTS[1].items() if k != "selector_as"}), SX.ExecStop)
gate("N04 a case create without `selector_as` is refused by create_route", "selector_as" in e, e)
e = sim_one(dict(ACTS[1], diagram=10, **{"as": "C9", "selector_as": "S9"}), upto=1)
gate("N05 a case on the TOP-LEVEL diagram (not a loop body) is refused (case_in's contract)", "not a For/While body" in e, e)
e = sim_one(dict(ACTS[1], label="Nope", **{"as": "C9", "selector_as": "S9"}), upto=1)
gate("N06 a case whose `label` names no panel control is refused", "need exactly one CONTROL" in e, e)
e = raises(lambda: SS.resolve_diag(state(2)[0], "new:C1.f2"), SS.SimError)
gate("N07 'new:C1.f2' (no third frame) is refused", "not created by any earlier action" in e, e)
e = raises(lambda: SX.compile_plan({"actions": [ACTS[0], {"op": "move_in", "nodes": [4], "dest_diagram": "new:DL1.f0", "pos": [0, 0]}]}),
           SX.ExecStop)
gate("N08 '.f0' of a LOOP alias is refused by compile_plan", "symbolic diagram" in e, e)
e = sim_one({"op": "tunnel", "loop": "new:C1", "body": "new:DL1.body", "parent": 10, "dir": "in", "as": "T9"})
gate("N09 a case tunnel whose `body` is not a frame of that case is refused", "is not a frame of CaseStructure" in e, e)
e = raises(lambda: SX.compile_plan({"actions": ACTS[:2] + [{"op": "move_in", "nodes": [4], "dest_diagram": "new:C1.body", "pos": [0, 0]}]}),
           SX.ExecStop)
gate("N10 '.body' of a CASE alias is refused by compile_plan", "symbolic diagram" in e, e)

# ------------------------------------------------------------------ L: the LabVIEW backend on fakes
class FakeS(object):
    work = "C:/fake/work.vi"

    def __init__(self):
        self.calls = []

    def _op(self, verb, fn, detail=""):
        self.calls.append(verb)
        try:
            return {"verb": verb, "err": None, "result": fn(), "s": 0.0}
        except Exception as x:   # noqa: BLE001
            return {"verb": verb, "err": str(x), "result": None, "s": 0.0}

    def junk_purge(self, tag="", hints=()):
        return None


class FakeG(object):
    def __init__(self, case_names=("False", "True"), owner=777):
        self.log, self.tun, self.lt, self.case_names, self.owner = [], {10, 11}, {20}, list(case_names), owner

    def report_all(self, W, cls):
        return [{"uid": u} for u in ([3, 5, 9] if cls == "Function" else [])]

    def uids(self, W, cls):
        return set(self.tun) if cls == "Tunnel" else set(self.lt) if cls == "LoopTunnel" else set()

    def queue_node(self, kind, W, scls, sidx, sname, di, pos):
        self.log.append(("queue_node", kind, scls, sidx, sname, di, tuple(pos)))
        self.lt.add(21)
        return [4242]

    def case_in(self, W, diagram_uid, location, selector_label, frame_names=("0, Default", "1"), position=None):
        self.log.append(("case_in", diagram_uid, tuple(location), selector_label, tuple(frame_names)))
        self.tun.add(12)
        return {"case": 900, "owner_class": "Diagram", "owner": self.owner, "names": list(self.case_names), "frames": [901, 902], "err": ""}


def lvbe(g):
    be = object.__new__(SX.LVBackend)
    be.g, be.s = g, FakeS()
    be.B = type("B", (), {"diag_index": staticmethod(lambda W, d: 3)})()
    be.addr = SX.Addr(None, owners={"777": ["WhileLoop", 776]})
    return be


real = [row(1051, "queue out", True, 88, 5, "Function", 10, "ParameterTerminal")]
g1 = FakeG()
out = lvbe(g1).create("queue", dict(dq), {"diagram": 777, "pos": [60, 60], "src": 1051}, real, {"acts": [15]})
gate("L01 LVBackend 'queue' + dequeue: queue_node('dequeue', W, 'Function', idx 1, 'queue out', di, pos), one new LoopTunnel = the "
     "auto tunnel", g1.log == [("queue_node", "dequeue", "Function", 1, "queue out", 3, (60, 60))] and out.get("uid") == 4242
     and out.get("auto_tunnel") == 21, (g1.log, out))
g2 = FakeG(case_names=("True", "False"))
out = lvbe(g2).create("case", ACTS[1], {"diagram": 777, "pos": [40, 40]}, [], {"acts": [2]})
gate("L02 LVBackend 'case': case_in(W, 777, pos, 'Sel', ('False','True')); frames returned IN THE PLAN'S ORDER by name (read back "
     "True,False -> [902, 901]); the one new Tunnel = the selector",
     g2.log == [("case_in", 777, (40, 40), "Sel", ("False", "True"))] and out.get("uid") == 900 and out.get("frames") == [902, 901]
     and out.get("selector") == 12, (g2.log, out))
e = raises(lambda: lvbe(FakeG(case_names=("0, Default", "1"))).create("case", ACTS[1], {"diagram": 777, "pos": [40, 40]}, [], {"acts": [2]}),
           SX.ExecStop)
gate("L03 NEGATIVE: frame names read back other than asked ('0, Default','1') STOP", "frame names read back" in e, e)
e = raises(lambda: lvbe(FakeG(owner=555)).create("case", ACTS[1], {"diagram": 777, "pos": [40, 40]}, [], {"acts": [2]}), SX.ExecStop)
gate("L04 NEGATIVE: the case read back owned by another diagram STOPS", "read back owned by" in e, e)
s0, _e0 = state(0)
s1_, _e1 = state(1)
lt_only = SX.bind_case_faces([], [], s0["terminals"], s1_["terminals"], {"obj": {}, "term": {}, "diag": {}})
s6, _ = state(6)
s7, _ = state(7)
bad_real = [row(99001, "", False, 0, 99000, "SelectorTunnel", 50, "OuterTerminal"),
            row(99002, "", True, 0, 99000, "SelectorTunnel", 51, "InnerTerminal"),
            row(99003, "", True, 0, 99000, "SelectorTunnel", 52, "InnerTerminal")]
e = raises(lambda: SX.bind_case_faces([], bad_real, s6["terminals"], s7["terminals"],
                                      {"obj": {}, "term": {}, "diag": {s7["sym"]["new:C1.f0"]: 60, s7["sym"]["new:C1.f1"]: 61}}), SX.ExecStop)
gate("L05 bind_case_faces: {} on an op that made no multi-frame face (a loop create); a real tunnel on OTHER frames STOPS at BINDING",
     lt_only == {} and "BINDING" in e and "0 real candidate" in e, (lt_only, e))

# ------------------------------------------------------------------ A: existing routes unchanged (R4)
OLD = {"while", "for", "local_read", "local_write", "indicator", "control", "primitive", "copy_in", "const_on_term", "queue", "subvi"}
gate("A01 CREATE_ROUTES / ROUTE_VERBS: every old key kept, only 'case' added; the queue route still resolves obtain/enqueue",
     set(SX.CREATE_ROUTES) == OLD | {"case", "case_wired"} and set(SX.ROUTE_VERBS) >= OLD and SX.ROUTE_VERBS["queue"] == [("gscript", "queue_node")]
     and SX.create_route(dict(dq, queue_kind="obtain")) == "queue" and SX.create_route(dict(dq, queue_kind="enqueue")) == "queue"
     and not SX.verbs_missing("case"), sorted(SX.CREATE_ROUTES))
e = raises(lambda: SS.resolve_diag(state(1)[0], "new:DL1"), SS.SimError)
gate("A02 resolve_diag: '.body' resolves as before, a suffix-less symbolic diagram is still refused",
     SS.resolve_diag(state(1)[0], "new:DL1.body") < 0 and "a symbolic diagram is" in e, e)
cp_copy = {"op": "create", "class": "CaseStructure", "diagram": 10, "donor_uid": 77, "as": "CC1"}
gate("A03 a COPIED case (donor_uid) keeps the copy_in route (the new case route is only for a NEW case)",
     SX.create_route(cp_copy) == "copy_in")

protocol._SCHEMAS.pop(SP, None)
bad = [l for l, ok in gates if not ok]
print("=== GATES: %d pass / %d fail%s" % (len(gates) - len(bad), len(bad), "; failing: " + bad[0] if bad else ""), flush=True)
print(protocol.result_line(protocol.make_result(len(gates) - len(bad), len(bad), bad[0] if bad else None,
                                                [{"path": "tools/bench/selftest_c120_stageplan_proposed.json",
                                                  "md5": SX.md5(os.path.join(ROOT, "tools", "bench", "selftest_c120_stageplan_proposed.json"))}])),
      flush=True)
sys.exit(1 if bad else 0)
