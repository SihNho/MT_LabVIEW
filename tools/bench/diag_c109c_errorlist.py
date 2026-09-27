"""Card 109-3 E2: offline re-verdict of the D1_l2_a3 Error List read against its new explicit expected file. NO LabVIEW
(errorlist_check imports LabVIEW lazily, tools/errorlist_check.py:29; reverdict is the offline path, :215).
PRIOR ART: tools/bench/c109_errorlist_reverdict.py (card 109-1, same calls for L2-A2); errorlist_check is NOT edited.
PREDICTION CONTRACT:
  G1 find_reusable(bed, md5 14337cfd) returns the 153323 read (qualifies: md5 before == after, gates true, raw == n_reported 29)
  G2 compare(raw items, expected entries): 0 extra, 0 missing; each entry used exactly its count (6 entries, total 29)
  G3 reverdict(..., expected file) -> OK, expected_file set, 0 extra, 0 missing
  G4 bed md5 still 14337cfda5780cb39d12deb5fe0d3db9
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c109c_errorlist.log -- py -u tools/bench/diag_c109c_errorlist.py"""
import json, os, sys                                                               # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import errorlist_check as EC, protocol                                             # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
BED = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_l2_a3_20260927_151224.vi"
MD5 = "14337cfda5780cb39d12deb5fe0d3db9"
EXP = os.path.join(B, "errorlist_expected_D1_l2_a3_20260927_151224.json")
gates, arts = {}, []


def gate(k, ok, msg):
    gates[k] = bool(ok)
    print("%s  %s  %s" % ("PASS" if ok else "FAIL", k, str(msg)[:500]), flush=True)


main, raw, why = EC.find_reusable(BED, MD5)
gate("G1_reusable_read", main and main.endswith("_20260927_153323.json"), (main, raw, why))
items = [dict(i) for i in json.load(open(raw, encoding="utf-8"))["items"]] if raw else []
for i in items:
    i.pop("licensed_by", None)
exp = json.load(open(EXP, encoding="utf-8"))["expected"]
extra, missing, usage = EC.compare(items, exp, [])
for e, u in zip(exp, usage):
    print("ENTRY %-45s count %2d used %2d" % ("+".join(e["norm_all"]), int(e["count"]), u["used"]), flush=True)
gate("G2_compare_exact", not extra and not missing and len(items) == 29 and
     all(u["used"] == int(e["count"]) for e, u in zip(exp, usage)) and sum(int(e["count"]) for e in exp) == 29,
     "extra %s missing %s" % (extra, missing))
v, out = EC.reverdict(BED, main, raw, expected_path=EXP) if main else ("NONE", None)
R = json.load(open(out, encoding="utf-8")) if out else {}
gate("G3_reverdict_OK", v == "OK" and R.get("expected_file") and not R.get("extra") and not R.get("missing"), (v, out))
gate("G4_bed_md5_unchanged", EC.md5(BED) == MD5, EC.md5(BED))
arts = [{"path": os.path.relpath(p, ROOT), "md5": EC.md5(p)} for p in (EXP, out) if p]
n_pass = sum(1 for x in gates.values() if x); n_fail = len(gates) - n_pass        # noqa: E702
first = next((k for k, x in gates.items() if not x), None)
print("=== GATES: %d pass / %d fail%s" % (n_pass, n_fail, "; failing: " + first if first else ""))
print(protocol.result_line(protocol.make_result(n_pass, n_fail, first, arts)))
sys.exit(0 if n_fail == 0 else 1)
