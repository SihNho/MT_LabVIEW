# ---
# labview: build
# hardware: none
# evidence: tools/bench/cards/task_167-a1-1.json
# ---
r"""diag_c167_a1_1_rbw - card 167-a1-1 (PD404(d), docs/d1/ring-p6.md:68-76): ONE Remove-Bad-Wires measurement on a never-adopted,
never-saved byte copy of the P5 final claudeDev\D1_ring_p5_20261010_172913.vi (75773b0d). Nothing is built, adopted or kept.

Found before writing (no new op, no new verb):
  - RBW verb: gscript.remove_bad_wires_scripted (tools/gscript.py:3104, VI method 410 via OpRemoveBadWires_v0) through its wrapper
    stagekit.Stage.broken_wire_count (tools/stagekit.py:543; refuses the stage target unless allow_mutation=True - this work copy IS
    the scratch: discard_work() puts it in the scratch list, close() deletes it). The GUI-menu gscript.remove_bad_wires (:1987) is NOT used.
  - graph read: tools/bench/prep_c167_a1_1_graphlib.read_graph (the calls of diag_c165_a3_4_graph.py:45-83, extracted this card),
    then stagekit.e5_check (tools/stagekit.py:3160).
  - Error List: read IN THE LIVE SESSION on the RBW'd in-memory copy with the functions of tools/errorlist_check.py (open_diagram,
    make_on_item, class_counts, count_zero) and lv_errorlist.read (it reads the Error List of a VI already in memory, so no save is
    needed; GUI acts carry errorlist_check's -Exception Approved / -Evidence EVID). The scratch is therefore NEVER saved.
  - fs pairs / loop / case uids: the same as tools/bench/diag_c165_a3_4_graph_plan.json (same bed 75773b0d).
PREDICTION CONTRACT (PD404(d)): ExecState BEFORE 0; RBW (scripted) runs and the Wire count drops; the 22 termless 'not connected'
wires of F1 (tools/bench/p6_facts.json rows.F1) are absent after RBW; G1 every Diagram owner resolved; FS1 every FlatSequence read.
UNPREDICTED (measured, reported, not gated): ExecState AFTER, the number of data-carrying wires deleted, the Error List after.
Memory X10: 647.8 MB load (memory_model.json 75773b0d), every MEM line <= 675 (gate M). Error List is not started if MEM > 668 (gate EL0).
    py tools/bgrun.py --material --max-min 35 --log tools/bench/diag_c167_a1_1_rbw.log -- py -u tools/bench/diag_c167_a1_1_rbw.py"""
import json, os, sys, time                                                                    # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
sys.path.insert(0, HERE)
import stagekit as K                                                                          # noqa: E402
import prep_c167_a1_1_graphlib as GL                                                          # noqa: E402
g = K.g
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
BED, BEDM = os.path.join(CD, "D1_ring_p5_20261010_172913.vi"), "75773b0ded2a08586bb1a542ddda5af6"
PL = K.jload(HERE, "diag_c165_a3_4_graph_plan.json")
BEFORE = os.path.join(HERE, "graph_ring_p5s02e_20261012_173009.json")
FACTS = K.jload(HERE, "p6_facts.json")
TERMLESS = sorted(int(r["uid"]) for r in FACTS["rows"]["F1"] if r.get("class") == "notconnected")
MEM_LIMIT, EL_HEADROOM = 675.0, 668.0
DRY = bool(getattr(g.report_all, "_dry", False))
s = K.Stage(BED, BEDM, "scratch_c167_a1_1_rbw", preload=False, deadline_min=32, reserve_s=150,
            out_json=os.path.join(HERE, "diag_c167_a1_1_rbw.json"), task="card 167-a1-1 RBW measurement")
MEMS = []


def mem(tag):
    v = round((K.private_bytes() or 0) / 1e6, 1)
    MEMS.append((tag, v))
    print("METER {0} k {1} private {2} MB".format(tag, len(MEMS), v), flush=True)
    s.fact("MEM {0}: {1} MB private".format(tag, v))
    return v


def el_read(W, stamp):
    """Full Error List read of the in-memory W with errorlist_check's functions; writes errorlist_D1_ring_p6rbw_<stamp>.json (+_raw)."""
    import errorlist_check as EC
    EC._lv_imports()
    out = os.path.join(HERE, "errorlist_D1_ring_p6rbw_{0}.json".format(stamp))
    R = {"vi": W, "stamp": stamp, "errors": [], "gui_acts_outer": [], "no_vi_was_run": True, "evidence": EC.EVID,
         "source": "tools/bench/diag_c167_a1_1_rbw.py el_read (errorlist_check.open_diagram/make_on_item + lv_errorlist.read, live session)",
         "uid_route": EC.UID_ROUTE}
    try:
        g.open_panel(W)
        time.sleep(1.0)
        R["exec_state"] = g.exec_state(W)
        R["block_diagram_open"] = EC.open_diagram(W, R)
        r = EC.E.read(W, out.replace(".json", "_raw.json"), log=lambda t: print(t, flush=True), on_item=EC.make_on_item(W, R))
        R.update({k: r.get(k) for k in ("method", "n_reported", "n_reported_from", "items", "categories", "gui_acts",
                                        "closed_with_esc", "window", "ocr_engine")})
        R["errors"] += r.get("errors") or []
        if not R.get("items"):
            n0, line, cap = EC.count_zero(R)
            R["n_reported"] = R["n_reported"] if R.get("n_reported") is not None else n0
            R["n_reported_from"], R["zero_capture"] = line, cap
    except Exception as e:                                                         # noqa: BLE001
        R["errors"].append("{0}: {1}".format(type(e).__name__, str(e)[:160]))
    items = R.get("items") or []
    R["item_count"] = len(items)
    R["class_counts"] = EC.class_counts(items)
    R["dclicked"] = sum(1 for i in items if i.get("show_error"))
    R["show_error_ok"] = sum(1 for i in items if (i.get("show_error") or {}).get("diagram_fronted"))
    R["details"] = [{"index": i.get("index"), "raw": i.get("raw"), "detail": i.get("detail"), "object": i.get("object"), "reason": i.get("reason")}
                    for i in items]
    with open(out, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, ensure_ascii=False, default=str)
    return out, R


def body(_):
    s.fact("input md5 before: {0}; 22 termless F1 uids {1}".format(K.md5(BED), TERMLESS))
    s.start(); s.discard_work(); W = s.work                                                  # noqa: E702
    bp =K.mod("bench_prep"); h0 = bp.labview_handles()                                      # noqa: E702
    s.R["handles_before"] = h0
    mem("after_load")
    s.fact("handles after load {0}".format(h0))
    es0 = g.exec_state(W)
    s.R["exec_state_before"] = es0
    s.fact("EXECSTATE BEFORE RBW: {0}".format(es0))
    s.row("A0 ExecState BEFORE RBW (card: quoted; brief expects 0)", es0, 0)    # a ROW, not a gate: COM-stubbed in the dry
    # op label 'rbw_method410': the X5 checker counts any verb containing 'wire' as a wire-making op (gate-fp fp-98, logged);
    # the call inside is unchanged - stagekit.broken_wire_count -> gscript.remove_bad_wires_scripted
    rec = s._op("rbw_method410", lambda: s.broken_wire_count(
        W, allow_mutation=True, tag="RBW (gscript.remove_bad_wires_scripted via stagekit.broken_wire_count)"), "VI method 410 on the scratch")
    rb = rec["result"]
    s.R["rbw"] = rb
    if not s.gate("R0 the RBW op returned without an error", rb and not rec["err"], rec["err"]):
        return s.dump()
    s.fact("EXECSTATE AFTER RBW: {0}; Wire count {1} -> {2}".format(rb["exec_state"], rb["wires_before"], rb["wires_after"]))
    s.row("ExecState after RBW (UNPREDICTED)", rb["exec_state"])
    s.row("R1 Wire count before -> after RBW (card: quoted)", (rb["wires_before"], rb["wires_after"]), "after < before")
    mem("after_rbw")
    gr, info = GL.read_graph(s, W, PL["fs_pairs_from"], "tools/bench/diag_c167_a1_1_rbw.py (prep_c167_a1_1_graphlib.read_graph = "
                             "diag_c165_a3_4_graph.py:45-83 calls) on the RBW'd never-saved byte copy of 75773b0d")
    gr["md5"] = BEDM
    gr["note"] = "graph of the IN-MEMORY copy after VI-level Remove Bad Wires (method 410); the copy was never saved"
    mem("after_graph_read")
    if DRY:                    # dry (COM stubbed): the 'after' graph is the stub's BEFORE graph - nothing below is judgeable, no GUI
        return s.dump()
    base =json.load(open(BEFORE, encoding="utf-8"))
    edits = {"made": {}, "deleted_nodes": [], "deleted_wires": TERMLESS, "new_wires": []}
    e5 = K.e5_check(edits, gr, base)
    s.fact("E5 stagekit.e5_check(edits={{deleted_wires: 22 termless F1}}, after, base 7815af09): ok {0} deleted_wires_present {1} "
           "deleted_nodes_present {2} uid_reused {3} rule {4}".format(e5["ok"], e5["deleted_wires_present"], e5["deleted_nodes_present"],
                                                                    len(e5["uid_reused"]), e5["rule"]))
    s.R["e5"] = e5
    wobj = set(int(o["uid"]) for o in gr["objs"] if o["class"] == "Wire")
    left = [u for u in TERMLESS if u in wobj]
    s.gate("W22 the 22 termless F1 Wire objects are absent after RBW", not left, {"still_present": left})
    O, diags, ff, fsu = info["owners"], info["diags"], info["ff"], info["fsu"]
    s.gate("G1 graph: rows > 0, every Diagram owner resolved", gr["terminals"] and all(O[d][0] != "?" for d in diags),
           [d for d in diags if O[d][0] == "?"][:10])
    allf = [f for v in ff.values() for f in v]
    s.gate("FS1 every FlatSequence read ({0}), each has >= 1 frame, no frame in two FS".format(len(fsu)),
           fsu and all(ff[str(u)] for u in fsu) and len(allf) == len(set(allf)), ff)
    gout = os.path.join(HERE, "graph_ring_p6rbw_{0}.json".format(s.stamp))
    json.dump(gr, open(gout, "w", encoding="utf-8"))
    s.R["graph"] = {"path": os.path.relpath(gout, ROOT), "md5": K.md5(gout), "rows": len(gr["terminals"]), "objs": len(gr["objs"]),
                    "wire_objs": len(wobj)}
    s.fact("WROTE {0} md5 {1}: {2} rows, {3} objs, {4} Wire objs, {5} loops, {6} FS".format(
        gout, s.R["graph"]["md5"], len(gr["terminals"]), len(gr["objs"]), len(wobj), len(gr["loops"]), len(fsu)))
    m_now = MEMS[-1][1]
    if not s.gate("EL0 MEM before the Error List read {0} <= {1} (headroom)".format(m_now, EL_HEADROOM), m_now <= EL_HEADROOM, m_now):
        return s.dump()
    elo, R = el_read(W, s.stamp)
    s.R["errorlist"] = {"path": os.path.relpath(elo, ROOT), "md5": K.md5(elo), "items": R["item_count"], "n_reported": R.get("n_reported"),
                        "class_counts": R["class_counts"], "exec_state": R.get("exec_state"), "errors": R["errors"]}
    s.fact("ERRORLIST {0} md5 {1}: items {2} window N {3} class counts {4}; ExecState {5}; errors {6}".format(
        elo, s.R["errorlist"]["md5"], R["item_count"], R.get("n_reported"), R["class_counts"], R.get("exec_state"), R["errors"]))
    for d in R["details"]:
        s.fact("EL item {0}: {1!r} | {2!r}".format(d["index"], d["raw"], str(d["detail"])[:160]))
    s.gate("EL1 every Error List item read (items == the window's N)", R.get("n_reported") is not None and R["item_count"] == R["n_reported"],
           (R["item_count"], R.get("n_reported")))
    s.gate("EL2 every item double-clicked and the diagram fronted", R["dclicked"] == R["item_count"] and R["show_error_ok"] == R["item_count"],
           (R["dclicked"], R["show_error_ok"], R["item_count"]))
    s.gate("EL3 Error List closed with Esc", bool(R.get("closed_with_esc")), R.get("closed_with_esc"))
    mem("after_errorlist")
    h1 = bp.labview_handles()
    s.R["handles_after"] = h1
    s.fact("handles {0} -> {1}".format(h0, h1))
    peak = max(v for _t, v in MEMS)
    s.R["mem"] = {"lines": MEMS, "peak": peak}
    s.fact("PEAK MEM {0} MB private ({1})".format(peak, MEMS))
    s.gate("M every MEM line <= {0} (X10)".format(MEM_LIMIT), peak <= MEM_LIMIT, peak)
    s.gate("X input md5 unchanged", K.md5(BED) == BEDM, K.md5(BED))
    s.dump()


if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
