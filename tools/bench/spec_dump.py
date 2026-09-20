"""spec_dump.py - human-readable dump of spec_wiring*.json (one VI per section) -> tools/bench/spec_dump.txt"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
out = open(os.path.join(HERE, "spec_dump.txt"), "w", encoding="utf-8")
for f in ("spec_wiring.json", "spec_wiring_more.json"):
    d = json.load(open(os.path.join(HERE, f), encoding="utf-8"))
    for name, v in d.items():
        out.write(f"\n===== {name}\n")
        out.write(" fp: " + repr({k.replace("\n", " "): (x["type"], x.get("shape", x.get("value")), "IND" if x["indicator"] else "CTRL") for k, x in v["fp"].items()}) + "\n")
        for cls in ("Constant", "Node", "ControlTerminal", "Structure", "SubVI"):
            objs = v["objects"][cls]
            out.write(f" {cls}: " + (repr([(o["uid"], tuple(o["pos"])) for o in objs]) if isinstance(objs, list) else str(objs)) + "\n")
        for dname, dg in v["diagrams"].items():
            out.write(f" diagram {dname}:\n")
            for n, (uid, _, terms) in dg["nodes"].items():
                out.write(f"   node {n} uid {uid}: " + ", ".join(f"t{t}={nm!r}@w{w}" for t, nm, w in terms) + "\n")
            single = [w for w, ends in dg["nets"].items() if len(ends) == 1]
            out.write("   single-ended wires: " + " ".join(single) + "\n")
out.close(); print("written")
