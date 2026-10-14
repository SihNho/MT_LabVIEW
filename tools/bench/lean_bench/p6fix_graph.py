"""p6fix_graph - offline, read-only: graph facts for lean task p6fix from a stored graph json of the P6 bed.
    py tools/bench/lean_bench/p6fix_graph.py shape <json>
    py tools/bench/lean_bench/p6fix_graph.py owner <json> <uid> [...]      every terminal of the given nodes
    py tools/bench/lean_bench/p6fix_graph.py wire <json> <wire uid> [...]  every terminal on the given wires
    py tools/bench/lean_bench/p6fix_graph.py grep <json> <text>            nodes/terminals whose name/label contains text"""
import json, sys                                                                         # noqa: E401


def load(p):
    return json.load(open(p, encoding="utf-8"))


def show(t):
    return "  %s %s %r %s w%s d%s" % (t["owner_uid"], t["owner_class"], t["term_name"], "src" if t["is_source"] else "snk",
                                       t["wire_uid"], t.get("frame_diagram"))


def main(av):
    cmd, d = av[0], load(av[1])
    if cmd == "shape":
        for k, v in d.items():
            if isinstance(v, list):
                print(k, len(v), json.dumps(v[0], ensure_ascii=False)[:500] if v else "")
            elif isinstance(v, dict):
                print(k, "dict", len(v), json.dumps(dict(list(v.items())[:3]), ensure_ascii=False)[:500])
            else:
                print(k, json.dumps(v, ensure_ascii=False)[:300])
        return
    T = d["terminals"]
    if cmd == "owner":
        for a in av[2:]:
            print("owner", a)
            for t in T:
                if str(t["owner_uid"]) == a:
                    print(show(t))
    elif cmd == "wire":
        for a in av[2:]:
            print("wire", a)
            for t in T:
                if str(t["wire_uid"]) == a:
                    print(show(t))
    elif cmd == "locals":                                   # every Local/Global node under the given loop uid, with its wire's sinks
        objs = dict((str(o["uid"]), o) for o in d["objs"])
        root = av[2]

        def under(u):
            seen = set()
            while u and u not in seen:
                seen.add(u)
                if u == root:
                    return True
                o = objs.get(u)
                u = str(o["owner"]) if o else ""
            return False
        for t in T:
            if t["owner_class"] in ("Local", "GlobalVariable", "PropertyNode") and under(str(t["owner_uid"])):
                sinks = [x for x in T if t["wire_uid"] and x["wire_uid"] == t["wire_uid"] and x is not t]
                print(show(t), "->", "; ".join("%s %s %r" % (x["owner_uid"], x["owner_class"], x["term_name"]) for x in sinks))
    elif cmd == "fs":                                       # the flat sequence(s) whose measured frame list holds the given diagram
        for k, v in d.get("fs_measured", {}).get("fs_frames", {}).items():
            if any(str(x) == av[2] for x in v):
                print("FlatSequence", k, "frames (left to right)", v)
    elif cmd == "grep":
        s = av[2].lower()
        for k, v in d.items():
            if isinstance(v, list):
                for r in v:
                    if s in json.dumps(r, ensure_ascii=False).lower():
                        print(k, json.dumps(r, ensure_ascii=False)[:400])


if __name__ == "__main__":
    main(sys.argv[1:])
