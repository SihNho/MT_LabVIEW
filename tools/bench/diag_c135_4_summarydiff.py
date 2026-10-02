"""diag_c135_4_summarydiff - card 135-4 pass 0 (offline, no LabVIEW, no COM).

Prior art: diag_c135_3_plandiff.py computes the same summary.json diff but prints only r2[:8] (line 96).
This file re-uses its diff()/split() rules verbatim (imported by exec of the helper block is avoided:
copied below, same IGN set) and prints ALL non-ignorable diffs of sim/ring_p3b2b_c135_1_fail/summary.json
vs sim/ring_p3b2b/summary.json.
PREDICTION (card 135-4 pass 0): real diffs == 14, and each one is a timing key ('secs') or a base-file
identity key (state/vi, graph, graph_md5, plan, md5, path). Anything else -> FAIL, return before launch.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402

IGN = {"base", "md5", "path", "goal", "at"}
OK_KEYS = {"secs", "vi", "graph", "graph_md5", "plan", "md5", "path"}
B = os.path.join(ROOT, "tools", "bench", "sim")


def diff(a, b, pre=()):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b), key=str):
            if k not in a:
                out.append((pre + (k,), "<absent>", b[k]))
            elif k not in b:
                out.append((pre + (k,), a[k], "<absent>"))
            else:
                out += diff(a[k], b[k], pre + (k,))
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append((pre + ("len",), len(a), len(b)))
        for i, (x, y) in enumerate(zip(a, b)):
            out += diff(x, y, pre + (i,))
    elif a != b:
        out.append((pre, a, b))
    return out


f = os.path.join(B, "ring_p3b2b_c135_1_fail", "summary.json")
g = os.path.join(B, "ring_p3b2b", "summary.json")
ds = diff(json.load(open(f, encoding="utf-8")), json.load(open(g, encoding="utf-8")))
real = [d for d in ds if not any(isinstance(k, str) and k in IGN for k in d[0])]
bad = []
for i, d in enumerate(real, 1):
    last = [k for k in d[0] if isinstance(k, str)][-1] if any(isinstance(k, str) for k in d[0]) else "?"
    cls = "timing" if last == "secs" else ("base-identity" if last in OK_KEYS else "OTHER")
    if cls == "OTHER":
        bad.append(d)
    print("DIFF %2d %-13s %s : %s -> %s" % (i, cls, "/".join(str(k) for k in d[0]),
                                          json.dumps(d[1], default=str)[:100], json.dumps(d[2], default=str)[:100]))
gates = [("summary real diffs == 14", len(real) == 14),
         ("every diff is timing or base-file identity", not bad)]
for lab, ok in gates:
    print("GATE %s %s" % ("PASS" if ok else "FAIL", lab))
npass = sum(1 for _, ok in gates if ok)
print(protocol.result_line(protocol.make_result(npass, len(gates) - npass, next((l for l, ok in gates if not ok), None))))
