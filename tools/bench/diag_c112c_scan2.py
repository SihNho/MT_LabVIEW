"""diag_c112c_scan2 - card 112-3 W0 OFFLINE: print the SR / selector rows of one wiki graph (fixture candidate). No LabVIEW."""
import json, os, sys, collections                                                     # noqa: E401
R = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "docs", "wiki", "subvi")
d = json.load(open(os.path.join(R, sys.argv[1] + ".json"), encoding="utf-8"))
print("file", d.get("file"), "md5", d.get("md5"), "bytes", d.get("bytes"))
T = d["terminals"]
print("row keys", sorted(T[0]))
byw = collections.defaultdict(list)
for r in T:
    if r.get("wire_uid"):
        byw[r["wire_uid"]].append(r)
for r in T:
    if r.get("owner_class") in ("LeftShiftRegister", "RightShiftRegister", "Tunnel") or r.get("term_class") == "ControlTerminal":
        peers = [(x["owner_uid"], x["owner_class"], x["term_uid"], x["term_name"], x["is_source"]) for x in byw.get(r.get("wire_uid"), []) if x is not r]
        print({k: r.get(k) for k in ("owner_uid", "owner_class", "term_uid", "term_name", "term_class", "is_source", "wire_uid", "frame_diagram")}, "peers", peers)
oc = collections.Counter(r.get("owner_class") for r in T)
print("owner classes", dict(oc))
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[]}')
