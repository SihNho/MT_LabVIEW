"""q_m4_wires_offline - READ-ONLY, no LabVIEW. The S1 wiki's terminal rows on the wires around #10686 (cycle 68):
which terminal sources w3362 / w31234, and what feeds the Quotient & Remainder divisor (the 25-frame question)."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
r = json.load(open(os.path.join(ROOT, "docs", "wiki", "subvi", "D1_s1_copy.json"), encoding="utf-8"))
T = r["terminals"]
print("rows", len(T), "keys", sorted(T[0].keys()))
wk = "wire_uid" if "wire_uid" in T[0] else "wire"
for w in (3362, 31234, 3268, 3050, 9105, 23526, 2344):
    print("W", w, [(t.get("term_uid"), t.get("name"), t.get("is_source"), t.get("owner_class"), t.get("owner_uid"))
                   for t in T if t.get(wk) == w])
lab = {}
for _d, rows in json.load(open(os.path.join(ROOT, "tools", "bench", "main_vi_node_labels.json"),
                               encoding="utf-8")).get("diagrams", {}).items():
    for x in rows:
        lab[int(x["uid"])] = x.get("label", "")
for u in (30146, 10825, 3057, 2136, 10686):
    print("NODE", u, "label", repr(lab.get(u)))
    for t in T:
        if t.get("owner_uid") == u:
            srcs = [(s.get("term_uid"), s.get("term_name"), s.get("owner_class"), s.get("owner_uid"))
                    for s in T if s.get(wk) == t.get(wk) and s.get("is_source") and t.get(wk)]
            print("   ", t.get("term_uid"), repr(t.get("term_name")), "src" if t.get("is_source") else "sink",
                  "w", t.get(wk), "<-", srcs if not t.get("is_source") else "")
for w in (31234,):
    pass
