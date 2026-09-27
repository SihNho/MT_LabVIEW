r"""diag_c114_plan - card 114-1 P1 + P2 (OFFLINE, no LabVIEW): on the SAVED B2b graph (tools/bench/graph_l2b2b_20260928.json, P1 read)
P1  the terminal-NAME diff of the bed vs S1 (docs/wiki/subvi/D1_s1_copy.json, md5 pinned) on the B3 row nodes + their cascade neighbours
    (depth 2 over wires, bed OR S1, structures/diagrams/CTs excluded) -> tools/bench/namediff_l2b3.json; D4 scope = nodes whose name
    multiset differs from S1's -> tools/bench/plan_l2b3_d4.json (schema toward-s1/1, as plan_l2b2b_d4.json).
P2  plan_l2b3_in.json: rows B3-01..06 (split_plan_111_l2b2.md s1 lines 34-36) = three tunnel groups on loop 1.2 (#10170, body #23166), each
    `tunnel` + wire src -> new:Tk.outer + wire new:Tk.inner -> sink. NOTHING TYPED BUT THE S1 TUNNEL UIDS OF THE SPLIT PAGE (28343, 5129,
    5328) AND THE BED SINKS (28370, 2992, 3176): the source terminal of each row is S1's source on the S1 tunnel's outer wire (same term uid
    must exist in the bed); the sink is the bed sink's unique OuterTerminal sink row; indexing = False (the loop class of S1's tunnels is
    printed). open_rows start from plan_l2b2b.json's; stagesim.simulate(route_check=True), round 2 re-declares the simulated end.
PRIOR ART: tools/bench/diag_c113b_plan.py (namediff + simulate + re-declare), plan_k_split.json (tunnel groups on #10170/#23166).
PREDICTION: S1 md5 5de014fe; 3 groups resolved; FINAL, open_rows_match; route check PASS 3 tunnel ops, none UNROUTABLE; the 7 B3 open rows
of plan_l2b2b.json close ((28083,'Mag pos when touched to glass'), (5696|6085, 'z index of first ref'|'z indices of all exp')).
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c114_plan.log -- py -u tools/bench/diag_c114_plan.py"""
import collections, hashlib, json, os, sys                                             # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))
import stagesim as SS, protocol                                                         # noqa: E401,E402
GR = os.path.join(HERE, "graph_l2b2b_20260928.json")
S1P, S1_MD5 = "docs/wiki/subvi/D1_s1_copy.json", "5de014fe580b938328fa8662cf2b0652"
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                           # noqa: E731
G, S1 = json.load(open(GR, encoding="utf-8")), json.load(open(os.path.join(ROOT, S1P), encoding="utf-8"))
B = json.load(open(os.path.join(HERE, "plan_l2b2b.json"), encoding="utf-8"))
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


BT, BW, ST, SW = by_term(G), by_wire(G), by_term(S1), by_wire(S1)
gate("S1 graph md5 == pin", md5(os.path.join(ROOT, S1P)) == S1_MD5, md5(os.path.join(ROOT, S1P)))
gate("B2b graph md5 of the VI == bed pin 4f51fd4c", G.get("md5") == "4f51fd4cb93e9116dee1bc0b07281f12", G.get("md5"))
cls_of = dict((int(o["uid"]), o["class"]) for o in G["objs"])
loops = dict((int(L["loop_uid"]), L) for L in G.get("loops") or [])
print("  FACT loop #10170 class {0}; S1 loop table: {1}".format((loops.get(10170) or {}).get("class"),
      [(L.get("loop_uid"), L.get("class")) for L in S1.get("loops") or []][:8]), flush=True)
# (id, split row, S1 tunnel, bed sink node)
GROUPS = [("t1", "B3-01/02", 28343, 28370), ("t2", "B3-03/04", 5129, 2992), ("t3", "B3-05/06", 5328, 3176)]
acts, rownodes = [], set()
for tid, sp, stun, sink in GROUPS:
    so = [r for r in S1["terminals"] if int(r["owner_uid"]) == stun and r["term_class"] == "OuterTerminal"]
    sw = int(so[0]["wire_uid"] or 0) if len(so) == 1 else 0
    srcs = [r for r in SW.get(sw, []) if r["is_source"] and int(r["owner_uid"]) != stun]
    src = BT.get(int(srcs[0]["term_uid"])) if len(srcs) == 1 else None
    dsts = [r for r in G["terminals"] if int(r["owner_uid"]) == sink and r["term_class"] == "OuterTerminal" and not r["is_source"]]
    print("  FACT {0} {1}: S1 tunnel #{2} ({3}) outer w{4} src {5}; bed src {6}; bed sink rows {7}".format(
        tid, sp, stun, (so[0]["owner_class"] if so else None), sw, [(r["owner_uid"], r["owner_class"], r["term_uid"], r["term_name"]) for r in srcs],
        src and (src["owner_uid"], src["owner_class"], src["term_uid"], src["term_name"], src["wire_uid"], src["frame_diagram"]),
        [(r["owner_class"], r["term_uid"], r["term_name"], r["wire_uid"], r["frame_diagram"]) for r in dsts]), flush=True)
    ok = bool(src and len(dsts) == 1 and src["is_source"])
    gate("ROW {0} ({1}) resolves: one S1 source on the S1 tunnel's outer wire, present in the bed; one unwired outer sink on #{2}".format(tid, sp, sink),
         ok and not int(dsts[0]["wire_uid"] or 0), (src and src["term_uid"], dsts and dsts[0]["term_uid"]))
    if not ok:
        continue
    s_own, d = int(src["owner_uid"]), dsts[0]
    T = tid.upper()
    acts += [{"op": "tunnel", "id": "b3_" + tid, "loop": 10170, "body": 23166, "dir": "in", "as": T, "indexing": False,
              "why": "{0} (split_plan_111_l2b2.md:34-36): replaces S1's 1.1 tunnel #{1} by a new tunnel on 1.2 #10170".format(sp, stun)},
             {"op": "wire", "id": "b3_{0}_out".format(tid), "src": {"uid": s_own, "term_uid": int(src["term_uid"])}, "dst": "new:{0}.outer".format(T),
              "why": "{0}: #{1} ({2}) {3!r} -> new tunnel outer (S1 wire {4})".format(sp, s_own, src["owner_class"], src["term_name"], sw)},
             {"op": "wire", "id": "b3_{0}_in".format(tid), "src": "new:{0}.inner".format(T), "dst": {"uid": sink, "term_uid": int(d["term_uid"])},
              "why": "{0}: new tunnel inner -> #{1} ({2}) outer face {3!r} (S1 wire of the sink {4})".format(
                  sp, sink, d["owner_class"], d["term_name"], (ST.get(int(d["term_uid"])) or {}).get("wire_uid"))}]
    rownodes |= {s_own, sink}
# ---- P1: name diff on the row nodes + cascade neighbours (depth 2 over wires, bed and S1)
SKIP = ("Diagram", "TopLevelDiagram", "WhileLoop", "ForLoop", "CaseStructure", "FlatSequence")
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
                    if x["owner_class"] not in SKIP and x["term_class"] != "ControlTerminal":
                        nxt.add(int(x["owner_uid"]))
    front = nxt if depth < 2 else set()
names = lambda tag, n: collections.Counter(r["term_name"] for r in dict((int(x["term_uid"]), x) for x in own_rows[(tag, n)]).values())   # noqa: E731
nd = []
for n in sorted(seen):
    a, b = names("bed", n), names("s1", n)
    nd.append({"node": n, "class": cls_of.get(n), "row_node": n in rownodes, "equal": a == b, "bed_only": dict(a - b), "s1_only": dict(b - a)})
scope = [x["node"] for x in nd if not x["equal"]]
for x in nd:
    print("  FACT NAMEDIFF #{0} {1} row={2} equal={3} bed-only {4} S1-only {5}".format(x["node"], x["class"], x["row_node"], x["equal"],
                                                                                      x["bed_only"], x["s1_only"]), flush=True)
ND = os.path.join(HERE, "namediff_l2b3.json")
json.dump({"schema": "namediff/1", "card": "114-1 P1", "bed_graph": {"path": "tools/bench/graph_l2b2b_20260928.json", "md5": md5(GR)},
           "s1": {"path": S1P, "md5": S1_MD5}, "row_nodes": sorted(rownodes), "nodes": nd, "scope_nodes": scope}, open(ND, "w", encoding="utf-8"), indent=1)
arts.append({"path": "tools/bench/namediff_l2b3.json", "md5": md5(ND)})
# ---- P2: the plan, simulated (route check on)
PIN = os.path.join(HERE, "plan_l2b3_in.json")
base_why = dict(((int(r["node"]), r["term"]), r["why"]) for r in B["open_rows"])
pin = {"schema": "stageplan/1", "stage": "l2b3", "goal": "L2-B3 (PD227(h), card 114-1): on the B2b bed D1_l2_b2b_20260928_015450.vi "
       "(graph_l2b2b_20260928.json, the SAVED file), rows B3-01..06 of split_plan_111_l2b2.md s1 = 3 tunnel groups on 1.2; every term uid looked "
       "up by tools/bench/diag_c114_plan.py", "base": {"path": "tools/bench/graph_l2b2b_20260928.json", "md5": md5(GR)},
       "context": {"s1_key": "D1_s1_copy"}, "actions": acts, "open_rows": [dict(r) for r in B["open_rows"]]}
kp = lambda keys: sorted(set((SS.V.key_parts(k)[0], SS.V.key_parts(k)[2]) for k in keys or []))   # noqa: E731
S, base_pairs = None, None
for rnd in (1, 2):
    json.dump(pin, open(PIN, "w", encoding="utf-8"), indent=1)
    S = SS.simulate(PIN, GR, out_root=os.path.join(HERE, "sim", "l2b3"), plan_out_dir=HERE, route_check=True)
    base_pairs, end = kp(S["steps"][0].get("cdiff_rows")), kp(S.get("end_cdiff_rows"))
    print("ROUND", rnd, "FINAL", S["final"], "open_rows_match", S["open_rows_match"], "failed", S["failed"], "base pairs", len(base_pairs),
          "end pairs", len(end), "declared", len(pin["open_rows"]), flush=True)
    if S["final"] or S["failed"]:
        break
    have = set((int(r["node"]), r["term"]) for r in pin["open_rows"])
    print("  DROPPED", sorted(have - set(end)), "ADDED", sorted(set(end) - have), flush=True)
    pin["open_rows"] = [{"node": n, "term": t, "why": base_why.get((n, t)) or ("carried from the B2b bed (saved-file cdiff, base)" if (n, t) in base_pairs
                         else "OPENED-BY-B3 in the simulation (not in the base cdiff)")} for n, t in end]
opened = [r for r in pin["open_rows"] if r["why"].startswith("OPENED-BY-B3")]
closed = sorted(set(base_pairs) - set((int(r["node"]), r["term"]) for r in pin["open_rows"]))
print("  FACT base cdiff pairs {0}; end {1}; closed by B3 {2}; OPENED-BY-B3 {3}".format(len(base_pairs), len(pin["open_rows"]), closed,
                                                                                  [(r["node"], r["term"]) for r in opened]), flush=True)
rc = S.get("route_check") or {}
for r in rc.get("rows") or []:
    print("ROUTE-ROW", r.get("k"), r.get("ids"), r.get("route"), "|", r.get("how"), "|", r.get("unroutable"), flush=True)
gate("P2 FINAL and open_rows_match", bool(S["final"] and S["open_rows_match"]), (S["final"], S["open_rows_match"], S["failed"]))
gate("P2 route check PASS, 3 tunnel ops covering {0} actions, none UNROUTABLE".format(len(acts)), rc.get("status") == "PASS" and len(rc.get("rows") or []) == 3
     and not any(r.get("unroutable") for r in rc.get("rows") or []), (rc.get("status"), str(rc.get("first_fail"))[:600]))
gate("P2 no OPENED-BY-B3 pair", not opened, [(r["node"], r["term"]) for r in opened])
if S.get("plan_out") and S["final"]:
    arts.append({"path": S["plan_out"]["path"], "md5": S["plan_out"]["md5"]})
    D4P = os.path.join(HERE, "plan_l2b3_d4.json")
    d4 = json.load(open(os.path.join(HERE, "plan_l2b2b_d4.json"), encoding="utf-8"))
    d4.update(stage="l2b3", card="tools/bench/cards/task_114-1.json P1 (D4 scope from the offline name diff, diag_c114_plan.py)",
              plan_md5=S["plan_out"]["md5"], scope_nodes=scope,
              scope_source="tools/bench/namediff_l2b3.json md5 {0}: the row/cascade nodes whose name multiset != S1's".format(md5(ND)))
    json.dump(d4, open(D4P, "w", encoding="utf-8"), indent=1)
    arts.append({"path": "tools/bench/plan_l2b3_d4.json", "md5": md5(D4P)})
    print("  FACT D4 scope {0} nodes: {1}".format(len(scope), scope), flush=True)
np_ = sum(1 for _g, ok in gates if ok)
print(protocol.result_line(protocol.make_result(np_, len(gates) - np_, next((g_ for g_, ok in gates if not ok), None), arts)))
