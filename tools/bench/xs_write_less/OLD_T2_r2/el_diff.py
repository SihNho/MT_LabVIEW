# ---
# labview: none
# hardware: none
# ---
"""el_diff - items in one Error List read (errorlist_check JSON) but not the other, counted as a multiset
(the same row may appear several times). Key = errorlist_check.norm_ocr(raw), the shared OCR-folded form.

  py el_diff.py <a.json> <b.json>
Last line: RESULT {...}.
"""
import collections
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from errorlist_check import norm_ocr  # noqa: E402  stdlib-only at import; LabVIEW modules load lazily

INPUTS = os.path.join(ROOT, "tools", "bench", "xs_write_less", "inputs")
DEFAULT = (os.path.join(INPUTS, "errorlist_scratch_c140_3_ring_p4s01_20261002_205117_20261002_205859.json"),
           os.path.join(INPUTS, "errorlist_scratch_c141_p4s01_20261002_230228_20261002_230850.json"))


def load(path):
    items = json.load(open(path, encoding="utf-8"))["items"]
    count = collections.Counter(norm_ocr(it["raw"]) for it in items)
    text = {norm_ocr(it["raw"]): it["raw"] for it in items}
    return count, text


def main():
    a, b = sys.argv[1:3] if len(sys.argv) >= 3 else DEFAULT
    (ca, ta), (cb, tb) = load(a), load(b)
    only_a, only_b = ca - cb, cb - ca
    for name, only, text in ((a, only_a, ta), (b, only_b, tb)):
        print("only in {0}: {1}".format(os.path.basename(name), sum(only.values())))
        for k in sorted(only):
            print("  {0:>3} x {1}".format(only[k], text[k]))
    print("RESULT " + json.dumps({"a": os.path.basename(a), "b": os.path.basename(b),
                                  "n_a": sum(ca.values()), "n_b": sum(cb.values()),
                                  "only_a": sum(only_a.values()), "only_b": sum(only_b.values()),
                                  "rc": 0}))


if __name__ == "__main__":
    main()
