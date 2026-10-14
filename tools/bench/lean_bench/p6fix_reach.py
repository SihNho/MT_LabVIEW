"""p6fix_reach - offline, read-only: does data from the given source nodes reach the given target nodes in the stored P6 bed graph?
Graph: owner -> owner along every wire (source terminal owner -> sink terminal owner); a structure is entered/left through its
tunnels, and (conservatively) every INPUT tunnel / shift register of a structure reaches every OUTPUT tunnel of the same structure
(structure membership from the graph's `owners` map: tunnel uid -> [structure class, structure uid]).
    py tools/bench/lean_bench/p6fix_reach.py <graph json> --from <uid> [...] --to <uid> [...]"""
import json, sys                                                                         # noqa: E401
from collections import deque
d = json.load(open(sys.argv[1], encoding="utf-8"))
av = sys.argv[2:]
src = [int(x) for x in av[av.index("--from") + 1:av.index("--to")]]
dst = set(int(x) for x in av[av.index("--to") + 1:(av.index("--skip") if "--skip" in av else None)])
T, OWN = d["terminals"], d["owners"]
by_w = {}
for t in T:
    if int(t["wire_uid"] or 0):
        by_w.setdefault(int(t["wire_uid"]), []).append(t)
adj = {}
for rs in by_w.values():
    for a in rs:
        if a["is_source"]:
            for b in rs:
                if not b["is_source"]:
                    adj.setdefault(int(a["owner_uid"]), set()).add(int(b["owner_uid"]))
struct_of, diags = {}, {}
for t in T:
    c = str(t["owner_class"])
    if "Tunnel" in c or "ShiftRegister" in c:
        diags.setdefault(int(t["owner_uid"]), set()).add(str(t["frame_diagram"]))
for tu, ds in diags.items():                        # inner diagram = the one whose owning structure sits on the other diagram
    for da in ds:
        o = OWN.get(da)
        if o and str(o[0]) not in ("Diagram", "TopLevelDiagram"):
            p = OWN.get(str(o[1]))
            if p and any(str(p[1]) == db for db in ds if db != da):
                struct_of[tu] = int(o[1])
        if tu not in struct_of and o and len(ds) == 1 and "Shift" in str([t for t in [o[0]]]):
            struct_of[tu] = int(o[1])
members = {}
for tu, su in struct_of.items():
    members.setdefault(su, set()).add(tu)
SKIP = set(int(x) for x in av[av.index("--skip") + 1:]) if "--skip" in av else set()   # enclosing loops: no cross-iteration mixing
if "--skip" in av:
    dst = set(int(x) for x in av[av.index("--to") + 1:av.index("--skip")])
for su, tus in members.items():                      # any tunnel of a structure -> every tunnel of it (conservative)
    if su in SKIP:
        continue
    for a in tus:
        adj.setdefault(a, set()).update(tus - {a})
print("tunnels mapped to structures: %d (structures %d)" % (len(struct_of), len(members)))
prev = {}
q = deque(src)
seen = set(src)
NOPASS = set(int(t["owner_uid"]) for t in T if str(t["owner_class"]) in ("Diagram", "TopLevelDiagram"))   # panel terminals: not one node
while q:
    u = q.popleft()
    if u in NOPASS:
        continue
    for v in adj.get(u, ()):
        if v not in seen:
            seen.add(v); prev[v] = u; q.append(v)                                  # noqa: E702
for t in sorted(dst):
    if t in seen:
        path, u = [t], t
        while u in prev:
            u = prev[u]; path.append(u)                                              # noqa: E702
        print("REACHES #%d via %s" % (t, " <- ".join(str(x) for x in path)))
    else:
        print("does NOT reach #%d" % t)
