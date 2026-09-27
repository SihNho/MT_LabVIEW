r"""diag_c113b_plan - card 113-1 P1 + P2 (OFFLINE, no LabVIEW): on the SAVED B2a graph (tools/bench/graph_l2b2a_20260928.json, P0)
P1  the terminal-NAME diff of the bed vs S1 (docs/wiki/subvi/D1_s1_copy.json, md5 pinned below) on the B2b row nodes + their cascade
    neighbours (every node sharing a wire with a row node, bed OR S1, depth 2, structures/diagrams excluded) ->
    tools/bench/namediff_l2b2b.json; D4 scope = the nodes whose name multiset differs from S1's (an equal node cannot grow an S1
    name without breaking D4's count cap), written to tools/bench/plan_l2b2b_d4.json (same schema as plan_l2b2a_d4.json).
P2  plan_l2b2b_in.json: rows B2-01..08 + B2-16 (split_plan_111_l2b2.md s2) - every term uid LOOKED UP in the base graph by
    (owner, face/name, direction), never typed; B2-07 only if S1's #29172 outer face has ONE sink and it is #28786 (card rule
    B2-07); then stagesim.simulate(route_check=True) as diag_c112c_plan.py does (round 1 = B2a's open_rows, round 2 = the
    simulated end re-declared, each pair tagged 'base' (in the bed's own cdiff) or 'OPENED-BY-B2b').
PRIOR ART: tools/bench/diag_c112c_plan.py (simulate + re-declare), diag_c111b_b1graph.py; stagesim/stagexec unchanged.
PREDICTION: S1 md5 5de014fe; 9 rows resolved; FINAL True, route check PASS (no UNROUTABLE); 0 OPENED-BY-B2b pairs.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c113b_plan.log -- py -u tools/bench/diag_c113b_plan.py"""
import collections, hashlib, json, os, sys                                             # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))
import stagesim as SS, protocol                                                         # noqa: E401,E402
GR = os.path.join(HERE, "graph_l2b2a_20260928.json")
S1P, S1_MD5 = "docs/wiki/subvi/D1_s1_copy.json", "5de014fe580b938328fa8662cf2b0652"
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                           # noqa: E731
G, S1 = json.load(open(GR, encoding="utf-8")), json.load(open(os.path.join(ROOT, S1P), encoding="utf-8"))
A = json.load(open(os.path.join(HERE, "plan_l2b2a.json"), encoding="utf-8"))
gates, arts = [], []


def gate(lab, ok, det=""):
    gates.append((lab, bool(ok)))
    print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", lab, str(det)[:900]), flush=True)


def by_term(gr):
    return dict((int(r["term_uid"]), r) for r in gr["terminals"])


def by_wire(gr):
    d = collections.defaultdict(list)
    for r in gr["terminals"]:
        if int(r["wire_uid"] or 0):
            d[int(r["wire_uid"])].append(r)
    return d


BT, BW = by_term(G), by_wire(G)
ST, SW = by_term(S1), by_wire(S1)
gate("S1 graph md5 == pin", md5(os.path.join(ROOT, S1P)) == S1_MD5, md5(os.path.join(ROOT, S1P)))


def face(owner, cls, src):                          # a tunnel's OUTER face / a node's named terminal / a CT (own uid)
    if cls == "CT":
        r = BT.get(owner)
        return r if r and r["term_class"] == "ControlTerminal" else None
    hits = [r for r in BT.values() if int(r["owner_uid"]) == owner and bool(r["is_source"]) == src and
            (r["term_class"] == "OuterTerminal" if cls == "outer" else r["term_name"] == cls)]
    return hits[0] if len(hits) == 1 else None


# (id, split-page row, src (owner, face|name|CT, is_source), dst (owner, face|name|CT, is_source))
ROWS = [("b2_01", "B2-01", (8885, "x*y", True), (10004, "outer", False)),
        ("b2_02", "B2-02", (8885, "x*y", True), (30135, "outer", False)),
        ("b2_03", "B2-03", (11363, "outer", True), (11261, "array", False)),
        ("b2_04", "B2-04", (28170, "CT", True), (31051, "outer", False)),
        ("b2_05", "B2-05", (29091, "CT", True), (31137, "outer", False)),
        ("b2_06", "B2-06", (29091, "CT", True), (30896, "outer", False)),
        ("b2_07", "B2-07", (29172, "outer", True), (28786, "CT", False)),
        ("b2_08", "B2-08", (5058, "x,y,z array out", True), (2765, "outer", False)),
        ("b2_16", "B2-16", (9306, "CT", True), (6132, "outer", False))]
s7 = [r for r in S1["terminals"] if int(r["owner_uid"]) == 29172 and r["term_class"] == "OuterTerminal"]
s7w = int(s7[0]["wire_uid"] or 0) if len(s7) == 1 else 0
s7sinks = sorted(set(int(x["term_uid"]) for x in SW.get(s7w, []) if not x["is_source"]))
b207 = s7sinks == [28786] and (ST.get(28786) or {}).get("term_class") == "ControlTerminal"
print("  FACT B2-07 rule: S1 #29172 outer face rows {0}, wire {1}, sinks {2} -> route it: {3}".format(len(s7), s7w, s7sinks, b207), flush=True)
acts, rownodes = [], set()
for rid, sp, s, d in ROWS:
    if rid == "b2_07" and not b207:
        continue
    rs, rd = face(*s), face(*d)
    gate("ROW {0} ({1}) resolves: src #{2} {3!r} -> dst #{4} {5!r}".format(rid, sp, s[0], s[1], d[0], d[1]), rs and rd,
         (rs and (rs["term_uid"], rs["wire_uid"]), rd and (rd["term_uid"], rd["wire_uid"])))
    if rs and rd:
        acts.append({"op": "wire", "id": rid, "src": {"uid": s[0], "term_uid": int(rs["term_uid"])},
                     "dst": {"uid": d[0], "term_uid": int(rd["term_uid"])},
                     "why": "{0} (split_plan_111_l2b2.md s1/s2): #{1} {2!r} (w{3}) -> #{4} {5!r} (w{6}); S1 wire of the sink: {7}".format(
                         sp, s[0], rs["term_name"], rs["wire_uid"], d[0], rd["term_name"], rd["wire_uid"],
                         (ST.get(int(rd["term_uid"])) or {}).get("wire_uid"))})
        rownodes |= {s[0], d[0]}
# ---- P1: name diff on the row nodes + cascade neighbours (depth 2 over wires, bed and S1)
SKIP = ("Diagram", "TopLevelDiagram", "WhileLoop", "ForLoop", "CaseStructure", "FlatSequence")
cls_of = dict((int(o["uid"]), o["class"]) for o in G["objs"])
own_rows = collections.defaultdict(list)
for gr, tag in ((G, "bed"), (S1, "s1")):
    for r in gr["terminals"]:
        own_rows[(tag, int(r["owner_uid"]))].append(r)
front, seen = set(n for n in rownodes if cls_of.get(n) not in SKIP and not (BT.get(n) or {}).get("term_class") == "ControlTerminal"), set()
for depth in (0, 1, 2):
    nxt = set()
    for n in front - seen:
        seen.add(n)
        for tag, bw in (("bed", BW), ("s1", SW)):
            for r in own_rows[(tag, n)]:
                for x in bw.get(int(r["wire_uid"] or 0), []):
                    o = int(x["owner_uid"])
                    if x["owner_class"] not in SKIP and x["term_class"] != "ControlTerminal":
                        nxt.add(o)
    front = nxt if depth < 2 else set()
names = lambda tag, n: collections.Counter(r["term_name"] for r in dict((int(x["term_uid"]), x) for x in own_rows[(tag, n)]).values())   # noqa: E731
nd = []
for n in sorted(seen):
    a, b = names("bed", n), names("s1", n)
    nd.append({"node": n, "class": cls_of.get(n), "row_node": n in rownodes, "equal": a == b,
               "bed_only": dict(a - b), "s1_only": dict(b - a)})
scope = [x["node"] for x in nd if not x["equal"]]
for x in nd:
    print("  FACT NAMEDIFF #{0} {1} row={2} equal={3} bed-only {4} S1-only {5}".format(x["node"], x["class"], x["row_node"], x["equal"],
                                                                                      x["bed_only"], x["s1_only"]), flush=True)
ND = os.path.join(HERE, "namediff_l2b2b.json")
json.dump({"schema": "namediff/1", "card": "113-1 P1", "bed_graph": {"path": "tools/bench/graph_l2b2a_20260928.json", "md5": md5(GR)},
           "s1": {"path": S1P, "md5": S1_MD5}, "row_nodes": sorted(rownodes), "nodes": nd, "scope_nodes": scope}, open(ND, "w", encoding="utf-8"), indent=1)
arts.append({"path": "tools/bench/namediff_l2b2b.json", "md5": md5(ND)})
# ---- P2: the plan, simulated (route check on)
PIN = os.path.join(HERE, "plan_l2b2b_in.json")
base_why = dict(((int(r["node"]), r["term"]), r["why"]) for r in A["open_rows"])
pin = {"schema": "stageplan/1", "stage": "l2b2b", "goal": "L2-B2b (PD226(e), card 113-1): on the B2a bed D1_l2_b2a_20260928_001426.vi "
       "(graph_l2b2a_20260928.json, the SAVED file), rows B2-01..08 + B2-16 of split_plan_111_l2b2.md s2 (B2-07 per card rule B2-07); "
       "every term uid looked up in the base graph by tools/bench/diag_c113b_plan.py",
       "base": {"path": "tools/bench/graph_l2b2a_20260928.json", "md5": md5(GR)}, "context": {"s1_key": "D1_s1_copy"},
       "actions": acts, "open_rows": [dict(r) for r in A["open_rows"]]}
S, base_pairs = None, None
for rnd in (1, 2):
    json.dump(pin, open(PIN, "w", encoding="utf-8"), indent=1)
    S = SS.simulate(PIN, GR, out_root=os.path.join(HERE, "sim", "l2b2"), plan_out_dir=HERE, route_check=True)
    kp = lambda keys: sorted(set((SS.V.key_parts(k)[0], SS.V.key_parts(k)[2]) for k in keys or []))   # noqa: E731
    base_pairs = kp(S["steps"][0].get("cdiff_rows"))
    end = kp(S.get("end_cdiff_rows"))
    print("ROUND", rnd, "FINAL", S["final"], "open_rows_match", S["open_rows_match"], "failed", S["failed"], "base pairs", len(base_pairs),
          "end pairs", len(end), "declared", len(pin["open_rows"]), flush=True)
    if S["final"] or S["failed"]:
        break
    have = set((int(r["node"]), r["term"]) for r in pin["open_rows"])
    print("  DROPPED", sorted(have - set(end)), "ADDED", sorted(set(end) - have), flush=True)
    pin["open_rows"] = [{"node": n, "term": t, "why": base_why.get((n, t)) or ("carried from the B2a bed (saved-file cdiff, base)" if (n, t) in base_pairs
                         else "OPENED-BY-B2b in the simulation (not in the base cdiff)")} for n, t in end]
opened = [r for r in pin["open_rows"] if r["why"].startswith("OPENED-BY-B2b")]
closed = sorted(set(base_pairs) - set((int(r["node"]), r["term"]) for r in pin["open_rows"]))
print("  FACT base cdiff pairs {0}; end {1}; closed by B2b {2}; OPENED-BY-B2b {3}".format(len(base_pairs), len(pin["open_rows"]), closed,
                                                                                    [(r["node"], r["term"]) for r in opened]), flush=True)
rc = S.get("route_check") or {}
for r in rc.get("rows") or []:
    print("ROUTE-ROW", r.get("k"), r.get("ids"), r.get("route"), "|", r.get("how"), "|", r.get("unroutable"), flush=True)
gate("P2 FINAL and open_rows_match", bool(S["final"] and S["open_rows_match"]), (S["final"], S["open_rows_match"], S["failed"]))
gate("P2 route check PASS, {0} rows, none UNROUTABLE".format(len(acts)), rc.get("status") == "PASS" and len(rc.get("rows") or []) == len(acts)
     and not any(r.get("unroutable") for r in rc.get("rows") or []), (rc.get("status"), str(rc.get("first_fail"))[:600]))
gate("P2 no pair OPENED by B2b in the simulation", not opened, [(r["node"], r["term"]) for r in opened])
D4P = os.path.join(HERE, "plan_l2b2b_d4.json")
if S.get("plan_out"):
    arts.append({"path": S["plan_out"]["path"], "md5": S["plan_out"]["md5"]})
    json.dump({"schema": "toward-s1/1", "stage": "l2b2b", "card": "tools/bench/cards/task_113-1.json P1 (D4 scope from the offline name diff)",
               "plan_md5": S["plan_out"]["md5"], "s1": {"path": S1P, "md5": S1_MD5, "why": "PD226(c) rule D4; same S1 file as plan_l2b2a_d4.json"},
               "scope_nodes": scope, "scope_source": "tools/bench/namediff_l2b2b.json md5 {0}: the row/cascade nodes whose name multiset != S1's".format(md5(ND)),
               "rule_e1": "as plan_l2b2a_d4.json (stagekit.d4_e1)", "rule_pb": "as plan_l2b2a_d4.json (stagekit.d4_pb)",
               "facts_only": "S1-FORM lines per scope node"}, open(D4P, "w", encoding="utf-8"), indent=1)
    arts.append({"path": "tools/bench/plan_l2b2b_d4.json", "md5": md5(D4P)})
np_ = sum(1 for _g, ok in gates if ok)
print(protocol.result_line(protocol.make_result(np_, len(gates) - np_, next((g_ for g_, ok in gates if not ok), None), arts)))
