"""Card 108-3 - OFFLINE consumer/producer tables of group B (#1359 #2222 #2626 #6104 #8885 #9833 #11261 #29874 + the
controls #47/#403 #9289/#9306 #28148/#28170 #28996/#29091) on the L2 chain bed and on S1. No LabVIEW, nothing opened.

Graphs: BED = graph_l2a1_bed_20260927.json (D1_l2_a1_20260925_235224.vi md5 51d9b8a3; single-line JSON, cited by
term_uid); S1 = par1359_95_graph.json (D1_s1_copy.vi md5 3e3d23ce; base of plan_disp.json; cited by line). S1 has
no owners/loops of its own: it borrows the BED's diagram->structure map (same S1 uids, Pre-decided 158) and
graph_loops_s1_20260924.json's machine SR pairs. Walker: diag_c108c_graph.py (prior art listed there).
PREDICTION CONTRACT: G1 bed graph md5 == 93d153dd (card pin); G2 all 8 group-B uids present in both graphs;
G3 tunnel sets contain the P0 lists (d1-loop12-17-split-plan.md:106-108), any extra is an unwired 'Tunnel' (run 1
FAILED '==': #7922/#29914 are the loops' unwired N terminals, which P0's data-tunnel list never carried); G4 the 4 control terminals present in both;
G5 every T1/T3/T4 cell carries a cite; G6 plan_disp.json parsed, moved set non-empty. Measure only; no destination.
"""
import json, os, sys, hashlib, re, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, ".."))
import protocol
from diag_c108c_graph import Graph, LOOPNAME
BEDP, S1P = os.path.join(HERE, "graph_l2a1_bed_20260927.json"), os.path.join(HERE, "par1359_95_graph.json")
PLANP, OUT = os.path.join(HERE, "sim", "disp", "plan_disp.json"), os.path.join(HERE, "facts_c108c_groupB.json")
B8, BS = [1359, 2222, 2626, 6104, 8885, 9833, 11261, 29874], {1359, 2222, 29874}
CTL = {403: 47, 9306: 9289, 28170: 28148, 29091: 28996}
A1_2 = {5540, 9647, 10247, 10445, 10950, 17289, 10969, 10757, 5058}
L15 = {10407, 48, 3529, 3560, 3447}
P0T = {1359: {9087, 9227, 9503, 10004, 10177, 11363, 31051, 31137, 28370}, 2222: {2276, 2451, 2765, 2992, 3176, 6132, 7091},
       29874: {29172, 29777, 29911, 30135, 29616, 30896}}
gates = []
def gate(n, ok, d):
    gates.append((n, bool(ok), d)); print("GATE", n, "PASS" if ok else "FAIL", d)
gate("G1 bed md5", hashlib.md5(open(BEDP, "rb").read()).hexdigest() == "93d153ddb36f1967c1e6e75f3541c565", "card pin")
bed = Graph(BEDP)
s1 = Graph(S1P, owners=json.load(open(BEDP, encoding="utf-8"))["owners"],
           loops=json.load(open(os.path.join(HERE, "graph_loops_s1_20260924.json"), encoding="utf-8"))["loops"])
ptxt = open(PLANP, encoding="utf-8").read(); plan = json.loads(ptxt); plines = ptxt.split("\n")
def pline(aid):
    return "tools/bench/sim/disp/plan_disp.json:%d" % next(i for i, l in enumerate(plines, 1) if '"id": "%s"' % aid in l)
moved = {}
for a in plan["actions"]:
    for u in a.get("nodes", []) + ([a["uid"]] if a["op"] == "delete_object" else []):
        moved[u] = (a["id"], pline(a["id"]))
gate("G6 plan", len(moved) >= 10, "moved/deleted uids %s" % sorted(moved))

def members(G):
    nodes = {G.node(t) for t in G.terms}
    return {n for n in nodes if n in B8 or BS & set(G.chain(n)) or G.struct_of_tunnel(n) in BS}
def tunnels(G, S):
    return sorted(u for u in G.by_owner if G.struct_of_tunnel(u) == S)
def io_terms(G, b, src):
    if b in BS:
        return [t for u in tunnels(G, b) for t in G.by_owner[u] if t["term_class"] == "OuterTerminal" and t["is_source"] == src]
    return [t for t in G.by_owner[b] if t["is_source"] == src]
def where(G, n, M):
    if n in M: return "group-B"
    if n in A1_2: return "1.2"
    if n in L15: return "1.5"
    if n == 376: return "1.7"
    return G.loop(n)
def tag(G, n, e, M):
    c, lab = G.ncls(n), G.label(n)
    if n in M: return "group-B internal"
    if n == 376 or "save" in lab.lower() or c == "ReadWriteFile": return "saved-data"
    if G.is_motor(n): return "motor"
    if e["term_class"] == "ControlTerminal": return "display-only (indicator)" if not e["is_source"] else "panel control"
    if c in ("Property", "Invoke"): return "UI property/invoke"
    if c.endswith("Constant"): return "constant"
    return "%s computation" % where(G, n, M)
def closure(G, n, M, cap=3000):
    """over-approximate downstream categories (node pass-through, error terminals skipped)."""
    seen, q, cats = {n}, collections.deque([n]), set()
    while q and len(seen) < cap:
        u = q.popleft()
        for t in (G.by_owner.get(u, []) if u not in G.term or G.term[u]["term_class"] != "ControlTerminal" else [G.term[u]]):
            if not t["is_source"] or not t["wire_uid"] or "error" in t["term_name"]: continue
            for s in G.by_wire[t["wire_uid"]]:
                v = G.node(s)
                if s["is_source"] or v in seen: continue
                seen.add(v); q.append(v)
                k = tag(G, v, s, M)
                if k in ("saved-data", "motor", "display-only (indicator)") or k.startswith(("1.2", "1.5", "1.7")): cats.add(k)
    return sorted(cats)
def tables(G):
    M = members(G); T1, T3 = [], []
    for b in B8:
        for src, T in ((True, T1), (False, T3)):
            for t in io_terms(G, b, src):
                for e, path in G.walk(t, src, lambda n: n in M and n != G.node(t)):
                    row = {"b": b, "term": t["term_name"], "term_uid": t["term_uid"], "owner": t["owner_uid"], "wire": t["wire_uid"],
                           "carriers": path, "cite_b": G.cite(t["term_uid"])}
                    if e is None:
                        row.update(end=None, tag="UNWIRED on this graph")
                    else:
                        n = G.node(e)
                        row.update(end=n, end_class=G.ncls(n), end_label=G.label(n), end_term=e["term_name"],
                                   loop=where(G, n, M), tag=tag(G, n, e, M), cite=G.cite(e["term_uid"]))
                        if src and n not in M: row["closure"] = closure(G, n, M)
                    T.append(row)
    return M, T1, T3
res = {"schema": "facts/1", "card": "108-3", "level": "STRUCTURAL, offline graph files only; no VI opened",
       "graphs": {"bed": [bed.name, bed.md5], "s1": [s1.name, s1.md5]}, "plan_disp_moved": {str(k): v for k, v in moved.items()}}
for key, G in (("bed", bed), ("s1", s1)):
    M, T1, T3 = tables(G)
    gate("G2 B uids %s" % key, all(b in G.cls for b in B8), "missing %s" % [b for b in B8 if b not in G.cls])
    xtra = {S: sorted(set(tunnels(G, S)) - P0T[S]) for S in BS}   # run 1: P0 lists DATA tunnels only; +N terminal
    gate("G3 tunnels %s" % key, all(P0T[S] <= set(tunnels(G, S)) for S in BS) and all(G.ncls(u) == "Tunnel" and not any(
        t["wire_uid"] for t in G.by_owner[u]) for x in xtra.values() for u in x), "extra (unwired Tunnel) %s" % xtra)
    gate("G4 ctl %s" % key, all(c in G.term for c in CTL), str([c for c in CTL if c not in G.term]))
    T4 = []
    for ct, ctl in CTL.items():
        if ct not in G.term: continue
        t = G.term[ct]
        for e, path in G.walk(t, True, lambda n: False):
            n = G.node(e) if e else None
            T4.append({"ctl": ctl, "ctlterm": ct, "label": t["term_name"], "reader": n, "reader_class": n and G.ncls(n),
                       "reader_term": e and e["term_name"], "carriers": path, "now": n and where(G, n, M),
                       "in_groupB": n in M, "plan_disp": moved.get(n), "cite": e and G.cite(e["term_uid"])})
        for lt in G.locals.get(t["term_name"], []):
            T4.append({"ctl": ctl, "ctlterm": ct, "label": t["term_name"], "reader": lt["owner_uid"], "reader_class": "Local",
                       "reader_term": "read" if lt["is_source"] else "WRITE", "now": where(G, lt["owner_uid"], M), "cite": G.cite(lt["term_uid"])})
    gate("G5 cites %s" % key, all(r.get("cite") or r.get("tag") == "UNWIRED on this graph" for r in T1 + T3 + T4), "")
    T2 = {b: {"self": moved.get(b), "members_moved": sorted([u, moved[u][0], moved[u][1]] for u in M if u in moved and
              (u == b or b in G.chain(u) or G.struct_of_tunnel(u) == b))} for b in B8}
    res[key] = {"members": len(M), "T1": T1, "T2": T2, "T3": T3, "T4": T4}
    for name, T in (("T1", T1), ("T3", T3)):
        for r in T:
            print(key, name, r["b"], repr(r["term"])[:28], "->", r.get("end"), r.get("end_class"), repr(r.get("end_label", ""))[:34],
                  repr(r.get("end_term", ""))[:22], r.get("loop"), "|", r["tag"], r.get("closure", ""), "via", r["carriers"][:6])
    for r in T4:
        print(key, "T4", r["ctl"], repr(r["label"])[:30], "->", r["reader"], r["reader_class"], repr(r["reader_term"])[:20], r["now"], r.get("plan_disp"))
    print(key, "T2", json.dumps(T2)[:900])
json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1, default=str)
npass = sum(1 for g in gates if g[1]); ff = next((g[0] + ": " + g[2] for g in gates if not g[1]), None)
print(protocol.result_line(protocol.make_result(npass, len(gates) - npass, ff,
      [{"path": "tools/bench/facts_c108c_groupB.json", "md5": hashlib.md5(open(OUT, "rb").read()).hexdigest()}])))
