"""p63_wires - offline: list every terminal on the given wire uids of a stored wiki/graph json (read-only helper, P6-3).
    py tools/bench/lean_bench/p63_wires.py <json> <wire uid> [...]  |  --owner <uid> [...]"""
import json, sys                                                                         # noqa: E401
d = json.load(open(sys.argv[1], encoding="utf-8"))
T = d["terminals"]
own = "--owner" in sys.argv
if "--name" in sys.argv:                                  # every terminal whose name equals the given text, with its owner's other terminals
    nm = sys.argv[sys.argv.index("--name") + 1]
    for t in T:
        if t["term_name"] == nm:
            print("   ", t["owner_uid"], t["owner_class"], repr(t["term_name"]), "src" if t["is_source"] else "snk", "w%s" % t["wire_uid"], "d%s" % t.get("frame_diagram"))
    sys.exit(0)
for a in sys.argv[2:]:
    if a == "--owner":
        continue
    w = int(a)
    rows = [t for t in T if (int(t["owner_uid"]) if own else int(t["wire_uid"])) == w]
    print(("owner" if own else "wire"), w)
    for t in rows:
        print("   ", t["owner_uid"], t["owner_class"], repr(t["term_name"]), "src" if t["is_source"] else "snk", "w%s" % t["wire_uid"], "d%s" % t.get("frame_diagram"))
