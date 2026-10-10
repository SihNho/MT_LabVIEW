# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_161-a1-1.md
# ---
r"""selftest_c161_delckpt - card 161-a1-1 (docs/d1/ring-p5b.md PD393(a)), OFFLINE (no LabVIEW, no COM): every delete_wire op is a
REQUIRED executor checkpoint.
Shared functions under test (stagexec): required_checkpoints (the one rule), checkpoint_ops (= {0} | required_checkpoints; called by
stagekit.RingSession), the Executor's CHECKPOINT refusal (run(), same rule), dry_run(checkpoints=...).
WHAT EXISTED FIRST: selftest_c158_runcheck.py (StrictBE / dry() pattern reused here as the same calls, S1-S3 refusal gates),
stagexec self-test T35/T40 (binding/last refusal). Data: plan_ring_p5s02b.json f4520b10 (+ pred a1fd43fb), plan_ring_p5s01a/
p5s01b/p5s02a.json and their preds (stored sets = pred memory_pred.checkpoints and e1.checkpoints[].op).
PREDICTION (gates):
 (first run, selftest_c161_delckpt.log: the compiled p5s02b op list has THREE delete_wire ops, 1, 4 and 8 - the brief named 4 and
  8; the decided rule 'every delete_wire op' makes op 1 required too, so the predictions below carry 1.)
 D1  p5s02b compiles to 10 ops; delete_wire ops == [1, 4, 8].
 D2  checkpoint_ops(p5s02b) == (0,1,2,3,4,5,7,8,9,10) == stored pred sets == x10 record == old (0,2,3,5,7,9,10) | {1,4,8}.
 V1  non-collecting dry, set (0,1,2,3,4,5,7,8,9,10): no CHECKPOINT stop (accepted).
 V2/V3/V5  that set without op 4 / 8 / 1: FAIL 'CHECKPOINT' naming [4] / [8] / [1] and 'delete_wire op(s) not in the set: [..]',
     0 backend calls.
 V4  the OLD stored p5s02b set (0,2,3,5,7,9,10): FAIL 'CHECKPOINT' naming [1, 4, 8], 0 backend calls.
 S<p> p5s01a / p5s01b / p5s02a: 0 delete_wire ops, so required_checkpoints adds nothing: checkpoint_ops == the pre-161 formula
     {0,last} | BIND_KINDS ops | move_in run-closing ops; the collecting dry with each stored pred set: CHECKPOINT rows only for
     non-delete_wire reasons (each named in a FACT line with its missing ops).
 P   md5 unchanged: stagesim 95a162ba, stagekit 9b8f82c1, stage_prerun 7605116f, plan p5s02b f4520b10, pred p5s02b a1fd43fb.
 FACT lines (no gate): the p5s02b dry with the new set (status, first fail, ops reached) - whether it gets past ops 5 and 9.
Usage: py tools/bgrun.py --material --max-min 10 --log tools/bench/selftest_c161_delckpt.log -- py -u tools/bench/selftest_c161_delckpt.py"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402
import stagexec as SX  # noqa: E402

G = {"pass": 0, "fail": 0, "first": None}
B = os.path.join(HERE, "plan_ring_p5s02b.json")
NEW = (0, 1, 2, 3, 4, 5, 7, 8, 9, 10)
DW = [1, 4, 8]
OLD = (0, 2, 3, 5, 7, 9, 10)


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


class StrictBE(SX.SimBackend):
    """The dry backend made NON-collecting (selftest_c158_runcheck.py:91-96): pre-op checks raise, as on the real backend."""

    def __init__(self, *a_, **k_):
        super(StrictBE, self).__init__(*a_, **k_)
        self.unroutable = ()


def dry(plan, cps, be_cls=None):
    log = []
    orig = SX.SimBackend
    if be_cls is not None:
        SX.SimBackend = be_cls
    try:
        st, ff, ex = SX.dry_run(plan, log=log.append, checkpoints=cps)
    finally:
        SX.SimBackend = orig
    return st, ff, ex, log


def stored_sets(stem):
    pr = jl(os.path.join(HERE, "plan_ring_{0}_pred.json".format(stem)))
    a = tuple(int(k) for k in (pr.get("memory_pred") or {}).get("checkpoints") or [])
    b = tuple(int(r["op"]) for r in (pr.get("e1") or {}).get("checkpoints") or [])
    return a, b


print("---------- (i) p5s02b: delete_wire ops are checkpoints", flush=True)
OPS = SX.compile_plan(jl(B))
dw = [k for k, o in enumerate(OPS, 1) if o["kind"] == "delete_wire"]
gate("D1 p5s02b 10 ops; delete_wire ops == {0}".format(DW), len(OPS) == 10 and dw == DW, (len(OPS), [o["kind"] for o in OPS]))
cp = SX.checkpoint_ops(OPS)
req = SX.required_checkpoints(OPS)
sa, sb = stored_sets("p5s02b")
XR = jl(os.path.join(HERE, "prep_c161_a3_2_x10.json"))   # 161-a3-2: pred re-made since 161-b1-1 holds the new set; OLD | DW == it (PD393(a))
gate("D2 checkpoint_ops(p5s02b) == {0} == stored pred sets == x10 record {1} == old {2} | {3}".format(NEW, XR["checkpoints"], OLD, set(DW)), cp == NEW and sa == cp
     and sb == cp and tuple(XR["checkpoints"]) == cp and tuple(sorted(set(OLD) | set(DW))) == cp, {"cp": cp, "req": dict((k, sorted(v)) for k, v in req.items()), "stored": (sa, sb)})

print("---------- (ii) the Executor refuses a p5s02b set lacking a delete_wire op before op 1", flush=True)
st, ff, ex, log1 = dry(B, set(NEW), StrictBE)
gate("V1 set {0}, non-collecting dry: no CHECKPOINT stop (accepted)".format(NEW), not str(ff or "").startswith("CHECKPOINT"),
     (st, str(ff)[:300]))
for lab, cps, miss in (("V2", set(NEW) - {4}, [4]), ("V3", set(NEW) - {8}, [8]), ("V5", set(NEW) - {1}, [1]),
                       ("V4", set(OLD), DW)):
    st_, ff_, ex_, _ = dry(B, cps, StrictBE)
    gate("{0} set {1}: FAIL 'CHECKPOINT' naming {2} (delete_wire), no op dispatched".format(lab, sorted(cps), miss),
         st_ == "FAIL" and str(ff_).startswith("CHECKPOINT") and ": {0} (need".format(miss) in str(ff_)
         and "delete_wire op(s) not in the set: {0}".format(miss) in str(ff_) and len(ex_.be.calls) == 0,
         (st_, str(ff_)[:400], len(ex_.be.calls)))
reached = [r.get("k") for r in ex.report if isinstance(r, dict) and r.get("k")]
print("FACT p5s02b dry new set: status {0}; ops reported {1}; reads_real {2}; reads_skipped {3}; first fail {4}".format(
    st, reached, sorted(ex.reads_real), sorted(ex.reads_skipped), str(ff)[:300]), flush=True)
print("FACT p5s02b dry new set past ops 5 and 9: {0}".format(5 in reached and 9 in reached), flush=True)

print("---------- (iii) stored p5s01a / p5s01b / p5s02a sets", flush=True)
for stem in ("p5s01a", "p5s01b", "p5s02a"):
    pp = os.path.join(HERE, "plan_ring_{0}.json".format(stem))
    ops = SX.compile_plan(jl(pp))
    n_dw = sum(1 for o in ops if o["kind"] == "delete_wire")
    a, b = stored_sets(stem)
    old_rule = tuple(sorted({0, len(ops)} | set(k for k, o in enumerate(ops, 1) if o["kind"] in SX.BIND_KINDS)
                            | set(r[-1] for r in SX.move_in_runs(ops))))      # the pre-161 checkpoint_ops body (ddf23a31 :2148-2149)
    st_, ff_, ex_, _ = dry(pp, set(a))
    pre = [r["err"] for r in getattr(ex_, "pre_op_fails", []) if r["err"].startswith("CHECKPOINT")]
    missing = sorted(set(old_rule) - set(a))
    gate("S {0}: {1} delete_wire ops; required delete_wire set empty; checkpoint_ops == pre-161 rule {2}; stored-set CHECKPOINT rows "
         "carry no delete_wire reason".format(stem, n_dw, old_rule),
         n_dw == 0 and not SX.required_checkpoints(ops)["delete_wire"] and SX.checkpoint_ops(ops) == old_rule
         and not [x for x in pre if "delete_wire op(s) not in the set" in x], (st_, str(ff_)[:200], pre))
    print("FACT {0} stored pred sets memory_pred {1} / e1 {2}; validates {3}{4}".format(
        stem, a, b, "UNCHANGED (accepted)" if not pre else "NO - refused before and after this card",
        "" if not missing else "; lacks {0} = move_in run-closing/BIND/last op(s) of the card 158-a1-2 rule, not delete_wire".format(
            missing)), flush=True)

PINS = {"tools/stagesim.py": "95a162ba", "tools/stagekit.py": "9b8f82c1", "tools/stage_prerun.py": "7605116f",
        "tools/bench/plan_ring_p5s02b.json": "f4520b10", "tools/bench/plan_ring_p5s02b_pred.json": "4cef0a8c"}   # pred re-pinned 161-a3-2 (48b50b29 -> 18729409 -> a1fd43fb); 162-a2-2: -> 4cef0a8c (census written by card 162-a1-2)
got = dict((k, md5(k)[:8]) for k in PINS)
gate("P pins unchanged", got == PINS, got)
print("FACT md5 stagexec {0}".format(md5("tools/stagexec.py")), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(0 if not G["fail"] else 1)
