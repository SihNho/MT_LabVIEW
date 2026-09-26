"""diag_c97_tools_peek.py - card 97-2, OFFLINE only (no LabVIEW): summarise candidate fixture graphs."""
import collections, json, sys  # noqa: E401
for p in sys.argv[1:]:
    d = json.load(open(p, encoding="utf-8"))
    print(p, "keys", {k: (len(v) if isinstance(v, (list, dict)) else v) for k, v in d.items()})
    objs = d.get("objects") or d.get("objs") or []
    print("  classes", dict(collections.Counter(o.get("class") for o in objs)))
    for o in objs:
        if o.get("class") in ("WhileLoop", "ForLoop", "CaseStructure", "Diagram", "TopLevelDiagram"):
            print("   ", {k: o.get(k) for k in ("uid", "class", "owner_uid", "owner_class", "pos")})
