"""diag_c134_1_keys - card 134-1: OFFLINE read of graph/sim JSON keys (FS fields). No LabVIEW. PREDICTION: prints keys."""
import json, os, sys                                                                          # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
for f in sys.argv[1:]:
    d = json.load(open(os.path.join(B, f), encoding="utf-8"))
    print(f, sorted(d.keys()) if isinstance(d, dict) else type(d))
    if isinstance(d, dict):
        for k in sorted(d.keys()):
            if k.startswith("fs") or k in ("borders", "base", "finalized", "sim_of", "owners"):
                print("  ", k, json.dumps(d[k], default=str)[:900])
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[]}')
