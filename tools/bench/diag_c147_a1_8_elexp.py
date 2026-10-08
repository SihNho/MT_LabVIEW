# ---
# labview: none
# hardware: none
# ---
r"""diag_c147_a1_8_elexp - card 147-a1-8 (OFFLINE, no LabVIEW): the Error List expected file of P4 session 6's adopted file
claudeDev\D1_ring_p4s06_<stamp>.vi (path + md5 from diag_c147_p4s06v18_scratch_sum.json), built MECHANICALLY from its full --role final read.
COPIED from tools/bench/diag_c147_a1_4_elexp.py (written by card 147-a1-4, unrun) with only the card id in the cites changed:
s05's expected entries (errorlist_expected_D1_ring_p4s05_20261008_002621.json, 6f2ca28a) each with count = the number of read items
errorlist_check.compare licensed by it; entries licensing 0 items are dropped (listed); read items no s05 entry licenses are added as one entry per
norm(raw) class with the measured count (listed, cite = the read file). The new read's total and per-class counts are then RECORDED against the
s05 read b654430d (PD354(a), not a gate).
PREDICTION CONTRACT: R read items == n_reported; V file md5 == sum final_md5; X compare(read, new expected) extra [] missing []; T total == items.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c147_a1_8_elexp.log -- py -u tools/bench/diag_c147_a1_8_elexp.py <read json>"""
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
READ = os.path.join(ROOT, sys.argv[1])
OLDREAD = os.path.join(B, "errorlist_D1_ring_p4s05_20261008_002621_20261008_012323.json")   # b654430d, the s05 read
S05 = os.path.join(B, "errorlist_expected_D1_ring_p4s05_20261008_002621.json")
SUM = J(os.path.join(B, "diag_c147_p4s06v18_scratch_sum.json"))
VI, VIM = SUM["final"], SUM["final_md5"]
NEW = os.path.join(B, "errorlist_expected_{0}.json".format(os.path.splitext(os.path.basename(VI))[0]))
G, ARTS = {"pass": 0, "fail": 0, "first": None}, []


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)


rd, s05 = J(READ), J(S05)
items = rd["items"]
gate("R read {0}: items {1} == n_reported {2}".format(rel(READ), len(items), rd.get("n_reported")), len(items) == rd.get("n_reported"))
gate("V adopted file md5 == sum final_md5 {0}; read bed == it".format(VIM[:8]), md5(VI) == VIM and os.path.basename(str(rd.get("bed"))) == os.path.basename(VI),
     (md5(VI), rd.get("bed")))
gate("S s05 expected md5 6f2ca28a, s05 read md5 b654430d", md5(S05).startswith("6f2ca28a") and md5(OLDREAD).startswith("b654430d"), (md5(S05), md5(OLDREAD)))
ext, _, usage = EC.compare(copy.deepcopy(items), s05["expected"])
exp, dropped, added = [], [], []
for e, u in zip(copy.deepcopy(s05["expected"]), usage):
    if u["used"] == 0:
        dropped.append("{0} x{1}".format(e.get("label"), e.get("count")))
        continue
    if u["used"] != int(e.get("count", 1)):
        e["cite"] = "{0}; count {1} -> {2} measured in {3}".format(e.get("cite"), e.get("count"), u["used"], rel(READ))
    e["count"] = u["used"]
    exp.append(e)
byk = {}
for raw in ext:
    it = next((i for i in items if i.get("raw") == raw), {})
    k = EC.norm(raw) or EC.norm(it.get("detail"))
    byk.setdefault(k, {"n": 0, "raw": raw, "idx": []})
    byk[k]["n"] += 1
    byk[k]["idx"].append(it.get("index"))
for k, v in sorted(byk.items()):
    exp.append({"norm_all": [k], "count": v["n"], "label": "{0} (new in session 6, measured)".format(v["raw"] or "(raw '' on OCR) " + k[:80]),
                "cite": "card 147-a1-8: read items {0} of {1} not licensed by any s05 entry; pred plan_ring_p4_s06v18_pred.json errorlist.fixed".format(
                    v["idx"], rel(READ))})
    added.append("{0} x{1}".format(k, v["n"]))
print("FACT dropped s05 entries (0 items licensed): {0}".format(dropped), flush=True)
print("FACT added entries (read items no s05 entry licenses): {0}".format(added), flush=True)
ex, mi, _ = EC.compare(copy.deepcopy(items), exp)
gate("X compare(read items, new expected): extra [] missing []", not ex and not mi, {"extra": ex, "missing": mi})
total = sum(int(e["count"]) for e in exp)
gate("T total {0} == sum(counts) and <= items {1}".format(total, len(items)), total <= len(items), total)
out = {"schema": "errorlist-expected/1", "bed": VI, "bed_md5": VIM,
       "decided_by": "card 147-a1-8 (PD354(a)): s05's entries with count = items licensed in the measured read; entries licensing none dropped: "
                     + ("; ".join(dropped) or "none") + "; entries added for unlicensed read items: " + ("; ".join(added) or "none"),
       "measured_from": rel(READ), "measured_md5": md5(READ), "base_expected": rel(S05), "total": total, "expected": exp,
       "format_note": s05.get("format_note")}
json.dump(out, open(NEW, "w", encoding="utf-8"), indent=1)
ARTS.append({"path": rel(NEW), "md5": md5(NEW)})
print("FACT wrote {0} md5 {1} total {2} entries {3}".format(rel(NEW), md5(NEW), total, len(exp)), flush=True)
o = J(OLDREAD)
a, b = EC.class_counts(items), EC.class_counts(o["items"])
diff = dict((k, (a.get(k, 0), b.get(k, 0))) for k in sorted(set(a) | set(b)) if a.get(k, 0) != b.get(k, 0))
print("RECORD new read total {0} vs s05 read b654430d total {1}".format(len(items), len(o["items"])), flush=True)
for k in sorted(set(a) | set(b)):
    print("RECORD class {0!r}: new {1} | s05 {2}".format(k, a.get(k, 0), b.get(k, 0)), flush=True)
print("RECORD per-class differences (new, s05): {0}".format(diff or "none"), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
sys.exit(1 if G["fail"] else 0)
