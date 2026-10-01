r"""diag_c132_1_peek - card 132-1: print a JSON file's top-level shape (and selected dotted paths). Read-only, offline."""
import json, sys                                                                     # noqa: E401
d = json.load(open(sys.argv[1], encoding="utf-8"))


def show(d, ind=""):
    for k, v in d.items():
        if isinstance(v, dict):
            print(ind + k, "dict", len(v), list(v)[:14])
        elif isinstance(v, list):
            print(ind + k, "list", len(v), (json.dumps(v[0])[:400] if v else ""))
        else:
            print(ind + k, repr(v)[:300])


show(d)
for k in sys.argv[2:]:
    x = d
    for p in k.split("."):
        x = x[int(p)] if p.lstrip("-").isdigit() and isinstance(x, list) else x[p]
    print("==", k, json.dumps(x)[:4000])
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":0,"fail":0},"first_fail":null,"artefacts":[]}')
