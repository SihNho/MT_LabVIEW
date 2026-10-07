# ---
# labview: none
# hardware: none
# ---
r"""diag_c145_2_elfacts - card 145-a1-2 (OFFLINE, read-only): print the facts of the s04 work copy's Error List read
(errorlist_D1_ring_p4s04_20261007_215031_20261007_220024.json, diag_c145_2_el.log): total, per-class counts vs the s03 expected file,
the extra and missing entries, and the pred's predicted new/closed items. No diagnosis, nothing written.
PREDICTION: the read file exists and has 58 items (diag_c145_2_el.log) -> RESULT 1/0.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c145_2_elfacts.log -- py -u tools/bench/diag_c145_2_elfacts.py"""
import collections, json, os, sys                                                          # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import errorlist_check as EC                                                                # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
R = json.load(open(os.path.join(B, "errorlist_D1_ring_p4s04_20261007_215031_20261007_220024.json"), encoding="utf-8"))
EX = json.load(open(os.path.join(B, "errorlist_expected_D1_ring_p4s03_20261007_202957.json"), encoding="utf-8"))
P = json.load(open(os.path.join(B, "plan_ring_p4_s04v18_pred.json"), encoding="utf-8"))["errorlist"]
items = R.get("items") or []
print("FACT items {0} / window N {1}; verdict {2}; by_design {3}".format(len(items), R.get("n_reported"), R.get("verdict"), R.get("by_design")), flush=True)
print("FACT extra {0}".format(json.dumps(R.get("extra"), ensure_ascii=False)), flush=True)
print("FACT missing {0}".format(json.dumps(R.get("missing"), ensure_ascii=False)), flush=True)
cc = collections.Counter(EC.norm(i.get("raw")) for i in items)
ec = dict((" ".join(e.get("norm_all") or []), int(e.get("count", 1))) for e in EX["expected"])
print("FACT read per-class {0}".format(json.dumps(dict(sorted(cc.items())), ensure_ascii=False)), flush=True)
print("FACT s03 expected per-entry {0} (total {1})".format(json.dumps(ec, ensure_ascii=False), EX.get("total")), flush=True)
for i in items:
    if i.get("raw") in (R.get("extra") or []) or not i.get("licensed_by"):
        print("FACT unlicensed item {0}: raw {1!r} detail {2!r} show_error {3}".format(i.get("index"), i.get("raw"), str(i.get("detail"))[:120],
              json.dumps(i.get("show_error"), ensure_ascii=False, default=str)[:300]), flush=True)
print("FACT pred predicted_total {0}; new {1}; closed {2}".format(P["predicted_total"], P["fixed"]["new_items"], P["fixed"]["closed_items"]), flush=True)
ok = len(items) == 58
print("GATE {0} | read file has 58 items".format("PASS" if ok else "FAIL"), flush=True)
print(protocol.result_line(protocol.make_result(int(ok), int(not ok), None if ok else "items", [])), flush=True)
sys.exit(0 if ok else 1)
