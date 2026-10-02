r"""selftest_x10_c136_2 - card 136-2 (gate-fp fp-33) self-test of X10's EDIT-DIAGNOSTIC branch (stage_prerun.x10_edit). OFFLINE,
no LabVIEW, no COM. PRIOR ART: selftest_x10_c132_4.py (read-only branch), selftest_x10_c130_1.py / _c132_1.py (Executor model).
PREDICTION: E1 edit trace (26 ops, 5 executed reads, opened VI md5 49cf7f77 = measured load 605.0) -> X10 PASS, one run N 26,
R 6, start 610.9 (605.0 + op-0 5.9), peak = 610.9 + 6*2.53 + 26*1.38 + 17.4 = 679.4 <= 690; E2 the same with 60 ops -> X10 FAIL,
peak 726.3, NOT UNMEASURED; E3 opened VI load unmeasured (md5 0*32) -> FAIL UNMEASURED 'load unmeasured'; E4 no x10_reads in the
trace -> FAIL UNMEASURED; E5 no ops (T2 shape) -> FAIL UNMEASURED, no 'edit model' text; E6 dry of diag_c136_1_routes.py on
graph_ring_p3b2b: 26 ops, x10_reads a list, X10 = whatever is measured (printed, not asserted beyond the model's terms).
    py tools/bgrun.py --material --max-min 6 --log tools/bench/selftest_x10_c136_2.log -- py -u tools/bench/selftest_x10_c136_2.py"""
import builtins, os, sys, tempfile                                                   # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stage_prerun as SP, protocol as P                                           # noqa: E401,E402
res = []


def gate(name, ok, det=""):
    res.append((name, bool(ok)))
    print("{0}  {1}  {2}".format("PASS" if ok else "FAIL", name, str(det)[:900]), flush=True)


fd, EDIT = tempfile.mkstemp(prefix="x10ed_c136_2_", suffix=".py")
with os.fdopen(fd, "w", encoding="utf-8") as f:
    f.write("import stagekit as K\ns = K.Stage('a', 'b', 'c')\n\ndef body(_):\n    s.start()\n    s.connect(1, 2)\n")
m = SP.load_memory_model()
v = lambda k: float(m[k]["value"])                                                 # noqa: E731
MD5 = "49cf7f770fc331e06607687af640ad5e"
st = round(float(m["load_by_vi"][MD5]["value"]) + v("op0_read_mb"), 1)
base = {"executors": [], "ops": ["connect_term_uid"] * 26, "first_mutation": "Stage._op connect_term_uid",
        "input_md5": MD5, "x10_reads": ["Stage.uid_index"] * 5}


def peak(n, r):
    return round(st + r * v("read_mb") + n * (v("edit_mb") + v("other_mb")) + v("final_read_mb"), 1)


ok, det = SP.x10_gate(EDIT, [], trace=base)
r = (det.get("runs") or [{}])[0]
gate("E1 edit trace modelled: PASS N 26 R 6 start {0} peak {1} == {2} <= 690".format(r.get("start_mb"), r.get("peak_mb"), peak(26, 6)),
     ok is True and len(det["runs"]) == 1 and r.get("N") == 26 and r.get("R") == 6 and r.get("start_mb") == st
     and r.get("peak_mb") == peak(26, 6) <= v("fail_above_mb") and r.get("edit") is True, det)
ok, det = SP.x10_gate(EDIT, [], trace=dict(base, ops=["connect_term_uid"] * 60))
r = (det.get("runs") or [{}])[0]
gate("E2 over limit: FAIL peak {0} == {1} > 690, not UNMEASURED".format(r.get("peak_mb"), peak(60, 6)),
     ok is False and r.get("peak_mb") == peak(60, 6) > v("fail_above_mb") and "UNMEASURED" not in (det.get("why") or ""), det)
ok, det = SP.x10_gate(EDIT, [], trace=dict(base, input_md5="0" * 32))
gate("E3 opened VI load unmeasured -> FAIL UNMEASURED", ok is False and "UNMEASURED" in det.get("why", "")
     and "load unmeasured" in det["why"] and not det.get("runs"), det.get("why"))
nr = dict(base)
nr.pop("x10_reads")
ok, det = SP.x10_gate(EDIT, [], trace=nr)
gate("E4 no whole-VI read count in the trace -> FAIL UNMEASURED", ok is False and "UNMEASURED" in det.get("why", "")
     and "x10_reads" in det["why"], det.get("why"))
ok, det = SP.x10_gate(EDIT, [], trace=dict(base, ops=[], first_mutation=None))
gate("E5 no ops (old T2 shape) -> FAIL UNMEASURED, no edit-model text", ok is False and "UNMEASURED" in det.get("why", "")
     and "edit model" not in det["why"], det.get("why"))
ROUTES = os.path.join(B, "diag_c136_1_routes.py")
GRAPH = os.path.join(B, "graph_ring_p3b2b_20261002_133824.json")
SP.D.__init__()
try:
    tr = SP.dry(ROUTES, GRAPH)
finally:
    builtins.open = SP.REAL_OPEN
ok, det = SP.x10_gate(ROUTES, tr.get("executors"), trace=tr)
gate("E6 dry of diag_c136_1_routes {0}: ops {1}, x10_reads {2} (X10 {3}: {4})".format(
    tr.get("status"), len(tr.get("ops") or []), len(tr.get("x10_reads") or []) if isinstance(tr.get("x10_reads"), list) else None,
    ok, det.get("why") or det.get("runs")), tr.get("status") == "PASS" and len(tr.get("ops") or []) == 26
     and isinstance(tr.get("x10_reads"), list), det)
os.remove(EDIT)
npass, nfail = sum(1 for _n, c in res if c), sum(1 for _n, c in res if not c)
print(P.result_line(P.make_result(npass, nfail, next((n for n, c in res if not c), None))), flush=True)
sys.stdout.flush()
os._exit(1 if nfail else 0)
