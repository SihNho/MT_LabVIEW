r"""selftest_gateclass_s2 - card chat-S2 (PD327): the STOP vs LOG-only gate table (tools/gateclass.py) and its four users.
OFFLINE, no LabVIEW, no COM: stagekit.Stage.gate is exercised by compiling its SOURCE (AST) into a namespace with a fake self,
so gscript is never imported; stagexec.bind_new / guard_peer.log_failure / census_predict.predict are pure.
Every soft-log write goes to a temp file (GATE_SOFT_LOG), never to tools/bench/gate_soft_log.jsonl.

PREDICTION CONTRACT (each one gate):
 G1 semantic +1 stops (count_verdict Function/Wire/ControlTerminal/DigitalNumericConstant/WhileLoop/LoopTunnel +1)
 G2 non-semantic +3 logs (Terminal 12 vs 9; InnerTerminal 7 vs 4)
 G3 non-semantic +40 % beyond max(5, 25 %) stops (Terminal 42 vs 30), and tolerance(30) == 8, tolerance(4) == 5
 G4 a name mismatch logs (NG / NAME-GATE / BINDING-NAME labels)
 G5 a STOP gate stops (FR, E3, PRIM, PB, D, an unknown label) even with a census-shaped detail
 G6 TD: the 141-2 detail (unwired [], lost 6 vs deletes 8) logs; the same with one unwired terminal stops
 G7 Stage.gate (source of tools/stagekit.py): a CEN2 Terminal +3 gate returns True, is in softs not fails, writes ONE soft line,
    prints SOFT not FAIL; a CEN2 Function +1 gate is a FAIL; a fatal LOG-only gate does NOT raise; a fatal STOP gate raises
 G8 stagexec.bind_new: FSOT keys differing ONLY by name bind by (class, direction) + one soft line; a repeated name-free key stops
 G9 guard_peer.log_failure: soft-only log -> no review owed; mixed log (soft + STOP line) -> review owed; soft + exception -> owed
 G10 census_predict.predict: a non-semantic class within tolerance is SOFT and the overall verdict is not FAIL
 G11 errorlist_verdict: loose ends +2 logs, a non-loose-end extra stops
"""
import ast
import io
import json
import os
import sys
import tempfile
import contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TMP = tempfile.mkdtemp(prefix="s2gc_")
SOFT = os.path.join(TMP, "soft.jsonl")
os.environ["GATE_SOFT_LOG"] = SOFT
os.environ["GATE_CARD"] = "chat-S2-selftest"
for p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "hooks")):
    sys.path.insert(0, p)
import gateclass as GC                                                 # noqa: E402
import protocol                                                        # noqa: E402

P, F = [], []


def gate(label, ok, det=""):
    (P if ok else F).append(label)
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(det)[:300]), flush=True)


def nsoft():
    return sum(1 for _ in open(SOFT, encoding="utf-8")) if os.path.exists(SOFT) else 0


# G1-G3
sem = [GC.count_verdict(c, 1, 0)[0] for c in ("Function", "Wire", "ControlTerminal", "DigitalNumericConstant", "WhileLoop",
                                                "LoopTunnel")]
gate("G1 semantic +1 stops", sem == ["stop"] * 6, sem)
ns = [GC.count_verdict("Terminal", 12, 9)[0], GC.count_verdict("InnerTerminal", 7, 4)[0]]
gate("G2 non-semantic +3 logs", ns == ["log", "log"], ns)
gate("G3 non-semantic +40% stops; tolerance(30)=8, tolerance(4)=5",
     GC.count_verdict("Terminal", 42, 30)[0] == "stop" and GC.tolerance(30) == 8 and GC.tolerance(4) == 5,
     (GC.count_verdict("Terminal", 42, 30), GC.tolerance(30), GC.tolerance(4)))
# G4-G5
nm = [GC.classify_gate(x)["verdict"] for x in ("NG every crossing op's NEW tunnel names == the simulator's", "NAME-GATE",
                                                 "BINDING-NAME FSOT")]
gate("G4 a name mismatch logs", nm == ["log"] * 3, nm)
cen = {"measured": {"Terminal": 12}, "declared": {"Terminal": 9}}
st = [GC.classify_gate(x, cen)["verdict"] for x in ("FR the 8 created objects", "E3 (PD217(c))", "PRIM created node",
                                                       "PB frame-keyed cdiff", "D new wires", "WHATEVER unknown gate")]
gate("G5 a STOP gate stops (also with a census-shaped detail)", st == ["stop"] * 6, st)
# G6 TD, the 141-2 detail verbatim (diag_c141_p4s01_scratch.log:280)
td = {'unwired': [], 'lost_rows': [27997, 28018, 28030, 28973, 28983, 28989],
      'plan_deletes': [27997, 28004, 28018, 28030, 28973, 28979, 28983, 28989]}
td_line = "  FAIL  TD every base terminal the sim keeps wired is still wired; rows lost == the plan's deletes  " + repr(td)
td2 = dict(td, unwired=[12345])
gate("G6 TD 141-2 logs; with an unwired terminal stops",
     GC.classify_gate("TD every base terminal", td)["verdict"] == "log" and GC.classify_line(td_line) == "log"
     and GC.classify_gate("TD x", td2)["verdict"] == "stop", (GC.classify_gate("TD", td)["rule"], GC.classify_gate("TD", td2)["rule"]))

# G7 Stage.gate from SOURCE
src = open(os.path.join(ROOT, "tools", "stagekit.py"), encoding="utf-8").read()
fn = next(n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.FunctionDef) and n.name == "gate"
          and n.args.args and n.args.args[0].arg == "self")


class Stop(Exception):
    pass


ns_ = {"_gateclass": GC, "_a": lambda t: str(t), "Stop": Stop}
exec(compile(ast.Module(body=[fn], type_ignores=[]), "stagekit.gate", "exec"), ns_)
SG = ns_["gate"]


class FakeStage(object):
    def __init__(self):
        self.passes, self.fails, self.softs = [], [], []


s = FakeStage()
n0 = nsoft()
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    r1 = SG(s, "CEN2 new-object census", False, {"measured": {"Terminal": 12}, "declared": {"Terminal": 9},
                                                "diff (measured, declared)": {"Terminal": (12, 9)}}, kind="census")
    r2 = SG(s, "CEN2 new-object census semantic", False, {"measured": {"Function": 1}, "declared": {}}, kind="census")
    r3 = SG(s, "NG names", False, {"sim": ["a"], "real": ["b"]}, fatal=True)
    raised = False
    try:
        SG(s, "FR frames", False, "x", fatal=True)
    except Stop:
        raised = True
out = buf.getvalue()
gate("G7 Stage.gate: soft CEN2 -> True/softs/1 line/SOFT print; semantic -> FAIL; fatal LOG-only no raise; fatal STOP raises",
     r1 is True and r2 is False and r3 is True and raised and s.softs == ["CEN2 new-object census", "NG names"]
     and s.fails == ["CEN2 new-object census semantic", "FR frames"] and nsoft() - n0 == 2
     and "  SOFT  CEN2 new-object census" in out and "  FAIL  CEN2 new-object census semantic" in out,
     (r1, r2, r3, raised, s.softs, s.fails, nsoft() - n0))

# G8 stagexec.bind_new
import stagexec as SX                                                  # noqa: E402


def row(t, o, cls, tc, src_, name):
    return {"term_uid": t, "owner_uid": o, "owner_class": cls, "term_class": tc, "is_source": src_, "term_name": name,
            "wire_uid": 0, "frame_diagram": 0}


sim = [row(-11, -10, "FlatSequenceOuterTunnel", "Terminal", False, ""), row(-12, -10, "FlatSequenceOuterTunnel", "Terminal", True, "")]
real = [row(501, 500, "FlatSequenceOuterTunnel", "Terminal", False, "Image Out"),
        row(502, 500, "FlatSequenceOuterTunnel", "Terminal", True, "Image Out")]
b = {"obj": {}, "term": {}, "diag": {}}
n0 = nsoft()
try:
    made = SX.bind_new([], real, [], sim, b)
    e8 = None
except SX.ExecStop as e:
    made, e8 = None, str(e)
sim2 = sim + [row(-13, -10, "FlatSequenceOuterTunnel", "Terminal", False, "")]
real2 = real + [row(503, 500, "FlatSequenceOuterTunnel", "Terminal", False, "x")]
try:
    SX.bind_new([], real2, [], sim2, {"obj": {}, "term": {}, "diag": {}})
    e8b = None
except SX.ExecStop as e:
    e8b = str(e)
gate("G8 bind_new: name-only FSOT difference binds by (class, direction) + 1 soft line; repeated name-free key stops",
     made == {-10: 500} and b["term"] == {-11: 501, -12: 502} and nsoft() - n0 == 1 and e8b and "BINDING" in e8b,
     (made, e8, b["term"], nsoft() - n0, (e8b or "")[:120]))

# G9 guard_peer.log_failure
import guard_peer as GP                                                # noqa: E402
HDR = "BGRUN START 2026-10-03 01:00:00 limit 5.0 min: py -u tools/recipes/stage_x.py\nBGRUN PID 1\n"
soft_log = (HDR + "  PASS  L0 plan\n" + td_line + "\n=== GATES: 1 pass / 1 fail; failing: TD every\n"
            'RESULT {"schema":"result-line/1","status":"FAIL","gates":{"pass":1,"fail":1},"first_fail":"TD every","artefacts":[]}\n'
            "BGRUN END rc=1 after 5s\n")
mixed = soft_log.replace("  PASS  L0 plan\n", "  FAIL  FR the 8 created objects  {'on': []}\n").replace(
    '"pass":1,"fail":1', '"pass":0,"fail":2')
exc = soft_log.replace("  PASS  L0 plan\n", "  PASS  L0 plan\nOBSERVED EXC boom\n")
v = [GP.log_failure(soft_log)[0], GP.log_failure(mixed)[0], GP.log_failure(exc)[0]]
gate("G9 guard_peer: soft-only log -> no review owed; mixed -> owed; soft + exception -> owed", v == [False, True, True], v)

# G10 census_predict
import census_predict as CP                                            # noqa: E402
samples = {"classes_measured": ["Terminal", "Function"], "ops": {}}
rep = CP.predict({"actions": []}, {"census": {"Terminal": 3}}, samples)
pc = dict((p["class"], p["verdict"]) for p in rep["classes"])
rep2 = CP.predict({"actions": []}, {"census": {"Function": 1}}, samples)
gate("G10 census_predict: Terminal derived 0 vs declared +3 is SOFT, overall not FAIL; Function 0 vs 1 is FAIL",
     pc.get("Terminal") == "SOFT" and rep["overall"] != "FAIL" and rep2["overall"] == "FAIL", (pc, rep["overall"], rep2["overall"]))

# G11 Error List
e1 = GC.errorlist_verdict(["Wire: Wire has loose ends", "Wire: Wire has loose ends"], [], 10)
e2 = GC.errorlist_verdict(["Insert Into Array: Contains unwired or bad terminal"], [], 51)
gate("G11 Error List: loose ends +2 logs; a non-loose-end extra stops", e1[0] == "log" and e2[0] == "stop", (e1, e2))

recs = [json.loads(x) for x in open(SOFT, encoding="utf-8")] if os.path.exists(SOFT) else []
gate("G12 every soft line carries cycle/card/script/gate/expected/measured/class/rule",
     recs and all(set(("cycle", "card", "script", "gate", "expected", "measured", "class", "rule")) <= set(r) for r in recs),
     len(recs))
print("=== GATES: {0} pass / {1} fail".format(len(P), len(F)))
print(protocol.result_line(protocol.make_result(len(P), len(F), F[0] if F else None)))
sys.exit(0 if not F else 1)
