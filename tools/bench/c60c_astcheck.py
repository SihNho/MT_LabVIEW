"""c60c_astcheck - static gate on tools/bench/diag_s3b_l0_localname_v2.py BEFORE it is launched.

The predecessor's gate (tools/bench/c60b_astcheck.py) with its checks KEPT, re-aimed at this cycle's
diagnostic, plus one addition (9): the forbidden alternative routes are named and machine-checked absent.
Touches NO LabVIEW, opens no COM, reads files only.

PREDICTION CONTRACT
  1 the file parses (ast.parse) and reports its line count and gate-site count
  2 `remove_bad_wires_scripted` / `remove_bad_wires` / `gui_save` are NEITHER imported NOR called
  3 `allow_broken=True` is never passed anywhere
  4 every `g.<verb>(...)` call names a `def <verb>` that already exists in tools/gscript.py
  5 every name imported from build_d1_v0 / diag_s2_scaffold / hash_probe / bench_prep exists there
  6 nothing under tools/recipes/ is opened for writing and nothing there is removed
  7 ROUTE CONFORMANCE for `move_in`, selected by `--route` (REPAIRED 2026-09-21, cycle 66)
      --route owner  (DEFAULT) : `move_in` is NEITHER imported NOR called
      --route movein           : `move_in` IS called at least once
    WHY. This gate was written for cycle 60's `owner` route, which deliberately excludes `move_in`. It was
    then reused as the fleet's generic static gate, so it FAILED BY CONSTRUCTION on every legitimate
    `move_in` build (cycle 64 `tools/bench/c64e_astcheck.log` 11/12, cycle 65 `tools/bench/c65_astcheck.log`
    11/12). That false positive is the SINGLETON intersection of runner cycles 49 n 50's failing gate lines
    (`tools/bench/cycle_runner.log:97,:100`) - i.e. a gate defect was the thing about to fire the runner's
    repeated-failure firefighter. The DEFAULT is `owner` so every existing invocation, which passes only a
    positional target, keeps this gate's pre-repair verdict byte for byte.
    NOT A COUNT, in either direction: stage M3 mandates FIVE `move_in` calls, so "called at most once" would
    be a second defect of the same shape. The printed gate NAME carries the route, so the two routes emit
    DIFFERENT failing lines and the runner's "same first failing gate line" matcher cannot conflate them.
  8 no owner comparison tests the literal 'Diagram' without also accepting 'TopLevelDiagram'
  9 the routes the brief FORBIDS are absent as calls: `build_invoke` (the peer's Invoke-seeded variant) and
    `copy_by_index` / `copy_into` / `move_by_label` (a donor switch)
"""
import argparse
import ast
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _parse_args(argv=None):
    """Added 2026-09-21 (cycle 66) for gate 7's route. The positional keeps the old `sys.argv[1]` contract
    and `--route` DEFAULTS TO `owner`, so an invocation that passes no flag behaves exactly as before."""
    ap = argparse.ArgumentParser(
        description="static gate on a tools/bench diagnostic, run BEFORE the diagnostic is launched")
    ap.add_argument("target", nargs="?", default="diag_s3b_l0_localname_v2.py",
                    help="script under tools/bench/ (an ABSOLUTE path is honoured as given)")
    ap.add_argument("--route", choices=("owner", "movein"), default="owner",
                    help="which construction route the target claims; decides gate 7's DIRECTION")
    return ap.parse_args(argv)


ARGS = _parse_args()
# os.path.join drops the prefix when the later part is absolute, so an absolute target passes through intact.
TARGET = os.path.join(ROOT, "tools", "bench", ARGS.target)
ROUTE = ARGS.route
GSCRIPT = os.path.join(ROOT, "tools", "gscript.py")
BANNED = ("remove_bad_wires_scripted", "remove_bad_wires", "gui_save")
FORBIDDEN_ROUTES = ("build_invoke", "copy_by_index", "copy_into", "move_by_label")
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

    mi_called, mi_imported = "move_in" in called, "move_in" in imported
    mi_detail = "route=%s called=%r imported=%r" % (ROUTE, mi_called, mi_imported)
    if ROUTE == "owner":
        gate("7[owner] move_in is neither imported nor called",
             not mi_called and not mi_imported, mi_detail)
    else:
        gate("7[movein] move_in is called at least once", mi_called, mi_detail)

    lone = [ln.strip() for ln in src.splitlines()
            if re.search(r"==\s*[\"']Diagram[\"']", ln) and "TopLevelDiagram" not in ln]
    gate("8 no owner comparison tests the literal 'Diagram' alone", not lone, "%r" % (lone[:3],))

    forb = [r for r in FORBIDDEN_ROUTES if r in called or r in imported]
    gate("9 the forbidden routes (Invoke-seeded variant, donor switch) are absent as calls", not forb,
         "%r" % (forb,))

    print("\n=== ASTCHECK %s%s" % ("OK" if not fails else "FAILED",
                                   ("; failing: " + ", ".join(fails)) if fails else ""), flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
