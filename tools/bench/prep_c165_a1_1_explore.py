# ---
# labview: none
# hardware: none
# offline-args: tools/bench/graph_ring_p5s02d_20261010_154830.json
# evidence: tools/bench/cards/task_165-1-1.json
# ---
"""Card 165-1-1 explorer (read-only, no LabVIEW): where step 4's binding record lives, and the graph-2a5fa0c4 rows
for the stubs w10362/w25232, the inner faces t8776/t24342, and the step-4 tunnel t_k3o (OK3).

Prediction contract: graph md5 2a5fa0c4...; t8776 / t24342 found once each; prints the keys of the scratch JSON so the
binding record can be quoted. Existing tools: vigraph.dedupe_rows (row dedupe, called), stagesim.base_state (owners)."""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import vigraph  # noqa: E402
import protocol  # noqa: E402

GP = os.path.join(HERE, "graph_ring_p5s02d_20261010_154830.json")
raw = open(GP, "rb").read()
print("GRAPH md5", hashlib.md5(raw).hexdigest())
g = json.loads(raw)
terms, _d = vigraph.dedupe_rows(g["terminals"])
print("GRAPH keys", sorted(g.keys()))
for w in (10362, 25232):
    rs = [r for r in terms if r.get("wire_uid") == w]
    print("WIRE", w, len(rs), json.dumps(rs))
for t in (8776, 24342):
    print("TERM", t, json.dumps([r for r in terms if r["term_uid"] == t]))
for u in (5204, 10404, 31803, 31807):
    print("OWNER", u, json.dumps([r for r in terms if r["owner_uid"] == u]))
    print("  OBJ", json.dumps([o for o in g.get("objs") or [] if int(o.get("uid") or 0) == u]))
own = g.get("owners") or {}
for k in ("23405", "686"):
    print("OWNERS", k, own.get(k))
print("OWNERS of 23041", [(k, v) for k, v in own.items() if int(v[1] or 0) == 23041])
SJ = os.path.join(HERE, "diag_c164_p5s02d_scratch.json")
s = json.load(open(SJ, encoding="utf-8"))
print("SCRATCH md5", hashlib.md5(open(SJ, "rb").read()).hexdigest())
print("SCRATCH keys", sorted(s.keys()) if isinstance(s, dict) else type(s))
for k, v in (s.items() if isinstance(s, dict) else []):
    if "bind" in k.lower() or k in ("sym_real", "bound", "binding"):
        print("SCRATCH", k, json.dumps(v)[:1500])
SR = os.path.join(HERE, "stage_runs.jsonl")
for ln in open(SR, encoding="utf-8"):
    if "p5s02d" in ln:
        print("RUNS", ln.strip()[:600])
print(protocol.result_line(protocol.make_result(1, 0, None, [])))
