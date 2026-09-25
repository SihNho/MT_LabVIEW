r"""selftest_vigraph_frame_80 - card 80-7 (plan PD180(b)(c)). OFFLINE, no LabVIEW, nothing written but the log.
PRIOR ART: vigraph.build4/computation_diff (default mode, unchanged), jev_candidates.load/diagram_tree (frame sets per
case from tunnel inner terminals - same grouping idea), l2a1_facts_80 F5 (the merge measured). No new op.
PREDICTIONS (contract):
  V1a frame mode: every InnerTerminal of #5540's / #10445's tunnels keys on its frame ordinal (5582->0, 5592->1;
      10453->0, 10459->1); V1b default graph is byte-identical in keys/edges to a build without the new argument;
      V1c no key collisions in frame mode on S1 or D1_k.
  V2  cdiff_frame(S1, D1_k) rows == the 10 PB rows of 178(c) (l2a1_facts_80.json table.cdiff) by (node, sink); every
      extra/missing row printed; merged baseline also == 10 (reproduces l2a1_facts_80 P1).
  V3  synthetic swap of #6016's two frame inners' wires (6018<->6022) on S1: merged cdiff 0 rows, frame cdiff >= 1.
      Control: the same on an unswapped copy -> frame cdiff 0 rows.
  V5  #23541 facts (offline, l2a1_graph_k_80.json + l2a1_facts_80.json owners): class, owner, label, writers, readers.
    py tools/bgrun.py --material --max-min 10 --log tools/bench/selftest_vigraph_frame_80.log -- py -u tools/bench/selftest_vigraph_frame_80.py"""
import collections, json, os, sys, time                                            # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))  # noqa: E702
import vigraph as V, jev_candidates as JC, protocol as PR                           # noqa: E401,E402
N, FF = {"pass": 0, "fail": 0}, []


def gate(label, ok, detail=""):
    N["pass" if ok else "fail"] += 1
    if not ok and not FF:
        FF.append(label)
    print("  {0}  {1}{2}".format("PASS" if ok else "FAIL", label, (" | " + str(detail)[:900]) if detail != "" else ""), flush=True)


def fact(x):
    print("  FACT  " + str(x)[:1200], flush=True)


def s1_parts():
    rec = json.load(open(os.path.join(JC.WIKI, JC.S1_KEY + ".json"), encoding="utf-8"))
    op, lp = JC._newest("graph_objs_s1_*.json"), JC._newest("graph_loops_s1_*.json")
    fact("S1 parts: wiki {0} md5 {1}; objs {2}; loops {3}".format(JC.S1_KEY, rec.get("md5"), os.path.basename(op), os.path.basename(lp)))
    return rec["terminals"], json.load(open(op, encoding="utf-8"))["objects"], json.load(open(lp, encoding="utf-8"))["loops"], rec["fs_tunnel_pairs"]


def cd_rows(cd):
    return sorted((V.key_parts(r["sink"])[0], V.key_parts(r["sink"])[2]) for r in cd["rows"])


t0, LAB = time.time(), JC.node_labels_default()
S1p = s1_parts()
gk = json.load(open(os.path.join(HERE, "l2a1_graph_k_80.json"), encoding="utf-8"))
F = json.load(open(os.path.join(HERE, "l2a1_facts_80.json"), encoding="utf-8"))
Kp = (gk["terminals"], gk["objs"], gk["loops"], gk["fs_tunnel_pairs"])
fact("D1_k graph md5 field {0} ({1} terminals)".format(gk["md5"], len(gk["terminals"])))
b = lambda p, fk: V.build4(p[0], p[1], p[2], LAB, p[3], frame_keyed=fk)             # noqa: E731
A0, B0, Af, Bf = b(S1p, False), b(Kp, False), b(S1p, True), b(Kp, True)
fact("build 4 graphs {0:.1f} s; frame record S1 {1}; K {2}".format(time.time() - t0, Af["method"]["frame_keyed"], Bf["method"]["frame_keyed"]))

print("---------- V1 keying")
want = {5999: 0, 6003: 1, 6018: 0, 6022: 1, 5705: 0, 6033: 1, 10586: 0, 10590: 1, 11338: 0, 11342: 1, 10752: 0, 10755: 1}
for tag, G in (("S1", Af), ("K", Bf)):
    got = dict((r["term_uid"], V.key_parts(k)[3]) for k, r in G["rows"].items() if r["term_uid"] in want)
    gate("V1a {0}: #5540/#10445 tunnel inners key on frame ordinal (5582/10453->0, 5592/10459->1)".format(tag), got == want, sorted(got.items()))
    gate("V1c {0}: frame mode has no key collisions".format(tag), not G["method"]["frame_keyed"]["key_collisions"], G["method"]["frame_keyed"]["key_collisions"])
Dn = V.build4(S1p[0], S1p[1], S1p[2], LAB, S1p[3])
gate("V1b default mode unchanged: same keys and edges with and without frame_keyed=False, no frame fields",
     set(Dn["rows"]) == set(A0["rows"]) and sorted(Dn["edges"]) == sorted(A0["edges"]) and "frame_keyed" not in A0 and "frame_keyed" not in A0["method"])
diffk = sorted(set(A0["rows"]) ^ set(Af["rows"]))
fact("V1 S1 keys that differ default vs frame: {0} (the inner terminals whose uid rank != frame rank)".format(len(diffk)))
try:
    V.computation_diff(A0, Bf); gate("V1d mixed-mode computation_diff refused", False)          # noqa: E702
except ValueError as e:
    gate("V1d mixed-mode computation_diff refused", True, str(e))

print("---------- V2 cdiff_frame(S1, D1_k) vs 178(c) PB")
pb = sorted((V.key_parts(k)[0], V.key_parts(k)[2]) for k in [])  # placeholder, replaced below
pb = sorted((r["node"], r["sink"].split(" ", 2)[2].strip("'") if "'" in r["sink"] else "") for r in F["table"]["cdiff"])
fact("PB (l2a1_facts_80.json table.cdiff, 178(c)): {0}".format(pb))
t1 = time.time(); cm = V.computation_diff(A0, B0); cf = V.computation_diff_frame(Af, Bf)                 # noqa: E702
fact("cdiff merged+frame {0:.1f} s".format(time.time() - t1))
gate("V2a merged baseline cdiff(S1, D1_k) == the 10 PB rows", cd_rows(cm) == pb, {"extra": sorted(set(cd_rows(cm)) - set(pb)), "missing": sorted(set(pb) - set(cd_rows(cm)))})
gate("V2 cdiff_frame(S1, D1_k) == the 10 PB rows (by node, sink)", cd_rows(cf) == pb,
     {"extra": sorted(set(cd_rows(cf)) - set(pb)), "missing": sorted(set(pb) - set(cd_rows(cf)))})
for r in cf["rows"]:
    fact("CDIFF_FRAME {0} before {1} after {2}".format(V.show(r["sink"]), r["before"], r["after"]))
fact("nodes added/removed frame {0}/{1}, merged {2}/{3}".format(len(cf["computation_nodes_added"]), len(cf["computation_nodes_removed"]),
     len(cm["computation_nodes_added"]), len(cm["computation_nodes_removed"])))

print("---------- V3 negative: swap #6016's frame inners' wires on S1")
T = [dict(r) for r in S1p[0]]
w = dict((r["term_uid"], r["wire_uid"]) for r in T if r["term_uid"] in (6018, 6022))
fact("V3 before swap: 6018 w{0} (frame 5582), 6022 w{1} (frame 5592)".format(w[6018], w[6022]))
for r in T:
    if r["term_uid"] in w:
        r["wire_uid"] = w[6022 if r["term_uid"] == 6018 else 6018]
sw = (T,) + S1p[1:]
nm, nf = V.computation_diff(A0, b(sw, False)), V.computation_diff_frame(Af, b(sw, True))
gate("V3a merged mode MISSES the swap (0 rows)", not nm["rows"], cd_rows(nm))
gate("V3b frame mode DETECTS the swap (>= 1 row)", len(nf["rows"]) >= 1, [(V.show(r["sink"]), r["before"][:3], r["after"][:3]) for r in nf["rows"]][:6])
nc = V.computation_diff_frame(Af, b(S1p, True))
gate("V3c control: frame cdiff(S1, S1 rebuilt) == 0 rows", not nc["rows"], cd_rows(nc))

print("---------- V5 #23541 on D1_k (offline)")
O = dict((int(k), tuple(v)) for k, v in F["owners"].items())


def loop_of(d):
    for _n in range(14):
        c, u = O.get(d, ("?", 0))
        if c in ("WhileLoop", "ForLoop"):
            return "{0}#{1}".format(c, u)
        if not u or c not in V.STRUCT_OWNER:
            return "top(D{0}:{1})".format(d, c)
        d = O.get(u, ("?", 0))[1]
    return "?"


KT = V.dedupe_rows(gk["terminals"])[0]
ct = [r for r in KT if r["term_uid"] == 23541]
cls_ = dict((int(o["uid"]), o["class"]) for o in gk["objs"])
fact("V5 #23541 rows {0}; census class {1}".format(ct, cls_.get(23541)))
lab = ct[0]["term_name"] if ct else None
same = [r for r in KT if r.get("term_class") == "ControlTerminal" and r["term_name"] == lab]
fact("V5 ControlTerminals labelled {0!r}: {1}".format(lab, [(r["term_uid"], r["is_source"], r["wire_uid"], r["frame_diagram"]) for r in same]))
WI = collections.defaultdict(list)
for r in KT:
    WI[r["wire_uid"]].append(r)
for r in ct:
    ends = [(x["owner_uid"], x["owner_class"], x["term_name"], x["is_source"], loop_of(int(x["frame_diagram"] or 0))) for x in WI[r["wire_uid"]] if x is not r] if r["wire_uid"] else []
    fact("V5 #23541 {0} w{1} diagram {2} loop {3} -> {4}".format("SOURCE(control)" if r["is_source"] else "SINK(indicator)", r["wire_uid"], r["frame_diagram"], loop_of(int(r["frame_diagram"] or 0)), ends))
loc = [r for r in KT if r["owner_class"] in ("Local", "Global") and r["term_name"] == lab]
for r in loc:
    fact("V5 {0} #{1} {2} w{3} diagram {4} loop {5}".format(r["owner_class"], r["owner_uid"], "READ" if r["is_source"] else "WRITE", r["wire_uid"], r["frame_diagram"], loop_of(int(r["frame_diagram"] or 0))))
refs = [r for r in KT if r["owner_class"] in ("Property", "Invoke", "ControlReference", "StaticControlReference") and lab and lab in (r["term_name"] or "")]
prop_like = collections.Counter(o["class"] for o in gk["objs"] if "Reference" in o["class"] or o["class"] in ("Property", "PropertyNode"))
fact("V5 reference-capable objects on D1_k by class (targets NOT in the offline census): {0}".format(dict(prop_like)))
wr = [r for r in ct if not r["is_source"] and r["wire_uid"]] + [r for r in loc if not r["is_source"]]
rd = [r for r in loc if r["is_source"]]
gate("V5 #23541: ControlTerminal, exactly 1 writer (w23556 from #10757), readers all Locals, label unique",
     bool(ct) and len(wr) == 1 and wr[0]["wire_uid"] == 23556 and len(same) == 1 and all(not r["is_source"] for r in ct),
     {"writers": [(r["owner_uid"], r["owner_class"], r["wire_uid"]) for r in wr], "local_readers": len(rd), "same_label": len(same)})
print("=== selftest_vigraph_frame_80: {0} pass / {1} fail ({2:.1f} s)".format(N["pass"], N["fail"], time.time() - t0))
print(PR.result_line(PR.make_result(N["pass"], N["fail"], FF[0] if FF else None)))
sys.exit(1 if N["fail"] else 0)
