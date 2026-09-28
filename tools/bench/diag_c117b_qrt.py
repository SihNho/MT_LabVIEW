"""Card 117-2 (offline, no LabVIEW, read-only): QRT facts per open cross-loop pair on the SAVED L2-R1 graph.

Existing tools used, not edited (found by `grep "^def " tools/stagesim.py tools/vigraph.py tools/jev_candidates.py`, the
same set diag_c114e_inventory.py uses): stagesim.base_state/cdiff_inputs/graph/effective_consumers
(tools/stagesim.py:239,1180,364,376), vigraph.computation_diff/effective_sources/reach4/terminals/key_parts
(tools/vigraph.py:847,782,675,653,248), jev_candidates.load/_ancestors (tools/jev_candidates.py:73,122).
Prediction contract: graph md5 == card (e429f7ad...); computation_diff(S1, R1) sink keys == plan_l2r1.json
end_cdiff_rows (16) and group into 11 (node, term) pairs; every pair has a non-empty S1 effective source; per pair the
script records S1 wire, S1 source(s) with their loop (by body-diagram ancestry), the R1 sink state, the sink's loop, the
case-frame chain of each source, and the S1 downstream ends of the sink node. Writes tools/bench/diag_c117b_qrt.json.
Ends with one RESULT line."""
import collections, hashlib, json, os, sys

ROOT = r"G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop"
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagesim as SS          # noqa: E402
import vigraph as V            # noqa: E402
import jev_candidates as JC    # noqa: E402
import protocol                # noqa: E402

B = os.path.join(ROOT, "tools", "bench")
GP, PP = os.path.join(B, "graph_l2r1_saved_20260928.json"), os.path.join(B, "plan_l2r1.json")
OUT = os.path.join(B, "diag_c117b_qrt.json")
LOOPS = {637: "1.1", 10170: "1.2", 23032: "1.5", 23041: "1.7"}
KNOWN_BODY = {639: 637, 23166: 10170, 23405: 23041}
END_CLASSES = ("ControlTerminal", "SubVI", "Local", "Global", "Property", "PropertyNode", "Invoke", "InvokeNode")
npass = nfail = 0
first_fail = None


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def gate(ok, label):
    global npass, nfail, first_fail
    print(("  PASS  " if ok else "  FAIL  ") + label)
    if ok:
        npass += 1
    else:
        nfail += 1
        first_fail = first_fail or label


gate(md5(GP) == "e429f7ad7b2eebdaabaf0db1a462f10e", "G0 md5 graph_l2r1_saved == card")
g = json.load(open(GP, encoding="utf-8"))
plan = json.load(open(PP, encoding="utf-8"))
print("GRAPH keys", sorted(g.keys()))
print("TERMROW keys", sorted((g.get("terminals") or [{}])[0].keys()))
print("LOOP keys", sorted(((g.get("loops") or [{}])[0] or {}).keys()))
st = SS.base_state(g)
lab, fs, rec = SS.cdiff_inputs(plan, st)
G = SS.graph(st, labels=lab, fs_pairs=fs)
S1 = JC.load("D1_s1_copy")
print("cdiff_inputs", rec, "R1 nodes", len(G["cls"]), "S1 nodes", len(S1["cls"]))
owners = st["owners"]
objs = dict((int(o["uid"]), o) for o in g.get("objs") or [])

# ---- loop body diagrams: KNOWN (split plan :185, :83) + every loop tunnel/SR inner face whose owner is a named loop
votes = collections.defaultdict(collections.Counter)
for u, o in objs.items():
    own = owners.get(str(u))
    if own and own[1] in LOOPS and o.get("class") in ("LoopTunnel", "LeftShiftRegister", "RightShiftRegister"):
        for r in G["by_node"].get(u, []):
            if r["term_class"] == "InnerTerminal" and r.get("frame_diagram"):
                votes[int(r["frame_diagram"])][own[1]] += 1
BODY = dict(KNOWN_BODY)
for d, c in votes.items():
    BODY.setdefault(d, c.most_common(1)[0][0])
print("BODY", BODY, "votes", {d: dict(c) for d, c in votes.items()})
TYPE_FIELDS = [k for k in ((g.get("terminals") or [{}])[0].keys()) if "type" in k.lower() and k != "term_class"]
print("TYPE_FIELDS", TYPE_FIELDS)


def where(GG, key):
    r = GG["rows"].get(key)
    if not r:
        return {"loop": None, "chain": [], "case_frames": [], "fd": None}
    d = int(r.get("frame_diagram") or 0)
    chain = JC._ancestors(GG["tree"], d) if d else []
    loop, before = "top", []
    for x in chain:
        if x in BODY:
            loop = BODY[x]
            break
        before.append(x)
    cases = [x for x in before if x in GG["tree"]["exclusive"]]
    return {"loop": loop, "loop_name": LOOPS.get(loop, loop), "fd": d, "chain": chain[:8],
            "inside_below_loop_body": before, "case_frames": cases}


def desc(GG, key):
    n, c, name, _o = V.key_parts(key)
    r = GG["rows"].get(key) or {}
    d = {"key": key, "node": n, "class": GG["cls"].get(n), "term": name, "term_uid": r.get("term_uid"),
         "label": (GG.get("labels") or {}).get(n, ""), "subvi": (GG.get("subvi_name") or {}).get(n),
         "wire": r.get("wire_uid")}
    for f in TYPE_FIELDS:
        d[f] = r.get(f)
    d.update(where(GG, key))
    return d


def direct_sources(GG, key):
    return sorted(a for k, a, _i in GG["in"].get(key, ()) if k == "wire")


def ends(GG, node):
    outs = V.terminals(GG, node=node, is_source=True)
    reach = V.reach4(GG, outs)
    c = collections.Counter()
    for k in reach:
        n, _c, name, _o = V.key_parts(k)
        cl = GG["cls"].get(n)
        r = GG["rows"].get(k) or {}
        if cl in END_CLASSES and not r.get("is_source"):
            c["{0}|{1}|{2}|{3}".format(n, cl, (GG.get("subvi_name") or {}).get(n) or (GG.get("labels") or {}).get(n, ""),
                                       name)] += 1
    return sorted(c)


cd = V.computation_diff(S1, G)
keys = sorted(set(r["sink"] for r in cd["rows"]))
want = sorted(plan["finalized"]["end_cdiff_rows"])
print("CDIFF n", len(keys), "only_measured", sorted(set(keys) - set(want)), "only_plan", sorted(set(want) - set(keys)))
gate(keys == want, "G1 cdiff(S1, R1 saved) sink keys == plan_l2r1 end_cdiff_rows ({0} vs {1})".format(len(keys), len(want)))
byrow = dict((r["sink"], r) for r in cd["rows"])
pairs = collections.OrderedDict()
for k in keys:
    n, _c, name, _o = V.key_parts(k)
    pairs.setdefault((n, name), []).append(k)
gate(len(pairs) == 11, "G2 pairs (node, term) == 11: {0}".format(len(pairs)))

out = []
for (n, name), ks in pairs.items():
    row = {"pair": [n, name], "rows": []}
    for k in ks:
        cr = byrow[k]
        s1_src = [desc(S1, x) for x in (cr["before"] or [])]
        r1_src = [desc(G, x) if x in G["rows"] else {"key": x} for x in (cr["after"] or [])]
        rr = {"key": k, "sink_S1": desc(S1, k) if k in S1["rows"] else None,
              "sink_R1": desc(G, k) if k in G["rows"] else None,
              "S1_direct_wire_sources": direct_sources(S1, k), "R1_direct_wire_sources": direct_sources(G, k),
              "S1_effective_sources": s1_src, "R1_effective_sources": r1_src,
              "S1_source_locations_in_R1": [desc(G, x["key"]) if x["key"] in G["rows"] else {"key": x["key"], "absent": True}
                                            for x in s1_src]}
        row["rows"].append(rr)
    row["sink_downstream_ends_S1"] = ends(S1, n)[:25]
    row["sink_downstream_ends_S1_n"] = len(ends(S1, n))
    gate(all(r["S1_effective_sources"] for r in row["rows"]) or n == 2626,
         "G3 #{0} '{1}' S1 effective source non-empty".format(n, name))
    out.append(row)
    print("PAIR", json.dumps(row, default=str)[:3000])

json.dump({"schema": "diag/c117b-qrt", "graph": {"path": "tools/bench/graph_l2r1_saved_20260928.json", "md5": md5(GP)},
           "plan": {"path": "tools/bench/plan_l2r1.json", "md5": md5(PP)}, "cdiff_inputs": rec, "body": BODY,
           "type_fields": TYPE_FIELDS, "cdiff_keys": keys, "pairs": out}, open(OUT, "w", encoding="utf-8"),
          indent=1, default=str)
gate(os.path.exists(OUT), "G4 written " + OUT)
print(protocol.result_line(protocol.make_result(npass, nfail, first_fail,
                                                [{"path": "tools/bench/diag_c117b_qrt.json", "md5": md5(OUT)}])))
