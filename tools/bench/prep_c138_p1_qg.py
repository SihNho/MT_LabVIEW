"""prep_c138_p1_qg - card 138-P1 read-only query of the bed graph json (no LabVIEW): terminal rows touching given uids."""
import json
import os
import sys
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
G = json.load(open(os.path.join(R, "tools/bench/graph_ring_p3b2b_20261002_133824.json"), encoding="utf-8"))
print("TOP", [k for k in G])
T = G["terminals"]
print("ROW keys", sorted(T[0]))
want = set(int(x) for x in sys.argv[1:])
for r in T:
    vals = set()
    for k in ("term_uid", "owner_uid", "wire_uid", "frame_diagram"):
        try:
            vals.add(int(r.get(k) or 0))
        except Exception:
            pass
    if vals & want:
        print(json.dumps(r)[:400])
for k in ("objects", "loops"):
    for o in G.get(k) or []:
        if any(int(o.get(f) or 0) in want for f in ("uid", "loop_uid", "diagram", "owner_uid") if str(o.get(f) or "0").lstrip("-").isdigit()):
            print(k.upper(), json.dumps(o)[:400])
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[]}')
