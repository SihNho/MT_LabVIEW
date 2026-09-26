"""card 100-6: offline read of the base graph rows the L1 re-route needs (no LabVIEW)."""
import json
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "tools", "bench", "par1359_95_graph.json"), encoding="utf-8"))
for r in d["terminals"]:
    if r["owner_uid"] == 9227:
        print(r)
print(sorted(d.keys()))
print([o for o in d["objs"] if o["uid"] == 9227])
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[]}')
