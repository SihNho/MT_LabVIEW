r"""diag_m8b_frame_source - card 75-2. PURE PYTHON, no LabVIEW: the TRACKING frame source `#6810 get buff image-lost
frames.vi` (Image Out t6865) and the CALIBRATION frame path (`#22692` -> Sequence #22541 local t22656 -> t22659), S1 + S3.
PRIOR ART: walk/desc/creator/structure_of are EXEC'D VERBATIM from diag_m8b_grab_consumers.py (75-1, md5 b3012aa4..., its
module body before `m0 =` - nothing re-typed); graphs as 75-1 (JC.load S1, JC.from_parts S3); #6810 internals from
docs/wiki/subvi/get buff image-lost frames.json; SequenceLocal has no readable uid (docs/toolkit-capabilities.md:601), so
the local link is read NON-POSITIONALLY as NAME-UNIQUENESS over every Diagram-owned terminal of the sequence's frames.
PREDICTION: Q1 #6810 present once in each VI, 4 inputs wired (Session In, Image In, Buffer to extract, error in);
Q2 t6865 has >=1 non-relay consumer in each VI; Q3 wiki #6810 holds exactly one SubVI = IMAQdx Get Image;
Q4 sequence #22541: exactly one source + one sink Diagram terminal named 'Image Out' (name-unique link); Q5 S3 md5 fixed.
    MATERIAL=1 py tools/bgrun.py --max-min 5 --log tools/bench/m8b_frame_source_75.log -- py -u tools/bench/diag_m8b_frame_source.py"""
import os, json                                                                     # noqa: E401
_SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diag_m8b_grab_consumers.py")
exec(compile(open(_SRC, encoding="utf-8").read().split("\nm0 = md5(S3VI)")[0], _SRC, "exec"))  # 75-1 defs, verbatim
NODE, TOUT = 6810, 6865
def flat(cons, acc, via=()):
    """every non-relay consumer reached (incl. image-out downstream and sequence-local continuations), one row each."""
    for c in cons if isinstance(cons, list) else []:
        if not c.get("dead_end_relay"):
            acc.append({"via": list(via), "node": c["node"], "class": c["class"], "name": c["name"], "term_uid": c["term_uid"],
                        "term_name": c["term_name"], "diagram": c["diagram"], "wire_uid": c["wire_uid"],
                        "structs": [(s["diagram"], s["owner_class"], s["structure"]) for s in c["structure_chain"]]})
            flat(c.get("image_out_downstream"), acc, via + (c["node"],))
        for m in (c.get("unmodelled_relay") or {}).get("matches", []):
            flat(m.get("consumers"), acc, via + ("seqlocal t%d->t%d" % (c["term_uid"], m["term_uid"]),))
    return acc
def seq_link(G, sink_tu, st_uid):
    fr = [u for u, o in G["objs"].items() if o["class"] in V.DIAGRAM_OWNER and structure_of(G, u)["structure"] == st_uid]
    sk = V.terminals(G, term_uid=sink_tu)[0]; nm = G["rows"][sk]["term_name"]                       # noqa: E702
    rows = [dict(desc(G, k), is_source=bool(r["is_source"]), pos=G["pos"].get(r["term_uid"]))
            for k, r in G["rows"].items() if r["owner_class"] in V.DIAGRAM_OWNER and r["owner_uid"] in fr and r["term_name"] == nm]
    return {"structure": st_uid, "frames": sorted(fr), "name": nm, "rows": rows,
            "all_seq_diagram_terms": sorted((r["term_name"], bool(r["is_source"]), r["owner_uid"], r["term_uid"])
                                            for r in G["rows"].values() if r["owner_class"] in V.DIAGRAM_OWNER and r["owner_uid"] in fr)}
m0 = md5(S3VI)
W1, WB, S3 = J("docs/wiki/subvi/D1_s1_copy.json"), J("docs/wiki/subvi/{0}.json".format(JC.BED_KEY)), J("tools/bench/graph_s3_loop15_20260924.json")
WG = J("docs/wiki/subvi/get buff image-lost frames.json")
gate("Q5a S3 table is a read of the card's S3 md5", S3["md5"] == m0 == "1a11d92aacabf7ec844d65b8af19f39f", (S3["md5"], m0))
G1 = JC.load(JC.S1_KEY); add_fs_parents(G1, W1["fs_tunnel_pairs"])                   # noqa: E702
G3 = JC.from_parts({"terminals": S3["terminals"], "graph_summary": W1["graph_summary"]}, S3["objs"], J("tools/bench/graph_loops_m4b_20260924.json")["loops"], JC.node_labels_default(), WB["fs_tunnel_pairs"], "s3"); add_fs_parents(G3, WB["fs_tunnel_pairs"])  # noqa: E501,E702
calls = WG["graph_summary"]["subvi_calls"]
inner = {w["sink_term"]: (w["src_class"], w["src_uid"], w["src_term"]) for w in WG["wires"] if w["sink_uid"] == 529}
outer = {w["src_term"]: (w["sink_class"], w["sink_uid"], w["sink_term"]) for w in WG["wires"] if w["src_uid"] == 529}
gate("Q3 wiki #6810: one SubVI = IMAQdx Get Image", len(calls) == 1 and "IMAQdx Get Image" in calls[0]["subvi_name"], calls)
print("  FACT  #6810 internals: #529 {0} inputs {1} outputs {2} (docs/wiki/subvi/get buff image-lost frames.json:491-495)".format(
      calls[0]["subvi_name"], inner, outer), flush=True)
res = {"card": "75-2", "method": __doc__.split("PREDICTION")[0].strip(), "get_buff_internals": {"subvi_calls": calls,
       "into_get_image": inner, "from_get_image": outer, "connector_pane": WG["connector_pane"], "wiki_md5": WG["md5"]}, "vis": {}}
for tag, G in (("D1_s1_copy", G1), ("D1_s3_loop15", G3)):
    v = res["vis"][tag] = {}
    ins = V.terminals(G, node=NODE, is_source=False)
    wired = [k for k in ins if G["rows"][k]["wire_uid"]]
    gate("Q1 {0}: #6810 inputs wired = 4".format(tag), len(wired) == 4, [G["rows"][k]["term_name"] for k in wired])
    v["inputs"] = []
    for k in ins:
        d = desc(G, k); d["direct_src"] = [desc(G, s) for s in sorted(V.sources_of(G, k))]
        d["true_src"] = [desc(G, s) for s in sorted(V.sources_of(G, k, collapse=True))]; v["inputs"].append(d)   # noqa: E702
        print("  FACT  {0} #6810 in t{1} '{2}' w{3} d{4} <- {5}".format(tag, d["term_uid"], d["term_name"], d["wire_uid"], d["diagram"],
              [(s["node"], s["class"], s["name"], s["term_uid"], s["term_name"], s["diagram"]) for s in d["true_src"]]), flush=True)
    ks = V.terminals(G, term_uid=TOUT); v["image_out"] = desc(G, ks[0]) if ks else None
    cons = walk(G, ks[0]) if ks else []; v["consumers_tree"] = cons
    v["pixel_readers"] = fl = flat(cons, [])
    gate("Q2 {0}: t6865 reaches >=1 consumer".format(tag), len(fl) >= 1, len(fl))
    for c in fl:
        print("  FACT  {0} t6865 -> #{1} {2} {3} t{4} '{5}' w{6} d{7} via {8} structs {9}".format(tag, c["node"], c["class"], c["name"],
              c["term_uid"], c["term_name"], c["wire_uid"], c["diagram"], c["via"], c["structs"][:3]), flush=True)
    cal = walk(G, V.terminals(G, term_uid=22701)[0])
    sl = v["seq_local"] = seq_link(G, 22656, 22541)
    src = [r for r in sl["rows"] if r["is_source"]]; snk = [r for r in sl["rows"] if not r["is_source"]]
    gate("Q4 {0}: seq #22541 'Image Out' Diagram terminals = 1 src + 1 sink".format(tag), len(src) == 1 and len(snk) == 1,
         [(r["term_uid"], r["is_source"], r["diagram"], r["pos"]) for r in sl["rows"]])
    v["calibration_pixel_readers"] = cfl = flat(cal, [])
    for c in cfl:
        print("  FACT  {0} cal t22701 -> #{1} {2} t{3} '{4}' d{5} via {6}".format(tag, c["node"], c["name"], c["term_uid"],
              c["term_name"], c["diagram"], c["via"]), flush=True)
gate("Q5b S3 md5 unchanged at end", md5(S3VI) == m0, m0)
out = os.path.join(HERE, "m8b_frame_source_75.json"); json.dump(res, open(out, "w", encoding="utf-8"), indent=1, default=str)  # noqa: E702
print("  FACT  wrote {0} ({1:.1f} KB) md5 {2}".format(out, os.path.getsize(out) / 1024.0, md5(out)), flush=True)
nf = sum(1 for _l, ok in GATES if not ok)
print(P.result_line(P.make_result(len(GATES) - nf, nf, next((l for l, ok in GATES if not ok), None), [{"path": "tools/bench/m8b_frame_source_75.json", "md5": md5(out)}])), flush=True)  # noqa: E501
sys.exit(1 if nf else 0)
