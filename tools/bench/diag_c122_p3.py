r"""diag_c122_p3 - card 122-2 (PD240(f)): ring P3 FACT SHEET, OFFLINE (no LabVIEW, no COM, no gscript/stagekit import - stagekit
imports gscript; precedent diag_c120_facts.py, which used protocol only). Reads graph_qrt_pool_20260928.json (pool bed) + the P2a
simulated end state sim/ring_p2a/step_08_delete_object.json (only to show the P2a-removed uids gone) and writes facts_c122_p3.json.
Prior art found: diag_c120_facts.py (back(), chain(), FSP) - reused here, plus a forward trace; facts_c120_qrtw.json G2/G3/G4.
PREDICTION: loop 1.1 = WhileLoop #637 / diagram #639 / i t644; #6810 BufNum = 'current image number' t6897 with >=1 sink on 639;
Image Out t6865 0 sinks; Image In t6857 traced back to IMAQ Create #13938 ('Cam', FS2 frame 13236) through tunnels + Property #35869;
#30117/#4580/i sources on 639; IMAQ Create #23099 'New Image' unwired after P2a; the 5 P2a uids absent from step_08.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c122_p3.log -- py -u tools/bench/diag_c122_p3.py"""
import json, os, sys                                                               # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))   # noqa: E702
import protocol                                                                     # noqa: E402
GF = "graph_qrt_pool_20260928.json"
G = json.load(open(os.path.join(HERE, GF), encoding="utf-8"))
S8 = json.load(open(os.path.join(HERE, "sim", "ring_p2a", "step_08_delete_object.json"), encoding="utf-8"))
T, OW, P, F = G["terminals"], G["owners"], [0, 0], {"source_graph": GF, "graph_md5": G.get("md5")}
OBJ = dict((int(o["uid"]), o) for o in G["objs"])
FSP = dict([(int(p["term_b"]), int(p["wire_a"] or 0)) for p in G["fs_tunnel_pairs"]] + [(int(p["term_a"]), int(p["wire_b"] or 0)) for p in G["fs_tunnel_pairs"]])
EXCL = [23105, 23118, 23136, 26017, 25898]
rows_of = lambda u: [r for r in T if int(r["owner_uid"]) == int(u)]                 # noqa: E731
term = lambda t: next((r for r in T if int(r["term_uid"]) == int(t)), None)       # noqa: E731
on_wire = lambda w: [r for r in T if w and int(r["wire_uid"] or 0) == int(w)]     # noqa: E731
K = lambda t: "{0}:terminals[term_uid={1}]".format(GF, t)                           # noqa: E731


def B(r):
    d = {k: r[k] for k in ("term_uid", "term_name", "is_source", "wire_uid", "owner_uid", "owner_class", "frame_diagram")}
    d["src"] = K(r["term_uid"]); return d                                           # noqa: E702


def gate(label, ok, detail=""):
    P[0 if ok else 1] += 1
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:600]), flush=True)


def chain(d):
    out, d = [], int(d)
    while d and str(d) in OW and len(out) < 30:
        out.append([d, OW[str(d)][0], int(OW[str(d)][1] or 0)]); d = out[-1][2]                  # noqa: E702
    return out


def back(t, n=0):
    """sink terminal -> hops [owner, class, frame_diagram, wire, src term] through tunnels to its first non-tunnel source."""
    hops, r = [], term(t)
    while r and n < 25:
        n += 1
        src = [x for x in on_wire(r["wire_uid"]) if x["is_source"]]
        if not src:
            hops.append(["NO SOURCE on w{0}".format(r["wire_uid"])]); break                  # noqa: E702
        x = src[0]; hops.append([int(x["owner_uid"]), x["owner_class"], x["frame_diagram"], int(r["wire_uid"] or 0), int(x["term_uid"])])   # noqa: E702
        if not x["owner_class"].endswith("Tunnel"):
            break
        w = FSP.get(int(x["term_uid"])) if x["owner_class"] == "FlatSequenceInnerTunnel" else None
        w = w or next((int(y["wire_uid"] or 0) for y in rows_of(x["owner_uid"]) if not y["is_source"] and y["wire_uid"]), 0)
        r = {"wire_uid": w} if w else hops.append(["tunnel #{0}: no wired input face".format(x["owner_uid"])])
    return hops


def fwd(t, path=(), seen=None, depth=0):
    """source terminal -> every END sink (non-tunnel owner), each with the tunnel hops [owner, class, frame_diagram, wire]."""
    seen, r, out = seen if seen is not None else set(), term(t), []
    if not r or not r["wire_uid"] or depth > 25:
        return out
    for x in on_wire(r["wire_uid"]):
        if x["is_source"] or int(x["term_uid"]) in seen:
            continue
        seen.add(int(x["term_uid"])); hop = path + ([int(x["owner_uid"]), x["owner_class"], x["frame_diagram"], int(r["wire_uid"])],)   # noqa: E702
        if x["owner_class"].endswith("Tunnel"):
            nxt = [y for y in rows_of(x["owner_uid"]) if y["is_source"] and y["wire_uid"]]
            w = FSP.get(int(x["term_uid"])) if x["owner_class"] == "FlatSequenceInnerTunnel" else None
            nxt += [y for y in on_wire(w) if y["is_source"]] if w else []
            for y in nxt:
                out += fwd(y["term_uid"], hop, seen, depth + 1)
            if not nxt:
                out.append({"end": B(x), "hops": list(hop), "note": "tunnel with no wired output face"})
        else:
            out.append({"end": B(x), "hops": list(hop)})
    return out


# 1 loop 1.1
F["loop_1_1"] = {"while_uid": 637, "diagram_uid": 639, "i_term": B(term(644)), "owners_639": OW.get("639"), "owners_637": OW.get("637"),
                 "chain_639": chain(639), "obj_637": OBJ.get(637), "src": GF + ":owners[639],owners[637],objs#637"}
srs = sorted(set((int(r["owner_uid"]), r["owner_class"]) for r in T if "ShiftRegister" in r["owner_class"] and int(r["frame_diagram"] or 0) in (639, 686)
                 and str(OW.get(str(r["owner_uid"]), [None, 0])[1]) == "637"))
F["loop_1_1"]["shift_registers"] = [[u, c, [B(x) for x in rows_of(u)]] for u, c in srs]
gate("L1 loop 1.1 = WhileLoop #637, diagram #639 owned by it, i t644 on 639", OW.get("639") == ["WhileLoop", 637] and (OBJ.get(637) or {}).get("class") == "WhileLoop"
     and term(644) and int(term(644)["frame_diagram"]) == 639, [OW.get("639"), OW.get("637"), F["loop_1_1"]["i_term"]])
# 2 #6810
F["n6810"] = {"terms": [B(r) for r in rows_of(6810)], "bufnum_name_cite": "docs/NAMES.md:86 ('current image number' = camera buffer number)"}
nm = dict((r["term_name"], r) for r in rows_of(6810) if r["term_name"])
for key, nmx in (("bufnum_out", "current image number"), ("image_out", "Image Out"), ("error_out", "error out"), ("missed_out", "Missed frames?")):
    F["n6810"][key] = {"term": B(nm[nmx]), "sinks": fwd(nm[nmx]["term_uid"])}
for key, nmx in (("image_in", "Image In"), ("error_in", "error in"), ("buffer_to_extract", "Buffer to extract"), ("session_in", "Session In")):
    F["n6810"][key] = {"term": B(nm[nmx]), "back": back(nm[nmx]["term_uid"])}
tip = F["n6810"]["image_in"]["back"][-1]
F["n6810"]["image_in_tip_rows"] = [B(r) for r in rows_of(tip[0])] if isinstance(tip[0], int) else []
F["cam_13938_new_image_fwd"] = fwd(next(r["term_uid"] for r in rows_of(13938) if r["term_name"] == "New Image"))
gate("N1 BufNum t6897 has >=1 sink, Image Out t6865 has 0", F["n6810"]["bufnum_out"]["sinks"] and not F["n6810"]["image_out"]["sinks"],
     [(s["end"]["owner_uid"], s["end"]["owner_class"], s["end"]["term_name"], s["end"]["frame_diagram"]) for s in F["n6810"]["bufnum_out"]["sinks"]])
gate("N2 Image In back-trace ends at a non-tunnel node; IMAQ Create #13938 'Cam' forward reaches it", isinstance(tip[0], int)
     and any(int(s["end"]["owner_uid"]) == tip[0] for s in F["cam_13938_new_image_fwd"]), [tip, F["n6810"]["image_in_tip_rows"]])
print("  FACT  error in back:", F["n6810"]["error_in"]["back"], "| error out sinks:", [(s["end"]["owner_uid"], s["end"]["owner_class"], s["end"]["term_name"],
      s["end"]["frame_diagram"]) for s in F["n6810"]["error_out"]["sinks"]], flush=True)
# 3 field sources
F["fields"] = {}
for f, u, tu in (("trans_pos", 30117, 30145), ("rot_pos", 4580, 4728), ("frame_i", 637, 644)):
    F["fields"][f] = {"node": u, "term": B(term(tu)), "obj": OBJ.get(u), "chain": chain(term(tu)["frame_diagram"]), "sinks": fwd(tu),
                      "inputs": [B(r) for r in rows_of(u) if not r["is_source"]] if u != 637 else []}
gate("F1 #30117/#4580 Value and i sources sit on 1.1's diagram 639", all(int(F["fields"][k]["term"]["frame_diagram"]) == 639 for k in F["fields"]),
     [(k, F["fields"][k]["term"]["frame_diagram"], len(F["fields"][k]["sinks"])) for k in F["fields"]])
# 4 the 20 pool images
fl = OW.get("23169"); F["pool"] = {"imaq_create": 23099, "for_body": 23169, "for_owner": fl, "for_chain": chain(23169), "create_rows": [B(r) for r in rows_of(23099)],
                                   "for_tunnels": [[u, [B(x) for x in rows_of(u)]] for u in sorted(set(int(r["owner_uid"]) for r in T
                                                   if r["owner_class"] == "LoopTunnel" and str(OW.get(str(r["owner_uid"]), [0, 0])[1]) == str((fl or [0, 0])[1])))]}
F["pool"]["new_image_wire_in_pool_graph"] = next((r["wire_uid"] for r in rows_of(23099) if r["term_name"] == "New Image"), None)
F["pool"]["target_chain_639"] = chain(639)
F["pool"]["measured_nested_route"] = {"cite": "tools/bench/opmodels/connect_across_fs.json (n=1, src #23118 t25591 on 13236 -> sink t26300 on 639)",
                                      "new": [[26262, "Invoke(stray)", 639], [26507, "LoopTunnel", "WhileLoop 637"], [26549, "FlatSequenceOuterTunnel", "FlatSequence 681"],
                                              [26775, "FlatSequenceOuterTunnel", "FlatSequence 12938"]], "hops": 4, "rule": "PD237(m): census == plan, stray Invoke removed in-recipe"}
gate("P1 IMAQ Create #23099 inside the For body 23169 on FS2 frame 13236", (fl or [None])[0] == "ForLoop" and any(c[0] == 13236 for c in chain(23169)), [fl, chain(23169)])
# 5 P2a exclusions
def all_terms(o):
    if isinstance(o, dict):
        return o["terminals"] if isinstance(o.get("terminals"), list) else next((x for v in o.values() for x in [all_terms(v)] if x), None)
    return None
T8 = all_terms(S8) or []
F["excluded_p2a"] = [{"uid": u, "in_pool_graph": bool(rows_of(u)) or u in OBJ, "in_p2a_sim_step08": any(int(r["owner_uid"]) == u for r in T8)} for u in EXCL]
used = json.dumps([F["loop_1_1"], F["n6810"], F["fields"], F["cam_13938_new_image_fwd"]])
gate("X1 the 5 P2a uids are absent from the P2a sim end state and from every bound fact", T8 and not any(x["in_p2a_sim_step08"] for x in F["excluded_p2a"])
     and not any('"owner_uid": {0}'.format(u) in used for u in EXCL), [F["excluded_p2a"], len(T8)])
out = os.path.join(HERE, "facts_c122_p3.json"); json.dump(F, open(out, "w", encoding="utf-8"), indent=1, default=str)   # noqa: E702
print("  FACT  wrote {0}".format(out), flush=True)
print(protocol.result_line(protocol.make_result(P[0], P[1], None if not P[1] else "see FAIL lines", [])), flush=True)
sys.exit(1 if P[1] else 0)
