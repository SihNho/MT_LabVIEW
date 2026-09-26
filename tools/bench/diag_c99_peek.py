"""diag_c99_peek: offline key/shape peek of card 99-1 input JSONs (no LabVIEW). Usage: py diag_c99_peek.py <file> [path.to.key]"""
import json, sys, hashlib

def shape(v, depth=0):
    if isinstance(v, dict):
        return "{" + ", ".join(f"{k}:{shape(x, depth+1) if depth < 1 else type(x).__name__}" for k, x in list(v.items())[:30]) + "}"
    if isinstance(v, list):
        return f"list[{len(v)}]" + (f" of {shape(v[0], depth+1)}" if v and depth < 2 else "")
    return type(v).__name__

f = sys.argv[1]
d = json.load(open(f, encoding="utf-8"))
if len(sys.argv) > 2:
    for k in sys.argv[2].split("."):
        d = d[int(k)] if isinstance(d, list) else d[k]
    print(json.dumps(d, indent=1)[:6000])
else:
    print(f, hashlib.md5(open(f, "rb").read()).hexdigest(), shape(d))
