# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_158-a1-1.md
# ---
r"""prep_c158_a1_1_regress - card 158-a1-1 measurements 1, 2 (OFFLINE, json only, no LabVIEW, no COM).
WHAT EXISTED FIRST and is CALLED, not copied: prep_c157_a1_1_regress.record (op lists, compile_all, RingSession.CHECKPOINTS, move_in
ops) and its suite list; prep_c156_a1_2_lib.run_suite / jload. The c157 script runs its measurement at module level, so its
top-level DEFINITIONS (everything before `mode = ...`) are executed from its own source via ast and its functions are called;
only OUT is pointed at tools/bench/sim/ring_p5s02a_c158/. The suite adds selftest_c157_innerface (and c158_runcheck if present).
  before : record() -> sim/ring_p5s02a_c158/before.json; suite tag c158before.
  after  : record() compared with before.json; suite tag c158after.
PREDICTION CONTRACT (after): op lists of the three plans EQUAL; every stored plan's compile EQUAL; CHECKPOINTS of each recipe ==
before minus its move_in ops that do not close a run of consecutive move_in ops (p5s02a and p5s02: - 10, 11); p5s02a ==
[0,1,3,6,8,9,12,15,16,17]; suite counts equal before except the pinned self-tests (c155, c156 back to 0 fail) and c157 (updated).
    py tools/bgrun.py --material --max-min 40 --log tools/bench/prep_c158_a1_1_before.log -- py -u tools/bench/prep_c158_a1_1_regress.py before"""
import ast
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "prep_c157_a1_1_regress.py")
_tree = ast.parse(open(SRC, encoding="utf-8").read(), SRC)
_defs = []
for _n in _tree.body:
    if isinstance(_n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "mode" for t in _n.targets):
        break
    _defs.append(_n)
C = {"__file__": SRC, "__name__": "prep_c157_a1_1_regress_defs"}
exec(compile(ast.Module(body=_defs, type_ignores=[]), SRC, "exec"), C)
L, protocol = C["L"], C["protocol"]
OUT = os.path.join(HERE, "sim", "ring_p5s02a_c158")
C["OUT"] = OUT
L.SUITE = L.SUITE + [("c157_innerface", ["tools/bench/selftest_c157_innerface.py"])]
if os.path.exists(os.path.join(HERE, "selftest_c158_runcheck.py")):
    L.SUITE = L.SUITE + [("c158_runcheck", ["tools/bench/selftest_c158_runcheck.py"])]
gate, G = C["gate"], C["G"]


def closers(move_in):
    """move_in ops that close a run of consecutive move_in ops (independent of stagexec)."""
    s = set(move_in)
    return sorted(k for k in s if k + 1 not in s)


mode = sys.argv[1] if len(sys.argv) > 1 else "after"
os.makedirs(OUT, exist_ok=True)
now = C["record"]()
print("FACT md5 {0}".format(now["md5"]), flush=True)
print("FACT checkpoints {0}".format(now["checkpoints"]), flush=True)
print("FACT move_in ops {0}".format(now["move_in"]), flush=True)
print("FACT op counts {0}".format(dict((p, len(v)) for p, v in now["ops"].items())), flush=True)
print("FACT suite {0}".format([n for n, _ in L.SUITE]), flush=True)
if mode == "before":
    with open(os.path.join(OUT, "before.json"), "w", encoding="utf-8") as f:
        json.dump(now, f, sort_keys=True)
    gate("B before.json written ({0} stored plans compiled)".format(len(now["compile_all"])), True)
else:
    bef = L.jload(os.path.join(OUT, "before.json"))
    for p in C["PLANS"]:
        gate("A1 {0} op list EQUAL to before ({1} ops)".format(p, len(now["ops"][p])), now["ops"][p] == bef["ops"][p])
    diff = sorted(k for k in set(bef["compile_all"]) | set(now["compile_all"]) if bef["compile_all"].get(k) != now["compile_all"].get(k))
    gate("A2 every stored plan compiles EQUAL to before ({0} plans, {1} differ)".format(len(now["compile_all"]), len(diff)), not diff, diff[:10])
    for name in now["checkpoints"]:
        b, a = set(bef["checkpoints"][name]), set(now["checkpoints"][name])
        mi = now["move_in"][name]
        want = (b - set(mi)) | set(closers(mi))
        gate("A3 {0} CHECKPOINTS after == before - move_in + run closers {1}".format(name, closers(mi)), a == want,
             {"before": sorted(b), "after": sorted(a), "want": sorted(want)})
    gate("A4 p5s02a CHECKPOINTS == [0,1,3,6,8,9,12,15,16,17]",
         list(now["checkpoints"]["stage_d1_ring_p5s02a"]) == [0, 1, 3, 6, 8, 9, 12, 15, 16, 17],
         now["checkpoints"]["stage_d1_ring_p5s02a"])
for name, rc, npass, nfail, last in L.run_suite("c158" + mode, outdir=OUT):
    print("SUITE {0} rc={1} PASS-lines={2} FAIL-lines={3} | {4}".format(name, rc, npass, nfail, last), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(0 if not G["fail"] else 1)
