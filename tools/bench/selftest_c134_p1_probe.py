"""card 134-P1 read-only probe (no LabVIEW): plan a/b bases, preds, pinned md5s. Prints facts only."""
import json, os, hashlib, sys                                                  # noqa: E401
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, "tools")
import protocol as P                                                           # noqa: E402
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                  # noqa: E731
for n in ("a", "b"):
    d = json.load(open("tools/bench/plan_ring_p3b2%s.json" % n, encoding="utf-8"))
    fz = d["finalized"]
    print(n, "plan md5", md5("tools/bench/plan_ring_p3b2%s.json" % n), "base", fz["base"], "final", d.get("final"))
    g = json.load(open(fz["base"]["path"], encoding="utf-8"))
    print("  base graph vi", g.get("vi"), g.get("md5"), "keys", sorted(g.keys()))
    pr = json.load(open("tools/bench/plan_ring_p3b2%s_pred.json" % n, encoding="utf-8"))
    print("  pred keys", sorted(pr.keys()), "bed_md5", pr.get("bed_md5"), "graph", pr.get("graph"),
          "mem", {k: (pr.get("memory_pred") or {}).get(k) for k in ("start_mb", "peak_mb", "fail_above_mb")})
    print("  errorlist", {k: v for k, v in (pr.get("errorlist") or {}).items() if k != "unwired_created_sinks"})
for r in ("tools/recipes/stage_d1_ring_p3b2a.py", "tools/recipes/stage_d1_ring_p3b2b.py", "tools/bench/plan_ring_p3b2a.json",
          "tools/bench/plan_ring_p3b2b.json", "tools/bench/graph_ring_p3b2a_fs_20261002_102553.json",
          "tools/bench/stage_d1_ring_p3b2a_scratch.py", "tools/bench/diag_c134_1_graph.py", "tools/bench/diag_c134_1_finalize_b.py",
          "tools/bench/diag_c134_1_graph_plan.json"):
    print(r, md5(r))
print(open("tools/bench/diag_c134_1_graph_plan.json", encoding="utf-8").read()[:1500])
print(P.result_line(P.make_result(1, 0, None)))
