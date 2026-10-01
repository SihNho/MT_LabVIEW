"""diag_c129_1_peek - card 129-1, OFFLINE read-only: print the top-level keys of plan / pred JSON files (format reference)."""
import json, sys                                                                    # noqa: E401
for f in sys.argv[1:]:
    d = json.load(open(f, encoding="utf-8"))
    print("==", f, list(d.keys()))
    for k, v in d.items():
        if k == "actions":
            print(" actions", len(v), json.dumps(v[0])[:400]); continue
        print(" ", k, ":", json.dumps(v)[:900])
