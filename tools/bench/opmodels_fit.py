r"""opmodels_fit - card chat-S1 step C. PURE PYTHON, no LabVIEW. Reads the measured diffs tools/bench/opmodels/raw/<op>_<n>.json
(opmodels_measure.py B1/B2 on dated scratches of D1_s4_loop17.vi) plus the bed dumps (bed_s4_loop17.json, bed_s3_loop15.json,
bed_l7_1a.json) and writes ONE model per op to tools/bench/opmodels/<op>.json: preconditions, what is added (symbolic), the
removal RULE, the edges added, side effects, the uid allocation pattern, and per sample the machine check of the rule
(`fits`). A rule that two samples do not both fit is written `verdict: ambiguous` with the disagreeing evidence.
The rules were written AFTER reading the diffs (step B), and are checked here against every sample - including the L7-1a
move (opmodels_check_move.py, 5/0).
PREDICTION: 10 model files written; every sample fits its op's rule, except the two sub-rules already known to disagree
(delete_object / move_in on a wire whose ONLY sink was the node), which are recorded as ambiguous, not failed.
    MATERIAL=1 py tools/bgrun.py --max-min 3 --log tools/bench/opmodels_fit.log -- py -u tools/bench/opmodels_fit.py"""
import collections, glob, json, os, sys                                            # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.dirname(HERE)]
import opmodels_lib as L, protocol as P                                            # noqa: E401,E402

OM = os.path.join(HERE, "opmodels")
J = lambda n: json.load(open(os.path.join(OM, n), encoding="utf-8"))              # noqa: E731
BED, S3, A7 = J("bed_s4_loop17.json"), J("bed_s3_loop15.json"), J("bed_l7_1a.json")
BED_UIDS = set(int(o["uid"]) for o in BED["objs"])
BED_E, BED_W, _h = L.edges(BED["terms"])
TUN = ("LoopTunnel", "Tunnel", "SelectorTunnel", "FlatSequenceInnerTunnel", "FlatSequenceOuterTunnel")
passes, fails = [], []


def gate(label, ok, detail=""):
    (passes if ok else fails).append(label)
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:400]), flush=True)


def raw(op):
    return [json.load(open(p, encoding="utf-8")) for p in sorted(glob.glob(os.path.join(OM, "raw", op + "_*.json")))]


def common(r):
    d = r["diff"]
    ta = collections.defaultdict(list)
    for t in d["terms_added"]:
        ta[t["owner_uid"]].append(t)
    inv = [o["uid"] for o in d["objs_added"] if o["class"] == "Invoke" and not any(t["wire_uid"] for t in ta[o["uid"]])]
    flips = [(c["term_uid"], c["owner_class"], c["changed"]["is_source"]) for c in d["terms_changed"] if "is_source" in c["changed"]]
    new = d["uid_alloc"]["new_obj_uids"]
    return {"stray_invokes": inv, "new_wires": [o["uid"] for o in d["objs_added"] if o["class"] == "Wire"],
            "deleted_wires": [o["uid"] for o in d["objs_removed"] if o["class"] == "Wire"],
            "new_objs_by_class": dict(collections.Counter(o["class"] for o in d["objs_added"])),
            "direction_flips": flips, "edges_added": len(d["edges_added"]), "edges_removed": len(d["edges_removed"]),
            "edges_rewired": len(d["edges_rewired"]), "exec_state_after": r["exec_state_after"],
            "uid": {"all_new_above_max": d["uid_alloc"]["all_new_above_max"], "new": new,
                    "reissued_bed_uids": sorted(u for u in new if u in BED_UIDS)},
            "wire_objs": [d["stats_before"]["wire_objs"], d["stats_after"]["wire_objs"]]}


def pairs(edges):
    return sorted((e["src"], e["sink"]) for e in edges)


def node_edges(E, terms, uid):
    mine = set(t["term_uid"] for t in terms if t["owner_uid"] == uid)
    return sorted(k for k in E if k[0] in mine or k[1] in mine)


# ---------------------------------------------------------------- per-op checks: return (fits, checks, ambiguous-notes)
def chk_move(r):
    n = r["meta"]["node"]
    pred, dead = L.apply_move(BED["terms"], n)
    EP, _w, HP = L.edges(pred)
    rm_p = sorted(set(BED_E) - set(EP))
    d = r["diff"]
    half_new = sorted(set(d["half_wires_after"]) - set(d["half_wires_before"]))
    hp_node = sorted(set(HP) - set(_h))
    c = {"pred_removed": rm_p, "obs_removed": pairs(d["edges_removed"]), "pred_new_half": hp_node, "obs_new_half": half_new,
         "dead_tunnels": dead}
    ok = c["pred_removed"] == c["obs_removed"] and not d["edges_added"] and hp_node == half_new
    return ok, c, []


def chk_delete_wire(r):
    w = r["meta"]["wire"]
    exp = sorted(k for k, v in BED_E.items() if v == w)
    d = r["diff"]
    c = {"expected_removed": exp, "obs_removed": pairs(d["edges_removed"]),
         "objs_removed": [(o["uid"], o["class"]) for o in d["objs_removed"]]}
    ok = exp == c["obs_removed"] and c["objs_removed"] == [(w, "Wire")] and not d["edges_added"]
    return ok, c, []


def chk_delete_object(r):
    n = r["meta"]["uid"]
    pred, dead, amb = L.apply_delete_object(BED["terms"], n)
    EP, _w, _hp = L.edges(pred)
    rm_p = sorted(set(BED_E) - set(EP))
    d = r["diff"]
    fl_o = sorted(c["term_uid"] for c in d["terms_changed"] if "is_source" in c["changed"])
    TB = dict((t["term_uid"], t) for t in BED["terms"])
    fl_p = sorted(t["term_uid"] for t in pred if t["is_source"] != TB[t["term_uid"]]["is_source"])
    del_w = [o["uid"] for o in d["objs_removed"] if o["class"] == "Wire"]
    c = {"pred_removed": rm_p, "obs_removed": pairs(d["edges_removed"]), "pred_flips": fl_p, "obs_flips": fl_o,
         "dead_tunnels": dead, "sole_sink_wires": amb, "sole_sink_wires_deleted": sorted(set(amb) & set(del_w))}
    ok = rm_p == c["obs_removed"] and fl_p == fl_o
    notes = ["sole-sink wire(s) {0}: deleted {1}".format(amb, c["sole_sink_wires_deleted"])] if amb else []
    return ok, c, notes


def chk_rbw(r):
    d = r["diff"]
    del_w = sorted(o["uid"] for o in d["objs_removed"] if o["class"] == "Wire")
    other = [(o["uid"], o["class"]) for o in d["objs_removed"] if o["class"] not in ("Wire", "Terminal")]
    c = {"half_before": d["half_wires_before"], "deleted_wires": del_w, "half_after": d["half_wires_after"],
         "live_edges_removed": pairs(d["edges_removed"]), "other_objs_removed": other}
    ok = del_w == sorted(d["half_wires_before"]) and not d["half_wires_after"] and not d["edges_removed"]
    return ok, c, []


def chk_creator(expect):
    def f(r):
        d = r["diff"]
        cls = sorted(o["class"] for o in d["objs_added"])
        c = {"objs_added": cls, "terms_added": [(t["owner_class"], t["is_source"], bool(t["wire_uid"])) for t in d["terms_added"]],
             "edges": [len(d["edges_added"]), len(d["edges_removed"])]}
        return cls == sorted(expect) and not d["edges_added"] and not d["edges_removed"] \
            and not any(t["wire_uid"] for t in d["terms_added"]), c, []
    return f


def chk_border(r):
    """tunnel + connect_from_wire: one new LoopTunnel on the loop, exactly 2 new edges src->tunnel->sink."""
    d = r["diff"]
    tun = [o["uid"] for o in d["objs_added"] if o["class"] == "LoopTunnel"]
    ad = d["edges_added"]
    chain = len(ad) == 2 and len(tun) == 1 and \
        sorted([ad[0]["src_owner"], ad[0]["sink_owner"], ad[1]["src_owner"], ad[1]["sink_owner"]]).count(tun[0]) == 2
    c = {"new_tunnels": tun, "edges_added": pairs(ad), "rewired": [(e["src"], e["sink"], e["wire"]) for e in d["edges_rewired"]],
         "source_wire_replaced": [e for e in d["terms_changed"] if "wire_uid" in e["changed"] and e["changed"]["wire_uid"][0]
                                  and e["changed"]["wire_uid"][1]]}
    return chain and not d["edges_removed"], c, []


def chk_wire_sr(r):
    d = r["diff"]
    ad = d["edges_added"]
    c = {"edges_added": [(e["src_owner"], e["sink_owner"], e["wire"]) for e in ad], "new_objs": len(d["objs_added"]),
         "joined_existing_wire": bool(ad) and ad[0]["wire"] in set(BED_W)}
    return len(ad) == 1 and not d["objs_added"] and not d["edges_removed"] and c["joined_existing_wire"], c, []


def chk_fsit(r):
    d = r["diff"]
    m = r["meta"]
    direct = [e for e in d["edges_added"] if e["sink"] == m["fsit_term"] and e["src_owner"] == m["src"]]
    restored = [e for e in d["edges_added"] if e not in direct]
    in_bed = [(e["src"], e["sink"]) in BED_E for e in restored]
    flips_up = [c for c in d["terms_changed"] if "is_source" in c["changed"] and c["changed"]["is_source"] == [False, True]]
    nw = [o["uid"] for o in d["objs_added"] if o["class"] == "Wire"]
    c = {"direct": pairs(direct), "restored": pairs(restored), "restored_all_in_bed": all(in_bed),
         "flips_back": [(x["term_uid"], x["owner_class"]) for x in flips_up], "new_wires": nw}
    return len(direct) == 1 and all(in_bed) and len(nw) == 1 and not d["edges_removed"], c, []


def chk_const(r):
    d = r["diff"]
    ad = d["edges_added"]
    top = [o for o in d["objs_added"] if o["class"].endswith("Constant") and o["owner"] == "Diagram"]
    c = {"constant_classes": sorted(o["class"] for o in d["objs_added"] if o["class"].endswith("Constant")),
         "edges_added": [(e["src_owner"], e["sink_owner"]) for e in ad], "new_wires": sum(1 for o in d["objs_added"] if o["class"] == "Wire")}
    return len(top) == 1 and len(ad) == 1 and ad[0]["src_owner"] == top[0]["uid"] and c["new_wires"] == 1, c, []


MODELS = [
    ("move_in", "stagekit.Stage.move_in -> build_d1_v0.move_in (OpMoveIn by uid)", chk_move,
     {"preconditions": ["node uid exists; destination Diagram index resolved live (build_d1_v0.diag_index)",
                        "target fully loaded (move_in calls ensure_loaded)"],
      "adds": ["nothing structural; 1 stray Invoke (6 unwired Terminals) on the destination diagram - junk_purge deletes it"],
      "removes_rule": "R1: every terminal of the moved node leaves its wire (wire_uid -> 0). The Wire OBJECT survives: a wire whose only "
                      "source or only sink was the node becomes a half-wire; a branched net keeps its other sinks. R2: a tunnel whose "
                      "sink terminal is now on a sourceless wire loses its direction (source terminals read is_source False), "
                      "cascading down tunnel chains - all edges out of it vanish (L7-1a #1929, #5020). Removed edges = "
                      "edges touching the node + edges out of R2 tunnels.",
      "edges_added": "none",
      "ambiguous": ["a wire from a CONSTANT whose only sink was the moved node: kept as a half-wire for #25091/w25190 "
                    "(move_in_2) but deleted outright for #25149/w25200 (setup of remove_bad_wires_2 and tunnel_1: Wire count "
                    "1908 -> 1907 over the setup; uid 25200 re-issued to a new wire by tunnel_1)"]}),
    ("add_shift_reg", "gscript.add_shift_reg (OpAddShiftReg_v0)", chk_creator(
        ["RightShiftRegister", "LeftShiftRegister", "InnerTerminal", "OuterTerminal", "InnerTerminal", "OuterTerminal"]),
     {"preconditions": ["WhileLoop index from report_all('WhileLoop') (live)", "target fully loaded"],
      "adds": ["RightShiftRegister R + LeftShiftRegister L, each with 1 inner + 1 outer terminal (4 terminal rows, all unwired, "
               "names ''); the op returns R's uid; R is APPENDED to Loop.Shift Registers[] (wire_sr_1: rights [24083, 24150, 23789])"],
      "removes_rule": "nothing", "edges_added": "none", "side_effects": ["ExecState 1 -> 0 (untyped register)"]}),
    ("tunnel", "connect_nested_v1 across a loop border (build_opconnectnested_v1; LabVIEW makes the tunnel)", chk_border,
     {"preconditions": ["source and sink on different sides of a WhileLoop border; both addressed by (Diagram idx, Nodes[] idx, "
                        "Terminals[] idx), read live"],
      "adds": ["1 LoopTunnel on the loop (+ InnerTerminal + OuterTerminal objects), 1 stray Invoke (6 unwired terminals)"],
      "removes_rule": "no edge removed. A source-side HALF-wire is replaced (tunnel_1: w25196 deleted, new w25200); a sink-side "
                      "half-wire is JOINED and keeps its uid (tunnel_2: the tunnel's outer terminal took w2160)",
      "edges_added": "exactly 2: source -> tunnel -> sink"}),
    ("connect_from_wire", "stagekit.Stage.connect_from_wire -> OpConnectFromWire_v0", chk_border,
     {"preconditions": ["the wire exists and the source terminal's index ON THE WIRE is read live (OpWireSource_v5)",
                        "sink addressed by index triple"],
      "adds": ["across a border: 1 LoopTunnel (+2 terminal objects), 1 stray Invoke"],
      "removes_rule": "no edge removed. The SOURCE's wire is RE-CREATED under a new uid: a half-wire (cfw_1 w9415) or a live "
                      "branched net (cfw_2 w23519 -> w25348: its 3 other sinks are re-wired, same (src, sink) pairs)",
      "edges_added": "exactly 2: source -> tunnel -> sink"}),
    ("wire_sr", "gscript.wire_sr('RightIn', ...) (OpWireSR_RightIn_v0)", chk_wire_sr,
     {"preconditions": ["register index k = position of the register's RIGHT uid in Loop.Shift Registers[] (read live)",
                        "body node/terminal index on Loop.Diagram, read live"],
      "adds": ["nothing: the register's inner terminal JOINS the source's existing wire (no new Wire object)"],
      "removes_rule": "nothing", "edges_added": "exactly 1: body source -> RightShiftRegister inner terminal",
      "side_effects": ["ExecState 0 -> 1 on both samples", "other registers' terminal NAMES changed '' -> 'total data array out' "
                       "(wire_sr_1) - names are not modelled"]}),
    ("fs_inner_tunnel_connect", "stagekit.Stage.fs_inner_tunnel_connect -> OpFsInnerTunnelConnect_v1", chk_fsit,
     {"preconditions": ["FSIT addressed by uid; SOURCE by index triple read BEFORE any edit",
                        "the op's own `error out` is never written (POISON readout is normal); errors are invoke_err + err_*"],
      "adds": ["1 Wire (source -> FSIT terminal), 1 stray Invoke"],
      "removes_rule": "nothing",
      "edges_added": "1 direct edge + RESTORATION: every downstream tunnel that had lost its direction (R2, after the setup "
                     "delete_wire) regains it, and its edges reappear exactly as in the bed"}),
    ("delete_wire", "build_opfsinnertunnelconnect_v0.del_wire (Wire by uid -> live index -> gscript.delete_object)", chk_delete_wire,
     {"preconditions": ["wire uid in report_all('Wire') (live)"],
      "adds": [], "removes_rule": "the Wire object and EVERY edge on it (all branches); its terminals read wire_uid 0. R2 applies "
                                  "to tunnels downstream (seen through the fs_inner_tunnel_connect restorations)",
      "edges_added": "none"}),
    ("delete_object", "build_opfsinnertunnelconnect_v0.del_node (uid -> live index -> gscript.delete_object)", chk_delete_object,
     {"preconditions": ["uid in report_all(cls) (live)"],
      "adds": [], "removes_rule": "the node and its terminal rows; every edge touching it; a wire it SOURCED survives as a sink-side "
                                  "half-wire; a branched wire it sank keeps its other sinks; R2 with cascade (#27605: LoopTunnels "
                                  "#28311, #28343 and, downstream, #28370)",
      "edges_added": "none",
      "ambiguous": ["a wire whose ONLY sink was the deleted node: deleted outright for w8385 (constant #1850 -> #7201) but kept as "
                    "half-wires for w2160 and w2187 (delete #1628, remove_bad_wires_1 half_wires_before)"]}),
    ("remove_bad_wires", "gscript.remove_bad_wires_scripted (VI method 410)", chk_rbw,
     {"preconditions": ["mutating: only on a scratch or with allow_mutation (stagekit rule 6)"],
      "adds": [], "removes_rule": "every half-wire (a wire with no source or no sink) - no live edge; ALSO FlatSequenceInnerTunnels "
                                  "left unconnected by the deletion (remove_bad_wires_1: #2283, #2301 with their terminals)",
      "edges_added": "none"}),
    ("const", "stagekit.Stage.const_row -> OpCreateConstOnTerm_v0 (WhileLoop body sink)", chk_const,
     {"preconditions": ["the sink terminal is UNWIRED", "loop index + Loop.Diagram node index + terminal index read live"],
      "adds": ["1 constant typed by the sink (DigitalNumericConstant; for an error cluster a ClusterConstant with Boolean/Numeric/"
               "String element constants) + 1 Wire"],
      "removes_rule": "nothing", "edges_added": "exactly 1: constant -> sink", "side_effects": ["no stray Invoke"]}),
    ("primitive", "gscript.build_index_array (OpBuildIA_v0, top-level diagram only)", chk_creator(
        ["IndexArray", "Terminal", "Terminal", "Terminal"]),
     {"preconditions": ["top-level diagram only; location"],
      "adds": ["1 IndexArray + 3 unwired terminals"], "removes_rule": "nothing", "edges_added": "none"}),
]

print(__doc__)
os.makedirs(OM, exist_ok=True)
for op, wrapper, chk, spec in MODELS:
    rs = raw(op)
    samples = []
    for r in rs:
        ok, c, notes = chk(r)
        samples.append({"raw": "raw/{0}_{1}.json".format(op, r["n"]), "target": r["meta"], "fits": ok, "checks": c,
                        "common": common(r), "notes": notes})
    if op == "move_in":
        samples.append({"raw": "bed_s3_loop15.json -> bed_l7_1a.json (L7-1a, move #376)", "target": {"node": 376},
                        "fits": True, "checks": "opmodels_check_move.log G1-G5 5/0: 16-edge cut set, 12 half-wires, flips "
                                                "{2043, 5050} (tunnels #1929, #5020)", "common": {}, "notes": []})
    fit_all = bool(samples) and all(s["fits"] for s in samples)
    rep = []                                     # B2 was run twice (run 1 kept in raw_B2_run1/): same effect up to uids?
    for r in rs:
        p1 = os.path.join(OM, "raw_B2_run1", "{0}_{1}.json".format(op, r["n"]))
        if os.path.exists(p1):
            a, b = json.load(open(p1, encoding="utf-8"))["diff"], r["diff"]
            same = (pairs(a["edges_added"]) == pairs(b["edges_added"]) and pairs(a["edges_removed"]) == pairs(b["edges_removed"])
                    and sorted(o["class"] for o in a["objs_added"]) == sorted(o["class"] for o in b["objs_added"]))
            rep.append({"n": r["n"], "same_effect": same, "new_uids_run1": a["uid_alloc"]["new_obj_uids"],
                        "new_uids_run2": b["uid_alloc"]["new_obj_uids"]})
    if rep:
        spec = dict(spec, repeat_run=rep)
        gate("R {0}: run 1 and run 2 have the same effect (edge pairs + object classes)".format(op),
             all(x["same_effect"] for x in rep), [(x["n"], x["new_uids_run1"] == x["new_uids_run2"]) for x in rep])
    model = dict({"schema": "opmodel/1", "op": op, "wrapper": wrapper, "measured_on": "claudeDev\\D1_s4_loop17.vi 4b621946 "
                  "(dated scratch copies)", "n_samples": len(samples),
                  "verdict": (("consistent" + ("; sub-rule AMBIGUOUS (see `ambiguous`)" if spec.get("ambiguous") else ""))
                              if fit_all else "ambiguous") if len(samples) >= 2 else "one-sample",
                  "uid_allocation": "new objects take FREE uids inside the existing range (never above the max); a uid freed "
                                    "by a deletion in the same edit is re-issued at once (w9415 -> the stray Invoke of "
                                    "connect_from_wire_1; w25200 -> tunnel_1's new wire). Model new ids SYMBOLICALLY.",
                  "stray_invoke": any(s["common"].get("stray_invokes") for s in samples),
                  "samples": samples}, **spec)
    with open(os.path.join(OM, op + ".json"), "w", encoding="utf-8") as f:
        json.dump(model, f, indent=1, default=str)
    gate("M {0}: {1} sample(s), rule fits all ({2})".format(op, len(samples), model["verdict"]), fit_all,
         [(s["raw"], s["fits"]) for s in samples if not s["fits"]])
print("=== GATES: {0} pass / {1} fail".format(len(passes), len(fails)))
print(P.result_line(P.make_result(len(passes), len(fails), fails[0] if fails else None, [])))
sys.exit(1 if fails else 0)
