# ---
# labview: none
# hardware: none
# evidence: tools/bench/diag_c165_a3_4_el.log:82-85
# ---
r"""diag_c165_a3_4_elcmp - card 165-3-4 (OFFLINE, read-only, writes nothing): the Error List read of the adopted step-5 file
(errorlist_D1_ring_p5s02e_20261010_172913_20261010_173731.json, 47 items) ended `missing 2` / ERRORLIST-VERDICT MISMATCH against the predicted
step-5 end errorlist_predicted_D1_ring_p5s02e_end.json (2a8e2984, 49). This prints, item by item, which predicted entries were licensed fewer
times than their count (errorlist_check.compare usage), and per class (errorlist_check.class_counts) read vs the p5s02d read 7450dd98. It is the
compare half of diag_c165_a3_4_elexp.py WITHOUT writing an expected file (the read did not match its prediction; nothing is adopted from it).
PREDICTION: prints; RESULT PASS when the files load (the counts are records, not gates).
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c165_a3_4_elcmp.log -- py -u tools/bench/diag_c165_a3_4_elcmp.py"""
import copy, json, os, sys                                                                   # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import errorlist_check as EC                                                                # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
J = lambda p: json.load(open(os.path.join(B, p), encoding="utf-8"))                          # noqa: E731
rd = J("errorlist_D1_ring_p5s02e_20261010_172913_20261010_173731.json")
pr = J("errorlist_predicted_D1_ring_p5s02e_end.json")
old = J("errorlist_D1_ring_p5s02d_20261010_152518_20261010_153416.json")
items = rd["items"]
ext, mis, usage = EC.compare(copy.deepcopy(items), pr["expected"])
print("FACT read items {0} (n_reported {1}); predicted total {2}; extra {3}; missing {4}".format(len(items), rd.get("n_reported"), pr.get("total"), ext, mis),
      flush=True)
for i, (e, u) in enumerate(zip(pr["expected"], usage)):
    if u["used"] != int(e.get("count", 1)):
        print("SHORT entry {0}: label {1!r} count {2} used {3} | status {4} | norm {5} | cite {6}".format(
            i, e.get("label"), e.get("count"), u["used"], e.get("status") or e.get("kind"), (e.get("norm_all") or e.get("norm"))[:3] if
            (e.get("norm_all") or e.get("norm")) else None, str(e.get("cite"))[:200]), flush=True)
a, b = EC.class_counts(items), EC.class_counts(old["items"])
for k in sorted(set(a) | set(b)):
    print("RECORD class {0!r}: read {1} | p5s02d read {2} | d {3:+}".format(k, a.get(k, 0), b.get(k, 0), a.get(k, 0) - b.get(k, 0)), flush=True)
print(protocol.result_line(protocol.make_result(1, 0, None, [])), flush=True)
