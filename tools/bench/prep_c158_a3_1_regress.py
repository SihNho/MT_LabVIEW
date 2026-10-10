# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_158-a3-1.md
# ---
r"""prep_c158_a3_1_regress - card 158-a3-1 measurements 1 and 2 (OFFLINE, json only, no LabVIEW, no COM).
WHAT EXISTED FIRST and is CALLED, not copied: prep_c158_a2_1_regress (its top-level DEFINITIONS, everything before `mode = ...`, executed
from its own source via ast - which itself executes prep_c158_a1_1_regress's definitions: record(), gate, the suite list incl.
c157_innerface / c158_runcheck / c158_wire0face, OUT = tools/bench/sim/ring_p5s02a_c158/).
  before : record() -> sim/ring_p5s02a_c158/before_a3.json; op lists, compile_all and checkpoints compared with before_a2.json (the
           158-a2-1 state, stagexec 7a712ccb unchanged since); suite tag c158a3before.
  after  : record() compared with before_a3.json (op lists, compile_all, checkpoints all EQUAL); suite tag c158a3after.
PREDICTION CONTRACT: before -> everything EQUAL to before_a2.json; after -> everything EQUAL to before_a3.json; suite counts equal to
the before run except re-pinned md5 strings (known failing as found: case_frame_c124 28/1, t6_regress 9/2).
    py tools/bgrun.py --material --max-min 40 --log tools/bench/prep_c158_a3_1_before.log -- py -u tools/bench/prep_c158_a3_1_regress.py before"""
import ast
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "prep_c158_a2_1_regress.py")
_tree = ast.parse(open(SRC, encoding="utf-8").read(), SRC)
_defs = []
for _n in _tree.body:
    if isinstance(_n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "mode" for t in _n.targets):
        break
    _defs.append(_n)
D = {"__file__": SRC, "__name__": "prep_c158_a2_1_regress_defs"}
exec(compile(ast.Module(body=_defs, type_ignores=[]), SRC, "exec"), D)
C, L, protocol, gate, G, OUT = D["C"], D["L"], D["protocol"], D["gate"], D["G"], D["OUT"]

mode = sys.argv[1] if len(sys.argv) > 1 else "after"
now = C["record"]()
print("FACT md5 {0}".format(now["md5"]), flush=True)
print("FACT checkpoints {0}".format(now["checkpoints"]), flush=True)
print("FACT op counts {0}".format(dict((p, len(v)) for p, v in now["ops"].items())), flush=True)
print("FACT suite {0}".format([n for n, _ in L.SUITE]), flush=True)
tag = "before_a2.json" if mode == "before" else "before_a3.json"
ref = L.jload(os.path.join(OUT, tag))
for p in C["PLANS"]:
    gate("A1 {0} op list EQUAL to {1} ({2} ops)".format(p, tag, len(now["ops"][p])), now["ops"][p] == ref["ops"][p])
diff = sorted(k for k in set(ref["compile_all"]) | set(now["compile_all"]) if ref["compile_all"].get(k) != now["compile_all"].get(k))
gate("A2 every stored plan compiles EQUAL to {0} ({1} plans, {2} differ)".format(tag, len(now["compile_all"]), len(diff)), not diff, diff[:10])
for name in now["checkpoints"]:
    gate("A3 {0} CHECKPOINTS EQUAL to {1}".format(name, tag), now["checkpoints"][name] == ref["checkpoints"][name],
         {"ref": ref["checkpoints"][name], "now": now["checkpoints"][name]})
if mode == "before":
    with open(os.path.join(OUT, "before_a3.json"), "w", encoding="utf-8") as f:
        json.dump(now, f, sort_keys=True)
    gate("B before_a3.json written ({0} stored plans compiled)".format(len(now["compile_all"])), True)
for name, rc, npass, nfail, last in L.run_suite("c158a3" + mode, outdir=OUT):
    print("SUITE {0} rc={1} PASS-lines={2} FAIL-lines={3} | {4}".format(name, rc, npass, nfail, last), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(0 if not G["fail"] else 1)
