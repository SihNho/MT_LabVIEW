"""diag_c101_peek - card 101-3: read-only peek at plan_disp.json (no LabVIEW). Prints keys, finalized, context, first actions.
RESULT line at the end (C6)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import protocol  # noqa: E402
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = json.load(open(os.path.join(ROOT, "tools/bench/sim/disp/plan_disp.json"), encoding="utf-8"))
print(list(P.keys()))
print(json.dumps(P["finalized"], indent=0)[:2500])
print("CONTEXT", json.dumps(P.get("context"))[:1200])
for i, a in enumerate(P["actions"]):
    print(i + 1, json.dumps(a)[:260])
print(len(P["actions"]), len(P["open_rows"]))
print(protocol.result_line("PASS", {"pass": 1, "fail": 0}) if hasattr(protocol, "result_line") else "RESULT {}")
