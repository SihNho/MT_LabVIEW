# ---
# labview: build
# hardware: none
# evidence: tools/bench/cards/task_169-a1-1.json
# ---
r"""stage_d1_ring_p6 - card 169-a1-1 (brief_169-a1-1.md; PD406(c)(d)(e), docs/d1/ring-p6.md:141-182): P6-1 = ONE launch on a byte copy of the
P5 final claudeDev\D1_ring_p5_20261010_172913.vi (75773b0d) named claudeDev\D1_ring_p6_<ts>.vi (Stage name "D1_ring_p6", Stage.__init__
stagekit.py:247 forms <name>_<stamp>.vi): R1 = Remove Bad Wires (op `rbw_method410`), R2 = Stage.delete_object(BuildArray #11261); nothing
else. Pre-save gates S-1..S-5 (PD406(e) + (b)); SAVED (Stage.save, scripted route, ExecState 1) ONLY when all pass, else the copy is a
scratch deleted at close. `--scratch`: the same rows and gates on a dated byte copy that is NEVER saved (the tool's scratch rule, PD406(c)).

Found before writing (docs/script-writing.md): the sequence is diag_c168_a1_2_rbwdel.py (card 168-a1-2, same bed, same two rows), whose logic
is shared and CALLED here, not pasted: stagekit Stage (_op, broken_wire_count -> gscript.remove_bad_wires_scripted, delete_object
stagekit.py:700, save stagekit.py:1204, e5_check), gscript.exec_state, prep_c167_a1_1_graphlib.read_graph, prep_c168_a1_2_lib (Meter,
gone_and_count, el_read, frame_cdiff, and - extracted by THIS card from diag_c168_a1_2_rbwdel.py:138-150 with self-tests T7-T10,
prep_c168_a1_2_lib_selftest_c169.log - fs3_check, tunnels_read, fs4_check, cdiff_rowset_diff). The work copy is declared a scratch first
(Stage.discard_work) and taken off the scratch list only after a successful save, as RingSession.finish does (stagekit.py:2768-2769).
Uids / class / wire counts come from diag_c168_a1_2_plan.json (no re-typed uid, prerun X6).
PREDICTION CONTRACT (gates; 168 measured every one on the same bed, diag_c168_a1_2_facts.md): A0 ExecState BEFORE RBW == 0; R0 RBW op without
error; A1 ExecState AFTER RBW == 0; R1 Wire count 2091 -> 2066; D0 delete op without error; D1 #11261 absent, Wire objects 2066; E5/W22/G1/FS1
graph checks as 168; EL0 MEM headroom <= 668; EL1-EL3 Error List read whole; S-1 ExecState after delete == 1; S-2 Error List 0 items, window N
0; S-3 #2626 4 inputs == 7815af09 sources; S-4 #5204/#10404 (IndexMode, canon, sig) == stored 7f2582ae; S-5 frame cdiff(S1, this copy) ==
frame cdiff(S1, 57f33e7c) row for row (30 rows, both differences empty); then SAVE: S1/S2/S3 of Stage.save (ExecState 1 re-read), PS saved md5
!= input, input unchanged; M every MEM line <= 675; X input md5 unchanged. Dry: A0/A1/R1/D1 stub-only (DRY-UNVERIFIED-OK in the card).
    py tools/bgrun.py --material --max-min 60 --log tools/bench/launch_c169_p6.log --unverified-card tools/bench/cards/task_169-a1-1.json
       -- py -u tools/recipes/stage_d1_ring_p6.py            (append --scratch for the never-saved scratch run)"""
import json, os, sys                                                                          # noqa: E401
RHERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(RHERE))   # noqa: E702
HERE = os.path.join(ROOT, "tools", "bench")
for _p in (os.path.join(ROOT, "tools"), RHERE, HERE):
    _p in sys.path or sys.path.insert(0, _p)                                                  # noqa: E701
import stagekit as K                                                                          # noqa: E402
import prep_c167_a1_1_graphlib as GL                                                          # noqa: E402
import prep_c168_a1_2_lib as LB                                                               # noqa: E402
g = K.g

# ---- INPUTS -------------------------------------------------------------------------------------------------------------------------
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
BED, BEDM = os.path.join(CD, "D1_ring_p5_20261010_172913.vi"), "75773b0ded2a08586bb1a542ddda5af6"
PL = K.jload(HERE, "diag_c165_a3_4_graph_plan.json")                                        # fs_pairs_from (as 168)
FACTS = K.jload(HERE, "p6_facts.json")
TERMLESS = sorted(int(r["uid"]) for r in FACTS["rows"]["F1"] if r.get("class") == "notconnected")
TUNPLAN = K.jload(HERE, "diag_c166_a1_1_tun_plan.json")["tunnels"]
TUN7F = K.jload(HERE, "diag_c166_a1_1_tun.json")["tunnels"]["p5s01"]                       # stored 7f2582ae reads
PLAN = K.jload(HERE, "diag_c168_a1_2_plan.json")                                       # the two rows + uids (PD406(c)(d))
DEL_CLS, DEL_UID = PLAN["delete"]["cls"], int(PLAN["delete"]["uid"])
FS3_NODE = int(PLAN["fs3_node"]["uid"])
W_BEFORE, W_AFTER = int(PLAN["wires"]["before_rbw"]), int(PLAN["wires"]["after_rbw"])
G168 = LB.G168                                                                                # 57f33e7c, PD406(b) reference graph
MEM_LIMIT, EL_HEADROOM = 675.0, 668.0
SCRATCH = "--scratch" in sys.argv
NAME = "scratch_c169_p6" if SCRATCH else "D1_ring_p6"
OUT_JSON = os.path.join(HERE, "launch_c169_p6_scratch.json" if SCRATCH else "launch_c169_p6.json")
DRY = bool(getattr(g.report_all, "_dry", False))
s = K.Stage(BED, BEDM, NAME, preload=False, deadline_min=55, reserve_s=150, out_json=OUT_JSON,
            task="card 169-a1-1 P6-1: RBW + delete #11261 on a byte copy of 75773b0d{0}".format(" (SCRATCH, never saved)" if SCRATCH else ", saved on the gates"))
M = LB.Meter(s, K.private_bytes)


# ---- CALLS --------------------------------------------------------------------------------------------------------------------------
def body(_):
    s.fact("mode {0}; input md5 before: {1}; 22 termless F1 uids {2}".format("SCRATCH" if SCRATCH else "BUILD", K.md5(BED), TERMLESS))
    s.start(); s.discard_work(); W = s.work                                                  # noqa: E702
    s.fact("WORK COPY (a scratch until the save gates pass): {0}".format(os.path.basename(W)))
    bp = K.mod("bench_prep"); h0 = bp.labview_handles()                                      # noqa: E702
    s.R["handles_before"] = h0
    M.mem("after_load")
    # ---- a. ExecState BEFORE
    es0 = g.exec_state(W)
    s.R["exec_state_before"] = es0
    s.fact("EXECSTATE BEFORE RBW: {0}".format(es0))
    s.gate("A0 ExecState BEFORE RBW == 0", es0 == 0, es0)
    # ---- b. R1 = RBW (op label rbw_method410, PD405(f))
    rec = s._op("rbw_method410", lambda: s.broken_wire_count(
        W, allow_mutation=True, tag="RBW (gscript.remove_bad_wires_scripted via stagekit.broken_wire_count)"), "VI method 410 on the work copy")
    rb = rec["result"]
    s.R["rbw"] = rb
    if not s.gate("R0 the RBW op returned without an error", rb and not rec["err"], rec["err"]):
        return s.dump()
    s.fact("EXECSTATE AFTER RBW: {0}; Wire count {1} -> {2}".format(rb["exec_state"], rb["wires_before"], rb["wires_after"]))
    s.gate("A1 ExecState AFTER RBW == 0", rb["exec_state"] == 0, rb["exec_state"])
    # ONE physical line (statement-scoped dry taint, stage_prerun.py:809, :1042; gate-fp fp-100)
    s.gate("R1 Wire count drop after RBW 2091 -> 2066", rb["wires_before"] == W_BEFORE and rb["wires_after"] == W_AFTER, (rb["wires_before"], rb["wires_after"]))
    M.mem("after_rbw")
    # ---- c. R2 = delete #11261
    drec = s.delete_object(DEL_CLS, DEL_UID, tag="169-a1-1 delete #11261 ")
    s.R["delete"] = {"err": drec["err"], "result": drec["result"], "outcome": drec.get("outcome")}
    s.gate("D0 Stage.delete_object({0}, {1}) returned without an error".format(DEL_CLS, DEL_UID), not drec["err"], drec["err"])
    es2 = g.exec_state(W)
    s.R["exec_state_after_delete"] = es2
    s.fact("EXECSTATE AFTER DELETE: {0}".format(es2))
    s.gate("D1 #11261 absent after delete and Wire objects 2066", *LB.gone_and_count(g, W, DEL_CLS, DEL_UID, W_AFTER, s.R, s.fact))
    M.mem("after_delete")
    # ---- d. graph read of the in-memory copy
    gr, info = GL.read_graph(s, W, PL["fs_pairs_from"], "tools/recipes/stage_d1_ring_p6.py (prep_c167_a1_1_graphlib.read_graph) on the "
                             "RBW'd + #11261-deleted {0} byte copy of 75773b0d, before the save".format("SCRATCH" if SCRATCH else "work"))
    gr["md5"] = BEDM
    gr["note"] = "graph of the IN-MEMORY copy after RBW (method 410) and the delete of BuildArray #11261, read BEFORE the save"
    M.mem("after_graph_read")
    if DRY:                    # dry (COM stubbed): nothing below is judgeable, no GUI, no save
        return s.dump()
    base = json.load(open(LB.BASE_GRAPH, encoding="utf-8"))
    e5 = K.e5_check({"made": {}, "deleted_nodes": [DEL_UID], "deleted_wires": TERMLESS, "new_wires": []}, gr, base)
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
    gout = os.path.join(HERE, "graph_ring_p6{0}_{1}.json".format("rbwd" if SCRATCH else "_presave", s.stamp))
    json.dump(gr, open(gout, "w", encoding="utf-8"))
    s.R["graph"] = {"path": os.path.relpath(gout, ROOT), "md5": K.md5(gout), "rows": len(gr["terminals"]), "objs": len(gr["objs"]),
                    "wire_objs": len(wobj), "deleted_in_objs": any(int(o["uid"]) == DEL_UID for o in gr["objs"])}
    s.fact("WROTE {0} md5 {1}: {2} rows, {3} objs, {4} Wire objs, {5} loops, {6} FS; #11261 in objs {7}".format(
        gout, s.R["graph"]["md5"], len(gr["terminals"]), len(gr["objs"]), len(wobj), len(gr["loops"]), len(fsu), s.R["graph"]["deleted_in_objs"]))
    # ---- e. full Error List of the in-memory copy (no save)
    m_now = M.lines[-1][1]
    if not s.gate("EL0 MEM before the Error List read {0} <= {1} (headroom)".format(m_now, EL_HEADROOM), m_now <= EL_HEADROOM, m_now):
        return s.dump()
    elo, R = LB.el_read(g, W, os.path.join(HERE, "errorlist_D1_ring_p6{0}_{1}.json".format("rbwd" if SCRATCH else "_presave", s.stamp)),
                        "tools/recipes/stage_d1_ring_p6.py -> prep_c168_a1_2_lib.el_read (live session, before the save)")
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
    # ---- f. PRE-SAVE GATES S-1..S-5 (PD406(e) + (b)): REAL gates; any FAIL = no save
    ok3, ev3, _d3 = LB.fs3_check(base, gr, FS3_NODE)
    tr = LB.tunnels_read(s, g, W, TUNPLAN)
    s.R["tunnels"] = tr
    ok4, ev4, _c4 = LB.fs4_check(tr, TUN7F)
    s5 = LB.cdiff_rowset_diff(LB.frame_cdiff(gr), LB.frame_cdiff(json.load(open(G168, encoding="utf-8"))))
    s.R["s5"] = s5
    sg = [s.gate("S-1 ExecState after the delete == 1", es2 == 1, es2),
          s.gate("S-2 Error List 0 error items (item count 0, window N 0)", R["item_count"] == 0 and R.get("n_reported") == 0,
                 (R["item_count"], R.get("n_reported"))),
          s.gate("S-3 #2626 has its 4 inputs wired, sources == 7815af09", ok3, ev3),
          s.gate("S-4 LoopTunnels #5204 / #10404 IndexMode + outer type == stored 7f2582ae", ok4, ev4),
          s.gate("S-5 frame cdiff(S1, this copy) == frame cdiff(S1, 57f33e7c) row for row", s5["ok"],
                 "rows {0} vs {1}; only in this copy {2}; only in 57f33e7c {3}".format(s5["rows_a"], s5["rows_b"], s5["only_a"], s5["only_b"]))]
    s.R["save_gates"] = sg
    M.mem("after_save_gates")
    if not all(sg):
        s.fact("NO SAVE: a pre-save gate FAILED ({0}); the work copy stays a scratch and is deleted at close".format(sg))
    elif SCRATCH:
        s.fact("SCRATCH RUN: every pre-save gate PASS; nothing saved, the copy is deleted at close (PD406(c))")
    else:
        # ---- g. SAVE (scripted route, ExecState 1; Stage.save re-reads ExecState after the save)
        m = s.save(broken_ok=False)
        if m and m != s.input_md5 and W in s.scratches:
            s.scratches.remove(W)                     # kept on disk, as RingSession.finish (stagekit.py:2768-2769)
        s.R["saved"] = {"path": W if m else None, "md5": m, "bytes": s.R["saves"].get("bytes")}
        s.gate("PS artefact saved, md5 differs from the input; input unchanged", m and m != s.input_md5 and K.md5(BED) == BEDM, m)
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
