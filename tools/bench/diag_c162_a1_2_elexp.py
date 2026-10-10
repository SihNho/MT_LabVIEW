# ---
# labview: none
# hardware: none
# evidence: tools/bench/diag_c158_a3_2b_elexp.py
# ---
r"""diag_c162_a1_2_elexp - card 162-a1-2 (OFFLINE, no LabVIEW; PD354(a), PD370(a)): the Error List expected file of P5-2 step 2's ADOPTED file
claudeDev\D1_ring_p5s02b_20261010_105511.vi (f9ae7751, diag_c162_a1_2_adopt.log), built MECHANICALLY from its full --role final read, and the
item-by-item comparison against the PREDICTED step-2 end errorlist_predicted_D1_ring_p5s02b_end.json (79ec3207, predicted 51).
COPY of tools/bench/diag_c158_a3_2b_elexp.py (card 158-a3-2b) with ONLY names changed: base expected = the predicted step-2 end 79ec3207 (was the
P5-1 expected), old read = the p5s02a read errorlist_D1_ring_p5s02a_20261010_023239_20261010_024108.json 25d6084b, pred plan_ring_p5s02b_pred.json,
HAND 51, VI = the adopted P5-2b file, labels; the read json is argv[1]. RECORD-only (no gate on the counts, PD354); classes by the same elcls.
PREDICTION CONTRACT: R read items == n_reported; V file md5 == f9ae7751; X compare(read, new expected) extra [] missing []; T total <= items.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c162_a1_2_elexp.log -- py -u tools/bench/diag_c162_a1_2_elexp.py <read json>"""
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
OLDREAD = os.path.join(B, "errorlist_D1_ring_p5s02a_20261010_023239_20261010_024108.json")   # 25d6084b, the p5s02a read
S08 = os.path.join(B, "errorlist_predicted_D1_ring_p5s02b_end.json")                         # 79ec3207 (predicted step-2 end; variable name kept from the copy)
PREDF = os.path.join(B, "plan_ring_p5s02b_pred.json")
VI = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_ring_p5s02b_20261010_105511.vi"
VIM = "f9ae77513a0188f0d88652a44267b1dd"
HAND = 51                                                                                    # errorlist_predicted_D1_ring_p5s02b_end.json total
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
gate("V adopted file md5 == {0}; read bed == it".format(VIM[:8]), md5(VI) == VIM and os.path.basename(str(rd.get("bed"))) == os.path.basename(VI),
     (md5(VI), rd.get("bed")))
gate("S predicted step-2 end md5 79ec3207, p5s02a read md5 25d6084b", md5(S08).startswith("79ec3207") and md5(OLDREAD).startswith("25d6084b"), (md5(S08), md5(OLDREAD)))
ext, mis0, usage = EC.compare(copy.deepcopy(items), s08["expected"])
print("FACT compare(read, predicted 79ec3207): extra {0} | missing {1}".format(ext, mis0), flush=True)
exp, dropped, added = [], [], []
for e, u in zip(copy.deepcopy(s08["expected"]), usage):
    if u["used"] == 0:
        dropped.append("{0} x{1}".format(e.get("label"), e.get("count")))
        continue
    if u["used"] != int(e.get("count", 1)):
        e["cite"] = "{0}; count {1} -> {2} measured in {3}".format(e.get("cite"), e.get("count"), u["used"], rel(READ))
        print("FACT predicted entry {0!r}: count {1} -> used {2}".format(e.get("label"), e.get("count"), u["used"]), flush=True)
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
    exp.append({"norm_all": [k], "count": v["n"], "label": "{0} (new in P5-2b, measured)".format(v["raw"] or "(raw '' on OCR) " + k[:80]),
                "cite": "card 162-a1-2: read items {0} of {1} not licensed by any predicted step-2 entry (79ec3207)".format(v["idx"], rel(READ))})
    added.append("{0} x{1} items {2}".format(k, v["n"], v["idx"]))
print("FACT dropped predicted entries (0 items licensed): {0}".format(dropped), flush=True)
print("FACT added entries (read items no predicted entry licenses): {0}".format(added), flush=True)
ex, mi, _ = EC.compare(copy.deepcopy(items), exp)
gate("X compare(read items, new expected): extra [] missing []", not ex and not mi, {"extra": ex, "missing": mi})
total = sum(int(e["count"]) for e in exp)
gate("T total {0} == sum(counts) and <= items {1}".format(total, len(items)), total <= len(items), total)
out = {"schema": "errorlist-expected/1", "bed": VI, "bed_md5": VIM,
       "decided_by": "card 162-a1-2 (PD354(a), PD370(a)): the predicted step-2 end's entries with count = items licensed in the measured read; entries licensing "
                     "none dropped: " + ("; ".join(dropped) or "none") + "; entries added for unlicensed read items: " + ("; ".join(added) or "none"),
       "measured_from": rel(READ), "measured_md5": md5(READ), "base_expected": rel(S08), "total": total, "expected": exp,
       "format_note": s08.get("format_note")}
json.dump(out, open(NEW, "w", encoding="utf-8"), indent=1)
ARTS.append({"path": rel(NEW), "md5": md5(NEW)})
print("FACT wrote {0} md5 {1} total {2} entries {3}".format(rel(NEW), md5(NEW), total, len(exp)), flush=True)
o = J(OLDREAD)
a, b = EC.class_counts(items), EC.class_counts(o["items"])
diff = dict((k, (a.get(k, 0), b.get(k, 0))) for k in sorted(set(a) | set(b)) if a.get(k, 0) != b.get(k, 0))
print("RECORD new read total {0} vs p5s02a read 25d6084b total {1}".format(len(items), len(o["items"])), flush=True)
for k in sorted(set(a) | set(b)):
    print("RECORD class {0!r}: new {1} | p5s02a {2}".format(k, a.get(k, 0), b.get(k, 0)), flush=True)
print("RECORD per-class differences vs p5s02a (new, p5s02a): {0}".format(diff or "none"), flush=True)
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
print("RECORD elcls per-class diff (read - pred {0}) {1}; total diff {2:+}".format(el.get("predicted_total"), json.dumps(pdiff, sort_keys=True),
      len(items) - int(el.get("predicted_total") or 0)), flush=True)
print("RECORD elcls per-class diff (read - p5s02a {0}) {1}; total diff {2:+}".format(len(o["items"]), json.dumps(s8diff, sort_keys=True), len(items) - len(o["items"])), flush=True)
print("RECORD read total {0} vs predicted {1}: {2:+}".format(len(items), HAND, len(items) - HAND), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
sys.exit(1 if G["fail"] else 0)
