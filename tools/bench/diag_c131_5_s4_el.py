r"""diag_c131_5_s4_el - card 131-5 step S4 (Error List half; census + fail_above 690 are diag_c131_4_census.py, run first, unchanged).
PD273(b) (docs/d1/ring-p3b.md): expected Error List for P3b-1 = 53 (class 'wire has loose ends' 22), proceeding under PD273(a)
(unverified). Writes, mechanically:
  1. plan_ring_p3b1_pred.json errorlist: removed += {"p3b_x_img_src_w3040": 1}, predicted_total 54 -> 53, row_sources cite the
     offline graph diff (diag_c131_5_stubs.log, the ONE one-sided wire the simulated end state retires: w3040, #6810 'Image Out').
  2. plan_ring_p3b1_pin.json (ring-p3b1-pin/1) from the 131-4 SCRATCH READ errorlist_scratch_c129_..._053812.json (53 items,
     extra [] -> new_count 0): stage_d1_ring_p3b1_el.py writes it only on a scratch PASS (:78-82), and that read failed only
     because the expectation was 54. The final-mode helper needs it (gate P, :49-50; PIN multiset, :84).
PRIOR ART: stage_d1_ring_p3b1_el.py builds the expected file from pred.removed (:36-45); this script only edits its inputs.
Touches no LabVIEW. PREDICTION: gates E1-E5 PASS; pred predicted_total 53, removed sum 2; pin new_count 0, total 53.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c131_5_s4_el.log -- py -u tools/bench/diag_c131_5_s4_el.py"""
import hashlib, json, os, sys, time                                                   # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol                                                                       # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
PRED = os.path.join(B, "plan_ring_p3b1_pred.json")
PINF = os.path.join(B, "plan_ring_p3b1_pin.json")
READ = os.path.join(B, "errorlist_scratch_c129_ring_p3b1_20261002_052136_20261002_053812.json")
STUBS = os.path.join(B, "diag_c131_5_stubs.log")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                         # noqa: E731
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:600]), flush=True)


sl = open(STUBS, encoding="utf-8").read().splitlines()
last = max(i for i, ln in enumerate(sl) if ln.startswith("BGRUN START"))           # the log appends; only its LAST run counts
ret = [(i + 1, ln) for i, ln in enumerate(sl) if i > last and ln.startswith("RETIRED ")]
gate("E1 stubs log (last run, rc=0) retires exactly ONE wire, w3040", any(ln.startswith("BGRUN END rc=0") for ln in sl[last:]) and len(ret) == 1 and ret[0][1].startswith("RETIRED w3040 "), ret)
R = json.load(open(READ, encoding="utf-8"))
gate("E2 scratch read: 53 items, extra [], header '53 errors and warnings', md5 c83c9bea",
     R.get("item_count") == 53 and not R.get("extra") and R.get("n_reported") == 53 and md5(READ) == "c83c9beadad904d90d102342c82ec8d1",
     (R.get("item_count"), R.get("extra"), R.get("n_reported"), md5(READ)))
if all(ok for _l, ok in gates):
    p = json.load(open(PRED, encoding="utf-8"))
    el = p["errorlist"]
    el["removed"]["p3b_x_img_src_w3040"] = 1
    el["predicted_total"] = el["bed_total"] - sum(el["removed"].values())
    el["row_sources"]["p3b_x_img_src_w3040"] = ("-1: w3040 (#6810 'Image Out' t6865, source-only in P3a) retired by the Image Out crossing "
                                                "(plan_ring_p3b1.json:476-486, net re-created PD256(c)); offline graph diff {0}:{1}; scratch read 53 "
                                                "(stage_d1_ring_p3b1_el_scratch.log:183); PD273(a)/(b) - UNVERIFIED by uid (read items carry none)"
                                                .format(os.path.relpath(STUBS, ROOT).replace("\\", "/"), ret[0][0]))
    json.dump(p, open(PRED, "w", encoding="utf-8"), indent=1)
    chk = json.load(open(PRED, encoding="utf-8"))["errorlist"]
    gate("E3 pred errorlist predicted_total == 53, removed sum 2", chk["predicted_total"] == 53 and sum(chk["removed"].values()) == 2, chk["removed"])
    cc = R.get("class_counts") or {}
    pin = {"schema": "ring-p3b1-pin/1", "new_count": 0, "new_items": [], "new_norm": [], "predicted": el.get("new_items_predicted"),
           "total": R["item_count"], "per_class": cc, "read": os.path.relpath(READ, ROOT), "expected": "tools\\bench\\errorlist_expected_scratch_ring_p3b1_pred.json",
           "scratch": R.get("bed"), "scratch_md5": R.get("bed_md5_after"), "t": time.time(),
           "written_by": "card 131-5 diag_c131_5_s4_el.py from the 131-4 scratch read (extra []), PD273(b): expected 53"}
    json.dump(pin, open(PINF, "w", encoding="utf-8"), indent=1)
    gate("E4 pin written: new_count 0, total 53", json.load(open(PINF, encoding="utf-8"))["total"] == 53, md5(PINF))
    gate("E5 loose-ends class in the read == 22", cc.get("wirewirehaslooseends") == 22, cc.get("wirewirehaslooseends"))
n = sum(1 for _l, ok in gates if ok)
ff = next((lab for lab, ok in gates if not ok), None)
arts = [{"path": os.path.relpath(x, ROOT), "md5": md5(x)} for x in (PRED, PINF)] if ff is None else []
print(protocol.result_line(protocol.make_result(n, len(gates) - n, ff, arts)), flush=True)
sys.exit(0 if ff is None else 1)
