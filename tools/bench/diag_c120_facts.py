r"""diag_c120_facts - card 120-1 G2-G7 OFFLINE half (no LabVIEW, no gscript import): reads graph_qrt_pool_20260928.json (written by
diag_c120_g.py) + graph_l2r2_saved_20260928.json (R2) + graph_l2r1_saved_20260928.json (the draft's base) + diag_c120_g.json (callees)
and writes tools/bench/facts_c120_qrtw.json. Prior art: diag_c117d_rows.py (owner lookups on a graph file), stagexec.tunnel_owner.
PREDICTION: G2 pool = 2 Obtain Queue + 1 ForLoop + 1 IMAQ Create + 1 Enqueue, all NEW vs R2, Obtains on one diagram; G3 #6810 and
#5058 have rows; G4 six field source rows (type = 'NO READER'); G5 #11261/#2626 rows; G7 every draft uid present; G6 = static grep table.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c120_facts.log -- py -u tools/bench/diag_c120_facts.py"""
import json, os, sys                                                               # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))   # noqa: E702
import protocol                                                                     # noqa: E402
L = lambda n: json.load(open(os.path.join(HERE, n), encoding="utf-8"))            # noqa: E731
G, R2, R1, CAL, DR = (L("graph_qrt_pool_20260928.json"), L("graph_l2r2_saved_20260928.json"), L("graph_l2r1_saved_20260928.json"),
                      L("diag_c120_g.json"), L("qrtw_rows_draft.json"))
T, OW, P, F = G["terminals"], G["owners"], [0, 0], {}
OBJ = dict((int(o["uid"]), o) for o in G["objs"])
old = set(int(r["owner_uid"]) for r in R2["terminals"]) | set(int(o["uid"]) for o in R2["objs"])
FSP = dict([(int(p["term_b"]), int(p["wire_a"] or 0)) for p in G["fs_tunnel_pairs"]] + [(int(p["term_a"]), int(p["wire_b"] or 0)) for p in G["fs_tunnel_pairs"]])


def gate(label, ok, detail=""):
    P[0 if ok else 1] += 1
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:400]), flush=True)
rows_of = lambda u: [r for r in T if int(r["owner_uid"]) == int(u)]                 # noqa: E731,E305
term = lambda t: next((r for r in T if int(r["term_uid"]) == int(t)), None)       # noqa: E731
brief = lambda r: {k: r[k] for k in ("term_uid", "term_name", "is_source", "wire_uid", "owner_uid", "owner_class", "frame_diagram", "term_class")}  # noqa: E731
on_wire = lambda w: [r for r in T if w and int(r["wire_uid"] or 0) == int(w)]     # noqa: E731


def chain(d):
    """[uid, owner class, owner uid]: diagram -> owning structure -> the diagram it sits on -> ... (owners map, diag_c120_g)."""
    out, d = [], int(d)
    while d and str(d) in OW and len(out) < 30:
        out.append([d, OW[str(d)][0], int(OW[str(d)][1] or 0)]); d = out[-1][2]                  # noqa: E702
    return out


def back(t, n=0):
    """Trace a sink terminal's net back through tunnels to its non-tunnel source: hops [(owner, class, frame_diagram, wire)]."""
    hops, r = [], term(t)
    while r and n < 25:
        n += 1
        src = [x for x in on_wire(r["wire_uid"]) if x["is_source"]]
        if not src:
            hops.append(["NO SOURCE on w{0}".format(r["wire_uid"])]); break                  # noqa: E702
        x = src[0]; hops.append([int(x["owner_uid"]), x["owner_class"], x["frame_diagram"], int(r["wire_uid"] or 0), int(x["term_uid"])])   # noqa: E702
        if not x["owner_class"].endswith("Tunnel") and x["owner_class"] not in ("LeftShiftRegister",):
            break
        w = FSP.get(int(x["term_uid"])) if x["owner_class"] == "FlatSequenceInnerTunnel" else None
        w = w or next((int(y["wire_uid"] or 0) for y in rows_of(x["owner_uid"]) if not y["is_source"] and y["wire_uid"]), 0)
        r = {"wire_uid": w} if w else hops.append(["tunnel #{0}: no wired input face".format(x["owner_uid"])])
    return hops
# G2 the pool
new = sorted(set(int(r["owner_uid"]) for r in T) - old)
F["G2_new_owners"] = [[u, rows_of(u)[0]["owner_class"], rows_of(u)[0]["frame_diagram"], sorted(set(r["term_name"] for r in rows_of(u)))] for u in new]
obt = [u for u in new if any(r["term_name"] == "queue out" for r in rows_of(u)) and any(r["term_name"] == "element data type" for r in rows_of(u))]
F["G2_obtains"] = dict((u, [brief(r) for r in rows_of(u)]) for u in obt)
F["G2_queue_out_sinks"] = dict((u, [brief(x) for r in rows_of(u) if r["term_name"] == "queue out" for x in on_wire(r["wire_uid"]) if not x["is_source"]]) for u in obt)
pd = sorted(set(int(rows_of(u)[0]["frame_diagram"]) for u in obt))
F["G2_pool_diagram"], F["G2_chains"] = pd, dict((d, chain(d)) for d in pd + [639, 23166, 686])
F["G2_existing_route_Image_In_6810"] = [back(r["term_uid"]) for r in rows_of(6810) if r["term_name"] == "Image In"]
tun12 = sorted(set(int(r["owner_uid"]) for r in T if r["owner_class"] == "LoopTunnel" and int(r["frame_diagram"] or 0) == 23166 and r["is_source"]))
F["G2_existing_routes_into_23166"] = dict((u, back(next(r["term_uid"] for r in rows_of(u) if not r["is_source"]))) for u in tun12
                                          if any(not r["is_source"] and r["wire_uid"] for r in rows_of(u)))
FS1, FS2 = {686, 81548, 113, 124, 759, 1817, 3121, 3628, 4866, 5031}, {13236, 15041, 21134, 25769, 12960, 14840, 19687, 19887, 20261, 26117}
F["G2_fs_sets_cite"] = "docs/d1-loop12-17-split-plan.md:116-117 (two top-level flat sequences, owner #536)"
F["G2_fs_frame_pos"] = dict((k, sorted([OBJ.get(d, {}).get("pos", [None])[0], d] for d in S if d in OBJ)) for k, S in (("FS1", FS1), ("FS2", FS2)))
fot = {}
_ = [fot.setdefault(int(r["owner_uid"]), []).append(r) for r in T if r["owner_class"] == "FlatSequenceOuterTunnel"]
side = lambda rs: "FS1" if any(int(x["frame_diagram"] or 0) in FS1 for x in rs) else ("FS2" if any(int(x["frame_diagram"] or 0) in FS2 for x in rs) else "?")  # noqa: E731
cross = [[u, side(rs), int(y["owner_uid"]), side(fot[int(y["owner_uid"])]), int(x["wire_uid"])] for u, rs in fot.items() for x in rs
         for y in on_wire(x["wire_uid"]) if y["owner_class"] == "FlatSequenceOuterTunnel" and int(y["owner_uid"]) != u and side(rs) != side(fot[int(y["owner_uid"])])]
F["G6_routes"] = {"IMAQ Copy (new subVI)": "EXISTS: stagexec create route 'subvi' (gscript.drop_subvi, stagexec.py:212,310-313); path docs/NAMES.md:960 (Management.llb)",
                  "Dequeue Element": "gscript.queue_node('dequeue') EXISTS (gscript.py:1340,1344, OpQueueDequeue_v0); stagexec plan route MISSING: create_route accepts queue_kind obtain|enqueue only (stagexec.py:305-308)",
                  "Case structure in a loop body": "gscript.case_in EXISTS (gscript.py:3508-3543: build_case on top level + move_in, selector wire severed by the move); NO stagexec CREATE_ROUTES entry (stagexec.py:198-213) -> plan route MISSING",
                  "typed constant on the Obtains' diagram 13236": "copy of an existing typed constant EXISTS: create_primitive_nested(donor={donor,uid}) (gscript.py:4418-4421; the pool's p_i32/p_ring rows, stage_d1_qrt_pool.log:86,95); "
                  "const_on_term only in a WhileLoop body (stagexec.py:207); OpCreateConstTop_v0 only on TOP-LEVEL Nodes[] terminals (gscript.py:2796-2802); a set-type op: none (grep set_type/SetType 0)"}
F["G2_fs_outer_tunnels"] = {"count": len(fot), "by_side": dict((k, sum(1 for rs in fot.values() if side(rs) == k)) for k in ("FS1", "FS2", "?")), "wires_between_FS1_FS2": cross}
F["G2_cam_forward_14741"] = [brief(x) for x in on_wire(14741)] + [brief(x) for p in G["fs_tunnel_pairs"] if int(p["uid"]) == 13167 for x in on_wire(p["wire_b"])]
gate("G2 pool: 2 Obtains on one diagram + new ForLoop/SubVI/Enqueue", len(obt) == 2 and len(pd) == 1, F["G2_new_owners"])
# G3
F["G3_6810_terms"], F["G3_5058_terms"] = [brief(r) for r in rows_of(6810)], [brief(r) for r in rows_of(5058)]
F["G3_6810_ImageOut_sinks"] = [brief(x) for r in rows_of(6810) if r["term_name"] == "Image Out" for x in on_wire(r["wire_uid"]) if not x["is_source"]]
F["G3_5058_outputs"] = [brief(r) for r in rows_of(5058) if r["is_source"]]
F["G3_callees"] = CAL.get("callees")
gate("G3 #6810/#5058 terminal rows + callee paths", F["G3_6810_terms"] and F["G3_5058_terms"] and "6810" in (CAL.get("callees") or {}), len(F["G3_6810_terms"]))
# G4 field sources
FS = [("F1", 30117, "Value"), ("F2", 4580, "Value"), ("F3", 644, None), ("F4", 5119, "x-y"), ("F5", 11608, "output cluster"), ("R0", 2626, "appended array")]
F["G4_fields"] = []
for f, u, nm in FS:
    rs = [r for r in ([term(644)] if nm is None else [r for r in rows_of(u) if r["term_name"] == nm and r["is_source"]]) if r]
    F["G4_fields"].append({"field": f, "uid": u, "rows": [brief(r) for r in rs], "owner_obj": OBJ.get(u), "data_type": "NO READER: Terminal.Data Type "
                           "634A008 resolves but no op reads its value (docs/NAMES.md:470-484; OpNodeTerms_v0 items fixed, opnodeterms_labels.json)"})
gate("G4 all six field source rows found", all(x["rows"] for x in F["G4_fields"]), [(x["field"], len(x["rows"])) for x in F["G4_fields"]])
# G5 M1-M4
F["G5"] = dict((u, {"terms_in_read_order": [brief(r) for r in rows_of(u)], "M1_concatenate_inputs": "NO READER (grep 'Concatenate' in tools/*.py: 0 hits "
               "outside tools/gpu; result_113-3.json:15)", "M2_input_names": [r["term_name"] for r in rows_of(u) if not r["is_source"]],
               "M3_index": "Terminals[] read order above (OpAllTerms_v1 via wiki_build.read_live)", "M4_type": "NO READER (as G4)"}) for u in (11261, 2626))
gate("G5 #11261/#2626 rows found", all(F["G5"][u]["terms_in_read_order"] for u in (11261, 2626)))
# G7 draft uids
R1T, chk = dict((int(r["term_uid"]), r) for r in R1["terminals"]), []
for row in DR["rows"]:
    for end in ("src", "dst"):
        e = row.get(end) or {}
        if isinstance(e, dict) and e.get("term_uid") is not None:
            a, b = R1T.get(int(e["term_uid"])), term(e["term_uid"])
            diff = None if not (a and b) else [k for k in ("owner_uid", "frame_diagram", "term_name", "wire_uid") if str(a[k]) != str(b[k])]
            chk.append({"row": row["id"], "end": end, "uid": e.get("uid"), "term_uid": e["term_uid"], "present": bool(b),
                        "changed_vs_R1": diff, "now": brief(b) if b else None, "r1": brief(a) if a else None})
import re                                                                           # noqa: E402  G7b: every '#uid' / diagram uid the draft names
R1O, R1F = dict((int(o["uid"]), o) for o in R1["objs"]), dict((int(r["owner_uid"]), r["frame_diagram"]) for r in R1["terminals"])
NF = dict((int(r["owner_uid"]), r["frame_diagram"]) for r in T)
ids = sorted(set(int(x) for x in re.findall(r"#(\d+)", json.dumps([DR["rows"], DR["loops"]]))) | set(int(r["diagram"]) for r in DR["rows"] if r.get("diagram")))
F["G7"], F["G7b"] = chk, [{"uid": u, "now": [OBJ.get(u, {}).get("class"), OBJ.get(u, {}).get("owner"), NF.get(u)], "r1": [R1O.get(u, {}).get("class"),
                          R1O.get(u, {}).get("owner"), R1F.get(u)], "same": [OBJ.get(u, {}).get("class"), OBJ.get(u, {}).get("owner"), NF.get(u)] ==
                          [R1O.get(u, {}).get("class"), R1O.get(u, {}).get("owner"), R1F.get(u)] and u in OBJ} for u in ids]
gate("G7 every draft term_uid present on the pool graph", all(c["present"] for c in chk), [c["term_uid"] for c in chk if not c["present"]])
print("  FACT  G7b {0} named uids; changed/absent vs R1: {1}".format(len(ids), [(x["uid"], x["now"], x["r1"]) for x in F["G7b"] if not x["same"]]), flush=True)
out = os.path.join(HERE, "facts_c120_qrtw.json"); json.dump(F, open(out, "w", encoding="utf-8"), indent=1, default=str)   # noqa: E702
print("  FACT  wrote {0}".format(out), flush=True)
print(protocol.result_line(protocol.make_result(P[0], P[1], None if not P[1] else "see FAIL lines", [])), flush=True)
sys.exit(1 if P[1] else 0)
