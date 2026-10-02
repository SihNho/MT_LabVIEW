r"""selftest_stagesim_fsexit_c138_1 - card 138-1 (offline, no LabVIEW): the stagesim FS-EXIT row (stagesim._fs_exit_wire,
FS_EXIT, FS_EXIT_NAMES) modelled on U6/U6' (diag_c137_7_types.log:290-306,317,328; diag_c137_5_routes.log:167-169), the
delete_wire case-tunnel row-loss fix (stagesim DROP_WHEN_UNWIRED, PD310(c)) and the stagexec FS-exit route (fs_wire_ops ->
variant fs_exit, FS_VARIANT_HOW, ROUTE_CENSUS, _fs_connect_check).
Prior art checked: stagesim selftest() builds states by hand the same way (base_state on a synthetic graph); stagexec
t_entry (stagexec.py ~4965) drives SS._fs_border_wire directly - copied shape. No new op.

  py -u tools/bench/selftest_stagesim_fsexit_c138_1.py [--stagesim <path to another stagesim.py>] [--only D]

--stagesim loads that file as `stagesim` (e.g. the git HEAD copy in %TEMP%) to show the D gates FAIL BEFORE the fix.
PREDICTION CONTRACT (current tools): E1-E7, D1-D3, X1-X4 all PASS; with --stagesim <HEAD copy> --only D: D1 and D2 FAIL.
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--stagesim" in sys.argv:
    _p = sys.argv[sys.argv.index("--stagesim") + 1]
    _spec = importlib.util.spec_from_file_location("stagesim", _p)
    SS = importlib.util.module_from_spec(_spec)
    sys.modules["stagesim"] = SS
    _spec.loader.exec_module(SS)
else:
    import stagesim as SS                                              # noqa: E402
import protocol                                                        # noqa: E402

ONLY = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, detail=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, str(detail)[:300]))


def row(t, name, src, w, owner, cls, diag, tc="Terminal"):
    return {"term_uid": t, "term_name": name, "is_source": src, "wire_uid": w, "owner_uid": owner, "owner_class": cls,
            "frame_diagram": diag, "term_class": tc}


BODY = 23166


def fs_state(feed_name="Num", feed_cls="Local", array_wired=True, src_cls="IndexArray", src_wired=False):
    """A While body BODY with a plan-made FS (as FS9) on it; on its frame f0: an Index Array #100 (element / index / array)
    fed from a #110 source named `feed_name`; on BODY: Equal? #200 with sink 'y'. As U6' built it (diag_c137_7_types.py:51-64)."""
    st = SS.base_state({"terminals": [row(299, "y", False, 0, 200, "Comparison", BODY),
                                      row(298, "x", False, 0, 200, "Comparison", BODY),
                                      row(297, "x = y?", True, 0, 200, "Comparison", BODY)],
                        "objs": [], "owners": {}})
    eff = {}
    SS._create_fs(st, {"as": "FS9"}, BODY, "FS9", eff)
    f0 = st["sym"]["new:FS9.f0"]
    if src_cls == "IndexArray":
        st["terminals"] += [row(101, "element", True, 0, 100, "IndexArray", f0), row(102, "index", False, 0, 100, "IndexArray", f0),
                            row(103, "array", False, 0, 100, "IndexArray", f0)]
    else:
        st["terminals"] += [row(101, "x+y", True, 0, 100, src_cls, f0), row(103, "x", False, 0, 100, src_cls, f0)]
    st["terminals"].append(row(111, feed_name, True, 0, 110, feed_cls, f0))
    if array_wired:
        SS.op_wire(st, {"id": "arr", "src": {"uid": 110, "term_uid": 111}, "dst": {"uid": 100, "term_uid": 103}}, {}, None, {})
    if src_wired:
        st["terminals"].append(row(121, "x", False, 0, 120, "Comparison", f0))
        SS.op_wire(st, {"id": "pre", "src": {"uid": 100, "term_uid": 101}, "dst": {"uid": 120, "term_uid": 121}}, {}, None, {})
    return st, f0


EXIT = {"id": "p_exit", "src": {"uid": 100, "term_uid": 101}, "dst": {"uid": 200, "term_uid": 299}}


def refused(fn, want):
    try:
        fn()
    except SS.SimError as e:
        return want in str(e), str(e)
    return False, "not refused"


def e_gates():
    print("---------- E: FS exit row (U6' measured shape)")
    st, f0 = fs_state()
    w_arr = next(r for r in st["terminals"] if r["term_uid"] == 103)["wire_uid"]
    n0 = len(st["terminals"])
    eff, _ = SS.op_wire(st, dict(EXIT), {}, None, {})
    T = eff.get("tunnels", [None])[0]
    tr = [r for r in st["terminals"] if r["owner_uid"] == T]
    fin = next((r for r in tr if not r["is_source"]), {})
    fout = next((r for r in tr if r["is_source"]), {})
    src = next(r for r in st["terminals"] if r["term_uid"] == 101)
    snk = next(r for r in st["terminals"] if r["term_uid"] == 299)
    gate("E1 how fs_exit, ONE FlatSequenceOuterTunnel, census == U6 delta (diag_c137_5_routes.log:168)",
         eff.get("how") == "fs_exit" and len(eff.get("tunnels") or []) == 1 and eff.get("census") == SS.FS_EXIT["census"]
         and len(st["terminals"]) - n0 == 2, eff.get("census"))
    gate("E2 tunnel on the FS border: sink face on the frame (on the source's wire), source face on the body (on the sink's "
         "wire) - U6' ENDS diag_c137_7_types.log:301-302",
         fin.get("frame_diagram") == f0 and fout.get("frame_diagram") == BODY and fin.get("wire_uid") == src["wire_uid"]
         and fout.get("wire_uid") == snk["wire_uid"] and src["wire_uid"] != snk["wire_uid"] and src["wire_uid"] < 0,
         (fin.get("frame_diagram"), fout.get("frame_diagram"), src["wire_uid"], snk["wire_uid"]))
    gate("E3 faces = source type, wires unbroken (U6' :290,305-306,317,328); array net untouched",
         eff.get("broken_predicted") is False and "source terminal's type" in eff.get("face_type", "")
         and next(r for r in st["terminals"] if r["term_uid"] == 103)["wire_uid"] == w_arr, (eff.get("broken_predicted"), w_arr))
    gate("E4 1b name reproduces diag_c137_7_types.log:301-302 on BOTH faces",
         fin.get("term_name") == fout.get("term_name") == "Index of closest\ncal image slice, bead 2"
         and eff.get("name_status") == "MEASURED", repr(fin.get("term_name")))
    st2, _ = fs_state(feed_name="Other", feed_cls="Local")
    eff2, _ = SS.op_wire(st2, dict(EXIT), {}, None, {})
    T2 = eff2["tunnels"][0]
    nm2 = sorted(set(r["term_name"] for r in st2["terminals"] if r["owner_uid"] == T2))
    gate("E5 1b an unmeasured feed -> UNPREDICTED-NAME on the faces + flagged (never silent '')",
         nm2 == [SS.UNPREDICTED_NAME] and eff2.get("name_status") == "UNPREDICTED-NAME"
         and str(T2) in (st2.get("unpredicted_names") or {}) and any("face name" in u for u in eff2.get("unmeasured")), nm2)
    st3, _ = fs_state(array_wired=False)
    ok, msg = refused(lambda: SS.op_wire(st3, dict(EXIT), {}, None, {}), "VOID source")
    gate("E6 1b void source (Index Array 'array' unwired, U6 diag_c137_5_routes.log:167-169) REFUSED", ok, msg)
    st4, _ = fs_state(src_wired=True)
    ok4, msg4 = refused(lambda: SS.op_wire(st4, dict(EXIT), {}, None, {}), "ALREADY-WIRED")
    st5, f5 = fs_state()
    st5["terminals"].append(row(399, "y", False, 0, 300, "Comparison", 777))
    st5["diagrams"]["777"] = BODY
    ok5, msg5 = refused(lambda: SS.op_wire(st5, {"id": "x", "src": {"uid": 100, "term_uid": 101},
                                                 "dst": {"uid": 300, "term_uid": 399}}, {}, None, {}), "only ONE border")
    st6, _ = fs_state(src_cls="Function")
    eff6, _ = SS.op_wire(st6, dict(EXIT), {}, None, {})
    gate("E7 unmeasured shapes: wired source refused, 2-border sink refused, non-IndexArray source broken? UNMEASURED flagged",
         ok4 and ok5 and eff6.get("broken_predicted") == "UNMEASURED" and eff6.get("name_status") == "UNPREDICTED-NAME",
         (msg4[:80], msg5[:80], eff6.get("broken_predicted")))


def d_gates():
    print("---------- D: delete_wire keeps a Case Tunnel whose faces are all unwired (PD310(c), v7 step 158-159)")
    # #10465's shape in graph_ring_p3b2b: Tunnel of CaseStructure #10445 on 23166, outer sink t10469 on w25415 (source #9647
    # t9668, other sink indicator t25557), inner t10467/t10468 on frames 10453/10459 with wire 0 (prep_c137_6_facts.md:18-21)
    rows = [row(9668, "x .and. y?", True, 25415, 9647, "Function", BODY),
            row(25557, "", False, 25415, 25557, "ControlTerminal", BODY),
            row(10469, "", False, 25415, 10465, "Tunnel", BODY, "OuterTerminal"),
            row(10467, "", True, 0, 10465, "Tunnel", 10453, "InnerTerminal"),
            row(10468, "", True, 0, 10465, "Tunnel", 10459, "InnerTerminal"),
            # a LoopTunnel whose last wire goes (the MEASURED drop, stage_d1_l7_r.json:221,228,588-589)
            row(5001, "out", True, 4000, 5000, "Function", BODY),
            row(4001, "", False, 4000, 4002, "LoopTunnel", BODY, "OuterTerminal"),
            row(4003, "", True, 0, 4002, "LoopTunnel", 5555, "InnerTerminal")]
    st = SS.base_state({"terminals": rows, "objs": [], "owners": {"10453": ["CaseStructure", 10445],
                                                                    "10459": ["CaseStructure", 10445]}})
    P = {"drop_unwired_tunnel": True}                  # opmodels/delete_wire.json:4 sim params
    eff, _ = SS.op_delete_wire(st, {"id": "p4_rbR_dw", "wire_uid": 25415}, P, None, {})
    gate("D1 after delete_wire w25415 Tunnel #10465 keeps its 3 rows, flagged unmeasured_unwired_tunnels",
         len(SS.node_rows(st, 10465)) == 3 and eff.get("unmeasured_unwired_tunnels") == [10465] and
         10465 not in eff.get("auto_removed_tunnels", []), (len(SS.node_rows(st, 10465)), eff))
    try:
        e2, _ = SS.op_wire(st, {"id": "p4_rbR_re0", "src": {"uid": 9647, "term_uid": 9668},
                                "dst": {"uid": 10465, "term_uid": 10469}}, {}, None, {})
        ok, det = e2.get("dst_term_uid") == 10469, e2
    except SS.SimError as e:
        ok, det = False, str(e)
    gate("D2 v7 step 159 (#9647 t9668 -> #10465 t10469) resolves and wires", ok, det)
    e3, _ = SS.op_delete_wire(st, {"id": "lt", "wire_uid": 4000}, P, None, {})
    gate("D3 a LoopTunnel left with no wire is still dropped (measured rule unchanged)",
         e3.get("auto_removed_tunnels") == [4002] and not SS.node_rows(st, 4002) and "unmeasured_unwired_tunnels" not in e3, e3)


def x_gates():
    print("---------- X: stagexec FS-exit route")
    import stagexec as SX
    plan = {"actions": [
        {"op": "create", "id": "c_fs", "class": "FlatSequence", "diagram": BODY, "as": "FS9"},
        {"op": "create", "id": "c_ia", "class": "IndexArray", "prim": "Index Array", "diagram": "new:FS9.f0", "as": "IA9"},
        {"op": "wire", "id": "w_exit", "src": "new:IA9.element", "dst": {"uid": 200, "term_uid": 299}},
        {"op": "wire_remove_loose_ends", "id": "rle", "of": "w_exit"}]}
    fsw = SX.fs_wire_ops(plan["actions"])
    gate("X1 fs_wire_ops: frame node -> body sink = variant fs_exit", (fsw.get(3) or {}).get("variant") == "fs_exit", fsw)
    gate("X2 FS_VARIANT_HOW fs_exit -> how fs_exit (the op carries stagesim's per-row census); not in ROUTE_CENSUS "
         "(census_samples.json has no FS-exit sample, selftest_case_frame_c124 U01)",
         SX.FS_VARIANT_HOW.get("fs_exit") == "fs_exit" and SX.FS_HOW_VARIANT.get("fs_exit") == "fs_exit"
         and "fs_exit" not in SX.ROUTE_CENSUS["connect_term_uid"], sorted(SX.FS_VARIANT_HOW))
    try:
        ops = SX.compile_plan(plan)
        k = [o for o in ops if 3 in o["acts"]]
        ok = len(k) == 1 and k[0]["kind"] == "connect_term_uid" and k[0].get("variant") == "fs_exit"
    except SX.ExecStop as e:
        ok, k = False, str(e)
    gate("X3 compile_plan: the exit = ONE connect_term_uid op, variant fs_exit (U6' ran g.connect_term_uid(W, snk, src), "
         "diag_c137_7_types.py:30,64)", ok, k)
    v7 = json.load(open(os.path.join(HERE, "plan_ring_p4_v7.json"), encoding="utf-8"))
    ops7 = SX.compile_plan(v7)
    n171 = [o for o in ops7 if 171 in o["acts"]]
    gate("X4 compile_plan(v7) passes and files v7 #171 p4_x_n2_out as connect_term_uid fs_exit",
         len(n171) == 1 and n171[0]["kind"] == "connect_term_uid" and n171[0].get("variant") == "fs_exit",
         (len(ops7), n171))


def main():
    print("stagesim from", SS.__file__)
    if ONLY in (None, "E"):
        e_gates()
    if ONLY in (None, "D"):
        d_gates()
    if ONLY in (None, "X"):
        x_gates()
    print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])))
    return 0 if not G["fail"] else 1


if __name__ == "__main__":
    sys.exit(main())
