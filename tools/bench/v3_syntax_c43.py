r"""v3_syntax_c43.py - syntax gate for the cycle-43 S0 recipe. Read-only: ast.parse + py_compile + sha256.
No LabVIEW, no COM, no edits. (Pattern: tools/bench/v7_syntax_c42.log, cycle 42.)"""
import ast
import hashlib
import os
import py_compile
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "V6_ParallelLoop", "tools", "recipes", "build_s0_closeref_v3.py")
if not os.path.exists(P):
    P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "recipes", "build_s0_closeref_v3.py")
src = open(P, "rb").read()
text = src.decode("utf-8")
ast.parse(text)
py_compile.compile(P, doraise=True)
print(f"ast.parse OK / py_compile OK   {P}")
print(f"lines {len(text.splitlines())}   bytes {len(src)}   sha256 {hashlib.sha256(src).hexdigest()}")
print(f"md5 {hashlib.md5(src).hexdigest()}")
sys.exit(0)
