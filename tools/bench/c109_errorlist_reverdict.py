"""Card 109-1: offline M1 / M2 / W2 for bed D1_l2_a2_20260927_132125. NO LabVIEW (errorlist_check imports LabVIEW
lazily, tools/errorlist_check.py:29; reverdict is the offline path, :215).

Prior art found: errorlist_check.compare / reverdict / find_reusable (tools/errorlist_check.py:183-245, 393-423) do
the whole verdict; this file only calls them. errorlist_check.py is NOT edited.

PREDICTION CONTRACT:
  G1 M1  compare(l2_a2 raw items, L2-A1 expected entries)  -> 0 extra, 0 missing (per-class counts equal)
  G2 M1  per-entry usage equals each entry's count (10 entries, total 35)
  G3 M2  stage_d1_l2a2.log RBW-deleted list == stage_d1_l2a1.json:866 list (29 uids, set equal, 25523 absent)
  G4     bed md5 now == 807c803e1cef1dc33cfdc936c87af1ca (the read's before == after)
  G5 W2  find_reusable(bed, md5) returns the 144914 read (qualifies)
  G6 W2  reverdict(... expected file of L2-A2) -> OK, 0 extra, 0 missing, expected_file set
"""
import hashlib, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import errorlist_check as EC   # noqa: E402
import protocol               # noqa: E402

B = os.path.join(ROOT, "tools", "bench")
BED = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_l2_a2_20260927_132125.vi"
MD5 = "807c803e1cef1dc33cfdc936c87af1ca"
MAIN = os.path.join(B, "errorlist_D1_l2_a2_20260927_132125_20260927_144914.json")
RAW = MAIN[:-5] + "_raw.json"
EXP_A1 = os.path.join(B, "errorlist_expected_D1_l2_a1_20260925_235224.json")
EXP_A2 = os.path.join(B, "errorlist_expected_D1_l2_a2_20260927_132125.json")
gates, arts = {}, []


def gate(k, ok, msg):
    gates[k] = bool(ok)
    print("%s  %s  %s" % ("PASS" if ok else "FAIL", k, msg), flush=True)


items = json.load(open(RAW, encoding="utf-8"))["items"]
exp1 = json.load(open(EXP_A1, encoding="utf-8"))["expected"]
its = [dict(i) for i in items]
for i in its:
    i.pop("licensed_by", None)
extra, missing, usage = EC.compare(its, exp1, [])
gate("G1_M1_zero_diff", not extra and not missing, "extra %d %s ; missing %d %s" % (len(extra), extra, len(missing), missing))
per = {}
for n, it in enumerate(its):
    txt = "%s %s" % (it.get("raw") or "", it.get("detail") or "")
    k = next((j for j, e in enumerate(exp1) if EC._hit(e, txt)), None)
    per.setdefault(k, []).append(it.get("index", n))
rows_ok = True
for j, (e, u) in enumerate(zip(exp1, usage)):
    ok = u["used"] == int(e.get("count", 1))
    rows_ok &= ok
    print("M1 ROW %d %-45s l2_a1 %2d  l2_a2 %2d  %s  first-hit items %s" % (
        j, "+".join(e["norm_all"]), int(e.get("count", 1)), u["used"], "==" if ok else "DIFF", per.get(j)), flush=True)
print("M1 unclassified items (no entry hits):", per.get(None), flush=True)
gate("G2_M1_counts_equal", rows_ok and len(its) == 35 and sum(u["used"] for u in usage[:len(exp1)]) == 35,
     "10 entries, %d items" % len(its))


def rbw(path):
    for ln, line in enumerate(open(path, encoding="utf-8", errors="replace"), 1):
        m = re.search(r"RBW deleted \[([0-9, ]+)\]", line)
        if m:
            return ln, [int(x) for x in m.group(1).split(",")]
    return None, []


l2, u2 = rbw(os.path.join(B, "stage_d1_l2a2.log"))
l1, u1 = rbw(os.path.join(B, "stage_d1_l2a1.json"))
gate("G3_M2_same_29", len(u1) == 29 and set(u1) == set(u2) and 25523 not in u2,
     "stage_d1_l2a2.log:%s n=%d ; stage_d1_l2a1.json:%s n=%d ; only_a2 %s only_a1 %s ; 25523 in a2 %s" % (
         l2, len(u2), l1, len(u1), sorted(set(u2) - set(u1)), sorted(set(u1) - set(u2)), 25523 in u2))

now = hashlib.md5(open(BED, "rb").read()).hexdigest()
gate("G4_bed_md5", now == MD5, "bed md5 now %s" % now)

mj, rj, why = EC.find_reusable(BED, now, B)
gate("G5_reusable", mj and os.path.basename(mj) == os.path.basename(MAIN), "find_reusable -> %s %s" % (mj, why))

v, out = EC.reverdict(BED, MAIN, RAW, bench=B, expected_path=EXP_A2)
R = json.load(open(out, encoding="utf-8"))
gate("G6_reverdict_OK", v == "OK" and not R["extra"] and not R["missing"] and R["expected_file"],
     "verdict %s extra %d missing %d expected_file %s out %s" % (v, len(R["extra"]), len(R["missing"]),
                                                                 R["expected_file"], out))
for p in (EXP_A2, out):
    arts.append({"path": protocol._rel(p), "md5": hashlib.md5(open(p, "rb").read()).hexdigest()})
    print("ARTEFACT %s %s" % (arts[-1]["path"], arts[-1]["md5"]), flush=True)
fails = [k for k, ok in gates.items() if not ok]
print(protocol.result_line(protocol.make_result(len(gates) - len(fails), len(fails), fails[0] if fails else None, arts)),
      flush=True)
sys.exit(1 if fails else 0)
