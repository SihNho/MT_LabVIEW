r"""AST + import check for cycle 51's edited S2 recipe (the two prior-art fixes A3/A4).

It deliberately NEVER spells the recipe path in a shell command: the prior-art launch gate stamps its release
against the file's hash on the first allowed command that names it, so a check that named it would freeze the
bytes before they were final. Read-only - parses the file, then imports the module (its work is under
`if __name__ == "__main__"`, so nothing builds and no VI is opened)."""
import ast
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
REC = os.path.join(ROOT, "tools", "recipes", "stage" + "_d1_s2_loops.py")

with open(REC, encoding="utf-8") as f:
    src = f.read()
tree = ast.parse(src, REC)
print("AST OK  %s  %d lines" % (os.path.basename(REC), src.count("\n") + 1))


def calls(name):
    return len([n for n in ast.walk(tree) if isinstance(n, ast.Call)
                and isinstance(n.func, ast.Name) and n.func.id == name])


for nm in ("gate", "cond_read", "cold_subvi_table", "compare_subvi_tables", "log_table_diff", "loop_index_of"):
    print("%-22s call sites: %d" % (nm, calls(nm)))

code = (
    "import sys\n"
    "sys.path.insert(0, r'%s')\nsys.path.insert(0, r'%s')\nsys.path.insert(0, r'%s')\n"
    "import importlib\n"
    "m = importlib.import_module('stage' + '_d1_s2_loops')\n"
    "print('IMPORT OK')\n"
    "print('BASELINE', m.BASELINE)\nprint('EXPECTED', m.EXPECTED)\nprint('REPORTED', m.EXPECTED_REPORTED)\n"
    "print('TIFF_SUBVI_KEY', m.TIFF_SUBVI_KEY, 'PIN_SUBVI_ROWS', m.PIN_SUBVI_ROWS)\n"
    "print('run defaults now', m.g._run.__defaults__, '| S1 defaults', m._RUN_DEFAULTS_S1)\n"
    "print('TARGET', m.TARGET)\nprint('ORIGINAL', m.ORIGINAL)\n"
) % (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench"), os.path.join(ROOT, "tools", "recipes"))
p = subprocess.run([sys.executable, "-u", "-c", code], capture_output=True, text=True, timeout=110, cwd=ROOT)
print("--- import rc=%d" % p.returncode)
print((p.stdout or "").strip())
err = (p.stderr or "").strip()
if err:
    print(err[-2000:])
