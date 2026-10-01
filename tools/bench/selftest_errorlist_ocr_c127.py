"""selftest_errorlist_ocr_c127 - card 127-2 STEP 3 (OFFLINE, no LabVIEW, no COM): errorlist_check's ADD-ONLY OCR aliases
(norm_ocr / ocr_fold / class_counts(ocr=True) / _hit fallback) over RECORDED Error List reads of card 126-4.
PREDICTION: E1 norm() unchanged ('SubVI.'-> 'subvi', 'subvl' stays 'subvl'); E2 default class_counts of the bed read
(errorlist_D1_ring_p3a_20261001_180540_20261001_181801_raw.json, 55) and the copy's before-read (errorlist_c126_4_s1_before_*,
55) DIFFER (126-4's failing gate); E3 with ocr=True they are EQUAL; E4 copy before vs after-RLE (ocr=True) differ ONLY in
the 'wire has loose ends' class, by -1 (diag_c126_4_op.log:52-60); E5 _hit: a norm_any rule keyed 'subvi' matches an
item read 'subvl' (fallback) and a rule that did not match before still does not match unrelated text."""
import glob, json, os, sys    # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P, errorlist_check as EC    # noqa: E402,E401
B = os.path.join(ROOT, "tools", "bench")
ok = []


def gate(n, c, d=""):
    ok.append((n, bool(c)))
    print("{0}  {1}  {2}".format("PASS" if c else "FAIL", n, str(d)[:1200]), flush=True)


def items(p):
    d = json.load(open(p, encoding="utf-8"))
    return d.get("items") or d.get("rows") or []


bed = items(os.path.join(B, "errorlist_D1_ring_p3a_20261001_180540_20261001_181801_raw.json"))
bef = items(sorted(glob.glob(os.path.join(B, "errorlist_c126_4_s1_before_*_raw.json")))[-1])
aft = items(sorted(glob.glob(os.path.join(B, "errorlist_c126_4_s1_after_*_raw.json")))[-1])
gate("E1 norm() unchanged", EC.norm("input of SubVI.") == "inputofsubvi" and EC.norm("subvl") == "subvl"
     and EC.norm_ocr("subvl") == EC.norm_ocr("SubVI") and EC.norm_ocr("anvthing") == EC.norm_ocr("anything"))
d0 = (EC.class_counts(bed), EC.class_counts(bef))
diff0 = sorted(set(d0[0].items()) ^ set(d0[1].items()))
gate("E2 default class_counts bed (n {0}) vs copy-before (n {1}) DIFFER (126-4's byte-exact failure)".format(len(bed), len(bef)),
     len(bed) == 55 and len(bef) == 55 and bool(diff0), diff0)
d1 = (EC.class_counts(bed, ocr=True), EC.class_counts(bef, ocr=True))
gate("E3 class_counts(ocr=True) bed == copy-before", d1[0] == d1[1], sorted(set(d1[0].items()) ^ set(d1[1].items())))
ca = EC.class_counts(aft, ocr=True)
dk = dict((k, ca.get(k, 0) - d1[1].get(k, 0)) for k in set(ca) | set(d1[1]) if ca.get(k, 0) != d1[1].get(k, 0))
gate("E4 copy before -> after RLE (ocr=True): only 'wire has loose ends' -1 (n {0} -> {1})".format(len(bef), len(aft)),
     len(aft) == 54 and len(dk) == 1 and list(dk.values()) == [-1] and "looseends" in list(dk)[0], dk)
r = {"norm_any": [EC.norm("You have connected an output loop tunnel to an input of SubVI.")]}
gate("E5 _hit fallback: a 'subvi' rule matches a 'subvl' read; unrelated text still misses",
     EC._hit(r, "You have connected an output loop tunnel to an input of Subvl. Change the input")
     and not EC._hit(r, "Wire: Wire has loose ends"), r)
np_, nf = sum(1 for _n, c in ok if c), sum(1 for _n, c in ok if not c)
print(P.result_line(P.make_result(np_, nf, next((n for n, c in ok if not c), None))), flush=True)
sys.exit(1 if nf else 0)
