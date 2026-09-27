"""Card 114-5 (offline, no LabVIEW, read-only): L2-R retire-candidate inventory on graph_l2b3_20260928.json.

Existing tools used, not edited: stagesim.base_state/graph/cdiff_inputs (tools/stagesim.py:239,364,1180),
stagesim.effective_consumers (tools/stagesim.py:376), vigraph.reach4 / effective_sources (tools/vigraph.py:675,782).
Prediction contract: graph + plan md5 match the card; every candidate uid is either found (class, owner) or reported
missing; per source face: direct wire sinks + effective (computation) consumers. Writes
tools/bench/facts_c114e_inventory.json. Ends with one RESULT line."""
import collections, hashlib, json, os, sys

ROOT = r"G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop"
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagesim as SS          # noqa: E402
import vigraph as V            # noqa: E402
import jev_candidates as JC    # noqa: E402
import protocol                # noqa: E402

B = os.path.join(ROOT, "tools", "bench")
GP, PP = os.path.join(B, "graph_l2b3_20260928.json"), os.path.join(B, "plan_l2b3.json")
WANT = {GP: "e45f75ab751b7de6c25d5a18a6533e0b", PP: "827be8f3d9fac5e36590544369eda1ca"}
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


for p, m in WANT.items():
    gate(md5(p) == m, "G0 md5 {0} == {1}".format(os.path.basename(p), m))

g = json.load(open(GP, encoding="utf-8"))
plan = json.load(open(PP, encoding="utf-8"))
st = SS.base_state(g)
lab, fs, rec = SS.cdiff_inputs(plan, st)
G = SS.graph(st, labels=lab, fs_pairs=fs)
print("graph", g.get("vi"), g.get("md5"), "cdiff_inputs", rec, "nodes", len(G["nodes"]), "edges", len(G["edges"]))
objs = dict((int(o["uid"]), o) for o in g.get("objs") or [])
owners = st["owners"]
loops = dict((int(L["loop_uid"]), L) for L in g.get("loops") or [])


def cls_of(u):
    return (objs.get(u) or {}).get("class") or G["cls"].get(u)


def label(u):
    return (G.get("labels") or {}).get(u, "")


def face_info(u):
    rows = [r for r in G["rows"].values() if r["node"] == u]
    out = []
    for r in sorted(rows, key=lambda x: (x["term_uid"], x["key"])):
        key = r["key"]
        d = {"key": key, "term_uid": r["term_uid"], "name": r["term_name"], "tclass": r["term_class"],
             "is_source": bool(r["is_source"]), "wire": r["wire_uid"], "frame_diagram": r.get("frame_diagram")}
        if r["is_source"]:
            direct = sorted(set((V.key_parts(b)[0], (G["rows"].get(b) or {}).get("term_uid")) for k, b, _i in
                                G["out"].get(key, ()) if k == "wire"))
            eff = sorted(SS.effective_consumers(G, key))
            d["direct_sinks"] = [[n, t, cls_of(n)] for n, t in direct]
            d["effective_consumers"] = [[k, cls_of(V.key_parts(k)[0]), label(V.key_parts(k)[0])] for k in eff]
            d["reach4_n"] = len(V.reach4(G, [key]))
        else:
            srcs = sorted(set(V.key_parts(a)[0] for k, a, _i in G["in"].get(key, ()) if k == "wire"))
            d["direct_sources"] = [[n, cls_of(n)] for n in srcs]
            try:
                d["effective_sources"] = sorted(V.effective_sources(G, key))[:8]
            except Exception as e:  # noqa: BLE001
                d["effective_sources"] = "ERR " + str(e)[:80]
        out.append(d)
    return out


def node_report(u, why):
    found = u in objs or u in G["cls"]
    rep = {"uid": u, "why": why, "found": found, "class": cls_of(u), "owner": owners.get(str(u)), "label": label(u)}
    if found:
        faces = face_info(u)
        rep["faces"] = faces
        live = set()
        direct = set()
        for f in faces:
            for k in f.get("effective_consumers", []):
                live.add(k[0])
            for n in f.get("direct_sinks", []):
                direct.add((n[0], n[1]))
        rep["live_consumer_keys"] = sorted(live)
        rep["live_consumers_n"] = len(live)
        rep["direct_sinks_n"] = len(direct)
    return rep


# ---- candidates named by the plan
PAIRS = [(9018, 9025, "PD225(d) ring SRB1 old (split plan :1931)"), (29505, 29512, "PD225(d) ring SRB2 old (:1931)"),
         (1147, 1142, "old 1.2 carrier (:43)"), (5796, 5805, "old 1.2 carrier (:43)"),
         (119, 2972, "old 1.2 carrier, kernel-only (:43, PD177(b) :482-487)"), (7311, 11001, "old 1.2 carrier (:43, PD222(c) :1891)")]
cands = []
for r_, l_, why in PAIRS:
    for u in (r_, l_):
        rep = node_report(u, why)
        rep["pair"] = [r_, l_]
        rep["machine_pair_on_637"] = str(r_) in ((loops.get(637) or {}).get("left_of") or {})
        cands.append(rep)

# ---- every SR on loop #637 (what the table says is there now)
L637 = loops.get(637) or {}
sr637 = {"right_uids": L637.get("right_uids"), "left_of": L637.get("left_of")}
sr_method = G["method"].get("sr")

# ---- raw cross-check: every terminal row (before dedupe) on each candidate face's wire
raw_by_wire = collections.defaultdict(list)
for r in g["terminals"]:
    if r.get("wire_uid"):
        raw_by_wire[r["wire_uid"]].append((r["term_uid"], bool(r["is_source"]), r["owner_uid"], r["owner_class"]))
for c in cands:
    for f in c.get("faces", []):
        f["raw_wire_rows"] = sorted(set(raw_by_wire.get(f["wire"], []))) if f["wire"] else []
        print("RAW #{0} t{1} w{2}: {3}".format(c["uid"], f["term_uid"], f["wire"], f["raw_wire_rows"]))

# ---- S1 context: the same uids' effective consumers in S1 (D1_s1_copy wiki graph)
S1 = JC.load("D1_s1_copy")
for c in cands:
    s1 = []
    for key, r in S1["rows"].items():
        if r["node"] == c["uid"] and r["is_source"]:
            s1 += sorted(SS.effective_consumers(S1, key))
    c["s1_effective_consumers"] = sorted(set(s1))
    print("S1 #{0}: {1}".format(c["uid"], c["s1_effective_consumers"][:8]))

# ---- tunnels: every LoopTunnel, loop found from its INNER face's body diagram (639 = #637's body)
BODY = {639: 637, 23166: 10170, 23405: 23041}
tunnels = []
for u, o in sorted(objs.items()):
    if o.get("class") != "LoopTunnel":
        continue
    fds = sorted(set(int(r.get("frame_diagram") or 0) for r in G["rows"].values()
                     if r["node"] == u and r["term_class"] == "InnerTerminal"))
    own = owners.get(str(u))
    loop_u = BODY.get(fds[0]) if len(fds) == 1 and fds[0] in BODY else (own[1] if own else None)
    rep = node_report(u, "tunnel inner fd {0}".format(fds))
    rep["owner_loop"] = loop_u
    rep["inner_fd"] = fds
    srcs_ok = any(f["is_source"] for f in rep.get("faces", []))
    snk_fed = [f for f in rep.get("faces", []) if not f["is_source"]]
    rep["sink_faces_fed"] = sum(1 for f in snk_fed if f.get("direct_sources"))
    rep["n_source_faces"] = sum(1 for f in rep.get("faces", []) if f["is_source"])
    rep["n_faces"] = len(rep.get("faces", []))
    tunnels.append(rep)
by_loop = collections.Counter(t["owner_loop"] for t in tunnels)
t637 = [t for t in tunnels if t["owner_loop"] == 637]
zero637 = [t for t in t637 if t.get("live_consumers_n", 0) == 0]
zero_all = [t for t in tunnels if t.get("live_consumers_n", 0) == 0]
gate(all(c["found"] is not None for c in cands), "G1 every candidate looked up (found y/n recorded)")
gate(len(t637) > 0, "G2 LoopTunnels owned by #637 enumerated: {0}".format(len(t637)))

for c in cands:
    print("CAND #{0} {1} owner={2} found={3} live={4} direct={5} keys={6}".format(
        c["uid"], c["class"], c["owner"], c["found"], c.get("live_consumers_n"), c.get("direct_sinks_n"),
        c.get("live_consumer_keys", [])[:6]))
    for f in c.get("faces", []):
        print("   face t{0} '{1}' {2} src={3} w{4} fd={5} direct={6} eff={7} srcs={8}".format(
            f["term_uid"], f["name"], f["tclass"], f["is_source"], f["wire"], f["frame_diagram"],
            f.get("direct_sinks"), [k[0] for k in f.get("effective_consumers", [])][:6], f.get("direct_sources")))
print("SR637", json.dumps(sr637))
print("SRMETHOD", json.dumps(sr_method)[:600])
print("TUNNELS by loop", dict(by_loop))
for t in t637:
    print("T637 #{0} live={1} direct={2} faces={3}".format(t["uid"], t.get("live_consumers_n"), t.get("direct_sinks_n"),
          [(f["term_uid"], f["name"], f["tclass"], f["is_source"], f["wire"], f.get("direct_sinks"), f.get("direct_sources"))
           for f in t.get("faces", [])]))
for t in zero_all:
    print("ZERO-LIVE tunnel #{0} loop #{1} faces={2} src_faces={3} sink_faces_fed={4} faces={5}".format(
        t["uid"], t["owner_loop"], t["n_faces"], t["n_source_faces"], t["sink_faces_fed"],
        [(f["term_uid"], f["tclass"], f["is_source"], f["wire"], f.get("direct_sinks"), f.get("direct_sources"))
         for f in t.get("faces", [])]))

out = {"schema": "facts/c114e-inventory", "graph": {"path": "tools/bench/graph_l2b3_20260928.json", "md5": md5(GP)},
       "plan": {"path": "tools/bench/plan_l2b3.json", "md5": md5(PP)}, "cdiff_inputs": rec,
       "tools": {"effective_consumers": "tools/stagesim.py:376", "reach4": "tools/vigraph.py:675",
                 "effective_sources": "tools/vigraph.py:782", "graph": "tools/stagesim.py:364 (JC.from_parts -> vigraph.build4)"},
       "candidates": cands, "loop637_sr_table": sr637, "sr_method": sr_method,
       "tunnels_by_loop": {str(k): v for k, v in by_loop.items()},
       "tunnels_637": [{"uid": t["uid"], "live_consumers_n": t.get("live_consumers_n"), "direct_sinks_n": t.get("direct_sinks_n"),
                        "n_faces": t["n_faces"], "n_source_faces": t["n_source_faces"], "sink_faces_fed": t["sink_faces_fed"],
                        "live_consumer_keys": t.get("live_consumer_keys")} for t in t637],
       "zero_live_tunnels": [{"uid": t["uid"], "owner_loop": t["owner_loop"], "faces": t.get("faces")} for t in zero_all]}
op = os.path.join(B, "facts_c114e_inventory.json")
json.dump(out, open(op, "w", encoding="utf-8"), indent=1, default=str)
gate(os.path.exists(op), "G3 facts written " + op)
print(protocol.result_line(protocol.make_result(npass, nfail, first_fail,
                                                [{"path": "tools/bench/facts_c114e_inventory.json", "md5": md5(op)}])))
