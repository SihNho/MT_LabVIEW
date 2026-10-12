# ---
# labview: none        # reads two saved Error List JSON files offline
# hardware: none
# ---
"""el_diff - items in one Error List read but not the other (multiset, keyed by errorlist_check.norm of `raw`).

  py el_diff.py [<a.json> <b.json>]       default: the c140_3 / c141 p4s01 pair in ../inputs
Prints the items only in A, then only in B, then a RESULT {...} line.
"""
import collections, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import errorlist_check as EC                                   # noqa: E402  (norm only; no LabVIEW import)

INPUTS = os.path.join(HERE, "..", "inputs")
DEFAULT = ("errorlist_scratch_c140_3_ring_p4s01_20261002_205117_20261002_205859.json",
           "errorlist_scratch_c141_p4s01_20261002_230228_20261002_230850.json")


def raws(path):
    return [it.get("raw") or "" for it in json.load(open(path, encoding="utf-8")).get("items") or []]


def only_in(a, b):
    """Raws of `a` left after removing, per norm key, as many as `b` holds (multiset difference)."""
    left = collections.Counter(EC.norm(r) for r in b)
    out = []
    for r in a:
        k = EC.norm(r)
        if left[k]:
            left[k] -= 1
        else:
            out.append(r)
    return out


def main():
    pa, pb = sys.argv[1:3] if len(sys.argv) >= 3 else [os.path.join(INPUTS, n) for n in DEFAULT]
    a, b = raws(pa), raws(pb)
    only_a, only_b = only_in(a, b), only_in(b, a)
    for name, path, rows in (("A", pa, only_a), ("B", pb, only_b)):
        print("only in %s (%s): %d" % (name, os.path.basename(path), len(rows)))
        for r, n in sorted(collections.Counter(rows).items()):
            print("  %2d x %s" % (n, r or "<empty raw>"))
    print("RESULT " + json.dumps({"a": os.path.basename(pa), "b": os.path.basename(pb), "n_a": len(a),
                                  "n_b": len(b), "only_a": len(only_a), "only_b": len(only_b),
                                  "identical": not only_a and not only_b}))


if __name__ == "__main__":
    main()
