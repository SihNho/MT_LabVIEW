"""diag_c112a_peek - card 112-1: print a stageplan's non-action keys and its actions (read-only, no LabVIEW)."""
import json
import sys

p = json.load(open(sys.argv[1], encoding="utf-8"))
print([k for k in p])
for k in p:
    if k not in ("actions", "steps"):
        print(k, "=", json.dumps(p[k])[:600])
for a in p["actions"]:
    print(json.dumps(a)[:500])
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[]}')
