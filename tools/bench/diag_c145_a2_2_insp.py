# ---
# labview: none
# hardware: none
# ---
"""card 145-a2-2 offline fact extraction (no diagnosis): the recorded Error List items of s04 vs s03 by text (multiset diff),
to record which items make up the per-class mismatch of selftest_elpred R4 (local recorded 0, re-derived +1)."""
import collections, json, os, re
ROOT = r"G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop"
os.chdir(ROOT)
J = lambda p: json.load(open(p, encoding="utf-8"))
A = J("tools/bench/elrule_fixtures/errorlist_p4s03_armA13K_20261007_103040.json")["items"]
B = J("tools/bench/errorlist_D1_ring_p4s04_20261007_215031_20261007_220024.json")["items"]
print("item keys", sorted(B[0].keys()))
norm = lambda x: re.sub(r"\s+", " ", "{0} || {1}".format(x.get("raw", ""), x.get("detail", ""))).strip()[:260]
ca, cb = collections.Counter(norm(x) for x in A), collections.Counter(norm(x) for x in B)
for t, n in sorted((cb - ca).items()):
    print("ADDED x{0} | {1}".format(n, t))
for t, n in sorted((ca - cb).items()):
    print("GONE  x{0} | {1}".format(n, t))
for x in B:
    if "local" in norm(x).lower():
        print("S04-LOCAL | {0}".format(norm(x)))
