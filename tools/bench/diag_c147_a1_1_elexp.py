# ---
# labview: none
# hardware: none
# ---
r"""diag_c147_a1_1_elexp - card 147-a1-1 step 2 (OFFLINE, no LabVIEW): the Error List expected file of P4 session 5's adopted file
claudeDev\D1_ring_p4s05_20261008_002621.vi (3f9ac26b), built MECHANICALLY from a full --role final read: s04's expected entries
(errorlist_expected_D1_ring_p4s04_20261007_215031.json) each with count = the number of read items errorlist_check.compare licensed by it;
entries licensing 0 items are dropped (listed). Form copied from tools/bench/diag_c145_a2_1_elexp.py (card 145-a2-1).
Mode `pred`: from the cycle-146 read of the same bytes (06a59001) -> tools/bench/diag_c147_a1_1_elpred.json (the --expected of the new read).
Mode `final <read json>`: from the NEW read -> tools/bench/errorlist_expected_D1_ring_p4s05_20261008_002621.json, and the new read's total and
per-class counts compared with 06a59001 (a RECORD, PD354(a), not a gate).
PREDICTION CONTRACT: R read items == n_reported; V adopted md5 3f9ac26b; X compare(read, new expected) extra [] missing []; T total == items
  (55 for 06a59001); dropped == s04 entries 'Image In' (SubVI) and Shift Register (facts diag_c146_a1_4_facts.md).
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c147_a1_1_elexp_<mode>.log -- py -u tools/bench/diag_c147_a1_1_elexp.py <mode> [read]"""
import copy, hashlib, json, os, sys                                                         # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import errorlist_check as EC                                                                # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                 # noqa: E731
J = lambda p: json.load(open(p, encoding="utf-8"))                                          # noqa: E731
MODE = (sys.argv[1:] or ["pred"])[0]
OLDREAD = os.path.join(B, "errorlist_D1_ring_p4s05_20261008_002621_20261008_003324.json")
READ = OLDREAD if MODE == "pred" else os.path.join(ROOT, sys.argv[2])
S04 = os.path.join(B, "errorlist_expected_D1_ring_p4s04_20261007_215031.json")
NEW = os.path.join(B, "diag_c147_a1_1_elpred.json" if MODE == "pred" else "errorlist_expected_D1_ring_p4s05_20261008_002621.json")
VI = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_ring_p4s05_20261008_002621.vi"
VIM = "3f9ac26b69179eb53c202d90407ce7ee"
G, ARTS = {"pass": 0, "fail": 0, "first": None}, []


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)


rd, s04 = J(READ), J(S04)
items = rd["items"]
gate("R read {0}: items {1} == n_reported {2}".format(rel(READ), len(items), rd.get("n_reported")), len(items) == rd.get("n_reported"))
gate("V adopted file md5 3f9ac26b", md5(VI) == VIM, md5(VI))
_, _, usage = EC.compare(copy.deepcopy(items), s04["expected"])
exp, dropped = [], []
for e, u in zip(copy.deepcopy(s04["expected"]), usage):
    if u["used"] == 0:
        dropped.append("{0} x{1}".format(e.get("label"), e.get("count")))
        continue
    if u["used"] != int(e.get("count", 1)):
        e["cite"] = "{0}; count {1} -> {2} measured in {3}".format(e.get("cite"), e.get("count"), u["used"], rel(READ))
    e["count"] = u["used"]
    exp.append(e)
print("FACT dropped s04 entries (0 items licensed): {0}".format(dropped), flush=True)
ex, mi, _ = EC.compare(copy.deepcopy(items), exp)
gate("X compare(read items, new expected): extra [] missing []", not ex and not mi, {"extra": ex, "missing": mi})
total = sum(int(e["count"]) for e in exp)
gate("T total {0} == sum(counts) and <= items {1}".format(total, len(items)), total <= len(items), total)
out = {"schema": "errorlist-expected/1", "bed": VI, "bed_md5": VIM,
       "decided_by": "card 147-a1-1 (PD354(a)(c)): s04's entries with count = items licensed in the measured read; entries licensing none dropped: "
                     + "; ".join(dropped),
       "measured_from": rel(READ), "measured_md5": md5(READ), "base_expected": rel(S04), "total": total, "expected": exp,
       "format_note": s04.get("format_note")}
json.dump(out, open(NEW, "w", encoding="utf-8"), indent=1)
ARTS.append({"path": rel(NEW), "md5": md5(NEW)})
print("FACT wrote {0} md5 {1} total {2} entries {3}".format(rel(NEW), md5(NEW), total, len(exp)), flush=True)
if MODE != "pred":
    o = J(OLDREAD)
    a, b = EC.class_counts(items), EC.class_counts(o["items"])
    diff = dict((k, (a.get(k, 0), b.get(k, 0))) for k in sorted(set(a) | set(b)) if a.get(k, 0) != b.get(k, 0))
    print("RECORD new read total {0} vs 06a59001 total {1} (read md5 {2})".format(len(items), len(o["items"]), md5(OLDREAD)), flush=True)
    for k in sorted(set(a) | set(b)):
        print("RECORD class {0!r}: new {1} | 06a59001 {2}".format(k, a.get(k, 0), b.get(k, 0)), flush=True)
    print("RECORD per-class differences (new, old): {0}".format(diff or "none"), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
sys.exit(1 if G["fail"] else 0)
