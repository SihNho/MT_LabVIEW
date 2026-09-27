"""diag_c115b_raw - card 115-2 R0: read-only shape dump of the opmodel raw samples of delete_object / delete_wire /
remove_bad_wires (what a replayer can rebuild). No LabVIEW."""
import json, os
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "opmodels", "raw")
for n in ("delete_object_1", "delete_object_2", "delete_wire_1", "delete_wire_2", "remove_bad_wires_1", "remove_bad_wires_2"):
    d = json.load(open(os.path.join(R, n + ".json"), encoding="utf-8"))
    print("=====", n, sorted(d.keys()))
    for k, v in d.items():
        if k == "diff":
            continue
        print("  ", k, json.dumps(v, default=str)[:400])
    D = d.get("diff") or {}
    for k, v in D.items():
        s = json.dumps(v, default=str)
        print("   diff.", k, (len(v) if isinstance(v, (list, dict)) else ""), s[:900])
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":0,"fail":0},"first_fail":null,"artefacts":[]}')
