r"""selftest_x10_c132_4 - card 132-4 (PD277(a), gate-fp fp-29) self-test of X10's READ-ONLY branch. OFFLINE, no LabVIEW, no COM.
PRIOR ART: selftest_x10_c132_1.py / selftest_x10_c130_1.py (X10 model), stage_prerun.dry / x10_gate / x10_readonly.
PREDICTION: T1 the read-only reader tools/bench/diag_c132_2_graph_p3b1.py, dry-run on the P3a graph (as 132-3) -> X10 PASS,
one modelled run N 0, R 2 (k 0 + 1 read_live call site), peak = start + 2*read + final_read (592.5 MB) <= 690;
T2 a stagekit script that calls s.connect and builds no Executor -> X10 FAIL UNMEASURED ('not read-only', 'connect');
T3 the reader's source with a dry trace carrying a Stage._op -> FAIL UNMEASURED; T4 no trace (old callers) -> FAIL UNMEASURED
(unchanged); T5 a whole-VI read inside a for loop -> FAIL UNMEASURED; T6 discard_work alone is not an edit (reader passes).
    py tools/bgrun.py --material --max-min 6 --log tools/bench/selftest_x10_c132_4.log -- py -u tools/bench/selftest_x10_c132_4.py"""
import builtins, os, sys, tempfile                                                   # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stage_prerun as SP, protocol as P                                           # noqa: E401,E402
res = []


def gate(name, ok, det=""):
    res.append((name, bool(ok)))
    print("{0}  {1}  {2}".format("PASS" if ok else "FAIL", name, str(det)[:900]), flush=True)


def tmp(src):
    fd, p = tempfile.mkstemp(prefix="x10ro_c132_4_", suffix=".py")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(src)
    return p


READER = os.path.join(B, "diag_c132_2_graph_p3b1.py")
GRAPH = os.path.join(B, "graph_ring_p3a_20261001_190155.json")
m = SP.load_memory_model()
v = lambda k: float(m[k]["value"])                                                 # noqa: E731
SP.D.__init__()
try:
    tr = SP.dry(READER, GRAPH)
finally:
    builtins.open = SP.REAL_OPEN
want = round(v("start_mb") + 2 * v("read_mb") + v("final_read_mb"), 1)
ok, det = SP.x10_gate(READER, tr.get("executors"), trace=tr)
runs = det.get("runs") or []
gate("T1 reader dry {0}: X10 PASS, N 0, R 2, peak {1} == {2} <= 690".format(tr.get("status"), runs[0]["peak_mb"] if runs else None, want),
     tr.get("status") == "PASS" and ok is True and len(runs) == 1 and runs[0]["N"] == 0 and runs[0]["R"] == 2
     and runs[0]["peak_mb"] == want and want <= v("fail_above_mb"), det)
ro_ok, ro = SP.x10_readonly(READER, tr)
gate("T6 discard_work alone is no edit: reader is read-only", ro_ok and "discard_work" in open(READER, encoding="utf-8").read(), ro)
EDIT = tmp("import stagekit as K\ns = K.Stage('a', 'b', 'c')\n\ndef body(_):\n    s.start()\n    s.connect(1, 2)\n")
clean = {"executors": [], "ops": [], "first_mutation": None}
ok, det = SP.x10_gate(EDIT, [], trace=clean)
gate("T2 edit-op script without Executor -> FAIL UNMEASURED (not read-only, connect)",
     ok is False and "UNMEASURED" in det.get("why", "") and "not read-only" in det["why"] and "connect" in det["why"], det.get("why"))
ok, det = SP.x10_gate(READER, [], trace=dict(clean, ops=["connect"], first_mutation="Stage._op connect"))
gate("T3 reader source + a dry Stage._op -> FAIL UNMEASURED", ok is False and "UNMEASURED" in det.get("why", "")
     and "Stage._op" in det["why"], det.get("why"))
ok, det = SP.x10_gate(READER, [])
gate("T4 no trace (old callers) -> FAIL UNMEASURED, unchanged", ok is False and det.get("why", "").startswith("UNMEASURED")
     and "not read-only" not in det["why"], det.get("why"))
LOOP = tmp("import stagekit as K\nimport wiki_build as W\n\ndef body(_):\n    for p in range(3):\n        W.read_live(p)\n")
ok, det = SP.x10_gate(LOOP, [], trace=clean)
gate("T5 whole-VI read inside a loop -> FAIL UNMEASURED", ok is False and "inside a loop" in det.get("why", ""), det.get("why"))
for p in (EDIT, LOOP):
    os.remove(p)
npass, nfail = sum(1 for _n, c in res if c), sum(1 for _n, c in res if not c)
print(P.result_line(P.make_result(npass, nfail, next((n for n, c in res if not c), None))), flush=True)
sys.stdout.flush()
os._exit(1 if nfail else 0)
