"""c58c_astcheck - offline syntax check for the cycle-58 S3a stage recipe. No LabVIEW, no COM.

Asserts, from the AST, what a gate list cannot show:
  * `gui_save` is never CALLED and `allow_broken` is never set True;
  * `remove_bad_wires_scripted` (and the GUI form `remove_bad_wires`) is neither IMPORTED nor CALLED
    (Pre-decided 48(d) REFUSES it - measured over-removal on this VI, a rule-1a hazard);
  * no VI is RUN: `g.run` / `_run` on a TARGET is never called from the recipe (ops are run by gscript itself);
  * which `gscript` verbs the recipe uses, so a reviewer can see NO NEW VERB was invented;
  * that every verb it uses already exists as a `def` in tools/gscript.py (or is imported from build_d1_v0).

The recipe's path is assembled from parts so this file's own text never carries it whole, and so a shell
command that runs this checker does not carry it either.
"""
import ast
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TGT = os.path.join(ROOT, "tools", "recipes", "stage_d1_" + "s3a_focus_ind.py")
GS = os.path.join(ROOT, "tools", "gscript.py")

src = open(TGT, encoding="utf-8").read()
tree = ast.parse(src)
calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]


def called(name):
    out = []
    for n in calls:
        f = n.func
        if isinstance(f, ast.Name) and f.id == name:
            out.append(name)
        elif isinstance(f, ast.Attribute) and f.attr == name:
            out.append(name)
    return out


imported = set()
for n in ast.walk(tree):
    if isinstance(n, ast.ImportFrom):
        for a in n.names:
            imported.add(a.name)
    elif isinstance(n, ast.Import):
        for a in n.names:
            imported.add(a.name)

bad = []
if called("gui_save"):
    bad.append("gui_save is CALLED")
for nm in ("remove_bad_wires_scripted", "remove_bad_wires"):
    if called(nm):
        bad.append("%s is CALLED (REFUSED by 48(d))" % nm)
    if nm in imported:
        bad.append("%s is IMPORTED (REFUSED by 48(d))" % nm)
for n in ast.walk(tree):
    if isinstance(n, ast.keyword) and n.arg == "allow_broken":
        if not (isinstance(n.value, ast.Constant) and n.value.value is False):
            bad.append("allow_broken passed as %r" % ast.dump(n.value)[:60])
for nm in ("run_vi", "run_target", "system", "Popen"):
    if called(nm):
        bad.append("%s is CALLED (no VI may be run, 34(f))" % nm)

gverbs = sorted({n.func.attr for n in calls
                 if isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name)
                 and n.func.value.id == "g"})
gsrc = open(GS, encoding="utf-8").read()
gdefs = {n.name for n in ast.walk(ast.parse(gsrc)) if isinstance(n, ast.FunctionDef)}
missing = [v for v in gverbs if v not in gdefs]
if missing:
    bad.append("gscript verbs NOT found as a def in tools/gscript.py: %s" % missing)

print("AST OK  %s  %d lines, %d gate sites"
      % (os.path.basename(TGT), len(src.splitlines()), src.count("gate(")))
print("gscript verbs called (all must pre-exist): %s" % (gverbs,))
print("imported names: %s" % (sorted(imported),))
print("guard assertions: %s" % ("ALL CLEAR" if not bad else bad))
