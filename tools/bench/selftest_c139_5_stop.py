r"""selftest_c139_5_stop - card 139-5 pass 1/3 (offline, no LabVIEW, no COM): the STOP route onto an EXISTING (base) While
loop's conditional terminal, `dst {"uid": <loop uid>, "term": "cond"}` (stagexec.base_cond + compile_plan + check_symbols,
stagesim.cond_target), plus the older self-tests of stagesim re-run with their counts.
Found before writing: the plan-made form 'new:W1.cond' -> kind 'stop' (stagexec.compile_plan, card 100-3 R8; self-test T36b)
and stagesim.cond_target/cond_row/op_wire (card 101-3; G45); LVBackend.stop / the dry backend's stop take ANY loop uid
(stagexec.py LVBackend.stop, OpStopFromNode_v0 by WhileLoop index). Nothing addressed a base loop's cond.
PREDICTION CONTRACT (all PASS):
  C1 plan-made While form unchanged: compile -> [create while, create local_read, stop loop 'new:DL1'];
  C2 {uid:100, term:cond} -> one op kind 'stop' loop 100 (int); C2b uid '100' (digit string) -> loop 100;
  C3 malformed {uid, term:cond, term_uid} -> ExecStop at check_symbols (names the action); C4 base cond as a SOURCE -> ExecStop;
  S1 sim: base While #100 (body 20, + an unnamed Diagram-owned sink row = its cond) <- 2.out (body 20): cond_of 100,
     dst_term = the cond row, how 'branch' (2.out already wired);  S2 the same row already wired -> SimError 'already wired';
  S3 {uid:1 (Constant), term:cond} -> SimError (not a While);  S4 a source on diagram 10 -> SimError (not on the body);
  S5 'new:DL1.cond' (plan-made) still cond_of the new loop;
  O1 `py tools/stagesim.py selftest` PASS with fail 0 (last count 105, stagesim_selftest_c133_1.log:110);
  O2 selftest_stagesim_fsexit_c138_1.py PASS 14/0 (selftest_stagesim_fsexit_c138_1.log:43).
    py tools/bgrun.py --material --max-min 10 --log tools/bench/selftest_c139_5_stop.log -- py -u tools/bench/selftest_c139_5_stop.py"""
import copy, json, os, re, subprocess, sys                                                  # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagesim as SS  # noqa: E402
import stagexec as SX  # noqa: E402
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:400]), flush=True)


def refuses(fn, exc, text):
    try:
        fn()
    except exc as e:
        return text in str(e), str(e)[:200]
    return False, "no exception"


LOC = {"op": "create", "id": "lr", "class": "Local", "diagram": "new:DL1.body", "as": "LR1", "label": "Stop", "mode": "read",
       "pos": [5, 5], "terminals": [{"name": "Stop", "is_source": True}]}
mk = {"op": "create", "id": "dl", "class": "WhileLoop", "diagram": 10, "as": "DL1", "pos": [0, 0]}
ops = SX.compile_plan({"actions": [mk, LOC, {"op": "wire", "id": "stop", "src": "new:LR1.value", "dst": "new:DL1.cond"}]})
got = [(o["kind"], o.get("route"), o.get("loop")) for o in ops]
gate("C1 plan-made While form unchanged", got == [("create", "while", None), ("create", "local_read", None), ("stop", None, "new:DL1")], got)
o2 = SX.compile_plan({"actions": [{"op": "wire", "id": "s", "src": "2.out", "dst": {"uid": 100, "term": "cond"}}]})
gate("C2 base form {uid:100, term:cond} -> stop loop 100", [(o["kind"], o.get("loop"), o["acts"]) for o in o2] == [("stop", 100, [1])], o2)
o2b = SX.compile_plan({"actions": [{"op": "wire", "id": "s", "src": "2.out", "dst": {"uid": "100", "term": "cond"}}]})
gate("C2b digit-string uid -> stop loop 100 (int)", [(o["kind"], o.get("loop")) for o in o2b] == [("stop", 100)], o2b)
ok3, m3 = refuses(lambda: SX.check_symbols([{"op": "wire", "id": "bad", "src": "2.out", "dst": {"uid": 23166, "term": "cond", "term_uid": 23246}}]),
                  SX.ExecStop, "action 1 (bad)")
gate("C3 malformed base cond (term_uid beside it) refused at check_symbols", ok3, m3)
ok4, m4 = refuses(lambda: SX.compile_plan({"actions": [{"op": "wire", "id": "src", "src": {"uid": 100, "term": "cond"}, "dst": "4.y"}]}),
                  SX.ExecStop, "is a sink")
gate("C4 base cond as a wire SOURCE refused", ok4, m4)


def state(wired=False):
    g = SS._synthetic()
    g["terminals"].append({"term_uid": 1099, "term_name": "", "is_source": False, "wire_uid": 9 if wired else 0, "owner_uid": 20,
                           "owner_class": "Diagram", "frame_diagram": 20, "term_class": "Terminal"})
    if wired:
        g["terminals"].append({"term_uid": 1098, "term_name": "", "is_source": True, "wire_uid": 9, "owner_uid": 20,
                               "owner_class": "Diagram", "frame_diagram": 20, "term_class": "Terminal"})
    # the bed graphs carry `owners` (graph_ring_p3b2b: owners['23166'] = ['WhileLoop', 10170], prep_c139_5_probe.log:4); the
    # synthetic toy has none, so the fixture states the one it needs (run 1 of this self-test: body list [] without it)
    g["owners"] = {"20": ["WhileLoop", 100], "30": ["WhileLoop", 200]}
    return SS.base_state(g)


WP = dict(SS.PROVISIONAL["wire"]["params"])
st = state()
gate("S0 synthetic: body 20 is owned by While #100", (st.get("owners") or {}).get("20") == ["WhileLoop", 100], (st.get("owners") or {}).get("20"))
e1, _c = SS.op_wire(st, {"src": "2.out", "dst": {"uid": 100, "term": "cond"}}, WP, None, {})
cr = [r for r in st["terminals"] if r["term_uid"] == 1099]
gate("S1 base While #100 cond <- 2.out: cond_of 100, dst t1099, branch, row wired",
     e1.get("cond_of") == 100 and e1.get("dst_term_uid") == 1099 and e1.get("how") == "branch" and cr[0]["wire_uid"] == 6, e1)
ok, m = refuses(lambda: SS.op_wire(state(True), {"src": "2.out", "dst": {"uid": 100, "term": "cond"}}, WP, None, {}), SS.SimError, "already wired")
gate("S2 cond row already wired -> SimError", ok, m)
ok, m = refuses(lambda: SS.op_wire(state(), {"src": "2.out", "dst": {"uid": 1, "term": "cond"}}, WP, None, {}), SS.SimError, "conditional terminal")
gate("S3 '.cond' of a non-While (Constant #1) -> SimError", ok, m)
ok, m = refuses(lambda: SS.op_wire(state(), {"src": "1.v", "dst": {"uid": 100, "term": "cond"}}, WP, None, {}), SS.SimError, "not on the loop's body")
gate("S4 source on diagram 10 (not body 20) -> SimError", ok, m)
s5 = state()
SS.op_create(s5, copy.deepcopy(mk), {}, None, {})
SS.op_create(s5, copy.deepcopy(LOC), {}, None, {})
e5, _c = SS.op_wire(s5, {"src": "new:LR1.value", "dst": "new:DL1.cond"}, WP, None, {})
gate("S5 plan-made 'new:DL1.cond' still cond_of the new loop", e5.get("cond_of") == s5["sym"]["new:DL1"], e5)


def run(args, label, want=None):
    p = subprocess.run([sys.executable, "-u"] + args, cwd=ROOT, capture_output=True, text=True, timeout=420)
    rl = [ln for ln in p.stdout.splitlines() if ln.startswith("RESULT {")]
    r = json.loads(rl[-1][7:]) if rl else {}
    gs = r.get("gates") or {}
    fails = [ln for ln in p.stdout.splitlines() if re.search(r"\bFAIL\b", ln)][:5]
    print("RUN", label, "rc", p.returncode, "gates", gs, "first_fail", r.get("first_fail"), fails, flush=True)
    gate("{0} PASS, fail 0 (pass {1})".format(label, gs.get("pass")), p.returncode == 0 and gs.get("fail") == 0 and
         (want is None or gs.get("pass") == want), (gs, p.stderr[-300:]))


run(["tools/stagesim.py", "selftest"], "O1 stagesim selftest")
run(["tools/bench/selftest_stagesim_fsexit_c138_1.py"], "O2 selftest_stagesim_fsexit_c138_1", 14)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(0 if not G["fail"] else 1)
