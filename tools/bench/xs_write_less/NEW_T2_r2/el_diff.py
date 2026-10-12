# ---
# labview: none
# hardware: none
# ---
"""el_diff.py - Error List items in one read but not the other (per item class, with counts), then a RESULT line.

  py el_diff.py <errorlist_a.json> <errorlist_b.json>

Item class = errorlist_check.class_counts(items, ocr=True) key (raw text normalised, OCR aliases folded), so an OCR
spelling change ('anvthing') or spacing change is not reported as a difference. No second parser or normaliser.
"""
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, TOOLS)
from errorlist_check import class_counts, norm_ocr  # noqa: E402


# shortcut: compares by item text only, so two same-text items at different diagram places are one class with a
# count; upgrade to a position/uid key once Error List reads carry the object uid (today uid=None).
def diff(items_a, items_b):
    """(only_a, only_b): {class key: surplus count} for each side."""
    ca, cb = Counter(class_counts(items_a, ocr=True)), Counter(class_counts(items_b, ocr=True))
    return dict(ca - cb), dict(cb - ca)


def label(items, key):
    """The first raw text in items whose class key is key (readable name for a folded key)."""
    return next((it.get("raw") for it in items if norm_ocr(it.get("raw")) == key), key)


_a = [{"raw": "Wire: Wire has loose ends."}, {"raw": "This wire is not connected to anything."}] * 2
_b = [{"raw": "This wire is not connected to anvthing."}, {"raw": "Wire:Wire has loose ends."}]
assert diff(_a, _b) == ({norm_ocr(_a[0]["raw"]): 1, norm_ocr(_a[1]["raw"]): 1}, {})
assert diff([], []) == ({}, {})
assert diff([], _b)[1] and not diff([], _b)[0]
assert label(_b, norm_ocr("Wire: Wire has loose ends.")) == "Wire:Wire has loose ends."

if len(sys.argv) != 3:
    print("RESULT " + json.dumps({"ok": False, "why": "usage: el_diff.py <a.json> <b.json>"}))
    sys.exit(2)
paths = sys.argv[1:]
missing = [p for p in paths if not os.path.isfile(p)]
if missing:
    print("RESULT " + json.dumps({"ok": False, "why": "missing file", "files": missing}))
    sys.exit(1)

reads = [json.load(open(p, encoding="utf-8")) for p in paths]
items = [r.get("items") or [] for r in reads]
only = diff(items[0], items[1])
for side, (p, its, d) in enumerate(zip(paths, items, only)):
    print("only in %s (%d of %d items):" % (os.path.basename(p), sum(d.values()), len(its)))
    for k, n in sorted(d.items()):
        print("  %2d x %s" % (n, label(its, k)))
    if not d:
        print("  (none)")
print("RESULT " + json.dumps({
    "ok": True, "n_items": [len(i) for i in items], "n_reported": [r.get("n_reported") for r in reads],
    "only_a": {label(items[0], k): n for k, n in only[0].items()},
    "only_b": {label(items[1], k): n for k, n in only[1].items()}}))
