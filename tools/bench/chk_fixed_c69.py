import os, sys
ROOT = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop"
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
os.chdir(ROOT)
import guard_cycle as g
p = os.path.join(ROOT, "archive", "peer", "2026-09-24-priorart-c69-split-plan.md")
b = open(p, encoding="utf-8").read()
ok, paths, bad = g.fixed_citations(p, b)
print("OK", sorted(ok))
print("BAD", bad)
