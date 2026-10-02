r"""diag_c134_6_el_items - card 134-6 step 2 (PD291(c)), the review's offline item-level test
(archive/peer/2026-10-02-c134-5-el-classrange.md:55-59): which entries of P3b-1's 53-item expected list
(errorlist_expected_D1_ring_p3b1_20261002_060910.json) are NOT matched by any item of the scratch-b read
(errorlist_scratch_c134_5_ring_p3b2b_20261002_112928_20261002_113807.json), using errorlist_check._hit (norm + OCR fallback) and
the checker's own greedy assignment (errorlist_check.compare, :418-432). Prints every expected entry (label, rule, count, used)
and, for each unmatched one, its full entry text. Also lists, per entry, how many read items its rule COULD match (so a greedy
order artefact is visible). Facts only; no launch decision. Touches no LabVIEW.
PRIOR ART: errorlist_check.compare / _hit / class_counts (reused, not re-implemented except the per-entry bookkeeping compare
does not return: its `missing` is e.get('match'), None for norm_all entries -> 'missing: [null, null]').
PREDICTION: E1 inputs at md5; E2 compare's own missing count == 2 (== the verdict file's); E3 exactly 2 unmatched entry slots,
both entries whose rule is the loose-ends class ('wirewirehasloose' in their folded rule) - REPORTED either way.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c134_6_el_items.log -- py -u tools/bench/diag_c134_6_el_items.py"""
import copy, hashlib, json, os, sys                                                    # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol, errorlist_check as EC                                                 # noqa: E401,E402
EXP = ("tools/bench/errorlist_expected_D1_ring_p3b1_20261002_060910.json", None)
RD = ("tools/bench/errorlist_scratch_c134_5_ring_p3b2b_20261002_112928_20261002_113807.json", "2a5840d09a59acba8b47099a84ec7570")
md5 = lambda p: hashlib.md5(open(os.path.join(ROOT, p), "rb").read()).hexdigest()     # noqa: E731
J = lambda p: json.load(open(os.path.join(ROOT, p), encoding="utf-8"))                 # noqa: E731
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:900]), flush=True)


gate("E1 read file at card md5", md5(RD[0]) == RD[1], md5(RD[0]))
print("  FACT expected file md5 {0}".format(md5(EXP[0])), flush=True)
ex, rd = J(EXP[0]), J(RD[0])
items = copy.deepcopy(rd["items"])
_x, missing, usage = EC.compare(copy.deepcopy(items), ex["expected"])
gate("E2 compare's missing count == verdict file's ({0} vs {1})".format(len(missing), len(rd.get("missing") or [])), len(missing) == len(rd.get("missing") or []) == 2)
left = [dict(e, count=int(e.get("count", 1))) for e in ex["expected"]]
used = [0] * len(left)
holder = [[] for _ in left]
for it in items:
    txt = "%s %s" % (it.get("raw") or "", it.get("detail") or "")
    k = next((i for i, e in enumerate(left) if e["count"] > 0 and EC._hit(e, txt)), None)
    if k is not None:
        used[k] += 1; left[k]["count"] -= 1; holder[k].append(it.get("index"))         # noqa: E702
can = [sum(1 for it in items if EC._hit(e, "%s %s" % (it.get("raw") or "", it.get("detail") or ""))) for e in ex["expected"]]
for i, e in enumerate(ex["expected"]):
    rule = e.get("norm_all") or e.get("norm_any") or e.get("match")
    print("  ENTRY {0:2d} count {1} used {2} could-match {3} rule {4} | {5}".format(
        i, e.get("count", 1), used[i], can[i], json.dumps(rule), str(e.get("label"))[:220]), flush=True)
un = [(i, left[i]["count"]) for i in range(len(left)) if left[i]["count"] > 0]
for i, n in un:
    print("  UNMATCHED entry {0} x{1}: {2}".format(i, n, json.dumps(ex["expected"][i], ensure_ascii=False)[:1500]), flush=True)
gate("E3 unmatched slots == 2 ({0})".format(un), sum(n for _i, n in un) == 2, un)
loose = all("wirewirehasloose" in EC.ocr_fold("".join(ex["expected"][i].get("norm_all") or ex["expected"][i].get("norm_any") or [])) for i, _n in un)
gate("E4 every unmatched entry is a loose-ends class entry", un and loose, [ex["expected"][i].get("norm_all") for i, _n in un])
n_ = sum(1 for _l, ok in gates if ok)
ff = next((lab for lab, ok in gates if not ok), None)
print(protocol.result_line(protocol.make_result(n_, len(gates) - n_, ff, [])), flush=True)
sys.exit(0 if ff is None else 1)
