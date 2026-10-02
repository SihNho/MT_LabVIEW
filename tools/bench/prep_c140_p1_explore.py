"""prep_c140_p1_explore - card 140-P1 read-only probe (offline): v14 op -> action map near the s1|s2 cut, cross-session refs."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
os.chdir(ROOT)
import stagexec as SX  # noqa: E402
P = json.load(open("tools/bench/plan_ring_p4_v14.json", encoding="utf-8"))
A = P["actions"]
OPS = SX.compile_plan(P)
print("ops", len(OPS))
for k, o in enumerate(OPS[:45], 1):
    print(k, o["kind"], o["acts"], [(A[n - 1]["id"], A[n - 1]["op"], A[n - 1].get("of")) for n in o["acts"]])


def refs(x):
    if isinstance(x, str) and x.startswith("new:"):
        yield x
    elif isinstance(x, dict):
        for y in x.values():
            yield from refs(y)
    elif isinstance(x, list):
        for y in x:
            yield from refs(y)


s1acts = set(n for o in OPS[:16] for n in o["acts"])
s1as = set(A[n - 1].get("as") for n in s1acts if A[n - 1].get("as"))
print("s1 actions", sorted(s1acts), "as", sorted(s1as))
for n, a in enumerate(A, 1):
    if n in s1acts:
        continue
    for r in refs(dict((x, y) for x, y in a.items() if x not in ("as", "why"))):
        b = r[4:].split(".")[0]
        if b in s1as or b[:-1] in s1as:
            print("CROSS", n, a["id"], a["op"], r, json.dumps(dict((k, v) for k, v in a.items() if k != "why"))[:400])
    if a.get("of") and any(A[m - 1]["id"] == a["of"] for m in s1acts):
        print("OFCROSS", n, a["id"], a["of"])
print(json.dumps(A[16])[:800])
print(json.dumps(P["finalized"].get("fs_routes"))[:600])
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS", "gates": {"pass": 0, "fail": 0}, "first_fail": None, "artefacts": []}))
