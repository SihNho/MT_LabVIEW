# ---
# labview: none
# hardware: none
# evidence: tools/bench/diag_c164_a3_5_elexp.py
# ---
r"""diag_c165_a3_4_elexp - card 165-3-4 (OFFLINE, no LabVIEW; PD354(a), PD370(a), PD396(e)): the Error List expected file of P5-2 step 5's ADOPTED file
(claudeDev\D1_ring_p5s02e_20261010_172913.vi == its byte copy D1_ring_p5_20261010_172913.vi, 75773b0d, diag_c165_a3_4_adopt.log), built MECHANICALLY
from its full --role final read, and the item-by-item comparison against the PREDICTED step-5 end errorlist_predicted_D1_ring_p5s02e_end.json
(2a8e2984, predicted 49, upper 51). COPY of tools/bench/diag_c164_a3_5_elexp.py (card 164-3-5, ran 5/0); changed lines ONLY: base expected = the
predicted step-5 end 2a8e2984, old read = the p5s02d read errorlist_D1_ring_p5s02d_20261010_152518_20261010_153416.json 7450dd98, pred
plan_ring_p5s02e_pred.json, VI = the read p5s02e file 75773b0d, HAND 49, labels. RECORD-only (no gate on the counts, PD354); classes by the same elcls.
PREDICTION CONTRACT: R read items == n_reported; V file md5 == 75773b0d; X compare(read, new expected) extra [] missing []; T total <= items.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c165_a3_4_elexp.log -- py -u tools/bench/diag_c165_a3_4_elexp.py <read json>"""
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
OLDREAD = os.path.join(B, "errorlist_D1_ring_p5s02d_20261010_152518_20261010_153416.json")   # 7450dd98, the p5s02d read
S08 = os.path.join(B, "errorlist_predicted_D1_ring_p5s02e_end.json")                         # 2a8e2984 (predicted step-5 end; variable name kept from the copy)
PREDF = os.path.join(B, "plan_ring_p5s02e_pred.json")
VI = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_ring_p5s02e_20261010_172913.vi"
VIM = "75773b0ded2a08586bb1a542ddda5af6"
HAND = 49                                                                                    # errorlist_predicted_D1_ring_p5s02e_end.json total
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
gate("S predicted step-5 end md5 2a8e2984, p5s02d read md5 7450dd98", md5(S08).startswith("2a8e2984") and md5(OLDREAD).startswith("7450dd98"), (md5(S08), md5(OLDREAD)))
ext, mis0, usage = EC.compare(copy.deepcopy(items), s08["expected"])
print("FACT compare(read, predicted 2a8e2984): extra {0} | missing {1}".format(ext, mis0), flush=True)
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
    exp.append({"norm_all": [k], "count": v["n"], "label": "{0} (new in P5-2e, measured)".format(v["raw"] or "(raw '' on OCR) " + k[:80]),
                "cite": "card 165-3-4: read items {0} of {1} not licensed by any predicted step-5 entry (2a8e2984)".format(v["idx"], rel(READ))})
    added.append("{0} x{1} items {2}".format(k, v["n"], v["idx"]))
print("FACT dropped predicted entries (0 items licensed): {0}".format(dropped), flush=True)
print("FACT added entries (read items no predicted entry licenses): {0}".format(added), flush=True)
ex, mi, _ = EC.compare(copy.deepcopy(items), exp)
gate("X compare(read items, new expected): extra [] missing []", not ex and not mi, {"extra": ex, "missing": mi})
total = sum(int(e["count"]) for e in exp)
gate("T total {0} == sum(counts) and <= items {1}".format(total, len(items)), total <= len(items), total)
out = {"schema": "errorlist-expected/1", "bed": VI, "bed_md5": VIM,
       "decided_by": "card 165-3-4 (PD354(a), PD370(a), PD396(e)): the predicted step-5 end's entries with count = items licensed in the measured read; "
                     "entries licensing none dropped: " + ("; ".join(dropped) or "none") + "; entries added for unlicensed read items: " + ("; ".join(added) or "none"),
       "measured_from": rel(READ), "measured_md5": md5(READ), "base_expected": rel(S08), "total": total, "expected": exp,
       "format_note": s08.get("format_note")}
json.dump(out, open(NEW, "w", encoding="utf-8"), indent=1)
ARTS.append({"path": rel(NEW), "md5": md5(NEW)})
print("FACT wrote {0} md5 {1} total {2} entries {3}".format(rel(NEW), md5(NEW), total, len(exp)), flush=True)
o = J(OLDREAD)
a, b = EC.class_counts(items), EC.class_counts(o["items"])
diff = dict((k, (a.get(k, 0), b.get(k, 0))) for k in sorted(set(a) | set(b)) if a.get(k, 0) != b.get(k, 0))
print("RECORD new read total {0} vs p5s02d read 7450dd98 total {1}".format(len(items), len(o["items"])), flush=True)
for k in sorted(set(a) | set(b)):
    print("RECORD class {0!r}: new {1} | p5s02d {2}".format(k, a.get(k, 0), b.get(k, 0)), flush=True)
print("RECORD per-class differences vs p5s02d (new, p5s02d): {0}".format(diff or "none"), flush=True)
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
print("RECORD elcls per-class diff (read - p5s02d {0}) {1}; total diff {2:+}".format(len(o["items"]), json.dumps(s8diff, sort_keys=True), len(items) - len(o["items"])), flush=True)
print("RECORD read total {0} vs predicted {1}: {2:+}".format(len(items), HAND, len(items) - HAND), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
sys.exit(1 if G["fail"] else 0)
