"""gui_report.py — table for the live click bench: method x micro-op."""
import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
rows = [json.loads(l) for l in open(os.path.join(HERE, "gui_results.jsonl"), encoding="utf-8") if l.strip()]
by = {}
for r in rows:
    by.setdefault((r["method"], r["op"]), []).append(r)
print(f"{'method':14} {'op':9} {'n':>2} {'pass':>4} {'med s':>6} {'actions':>7} {'shots read':>10} {'px':>5}")
for (m, op), rs in sorted(by.items()):
    ok = sum(1 for r in rs if r.get("ok"))
    secs = statistics.median(r.get("seconds", 0) for r in rs)
    acts = statistics.median(r.get("gated_actions", 0) for r in rs)
    shots = statistics.median(r.get("screenshots_read", 0) for r in rs)
    px = [r["px_error"] for r in rs if r.get("px_error") is not None and r.get("ok")]
    print(f"{m:14} {op:9} {len(rs):2d} {ok:>4} {secs:6.1f} {acts:7.0f} {shots:10.0f} "
          f"{(statistics.median(px) if px else float('nan')):5.1f}")
