r"""A4 - every functional unit named in docs/frame-loop-wire-graph.md reproduced by vigraph.path() on the S1 graph.
OFFLINE: the S1 graph is built exactly as tools/jev_candidates.load() builds it (wiki v1 terminals + fs_tunnel_pairs
+ graph_objs/graph_loops + node labels). No LabVIEW, no model.

UNITS (parsed from the doc's own tables; every end is anchored by a WIRE UID where the doc gives one - exact - and by
node uid / subVI file name otherwise - node-level, i.e. through `thru` edges, an over-approximation):
  K  kernel #5058 inputs (10): the source of the named wire -> #5058's sink on that wire; for the 6 rows fed through
     the loop border the path is extended to the nearest terminal OUTSIDE the frame-loop body (diagram 639)
  KO kernel outputs (3): source of the wire -> every consumer node named on the row
  SR state carriers (14): body write (wire in the right table) -> right register -> left register -> body read (wire
     in the left table); must use an `sr` edge. SRF: the 4 with a named final-value consumer: write -> that sink
  TI loop-border input tunnels (25): the tunnel -> each consumer named inside (and the named source -> the tunnel)
  TO loop-border output tunnels (6): producer -> tunnel -> consumer
  U  the three candidate units: every member reaches or is reached by another member (directed path, any kind)
  FS sequence-crossing cases R1/R2 of tools/bench/diag_vigraph_check.py (wire+fs edges only) + every doc path above
     that uses an `fs` edge
PREDICTION CONTRACT: recall == 1.0 in every group. A miss is printed with its row, never dropped.

    MATERIAL=1 py tools/bgrun.py --max-min 5 --log tools/bench/bench_map_a4.log -- py -u tools/bench/bench_map_20260923/a4_units.py
"""
import collections, json, os, re, sys, time                                      # noqa: E401

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, TOOLS)
import jev_candidates as JC                                                        # noqa: E402
import vigraph as V                                                                # noqa: E402

DOC = os.path.join(os.path.dirname(TOOLS), "docs", "frame-loop-wire-graph.md")
BODY = 639
REACH_CASES = (("R1 VISA out, FSOT + 4 FSIT", 34418, 20087), ("R2 refnum out, 2 nested FSOT + 2 FSIT", 59107, 7255))
G = JC.load(JC.S1_KEY)
BYNAME = collections.defaultdict(list)
for u, n in G["subvi_name"].items():
    BYNAME[n.lower()].append(u)
RES, STRUCT = collections.defaultdict(list), {}


def rows_of(title, header=True):
    """The table rows under `title` (a heading; or a header row itself with header=False), rows re-joined across
    newlines inside backticks; stops at the next heading of any level."""
    text = open(DOC, encoding="utf-8").read().split(title, 1)[1].split("\n#", 1)[0]
    out, cur = [], None
    for ln in text.splitlines():
        if ln.startswith("|"):
            cur = ln
        elif cur is not None and cur.count("`") % 2:
            cur += "\n" + ln
        else:
            cur = None
            continue
        if cur.count("`") % 2 == 0 and not re.match(r"\|\s*-", cur):
            out.append([c.strip() for c in cur.strip("|").split(" | ")])
            cur = None
    return out[1:] if header else out


def ends(cell):
    """[(node uid, terminal name or None)] named in a cell: `#uid · name`, `#uid t3 ...`, `subVI x.vi · name`."""
    out = [(int(u), n) for u, n in re.findall(r"#(\d+)\s*·\s*`([^`]*)`", cell)]
    out += [(int(u), None) for u in re.findall(r"#(\d+)\b(?!\s*·)", cell)]
    for nm, t in re.findall(r"subVI (.+?\.vi)\s*·\s*`([^`]*)`", cell):
        if BYNAME.get(nm.lower()):
            out.append((tuple(BYNAME[nm.lower()]), t))     # every call site of that file: ANY may be the one
    return out


def nodes(u, name=None):
    """A graph node for a doc uid. A STRUCTURE owns no terminal (its tunnels do), so it is replaced by its
    border tunnels - jev_candidates.structure_terminals, a HEURISTIC - filtered by terminal name when given."""
    if isinstance(u, tuple):
        return [n for x in u for n in nodes(x, name)[0]], "subVI call sites"
    if u in G["cls"]:
        return [u], "node"
    tun, how = JC.structure_terminals(G, u)
    if name:
        named = [t for t in tun if V.terminals(G, node=t, name=name)]
        tun = named or tun
    STRUCT[u] = how
    return tun, "structure->tunnels"


def npath(a, b, name_a=None, name_b=None):
    A, _ = nodes(a, name_a)
    B, _ = nodes(b, name_b)
    ps = [V.path(G, x, y) for x in A for y in B]
    ps = [p for p in ps if p]
    return min(ps, key=len) if ps else []


def src_of(w):
    return [k for k in V.wire_terminals(G, w) if G["rows"][k]["is_source"]]


def snk_of(w):
    return [k for k in V.wire_terminals(G, w) if not G["rows"][k]["is_source"]]


def rec(group, label, p, need_kind=None):
    kinds = sorted({k for a, b in zip(p, p[1:]) for k, n, _i in G["out"].get(a, ()) if n == b})
    ok = bool(p) and (need_kind is None or need_kind in kinds)
    RES[group].append({"unit": label, "ok": ok, "len": len(p), "kinds": kinds,
                       "path": [V.show(x) for x in p][:12]})


def outward(sink, down=False):
    """Shortest walk from `sink` (upstream; downstream with down=True) to a terminal NOT on the frame-loop body."""
    prev, q = {sink: None}, collections.deque([sink])
    while q:
        cur = q.popleft()
        if int(G["rows"][cur].get("frame_diagram") or 0) not in (0, BODY):
            out = []
            while cur is not None:
                out.append(cur)
                cur = prev[cur]
            return out[::-1] if down else out
        for _k, a, _i in G["out" if down else "in"].get(cur, ()):
            if a not in prev:
                prev[a] = cur
                q.append(a)
    return []


def main():
    t0 = time.time()
    for name, w, fed in rows_of("## The tracking kernel call (#5058)")[:10]:
        s, d = src_of(int(w)), [k for k in snk_of(int(w)) if V.key_parts(k)[0] == 5058]
        p = V.path(G, s[0], d[0]) if s and d else []
        if "boundary" in fed and d:
            p = outward(d[0])
        rec("K", "#5058 {0!r} <- w{1} ({2})".format(name, w, fed[:40]), p)
    for row in rows_of("| output terminal | wire | consumed by |", header=False)[:3]:
        s = src_of(int(row[1]))
        for u, _t in ends(row[2]) or [(None, None)]:
            p = (npath(V.key_parts(s[0])[0], u) and [s[0]] + npath(V.key_parts(s[0])[0], u)[1:]) if s and u \
                else (outward(s[0], down=True) if s else [])
            rec("KO", "#5058 {0} -> {1}".format(row[0], "#{0}".format(u) if u else "outside the body"), p)
    right = rows_of("## Per-frame STATE carriers — MEASURED (OpShiftRegs_v0")
    left = rows_of("## Per-frame STATE carriers — MEASURED, LEFT side")
    for r, l in zip(right, left):
        ww = [int(x) for x in re.findall(r"wire (\d+)", r[3])]
        wr = [int(x) for x in re.findall(r"wire (\d+)", l[3])]
        s, d = (src_of(ww[0]) if ww else []), [k for w in wr for k in snk_of(w)]
        rec("SR", "reg {0} {1}: w{2} -> ... -> {3}".format(r[0], r[1], ww[:1], wr),
            min((V.path(G, s[0], x) for x in d), key=len) if s and d else [], need_kind="sr")
        wf = [int(x) for x in re.findall(r"wire (\d+)", r[4])]
        if wf and "unused" not in r[4] and s and snk_of(wf[0]):
            rec("SRF", "reg {0} final value -> w{1}".format(r[0], wf[0]), V.path(G, s[0], snk_of(wf[0])[0]))
    for grp, title in (("TI", "### Inputs (what the frame loop"), ("TO", "### Outputs (what leaves")):
        for row in rows_of(title):
            t = int(row[0])
            for u, nm in ends(row[3]):
                if grp == "TI" or u != t:
                    rec(grp, "tunnel #{0} -> #{1} {2!r}".format(t, u, nm), npath(t, u, None, nm))
            for u, nm in ends(row[2]):
                if u != t:
                    rec(grp, "#{0} {1!r} -> tunnel #{2}".format(u, nm, t), npath(u, t, nm, None))
    text = open(DOC, encoding="utf-8").read()
    for k in range(3):
        body = text.split("### unit {0} ".format(k), 1)[1].split("\n#", 1)[0]
        mem = set(int(x) for x in re.findall(r"^- #(\d+)", body, re.M))
        absent = sorted(u for u in mem if u not in G["objs"])       # not in S1's GObject census at all
        for u in absent:
            print("  FACT  unit {0} member #{1} is NOT IN S1 (the doc was measured on the 2026-09-01 working copy); "
                  "excluded".format(k, u))
        STRUCT["absent_in_S1_unit{0}".format(k)] = absent
        mem -= set(absent)
        nn = dict((u, set(nodes(u)[0])) for u in mem)
        for u in sorted(mem):
            down = {V.key_parts(x)[0] for x in V.reach4(G, list(nn[u]))}
            up = {V.key_parts(x)[0] for x in V.sources_of(G, [k for n in nn[u] for k in V.terminals(G, node=n)])}
            others = set().union(*[nn[v] for v in mem if v != u]) if len(mem) > 1 else set()
            ok = bool(nn[u]) and (len(mem) == 1 or bool((down | up) & others))
            RES["U"].append({"unit": "unit {0} member #{1}".format(k, u), "ok": ok, "len": None, "kinds": []})
    for label, ws, wk in REACH_CASES:
        s, d = src_of(ws), snk_of(wk)
        rec("FS", label, V.path(G, s[0], d[0], kinds=("wire", "fs")) if s and d else [], need_kind="fs")
    out = {"when": time.strftime("%Y-%m-%d %H:%M:%S"), "groups": {}, "rows": RES,
           "structures_resolved_by_heuristic": dict((str(k), v) for k, v in STRUCT.items()),
           "graph_fs_method": G["method"]["fs_tunnel"].get("rule")}
    print("  FACT  fs edges: {0}; {1} structure uid(s) resolved to tunnels by the heuristic".format(
        out["graph_fs_method"], len(STRUCT)))
    for grp, rs in RES.items():
        n_ok = sum(r["ok"] for r in rs)
        lens = sorted(r["len"] for r in rs if r["ok"] and r["len"])
        fsn = sum(1 for r in rs if "fs" in r["kinds"])
        out["groups"][grp] = {"n": len(rs), "ok": n_ok, "recall": round(n_ok / len(rs), 4) if rs else None,
                              "path_len_min_med_max": [lens[0], lens[len(lens) // 2], lens[-1]] if lens else None,
                              "using_fs_edge": fsn}
        for r in rs:
            if not r["ok"]:
                print("  FACT  MISS {0}: {1} | {2}".format(grp, r["unit"], r["path"] if r.get("path") else "no path"))
        print("  {0}  A4 {1}: {2}/{3} reproduced; path len min/med/max {4}; {5} use an fs edge".format(
            "PASS" if n_ok == len(rs) else "FAIL", grp, n_ok, len(rs), out["groups"][grp]["path_len_min_med_max"], fsn))
    tot = sum(g["n"] for g in out["groups"].values())
    ok = sum(g["ok"] for g in out["groups"].values())
    out["recall_all"] = round(ok / tot, 4)
    json.dump(out, open(os.path.join(HERE, "a4_units.json"), "w", encoding="utf-8"), indent=1)
    print("=== A4: {0}/{1} units reproduced (recall {2}) in {3:.1f}s".format(ok, tot, out["recall_all"], time.time() - t0))
    return 0 if ok == tot else 1


if __name__ == "__main__":
    raise SystemExit(main())
