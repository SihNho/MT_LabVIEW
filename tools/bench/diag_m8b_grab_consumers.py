r"""diag_m8b_grab_consumers - card 75-1 (B). PURE PYTHON, no LabVIEW: every downstream consumer of the camera image from
`#15403 IMAQdx Grab` t15412 and `#22692 IMAQdx Get Image` t22701, in S1 (`D1_s1_copy.vi`) and S3 (`D1_s3_loop15.vi`).
PRIOR ART: vigraph.build4 via jev_candidates.load/from_parts; S3 inputs as cdiff_blindspot_74.py:41-49 (S3 not in docs/wiki).
WALK: wire edges; scheduling relays (vigraph.transparent) walked THROUGH; first non-relay node = CONSUMER; wired '*image*' outputs
walked on (depth<=4); a relay with no onward edge (Diagram-owned sink = stacked-seq local) = DEAD-END, resolved by HEURISTIC
(same-structure Diagram terminals, same pos or name). Structure uid = nearest top-left object of the owner class (POSITIONAL).
PREDICTION: P1 both terminals in both VIs; P2 S1 t15412 reaches #15442 t15463 + LoopTunnel #15188 (m8 plan:90); P3 S3 md5 fixed.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/m8b_grab_consumers_75.log -- py -u tools/bench/diag_m8b_grab_consumers.py"""
import hashlib, json, os, sys                                                       # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, os.path.dirname(HERE))  # noqa: E702
import vigraph as V, jev_candidates as JC, protocol as P                            # noqa: E401,E402
J = lambda p: json.load(open(os.path.join(ROOT, p), encoding="utf-8"))             # noqa: E731
S3VI = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_s3_loop15.vi"
SRC = {15412: "#15403 IMAQdx Grab 'Image Out'", 22701: "#22692 IMAQdx Get Image 'Image Out'"}
GRAB, GATES = {15412: 15403, 22701: 22692}, []
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                       # noqa: E731
def gate(label, ok, detail=""):
    GATES.append((label, bool(ok))); print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:500]), flush=True)  # noqa: E702
def add_fs_parents(G, fs_pairs):
    fr = dict((r["term_uid"], int(r.get("frame_diagram") or 0)) for r in G["rows"].values())
    for p in fs_pairs or []:
        a, b = fr.get(p.get("term_a")), fr.get(p.get("term_b"))
        if p["class"] == V.FS_OUT and a and b and a != b:
            G["tree"]["parent"].setdefault(b, a)                                    # OuterTerminal frame = parent
def structure_of(G, d):
    o = G["objs"].get(d)
    if not o: return {"diagram": d, "owner_class": None, "structure": None}  # noqa: E701
    oc, (dx, dy) = o["owner"], o["pos"]; sc = "FlatSequence" if oc == "FlatSequenceFrame" else oc  # noqa: E702
    cand = [(abs(dx - s["pos"][0]) + abs(dy - s["pos"][1]), u) for u, s in G["objs"].items()
            if s["class"] == sc and s["pos"][0] <= dx and s["pos"][1] <= dy]
    st = min(cand)[1] if cand else None
    return {"diagram": d, "diagram_class": o["class"], "owner_class": oc, "structure": st,
            "structure_owner": G["objs"][st]["owner"] if st else None}
def chain(G, d):
    out = [structure_of(G, x) for x in JC._ancestors(G["tree"], d)] if d else []
    if out and out[-1].get("structure_owner") == "TopLevelDiagram":
        out.append(structure_of(G, next(u for u, o in G["objs"].items() if o["class"] == "TopLevelDiagram")))
    return out
def desc(G, key):
    r = G["rows"][key]; n = r["node"]; d = int(r.get("frame_diagram") or 0)       # noqa: E702
    return {"node": n, "class": G["cls"].get(n), "name": G["subvi_name"].get(n) or G["labels"].get(n) or None,
            "term_uid": r["term_uid"], "term_name": r["term_name"], "wire_uid": r["wire_uid"], "diagram": d,
            "structure_chain": chain(G, d)}
def seq_local(G, key, depth, seen):
    r = G["rows"][key]; st = structure_of(G, int(r.get("frame_diagram") or 0)); p = G["pos"].get(r["term_uid"])  # noqa: E702
    frames = [u for u, o in G["objs"].items() if o["class"] in V.DIAGRAM_OWNER and structure_of(G, u)["structure"] == st["structure"]]
    out = {"structure": st, "frames": sorted(frames), "sink_pos": p, "rule": "HEURISTIC same structure, Diagram-owned, same pos or name", "matches": []}
    for k2, r2 in G["rows"].items():
        if k2 != key and r2["owner_class"] in V.DIAGRAM_OWNER and r2["owner_uid"] in frames and \
                (G["pos"].get(r2["term_uid"]) == p or r2["term_name"] == r["term_name"]):
            m = dict(desc(G, k2), is_source=bool(r2["is_source"]), pos=G["pos"].get(r2["term_uid"]))
            if r2["is_source"] and depth < 4:
                m["consumers"] = walk(G, k2, depth + 1, seen)
            out["matches"].append(m)
    return out
def walk(G, src_key, depth=0, seen=None):
    seen = seen if seen is not None else set()
    out, stack = [], [(src_key, [])]
    while stack:
        cur, hops = stack.pop()
        for kind, nxt, _info in sorted(G["out"].get(cur, ()), key=lambda e: (e[0], e[1])):
            if kind == "thru" or (kind, cur, nxt) in seen:
                continue
            seen.add((kind, cur, nxt))
            if V.transparent(G, nxt) and not G["out"].get(nxt):
                out.append(dict(desc(G, nxt), edge=kind, relays=hops, dead_end_relay=True,
                                unmodelled_relay=seq_local(G, nxt, depth, seen)))
            elif V.transparent(G, nxt):
                h = hops + [dict(desc(G, nxt), edge=kind)]
                for k2, n2, _i in G["out"].get(nxt, ()):                            # relay: its other face
                    if k2 == "thru" and (k2, nxt, n2) not in seen:
                        seen.add((k2, nxt, n2)); stack.append((n2, h + [dict(desc(G, n2), edge="thru")]))  # noqa: E702
                stack.append((nxt, h))
            else:
                c = dict(desc(G, nxt), edge=kind, relays=hops)
                img = [k for k in V.terminals(G, node=c["node"], is_source=True)
                       if "image" in G["rows"][k]["term_name"].lower() and G["rows"][k]["wire_uid"]]
                c["image_out_terms"] = [G["rows"][k]["term_uid"] for k in img]
                c["image_out_downstream"] = [x for k in img for x in walk(G, k, depth + 1, seen)] if depth < 4 else "depth-cap"
                out.append(c)
    return out
def creator(G, grab):
    return [{"grab_input": desc(G, k), "creator": desc(G, s), "ref_receivers": walk(G, s)}
            for k in V.terminals(G, node=grab, is_source=False) if "image" in G["rows"][k]["term_name"].lower()
            for s in sorted(V.sources_of(G, k, collapse=True))]
def hop(h): return "{0}:#{1}{2} t{3} '{4}' w{5} d{6}".format(h["edge"], h["node"], h["class"], h["term_uid"], h["term_name"], h["wire_uid"], h["diagram"])

m0 = md5(S3VI)
W1, WB, S3 = J("docs/wiki/subvi/D1_s1_copy.json"), J("docs/wiki/subvi/{0}.json".format(JC.BED_KEY)), J("tools/bench/graph_s3_loop15_20260924.json")
gate("P3a S3 table is a read of the card's S3 md5", S3["md5"] == m0 == "1a11d92aacabf7ec844d65b8af19f39f", (S3["md5"], m0))
G1 = JC.load(JC.S1_KEY); add_fs_parents(G1, W1["fs_tunnel_pairs"])                   # noqa: E702
G3 = JC.from_parts({"terminals": S3["terminals"], "graph_summary": W1["graph_summary"]}, S3["objs"], J("tools/bench/graph_loops_m4b_20260924.json")["loops"], JC.node_labels_default(), WB["fs_tunnel_pairs"], "s3"); add_fs_parents(G3, WB["fs_tunnel_pairs"])  # noqa: E501,E702
res = {"card": "75-1", "method": __doc__.split("WALK:")[1].split("PREDICTION")[0].strip(), "vis": {}}
for tag, G in (("D1_s1_copy", G1), ("D1_s3_loop15", G3)):
    v = res["vis"][tag] = {"source": "docs/wiki/subvi/D1_s1_copy.json" if G is G1 else "tools/bench/graph_s3_loop15_20260924.json (not in docs/wiki)", "sources": {}}  # noqa: E501
    for tu, lab in SRC.items():
        ks = V.terminals(G, term_uid=tu); gate("P1 {0}: {1} present".format(tag, lab), len(ks) == 1, ks)  # noqa: E702
        cons = walk(G, ks[0])
        v["sources"][str(tu)] = {"label": lab, "source": desc(G, ks[0]), "consumers": cons, "creator": creator(G, GRAB[tu])}
        for c in cons:
            print("  FACT  {0} t{1} -> #{2} {3} t{4}{5} | chain {6} | structs {7}".format(tag, tu, c["node"], c["name"], c["term_uid"],
                  " DEAD-END" if c.get("dead_end_relay") else "", " > ".join(hop(h) for h in c["relays"] + [c]),
                  [(s["diagram"], s["owner_class"], s["structure"]) for s in c["structure_chain"]]), flush=True)
            for m in (c.get("unmodelled_relay") or {}).get("matches", []):
                print("  FACT  {0}   dead-end -> Diagram terminal t{1} '{2}' src={3} d{4}: {5}".format(tag, m["term_uid"], m["term_name"],
                      m["is_source"], m["diagram"], [(x["node"], x["name"], x["term_name"], x["diagram"]) for x in m.get("consumers", [])]), flush=True)
        for cr in v["sources"][str(tu)]["creator"]:
            print("  FACT  {0} grab #{1} '{2}' <- creator #{3} {4} t{5}; ref receivers {6}".format(tag, GRAB[tu], cr["grab_input"]["term_name"],
                  cr["creator"]["node"], cr["creator"]["name"], cr["creator"]["term_uid"],
                  [(x["node"], x["class"], x["name"], x["term_name"]) for x in cr["ref_receivers"]]), flush=True)
s1c = res["vis"]["D1_s1_copy"]["sources"].get("15412", {}).get("consumers", [])
hit = set((c["node"], c["term_uid"]) for c in s1c) | set(h["node"] for c in s1c for h in c["relays"])
gate("P2 S1 t15412 reaches #15442 t15463 and LoopTunnel #15188", (15442, 15463) in hit and 15188 in hit, sorted(hit, key=str)[:12])
gate("P3b S3 md5 unchanged at end", md5(S3VI) == m0, m0)
out = os.path.join(HERE, "m8b_grab_consumers_75.json"); json.dump(res, open(out, "w", encoding="utf-8"), indent=1)  # noqa: E702
print("  FACT  wrote {0} ({1:.1f} KB) md5 {2}".format(out, os.path.getsize(out) / 1024.0, md5(out)), flush=True)
nf = sum(1 for _l, ok in GATES if not ok)
print(P.result_line(P.make_result(len(GATES) - nf, nf, next((l for l, ok in GATES if not ok), None), [{"path": "tools/bench/m8b_grab_consumers_75.json", "md5": md5(out)}])), flush=True)  # noqa: E501
sys.exit(1 if nf else 0)
