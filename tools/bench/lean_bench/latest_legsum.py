"""latest_legsum - offline: per leg of a legs json (p6fix_legs.py output), the v5 numbers and the alignment numbers.
    py tools/bench/lean_bench/latest_legsum.py <legs json> [...]"""
import json, sys                                                                         # noqa: E401
for f in sys.argv[1:]:
    d = json.load(open(f, encoding="utf-8"))
    print("==", f)
    for t, r in d["legs"].items():
        a = (r.get("align") or {}).get("align", {})
        c = (r.get("align") or {}).get("col0", {})
        print(" %-5s v5lost %s frames_delta %s secs %s attempts %s | rows %s matched %s damaged %s incr %s span %s..%s lost %s gaps %s | col0 own %s/%s"
              % (t, r.get("lost"), r.get("frames_delta"), r.get("secs"), r.get("attempts"), a.get("rows_B"), a.get("matched"),
                 a.get("damaged"), a.get("strictly_increasing"), a.get("first_A"), a.get("last_A"), a.get("lost_in_span"),
                 a.get("gap_hist"), c.get("col0_own"), c.get("rows")))
