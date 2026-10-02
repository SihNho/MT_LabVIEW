r"""diag_c140_3_elcmp - card 140-3 item 4 record (offline, no LabVIEW): the scratch's full Error List read (52 items, run without an
expected file -> verdict MISMATCH by construction) compared with the BED's expected file (51) through errorlist_check.compare and
class_counts(ocr=True). Facts only; no gate decides anything here.
PREDICTION (pred file plan_ring_p4_s01_pred.json): total 51 (alternative 53); measured window count 52.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c140_3_elcmp.log -- py -u tools/bench/diag_c140_3_elcmp.py"""
import json, os, sys                                                                         # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import errorlist_check as EC                                                                  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
RD = json.load(open(os.path.join(B, "errorlist_scratch_c140_3_ring_p4s01_20261002_205117_20261002_205859.json"), encoding="utf-8"))
EX = json.load(open(os.path.join(B, "errorlist_expected_D1_ring_p3b2b_20261002_130007.json"), encoding="utf-8"))
BED = json.load(open(os.path.join(B, "errorlist_D1_ring_p3b2b_20261002_130007_20261002_130834.json"), encoding="utf-8"))
items = [dict(i) for i in RD["items"]]
extra, missing, usage = EC.compare(items, EX["expected"])
print("READ items", len(items), "| bed expected total", EX.get("total"), "| extra", len(extra), "| missing", len(missing))
for e in extra:
    print("EXTRA", repr(e)[:200])
for m in missing:
    print("MISSING", repr(m)[:200])
for u in usage:
    print("USAGE", json.dumps(u, ensure_ascii=True)[:200])
a, b = EC.class_counts(items, ocr=True), EC.class_counts(BED.get("items") or [], ocr=True)
for k in sorted(set(a) | set(b)):
    if a.get(k, 0) != b.get(k, 0):
        print("CLASS-DELTA", repr(k)[:120], "bed", b.get(k, 0), "-> scratch", a.get(k, 0))
ok = not extra and not missing and len(items) == 51
print(protocol.result_line(protocol.make_result(1 if ok else 0, 0 if ok else 1, None if ok else "EL scratch 52 != predicted 51 (alt 53)", [])), flush=True)
sys.exit(0 if ok else 1)
