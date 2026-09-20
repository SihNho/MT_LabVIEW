"""c56m5b_astcheck - offline syntax check for tools/bench/diag_s56_transport3b.py. No LabVIEW, no COM."""
import ast
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TGT = os.path.join(HERE, "diag_s56_transport3b.py")
src = open(TGT, encoding="utf-8").read()
ast.parse(src)
print("AST OK  %s  %d lines, %d gate sites" % (os.path.basename(TGT), len(src.splitlines()), src.count("gate(")))
