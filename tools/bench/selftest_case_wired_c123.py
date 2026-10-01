"""Self-test of card 123-7 STEP 1 (PD248(d)): the stagexec plan route `case_wired` + the stagesim model of gscript.case_wired.
No LabVIEW, no COM: stagesim/stagexec on the synthetic graph; the LabVIEW backend's branch on fakes.

WHAT EXISTED FIRST: the `case` route of card 120-3 R2 (gscript.case_in, selector from a panel control, wired by a later row) and its
self-test tools/bench/selftest_c120_routes.py; this adds the variant whose selector is wired IN THE SAME ACT from `src`.
Measured shape used by the model: tools/bench/diag_c123_wired.log:87-88 (CaseStructure 1, Diagram 2, Tunnel 1, OuterTerminal 1,
InnerTerminal 2, Wire 1; junk Invoke purged).
PREDICTION (14 gates): R01-R03 routing; M01-M05 the model (new wire, branch, three refusals); P01-P02 compile + dry run bound;
L01-L03 the LabVIEW branch on fakes (call + two STOPs); A01 the label route unchanged.
Usage: py tools/bench/selftest_case_wired_c123.py"""
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
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, str(detail)[:300]), flush=True)


def raises(fn, exc):
    try:
        fn()
        return "no error"
    except exc as e:
        return "refused: " + str(e)


base = SS._synthetic()
base["terminals"].append({"term_uid": 1025, "term_name": "flag", "is_source": True, "wire_uid": 0, "owner_uid": 2,
                          "owner_class": "SubVI", "frame_diagram": 20, "term_class": "Terminal"})
CW = {"op": "create", "id": "cw", "class": "CaseStructure", "diagram": 20, "as": "C1", "selector_as": "S1", "src": "2.flag",
      "frames": ["False", "True"], "pos": [40, 40]}
CB = dict(CW, id="cb", src="2.out", **{"as": "C2", "selector_as": "S2"})
LBL = {"op": "create", "id": "cl", "class": "CaseStructure", "diagram": 20, "as": "C3", "selector_as": "S3", "label": "Sel"}

gate("R01 create_route: CaseStructure + src, no label -> 'case_wired'; with label -> 'case'",
     SX.create_route(CW) == "case_wired" and SX.create_route(LBL) == "case")
gate("R02 verbs_missing('case_wired') == [] (gscript.case_wired / struct_copy_nested / case_frames defined)",
     SX.verbs_missing("case_wired") == [], SX.verbs_missing("case_wired"))
e = raises(lambda: SX.create_route({k: v for k, v in CW.items() if k != "selector_as"}), SX.ExecStop)
gate("R03 case_wired without selector_as is refused by create_route", "selector_as" in e, e)


def sim(acts):
    st = SS.base_state(base)
    effs = [SS.OPS[a["op"]](st, a, SS.model_for(a["op"], {})[0], None, {})[0] for a in acts]
    return st, effs


st, (ef,) = sim([CW])
C1, F0, F1, S1 = st["sym"]["new:C1"], st["sym"]["new:C1.f0"], st["sym"]["new:C1.f1"], st["sym"]["new:S1"]
sel = [r for r in st["terminals"] if r["owner_uid"] == S1]
so = next(r for r in sel if r["term_class"] == "OuterTerminal")
src = next(r for r in st["terminals"] if r["term_uid"] == 1025)
gate("M01 new wire: CaseStructure + 2 frames on body 20, selector Tunnel = 1 outer SINK + 1 inner SOURCE per frame, outer on "
     "a NEW wire == src's wire, src_branch False",
     st["owners"][str(F0)] == ["CaseStructure", C1] and st["owners"][str(F1)] == ["CaseStructure", C1]
     and sorted((r["term_class"], r["is_source"], r["frame_diagram"]) for r in sel)
     == sorted([("OuterTerminal", False, 20), ("InnerTerminal", True, F0), ("InnerTerminal", True, F1)])
     and so["wire_uid"] and so["wire_uid"] == src["wire_uid"] and ef.get("src_branch") is False and ef.get("wired") is True, ef)
st2, (eb,) = sim([CB])
so2 = next(r for r in st2["terminals"] if r["owner_uid"] == st2["sym"]["new:S2"] and r["term_class"] == "OuterTerminal")
gate("M02 branch: an already-wired src (2.out, w6) -> selector outer on w6, src_branch True", so2["wire_uid"] == 6 and eb.get("src_branch") is True, eb)
e = raises(lambda: sim([dict(CW, frames=["0, Default", "1"])]), SS.SimError)
gate("M03 frames other than False/True are refused (donor + Boolean selector)", "False" in e and "case_wired" in e, e)
e = raises(lambda: sim([dict(CW, diagram=30)]), SS.SimError)
gate("M04 src on another diagram (20) than the case (30) is refused", "same diagram" in e, e)
e = raises(lambda: sim([dict(CW, diagram=10, src="1.v")]), SS.SimError)
gate("M05 a CONSTANT source is refused (not a Node; case_wired resolves Nodes[])", "not a Node" in e, e)

ops = SX.compile_plan({"actions": [CW]})
gate("P01 compile_plan: the row compiles to ONE create op with route 'case_wired'",
     [(o["kind"], o.get("route")) for o in ops] == [("create", "case_wired")], ops)
tmp = tempfile.mkdtemp(prefix="selftest_cw123_")
gp, md = os.path.join(tmp, "graph.json"), os.path.join(tmp, "models")
os.makedirs(md, exist_ok=True)
json.dump(base, open(gp, "w", encoding="utf-8"))
PLAN = {"schema": "stageplan/1", "stage": "xcw123", "actions": [CW], "context": {"s1_graph": {"path": gp}}}
pp = os.path.join(tmp, "plan_in_xcw123.json")
json.dump(PLAN, open(pp, "w", encoding="utf-8"))
q = lambda *a, **k: None   # noqa: E731
S = SS.simulate(pp, gp, out_root=os.path.join(tmp, "sim"), plan_out_dir=tmp, model_dir=md, log=q)
dst, dff, ex = SX.dry_run(os.path.join(tmp, "plan_xcw123.json"), log=q, model_dir=md, require_final=False)
bo, bd = ex.bind.get("obj") or {}, ex.bind.get("diag") or {}
ls = ex.step(1)["state"]["sym"]
gate("P02 simulate + DRY RUN PASS: case, selector bound to positive uids, both frames bound",
     S["failed"] is None and dst == "PASS" and bo.get(ls["new:C1"], -1) > 0 and bo.get(ls["new:S1"], -1) > 0
     and all(bd.get(ls[k], -1) > 0 for k in ("new:C1.f0", "new:C1.f1")), (S["failed"], dst, str(dff)[:200]))


class FakeS(object):
    work = "C:/fake/work.vi"

    def _op(self, verb, fn, detail=""):
        try:
            return {"verb": verb, "err": None, "result": fn(), "s": 0.0}
        except Exception as x:   # noqa: BLE001
            return {"verb": verb, "err": str(x), "result": None, "s": 0.0}

    def junk_purge(self, tag="", hints=()):
        return None


class FakeG(object):
    def __init__(self, **over):
        self.log, self.tun, self.over = [], {10, 11}, over

    def uids(self, W, cls):
        return set(self.tun) if cls == "Tunnel" else set()

    def case_wired(self, W, dg, node, term, pos=(40, 40), donor=None):
        self.log.append(("case_wired", dg, node, term, tuple(pos)))
        self.tun.add(12)
        r = {"case": 900, "names": ["True", "False"], "frames": [902, 901], "selector_wire": 77, "src_wire": 77,
             "invoke_left": [], "purged": 1}
        r.update(self.over)
        return r


def lvbe(g):
    be = object.__new__(SX.LVBackend)
    be.g, be.s = g, FakeS()
    be.B = type("B", (), {"diag_index": staticmethod(lambda W, d: 3)})()
    be.addr = SX.Addr(None, owners={"20": ["WhileLoop", 100]})
    return be


real = [{"term_uid": 1025, "term_name": "flag", "is_source": True, "wire_uid": 0, "owner_uid": 2, "owner_class": "SubVI",
         "frame_diagram": 20, "term_class": "Terminal"}]
g1 = FakeG()
out = lvbe(g1).create("case_wired", CW, {"diagram": 20, "pos": [40, 40], "src": 1025}, real, {"acts": [1]})
gate("L01 LVBackend 'case_wired': case_wired(W, 20, node 2, 'flag', pos); frames in the PLAN's order by name ([901, 902]); "
     "the one new Tunnel = the selector", g1.log == [("case_wired", 20, 2, "flag", (40, 40))] and out.get("uid") == 900
     and out.get("frames") == [901, 902] and out.get("selector") == 12, (g1.log, out))
e = raises(lambda: lvbe(FakeG(invoke_left=[5])).create("case_wired", CW, {"diagram": 20, "pos": [0, 0], "src": 1025}, real,
                                                        {"acts": [1]}), SX.ExecStop)
gate("L02 NEGATIVE: a junk Invoke left after the verb's purge STOPS", "junk Invoke" in e, e)
e = raises(lambda: lvbe(FakeG(selector_wire=78)).create("case_wired", CW, {"diagram": 20, "pos": [0, 0], "src": 1025}, real,
                                                         {"acts": [1]}), SX.ExecStop)
gate("L03 NEGATIVE: selector wire != source wire STOPS", "selector wire" in e, e)
gate("A01 the 'case' (label) route keeps its verbs; every earlier CREATE_ROUTES key kept",
     SX.ROUTE_VERBS["case"] == [("gscript", "case_in"), ("gscript", "case_frames")]
     and {"while", "for", "local_read", "local_write", "indicator", "control", "primitive", "copy_in", "const_on_term", "queue",
          "subvi", "case"} <= set(SX.CREATE_ROUTES), sorted(SX.CREATE_ROUTES))

bad = [l for l, ok in gates if not ok]
print("=== GATES: %d pass / %d fail%s" % (len(gates) - len(bad), len(bad), "; failing: " + bad[0] if bad else ""), flush=True)
print(protocol.result_line(protocol.make_result(len(gates) - len(bad), len(bad), bad[0] if bad else None, [])), flush=True)
sys.exit(1 if bad else 0)
