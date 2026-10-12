# ---
# labview: none
# hardware: none
# ---
r"""el_diff - the Error List items in one stored read but not the other (OFFLINE, json only, writes nothing).
Found before writing: errorlist_check.class_counts(items, ocr=True) ({norm_ocr(raw): n}, tools/errorlist_check.py:471) is the
item key every Error List check already uses; this file CALLS it and only subtracts the two count maps.
    py tools/bench/xs_write_less/NEW_T2_r1/el_diff.py <a.json> <b.json>"""
import collections, json, os, sys                                                          # noqa: E401
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")))
from errorlist_check import class_counts, norm_ocr                                         # noqa: E402


def diff(items_a, items_b):
    """(only_a, only_b): {class key: n} of the items in one read beyond the other, counts included, and {key: raw} for display."""
    # shortcut: keys on the OCR-folded raw text only (vi name, row, detail ignored); upgrade if two classes share a raw text.
    ca, cb = collections.Counter(class_counts(items_a, ocr=True)), collections.Counter(class_counts(items_b, ocr=True))
    raw = {norm_ocr(it.get("raw")): it.get("raw") or "" for it in list(items_b or []) + list(items_a or [])}
    return dict(ca - cb), dict(cb - ca), raw


# self-check: counts matter (2 vs 1 of a class is one extra), OCR aliases fold, empty input is fine
_a = [{"raw": "X: y"}, {"raw": "X: y"}, {"raw": "SubVI z"}]
_b = [{"raw": "X: y"}, {"raw": "SubVl z"}, {"raw": "W"}]
assert diff(_a, _b)[:2] == ({"xy": 1}, {"w": 1}), diff(_a, _b)
assert diff([], [])[:2] == ({}, {})


def main(pa, pb):
    a, b = (json.load(open(p, encoding="utf-8")).get("items") or [] for p in (pa, pb))
    only_a, only_b, raw = diff(a, b)
    for name, p, only in (("A", pa, only_a), ("B", pb, only_b)):
        print("only in %s (%s): %d item(s)" % (name, os.path.basename(p), sum(only.values())))
        for k, n in sorted(only.items()):
            print("  %d x %s" % (n, raw[k] or "(empty raw)"))
    return {"ok": True, "a_items": len(a), "b_items": len(b),
            "only_a": sum(only_a.values()), "only_b": sum(only_b.values())}


if __name__ == "__main__":
    try:
        if len(sys.argv) != 3:
            raise ValueError("usage: el_diff.py <a.json> <b.json>")
        r = main(sys.argv[1], sys.argv[2])
    except (OSError, ValueError) as e:
        r = {"ok": False, "error": "%s: %s" % (type(e).__name__, e)}
    print("RESULT " + json.dumps(r))
    sys.exit(0 if r["ok"] else 1)
