# ---
# labview: none
# hardware: none
# ---
"""p6close_lineage - read-only: print the lineage facts of the final P6 VI and its 4 test VIs from the stored build records
(latest_build.json, p6fix_build.json). Opens no VI.
    py tools/bench/lean_bench/p6close_lineage.py keys          -> top-level keys + gate names of both records
    py tools/bench/lean_bench/p6close_lineage.py grep <text>   -> every json path whose key or value contains <text>"""
import json, os, sys                                                                       # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
RECS = dict((n, json.load(open(os.path.join(HERE, n + ".json")))) for n in ("latest_build", "p6fix_build"))


def walk(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from walk(v, "%s.%s" % (path, k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, "%s[%d]" % (path, i))
    else:
        yield path, o


if __name__ == "__main__":
    if sys.argv[1] == "keys":
        for n, d in RECS.items():
            print("==", n)
            for k, v in d.items():
                print("  %s: %s" % (k, type(v).__name__ + (" len %d" % len(v) if isinstance(v, (list, dict)) else " " + str(v)[:100])))
            for g in d.get("gates", []):
                print("   gate", str(g)[:240])
    elif sys.argv[1] == "grep":
        for n, d in RECS.items():
            for p, v in walk(d):
                s = "%s = %s" % (p, v)
                if sys.argv[2].lower() in s.lower():
                    print(n, s[:400])
