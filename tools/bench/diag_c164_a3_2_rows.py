# ---
# labview: none
# hardware: none
# offline-args: tools/bench/graph_ring_p5s02c_20261010_131658.json
# evidence: tools/bench/cards/task_164-3-2.json
# ---
"""Card 164-3-2: print the stored-graph rows for the K3f/K4f terminals (read-only, no LabVIEW).

Prediction contract: graph md5 == 3d5196ab...; t8776 / t24342 each found once, owner LoopTunnel #5204 / #10404;
every wire on those tunnels listed with all its terminal rows. Existing tools checked: vigraph.dedupe_rows
(terminal-row dedupe, called here), vigraph.wire_terminals needs build4's G (not needed for a raw row dump).
"""
import hashlib
import json
import sys

sys.path.insert(0, "tools")
import vigraph  # noqa: E402
import protocol  # noqa: E402

P = sys.argv[1] if len(sys.argv) > 1 else "tools/bench/graph_ring_p5s02c_20261010_131658.json"
raw = open(P, "rb").read()
md5 = hashlib.md5(raw).hexdigest()
g = json.loads(raw)
print("MD5", md5)
print("KEYS", {k: (len(v) if isinstance(v, (list, dict)) else v) for k, v in g.items() if k != "vi"})
terms, drec = vigraph.dedupe_rows(g["terminals"])
print("DEDUPE", json.dumps(drec))
TUN = (5204, 10404)
fails = 0
wires = set()
for t in TUN:
    rows = [r for r in terms if r["owner_uid"] == t]
    print("TUNNEL", t, "rows", len(rows))
    for r in rows:
        print("  ", json.dumps(r))
        if r.get("wire_uid"):
            wires.add(r["wire_uid"])
for tu in (8776, 24342):
    n = sum(1 for r in terms if r["term_uid"] == tu)
    print("TERM", tu, "count", n)
    fails += n != 1
for w in sorted(wires):
    rows = [r for r in terms if r.get("wire_uid") == w]
    print("WIRE", w, "ends", len(rows))
    for r in rows:
        print("  ", json.dumps(r))
for k in ("objects", "objs", "wires", "loops", "frames", "owners"):
    v = g.get(k)
    if isinstance(v, list):
        hit = [o for o in v if isinstance(o, dict) and (o.get("uid") in TUN or o.get("wire_uid") in wires)]
        for o in hit:
            print(k.upper(), json.dumps(o)[:400])
    elif isinstance(v, dict):
        for kk in [str(x) for x in TUN] + [str(x) for x in wires]:
            if kk in v:
                print(k.upper(), kk, json.dumps(v[kk])[:400])
print(protocol.result_line({"status": "PASS" if fails == 0 else "FAIL", "gates": {"pass": 2 - fails, "fail": fails},
                            "first_fail": None if fails == 0 else "term count", "artefacts": []}))
