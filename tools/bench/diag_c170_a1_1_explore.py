# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/task_170-a1-1.json
# ---
r"""diag_c170_a1_1_explore - card 170-a1-1: offline read of the stored graphs (P6 fbc7b7ee, S1 wiki json, get-buff-image wiki json)
for facts F1-F4. Read only; prints what it finds, decides nothing (the facts script cites from this log).
Found before writing (CALLED): tools/bench/diag_c108c_graph.Graph (terminals/owners/walk), with the same graph_summary/objs json
hand-off as diag_c167_a1_4_ready.py:111-122 (the shared file is not edited).
PREDICTION: prints the structure keys, the uid dumps and the name hits; no gate decides anything (EXPLORE lines only).
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c170_a1_1_explore.log -- py -u tools/bench/diag_c170_a1_1_explore.py"""
import json, os, re, sys, types                                                             # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
os.chdir(ROOT)
for _p in (ROOT, os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench")):
    _p in sys.path or sys.path.insert(0, _p)                                                # noqa: E701
import diag_c108c_graph as DG                                                               # noqa: E402
import protocol as PR                                                                       # noqa: E402

GF = "tools/bench/graph_ring_p6_20261012_212645.json"
S1F = "docs/wiki/subvi/D1_s1_copy.json"
GBF = "docs/wiki/subvi/get buff image-lost frames.json"
_loads = json.loads


def _loads_gs(s):
    g = _loads(s)
    if isinstance(g, dict) and "terminals" in g:
        g.setdefault("graph_summary", {})
        g.setdefault("objs", [])
    return g


DG.json = types.SimpleNamespace(loads=_loads_gs)
RAW = {k: _loads(open(p, encoding="utf-8").read()) for k, p in (("p6", GF), ("s1", S1F), ("gb", GBF))}
G = {k: DG.Graph(os.path.join(ROOT, p).replace("\\", "/")) for k, p in (("p6", GF), ("s1", S1F), ("gb", GBF))}
for k, r in RAW.items():
    print("KEYS %s %s" % (k, {kk: (type(v).__name__, len(v) if hasattr(v, "__len__") else v) for kk, v in r.items()}), flush=True)
    for kk in ("objs", "owners", "graph_summary", "loops", "fs_tunnel_pairs", "nodes", "constants"):
        v = r.get(kk)
        if isinstance(v, list) and v:
            print("SAMPLE %s.%s %s" % (k, kk, json.dumps(v[0], default=str)[:600]), flush=True)
        elif isinstance(v, dict) and v:
            print("SAMPLE %s.%s keys %s first %s" % (k, kk, list(v)[:20], json.dumps(list(v.items())[0], default=str)[:600]), flush=True)


def dump(k, uid):
    g = G[k]
    ts = g.by_owner.get(uid, [])
    print("UID %s #%d class %s loop %s chain %s n_terms %d" % (k, uid, g.cls.get(uid), g.loop(uid) if ts else None,
                                                             [(s, g.cls.get(s)) for s in g.chain(uid)] if ts else None, len(ts)), flush=True)
    for t in ts:
        ends = g.walk(t, t["is_source"], lambda n: False) if t["wire_uid"] else [(None, [])]   # source -> walk down
        direct = [(o["owner_uid"], o["owner_class"], o["term_name"], o["term_uid"]) for o in g.by_wire.get(t["wire_uid"], [])
                  if o["term_uid"] != t["term_uid"]] if t["wire_uid"] else []
        print("  T %s t%d %r src=%s w%s d%s direct=%s ends=%s" % (k, t["term_uid"], t["term_name"], t["is_source"], t["wire_uid"],
              t["frame_diagram"], direct[:8], [(e["owner_uid"], e["owner_class"], e["term_name"], e["term_uid"], path[:6]) if e else None
                                               for e, path in ends][:10]), flush=True)


OBJ = {o["uid"]: o for o in RAW["p6"]["objs"]}
OWN = RAW["p6"]["owners"]


def objchain(u):
    """obj owner field -> owners map, up to the top (pass 2: the Graph.chain stops where struct_outer has no tunnel)."""
    out, n = [], 0
    o = OBJ.get(u)
    d = o and o.get("owner")
    while d not in (None, "", 0) and n < 30:
        n += 1
        ow = OWN.get(str(d))
        out.append((d, ow))
        if not ow:
            break
        so = OBJ.get(ow[1])
        d = so and so.get("owner")
    return out


ARGS = [int(a) for a in sys.argv[1:]] or [29648, 29655, 1978, 1445, 1034, 2179, 5351, 27056, 27039, 22692, 21305, 22541, 26411,
                                          26446, 26615, 26145, 3292, 2143, 2991, 27311, 27373, 29403, 29548]
for u in ARGS:
    print("OBJ #%d %s chain %s" % (u, json.dumps(OBJ.get(u)), objchain(u)), flush=True)
    dump("p6", u)
for L_ in RAW["p6"]["loops"]:
    hit = {r: l for r, l in (L_.get("left_of") or {}).items() if int(r) in ARGS or any(int(x) in ARGS for x in (l if isinstance(l, list) else [l]))}
    if hit:
        print("LOOP %s #%s left_of hits %s" % (L_["class"], L_["loop_uid"], hit), flush=True)
for d in (22650, 26117, 22427, 12960, 639, 23166, 686, 536):
    print("OWNER d%d %s struct_outer %s" % (d, OWN.get(str(d)), G["p6"].struct_outer.get((OWN.get(str(d)) or [0, 0])[1])), flush=True)
for d in (27219, 27232, 3292):
    print("ONDIAG %d %s" % (d, sorted((o["uid"], o["class"]) for o in RAW["p6"]["objs"] if o.get("owner") == d)[:80]), flush=True)
print(PR.result_line(PR.make_result(1, 0, None, [])), flush=True)
