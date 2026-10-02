r"""diag_c134_5_el - card 134-5 step 3 (PD283(e), PD290(d)): judge the Error List read of the scratch-b FINAL file against the computed
class range tools/bench/errorlist_expect_p3b2ab.json (total 49..52, per-class lo/hi). Reads the NEWEST
tools/bench/errorlist_scratch_c134_5_ring_p3b2b_*.json written by tools/errorlist_check.py (--count-only --role scratch) and counts
its items per class with errorlist_check.class_counts(items, ocr=True) (norm_ocr keys - the keys the range file uses,
plan_ring_p3b_split_p3b2.py:294 <- stage_d1_ring_p3b1_el.py:122,139; review archive/peer/2026-10-02-c134-5-el-classrange.md). Nothing typed: every bound comes
from the range file. Touches no LabVIEW.
PREDICTION: E0 read verdict file present, every read gate True; E1 total in [total_lo, total_hi]; E2 every class within [lo, hi] and no
class outside the range file.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c134_5_el.log -- py -u tools/bench/diag_c134_5_el.py"""
import glob, hashlib, json, os, sys                                                   # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol, errorlist_check as EC                                                # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
RNG = os.path.join(B, "errorlist_expect_p3b2ab.json")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                         # noqa: E731
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:900]), flush=True)


fs = sorted(f for f in glob.glob(os.path.join(B, "errorlist_scratch_c134_5_ring_p3b2b_*.json")) if not f.endswith("_raw.json") and "_raw_full" not in f)
gate("E0a one Error List verdict file of the scratch-b final", fs, fs[-1:] if fs else None)
if fs:
    R = json.load(open(fs[-1], encoding="utf-8"))
    rg = json.load(open(RNG, encoding="utf-8"))
    print("  FACT read {0} md5 {1}: read_mode {2}, items {3}, window N {4}, verdict {5}, extra {6}, missing {7}, seconds {8}".format(
        os.path.relpath(fs[-1], ROOT), md5(fs[-1]), R.get("read_mode"), R.get("item_count"), R.get("n_reported"), R.get("verdict"),
        len(R.get("extra") or []), len(R.get("missing") or []), R.get("read_seconds")), flush=True)
    gate("E0b every read gate True (window, count, all items, esc, scratch identical/deleted, input unchanged, refs)",
         all((R.get("gates") or {}).values()) and R.get("gates"), R.get("gates"))
    # the range file's keys are norm_ocr keys (OCR aliases folded: 'youhaye', 'subyi'), so count with ocr=True (class_counts doc,
    # errorlist_check.py:472-473); the first run of this script counted with plain norm() and failed E2 on spelling only.
    cc = EC.class_counts(R.get("items"), ocr=True)
    def fold(d):                                                                   # SUM on a fold collision (review nit), never overwrite
        o = {}
        for k, v in d.items():
            o[EC.norm_ocr(k)] = o.get(EC.norm_ocr(k), 0) + v
        return o
    rg["per_class_lo"], rg["per_class_hi"] = fold(rg["per_class_lo"]), fold(rg["per_class_hi"])
    tot = len(R.get("items") or [])
    print("  FACT class counts {0}".format(json.dumps(cc, sort_keys=True)), flush=True)
    gate("E1 total {0} in [{1}, {2}] (errorlist_expect_p3b2ab.json)".format(tot, rg["total_lo"], rg["total_hi"]),
         rg["total_lo"] <= tot <= rg["total_hi"] and tot == R.get("n_reported"), (tot, R.get("n_reported")))
    lo, hi = rg["per_class_lo"], rg["per_class_hi"]
    bad = dict((k, (cc.get(k, 0), lo.get(k, 0), hi.get(k, 0))) for k in sorted(set(cc) | set(lo) | set(hi))
               if not (lo.get(k, 0) <= cc.get(k, 0) <= hi.get(k, 0)) or k not in lo)
    gate("E2 every class within [lo, hi] and none outside the range file", not bad, {"(got, lo, hi)": bad})
n = sum(1 for _l, ok in gates if ok)
ff = next((lab for lab, ok in gates if not ok), None)
print(protocol.result_line(protocol.make_result(n, len(gates) - n, ff, [{"path": os.path.relpath(fs[-1], ROOT), "md5": md5(fs[-1])}] if fs else [])), flush=True)
sys.exit(0 if ff is None else 1)
