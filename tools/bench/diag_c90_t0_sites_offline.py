r"""diag_c90_t0_sites_offline - card 90-4 B: the stamp-site table for PD196(d) step 3, READ OFFLINE from the S1 wiki.

FOUND FIRST: docs/wiki/subvi/D1_s1_copy.json (5748 terminal rows with owner_uid/frame_diagram/wire_uid, 1899 wires with
src/sink uids, graph_summary.subvi_calls = 97 call sites with diagram INDEX), tools/bench/graph_objs_s1_20260923.json
(9981 GObjects: diagram uid -> class/owner class), graph_loops_s1_20260924.json (loop uid -> shift registers),
jev_candidates.load('D1_s1_copy') (vigraph.build4 + diagram_tree: diagram parent chain from tunnel inner/outer frames),
result_89-1.json (the 11 group uids). vigraph.py:231: a loop's iteration terminal `i` is a DIAGRAM-owned source row
(S1 #644 on diagram #639 feeding w3268). No LabVIEW is touched here; the placement check is diag_c90_t0_place.py.

PREDICTION CONTRACT: P1 every group name resolves to >=1 call site; P2 every site has a frame_diagram and a parent chain
ending at the top-level diagram #536; P3 the frame loop #637's body #639 carries exactly one diagram-owned source `i`
(#644); P4 each of the 3 While loops resolves to one body diagram; P5 rows == sites (one per call site).
Output: tools/bench/t0_sites_s1.json. RESULT line last (C6).
"""
import collections, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402
import jev_candidates as JC  # noqa: E402

OUT = os.path.join(HERE, "t0_sites_s1.json")
GROUPS = [("kernel", "Track N beads four-fold over-kernel-v3.vi"), ("ImageToArray", "IMAQ ImageToArray"),
          ("display", "Flatten Pixmap.vi"), ("display", "Draw Flattened Pixmap.vi"), ("display", "grayscale color table.vi"),
          ("display", "rect coord from center.vi"), ("display", "Draw Grayed Out Rect.vi"), ("display", "Draw Circle by Radius.vi"),
          ("display", "Draw Text at Point.vi"), ("plot Z", "N bead plot Z.vi"), ("plot dZ", "N bead plot dZ.vi"),
          ("save trace", "save trace.vi"), ("save xyz", "save N xyz traces.vi"), ("check N bead pos", "check N bead pos v3-kimlab.vi"),
          ("Median", "Median Filter.vi"), ("FIR", "FIR Filter (DBL).vi")]
P, F, facts = [], [], []


def gate(label, ok, detail=""):
    (P if ok else F).append(label); print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, detail), flush=True)


G = JC.load(JC.S1_KEY)
rec = G["wiki"]; objs = G["objs"]; rows = G["rows"]; by_node = G["by_node"]; tree = G["tree"]
diag_objs = [o for o in json.load(open(JC._newest("graph_objs_s1_*.json"), encoding="utf-8"))["objects"] if o["class"] in ("Diagram", "TopLevelDiagram")]
diag_index = {int(o["uid"]): i for i, o in enumerate(diag_objs)}          # report_all('Diagram') traverse order
loops = json.load(open(JC._newest("graph_loops_s1_*.json"), encoding="utf-8"))["loops"]
wires = {int(w["wire_uid"]): w for w in rec["wires"]}
calls = rec["graph_summary"]["subvi_calls"]
# --- diagram -> owning structure uid: tunnel rows (LoopTunnel/SR/SelectorTunnel/Tunnel/FS) have owner_uid = tunnel uid; the
# STRUCTURE uid is known only for loops with shift registers (graph_loops right_uids) -> body diagram via the SR inner frame.
body_of_loop, loop_of_body = {}, {}
for L in loops:
    for r_uid in L["right_uids"]:
        for r in by_node.get(int(r_uid), ()):
            if r["term_class"] == "InnerTerminal" and r.get("frame_diagram"):
                body_of_loop[L["loop_uid"]] = int(r["frame_diagram"]); loop_of_body[int(r["frame_diagram"])] = (L["class"], L["loop_uid"])
# diagram-owned source rows = iteration terminals `i` (vigraph.py:231)
i_terms = collections.defaultdict(list)
for r in rec["terminals"]:
    # FP control terminals ALSO read as diagram-owned sources (named); the loop's `i` is the UNNAMED one (S1 #644, name '')
    if r["owner_class"] == "Diagram" and r["is_source"] and r["term_name"] == "":
        d = int(r["frame_diagram"] or r["owner_uid"])
        if r["term_uid"] not in [t["term_uid"] for t in i_terms[d]]:
            i_terms[d].append({"term_uid": r["term_uid"], "name": r["term_name"], "wire_uid": r["wire_uid"], "owner_uid": r["owner_uid"]})
whiles = [L for L in loops if L["class"] == "WhileLoop"]
loop_rows = []
for L in whiles:
    body = body_of_loop.get(L["loop_uid"])
    loop_rows.append({"loop_uid": L["loop_uid"], "body_diagram": body, "body_index": diag_index.get(body), "i_terminals": i_terms.get(body, [])})
    facts.append("WhileLoop #%d body #%s (index %s) i-terminals %r" % (L["loop_uid"], body, diag_index.get(body), i_terms.get(body, [])))
gate("P4 each of the 3 While loops resolves to one body diagram", len(whiles) == 3 and all(x["body_diagram"] for x in loop_rows), repr([(x["loop_uid"], x["body_diagram"]) for x in loop_rows]))
gate("P3 frame loop #637 body #639 has exactly one `i` (#644)", [t["term_uid"] for t in i_terms.get(639, [])] == [644], repr(i_terms.get(639)))


def chain(d):
    out = []
    for a in JC._ancestors(tree, d):
        o = objs.get(a, {}); lc = loop_of_body.get(a)
        out.append({"diagram": a, "index": diag_index.get(a), "owner_class": o.get("owner", "?"), "loop": lc[1] if lc else None})
    return out


sites = []
for gname, vi in GROUPS:
    hits = [c for c in calls if c["subvi_name"].endswith(vi)]
    gate("P1 %s -> %s resolves" % (gname, vi), bool(hits), repr([h["node_uid"] for h in hits]))
    for c in hits:
        u = int(c["node_uid"]); rs = by_node.get(u, [])
        fd = next((int(r["frame_diagram"]) for r in rs if r.get("frame_diagram")), 0)
        ch = chain(fd) if fd else []
        outs = [r for r in rs if r["is_source"]]; wired = [r for r in outs if r["wire_uid"]]
        ins = [r for r in rs if not r["is_source"] and r["wire_uid"]]
        err_out = next((r for r in wired if r["term_name"].startswith("error out")), None)
        pick = err_out or (wired[0] if wired else None)
        # REVIEW archive/peer/2026-09-26-c90-sites-p2-treegap.md (accepted): the holding loop is the innermost WHILE-loop
        # body in the chain (objs owner == 'WhileLoop'), never "the innermost loop that has a shift register" (run 1 gave
        # #16788/#16827 For loop #16557 and missed case frame #16303). Inner For loops are reported separately.
        holding = next((x for x in ch if x["owner_class"] == "WhileLoop"), None)
        inner_for = [x["diagram"] for x in ch if x["owner_class"] == "ForLoop" and (not holding or ch.index(x) < ch.index(holding))]
        cond = [x for x in ch[:-1] if x["owner_class"] in ("CaseStructure", "EventStructure")]
        cond_below_loop = [x for x in cond if holding and ch.index(x) < ch.index(holding)]
        alt = None
        if not pick and ins:
            w = ins[-1]; alt = {"kind": "last wired INPUT (completion cannot be stamped; only readiness of this input)", "term": w["term_name"], "wire_uid": w["wire_uid"], "n_sink": wires.get(w["wire_uid"], {}).get("n_sink")}
        row = {"group": gname, "node_uid": u, "vi": c["subvi_name"], "diagram": fd, "diagram_index": diag_index.get(fd), "chain": ch,
               "holding_loop": holding["loop"] if holding else None, "holding_loop_body": holding["diagram"] if holding else None,
               "inner_for_loop_bodies": inner_for,
               "case_frames_between_node_and_loop": [x["diagram"] for x in cond_below_loop],
               "runs_every_iteration": (holding is not None and not cond_below_loop),
               "loop_proven_by_tree": holding is not None or (ch and ch[-1]["diagram"] == 536),
               "n_outputs": len(outs), "n_outputs_wired": len(wired),
               "stamp_terminal": ({"term": pick["term_name"], "term_uid": pick["term_uid"], "wire_uid": pick["wire_uid"], "n_sink": wires.get(pick["wire_uid"], {}).get("n_sink")} if pick else None),
               "alternative": alt, "status": "OK" if pick else ("ALT-INPUT" if alt else "UNADDRESSABLE: no wired terminal at all")}
        sites.append(row)
        facts.append("#%d %s D#%s(idx %s) while %s inner-for %r every-iter %s case-frames %r proven %s out %s" % (u, c["subvi_name"], fd, diag_index.get(fd), row["holding_loop"], inner_for, row["runs_every_iteration"], row["case_frames_between_node_and_loop"], row["loop_proven_by_tree"], row["stamp_terminal"] or alt))
        print("  ROW  " + facts[-1], flush=True)
# jev_candidates.diagram_tree is built from LoopTunnel/Tunnel/SelectorTunnel/SR inner-outer frames ONLY (TREE_OWNERS), so a
# chain stops at a Sequence / FlatSequenceFrame diagram: run 1 measured every chain ending at #686 / #15041 / #3121, not #536.
# Accepted end = #536 or a diagram owned by a sequence structure (reported per row as `chain_end_owner`).
SEQ_OWNERS = ("Sequence", "FlatSequenceFrame", "FlatSequence")
for s in sites:
    end = s["chain"][-1]["diagram"] if s["chain"] else None
    s["chain_end_owner"] = objs.get(end, {}).get("owner", "?") if end else None
bad_chain = [(s["node_uid"], [x["diagram"] for x in s["chain"]], s["chain_end_owner"]) for s in sites
             if not (s["diagram"] and s["chain"] and (s["chain"][-1]["diagram"] == 536 or s["chain_end_owner"] in SEQ_OWNERS))]
gate("P2 every site has a frame diagram and a chain ending at #536 or at a sequence frame (tree gap)", not bad_chain, repr(bad_chain))
facts.append("chain ends: %r" % sorted(set((s["chain"][-1]["diagram"], s["chain_end_owner"]) for s in sites if s["chain"])))
print("  FACT  " + facts[-1])
unproven = [(s["node_uid"], s["chain"][-1]["diagram"]) for s in sites if not s["loop_proven_by_tree"]]
facts.append("rows whose holding loop the tunnel-tree cannot prove (chain stops at a sequence frame with no While body above): %r" % unproven)
print("  FACT  " + facts[-1])
# REVIEW archive/peer/2026-09-26-c90-place-oc2-ownerchain.md (accepted): the owner-chain op stops at a FlatSequenceFrame with
# 1055 (MEASURED LIMIT, docs/toolkit-capabilities.md:65), and the sequence bridge was ALREADY DERIVED offline on 2026-09-24 -
# tools/bench/p1_c70_f3a.log:44-60: the two TOP-LEVEL flat sequences' frame groups, parent [536], 167 edges / 0 contradictions.
F3A_TOP_FRAMES = {"FS#681": [113, 124, 686, 759, 1817, 3121, 3628, 4866, 5031, 81548],
                  "FS#12938": [12960, 13236, 14840, 15041, 19687, 19887, 20261, 21134, 25769, 26117]}
for s in sites:
    end = s["chain"][-1]["diagram"] if s["chain"] else None
    fs = next((k for k, v in F3A_TOP_FRAMES.items() if end in v), None)
    s["chain_end_is_top_level_frame_of"] = fs
    s["loop_proven_by"] = "tunnel-tree" if s["loop_proven_by_tree"] else ("f3a-derived: %s frame -> #536, no While above (p1_c70_f3a.log:44-60)" % fs if fs else "UNPROVEN")
gate("P7 every chain end is #536 or a frame of a top-level flat sequence (f3a groups) -> no unproven holding loop",
     all(s["loop_proven_by"] != "UNPROVEN" for s in sites), repr([(s["node_uid"], s["loop_proven_by"]) for s in sites if not s["loop_proven_by_tree"]]))
gate("P6 the two loop-C draw sites #16788/#16827 carry case frame #16303 and every-iter False (review falsifier)",
     all(s["case_frames_between_node_and_loop"] == [16303] and not s["runs_every_iteration"] for s in sites if s["node_uid"] in (16788, 16827)))
gate("P5 rows == call sites", len(sites) == sum(1 for gname, vi in GROUPS for c in calls if c["subvi_name"].endswith(vi)))
json.dump({"input": rec["file"], "input_md5": rec["md5"], "source": "docs/wiki/subvi/D1_s1_copy.json (offline)", "while_loops": loop_rows,
           "sites": sites, "placement_check": "see diag_c90_t0_place.py / t0_sites_s1_place.json", "facts": facts, "gates": {"pass": P, "fail": F}},
          open(OUT, "w", encoding="utf-8"), indent=1)
print("=== GATES: %d pass / %d fail%s" % (len(P), len(F), ("; failing: " + ", ".join(F)) if F else ""))
print(protocol.result_line(protocol.make_result(len(P), len(F), F[0] if F else None, [{"path": OUT}])))
sys.exit(0 if not F else 1)
