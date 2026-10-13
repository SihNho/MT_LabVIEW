"""p63_peek - print the shape of P6-2's leg records (read-only helper for lean task P6-3)."""
import json, os, sys
B = os.path.dirname(os.path.abspath(__file__))


def walk(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from walk(v, p + "/" + str(k))
    elif isinstance(o, list) and len(o) > 8:
        yield p, "list[%d] %s" % (len(o), json.dumps(o[:2], ensure_ascii=False)[:200])
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, p + "[%d]" % i)
    else:
        yield p, json.dumps(o, ensure_ascii=False)[:200]


f = sys.argv[1]
d = json.load(open(os.path.join(B, f), encoding="utf-8"))
pat = sys.argv[2].lower() if len(sys.argv) > 2 else ""
for p, v in walk(d):
    if pat in p.lower() or pat in v.lower():
        print(p, "=", v)
