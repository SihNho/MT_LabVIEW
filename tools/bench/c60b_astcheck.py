"""c60b_astcheck - static gate on tools/bench/diag_s3b_l0_localname.py BEFORE it is launched.

Same shape as c60_astcheck (cycle 60 attempt 1) and c58b_astcheck: parse the diagnostic, prove the guards the
brief imposes, and prove every gscript verb it calls already exists as a `def` in tools/gscript.py (no new
verb, no patched tool). Touches NO LabVIEW, opens no COM, reads files only.

PREDICTION CONTRACT
  1 the file parses (ast.parse) and reports its line count and gate-site count
  2 `remove_bad_wires_scripted` / `remove_bad_wires` / `gui_save` are NEITHER imported NOR called
  3 `allow_broken=True` is never passed anywhere
  4 every `g.<verb>(...)` call names a `def <verb>` that already exists in tools/gscript.py
  5 every name imported from build_d1_v0 / diag_s2_scaffold / hash_probe / bench_prep exists there
  6 nothing under tools/recipes/ is opened for writing and nothing there is removed
  7 `move_in` is neither imported nor called (the brief forbids reproducing attempt 1's pointless relocation)
  8 no owner comparison tests the literal 'Diagram' without also accepting 'TopLevelDiagram'
"""
import ast
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TARGET = os.path.join(ROOT, "tools", "bench", "diag_s3b_l0_localname.py")
GSCRIPT = os.path.join(ROOT, "tools", "gscript.py")
BANNED = ("remove_bad_wires_scripted", "remove_bad_wires", "gui_save")
IMPORTS = {"build_d1_v0": os.path.join(ROOT, "tools", "recipes", "build_d1_v0.py"),
           "diag_s2_scaffold": os.path.join(ROOT, "tools", "bench", "diag_s2_scaffold.py"),
           "hash_probe": os.path.join(ROOT, "tools", "hash_probe.py"),
           "bench_prep": os.path.join(ROOT, "tools", "bench", "bench_prep.py")}
fails = []


def gate(name, ok, detail=""):
    if not ok:
        fails.append(name)
    print("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else ""), flush=True)
    return ok


def defs_in(path):
    with open(path, encoding="utf-8") as f:
        return set(re.findall(r"^\s*def\s+(\w+)", f.read(), re.M))


def main():
    src = open(TARGET, encoding="utf-8").read()
    tree = ast.parse(src)
    n_gates = sum(1 for n in ast.walk(tree)
                  if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "gate")
    gate("1 the diagnostic parses", True, "%d lines, %d gate sites" % (len(src.splitlines()), n_gates))

    called, attrs = set(), set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name):
                called.add(f.id)
            elif isinstance(f, ast.Attribute):
                called.add(f.attr)
                if isinstance(f.value, ast.Name) and f.value.id == "g":
                    attrs.add(f.attr)
    imported = {a.name for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) for a in n.names}
    bad = [b for b in BANNED if b in called or b in imported]
    gate("2 remove_bad_wires_scripted / remove_bad_wires / gui_save neither imported nor called",
         not bad, "%r" % (bad,))

    ab = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
          for k in n.keywords if k.arg == "allow_broken"
          and isinstance(k.value, ast.Constant) and k.value.value is True]
    gate("3 allow_broken=True is never passed", not ab, "%d site(s)" % len(ab))

    gdefs = defs_in(GSCRIPT)
    missing = sorted(a for a in attrs if a not in gdefs and not a.startswith("_") and a not in ("CLAUDEDEV",))
    private = sorted(a for a in attrs if a.startswith("_"))
    gate("4 every g.<verb> called already exists as a def in tools/gscript.py", not missing,
         "verbs used: %r ; private helpers used: %r ; MISSING: %r"
         % (sorted(a for a in attrs if not a.startswith("_")), private, missing))
    gate("4b the private gscript helpers used also exist", all(p in gdefs for p in private),
         "%r" % [p for p in private if p not in gdefs])

    want = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and n.module in IMPORTS:
            want.setdefault(n.module, set()).update(a.name for a in n.names)
    for mod, names in sorted(want.items()):
        d = defs_in(IMPORTS[mod])
        miss = sorted(x for x in names if x not in d)
        gate("5 %s exports %s" % (mod, ", ".join(sorted(names))), not miss, "MISSING %r" % (miss,))

    recipes_writes = [ln for ln in src.splitlines()
                      if "recipes" in ln and ("open(" in ln or "shutil" in ln or "remove(" in ln)]
    gate("6 nothing under tools/recipes/ is opened for writing or removed", not recipes_writes,
         "%r" % (recipes_writes[:3],))

    gate("7 move_in is neither imported nor called",
         "move_in" not in called and "move_in" not in imported, "called=%r imported=%r"
         % ("move_in" in called, "move_in" in imported))

    lone = [ln.strip() for ln in src.splitlines()
            if re.search(r"==\s*[\"']Diagram[\"']", ln) and "TopLevelDiagram" not in ln]
    gate("8 no owner comparison tests the literal 'Diagram' alone (attempt 1's defect at :608)",
         not lone, "%r" % (lone[:3],))

    print("\n=== ASTCHECK %s%s" % ("OK" if not fails else "FAILED",
                                   ("; failing: " + ", ".join(fails)) if fails else ""), flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
