# ---
# labview: none
# hardware: none
# ---
r"""diag_c152_b3_1_elexp - card 152-b3-1 (OFFLINE, no LabVIEW; PD354(a), PD368(e)): the Error List expected file of P4 session 9's
adopted file claudeDev\D1_ring_p4s09_<stamp>.vi (path + md5 from diag_c152_p4s09v18_scratch_sum.json), built MECHANICALLY from its full --role final read.
COPIED from tools/bench/diag_c151_a1_1_elexp.py (6d73cbb5, card 151-a3-1, ran 5/0) with names changed (s07 -> s08 base: expected
errorlist_expected_D1_ring_p4s08_20261009_031503.json c19cde96, read errorlist_D1_ring_p4s08_20261009_031503_20261009_032121.json b5b9a3f1;
pred plan_ring_p4_s09v18_pred.json, predicted 46 (alternative_total 45 with carry)). RECORD-only (no gate, PD354); classes by the SAME elcls as
tools/recipes/stage_d1_ring_p4_s09v18_scratch.py:91-106 (copied). Changed lines: 5-13, 25-28, 63, 82-84, 93, 103-106, 111, 116-118.
PREDICTION CONTRACT: R read items == n_reported; V file md5 == sum final_md5; X compare(read, new expected) extra [] missing []; T total == items.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c152_b3_1_elexp.log -- py -u tools/bench/diag_c152_b3_1_elexp.py <read json>"""
import collections, copy, hashlib, json, os, re, sys                                        # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import errorlist_check as EC                                                                # noqa: E402
import elrule as ELR                                                                        # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                 # noqa: E731
J = lambda p: json.load(open(p, encoding="utf-8"))                                          # noqa: E731
READ = os.path.join(ROOT, sys.argv[1])
OLDREAD = os.path.join(B, "errorlist_D1_ring_p4s08_20261009_031503_20261009_032121.json")   # b5b9a3f1, the s08 read
S08 = os.path.join(B, "errorlist_expected_D1_ring_p4s08_20261009_031503.json")              # c19cde96
PREDF = os.path.join(B, "plan_ring_p4_s09v18_pred.json")
SUM = J(os.path.join(B, "diag_c152_p4s09v18_scratch_sum.json"))
VI, VIM = SUM["final"], SUM["final_md5"]
NEW = os.path.join(B, "errorlist_expected_{0}.json".format(os.path.splitext(os.path.basename(VI))[0]))
G, ARTS = {"pass": 0, "fail": 0, "first": None}, []
OCR_ALIASES = (("vl", "vi"), ("v", "y"))                                                    # == recipe:87


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)


def norm_ocr(s):                                                                            # == recipe:91-95
    k = re.sub(r"[^a-z0-9]", "", (s or "").lower())
    for a, b in OCR_ALIASES:
        k = k.replace(a, b)
    return k


def elcls(it):                                                                              # == recipe:98-106
    c = ELR.item_class("{0} {1}".format(it.get("raw", ""), it.get("detail", "")))
    if c:
        return c
    k = norm_ocr(it.get("raw"))
    if "unwiredorbadterminal" in k or ("requiredinput" in k and "notwired" in k):
        return "input"
    return "other:" + k


rd, s08 = J(READ), J(S08)
items = rd["items"]
gate("R read {0}: items {1} == n_reported {2}".format(rel(READ), len(items), rd.get("n_reported")), len(items) == rd.get("n_reported"))
gate("V adopted file md5 == sum final_md5 {0}; read bed == it".format(VIM[:8]), md5(VI) == VIM and os.path.basename(str(rd.get("bed"))) == os.path.basename(VI),
     (md5(VI), rd.get("bed")))
gate("S s08 expected md5 c19cde96, s08 read md5 b5b9a3f1", md5(S08).startswith("c19cde96") and md5(OLDREAD).startswith("b5b9a3f1"), (md5(S08), md5(OLDREAD)))
ext, _, usage = EC.compare(copy.deepcopy(items), s08["expected"])
exp, dropped, added = [], [], []
for e, u in zip(copy.deepcopy(s08["expected"]), usage):
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
    exp.append({"norm_all": [k], "count": v["n"], "label": "{0} (new in session 9, measured)".format(v["raw"] or "(raw '' on OCR) " + k[:80]),
                "cite": "card 152-b3-1: read items {0} of {1} not licensed by any s08 entry; pred plan_ring_p4_s09v18_pred.json errorlist.fixed".format(
                    v["idx"], rel(READ))})
    added.append("{0} x{1}".format(k, v["n"]))
print("FACT dropped s08 entries (0 items licensed): {0}".format(dropped), flush=True)
print("FACT added entries (read items no s08 entry licenses): {0}".format(added), flush=True)
ex, mi, _ = EC.compare(copy.deepcopy(items), exp)
gate("X compare(read items, new expected): extra [] missing []", not ex and not mi, {"extra": ex, "missing": mi})
total = sum(int(e["count"]) for e in exp)
gate("T total {0} == sum(counts) and <= items {1}".format(total, len(items)), total <= len(items), total)
out = {"schema": "errorlist-expected/1", "bed": VI, "bed_md5": VIM,
       "decided_by": "card 152-b3-1 (PD354(a), PD368(e)): s08's entries with count = items licensed in the measured read; entries licensing none dropped: "
                     + ("; ".join(dropped) or "none") + "; entries added for unlicensed read items: " + ("; ".join(added) or "none"),
       "measured_from": rel(READ), "measured_md5": md5(READ), "base_expected": rel(S08), "total": total, "expected": exp,
       "format_note": s08.get("format_note")}
json.dump(out, open(NEW, "w", encoding="utf-8"), indent=1)
ARTS.append({"path": rel(NEW), "md5": md5(NEW)})
print("FACT wrote {0} md5 {1} total {2} entries {3}".format(rel(NEW), md5(NEW), total, len(exp)), flush=True)
o = J(OLDREAD)
a, b = EC.class_counts(items), EC.class_counts(o["items"])
diff = dict((k, (a.get(k, 0), b.get(k, 0))) for k in sorted(set(a) | set(b)) if a.get(k, 0) != b.get(k, 0))
print("RECORD new read total {0} vs s08 read b5b9a3f1 total {1}".format(len(items), len(o["items"])), flush=True)
for k in sorted(set(a) | set(b)):
    print("RECORD class {0!r}: new {1} | s08 {2}".format(k, a.get(k, 0), b.get(k, 0)), flush=True)
print("RECORD per-class differences vs s08 (new, s08): {0}".format(diff or "none"), flush=True)
pr = J(PREDF)
el = pr.get("errorlist") or {}
want = (el.get("per_class") or {}).get("predicted") or {}
got = collections.Counter(elcls(x) for x in items)
got08 = collections.Counter(elcls(x) for x in o["items"])
pdiff = dict((c, got.get(c, 0) - want.get(c, 0)) for c in sorted(set(got) | set(want)) if got.get(c, 0) != want.get(c, 0))
s8diff = dict((c, got.get(c, 0) - got08.get(c, 0)) for c in sorted(set(got) | set(got08)) if got.get(c, 0) != got08.get(c, 0))
print("RECORD pred keyed to plan md5 {0}; predicted_total {1}; alternative_total {2}".format((pr.get("plan") or {}).get("md5"), el.get("predicted_total"),
      el.get("alternative_total")), flush=True)
print("RECORD elcls classes read {0}".format(json.dumps(dict(sorted(got.items())), sort_keys=True)), flush=True)
print("RECORD elcls per-class diff (read - pred 46) {0}; total diff {1:+}".format(json.dumps(pdiff, sort_keys=True), len(items) - int(el.get("predicted_total") or 0)), flush=True)
print("RECORD elcls per-class diff (read - s08 46) {0}; total diff {1:+}".format(json.dumps(s8diff, sort_keys=True), len(items) - len(o["items"])), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
sys.exit(1 if G["fail"] else 0)
