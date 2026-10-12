# ---
# labview: build
# hardware: none
# evidence: tools/bench/cards/task_168-a1-2.json
# ---
r"""diag_c168_a1_2_rbwdel - card 168-a1-2 (brief_168-a1-2.md, PD405(c)(d)(g) docs/d1/ring-p6.md:111-138): ONE never-saved, never-adopted
byte copy of the P5 final claudeDev\D1_ring_p5_20261010_172913.vi (75773b0d): Remove Bad Wires (VI method 410), delete BuildArray #11261,
ExecState at each step, graph read, FULL Error List, save gates F-S1..F-S5 as FACTS. Nothing is saved, adopted or repaired.

Found before writing (no new op, no new verb): the sequence and calls of diag_c167_a1_1_rbw.py (same bed): Stage + discard_work;
RBW = s._op("rbw_method410", s.broken_wire_count(W, allow_mutation=True)) (stagekit.py:543 -> gscript.remove_bad_wires_scripted:3104);
delete = Stage.delete_object("BuildArray", 11261) (stagekit.py:700 -> build_opfsinnertunnelconnect_v0.del_node; class string as stored for
#11261 in graph_ring_p6rbw_20261012_191349.json); graph = prep_c167_a1_1_graphlib.read_graph + stagekit.e5_check; Error List / MEM meter /
tunnel read / frame cdiff = prep_c168_a1_2_lib (extracted this card from diag_c167_a1_1_rbw.py:44-84, diag_c166_a1_1_tun.py:42-50,
diag_c167_a1_3_closure.py:144-147; self-test 5/0 prep_c168_a1_2_lib_selftest.log).
PREDICTION CONTRACT (gates): A0 ExecState BEFORE RBW == 0; R0 RBW op without error; A1 ExecState AFTER RBW == 0 (167 measured 0 on the same
bed); R1 Wire count 2091 -> 2066; D0 delete op without error; D1 #11261 absent from the BuildArray list and Wire objects == 2066
(p6_buildarray.md:116); W22/G1/FS1/E5 graph checks as 167 (+ deleted_nodes [11261]); EL0 MEM headroom; EL1-EL3 Error List read whole;
M every MEM line <= 675 (X10); X input md5 unchanged.
UNPREDICTED (ROWS, never gates): ExecState after the delete; the Error List after; F-S1..F-S5.
    py tools/bgrun.py --material --max-min 35 --log tools/bench/diag_c168_a1_2_rbwdel.log -- py -u tools/bench/diag_c168_a1_2_rbwdel.py
      --unverified-card tools/bench/cards/task_168-a1-2.json  (bgrun option, before `--`)"""
import json, os, sys                                                                          # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
sys.path.insert(0, HERE)
import stagekit as K                                                                          # noqa: E402
import prep_c167_a1_1_graphlib as GL                                                          # noqa: E402
import prep_c168_a1_2_lib as LB                                                               # noqa: E402
g = K.g
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
BED, BEDM = os.path.join(CD, "D1_ring_p5_20261010_172913.vi"), "75773b0ded2a08586bb1a542ddda5af6"
PL = K.jload(HERE, "diag_c165_a3_4_graph_plan.json")
FACTS = K.jload(HERE, "p6_facts.json")
TERMLESS = sorted(int(r["uid"]) for r in FACTS["rows"]["F1"] if r.get("class") == "notconnected")
TUNPLAN = K.jload(HERE, "diag_c166_a1_1_tun_plan.json")["tunnels"]
TUN7F = K.jload(HERE, "diag_c166_a1_1_tun.json")["tunnels"]["p5s01"]                      # stored 7f2582ae reads (diag_c166_a1_1_tun.log:44-47)
PLAN = K.jload(HERE, "diag_c168_a1_2_plan.json")                                      # this card's finalized decision rows
DEL_CLS, DEL_UID = PLAN["delete"]["cls"], int(PLAN["delete"]["uid"])
FS3_NODE = int(PLAN["fs3_node"]["uid"])
W_BEFORE, W_AFTER = int(PLAN["wires"]["before_rbw"]), int(PLAN["wires"]["after_rbw"])
MEM_LIMIT, EL_HEADROOM = 675.0, 668.0
DRY = bool(getattr(g.report_all, "_dry", False))
s = K.Stage(BED, BEDM, "scratch_c168_a1_2_rbwdel", preload=False, deadline_min=32, reserve_s=150,
            out_json=os.path.join(HERE, "diag_c168_a1_2_rbwdel.json"), task="card 168-a1-2 RBW + delete #11261 measurement")
M = LB.Meter(s, K.private_bytes)


def body(_):
    s.fact("input md5 before: {0}; 22 termless F1 uids {1}".format(K.md5(BED), TERMLESS))
    s.start(); s.discard_work(); W = s.work                                                  # noqa: E702
    s.fact("SCRATCH (never saved, deleted at close): {0}".format(os.path.basename(W)))
    bp = K.mod("bench_prep"); h0 = bp.labview_handles()                                      # noqa: E702
    s.R["handles_before"] = h0
    M.mem("after_load")
    s.fact("handles after load {0}".format(h0))
    # ---- a. ExecState BEFORE
    es0 = g.exec_state(W)
    s.R["exec_state_before"] = es0
    s.fact("EXECSTATE BEFORE RBW: {0}".format(es0))
    s.gate("A0 ExecState BEFORE RBW == 0", es0 == 0, es0)
    # ---- b. RBW (op label as diag_c167_a1_1_rbw.py:100-101, PD405(f))
    rec = s._op("rbw_method410", lambda: s.broken_wire_count(
        W, allow_mutation=True, tag="RBW (gscript.remove_bad_wires_scripted via stagekit.broken_wire_count)"), "VI method 410 on the scratch")
    rb = rec["result"]
    s.R["rbw"] = rb
    if not s.gate("R0 the RBW op returned without an error", rb and not rec["err"], rec["err"]):
        return s.dump()
    s.fact("EXECSTATE AFTER RBW: {0}; Wire count {1} -> {2}".format(rb["exec_state"], rb["wires_before"], rb["wires_after"]))
    s.gate("A1 ExecState AFTER RBW == 0", rb["exec_state"] == 0, rb["exec_state"])
    # ONE physical line: the dry scopes taint to the gate statement's last line event (stage_prerun.py:809, :1042; gate-fp fp-100)
    s.gate("R1 Wire count drop after RBW 2091 -> 2066", rb["wires_before"] == W_BEFORE and rb["wires_after"] == W_AFTER, (rb["wires_before"], rb["wires_after"]))
    M.mem("after_rbw")
    # ---- c. delete #11261 by the existing route
    drec = s.delete_object(DEL_CLS, DEL_UID, tag="168-a1-2 delete #11261 ")
    s.R["delete"] = {"err": drec["err"], "result": drec["result"], "outcome": drec.get("outcome")}
    s.gate("D0 Stage.delete_object({0}, {1}) returned without an error".format(DEL_CLS, DEL_UID), not drec["err"], drec["err"])
    es2 = g.exec_state(W)
    s.R["exec_state_after_delete"] = es2
    s.fact("EXECSTATE AFTER DELETE: {0}".format(es2))
    s.row("ExecState after the delete of #11261 (UNPREDICTED)", es2)
    # the two reads are taken INSIDE the gate statement (LB.gone_and_count, one line, untraced module), so the dry sees them as the
    # stale-graph reads they are (stage_prerun.py:622 + :809 statement-scoped taint; gate-fp fp-100); the real run reads the same values
    s.gate("D1 #11261 absent after delete and Wire objects 2066", *LB.gone_and_count(g, W, DEL_CLS, DEL_UID, W_AFTER, s.R, s.fact))
    M.mem("after_delete")
    # ---- d. graph read
    gr, info = GL.read_graph(s, W, PL["fs_pairs_from"], "tools/bench/diag_c168_a1_2_rbwdel.py (prep_c167_a1_1_graphlib.read_graph) on the "
                             "RBW'd + #11261-deleted never-saved byte copy of 75773b0d")
    gr["md5"] = BEDM
    gr["note"] = "graph of the IN-MEMORY copy after VI-level Remove Bad Wires (method 410) and the delete of BuildArray #11261; never saved"
    M.mem("after_graph_read")
    if DRY:                    # dry (COM stubbed): the 'after' graph is the stub's BEFORE graph - nothing below is judgeable, no GUI
        return s.dump()
    base = json.load(open(LB.BASE_GRAPH, encoding="utf-8"))
    edits = {"made": {}, "deleted_nodes": [DEL_UID], "deleted_wires": TERMLESS, "new_wires": []}
    e5 = K.e5_check(edits, gr, base)
    s.fact("E5 stagekit.e5_check(edits={{deleted_nodes: [11261], deleted_wires: 22 termless F1}}, after, base 7815af09): ok {0} "
           "deleted_wires_present {1} deleted_nodes_present {2} uid_reused {3} rule {4}".format(
               e5["ok"], e5["deleted_wires_present"], e5["deleted_nodes_present"], len(e5["uid_reused"]), e5["rule"]))
    s.R["e5"] = e5
    s.gate("E5 stagekit.e5_check ok (11261 + 22 termless wires absent)", e5["ok"], {k: e5[k] for k in ("deleted_wires_present", "deleted_nodes_present")})
    wobj = set(int(o["uid"]) for o in gr["objs"] if o["class"] == "Wire")
    s.gate("W22 the 22 termless F1 Wire objects are absent", not [u for u in TERMLESS if u in wobj], [u for u in TERMLESS if u in wobj])
    O, diags, ff, fsu = info["owners"], info["diags"], info["ff"], info["fsu"]
    s.gate("G1 graph: rows > 0, every Diagram owner resolved", gr["terminals"] and all(O[d][0] != "?" for d in diags),
           [d for d in diags if O[d][0] == "?"][:10])
    allf = [f for v in ff.values() for f in v]
    s.gate("FS1 every FlatSequence read ({0}), each has >= 1 frame, no frame in two FS".format(len(fsu)),
           fsu and all(ff[str(u)] for u in fsu) and len(allf) == len(set(allf)), len(allf))
    gout = os.path.join(HERE, "graph_ring_p6rbwd_{0}.json".format(s.stamp))
    json.dump(gr, open(gout, "w", encoding="utf-8"))
    s.R["graph"] = {"path": os.path.relpath(gout, ROOT), "md5": K.md5(gout), "rows": len(gr["terminals"]), "objs": len(gr["objs"]),
                    "wire_objs": len(wobj), "buildarray_11261_in_objs": any(int(o["uid"]) == DEL_UID for o in gr["objs"])}
    s.fact("WROTE {0} md5 {1}: {2} rows, {3} objs, {4} Wire objs, {5} loops, {6} FS; #11261 in objs {7}".format(
        gout, s.R["graph"]["md5"], len(gr["terminals"]), len(gr["objs"]), len(wobj), len(gr["loops"]), len(fsu), s.R["graph"]["buildarray_11261_in_objs"]))
    # ---- e. full Error List of the in-memory scratch
    m_now = M.lines[-1][1]
    if not s.gate("EL0 MEM before the Error List read {0} <= {1} (headroom)".format(m_now, EL_HEADROOM), m_now <= EL_HEADROOM, m_now):
        return s.dump()
    elo, R = LB.el_read(g, W, os.path.join(HERE, "errorlist_D1_ring_p6rbwd_{0}.json".format(s.stamp)),
                        "tools/bench/diag_c168_a1_2_rbwdel.py -> prep_c168_a1_2_lib.el_read (live session, no save)")
    s.R["errorlist"] = {"path": os.path.relpath(elo, ROOT), "md5": K.md5(elo), "items": R["item_count"], "n_reported": R.get("n_reported"),
                        "class_counts": R["class_counts"], "exec_state": R.get("exec_state"), "errors": R["errors"]}
    s.fact("ERRORLIST {0} md5 {1}: items {2} window N {3} class counts {4}; ExecState {5}; errors {6}".format(
        elo, s.R["errorlist"]["md5"], R["item_count"], R.get("n_reported"), R["class_counts"], R.get("exec_state"), R["errors"]))
    for d in R["details"]:
        s.fact("EL item {0}: {1!r} | {2!r} | uid {3}".format(d["index"], d["raw"], str(d["detail"])[:160], d["uid"]))
    s.gate("EL1 every Error List item read (items == the window's N)", R.get("n_reported") is not None and R["item_count"] == R["n_reported"],
           (R["item_count"], R.get("n_reported")))
    s.gate("EL2 every item double-clicked and the diagram fronted", R["dclicked"] == R["item_count"] and R["show_error_ok"] == R["item_count"],
           (R["dclicked"], R["show_error_ok"], R["item_count"]))
    s.gate("EL3 Error List closed with Esc (or no list to close)", bool(R.get("closed_with_esc")) or R["item_count"] == 0, R.get("closed_with_esc"))
    M.mem("after_errorlist")
    # ---- f. save gates as FACTS (rows; no save)
    fs = {}
    fs["F-S1"] = (es2 == 1, "ExecState after the delete {0} (== 1 wanted)".format(es2))
    fs["F-S2"] = (R["item_count"] == 0 and R.get("n_reported") == 0, "Error List items {0}, window N {1}".format(R["item_count"], R.get("n_reported")))
    i_b, i_s = LB.inputs_of(base, FS3_NODE), LB.inputs_of(gr, FS3_NODE)
    sb = [(r["term_uid"], [x[0] for x in r["sources"]]) for r in i_b]
    ss = [(r["term_uid"], r["wire_uid"], [x[0] for x in r["sources"]]) for r in i_s]
    fs["F-S3"] = (len(i_s) == 4 and all(r["wire_uid"] and r["sources"] for r in i_s) and [(a, c) for a, _b, c in ss] == sb,
                  "#2626 inputs scratch (term, wire, src owners) {0} vs 7815af09 (term, src owners) {1}".format(ss, sb))
    tr = {}
    for u, exp in sorted(TUNPLAN.items(), key=lambda kv: int(kv[0])):
        tr[u] = LB.tunnel_read(s, g, W, int(u), exp["outer_term"])
        s.fact("TUN scratch #{0}: {1}".format(u, json.dumps(tr[u], sort_keys=True)))
    s.R["tunnels"] = tr
    cmp4 = dict((u, (tr[u]["index_mode"], tr[u]["canon"], tr[u]["sig"], TUN7F[u]["index_mode"], TUN7F[u]["canon"], TUN7F[u]["sig"])) for u in tr)
    fs["F-S4"] = (all(tr[u]["index_mode"] is not None and tr[u]["sig"] and (c[0], c[1], c[2]) == (c[3], c[4], c[5]) for u, c in cmp4.items()),
                  "#uid (IndexMode, canon, sig) scratch vs stored 7f2582ae (diag_c166_a1_1_tun.json tunnels.p5s01): {0}".format(cmp4))
    cr = LB.closure_rd_diff(LB.frame_cdiff(gr), json.load(open(LB.CLOSURE, encoding="utf-8")))
    s.R["fs5"] = cr
    fs["F-S5"] = (not cr["only_diff"] and not cr["only_closure_cdiff"],
                  "frame cdiff rows {0}; closure R+DISP rows {1}; only in diff {2}; R/DISP cdiff sinks not in diff {3}; R/DISP rows without "
                  "cdiff sink {4}".format(cr["diff_rows"], cr["rd_rows"], cr["only_diff"], cr["only_closure_cdiff"], cr["only_closure_no_cdiff"]))
    s.R["save_gates"] = dict((k, {"pass": bool(v[0]), "evidence": v[1]}) for k, v in fs.items())
    for k in sorted(fs):
        s.row("{0} save gate (FACT, not a launch gate)".format(k), "PASS" if fs[k][0] else "FAIL")
        s.fact("{0} {1}: {2}".format(k, "PASS" if fs[k][0] else "FAIL", fs[k][1]))
    M.mem("after_save_gates")
    h1 = bp.labview_handles()
    s.R["handles_after"] = h1
    s.fact("handles {0} -> {1}".format(h0, h1))
    s.R["mem"] = {"lines": M.lines, "peak": M.peak()}
    s.fact("PEAK MEM {0} MB private ({1})".format(M.peak(), M.lines))
    s.gate("M every MEM line <= {0} (X10)".format(MEM_LIMIT), M.peak() <= MEM_LIMIT, M.peak())
    s.gate("X input md5 unchanged", K.md5(BED) == BEDM, K.md5(BED))
    s.dump()


if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
