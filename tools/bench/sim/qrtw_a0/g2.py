"""card 120-5 offline: constant candidates in the pool-bed graph dump (no LabVIEW). Types are NOT in the dump; this only
lists candidates by class + where their wire goes, for a later read_term_type census."""
import json, os, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
os.chdir(ROOT)
d = json.load(open('tools/bench/graph_qrt_pool_20260928.json', encoding='utf-8'))
objs = dict((o["uid"], o) for o in d["objs"])
byw = collections.defaultdict(list)
for r in d["terminals"]:
    if r["wire_uid"]:
        byw[r["wire_uid"]].append(r)
rows_of = collections.defaultdict(list)
for r in d["terminals"]:
    rows_of[r["owner_uid"]].append(r)
cnt = collections.Counter(o["class"] for o in d["objs"] if "Constant" in o["class"])
print("CONST CLASSES", dict(cnt))
kids = collections.Counter(o["owner"] for o in d["objs"] if "Constant" in o["class"])
for cls in ("ClusterConstant", "ArrayConstant", "DigitalNumericConstant"):
    L = [o for o in d["objs"] if o["class"] == cls]
    print("==", cls, len(L))
    for o in L[:400]:
        rs = rows_of.get(o["uid"], [])
        fd = rs[0]["frame_diagram"] if rs else None
        sinks = []
        for r in rs:
            for x in byw.get(r["wire_uid"], []):
                if not x["is_source"]:
                    sinks.append((x["owner_uid"], x["owner_class"], x["term_name"]))
        print(" ", o["uid"], "owner", o["owner"], "frame", fd, "sinks", sinks[:3])
print("686 owner", d["owners"].get("686"))
print("686 constants", [(o["uid"], o["class"]) for o in d["objs"]
                        if "Constant" in o["class"] and any(r["frame_diagram"] == 686 for r in rows_of.get(o["uid"], []))])
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[]}')
