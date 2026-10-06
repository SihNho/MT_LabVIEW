# ---
# labview: none
# hardware: none
# ---
"""selftest_fntest_owners - card chat-F3b: fntest_lib.owners_of (fixed after tools/bench/fntest_g2.log:257-271) run OFFLINE
from its source (ast; fntest_lib is not imported, so nothing reaches LabVIEW) on a read_live-shaped objs list whose `owner`
column is the owner CLASS NAME, as gscript.report_all returns it.
PREDICTION (every gate PASS): T1 loop bodies map to [WhileLoop, loop uid] and the FS frame to [FlatSequence, fs uid] via the
resolver; the top-level diagram (resolver raises) is left out; T2 a second call asks the resolver nothing (cache); T3 an
integer owner column is used as it is with no resolver; T4 no resolver + class-name owners -> {} (never a crash).
py tools/bgrun.py --material --max-min 3 --log tools/bench/selftest_fntest_owners.log -- py -u tools/bench/selftest_fntest_owners.py"""
import ast
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import protocol                                                                    # noqa: E402

src = open(os.path.join(HERE, "fntest_lib.py"), encoding="utf-8").read()
ns = {}
exec(compile(ast.Module(body=[n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == "owners_of"],
                        type_ignores=[]), "fntest_lib.py", "exec"), ns)
owners_of, G = ns["owners_of"], []


def gate(label, ok, detail=""):
    G.append((label, bool(ok)))
    print("  %s  %s%s" % ("PASS" if ok else "FAIL", label, "" if ok else "  | %s" % (detail,)), flush=True)


objs = [{"uid": 3, "class": "Diagram", "owner": "VI"}, {"uid": 44, "class": "WhileLoop", "owner": "Diagram"},
        {"uid": 92, "class": "Diagram", "owner": "WhileLoop"}, {"uid": 46, "class": "WhileLoop", "owner": "Diagram"},
        {"uid": 112, "class": "Diagram", "owner": "WhileLoop"}, {"uid": 281, "class": "FlatSequence", "owner": "Diagram"},
        {"uid": 291, "class": "Diagram", "owner": "FlatSequence"}]
asked = []


def res(u):
    asked.append(u)
    if u == 3:
        raise RuntimeError("owner_of(3) is not an answer (the top-level diagram's owner is the VI)")
    return {92: ("WhileLoop", 44), 112: ("WhileLoop", 46), 291: ("FlatSequence", 281)}[u]


cache = {}
m = owners_of(objs, res, cache)
gate("T1 bodies -> [WhileLoop, loop], FS frame -> [FlatSequence, fs], top-level left out",
     m == {"92": ["WhileLoop", 44], "112": ["WhileLoop", 46], "291": ["FlatSequence", 281]}, m)
n = len(asked)
gate("T2 second call: same map, the resolver asked nothing (cache)", owners_of(objs, res, cache) == m and len(asked) == n, asked)
gate("T3 an integer owner column is used as it is", owners_of([{"uid": 5, "class": "Diagram", "owner": 7},
                                                               {"uid": 7, "class": "WhileLoop", "owner": "Diagram"}])
     == {"5": ["WhileLoop", 7]})
gate("T4 no resolver + class-name owners -> {} (no crash)", owners_of(objs) == {})
bad = [x for x in G if not x[1]]
print("=== %d pass / %d fail" % (len(G) - len(bad), len(bad)), flush=True)
print(protocol.result_line(protocol.make_result(len(G) - len(bad), len(bad), bad[0][0] if bad else None, [])), flush=True)
sys.exit(1 if bad else 0)
