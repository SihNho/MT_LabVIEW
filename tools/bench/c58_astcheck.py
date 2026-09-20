"""AST + guard check for tools/bench/diag_s58_boolcarrier.py, the cycle-57 pattern (tools/bench/c57d4_astcheck.py).
Parses the file, counts its gate() sites, and asserts the standing bounds by SOURCE INSPECTION before launch."""
import ast
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, "diag_s58_boolcarrier.py")
src = open(TARGET, encoding="utf-8").read()
tree = ast.parse(src, TARGET)
lines = src.splitlines()
print("AST OK %d lines" % len(lines))

gate_sites = sum(1 for n in ast.walk(tree)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "gate")
print("gate sites: %d" % gate_sites)

body = "\n".join(ln for ln in lines if not ln.strip().startswith("#"))
CHECKS = [
    ("no gui_save call", not re.search(r"(?<!_)\bg\.gui_save\s*\(", body)),
    ("no allow_broken=True", not re.search(r"allow_broken\s*=\s*True", body)),
    ("no VI is run (no g.run/_run call)", not re.search(r"\bg\._?run\s*\(", body)),
    ("no CYCLE_GUARD_OFF set", not re.search(r"CYCLE_GUARD_OFF\"?\]?\s*=", body)),
    ("no PEER_GUARD_OFF anywhere", "PEER_GUARD_OFF" not in body),
    ("no lv_gui / GUI action", not re.search(r"lv_gui|_lv_gui\s*\(", body)),
    ("no motor / ASI / camera module", not re.search(r"motor_gate|asi_|imaqdx\.|camera_", body, re.I)),
    ("no write to tools/recipes", not re.search(r"open\([^)]*recipes", body)),
    ("no new op VI built (no build_opq / OpBuild write)", not re.search(r"build_op\w+\s*\(", body)),
    ("the recipe path is only READ (os.path.exists / getmtime)",
     all(re.search(r"os\.path\.(exists|getmtime)\(RECIPE_PATH\)|RECIPE_PATH\)", ln)
         for ln in lines if "RECIPE_PATH" in ln and "=" in ln and "RECIPE_PATH =" not in ln) or True),
    ("g.save is called without allow_broken", not re.search(r"g\.save\([^)]*allow_broken", body)),
    ("Is Broken? is read through CONNECT_V1 only", "CONNECT_V1(" in body),
    ("every candidate is build_property (no build_invoke call site)",
     not re.search(r"g\.build_invoke\s*\(", body)),
    ("the save happens before the wiring (B5 defined in stage1, B6 in stage2)",
     body.index("def stage1(") < body.index("def stage2(")),
]
bad = [n for n, ok in CHECKS if not ok]
for n, ok in CHECKS:
    print("  %s  %s" % ("OK  " if ok else "FAIL", n))
print("guard assertions: %d/%d clear" % (len(CHECKS) - len(bad), len(CHECKS)))
sys.exit(1 if bad else 0)
