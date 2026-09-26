r"""diag_c101b_syntax - card 101-4: READ-ONLY parse of the edited stage recipe before its prior-art review (so the
reviewed bytes are the bytes that run). ast.parse + pyflakes when installed + the <=120-line rule. Imports nothing
from the recipe, runs nothing, touches no LabVIEW.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c101b_syntax.log -- py -u tools/bench/diag_c101b_syntax.py"""
import ast, os, sys                                                                  # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol                                                                      # noqa: E402
p = os.path.join(ROOT, "tools", "recipes", "stage_d1_disp.py")
src = open(p, encoding="utf-8").read()
n_lines = len(src.splitlines())
ok_parse, why = True, ""
try:
    ast.parse(src)
except SyntaxError as e:
    ok_parse, why = False, str(e)
msgs = []
try:
    from pyflakes import api as F, reporter as Rp                                    # noqa: E402
    import io
    out, err = io.StringIO(), io.StringIO()
    F.check(src, p, Rp.Reporter(out, err))
    msgs = [m for m in (out.getvalue() + err.getvalue()).splitlines() if m.strip()]
except ImportError:
    msgs = None                          # review c101-4-syntax s2: an absent pyflakes must not read as a PASS
print("  FACT pyflakes: {0}".format("SKIPPED (not installed)" if msgs is None else msgs), flush=True)
# S3 without pyflakes (review archive/peer/2026-09-27-c101-4-syntax.md s2): every Name LOADED anywhere must be bound
# SOMEWHERE in the file (assign / import / def / class / arg / for / with / except / comprehension) or be a builtin.
# Coarser than pyflakes (scope-blind), but it is a real check, and it catches a misspelt name.
import builtins                                                                      # noqa: E402
tree = ast.parse(src) if ok_parse else None
bound = set(dir(builtins)) | {"__file__", "__name__", "__doc__"}
for nd in (ast.walk(tree) if tree else ()):
    if isinstance(nd, ast.Name) and isinstance(nd.ctx, (ast.Store, ast.Del)):
        bound.add(nd.id)
    elif isinstance(nd, (ast.FunctionDef, ast.ClassDef)):
        bound.add(nd.name)
    elif isinstance(nd, ast.arg):
        bound.add(nd.arg)
    elif isinstance(nd, ast.alias):
        bound.add((nd.asname or nd.name).split(".")[0])
    elif isinstance(nd, ast.ExceptHandler) and nd.name:
        bound.add(nd.name)
loaded = sorted(set(nd.id for nd in (ast.walk(tree) if tree else ()) if isinstance(nd, ast.Name) and isinstance(nd.ctx, ast.Load)))
unbound = [n for n in loaded if n not in bound]
print("  FACT AST names loaded {0}, never bound anywhere: {1}".format(len(loaded), unbound), flush=True)
# S4 = stage_prerun's own X6 lint (stage_prerun.lint + OfflineGraph, the prerun's input graph), run BEFORE the prior-art
# review so the released bytes already pass it (stage_d1_disp_prerun6.log: X6 flagged the slice bound 600 = a node uid)
import stage_prerun as SP                                                            # noqa: E402
ints, strs = SP.lint(p, SP.OfflineGraph(os.path.join(ROOT, "tools", "bench", "par1359_95_graph.json")))
print("  FACT X6 lint: uids {0}; names {1}".format(ints, strs), flush=True)
g = [("S1 parses", ok_parse), ("S2 <= 120 lines ({0})".format(n_lines), n_lines <= 120),
     ("S3 no name loaded that is bound nowhere (AST; pyflakes {0})".format("absent" if msgs is None else "present"),
      ok_parse and not unbound and not [m for m in (msgs or []) if "undefined name" in m]),
     ("S4 stage_prerun X6 lint: no re-typed uid / terminal name", not ints and not strs)]
for lab, ok in g:
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", lab, why if lab.startswith("S1") else ""), flush=True)
n = sum(1 for _l, ok in g if ok)
print(protocol.result_line(protocol.make_result(n, len(g) - n, next((l for l, ok in g if not ok), None))), flush=True)
sys.exit(0 if n == len(g) else 1)
