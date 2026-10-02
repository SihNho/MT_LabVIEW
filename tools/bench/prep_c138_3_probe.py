r"""prep_c138_3_probe - card 138-3, read-only: fixture state of the two red self-tests' inputs (no tool edit, no LabVIEW).
PREDICTION: prints git status / md5 of the plan fixtures and their finalized.base; ends with a RESULT line."""
import json, os, subprocess, sys                                                     # noqa: E401
B = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(os.path.dirname(B))   # noqa: E702
sys.path.insert(0, os.path.join(R, "tools"))
import protocol as P                                                                 # noqa: E402
FX = ["tools/bench/plan_ring_p3b2.json", "tools/bench/plan_ring_p3b2b.json", "tools/bench/plan_ring_p3b2a.json",
      "tools/bench/plan_ring_p3b1.json", "tools/bench/graph_ring_p3b1_20261002_073225.json"]
g = lambda *a: subprocess.run(["git"] + list(a), cwd=R, capture_output=True, text=True).stdout.strip()   # noqa: E731
for f in FX:
    print("FILE", f, "status=[%s]" % g("status", "--short", "--", f), "log:", g("log", "-2", "--format=%h %ci", "--", f).replace("\n", " | "))
    try:
        p = json.load(open(os.path.join(R, f), encoding="utf-8"))
    except Exception as e:
        print("  ERR", e); continue
    fin = p.get("finalized") or {}
    b = fin.get("base") or {}
    print("  top keys", sorted(p)[:15], "final", p.get("final"))
    print("  base", {k: v for k, v in b.items() if k not in ("terminals",)})
    print("  provisional fields", {k: v for k, v in p.items() if "provis" in k.lower()}, {k: v for k, v in fin.items() if "provis" in k.lower()})
    if b.get("path"):
        bp = b["path"] if os.path.isabs(b["path"]) else os.path.join(R, b["path"])
        try:
            BB = json.load(open(bp, encoding="utf-8"))
            print("  base file keys", sorted(BB)[:20], "status=[%s]" % g("status", "--short", "--", b["path"]))
        except Exception as e:
            print("  base ERR", e)
print(P.result_line(P.make_result(1, 0, None, [])))
