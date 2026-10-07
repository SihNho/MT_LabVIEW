# ---
# labview: none
# hardware: none
# ---
r"""diag_c146_a1_4_elfacts - card 146-a1-4 (OFFLINE, read-only): print the facts of the s05 work copy's Error List read
(errorlist_D1_ring_p4s05_20261008_002621_20261008_003324.json, diag_c146_a1_4_el.log): total, per-class counts of the read, the s04 expected
file's entries with the count each one matched (errorlist_check.compare usage), the missing entries, and the pred's predicted new/closed items.
COPIED from tools/bench/diag_c145_2_elfacts.py with names changed + the per-entry usage print. No diagnosis, nothing written.
PREDICTION: the read file exists, md5 06a59001, and has 55 items (diag_c146_a1_4_el.log:90) -> RESULT 2/0.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c146_a1_4_elfacts.log -- py -u tools/bench/diag_c146_a1_4_elfacts.py"""
import collections, copy, hashlib, json, os, sys                                            # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import errorlist_check as EC                                                                # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
RF = os.path.join(B, "errorlist_D1_ring_p4s05_20261008_002621_20261008_003324.json")
R = json.load(open(RF, encoding="utf-8"))
EX = json.load(open(os.path.join(B, "errorlist_expected_D1_ring_p4s04_20261007_215031.json"), encoding="utf-8"))
P = json.load(open(os.path.join(B, "plan_ring_p4_s05v18_pred.json"), encoding="utf-8"))["errorlist"]
items = R.get("items") or []
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, d), flush=True)


gate("read file md5 06a59001", hashlib.md5(open(RF, "rb").read()).hexdigest().startswith("06a59001"))
print("FACT items {0} / window N {1}; verdict {2}; by_design {3}".format(len(items), R.get("n_reported"), R.get("verdict"), R.get("by_design")), flush=True)
print("FACT extra {0}".format(json.dumps(R.get("extra"), ensure_ascii=False)), flush=True)
print("FACT missing {0}".format(json.dumps(R.get("missing"), ensure_ascii=False)), flush=True)
cc = collections.Counter(EC.norm(i.get("raw")) for i in items)
print("FACT read per-class {0}".format(json.dumps(dict(sorted(cc.items())), ensure_ascii=False)), flush=True)
ex, mi, usage = EC.compare(copy.deepcopy(items), EX["expected"])
print("FACT compare usage {0}".format(json.dumps(usage, ensure_ascii=False, default=str)[:1500]), flush=True)
for n, e in enumerate(EX["expected"]):
    print("FACT s04 entry {0}: norm_all {1} count {2} label {3!r}".format(n, e.get("norm_all"), e.get("count"), str(e.get("label"))[:110]), flush=True)
for i in items:
    print("FACT item {0}: raw {1!r} detail {2!r} licensed_by {3!r}".format(i.get("index"), str(i.get("raw"))[:90], str(i.get("detail"))[:90],
                                                                       i.get("licensed_by")), flush=True)
print("FACT pred predicted_total {0}; new {1}; closed {2}; open_at_end {3}".format(P["predicted_total"], P["fixed"]["new_items"],
                                                                                 P["fixed"]["closed_items"], P["fixed"].get("open_at_end")), flush=True)
gate("read file has 55 items", len(items) == 55, len(items))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
