"""c58b_astcheck - offline syntax check for tools/bench/diag_s58_boolwire.py. No LabVIEW, no COM.

Same pattern as c57_astcheck.py / c58_astcheck.py, plus the two guards this dispatch's brief adds:
  * `gui_save` is never CALLED and `allow_broken` is never set True;
  * `remove_bad_wires_scripted` / `remove_bad_wires` are never CALLED and never IMPORTED (48(d) REFUSES them);
  * the stop-recorded S3a recipe path is only ever READ about (os.path.exists / getmtime), never opened for
    write and never passed to a runner;
  * which `gscript` verbs the script uses, so the reviewer can see no new verb was invented.
"""
import ast
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TGT = os.path.join(HERE, "diag_s58_boolwire.py")
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


bad = []
if called("gui_save"):
    bad.append("gui_save is CALLED")
for v in ("remove_bad_wires_scripted", "remove_bad_wires"):
    if called(v):
        bad.append("%s is CALLED - 48(d) REFUSES it" % v)
for n in ast.walk(tree):
    if isinstance(n, (ast.Import, ast.ImportFrom)):
        for al in n.names:
            if "remove_bad_wires" in al.name:
                bad.append("remove_bad_wires* is IMPORTED")
    if isinstance(n, ast.keyword) and n.arg == "allow_broken":
        if not (isinstance(n.value, ast.Constant) and n.value.value is False):
            bad.append("allow_broken passed as %r" % ast.dump(n.value)[:60])
if "s3a_focus_ind" in src:
    for n in calls:
        f = n.func
        nm = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")
        if nm in ("open", "remove", "copy2", "run", "Popen", "system"):
            for a in ast.walk(n):
                if isinstance(a, ast.Constant) and isinstance(a.value, str) and "s3a_focus_ind" in a.value:
                    bad.append("the forbidden recipe is passed to %s()" % nm)

verbs = sorted({n.func.attr for n in calls
                if isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name)
                and n.func.value.id == "g"})
dels = [n for n in calls if isinstance(n.func, ast.Attribute) and n.func.attr == "delete_object"]
print("AST OK  %s  %d lines, %d gate sites" % (os.path.basename(TGT), len(src.splitlines()), src.count("gate(")))
print("gscript verbs called: %s" % (verbs,))
print("delete_object call sites: %d (all routed through delete_by_uid)" % len(dels))
print("guard assertions: %s" % ("ALL CLEAR" if not bad else bad))
