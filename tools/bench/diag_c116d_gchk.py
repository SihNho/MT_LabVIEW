import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
print(d.get("md5"), list(d.keys())[:12])
rows = d["terminals"]
print(rows[0])
W = {}
for r in rows:
    if r["wire_uid"]:
        W.setdefault(int(r["wire_uid"]), []).append((int(r["owner_uid"]), r.get("owner_class") or r.get("term_class"), r["term_name"], bool(r["is_source"]), r.get("frame_diagram")))
for w, v in sorted(W.items()):
    print(w, v)
