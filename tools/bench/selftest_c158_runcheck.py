# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_158-a1-2.md
# ---
r"""selftest_c158_runcheck - card 158-a1-2 (docs/d1/ring-p5.md PD384(b)), OFFLINE on recorded data (no LabVIEW, no COM).
Shared functions under test (stagexec): move_in_runs, checkpoint_ops (called by stagekit.RingSession), run_fate_lines (called by
Executor.run at a run-closing checkpoint read), the Executor's CHECKPOINT refusal, dry_run(checkpoints=...).
Data: plan_ring_p5s02a.json 4284c22a and its sim steps tools/bench/sim/ring_p5s02a/.
WHAT EXISTED FIRST: selftest_c157_innerface.py (the FATE dry run on p5s02a and the six M3 wires, its expected rows are the ones
below); stagexec T35/T40b (checkpoint-set refusal of binding/last ops); prep_c158_a1_1_regress.closers (independent closer rule).
PREDICTION (gates):
 R1  move_in_runs(p5s02a) == [(10, 11, 12)]; checkpoint_ops(p5s02a) == (0,1,3,6,8,9,12,15,16,17).
 R2  synthetic op lists: [move_in, connect, move_in, move_in] -> runs [(1,), (3, 4)], checkpoints (0, 1, 4);
     [connect, move_in] -> runs [(2,)], checkpoints (0, 2).
 S1  set missing 12, NON-collecting sim backend: dry FAIL 'CHECKPOINT: ...' naming 12, no op dispatched (backend calls == 0).
 S2  set missing 17 (the last op), same: FAIL 'CHECKPOINT' naming 17, calls == 0.
 S3  set missing 12, collecting (dry) backend: one pre-op CHECKPOINT row naming 12; status FAIL.
 E1  dry_run with the full set: PASS; whole reads exactly at ops 1,3,6,8,9,12,15,16,17; skipped 2,4,5,7,10,11,13,14.
 E2  run_fate_lines called ONCE, at op 12 (the Executor's current op), with run (10, 11, 12); six FATE lines, all step=10,
     wires {10394, 24091, 24153, 24285, 24312, 24330} (the six M3 wires) with the c157 F2 sources/sinks.
 E3  no FATE-UNREAD line in E1's log nor in the every-op dry run (checkpoints None), which also logs the same six lines once.
 E4  run_fate_lines((10,11,12)) on the recorded step_12 terminals == the six lines (sink_term 5772/5787/5778/5683/5782/5760).
 P   pins: stagesim 95a162ba (re-pinned 160-a2-1 from a3261b56; 160-a1-1 from eb99c6ba), addrcheck 207beb0d, stage_prerun 7605116f (re-pinned 159-f1-1 from 9decb20f), plan 4284c22a.
Usage: py tools/bgrun.py --material --max-min 10 --log tools/bench/selftest_c158_runcheck.log -- py -u tools/bench/selftest_c158_runcheck.py"""
import hashlib
import inspect
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402
import stagexec as SX  # noqa: E402

G = {"pass": 0, "fail": 0, "first": None}
PLAN = os.path.join(HERE, "plan_ring_p5s02a.json")
WANT_CP = (0, 1, 3, 6, 8, 9, 12, 15, 16, 17)
M3 = {10394: (3060, 5772), 24091: (25235, 5787), 24153: (24367, 5778), 24285: (24190, 5683), 24312: (24288, 5782),
      24330: (24360, 5760)}   # wire -> (src_term, sink_term), selftest_c157_innerface.py:144-145


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(d)[:700]), flush=True)


def md5(rel):
    with open(os.path.join(ROOT, rel), "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def jl(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


P = jl(PLAN)
OPS = SX.compile_plan(P)
STEPS = dict((int(s["n"]), os.path.join(ROOT, s["path"])) for s in P["finalized"]["step_files"])
step_of = lambda n: jl(STEPS[n])                                                   # noqa: E731


def fate_ok(lines):
    """six lines, all step=10, wires/sources/sinks == M3."""
    got = {}
    for ln in lines:
        f = dict(x.split("=", 1) for x in ln.split()[1:])
        got[int(f["wire"])] = (f["step"], int(f["src_term"]), f["sink_term"])
    return len(lines) == 6 and got == dict((w, ("10", s, str(t))) for w, (s, t) in M3.items())


print("---------- (i) run-closing checkpoint rule", flush=True)
runs = SX.move_in_runs(OPS)
gate("R1 p5s02a move_in_runs == [(10, 11, 12)], checkpoint_ops == {0}".format(WANT_CP),
     runs == [(10, 11, 12)] and SX.checkpoint_ops(OPS) == WANT_CP, (runs, SX.checkpoint_ops(OPS)))
mk = lambda *ks: [{"kind": k} for k in ks]                                         # noqa: E731
a, b = mk("move_in", "connect", "move_in", "move_in"), mk("connect", "move_in")
gate("R2 synthetic: runs [(1,),(3,4)] cp (0,1,4); runs [(2,)] cp (0,2)",
     SX.move_in_runs(a) == [(1,), (3, 4)] and SX.checkpoint_ops(a) == (0, 1, 4)
     and SX.move_in_runs(b) == [(2,)] and SX.checkpoint_ops(b) == (0, 2),
     (SX.move_in_runs(a), SX.checkpoint_ops(a), SX.move_in_runs(b), SX.checkpoint_ops(b)))

print("---------- (ii) the Executor refuses a set lacking a run-closing / last op before op 1", flush=True)


class StrictBE(SX.SimBackend):
    """The dry backend made NON-collecting (unroutable is not a list): pre-op checks raise, as on the real backend."""

    def __init__(self, *a_, **k_):
        super(StrictBE, self).__init__(*a_, **k_)
        self.unroutable = ()


def dry(cps, be_cls=None):
    log = []
    orig = SX.SimBackend
    if be_cls is not None:
        SX.SimBackend = be_cls
    try:
        st, ff, ex = SX.dry_run(PLAN, log=log.append, checkpoints=cps)
    finally:
        SX.SimBackend = orig
    return st, ff, ex, log


for lab, miss in (("S1", 12), ("S2", 17)):
    st, ff, ex, _ = dry(set(WANT_CP) - {miss}, StrictBE)
    gate("{0} set missing {1}, non-collecting sim backend: FAIL 'CHECKPOINT' naming {1}, no op dispatched".format(lab, miss),
         st == "FAIL" and str(ff).startswith("CHECKPOINT") and "[{0}]".format(miss) in str(ff) and len(ex.be.calls) == 0,
         (st, str(ff)[:300], len(ex.be.calls)))
st, ff, ex, _ = dry(set(WANT_CP) - {12})
pre = [r for r in ex.pre_op_fails if r["err"].startswith("CHECKPOINT")]
gate("S3 set missing 12, collecting dry backend: one pre-op CHECKPOINT row naming 12; FAIL", st == "FAIL" and len(pre) == 1
     and "[12]" in pre[0]["err"], (st, [r["err"] for r in pre]))

print("---------- (iii)/(iv) FATE lines of ops 10-12 from the op-12 read", flush=True)
CALLS = []
_orig_rfl = SX.run_fate_lines


def spy(run, ops, step_of_, read_rows, bind_term=None):
    CALLS.append((tuple(run), inspect.currentframe().f_back.f_locals.get("k")))
    return _orig_rfl(run, ops, step_of_, read_rows, bind_term)


SX.run_fate_lines = spy
try:
    st1, ff1, ex1, log1 = dry(set(WANT_CP))
    st0, ff0, ex0, log0 = dry(None)
finally:
    SX.run_fate_lines = _orig_rfl
f1 = [x.strip() for x in log1 if x.strip().startswith("FATE ")]
f0 = [x.strip() for x in log0 if x.strip().startswith("FATE ")]
gate("E1 full set: PASS; reads at 1,3,6,8,9,12,15,16,17; skipped 2,4,5,7,10,11,13,14", st1 == "PASS"
     and sorted(ex1.reads_real) == [1, 3, 6, 8, 9, 12, 15, 16, 17] and sorted(ex1.reads_skipped) == [2, 4, 5, 7, 10, 11, 13, 14],
     (st1, str(ff1)[:200], ex1.reads_real, ex1.reads_skipped))
gate("E2 run_fate_lines called once per run, at op 12, run (10,11,12); six FATE lines step=10 == the six M3 wires",
     CALLS[:1] == [((10, 11, 12), 12)] and fate_ok(f1), {"calls": CALLS, "fate": f1})
for ln in f1:
    print("  " + ln, flush=True)
gate("E3 no FATE-UNREAD (full set, every-op run); every-op run: PASS, the same six lines once",
     not [x for x in log1 + log0 if "FATE-UNREAD" in x] and st0 == "PASS" and sorted(f0) == sorted(f1)
     and CALLS[1:] == [((10, 11, 12), 12)], {"calls": CALLS, "st0": st0, "f0": f0})
rec = SX.run_fate_lines((10, 11, 12), OPS, step_of, step_of(12)["state"]["terminals"])
gate("E4 run_fate_lines on the recorded step_12 terminals: the six M3 lines", fate_ok(rec), rec)

PINS = {"tools/stagesim.py": "95a162ba", "tools/addrcheck.py": "207beb0d", "tools/stage_prerun.py": "7605116f",
        "tools/bench/plan_ring_p5s02a.json": "4284c22a"}
got = dict((k, md5(k)[:8]) for k in PINS)
gate("P pins unchanged", got == PINS, got)
print("FACT md5 stagexec {0} stagekit {1}".format(md5("tools/stagexec.py"), md5("tools/stagekit.py")), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(0 if not G["fail"] else 1)
